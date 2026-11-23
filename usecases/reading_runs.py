"""Ambiguous text answered under each named reading, on a law's staged route (feature C). Outside VE core and the kernel.

A provision whose words allow two readings is written as a READING BLOCK in the law's reading table (TSV, below): exactly
two named readings, the source words that carry the ambiguity (quoted verbatim), each reading as data edits to the law's
rule table, and a "differ when" case. For every question the block lists, this module runs the law's own staged route
(its run.py main(), which Lean-checks every answer exactly as for a single-reading answer) once per reading, records each
answer under its reading's name, and prints it beside that reading's own rules in checked English. Nothing here decides
an answer: an answer is the law's Lean-checked run under one reading's rules; this module only pairs runs with readings,
and that pairing is guarded before any per-reading line is printed:
  words     the quoted words occur in the source verbatim, at word boundaries (runs of white space count as one space);
  hash      each run records the sha256 of the rule list it consumed (order-free); the two readings' hashes differ;
  diff      outside the rows a reading's own edits name, its rules equal the translation's byte for byte (a reading with
            no edits IS the translation); every consumed rule names its row; each reading has rules of its own;
  edits     every edit takes effect (a replace on a builder row matches in some run of the block);
  readback  each rule that differs between the readings renders to controlled English that parses back to itself;
  differ    the "differ when" case, run under both readings, gives Lean-checked answers that differ, each the one stated.
A failed guard prints no per-reading line: the question stays writer-ambiguous. Two readings never yield one answer
unless both give it ("Both readings written for ... give this answer"). An answer is decided only if the law's run gives
a value (not OPEN, UNSUPPORTED, ...); "N/A" (a question not asked) only if the table's law line names the condition
question and that question is decided under the same reading.

Table: "# law<TAB>{json}" names the use case ({"translation": module with rules() and MUTANTS, "slot": index of the
formula (or builder) in a table entry, optional "cases", "run", and "conditions": {answer key: [condition answer key,
words]}}); other "#" lines are provenance; then the header COLUMNS and two rows per block (readings A and B; every column
but reading, name, rules_en, edits and differ_expect is the same in both). edits: JSON list of {"op": "replace", "row",
"old", "new"} ("?x" strings in old are pattern variables; on a builder row old is matched in each ground formula the row
builds), {"op": "set"|"and", "row", "formula"}, {"op": "copy", "row": <new row>, "from"}, {"op": "drop", "row"}.
questions: comma list of <case id>/<answer key>. differ_case: {"id": "DW-...", "from": <case id>, "patch": [[op, path,
value], ...]} with op set|append|del; it runs in place of its base case, under the base case's id. differ_expect: {"q":
<answer key>, "answer": <answer under this reading>}.

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
LAW_KEYS = {"translation", "cases", "run", "slot", "conditions"}
UNDECIDED = {"OPEN", "UNSUPPORTED", "REFUSED", "UNKNOWN", "INCONSISTENT", "CANNOT", "ERROR", "N/A", ""}


class TableError(ValueError):
    pass


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def load_table(path):
    """-> (law config, {block id: {"A": row, "B": row}}). Refuses a block that is not exactly two named readings (F1)."""
    cfg, notes, rows, header = None, [], [], None
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        if line.startswith("# law\t"):
            if cfg is not None:
                raise TableError(f"line {n}: a second '# law' line")
            cfg = json.loads(line.split("\t", 1)[1])
            if set(cfg) - LAW_KEYS:
                raise TableError(f"line {n}: unknown law keys {sorted(set(cfg) - LAW_KEYS)} (no guard can be switched off)")
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
        if not _norm(a["name"]) or not _norm(b["name"]) or _norm(a["name"]).casefold() == _norm(b["name"]).casefold():
            raise TableError(f"{bid}: each reading needs its own name")
        if a["edits"] == b["edits"]:
            raise TableError(f"{bid}: the two readings have the same rules")
        if not a["questions"] or not _norm(a["words"]):
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
    """F4: the quoted words are a verbatim substring of the source, starting and ending at word boundaries."""
    w = _norm(words)
    lead, trail = (r"(?<!\w)" if w[:1].isalnum() else ""), (r"(?!\w)" if w[-1:].isalnum() else "")
    return bool(w) and re.search(lead + re.escape(w) + trail, _norm(source_text)) is not None


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


def transform(edits, slot, hits=None):
    """The reading's edits as a table transform (the law's MUTANTS hook: table -> table). hits[i] counts the matches of
    edit i (a replace on a builder row is only known to match when the row is built)."""
    hits = hits if hits is not None else [0] * len(edits)

    def builder_replace(fn, i, old, new):
        def build(*a, **kw):
            out = []
            for f in fn(*a, **kw):
                h = []
                out.append(_replace(f, old, new, h))
                hits[i] += len(h)
            return out
        return build

    def apply(table):
        as_list = isinstance(table, list)  # a list of entries keyed by their first cell (faa-medical)
        if as_list and len({e[0] for e in table}) != len(table):
            raise TableError("a list table with two entries of one key")
        t = {e[0]: e for e in table} if as_list else dict(table)
        for i, e in enumerate(edits):
            if e["op"] == "copy":
                new = int(e["row"]) if all(isinstance(k, int) for k in t) and str(e["row"]).isdigit() else e["row"]
                if new in t or str(new) in map(str, t):
                    raise TableError(f"copy: row {new!r} already exists")
                k0 = _row(t, e["from"])
                src = t[k0]
                t[new] = (new, *src[1:]) if src[0] == k0 else src  # an entry that names its own row
                hits[i] += 1
                continue
            k = _row(t, e["row"])
            if e["op"] == "drop":
                t.pop(k)
                hits[i] += 1
                continue
            entry = list(t[k])
            body = entry[slot]
            if e["op"] == "replace" and callable(body):
                entry[slot] = builder_replace(body, i, e["old"], e["new"])
            elif e["op"] == "replace":
                h = []
                entry[slot] = _replace(body, e["old"], e["new"], h)
                if not h:
                    raise TableError(f"row {k}: the replace edit matches nothing")
                hits[i] += len(h)
            elif e["op"] in ("set", "and") and not callable(body):
                entry[slot] = e["formula"] if e["op"] == "set" else ["and", body, e["formula"]]
                hits[i] += 1
            else:
                raise TableError(f"row {k}: op {e['op']} not allowed here")
            t[k] = tuple(entry)
        return list(t.values()) if as_list else t
    return apply


def edit_rows(edits):
    return {str(e["row"]) for e in edits}


def row_of(rule):
    """The table row a ground rule came from: its row or unit, else its id before a '.<conjunct number>' suffix."""
    if "row" in rule or "unit" in rule:
        return str(rule.get("row", rule.get("unit")))
    m = re.fullmatch(r"(.+)\.\d+", str(rule.get("id", "")))
    return m.group(1) if m else None


def _canon(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"), default=str)


def rules_sha256(rule_lists):
    """sha256 of the rules consumed, as a multiset (the order the law consumed them in does not count)."""
    return hashlib.sha256(json.dumps(sorted(_canon(r) for rs in rule_lists for r in rs)).encode()).hexdigest()


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
        self.cfg, self.key, self.consumed, self.envs = cfg, None, [], []
        orig, sig = self.T.rules, inspect.signature(self.T.rules)

        def rules(*a, **kw):
            bound = sig.bind(*a, **kw)
            if self.key is not None and bound.arguments.get("mutant") is None:
                bound.arguments["mutant"] = self.key
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
        """Index of the encoded case: by id, else by case (a case of several records: the one asking `key`)."""
        cs = self.K.CASES
        hits = [i for i, c in enumerate(cs) if c.get("id") == case_id] or [
            i for i, c in enumerate(cs) if c.get("case") == case_id]
        if len(hits) > 1 and key:
            asks = lambda c: json.dumps(key) in json.dumps(c.get("questions", c.get("qids", c)), default=str)  # noqa: E731
            hits = [i for i in hits if asks(cs[i])] or hits
        if len(hits) != 1:
            raise TableError(f"case {case_id}: {len(hits)} encoded cases match")
        return hits[0]

    def answers(self, case_id, edits, extra_case=None, lean=True, key=None, label="~reading", hits=None):
        """Run the law's main() on one case under `edits` (None: the translation as written) -> (answers, rules, env).
        extra_case: a patched copy of case `case_id`, run in its place under its id (laws key bridged data by case id).
        The law module is restored whatever happens (MUTANTS key, rules hook, case list)."""
        cases, at, saved = self.K.CASES, None, None
        try:
            self.consumed, self.envs = [], []
            if edits is not None:
                self.T.MUTANTS[label] = ("reading table edits", transform(edits, self.cfg["slot"], hits))
                self.key = label
            at = self.find(case_id, key)
            case_id = cases[at].get("id", case_id)
            if extra_case is not None:
                saved, cases[at] = cases[at], extra_case
            with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
                out = Path(d) / "run.json"
                self.run.main(["--cases", case_id, "--out", str(out)] + ([] if lean else ["--no-lean"]))
                data = json.loads(out.read_text())
        finally:
            if saved is not None:
                cases[at] = saved
            self.key = None
            self.T.MUTANTS.pop(label, None)
        recs = [r for r in data["records"] if case_id in (r.get("id"), r.get("case")) and "answers" in r]
        recs = [r for r in recs if key is None or key in r["answers"]] or recs
        if len(recs) != 1:
            raise TableError(f"case {case_id}: {len(recs)} records in the run file")
        return recs[0]["answers"], list(self.consumed), (self.envs[-1] if self.envs else None)


def decided(v):
    """A value the law's run gave (Lean-gated by the law): not an undecided marker, not rejected, not a bare N/A."""
    if isinstance(v, dict):
        if v.get("lean_rejected"):
            return False
        v = v.get("answer")
    if isinstance(v, list):
        return True
    return isinstance(v, str) and v.strip().upper() not in UNDECIDED


