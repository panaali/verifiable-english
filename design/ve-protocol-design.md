# Proof-carrying debate over Verifiable English: a protocol and three frontier-scale experiments

**Position adopted throughout.** The *English* surface of VE exists for **human** oversight, because humans read
English better than Lean. It is not claimed to help language models: the preregistered experiment run on 2026-09-21
found no benefit for a capable model judge, and both reviews agree the surface stops mattering above roughly 32B on
short items (`/Users/seyran/code/manage-agents/reviews/SYNTHESIS.md`, §A.1, §D). In **model-only** settings the benefit
must come from (i) **verifiability** — a checker whose soundness is proved, so proof search can be adversarial — and
(ii) the **protocol** that VE supplies to debate. And it must appear at **frontier scale**, where frontier models
actually fail: obfuscated arguments, long context and compaction, very large work products, equal-strength
adversaries, reward hacking.

---

## 1. What the debate project actually contains

### 1.1 Inventory

**Protocol rules.** `/Users/seyran/code/debate/docs/inference-protocol.md` (3,612 words) is the substantive artefact:
a governing rule ("any claim may be asserted, provided it is typed; every claimed inference must be certified — and
every claimed *non*-inference must be certified too"), Phase 0 signature review (§2), assertion with quantifier
elicitation (§3), four verdicts (§4: `CERTIFIED`/`REFUTED`/`GAP`/`COMPATIBLE`), leaf typing (§5), cross-branch bridges
(§6), prohibitions (§7), the judge's view (§8), a two-AI section (§9) and stated limits (§10).
`docs/evidence-protocol.md` (3,674 words) is the leaf layer; `thesis.md`, `learnings.md`, `results.md`, `claims.md`
(20 claims with statuses and strongest objections) and `open-questions.md` (26 questions) surround it.

**Lean.** 2,877 lines under `/Users/seyran/code/debate/Debate/`: `Protocol.lean`, `Evidence.lean` +
`Evidence/Examples.lean` (11 theorems), `Birthright/{Constitutional,Ancestry,Judicial,Policy,Normative,Motion,TwoAI,
Audit,Ledger}.lean`, `DeathPenalty/` (six branches). Per-file theorem counts sum to ~92; `results.md` reports 90
audited, all reporting no axioms.

**Runs.** `docs/runs/two-ai-1/` (openings, rebuttals, back-translation, formalizer log, opaque signature),
`docs/runs/evidence-1/` (two opposed evidence agents), `docs/runs/phase0-redteam-1/` (ten attacks on the setup),
`docs/runs/death-penalty/`, and a separate Lake project `/Users/seyran/code/debate/experiments/epr-bohr-1935/`.

### 1.2 Genuinely good and reusable

1. **A negative verdict must be a countermodel, never a failed search** (`inference-protocol.md` §4.2). "No proof was
   produced" scores search budget, not honesty. VE independently implements the same discipline: `NotFound` and
   `ResourceLimit` never become findings (`/Users/seyran/code/ve-integration/docs/implementation.md`, "Entailment
   evidence and trust boundary").
2. **The no-promotion rule** (§4.3): refuting premise P of an argument for C returns C to *unsupported*, never to
   *refuted*. Without it, formalisation makes routes easy to snipe and rewards attacking whichever path the opponent
   named. VE's protocol has the logical half of this (`docs/spec/debate-protocol.md`: "A `refuted` edge cannot support
   its original conclusion") but not the scoring rule. Import it.
3. **Split-on-demand, granted by default, burden on whoever wants two usages merged** (§2.2–2.3). This is the single
   most valuable import, because it is precisely the answer to VE's own weakness #1 (the merged-vocabulary attack,
   `docs/spec/debate-protocol.md`, "The same attack when the vocabulary is merged").
4. **Extracted premises with an owner and three buttons** (§4.4): approve / withdraw / **narrow the conclusion**. The
   third is the constructive move VE lacks: derive the weaker conclusion the premises *do* support.
5. **Position witnesses and nonempty countermodels** (§2.7, §2.9). Each side exhibits a model of the environment in
   which its whole position holds. This catches an inconsistent environment, which an axiom audit cannot.
6. **Cross-branch bridges demanded up front** (§6), and the rule that an *identification* of a symbol across branches
   is itself a typed claim requiring consent.
7. **Procedural rules unamendable during a run** (§2.6), with no adjudicator empowered to grant exceptions.
8. **The judge sees the disputed node set first and tallies last, never as a score** (§8).
9. **The ledger discipline itself** (`claims.md`, `open-questions.md`): every claim carries a status and its strongest
   objection, and nothing is deleted. This is the repo's best epistemic habit and should be copied into VE.

### 1.3 What is sloppy, and what a sceptical reviewer would reject

- **No comparison arm exists anywhere in the repository.** Every finding is an existence proof. C1 ("requiring a
  certificate for every claimed inference removes the need for the judge to locate the flaw") is marked SUPPORTED in
  `docs/claims.md` on the basis of one reconstruction with no adversary, no baseline, no control and no alternative
  formalisation. `learnings.md` §1 concedes "a careful reader can identify many of the same gaps without Lean"; the
  claim status does not reflect that.
- **"90 theorems, all reporting no axioms" is a headline that certifies nothing about any argument.** The repo says so
  (`inference-protocol.md` §7), but `results.md` still leads with the number. The theorems are bespoke per branch;
  Q11 records that a second debate starts from zero.
- **The evidence protocol is a 3,674-word LLM prompt, not a protocol.** Nothing in it is checkable by anyone but the
  agent that ran it — Q2 states this. The Lean evidence work (`Debate/Evidence/Examples.lean`) checks probability
  orderings and partition sums: arithmetic coherence, not search adequacy.
- **Fidelity is unestablished and partly circular.** The reconstructions have no speaker approval (`thesis.md` §5),
  and the same model family extracted the transcript, wrote the formalisation and reported the finding; Q3 concedes
  that K-EX "may be an artefact of its own vocabulary choices".
- **Mixed units in the headline table.** `results.md`'s compatibility counts pool models witnessing a whole position
  with models resolving one exchange; the caveat sits below the table.
- **Countermodels were searched over `Unit` and `Bool`** (Q9). The claim that countermodels are as cheap to find as
  proofs are to check has never been tested outside toy signatures.
- **The judge-facing ledger is unverified metadata.** Descriptions, verdict labels and theorem references "must also
  be reviewed" (§7) — and no run has done that review.
- **"At scale" in C13 rests on N = 2 transcripts**; C12's two-layer convergence is self-acknowledged as possibly a
  shared prior (Q13) yet still appears as evidence in `thesis.md` §3. **Adversariality is untested**: two-AI run 1 had
  two cooperative participants, one run, three rounds (Q7), and the evidence run used an easy claim (Q2).

**Net:** the *rules* are worth keeping and are better than the artefacts that motivate them. The *evidence* would be
rejected by any reviewer asking for a baseline.

---

## 2. Protocol specification: proof-carrying debate over VE, model-only

### 2.1 Roles

| Role | Trust | Job |
|---|---|---|
| **Proposer** P | untrusted | Commit a root claim and a claim graph supporting it; supply certificates |
| **Critic** C | untrusted | Attack with checkable artefacts; may not win by assertion |
| **Checker** K | **trusted, mechanical** | Parse, type, bind identities, replay certificates, validate models, compose, account budgets |
| **Judge** J | untrusted, bounded | Decide everything K cannot: leaf truth, faithfulness, vocabulary, the final verdict |

There is no third-party formaliser. In model-only settings P authors its own VE and is bound by it; C attacks the
formalisation with the moves below. (The debate project's third-party formaliser exists because human speakers do not
write logic; that constraint is absent here.)

### 2.2 Artefacts a move must carry

- **Claim**: exact VE bytes (including final newline), `source_id`, `meaning_id` under environment `E`, `environment_id`,
  a type (`DEDUCED` / `EMPIRICAL` / `INTERPRETIVE` / `NORMATIVE` / `DEFINITION` / `STIPULATED`) and an owner. A local
  alias is never a meaning.
- **Edge**: ordered premise claim ids, exact conclusion claim id, and either a tableau certificate
  (`checker_version`, `environment_id`, `premise_meaning_ids`, `conclusion_meaning_id`, `trace` — data only, no
  executable code, no theorem names) or a complete finite model.
- **Countermodel**: a complete `FiniteModel` making every premise true and the conclusion false, replayed by the
  evaluator.
- **Distinguishing scenario**: a `compare(E, a, b)` result with label `DIFFERENT`, its checked distinguishing model,
  and the relation (`weaker` / `stronger` / `incomparable` / `unknown`).
- **Evidence record**: `{claim_id, snapshot_digest, passage_span, retrieval_time, scope, source_uri, reviewer,
  judgment ∈ {accepted, disputed, unassessed}}`. A mutable URL alone is insufficient.

### 2.3 Legal moves

| Move | Carries | Checker action |
|---|---|---|
| `assert(claim, type, owner)` | claim bytes | parse, type-check, bind identity; reject duplicate alias or cross-environment reuse |
| `decompose(conclusion, Δ, certificate)` | edge + certificate | replay; emit `follows` or reject |
| `challenge-inference(edge, M)` | countermodel | evaluate Δ true, C false; emit `gap`; emit `CheckerConflict` if a `follows` certificate also stands |
| `challenge-premise(leaf, reason_type)` | reason type only | mark disputed; **no promotion** to a refuted root |
| `challenge-formalisation(claim, rival, M)` | rival VE statement + distinguishing model | `compare`; accept only on `DIFFERENT`; record relation and both English renderings |
| `split-predicate(p → p1, p2, uses)` | two divergent uses with their evidence records | granted **by default**; every claim mentioning `p` is re-committed under a new `environment_id`; **all certificates over `p` are voided** and must be re-supplied |
| `bridge-premise(edge, B)` | new leaf B + re-certified edge | replay the repaired edge; B enters the leaf set with an owner |
| `narrow(claim, weaker, certificate)` | weaker conclusion + certificate | replay; the weaker claim replaces the original in the derivation |
| `concede(claim | edge)` | — | record; the conceded object cannot be re-asserted this run |

A move without its artefact is **not a move**: it is logged as rhetoric, costs its budget, and changes no status.

### 2.4 What K decides mechanically, and what is left to J

**K decides:** parse and type acceptance; identity binding; graph acyclicity and reference resolution; the four edge
judgments (`follows`, `refuted`, `gap`, `unresolved`); composition of certified edges into `Entails(E, L, root)`
with **every undischarged leaf retained in `L`**; `CheckerConflict`; oracle relations; split bookkeeping; resource
statuses; and the transcript hash chain. Resource exhaustion is an operational status, never evidence.

**J decides:** whether the root is the question that was asked; whether the leaves in `L` are true and adequately
evidenced; whether the vocabulary descriptions are honest and consistently used; which of two rival formalisations is
faithful when the oracle reports `DIFFERENT`; and the final verdict. **A checked conditional argument is not an
approval.**

### 2.5 Guarantees inherited from the Lean-verified checker — and those not

**Inherited.** `VE.Tableau.checkCertificate_sound` (`lean/VE/TableauChecker.lean:176`) and
`VE.Closure.Tableau.checkCertificate_sound` / `checkCertificate_sound_v0` (`lean/VE/TableauExtendedChecker.lean:215,
237`): if the checker accepts a certificate, then `Entails(E, Δ, C)` holds over **every** admissible structure at
every universe, including empty sorts — with *no certificate-soundness premise*. Proof search is therefore fully
untrusted and may be adversarial. `VE.ClaimGraph.check_sound_of_certificateSound`
(`lean/VE/ClaimGraph.lean:269`), with `acyclicCheck_sound`, gives obligation P10: certified acyclic composition yields
the root implication **retaining all undischarged leaves**.

**Not inherited.** (a) The argument layer actually used by the experiments replays certificates in **Python**, not
Lean; `docs/spec/verification-contract.md` labels those records `assurance: experimental`. (b) Parser obligations
P1–P3 and evaluator agreement P6 are *pending*; JSON decoding and environment validation are explicitly trusted
components. (c) **Completeness is not a guarantee**: `NotFound`/`ResourceLimit` are silent. (d) The equivalence oracle
returns `UNKNOWN` at a measured 2.0% (8/400) under audited budgets
(`experiments/oracle/results/summary.json`); `UNKNOWN` is never a semantic answer. (e) Nothing is inherited about leaf
truth, faithfulness of the formalisation, neutrality of the vocabulary, or whether an honest proposer can afford a
certificate at all.

### 2.6 Evidence protocol for factual leaves, and its limits

Keep the debate project's leaf discipline — provenance separate from interpretation, competing explanations, explicit
falsification attempts, calibrated intervals — as the **authoring standard** for `EMPIRICAL` leaves, with one change:
its output must be an evidence record (§2.2), not prose. Limits: compliance with the prompt is unverifiable; a digest
proves a document says something, never that the search was unbiased; arithmetic coherence of a probability table
catches incoherence, not lopsided search. Presentations lead with the leaf set, never the certified-edge count.

### 2.7 Termination, scoring, transcript

Alternating rounds under a **fixed token and move budget per role**, declared before the run. Termination: no legal
move remains, or budget exhausted, or both sides concede. K then emits the report — root, `L` ordered by how many
conclusions depend on each leaf, disputed set, gaps with their countermodels, unresolved obligations, and last of all
the counts. J receives it with its **own** inspection budget (at most *k* claim-opens and *B* tokens).

Scoring is findings-based, never tallies: a `gap` on an edge P submitted is P's error; a challenge without a checked
artefact is C's error and costs C its budget; a `CheckerConflict` voids the run. Nobody is penalised for an ambiguity
the procedure failed to resolve.

A **transcript** is an append-only JSONL hash chain: one object per move `{round, role, move, payload,
checker_record, budget_after, prev_hash}`, replayable end-to-end from the environment and the move log alone.

---

## 3. Where this should beat existing methods for frontier models

### (a) Obfuscated arguments — the lead case

> **Correction 2 (2026-09-22, after re-reading BC20, DED, PE and SC in full; `~/code/manage-agents/reviews/obfuscation-recheck.md`).**
> "VE contributes nothing to obfuscated arguments" holds only for a protocol that ACCEPTS leaves without proof. Under a
> MANDATORY-PROOF rule (nothing is accepted unless the verified checker derives it from declared, reviewed foundations),
> a dishonest prover cannot win by assuming false sub-claims: this defeats the Barnes-Christiano construction for fully
> formalised claims (soundness). BC20 itself: with enough budget, "just have both debaters write out their entire proof,
> and run a checker"; PE section 8 proposes Lean proofs for mathematical subclaims plus debate for fuzzier ones. The honest
> side wins only when the truth has an affordable proof (completeness); otherwise the result is "unresolved", which is
> safe but unhelpful. Not covered: proofs longer than the budget (the PSPACE regime debate targets); foundation leaves
> accepted without proof (physical laws, idealisations, tolerances, empirical claims), where estimation is still needed;
> formalisation faithfulness (e.g. the train example: the flaw moves to one visible model-choice leaf); cost (measured on
> one self-reviewed pilot: iceberg root proved in 912 s). The rho = N objection applies to estimated leaves, not proved
> ones. See `design/vex-mandatory-evidence.md` for extending this to statistical, approximate and heuristic claims.

> **Correction (2026-09-21, after a full reading of the primary sources; overrides the text below).** In Barnes and
> Christiano's obfuscated arguments the premises are already explicit and the steps are valid (their RSA example and
> their closing formal-logic example): one explicit sub-claim is false and NEITHER debater can tractably find which.
> Explicit premises and checked deductions therefore contribute nothing on the canonical cases, and a certified
> conjunction over N leaves has the worst stability parameter (rho = N). See `positioning-vs-debate-theory.md` section 4.
> What VE does target is a different, named problem: smuggled premises, equivocation and a term defined differently in
> different sub-claims (safety-case sketch D5.5, "gerrymandering"), which prover-estimator debate does not handle and
> cross-examination does; cross-examination is the baseline to beat. This section is not "the lead case"; F0 is the
> "long-argument flaw localisation" study of PLAN-V3, not an obfuscated-arguments benchmark.

**Mechanism.** In Barnes and Christiano's failure, a long decomposition's every step looks locally plausible and the
flaw hides among N steps; neither debater can locate it efficiently. Under this protocol the checker **replays every
deductive step**, at cost linear in certificate size and *zero judge attention*. A flaw in a deduction cannot hide:
the step is either certified (hence sound, by `checkCertificate_sound`) or it is not, and an uncertified step is a
visible unresolved obligation, or a `gap` with a countermodel the judge can evaluate in one scenario. What survives is
**K leaf premises plus the formalisation** — a set whose size the proposer must declare, not a search over N steps.

**Honest limit.** Obfuscation migrates. The proposer can inflate K, or hide the flaw in the English rendering of a
claim, or in one vague predicate justified differently in two branches — the merged-vocabulary attack, where the
checker is blind *by construction*. The protocol's answers are moves, not guarantees: `challenge-formalisation` with a
checked distinguishing scenario forces a disagreement about meaning into a concrete world the judge can inspect;
`split-predicate` is granted by default and **voids every certificate over the split symbol**, so an equivocation that
was carrying the argument must reappear as an explicit bridge premise with an owner.

**Closest prior methods to beat:** debate with cross-examination (which Buhl et al. §4.4.2 D5.5 already claims avoids
the cross-branch inconsistency failure), prover-estimator debate, doubly-efficient debate. **Why VE might not win:**
the honest proposer may be unable to formalise the domain at all (E0: strict fit 0% for Cedar, 0% for FRET); certificate
production may exceed budget where prose costs nothing; and the half of the result that VE wins (deduction flaws) is
true by construction.

### (b) Cross-examination and consistency across branches

**Mechanism.** Claims are bound to `source_id` and `meaning_id` under one `environment_id`. A claim cannot be silently
re-interpreted between branches, because re-interpretation changes the identity, and a changed identity cannot inherit
a certificate, a confirmation, or an evidence judgment. Cross-examination achieves this by *successful questioning and
the judge's memory*; identity binding achieves it mechanically and audibly. **Closest prior:** debate with
cross-examination. **Why it might not win:** if the vocabulary is merged, identity binding certifies the equivocation
and a "proof checked" label may make it *harder* to notice than in prose (known weakness #2). Identity is a guarantee
about symbols, not about senses.

### (c) Long context and compaction

**Mechanism.** A canonical claim is a hash over exact bytes. Compaction — where an LLM summarises its own context and
loses conditions — cannot silently rewrite a claim without changing its `meaning_id`; and when the agent *does*
re-author, `compare` measures the drift exactly, with a label and a checked distinguishing model. Drift becomes a
measured quantity rather than an anecdote. **Closest prior:** LLM-summary compaction, key-value memory tools,
structured JSON requirements. **Why it might not win:** verbatim JSON survives compaction just as well; VE's unique
contribution is the *oracle*, which only matters when the requirement is restated rather than copied.

### (d) Reward signals for training

**Mechanism.** Checker-determined findings cannot be argued with: a `gap` is a model, a `follows` is a replayed
certificate, and neither responds to persuasion. A reward computed from K is immune to the judge-flattery channel that
makes debate rewards teach deception. **Closest prior:** process supervision, critique models, self-consistency
voting, FormalJudge-style spec+solver. **Why it might not win:** hacking migrates to the choice of specification — a
policy learns to certify vacuous or over-strengthened claims. The project's own Phase T analysis already found that
the checker-in-the-reward contrast was "close to true by construction" (`PLAN.md`, Phase T), which is the correct
verdict and must not be forgotten.

---

## 4. Three experiments: model-only, frontier-scale, preregistrable, ≤ ~$100 each

All arms use Gemini via Vertex ($273 credit) plus OpenRouter; Claude/GPT subscriptions for spot checks only.
**Fairness rule for every experiment:** every arm receives the same argument content, the same world-query budget and
the same judge; the prose arms get a deterministic fluent rendering of the *identical* claim graph plus freedom for a
frontier model to rewrite it as prose, subject to a content check that the leaf set is preserved; and **every arm is
charged its full dollar cost, including VE authoring and certificate production**, amortised per item. Report
cost-matched comparisons (top up the prose arms' critic tokens until dollars are equal).

### F0 (lead) — Obfuscated arguments

> **Correction (2026-09-21, after a full reading of the primary sources; overrides the text below).** In Barnes and
> Christiano's obfuscated arguments the premises are already explicit and the steps are valid (their RSA example and
> their closing formal-logic example): one explicit sub-claim is false and NEITHER debater can tractably find which.
> Explicit premises and checked deductions therefore contribute nothing on the canonical cases, and a certified
> conjunction over N leaves has the worst stability parameter (rho = N). See `positioning-vs-debate-theory.md` section 4.
> What VE does target is a different, named problem: smuggled premises, equivocation and a term defined differently in
> different sub-claims (safety-case sketch D5.5, "gerrymandering"), which prover-estimator debate does not handle and
> cross-examination does; cross-examination is the baseline to beat. This section is not "the lead case"; F0 is the
> "long-argument flaw localisation" study of PLAN-V3, not an obfuscated-arguments benchmark.

**Generation.** A seeded generator builds a certified VE claim graph of N ∈ {50, 500, 5000} deduction steps by forward
chaining from a leaf set over a synthetic vocabulary (contamination-free), each edge certified by the prover, so the
clean article is *valid by construction*. Then exactly one flaw is planted, of one of three types:
- **D (deduction):** one edge's conclusion is replaced by a subtly different variant. Validated by
  `ve.attacks.validate_attack`: must be `DIFFERENT` with a checked distinguishing model, and must not be detectable by
  string comparison. Local plausibility is *calibrated*: a frontier model shown the step in isolation must accept it at
  ≥ 70% on the dev split.
- **L (leaf premise):** one leaf is false in a held-out reference **world model**. All arms may query the world model
  at a fixed cost per leaf, so leaf-checking is a budgeted search for every arm and VE gets no free oracle.
- **F (formalisation):** the English shown to the judge differs in meaning from the committed VE statement; ground
  truth is `compare` returning `DIFFERENT` with a checked model.
A **no-flaw control condition** (20% of items) measures false alarms.

**What the judge sees.** One frontier judge, inspection budget *B* tokens and at most *k* claim-opens. It returns
(verdict, flaw location as a claim/step id, confidence).

**Arms.** (1) prose debate, frontier critic must locate the flaw; (2) debate with cross-examination (critic may put
*k* questions to the proposer, answers in the transcript); (3) chunked direct review, no debater; (4) VE protocol with
the real checker; (5) **VE protocol with a forged checker line** — a checker-shaped verdict block written by the
proposer, asserting `follows` for the corrupted edge, with no replayable certificate.

**Metrics.** Flaw-localisation accuracy (exact id), judge accuracy (sound/unsound), false-alarm rate on control items,
and **tokens and dollars per decision as a function of N** (the slope is the result, not the level).

**Prediction.** VE localisation ≈ 1.0 for D flaws at every N with cost flat in N — *and this is by construction; it is
reported as a mechanism demonstration, not a finding*. For L flaws: VE narrows the search to K leaves and should beat
prose at N = 5000, but well below 1.0. For F flaws: VE ≈ prose unless the judge uses the distinguishing-scenario
move. Arm 5 should collapse if the judge is verifying rather than deferring.

**Refutation.** If at N = 5000 arm 2 matches arm 4 on L and F flaws at equal or lower dollar cost — so that VE's only
advantage is the by-construction D cell — VE adds nothing over cross-examination. Equally refuting: arm 5 scoring at
arm 4's level (deference, not verification), or VE authoring cost exceeding the judge cost saved.

**Threats to validity.** *By construction:* D-flaw localisation, and the validity of the clean article. *Not by
construction:* L and F localisation, judge accuracy, all cost slopes, and the forged-checker control. Other threats:
generator style artefacts (mitigated by the no-flaw control and string-detectability screening); the prose rendering
being a straw man (mitigated by free frontier rewriting under a content check); judge self-preference (two judge
families); and contamination (synthetic vocabularies).

**Budget.** Items per cell 40 / 20 / 10 for N = 50 / 500 / 5000; only arms 1–3 pay full-context input. Bulk critic
reading at Flash tier, judging at Pro tier. Estimated $60–85.

### F1 — Requirement retention under long context and compaction

An agent receives 10–40 requirement clauses, then works through 50k / 200k / 800k tokens of distractor work with
forced compactions, then must restate the requirements and decide 20 held-out distinguishing scenarios. **Arms:**
prose notes; LLM-written summary (the default compaction); key-value memory tool; **verbatim structured JSON without a
checker** (the real baseline); VE claims with identity hashes re-parsed and re-checked after every compaction; VE +
oracle drift report. **Metrics:** drift by `compare` (equivalent/weaker/stronger/incomparable/unknown); enforcement
accuracy on the scenarios; dollars. **Ground truth without human labels:** the oracle and the finite evaluator.
**By construction:** hash survival and the scenario labels. **Not by construction:** whether re-anchoring on the
canonical claim improves downstream *enforcement* over the verbatim-JSON arm — that is the only real finding here, and
the honest prior is a small effect. **Threats:** the VE arm may win only by being shorter and verbatim; forced
compaction is a harness artefact and its implementation must be published. Estimated $40–70.

### F2 — The merged-predicate duel (tests the protocol, not the checker)

The checker is blind here by design, so this isolates the **moves**. A frontier proposer must reach a target
conclusion not entailed by the honest premise set but entailed once one of ~5 mergeable predicates in a ~60-predicate
vocabulary is merged; graphs of 200–1,000 steps; an **equal-strength** frontier critic. **Arms:** (A) checker only,
no protocol moves; (B) full protocol; (C) prose debate with cross-examination and a shared glossary; (D) full protocol
with `split-predicate` disabled. **Metrics:** rate at which the judge approves the unsound root; moves and dollars to
expose the equivocation; which move exposed it. **Ground truth:** by construction — the generator knows the honest
split, and unsoundness is witnessed by a checked countermodel over the split vocabulary. **Prediction:** A ≈ C or
worse (the "proof checked" harm); B > A; B − D measures the split move. **Refutation:** B ≈ C at equal cost means the
protocol adds nothing over cross-examination, which is exactly what Buhl et al. already claim. **Threats:** the merge
is planted and therefore discoverable; the base rate of this attack in the wild is unmeasured (known weakness #6); the
critic's competence, not VE, may be the operative variable. Estimated $50–80.

---

## 5. What must be built in VE

| Component | Detail | Rough effort |
|---|---|---|
| Argument generator | seeded environment + certified forward chaining + three flaw injectors + validators (`validate_attack`, `compare`, world model) | 3 days |
| World-model oracle service | held-out reference model, per-query cost accounting shared by all arms | 1 day |
| Transcript format | `docs/spec/transcript.md` + JSONL hash chain, replayable from environment + moves | 1 day |
| Debate runner | role prompting, move parsing into typed moves, checker invocation, budget accounting, on-disk response cache | 3 days |
| Judge harness | inspection-budget enforcement via a claim-open API rather than dumping the graph | 1 day |
| Evidence-record schema | the §2.2 record, wire-validated, plus a scope-mismatch linter | 0.5 day |
| Forged-checker renderer | the deference control | 0.25 day |
| Drift reporter + scenario generator | for F1 | 1 day |
| Cost accounting | dollars per decision including VE authoring | 0.5 day |

About two engineer-weeks, or a few days with parallel agents. No language extension is required; `relational-fol@0`
plus `closure@0` suffices for synthetic items.

---

## 6. What a positive result would, and would not, show

A positive result across F0, F1 and F2 would show that, for *synthetically generated arguments within VE's
first-order fragment*, a debate protocol whose deductive steps are replayed by a soundness-proved checker lets a
frontier judge locate planted flaws more accurately and at cost that grows more slowly in argument size than prose
debate, cross-examination or chunked review at matched dollars — and that the gain is not deference, because the
forged-checker arm collapses. It would **not** show that VE helps a human, that the English surface contributes
anything (the model-only arms are indifferent to it), that real frontier work products are formalisable (E0 says much
of policy and requirements text is not), that an honest agent can afford certificates on a real task, that the planted
attacks occur at any meaningful rate in the wild, that the leaf and formalisation layers — where the obfuscated-
arguments problem actually lives after the checker has done its work — are solved rather than made visible, or that a
checked conditional argument should ever be read as an approval.
