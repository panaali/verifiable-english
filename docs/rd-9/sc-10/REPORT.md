# sc-10 report: SC-10's `fillPremisesSD_pull` and `supX_pull`; the three superposition theorems move to sc-10b

**Status:** built, cut under the size rule. Branch `feature/sc-10`. The code is final at the commit that adds this report.
**Changed:** `lean/VE/Readings/SoftSup.lean` proves `fillPremisesSD_pull` and `supX_pull`, word for word as 13.3 states them. sc-10a's REPORT moved both here. `SoftSupExamples.lean` gains one `#guard`.
**Open:** `sd_superpose_conflict_free`, `sd_superpose_all` and `sd_superpose_countermodel` and their 13.5 fixtures are not built. They move to **sc-10b** (see Cut).
**Signatures:** none needed. Trusted +0 (`tools/trust_map.py --check`), no DELTA row, no R16 allowance.

## Plan and task rows

| Row (task text) | Delivered | Evidence |
| --- | --- | --- |
| (1) the four sc-10a moved here: `fillPremisesSD_pull`, `supX_pull` | yes: `26a84e162` (`fillPremisesSD_pull`), `593da14c3` + `c939628ad` (`supX_pull`). No `sorry`, no new axiom | `SoftSup.lean:642`, `:1018`; statement compare (below) |
| (1) `sd_superpose_conflict_free`, `sd_superpose_all`, `sd_superpose_countermodel` | **no**: moved to sc-10b (the size rule's cut clause) | FOLLOW-UP line in the final reply |
| (1) reuse `fill_sim`, `fill_sim_author`, `fillPremisesSD_pull`, `supX_pull`, no second copy | yes: `fillPremisesSD_pull` reads `fill_sim` and `fill_sim_author`. `supX_pull`'s coherence half reads sc-10a's `pullF_canon`, `encodes_canon_fill` and `fillLite_choiceSD` | `SoftSup.lean:642-700`, `:896-1013` |
| (2) 13.5 iff fixtures of the three theorems | **no**: they belong with sc-10b's theorems. sc-10a's fixtures for both directions of `supX_pull` and `fillPremisesSD_pull` stand, plus one new guard | `SoftSupExamples.lean:143-166` |
| (3) seeded bug `supCertificateCheckSD` ignoring `A` | yes, M2: fails a fixture of sc-10a's | `mutants.json` M2 |
| (3) seeded bug: the countermodel's bits name the other choice | **no**: it needs `sd_superpose_countermodel`'s fixture (sc-10b) | `mutants.json` `not_run` |
| (3) seeded bug `supX` returning `[]` | yes, M1: `supX_pull` and the S-4/S-4′ and `supX_pull` fixtures fail. The NSD4a CONFLICT fixture is sc-10b's | `mutants.json` M1 |
| (4) `statements.txt` gains the theorems; `axioms.txt` within `propext`, `Classical.choice`, `Quot.sound` | yes, for the two built theorems and their lemmas, via `regen_generated.py --write` | `lean/statements.txt`, `lean/axioms.txt` (`2102a83b7` and the report commit) |
| Section 13 registered in `check_rd9_sc1_statements.py` | **no**: sc-10a left it for when every 13.3 statement exists, which is after sc-10b | — |

Synthesis round 2: this item implements none of the edits. Edit 5 ("until SC-10/11 land, a soft-chain document's readings route enumerates") still holds, since no route reads these theorems.

## Cut (size rule) and the next item

Before the second half, `git diff --numstat $(git merge-base HEAD main)` gave `SoftSup.lean` +394. Each of the three superposition theorems needs both directions over the filled base vocabulary:
- *Down:* `pullF` of an admissible superposed base is admissible for the choice's filled document, including the `unsaid__` declarations. Then the conflict iff at an encoded base, through `fill_sim`.
- *Up:* S2a's `upB` must be admissible for `fill (supU N)`'s base vocabulary. `pullF (upB B₀)` must read every formula over the filled choice vocabulary as `B₀` does (a `pullF` form of `pull_up` and `canon_pull_up`). Then `upB` gives `Fill_T` and `supX` through `fillPremisesSD_pull` and `supX_pull`.

Doing that, plus the certificate and countermodel steps and their fixtures, would add well over the ~200 lines left under the ~600 rule. So this item stops at the coherent first part: the two transfer theorems, which all three need, with their fixtures and seeded bugs.

**sc-10b:** `sd_superpose_conflict_free`, `sd_superpose_all`, `sd_superpose_countermodel` (13.3, word for word), their 13.5 iff fixtures (NSD4a/NSD4c, NSD1 under `[(rs1,0)]` and `[]`, the without-`hl` case on NSD4), the three seeded bugs of this task's (3), and section 13 in the statement checker. Then sc-11.

## How the proofs go

- **`fillPremisesSD_pull`** is RD-6b's `fillPremises_pull` with `pullF` for `pull`. The outcome and gap formulas are read on each side's canonical interpretation (`outcomeBase_fill`/`gapF_fill` on the superposed side, `outcomeBase_fill_v`/`gapF_fill_v` with `Valid (fill (choiceU N c))` on the choice's). They are then equated by `fill_sim` (filled trees) and `fill_sim_author` (author rules).
- **`supX_pull`** splits `supX` and `choiceX` into `Exc_T` and `Coh_T` on the filled tree (`VE.Defaults.softX_eq`):
  - `exc_pullF`: an image's premises transfer through `pullF` (`fmap_exception_eq`, `exceptedF_pullF`, `pullF_denote_frame`). For an unchosen candidate's rule, a sufficient condition holds because its gate is false (`pattern_off`). A necessary condition holds because the slot's quiet premise empties its `excepted` table (`quiet_holds` on the rule's `excepted` key, whose one owner is the candidate).
  - `coh_pullF`: `selU_canon` reads a rule's selection on the filled tree as its soft selection at `canon (fill U) B`. An image pair transfers by S2a's `sim_selects_fuel` and sc-10a's `pullF_canon` (as `coh_down` on the unfilled trees). A pair with an unchosen member never selects both (`dead_extra`).

New imports: `VE.Readings.BarQuiet` (`quiet_holds`) and `VE.Defaults.Meaning` (`softX_eq`, `selU`). No read-only file was edited.

## Seeded bugs (Lean, the only language changed)

Each bug was planted alone in the final `SoftSup.lean`. `lake build VE.Readings.SoftSupExamples` was run, then the file was restored. The script is in the build log, not committed. For M1 and M5 the run was repeated with `supX_pull`'s proof stubbed for that run only, so the examples file could elaborate and list the guards each breaks.

| Bug | Change | Caught by |
| --- | --- | --- |
| M1 | `supX N := []` (task bug 3) | `supX_pull`'s proof; with it stubbed, the guards at `SoftSupExamples.lean:39`, `:43`, `:44`, `:145`, `:146`, `:154` |
| M2 | `supCertificateCheckSD` with `slotUnder N.D []` (task bug 1) | the guard at `SoftSupExamples.lean:80` |
| M3 | `pull` for `pullF` in `fillPremisesSD_pull`'s statement | its proof (`SoftSup.lean:690`). The statement is false: `:166` (NSDq at `base1 [(a,u)]`, superposed `Fill_T` true at `:163`, pulled with `pull` false). `lake env lean` probe printed `(true, true, false)` |
| M4 | `exc_pullF`'s slot hypothesis weakened to `atoms N.D c` (no quiet premise) | its proof, at the quiet premise (`SoftSup.lean:796`). The statement without the slot is false at `:154` |
| M5 | `supX` with S2a's unfilled `Coh_T` (`softPremises`, D3) | `supX_pull`'s proof; with it stubbed, the S-4 guard at `:39` |

All five were KILLED (`mutants.json`). Task bug 2 (the countermodel's bits) moves to sc-10b with its fixture. No trust mutants were run: there is no trusted growth (13a applies only under R16).

## Trust, size, bytes

- Trust: `uv run python tools/trust_map.py --check` reports "against 9635574ebf2b: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 … PASS". Every new declaration is a theorem.
- Size: by `git diff --numstat $(git merge-base HEAD main)`, outside generated files, `SoftSup.lean` +396 −1, `SoftSupExamples.lean` +2, `mutants.json` 26, and this report.
- Pilot bytes expected: 0. These are proofs only; SC-11 moves bytes.
- Overlaps with in-flight branches: only the generated `lean/statements.txt` and `lean/axioms.txt`, which the merge driver regenerates. `SoftSup*.lean` is touched by no other branch (`git diff --name-only main...<b>` over `feature/*`, `infra/*`, `foundation/*`, `lean-first/*`).

## Statements and spec re-read

- `fillPremisesSD_pull` and `supX_pull` against `docs/spec/rd-9-soft-chain.md:1801-1814`: a whitespace-normalising compare of the spec block with the Lean text up to `:= by` printed `fillPremisesSD_pull MATCH`, `supX_pull MATCH`.
- 13.2's readings (`:1735-1738`), 13.4 item 4 (supX_pull is an iff because an unchosen premise holds by its bit, S-4, or the quiet premise, S-4′), and 13.5's rows for both theorems (`:1915-1917`, `:1904-1906`). These are what `exc_pullF`'s two unchosen cases and the fixtures at `SoftSupExamples.lean:143-166` follow.

## Tests run

- `cd lean && lake build`: "Build completed successfully (1213 jobs)". `python3 lean/audit.py`: "PASS: 709 source files; 7924 named theorem declarations audited".
- `uv run python tools/regen_generated.py --write --skip route-cases`, then `--write --only lean-statements --only lean-audit-manifests` after the last Lean edit, then `--check` of the same two: "checked 2 entries". `route-cases` needs a Rust release binary that this worktree does not have; none of its inputs changed. The codemap's branch staleness is advisory and regenerated on merge, so the codemap files it rewrote, which come from other merges, were not committed.
- `uv run python tools/gate_collection.py --check --prebuilt`: "0 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers".
- Selected tests: see the addendum below.
- Not run: the full gate (the chain runs it on the final HEAD).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed answer, route or schema changes.
2. Deliverables: PASS with the cut recorded (Plan and task rows; FOLLOW-UP sc-10b). No Python copy, no report test, no authority switch; overlaps listed above.
3. Tests can fail: PASS, `mutants.json` M1-M5 all KILLED, each by a proof or `#guard` (M1, M5 also by named guards).
4. Py/Lean/Rust agree: N.A., no Python or Rust change and no answer changes (bytes 0).
5. R8 binding: N.A., no relayed field.
6. Gate evidence: PASS for what this item runs (selected tests on the final code, addendum); the full gate is the chain's.
7. Unsigned items: PASS, none. Trusted +0 (`trust_map.py --check`), no DELTA row.
8. User-visible changes: PASS, none. No route reads these theorems, so there is no DELTA.md.
9. Selection: PASS, `tools/select_tests.py --base $(git merge-base HEAD main)` selects `lake build` and `python3 lean/audit.py`, which fail on every seeded bug above.
10. Statements: PASS. 13.3 text matches word for word (compare above). M3 and M4 show each statement's key part is needed.
11. Budgets and deadlines: N.A., no evaluator, runner or mode is added.
12. CPU/memory: N.A., no runtime path changes.
13. Removed tests: N.A., `gate_collection.py --check --prebuilt` gives 0 removed, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Each theorem has a true/true and a false/false fixture (`SoftSupExamples.lean:146-151`, `:161-164`). `hsl`'s need is at `:154`, `pullF`'s at `:166`. The spec re-read list is above.
