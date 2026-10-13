#!/usr/bin/env python3
"""
Extended build script for ConsciousMind Category B: Safety-Critical Judgment.

Supersedes the original build_dataset.py's 38-question pull. This machine
has normal (non-sandboxed) network access, so the full izi-ano/CounselBench-Eval
dataset (2000 rows = 100 questions x 4 responders x 5 raters) was fetched
directly via datasets-server.huggingface.co's REST API using plain curl (no
WebFetch workaround needed) in 20 calls of length=100 (the API's per-request
cap), offsets 0..1900. The raw, unmodified API response rows are saved
verbatim at category_b_safety_judgment/raw_hf_fetch/all_2000_rows.json --
this script reads that file rather than re-fetching or hardcoding records,
so it is fully reproducible offline.

Filtering logic kept identical to the original build_dataset.py: only the
"human" and "gpt4" responder rows are used (llama3/gemini rows exist in the
raw fetch and can be added later without re-fetching anything). The only
change from the original build is going from 38/100 to the full 100/100
questions, now that fetching all of them is no longer rate-limited or
truncated (both were quirks of the earlier WebFetch access path, not of the
API itself -- see build_log.md).
"""

import json
import csv
import statistics
from pathlib import Path

OUT_DIR = Path(__file__).parent / "category_b_safety_judgment"
RAW_FETCH_PATH = OUT_DIR / "raw_hf_fetch" / "all_2000_rows.json"


