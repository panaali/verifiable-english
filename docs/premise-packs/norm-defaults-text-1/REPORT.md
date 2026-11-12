# norm-defaults-text-1: record corrections and review fixes (REPORT)

Summary: READY FOR RECHECK. Review F1 and F2 are fixed in 41ce344aa3, recheck F3 in f3f360c1c3 and recheck F4 in
321a3aba02; each listed probe failed before and passes after. Selected tests passed (35 units, 0 failures); `lake build` and `lean/audit.py` passed.
The merge train owns the full gate.
No product behavior changed, no DELTA row is needed under the item's no-DELTA ruling, and no signature is reserved.

## Review fixes (2026-11-12)

- F1 -> qualify the wrapper-free `todayGate` claim with the legacy-profile restriction ->
  `tests/test_norm_defaults_records.py::test_wrapper_free_gate_claims_keep_legacy_hypothesis` and
  `::test_gate_scope_scan_refuses_unqualified_equivalence` -> 41ce344aa3.
- F2 -> distinguish the admitted alternatives pair from the refused risk pair in `docs/INTEGRATION-GAPS.md`,
  and include that record in the Lean-derived gate check ->
  `tests/test_norm_defaults_records.py::test_alternatives_norm_defaults_gate_records_agree` and
  `::test_pair_scan_refuses_stale_records` -> 41ce344aa3.

The F1 and F2 executable review probes each exited 1 before the fix and 0 afterward. The focused regression file
passed 8 tests. The selected Mac run passed 34 units with 0 failures; the selector deferred two broad files to the
chain gate. `lake build` completed 1429 jobs; `python3 lean/audit.py` audited 864 source files and 9911 theorem
declarations with the standard axiom allowlist. The three tests listed in `main-known-red.txt` are pre-existing and
were neither edited nor encountered in the selected run. No full suite, release gate, or trust-mutant sweep ran:
this review fix changes documentation and its tests only.

## Recheck fix (2026-11-12, looprecheck1 F3; DRI note reviews/dri-decisions-20261112-norm-defaults-text-1.md item 1)

- F3 -> the integration status paragraph of `docs/spec/norm-defaults.md` and deliverable 1 below now say that on a
  list with a wrapper the answers of `gateOf profileTable` (`dispatch`) and `todayGate` need not agree. They differ
  on `[readings@1, relational-fol@0]`. On `[alternatives@0, norm-defaults@0, readings@1, relational-fol@0]` both
  refuse with `UnsupportedProfile: alternatives@0 requires norms@0`. No other record the
  branch touched stated the categorical difference (grep "wrapper" over the branch's files) ->
  `tests/test_norm_defaults_records.py::test_f3_probe_no_categorical_wrapper_difference` (the probe, verbatim),
  `::test_wrapper_records_say_need_not_agree` (every record the item touched), a shared-refusal test and
  `::test_wrapper_scans_refuse_and_accept` -> f3f360c1c3. Recheck F4 (below) replaced the shared-refusal test,
  whose parser of `todayGate`'s checks could not back the claim it was written for.

Both lists' answers were read by direct Lean evaluation at 302316a182 (`lake env lean` on a scratch file evaluating
`todayGate`, `dispatch` and `gateOf profileTable`). PROBE F3 exited 1 before the fix and 0 after. With the two records
restored from 302316a182 the three record tests failed (`3 failed, 9 passed`); after the fix the file passes 12.
Writing this section, the shared-refusal check paired a differing list with the shared refusal when both sat in one
sentence; its pattern was made to stop at the next list, and this section names the two lists in separate sentences.
The
selected run (VM fallback; cloud slots busy) passed 35 units with 0 failures and deferred `tests/test_repo_map.py`
and `tests/test_select_tests.py` to the chain gate. `lake build` completed 1429 jobs; `python3 lean/audit.py` passed
(864 source files, 9911 theorem declarations). Docs and tests only: no Lean, Python or Rust product change, so no
seeded product bug applies; trust +0; no DELTA row (item-specific no-DELTA ruling); no signature reserved. The
three `main-known-red.txt` tests are pre-existing, not edited and not selected.

