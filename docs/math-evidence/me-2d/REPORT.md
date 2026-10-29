# me-2d REPORT: the words checks of `calc@0` (math-evidence ME-2, fourth part)

**Status:** built. The final HEAD is the branch's last commit, `feature/me-2d`.

**What changed:** the `calc@0` decoder refuses value words outside W6's verbalisation rule and spec 11.2's rules
(`VerbalisationCollision`, `ValueWordsForm`, `ReservedWord`). It uses the refusal texts of the spec's diagnostics
table and reuses W6a's Lean check.

**Signatures:** every changed answer is SIGNED by the DRI (reviews/dri-decisions-20261027-featureplan-gates.md item
5), and trust growth (V +8) is signed under R16. No signature is reserved and nothing is open. Bytes: 0.

## Statement gate

ME-S passed (manage-agents `math-evidence-p3ver2.final.md`: PASS). This item adds and changes no theorem statement.
`Wire.decodeCase_wellFormed` builds unchanged over the new `decode`. The `rests_on` spec gap (me-2c "Not
delivered" (2)) is not this item's.

## Plan rows and directives delivered

| Row or directive | Delivered | Where, checked by |
|---|---|---|
| `valueWordsOk` in the decoder (11.2: "the" first, no phrase word first, no reserved word) | yes | `VE.Calc.Wire.checkWords` (`lean/VE/Calc/Wire.lean:234`), called by `Wire.value` for each value, after its name and before its source. It reads 11.2's lists through `English.leadingPhrase` and `English.reservedIn` (`lean/VE/Calc/Render.lean:16`, `:20`), which `valueWordsOk` now reads too, so the lists have one owner |
| W6a's `checkVerbalisations` (`VerbalisationCollision`, "as W6a") | yes, reused, not copied | `VE.Calc.Wire.checkVerbalisations` (`Wire.lean:243`) hands each value's words to `VE.Time.Wire.checkVerbalisations` as a constant's verbalisation. `decode` calls it after all values are read and before premises, claims and `admit`'s name checks. W6's whitespace rule (`VE.Time.Wire.displayString`) runs first, in `checkWords`, so it comes before 11.2's rules |
| Each check's refusal text as the spec gives it | yes | `ValueWordsForm: the words of <name> must begin with "the" and not with "<phrase>"`; `ReservedWord: "<word>" in the words of <name>`; `VerbalisationCollision(<a>, <b>)` and W6's texts as W6a gives them |
| Route cases re-recorded | yes | `tests/data/route-cases.jsonl`: case 18 answers `VerbalisationCollision(x, x)`. New cases 24-28 cover `DuplicateName` with distinct words, `ValueWordsForm`, `ReservedWord`, a collision of two names, and the nearest accepted words. EXPECTED is in `tests/test_calc_service.py::test_route_cases_answer_their_rows`. The calc mode is not in `tests/route_case_recorder.py`'s `ROUTE_MODES`, so the cases were added to the corpus as me-2c added case 23, and the test records each answer |
| Condition: DELTA lists each changed route case and guard with its new text | yes | `DELTA.md` rows 1-8 (route case 18; me-2c's nine guards, grouped as in me-2c's REPORT) and rows 9-12 (each class of words that is now refused) |
| Condition: one fixture per check on both sides | yes | `lean/VE/Calc/RunExamples.lean`, section "The words checks" (`:930`): the accepted-words guard (`:942`) has 27 nearest accepted words. Each answers `c1 holds` with the `meaning_id` of "the x". The `expect` guard (`:947`) has 36 refused rows covering each phrase word, each reserved word, the order of the checks, every source kind, W6's rule at its boundaries (empty, 256/257 characters, double space, trailing space, tab) and collisions (first/last of three, before `UnknownName`, words one character apart accepted). Through the service: route cases 24-28 |
| Condition: placeholder words "w" get valid words | yes | Every `"words": "w"` in `RunExamples.lean` is now "the w". The digests are unchanged because words are not hashed. The 64-byte words guard uses "the {s}{s}{s}". The hostile set's `duplicate-name` row gives the second `x` other words, so it still reaches `DuplicateName`. me-2c's `line-words` fixture pins the nearest accepted words' line |
| Do not edit `Protocol.lean`, `service_schema.py`, or the spec | kept | `git diff main...HEAD --stat` |
| Each new check on both sides of each boundary | yes | as the condition rows above |

Not delivered: none. Size: +355/−43 hand-written lines outside generated files (`git diff --numstat` against the
merge base, excluding `checkers.lock`, `declarations.txt`, `assurance-manifest.md` and `trust-mutants.json`),
within ITEM_SIZE_TRIAL's 800-1,500. The item needed no cut.

## Deviations and readings (no DRI ruling needed: each is the spec's text or W6a's)

- **`<phrase>` in `ValueWordsForm`.** The spec has one template for two faults. A value's words that begin with a phrase
  word name it (`not with "the sum of"`). Words that do not begin with "the" name their first word
  (`not with "baseline"`, `not with "The"`).
- **`ReservedWord` names the first reserved word in 11.2's order** (`English.reservedWords`). "times ten to the power"
  contains "to the power", which comes earlier in that order, so it is reported as "to the power".
- **W6's rule is part of "W6a's check".** Words that are empty, over 256 characters, or not whitespace-normalised are
  refused with W6a's own texts, as plan W6a says ("whitespace-normalised … checked by the Lean check W6a already
  runs"). Spec 3.2's limit 7 still does not cap `words` at 64 bytes.
- **Fault order.** A value's own words checks run as that value is read. Collisions are checked after every value is
  read, and before premises, claims and `DuplicateName`/`UnknownName`. This is me-2c's measured placement, and it
  gives exactly the route case and guard changes me-2c listed.
- **Two pre-existing guards in `RunExamples.lean` were restated without an inline `match`**, with the same meaning:
  R-3's line (now `r3Line`, `:731`) and the unknown-reason guard (now a membership test). With an inline `match`,
  `tools/trust_mutants.py` read these guards as "elaborated otherwise than without the mutant" (UNKNOWN), although
  they failed under the mutant.

## Seeded bugs (`docs/math-evidence/me-2d/mutants.json`)

Lean is the only language with product code changed. The Python changes are tests and fixtures, and there is no Rust.
Each bug was applied alone to the final tree, built with `lake build VE.Calc.<module>`, and restored. Every one failed
the named `#guard`.

| # | File | Bug | Fails |
|---|---|---|---|
| M1 | lean/VE/Calc/Wire.lean | `ValueWordsForm` check disabled in `checkWords` | `RunExamples.lean:947` row `no-the` (the case answered) |
| M2 | lean/VE/Calc/Wire.lean | `ReservedWord` check disabled | `:947` row `and` |
| M3 | lean/VE/Calc/Wire.lean | `VerbalisationCollision` disabled (`checkVerbalisations []`) | `:495` (hostile set, `duplicate-name-words`), `:947` row `collision` |
| M4 | lean/VE/Calc/Render.lean | reserved word list missing "through" | `:947` row `through` |
| M5 | lean/VE/Calc/Render.lean | `leadingPhrase` finds nothing | `:947` row `sum` |
| M6 | lean/VE/Calc/Render.lean | `reservedIn` matches inside words | `:942` (accepted words: "the island" refused), and 7 more guards |
| M7 | lean/VE/Calc/Wire.lean | `ValueWordsForm` names the whole words | `:947` row `form-first` |
| M8 | lean/VE/Calc/Wire.lean | W6's rule not run first | `:947` row `empty` |
| M9 | lean/VE/Calc/Render.lean | `valueWordsOk` drops the reserved-word conjunct | `lean/VE/Calc/Examples.lean:488` (and `:361`, `:446`) |
| M10 | lean/VE/Calc/Wire.lean | collision check loses the names | `:495`, `:947` row `collision` |
| M11 | lean/VE/Calc/Wire.lean | W6's rule with a trailing space allowed | `:947` row `whitespace-first` |

## Trust (R16)

`tools/trust_map.py --check` on the final HEAD gives K +0, S +0 and untied V +8, and PASSes with the allowance in
`docs/trust-baseline.json`. The V lines are `Render.lean` +6 (G[V] `leadingPhrase`, `reservedIn`) and `Wire.lean` +2
(D[V], the two calls). `checkWords` and `checkVerbalisations` are D[R], with `admit` (+16). The fixture helpers are T
(`tools/trust-classes.json`). Trust mutants (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/math-evidence/me-2d/trust-mutants-allow.json --json docs/math-evidence/me-2d/trust-mutants.json`) exit 0 with
27 KILLED, 0 SURVIVOR, 0 UNKNOWN, 2 INVALID and 5 ALLOWED. Every allowance is an equivalent mutant or a mutant that
does not elaborate, and has its reason in the file. FOLLOW-UPS "## me-2d" asks for the ties pass.

## Tests run

- `lake build` (full) and `python3 lean/audit.py`: PASS (653 files).
- `tools/regen_generated.py --write`, then `--check` per entry for the assurance pins. `ve/assurance-manifest.json`'s
  Calc/Wire pin (474 → 494 lines, two declarations added) was reviewed by hand, since the generator only checks it.
- Selected tests (`mac-pytest.sh --select`, HEAD 73e32e84): 287 passed and 1 failed. The failure was
  `test_committed_trust_table_covers_every_declaration` (the new declarations were unclassified). It was fixed in
  56aaacc59, then rerun with `tests/test_consolidation_tools.py` and `tests/test_trust_budget.py` on 3d30868d: 293 passed.
- `tools/gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused/stale/malformed.
- None of these runs met a known-red test of main.
- Not run: the full gate (the chain runs it on the final HEAD).

## Pilot bytes

0. The item only refuses ill-formed value words. No pilot case uses `calc` words outside 11.2 (route cases 1-23
unchanged but 18).

## Next item

ME-3 (rank 92, the Python relay), then me-4.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. The response schema is unchanged (`calc.json` not regenerated). The new refusals are `error` text, already typed `common.json#/$defs/text`, and pass `tests/test_route_row_schemas.py` (selected run).
2. Every deliverable built, no rule broken: PASS. See the plan rows table above. One owner: 11.2's lists are read by `checkWords` and `valueWordsOk` alike (M4 and M9), and W6a's check is called, not copied. No Python decision was added.
3. Tests can fail: PASS. Seeded bugs M1-M11 (`mutants.json`). Trust mutants exit 0 (`trust-mutants.json`).
4. Python, Lean and Rust agree, and valid inputs pass: PASS. The accepted-words guard `RunExamples.lean:942` gives each accepted word list the same rows and `meaning_id` as on main, and route case 28 checks the same through the service. Python and Rust have no words decision.
5. R8 binding: N.A. No field Python reads from the answer was added or changed.
6. Gate evidence matches the final HEAD: PASS for the evidence here. The gate itself is run by the chain on the final HEAD.
7. No unsigned item: PASS. Every DELTA row cites the DRI's decision item 5, or R16 (row 13). No reserved signature.
8. Every user-visible change in DELTA: PASS. DELTA rows 1-12 cover the route case change, the nine guards, and each class of newly refused words with its text.
9. Test selection finds the tests: PASS. `tools/select_tests.py --base <merge-base>` selects `tests/test_calc_service.py`, `tests/test_route_row_schemas.py` and `tests/test_assurance_manifest.py`.
10. Lean statements and proofs: N.A. No theorem is added or changed. `decodeCase_wellFormed` builds unchanged (`lake build`).
11. Budgets and limits fail closed: PASS. W6's 256-character cap refuses at 257 and accepts at 256 (the words section's `long` row and the guard at `:942`). No budget changed.
12. No CPU or memory regression: PASS. Each value's words are scanned once, against 11.2's 16 fixed words. The collision check is W6a's linear `find?` over at most 512 values (limit 3). There is no new enumeration.
13. Test-removed trailers: N.A. No test is removed or renamed (`tools/gate_collection.py --check --prebuilt`: 0 removed, 0 stale, 0 malformed).

## FIXMAP

Files:
- `lean/VE/Calc/Wire.lean`: the `ve-calc@0` decoder. It owns `checkWords` (W6's rule, then `ValueWordsForm`, then `ReservedWord`) and `checkVerbalisations` (W6a's collision check over the values), and the calls in `value` and `decode`.
- `lean/VE/Calc/Render.lean`: 11.2's lists (`reservedWords`, `phraseWords`) and the lookups `leadingPhrase` and `reservedIn`. `valueWordsOk` reads them, for the renderer.
- `lean/VE/Time/Wire.lean` (not edited): `displayString`, `checkVerbalisations` (W6a), which are reused.
- `lean/VE/Calc/RunExamples.lean`: fixtures. Placeholder words became "the w", and the words section is at `:930`.
- `tests/data/route-cases.jsonl`: calc route cases 18 (now a collision) and 24-28 (new).
- `tests/test_calc_service.py`: EXPECTED for every calc route case.
- `ve/assurance-manifest.json`: the reviewed pin of `Calc/Wire.lean` (lines, sha256, declarations, `total_lines`). `docs/spec/assurance-manifest.md` is generated from it.
- `tools/trust-classes.json`, `docs/trust-baseline.json`: classes of the new declarations, and the R16 allowance (V +8).
- `docs/math-evidence/me-2d/`: DELTA, REPORT, `mutants.json` (seeded bugs), `trust-mutants.json` and `trust-mutants-allow.json`.

Key definitions (spec section -> name -> file:line):
- 3.1 words rules / 11.2 -> `VE.Calc.Wire.checkWords` -> lean/VE/Calc/Wire.lean:234
- 3.1 W6a check -> `VE.Calc.Wire.checkVerbalisations` -> lean/VE/Calc/Wire.lean:243 (calls VE.Time.Wire.checkVerbalisations, lean/VE/Time/Wire.lean:103)
- call sites -> `Wire.value` lean/VE/Calc/Wire.lean:255; `Wire.decode` lean/VE/Calc/Wire.lean:416
- 11.2 lists -> `English.reservedWords` Render.lean:7, `phraseWords` :12, `leadingPhrase` :16, `reservedIn` :20, `valueWordsOk` :25
- W6 rule -> `VE.Time.Wire.displayString` lean/VE/Time/Wire.lean:85

Regression commands:
- `cd lean && PATH=~/.elan/bin:$PATH lake build VE.Calc.RunExamples VE.Calc.Examples` (all words guards)
- `uv run pytest -q tests/test_calc_service.py tests/test_route_row_schemas.py` (needs `lake build ve_service` and a regenerated `lean/checkers.lock`)
- `uv run pytest -q tests/test_assurance_manifest.py tests/test_consolidation_tools.py -k "pinned or trust_table"`
- `uv run python tools/trust_map.py --check`

Generated files: `lean/checkers.lock`, `lean/declarations.txt` and `docs/spec/assurance-manifest.md`. Regenerate them with
`uv run python tools/regen_generated.py --write`. Any edit to `Calc/Wire.lean` also needs its pin in
`ve/assurance-manifest.json` updated by hand: lines, sha256, range, and `lean_decoders.total_lines`, which only a merge
derives.

Trust mutants: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/math-evidence/me-2d/trust-mutants-allow.json --json docs/math-evidence/me-2d/trust-mutants.json`. After a check-only or allow-only change, add `--rescore docs/math-evidence/me-2d/trust-mutants.json`.
## END FIXMAP
