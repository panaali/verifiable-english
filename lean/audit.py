"""Re-run every named theorem's Lean transitive-axiom audit and enforce policy."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
actual = set()
for source in sorted((ROOT / "VE").glob("*.lean")):
    text = source.read_text()
    namespace = re.search(r"^namespace (\S+)", text, re.M)
    declarations = re.findall(r"^theorem (\w+)", text, re.M)
    if declarations:
        assert namespace, source
        actual.update(f"{namespace[1]}.{name}" for name in declarations)
    assert not re.search(r"\b(sorry|axiom|unsafe|native_decide|implemented_by)\b", text), source
recorded = set(re.findall(r"^#print axioms (\S+)", (ROOT / "VE/Audit.lean").read_text(), re.M))
assert actual == recorded, {"missing": actual - recorded, "extra": recorded - actual}
result = subprocess.run(["lake", "env", "lean", "VE/Audit.lean"], cwd=ROOT,
                        text=True, capture_output=True, check=True)
seen = set()
for line in result.stdout.splitlines():
    match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
    if not match:
        raise AssertionError(f"Unexpected audit output: {line}")
    name, _, dependencies = match.groups()
    seen.add(name)
    axioms = set(dependencies.split(", ")) if dependencies else set()
    assert axioms <= ALLOWED, (name, axioms - ALLOWED)
assert seen == actual
print(result.stdout, end="")
print(f"PASS: {len(seen)} named theorems; only the declared standard axiom allowlist.")
