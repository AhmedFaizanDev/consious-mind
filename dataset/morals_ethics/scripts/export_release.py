#!/usr/bin/env python3
"""Split output/morals_ethics_25k.csv into a published-only file and a synthetic-only file.

Rows are copied unchanged (same columns, same order); the 25k file is not modified.
    python3 scripts/export_release.py
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "output"
SRC = OUT / "morals_ethics_25k.csv"

with open(SRC, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    fields, rows = r.fieldnames, list(r)

parts = {
    "morals_ethics_published.csv": [x for x in rows if x["is_synthetic"] != "True"],
    "morals_ethics_synthetic.csv": [x for x in rows if x["is_synthetic"] == "True"],
}
assert sum(len(v) for v in parts.values()) == len(rows)
for name, part in parts.items():
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(part)
    print(f"{name}: {len(part)} rows")
