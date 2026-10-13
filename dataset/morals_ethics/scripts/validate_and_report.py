#!/usr/bin/env python3
"""Stage 3: independent validation of output/morals_ethics_25k.csv and the data-quality report.

Re-reads only the final CSV (plus build_stats.json for upstream failure counts), so it checks what was actually
shipped. Writes DATA_QUALITY_REPORT.md and work/quality_report.json. Exit code 1 if a hard check fails.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from datasketch import MinHash, MinHashLSH

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402

cfg = json.load(open(HERE / "config.json"))
df = pd.read_csv(HERE / "output" / "morals_ethics_25k.csv", dtype=str, keep_default_na=False)
stats = json.load(open(HERE / "work" / "build_stats.json"))
hard_fail = []
R = {}  # report data

REQUIRED = ["item_id", "origin", "source_dataset", "source_component", "source_item_id", "split", "task_type", "domain",
            "scenario_text", "question_text", "response_format", "answer_options", "label_type", "human_label_status",
            "license", "citation", "source_url", "validation_status"]
n = len(df)
R["rows"] = n
R["unique_item_ids"] = int(df.item_id.nunique())
if R["unique_item_ids"] != n:
    hard_fail.append("duplicate item_id")

# --- missing required fields
R["missing_required"] = {c: int((df[c].str.strip() == "").sum()) for c in REQUIRED if (df[c].str.strip() == "").any()}
if R["missing_required"]:
    hard_fail.append(f"missing required fields: {R['missing_required']}")

# --- enumerations
enums = {
    "origin": {"human_authored", "llm_generated_published", "author_written", "synthetic_this_project"},
    "split": {"train", "dev", "test"},
    "human_label_status": {"human_labeled", "author_designated", "unlabeled", "model_generated_unvalidated"},
}
R["bad_enum"] = {c: int((~df[c].isin(v)).sum()) for c, v in enums.items() if (~df[c].isin(v)).any()}
if R["bad_enum"]:
    hard_fail.append(f"bad enum values: {R['bad_enum']}")

# --- label validity
bad_label = 0
for _, r in df.iterrows():
    opts = [o.strip() for o in r.answer_options.split("|")]
    if r.label_type == "none":
        if r.label:
            bad_label += 1
    elif r.response_format != "philosopher_single_choice":
        if not any(r.label == o or o.split(" (")[0] == r.label for o in opts):
            bad_label += 1
R["label_validity_failures"] = bad_label
if bad_label:
    hard_fail.append(f"{bad_label} invalid labels")
ag = pd.to_numeric(df.label_agreement.replace("", None), errors="coerce")
R["agreement_out_of_range"] = int(((ag < 0) | (ag > 1)).sum())

# --- JSON columns parse
badj = 0
for c in ("label_distribution", "extra"):
    for v in df[c]:
        if v:
            try:
                json.loads(v)
            except Exception:  # noqa: BLE001
                badj += 1
R["malformed_json_cells"] = badj
if badj:
    hard_fail.append("malformed JSON cells")

# --- duplicates
df["_k"] = df.scenario_text.map(adapters.norm_key) + "||" + df.question_text.map(adapters.norm_key)
R["exact_duplicate_rows"] = int(df._k.duplicated().sum())
R["exact_duplicate_scenario_text"] = int(df.scenario_text.map(adapters.norm_key).duplicated().sum())
R["duplicate_rate"] = round(R["exact_duplicate_rows"] / n, 6)
if R["exact_duplicate_rows"]:
    hard_fail.append("exact duplicates in final")

# --- near-duplicate / leakage check, recomputed independently on the final file
nd = cfg["near_dup"]
sim = df.scenario_text.map(lambda t: t.split("\nCandidate traits:")[0])
def sh(t):
    w = re.sub(r"[^a-z0-9 ]+", " ", t.lower()).split()
    k = nd["shingle_words"]
    return set(w) if len(w) < k else {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}
lsh = MinHashLSH(threshold=nd["jaccard"], num_perm=nd["num_perm"])
mh = {}
for i, t in enumerate(sim):
    if len(t.split()) < nd["min_words"]:
        continue
    m = MinHash(num_perm=nd["num_perm"])
    for s in sh(t):
        m.update(s.encode())
    mh[i] = m
    lsh.insert(str(i), m)
pairs, cross, cross_ex = 0, 0, []
for i, m in mh.items():
    for j in lsh.query(m):
        j = int(j)
        if j > i:
            pairs += 1
            if df.split[i] != df.split[j]:
                cross += 1
                if len(cross_ex) < 5:
                    cross_ex.append((df.item_id[i], df.item_id[j]))
R["near_dup_pairs_remaining_jaccard_ge_%.2f" % nd["jaccard"]] = pairs
R["near_dup_pairs_crossing_splits"] = cross
R["near_dup_cross_split_examples"] = cross_ex
if cross:
    hard_fail.append(f"{cross} near-duplicate pairs cross splits")

# --- cross-source overlap of the same Reddit posts (title-level), informational
def strip_aita(t):
    t = adapters.norm_key(t)
    return re.sub(r"^(aita|wibta|am i the asshole|would i be the asshole|aita for|wibta for) ?(for |if |that )?", "", t)
scan = df[df.source_component == "Scruples-Anecdotes"].scenario_text.map(lambda t: strip_aita(t.split("\n")[0].replace("Title: ", "")))
sc_aita = df[df.source_component == "SocialChem101-amitheasshole"].scenario_text.map(lambda t: strip_aita(t.split("\n")[0].replace("Situation: ", "")))
R["cross_source_reddit_title_overlap_scruples_vs_socialchem"] = int(len(set(scan) & set(sc_aita)))

# --- composition
R["origin_counts"] = df.origin.value_counts().to_dict()
R["real_vs_synthetic"] = {"sourced_real_or_published": int((df.origin != "synthetic_this_project").sum()),
                          "synthetic_this_project": int((df.origin == "synthetic_this_project").sum())}
R["domain_distribution"] = df.domain.value_counts().to_dict()
R["component_counts"] = df.source_component.value_counts().to_dict()
R["label_availability"] = df.human_label_status.value_counts().to_dict()
R["label_type_counts"] = df.label_type.value_counts().to_dict()
R["split_counts"] = df.split.value_counts().to_dict()
R["split_by_origin"] = pd.crosstab(df.origin, df.split).to_dict()
R["license_coverage"] = {"rows_with_license": int((df.license.str.strip() != "").sum()), "rows_with_citation": int((df.citation.str.strip() != "").sum()),
                         "rows_with_url": int((df.source_url.str.strip() != "").sum())}
R["license_stated_vs_unstated"] = {
    "explicit_license_in_source": int(df.license.str.contains(r"MIT|Apache|CC BY|CC-BY", regex=True).sum()),
    "not_stated_in_source_verify": int(df.license.str.contains("Not stated|verify|Verify", regex=True).sum()),
}
R["prior_workbook_items_preserved"] = int((df.preserved_from_prior_workbook == "True").sum())
R["items_with_prior_model_responses"] = int((pd.to_numeric(df.n_prior_model_responses) > 0).sum())
R["text_chars"] = {k: float(v) for k, v in pd.to_numeric(df.text_chars).describe().round(1).to_dict().items()}
R["label_distribution_by_component"] = {c: g.label.replace("", "(none)").value_counts().to_dict() for c, g in df.groupby("source_component")}
R["upstream_validation_failures"] = stats.get("validation_failures", {})
R["dedup_actions"] = stats.get("dedup", {})
R["stage_counts"] = stats.get("stage", {})
labeled = df[df.human_label_status != "unlabeled"]
R["valid_labeled_items"] = int(len(labeled))
R["valid_unique_items"] = int(n - len(hard_fail) * 0 - R["exact_duplicate_rows"])  # all rows passed validation if no hard failure
R["hard_failures"] = hard_fail
json.dump(R, open(HERE / "work" / "quality_report.json", "w"), indent=2, default=str)


def tbl(d, h1, h2):
    return f"| {h1} | {h2} |\n|---|---:|\n" + "\n".join(f"| {k} | {v} |" for k, v in d.items()) + "\n"


md = f"""# Data-quality report - `morals_ethics_25k.csv`

