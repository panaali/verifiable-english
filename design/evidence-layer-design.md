# An evidence layer for Verifiable English

**The claim.** VE checks deduction from leaves and refuses to touch the leaves. The debate project
assesses leaves and has no machine-checked deduction. Neither half is worth much alone: a certified
graph over unassessed leaves is a conditional nobody should read as approval, and a probability table
over unrelated propositions is a mood. Joined, VE's claim graph says *which* leaves matter and *how
they compose*, and the evidence layer says *how strongly each is supported and why* — and the join
buys three things that neither side has today: a **sound lower bound** on the root, a **coherence
checker** that uses VE's entailment oracle to constrain probabilities mechanically, and an
**adversarial update ledger** that makes a premature estimate a protocol violation rather than a habit.

---

## 1. What the debate project's evidence method actually is

### 1.1 The procedure

`/Users/seyran/code/debate/docs/evidence-protocol.md` (3,674 words) is a twelve-section prompt, not a
protocol. Its steps: (1) a claim ledger — actor, action, object, date, scope, qualifiers — with broad
allegations broken into separately testable claims; (2) inspection of primary material, recording for
screenshots who published them, visible timestamps, crop edges, completeness; (3) authenticity,
completeness, contemporaneity, independence, relevance and error-susceptibility scored *separately*,
explicitly refusing to count reprints of one wire story as corroboration; (4) two timelines — events
and *publication/version* history — with archive captures, PDF metadata and `Last-Modified` headers
treated as clues, not logs; (5) precise reading of disputed wording against at least two
interpretations; (6) observation / inference / normative judgment kept apart; (7) mechanisms, with
public knowledge, rumour, private hint, retrieval and training exposure distinguished; (8) competing
explanations constructed and attacked; (9) subjective probabilities with ranges per precise
proposition, never a global "person X was wrong" score; (10) a challenge-evidence-revise loop with a
stopping rule; (11) a thirteen-item self-audit; (12) an auditable answer. `evidence-protocol-v1.md` is
the same skeleton, 1,000 words shorter, without the completion criteria and self-audit.

### 1.2 The two cases

**Credit dispute** (`docs/sources/case-credit-dispute.md`,
`docs/sources/case-credit-dispute-agent-run.md`). The OpenAI Navier–Stokes attribution row. The run
produced: a list of what was actually inspected versus quoted; a screenshot analysis noting the contact
label, the missing date, the status-bar clock that is *not* a message timestamp; a UTC archive table
(complaint ≈18:08, archived PDF 18:28:48 with 16 references, revised PDF 20:04:49 with 22, repost
21:32:14); and a probability table — rumours motivated the effort 95–99%; career remark made >95%;
retaliatory intent 30–60%; affiliation restricted collaboration 90–99%; omission a significant
attribution failure 85–95%; unpublished content materially helped, by any route, 10–40% "highly
prior-sensitive" — plus a four-scenario partition summing to 100% (60/25/10/5).

**Amini** (`docs/sources/case-amini-un-fact-finding.md`, 21k words). A long multi-turn investigation
of the UN fact-finding mission's conclusion. It produced mechanism rankings, an explicit separation of
*any assault* / *severe assault* / *assault caused death*, and a final scenario table. It is also the
clearest record of estimates moving under pressure: direct traumatic causation ~20% (line 824) → ~10%
after CCTV, absent lesion and the craniopharyngioma history (line 949) → 15–20% on learning the UN had
non-public material (line ~1334) → 5–8% after the van-arrival behaviour (line ~1394); "any physical
assault" 45% → 55–65% → 35–45% over the same turns.

**One adversarial run** (`docs/runs/evidence-1/`). Leaf K1 of the birthright graph, two agents with
opposite assignments and no shared context, decomposed into K1a–K1d. Both moved toward the other on
their weakest sub-claim: FOR lowered K1d from 25–45 to 15–35 after reading *Wong Kim Ark* in full;
AGAINST raised K1c from ~60 to 75–88 after finding tribal members were in fact tried and convicted
(`RESULTS.md`). AGAINST found a post-freeze Supreme Court decision; **FOR did not search for it and
said so** — an asymmetry of search, recorded, on the record.

### 1.3 What is already mechanical

