# sc-3a: layout anchors, heading and label reaches (layout half). Build report

No DRI signature is reserved in this item. The one DELTA row (trust budget, net +11 lines, K +0) is signed by
standing ruling R16.

This item builds the layout half of the plan's SC-3a:
- `lean/VE/Layout/Anchors.lean`: discourse's anchor containment and anchor checks, moved, so one body serves
  discourse and scope; the anchor reach and the heading;
- the label reach (`itemRun`) in `lean/VE/Layout/List.lean`;
- the spec's layout theorems and fixtures.

The scope half is **not built**: `anchor_reach_iff`, `label_reach_iff` and `title_identity` are stated over `SDoc`,
`covered` and `govern`, and those do not exist on main. The task said SC-1a had merged `Effect`, `Governor` and
`Reach`, but SC-1a was cut (docs/scope/sc-1a/REPORT.md): main has only `lean/VE/Layout/List.lean`. `Effect` is on
local branch `wip/sc-1ab-own` (sc-1ab), and `Reach`, `Governor`, `SDoc` and `govern` are sc-1ac, which has not
started. Building them here would duplicate sc-1ab and sc-1ac, so the scope half is the next item, **sc-3ab** (Next
items).

- Branch `feature/sc-3a`, worktree `/home/seyran/code/ve-sc-3a`, merge base `702ff7429` (main).
- Plan: [scope-PLAN.md](../../spec/scope-PLAN.md), section "SC-3a. Layout anchors, heading and label reaches,
  titles". Spec: [scope.md](../../spec/scope.md) 1.2, 1.3, 4.1, 5.5 and 7.5. Both are already on main.
- SYNTHESIS 4.1: SC-3a is a phase-4 Lean core, built in parallel with the other cores. SYNTHESIS 4.2: no shared-file
  queue names `Access.lean` or `WellFormed.lean`. DRI-DECISIONS-PHASE2 "Scope": SC1 (AP-3 → SC-4) and SC2 (pilot
  prompts) do not touch SC-3a. SC3 (layer `research`) does not apply, because `VE.Layout.*` is already layer 2
  (profiles).
- Plain words: [lean/SCOPE.md](../../../lean/SCOPE.md).

## Statement gate

**PASS.** I checked this before building:
- The spec's statement review returned FIX. The confirmation rounds closed it:
  `manage-agents/scope-p3ver1.final.md` found one fix, and `scope-p3ver2.final.md` returned PASS. The plan says that
  PASS opens SC-1a and SC-3a. sc-1a's [STATEMENT-GATE.md](../sc-1a/STATEMENT-GATE.md) records that later drafts
  change no Lean block.
- **Access.lean's statements are unchanged.** `acc_no_heuristic`, `name_scope`, `innermost_within` and
  `narrower_mem` keep their statements and are re-proved by unfolding. Every one of the 5,978 theorem statements at
  `702ff7429` is identical at HEAD, and none is removed. See [statements-unchanged.txt](statements-unchanged.txt),
  produced by `evidence/statements_unchanged.py`, which compares `lean/statements.txt` and ignores only the `-- uses`
  and `-- expr` metadata lines.
- **`discourse_anchorsOk_unchanged` holds.** It is proved by `rfl`, and so is `discourse_innermost_unchanged`.
  `discourse_within_unchanged` is proved by `List.map_map` (see Cost).
- **Built text against the approved text:** 17 of 17 exact ([statement-diff.txt](statement-diff.txt), from
  `evidence/spec_diff.py`). These are spec 4.1's `itemFrom`, `itemRun`, `ItemUnit`, `spansOf`, `within`,
  `narrower`, `innermostAnchor`, `anchorUnits`, `headingOf`, `anchorReach`, `reachesRoot`, `anchorsOk`, and spec
  5.5's `itemRun_iff`, `anchorReach_iff` and the three `discourse_*_unchanged` theorems. The comparison ignores
  whitespace and comments, and compares theorems up to `:=`.
- No statement had to change, so the item did not stop.

**In-flight check.** No branch touches `Access.lean` or `WellFormed.lean` (`git diff --name-only main...<b>` for
every `lean-first/*`, `feature/*`, `infra/*`, `foundation/*` and `wip/*` branch, 2026-10-19):
- `lean-first/b18` touches `Discourse/Loader.lean`, `Discourse/Wire.lean` and `tests/test_discourse.py`, as the
  task said.