def resolve(answers, key, cfg):
    """(value, decided, words) for one answer key of one run. "N/A" is decided only when the law line names the question
    it depends on and that question is decided in the same run; the words name that condition."""
    v = answers.get(key)
    cond = cfg.get("conditions", {}).get(key)
    if v == "N/A" and cond and decided(answers.get(cond[0])):
        return v, True, f"not asked under this reading ({cond[1]} is certified false)"
    return v, decided(v), fmt(v)


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


def compare(block, base, runs):
    """Guards hash, diff and readback for one case -> (failures, {reading: [checked English of its own rules]})."""
    fails, flat = [], {r: [x for rs in runs[r][1] for x in rs] for r in ("A", "B")}
    base_flat = [x for rs in base for x in rs]
    if rules_sha256(runs["A"][1]) == rules_sha256(runs["B"][1]):
        fails.append("hash: both readings consumed the same rules")
    if any(row_of(x) is None for x in base_flat + flat["A"] + flat["B"]):
        fails.append("diff: a consumed rule names no row")
    for r in ("A", "B"):
        rows = edit_rows(block[r]["edits"])
        outside = lambda rs: sorted(_canon(x) for x in rs if row_of(x) not in rows)  # noqa: E731
        if outside(flat[r]) != outside(base_flat):
            fails.append(f"diff: reading {r} differs from the translation outside its rows {sorted(rows)}")
    english = {}
    for r, o in (("A", "B"), ("B", "A")):
        other = {_canon(x) for x in flat[o]}
        own = [x for x in flat[r] if _canon(x) not in other]
        if not own:
            fails.append(f"diff: reading {r} has no rules of its own")
        english[r] = [readback(runs[r][2], x) for x in own]
        if None in english[r]:
            fails.append(f"readback: a rule of reading {r} has no checked English wording")
    return fails, english


