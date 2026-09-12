#!/usr/bin/env python3
"""Recompute the headline numbers directly from the published labels CSV. No corpus needed.
Usage: python reproduce_from_labels.py
"""
import csv, os, math

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "bva_decision_labels_2021_2025.csv")

def wilson(k, n, z=1.96):
    ph = k / n; d = 1 + z*z/n
    c = (ph + z*z/(2*n)) / d
    h = (z*math.sqrt(ph*(1-ph)/n + z*z/(4*n*n))) / d
    return (100*(c-h), 100*(c+h))

parsed = 0; merits = 0; affirmed = 0; total = 0
by_year = {}
with open(CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        total += 1
        lbl = row["decision_label"]
        if lbl == "no_disposition_parsed":
            continue
        parsed += 1
        y = by_year.setdefault(row["year"], [0, 0])
        y[0] += 1
        if lbl == "merits_grant":
            merits += 1; y[1] += 1
        elif lbl == "fully_affirmed":
            affirmed += 1

lo, hi = wilson(merits, parsed)
print(f"rows: {total} | parsed disposition: {parsed}")
print(f"decisions with >=1 merits grant: {merits}/{parsed} = {100*merits/parsed:.1f}%  (95% CI {lo:.1f}-{hi:.1f})")
print(f"fully affirmed (all issues denied): {affirmed}/{parsed} = {100*affirmed/parsed:.1f}%")
print("by year (merits-grant rate):")
for y in sorted(by_year):
    n, g = by_year[y]
    print(f"  {y}: {100*g/n:.1f}%  (n={n})")
