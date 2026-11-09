# pe-1b REPORT: PE-R11 and PE-R8 in `VE.Purposes` (honest version, L1 only)

Status: delivered in full. No signature is reserved and no part moved to pe-1c. HEAD: the last commit of
`feature/pe-1b`. The four † theorems are proved, `check` has step 6a, `check_ok_iff` is re-proved with the new
conjunct, and every listed fixture is a `#guard`. Trust: S +12, K +0 (R16). No user-visible delta.
SELECTED: SEE-TESTS. Next item: pe-2.

Plan and spec: `docs/spec/purpose-explanation-PLAN.md` "PE-1" (lines 1009-1045: F2c-F2e, F9, F9a, F10 and the
seeded bugs) and section 10.3 (PE-R8 and PE-R11 as applied). `docs/spec/purpose-explanation.md` 4.1-4.4, and its
7.2 row 6a. Both are pe-1's verbatim copies on main. This branch does not edit them.

## Delivered

| Task deliverable | Where | Evidence |
|---|---|---|
| (1) `Part.readings` and `Units.packSources` (defaulted fields, spec 4.1) | `WellFormed.lean` (where `Part` is; `Decl.lean` is not edited) | every existing #guard still passes: `lake build VE.Purposes.Examples` gives 0 errors |
| (1) `packsInert`, `check` step 6a, the `WellFormed` conjunct, and `check_ok_iff` re-proved | `WellFormed.lean` | `check_ok_iff`'s proof is unchanged and closes; `lake build` gives "Build completed successfully (1319 jobs)" |
| (1) `packsInert_iff`, `packsInert_nil` | `WellFormed.lean` | proved, no `sorry`; `python3 lean/audit.py` passes |
| (1) F2c, F2d, F2e | `Examples.lean`, section "F2c, F2d, F2e" | F2c and F2d give the 6a text; F2e gives `.ok ()` |
| (2) `targetKind`, `holdsTarget`, `shownUnder`, `unlinkedActive`, `shownUnder_iff`, `unlinkedActive_iff` | `WellFormed.lean` | proved; audit passes |
| (2) F9, F9a, F10, F3's `unlinkedActive = []`, and F1, F2 and F8's `shownUnder = []` | `Examples.lean`, sections F3, F9 and F10 | the values pe-1's `#eval` computed, below |
| The plan's four seeded bugs, plus one mutant per new definition | `mutants.json` | 13 mutants, each killed (below) |
| Trust-mutant sweep on the final Lean | `trust-mutants.json`, `trust-mutants-allow.json` | exits 0 |
| Generated files | regen commit | `uv run python tools/regen_generated.py --write --skip route-cases` ("wrote 36 entries") |

`route-cases` is skipped as R12 and pe-1 allow: its writer needs the Rust release binary, which this worktree has
not built. The full run stopped with "CheckerUnavailable: missing Rust executable …/rust/target/release/ve
… regen_generated: failed: route-cases". This item changes none of its inputs.

The fixture values all equal pe-1's `#eval`s (its REPORT, "The stub elaboration for pe-1b is done"):
- F2c (`packSources = ["u0019.s01.p3"]`) and F2d (`["u0019.s01"]`) give
  "InvalidPurposes: link l1 has a side the text does not state, and a pack takes a premise from it".
- F2e (`["u0019.s01.p1"]`) gives `.ok ()`.
- F9 (61 B) gives `.ok ()`, `shownUnder = [("f.p3", ["rationale", "limiting"])]` and `unlinkedActive = []`.
- F9a gives `.ok ()` and `shownUnder = [("f.p3", [])]`.
- F10 (68 B) gives `.ok ()`, `shownUnder = []` and `unlinkedActive = ["g.p1"]`.
- F3 gives `unlinkedActive = []` for both links.
- F1, F2 and F8 give `shownUnder = []`.

So the statement gate needed no DRI question.

