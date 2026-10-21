# sc-3ab: `govern`'s heading and label reaches and the block's anchor checks (scope@0, SC-3a's govern half). Build report

**Stopped at the statement gate for one theorem; DRI decision needed (no DELTA signature reserved):** spec 5.5's
`title_identity` is false as stated, on JSON objects no parser builds (F-raw-title, mechanised). It is the class of
sc-1ad's five stopped theorems and is settled by the same DRI decision (fix (a) or (b) in sc-1ad's REPORT).
`title_identity` is **sc-3ac**, after that decision. Everything else is delivered: the anchor and label reaches,
`admitBlock` step 7 and step 8's unit check, `anchor_reach_iff`, `label_reach_iff`, and the fixtures' `govern`
halves.

- Branch `feature/sc-3ab`, worktree `/home/seyran/code/ve-sc-3ab`, merge base `68f18dcdc` (main, after sc-1ad).
- Plan and spec on main, identical to `c5197da78` (`git diff c5197da78 HEAD -- docs/spec/scope*.md` is empty). Plan
  section "SC-3a"; spec 4.2, 5.5, 6.2 and 7.5. SYNTHESIS 4.1: SC-3a is a phase-4 Lean core. SYNTHESIS 4.2: no
  shared-file queue names `lean/VE/Scope/`. DRI-DECISIONS-PHASE2 "Scope": SC1 (AP-3 → SC-4) is the reason for this
  item; SC2 (pilot prompts) does not touch it; SC3 (layer `research`) does not apply, because `VE.Scope.*` is layer 2.
- Read first: sc-3a's, sc-1ac's and sc-1ad's REPORTs. The anchor checks have one owner, `lean/VE/Layout/Anchors.lean`
  (sc-3a). `admitBlock` calls `VE.Layout.anchorsOk`, `VE.Layout.anchorReach`, `VE.Layout.headingOf` and
  `VE.Layout.itemRun`, and copies none of them.

## Statement gate

[statement-diff.txt](statement-diff.txt), from [evidence/spec_diff.py](evidence/spec_diff.py) (whitespace and comments
ignored, theorems up to `:=`):
- `anchor_reach_iff` and `label_reach_iff`: **exact**. Both are proved from sc-3a's layout theorems, unchanged.
- `coveredLayout`, `kindOf` and `defSpans`: exact. `admitBlock` differs only in sc-1ac's recorded deviation 2:
  `c.isNull`, not `c == .null`.
- sc-3a's statements are unchanged in the compiled `lean/statements.txt`: `acc_no_heuristic`, `name_scope`,
  `innermost_within`, `discourse_anchorsOk_unchanged`, `discourse_within_unchanged`,
  `discourse_innermost_unchanged`, `anchorReach_iff` and `itemRun_iff`. Of all 6,403 statements at `68f18dcdc`,
  0 changed and 0 were removed. This item touches no file of sc-3a.
- **`title_identity`: false as stated, so not built.**

**Why `title_identity` fails.** Take `D` whose only governor is one title `g`:
- `govern D` takes the governor branch and returns `patch D []`. That is
  `D.doc.setObjVal! "units" (.arr xs)` with the units unchanged.
- `govern D'`, where `D'` has `g` removed, has no governor and returns `D.doc` itself.
- `Json.obj` holds any `Std.TreeMap.Raw`. On an unbalanced tree, `setObjVal!` (`insert!`) rotates and drops members,
  as sc-1ad found.

F-raw-title (`lean/VE/Scope/Examples.lean`, a `#guard`) is the UDHR document of F8 with the top level
`x(units(·, w(·, wa)))`. With `g8` the answer has no `wa`; without it the answer has `"WA"`. Both calls succeed, so
`govern D' = .ok out` fails for the `out` of `govern D`.

Every object a JSON parser builds is balanced. On such a document the two answers agree: F8 and F9′ compare them as
values. Making the theorem provable needs either an added hypothesis (fix (a)) or a changed `patch` (fix (b)). Both
change approved text, which needs the DRI (BUILDER-CHECKLIST 10), so this item builds neither.

The case of two or more governors needs neither fix. The title is not a frame, not unary and not graph, so removing
it changes no step. With distinct ids (step 3), `ordered` filtered by id is `ordered` of the filtered list, because
mergeSort is stable (`List.mergeSort_cons`). I argue this here and have not proved it; sc-3ac proves it.

FOLLOW-UPS.md, "## sc-3ab (2026-10-21)", records the decision request.

## Plan rows

