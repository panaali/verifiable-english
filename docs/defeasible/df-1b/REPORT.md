# df-1b: the relay and the first pilot number (build report)

No DRI signature is reserved. There is no DELTA row: the flag is opt-in, and no answer given without it changes
(P-1's three answers without the flag are df-03's recorded ones, byte for byte). Trust grows by +0. **Size cut:** this
item delivers (1) the relay with its binding checks and tests and (2) the flag, the two-question order and the search.
(3) the English, (4) the `default:` lint prefix and the recorded route cases, and (5) the probe script go to **df-1bb**
(section 5).

Branch `feature/df-1b`, base main f39c78dde (the merge base). Plan and spec as on main (`docs/spec/defeasible-PLAN.md`
DF-1b, 2.2, 2.3, 2.8, 4.1, 4.2, 6.2, 6.3; `docs/spec/defeasible.md` 4, 5, 7.2).

**Statement gate.** DF-S passed (`manage-agents/defeasible-p3ver1.final.md`). This item adds no Lean statement and
changes no Lean file. The relay needed no answer field the shapes lack (section 2, item 4 notes one field the shapes
type only as `str`).

## 1. Plan rows delivered

| Plan row (DF-1b) | Where | Test |
| --- | --- | --- |
| `ve/defaults.py` sends `defaults-*` cases through `relay`, shape and binding only (R8) | `run`, `answer`, `bind_*` | `tests/test_defaults_answer.py` |
| every label in `assumptions` is one of the same case's `default_premises` (and in their order, each once) | `bind_certificate` | `::test_assumptions_and_basis`; P1 |
| `pairs` match `coherence_targets` one to one, in order | `bind_coherence` | `::test_pairs_and_collision`; B2 |
| every entity in a situation is in the request's model | `_situation` | `::test_forced_tuple_sorts` |
| `verdict`, `basis`, `form` are their enums | the shape (`check_row` in `run`, also on stubbed rows) | `::test_mutants_never_pass_as_answers`; B7 |
| `basis`, `form`, `assumptions` exactly with FOLLOWS; `needs` only with `strict_model` | `bind_certificate` | `::test_assumptions_and_basis`; P2 |
| each `forced` entry: a default rule of the source, condition index below its number of stated conditions, the rule's sorts and arity, entities in the model | `bind_model`, `_tuple` | `::test_forced_condition_index_rule_and_tuple`, `::test_forced_tuple_sorts`; P3, B5 |
| each pair and the collision's rule names are a pair of `coherence_targets`; each decider is the decider of one of its two rules (or `unstated`) | `bind_coherence` | `::test_pairs_and_collision`; B3 |
| `--assume-no-exception` on `ve document readings` (`ve/document/cli.py`, the package that replaced `ve/document.py`) | `_assume_no_exception` | `tests/test_defaults_lean.py::test_p1_follows_unless_an_exception_applies`, `::test_flag_refusals`; F1 |
| the strict question first; the default question only when the strict one has no certificate, with the strict countermodel as `strict_model` (none found: none sent, basis `unsettled`) | `ask` | `::test_zeta_strict_question_first`, `::test_alpha_needs_its_one_exception_and_the_strict_countermodel`; Q1, Q2 |
| the search reads `defaults-elaborate` | `_Search` (`Dflt_T`, the coherence targets) | every `ask` test; Q3 |
| `tests/test_defaults_lean.py`: 4.1's fixtures through the service | DF-α, α′, β (i) and (ii), β2, γ, γ′, ω, δ, ε, ζ, η, θ, ι, κ | 22 tests |
| `tests/test_defaults_answer.py`: one and two faults; each `CheckerUnavailable` or nothing shown changes; the three `forced` mutation fixtures | 7 genuine answers (each kind and verdict), every binding on both sides, each refusal named by its check | 16 tests |
| P-1 (4.2) | df-03's three probe documents through the flag | `::test_p1_follows_unless_an_exception_applies` |
| English DE1–DE7, DE11, DE12; `default:` in `tools/relay_lint.py`; route cases; `probe_defaults.py`, P-3 | **df-1bb** | — |

