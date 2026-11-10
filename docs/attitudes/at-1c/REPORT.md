# at-1c report: the attitudes Lean core, part three (spec 2.7-2.9, seven statements of 6.1)

Status: done; deliverables (1)-(5) built, the seven statements proved (six new, `table_reviewed` at-1a's); selected tests passed; the chain gates this final HEAD.
Changed: new `Frame.lean` (2.7), `Semantics.lean` (2.8), `Route.lean` (2.9's first block); `Theorems.lean` gains six proofs; `Examples.lean` gains 7.2-7.5's guards and examples.
Signatures: none reserved. One added line, `labelOrigin`'s stand-in, SIGNED by the DRI (reviews/dri-decisions-20261108-at-1c.md item 1). Trust +109 (K +0) by standing ruling R16.
Open: size over the 700-900 estimate (section "Size": 1,075 hand-written lines before this report; the overrun is the proofs' helper lemmas). Row at-1a-tie is now complete (section "Trust").
Next item: at-1 (the other fifteen statements of 6.1, and at-1b-tie's move of `AFormula.toFormula`), then at-2 and at-3a.

Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core". Spec: docs/spec/attitudes.md (draft 8) 2.7-2.9, 6.1, 7.2-7.5. Statement gate: AT-0 is
done (reviews/dri-decisions-20261103-fp-attitudes-r2.md item 3). DRI decision files named here are in manage-agents/reviews/.

## Deliverables

| Task line | Delivered | Commit | Test or check |
|---|---|---|---|
| (1) spec 2.7 in `Frame.lean`, verbatim; guards on F-AT2 (labels, premise count) and F-AT6 (the pairs) | the ten definitions; guards on F-AT1 (labels, premises as written), F-AT2, F-AT3, F-AT6, F-AT7, F-AT0, F-AT5, C-a, `knows → believes`, each branch of `entailsMode` and `sameSubject` | 89a796082 | `Examples.lean` section "2.7"; `spec_text_check.py` |
| (2) spec 2.8 in `Semantics.lean`, verbatim; 7.2's points as guards where decidable | `AttModel`, `contentAt`, `Intended`, `AFormula.denote`, `interp`, `restrict`, `seedClosure`. 7.2's decidable columns as `#guard`s: "frame holds" (M1-M4: true, false, false, true) and "guard on `interp`" (true, true, false, false), on finite models. The Prop columns ("Intended", "guard under the attitude semantics") are `example`s on the same points: M1, M4 intended, M2, M3 not; the guard true at M1, M2, false at M3, M4 | 55e0a4702, b65b6d0c2 | sections "2.8" and "2.8 and 2.9's propositions" |
| (3) spec 2.9 in one more module; 7.3's guards computable without AT-2 | `Route.lean`, the module spec 6.2 names for AT-2's statements (it imports `VE.NormDefaults.Layered`; `Semantics.lean` stays light for at-1); ATTITUDES.md says so. `toU`, `SettledAsX`, `UnsaidFree`, `attitudesPack`, `attitudesRow`, and AT-2's stand-in `labelOrigin` (signed, below). Guards: `toU`/`WellFormedU` on U1; RM1-RM4's first failing labels; `table3` and `enumerateSettled` at RM1, RM4; the frame unsaid-free and typed over `envAt (fill U1) 0` and `baseEnvAtt`; F-AT8; RM4's two fillings; PK-1 as built; `attitudesPack_premises` (F-AT1, F-AT2); `assemble` (ok, and drafts 1-4's pack refused with its text); the names in U1's base; `envX` by `rfl`; `attitudesRow`'s fields and `slotAgrees`. Size measured here: 288 lines | 55e0a4702 | section "2.9"; "Size" |
| (4) the seven statements, proved; 7.5's guard per theorem; 7.4's both directions | `frame_wellFormed`, `frame_universalQF`, `frameLabels_nodup`, `framePairs_modes`, `framePairs_transitive`, `empty_relations_frame` in `Theorems.lean`; `table_reviewed` stays at-1a's in `Scale.lean` (DRI FYI, decision item 2; its 7.5 guard is at-1a's, `Examples.lean` section 2.1). 7.5: one guard per theorem (F-AT2, F-AT6 and the every-mode document, F-AT1/F-AT2). None of the seven is an iff; 7.4's rows that touch 2.7 are guarded both ways: premise 3 (F-AT7 with and without the item), premise 4 (F-AT3 with, without, reversed) | b65b6d0c2 | `python3 lean/audit.py` PASS; section "Runs" |
| (5) at-1a-tie's second half | `baseEnvAtt` S to D[V], tied to `frame_wellFormed` | 54e761444 | section "Trust" |
| Generated files (R12) | `regen_generated.py --write` (`wrote 34 entries`); `lean/VE.lean` unchanged (the new modules are reached through `Examples.lean` and `Theorems.lean`) | 54e761444, af841eb32 | `regen_generated.py --check --skip route-cases`: `checked 34 entries` |
| R16 record, FOLLOW-UPS row "## at-1c" | DELTA row 1; `trust_map.py --allow` with R16's signature; the row | 21bd1a5ed, af841eb32 | `trust_map.py --check`: PASS |

Not delivered: nothing. The seam before (4) was not used (288 lines after (3)). Kept out on purpose: `lean/VE/NormDefaults/Packs.lean`
(`pointCheck`, `OriginsExact`, `packEntry`, `furtherEntries`: AT-2), `lean/VE/Compose/Dispatch.lean` (`attitudesRow` is defined, not
registered: AT-3a), `tools/layer_policy.py` (`VE.Attitudes.*` is layer 3 already; `check_lean_imports.py` keeps the graph). Branch overlap:
no in-flight `lean-first/*`, `feature/*`, `infra/*`, `foundation/*` branch touches `lean/VE/Attitudes` or `lean/ATTITUDES.md`; several touch
`tools/trust-classes.json` and `lean/VE.lean`, which are union-merged side tables (my edits add the at-1c modules' entries only).

## Signed differences from the spec

One added line, no changed spec line. `spec_text_check.py` allows exactly this string once.

1. **`labelOrigin`:** `def labelOrigin (_A : AttDoc) (_l : String) : VE.NormDefaults.Packs.RequestPath := []`, beside `attitudesPack`, which reads
   it. SIGNED, reviews/dri-decisions-20261108-at-1c.md item 1. Spec section 0 lists `labelOrigin` as AT-2's stand-in, and the stub declares it
   `opaque`, which `lean/audit.py` refuses. Its conditions are met: class S; (a) `#guard labelOriginStandInUnread` (`Examples.lean`) fails if a
   profile row for `attitudes@0` or a layered kind needing the pack appears while every origin is the root (probe: its condition
   with `profileTable ++ [attitudesRow]` evaluates to `false`); (b) a guard pins each origin
   to `[]` and the origins' keys to `frameLabels A`; (c) the decider put the replacement on row at-2's note. The PK-1-as-built guard and the
   `consts` seeded bug's guard stay selected (`lake build VE.Attitudes.Examples`).

## Spec re-read

- `python3 docs/attitudes/at-1c/spec_text_check.py`: `25 pieces, 0 missing, 1 signed addition, 7 of 7 statements`, rc 0. It reads every
  declaration of 2.7, 2.8 and 2.9's first block (2.9's `pointCheck` block is skipped and refused if read) and the seven statements. Opposite
  direction, each by editing and restoring: `entailsMode` without `w != w2 &&` gives `1 missing`; `framePairs_transitive` without `(hne : k1 ≠
  k3)` gives `1 missing`.
- 2.9's text: `toU`, `SettledAsX`, `UnsaidFree` and the three `open` lines are in `Route.lean` as written, imports added only.
- 7.1's F-AT1, F-AT2, F-AT3, F-AT5, F-AT6, F-AT7 and F-AT0 frame values, 7.2's table and 7.3's RM1-RM4 columns computable without AT-2: each
  is a guard with the spec's value (sections 2.7-2.9 of `Examples.lean`). `table3`/`enumerateSettled` at RM1 is `some false`, at RM4 `none`, as
  7.3 says.
- 7.3's row "the frame reads no unsaid table on U and is typed over `envAt (fill U) 0` and `baseEnvAtt`": guarded.

## Seeded bugs and mutants

Each bug was planted, `lake build VE.Attitudes.Examples VE.Attitudes.Theorems` run, the file restored. `docs/attitudes/at-1c/mutants.json` has
all 27 with every failing check (Examples.lean line numbers as of 22199aa9a). Only Lean product code changed: no Python, no Rust.

| Bug (task) | File | Failing check |
|---|---|---|
| `framePairs` with a pair starting at `believes` (`entailsMode` gains `.act .believes, .thinks _ => true`) | `lean/VE/Attitudes/Frame.lean` | `framePairs_modes`'s 7.5 guard (every-mode document `fatAll`), `entailsMode`'s branch guard; the proof `framePairs_modes` |
| `framePairs` without `thinks w → thinks w2` | `Frame.lean` | `framePairs_transitive`'s 7.5 guard (F-AT6's instance), F-AT6's and F-AT3's pair guards |
| `frameLabels` repeating a label (every factive label the same) | `Frame.lean` | F-AT2's nodup guard, F-AT1's labels; the proof `frameLabels_nodup` |
| `attitudesPack` with a non-empty `consts` | `lean/VE/Attitudes/Route.lean` | 2.9's PK-1-as-built guard; `assemble`'s guard; `envX`'s `rfl` |

One mutant per new trusted definition (common rules), each failing at least one `#guard` or example: `sameSubject` (no content test),
`framePairs` (pairs reversed), `closeOver` (binders swapped), `atomAt` (arguments swapped), `knowsKeys` (negated), `factive` and `entails`
(converse), `framePremises` (no pairs), `AttModel` (`J` into `Bool`: refused), `contentAt` (slot unbound), `Intended` (no factivity),
`AFormula.denote` (`or` as `and`), `interp` (ignores `J`), `restrict` (keeps the names), `seedClosure` (any tuple), `toU` (drops `unspec`),
`SettledAsX` (flipped), `UnsaidFree` (vacuous), `attitudesRow` (drafts 1-4's `requires`), `labelOrigin` (not the root), `baseEnvAtt` (sorts
reversed). Proofs say what they claim: `checkCond` without its quantifier check breaks `frame_universalQF`'s helper (`checkCond_key`), and
`checkNames` without its `:` check breaks `frameLabels_nodup`'s helper (`checkNames_colon`); both also fail an at-1b guard.

The sweep: `docs/attitudes/at-1c/trust-mutants.json`, head af841eb32 (the final Lean): 244 mutants, 140 KILLED, 0 SURVIVOR, 0 UNKNOWN, 14
INVALID, 90 ALLOWED, 0 NOT RUN, exit 0. Kills by definition: `framePairs` 26, `framePremises` 26, `frameLabels` 24, `attitudesPack` 20,
`entailsMode` 14, `knowsKeys` 11, `attitudesRow` 8, `sameSubject` 7, `atomAt` 4. The tool writes no mutant for `factive`, `entails`, `interp` or
`labelOrigin`; each has a hand mutant above. The 90 ALLOWED, by `raw_status`: 66 SURVIVOR of Prop definitions (`AFormula.denote` 36,
`contentAt` 13, `Intended` 6, `SettledAsX` 5, `restrict` 3, `seedClosure` 3). Each breaks a named example that pins its definition both ways
on F-AT1's points, as for at-1b's `AWellFormed`. The other 24 are UNKNOWN: 22 mutants Lean refuses to elaborate, and 2 of `UnsaidFree`,
which the guards decide through `instDecidableUnsaidFree` (the probe does not count that instance; both guards fail). The first sweep
(22199aa9a) left 69 SURVIVOR. Of those, 3 were killable: `framePairs`' inner `drop 1` and `entailsMode`'s `take 1`/`dropLast` of
`knowsThinks`. The guards in a4fa2e74a kill them (a pair onto the document's first key; premise 3 from a table's last item). The same commit's
examples give every other survivor a named proof it breaks (each connective of `AFormula.denote`, closed conditions, `contentAt`'s other
lengths).

Commands: `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/attitudes/at-1c/trust-mutants-allow.json --rescore …
--json docs/attitudes/at-1c/trust-mutants.json`: exit 0 (on the VM, a full run because `Route.lean` changed; 7,519 s).

## Trust

`uv run python tools/trust_map.py --check`, PASS: `K +0, S +87, D +7, G +22, tied +7, unclassified +0, trusted +109`;
`Semantics.lean` +41, `Frame.lean` +39, `Route.lean` +36, `Syntax.lean` -7. Classes: S for the 2.7-2.8 definitions and `SettledAsX`,
`UnsaidFree`, `labelOrigin` (the decision's class); G[V] for `toU`, `attitudesPack`, `attitudesRow`, as `softPack`, `rightsPack` and
`profileTable` are; fixtures T; theorems P. Within R16 (at most 150, no K); DELTA row 1 itemises it; FOLLOW-UPS.md row "## at-1c".

**Row at-1a-tie, measured (second half).** `baseEnvAtt`, 7 lines, moved from S to D[V] tied to `frame_wellFormed`, whose statement uses it
with `framePremises` (S) as the other anchor: `D +7, tied +7`, `Syntax.lean` trusted -7. With at-1b's -15, at-1a-tie is complete (-22).
No docstring trimmed, no line joined, nothing else reclassified.

## Size

`git diff --numstat $(git merge-base HEAD main)`, without generated files and the tool-written `trust-mutants.json` and `docs/trust-baseline.json`:

| Kind | Lines |
|---|---|
| Spec Lean, verbatim, plus the signed line | `Frame.lean` 49, `Semantics.lean` 54, `Route.lean` 53 (156; spec text about 120, the rest imports, module docs and the stand-in) |
| Statements and proofs | `Theorems.lean` 378: the six statements with docstrings about 40, their proofs about 140, helper lemmas about 200 (extracting each key's checked facts from `checkAtt`, typing over `baseEnvAtt`, weakening, distinct labels from `checkNames`' `:` check) |
| Guards and fixtures | `Examples.lean` 305: 2.7 54, 2.8 19, 2.9 71, 7.5 26, the Prop examples 128 (about 45 of them the sweep's fixtures), imports 3 |
| Evidence | `mutants.json` 29, `trust-mutants-allow.json` 52, `spec_text_check.py` 55 |
| Docs and side tables | `ATTITUDES.md` 11, `DELTA.md` 16, `tools/trust-classes.json` 73, this report |

Measured after (3), as the task asks: 288 lines (55e0a4702: `Examples.lean` 133, `Frame.lean` 49, `Route.lean` 52, `Semantics.lean` 54), well
under ~900, so (4) stayed. The total, 1,075 before this report, is over the 700-900 estimate. The guards came in at the estimate (250-350).
The statements' proofs did not: the estimate counted about 60 statement lines. No guard, docstring or proof was trimmed.

## Pilot bytes

None expected: a structure row (bytes 0). No route, verdict or wording changes (DELTA), so nothing is claimed.

## Runs

- `lake build` (full) on the final Lean: `Build completed successfully (1317 jobs)`. `python3 lean/audit.py`: `PASS: 786 source files; 8709 named
  theorem declarations audited`. `#print axioms`: the six use only `propext`, `Quot.sound` and (four of them) `Classical.choice`.
- `python3 tools/check_lean_imports.py`: `Lean layer graph kept (786 modules, 22 reviewed legacy edges)`.
- `zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on a500c713d: 5 shards, 19 units, 19 passed, exit 0
  (`tests/test_trust_mutants.py` chunked: 141 passed). Not rerun; later commits are this report only.
- `regen_generated.py --write` stopped at `route-cases` (no Rust release binary here: `CheckerUnavailable: missing Rust executable`), so it ran
  with `--skip route-cases`: `wrote 34 entries`. No route case reads `VE.Attitudes`, and the final `--check --skip route-cases` gives `checked 34
  entries`. The chain's gate checks `route-cases` with its binary.
- `grep -rln VE.Attitudes lean/VE/Service lean/VE/Route lean/Main.lean ve/`: no file, so no route reads these modules.
- Not run here: the full gate (the chain runs it). No test in main-known-red.txt was touched.
- The `decide +kernel` examples avoid degree keys' names: the kernel does not reduce `String.map` (in `Mode.slug` for `thinks`). So `interp` and
  `restrict` are pinned on F-AT9 (one `knows` key); the frame's guards cover the degree names by `#guard`.

FOLLOW-UP: none new. at-1a-tie is complete here; at-1b-tie stays with at-1.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no service mode, schema or relay changes (grep in "Runs").
2. PASS: "Deliverables" gives each task line with its commit and check; no Python copy of a Lean decision, no report test (`git diff --stat`: no `tests/`, `ve/` or `tools/*.py` file).
3. PASS: `mutants.json` (27, each failing a named guard or example); `trust-mutants.json` 0 SURVIVOR, 0 UNKNOWN, allow reasons one per (definition, operator) pair, each naming the proof broken or Lean's refusal.
4. N.A.: Lean only, read by no route; no Python or Rust product code changed.
5. N.A.: no relayed field.
6. N.A. here: the chain gates the final HEAD. `trust-mutants.json` names af841eb32, whose Lean equals this HEAD's (`git diff af841eb32 HEAD -- lean` empty); later commits are evidence and this report.
7. PASS: the one spec deviation is signed by the DRI's decision file; DELTA row 1 cites R16 with its evidence; no cell reserves a signature.
8. PASS: no user-visible output changes; DELTA says so, with the grep.
9. PASS: the selection ran `lake build` of the changed modules' checks and `tests/test_trust_mutants.py`; 19 units passed.
10. PASS: the `thm-*` rows of `mutants.json` show the proofs depend on `checkAtt`'s checks; `spec_text_check.py` checks every statement verbatim and fails on a weakened one.
11. N.A.: no evaluator, budget or deadline; nothing runs these definitions on a route.
12. N.A.: no runtime path changes.
13. PASS: no test removed or renamed.
14. PASS: both directions: frame holds and fails (M1-M4, RM1-RM4), premise 3 and 4 with and without, `Intended` and the guard true and false, `seedClosure` reaching and not, `spec_text_check.py` passing and failing. Each claim names its command.
15. PASS, the four classes. Overclaim: "no route reads" rests on the grep; "verbatim" on `spec_text_check.py`, with its one signed addition named. No silent cut: every deliverable built; the size overrun is reported with its cause. Every check can fail: `mutants.json`, `trust-mutants.json`. Limits before work: N.A., no evaluator.
