#!/usr/bin/env python3
"""
bva_det_parser.py  (RECONSTRUCTED 2026-09-12 from BVA_study_METHODS_2026-09-06.md spec)

Deterministic ORDER-section classifier for BVA decisions.
Reads each decision's dispositive (ORDER) section and classifies every issue's disposition,
distinguishing a MERITS grant (a substantive benefit) from a PROCEDURAL reopening
("application/petition to reopen ... is granted"), which is NOT counted as overturning the RO.

Decision-level label:
  merits_grant = the decision grants >=1 issue on the merits (>=1 non-procedural grant)
  fully_affirmed = >=1 issue, every issue denied (no grant/remand/dismissal)
Reproduction targets (METHODS sec.7): 32.8% decisions w/ >=1 merits grant (denom = parsed),
  18.9% issue-level merits grants, 18.4% fully affirmed.
"""
import re

# ---- dispositive-block boundaries ----
RE_ORDER = re.compile(r'(?m)^\s*ORDER\s*$')
RE_DATELINE = re.compile(r'(?m)^\s*DATE:\s*.*$')
RE_BLOCK_END = re.compile(
    r'(FINDINGS? OF FACT|REASONS AND BASES|REASONS FOR REMAND|CONCLUSIONS? OF LAW'
    r'|REASONS? FOR DECISION|THE BOARD OF VETERANS)', re.I)

# ---- disposition verbs ----
RE_DISP = re.compile(r'\b(?:is|are)\s+(granted|denied|remanded|dismissed|vacated|withdrawn)\b', re.I)
# grant that is merely procedural (reopening), not a merits win
RE_PROC_SUBJECT = re.compile(
    r'(application|petition|motion|request)\b[^.;]{0,80}\b(to\s+)?reopen', re.I)
RE_REOPEN_GRANT = re.compile(r'\b(to\s+reopen|reopening|new and material evidence|readjudicat)'
                             r'[^.;]{0,60}\b(is|are)\s+granted', re.I)
# "reopened and granted" / a substantive grant verb present -> still merits
RE_SUBSTANTIVE_GRANT_CTX = re.compile(
    r'(service connection|compensation|disability rating|evaluation|entitlement to an? (?:increased|higher|earlier|effective)'
    r'|total disability|individual unemployability|TDIU|special monthly|reopened and granted)', re.I)


def extract_block(text):
    """Return the dispositive block (ORDER section or top disposition block)."""
    m = RE_ORDER.search(text)
    if m:
        start = m.end()
    else:
        d = RE_DATELINE.search(text)
        start = d.end() if d else 0
    rest = text[start:]
    e = RE_BLOCK_END.search(rest)
    block = rest[:e.start()] if e else rest[:4000]
    return block


def split_issues(block):
    """Split the block into issue-statement sentences, each containing one disposition."""
    # normalize whitespace; split on sentence boundaries that precede a new 'Entitlement/The/Service' etc.
    # Simplest robust unit: each disposition verb match anchors one issue; take the clause ending at it.
    issues = []
    last = 0
    for m in RE_DISP.finditer(block):
        clause = block[last:m.end()]
        issues.append((clause, m.group(1).lower()))
        last = m.end()
    return issues


def classify_issue(clause, disp):
    """Return one of: merits_grant, proc_grant, denied, remanded, dismissed."""
    if disp == 'granted':
        # procedural reopening grant?
        if RE_REOPEN_GRANT.search(clause) or RE_PROC_SUBJECT.search(clause):
            if not re.search(r'reopened and granted', clause, re.I):
                return 'proc_grant'
        return 'merits_grant'
    if disp in ('denied',):
        return 'denied'
    if disp in ('remanded',):
        return 'remanded'
    if disp in ('dismissed', 'vacated', 'withdrawn'):
        return 'dismissed'
    return 'other'


def classify_decision(text):
    """Return dict with issue counts and decision-level flags. None-ish if unparsed."""
    block = extract_block(text)
    issues = split_issues(block)
    cats = [classify_issue(c, d) for c, d in issues]
    n = len(cats)
    if n == 0:
        return {'parsed': False}
    merits_g = cats.count('merits_grant')
    proc_g = cats.count('proc_grant')
    denied = cats.count('denied')
    remanded = cats.count('remanded')
    dismissed = cats.count('dismissed')
    has_merits_grant = merits_g > 0
    fully_affirmed = (denied > 0 and merits_g == 0 and proc_g == 0
                      and remanded == 0 and dismissed == 0)
    return {
        'parsed': True, 'n_issues': n,
        'merits_grant': merits_g, 'proc_grant': proc_g,
        'denied': denied, 'remanded': remanded, 'dismissed': dismissed,
        'has_merits_grant': has_merits_grant, 'fully_affirmed': fully_affirmed,
    }
