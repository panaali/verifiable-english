# sc-7: scope's authoring wordings (scope-PLAN.md SC-7 at 90807e7f7, lines 1145-1158)

**Summary.** Built (1)-(3): `Pinned.parseGovernor`/`renderGovernor` (spec 2.2), `scope_parseRender`/`scope_renderParse`
(spec 5.8's text), F5a, one round-trip and one paraphrase `#guard` per 2.2 row, and the folded sc-4-f12. (4), the IDE
wiring, is cut at the size line as the task directs. Trust: K +0, S +37, V +112, trusted +149 (R16). No DRI signature is
reserved. Tests: the selected run passes (see the last fix round). Fix rounds: "Review F1", "Review F7", "Recheck F8 and
F9", "Recheck F10 and DRI note (c)": `clause` is now an allow-list (two F9 accept-direction guards could not stay; see there).

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
   clause is refused, not read as a title: "## When should Claude refuse?" and "### If in doubt, ask!" (a word of
   the slot ends a sentence, `clause`) are refused; "## Should Claude refuse?" is a title.
5. **Frontier.** The paraphrase takes the fitted candidate (`Context.fits`, SC-5's). With none it asks "Which rule or
   list above does this qualify?", my wording for the spec's "a question".
6. **sc-4's F12 row (sc-4 REPORT.md:21) dropped the residual.** Spec 1.9 says "with `UnresolvedScope`". It is SC-5's
   (spec:1612) and is not built. The unit is UNFORMALISED (`meaning: {"unformalised": "norms"}`) with no residual.

## Size

`git diff --numstat` against the merge base, without generated files and mutant JSON: Authoring.lean 210, Examples
107, test_scope_authoring.py 49, trust-classes.json 59, ScopeExamples.lean 17, test_scope_lean.py 14, FarExamples.lean
8, the manifest 4, VE.lean 2, DELTA 10, and this report, 118. Total 598. (4) needs a mode, a schema, a
relay and binding fuzz tests (docs/ROUTE-RECIPE.md), well past 600.

## Evidence

- **Trust** (`tools/trust_map.py --check`): K +0, S +37, D +140, trusted +149 against da5303b78769, all in Authoring.lean.
- **Trust mutants**: `mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Scope/AuthoringExamples.lean --json
  docs/scope/sc-7/trust-mutants.json --allow docs/scope/sc-7/trust-mutants-allow.json`, a full run on b11beab23 (the
  allow-list round; later commits change no Lean): 229 KILLED, 0 SURVIVOR, 0 UNKNOWN, 64 INVALID, 27 ALLOWED (ill-typed, or
  one of 4 equivalent), exit 0. F8 and F9's full run on c494438df gave 213 KILLED. F7's full run on b4fa6691a gave 199
  KILLED. F1's full run on 971464587 gave 196 KILLED, 58 INVALID. The first run on 0367744f2 gave 193 KILLED, 60 INVALID, 29 ALLOWED.
  Earlier runs left 15 survivors; each was closed by a new `#guard` or by giving `attitude` an `Option` degree.
- **Hand mutants** (`docs/scope/sc-7/mutants.json`): each was planted, `lake build VE.Scope.AuthoringExamples` was run,
  and the code was restored. Every one is KILLED. They cover the 11 definitions the sweep does not kill (`closers`,
  a string with no sweep operator: see "Review F7"):
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

## Review F1 (fix round, sc-7-review.final.md)

- **Finding.** A slot could end a sentence: `## When should Claude refuse?` and `### If in doubt, ask!` parsed as
  narrowings, "…where is the act irreversible?." was accepted, "The rules below are called the x. The rules below are
  called the y." gave one list name, and "section 3?, x." was accepted.
- **Fix (the class).** `Pinned.clause` is every slot's one check: the condition, the rule, the When/If heading's
  condition, the frontier, the list name (`listName`) and the section. No word of a slot ends in ".", "?", "!", ":",
  "…", "‽" or "。？！：．", before any of ” ’ " ) ] » (this round said "any closing quote or bracket", an overclaim:
  review F7 widened the set to `Pinned.closers`). A title's heading is no slot. The docstrings of
  `clause` and `readHeading` now say what the code does. Lean only: no Python or Rust reads a wording (sc-7b).
- **Regression tests.** `AuthoringExamples.lean:110` (the review's probe, verbatim), `:113` (every slot and every
  sentence end), `:125` and `:127` (a comma, and a bad first character, in the section slot), `:130-:133` (the
  accepted direction: "## Should Claude refuse?" is a title; "3.2" stays in a slot; "users’"), and
  `tests/test_scope_authoring.py::test_review_f1_no_slot_ends_a_sentence_is_guarded`. Probe F1 fails on b5c25c551
  and passes on 6db17810d.
- **Seeded bugs** (`mutants.json`, the 6 marked "sc-7 review F1"): the old `clause` (fails :110, :113); no closing-
  quote strip, no full-width ends, `listName` back to `spaced`, the section without `clause` (each fails :113); the
  section without its comma check (fails :125). Each was planted and then restored.
- **Trust.** V +2 (`clause`, 4 lines). sc-7 is K +0, S +37, V +106, trusted +143 (R16, at most 150; the allowance was
  recorded with `trust_map.py --allow`). Trust mutants: the full run on 6db17810d left 1 SURVIVOR (`readings` :179,
  `s` -> `s.drop 1`) and 1 UNKNOWN (`clause` list-empty, ill-typed). `:127` kills the first. The second is allowed,
  and the 2 stale `clause` allowances (body-true/false, now KILLED) are dropped. Final run on 971464587: exit 0.
- **Tests.** `mac-pytest.sh --select -- --base da5303b78 --run` on 2617211d (ve-cloud-2, 3981 s): exit 0, 129 files
  exit 0, none failed. `(cd lean && lake build)`: "Build completed successfully (1329 jobs)". `python3 lean/audit.py`:
  PASS, 794 files. `regen_generated.py --check` passes. Not run: the full gate (the merge train runs it).
- **C findings** are follow-ups, except the bookkeeping this round touched anyway: B5's check location (F4), the
  FOLLOW-UPS.md sc-7 row's numbers (F4), and a comma fixture for the section slot (F5).

## Review F7 (fix round, reviews/sc-7-dri-note-20261109.md, sc-7-looprecheck1.final.md)

- **Finding (A).** `clause` dropped only ” ’ " ) ] » before looking for a sentence end, while its docstring, DELTA and
  this report said "before any closing quote or bracket". `## If the user says 'stop.'` was read as a narrowing (its
  curly form was refused), and "the x.' The rules below are called the y", `x.} y`, `x.› y`, `x。」 y` and `x.） y`
  were accepted.
- **Fix (the class).** `Pinned.closers` (Authoring.lean:31-34) is every closer: each character of Unicode 16.0's
  categories Pe, Pf and Pi (Pi too, since German and Danish close with “ and «), the quotes `"`, `'`, `＂` and `＇`, `>`,
  and Markdown's `*`, `_`, `` ` `` and `~`. Its 108 characters were generated from `unicodedata` in code-point order.
  `clause` drops every trailing closer, and its docstring names each terminator, ‽ included (F1's docstring left it
  out). Docstrings, DELTA.md and this report say the same sets. A closer after no sentence end stays in its slot
  (`users'`, "(as above) is “final”"). Lean only: no Python or Rust reads a wording (sc-7b).
- **Regression tests.** `AuthoringExamples.lean:138` (PROBE F7 verbatim, plus `x.› y` and `x.） y`), `:142` (the DRI
  note's closers, the ASCII and Markdown ones and the opening-form quotes are in `closers`), `:150` (every closer, alone
  and before `)”`, after every sentence end, in all 9 slot positions), `:153-:154` (the accepted direction).
  `tests/test_scope_authoring.py::test_review_f7_the_probe_wordings_are_refused` (Lean's verdict on each wording, and
  each is in a guard), and `::test_review_f7_clause_refuses_exactly_the_documented_closers`. The second runs `clause`
  on "x." plus each Unicode scalar that is a `wordChar`, through `lake env lean`. It checks that the refused set is
  exactly the docstrings' (the terminators, Pe ∪ Pf ∪ Pi from `unicodedata`, and the listed extras), with both
  docstrings read from the compiled environment (`findDocString?`). PROBE F7 exits 1 on 8bbc4b2b0 and 0 on ecd3e18f5.
  All 6 wordings are accepted on 8bbc4b2b0. The F1 guards and the 5 earlier tests still pass.
- **Seeded bugs** (`mutants.json`, the 5 marked "sc-7 review F7", each planted and then restored):
  - the old closer set: fails :138 and :142;
  - `'` dropped: fails :138 and :142, and the sweep no longer refuses U+0027;
  - an unnamed `,` added: fails `test_review_f7_clause_refuses_exactly_the_documented_closers`;
  - `>` dropped from the docstring: fails the same test;
  - one closer stripped instead of all: fails only :150.
  The membership guard :142 was added after the class guard alone missed a dropped closer, because it ranges over
  `closers` itself (b4fa6691a).
- **Trust.** V +5 (`closers`, 4 lines and its blank line). sc-7 is K +0, S +37, V +111, trusted +148 (R16, at most 150;
  `trust_map.py --allow`, signed by standing ruling R16). `test_scope_lean.py`'s AUTHORING list names `closers`. The
  manage-agents FOLLOW-UPS.md sc-7 ties row now says +111/+148 and names `closers`. Trust mutants: full run on b4fa6691a
  (ve-mac-1), 199 KILLED, 0 SURVIVOR, 0 UNKNOWN, exit 0. `closers` is a string literal with no sweep operator; the
  seeded bugs above kill it. `clause`'s allow reason now cites :38/:39 (the line shift from this fix; the other stale
  references stay F4's follow-up). Rescored on 502511501: exit 0.
- **Tests.** `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 2810cac86 (ve-cloud-3, 4305 s):
  exit 0, 120 units, 0 failed; `test_scope_authoring.py` and `test_scope_lean.py` among them. `(cd lean && lake
  build)`: "Build completed successfully (1329 jobs)". `python3 lean/audit.py`: PASS, 794 files. `regen_generated.py
  --check`: "checked 37 entries". No test of main-known-red.txt failed. Not run: the full gate (the merge train runs
  it).

## Recheck F8 and F9 (fix round, reviews/sc-7-dri-note-20261109b.md and its amendment, sc-7-c090722-looprecheck1.final.md)

- **Findings (A).** F8: `clause`'s sentence ends were 11 characters, so "the x‼ The rules below are called the y" was one
  list name, and `x⁉ y`, `x؟ y`, `x｡ y`, `x﹖ y` and `x। y` were conditions. F9: `clause` dropped only `closers` before
  it read a word's last character, so U+200B, U+2060, U+00AD, U+FE0F or U+0301 after a "." hid the sentence end.
  PROBE F8 and PROBE F9 exit 1 on 3fa303c51 and 0 on f5b2f2124.
- **Fix (since replaced), Lean only.** `clause` refused a word whose last character, once its trailing closers and
  invisible characters were dropped, was in a literal list of sentence ends; `wordChar` also refused the C1 controls and
  the five fillers drawn as a space (U+115F, U+1160, U+2800, U+3164, U+FFA0), which stood in for a space in
  "x.\u3164The rules below are called the y" (this part stays). The recheck (F10) found the list incomplete and more
  invisible characters outside the dropped set, so the next round replaced both lists with an allow-list, and the claims
  this round made about the two sets' completeness, their sources and the sweeps over them are withdrawn.
- **Regression tests.** PROBE F8 and PROBE F9, verbatim, in `AuthoringExamples.lean`; the F8 guard over the sentence
  ends F8 named; F9's guards on U+00AD, U+FE0F, "x.)\u0301 y", invisible characters mixed with closers, the Hangul
  fillers, the braille blank and the C1 controls. All of them stay. The Python sweeps over the two sets were replaced by
  the next round's exactness sweep.
- **Seeded bugs** (`mutants.json`, the 6 marked "sc-7 recheck", on the code of that round, each planted and then restored,
  all KILLED):
  - `‼` dropped from the sentence ends: fails :159, :163 and :171;
  - U+200B dropped from the stripped set: fails :163, :169, :171 and :177;
  - U+0301 dropped: fails :169 and :171;
  - U+3164 dropped from both the stripped set and `wordChar`: fails :183 and :189;
  - U+3164 dropped from `wordChar` only: fails :189;
  - U+0483, which no guard names, dropped: `lake build` passes, and the sweep fails
    `test_review_f7_clause_refuses_exactly_the_documented_closers` and `test_review_f9_no_invisible_character_hides_a_sentence_end`.
    This ran with the statement-inventory import stubbed, because the inventory is stale while a mutant is planted.
- **Trust.** V +2 (the `clause` docstring grew from 2 lines to 4; `wordChar` keeps its 3 lines). sc-7 is K +0, S +37,
  V +113, trusted +150, at R16's cap (`trust_map.py --allow`, signed by standing ruling R16). Both DELTA Ruling cells
  cite R16. No DRI signature is reserved. No new definition, so the AUTHORING list in `test_scope_lean.py` is
  unchanged. The manage-agents FOLLOW-UPS.md sc-7 ties row now says +113/+150. Trust mutants: full run on c494438df
  (ve-cloud-2): 213 KILLED, 0 SURVIVOR, 0 UNKNOWN, exit 0. Rescored on 5dd5256c5 after `clause`'s allow reason moved
  from :38/:39 to :40: exit 0.
- **Tests.** `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 8e52487c3 (Claude cloud, 5
  shards, 3013 s): exit 0, 129 units, 0 failed. `test_scope_authoring.py` and `test_scope_lean.py` were among them.
  `(cd lean && lake build)`: "Build completed successfully (1329 jobs)". `python3 lean/audit.py`: PASS, 794 files.
  No test listed in main-known-red.txt failed. Not run: the full gate (the merge train runs it).

## Recheck F10 and DRI note (c) (fix round, reviews/sc-7-dri-note-20261109c.md, sc-7-c091054-looprecheck1.final.md)

- **Findings.** F10 (A): the sentence-end literal left out U+2CF9..U+2CFB, so "x⳹ y" was a condition. Deferred to the
  DRI: U+1D159, U+E000 and U+FFFC after a "." hid the sentence end. The DRI note (c) rules on the class (a character at
  a word's end that hides a sentence end from `clause`): an allow-list. PROBE F10 exits 1 on c82b303ed and 0 on b880471cf.
  The same probe with "x. y", "x.￼ y" and "x.\U0001D159 y" fails on c82b303ed and passes on b880471cf.
- **Fix (the class), Lean only** (`lean/VE/Scope/Authoring.lean:36-40`; no Python or Rust reads a wording before sc-7b).
  `clause` drops a word's trailing `closers` as before. The word must then be non-empty, and its last character must be
  in this allow-list and no other:
  - an ASCII letter or digit;
  - a Latin letter of U+00C0 to U+024F, except U+00D7 "×", U+00F7 "÷" and U+01C3 "ǃ";
  - one of `,` `;` `-` `%` `/` `&` `+` `=` `#` `$` `@`.

  The sentence-end literal and the Cf/Mn/Me/Default_Ignorable range table are gone. An empty word (one made only of
  closers) is now refused through `Option.any` on `getLast?`, so it no longer falls through to `String.back`'s default.
  `wordChar` is unchanged, including its refusal of the fillers anywhere in a word. `closers` is unchanged.
  - **U+01C3 is left out, beyond the note's start list.** LATIN LETTER RETROFLEX CLICK is a letter (Lo) drawn exactly as
    "!", so "the xǃ The rules below are called the y." would read as two sentences to a person and as one list name to
    `clause`. That is a hole in the allow-list itself. The note's widening rule is not used: no character was added.
  - **Two accept-direction guards could not stay.** F9's round had guards that accepted "the café rules" and "the
    act is final​". Those words end in a mark and a format character. The note asks both "do not admit any … mark,
    format … character" (with the exactness sweep) and "do not narrow the existing accepted-direction guards". These
    two guards cannot meet both. The guards now assert refusal (`AuthoringExamples.lean:194`), and the precomposed
    "café" carries the accepted direction (`:228`, `:229`). The DRI may overrule this. No answer on main changes, since
    no route reads the code.
- **Regression tests** (`lean/VE/Scope/AuthoringExamples.lean`):
  - `:200`: PROBE F10, verbatim.
  - `:203`, `:206`: U+FFFC and U+E000 after "." as a condition and as a list name, and U+1D159, U+E000 and U+FFFC in
    every slot (alone, after ".", and before "”").
  - `:209`, `:210`: an empty word, as a word, in a condition and in a list name.
  - `:213`, `:214`: a C1 control inside a word.
  - `:217`, `:218`: every closer dropped after an allowed character, and a condition in ASCII quotes.
  - `:221`, `:223`: one accepted word per allow-list class (ASCII letters, digits, the Latin range's ends, "café", each
    allowed punctuation character), and the refused neighbours (×, ÷, ¿, ɐ, ".", "!", "?", ":", U+0301, U+200B, α, ٣).
  - `:225`, `:227`: "ǃ" refused, with its neighbours ǀ ǁ ǂ Ǆ accepted.
  - `:228` to `:230`: round trips with "café" and with every allowed punctuation character.

  PROBE F7, F8 and F9's guards, F7's closer sweep and F9's sample stay. `tests/test_scope_authoring.py` replaces the
  terminator and strip-set sweeps with one exactness sweep: a single `lake env lean` process (one `#eval`, about 60 s).
  For every Unicode scalar value c, `::test_clause_accepts_exactly_its_documented_allow_list` checks that `clause`
  accepts "x" c and "x" c ")" exactly when c is in `ALLOW` or is a closer (less `wordChar`'s refusals), and accepts
  "x." c exactly when c is in `ALLOW`. `ALLOW` is written in the test from the note, apart from the Lean code (470
  characters). The test also checks that the docstring states the allow-list in those words and names no enumerated
  Unicode set. `::test_word_char_refuses_exactly_its_documented_characters` keeps `wordChar`'s sweep.
  `::test_review_f8_f9_f10_the_probe_wordings_are_refused_and_guarded` covers the probe wordings (with U+1D159, U+E000
  and U+FFFC) and the guards.
- **Seeded bugs** (`mutants.json`, the 5 marked "DRI note 2026-11-09 (c)", planted on b880471cf and then restored, all
  KILLED; the line numbers are b880471cf's):
  - (1) `.` added to the allow-list: fails :69, :113, :138, :150 and the refused-neighbour guard;
  - (2) U+FFFC admitted: fails the two U+FFFC guards;
  - (3) the Latin range dropped: fails the accepted-class guard, the ǃ-neighbour guard and both "café" round trips;
  - (4) an empty word let through (`.any` → `.all`): fails both empty-word guards;
  - (5) U+FFFD admitted, which no guard names: `lake build` passes, and
    `test_clause_accepts_exactly_its_documented_allow_list` fails ("accepted, not allowed": U+FFFD). This ran after
    `tools/lean_statements.py` on the planted tree, which was then restored and regenerated.
- **Trust** (`tools/trust_map.py --check` on the final HEAD). Per file: `lean/VE/Scope/Authoring.lean` was +150 at
  c82b303ed and is +149 now. Per definition: `clause` goes from 7 lines to 6 (3 docstring lines, 2 code lines, 1
  blank); `closers` (5) and `wordChar` (4) are unchanged. The item is K +0, S +37, V +112, trusted +149, under R16's
  cap. No new allowance is recorded: the ledger's allowances total +150. Both DELTA Ruling cells cite R16, and no DRI
  signature is reserved. No new definition, so `test_scope_lean.py`'s AUTHORING list is unchanged.
- **Trust mutants** (full runs, ve-cloud-3):
  - On b880471cf, exit 1 with 3 survivors:
    - `wordChar` `0x7F ≤` → `=`, because the C1 guards put the control after a "." where the allow-list already
      refuses it;
    - `clause` `closers` → `closers.drop 1`;
    - `clause` `toList` → `toList.reverse.take 1`, which is equivalent under `getLast?`.

    The first two are now killed by `:213`/`:214` and `:217`/`:218`. `:213` also kills `c.toNat ≤ 0x9F` → `<` (M100).
    M100 had been hidden under `wordChar`'s le-lt allowance, which matches on definition and operator and was written
    for the equivalent `0x20 ≤`. The third is allowed with its equivalence reason, and `clause`'s list-empty reason now
    cites :39 and :40.
  - On b11beab23: 229 KILLED, 0 SURVIVOR, 0 UNKNOWN, 64 INVALID, 27 ALLOWED, exit 0.
- **Tests.** `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on 76eda2367 (ve-cloud-3, 4537 s):
  exit 0, 120 units, 0 failed. `test_scope_authoring.py` (exit 0, 440 s) and `test_scope_lean.py` were among them. The
  new and changed tests also ran on their own: 28 passed. `(cd lean && lake build)`: "Build completed successfully
  (1329 jobs)". `python3 lean/audit.py`: PASS, 794 files. `trust_map.py --check`: PASS, trusted +149.
  `regen_generated.py --check`: "checked 37 entries". No test of main-known-red.txt failed. Not run: the full gate
  (the merge train runs it).

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
6. PASS: trust-mutants.json is for head b11beab23, whose Lean tree is HEAD's. The gate is the chain's, on the final HEAD.
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
