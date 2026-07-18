#!/usr/bin/env python3
"""Merge fork outputs (out/batch_NN.jsonl) into the final Phase-2 deliverables.

Dedups by subject code, then writes two CSVs beside the out-dir:
  all_scored.csv        — every scored subject with its verdict
  relevant_subjects.csv — only verdict in {relevant, borderline}, the outreach shortlist

Reports per-verdict counts and flags any batch whose input has no output yet.
"""
import argparse
import csv
import glob
import json
import os
import re

OUT_FIELDS = ["code", "name", "department", "guarantor", "guarantor_profile",
              "detail_url", "verdict", "reason", "description"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", required=True, help="dir holding batch_NN.jsonl fork outputs")
    ap.add_argument("--batch-dir", required=True, help="dir holding batch_NN.json fork inputs (for coverage check)")
    ap.add_argument("--dest", required=True, help="dir to write all_scored.csv and relevant_subjects.csv")
    args = ap.parse_args()

    seen = {}
    for path in sorted(glob.glob(os.path.join(args.out_dir, "batch_*.jsonl"))):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            seen.setdefault(o["code"], o)

    scored = sorted(seen.values(), key=lambda o: o["code"])

    def write(name, objs):
        with open(os.path.join(args.dest, name), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=OUT_FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(objs)

    write("all_scored.csv", scored)
    shortlist = [o for o in scored if o.get("verdict") in ("relevant", "borderline")]
    write("relevant_subjects.csv", shortlist)

    counts = {}
    for o in scored:
        counts[o.get("verdict", "?")] = counts.get(o.get("verdict", "?"), 0) + 1

    missing = []
    for bp in sorted(glob.glob(os.path.join(args.batch_dir, "batch_*.json"))):
        n = re.search(r"batch_(\d+)\.json$", bp).group(1)
        if not os.path.exists(os.path.join(args.out_dir, f"batch_{n}.jsonl")):
            missing.append(n)

    print(f"scored {len(scored)} unique subjects: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"shortlist (relevant+borderline): {len(shortlist)} -> relevant_subjects.csv")
    if missing:
        print(f"WARNING missing outputs for batches: {' '.join(missing)}")


if __name__ == "__main__":
    main()
