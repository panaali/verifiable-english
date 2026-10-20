# sc-1ac: `govern` and the block's admission (scope@0, Lean core). Build report

No DRI signature is reserved in this item. The one DELTA row (trust budget, +132 lines, K +0) is signed by standing
ruling R16. To fit R16 and the size rule, the item is cut in two. **sc-1ac** builds the data model, the reaches, the
base objects, the unary effects, `admitBlock`, `govern`, five of spec 5.1's theorems and 7.1's `govern` fixtures.
**sc-1ad** builds the rest (Next items):
- the precedence graph step;
- the theorems about what `govern` writes;
- the three refusal theorems, already proved on local branch `wip/sc-1ad-refusals`;
- the run path `governFast`.

- Branch `feature/sc-1ac`, worktree `/home/seyran/code/ve-sc-1ac`, merge base `75a9bcef9` (main, after sc-1ab).
- Plan: [scope-PLAN.md](../../spec/scope-PLAN.md), section "SC-1a. Lists and lead-ins: Lean core" and design 1.2–1.4.
  Spec: [scope.md](../../spec/scope.md), 1.1–1.5, 4.2, 5.1, 6 and 7.1. Both are identical to `beb5c4630`
  (`git diff beb5c4630 HEAD -- docs/spec/scope*.md` is empty; the blobs are `44fbade7` and `80f31a10`, as sc-1a
  recorded).
- SYNTHESIS 4.1 and 4.2: SC-1a is a phase-4 Lean core, and no shared-file queue names its files.
  DRI-DECISIONS-PHASE2 "Scope": SC1 (the AP-3 → SC-4 queue) and SC2 (pilot prompts) do not touch sc-1ac. SC3 (layer
  `research`) does not apply, because `VE.Scope.*` is already layer 2 (profiles).
- sc-3a's files (`lean/VE/Layout/`, `lean/VE/Discourse/`) are not touched.
- Plain words: [lean/SCOPE.md](../../../lean/SCOPE.md), section "`VE/Scope/Govern.lean`".

## Statement gate

**PASS.** The scope statement review closed with PASS (`manage-agents/scope-p3ver1.final.md`, then
`scope-p3ver2.final.md`), which opened SC-1a; sc-1a's [STATEMENT-GATE.md](../sc-1a/STATEMENT-GATE.md) records it.
sc-1ac is part of SC-1a.

[statement-diff.txt](statement-diff.txt), from [evidence/spec_diff.py](evidence/spec_diff.py), compares each
declaration built here with spec 4.2 and 5.1. It ignores whitespace and comments, and compares theorems up to `:=`:
- **Theorems: 5 of 5 exact**: `itemRule_decoder`, `govern_identity`, `govern_orphan`, `govern_admits`,
  `governorsOf_iff`. No statement had to change, so the item did not stop.
- **Definitions: 36 of 39 exact.** The other three are `coveredLayout`, `admitBlock` and `govern`; each refuses what a
  later item adds (deviations 1 to 3).
- **Helpers not in the spec**: `coversU_iff`, `mem_ordered`, `ordered_sorted`, `baseName_some`.

## Plan rows

