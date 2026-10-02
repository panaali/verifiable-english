"""Writes the environment files of the agent-policy case from one declaration.

The policy states no completion default for either regulated predicate, so the
case ships one environment per pair of defaults (PLAN section 3.2), plus the
flag-free copy that the Lean norms route accepts (PLAN section 8), and one with
both completions unspecified under norm-defaults@0. Run
`python usecases/agent-policy/environments.py` to regenerate them; the test
checks that the committed files equal this output.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

TOOLS = ("read_file", "write_file", "delete_file", "shell", "web_fetch", "send_email",
         "post_message", "purchase", "get_secret", "schedule_task", "spawn_agent")


def _unary(sort, word, decider):
    return {"arguments": [sort], "description": f"{{0}} is {word}, as recorded by {decider}",
            "verbalisation": f"{{0}} is {word}", "negative_verbalisation": f"{{0}} is not {word}"}


def _effect(sort, verb, decider):
    return {"arguments": ["action", sort], "description": f"{{0}} {verb} {{1}}, as recorded by {decider}",
            "verbalisation": f"{{0}} {verb} {{1}}"}


PREDICATES = {
    "tool": {"arguments": ["action", "$string"], "functional": True, "total": True,
             "description": "the tool that the agent harness records for the action",
             "verbalisation": "{0} uses {1}"},
    "reads": _effect("file", "reads", "the file tools and the shell tracer"),
    "writes": _effect("file", "writes", "the file tools and the shell tracer"),
    "deletes": _effect("file", "deletes", "the file tools and the shell tracer"),
    "contacts": _effect("host", "contacts", "the network layer"),
    "messages": _effect("person", "messages", "the mail and chat tools"),
    "discloses": _effect("secret", "discloses", "the data-loss scanner"),
    "resides_in": {"arguments": ["file", "directory"],
                   "description": "{0} resides in {1}, as resolved by the path resolver",
                   "verbalisation": "{0} resides in {1}",
                   "negative_verbalisation": "{0} does not reside in {1}"},
    "confidential": _unary("file", "confidential",
                           "the path resolver: the file is on the credential path list"),
    "tracked": _unary("file", "tracked", "git: the file is under version control"),
    "allowlisted": _unary("host", "allowlisted", "the network layer: the host is on the network allowlist"),
    "principal": _unary("person", "principal", "the harness: the person is the user the agent works for"),
    "confirmed": _unary("action", "confirmed", "the harness: the user confirmed the action in a dialog"),
    "readonly": _unary("action", "readonly", "the shell classifier: the command changes nothing"),
    "privileged": _unary("action", "privileged", "the shell: the action runs with elevated privileges"),
    "affordable": _unary("action", "affordable",
                         "the payment tool: the amount is within the spending limit"),
    "reported": _unary("action", "reported", "the harness: the action was reported to the user"),
    "permitted": {"arguments": ["action"], "description": "the agent may perform the action",
                  "regulated": {"role": "permission", "default": "deny", "act": "{0} be performed"}},
    "report_required": {"arguments": ["action"], "description": "the agent must report the action to the user",
                        "regulated": {"role": "obligation", "default": "deny",
                                      "act": "{0} be reported to the user"}},
}

BASE = {
    "language": "ve.core@0.2",
    "profiles": ["data@0", "norms@0", "relational-fol@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {
            "action": {"description": "an action in the agent's log"},
            "file": {"description": "a file path, as resolved by the path resolver"},
            "host": {"description": "a network host"},
            "person": {"description": "a message recipient"},
            "secret": {"description": "a secret value found by the data-loss scanner"},
            "directory": {"description": "a directory, such as the agent's workspace"},
        },
        "predicates": PREDICATES,
        "constants": {
            **{name: {"sort": "$string", "description": f"the {name} tool"} for name in TOOLS},
            "workspace": {"sort": "directory", "description": "the workspace directory of the agent's task"},
        },
    },
}

# File name suffix -> (permitted default, report_required default).
VARIANTS = {
    "deny-neednot": ("deny", "deny"),
    "deny-must": ("deny", "allow"),
    "allow-neednot": ("allow", "deny"),
    "allow-must": ("allow", "allow"),
}


def variant(permitted, report):
    data = copy.deepcopy(BASE)
    predicates = data["vocabulary"]["predicates"]
    predicates["permitted"]["regulated"]["default"] = permitted
    predicates["report_required"]["regulated"]["default"] = report
    return data


def lean_variant():
    """The deny-neednot environment without the `tool` flags (PLAN section 8, finding A)."""
    data = variant("deny", "deny")
    tool = data["vocabulary"]["predicates"]["tool"]
    del tool["functional"], tool["total"]
    return data


def unspecified_variant():
    """Both completions `unspecified` under norm-defaults@0 (docs/spec/norm-defaults.md
    fixture u4): the policy states neither default, and this says so."""
    data = variant("unspecified", "unspecified")
    data["profiles"] = sorted({*data["profiles"], "norm-defaults@0"})
    return data


def unspecified_file():
    return {"environment.unspecified.json": json.dumps(unspecified_variant(), indent=2) + "\n"}


def files():
    out = {f"environment.{name}.json": variant(*defaults) for name, defaults in VARIANTS.items()}
    out["environment.lean.json"] = lean_variant()
    return {name: json.dumps(data, indent=2) + "\n" for name, data in out.items()}


if __name__ == "__main__":
    for name, text in {**files(), **unspecified_file()}.items():
        (HERE / name).write_text(text)
