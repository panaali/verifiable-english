Status: PASS on local checks; the chain runs the final release gate.
HEAD: `38571b519` for the tested implementation; this report is a later commit.
AGENTS.md: 8,082 -> 5,913 bytes; Generated files section: 700 bytes.
Moved: the seven-step `discourse` recipe to `docs/ROUTE-RECIPE.md`, verbatim apart from its title level.
Open items: none; no DELTA, DRI signature, or trust change.

# eff-readdiet build report

## Delivered and checked

| Acceptance item | Owner | Evidence |
| --- | --- | --- |
| Keep the route-recipe heading and link; move steps 1–7 verbatim | AGENT | `AGENTS.md:51`, `docs/ROUTE-RECIPE.md:1`; byte comparison against `git show d9cff5345:AGENTS.md` passed |
| Condense Generated files without dropping its rules or commands; leave other AGENTS sections unchanged | AGENT | Section 700 bytes; script compared all other sections byte for byte with base; `test_repo_map.py` passed |
| Apply existing path, Lean-name and command checks to both entry docs; guard link and 6,000-byte limit | AGENT | `tests/test_repo_map.py`: 33 passed; three seeded bugs below failed their named tests |
| Add recipe beside AGENTS.md in docs index | AGENT | `docs/README.md:15` |
| Run selected tests on the finished code | AGENT | Mac runner snapshot of implementation: 474/474 fallback units, zero failed/error IDs, exit 0; post-commit selection probe: 21/474 units, including `tests/test_repo_map.py` |
| Final-HEAD release gate | EXTERNAL, chain | Deferred to the chain as instructed; `tools/gate.py` was not run here |

The selected runner used its full fallback because the implementation was still an uncommitted snapshot at invocation. After commit, `uv run python tools/select_tests.py --base $(git merge-base HEAD main)` selected 21 units. The fallback covered those units, and `tests/test_repo_map.py` passed in both its direct run and the fallback. No generated-file input, Lean, Rust, or product Python file changed; regeneration, Lean build/audit, and trust_mutants do not apply. No user-visible VE output or trust change exists, so there are no DELTA rows.

## Seeded bugs

Each mutant was temporary, its named pytest test failed, and the file was restored before the passing run.

| Mutant | Changed file | Failing test |
| --- | --- | --- |
| Replace `lean/VE/Discourse/Run.lean` with a nonexistent path | `docs/ROUTE-RECIPE.md` | `test_every_path_named_in_agents_md_exists[ROUTE-RECIPE.md]` |
| Pad AGENTS.md to 6,013 bytes | `AGENTS.md` | `test_agents_md_is_short_and_claude_md_is_its_symlink` |
| Remove the backticked recipe link | `AGENTS.md` | `test_agents_md_links_route_recipe` |

## Build checklist applicability

Items 1–12, 15, and 17–19 concern product parsers, wire answers, verdicts, Lean proofs, or use cases; none changed. Item 13 is covered by the three failures above. Item 14: the modified tests retain the `tmp_path` cache fixture, and the added checks only read repository files. Item 16: both entry docs are checked by the same parametrized checks. Item 20: this report gives status, evidence and unrun checks. Item 21: all acceptance items above carry AGENT or EXTERNAL owners. Item 22: direct `test_repo_map.py` passed (33 tests); the selected runner passed (474 units); the chain owns the final gate under this task's override. Item 23: no user-visible delta or signature applies. No tests were removed or renamed. Free disk at handoff: 178 GB.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean answer or decoder changed.
2. PASS — acceptance table above; byte comparison probe and `test_repo_map.py` cover all required files.
3. PASS — three seeded failures in the Seeded bugs table.
4. N.A. — no Python, Lean or Rust product behavior changed.
5. N.A. — no relay or binding changed.
6. N.A. — final gate is run by the chain on the committed HEAD; this batch has no gate evidence.
7. PASS — `git diff main...38571b519 --name-only` contains documentation and one test file only; no DELTA or trust growth.
8. PASS — the same diff shows no VE output path changed; DELTA is empty.
9. PASS — `tools/select_tests.py --base $(git merge-base HEAD main)` selects 21/474 units, including `tests/test_repo_map.py`; the three seeded failures show the selected test can fail.
10. N.A. — no Lean statement or proof changed.
11. N.A. — no budget or deadline changed.
12. N.A. — no runtime path changed.
13. PASS — `git diff main...38571b519 -- tests/test_repo_map.py` keeps every old test name; no Test-removed trailer needed.

## FIXMAP

- `AGENTS.md`: short always-loaded instructions; route pointer at line 51; generated-file rules at line 55.
- `docs/ROUTE-RECIPE.md`: seven-step worked `discourse` recipe; runner step at line 5, relay step at line 18, fuzz step at line 23.
- `docs/README.md`: documentation index; route recipe row at line 15.
- `tests/test_repo_map.py`: entry-doc path, Lean-name, command, size, link and symlink guards.
- `docs/infra/eff-readdiet/REPORT.md`: this build evidence and handoff.
- `spans` -> `tests/test_repo_map.py:96`; `commands` -> `tests/test_repo_map.py:105`; `script_of` -> `tests/test_repo_map.py:121`.
- `test_agents_md_is_short_and_claude_md_is_its_symlink` -> `tests/test_repo_map.py:132`; `test_agents_md_links_route_recipe` -> `tests/test_repo_map.py:139`.
- `test_every_path_named_in_agents_md_exists` -> `tests/test_repo_map.py:144`; `test_every_lean_name_in_agents_md_is_declared` -> `tests/test_repo_map.py:152`; `test_every_command_named_in_agents_md_exists_and_the_fast_ones_answer_help` -> `tests/test_repo_map.py:163`.
- Regression: `UV_CACHE_DIR=/tmp/ve-eff-readdiet-uv uv run pytest -q tests/test_repo_map.py`.
- Selection: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.
- Generated files needing regen: none; if an input later changes, use `uv run python tools/regen_generated.py --write`.
- trust_mutants: not used; no command or JSON path applies.

## END FIXMAP
