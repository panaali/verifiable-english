"""Mutant records of one document (plan 2d): structural (structural.py) and wording (wording.py), their edits, their
parse status, their equivalence and the declarations of usecases/<doc>/fidmech/equivalents.json.

- **Record.** `{"id", "document", "unit", "class", "op", "where", "edits": [{"file", "find", "replace",
  "file_sha256"}], "equivalent", "parse", "seed", "generator", "inputs_sha256"}`. Each `find` occurs exactly once in
  its file (as it is before the mutant), the edits of one file do not overlap, and `file_sha256` is that file's
  sha256. The harness enumerates every candidate, so `seed` is None.
- **Parse.** `ok`, or `stillborn` when an edited rule line, environment or PRECEDENCE literal does not parse (or parses
  to another rule than the edit made). Stillborn mutants are counted and listed, never scored.
- **Equivalence** is set only for structural mutants: `syntactic` (structural.syntactic, the rule file alone changed)
  or `declared:<reason>`. Wording mutants are never equivalent: `record` refuses one that says so.
- **Declarations.** An entry of equivalents.json is `{"id", "reason", "binding"}`. `binding` is the sha256 of the
  canonical JSON of the mutant's edits, fp-1 of its unit (tools/fidmech/fp1.py), facts.d1.ve's sha256, the
  PRECEDENCE literal and bindings.json's sha256; equivalents.json itself and the commit are not in it (a binding that
  held them could never be written). An entry whose binding differs is not applied and is reported `stale`.
"""
from __future__ import annotations

import ast as pyast
import difflib
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from tools.fidmech import fp1
from tools.fidmech import structural as S
from tools.fidmech.records import canonical

CLASSES = ("structural", "wording", "plant", "real-defect")
RECORD_KEYS = ("id", "document", "unit", "class", "op", "where", "edits", "equivalent", "parse", "seed", "generator",
               "inputs_sha256")
WHERE = ("rule", "act", "legend", "precedence", "unless")
EQUIVALENTS = "fidmech/equivalents.json"


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def record(document, unit, class_, op, where, edits, files, *, parse="ok", equivalent=None, n=1):
    """A checked mutant record; `files` {name: text} are the case's files the edits apply to."""
    if class_ not in CLASSES or where not in WHERE or parse not in ("ok", "stillborn"):
        raise ValueError(f"{unit}:{op}: class {class_!r}, where {where!r} or parse {parse!r} is not allowed")
    if equivalent is not None and class_ != "structural":
        raise ValueError(f"{unit}:{op}: a {class_} mutant is never equivalent")
    if not edits:
        raise ValueError(f"{unit}:{op}: no edit")
    for edit in edits:
        text = files[edit["file"]]
        if not edit["find"] or text.count(edit["find"]) != 1:
            raise ValueError(f"{unit}:{op}: `find` occurs {text.count(edit['find'])} times in {edit['file']}")
        if edit["file_sha256"] != sha256_text(text):
            raise ValueError(f"{unit}:{op}: file_sha256 of {edit['file']} is not the file's")
    apply_edits(files, edits)  # overlapping edits of one file are refused there
    return dict(zip(RECORD_KEYS, (f"{document}:{unit}:{op}:{n}", document, unit, class_, op, where, edits, equivalent,
                                  parse, None, S.GENERATOR, None)))


def apply_edits(files, edits):
    """{file: new text} of the files the edits change; each edit is placed where its `find` occurs in the original."""
    out = {}
    for name in dict.fromkeys(e["file"] for e in edits):
        text = files[name]
        spans = sorted((text.index(e["find"]), e) for e in edits if e["file"] == name)
        for (a, e), (b, _) in zip(spans, spans[1:]):
            if a + len(e["find"]) > b:
                raise ValueError(f"overlapping edits in {name}")
        for start, e in reversed(spans):
            text = text[:start] + e["replace"] + text[start + len(e["find"]):]
        out[name] = text
    return out