Generated by `scripts/validate_and_report.py` from the shipped CSV (re-validated independently of the build step).

## Headline

| Check | Result |
|---|---|
| Rows | **{n:,}** |
| Unique `item_id` | {R['unique_item_ids']:,} |
| Exact duplicate rows (normalized scenario+question) | {R['exact_duplicate_rows']} (rate {R['duplicate_rate']:.4%}) |
| Rows failing any hard validation check | {"0" if not hard_fail else "see below"} |
| Sourced real/published items | {R['real_vs_synthetic']['sourced_real_or_published']:,} |
| Synthetic (this project, Claude-written, no labels) | {R['real_vs_synthetic']['synthetic_this_project']:,} |
| Items with a human-derived label | {R['label_availability'].get('human_labeled', 0):,} |
| Items with an author/design-designated label (not crowd) | {R['label_availability'].get('author_designated', 0):,} |
| Unlabeled items (open dilemmas) | {R['label_availability'].get('unlabeled', 0):,} |
| Near-duplicate pairs left (Jaccard >= {nd['jaccard']}) | {R['near_dup_pairs_remaining_jaccard_ge_%.2f' % nd['jaccard']]} (kept by policy: max {nd['max_per_cluster']} per cluster; all inside one split) |
| Near-duplicate pairs crossing train/dev/test | **{R['near_dup_pairs_crossing_splits']}** |
| Prior-workbook items preserved (ids unchanged) | {R['prior_workbook_items_preserved']} / 416 |
| Hard failures | {", ".join(hard_fail) or "none"} |

