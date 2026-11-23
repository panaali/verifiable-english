"""Ambiguous text answered under each named reading, on a law's staged route (feature C). Outside VE core and the kernel.

A provision whose words allow two readings is written as a READING BLOCK in the law's reading table (TSV, below): exactly
two named readings, the source words that carry the ambiguity (quoted verbatim), each reading as data edits to the law's
rule table, and a "differ when" case. For every question the block lists, this module runs the law's own staged route
(its run.py main(), which Lean-checks every answer exactly as for a single-reading answer) once per reading, records each
answer under its reading's name, and prints it beside that reading's own rules in checked English. Nothing here decides
an answer: an answer is the law's Lean-checked run under one reading's rules; this module only pairs runs with readings,
and that pairing is guarded before any per-reading line is printed:
  hash      each run records the sha256 of the rule list it consumed; the two readings' hashes must differ;
  diff      outside the rows the block's edits name, each reading's rules equal the law's translation byte for byte;
  readback  each rule that differs between the readings renders to controlled English that parses back to itself;
  differ    the "differ when" case, run under both readings, gives Lean-checked answers that differ, each the one stated.
A failed guard prints no per-reading line: the question stays writer-ambiguous. Two readings never yield one answer
unless both give it ("Both readings written for ... give this answer").

Table: "# law<TAB>{json}" names the use case ({"translation": module with rules() and MUTANTS, "slot": index of the
formula (or builder) in a table entry, "readback": true}); other "#" lines are provenance; then
the header COLUMNS and two rows per block (readings A and B; every column but reading, name, rules_en, edits and
differ_expect is the same in both). edits: JSON list of {"op": "replace", "row", "old", "new"} ("?x" strings in old are
pattern variables), {"op": "set"|"and", "row", "formula"}, {"op": "copy", "row", "from"}, {"op": "drop", "row"}.
questions: comma list of <case id>/<answer key>. differ_case: {"id": "DW-...", "from": <case id>, "patch": [[op, path,
value], ...]} with op set|append|del. differ_expect: {"q": <answer key>, "answer": <answer under this reading>}.

Usage: python -B usecases/reading_runs.py --law-dir <worktree>/usecases/<law> --table <law>.tsv --source <source.txt>
       --out <result.json> [--blocks B1,B2]
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib
import inspect
import io
import json
import re
import sys
import tempfile
from pathlib import Path

COLUMNS = ("block", "citation", "words", "reading", "name", "rules_en", "edits", "questions", "differ_case",
           "differ_expect")
PER_READING = ("reading", "name", "rules_en", "edits", "differ_expect")
KEY = "~reading"
UNDECIDED = {"OPEN", "UNSUPPORTED", "REFUSED", "UNKNOWN"}


class TableError(ValueError):
    pass


def load_table(path):
    """-> (law config, {block id: {"A": row, "B": row}}). Refuses a block that is not exactly two named readings (F1)."""
    cfg, notes, rows, header = None, [], [], None
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("# law\t"):
            cfg = json.loads(line.split("\t", 1)[1])
        elif line.startswith("#"):
            notes.append(line)
        elif header is None:
            header = tuple(line.split("\t"))
            if header != COLUMNS:
                raise TableError(f"line {n}: header must be {COLUMNS}")
        else:
            cells = line.split("\t")
            if len(cells) != len(COLUMNS):
                raise TableError(f"line {n}: {len(cells)} cells, want {len(COLUMNS)}")
            row = dict(zip(COLUMNS, cells))
            for c in ("edits", "differ_case", "differ_expect"):
                row[c] = json.loads(row[c])
            row["questions"] = [q.strip() for q in row["questions"].split(",") if q.strip()]
            rows.append(row)
    if cfg is None:
        raise TableError("no '# law' line")
    blocks, seen_q = {}, {}
    for row in rows:
        blocks.setdefault(row["block"], []).append(row)
    out = {}
    for bid, rs in blocks.items():
        if sorted(r["reading"] for r in rs) != ["A", "B"]:
            raise TableError(f"{bid}: a block has exactly two readings, A and B (got {[r['reading'] for r in rs]})")
        a, b = sorted(rs, key=lambda r: r["reading"])
        for c in COLUMNS:
            if c not in PER_READING and a[c] != b[c]:
                raise TableError(f"{bid}: column {c} differs between the readings")
        if not a["name"].strip() or not b["name"].strip() or a["name"] == b["name"]:
            raise TableError(f"{bid}: each reading needs its own name")
        if a["edits"] == b["edits"]:
            raise TableError(f"{bid}: the two readings have the same rules")
        if not a["questions"] or not a["words"].strip():
            raise TableError(f"{bid}: no questions or no quoted words")
        if not str(a["differ_case"].get("id", "")).startswith("DW-"):
            raise TableError(f"{bid}: the differ-when case needs an id starting DW-")
        if a["differ_expect"]["q"] != b["differ_expect"]["q"] or a["differ_expect"]["answer"] == b["differ_expect"]["answer"]:
            raise TableError(f"{bid}: the differ-when case must state one question with a different result per reading")
        for q in a["questions"]:
            if q in seen_q:
                raise TableError(f"{bid}: question {q} is already in block {seen_q[q]} (one block per question, F1)")
            seen_q[q] = bid
        out[bid] = {"A": a, "B": b}
    return {**cfg, "notes": notes}, out


def words_in_source(words, source_text):
    """F4: the quoted words are a verbatim substring of the source (runs of white space count as one space)."""
    norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731
    return norm(words) in norm(source_text)


def _match(p, t, b):
    if isinstance(p, str) and p.startswith("?"):
        if p in b:
            return b[p] == t
        b[p] = t
        return True
    if isinstance(p, list):
        return isinstance(t, list) and len(p) == len(t) and all(_match(x, y, b) for x, y in zip(p, t))
    return p == t


def _subst(t, b):
    if isinstance(t, str) and t.startswith("?"):
        return b[t]
    return [_subst(x, b) for x in t] if isinstance(t, list) else t


def _replace(f, old, new, hits):
    b = {}
    if _match(old, f, b):
        hits.append(1)
        return _subst(new, b)
    return [_replace(x, old, new, hits) for x in f] if isinstance(f, list) else f


def _row(table, r):
    for k in (r, str(r), int(r) if str(r).lstrip("-").isdigit() else None):
        if k in table:
            return k
    raise TableError(f"row {r!r} is not in the law's table")


def transform(edits, slot):
    """The reading's edits as a table transform (the law's MUTANTS hook: table -> table)."""
    def apply(table):
        as_list = isinstance(table, list)  # a list of entries keyed by their first cell (faa-medical)
        t = {e[0]: e for e in table} if as_list else dict(table)
        for e in edits:
            if e["op"] == "copy":
                src = t[_row(t, e["from"])]
                t[e["row"]] = (e["row"], *src[1:]) if src[0] == e["from"] else src  # an entry that names its row
                continue
            k = _row(t, e["row"])
            if e["op"] == "drop":
                t.pop(k)
                continue
            entry = list(t[k])
            body = entry[slot]
            if e["op"] == "replace" and callable(body):
                entry[slot] = (lambda fn, o, n: lambda *a, **kw: [_replace(f, o, n, []) for f in fn(*a, **kw)])(
                    body, e["old"], e["new"])
            elif e["op"] == "replace":
                hits = []
                entry[slot] = _replace(body, e["old"], e["new"], hits)
                if not hits:
                    raise TableError(f"row {k}: the replace edit matches nothing")
            elif e["op"] in ("set", "and") and not callable(body):
                entry[slot] = e["formula"] if e["op"] == "set" else ["and", body, e["formula"]]
            else:
                raise TableError(f"row {k}: op {e['op']} not allowed here")
            t[k] = tuple(entry)
        return list(t.values()) if as_list else t
    return apply


def declared_rows(block):
    return {str(e["row"]) for r in ("A", "B") for e in block[r]["edits"]}


def row_of(rule):
    """The table row a ground rule came from: its row or unit, else its id up to the last dot."""
    return str(rule.get("row", rule.get("unit", str(rule.get("id", "")).rsplit(".", 1)[0])))


def _canon(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"), default=str)


def rules_sha256(rule_lists):
    return hashlib.sha256(json.dumps([[_canon(r) for r in rs] for rs in rule_lists]).encode()).hexdigest()


class Law:
    """One law's use case, loaded once per process; runs its own main() under a reading's edits (or none)."""

    def __init__(self, law_dir, cfg):
        self.dir = Path(law_dir).resolve()
        for p in (str(self.dir.parents[1]), str(self.dir)):
            if p not in sys.path:
                sys.path.insert(0, p)
        self.T = importlib.import_module(cfg.get("translation", "translation"))
        self.K = importlib.import_module(cfg.get("cases", "cases"))
        self.run = importlib.import_module(cfg.get("run", "run"))
        self.cfg, self.edits, self.consumed, self.envs = cfg, None, [], []
        orig, sig = self.T.rules, inspect.signature(self.T.rules)

        def rules(*a, **kw):
            bound = sig.bind(*a, **kw)
            if self.edits is not None and bound.arguments.get("mutant") is None:
                bound.arguments["mutant"] = KEY
            out = orig(*bound.args, **bound.kwargs)
            self.consumed.append(copy.deepcopy(out))
            return out
        self.T.rules = rules
        env_cls = self.run.Environment

        def capture(raw, *a, **kw):
            self.envs.append(raw)
            return env_cls(raw, *a, **kw)
        self.run.Environment = capture

    def find(self, case_id, key=None):
        """Index of the encoded case: by id, else by case (a case of several records: the one that holds `key`)."""
        cs = self.K.CASES
        hits = [i for i, c in enumerate(cs) if c.get("id") == case_id] or [
            i for i, c in enumerate(cs) if c.get("case") == case_id]
        if len(hits) > 1 and key:
            hits = [i for i in hits if json.dumps(key) in json.dumps(cs[i], default=str)] or hits
        if len(hits) != 1:
            raise TableError(f"case {case_id}: {len(hits)} encoded cases match")
        return hits[0]

    def answers(self, case_id, edits, extra_case=None, lean=True, key=None):
        """Run the law's main() on one case under `edits` (None: the translation as written) -> (answers, rules, env).
        extra_case: a patched copy of case `case_id`, run in its place under its id (laws key bridged data by case id)."""
        self.T.MUTANTS[KEY] = ("reading table edits", transform(edits or [], self.cfg["slot"]))
        self.edits, self.consumed, self.envs = edits, [], []
        cases = self.K.CASES
        at = self.find(case_id, key)
        case_id = cases[at].get("id", case_id)
        if extra_case is not None:
            saved, cases[at] = cases[at], extra_case
        try:
            with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
                out = Path(d) / "run.json"
                self.run.main(["--cases", case_id, "--out", str(out)] + ([] if lean else ["--no-lean"]))
                data = json.loads(out.read_text())
        finally:
            if extra_case is not None:
                cases[at] = saved
            self.edits = None
            self.T.MUTANTS.pop(KEY, None)
        recs = [r for r in data["records"] if case_id in (r.get("id"), r.get("case")) and "answers" in r]
        recs = [r for r in recs if key is None or key in r["answers"]] or recs
        if len(recs) != 1:
            raise TableError(f"case {case_id}: {len(recs)} records in the run file")
        return recs[0]["answers"], list(self.consumed), (self.envs[-1] if self.envs else None)


def decided(v):
    a = v.get("answer") if isinstance(v, dict) else v
    return a is not None and a not in UNDECIDED and not (isinstance(v, dict) and v.get("lean_rejected"))


def readback(env_raw, rule):
    """Checked English: the rule's controlled-English wording, if it parses back to exactly the rule, else None."""
    from ve.environment import Environment
    from ve.surface.time import parse_w6_sentence, render_w6_sentence
    from ve.units import elaborate_quantity
    try:
        env = Environment(env_raw)
        can, _ = elaborate_quantity(env, {"format": "ve-quantity@1", "formula": rule["formula"]})
        s = render_w6_sentence(env, can)
        return s if parse_w6_sentence(env, s) == can else None
    except Exception:  # noqa: BLE001 - any failure means no checked wording
        return None