def line_edits(name, old, new):
    """The edits that turn `old` into `new`: changed line runs, each widened by whole lines until its `find` occurs once
    in `old`; runs whose widened lines meet are merged."""
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    codes = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()

    def to_b(x):
        for tag, i1, i2, j1, j2 in codes:
            if tag == "equal" and i1 <= x <= i2:
                return j1 + x - i1
            if x == i1:
                return j1
            if x == i2:
                return j2
        raise AssertionError(x)
    runs = [[i1, i2] for tag, i1, i2, _, _ in codes if tag != "equal"]
    while True:
        for run in runs:
            while not "".join(a[run[0]:run[1]]) or old.count("".join(a[run[0]:run[1]])) != 1:
                if run[0] == 0 and run[1] == len(a):
                    raise ValueError(f"{name}: no unique context for an edit")
                run[0], run[1] = max(run[0] - 1, 0), min(run[1] + 1, len(a))
        merged = []
        for run in runs:
            if merged and run[0] <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], run[1])
            else:
                merged.append(run)
        if len(merged) == len(runs):
            break
        runs = merged
    digest = sha256_text(old)
    return [{"file": name, "find": "".join(a[lo:hi]), "replace": "".join(b[to_b(lo):to_b(hi)]), "file_sha256": digest}
            for lo, hi in runs]


def rule_edit(files, block, line):
    """The edit that replaces one block's rule line (with its header when the line alone is not unique)."""
    text = files[S.RULES]
    find, replace = block.text, line
    if text.count(find) != 1:
        find, replace = block.header + "\n" + block.text, block.header + "\n" + line
    return [{"file": S.RULES, "find": find, "replace": replace, "file_sha256": sha256_text(text)}]


def _unquoted(header):
    return re.sub(r'"[^"]*"|“[^”]*”', "", header)


# ---- structural ---------------------------------------------------------------------------------------------------

def structural_mutants(document, files, env, selected, atoms):
    """(records, report) of every structural mutant of a document. `files` {name: text}: rules.d1.ve and the
    translation module; `env` the soft environment the rules are parsed in; `selected` and `atoms` the adapter's
    {item: rule ids} and {item: case-model atoms}."""
    blocks = S.rule_blocks(files[S.RULES])
    tname = S.translation_name(files)
    found, report = [], {"unrenderable": [], "undecided": [], "no-item": [], "no-guard-true": [],
                         "duplicates": Counter(), "no-op": Counter()}
    for index, block in enumerate(blocks):
        prefix = S.RULE_LINE.match(block.text).group(1)
        rule = S.parse(env, block.text)
        try:
            renders = S.same_edit(rule, S.parse(env, S.render(rule, env, prefix)))
        except S.REFUSED as error:
            report["undecided" if isinstance(error, S.CheckerUnavailable) else "unrenderable"].append(block.id)
            continue
        if not renders:  # VE's renderer cannot write this rule back: no op of it is written
            report["unrenderable"].append(block.id)
            continue
        sort = env.predicates[rule.core.predicate].arguments[0]
        true = S.guard_candidates(env, block.id, sort, selected, atoms)
        ops = S.ops_of(rule, env, exception=bool(S.EXCEPTION_HEADER.search(_unquoted(block.header))), true_atoms=true)
        if not any(op == "add-guard-true" for op, _, _ in ops):
            report["no-guard-true" if any(block.id in r for r in selected.values()) else "no-item"].append(block.id)
        for k, (op, where, edited) in enumerate(ops):
            found.append((S.KEEP_FIRST.index(op), index, k, block, op, where, edited, rule, prefix))
    source = files[tname]
    segment = pyast.get_source_segment(source, S._precedence_node(source))
    table = S.precedence(source)
    for k, (key, targets) in enumerate((key, t) for key, ts in table.items() for t in ts):
        new = {key2: tuple(t for t in ts if (key2, t) != (key, targets)) for key2, ts in table.items()}
        new = {key2: ts for key2, ts in new.items() if ts}
        found.append((S.KEEP_FIRST.index("drop-exception"), -1, k, key, "drop-exception", "precedence", (segment, new),
                      None, None))
    records, stillborn, seen, numbers = [], [], set(), Counter()
    for _, _, _, block, op, where, edited, rule, prefix in sorted(found, key=lambda f: f[:3]):
        if where == "precedence":
            segment, new = edited
            unit = block
            replacement = S.render_precedence(new)
            edits = [{"file": tname, "find": segment, "replace": replacement, "file_sha256": sha256_text(source)}]
            try:
                parsed = S.precedence(source.replace(segment, replacement, 1)) == new
                reason = None if parsed else "PRECEDENCE reads back as another table"
            except (SyntaxError, ValueError) as error:
                reason = f"PRECEDENCE does not parse: {error}"
            equivalent = None
        else:
            unit = block.id
            try:
                line = S.render(edited, env, prefix)
            except S.REFUSED as error:
                report["unrenderable"].append(f"{unit}:{op}: {type(error).__name__}: {error}"[:300])
                continue
            if line == block.text:
                report["no-op"][op] += 1
                continue
            edits = rule_edit(files, block, line)
            reason, equivalent = None, None
            try:
                parsed = S.parse(env, line)
                if not S.same_edit(edited, parsed):
                    reason = "the written line parses to another rule than the edit"
                elif S.syntactic(rule, parsed):
                    equivalent = "syntactic"
            except S.REFUSED as error:
                reason = _refusal(error)
        key = canonical(edits)
        if key in seen:
            report["duplicates"][op] += 1
            continue
        seen.add(key)
        numbers[unit, op] += 1
        rec = record(document, unit, "structural", op, where, edits, files, parse="stillborn" if reason else "ok",
                     equivalent=equivalent, n=numbers[unit, op])
        records.append(rec)
        if reason:
            stillborn.append({"id": rec["id"], "reason": reason})
    report["stillborn"] = stillborn
    order = {u: i for i, u in enumerate(table)} | {b.id: len(table) + i for i, b in enumerate(blocks)}
    records.sort(key=lambda r: (S.OPS.index(r["op"]), order[r["unit"]], r["id"]))
    return records, report


