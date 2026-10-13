# ConsciousMind — Project Status (read this first)

If you are a fresh Claude Code session picking this up: read this file, then
`RESEARCH_NOTES.md` for the full reasoning trail. Don't re-derive decisions
that are already made and justified below — extend them.

## One-line status (updated 2026-09-23 — scope reset)

**The deliverable was reset on 2026-09-23** from a broader
"consciousness/metacognition framework" framing to its actual, narrower
target: a dataset of categories where there is *credible, verified*
evidence of a human advantage over AI/LLMs. This is a stricter bar than the
earlier build met. Under it: **Category A (FANToM) kept as-is (150 items,
strong evidence). Category B was rebuilt** — the original "response
quality" framing (CounselBench-Eval ratings) was found to *not* show a
human advantage (GPT-4 rated higher on Overall/Toxicity) and was retired in
favor of a narrower, evidenced construct found in the same data: GPT-4-0613
declined to substantively engage (canned refusal) on 34/100 real
mental-health questions the human therapist answered directly on all 100
(0% human refusal) — corrected from an earlier miscounted 18%. **Six
additional 2025–2026 "humans beat AI" benchmarks were researched fresh
against primary sources and rejected** (all had closed, inverted, or lacked
a real human baseline) — see `dataset/REJECTED_CANDIDATES.md`.

**Final core dataset: 250 items across 2 categories.** See `dataset/README.md`.

## Immediate next step

None blocking. Both core categories are built, verified, and documented.
The staged LLM pilot (testing current models against this data) is the
natural next milestone but is explicitly out of scope for this deliverable.

## What's in this folder

```
consciousmind_project/
├── PROJECT_STATUS.md              <- you are here
├── RESEARCH_NOTES.md              <- full research trail, including the 2026-09-23 reset
├── HANDOFF.md                     <- full work log, current as of 2026-09-23
├── dataset/
│   ├── README.md                  <- START HERE for the dataset itself
│   ├── AUDIT.md                   <- field-level audit, dedup/consistency checks
│   ├── REJECTED_CANDIDATES.md     <- 6 candidates researched and rejected, with sources
│   ├── category_a_theory_of_mind/         <- Category A (unchanged, kept)
│   ├── category_b_deflection_under_severity/  <- Category B, FINAL (new 2026-09-23)
│   └── category_b_safety_judgment/        <- Category B, SUPERSEDED (kept, not deleted — see NOTE.md)
└── reference/                      <- cloned source repos (fantom, CounselBench), code only
```

## Known open items (not blockers, just unresolved)

1. **Licenses:** CounselBench-Eval is CC-BY-NC-ND-4.0; FANToM's dataset
   carries an "evaluation purposes only" author note. Both fine for
   internal research; both need author clearance before any public release.
2. **Metacognitive Calibration** remains undocumented-as-built — it would
   require new human recruitment, explicitly out of scope for this
   deliverable (see `RESEARCH_NOTES.md`).
3. **No LLM API calls have been made against either category.** Everything
   built is reference/ground-truth data only. Category B's 34%-refusal
   finding is evidence about one 2023 model (GPT-4-0613), not a claim about
   current models — testing whether it recurs is the natural next
   milestone, not yet run.
4. **Category A's currency for 2026-era models is unverified** — the
   published gap held between 2023 GPT-4 and 2024 GPT-4o, but no model
   evaluation has been run since, in this project.
