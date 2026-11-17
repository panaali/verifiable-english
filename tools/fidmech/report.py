"""The fid-mech report (plan 8): kill tables, units passing the stated checks, lever-off hits, adjudication matching,
plants and real defects, and the run cost, from the batch directories tools/fidmech/runner.py writes. Counts only.

  uv run python -m tools.fidmech report BATCH_DIR... --out DIR [--inputs DIR] [--cr FILE] [--rows DIR]

- **Kill table** (plan 2e). Rows are ops; per instrument (K, L1-L4, D, CR) killed / decided, where decided leaves out
  K error, inconclusive and not-run, a text check's error and CR not-read (each counted beside). "any" is killed by
  at least one instrument; "none" is split: every instrument ran (CR included), CR not read, some instrument did not
  run. Scored = parse ok and not equivalent; stillborn mutants are listed, never scored.
- **Units passing the stated checks** (L1, L2, L3, D, K-structural): no L1, L2, L3 or D hit at baseline, and every
  applicable non-equivalent structural mutant of the unit ran to a decided K verdict and K killed it. Any
  inconclusive, error or not-run makes the unit incomplete; a unit with no applicable mutant is untested. Printed
  with and without flip-force, with declared equivalents counted as survivors, and without D for a document with no
  sidecar. Never "faithful".
- **Adjudication** (`adjudicate`). A baseline hit is confirmed by a REAL-by-both finding, contradicted by a
  NOT-by-both one, of the SAME allegation class (ALLEGATION; the classes in NO_ALLEGATION have none), on the hit's
  unit, whose cited text (word, for the word classes) the hit overlaps, on a unit whose fp-1 is unchanged since the
  adjudication. Everything else is unadjudicated.
- **CR** (`fill_cr`): a recall-gate record fills a wording mutant's CR only on (unit, kind, old, new) and a fp-1
  equal both to fp1.json's measured row and to the unit's fp-1 in the batch; anything else stays not-read.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

INSTRUMENTS = ("K", "L1", "L2", "L3", "L4", "D", "CR")
TEXT = ("L1", "L2", "L3", "L4", "D")
DECIDED = {"K": ("killed", "survived"), "CR": ("found", "missed"), **{c: ("killed", "survived") for c in TEXT}}
KILL = {"K": "killed", "CR": "found", **{c: "killed" for c in TEXT}}
ALLEGATION = {"L1c": "cut or short quote", "L1e": "cut or short quote", "L1n": "number changed",
              "D": "word dropped", "L3w": "word added", "L2b": "bare legend", "L4u": "obligation not translated"}
NO_ALLEGATION = ("L1m", "L1u", "L1a", "L2q", "L2a", "L4l")
WORD_CLASSES = ("D", "L3w")
L1_CLASSES = ("L1m", "L1n", "L1u", "L1c", "L1e", "L1a")
HEADLINE = "Units passing the stated checks (L1, L2, L3, D, K-structural)"
BLIND_SPOT = ("blind spot: K cannot see act or legend wording (opaque atoms); L1-L3 and D see the text, not the "
              "rule's meaning; see the escapes of plan 11")
OLD_FIGURES = ("old joint-run figures (item 49, the joint K + CR run before this harness, not isolated): "
               "6/12 plants, 0/14 real RSP defects")
CHALLENGER = ("the challenger's 2.8 CPU-h per 100 mutants is an estimate for a 280-question set; RSP has 126 "
              "questions, so the figures are not like for like")
SCOPED = ("structural", "wording")


def load_batch(directory):
    d = Path(directory)
    batch = json.loads((d / "batch.json").read_text(encoding="utf-8"))
    lines = [json.loads(x) for x in (d / "results.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()] \
        if (d / "results.jsonl").exists() else []
    mutants = [json.loads(x) for x in (d / "mutants.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    text = json.loads((d / "textcheck.json").read_text(encoding="utf-8")) if (d / "textcheck.json").exists() else None
    return {"batch": batch, "lines": lines, "mutants": mutants, "text": text}


def _declared(line):
    return (line["mutant"]["equivalent"] or "").startswith("declared:")


def verdicts(line, declared_as_survivor=False):
    """A line's verdicts; a declared equivalent counted as a survivor reads survived on every instrument it ran."""
    v = dict(line["record"]["verdict"])
    if declared_as_survivor and _declared(line):
        v.update({k: "survived" for k in ("K", *TEXT)})
    return v