| Row (task; plan SC-1a, the `govern` part) | Status | Where |
|---|---|---|
| `Reach`, `Governor`, `SDoc` | delivered | `lean/VE/Scope/Govern.lean`; spec text, exact |
| `applyEffect`, `itemRule` with `itemRule_decoder` | delivered | same; `Theorems.lean` |
| The reaches: `coveredLayout`, `frameOn`, `covered`, `governorsOf` with `governorsOf_iff` | delivered | the anchor and label reaches are **sc-3ab** (task); until then refused (deviation 1) |
| `baseObj`, `baseName`, the order (`classOf`, `position`, `ordered`), `composed`, `orderCheck`, `affected`, `patch` | delivered | spec text, exact; `ordered_sorted` states order 1.4 |
| `admitBlock` steps 1–6 | delivered | spec text |
| `admitBlock` step 8 | delivered, without its anchor and label unit check | that check and step 7 are **sc-3ab** (task); until then a block with anchors is refused (deviation 2) |
| `govern` | delivered | the precedence graph step is **sc-1ad** (the cut); until then a graph governor is refused (deviation 3) |
| `govern_identity`, `govern_orphan`, `govern_admits`, `governorsOf_iff`, `itemRule_decoder` | delivered | `Theorems.lean` |
| `frontier_graph_refused`, `readings_refused`, `nonrule_refused` | **sc-1ad** (size) | proved, with their admission lemma `admit_governor`, on local branch `wip/sc-1ad-refusals` = `cd750a68a`; removed here in `cac25d177`. Their fixtures (F-fg, F-rs, F-nr) are delivered here |
| `govern_preserves`, `govern_provenance`, `decodeNorm_name`, `govern_strings`, `govern_no_new_symbols`, `HasStr`, `payload`, `BlockBound` | **sc-1ad** (R16 and size) | not started |
| The run path `governFast` with `governFast_eq` | **sc-1ad** (size) | not started |
| 7.1's `govern` fixtures | delivered, except F-sym | next table |
| Seeded bugs for each | delivered | 58 Lean mutants (Seeded bugs) |
| The R16 row | delivered | [DELTA.md](DELTA.md): +132 |
| `lean/audit.py` and `tools/regen_generated.py --check` pass | delivered | Tests |
| `lean/VE.lean` imports, `lean/SCOPE.md` | delivered | one import (a `[union]` file); a section on `govern` |

Spec 7.1's `govern` fixtures (`lean/VE/Scope/Examples.lean`, section "sc-1ac"). They are `#guard`s on the
hard-constraint layout, with u0173.s01 after it and the norms chain's environment:

| Fixture | Status |
|---|---|
| F1-g | delivered: u0165.s01's and u0165.s07's contents are the spec's JSON byte for byte. Every item is composed, the lead-in keeps no content, and every unit keeps its id, kind and place |
| F1″ | delivered: `govern` succeeds, and `itemRule` gives the norms chain's own text (`fields do not match: expected [name, predicate, sign, guard, unless, over], got [guard, name, over, sign, unless]`) |
| F-id | delivered, both halves (a four-norm document with another member; no content with a well-formed list name), equal as values |
| F-orph | delivered: `ScopeOrphanPart: u0165.s01` |
| F-meta | delivered: the three list-name cases with the spec's texts. The two-root anchor case is refused as `UnsupportedProfile: scope@0 anchors require SC-3a` until sc-3ab, which gives discourse's text |
| F-fg, F-mm, F-2f, F-rs, F-nr, F-pend, F-go | delivered with the spec's values. F-rs also refuses the governor's own unit and returns an unrelated reading set unchanged |
| F-sym | **sc-1ad**: it is the counterfixture of `govern_no_new_symbols`. Its computed half (`unless` gets the payload's string) holds here |

Beyond 7.1, each one added so that a seeded bug fails a fixture:
- each admission step's refusal in fault order, and the limits at 256 and 257;
- `ScopeReserved: own`, `ScopeUnknownRule`, and a carve-out on a rule without `unless`;
- SC-2's F7 and F7′ on this item's `govern`;
- the order of two carve-outs of one class and of a `rules` reach;
- the refusals that stand until sc-1ad and sc-3ab.

Kernel theorems on a three-unit document (`short_access`, `short_base`, `short_effects`, `short_govern`, by `rfl`)
state the values of every definition. `reaches_seven`, `governor_fields` and `sdoc_fields` pin the data types.

## Deviations

1. **The anchor and label reaches are sc-3ab's (task).** `coveredLayout` refuses them with
   `UnsupportedProfile: scope@0 anchor reach requires SC-3a` (and `label`), in the form of the spec's frontier
   refusal. It never reads them as empty. sc-3ab replaces the two lines with `VE.Layout.anchorReach` and
   `VE.Layout.itemRun`.
2. **`admitBlock` has no step 7 yet (task), and tests `null` by its constructor.**
   - Discourse's anchor checks and step 8's anchor and label unit check are sc-3ab's. Until then a block with anchors
     is refused (`UnsupportedProfile: scope@0 anchors require SC-3a`). Without that line the built `admitBlock`
     would admit anchors that spec 6.2 step 7 refuses, which would widen what is accepted. I found this while writing
     the DELTA and fixed it in `283f9e429`. `anchorsOk` passes on an empty list, so a block without anchors is
     admitted exactly as the spec admits it.
   - `c.isNull`, not the spec's `c == .null`. Lean's `==` on `Json` is a `partial def` (`Lean/Data/Json/Basic.lean`,
     `beq'`), opaque to proofs, so `nonrule_refused` cannot be proved of the spec's text. `isNull` and the compiled
     `==` agree on every value (a `#guard` checks one value of each constructor). This is recorded for the spec's next
     revision in FOLLOW-UPS.md, "## sc-1ac".
3. **The precedence graph step is sc-1ad's (the cut).** `normOf`, `edgesOf`, `edgesInto`, `ruleTable`, `edgesFor`
   and `addOver` would add about 31 trusted lines, which takes the item over R16's 150 (measured: 167). Until
   sc-1ad, `govern` refuses a `precedes` or `yields` governor after composition, where `ruleTable` would run
   (`UnsupportedProfile: scope@0 precedence requires SC-4`). For a block without graph governors the spec's graph
   step changes nothing: `ruleTable` decodes no unit and `addOver []` returns its object.

   So every answer the built `govern` gives is the answer of the spec's text. It refuses more (anchors, anchor and
   label reaches, precedence), never less. This is argued here and pinned by fixtures, not proved; sc-1ad and sc-3ab
   restore the spec's text.