`Debate/Evidence.lean` (131 lines) types `Grade`, `Provenance` (source, locator, `inspected : Bool`,
quote) and `Entry`, plus `Credence` as a percent interval with three decidable checks:
`entailsCoherent p q := p.lo ≤ q.hi`, `entailsEitherCoherent`, `overlaps`, and `partitionCoherent`
(lows sum ≤ 100 ≤ highs sum). `Debate/Evidence/Examples.lean` applies them to the case tables, and
`K1c_readings_differ` shows the overlap check *detecting* that FOR's K1c and AGAINST's reading-2 K1c
are different propositions. That is the one place in either repository where an evidence artefact is
mechanically checked, and it works.

### 1.4 What is sloppy

- **Unverifiable compliance.** Nothing in a 3,674-word prompt is checkable by anyone but the agent that
  ran it; `docs/open-questions.md` Q2 concedes this in those words. "I inspected the bibliography" is
  an assertion.
- **Anchoring and order-dependence.** The Amini estimates above are non-monotone and each move follows a
  *user* push, not the agent's own search. Nothing records which evidence caused which delta, so the
  trajectory cannot be audited or replayed in a different order.
- **Search bias — "the hole."** `docs/learnings.md` §6 states it exactly: four real sources, checked
  inferences, and a mistaken impression of strength, because the agent is better at finding support than
  objections. `RESULTS.md` says its own run "was a case where the counterevidence was easy to find …
  which is exactly the case the hole is not about."
- **No calibration check and no comparison arm.** No estimate in either case has a resolvable outcome;
  no arm answers "would a model asked directly have done worse?"
- **Single model family, circularity.** Both evidence-1 agents, the formalizer and the ledger are the
  same family; `RESULTS.md` says convergence "is consistent with both having the same blind spot."
- **Provenance drift in the formalisation itself.** `Debate/Evidence/Examples.lean` says its Amini
  numbers are "the ones the evidence layer actually produced," and encodes 45–60 / 15–25 / 5–10. The
  45–60 figure occurs at `case-amini-un-fact-finding.md:2324`, inside a *generic protocol template*
  section ("# 12. Assign probabilities", introduced as "Example:"), while the investigation's own final
  figures are 35–45 / 15–25 / 5–8. A number reached Lean with no record binding it to its source. This
  is the schema's motivating bug.
- **The coherence check is weaker than it looks.** `entailsCoherent p q := p.lo ≤ q.hi` asks only that
  *some* point pair respects the ordering. P(severe) = [15,25] passes against P(any) = [10,20]. It
  should be constraint *narrowing*, not satisfiability (§2.3).
- **`partitionCoherent` trusts the author** that the list is exclusive and exhaustive — precisely the
  thing VE's oracle can decide.

---

## 2. The design

### 2.1 Evidence-record schema

One record = one passage bearing on one leaf. Extends VE's existing `Evidence` dataclass
(`/Users/seyran/code/ve-integration/ve/argument.py:104`), which already carries `evidence_id`,
`claim_id`, `snapshot_id`, `passage`, `reviewer`, `target_scope`, `judgment`.

| Field | Content | Checkable? |
|---|---|---|
| `evidence_id`, `claim_id` | leaf this bears on | yes (resolves in graph) |
| `source_uri`, `snapshot_digest`, `snapshot_bytes` | immutable capture; SHA-256 | yes (recompute) |
| `retrieval_time`, `publication_time`, `time_basis` | UTC; `archive_capture` / `http_header` / `pdf_metadata` / `stated` | partly (format, ordering) |
| `passage_span`, `passage` | byte offsets + quoted text | **yes**: quote-in-snapshot |
| `extraction_claim` | the VE formula the passage is said to support | no (judgment) |
| `extraction_check` | second model, fresh context, sees passage + `extraction_claim` only, returns supports/contradicts/neither | yes that it ran; no that it is right |
| `scope` | actor, time interval, jurisdiction, population | yes against the leaf's declared scope |
| `provenance_chain` | ordered originator → intermediaries → this artefact | partly (well-formedness, cycles) |
| `independence_group` | id shared by all records tracing to one originator | no (declared); **yes** that members share it |
| `direction`, `strength` | `supports` / `undercuts`; likelihood ratio or interval | no |
| `reliability_prior`, `reliability_reason` | one of a fixed enum of reasons (machine-generated log / contemporaneous document / party admission against interest / self-serving statement / anonymous testimony / retrospective recollection) | enum membership only |
| `search_record_id` | the query log that produced it | yes it exists |

