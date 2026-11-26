#!/usr/bin/env python3
"""Stage 1: run each adapter and checkpoint its normalized output to work/staged/<name>.jsonl.

Resumable: an adapter whose staged file + .done marker exist is skipped (use --force to redo).
Failures (malformed rows) are logged to logs/stage_failures.jsonl, skips are counted.
"""
import argparse, json, sys, time
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import adapters

HERE = Path(__file__).resolve().parents[1]
STAGED = HERE / "work" / "staged"
LOGS = HERE / "logs"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    cfg = json.load(open(HERE / "config.json"))
    STAGED.mkdir(parents=True, exist_ok=True); LOGS.mkdir(exist_ok=True)
    summary = {}
    for name, fn in adapters.ADAPTERS.items():
        if a.only and name not in a.only:
            continue
        out, done = STAGED / f"{name}.jsonl", STAGED / f"{name}.done"
        if done.exists() and not a.force:
            summary[name] = json.load(open(done)); print(f"[skip] {name} {summary[name]}"); continue
        t0 = time.time(); n = 0; errs = 0; skips = Counter()
        with open(out, "w", encoding="utf-8") as f, open(LOGS / "stage_failures.jsonl", "a", encoding="utf-8") as ef:
            for r in fn(cfg):
                if "_error" in r:
                    errs += 1; ef.write(json.dumps({"adapter": name, "error": r["_error"]}) + "\n"); continue
                if "_skip" in r:
                    skips[r["_skip"]] += 1; continue
                f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
        info = {"emitted": n, "errors": errs, "skipped": dict(skips), "seconds": round(time.time() - t0, 1)}
        json.dump(info, open(done, "w")); summary[name] = info; print(f"[done] {name} {info}")
    json.dump(summary, open(HERE / "work" / "stage_summary.json", "w"), indent=2)

if __name__ == "__main__":
    main()
