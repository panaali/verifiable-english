"""PS-E1 scorer: bars, candidate table and results, read from the prereg file and the saved raw answers."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e1_items  # noqa: E402
import e1_stub  # noqa: E402

RAW = e1_items.DATA / "raw"
TABLE = e1_items.DATA / "candidate-table.json"
RESULTS = e1_items.ROOT / "docs/research/presupposition-E1.md"
SPEC = e1_items.ROOT / "docs/spec/presupposition.md"
LABEL = "proxy, an upper bound for careful readers"
ANSWER = re.compile(r"^\s*\(?([a-eA-E])\)?[.:]?\s*$")
ROWS = ("definite", "plural", "generic")
MEASURED = ("top", "negated", "antecedent", "consequent", "rule_act", "rule_guard")
ALL_CELLS = ("top", "negated", "antecedent", "consequent", "disjunct", "rule_act", "rule_guard")
LEAN_CELL = {"top": ".top", "negated": ".negated", "antecedent": ".antecedent", "consequent": ".consequent",
             "disjunct": ".disjunct", "rule_act": ".ruleAct", "rule_guard": ".ruleGuard"}
LEAN_CAND = {"assumed": ".assumed", "conditioned": ".conditioned", "asserted": ".asserted", "in_place": ".inPlace",
             "unconditional": ".unconditional"}


def config(text=None):
    text = e1_stub.PREREG.read_text() if text is None else text
    return json.loads(text.split("<!-- config:begin -->\n```json\n")[1].split("```\n<!-- config:end -->")[0])


def letter(item, record):
    """(letter, why): a call error or an answer outside the item's options counts as (d) and is listed (F2)."""
    if record.get("error"):
        return "d", "error"
    found = ANSWER.match(record.get("answer") or "")
    if found and found.group(1).lower() in item["options"]:
        return found.group(1).lower(), None
    return "d", "malformed"


def tally(items, records, trials):
    """Letter counts per item from one final record per trial; a missing or unfinished trial refuses."""
    counts, errors, malformed = {}, [], []
    for item in items:
        count = Counter()
        for t in range(1, trials + 1):
            record = records.get((item["id"], t))
            if record is None or record.get("state") != "final":
                raise ValueError(f"trial {item['id']}#{t} has no final record")
            got, why = letter(item, record)
            count[got] += 1
            if why:
                (errors if why == "error" else malformed).append(f"{item['id']}#{t:02d}")
        counts[item["id"]] = {k: count[k] for k in item["options"]}
    return counts, errors, malformed


def carriers(item, count, row):
    """Answers per carrier of a target item; (b) and (e) are one class only where the stub row says so (R-D4)."""
    out = {item["key"][k]: n for k, n in count.items() if k != "d"}
    if row["be_one_class"]:
        out["conditioned"] += out["in_place"]
    return out


def class_cell(cfg, pair, counts, table):
    """One class in one cell: its two items against the plan's bars."""
    bars, order = cfg["bars"], cfg["candidate_order"]
    each = [carriers(i, counts[i["id"]], table[i["id"]]) for i in pair]
    cands = [k for k in order if all(c.get(k, 0) >= bars["candidate_min"] for c in each)]
    ones = [k for k in order if all(c.get(k, 0) >= bars["one_reading_min"] for c in each)]
    no_carrier = any(counts[i["id"]]["d"] > bars["cannot_tell_max"] for i in pair)
    return {"candidates": [] if no_carrier else cands, "one_reading": ones[0] if ones and not no_carrier else None,
            "no_carrier": no_carrier, "shares": each}


def row_cell(cfg, classes):
    """The row's cell from its classes' cells (prereg rules 2 and 3): a no-carrier class empties it, one reading
    needs every class to agree, otherwise the union in share order."""
    order = cfg["candidate_order"]
    total = Counter()
    for c in classes.values():
        for share in c["shares"]:
            total.update(share)
    notes = []
    if any(c["no_carrier"] for c in classes.values()):
        return {"cell": [], "status": "no_carrier", "total": total, "notes": notes}
    union = [k for k in order if any(k in c["candidates"] for c in classes.values())]
    if len({tuple(sorted(c["candidates"])) for c in classes.values()}) > 1:
        notes.append("classes disagree: " + "; ".join(f"{n} {c['candidates']}" for n, c in classes.items()))
    ones = {c["one_reading"] for c in classes.values()}
    status = "open"
    if len(ones) == 1 and None not in ones:
        one = ones.pop()
        status = "one_reading"
        union = [one] + (["in_place"] if one == "conditioned" and "in_place" in union else [])
    if "assumed" in union and "asserted" in union:  # cellOk, spec 10 C3: the cell lists assumed
        union.remove("asserted")
        notes.append("asserted also above the bar; dropped for assumed (C3), PS-E2 tests its wording as a paraphrase")
    if "in_place" in union and "conditioned" not in union:  # cellOk: never in place without conditioned
        union.append("conditioned")
    return {"cell": sorted(union, key=lambda k: (-total[k], order.index(k))), "status": status, "total": total,
            "notes": notes}


