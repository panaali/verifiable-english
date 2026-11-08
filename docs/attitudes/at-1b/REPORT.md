# at-1b report: the attitudes Lean core, part two (spec 2.5, 2.6, five statements of 6.1)

Status: done; deliverables (1)-(4) built, the five statements proved; selected tests passed after one fix; the chain gates this final HEAD.
Changed: `Syntax.lean` gains 2.5-2.6 verbatim but for two DRI-signed lines; new `Theorems.lean`; `Examples.lean` gains one guard per row of 5.2.
Signatures: none reserved; S +165 (K +0) SIGNED by the DRI (reviews/dri-decisions-20261105-at-1b-trust.md item 1). No DELTA row is reserved.
Open: cut-back rows `at-1b-tie` (filed by the DRI) and `at-1a-tie` (first half done, 7 lines short, section "Trust"); size over the guide, ruled on (section "Size").
Next item: at-1 (spec 2.7-2.9 and the rest of 6.1, with at-1a-tie's second half), then at-2 and at-3a.

Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core". Spec: docs/spec/attitudes.md (draft 8). Statement gate: AT-0 is done
(reviews/dri-decisions-20261103-fp-attitudes-r2.md item 3). Two lines had to change; each was stopped on and signed
(section "Signed differences from the spec"). DRI decision files named here are in manage-agents/reviews/.

## Deliverables

| Task line | Delivered | Commit | Test or check |
|---|---|---|---|
| (1) spec 2.5: `atom`, `AFormula.toFormula`, `ARule.toNode`, `toNorms`, `partClaim` | in `Syntax.lean` after 2.4, as lean/ATTITUDES.md says | 9c0e373b2 | Examples.lean:334-:377; `spec_text_check.py` |
| (2) spec 2.6: the 15 definitions named by the task, as the spec writes them | in `Syntax.lean` | 9c0e373b2, 814e0f03f | section "Spec re-read" |
| (2) `#guard`s: one per 5.2 row, each with the spec's text | Examples.lean:457-:493: 25 guards, D1-D18, D0, D6a, D6b, D14a-D14d, in the table's order | 7788c6b96 | `lake build VE.Attitudes.Examples` |
| (2) F-AT1 and F-AT0 elaborate and pass `checkAtt` | elaborate :334, :372; pass :498 | 7788c6b96 | same |
| (2) C-e's part passes `checkParts`; the same node in a guard is refused at D14c; `c_e` in the guards' names | :506, :507 (with the compound part, `c_e_compound`) | 7788c6b96 | same |
| (3) `Theorems.lean`: `names_fresh`, `names_injective`, `keyOf_name`, `envAtt_extends`, `toNorms_wellFormed`, proved | from `checkNames` and the `Nodup` check, by `checkAtt_tail` and `checkNames_mem`, as the spec's proof notes say | 6284ed01d, 1a7f3ef8d | `python3 lean/audit.py`: `PASS: 775 source files; 8604 named theorem declarations audited` |
| (3) 7.5's `#guard` per theorem | Examples.lean:529-:536 | 7788c6b96 | `lake build` |
| (3) 7.4's both directions | none of the five is an iff; 7.4's `checkAtt` row: passes :498-:499, each failing row :457-:493; D14d's row :504 | 7788c6b96 | `lake build` |
| (4) imports and generated files through `regen_generated.py --write` (R12) | `regen_generated: wrote 35 entries`; `lean/VE.lean`'s one import line by hand (no writer); `trust-classes.json` | 8f94b9a55, 7788c6b96 | `regen_generated.py --check` on 4e280e220: `checked 35 entries` |
| Also: at-1a-tie, first half | `keys`, `name`, `keyOf`, `envAtt` to D[V] tied; `baseEnvAtt` stays S (decision -trust item 2) | 7788c6b96 | section "Trust" |
| Seeded bugs; a mutant per new trusted definition; the sweep | section "Seeded bugs and mutants" | 6ce23fdce and later | `mutants.json`, `trust-mutants.json` |
| R16 record, FOLLOW-UPS row "## at-1b" | DELTA row 1; `--allow` with the DRI's signature; row written | 6ce23fdce | `trust_map.py --check`: `PASS` |

Not delivered: nothing. The seam was not used. Kept out on purpose: `lean/VE/Attribution/`, `Frame.lean`, `Semantics.lean`,
`tools/layer_policy.py`. Branch overlap: no other in-flight branch of `lean-first/*`, `feature/*`, `infra/*`, `foundation/*`
changes `lean/VE/Attitudes` or `lean/ATTITUDES.md` against main (loop over `git diff --name-only main...<branch>`, empty).

## Signed differences from the spec

Two, each by exact string in `docs/attitudes/at-1b/spec_text_check.py`. docs/spec/attitudes.md and the stub stay verbatim;
row at-rev2 corrects them.

1. **D14c, both lines of `renderCheck`:** `.bind (fun w => VE.Reports.wantsPhrase? (w.stripPrefix "{0} "))` for `.bind
   VE.Reports.wantsPhrase?`. SIGNED, reviews/dri-decisions-20261105-at-1b.md item 1. The spec's text was right only for the
   stub's stand-in: at-1w's merged function takes the finite phrase and answers `none` on `{0} …`, which would refuse every
   `wants` condition, against spec 7.1's C-c and C-e. It stays closed because `{0} ` first and each hole once are V3 of
   `Lexicon.failures`, and D6a runs before `checkConds` and `checkParts`: `is safe` and `{0} is {0}` are refused at D6a
   (Examples.lean:515). The head rule alone would not do it, since `wantsPhrase?` accepts `is safe`.
2. **`checkNames`:** `n.utf8ByteSize > VE.Limits.maxIdentifierBytes` for the literal `64`. SIGNED,
   reviews/dri-decisions-20261105-at-1b-limit.md item 1. `tests/test_lean_limits.py` requires each non-frozen check to read
   `VE.Limits`. The limit is `abbrev … := 64`. The diagnostic keeps spec 5.2's D17 text (:491) and `names_fresh` keeps its `≤ 64`.

## Spec re-read

- `python3 docs/attitudes/at-1b/spec_text_check.py`: `25 pieces, 0 missing, [2, 1] signed differences, 5 of 5 statements`, rc 0.
  It reads every declaration of attitudes.md 2.5 and 2.6 and the five statements of 6.1. Opposite direction, each by
  editing `Syntax.lean` and restoring it: the literal `64` gives `1 missing`, rc 1; another form of the D14c call
  (`w.drop 4`) gives rc 1.
- `checkAtt`'s order against spec 5.2 (:1227 "D1–D6, D6a, D6b, D7–D9, D10–D14, D14a–D14d, D15–D18"). Examples.lean's guards are in
  that order, and swapping D6 with D6b breaks D6's row (`seed-checkAtt-swap-D6-D6b`).
- C-a, C-b, C-c, C-d, C-e, F-AT0-F-AT3, F-AT5, F-AT9 against spec 7.1. The fixture documents are the stub's S5, copied. Elaborated
  guards: Examples.lean:334 (F-AT1), :501 (F-AT9).
- D5's bound against QS-1 (:523: 54 declared pass, 55 refused). D15's against `VE.Reports.maxPredicates` (:520: 238 pass, 239 refused). D17's against 64 bytes (:675).
- `partClaim` against spec 2.5 (closed; `attitude φ`): Examples.lean:375, :376.
- `AWellFormed` against spec 11 item 6 (a condition outside the document is not well formed): Examples.lean:704, by way of `awf_iff`.

## Seeded bugs and mutants

Each bug was planted in `lean/VE/Attitudes/Syntax.lean`, `lake build VE.Attitudes.Examples VE.Attitudes.Theorems` run, and the file
restored and compared with `cmp`. `docs/attitudes/at-1b/mutants.json` has all 35, each with its first failing guard. Only Lean product code changed.

| Bug | Failing check |
|---|---|
| `checkAtt` with D6 and D6b swapped | Examples.lean:464 (D6's row answers D6b's text) |
| `renderCheck` without D14a's slot mention | :485 (D14a's row, `ca2`) |
| `checkParts` with `part := false` | :506, :507 (`c_e_part`) |
| `toNode` dropping a rule's carve-outs | :361 (`fat1c`, F-AT1 with carve-outs) |
| D14c without `stripPrefix` (DRI condition) | :499 (`cc1`), :506 (`c_e_part`) |
| `checkNames` without its 64-byte check (DRI condition) | :491 (D17's row), and the proof at Theorems.lean:55 |

Proofs say what they claim (item 10): removing `checkNames`, the `Nodup` check or `validate` from `checkAtt` breaks the proofs at
Theorems.lean:40, :40 and :44; `envAtt` losing `E`'s predicates breaks :104; `keyOf` with another search breaks :98.

Per new trusted definition. `docs/attitudes/at-1b/trust-mutants.json`, head b7b7428a6 (Lean identical to 814e0f03f, a rescore of the
allow file's reformat): 479 mutants: 294 KILLED, 0 SURVIVOR, 0 UNKNOWN, 74 INVALID, 111 ALLOWED, 0 NOT RUN, exit 0. Kills by definition:
`checkAtt` 55, `checkCond` 25, `checkNames` 27, `checkParts` 1, `lexAgrees` 75, `lexCovers` 16, `lexPred` 15, `lexTerm` 15, `mentionsSlot` 30,
`renderCheck` 21, `renderable` 2, `WellFormedAtt` 2, `ARule.toNode` 5, `toNorms` 5. The tool kills nothing in `AFormula.toFormula` (its operators
give type errors) and has no mutant for `atom`, `partClaim`, `throwIf` or `checkConds`: those have hand mutants in `mutants.json`, each failing a guard.

The 111 ALLOWED, read from each row's `raw_status`: 82 UNKNOWN, 29 SURVIVOR. The UNKNOWN are mutants Lean refuses to elaborate, and the two
default-argument flips whose probe reads a changed caller (`checkCond-default-part-true`, `renderCheck-default-part-true` fail guards :506, :518).
The SURVIVOR are 27 of `AWellFormed`, a Prop no check evaluates, each breaking the proof `awf_iff` (detail: `the proofs it breaks:
lean/VE/Attitudes/Examples.lean:689`), and 2 equivalents: `.take 1` before `.head?` (Syntax.lean:325) and `n.drop 1` before the colon check
(:309), since a generated name starts with `attitudes__`. The first sweep (8f94b9a55) left 50 SURVIVOR and 164 UNKNOWN; the fixtures in 20cdca576
kill every killable one. 82 of those UNKNOWN came from one guard's inline lambda (D16), now the definition `d16`.

Commands: `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/attitudes/at-1b/trust-mutants-allow.json --rescore … --json
docs/attitudes/at-1b/trust-mutants.json`: exit 0.

## Trust

`uv run python tools/trust_map.py --check`, rc 0: `K +0, S +165, D +15, G +0, tied +15, unclassified +0, trusted +165`; `VE/Attitudes/Syntax.lean` +165.
That is +180 of spec text less the tie move's 15. The bound is S at most +170 with the move made (decision -trust item 1). Classes: S for the 20 new
definitions, as `checkAlt`, `validateAlt` and `checkRisk` are; theorems P; Examples.lean's fixtures T. `review-ready.py --delta-dri-needed`: `no DELTA row reserved for the DRI`.

**Row at-1a-tie, measured.** Moved to D[V] tied: `keys` 3, `name` 4, `keyOf` 2 (each tied to `names_fresh`, `names_injective`, `keyOf_name` as its statement uses it),
`envAtt` 6 (`envAtt_extends`): -15, `D +15, tied +15`. Shortfall on the at-1a-tie first half: `baseEnvAtt`, 7 lines, stays S, because none of the five statements names
it and `tools/trust_map.py` refuses that tie; it moves at at-1, tied to `frame_wellFormed` (decision -trust item 2). Row at-1b-tie (`AFormula.toFormula`, 10 lines, once at-1 proves `att_elaboration_faithful`) is the DRI's.
No docstring trimmed, no line joined, nothing else reclassified.

## Size

`git diff --numstat $(git merge-base HEAD main)`, without generated files and the tool-written trust-mutants.json:

| Kind | Lines |
|---|---|
| Spec Lean, verbatim but for the two signed lines | Syntax.lean 180 of its 189 (imports, section headers and module doc are the rest) |
| Proofs | Theorems.lean 138 |
| Guards and fixtures | Examples.lean 395, of which 172 are the trust-sweep and `AWellFormed` fixtures (:538-:709) |
| Docs | ATTITUDES.md 6, DELTA.md 16, this report |
| Evidence | mutants.json 37, trust-mutants-allow.json 32, spec_text_check.py 55 |
| Side tables | trust-classes.json 120, trust-baseline.json 7, VE.lean 1 |

The total is over the ~600 guide. The DRI ruled the five statements stay and the size is reported here, and rejected the cut to at-1bb
(reviews/dri-decisions-20261105-at-1b-size.md item 1). No guard or docstring was trimmed.

## Pilot bytes

None expected: a structure row (bytes 0). No route, verdict or wording changes (DELTA), so nothing is claimed.

## Runs

- `lake build` (full) on this HEAD's Lean: `Build completed successfully (1302 jobs)`. `python3 lean/audit.py`: `PASS: 775 source files; 8604 named theorem declarations audited`.
- `#print axioms`: the five theorems use only `propext`, `Quot.sound` and (`keyOf_name`) `Classical.choice`.
- `zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 6ce23fdce: `recorded 100 units …; 1 failed`, exit 1. The one failure was `tests/test_lean_limits.py::test_no_non_frozen_lean_check_hard_codes_a_limit`; 814e0f03f fixes it, and the rerun of that id (`mac-pytest.sh -- <id>`, on the VM) gives `1 passed`. As the task says, the whole selection was not rerun on the fix.
- `uv run python tools/gate_collection.py --check --prebuilt`: `0 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed`. `python3 tools/check_lean_imports.py`: `Lean layer graph kept (775 modules, 22 reviewed legacy edges)`.
- `grep -rln VE.Attitudes lean/VE/Service lean/VE/Route lean/Main.lean ve/`: no file, so no route reads these modules.
- Not run here: the full gate (the chain runs it). Main has moved 97 commits past the merge base; not merged here (the train syncs), and `git diff --name-only HEAD...main` is empty on `lean/VE/Attitudes`, `lean/VE/Attribution`, `lean/VE/Norms/Tree.lean`, `lean/VE/EnglishGrammar/Lexicon.lean` and `tools/trust_map.py`. No test in main-known-red.txt was touched.
- One slip, no effect on the result: `tools/trust_map.py --files <path>` writes its report to `<path>`, and I gave it `Syntax.lean`, overwriting the working copy with JSON. It was restored from the commit made just before (353 lines, `trust_map.py --check` unchanged at +180); the file was committed, so nothing was lost.

FOLLOW-UP: none new. The DRI filed `at-1b-tie`; `at-1a-tie`'s shortfall is recorded above.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no service mode, schema or relay changes (grep in "Runs").
2. PASS: section "Deliverables" gives each task line with its commit and check. No Python copy, no report test: `git diff --stat` shows no `tests/`, `ve/` or `tools/*.py` file.
3. PASS: `mutants.json` (35, each failing a named guard or proof); `trust-mutants.json`: 0 SURVIVOR, 0 UNKNOWN; the allow file's reasons are one per pair.
4. N.A.: Lean only, read by no route; no Python or Rust product code changed.
5. N.A.: no relayed field.
6. N.A. here: the chain gates the final HEAD. `trust-mutants.json` names b7b7428a6, whose Lean equals this HEAD's (`git diff b7b7428a6 HEAD -- lean` empty); later commits are the evidence and this report.
7. PASS: DELTA row 1 cites the DRI's decision file; `review-ready.py --delta-dri-needed`: rc 0.
8. PASS: no user-visible output changes: no route reads the modules (grep in "Runs"); DELTA says so.
9. PASS: the selection ran `lake build` and `tests/test_lean_limits.py`, and that test caught the literal limit: a real change whose selection held the test that fails.
10. PASS: the `thm-*` rows of `mutants.json` break the five proofs (section "Seeded bugs"). No statement changed; `spec_text_check.py` checks them.
11. N.A.: no evaluator, budget or deadline; `checkAtt` is read by no runner yet. The bounds it checks have boundary fixtures (:520, :523, :675).
12. N.A.: no runtime path changes.
13. PASS: `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed. No test removed.
14. PASS: opposite directions: passes :498-:499, each row refused :457-:493; D14c :514 both ways; D14d :504; `lexAgrees` both ways :602, :605; `spec_text_check.py` passes and fails. Each claim here names its command.
15. PASS, the four classes. Overclaim: "no route reads" and "no user-visible" rest on the grep in "Runs"; "verbatim" on `spec_text_check.py`, with its two signed differences named. No silent cut: the task's deliverables are all built, and the size question went to the DRI. Every check can fail: `trust-mutants.json` and `mutants.json`. Limits before work: N.A., no evaluator.