def compare(block, base, runs, check_readback=True):
    """Guards hash, diff and readback for one case -> (failures, {reading: [checked English of its own rules]})."""
    rows, fails = declared_rows(block), []
    flat = {r: [x for rs in runs[r][1] for x in rs] for r in ("A", "B")}
    if rules_sha256(runs["A"][1]) == rules_sha256(runs["B"][1]):
        fails.append("hash: both readings consumed the same rules")
    outside = lambda rs: sorted(_canon(x) for x in rs if row_of(x) not in rows)  # noqa: E731
    base_out = outside(x for rs in base for x in rs)
    for r in ("A", "B"):
        if outside(flat[r]) != base_out:
            fails.append(f"diff: reading {r} changes rules outside rows {sorted(rows)}")
    own, english = {}, {}
    for r, o in (("A", "B"), ("B", "A")):
        other = {_canon(x) for x in flat[o]}
        own[r] = [x for x in flat[r] if _canon(x) not in other]
        english[r] = [readback(runs[r][2], x) if check_readback else json.dumps(x["formula"]) for x in own[r]]
        if None in english[r]:
            fails.append(f"readback: a rule of reading {r} has no checked English wording")
    return fails, english


def fmt(v):
    if isinstance(v, list):
        return ", ".join(map(str, v)) if v else "none"
    if isinstance(v, dict):
        extra = ", ".join(f"{k} {v[k]}" for k in sorted(v) if k != "answer")
        return f"{v.get('answer')}" + (f" ({extra})" if extra else "")
    return "not asked under this reading" if v == "N/A" else str(v)


