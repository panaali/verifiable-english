# sc-7: scope's authoring wordings (scope-PLAN.md SC-7 at 90807e7f7, lines 1145-1158)

**Summary.** Built (1)-(3): `Pinned.parseGovernor`/`renderGovernor` (spec 2.2), `scope_parseRender`/`scope_renderParse`
(spec 5.8's text), F5a, one round-trip and one paraphrase `#guard` per 2.2 row, and the folded sc-4-f12. (4), the IDE
wiring, is cut at the size line as the task directs. Trust: K +0, S +37, V +104 (R16). No DRI signature is reserved.
Tests: the selected run passes after two classification fixes (see "Tests run").

FOLLOW-UP: sc-7b IDE writes the scope block from the 2.2 wordings

## Before building

- **edits-scope.md.** No line names SC-7; this item implements none of its edits. The title row keeps edit 6 / DEC 10.
- **Overlap.** `git diff --name-only main...<branch>` over the 17 branches ahead of main (base da5303b78): none touches
  `lean/VE/EnglishGrammar/`, `lean/VE/Scope/`, `lean/VE/Service/ScopeExamples.lean` or `lean/VE/Discourse/Access.lean`.
  Three (et-4b, pe-1, me-1) touch `lean/VE.lean`, an import union (lean-roots [union]).
- **Queue (sprint item 6).** SC-7 lands before AT-5, QT-A6, ME-11 and QT-B3: all four were blocked on 2026-11-03, and
  item 6 lets a row on disjoint paths go first. SC-7 appends to no shared catalogue file, so they rebase onto nothing.

## Plan rows and directive lines

| Row | Delivered | Where |
|---|---|---|
| (1) parse/render, exactly 2.2's wordings | yes | `lean/VE/Scope/Authoring.lean` (1ba7f549c, ab954263e, 0367744f2) |
| (2) the two theorems, word for word | yes | same file; `tests/test_scope_authoring.py::test_the_round_trip_statements_are_spec_5_8s_text` |
| (3) F5a, per-row round trip and paraphrase | yes | `lean/VE/Scope/AuthoringExamples.lean` (`trip`, `para` per row); `test_each_row_of_2_2_has_a_round_trip_and_a_paraphrase_guard`, `test_f5a_guards_u0170_s01s_wording_as_the_spec_quotes_it` |
| (4) IDE wiring through the relay | cut (sc-7b) | "Size" |
| `actions_version` | not needed | no file under `lean/VE/EnglishGrammar/` or `ve/english_grammar/` changes; `english_grammar_gen.py --check` exits 0 |
| sc-4-f12 | yes | comment at `FarExamples.lean:77-80`; `#guard u0047Statuses` (`lean/VE/Service/ScopeExamples.lean`, document mode on the pinned rows); span `#guard` (95, 209 bytes) in FarExamples |
| DELTA, allowance, ties row | yes | `DELTA.md`, `docs/trust-baseline.json`, FOLLOW-UPS.md "## sc-7" |

## Deviations

1. **Placement.** The wordings are in `lean/VE/Scope/Authoring.lean`, not rows of english-lean's catalogue (spec 2.2).
   The catalogue has no template list. A trusted file under `lean/VE/EnglishGrammar/` joins its LOCK and raises
   `actions_version` in every English answer. The condition and rule slots stay `{"english": text}` for the English
   reader (sc-7b), so scope adds no grammar. Spaces are discourse's `spaceChar`, which keeps the import inward.
2. **Slots.** The slots are the list name ("the …"), the condition, the rule, a one-word section and the heading;
   every other word is fixed. "Claude" is fixed: the `frame` part carries no agent. A wording is accepted only when
   exactly one row's block renders back to its bytes, so a wording two rows read is refused.
3. **Block.** It holds what the wording fixes. The reach the layout resolves is written `"list"`,
   `{"anchor": {"heading": h, "level": k}}` or `{"anchor": {"section": s}}`. Ids come in sc-7b.
4. **Headings.** Levels 1-6 are accepted; "If" paraphrases as "applies only if". A "When"/"If" heading that is no
   clause is refused, not read as a title.
5. **Frontier.** The paraphrase takes the fitted candidate (`Context.fits`, SC-5's). With none it asks "Which rule or
   list above does this qualify?", my wording for the spec's "a question".
6. **sc-4's F12 row (sc-4 REPORT.md:21) dropped the residual.** Spec 1.9 says "with `UnresolvedScope`". It is SC-5's
   (spec:1612) and is not built. The unit is UNFORMALISED (`meaning: {"unformalised": "norms"}`) with no residual.

## Size

`git diff --numstat` against the merge base, without generated files and mutant JSON: Authoring.lean 210, Examples
107, test_scope_authoring.py 49, trust-classes.json 59, ScopeExamples.lean 17, test_scope_lean.py 11, FarExamples.lean
8, the manifest 4, VE.lean 2, DELTA 10, and this report, about 110. Total about 590. (4) needs a mode, a schema, a
relay and binding fuzz tests (docs/ROUTE-RECIPE.md), well past 600.

## Evidence

- **Trust** (`tools/trust_map.py --check`): K +0, S +37, D +132, trusted +141 against da5303b78769, all in Authoring.lean.
- **Trust mutants**: `mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Scope/AuthoringExamples.lean --json
  docs/scope/sc-7/trust-mutants.json --allow docs/scope/sc-7/trust-mutants-allow.json`, a full run on 0367744f2: 193
  KILLED, 0 SURVIVOR, 0 UNKNOWN, 60 INVALID, 29 ALLOWED (ill-typed, or one of 3 equivalent), exit 0, tree = HEAD.
  Earlier runs left 15 survivors; each was closed by a new `#guard` or by giving `attitude` an `Option` degree.
- **Hand mutants** (`docs/scope/sc-7/mutants.json`): each was planted, `lake build VE.Scope.AuthoringExamples` was run,
  and the code was restored. Every one is KILLED. They cover the 10 definitions the sweep does not kill:
  `Row.wording`:25, `frameWording`:21, `kindWording`:34, `kindCondition`:34, `textOf`/`englishOf`/`narrowed?`:29,
  `renderGovernor`:21, `between`:25, `splitOnce`:103. Lines are in AuthoringExamples.lean.
- **Seeded bugs, one per claimed behaviour.** Lean is the only product language changed.
  - B1, no spacing variant: `spaced` loses `!w.isEmpty` (Authoring.lean). Caught at AuthoringExamples.lean:69.
  - B2, two readings refused: `parseGovernor` takes the first reading (Authoring.lean). Caught at :101.
  - B3, F5a: `readHeading` reads any line as a heading (Authoring.lean). Caught at :65 (`readings u0170s01 == []`).
  - B4, paraphrase: "If" headings say "when" (Authoring.lean). Caught at :49.
  - B5, sc-4-f12: `unitStatuses` reads `support` (lean/VE/Service/Document.lean). Caught by the u0047 status `#guard`.
  - B6, theorem: `parseGovernor` loses its render check. `scope_parseRender` fails at Authoring.lean:201.

## Tests run

- `mac-pytest.sh --select -- --base da5303b78 --run`, once, on e193eb42 (ve-cloud-3, 7316 s): 490 of 492 files exit
  0. The failures were `test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` and 5 ids of
  `test_scope_lean.py`, all new-file classification. c2223e88 fixes them (an `other_json` reason; an AUTHORING list
  like WIRE/READINGS). The rerun of those ids passed ("6 passed", ve-mac-1).
- `(cd lean && lake build)`: "Build completed successfully (1329 jobs)". `python3 lean/audit.py`: PASS, 794 files.
  `gate_collection.py --check --prebuilt`: 4 added, 0 refused, 0 stale, 0 malformed. `regen_generated.py --check`:
  "checked 37 entries".
- No test of main-known-red.txt failed. Not run: the full gate, which the chain runs.

## Spec re-read

The theorems against docs/spec/scope.md:1569-1573 (test). The nine 2.2 rows against :364-374, each wording and
paraphrase a `#guard`; the frontier paraphrase adds a final ".". F5a against :353-355 and 7.8, byte for byte (test).
The names against 8.1 (:1788).

## Bytes and next item

No bytes on the translations, and nothing is claimed before a pilot audit. Next: none in scope's build list (sc-3b
waits on sc-2c/sc-2d); sc-e1/sc-e2 come after Nov 12; sc-7b is the follow-up.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer; no route reads the wordings before sc-7b.
2. PASS: the plan-rows table above. (4) is cut where the task names the cut. No Python reads a wording.
3. PASS: trust-mutants.json (exit 0) and mutants.json (all KILLED). The allow list gives exact (definition, operator)
   pairs, each with its reason.
4. N.A.: Lean only, with no Python or Rust path. Valid inputs pass: nine `trip`s, plus the curly-quote slot.
5. N.A.: no relay and no Python reader.
6. PASS: trust-mutants.json is for head 0367744f2, tree = HEAD. The gate is the chain's, on the final HEAD.
7. PASS: both DELTA rows cite R16 with evidence. Nothing reserved.
8. PASS: no existing answer changes, since no route reaches the code. The selected run passes after the fix.
9. PASS: the selection held test_scope_authoring.py, test_scope_lean.py and test_assurance_manifest.py, and it found
   both new-file failures.
10. PASS: B6 breaks the proof. `test_the_statement_gate_sees_a_changed_conclusion` shows the statement test fails.
11. N.A.: `parseGovernor` is no evaluator, runner or mode. 8 rows each read the string once (linear), and at most 8
   candidates render. sc-7b charges the request size.
12. N.A.: no existing path changes.
13. PASS: no test removed. gate_collection: 0 refused, 0 stale, 0 malformed.
14. PASS: both directions are guarded (refusal lists; the accepted rows, headings at levels 1/3/6, the curly-quote
   slot). Each claim names its command. Spec re-read is above.
15. PASS: each "no", "none" and "every" here and in DELTA cites a guard, a JSON or a check. The cut is the task's
   named one. No limit applies (item 11).
