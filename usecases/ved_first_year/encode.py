"""The encoder's facts for one case (cases.py). SAME-FAMILY. Written with the translation, BEFORE questions-enc.jsonl was
opened; cases.py (the per-case records) after.

Conventions (stated, the same for every case):
C1 closed world over translation.V_FACTS / A_FACTS: a fact the case record does not list as true is stated false; the
   encoder lists every true fact it reads in the question's facts;
C2 constants only where the question gives them: the first registration date, the applicable CO2 emissions figure (Part 1A
   out: stated; never typed when the certificate specifies no figure: then 1GA(1C) decides it or nothing does), the list
   price or the notional price, each accessory's list or notional price, each licence's date; the whole years and days from
   the first registration to a licence's date come only from bridge/bridges.jsonl (never typed by the encoder);
C3 "propelled by diesel" and the standard the certificate indicates are copied as stated (fixed facts of the test); a
   certificate indicating Euro 6d-TEMP is not one indicating Euro 6d (ind6d false, ind6dtemp true), as the text's own
   parenthesis in 1GC(5) says;
C4 an accessory the facts name as non-standard and attached when the vehicle was first registered under the Act is listed
   with those facts; an accessory fitted later, or standard, is listed with them false (it then counts GBP 0);
C5 a licence the facts call the first vehicle licence is asked as Q1 (rate1); any other licence is an item of its own with
   its date (Q2 rate2, Q3 ge2).
C6 (latent-ved-1125, translation R7) `mcaravan` (1GA(2A): the certificate identifies the vehicle as a motor caravan) is a
   fact the frozen encoders never had. For a case of a frozen encoder file it comes ONLY from the fresh encoder seat's
   record latent-enc/mcaravan.json (a frozen case = id V001-V043; matched by the case's id and the sha256 of its encoded
   vehicles, so an edited case falls out): true -> stated true; false -> stated false (C1: no sentence bears on it); null, or a frozen case or
   vehicle the record does not hold -> UNKNOWN (a missing record file stops the run): no fact either way, so for a vehicle first registered on or after
   12 March 2020 `mc_excl`, `applies` and every rate stay open (VE refuses). Any other case (smoke, tests) states it like
   every other fact, or lists it under "unknown" (the only fact that may be left unknown).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import translation as T

HERE = Path(__file__).resolve().parent
UNKNOWN_OK = ("mcaravan",)  # C6: the only fact a case may leave unknown


def literal(name, value):
    base = name.rsplit("_", 1)[0]
    unit = T.ALL_UNITS[base][0]
    term = ["const", unit, name]
    if unit == T.DAY:
        return ["eq", term, ["date", value]]
    return ["eq", term, ["decimal", unit, str(value)]]


def bridges():
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[(r["case"], r["licence"])] = (r["years"], r["days"])
    return out


def ctx_of(case):
    return T.Ctx([{"id": v["id"], "accessories": [a["id"] for a in v.get("accessories", ())],
                   "licences": [l["id"] for l in v.get("licences", ())]} for v in case["vehicles"]])


def _unary(out, item, mine, table, unknown=()):
    bad = set(mine) - set(table)
    if bad:
        raise ValueError(f"{item}: unknown facts {sorted(bad)}")
    bad = (set(unknown) - set(UNKNOWN_OK)) | (set(unknown) & set(mine))
    if bad:
        raise ValueError(f"{item}: facts that may not be left unknown, or stated and unknown: {sorted(bad)}")
    for p in table:
        if p in unknown:
            continue
        f = T.U(p, item)
        out.append({"id": f"{item}.{p}", "formula": f if p in mine else ["not", f]})


def vehicles_sha256(case):
    """The fingerprint C6 matches a frozen case by (its id and its encoded vehicles)."""
    text = json.dumps(case["vehicles"], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def _mcaravan_record():
    p = HERE / "latent-enc" / "mcaravan.json"
    if not p.exists():
        return None  # a frozen case then raises (review finding: never refuse silently)
    return json.loads(p.read_text(encoding="utf-8"))["cases"]


MCARAVAN = _mcaravan_record()  # (case id + "/" + vehicles sha256) -> {vehicle id: true | false | null}


def frozen_case(case):
    """C6: a case of a frozen encoder file (cases.py, xfam/cases_xfam.py: ids V001-V043); smoke and test cases use other
    ids. Its mcaravan comes from the record only; a missing record leaves it unknown."""
    return re.fullmatch(r"V0(0[1-9]|[1-3]\d|4[0-3])", case["id"]) is not None


def _mcaravan_of(case, v):
    """C6 -> (stated true?, unknown?) for vehicle v."""
    if not frozen_case(case):
        return "mcaravan" in v.get("facts", ()), "mcaravan" in v.get("unknown", ())
    if "mcaravan" in v.get("facts", ()) or v.get("unknown"):
        raise ValueError(f"{case['id']}: a frozen case states mcaravan itself")
    if MCARAVAN is None:
        raise SystemExit("latent-enc/mcaravan.json is missing: the frozen cases have no motor-caravan record (C6)")
    got = MCARAVAN.get(case["id"] + "/" + vehicles_sha256(case), {}).get(v["id"])
    return got is True, got is None


def facts(case):
    out = []
    br = bridges()
    for v in case["vehicles"]:
        x = v["id"]
        mc, mc_unknown = _mcaravan_of(case, v)
        mine = [f for f in v.get("facts", ()) if f != "mcaravan"] + (["mcaravan"] if mc else [])
        unknown = [f for f in v.get("unknown", ()) if f != "mcaravan"] + (["mcaravan"] if mc_unknown else [])
        _unary(out, x, mine, T.V_FACTS, unknown)
        for base, value in sorted(v.get("ints", {}).items()):
            if base not in T.V_UNITS or base in T.ASKED_BASES:
                raise ValueError(f"{case['id']}: {base} is not a stated vehicle constant")
            out.append({"id": f"{base}_{x}", "formula": literal(f"{base}_{x}", value)})
        for a in v.get("accessories", ()):
            _unary(out, a["id"], a.get("facts", ()), T.A_FACTS)
            for base, value in sorted(a.get("ints", {}).items()):
                if base not in ("alp", "anp"):
                    raise ValueError(f"{case['id']}: {base} is not a stated accessory constant")
                out.append({"id": f"{base}_{a['id']}", "formula": literal(f"{base}_{a['id']}", value)})
        for l in v.get("licences", ()):
            out.append({"id": f"dlic_{l['id']}", "formula": literal(f"dlic_{l['id']}", l["date"])})
            b = br.get((case["id"], l["id"]))
            if b is not None:
                out.append({"id": f"ly_{l['id']}", "formula": literal(f"ly_{l['id']}", b[0])})
                out.append({"id": f"ld_{l['id']}", "formula": literal(f"ld_{l['id']}", b[1])})
    return out
