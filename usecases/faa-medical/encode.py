"""14 CFR 61.23: turn the encoder's records (cases.py) into VE facts. Mechanical; every reading is in cases.py.

Bridges come only from bridge/bridges.jsonl (the tested script's output on the dates cases.py transcribes; checked by
hash). Every fact predicate gets a literal (true or false), except those the record lists as unknown, so negative steps can
be proved (closed facts, as law 1 and release B).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import translation as T

R = T.R
HERE = Path(__file__).resolve().parent


def load_bridges(sha):
    p = HERE / "bridge" / "bridges.jsonl"
    if not p.exists():
        return {}
    raw = p.read_bytes()
    if sha and hashlib.sha256(raw).hexdigest() != sha:
        raise SystemExit("bridge/bridges.jsonl differs from the sealed bridges.jsonl")
    return {d["id"]: d for d in (json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip())}


_BRIDGES = {}


def bridges():
    if not _BRIDGES:
        import cases as K
        _BRIDGES.update(load_bridges(K.BRIDGES_SHA256))
    return _BRIDGES


def records(case):
    return sorted(case.get("certs", {})), sorted(case.get("apps", {}))


def candidate_days(case):
    b = bridges()[case["id"]]
    days = set()
    for rec in b["certs"].values():
        days |= {rec[f"end{n}"] for n in (6, 12, 24, 60)}
    for k in ("course_end24", "basic_exam_end48"):
        if k in b:
            days.add(b[k])
    return sorted(days)


def facts(case):
    """[{"id", "formula"}] and the list of unknown facts left out."""
    out = []
    unknown = set(case.get("unknown", []))
    true = set(case.get("true", []))
    bad = (true | unknown) - set(R.FACTS)
    if bad:
        raise ValueError(f"{case['id']}: not fact names: {sorted(bad)}")
    b = bridges()[case["id"]]

    def lit(fid, value, f):
        out.append({"id": fid, "formula": f if value else R.Not(f)})

    def eq(fid, const, iso):
        out.append({"id": fid, "formula": ["eq", R.ci(const), R.day(iso)]})

    for name in R.FACTS:
        if name not in unknown:
            lit(f"pilot.{name}", name in true, R.u(name))
    eq("flight_day", "flight_day", b["flight_day"])
    if "sixtieth" in b:
        eq("sixtieth", "sixtieth", b["sixtieth"])
    for k, rec in sorted(case.get("certs", {}).items()):
        br = b["certs"][k]
        cls = rec["class"]
        lit(f"{k}.first_class", cls == 1, R.U("first_class", k))
        lit(f"{k}.second_class", cls == 2, R.U("second_class", k))
        lit(f"{k}.third_class", cls == 3, R.U("third_class", k))
        if rec.get("suspended") is not None:
            lit(f"{k}.suspended_or_revoked", rec["suspended"], R.U("suspended_or_revoked", k))
        if "under40_exam" in br:
            lit(f"{k}.under40_exam", br["under40_exam"], R.U("under40_exam", k))
        lit(f"{k}.after_2006", br["after_2006"], R.U("after_2006", k))
        eq(f"{k}.exam", f"{k}_exam", br["exam"])
        for n in (6, 12, 24, 60):
            eq(f"{k}.end{n}", f"{k}_end{n}", br[f"end{n}"])
    later = {tuple(x) for x in b["later"]}
    certs = sorted(case.get("certs", {}))
    for x in certs:
        for y in certs:
            if x != y:
                lit(f"{x}.later.{y}", (x, y) in later, R.B("later", x, y))
    for k, rec in sorted(case.get("apps", {}).items()):
        if rec.get("eligible") is not None:
            lit(f"{k}.app_eligible", rec["eligible"], R.U("app_eligible", k))
        if rec.get("denied") is not None:
            lit(f"{k}.app_denied", rec["denied"], R.U("app_denied", k))
    app_later = {tuple(x) for x in b["app_later"]}
    apps = sorted(case.get("apps", {}))
    for x in apps:
        for y in apps:
            if x != y:
                lit(f"{x}.app_later.{y}", (x, y) in app_later, R.B("app_later", x, y))
    for k in ("course_day", "course_end24", "basic_exam_day", "basic_exam_end48"):
        if k in b:
            eq(k, k, b[k])
    unknown_out = [f"pilot.{u}" for u in sorted(unknown)]
    for k, rec in sorted(case.get("certs", {}).items()):
        if rec.get("suspended") is None:
            unknown_out.append(f"{k}.suspended_or_revoked")
        if "under40_exam" not in b["certs"][k]:
            unknown_out.append(f"{k}.under40_exam")
    return out, unknown_out


def dates_line(case, facts_text):
    """The bridge script's input line for a case (the stated dates, transcribed; the script checks each is stated)."""
    d = dict(case["dates"])
    return {"id": case["id"], "facts": facts_text, **d}