- `tools/trust-classes.json` is also edited by `feature/et-7b`, `foundation/me-1` and `lean-first/b18`. It is a
  JSON ledger merged by the `ve-generated` driver.
- `lean/VE/Route/frozen-sources.sha256` appears on `foundation/me-1` and `infra/arch-AR-1`. It is generated (R12),
  and this item does not change it (plan rows).

## Plan rows

| Plan SC-3a row | Status | Where |
|---|---|---|
| New `lean/VE/Layout/Anchors.lean`: the bodies of discourse's `within`, `narrower`, `innermostAnchor`, over (unit spans, anchors) | delivered | `8a52b80a8`; the spec's text, exact |
| Discourse's three definitions become one-line calls | delivered | `Access.lean`. `within` and `innermostAnchor` pass `D.base.units.map (id, start, stop)`, one map, not `unitKeys` mapped again (`8b91d9974`, Cost) |
| `anchorsOk` and its helpers (`req`, `runAll`, `allOk`, `dupOf`, `spanIn`, `spansDisjoint`) move, over (anchors, definition spans, unary test); discourse opens them from there | delivered | The helpers keep their `VE.Discourse` names, so no caller changes: they are defined in `Anchors.lean`, below `Access.lean`. `reachesRoot`, `definitionIn` and `unitSpan` go too (only the moved bodies used them) |
| `lean/VE/Discourse/Access.lean`: statements and theorems unchanged; `acc_no_heuristic`, `name_scope`, `innermost_within` re-proved by unfolding | delivered | Statement gate. `narrower_mem` and `innermost_within` are now one-line proofs from `VE.Layout.narrower_mem` and `VE.Layout.innermost_within` |
| `lean/VE/Discourse/WellFormed.lean`: `anchorsOk` a call (`discourse_anchorsOk_unchanged`); discourse's anchor fixtures pass unchanged | delivered | `tests/test_discourse_lean.py` (κ anchor tables, ι exports) and the other discourse tests pass: 468 on `8b91d997` |
| `lean/VE/Route/frozen-sources.sha256`, regenerated by its own tool | regenerated, **no change** | Since AR-1's narrow freeze (D2) the file hashes only K-holding modules and the `ve.core@0.1` decoders. Neither discourse file is listed. `frozen.py --write` (through `regen_generated.py --write`) leaves it unchanged, and `frozen.py` passes |
| `tools/trust-classes.json`: the entries of `Access.lean` and `WellFormed.lean`, and the class of the new file | delivered | Trust |
| Theorems `anchor_reach_iff`, `title_identity` (plan 5.5, over `SDoc`) | **sc-3ab** | need `SDoc`, `covered`, `govern` (sc-1ac) |
| Theorems `discourse_within_unchanged`, `discourse_anchorsOk_unchanged` | delivered | `lean/VE/Layout/Discourse.lean`, with `discourse_innermost_unchanged` (spec 5.5) |
| Fixtures F8, F8-tree, F9′, F10 | delivered for the layout half; the `govern` halves in **sc-3ab** | next table |
| Bytes: 0 on the pinned runs | as planned | Pilot bytes |
| Deleted: discourse's anchor bodies, moved, not copied | delivered | `WellFormed.lean` −90 lines, `Access.lean` −32. The pre-move copy used to prove the move changed nothing is saved evidence outside `lean/`, not tree code (Discourse unchanged) |

Spec 5.5 and 7.5:

| Spec item | Status | Where |
|---|---|---|
| `itemRun_iff` | delivered | `List.lean`, with helpers `mem_itemFrom` and `itemRun_ok` |
| `anchorReach_iff` | delivered | `Anchors.lean`, with `mem_anchorUnits`, `narrower_mem` and `innermost_within` |
| `discourse_within_unchanged`, `discourse_innermost_unchanged`, `discourse_anchorsOk_unchanged` | delivered | `Discourse.lean` |
| `anchor_reach_iff`, `label_reach_iff`, `title_identity` (VE.Scope) | **sc-3ab** | over `SDoc`, `covered` and `govern` |
| `restrictAssertion`, `carveAssertion` and their denotation lemmas | SC-3b | the spec's SC-3b part |
| F8: the anchor reach is `[u110, u111, u112]`, the heading `u109` | delivered | `#guard`s in `lean/VE/Scope/Examples.lean`, on the UDHR's own bytes (`udhrPieces`, `udhrAnchors`). The guards also check Article 30, the root's heading and the innermost anchor of each unit. "`govern` returns the document unchanged" is **sc-3ab** |
| F8-tree: two articles under a missing root | delivered | `#guard`: `InvalidInput: anchors must form one tree`, discourse's text from the moved `anchorsOk`. "From `admitBlock` step 7" is **sc-3ab** |
| F8-out: the headings are not in Article 29's reach | delivered | `#guard`, computed |
| F9′: `## Instructable behaviors` | layout half delivered; the title in **sc-3ab** | `#guard`s on the pinned run's own units (finding 1) |
| F10: the label reaches `[u0073.s01, …, s04]`, not s05; `NotALabel: u0073.s04`; u0182.s02 reaches `[s02, s03]` | delivered | `#guard`s, plus u0073.s08 (stops at the paragraph u0074.s01) |
| Kernel forms of the same contracts | delivered | `short_items`; `box_anchors` (containment at both boundaries, the innermost anchor, a tie of equal sizes, the reach, `ScopeUnknownAnchor` for an empty and an unknown anchor); `span_tests`; `reaches_root` (fuel, nesting, a missing parent); `anchor_checks` with `#guard`s, one per anchor diagnostic in order, and the limit at 1,024 and 1,025. Sibling-label checks go through `String.toLower`, which the kernel does not reduce, so those three are `#guard`s |

## Findings and deviations

1. **Finding for SC-3b's addendum and sc-3ab: a heading is two units in the pinned constitution run.** In
   `run-20261012T1800Z`, "### Instructable behaviors" is `u0151.heading` ("### ") followed by
   `u0151.presupposition` ("Instructable behaviors"). Spec 1.2 makes an anchor's first unit its heading. So the
   marker is the heading, and the heading's words fall inside the anchor reach (fixture F9′). For a title this is
   harmless. For a condition heading (SC-3b) the heading's own words would be governed. The addendum should decide
   how a heading's units are recorded. This is recorded in FOLLOW-UPS.md, "## sc-3a".
2. **The cut: the scope half goes to sc-3ab.** This is a dependency, not size: see the top of this report.
3. **The theorems relating discourse to the layout are in a new file, `lean/VE/Layout/Discourse.lean`.** They name
   `VE.Discourse.anchorsOk`, which is in `WellFormed.lean`, above `Anchors.lean` in the import graph. The plan names
   no file for them.
4. **Discourse's spans are mapped once.** The spec's statements write discourse's spans as `(unitKeys D).map …`. A
   literal one-line call with that argument made discourse's `within` map the units twice per call. Measured
   (interpreted, 300 units), that was 1.3 to 1.5 times slower. So the calls pass `D.base.units.map (id, start, stop)`,
   which is equal by `List.map_map`. The statements are the spec's, and `discourse_within_unchanged` and
   `discourse_innermost_unchanged` are proved by that lemma, not by `rfl`.
