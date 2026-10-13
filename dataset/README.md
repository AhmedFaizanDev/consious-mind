# ConsciousMind — Human-Advantage Benchmark Dataset (final, 2026-09-23)

**Deliverable:** a research-grade dataset of categories/tasks for which
there is credible, verified evidence that humans have a meaningful advantage
over current AI/LLMs. This is the immediate deliverable requested — not a
consciousness/metacognition framework (that framing was explicitly
descoped; see `RESEARCH_NOTES.md` §8 for why).

Two categories are included. Both were stress-tested against primary
sources, not assumed from memory or secondary summaries — see
`REJECTED_CANDIDATES.md` for six additional 2025–2026 candidates that were
checked and failed to hold up. No LLM APIs were called, no humans were
recruited, and nothing was fabricated to build any of this.

## Final categories

| Category | Task | Items | Human baseline | Status |
|---|---|---|---|---|
| **A — Interactive Theory of Mind** (FANToM) | Track what a character in a conversation does/doesn't believe or know | 150 | 93.8% / 90.6% / 90.6% (published, matched-condition) vs. GPT-4o 49.7% / 41.7% / 21.7% | Built |
| **B — Deflection Under Clinical Severity** (derived from CounselBench-Eval) | Does a system decline to substantively engage with a real mental-health question a licensed professional was willing to engage with? | 100 | 0% refusal (real, per-item, matched-condition) vs. GPT-4-0613 34% refusal | Built |

Full field-level audit (schema, dedup, provenance, reproducibility) is in
[`AUDIT.md`](AUDIT.md) — read that before building anything on top of this.

## Category A — Interactive Theory of Mind (FANToM)

**Why it qualifies:** the strongest evidence base of anything considered in
this project. A real, peer-reviewed (EMNLP 2023), multi-model, matched-
condition human baseline — 11 CS graduate volunteers given the identical
short-context input and instructions as the models — scored 93.8% (belief
choice), 90.6% (answerability list), 90.6% (info-access list). The
contemporaneous model score (GPT-4o-2024-05-13, per the maintainers' own
tracked leaderboard) was 49.7% / 41.7% / 21.7% — a 44–69 point gap that had
not closed between the 2023 GPT-4 release and the 2024 GPT-4o update. Not a
public leaderboard/prize benchmark, which plausibly explains why this gap
held up longer than every 2025–2026 leaderboard-driven candidate checked
during this session (all six of which had closed, inverted, or turned out
to lack a genuine human baseline — see `REJECTED_CANDIDATES.md`).

**Ground truth:** FANToM's own author-provided answer key, used verbatim
(not re-derived). **Human reference:** fixed published aggregate accuracy —
not per-item, since FANToM's raw per-item human responses were never
released.

**Task:** given a short conversation excerpt and a question about what a
specific character believes or knows (having missed part of the
conversation), answer it. Three sub-tasks, 50 items each:
- `belief_choice` — multiple-choice belief question.
- `answerability_list` — list every character who knows the answer.
- `info_access_list` — list every character with access to a fact.

