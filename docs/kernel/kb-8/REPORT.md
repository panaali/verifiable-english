# KB-8 build report: a wire theorem for the `quantity` mode

**Acceptance not met as written: quantity wrap 75 as measured (task: at most 30); DRI 2026-11-12 item 1 (reviews/dri-decisions-20261112-kb-8.md) accepted the measured figure; FOLLOW-UP kb-closure-attrib.**
Status: built; HEAD e420dfbec9 (tested; this report is the one docs-only commit after it) on main 35a9ba135f (kb-7 merged; the branch was rebuilt on it and every generated file regenerated with its tool).
Changed: lean/VE/Time/WireSound.lean (five theorems, one per verdict-bearing kind, plus `runCaseReported_ok`); registry path `quantity` (subject `runCase` and `Document.extension`; nonverdict `runCount`, `runConversion`); ties; closure baseline and records re-measured.
Open: no other item. Figures: kernel 9,504 (unchanged, the signed total); quantity spec 2,267 / wrap 75; trusted Lean -58 (K +0, S +0); DELTA none.
Signatures: none needed. The DRI's two decisions on this item are in reviews/dri-decisions-20261112-kb-8.md.

SIZE: 265 product (Lean: WireSound.lean 264, VE.lean 1), 0 tests, 151 other hand-written lines (registry 26, trust ties 17, assurance manifest 1, consolidation plan 4, spec 24, frozen-keys 2, seeded-bugs record 76, not counting this report).

## What was built

`lean/VE/Time/WireSound.lean`, namespace `VE.Time.Wire`:

| Theorem | Hypotheses | Conclusion (decoders, answer fields, semantic relations only) | Ends in |
|---|---|---|---|
| `quantity_admission_wire_sound` | `runCase j more = .ok answer`; `kind` is `"admission"` or absent | id, environment and quantity as decoded; `answer = ok id [assurance, Q, core, meaning_id, core_meaning_id, environment_id, target_environment_id] ++ value`; `Admitted` and the core `WellFormed`; no `model` field and `value = []`, or the decoded order model `d` and `value = [("value", b), ("evaluations", work)]` with `b = core.eval d.toModel []` | `Admission.sound`, `evalB_sorted_sound` |
| `quantity_countermodel_wire_sound` | `runCase j more = .ok answer`; kind `"countermodel"` | premises, conclusion and model as decoded; the closed seven-field answer; every statement `Admitted`; `refutes = (premise cores all true in d && !conclusion core true in d)` | `refutesB_sorted_sound` |
| `quantity_certificate_wire_sound` | `runCase j more = .ok answer`; kind `"certificate"` | premises, conclusion and certificate as decoded; the closed seven-field answer; every statement `Admitted`; `valid = true →` the certificate is bound to these meaning ids and `TEntails` over every admissible tagged structure (`valid = false` asserts nothing) | `checkW6Certificate_sound` |
| `quantity_document_wire_sound` | `runCase j Document.extension = .ok answer`; kind `"document"` | the document decoded by `Document.decodeDocument`; the properties of `Document.admitDecoded_sound` on its admission `res`; `answer = ok id [admitted, assurance, report, report_id, environment_id, kinds]` with the report and its digest stated | `admitDecoded_sound` |
| `extension_document_sound` | `Document.extension w id kind j = .ok answer` | `kind = "document"` and the same conclusion | `admitDecoded_sound` |
| `runCaseReported_ok` | `runCase j more = .ok answer` | `runCaseReported j more = answer` | (ties the entry) |

Every answer is a closed field list (sibling lesson kb-7 F1: no open tail that could override a stated key; seed S7 below appends a second `valid` and the proof breaks). A spent budget ends the case with an error, never an answer, so no theorem covers it (three-valued: UNKNOWN is never false). The `evaluations` count is the evaluator's work and is not stated.

