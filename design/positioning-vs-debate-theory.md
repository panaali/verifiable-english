# Positioning Verifiable English against Irving-group debate theory

Sources read in full from arXiv HTML (downloaded and converted to text locally, not via a summarising
fetch tool): **PE** = Brown-Cohen, Irving, Piliouras, Chen, Li, Xun, *Avoiding Obfuscation with
Prover-Estimator Debate*, arXiv:2506.13609**v2**; **DQC** = Brown-Cohen, Irving, Marshall, Newman,
Piliouras, Szegedy, *Debate is efficient with your time*, arXiv:2602.08630v1; **SC** = Buhl, Pfau,
Hilton, Irving, *An alignment safety case sketch based on debate*, arXiv:2505.03989v3; **DED** =
Brown-Cohen, Irving, Piliouras, *Scalable AI safety via doubly-efficient debate*, arXiv:2311.14125v1;
**BC20** = Barnes & Christiano, *Debate update: obfuscated arguments problem* (Alignment Forum, 23 Dec
2020). VE side read locally: `docs/spec/debate-protocol.md`, `docs/architecture-and-design.md`,
`lean/METATHEORY.md`, `lean/CLOSURE.md`, `docs/oracle.md`, `reviews/SYNTHESIS.md`, and the parallel
`design/ve-protocol-design.md`.

---

## Direct answer

**(a) What they already cover, and we must not claim.** PE §8 already proposes our headline
combination, almost verbatim: "one could require the debaters to produce machine-verifiable proofs in
Lean for all mathematical subclaims, and use prover-estimator debate to verify fuzzier subclaims."
Proofs-plus-debate is their idea, not ours. DQC already assumes a verifier that checks one step of a
computation cheaply — Theorem 6 checks a single gate in `log(size) + 3` queries — so "the judge checks
a deductive step at near-zero cost" is an existing *assumption* of their model, not a gap we fill
theoretically. DED Theorem 5.3 already achieves `O(1)` oracle queries with cross-examination. And SC
§4.4.2 D5.5 states that cross-examination *already avoids* the cross-branch definitional-inconsistency
failure that our identity binding targets. We should claim none of these as novel.

**(b) Where we are complementary.** Their theory assumes what VE builds: a claim with a fixed meaning,
and a verifier that can actually decide whether one claim follows from others. In DQC that verifier is
a logic gate; in a natural-language debate it is a human or an LLM, and nothing in their papers makes
it sound. VE's Lean-verified `checkCertificate_sound` is an instantiation of an assumption they
already rely on, for a setting where it is currently false. That is real but modest, and it is
engineering, not theory.

