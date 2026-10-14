"""DF-0 item 4: the plain-default probe (docs/research/defeasible-phase1.md 1.4, committed first).

    uv run python research/defeasible/probe_plain_default.py

Writes one `ve-document@1` per variant under the evidence directory and records, verbatim, what `ve document check`
and `ve document render` do with it today. Every `ve` run is under `prlimit --as=6442450944`.
"""
from __future__ import annotations

import json
import subprocess
import sys

from common import EVIDENCE, ROOT, write_json

LIMIT = ["prlimit", "--as=6442450944"]
PROFILES = ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
OPERATOR = {"operator": {"description": "an operator", "verbalisation": {"singular": "operator",
                                                                        "plural": "operators"}}}
EXCEPTION = {"decided_by": "operator", "sufficient": [], "necessary": [], "factors": []}


def environment(predicates, profiles=PROFILES):
    return {"language": "ve.core@0.2", "profiles": profiles, "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": OPERATOR, "predicates": predicates, "constants": {}}}


def g1(predicate):
    return {"norm": {"name": "g1", "predicate": predicate, "sign": True, "guard": ["top"], "unless": [],
                     "over": [], "mode": "default", "exception": dict(EXCEPTION)}}


# Spec 8.1 (draft 2): plain `instructs(operator)`, `unspecified`.
SPEC = ({"instructs": {"arguments": ["operator"], "description": "{0} instructs", "verbalisation": "{0} instructs",
                       "regulated": {"role": "plain", "default": "unspecified"}}},
        "instructs", "Every operator instructs, unless an exception applies.\n")
# Plan table 4.1 (draft 3): the same rule over `instructs_via_system_prompt`, with its verbalisation.
PLAN = ({"instructs_via_system_prompt": {
            "arguments": ["operator"], "description": "{0} gives its instructions in the system prompt",
            "verbalisation": "{0} gives its instructions in the system prompt",
            "regulated": {"role": "plain", "default": "unspecified"}}},
        "instructs_via_system_prompt",
        "Every operator gives its instructions in the system prompt, unless an exception applies.\n")
# Control (not the plan's item): g1 on a declared obligation with its dual permission.
CONTROL = ({"instruct_required": {"arguments": ["operator"], "description": "{0} is required to instruct",
                                  "regulated": {"role": "obligation", "default": "unspecified",
                                                "act": "{0} instruct", "permission": "instruct_permitted"}},
            "instruct_permitted": {"arguments": ["operator"], "description": "{0} may instruct",
                                   "regulated": {"role": "permission", "default": "unspecified",
                                                 "act": "{0} instruct"}}},
           "instruct_required", "Every operator should instruct.\n")


def without_defaults(predicates):
    """Post hoc (added after the pre-registered variants were refused at load): the same predicates completed by
    `deny`, under the profiles without `norm-defaults@0`, so that the document reaches the soft route."""
    out = json.loads(json.dumps(predicates))
    for decl in out.values():
        decl["regulated"]["default"] = "deny"
    return out


def document(predicates, predicate, source, profiles=PROFILES):
    front = {"format": "ve-document@1", "environment": environment(predicates, profiles),
             "units": [{"id": "g1", "span": [0, len(source.encode())], "kind": "norm", "meaning": "specified",
                        "support": "assumption", "content": g1(predicate)}]}
    return "---\n" + json.dumps(front, indent=1) + "\n---\n" + source


def ve(*args):
    run = subprocess.run([*LIMIT, sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
    return {"argv": ["ve", *args], "exit": run.returncode, "stdout": run.stdout, "stderr": run.stderr}


def main():
    out = EVIDENCE / "plain-default-probe"
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    soft_only = [p for p in PROFILES if p != "norm-defaults@0"]
    variants = [(name, predicates, predicate, source, PROFILES, False)
                for name, (predicates, predicate, source) in (("spec-8.1", SPEC), ("plan-4.1", PLAN),
                                                              ("control-obligation", CONTROL))]
    variants += [(name + "-deny", without_defaults(predicates), predicate, source, soft_only, True)
                 for name, (predicates, predicate, source) in (("spec-8.1", SPEC), ("plan-4.1", PLAN),
                                                               ("control-obligation", CONTROL))]
    for name, predicates, predicate, source, profiles, post_hoc in variants:
        path = out / f"{name}.ve.md"
        path.write_text(document(predicates, predicate, source, profiles))
        rel = str(path.relative_to(ROOT))
        results[name] = {"document": rel, "post_hoc": post_hoc, "check": ve("document", "check", rel),
                         "render": ve("document", "render", rel)}
    write_json("plain-default-probe.json", {
        "expected_by_plan": "check passes, render refuses with ve/norm_english.py:398's text",
        "results": results})
    for name, row in results.items():
        for step in ("check", "render"):
            r = row[step]
            print(f"{name} {step}: exit {r['exit']}; {(r['stdout'] + r['stderr']).strip()[:300]}")


if __name__ == "__main__":
    main()
