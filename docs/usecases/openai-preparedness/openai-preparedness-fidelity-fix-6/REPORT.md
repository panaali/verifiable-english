# openai-preparedness-fidelity-fix-6: the three PF units both relay seats judged REAL

No DRI signature is reserved, no DELTA row and no question is open. All three units are fixed. No answer moved:
`run.py` gives 236 / 239 after each batch, and results.json is byte-identical to main's.

Ruling: addendum 9 items 58b, 59 and 61 (reviews/dri-decisions-20261112-audit-stability.md). The relay is
reviews/audit-newrule-fsfpf/pf-relay4/result.md. Also binding: lp1701 item 1 (a documented omission earns no credit),
addendum 2 items 13-14, addendum 6 item 41, and post-sprint plan section 1. The work starts from main 4a5d3460d3,
which already has fix-5 merged (dc67245e0a). No AMENDMENT line clears a unit. The one amendment, the kb-10b-switch
merge note, concerns run.py, and this item does not edit run.py.

Commits: 3750cbbb82 (batch 1), d9ef41082c (batch 2), then this REPORT.

## Units changed, by checklist class

| unit | finding (relay; source) | class it answers | fix |
|---|---|---|---|
| f15-third-party | C1/C5, (ii)/(ii): "OpenAI will work with third-parties to independently evaluate models" (pf-v2.txt:14) had become the required result "must have third parties independently evaluate the model" | 1, 5, 11 | The act `third_party_evaluation` is now "{0} work with third parties to independently evaluate the model" (59 characters, no reserved word). The rule reads "Every situation must work with third parties to independently evaluate the model, if both ...". The legend quotes 5.2's sentence in full. Both guards are unchanged: `deeper_testing_warranted` carries the deeming about a deployment (OT14), and `third_party_available` carries "when available and feasible". |
| f9-risk-paths | C1, (iv)/(iv): "We first identify the plausible ways ..." (pf-v2.txt:11); "first" was dropped and not recorded | 1, 11 | The legend of `risk_paths` quotes the whole sentence, "first" included. It is not a pointer legend. The act is unchanged: with "first" it would be 82 characters, and `canonicalAct` (lean/VE/Norms/Wire.lean:33) refused it ("invalid act phrase for risk_paths", from build_document.py). The header says event order (ET, as PLAN O7) is not formalised and names the word. The spans.json entry p11-u161 gets an `untranslated` record on the bytes of "first" (reason `event_order`, detail "ET: ...") and lists ET among its waits. |
| f9-specific | C1, (iv)/(iv): "For each of those, we then identify ..." (pf-v2.txt:11); "then" was dropped | 1, 11 | The same fix for "then". The legend of `specific_safeguards_per_path` quotes the whole sentence. "then" is a reserved word (`actReserved`, lean/VE/Acts/LexicalBase.lean:8), so it can only be in the legend. The header and p11-u162 (an `event_order` record on "then"; waits SC, ET) record the order. The per-item scope (C2) is unchanged: the header still says "SC-blocked", and the reason, detail and act are unchanged. |

No other block changed, and no shared predicate or legend was renamed. The three legends are the only ones changed.
Predicate names, guards and the run.py tables are unchanged. In particular, `K_ITEMS["THIRD_PARTY_EVALUATION"]` still
names `third_party_evaluation`.

