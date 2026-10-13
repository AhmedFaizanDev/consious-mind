# ConsciousMind Dataset — One-Page Summary

**Goal:** a dataset of tasks/items for which there is documented evidence of
a meaningful human advantage over AI/LLMs. Two categories, 250 items total.
Built entirely from real, previously-published, human-baselined data — no
items were generated, simulated, or fabricated, no LLM APIs were called, no
human studies were run for this build.

## What the dataset contains

| Category | Task | Items |
|---|---|---|
| **A — Interactive Theory of Mind** (FANToM, Kim et al., EMNLP 2023) | Given a short conversation, determine what a specific character does or doesn't believe/know, having missed part of it | 150 |
| **B — Deflection Under Clinical Severity** (derived from CounselBench-Eval) | Given a real mental-health question, does the respondent substantively engage or deflect with a non-answer? | 100 |

## What evidence supports human advantage

- **Category A:** a published, peer-reviewed, matched-condition study —
  11 human volunteers and multiple LLMs given the identical input and
  instructions. Humans scored 93.8% / 90.6% / 90.6% across the three
  question types; GPT-4o scored 49.7% / 41.7% / 21.7% on the same tasks.
  A 44–69 point gap, independently published, not produced by this project.

- **Category B:** on 100 real CounselChat questions, a licensed therapist
  gave a substantive answer to every single one (100/100) under real
  professional and reputational constraints. GPT-4-0613, asked the same
  100 questions, gave a non-substantive canned refusal on 34/100 (34%) —
  a rate that rises with topic severity (100% on depression questions,
  0% on administrative/relationship questions). **Precise claim:** this is
  a measured *behavioral engagement-rate gap* under matched conditions. It
  is *not* a claim that any individual GPT-4 refusal was clinically wrong
  — a professional choosing to engage proves engagement was feasible, not
  that declining was incorrect. The dataset measures the rate, not the
  correctness of any single decision.

## What is specific to historical model snapshots (not general "AI")

- Category A's model comparison point is GPT-4o-2024-05-13, and the
  finding is that the gap had **not closed** between 2023 GPT-4 and 2024
  GPT-4o — a two-generation stability check, not a claim about 2026 models.
- Category B's 34% refusal rate is a property of **one specific 2023 model
  checkpoint** (GPT-4-0613). It is evidence motivating a hypothesis — that
  this kind of over-cautious deflection can occur — not a claim that
  current or future models behave the same way.

## What has not yet been tested on current models

**Nothing in this dataset has been run against any 2026-era model.** No LLM
API calls were made during construction. Both categories provide the
machinery (items, ground truth, human baseline) to test current models —
that evaluation is the deliberate next step, explicitly out of scope here.

## Other honest limits

- Both source datasets are likely present in current LLM training data
  (FANToM public since 2023, CounselChat since 2019) — contamination is a
  live, untested alternative explanation for any future result.
- Category A's human baseline is a fixed published aggregate, not raw
  per-item data (none was ever released) — supports comparing a model's
  overall accuracy to the baseline, not per-item statistical testing.
- Six additional high-profile 2025–2026 "humans beat AI" benchmarks (e.g.
  ARC-AGI-2, GAIA, Humanity's Last Exam) were checked directly against
  primary sources and rejected — each had either closed, inverted, or
  turned out to lack a genuine human baseline once verified beyond
  secondary summaries (`dataset/REJECTED_CANDIDATES.md`).
- Licensing: both categories are internal-research-use only. FANToM
  carries an "evaluation purposes only" author note; CounselBench-Eval is
  CC-BY-NC-ND-4.0. Neither is cleared for public redistribution.

## Location

`/Users/faizan/RootVault/ conscious-mind/dataset/` — start at `README.md`
for the full write-up, `AUDIT.md` for the field-level integrity audit.
