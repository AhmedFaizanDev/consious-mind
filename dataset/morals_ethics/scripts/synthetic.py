#!/usr/bin/env python3
"""Synthetic gap-filling for applied / professional ethics (clearly separated from sourced data).

Subcommands
  prompts   write one prompt file per (domain, sub-topic) cell to work/synthetic/prompts/
  generate  call the Anthropic API for every cell not yet in work/synthetic/raw/ (needs ANTHROPIC_API_KEY;
            batched per cell, checkpointed per cell, exponential backoff, failures -> logs/synthetic_failures.jsonl)
  ingest    validate raw cell files, drop duplicates against the sourced pool and each other, and write
            work/synthetic/validated.jsonl in the staged-record schema (origin='synthetic_this_project',
            label_type='none': NO answer labels are generated)

A cell file work/synthetic/raw/<domain>__<idx>.json is a JSON array in the format requested by synthetic_prompt.md;
it can come from `generate` or from any other Claude session. Provenance is recorded per file in
work/synthetic/raw/<domain>__<idx>.meta.json when present (generator model, date, method).
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
SPEC = json.load(open(HERE / "synthetic_spec.json"))
PROMPT = (HERE / "synthetic_prompt.md").read_text()
SYN = HERE / "work" / "synthetic"
LOGS = HERE / "logs"
LEAKS = re.compile(r"\b(the (right|correct|best|moral) (thing|choice|answer|option)|should obviously|clearly (wrong|right)|correct answer)\b", re.I)


def cells():
    for dom, subs in SPEC["domains"].items():
        for i, sub in enumerate(subs):
            yield dom, i, sub


def build_prompt(dom, sub, avoid_titles):
    avoid = ""
    if avoid_titles:
        avoid = "\nAlready used in this dataset (do not repeat these ideas): " + "; ".join(avoid_titles[:60]) + "\n"
    return PROMPT.format(n=SPEC["items_per_cell"], domain=dom.replace("_", " "), subtopic=sub, avoid=avoid)


def cmd_prompts(_):
    (SYN / "prompts").mkdir(parents=True, exist_ok=True)
    for dom, i, sub in cells():
        (SYN / "prompts" / f"{dom}__{i}.txt").write_text(build_prompt(dom, sub, []))
    print("prompts written:", len(list(cells())))


def parse_json_array(txt):
    txt = txt.strip()
    txt = re.sub(r"^```(?:json)?|```$", "", txt, flags=re.M).strip()
    return json.loads(txt[txt.index("["): txt.rindex("]") + 1])


def cmd_generate(a):
    import anthropic  # pip install anthropic
    client = anthropic.Anthropic()
    raw = SYN / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    for dom, i, sub in cells():
        out = raw / f"{dom}__{i}.json"
        if out.exists():
            continue  # checkpoint: never regenerate a completed cell
        titles = []
        for f in raw.glob(f"{dom}__*.json"):
            try:
                titles += [x.get("title", "") for x in json.load(open(f))]
            except Exception:  # noqa: BLE001
                pass
        for attempt in range(5):
            try:
                msg = client.messages.create(model=a.model, max_tokens=16000, temperature=1.0,
                                             messages=[{"role": "user", "content": build_prompt(dom, sub, titles)}])
                items = parse_json_array(msg.content[0].text)
                out.write_text(json.dumps(items, ensure_ascii=False, indent=1))
                (raw / f"{dom}__{i}.meta.json").write_text(json.dumps(
                    {"generator": a.model, "method": "anthropic_api", "date": time.strftime("%Y-%m-%d"),
                     "prompt_sha1": hashlib.sha1(build_prompt(dom, sub, []).encode()).hexdigest()}))
                print("ok", out.name, len(items))
                time.sleep(a.sleep)
                break
            except Exception as e:  # noqa: BLE001
                with open(LOGS / "synthetic_failures.jsonl", "a") as lf:
                    lf.write(json.dumps({"cell": out.name, "attempt": attempt, "error": str(e)[:300]}) + "\n")
                time.sleep(2 ** (attempt + 1))


def to_record(dom, sub_idx, sub, j, k, meta):
    opts = [adapters.clean(o) for o in j["options"]]
    letters = "ABC"[: len(opts)]
    scen = adapters.clean(j["scenario"])
    sid = f"{dom}__{sub_idx}__{k}"
    return adapters.rec(
        source_dataset="ConsciousMind synthetic applied-ethics set (this project)", source_component="Synthetic-AppliedEthics",
        source_item_id=sid, source_split="none", origin="synthetic_this_project",
        task_type="dilemma_open_choice", domain=dom, topic_tag=SPEC["domains"][dom][sub_idx],
        ethical_framework="Applied / professional ethics (model-written dilemma; no answer key)",
        scenario_text=scen + "\n" + "\n".join(f"Option {l}: {o}" for l, o in zip(letters, opts)),
        question_text="Which option would you choose, and why? There is no gold answer.",
        response_format="open_dilemma_choice", answer_options="|".join(letters),
        label="", label_raw="", label_type="none",
        label_transform="No label: scenario generated by a language model with no answer key; not human-authored or human-validated.",
        extra={"title": adapters.clean(j["title"]), "tension_model_generated": j.get("tension"), "region_model_generated": j.get("region"),
               "generator": meta.get("generator", "Claude (model version not exposed by generating session)"),
               "generation_method": meta.get("method", "unknown"), "generation_date": meta.get("date", "")},
        license="Generated by this project; no third-party license. Not human-authored.",
        citation="This project (ConsciousMind); generated with Claude", source_url="n/a (synthetic)",
        contamination_risk="low (new text)", _key=adapters.norm_key(scen), _sim=scen,
    )


def cmd_ingest(_):
    raw = SYN / "raw"
    LOGS.mkdir(exist_ok=True)
    fail = open(LOGS / "synthetic_ingest_failures.jsonl", "w")
    recs, seen_titles, seen_open = [], set(), {}
    stats = {"files": 0, "raw_items": 0, "accepted": 0, "rejected": {}}

    def reject(why, cell, k):
        stats["rejected"][why] = stats["rejected"].get(why, 0) + 1
        fail.write(json.dumps({"cell": cell, "idx": k, "reason": why}) + "\n")

    for dom, i, sub in cells():
        f = raw / f"{dom}__{i}.json"
        if not f.exists():
            continue
        stats["files"] += 1
        meta = json.load(open(raw / f"{dom}__{i}.meta.json")) if (raw / f"{dom}__{i}.meta.json").exists() else {}
        try:
            items = json.load(open(f))
        except Exception:  # noqa: BLE001
            reject("unparseable_file", f.name, -1)
            continue
        for k, j in enumerate(items):
            stats["raw_items"] += 1
            try:
                scen, opts = adapters.clean(j["scenario"]), j["options"]
                assert isinstance(opts, list) and 2 <= len(opts) <= 3 and all(isinstance(o, str) for o in opts)
                assert adapters.clean(j["title"])
            except Exception:  # noqa: BLE001
                reject("schema", f.name, k)
                continue
            nw = len(scen.split())
            if not (45 <= nw <= 220):
                reject("scenario_length", f.name, k)
                continue
            if any(not (6 <= len(o.split()) <= 60) for o in opts) or len({adapters.norm_key(o) for o in opts}) != len(opts):
                reject("option_quality", f.name, k)
                continue
            if LEAKS.search(scen) or any(LEAKS.search(o) for o in opts):
                reject("answer_leak_phrase", f.name, k)
                continue
            op = " ".join(scen.lower().split()[:4])
            seen_open[op] = seen_open.get(op, 0) + 1
            if seen_open[op] > 3:
                reject("repeated_opening", f.name, k)
                continue
            tk = adapters.norm_key(j["title"])
            if tk in seen_titles:
                reject("duplicate_title", f.name, k)
                continue
            seen_titles.add(tk)
            recs.append(to_record(dom, i, sub, j, k, meta))
    out = SYN / "validated.jsonl"
    with open(out, "w", encoding="utf-8") as fo:
        for r in recs:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats["accepted"] = len(recs)
    json.dump(stats, open(SYN / "ingest_stats.json", "w"), indent=2)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("prompts").set_defaults(fn=cmd_prompts)
    g = sp.add_parser("generate")
    g.add_argument("--model", default="claude-sonnet-5-5")
    g.add_argument("--sleep", type=float, default=1.0)
    g.set_defaults(fn=cmd_generate)
    sp.add_parser("ingest").set_defaults(fn=cmd_ingest)
    a = ap.parse_args()
    a.fn(a)