| Row (task) | Status | Where |
|---|---|---|
| (1) The anchor and label reaches in `coveredLayout` | delivered, spec 4.2's text | `Govern.lean`: `VE.Layout.anchorReach`, `VE.Layout.itemRun`; sc-1ac's two refusals deleted. `governFast` reads them through `coveredLayout` (`governFast_eq` unchanged) |
| (2) `admitBlock` step 7, replacing the anchors refusal | delivered, spec text | `VE.Layout.anchorsOk D.anchors (defSpans D) (unaryPred …)`, with spec 4.2's `kindOf` and `defSpans`; the refusal deleted |
| (2) Step 8's anchor and label unit check | delivered, spec text | a non-graph governor of an anchor reach sits on the heading, of a label reach on the item |
| (3) `anchor_reach_iff`, `label_reach_iff` | delivered, exact | `Theorems.lean` |
| (3) `title_identity` | **sc-3ac** (statement gate) | F-raw-title above |
| (4) F8: `govern` returns the document unchanged | delivered | `#guard`s, by `govern` and by `governFast`, with Article 29's three paragraphs as norms; the reach through `covered` |
| (4) F8-tree from `admitBlock` step 7 | delivered | `InvalidInput: anchors must form one tree`, also before a governor's own step-8 fault (fault order 6.2) |
| (4) F9′ as a title | delivered | the pinned run's units: heading marker `u0151.heading` |
| (4) F-meta's two-root case | delivered | discourse's text, where sc-1ac refused with `UnsupportedProfile` |
| Each fixture with a seeded bug | delivered | Seeded bugs |
| Name what does not fit as sc-3ac | done | Next items |

Fixtures beyond the four, each added so that a seeded bug fails a named check:
- F10's `govern` half (a label as a title: the document unchanged, by both paths; the reach through `covered`);
- step 8's checks (a unit off the heading or the item, recorded units, an unknown anchor, `NotALabel` through
  `govern`, an anchor reach in a block without anchors);
- a `precedes` governor off the heading (graph governors are exempt);
- a narrowing over an anchor, which composes Article 29's rules and leaves u114;
- step 7's export check, which reads the definition units by kind and the unary test.

`admit_governor` (sc-1ad) keeps its statement. Its proof's side goal now splits the new step-8 match too, so it runs
under `set_option maxHeartbeats 400000` (the default is 200,000). `VE.Scope.Theorems` builds in about 30 s instead
of 19 s.

## Seeded bugs (Lean; [mutants.json](mutants.json))

There are 11 mutants, all in Lean, the only language whose product code changed. They were applied to the final code
by a runner outside the repository: build `VE.Scope.Examples`, record the failing declarations, restore. **All 11
fail a named check.** The three caught first by a proof were run again with those two proofs replaced by `sorry`.
That control build passes, and each of the three then fails fixtures too.

| Mutant | Definition | Behaviour | Fails |
|---|---|---|---|
| anchor reach empty | `coveredLayout` | (1) | `anchor_reach_iff`; without proofs F8 reach, F8, graph-on-anchor, narrowing, F9′ |
| anchor reach keeps the heading | `coveredLayout` | (1) | `anchor_reach_iff`; without proofs F8 reach, F8, step 8, graph-on-anchor, narrowing, F9′ |
| label reach is the item only | `coveredLayout` | (1) | `label_reach_iff`; without proofs step 8, F10 reach, F10 |
| step 7 dropped | `admitBlock` | (2) | F-meta two-root, F8-tree, exports |
| step 7 without the unary test | `admitBlock` | (2) | exports |
| step 7 after step 8 | `admitBlock` | (2), fault order | F8-tree |
| `kindOf` reads `id` | `kindOf` | (2) | exports |
| `defSpans` takes every unit | `defSpans` | (2) | exports |
| heading check dropped | `admitBlock` | (2) | step 8 |
| graph governors checked too | `admitBlock` | (2) | graph-on-anchor |
| item check dropped | `admitBlock` | (2) | step 8 |

`tools/trust_mutants.py` (checklist 13a, through `mac-pytest.sh --trustmut`, which fell back to the VM because
ve-mac-1 was unreachable) selects **0 definitions**: the item adds no trusted line. Its output is
[trust-mutants.json](trust-mutants.json) (exit 0). The hand mutants above cover `coveredLayout`'s changed lines.

## Trust

`uv run python tools/trust_map.py --check` against `68f18dcdc`: **PASS**, K +0, S +0, untied V +0, trusted **+0**.
- G +11 are reject-only (G[R]): `kindOf` and `defSpans`, which only feed step 7's refusal, and `admitBlock`'s lines.
- The new fixtures are T. `tools/trust-classes.json` lists them.
- No allowance is recorded and no R16 row is needed (DELTA.md).

## Size

Measured with `git diff --numstat 68f18dcdc`, generated files excluded.
- **Code, fixtures and side table: 135 lines added.** `Examples.lean` 83, `Govern.lean` 21 (9 deleted),
  `Theorems.lean` 16, `trust-classes.json` 15.
- Docs and evidence: `lean/SCOPE.md` +18, DELTA 16, `spec_diff.py` 60, the saved outputs 25, `mutants.json` 13, and
  this report.

The total is under 600.

## Tests

- **Lean.** `lake build` of the scope modules has no error. Every `#guard` holds, including the new ones.
- **Generated files.** `tools/regen_generated.py --write`, then `--check`: 33 entries, all current.
  - `lean/VE/Audit.lean`, `axioms.txt`, `declarations.txt` and `statements.txt` were regenerated.
  - The Rust release binary was built with `tools/rust_build.py` and is pinned (Rust unchanged).
