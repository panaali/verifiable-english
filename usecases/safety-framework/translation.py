"""Loads the D1 translation: the rule candidates of `rules.d1.ve` and the premises of `facts.d1.ve`.

Both files are blocks of a header line `## <id> | <when> | <source>` followed by
one line of VE English. A rule block is one VE norm rule, parsed alone with
VE's one-reading check (`ve.norm_english.parse_english`), so that a document
of any reading choice is assembled from parsed rules without parsing again.
`<when>` is `always` or a conjunction of reading choices (`RS1=G & RS8=rel`):
the rule belongs to the document of every complete choice that satisfies it.
A fact block is one paragraph of VE English sentences, parsed with VE's
one-reading check (`ve.english.parse_english`).

The reading sets (PLAN 3.1) are `READING_SETS`. RS0 and RS10 are not here:
under the N1 narrowing every rule from a "will" sentence is a commitment, and
RS10 concerns the dates of D3 only.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

import vocabulary  # noqa: E402
from ve.english import parse_english as parse_sentences  # noqa: E402
from ve.norm_english import parse_english as parse_rules  # noqa: E402
from ve.softnorms import SoftEnvironment, SoftNormDocument  # noqa: E402

READING_SETS = {
    "RS1": ("S", "G"),
    "RS2": ("P", "U"),
    "RS3": ("F", "Ds"),
    "RS4aim": ("default", "intent"),
    "RS4holistic": ("strict", "default"),
    "RS4within": ("strict", "default"),
    "RS4elicitation": ("strict", "default"),
    "RS5": ("D", "R"),
    "RS6": ("same", "different"),
    "RS7": ("E", "M"),
    "RS8": ("scope", "rel"),
    "RS9": ("same", "different"),
}
# The exception headers of the translation: rule -> the rules it takes precedence over.
PRECEDENCE = {"f3": ("f2",)}
# Rules from a "will" sentence about the developer's own process (RS0): under the
# prediction reading, without N1, none of them is a norm.
WILL_RULES = {"f6", "f7-rra", "f7-sc", "f9-acc", "f9-dm", "f9-sec", "f9-rel", "f10-acc", "f10-dm-same",
              "f10-dm-diff", "f10-sec", "f10-rel-same", "f10-rel-diff", "f11-acc", "f11-dm", "f11-sec",
              "f11-rel", "f14", "f17-pra", "f17-add", "f18-yearly", "f18-frequent"}


@dataclass(frozen=True)
class Block:
    id: str
    when: tuple[tuple[str, str], ...]
    source: str
    text: str


def read_blocks(name):
    lines = (HERE / name).read_text().splitlines()
    if len(lines) % 2:
        raise SystemExit(f"{name}: a header line without its block")
    blocks = []
    for header, text in zip(lines[::2], lines[1::2]):
        m = re.fullmatch(r"## ([a-z0-9-]+) \| ([^|]+) \| (.+)", header)
        if m is None or text.startswith("## "):
            raise SystemExit(f"{name}: malformed header {header!r}")
        when = () if m[2].strip() == "always" else tuple(
            tuple(part.strip().split("=")) for part in m[2].split("&"))
        for set_id, choice in when:
            if choice not in READING_SETS.get(set_id, ()):
                raise SystemExit(f"{name}: unknown reading {set_id}={choice}")
        blocks.append(Block(m[1], when, m[3], text))
    return blocks


@lru_cache(maxsize=None)
def environment(default="deny"):
    return SoftEnvironment(vocabulary.environment(default))


def rule_blocks():
    return [b for b in read_blocks("rules.d1.ve")]


@lru_cache(maxsize=None)
def parsed_rule(block_id, default="deny", text=None):
    """One candidate rule, parsed alone with the one-reading check, as a wire dict."""
    block = next(b for b in rule_blocks() if b.id == block_id)
    source = text if text is not None else block.text
    document = parse_rules(environment(default), source)
    if len(document.rules) != 1:
        raise SystemExit(f"{block_id}: expected one rule")
    data = document.rules[0].to_dict()["norm"]
    data["name"] = block_id
    return json.dumps(data, sort_keys=True)


def applies(block, choice):
    return all(choice.get(set_id) == value for set_id, value in block.when)


def document(choice, *, default="deny", drop=(), extra=(), precedence=None):
    """The soft norm document of one complete (or partial) reading choice.

    `extra` adds (id, text) rules (mutants and the reading without N2);
    `drop` removes rules by id; `precedence` replaces PRECEDENCE (mutant m1).
    """
    precedence = PRECEDENCE if precedence is None else precedence
    rules = []
    for block in rule_blocks():
        if block.id in drop or not applies(block, choice):
            continue
        rules.append(json.loads(parsed_rule(block.id, default)))
    for rule_id, text in extra:
        data = parse_rules(environment(default), text).rules[0].to_dict()["norm"]
        data["name"] = rule_id
        rules.append(data)
    names = {r["name"] for r in rules}
    for rule in rules:
        rule["over"] = [m for m in precedence.get(rule["name"], ()) if m in names]
    return SoftNormDocument(environment(default), [{"norm": r} for r in rules])


@lru_cache(maxsize=None)
def facts():
    """The fixed premises, as (block id, source, formulas)."""
    base = base_environment()
    result = []
    for block in read_blocks("facts.d1.ve"):
        result.append((block.id, block.source, tuple(parse_sentences(base, block.text).formulas)))
    return tuple(result)


@lru_cache(maxsize=None)
def base_environment():
    """The base vocabulary (no regulated predicates) in which facts and cases are stated."""
    from ve.environment import Environment
    data = vocabulary.environment()
    data["vocabulary"]["predicates"] = {name: entry for name, entry in data["vocabulary"]["predicates"].items()
                                        if "regulated" not in entry}
    data["profiles"] = ["relational-fol@0"]
    return Environment(data)


if __name__ == "__main__":
    for block in rule_blocks():
        parsed_rule(block.id)
        print("ok", block.id)
    print(sum(len(f) for _, _, f in facts()), "premises")
