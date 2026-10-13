# Build Log

## Environment constraints discovered

This build ran in a sandboxed cloud environment whose outbound network policy
(an egress proxy) blocks several hosts needed by the original data-access plan:

- `storage.googleapis.com` (FANToM's data host) — blocked, confirmed via
  direct `curl` (403 on CONNECT) and via `WebFetch` (fetch succeeded at the
  transport level but returned binary tar.gz content with no way to save raw
  bytes to disk from that tool).
- `huggingface.co` and `datasets-server.huggingface.co` — blocked for direct
  `curl`/Python `huggingface_hub` access from the Bash tool (403 on CONNECT),
  but **reachable through `WebFetch`**, which routes through a different
  backend. This is what made Category B possible in this session.
- `github.com` and `raw.githubusercontent.com` — reachable from both Bash and
  WebFetch throughout.

## Category A (FANToM) — access attempts, resolved 2026-09-22

In the original cloud sandbox, all direct access attempts failed:

1. Direct download of `https://storage.googleapis.com/ai2-mosaic-public/projects/fantom/fantom.tar.gz` — blocked (Bash), binary/unusable (WebFetch).
2. `https://hyunw.kim/fantom` (project page, custom domain) — blocked (403 at proxy).
3. Guessed GitHub raw-content mirror paths (`skywalker023/fantom/main/data/fantom.json`, `skywalker023/fantom_data/main/full_dataset.json`) — 404, no such files exist.
4. Hugging Face dataset search for a third-party mirror (`huggingface.co/api/datasets?search=fantom`) — found one candidate, `clembench-playpen/fantom`, but its data is gated (401 Unauthorized on the datasets-server API — requires an HF auth token this session does not have).
5. Broader HF search (`theory of mind stress-testing`) — no relevant results.

**Resolved on the local machine:** run from `/Users/faizan/RootVault/ conscious-mind`
(normal network access, not the cloud sandbox), a direct `curl` of the same
`storage.googleapis.com` URL succeeded immediately (HTTP 200, 1,040,898
bytes), and its SHA-256 (`1d08dfa0ea474c7f83b9bc7e3a7b466eab25194043489dd618b4c5223e1253a4`)
matched the hash hardcoded in `reference/fantom/task/dataset_loader.py`
exactly, confirming an unmodified, authentic copy of the authors' release.
Extracted to `category_a_theory_of_mind/raw_fantom/fantom_v1.json` (870
conversation sets). `category_a_theory_of_mind/build_dataset.py` then built
150 items (50 per question type) from it — see `SOURCE.md` in that folder
for the full construction method. This confirms the earlier "blocked" status
was specific to that sandbox's egress policy, not to FANToM's data being
generally unreachable.

## Category B (CounselBench-Eval) — how it was actually fetched

`huggingface.co`'s own hub API and `datasets-server.huggingface.co`'s REST API
are both reachable via `WebFetch`, which returns the actual JSON content when
explicitly instructed to output raw/verbatim data rather than a prose summary.

Endpoint used:
```
GET https://datasets-server.huggingface.co/rows?dataset=izi-ano/CounselBench-Eval&config=default&split=test&offset={N}&length={M}
```

Important discovered facts about this endpoint and this fetch method:
- The dataset's split is named `test`, not `train` (a first attempt at
  `split=train` returned a 500 error; `GET /splits?dataset=...` revealed the
  correct split name).
- The dataset has exactly **2000 rows** (`num_rows_total: 2000`), consistent
  with the paper's stated "100 questions × 4 responders × 5 raters."
- Rows are laid out in fixed, deterministic blocks: **every 20 consecutive
  rows = one question**, in the fixed order `gpt4, llama3, gemini, human`
  (5 rater rows each). This was confirmed directly from returned data and
  used to fetch one full question per `offset` step of 20.
