# Commands and questions in VE

2026-09-28 · Design proposal against `df874bd`; no implementation or new coverage claimed.
Four body pages (A4, 11-point text, 18 mm margins), followed by a summary. Proposed names are versioned contracts, not shipped APIs.

## 1. Decision and evidence

Make **COMMANDS** (`instruction`) and **QUESTIONS** (`question`) first-class typed content, retaining W2's existing kinds. A command directs an addressee to act; a question requests a response satisfying an answer contract. Neither asserts its embedded proposition. Checking a request's meaning is separate from checking an answer or evidence of compliance. Merely recognising an imperative or question mark earns no semantic coverage.

**Evidence inspected.** The [web catalogue](../../../ve-webapp/webapp/vocabulary/catalogue.json) at web commit `ad1bb360` records **265 SENTENCE segments: 120 without gaps, 145 with SyntaxError; 129 LABEL segments; five dynamic gap paths**. These are stored parser classifications, not a fresh audit or source-byte coverage. Catalogue SHA-256: `f6e343808b098da34b2376d28fd4bf10ce55c5f0dd2db6e5ff1a56e061265bfa`. Its [measurement README](../../../ve-webapp/webapp/vocabulary/README.md) explicitly names commands/questions as gaps and requires a runtime policy for dynamic text. Examples include “Open the writing desk.”, “Choose authoring or translation mode.”, “Change example now?” and “Did every sampled district report a drop?” Other failures concern time, quantities, causation, definitions and vocabulary; 145 is not a speech-act opportunity count.