Rule: **no assessment may be promoted without at least one record, and every record must name an
independence group even if that group has one member.** A record with `inspected = false` (the
`Provenance` flag already in `Debate/Evidence.lean:58`) cannot carry a likelihood ratio above a declared
cap.

### 2.2 How a leaf gets a probability

Per leaf L: (i) a **prior** with a stated basis from a fixed enum (reference class / structural /
uniform-over-declared-alternatives), (ii) records partitioned into independence groups, (iii) one
likelihood ratio *per group*, not per record — ten reprints of one wire story are one group and update
once, (iv) the posterior as the product of group LRs against the prior odds, (v) if the assessor cannot
justify point values, an **interval** [lo, hi] propagated by interval arithmetic on odds. Interval
output is the default; point values require a `reliability_reason` of machine-generated log or party
admission.

**Adversarial search obligation.** Each side must log queries run, sources returned, and sources
*rejected with a reason*, in a `search_record`. A leaf carries a flag `disconfirming_search : bool`,
set only if the log contains at least one query whose stated target was evidence *against* the side's
assignment, and at least one record with `direction = undercuts` — or an explicit "searched, found
none" entry. This is the mechanisable residue of `learnings.md` §6; it does not prove the search was
adequate, only that its absence is visible. The FOR agent's "did not search for it and said so" becomes
a field, not a footnote.

### 2.3 The coherence checker

VE's oracle decides entailment and equivalence between formal claims. That turns probability coherence
from an authoring norm into a check. Over a set of assessed claims A₁…A_k in one environment:

| Constraint | Trigger | Source of the trigger |
|---|---|---|
| P(A) + P(¬A) = 1 | always | negation is syntactic |
| P(A) ≤ P(B) | `entails(E, A, B)` | tableau certificate |
| P(A) = P(B) | `compare(E,A,B) = EQUIVALENT` | oracle |
| P(A∧B) ≤ min(P(A),P(B)), ≥ max(0, P(A)+P(B)−1) | conjunction assessed | Fréchet |
| P(A∨B) ≥ max(P(A),P(B)), ≤ min(1, P(A)+P(B)) | disjunction assessed | Fréchet |
| P(A) + P(B) ≤ 1 | `entails(E, A∧B, ⊥)` | certificate of exclusivity |
| Σ P(Aᵢ) = 1 | exclusive **and** `entails(E, ⊤, ⋁Aᵢ)` | certificate of exhaustiveness |
| P(root) ≥ Fréchet lower bound of its leaves | certified derivation | §2.4 |

**Implementation.** For k ≤ ~12 assessed claims, build the atom table: for each of the 2^k sign
patterns ask the model finder whether the conjunction is satisfiable. Coherence is then exact LP
feasibility over atom masses (de Finetti), and interval assessments are box constraints. Above k = 12,
fall back to the pairwise and triple constraints above — a sound relaxation, since dropping constraints
can only *reduce* reported violations. **An `UNKNOWN` from the oracle drops the constraint; it never
asserts one.** The oracle's measured `UNKNOWN` rate is 2.0% (8/400,
`/Users/seyran/code/ve-integration/experiments/oracle/results/summary.json`).

**Reporting and repair.** A violation is reported as the *minimal infeasible subset* of constraints
plus the offending assessments, and the LP's nearest coherent projection is offered as a suggestion,
never applied. The assessor must move at least one interval and say which record justified the move;
an unmoved violated assessment blocks the report. Justification, one sentence: *if your stated
intervals admit no probability measure over the environment's models, a bookmaker can assemble bets
you call fair that lose you money in every world consistent with the environment.*

**What it does not guarantee.** Coherent is not correct. A perfectly coherent table built on a lopsided
search is exactly `learnings.md` §6. Replace `partitionCoherent`'s trust in the author with an
exhaustiveness certificate, and the check gets stronger; it never becomes a check on the search.

### 2.4 Propagation to the root

