"""Loads the D1 translation of the anthropic-rsp case: the rules of `rules.d1.ve` and the premises of `facts.d1.ve`.

The block format is safety-framework's (`translation.py` there): a header `## <id> | <when> | <source>` and one line
of VE English. Rule headers also carry `| RS0` or `| independent` before the source: this records whether removing
N1 changes that rule from a commitment to a prediction. `<when>` is `always` or a conjunction of reading choices
(`RS2=Ds & RS2force=strict`). A rule block is
one VE norm rule, parsed alone with VE's one-reading check; a fact block is one paragraph of VE English sentences.
The reading sets are PLAN 3.1's; a set the text has on several independent sentences (RS6, RS8, RS12) has one
harness set per sentence, so that no choice on one sentence is forced on another. N1 (every RS0 statement a
commitment), N2 (the changelog is history) and N3 (RS6 = P in 3.6.1) are applied: they have no set here.
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
import rsp_vocabulary as vocabulary  # noqa: E402

READING_SETS = {
    "RS1": ("cond", "uncond", "ov"), "RS2": ("F", "Ds"), "RS2force": ("strict", "default"),
    "RS3o": ("suff", "iff"), "RS3i": ("suff", "iff"), "RS3c": ("third", "result"), "RS4": ("scope", "rel"),
    "RS5": ("import", "noimport"), "RS7": ("exec", "final"), "RS9": ("window", "bound"), "RS11": ("at", "trigger"),
    "RS13": ("default", "frequency"),
    **{f"RS6{s}": ("P", "M") for s in ("redact", "split", "notice")},
    **{f"RS8{s}": ("strict", "default") for s in ("evidence", "attempt", "revenue")},
    **{f"RS12{s}": ("default", "intent") for s in ("advance", "strive", "candid", "minimize", "justify", "review",
                                                    "before")},
}
# The exception headers: rule -> the rules it takes precedence over (3.4 step 5 over step 3's "ultimate").
PRECEDENCE = {"f12-board-approval": ("f12-final",)}


@dataclass(frozen=True)
class Block:
    id: str
    when: tuple[tuple[str, str], ...]
    source: str
    text: str
    narrowing: str | None = None


def read_blocks(name):
    lines = (HERE / name).read_text().splitlines()
    if len(lines) % 2:
        raise SystemExit(f"{name}: a header line without its block")
    blocks = []
    for header, text in zip(lines[::2], lines[1::2]):
        if name == "rules.d1.ve":
            m = re.fullmatch(r"## ([a-z0-9-]+) \| ([^|]+) \| (RS0|independent) \| (.+)", header)
        else:
            m = re.fullmatch(r"## ([a-z0-9-]+) \| ([^|]+) \| (.+)", header)
        if m is None or text.startswith("## "):
            raise SystemExit(f"{name}: malformed header {header!r}")
        when = () if m[2].strip() == "always" else tuple(
            tuple(part.strip().split("=")) for part in m[2].split("&"))
        for set_id, choice in when:
            if choice not in READING_SETS.get(set_id, ()):
                raise SystemExit(f"{name}: unknown reading {set_id}={choice}")
        blocks.append(Block(m[1], when, m[4] if name == "rules.d1.ve" else m[3], text,
                            m[3] if name == "rules.d1.ve" else None))
    return blocks


@lru_cache(maxsize=None)
def environment():
    from ve.softnorms import SoftEnvironment
    return SoftEnvironment(vocabulary.environment())


@lru_cache(maxsize=None)
def rule_blocks():
    return tuple(read_blocks("rules.d1.ve"))


@lru_cache(maxsize=None)
def parsed_rule(block_id):
    """One rule, parsed alone with the one-reading check, as a wire dict (JSON text)."""
    from ve.norm_english import parse_english
    block = next(b for b in rule_blocks() if b.id == block_id)
    document = parse_english(environment(), block.text)
    if len(document.rules) != 1:
        raise SystemExit(f"{block_id}: expected one rule")
    data = document.rules[0].to_dict()["norm"]
    data["name"] = block_id
    return json.dumps(data, sort_keys=True)


@lru_cache(maxsize=None)
def base_environment():
    """The vocabulary without regulated predicates, in which the premises are stated."""
    from ve.environment import Environment
    data = vocabulary.environment()
    data["vocabulary"]["predicates"] = {name: entry for name, entry in data["vocabulary"]["predicates"].items()
                                        if "regulated" not in entry}
    data["profiles"] = ["relational-fol@0"]
    return Environment(data)


@lru_cache(maxsize=None)
def facts():
    """The premises, as (block, formulas)."""
    from ve.english import parse_english
    return tuple((block, tuple(parse_english(base_environment(), block.text).formulas))
                 for block in read_blocks("facts.d1.ve"))


if __name__ == "__main__":
    for block in rule_blocks():
        parsed_rule(block.id)
    print(len(rule_blocks()), "rules,", sum(len(f) for _, f in facts()), "premises")
