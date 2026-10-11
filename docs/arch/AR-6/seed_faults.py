"""Plant each AR-6 lint fault, prove its named test fails, then restore the source (evidence/mutants.json)."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402  (the one builder of a nested pytest command)
LINT = "tools/identity_lint.py"
TESTS = "tests/test_identity_lint.py::"
CASES = [
    ("rule 1 reads only domain forms in a relayed module", LINT,
     "    if relayed and value.startswith(LEAN_PREFIXES) and not value.startswith(\"ve-document@\"):",
     "    if False:",
     TESTS + 'test_seeded_preimages_in_a_relayed_module_fail[DOMAIN = "ve-report-"\\n    return digest(DOMAIN + v '
             '+ "\\\\n", p)-ve-report-]'),
    ("rule 2 reads relayed modules only", LINT,
     "        if domain is not None:\n",
     "        if domain is not None and in_relay:\n",
     TESTS + 'test_rule_two_reads_domain_literals_in_every_module[return digest("ve-my-record-v1\\\\n", p)-True]'),
    ("a stale entry passes", LINT,
     "        if extra > 0:\n            out.append",
     "        if False:\n            out.append",
     TESTS + "test_an_entry_whose_site_is_gone_is_stale"),
    ("the sites may grow", LINT,
     "for (path, domain, owner), n in sorted((counted(head) - counted(base)).items())",
     "for (path, domain, owner), n in sorted((counted(base) - counted(head)).items())",
     TESTS + "test_the_sites_only_shrink_whatever_their_owner"),
    ("only the Lean-owned sites are ratcheted", LINT,
     "for e in entries if type(e) is dict)",
     "for e in entries if type(e) is dict and e.get(\"owner\") == \"lean\")",
     TESTS + "test_the_sites_only_shrink_whatever_their_owner"),
    ("a domain may change owner against the base", LINT,
     "for domain in sorted(old.keys() & new.keys()) if old[domain] != new[domain]]",
     "for domain in sorted(old.keys() & new.keys()) if False]",
     TESTS + "test_no_domain_changes_owner_or_gains_a_second_one[ve-bundle-v0\\n]"),
    ("a domain may have two owners", LINT,
     "for domain, names in sorted(owners(entries).items()) if \"/\" in names]",
     "for domain, names in sorted(owners(entries).items()) if False]",
     TESTS + "test_no_domain_changes_owner_or_gains_a_second_one[ve-bundle-v0\\n]"),
    ("a domain Lean computes may be Python's", LINT,
     "        elif owner == \"python\" and lean_holders(entry[\"domain\"]):",
     "        elif False:",
     TESTS + "test_a_domain_lean_computes_cannot_be_python_owned[ve-claim-v1\\n]"),
    ("main ignores --base", LINT,
     "    if base is not None:\n        out = growth(base, entries)",
     "    if False:\n        out = growth(base, entries)",
     TESTS + "test_main_with_base_fails_on_a_grown_allowlist[drop python]"),
    ("the relay lint's helpers are not relayed", LINT,
     "for path in modules + relay_lint.helpers([p for p in modules if p.is_file()]):",
     "for path in modules:",
     TESTS + "test_the_relayed_modules_come_from_the_relay_lint"),
    ("a nested function of a relayed function is not relayed", LINT,
     "(bool(relayed) and scope.split(\".\", 1)[0] in relayed)",
     "(bool(relayed) and scope in relayed)",
     TESTS + "test_only_the_relayed_functions_of_a_module_are_relayed"),
    ("`.encode()` is not read as part of a string expression", LINT,
     "    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == \"encode\":",
     "    if False:",
     TESTS + 'test_rule_two_reads_domain_literals_in_every_module[return digest("ve-meaning-".encode() + v + '
             'b"\\\\n", p)-True]'),
    ("a concatenation is read part by part", LINT,
     "    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):",
     "    if False:",
     TESTS + 'test_seeded_preimages_in_a_relayed_module_fail[return digest("ve-report-" + v + "\\\\n", p)'
             '-ve-report-{}\\n]'),
    ("a Python record may use a Lean-owned domain", LINT,
     "        elif owner == \"python\" and entry[\"domain\"].startswith(LEAN_PREFIXES):",
     "        elif False:",
     TESTS + "test_a_python_entry_names_a_record_of_d7_and_no_lean_domain[proposals-ve-meaning-unheld-v9\\n-False]"),
]


def main() -> None:
    records = []
    for name, relative, before, after, test in CASES:
        path = ROOT / relative
        original = path.read_text()
        if original.count(before) != 1:
            raise RuntimeError(f"expected one mutation site for {name}")
        try:
            path.write_text(original.replace(before, after, 1))
            run = subprocess.run(nested_pytest.command(["-q", test]), cwd=ROOT,
                                 env=nested_pytest.environment(os.environ), capture_output=True, text=True,
                                 check=False)
        finally:
            path.write_text(original)
        output = run.stdout + run.stderr
        if run.returncode == 0 or "1 failed" not in output:
            raise RuntimeError(f"{name}: expected a test failure, got {run.returncode}: {output[-1000:]}")
        records.append({"bug": name, "file": relative, "test": test,
                        "exit_code": run.returncode, "failure_excerpt": output[-1200:]})
    evidence = ROOT / "docs/arch/AR-6/evidence/mutants.json"
    evidence.write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(records)} seeded faults caught")


if __name__ == "__main__":
    main()
