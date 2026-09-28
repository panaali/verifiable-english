# Speech acts in Lean (`lean/VE/SpeechActs/*`)

Specification: [docs/spec/speech-acts.md](../docs/spec/speech-acts.md) section 8 (draft 4, the item-1
statements), plan [speech-acts-PLAN.md](../docs/spec/speech-acts-PLAN.md) item 2. This file lists every
definition the statements read, every theorem in plain words, where the Lean deviates from the statement
schemata, and what is not done. `lean/audit.py` audits every theorem below: no `sorry`, only `propext`,
`Classical.choice` and `Quot.sound`. No frozen P0 file, no `lean/VE/Route/*` and no `lean/VE/Norms/*` source
changed; `VE.lean` and `VE/Audit.lean` gained imports and audit entries only, and `lakefile.toml` gained the
`ve_speech_acts_route` target (root `SpeechActsMain.lean`) without changing existing targets.

## Files

| File | Contents |
|---|---|
| `Tree.lean` | `Force`, `Mode`, `Scope`, `Command`, `Query`, `Question`, `Answer`, `SpeechDoc` (regulated declarations in the core); `regOf`, `actSorts`, `addresseeConst`, `eqGuard`, `demand`, `policy`, `premises`, `En`, `boundTuple`, `queryPremises`, `pinnedAsserted`, `trivialQuery`, `combine`, `core`; the executable `checkSpeech`/`validateSpeech`/`WellFormedSpeech` and `ValidSpeech` |
| `Demand.lean` | the section 8.2 theorems and their helper lemmas |
| `Answer.lean` | `presupposition`, `tokens`, `correct`, `AnswersAt`, `answerEval`; the section 8.3 theorems |
| `Consequence.lean` | the section 8.4 theorems; `entails_lower` (a structure lifted along `ULift`) |
| `Wire.lean` | the profile allowlist, the strict scope block, the canonical environment, `decodeSpeechEnvironment`, `scope_in_identity`, the unit and document decoder (`Decoded`) |
| `Run.lean`, `../SpeechActsMain.lean` | the `ve_speech_acts_route` executable and the soundness of its replays |

