# fid-mech-b4: structural and wording mutants, mutant records, equivalence and declarations (build report)

**Status:** built; review F1 (B, widen-quantifier) fixed in fcf2aae834 (section 15), ready for recheck. **Branch:** infra/fid-mech-b4, base main b00f97f5c2 (main has not moved).
**What changed:** tools/fidmech/{structural,mutants,fp1}.py are new; wording.py is moved in from manage-agents with a harness mode; there are three actors.json and three empty equivalents.json files; and a CLI (`mutants`, `actors`).
**Open:** the install read (section 7) waits for the decider. **DRI signature:** none reserved. DELTA is none and trust is +0.
**Not run here:** the full gate (the chain runs it on the final HEAD) and a mutant run on VM1 (B5's job).

SIZE: 952 product, 686 tests, 52 other hand-written lines (after the F1 fix: structural.py +25/−13, tests/test_fidmech_prune.py 119). Product is structural.py 290, mutants.py 419, fp1.py 90, `__main__.py` +61/−3 and wording.py +91/−16 against the verbatim copy e6aa6effb9. The 356 moved lines and the copied fixture data are not counted. "Other" is the fixture rules (20) and the actors review script (32). There is no seam cut: the operations seat's override 1 sets no line cap, and every deliverable passes its own tests.

## 1. Deliverables (task DO list; plan rev 2 sections 2d, 5.1, 5.2, 9, 10; decision item 1)

| task line | delivered by | test |
|---|---|---|
| (1) structural.py: the 8 ops, made on the parsed form and written back as VE English | `structural.ops_of`, `render`, `mutants.structural_mutants` (68aa6a24f8) | `test_each_op_writes_its_expected_mutant_back_as_ve_english[<op>]` x8 |
| (1) guard templates use the rule's own bound variable and sort | VE's `render_rule_sentence` writes the edited Norm, so the subject is named by its sort | `test_the_guard_template_names_the_bound_variables_sort` |
| (1) add-guard-true: a unary base predicate of the sort, true in an item selecting the rule, used nowhere in the rule | `structural.guard_candidates` + the `used` filter in `ops_of` | `test_add_guard_true_never_picks_a_predicate_the_rule_uses` (FSF f4-check-r shape) |
| (1) drop-exception: the PRECEDENCE pairs and the header-declared exceptions | `structural_mutants` (PRECEDENCE read with `ast.literal_eval`), `EXCEPTION_HEADER` | `test_a_header_declared_exception_and_its_precedence_pair_are_each_dropped` |
| (1) plan-2d record; `find` occurs once; file_sha256 per edit; stillborn counted and listed, never scored | `mutants.record`, `line_edits`, `rule_edit`, `scorable` | `test_an_edit_widens_until_its_find_occurs_once`, `test_a_record_refuses_a_find_that_is_not_unique_a_stale_sha_and_overlapping_edits`, `test_every_find_occurs_once_and_every_mutant_parses_to_its_edit`, `test_stillborn_records_are_never_scored`, `test_wording_mutants_are_scored_never_equivalent_and_stillborn_ones_are_listed` |
| (1) real counts per document and op | `python -m tools.fidmech mutants --doc <doc>` | section 2; docs/infra/fid-mech-b4/counts-*.txt |
| (2) `equivalent` only for structural ops; `syntactic` only for a change to the rule file alone, compared through SoftRule.to_dict with and/or operands sorted recursively and `over` kept | `structural.canonical_rule`, `syntactic`, `mutants.rule_equivalence`, the guard in `mutants.record` | `test_two_conjuncts_reordered_are_syntactic`, `test_flip_force_is_never_syntactic`, `test_canonicalisation_sorts_nested_and_or_operands_and_keeps_over`, `test_a_wording_mutant_is_never_equivalent` |
| (3) `declared:<reason>` bound to the id and to sha256(edits + fp-1 of the unit + facts.d1.ve + PRECEDENCE + bindings.json); equivalents.json and the commit left out; a stale entry is reported, not applied | `mutants.binding_inputs`, `binding`, `apply_declarations`, `load_declarations` | `test_a_bound_declaration_applies`, `test_a_declaration_stops_applying_when_what_it_rests_on_changes[fp1,facts,precedence,bindings]`, `..._when_the_mutants_edits_change`, `test_each_binding_input_alone_changes_the_binding[x4]`, `test_equivalents_json_and_the_commit_are_left_out_of_the_binding` |
| (3) fp-1 ported, with a golden test against fp1.json (sha256 2a0a6dcb...) | tools/fidmech/fp1.py; tests/data/fidmech/fp1-golden.json and fp1-inputs/ | `test_fp1_equals_uc_audits_values_on_the_frozen_inputs` (45 FSF units at 0f6d59d441) |
| (3) equivalents.json shipped as `[]` | usecases/*/fidmech/equivalents.json | `test_b4_ships_no_declaration[x3]` |
| (4) wording.py moved; plan()/apply() byte-compatible; ACTORS unchanged; golden on frozen inputs | e6aa6effb9 (verbatim copy) + 68aa6a24f8; tests/data/fidmech/wording-golden.json | `test_plan_and_apply_give_the_bundles_output_on_the_frozen_inputs[x3]`, `test_actors_is_unchanged` |
| (4) harness enumeration as new functions; a case-aware actor matcher reading actors.json | `wording.harness_candidates`, `actor_pattern`, `load_actors`, `propose_actors`; `mutants.wording_mutants` | `test_the_actors_json_matcher_finds_an_actor_the_legacy_list_cannot[PF,FSF]`, `test_the_matcher_reads_a_first_letter_in_either_case_and_nothing_else`, `test_an_actors_json_whose_list_is_not_generated_less_removed_plus_added_is_refused`, `test_the_actors_command_checks_and_rewrites_the_generated_list` |
| (5) the generator version and the mutant ids/edits enter inputs_sha256 | `mutants.document_mutants` calls B3's `collect_inputs(generator_version="fidmech/1", mutants=...)` | `test_the_generator_version_and_mutant_edits_enter_inputs_sha256`; real value in section 6 |
| (6) install read: uc-audit-blind.py.new-fidmech + test; msg.sh dri | manage-agents tools-local/ (section 7) | tools-local/test-uc-audit-blind-fidmech.py: exit 0 on the .new, exit 1 on the installed file |

Every new test fails on main: `git ls-tree main tools/fidmech/` lists no structural.py, mutants.py, fp1.py or wording.py, so each new test file fails to import there. The seeded bugs (section 9) show that each test also fails on a wrong behaviour.

## 2. Structural mutants (plan 5.1)

**The parsed form.** Each rule line is parsed by `ve.norm_english.parse_english` (Lean) into a SoftRule. An op edits the parsed Norm (guard, unless, mode) and `render_rule_sentence` writes it back on one line. The written line is parsed again, and it counts as `ok` only if its core and mode equal the edit (`structural.same_edit`).
- A line VE refuses, or one that parses to another rule, is `stillborn`.
- A parse that gets no answer (CheckerUnavailable) is `stillborn` with the reason prefix `undecided:`. It is never scored either way.
- Any other exception propagates (2e5a79bcf9; `test_an_unanswered_parse_is_undecided_and_unscored_and_any_other_error_propagates`).
- A rule the renderer cannot write back is listed as `unrenderable` and gets no ops. There are 0 in all three documents.
- The renderer writes "both of the following hold" where an author wrote "all of the following" (a round-trip probe of every rule, not committed: RSP 0 of 76 lines differ once line breaks are joined, FSF 6 of 45 and PF 18 of 91 differ only so). Those mutants' lines therefore differ in that wording too, which has the same parse.

**Counts** (`uv run python -m tools.fidmech mutants --doc <doc>`; docs/infra/fid-mech-b4/counts-<doc>.txt). The columns are mutants / stillborn / syntactic / duplicates. The plan's RSP figures were estimates.

| op | RSP | PF | FSF |
|---|---|---|---|
| drop-conjunct | 61 / 0 / 0 / 5 | 141 / 0 / 0 / 0 | 60 / 0 / 0 / 2 |
| drop-unless | 3 / 0 / 0 / 0 | 4 / 0 / 0 / 0 | 8 / 0 / 0 / 0 |
| drop-disjunct | 2 / 0 / 0 / 0 | 8 / 0 / 0 / 0 | 18 / 0 / 0 / 0 |
| drop-exception | 3 / 0 / 0 / 0 | 8 / 0 / 0 / 0 | 2 / 0 / 0 / 0 |
| flip-force | 73 / 0 / 0 / 0 | 91 / 0 / 0 / 0 | 41 / 0 / 0 / 0 |
| add-guard-true | 10 / 0 / 0 / 0 | 63 / 0 / 0 / 0 | 16 / 0 / 0 / 0 |
| rule-drop | 76 / 0 / 0 / 0 | 90 / 0 / 0 / 1 | 44 / 0 / 0 / 1 |
| widen-quantifier | 5 / 0 / 0 / 0 | 0 | 2 / 0 / 0 / 0 |
| rules, and the reason a rule has no add-guard-true | 76; 39 in no item, 27 with no unused true predicate | 91; 0 in no item, 28 with no unused true predicate | 45; 11 in no item, 18 with no unused true predicate |

- **Against the plan's estimate:** RSP shows 61 drop-conjunct plus 5 widen (estimate 67), 3 drop-exception (3), 73 flip-force (76), **10 add-guard-true (estimate 76)**, 76 rule-drop (76) and 5 widen (about 4).
- **Why add-guard-true is 10, not 76.**
  - 39 of RSP's 76 rules are selected by no item, as Opus point 9 says.
  - Of the 37 selected rules, 27 are selected only by items whose case model holds no unary base situation predicate the rule does not already use. In a typical RSP case model, the predicates that hold are exactly the guard's own.
  - So no invented guard that the probed cases satisfy exists for those rules. The figure is a measurement, not a defect.
- **flip-force on a plain predicate:** three RSP rules (f8-public, f8-internal, f8-autonomous) and four FSF rules use a plain predicate, which carries no force. VE refuses a default rule on it ("A default rule needs a declared obligation or permission act"), so these rules get no flip-force.
- **Duplicates** are kept once, under the narrower op (`KEEP_FIRST`):
  - RSP's 5 widen-quantifier mutants each equal a drop-conjunct of the one restricting conjunct.
  - FSF f3's and PF f11-exception's rule-drop equal their header-exception drop.
- **Syntactic:** 0 in every document. No op of the table reorders operands.
- **inputs_sha256 in each counts file:** the counts files were written while they themselves were uncommitted, so those values bind that state. A clean-tree value is in section 6.

## 3. Equivalence and declarations (plan 2d; Opus round 2 points 4 and 9)

**Syntactic equivalence.**
- `syntactic` is set only when every edit is to rules.d1.ve and every changed rule's parse equals the original after `canonical_rule`.
- `canonical_rule` takes `SoftRule.to_dict()` (mode, rank, exception and `over` kept), flattens every and/or chain and sorts its operands by canonical JSON, recursively.
- `test_flip_force_is_never_syntactic` shows both sides of point 9. For a flip-force mutant, `Norm.to_dict()` is equal to the original's (`rule.core.to_dict() == flipped.core.to_dict()`) while `syntactic` is False. Every flip-force record in both fixtures has `equivalent: null`.
- Seeded bug 4 (comparison through `core.to_dict`) makes that test fail.

**Declarations.**
- An entry is `{"id", "reason", "binding"}`.
- `binding` is the sha256 of the canonical JSON of `{"edits", "fp1": fp-1 of the unit, "facts_sha256", "precedence": the PRECEDENCE literal as sorted pairs, "bindings_sha256"}`.
- `edits` are the record's own, file_sha256 included. That is the literal reading of "the mutant's edits", and the narrower one: any other change to the edited file also makes a declaration stale.
- equivalents.json and the commit are in no input (`test_equivalents_json_and_the_commit_are_left_out_of_the_binding`: a second entry and a new commit leave the declaration applied).
- A declaration that does not match is reported, not applied:
  - a stale binding is reported as `stale`;
  - an unknown id as `unknown`;
  - a declaration of a wording mutant as `not-structural`;
  - one on an already syntactic mutant as `already-equivalent`.
- B4 ships `[]` in all three documents and makes no declaration.

## 4. fp-1 (tools/fidmech/fp1.py)

- The port follows uc-audit.py `fingerprints_of` (:1246) and its helpers `_semantic`, `_unit_shared`, `rule_blocks`, `legend_raw` and `_fp`.
- It reuses `wording._used` for `used_predicates`, which is the same function (one owner).
- **Golden.** tests/data/fidmech/fp1-golden.json copies the 45 FSF values at commit 0f6d59d441 from manage-agents reviews/fid-mech-harness/inputs/fp1.json (sha256 2a0a6dcb9e1f94ecce820bbcfe4a6deef4107435ce51417cbe4c829c0c35988b, checked with `sha256sum`).
- The inputs are FSF's 7 semantic files at that commit (`git show`), under tests/data/fidmech/fp1-inputs/. A `.py` file is stored as `.py.txt`, as B3 stored run.py.txt.
- No other file of that directory was read.

## 5. Wording (plan 5.2, 9)

**The move.**
- e6aa6effb9 copies tools-local/wording-mutants.py (sha256 ae53257d...) in byte for byte.
- 68aa6a24f8 and later commits add the following; the default path is unchanged:
  - VE as the owner, in the docstring;
  - `actors`/`pattern` parameters on `actor_cands`;
  - an `actors`/`pattern`/`structural` parameter on `candidates`;
  - the harness functions.
- In a swap, `actor_cands` now uses the matched text. With `_wb` and ACTORS that text equals the list entry, so output is the same.
- **Golden.** It holds plan() for seeds 1-5 (n = 10) on each document's frozen rules.d1.ve, vocabulary .py and environment.d1.json, and the sha256 of each file apply() writes for each planned mutant (150 mutants). It was recorded from the manage-agents copy by docs/infra/fid-mech-b4/record-wording-golden.py.txt. The moved copy gives the same output (`test_plan_and_apply_give_the_bundles_output_on_the_frozen_inputs`).

**Harness mode.**
- `harness_candidates(files, unit, actors)` gives every wording candidate (actor, qualifier, quantity, attachment) of a unit with the case's actors. `mutants.wording_mutants` turns each one into a record:
  - the edits are line runs, widened until each `find` is unique;
  - identical edits are kept once;
  - parse is checked by building the mutated environment and parsing every changed rule line and every rule that uses the mutated predicate.
- The actor matcher reads a phrase's first letter in either case ("The SAG" is "the SAG") and nothing else.
- A replacing actor holds no "and" or "or": VE refuses an act phrase with a logic word, so such a mutant could only be stillborn. The full actors list is still used for matching.

**actors.json.**
- Each file is generated by `propose_actors`: capitalised phrases ending in an acronym, a role head or a CamelCase name; every ACTORS phrase found; and role noun phrases with at most one modifier.
- Each file was then reviewed (docs/infra/fid-mech-b4/actors-review.py.txt). Each holds `generated`, `removed` and `added`, each entry with a reason, and `actors`. `load_actors` refuses a file whose `actors` is not generated − removed + added.
- **Removed by hand:**
  - **PF (8):** improved public, ARA, AI, ET, US, Employees, The SAG Chair, SSC. SSC is an alias of "the Safety and Security Committee" in the same legend, so swapping the two changes no actor.
  - **FSF (9):** the CBRN, the CCL, CCA, CCL, SEC, TCL, AI, appropriate government, overall public.
  - **RSP (15):** comprehensive public, provide public, made public, Public, public, manipulate users, sabotage users, hundred employees, Misaligned AI, AI, the RSP, Actors, Competitors, this group, these competitors.
- **Added by hand:** FSF "Google", the developer the legends name ("restricted to Google"), a plain capitalised word the generator does not take.
- **Lists:** PF 15 actors (23 generated), FSF 10 (18), RSP 46 (61).

**Actor mutants per document** (counts files; docs/infra/fid-mech-b4/actor-candidates.txt):

| document | actor mutants (ok / stillborn / duplicates removed) | legacy candidates() actor rows | harness actor rows | units with a harness actor row and no legacy one |
|---|---|---|---|---|
| RSP | 57 (48 / 9 / 14) | 44 | 71 | 11 |
| PF | 53 (46 / 7 / 60) | 5 | 113 | 64 |
| FSF | 14 (14 / 0 / 22) | 0 | 36 | 20 |

- The other wording mutants (mutants / stillborn) are:

  | kind | RSP | PF | FSF |
  |---|---|---|---|
  | qualifier | 97 / 1 | 24 / 0 | 23 / 0 |
  | quantity | 44 / 0 | 30 / 0 | 27 / 0 |
  | attachment | 4 / 0 | 1 / 0 | 1 / 0 |

- The one RSP qualifier stillborn is `undecided` (f10-attempt-strict:qualifier:1, CheckerUnavailable "changed source predicate").
- The 16 actor stillborns are VE's "invalid act phrase" refusals of the replaced act. They are counted and listed, never scored.

## 6. inputs_sha256 (plan 2e, B3's records.py)

On a clean tree at commit 732ebf412e (`git status` empty before and after), `uv run python -m tools.fidmech mutants --doc anthropic-rsp` prints `inputs_sha256 bbe3c9d1f1b9317e7ad221eee90d21e85cf3a31cd43431c7ac9f69649ecd743e` (docs/infra/fid-mech-b4/inputs-sha256-rsp-clean.txt). It covers 435 mutants with generator `fidmech/1`. The counts are identical to counts-anthropic-rsp.txt (diff: one blank line).

## 7. Install read (plan 9; DRI install-read rule)

Built in manage-agents and **not installed**. tools-local/wording-mutants.py is not deleted.
- `tools-local/uc-audit-blind.py.new-fidmech` (sha256 b8de1637...) is a copy of the installed uc-audit-blind.py (sha256 27edef7d..., 2026-11-13; no other .new pending) with 3 changed lines:
  - `wm()` loads `VE / 'tools' / 'fidmech' / 'wording.py'`, where VE is the bundle's pinned checkout /home/seyran/code/verifiable-english, instead of `M / 'tools-local' / 'wording-mutants.py'`;
  - its docstring and the module docstring name the new owner.
  - `python3 -m py_compile` passes.
- `tools-local/test-uc-audit-blind-fidmech.py` (sha256 c8644747...) loads a uc-audit-blind.py and checks two things: that `wm()` loads `<VE>/tools/fidmech/wording.py`, and that its plan()/apply() give wording-golden.json on the frozen inputs (3 documents x 5 seeds).
  - `python3 -I tools-local/test-uc-audit-blind-fidmech.py --ve /home/seyran/code/ve-fid-mech-b4` exits 0 ("all checks pass").
  - The same command on the installed `tools-local/uc-audit-blind.py` exits 1: "FAIL uc-audit-blind.py: the generator is .../tools/fidmech/wording.py (loaded: .../tools-local/wording-mutants.py)".
- Until fid-mech-b4 merges, VE main has no tools/fidmech/wording.py. The .new would then load no generator, which fails closed, so it is installed only after the merge.

## 8. Tests

New files:
- tests/test_fidmech_structural.py: 16 tests, all marked `needs_lean`, B3's skipif on lean/.lake/build/bin/ve_service, as a module `pytestmark`.
- tests/test_fidmech_mutants.py: 25 tests, no Lean.
- tests/test_fidmech_wording.py: 13 tests. One is `needs_lean`: `test_wording_mutants_are_scored_never_equivalent_and_stillborn_ones_are_listed`.
- tests/test_fidmech_prune.py (review F1): 5 tests, 10 ids. Three need no Lean (`prune` on every tree shape up to six leaves and every subset of leaves; `drop` = `prune` of one path; the reviewer's two stale-path shapes). Two are marked `needs_lean` per test, because they parse rows-cond: the probe and every bracketing of up to five conjuncts through `ops_of`.

The new tests contain neither of the two texts the fidq step selects on.

**Plant table (task test → class it kills)**

| task test | test | class |
|---|---|---|
| per op on a 4-6 block fixture, one expected mutant each | `test_each_op_writes_its_expected_mutant_back_as_ve_english[...]` x8 (5 RSP blocks, 3 FSF rule blocks and a premise block) | the op's edit is wrong |
| guard template uses the bound variable's sort | `test_the_guard_template_names_the_bound_variables_sort` | a hard-coded "that situation" |
| add-guard-true never a used predicate (FSF f4-check-r) | `test_add_guard_true_never_picks_a_predicate_the_rule_uses` | `A and A` |
| `find` unique | `test_an_edit_widens_until_its_find_occurs_once`, `test_a_record_refuses_a_find_that_is_not_unique_a_stale_sha_and_overlapping_edits` | non-unique find |
| stillborn listed and unscored | `test_stillborn_records_are_never_scored`, `test_wording_mutants_are_scored_never_equivalent_and_stillborn_ones_are_listed`, `test_an_unanswered_parse_is_undecided_and_unscored_and_any_other_error_propagates` | stillborn scored |
| two conjuncts reordered → syntactic | `test_two_conjuncts_reordered_are_syntactic` | no canonical sort |
| flip-force never syntactic | `test_flip_force_is_never_syntactic` | Norm.to_dict comparison |
| actor-swapped act → scored, never equivalent | `test_wording_mutants_are_scored_never_equivalent_and_stillborn_ones_are_listed`, `test_a_wording_mutant_is_never_equivalent` | an equivalent wording mutant |
| declaration applies when bound; stops on edits / fp-1 / facts / PRECEDENCE / bindings.json | `test_a_bound_declaration_applies`, `test_a_declaration_stops_applying_when_what_it_rests_on_changes[4]`, `..._when_the_mutants_edits_change` | stale applied; an input left out |
| no change when only equivalents.json or the commit changes | `test_equivalents_json_and_the_commit_are_left_out_of_the_binding` | circular binding |
| fp-1 golden | `test_fp1_equals_uc_audits_values_on_the_frozen_inputs` | port differs |
| wording golden | `test_plan_and_apply_give_the_bundles_output_on_the_frozen_inputs[3]` | plan/apply output differs |
| actors.json matcher finds a PF and an FSF actor that ACTORS cannot | `test_the_actors_json_matcher_finds_an_actor_the_legacy_list_cannot[openai-preparedness-f7-compile-the SAG, safety-framework-f14-governance function]` | matcher reads ACTORS |

**Condition tests, all selected and passing in the selected run** (docs/infra/fid-mech-b4/selected-run.txt, "exit 0"):
- B1-B3's: tests/test_fidmech_segment.py, test_fidmech_l1.py, test_fidmech_b2.py, test_fidmech_data.py, test_fidmech_bindings.py, test_fidmech_adapters.py (1139 s), test_fidmech_worker.py, test_fidmech_records.py;
- tests/test_rsp_fidelity_fix.py;
- this batch's tests/test_fidmech_structural.py, test_fidmech_mutants.py and test_fidmech_wording.py.

## 9. Seeded bugs (docs/infra/fid-mech-b4/seeded-bugs.json; replay script seeded-bugs.py.txt)

Python is the only language changed: no Lean, no Rust. 18 plants were each applied, run against their named test and restored; all 18 were killed. They ran at b320272017, and the tree was clean after each. 2e5a79bcf9 later changed only exception handling, and all 18 plant sites still occur exactly once at HEAD (checked by script).

**Review fix (F1):** the fix rewrote `drop` as `prune` of one path, so plant 1's site moved to `_prune` (the collapsed parent keeps the dropped leaf, not its sibling). Plants 1, 19 and 20 were replayed with the script (`uv run python docs/infra/fid-mech-b4/seeded-bugs.py.txt '<bug prefix>'`) on fcf2aae834's tree, and all three were killed. All 20 plant sites occur exactly once in the working tree (checked by script), and structural.py was byte-identical to its backup after the replays.

| # | file | plant | killed by |
|---|---|---|---|
| 1 | tools/fidmech/structural.py | drop-conjunct drops the sibling (site moved into `_prune` by F1; replayed) | test_each_op_writes_its_expected_mutant_back_as_ve_english (3 failed), test_fidmech_prune.py::test_drop_is_prune_of_one_path_on_and_and_or_trees |
| 2 | tools/fidmech/structural.py | add-guard-true takes a used predicate | test_add_guard_true_never_picks_a_predicate_the_rule_uses |
| 3 | tools/fidmech/structural.py | a hard-coded "that situation" | test_the_guard_template_names_the_bound_variables_sort |
| 4 | tools/fidmech/structural.py | equivalence through Norm.to_dict | test_flip_force_is_never_syntactic |
| 5 | tools/fidmech/structural.py | no sort of and/or operands | test_two_conjuncts_reordered_are_syntactic |
| 6 | tools/fidmech/mutants.py | header exception not read | test_a_header_declared_exception_and_its_precedence_pair_are_each_dropped |
| 7 | tools/fidmech/structural.py | widen restricts the subject | test_each_op_writes_its_expected_mutant_back_as_ve_english (2 failed) |
| 8 | tools/fidmech/mutants.py | an edit not widened to a unique find | test_an_edit_widens_until_its_find_occurs_once |
| 9 | tools/fidmech/mutants.py | a find occurring twice accepted | test_a_record_refuses_a_find_that_is_not_unique_a_stale_sha_and_overlapping_edits |
| 10 | tools/fidmech/mutants.py | a wording mutant may be equivalent | test_a_wording_mutant_is_never_equivalent |
| 11 | tools/fidmech/mutants.py | stillborn mutants scored | test_stillborn_records_are_never_scored (+ the Lean wording test) |
| 12 | tools/fidmech/mutants.py | equivalents.json folded into the binding | test_equivalents_json_and_the_commit_are_left_out_of_the_binding |
| 13 | tools/fidmech/mutants.py | bindings.json left out of the binding | test_a_declaration_stops_applying_when_what_it_rests_on_changes[bindings] |
| 14 | tools/fidmech/mutants.py | a stale declaration applied | test_a_declaration_stops_applying_when_what_it_rests_on_changes (5 failed) |
| 15 | tools/fidmech/fp1.py | build_document.py not shared | test_fp1_equals_uc_audits_values_on_the_frozen_inputs |
| 16 | tools/fidmech/wording.py | apply() re-dumps with indent 1 | test_plan_and_apply_give_the_bundles_output_on_the_frozen_inputs (3 failed) |
| 17 | tools/fidmech/wording.py | one ACTORS entry dropped | test_plan_and_apply_give_..., test_actors_is_unchanged |
| 18 | tools/fidmech/wording.py | harness matches ACTORS, not actors.json | test_the_actors_json_matcher_finds_an_actor_the_legacy_list_cannot (2 failed) |
| 19 | tools/fidmech/structural.py | F1: widen drops its restricting conjuncts one path at a time (the pre-fix code, as a reduce) | test_fidmech_prune.py::test_probe_f1_two_restricting_conjuncts_are_dropped_together, ::test_widen_quantifier_keeps_exactly_the_non_restricting_conjuncts_on_every_shape (2 failed) |
| 20 | tools/fidmech/structural.py | F1 class: `_prune` ignores a second path in the same walk | test_fidmech_prune.py::test_prune_keeps_exactly_the_other_leaves_in_order_for_every_shape_and_subset[5,6], ::test_the_reviewers_two_stale_path_shapes (6 failed) |

My first plant for #12 survived, and it was a bad plant. It added a key to `binding_inputs` that `binding()` never reads, so it changed nothing. The replant puts equivalents.json's sha where the hash reads it, and it is killed.

**trust_mutants:**
- The light lane prints `NOT 12111 changed lines outside generated files > 150 (41 files)`. Most of those lines are frozen fixture data.
- `uv run python tools/trust_mutants.py --plan` (a plan, which may be run directly) prints `{"definitions": 0, "mutants": 0, "to_run": 0}` (docs/infra/fid-mech-b4/trust-mutants-plan.json).
- No Lean changed, so there is nothing to sweep and no sweep was run.

## 10. Test runs

- **Selected run, once:** `mac-pytest.sh --select -- --base b00f97f5c2 --run` on a2c27c6281, run on ve-cloud-2.
  - 268 units: 267 exit 0 and 1 exit 1. The failing unit was tests/test_history_tests.py, 2 tests: the generated tests/history-dependent.json did not yet list the new tests and the CLI tests that now reach records.py's git.
  - Fix: `python tools/history_tests.py --write` (its generator, b320272017; again in d93f85ef4a for test_fidmech_wording.py). Then those 2 failed ids passed ("2 passed in 52.70s"), and `--check` exits 0.
- **After later code changes:**
  - 2e5a79bcf9 (exception narrowing) and d93f85ef4a (the actors CLI test): I reran only the tests of that code. tests/test_fidmech_mutants.py gave 25 passed; tests/test_fidmech_structural.py and test_fidmech_wording.py gave 28 passed; the new actors CLI test gave 1 passed.
  - The CLI tests of the condition files (`main()` in segment, l1 and b2) gave 36 + 3 passed.
- **Other checks:**
  - `uv run python tools/regen_generated.py --check` exits 0. It warns only "codemap is stale (regenerated on merge)", as on B3.
  - `select_tests` picks every condition test file and the three new files.
- **Pre-existing red:** main-known-red.txt lists four tests (lean_service sub-tick x2, rd8 report, ownership_floor FSF adapter). I touched none of them. tests/test_lean_service.py and tests/test_readings_defaults_rd8_report.py were in the selection and exited 0 on ve-cloud-2; tests/test_ownership_floor.py was not selected (selected-run.txt, /tmp unit list).

## 11. Decisions inside the plan (each the conservative or narrower reading; no DRI question)

1. **flip-force flips the mode** (strict ↔ default). VE fixes a predicate's role in its vocabulary entry, so "may ↔ must" and "need not ↔ must not" (role crossings) have no parsed form, and VE refuses those lines. A plain predicate has no force, so it gets no flip.
2. **A header-declared exception** is a header whose text outside quotes says "exception to". PF f11-exception-deploy's header says "the exception also covers", so it is not read as one. Its always-false-guard mutant still exists, as its rule-drop.
3. **add-guard-true adds one predicate per rule:** the one true in the most selecting items (then by name), on the subject (the first argument). The plan's wording "at least one item" holds.
4. **rule-drop and header exceptions use the always-false guard** ("if this is impossible"; ast.Bottom). They do not delete the block, which would break run.py's references.
5. **Identical edits are kept once, under the narrower op** (KEEP_FIRST). Duplicates are counted.
6. **Wording mutants do not repeat across units.** An act mutation shared by several units is kept under the first unit, and duplicates are counted.
7. **A declaration's binding uses the record's edits with file_sha256** (section 3).
8. **The harness's replacing actors hold no logic word**, and SSC is removed as an alias (section 5).
9. **An unanswered parse is stillborn, marked undecided.** It is never scored, and it is never presented as a VE refusal.
10. **`seed` is null in harness records**, because the enumeration is exhaustive and nothing is sampled.

## 12. DELTA

None. This is Python tooling and data: no Lean line, no Rust line, no verdict, answer or translation changed, and no decision path replaced. Trust +0 and no signature is reserved. No DELTA.md is written, because there is no row. The harness only reports; it gates nothing.

## 13. Spec re-read

- **plan 2d record keys ↔ `mutants.RECORD_KEYS`.**
  - The keys, in plan order: id, document, unit, class, op, where, edits, equivalent, parse, seed, generator, inputs_sha256.
  - The `where` set: rule, act, legend, precedence, unless.
  - "find occurs exactly once" ↔ `record`.
  - "equivalent set ONLY for structural ops" ↔ `record`'s guard.
  - "syntactic when only the rule file changed and ... canonicalisation sorts the operands of commutative and/or, recursively, and keeps over/PRECEDENCE" ↔ `rule_equivalence` and `canonical_rule`.
- **plan 5.1 table ↔ `structural.OPS` and `ops_of`**, op by op. Two differences are recorded as decisions 1 and 2.
- **Opus round 2 point 4 ("bind each declaration to the sha of the mutant's edits plus item 44's fp-1 of the unit, facts.d1.ve, PRECEDENCE and bindings.json, and leave out equivalents.json and the commit") ↔ `binding_inputs` and `binding`.**
- **Point 9 ("Equivalence uses SoftRule.to_dict (ve/softnorms.py:133-146), never Norm.to_dict, and a fixture shows flip-force is never syntactic") ↔ `canonical_rule`** (`rule.to_dict()` on a SoftRule) and `test_flip_force_is_never_syntactic`.
- **plan 5.2 "case-aware matcher ... actors.json ... generated ... then reviewed"; "the legacy plan()/apply() path keeps ACTORS unchanged" ↔ `harness_candidates`, `propose_actors`, `load_actors`** and `test_actors_is_unchanged`.
- **plan 9 golden: "frozen copies of the input files: rules.d1.ve, the vocabulary .py and environment.d1.json of the three documents" ↔ tests/data/fidmech/wording-inputs/<doc>/**, with the vocabulary as `.py.txt`.

## 14. Notes for the DRI

- **add-guard-true is thin on RSP** (10 rules) because case models hold little beyond each rule's own guard. The blind spot it measures can only be measured where a case holds an extra true predicate. This is a property of the cases, not of the generator; widening the cases is translation work, outside the harness.
- **About 16% of the actor mutants are stillborn** (16 of 124): VE's act-phrase check refuses the replaced phrase. They are listed, never scored. A later generator could try the next replacing actor when VE refuses one; that would need Lean inside candidate enumeration, so it is not done here.
- **B3 review note C** (FSF atoms listed for items whose rules are also selected in a model without them) changes only which items count toward add-guard-true's "most items" order. It cannot produce `A and A`, because used predicates are excluded first.
- **Wording mutation of a predicate's act changes every unit that uses it.** B5's per-unit tables should credit such a mutant to the predicate's units, not only to the first one; the record keeps the first unit.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer and no new route. The harness reads VE's parse through the existing public `parse_english`.
2. PASS: section 1 maps every DO line to a commit and a test. There is no new Python copy of a Lean decision: equivalence compares VE's own parse, and `render_rule_sentence` and `parse_english` are VE's. There is no permanent report test (the counts are saved evidence, not tested), and no protected file was touched (`git diff --stat main...HEAD` has no quote_evidence.py, conftest, run.py, bindings.json or translation file).
3. PASS: 20 seeded bugs, all killed (seeded-bugs.json; 19 and 20 are review F1's). The opposite directions are covered by the plant table in section 8.
4. N.A.: no Python, Lean or Rust path pair changed. The wording golden compares the old and new copies byte for byte (`test_plan_and_apply_give_the_bundles_output_on_the_frozen_inputs`).
5. PASS (inputs): an undeclared declaration id is reported as `unknown`; a wording or already-equivalent target is refused (`test_a_declaration_names_a_structural_mutant_with_no_equivalence`); a malformed entry is refused (`test_a_malformed_declaration_is_refused`).
6. PASS: main has not moved (`git log HEAD..main` is empty); the chain gates the final HEAD.
7. PASS: no DELTA row, no trust growth (trust-mutants-plan.json, 0 definitions).
8. PASS: no user-visible change. There is no answer, translation or results.json change, and DELTA is none.
9. PASS: `select_tests` picks all 12 condition and new test files (section 10).
10. N.A.: no Lean.
11. PASS: no new deadline. Tests use no sleep or timeout (tests/test_hang_guards.py ran in the selected run). An unanswered parse is never ok (`test_an_unanswered_parse_is_undecided_and_unscored_and_any_other_error_propagates`).
12. N.A.: an offline tool, not on a check or render path.
13. PASS: no test removed or renamed.
14. PASS: opposite directions are tested (applies/stale; syntactic/not; matcher finds/does not overmatch; `actors --check` 0/1). Every claim names its command or evidence file. Spec re-read is in section 13.
15. PASS:
    - **overclaim:** the universal words in this report each name a test or an evidence file.
    - **cut deliverable:** none.
    - **every new check can fail:** section 9.
    - **limits:** N.A., no new limit.

## 15. Review fix (manage-agents fid-mech-b4-review.final.md; the overlapped review -ov.final.md has the same single finding)

| finding | class | fix | regression tests | commit |
|---|---|---|---|---|
| F1 (B) widen-quantifier dropped its restricting conjuncts one path at a time. Each drop collapsed a parent, so the remaining paths were stale: two restricting conjuncts crashed the run (AttributeError outside REFUSED), or a stale path on an Or leaf dropped half of it silently | several positional edits applied in sequence, each reading a tree the previous one reshaped | `structural.prune(formula, paths)` reads every path on the original tree in one walk. A parent left with one child becomes that child; no leaf left gives ast.Top. `drop` is `prune` of one path, and widen-quantifier calls `prune` once | tests/test_fidmech_prune.py: `test_probe_f1_two_restricting_conjuncts_are_dropped_together` (the probe), `test_widen_quantifier_keeps_exactly_the_non_restricting_conjuncts_on_every_shape`, `test_prune_keeps_exactly_the_other_leaves_in_order_for_every_shape_and_subset[1-6]`, `test_drop_is_prune_of_one_path_on_and_and_or_trees`, `test_the_reviewers_two_stale_path_shapes` | fcf2aae834 |

- **Probe F1:** before the fix it raised `AttributeError: 'Unary' object has no attribute 'right'` (structural.py `drop`). After it, the probe passes and is the test `test_probe_f1_two_restricting_conjuncts_are_dropped_together`.
- **Sweep (same class):** drop-conjunct and both drop-disjunct sites now go through `prune` and edit one path. `mutants.apply_edits` places every text edit at its `find` in the original file in one pass and refuses overlaps. No other site in tools/fidmech/ applies several positional edits one after another (grep for `reverse=True`, `drop(`, `_put(`, offsets).
- **Counts unchanged:** I reran `uv run python -m tools.fidmech mutants --doc <doc>` for all three documents on fcf2aae834. Each per-op table equals the saved counts-<doc>.txt; the only diffs are the saved files' `time` lines. As the review said, each real two-variable rule has at most one restricting conjunct, and `prune` of one path is the old `drop`. The inputs_sha256 changes by design, because it covers the commit and every file under tools/fidmech/ (records.py `collect_inputs`).
- **Checks on the fix:**
  - `mac-pytest.sh --select -- --base b00f97f5c2 --run` on fcf2aae834 plus the seeded-bug evidence ran on ve-cloud-2: 271 units, 0 failed, exit 0. It selected test_fidmech_prune.py, test_fidmech_structural.py and test_fidmech_mutants.py.
  - `lake build` completed (1475 jobs); `python3 lean/audit.py` gave PASS.
  - `regen_generated.py --check` and `history_tests.py --check` exit 0.
- **Pre-existing red** (main-known-red.txt): untouched. tests/test_lean_service.py and test_readings_defaults_rd8_report.py exited 0 in this selected run; test_ownership_floor.py was deferred to the chain gate.
- **DELTA:** none. Python tooling only: no Lean, Rust or `ve/` file, no verdict, translation or answer, so there is no DELTA row and no Ruling cell. No DRI signature is reserved.
- **Review notes (C, not filed):** not changed here. The three surviving seeded bugs the reviewer lists (the `used` unless predicates, the sort filter, the stillborn "parses to another rule" check) are missing test rows, and are left for a later item.