def fmt(v):
    if isinstance(v, list):
        return ", ".join(map(str, v)) if v else "none"
    if isinstance(v, dict):
        extra = ", ".join(f"{k} {v[k]}" for k in sorted(v) if k != "answer")
        return f"{v.get('answer')}" + (f" ({extra})" if extra else "")
    return str(v)


def report(block, said, english):
    """The lines a reader sees: both readings named with the quoted words, each answer under its own reading's rules.
    said: {reading: (value, decided, words)}."""
    cit = block["A"]["citation"]
    lines = [f'The text allows two readings of {cit}: "{block["A"]["words"]}".']
    for r in ("A", "B"):
        rules = "; ".join(e.rstrip(".") for e in english[r])
        lines.append(f'If {cit} means "{block[r]["name"]}" ({rules}): '
                     f'{said[r][2] if said[r][1] else "VE could not decide this"}.')
    if said["A"][1] and said["B"][1] and _canon(said["A"][0]) == _canon(said["B"][0]):
        lines.append(f"{said['A'][2]}. Both readings written for {cit} give this answer.")
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


def run_block(law, bid, block, source):
    """Every guard, then every question of the block under each reading -> result dict."""
    a = block["A"]
    out = {"citation": a["citation"], "words": a["words"], "guards": [], "questions": {}, "readback": True}
    if not words_in_source(a["words"], source):
        out["guards"] = ["words: the quoted words are not in the source verbatim"]
        out["questions"] = {q: {"status": "writer-ambiguous", "guards": out["guards"], "answers": {},
                                "report": [f"{a['citation']}: no per-reading answer (quoted words not in the source)."]}
                            for q in a["questions"]}
        return out
    hits = {r: [0] * len(block[r]["edits"]) for r in ("A", "B")}
    run = lambda cid, r, **kw: law.answers(cid, block[r]["edits"], label=f"~reading:{bid}:{r}", hits=hits[r], **kw)  # noqa: E731
    dc, exp = a["differ_case"], {r: block[r]["differ_expect"] for r in ("A", "B")}
    fails, cfg = [], law.cfg
    try:
        dq = exp["A"]["q"]
        case = _differ_case(law, dc, dq)
        base = law.answers(dc["from"], None, case, lean=False, key=dq)[1]
        runs = {r: run(dc["from"], r, extra_case=case, key=dq) for r in ("A", "B")}
        said = {r: resolve(runs[r][0], dq, cfg) for r in ("A", "B")}
        fails += compare(block, base, runs)[0]
        if not (said["A"][1] and said["B"][1] and _canon(said["A"][0]) != _canon(said["B"][0])):
            fails.append(f"differ: the differ-when case gives {[said[r][0] for r in 'AB']} (Lean-checked answers "
                         "that differ needed)")
        for r in ("A", "B"):
            if _canon(said[r][0]) != _canon(exp[r]["answer"]):
                fails.append(f"differ: reading {r} gives {said[r][0]!r}, the table states {exp[r]['answer']!r}")
        out["differ"] = {"case": dc["id"], "got": {r: said[r][0] for r in ("A", "B")},
                         "hash": {r: rules_sha256(runs[r][1]) for r in ("A", "B")}}
    except Exception as exc:  # noqa: BLE001 - any failure fails the guard
        fails.append(f"differ: {type(exc).__name__}: {exc}")
    for q in a["questions"]:
        cid, key = q.split("/", 1)
        try:
            base = law.answers(cid, None, lean=False, key=key)[1]
            runs = {r: run(cid, r, key=key) for r in ("A", "B")}
            said = {r: resolve(runs[r][0], key, cfg) for r in ("A", "B")}
            qfails, english = compare(block, base, runs)
            res = {"answers": {r: said[r][0] for r in ("A", "B")}, "said": {r: said[r][2] for r in ("A", "B")},
                   "decided": {r: said[r][1] for r in ("A", "B")}, "english": english,
                   "hash": {r: rules_sha256(runs[r][1]) for r in ("A", "B")}, "base_hash": rules_sha256(base)}
        except Exception as exc:  # noqa: BLE001
            qfails, res = [f"run: {type(exc).__name__}: {exc}"], {}
        res["guards"] = qfails
        out["questions"][q] = res
    for r in ("A", "B"):
        for i, n in enumerate(hits[r]):
            if n == 0:
                fails.append(f"edits: reading {r} edit {i} ({block[r]['edits'][i]['op']} row "
                             f"{block[r]['edits'][i]['row']}) never took effect")
    out["guards"] = fails
    for q, res in out["questions"].items():
        res["guards"] = fails + res["guards"]
        if res["guards"]:
            res.update(status="writer-ambiguous", answers={},
                       report=[f"{a['citation']}: no per-reading answer ({'; '.join(res['guards'])})."])
        else:
            res.update(status="per-reading", report=report(block, {r: (res["answers"][r], res["decided"][r],
                                                                       res["said"][r]) for r in ("A", "B")},
                                                           res["english"]))
    return out


def run_table(law_dir, table, source, out=None, blocks=None):
    cfg, all_blocks = load_table(table)
    src = Path(source).read_text(encoding="utf-8")
    law = Law(law_dir, cfg)
    result = {"table_sha256": hashlib.sha256(Path(table).read_bytes()).hexdigest(), "notes": cfg["notes"], "blocks": {}}
    for bid, block in all_blocks.items():
        if blocks is None or bid in blocks:
            result["blocks"][bid] = run_block(law, bid, block, src)
    if out:
        Path(out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--law-dir", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--blocks")
    args = ap.parse_args(argv)
    result = run_table(args.law_dir, args.table, args.source, args.out, args.blocks and args.blocks.split(","))
    for b in result["blocks"].values():
        for q, r in b["questions"].items():
            print(q, r["status"], *r.get("report", []), sep="\n  ")
    return result


if __name__ == "__main__":
    main()
