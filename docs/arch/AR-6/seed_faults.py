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
    ("the Lean-owned sites may grow", LINT,
     "for (path, domain), n in sorted((lean(head) - lean(base)).items())",
     "for (path, domain), n in sorted((lean(base) - lean(head)).items())",
     TESTS + "test_the_lean_owned_sites_only_shrink"),
    ("a concatenation is read part by part", LINT,
     "    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):",
     "    if False:",
     TESTS + 'test_seeded_preimages_in_a_relayed_module_fail[return digest("ve-report-" + v + "\\\\n", p)'
             '-ve-report-{}\\n]'),
    ("a Python record may use a Lean-owned domain", LINT,
     "        elif owner == \"python\" and entry[\"domain\"].startswith(LEAN_PREFIXES):",
     "        elif False:",
     TESTS + "test_a_python_entry_names_a_record_of_d7_and_no_lean_domain[proposals-ve-meaning-{}\\n-False]"),
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
