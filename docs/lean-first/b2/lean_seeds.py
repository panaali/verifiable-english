"""Lean-side seeded bugs of lean-first batch 2: each is built into `ve_service` (its theorem's proof stubbed, since the
theorem itself refuses the seed at build time), listed in the lock for the run, tested and reverted.

    PATH=~/.elan/bin:$PATH uv run --frozen python docs/lean-first/b2/lean_seeds.py
"""
import json, subprocess, hashlib
from pathlib import Path
SEEDS = [
  ("S7 Lean registration is content-addressed: the digest check removed",
   "  unless caseDigest member.2 == digest do\n    throw s!\"InvalidInput: environment handle {digest} is not the SHA-256 of its text\"\n",
   "",
   ["tests/test_lean_handles.py::test_a_registration_whose_key_is_not_its_digest_is_refused"],
   ("  simp [registerOne, hk, hd, bind, Except.bind]\n", "  sorry\n")),
  ("S8 Lean answers a handle as the case with its environment: the case gets the table's first environment",
   "      | some env => pure (.obj ((kvs.erase handleKey).insert \"environment\" env))\n",
   "      | some env => pure (.obj ((kvs.erase handleKey).insert \"environment\" (h.table.values.headD env)))\n",
   ["tests/test_lean_handles.py::test_handles_answer_the_evaluation_corpus_as_resending_does"],
   ("  | error _ => simp [hd, ht, pure, Except.pure]\n", "  | error _ => sorry\n")),
  ("S9 Lean's table holds maxHandles environments: it empties at 3",
   "      if h.table.size + 1 > maxHandles || h.bytes + size > maxHandleBytes then {} else h\n",
   "      if h.table.size + 1 > 3 || h.bytes + size > maxHandleBytes then {} else h\n",
   ["tests/test_lean_handles.py::test_the_client_mirrors_the_services_eviction"],
   ("", "")),
]
protocol, lock = Path("lean/VE/Service/Protocol.lean"), Path("lean/checkers.lock")
original_lock = lock.read_text()
for name, old, new, tests, (proof, stub) in SEEDS:
    s = protocol.read_text(); assert old in s and proof in s, name
    protocol.write_text(s.replace(old, new, 1).replace(proof, stub, 1))
    try:
        b = subprocess.run(["lake", "build", "ve_service"], cwd="lean", capture_output=True, text=True)
        if b.returncode: print(name, "BUILD FAILED", b.stdout[-1500:]); continue
        digest = hashlib.sha256(Path("lean/.lake/build/bin/ve_service").read_bytes()).hexdigest()
        data = json.loads(original_lock); data["ve_service"].append(digest)
        lock.write_text(json.dumps(data, indent=2) + "\n")
        proc = subprocess.run(["uv", "run", "--frozen", "pytest", "-q", "-p", "no:randomly", *tests],
                              capture_output=True, text=True, timeout=1500)
        tail = [l for l in proc.stdout.splitlines() if l.strip()][-1]
        print(name, "->", "CAUGHT" if proc.returncode != 0 else "MISSED", "|", tail, flush=True)
        for line in proc.stdout.splitlines():
            if line.startswith("FAILED"): print("   ", line[:160])
    finally:
        subprocess.run(["git", "checkout", "--", str(protocol)], check=True)
        lock.write_text(original_lock)
b = subprocess.run(["lake", "build", "ve_service"], cwd="lean", capture_output=True, text=True)
print("rebuilt", b.returncode, hashlib.sha256(Path("lean/.lake/build/bin/ve_service").read_bytes()).hexdigest())