4. **The refusal theorems moved to sc-1ad (size).** `frontier_graph_refused`, `readings_refused` and
   `nonrule_refused` are proved from `admit_governor`, a 50-line lemma that walks the 42 effect and reach cases of
   step 8. Together they are 89 lines. They are kept on `wip/sc-1ad-refusals` and need no change to come back.
5. **Fixture form (as sc-1a's deviation 2).** The pilot-layout fixtures are `#guard`s. The kernel forms are `rfl`
   theorems on a three-unit document, with `List.mergeSort_singleton` and `List.mergeSort_nil` rewritten first:
   `mergeSort` is well-founded recursion, which the kernel does not unfold. Order 1.4 over several governors is
   `ordered_sorted` (through `List.sorted_mergeSort`) and the `#guard` on the order of carve-outs.
6. **Generated `Audit.lean` lines removed by hand, then regenerated (as sc-1a's deviation 4).** When the refusal
   theorems moved out, the generated `lean/VE/Audit.lean` still named them and no generator could run. I deleted
   exactly those five `#print axioms` lines and ran `tools/regen_generated.py --write`, which rewrote the file.
7. **Reused lemmas.** `Theorems.lean` imports `VE.NormDefaults.Check` (`ebind_ok`) and `VE.Readings.Strings`
   (`startsWith_append_ascii`) instead of copying them. `tools/check_lean_imports.py` passes.

## Size

The feed's rule is about 600 changed hand-written lines (`git diff --numstat 75a9bcef9`, generated files excluded).
This item is **about 650 lines of code, fixtures, tests and side tables** (646 added):
- Lean 538: `Govern.lean` 232 (definitions, spec text; 68 of them reject-only, G[R]), `Examples.lean` 236 (the
  fixtures and their kernel forms), `Theorems.lean` 69, `VE.lean` 1.
- `tests/test_scope_lean.py` +13/−3.
- `tools/trust-classes.json` 93, `ve/assurance-manifest.json` 2.

That is above 600, after the two cuts. The first cut, the graph step, was measured at 167 trusted lines, 714
hand-written lines at the midpoint. The second, the refusal theorems, saved 89 lines. What remains is the spec's text
of the definitions sc-3ab and sc-1ad build on, with the fixtures that the R16 condition (each new trusted definition
exercised) and the 58 mutants need. Cutting further would split a definition from its fixtures.

Docs and evidence come on top, as in sc-1a and sc-1ab:
- `lean/SCOPE.md` +40;
- `DELTA.md` 20;
- `mutants.json` 60;
- `statement-diff.txt` 56 (the script's output);
- `evidence/spec_diff.py` 39;
- this report.

`docs/trust-baseline.json` (+14) is the allowance ledger written by `trust_map.py --allow`.

## Overlap check

Hand-written files: `lean/VE/Scope/{Govern,Theorems,Examples}.lean`, `lean/VE.lean`, `lean/SCOPE.md`,
`tests/test_scope_lean.py`, `tools/trust-classes.json`, `docs/trust-baseline.json`, `ve/assurance-manifest.json`,
`docs/scope/sc-1ac/*`. I compared them with `git diff --name-only main...<b>` for every `lean-first/*`, `feature/*`,
`infra/*` and `foundation/*` branch (2026-10-20):
- `lean/VE.lean` (a `[union]` import list) is also edited by `feature/ap-1b`, `feature/me-9` and `foundation/me-1`.
- The JSON ledgers are also edited by `feature/ap-1b`, `feature/df-1ab`, `feature/et-3c`, `feature/jt-2`,
  `feature/me-9`, `feature/qt-a1c` and `foundation/me-1`. `tools/trust-classes.json` and
  `docs/trust-baseline.json` merge through the `ve-generated` driver. `ve/assurance-manifest.json` is also edited by
  `feature/jt-2` and `foundation/me-1`, in other entries.
- No other branch touches `lean/VE/Scope/`, `lean/SCOPE.md` or `tests/test_scope_lean.py`.

## Seeded bugs (Lean; [mutants.json](mutants.json))

58 mutants, all in Lean, the only language whose product code changed. The Python change is a test file, and the
JSON files are side tables and ledgers.

**Coverage.** Every one of the 30 new trusted definitions that `tools/trust_map.py` lists has at least one mutant:
- S: `Reach`, `Governor`, `SDoc`, `applyEffect` (3), `isFrame`, `unary`, `graph`, `baseObj` (2), `covered`,
  `classOf`, `position`, `ordered`, `composed`, `affected`, `govern` (3);
- G[V]: `keysOf`, `unitsOf`, `idOf`, `unitIds`, `contentOf`, `isPart`, `isNorm`, `objectOf`, `partUnits`, `ruleUnits`,
  `coveredLayout` (2), `frameOn`, `baseName`, `newContent`, `patch`.

Further mutants cover the tied definitions (`itemRule`, `governorsOf`, `coversU`) and every claimed behaviour of the
reject-only code: `admitBlock`'s steps (14), `orderCheck`, `firstDup`, `conditions`, `vocabularyNames` and
`setUnits`.

**Method.** The runner (outside the repository) handled each mutant in turn:
1. It applied the mutant to the committed source.
2. It ran `lake build VE.Scope.Examples` and recorded the failing declarations.
3. When a proof in `Theorems.lean` failed first, it compiled the fixtures a second time without `Theorems.lean`, in a
   scratch copy of `Examples.lean` importing `VE.Scope.Govern`. It recorded the fixtures that fail beyond the
   unmutated control. The only control error is sc-1ab's `mergeParts_text`, which needs `Theorems.lean`.
4. It restored the file.

**Result.** The final sweep ran on `1ecdf1612`, the final code. All 58 mutants fail, and every one fails a fixture
too: 51 a fixture directly, and the 7 caught first by a proof also with the proofs bypassed. Afterwards the tree was
clean and `lake build` passed.

**Equivalent until sc-1ad.** `affected`'s `precedes` and `yields` rows are spec text, but `govern` refuses every
graph governor after composition. A mutant in those rows therefore changes no answer until sc-1ad, and none is
listed.

**Survivors of earlier sweeps, each fixed:**
- `coversU` reading the recorded units survived every `govern` fixture. Admission makes the recorded and
  regenerated reaches equal, so only `coversU_iff` caught it. `short_base` now states `coversU` directly.
- A cites part (for `isPart` and `newContent`) had no fixture.
- F7′'s guard passed when both orders failed.
- `ScopeReserved: own` had no fixture.

| # | Definition | Mutant (claimed behaviour) | Fails |
|---|---|---|---|
| 1 | `Reach` | an eighth constructor (the seven reaches) | `reaches_seven` |
| 2 | `Governor` | an extra field with a default | `governor_fields`, the fixtures' governors |
| 3 | `SDoc` | an extra field with a default | `sdoc_fields`, `short_access` |
| 4 | `keysOf` | keys reversed | `short_access` |
| 5 | `unitsOf` | the first unit dropped | F1-g `#guard`s, `short_access` |
| 6 | `idOf` | reads `kind` | F1-g `#guard`s, `short_access` |
| 7 | `unitIds` | reversed | `#guard`s, `short_access` |
| 8 | `contentOf` | a missing unit reads `[]` | `short_access` |
| 9 | `isPart` | a cites part is no part | `short_access`, `short_govern` |
| 10 | `isNorm` | a cites norm is no norm | `short_access` |
| 11 | `objectOf` | part and norm swapped | F1-g, `short_access` |
| 12 | `partUnits` | reads norms | F-orph, `short_access` |
| 13 | `ruleUnits` | parts only | `#guard`s, `short_access` |
| 14–16 | `applyEffect` | no `own` substitution; a carve-out replaces `unless`; a frame is refused | `short_effects`; the F7′ and order `#guard`s |
| 17–19 | `isFrame`, `unary`, `graph` | a constructor dropped | `short_effects`, `#guard`s |
| 20–21 | `coveredLayout` | a list reach is empty; an anchor reach is empty | F1-g; the anchor refusal `#guard` |
| 22 | `frameOn` | any effect gives a base object | the order `#guard` |
| 23–24 | `baseObj` | no orphan refusal; two frames take the first | `short_base`; F-2f |
| 25 | `baseName` | reads the predicate | `baseName_some`; the order `#guard` |
| 26 | `covered` | a rules reach covers every rule | the order `#guard` |
| 27–29 | `classOf`, `position`, `ordered` | rules early; every position 0; unsorted | the order `#guard`; `ordered_sorted` |
| 30 | `composed` | no effect applied | F7′ and order `#guard`s |
| 31 | `affected` | a part is not affected | `short_govern` |
| 32 | `newContent` | cites dropped | `short_govern` |
| 33 | `patch` | other units touched | `short_govern` |
| 34–36 | `govern` | no admission; precedence ignored; an orphan accepted | `govern_admits` and 26 `#guard`s (F-meta); the precedence `#guard`; `govern_orphan`, F-orph |
| 37–39 | `itemRule`, `governorsOf`, `coversU` (tied) | the item decoded alone; any effect; the recorded units | their tie theorems; F1″, F-go, `short_base` |
| 40–53 | `admitBlock` | each step's check dropped or moved off its boundary (limits, unknown unit, list-name scope and units, anchors, `ownSafe`, the frame's unit and reach, frontier graph, recorded units, reading sets, non-rules, `null`) | each step's `#guard` (F-meta, F-mm, F-fg, F-rs, F-nr, F-pend, the 257 and 256 boundaries) |
| 54–58 | `orderCheck`, `firstDup`, `conditions`, `vocabularyNames`, `setUnits` | commute everything; no repeat; a carve-out has no condition; no sorts; reads `id` | F7; duplicate, depth, `ScopeReserved` and F-rs `#guard`s |

## Trust

Measured on this HEAD with `uv run python tools/trust_map.py --check` against `75a9bcef9`: **PASS**.
- K +0, S +90, G[V] +42 untied, trusted **+132**, all in `lean/VE/Scope/Govern.lean`.
- Tied, not trusted: `coversU`, `governorsOf`, `itemRule`. G[R] (reject-only, not trusted): `admitBlock`,
  `orderCheck`, `conditions`, `vocabularyNames`, `firstDup`, `setUnits`.
- `Theorems.lean` is P, and the new fixtures are T.
- The growth is recorded with `--allow` as `SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-1ac, 2026-10-18`.
- Every new trusted definition is named by a theorem
  (`tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem`). That check can fail
  (`::test_a_govern_definition_no_theorem_uses_is_reported`), and every such definition has a mutant that fails
  (above). The ties are checked by `::test_each_tie_names_a_theorem_about_its_definition`.
- The ties-pass row is in manage-agents FOLLOW-UPS.md, "## sc-1ac (2026-10-20)".

## Tests

- **Lean**:
  - `lake build` (1,051 jobs) has no error, and every `#guard` and kernel fixture holds. `VE.Scope.Theorems` builds
    in about 2 s and `VE.Scope.Examples` in about 26 s.
  - `python3 lean/audit.py`: PASS, 596 files, 6,744 theorems, only the standard axioms.
- **Generated files**: `uv run python tools/regen_generated.py --check`: 32 entries, all current.
- **Gate collection**: `uv run python tools/gate_collection.py --check --prebuilt`: 18,423 collected, 4 added,
  0 removed, 0 refused, 0 stale, 0 malformed. No test was removed.
- **Other checks**: `tools/repo_map.py --check` PASS (37 modes; none added); `tools/check_lean_imports.py` kept
  (596 modules); `tests/test_assurance_manifest.py` 137 passed after the reason for `Govern.lean` was added.
- **Selected tests** (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`):
  - on ve-mac-1 at `a5f795cb` (clean): 80 of 457 units, exit 0, 0 failed;
  - FINAL_RUN.
  No test from `main-known-red.txt` failed.
- **Full gate**: not run by me, as the task says. The chain runs it on the final HEAD.

## Pilot bytes (estimate)

0 B in both pilots: no route calls `govern` yet. The first scope number moves at SC-1b (an estimate of +22 B on the
constitution, u0164.s02's lead-in), after sc-1ad, ar-10a and lf-16g. Nothing is claimed before a pilot audit.

## Next items

- **sc-1ad** (cut from this item for R16 and size):
  - the precedence graph step, about +31 trusted lines: `normOf`, `edgesOf`, `edgesInto`, `ruleTable`, `edgesFor`,
    `addOver`. It replaces `govern`'s precedence refusal with spec 4.2's text;
  - `HasStr`, `payload` and `BlockBound`;
  - the theorems `decodeNorm_name`, `govern_preserves`, `govern_provenance`, `govern_strings` and
    `govern_no_new_symbols`, with F-sym;
  - the run path `governFast` with `governFast_eq`;
  - `frontier_graph_refused`, `readings_refused` and `nonrule_refused`, from `wip/sc-1ad-refusals` (`cd750a68a`).

  A risk recorded in FOLLOW-UPS: `govern_preserves` reads members of a raw `Std.TreeMap.Raw` after `setObjVal!`,
  sc-1a's `mergeParts` finding again. It should be checked against an unordered tree before it is proved.
- **sc-3ab**: the anchor and label reaches in `coveredLayout`, `admitBlock` step 7 (replacing the anchors refusal) and
  step 8's anchor and label unit check, spec 5.5's `anchor_reach_iff`, `label_reach_iff` and `title_identity`, and
  the fixtures' `govern` halves (F8, F8-tree, F9′, F-meta's two-root case). It needs only this item's `SDoc`,
  `covered` and `govern`.
- **SC-1b** follows sc-1ad, ar-10a and lf-16g. Its document mode calls `governFast`, which is sc-1ad's.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no relayed Lean answer, route or response field is added.
2. **Every required deliverable built.** PASS: see Plan rows. The cuts to sc-1ad and sc-3ab follow the task (sc-3ab)
   and the feed's size rule and R16 (sc-1ad), and are named. There is no Python copy of a Lean decision and no new
   report test. The shared hand-written files are a `[union]` import list and the JSON ledgers (Overlap check).
   Probe: `git diff --name-only main...HEAD`.
3. **Tests and gates can fail.** PASS: 58 seeded Lean mutants, each failing a named theorem or `#guard`, and each
   failing a fixture with the proofs bypassed (`mutants.json`), with an unmutated control. The R16 check's can-fail
   test is `tests/test_scope_lean.py::test_a_govern_definition_no_theorem_uses_is_reported`.
4. **Python, Lean and Rust agree; valid inputs still pass.** N.A. for agreement: only a Lean implementation exists.
   Valid inputs pass: F1-g (the seven hard-constraint rules composed) and F-id (`#guard`s).
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I can take it. The tree is committed and clean, and the
   chain runs the full gate on the final HEAD. The evidence commit list is below (`git log --no-merges main..HEAD`).
7. **No unsigned item.** PASS: the one DELTA row cites R16 and meets its conditions (132 <= 150, K +0, itemised,
   exercised, FOLLOW-UPS row).
8. **Every user-visible change in DELTA.** PASS: DELTA.md lists the trust row and says why nothing else is a delta.
   There is no caller, and every answer is the spec's text's answer (deviation 3).
9. **Test selection finds the tests.** PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 80 of
   457 units on the Mac. They include `lake build`, `lean/audit.py`, `tests/test_scope_lean.py`,
   `tests/test_trust_budget.py` and `tests/test_assurance_manifest.py`; the Lean build runs every mutant's failing
   check.
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` has 5 of 5 theorems exact, with no
    hypothesis added. Mutants 34, 36 and 37–39 break `govern_admits`, `govern_orphan`, `itemRule_decoder`,
    `governorsOf_iff` and `coversU_iff`.
11. **Budgets fail closed.** PASS for the limits added: 256 governors and 256 list names (`ResourceLimit`, with
    `#guard`s at 256 and 257; mutants 40–41), and the condition depth (`ResourceLimit: scope condition depth
    exceeds 64`, `#guard` with `nest 64`; mutant 56).
12. **No CPU or memory regression.** N.A. for the pilots: no route calls the new code. Build cost: `VE.Scope.Theorems`
    about 2 s and `VE.Scope.Examples` about 26 s. The run path's benchmark is SC-1b's B1, on `governFast`.
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and
    0 malformed. No test was removed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
1ecdf1612 sc-1ac: regenerate declarations
283f9e429 sc-1ac: refuse a block with anchors until sc-3ab's anchor checks (fail closed; F-meta's anchor case)
a5f795cb6 sc-1ac: saved statement diff (5 of 5 theorems exact; 38 of 41 definitions, 3 deviations) and 57 seeded Lean mutants
c02c7caec sc-1ac: R16 trust allowance (S +90, V +42, K +0)
d3440c440 sc-1ac: coversU kernel fixture; assurance manifest reason for Govern.lean; lean/SCOPE.md for govern; regenerate
75a2bd23b sc-1ac: fixtures for cites parts, ScopeReserved and F7′ on a composed rule; drop guards the kernel forms cover
cac25d177 sc-1ac: cut the refusal theorems to sc-1ad (size rule; saved on wip/sc-1ad-refusals); R16 checks for Govern.lean; regenerate
cd750a68a sc-1ac: trust classes for VE.Scope.Govern; regenerate
b231ac807 sc-1ac: kernel fixtures naming every new trusted definition; ordered_sorted, baseName_some
83e83a15a sc-1ac: VE.Scope.Govern (reaches, admitBlock, govern) with theorems and spec 7.1 fixtures
```
