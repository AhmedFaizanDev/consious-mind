# ConsciousMind Dataset — Audit (updated 2026-09-23, post-reset)

Supersedes the 2026-09-22 audit, which covered the pre-reset two-category
structure. This covers the final structure: Category A (FANToM, unchanged)
+ Category B (final: Deflection Under Severity, new this session), with the
original CounselBench quality-rating framing retained as labeled
supplementary data, not a core category. See `README.md` for the reasoning
behind the reset and `REJECTED_CANDIDATES.md` for what else was considered.

## 1. Final item counts

| Category | Items | Role |
|---|---|---|
| A — Interactive Theory of Mind (FANToM) | 150 | Core |
| B — Deflection Under Clinical Severity | 100 | Core |
| **Core total** | **250** | |
| B (superseded) — CounselBench-Eval response-quality ratings | 200 | Supplementary only — see `category_b_safety_judgment/NOTE.md` |

## 2. Schema

**Category A** (`category_a_theory_of_mind/items.json`): unchanged from the
2026-09-22 audit — see that section preserved below in §2a.

**Category B, final** (`category_b_deflection_under_severity/items.json`):

| Field | Type | Description |
|---|---|---|
| `item_id` | str | `deflect_001`..`deflect_100`, unique |
| `questionID` | str | source CounselBench `questionID` |
| `topic` | str | CounselBench's own topic tag (20 topics × 5 questions each) |
| `questionTitle` / `questionText` | str / str-or-null | the real CounselChat question |
| `human_response` | str | the real licensed-therapist answer |
| `human_engaged_substantively` | bool | always `True` — the ground-truth anchor (proven, not assumed) |
| `gpt4_response` | str | GPT-4-0613's answer to the same question |
| `gpt4_is_canned_refusal` | bool | derived via a verified, deterministic rule (word-count band + phrase match, both independently confirmed to agree on all 100 items) |
| `source` | object | dataset name, derivation path, derivation rule (spelled out verbatim), license |

### 2a. Category A schema (unchanged from prior audit)

| Field | Type | Present on | Description |
|---|---|---|---|
| `item_id` | str | all | unique per item |
| `conversation_id` | str | all | FANToM's `set_id` |
| `question_type` | str | all | `belief_choice` / `answerability_list` / `info_access_list` |
| `context` | str | all | verbatim `short_context` |
| `question` | str | all | full question text |
| `correct_answer` / `wrong_answer` | str or list[str] | all | type-dependent |
| `tom_order` | str | `belief_choice` only | first/second-order |
| `human_baseline_accuracy` | float | all | fixed published constant |
| `license_note` / `first_public_date` | str | all | constants |

## 3. Ground truth per category

- **Category A:** FANToM's own author-provided answer key — programmatic,
  not re-derived.
- **Category B (final):** per-item, what's proven by the paired human
  response is that substantive engagement was *undertaken in practice* and
  *feasible* — not that any specific refusal was clinically wrong. The
  measured claim is a behavioral rate gap under matched conditions (100%
  human engagement vs. 66% model engagement / 34% refusal), not a
  clinical-correctness verdict on individual responses. Not assumed, not
  aggregate — but also not over-claimed as a safety judgment.

## 4. Human baseline

- **Category A:** fixed published aggregate (93.8% / 90.6% / 90.6%), 11 CS
  graduate volunteers, matched short-context condition. Not per-item.
- **Category B (final):** real, per-item, matched-condition — the `human`
  responder's own refusal rate on these exact 100 questions: **0/100
  (0%)**, directly comparable to GPT-4-0613's 34/100 (34%) on the same
  items under the same protocol.

## 5. Source and provenance

Unchanged for Category A (see prior audit / `category_a_theory_of_mind/SOURCE.md`).
Category B (final) derives entirely from already-verified, already-audited
data (`category_b_safety_judgment/items.json`, itself sourced from
`izi-ano/CounselBench-Eval` via direct REST API fetch, verified in the prior
audit) — no new external fetch, no new source to verify. Full derivation
rule documented in `category_b_deflection_under_severity/SOURCE.md` and
`build_log.md`.

## 6. Duplicate / consistency checks (all passed, re-verified this session)

**Category B (final):**
- 100/100 unique `item_id`; 100/100 unique `questionID` — no duplicates.
- `human_engaged_substantively` is `True` on all 100 items (the intended
  invariant — verified, not just asserted).
- `gpt4_is_canned_refusal` derivation rule (word-count band 41–45 AND
  phrase match) verified to produce an **identical** 34-item set via two
  independent methods; the build script asserts this equivalence on every
  item and would fail loudly, not silently, if a future edit broke it.
- The two shortest *human* responses (37, 42 words — the ones closest to
  the refusal-length band) were read directly and confirmed to be genuine
  substantive answers, not false negatives in the "0% human refusal" claim.
- No empty `human_response` or `gpt4_response` text in any of the 100 items.
- Field set is identical across all 100 items (no missing/extra fields).
- Reproducibility: `build_dataset.py` re-run this session, produced
  identical output.

**Category A:** re-verified intact, 150 items, unchanged from prior audit
(no modifications made this session).

## 7. Missing, ambiguous, or malformed records

None found in either core category. The two pre-existing data-quality notes
from the prior audit (22/200 items in the superseded `category_b_safety_judgment`
with null `questionText`; 18/200 with raw HTML markup) still apply to that
supplementary folder only — they do not affect either core category, since
Category B (final) uses `questionTitle`/`response` text that was confirmed
present and non-empty on all 100 items.

## 8. Licensing and redistribution

Unchanged from the prior audit's determination — see `README.md`'s
licensing section for the current, condensed version. Both categories:
internal research use is clear; public redistribution requires author
clearance (FANToM: "evaluation purposes only" note; CounselBench-Eval:
CC-BY-NC-ND-4.0). This applies identically to the new Category B derivation,
since it inherits CounselBench-Eval's license — nothing about re-deriving a
refusal flag from already-licensed response text changes that license.

## 9. What this dataset is intended to measure, and what it does not establish

See `README.md`'s dedicated section — kept there rather than duplicated
here, since it is the primary entry point for a new reader.

## Final determination

**The dataset (250 core items across two categories) is internally
complete, evidence-verified against primary sources rather than assumed,
and ready to move to the evaluation phase**, subject to the license and
scope caveats above. No fabricated, synthetic, or placeholder items exist
anywhere. The one correction made during this audit (Category B's refusal
count: 18 → 34) was verified via an independent, reproducible method before
being adopted, not asserted. No data was deleted; the superseded framing is
preserved and clearly labeled.
