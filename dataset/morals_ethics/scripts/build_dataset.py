#!/usr/bin/env python3
"""Stage 2: validate, de-duplicate, cluster near-duplicates, select, split, and write the dataset.

Inputs : work/staged/*.jsonl (from stage_sources.py), optional work/synthetic/validated.jsonl
Outputs: output/morals_ethics_25k.csv
         output/morals_ethics_25k_prior_model_responses.csv   (prior LLM responses, keyed by item_id)
         output/source_manifest.csv / source_manifest.json
         work/build_stats.json                                (consumed by validate_and_report.py)
         logs/validation_failures.jsonl, logs/dedup_log.jsonl

Deterministic given config.json (seed) and the staged inputs. Raw files are never modified.
"""
import csv
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from datasketch import MinHash, MinHashLSH

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
STAGED, LOGS, OUT, WORK = HERE / "work" / "staged", HERE / "logs", HERE / "output", HERE / "work"

# quota weights for the large pools (small pools are taken whole); see README for rationale
WEIGHTS = {
    "ethics_commonsense": 2500, "ethics_justice": 1300, "ethics_deontology": 1300, "ethics_virtue": 1100,
    "ethics_util": 1300, "scruples_anecdotes": 4800, "scruples_dilemmas": 2700, "social_chem": 7000,
}
TAKE_ALL = ["prior_workbook", "daily_dilemmas", "moralchoice", "moralexceptqa", "bigbench_moral"]
PREFIX = {
    "ETHICS-CommonsenseMorality": "CM", "ETHICS-Justice": "JUST", "ETHICS-Deontology": "DEON", "ETHICS-Virtue": "VIRT",
    "ETHICS-Utilitarianism": "UTIL", "Scruples-Anecdotes": "SCAN", "Scruples-Dilemmas": "SCDL", "DailyDilemmas": "DD",
    "MoralExceptQA": "MEQA", "BIGbench-MoralPermissibility": "BBMP", "BIGbench-SimpleEthicalQuestions": "BBSE",
}
COLUMNS = [
    "item_id", "origin", "is_synthetic", "source_dataset", "source_component", "source_item_id", "source_split",
    "split", "task_type", "domain", "topic_tag", "ethical_framework", "scenario_text", "question_text",
    "response_format", "answer_options", "label", "label_raw", "label_type", "human_label_status", "label_transform",
    "label_distribution", "n_annotators", "label_agreement", "adversarial_filtered", "near_dup_cluster_id",
    "near_dup_cluster_size", "text_chars", "n_prior_model_responses", "preserved_from_prior_workbook", "extra",
    "license", "citation", "source_url", "contamination_risk", "validation_status",
]
BAD_PLACEHOLDER = re.compile(r"^(nan|none|null|\[removed\]|\[deleted\])$", re.I)


# --------------------------------------------------------------------------- validation
def validate(r):
    """Return list of failure reasons (empty = valid)."""
    f = []
    for k in ("source_dataset", "source_component", "source_item_id", "origin", "task_type", "domain",
              "scenario_text", "question_text", "response_format", "answer_options", "license", "citation", "source_url"):
        if not str(r.get(k, "")).strip():
            f.append(f"missing:{k}")
    st = r.get("scenario_text", "")
    if len(st) < 12:
        f.append("scenario_too_short")
    if len(st) > 6000:
        f.append("scenario_too_long")
    if BAD_PLACEHOLDER.match(st.strip()):
        f.append("placeholder_text")
    if "�" in st:
        f.append("encoding_replacement_char")
    if r.get("origin") not in ("human_authored", "llm_generated_published", "author_written", "synthetic_this_project"):
        f.append("bad_origin")
    opts = [o.strip() for o in str(r.get("answer_options", "")).split("|") if o.strip()]
    if r.get("label_type") != "none":
        lab = str(r.get("label", ""))
        if not lab:
            f.append("labeled_type_but_empty_label")
        elif r.get("response_format") not in ("philosopher_single_choice",) and opts:
            # label must be one of the options (or the option's leading word, e.g. 'Yes (clearly wrong)')
            if not any(lab == o or o.split(" (")[0] == lab for o in opts):
                f.append("label_not_in_options")
    elif r.get("label"):
        f.append("unlabeled_type_but_label_present")
    ag = r.get("label_agreement", "")
    if ag != "" and not (0 <= float(ag) <= 1):
        f.append("agreement_out_of_range")
    return f