def rule_equivalence(files, env, edits):
    """`syntactic` when the edits change the rule file alone and every rule line they change parses to a rule equal to
    the original's after canonicalisation (structural.syntactic); otherwise None."""
    if not edits or any(e["file"] != S.RULES for e in edits):
        return None
    old = {b.id: b.text for b in S.rule_blocks(files[S.RULES])}
    new = {b.id: b.text for b in S.rule_blocks(apply_edits(files, edits)[S.RULES])}
    changed = [i for i in old if old[i] != new.get(i)]
    if set(old) != set(new) or not changed:
        return None
    try:
        same = all(S.syntactic(S.parse(env, old[i]), S.parse(env, new[i])) for i in changed)
    except S.REFUSED:  # a line VE refuses, or does not answer, is no equivalent
        return None
    return "syntactic" if same else None


def scorable(records):
    """The records a kill table scores: never a stillborn one."""
    return [r for r in records if r["parse"] == "ok"]


# ---- wording ------------------------------------------------------------------------------------------------------

def wording_mutants(document, files, actors, *, parse_env=None):
    """(records, report) of every wording candidate of every rule-block unit (wording.harness_candidates), with
    the case's actors (actors.json). `parse_env(env_json_text)` builds the soft environment a mutant's rules are
    parsed in; without it every record is `ok` unchecked and the report says so."""
    from tools.fidmech import wording as W
    blocks = W._blocks(files.get(S.RULES, ""))[0]
    records, stillborn, seen, numbers = [], [], set(), Counter()
    report = {"duplicates": Counter(), "parse_checked": parse_env is not None}
    for unit in blocks:
        for kind, where, pred, old, new in W.harness_candidates(files, unit, actors):
            changed = W.apply(files, [{"unit": unit, "kind": kind, "where": where, "pred": pred, "old": old,
                                       "new": new}])
            edits = [e for name in sorted(changed) if changed[name] != files[name]
                     for e in line_edits(name, files[name], changed[name])]
            if not edits:
                continue
            key = canonical(edits)
            if key in seen:
                report["duplicates"][kind] += 1
                continue
            seen.add(key)
            reason = _wording_stillborn(files, changed, parse_env, pred) if parse_env else None
            numbers[unit, kind] += 1
            rec = record(document, unit, "wording", kind, where, edits, files,
                         parse="stillborn" if reason else "ok", n=numbers[unit, kind])
            records.append(rec)
            if reason:
                stillborn.append({"id": rec["id"], "reason": reason})
    report["stillborn"] = stillborn
    return records, report


