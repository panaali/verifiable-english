#!/usr/bin/env python3
"""JT-0p items 1 and 3 and the descriptive forecast (docs/research/judgment-terms-phase1.md, 1.3.4 to 1.3.6 and 1.4).

    python3 research/judgment-terms/measure.py instrument   # instrument-{udhr,udhr-jt0p,constitution}.json
    python3 research/judgment-terms/measure.py scan         # integrity-scan.json (hits, before the hand reading)
    python3 research/judgment-terms/measure.py integrity    # integrity.json (hits merged with integrity_verdicts.tsv)
    python3 research/judgment-terms/measure.py forecast     # admission-forecast.json
    python3 research/judgment-terms/measure.py reproduce    # reproduction.json (P2 to P9; P1 is jt0p.py's)

Reads the pinned pilot runs (read only), the JT-0p ledger copy in run-jt0p/ and the hand class table
open_term_class.tsv. Standard library only; no checker call, no model call. Lean owns admission: the forecast only
reads the records and says which of the plan's checks 1 to 5 would fire.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVIDENCE = ROOT / "docs/research/evidence/judgment-terms"
PILOTS = Path("/home/seyran/code/manage-agents/pilots")
UDHR_RUN = PILOTS / "udhr/run-20261012T1800Z"
CONST_RUN = PILOTS / "claude-constitution/run-20261012T1800Z"
UDHR_SOURCE = PILOTS / "udhr/source/udhr.md"
CONST_SOURCE = PILOTS / "claude-constitution/source/claude-constitution.md"
UDHR_PARTS = [f"translation-part0{i}.ve.md" for i in range(1, 5)]
JT0P = HERE / "run-jt0p"

# 1.3.5 (b): the plan's 2.4 catalogue, in the word forms the pre-registration lists.
CATALOGUE_WORDS = ["reasonable", "reasonably", "unreasonable", "appropriate", "appropriately", "inappropriate",
                   "arbitrary", "arbitrarily", "fair", "fairly", "unfair", "just", "legitimate", "illegitimate",
                   "genuine", "genuinely", "adequate", "adequately", "effective", "effectively", "necessary", "due",
                   "overly"]
CATALOGUE_PHRASES = ["good judgment"]

# R2.1's lexicon, as written (P8, P9).
BASE_LEXICON = ("reasonabl* unreasonabl* appropriate* inappropriate* significant* serious* substantial* severe severely "
                "severity genuine* overly excessive* undue unduly unnecessar* adequate* inadequate* proper properly "
                "improper* arbitrar* fair fairly unfair* legitima* illegitima* acceptabl* unacceptabl* egregious* "
                "flagrant* catastroph* harmful harmless beneficial wise wisely unwise high-stakes dangerous* "
                "problematic").split() + ["good judgment"]
UDHR_ADDITIONS = ("necessary just cruel inhuman degrading barbarous favourable effective competent impartial independent "
                  "indispensable worthy essential importance due natural fundamental").split()

# P6, P7: R2.3's own term lists.
R23_JUDGMENT = ["ill_treatment", "effective", "arbitrary", "genuine", "just_and_favourable_conditions_of_work", "merit",
                "just_requirements", "morality", "general_welfare", "due_recognition_and_respect", "democratic_society"]
R23_BORDERLINE = ["discrimination", "persecution", "free_and_full_consent", "full_development_of_the_human_personality",
                  "free_and_full_development"]


def lexicon_pattern(entries):
    parts = []
    for entry in entries:
        if entry.endswith("*"):
            parts.append(r"\b" + re.escape(entry[:-1]) + r"[\w-]*")
        else:
            parts.append(r"\b" + re.escape(entry) + r"\b")
    return re.compile("|".join(parts), re.IGNORECASE)


CATALOGUE_RE = lexicon_pattern(CATALOGUE_WORDS + CATALOGUE_PHRASES)


def front(path):
    lines = Path(path).read_text().split("\n")
    assert lines[0] == "---" and lines[2] == "---", path
    return json.loads(lines[1])


def udhr_ledger(path=UDHR_RUN / "units.json"):
    return json.loads(Path(path).read_text())["units"]


def const_ledger():
    return json.loads((CONST_RUN / "units.json").read_text())


def classes():
    table = {}
    rows = (HERE / "open_term_class.tsv").read_text().splitlines()
    assert rows[0].split("\t") == ["pilot", "term", "class", "borderline", "reason"]
    for row in rows[1:]:
        pilot, term, klass, borderline, reason = row.split("\t")
        assert klass in {"judgment", "classification", "exception", "attitude", "proportion"}, row
        table[(pilot, term)] = {"class": klass, "borderline": borderline == "yes", "reason": reason}
    return table


def span_bytes(unit):
    start, end = unit["span"]
    return end - start


def source_text(source: bytes, unit):
    start, end = unit["span"]
    return source[start:end].decode("utf-8")


def write(name, data):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------------------------------------------
# Item 1: the instrument (1.3.4)

def instrument(pilot, ledger, declared, source):
    table = classes()
    names = list(dict.fromkeys(declared + [t for u in ledger for t in (u.get("open_terms") or [])]))
    open_term_class = {}
    unclassified = []
    for name in names:
        row = table.get((pilot, name))
        if row is None:
            unclassified.append(name)
        else:
            open_term_class[name] = row["class"]
    units, by_status, by_missing = {}, defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    class_units = defaultdict(lambda: [0, 0])
    catalogue = defaultdict(lambda: {"with_judgment_term": [0, 0], "without_judgment_term": [0, 0]})
    total = [0, 0]
    for unit in ledger:
        terms = unit.get("open_terms") or []
        judgment = [t for t in terms if open_term_class.get(t) == "judgment"]
        size = span_bytes(unit)
        for klass in sorted({open_term_class.get(t, "unclassified") for t in terms}):
            class_units[klass][0] += 1
            class_units[klass][1] += size
        status = unit["status"]
        missing = unit.get("missing_feature") or "none"
        if judgment:
            units[unit["id"]] = judgment
            for bucket in (by_status[status], by_missing[missing], total):
                bucket[0] += 1
                bucket[1] += size
        if CATALOGUE_RE.search(source_text(source, unit)):
            key = "with_judgment_term" if judgment else "without_judgment_term"
            catalogue[status][key][0] += 1
            catalogue[status][key][1] += size
    pair = lambda d: {k: {"units": v[0], "bytes": v[1]} for k, v in sorted(d.items())}
    return {
        "open_term_class": open_term_class,
        "unclassified": unclassified,
        "class_counts": dict(sorted(Counter(open_term_class.values()).items())),
        "borderline_judgment_terms": sorted(n for n, k in open_term_class.items()
                                            if k == "judgment" and table[(pilot, n)]["borderline"]),
        "judgment_term_units": {"total": total[0], "by_status": {k: v[0] for k, v in sorted(by_status.items())},
                                "by_missing_feature": {k: v[0] for k, v in sorted(by_missing.items())}},
        "judgment_term_bytes": {"total": total[1], "by_status": {k: v[1] for k, v in sorted(by_status.items())},
                                "by_missing_feature": {k: v[1] for k, v in sorted(by_missing.items())}},
        "units_by_open_term_class": pair(class_units),
        "catalogue_units_by_status": {k: {kk: {"units": vv[0], "bytes": vv[1]} for kk, vv in v.items()}
                                      for k, v in sorted(catalogue.items())},
        "judgment_terms": units,
    }


def cmd_instrument():
    udhr_source, const_source = UDHR_SOURCE.read_bytes(), CONST_SOURCE.read_bytes()
    udhr_declared = [t["name"] for t in front(UDHR_RUN / UDHR_PARTS[0])["open_terms"]]
    jt0p_declared = [t["name"] for t in front(JT0P / UDHR_PARTS[0])["open_terms"]]
    const_declared = [t["name"] for t in front(CONST_RUN / "translation.ve.md")["open_terms"]]
    out = {
        "instrument-udhr.json": instrument("udhr", udhr_ledger(), udhr_declared, udhr_source),
        "instrument-udhr-jt0p.json": instrument("udhr", udhr_ledger(JT0P / "units.json"), jt0p_declared, udhr_source),
        "instrument-constitution.json": instrument("constitution", const_ledger(), const_declared, const_source),
    }
    for name, data in out.items():
        write(name, data)
        print(name, "terms", len(data["open_term_class"]), "unclassified", data["unclassified"], data["class_counts"],
              "judgment units", data["judgment_term_units"]["total"], "bytes", data["judgment_term_bytes"]["total"])


# --------------------------------------------------------------------------------------------------------------
# Item 3: the by-hand integrity check (1.3.5)

def predicates_read(node, out):
    """Every predicate name a content reads: formula atoms, a norm's regulated predicate, guard and carve-outs."""
    if isinstance(node, list):
        if len(node) >= 2 and node[0] in ("unary", "binary", "nary", "atom", "pred") and isinstance(node[1], str):
            out.append(node[1])
        for child in node:
            predicates_read(child, out)
    elif isinstance(node, dict):
        if "predicate" in node and isinstance(node["predicate"], str):
            out.append(node["predicate"])
        for value in node.values():
            predicates_read(value, out)
    return out


