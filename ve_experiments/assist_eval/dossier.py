"""Deterministic reading of a P5 dossier's PUBLIC text: the waiver allowlist W(item), a reference
formalisation of every given sentence, and the graph checks the evaluation applies on top of the tool.

Nothing here reads labels. Every rule is a function of the dossier text (premises, records, the
claimed paragraphs' wording) and the public vocabulary, so W is fixed before any author runs and is
content-hashed into the PREREG manifest (``waivers.json``).

Given sentences are template text. Kinds:

* ``declared``   "Rules r09, r00 are declared."                   waive-only (W code ``declared``)
* ``unassumed``  "The checks that A and B remain unassumed."     waive-only (W code ``unassumed``);
                  its ASSUMPTION RESTRICTION stays: no assumption node may entail A or B.
* ``lot``        "The sample from lot unit0 is unit2."            waive-only (W code ``lot-sample``): the
                  vocabulary cannot state it.
* ``facts``      "unit0 is sized; unit0 is released."            reference = the conjunction
* ``supplied``   "Lot unit0 supplied sample unit2."               reference = supplied(unit0, unit2)
* ``rule``       "If A and B, then C."                            reference = if (A and B), then (C)
* ``unparsed``   any given sentence none of the templates above parses. NEVER in W (it cannot be waived); no
                  reference, so no deterministic content or coverage check (the auditor alone judges it).
                  No dev sentence is unparsed; five held-out sentences are ("rule + lot sentence" in one
                  given sentence). The 2026-09-23 "lot tail" branch that split them was written after the
                  held-out text had been read and was removed (README "W and the held-out text").

W(item) = the waive-only sentences, plus
* ``unused-fact``: a facts/supplied sentence none of whose atoms is an antecedent of a live rule or of a
  relied-on dead rule, or is mentioned by a claimed sentence;
* ``dead-rule``: a rule with an antecedent atom that is not derivable from the given facts by the given
  rules, PROVIDED no claimed sentence relies on it. A claimed sentence relies on a dead rule when it
  mentions (sense-free) one of the rule's underivable antecedent atoms together with its consequent atom
  (a "would imply ..., respectively" sentence, or a reason that is never established). A relied-on dead
  rule must be formalised.

Graph checks (``graph_violations``), each blocking evaluation success and the gap route:
* every waiver is in W;
* no node is anchored to a waive-only sentence;
* ANCHOR CONTENT, per anchor: an assumption anchored to given sentences must be entailed by EACH anchor's
  reference formalisation ALONE (it states what that sentence says, or part of it). An assumption citing
  two sentences jointly (Q anchored to "P" and "if P then Q") fails: split it, one assumption per sentence.
  Citing a sentence is not enough: a lot/sample bridge anchored to a rule sentence fails;
* COVERAGE, per formalised given sentence (every non-W one must be formalised; a formalised W sentence is
  checked too, so the check reveals nothing about W): the nodes anchored to it (assumptions AND steps) must
  together entail its reference formalisation (nothing it says is dropped);
* CLAIM STEPS: a step anchored to a claimed sentence must not be valid (a tautology states nothing; decided
  "no" required) and may use only the (unit, term) atoms its sentence(s) mention ("unitN is TERM", or
  "the immediately preceding TERM result" for any unit); no relation, identity or author-declared predicate;
* no assumption node entails an atom a "remain unassumed" sentence lists (decided "no" required).
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import re

from ve.assist.sources import source_from_p5

W_CODES = {
    "declared": "only lists which rules are declared",
    "unassumed": "only states which checks remain unassumed (its atoms may still never be assumed)",
    "lot-sample": "a lot/sample statement the vocabulary cannot express",
    "unused-fact": "a fact no live rule, relied-on rule or claimed sentence uses",
    "dead-rule": "a rule whose antecedents cannot be derived from the given facts and on which no claimed "
                 "sentence relies",
}
WAIVE_ONLY = ("declared", "unassumed", "lot-sample")

ATOM = re.compile(r"^(unit\d+) is ([a-z][a-z-]*)(?: \(([^)]+)\))?$")
MENTION = re.compile(r"\b(unit\d+) is ([a-z][a-z-]*)")
DECLARED = re.compile(r"^Rules? .+ (?:is|are) declared\.$")
UNASSUMED = re.compile(r"^The checks? that (.+) remains? unassumed\.$")
LOT = re.compile(r"^The sample from lot (unit\d+) is (unit\d+)\.$")
SUPPLIED = re.compile(r"^Lot (unit\d+) supplied sample (unit\d+)\.$")
RULE = re.compile(r"^If (.+), then (.+)\.$")
PRECEDING = re.compile(r"\bthe immediately preceding ([a-z][a-z-]*) result\b")
WOULD = re.compile(r"^The checks? that (.+) would (?:imply|establish) that (.+), respectively\.$")


class DossierError(ValueError):
    pass


def _predicates(environment):
    """(term, sense) -> predicate name and term -> [names], from the public glossary descriptions."""
    by_sense, by_term = {}, {}
    for name, row in environment["vocabulary"]["predicates"].items():
        m = re.fullmatch(r"(.+): (.+) \((R\d+)\)", row["description"])
        if not m:
            continue
        by_sense[(m[1], m[2])] = name
        by_term.setdefault(m[1], []).append(name)
    return by_sense, by_term


def _atom(text, by_sense, by_term):
    m = ATOM.match(text.strip())
    if not m:
        raise DossierError(f"not an atom: {text!r}")
    unit, term, sense = m[1], m[2], m[3]
    if sense is not None:
        if (term, sense) not in by_sense:
            raise DossierError(f"unknown sense {term} ({sense})")
        return unit, by_sense[(term, sense)], term
    names = by_term.get(term, [])
    if len(names) != 1:
        raise DossierError(f"term {term!r} needs a sense ({len(names)} predicates)")
    return unit, names[0], term


def _conj(parts):
    return parts[0] if len(parts) == 1 else f"({parts[0]}) and ({_conj(parts[1:])})"


def _atom_text(atom):
    return f"@{atom[0]} is {atom[1]}"


def _classify(text, by_sense, by_term):
    if DECLARED.match(text):
        return {"kind": "declared"}
    m = UNASSUMED.match(text)
    if m:
        return {"kind": "unassumed", "mentions": [(u, t) for u, t in MENTION.findall(m[1])]}
    if LOT.match(text):
        return {"kind": "lot"}
    m = SUPPLIED.match(text)
    if m:
        return {"kind": "supplied", "atoms": [], "reference": f"@{m[1]} supplied @{m[2]}."}
    m = RULE.match(text)
    if m:
        ante = [_atom(a, by_sense, by_term) for a in m[1].split(" and ")]
        cons = [_atom(a, by_sense, by_term) for a in m[2].split(" and ")]
        if len(cons) != 1:
            raise DossierError(f"rule with {len(cons)} consequents: {text!r}")
        return {"kind": "rule", "antecedents": ante, "consequent": cons[0],
                "reference": f"if ({_conj([_atom_text(a) for a in ante])}), then ({_atom_text(cons[0])})."}
    parts = [p for p in text.rstrip(".").split("; ")]
    atoms = [_atom(p, by_sense, by_term) for p in parts]
    return {"kind": "facts", "atoms": atoms,
            "reference": (_conj([_atom_text(a) for a in atoms]) + ".") if len(atoms) > 1
            else _atom_text(atoms[0]) + "."}


def _classify_or_unparsed(text, by_sense, by_term):
    try:
        return _classify(text, by_sense, by_term)
    except DossierError:
        return {"kind": "unparsed"}


def _key(atom):
    return atom[0], atom[1]


def _surface(atom):
    return atom[0], atom[2]  # (unit, term): what a claimed sentence can mention (senses left open)


@lru_cache(maxsize=None)
def _analyse_json(item_json):
    item = json.loads(item_json)
    built = source_from_p5(item)
    by_sense, by_term = _predicates(built["environment"])
    sentences = built["source"]["sentences"]
    given = {s["id"]: {"text": s["text"], **_classify_or_unparsed(s["text"], by_sense, by_term)}
             for s in sentences if s["role"] == "given"}
    claimed = [s for s in sentences if s["role"] == "claimed"]
    facts = {_key(a) for g in given.values() if g["kind"] == "facts" for a in g["atoms"]}
    rules = {sid: g for sid, g in given.items() if g["kind"] == "rule"}
    derivable = set(facts)
    changed = True
    while changed:
        changed = False
        for g in rules.values():
            if all(_key(a) in derivable for a in g["antecedents"]) and _key(g["consequent"]) not in derivable:
                derivable.add(_key(g["consequent"]))
                changed = True
    # What each claimed sentence mentions, sense-free: "unitN is term" pairs, plus "the immediately
    # preceding TERM result" as (any unit, TERM).
    mentions = [set(MENTION.findall(s["text"])) | {("*", t) for t in PRECEDING.findall(s["text"])}
                for s in claimed]
    said = lambda atom, m: atom in m or ("*", atom[1]) in m
    pairs = []  # (antecedent, consequent) surface pairs of "would imply ..., respectively" sentences
    for s in claimed:
        m = WOULD.match(s["text"])
        if m:
            left, right = MENTION.findall(m[1]), MENTION.findall(m[2])
            pairs += list(zip(left, right))
    live, relied = set(), set()
    for sid, g in rules.items():
        missing = [a for a in g["antecedents"] if _key(a) not in derivable]
        if not missing:
            live.add(sid)
            continue
        cons = _surface(g["consequent"])
        if any(said(_surface(a), m) and cons in m for a in missing for m in mentions) or any(
                (_surface(a), cons) in pairs for a in missing):
            relied.add(sid)
    used_atoms = {_key(a) for sid in live | relied for a in rules[sid]["antecedents"]}
    mentioned = set().union(*mentions) if mentions else set()
    said_any = lambda atom: said(atom, mentioned)
    allow = {}
    for sid, g in given.items():
        kind = g["kind"]
        if kind in ("declared", "unassumed"):
            allow[sid] = kind
        elif kind == "lot":
            allow[sid] = "lot-sample"
        elif kind == "rule" and sid not in live and sid not in relied:
            allow[sid] = "dead-rule"
        elif kind == "facts" and not any(_key(a) in used_atoms or said_any(_surface(a)) for a in g["atoms"]):
            allow[sid] = "unused-fact"
        elif kind == "supplied":
            allow[sid] = "unused-fact"  # no rule has a binary antecedent; claimed sentences never mention lots
    unassumed = []
    for g in given.values():
        if g["kind"] == "unassumed":
            for unit, term in g["mentions"]:
                for name in by_term.get(term, []):
                    unassumed.append(f"@{unit} is {name}.")
    return {"allow": dict(sorted(allow.items())),
            "reference": {sid: g["reference"] for sid, g in given.items() if "reference" in g},
            "kinds": {sid: g["kind"] for sid, g in given.items()},
            "unassumed": sorted(set(unassumed)),
            "premises": sorted(g["reference"] for g in given.values() if "reference" in g),
            "mentions": {s["id"]: sorted(m) for s, m in zip(claimed, mentions)},
            "terms": {name: term for term, names in by_term.items() for name in names},
            "live_rules": sorted(live), "relied_dead_rules": sorted(relied)}


def analyse(item):
    return _analyse_json(json.dumps(item, sort_keys=True))


def allowlist(item):
    """W(item): {sentence id: W code}."""
    return analyse(item)["allow"]


def waive_only(item):
    return {sid for sid, code in allowlist(item).items() if code in WAIVE_ONLY}


def allowlist_document(splits=("dev", "heldout")):
    """The preregistered W for every evaluation item, with each sentence's text hash (``waivers.json``)."""
    from .items import items
    out = {"format": "ve-assist-eval-waivers@1", "codes": W_CODES, "items": {}}
    for split in splits:
        for item in items(split):
            texts = {s["id"]: s["text"] for s in source_from_p5(item)["source"]["sentences"]}
            out["items"][item["id"]] = {
                "split": split,
                "waivable": {sid: {"code": code, "text_sha256": hashlib.sha256(texts[sid].encode()).hexdigest()}
                             for sid, code in allowlist(item).items()}}
    return json.dumps(out, indent=1, sort_keys=True) + "\n"


