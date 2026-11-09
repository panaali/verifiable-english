# pk-1-conditions-b-cfr-1: the readers of `Pack.conditions` (REPORT)

Summary: READY FOR REVIEW. The `Pack.conditions` docstring names its readers `packConditions` and `providerConditions`;
tests/test_pack_conditions_doc.py holds it (fails on the base). Comment and test only; trust +0; pilot bytes 0.
Seeded bugs S1-S7 each fail a named test. No DELTA row, no DRI signature reserved. Next item: none.
Selected tests: see "Test runs" (final run on committed code).

Source: DRI 2026-11-09, reviews/dri-decisions-20261109-l1-c-regrade-norm-defaults.md item 1 (regrade #10; finding
pkcb-F3). The plan is the code on main; base 9f5dd46ab (`git merge-base HEAD main`). No plan section or statement gate.

## Deliverables (all AGENT)

| # | Row (task) | Delivered by |
|---|---|---|
| 1 | Docstring states its readers, keeping the profile-composition 1.9 reference | lean/VE/NormDefaults/Packs.lean:40 (field docstring, one line, so trust +0) names both; the module docstring (Packs.lean:14-16, class `o`) gives their roles: `packConditions` looks the conditions up by decision key for the uniform decision premises (`dfltUniform`); with `providerConditions` the defaults route refuses a document any of whose packs states a condition until EXP-D3 settles (`defaultsRows`, Route.lean:24) |
| 2 | `test_pack_conditions_reader_documentation`: fails while the docstring says "no reader"; passes only when it names both readers and each is a `def` in Uniform.lean | tests/test_pack_conditions_doc.py, with the opposite direction in `test_pack_conditions_reader_documentation_refuses` (the old docstring and a renamed `def` are refused) |
| 3 | Grep lean/ for other "no reader" / "not read yet" comments on a pack field | None (below) |

