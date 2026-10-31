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
                "RS13": ("permission", "might"), "RS15": ("explanation", "rule"),
                "RS2": ("nest", "sep"), "RS4s": ("scoped", "unscoped"), "RS6": ("req", "desc"),
                "RS7": ("noinput", "nodelib"), "RS10": ("publication", "unstated"), "RS11": ("final", "process"),
                "RS14": ("appointment", "unstated"), "RS16": ("coupled", "option"), "RS17": ("bperm", "bmight")}
# Rule priority the text states (PLAN 3.1): F11's adjustment is an exception to the High deployment rule, and N2
# gives the "For the avoidance of doubt" clause priority over the requirement it qualifies.
PRECEDENCE = {"f11-exception": ("f2-deploy", "f2-deploy-any", "f2-reminder", "f2-reminder-any"),
              "f16-without-noinput": ("f16-informed",)}
N2_PRECEDENCE = ("f16-without-noinput", "f16-informed")
# RS0 (PLAN 3.1): process statements in the future or present tense ("we will", "we compile", "we do not
# deploy", "every covered model undergoes"). N1 narrows each to a commitment; without N1 they are predictions.
RS0_STATEMENTS = ("f2-no-deploy", "f2-no-deploy-any", "f4-security", "f7-evaluations", "f7-report", "f8-start",
                  "f9-report", "f9-risk-paths", "f9-specific", "f9-efficacy", "f9-threshold", "f10-validate",
                  "f10-review", "f13-review", "f13-results", "f14-document", "f14-investigate", "f14-corrective",
                  "f15-disclose", "f15-safeguards", "f15-third-party", "f16-ssc-visibility", "f16-year")


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