## Recheck fix (2026-11-12, looprecheck1 F4; DRI note reviews/dri-decisions-20261112-norm-defaults-text-1.md item 2)

- F4 -> the integration status paragraph of `docs/spec/norm-defaults.md` no longer states a general condition for
  when the two gates agree. It keeps the shared refusal as an example only: "They can share a refusal: on
  `[alternatives@0, norm-defaults@0, readings@1, relational-fol@0]` both gates answer `UnsupportedProfile:
  alternatives@0 requires norms@0`". No other record the branch wrote states the condition (grep "names no wrapper",
  "share a refusal"). This REPORT's F3 entry described the removed test as finding the check that refuses a list
  first; it is corrected above.
  The shared-refusal test is removed with its parser. In its place:
  - `tests/test_norm_defaults_records.py::GATE_ANSWERS` holds literal answers of `todayGate`, `dispatch` and
    `gateOf profileTable` for five wrapper lists: the two the spec names and F4's three counterexamples
    (`[norm-defaults@0, readings@1, relational-fol@0]`, `[readings@1]`,
    `[readings@1, relational-fol@0, speech-acts@0]`). They were read with `#eval` in Lean (`lake env lean` on a
    scratch file importing `VE.Compose.Dispatch`, at 006b99ae3e).
  - `::test_gate_answers_are_leans` writes one `#guard` per literal answer into a file under `tmp_path` and elaborates
    it with `lake env lean`; the file must elaborate. A copy with `todayGate`'s and `dispatch`'s answers on
    `[readings@1, relational-fol@0]` swapped must fail at exactly those two guards.
  - `::test_wrapper_records_name_leans_answers`: in every record of `WRAPPER_RECORDS`, each list naming a wrapper
    profile must be a key of `GATE_ANSWERS`. Each answer named after it (up to the next list or the sentence's end)
    must be one of that list's answers. An answer after a gate's name must be that gate's answer, and "both" may only
    appear on a list whose three answers are equal. The spec must name `todayGate`'s and then `dispatch`'s answer on
    `[readings@1, relational-fol@0]`, and the single shared answer on the alternatives list.
  - `::test_wrapper_records_state_no_agreement_condition`: no sentence of `WRAPPER_RECORDS` that names `todayGate` or
    the two gates together pairs a word of agreement (the test's `AGREEMENT`) with a conditional word (`CONDITION`).
  - `::test_f4_probe_no_general_shared_refusal_condition`: PROBE F4, verbatim but rooted at the checkout.
  - `::test_wrapper_scans_refuse_and_accept`: the scans refuse the withdrawn sentence verbatim and F4's three
    counterexamples stated as shared refusals, and accept the spec's two sentences.

PROBE F4 exited 1 on 006b99ae3e and exits 0 after the fix; PROBEs F1, F2 and F3 still exit 0. With the spec put
back as it was at 006b99ae3e the file fails `::test_f4_probe_no_general_shared_refusal_condition` and
`::test_wrapper_records_state_no_agreement_condition` (`2 failed, 13 passed`); after the fix it passes 15. The
selected run (VM fallback) passed 35 units with 0 failures and deferred `tests/test_repo_map.py` and
`tests/test_select_tests.py` to the chain gate. `lake build` completed 1429 jobs; `python3 lean/audit.py` passed (864
source files, 9911 theorem declarations). Docs and tests only: no Lean,
Python or Rust product change, so no seeded product bug applies; trust +0; no DELTA row (item-specific no-DELTA
ruling, item 1 of that decision file); no signature reserved. The three `main-known-red.txt` tests are pre-existing, not edited.

## Initial build record

Records and one new test file only: the norm-defaults spec names `gate_legacy`'s proved
target (`dispatch`), the alternatives/norm-defaults gate records say "admitted" (ET-7, D46), and pk-1's identity
claims are scoped to `docs/premise-packs/pk-1/evidence/ab_full.txt`; each condition test fails on main, passes here.
No verdict, binding, Lean, Python product or Rust change; trust +0; pilot bytes 0; no DELTA row; no signature reserved.

Source: reviews/dri-decisions-20261111-portfolio1500.md item 5 (first bullet); regrade
reviews/l1-c-regrade-norm-defaults-c-20261111.md #14 ndc2-F1, #16 ndc2-F3, #19 pk1c1-F1. Base 175814252.

SIZE: 0 product, 251 tests, 70 other hand-written lines (doc lines added or changed, from
`git diff --numstat 175814252`, generated code map excluded), plus this REPORT.

## 1. Deliverables (all AGENT, all delivered)

1. **ndc2-F1.** `docs/spec/norm-defaults.md` (integration status paragraph, :300-305) now says that `gate_legacy`
   (`Dispatch.lean:1307`) proves `gateOf profileTable` agrees with `dispatch`, which strips the wrapper profiles,
   runs `todayGate` on the rest and checks each wrapper (`Dispatch.lean:535-545`). On a list with a wrapper the two
   answers need not agree with each other; review F3 qualified this sentence with one list where they differ and the
   shared-refusal list `[alternatives@0, norm-defaults@0, readings@1, relational-fol@0]` (both:
   `UnsupportedProfile: alternatives@0 requires norms@0`). The cite of `todayGate` is corrected to `:32-72` (it said `:31-71`), and the
   risk check's cite at :316 to `Dispatch.lean:40` (it said `:39`).
   Test `test_norm_defaults_spec_names_gate_legacy_target` reads the theorem's statement from
   `lean/VE/Compose/Dispatch.lean` (`gateOf profileTable ps = <f> ps`; an unexpected statement form fails), reads
   `<f>`'s definition to see that it filters `wrapperProfiles`, and requires every spec sentence citing
   `gate_legacy` to say "`gateOf profileTable` agrees with `<f>`" and to mention the wrappers.
2. **ndc2-F3.** Every current record of the pair now says what `todayGate` does (admitted):
   - `lean/NORMDEFAULTS.md:171-175`: the risk branch stays refused (check 5); the alternatives pair is admitted since
     ET-7 (D46).
   - `docs/spec/composition.md` 4.2 check 6 (:426): marked withdrawn by ET-7, text "none"; the numbers of the other
     checks are kept, so the references to checks 7 to 18 elsewhere stay right.
   - `composition.md` 9.3 transcribed `todayGate` (:865-877): the two lines of check 6 removed (Lean's body has none).
   - `composition.md` 9.3 `TodayList` (:925): the `norm-defaults@0` clause loses `"alternatives@0" ∉ ps` (Lean's
     `TodayList`, `Dispatch.lean:107`).
   Further copies found by search (`grep -rn "alternatives@0 with norm-defaults@0\|eighteen checks\|refused at
   profile" --include=*.md`, and reading 9.3) and fixed in `composition.md`:
   - `today_alternatives`'s statement (:948): loses `"norm-defaults@0" ∉ ps`, as Lean's (`Dispatch.lean:456-457`)
     and et-7's DELTA row 2 record.
   - The 9.3 prose (:1030-1033): "`norm-defaults@0 ∉ ps` in ... `today_alternatives` ... is the gate's checks 5, 6".
   - D47's note (:1194): "check 5 before check 6" becomes "check 5; ET-7 withdrew check 6". The answer cell is
     unchanged, and `tests/test_compose_dispatch.py` still parses the 10.1 table.
   - "eighteen checks" (:622, :865, :1315): now "eighteen numbered, check 6 withdrawn by ET-7".
   Copies left as they are, because they are dated history and not current claims: the composition change log
   (Draft 3 row, :1456); `docs/lean-first/b5/DELTA.md:17`; `docs/en-e3-norm/en-2/DELTA.md:38`;
   `docs/en-e3-norm/en-2c/REPORT.md:90,108`. Other texts are correct already. `docs/spec/norm-defaults.md:306-313`
   says the pair is admitted, and `pendingWithDefaults`'s by-name refusal is still current
   (`lean/VE/Compose/Examples.lean:651`, `tests/test_alternatives_fill.py:384`).
   `docs/spec/events-time-causation.md:641` records the deletion. `docs/spec/risk.md:854` is about risk only.
   Test `test_alternatives_norm_defaults_gate_records_agree` reads `todayGate`'s row for the pair from Lean
   (`gate_refusals` of `tests/test_norm_defaults_documented_support.py`, imported, not copied, and not edited).
   It also asserts that Lean's `TodayList` and `today_alternatives` agree with that row. It then checks
   composition.md, NORMDEFAULTS.md and norm-defaults.md for the following, each compared with Lean's row:
   - prose saying alternatives is "refused/rejected at profile validation";
   - a 4.2 check row for the pair;
   - the D46 row;
   - the transcribed `todayGate`, `TodayList` and `today_alternatives`;
   - the "check 6 in `today_alternatives`" prose.
3. **pk1c1-F1.** `docs/premise-packs/pk-1/REPORT.md` :94 (the pk-1-cfr-1c note) and :161 (section 6, now :163-166),
   and self-review item 8 (:198-200, "the base/head diff is empty"), now claim 0 differences only on the inputs of
   `docs/premise-packs/pk-1/evidence/ab_full.txt`. They call it a sampled comparison and say the 33 route cases have
   no valid differential (section 2; pk-1-cfr-1b replaces it). :94 also says no theorem states that hunk's identity.
   `docs/premise-packs/pk-1/DELTA.md:6-9` ("What users see does not change ... every answer, array and diagnostic is
   today's") now says no change is intended and none was found on the inputs the saved differential ran. `evidence/`
   is unchanged.
   Test `test_pk1_identity_claims_match_their_assurance` looks at each identity sentence of pk-1's REPORT.md and
   DELTA.md ("byte-identical", "0/no differences", "diff is empty", "is/are today's", "users see does not change").
   Each must cite a saved differential whose first line is not INVALID and whose last line is `exit 0` (the record's
   assurance is read from the file). A sentence that cites an INVALID or failed record fails. Universal wording
   ("every/all/any output/answer/array/diagnostic/input", "on today's routes", "the base/head diff") also fails,
   because each pk-1 record is a sampled differential.
   pk-1b REPORT :132 and pk-1s DELTA :12 stay with pk-1-cfr-1c (regrade line 119).

Opposite directions, in the same file: `test_gate_legacy_scan_refuses_old_sentences` (main's sentence, a sentence
naming `todayGate`, one without wrappers, a bare citation, none), `test_pair_scan_refuses_stale_records` (each stale
form refused while Lean admits; the admitted records refused, and accepted, against a Lean source with the refusal
put back) and `test_identity_scan_refuses_and_accepts` (scoped claims accepted; universal, uncited, INVALID-cited and
support-only-cited claims refused).

## 2. Fails on main first

The three condition tests run against main's five records (`git checkout 175814252 -- <the five files>`, then
`uv run pytest -q tests/test_norm_defaults_records.py`, then restored): `3 failed, 3 passed`.
- `test_norm_defaults_spec_names_gate_legacy_target`: `Left contains 2 more items`: "names no target agreeing with
  `gateOf profileTable`" and "omits that `dispatch` strips and checks the wrapper profiles", both on the integration
  status sentence.
- `test_alternatives_norm_defaults_gate_records_agree`: `Left contains 6 more items`, all in composition.md except
  the last:
  - "reads check 6 into `today_alternatives`";
  - "4.2 check row refuses the pair";
  - "the transcribed todayGate differs from Lean's on the pair";
  - "TodayList's norm-defaults@0 clause differs from Lean's";
  - "today_alternatives differs from Lean's statement";
  - lean/NORMDEFAULTS.md: "says refused, todayGate admits: Still open: the alternatives and risk branches ...".
- `test_pk1_identity_claims_match_their_assurance`: `Left contains 8 more items`:
  - REPORT: 'It is byte-identical (A/B above).' cites no valid saved differential;
  - REPORT: "None: every output on today's routes is byte-identical (section 2)." cites no valid saved differential,
    and claims identity beyond the sampled inputs;
  - REPORT item 8: "the base/head diff is empty" claims identity beyond the sampled inputs;
  - DELTA: "What users see does not change ..." and "On those lists every answer, array and diagnostic is today's:"
    each cite no valid saved differential and claim identity beyond the sampled inputs.

At HEAD: `uv run pytest -q tests/test_norm_defaults_records.py tests/test_pk1_route_case_evidence_validity.py
tests/test_compose_dispatch.py tests/test_norm_defaults_documented_support.py`: `69 passed`.

## 3. Seeded bugs

Each was planted alone by a script (`/tmp/ndt1-seed.py`, not committed). The script ran
`uv run pytest -q tests/test_norm_defaults_records.py::<test>`, saw `1 failed`, and restored the file
(`git checkout`; the tree was clean afterwards). Only docs changed (no Lean, Python product or Rust file), so these
are the item's seeded bugs. "main" means main's whole file was restored.

| # | File | Planted | Failing test |
|---|---|---|---|
| S1 | docs/spec/norm-defaults.md | main (the `todayGate`-target sentence) | test_norm_defaults_spec_names_gate_legacy_target |
| S2 | lean/NORMDEFAULTS.md | main (":171-172 refused at profile validation") | test_alternatives_norm_defaults_gate_records_agree |
| S3 | docs/spec/composition.md | 4.2 check 6 with its refusal text | test_alternatives_norm_defaults_gate_records_agree |
| S4 | docs/spec/composition.md | the two check-6 lines back in the transcribed `todayGate` | test_alternatives_norm_defaults_gate_records_agree |
| S5 | docs/spec/composition.md | `"alternatives@0" ∉ ps` back in `TodayList` | test_alternatives_norm_defaults_gate_records_agree |
| S6 | docs/spec/composition.md | `"norm-defaults@0" ∉ ps` back in `today_alternatives` | test_alternatives_norm_defaults_gate_records_agree |
| S7 | docs/spec/composition.md | the 9.3 "checks 5, 6" prose | test_alternatives_norm_defaults_gate_records_agree |
| S8 | docs/premise-packs/pk-1/REPORT.md | main (:94, :161, item 8) | test_pk1_identity_claims_match_their_assurance |
| S9 | docs/premise-packs/pk-1/DELTA.md | main (:6-9) | test_pk1_identity_claims_match_their_assurance |
| S10 | docs/premise-packs/pk-1/REPORT.md | new "The 33 route cases are byte-identical (`evidence/ab_route_cases.txt`)." | test_pk1_identity_claims_match_their_assurance ("which is INVALID") |

## 4. Checks, trust and DELTA

- Trust: `uv run python tools/trust_map.py --check` on the final tree: `K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0`, PASS. No Lean file changed, so there is no R16 growth, no mutants.json and no
  trust_mutants sweep (checklist 13a applies to trusted Lean growth). The light lane printed `NOT 321 changed lines
  outside generated files > 150` (it counts the test file and the docs); no trust_mutants sweep was run, because
  this item changes no trusted Lean.
- `cd lean && lake build` (unchanged Lean, after `lean-prep.sh`): `Build completed successfully (1429 jobs)`.
  `tools/gate_collection.py --check --prebuilt`: `6 added, 0 removed by a trailer, 0 refused, 0 stale and
  0 malformed`.
- Regen: the new test file feeds the code map only (`tools/code_map.py --check`: `stale code map`), so
  `tools/regen_generated.py --write --only codemap` was run once and committed. The other code-map rows it rewrote
  were already stale on main.
- Selection: `tools/select_tests.py --base 175814252` selects `tests/test_norm_defaults_records.py`,
  `tests/test_norm_defaults_documented_support.py`, `tests/test_pk1_route_case_evidence_validity.py` and
  `tests/test_compose_dispatch.py` (36/610 units).
- DELTA: none, because this item makes no user-visible change. No DRI signature.
- Pilot bytes expected to move: 0 (records and tests only).
- In-flight overlap: no branch under `lean-first/`, `feature/`, `infra/` or `foundation/` touches these files
  (`git diff --name-only main...<branch>`, checked at the start).
- Spec re-read: `gate_legacy` against `Dispatch.lean:1306-1307` and `dispatch` against `:535-545`. `todayGate`
  against `:32-72`. `TodayList` against `:99-107`. `today_alternatives` against `:456-457`. D46 against
  `composition.md:1193`. ET-7's statement change against `docs/events-time-causation/et-7/DELTA.md:13-14`.
  `ab_full.txt` and `ab_route_cases.txt` were read for their first and last lines.

## 5. Notes for the DRI

- The Lean docstring of `todayGate` (`lean/VE/Compose/Dispatch.lean:31`) and `lean/COMPOSE.md:35` still say
  "eighteen checks". The first is a Lean file, and this item makes no Lean change; the second is outside this
  item's files. Wording only, with no verdict effect.
- `tests/test_pk1_route_case_evidence_validity.py` was not edited. The new identity scan is in
  `tests/test_norm_defaults_records.py` and adds the universal-wording and INVALID-cite checks (the C part of
  pk1c1-F2 stays with pk-1-cfr-1c).
- Selected tests on committed HEAD 8674805cb (`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 175814252
  --run`, run on the VM by the runner's choice): exit 0, "recorded 36 units for tree 7e04d75075; ... 0 failed", 969 s.
  Only this REPORT changed after it.

## 6. Next items

norm-defaults-cfr-1b-cfr-1, norm-defaults-cfr-1-cfr-1 and pk-1-cfr-1b (their own queue rows, disjoint paths). No
FOLLOW-UP from this item.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., because no relayed answer changed.
2. Required deliverables: PASS. All three were delivered (section 1), and the three condition tests are in
   tests/test_norm_defaults_records.py.
3. Tests can fail: PASS. S1-S10 (section 3), plus the opposite-direction tests in section 1.
4. Python, Lean and Rust agree: N.A., because no product code changed (trust_map +0; Lean build unchanged).
5. R8 binding: N.A., because no relayed field changed.
6. Gate evidence on the final HEAD: PASS. The chain gates the committed HEAD, and the selected run is below.
7. No unsigned item: PASS. There is no DELTA row and no reserved signature.
8. User-visible changes in DELTA: N.A., because these are records only; `git diff --stat` shows no product file.
9. Test selection: PASS. `tools/select_tests.py` selects the four test files (section 4).
10. Lean statements: N.A. for Lean. The spec's copies now match Lean, as
    test_alternatives_norm_defaults_gate_records_agree and test_norm_defaults_spec_names_gate_legacy_target check.
11. Budgets and deadlines: N.A., because no runtime code changed.
12. CPU and memory: N.A., because no runtime code changed. The new tests read four text files.
13. Test-removed trailers: PASS. `gate_collection.py --check --prebuilt` reports 0 removed and 0 malformed.
14. Both directions, cited evidence and spec re-read: PASS. See the opposite-direction tests (section 1), the
    commands quoted in sections 2 and 4, and the spec re-read lines in section 4.
15. No overclaim: PASS. "every"/"all" in this report refer to the listed files and greps; each fix is checked by the
    three condition tests. Nothing was silently cut. Each new check has a seeded bug (S1-S10). No limit is involved
    (N.A.).