def token_run(term, name):
    """`term` occurs in `name` as a whole run of `_`-separated tokens."""
    t, n = term.split("_"), name.split("_")
    return any(n[i:i + len(t)] == t for i in range(len(n) - len(t) + 1))


def words_of(text):
    return re.findall(r"[a-z]+", text.lower())


def scan_document(pilot, label, doc, statuses, source, wanted=("CHECKED", "LABELLED")):
    vocab = doc["environment"]["vocabulary"]["predicates"]
    terms = [t["name"] for t in doc["open_terms"]]
    sets = defaultdict(list)
    for item in doc.get("reading_sets", []):
        sets[item["unit"]].append(item)
    hits, scanned = [], {}
    for unit in doc["units"]:
        status = statuses.get(unit["id"])
        if status not in wanted:
            continue
        contents = [unit.get("content")] + [r.get("content") for s in sets.get(unit["id"], []) for r in s["readings"]]
        contents = [c for c in contents if c is not None]
        if not contents:
            continue
        preds = list(dict.fromkeys(p for c in contents for p in predicates_read(c, [])))
        scanned[unit["id"]] = {"status": status, "predicates": preds}
        for pred in preds:
            decl = vocab.get(pred, {})
            verbal = decl.get("verbalisation") or ""
            text = " ".join([pred.replace("_", " "), decl.get("description", ""), verbal])
            open_link = [t for t in terms if t == pred or token_run(t, pred)]
            if "open term" in decl.get("description", "").lower():
                open_link.append("(description says 'open term')")
            catalogue = sorted({m.group(0).lower() for m in CATALOGUE_RE.finditer(text)})
            if open_link or catalogue:
                hits.append({"pilot": pilot, "document": label, "unit": unit["id"], "status": status,
                             "predicate": pred, "regulated": "regulated" in decl, "open_term_link": open_link,
                             "catalogue_words": catalogue, "description": decl.get("description", ""),
                             "verbalisation": verbal, "source": source_text(source, unit).strip()})
    return scanned, hits


