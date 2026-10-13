# ConsciousMind — Handoff

One document: what's done, exactly how it was done, and what's left to reach
a final dataset. `PROJECT_STATUS.md` is the short version of this;
`RESEARCH_NOTES.md` is the full research trail (literature review, category
stress-testing, rejected candidates). This file is the work log.

**2026-09-23 update:** the deliverable was reset to its actual scope — a
human-advantage benchmark, not a consciousness/metacognition framework. Read
`RESEARCH_NOTES.md` §8 and `dataset/README.md` first; the sections below
describe the pre-reset build and are kept for provenance, but Category B's
framing described there (§1.3's "Category B — Safety-Critical Judgment")
has been superseded by `dataset/category_b_deflection_under_severity/`.

---

## 0. 2026-09-23 session — scope reset and final construction

**What changed:** the professor's actual deliverable — a dataset of
categories with credible evidence of human advantage over AI — was
re-audited against a strict "no unsupported claims" bar.

- **Category A (FANToM):** unchanged, re-verified intact. Still the
  strongest evidence base in the project.
- **Category B:** rebuilt. The original CounselBench-Eval "response
  quality" framing was retired — the data shows GPT-4 rated *higher* on
  Overall Quality and *lower* on Toxicity than the human therapist, so it
  does not support a human-advantage claim. In its place: **Deflection
  Under Clinical Severity**, built from the same already-collected data.
  Re-deriving the refusal signal precisely (word-count-band + phrase-match,
  cross-verified to agree exactly) found the true GPT-4-0613 canned-refusal
  rate is **34/100 (34%)**, not the 18% originally reported — the original
  detection only matched one exact string. Human refusal rate: 0/100 (0%),
  verified per-item, not assumed. The refusal rate tracks a clean,
  monotonic topic-severity gradient (depression 100% → mundane topics 0%)
  — see `dataset/category_b_deflection_under_severity/build_log.md`. **This
  measures a behavioral engagement-rate gap, not a clinical-correctness
  verdict** — a professional engaging proves engagement was feasible/
  undertaken, not that a model's refusal was clinically wrong (2026-09-23
  wording correction, prompted by a professor-facing review — see
  `dataset/category_b_deflection_under_severity/SOURCE.md`).
- **Six additional 2025–2026 "humans beat AI" benchmarks were researched
  fresh** (ARC-AGI-2, GAIA, ARC-AGI-3, Humanity's Last Exam, divergent-
  thinking/creativity studies, AI-vs-superforecaster forecasting) and all
  six were rejected after checking primary sources directly — every one had
  either closed, inverted, or turned out to lack a genuine human baseline
  once verified beyond secondary/blog summaries. Full detail with sources
  in `dataset/REJECTED_CANDIDATES.md`.
- **Nothing was deleted.** The original `category_b_safety_judgment/` data
  is preserved in full, relabeled via `NOTE.md` as supplementary (not a
  core human-advantage category), consistent with "preserve original data
  and provenance."
- **Final core dataset: 250 items (150 + 100) across 2 categories.**
  Integrity/dedup/reproducibility checks re-run and passed — see
  `dataset/AUDIT.md`.

---

## 1. What has been done (pre-reset build — see §0 for what superseded this)

### 1.1 Research and category selection (complete)

Started from a broad question — where do LLMs genuinely not outperform
humans, in domains connected to consciousness/metacognition/self-awareness/
emotion/mental health/social reasoning — and narrowed it through several
rounds of stress-testing against real evidence, not assumption:

- Reviewed the seed literature map (OpenCausaLab/Awesome-LLM-Consciousness)
  plus supplementary primary sources.
- Produced an initial shortlist of 3 candidate categories: Interactive
  Theory of Mind, Safety-Critical Judgment (mental-health counseling
  quality), and Metacognitive Calibration.
