"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). SAME-FAMILY.

Encoder: dri-statute-corpus-ved-first-year-1123 (Opus 5.5), after the translation was committed (63a9392685, 00:39:59Z);
questions-enc.jsonl opened at 00:40:04Z. One vehicle per case (item v1). Per vehicle: "facts" (unary facts true of it, every
other one false: encode.py C1), "ints" (dreg = the day it was FIRST registered, under the Act or under the law of a country
outside the United Kingdom; co2 = the stated applicable CO2 emissions figure, only where the certificate specifies one; lp
= list price or np = notional price), accessories (each with its facts and stated price), licences (one item per licence
date a question asks about, other than the first). The questions' forms are copied from questions-enc.jsonl: Q1 -> rate1
(the vehicle), Q2 -> rate2 and Q3 -> ge2 (the licence taking effect on the date the question names; the date is read from
the question text and must be one of the case's licence dates). "judgement": anything the encoder decided beyond copying a
stated fact (flips.py flips each). PROBES: out-of-scope cases (every answer UNSUPPORTED).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "19493bd2b34a7d8d28b7e6b6018640b7159597c91dcd9cbb0cf624df4fe655c8"
_RAW = (HERE / "questions-enc.jsonl").read_bytes()
if hashlib.sha256(_RAW).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")
ENC = [json.loads(l) for l in _RAW.decode().splitlines() if l.strip()]

COC, UKAC = ["basis_coc", "cert_lpv"], ["basis_ukac", "cert_lpv"]
FIG = ["cert_co2"]          # the certificate specifies a CO2 emissions figure in g/km
ZERO = ["zero_rate"]        # "the vehicle's rate of carbon dioxide emissions (in g/km) is zero"
D = ["diesel"]              # constructed to be propelled by diesel
E6D, TEMP = ["ind6d"], ["ind6dtemp"]  # what an EU certificate of conformity indicates (encode.py C3)
LP = ["has_lp"]
ACC = ["a_nonstd", "a_attached", "a_has_lp"]  # non-standard, attached when first registered under the Act, list price


def acc(n, price, facts=ACC):
    key = "alp" if "a_has_lp" in facts else "anp"
    return {"n": n, "facts": list(facts), "ints": {key: price}}


# id: (facts, first registration, CO2 figure or None, ("lp"|"np", price), accessories, licence dates, judgement)
V = {
    "V001": (COC + FIG + ZERO + LP, "2026-06-10", "0", ("lp", "48000.00"), [], ["2027-06-10"], []),
    "V002": (UKAC + ZERO + LP, "2025-08-03", None, ("lp", "50000.00"), [], ["2026-08-03"], []),
    "V003": (COC + ZERO + LP, "2025-09-01", None, ("lp", "50000.01"), [], ["2026-09-01"], []),
    "V004": (COC + FIG + ZERO + LP, "2026-01-05", "0", ("lp", "49500.00"), [acc(1, "600.00")],
             ["2027-01-05", "2032-01-05"], []),
    "V005": (COC + ZERO + LP, "2025-03-20", None, ("lp", "72000.00"), [], ["2026-03-20"], []),
    "V006": (UKAC + FIG + ZERO + LP, "2025-04-01", "0", ("lp", "65000.00"), [], ["2026-04-01"], []),
    "V007": (COC + FIG + ZERO + LP + ["taxi"], "2026-02-02", "0", ("lp", "58000.00"), [], ["2027-02-02"], []),
    "V008": (COC + FIG + E6D + LP, "2026-05-12", "1", ("lp", "41000.00"), [], ["2027-05-12", "2032-05-13"], []),
    "V009": (UKAC + FIG + LP, "2025-07-01", "50", ("lp", "40000.00"), [], ["2026-07-01"],
             ["a UK approval certificate 'indicates the Euro 6d emission standard': ind6d false (not an EU certificate "
              "of conformity; petrol, so it moves nothing)"]),
    "V010": (COC + FIG + LP, "2025-10-15", "51", ("lp", "40000.01"), [], ["2026-10-15"], []),
    "V011": (COC + FIG + D + E6D + LP, "2026-03-03", "90", ("lp", "38500.00"), [acc(1, "1600.00")], ["2027-03-03"], []),
    "V012": (COC + FIG + E6D + LP, "2025-11-09", "91", ("lp", "39000.00"),
             [acc(1, "1000.50", ["a_nonstd", "a_attached"])], ["2026-11-09"], []),
    "V013": (UKAC + FIG + LP, "2026-01-20", "110", ("lp", "36000.00"),
             [acc(1, "3000.00"), acc(2, "2500.00", ["a_nonstd", "a_has_lp"])], ["2027-01-20"],
             ["the roof box fitted on 14 February 2026, after first registration: not attached when first registered "
              "under the Act (a_attached false)",
              "a UK approval certificate 'indicates the Euro 6d emission standard': ind6d false (not an EU certificate "
              "of conformity; petrol, so it moves nothing)"]),
    "V014": (COC + FIG + D + E6D + LP, "2024-04-04", "111", ("lp", "42000.00"), [], ["2027-05-06", "2030-04-05"],
             ["first registered = in Germany under German law on 4 April 2024 (not the United Kingdom registration of "
              "6 May 2026): 1GA(1)(a), 1GE(1)(b), (c) read 'first registered, under this Act or under the law of a "
              "country or territory outside the United Kingdom'"]),
    "V015": (COC + FIG + E6D, "2026-04-30", "150", ("np", "44000.00"), [], ["2027-04-30"], []),
    "V016": (UKAC + FIG, "2025-06-16", "151", ("np", "39500.00"), [acc(1, "2000.00")], ["2026-06-16"],
             ["a UK approval certificate 'indicates the Euro 6d emission standard': ind6d false (not an EU certificate "
              "of conformity; petrol, so it moves nothing)"]),
    "V017": (COC + FIG + E6D + LP, "2025-08-07", "190", ("lp", "39999.99"), [], ["2026-08-07"], []),
    "V018": (COC + FIG + E6D + LP, "2025-12-01", "191", ("lp", "85000.00"), [],
             ["2026-12-01", "2031-11-30", "2031-12-01"], []),
    "V019": (COC + FIG + E6D + LP, "2026-02-14", "255", ("lp", "120000.00"), [], ["2027-02-14"], []),
    "V020": (UKAC + FIG + LP, "2026-02-28", "256", ("lp", "150000.00"), [], ["2028-02-28", "2032-03-01"], []),
    "V021": (COC + FIG + D + TEMP + LP, "2026-06-06", "50", ("lp", "32000.00"), [], ["2027-06-06"], []),
    "V022": (COC + FIG + D + LP, "2025-09-02", "75", ("lp", "41250.00"), [], ["2026-09-02"], []),
    "V023": (UKAC + FIG + D + LP, "2025-11-11", "76", ("lp", "40000.00"), [acc(1, "250.00")], ["2026-11-11"],
             ["a UK approval certificate 'indicates the Euro 6d emission standard': ind6d false (not an EU certificate "
              "of conformity; 1GC(5) needs one in any case)"]),
    "V024": (COC + FIG + D + LP, "2025-05-19", "100", ("lp", "27000.00"), [], ["2026-05-19"], []),
    "V025": (COC + FIG + D + TEMP + LP, "2025-07-25", "101", ("lp", "46000.00"), [], ["2026-07-25"], []),
    "V026": (COC + FIG + D + TEMP + LP, "2026-02-03", "130", ("lp", "39000.00"),
             [acc(1, "1000.00", ["a_nonstd", "a_attached"])], ["2027-02-03"], []),
    "V027": (UKAC + FIG + D, "2025-06-13", "131", ("np", "52000.00"), [], ["2026-06-13"], []),
    "V028": (COC + FIG + D + TEMP + LP, "2025-09-22", "170", ("lp", "38000.00"), [acc(1, "2500.00")], ["2027-03-01"],
             ["first registered = in France under French law on 22 September 2025 (not the United Kingdom "
              "registration of 1 March 2026)"]),
    "V029": (COC + FIG + D + LP, "2026-04-10", "171", ("lp", "55000.00"), [], ["2027-04-10", "2032-04-10"], []),
    "V030": (COC + FIG + D + TEMP + LP, "2025-10-01", "225", ("lp", "64000.00"), [], ["2026-10-01"], []),
    "V031": (COC + FIG + D + TEMP + LP, "2025-12-17", "226", ("lp", "71000.00"), [], ["2026-12-17"], []),
    "V032": (COC + FIG + D + LP, "2026-01-08", "256", ("lp", "90000.00"), [], ["2027-01-08"], []),
    "V033": (COC + FIG + LP, "2017-04-01", "140", ("lp", "45000.00"), [], ["2027-05-04"],
             ["first registered = in Ireland under Irish law on 1 April 2017 (not the United Kingdom registration of "
              "4 May 2026)"]),
    "V034": (COC + FIG + D + E6D + LP, "2025-05-15", "75", ("lp", "38000.00"),
             [acc(1, "3000.00", ["a_nonstd", "a_has_lp"]), acc(2, "1500.00")], ["2027-08-01"],
             ["first registered = in Belgium under Belgian law on 15 May 2025 (not the United Kingdom registration of "
              "1 August 2026)",
              "the towbar attached at the Belgian registration and removed before the United Kingdom registration: not "
              "attached when first registered under the Act (a_attached false)"]),
    "V035": (COC + FIG + E6D + LP + ["taxi"], "2026-03-09", "20", ("lp", "62000.00"), [], ["2027-03-09"], []),
}

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


def _date_in(text):
    m = re.search(r"taking effect on (\d{1,2}) (\w+) (\d{4})", text)
    if not m:
        return None
    return dt.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))).isoformat()


