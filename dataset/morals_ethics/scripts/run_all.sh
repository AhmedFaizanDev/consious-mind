#!/usr/bin/env bash
# Rebuild morals_ethics_25k.csv end to end. Every stage is resumable / idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/fetch_sources.py                 # skips anything already downloaded (never overwrites raw files)
python3 scripts/stage_sources.py                 # per-source checkpoints in work/staged (use --force to redo)
python3 scripts/synthetic.py prompts             # (re)write per-cell prompts
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  python3 scripts/synthetic.py generate          # only fills cells missing from work/synthetic/raw
fi
python3 scripts/synthetic.py ingest              # validate whatever raw synthetic cells exist
python3 scripts/build_dataset.py                 # validate, dedup, cluster, select, split, write CSV + manifest
python3 scripts/validate_and_report.py           # independent re-check + DATA_QUALITY_REPORT.md