- Stress-tested each against actual released data/code (not paper abstracts):
  checked whether a real human baseline exists, whether the data is
  reachable/reusable, licensing, contamination risk, and whether a fair
  human-vs-LLM comparison is even possible.
- **Result:** Theory of Mind (FANToM) and Safety-Critical Judgment
  (CounselBench) survived with strong evidence. Metacognitive Calibration
  was deprioritized — the literature search found no existing dataset with
  a paired human baseline for calibration, so building it would require
  assuming a human-favoring gap rather than measuring one. It is documented
  as a future candidate, not built.

Full reasoning, rejected alternatives (Hi-ToM, ExploreToM, SelfAware, generic
empathy benchmarks), and exact numbers are in `RESEARCH_NOTES.md`.

### 1.2 Direct source audits (complete)

Both final sources were audited by cloning and reading their actual code,
not just their papers:

- **FANToM** (`reference/fantom/`, cloned from `skywalker023/fantom`, MIT
  license): read `eval_fantom.py` for exact prompts and scoring functions,
  `task/dataset_loader.py` for how the data is actually loaded and where it's
  hosted. Confirmed the human baseline: 11 CS graduate volunteers, same
  short-context condition as the models, accuracy 93.8% (BeliefQ[Choice]),
  90.6% (AnswerabilityQ[List] and InfoAccessQ[List]), 87.5% (strict "All"
  metric) — versus GPT-4o-2024-05-13 at 49.7% / 41.7% / 21.7% / 2.0%.
- **CounselBench** (`reference/CounselBench/`, cloned from
  `llm-eval-mental-health/CounselBench`): read the prompt templates, scoring/
  significance-test code, and rubric definitions directly. Confirmed
  CounselBench-Eval is 2000 rows = 100 questions × 4 responders (gpt4,
  llama3, gemini, human) × 5 expert raters, rated on Overall/Empathy/
  Specificity/Medical-advice/Factual-consistency/Toxicity, with a genuine
  paired human-response condition (`responder="human"`).

### 1.3 Dataset construction (both categories complete — updated 2026-09-22)

Per your instruction to stop the LLM pilot and build the actual dataset from
verified sources, `dataset/` was built with reproducible, auditable code —
no fabricated or simulated data anywhere.

**Category A — Interactive Theory of Mind (`dataset/category_a_theory_of_mind/`) — built (was blocked, now resolved):**
- The earlier "blocked" status was specific to the cloud sandbox that did
  the original research/audit work — its egress policy blocked
  `storage.googleapis.com` outright. Run from this local machine (normal
  network access), a direct `curl` of the same URL
  (`https://storage.googleapis.com/ai2-mosaic-public/projects/fantom/fantom.tar.gz`)
  succeeded on the first attempt (HTTP 200, 1,040,898 bytes), and its
  SHA-256 matched the hash hardcoded in the authors' own
  `reference/fantom/task/dataset_loader.py` exactly — confirming an
  authentic, unmodified copy of the release, not a workaround or mirror.
- Extracted to `dataset/category_a_theory_of_mind/raw_fantom/fantom_v1.json`
  (870 conversation sets, the full real release).
- Built 150 items (50 `belief_choice`, 50 `answerability_list`, 50
  `info_access_list`) via `dataset/category_a_theory_of_mind/build_dataset.py`
  — deterministic, seed=42, fully reproducible (re-running the script
  produces byte-identical `items.json`). Followed `SCHEMA.md` exactly: only
  `short_context`, only the `missed_info_accessibility == "inaccessible"`
  scenario (the one the published human baseline was measured on), binary
  Y/N variants excluded, deduped on `(set_id, question_type, question_text)`,
  belief items stratified by ToM order (32 first-order / 18 second-order,
  proportional to availability), multiple-choice construction and prompt
  templates reused verbatim from `reference/fantom/eval_fantom.py`.
