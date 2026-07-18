#!/usr/bin/env python3
"""Split the filtered CVUT subject CSV into deterministic fork-input batches.

Partition is stable: batch N always holds the same rows (input order), so a
re-run is safe and resumable — a batch is "pending" iff its output JSONL is
missing or has fewer lines than its input. Prints the pending batch numbers so
the orchestrator knows exactly which forks to (re)spawn.
"""
import argparse
import csv
import json
import os

FORK_FIELDS = ["code", "name", "department", "detail_url", "guarantor", "guarantor_profile"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="filtered subjects CSV (rows with a person)")
    ap.add_argument("--batch-dir", required=True, help="dir to write batch_NN.json fork inputs")
    ap.add_argument("--out-dir", required=True, help="dir where forks write batch_NN.jsonl outputs")
    ap.add_argument("--size", type=int, default=10, help="subjects per batch (default 10)")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    batches = [rows[i:i + args.size] for i in range(0, len(rows), args.size)]
    os.makedirs(args.batch_dir, exist_ok=True)

    pending = []
    for n, batch in enumerate(batches):
        slim = [{k: r[k] for k in FORK_FIELDS} for r in batch]
        with open(os.path.join(args.batch_dir, f"batch_{n:02d}.json"), "w", encoding="utf-8") as f:
            json.dump(slim, f, ensure_ascii=False, indent=1)
        out = os.path.join(args.out_dir, f"batch_{n:02d}.jsonl")
        done = sum(1 for _ in open(out, encoding="utf-8")) if os.path.exists(out) else 0
        if done < len(batch):
            pending.append(n)

    print(f"{len(rows)} subjects -> {len(batches)} batches of {args.size} in {args.batch_dir}")
    print(f"pending: {' '.join(f'{n:02d}' for n in pending) if pending else '(none — all complete)'}")


if __name__ == "__main__":
    main()