**Not on Lean's side.** The order of the two questions is the plan's approved design and is not in Lean on main (no
Lean kind asks both), so it is in `ask`; Lean decides each answer. `Document.lean` is not touched: the readings
command with `--conclusion` runs in Python's `ve/document/cli.py`, so sc-1b's queue does not apply.

### P-1, the first measured answers (before: df-03, after: this branch)

Before (df-03, `baseline.json`, main 702ff742): 0 of 3 (NONE each, over 0 fixed premises). After, `ve document
readings p1-<set>.ve.md --conclusion question-<set>.json --assume-no-exception`, verbatim:

```text
force-u0036-s05     {"question": "default", "kind": "defaults-certificate", "answer": {"assumptions": ["default:exception:clarify-ambiguity"], "basis": "needs", "form": "short", "verdict": "FOLLOWS"}}
force-u0156-s03     {"question": "default", "kind": "defaults-certificate", "answer": {"assumptions": ["default:exception:no-system-prompt-deception"], "basis": "needs", "form": "short", "verdict": "FOLLOWS"}}
force-u0263-s04-p2  {"question": "default", "kind": "defaults-certificate", "answer": {"assumptions": ["default:exception:comply-no-exploit-instruction"], "basis": "needs", "form": "short", "verdict": "FOLLOWS"}}
```

That is 3 of 3 FOLLOWS, basis `needs` and the short form, one assumption each, which is the plan's expected value. The
pilot's `metrics.json` field and P-3 wait for df-1bb's probe. df-03's strict control now answers on the strict
question: `{"question": "strict", "valid": true}`. Its review follow-up was that the old route answers NONE there.

## 2. Deviations and design points