def scan_all(wanted):
    out = {"scanned_units": {}, "hits": []}
    udhr_source, const_source = UDHR_SOURCE.read_bytes(), CONST_SOURCE.read_bytes()
    udhr_status = {u["id"]: u["status"] for u in udhr_ledger()}
    for part in UDHR_PARTS:
        scanned, hits = scan_document("udhr", part, front(UDHR_RUN / part), udhr_status, udhr_source, wanted)
        out["scanned_units"][f"udhr/{part}"] = scanned
        out["hits"] += hits
    # The constitution's check.json records no unit statuses; its ledger's are the run's record of them.
    const_status = {u["id"]: u["status"] for u in const_ledger()}
    scanned, hits = scan_document("constitution", "translation.ve.md", front(CONST_RUN / "translation.ve.md"),
                                  const_status, const_source, wanted)
    out["scanned_units"]["constitution/translation.ve.md"] = scanned
    out["hits"] += hits
    return out


def cmd_scan():
    out = scan_all(("CHECKED", "LABELLED"))
    # Positive control (not the check): the same scanner over OPEN and READINGS units must find their open terms.
    control = scan_all(("OPEN", "READINGS"))
    out["control_open_and_readings"] = {
        "scanned": sum(len(v) for v in control["scanned_units"].values()),
        "units_with_hits": sorted({(h["pilot"], h["unit"]) for h in control["hits"]}),
        "hits": [{k: h[k] for k in ("pilot", "unit", "status", "predicate", "open_term_link", "catalogue_words")}
                 for h in control["hits"]]}
    write("integrity-scan.json", out)
    print("scanned", {k: len(v) for k, v in out["scanned_units"].items()}, "hits", len(out["hits"]))
    print("control: scanned", out["control_open_and_readings"]["scanned"], "units with hits",
          len(out["control_open_and_readings"]["units_with_hits"]))
    for h in out["hits"]:
        print(f"{h['pilot']}\t{h['unit']}\t{h['status']}\t{h['predicate']}\t{h['open_term_link']}\t{h['catalogue_words']}"
              f"\t{h['source'][:110]}")


