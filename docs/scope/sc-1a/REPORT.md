# sc-1a: lists and lead-ins, the Lean core (first part). Build report

No DRI signature is reserved in this item. The one DELTA row (trust budget, +79 lines, K +0) is signed by standing ruling
R16. To fit the feed's size rule and R16, this item is the plan's SC-1a cut to its first coherent part: the layout's
list runs, that is, which units a lead-in governs (`VE.Layout.List`, with `listRun_iff` and `listRun_ok_iff` proved
and the spec's layout fixtures). The effects on a rule's JSON object are the next item, **sc-1ab**: joining parts,
conditions and `own`, and the order table. Most of it is already built and proved, saved on local branch
`wip/sc-1ab-own`. `govern` and its theorems follow in **sc-1ac**.

- Branch `feature/sc-1a`, worktree `/home/seyran/code/ve-sc-1a`, merge base `c7fc6acac`.
- Plan: `research/scope-p1` at `5c5faba50`, [scope-PLAN.md](../../spec/scope-PLAN.md), section "SC-1a. Lists and
  lead-ins: Lean core", and the gate text of section 5.
- Spec: [scope.md](../../spec/scope.md), sections 1.2, 4.1, 5.1 and 7.1.
- Both files are copied verbatim from `5c5faba50` (same git blobs, `44fbade7` and `80f31a10`). Main did not have
  them. Their links to `docs/research/scope*.md` do not resolve on main, because the research files are not on main.
  No test checks those links.
- Plain words: [lean/SCOPE.md](../../../lean/SCOPE.md).

## Statement gate

**PASS**, recorded in [STATEMENT-GATE.md](STATEMENT-GATE.md).
- The confirmation round on the draft-2 diff, run a second time after the first round's single finding, returned
  PASS (`manage-agents/scope-p3ver2.final.md`). That PASS opens SC-1a and SC-3a.
- Later drafts change no statement this item builds. Plan draft 5 and spec draft 4 changed no Lean block, and the
  phase-2 fix `5c5faba50` left every Lean block byte-identical.
- DRI-DECISIONS-PHASE2 "Scope", SC1 to SC3: none of them changes SC-1a.
- No new confirmation round was run.

Built text against the approved text: [statement-diff.txt](statement-diff.txt) compares every declaration this item
builds with spec 4.1, 4.2 and 5.1, ignoring whitespace and doc comments, and theorems up to `:=`. **20 of 20 are
exact**: `Unit`, the 17 definitions of 4.1's list part, `listRun_iff` and `listRun_ok_iff`. The four helper
theorems (`continues_iff`, `mem_runFrom`, `indexOf_iff`, `listRun_ok`) are not in the spec. The other 88 approved
declarations belong to sc-1ab, sc-1ac or SC-3a (the next table).

## Plan rows

| Plan SC-1a row | Status | Where |
|---|---|---|
| `lean/VE/Layout/List.lean`: `Unit`, `ofSource` with `paraCounts`, `listRun`, `GovernedItem` | delivered | `b2dd5747f`. `listRun_iff` and `listRun_ok_iff` are proved, with the helpers above |
| `lean/VE/Scope/Examples.lean` | delivered for the layout fixtures | L1, L1-p, F1, F1‴, F2, F2′, F2″ (next table) |
| `lean/VE/Scope/Theorems.lean`: `mergeParts_keys`, `mergeParts_conflict`, `substOwn_no_own`, `substOwn_id` (plus `commutes_symm`, spec 5.1) | **sc-1ab** (size rule, R16) | Proved on `wip/sc-1ab-own` = `b8a4e5255`, in `lean/VE/Scope/{Effects,Theorems}.lean`. `commutes_symm` and `Commutes` are at `b2dd5747f`. Removed from this branch in `65757f4f9`, `7eedac042` and `8571ce1a9` |
| `lean/VE/Scope/{Wire,Govern}.lean`: `SDoc`, the reaches, `admitBlock`, `govern`, the run path `governFast` with `governFast_eq`, `itemRule_decoder`, `govern_identity`, `govern_orphan`, `govern_admits`, `govern_preserves`, `govern_provenance`, `governorsOf_iff`, `decodeNorm_name`, `govern_strings`, `govern_no_new_symbols`, `frontier_graph_refused`, `readings_refused`, `nonrule_refused` | **sc-1ac** | not started |
| `lean/SCOPE.md` | delivered, for this item's files | `6152c97b8`, updated in `8571ce1a9` |
| `lean/VE.lean`: imports | delivered | two imports (`VE.Layout.List`, `VE.Scope.Examples`), a `[union]` file |
| `lean/VE/Audit.lean`: one `#print axioms` per theorem | regenerated | `lean/audit.py --write` through `tools/regen_generated.py --write`: 13 lines |
| `tools/layer_policy.py`: `VE.Layout.*` and `VE.Scope.*` in the profiles layer | **not needed** | `lean_layer` already maps every `VE.*` module that no earlier rule names to layer 2, profiles. So this item does not touch the file that `feature/ap-2` and `lean-first/b18` also edit |
| `tests/test_scope_lean.py` | delivered | R16's "exercised" condition and the ties (Tests) |
| Exit: `lake build`; the audit; `Examples` by `decide`; one seeded Lean bug per theorem family | delivered, with one deviation | Kernel `decide` takes about 5 minutes on the pilot excerpts. So the excerpts are `#guard`s, and the same contracts are kernel theorems on short layouts that cover every field (deviation 2) |

Spec 7.1 fixtures:

| Fixture | Status | Where (`lean/VE/Scope/Examples.lean`) |
|---|---|---|
| L1 | delivered | `#guard`, the layout of u0164.s01–u0166.s01. Kernel: `short_layout`, `of_source` |
| L1-p | delivered | `para_counts` (kernel, on the synthetic layout with tab, CR and space-only blank lines) and a `#guard` over the three pilot layouts |
| F1, F1‴ | delivered | `#guard`s. Kernel: `short_run` |
| F2, F2′ | delivered | `#guard`s: the run, the mid-line continuations and the depth-1 sub-bullets |
| F2″ | delivered, plus one case | `#guard`s and `short_run`: prose after a lead-in, `u0164.s01`, an unknown unit, and a unit that does not end with ":" but is followed by an item (`u0165.s01`, `a.s04`), which the second seeded-bug pass showed nothing covered |
| F1-m, F1′, F-own (and F7-t, an SC-2 row) | **sc-1ab** | built and passing on `wip/sc-1ab-own` (F7-t at `b2dd5747f`) |
| F1″, F-id, F-orph, F-meta, F-sym, F-fg, F-mm, F-2f, F-rs, F-nr, F-pend, F-go | **sc-1ac** | need `govern` |

## Deviations

1. **The cut.** The full SC-1a batch, as first built (`b2dd5747f`), measured 254 unclassified lines (172 trusted
   once classified), over R16's 150. The order table went first, at +132. At +93 the item was still about 780
   hand-written lines, against the feed's ~600, so `VE.Scope.Effects` moved as a whole. What remains is one file
   and one contract, the list run. The rest is named as sc-1ab and sc-1ac in Next items.
2. **Fixture form.** Spec 7.1 says "`Examples.lean` by `decide`/`rfl`". Kernel `decide` on the three pilot excerpts
   took 5 min 7 s per build (measured), so the pilot excerpts are `#guard`s. Each definition is still stated about by
   a kernel theorem on a short layout: `short_layout` covers `item`, `midLine`, `lead`, `label` and `para`, a mid-line
   lead-in, labels, a continuation, a sub-bullet, odd indentation, a numbered item and a new paragraph. The others
   are `short_run`, `of_source`, `markers`, `bold_labels`, `byte_tests` and `para_counts`.
3. **A finding for sc-1ab, not built here.** The approved `mergeParts_keys` (spec 5.1) is false of spec 4.2's text
   of `mergeParts`:
   - `Json.obj` holds a raw `Std.TreeMap.Raw`, so an out-of-order tree can list a key in `VE.Bridge.fields` that
     `getObjVal?` does not find. The spec's text then copies that key into the joined object.
   - A mechanised counterfixture shows this: `unordered_join`, by `decide +kernel`, on `wip/sc-1ab-own`.
   - The repair built there keeps the theorem statement verbatim and has `mergeParts` read members through `lookups`.
     On every well-formed object that is the spec's text (a `#guard` checks it). With it, `mergeParts_keys` and
     `mergeParts_conflict` are proved for every JSON value.
   - It is a definition change, recorded in manage-agents FOLLOW-UPS.md under "## sc-1a" for sc-1ab and the spec's
     next revision. sc-1a builds no `mergeParts`, so this item needs no ruling on it.
4. **Generated Audit lines removed by hand, then regenerated.** Each cut removed theorems that the generated
   `lean/VE/Audit.lean` still named. `lean_statements.py` builds `VE.Audit`, so no generator could run. I deleted
   exactly those `#print axioms` lines and then ran `tools/regen_generated.py --write`, which rewrote the file. The
   committed file is the generator's output, and `regen_generated.py --check` passes (31 entries).

## Size

The rule is about 600 changed lines outside generated files. This item is **+531 lines** of hand-written code
(`git diff --numstat main...HEAD`):
- Lean 419: `lean/VE/Layout/List.lean` 256 (definitions about 105, proofs about 150), `lean/VE/Scope/Examples.lean`
  161, `lean/VE.lean` 2.
- `tests/test_scope_lean.py` 53.
- `tools/trust-classes.json` 59.

Docs come on top: the two verbatim copies, `lean/SCOPE.md` (46) and this directory. `docs/trust-baseline.json` is
the allowance ledger.

## Overlap check (hand-written files against branches in flight)

Files this item edits by hand:
- `lean/VE.lean`;
- `tools/trust-classes.json`, `docs/trust-baseline.json`;
- the new `lean/VE/Layout/List.lean`, `lean/VE/Scope/Examples.lean`, `lean/SCOPE.md`, `tests/test_scope_lean.py`,
  `docs/spec/scope*.md` and `docs/scope/sc-1a/*`.

I compared them with `git diff --name-only main...<b>` for every `lean-first/*`, `feature/*`, `infra/*` and
`foundation/*` branch:
- No branch touches `lean/VE/Layout/`, `lean/VE/Scope/`, `lean/SCOPE.md`, the scope spec or `tests/test_scope*`.
- `lean/VE.lean` is also edited by `feature/ap-2`, `feature/et-7`, `feature/pk-1`, `foundation/me-1` and
  `lean-first/b18`. It is a `[union]` import list, and the plan lists it as shared.
- `tools/layer_policy.py` (edited by `feature/ap-2` and `lean-first/b18`) is not touched (plan rows).
- `lean/VE/Audit.lean` and the other inventories are generated (R12). The two JSON ledgers merge through the
  `ve-generated` driver.

## Seeded bugs (Lean; [mutants.json](mutants.json))

Each mutant was applied to the committed source and built with `lake build VE.Scope.Examples`, then the source was
restored; the tree was clean afterwards and the library was rebuilt. Each one also ran a second way: the mutated
definitions were compiled with the fixtures in a scratch file (never committed) without `List.lean`'s proofs, so the
fixtures run. An unmutated control raised no error there.

| # | Mutant (claimed behaviour) | File | Fails (build) | Fails (fixtures, proofs bypassed) |
|---|---|---|---|---|
| 1 | the run governs items of depth at least `d` (only depth `d` is governed) | `lean/VE/Layout/List.lean` | `mem_runFrom` (List.lean:113) | F2′ `#guard` (`u0072.s02`), `short_run` |
| 2 | `continues` ignores `midLine` (a mid-line continuation keeps the run going) | `lean/VE/Layout/List.lean` | `continues_iff` (List.lean:108) | F2 and F2′ `#guard`s, `short_run` |
| 3 | `listRun` accepts a unit not ending with ":" (a lead-in must end with ":") | `lean/VE/Layout/List.lean` | `listRun_ok` (List.lean:184) | the F2″ `#guard` on `u0165.s01`, `short_run` |
| 4 | an odd indentation makes an item | `lean/VE/Layout/List.lean` | `short_layout` (Examples.lean:107) | `short_layout`, `short_run` |
| 5 | `paraCounts` counts every newline (para counts blank lines) | `lean/VE/Layout/List.lean` | the L1 `#guard` (Examples.lean:64) | L1, `short_layout`, `of_source`, `para_counts`, L1-p |
| 6 | a marker without its space (`*x` is not an item) | `lean/VE/Layout/List.lean` | `markers` (Examples.lean:125) | `markers` |

Mutant 3's second column is new. On the first pass, no fixture had a unit without ":" that an item follows, and only
the proof caught it. `8571ce1a9` adds that case to `short_run` and to the pilot `#guard`s. No Python or Rust product
code changed. The sc-1ab code on `wip/sc-1ab-own` had its own seeded bugs (`ScopeConflict` turned into an override,
`lookups` read as `fields`, `substOwn` skipping objects, `ownSafe` ignoring `exists`). Each failed a proof or fixture
(commit `7130d01d6`'s `mutants.json`), and sc-1ab reports them.

## Trust

Measured on this HEAD with `uv run python tools/trust_map.py --check` against `c7fc6acac`: **PASS**.

| | Lines |
|---|---|
| K | +0 |
| S | +17 (`Unit`, `GovernedItem`) |
| D[V] untied | +62 (`ofSource`, `paraCounts`, `lineStart`, `spacesOnly`, `skipSpaces`, `markerLen`, `lastNonBlank`, `boldLabel`, `isBlank`, `isDigit`, `sp`, `nl`) |
| D[V] tied | +21, not trusted (`continues`, `indexOf`, `runFrom`, `listRun`, tied by `continues_iff`, `indexOf_iff`, `mem_runFrom`, `listRun_iff`/`listRun_ok_iff`) |
| trusted | **+79**, all in `lean/VE/Layout/List.lean` |

- The growth is recorded with `--allow` as S +17 and V +62, `SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-1a,
  2026-10-18`.
- `lean/VE/Scope/Examples.lean` is T.
- Every new trusted definition is stated about by a theorem that can fail
  (`tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem`, and the seeded bugs).
- The ties-pass row is in manage-agents FOLLOW-UPS.md under "## sc-1a (2026-10-18)".

## Tests

- **Selected tests**, `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on ve-mac-1 at
  `8571ce1a` (clean): 72 units, exit 0, 0 failed. Earlier, the same selection at the wider cut (74 units, VM) also
  passed in full.
- **The new test file**, `tests/test_scope_lean.py`, 4 tests:
  - `test_the_scope_files_are_classified`;
  - `test_every_trusted_scope_definition_is_used_by_a_theorem`. It caught a real gap during the build: no theorem
    named `ofSource` directly. `of_source` fixes that;
  - `test_each_tie_names_a_theorem_about_its_definition`;
  - `test_a_definition_no_theorem_uses_is_reported`, which shows the check can fail.
- **Lean**:
  - `lake build`: 989 jobs, no error. Every `#guard` and kernel fixture holds.
  - `python3 lean/audit.py`: PASS, 549 files, 6,304 theorems, only the standard axioms.
- **Generated files**: `uv run python tools/regen_generated.py --check`: 31 entries checked, all current.
- **Gate collection**: `uv run python tools/gate_collection.py --check --prebuilt`: 17,326 collected, 4 added, 0
  removed, 0 refused, 0 stale, 0 malformed. No test was removed, so no `Test-removed` trailer is needed.
- **Repository map**: `uv run python tools/repo_map.py --check`: PASS. No mode was added.
- **Full gate**: not run by me, as the task says. The chain runs it on the final HEAD.
- **Known red**: none of `main-known-red.txt`'s tests failed in the selected run.

## Pilot bytes (estimate)

0 B in both pilots. SC-1a is Lean core only: plan 0, "SC-1a | 0", "Bytes. 0 (no route yet)". No route calls the
layout. The first number moves at SC-1b, an estimated +22 B OPEN on the constitution (u0164.s02's lead-in, C12),
once sc-1ab, sc-1ac and SC-1b's document mode are in. Nothing is claimed before a pilot audit.

## Next items

- **sc-1ab**: `lean/VE/Scope/Effects.lean`, the effects on a rule's JSON object, built on `wip/sc-1ab-own` =
  `b8a4e5255` (with `Theorems.lean` and the F1-m, F1′ and F-own fixtures):
  - `lookups` and `mergeParts`, with `mergeParts_keys`, `mergeParts_conflict` and the counterfixture
    `unordered_join` (about +14 trusted lines). The DRI may want to see the definition change (deviation 3);
  - `depthLimit`, `members`, `hasOwn`, `depthOk`, `ownSafe` and `substOwn`, with `substOwn_no_own` and `substOwn_id`
    (about +39);
  - `Effect`, `narrowing` and `Commutes`, with `commutes_symm` and F7-t (about +21; text at `b2dd5747f`).
  Its own R16 row would come to about +74.
- **sc-1ac**: `Reach`, `Governor`, `SDoc`, `applyEffect`, `itemRule`, the reaches, `admitBlock`, `govern`, the run
  path `governFast`, the rest of spec 5.1's theorems, and 7.1's `govern` fixtures. It likely needs its own cut to
  stay within R16 and the size rule, unless `governorsOf` is tied by `governorsOf_iff` and `admitBlock` is G[R].
- **SC-1b** follows after ar-10a and lf-16g, as the feed says. It needs sc-1ab and sc-1ac.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no relayed Lean answer and no response field is added; no route or
   service change.
2. **Every required deliverable built.** PASS, with the plan rows above. The cuts to sc-1ab and sc-1ac follow the
   feed's size rule and R16, and are named. There is no Python copy of a Lean decision and no new report test. The
   only hand-written file shared with an in-flight branch is the `[union]` `VE.lean`. Probe:
   `git diff --name-only main...HEAD`.
3. **Tests and gates can fail.** PASS: six seeded Lean mutants, each failing a proof and, with the proofs bypassed, a
   fixture (`mutants.json`, with an unmutated control). The R16 check's own can-fail test is
   `tests/test_scope_lean.py::test_a_definition_no_theorem_uses_is_reported`.
4. **Python, Lean and Rust agree; valid inputs still pass.** N.A.: there is only a Lean implementation of the layout,
   and no Python or Rust copy exists or is added. The pilot excerpts are valid inputs and pass: the L1, F1, F2 and
   F2′ `#guard`s.
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I can take it. The tree is committed and clean, and the
   chain runs the full gate on the final HEAD. Evidence commit list below, from `git log --no-merges main..HEAD`.
7. **No unsigned item.** PASS: the one DELTA row cites R16, with its conditions met (79 <= 150, K +0, itemised,
   exercised, FOLLOW-UPS row). Probe: `python3 review-ready.py --delta-dri-needed`: "No DELTA row reserved for the
   DRI"; review-ready's `[delta]` passes.
8. **Every user-visible change in DELTA.** PASS: DELTA.md lists the trust row and why nothing else is a delta. No
   existing file changes behaviour; the selected run passes unchanged.
9. **Test selection finds the tests.** PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 72 of
   436 units, including `tests/test_scope_lean.py`, plus `lake build` and the audit, which run every seeded bug's
   failing check.
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` shows 20 of 20 exact. No hypothesis is
    added. Mutants 1 to 3 break `mem_runFrom`, `continues_iff` and `listRun_ok`, which `listRun_iff` and
    `listRun_ok_iff` rest on.
11. **Budgets fail closed.** N.A.: no budget, limit or deadline is added (spec 8.2's limits are sc-1ac's
    `admitBlock`).
12. **No CPU or memory regression.** N.A. for the pilots: no route calls the new code. The build cost is measured:
    the kernel fixtures take about 10 s. The 5-minute variant was not kept (deviation 2).
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt` shows 0 refused, 0 stale and 0
    malformed. No test was removed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
8571ce1a9 sc-1a: cut to the layout's list runs (size rule); Effects moves to sc-1ab; boundary fixture for NotALeadIn
7eedac042 sc-1a: cut conditions and own to sc-1ab (size rule); re-measure trust (+93, R16) and redo evidence
b8a4e5255 sc-1a: R16 trust allowance (S +62, V +70, K +0) and DELTA
7130d01d6 sc-1a: saved statement diff and seeded-bug record (9 Lean mutants, each fails a proof or fixture)
6152c97b8 sc-1a: scope plan and spec copied verbatim from 5c5faba50; statement gate record; lean/SCOPE.md
5e5a8a051 sc-1a: R16 exercised check for the scope files, of_source fixture, assurance manifest entries
65757f4f9 sc-1a: cut the order table to sc-1ab (R16 limit); mergeParts reads members by lookup; trust classes; regenerate
b2dd5747f sc-1a: scope@0 layout (list runs) and effects core in Lean, with theorems and fixtures
```