def scored(lines, classes=SCOPED, declared_as_survivor=False):
    """The lines a kill table scores: parse ok, not equivalent (a declared one when counted as a survivor)."""
    return [x for x in lines if x["mutant"]["class"] in classes and x["mutant"]["parse"] == "ok"
            and (x["mutant"]["equivalent"] is None or (declared_as_survivor and _declared(x)))]


def kill_row(lines, declared_as_survivor=False):
    """Counts of one group of scored lines: per instrument killed and decided, the outcomes left out, any, none."""
    row = {"scored": len(lines)}
    for instrument in INSTRUMENTS:
        vs = [verdicts(x, declared_as_survivor)[instrument] for x in lines]
        row[instrument] = {"killed": sum(v == KILL[instrument] for v in vs),
                           "decided": sum(v in DECIDED[instrument] for v in vs),
                           "left_out": dict(Counter(v for v in vs if v not in DECIDED[instrument]))}
    any_killed, none = 0, Counter()
    for x in lines:
        v = verdicts(x, declared_as_survivor)
        if any(v[i] == KILL[i] for i in INSTRUMENTS):
            any_killed += 1
        elif all(v[i] in DECIDED[i] for i in INSTRUMENTS):
            none["every instrument ran"] += 1
        elif all(v[i] in DECIDED[i] for i in INSTRUMENTS if i != "CR"):
            none["CR not read"] += 1
        else:
            none["some instrument did not run"] += 1
    row["any"] = any_killed
    row["none"] = dict(none)
    return row


def kill_table(lines, declared_as_survivor=False):
    """{op: row} over the scored lines, and the document's row under "all"."""
    rows = scored(lines, declared_as_survivor=declared_as_survivor)
    ops = list(dict.fromkeys(x["mutant"]["op"] for x in rows))
    table = {op: kill_row([x for x in rows if x["mutant"]["op"] == op], declared_as_survivor) for op in ops}
    table["all"] = kill_row(rows, declared_as_survivor)
    return table


def score(row, instrument="K"):
    """(killed, n) of the mutation score (K: K-killed / K-decided) or the any-instrument score (any / scored)."""
    if instrument == "any":
        return row["any"], row["scored"]
    return row[instrument]["killed"], row[instrument]["decided"]


def unit_hits(text, with_d=True):
    """{unit: sorted classes} of the baseline L1, L2, L3 and D hits on each unit (L2 through the predicate's users)."""
    out = {u: set() for u in text["units"]}
    for h in text["hits"]:
        cls = h["class"]
        if cls in L1_CLASSES or cls == "L3w" or (with_d and cls == "D"):
            if h["block"] in out:
                out[h["block"]].add(cls)
        elif cls in ("L2b", "L2q", "L2a"):
            for u in text["users"].get(h["block"], ()):
                out.setdefault(u, set()).add(cls)
    return {u: sorted(c) for u, c in out.items()}