# --------------------------------------------------------------------------- selection helpers
def stratified_pick(items, n, strata_fn, rng):
    """Round-robin over strata (balanced); strata exhausted early hand their share to the others."""
    groups = defaultdict(list)
    for it in items:
        groups[strata_fn(it)].append(it)
    for g in groups.values():
        rng.shuffle(g)
    keys = sorted(groups, key=str)
    out = []
    while len(out) < n and any(groups[k] for k in keys):
        for k in keys:
            if groups[k] and len(out) < n:
                out.append(groups[k].pop())
    return out


def strata_for(comp):
    def fn(r):
        ex = json.loads(r["extra"]) if r["extra"] else {}
        if comp == "ethics_commonsense":
            return (r["label"], ex.get("length_class"), r["source_split"])
        if comp in ("ethics_justice", "ethics_deontology"):
            return (r["label"], r["source_split"])
        if comp == "ethics_virtue":
            return (r["label"], r["source_split"])
        if comp == "ethics_util":
            return (r["label"], r["source_split"])
        if comp == "scruples_anecdotes":
            return (r["label"], r["source_split"])
        if comp == "scruples_dilemmas":
            return (r["label"], bool(ex.get("controversial")))
        if comp == "social_chem":
            return (r["topic_tag"], r["label"])
        return ("all",)
    return fn


