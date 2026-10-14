"""DF-E3: colliding rule pairs where one guard strictly implies the other and no precedence or rank is written.

    uv run python research/defeasible/specificity_pairs.py

The operational definition is docs/research/defeasible-phase1.md 1.5, committed before this ran. Rules are read with
VE's own parsers and decoders (unchanged); guards stay in the wire form, and implication is decided by a truth table
when both guards are quantifier-free with no defined predicate, else by VE's tableau (a certificate, or unknown).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from common import CONSTITUTION_RUN, ROOT, UDHR_RUN, front_matter, sha256, write_json

sys.path.insert(0, str(ROOT))

from ve.ast import formula_from_data  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.norm_english import parse_english  # noqa: E402

CONNECTIVES = {"top", "bottom", "and", "or", "not", "implies", "iff"}
QUANTIFIERS = {"forall", "exists"}
USECASES = ROOT / "usecases"


class Rule:
    def __init__(self, data, *, origin, condition=()):
        self.name = data["name"]
        self.predicate = data["predicate"]
        self.sign = data["sign"]
        self.guard = data["guard"]
        self.unless = data.get("unless", [])
        self.over = tuple(data.get("over", ()))
        self.mode = data.get("mode", "strict")
        self.rank = data.get("rank")
        self.origin = origin
        # Rules are present together when their conditions agree: a reading-set id maps to one choice.
        self.condition = tuple(condition)

    def key(self):
        return json.dumps([self.predicate, self.sign, self.guard, self.unless], sort_keys=True)


class Corpus:
    def __init__(self, name, env_data, rules, *, soft=None, note=""):
        self.name = name
        self.env_data = env_data
        self.rules = rules
        self.soft = soft or {}
        self.note = note


# ---------------------------------------------------------------- loaders

def _norm_of(content):
    return content.get("norm") if isinstance(content, dict) else None


def translation(name, path):
    meta = front_matter(path)
    rules = []
    for unit in meta["units"]:
        norm = _norm_of(unit.get("content"))
        if unit.get("kind") == "norm" and norm:
            rules.append(Rule(norm, origin=unit["id"]))
    for reading_set in meta.get("reading_sets", []):
        for reading in reading_set.get("readings", []):
            norm = _norm_of(reading.get("content"))
            if norm:
                rules.append(Rule(norm, origin=f"{reading_set['id']}:{reading['id']}",
                                  condition=[(reading_set["id"], reading["id"])]))
    return Corpus(name, meta["environment"], rules, soft=meta["environment"]["vocabulary"].get("soft"))


def _manifest_env(directory, text_name, manifest_name, candidates):
    manifest = json.loads((directory / manifest_name).read_text())
    for candidate in candidates:
        data = json.loads((directory / candidate).read_text())
        data = data.get("environment", data)
        if Environment(data).environment_id == manifest["environment_id"]:
            return data, manifest
    raise SystemExit(f"{directory.name}: no environment matches {manifest_name}")


def english(name, directory, text_name, manifest_name, candidates):
    env_data, manifest = _manifest_env(directory, text_name, manifest_name, candidates)
    document = parse_english(Environment(env_data), (directory / text_name).read_text(), manifest)
    rules = [Rule(r.to_dict()["norm"], origin=f"{text_name}:{r.name}") for r in document.rules]
    return Corpus(name, env_data, rules, note=f"{text_name} with {manifest_name}")


def safety_framework():
    sys.path.insert(0, str(USECASES / "safety-framework"))
    import translation as T  # the use case's own loader
    import vocabulary as V
    env_data = V.environment("deny")
    rules = []
    for block in T.rule_blocks():
        data = json.loads(T.parsed_rule(block.id))
        data["over"] = list(T.PRECEDENCE.get(block.id, ()))
        rules.append(Rule(data, origin=block.id, condition=block.when))
    return Corpus("safety-framework", env_data, rules, soft=env_data["vocabulary"].get("soft"),
                  note="rules.d1.ve blocks with translation.PRECEDENCE; co-present when their reading choices agree")


def eligibility():
    env_data = json.loads((USECASES / "eligibility/environment.json").read_text())
    data = json.loads((USECASES / "eligibility/rules.json").read_text())
    norms = [r for r in data["rules"] if "norm" in r or "predicate" in r and "sign" in r]
    return Corpus("eligibility", env_data, [Rule(n.get("norm", n), origin=n.get("id", "?")) for n in norms],
                  note=f"profiles {env_data['profiles']}; {len(data['rules'])} rules of format {data['format']}, "
                       f"{len(norms)} of them norms")


def corpora():
    yield translation("constitution", CONSTITUTION_RUN / "translation.ve.md")
    for part in ("translation.ve.md", "translation-part01.ve.md", "translation-part02.ve.md",
                 "translation-part03.ve.md", "translation-part04.ve.md"):
        corpus = translation("udhr", UDHR_RUN / part)
        corpus.note = part
        yield corpus
    yield english("agent-policy", USECASES / "agent-policy", "policy.ve", "policy.manifest.json",
                  sorted(p.name for p in (USECASES / "agent-policy").glob("environment*.json")))
    yield safety_framework()
    yield eligibility()
    yield english("asimov", USECASES / "asimov-laws", "rules.ve", "rules.manifest.json", ["environment.json"])
    yield english("asimov", USECASES / "asimov-extended", "rules.ve", "rules.manifest.json", ["environment.json"])


# ---------------------------------------------------------------- the pair tests

def co_present(a, b):
    """Present together in some choice: every reading set both name has the same choice in both."""
    choices = dict(a.condition)
    return all(choices.get(k, v) == v for k, v in b.condition)


def regulated(env_data):
    return {name: decl["regulated"] for name, decl in env_data["vocabulary"]["predicates"].items()
            if "regulated" in decl}


def incompatible(a, b, reg):
    """soft-norms 1.4: one act, opposite polarity."""
    if a.predicate == b.predicate:
        return a.sign != b.sign
    for r, m in ((a, b), (b, a)):
        decl = reg.get(r.predicate, {})
        if decl.get("role") == "obligation" and decl.get("permission") == m.predicate and r.sign and not m.sign:
            return True
    return False


def reaches(rules, start, goal):
    by_name = {}
    for rule in rules:
        by_name.setdefault(rule.name, rule)
    seen, todo = set(), [start]
    while todo:
        name = todo.pop()
        if name == goal:
            return True
        if name in seen or name not in by_name:
            continue
        seen.add(name)
        todo.extend(by_name[name].over)
    return False


def outranks(soft, high, low):
    if not soft or high is None or low is None:
        return False
    edges = {}
    for x, y in soft.get("outranks", []):
        edges.setdefault(x, set()).add(y)
    seen, todo = set(), [high]
    while todo:
        x = todo.pop()
        for y in edges.get(x, ()):
            if y == low:
                return True
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return False


def _walk(f, atoms, flags, defined):
    if not isinstance(f, list):
        return
    head = f[0]
    if head in QUANTIFIERS:
        flags.add("quantifier")
        return
    if head in CONNECTIVES:
        for sub in f[1:]:
            _walk(sub, atoms, flags, defined)
        return
    if len(f) > 1 and isinstance(f[1], str) and f[1] in defined:
        flags.add("defined")
    atoms.add(json.dumps(f, sort_keys=True))


def _value(f, assignment):
    head = f[0]
    if head == "top":
        return True
    if head == "bottom":
        return False
    if head == "and":
        return all(_value(x, assignment) for x in f[1:])
    if head == "or":
        return any(_value(x, assignment) for x in f[1:])
    if head == "not":
        return not _value(f[1], assignment)
    if head == "implies":
        return (not _value(f[1], assignment)) or _value(f[2], assignment)
    if head == "iff":
        return _value(f[1], assignment) == _value(f[2], assignment)
    return assignment[json.dumps(f, sort_keys=True)]


def implies(g, h, env_data, predicate):
    """'yes', 'no' or 'unknown', with the method used."""
    defined = {n for n, d in env_data["vocabulary"]["predicates"].items() if "defined" in d}
    atoms, flags = set(), set()
    _walk(g, atoms, flags, defined)
    _walk(h, atoms, flags, defined)
    if not flags:
        atoms = sorted(atoms)
        if len(atoms) > 20:
            return "unknown", "truth table too large"
        for values in itertools.product((False, True), repeat=len(atoms)):
            assignment = dict(zip(atoms, values))
            if _value(g, assignment) and not _value(h, assignment):
                return "no", "truth table"
        return "yes", "truth table"
    return _tableau(g, h, env_data, predicate)


_BASE = {}


def _tableau(g, h, env_data, predicate):
    key = json.dumps(env_data, sort_keys=True)
    if key not in _BASE:
        data = json.loads(key)
        data["vocabulary"]["predicates"] = {n: d for n, d in data["vocabulary"]["predicates"].items()
                                            if "regulated" not in d}
        data["vocabulary"].pop("soft", None)
        data["profiles"] = [p for p in data["profiles"]
                            if p not in {"norms@0", "soft-norms@0", "norm-defaults@0", "readings@1", "rights@0",
                                         "documents@1"}]
        try:
            _BASE[key] = Environment(data)
        except Exception as exc:
            _BASE[key] = f"base environment refused: {type(exc).__name__}: {exc}"[:200]
    base = _BASE[key]
    if isinstance(base, str):
        return "unknown", base
    sorts = env_data["vocabulary"]["predicates"][predicate]["arguments"]
    try:
        # Close the wire form first (index 0 is the last argument, as norms.py's context), then decode.
        closed = ["implies", g, h]
        for sort in reversed(sorts):
            closed = ["forall", sort, closed]
        result = prove_entailment(base, [], formula_from_data(base, closed))
    except Exception as exc:  # an input the tableau does not take is an unknown direction, never a 'no'
        return "unknown", f"tableau error: {type(exc).__name__}: {exc}"[:200]
    return ("yes", "tableau certificate") if result.status == "Found" else ("unknown", f"tableau {result.status}")


# ---------------------------------------------------------------- the count

def pairs(corpus):
    reg = regulated(corpus.env_data)
    for a, b in itertools.combinations(corpus.rules, 2):
        if a is b or not co_present(a, b) or not incompatible(a, b, reg):
            continue
        present = [r for r in corpus.rules if not r.condition or r is a or r is b
                   or set(r.condition) <= set(a.condition) | set(b.condition)]
        written = (reaches(present, a.name, b.name) or reaches(present, b.name, a.name)
                   or outranks(corpus.soft, a.rank, b.rank) or outranks(corpus.soft, b.rank, a.rank))
        forward = implies(a.guard, b.guard, corpus.env_data, a.predicate)
        backward = implies(b.guard, a.guard, corpus.env_data, b.predicate)
        yield a, b, written, forward, backward


def classify(written, forward, backward):
    f, b = forward[0], backward[0]
    if "unknown" in (f, b) and not (f == "yes" and b == "yes"):
        if (f, b) in {("yes", "unknown"), ("unknown", "yes")}:
            kind = "implied, converse unknown"
        elif (f, b) in {("no", "unknown"), ("unknown", "no")}:
            kind = "converse unknown, no implication found"
        else:
            kind = "both unknown"
    elif f == "yes" and b == "yes":
        kind = "equivalent"
    elif f == "yes" or b == "yes":
        kind = "strict"
    else:
        kind = "neither"
    return ("written: " if written else "") + kind


def main():
    rows, seen, census = [], set(), {}
    for corpus in corpora():
        stats = census.setdefault(corpus.name, {"rule_sets": [], "rules": 0, "colliding": 0})
        stats["rule_sets"].append({"source": corpus.note, "rules": len(corpus.rules)})
        for a, b, written, forward, backward in pairs(corpus):
            key = (corpus.name, *sorted((a.key(), b.key())))
            if key in seen:
                continue
            seen.add(key)
            stats["colliding"] += 1
            rows.append({"corpus": corpus.name, "source": corpus.note,
                         "rules": [{"name": r.name, "origin": r.origin, "predicate": r.predicate, "sign": r.sign,
                                    "mode": r.mode, "rank": r.rank, "guard": r.guard, "unless": r.unless,
                                    "over": list(r.over)} for r in (a, b)],
                         "both_default": a.mode == "default" and b.mode == "default",
                         "written_precedence_or_rank": written,
                         "a_implies_b": list(forward), "b_implies_a": list(backward),
                         "class": classify(written, forward, backward)})
        stats["rules"] = sum(s["rules"] for s in stats["rule_sets"])
    qualifying = [r for r in rows if r["class"] == "strict"]
    possible = [r for r in rows if r["class"] in {"implied, converse unknown", "both unknown"}]
    certain, upper = len(qualifying), len(qualifying) + len(possible)
    verdict = "met" if certain >= 5 else ("UNKNOWN" if upper >= 5 else "not met")
    summary = {"qualifying": certain, "qualifying_if_unknown_resolved_favourably": upper, "bar": 5,
               "verdict": verdict, "by_class": {}}
    for row in rows:
        summary["by_class"][row["class"]] = summary["by_class"].get(row["class"], 0) + 1
    write_json("specificity-pairs.json", {
        "definition": "docs/research/defeasible-phase1.md 1.5",
        "inputs": {"constitution": sha256(CONSTITUTION_RUN / "translation.ve.md"),
                   "udhr": {p.name: sha256(p) for p in sorted(UDHR_RUN.glob("translation*.ve.md"))}},
        "census": census, "summary": summary, "pairs": rows})
    print(json.dumps({"census": {k: {"rules": v["rules"], "colliding": v["colliding"]} for k, v in census.items()},
                      "summary": summary}, indent=1))


if __name__ == "__main__":
    main()