**Fails on the base.** With `git show 9f5dd46ab:lean/VE/NormDefaults/Packs.lean` in place (seeded bug S1):
`uv run pytest -q --noconftest tests/test_pack_conditions_doc.py` gave
`E AssertionError: assert ['the docstri...reader yet).'] == []` and `2 failed` (the first is
`test_pack_conditions_reader_documentation`; the message is "the docstring says it has no reader: Each stated
sufficient condition and its decision (profile-composition 1.9; no reader yet)."). On HEAD: `2 passed`.
`--noconftest` skips conftest (its backend build among it); the test reads two source files and needs no backend. It
also runs under the normal conftest in the selected run.

**Other comments.** `grep -rniE "no reader|not (yet )?read|nothing reads|read by no|no consumer|unused yet" lean
--include=*.lean --exclude-dir=.lake`: on the base the only pack-field match is Packs.lean's `conditions` docstring;
on HEAD the matches mentioning "pack" number 0. The other matches concern decoders, front matter and limits. None
changed.

**Stays selected.** `uv run python tools/select_tests.py --paths lean/VE/Defaults/Uniform.lean
lean/VE/NormDefaults/Packs.lean --static --explain --no-record` lists `tests/test_pack_conditions_doc.py: names
lean/VE/Defaults/Uniform.lean (static); names lean/VE/NormDefaults/Packs.lean (static)`.

## Seeded bugs

Each was planted, run with `uv run pytest -q --noconftest tests/test_pack_conditions_doc.py`, seen to fail, and
restored (`2 passed` afterwards). "main" = `test_pack_conditions_reader_documentation`, "refuses" =
`test_pack_conditions_reader_documentation_refuses`.

| # | Lang | File | Bug | Fails |
|---|---|---|---|---|
| S1 | Lean | lean/VE/NormDefaults/Packs.lean | the base docstring restored | main: `assert ['the docstri...reader yet).'] == []` |
| S2 | Python | tests/test_pack_conditions_doc.py | `providerConditions` in `READERS` renamed `providerConditionsX` | main: `assert ['the docstri...Uniform.lean'] == []` |
| S3 | Lean | lean/VE/NormDefaults/Packs.lean | "(profile-composition 1.9)" dropped | main: `assert ['the docstri...Conditions`.'] == []` |
| S4 | Lean | lean/VE/NormDefaults/Packs.lean | `` `providerConditions` `` replaced by "the provider guard" | main: `assert ['the docstri...vider guard.'] == []` |
| S5 | Lean | lean/VE/Defaults/Uniform.lean (planted only) | `def providerConditions` renamed `providerConditionsOld` | main: `assert ['providerCon...Uniform.lean'] == []` |
| S6 | Python | tests/test_pack_conditions_doc.py | the "no reader" check replaced by `if False:` | refuses: `assert [] == ['the docstri...Conditions`.']` |
| S7 | Python | tests/test_pack_conditions_doc.py | the `def` check replaced by `if False:` | refuses: `assert [] == ['providerCon...Uniform.lean']` |

S1 and S2 are the two the task names. The only product code changed is a Lean docstring; no Python or Rust product
code changed.

## Trust and mutants

`uv run python tools/trust_map.py --check` after the regen commit: `against 9f5dd46ab4ed: K +0, S +0, D +0, G +0, tied
+0, unclassified +0, trusted +0` and `PASS`. `uv run python tools/trust_mutants.py --plan`: `"definitions": 0,
"mutants": 0` (light-lane prints NOT only because Packs.lean is a trusted-core file), so no sweep was run.

## Builds and generated files

`lake build`: `Build completed successfully (1327 jobs)`. `python3 lean/audit.py`: `PASS: 795 source files`.
`uv run python tools/lean_statements.py` then `uv run python tools/regen_generated.py --write` (`wrote 37 entries`):
lean/declarations.txt and docs/codemap/*.md change; no generated file was edited by hand.

## Scope and size

Hand-written: Packs.lean +6/-2, tests/test_pack_conditions_doc.py, DELTA.md and this REPORT. The loop
`git diff --name-only main...<b>` over all 424 `lean-first/* feature/* infra/* foundation/*` branches finds the two
files only on this branch. The other C findings of the regrade are out of scope.

## Test runs

Final selected run, on committed HEAD d8d75905f (clean tree): `MAC_PYTEST_NO_DEFER=1 zsh
/home/seyran/code/manage-agents/mac-pytest.sh --select -- --base 9f5dd46ab --run` (through `wait-bg.sh --start`)
ended `summary: ran on ve-cloud-3, select_tests, exit=0, 9353s`, `recorded 528 units ...; 0 failed`;
`tests/test_pack_conditions_doc.py: exit 0 in 1.3 s` (under the normal conftest). An earlier copy of the same run was
stopped at the 50-minute background limit before it finished (no failure in its partial log); the run above replaced
it. Only this REPORT changed after the run.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer changed).
2. Deliverables built, no rule broken: PASS (table above; no Python copy of a Lean decision; no report test).
3. Tests can fail: PASS (S1-S7).
4. Py/Lean/Rust agree: N.A. (no behaviour changed).
5. R8 binding: N.A. (no relay).
6. Gate evidence matches final HEAD: PASS (final selected run on committed HEAD; the chain gates it).
7. No unsigned item: PASS (DELTA has no row; no signature reserved).
8. Every user-visible change in DELTA: PASS (none: comment and test only).
9. Selection finds the tests: PASS (`select_tests.py --paths ... --static --explain` above).
10. Lean statements say what is claimed: PASS (no statement changed; audit PASS).
11. Budgets fail closed: N.A. (no limit or deadline).
12. No CPU or memory regression: N.A. (a comment).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS (`..._refuses`; each claim cites its command; re-read
    Uniform.lean:29 `packConditions`, :223 `providerConditions`, Route.lean:24, profile-composition 1.9 named).
15. Overclaim / silent cut / checks can fail / limits: PASS (the docstrings claim only what Uniform.lean and Route.lean
    do; no deliverable cut; S6, S7 for the new checks; limits N.A.).

Build checklist: 13, 13a (no trusted growth; plan 0 mutants), 14, 20, 21, 22, 23 done; 1-12 and 15-19 N.A. (no
contract, relay, schema, English, state or spec-stage change).