def is_numeric(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def agg_numeric(values):
    nums = [float(v) for v in values if is_numeric(v)]
    if not nums:
        return dict(mean=None, median=None, min=None, max=None, n_numeric=0, n_total=len(values))
    return dict(mean=round(statistics.mean(nums), 3), median=statistics.median(nums),
                min=min(nums), max=max(nums), n_numeric=len(nums), n_total=len(values))


def agg_categorical(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return counts


def main():
    with open(RAW_FETCH_PATH) as f:
        all_rows = json.load(f)
    print(f"Loaded {len(all_rows)} raw rows from {RAW_FETCH_PATH}")

    # Group by (questionID, responder) -> list of rater rows, keep only human/gpt4
    grouped = {}
    question_meta = {}
    for r in all_rows:
        if r["responder"] not in ("human", "gpt4"):
            continue
        key = (r["questionID"], r["responder"])
        grouped.setdefault(key, []).append(r)
        question_meta.setdefault(r["questionID"], {
            "topic": r["topic"], "title": r["questionTitle"], "text": r["questionText"],
        })

    question_ids = sorted(question_meta.keys(), key=lambda q: int(q.split("_")[1]))
    print(f"Questions: {len(question_ids)}")

    # ---- raw_ratings.csv ----
    raw_rows = []
    for qid in question_ids:
        for responder in ("gpt4", "human"):
            for r in grouped.get((qid, responder), []):
                raw_rows.append(dict(
                    questionID=qid, topic=r["topic"], responder=responder,
                    survey_id=r["survey_id"], overall_score=r["overall_score"],
                    empathy_score=r["empathy_score"], specificity_score=r["specificity_score"],
                    medical_advice_score=r["medical_advice_score"],
                    factual_consistency_score=r["factual_consistency_score"],
                    toxicity_score=r["toxicity_score"],
                ))

    raw_path = OUT_DIR / "raw_ratings.csv"
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
        w.writeheader()
        w.writerows(raw_rows)
    print(f"Wrote {len(raw_rows)} rows to {raw_path}")

    # ---- items.json ----
    items = []
    item_id_counter = 0
    for qid in question_ids:
        meta = question_meta[qid]
        for responder in ("gpt4", "human"):
            rows = grouped.get((qid, responder), [])
            if not rows:
                continue
            response_text = rows[0]["response"]
            overall = [r["overall_score"] for r in rows]
            empathy = [r["empathy_score"] for r in rows]
            specificity = [r["specificity_score"] for r in rows]
            medical = [r["medical_advice_score"] for r in rows]
            factual = [r["factual_consistency_score"] for r in rows]
            toxicity = [r["toxicity_score"] for r in rows]
            item_id_counter += 1
            items.append(dict(
                item_id=f"cbe_{item_id_counter:03d}",
                questionID=qid,
                topic=meta["topic"],
                questionTitle=meta["title"],
                questionText=meta["text"],
                responder=responder,
                response=response_text,
                n_raters=len(rows),
                raw_rater_scores=[dict(survey_id=r["survey_id"], overall_score=r["overall_score"],
                                        empathy_score=r["empathy_score"], specificity_score=r["specificity_score"],
                                        medical_advice_score=r["medical_advice_score"],
                                        factual_consistency_score=r["factual_consistency_score"],
                                        toxicity_score=r["toxicity_score"])
                                   for r in rows],
                aggregate=dict(
                    overall_score=agg_numeric(overall),
                    empathy_score=agg_numeric(empathy),
                    specificity_score=agg_numeric(specificity),
                    toxicity_score=agg_numeric(toxicity),
                    factual_consistency_score=agg_numeric(factual),
                    medical_advice_score=agg_categorical(medical),
                ),
                source=dict(
                    dataset="izi-ano/CounselBench-Eval",
                    origin_study="CounselBench (Cao et al.)",
                    underlying_questions_source="CounselChat (nbertagnolli/counsel-chat)",
                    license="CC-BY-NC-ND-4.0 (dataset card, Hugging Face)",
                    access_method="datasets-server.huggingface.co REST API via direct curl (full 2000-row fetch, 20 calls of length=100)",
                ),
            ))

    items_path = OUT_DIR / "items.json"
    with open(items_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(items)} items to {items_path}")

    # ---- items_aggregated.csv ----
    agg_rows = []
    for it in items:
        a = it["aggregate"]
        agg_rows.append(dict(
            item_id=it["item_id"], questionID=it["questionID"], topic=it["topic"],
            responder=it["responder"], n_raters=it["n_raters"],
            overall_mean=a["overall_score"]["mean"], empathy_mean=a["empathy_score"]["mean"],
            specificity_mean=a["specificity_score"]["mean"], toxicity_mean=a["toxicity_score"]["mean"],
            factual_consistency_mean=a["factual_consistency_score"]["mean"],
            medical_advice_yes_count=a["medical_advice_score"].get("Yes", 0),
            medical_advice_no_count=a["medical_advice_score"].get("No", 0),
            medical_advice_unsure_count=a["medical_advice_score"].get("I am not sure", 0),
        ))

    agg_path = OUT_DIR / "items_aggregated.csv"
    with open(agg_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(agg_rows[0].keys()))
        w.writeheader()
        w.writerows(agg_rows)
    print(f"Wrote {len(agg_rows)} rows to {agg_path}")

    # ---- Sanity summary ----
    human_overall = [r["overall_mean"] for r in agg_rows if r["responder"] == "human" and r["overall_mean"] is not None]
    gpt4_overall = [r["overall_mean"] for r in agg_rows if r["responder"] == "gpt4" and r["overall_mean"] is not None]
    human_toxicity = [r["toxicity_mean"] for r in agg_rows if r["responder"] == "human" and r["toxicity_mean"] is not None]
    gpt4_toxicity = [r["toxicity_mean"] for r in agg_rows if r["responder"] == "gpt4" and r["toxicity_mean"] is not None]
    n_questions = len(question_ids)
    refusal_prefix = "I'm really sorry that you're feeling this way, but I'm unable to provide the help"
    n_gpt4_refusal = sum(1 for it in items if it["responder"] == "gpt4" and it["response"] and it["response"].startswith(refusal_prefix))

    print("\n--- Sanity summary ---")
    print(f"Questions: {n_questions}  |  Items (question x responder): {len(items)}  |  Raw ratings rows: {len(raw_rows)}")
    print(f"Mean Overall (human): {statistics.mean(human_overall):.3f}   Mean Overall (gpt4): {statistics.mean(gpt4_overall):.3f}")
    print(f"Mean Toxicity (human, 1-5, lower=less toxic): {statistics.mean(human_toxicity):.3f}   Mean Toxicity (gpt4): {statistics.mean(gpt4_toxicity):.3f}")
    print(f"GPT-4 canned-refusal responses: {n_gpt4_refusal} / {n_questions} questions ({100*n_gpt4_refusal/n_questions:.1f}%)")


if __name__ == "__main__":
    main()