def _wording_stillborn(files, changed, parse_env, pred):
    """None, or why the mutated environment or a rule line it touches (changed, or using `pred`) does not parse."""
    from tools.fidmech import wording as W
    try:
        env = parse_env(changed.get(S.ENVIRONMENT, files[S.ENVIRONMENT]))
        new_rules = {b.id: b.text for b in S.rule_blocks(changed.get(S.RULES, files[S.RULES]))}
        old_env = json.loads(files[S.ENVIRONMENT])
        for block in S.rule_blocks(files[S.RULES]):
            if new_rules.get(block.id) != block.text or pred in W._used(block.text, old_env):
                S.parse(env, new_rules[block.id])
    except S.REFUSED as error:
        return _refusal(error)
    return None


def _refusal(error):
    """The stillborn reason of a refused (or unanswered) parse; an unanswered one is marked `undecided`: it is not
    scored either way, and the report lists it apart from the lines VE refused."""
    text = f"{type(error).__name__}: {error}"[:300]
    return ("undecided: " + text) if isinstance(error, S.CheckerUnavailable) else text


def counts(records, report):
    """{op: {"mutants", "ok", "stillborn", "syntactic", "duplicates"}} in op order."""
    out = {}
    for r in records:
        row = out.setdefault(r["op"], Counter())
        row["mutants"] += 1
        row[r["parse"]] += 1
        row["syntactic"] += r["equivalent"] == "syntactic"
    for op, n in report.get("duplicates", {}).items():
        out.setdefault(op, Counter())["duplicates"] += n
    order = list(S.OPS) + ["actor", "qualifier", "quantity", "attachment"]
    return {op: {k: out[op][k] for k in ("mutants", "ok", "stillborn", "syntactic", "duplicates")}
            for op in sorted(out, key=lambda o: order.index(o) if o in order else len(order))}


# ---- declarations -------------------------------------------------------------------------------------------------

def binding_inputs(case_dir):
    """What a declaration rests on besides its edits: fp-1 per unit, facts.d1.ve, PRECEDENCE and bindings.json."""
    case_dir = Path(case_dir)
    files = fp1.semantic_files_tree(case_dir)
    names = [n for n in files if n.endswith("translation.py")]
    table = S.precedence(files[names[0]].decode("utf-8")) if len(names) == 1 else None
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None  # noqa: E731
    return {"fp1": fp1.fingerprints_of(files), "facts_sha256": sha(case_dir / S.FACTS),
            "precedence": sorted([k, list(v)] for k, v in table.items()) if table is not None else None,
            "bindings_sha256": sha(case_dir / S.BINDINGS)}


def binding(rec, inputs):
    """The sha256 a declaration of `rec` is bound to (`inputs` from binding_inputs)."""
    return hashlib.sha256(canonical({"edits": rec["edits"], "fp1": inputs["fp1"].get(rec["unit"]),
                                     "facts_sha256": inputs["facts_sha256"], "precedence": inputs["precedence"],
                                     "bindings_sha256": inputs["bindings_sha256"]})).hexdigest()


def load_declarations(path):
    """The entries of an equivalents.json; a malformed entry is refused."""
    entries = json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).is_file() else []
    if not isinstance(entries, list):
        raise ValueError(f"{path}: not a list")
    for e in entries:
        if (not isinstance(e, dict) or set(e) != {"id", "reason", "binding"}
                or not all(isinstance(e[k], str) and e[k].strip() for k in e)
                or not re.fullmatch(r"[0-9a-f]{64}", e["binding"])):
            raise ValueError(f"{path}: malformed declaration {e!r}")
    return entries


