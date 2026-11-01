# jt-3a report: the evaluative catalogue rows and the `undeclared_evaluative` report

Status: built; no DRI signature reserved (DELTA rows: R3, R16). HEAD: the commit that adds this report.
Lean reports `undeclared_evaluative` in the document mode under `judgments@0`, over english-lean's evaluative rows
(`lean/VE/EnglishGrammar/Evaluative.lean`), typed with its encoder theorem; the relay binds it (R8).
Open: "good judgment" (a phrase row) is jt-3p; spec 9.5's refusal and rewrite text and the lines are jt-3. Bytes 0.
The chain runs the full gate on the final HEAD.

Plan: docs/spec/judgment-terms-PLAN.md "JT-3. English rows and the undeclared-word report" (and D15, 2.4's catalogue
row, 3.5), spec docs/spec/judgment-terms.md 7, 8.4 and 11.7 (11.8's `undeclaredEvaluative_iff` row), jt-2c's REPORT.
Statement gate: the judgment-terms statement review accepted spec 7 and 8.4 (spec change log, draft 2 and 3; the plan's
change log, 2026-10-14 rows 2 and 3). No statement changed: `undeclaredEvaluative_iff` is spec 7's text, word for word.
Synthesis round 2: this item implements edits-judgment-terms.md item 3 (the rows carry no sense of their own: no gloss,
no numbered sense, no `sense__<word>_<n>` name; senses owns those), as the DRI's decision confirms
(reviews/dri-decisions-20261031-jt-3a.md item 1). Items 1, 2 and 4 concern other batches.

## DRI decisions (reviews/dri-decisions-20261031-jt-3a.md, asked through msg.sh)

1. Option (a): one-word rows only; the approved statement unchanged; "good judgment" is not delivered here (jt-3p).
2. Spec 9.5's authoring refusal and rewrite text moves to jt-3; in jt-3a "with their refusals and rewrites" means the
   rows' `otherSenses` and nothing more. No test here asserts reader-facing or authoring wording.
3. jt-3p (blocked by jt-3a) makes a row's word a phrase, signed by the DRI for that item.

## Plan rows

| Row | Delivered | Where | Checked by |
|---|---|---|---|
| (1) Catalogue rows for the evaluative words, each tied to its evaluative sense, with their refusals (`otherSenses`), in english-lean's single catalogue; no second source of templates | yes, but "good judgment" (DRI item 1) | `VE.EnglishGrammar.evaluativeRows`: reasonable, appropriate, appropriately, arbitrary, arbitrarily, fair, legitimate, genuine, genuinely, adequate, overly, just (not "just as"), effective (not "effective date"), necessary (not "necessary condition"), due (not "due date", "due to") | `lean/VE/EnglishGrammar/Examples.lean` #guards (11.7's rows present; the plan's words listed, their other senses not); S5 |
| (2) `undeclared_evaluative` computed by Lean in the document mode: base predicates (regulated included) whose words match a row, not bound | yes | `VE.Judgments.undeclaredEvaluative` and `predicateWords` (`lean/VE/Judgments/Undeclared.lean`, spec 7), `Env.basePredicates` and the `check`/`encode` lines (`lean/VE/Service/Document.lean`) | 11.7 #guards in `lean/VE/Judgments/Examples.lean`, `lean/VE/Service/UndeclaredExamples.lean`; `tests/test_judgments_undeclared.py::test_lean_lists_the_catalogue_matches_that_are_not_bound`; S1-S4, S6 |
| (3) Typed response shape, encoder theorem, generated schema through its tool | yes | `ResponseShape.Schemas.Document.undeclaredEvaluative`; `ResponseShape.Encoders.Document.undeclared_fits` and `document_fits`; `ve/backends/lean_service_schema/document.json` (`tools/regen_generated.py --write`) | `lake build`; `tests/test_response_schemas.py` (passed, below) |
| (4) Relay: schema and binding; each name a base predicate of the request (regulated included), not bound; fuzz retypes and rebinds; a genuine regulated answer accepted | yes | `ve/document/lean.py` `_undeclared_bound`, called by `_bind_document_answer` | `tests/test_judgments_undeclared.py` (13 tests); `tools/relay_mutation_gate.py --route service:document` "13 fixtures, 5016 mutants, 5012 refused, 4 allowed", "0 failures" (allow entry JT3A1: an emptied list is Lean's decision); P1-P3 |
| Seeded bugs named by the task | yes | `mutants.json`: S1 (other senses ignored: `due_date` listed), P1 (a bound judgment accepted), P2 (a regulated predicate refused) | below |
| Not this item: declaration, legend and status lines, `test_declaration_lines_match_jt_e1r_templates` | not built | jt-3 | none |

Theorems: `hasPhrase_iff`, `undeclaredEvaluative_iff` (spec 7), and `matches_iff`, `predicateWords_name`, added so that
`tests/test_judgments_exercised.py` finds a theorem about every trusted judgment definition.

Deviations, recorded here only:
- The rows are in a new english-lean file, `lean/VE/EnglishGrammar/Evaluative.lean`, not in `Catalogue.lean`. D15 puts
  "english-lean's single catalogue" in `lean/VE/EnglishGrammar/*`, and there is still one list. In `Catalogue.lean`, every
  trust mutant of the rows rebuilt the whole English grammar cone and hit the 1800 s build timeout (first run, logged
  UNKNOWN "lake build did not finish in 1800 s"). `Catalogue.lean` is unchanged against the merge base. The new file
  is TRUSTED in `tools/english_grammar_gen.py`, so the English `actions_version` is 36. The ask fixtures were
  re-recorded (`tools/ask_fixtures.py --write`); a field diff of the 17 files shows only
  `result/identities/actions_version` (17) and `seconds` (10) changed. The S3 comparison
  (`python -m conformance.english_lean_s3_compare`) changes only `actions_version` (170 rows) and Lark's
  expected-token order in two Python messages, as in jt-2c.
- Order. On the wire, Lean reads the vocabulary as a JSON object, ordered by key. So the list comes in name order,
  and 11.7's `[reasonable_grounds, just_requirement, make_reasonable_efforts]` arrives as
  `[just_requirement, make_reasonable_efforts, reasonable_grounds]`. The set and the stub's values are unchanged
  (the Judgments/Examples #guards keep 11.7's list order). The relay checks Lean's order, so a reordered list is refused.
- The import rule (`tools/check_lean_imports.py`) forbids `VE.Judgments` (layer 2) from importing english-lean (layer 3).
  So the catalogue #guards are in `VE.EnglishGrammar.Examples`. The first selected run caught this (shard 1).

## Seeded bugs (docs/judgment-terms/jt-3a/mutants.json)

Each one was planted in a file this item changed, run against the named check, and then restored.

| Id | Language, file | Mutation | Fails |
|---|---|---|---|
| S1 | Lean, `lean/VE/Judgments/Undeclared.lean` | `matches` ignores `otherSenses` | `Judgments/Examples.lean:360` (`due_date` listed), `:361`; `undeclaredEvaluative_iff`'s proof |
| S2 | Lean, same | the filter drops `!J.contains p` | `:360`, `:364` |
| S3 | Lean, same | `hasPhrase` skips the last position | `:374`; `hasPhrase_iff` |
| S4 | Lean, same | template words not lower-cased | `:379` |
| S5 | Lean, `lean/VE/EnglishGrammar/Evaluative.lean` | `due` loses "due to" | `EnglishGrammar/Examples.lean:200`, `:210` |
| S6 | Lean, `lean/VE/Service/Document.lean` | W3-defined names kept | 4 tests of `tests/test_judgments_undeclared.py` (service rebuilt, build pinned for the run) |
| P1 | Python, `ve/document/lean.py` | a bound judgment accepted | `::test_every_mutant_of_the_field_is_refused[bound]`, `::test_a_bound_judgment_listed_is_refused_and_unbound_it_is_relayed` |
| P2 | Python, same | a regulated predicate refused | `::test_a_regulated_predicate_is_listed_and_still_not_admitted` and 4 more |
| P3 | Python, same | order not checked | `::test_which_predicates_match_is_lean_s[out of order]` and 2 more |

S1 to S3 break their iff proofs first. They were run again with those proofs replaced by `sorry`, to show that the
#guards also fail. S1's pytest run stopped at conftest's build step on the same #guard.

## Trust

`uv run python tools/trust_map.py --check`: "K +0, S +36, D +1, G +20, tied +0, unclassified +0, trusted +57" against
`8c28fe28635a`; "PASS". Per file: Undeclared.lean S +27, Evaluative.lean S +9, Document.lean G[V] +13,
Schemas/Document.lean G[V] +8. The allowance is recorded with `--signed "SIGNED by standing ruling R16 (DRI-RULINGS.md),
jt-3a, 2026-11-01"`. The FOLLOW-UPS.md row "## jt-3a" asks for the ties pass. Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --test
lean/VE/Judgments/Examples.lean --test lean/VE/EnglishGrammar/Examples.lean --test lean/VE/Service/UndeclaredExamples.lean
--allow docs/judgment-terms/jt-3a/trust-mutants-allow.json --rescore ...`, `trust-mutants.json` at head `8f302d6d5`,
exit 0): "KILLED 221, SURVIVOR 0, UNKNOWN 0, INVALID 20, ALLOWED 24, NOT RUN 0" over 10 definitions (265 mutants; the
rescore reused 198 verdicts from the full run at `4c2ea7caa` and reran 67). The full run's 12 survivors were fixed by
new checks: a phrase at position 2, `J` with two names, a second W3-defined name, the `judgments` member beside the
new one, and a template that starts with a letter. The rest are allowed in `trust-mutants-allow.json`, one reason
each: three equivalent `hasPhrase` length mutants, and 13 operator cuts that do not elaborate.

## Checks run

- `lake build` (full): "Build completed successfully (1197 jobs)". `python3 lean/audit.py`: "PASS: 693 source files"
  on the final Lean: "PASS: 695 source files; 7814 named theorem declarations audited".
- `uv run python tools/regen_generated.py --write`: "wrote 34 entries". `python3 tools/check_lean_imports.py`:
  "Lean layer graph kept". `uv run python tools/english_grammar_gen.py --check`: no finding. `tools/ask_fixtures.py
  --check`: "18 of 18 recorded answers replayed".
- Local: `tests/test_judgments_undeclared.py tests/test_judgments_exercised.py tests/test_judgments_answer.py
  tests/test_english_lean_s3_compare.py` "47 passed"; `tests/test_judgments_answer.py tests/test_judgments_document.py
  tests/test_response_schemas.py` "92 passed"; `tests/test_assurance_manifest.py` "138 passed".
- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on `b50349522`): "424/517
  test units", six shards, "424 passed" (shard lines "72 units, 72 passed", "78", "79", "63", "70", "62"),
  "exit=0". A first selected run on `76149b73e` (before the restructure) failed 4 files: the import rule (shard 1,
  which stopped its 79 units), `test_assurance_manifest.py` (the `Document.lean` pin), `test_english_lean_s3_compare.py`
  (re-recorded) and `test_judgments_exercised.py` (the two theorems); each is fixed above, and the second run covers them.
- `uv run python tools/gate_collection.py --check --prebuilt`: "13 added, 0 removed by a trailer, 0 refused, 0 stale and 0
  malformed trailers". `tools/relay_mutation_gate.py --route service:document`: "0 failures".

Spec re-read: `undeclaredEvaluative`, `EvaluativeRow`, `hasPhrase`, `matches` and `_iff` against judgment-terms.md 7
(lines 689-716, word for word). The relay binding ("base predicate of the request's environment, not W3-defined, a
regulated one included; not a declared open term; no repeat") against 8.4 (lines 787-793); Lean's order is added
(8.3's A5 reasoning). The fixture values against 11.7 (lines 1000-1004) and 11.8's `undeclaredEvaluative_iff` row
(line 1020). The report wording ("these words match the catalogue; review them") is only in the docstrings, and no
line displays it, against D15 and the task ("no reader-facing wording").

Not covered: whether a listed word is a judgment in its context. That is a named open residual, and it is never counted
as semantic coverage. Size: 642 hand-written lines changed (added plus removed; 629 added) outside generated files, the saved trust mutant
evidence and this report (`git diff --numstat` against the merge base): Lean 131, Lean fixtures and examples 140,
tests 153, side tables, docs and evidence 218. That is just over the ~600 line. The checks added to kill the trust survivors (+28) and the
service-level fixture file (+61) are what push it over; no deliverable was added.

Pilot bytes: 0 expected (no unit changes status; the field is review information).

Next: jt-3 (the declaration, legend and status lines and 9.5's text, after jt-e1s), jt-3p (phrase rows), then jt-4.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS. `tests/test_judgments_undeclared.py::test_every_mutant_of_the_field_is_refused` retypes the field and each member
   (7, true, null, {}, 1.5, "\ud800", "", [[]], a 10k-deep list), and `relay_mutation_gate.py --route service:document`
   drops, empties, duplicates and retypes every field ("0 failures"). A bad byte on stdout belongs to the transport,
   which this item does not change (`tests/test_lean_service.py`, selected and passed).
2. Deliverables and rule breaks: PASS. See the plan rows above. Not delivered, each by DRI ruling: "good judgment"
   (jt-3p) and 9.5's text (jt-3). No Python copy of a Lean decision: `_undeclared_bound` checks membership, order and
   repeats only, never a match. No new permanent report test. In-flight overlap (`git diff --name-only main...<branch>` over every `lean-first/*`, `feature/*`,
   `infra/*` and `foundation/*` branch, for every file touched here):
   - feature/pc-1 edits `lean/VE/Service/Document.lean` (near `check` and `encode`) and
     `lean/ResponseShape/Encoders/Document.lean` (`document_fits` becomes `body_fits`). SYNTHESIS 4.2 (line 337) queues
     the document mode "in landing order", so whichever lands second merges; both edits are additive.
   - The shared ledgers `tools/trust-classes.json`, `ve/assurance-manifest.json` and the import list `lean/VE.lean`
     are also edited by feature/cmp-s4a, pc-6a, qt-a3db, sc-2d, wg-6a, pk-1-conditions and foundation/me-1.
   - The generated files are not an overlap (R12).
3. Tests can fail: PASS. `mutants.json` (S1-S6, P1-P3); `trust-mutants.json` (0 survivors, 0 unknown).
4. Lean and Python agree, valid inputs pass: PASS. `tests/test_judgments_undeclared.py::test_lean_lists_the_catalogue_matches_that_are_not_bound` (the
   genuine answers are relayed; the vocabulary written out of key order comes back in Lean's order), and
   `::test_a_vocabulary_at_the_predicate_limit_is_reported_whole`. Rust is untouched (N.A.).
5. R8 binding: PASS. `tests/test_judgments_undeclared.py::test_every_mutant_of_the_field_is_refused` covers `absent`, a sort, a unit id, a W3-defined
   name, a bound judgment, a doubled member and a case-shifted name. `::test_which_predicates_match_is_lean_s` covers
   the empty list (accepted: Lean's decision), out of order and repeated. `::test_the_field_is_there_exactly_under_the_profile`
   covers an extra member.
6. Gate evidence on the final HEAD: PASS for this item's evidence. `trust-mutants.json` is at `8f302d6d5`, and later
   commits change no Lean file except the evidence; the selected run is on `b50349522`. Not synced with main: the
   chain's gate and the merge train run on the merge candidate.
7. No unsigned item: PASS. DELTA rows cite R3 and R16; no signature is reserved.
8. Every user-visible change in DELTA: PASS. The one changed answer is the new member. The English `actions_version`
   36 is the lock's version rule for a new trusted grammar file, as in jt-2c (35). The ask fixtures and the S3
   comparison were re-recorded with field diffs (above).
9. Selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_judgments_undeclared.py`,
   `tests/test_judgments_answer.py`, `tests/test_judgments_exercised.py` and `tests/test_assurance_manifest.py`; seeded
   S6 and P1-P3 fail `tests/test_judgments_undeclared.py`.
10. Lean statements: PASS. `undeclaredEvaluative_iff` is spec 7's text. The encoder theorem `undeclared_fits` is
    about the encoded member, and `document_fits` covers `encode`. S1-S3 break the iff proofs. The schema's fingerprint
    #guard changes with the shape. No statement checker exists for this spec (`tools/check_*_statements.py` has none
    for judgment terms).
11. Budgets: N.A. The report has no budget of its own. Its size is the vocabulary's, under `max_predicates`:
    `tests/test_judgments_undeclared.py::test_a_vocabulary_at_the_predicate_limit_is_reported_whole` (256 answered whole; 257 `ResourceLimit`).
12. CPU: PASS by construction, not timed. One pass over the base predicates, each word list computed once, times 15
    rows. The 256-predicate fixture answers. No pilot was timed.
13. Test-removed trailers: PASS. `tools/gate_collection.py --check --prebuilt`: "0 removed by a trailer, 0 refused, 0 stale
    and 0 malformed".
14. Both directions, cited evidence, spec re-read: PASS. `::test_a_bound_judgment_listed_is_refused_and_unbound_it_is_relayed`,
    `::test_a_regulated_predicate_is_listed_and_still_not_admitted` (listed, yet `JudgmentRegulated`),
    `::test_the_field_is_there_exactly_under_the_profile`. Each claim above names its command; the spec re-read is
    listed under "Checks run".