def unit_status(lines, text, *, flip_force=True, declared_as_survivor=False, with_d=True):
    """{"passing", "failing", "incomplete", "untested", "with_survivor"} counts and the unit lists (rows only)."""
    hits = unit_hits(text, with_d)
    structural = [x for x in scored(lines, ("structural",), declared_as_survivor)
                  if flip_force or x["mutant"]["op"] != "flip-force"]
    by_unit = {}
    for x in structural:
        by_unit.setdefault(x["mutant"]["unit"], []).append(verdicts(x, declared_as_survivor)["K"])
    status, why = {}, Counter()
    for u in text["units"]:
        ks = by_unit.get(u)
        if not ks:
            status[u] = "untested"
        elif hits.get(u):
            status[u] = "failing"
            why.update({"text hit " + ("L1" if c in L1_CLASSES else c[:2] if c != "D" else "D")
                        for c in hits[u]})
            why["K survivor"] += "survived" in ks
        elif any(k not in DECIDED["K"] for k in ks):
            status[u] = "incomplete"
        else:
            status[u] = "passing" if all(k == "killed" for k in ks) else "failing"
            why["K survivor, no text hit"] += status[u] == "failing"
    counts = Counter(status.values())
    survivors = sorted(u for u, ks in by_unit.items() if "survived" in ks)
    return {"units": len(status), **{k: counts.get(k, 0) for k in ("passing", "failing", "incomplete", "untested")},
            "with_survivor": len(survivors), "failing_by": dict(sorted(why.items())),
            "lists": {"status": status, "with_survivor": survivors}}


def _norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (text or "").lower())).strip()


def _words(text):
    return set(_norm(text).split())


def overlaps(a, b, n=4):
    """Whether two texts overlap: one holds the other, or they share a run of `n` words."""
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    wa, wb = a.split(), b.split()
    grams = {tuple(wa[i:i + n]) for i in range(len(wa) - n + 1)}
    return any(tuple(wb[i:i + n]) in grams for i in range(len(wb) - n + 1))


def _hit_words(h):
    quote = h["quote"] or ""
    return _words(quote.split(": ", 1)[1] if quote.startswith("loss ") else quote)


def adjudicate(hit, document, adjudications, users, fp_now):
    """("confirmed" | "contradicted" | "unadjudicated", the finding id or a reason) of one baseline hit."""
    allegation = ALLEGATION.get(hit["class"])
    if allegation is None:
        return "unadjudicated", "the check class has no allegation class"
    units = set(users.get(hit["block"], ())) if hit["class"] == "L2b" else {hit["block"]}
    found = {"REAL-by-both": [], "NOT-by-both": []}
    for f in adjudications:
        if f["case"] != document or f["allegation_class"] != allegation or f["verdict"] not in found:
            continue
        if hit["class"] != "L4u" and f["unit"] not in units:
            continue
        if hit["class"] in WORD_CLASSES:
            if not (_hit_words(hit) & _words(f.get("word"))):
                continue
        elif hit["class"] != "L2b" and not overlaps(hit["quote"], f["cited_text"]):
            continue
        if fp_now.get(f["fp1_key"]) != f["fp1"]:
            continue
        found[f["verdict"]].append(f["id"])
    if found["REAL-by-both"]:
        return "confirmed", found["REAL-by-both"][0]
    if found["NOT-by-both"]:
        return "contradicted", found["NOT-by-both"][0]
    return "unadjudicated", "no finding of the same class, unit, text and unchanged fp-1"


def _cr_entries(data):
    """Every recall-gate mutant entry of a --cr file: a list of entries, or any nesting holding
    {"recall_gate": {"mutants": [...]}}."""
    if isinstance(data, list):
        if all(isinstance(e, dict) and "kind" in e for e in data):
            return list(data)
        return [e for x in data for e in _cr_entries(x)]
    if isinstance(data, dict):
        gate = data.get("recall_gate")
        if isinstance(gate, dict) and isinstance(gate.get("mutants"), list):
            return list(gate["mutants"])
        return [e for v in data.values() if isinstance(v, (dict, list)) for e in _cr_entries(v)]
    return []


def fill_cr(lines, mutants, entries, fp1_rows, fp_now, document):
    """Set CR found/missed on the wording lines a recall-gate entry matches (unit, kind, old in a find and new in
    its replace, and fp-1 equal to fp1.json's measured row and to the batch's); the number filled."""
    measured = {r["unit"]: r["fp1"] for r in fp1_rows if r["case"] == document and r["role"] == "measured"}
    edits = {m["id"]: m["edits"] for m in mutants}
    filled = 0
    for x in lines:
        m = x["mutant"]
        if m["class"] != "wording":
            continue
        for e in entries:
            if (e.get("unit") != m["unit"] or e.get("kind") != m["op"] or "found" not in e
                    or not e.get("fp1") or e["fp1"] != measured.get(m["unit"]) or e["fp1"] != fp_now.get(m["unit"])):
                continue
            if any(e.get("old") and e["old"] in d["find"] and e.get("new") and e["new"] in d["replace"]
                   for d in edits.get(m["id"], ())):
                x["record"]["verdict"]["CR"] = "found" if e["found"] else "missed"
                filled += 1
                break
    return filled