def apply_declarations(records, entries, inputs):
    """(records with each bound declaration applied, report). A declaration applies only to a structural mutant
    with no equivalence yet, and only while its binding matches; otherwise it is reported and not applied."""
    by_id = {r["id"]: r for r in records}
    report = {k: [] for k in ("applied", "stale", "unknown", "not-structural", "already-equivalent")}
    out = {r["id"]: r for r in records}
    for e in entries:
        rec = by_id.get(e["id"])
        if rec is None:
            report["unknown"].append(e["id"])
        elif rec["class"] != "structural":
            report["not-structural"].append(e["id"])
        elif rec["equivalent"] is not None:
            report["already-equivalent"].append(e["id"])
        elif binding(rec, inputs) != e["binding"]:
            report["stale"].append(e["id"])
        else:
            out[e["id"]] = {**rec, "equivalent": "declared:" + e["reason"]}
            report["applied"].append(e["id"])
    return [out[r["id"]] for r in records], report


# ---- one document in a worktree -----------------------------------------------------------------------------------

def case_files(case_dir):
    """{name: text} of the case files the generators read and edit: the rules, the environment, the vocabulary and
    the translation module."""
    return {f.name: f.read_text(encoding="utf-8") for f in sorted(Path(case_dir).iterdir()) if f.is_file() and (
        f.name in (S.RULES, S.ENVIRONMENT) or f.name.endswith("vocabulary.py") or f.name.endswith("translation.py"))}


def selection(worktree, document):
    """The adapter's {item: rule ids} and {item: case-model atoms} of the committed results.json, the atoms read
    through the worktree's run.py (imported, never run)."""
    from tools.fidmech import adapters, worker
    worktree = Path(worktree)
    results = json.loads((worktree / "usecases" / document / "results.json").read_text(encoding="utf-8"))
    roots = (worktree / "usecases",)
    saved = list(sys.path)
    worker.purge(roots)
    try:
        projection = adapters.project(document, results, worker.import_run(worktree, document))
    finally:
        sys.path[:] = saved
        worker.purge(roots)
    return projection.rules, projection.atoms


def document_mutants(worktree, document, *, kinds=("structural", "wording"), parse_wording=True):
    """(records, report) of one document: every mutant of `kinds`, the declarations applied and inputs_sha256 set
    (tools/fidmech/records.py collect_inputs, with the generator version and every mutant id and edits)."""
    from types import SimpleNamespace

    from ve.softnorms import SoftEnvironment
    from tools.fidmech import records as R
    from tools.fidmech import wording as W
    case_dir = Path(worktree) / "usecases" / document
    files = case_files(case_dir)
    env = SoftEnvironment(json.loads(files[S.ENVIRONMENT]))
    records, report = [], {}
    if "structural" in kinds:
        selected, atoms = selection(worktree, document)
        found, report["structural"] = structural_mutants(document, files, env, selected, atoms)
        records += found
    if "wording" in kinds:
        actors = W.load_actors(case_dir / "fidmech" / "actors.json")
        parse_env = (lambda text: SoftEnvironment(json.loads(text))) if parse_wording else None
        found, report["wording"] = wording_mutants(document, files, actors, parse_env=parse_env)
        records += found
    records, report["declarations"] = apply_declarations(
        records, load_declarations(Path(worktree) / "usecases" / document / EQUIVALENTS), binding_inputs(case_dir))
    digest = R.inputs_sha256(R.collect_inputs(worktree, document, generator_version=S.GENERATOR,
                                              mutants=[SimpleNamespace(id=r["id"], edits=r["edits"]) for r in records]))
    return [{**r, "inputs_sha256": digest} for r in records], report


def to_worker(rec, case_files_text):
    """A record as the worker's mutant: {path under usecases/: the edited file's text}."""
    from tools.fidmech.worker import Mutant
    return Mutant(rec["id"], {f"{rec['document']}/{name}": text
                              for name, text in apply_edits(case_files_text, rec["edits"]).items()})