The self-review added more fixtures, each needed to kill a mutant or to test the opposite direction:
- Fault order: 6 before 6a, and 6a before 7.
- 6a on a purpose side (F1's `u0146.s01.p3`). F1 with only its target and marker sourced gives `.ok ()`.
- A `because` link whose slots differ: `targetKind F2 f2l = some .norm`, and `shownUnder` on F2 with a set on
  its target.
- Reading names on a part with no set: nothing is shown.
- `unlinkedActive` leaves out an inert unlinked part, a part of another unit, and every part when the marker has
  no unit.
- `wf` holds on F2e, F9 and F10, and fails on F2d.

### Statements against the spec

I compared each spec text with its Lean text mechanically, after normalising whitespace. The script extracts each
`def`/`theorem` block from `docs/spec/purpose-explanation.md` and from `WellFormed.lean`, up to `:= by`. All 11 are
SAME:
- `packsInert_iff`, `packsInert_nil`, `shownUnder_iff`, `unlinkedActive_iff` and `check_ok_iff`;
- `packsInert`, `targetKind`, `holdsTarget`, `shownUnder`, `unlinkedActive` and `WellFormed`.

Step 6a's text is checked by the F2c #guard (`packText`), and equals spec 7.2's row 6a (line 1476). The only
differences from the spec are the `†` draft markers, which are dropped from the doc comments.

Spec re-read:
- `Part.readings` and `Units.packSources` against spec lines 527 and 533.
- `packsInert`, `targetKind`, `holdsTarget`, `shownUnder` and `unlinkedActive` against lines 621-650.
- Step 6a against lines 674-675 and 1476.
- `WellFormed` against lines 688-693.
- The four † theorems against lines 695-714.
- The fixtures against plan lines 1009-1024.

### What this item does not claim

- `shownUnder_iff`'s doc comment comes from the spec: "the view gives one name per kind
  (`checkDocSetsView_readings`, 5.1), so no candidate is cut by the zip". That theorem is PE-2's (the checked-view
  refactor). This item proves nothing about the view. Until PE-2, `readings` and `candidates` are just the
  fields a caller passes.
- `packsInert_iff` covers packs only given the obligation `packSources_complete` (spec 5.1), which is PE-2's.
- Content: structure is checked, and what the linked parts say stays a named open residual (DRI sprint decision
  item 2). Nothing here counts as semantic coverage.

## Size

Measured with `git diff --numstat $(git merge-base HEAD main)`. (1) and (2) were written and committed together
(547ed0685), so there is no separate measurement after (1). At that commit the count was 175 lines:
Examples.lean +63/-5, WellFormed.lean +105/-2.

Final hand-written lines:
- Lean: WellFormed.lean +105/-2, Examples.lean +81/-5.
- Side table: tools/trust-classes.json +29/-1.
- Evidence: mutants.json +226, trust-mutants-allow.json +34.
- Docs: this report and DELTA.md.

The total stays under the ~600-line line. Generated and verbatim files are excluded: inventories, `Audit.lean`,
the codemap, `trust-baseline.json` and `trust-mutants.json`.

`lean/VE/Route/Inert.lean`, `Admission.lean`, `lean/VE/Service/` and every Python and Rust file are unchanged
(`git diff --stat $(git merge-base HEAD main) -- lean/VE/Route/ lean/VE/Service/ ve/ rust/` is empty). This item
needed nothing more in Inert.lean.

In-flight overlap: `git diff --name-only main...<branch>` for every `feature/*`, `lean-first/*`, `infra/*` and
`foundation/*` branch touches nothing under `lean/VE/Purposes/` or `docs/purpose-explanation/`. Eleven branches
also edit `tools/trust-classes.json`: ap-4, ci-2b, ci-3a, ci-5, pk-1-conditions-b, ps-2aa, qt-a4b, sc-10b,
sc-7, sn-b6-f8-trust and me-1. This item's entries sit only inside the existing `VE/Purposes/*` keys, so a merge
touches other lines.

## Seeded bugs (Lean, the only language changed)

The method is in `mutants.json`'s `command`:
- Each bug is planted alone, in memory, in `lean/VE/Purposes/WellFormed.lean`.
- The mutated module and `Examples.lean` are elaborated as one file with `lake env lean`, so a broken proof does
  not hide the #guards after it.
