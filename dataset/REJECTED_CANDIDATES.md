# Candidate human-advantage categories researched and rejected (2026-09-23)

Before finalizing the dataset, the major current "humans beat AI" benchmarks
were checked directly against primary sources rather than assumed from
general knowledge or secondary blog summaries. Every one of them either
failed on evidence quality or has already closed/inverted as of the current
date. This is recorded so a future session doesn't have to re-run the same
search and re-discover the same dead ends.

**Pattern worth noting:** every headline, prize-money/leaderboard-driven
"humans beat AI" benchmark checked here has closed or inverted within about
12–18 months of going viral — precisely because a famous public gap becomes
an optimization target for frontier labs. FANToM (the one category kept) is
not a public leaderboard/prize benchmark, which may be part of why its
published 2023–2024 gap held up longer than any of these.

## ARC-AGI-2 — REJECTED (inverted)

- **Claim checked:** human panel ~60–66% vs. LLMs starting near 0%.
- **Verified:** true at launch (2025). As of September 2026, the top model
  (per public leaderboard tracking) scores 95% vs. a human baseline of 66%
  — a 29-point gap **in AI's favor**. The finding has fully inverted.
- **Source:** [ARC-AGI-2 leaderboard, BenchLM.ai, Sept 2026](https://benchlm.ai/benchmarks/arc-agi-2); [ARC-AGI-2 technical report](https://arxiv.org/pdf/2505.11831).

## GAIA — REJECTED (saturated)

- **Claim checked:** original paper reported human 92% vs. GPT-4-with-plugins 15%.
- **Verified:** true in the 2023 paper. As of 2026, top agent scaffolds
  score 91–95% on the same 466-item set — at or above the original human
  baseline. No longer a human-advantage benchmark; now a benchmark of agent
  scaffolding quality.
- **Source:** [GAIA paper](https://arxiv.org/pdf/2311.12983); [GAIA leaderboard, Sept 2026](https://benchlm.ai/benchmarks/gaia).

## ARC-AGI-3 — REJECTED (wrong format + high fragility risk)

- **Claim checked (from secondary sources):** "humans solve 100%, AI <1%."
- **Verified against the primary source (ARC Prize's own human-baseline
  blog post):** the actual measured completion rate was 42% (145/342
  first-attempt plays across 25 public demo tasks), not 100% — the "100%"
  claim conflates *solvability* ("every task beaten by at least 2 of 458
  participants") with *average accuracy*, which are very different claims.
  This is exactly the kind of unverified secondary-source number this
  project's standards exist to catch.
- **Also rejected on format grounds:** ARC-AGI-3 requires an interactive,
  rendered game environment (participants take actions and observe results
  over multiple steps), not a static text/data item — outside this
  project's text-only, static-item dataset scope, and would require
  building an interactive eval harness rather than assembling a dataset.
- **Also rejected on durability grounds:** released April 2026, essentially
  brand new; given ARC-AGI-2's ~12-month collapse from "single digits" to
  "95%," a benchmark this new and this publicly targeted (own Kaggle prize
  competition) has a high near-term risk of the same trajectory.
- **Source:** [ARC Prize: Measuring Human Performance on ARC-AGI-3](https://arcprize.org/blog/arc-agi-3-human-dataset).

## Humanity's Last Exam (HLE) — REJECTED (no genuine human baseline exists)

- **Claim checked (widely repeated in secondary/blog sources):** "human
  domain experts average ~90% accuracy."
- **Verified against primary sources (arXiv paper, Wikipedia article):**
  **no independent human-cohort accuracy baseline was ever collected.**
  Human experts were used only for *question vetting* (filtering/QC during
  dataset creation, in two review rounds) — a fundamentally different thing
  from a matched-condition human test-taking baseline. The "~90%" figure
  circulating in secondary sources could not be traced to any primary-source
  methodology and appears to be a misattribution or fabrication propagating
  through derivative content.
- **Why this matters:** this is exactly the failure mode this project is
  built to avoid — a plausible-sounding, widely-repeated "human beats AI"
  number with no real matched-condition data behind it. Including it would
  have been indefensible under direct questioning.
- **Source:** [HLE paper, arXiv](https://arxiv.org/abs/2501.14249); [Wikipedia — Humanity's Last Exam](https://en.wikipedia.org/wiki/Humanity%27s_Last_Exam) (no human-baseline methodology found in either).

## Divergent-thinking / creativity (Alternative Uses Task) — REJECTED (contested, reversed)

- **Claim checked:** Koivisto & Grassini 2023 (*Scientific Reports*) —
  "best humans still outperform AI" on creative divergent thinking.
- **Verified:** the original paper received a correction (Feb 2024) for
  data-analysis errors, and multiple follow-up studies since (2024–2025,
  also in *Scientific Reports*) found the opposite — generative AI models
  outperforming humans/students on the same task family on average. The
  literature is actively contested and has trended against the
  human-advantage finding since 2023. Not stable enough to build a dataset
  category on.
- **Source:** [Original paper](https://www.nature.com/articles/s41598-023-40858-3); [correction](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10879133/); [2025 reversal finding](https://www.nature.com/articles/s41598-025-21398-4).

## Forecasting (superforecasters vs. LLMs, ForecastBench) — REJECTED (closing to parity now)

- **Claim checked:** superforecasters outperform LLMs on real-world binary
  event forecasting (Brier score), e.g. superforecaster 0.096 vs. top LLM
  0.122–0.130 on ForecastBench.
- **Verified:** real, well-designed, genuinely contamination-resistant
  (questions concern unresolved future events) — methodologically the
  strongest of the rejected candidates. But the benchmark's own maintainers
  report other systems "have likely reached parity with superforecasters,"
  with one system already ranking above the superforecaster median on
  market questions, and project LLM-superforecaster parity for **late
  2026** — i.e., approximately now. Too close to the edge of flipping to
  serve as a stable "credible evidence of human advantage" claim without
  re-running a fresh measurement, which is out of scope for this build.
- **Source:** [Evaluating LLMs on Real-World Forecasting Against Human Superforecasters](https://arxiv.org/html/2507.04562v3); [ForecastBench parity update](https://forecastingresearch.substack.com/p/ai-models-have-likely-reached-parity).

## What survived: FANToM only

Of every category considered (the two originally built, plus six additional
2025–2026 candidates researched fresh this session), **FANToM (Category A)
is the only one that clears the bar**: real published multi-model human
baseline collected under matched conditions, not a leaderboard/prize target,
accessible real data, and — per its own repo's tracking — the gap had not
closed between 2023 GPT-4 and 2024 GPT-4o (though, per that same honesty
standard, its 2026-era currency is unverified since no model evaluation was
run in this project).