# ------------------------------------------------------------------ graph checks

def _parse(session, text):
    return session._parse(text, "auto")[0]


def formula_atoms(formula):
    """What a formula talks about: {(unit, predicate)} for unary atoms (unit "?" for a quantified variable),
    plus ("!", kind) markers for every relation, identity, arithmetic or reachability atom."""
    import dataclasses
    from ve import ast
    found, pending = set(), [formula]
    while pending:
        node = pending.pop()
        if type(node) is ast.Unary:
            found.add((node.term.name if type(node.term) is ast.Const else "?", node.predicate))
            continue
        if type(node) in (ast.Binary, ast.Eq, ast.Reach, ast.Lt, ast.Le):
            found.add(("!", type(node).__name__ + (f" {node.predicate}" if type(node) is ast.Binary else "")))
            continue
        if dataclasses.is_dataclass(node):
            for f in dataclasses.fields(node):
                value = getattr(node, f.name)
                if dataclasses.is_dataclass(value):
                    pending.append(value)
    return found


def _unmentioned(atoms, mentions, terms):
    """The atoms of a claim step its sentence(s) do not mention (as readable strings)."""
    said = {tuple(m) for m in mentions}
    wild = {t for u, t in said if u == "*"}
    out = []
    for unit, pred in sorted(atoms):
        term = terms.get(pred)
        if unit == "!":
            out.append(pred)
        elif term is None:
            out.append(f"{pred} (not a dossier predicate)")
        elif unit == "?":
            if not any(t == term for _, t in said):
                out.append(f"<variable> is {term}")
        elif (unit, term) not in said and term not in wild:
            out.append(f"{unit} is {term}")
    return out