- A control run with no mutation gives 0 errors.
- The checkout is never written.

| # | Plan bug / definition | Mutation | Fails (first named #guard; all in `fails_at`) |
|---|---|---|---|
| P1 | plan: `packsInert` reading only the parts, not their unit | drop `!(p.parent.any U.packSources.contains)` | F2d, `Examples.lean:105`; `packsInert_iff` |
| P2 | plan: `packsInert` always true | `true \|\| …` | F2c, `Examples.lean:104`; `packsInert_iff` |
| P3 | plan: `holdsTarget` reading the reason's slot | `targetKind` arms swapped | F9's `shownUnder`, `Examples.lean:236` (and :116, :117) |
| P4 | plan: `unlinkedActive` keeping parts another link names | drop the `B.links.any` filter | F10's value, `Examples.lean:255`; F3's `[]`, :136; `unlinkedActive_iff` |
| H1 | `unlinkedActive` keeping inert parts (the plan row's other half) | drop `!p.kind.inert` | `Examples.lean:266` (synthetic: in F10 and F3 every inert part is linked, so their values cannot tell); `unlinkedActive_iff` |
| H2 | `unlinkedActive` without the unit filter | drop `p.parent == some u` | `Examples.lean:266`; `unlinkedActive_iff` |
| H3 | `shownUnder` keeping a part with no set | `if false then none` | F10's `shownUnder = []`, :254; F1/F2/F8, :257; `shownUnder_iff` |
| H4 | `holdsTarget` negated | `!=` | F2 `because` set, :117; F9, :236; `shownUnder_iff` |
| H5 | `targetKind` giving a non-causal marker a kind | `\| _ => some .norm` | :259 |
| H8 | `targetKind`'s `because` arm reading the reason's slot | `then c else c` | :116, :117 (found by the self-review: no `because` fixture had distinct slots) |
| H6 | `check` without step 6a | the `require` removed | F2c, F2d; `check_ok_iff` |
| H9 | `check` running 6a after step 7 | the two steps swapped | F2 sole + pack, :110; `check_ok_iff` |
| H7 | `WellFormed` without the `packsInert` conjunct | the conjunct dropped | `wf` F2d, :278; `check_ok_iff` |

## Trust (R16)

- `uv run python tools/trust_map.py --check` on the final Lean prints "against 0f9fc890970e: K +0, S +12, D +0,
  G +21, tied +23, unclassified +0, trusted +12" and "PASS: K, S and untied [V] within 0f9fc890970e and the
  allowances introduced since" (exit 0).
- The allowance was recorded with `trust_map.py --allow`. It is signed `SIGNED by standing ruling R16
  (DRI-RULINGS.md), pe-1b, 2026-11-09`, and the per-file counts are in DELTA.md row 1.
- Classes, in `tools/trust-classes.json`:
  - S: `targetKind` and `holdsTarget`.
  - G[V]: `packsInert` (tied by `packsInert_iff` and `packsInert_nil`), `shownUnder` (`shownUnder_iff`) and
    `unlinkedActive` (`unlinkedActive_iff`).
  - T: the new fixtures (`packText`, `f9u`, `F9`, `f9l`, `f10u`, `F10`, `f10l`).
- The trust-mutant sweep: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --test
  lean/VE/Purposes/Examples.lean --json docs/purpose-explanation/pe-1b/trust-mutants.json`. It planned 22 mutants
  on 3 definitions (`targetKind`, `holdsTarget`, `WellFormed`).
  - The first run exited 1: 4 KILLED, 18 UNKNOWN. Every UNKNOWN is on the Prop `WellFormed`: "wfDecidable, which it
    reads, is not what it is without the mutant".
  - I planted each of the 18 in memory with the method above. Every one breaks `check_ok_iff`
    (`WellFormed.lean:187`, "unsolved goals"), and each also fails a `wf` #guard (:275 or :278).
  - The allow file gives that reason for each operator: `body-true`, `body-false`, `and-or`, `eq-le`, `eq-ne`
    and `bool-flip`. This is pe-1's precedent for the same Prop.
  - The `--rescore` run with `--allow` exited 0: **KILLED 4, ALLOWED 18, SURVIVOR 0, UNKNOWN 0, INVALID 0, NOT
    RUN 0.** The raw verdicts were 18 UNKNOWN and no SURVIVOR.
- The sweep does not mutate the tied G[V] definitions or `check`. Mutants P1-P4, H1-H3, H6 and H9 cover them.
- FOLLOW-UPS.md has the ties-pass row under "## pe-1b".

## Tests

- Lean: `cd lean && lake build` prints "Build completed successfully (1319 jobs)". `python3 lean/audit.py` prints
  "PASS: 789 source files; 8712 named theorem declarations audited … only the declared standard axiom allowlist".
- `uv run python tools/lean_statements.py` prints "removed: 0, changed: 0" (additions only).
- Selected tests: SEE-TESTS.
- No Python or Rust file changed, so there is no relay, schema or R8 binding to fuzz.

## Pilot bytes

Estimate: 0 (the structure row). Nothing calls the code. Nothing is claimed before a pilot audit.

## Next item

pe-2: the `purposes` block in the document mode, relayed and shown. Its `eligible` uses Decl's `NotChecked`
(row pe-2-eligible), and it shows `shownUnder` and `unlinkedActive`. PE-E1 sits beside it. This item cuts nothing,
so there is no pe-1c.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 0 A, 3 B, 8 C; fixed 10. Fixed: all three B and seven C (the `because` fixture with distinct
slots, F9a's check, the FOLLOW-UPS row, F10 as the spec gives it, the 6a fault-order and purpose-side fixtures, the
`fails_at` line mapping, line wrapping and the report notes). The eighth C, a size measurement taken after (1)
alone, cannot be redone from history, so the Size section says so.

1. N.A.: no Lean answer reaches a relay; no route, mode or schema is added (DELTA.md's grep).
2. PASS: the Delivered table covers every task deliverable, and nothing is cut. No Python copy of a Lean decision,
   and no report test. The overlap check is in Size.
3. PASS: 13 seeded bugs, each failing a named #guard (`mutants.json`), and `trust-mutants.json` exits 0. The allow
   file names exact definitions and operators.
4. N.A.: no Python or Rust path computes these checks; Lean is the one owner.
5. N.A.: no field is relayed to Python.
6. PASS: the branch starts at main's merge base 0f9fc8909, and all evidence names its commits. The gate runs on
   the committed final HEAD (the chain's step).
7. PASS: DELTA.md row 1 cites R16, with the trust-mutant and seeded-bug evidence R16 asks for.
8. PASS: DELTA.md says no user-visible delta, and its grep and `git diff --stat` show it.
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 467 of 556 units, including
   `test_trust_budget.py`, `test_trust_mutants.py`, `test_lean_default_build.py` and `test_assurance_manifest.py`.
10. PASS: each seeded bug breaks the proof it should (`packsInert_iff`, `shownUnder_iff`, `unlinkedActive_iff`,
    `check_ok_iff`). The statements are the spec's (the mechanical comparison above). No `tools/check_*_statements.py`
    covers purposes.
11. PASS: no evaluator or clock is added. `check` still counts the links against `maxLinks` first (the 257-link
    #guard). The new definitions walk lists already in the view, once each.
12. N.A.: no route calls the code, so no pilot time changes.
13. PASS: no test removed. Only #guards were added to `Examples.lean`, and nothing was renamed.
14. PASS: both directions for each new check:
    - 6a refuses F2c, F2d and F1's purpose, and passes F2e and the sourced target and marker.
    - `shownUnder`: a set on the target versus none.
    - `unlinkedActive`: `["g.p1"]` versus `[]`.
    Every claim here cites its command, and the spec re-read is above.
15. PASS:
    - Overclaim: `checkDocSetsView_readings` and `packSources_complete` are written as PE-2's.
    - No cut.
    - Every new check can fail: the 13 seeded bugs.
    - Limits before work: item 11.
