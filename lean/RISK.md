# Risk in Lean (`lean/VE/Risk/*`)

Specification: [docs/spec/risk.md](../docs/spec/risk.md) section 7 (stage A, draft 3) and
[docs/spec/risk-PLAN.md](../docs/spec/risk-PLAN.md) item 2. This file lists the files, the choices made where
section 7 gives schemata, every theorem of 7.2 in plain words, the `ve_risk_route` cases and every deviation.
`lean/audit.py` audits every theorem: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`. No frozen
P0 file and no `lean/VE/Norms/*`, `lean/VE/Alternatives/*`, `lean/VE/Route/*` or `lean/VE/Time/*` source changed
(`python3 VE/Route/frozen.py`); `VE.lean`, `VE/Audit.lean`, the frozen-source manifest and `lakefile.toml` gained
imports, audit entries, manifest entries and the `ve_risk_route` target (root `RiskMain.lean`) only.

## Files

| File | Contents |
|---|---|
| `Cond.lean` | `LinForm`, `LinForm.normalize`, `NormLinForm`, `Cond` (atoms hold normal forms), `nnf`, boxes, `Scoped`, `Separable`, `UnitCoefficients`, `fmin`, `fmax`, the extremal valuations |
| `Derive.lean` | `possibleE`, `certainE` (the table of 4.3 on `nnf c`), the `=` witness `eqWit`, the canonical witness `witnessE`, and the endpoint theorems |
| `Decl.lean` | `RiskEnv`, `RiskDoc`, `E_risk` (`riskEnv`, `riskExtEnv`), the word bodies `orWorseF`, `lessWorstF`, `riskInline`, `withRiskDefinitions`, `toAlt`, the order `closure`, `WellFormedRisk` with the diagnostics of 6 and its facts `RiskValid` |
| `Severity.lean` | `risk_wellFormed_alt`, `severity_strict` |
| `Background.lean` | the slot premises and `riskPremises`, `BaseAdmissibleRisk`, `backgroundValidRisk`, `RiskConflictFree`, `riskConflictFreeCheck`; the policy theorems; `oldEnvRisk`, `compatFacts`, `ReductVia`, the expansion and conservativity |
| `Words.lean` | `risk_inline_faithful`, `LessWorst`, `lessWorst_strict`, profiles and `precaution_has_maximal` |
| `Record.lean` | `Decision`, `Entry`, `entryHash`, `withdrawnBefore`, the record and entry-content decoders, condition elaboration, `admitDecision`, `box`, sources, `Suff`, `Nec`, `Completed`, `regenerate`, the observation view, `validateDecision` (V1 to V11), the decision model (`decisionData`, `decisionModel`, `decisionRows`, `modelTables`), `statuses`; the record theorems |
| `Report.lean` | `Outcome`, `Endpoint`, `endpoints`, `current`, `perturb`, `outcomeAt`, `candidates`, `marginLimit`, `scan`, `scanInvalid`, `scanConflict`, the generic walk lemmas |
| `Piecewise.lean` | `status_piecewise_constant` and the three scan theorems |
| `Audit.lean` | `logPrefix`, `snapshotOf`, `Q1`, `Q2`, `auditQ12`, the untrusted `auditQ3`; the audit theorems |
| `Wire.lean` | profile gate, the strict `risk` block decoder, W6 units, `excludes`, `decodeRiskSource`, `decodeEntry`, `decodeSupplied`, `decodeLog`, the legend and the `risk-elaborate` outputs |
| `Admission.lean` | W2 graph admission with regenerated `risk:*` and `risk:profile:<word>` leaves |
| `Run.lean`, `../RiskMain.lean` | the replays, the wire theorems and the `ve_risk_route` executable |

## Choices where section 7 gives schemata

* **`RiskDoc`.** The complete original environment is carried as its declaration lists, `vocab :
  VE.Bridge.Vocabulary`, and `R.E` is *defined* as `R.vocab.environment`: the decision model enumerates the
  constants of each sort (4.4), which a function-valued `VE.Environment` cannot. `RiskDoc` also carries the
  policy identity `policy = (environment_id, document_hash)` that a record binds (A1) and the labels of `Γ`
  (V11 names a failing unit by its label). The spec's statements are unchanged (`R.E` elaborates as before).
* **`WellFormedRisk`** is `checkRisk` (the diagnostics of 4.1 and 6 in order, then alt's `validateAlt (toAlt R)`)
  followed by the Boolean `riskSemanticCheck`, from which `RiskValid` (the facts the proofs use) follows. Besides
  4.1 it checks four conditions the expansion needs and 4.1 implies for decoded sources: the role predicates and
  the chooser, action and harm sorts belong to `E` (so none is generated or the severity sort), no literal is of
  the severity sort or a class, and no definition shadows a generated name.
* **`possibleE`/`certainE`** are the first and second components of one evaluator `endsE` on `nnf c`; `endsE`
  swaps and negates at a `not`, which never occurs on `nnf c`, so no mutual block is needed (mutual blocks break
  the audit scanner).
* **`witnessE` for `=`** moves the quantities of the form in the order of the normal form (first occurrence in
  the condition), not in the record's quantity order: the proof then needs no permutation argument. The witness
  is canonical either way and the fixtures only fix `<` and `≤` witnesses.
* **Records.** `Decision` has two helper fields: `chooserLabel`, and `issues` (a problem found while decoding a
  cited entry's content, with the validation step that reports it: an unknown quantity at V1, a value off the grid
  at V3 or V4, a statement form at V6, a tag mismatch or an off-grid literal in a condition at V7), so the
  diagnostic order of 4.4 is kept although contents are decoded at admission. A missing estimator is `""` and a
  missing support is `none`. The two content-count limits (64 estimates and settings, 128 conditions and
  statements) are checked when the cited contents are decoded, after citation matching.
* **The view.** Validation, the decision model and the statuses read the record through `view R d`: the record
  with its estimate values erased (`strip`) and a finite list of observations (`obs`: each estimate's range check,
  each quantity's intersection check, the box's well-formedness, each condition's scoping, shared quantity and
  non-unit coefficient, and per cell the endpoint answers of `S`, `N` and `S ∧ ¬N`). `outcomeAt` is a function of
  the view of the perturbed record, which is what makes `status_piecewise_constant` provable.
* **Validation** ends in a Boolean gate `viewGate` (box well-formed, every cell's sides scoped, separable and
  unit-coefficient, `S = N` or `S ∧ ¬N` impossible, model data valid, alt's model checks, and the risk premises
  evaluated true on the decision model). The risk premises are therefore *checked* at V11 rather than proved to
  hold by construction; `risk_scenario_sound` needs them. They are expected to hold on every record that passes
  V1 to V10 (no fixture fails there), but no theorem states it. A duplicate alternative or quantity name is `DuplicateDeclaration: alternative <n>` /
  `DuplicateDeclaration: quantity <n>` at V1 (6 names no text for these).
* **The decision model**'s relation list puts `leads_to` and `risk__might_lead_to` first, so `modelTables` reads
  back exactly the regenerated lists. `entity` of 7.1 is `entityIn R d x` (the constant table depends on both).
* **Candidates** are deduplicated (`dedup`); the current value is included, so a scanned value always has a
  candidate strictly between it and the current value.
* **The audit.** Q1 on a record that is admitted but invalid is `notReplayable` with the validation diagnostic
  (4.10 names only admission failures). Q2 decodes every live estimate of the record's quantities in the prefix
  (not superseded before the decision) and compares Q1 verdicts.
* **The wire.** A case is `{"id", "kind", "environment", "document", ...}` with `document = {"norms",
  "units"?}`. `$string` literals, definitions and data flags are rejected on this route (as alt rejects the last
  two). The outer package binding is `(environment_id, document_hash, target)` with alt's document hash over the
  complete risk environment; the inner certificate binds `riskBaseEnvironmentJson`: the base environment with the
  blocks, the W6 extension, the regulated predicates and the `alternatives@0`, `risk@0`, `norms@0` profiles
  removed, and the severity sort, the class constants and the three generated predicates added. A Python prover
  must bind the same JSON.

## Theorems in plain words

Names have prefix `VE.Risk.` (the wire theorems `VE.Risk.Run.`).

| Theorem | Statement in plain words |
|---|---|
| `risk_wellFormed_alt` | A well-formed risk document is a well-formed alternatives document over `E_risk`. |
| `severity_strict` | The closed severity order is irreflexive and transitive. |
| `normalize_normal`, `normalize_eval` | The normaliser returns a normal form (distinct names, no zero coefficient) with the same value under every valuation. |
| `nnf_holds` | `nnf` keeps the meaning of a condition. |
| `possibleE_complete`, `certainE_sound` | On a scoped condition, a satisfying valuation in the box makes `possibleE` true, and `certainE` true means every valuation in the box satisfies it. |
| `possibleE_iff`, `certainE_iff` | On a well-formed box and a scoped, separable, unit-coefficient condition, `possibleE` holds exactly when some valuation in the box satisfies it, and `certainE` exactly when every one does. |
| `witnessE_sound` | Under the same hypotheses, a possible condition's canonical witness lies in the box and satisfies it. |
| `regenerate_sound` | On a valid record, a cell is `might` exactly when some completed case has the harm, and `leads` exactly when every completed case has it. |
| `certain_within_possible` | On a valid record every `leads` cell is a `might` cell. |
| `regenerate_witness` | Every regenerated witness is the valuation of a completed case with the harm. |
| `risk_inline_faithful` | On every structure admissible for `E_risk`, an inlined formula is true iff the original is true when the two words are interpreted by their bodies. |
| `lessWorst_strict` | Under the slot premises `less_worst` is irreflexive and transitive. |
| `precaution_has_maximal` | Under the slot premises every chooser with an alternative has one no other alternative beats (via profiles, finitely many). |
| `risk_expansion` | Every structure satisfying alt's background and the compatibility facts expands, on the old carrier plus one element per class, to a `BaseAdmissibleRisk` structure whose old reduct is the given one. |
| `risk_conservative` | Over the old signature, consequence under the risk premises equals consequence under alt's background with the compatibility facts. |
| `risk_conflict_free`, `alt_conflict_free_risk` | Accepted certificates for every W1 target (over `Background_baseAlt ++ riskPremises` or alt's backgrounds), or alt's conflict-freedom, give `RiskConflictFree`. |
| `risk_followable_sound` | FOLLOWABLE: an accepted certificate over `Background_baseAlt ++ riskPremises ++ Γ` gives `FollowableIn` in every document expansion of every `BaseAdmissibleRisk` structure satisfying `Γ`. |
| `risk_dilemma_witness_sound` | DILEMMA: a typed chooser of a valid finite witness passing `backgroundValidRisk` and `Γ` at which `¬followable°` evaluates true refutes the document-wide claim. |
| `admitDecision_sound` | An admitted record takes the decision entry's sequence number and its hash is authentic; every citation precedes it, matches an entry by id, sequence number and recomputed hash, and names nothing withdrawn before the decision. |
| `risk_scenario_sound` | A valid record's decision model is valid for the base environment, passes alt's validation with its signed rows and `backgroundValidRisk`, is `BaseAdmissibleRisk`, and its tables are the regenerated ones. |
| `status_piecewise_constant` | The outcome of a moved endpoint changes only between two adjacent candidates. |
| `scan_sound`, `scanInvalid_sound`, `scanConflict_sound` | Each scan returns the nearest candidate of its kind beyond the current value, and no value strictly between (or beyond, when it returns none) is of its kind (for `scan`: every such value keeps the status or is invalid or a conflict). |
| `snapshot_prefix` | The audit snapshot reads only the log prefix up to the decision. |
| `verdict_ignores_outcomes` | Two logs that agree up to the decision give equal Q1, Q2 and procedure lines for the same queried alternative. |
| `snapshot_no_hindsight` | An admitted snapshot's decision has the referenced sequence number, and every citation precedes it and matches a prefix entry by id, sequence number and hash. |
| `Run.risk_wire_scenario_sound` | A raw `risk-decision` replay decodes to its source, entry and supplied entries; the record is admitted, valid and within the candidate limit; the tables, the conflict check, the statuses and every scan are the Lean definitions'. |
| `Run.risk_wire_audit_sound` | A raw `risk-audit` replay decodes its source and log and reports `auditQ12`. |
| `Run.risk_wire_conflict_sound`, `Run.risk_wire_followable_sound` | Raw conflict and followability replays decode to a well-formed source and give `RiskConflictFree` and the FOLLOWABLE claim. |
| `Run.risk_wire_acceptance` | A raw W2 admission answer is the checked report bound to the complete risk source; its root follows from the regenerated premises and definitions and the remaining report assumptions. |

The remaining theorems are helper lemmas (list and box lemmas, the gap-stability and sign lemmas of
`Piecewise.lean`, the expansion lemmas) audited under the same allowlist.

## How `status_piecewise_constant` is proved

The outcome is a function of the view (above). Between `x` and `x + 1`, when not both are candidates:

1. no endpoint `w` of a cited estimate of the moved quantity equals `x` or `x + 1` (`Gap`), because `w − 1`, `w`
   and `w + 1` are candidates;
2. every bound of every estimate of that quantity, and hence the effective range under each combination rule, is
   *gap-stable*: it is the moved value at both points, or constant there and equal to such an endpoint (`GS`,
   closed under `min`, `max`, folds and the `latest` selection); the bound on the other side does not move at
   all; comparisons of gap-stable values agree at `x` and `x + 1` (`GS.le`, `GS.eq`);
3. for every atom of every record condition, the extremum that depends on the endpoint is `c·x + K` with `K`
   the matching extremum of the rest on the current box, and its sign changes only between two of the four
   threshold candidates (`sign_step`); the other extremum does not move;
4. so the boxes at `x` and `x + 1` agree on membership, point-ness, well-formedness and the signs of every atom's
   extrema (`boxStep`, `atom_step`), endpoint evaluation agrees (`endsE_congr`), every observation agrees
   (`obs_step`), and the views and outcomes are equal.

The scans evaluate every candidate beyond the current value; `walk` carries a candidate's outcome to the values
between candidates.

## The `ve_risk_route` cases

| Kind | Extra input | Output |
|---|---|---|
| `risk-elaborate` | none | `environment_id`, `document_hash`, `e_risk`, `legend`, `risk_premises`, `unranked_severities`, `inlined`, `alternatives`, `base_premises`, `followable`, `unmapped_obligations`, and W1's regenerated outputs |
| `risk-decision` | `decision` (the decision entry), `entries` (the supplied entries) | a diagnostic (with the witness case of `S ∧ ¬N` for `SufficientOutsideNecessary` and `RiskInconsistent`); or `verdict: CONFLICT` with the target and tuple; or `tables` (with witnesses), `statuses` (with firing rules and `by_default`), `worst_cases`, `margins`, `record_invalid`, `record_conflict`, `lines` (`unexamined_possible`, `assumed_ruled_out`, `point_estimates`, `default_decided`), `clear`, `conditional_on`, `decision_record_id`, `text` |
| `risk-conflict` | `packages`, or `witness` (`model`, `target`, `tuple`) | CONFLICT-FREE / CONFLICT / UNKNOWN |
| `risk-followable` | `packages` and `package`, or `packages` and `witness` (`model`, `chooser`) | FOLLOWABLE / DILEMMA / UNKNOWN / `not computed` |
| `risk-audit` | `log`, `decision` (`{"id", "seq"}`), optional `alternative` (else the `taken` entry) | `q1`, `q2`, `procedure`, `q3`, `not_concluded` |
| `risk-certificate` | `premises`, `conclusion`, `certificate` over `backgroundAlt ++ riskPremises ++ layer premises ++ premises` | `valid`, `conditional_on` |
| `admission` | W2 `document` with units and graph | `admitted`, `report`, `report_id`, `kinds`, `conditional_on` |

Cases without the profile, the block or a `risk-*` kind are delegated to `VE.Alternatives.Run`.

Tests: `tests/test_risk_lean_route.py` (51 cases, fixtures built by `conformance/risk.py`) runs the executable on
k1 to k12, k15 to k18, k20 to k22, k24 to k28, k30, k32 to k35, k38 to k40, the audit (k13, k14, k15, k32), the
environment checks (k9a, k26, stage B fields, the profile gate) and W2 admission.

## Status, deviations and what is not claimed

* Every theorem of 7.2 is proved, with the spec's hypotheses. Universe levels are explicit where 7.2 leaves them
  implicit: the structures of `risk_expansion` and `risk_conservative` share one universe `u`, and the wire
  theorems are stated at universe 0 (the Bridge models).
* Not implemented: the rendered report of 5.2 is a condensed `text` plus structured fields (margin sentences,
  worst-case wording and reasons are rendering, not certified, 7.4); `unranked_severities` is reported for the
  environment only, not per record; Q3 names the ruling-out source but not the contradicted estimate; the stage B
  and C fields are rejected as 1.1 requires.
* The deviations listed under "Choices" above: `RiskDoc` carries the declaration lists, the policy identity and
  `Γ`'s labels; `Decision` carries `chooserLabel` and `issues`; the `=` witness order; the view; the risk
  premises checked at V11; the content-count limits after citation matching; the risk route rejects `$string`
  literals; the inner certificate binding environment.
* Nothing is claimed about rendering, the diagnosis, Q3, the English surface (item 3), reader comprehension, or
  the truth of estimates, conditions, statements, the alternative list or the classification (7.4).
