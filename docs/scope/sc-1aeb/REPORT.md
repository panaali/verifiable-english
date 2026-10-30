# sc-1aeb: `govern_provenance` under `JsonWF D.doc`

Status: built, ready for the gate. No DRI signature is reserved or needed.
`govern_provenance` (spec 5.1) is proved under `(hw : JsonWF D.doc)`, its only change from the spec's text
(`Theorems.lean:1413`). F1-g is now a `#guard` of the theorem's conclusion, tested on both sides (`Examples.lean:903-910`).
sc-1ae's review F5 is fixed; F4 was already fixed on main. SC-1a's five statements are now all proved.
Open: sc-1af (the parser condition; waits on the DRI). Trust +0. Selected tests: 80 units passed. Full gate: not run by me (the chain runs it).

Read first: the DRI decision `reviews/dri-decisions-20261027-featureplan-gates.md` item 2 (fix (a): five statements gain
`.WF`, and `govern_provenance` is one of them); `debates/plan-synthesis-2/edits-scope.md` (none of its seven edits nor
DEC 10/16 concerns `govern_provenance`, so this item implements none of them); sc-1ae's REPORT ("Size", "Next items")
and reviews `sc-1ae-review.final.md` and `sc-1ae-review-ov.final.md` (F4, F5).

## Plan rows

| Row (task) | Status | Where |
|---|---|---|
| (1) `govern_provenance` proved under `JsonWF D.doc`, on sc-1ae's lemmas | delivered | `lean/VE/Scope/Theorems.lean:1413`; it uses `govern_ok`, `comp_entry`, `unitsOf_patch`, `edgesFor_ok`, `governorsOf_iff`, `idOf_set`, `setObjVal_self`, `jsonWF_top`, `unitsOf_mem`, plus five new lemmas (below) |
| Statement gate: only `JsonWF D.doc` added, sc-1ae's `JsonWF`, spec text otherwise | delivered, exact | `docs/scope/sc-1aeb/statement-diff.txt` (lines 62-64, `DIFFERS theorem govern_provenance`). Its `built` line minus ` (hw : JsonWF D.doc)` equals its `spec` line (checked by a Python probe on the script's output: `True`) |
| (2) F-raw's `#guard`s unchanged | delivered | `git diff --numstat` on `Examples.lean`: 29 lines added, 0 removed; F-raw is still at `Examples.lean:738`, `:743`, `:748` |
| (2) F1-g as a `#guard` of the conclusion | delivered (it was not one before) | `Examples.lean:883-910`: `provenanceOf` computes the conclusion for one unit; one `example` applies the theorem to F1-g's document (`parts_wf`) |
| (3) seeded bugs: `JsonWF` dropped; governor order reversed (in `governorsOf` and in the fold); edges left out of `addOver` | delivered | "Seeded bugs" below; [mutants.json](mutants.json) |
| (3) one mutant per new trusted definition | N.A.: no new trusted definition | `trust_map.py --check`: "trusted +0" |
| (4) F4: `HasStr eq-le` INVALID; `BlockBound body-false`'s kill is `Examples.lean:764` | already closed on main, by sc-1ae fix1 (`30896a2c9`) | `docs/scope/sc-1ae/trust-mutants-allow.json`: eq-le reads "INVALID by hand (review F4)"; body-false names "Examples.lean:764". Since sc-3ab and sc-3ac merged, that fixture sits at `Examples.lean:817-821`; I did not edit the allow file |
| (4) F5: statement-diff header says sc-1ae | delivered | `docs/scope/sc-1ae/statement-diff.txt:1` now reads "sc-1ae statement diff …" |
| Its line in a statement diff | delivered | `docs/scope/sc-1aeb/statement-diff.txt` (output of `python3 docs/scope/sc-1ac/evidence/spec_diff.py`; first line names this item) |
| Not taken | sc-1af (as the task says) | |

## The proof

- **Which branch of `govern`.** `govern_ok` gives two cases. In the first, `D.governors = []` and `partUnits D = []`.
  Then `affected D` holds only part units, and there are none, so `hu` is impossible. In the second,
  `mapM_ok_of_mem` (new) finds `(u, o₁) ∈ comp` with `composed D u = .ok o₁`. Unfolding `composed` gives
  `o₀` and the fold. `edgesFor_ok` gives `es`, and `governorsOf_iff` gives the last conjunct.
