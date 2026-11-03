#!/usr/bin/env bash
# Full local evaluation: start Ollama (GPU, 8 parallel slots), then for each model:
# pull -> 50-item smoke test -> full sample run -> score -> commit + push results.
# Safe to re-run: pulls and runs both resume.
#   nohup bash dataset/morals_ethics/scripts/run_ollama_eval.sh > dataset/morals_ethics/eval/run.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/../../.."
EVAL=dataset/morals_ethics/scripts/eval_ollama.py
MODELS=(llama3.1:8b qwen2.5:7b gemma2:9b)
WORKERS=${WORKERS:-8}

if ! curl -s localhost:11434/api/version >/dev/null; then
  OLLAMA_NUM_PARALLEL=$WORKERS OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 \
    nohup ollama serve > dataset/morals_ethics/eval/ollama_server.log 2>&1 &
  sleep 5
fi

save() {
  git add dataset/morals_ethics/eval
  git commit -q -m "Ollama eval results: $1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q || echo "!!! push failed for $1 (results are committed locally)"
}

for m in "${MODELS[@]}"; do
  echo "=== $(date '+%H:%M') pulling $m"
  until ollama pull "$m"; do echo "pull failed, retrying in 30s"; sleep 30; done

  echo "=== $(date '+%H:%M') smoke test $m"
  python3 "$EVAL" run --model "$m" --limit 50 --workers $WORKERS
  python3 - "$m" <<'EOF'
import json, re, sys
f = "dataset/morals_ethics/eval/responses/" + re.sub(r"[^A-Za-z0-9._-]+", "_", sys.argv[1]) + ".jsonl"
rs = [json.loads(l) for l in open(f)]
bad = sum(r["parsed"] is None for r in rs)
print(f"smoke: {len(rs)} answered, {bad} unparsed")
sys.exit(1 if len(rs) < 45 or bad > len(rs) * 0.3 else 0)
EOF
  if [ $? -ne 0 ]; then echo "!!! smoke test failed for $m, skipping full run"; continue; fi

  echo "=== $(date '+%H:%M') full run $m"
  python3 "$EVAL" run --model "$m" --workers $WORKERS
  python3 "$EVAL" score
  save "$m"
done
echo "=== $(date '+%H:%M') ALL DONE"
