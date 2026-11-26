#!/usr/bin/env python3
"""Fetch the public source datasets for the Morals & Ethics build.

Idempotent: anything already present under data/raw_sources/ is skipped (never
overwritten). Records the git commit of each cloned repo and the SHA-256 of each
downloaded archive in dataset/morals_ethics/work/fetch_manifest.json so the
exact inputs are pinned.

Hugging Face, Zenodo and arXiv are not reachable from the build sandbox
(egress policy), so only GitHub and storage.googleapis.com sources are used.
"""
import hashlib
import json
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw_sources"
MANIFEST = ROOT / "dataset" / "morals_ethics" / "work" / "fetch_manifest.json"

GIT_REPOS = {
    # dir name: (url, sparse_paths or None)
    "psalm-alignment": ("https://github.com/christian-machine-intelligence/psalm-alignment.git", None),  # ETHICS data mirror
    "daily_dilemmas": ("https://github.com/kellycyy/daily_dilemmas.git", None),
    "moralchoice": ("https://github.com/ninodimontalcino/moralchoice.git", None),
    "MoralCoT": ("https://github.com/feradauto/MoralCoT.git", None),  # MoralExceptQA lives here
    "BIG-bench": ("https://github.com/google/BIG-bench.git", ["bigbench/benchmark_tasks"]),
    "ethics": ("https://github.com/hendrycks/ethics.git", None),  # code/README/license only
    "scruples": ("https://github.com/allenai/scruples.git", None),  # code/license only
}

ARCHIVES = {
    # dir name: (url, kind)
    "scruples_anecdotes": ("https://storage.googleapis.com/ai2-mosaic-public/projects/scruples/v1.0/data/anecdotes.tar.gz", "tar"),
    "scruples_dilemmas": ("https://storage.googleapis.com/ai2-mosaic-public/projects/scruples/v1.0/data/dilemmas.tar.gz", "tar"),
    "social_chem_101": ("https://storage.googleapis.com/ai2-mosaic-public/projects/social-chemistry/data/social-chem-101.zip", "zip"),
}


def run(cmd, cwd=None, retries=4):
    for i in range(retries):
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip()
        wait = 2 ** (i + 1)
        print(f"  retry {i + 1}/{retries} in {wait}s: {r.stderr.strip()[:200]}", file=sys.stderr)
        time.sleep(wait)
    raise RuntimeError(f"command failed: {' '.join(cmd)}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"repos": {}, "archives": {}}

    for name, (url, sparse) in GIT_REPOS.items():
        dest = RAW / name
        if not dest.exists():
            print(f"cloning {url}")
            if sparse:
                run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", "-q", url, str(dest)])
                run(["git", "sparse-checkout", "set", *sparse], cwd=dest)
            else:
                run(["git", "clone", "--depth", "1", "-q", url, str(dest)])
        else:
            print(f"present: {name}")
        manifest["repos"][name] = {"url": url, "commit": run(["git", "rev-parse", "HEAD"], cwd=dest)}

    dl = RAW / "_dl"
    dl.mkdir(exist_ok=True)
    for name, (url, kind) in ARCHIVES.items():
        dest = RAW / name
        if dest.exists() and any(dest.iterdir()):
            print(f"present: {name}")
            fn0 = dl / url.rsplit("/", 1)[1]
            if fn0.exists():
                manifest["archives"][name] = {"url": url, "sha256": sha256(fn0), "bytes": fn0.stat().st_size}
            elif name not in manifest["archives"]:
                manifest["archives"][name] = {"url": url, "sha256": None, "note": "extracted dir existed; archive not kept"}
            continue
        fn = dl / url.rsplit("/", 1)[1]
        if not fn.exists():
            print(f"downloading {url}")
            for i in range(4):
                try:
                    urllib.request.urlretrieve(url, fn)
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  retry {i + 1}: {e}", file=sys.stderr)
                    time.sleep(2 ** (i + 1))
            else:
                raise RuntimeError(f"download failed: {url}")
        dest.mkdir(parents=True)
        if kind == "tar":
            with tarfile.open(fn) as t:
                t.extractall(dest, filter="data")
        else:
            with zipfile.ZipFile(fn) as z:
                z.extractall(dest)
        manifest["archives"][name] = {"url": url, "sha256": sha256(fn), "bytes": fn.stat().st_size}

    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print("fetch manifest written:", MANIFEST)


if __name__ == "__main__":
    main()
