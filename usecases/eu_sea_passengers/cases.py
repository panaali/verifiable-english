"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-eu-sea-passengers-1123 (Opus 5.5), after the translation was committed (8cfbe1c30b, 19:50Z).
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
ENC_SHA256 = "bbd5ed40ac4dca14703cbf5886a056410d5702abee25fee32845c0de02c7a817"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
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
    # Tallinn (MS) -> Helsinki (MS); c established in Estonia
    case("E001", SEA + TT + MSMS + ["est_ms"], 2000, 40, km=82, sched=(2, 0), delay=(1, 0), price="48.00"),
    case("E002", SEA + TT + MSMS + ["est_ms"], 2000, 40, km=82, sched=(2, 30), delay=(0, 59), price="52.00"),
    # Algeciras (MS) -> Tangier (not); c in Spain
    case("E003", SEA + TT + ["in_ms_e", "est_ms"], 1200, 25, km=60, sched=(1, 30), delay=(2, 0), price="36.00"),
    # Tangier (not) -> Algeciras (MS); c in Morocco (not a Member State)
    case("E004", SEA + TT + ["in_ms_d"], 1200, 25, km=60, sched=(1, 30), delay=(2, 1), price="40.00"),
    # Lake Geneva: Lausanne (not) -> Geneva (not); c in Switzerland
    case("E005", LAKE + TT, 600, 8, km=60, sched=(3, 30), delay=(2, 0), price="44.00"),
    # Genoa (MS) -> Tunis (not); c in Tunisia; accommodation, 1 overnight stay; purpose transport
    case("E006", SEA + TT + ["in_ms_e", "accomm"], 1800, 60, km=870, nights=1, sched=(24, 0), delay=(6, 0),
         price="160.00"),
    case("E007", SEA + TT + MSMS + ["est_ms", "accomm"], 2200, 70, km=1000, nights=1, sched=(24, 1), delay=(5, 59),
         price="140.00"),
    # through Harbour Tickets Online (a retailer for the carrier: not c)
    case("E008", SEA + TT + MSMS + ["est_ms", "accomm"], 1500, 45, km=270, nights=1, sched=(10, 0), delay=(6, 1),
         price="90.00"),
    # Bari (MS) -> Durres (not)
    case("E009", SEA + TT + ["in_ms_e", "est_ms", "accomm"], 1400, 40, km=230, nights=1, sched=(8, 0), delay=(2, 0),
         price="70.00"),
    case("E010", SEA + TT + MSMS + ["est_ms"], 800, 18, km=70, sched=(4, 0), delay=(2, 1), price="30.00"),
    case("E011", SEA + TT + MSMS + ["est_ms"], 1000, 22, km=145, sched=(4, 1), delay=(1, 59), price="42.00"),
    # through Nordreise Travel (a retailer acting for Sven: not c); threshold EUR 6.00
    case("E012", SEA + TT + MSMS + ["est_ms"], 900, 30, km=170, sched=(6, 0), delay=(4, 1), price="55.00", thr="6.00"),
    # storm said, not proved (weather false)
    case("E013", SEA + TT + MSMS + ["est_ms", "accomm"], 1600, 55, km=1100, nights=1, sched=(30, 0), delay=(12, 1),
         price="200.00"),
    # no published timetable
    case("E014", SEA + MSMS + ["est_ms"], 150, 6, km=45, sched=(2, 0), delay=(3, 0), price="60.00"),
    # return, both legs EUR 240.00
    case("E015", SEA + TT + MSMS + ["est_ms", "accomm", "ret"], 1500, 50, km=560, nights=1, sched=(18, 0),
         delay=(3, 0), rprice="240.00"),
    # return; the delayed (return) leg Bodrum (not) -> Kos (MS), the facts' ports; c in Turkiye
    case("E016", SEA + TT + ["in_ms_d", "ret"], 350, 10, km=25, sched=(0, 45), delay=(2, 5), rprice="50.00"),
    # Danube, no timetable, exclusively pleasure, accommodation, 5 overnight stays; Passau (MS) -> Budapest (MS)
    case("E017", LAKE + MSMS + ["est_ms", "pleasure", "accomm"], 180, 40, km=640, nights=5, sched=(120, 0),
         delay=(10, 0), price="1200.00"),
    # Rhine, timetable, exclusively pleasure, accommodation, 2 overnight stays; contract with Rhine Leisure Lines (c),
    # concluded through Lowlands Holidays (a package organiser, not a carrier: not c)
    case("E018", LAKE + TT + MSMS + ["est_ms", "pleasure", "accomm"], 160, 30, km=700, nights=2, sched=(50, 0),
         delay=(7, 0), price="480.00",
         judgement=["an operation exclusively for pleasure and recreation, run to a published timetable, read as a "
                    "passenger transport service (Art 3(f)): it transports the passenger (pax_transport)"]),
    # Lake Garda
    case("E019", LAKE + TT + MSMS + ["est_ms"], 12, 4, km=15, sched=(0, 40), delay=(1, 30), price="40.00"),
    case("E020", LAKE + TT + MSMS + ["est_ms"], 13, 4, km=10, sched=(1, 0), delay=(1, 30), price="20.00", thr="8.00"),
    # Lake Constance, crew 3
    case("E021", LAKE + TT + MSMS + ["est_ms"], 150, 3, km=4, sched=(0, 20), delay=(1, 10), price="12.00"),
    # Rhine, 499 m / 500 m
    case("E022", LAKE + TT + MSMS + ["est_ms"], 300, 5, m=499, sched=(0, 10), delay=(1, 0), price="8.00"),
    case("E023", LAKE + TT + MSMS + ["est_ms"], 300, 5, m=500, sched=(0, 10), delay=(1, 0), price="4.00", thr="2.00"),
    # Seine sightseeing: exclusively pleasure, an excursion or sightseeing tour, no accommodation
    case("E024", LAKE + TT + MSMS + ["est_ms", "pleasure", "excursion"], 250, 5, km=7, sched=(1, 0), delay=(1, 30),
         price="20.00"),
    # Lake Geneva: Evian (MS) -> Lausanne (not); steam engine; individual replica designed 1912, original materials; 36
    case("E025", LAKE + TT + ["in_ms_e", "est_ms", "hist", "orig_mat"], 36, 6, km=13, sched=(1, 0), delay=(1, 0),
         price="24.00", dyear=1912),
    # Lake Como; the same with 37 passengers; threshold EUR 6.00
    case("E026", LAKE + TT + MSMS + ["est_ms", "hist", "orig_mat"], 37, 6, km=30, sched=(3, 0), delay=(1, 0),
         price="32.00", thr="6.00", dyear=1912),
    # sail only, no engine; 50 passengers; not a historical ship
    case("E027", SEA + TT + MSMS + ["est_ms", "accomm", "not_mech"], 50, 10, km=200, nights=1, sched=(20, 0),
         delay=(4, 0), price="150.00"),
    # open ticket, no time of departure ever specified
    case("E028", SEA + TT + MSMS + ["est_ms", "open_t"], 1000, 22, km=170, sched=(5, 0), delay=(3, 0), price="60.00"),
    # open ticket, time of departure specified
    case("E029", SEA + TT + MSMS + ["est_ms", "open_t", "dep_spec"], 1000, 22, km=170, sched=(5, 0), delay=(4, 0),
         price="60.00"),
    # Lake Constance: Friedrichshafen (MS) -> Romanshorn (not); a travel pass, no time of departure specified;
    # the price actually paid for the delayed service EUR 4.80 (stated)
    case("E030", LAKE + TT + ["in_ms_e", "est_ms", "pass_t", "open_t"], 700, 9, km=12, sched=(0, 40), delay=(1, 5),
         price="4.80",
         judgement=["a travel pass with no time of departure specified also read as an open ticket (open_t; the "
                    "travel-pass exception of Art 20(1) then applies)"]),
    # informed before buying
    case("E031", SEA + TT + MSMS + ["est_ms", "informed"], 2000, 40, km=82, sched=(2, 0), delay=(1, 30),
         price="48.00"),
    # informed after buying
    case("E032", SEA + TT + MSMS + ["est_ms"], 2000, 40, km=82, sched=(3, 0), delay=(2, 30), price="44.00"),
    # the passenger's fault
    case("E033", SEA + TT + MSMS + ["est_ms", "fault"], 900, 30, km=170, sched=(6, 0), delay=(3, 0), price="56.00"),
    # Dublin (MS) -> Holyhead (not); weather proved (stated judgment)
    case("E034", SEA + TT + ["in_ms_e", "est_ms", "weather"], 1500, 50, km=110, sched=(3, 15), delay=(7, 0),
         price="64.00"),
    # extraordinary circumstances proved (stated judgment); accommodation, 1 overnight stay
    case("E035", SEA + TT + MSMS + ["est_ms", "accomm", "extraord"], 2200, 70, km=320, nights=1, sched=(10, 0),
         delay=(8, 0), price="96.00"),
]

PROBES = {
    "E036": "cancellation: re-routing or reimbursement (Arts 17, 18)",
    "E037": "assistance in the event of delayed departure (Art 17)",
    "E038": "rights of disabled persons",
    "E039": "lost luggage",
    "E040": "adequate compensation for recurrent delays on a season ticket (Art 19(2))",
    "E041": "how and when compensation is paid, vouchers (Art 19(5))",
    "E042": "a journey by air",
    "E043": "a journey by rail",
    "E044": "a journey by bus",
    "E045": "cancellation: accommodation (Art 17)",
}
PROBE_QIDS = {cid: [f"{cid}-1"] for cid in PROBES}
UNSUPPORTED = {}