def cmd_integrity():
    scan = json.loads((EVIDENCE / "integrity-scan.json").read_text())
    verdicts = {}
    rows = (HERE / "integrity_verdicts.tsv").read_text().splitlines()
    assert rows[0].split("\t") == ["pilot", "unit", "predicate", "verdict", "reason"]
    for row in rows[1:]:
        pilot, unit, pred, verdict, reason = row.split("\t")
        assert verdict in {"hidden judgment", "other sense", "not a judgment"}, row
        verdicts[(pilot, unit, pred)] = {"verdict": verdict, "reason": reason}
    merged = []
    for hit in scan["hits"]:
        key = (hit["pilot"], hit["unit"], hit["predicate"])
        assert key in verdicts, f"no hand verdict for {key}"
        merged.append({**hit, **verdicts.pop(key)})
    assert not verdicts, f"verdicts without a hit: {sorted(verdicts)}"
    summary = Counter((h["pilot"], h["status"], h["verdict"]) for h in merged)
    write("integrity.json", {"scanned_units": scan["scanned_units"],
                             "summary": [{"pilot": p, "status": s, "verdict": v, "hits": n}
                                         for (p, s, v), n in sorted(summary.items())],
                             "hits": merged})
    for (p, s, v), n in sorted(summary.items()):
        print(p, s, v, n)


# --------------------------------------------------------------------------------------------------------------
# Descriptive: admission forecast (1.3.6)

CHECKS = ["JudgmentUnbound", "JudgmentArguments", "JudgmentRegulated", "JudgmentCriterionAsUnit", "JudgmentDecider"]


def forecast_document(doc):
    preds = doc["environment"]["vocabulary"]["predicates"]
    rows, counts, first = [], Counter(), Counter()
    for rec in doc["open_terms"]:
        name = rec["name"]
        pred = preds.get(name)
        fired = []
        if pred is None:
            fired.append("JudgmentUnbound")
        else:
            if pred.get("arguments") != rec["arguments"]:
                fired.append("JudgmentArguments")
            if "regulated" in pred:
                fired.append("JudgmentRegulated")
        if rec["necessary"] or rec["sufficient"]:
            fired.append("JudgmentCriterionAsUnit")
        if rec["decided_by"] == "unstated":
            fired.append("JudgmentDecider")
        counts.update(fired)
        first[fired[0] if fired else "admitted"] += 1
        candidates = sorted(p for p in preds if p != name and token_run(name, p)) if pred is None else []
        rows.append({"term": name, "first_fault": fired[0] if fired else None, "all_faults": fired,
                     "decided_by": rec["decided_by"], "arguments": rec["arguments"],
                     "predicate_sorts": pred.get("arguments") if pred else None, "rename_candidates": candidates})
    return {"records": len(doc["open_terms"]), "first_fault": dict(sorted(first.items())),
            "fails_check": {c: counts.get(c, 0) for c in CHECKS}, "rows": rows}


def cmd_forecast():
    out = {}
    for label, run in (("udhr", UDHR_RUN), ("udhr-jt0p", JT0P)):
        for part in UDHR_PARTS:
            out[f"{label}/{part}"] = forecast_document(front(run / part))
    out["constitution/translation.ve.md"] = forecast_document(front(CONST_RUN / "translation.ve.md"))
    # A term is bound in the UDHR if some part binds it (the parts share one record list).
    for label in ("udhr", "udhr-jt0p"):
        bound_somewhere = sorted({r["term"] for part in UDHR_PARTS for r in out[f"{label}/{part}"]["rows"]
                                  if "JudgmentUnbound" not in r["all_faults"]})
        out[f"{label}/any-part-binds"] = bound_somewhere
    write("admission-forecast.json", out)
    for key, value in out.items():
        if isinstance(value, dict):
            print(key, value["first_fault"], value["fails_check"])
        else:
            print(key, value)


