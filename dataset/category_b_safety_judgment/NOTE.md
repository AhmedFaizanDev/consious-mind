# Reclassified 2026-09-23 — read before using this folder

**This data is preserved exactly as built — nothing deleted, nothing
relabeled, no scores altered.** This note only changes how it should be
*used*.

## What changed

This folder was originally framed as "Category B: Safety-Critical Judgment"
— the idea being that response-quality ratings (Overall, Empathy,
Specificity, Factual Consistency, Toxicity) would show humans rated higher
than GPT-4. **The data does not support that claim:**

- Mean Overall: human 2.60 vs. gpt4 3.28 (gpt4 rated *higher*)
- Mean Toxicity (lower = better): human 2.56 vs. gpt4 1.78 (gpt4 rated
  *less* toxic)

On every rated quality dimension in this dataset, GPT-4-0613 does not lose
to the human therapist baseline. Presenting this data as "humans give
higher-quality mental-health responses" would be an unsupported claim the
data itself contradicts.

## What's still real and usable here

- The response-quality ratings themselves are real, expert-collected,
  reliable data (Krippendorff's α ≥0.7 in the original study) — useful for
  other research questions (e.g., studying LLM-judge inflation, or as a
  general mental-health-response-quality resource), just not for a
  human-advantage claim.
- **One genuine, evidenced human-advantage signal was found in this exact
  data** and has been extracted into its own properly-scoped category:
  `../category_b_deflection_under_severity/` — GPT-4-0613 gave a canned
  non-substantive refusal on 34/100 questions (not the 18 originally
  reported — recount corrected this session), 0/100 for the human
  therapist, with the refusal rate tracking topic severity. That is the
  category to use for the "human advantage" benchmark, not this folder's
  aggregate quality scores.

## Why this folder is kept rather than deleted

Per project convention: preserve original data and provenance rather than
silently discarding a build. This folder remains the source data that
`category_b_deflection_under_severity/build_dataset.py` derives from — it is
infrastructure for that category now, not a standalone deliverable.