def plant_rows(lines, rows):
    """Per plant and per defect: its status and, for an applied one, its K and text verdicts and whether any
    instrument told the two versions apart (rows go to manage-agents only)."""
    by_id = {x["record"]["id"]: x for x in lines}
    out = {}
    for part in ("plants", "defects"):
        out[part] = []
        for r in rows.get(part, ()):
            row = dict(r)
            x = by_id.get(r.get("mutant"))
            if x is not None:
                v = x["record"]["verdict"]
                row.update({"K": v["K"], "text": {c: v[c] for c in TEXT},
                            "any": any(v[i] == KILL[i] for i in INSTRUMENTS)})
            out[part].append(row)
    return out


def plant_counts(prows):
    """Counts of plant_rows: applied, killed by K / K-decided, by any instrument, and the statuses."""
    out = {}
    for part, rows in prows.items():
        applied = [r for r in rows if r["status"] == "applied"]
        ran = [r for r in applied if "K" in r]
        out[part] = {"entries": len(rows), **Counter(r["status"] for r in rows),
                     "K_killed": sum(r["K"] == "killed" for r in ran),
                     "K_decided": sum(r["K"] in DECIDED["K"] for r in ran),
                     "any_killed": sum(r["any"] for r in ran), "text_killed": sum(
                         any(r["text"][c] == "killed" for c in TEXT) for r in ran),
                     "not_applicable_by": dict(Counter(reason_class(r["reason"]) for r in rows
                                                       if r["status"] == "not applicable"))}
    return out


REASONS = (("is gone from the file under test", "the plant's unit text is gone at the tree under test"),
           ("times in the file under test", "the changed text is not unique at the tree under test"),
           ("the repair deleted", "the repair deleted text the defect needs"),
           ("never read as the repair", "the repaired text changed later"))


def reason_class(reason):
    """The class of a not-applicable reason; VE gets the class, the reason (which names the unit) stays in rows."""
    return next((label for key, label in REASONS if key in reason), "other")


