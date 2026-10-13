# Category A: Interactive Theory of Mind — RESOLVED (was blocked)

## Status update (2026-09-22)

**No longer blocked.** Run from a machine with normal (non-sandboxed)
network access, `fantom.tar.gz` downloaded directly from
`storage.googleapis.com` on the first attempt (HTTP 200, 1,040,898 bytes),
and its SHA-256 matched the hash hardcoded in the authors' own
`task/dataset_loader.py` exactly. The blockers below were specific to the
earlier cloud sandbox's egress policy, not to FANToM's data being
unreachable in general. See `SOURCE.md` for the built dataset's provenance
and `build_dataset.py` for the construction code. The rest of this file is
kept as the historical record of what was tried before that.

## Original status (superseded)

**No items were built for this category.** The source data (FANToM) could
not be retrieved from this build environment despite multiple access
attempts. Fabricating conversations to populate this category was
deliberately avoided — a dataset item claiming to be "FANToM" that was not
actually sourced from FANToM would corrupt the entire premise of reusing an
externally-validated, human-baselined benchmark, which was the whole reason
this source was selected in the first place.

## Why FANToM specifically, and why it survived the stress-test

FANToM (Kim et al., EMNLP 2023) is the one theory-of-mind source, of several
evaluated earlier in this project, with a genuine published human baseline
collected under matched conditions (11 CS graduate volunteers, same
short-context condition, same instructions as the LLMs tested) — not an
assumption of human advantage, an actually measured one. See this project's
earlier audit turns for the full comparison against Hi-ToM and ExploreToM
(both rejected for lacking any human baseline).

## Exactly what is needed to unblock this

One of:

1. **The extracted contents of `fantom.tar.gz`**
   (`https://storage.googleapis.com/ai2-mosaic-public/projects/fantom/fantom.tar.gz`,
   ~a few MB), downloaded from an environment that can reach
   `storage.googleapis.com`, then provided to a build environment that can
   read it (uploaded as a file, or the extracted JSON pasted/attached
   directly).
2. Alternatively, running `skywalker023/fantom`'s own
   `task/dataset_loader.py` (already cloned and inspected in this project —
   see prior turns) in an environment with open network access, then
   exporting the loaded dataframe to JSON/CSV for transfer.

Once either is available, the exact construction method is already fully
specified — see `SCHEMA.md` in this folder — and does not require repeating
any of the design or audit work already done.

## What was actually tried in this session (see `../build_log.md` for full detail)

1. Direct download from `storage.googleapis.com` — blocked by sandbox
   egress policy (Bash: 403 on CONNECT; WebFetch: reached the host but
   returned unusable binary content with no way to save raw bytes).
2. The project's own webpage (`hyunw.kim/fantom`, a custom domain) — blocked.
3. Guessed GitHub raw-content mirror paths — none exist (404).
4. A Hugging Face dataset search for a third-party mirror — found one
   candidate (`clembench-playpen/fantom`) but it is access-gated (401,
   requires an auth token not available in this session).

This is a definitive "not reachable from here," not a "didn't look hard
enough" — four independent routes were tried and each failed for a
different, verifiable reason.