Let leaves L₁…L_n carry a VE certificate for `Entails(E, {L₁…L_n}, C)`. As events, ⋀Lᵢ ⊆ C, so

> **P(C) ≥ P(⋀Lᵢ) ≥ max(0, Σ P(Lᵢ) − (n−1))**   (Fréchet–Hoeffding lower bound)

and the conjunction is at most min P(Lᵢ). This is the **only** sound statement without a dependence
assumption. Under *declared* independence P(⋀Lᵢ) = ∏P(Lᵢ), which is larger; it is reported as a second
line labelled assumption-dependent, never as the bound. With intervals, compute the bound from the lows.

**The bound is vacuous when the doubt budget Σ(1 − P(Lᵢ)) ≥ 1.** Seven leaves at 0.95 give 0.65; seven
at 0.85 give 0. This is exactly where **prover-estimator debate**'s stability assumption shows up. In
that protocol an estimator assigns probabilities to subclaims and the completeness guarantee requires
that small changes in subclaim probabilities cause only small changes upstream. VE makes the
sensitivity computable rather than assumed: ∂LB/∂P(Lᵢ) = 1 for every leaf in the active Fréchet
regime, so the bound is maximally unstable — one leaf moving 0.05 moves the root bound 0.05, and n
leaves each moving 0.05 destroys it. The design's response is to *report* the regime: the checker
states whether the bound is Fréchet-active, how many leaves it has, and the doubt budget, and refuses
to print a lower bound above 0 without also printing n.

**Alternative derivations.** Two certified derivations D₁, D₂ of the same C give C ⊇ (⋀L) ∪ (⋀M), so
soundly **P(C) ≥ max(LB(D₁), LB(D₂))**. Only if the two leaf sets are disjoint *and* declared
independent may one report 1 − (1−p₁)(1−p₂), labelled as such. Shared leaves forbid it; the checker
detects sharing mechanically.

**Countermodels and refuted leaves.** A countermodel on an edge removes that derivation from the
disjunction; the root's lower bound falls to the max over the survivors, possibly 0. A leaf assessed at
0 does the same. Neither produces an **upper** bound on P(C) — the debate project's no-promotion rule
(`inference-protocol.md` §4.3), now arithmetic. Upper bounds have exactly one source: a certified
derivation of ¬C from leaves M, giving P(C) ≤ 1 − LB(M).

### 2.5 Mechanical versus judgment

**Mechanical:** digest recomputation; quote-in-snapshot (byte span matches); scope-subsumption of the
record's scope by the leaf's declared scope; retrieval/publication time ordering and `time_basis`
enum; independence-group membership consistency; every leaf has ≥1 assessment; every assessment has
≥1 record; `disconfirming_search` flag present; coherence constraints (§2.3); Fréchet arithmetic and
sensitivity; alternative-derivation leaf-sharing; graph acyclicity and certificate replay (already VE).

**Judgment, permanently:** reliability priors; whether the passage is *relevant* to the leaf;
likelihood ratios; whether two sources are genuinely independent; whether the root is the question that
was asked; whether the English rendering is faithful. The report must print these in a separate
column, and the presentation leads with the leaf set, never with the certified-edge count
(`ve-protocol-design.md` §2.6).

### 2.6 Calibration without human labels

1. **Post-cutoff resolved questions.** Propositions with a public outcome after the model's cutoff,
   with a frozen document snapshot from before resolution. Score Brier and ECE on leaves and roots.
   Lower-bound validity is testable frequentistically: among roots with LB ≥ 0.8, at least 80% must
   resolve true. `docs/runs/evidence-1/RESULTS.md` contains a ready-made instance — *Trump v. Barbara*,
   decided 30 June 2026, post-freeze, verified, found by one agent and not searched for by the other.
2. **Synthetic worlds.** Sample a latent world from a Bayes net, emit documents with known reliability
   and known duplication structure, compute the exact posterior by enumeration. Ground truth for every
   leaf and, via the certified graph, for the root.
3. **Label-free consistency.** P(A) + P(¬A) = 1; monotonicity under oracle-certified entailment;
   **equivalence invariance** — two VE claims the oracle labels `EQUIVALENT`, shown in different
   renderings and different contexts, must receive the same probability. This needs no ground truth at
   all and is the cheapest signal in the design.