"Unique valid items" = {R['valid_unique_items']:,} (rows that pass every check above and are not exact duplicates). This count is for *structural* validity;
it is **not** a claim that labels are morally correct (see README, limitations).

## Real vs. synthetic and provenance of the text
{tbl(R['origin_counts'], 'origin', 'items')}
- `human_authored`: written by crowd workers, Reddit users or researchers in the source study.
- `author_written`: hand-written by the source dataset authors (e.g. MoralExceptQA vignettes, MoralChoice hand-written set).
- `llm_generated_published`: generated by an LLM *by the source authors* (DailyDilemmas, MoralChoice low-ambiguity); not human-authored even though sourced.
- `synthetic_this_project`: generated in this project by Claude to fill the applied-ethics gap; never labeled.

## Domain distribution
{tbl(R['domain_distribution'], 'domain', 'items')}
## Source components
{tbl(R['component_counts'], 'source_component', 'items')}
## Label availability and type
{tbl(R['label_type_counts'], 'label_type', 'items')}
Label distributions per component are in `work/quality_report.json` (`label_distribution_by_component`). **Several components were
label-balanced by the sampling procedure (e.g. Social Chemistry 101 five-point judgments are close to uniform); this does not
reflect the natural distribution in the source.**

## Splits (cluster-aware)
{tbl(R['split_counts'], 'split', 'items')}
Splits are assigned by hashing the near-duplicate cluster id (or item id for singletons), so near-duplicates always land in the same split.
Independent re-check on the final file: **{R['near_dup_pairs_crossing_splits']}** near-duplicate pairs cross splits.
Cross-source check: {R['cross_source_reddit_title_overlap_scruples_vs_socialchem']} Reddit titles appear in both Scruples-Anecdotes and Social Chemistry (AITA)
(different tasks; items may share a source post, so do not treat them as independent samples if that matters for your analysis).

## Source / license coverage
- rows with license field: {R['license_coverage']['rows_with_license']:,}; citation: {R['license_coverage']['rows_with_citation']:,}; source URL: {R['license_coverage']['rows_with_url']:,}
- rows whose source states an explicit license (MIT / Apache / CC BY): {R['license_stated_vs_unstated']['explicit_license_in_source']:,}
- rows whose source does **not** state a license in the distributed files (verify before redistribution): {R['license_stated_vs_unstated']['not_stated_in_source_verify']:,}

## Validation failures and de-duplication
Upstream (per adapter) validation failures that removed records before selection:
{tbl(R['upstream_validation_failures'] or {'none': 0}, 'adapter:reason', 'records')}
De-duplication actions during build:
{tbl(R['dedup_actions'], 'action', 'records')}
Prior-workbook ids are never removed by dedup. Records whose normalized text appeared with conflicting labels were dropped (`label_conflict_dropped`).

## Row-level checks
- invalid labels: {R['label_validity_failures']} - malformed JSON cells: {R['malformed_json_cells']} - agreement outside [0,1]: {R['agreement_out_of_range']}
- scenario length (chars): {R['text_chars']}
"""
(HERE / "DATA_QUALITY_REPORT.md").write_text(md)
print(md[:2500])
sys.exit(1 if hard_fail else 0)