Registry (`tools/kernel-paths.json`, path `quantity`, tier still candidate): subject `VE.Time.Wire.runCase` and `VE.Time.Document.extension`; theorems the five above; nonverdict `VE.Time.Wire.runCount` (`count`: a counting expansion) and `VE.Time.Wire.runConversion` (`day`, `civil`, `lower`, `render`), each with its reason. `lean/VE.lean` imports the module, so no registry `imports` entry is needed.

Trust map (`tools/trust-classes.json`): `runCase` tied to the four runCase theorems, `runCaseReported` to `runCaseReported_ok`. The statements define no new trusted declaration (they are written out in the theorems). `python3 tools/trust_map.py --check`: "against 35a9ba135fe2: K +0, S +0, D +0, G +0, tied +58, unclassified +0, trusted -58 ... PASS".

## Figures (commands and outputs)

- `python3 tools/kernel_closure.py --out docs/kernel/closure-baseline.json` (copy: docs/kernel/kb-8/closure.json):
  `quantity candidate 5 2267 75 2274`; `kernel (distinct lines of every path of tier kernel): 9504`; `under the frozen keys' answers: 16150, of them in the kernel: 9504`; `definitions that write a verdict token: 57, of them outside the kernel: 56 in 28 modules`; no problem line. Before (main 35a9ba135f's baseline): quantity 4 theorems, spec 613, wrap 1,804, lines 2,040; keyed 16,185.
- Spec 2,267 is under 2,500, so no module list is required. Largest spec modules (JSON `spec_modules`): VE.Time.Wire 553, VE.Order.Tableau 244, VE.Time.Document 210, VE.Time.Syntax 162, VE.Order.Wire 156, VE.Route.Admission 154, VE.Route.Wire 128, VE.Route.Decode 99, VE.CertificateWire 94, VE.Time.Semantics 86.
- The wrap's 75 lines, by declaration (the Lean half's decl list): 7 lines of code (`runCaseReported` 6, `noExtension` 1, its default argument); 28 lines of data types reached through the `more : Extension` parameter (`Extension`, `W6Env`, `QVocab`, `UnitDecl`, `Display`, `QType`), which the spec also reads (path lines = spec + 7); 40 lines that are `decodeUnit`'s whole range, charged because `runCaseReported`'s `match` reuses Lean's matcher `VE.Time.Wire.decodeUnit.match_1` and `tools/kernel_closure.lean` `rangeOf` gives `f.match_1` the range of `f`. Probe: `runCaseReported` value constants = `[Extension, decodeUnit.match_1, runCase]`.
- Kernel total unchanged: 9,504 = main's saved and signed total (docs/kernel/ALLOWANCES.md "signed total: 9,504 lines"); `tests/test_kernel_closure.py`: 27 passed.
- `cd lean && lake build`: "Build completed successfully (1430 jobs)". `python3 lean/audit.py`: "PASS: 865 source files; 9917 named theorem declarations audited ... only the declared standard axiom allowlist". The six theorems use `propext`, `Classical.choice`, `Quot.sound` (lean/axioms.txt).
- No executable evaluator in a conclusion: the compiled `-- uses` lines of the five theorems (lean/statements.txt) name none of evalB, refutesB, checkW6Certificate, checkCertificate, admitDocument, admitDecoded, countermodelCheck, admitNodes, checkGraph, Budget.orderMem, tableIndex (probe script in the build log).

## The five frozen keys (run on the final tree, eligibility first; each exit 0, working tree unchanged)

| Key | Command | Result | Main's record |
|---|---|---|---|
| eligibility | `uv run python usecases/eligibility/run.py --no-write` | exit 0, mutants_killed 32/32, open [] | — |
| Anthropic RSP | `usecases/anthropic-rsp/run.py --check` | 110 / 126 | usecases/anthropic-rsp/README.md:88 "**110 / 126**" |
| OpenAI Preparedness | `usecases/openai-preparedness/run.py --check --base-only` | 230 / 239 | usecases/openai-preparedness/README.md:129 "**230 / 239**" |
| DeepMind FSF | `usecases/safety-framework/run.py --check` | 257/262 | usecases/safety-framework/README.md:289 |
| agent policy | `usecases/agent-policy/check.py base` | exit 0, every `*_disagreements` empty | — |