def _build():
    cases, probes, probe_qids = [], {}, {}
    for c in ENC:
        cid = c["id"]
        if c["scope"] == "out":
            probes[cid] = "out-of-scope probe (questions-enc.jsonl scope 'out')"
            probe_qids[cid] = [q["qid"] for q in c["questions"]]
            continue
        facts, dreg, co2, (pk, price), accs, lics, judgement = V[cid]
        ints = {"dreg": dreg, pk: price}
        if co2 is not None:
            ints["co2"] = co2
        lic_ids = {d: f"v1l{i}" for i, d in enumerate(lics, 1)}
        veh = {"id": "v1", "facts": list(facts), "ints": ints,
               "accessories": [{"id": f"v1a{a['n']}", "facts": a["facts"], "ints": a["ints"]} for a in accs],
               "licences": [{"id": i, "date": d} for d, i in lic_ids.items()]}
        qs = []
        for q in c["questions"]:
            if q["kind"] == "Q1":
                qs.append({"qid": q["qid"], "item": "v1", "vehicle": "v1", "form": "rate1"})
                continue
            d = _date_in(q["text"])
            if d not in lic_ids:
                raise SystemExit(f"{q['qid']}: licence date {d} not in the case's licences")
            qs.append({"qid": q["qid"], "item": lic_ids[d], "vehicle": "v1",
                       "form": "rate2" if q["kind"] == "Q2" else "ge2"})
        cases.append({"id": cid, "vehicles": [veh], "questions": qs, "judgement": list(judgement)})
    return cases, probes, probe_qids


CASES, PROBES, PROBE_QIDS = _build()
UNSUPPORTED = {}  # no in-scope question is outside what the translation carries (decided per question, none found)
# The six-year bridge's input (copied from the facts: the first registration date, each licence's date).
BRIDGE_INPUTS = [{"case": c["id"], "licence": l["id"], "registered": c["vehicles"][0]["ints"]["dreg"], "date": l["date"]}
                 for c in CASES for l in c["vehicles"][0]["licences"]]