- **What `patch` writes back.** Every entry of `comp` for `u` carries `o₁` (`comp_entry`: `composed` is a function),
  so `lookup_map_eq` (new) gives `addOver es o₁` at `u`. `unitsOf_patch` and `find_map_id` (new; a unit keeps its
  `id`, `idOf_set`) find the same unit in the answer. `normOf_newContent` (new) reads the rule back as `norm`.
  For a part, `Json.mkObj` gets distinct keys; for a norm, the content's own tree gets `setObjVal_self`.
- **Where the hypothesis is used.** The answer's `units` (`unitsOf_patch D hw`). The top level of each unit
  (`idOf_set`, `setObjVal_self`). The top level of the unit's content (`normOf_newContent`). F-raw shows the statement
  fails without it.

## Fixtures (`Examples.lean:883-910`): both sides of `provenanceOf`

- Accepts: F1-g (`[g1]`), where the seven items are exactly `affected D` and each holds. Also `[g1, gN, gP, gY]`: a
  unary narrowing on every item, and precedence edges into five of them. Every item holds.
- Refuses, at the boundary: the units just before and after the list (the lead-in `u0164.s02` and `u0166.s01`),
  which are not affected. Refuses on other answers: the ungoverned document; `[g1]`'s answer checked against
  `[g1, gP, gY]`, which fails exactly at the five units that have edges (`[false, true, false, false, false, false, true]`);
  `[g1]`'s answer checked against `[g1, gN]`, which fails at every item.
- The coverage conjunct cannot be refuted on any `D`: `governorsOf_iff` proves it. So no fixture refutes it.

## Seeded bugs (Lean; [mutants.json](mutants.json))

Lean is the only language whose product code changed. `tools/trust-classes.json` (two class-T names) and docs are
the rest. Each mutant was applied by `/tmp/sc1aeb/mut.py`, which ran `cd lean && lake build VE.Scope.Examples` and
then restored the source. The result is listed with each.

1. `JsonWF` dropped from `govern_provenance` (`Theorems.lean`). The build fails at `Theorems.lean:1436`, the units'
   top levels (`hu'`), and at `:1443`, `unitsOf_patch D hw`. It also leaves an unsolved goal at `:1419`.
