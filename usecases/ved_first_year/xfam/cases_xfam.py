"""CROSS-FAMILY encoder records for ved-first-year (the Codex-written set, questions-enc.jsonl ONLY; sha256 checked at import).

Encoder: a fresh Opus 5.5 session (row statute-corpus-xfam-answer5-1124). The translation (translation.py), the encoder
conventions (encode.py C1-C5), the runner (run.py) and the bridge (bridge/years.py) are FROZEN: this file only states each
case's facts in their vocabulary. Never write an answer, a rate, a total, a band or a duration here.

Record format (fill V, Q and JUDGEMENT; leave the code below them unchanged):
- V: case id -> list of vehicles, in the order the facts name them. A vehicle is veh(owner, facts, dreg, co2, price,
  accessories), where
    owner        the name the questions use ("Alice" for "Alice's car");
    facts        the unary facts of translation.V_FACTS true of the vehicle (encode.py C1: every other one is false);
    dreg         "YYYY-MM-DD": the day the vehicle was first registered, in the sense of translation.V_UNITS["dreg"];
    co2          the stated applicable CO2 emissions figure in g/km as a string, or None where none is stated;
    price        ("lp", "<amount>") for a stated list price or ("np", "<amount>") for a stated notional price, the
                 amount as stated without "GBP" or commas (e.g. "50000.01");
    accessories  [acc(n, "<amount>", facts)] per accessory the facts name (n = 1, 2, ... within the vehicle; facts from
                 translation.A_FACTS: true ones only; the amount is its stated list price (if "a_has_lp" is true) or its
                 stated notional price).
- Q: qid -> (owner, None) for a Q1 question (the first vehicle licence), or (owner, "YYYY-MM-DD") for a Q2 / Q3 question
  (the licence taking effect on that date, as the question names it). The form follows the kind: Q1 -> rate1 (the vehicle),
  Q2 -> rate2, Q3 -> ge2 (the licence item). Every in-scope qid is in Q or in UNSUPPORTED.
- UNSUPPORTED: case id -> (reason, [qids]) for in-scope questions the vocabulary cannot state (leave them out of Q).
- JUDGEMENT: case id -> [one short line per reading beyond copying a stated fact].
Out-of-scope cases (scope "out") need nothing: they become PROBES (every answer UNSUPPORTED).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "2e5541f390010b1b2580888a82318e74eb09a3aa70731626891f360ffb83b1b0"
_P = HERE / "questions-enc.jsonl"
if not _P.exists():
    _P = HERE.parent / "questions-enc.jsonl"
_RAW = _P.read_bytes()
if hashlib.sha256(_RAW).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")
ENC = [json.loads(l) for l in _RAW.decode().splitlines() if l.strip()]


def veh(owner, facts, dreg, co2, price, accessories=()):
    return {"owner": owner, "facts": list(facts), "dreg": dreg, "co2": co2, "price": tuple(price),
            "accessories": list(accessories)}


def acc(n, price, facts):
    key = "alp" if "a_has_lp" in facts else "anp"
    return {"n": n, "facts": list(facts), "ints": {key: price}}


V = {
    "V001": [
        veh("Alice", ["basis_coc", "cert_lpv", "zero_rate", "has_lp"], "2025-04-01", None, ("lp", "50000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "zero_rate", "diesel", "has_lp"], "2025-04-01", None, ("lp", "50000.01"), []),
    ],
    "V002": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "1", ("lp", "40000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "1", ("lp", "40000.01"), []),
    ],
    "V003": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "49", ("lp", "39999.99"), [acc(1, "0.02", ["a_nonstd", "a_attached", "a_has_lp"])]),
        veh("Ben", ["basis_ukac", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "49", ("lp", "39900"), [acc(1, "100.01", ["a_nonstd", "a_attached"])]),
    ],
    "V004": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2"], "2025-04-01", "50", ("np", "40000"), [acc(1, "1000", ["a_nonstd", "a_attached", "a_has_lp"])]),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp"], "2025-04-01", "50", ("np", "40000.01"), [acc(1, "2000", ["a_nonstd", "a_attached"])]),
    ],
    "V005": [
        veh("Alice", ["basis_ukac", "cert_lpv", "cert_co2", "has_lp", "taxi"], "2025-04-01", "51", ("lp", "45000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "51", ("lp", "30000"), []),
    ],
    "V006": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2020-11-02", "74", ("lp", "45000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "74", ("lp", "30000"), []),
    ],
    "V007": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2020-11-01", "75", ("lp", "45000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "75", ("lp", "30000"), []),
    ],
    "V008": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2020-10-31", "76", ("lp", "45000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "76", ("lp", "30000"), []),
    ],
    "V009": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "89", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "89", ("lp", "30000"), []),
        veh("Cara", ["basis_ukac", "cert_lpv", "zero_rate", "has_lp"], "2025-03-31", None, ("lp", "50000.01"), []),
    ],
    "V010": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "90", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "90", ("lp", "30000"), []),
        veh("Cara", ["basis_coc", "cert_lpv", "cert_co2", "zero_rate", "has_lp"], "2025-04-01", None, ("lp", "50000"), [acc(1, "0.01", ["a_nonstd", "a_attached", "a_has_lp"])]),
    ],
    "V011": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "91", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "91", ("lp", "30000"), []),
        veh("Cara", ["basis_coc", "cert_lpv", "cert_co2", "zero_rate"], "2025-04-02", None, ("np", "50000.01"), []),
    ],
    "V012": [
        veh("Alice", ["basis_ukac", "cert_lpv", "cert_co2", "has_lp"], "2017-04-01", "99", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "99", ("lp", "30000"), []),
    ],
    "V013": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "100", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "100", ("lp", "30000"), []),
    ],
    "V014": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "101", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "101", ("lp", "30000"), []),
    ],
    "V015": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "109", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "109", ("lp", "30000"), []),
    ],
    "V016": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "110", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "110", ("lp", "30000"), []),
    ],
    "V017": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "111", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "111", ("lp", "30000"), []),
    ],
    "V018": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "129", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "129", ("lp", "30000"), []),
    ],
    "V019": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "130", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "130", ("lp", "30000"), []),
    ],
    "V020": [
        veh("Alice", ["basis_ukac", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "131", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "131", ("lp", "30000"), []),
    ],
    "V021": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "149", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "149", ("lp", "30000"), []),
    ],
    "V022": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "150", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "150", ("lp", "30000"), []),
    ],
    "V023": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "151", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "151", ("lp", "30000"), []),
    ],
    "V024": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "169", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "169", ("lp", "30000"), []),
    ],
    "V025": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "170", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "170", ("lp", "30000"), []),
    ],
    "V026": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "171", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "171", ("lp", "30000"), []),
    ],
    "V027": [
        veh("Alice", ["basis_ukac", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "189", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "189", ("lp", "30000"), []),
    ],
    "V028": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "190", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "190", ("lp", "30000"), []),
    ],
    "V029": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "191", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "191", ("lp", "30000"), []),
    ],
    "V030": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "224", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "224", ("lp", "30000"), []),
    ],
    "V031": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "225", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "225", ("lp", "30000"), []),
    ],
    "V032": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "226", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "226", ("lp", "30000"), []),
    ],
    "V033": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "254", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "254", ("lp", "30000"), []),
    ],
    "V034": [
        veh("Alice", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6d", "has_lp"], "2025-04-01", "255", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "ind6dtemp", "has_lp"], "2025-04-01", "255", ("lp", "30000"), []),
    ],
    "V035": [
        veh("Alice", ["basis_ukac", "cert_lpv", "cert_co2", "has_lp"], "2025-04-01", "256", ("lp", "30000"), []),
        veh("Ben", ["basis_coc", "cert_lpv", "cert_co2", "diesel", "has_lp"], "2025-04-01", "256", ("lp", "30000"), []),
    ],
}

Q = {
    "V001-1": ("Alice", None),
    "V001-2": ("Ben", None),
    "V001-3": ("Alice", "2026-04-01"),
    "V001-4": ("Alice", "2026-04-01"),
    "V001-5": ("Ben", "2026-04-01"),
    "V001-6": ("Ben", "2026-04-01"),
    "V002-1": ("Alice", None),
    "V002-2": ("Ben", None),
    "V002-3": ("Alice", "2026-04-01"),
    "V002-4": ("Alice", "2026-04-01"),
    "V002-5": ("Ben", "2026-04-01"),
    "V002-6": ("Ben", "2026-04-01"),
    "V003-1": ("Alice", None),
    "V003-2": ("Ben", None),
    "V003-3": ("Alice", "2026-04-01"),
    "V003-4": ("Alice", "2026-04-01"),
    "V003-5": ("Ben", "2026-05-01"),
    "V003-6": ("Ben", "2026-05-01"),
    "V004-1": ("Alice", None),
    "V004-2": ("Ben", None),
    "V004-3": ("Alice", "2026-04-01"),
    "V004-4": ("Alice", "2026-04-01"),
    "V004-5": ("Ben", "2026-04-01"),
    "V004-6": ("Ben", "2026-04-01"),
    "V005-1": ("Alice", None),
    "V005-2": ("Ben", None),
    "V005-3": ("Alice", "2026-05-01"),
    "V005-4": ("Alice", "2026-05-01"),
    "V006-1": ("Alice", None),
    "V006-2": ("Ben", None),
    "V006-3": ("Alice", "2026-11-01"),
    "V006-4": ("Alice", "2026-11-01"),
    "V007-1": ("Alice", None),
    "V007-2": ("Ben", None),
    "V007-3": ("Alice", "2026-11-01"),
    "V007-4": ("Alice", "2026-11-01"),
    "V008-1": ("Alice", None),
    "V008-2": ("Ben", None),
    "V008-3": ("Alice", "2026-11-01"),
    "V008-4": ("Alice", "2026-11-01"),
    "V009-1": ("Alice", None),
    "V009-2": ("Ben", None),
    "V009-3": ("Cara", "2026-04-01"),
    "V009-4": ("Cara", "2026-04-01"),
    "V010-1": ("Alice", None),
    "V010-2": ("Ben", None),
    "V010-3": ("Cara", "2026-04-01"),
    "V010-4": ("Cara", "2026-04-01"),
    "V011-1": ("Alice", None),
    "V011-2": ("Ben", None),
    "V011-3": ("Cara", "2026-04-02"),
    "V011-4": ("Cara", "2026-04-02"),
    "V012-1": ("Alice", None),
    "V012-2": ("Ben", None),
    "V013-1": ("Alice", None),
    "V013-2": ("Ben", None),
    "V014-1": ("Alice", None),
    "V014-2": ("Ben", None),
    "V015-1": ("Alice", None),
    "V015-2": ("Ben", None),
    "V016-1": ("Alice", None),
    "V016-2": ("Ben", None),
    "V017-1": ("Alice", None),
    "V017-2": ("Ben", None),
    "V018-1": ("Alice", None),
    "V018-2": ("Ben", None),
    "V019-1": ("Alice", None),
    "V019-2": ("Ben", None),
    "V020-1": ("Alice", None),
    "V020-2": ("Ben", None),
    "V021-1": ("Alice", None),
    "V021-2": ("Ben", None),
    "V022-1": ("Alice", None),
    "V022-2": ("Ben", None),
    "V023-1": ("Alice", None),
    "V023-2": ("Ben", None),
    "V024-1": ("Alice", None),
    "V024-2": ("Ben", None),
    "V025-1": ("Alice", None),
    "V025-2": ("Ben", None),
    "V026-1": ("Alice", None),
    "V026-2": ("Ben", None),
    "V027-1": ("Alice", None),
    "V027-2": ("Ben", None),
    "V028-1": ("Alice", None),
    "V028-2": ("Ben", None),
    "V029-1": ("Alice", None),
    "V029-2": ("Ben", None),
    "V030-1": ("Alice", None),
    "V030-2": ("Ben", None),
    "V031-1": ("Alice", None),
    "V031-2": ("Ben", None),
    "V032-1": ("Alice", None),
    "V032-2": ("Ben", None),
    "V033-1": ("Alice", None),
    "V033-2": ("Ben", None),
    "V034-1": ("Alice", None),
    "V034-2": ("Ben", None),
    "V035-1": ("Alice", None),
    "V035-2": ("Ben", None),
}

UNSUPPORTED = {
}

JUDGEMENT = {
    "V001": ["Ben: certificate specifies a CO2 figure but the facts state none (only a zero rate of emissions); co2 left unstated, not typed as 0"],
    "V003": ["Ben: first registered under the law of Germany on 1 April 2025 before UK registration; dreg = that foreign date (V_UNITS dreg, 1GA(1)(a)); basis = the certificate stated for it", "Ben: UK approval certificate indicating a Euro 6d standard: not an EU certificate of conformity, so ind6d/ind6dtemp false"],
    "V005": ["Alice: first registered under the law of France on 1 April 2025 before UK registration; dreg = that foreign date (V_UNITS dreg, 1GA(1)(a)); basis = the certificate stated for it"],
    "V010": ["Cara: certificate specifies a CO2 figure but the facts state none (only a zero rate of emissions); co2 left unstated, not typed as 0"],
    "V011": ["Cara: certificate specifies a CO2 figure but the facts state none (only a zero rate of emissions); co2 left unstated, not typed as 0"],
}


# --- below: the record builder (unchanged by the encoder) -----------------------------------------------------------

def _build():
    cases, probes, probe_qids = [], {}, {}
    unsup = {q for _, qs in UNSUPPORTED.values() for q in qs}
    for c in ENC:
        cid = c["id"]
        if c["scope"] == "out":
            probes[cid] = "out-of-scope probe (questions-enc.jsonl scope 'out')"
            probe_qids[cid] = [q["qid"] for q in c["questions"]]
            continue
        vehicles, by_owner, lic_ids = [], {}, {}
        for i, v in enumerate(V.get(cid, []), 1):
            vid = f"v{i}"
            by_owner[v["owner"]] = vid
            pk, price = v["price"]
            ints = {"dreg": v["dreg"], pk: price}
            if v["co2"] is not None:
                ints["co2"] = v["co2"]
            dates = sorted({d for q, (o, d) in Q.items() if q.startswith(cid + "-") and o == v["owner"] and d})
            lic_ids.update({(v["owner"], d): f"{vid}l{j}" for j, d in enumerate(dates, 1)})
            vehicles.append({"id": vid, "facts": list(v["facts"]), "ints": ints,
                             "accessories": [{"id": f"{vid}a{a['n']}", "facts": a["facts"], "ints": a["ints"]}
                                             for a in v["accessories"]],
                             "licences": [{"id": lic_ids[(v["owner"], d)], "date": d} for d in dates]})
        qs = []
        for q in c["questions"]:
            if q["qid"] in unsup or q["qid"] not in Q or Q[q["qid"]][0] not in by_owner:
                continue  # check.py reports a qid missing from both Q and UNSUPPORTED, or an unknown owner
            owner, d = Q[q["qid"]]
            vid = by_owner[owner]
            if q["kind"] != "Q1" and (owner, d) not in lic_ids:
                continue  # check.py reports a Q2/Q3 without its date
            if q["kind"] == "Q1":
                qs.append({"qid": q["qid"], "item": vid, "vehicle": vid, "form": "rate1"})
            else:
                qs.append({"qid": q["qid"], "item": lic_ids[(owner, d)], "vehicle": vid,
                           "form": "rate2" if q["kind"] == "Q2" else "ge2"})
        if qs:
            cases.append({"id": cid, "vehicles": vehicles, "questions": qs, "judgement": list(JUDGEMENT.get(cid, []))})
    return cases, probes, probe_qids


CASES, PROBES, PROBE_QIDS = _build()
# The six-year bridge's input (copied from the records: the first registration date, each licence's date).
BRIDGE_INPUTS = [{"case": c["id"], "licence": l["id"], "registered": v["ints"]["dreg"], "date": l["date"]}
                 for c in CASES for v in c["vehicles"] for l in v["licences"]]
