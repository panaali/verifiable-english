"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-sick-pay-1123 (Opus 5.5), after the translation was committed (86c744516b). Each in-scope case
is transcribed by hand from its facts into one Spec per employer (encode.py): the contract (first day, last day, normal
weekly earnings, the day a disqualifying period begins), the stated day ranges (no illness / an illness the employee
cannot (or can) reasonably be expected to work with / deemed incapable by regulations), the weekly required or agreed days
(Sunday = 0 ... Saturday = 6), the anchor (a day the facts name with its day of the week: the first Sunday they name), and
the asked days and runs. The questions' forms (rate / pay / amount / run) and dates are read from their text by QRE.
"judgement": anything the encoder decided beyond copying a stated fact (listed as "encoder judgement").
PROBES: out-of-scope cases (scope "out" in questions-enc.jsonl: every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from encode import Spec

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "340163743ad16d66dcf3c418c738a145c29424e4db98d0d3dbbc0d546c3e387e"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

N, I, ILLCAN, DM = set(), {"dis", "cannot"}, {"dis"}, {"deemed"}
MF, ALL7 = [1, 2, 3, 4, 5], list(range(7))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
DATE = r"(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday) (\d{1,2}) (\w+) (\d{4})"


def iso(m):
    return dt.date(int(m[2]), MONTHS.index(m[1]) + 1, int(m[0])).isoformat()


def parse_q(text):
    """-> (employer, form, args) from a question's text."""
    m = re.match(r"What is the weekly rate of statutory sick pay for \w+ from (.+)\?$", text)
    if m:
        return m[1], "rate", {}
    m = re.match(r"Is statutory sick pay payable by (.+) to \w+ for " + DATE + r"\?$", text)
    if m:
        return m[1], "pay", {"date": iso(m.groups()[1:])}
    m = re.match(r"What amount of statutory sick pay is payable by (.+) to \w+ for the days from " + DATE + " to " + DATE
                 + r"\?$", text)
    if m:
        g = m.groups()
        return g[0], "run", {"first": iso(g[1:4]), "last": iso(g[4:7])}
    m = re.match(r"What amount of statutory sick pay is payable by (.+) to \w+ for " + DATE + r"\?$", text)
    if m:
        return m[1], "amount", {"date": iso(m.groups()[1:])}
    raise ValueError(text)


ENC = {c["id"]: c for c in map(json.loads, (HERE / "questions-enc.jsonl").read_text(encoding="utf-8").splitlines())}

# (contract, spans, weekly, anchor) per employer; spans/weekly as encode.Spec
S = {}


def sub(cid, employer, contract, spans, weekly, anchor):
    S.setdefault(cid, {})[employer] = (contract, spans, weekly, anchor)


def C(start, end, nwe, dq=None):
    return {"start": start, "end": end, "nwe": nwe, "dq": dq}


sub("S001", "Harbour Bakery Limited", C("2026-04-06", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-05-04", N), ("2026-05-05", "2026-05-05", I), ("2026-05-06", "2026-05-31", N)],
    [("2026-05-03", "2026-05-09", {"required": MF})], ("2026-05-03", 0))
sub("S002", "Quarry Lane Garage Limited", C("2026-04-06", "2027-04-30", "200.00"),
    [("2026-01-01", "2026-05-13", N), ("2026-05-14", "2026-05-20", DM), ("2026-05-21", "2026-05-31", N)],
    [("2026-05-10", "2026-05-23", {"required": MF})], ("2026-05-10", 0))
sub("S003", "Willow Print Limited", C("2026-04-06", "2027-03-31", "154.10"),
    [("2026-01-01", "2026-06-07", N), ("2026-06-08", "2026-06-12", DM), ("2026-06-13", "2026-06-30", N)],
    [("2026-04-05", "2026-06-27", {"agreed": [3]})], ("2026-04-05", 0))
sub("S004", "Northgate Library Trust", C("2026-04-06", "2027-03-31", "154.05"),
    [("2026-01-01", "2026-06-14", N), ("2026-06-15", "2026-06-19", DM), ("2026-06-20", "2026-06-30", N)],
    [("2026-06-14", "2026-06-20", {"required": [1, 3, 5]})], ("2026-06-14", 0))
sub("S005", "Cedar Dental Practice Limited", C("2026-04-06", "2027-03-31", "154.06"),
    [("2026-01-01", "2026-06-17", N), ("2026-06-18", "2026-06-18", DM), ("2026-06-19", "2026-06-30", N)],
    [("2026-06-14", "2026-06-20", {"required": MF})], ("2026-06-14", 0))
sub("S006", "Meadowbank Care Home Limited", C("2026-04-06", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-06-25", N), ("2026-06-26", "2026-06-29", DM), ("2026-06-30", "2026-07-31", N)],
    [("2026-06-21", "2026-07-04", {"required": ALL7})], ("2026-06-21", 0))
sub("S007", "Fernhill Office Supplies Limited", C("2026-04-06", "2027-03-31", "150.00"),
    [("2026-01-01", "2026-07-03", N), ("2026-07-04", "2026-07-06", I), ("2026-07-07", "2026-07-31", N)],
    [("2026-06-28", "2026-07-11", {"required": MF})], ("2026-06-28", 0))
sub("S008", "Bridge Street Accountants Limited", C("2026-04-06", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-07-06", N), ("2026-07-07", "2026-07-07", ILLCAN), ("2026-07-08", "2026-07-08", I),
     ("2026-07-09", "2026-07-31", N)],
    [("2026-07-05", "2026-07-11", {"required": MF})], ("2026-07-05", 0))
sub("S009", "Oakfield Joinery Limited", C("2026-04-06", "2027-03-31", "150.00"),
    [("2026-01-01", "2026-07-12", N), ("2026-07-13", "2026-07-15", DM), ("2026-07-16", "2026-07-31", N)],
    [("2026-07-12", "2026-07-18", {"required": MF})], ("2026-07-12", 0))
sub("S010", "Lakeside Hotel Limited", C("2026-06-03", "2027-06-30", "105.00"),
    [("2026-01-01", "2026-05-31", N), ("2026-06-01", "2026-06-05", DM), ("2026-06-06", "2026-06-30", N)],
    [("2026-05-31", "2026-06-06", {"required": [3, 4, 5]}), ("2026-06-07", "2026-06-20", {"required": MF})],
    ("2026-05-31", 0))
sub("S011", "Ashby Transport Limited", C("2026-05-18", "2027-05-31", "150.00"),
    [("2026-01-01", "2026-05-03", N), ("2026-05-04", "2026-05-08", DM), ("2026-05-09", "2026-06-07", N),
     ("2026-06-08", "2026-06-10", DM), ("2026-06-11", "2026-06-30", N)],
    [("2026-05-17", "2026-06-13", {"required": MF})], ("2026-05-17", 0))
sub("S012", "Westmoor Farm Shop Limited", C("2026-04-06", "2026-06-17", "105.00"),
    [("2026-01-01", "2026-06-14", N), ("2026-06-15", "2026-06-19", DM), ("2026-06-20", "2026-06-30", N)],
    [("2026-04-05", "2026-06-13", {"required": MF}), ("2026-06-14", "2026-06-20", {"required": [1, 2, 3]})],
    ("2026-04-05", 0))
sub("S013", "Riverside Garden Centre Limited", C("2026-04-06", "2026-06-23", "150.00"),
    [("2026-01-01", "2026-06-21", N), ("2026-06-22", "2026-06-26", DM), ("2026-06-27", "2026-07-31", N)],
    [("2026-04-05", "2026-06-20", {"required": MF}), ("2026-06-21", "2026-06-27", {"required": [1, 2]})],
    ("2026-04-05", 0))
sub("S014", "Kestrel Software Limited", C("2026-04-06", "2027-03-31", "200.00"),
    [("2026-01-01", "2026-07-19", N), ("2026-07-20", "2026-07-22", DM), ("2026-07-23", "2026-09-30", N)],
    [("2026-07-19", "2026-07-25", {"required": MF})], ("2026-07-19", 0))
sub("S015", "Elm Logistics Limited", C("2026-03-02", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-03-31", N), ("2026-04-01", "2026-10-31", DM)],
    [("2026-03-29", "2026-10-31", {"required": MF})], ("2026-03-29", 0))
sub("S016", "Granite Stoneworks Limited", C("2026-03-02", "2027-03-31", "150.00"),
    [("2026-01-01", "2026-04-01", N), ("2026-04-02", "2026-10-31", DM)],
    [("2026-03-29", "2026-10-10", {"required": MF}), ("2026-10-11", "2026-10-17", {"required": [1, 3, 5]}),
     ("2026-10-18", "2026-10-31", {"required": MF})], ("2026-03-29", 0))
sub("S017", "Fairway Couriers Limited", C("2026-03-02", "2027-06-30", "105.00"),
    [("2026-01-01", "2026-04-05", N), ("2026-04-06", "2026-09-25", DM), ("2026-09-26", "2026-11-20", N),
     ("2026-11-21", "2026-12-18", DM)],
    [("2026-04-05", "2026-12-19", {"required": MF})], ("2026-04-05", 0))
sub("S018", "Hollins Haulage Limited", C("2026-03-02", "2027-06-30", "105.00"),
    [("2026-01-01", "2026-04-05", N), ("2026-04-06", "2026-09-25", DM), ("2026-09-26", "2026-11-21", N),
     ("2026-11-22", "2026-12-18", DM)],
    [("2026-04-05", "2026-12-19", {"required": MF})], ("2026-04-05", 0))
sub("S019", "Pebble Beach Café Limited", C("2026-03-02", "2027-03-31", "200.00"),
    [("2026-01-01", "2026-04-07", N), ("2026-04-08", "2026-10-31", DM)],
    [("2026-03-29", "2026-10-31", {"agreed": [1]})], ("2026-03-29", 0))
sub("S020", "Bluebell Nursery Limited", C("2026-04-06", "2027-03-31", "105.00", dq="2026-07-12"),
    [("2026-01-01", "2026-06-28", N), ("2026-06-29", "2026-07-24", I)],
    [("2026-06-28", "2026-07-25", {"required": MF})], ("2026-06-28", 0))
sub("S021", "Silverdale Cleaning Services Limited", C("2026-04-06", "2027-03-31", "200.00", dq="2026-07-15"),
    [("2026-01-01", "2026-07-05", N), ("2026-07-06", "2026-07-17", DM)],
    [("2026-07-05", "2026-07-18", {"required": MF})], ("2026-07-05", 0))
for emp, nwe, req in (("Hilltop Farm Limited", "105.00", MF), ("River Café Limited", "60.00", [0, 3, 6])):
    sub("S022", emp, C("2026-04-06", "2027-03-31", nwe),
        [("2026-01-01", "2026-06-01", N), ("2026-06-02", "2026-06-06", DM), ("2026-06-07", "2026-06-30", N)],
        [("2026-05-31", "2026-06-06", {"required": req})], ("2026-05-31", 0))
sub("S023", "Moorland Water Services Limited", C("2026-04-06", "2027-03-31", "150.00"),
    [("2026-01-01", "2026-08-01", N), ("2026-08-02", "2026-08-08", DM), ("2026-08-09", "2026-08-31", N)],
    [("2026-07-26", "2026-08-15", {"agreed": [2, 4]})], ("2026-07-26", 0))
sub("S024", "Thornbury Bookshop Limited", C("2026-04-06", "2027-03-31", "45.00"),
    [("2026-01-01", "2026-08-11", N), ("2026-08-12", "2026-08-14", DM), ("2026-08-15", "2026-08-31", N)],
    [("2026-08-09", "2026-08-15", {"required": [1, 2, 3, 4]})], ("2026-08-09", 0))
sub("S025", "Brookside Deliveries Limited", C("2026-04-06", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-08-20", N), ("2026-08-21", "2026-08-23", I), ("2026-08-24", "2026-08-31", N)],
    [("2026-08-16", "2026-08-29", {"required": [1, 2, 3, 4, 5, 6]})], ("2026-08-16", 0))
sub("S026", "Cobble Street Pharmacy Limited", C("2026-04-06", "2027-03-31", "150.00"),
    [("2026-01-01", "2026-08-25", N), ("2026-08-26", "2026-09-01", DM), ("2026-09-02", "2026-09-30", N)],
    [("2026-08-23", "2026-08-29", {"required": [1, 3, 5]}), ("2026-08-30", "2026-09-05", {"required": MF})],
    ("2026-08-23", 0))
sub("S027", "Lantern Theatre Trust Limited", C("2026-04-06", "2027-03-31", "200.00"),
    [("2026-01-01", "2026-09-07", N), ("2026-09-08", "2026-09-08", DM), ("2026-09-09", "2026-09-09", N),
     ("2026-09-10", "2026-09-10", DM), ("2026-09-11", "2026-09-30", N)],
    [("2026-09-06", "2026-09-12", {"required": MF})], ("2026-09-06", 0))
sub("S028", "Orchard Vets Limited", C("2026-09-12", "2027-09-30", "105.00"),
    [("2026-01-01", "2026-09-09", N), ("2026-09-10", "2026-09-15", DM), ("2026-09-16", "2026-09-30", N)],
    [("2026-09-06", "2026-09-12", {"required": []}), ("2026-09-13", "2026-09-26", {"required": MF})],
    ("2026-09-13", 0))
sub("S029", "Pinewood Sawmill Limited", C("2026-04-06", "2026-09-18", "105.00"),
    [("2026-01-01", "2026-09-18", N), ("2026-09-19", "2026-09-25", DM)],
    [("2026-04-05", "2026-09-19", {"required": MF})], ("2026-04-05", 0))
sub("S030", "Fieldgate School Trust", C("2026-04-06", "2027-03-31", "120.00"),
    [("2026-01-01", "2026-09-27", N), ("2026-09-28", "2026-10-02", I), ("2026-10-03", "2026-10-31", N)],
    [("2026-09-27", "2026-10-03", {"required": MF})], ("2026-09-27", 0))
sub("S031", "Hazel Court Lettings Limited", C("2026-04-06", "2027-03-31", "150.00"),
    [("2026-01-01", "2026-10-04", N), ("2026-10-05", "2026-10-09", DM), ("2026-10-10", "2026-10-31", N)],
    [("2026-09-27", "2026-10-17", {"agreed": [1, 3, 5]})], ("2026-09-27", 0))
sub("S032", "Canal Boat Hire Limited", C("2026-04-06", "2027-03-31", "200.00"),
    [("2026-01-01", "2026-10-12", N), ("2026-10-13", "2026-10-16", DM), ("2026-10-17", "2026-10-31", N)],
    [("2026-10-11", "2026-10-17", {"required": [4]})], ("2026-10-11", 0))
sub("S033", "Larch Engineering Limited", C("2026-06-01", "2027-05-31", "105.00"),
    [("2026-01-01", "2026-05-03", N), ("2026-05-04", "2026-05-06", DM), ("2026-05-07", "2026-07-05", N),
     ("2026-07-06", "2026-07-07", DM), ("2026-07-08", "2026-07-31", N)],
    [("2026-05-31", "2026-07-11", {"required": MF})], ("2026-05-31", 0))
sub("S034", "Quayside Ices Limited", C("2026-04-06", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-05-31", N), ("2026-06-01", "2026-06-05", DM), ("2026-06-06", "2026-07-31", N),
     ("2026-08-01", "2026-08-05", DM), ("2026-08-06", "2026-08-31", N)],
    [("2026-05-31", "2026-08-08", {"required": MF})], ("2026-05-31", 0))
sub("S035", "Market Hall Traders Limited", C("2026-04-06", "2027-03-31", "105.00"),
    [("2026-01-01", "2026-10-22", N), ("2026-10-23", "2026-10-26", I), ("2026-10-27", "2026-11-15", N)],
    [("2026-10-18", "2026-10-31", {"required": [0, 6]})], ("2026-10-18", 0))

# Encoder judgement (a decision beyond copying a stated fact; such a case leaves "without anything computed outside Lean"):
JUDGEMENT = {
    "S028": ["the week beginning Sunday 6 September: no day of it is a required day (Sunday to Friday fall before the "
             "contract first takes effect; the contract does not require Saturday 12 September)"],
}
# Transcription notes (copies of stated facts, not judgement; listed for the audit):
NOTES = {
    "S010": "the week beginning Sunday 31 May: its required days are the stated Wednesday to Friday",
    "S011": "'on the days of that gap on which the contract requires it, Kofi works': no incapacity, as stated",
    "S013": "'brought to an end on Tuesday 23 June 2026, which is the last day of the contract': the contract's end day",
    "S020": "the maternity pay period begins on 12 July: the disqualifying period's start (fixed fact of the brief)",
    "S021": "the maternity allowance period begins on 15 July: the disqualifying period's start (fixed fact)",
    "S022": "two employers: one sub-case each (C2); 'This applies under both contracts': deemed under each",
}


def _build():
    cases, probes, probe_qids = [], {}, {}
    for cid, c in ENC.items():
        if c["scope"] == "out":
            probes[cid] = "out-of-scope probe (questions-enc.jsonl scope 'out': SELECTION.md 'Not supported')"
            probe_qids[cid] = [q["qid"] for q in c["questions"]]
            continue
        by_emp = {}
        for q in c["questions"]:
            emp, form, args = parse_q(q["text"])
            by_emp.setdefault(emp, []).append({"qid": q["qid"], "form": form, **args})
        subs = []
        for emp, qs in by_emp.items():
            contract, spans, weekly, anchor = S[cid][emp]
            asked = sorted({q["date"] for q in qs if q["form"] in ("pay", "amount")})
            runs = sorted({(q["first"], q["last"]) for q in qs if q["form"] == "run"})
            spec = Spec(f"{cid}/{emp}", contract, spans, weekly, anchor, asked=asked, runs=runs)
            subs.append({"employer": emp, "spec": spec, "questions": qs})
        cases.append({"id": cid, "subs": subs, "judgement": JUDGEMENT.get(cid, [])})
    return cases, probes, probe_qids


CASES, PROBES, PROBE_QIDS = _build()
UNSUPPORTED = {}