2. A wrong conclusion, `some o₁` (no edges) (`Theorems.lean`). Fails at `:1455`.
3. The fold reversed in `composed` (`Govern.lean`). Fails at `Theorems.lean:1431` (the fold conjunct), at `:527` and
   `:531` (`governFast_eq`'s run path) and at `:1064`.
4. `governorsOf` reversed (`Govern.lean`). Fails at `Theorems.lean:525` (`governorsOfF_slow`: the run path's order
   must be `govern`'s), at `:527` and `:531`, and at `:1425`.
5. The edges left out of `addOver` in `govern` (`Govern.lean`). Fails at `Theorems.lean:531` and at `:1084`
   (`govern_ok`).
6. `provenanceOf` true where there is no base rule (`Examples.lean`). Fails at `#guard Examples.lean:903` (F1-g's
   boundary units).
7. `provenanceOf` without its comparison (`Examples.lean`). Fails at `:907`, `:908` and `:910` (the refusing side).

Mutants 3-5 break proofs before `Examples.lean` elaborates, so a second command showed that the `#guard`s catch
them too: `lake build VE.Scope.Govern && lake env lean VE/Scope/Examples.lean` (`/tmp/sc1aeb/guardmut.py`). This
builds only the mutated `Govern.olean`, under the unchanged `Theorems.olean`, then rebuilds after restoring. Results:
- Mutant 5 fails F1-g's guard `Examples.lean:905` and sc-1ad's `overOf` guards (`:594`, `:614`, `:621`, `:977`).
- Mutant 3 fails `:551`, `:578` and `:1052` (carve-outs append in governor order).
- Mutant 4 fails `:547`, `:551`, `:578` and `:1052`.

## Trust, DELTA, size

- `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0", PASS.
  So no R16 allowance and no FOLLOW-UPS row. The new lemmas are theorems. `provenanceOf` and `provAt` are fixtures,
  class T in `tools/trust-classes.json`.
- [DELTA.md](DELTA.md) has one row: the approved statement plus `hw`. It is SIGNED by the DRI on 2026-10-27, item 2,
  which names `govern_provenance`; its condition tests are F-raw's guards. No answer or refusal changes.
- Size, from `git diff --numstat $(git merge-base HEAD main)`. Hand-written lines:
  - `Theorems.lean` +107 (proof and five lemmas, against sc-1ae's estimate of about 80);
  - `Examples.lean` +29;
  - `lean/SCOPE.md` +3/−2; `tools/trust-classes.json` +2;
  - sc-1ae's header 1; DELTA 13; `mutants.json` 9;
  - this report.

  That is about 165 lines plus the report. Not counted: the statement diff (script output) and the generated
  `Audit.lean`, `axioms.txt`, `declarations.txt` and `statements.txt`.
- Pilot bytes (estimate): 0. This is a proof only.

## Overlap check

Hand-written files: `lean/VE/Scope/{Theorems,Examples}.lean`, `lean/SCOPE.md`, `tools/trust-classes.json` and
`docs/scope/sc-1ae{,b}/*`. I ran `git diff --name-only main...<b>` over every `lean-first/*`, `feature/*`, `infra/*`
and `foundation/*` branch:
- `feature/sc-1af` edits `lean/VE/Scope/Examples.lean`, in hunks at lines 748 and 1009; my block is at 883. It also
  edits `Govern.lean`, `Wire.lean` and `WireExamples.lean`, which I do not touch.
- Five branches add names to `tools/trust-classes.json`.
- No branch edits `Theorems.lean` or `lean/SCOPE.md`.

## Commands run

- `lake build VE.Scope.Theorems` and `lake build VE.Scope.Examples` while iterating.
- `uv run python tools/regen_generated.py --write`, once: "wrote 33 entries". It first needed the Rust release
  binary, so I ran `python3 tools/rust_build.py`, which reported it "pinned in lean/checkers.lock", unchanged.
- `cd lean && lake build`: "Build completed successfully (1161 jobs)".
- `python3 lean/audit.py`: "PASS: 670 source files; 7482 named theorem declarations audited".
- `uv run python tools/gate_collection.py --check --prebuilt`: "0 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed".
- `uv run python tools/regen_generated.py --check`: "checked 33 entries".
- `zsh …/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: 80 units in 4 shards (18, 20, 22 and
  20), all passed, exit 0 (GitHub Actions run `sc-1aeb-3c56ac09-t326315`). The selection includes
  `tests/test_scope_lean.py`.
- Not run: the full gate (the chain runs it) and `trust_mutants` (trust is +0, and no new trusted definition).

## Next items

- **sc-1af**: the parser condition (`feature/sc-1af` exists; it waits on the DRI's amendment).
- **sc-3ac** (`title_identity`, rank 88), on the same files.

## Spec re-read

- `govern_provenance` against `docs/spec/scope.md:1073-1080`: names, binder order, the five conjuncts and their order
  are the same.
- F1-g against `docs/spec/scope.md:1664`: the seven part units under `g1`, with `u0164.s02` not composed. The guard at
  `:903` refuses the conclusion there.
- The DELTA row against the DRI decision item 2: `govern_provenance` is one of the five statements it lists.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., because no route, response or relay changes.
2. Deliverables built, no rule broken: PASS. Every task row is in "Plan rows". There is no Python copy, no report
   test and no overlap on a hunk ("Overlap check").
3. Tests can fail: PASS. Seven mutants, each failing a named proof or `#guard` ([mutants.json](mutants.json)). No
   trusted growth, so no `trust_mutants` run.
4. Python, Lean and Rust agree: N.A., because no runtime definition changed (`trust_map.py --check`: +0).
5. R8 binding: N.A., because no relayed field.
6. Gate evidence on the final HEAD: PASS by process. The full gate is run by the chain on the committed HEAD. The
   branch's base is main's tip `81b837121`.
7. Nothing unsigned: PASS. The one DELTA row cites the DRI's 2026-10-27 decision item 2, and trust is +0.
8. Every user-visible change in DELTA: PASS. The statement is the only change; no answer changes (DELTA.md).
9. Test selection: PASS. `tools/select_tests.py --base …` selects `tests/test_scope_lean.py` and the Lean build steps,
   and it did not select every unit.
10. Statements say what is claimed: PASS. The wrong-conclusion mutant 2 breaks the build (`Theorems.lean:1455`). The
    added hypothesis has the DRI ruling and the mechanised counterexample, F-raw (`Examples.lean:738-748`). The
    statement diff (`spec_diff.py`) shows `hw` is the only difference.
11. Budgets and limits: N.A., because there is no budget or limit code.
12. CPU and memory: N.A. The new `#guard`s run `govern` four times on the hard-constraint layout; no runtime
    code changed.
13. Removed tests: PASS. `gate_collection.py --check --prebuilt` reports 0 removed and 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. "Fixtures" covers the accepting and refusing sides and the
    boundary units, "Commands run" gives the evidence, and "Spec re-read" is above.