- **`WebFetch` truncates large responses.** Requesting `length=100` rows
  reliably returned only ~50 rows' worth of content, silently, despite
  explicit instructions not to truncate — confirmed by three separate probes
  before switching strategy. Requesting `length=20` (one full question block)
  was reliably complete in every successful call — verified by checking that
  exactly 5 gpt4 rows + 5 human rows came back each time.
- **Given this, every question in `items.json` was fetched at `length=20`,
  one WebFetch call per question**, requesting only `human` and `gpt4` rows
  (i.e., excluding `llama3`/`gemini` from the request to keep each response
  small and further reduce truncation risk) and excluding the free-text
  `*_reason`/`*_copy` fields (kept for future work, not needed for the
  aggregate-score task built here).
- 40 question-block offsets were targeted (0, 20, 40, ..., 780 — the first 40
  of the dataset's 100 questions, in release order). **38 of 40 succeeded.**
  Offsets 660 and 680 returned HTTP 429 (rate-limited) on three attempts each
  and were not retried further, to avoid hammering a third-party API. The
  dataset therefore has 38 questions, not 40 — documented here rather than
  padded to a round number.
- Fidelity check performed: for every successful fetch, the response was
  verified to contain exactly 5 `gpt4` score-rows and 5 `human` score-rows
  with a consistent `survey_id` set per question (matching the block-of-20
  structure), before being transcribed into `build_dataset.py`. No row was
  edited, reworded, or numerically adjusted after extraction.

## Reproducibility (original 38-question build)

`build_dataset.py` (top level) contains the 38 fetched records as literal
data and deterministically produces `raw_ratings.csv`, `items.json`, and
`items_aggregated.csv`. Re-running it reproduces the exact same output
files. Kept as-is for historical/audit purposes; superseded by the full
build below.

## Category B extension to the full 100 questions — 2026-09-22

Run from a machine with normal network access (not the cloud sandbox), a
direct `curl` of `datasets-server.huggingface.co`'s REST API succeeded
immediately, with none of the truncation or rate-limiting quirks that
constrained the original `WebFetch`-based build:

- The API's `length` parameter has a hard cap of 100 rows per request
  (confirmed: `length=500` returns `{"error":"Parameter 'length' must not
  be greater than 100"}`). All 2000 rows were fetched in 20 calls of
  `length=100` at `offset=0,100,200,...,1900` — every call returned exactly
  100 rows, no truncation, no rate-limiting, on the first attempt.
- The raw, unmodified rows from all 20 calls were consolidated and saved
  verbatim to `category_b_safety_judgment/raw_hf_fetch/all_2000_rows.json`
  (2000 rows, 100 unique `questionID`s x 4 responders x 5 raters — confirmed
  by direct count).
- `dataset/build_dataset_full.py` reads that file (no hardcoded records,
  no re-fetching) and rebuilds `raw_ratings.csv` / `items.json` /
  `items_aggregated.csv` for all 100 questions x 2 responders (`human`,
  `gpt4`) = 200 items, 1000 raw rating rows — fully deterministic, same
  filtering logic (human + gpt4 only) as the original 38-question build.
- Sanity check: the full-100 pull reproduces the same pattern found in the
  original 38-question sample — mean Overall 2.60 (human) vs 3.28 (gpt4),
  mean Toxicity 2.56 (human) vs 1.78 (gpt4, lower=better), and GPT-4 canned
  refusals on 18/100 questions (18.0%, versus 18.4% in the smaller sample) —
  confirming the earlier finding was not an artifact of the smaller pull.

## Reproducibility (full 100-question build)

Run `python3 dataset/build_dataset_full.py` from the `dataset/` directory
(or its parent). It reads `category_b_safety_judgment/raw_hf_fetch/all_2000_rows.json`
and regenerates `raw_ratings.csv`, `items.json`, and `items_aggregated.csv`
deterministically — no network access required, no hardcoded records. To
add `llama3`/`gemini` responders later, extend the responder loop in
`build_dataset_full.py`; their raw rows already exist in the saved fetch.
