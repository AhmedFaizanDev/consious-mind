# Category A: Interactive Theory of Mind — Source & Provenance

## Origin

- **Dataset:** FANToM (Kim et al., EMNLP 2023)
- **Downloaded from:** `https://storage.googleapis.com/ai2-mosaic-public/projects/fantom/fantom.tar.gz`
  (the canonical URL hardcoded in `reference/fantom/task/dataset_loader.py`)
- **Integrity check:** SHA-256 of the downloaded `fantom.tar.gz` was verified
  against the hash hardcoded in the authors' own loader
  (`1d08dfa0ea474c7f83b9bc7e3a7b466eab25194043489dd618b4c5223e1253a4`) —
  exact match, confirming this is the authors' unmodified release artifact,
  not a corrupted or tampered copy.
- **License:** MIT (code repository, `reference/fantom/LICENSE`). The dataset
  itself carries an additional "evaluation purposes only" usage note from the
  authors, separate from the code license — see the top-level project README
  / `PROJECT_STATUS.md` for what this means for release.
- **Raw extracted data:** `raw_fantom/fantom_v1.json` (870 conversation
  "sets", not redistributed further than this local copy — see licensing
  note below on release).

## What this subset contains

150 items built from the raw 870-set release by `build_dataset.py`
(deterministic, seed=42, fully reproducible — re-running the script produces
byte-identical `items.json`):

- **50 `belief_choice` items** — multiple-choice false-belief questions,
  stratified proportionally by ToM order (32 first-order / 18 second-order,
  matching the ~642:351 ratio of first- to second-order questions available
  in the `inaccessible` scenario). Choice ordering (which letter is correct)
  is randomized per item using the same logic as
  `eval_fantom.py::set_beliefQA_multiple_choices`, seeded for reproducibility.
- **50 `answerability_list` items** — "list all characters who know the
  correct answer" questions.
- **50 `info_access_list` items** — "list all characters who know this
  information" questions.

All three types are filtered to:
- `short_context` only (the condition the published human baseline was
  measured on — see `SCHEMA.md`)
- `missed_info_accessibility == "inaccessible"` only (the actual ToM test
  scenario that the published human-baseline numbers below correspond to,
  per `eval_fantom.py`'s `score_and_analyze(target_scenario='inaccessible')`
  — the `"accessible"` scenario is FANToM's control-question condition and
  was not sampled here)
- binary (Yes/No) question variants excluded entirely (no human baseline
  exists for them — see `SCHEMA.md`)
- deduplicated on `(set_id, question_type, question_text)`

Each item's exact fields, prompt-construction logic, and scoring functions
are reused verbatim from `reference/fantom/eval_fantom.py` — not
reimplemented from scratch. See `SCHEMA.md` for the full field spec.

## Human baseline (published aggregate, not re-derived)

11 CS graduate volunteers, same `short_context` condition, same instructions
as the models, no additional tutorials:

| Question type | Human baseline accuracy |
|---|---|
| `belief_choice` (BeliefQ[Choice]) | 93.8% |
| `answerability_list` (AnswerabilityQ[List]) | 90.6% |
| `info_access_list` (InfoAccessQ[List]) | 90.6% |

These are fixed aggregate constants attached to every item of that type —
FANToM's raw per-item human responses were never publicly released, so no
per-item human answer exists to attach instead.

## Deduplication and contamination notes

- No duplicate `(set_id, question_type, question_text)` triples exist in
  `items.json` — enforced at build time.
- **Contamination risk:** FANToM has been public since October 2023 and is
  very likely present in the training data of most current LLMs. Any future
  evaluation of frontier models against this item set should treat scores
  with that in mind — a model doing well may reflect memorization of FANToM
  itself, not durable theory-of-mind capability. `first_public_date` is
  attached to every item for exactly this purpose.

## Release note

The raw FANToM data (`raw_fantom/fantom_v1.json`, the full 870-set release)
is kept local to this project folder and is **not** intended for public
redistribution beyond what the authors' own "evaluation purposes only" note
permits. `items.json` (this 150-item derived subset) inherits the same
restriction. See `PROJECT_STATUS.md` / `HANDOFF.md` for the overall
licensing/release posture across both dataset categories.
