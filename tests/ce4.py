"""`CE4`: the four sets of the constitution pilot's run 20261010T1800Z in a small document (docs/spec/
rd-9-soft-chain-PLAN.md 5.2; spec 8.2).

The document is built from the pinned translation, never retyped: `translation.ve.md` at pilot commit `76922d6c`,
kept byte for byte in `tests/data/ce4/` (gzip) and checked against its git blob id. Its frame has the sorts
`claude_instance`, `situation` and `user`, the base predicates `genuine_ambiguity` and
`explicit_instruction_against_exploits` and the four regulated predicates, each `unspecified`, with their act phrases
and verbalisations copied; its profiles add `soft-norms@0`. Each `default` candidate is rewritten from "strict rule +
`unless` over an `exception_to_*` open term" to the same rule with `mode: default`, an unstated exception and no
`unless`; the four open terms are dropped. The `strict` candidates and the source words are unchanged (a source word's
span moves with its sentence into the small document's text).

`SIGMA` is spec 8.2's σ for C1 to C4, over the filled author vocabulary: the witness `default`, its decision table,
the shared filling of the regulated predicate and the base facts.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
from pathlib import Path

from ve.norm_defaults import unsaid_name

PILOT_COMMIT = "76922d6c"
PILOT_PATH = "usecases/claude-constitution-pilot/run-20261010T1800Z/translation.ve.md"
COPY = Path(__file__).resolve().parent / "data" / "ce4" / "translation-76922d6c.ve.md.gz"
BLOB = "2d9f53e679f90154e900be34f4dcf5bdb36ecdaa"  # `git rev-parse 76922d6c:<PILOT_PATH>`
SHA256 = "260a14b9d37949987f549b0af6a244235b991813a6f7ea9ad346fec2283f5cdc"

SORTS = ("claude_instance", "situation", "user")
BASE = ("genuine_ambiguity", "explicit_instruction_against_exploits")
REGULATED = ("clarification_required", "denial_of_being_claude_permitted", "system_prompt_deception_permitted",
             "exploit_instruction_compliance_required")
UNSTATED = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}

# The sets in the translation's order, with the rule each reading states.
SETS = ("force-u0036-s05", "force-u0125-s04-p2", "force-u0156-s03", "force-u0263-s04-p2")
RULES = {"force-u0036-s05": "clarify-ambiguity", "force-u0125-s04-p2": "no-denying-being-claude",
         "force-u0156-s03": "no-system-prompt-deception", "force-u0263-s04-p2": "comply-no-exploit-instruction"}


def pinned_bytes():
    """The translation's bytes, checked against the pilot commit's blob."""
    data = gzip.decompress(COPY.read_bytes())
    assert hashlib.sha256(data).hexdigest() == SHA256
    assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == BLOB
    return data


def translation():
    """(front matter, body bytes) of the pinned translation."""
    data = pinned_bytes()
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def environment():
    front, _ = translation()
    source = front["environment"]
    vocabulary = source["vocabulary"]
    return {"language": source["language"], "spec_revision": source["spec_revision"],
            "profiles": sorted({*source["profiles"], "soft-norms@0"}),
            "vocabulary": {"sorts": {s: copy.deepcopy(vocabulary["sorts"][s]) for s in SORTS},
                           "constants": {},
                           "predicates": {p: copy.deepcopy(vocabulary["predicates"][p]) for p in (*BASE, *REGULATED)}}}


def soft_default(content):
    """A `default` candidate's rule without its `exception_to_*` open term: `mode: default`, an unstated exception,
    no `unless`."""
    rule = copy.deepcopy(content["norm"])
    assert len(rule["unless"]) == 1 and rule["unless"][0][1].startswith("exception_to_"), rule
    return {"norm": {**rule, "unless": [], "mode": "default", "exception": copy.deepcopy(UNSTATED)}}


def reading_sets():
    """The four sets, the `default` candidates rewritten, each set's units and source word as the translation has
    them; no situation recorded (`with_situations`)."""
    front, _ = translation()
    out = []
    for R in front["reading_sets"]:
        assert R["id"] in SETS and [a["id"] for a in R["readings"]] == ["strict", "default"]
        readings = []
        for a in R["readings"]:
            content = soft_default(a["content"]) if a["id"] == "default" else copy.deepcopy(a["content"])
            readings.append({"id": a["id"], "kind": a["kind"], "content": content,
                             "admission": {"who": a["admission"]["who"], "why": a["admission"]["why"],
                                           "distinguishing_models": {}}})
        out.append({"id": R["id"], "unit": R["unit"], "version": R["version"], "status": R["status"],
                    "source_word": list(R["source_word"]), "readings": readings})
    assert [R["id"] for R in out] == list(SETS)
    return out


def base(relations=None):
    """The base of a situation of `CE4`: one element of each sort, the base facts `relations`, every shared filling
    empty unless `relations` sets it."""
    filled = {p: [] for p in BASE} | {unsaid_name(p): [] for p in REGULATED}
    filled.update({p: [list(row) for row in rows] for p, rows in (relations or {}).items()})
    return {"domains": {"claude_instance": ["c"], "situation": ["s"], "user": ["u"]}, "constants": {},
            "relations": filled}


def sigma(set_id):
    """Spec 8.2's σ for the set (C1 to C4): witness `default`, its exception decided for the tuple, the outcome on
    the tuple; C1 and C3 fill the gap 'yes' (true), C2 and C4 leave it empty with the guard's base fact (false)."""
    predicate, row, relations, value = {
        "force-u0125-s04-p2": ("denial_of_being_claude_permitted", ["c"],
                               {unsaid_name("denial_of_being_claude_permitted"): [["c"]]}, True),
        "force-u0036-s05": ("clarification_required", ["c", "s"], {"genuine_ambiguity": [["s"]]}, False),
        "force-u0156-s03": ("system_prompt_deception_permitted", ["c", "u"],
                            {unsaid_name("system_prompt_deception_permitted"): [["c", "u"]]}, True),
        "force-u0263-s04-p2": ("exploit_instruction_compliance_required", ["c", "s"],
                               {"explicit_instruction_against_exploits": [["c", "s"]]}, False)}[set_id]
    return {"base": base(relations), "fixed": [], "witness": "default",
            "decisions": [{"key": {"excepted": RULES[set_id]}, "tuples": [row]}],
            "probe": {"outcome": {"predicate": predicate, "tuple": row}}, "value": value}