### 2.7 Adversarial pressure on premature estimates

The Amini trajectory and the evidence-1 concessions are the same phenomenon: the estimate improved only
when something pushed. Make it a rule.

- An assessment has status `provisional` until it has survived one full challenge round.
- Every assessment carries an **update ledger**: ordered `(round, p_before, p_after, move_id,
  evidence_id | search_record_id, one-line reason)`. A probability that changes without a ledger entry
  is rejected by the checker. This is the audit trail the Amini file lacks.
- `request-search` names a *specific* target (proposition, direction, source class, time window) and
  obliges the other side to execute it and log the result, including "found none."
- **Stopping:** `settled` when k challenge rounds produce no update with |Δ midpoint| ≥ ε (ε = 0.05)
  and no interval-width change ≥ 0.10; `contested` if the two sides' intervals do not overlap at budget
  exhaustion — and then both are reported, never averaged. Non-overlap is already the useful signal:
  `K1c_readings_differ` in `Debate/Evidence/Examples.lean` caught a *proposition* mismatch that way.

Honest caveat: two cases and one run, all single-family, with no control arm, show that estimates
*move* under pressure. They do not show the moves were improvements. §4 is designed to measure that.

### 2.8 Debate moves added

| Move | Must carry | Checker action |
|---|---|---|
| `submit-evidence(leaf, record)` | full §2.1 record | digest, quote-in-snapshot, scope, extraction check |
| `assess-leaf(leaf, prior, groups, LRs, posterior)` | basis enum + record ids | recompute posterior; run coherence; mark `provisional` |
| `challenge-evidence(record, ground)` | ground ∈ {extraction, scope, staleness, independence, reliability} + the artefact for that ground: a counter-reading with span, a scope witness, a later snapshot with digest, a shared-originator chain, an enum mismatch | void the record if the ground is mechanical (extraction/scope/staleness/independence-chain); mark disputed if reliability |
| `submit-counter-evidence(leaf, record)` | record with `direction = undercuts` | as `submit-evidence`; sets `disconfirming_search` |
| `request-search(leaf, target, direction, window)` | specific target | obliges a `search_record`; unanswered request = outstanding obligation on the report |
| `challenge-coherence(set)` | the violated constraint + its oracle certificate | recompute LP; report minimal infeasible subset |
| `challenge-bound(root)` | the arithmetic disputed | recompute; a wrong bound is the proposer's error |