def shingles(text, k):
    w = re.sub(r"[^a-z0-9 ]+", " ", text.lower()).split()
    if len(w) < k:
        return set(w)
    return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def main():
    cfg = json.load(open(HERE / "config.json"))
    seed = cfg["seed"]
    LOGS.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    vlog = open(LOGS / "validation_failures.jsonl", "w", encoding="utf-8")
    dlog = open(LOGS / "dedup_log.jsonl", "w", encoding="utf-8")
    stats = {"seed": seed, "stage": {}, "validation_failures": Counter(), "dedup": {}}

    # ---- load + validate -------------------------------------------------------------------
    pool = {}  # adapter -> list
    names = TAKE_ALL + list(WEIGHTS)
    synth = WORK / "synthetic" / "validated.jsonl"
    for name in names:
        rows = [json.loads(l) for l in open(STAGED / f"{name}.jsonl", encoding="utf-8")]
        ok = []
        for r in rows:
            fails = validate(r)
            if fails:
                for x in fails:
                    stats["validation_failures"][f"{name}:{x}"] += 1
                vlog.write(json.dumps({"adapter": name, "source_item_id": r["source_item_id"], "failures": fails}) + "\n")
            else:
                ok.append(r)
        pool[name] = ok
        stats["stage"][name] = {"staged": len(rows), "valid": len(ok)}
    if synth.exists() and cfg.get("include_synthetic", False):
        rows = [json.loads(l) for l in open(synth, encoding="utf-8")]
        pool["synthetic"] = [r for r in rows if not validate(r)]
        stats["stage"]["synthetic"] = {"staged": len(rows), "valid": len(pool["synthetic"])}

    # ---- exact dedup (priority: prior workbook first, then file order) ----------------------
    seen = {}  # _key -> (adapter, record)
    conflicts = set()
    for name in names + (["synthetic"] if "synthetic" in pool else []):
        kept = []
        for r in pool[name]:
            k = r["_key"]
            if k in seen:
                prev_name, prev = seen[k]
                same = (prev.get("_lab") or prev["label"]) == (r.get("_lab") or r["label"]) or r["label_type"] == "none" or prev["label_type"] == "none"
                if not same:
                    conflicts.add(k)
                dlog.write(json.dumps({"kind": "exact_duplicate", "dropped": r["source_item_id"], "kept": prev["source_item_id"],
                                       "dropped_adapter": name, "kept_adapter": prev_name, "label_conflict": not same}) + "\n")
                stats["dedup"][f"exact_dup:{name}"] = stats["dedup"].get(f"exact_dup:{name}", 0) + 1
                continue
            seen[k] = (name, r)
            kept.append(r)
        pool[name] = kept
    # label-conflicting duplicates are ambiguous items: drop the surviving copy too (unless preserved prior item)
    n_conf = 0
    for name in names:
        before = len(pool[name])
        pool[name] = [r for r in pool[name] if not (r["_key"] in conflicts and not r["preserved_from_prior_workbook"])]
        n_conf += before - len(pool[name])
    stats["dedup"]["label_conflict_dropped"] = n_conf

    # ---- quota allocation ----------------------------------------------------------------------
    target = cfg["target_total"]
    fixed = sum(len(pool[n]) for n in TAKE_ALL)
    if "synthetic" in pool:
        fixed += len(pool["synthetic"])
    remaining = target - fixed
    quotas = {n: len(pool[n]) for n in TAKE_ALL}
    # leave headroom for near-dup removal: we over-select candidates, then trim to the quota
    free = {n: len(pool[n]) for n in WEIGHTS}
    alloc = {n: 0 for n in WEIGHTS}
    wsum = {n: WEIGHTS[n] for n in WEIGHTS}
    left = remaining
    active = set(WEIGHTS)
    while left > 0 and active:
        tw = sum(wsum[n] for n in active)
        gave = 0
        for n in sorted(active):
            share = min(free[n] - alloc[n], round(left * wsum[n] / tw))
            alloc[n] += share
            gave += share
        left -= gave
        active = {n for n in active if alloc[n] < free[n]}
        if gave == 0:
            break
    quotas.update(alloc)
    stats["quotas"] = quotas

    # ---- candidate over-selection -> near-dup clustering -> final pick -----------------------
    rng = random.Random(seed)
    nd = cfg["near_dup"]
    cand = []  # (adapter, record)
    for n in names:
        if n in TAKE_ALL:
            cand += [(n, r) for r in pool[n]]
        else:
            over = min(len(pool[n]), int(quotas[n] * 1.35) + 50)
            pk = stratified_pick(pool[n], over, strata_for(n), random.Random(f"{seed}-{n}"))
            cand += [(n, r) for r in pk]
    if "synthetic" in pool:
        cand += [("synthetic", r) for r in pool["synthetic"]]
    stats["candidates"] = len(cand)

    lsh = MinHashLSH(threshold=nd["jaccard"], num_perm=nd["num_perm"])
    mhs, eligible = {}, set()
    for i, (n, r) in enumerate(cand):
        sh = shingles(r["_sim"], nd["shingle_words"])
        if len(re.sub(r"[^a-z0-9 ]+", " ", r["_sim"].lower()).split()) < nd["min_words"] or not sh:
            continue
        m = MinHash(num_perm=nd["num_perm"])
        for s in sh:
            m.update(s.encode())
        mhs[i] = m
        lsh.insert(str(i), m)
        eligible.add(i)
    uf = UF()
    for i in eligible:
        uf.find(i)
        for j in lsh.query(mhs[i]):
            j = int(j)
            if j != i:
                uf.union(i, j)
    clusters = defaultdict(list)
    for i in range(len(cand)):
        clusters[uf.find(i)].append(i)
    # keep at most max_per_cluster per cluster: prior-workbook items first, then seeded random
    dropped = set()
    for root, members in clusters.items():
        if len(members) <= nd["max_per_cluster"]:
            continue
        members.sort(key=lambda i: (not cand[i][1]["preserved_from_prior_workbook"], rng.random()))
        for i in members[nd["max_per_cluster"]:]:
            dropped.add(i)
            dlog.write(json.dumps({"kind": "near_duplicate_trimmed", "dropped": cand[i][1]["source_item_id"], "adapter": cand[i][0],
                                   "cluster_root": root, "cluster_size": len(members)}) + "\n")
    stats["dedup"]["near_dup_trimmed"] = len(dropped)
    csize = {root: len(m) for root, m in clusters.items()}

    survivors = defaultdict(list)
    for i, (n, r) in enumerate(cand):
        if i not in dropped:
            r["_cluster"] = uf.find(i)
            survivors[n].append(r)
    # one Social-Chemistry item per situation (several annotator-written actions of one situation would be correlated)
    sc = survivors["social_chem"]
    random.Random(f"{seed}-scsit").shuffle(sc)
    seen_sit, uniq = set(), []
    for r in sc:
        sit = adapters.norm_key(r["scenario_text"].split("\n")[0])
        if sit in seen_sit:
            stats["dedup"]["socialchem_same_situation_dropped"] = stats["dedup"].get("socialchem_same_situation_dropped", 0) + 1
            continue
        seen_sit.add(sit)
        uniq.append(r)
    survivors["social_chem"] = uniq
    final = []
    for n in names + (["synthetic"] if "synthetic" in pool else []):
        s = survivors[n]
        if n in TAKE_ALL or n == "synthetic":
            final += s
        else:
            final += stratified_pick(s, quotas[n], strata_for(n), random.Random(f"{seed}-final-{n}"))
    # top up if near-dup trimming left us short (draw from not-yet-selected survivors of large pools)
    if len(final) < target:
        chosen = {id(r) for r in final}
        spare = [r for n in WEIGHTS for r in survivors[n] if id(r) not in chosen]
        rng.shuffle(spare)
        need = target - len(final)
        final += spare[:need]
        stats["topup_after_neardup"] = min(len(spare), need)

    # ---- ids, splits, derived columns --------------------------------------------------------
    resp = pd.read_excel(adapters.XLSX, sheet_name="LLM_Responses_Collected")
    nresp = resp.groupby("item_id").size().to_dict()
    sp = cfg["splits"]
    out_rows = []
    for r in final:
        if not r["item_id"]:
            pfx = PREFIX.get(r["source_component"]) or ("SC101" if r["source_component"].startswith("SocialChem101") else
                  "MCH" if r["source_component"].startswith("MoralChoice") else "X")
            r["item_id"] = f"{pfx}-" + hashlib.sha1((r["source_component"] + "|" + r["source_item_id"]).encode()).hexdigest()[:10]
        root = r.get("_cluster", r["item_id"])
        csz = csize.get(root, 1)
        h = int(hashlib.sha1(f"{seed}|{root if csz > 1 else r['item_id']}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
        r["split"] = "train" if h < sp["train"] else ("dev" if h < sp["train"] + sp["dev"] else "test")
        r["near_dup_cluster_id"] = f"ND-{root:06d}" if csz > 1 else ""
        r["near_dup_cluster_size"] = csz if csz > 1 else ""
        r["text_chars"] = len(r["scenario_text"])
        r["n_prior_model_responses"] = int(nresp.get(r["item_id"], 0))
        r["is_synthetic"] = r["origin"] == "synthetic_this_project"
        lt = r["label_type"]
        r["human_label_status"] = ("human_labeled" if lt.startswith("human") else
                                   "author_designated" if lt in ("dataset_design_intended", "author_designated") else
                                   "model_generated_unvalidated" if lt == "model_generated" else "unlabeled")
        r["validation_status"] = "passed"
        out_rows.append(r)
    ids = Counter(r["item_id"] for r in out_rows)
    assert all(v == 1 for v in ids.values()), [k for k, v in ids.items() if v > 1][:5]
    out_rows.sort(key=lambda r: (not r["preserved_from_prior_workbook"], r["source_component"], r["item_id"]))

    with open(OUT / "morals_ethics_25k.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore", quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in out_rows:
            w.writerow({c: r.get(c, "") for c in COLUMNS})

    # sidecar: prior model responses (preserved verbatim)
    keep = set(ids)
    rcols = [c for c in resp.columns]
    resp[resp["item_id"].isin(keep)].to_csv(OUT / "morals_ethics_25k_prior_model_responses.csv", index=False, columns=rcols)

    # source manifest
    fm = json.load(open(WORK / "fetch_manifest.json")) if (WORK / "fetch_manifest.json").exists() else {}
    man = defaultdict(lambda: {"imported_staged": 0, "valid_after_validation": 0, "in_final": 0})
    for n, s in stats["stage"].items():
        pass
    for r in out_rows:
        m = man[r["source_component"]]
        m.update(dataset=r["source_dataset"], url=r["source_url"], license=r["license"], citation=r["citation"], origin=r["origin"],
                 label_types=sorted(set(m.get("label_types", [])) | {r["label_type"]}))
        m["in_final"] += 1
    man = {k: dict(v) for k, v in sorted(man.items())}
    json.dump({"pins": fm, "components": man, "stage": stats["stage"]}, open(OUT / "source_manifest.json", "w"), indent=2, default=list)
    with open(OUT / "source_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_component", "dataset", "origin", "items_in_final", "label_types", "license_or_usage", "original_url", "citation"])
        for k, v in man.items():
            w.writerow([k, v["dataset"], v["origin"], v["in_final"], ";".join(v["label_types"]), v["license"], v["url"], v["citation"]])

    stats["final_rows"] = len(out_rows)
    stats["validation_failures"] = dict(stats["validation_failures"])
    json.dump(stats, open(WORK / "build_stats.json", "w"), indent=2, default=str)
    print(json.dumps({"final_rows": len(out_rows), "quotas": quotas, "dedup": stats["dedup"],
                      "validation_failures": stats["validation_failures"]}, indent=1))


if __name__ == "__main__":
    main()
