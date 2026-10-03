# S4 item 1 integration verification

The integration branch merges `wire-s4/py` and `wire-s4/lean`. The public
admission fixtures exercise `ve.admission.admit_document` on S1–S4 and compare
the raised error with the legacy validator's error. The three-way fixture
compares the full record written in the item-1 specification with the public
admission error, the Python engine and `ve_diagnose` on those same sources.
The accepted admission fixture checks the public entry point as well.

## L2: Lean rows across the switch

The revision-3 `ve_diagnose` binary was built in the `wire-s4/lean` checkout at
`15ed338c` (SHA-256
`9d9f4e692da437d76acc8b399a01dca5dc68e042d0bbeb1ce5e77a8764602dd4`).
The revision-4 binary was built in this integration checkout (SHA-256
`abad4e1ac604b69d7a814346cbc597ac976e94173bb27fd498b7e451247164fa`).
Both received the 8,574 cases that Lean reads from the current
`conformance.wire_contract_gate.gate_cases` corpus. Each returned 7,452 fault
records. All 8,574 response rows were equal after removing only the
`revision` member from each diagnostic. Every old fault record had revision 3,
and every new fault record had revision 4.

## Gates

Run in this worktree on Python 3.12.3, without model calls:

- `PATH=~/.elan/bin:$PATH lake build` in `lean/`: 544 jobs passed.
- `python lean/audit.py`: 2,819 theorem declarations; standard axiom allowlist only.
- `cargo test --workspace --locked -j 2` in `rust/`: passed.
- Full non-live pytest suite with four workers: 5,747 passed, 6 optional skips.
- `python -m conformance.wire_contract_gate --check`: 8,578 cases, zero
  mismatches, no unmet coverage and no legacy verdict difference.
- `tools/wire_contract.py --check`, `lean/VE/Route/frozen.py`,
  `tools/check_lean_imports.py`, and the delta report check: passed.

The remaining S4 plan items 2–6 need their own statement specifications.
They are outside the item-1 public switch.

## Review fixes (2026-10-03)

After the fixes of the wire-s4 reviews (spec section 15), in this worktree, without model calls:

- `lake build`: 544 jobs passed; `python lean/audit.py`: 2,819 theorem declarations, standard axiom
  allowlist only. No Lean or Rust source changed, so `cargo test` was not rerun.
- `python -m conformance.wire_contract_gate --check`: 8,796 cases, zero mismatches, no unmet coverage, no
  legacy verdict or code difference; 498 text changes in seven signed checks.
- `tools/wire_contract.py --check`, `lean/VE/Route/frozen.py`, `tools/check_lean_imports.py` and the delta
  report check: passed.
- Full non-live pytest suite with four workers: 5,754 passed, 6 optional skips.
