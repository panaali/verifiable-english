# sc-2: named lists and later qualifications — build report

Status: **partial, size cut**; no DRI signature reserved. Source HEAD `3ae897200` (the two SC-2 source commits); this report and evidence follow it.
Changed: proved the exact `listName_run` statement and added F3/F4/F6 fixtures without attitude nodes; all selected tests passed.
Open: seven other spec 5.4 proofs and their proof fixtures are **sc-2c**; AT-3a's attitude decoder and its F3/F4 reading are **sc-2b**.
Pilot: no translation edit, byte claim, or coverage audit in this item.

## Baseline and statement gate

On main `8868ce212`, `Effects.lean` already defines all six `Effect` constructors, `hasOwn`, `ownSafe`, `substOwn`, `Commutes`, and `mergeParts`. `Govern.lean` already defines `applyEffect` (reguard replaces the guard with `substOwn` of the original JSON; carve-out appends one substituted condition), `coveredLayout` for a discourse `ContentName`, the registering list's exact-run check in `admitBlock`, `orderCheck`, and `govern`. These came from SC-1a/SC-1b; sc-5rb already uses the two effects per choice. The check uses discourse's decoder, not a second scope name table. sc-1ae supplies `JsonWF`; this cut adds no hypothesis to a 5.4 statement.

The statement review closed **PASS** (`scope-p3ver2.final.md:1`, after `scope-p3ver1.final.md`). A whitespace-normalising comparison of `listName_run` in `docs/spec/scope.md:1306` and `lean/VE/Scope/Theorems.lean` printed `statement match: True` ([evidence/checks.txt](evidence/checks.txt)). No other 5.4 theorem is claimed proved here. The round-2 synthesis's `substOwn` through AT-3a decoder lemma (edit 1) belongs to sc-2b and is **not** implemented here; its `ContentName` re-pointing (edit 4) was on main before this cut.

## Plan rows and fixtures

| Plan row | Result and evidence |
|---|---|
| List name registers exactly its lead-in run | `listName_run`, plus `admitted_list_names_nodup` and `nodup_map_unique`, source commit `f96ffcb71`; `lake build VE.Scope.Theorems` passed. Existing accepting and refusing list-name guards in `Examples.lean` cover exact units, wrong units, wrong lead, wrong scope, unknown name, and 256/257 boundary. |
| `reguard_applies`, `restrict_applies`, `carveOut_applies`, `applyEffect_typed`, `own_congr`, `commute_applies`, `order_refused` | **sc-2c**: no proof or changed statement is claimed. These traverse both the norms and soft-norms decoder and the nested governor loops. Carry the exact 5.4 statements forward. |
| F3 without attitude words | `Examples.lean` F3 guard checks all seven substituted guard JSON values, using each rule's own guard, and checks decoding of the first and last rule. `lake build VE.Scope.Examples` passed after source commit `3ae897200`. The original attitude-word F3 is sc-2b. |
| F4, F4-r3, F4-c | The two-element model has `likely_guard` true and the original guard false: replacement applies, narrowing does not. F4-c tests the retained carve-out with `tested_by_anthropic` false and true. `lake build VE.Scope.Examples` passed. Attitude semantics in the original F4 are sc-2b. |
| F6 and F6′ | The carve-out reaches all seven named rules; the no-carve-out side remains empty. The soft decoder admits eight carve-outs and refuses the ninth with its own diagnostic. `lake build VE.Scope.Examples` passed. |
| F7 and F7′ | Already on main in `Examples.lean`: two own-mentioning reguards refuse with `ScopeOrder`; narrowing plus own-free carve-out is accepted in either order. No duplicate fixture added. |
| Pilot | No edit. The plan's `u0164.s01` +68 B LABELLED is an estimate; `u0173.s01` +263 B requires AT-3a and is not claimed. |

The size measurement before the second half (`git diff --numstat $(git merge-base HEAD main)`) was 57 handwritten proof lines. The final SC-2 source adds 57 proof lines and changes 55 fixture lines. The remaining seven exact statements need decoder and order lemmas; **their size is an estimate**, informed by sc-1ae's report of about 600 proof lines for its decoder/string proofs (`docs/scope/sc-1ae/REPORT.md`, “Size”). I cut them to sc-2c under the feed's ~600-line rule rather than claim the batch finished. The actual line count for sc-2c is unverified.

After sc-2b and sc-2c, the dependent feature item is sc-3b (headings and labels, the constitution's second queue).

## Validation and risk

- `UV_CACHE_DIR=/tmp/sc2-uv-cache uv run python tools/regen_generated.py --write`: PASS, 33 entries ([evidence/checks.txt](evidence/checks.txt)); the first run lacked a Rust executable, then `python3 tools/rust_build.py` built and pinned it. No Rust product source changed.
- `PATH=~/.elan/bin:$PATH lake build`: PASS, 1159 jobs. `python3 lean/audit.py`: PASS, 668 files and 7476 declarations, standard axiom allowlist only ([evidence/checks.txt](evidence/checks.txt)).
- `UV_CACHE_DIR=/tmp/sc2-uv-cache uv run python tools/trust_map.py --check`: PASS, K +0, S +0, trusted +0 against main ([evidence/checks.txt](evidence/checks.txt)). There is no new trusted definition or R16 allowance, so the R16 trust-mutant run and ties-pass follow-up do not apply.
- `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: PASS, 3 shards, 24 + 28 + 25 = 77 units and 0 failures ([evidence/checks.txt](evidence/checks.txt)). The full release gate was **not run** here; the chain runs it on final committed HEAD as instructed.
- Three seeded Lean bugs in changed fixture code were planted independently, failed the named `#guard` with `lake build VE.Scope.Examples` exit 1, and were removed: [mutants.json](mutants.json). No Python or Rust product code changed.
- Hand-written overlap check across in-flight `lean-first/*`, `feature/*`, `infra/*`, and `foundation/*` branches printed no overlap for `Theorems.lean` or `Examples.lean`. `df -h .` reported 145 G available. No test was removed or renamed.

## Spec re-read and self-review against BUILDER-CHECKLIST

Spec re-read: `listName_run` against `docs/spec/scope.md:1306`; named reach and exact manifest against `:153-166`; `own` substitution against `:182-204`; effect order against `:205-245`; the no-attitude limit against `:1237-1242`. The copied plan's SC-2 row is `docs/spec/scope-PLAN.md:754-848` at `72a241fba`.

1. N.A. — no relayed answer or request decoder changed.
2. PASS — plan-row table above and `git diff --stat main...HEAD`; partial size cut is explicit.
3. PASS — `mutants.json`, each named `#guard` failed.
4. N.A. — no production route or decoder changed.
5. N.A. — no new relayed field or binding changed.
6. N.A. — chain-owned final-HEAD gate pending; selected run passed ([evidence/checks.txt](evidence/checks.txt)).
7. PASS — `DELTA.md` has no behavior row; `trust_map.py --check` reports +0.
8. PASS — `git diff main...HEAD -- lean/VE/Scope` shows proofs and guards only.
9. PASS — selected-test command passed 77 units ([evidence/checks.txt](evidence/checks.txt)).
10. PASS — whitespace comparison printed `statement match: True`; replacing `n.units = us` by `n.units = []` made `lake build VE.Scope.Theorems` fail ([evidence/checks.txt](evidence/checks.txt)).
11. PASS — F6′ `#guard` checks eight accepted and nine refused in `lake build VE.Scope.Examples`.
12. N.A. — no production computation changed.
13. N.A. — no test removed or renamed.
14. PASS — F3/F4/F6 guards exercise both directions; spec re-read listed above and test commands cited per claim.
