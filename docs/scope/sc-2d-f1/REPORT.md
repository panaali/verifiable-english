# sc-2d-f1: pin spec 5.4's effect-statement binders from the elaborated statements — build report

Status: **done**. No DRI signature reserved, no DELTA row (tests and docs only), trust +0. Base `0295df1743`.
SIZE: 0 product, 227 tests, 6 other hand-written lines (plus this report); the review fix (F1) added 85 test lines.
Pilot: 0 bytes (tests and docs only); nothing claimed. Next: none.

## Deliverables

| Row | Result |
|---|---|
| (1) Binders from `lean/statements.txt`, compared with spec 5.4 | `tests/test_scope_5_4_statements.py`: `typed` reads the elaborated statement of `VE.Scope.<name>` from the generated `lean/statements.txt`; `telescope` splits it into `∀` groups of every bracket kind and anonymous `A →` premises, up to the conclusion (a `∀` binder without brackets raises, never skips). `spec_binders` reads every bracketed binder of spec 5.4's text (`(..)`, `{..}`, `⦃..⦄`, `[..]`). `binder_faults` requires the spec's binders to be exactly the pinned explicit names, and the elaborated telescope to match them binder for binder: a name without an `h` prefix stays a named `(x : T)`, a hypothesis is an anonymous premise, and the premise at `hw` is `VE.Scope.JsonWF o`. The regex over explicit `(..)` binders (`binders`) is deleted. The source-equals-spec comparison is unchanged. |
| (2) A test that fails on an added implicit or instance binder in both texts | `test_a_binder_added_to_both_texts_fails` (25 cases: `{hx : True}`, `[inst : Inhabited Nat]`, `[Inhabited Nat]`, `⦃hx : True⦄`, `(hx : True)` × the five), plus `test_an_effect_statement_takes_exactly_the_signed_premises` on the real files. Real planted edits below. |
| (3) docs/scope/sc-2d/REPORT.md:13 | Now states what the pin checks, and what it does not: a premise's or the conclusion's type changed in both texts with the binders kept (only `hw`'s elaborated type is read). |
| (4) docs/scope/sc-2c/REPORT.md:4 | Now: F-raw-effect (`Examples.lean:1165`, `#guard` :1180) refutes only the three effect identities (the `N' = { N with .. }` conjunct of `reguard_applies`, `restrict_applies`, `carveOut_applies`), not typing preservation or commutation. Line 5 said all five "are false on a raw rule tree", the same overclaim; it now says the first three are, and no fixture shows the other two false. |

## Planted edits in both texts (deliverable 2)

Each was planted in `lean/VE/Scope/Theorems.lean` and in `docs/spec/scope.md` at the same place (before `(hw : JsonWF o)`), built with `lake build VE.Scope.Theorems`, and printed with `tools/lean_statements.py`'s own `SCRIPT` (its `import VE` narrowed to `import VE.Scope.Theorems`). The printed block was then spliced into `lean/statements.txt`. Both test files ran through a driver that loads `proof_cut` alone, because `tools/check_readings_defaults_statements.py`'s import-time inventory guard refuses a Lean tree whose inventory was not rebuilt. Afterwards everything was restored with `git checkout` and the module rebuilt.

| Plant | Lean printed | main's test (`git show main:tests/test_scope_5_4_statements.py`) | this branch's test |
|---|---|---|---|
| `{hx : True}` in `reguard_applies` | `∀ {hx : True}, VE.Scope.JsonWF o → …` | `18 passed` (the sc-2d overclaim) | `FAILED …test_an_effect_statement_takes_exactly_the_signed_premises[reguard_applies]`, `1 failed, 42 passed` |
| `[inst : Inhabited Nat]` in `carveOut_applies` | `∀ [inst : Inhabited Nat], VE.Scope.JsonWF o → …` | `18 passed` | `FAILED …[carveOut_applies]`, `1 failed, 42 passed` |

Restored: `uv run pytest -q tests/test_scope_5_4_statements.py`: `43 passed`.

## Seeded bugs (Python, the changed test file; each planted alone, then restored with `git checkout`)

No product code changed in any language. The bugs are planted in the new checker itself.

| Bug | File | Fails |
|---|---|---|
| The planted binders: `{hx : True}` and `[inst : Inhabited Nat]` in both texts | lean/VE/Scope/Theorems.lean, docs/spec/scope.md, lean/statements.txt | `test_an_effect_statement_takes_exactly_the_signed_premises[reguard_applies]` and `[carveOut_applies]` (above) |
| M1 `groups` skips every non-`(` bracket group | tests/test_scope_5_4_statements.py | `test_a_binder_added_to_both_texts_fails[{hx : True}-reguard_applies]` and the other `{..}`, `[..]` and `⦃..⦄` cases |
| M2 `telescope` reads only the leading `∀` (stops at a `∀` after a premise) | tests/test_scope_5_4_statements.py | `test_an_effect_statement_takes_exactly_the_signed_premises[reguard_applies]`, `[restrict_applies]`, `[carveOut_applies]`, `[commute_applies]` (4 failed, 39 passed) |
| M3 the elaborated type at `hw` is not read | tests/test_scope_5_4_statements.py | `test_the_check_tells_a_changed_statement` (1 failed, 42 passed) |

## Review fix (sc-2d-f1-review.final.md)

| Finding | Fix | Regression tests |
|---|---|---|
| F1 (B): `def Typed` (spec 5.4, docs/spec/scope.md:1272) was not compared; `Typed := True` passed all 18 checks | The class (a declaration of the spec block outside a hand list is never compared) is removed: `approved()` reads every declaration of spec 5.4's Lean block with the RD statement gate's shared parser (`tools/check_readings_defaults_statements.declarations`: a theorem to its proof's `:=`, a definition with its body), and `declaration_faults` compares each with the Lean source. `PROVED` is now derived from the block, not listed by hand; `EXPECTED` pins the kinds (8 theorems, 1 def). | `test_every_declaration_of_spec_5_4_is_the_lean_text[*]` (9), `test_a_vacuous_declaration_fails[*]` (9: each def body, and each theorem's conclusion, replaced by `True`), `test_spec_5_4_declares_the_reviewed_declarations` |

PROBE F1, run as given: before the fix `18 passed, 25 deselected` and `AssertionError: Typed := True was accepted by the statement gate`; after it, exit 0 with `FAILED …test_every_declaration_of_spec_5_4_is_the_lean_text[def Typed]` (the other 9 failures under the probe are `test_a_vacuous_declaration_fails`, whose baseline check sees the mutated source).

Seeded bugs for F1 (each planted alone, then restored with `git checkout` or the reverse edit):

| Bug | File | Fails |
|---|---|---|
| `def Typed … : Prop := True` in the Lean source | lean/VE/Scope/Theorems.lean | the probe's substitution: `test_every_declaration_of_spec_5_4_is_the_lean_text[def Typed]`. Planted in the file itself, the module no longer builds (`applyEffect_typed`'s proof: `Insufficient number of fields for ⟨...⟩`), and the test file's import-time inventory guard stops collection with `error: build failed` |
| M4 `declaration_faults` compares only theorems (main's behaviour) | tests/test_scope_5_4_statements.py | `test_a_vacuous_declaration_fails[def Typed]` (1 failed, 17 passed of the two new tests) |

## Checks run

- Review fix: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 72b6f0aac5: 3 shards on GitHub Actions, 32 units passed, exit 0. `lake build`: completed (1390 jobs); `python3 lean/audit.py`: PASS (845 files, 9479 theorems). `tests/test_scope_5_4_statements.py`: 62 passed (43 before the fix).
- `uv run pytest -q tests/test_scope_5_4_statements.py`: 43 passed (18 before: the new cases are the 25 plants).
- Chain run 1 (selected tests, 3 shards): `tests/test_inventory_path.py::test_no_train_only_path_is_read_outside_the_accessor` failed: `typed` read `ROOT / "lean/statements.txt"` directly. Fixed: it reads the list through the accessor, `lean_statements.inventory_path(lean_statements.STATEMENTS)` (which refuses a stale inventory). Afterwards that test and `tests/test_scope_5_4_statements.py` (43) pass.
- `uv run python tools/select_tests.py --paths <p>` selects `tests/test_scope_5_4_statements.py` for each of `lean/statements.txt` (the new input), `docs/spec/scope.md` and `lean/VE/Scope/Theorems.lean`, and for `--base $(git merge-base HEAD main)`.
- `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS.
- `light-lane.py check`: before the review fix `LIGHT 148 changed lines outside generated files <= 150 (3 files), no trusted-core file`; after it `NOT 318 changed lines outside generated files > 150 (4 files) against 0295df17` (size only: still no trusted-core file), so the branch takes the normal lane. No trust_mutants sweep (no product code).
- Overlap: no in-flight `feature/*`, `lean-first/*`, `infra/*` or `foundation/*` branch touches these files.
- Spec re-read: `reguard_applies`, `restrict_applies`, `carveOut_applies`, `applyEffect_typed`, `commute_applies` against docs/spec/scope.md:1246-1319 (5.4, `### 5.4` at :1237); their telescopes, as printed by the parser, match the pins name for name.

## Notes for the DRI

- The pin trusts `lean/statements.txt` to be fresh. A Lean edit without regeneration is caught by `tools/regen_generated.py --check` in the gate, `typed` reads it through `inventory_path` (StaleInventory on a changed module), and the test file's import (`tools/check_readings_defaults_statements.py`) refuses a stale inventory.
- Still not pinned: a premise's or the conclusion's type changed in both the spec and the Lean source with the binders kept. That is a spec change, reviewed as one; sc-2d's report now says so.
- docs/scope/sc-2d/DELTA.md row 1 says "a statement without `hw` or with another premise fails". That is true under the new pin, so the signed row is not edited.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. (no relayed answer touched).
2. Deliverables built, no rule broken: PASS (rows (1)-(4) above; no Python copy of a Lean decision; no report test added).
3. Tests can fail: PASS (M1-M3 and the two real plants, with failing test names above).
4. Python, Lean and Rust agree: N.A. (no product code).
5. R8 binding: N.A.
6. Gate evidence on final HEAD: N.A. here (fast lane: the chain runs the selected tests on the final HEAD).
7. No unsigned item: PASS (no DELTA row, trust +0).
8. User-visible changes in DELTA: N.A. (no output changes).
9. Test selection: PASS (`select_tests.py --paths lean/statements.txt` and the two sources select `tests/test_scope_5_4_statements.py`).
10. Lean statements say what is claimed: PASS (`test_an_effect_statement_takes_exactly_the_signed_premises` on the planted `{hx : True}` and `[inst : Inhabited Nat]`).
11. Budgets fail closed: N.A.
12. No CPU or memory regression: N.A. (one test file reading two text files, 43 tests in about 5 s).
13. Test-removed trailers: N.A. (no test removed or renamed; `binders` was a helper, not a test).
14. Both directions, cited evidence, spec re-read: PASS (accept: the five real statements pass; refuse: 25 plants, plus the two real ones; commands cited above).
15. No overclaim: PASS (the sc-2d and sc-2c corrections; this report's "not pinned" note). No silent cut: PASS (nothing cut). Every new check can fail: PASS (M1-M3). Limits charged: N.A.
