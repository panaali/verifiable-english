# VE v0: Debate Claims and Argument Checking

**Status:** First draft. The protocol, certificate replay path, and proofs are pending. This is the local research prototype's contract, not a claim of a secure public proof service or a complete alignment protocol.

**Experimental implementation:** The Python prototype implements these graph
and finding semantics using data-only tableau certificates checked by a small
Python replay checker. This is a separately labeled trust boundary, not the Lean
replay path or completed metatheory described below. See the
[implementation contract](../implementation.md#entailment-evidence-and-trust-boundary).

VE supplies claims and checks for a proposer, critic, and supervisor. It can be used with cross-examination or other debate strategies; it does not select a training algorithm, reward equilibrium, or probabilistic evidence aggregator. The [roadmap](../roadmap.md) compares these choices experimentally.

## Commitments and scope

An argument uses one validated `relational-fol@0` environment `E`. The [language specification](v0-language.md) defines its grammar, typed AST, interpretation, and artifact identities.

- A claim contains exactly one closed VE statement, including its final LF. Its exact bytes determine `source_id`; checked parsing determines its AST and `meaning_id` under `E`.
- A local name such as `c1` is an alias for that claim, not its meaning. Duplicate aliases, unresolved references, and conflicting bindings are errors.
- The supervisor confirms the root claim, vocabulary descriptions, and intended scope. The original task remains available for comparison. Confirmation is a recorded human judgment, not a theorem that intent has been recovered.
- Every reference resolves to the same committed claim object. A changed formula, description, or environment cannot reuse attached confirmation or inference evidence. Identical words under different environments are not interchangeable.
- All branches share `E`. A proposed vocabulary change requires a new argument commitment; v0 has no automatic translation between environments. Relations between distinct predicates require explicit premises even when their descriptions sound similar.

The supervisor sees canonical VE generated from the accepted AST, its definitions, and the exact status of the claim. Free-form explanations are commentary; they cannot replace the committed root or become the statement certified by a proof. This protects formal correspondence after commitment. Misleading descriptions and wrong initial commitments remain targets for human review and adversarial evaluation.

## Arguments and certificates

The submitted argument is a finite directed acyclic graph with a designated root. Each node is either a premise leaf or a conclusion of one submitted deduction. An edge names its ordered list of premise claims and exact conclusion claim; every reference must exist under `E`. Cycles and self-support are invalid. The checker verifies this submitted graph, not the exponentially larger tree of all possible future debates.

For closed premises `Δ` and conclusion `C`, a positive edge certificate must prove:

```text
Entails(E, Δ, C) := ∀ admissible S,
  (∀ A ∈ Δ, Denote(E,A,S)) → Denote(E,C,S)
```

The trusted checking path constructs this expected proposition from the parsed claims. It checks the actual proof term against that proposition in the pinned Lean environment and audits its dependencies. The certificate cannot choose another conclusion, add an undisplayed premise, redefine a predicate, or substitute a theorem name for a proof. Standard logical dependencies follow the [verification contract](verification-contract.md#proof-dependencies-and-trusted-components).

Proof production is untrusted and resource-bounded. The local prototype may use an isolated Lean proof worker, then replay the resulting declarations in the fixed checking environment. Successful compilation by the worker is insufficient. The first implementation gate must specify the artifact encoding, allowed declarations, isolation, and replay procedure before accepting agent-produced certificates. VE text itself contains no executable Lean. External proof code must never run in the trusted checker process.

The edge judgments are:

| Judgment | Required evidence | Meaning |
|---|---|---|
| `follows` | Checked proof of `Entails(E,Δ,C)` | The exact conclusion follows under the displayed premises |
| `refuted` | Checked proof of `Entails(E,Δ,Not(C))` | The displayed premises entail the negation |
| `gap` | Valid finite `M` with all of `Δ` true and `C` false, checked by the finite evaluator | This inference is invalid; it does not establish that `C` is false in the actual world |
| `unresolved` | No accepted positive, negative, or countermodel certificate | No conclusion about entailment has been established |

Record all established findings rather than choosing a single winning label. Both `follows` and `refuted` can hold under inconsistent premises; their coexistence must be displayed as a contradiction in those premises. `refuted` and `gap` can coexist. Use `unresolved` only when no finding is established.

For the exact same `E`, `Δ`, and `C`, `follows` and `gap` cannot both be sound: the latter supplies a model contradicting the former. Report `CheckerConflict` as an operational integrity error, retain both artifacts for diagnosis, and withhold a successful combined checking record. Do not explain this combination as inconsistent premises; a valid gap witness satisfies every premise. The same rule applies when a purported model of all premises accompanies both `follows` and `refuted`.

Malformed artifacts, invalid proofs, resource exhaustion, and cancellation have separate operational statuses. Failure or timeout in proof search is not `gap` or `refuted`. Finite satisfaction alone cannot produce `follows`. A gap in an intermediate edge does not refute the root; another argument might establish it.

When every edge supporting the root has a `follows` certificate, the checker composes the implications into `Entails(E,L,root)`, where `L` contains every undischarged premise leaf used by the submitted derivation. A `refuted` edge cannot support its original conclusion; using its proof requires an explicit claim for `Not(C)`. The checker displays all remaining leaves with the root. An uncertified intermediate claim remains an unresolved obligation and cannot be silently relabeled as an accepted premise. A supervisor may explicitly consider a different conditional argument with that extra assumption.

Certificates prove conditional claims. Assuming the desired answer does not resolve it: the answer remains a leaf obligation. Contradictory premises can entail both a claim and its negation in classical logic; do not turn either certificate into an unconditional approval. An optional finite model satisfying all leaves establishes their joint satisfiability, not their truth. Failure to find such a model establishes neither inconsistency nor consistency.

## Evidence and supervisor decisions

Premise leaves may have empirical, interpretive, definitional, or normative descriptions, with source references and a supervisor's accepted/disputed/unassessed judgment. These are evidence metadata, not new logical operators or proof of facts. The checker never converts an unsupported claim into an axiom about reality.

An evidence judgment must identify the claim, inspected evidence snapshot, relevant passage or records, reviewer, and target scope. A mutable URL alone is insufficient to identify the reviewed content. Keep evidence judgments separate from mathematical certificates: changing an evidence snapshot or the deployment under review requires reassessment of affected factual support and approval, even if the formula and conditional proof remain unchanged. Specify these records in G0 before implementing interchange.

The review interface should group all uses of a predicate with their supporting evidence, so that the critic and supervisor can challenge whether those uses share one interpretation. This is a procedural defense to evaluate, not a new formal guarantee. A leaf needed for approval but left unassessed remains outstanding; sampling a few leaves does not establish all premises, and v0 supplies no statistical sampling guarantee.

Finite models used as hypothetical examples need no factual attestation. If a model represents a real submission, the experiment or application must explain how its entries and completeness are established independently of the proposer. Values such as `safe`, `reviewed`, or `compliant` cannot stand in for computations or observations the system is meant to verify.

The supervisor may approve the submitted result, reject it, request repair, or leave it unresolved. Approval depends on the root interpretation and outstanding evidence, not the number of certified edges. A smaller set of remaining claims need not be easier to judge. Measure their difficulty and review cost.

The checking record binds the exact environment, root, source/meaning identities, dependency graph, leaf assumptions, witness models, proof artifacts, and checker build. A record is valid only for those objects. The protocol wire schema and its canonical encoding must be fixed before interchange; local aliases and UI labels are never sufficient evidence of correspondence.

## Worked example

Use one sort `service`, with unary predicates `deployed`, `ops_reviewed`, `security_reviewed`, and `approved`. Operations review and security review are distinct declared concepts. The illustrative claims are:

```text
for every service s, (if (s is deployed), then (s is ops_reviewed)).
for every service s, (if (s is security_reviewed), then (s is approved)).
```

The proposed root is:

```text
for every service s, (if (s is deployed), then (s is approved)).
```

A countermodel contains one service `api` with `deployed` and `ops_reviewed` true, and `security_reviewed` and `approved` false. Both premises hold; the second is vacuously true. The root is false. The resulting judgment is `gap`, even if a prose explanation calls both predicates “reviewed.”

Adding the explicit premise below makes the inference valid:

```text
for every service s, (if (s is ops_reviewed), then (s is security_reviewed)).
```

That bridge is now a visible leaf to assess. The proof does not make it a fact. A proof produced with this bridge cannot be attached to the original two-premise edge.

### The same attack when the vocabulary is merged

The example above presupposes that someone already split “reviewed” into two predicates. That split is where the equivocation was actually caught, and the checker did not perform it. An adversarial proposer would instead declare a single predicate `reviewed` with the description “Recorded as reviewed,” and submit:

```text
for every service s, (if (s is deployed), then (s is reviewed)).
for every service s, (if (s is reviewed), then (s is approved)).
```

The root now has a `follows` certificate. The proposer supports the first leaf with operations-review records and the second with a security policy. Each leaf looks acceptable when judged alone, and the checked proof asserts that they compose. The meaning change has moved from the deduction into the free-English description and the evidence attached to the leaves, where v0 checks nothing. This is the cross-branch inconsistency from the motivating research, and a certified edge may make it harder to notice than it would be in prose.

v0's defenses here are procedural: the supervisor or critic must notice that the evidence uses incompatible senses and demand a vocabulary split or adequate support under one interpretation. Multiple evidence sources alone are not a defect. Test the proposed predicate-use panel against equally equipped prose and structured interfaces. Whether people detect this attack more reliably is an open empirical question and a required attack in the [adversarial evaluation](../roadmap.md#adversarial-evaluation). Who authors the vocabulary, and whether the critic may challenge it before commitment, must be fixed in G0.

These expected outcomes are executable as `ve.argument_fixtures.worked_examples()`
and tested in `tests/test_argument_fixtures.py`. The first example tests both a
rejected substitution and a valid repair; the second tests a substitution the
checker accepts. Both use only v0 syntax. Passing those tests is empirical
implementation evidence; the [formal obligations](verification-contract.md#argument-checking-contract)
remain pending.

## Bounds and unsupported claims

Initial prototype limits are 256 claims, 512 premise references total, and a 16 MiB aggregate argument package including certificates and models. Per-claim and per-model limits also follow the language specification. Proof construction, replay time, and memory receive separate budgets fixed for each experiment; exhaustion remains operational failure, never evidence against the claim.

General probability, time, obligation, causality, and arbitrary mathematical definitions are outside this profile. A bounded mathematical extension requires its own semantics and preservation theorem. Proving argument composition does not prove that honest play wins a debate, that an honest agent can afford certificates, or that a limited judge can reliably decide the remaining premises.