**(c) Where VE could add genuine insight.** Highest confidence: *measuring the leaf/deduction split of
real obfuscated arguments*. PE §8 names as its main open problem understanding "when stability can be
achieved ... in practice for debates in messy, unformalized settings"; nobody has measured what
fraction of obfuscation hides in invalid inferences versus false leaves. BC20 defines both flaw types
(a node "not implied by its children" versus a false answer) and never separates them. We can, and the
number decides how much the §8 hybrid can buy. Medium confidence: a `challenge-formalisation` move
carrying a *checked* distinguishing model (VE's three-valued oracle) as a concrete mechanism for
D5.5-style disputes. Low confidence: anything about the English surface — our own reviewers report the
effect vanishes by 32B (`SYNTHESIS.md` §A1).

**(d) What undercuts us.** Three things, seriously. First, the stability analysis below: a
machine-checked conjunction is the *worst possible* node for PE debate's ρ-stability, so checked
deductions do not help there and arguably hurt. Second, BC20's canonical obfuscated argument (RSA: "no
factor below X" and "no factor above X") is a **valid** deduction from **false leaves** — our checker
certifies it and catches nothing. Third, PE §8's own dichotomy classifies mathematical proofs as the
*unstable* class, i.e. exactly the class their protocol cannot exploit.

---

## 1. Their results, stated precisely

### 1.1 Prover-estimator debate (PE, v2)

**Setting.** A claim is membership `x ∈ L` for `L ∈ Γ^O(T) = NTIME^O(T) ∩ coNTIME^O(T)` (Defs 3.1,
3.2): problems with proofs of both "yes" and "no" checkable in time `T` given a **human judgement
oracle** `O` (§3.1: "queries to the oracle `O(u)` corresponds to querying human judgement"). The judge
is a polynomial-time oracle Turing machine `V` (Def 4.1) returning a payoff in `[-1,1]`. Debater power
is **purely relative**: `A` ranges over an arbitrary `𝒜`, and `ℬ` is circuits of a given size that may
query `A` at each gate.

A **recursive decomposition** (Def 5.1) of depth `d`, width `q` is a machine `M_D(x, y, z)` mapping
queries and answers to the parent's answer, bottoming out at leaf queries answered by `O` against an
implicit proof `u` of length `m ≤ q^d`. For any `L ∈ Γ^O(T)` there is a natural decomposition with
`d = log T`, `q = 2`, where `M_D` **"simply computes the AND function on the query answers"** (§5) —
this matters below. `𝒜`-provability (Def 5.2) says one `A ∈ 𝒜` correctly answers every query in the
decomposition with probability `1 − γ`.

**Stability — the exact definition (Def 5.3).** For `z ∈ {0,1}^q`, let `D_ε(z)` be the set of
distributions `p` over `{0,1}^q` with `Pr_{z'~p}[z'_i ≠ z_i] ≤ ε` for every `i ∈ [q]`. Then `M_D` is
**ρ-stable at node `(x,y)`** if for every `ε > 0` and every `p ∈ D_ε(z)`, where `z` is the ground-truth
solution at `(x,y)`,

> `Pr_{z'~p}[ M_D(x,y,z') ≠ M_D(x,y,z) ] ≤ ρ · ε`.

`M_D` is ρ-stable for input `x` w.r.t. `A` if this holds at every node the debate tree generated by `A`
might visit. Note the constraint is on **marginals** — v2's introduction records that an earlier
preprint's theorem was wrong because the definition used *conditional* probabilities; the fix was
found by the last three authors (Chen, Li, Xun). **Observation A.7** makes it exact: `M_D` is ρ-stable
at `(x,y)` **iff** `fbs_z(M_D(x,y,·)) ≤ ρ`, the *fractional block sensitivity* (Def A.6, an LP over
sensitive blocks) of the node function at the ground truth.

**Protocol (Fig. 2).** Reward ratio `r = 1/ρ`. Per round: `A` declares `p̂_k` over/under/correct
(`∈ {-1,0,1}`) and emits queries `y^k`; `B` returns a **joint** distribution `p_k` over `{0,1}^q`;
`z^k ~ p_k` under trusted randomness; `A`'s reward is `r^k · A^k · (M_D(x,y^k,z^k) − p̂_k)`. Then
**`A`** — not `B` — picks the child `j`, and `p̂_{k-1}` is the *marginal* of `z^k_j`. The last round
uses `O` directly.

**Theorem 6.1.** *Completeness*: if `M_D` is `𝒜`-provable with prob. `1−γ` via `A*` **and** ρ-stable at
`x` w.r.t. `A*` with prob. `1−γ`, then some `A ∈ 𝒜` gets `E[V^{A,B}(x)] ≥ 1/ρ^{d+1}` against **any**
`B` of any size, with prob. `≥ 1−2γ`. *Soundness*: for `ℬ` = circuits of size `O(q 2^{3q} n d²/η²)`
querying `A` at each gate, for every `A ∈ 𝒜` there is `B ∈ ℬ` with
`E_x[V^{A,B}(x)] ≤ Pr[A(x)=L(x)]/ρ^{d+1} + η`. **Stability is required for completeness only.**
Theorem 6.2 converts this to: in every `α`-approximate `A`-leading Stackelberg equilibrium,
`Pr[A(x)=L(x)] > 1−5ε`. The `2^{3q}` factor forces `q` to be constant in `n` (§7: `B` must explicitly
represent a distribution over `2^q` answers).

**Savings condition, stated by them.** §6.1: prover-estimator debate improves on doubly-efficient
debate's `O(n^c)` cost only "when there exists a very stable decomposition `M_D` (`ρ ≪ q`)".

**Stated limitations / open problems (§8).** Stability may fail for all efficient decompositions, in
which case the protocol safely rejects; whether stability is *necessary* is open; results are
average-case not worst-case; no lower bound on `B`'s circuit size is known. And the hybrid proposal:
an "optimistic hope" that problems split into "those that require very precise dependence on
individual subclaims (e.g. **mathematical proofs**)" and "those that do not (e.g. scientific knowledge
obtained by noisy empirical evidence)" — Lean proofs for the former, PE debate for the latter.
Appendix C recommends debater asymmetry, explicit uncertainty estimates, and multiple `B` updates per
`A` update.

### 1.2 Debate query complexity (DQC)

**Setting.** Two **all-powerful** provers, a deterministic verifier `M_ℓ` that adaptively queries `ℓ`
bits of `x‖α_1β_1…α_kβ_k` (§2). `DQC(f)` = least `ℓ` admitting a `(k,ℓ)`-debate; `k` is unbounded in
the definition but Lemma 3 shows `k ≤ 2^ℓ` w.l.o.g. **Results.** Cor. 4: `DQC(f) ≥ log n` if `f`
depends on all variables. Thm 5: `DQC(f) ≤ depth(C_f)+1` (Karchmer–Wigderson). Thm 6:
`DQC(f) ≤ log(size(C_f)) + 3` by **cross-examination** — Alice writes every gate value, Bob names one
bad gate, the verifier reads that gate and its two inputs and applies the gate's truth table. Lemma 8
generalises this; **Thm 9: `PSPACE/poly = {f : DQC(f) ≤ O(log n)}`**. Cor. 7: proving
`DQC(f) ≥ log n + 6` for `f ∈ P` would beat the best known `≈5n` circuit lower bound. §5: randomisation
does not help in the `PSPACE/poly` regime. **Stated limitations.** Open problems name exactly our
concerns: "Our results assume unbounded debaters"; verifier opacity when the verifier is an LLM;
whether LLM debates show the predicted logarithmic scaling; human value oracles.

### 1.3 Safety case sketch (SC) and BC20

SC's key claim 2 routes truth through a hypothetical full-tree process `M` and needs (i)
M-approximation and (ii) truth of `M`. **D5.5** (§4.4.2), quoted: "it might be possible to define the
same term differently in different subclaims, rendering an argument that appears valid but is not; if
human judges are called only at the leaf nodes, such inconsistencies might not be caught by `M`. Some
debate protocols, such as cross-examination, avoid this failure mode, but prover-estimator debate —
our example in this safety case — does not." §4.4.2 also leaves the stability evidence box **blank**
(E5.5), and floats transforming an unstable `M` into a stable `M*`. §5.2 lists "avoids gerrymandering"
and "does not require stability" as desiderata PE debate fails.

BC20 defines the problem: arguments invalid through a few flawed steps, too large to search naively,
with neither debater knowing where. Its key sentence for us — a flaw exists "if one of the nodes is
**not implied by its children**, *or* if one of the dishonest answers is obviously worse" — gives two
distinct flaw classes. Its conclusion anticipates stability by five years: we can only trust arguments
"small enough that we could find a single flaw if one existed, or ... robust enough that it is correct
unless it has many flaws."

## 2. What they assume that VE could supply, and vice versa

| Their assumption | VE's offer | Honest status |
|---|---|---|
| Claims have a fixed meaning across the tree | `source_id`/`meaning_id` under one environment `E`; a changed formula cannot inherit a certificate (`debate-protocol.md`) | Supplies *symbol*-level fixity only; sense-level equivocation survives (weakness #1) |
| The verifier can decide a single step (DQC Thm 6's gate check; `M_D`'s AND) | `checkCertificate_sound`: acceptance ⟹ entailment over **all** admissible structures, no certificate-soundness premise | Genuine, and stronger than they need; but they already assume it |
| Consistency of definitions across branches (D5.5) | Identity binding + `split-predicate` voiding certificates over the split symbol | Mechanical version of what cross-examination already achieves by questioning |
| `O` = "human judgement" answers leaves correctly | Nothing. Leaves are exactly where VE checks nothing | VE *depends* on this assumption as much as they do |
| Debaters can afford their strategies | Nothing — VE **adds** cost (formalisation + proof search) | VE's coverage data makes a hidden cost visible; see §5 |

What VE assumes that they do not: that the task is formally statable at all in a function-free
many-sorted FOL fragment with equality and transitive closure; that a human can sign off on a root
claim's *meaning* (untested with humans — `SYNTHESIS.md` §A5: "no human has read the Lean theorem
statements, the templates or the preregistrations"); and that proof production is affordable.

## 3. The stability question, worked

**Claim to test.** If an argument is a VE claim graph whose internal edges are machine-checked, then
uncertainty lives only at the leaves; does ρ-stability then constrain only the leaf distribution?

**Answer: it relocates the requirement onto the worst-case node shape. It does not weaken it, and by
one reading it makes it worse.**

Work Def 5.3 directly. Take a VE root `R` certified as `Entails(E, {L_1,…,L_N}, R)` with all internal
edges checked. In PE's framework the node function is `M_D(x,y,z) = z_1 ∧ … ∧ z_N`, where `z_i` is
"leaf `i` is true". Honest case: ground truth `z = 1^N`, `M_D(z) = 1`.

*Lower bound.* Let `p` place mass `ε` on each of the `N` points "only leaf `i` false", and `1 − Nε` on
`1^N` (valid for `ε ≤ 1/N`). Every marginal `Pr[z'_i ≠ 1] = ε`, so `p ∈ D_ε(z)`. But
`Pr[AND(z') ≠ 1] = Nε`. Hence ρ must be at least `N`.

*Upper bound, for any node.* `Pr[M_D(z') ≠ M_D(z)] ≤ Pr[z' ≠ z] ≤ Σ_i Pr[z'_i ≠ z_i] ≤ qε`, so
**`ρ ≤ q` holds trivially for every `M_D` of width `q`**. Equivalently `fbs ≤ q` (Obs. A.7).

So `fbs_{1^N}(AND_N) = N` **exactly**: a conjunction sits precisely on the trivial ceiling. A checked
deductive composition is the *maximally unstable* node function of its width. Contrast the paper's own
worked example (§5): majority over studies with 2/3 support is ρ-stable at `ρ = 4` regardless of how
many studies there are.

**Why exactness does not help.** Definition 5.3 never mentions how `M_D` is computed. Both `M_D(z')`
and `M_D(z)` are evaluated exactly; the perturbation is applied to the *ground truth of the
subclaims*, not to the node's computation. So "a verified checker propagates no estimation error" is
true and **irrelevant to stability**. Stability was never about noisy composition; it is about a node
function being sensitive to which leaves are true. Machine-checking the AND changes nothing about the
AND.

**Quantitative consequence.** Completeness gives `E[V] ≥ 1/ρ^{d+1}`.
*Flat shaping* (one node, `q = N`): `ρ = N`, and soundness needs `ℬ` of size `O(q 2^{3q} nd²/η²)` —
exponential in `N`, outside the regime where §7 requires `q` constant. Not usable.
*Balanced binary AND tree* (`q = 2`, `ρ = 2`, `d = log₂ N`): `ℬ` stays polynomial, but the reward gap
is `1/2^{d+1} = 1/(2N)`. You need `Ω(N)` debates per unit of training signal — precisely the
`O(n^c)` cost of doubly-efficient debate, which §6.1 says PE debate beats only when `ρ ≪ q`. Here
`ρ = q`. **A purely deductive VE argument gives prover-estimator debate zero advantage.** PE §8 says
as much when it files "mathematical proofs" under the precise-dependence, i.e. unstable, class.

**What would have to be true of the leaves.** Since ρ is a combinatorial property of the node function
at the ground truth, making leaves *individually more certain* does not reduce it — Def 5.3 quantifies
over all `p` with the given marginals, including adversarially correlated ones. Only the argument's
**shape** matters. My own LP calculation from Obs. A.7 (not a theorem in the paper): if the root has
`k` independent derivations from disjoint leaf sets of size `s` each, minimal sensitive blocks pick one
leaf per derivation (`k` coordinates), one can pack `s` such blocks disjointly, and the per-coordinate
budget caps the LP at `ks/k = s`. So `fbs = s`: redundancy across derivations does **not** reduce ρ
below the length of a single derivation; `ρ = 1` only when individual leaves suffice (a pure OR). The
design implication is uncomfortable and worth stating: to interoperate with PE debate, VE should
prefer **short, redundant, over-determined** claim graphs over minimal elegant proofs — the opposite of
what formalisation practice optimises.

**Verdict.** Relocates, and mildly worsens. VE should not claim to weaken the stability assumption.
The defensible claim is narrower: VE makes ρ *measurable* on real arguments, which is exactly the §8
open problem.

## 4. Obfuscated arguments specifically

**What PE guarantees.** Soundness (Thm 6.1) holds "even if stability is violated and the subproblems
are obfuscated": `B` of size `O(q2^{3q}nd²/η²)` produces outcome-indistinguishable probabilities
(Lemma A.3, following Dwork et al. 2021), so `A` cannot reliably point at an error direction, and `A`'s
payoff falls below a known threshold. §8: "requires stability for completeness but not soundness, and
thus is safe to use even if one is not confident in stability." Obfuscation therefore yields
**rejection**, not deception. That is a real guarantee and VE has nothing comparable.

**What a verified checker adds.** BC20's flaw taxonomy has two classes. A checker eliminates the first
("a node not implied by its children") **entirely and at zero judge cost**, because every edge either
carries a certificate — hence `Entails` over all admissible structures — or is a visible unresolved
obligation, or is a `gap` with a finite countermodel the judge evaluates in one scenario. The search
space of `N` plausible-looking steps collapses to the declared leaf set.

**Where it does not.** BC20's own canonical example is immune. "No prime factor less than X" ∧ "no
prime factor greater than X" ⟹ "no prime factors" is a **valid** inference; the flaw is a false leaf,
and locating it is factoring. Our checker certifies the edge and catches nothing. Worse, BC20's
construction recipe (§"General method") explicitly manufactures *false subclaims*, not invalid
inferences: "you have a large number of fairly substantive and relevant false claims that you're
allowed to assume." So on the literature's paradigm cases, VE's contribution to obfuscation is **zero**,
and this must be said plainly.

**Migration map.**

| Destination | Addressed by | Strength |
|---|---|---|
| Leaf premises | **Their** estimator (PE soundness); VE nothing | Their result, not ours |
| The formalisation (root ≠ task) | VE `challenge-formalisation` + oracle `DIFFERENT` with a checked distinguishing model | Procedural move, no guarantee |
| Vocabulary / merged predicate | VE `split-predicate`, voiding certificates over the split symbol; cross-examination (per D5.5) | Procedural; checker "blind by construction" (`debate-protocol.md`) |
| Omitted requirements | Nothing, in either | Open in both |

Note the asymmetric risk our own docs already record (weakness #2): a "proof checked" label on an
argument whose flaw lives in a leaf may make it *harder* to spot than in prose. That is a testable
harm, and the honest framing of the whole obfuscation story.

## 5. Query complexity with a checker in the loop

DQC's verifier queries `ℓ` bits of the transcript. Folding a verified checker into `V` means deductive
queries are answered by machine at **zero human cost**, so the human-query count would be over leaves
only. But two corrections are needed before claiming anything.

First, **their model already grants this**. DQC Thm 6's verifier reads one gate index plus two input
wires and "can determine which gate type this is and check whether Alice's output matches the logic
table" — the per-step check is already free and sound by fiat; DED Thm 5.3 already gives `O(1)` oracle
queries. VE cannot improve these bounds. It can only make the assumption *true* for semantic
entailment between English claims, where today it is not: instantiation, not theory.

Second, **the cost does not vanish; it moves to the debaters**, and both papers are built so that this
is invisible. DQC assumes provers are "all-powerful" (§2) and lists "Computationally bounded debaters"
as open. PE bounds `B` only *relative to* `A`, leaving `𝒜` arbitrary. Formalisation effort, proof
search, and the risk that an honest proposer cannot formalise the domain at all land in that unmeasured
space — `ve-protocol-design.md` §3(a) records strict fit 0% for Cedar, 0% for FRET. Making that cost a
measured quantity is a contribution their framework structurally cannot make.

## 6. What would be genuinely new, and what would not

**Not new.** Proofs combined with debate — PE §8, their own proposal. Controlled English — ACE/PENG/
Logical English (`SYNTHESIS.md` §A4). Verified FOL provers — Ridge–Margetson, Schlichtkrull, SeCaV
(*citations to verify*; not opened). A cheap per-step check by the judge — DQC Thm 6. Cross-branch
consistency via cross-examination — SC D5.5. "Trust only small or robust arguments" — BC20, 2020.

**New if the experiments work.** (1) An *implemented* verified substrate in which "check every step"
is genuinely free and sound for a human-readable claim language: PE §8 proposes the architecture;
nobody has built the English-facing half. (2) **Measured migration of obfuscation** — the
leaf-versus-deduction split of real obfuscated arguments. BC20 names both flaw classes and never
separates them, and the ratio determines the entire value of the §8 hybrid. Strongest card. (3) A
formalisation-challenge move backed by a *checked* distinguishing model, as a concrete mechanism for
D5.5 disputes. (4) **Empirical ρ and leaf/deduction ratios in real arguments**, answering PE §8's call
to understand "when stability can be achieved ... in practice for debates in messy, unformalized
settings" and to characterise "the structure of problems that admit stable decompositions". (5) The
measured cost of formalisation — the debater-side cost their unbounded-debater assumptions hide.

All five are contingent: `SYNTHESIS.md` records that the surface effect vanishes by 32B, that E4
measured deference to a printed verdict rather than comprehension, and that no human has yet read the
Lean statements.

## 7. Three questions for the authors

1. **Is a certified conjunction the worst case for you?** For `M_D = AND` over `q` true subclaims,
   `fbs = q`, so `ρ = q` and the completeness gap `1/ρ^{d+1}` degenerates to doubly-efficient debate's
   cost — the regime §6.1 says you beat only when `ρ ≪ q`. Does that mean a machine-checked deductive
   skeleton is precisely the *worst* input to prover-estimator debate, and is the §8 hybrid therefore
   meant to **remove** proof-carrying subtrees from the recursion (treating a certified subtree as a
   single leaf) rather than recursing through them?

2. **Is there a version of Theorem 6.1 with verifier-computable nodes?** If some `M_D` nodes are
   computed exactly by a trusted checker at zero oracle cost, does the operative ρ become the
   fractional block sensitivity of the *leaf-to-root* function, and does the `O(q2^{3q}nd²/η²)` bound
   on `ℬ` change when `B` need not estimate those nodes at all?

3. **Does formal identity recover cross-examination inside PE debate?** D5.5 says cross-examination
   avoids cross-branch definitional inconsistency and PE debate does not. If every subclaim is bound to
   a canonical formal identity, so the same symbol cannot be silently re-interpreted, does that recover
   the cross-examination property without the multiple-copies machinery — or does the equivocation just
   move into the interpretation of the formal vocabulary, leaving the theory unchanged?

## 8. Plain summary (150 words)

Irving's group has, in the last year, published the protocol we would be building on and the
limitation that constrains it. Prover-estimator debate mitigates obfuscated arguments by having the
estimator assign probabilities the prover cannot distinguish from truth; it is sound even under
obfuscation, but useful only for ρ-stable arguments. Their §8 already proposes combining Lean proofs
for precise subclaims with debate for fuzzy ones — our architecture, in their words. Working through
their Definition 5.3, a machine-checked conjunction over N leaves has ρ exactly N, the worst possible
value, so verified deductions do not weaken the stability assumption; they relocate it onto the least
favourable node shape. Verifiable English's defensible contribution is therefore not theoretical. It
is an implemented verified substrate plus measurements they explicitly ask for: where obfuscation
actually hides, and what stability looks like in real arguments.

## 9. Open problems in debate / scalable oversight and what VE could address at frontier scale

Beyond obfuscated arguments. "Stated" = I read the sentence in the cited section; "unverified" = I did
not open the source. VE mechanisms: **CHK** verified checker, **ID** identity-bound claims, **ORC**
equivalence oracle, **GRAPH** claim graphs with retained assumptions, **SPLIT** predicate splitting,
**EVID** evidence records.

| Problem | Source | VE mechanism | Honest limit | Frontier-scale experiment |
|---|---|---|---|---|
| **Gerrymandering / inconsistent definitions across branches** | SC §4.4.2 D5.5; §5.2 bullet 4 ("prover-estimator debate ... does not" avoid it) — stated | ID + SPLIT + ORC | Binds *symbols*, not senses; a merged predicate is certified anyway (weakness #1); cross-examination already solves it | Merged-predicate duel: equal frontier debaters, VE arm vs cross-examination arm, measure judge false-approval |
| **Verifier opacity / trusted weak checker** | DQC §6 open problems ("When the verifier is a large language model ... debaters cannot exploit its structure") — stated. AI-control framing — unverified | CHK | Covers only the formal fragment; JSON decoding and env validation are trusted (`ve-protocol-design.md` §2.5) | Untrusted frontier prover + zero-capability Lean checker vs LLM-judge baseline, on planted-flaw specs |
| **Judge exploitation by persuasion / sycophancy** | SC §4.4.2 ("claims playing on human biases or emotions") — stated | CHK (findings are not arguable) | Only deductive findings are immune; the printed verdict invites deference, and E4 measured deference (`SYNTHESIS.md` §A2) | Forged-checker-line control arm (SYNTHESIS item 12) at frontier scale |
| **Systematic judge error** | SC §4.4.2 C5.1, §5.2 bullet 5; PE §8 cites Irving (2025) — stated | CHK + ORC countermodels | VE cannot fix leaf judgement, which is where systematic error lives | Compare error on leaves judged in prose vs with a checked distinguishing model |
| **Reward hacking / model writes its own spec and tests** | Not in these papers — unverified (Krakovna et al.; Denison et al.) | ID + GRAPH | Only if the spec is signed off *before* the work and cannot be re-authored | Agent optimises against a spec it may rewrite; measure drift via `meaning_id` + ORC |
| **Hiding information in free parameters (subclaim/vocabulary choice)** | PE §8 cites Pfau & Irving (2025), *Unexploitable search* — stated as open; paper unverified | SPLIT + ORC | Choosing the vocabulary *is* a free parameter; VE adds one rather than removing it | Measure whether a critic's `split-predicate` right cancels the proposer's vocabulary advantage |
| **True-but-misleading claims, suboptimal framings** | SC §3.4 fn. 7 — stated | EVID + ID | VE checks entailment, never pragmatics | Frontier proposer writes a technically-true certified report; measure judge detection |
| **Efficient verification of long work / query budget** | DQC (whole paper); open problem "Do debates between actual language models exhibit the logarithmic query scaling" — stated | CHK + GRAPH | Cost moves to authoring and proving, which their unbounded-debater model hides | Measure judge queries and proposer tokens vs argument size; test the `log` prediction |
| **Unfaithful reasoning / process supervision** | BC20 §"Are these obfuscated arguments distinctive" (honest debaters "may need to give an argument that doesn't mirror ... their reasoning") — stated; CoT-faithfulness literature unverified | CHK | Sidesteps faithfulness rather than measuring it: a certificate is valid regardless of how it was found | Compare judge accuracy under certified arguments vs CoT, with a deliberately unfaithful proposer |
| **Long-horizon drift, compaction, hand-offs** | SC §3.4, §4.5 (distribution shift, alignment faking) — stated; "compaction" is our framing — unverified | ID + ORC | Verbatim JSON survives compaction equally well; ORC matters only when a requirement is *restated* | F1: requirement retention across long context and forced compaction |
| **Deductive arguments may not exist for the domain** | SC D5.4; §5.2 ("will many questions ... be difficult to answer via deductive arguments?") — stated | none — VE is *exposed* to this | Our own coverage data is bad (strict fit 0% Cedar, 0% FRET) | Measure formalisable fraction on an independently sourced task distribution |
| **Exploration hacking, sandbagging, gradient hacking, collusion** | SC §3.3, §4.4.2 C5.2, §5.2 — stated | none meaningful | VE adds nothing; do not claim it | — |
| **Grounding of factual leaves** | PE's oracle `O` (§3.1) is assumed correct — assumption, not stated problem | EVID only | VE verifies no facts (`debate-protocol.md`) | — |

**Top three** by (community importance) × (VE fit) × (cheap, model-only):

1. **Gerrymandering / D5.5.** Explicitly a protocol desideratum PE debate fails, and §5.2 asks for a
   protocol combining it with cross-examination; ID + SPLIT is a candidate mechanism that needs no
   multiple-copy machinery. Cheapest to test (F2 exists). The result is only interesting if VE beats a
   *strong* cross-examination baseline, not prose.
2. **Verifier opacity / trusted zero-capability checker.** Their own open problem, and VE's single
   strongest asset — a verifier whose soundness is a theorem rather than a capability assumption. Fits
   the AI-control audience directly.
3. **Judge exploitation by persuasion.** High importance, moderate fit, very cheap, and the honest
   version includes the forged-checker control that could show *harm* instead of benefit.

Strong fourth, held back only because I could not verify its sources: reward hacking where the model
authors the spec it is graded against — identity-bound claims are an unusually clean answer there.

## 10. Related 2025–2026 work encountered

**Opened and read:** PE (2506.13609v2); DQC (2602.08630v1); SC (2505.03989v3); DED (2311.14125v1);
BC20 (Alignment Forum).

**Seen only as citations** (not opened — titles taken verbatim from the reference lists of PE and SC):

- Pfau & Irving (2025), *Unexploitable search: blocking malicious use of free parameters* — PE §8 flags
  it as the open problem of debaters hiding information in the subclaims they choose. Most relevant
  unread item for VE, since choosing the vocabulary is exactly a free parameter.
- Irving (2025), *Dodging systematic human errors in scalable oversight* — PE §8's other named gap;
  bears directly on VE's leaf-judgement assumption.
- Bengio et al. (2025), *Superintelligent agents pose catastrophic risks: can Scientist AI offer a
  safer path?*, arXiv:2502.15657 — PE Fig. 3 contrasts its Bayesian structure with PE debate.
- Hammond & Adam-Day (2025), *Neural interactive proofs*, ICLR 2025 — prover-verifier line.
- Kirchner et al. (2024), *Prover-verifier games improve legibility of LLM outputs*, arXiv:2407.13692.
- Amit, Goldwasser, Paradise, Rothblum (2024), *Models that prove their own correctness*,
  arXiv:2405.15722.
- Kenton et al. (2024), *On scalable oversight with weak LLMs judging strong LLMs*, ICML.
- Khan et al. (2024), *Debating with more persuasive LLMs leads to more truthful answers*, ICML.
- Arnesen, Rein, Michael (2024), *Training language models to win debates with self-play improves
  judge accuracy*.
- Michael et al. (2023), *Debate helps supervise unreliable experts*, arXiv:2311.08702.


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