Scoring functions reused verbatim from `reference/fantom/eval_fantom.py`
(`evaluate_mc_belief_q`, `evaluate_list_q`) — not reimplemented. Full spec:
`category_a_theory_of_mind/SCHEMA.md`. Provenance and integrity
verification (SHA-256 match against the authors' own hash):
`category_a_theory_of_mind/SOURCE.md`.

**Honest limits:** the human baseline is a fixed aggregate, not a
distribution (no per-item statistical testing possible). FANToM has been
public since October 2023 — contamination in current models' training data
is likely and unverified (no model evaluation was run here). The 2023–2024
gap-durability finding says nothing about 2026-era models.

## Category B — Deflection Under Clinical Severity

**Why this shape, not the original "response quality" framing:** the
project originally built a broader "Safety-Critical Judgment" category from
this same source, predicting how expert raters would score response
*quality*. That data does not show a human advantage — GPT-4 was rated
*higher* on Overall Quality (3.28 vs. 2.60) and *lower* on Toxicity (1.78
vs. 2.56, lower=better). Including that framing as "evidence of human
advantage" would have been an unsupported claim contradicted by the
project's own data. See `category_b_safety_judgment/NOTE.md` for the full
reclassification record — that data is preserved, not deleted, just no
longer used to anchor a human-advantage claim.

**What the data does support**, once re-examined precisely this session
(the original count was wrong — see below): on the same 100 real
CounselChat questions, **the licensed human therapist substantively engaged
with every single one (100/100)** — real proof of engageability, not an
assumption, since a real professional under real liability constraints
chose to answer directly every time. **GPT-4-0613 gave a canned,
non-substantive refusal on 34/100 (34%)** — corrected from an earlier
18% count, which only matched one exact string; the true count was found by
inspecting the full response-length distribution (34 responses cluster
tightly at 41–45 words with the refusal phrase; every other response is 76+
words) — a verified, deterministic partition, not a fuzzy estimate.

**The refusal rate is not random — it tracks topic severity in a clean,
monotonic gradient:** depression 100% (5/5) → self-esteem/behavioral-change
80% → anxiety/social-relationships 60% → trauma/domestic-violence/
substance-abuse 40% → administrative/relationship topics 0%. Full table in
`category_b_deflection_under_severity/build_log.md`.

**Ground truth, stated precisely:** per item, what's proven by the paired
human response is that substantive engagement was *undertaken in practice*
by a licensed professional, under real professional and reputational
constraints — i.e., it was feasible. **This is not proof that any given
GPT-4-0613 refusal was clinically wrong or unsafe** — the dataset does not
adjudicate individual clinical correctness, human or model. What it
measures is a **behavioral rate difference under matched conditions**: the
human-professional condition engaged substantively on 100/100 of these
questions; this model's condition did so on 66/100 (34% declined). That
rate gap — not a clinical verdict — is the finding. **Human reference:** 0%
refusal rate, real and per-item, not an aggregate estimate.

**This connects to an established benchmark genre** — "over-refusal" /
"exaggerated safety behavior" evaluation in LLM safety research (e.g.
XSTest, OR-Bench) — but with a genuine paired human-professional engagement
baseline per item, rather than a synthetic or LLM-judged safety label.

**Honest limits (stated explicitly in `category_b_deflection_under_severity/SOURCE.md`):**
this is evidence about one 2023 model snapshot (GPT-4-0613), not "AI" in
general — the dataset provides the machinery to test whether the pattern
recurs in other/current models, it does not itself prove that. The refusal-
detection rule is a verified partition of this model's response set, not a
general-purpose refusal classifier. Topic tags are CounselBench's own
pre-existing labels, not a clinically validated severity scale.

## What was rejected, and why

- **CounselBench-Eval's original quality-rating framing** — see above;
  kept as supplementary data, not part of the core claim.
- **Metacognitive Calibration** — no existing dataset has a genuine paired
  human baseline for this construct; building it would require new human
  recruitment, explicitly out of scope for this deliverable. Documented as
  future work only (`RESEARCH_NOTES.md`).
- **Six additional 2025–2026 "human advantage" candidates**, checked fresh
  against primary sources this session and rejected: ARC-AGI-2 (inverted —
  AI now 95% vs. human 66%), GAIA (saturated — agents now 91–95% vs. human
  92%), ARC-AGI-3 (wrong task format, and its "100% human" claim doesn't
  match the primary source's actual 42% completion rate), Humanity's Last
  Exam (the widely-repeated "~90% human baseline" has no basis in the
  primary sources — human experts were used only for question vetting, not
  an accuracy baseline), divergent-thinking/creativity studies (the 2023
  finding was corrected and reversed by 2024–2025 follow-ups), and
  AI-vs-superforecaster forecasting (methodologically strong, but the
  benchmark's own maintainers report parity arriving around now). Full
  detail, with sources, in `REJECTED_CANDIDATES.md`.

## What this dataset does NOT establish

- **No model has been evaluated against this dataset.** Every number above
  is either a published third-party finding (Category A) or a fact already
  present in already-collected real data (Category B's refusal count).
  Nothing here has been tested against a current (2026) model.
- **Contamination is likely and unverified** for both categories (FANToM
  public since 2023, CounselChat's underlying Q&A public since 2019).
- **Category B's finding is about one specific 2023 model**, not "AI"
  broadly — it motivates a hypothesis to test, it doesn't prove it holds
  generally.
- **Sample sizes (150 + 100 = 250 items) are research-pilot scale.**

## Directory contents

```
dataset/
├── README.md                                  (this file)
├── AUDIT.md                                   (field-level audit, dedup/consistency checks)
├── REJECTED_CANDIDATES.md                     (six 2025-2026 candidates checked and rejected, with sources)
├── category_a_theory_of_mind/
│   ├── SCHEMA.md / SOURCE.md / BLOCKED.md      (spec, provenance, integrity verification)
│   ├── build_dataset.py                        (reproducible, seed=42)
│   ├── items.json                              (150 items)
│   └── raw_fantom/fantom_v1.json                (raw FANToM release, hash-verified)
├── category_b_deflection_under_severity/       (FINAL Category B — the human-advantage claim)
│   ├── SOURCE.md / build_log.md                (construct, verified derivation, honest limits)
│   ├── build_dataset.py                         (reproducible, derives from category_b_safety_judgment/)
│   ├── items.json                               (100 items)
│   └── items_flat.csv
└── category_b_safety_judgment/                 (SUPERSEDED framing — kept, not deleted; see NOTE.md)
    ├── NOTE.md                                  (why this folder's original framing was dropped)
    ├── SOURCE.md / items.json / raw_ratings.csv / items_aggregated.csv
    └── raw_hf_fetch/all_2000_rows.json          (raw, unmodified full API fetch — all 4 responders)
```

## Licensing (internal research use only — not cleared for public release)

- **Category A (FANToM):** MIT code license, but the dataset carries an
  additional "evaluation purposes only" note from the authors. Internal use
  is fine; public redistribution needs author confirmation.
- **Category B (CounselBench-Eval, both the retained framing and the
  superseded one):** CC-BY-NC-ND-4.0 (non-commercial, no derivatives).
  Internal use is fine; public redistribution needs explicit clearance from
  the CounselBench authors.