The [current tutorial](../onboarding/ve-tutorial.html), especially its worked arguments and demo instructions, asks whether conclusions follow and tells readers to choose examples. [VE's README](../../README.md) also mixes executable command examples, explanations and instructions. Code samples are quoted content, not automatically active instructions. In [OpenStax, Elementary Algebra 2e, chapter 3 review exercises](https://openstax.org/books/elementary-algebra-2e/pages/3-review-exercises) (accessed 2026-09-28), exercises 339–340 request reflection and explanation; 341 asks for a population count; 342 directs the student to find a count. This small evidence sample motivates distinct response contracts, not a textbook coverage estimate.

**Build on the merged boundary.** Reuse [W1 norms](norms.md) for obligations/prohibitions, [W2 documents](document.md) for spans, kinds, readings and open terms, [W3 definitions](../../lean/VE/Definitions/STATEMENTS.md) for typed aliases/bodies and dependency-preserving citations, and the [natural view](../natural-view.md) for writable/rendered English parity. W2 labels already exist; speech-act elaboration does not. [Integration gaps](../INTEGRATION-GAPS.md) still gate W1/W3/data combinations, non-assertion readings, W8 authoring and full-document natural rendering.

Use a new opt-in `speech-acts@0` document route, with `ve-document@2` content and `ve.prose@2` presentation. Preserve old routes, IDs, canonical bytes, certificates and printers. Start with existing FOL/W1 fragments; reject unsupported combinations. Follow [VISION](../../VISION.md): elaborate by default; any inference needing new logic requires a committed pilot failure, independently specified semantics and a verified profile. No temporal, causal, epistemic or execution logic is smuggled into an action name.

<div style="break-after: page;"></div>

## 2. Semantics and boundaries

**Command.** Store issuer, typed addressee, context/scope, force (`require` or `forbid`), declared act and arguments, guard, and W1 policy/rule reference. The context explicitly binds “you”, definite objects and the applicable task/session. Missing bindings leave a repair case; they never mean every reader forever. The issuer's authority is provenance or a named assumption, not a theorem.

Independently interpret a direct command as a document-level demand on that addressee in that scope. Its normative realization uses W1's applicability, selection and completion semantics: positive force contributes `required_act(args)`; negative force contributes `¬permitted_act(args)`, **not** `¬required_act(args)`. Bind the addressee/objects with equality guards in a typed W1 rule. Regulated declarations, duals, defaults and priorities must be explicit and identity-bound; never silently replace a document's defaults. Unscoped acts use the pinned task context, not invented time arguments. N-ary or temporal requirements beyond the admitted route remain unsupported.

An active authored directive supplies the named norm to that document's policy. A quotation, example or reported directive supplies none. Adopting it requires a separate attributed adoption with a verified norm bridge and retained provenance. Requests, advice and invitations are not automatically hard duties; ambiguous source force stays in a reading set. “Please” may preserve force only after approval. Norm checking can establish requirements/conflicts; it cannot establish execution, authority, ability, deadlines or fulfilment. Reading or checking a command never executes it.

**Question.** Store asker, addressee, context, response mode, domain, presuppositions, and a typed answer contract. For an ordinary finite question, each response token `a` has a closed correctness formula `F(a)` in the pinned environment: `Answers(Q,M) = {a | M satisfies F(a)}`. A polar question about `P` has `{yes ↦ P, no ↦ ¬P}`. A finite “which” question has one formula per named alternative; single-answer mode requires exclusivity, while an exhaustive answer `S` requires all selected alternatives true and every unselected alternative false. An empty exhaustive answer is legitimate. The list's completeness and singular existence/uniqueness are explicit presuppositions, never facts inferred from asking.

Given admissible premises `B`, an answer is supported by a replayed proof of `B ⇒ F(a)` (including required presuppositions), or is evaluated only in an explicitly supplied valid model. Lack of proof is UNKNOWN, not “no”. A countermodel to `B ⇒ P` does not establish `B ⇒ ¬P`. **Consequence questions** instead request a certificate of entailment or a checked countermodel for the pinned `B,P`; search exhaustion is a third report outcome, not a truth-valued answer. Every answer retains its assumptions, evidence kind and vacuity status.

“Which reading did you mean?” binds a reading-set version and asks about the addressee's intent. A signed nomination records testimony/author choice, not proof of intent or fidelity; none/multiple/outside-set responses reopen clarification. “Prove that …” requests a certificate for a pinned premise/target pair; it never adds the target as a premise. “Answer question 2.” requests a linked response, without making every question an obligation. Explanations and unrestricted mathematical solutions need declared rubrics or richer profiles; unsupported content stays visible.

<div style="break-after: page;"></div>

## 3. English, admission and honest reports

These are proposed one-reading wordings, conditional on visible, uniquely bound context. Notation belongs in the inspector, never in reader-facing text.

| English | Sole admitted reading / check |
|---|---|
| “Click Check.” | This instruction requires its addressee to click the uniquely named Check control in this task. No claim that a click occurred. |
| “Do not share the token.” | This instruction forbids its addressee's declared sharing act on the bound token in this scope. The recipient scope must be declared; no invented definition of disclosure. |
| “Open the writing desk.” | Require the bound opening act; opening, reading and editing are distinct acts. |
| “Is Atlas reviewed?” | Request whether the declared property holds of Atlas; yes/no correctness is the property/its negation. |
| “Which of Atlas and Beacon are reviewed?” | Request the complete subset of these two named alternatives satisfying that property, including none. |
| “Which reading did you mean?” | Request one intended reading from the displayed, versioned alternatives; intent and the singular presupposition remain explicit residuals. |
| “Does it follow from these premises that Tom is an animal?” | Request an entailment certificate or countermodel for the displayed premises and target. |
| “Prove that Tom is an animal using these premises.” | Require submission of an accepted certificate for that exact query; the task may be unsolved or impossible. |

All accepted input, including rendered output, passes complete all-derivations checking across assertions, norms, commands and questions. Multiple derivations or exhausted parsing budget reject admission. An action declaration cannot hide an entire sentence behind an opaque predicate and claim fidelity. Use typed slots and W3 aliases only where their meanings are declared; show a paraphrase and distinguishing situation for alternatives.

“Must Tom be a cat?” can mean necessity or duty; “Can you open the desk?” can ask ability, permission or make a request. Preserve each plausible source reading in translation. “Click Check and save.” has coordination/order questions; do not erase “then”, purpose clauses or timing by splitting it. Authoring offers plain-English rewrites and binds approval to meaning and presentation. Translation keeps all admitted alternatives and unresolved candidates; a cited narrowing never overwrites the original set. Treat inferred synonymy likewise.

Report **meaning admitted**, **norm outcome/conflict**, **answer evidence and its scope**, and **compliance evidence** separately. A well-formed unanswered question can have checked semantics; it has no checked answer. A checked proof submission establishes certificate validity, not the student's understanding. Physical completion requires external evidence; “clear explanation” stays open with W2's decider/criteria/version, or unformalised if no adequate contract exists.

Bind the content kind, force, participants, scope, response mode/domain, presuppositions, environment/profile versions, premise/target IDs, reading choices and transitive dependencies into the new identities. Regenerate all elaborations from decoded content. Never admit the body of a question or command as an assertion leaf; answer-to-claim and adoption bridges must state exactly what evidence licenses. Quoted and hedged nesting retains W2 provenance. Reading sets list readings considered so far, never claim exhaustiveness; intent weights cannot affect checks. For non-assertion sets, elaborate complete compatible choices separately (existing limit 64); otherwise UNKNOWN. The assertion-disjunction shortcut is inapplicable.

<div style="break-after: page;"></div>

## 4. Proof gates, delivery and pilot accounting

**Lean obligations (new route; existing checker unchanged).** Review direct command/answer semantics independently of the elaborator. Prove typing/substitution and deterministic elaboration; command faithfulness to W1, including polarity/defaults; question-answer correctness for polar, single and exhaustive responses; proof-task and consequence-response soundness using the production checker. Prove that dormant requests introduce no assertion consequences; active demands have only their explicitly admitted normative consequences. Reuse W1's conditional expansion/conflict theorems, not unconditional conservativity for adding duties. Reuse W3's conservative definitions only in admitted combinations.

Require executable admission, regenerated Background validity, model/countermodel correspondence, universe-general certificate soundness without a soundness premise, identity/provenance binding, bridge composition, old-route gates and an end-to-end report theorem. Audit under the existing Lean axiom allowlist. New logic additionally owes conservativity and `CertificateSound`. Declare the surface proof boundary; tests cannot prove English understanding.

**Work items, in order.**

1. Pin the source inventory and fixtures; review semantics, schema, wordings and theorem statements. This task delivers the plan; model-based reviews are not run here.
2. Implement typed command/question content in `ve/speech_acts.py`, profile dispatch and W2 integration; regenerate W1 rules and answer queries. Implement `lean/VE/SpeechActs/` admission/faithfulness/report proofs; no enabled route before these gates pass.
3. Add English parsing/rendering, W2-aware natural presentation and W8 replay/approval. Require untrained English speakers to interpret and author held-out cases, including scope/polarity/answer-completeness traps; publish errors and repairs. Until passed, expose strict experimental tooling only.
4. Add Python/Rust/Lean conformance and end-to-end fixtures: prohibition versus optionality; quoted commands; forged context/domain/revision; conflicting duties; false presupposition; empty/multiple answers; unsupported profiles; forged certificates; inconsistent premises/vacuity; translation alternatives; mixed spans; budget exhaustion. Preserve legacy hashes. Close mixed-profile gaps before enabling those combinations.
5. Rerun web audit and tutorial fixtures; then a pinned textbook sample. Keep the strict web gate failing for remaining fixed/dynamic gaps. Refresh North Star only from measured source-span deltas and fidelity audits.

**Coverage.** Partition every source UTF-8 byte once, including punctuation, quotations and mixed units; report bytes/units by kind and C/L/O/R/U. C requires substantive admitted meaning, not completion or answer truth. L is metadata only; O retains open judgments; R retains fully elaborated unresolved alternatives; U includes any unelaborated reading or unsupported component. Apply U, then R, then O, then C; L applies only to non-substantive spans. W2 stores readings under OPEN: supply a disjoint reporting projection and reconcile totals without rewriting old reports. Count open terms, named assumptions, bridge leaves and unresolved sets, retaining per-reading residuals under R. No C gain for guessed deciders or opaque action glosses.

**Expected unlock and risks.** The [North Star portfolio](../../../ve-northstar/NORTH-STAR.md) gives W/D/V weight 3 and T weight 1; speech-act byte opportunities remain unknown. Expect direct gains in web instructions/clarifications and tutorial tasks, then exercise prompts whose underlying mathematics already fits. Reflection, general mathematics, runtime messages, time and causation remain co-blockers. C/U/A/Y may gain explicit directives, not wholesale norm/rights coverage. Measure gains against identical source hashes, separating rewrites and relabelling; do not sum overlapping blockers. Main risks are false normative authority, hidden scope/presuppositions, answer-as-truth badges and training-dependent English. Explicit contexts, separate evidence reports, reading preservation and the human fidelity gate address them; none promises universal coverage.

<div style="break-after: page;"></div>

## Summary

Add typed commands and questions through a versioned document profile while preserving VE's checker and existing meanings. Commands express scoped demands on named addressees and elaborate to W1 obligations or prohibitions. Questions carry explicit response domains, presuppositions and answer contracts; consequence questions and proof exercises reuse certificate and countermodel checking. Neither construct asserts its embedded content or executes an action. Distinguish admitted meaning, supported answers, normative consequences and external compliance evidence. Bind context and reading choices into identities; preserve translation alternatives and open judgments. Require Lean faithfulness, admission and bridge proofs, cross-language conformance, and untrained-reader fidelity gates. The immediate opportunity is web copy and tutorial tasks, followed by bounded textbook exercises. Remeasure source bytes before claiming gains; the current web parser failures are not a semantic unlock estimate.
