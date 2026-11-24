"""PAWHP: turn the encoder's records (cases.py) into VE facts. Mechanical; every reading is in cases.py.

Bridges come only from bridge/bridges.jsonl (checked by hash). Every fact predicate gets a literal (true or false) for
every person, except those the record lists as unknown, so negative steps can be proved (closed facts, as release B).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import translation as T

R = T.R
HERE = Path(__file__).resolve().parent
BRIDGES_SHA256 = "1b6c2939098c77d2bb257fbb7650fee0268aec071c336a56332fc5227f04275c"
EPOCH_MIN = "1970-01-01"


def load_bridges():
    raw = (HERE / "bridge" / "bridges.jsonl").read_bytes()
    if hashlib.sha256(raw).hexdigest() != BRIDGES_SHA256:
        raise SystemExit("bridge/bridges.jsonl differs from the sealed bridges.jsonl")
    out = {}
    for line in raw.decode("utf-8").splitlines():
        d = json.loads(line)
        if "id" in d:
            out[d["id"]] = d["births"]
    return out


BRIDGES = load_bridges()

UNKNOWN_GROUPS = {
    "rb": ["benefit_day", "benefit_throughout", "own_rb_throughout"],
    "pic": ["not_pic_some_day", "pic_by_last_day", "bii_possible"],
    "fipt": ["ever_fipt", "remains_fipt"],
    "custody": ["custody_throughout_qw"],
    "wfp": ["wfp_awarded", "wfp_award_in_error"],
    "paid": ["paid_for_qw"],
}
PAIR_PREDS = ("married_or_cp", "same_household", "living_as_married", "share_mutual_home")


def clamp(iso):
    return EPOCH_MIN if iso is None or iso < EPOCH_MIN else iso


def bridge(case_id, person):
    b = BRIDGES[case_id][person["b"]]
    pa = b["pa_date"]
    pa_date = pa[0] if len(pa) == 1 else pa[{"F": 0, "M": 1}[person["sex"]]]
    return b, pa_date


ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def fipt_facts(c, p, unknown, put, out):
    """Free in-patient treatment (row statute-xfam-wrong-pawhp-1): the encoder states only the stay's dates,
    "fipt": [<day entered>, <day left> | None (not left)], for a stay that is free in-patient treatment (SI 2005/3360
    reg. 2(4); convention C6). fipt_throughout_qw and fipt_52w_before are derived from these dates by translation.fipt_rules
    in the checker (reg. 2(5): the period begins the day after entry); stating them is refused. More than one stay is out
    of scope (no linking rule is imported) and refused."""
    for legacy in ("fipt_throughout_qw", "fipt_52w_before"):
        if legacy in p:
            raise SystemExit(f"{c}: '{legacy}' is derived from the stay dates; state 'fipt': [entered, left|None]")
    stay = p.get("fipt")
    if stay is not None and not (type(stay) in (list, tuple) and len(stay) == 2 and type(stay[0]) is str
                                 and ISO.fullmatch(stay[0]) and (stay[1] is None or (type(stay[1]) is str
                                                                                    and ISO.fullmatch(stay[1])))):
        raise SystemExit(f"{c}: 'fipt' must be one stay [entered, left|None] (more than one stay is out of scope): {stay!r}")
    if stay is not None and stay[1] is not None and stay[1] < stay[0]:
        raise SystemExit(f"{c}: 'fipt' leaves before it enters: {stay!r}")
    put("ever_fipt", stay is not None)
    if stay is None or "ever_fipt" in unknown:
        return
    put("remains_fipt", stay[1] is None)
    out.append({"id": f"{c}.fipt_entry", "formula": ["eq", ["const", "day", f"{c}_fipt_entry"], R.day(clamp(stay[0]))]})
    if stay[1] is not None:
        out.append({"id": f"{c}.fipt_left", "formula": ["eq", ["const", "day", f"{c}_fipt_left"], R.day(stay[1])]})


def facts(case):
    """[{"id", "formula"}] and the list of unknown facts left out."""
    out, unknown_out = [], []
    people = case["people"]

    def lit(fid, value, f):
        out.append({"id": fid, "formula": f if value else R.Not(f)})

    for p in people:
        c = p["c"]
        unknown = set()
        for u in p.get("unknown", []):
            unknown |= set(UNKNOWN_GROUPS.get(u, [u]))
        unknown_out += [f"{c}.{u}" for u in sorted(unknown)]

        def put(pred, value):
            if pred not in unknown:
                lit(f"{c}.{pred}", value, R.U(pred, c))
        rb = p.get("rb", {})
        if "benefit_day" not in unknown:
            for b in T.BENEFITS:
                lit(f"{c}.benefit_day.{b}", b in rb, R.B("benefit_day", c, b))
                lit(f"{c}.benefit_throughout.{b}", rb.get(b) == "throughout", R.B("benefit_throughout", c, b))
        put("own_rb_throughout", any(v == "throughout" for v in rb.values()))
        if "each_day" in p or "rb_each_day_with_member" not in unknown:
            put("rb_each_day_with_member", p.get("each_day", any(v == "throughout" for v in rb.values())))
        put("not_pic_some_day", p.get("not_pic_some_day", True))
        put("pic_by_last_day", p.get("pic_by_last_day", False))
        put("bii_possible", p.get("bii_possible", False))
        put("wfp_awarded", p.get("wfp", False))
        put("wfp_award_in_error", p.get("wfp_award_in_error", False))
        fipt_facts(c, p, unknown, put, out)
        put("custody_throughout_qw", p.get("custody_throughout_qw", False))
        put("paid_for_qw", p.get("paid", False))
        put("married_to_several", p.get("married_to_several", False))
        put("rb_by_later_decision", p.get("rb_by_later_decision", False))
        if c == "applicant":
            if p["b"] is not None:
                b, pa_date = bridge(case["id"], p)
                out.append({"id": "applicant.pa_date", "formula": ["eq", R.ci("applicant_pa_date"), R.day(clamp(pa_date))]})
                out.append({"id": "applicant.eightieth", "formula": ["eq", R.ci("applicant_eightieth"),
                                                                     R.day(clamp(b["eightieth"]))]})
            put("ever_resident_scot", True)
            out.append({"id": "applicant.scot_from", "formula": ["eq", R.ci("applicant_scot_from"),
                                                                 R.day(clamp(p.get("scot_from")))]})
            put("remains_resident_scot", p.get("scot_last_day") is None)
            if p.get("scot_last_day"):
                out.append({"id": "applicant.scot_last_day", "formula": ["eq", R.ci("applicant_scot_last_day"),
                                                                         R.day(p["scot_last_day"])]})
            care = p.get("care")
            put("ever_in_care", care is not None)
            if care:
                out.append({"id": "applicant.care_from", "formula": ["eq", R.ci("applicant_care_from"), R.day(clamp(care[0]))]})
                put("remains_in_care", care[1] is None)
                if care[1]:
                    out.append({"id": "applicant.care_last_day", "formula": ["eq", R.ci("applicant_care_last_day"),
                                                                             R.day(care[1])]})
            put("applied", p.get("received") is not None)
            if p.get("received"):
                out.append({"id": "applicant.received", "formula": ["eq", R.ci("applicant_received"), R.day(p["received"])]})
            put("opt_out_before_payment", p.get("opt_out_before_payment", False))
            put("opt_in_before_payment", p.get("opt_in_before_payment", False))
            put("opt_in_made", p.get("opt_in_made", False))
            put("opt_in_future_only", p.get("opt_in_future_only", False))
            if p.get("opt_in_day"):
                out.append({"id": "applicant.opt_in_day", "formula": ["eq", R.ci("applicant_opt_in_day"), R.day(p["opt_in_day"])]})
            put("s115_ceased_by_later_decision", p.get("s115_ceased_by_later_decision", False))
        else:
            if p["b"] is not None:
                b, _ = bridge(case["id"], p)
                put("reached_pa", b["reached_pa_by_week_end"])
                put("reached_80", b["reached_80_by_week_end"])
            put("meets_8_2a", p.get("meets_8_2a", True))
            put("in_residential_care", p.get("in_residential_care", False))
    stated = {}
    for a, b, preds in case.get("pairs", []):
        for pred in preds:
            stated[(a, b, pred)] = stated[(b, a, pred)] = True
    for p in people:
        for o in people:
            if p["c"] == o["c"]:
                continue
            for pred in PAIR_PREDS:
                lit(f"{p['c']}.{pred}.{o['c']}", stated.get((p["c"], o["c"], pred), False), R.B(pred, p["c"], o["c"]))
    for m in case.get("marriages", []):
        lit(f"{m['c']}.under_polygamy_law", m["polygamy_law"], ["unary", "under_polygamy_law", R.c(m["c"])])
        for p in people:
            lit(f"{p['c']}.member_of.{m['c']}", p["c"] in m["members"], ["binary", "member_of", R.c(p["c"]), R.c(m["c"])])
    return out, unknown_out