- **Other checks.**
  - `tests/test_scope_lean.py` and `tests/test_trust_budget.py`: 19 passed.
  - `tools/repo_map.py --check`: PASS (37 modes).
  - `tools/check_lean_imports.py`: layer graph kept. `Govern.lean` now imports `VE.Discourse.Access` for
    `unaryPred`. That module was already a dependency through `VE.English.Parse`.
- **Selected tests.** `zsh mac-pytest.sh --select -- --base 68f18dcdc --run` ran on the VM, because ve-mac-1 was
  unreachable. It ran on `8dfd93148`, the final code (only DELTA.md and this report follow it): 80 of 460 units,
  0 failed, exit 0, in 5,913 s. No test from `main-known-red.txt` failed.
- **Full gate.** Not run by me, as the task says. The chain runs it on the final HEAD.

## Pilot bytes (estimate)

0 B in both pilots, as the plan says. The constitution's 39 headings and the UDHR's 32 are titles, already LABELLED.
The bold labels are blocked by their own content (graded force). No route calls `govern` yet. Nothing is claimed
before a pilot audit.

## Next items

- **sc-3ac** (after the DRI's decision on sc-1ad's fix (a) or (b)): spec 5.5's `title_identity`.
  - With two or more governors, the proof needs no fix: `ordered` commutes with the filter (from
    `List.mergeSort_cons`), the admission is monotone, and `frameOn`, `covered` and `governorsOf` do not change.
  - With the title alone, it needs the fix: `patch D [] = D.doc` on a well-formed document.
- **sc-3b** (after its approved addendum and SC-2): condition headings and assertion targets. A narrowing over an
  anchor already composes the reached norms (fixture above); sc-3a's finding 1 (a heading is two units in the pinned
  run) is still an input to its addendum.
- **SC-4** after AP-3.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no relayed Lean answer, route, mode or schema is added.
2. **Every required deliverable built.** PASS: every task row is in Plan rows. The stopped theorem is behind the
   statement gate (a mechanised counterexample), and sc-3ac is named. There is no Python copy of a Lean decision and
   no report test. Probe: `git diff --name-only main...HEAD`. The hand-written overlaps with in-flight branches are
   only the JSON ledger `tools/trust-classes.json` (ap-1b, ap-1d, jt-2, me-2, me-9b, me-1), merged by its driver.
3. **Tests and gates can fail.** PASS: 11 seeded Lean mutants, each failing a named `#guard` or theorem
   ([mutants.json](mutants.json)), with a proofs-bypassed control. `tools/trust_mutants.py` exits 0 with nothing to
   mutate.
4. **Python, Lean and Rust agree; valid inputs still pass.** N.A. for agreement: only Lean implements scope. Valid
   inputs pass: F8, F9′ and F10 return the document unchanged, by `govern` and `governFast` (`#guard`s).
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I can take it. The tree is committed and clean. The
   evidence commit list is below. The chain runs the full gate on the final HEAD.
7. **No unsigned item.** PASS: DELTA has no row (trust +0, no caller, no statement changed). No DELTA cell reserves
   a signature. The stop for the DRI is the first line of this report.
8. **Every user-visible change in DELTA.** PASS: DELTA.md explains why nothing is user-visible. The texts sc-1ac's
   refusals wrote appear in no answer.
9. **Test selection finds the tests.** PASS: `select_tests` picks 80 of 460 units, including `lake build`, the audit,
   `tests/test_scope_lean.py` and `tests/test_trust_budget.py`. The Lean build runs every mutant's failing check.
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` shows both theorems exact and 0 of 6,403
    statements changed. The anchor and label mutants break `anchor_reach_iff` and `label_reach_iff`. The false
    statement is not weakened; it is stopped with F-raw-title.
11. **Budgets fail closed.** N.A.: no limit is added. Step 7's 1,024-anchor limit is sc-3a's, with its boundary
    fixtures.
12. **No CPU or memory regression.** N.A. for the pilots: no route calls `govern`. Build cost: `VE.Scope.Theorems`
    about 30 s (was 19 s), because of `admit_governor`.
13. **Test-removed trailers.** PASS: no test was removed or renamed; `tools/gate_collection.py --check --prebuilt`: 19,101 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
0843839b7 sc-3ab: DELTA (no user-visible delta; trust +0)
8dfd93148 sc-3ab: statement-gate evidence, seeded Lean mutants (11, all failing a named check), trust-mutants run; lean/SCOPE.md
8f102e68d sc-3ab: regenerate declarations
56e6c2e92 sc-3ab: admit_governor at 400k heartbeats (step 8's reach match doubles the side goal's cases)
985053346 sc-3ab: trust classes (kindOf, defSpans G[R]; fixtures T); regenerate
9b8e20b1d sc-3ab: anchor and label reaches in coveredLayout, admitBlock step 7 and step 8's unit check (spec 4.2's text); anchor_reach_iff, label_reach_iff; govern fixtures F8, F8-tree, F9′, F10, F-meta's two-root case; F-raw-title
```
