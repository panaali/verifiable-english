"""Build the four source-bound agent-policy question fixtures (plan §6.2).

The existing norm-English and English readers supply content. This script only
selects source sentences, records their byte spans, and writes documents. It
does not decide any question or replay a verdict.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from ve.ast import formula_to_data
from ve.english import parse_english
from ve.environment import Environment


HERE = Path(__file__).resolve().parent
POLICY = HERE.parents[1] / "agent-policy"
sys.path.insert(0, str(POLICY))
import check as agent  # noqa: E402

RECORDS = ("a10", "a13", "a25", "a26", "a27")
NAMES = ("a-unspecified", "a-deny", "a-rules", "a-conflict")


def environment(name: str) -> Environment:
    # The flag-free `.lean.json` copy omits `tool`'s functional/total contract,
    # which the authored rule and log English need. The full deny/deny source
    # has the same completion choice and keeps that contract.
    source = "environment.deny-neednot.json" if name == "a-deny" else "environment.unspecified.json"
    raw = json.loads((POLICY / source).read_text())
    raw["profiles"] = sorted(set(raw["profiles"]) | {"documents@1"})
    raw["vocabulary"]["constants"].update(json.loads((POLICY / "log.vocabulary.json").read_text())["constants"])
    return Environment(raw)


def _selected_log() -> list[str]:
    paragraphs = (POLICY / "log.ve").read_text().strip().split("\n\n")
    chosen = [paragraphs[0]]
    for paragraph in paragraphs[1:]:
        if any(f'"{record}"' in paragraph for record in RECORDS):
            # Every paragraph belongs to exactly one action; a reference to
            # another action in a formula does not change the record selection.
            first = paragraph.splitlines()[0]
            if any(f'"{record}"' in first for record in RECORDS):
                chosen.append(paragraph)
    if len(chosen) != 1 + len(RECORDS):
        raise ValueError("the agent log no longer has the five selected records")
    return [line for paragraph in chosen for line in paragraph.splitlines() if line]


def build(name: str) -> str:
    if name not in NAMES:
        raise ValueError(name)
    env = environment(name)
    original = (POLICY / "policy.ve").read_text()
    if name == "a-conflict":
        policy_text = original
    else:
        policy_text, _ = agent.mutant_edits.m1(original, "")
    rules = agent.policy(policy_text, agent.mutant_edits.names(), env).rules
    rule_lines = [line for line in policy_text.splitlines() if line]
    if len(rule_lines) != 26 or len(rules) != 26:
        raise ValueError("the policy no longer has 26 aligned rules")
    log_lines = [] if name == "a-rules" else _selected_log()
    if log_lines:
        read = parse_english(env, "\n".join(log_lines) + "\n")
        if len(read.formulas) != len(log_lines):
            raise ValueError("the log reader did not return one formula per source sentence")
        formulas = [formula_to_data(env, formula) for formula in read.formulas]
    else:
        formulas = []
    units = []
    offset = 0
    for number, (line, rule) in enumerate(zip(rule_lines, rules, strict=True), 1):
        end = offset + len((line + "\n").encode())
        units.append({"id": f"rule{number:02}", "span": [offset, end], "kind": "norm",
                      "meaning": "specified", "support": "none", "content": rule.to_dict()})
        offset = end
    for number, (line, formula) in enumerate(zip(log_lines, formulas, strict=True), 1):
        end = offset + len((line + "\n").encode())
        units.append({"id": f"record{number:03}", "span": [offset, end], "kind": "asserted",
                      "meaning": "specified", "support": "observation", "content": {"ast": formula}})
        offset = end
    meta = {"format": "ve-document@1", "environment": env.to_dict(), "units": units}
    return "---\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\n---\n" + \
        "".join(line + "\n" for line in [*rule_lines, *log_lines])


if __name__ == "__main__":
    for fixture in NAMES:
        (HERE / f"{fixture}.ve.md").write_text(build(fixture))