def graph_violations(session, item):
    """Evaluation-level violations of the dossier contract (see the module docstring); [] when clean."""
    info = analyse(item)
    allow, only = info["allow"], {sid for sid, c in info["allow"].items() if c in WAIVE_ONLY}
    refs = info["reference"]
    out = []
    for sid in session.waivers:
        if sid not in allow:
            out.append(f"waiver outside W: {sid}")
    unassumed = [_parse(session, t) for t in info["unassumed"]]
    parsed = {}
    ref = lambda sid: parsed.setdefault(sid, _parse(session, refs[sid]))
    for node in session.nodes.values():
        bad = [a for a in node.anchors if a in only]
        if bad:
            out.append(f"node {node.name} is anchored to waive-only sentence(s) {', '.join(bad)}")
            continue
        claimed = [a for a in node.anchors if session.sentences[a]["role"] == "claimed"]
        if node.kind == "step" and claimed:
            if session._decide((), node.formula) != "no":
                out.append(f"step {node.name} (anchored to {', '.join(claimed)}) is not decided non-valid: a "
                           f"claim step must state something")
            mentions = [m for a in claimed for m in info["mentions"].get(a, [])]
            mentions += [(u, info["terms"].get(p)) for a in node.anchors if a in refs
                         for u, p in formula_atoms(ref(a)) if u not in ("!", "?")]
            extra = _unmentioned(formula_atoms(node.formula), mentions, info["terms"])
            if extra:
                out.append(f"step {node.name} uses what its sentence(s) {', '.join(claimed)} do not mention: "
                           + "; ".join(extra))
        if node.kind != "assumption":
            continue
        for atom in unassumed:
            if session._decide([node.formula], atom) != "no":
                out.append(f"assumption {node.name} may assume an unassumed check ({session._canonical(atom)})")
        roles = {session.sentences[a]["role"] for a in node.anchors}
        if not node.anchors or roles != {"given"}:
            continue  # unanchored / claim-anchored: the tool already reports these
        for a in node.anchors:
            if a not in refs:
                continue  # an unparsed given sentence: no reference; the auditor alone judges it
            verdict = session._decide([ref(a)], node.formula)
            if verdict != "yes":
                out.append(f"assumption {node.name} does not state what its anchor {a} alone says "
                           f"(content check {verdict})" + ("; one assumption per sentence"
                                                           if len(node.anchors) > 1 else ""))
    for sid in refs:
        # Every formalised given sentence, in W or not (so the check is flaw-neutral and reveals nothing
        # about W); an unformalised, unwaived one is the tool's own "uncovered" failure.
        nodes = [n.formula for n in session.nodes.values() if sid in n.anchors]
        if not nodes:
            continue
        verdict = session._decide(nodes, ref(sid))
        if verdict != "yes":
            out.append(f"the nodes anchored to given {sid} do not state all it says (coverage check {verdict})")
    return out


def gap_not_derivable(session, item, formula):
    """Is ``formula`` NOT entailed by the whole dossier (every given sentence's reference)? "no" means a
    genuine gap; "yes"/"unknown" means the dossier's premises may repair it (not a demonstrated gap)."""
    premises = [_parse(session, t) for t in analyse(item)["premises"]]
    return session._decide(premises, formula)