5. **Generated `Audit.lean` lines removed by hand, then regenerated (as sc-1a's deviation 4).** The equivalence
   theorems `before_*` first sat in the tree. When they moved out, the generated `lean/VE/Audit.lean` still named
   them, and no generator could run, because the build fails. I deleted exactly those four `#print axioms` lines
   and ran `tools/regen_generated.py --write`, which rewrote the file. `regen_generated.py --check` passes
   (31 entries).
6. **Regeneration order.** `english-lexicon-fixtures` spawns `ve_service` before the `checker-pins` entry pins the
   new build. So each regeneration ran `regen_generated.py --write --only checker-pins` first, then `--write`, both
   with `VE_REGEN_NO_RUST=1`. Rust is unchanged; its release binary was built with `tools/rust_build.py` and is
   pinned. As a result, `lean/checkers.lock` gains two `ve_service` pins: the first build (`dcf51993…`, superseded)
   and the current one (`398d29d3…`). The lock is generated and append-only, so I left it as the generator wrote it.

## Discourse unchanged

`evidence/before-bodies.lean.txt` restates the bodies discourse had at `702ff7429`: `unitSpan`, `within`,
`narrower`, `innermostAnchor`, `reachesRoot`, `definitionIn` and `anchorsOk`. It proves `before_within`,
`before_innermost`, `before_reachesRoot` and `before_anchorsOk`: each old body equals the new call on **every**
discourse document.
- Run on this HEAD, as its header says (copy to `lean/VE/Layout/Before.lean`, then `lake env lean`): exit 0.
- With a planted difference (the limit 1,024 changed to 1,023 in the old body) it fails, at `before_anchorsOk`.
- It is kept outside `lean/` on purpose: a pre-move copy in the tree would be the copy that "moved, not copied"
  rules out.

## Cost

Checklist 12. Discourse's containment is no slower after the move. The measurement is
`evidence/containment-bench.lean.txt`, interpreted, on a synthetic discourse document of n units and 40 sections.
It runs, for every unit, its innermost anchor and then `within` for every earlier unit (the `earlierUnits` pattern).

| n | pre-move bodies | calls, as first written (`unitKeys` mapped again) | calls, final (one map) |
|---|---|---|---|
| 150 | 1.6–2.1 s | 1.7–2.0 s | 1.2–1.3 s |
| 300 | 9.0–11.5 s | 14.1–15.9 s | 5.6–7.7 s |

Three runs each; the pre-move column spans both sessions, the two others ran beside it. The final calls are faster, because `innermostAnchor` builds the span list once rather than once
per anchor. No pilot route calls scope's new functions, so scope's own cost is first measured by SC-1b's B1 row.

## Size

The feed's rule is about 600 changed hand-written lines. I counted with `git diff --numstat 702ff7429`, excluding
generated files:
- Lean: **499 added** (deleted 126).
  - `Anchors.lean` 194, of which about 100 are discourse's moved bodies: 85 lines identical, and the anchor checks
    with `D.K.anchors` read as `anchors`.
  - `List.lean` 112, `Scope/Examples.lean` 141, `Layout/Discourse.lean` 26.
  - `Access.lean` +16/−32, `WellFormed.lean` +8/−90, `VE.lean` 2.
- `tests/test_scope_lean.py`: +28/−9.
- `tools/trust-classes.json`: +106/−44.

Code, tests and side table come to **633 added lines**, which is about 533 without the lines moved from discourse
(122 deleted there). This is the plan's move plus the layout half, with nothing beyond it.

Docs and evidence come on top, as in sc-1a:
- `lean/SCOPE.md` +44;
- the two evidence scripts, 68;
- the two evidence Lean texts, 117;
- the saved outputs, 54;
- `mutants.json`, 658, written by the mutant runner;
- this report and DELTA.md.

## Seeded bugs (Lean; [mutants.json](mutants.json))

32 mutants, all in Lean, the only language whose product code changed. There is at least one mutant in every new or
moved trusted definition that `tools/trust_map.py` lists:
- `Anchors.lean` S: `within`, `narrower`, `innermostAnchor`, `reachesRoot`, `anchorsOk`, `req`, `runAll`, `allOk`,
  `dupOf`, `spanIn`, `spansDisjoint`;
- `Anchors.lean` D[V]: `headingOf`, `spansOf`;
- `List.lean` S: `ItemUnit`.

There are further mutants in each claimed behaviour of the tied definitions (`anchorUnits`, `anchorReach`,
`itemFrom`, `itemRun`) and of discourse's calls.

**Method.** For each mutant, the runner:
1. applied it to the committed source;
2. ran `lake build VE.Layout.Anchors VE.Layout.List VE.Layout.Discourse VE.Scope.Examples`;
3. recorded the failing declarations;
4. restored the file.

**Result.** All 32 fail. The tree was clean afterwards, and the full `lake build` passed. When a proof caught the
mutant first, a second pass kept the mutant, replaced the failing proofs with `sorry` in a scratch copy and rebuilt,
so the fixtures ran. 28 of the 32 fail a fixture, directly or with the proofs bypassed. The other four are
proof-only:
- `ItemUnit` is a `Prop`. Only `itemRun_iff` can test it, as `GovernedItem` in sc-1a.
- Discourse's three calls have no Lean document fixture. Their spec theorems pin them, and so does the saved
  equivalence proof.

| # | Mutant | Definition | Fails | Fixtures, proofs bypassed |
|---|---|---|---|---|
| 1 | within-start: `≤` → `<` at the anchor's first byte | `within` | F8 `#guard`, F8 innermost `#guard`, F9′ `#guard` | — |
| 2 | within-end: `≤` → `<` at the anchor's last byte | `within` | F8 `#guard`, F8 innermost `#guard`, F9′ `#guard`, `box_anchors` | — |
| 3 | narrower-tie: `<` → `≤` | `narrower` | `box_anchors` | — |
| 4 | innermost-first: `foldl narrower` → `head?` | `innermostAnchor` | `innermost_within` | F8 innermost `#guard`, `box_anchors` |
| 5 | units-order: units reversed | `anchorUnits` | `mem_anchorUnits`, `anchorReach_iff` | F8 `#guard`, F8-out `#guard`, F9′ `#guard`, `box_anchors` |
| 6 | heading-last: `head?` → `getLast?` | `headingOf` | `anchorReach_iff` | F8 `#guard`, F9′ `#guard`, `box_anchors` |
| 7 | reach-heading: the heading kept in the reach | `anchorReach` | `anchorReach_iff` | F8 `#guard`, F8-out `#guard`, F9′ `#guard`, `box_anchors` |
| 8 | reach-text: `ScopeUnknownAnchor` → `ScopeUnknownUnit` | `anchorReach` | `box_anchors` | — |
| 9 | spans-swap: `(end, start)` | `spansOf` | F8 `#guard`, F8-out `#guard`, F8 innermost `#guard`, F9′ `#guard` | — |
| 10 | root-fuel: fuel 0 → true | `reachesRoot` | `reaches_root` | — |
| 11 | root-nested: parent's span not checked | `reachesRoot` | `reaches_root`, `anchor_checks` | — |
| 12 | limit: `≤ 1024` → `≤ 1025` | `anchorsOk` | `anchor_checks` | — |
| 13 | limit-boundary: `≤ 1024` → `< 1024` | `anchorsOk` | `anchor_checks` | — |
| 14 | one-tree: `== 1` → `≤ 1` | `anchorsOk` | F8-tree `#guard` | — |
| 15 | label-case: `toLower` dropped | `anchorsOk` | DuplicateAnchor `#guard` | — |
| 16 | overlap: disjointness not checked | `anchorsOk` | overlap `#guard` | — |
| 17 | exports-unary: unary test dropped | `anchorsOk` | `anchor_checks` | — |
| 18 | exports-def: any definition span accepted | `anchorsOk` | `anchor_checks` | — |
| 19 | req-swap: never fails | `req` | `req_ok` | F8-tree `#guard`, overlap `#guard`, `anchor_checks` |
| 20 | runall-skip: continues past a failure | `runAll` | `runAll_ok`, `runAll_cons` | F8-tree `#guard`, DuplicateAnchor `#guard`, overlap `#guard`, `anchor_checks` |
| 21 | allok-first: checks the first element only | `allOk` | `allOk_ok`, `allOk_iff` | DuplicateAnchor `#guard`, overlap `#guard`, `anchor_checks` |
| 22 | dupof-none: finds no repeat | `dupOf` | `dupOf_none` | `anchor_checks` |
| 23 | spanin-strict: `≤` → `<` | `spanIn` | `span_tests`, `anchor_checks`, DuplicateAnchor `#guard`, overlap `#guard`, touching siblings `#guard` | — |
| 24 | disjoint-strict: touching spans overlap | `spansDisjoint` | F8 anchorsOk `#guard`, `span_tests`, box anchorsOk `#guard`, touching siblings `#guard` | — |
| 25 | item-same-depth: `d <` → `d ≤` | `itemFrom` | `mem_itemFrom` | F10 `#guard`, `short_items` |
| 26 | item-midline: mid-line units dropped | `itemFrom` | `mem_itemFrom` | F10 `#guard`, `short_items` |
| 27 | item-label: the label not required | `itemRun` | `itemRun_ok` | F10 NotALabel `#guard`, `short_items` |
| 28 | item-text: `NotALabel` → `NotALeadIn` | `itemRun` | F10 NotALabel `#guard`, `short_items` | — |
| 29 | itemunit-depth: `d <` → `d ≤` in the statement | `ItemUnit` | `itemRun_iff` | proof-only |
| 30 | discourse-within: a unit's end read as its start | discourse `within` | `innermost_within`, `acc_no_heuristic` | proof-only |
| 31 | discourse-innermost: anchors reversed | discourse `innermostAnchor` | `innermost_within` | proof-only |
| 32 | discourse-anchorsok: unary test always true | discourse `anchorsOk` | `discourse_anchorsOk_unchanged` | proof-only |

One more check can fail: the saved equivalence proof fails on a planted difference (Discourse unchanged).

## Trust

Measured on this HEAD with `uv run python tools/trust_map.py --check` against `702ff7429`: **PASS**.

| | Lines |
|---|---|
| K | +0 |
| S | +6 net: `Anchors.lean` +63 (moved bodies and generic checks), `List.lean` +7 (`ItemUnit`), against `WellFormed.lean` −48 and `Access.lean` −16 |
| D[V] untied | +5 (`headingOf`, `spansOf`) |
| tied, not trusted | `anchorUnits`, `anchorReach`, `itemFrom`, `itemRun`; discourse's `within`, `innermostAnchor`, `anchorsOk` (now G[V], tied by the three `discourse_*_unchanged` theorems) |
| trusted | **+11 net** (`Anchors.lean` +68, `List.lean` +7, `WellFormed.lean` −48, `Access.lean` −16) |

- Recorded with `--allow` as S +6 and V +5, `SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-3a, 2026-10-19`.
- `lean/VE/Layout/Discourse.lean` holds theorems only (an empty table entry), and the new fixtures are T.
- **R16 "exercised".** `tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem` found
  three moved definitions that no theorem stated anything about: `spanIn`, `spansDisjoint` and `reachesRoot`. The
  fixtures `span_tests` and `reaches_root` close that gap. `::test_each_tie_names_a_theorem_about_its_definition`
  now covers the ties of `Anchors.lean`, `List.lean`, `Access.lean` and `WellFormed.lean`.
- The ties-pass row is in manage-agents FOLLOW-UPS.md, "## sc-3a (2026-10-19)".

## Tests

- **Selected tests** (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`), on ve-mac-1 at
  `b152db4a` (clean): 356 of 445 units, exit 0, 0 failed. The run included `lake build`, the audit, all five
  `tests/test_discourse*.py` files, `test_scope_lean.py`, `test_trust_budget.py` and `test_frozen_sources.py`.
- **After the last Lean change** (`8b91d997`, discourse's one-map spans), on ve-mac-1: the discourse, scope,
  trust, frozen, assurance and regeneration tests, 11 files, 468 passed, exit 0.
- **New and changed tests:** `tests/test_scope_lean.py`, 4 tests. The tie check is widened; no test was added or
  removed.
- **Lean:**
  - `lake build`: 1,023 jobs, no error.
  - `python3 lean/audit.py`: PASS, 572 files, 6,504 theorems, only the standard axioms.
- **Generated files:** `uv run python tools/regen_generated.py --check`: 31 entries, all current.
- **Gate collection:** `uv run python tools/gate_collection.py --check --prebuilt`: 18,161 collected, 0 added,
  0 removed, 0 refused, 0 stale, 0 malformed.
- **Other checks:** `tools/repo_map.py --check` PASS (36 modes); `tools/check_lean_imports.py` PASS;
  `review-ready.py --delta-dri-needed`: no DELTA row reserved for the DRI.
- **Full gate:** not run by me, as the task says. The chain runs it on the final HEAD.
- **Known red:** none of `main-known-red.txt`'s tests failed in the selected run.

## Pilot bytes (estimate)

0 B in both pilots, as the plan says ("0 pinned", measured by SC-M0). The constitution's 39 headings (349 B) and
the UDHR's 32 (495 B) are titles, already LABELLED. The 42 bold labels are blocked by their own content. No route
calls the layout yet. Nothing is claimed before a pilot audit.

## Next items

- **sc-3ab** (after sc-1ac's `SDoc`, `covered` and `govern`):
  - spec 5.5's `anchor_reach_iff`, `label_reach_iff` and `title_identity`;
  - `coveredLayout`'s anchor and label cases, which call `VE.Layout.anchorReach` and `VE.Layout.itemRun` as built
    here;
  - `admitBlock` step 7 (`VE.Layout.anchorsOk` on the block's anchors) and step 8 (title reaches; heading and item
    units);
  - the fixtures' `govern` halves: F8 (the document unchanged), F8-tree through `admitBlock`, F9′ as a title, and
    F-meta's two-root case.

  Its trust growth should be small, because the reaches are built here.
- **sc-3b** follows: condition headings, gated on its approved addendum and SC-2. Finding 1 is an input to that
  addendum.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no relayed Lean answer and no response field is added; no route,
   mode or schema changes.
2. **Every required deliverable built.** PASS, with every plan row in the Plan rows table above. The scope half is
   sc-3ab, a dependency cut (sc-1ac). No Python copy of a Lean decision and no report test was added. The only
   hand-written shared files are `Access.lean`, `WellFormed.lean` (in-flight check) and `VE.lean` (`[union]`).
   Probe: `git diff --name-only main...HEAD`.
3. **Tests and gates can fail.** PASS: 32 seeded Lean mutants, all failing a named check (`mutants.json`), plus the
   planted difference in the equivalence evidence. The R16 check's own can-fail test is
   `tests/test_scope_lean.py::test_a_definition_no_theorem_uses_is_reported`.
4. **Python, Lean and Rust agree; valid inputs still pass.** PASS: discourse's answers are proved equal to the
   pre-move bodies on every document (`evidence/before-bodies.lean.txt`). The discourse three-way and Lean tests
   pass unchanged (`tests/test_discourse_three_way.py`, `tests/test_discourse_lean.py`, 468 tests). The pilot
   excerpts (F8, F9′, F10) are valid inputs and pass.
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I can take it: all commits are made and the tree is
   clean; the chain runs the full gate on the final HEAD. The evidence commit list is below.
7. **No unsigned item.** PASS: the one DELTA row cites R16, and its conditions hold (net 11 <= 150, K +0,
   itemised, exercised, FOLLOW-UPS row). `review-ready.py --delta-dri-needed`: none.
8. **Every user-visible change in DELTA.** PASS: DELTA.md has the trust row and says why nothing else is a delta.
   Discourse is proved unchanged, and its tests pass.
9. **Test selection finds the tests.** PASS: `tools/select_tests.py --base 702ff7429` selects 356 of 445 units,
   including `lake build`, the audit and `tests/test_scope_lean.py`. Those are the checks every seeded mutant fails.
   Every new path has a layer (`tools/layer_policy.source_layer`: `lean/VE/Layout/*` 2, `docs/scope/sc-3a/*` 5).
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` is 17 of 17 exact, and
    `statements-unchanged.txt` shows 0 of 5,978 statements changed. Mutants 5–7, 25–27 and 29 break
    `anchorReach_iff`, `mem_anchorUnits`, `mem_itemFrom`, `itemRun_ok` and `itemRun_iff`.
11. **Budgets fail closed.** PASS for the one limit touched: the anchor limit is a `ResourceLimit` at 1,025 and
    passes at 1,024 (`anchor_checks`; mutants 12 and 13). No other budget changes.
12. **No CPU or memory regression.** PASS: see Cost. The first version's second map was found and removed
    (`8b91d9974`). The final calls are faster than the pre-move bodies on the benchmark.
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale,
    0 malformed. No test was removed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
0ca349b26 sc-3a: containment benchmark evidence reads the Before bodies from their one saved copy
8b91d9974 sc-3a: discourse passes its spans with one map (no extra cost); proofs by List.map_map; containment benchmark evidence
b152db4a5 sc-3a: List.lean header names the label reach; declarations regenerated
e964340dc sc-3a: R16 trust allowance (S +6, V +5 net, K +0); lean/SCOPE.md for the anchor and label reaches
81375952b sc-3a: seeded bugs: 32 Lean mutants over every new or moved trusted definition, each failing a named check
5975c507f sc-3a: pre-move equivalence kept as saved evidence, not in the tree; span and root-walk fixtures; R16 tie checks; statement evidence
8a52b80a8 sc-3a: layout anchors (discourse's containment and anchor checks moved to VE.Layout), label reach itemRun
```
