#!/usr/bin/env python3
"""Run the deterministic classifier over a directory of BVA decision text files.
Usage: python census.py <folder-of-.txt-decisions>
Prints the same rates encoded in data/bva_decision_labels_2021_2025.csv.
The Board publishes every decision; fetch 2021-2025 decisions as .txt into <folder> to re-run from source.
"""
import os, sys, glob, math
import bva_det_parser as P

def wilson(k, n, z=1.96):
    ph = k / n; d = 1 + z*z/n
    c = (ph + z*z/(2*n)) / d
    h = (z*math.sqrt(ph*(1-ph)/n + z*z/(4*n*n))) / d
    return (100*(c-h), 100*(c+h))

def main():
    if len(sys.argv) < 2:
        print("usage: python census.py <folder-of-.txt-decisions>"); sys.exit(1)
    files = glob.glob(os.path.join(sys.argv[1], "**", "*.txt"), recursive=True)
    parsed = 0; merits = 0; affirmed = 0
    for p in files:
        try:
            t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        r = P.classify_decision(t)
        if not r["parsed"]:
            continue
        parsed += 1
        if r["has_merits_grant"]: merits += 1
        if r["fully_affirmed"]: affirmed += 1
    if not parsed:
        print("no parseable decisions found in", sys.argv[1]); return
    lo, hi = wilson(merits, parsed)
    print(f"files: {len(files)} | parsed disposition: {parsed}")
    print(f"decisions with >=1 merits grant: {merits}/{parsed} = {100*merits/parsed:.1f}%  (95% CI {lo:.1f}-{hi:.1f})")
    print(f"fully affirmed: {affirmed}/{parsed} = {100*affirmed/parsed:.1f}%")

if __name__ == "__main__":
    main()