def document_report(b, inputs=None, cr=None):
    """The counts of one batch: report.json's entry for its document, and the rows that stay outside VE."""
    batch, lines, text = b["batch"], b["lines"], b["text"]
    document = batch["document"]
    fp_now = batch.get("fp1", {})
    if cr is not None and inputs is not None:
        batch["cr_filled"] = fill_cr(lines, b["mutants"], _cr_entries(cr), inputs["fp1"], fp_now, document)
    out = {"document": document, "status": batch.get("status"), "inputs_sha256": batch.get("inputs_sha256"),
           "in_sample": document == "anthropic-rsp", "mutants": batch.get("mutants"), "ran": batch.get("ran"),
           "not_run": batch.get("not_run"), "measurements": batch.get("measurements")}
    stillborn = [m for m in b["mutants"] if m["parse"] != "ok"]
    out["stillborn"] = {"count": len(stillborn), "by_op": dict(Counter(m["op"] for m in stillborn))}
    out["kill_table"] = kill_table(lines)
    out["kill_table_declared_as_survivor"] = {"all": kill_table(lines, True)["all"]}
    errors = [x["record"]["kernel"].get("error") or "" for x in scored(lines) if x["record"]["verdict"]["K"] == "error"]
    out["K_errors"] = dict(Counter(":".join((e.strip().splitlines() or [""])[-1].split(":")[:2])
                                   for e in errors).most_common())
    out["equivalent"] = dict(Counter(m["equivalent"].split(":")[0] for m in b["mutants"] if m["equivalent"]))
    sel = batch.get("selection") or {}
    unprobed = set(sel.get("in_no_item", ()))
    k_unprobed = [x["record"]["verdict"]["K"] for x in scored(lines) if x["mutant"]["unit"] in unprobed]
    out["unprobed_rules"] = {"rule_blocks": sel.get("rule_blocks"), "in_no_item": len(unprobed),
                             "their_scored_mutants": len(k_unprobed), "K": dict(Counter(k_unprobed))}
    rows = {}
    if text is not None:
        sidecar = text.get("sidecar", True)
        variants = {"all ops": {}, "without flip-force": {"flip_force": False},
                    "declared equivalents counted as survivors": {"declared_as_survivor": True}}
        if not sidecar:
            variants["without D (no sidecar)"] = {"with_d": False}
        units = {name: unit_status(lines, text, **kw) for name, kw in variants.items()}
        rows["units"] = {name: u.pop("lists") for name, u in units.items()}
        out["units"] = units
        out["sidecar"] = sidecar
        out["hits"] = {"raw": text["counts"], "also_gated": text.get("also_gated", {}),
                       "levers": {k: ({"cleared": len(v["cleared"]), "added": len(v["added"])} if "error" not in v
                                      else {"error": v["error"]}) for k, v in text["levers"].items()}}
        if inputs is not None:
            results = [adjudicate(h, document, inputs["adjudications"], text["users"], fp_now) for h in text["hits"]
                       if h["class"] != "L4g"]
            out["adjudication"] = dict(Counter(r[0] for r in results))
            mine = [f for f in inputs["adjudications"] if f["case"] == document]
            out["adjudication_findings"] = {
                "findings": len(mine), **dict(Counter(f["verdict"] for f in mine)),
                "unit_fp1_unchanged": sum(fp_now.get(f["fp1_key"]) == f["fp1"] for f in mine)}
            rows["adjudication"] = [{"hit": [h["class"], h["block"], h["quote"]], "outcome": r[0], "by": r[1]}
                                    for h, r in zip([h for h in text["hits"] if h["class"] != "L4g"], results)]
    syntactic = [x for x in lines if x["mutant"]["equivalent"] == "syntactic"]
    out["control_false_alarms"] = sum(bool(x["text"]["new_hits"]) for x in syntactic)
    blind = [x for x in scored(lines) if not any(x["record"]["verdict"][i] == KILL[i] for i in INSTRUMENTS)]
    out["blind_spot"] = dict(Counter(x["mutant"]["op"] for x in blind))
    rows["blind_spot_units"] = sorted({x["mutant"]["unit"] for x in blind})
    prows = plant_rows(lines, batch.get("rows") or {})
    out["plants_and_defects"] = plant_counts(prows)
    rows["plants_and_defects"] = prows
    return out, rows


def _cell(row, instrument):
    k, n = score(row, instrument)
    return f"{k}/{n}"