A move without its artefact is not a move (VE's existing rule).

---

## 3. One system

**Data model.** `Claim` gains `scope` and `assessment_id`. New `Assessment {assessment_id, claim_id,
prior, prior_basis, groups: [(group_id, lr_lo, lr_hi)], posterior_lo, posterior_hi, status:
provisional|settled|contested, update_ledger, search_record_ids, disconfirming_search}`. `Evidence`
gains the §2.1 fields. New `SearchRecord {queries, results, rejections_with_reason, executor, time}`.
New `Bound {root, derivation_id, leaf_ids, lb_frechet, ub_min, lb_independent, doubt_budget,
sensitivities}`. `ArgumentResult` gains `bounds`, `coherence_report`, `assessment_gaps`.

**What the checker reports.**

```
root: R   derivations: 1 certified (7 leaves), 1 gap (countermodel m3)
bound:  P(R) >= 0.62  (Frechet, 7 leaves, doubt budget 0.38 -- ACTIVE regime, d(LB)/d(P_i) = 1)
        P(R) >= 0.71  under declared independence of leaves {1,2,4,6,7}   [ASSUMPTION]
        P(R) <= 0.88  (min leaf)      no certified derivation of not-R: no upper bound from refutation
uncertainty: leaves 3 (0.72) and 5 (0.78) contribute 0.50 of the doubt budget
records: 19 evidence records, 4 independence groups; 3 records fail scope-subsumption (L5)
coherence: satisfied (14 constraints; 2 dropped, oracle UNKNOWN)
gaps: 2 leaves have no disconfirming search on record (L2, L6)
      1 request-search unanswered (L3, round 2)
      1 assessment still provisional (L5)
judgment items not checked: 7 reliability priors, 4 independence declarations, 9 likelihood ratios
```

**Worked example — the credit dispute** (only material in `case-credit-dispute-agent-run.md`). Root R:
*"The Navier–Stokes manuscript publicly available at 18:28:48 UTC on 8 Sep 2026 omitted the
Córdoba–Martínez-Zoroa prior work, and a version citing it was publicly available by 20:04:49 UTC."*

| Leaf | Statement | Assessment | Why |
|---|---|---|---|
| L1 | the 18:28:48 capture has 16 references, none Córdoba–Martínez-Zoroa | 0.98 | digest + quote-in-snapshot are mechanical; residual is archive integrity |
| L2 | the 20:04:49 capture has 22 references including three relevant entries | 0.98 | same |
| L3 | archive capture time = public availability time | 0.85 | the run itself says metadata and headers "are not authenticated publication logs" |
| L4 | that work is *relevant* prior work | 0.90 | interpretive; supported by the revised paper's own explanation; matches the run's 85–95% |
| L5 | the two captures are the same document | 0.95 | identity leaf, invisible in the prose version |

Fréchet: Σ = 4.66, n = 5 ⇒ **P(R) ≥ 0.66**, ≤ 0.90; under declared independence 0.70. Sensitivity says
L3 is the buy: an authenticated publication log moving L3 to 0.95 lifts the bound to 0.76 — and the
run's own "decisive missing evidence" list independently names provenance records. Contrast the
headline claim *"unpublished technical content materially helped OpenAI"*, given 10–40% in the same
file: under this layer it has **no certified derivation at all**, so it gets a direct assessment with
no bound, and the report says so instead of letting it share a page with a checked number. No
probability is attached to any named person's intent.

---

## 4. Two experiments (model-only, ≤ ~$100 each)

Both preregistered; all arms cost-matched including layer authoring; two judge families.

### E-A. Planted investigative worlds

**Ground truth.** Sample a latent world from a Bayes net over ~15 binary facts. Emit a corpus: each
document has a known emission model (reliability), documents are grouped by originator with known
reprint multiplicity, and *m* misleading documents are planted. The root is derived from leaves by a
certified VE graph, so the exact posterior P(root | corpus) is computable by enumeration. Synthetic
vocabulary ⇒ contamination-free.

**Arms.** (1) frontier model, corpus in context, "give P(root)"; (2) two-sided debate, no layer, judge
outputs a probability; (3) RAG with citations; (4) layer without the adversarial round; (5) full layer;
(6) full layer, independence grouping disabled; (7) full layer, coherence checker disabled.
**Sub-study E-A0** (~$15, no retrieval): elicit probabilities for logically related claim sets in
separate contexts with randomised order; measure raw violation rate per constraint class and the
LP distance to the nearest coherent assignment; then test whether projecting to coherence improves
Brier.

**Metrics.** Leaf and root Brier, ECE; **bound validity** = fraction of items where the true posterior
falls below the claimed lower bound, reported twice (with model leaf probabilities, and with
ground-truth leaf probabilities, where violation must be 0 by construction); **duplication robustness**
= ΔBrier when each corpus is reprinted ×10; **planted-misleading robustness** = ΔBrier in *m*;
independence-grouping F1 against ground-truth groups; coherence-violation rate; $/item.

**Predictions.** Arms 1–3 degrade sharply under ×10 duplication; arm 5 near-flat *conditional on
grouping F1*, which is the real measurement. Arm 5 > arm 4 on Brier under planted misleading evidence.
Arm 7 − arm 5 isolates coherence. **True by construction:** the Fréchet bound holds given correct leaf
marginals; deduplication helps if groups are correct. **Not by construction:** grouping F1, whether
coherence enforcement improves Brier, whether the challenge round repairs overconfidence, all costs.
**Refutation:** arm 1 matching arm 5 on Brier at equal cost *and* not degrading under duplication; or
bounds vacuous (0) on a majority of items with n ≥ 5 — a vacuous bound is worthless however sound.
Budget ~$70–90.

### E-B. Post-cutoff resolved questions, staged

**Ground truth.** ~120 propositions resolved between the model cutoff and run date, with a frozen
pre-resolution snapshot; plus 40 matched pre-cutoff questions as a contamination control. Each is
decomposed into a 3–8-leaf VE graph whose root is the resolvable proposition.

**Arms, staged within item** (this is the point): (0) direct probability, no search; (1) direct with
search; (2) RAG with citations; (3) layer, single pass; (4) layer + executed `request-search`;
(5) layer + one adversarial challenge round. Estimates are recorded at every stage.

**Metrics.** Brier and ECE per stage; **overconfidence repair** = E|p₀ − y| − E|p₅ − y|; fraction of
items whose first estimate was on the wrong side of 0.5 and was corrected; movement direction
conditional on outcome; **lower-bound calibration** (among roots with LB ≥ t, fraction resolving true,
for t = 0.6/0.7/0.8/0.9); pre- vs post-cutoff gap as the contamination check; $/item.

**Predictions.** Stage 0 overconfident; most of the gain at stage 4 (forced search), a smaller but
non-zero gain at stage 5. **Refutation:** stage 3 ≈ stage 5 (the challenge round adds nothing — the
user's observation does not generalise), or arm 1 Brier ≈ stage 5 Brier at a tenth of the cost.
**True by construction:** nothing, except that stage estimates exist. Budget ~$60–90.

---

## 5. Risks and limits

**False precision.** A bound printed to two decimals from six judged likelihood ratios is arithmetic
theatre. Mitigation: intervals by default; print n and the doubt budget beside every bound; refuse
point posteriors without an enumerated `reliability_reason`.

**Garbage-in priors.** Everything downstream is a function of priors and LRs that no check touches.
The report's separate "judgment items not checked" column exists so a reader can see how much of the
number is opinion.

**Adversarial source manufacture.** A digest proves bytes existed at retrieval time. It proves nothing
about authenticity, and an adversary can stand up real pages and real-looking outlets. Independence
groups are *declared*, so manufacturing apparent independence is the natural attack — the analogue of
VE's merged-predicate attack, one layer down, and the checker is blind to it by construction.

**Base-rate neglect and stability.** Many slightly uncertain leaves make the bound vacuous; the
temptation will be to assume independence to recover a printable number. The independence line must
stay labelled `[ASSUMPTION]` and must never be the headline.

**Ethics.** The Amini case concerns a real person's death, named officials, named physicians and a
contested state investigation. Probabilistic output about such matters must be scoped to propositions,
never to persons; must not assign probabilities to identified individuals' criminal conduct; must not
be presented as a finding of fact, an investigation, or a substitute for a fact-finding mission; and
must reproduce the source's own limits (the UN mission "was unable to determine the immediate medical
cause of death"). Prefer the credit dispute for demonstrations.

**Never claim:** that these are measured frequencies; that a lower bound is the probability; that a
coherent table is an accurate one; that a certified graph makes any leaf true; that a digest
authenticates a document; that a logged search was an adequate one; that a checked conditional argument
is an approval.

---

## 6. Build list

| Component | Effort |
|---|---|
| Evidence-record schema + wire validation; digest, quote-in-snapshot, scope-subsumption, time-basis linters | 1.5 d |
| `Assessment`, update ledger, `SearchRecord`; status machine (provisional/settled/contested) | 1.5 d |
| Coherence checker: atom table via model finder, LP feasibility, minimal infeasible subset, nearest-coherent projection, pairwise fallback | 3 d |
| Bound engine: Fréchet, independence line, alternative-derivation max, leaf-sharing detection, sensitivities, doubt budget | 1.5 d |
| Checker report §3 + "judgment items not checked" column | 1 d |
| New debate moves in the runner; obligation tracking for unanswered `request-search` | 2 d |
| E-A world generator, exact posterior, duplication/misleading injectors | 3 d |
| E-B question set, snapshot freezing, staged harness | 2 d |
| Extraction-check harness (fresh-context second model) | 0.5 d |
| Lean: lift `Credence` to narrowing + prove Fréchet bound composition sound for `ClaimGraph` | 2–3 d |
| Port `Debate/Evidence.lean` records into VE's schema; re-derive the Examples tables *from records* | 1 d |

≈ three engineer-weeks, or under a week with parallel agents. No language extension: probabilities live
in the assessment layer, never inside VE formulas — VE's own spec puts "general probability" outside
the profile (`docs/spec/debate-protocol.md`, "Bounds and unsupported claims"), and that boundary is
load-bearing, not an omission.
