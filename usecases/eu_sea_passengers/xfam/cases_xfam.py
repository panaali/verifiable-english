"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). TEMPLATE for the cross-family encoder: the build's helpers and conventions, records removed.

Each case: "facts" (unary facts true; every other one false, encode.py C1), "ints" (the ship's certified passengers and crew,
the one-way distance in metres, the overnight stays, the design year, the scheduled journey and the delay as (whole hours,
minutes), the prices and the carrier's threshold in EUR), "questions" (qid -> form: applies = Q1, right = Q2, pay = Q3),
"judgement" (anything the encoder decided beyond copying a stated fact or a convention of encode.py: listed as "encoder
judgement"). PROBES: out-of-scope cases (every answer UNSUPPORTED). No bridge: every duration is stated.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC = HERE / "questions-enc.jsonl" if (HERE / "questions-enc.jsonl").exists() else HERE.parent / "questions-enc.jsonl"
ENC_SHA256 = "10d5c74bcfec43e8add13e3a13eea9abb19182893387d6165686c1928621404b"
if hashlib.sha256(ENC.read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")

# Facts every in-scope case states or the conventions fix (encode.py C4): the passenger has a contract of carriage with c
# and a ticket; c is a legal person offering transport by sea or inland waterway to the general public; both places are
# places with works and facilities for the reception of ships from which passengers regularly embark or disembark; the
# operation is commercial and transports the passenger, on a vessel.
BASE = ["contract", "doc", "person", "offers_public", "works_e", "regular_e", "works_d", "regular_d", "commercial",
        "pax_transport", "vessel"]
SEA = ["by_sea"]
LAKE = ["inland", "water_used"]  # "operated on the inland waterway of Lake X / the river Y" (C4)
TT = ["timetable"]
MSMS = ["in_ms_e", "in_ms_d"]
FORMS = ("applies", "right", "pay")


def case(cid, facts, cap, crew, km=None, m=None, nights=0, sched=(0, 0), delay=(0, 0), price=None, rprice=None,
         thr=None, dyear=None, judgement=()):
    facts = BASE + list(facts) + (["has_thr"] if thr is not None else [])
    ints = {"cap_p": cap, "crew_p": crew, "dist_p": km * 1000 if km is not None else m, "nights_p": nights,
            "sch_h_p": sched[0], "sch_m_p": sched[1], "del_h_p": delay[0], "del_m_p": delay[1]}
    if price is not None:
        ints["price_p"] = price
    if rprice is not None:
        ints["rprice_p"] = rprice
    if thr is not None:
        ints["thr_p"] = thr
    if dyear is not None:
        ints["dyear_p"] = dyear
    return {"id": cid, "facts": facts, "ints": ints,
            "questions": [{"qid": f"{cid}-{i}", "item": "p", "form": f} for i, f in enumerate(FORMS, 1)],
            "judgement": list(judgement)}


CASES = [
    # defaults stated in every in-scope case unless the record says otherwise: c established in a Member State, both
    # ports in a Member State, by sea, published timetable, 80 passengers / 8 crew, 20000 metres, zero overnight stays,
    # single ticket for a specified departure (dep_spec), no threshold, neither weather nor extraordinary circumstances.
    case("E001", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(0, 59),
         price="80.00"),
    case("E002", SEA + TT + MSMS + ["est_ms", "dep_spec"], 13, 4, m=500, nights=0, sched=(4, 0), delay=(1, 0),
         price="80.00"),
    case("E003", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(1, 1),
         price="20.00", thr="6.00",
         judgement=["c = Harbour Navigation (the contract party); the seller Landing Tickets is not c"]),
    case("E004", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(1, 59),
         price="28.00", thr="6.00"),
    case("E005", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(2, 0),
         price="24.00", thr="6.00"),
    case("E006", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(2, 1),
         price="80.00",
         judgement=["the proposed fee/telephone/stamp deductions are not stated as facts (no vocabulary term)"]),
    case("E007", SEA + TT + ["in_ms_e", "est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 1), delay=(1, 59),
         price="80.00"),
    case("E008", SEA + TT + MSMS + ["est_ms", "ret"], 80, 8, m=20000, nights=0, sched=(8, 0), delay=(2, 0),
         price="40.00", rprice="160.00",
         judgement=["c = Harbour Navigation (the contract party); the booking retailer Harbour Bookings is not c"]),
    case("E009", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(8, 0), delay=(2, 1),
         price="80.00"),
    case("E010", SEA + TT + MSMS + ["est_ms", "dep_spec", "hist", "orig_mat"], 37, 8, m=20000, nights=0,
         sched=(8, 0), delay=(3, 59), price="80.00", dyear=1964,
         judgement=["'replica of a historical passenger ship designed in 1964': 1964 read as the design year"]),
    case("E011", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(8, 0), delay=(4, 0),
         price="80.00"),
    case("E012", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(8, 0), delay=(4, 1),
         price="80.00"),
    case("E013", LAKE + TT + ["in_ms_d", "dep_spec"], 80, 8, m=20000, nights=0, sched=(8, 1), delay=(2, 59),
         price="80.00"),
    case("E014", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 0), delay=(3, 0),
         price="80.00"),
    case("E015", SEA + TT + MSMS + ["est_ms", "dep_spec", "weather"], 80, 8, m=20000, nights=1, sched=(24, 0),
         delay=(3, 1), price="80.00",
         judgement=["c = Harbour Navigation (the contract party); the tour operator Holiday Assembly is not c"]),
    case("E016", SEA + TT + MSMS + ["est_ms", "pass_t"], 80, 8, m=20000, nights=1, sched=(24, 0), delay=(5, 59),
         price="80.00", judgement=["the travel pass is not stated to be an open ticket: open_t false (C1)"]),
    case("E017", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 0), delay=(6, 0),
         price="80.00"),
    case("E018", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 0), delay=(6, 1),
         price="80.00"),
    case("E019", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 1), delay=(5, 59),
         price="80.00"),
    case("E020", SEA + TT + MSMS + ["est_ms", "open_t", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 1),
         delay=(6, 0), price="80.00"),
    case("E021", SEA + TT + MSMS + ["est_ms", "dep_spec", "extraord"], 80, 8, m=20000, nights=1, sched=(24, 1),
         delay=(6, 1), price="80.00"),
    case("E022", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 1), delay=(11, 59),
         price="80.00"),
    case("E023", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=1, sched=(24, 1), delay=(12, 0),
         price="80.00"),
    case("E024", SEA + TT + MSMS + ["est_ms", "dep_spec", "pleasure", "accomm"], 80, 8, m=20000, nights=2,
         sched=(48, 0), delay=(12, 1), price="80.00"),
    case("E025", SEA + TT + MSMS + ["est_ms", "dep_spec"], 12, 8, m=20000, nights=0, sched=(4, 0), delay=(1, 0),
         price="80.00"),
    case("E026", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 3, m=20000, nights=0, sched=(4, 0), delay=(1, 0),
         price="80.00"),
    case("E027", SEA + TT + MSMS + ["est_ms", "dep_spec"], 80, 8, m=499, nights=0, sched=(4, 0), delay=(1, 0),
         price="80.00"),
    case("E028", SEA + TT + MSMS + ["est_ms", "dep_spec", "pleasure", "accomm", "excursion"], 80, 8, m=20000,
         nights=2, sched=(48, 0), delay=(12, 1), price="80.00"),
    case("E029", SEA + TT + MSMS + ["est_ms", "dep_spec", "hist", "orig_mat"], 36, 8, m=20000, nights=0,
         sched=(4, 0), delay=(1, 0), price="80.00", dyear=1964,
         judgement=["'replica of a historical passenger ship designed in 1964': 1964 read as the design year"]),
    case("E030", SEA + TT + MSMS + ["est_ms", "dep_spec", "not_mech"], 80, 8, m=20000, nights=0, sched=(4, 0),
         delay=(1, 0), price="80.00"),
    case("E031", SEA + MSMS + ["est_ms", "dep_spec", "pleasure", "accomm", "excursion"], 80, 8, m=20000, nights=3,
         sched=(72, 0), delay=(12, 1), price="80.00"),
    case("E032", SEA + TT + MSMS + ["est_ms", "dep_spec", "informed"], 13, 4, m=500, nights=0, sched=(4, 0),
         delay=(1, 0), price="80.00"),
    case("E033", SEA + TT + MSMS + ["est_ms", "open_t"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(1, 0),
         price="80.00"),
    case("E034", SEA + TT + ["est_ms", "dep_spec"], 80, 8, m=20000, nights=0, sched=(4, 0), delay=(1, 0),
         price="80.00"),
    case("E035", SEA + TT + MSMS + ["est_ms", "dep_spec", "fault"], 13, 4, m=500, nights=0, sched=(4, 0),
         delay=(1, 0), price="80.00"),
]

PROBES = {
    "E036": "out of scope: cancellation (Arts 16-18), not delay in arrival under Art 19",
    "E037": "out of scope: cancellation (Arts 16-18), not delay in arrival under Art 19",
    "E038": "out of scope: cancellation (Arts 16-18), not delay in arrival under Art 19",
    "E039": "out of scope: rights of disabled persons / persons with reduced mobility (Arts 7-15)",
    "E040": "out of scope: lost luggage (not covered by Arts 2, 3, 19, 20)",
    "E041": "out of scope: season-ticket recurrent delays, Art 19(2) not in the translation",
    "E042": "out of scope: Art 19(5) payment time and form not in the translation",
    "E043": "out of scope: Art 19(5) voucher conditions not in the translation",
    "E044": "out of scope: air transport, not sea or inland waterway",
    "E045": "out of scope: bus transport, not sea or inland waterway",
}
PROBE_QIDS = {cid: [f"{cid}-1"] for cid in PROBES}
UNSUPPORTED = {}