They cannot move: `ve_service` (root `Serve`, which imports `VE.Service.Protocol`) does not import `VE.Time.WireSound`; only `lean/VE.lean` and `lean/VE/Audit.lean` do. (The 2026-11-11 record's 111 and 231 are main's earlier figures; main's own READMEs now say 110 and 230.)

## Seeded bugs (docs/kernel/kb-8/seeded-bugs.json; each planted, shown failing, restored)

| Id | File | Mutation | Fails |
|---|---|---|---|
| S1 (task a) | lean/VE/Time/Wire.lean | certificate answer `valid` := `true` | `lake build VE.Time.WireSound`: quantity_certificate_wire_sound, WireSound.lean:167 |
| S2 (task b) | lean/VE/Route/Decode.lean | `decodeOrderModel` keeps `rows.dropLast` | no proof breaks (the theorems speak of the decoded model); existing tests fail: tests/test_fret_w6a_rerating.py::test_bounded_response_unrolls_and_lean_admits_it[16-51] and [13-42] (values [False, False, False], expected [True, True, False]), tests/test_w6a_looprecheck1.py::test_pinned_counting_fixtures_evaluate_identically_relay_and_lean; the full build fails at the #guard lines lean/VE/Cardinality/RunExamples.lean:461-473. Clean tree, same mode: 3 passed |
| S3 | lean/VE/Time/Wire.lean | admission `value` := `!value` | quantity_admission_wire_sound, WireSound.lean:74 |
| S4 | lean/VE/Time/Wire.lean | countermodel `refutes` := `!refutes` | quantity_countermodel_wire_sound, WireSound.lean:123 |
| S5 | lean/VE/Time/Document.lean | document `environment_id` := `w.targetId` | extension_document_sound, WireSound.lean:200 |
| S6 | lean/VE/Time/WireSound.lean | the countermodel statement negated | quantity_countermodel_wire_sound, WireSound.lean:124 |
| S7 | lean/VE/Time/Wire.lean | certificate answer appends `("valid", true)` (kb-7 F1's class) | quantity_certificate_wire_sound, WireSound.lean:167 |

The Lean seeds were run on both the first build and the rebuilt branch, with the same results. S2 was run on the first build; its files are byte-identical on the final base.

## Trust mutants

The change is not light (`light-lane.py check`: NOT, new Lean files), so the sweep ran: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --rescore <first run> --json docs/kernel/kb-8/trust-mutants.json` gave "0 definitions, 0 mutants ... 0 SURVIVOR", exit 0. The change adds or changes no trusted declaration.

## Tests

- Final selected run on the committed HEAD e420dfbec9: `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 35a9ba135f --run`: exit 0; the remote runner (ve-cloud-2) selected 503 of 608 units with its own map and recorded "503 units for tree fd938eab45; ... 0 failed" (log /tmp/kb8-selected2.log, 7,897 s).
- The first selected run (pre-rebase tree) failed two tests, both fixed here: tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified (WireSound.lean is now classified in ve/assurance-manifest.json `other_json`) and tests/test_consolidation_tools.py::test_committed_ledger_names_real_declarations (docs/CONSOLIDATION-PLAN.md steps 5 and 8b re-quoted from `python3 tools/trust_map.py --ledger` after the two ties: 466 -> 415 and 3795 -> 3788 lines left to tie).
- While iterating: tests/test_kernel_closure.py 27 passed; tests/test_assurance_manifest.py 157 passed; tests/test_consolidation_tools.py -k "ledger or ties" 55 passed.
- Not run by me: the full release gate (the chain runs it).

## DELTA

None. No answer byte, runner, decoder, schema or Python/Rust code changes; the service binary does not import the new module (above). No DELTA.md.

## Deliverables (task lines) and where they are

| Task line | Delivered by |
|---|---|
| One theorem per verdict-bearing case kind of `runCase j Document.extension`, hypothesis `runCase j more = .ok answer` and the kind | e039e2b1d7 (four kinds, plus `extension_document_sound` and `runCaseReported_ok`) |
| Non-verdict kinds listed under `nonverdict` with a reason of at least 20 characters | 855088b32a (`runCount`, `runConversion`) |
| Conclusions mention decoders, result fields and semantic relations only | `-- uses` probe above |
| Statements proposed in the first commit, statement and proof together, no sorry | e039e2b1d7 (all kinds in one commit; no `sorry`: audit PASS) |
| kernel-paths.json: subject, theorems, tier candidate; imports if needed | 855088b32a (VE.lean imports the module) |
| Regenerate closure-baseline.json | e45524436d |
| Acceptance: wrap at most 30 | NOT MET: 75 as measured, accepted by the DRI (item 1); FOLLOW-UP below |
| Acceptance: spec figure (list modules if above 2,500) | 2,267 (list given anyway) |
| Acceptance: lake build, audit, no new axiom | above |
| Acceptance: kernel total unchanged | 9,504 = signed total |
| Acceptance: five keys pass unchanged, eligibility first | above |
| Seeded bugs (a) and (b), recorded and restored | S1, S2 |
| Merge order: only quantity entries; regenerate after kb-7 merges | the branch was rebuilt on main 35a9ba135f; generated files regenerated with their tools; non-quantity cells re-quoted only as DRI item 2 allows |

FOLLOW-UP: kb-closure-attrib tools/kernel_closure.lean `rangeOf` charges a reused matcher (`f.match_1` used by another declaration) with the whole range of `f`, and charges to a wrap the data types its spec already reads; charge a reused matcher to the declaration that uses it with no extra lines, re-measure every path in the same change (quantity's wrap expected about 7 to 35). Filed by the DRI's item 1 as the unfinished part of kb-8's acceptance.

## Spec re-read

- "one theorem per verdict-bearing case kind of `VE.Time.Wire.runCase j VE.Time.Document.extension`" against prompts/task-kb-8.txt: the verdict-bearing kinds of `runCase` (Wire.lean `runCase`) are admission (`value`), countermodel (`refutes`), certificate (`valid`) and, through the extension, document (`admitted`); four theorems on `runCase`, one on the extension.
- "hypothesis `runCase j more = .ok answer` and the kind": the admission, countermodel and certificate theorems hold for every `more` (those kinds never reach it); the document theorem fixes `more := Document.extension`.
- "the answer's verdict field is what the proved checker returned AND the checker's soundness conclusion holds": stated through the checker's soundness conclusion, not the checker's name, because the next sentence of the task forbids an executable evaluator in a conclusion. Certificate: `valid = true →` binding ∧ `TEntails` (what `checkW6Certificate_sound` concludes from `.ok true`). A `false` is a rejection, not a refutation, so it asserts nothing.
- "entailment over admissible order structures for an accepted certificate": `TEntails w.vocab.env (ps.map (·.formula)) c.formula` (the direct tagged semantics over every admissible tagged structure).
- "truth or refutation in the decoded model for an evaluation or countermodel": `Formula.eval d.toModel []` on the regenerated cores, `d` from `VE.Route.Decode.decodeOrderModel`.
- "`Admitted` for a document": the full conclusion of `Document.admitDecoded_sound` (and `VE.Time.Admitted` for each statement of the other kinds).
- "subject: [\"VE.Time.Wire.runCase\"]": recorded with a second subject, see Notes 1.
- kb-7 review F1 (sibling lesson): every stated answer is a closed `Wire.ok id [...]` list; seed S7.

## Notes for the DRI

1. Registry subject: `VE.Time.Document.extension` was added beside `VE.Time.Wire.runCase`. The mode's pin (`runMode_quantity`) hands `Document.extension` to `runCaseReported`, so the registry lists it as a second entry root, and the wrap walked its body (`runDocument`, `admitDocument`, the decoders) as unproved code. `extension_document_sound` states its answer (the tool's `stated` lists it), so it is a subject by the registry's own rule. With only `runCase` as subject the wrap would count the whole document route.
2. Statement predicates are written out inside the theorems rather than as new definitions, so trusted Lean does not grow (S +0). The document conclusion is therefore repeated in `extension_document_sound` and `quantity_document_wire_sound`.
3. Main's drift: before kb-7 merged, today's main measured 8,738 against the signed 8,732 (DRI item 2 signed it for kb-8 to record). kb-7's merge then re-measured main and signed 9,504, which already includes it, so this branch adds no ALLOWANCES row. Main also moved four candidate rows of the spec's table since kb-7's measurement (normDefaults, readingsRoute, discourse, document); they are re-quoted mechanically, as item 2 allows.
4. The seeded run for S2 needed two harness steps: `--noconftest`, because the session's `lake build` stops first at the cardinality `#guard`s; and the seeded `ve_service` build id added to lean/checkers.lock for the run (restored from git after). The clean tree passes in the same mode.
5. `tools/regen_generated.py --write` (all entries) needs the Rust release binary for `route-cases`; it was run with `--skip route-cases` (an unaffected input). Its codemap churn (advisory on branches, regenerated on merge) was not committed.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no answer, schema or relay changes (DELTA none; the service does not import the module).
2. Every required deliverable built: PASS, deliverables table above. The one unmet acceptance line is recorded as the DRI decided (item 1).
3. Tests and gates can fail: PASS, docs/kernel/kb-8/seeded-bugs.json S1-S7 (six Lean proofs break; S2 breaks test_bounded_response_unrolls_and_lean_admits_it and test_pinned_counting_fixtures_evaluate_identically_relay_and_lean).
4. Python, Lean and Rust agree: N.A., no runner changed. The five keys exit 0 with main's figures (keys table).
5. R8 binding: N.A., no field Python reads changed.
6. Gate evidence matches final HEAD: PASS. Rebuilt on main 35a9ba135f (merge base); final selected run on committed HEAD e420dfbec9; evidence from `git log 35a9ba135f..HEAD --no-merges` (six commits plus this report).
7. No unsigned item: PASS. `trust_map.py --check` K +0, S +0; kernel 9,504 = signed total (test_the_kernel_is_within_the_signed_total); DELTA none; both DRI decisions cited.
8. Every user-visible change in DELTA: N.A., none; keys unchanged (table).
9. Test selection finds the tests: PASS. `select_tests.py --base 35a9ba135f` selects tests/test_kernel_closure.py, tests/test_trust_ratchet.py, tests/test_trust_budget.py, tests/test_w6a_looprecheck1.py (which catches S2), not every unit.
10. Lean statements say what is claimed: PASS. S1, S3-S7 break the build; the theorems are about `runCase`'s returned `answer` (hypothesis `= .ok answer`, conclusion `answer = ok id [...]`); the `-- uses` probe finds no evaluator.
11. Budgets fail closed: N.A., no budget code changed; an exhausted budget is an error, which no theorem covers (stated in the module docstring).
12. No CPU or memory regression: N.A., theorems only; the service binary is unchanged.
13. Test-removed trailers: N.A., no test removed or renamed (`gate_collection.py --check --prebuilt`: rc 0, "34512 collected ... 0 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers").
14. Both directions, cited evidence, spec re-read: PASS. Each seed fails and the restored tree builds and passes (S2: 3 passed clean); spec re-read section above.
15. No overclaim, no silent cut, new checks can fail, limits first: PASS. The unmet wrap line is in the first line, not rewritten; no deliverable was cut; seeds S1-S7; no limit code changed (N.A. for limits).