def with_situations(raw, sets, situation_id, situations=None):
    """The sets with each one's situation (`situations[set]`, else `sigma`) recorded for both pairs."""
    out = []
    for R in copy.deepcopy(sets):
        entry = (situations or {}).get(R["id"]) or sigma(R["id"])
        sid = situation_id(raw, entry)
        R["situations"] = {sid: entry}
        for a in R["readings"]:
            a["admission"]["distinguishing_models"] = {b["id"]: sid for b in R["readings"] if b["id"] != a["id"]}
        out.append(R)
    return out


def wire_document(sets):
    """The Lean route's document: one unit per set, no fixed unit."""
    return {"units": [{"id": R["unit"]} for R in sets], "reading_sets": sets}


def source_text():
    """The small document's text and its units: each set's sentence from the translation in order, each unit's span
    and each source word's span moved with its sentence."""
    front, body = translation()
    units, text, moved = [], b"", {}
    for R in front["reading_sets"]:
        u = next(x for x in front["units"] if x["id"] == R["unit"])
        start, stop = u["span"]
        sentence = body[start:stop].rstrip(b"\n ") + b"\n"
        offset = len(text) - start
        units.append({"id": u["id"], "span": [len(text), len(text) + len(sentence)], "kind": u["kind"],
                      "meaning": "specified", "support": u["support"], "content": None})
        moved[R["id"]] = [w + offset for w in R["source_word"]]
        text += sentence
    return text, units, moved