`eqGuard`, `demand`, `policy` and `premises` live in `Tree.lean` rather than `Demand.lean` (spec 8's file list)
because `WellFormedSpeech` checks W1's `WellFormed (policy D)`.

## Definitions under statement review

| Name | Meaning |
|---|---|
| `eqGuard D c` | `conj (eqsFrom n (you :: args))`: `var n = @you`, `var (n-1) = @a₁`, …, `var 0 = @aₙ`, right-nested; one equality per situation variable (4.2) |
| `demand D c` | the W1 node `cmd-<u>` on `c.act` with sign `force = require`, guard `.and (eqGuard D c) c.guard`, no carve-outs, no edges (8.1 verbatim) |
| `policy D` | `⟨D.E, D.lits, ⟨D.regulated, [], D.norms ++ D.commands.map (demand D)⟩⟩` |
| `premises D` | `background (policy D) ++ elaborate (policy D).T ++ assertedFormulas D` |
| `boundTuple D c S` | the constants `you :: c.args` denoted in `S`, in argument order (`none` if one does not denote) |
| `presupposition D q` | `⊤` except single choice: `(⋁ P(aᵢ)) ∧ ⋀_{i<j} ¬(P(aᵢ) ∧ P(aⱼ))` with `anyF`/`allF`; reading questions also get `⊤` (their presupposition is the open term, carried on the wire) |
| `tokens D q` | polar `[yes, no]`; single choice the domain; complete list every sublist of the domain in domain order (`sublistsOf`); follows and reading questions have none (their outcomes are judgments and nominations) |
| `correct D q a` | polar `body`/`¬body`; `.one a` → `P(a)` for a domain member; `.all S` → `⋀_{a∈S} P(a) ∧ ⋀_{a∈dom∖S} ¬P(a)` for a sublist `S` (tested with `List.isSublist`); `none` otherwise |
| `AnswersAt D q S a` | 8.1 verbatim: a token, `H` true, and its correctness formula true |
| `WellFormedSpeech D` | the section 7 diagnostics in its order (scope block, commands, questions, asserted typing, `UnknownRule: rule cmd-<u>`, W1 `validate` of `policy D` verbatim, queries), then the Boolean `semanticSpeech`; the profile gate, bindings, reading-question meanings and query regeneration run in the decoder |
| `combine D₁ D₂` | `ScopeMismatch: <task₁>, <task₂>` when the scope blocks differ; otherwise the concatenation when environment, literals and regulated declarations agree. Environment equality is not decidable on the function-valued `VE.Environment`, so `combine` is noncomputable (the specification-level operation); the executable form compares environment ids |

## Theorems in plain words

Names have prefix `VE.SpeechActs.`.

| Theorem | Statement in plain words |
|---|---|
| `policy_wellFormed` | A well-formed speech-act document regenerates a W1-well-formed policy. |
| `demand_shape` | Every command rule has no carve-outs, no precedence edges, the realising predicate, and a guard typed in that predicate's situation context. |
| `demand_polarity` | `require` gives sign + on an obligation-role predicate; `forbid` gives sign − on a permission-role predicate. |
| `demand_applies` | At a typed tuple, the command rule applies exactly when the tuple is the bound one and the guard holds. |
| `demand_consequence` | Where the norm elaborations hold, at the bound tuple with the guard true and no opposite rule deciding, the realising relation holds exactly when the force is `require`. |
| `demand_conflict_local` | Where an opposite rule also decides at the bound tuple, the norm elaborations cannot all hold. |
| `demand_conflict` | Under W1's `AgreesBelow` below the realising predicate, the same situation makes the base restriction a W1 conflict. |
| `scope_single` | Every command rule is guarded by the scope's one addressee: its equality guard mentions no predicate and its bound tuple starts with the addressee's denotation. |
| `answers_polar`, `answers_one` | At most one polar answer; at most one single-choice answer. |
| `answers_all`, `answers_all_empty` | Exactly one complete-list answer in every structure; the empty list when no alternative satisfies the body. |
| `answers_presupposition` | Where the presupposition fails no token is an answer. |
| `support_sound`, `support_conditional_sound` | A certificate for `premises ⊢ H ∧ F(a)` makes `a` an answer in every admissible model of the premises; one for `premises ++ [H] ⊢ F(a)` does so wherever `H` also holds. |
| `support_exclusive`, `support_exclusive_one` | Opposite polar answers, or two distinct single-choice answers, are both certified only over unsatisfiable premises. |
| `model_answers`, `model_presupposition_failed` | The finite evaluator's answer test is exactly `AnswersAt` in the model; with `H` false it accepts nothing. |
| `countermodel_not_negative` | A countermodel to the body gives "no" in that model only; given a premise model satisfying the body, "no" is not an answer in every premise model. |
| `follows_sound`, `gap_sound`, `follows_gap_exclusive` | An accepted certificate over `Π_q` is entailment; a validated countermodel refutes it at every universe; the two never coexist. |
| `query_target_separate` | The stored premise list of a query is the regenerated pinned list, and a target among its premises is flagged `trivialQuery`. |
| `premises_core`, `questions_no_premises`, `dormant_invariance` | Premises and policy are functions of the active core; questions contribute nothing; documents with one core replay the same certificates and have the same conflict status. |
| `speech_route_acceptance` | W1's `norms_route_acceptance` on the regenerated policy, verbatim. |
| `answer_bridge_sound` | The answer-to-claim bridge licenses exactly `H ∧ F` of a certificate-supported answer. |
| `combine_scope`, `two_task_separation`, `policy_rules` | A successful combination has one scope and one environment and concatenates the commands; different scopes are `ScopeMismatch`; every rule of a policy is an author norm or a demand of the document's own commands. |
| `Wire.scope_in_identity` | A decoded environment's canonical form carries exactly the canonical encoding of its scope block, so `environment_id` binds the scope. |
| `Wire.decoded_active_commands`, `Wire.decoded_premises` | For a decoded document: a command is in the core exactly when some unit of kind `instruction`, specified meaning and not pending carries it; the premise list is regenerated from active norms, active commands and fixed assertions only. |
| `Run.speech_wire_answer_sound` | A `speech-answer` replay whose certificate is accepted establishes the answer on every admissible model of the regenerated premises (conditionally, or as a presupposition failure, by evidence kind); on the model path the evaluator's answers are exactly `AnswersAt`. |
| `Run.speech_wire_consequence_sound` | `follows` from a replay is entailment over the regenerated `Π_q`; `gap` is its refutation; never both. |
| `Run.speech_wire_conflict_witness_sound` | A `CONFLICT` witness on the regenerated policy refutes its conflict-freedom and the document property. |
| `Run.speech_wire_conflict_free_sound` | A `CONFLICT-FREE` package replay makes every base-admissible structure conflict-free for the regenerated policy (W1's `conflictFreeCheck_sound`), the hypothesis of `speech_route_acceptance`. |
| `Run.premiseStatus_sound` | A model status is a model of the checked list; an inconsistency certificate refutes every admissible model of it. |

The remaining theorems are helper lemmas (formula typing and closedness, `eqsFrom` denotation, sublists and
pairs, JSON object lookup after insertion, the `ULift` lift) audited with the same allowlist.

## Deviations from the statement schemata

* **Universes.** `countermodel_not_negative` fixes one universe for `S'` and the quantified `S`, and
  `speech_route_acceptance` one universe for all its structures (as W1's `norms_route_acceptance` does); the
  schemata leave the levels implicit and would otherwise be unprovable. `gap_sound` is proved for `Entails` at
  every universe (`entails_lower`).
* **Unused hypotheses.** Several statements carry hypotheses their proofs do not need (`hS` in
  `demand_applies`, `hno` in `demand_consequence`, `hS` in `answers_all`); the statements are kept as written.
* **Scope block placement.** `speech_acts` is a top-level field of the environment object, beside
  `vocabulary`: `scope_in_identity` reads it with `b.getObjVal? "speech_acts"` on the canonical environment.
  3.1's excerpt shows it beside `predicates`; the Python side must use the same placement.
* **Proof-task act phrase.** Resolved in spec draft 5 (16): 1.4's act is `{0} submit a proof of {1}`, which
  W1's frozen act-phrase linter accepts (`for` is reserved; `VE.Norms.Wire.actReserved`, Python
  `ve/environment.py` `RESERVED`); neither checker relaxes the linter.
* **Wording-level checks.** `ModeMismatch` needs the English wording (plan item 3); query targets are read
  from the stored records, whose premise ids are compared with the earlier asserted units (`QueryMismatch`).
* **Diagnostics without fixed text in section 7.** A command whose argument count or sorts do not fit is
  `TypeMismatch: invalid command fields for <u>`; an asserted unit that does not type is `InvalidInput:
  ill-typed asserted unit <u>`; environment mismatch in `combine` is `InvalidInput: combined documents need one
  environment identity`.
* **Meaning ids (3.5).** A command's `ast` is `{"command": {"force", "act", "args", "guard"}}`, plus, for a
  proof task (a slot of sort `query`), `"query": {"id", "premises": [premise meaning ids], "target": target
  meaning id}`; a question's is `{"question": {"mode", ...}}` with its body, sort and domain in wording order, the
  query's identity for `follows`, or the set and version. Spec draft 5 (3.5) fixes this JSON shape, and
  Python's `SpeechDocument.meaning_ids` digests the same objects (conformance-tested for both query kinds).
* **Paraphrases** follow 2.1 (`In this task, you are required to click check.`); fixture α's "you must" wording
  is not used. A guard renders as `, where the stated condition holds` until the English layer exists.
* **Premise status.** Lean has no search budget; without evidence the status is `UNKNOWN (no premise-status
  evidence); vacuous: unknown`.
* **Model path.** A model supplies base tables only; regulated tables are computed from the completed outcomes
  in layer order, then the model must satisfy the whole checked list (elaborations included) and
  `Background_base`.

## The `ve_speech_acts_route` cases

Every case is `{"id", "kind", "environment", "document", ...}`; the environment carries the three allowlisted
profiles and the top-level `speech_acts` block; `document` has `units` (W2 unit objects with `id`, `span`,
`kind`, optional `meaning`, `support`, `content`), optional `queries` and optional W2-form `reading_sets`
(read for `unit`, `version`, `status` and, for an authored version, its one reading's `kind` and
`content`: the latest version of a unit's set decides, open keeping it pending, authored supplying its
meaning). Wire constants are declaration names (lower case). The frozen restricted JSON input parser
rejects `null`, so W2's unelaborated (`"content": null`) candidates cannot reach the route; an open set's
candidates are not read, and an authored choice needs its content.

| Kind | Extra input | Output |
|---|---|---|
| `speech-elaborate` | none | `environment_id`, `scope`, `legend`, `premises` (the regenerated `premises(D)`), `policy` (W1 `norms-elaborate` output), `commands` (rule, paraphrase, `meaning_id`), `dormant`, `questions` (with `meaning_id`), `queries` |
| `speech-answer` | `question`, `evidence` (`certificate` or `conditional` with `answer`, `presupposition_failed`, `model`), optional `premise_status` (`model` or `inconsistent`), optional `model_id` | the answer line of 5.3 |
| `speech-consequence` | `query`, `certificate` and/or `model`, optional `premise_status` (as `speech-answer`) and `model_id` | `follows (certificate; premises: <status>; vacuous: <no, yes or unknown>)`, `gap (model <id>)`, `unresolved (no accepted evidence)`; `CheckerConflict` when both hold |
| `speech-conflict` | `packages` (target → `{"environment_id", "document_hash", "target", "certificate"}`) | `CONFLICT-FREE`, or `UNKNOWN` with the first target lacking an accepted certificate; the outer binding is the canonical environment id, the document hash `ve-speech-acts-<identity version>` over `{"environment_id", "document"}` and the target; the inner certificate binds the regenerated base environment (scope block, regulated predicates, `speech-acts@0` and `norms@0` removed), `Background_base` and `∀x̄. ¬conflict` |
| `speech-conflict` | `witness` (W1's shape) | `CONFLICT` or `UNKNOWN` on the regenerated policy |

Cases without a speech-act construct (profile, block, `speech-*` kind, `binding` unit, command or question
content) delegate unchanged to `Norms.Run.runCase`. A query whose target is one of its pinned premises carries
the warning `TrivialQuery: <query id>` in `speech-elaborate`. `tests/test_speech_acts_lean.py` runs section 9
fixtures against the executable; the Python prover serves only as an untrusted certificate search over the lists
Lean regenerates. `tests/test_speech_acts_conformance.py` compares Python and Lean regeneration and answer
evaluation with Rust's FOL evaluation of their common finite-model projection. It also exercises a complete
source file through Python's experimental inspection path; Rust has no speech-act document decoder.

## Not done

* **Section 8.5's wrapper and admission.** `SpeechSource` (W2's identity payload, source bytes and fences,
  structured open terms, reading sets and narrowings), `SpeechAdmitted`, `source_retained`, `active_commands`
  over `SpeechSource` (`Wire.decoded_active_commands` is the analogue over the present decoder),
  `bindings_withheld` and `speech_wire_acceptance` are not implemented; the `admission` kind on a speech-act
  input is rejected with `UnsupportedProfile: case kind admission is not available on the speech-acts route`.
  It needs the `ve-document@2` JSON (front matter, source, fences) as the route input and Lean decoders
  mirroring `ve/readings.py`'s `validate_reading_sets` and `validate_narrowings`.
* **Records.** Answer, compliance and nomination records are accepted as document keys but not decoded; there
  is no compliance line and no nomination status; binding units have no meaning id.
* **Route-wide conformance and English fidelity.** Python's experimental `SpeechDocument`, `SpeechSource` and
  restricted English parser are present. The section 9 shared fixtures above cover a subset of semantic results;
  Rust still has no speech-act parser or admission route. W8 replay/approval, all-derivations English checks and
  the human fidelity gate (plan item 3) remain open.
