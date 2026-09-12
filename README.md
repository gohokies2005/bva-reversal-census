# How often does the Board of Veterans' Appeals overturn the regional office?

This repository is the methodology and data behind one figure: **across all Board of Veterans' Appeals (BVA) decisions issued from 2021 through 2025, the Board granted a veteran at least one previously denied benefit in about one in three appealed cases (33.3 percent).** It accompanies a Health Affairs Forefront essay by Ryan Kasky, DO.

The figure is produced by a **deterministic, rule-based program** — not a machine-learning model and not human judgment. The same decisions always yield the same number, and anyone can re-run the rule or recompute the result from the published data.

**Conflict-of-interest disclosure:** The author operates a service that prepares independent medical opinions for veterans appealing VA denials, and therefore has a financial interest in the conclusion that VA adjudication is often wrong. Every number here is derived from the Board's own public decisions and is reproducible from the code and data in this repository; none depends on the author's case files.

---

## The number, precisely

- Unit of analysis: a **Board decision** (one case). A case can contain several separate issues.
- Denominator: decisions with a readable disposition — **290,661** of the 295,756 issued 2021–2025 (about 1.7 percent could not be parsed).
- Numerator: decisions containing **at least one merits grant** — a substantive benefit awarded (service connection, a rating, TDIU, an effective date).
- Result: **96,935 / 290,661 = 33.3 percent** (95 percent confidence interval 33.2–33.5).

What it is **not**: not one in three of all veterans (only those who appealed to the Board), not one in three claims (the unit is a case, and "at least one" issue), and **not a finding that the VA was "wrong" one in three times** — a grant can reflect new evidence, a change in law, benefit of the doubt, or the Board reweighing the record. A merits grant is a disposition fact, not a judgment about why.

## The rule (how a decision is classified)

For each decision the program reads the **ORDER section** (the Board's dispositive section; for pure-remand decisions that omit the header, the disposition block) and classifies every issue by the Board's own closing verb:

```
"... is granted"                -> a GRANT
"... is denied"                 -> denied
"... is remanded"               -> remanded (sent back, not decided)
"... is dismissed / withdrawn"  -> dismissed
```

A grant is split in two:

- **Merits grant** — a benefit awarded. Counts as the regional office being overturned.
- **Procedural reopening** — only a "petition/application to reopen ... is granted," where the underlying issue is typically remanded. **Does not count.** Excluding these is the core of the method; counting them inflates the rate.

A decision is labeled `merits_grant` if it grants at least one issue on the merits, and `fully_affirmed` if every issue was denied. The rule is fixed (`re` / regular expressions only — see `bva_det_parser.py`), so it involves no model and no subjective judgment.

## Files

- `bva_det_parser.py` — the classifier. Its only import is Python's `re` module. No AI, no network.
- `census.py` — runs the classifier over a directory of decision text files and prints the rates.
- `reproduce_from_labels.py` — recomputes the headline numbers directly from the published labels CSV (no corpus download needed).
- `data/bva_decision_labels_2021_2025.csv` — the derived dataset: one row per decision (citation, year, assigned label, issue counts). This is what the result is computed from.
- `data/spotcheck_100.csv` — 100 random decisions with the Board's own disposition lines shown beside the assigned label, so the rule can be checked by eye.

## How to verify (three ways, easiest first)

1. **Recompute from the published data.** `python reproduce_from_labels.py` reads `data/bva_decision_labels_2021_2025.csv` and prints 33.3 percent. No download required.
2. **Spot-check against the public record.** Open `data/spotcheck_100.csv`, take any citation number, look it up in the Board's free decision search (https://www.index.va.gov/search/va/bva.jsp or https://search.usa.gov/search?affiliate=bvadecisions), and confirm the label matches the Board's own words.
3. **Re-run the rule from source.** The Board publishes every decision. Fetch the 2021–2025 decisions into a folder of `.txt` files and run `python census.py <folder>`; you will get the same rate the labels CSV encodes.

## Honest limits

- **This is appealed cases only** — roughly two percent of all VA claims, self-selected for being contestable. It is not, and cannot be, a VA-wide error rate.
- **Reproducibility is not the same as an accuracy audit.** The code being deterministic means the result is consistent and auditable; the spot-check shows the labels match the Board's words. A formal precision/recall validation against independent blind human coding is **not** included here — the original blind-coded validation set from the 2021–2025 study was lost. For the corroborating use this figure is put to, the deterministic rule plus the spot-check is the basis offered. A future blind re-validation on a fresh sample would add a formal accuracy figure.
- **Scope.** This repository covers only the grant/deny/remand disposition classification. It does not cover any other analysis.

## License

Code: MIT. Data: the decisions are U.S. government public records; the derived labels are released CC0 / public domain.