def analyse(cfg, items, counts, rows):
    """Every bar of the plan on the saved counts, and the candidate table."""
    bars, by_id = cfg["bars"], {r["id"]: r for r in rows}
    targets = [i for i in items if i["family"] == "target"]
    cells = {}
    for row in ROWS:
        for cell in MEASURED:
            classes = {}
            for cls in (c for c, r in cfg["mapping"].items() if r == row):
                pair = [i for i in targets if i["class"] == cls and i["cell"] == cell]
                classes[cls] = class_cell(cfg, pair, counts, by_id)
            cells[row, cell] = row_cell(cfg, classes) | {"classes": classes}
    controls = {i["id"]: counts[i["id"]][i["expected"]] for i in items if i["family"] == "control"}
    passing = sum(n >= bars["control_min"] for n in controls.values())
    suspension = {i["id"]: counts[i["id"]]["c"] for i in items if i["family"] == "suspension"}
    proviso = {row: {i["id"]: counts[i["id"]]["c"] for i in items if i["family"] == "proviso" and i["row"] == row}
               for row in ROWS}
    for row, pair in proviso.items():
        cell = cells[row, "consequent"]
        if all(n >= bars["proviso_min"] for n in pair.values()):
            previous = cell["status"]
            cell["total"] = cell["total"] + Counter({"unconditional": sum(pair.values())})
            order = cfg["candidate_order"]
            cell["cell"] = sorted(cell["cell"] + ["unconditional"], key=lambda k: (-cell["total"][k], order.index(k)))
            if previous != "open":
                cell["notes"].append(f"target cell was {previous}; proviso independently adds unconditional")
                cell["status"] = "open"
    table = [{"row": row, "cells": {c: list(cells[row, c]["cell"]) if c != "disjunct" else [] for c in ALL_CELLS}}
             for row in ROWS]
    return {"cells": cells, "table": table, "controls": controls, "controls_passing": passing,
            "controls_ok": passing >= bars["controls_passing_min"], "suspension": suspension,
            "suspension_ok": all(n <= bars["suspension_c_max"] for n in suspension.values()), "proviso": proviso}


def table_ok(table):
    """`tableOk` from Lean: the spec's own `Candidate` and `cellOk` are elaborated, never copied here."""
    spec = SPEC.read_text()
    cand = re.search(r"inductive Candidate where\n.*?deriving DecidableEq, Repr\n", spec, re.S).group(0)
    cell_ok = re.search(r"def cellOk \(pc : PositionClass\) \(cs : List Candidate\) : Bool :=\n.*?\n\n", spec, re.S).group(0)
    lines = "\n".join(
        f"#eval IO.println (cellOk {LEAN_CELL[c]} [{', '.join(LEAN_CAND[k] for k in row['cells'][c])}])"
        for row in table for c in ALL_CELLS)
    source = f"import VE.Presupposition.Frame\nnamespace VE.Presupposition\n{cand}\n{cell_ok}\n{lines}\nend VE.Presupposition\n"
    return all(line == "true" for line in e1_stub.run_lean(source, "PsE1Table.lean").split())


def load_records(raw=RAW):
    records = {}
    for path in Path(raw).glob("*/*.json"):
        record = json.loads(path.read_text())
        if path.parent.name != record["id"] or path.name != f"{record['trial']:02d}.json":
            raise ValueError(f"misfiled raw record {path}")
        records[record["id"], record["trial"]] = record
    return records


def bound(items, cfg, records):
    """Every saved record names a frozen item's trial and the exact prompts it was sent."""
    known = {i["id"]: i for i in items}
    for (id_, trial), record in records.items():
        if id_ not in known or not 1 <= trial <= cfg["trials_per_item"]:
            raise ValueError(f"raw record outside the frame: {id_}#{trial}")
        if (record["prompt_sha256"] != e1_items.sha(e1_items.prompt(known[id_]))
                or record["system_sha256"] != e1_items.sha(cfg["reader_instruction"])):
            raise ValueError(f"rebound raw record: {id_}#{trial}")