# --------------------------------------------------------------------------------------------------------------
# Reproduction checks P2 to P9 (1.4)

def check(expected, measured):
    return {"expected": expected, "measured": measured, "pass": expected == measured}


def cmd_reproduce():
    ledger = udhr_ledger()
    by_id = {u["id"]: u for u in ledger}
    claimed = sum(span_bytes(u) for u in ledger if u["status"] != "UNFORMALISED")
    pct = lambda b: f"{100 * b / 10916:.2f}%"
    out = {}
    out["P2"] = check({"bytes": 4792, "percent": "43.90%"}, {"bytes": claimed, "percent": pct(claimed)})
    out["P3"] = check({"u010": 132, "u060": 66}, {u: span_bytes(by_id[u]) for u in ("u010", "u060")})
    jt0p = udhr_ledger(JT0P / "units.json")
    claimed_jt0p = sum(span_bytes(u) for u in jt0p if u["status"] != "UNFORMALISED" and u.get("claimed", True))
    out["P4"] = check({"bytes": 4924, "percent": "45.11%"}, {"bytes": claimed_jt0p, "percent": pct(claimed_jt0p)})
    out["P5"] = check({"udhr": [52, 52, 52, 52], "constitution": 33},
                      {"udhr": [len(front(UDHR_RUN / p)["open_terms"]) for p in UDHR_PARTS],
                       "constitution": len(front(CONST_RUN / "translation.ve.md")["open_terms"])})

    def carrying(terms):
        units = [u for u in ledger if set(u.get("open_terms") or []) & set(terms)]
        status = defaultdict(lambda: [0, 0])
        for u in units:
            status[u["status"]][0] += 1
            status[u["status"]][1] += span_bytes(u)
        return {"units": len(units), "bytes": sum(span_bytes(u) for u in units),
                "by_status": {k: {"units": v[0], "bytes": v[1]} for k, v in sorted(status.items())},
                "ids": [u["id"] for u in units]}

    p6 = carrying(R23_JUDGMENT)
    out["P6"] = check({"units": 11, "bytes": 1333, "by_status": {"OPEN": {"units": 8, "bytes": 706},
                                                                 "READINGS": {"units": 3, "bytes": 627}}},
                      {k: p6[k] for k in ("units", "bytes", "by_status")})
    out["P6"]["ids"] = p6["ids"]
    p7 = carrying(R23_JUDGMENT + R23_BORDERLINE)
    out["P7"] = check({"units": 18, "bytes": 1945}, {"units": p7["units"], "bytes": p7["bytes"]})
    out["P7"]["ids"] = p7["ids"]

    base = lexicon_pattern(BASE_LEXICON)
    lines = [l for l in CONST_SOURCE.read_text().split("\n") if l.strip()]
    hits = sum(1 for l in lines if base.search(l))
    out["P8"] = check({"lines_with_word": 203, "non_empty_lines": 454}, {"lines_with_word": hits,
                                                                          "non_empty_lines": len(lines)})
    udhr = lexicon_pattern(BASE_LEXICON + UDHR_ADDITIONS)
    source = UDHR_SOURCE.read_bytes()
    units = [u for u in ledger if u["status"] == "UNFORMALISED" and u["id"] not in ("u043", "u093")
             and udhr.search(source_text(source, u))]
    out["P9"] = check({"units": 12, "bytes": 1942}, {"units": len(units), "bytes": sum(span_bytes(u) for u in units)})
    out["P9"]["ids"] = [u["id"] for u in units]
    out["P9"]["words"] = {u["id"]: sorted({m.group(0).lower() for m in udhr.finditer(source_text(source, u))})
                          for u in units}
    write("reproduction.json", out)
    for key, value in out.items():
        print(key, "PASS" if value["pass"] else "FAIL", "expected", value["expected"], "measured", value["measured"])


if __name__ == "__main__":
    commands = {"instrument": cmd_instrument, "scan": cmd_scan, "integrity": cmd_integrity,
                "forecast": cmd_forecast, "reproduce": cmd_reproduce}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(__doc__)
    commands[sys.argv[1]]()