1. **The strict question** is Lean's layered `norm-defaults-certificate` (`EntailsX U X Γ φ`, the document's own
   rules; the existing route answers without them, df-03's "For DF-1b"). It does not require a model, so DF-ι's
   contradictory premises answer `strict` (F-DF1′'s case); `defaults-certificate` on them is UNKNOWN (tested).
2. **The gate's search** (pair certificates, a collision) is in this item, because DF-γ and DF-δ need it. Pair
   certificates are bound with `norm_defaults_route._source_binding` (a new `listed` argument), the one Python site of
   layered meaning ids (identity lint); `Exc_T` is the layered row's `soft` without its last `Coh_T` entries, which
   must equal the coherence targets' premises (otherwise no gate evidence is sent, and the answer is UNKNOWN).
3. **DF-δ's assumptions** are `[default:exception:r1, default:exception:r2, default:ranking:…]`, not the plan's two:
   the certificate found uses r2's premise, and plan 2.9 claims no minimality. The test asserts the two the plan names.
4. **What no binding can check (R8: semantic fields are Lean's).** The relay cannot tell a dropped assumption among
   several, an in-range change of a condition index, or another `reason` text from Lean's answer. The `reason` shape is
   `str`. An enum of spec 5's four statuses, with the collision's rules echoed, would be shape work in Lean (follow-up
   for df-1bb or the shapes). The fuzz does not swap `reason` text for that reason. `defaults-elaborate`'s labels and
   formulas are Lean-generated and only bindable as distinct labels and targets equal to the soft elaboration's
   colliding pairs. Their mutants are tested end to end: each is `CheckerUnavailable`, changes nothing, or loses the
   search its evidence (every verdict UNKNOWN or the genuine one). Lean binds every certificate and model to its own
   regeneration (`::test_elaborate_mutants_lose_evidence_at_most`).
5. **Shown** is Lean's row without `id`, `status` and `situation`. The situation is the unsaid tables of the model the
   request sent (`situationJson`); its entities are bound, and df-1bb's English renders the request's model.
6. **Bindings beyond the plan's list**, each tested both ways: `forced` equals the rows of the default rules' exception
   tables in the request's model (names from Lean's bound soft elaboration, `soft_source`), in rule then tuple order;
   `basis` is `strict` exactly with no assumption; deciders are distinct; a reason is not empty.

## 3. Evidence

- `lake build` (no Lean change): passes. `python3 tools/rust_build.py`: pinned binary.
- `tools/trust_map.py --check`: PASS, K +0, S +0, trusted +0 (Python only; no allowance, no FOLLOW-UPS row).
- `tools/regen_generated.py --check`: 33 entries current (`.importlinter` regenerated for `ve.defaults`).
- `tools/relay_lint.py`: PASS, and `ve/defaults.py` alone passes every rule.
- `tools/gate_collection.py --check --prebuilt`: 19,570 collected; 36 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- Selected tests (`mac-pytest.sh --select`, Mac runner): run 1 (HEAD 403056c0) failed `test_identity_lint.py` (a new
  meaning-id site), fixed in 6798a6a2b; run 2 (HEAD 6798a6a2) failed only `tools/test_layer_policy.py` (the layer
  table's documentation), fixed in ce3060bfc, then passing alone. The final selected run is in section 6. No test of
  `main-known-red.txt` failed.
- Not run by me: the full gate (the chain runs it on the final HEAD).

## 4. Seeded bugs, trust, size, pilot bytes

Seeded bugs (Python; `mutants.json`, run by `evidence/run_mutants.py`, saved `evidence/mutants.out`). The controls
pass, and **all 21 fail their tests** (14 of the build, 7 of review F1). No Lean or Rust file changed.

| # | File: bug | Fails |
| --- | --- | --- |
| P1 | `ve/defaults.py`: an assumption label not in `default_premises` accepted (plan) | `test_defaults_answer.py::test_assumptions_and_basis` |
| P2 | `needs` accepted without `strict_model` (plan) | `::test_assumptions_and_basis` |
| P3 | a `forced` condition index at the rule's number of conditions accepted (plan) | `::test_forced_condition_index_rule_and_tuple` |
| B1–B7 | `strict` with assumptions; pairs as a set; deciders unbound; `forced` not the model's exceptions; a tuple's sorts unchecked; targets not the source's pairs; the shape check skipped | `::test_assumptions_and_basis`, `::test_pairs_and_collision` (B2, B3), `::test_forced_condition_index_rule_and_tuple`, `::test_forced_tuple_sorts`, `::test_elaborate_labels_and_targets`, `::test_mutants_never_pass_as_answers` |
| Q1–Q3 | the strict question skipped; no `strict_model` sent; no gate evidence sent | `test_defaults_lean.py::test_zeta_strict_question_first`, `::test_alpha_…`, `::test_delta_…` |
| F1 | `ve/document/cli.py`: the flag ignored | `::test_p1_follows_unless_an_exception_applies` |
| RF1a–RF1g | review F1: a collision's rules not a coherence target; a coherence situation's entities unbound; `forced` order unchecked; `--sentence`/`--narrowing` accepted; a document with no soft norms accepted; a reading set accepted; a model row's situation and `forced` both dropped | `test_defaults_answer.py::test_pairs_and_collision` (a, b), `::test_forced_order_rule_then_tuple`, `test_defaults_lean.py::test_flag_refusals` (d–f), `::test_forced_condition_index_rule_and_tuple` |

The plan's two renderer bugs (DE1 without "Unless an exception applies"; DE6 for DF-β (i)) go with the English to
df-1bb.

**Size** (`git diff --numstat f39c78dde`, hand-written): product 345 (`ve/defaults.py` 310, `cli.py` 25,
`norm_defaults_route.py` 10), tests 492, seeded-bug evidence 158 (`mutants.json` 121, runner 37), and this report.
That is about 1,000 lines without the report, above the ~600 guideline. At the half-way measurement the relay and
the flag came to 549 lines, and I cut there: everything after it is (1)'s required fuzz file, the fixes the checks and
the fuzz forced, and the evidence. The gate's search was not in the measured half's budget. Without it DF-γ and DF-δ
would only answer UNKNOWN through the flag.

**Pilot bytes** (estimate; nothing is claimed before a pilot audit): the constitution's defaults path is 8,764 B
primary (research share). This item makes P-1's three probes answerable (0 → 3 of 3, measured above on df-03's probe
documents, not in a pilot run). The pilot's "Feature upgrades" count moves only once df-1bb's probe runs.

## 5. Next items

- **df-1bb**:
  - the English: DE1–DE7 (DE4·u, DE7's decider sentences), DE11 and DE12 from Lean's `basis`, `form`, `forced` and
    `giveWayDeciders`, with the existing rule, condition and situation renderers, and the plan's two renderer seeded
    bugs;
  - `tools/relay_lint.py`: `default:` forbidden in `ve/`, and `ve/defaults.py` in `RELAYED`. feature/q1-4 also edits
    this file;
  - route cases of the flag recorded by `tests/route_case_recorder.py`;
  - `docs/defeasible/df-1b/probe_defaults.py` on P-1 and P-3 as small probe documents (L70), answers verbatim, and the
    pilot's `default_answer_probe`;
  - a typed `reason` (section 2, item 4), if the shapes' owner agrees.
- Then DF-2 (the meaning, Lean) alongside; DF-E1 (needs the DRI's model budget); DF-3.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report): 0a2a24ce0, f03f9d975,
ce3060bfc, 6798a6a2b, 403056c07, ccd6898ba, 0b7813002, eaac6e59b.

## 6. Final selected run

Run 3 (`mac-pytest.sh --select`, Mac runner, HEAD 3cfbd44d, clean) ran all 275 selected units. Two failed:

- `test_defaults_answer.py::test_elaborate_mutants_lose_evidence_at_most[gamma]`: a RecursionError. The test's stub
  handed the 10k-deep retype to the relay without the transport's decoder.
- `test_nested_pytest.py::test_every_pytest_command_is_built_by_the_builder`: the mutant runner built its own pytest
  command.

Both were fixed in the next commit: the stub decodes through `_decode_json`, and the runner uses
`tools/nested_pytest.py`. After the fix, `tests/test_defaults_answer.py` and `tests/test_nested_pytest.py` pass
(45 passed). The runner was rerun with the builder's command: all 14 bugs fail (`evidence/mutants.out`). No product
file changed after run 3.

## 7. Review fix (df-1b-review.final.md)

**F1 (B): checks tested on one side only.** The class is "a binding check no fixture needs". Fixed structurally:
`tests/test_defaults_checks.py::test_review_f1_every_check_is_needed_by_a_both_sides_test` reads every check from
the source (`tests/check_mutants.py`, the AST enumeration `tests/test_rights_licence_relay.py` used, now shared): each
`if ...: raise` of `ve/defaults.py` and the flag's checks in `ve/document/cli.py`, weakened one sub-condition at a
time or made always true, and each helper check call deleted, 81 seeded bugs in all. Each must fail one of the
both-sides tests (`BOTH_SIDES` and `test_flag_refusals`); a check added later is enumerated too. The tests read Lean's
genuine rows asked once per session, so the 81 runs take seconds. Planting an unneeded check makes it fail
(`row.get('zzz') -> False` survives).

To make every check needed, each refusal now names the check that must refuse it (`_refused(what, ...)`), and each
fixture breaks one check alone:
- the collision's rules: no witness, the witness's rules not the row's, and both moved to a pair that is no
  coherence target, each alone; the coherence situation's entities in and outside the witness model; three distinct
  named deciders (DF-γ′);
- `forced` order: Lean's four-entry DF-β2 row reordered within a rule, across rules and reversed
  (`::test_forced_order_rule_then_tuple`);
- the model row's verdict: situation and `forced` both absent with DOES-NOT-FOLLOW, both present with UNKNOWN; the
  certificate row's verdict: `form` missing with FOLLOWS, `form` or no reason with UNKNOWN;
- `run`: a row with another `id` is refused by the shape, which binds `id` to the request. `run`'s own id check could
  never fire after it, so it is removed (one owner);
- the flag (`test_flag_refusals`, `ask` stubbed so a refusal is shown to come before any question): no conclusion,
  `--under`, `--sentence`, `--narrowing`, a document with no soft norms, p2-ce4, and on the loaded P-1 document a
  content-bearing reading set alone and a reading set alone; the P-1 document itself is asked.

PROBE F1 failed before the fix (all three mutants survived) and passes after it (each fails a test). Seeded bugs
RF1a–RF1g are in `mutants.json` and fail their tests (`evidence/mutants.out`). No Lean or Rust file changed; trust
+0; no DELTA row.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** PASS: `test_defaults_answer.py::test_mutants_never_pass_as_answers` retypes
   each member to 7, 1.5, true, null, [], {}, "x", "\ud800" and a 10k-deep list, through the transport's
   `_decode_json`, and `run` re-checks the shape on every row. Request side:
   `test_defaults_lean.py::test_a_malformed_conclusion_is_a_diagnostic`. The transport and its 0xff handling are
   unchanged (`LeanService`).
2. **Every deliverable built.** PASS: section 1 and the df-1bb cut (size rule). No Python copy of a Lean decision: the
   bindings read the request and Lean's other rows. No permanent report test. No file overlaps a branch in flight:
   `relay_lint.py` (feature/q1-4) is left to df-1bb.
3. **Tests can fail.** PASS: 21 seeded bugs, `evidence/mutants.out`, and every check's 81 enumerated weakenings and
   deletions (`tests/test_defaults_checks.py`, section 7). No Lean change, so no `trust_mutants` run.
4. **Python, Lean and Rust agree.** PASS: `::test_p1_follows_unless_an_exception_applies` compares the answer without
   the flag with df-03's saved stdout, byte for byte; `_source_binding`'s default path is unchanged
   (`test_norm_defaults_soft_kinds.py` passes). The fixtures include two-sort tuples (`::test_forced_tuple_sorts`) and
   hyphenated rule names next to their generated tables (P-1).
5. **R8 binding.** PASS: an undeclared rule (`r9`), a shifted index, an extra or duplicated row and an empty list are
   refused (`::test_forced_condition_index_rule_and_tuple`, `::test_pairs_and_collision`,
   `::test_elaborate_labels_and_targets`, `::test_assumptions_and_basis`). Input side: an entity outside the model and
   wrong arity (`::test_forced_tuple_sorts`).
6. **Gate evidence matches the final HEAD.** PASS: base is the merge base f39c78dde, the commit list is from
   `main..HEAD --no-merges`, and the chain gates the final HEAD.
7. **No unsigned item.** PASS: no DELTA row; trust +0.
8. **Every user-visible change in DELTA.** PASS: without the flag nothing changes (`::test_p1_…` against df-03's
   saved answers). The flag is new, opt-in behaviour.
9. **Test selection.** PASS: the selection ran the new files and the two checks that failed (`test_identity_lint.py`,
   `tools/test_layer_policy.py`). Each seeded bug fails a test in the selected `tests/test_defaults_*.py`.
10. **Statements say what is claimed.** N.A.: no Lean statement or proof changed.
11. **Budgets fail closed.** PASS: `test_defaults_lean.py::test_an_empty_budget_is_unknown` (`MAX_STEPS` and
    `MAX_DOMAIN` 0: UNKNOWN, never FOLLOWS). No fixed waits.
12. **No CPU or memory regression.** N.A.: no existing path changes; the flag's search runs only when asked. Each
    fixture question takes 1–7 s on the VM. No pilot run (L70).
13. **Test-removed trailers.** PASS: `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.