Spec re-read:
- The f15 act against pf-v2.txt:14 and PLAN.md:281 (K14: "working with third parties to evaluate the model
  required").
- The f9 legends against pf-v2.txt:11 and PLAN O7.
- Both headers against the byte spans printed from the pinned source: "first" is once in p11-u161 and "then" is once
  in p11-u162 (`python3 -c` on pf-v2.txt[32521:32655] and [32655:32715]). The tests compare the recorded spans with
  those bytes.

## Batch 1: f15-third-party (PROJECTED)

- `cd usecases/openai-preparedness && uv run python run.py` at 3750cbbb82 gave "236 / 239 (1338.0 s)", and results.json
  was byte-identical to main's (the field-by-field compare printed nothing; `git status` was clean).
- VE answers: K14 ALL -> ALL (key ALL, agree). N3 NONE -> NONE (key NONE, agree). Stop-rule question 1 does not
  apply.
- **PROJECTED** union, from the relay re-score 87 passing / 93 failing on confirmed / 59 failing only on disputed (of
  239): **88 / 92 / 59**.
  - K14: failing (confirmed, f15-third-party) -> passing. According to the task's answer-to-unit table, K14 rests on no
    other failing unit.
  - N3: failing -> failing, because it rests on many other units.
  - This holds only if the re-read clears f15-third-party. K14 also needs the omission reads (see Notes 1).

## Batch 2: f9-risk-paths and f9-specific (PROJECTED)

- `run.py` at d9ef41082c gave "236 / 239 (1389.7 s)", and results.json is unchanged.
- **PROJECTED** union: **88 / 92 / 59**, unchanged by this batch. The only answer resting on these two units is N3:
  failing -> failing (it rests on many other units).

Nothing is claimed before the re-read.

## Regulated predicates

61 of 64: the same on main and on this branch, counted from environment.d1.json with a `python3 -c` count of
predicates that have `regulated`. No predicate is new.

## Generated files (each by its own script)

- `pf_vocabulary.py` wrote environment.d1.json.
- `build_document.py` wrote spans.json and coverage.json; the status totals are unchanged.
- `stage0.py` and `measure.py` wrote units.json and gaps.json:
  - ET: 29 units / 8,272 bytes -> 31 / 8,466.
  - JT alone: 12 / 2,193 -> 11 / 2,059.
  - SC alone: 24 / 3,759 -> 23 / 3,699.
- README's blocker table is hand-edited to match these, as in fix-5.
- `source/quote_evidence.py` left quote-hashes.json unchanged.
- run.py's results.json is unchanged.

Checks on the final code:
- `build_document.py --check`, `stage0.py --check` and `measure.py --check` each exit 0.
- `uv run python tools/regen_generated.py --check` exits 0 ("checked 41 entries").
- `usecases/safetyfw_accounting.py openai-preparedness --check` exits 0 with "0 of 117 quotes unanchored".

## Tests

New tests in tests/test_pf_fidelity_fix.py (5 passed):
- (a) `test_f15_third_party_act_is_openais_work_with_third_parties`. It also asserts that no act and no rule says
  "have third parties independently evaluate", and that K14 is still ALL = key.
- (b) `test_f9_selection_steps_carry_their_order_word_and_record_the_order_as_et`, for both units. It checks the
  legend quote, the header's ET sentence, ET in the waits, and the `event_order` record whose span is exactly the
  word's bytes in the pinned source.
- (c) `test_f9_specific_keeps_its_per_item_scope_record`, which checks that the SC record is unchanged.
- `test_fix6_units_carry_only_their_recorded_exposures`: see Notes 1.

`tests/test_safetyfw_usecases.py::test_pf_every_byte_has_ve_status_and_one_unit` passes, and it checks the README
table. No existing test was changed or removed: none pinned the old text (`grep` for the old acts in tests/ found
none). The selected run and its result are below.

## Seeded bugs (each planted, its test run, then restored with `git checkout`)

| | file | bug | failing test |
|---|---|---|---|
| a | usecases/openai-preparedness/pf_vocabulary.py (+ rules.d1.ve) | the act back to "have third parties independently evaluate the model" | test_f15_third_party_act_is_openais_work_with_third_parties (AssertionError on the act) |
| b | usecases/openai-preparedness/pf_vocabulary.py | "first" dropped from `risk_paths`' legend | test_f9_selection_steps_..._as_et[f9-risk-paths-...] (legend quote differs) |
| c | usecases/openai-preparedness/pf_vocabulary.py | "then" dropped from `specific_safeguards_per_path`' legend | test_f9_selection_steps_..._as_et[f9-specific-...] (legend quote differs) |
| d | usecases/openai-preparedness/spans.json | f9-risk-paths' ET record and ET wait removed | test_f9_selection_steps_..._as_et[f9-risk-paths-...] ("assert 'ET' in ['JT']") |
| e | usecases/openai-preparedness/build_document.py | f9-specific's placement waits back to ("SC",) | tests/test_safetyfw_usecases.py::test_pf_every_byte_has_ve_status_and_one_unit ("spans.json or coverage.json is out of date") |

Only Python changed, in the use case. There is no ve/, lean/ or rust/ change, so no Lean or Rust seed applies, and
there is no trust growth, mutant JSON or trust_mutants record.

## Open list

- **Questions sent: none.** Stop-rule question 1 did not arise (K14 and N3 kept their answers). Question 2's case did
  arise, and the task file gives its answer: "then" goes in the legend only, and I say so here. "first" also goes
  in the legend only, because the act limit refuses it; the task names that case too ("where an act cannot hold a
  qualifier within 80 characters, the predicate's legend quotes the full sentence"). No unit is left unfixed.
- **Out of scope, unchanged, with their rulings:**
  - Item 59, still split, stay failing (reported as disputed): f1-halt-strict, f1-halt-default, f1-misuse-bio-strict,
    f1-misuse-bio-default, f10-validate, f16-without-noinput, f16-without-nodelib.
  - Item 59, cleared: f16-sag-recommend ((iii) by both) and f9-efficacy (NOT by both).
  - Item 59, (i) by both, disputed source reading, on reviews/key-ruling-list-openai-preparedness.md:
    f16-board-mandate, f16-board-reverse, f2-no-deploy-any.
  - C6, C-doc and G9: VE answer != key (PLAN 12 items 18-20). Keys and scorer untouched.
- **K findings: none.** PLAN section 6 and answer-key.json are untouched; `test_answer_key_equals_section_6_cell_by_cell`
  is in the selected run.

## Budget

The launcher gave no reading. I did not run ucfix-budget.py.

## Notes for the DRI

1. **Omission rule on the three units** (the installed omission-2 rule as ported in tests/omission_rule.py; the test
   is `test_fix6_units_carry_only_their_recorded_exposures`).
   - f15-third-party keeps two `loss` exposures from its accounting line: "(as described in Section 3.1)" and "for
     example based on results of Capabilities Report presented to them", both tagged `exposition` (any tag other
     than restates / rule / reading counts as a loss). They are unchanged from main, and I left them as they are: the
     rule does not formalise either clause. So K14 counts as audited only after an omission-audit seat's dependency
     read clears them, not on this fix alone.
   - Item 27 of PLAN section 12 adds a `plan12` exposure to f15-third-party and one to f9-specific.
   - f9-specific keeps its `unformalised` exposure (SC).
   - f9-risk-paths has none.
   - The full-sentence legends resolve the three `mistag` exposures main had: f9-risk-paths' "We use the following
     process to select safeguards for a deployment" (restates), and f15-third-party's "If we deem that a deployment
     warrants" and "OpenAI will work with third-parties to" (restates).
2. The act could hold "first" only if it dropped "proposed" or reworded "can arise". I kept the act's wording to add
   no new C1 question, and the legend carries the word.

## PLAN

Section 12 item 27 records this item. No other PLAN section changed.

## Next item

After merge, the DRI decider launches both of these; the builder runs no audit:
- the production checklist pass, which re-reads only the changed units (addendum 8 item 56): f15-third-party,
  f9-risk-paths, f9-specific;
- the full union audit at the Nov 23 checkpoint.

## Size

SIZE: 30 product (use-case Python and rules: pf_vocabulary.py 17+/6-, build_document.py 7+/2-, rules.d1.ve 3+/3-;
added lines), 106 tests, 19 other hand-written lines (PLAN 13, README 6), plus this REPORT. Generated: spans.json,
coverage.json, environment.d1.json, gaps.json, units.json. Measured with `git diff --numstat $(git merge-base HEAD
main)`.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer, schema or route changed (no ve/, lean/ or rust/ file in `git diff --stat main...HEAD`).
2. PASS: deliverables 1-3, condition tests (a)-(c), seeds (a)-(d) (plus e), the PLAN 12 entry, README and REPORT are
   above. Each is tied to commit 3750cbbb82 or d9ef41082c and to the tests named above. The only overlap is
   kb-10b-switch on run.py, which this item does not edit.
3. PASS: seeds a-e, each failing its named test.
4. N.A.: no Python, Lean or Rust checker path changed. The valid case still passes: run.py gives 236 / 239.
5. N.A.: no binding or relay changed.
6. PASS: the selected run on the committed final HEAD is below.
7. PASS: no DELTA row and no reserved signature.
8. N.A.: no user-visible VE behaviour changed (use-case translation text only; results.json is unchanged).
9. PASS: the new tests are in tests/test_pf_fidelity_fix.py, which the selection maps to usecases/openai-preparedness/,
   and `regen_generated.py --check` exits 0.
10. N.A.: no Lean statement or proof changed.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no runtime code. run.py took 1338.0 s and 1389.7 s (fix-5: 1458.4 s).
13. PASS: no test removed or renamed (`git diff main...HEAD -- tests/` adds lines only).
14. PASS: both directions are tested. Test (a) asserts the new act and the absence of the old act. Test (b) asserts the
    order word in the legend and its absence from the act. Seeds b-d show that removing a record fails. Every count in
    this REPORT names its command. The spec re-reads are listed above.
15. PASS:
    - Overclaims checked: "no answer moved" (run.py output, results.json unchanged), "unchanged" SC record (test (c)),
      "none" exposures for f9-risk-paths (`test_fix6_units_carry_only_their_recorded_exposures`).
    - No deliverable was cut.
    - Every new check has a seed (a-e).
    - Limits: N.A.

## Selected run

(filled in below after the run on the committed HEAD)