def render(report):
    """REPORT.md of report.json's dict (counts only)."""
    out = ["# fid-mech report (counts only)", "",
           f"Headline: **{HEADLINE}**. Never \"faithful\". {BLIND_SPOT}.", ""]
    if report.get("inputs_sha256"):
        out += ["Inputs read by sha256: " + ", ".join(f"{k} {v[:16]}..." for k, v in report["inputs_sha256"].items()),
                ""]
    for d in report["documents"]:
        out += [f"## {d['document']}" + (" (in-sample)" if d["in_sample"] else " (out-of-sample under the freeze "
                                                                              "rule)"), "",
                f"batch status {d['status']}; {d['mutants']} mutants, {d['ran']} run, {d['not_run']} not run; "
                f"stillborn {d['stillborn']['count']} (listed, never scored) {d['stillborn']['by_op']}; "
                f"equivalent {d['equivalent']}; inputs_sha256 {d['inputs_sha256']}", ""]
        for name, u in d.get("units", {}).items():
            out.append(f"- {HEADLINE}, {name}: {u['passing']} of {u['units']} (failing {u['failing']}, incomplete "
                       f"{u['incomplete']}, untested {u['untested']}; units with at least one K survivor "
                       f"{u['with_survivor']}); failing units by cause (a unit can have several) {u['failing_by']}")
        t = d["kill_table"]
        out += ["", "| op | scored | K | L1 | L2 | L3 | L4 | D | CR | any | none | K left out |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for op, row in t.items():
            out.append(f"| {op} | {row['scored']} | " + " | ".join(_cell(row, i) for i in INSTRUMENTS)
                       + f" | {row['any']}/{row['scored']} | {row['none']} | {row['K']['left_out']} |")
        a, s = t["all"], d["kill_table_declared_as_survivor"]["all"]
        out += ["", f"- mutation score (K) {_cell(a, 'K')}, any-instrument score {_cell(a, 'any')}; with declared "
                    f"equivalents counted as survivors: K {_cell(s, 'K')}, any {_cell(s, 'any')}. No Wilson "
                    "interval: mutants of one unit are correlated and generated, not sampled.",
                f"- unprobed rules: {d['unprobed_rules']['in_no_item']} of {d['unprobed_rules']['rule_blocks']} rule "
                f"blocks are in no item; every K mutant of such a rule survives K (their K verdicts: "
                f"{d['unprobed_rules']['K']}).",
                f"- K errors (VE refused the mutated document when it ran, or the run failed), by last line: "
                f"{d['K_errors']}",
                f"- control false alarms (new hits on syntactic equivalents): {d['control_false_alarms']}",
                f"- blind spot (no kill among the instruments run), by op: {d['blind_spot']}"]
        if "hits" in d:
            out += [f"- baseline hits by class: {d['hits']['raw']}; also gated: {d['hits']['also_gated']}",
                    f"- hits each lever clears / adds when off: {d['hits']['levers']}"]
        if "adjudication" in d:
            c = d["adjudication"]
            out.append(f"- adjudication of the baseline hits: {c.get('confirmed', 0)} confirmed, "
                       f"{c.get('contradicted', 0)} contradicted, {c.get('unadjudicated', 0)} unadjudicated; the "
                       f"document's findings: {d['adjudication_findings']} (a hit matches only a finding whose unit's "
                       "fp-1 is unchanged since the adjudication)")
            if c.get("unadjudicated"):
                out.append(f"- false-discovery proportion among hits not measured: {c.get('confirmed', 0)} confirmed, "
                           f"{c.get('contradicted', 0)} contradicted, {c.get('unadjudicated', 0)} unadjudicated. "
                           "Item 32's false-alarm figure needs a seeded adjudication sample (two blind adjudicators, "
                           "about 20 hits per document), offered to the DRI and not run here.")
        pd = d["plants_and_defects"]
        for part, c in pd.items():
            if c["entries"]:
                out.append(f"- {part}: {json.dumps(c, ensure_ascii=False)}")
        if any(c["entries"] for c in pd.values()):
            out.append(f"- {OLD_FIGURES}")
        m = d.get("measurements") or {}
        out += [f"- run cost (measured): {json.dumps(m, ensure_ascii=False)}; tokens 0. {CHALLENGER}.", ""]
    return "\n".join(out) + "\n"


def main(args) -> int:
    from tools.fidmech import manifests
    try:
        inputs = manifests.load(args.inputs) if args.inputs else None
    except manifests.InputsError as e:
        print(f"fidmech report: {e}", flush=True)
        return 65
    cr = json.loads(Path(args.cr).read_text(encoding="utf-8")) if args.cr else None
    docs, rows = [], {}
    for directory in args.batches:
        d, r = document_report(load_batch(directory), inputs, cr)
        docs.append(d)
        rows[d["document"]] = r
    report = {"documents": docs, "inputs_sha256": inputs["sha256"] if inputs else None}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "REPORT.md").write_text(render(report), encoding="utf-8")
    if args.rows:
        Path(args.rows).mkdir(parents=True, exist_ok=True)
        (Path(args.rows) / "rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    print(f"wrote {out / 'REPORT.md'} and report.json" + (f"; rows to {args.rows}" if args.rows else ""))
    return 0