- Provenance, integrity verification, and license posture documented in
  `dataset/category_a_theory_of_mind/SOURCE.md`. `BLOCKED.md` is kept as the
  historical record of what was tried before, with a status update at the
  top pointing to the resolution.

**Category B — Safety-Critical Judgment (`dataset/category_b_safety_judgment/`) — built (extended from 38 to full 100 questions):**
- Original pilot: CounselBench-Eval, fetched live from Hugging Face's
  `datasets-server.huggingface.co` REST API via the `WebFetch` tool (the
  only reachable path from the original cloud sandbox — direct
  `huggingface.co`/`curl` access was blocked there). 38 of the first 40
  questions succeeded (2 hit rate-limiting) — documented in
  `dataset/build_dataset.py` (kept as the historical build) and
  `dataset/build_log.md`.
- **Extended 2026-09-22:** run from this local machine (normal network
  access), a direct `curl` of the same REST API retrieved **all 2000 rows**
  (100 questions × 4 responders × 5 raters) cleanly in 20 calls of
  `length=100` (the API's per-request cap) — no truncation, no
  rate-limiting, confirming those were quirks of the earlier `WebFetch` path,
  not of the API itself. Raw rows saved verbatim to
  `dataset/category_b_safety_judgment/raw_hf_fetch/all_2000_rows.json`.
- `dataset/build_dataset_full.py` rebuilt the dataset from that raw fetch
  (no hardcoded records, fully reproducible offline) for all 100 questions ×
  2 responders (`human`, `gpt4`) = 200 rated items, 1000 raw rater
  judgments — same filtering logic as the original build (only
  human/gpt4; llama3/gemini rows exist in the raw fetch for future work).
- Provenance, license (CC-BY-NC-ND-4.0 — flagged as needing resolution
  before any public release), and the full verbatim rubric are documented in
  `dataset/category_b_safety_judgment/SOURCE.md`.
- The full 100-question pull confirms the same non-cherry-picked signal
  found in the original 38-question sample: mean Overall score 2.602
  (human) vs 3.284 (GPT-4) on a 1–5 scale where GPT-4 rates itself/is rated
  higher; mean Toxicity 2.564 (human) vs 1.778 (GPT-4, lower = less toxic);
  and GPT-4 gave a canned refusal response on 18 of 100 (18.0%)
  distress-related questions — nearly identical to the 18.4% found in the
  smaller pilot, confirming this wasn't a sampling artifact.

### 1.4 Consolidation (complete)

Everything above — both dataset categories, the two reference repos
(`.git` stripped), `PROJECT_STATUS.md`, and `RESEARCH_NOTES.md` — has been
written directly into this connected folder
(`/Users/faizan/RootVault/ conscious-mind`) so it's ready to open in Claude
Code as-is.

---

## 2. What's left (updated 2026-09-22 — no true blockers remain)

Both categories are built from real, verified, auditable data. What remains
is judgment calls, not missing engineering:

1. **Resolve licenses before any public release.** CounselBench-Eval is
   CC-BY-NC-ND-4.0 (non-commercial, no derivatives); FANToM's dataset
   carries an "evaluation purposes only" author note on top of its MIT code
   license. Both are fine for internal research use as-is. If the dataset
   is ever meant to be shared or published beyond the team, both need
   explicit clearance from their respective authors first.

2. **Decide on Metacognitive Calibration (optional, not required for
   "final").** Deliberately not built — no existing dataset with a genuine
   paired human baseline was found. If a third category is wanted, the next
   step isn't sourcing an existing dataset; it's designing a small original
   paired human pilot first, since assuming the human-favoring direction
   here would be exactly the kind of unverified assumption this whole
   project has been avoiding.

3. **The staged LLM pilot (Stage 1 → gate → Stage 2) is still unrun against
   both categories.** This was the original execution goal before the
   project redirected to dataset-building; it's the natural next milestone
   now that both categories have real data — but it's a separate
   deliverable from "the dataset exists and is well-sourced," which is now
   true.
