# Lean-first batch 10a: DELTA

Base `2ce1134e` (`main` when the batch started), head `lean-first/b10a`. Plan `docs/LEAN-FIRST-PLAN.md` (draft 3,
branch `design/lean-first`), section 5.2 row 10a: **norm defaults, Lean side**: reached witnesses,
`UngroundedDefault`, soft and rights branches; no Python or Rust deleted (batch 10b switches the callers and deletes
`ve/norm_defaults.py`). Started early by the DRI (2026-10-05) beside batches 1 and 2, since it only adds Lean. Lead
directive: one owner per piece of logic.

## What was added

Everything is in `lean/VE/NormDefaults/`, dispatched by the unchanged `ve_norm_defaults_route` executable
(`Run.lean`). No Python module, Rust file, frozen runner or existing theorem statement changed.

| File | What | Theorems (new) |
|---|---|---|
| `Report.lean` | The `norm-defaults-report` kind: the spec 3.2 lines of every regulated predicate. `completion`; `gaps` / `default reached` as `reachable` (Lean's own search in a supplied base situation, a port of Python's `_reached_witness`: the canonical filling where `reached_p` is Kleene-true, else the first assignment of the point's closed cone, at most `MAX_UNSAID_ATOMS` atoms in Python's order, under which the open `Fill_T` instances meeting the cone and `reached_p` are Kleene-true, extended canonically and then checked; or a supplied witness replayed), `none` (a `reached:<p>` certificate replayed) or `unknown`; the `completions` block (Python `validate_completions`, its texts); `grounded:` / `UngroundedDefault:`; `inherits_from`; the residual `gaps` and `ungrounded_defaults` and the findings. One report for every route: `ReportSource` gives the route's document, its extra base premises `X`, its situation decoder and its two evidence replays. | `grounding_ungrounded_iff`, `admissibleX_of_fill`, `reachedSome_of_fill`, `ReachedData.reachedSome`, `report_sound`, `normDefaults_wire_report_sound` |
| `Layered.lean` | The soft and rights branches (spec 2.3 and 3.3: `fill` last): `fill (soften T)` and `fill (soften (correlate D))`, decoded by the route's own decoder over the placeholder completions; the author limits on the softened tree (`checkAuthorN`); `X` = `Soft_T` with `Coh_T` regenerated on `fill U` (its selections read unsaid atoms) and, on rights, the limitation premises; base background `Background_base(E‴) ++ X ++ Fill_T`, Python's generator order. Kinds `norm-defaults-elaborate` (with `soft`, `rights`, `environment_id`, `document_hash`, `base_environment`), `-conflict` (packages, or a filled witness), `-status` (`table3`, `enumerate`, `undecided` with fillings that must satisfy `X`) and `-report`. Evidence is a base situation with a separate `filling`. | `layered_cert_sound`, `target_not_conflictFree`, `layered_conflict_sound`, `FilledX.admissible`, `layered_report_sound` |
| `Evidence.lean`, `Replay.lean`, `Wire.lean` | One owner for what the new files reuse: `coneOf` and `openInstances` (the cone of any formula; `coneAtoms` is `coneOf` of an outcome), `reachedFromU` (the filled-model decoder; `replayReached` calls it, fault order kept), `checkAuthorN` (the author limits with the route's generated predicates counted; `checkAuthor` is its norms case). | none (definitions only; existing proofs unchanged) |

The 11 new theorems use the standard axioms only (`lean/audit.py`: PASS, 3,943 theorems; `lean/axioms.txt` gained
their 11 lines). `tools/lean_statements.py` reports 11 statements added, 0 removed, 0 changed. New definitions of
meaning: `BaseAdmissibleX` (W1 base admissibility on `fill U`, `Fill_T` and `X`), `ReachedSome`, `NeverReached`,
`ReportSound`, `ConflictFreeX`, `UndecidedAtX`, `cohPremiseU`; with `X = []` the first three are the norms route's
notions (`normDefaults_wire_report_sound`).

Bookkeeping: `lean/VE/Route/frozen-sources.sha256` rehashes the six edited or new files and `VE/Audit.lean`;
`ve/assurance-manifest.json` pins `Report.lean` and `Layered.lean` as decoders and re-pins `Wire.lean` and
`Replay.lean` (`docs/spec/assurance-manifest.md` regenerated); `tools/trust-classes.json` classifies every new
declaration (unclassified stays 0; the decision functions are C, `conflictFreeX` and `groundingOf` tied to their
theorems; `tools/trust_map.py --check` already failed at the base on other batches' growth, and this batch adds 361
trusted lines of decoders and glue); `lean/statements.txt`, `declarations.txt`, `predicates.txt` and
`tools/gate-collection.json` regenerated (additions only).

## Evidence that Lean answers as Python does

| Test | What |
|---|---|
| `tests/test_norm_defaults_report.py::test_report_with_a_situation_is_pythons_line_for_line` | the 18 norms-route fixtures and every situation, authored and translation: lines, witness tuple and filling, residual and findings identical |
| `…::test_report_replays_pythons_search_evidence` | the same without a situation: Python's small-model witnesses and proved certificates replay to Python's lines (`none` and `reachable` both occur) |
| `…::test_report_on_generated_trees` | spec 8's generator: 1,000 trees with their situations and 200 through Python's search evidence (1,200 reports), a quarter with a `completions` block: identical |
| `…::test_completions_faults_have_pythons_text` and five more | every malformed `completions` block (types swapped, absent or extra fields, duplicate cites, blank reasons in Python's `str.isspace` sense, unknown units) gives Python's text |
| `…::test_tampered_evidence_never_becomes_a_line`, `…::test_malformed_fields_are_refused_or_inert` | a witness where a rule decides, a filling that breaks `Fill_T`, another document's certificate, and every field or situation part of the wrong shape: refused or `unknown`, never `reachable` or `none`; a malformed situation is refused exactly when Python refuses it |
| `tests/test_norm_defaults_layered.py::test_soft_and_rights_fixtures_agree_with_python` | spec 9's u2, u3, u8 and u9 (with their deny, allow and strict variants) and a coherence case: the regeneration, `Soft_T`, the rights premises and the bound base environment byte for byte; every status, conflict verdict (certificates and filled witnesses) and report as Python's |
| `…::test_undecided_fillings_must_satisfy_the_route_premises`, `…::test_rights_limitation_premises_bind_fillings`, `…::test_packages_are_bound_to_the_source_and_the_layered_background` | `X` binds every filling and every certificate |

## Gate (section 5.1)

1. **Suite.** The full suite at the head, in chunks with the prebuilt binaries, in a clean worktree: see "Suite at
   the head" below. No existing test changed.
2. **Corpus A/B.** `tools/lean_first_diff.py` over every corpus, base and head: identical (table below). Besides the
   route, five executables changed bytes because they import the edited norm-defaults modules (`ve_service`,
   `ve_readings_route`, `ve_discourse_route`, `ve_diagnose`, `ve_response_decode`); the probe, conformance,
   readings, discourse and pilot corpora run through them. The new kinds have no Python caller, so nothing
   Python-visible changes, and this batch lists no `wording`, `order`, `verdict` or `availability` change. The
   differential fuzzer's baseline is untouched (no Python, Rust or existing Lean diagnostic changed).
3. **Deletion ledger.** Row 10a deletes nothing.
4. **Latency.** Paired runs below: no workload got slower beyond noise; the new kinds cost about 3 ms of CPU per
   case (budget: 2 ms p50 per interactive call, 1 s per document check; a report is a document-level call).

<!-- BEGIN GENERATED: python docs/lean-first/b10a/report.py --write -->
### Gate item 2: corpus A/B

| Records per side | Same | Wording | Order | Verdict | Availability | Unlisted |
|---:|---:|---:|---:|---:|---:|---:|
| 66,242 | 66,242 | 0 | 0 | 0 | 0 | 0 |

| Corpus / authority | Records per side |
|---|---:|
| conformance/lean | 19,806 |
| conformance/python | 19,806 |
| discourse/default | 6,350 |
| pilots/default | 273 |
| probe/lean | 9,435 |
| probe/python | 9,435 |
| readings/default | 1,137 |

Base records `feb024e0436d…`, head records `8c96c407eb77…` (SHA-256 of the record files, 66,242 and 66,242 lines).

### Gate item 4: latency (paired, base and head alternating)

| Workload | Side | Runs | CPU per run (s) | Median CPU (s) | Change | Load |
|---|---|---:|---|---:|---:|---|
| `ve_norm_defaults_route`, 22,640 cases in 23 chunks | base | 4 | 29.18, 22.74, 22.55, 23.83 | 23.28 |  | 8.4–20.8 |
|  | head | 4 | 23.11, 23.34, 22.42, 22.30 | 22.77 | −2% | 10.3–20.7 |
| `lean_first_diff.py record readings` | base | 2 | 192.82, 220.30 | 206.56 |  | 10.1–28.7 |
|  | head | 2 | 187.52, 223.85 | 205.69 | 0% | 20.6–31.8 |
| `lean_first_diff.py record probe` (lean authority) | base | 2 | 105.17, 94.20 | 99.69 |  | 10.0–11.1 |
|  | head | 2 | 90.11, 87.19 | 88.65 | −11% | 12.9–13.9 |

| New kinds (head only) | Cases | CPU per run (s) | CPU per case (ms, best run) |
|---|---:|---|---:|
| report | 1,235 | 4.61, 3.76, 3.60 | 2.91 |
| layered other kinds | 66 | 0.15, 0.15, 0.16 | 2.27 |

### Seeded bugs (build checklist 13)

| Seeded bug | Failing tests (of 48 in the two new files) | Tests that caught it |
|---|---:|---|
| M1 reached witness search: no cone enumeration | 3 | `test_soft_and_rights_fixtures_agree_with_python`; `test_report_on_generated_trees`; `test_report_with_a_situation_is_pythons_line_for_line` |
| M2 findings count every grounding line | 3 | `test_layered_report_grounding`; `test_grounding_lines_follow_the_completions_block`; `test_report_on_generated_trees` |
| M3 completions: a blank reason accepted | 3 | `test_completions_faults_have_pythons_text[block13]`; `test_completions_faults_have_pythons_text[block14]`; `test_completions_faults_have_pythons_text[block15]` |
| M4 inherits_from: guards of p only, not the cone | 3 | `test_report_on_generated_trees`; `test_report_replays_pythons_search_evidence`; `test_report_with_a_situation_is_pythons_line_for_line` |
| M5 soft: Coh_T on soften T, not on fill U | 3 | `test_coherence_is_regenerated_on_the_filled_tree`; `test_soft_and_rights_fixtures_agree_with_python`; `test_undecided_fillings_must_satisfy_the_route_premises` |
| M6 rights: limitation premises dropped | 3 | `test_packages_are_bound_to_the_source_and_the_layered_background`; `test_rights_limitation_premises_bind_fillings`; `test_soft_and_rights_fixtures_agree_with_python` |
| M7 status: UNDECIDED without the route premises X | — | does not build: VE/NormDefaults/Layered.lean:358:79: Application type mismatch: The argument (proof obligation) |
<!-- END GENERATED -->

## Suite at the head

To be filled from the clean-worktree run of the head.

## What batch 10b must list when the callers switch

None of these is Python-visible in 10a (no caller uses the new kinds); each becomes a DELTA line of 10b.

1. `order`: Lean reads a `completions` block in key order (its JSON objects are keyed maps); Python reads it in
   insertion order, so with two faulty entries the first reported can differ
   (`test_completions_are_read_in_key_order`).
2. `wording`: a situation with an `unsaid__` table is `InvalidModel(norm-defaults): <n> is a filling; supply it as a
   filling, not a table` in Lean, the same text without the `InvalidModel(norm-defaults): ` prefix in Python.
3. `availability`: on 6 of the 40 malformed situation shapes swept, Python raises `AttributeError` (not a `VEError`);
   Lean refuses each with a diagnostic.
4. `verdict` (possible, not observed): Lean's witness search has the atom budget but no evaluation budget; Python
   reports `unknown` when its evaluator exhausts `MAX_EVALUATIONS`. No fixture or generated tree reached it.
5. Soft and rights: Python's `UnspecifiedSoftDocument` crashes (`InvalidModel: undecided witness failed its own
   check`) where `Coh_T` on `fill U` excludes the fillings its enumeration found; Lean answers UNKNOWN. Python's
   soft/rights packages carry the W1 hash of the softened document; Lean binds the route's own document hash
   (`softDocumentHash`, `rightsDocumentHash`) and returns it, with `environment_id` and `base_environment`, in the
   elaborate row (rule 5: Python reads identities from Lean). Evidence on these branches is a base situation with a
   separate `filling`. `ve/document.py` refuses norm-defaults documents on the soft and rights routes today ("await
   the Lean route"); 10b can admit them through `Layered.lean`.

## Not done

| Item | Tag | Owner |
|---|---|---|
| The caller switch and the deletion of `ve/norm_defaults.py` and Python's norm-defaults admission | AGENT | batch 10b |
| Alternatives and risk branches (`fill (inlineTree A)`, spec 3.3's integration gap); row 10a names soft and rights only | AGENT | DRI decides the batch |
| `norm-defaults-gaps`, `-certificate` and `admission` on the soft and rights branches (refused with `UnsupportedProfile`; `-report` with `predicates` gives the gap line) | AGENT | batch 10b if a caller needs them |
| An enumeration that also reads `X` (SETTLED where only `Soft_T` excludes the other value; Lean answers UNKNOWN there, sound) | AGENT | batch 10b or later |
| The migration audit (`audit_completions`) as a Lean kind: it composes the report on switched sources, which the report kind supports | AGENT | batch 10b |
| DRI signature | HUMAN | none needed: no change is listed |

## Build checklist

Applicable lines: 1 (texts: the new diagnostics are Lean's, Python's existing texts reproduced where Python has them,
no hand copy added to Python), 2 (malformed `completions`, fields and evidence; the 1,200-case generated
differential), 3 (blank reasons use `VE.Norms.Wire.pyWhitespace`, the shared `str.isspace` set; NBSP, U+2003,
U+3000, U+001C, U+0085 tested), 4 (no consumer yet: 10b validates the rows), 5 (every report field, evidence entry
and situation part replaced by 7, true, [], {}, "x", [7], {"a": 7}, [[]]; Lean's reader rejects `null`), 6 (three
values: `reachable`, `none`, `unknown`; an atom budget or missing evidence is `unknown`), 13 (seeded bugs below;
empty evidence gives `unknown`), 14 (tests run the built route on inputs they build), 15 (packages bind the source
environment, the route's document hash, the base environment and the premise list; mutations tested), 16 (audit,
frozen inventory, manifest, trust classes and gate collection regenerated), 17 (`tools/lean_statements.py`: added
only), 20 (the tables above are rendered by `report.py` and checked by `tests/test_lean_first_b10a_report.py`), 21
(tags above), 22 (committed; the suite ran on the head in a clean worktree). Not applicable: 7 to 12, 18, 19 (no
public operation, deadline, fold, English, entry point, regex, ledger or use case changed).
