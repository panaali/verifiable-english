"""The PF D1 blocks use the same two-line format and VE parser as the RSP baseline."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
import json
import re
from dataclasses import dataclass
from functools import lru_cache

sys.path.insert(0, str(HERE))
import pf_vocabulary as vocabulary  # noqa: E402

READING_SETS = {"RS1": ("strict", "default"), "RS3": ("ext", "any"), "RS5": ("within", "exception"),
                "RS9": ("strict", "default"), "RS18": ("inuse", "devonly"), "RS0": ("commitment", "prediction"),
                "RS8": ("rel", "pred"), "RS4": ("N", "P"), "RS12": ("suff", "iff"),
                "RS13": ("permission", "might"), "RS15": ("explanation", "rule")}


@dataclass(frozen=True)
class Block:
    id: str
    when: tuple
    source: str
    text: str


def read_blocks(name):
    lines = (HERE / name).read_text().splitlines()
    if len(lines) % 2:
        raise ValueError(f"{name}: a header has no block")
    out = []
    for header, sentence in zip(lines[::2], lines[1::2]):
        match = re.fullmatch(r"## ([a-z0-9-]+) \| ([^|]+) \| (.+)", header)
        if not match:
            raise ValueError(f"{name}: malformed header {header!r}")
        when = () if match[2] == "always" else tuple(tuple(s.strip().split("=")) for s in match[2].split("&"))
        if any(choice not in READING_SETS.get(set_id, ()) for set_id, choice in when):
            raise ValueError(f"{name}: bad reading {when}")
        out.append(Block(match[1], when, match[3], sentence))
    return tuple(out)


@lru_cache(maxsize=None)
def environment():
    from ve.softnorms import SoftEnvironment
    return SoftEnvironment(vocabulary.environment())


@lru_cache(maxsize=None)
def rule_blocks():
    return read_blocks("rules.d1.ve")


@lru_cache(maxsize=None)
def parsed_rule(block_id):
    from ve.norm_english import parse_english
    block = next(b for b in rule_blocks() if b.id == block_id)
    document = parse_english(environment(), block.text)
    if len(document.rules) != 1:
        raise ValueError(f"{block_id}: expected one rule")
    result = document.rules[0].to_dict()["norm"]
    result["name"] = block_id
    return json.dumps(result, sort_keys=True)


@lru_cache(maxsize=None)
def base_environment():
    from ve.environment import Environment
    data = vocabulary.environment()
    data["vocabulary"]["predicates"] = {n: e for n, e in data["vocabulary"]["predicates"].items()
                                          if "regulated" not in e}
    data["profiles"] = ["relational-fol@0"]
    return Environment(data)


@lru_cache(maxsize=None)
def facts():
    from ve.english import parse_english
    return tuple((b, tuple(parse_english(base_environment(), b.text).formulas))
                 for b in read_blocks("facts.d1.ve"))
