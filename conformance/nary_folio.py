"""Offline FOLIO v2 n-ary witness audit; the corpus itself stays gitignored.

Run after downloading the two tasksource/folio v2 JSONL files documented in
data/README.md. The source's symbolic FOL is parsed before translating it to
VE; malformed gold is reported, never silently repaired.
"""
from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

from lark import Lark, Tree, Token

from ve.ast import (And, Atom, Binary, Const, Document, Eq, Exists, Forall,
                    Implies, Not, Or, Unary, Var)
from ve.environment import Environment
from ve.parser import parse
from ve.printer import print_document
from ve.profiles import LANGUAGE, SPEC_REVISION

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = r"""
?start: formula
?formula: implication
?implication: disjunction ("→" implication)? -> implication
?disjunction: xor ("∨" xor)* -> disjunction
?xor: conjunction ("⊕" conjunction)* -> xor
?conjunction: unary ("∧" unary)* -> conjunction
?unary: "¬" unary -> negation
      | "∀" NAME unary -> universal
      | "∃" NAME unary -> existential
      | "(" formula ")" -> grouped
      | atom
?atom: NAME "(" terms ")" -> predicate
     | term "=" term -> equality
terms: term ("," term)*
term: NAME
NAME: /[A-Za-z0-9_][A-Za-z0-9_.-]*/
%import common.WS
%ignore WS
"""
FOL = Lark(GRAMMAR, parser="lalr")
ATOM = re.compile(r"([A-Za-z_][A-Za-z0-9_.-]*)\(([^()]*)\)")


def folio_pairs():
    seen = set()
    for split in ("train", "validation"):
        path = ROOT / f"data/folio/tasksource_folio_v2_{split}.jsonl"
        for line in path.read_text().splitlines():
            row = json.loads(line)
            natural = row["premises"].split("\n")
            formal = row["premises-FOL"].split("\n")
            pairs = ([(f"s{row['story_id']}:p{i}", a, b)
                      for i, (a, b) in enumerate(zip(natural, formal))]
                     if len(natural) == len(formal) else [])
            pairs.append((f"e{row['example_id']}:c", row["conclusion"], row["conclusion-FOL"]))
            for id_, nl, fol in pairs:
                if (nl, fol) not in seen:
                    seen.add((nl, fol))
                    yield id_, nl, fol


def has_nary_atom(fol: str) -> bool:
    return any(len(match.group(2).split(",")) > 2 for match in ATOM.finditer(fol))


def identifier(kind: str, original: str) -> str:
    slug = re.sub(r"[^a-z0-9_]", "_", original.lower())[:40]
    digest = hashlib.sha256(original.encode()).hexdigest()[:8]
    return f"{kind}_{slug}_{digest}"


def convert(tree: Tree, binders: tuple[str, ...], predicates: dict, constants: dict):
    def term(node):
        name = str(node.children[0])
        if name in binders:
            return Var(binders[::-1].index(name))
        if name in {"x", "y", "z", "t"}:
            raise ValueError(f"free variable {name}")
        key = identifier("c", name)
        if key in constants and constants[key] != name:
            raise ValueError(f"constant name collision {name}")
        constants[key] = name
        return Const(key)

    kind, children = tree.data, tree.children
    if kind == "predicate":
        source = str(children[0])
        name = identifier("p", source)
        args = tuple(term(child) for child in children[1].children)
        if name in predicates and predicates[name] != (source, len(args)):
            raise ValueError(f"predicate signature collision {source}")
        predicates[name] = source, len(args)
        if len(args) == 1:
            return Unary(name, args[0])
        if len(args) == 2:
            return Binary(name, *args)
        if 3 <= len(args) <= 6:
            return Atom(name, args)
        raise ValueError(f"unsupported arity {len(args)} for {source}")
    if kind == "equality":
        return Eq(term(children[0]), term(children[1]))
    if kind == "grouped":
        return convert(children[0], binders, predicates, constants)
    if kind == "negation":
        return Not(convert(children[0], binders, predicates, constants))
    if kind in {"universal", "existential"}:
        variable = str(children[0])
        if variable in binders:
            raise ValueError(f"shadowed variable {variable}")
        body = convert(children[1], (*binders, variable), predicates, constants)
        return (Forall if kind == "universal" else Exists)("entity", body)
    parts = [convert(child, binders, predicates, constants) for child in children]
    if kind == "implication":
        return Implies(*parts) if len(parts) == 2 else parts[0]
    if kind == "conjunction":
        operation = And
    elif kind == "disjunction":
        operation = Or
    elif kind == "xor":
        operation = lambda a, b: Or(And(a, Not(b)), And(Not(a), b))
    else:
        raise ValueError(f"unsupported syntax {kind}")
    result = parts[0]
    for part in parts[1:]:
        result = operation(result, part)
    return result


def direct_parse(fol: str):
    # Thousands separators are lexical parts of FOLIO numeric names. Time and
    # quantities remain opaque user-sort names in stage 1.
    lexical = re.sub(r"(?<=\d),(?=\d{3}\b)", "", fol)
    predicates, constants = {}, {}
    formula = convert(FOL.parse(lexical), (), predicates, constants)
    env = Environment({
        "language": LANGUAGE,
        "profiles": ["closure@0", "nary@0", "relational-fol@0"],
        "spec_revision": SPEC_REVISION,
        "vocabulary": {
            "sorts": {"entity": {"description": "Entity"}},
            "predicates": {name: {"arguments": ["entity"] * arity,
                                  "description": source}
                           for name, (source, arity) in predicates.items()},
            "constants": {name: {"sort": "entity", "description": source}
                          for name, source in constants.items()},
        },
    })
    doc = Document((formula,))
    strict = print_document(env, doc)
    assert parse(env, strict) == doc
    return strict


def report():
    pairs = [(id_, nl, fol) for id_, nl, fol in folio_pairs() if has_nary_atom(fol)]
    failures = {}
    for id_, _, fol in pairs:
        try:
            direct_parse(fol)
        except (Exception) as error:
            failures[id_] = str(error).splitlines()[0]
    frozen = json.loads((ROOT / "experiments/E0/survey_samples/_drawn/folio.json").read_text())
    labels = {json.loads(line)["id"]: json.loads(line)["class"] for line in
              (ROOT / "experiments/E0/survey_samples/folio.jsonl").read_text().splitlines()}
    sample = frozen["sample"]
    newly_direct = [row["id"] for row in sample if labels[row["id"]] == "b"
                    and has_nary_atom(row["fol"]) and row["id"] not in failures]
    baseline = sum(labels[row["id"]] == "a" for row in sample)
    return {"nary_pairs": len(pairs), "direct_parses": len(pairs) - len(failures),
            "failures": failures, "frozen_sample": {
                "baseline_direct_fit": baseline, "new_nary_ids": newly_direct,
                "new_direct_fit": baseline + len(newly_direct), "sample_size": len(sample)}}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