def report(block, ans, english):
    """The lines a reader sees: both readings named with the quoted words, each answer under its own reading's rules."""
    a, cit = block["A"], block["A"]["citation"]
    lines = [f'The text allows two readings of {cit}: "{a["words"]}".']
    for r in ("A", "B"):
        said = fmt(ans[r]) if decided(ans[r]) else "VE could not decide this"
        lines.append(f'If {cit} means "{block[r]["name"]}" ({"; ".join(e.rstrip(".") for e in english[r])}): {said}.')
    if decided(ans["A"]) and decided(ans["B"]) and _canon(ans["A"]) == _canon(ans["B"]):
        lines.append(f"{fmt(ans['A'])}. Both readings written for {cit} give this answer.")
    else:
        lines.append("The readings do not give one answer; VE gives none without naming the reading.")
    return lines


def _differ_case(law, dc, key):
    case = copy.deepcopy(law.K.CASES[law.find(dc["from"], key)])
    for op, path, *val in dc["patch"]:
        *head, last = path
        node = case
        for p in head:
            node = node[p]
        if op == "set":
            node[last] = val[0]
        elif op == "append":
            node[last].append(val[0])
        elif op == "del":
            del node[last]
        else:
            raise TableError(f"differ-when: patch op {op}")
    return case


def run_block(law, block, check_readback=True):
    """Every guard, then every question of the block under each reading -> result dict."""
    out = {"citation": block["A"]["citation"], "words": block["A"]["words"], "guards": [], "questions": {}}
    dc, exp = block["A"]["differ_case"], {r: block[r]["differ_expect"] for r in ("A", "B")}
    try:
        dq = exp["A"]["q"]
        case = _differ_case(law, dc, dq)
        base = law.answers(dc["from"], None, case, lean=False, key=dq)[1]
        runs = {r: law.answers(dc["from"], block[r]["edits"], case, key=dq) for r in ("A", "B")}
        got = {r: runs[r][0].get(exp[r]["q"]) for r in ("A", "B")}
        fails, _ = compare(block, base, runs, check_readback)
        if not (decided(got["A"]) and decided(got["B"]) and _canon(got["A"]) != _canon(got["B"])):
            fails.append(f"differ: the differ-when case gives {got} (Lean-checked answers that differ needed)")
        for r in ("A", "B"):
            if _canon(got[r]) != _canon(exp[r]["answer"]):
                fails.append(f"differ: reading {r} gives {got[r]!r}, the table states {exp[r]['answer']!r}")
        out["differ"] = {"case": dc["id"], "got": got}
    except (TableError, KeyError, IndexError, TypeError) as exc:
        fails = [f"differ: {type(exc).__name__}: {exc}"]
    out["guards"] = fails
    for q in block["A"]["questions"]:
        cid, key = q.split("/", 1)
        try:
            base = law.answers(cid, None, lean=False, key=key)[1]
            runs = {r: law.answers(cid, block[r]["edits"], key=key) for r in ("A", "B")}
            ans = {r: runs[r][0].get(key) for r in ("A", "B")}
            qfails, english = compare(block, base, runs, check_readback)
        except (TableError, KeyError, IndexError, TypeError) as exc:
            ans, qfails, english = {}, [f"run: {type(exc).__name__}: {exc}"], {}
        res = {"guards": fails + qfails, "hash": {r: rules_sha256(runs[r][1]) for r in ("A", "B")} if ans else {}}
        if res["guards"]:
            res.update(status="writer-ambiguous", answers={},
                       report=[f"{block['A']['citation']}: no per-reading answer ({'; '.join(res['guards'])})."])
        else:
            res.update(status="per-reading", answers=ans, english=english, report=report(block, ans, english))
        out["questions"][q] = res
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--law-dir", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--blocks")
    args = ap.parse_args(argv)
    cfg, blocks = load_table(args.table)
    source = Path(args.source).read_text(encoding="utf-8")
    law = Law(args.law_dir, cfg)
    result = {"table_sha256": hashlib.sha256(Path(args.table).read_bytes()).hexdigest(), "notes": cfg["notes"], "blocks": {}}
    for bid, block in blocks.items():
        if args.blocks and bid not in args.blocks.split(","):
            continue
        if not words_in_source(block["A"]["words"], source):
            result["blocks"][bid] = {"guards": ["words: the quoted words are not in the source verbatim"],
                                     "questions": {q: {"status": "writer-ambiguous"} for q in block["A"]["questions"]}}
            continue
        result["blocks"][bid] = run_block(law, block, cfg.get("readback", True))
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for bid, b in result["blocks"].items():
        for q, r in b["questions"].items():
            print(q, r["status"], *r.get("report", []), sep="\n  ")
    return result


if __name__ == "__main__":
    main()
