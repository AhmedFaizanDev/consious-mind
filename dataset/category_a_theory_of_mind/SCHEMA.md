# Category A: Interactive Theory of Mind — Intended Schema (ready to populate)

This defines exactly how Category A should be built the moment FANToM's raw
data is available (see `BLOCKED.md`). Nothing here is speculative — every
field, prompt, and scoring rule below was confirmed by directly reading
`skywalker023/fantom`'s source code (`eval_fantom.py`,
`task/dataset_loader.py`) in an earlier turn of this project, not inferred
from the paper alone.

## Source

- **Dataset:** FANToM (Kim et al., EMNLP 2023)
- **License:** MIT (code repository); the dataset itself carries an
  additional "evaluation purposes only" usage note from the authors.
- **Human baseline:** 11 CS graduate volunteers, same `short_context`
  condition, same instructions as models, no additional tutorials — accuracy
  93.8% (BeliefQ[Choice]), 90.6% (AnswerabilityQ[List]), 90.6%
  (InfoAccessQ[List]), 87.5% (strict all-correct "All" metric). Binary (Y/N)
  question variants have **no** human baseline and should be excluded from
  any human-comparison task built from this category.

## Item fields (per task item)

```
item_id                str    e.g. "fantom_001"
conversation_id         str    FANToM's own set_id
question_type            str    one of: "belief_choice", "answerability_list", "info_access_list"
context                  str    the "short_context" field (verbatim, do not alter)
question                 str    the question text (for belief_choice, includes the multiple-choice options exactly as FANToM formats them)
correct_answer            (varies by type — see scoring below)
wrong_answer               (varies by type)
human_baseline_accuracy    float  fixed reference value: 0.938 / 0.906 / 0.906 by type (aggregate, not per-item — FANToM's raw per-item human responses were never released)
license_note              str    "MIT (code); dataset for evaluation purposes only per author note"
first_public_date          str    "2023-10" (EMNLP 2023) — for contamination-risk tracking
```

## Exact prompt template (verbatim, do not paraphrase)

Header, prepended to every item:
```
This is a theory-of-mind test. Please answer the question regarding facts or beliefs, based on the following in-person conversation between individuals who have just met.

```

Per-type body:
- **BeliefQ[Choice]:** `{context}\n\nQuestion: {question}\n{choices_text}\n\nChoose an answer from above:`
- **AnswerabilityQ[List]:** `{context}\n\nTarget: {fact_question}\nQuestion: {question}\nAnswer:`
- **InfoAccessQ[List]:** `{context}\n\nInformation: {fact_question} {fact_answer}\nQuestion: {question}\nAnswer:`

No system prompt beyond the header above — this matches what the 11 human
volunteers were given (single user turn, no extra instructions).

## Scoring (reuse verbatim from `eval_fantom.py`, do not reimplement)

- **BeliefQ[Choice]:** `evaluate_mc_belief_q` — response must start with the
  correct letter in one of these forms: `a)`, `a.`, `a:`, `(a)`, or the bare
  letter `a`.
- **AnswerabilityQ[List] / InfoAccessQ[List]:** `evaluate_list_q` — every
  character name in `correct_answer` must appear (case-insensitive
  substring) in the response, AND no character name from `wrong_answer` may
  appear. Binary pass/fail.

## Construction steps once data is available

1. Load the extracted FANToM data (JSON, grouped by `set_id`).
2. Filter to `conversation_input_type == "short"` only (the human-baselined
   condition — do not use the `"full"` condition, which has no human
   comparison).
3. Extract items of the three question types listed above; discard the two
   binary (Y/N) variants (no human baseline exists for them).
4. Deduplicate on `(set_id, question_type, question_text)`.
5. Populate the fields above; attach the fixed human-baseline constants
   (do not attempt to re-derive a human accuracy figure — none exists
   beyond the published aggregate).
6. Flag every item with `first_public_date: "2023-10"` for downstream
   contamination-risk handling — this dataset has been public for multiple
   years and is very likely present in current LLM training data.

No sampling strategy is prescribed here beyond what the earlier pilot design
already specified (50 items per type, stratified, seed=42) — that
specification still stands and should be applied once real data exists.