def results_md(cfg, items, counts, out, errors, malformed, calls, cw):
    bars = cfg["bars"]
    listed = lambda ids: f"{len(ids)}{' ' + ', '.join(ids) if ids else ''}"  # noqa: E731
    lines = ["# PS-E1: which carriers do readers take?", "",
             f"Generated by `docs/presupposition/ps-e1/e1_score.py --write` from the saved raw answers. Every result is "
             f"labelled **{LABEL}**: Sonnet 5.5 is a proxy, and none of this establishes what untrained human readers "
             "understand. It decides candidates and wording only; it never admits a sentence (D2-6).", "",
             f"Calls: {calls}. CW used (reported usage): {cw}. Call errors, counted as (d): {listed(errors)}. "
             f"Answers outside the options, counted as (d): {listed(malformed)}.", "", "## Bars (plan, verbatim) and scores", "",
             f"**Controls** ({LABEL}): \"at least 36/40 choose the answer the proved carrier predicts, on at least 11 of 12 "
             f"items.\" Scored: {out['controls_passing']} of 12: {'HOLDS' if out['controls_ok'] else 'FAILS'}. Answers for the "
             "key: " + ", ".join(f"{k} {v}/40" for k, v in out["controls"].items()) + ".", "",
             f"**Suspension** ({LABEL}): \"(c) at most 6/40 on each item.\" Scored: "
             f"{'HOLDS' if out['suspension_ok'] else 'FAILS'}: " + ", ".join(f"{k} {v}/40" for k, v in out["suspension"].items())
             + ".", "", f"**Proviso** ({LABEL}): \"reported as the share of unconditional-assumption answers. If at least 6/40 "
             "on both items, the unconditional goal becomes an extra candidate in the consequent cells.\" Scored:", ""]
    for row, pair in out["proviso"].items():
        met = all(n >= bars["proviso_min"] for n in pair.values())
        lines.append(f"- {row}: " + ", ".join(f"{k} {v}/40" for k, v in pair.items()) + f"; share "
                     f"{sum(pair.values()) / (40 * len(pair)):.3f}; {'at or above' if met else 'below'} the bar on both.")
    lines += ["", f"**Candidate** ({LABEL}): \"at least 6/40 on each of the cell's two items.\" **One-reading**: \"one carrier "
              "gets at least 36/40 on both items.\" **No carrier**: \"(d) exceeds 10/40 on either item.\" Per class and cell:",
              "", "| class | cell | candidates | one reading | no carrier |", "|---|---|---|---|---|"]
    lines += [f"| {cls} | {cell} | {', '.join(cc['candidates']) or '-'} | {cc['one_reading'] or '-'} | "
              f"{'yes' if cc['no_carrier'] else 'no'} |" for (_, cell), c in out["cells"].items() for cls, cc in c["classes"].items()]
    lines += ["", f"## Candidate table ({LABEL})", "", "`docs/research/presupposition-E1/candidate-table.json`, the file PS-2a "
              "and PS-6 read; `tableOk` held on it (Lean, `e1_score.table_ok`).", "",
              "| row | cell | candidates | status | notes |", "|---|---|---|---|---|"]
    lines += [f"| {row} | {cell} | {', '.join(c['cell']) or '-'} | {c['status']} | {' '.join(c['notes']) or '-'} |"
              for (row, cell), c in out["cells"].items()]
    lines += ["", f"## Answers per item ({LABEL})", "", "| item | a | b | c | d | e |", "|---|---|---|---|---|---|"]
    lines += [f"| {i['id']} | " + " | ".join(str(counts[i["id"]].get(k, "-")) for k in "abcde") + " |" for i in items]
    return "\n".join(lines) + "\n"


def generate(raw=RAW):
    """(table JSON text, results text) from the prereg file, the frozen items and the saved raw answers."""
    cfg, items, rows = config(), e1_items.load(), e1_stub.saved_table()
    records = load_records(raw)
    bound(items, cfg, records)
    counts, errors, malformed = tally(items, records, cfg["trials_per_item"])
    out = analyse(cfg, items, counts, rows)
    if not table_ok(out["table"]):
        raise ValueError("tableOk fails on the candidate table: a PS-E1 analysis error (spec 6)")
    calls = sum(r["model_calls"] for r in records.values())
    cw = sum(r["charged_cw"] + r["prior_cw"] for r in records.values())
    return (json.dumps(out["table"], indent=1) + "\n", results_md(cfg, items, counts, out, errors, malformed, calls, cw))


if __name__ == "__main__":
    table, results = generate()
    if sys.argv[1:] == ["--write"]:
        TABLE.write_text(table)
        RESULTS.write_text(results)
    elif sys.argv[1:] == ["--check"]:
        raise SystemExit(0 if (TABLE.read_text(), RESULTS.read_text()) == (table, results) else "saved results are stale")
    else:
        raise SystemExit("usage: e1_score.py --write|--check")
