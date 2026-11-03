# Handoff - Morals & Ethics dataset session (2026-10-13 to 2026-11-03)

Branch: `claude/serene-goodall-048eve` (not merged to the default branch; no PR opened).
Read `dataset/morals_ethics/README.md` (schema, method, limitations) and `PRESENTATION_GUIDE.md` (how to explain it) first.

## Goal
Build one clean research CSV of ~25,000 unique moral/ethical scenarios for ConsciousMind, from published datasets first, synthetic only for real gaps,
preserving the earlier workbook (`data/CM_Ethics_Dataset_1.xlsx`, untouched).

## What was done
1. **Audit:** only `data/CM_Ethics_Dataset_1.xlsx` (416 items: 400 ETHICS + 16 PhilPapers; 1,248 Claude opus/sonnet/haiku responses) was morals/ethics. The rest of the repo is theory-of-mind/counseling work.
2. **Sources fetched** (`scripts/fetch_sources.py`; GitHub + storage.googleapis.com only, since Hugging Face/Zenodo/arXiv/ollama.com are blocked in the cloud sandbox): ETHICS (via GitHub mirror `psalm-alignment`), Scruples anecdotes + dilemmas, Social Chemistry 101, DailyDilemmas, MoralChoice, MoralExceptQA, BIG-bench `simple_ethical_questions`. Commits/hashes pinned in `work/fetch_manifest.json`.
3. **Adapters** (`scripts/adapters.py`) convert each source to one schema, keep original labels (`label_raw`) and log transforms (`label_transform`); `stage_sources.py` checkpoints to `work/staged/`.
4. **Synthetic gap-fill** (`scripts/synthetic.py`, `synthetic_spec.json`, `synthetic_prompt.md`): 12 applied-ethics domains x 5 sub-topics x 25 = 1,500 requested, 1,498 accepted. Written by 12 Claude subagents (no API key was available). Unlabeled, flagged `is_synthetic`. Raw cells in `work/synthetic/raw/`.
5. **Build** (`scripts/build_dataset.py`): validate, exact-dedup (prior workbook wins), drop label-conflicting duplicates (601), MinHash near-dup clustering (max 2/cluster), one Social Chemistry item per situation, label-balanced stratified selection, cluster-aware train/dev/test (70/10/20).
6. **Verify** (`scripts/validate_and_report.py`): 25,000 rows, 0 exact duplicates, 0 invalid labels, 0 cross-split near-duplicate pairs; rebuild is byte-identical. Prior-workbook ETHICS items cross-checked against the mirror (400/400 match).
7. **Decisions along the way:** BIG-bench `moral_permissibility` excluded (mismatched vignette/question, templating); Social Chemistry restricted to actions a character actually performs; the user briefly asked for published-only data, then clarified that synthetic items are fine as long as sourced data is from published datasets, so the synthetic set is included (`include_synthetic=true` in `config.json`).
8. **Docs:** README, DATA_QUALITY_REPORT, source manifest, `papers/PAPERS.md` (+ `fetch_papers.sh`; arXiv IDs unverified), PRESENTATION_GUIDE.

## Final dataset (`dataset/morals_ethics/output/`)
- `morals_ethics_25k.csv` - 25,000 rows x 36 columns (23,502 from published datasets + 1,498 synthetic)
- `morals_ethics_25k_prior_model_responses.csv` - the 1,248 earlier Claude responses, keyed by `item_id`
- `source_manifest.csv|json` - sources, licenses, citations, counts
Labels: 20,666 human-derived, 802 author-designated, 3,532 unlabeled.

## What is NOT in git (re-create locally)
- `data/raw_sources/` (~4 GB, gitignored): `python3 dataset/morals_ethics/scripts/fetch_sources.py`
- `dataset/morals_ethics/work/staged/` (~500 MB, gitignored): `python3 dataset/morals_ethics/scripts/stage_sources.py`
- Neither is needed just to use the CSV. Full rebuild: `pip install -r dataset/morals_ethics/requirements.txt && bash dataset/morals_ethics/scripts/run_all.sh`
  (on a machine with normal internet the extra sources in the README's "reviewed and excluded" list can also be tried).

## Open items / next steps
1. **Local-model evaluation (discussed, not built):** write `scripts/eval_ollama.py` - fixed prompt per `response_format`, temperature 0 + seed, resumable JSONL output, scoring on labeled rows only (accuracy by source/domain/`label_agreement`, ETHICS `test_hard` vs `test`, A/B position bias); refusal/hedge rates for the unlabeled dilemmas; start with a ~2,000-row stratified sample. Candidate models: Llama 3.1 8B, Qwen 2.5 7B/14B, Gemma 2 9B, Mistral 7B. Can be compared with the Claude answers already in the prior-workbook responses (416 items). The cloud sandbox cannot run Ollama (blocked, no GPU); run locally.
2. **Licenses:** Scruples, Social Chemistry 101, MoralExceptQA state no data license in the retrieved files - verify before any public release.
3. **Verify arXiv IDs** in `papers/PAPERS.md`; download PDFs with `papers/fetch_papers.sh`.
4. **Possible extensions** (hosts blocked here): Moral Stories, MIC, Delphi/Commonsense Norm Bank, ValuePrism, MFRC.
5. **Synthetic set** has had only automated checks + a small manual read; consider human review before relying on it.
6. A human-vs-AI claim still needs a matched human baseline; the CSV is an item pool, not evidence of human advantage.

## Caveats to remember
- Labels are crowd/author conventions, not moral truth; Social Chemistry was sampled label-balanced (not natural rates).
- Almost all published items are well-known benchmarks (contamination risk). I did not read the original papers (hosts blocked); source-method descriptions come from READMEs/repo code and the prior workbook.
- DailyDilemmas being GPT-4-generated is my understanding from the repo, not read in the paper.
