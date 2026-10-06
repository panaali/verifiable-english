"""Seeded bugs for lean-first batch 9: each must make its test fail; every file is restored.

    python3 -I docs/lean-first/b9/mutants.py > docs/lean-first/b9/evidence/mutants.txt

A Lean mutant's build is allowed in `lean/checkers.lock` while its test runs, so the test fails on the
answer, not on the build pin; the clean build is restored and checked against the lock after each.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools import nested_pytest  # noqa: E402
LOCK = ROOT / "lean/checkers.lock"
SERVICE = ROOT / "lean/.lake/build/bin/ve_service"
ENV = {**os.environ, "VE_NATIVE_PREBUILT": "1", "PATH": f"{Path.home()}/.elan/bin:{os.environ['PATH']}"}

MUTANTS = [
    ("M1 Lean check mode answers the erased core", "lean", "lean/VE/Service/Standalone.lean",
     '("Q", a.Q), ("core", a.core),', '("Q", a.Q), ("core", a.Q),',
     ["tests/test_units_lean_w6a.py::test_news_admission_agrees_with_the_relay"]),
    ("M2 either W6 field selects Lean's decoder", "lean", "lean/VE/Service/Standalone.lean",
     ' || (environment.getObjVal? "units").isOk then', ' then',
     ["tests/test_units_relay_w6a.py::test_either_w6_field_takes_lean_s_decoder"]),
    ("M3 a W6 environment is admitted by Lean before Python constructs it", "python", "ve/environment.py",
     '"time@0" in data["profiles"] and "risk@0" not in data["profiles"]):',
     '"time@9" in data["profiles"] and "risk@0" not in data["profiles"]):',
     ["tests/test_units_relay_w6a.py::test_every_display_collision_class_rejects"]),
    ("M4 an exhausted certificate replay is ResourceLimit, never false", "python", "ve/units.py",
     '''    [row] = decide("quantity", [{"id": "certificate", "kind": "certificate",
                                "environment": env.to_dict(), "premises": premises,
                                "conclusion": conclusion, "certificate": certificate}])
    return row["valid"]''',
     '''    from .errors import ResourceLimit
    try:
        [row] = decide("quantity", [{"id": "certificate", "kind": "certificate",
                                    "environment": env.to_dict(), "premises": premises,
                                    "conclusion": conclusion, "certificate": certificate}])
    except ResourceLimit:
        return False
    return row["valid"]''',
     ["tests/test_w6a_certificate_steps.py::test_quantity_certificates_share_the_step_budget"]),
    ("M5 Rust refuses a quantity case", "rust", "rust/ve/src/main.rs",
     'return Err(Error::new("UnsupportedProfile", "quantities are checked by the Lean quantity route"));',
     'return Ok(json!({"id": v.get("id").cloned().unwrap_or(json!("")), "status": "ok"}));',
     None),
]


def main():
    lock = LOCK.read_text()
    for name, kind, relative, old, new, tests in MUTANTS:
        path = ROOT / relative
        original = path.read_text()
        assert original.count(old) == 1, (name, original.count(old))
        path.write_text(original.replace(old, new))
        try:
            if kind == "lean":
                built = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", env=ENV,
                                   capture_output=True, text=True, timeout=3000)
                assert built.returncode == 0, built.stdout[-2000:]
                digest = hashlib.sha256(SERVICE.read_bytes()).hexdigest()
                LOCK.write_text(lock.replace('"ve_service": [', f'"ve_service": [\n    "{digest}",', 1))
            if kind == "rust":
                done = subprocess.run(["cargo", "test", "-q", "-p", "ve", "quantity"], cwd=ROOT / "rust",
                                      env=ENV, capture_output=True, text=True, timeout=3000)
            else:
                done = subprocess.run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *tests],
                                                            python=[str(ROOT / ".venv/bin/python")]),
                                      cwd=ROOT, env=nested_pytest.environment(ENV), capture_output=True,
                                      text=True, timeout=3000)
            output = done.stdout + done.stderr
            failed = done.returncode != 0 and ("FAILED" in output or "test result: FAILED" in output
                                               or "panicked" in output)
            tail = "\n    ".join(line for line in output.strip().splitlines()[-6:])
            print(f"{name}: exit={done.returncode} failed={failed}\n    {tail}", flush=True)
            assert failed, name
        finally:
            path.write_text(original)
            LOCK.write_text(lock)
            if kind == "lean":  # the next mutant runs against the clean, pinned build
                clean = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", env=ENV,
                                       capture_output=True, text=True, timeout=3000)
                assert clean.returncode == 0
                assert hashlib.sha256(SERVICE.read_bytes()).hexdigest() in lock
    rebuilt = subprocess.run(["lake", "build", "ve_service"], cwd=ROOT / "lean", env=ENV,
                             capture_output=True, text=True, timeout=3000)
    assert rebuilt.returncode == 0
    digest = hashlib.sha256(SERVICE.read_bytes()).hexdigest()
    assert digest in lock, digest
    print(f"all mutants removed; ve_service rebuilt clean ({digest[:12]}, pinned)", flush=True)


if __name__ == "__main__":
    main()
