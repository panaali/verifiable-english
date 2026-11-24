"""The reg. 3(6) household overlay for the cross-family records (row statute-xfam-wrong-uc-award-1).

The fix reads a field the frozen encoders never stated: absent_from(x, y), the household a temporary absence is from
(translation.absent6). A fresh Opus 5.5 encoder seat (reg36-enc/README.md) wrote reg36-enc/absences.jsonl from the Codex
set's questions-enc.jsonl and the law only. This module applies it MECHANICALLY to the frozen records (cases_xfam.py is
unchanged): for each absence line, in every award record of that case where the absent person is a member of a stated
couple, add ("absent_from", person, y) for each named household member y (a household outside the record is an error,
not skipped: the default would misread it). Lines for
persons in no couple (children: reg. 4(7) reads only the unary facts) are not applied; no other field changes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

FILE = Path(__file__).resolve().parent / "reg36-enc" / "absences.jsonl"


def lines(path=FILE):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def apply(cases, path=FILE):
    """-> {record id: [links added]}; the records in `cases` are updated in place."""
    added = {}
    for ln in lines(path):
        if not isinstance(ln["absent_from"], list):
            continue
        x = ln["person"].lower()
        for rec in cases:
            if rec["case"] != ln["id"] or x not in rec["persons"]:
                continue
            if not any(l[0] == "couple" and x in l[1:] for l in rec["links"]):
                continue
            for name in ln["absent_from"]:
                y = name.lower()
                link = ["absent_from", x, y]
                if y not in rec["persons"]:
                    raise ValueError(f"{rec['id']}: {x}'s absence is from {y}'s household, not a person of the record "
                                     "(the absent6 default would read it as the record's own couple)")
                if y != x and link not in rec["links"]:
                    rec["links"].append(link)
                    added.setdefault(rec["id"], []).append(tuple(link))
    return added


def sha256(path=FILE):
    return hashlib.sha256(path.read_bytes()).hexdigest()
