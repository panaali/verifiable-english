# Answers that hold unless an exception applies (general defeasible consequence): buildable plan

> **DF-S (2026-10-14):** the statement spec [defeasible.md](defeasible.md) draft 1 elaborates every statement of
> section 3 against the build of `rd-9/integrate` (`fbb81599`) and computes every fixture of 4.1. It corrects 19
> statements and fixtures (its section 2). The largest correction: `basis_needs_sound` as written below is false
> without RD-9's `localFree` (fixture DF-σ). Where this plan and the spec differ, the spec's section 7 (Lean) and
> section 8 (fixtures) are authoritative. The design and decisions below are unchanged. Next: the statement review.
>
> Status: plan, **draft 2** (2026-10-14), branch `design/defeasible` from `main` at `f98183bf`. Draft 2 applies the
> converged plan debate (`manage-agents/debates/design-defeasible/`, rounds 1–3, verdict REVISE, candidate A kept: the
> joint position at the end of `fable.md` and Astra's round 3 in `astra.md`), and checks the plan against
> `manage-agents/debates/plan-synthesis/SYNTHESIS.md` and `DRI-DECISIONS-PHASE2.md` (section 11). Draft 1 was written
> from the brief (`manage-agents/prompts/research-wave/defeasible.txt`) and the research note
> [docs/research/defeasible.md](../research/defeasible.md), whose recommendation (candidate A) this plan builds. Inputs
> read: soft-norms.md, norms.md, norm-defaults.md, readings-defaults.md and its PLAN, the RD-9 spec and plan
> (`rd-9-soft-chain.md`, `rd-9-soft-chain-PLAN.md` on `rd-9/integrate`), weighing's research, PLAN (draft 5) and spec
> (draft 4) on `research/weighing-p1` at `8ed5f5cb`, the plan-synthesis files, the two pilot runs `20261012T1800Z`, and
> `lean/VE/{SoftNorms,NormDefaults,Readings}/*.lean` on `main` and on `rd-9/integrate`. Planning only: no code, proof,
> test or generated file changed, and no model was called. **The Lean statements below were not elaborated**: neither
> session ran `lake`. Every name they use was read in the sources named beside it; names on unmerged branches (RD-9,
> PK-1, WG-6) are taken from their reviewed specs and are interfaces until those land. Elaborating every statement is
> DF-S's first step. Fixture values marked *derived* were worked out by reading the sources and were not run.

## Change log

| Date | Draft | What |
|---|---|---|
| 2026-10-13 | 1 | Plan for candidate A of docs/research/defeasible.md: decisions D1 to D14; `Dflt_T`, the gate, the basis, four layered kinds; the meaning theorem; readings through RD-9's fold; defaults about facts; situations with observations on WG-6; Lean statements (not elaborated); fixtures DF-α to DF-ξ and P-1 to P-5; batches DF-0 to DF-7 with four pre-registered experiments; dependencies, shared files and merge order; shared pieces S1 to S11. Planning only. |
| 2026-10-14 | 2 | The debate's joint position, item by item. **(1) Default bases** minimise decisions with the unsaid tables varied (circumscription with varied predicates), in `DefaultBase` (3.4) and `DefaultCompletion` (3.6) alike, said in 0, 3.4, 3.6, 8 and S1 (new D15). Draft 1's two definitions of "no exception" (filling fixed in 3.4, varied in 3.6) are gone. **(2)** Draft 1's `hfill` (false whenever a default rule sits on a pair member) is replaced by the computed check `replacementSafe` and the replacement-admissibility lemma `replace_admissible` (3.4). **(3)** Astra's counterexample (one default obligation, its paired permission, both unspecified, fillings no/no) is fixture DF-π, and DF-π′ at one situation. **(4)** Fallback if DF-S cannot confirm the (→) proof: Astra's restriction, no minimality claim anywhere (3.4); no English or doc text claims minimality until DF-2 is proved (0, 2.9, DF-1a). **(5) DF-5** starts on WG-6's full bounded enumeration over every typed open atom, observations and constraints included, UNKNOWN beyond the bound; cone pruning only after `cone_minimal_iff` is proved (D10, 2.7, 3.6, DF-5). **(6) Basis** `strict \| needs \| unsettled`, `needs` only with a checked strict countermodel (`basis_needs_sound`); DE12 for `unsettled`; DF-E1's 12 default items all `needs` (D4, 2.2, 3.2, 3.3). **(7)** Non-vacuity conjunct in `defaults_certificate_sound` (3.3). **(8) DF-3** shows the default fold only when the strict fold is FREE; a default-fold CONFLICT renders as DE7 per choice; fixture DF-ρ with its English (2.4, 3.5, DF-3). **(9) English**: DE5 "whatever <deciders> decide" (DF-ζ gains a default rule so that a decider exists); DE8 in Astra's wording; DE1 and DE6 in a short and a long form chosen by Lean: short DE1 only when every kept assumption is a rule's exception with no stated condition (Astra's round-3 tightening: no switch, no ranking), short DE6 only when no exception holds at the situation; otherwise DE1′ and DE6′ (DE6′'s first sentence is Fable's round-1 long form), with DE11 naming each forced exception, shared with DE10 (D6, 2.8). DF-E1 measures both forms on all-`needs` items including DF-ε and DF-δ shapes, and drops the short form if it reads no better; draft 1's "By default" arm is dropped (D6, DF-E1). **(10)** Review checklist items 2, 5, 8, 10 and 12 extended (9). **(11)** Batch order as agreed (5, "Batch order"); DF-6 also waits for its own reviewed replacement argument. Also: DRI phase-2 decisions SC2, ET1 and ET2 applied to DF-4 and DF-E2; DF-3's pilot claim limited to the enumerated route; section 11 lists seven cross-plan issues. Planning only. |
| 2026-10-14 | 2 (status) | Status line only: DF-S's statement spec [defeasible.md](defeasible.md) draft 1 is written and supersedes section 3's statements and 4.1's *derived* values with elaborated and computed ones. The debate's edits above are unchanged. |

## 0. Summary

A default rule in VE ("Every assistant should share helpful information.") is a strict rule plus a named, open
exception that a named decider decides. Today nobody can ask what follows **when no exception applies**: the soft route
answers only what holds whatever the deciders find, so a default rule alone proves nothing about its act. This plan adds
that answer, as a distinct kind of answer with explicit premises, in five steps, each with one owner:

1. **The no-exception premises `Dflt_T`.** Lean generates one labelled premise per default rule ("its exception holds
   only where the text's own sufficient conditions say so"), per switch ("no one has turned it off") and per ranking
   decision ("the lower-ranked consideration does not outweigh the higher one"). A default answer is RD-9's checked
   entailment with `X ++ Dflt_T` for `X`, so every RD-9 soundness theorem applies unchanged.
2. **The gate and its conflicts.** Before answering, Lean checks that no two colliding default rules both apply when no
   exception applies (one certificate per colliding pair). Where they would, it shows the situation in English and
   gives no default verdict.
3. **The basis.** Every answer says whether it is strict, needs the no-exception premises (a checked strict
   countermodel shows it), or was not checked without them, and lists the premises its certificate used. Lean computes
   all of it; `strict` and `needs` are theorems. The English of a default answer begins "Unless an exception applies,
   …" only where that is exactly true (every premise it rests on is a rule's exception with no stated condition), and
   "Under the assumptions listed below, …" otherwise.
4. **The meaning.** Under the gate and a computed check on the other premises, entailment from `X ++ Dflt_T` equals
   truth in every situation whose open decisions are minimal, the unsaid tables of norm-defaults being free to vary
   while the facts stay fixed (McCarthy's circumscription of the decisions with the unsaid predicates varied, reduced
   to completion, Reiter 1982 and Lifschitz 1985). One theorem, DF-2. Until it is proved, no English or doc text claims
   minimality; if DF-S cannot confirm its proof, answers stay explicitly conditional on `Dflt_T` and nothing claims
   minimality.
5. **Further uses.** Across readings through RD-9's generic fold; a wording for default rules about facts; at one
   situation with observed outcomes, on weighing's zone machinery; weighing's override conditions; question
   answering.

The smallest change that moves a pilot number is DF-1a with DF-1b (Lean, then its relay): the three constitution
"should" sets' default readings, as standalone documents, go from no answer to "unless an exception applies, the
conclusion follows" (0 of 3 to 3 of 3, *derived*). The byte gain of the whole plan is small and comes from DF-4 alone:
98 to 572 B on the constitution (*estimate*), 0 on the UDHR (research note 2.3, 5.1).

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | A default answer is a **distinct kind** whose extra premises (`Dflt_T`) are generated by Lean and named in the answer. No new consequence relation, no new inference rule | VISION's converged rule, item 5: "Non-monotone systems enter only as sealed content whose conclusions are computed under a distinct kind and used as conditional premises"; item 8: conditional consequences of open adjudication may be checked; weighing D13 ("no default inference inside the checker") | a defeasible-logic or answer-set engine (research 4.2); rational closure (4.3) |
| D2 | `Dflt_T` says: (a) a default rule's exception holds only where one of its **stated sufficient conditions** holds; (b) no switch is on; (c) no `outweighs` finding holds. Necessary conditions add nothing (an exception that does not hold meets them) | (a) respects the text's own exceptions instead of contradicting them (weighing's all-false record is "ruled out" where a sufficient condition holds); (b) a switch records an instruction, and the constitution's default behaviours are exactly "what Claude does absent instructions" (u0153.s02); (c) the holistic ranking reads "higher-priority considerations should generally dominate" (u0016.s02) | leaving switches open (every alterable rule would answer "left to the operator"); minimising only exceptions |
| D3 | The **gate** is no-exception coherence: every colliding pair's coherence premise follows from `Exc_T ++ R ++ Dflt_T` on the base (one tableau certificate per pair). `Coh_T` stays in `X` for the answer itself | `ConflictFreeX U (X ++ Dflt_T)` would be vacuous: a base where two defaults collide fails `Coh_T` and drops out. Dropping `Coh_T` from `X` would change existing answers. The per-pair check is soft's DISJOINT classification with `Dflt_T` added | a global conflict check with `Dflt_T`; no gate (default answers vacuous at collisions) |
| D4 | The **basis** is Lean's and three-valued: `strict` when the certificate still checks with every `Dflt_T` premise read as `⊤` (readings' merged `usedLabels`); otherwise `needs` when a strict countermodel sent with the request checks (RD-9's `modelCheckX` on the document's own `X`), and `unsettled` when none does; with the labels the certificate used. `basis_strict_sound` and `basis_needs_sound` make `strict` and `needs` theorems | "never present a default conclusion as a strict one" (brief) needs a proof, not a convention; `usedLabels` works greedily over one certificate, so a kept label shows that this certificate used the premise, not that the conclusion needs it; verdicts are three-valued (CLAUDE.md); one owner (Lean) | a two-valued `strict \| default` (draft 1); Python comparing a strict and a default answer |
| D5 | Over all situations, a question that assumes no exception **states facts only**: its premises name no regulated and no decision predicate. Observed outcomes go to DF-5, at one situation | with an observed outcome the minimal situation need not be unique, and over all situations deciding it is Π2^p-hard propositionally (Eiter and Gottlob 1993); at one finite situation it is a bounded enumeration | answering such questions with `Dflt_T` (a stated exception would make the answer vacuous) |
| D6 | The reader-facing marker has **two forms, and Lean chooses**. The short form "Unless an exception applies, …" (DE1) only when every kept assumption is a rule's exception with no stated sufficient condition; "Even if no exception applies, …" (DE6) only when no exception holds at the situation shown. Otherwise the long forms "Under the assumptions listed below, …" (DE1′) and "Even if no exception applies beyond those the text states, …" (DE6′, with DE11 naming each exception that holds there). One plain sentence per assumption. DF-E1 measures both forms; if the short form reads no better, it is dropped and Lean always prints the long form | the short form is exactly true only in that case: a switch (DF-ε), a ranking (DF-δ) or a stated condition (DF-β) is an assumption it does not state, and at DF-β (i)'s situation the text's own exception applies; W1 already uses "By default, a <noun> may <act>." for the completion legend, and one phrase must not carry two meanings | one marker for every answer (draft 1; false at DF-β (i)); "By default, …"; symbols, labels, or decision names in the text |
| D7 | **No new profile** for DF-1 to DF-3 and DF-5 to DF-7: they add kinds and answers only; no existing route, answer, identity, certificate or theorem statement changes (meaning freeze, converged rule item 2). DF-4 adds English for a wire form that already exists (a soft default rule on a plain predicate); the plan proposes no profile, and DF-S's review may require `defaults@0`, which would then be one AR-10 row | the wire meaning is merged; only previously refused English becomes accepted | a `defaults@0` profile for answer kinds |
| D8 | **Specificity is never applied automatically.** A "more specific than" check (guard entailment) may become an IDE suggestion, only if DF-E3's bar is met | u0100.s04 ranks the more specific guidelines below safety and ethics because they are more specific; lex superior beats lex specialis; a derived priority is an interpretive choice | rational closure, System Z, inheritance-network specificity |
| D9 | Across readings, the fold is **RD-9's `foldG`** over a new per-choice semantics `dSem` | one owner of the fold; the fold theorems hold for any `ChoiceSem` | a second fold |
| D10 | At one situation, the minimal completions are a filter over **weighing's bounded enumeration** (WG-6, in `NormDefaults/Evidence.lean` and `Weighing/Zone.lean`) over **every typed open atom** of the situation (decision and unsaid atoms), with the observations and every premise of X checked on each full assignment, and UNKNOWN beyond the bound. Cone pruning replaces it only after `cone_minimal_iff` (3.6) is proved. Weighing's record "assuming no exception applies" is DF-5's instance when no sufficient condition holds and nothing is observed (`defaultZone_eq_noException`) | SYNTHESIS O18: one three-valued evaluator; one sentence and one meaning for "no exception" (shared piece S1); WG-6's cone answers ordinary consequence, and filtering it for global minimality needs its own proof (an observation or a premise may tie a cone atom to atoms outside it; debate) | a second enumerator in `Defaults/`; cone pruning before its lemma |
| D11 | `weighing@0` documents are **refused** by the default kinds until DF-6 adds weighing's sufficient override conditions to `Dflt_T` | `Dflt_T`'s "no override" would contradict a stated sufficient override condition and silently exclude the situations where it holds | answering weighing documents with soft's `Dflt_T` |
| D12 | **One owner per piece of logic.** Lean generates `Dflt_T`, the coherence targets, the gate, the basis, the assumptions and the choice of English rows. Python relays (schema and binding, R8) and renders; it reads `Dflt_T` only from Lean's `defaults-elaborate` answer. The relay lint forbids `default:` label literals in Python, as RD-9 forbids `soft__` and `unsaid__` | CLAUDE.md, lead directive | a Python `Dflt_T` for the search |
| D13 | Frequency words ("normally", "typically", "usually", "generally", "in most cases", "as a rule") on a **plain** predicate are a reading set {default rule about a fact, frequency claim}. The default candidate is DF-4's wording; the frequency candidate is quantities' (QT-A6) and may stay pending (W2) until it lands. The row lives in english-lean's catalogue | soft 2.2 already decides this for deontic predicates; SYNTHESIS O15: the catalogue owns reading sets for source words; generics are neither "most" nor "all" (research 3.3) | choosing one reading |
| D14 | "…, unless there is good reason not to." on a default rule is input for the rule's own exception, with the phrase kept as a factor ("The exception to rule n takes account of whether there is good reason not to <act>."). One reading | the rule's exception is exactly "there is good reason not to"; a carve-out over an open term would differ only in that answers assuming no exception would leave it open, and the source sentence is about the exception | an open-term carve-out reading |
| D15 | **A default base minimises the decisions while the unsaid tables vary**: circumscription of the decision predicates with norm-defaults' unsaid predicates varied, and the facts, domain and constants fixed. One definition for the meaning theorem (`DefaultBase`, 3.4) and for situations (`DefaultCompletion`, 3.6). Whether the theorem's (→) direction applies to a document is a computed check (`replacementSafe`): the other packs' premises and the base background name no decision and no pair member's unsaid predicate | it is what Lean computes: `EntailsX` with `Dflt_T` ranges over every filling that satisfies `Fill_T`; `Fill_T` is built from substituted outcomes of author rules, and a default rule's outcome carries `¬excepted`, so with the filling fixed an excepted base can be minimal while `Dflt_T` entails the obligation (DF-π, Astra's counterexample); a fixed filling would also make DF-5 report DF-π's obligation as left open | fixed fillings in both (true only under a preservation property, false for one default obligation with an unspecified paired permission); fixed in 3.4 and varied in 3.6 (draft 1: two meanings of "no exception") |

## 2. Design

### 2.1 The no-exception premises `Dflt_T`

Regenerated from the decoded soft document at every trusted site, never read from the wire:

```text
for each default rule N, with stated sufficient conditions C₁ … C_k (k ≥ 0):
    ∀x̄. excepted_N(x̄) → (C₁(x̄) ∨ … ∨ C_k(x̄))          label default:exception:<N>    (k = 0: ∀x̄. ¬excepted_N(x̄))
for each rule N and each party π that may turn it off:
    ∀x̄. ¬off_{N,π}(x̄)                                    label default:switch:<N>:<π>
for each outweighs decision (a, L, H) (holistic flag only):
    ∀x̄. ¬outweighs_{a,L,H}(x̄)                             label default:ranking:<L>:<H>:<a>
```

The `C_i` are soft's exception conditions: quantifier-free, over base predicates of `E` only (soft 3.2, 6.1). So each
premise is in soft's universal, function-free fragment, typed over the filled base vocabulary. With `Exc_T` (whose
sufficient premises say `C_i → excepted_N`), `Dflt_T` makes `excepted_N` exactly the disjunction of the stated
conditions: the least exception table the text forces.

### 2.2 The answer kinds (layered route, rows of PK-1's kind table)

| Kind | Request | Answer | Evidence and theorem |
|---|---|---|---|
| `defaults-elaborate` | the layered source | `default_premises` (label, AST), `coherence_targets` (the two rule names, AST) | regenerated; `dflt_wellFormed` |
| `defaults-coherence` | the source; per colliding pair an optional certificate, or a `witness` (a finite base and filling, with the pair and tuple) | `verdict` COHERENT, COLLISION or UNKNOWN; `pairs` (rules, status resolved / collision / unknown); on COLLISION the situation, with the effects of both rules | `defaultCoherenceCheck_sound`; `collision_sound` |
| `defaults-certificate` | the source, `premises` (facts only, D5), `conclusion`, a `certificate`, the pairs' certificates, a finite `model` of the premises with no exception, and optionally a `strict_model` (a finite model and filling of the document's own premises, without `Dflt_T`, where the conclusion fails) | `verdict` FOLLOWS or UNKNOWN; with FOLLOWS, `basis` (strict, needs, unsettled), `form` (short, long) and `assumptions`; with UNKNOWN, `reason` | `defaults_certificate_sound` (`acceptanceX` with `X ++ Dflt_T`, `assumptions_sound`, the non-vacuity conjunct, `basis_strict_sound`, `basis_needs_sound`); `followsForm_short` |
| `defaults-model` | the source, `premises`, `conclusion`, a finite `model` and `filling` | `verdict` DOES-NOT-FOLLOW or UNKNOWN; the situation and its gaps; `forced` (each exception that holds at the situation, with the stated condition that forces it) | `defaults_model_sound` (`modelCheckX_sound` with `X ++ Dflt_T`, and `forced = []` means no exception holds there); after DF-2 the situation is a default base (`defaultBase_of_dflt`) |

FOLLOWS needs all three: the certificate checks against `premisesX U (X ++ Dflt_T) Γ` (bound by `bindCertX`), the gate's
certificates all check, and the model checks with `modelCheckX U (X ++ Dflt_T)`. Missing any, the answer is UNKNOWN
with its reason (2.6). The model is required so that a default answer is never vacuous: with `Dflt_T` added, the
premises could hold in no situation; the non-vacuity conjunct of `defaults_certificate_sound` states what the checked
model gives. The basis is `needs` only when the `strict_model` checks with `modelCheckX U X` (no `Dflt_T`), so that the
conclusion is shown not to follow from the document's own premises; with no strict model, or one that does not check,
the basis is `unsettled`, never `needs`. A countermodel needs no gate: a base satisfying `X ++ Dflt_T` is a default base
whatever the other bases do (`defaultBase_of_dflt`, DF-2).

Search is untrusted: Python's generic prover and model search, fed with Lean's `defaults-elaborate` output, propose
certificates, models and witnesses; Lean checks every one.

### 2.3 The gate and what a reader sees when it fails

A colliding pair (soft's `CP(T)`) is **resolved** when its coherence premise follows from the base background,
`Exc_T`, the other packs' premises `R`, `Dflt_T` and `Fill_T`. Ranked pairs are resolved under either flag (a ranked
pair's coherence premise is valid on `T′`, soft's `coh_rank_valid_unconditional`; DF-S confirms it on `fill U`, and the
search is expected to find its certificate quickly, *estimate*); unranked pairs are resolved where the rules' guards,
carve-outs or stated exception conditions keep them apart. A **collision** is a checked finite base
where, with `Dflt_T`, both rules of a pair select: the situation in which, with no exception, the text asks for both.
The English (2.8, DE7) names the two rules, their effects, the absence of a ranking, and the decider.

### 2.4 Readings (DF-3)

For each compatible choice `c`, `dSem` reads entailment, countermodels and consistency with
`choiceX N c ++ Dflt_T(c)`, and conflict freedom as RD-9's strict conflict freedom together with the gate on the
choice's soft document. RD-9's `foldG_*` theorems then give ALL, SOME and NONE "unless an exception applies", gated on
CONFLICT-FREE exactly as RD-9's fold is. The answer reports the strict fold first; when it is not ALL, it adds the
default fold with its basis and, per choice, the assumptions used.

The default fold is shown **only when the strict conflict fold is FREE**. `dSem.notFree c` is "strict conflict, or the
gate fails", and RD-9's `HoldsG .conflict` reads `notFree` alone, so without this rule a choice where the text only
leaves a collision open would get RD-9's contradiction wording. With it, a default-fold CONFLICT can only come from the
gate, and it renders as DE7 for each choice whose gate fails ("Under <reading>: Rules <m> and <n> conflict here unless
one of them gives way: …"). Where the strict fold is not FREE, RD-9's answer stands alone. Fixture DF-ρ.

### 2.5 Defaults about facts (DF-4)

A default rule on a plain regulated predicate (merged semantics, refused English today:
`ve/norm_english.py:397-398`) gets one wording:

```text
Rule n. Every <noun> <verbalisation>, unless an exception applies.
The exception to rule n is decided by <decider>.            (soft's existing decider sentence)
```

Paraphrase (IDE): "Each <noun> <verbalisation>, except where rule n's exception applies; <decider> decides where it
applies." The completion of the predicate is whatever its declaration says (`unspecified` under `norm-defaults@0`, so
cases no rule decides stay "the text does not say"). In translation, D13's reading set applies to frequency words with a
plain predicate. The refusal "A default rule needs a declared obligation or permission act" is deleted, not kept
beside the new row.

### 2.6 Diagnostics and statuses

| # | Text | When |
|---|---|---|
| 1 | `UnsupportedProfile: answers that assume no exception are not available with weighing@0 yet` | the source's profiles contain `weighing@0` (until DF-6) |
| 2 | `InvalidInput: answers that assume no exception need premises that name no decision: <label>` | a premise of `X` outside the soft pack names a decision predicate (computed check `decisionFree`; no pack does today) |
| 3 | `InvalidInput: a question that assumes no exception may state facts only; it states <what>` with `<what>` one of `what rule <n> decides`, `whether rule <n>'s exception applies`, `whether <party> has turned rule <n> off`, `whether <rank l> outweighs <rank h> on <act phrase>` | a premise of the question names a regulated or decision predicate (D5) |
| 4 | `ResourceLimit: generated default premise <label>` | a `Dflt_T` premise over `MAX_DEPTH` or `MAX_NODES`, computed before it is built |
| 5 | `InvalidInput: coherence certificates do not match the colliding pairs` | the request's pair list differs in length or order from `coherence_targets` |

Statuses, not errors: `UNKNOWN (with no exception, rules <m> and <n> conflict)`, `UNKNOWN (no-exception coherence
not checked)`, `UNKNOWN (no checked situation where the premises hold with no exception)`, `UNKNOWN (no certificate)`.

### 2.7 At one situation, with observations (DF-5)

At a finite situation `M`, with weighing's record (fixed decision atoms) and a list of **observed outcomes** (a
regulated atom and its value), the **default completions** are the admissible completions (weighing's
`AdmissibleCompletion` over PK-1's whole assembled X and `Fill_T`, switches off unless the record says otherwise) that
agree with the observations and are minimal in their decision atoms. The completions compared range over every
admissible completion, so their unsaid tables vary; only the decision atoms are compared, and the facts and the domain
are `M`'s (D15, the same definition as `DefaultBase`). The answer: `by default <value>` (every default completion
agrees, and one exists), `by default left to <decider>` (two default completions with the same filling differ), `by
default not said` (they differ only in the filling), `no completion` (the record or the observations are ruled out, with
Lean's labels), or `unknown` with weighing's reasons.

Enumeration (D10): every assignment of **every typed open atom** of `M` not fixed by the record (decision atoms and
unsaid atoms), not only the query's cone, each checked against X, `Fill_T` and the observations by evaluation on the
finite situation, then the minimality filter over the survivors' decision parts. Budget: at most 12 such atoms
(`maxDefaultAtoms`, at most 4,096 assignments); beyond it, `unknown (budget)`. Cone pruning, with weighing's 16-atom
cone budget, is enabled only after `cone_minimal_iff` is proved; a cone that merely contains the observations' atoms
is not enough. With `events@0` on, a `leftTo` or `notSaid` witness also needs events' completion-preservation theorem,
otherwise `unknown` (weighing edit 6).

### 2.8 The English (one reading each; Lean selects the rows, Python renders them)

| # | Wording | The one reading | When |
|---|---|---|---|
| DE1 | `Unless an exception applies, the conclusion follows: <conclusion>.` | In every situation the rules allow where the exception of no listed rule applies, the conclusion holds | FOLLOWS, basis `needs` or `unsettled`, `form` short: every kept assumption is a rule's exception with no stated sufficient condition (`followsForm`) |
| DE1′ | `Under the assumptions listed below, the conclusion follows: <conclusion>.` | In every situation the rules allow where every listed assumption holds (an exception only where the text's own conditions say, no switch on, the ranking kept), the conclusion holds | FOLLOWS, basis `needs` or `unsettled`, `form` long: some kept assumption is a switch, a ranking, or an exception with stated conditions |
| DE2 | `This assumes that the exception to rule <n> does not apply. <Decider> decides where it applies; the text names no case.` | the assumption `default:exception:<n>` with no stated condition | per used assumption |
| DE2′ | `This assumes that the exception to rule <n> applies only where the text says it does: <condition>[, or <condition>]*. <Decider> decides any other case.` | the same assumption with stated sufficient conditions | per used assumption |
| DE3 | `This assumes that <party> has not turned rule <n> off.` | `default:switch:<n>:<party>` | per used assumption |
| DE4 | `This assumes that, on <act phrase>, the <rank l> consideration does not outweigh the <rank h> consideration. <Decider> decides where it does.` | `default:ranking:<l>:<h>:<act>` | per used assumption |
| DE5 | `This holds whatever <deciders> decide.` (`decides` with one decider) | basis strict: the conclusion follows from the document's own premises, whatever any exception, switch or ranking decision is | FOLLOWS, basis strict, asked with no exception assumed, `Dflt_T` not empty; `<deciders>` are the deciders of `Dflt_T`'s premises, each once, in rule order, in soft's decider phrases. With `Dflt_T` empty the question is the strict one (F-DF1) and DE5 is not shown |
| DE6 | `Even if no exception applies, the conclusion does not follow. It fails here: <situation>.` | a default base where the conclusion fails and no rule's exception holds | DOES-NOT-FOLLOW, `forced` empty; followed by norm-defaults' gap sentences where the text is silent |
| DE6′ | `Even if no exception applies beyond those the text states, the conclusion does not follow. It fails here: <situation>.` followed by one DE11 per entry of `forced` | a default base where the conclusion fails; every exception that holds there is one the text's own conditions force | DOES-NOT-FOLLOW, `forced` not empty; then the gap sentences as DE6 |
| DE7 | `Rules <m> and <n> conflict here unless one of them gives way: <effect of m>, and <effect of n>. The text ranks neither above the other, and names no exception that applies here. Which rule gives way is left to <decider>.` | a checked collision with no exception | COLLISION, the gated UNKNOWN of a question, and in DF-3, prefixed `Under <reading>:`, each choice whose gate fails when the strict fold is FREE (2.4) |
| DE8 | `Under every reading, the conclusion follows under the assumptions listed for that reading.` followed, for each reading whose basis is not strict, by the reading and its DE2 to DE4 sentences | the default fold is ALL; each reading's conclusion follows from its own premises with its listed assumptions | DF-3, the default fold ALL and some choice's basis not strict |
| DE9 | `Rule n. Every <noun> <verbalisation>, unless an exception applies.` | 2.5 | DF-4, authoring and rendering |
| DE10 | `Even with no exceptions beyond those the facts here force, the answer depends on which rule gives way: <two completions>.` / `With no exceptions beyond those the facts here force, <result>.` followed by one DE11 per exception a stated condition forces, and `The facts here force <exception>.` per exception only the observations force | 2.7 | DF-5 |
| DE11 | `The text's own exception to rule <n> applies here: <condition>.` | at the situation shown, `<condition>`, a stated sufficient condition of rule n's exception, holds, so `Exc_T` forces the exception | after DE6′ and DE10, once per exception a stated condition forces (Lean lists them); one sentence for both |
| DE12 | `Whether it also holds without these assumptions was not checked.` | basis `unsettled`: no strict countermodel was checked, so the conclusion may or may not follow from the document's own premises | FOLLOWS, basis `unsettled`, after DE1 or DE1′ and the assumption sentences |

Non-wordings: any `default:`, `soft__` or `unsaid__` name; "by default" for these answers (D6); "unless an exception
applies" where a kept assumption is a switch, a ranking or an exception with stated conditions; "even if no exception
applies" where an exception holds at the situation shown; a label, a formula or a decision name. Every row goes
through W7's all-derivations gate before it is shown; DE9 is the only one an author writes. Lean selects every row
(`basis`, `form`, `forced`); Python renders the row it is given and never chooses between DE1 and DE1′ or DE6 and DE6′.

### 2.9 Not claimed

- No claim that an exception does not apply in fact. A default answer says what holds if none applies.
- No answer over all situations to a question that states an outcome a rule decides (D5); DF-E4 is research.
- No automatic priority by specificity, recency or authority (D8).
- No byte figure for DF-1 to DF-3 or DF-5 to DF-7: they change answers, not coverage.
- No minimality of the listed assumptions: `assumptions` is a set sufficient for the certificate checked, as readings'
  conditions are (`usedLabels`); a different certificate may need fewer.
- No claim that the conclusion needs its assumptions unless the basis is `needs` (a checked strict countermodel). With
  `unsettled`, DE12 says that this was not checked.
- Under the gate and `replacementSafe` only: the minimality theorem, and only once DF-2 has proved it. Until then, and
  for every document that fails the check, answers are conditional on `Dflt_T` and no English, `lean/DEFAULTS.md` or
  doc text says that the situations they range over are those with the fewest decisions. Where the gate fails, the
  answer is UNKNOWN with DE7, never a choice of which rule gives way.

## 3. Lean statements

### 3.1 Files

| Batch | File | Declarations |
|---|---|---|
| DF-1a | `lean/VE/Defaults/Premises.lean` (new) | 3.2 |
| DF-1a | `lean/VE/Defaults/Wire.lean` (new), `lean/VE/Defaults/Examples.lean` (new, `#guard`s) | 3.3 |
| DF-1a | `lean/ResponseShape/Schemas/NormDefaults.lean`, `lean/ResponseShape/Encoders/NormDefaults.lean` (four rows, four encoder theorems) | 2.2 |
| DF-2 | `lean/VE/Defaults/Meaning.lean` (new) | 3.4 |
| DF-3 | `lean/VE/Readings/DefaultVerdicts.lean` (new) | 3.5 |
| DF-5 | `lean/VE/Defaults/Zone.lean` (new), `ZoneExamples.lean` (new) | 3.6 |
| DF-6 | `lean/VE/Defaults/Premises.lean`, `Meaning.lean` (own files) | 3.7 |
| all | `lean/DEFAULTS.md` (new): every definition and theorem in plain words | — |

Each block below is meant to elaborate inside one namespace with these `open`s:

```lean
namespace VE.Defaults
open VE.Norms (bindAll atom anyF preds Sat DocumentExpansion restrictAll envAt)
open VE.SoftNorms (SoftDoc SoftNode exceptedF outweighsF offName sortsOf actSortsOf outweighsTriples
  decisionNames offDecisions collidingPairs excPremises soften WellFormedSoft)
open VE.NormDefaults (UDoc fill fillPremises WellFormedU EntailsX modelCheckX)
open VE.NormDefaults.Wire (BaseAdmissibleX cohPremiseU softLabelledU premisesX LayeredU)
universe u
```

Sources of the names: `bindAll`, `atom`, `anyF` (`lean/VE/Norms/Basic.lean:18-31`); `preds` (`Norms/Tree.lean:143`);
`exceptedF`, `outweighsF`, `excPremises`, `soften` (`SoftNorms/Soften.lean:64-157`); `offName`, `outweighsTriples`,
`decisionNames`, `offDecisions`, `collidingPairs` (`SoftNorms/Tree.lean:242-295`); `BaseAdmissibleX`
(`NormDefaults/Report.lean:201`); `EntailsX` (`NormDefaults/LayeredEntail.lean:14`, `rd-9/integrate`); `cohPremiseU`,
`softLabelledU`, `LayeredU` (`NormDefaults/Layered.lean:45-72`, `rd-9/integrate`); `premisesX`, `modelCheckX`,
`acceptanceX`, `modelCheckX_sound`, `bindCertX` (rd-9-soft-chain.md 6, `Wire.` prefix as there); `usedLabels`, `blank`
(`Readings/Verdicts.lean:650-664`).

### 3.2 DF-1a: the premises, the gate and the basis (`Defaults/Premises.lean`)

```lean
/-- The no-exception premises of one rule: its exception holds only where one of its stated sufficient conditions
    holds, and none of its switches is on. -/
def dfltOf (D : SoftDoc) (N : SoftNode) : List (String × VE.Formula) :=
  (match N.mode, N.exception with
   | .default, some e =>
       [("default:exception:" ++ N.name,
         bindAll (sortsOf D N.pred) (.implies (exceptedF D N) (anyF e.sufficient)))]
   | _, _ => []) ++
  N.alterable.map (fun π =>
    ("default:switch:" ++ N.name ++ ":" ++ π,
     bindAll (sortsOf D N.pred) (.not (atom (offName N π) (sortsOf D N.pred)))))

/-- `Dflt_T`: the rules' premises in rule order, then one per `outweighs` decision, in soft's triple order. -/
def dfltLabelled (D : SoftDoc) : List (String × VE.Formula) :=
  D.T.nodes.flatMap (dfltOf D) ++
  (outweighsTriples D).map (fun (a, L, H) =>
    ("default:ranking:" ++ L ++ ":" ++ H ++ ":" ++ a, bindAll (actSortsOf D a) (.not (outweighsF D a L H))))

def dfltPremises (D : SoftDoc) : List VE.Formula := (dfltLabelled D).map (·.2)
def dfltLabels (D : SoftDoc) : List String := (dfltLabelled D).map (·.1)

/-- The premises of a default answer: the document's own `X` (PK-1's assembled X), then `Dflt_T`. -/
def defaultX (D : SoftDoc) (X : List VE.Formula) : List VE.Formula := X ++ dfltPremises D

/-- `Dflt_T` read as `⊤`. -/
def withoutDefaults (D : SoftDoc) (X : List VE.Formula) : List VE.Formula :=
  X ++ (dfltPremises D).map (fun _ => VE.Formula.top)

/-- Names no decision predicate of `D`. -/
def decisionFree (D : SoftDoc) (φ : VE.Formula) : Bool :=
  (preds φ).all (fun p => !(decisionNames D).contains p)

/-- PK-1's provider obligation 2. `L.U.D = soften L.D` holds on both layered branches (`decodeSoftU`,
    `decodeRightsU`). -/
theorem dflt_wellFormed (U : UDoc) (D : SoftDoc) (hU : U.D = soften D) (hD : WellFormedSoft D = true) :
    ∀ a ∈ dfltPremises D, a.WellFormed (envAt (fill U) 0) []

/-- More premises (or `⊤`) never lose an entailment. -/
theorem entailsX_mono (U : UDoc) (X₁ X₂ Γ : List VE.Formula) (φ : VE.Formula)
    (h : ∀ a ∈ X₁, a = .top ∨ a ∈ X₂) : EntailsX.{u} U X₁ Γ φ → EntailsX.{u} U X₂ Γ φ

/-- A conclusion that follows with every `Dflt_T` premise read as `⊤` follows from the document's own premises. -/
theorem strict_of_withoutDefaults (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) (φ : VE.Formula)
    (h : EntailsX.{u} U (withoutDefaults D X) Γ φ) : EntailsX.{u} U X Γ φ

/-- The gate: on every base admissible with the exception premises, the other packs' premises `R` and `Dflt_T`, no
    colliding pair of default rules both selects. -/
def DefaultCoherent (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (excPremises D ++ R ++ dfltPremises D) B →
    ∀ M N, (M, N) ∈ collidingPairs D → (cohPremiseU U D M N).denote B []

/-- One certificate per colliding pair, in `collidingPairs` order, each for the pair's `cohPremiseU` from
    `backgroundBase (fill U) ++ excPremises D ++ R ++ dfltPremises D ++ fillPremises U` (the list
    `conflictFreeCheckX` checks its targets against, with `excPremises D ++ R ++ dfltPremises D` for `X`). Body: the
    tableau check of each certificate, as `Wire.conflictFreeCheckX`. -/
def defaultCoherenceCheck (U : UDoc) (D : SoftDoc) (R : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) : Bool

theorem defaultCoherenceCheck_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (R : List VE.Formula) (hR : ∀ a ∈ R, a.WellFormed (envAt (fill U) 0) [])
    (certs : List (Option VE.Tableau.Certificate)) (hc : defaultCoherenceCheck U D R certs = true) :
    DefaultCoherent.{u} U D R

/-- A checked collision: the finite base and filling satisfy `Exc_T ++ R ++ Dflt_T` and `Fill_T` (`extraValid`), and
    both rules named select at the tuple. -/
def collisionCheck (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String) (vs : List VE.Bridge.Entity) : Bool

theorem collision_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity) (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity)
    (m n : String) (vs : List VE.Bridge.Entity) (hc : collisionCheck U D R M F m n vs = true) :
    ¬ DefaultCoherent.{0} U D R

/-- The certificate check the answer kinds use (`checkCertificate` over a premise list, as RD-9's kinds). -/
def certChecks (ps : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate) : Bool

/-- The `Dflt_T` labels a certificate needs: readings' merged `usedLabels` over `Dflt_T`, with
    `premisesX U (defaultX D X) Γ = background (fill U) ++ X ++ Dflt_T ++ (fillPremises U ++ elaborate (fill U).T ++ Γ)`
    split around `Dflt_T`. The list is sufficient for this certificate; it is not claimed minimal. -/
def assumptionsOf (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) : List String :=
  VE.Readings.usedLabels (fun ps => certChecks ps φ c)
    (VE.Norms.background (fill U) ++ X) (dfltLabelled D)
    (fillPremises U ++ VE.Norms.elaborate (fill U).T ++ Γ)

theorem assumptions_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (X Γ : List VE.Formula) (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) (hc : certChecks (premisesX U (defaultX D X) Γ) φ c = true) :
    EntailsX.{u} U (X ++ VE.Readings.blank (dfltLabelled D) (assumptionsOf U D X Γ φ c)) Γ φ

/-- `strict`: no `Dflt_T` label kept. `needs`: labels kept, and a strict countermodel checked. `unsettled`: labels kept,
    and no strict countermodel checked. -/
inductive Basis | strict | needs | unsettled
  deriving DecidableEq, Repr

def basisOf (as : List String) (strictCounter : Bool) : Basis :=
  if as.isEmpty then .strict else if strictCounter then .needs else .unsettled

/-- `basis = strict` is sound: the conclusion follows from the document's own premises. -/
theorem basis_strict_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (X Γ : List VE.Formula) (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) (hc : certChecks (premisesX U (defaultX D X) Γ) φ c = true) (sc : Bool)
    (hb : basisOf (assumptionsOf U D X Γ φ c) sc = .strict) :
    EntailsX.{u} U X Γ φ

/-- `basis = needs` is sound: a strict countermodel, checked by RD-9's `modelCheckX` with the document's own `X` and no
    `Dflt_T`, shows that the conclusion does not follow without the assumptions. -/
theorem basis_needs_sound (U : UDoc) (h : WellFormedU U = true) (X Γ : List VE.Formula)
    (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity)
    (hm : (modelCheckX U X M F Γ φ).1 = true ∧ (modelCheckX U X M F Γ φ).2 = false) :
    ¬ EntailsX.{0} U X Γ φ

/-- Which form of DE1 Lean selects. -/
inductive Form | short | long
  deriving DecidableEq, Repr

/-- The labels whose premise says only "rule n's exception does not apply": a default rule's exception premise with
    no stated sufficient condition (2.1, `k = 0`). -/
def bareExceptionLabels (D : SoftDoc) : List String :=
  D.T.nodes.filterMap (fun N => match N.mode, N.exception with
    | .default, some e => if e.sufficient.isEmpty then some ("default:exception:" ++ N.name) else none
    | _, _ => none)

/-- DE1's short form only when every kept assumption is a bare exception: no switch, no ranking, no stated
    condition. -/
def followsForm (D : SoftDoc) (as : List String) : Form :=
  if as.all (fun l => (bareExceptionLabels D).contains l) then .short else .long

/-- DE1's short form says no more than the kept premises: each is "rule n's exception holds nowhere". -/
theorem followsForm_short (D : SoftDoc) (as : List String) (h : followsForm D as = .short) :
    ∀ l ∈ as, ∃ N ∈ D.T.nodes, l = "default:exception:" ++ N.name ∧
      (l, bindAll (sortsOf D N.pred) (.implies (exceptedF D N) (anyF []))) ∈ dfltLabelled D
```

Proof notes. `entailsX_mono`: `BaseAdmissibleX U X₂ B` gives `Sat B X₁` premise by premise. `strict_of_withoutDefaults`
is `entailsX_mono` with every element of `withoutDefaults` either `⊤` or in `X`. `assumptions_sound` is
`usedLabels_sound` followed by RD-9's `acceptanceX` on the list with the dropped premises read as `⊤` (well formed
because `⊤` is); `dfltLabelled D` is passed as a `VE.Compose.Labelled`, and `usedLabels_sound`'s hypothesis
`wellLabelled` is a lemma of this batch (`dfltLabelled_wellLabelled`: rule names are distinct, a rule's parties are
distinct, `outweighsTriples` is deduplicated, and the three prefixes differ). `basis_strict_sound`: with no label kept, `blank` reads all of `Dflt_T` as `⊤` (`blank_all`'s dual),
which is `withoutDefaults`. `basis_needs_sound` is `modelCheckX_sound` at `X`: its structure satisfies every hypothesis
of `EntailsX.{0} U X Γ φ` and falsifies `φ` (universe 0, as RD-9's witnesses). `followsForm_short` unfolds
`bareExceptionLabels` and `dfltOf` at `k = 0`. `defaultCoherenceCheck_sound` is the tableau's soundness on base
structures, as in `Wire.conflictFreeCheckX_sound`. `collision_sound` evaluates `cohPremiseU` on the checked finite base;
universe 0 as `Layered.lean`'s witnesses.

### 3.3 DF-1a: the wire (`Defaults/Wire.lean`)

```lean
namespace VE.Defaults.Wire

/-- What a `defaults-*` case reads from a decoded layered document: `R` is `X` after the soft pack (PK-1). -/
structure DefaultsView where
  L : LayeredU
  R : List VE.Formula
  hX : L.X = (softLabelledU L.U L.D).map (·.2) ++ R
  hR : R.all (decisionFree L.D) = true

/-- Diagnostics 1 and 2 of 2.6, in that order. -/
def viewOf (L : LayeredU) : Except String DefaultsView

/-- The `defaults-*` kinds of 2.2; `none` for any other kind. Called from PK-1's kind table. -/
def defaultsCase (L : LayeredU) (id kind : String) (j : Json) : Except String (Option Json)

structure CertReplay where
  v : DefaultsView
  Γ : List VE.Formula
  φ : VE.Formula
  c : VE.Tableau.Certificate
  coherent : Bool               -- every pair's certificate checked (`defaultCoherenceCheck`)
  model : Bool                  -- `(modelCheckX v.L.U (defaultX v.L.D v.L.X) M F Γ .top).1`
  strictCounter : Bool          -- the request's `strict_model` (M₀, F₀) checked:
                                -- `modelCheckX v.L.U v.L.X M₀ F₀ Γ φ = (true, false)`; `false` when absent
  assumptions : List String     -- `assumptionsOf`, recomputed by Lean
def replayCert (j : Json) : Except String CertReplay

/-- The answer's verdict: FOLLOWS needs the gate and the model (2.2); otherwise UNKNOWN with its reason. -/
def verdictOf (x : CertReplay) : String := if x.coherent && x.model then "FOLLOWS" else "UNKNOWN"

/-- What a FOLLOWS answer claims: the entailment with the kept assumptions; the gate; that the premises hold with no
    exception in some situation (non-vacuity); and its basis. -/
theorem defaults_certificate_sound (j : Json) (x : CertReplay) (h : replayCert j = .ok x) :
    EntailsX.{u} x.v.L.U (x.v.L.X ++ VE.Readings.blank (dfltLabelled x.v.L.D) x.assumptions) x.Γ x.φ ∧
    (x.coherent = true → DefaultCoherent.{u} x.v.L.U x.v.L.D x.v.R) ∧
    (x.model = true → ∃ S : VE.Structure.{0},
      BaseAdmissibleX x.v.L.U (defaultX x.v.L.D x.v.L.X) (restrictAll (fill x.v.L.U).T S) ∧
      DocumentExpansion (fill x.v.L.U) (restrictAll (fill x.v.L.U).T S) S ∧ Sat S x.Γ) ∧
    (basisOf x.assumptions x.strictCounter = .strict → EntailsX.{u} x.v.L.U x.v.L.X x.Γ x.φ) ∧
    (basisOf x.assumptions x.strictCounter = .needs → ¬ EntailsX.{0} x.v.L.U x.v.L.X x.Γ x.φ)

/-- FOLLOWS is given only with the gate and the model. -/
theorem defaults_follows_gated (j : Json) (x : CertReplay) (h : replayCert j = .ok x)
    (hv : verdictOf x = "FOLLOWS") : x.coherent = true ∧ x.model = true

structure ModelReplay where
  v : DefaultsView
  Γ : List VE.Formula
  φ : VE.Formula
  M : VE.FiniteModel VE.Bridge.Entity
  F : VE.NormDefaults.FiniteFill v.L.U VE.Bridge.Entity
  ok : (modelCheckX v.L.U (defaultX v.L.D v.L.X) M F Γ φ).1 = true ∧
       (modelCheckX v.L.U (defaultX v.L.D v.L.X) M F Γ φ).2 = false
  forced : List (String × Nat × List VE.Bridge.Entity)
                                -- `forcedAt`: each rule whose exception holds at a typed tuple of `M`, with the index
                                -- of a stated sufficient condition that holds there (DE11), recomputed by Lean
def replayModel (j : Json) : Except String ModelReplay

/-- The exceptions that hold on the finite base, each with the first stated sufficient condition that holds at its
    tuple (with `Dflt_T` satisfied, one always does). Lean evaluates both on `M`. -/
def forcedAt (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) : List (String × Nat × List VE.Bridge.Entity)

/-- The situation shown; with `forced = []` no rule's exception holds there (DE6's short form). -/
theorem defaults_model_sound (j : Json) (x : ModelReplay) (h : replayModel j = .ok x) :
    ∃ S : VE.Structure.{0},
      BaseAdmissibleX x.v.L.U (defaultX x.v.L.D x.v.L.X) (restrictAll (fill x.v.L.U).T S) ∧
      DocumentExpansion (fill x.v.L.U) (restrictAll (fill x.v.L.U).T S) S ∧ Sat S x.Γ ∧ ¬ x.φ.denote S [] ∧
      (x.forced = [] → ∀ N ∈ x.v.L.D.T.nodes, N.mode = .default →
        (bindAll (sortsOf x.v.L.D N.pred) (.not (exceptedF x.v.L.D N))).denote S [])

/-- The kinds above answer only `defaults-*`; every existing kind is answered by `layeredCase` as today. -/
theorem defaultsCase_other (L : LayeredU) (id kind : String) (j : Json) (hk : ¬ kind.startsWith "defaults-") :
    defaultsCase L id kind j = .ok none
```

`defaults_model_sound` is `modelCheckX_sound` at `X := defaultX …` (its conclusion read as RD-9 states it); its last
conjunct evaluates each `excepted` atom on the checked finite base (`forcedAt` lists every one that holds).
`defaults_certificate_sound`'s non-vacuity conjunct is `modelCheckX_sound` at `defaultX` with `φ := ⊤`, the model the
replay checked; its `needs` conjunct is `basis_needs_sound` on the request's `strict_model`. `defaultsCase_other` is the
conservativity statement at the wire: no existing kind's answer changes.

### 3.4 DF-2: the meaning (`Defaults/Meaning.lean`)

```lean
/-- `B` with the tables `δ` on the decision predicates of `D` and `F` on the unsaid predicates of `U`; the facts, the
    domain, the constants and every other symbol as in `B`. -/
def withOpen (U : UDoc) (D : SoftDoc) (B : VE.Structure.{u}) (δ F : String → List B.Carrier → Prop) :
    VE.Structure.{u} :=
  { B with relation := fun p vs =>
      if p ∈ decisionNames D then δ p vs
      else if p ∈ VE.NormDefaults.unsaidNames U then F p vs
      else B.relation p vs }

/-- No switch of `D` is on in `B`: the switch premises of `Dflt_T` hold (at typed tuples, as every premise reads). -/
def SwitchesOff (D : SoftDoc) (B : VE.Structure.{u}) : Prop :=
  Sat B (((dfltLabelled D).filter (fun a => a.1.startsWith "default:switch:")).map (·.2))

/-- A default base: admissible with the document's own `X`, no switch on, and no admissible base on the same facts
    with fewer decisions, where the competing base may also change the unsaid tables: circumscription of the decision
    predicates with norm-defaults' unsaid predicates varied (D15). The facts, the domain and the constants are fixed. -/
def DefaultBase (U : UDoc) (D : SoftDoc) (X : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleX U X B ∧ SwitchesOff D B ∧
  ∀ δ F : String → List B.Carrier → Prop,
    (∀ p ∈ decisionNames D, ∀ vs, δ p vs → B.relation p vs) →
    BaseAdmissibleX U X (withOpen U D B δ F) → SwitchesOff D (withOpen U D B δ F) →
    ∀ p ∈ decisionNames D, ∀ vs, B.relation p vs → δ p vs

/-- `X` as RD-9 and PK-1 assemble it: soft's pack (exception premises, then coherence premises on `fill U`), then
    the other packs `R`. -/
def softX (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : List VE.Formula :=
  (softLabelledU U D).map (·.2) ++ R

/-- `δ_B`: the least decision tables on `B`'s facts. A rule's exception holds exactly at the typed tuples where one of
    its stated sufficient conditions holds in `B`; no switch; no `outweighs`. -/
def leastDecisions (D : SoftDoc) (B : VE.Structure.{u}) : String → List B.Carrier → Prop

/-- The computed check that replaces draft 1's `hfill`: the other packs' premises `R` and the base background name no
    decision predicate of `D` and no unsaid predicate of a pair member (the tables `fill_extends` repairs). -/
def replacementSafe (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Bool :=
  (R ++ VE.Norms.backgroundBase (fill U)).all (fun φ => (preds φ).all (fun p =>
    !(decisionNames D).contains p &&
    !((VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName).contains p))

/-- Replacement admissibility: on a base admissible with `softX`, the least decisions `δ_B`, with the pair members'
    unsaid tables repaired and every other unsaid table kept, give a base admissible with `defaultX`. -/
theorem replace_admissible (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hsafe : replacementSafe U D R = true)
    (hcoh : DefaultCoherent.{u} U D R) (B : VE.Structure.{u}) (hB : BaseAdmissibleX U (softX U D R) B) :
    ∃ F : String → List B.Carrier → Prop,
      (∀ p, p ∉ (VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName → ∀ vs, (F p vs ↔ B.relation p vs)) ∧
      BaseAdmissibleX U (defaultX D (softX U D R)) (withOpen U D B (leastDecisions D B) F)

/-- A base with the no-exception premises is a default base. No gate needed. -/
theorem defaultBase_of_dflt (U : UDoc) (D : SoftDoc) (hU : U.D = soften D) (hD : WellFormedSoft D = true)
    (R : List VE.Formula) (B : VE.Structure.{u})
    (hB : BaseAdmissibleX U (defaultX D (softX U D R)) B) :
    DefaultBase U D (softX U D R) B

/-- Under the gate and the computed check, a default answer means: the conclusion holds in every expansion of every
    default base where the question's facts hold. -/
theorem default_entails_minimal (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hsafe : replacementSafe U D R = true)
    (hcoh : DefaultCoherent.{u} U D R) (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (defaultX D (softX U D R)) Γ φ ↔
      ∀ S : VE.Structure.{u}, DefaultBase U D (softX U D R) (restrictAll (fill U).T S) →
        DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

/-- `defaults_model_sound`'s situation is a default base. -/
theorem defaults_model_default_base (j : Json) (x : Wire.ModelReplay) (h : Wire.replayModel j = .ok x) :
    ∃ S : VE.Structure.{0}, DefaultBase x.v.L.U x.v.L.D x.v.L.X (restrictAll (fill x.v.L.U).T S) ∧
      DocumentExpansion (fill x.v.L.U) (restrictAll (fill x.v.L.U).T S) S ∧ Sat S x.Γ ∧ ¬ x.φ.denote S []
```

Proof notes. `defaultBase_of_dflt` (unchanged from draft 1): with `Exc_T` and `Dflt_T`, `B`'s exception table is
exactly the stated sufficient conditions, its switches and `outweighs` tables are empty; any admissible competitor
`(δ, F)` with `δ` below `B` satisfies `Exc_T`, whose conditions are base formulas of `soften D` over the unchanged facts
(soft 3.2, `hD`; the unsaid names are fresh there, `hu.freshPred`), so `δ` contains the same exception table whatever
`F` is: `B` is minimal.

`replace_admissible`, the replacement-admissibility lemma. Put `δ_B` on the decisions of `B`, keeping every other table,
and apply `fill_extends` (`NormDefaults/Premises.lean:293`): decisions are base predicates of `U.D = soften D`, so
`fill_extends` applies to the replaced base and gives a filling `F` that satisfies `Fill_T`, changes only the pair
members' unsaid tables, and makes the permission members true (`canonicalFill`). The result satisfies: the base
background and `R`, because they name no decision and no pair member's unsaid predicate (`hsafe`) and every table they
read is `B`'s; `Exc_T`, because its conditions are over the unchanged facts and `δ_B` sets each exception exactly where
a sufficient condition holds (a necessary condition holds there because it holds in `B`, where `Exc_T` forces the
exception); `Dflt_T`, by construction. So it is admissible with `Exc_T ++ R ++ Dflt_T`, and the gate `hcoh` gives
`Coh_T`: it is admissible with `defaultX`.

`default_entails_minimal`, (→): let `B` be a default base. `δ_B` is below `B` on decisions (`B` satisfies `Exc_T`'s
sufficient premises; `δ_B` has no switch and no `outweighs`). By `replace_admissible`, `withOpen U D B δ_B F` is
admissible with `defaultX`, hence with `softX`, and has no switch on: it is a competitor. Minimality gives `B = δ_B` on
decisions. `Dflt_T` names decisions and facts only, on which `B` and the competitor agree, so `B` satisfies `Dflt_T`;
`B` is admissible with `defaultX` and `EntailsX` applies. (←): a base admissible with `defaultX` is a default base by
`defaultBase_of_dflt`. The table comparisons in `DefaultBase` range over all tuples; an admissible base's relations
hold only at typed tuples (`Admissible`), which is what makes them agree with the premises' typed quantifiers. What
DF-S must confirm as true, not only well typed: `replace_admissible` (in particular that `fill_extends` applies after
the decisions are replaced, and that `withOpen`'s unsaid tables are read on typed tuples as `withFill` reads them),
that `Dflt_T` and `Exc_T` name no unsaid predicate, and the typing fact. `hR` of draft 1 is part of `hsafe`. This is
Reiter's (1982) and Lifschitz's (1985) "circumscription equals completion" for definitional abnormalities, with the
unsaid predicates varied (Lifschitz's circumscription with varied predicates), in VE's setting.

**Why the unsaid tables vary (DF-π, Astra's counterexample).** One default obligation `r1` on `x_required`, its
paired permission `x_permitted`, both `unspecified`, no stated exception condition, situation `a`. Take `B_π` with
`r1`'s exception at `a` and both gap fillings "no". Then both outcomes are false and `Fill_T` holds. With the filling
fixed, removing the exception makes `x_required(a)` true while `x_permitted(a)` stays false, which violates `Fill_T`;
so `B_π` is minimal among bases with its filling, the gate passes (no colliding pair), and yet `Dflt_T` entails
`x_required(a)`. Draft 1's fixed-filling `DefaultBase` therefore made `default_entails_minimal` false here, and its
`hfill` was false whenever a default rule sits on a pair member (`fillPremises` is built from `pairConflict (fill U)`
and `gapF`, substituted outcomes that carry `¬excepted`). With the filling varied, the competitor "no exception, the
permission's gap filled yes" is admissible, so `B_π` is not a default base, and both sides of the theorem hold. DF-π's
two `example`s in `Defaults/Meaning.lean` check exactly this: draft 1's fixed-filling minimality holds at `B_π` (that
definition kept in the stub only), and `¬ DefaultBase U D (softX U D []) B_π`.

**Fallback (Astra's restriction).** If DF-S cannot confirm the (→) proof as stated, DF-2 proves `defaultBase_of_dflt`
and (←) only, and states (→) with `replace_admissible`'s conclusion as an explicit hypothesis on the document instead
of a lemma. Then no English, `lean/DEFAULTS.md` or doc text claims minimality anywhere (0, 2.9, 8 and S1 are restated
as conditional on `Dflt_T`), and every default answer stays explicitly conditional on the assumptions it lists. A
document that fails `replacementSafe` gets the same treatment under the main plan.

### 3.5 DF-3: readings (`Readings/DefaultVerdicts.lean`)

```lean
namespace VE.Readings
open VE.Defaults

/-- A choice's soft document, as RD-9's `softXL` reads it; and the non-soft part of its `X` (empty on the soft chain). -/
def choiceSoft (N : NDoc) (c : Choice) : VE.SoftNorms.SoftDoc
def choiceR (N : NDoc) (c : Choice) : List VE.Formula

/-- Per-choice results unless an exception applies: RD-9's `xSem` with `Dflt_T` appended; conflict freedom is the
    strict one together with the gate. Field names are RD-9's `ChoiceSem` (rd-9-soft-chain.md 1.9). -/
def dSem (N : NDoc) : ChoiceSem :=
  { xSem N (fun c => choiceX N c ++ dfltPremises (choiceSoft N c)) with
    free := fun c => (sdSem N).free c ∧ DefaultCoherent (choiceU N c) (choiceSoft N c) (choiceR N c),
    notFree := fun c => (sdSem N).notFree c ∨ ¬ DefaultCoherent (choiceU N c) (choiceSoft N c) (choiceR N c) }

theorem dSem_entails (N : NDoc) (c : Choice) (Γ : List VE.Formula) (φ : VE.Formula) :
    (dSem N).entails c Γ φ ↔
      EntailsX (choiceU N c) (defaultX (choiceSoft N c) (choiceX N c)) ((choiceDoc N.D c).2 ++ Γ) φ   -- `Iff.rfl`
```

RD-9's `foldG_all_sound`, `foldG_some_sound`, `foldG_none_sound`, `foldG_conflict_free_sound`, `foldG_conflict_sound`
and `foldG_premises_*_sound` apply to `dSem N` as stated: DF-3 adds no fold theorem. Its wire theorem is RD-9 SC-5's
`readings-verdicts` theorem with `dSem` for `sdSem`, the rows read from per-choice `defaults-certificate`,
`defaults-model` and `defaults-coherence` replays, with one added conjunct: the `default` member is present only when
the strict conflict fold is FREE, so a default-fold CONFLICT names choices whose gate fails (each with its checked
collision, `collision_sound`) and is rendered as DE7 per choice, never with RD-9's contradiction wording (2.4).
Enumerated route only (at most 64 choices); the superposed route needs `Transfers` for `Dflt_T`, which is not a PK-1
pack, so PK-1's provider obligation 4 does not cover it; it is not in this plan (section 11, issue 6).

### 3.6 DF-5: at one situation (`Defaults/Zone.lean`)

Interface over WG-6's reviewed names (weighing-PLAN 3.4); exact once WG-6 lands. WG-6's reviewed enumeration is over
the query's cone (`coneValuesO`); the enumeration over a given atom list that DF-5 calls is a request to WG-6, the
owner (section 11, issue 1), not a second enumerator.

```lean
namespace VE.Defaults
open VE.Weighing (AdmissibleCompletion OutcomeIn decisionAtoms openNames SettledZ ZoneUnknown)

/-- `R₁` holds no decision atom of the situation that `R₂` lacks. Only decision atoms are compared; the unsaid atoms
    of the two completions are free to differ (D15, as `DefaultBase`). -/
def DecLe (D : SoftDoc) (M : VE.FiniteModel α) (R₁ R₂ : String → List α → Prop) : Prop :=
  ∀ a ∈ decisionAtoms D M, R₁ a.1 a.2 → R₂ a.1 a.2

/-- Each observed outcome has its observed value. -/
def Observed (U : UDoc) (M : VE.FiniteModel α) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (R : String → List α → Prop) : Prop :=
  ∀ o ∈ obs, (OutcomeIn U M R o.1.1 o.1.2 ↔ o.2 = true)

/-- Switches off, except where the record says otherwise. -/
def switchesOffRecord (D : SoftDoc) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool)) :
    List ((String × List α) × Bool)

/-- A default completion: admissible with the record and the switches off, agreeing with the observations, and minimal
    in decisions among such completions. `R'` ranges over every admissible completion, whose open atoms are the decision
    and the unsaid atoms (`openNames`), so its unsaid tables vary; the facts and the domain are `M`'s, fixed by
    `AdmissibleCompletion`. This is `DefaultBase`'s comparison at one situation. -/
def DefaultCompletion (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α) (record obs)
    (R : String → List α → Prop) : Prop :=
  let rec' := record ++ switchesOffRecord L.D M record
  AdmissibleCompletion L.U X M (openNames L) rec' R ∧ Observed L.U M obs R ∧
  ∀ R', AdmissibleCompletion L.U X M (openNames L) rec' R' → Observed L.U M obs R' → DecLe L.D M R' R →
    DecLe L.D M R R'

def ByDefaultZ (L X M record obs r vs) (b : Bool) : Prop :=
  (∃ R, DefaultCompletion L X M record obs R) ∧
  ∀ R, DefaultCompletion L X M record obs R → (OutcomeIn L.U M R r vs ↔ b = true)

def ByDefaultLeftTo (L X M record obs r vs) : Prop :=
  ∃ R₁ R₂, DefaultCompletion L X M record obs R₁ ∧ DefaultCompletion L X M record obs R₂ ∧
    (∀ n ∈ VE.NormDefaults.unsaidNames L.U, ∀ ws, R₁ n ws ↔ R₂ n ws) ∧
    OutcomeIn L.U M R₁ r vs ∧ ¬ OutcomeIn L.U M R₂ r vs

inductive DefaultZone (α : Type u)
  | byDefault (b : Bool) (witness : List ((String × List α) × Bool))
  | leftTo (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool))
  | notSaid (w₁ w₂ : List ((String × List α) × Bool))
  | noCompletion (labels : List String)
  | unknown (reason : ZoneUnknown α)

/-- The bound on the open atoms enumerated: every typed open atom of the situation not fixed by the record. -/
def maxDefaultAtoms : Nat := 12

/-- Every typed open atom of `M` not fixed by the record: the decision atoms, and the unsaid atoms under
    `norm-defaults@0`. Not a cone: the question's atoms, the observations' atoms and every atom a premise of X or
    `Fill_T` names are all in it. -/
def openAtomsAll (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool)) :
    List (String × List α)

/-- WG-6's bounded enumeration over `openAtomsAll` (the atom list given, no cone pruning; `unknown (budget)` beyond
    `maxDefaultAtoms`), then the full assignments that satisfy X and `Fill_T` (each premise evaluated on the finite
    situation) and agree with the observations, then the minimality filter over their decision parts. -/
def defaultZoneOf (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α) (record obs)
    (r : VE.Norms.Regulated) (vs : List α) (proposed : List (List ((String × List α) × Bool))) : DefaultZone α

/-- Stated now, proved before any cone pruning is enabled (D10): for a cone that contains the question's atoms and
    the observations' atoms and is closed under sharing a premise instance of X or `Fill_T`, the restrictions of the
    default completions to the cone are exactly the decision-minimal admissible cone assignments that extend to an
    admissible completion agreeing with the observations (minimal completions factor over independent components).
    Containing the observations' atoms alone is not enough. -/
theorem cone_minimal_iff -- statement fixed by DF-S; cone pruning only after it is proved

theorem defaultZone_byDefault_sound (L X M valid hb record obs r hr vs typed proposed b w)
    (hz : defaultZoneOf L X M record obs r vs proposed = .byDefault b w) :
    ByDefaultZ L (X.map (·.2)) M record obs r vs b

theorem defaultZone_leftTo_sound (L X M valid hb record obs r hr vs typed proposed differ w₁ w₂)
    (hz : defaultZoneOf L X M record obs r vs proposed = .leftTo differ w₁ w₂) :
    ByDefaultLeftTo L (X.map (·.2)) M record obs r vs ∧ ∀ a ∈ differ, a.1 ∈ decisionNames L.D

/-- Weighing's record "assuming no exception applies": every `excepted` atom of the situation set to false. -/
def noExceptionRecord (D : SoftDoc) (M : VE.FiniteModel α) : List ((String × List α) × Bool)

/-- No stated sufficient exception condition holds at any typed tuple of the finite base `M` (evaluation on `M`). -/
def noSufficientHolds (D : SoftDoc) (M : VE.FiniteModel α) : Bool

/-- Weighing's record is the instance with nothing observed, no switch and no `outweighs` decision in the document,
    no sufficient condition holding at `M`, and an admissible completion agreeing with the record. In general this
    plan's record also sets every switch off and keeps the ranking (2.1), which weighing's record leaves open. It needs
    the varied comparison: with the filling fixed, DF-π's excepted completion with fillings no/no would be minimal and
    the left side would fail where weighing's record gives `settled yes` (DF-π′). -/
theorem defaultZone_eq_noException (L X M r vs b)
    (hnone : offDecisions L.D = [] ∧ outweighsTriples L.D = [])
    (hsuff : noSufficientHolds L.D M = true)
    (hadm : ∃ R, AdmissibleCompletion L.U X M (openNames L) (noExceptionRecord L.D M) R) :
    ByDefaultZ L X M [] [] r vs b ↔ SettledZ L.U X M (openNames L) (noExceptionRecord L.D M) r vs b
```

Proof notes. With the full enumeration every assignment sets every open atom, so admissibility and each observation are
decided by evaluation on the finite situation (no Kleene unknown), and the minimality filter compares exactly the
admissible completions `DefaultCompletion` quantifies over: `defaultZone_byDefault_sound` and
`defaultZone_leftTo_sound` need the enumeration's completeness over `openAtomsAll` and no cone lemma. A witness reported
for `byDefault` is checked with `modelCheckX` as weighing's are. `defaultZone_eq_noException`: by `hadm` some admissible
completion has no decision at all; it is below every completion, so with no switch and no `outweighs` decision the
default completions are exactly the admissible completions with every exception false, which are weighing's.

### 3.7 DF-6: with `weighing@0`

```lean
/-- With `weighing@0`: an `outweighs` decision holds only where one of weighing's sufficient override conditions on it
    holds (the sufficient case of `Dec_T`, WG-2's `condPremise`); switches stay off (weighing allows no sufficient
    switch condition, its D6). Replaces `dfltLabelled`'s ranking part when the block is present; equal to it when the
    block has no sufficient override condition. -/
def dfltRankingW (D : SoftDoc) (Wd : VE.Weighing.WeighDoc) : List (String × VE.Formula)

theorem dfltRankingW_empty (D : SoftDoc) (Wd : VE.Weighing.WeighDoc) (h : sufficientOverrides Wd = []) :
    dfltRankingW D Wd = (dfltLabelled D).filter (fun a => a.1.startsWith "default:ranking:")

/-- `default_entails_minimal` with weighing's pack in `R`: weighing's premises name decisions, so `replacementSafe`
    fails and `replace_admissible` does not apply. It is replaced by weighing's own replacement argument: its
    sufficient conditions are base formulas (weighing D6), its strict-pair premises agree with `Dflt_T` (both say no
    override), and its necessary conditions, which can constrain decisions and entail base facts (SYNTHESIS C1, W-κ),
    still hold after the decisions are replaced by the least ones. -/
theorem default_entails_minimal_weigh -- statement fixed by DF-S after WG-1's review
```

DF-6 waits for that replacement argument to pass its own statement review; until then `weighing@0` documents keep
diagnostic 1.

## 4. Fixtures

### 4.1 Synthetic (`#guard`s in `Defaults/Examples.lean`; the same through the service in Python)

Unless a fixture says otherwise: weighing's soft frame (one sort `assistant`, act X with `x_required` obligation and
`x_permitted` permission as its dual, situation `a`, guards `⊤`), profiles `norm-defaults@0`, `norms@0`,
`relational-fol@0`, `soft-norms@0`, with `x_required` `unspecified` and `x_permitted` allow-by-default, decider "the
assistant". Values *derived*; DF-S computes them in the stub.

| # | Document | Question | Expected |
|---|---|---|---|
| DF-α | r1 "Every assistant should X." (default, `unstated`, no conditions) | `∀a. x_required(a)` | strict: no certificate; the strict countermodel (r1's exception at a, filling no) is sent as `strict_model`; `defaults-coherence` COHERENT (no pair); `defaults-certificate` FOLLOWS, basis `needs`, form short, assumptions `[default:exception:r1]`; DE1 + DE2 |
| DF-α′ | DF-α, the request without `strict_model` (or with one that does not check) | as DF-α | FOLLOWS, basis `unsettled` (never `needs`), form short; DE1 + DE2 + DE12 |
| DF-β | DF-α + "Rule 1 is excepted when that assistant is urgent." (`urgent` base) | (i) `∀a. x_required(a)`; (ii) `∀a. ¬urgent(a) → x_required(a)` | (i) `defaults-model` DOES-NOT-FOLLOW at `urgent(a)` (the exception is forced; filling no); `forced` = [rule 1 at a, its condition]; DE6′ + DE11 "The text's own exception to rule 1 applies here: that assistant is urgent.", never DE6; (ii) FOLLOWS, basis `needs` (strict countermodel {urgent: ∅, excepted: {a}}, filling no), form long (the assumption has a stated condition), `[default:exception:r1]`; DE1′ + DE2′ naming the condition. The `#guard`: `Dflt_T`'s premise is false on {urgent: ∅, excepted: {a}} and true on {urgent: {a}, excepted: {a}} |
| DF-γ | r1 "should X" and r2 "should not X" (`x_permitted`, default), unranked | any | `defaults-coherence` COLLISION at a with no exception; every question UNKNOWN (with no exception, rules r1 and r2 conflict); DE7 |
| DF-δ | DF-γ + r1 serves safety, r2 serves helpfulness, safety outranks helpfulness, holistic | `∀a. x_required(a)` | COHERENT (rank-resolved); FOLLOWS, basis `needs` (strict countermodel: r1's exception at a), form long (a ranking assumption), assumptions `[default:exception:r1, default:ranking:helpfulness:safety:x_permitted]`; DE1′ + DE2 + DE4, never DE1 |
| DF-δ′ | DF-δ with the strict flag | as DF-δ | FOLLOWS, assumptions `[default:exception:r1]` (no `outweighs` decision exists), form short; DE1 + DE2 |
| DF-ε | r1 "should X (users may turn off)" | `∀a. x_required(a)` | FOLLOWS, basis `needs`, form long (a switch assumption), assumptions `[default:exception:r1, default:switch:r1:user]`; DE1′ + DE2 + DE3, never DE1 |
| DF-ζ | r0 "Every assistant must X." and r1 "Every assistant should X." (default, decided by the assistant) | `∀a. x_required(a)` | FOLLOWS, basis strict, assumptions `[]`; DE5 "This holds whatever the assistant decides." (r1 gives `Dflt_T` a decider; draft 1's r0 alone has `Dflt_T = []`, which is F-DF1's case) |
| DF-η | DF-α | premises "r1's exception applies to a" | diagnostic 3, `… it states whether rule r1's exception applies` |
| DF-θ | DF-α with `weighing@0` and an empty block | any | diagnostic 1 (until DF-6) |
| DF-ι | DF-α | premises that no situation satisfies with the frame's flags | UNKNOWN (no checked situation where the premises hold with no exception), never FOLLOWS |
| DF-κ | DF-α, the same certificate with a binding that omits a `Dflt_T` premise, or adds one | — | `bindCertX` refuses; UNKNOWN (no certificate) |
| DF-λ | plain `instructs_via_system_prompt(operator)`, verbalisation "{0} gives its instructions in the system prompt", `unspecified`; g1 "Every operator gives its instructions in the system prompt, unless an exception applies." | `∀o. instructs_via_system_prompt(o)` | DF-4: parses with one derivation; `print(parse(s)) = s`; strict no (a strict countermodel sent); FOLLOWS, basis `needs`, form short, `[default:exception:g1]` |
| DF-μ | DF-λ at {o1, o2}, observed `instructs_via_system_prompt(o1)` = no | zones at o1 and o2 | DF-5 (full enumeration, 4 open atoms): the one default completion excepts g1 at o1 only (DE10 "The facts here force the exception to rule g1 for o1"); at o2 `byDefault yes` |
| DF-μ′ | plain `p`, r1 (+, guard `A`), r2 (−, guard `B`), unranked, a with `A(a)`, `B(a)` | zone of p at a | `leftTo` (two default completions: r1 excepted, or r2 excepted) |
| DF-μ″ | DF-S writes it: r1 on plain `p` and r2 on plain `q`, colliding (incompatible acts), unranked, a with both guards | zone of `p` at a | `leftTo` (*derived*), found only because the enumeration includes r2's exception atom, outside `p`'s cone; the regression for enumerating every open atom before `cone_minimal_iff` (DF-5) |
| DF-ν | readings: RD-9's F-SD1 (K1, set {strict, default} on "avoid deceiving", `avoid_required` unspecified) | `∀ agent ∀ user. avoid_required` | RD-9: SOME; strict fold FREE; DF-3: ALL, the default choice with `[default:exception:no-deception]`; DE8 "Under every reading, the conclusion follows under the assumptions listed for that reading.", then the default reading with its DE2 |
| DF-ξ | weighing's Z-ε (record "no exception applies", no sufficient condition) | its zone | DF-5's `byDefault` equals weighing's `settled yes` (`defaultZone_eq_noException`) |
| DF-π | Astra's counterexample: r1 "Every assistant should X." (default, no conditions), with `x_permitted` also `unspecified` (not allow-by-default); `B_π` = {excepted: {a}}, both gap fillings no | `∀a. x_required(a)` | DF-2's two `example`s: draft 1's fixed-filling minimality holds at `B_π`; `¬ DefaultBase U D (softX U D []) B_π` (the competitor: no exception, the permission's gap filled yes); `replacementSafe` true, gate COHERENT (no pair). `defaults-certificate` FOLLOWS, basis `needs`, form short; DE1 + DE2. Regression for D15: the right side of `default_entails_minimal` holds (with draft 1's definition it failed at `B_π`) |
| DF-π′ | DF-π at the situation {a}, nothing observed, no record | zone of `x_required` at a | DF-5: `byDefault yes` (the only default completions have no exception and the permission filled yes); equal to weighing's `settled yes` under its "no exception applies" record (`defaultZone_eq_noException`). A filter that compares only completions with the same filling keeps the excepted completion with fillings no/no and does not answer `byDefault yes` |
| DF-ρ | DF-ν plus a second reading set whose default reading collides with K1's default reading, unranked, and whose readings meet K1's strict reading without strict conflict (DF-S writes the set and computes it in the stub) | as DF-ν | RD-9: strict fold FREE; DF-3: default fold CONFLICT, from the gate only; English: RD-9's strict answer, then per choice whose gate fails "Under <reading>: Rules <m> and <n> conflict here unless one of them gives way: <effect of m>, and <effect of n>. The text ranks neither above the other, and names no exception that applies here. Which rule gives way is left to <decider>." (DE7), never RD-9's contradiction wording; with the strict fold not FREE, no default member at all |

### 4.2 From the pilots (*derived*; measured by the batch named)

| # | Unit and source words | Question | Expected |
|---|---|---|---|
| P-1 (DF-1b) | the three remaining constitution sets' `default` candidates as standalone soft documents in `CE4`'s frame (RD-9 SC-9): u0036.s05 "Claude should ask for clarification in cases of genuine ambiguity."; u0156.s03 "Claude shouldn't actively deceive the user about the existence of a system prompt or its content."; u0263.s04.p2 "… in situations where Claude has explicitly been instructed not to engage in unintended exploits, it should comply." | `∀ c ∀ s. genuine_ambiguity(s) → clarification_required(c, s)`; `∀ c ∀ u. ¬ system_prompt_deception_permitted(c, u)`; `∀ c ∀ s. explicit_instruction_against_exploits(c, s) → exploit_instruction_compliance_required(c, s)` | strict: no certificate, and a strict countermodel each (the rule's exception taken); FOLLOWS, basis `needs`, form short, one assumption each (`decided_by: unstated`, DE1 + DE2 "the text names no case"). The pilot number: probes answered unless an exception applies, 0 → 3 |
| P-2 (DF-3) | the same three sets inside `CE4` (readings) | the same three | RD-9: SOME each (C7's value); strict fold FREE; DF-3: ALL, DE8 |
| P-3 (DF-1b) | u0073.s05, RD-9's C9 (one default rule, three sufficient exception conditions: unsafe, unethical, against Anthropic's guidelines) | compliance where none of the three holds; compliance with no condition stated | FOLLOWS, form long, DE1′ + DE2′ listing the three conditions; DOES-NOT-FOLLOW at a situation where one holds, DE6′ + DE11 naming it |
| P-4 (DF-3, *estimate*) | UDHR u017 "and should act towards one another in a spirit of brotherhood." once RD-9's UDHR migration gives it {strict, default} | everyone acts towards one another in that spirit | RD-9: SOME; DF-3: ALL, DE8. Depends on how the pilot writes u017 |
| P-5 (DF-4) | u0031.s04 "In most cases, failing to be helpful is costly, even if it's a cost that's sometimes worth it." | — | a reading set {DE9 rule on a plain predicate with an open term for "costly", the majority claim (quantities; pending)}; admitted; DF-E2 audits it |

### 4.3 Conservativity

| # | Case | Expected |
|---|---|---|
| F-DF0 | every existing layered kind on soft-norms, norm-defaults and rights fixtures (`tests/test_norm_defaults_layered.py`, RD-9's F-SD0, F-SD0′, F-SD0″) | byte-identical answers (`defaultsCase_other`) |
| F-DF1 | a document without default rules or switches | `Dflt_T = []`; `defaults-certificate` gives basis strict exactly where `norm-defaults-certificate` gives a certificate |
| F-DF2 | DF-3 on S1's K1 to K22 and S2a's M1 to M20 | the strict fold byte-identical; the default fold present only where a choice has a default rule and the strict conflict fold is FREE |

## 5. Batches

The first two rows have no product code. The first build batch that moves a pilot number is DF-1a with DF-1b
(Lean, then its relay); nothing smaller does, because the pilots reach Lean only through the CLI.

| Batch | What | Hours | Kind | Needs | Pilot effect |
|---|---|---|---|---|---|
| DF-0 | Phase 1 measurement: the second reader, bare generics, the baseline probes, the plain-default probe | 2–3 | measurement | RD-9 SC-9 for the baseline (the rest now) | none; baseline |
| DF-S | Statement spec `docs/spec/defeasible.md` from draft 2, stub elaboration, statement review (Astra + Opus until converged; Fable arbitrates only an unconverged debate) | 3–4 | planner | DF-0 | none |
| DF-1a | `Dflt_T`, the gate, the three-valued basis, the form choice, four kinds, wire theorems, shapes and encoders | 5–6 | Lean | DF-S; `rd-9/integrate` merged; PK-1 | none (no CLI yet) |
| DF-1b | Relay, binding, CLI flag, English display, fuzz tests, pilot probes P-1 and P-3 | 4–5 | Python | DF-1a; RD-9 SC-8 | P-1: 0 → 3 probes answered (*derived*); 0 B |
| DF-E1 | Reader test of the two forms | 2–3 | experiment | DF-1b | decides whether DE1's and DE6's short forms are kept |
| DF-2 | The meaning theorem, with the replacement-admissibility lemma | 5–6 | Lean | DF-1a (runs alongside DF-1b) | none (meaning) |
| DF-3 | Readings: `dSem`, `readings-verdicts` with the default fold shown when the strict fold is FREE, DE7 per choice, DE8 | 5–6 | Lean, Python | DF-1b, DF-E1; RD-9 SC-5 | P-2: 3 queries SOME → ALL unless an exception applies (*derived*); P-4 (*estimate*, enumerated route only); 0 B |
| DF-4 | Defaults about facts: DE9, the reading-set row, deletion of the refusal | 4–5 | English | DF-1b, after DF-3 in the batch order; an english-lean catalogue slot (section 11, issue 3) | 98–572 B, 1–3 units, constitution (*estimate*), only after DF-E2 passes |
| DF-E2 | Generic translations, blind audit | 3–4 | experiment | DF-4; `infra/oom-rootcause`, then premise-scale, first if a translation adds a sort to an existing part (DRI ET1) | gates DF-4's use in pilots |
| DF-5 | At one situation with observations, full bounded enumeration | 5–6 | Lean, Python | DF-2; weighing WG-6 (with the enumeration over a given atom list, section 11, issue 1), WG-7; the corrected statements (DF-S on draft 2). Cone pruning: `cone_minimal_iff` proved | none in bytes; answers for presumptions once attitudes expresses them |
| DF-6 | `weighing@0` in `Dflt_T` | 2–3 | Lean | DF-2; weighing WG-3; its replacement argument reviewed (3.7) | lifts diagnostic 1 |
| DF-7 | "Yes, unless an exception applies" in question answering | 3–4 | Lean, Python | DF-3; `qa-q2` merged | none in bytes |
| DF-E3 | Specificity need | 2 | experiment | none | decides whether an IDE check is built |
| DF-E4 | Observations over all situations | 4–6 | research | DF-5 | decides whether anything is built |

### Batch order (as the plan debate agreed)

1. DF-0, then DF-S on draft 2.
2. DF-1a, after `rd-9/integrate` merges and PK-1 lands.
3. DF-1b, with DF-2 alongside.
4. DF-E1, DF-3, DF-4, then DF-E2.
5. DF-5 after WG-6, WG-7 and the corrected statements. Cone pruning separately waits for `cone_minimal_iff`.
6. DF-6 after WG-3 and its reviewed replacement argument.
7. DF-7 after `qa-q2`.

DF-E3 can run at any time. No English, `lean/DEFAULTS.md` or doc text claims minimality until DF-2 is proved; under
the fallback (3.4), never.

### DF-0. Phase 1 measurement (no product code, 2–3 h)

1. A second reader (a pilot auditor, blind to section 2.3's classes) classifies the 99 screened constitution units into
   the nine classes of research 2.3. **Bar, fixed now**: agreement on "G or not G" on at least 90 of 99 units; if not,
   research 2.3's G-class figures are withdrawn and replaced by the second reader's.
2. Bare generics: units whose first clause has a bare plural or a mass-noun subject and a present-simple verb, no
   marker word, and no deontic verb (a stated screen, committed before it runs), counted and classified like 1.
3. Baseline: on RD-9 SC-9's probe translation, P-1's and P-2's questions with today's kinds, answers recorded verbatim.
4. The plain-default probe: a soft document with DF-λ's rule as JSON content, through `ve document check` and
   `render`; record what each does today (expected: check passes, render refuses with
   `ve/norm_english.py:398`'s text).

Outputs: `docs/research/defeasible-phase1.md` and the screen scripts under `docs/research/defeasible-phase1/`.

### DF-S. Statement review (planner, 3–4 h)

The spec gives 2.1 to 2.9 and section 3 of draft 2 as statements, elaborated in an untracked stub
(`lean/SpecStubs_defeasible.lean`, run with `lake -d lean env lean`), with every fixture of 4.1 computed, DF-π's two
`example`s and DF-ρ's second set among them. Review checklist in section 9. Gate for DF-1a: both reviewers accept each
statement as **true under its hypotheses**, in particular `replace_admissible` and the (→) proof of
`default_entails_minimal` (3.4), `basis_needs_sound`, the non-vacuity conjunct, and `assumptions_sound`'s split of
`premisesX`. If they cannot confirm the (→) proof, DF-S adopts the fallback of 3.4 (Astra's restriction, no minimality
claim anywhere) and records it in the spec; DF-1a does not wait for DF-2 either way.

### DF-1a. The premises, the gate, the basis, the kinds (Lean, 5–6 h)

- **Lean.** `Defaults/Premises.lean` (3.2), `Defaults/Wire.lean` (3.3), `Defaults/Examples.lean` (DF-α to DF-ι, DF-κ as
  `#guard`s on regenerated premises, labels, Kleene values on finite models, and wire answers). The four kinds are one
  row of PK-1's layered kind table, calling `defaultsCase`. Response shapes and encoder theorems for the four kinds.
  The new modules are added to the import lists `lean/VE.lean` and `lean/ResponseShape.lean` (union-merged).
  `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`, `lean/axioms.txt` and `lean/{statements,predicates,
  declarations}.txt` are generated (`lean/audit.py --write`, `tools/lean_statements.py`), through
  `tools/regen_generated.py --write`, never by hand. `lean/DEFAULTS.md` in plain words; it describes default answers
  as conditional on the listed assumptions and says nothing about minimality until DF-2 is proved.
- **Trust.** The new Lean is trusted code: the trust tables (`tools/trust-classes.json`, `docs/trust-baseline.json`)
  grow, and growth beyond the signed budget needs `tools/trust_map.py --write --reason` with the DRI's signature, as
  RD-9's did. The batch reports the measured growth.
- **Deleted, not duplicated.** Nothing on `main` computes this today. `assumptionsOf` calls readings' `usedLabels`;
  the certificate check, the binder (`bindCertX`) and the model check are RD-9's.
- **Seeded bugs** (Lean, each shown failing a named test, then restored): `dfltOf` drops the sufficient-condition
  disjunct (DF-β (ii) fails); `basisOf` always returns `.strict` (DF-α's basis `#guard` fails); `basisOf` returns
  `.needs` without a checked strict countermodel (DF-α′'s `#guard` fails); `followsForm` ignores switch labels (DF-ε's
  form `#guard` fails); `forcedAt` returns `[]` (DF-β (i)'s `#guard` fails); `defaultsCase` answers FOLLOWS without the
  coherence certificates (DF-γ's `#guard` fails).
- **Done when** every `#guard` passes, `python3 lean/audit.py` passes (no banned words, even in comments),
  `tools/regen_generated.py --check` passes, and the trust growth is signed.

### DF-1b. The relay and the first pilot number (Python, 4–5 h)

- **Python.** `ve/defaults.py` (new): sends `defaults-*` cases with `rows` from `ve/backends/relay.py`; checks the
  schema and the binding only (R8): every label in `assumptions` is one of the same case's `default_premises`; `pairs`
  match `coherence_targets` one to one, in order; every entity in a situation is in the request's model; `verdict`,
  `basis` (strict, needs, unsettled) and `form` are their enums; `basis`, `form` and `assumptions` appear exactly with
  FOLLOWS; `needs` appears only when the request carried a `strict_model`; every rule in `forced` is a rule of the
  request and every entity is in its model. `ve document readings <path> --conclusion <file> --assume-no-exception`
  (flag in `ve/document.py`) asks the strict question first and the default question only when the strict one has no
  certificate, sending the strict countermodel the strict search found as `strict_model` (none found: none sent, and the
  basis is `unsettled`); the search reads `defaults-elaborate`. English: DE1 to DE7, DE11 and DE12 rendered from Lean's
  rows (`basis`, `form`, `forced`) with the existing rule, condition and situation renderers; Python never chooses a
  form.
- **Tests.** `tests/test_defaults_lean.py` (4.1's fixtures through the service), `tests/test_defaults_answer.py` (fuzz:
  each member dropped, emptied, retyped, duplicated or reordered, a label swapped for another case's, a pair moved; one
  and two faults: every mutant is `CheckerUnavailable` or changes nothing shown), genuine cases recorded into
  `tests/data/route-cases.jsonl` by `tests/route_case_recorder.py`. `tools/relay_lint.py` forbids `default:` literals in
  `ve/`.
- **Pilot.** P-1 and P-3 as a probe script in the next pilot run's directory (`probe_defaults.py`), answers recorded
  verbatim; the pilot's `metrics.json` gains `default_answer_probe` (questions, strict answers, default answers,
  UNKNOWN with reasons).
- **Seeded bugs** (Python): the relay accepts an assumption label not in `default_premises` (a fuzz test fails); the
  relay accepts `needs` on a request without `strict_model` (a fuzz test fails); the renderer drops DE1's "Unless an
  exception applies" (the English fixture test fails); the renderer prints DE6 for DF-β (i) (its English fixture test
  fails).

### DF-E1. The two forms (experiment, 2–3 h)

Pre-registered now. Items: 24 rendered answers from DF-1b, 12 with basis `needs` (every one with a checked strict
countermodel, so that each conclusion is proved to need its assumptions) and 12 strict. Of the 12 `needs` items, 6 are
short-eligible (only exceptions with no stated condition, as DF-α) and 6 are not, including DF-ε's shape (a switch) and
DF-δ's (a ranking). Each item is shown in the long form (DE1′); the short-eligible items are also shown in the short
form (DE1), on separate reader calls. Reader: Sonnet 5.5 as the zero-training human proxy
(project practice), given only the rendered answer and the rule text. Question per item: "Could the conclusion be false
in a situation the text allows, if the decider finds that an exception applies, a party turns the rule off, or the
lower-ranked consideration outweighs the higher one?" (yes for `needs`, no for strict). **Bar**: a form passes if at most
1 of its `needs` items is read as strict and at most 1 of the 12 strict items as `needs`. The long form must pass; if it
fails, DF-3 waits for a redesign of the wording. The short form is kept only if it passes and has fewer misreadings
than the long form on the 6 short-eligible items; otherwise it reads no better, it is dropped, and Lean always selects
DE1′. DE6's short form is kept or dropped with DE1's. "By default, …" is not a candidate (D6).

### DF-2. The meaning (Lean, 5–6 h)

`Defaults/Meaning.lean` (3.4): `withOpen`, `DefaultBase` with the unsaid tables varied, `leastDecisions`,
`replacementSafe`, `replace_admissible`, `defaultBase_of_dflt`, `default_entails_minimal`, DF-π's two `example`s, and
the corollary for `defaults-model`. No answer, text or shape changes; once it is proved, `lean/DEFAULTS.md` may state
the minimality reading for documents that pass `replacementSafe`. Under the fallback (3.4) it proves
`defaultBase_of_dflt` and (←) only, and nothing claims minimality. **Seeded bugs**: `default_entails_minimal` stated
without `hcoh`: the build fails, and the stub's DF-γ counterexample (the left side holds vacuously at the collision,
the right side does not) shows that statement false; `DefaultBase` with the filling fixed (draft 1's definition):
DF-π's second `example` fails (`B_π` becomes a default base).

### DF-3. Readings (Lean and Python, 5–6 h)

- **Lean.** `Readings/DefaultVerdicts.lean` (3.5); `readings-verdicts` gains, when the request asks for it and the
  strict conflict fold is FREE, the default fold beside the strict one (`default` member: verdict, per-choice basis and
  assumptions, the choices whose gate fails with their collisions, English DE8 or DE7 per choice). One dispatch line in
  RD-9's verdict kind; shapes and encoders for the new member.
- **Python.** `ve/readings_verdicts.py` relays the new member and binds it (choices exist in the request; labels are the
  choice's `default_premises`; the member is absent when the strict fold is not FREE); `--assume-no-exception` reaches
  readings documents.
- **Deleted, not duplicated.** No second fold: `foldG` with `dSem`.
- **Fixtures.** DF-ν, DF-ρ (with its expected English), F-DF2.
- **Pilot.** P-2 on `CE4`, and on the pilot's translation once it adopts RD-9's soft form, where its choices are
  enumerable (at most 64); a translation on the superposed route (`readings@1`) is not measured until `Transfers` for
  `Dflt_T` exists (section 11, issue 6). P-4 when the UDHR has it, on the same condition.
- **Seeded bugs**: `dSem.free` without the gate (DF-ρ gives ALL; the test fails); the default fold shown when the
  strict fold is not FREE, or its CONFLICT rendered with RD-9's contradiction wording (DF-ρ's English test fails); the
  relay keeps a choice not in the request (fuzz fails).

### DF-4. Defaults about facts (English, 4–5 h)

- **English.** DE9 and D14's input form, registered where norm wordings are registered when the batch runs: rows in
  english-lean's Lean catalogue (`lean/VE/EnglishGrammar/*`) if it owns norm wordings by then, else
  `ve/surface/softnorms.py` and `ve/norm_english.py`, never both. The reading-set row for frequency words with a plain
  predicate (D13), with the frequency candidate as quantities' row or pending. DE9's fixed phrase "unless an exception
  applies" is a catalogue row of the kind "profile-fixed wording, not judged by the author lint" (DRI ET2). The batch's
  slot in the `lean/VE/EnglishGrammar/*` queue is the DRI's (section 11, issue 3).
- **Deleted.** `_soft_consequence`'s refusal for plain predicates (`ve/norm_english.py:397-398`).
- **Fixtures.** DF-λ through W7's all-derivations gate and `tests/test_english_unambiguity.py`; P-5.
- **Seeded bug**: the row renders "normally" for DE9 (the W7 gate finds two readings; the test fails).
- **Bytes**: 98–572 B, 1 to 3 constitution units (*estimate*), counted only after DF-E2 passes.

### DF-E2. Generic sentences, translated and audited (experiment, 3–4 h)

Pre-registered now. The 19 G-class units of research 2.3 (and DF-0's bare generics, if any): a pilot translator
writes each as D13's reading set, or leaves it UNFORMALISED with the blocker named; a blind auditor (pilot practice)
judges each attempted unit. **Bar**: 0 invented exceptions (no exception condition the text does not state, the lesson
of u0125.s04.p2) and at least 80% of attempted units FAITHFUL. If it fails, DF-4's wording stays available to authors
but is not used in pilot translations. The translator's instructions reach the pilot through the DRI's merged
pilot prompt (DRI SC2), and a translation that adds a sort to an existing part waits for `infra/oom-rootcause`, then
premise-scale (DRI ET1).

### DF-5. At one situation, with observations (Lean and Python, 5–6 h)

`Defaults/Zone.lean` (3.6) on WG-6's `Weighing/Zone.lean`; the kind `defaults-zone` (a row of PK-1's kind table);
English DE10 and DE11; fixtures DF-μ, DF-μ′, DF-ξ, DF-π′; relay in `ve/defaults.py`. **Deleted, not duplicated**: no
second enumerator. `defaultZoneOf` calls WG-6's bounded enumeration over `openAtomsAll` (every typed open atom of the
situation, decision and unsaid, not the cone; the atom-list form is WG-6's to expose, section 11, issue 1), keeps the
full assignments that satisfy X and `Fill_T` and agree with the observations (each evaluated on the finite situation),
and filters the decision-minimal ones, all in `Defaults/Zone.lean`; `NormDefaults/Evidence.lean` is edited by WG-6
only (SYNTHESIS O18). Beyond `maxDefaultAtoms` the answer is `unknown (budget)`. **Cone pruning** (`coneValuesO`) is a
later step of this batch's owner, enabled only after `cone_minimal_iff` is proved and reviewed; until then it is not
called. **Seeded bugs**: the minimality filter compares unsaid atoms too (DF-μ's filling-only difference turns into
`leftTo`; the test fails); the filter compares only completions with the same filling (DF-π′ no longer answers
`byDefault yes`; the test fails); the enumeration is restricted to the query's cone (fixture DF-μ″, which DF-S writes
and computes: an atom outside the query's cone changes which completions are minimal, for example r1 on `p` and r2 on
`q` colliding, unranked, where the zone of `p` at a is `leftTo`, *derived*; the test fails).

### DF-6. With `weighing@0` (Lean, 2–3 h)

3.7; diagnostic 1 removed; fixtures: weighing's W-ε (sufficient override condition) and W-α (`always`) with
DF-α's question. **Seeded bug**: `dfltRankingW` ignores the sufficient override condition (W-ε's default answer turns
FOLLOWS where the override condition holds; the test fails).

### DF-7. Question answering (Lean and Python, 3–4 h)

After `qa-q2` merges: a question read by Q1 and answered by Q2 gets, when the strict answer is not "yes" and the
default one is, "Yes, unless an exception applies:" (Lean's `form` short) or "Yes, under the assumptions listed
below:" (`form` long) with DE2 to DE4 and, for basis `unsettled`, DE12, from the same kinds. No new kind; Q2's English
rows gain the default case. **Seeded bug**: Q2 renders a default answer as "Yes." (the fixture test fails).

### DF-E3. Specificity (experiment, 2 h)

Pre-registered now. Across the constitution and UDHR translations, the agent-policy, safety-framework, eligibility and
Asimov use cases: colliding default pairs (or W1 pairs on one predicate) where one rule's guard implies the other's
(one entailment each) and the text writes no precedence or rank. **Bar**: build an IDE check that suggests "Rule m
(exception to rule n)." only if at least 5 such pairs exist; automatic specificity is not built whatever the count
(D8).

### DF-E4. Observations over all situations (research, 4–6 h)

Pre-registered now. Count the pilot questions (probes and `ve ask` items) that state an outcome a default rule decides.
For those, try certificates of minimality from an untrusted prover (a 2QBF certificate for "every smaller decision
table violates a premise", checked in Lean by evaluation on a finite candidate domain). **Bar**: no build unless at
least 3 pilot questions need it and DF-5's per-situation answers cannot serve them.

## 6. Dependencies, shared files and merge order

### 6.1 In-flight items this plan depends on

| Item | Branch | What this plan uses | Batches |
|---|---|---|---|
| RD-9 | `rd-9/integrate` (fix rounds) | `EntailsX`, `acceptanceX`, `modelCheckX(_sound)`, `conflictFreeCheckX`, `bindCertX`, `premisesX`, `LayeredU`, `softLabelledU`, `cohPremiseU`; `ChoiceSem`, `xSem`, `sdSem`, `foldG_*`; SC-8 (`ve document` on soft documents); SC-9 (`CE4`, the constitution's default rules) | DF-0, DF-1a, DF-1b, DF-3 |
| PK-1 (premise packs) | new item after `rd-9-int` merges (SYNTHESIS 2.1) | the layered kind table (one row); the soft pack's position in X | DF-1a, DF-5 |
| Weighing | `research/weighing-p1`, build items WG-3, WG-6, WG-7 | the weighing pack (DF-6); zone machinery (DF-5), including a bounded enumeration over a given atom list, which WG-6's reviewed cone enumeration does not yet expose (section 11, issue 1) | DF-5, DF-6 |
| english-lean | the norm-wording step of its catalogue (SYNTHESIS O15) | where DE9 and D13's row live | DF-4 |
| Question answering | `qa-q2` (fix rounds) | Q2's English answers | DF-7 |
| Lean document mode | `lean-first/b16g` (`lf-16g`) | if `ve document`'s readings command has moved to Lean's document mode, DF-1b's flag goes there instead | DF-1b, DF-3 |

### 6.2 Files each batch touches

New files carry most of the work; every shared file is listed.

| Batch | New files | Shared files (one-line or row edits) | Generated (regenerate, never hand-edit or hand-merge) |
|---|---|---|---|
| DF-0 | `docs/research/defeasible-phase1.md`, `docs/research/defeasible-phase1/*` | — | — |
| DF-S | `docs/spec/defeasible.md` | this plan's status line | — |
| DF-1a | `lean/VE/Defaults/{Premises,Wire,Examples}.lean`, `lean/DEFAULTS.md` | PK-1's kind table (one row, in `lean/VE/NormDefaults/Layered.lean` or PK-1's `Packs.lean`); `lean/ResponseShape/Schemas/NormDefaults.lean`, `Encoders/NormDefaults.lean` (four rows); the import lists `lean/VE.lean`, `lean/ResponseShape.lean` (union-merged) | `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`, `lean/axioms.txt` (`lean/audit.py --write`); `lean/{statements,predicates,declarations}.txt`; `lean/checkers.lock`; `ve/backends/lean_service_schema/norm-defaults.json` (`tools/response_schemas.py --write`); the trust tables (growth signed by the DRI) |
| DF-1b | `ve/defaults.py`, `tests/test_defaults_lean.py`, `tests/test_defaults_answer.py` | `ve/document.py` (the flag; or the Lean document mode after `lf-16g`, in SYNTHESIS 4.2's document-mode queue); `tools/relay_lint.py` (one prefix) | `tests/data/route-cases.jsonl` (recorder); the gate's collection record |
| DF-2 | `lean/VE/Defaults/Meaning.lean` | `lean/VE.lean` (import) | the audit manifests and statement lists; `lean/checkers.lock`; the trust tables |
| DF-3 | `lean/VE/Readings/DefaultVerdicts.lean` | RD-9's verdict kind (one dispatch line, `Readings/SoftVerdicts.lean`); `lean/ResponseShape/Schemas/Readings.lean`, `Encoders/Readings.lean`; `ve/readings_verdicts.py`; `ve/readings_english.py` (DE8 renderer); `lean/VE.lean` | `ve/backends/lean_service_schema/readings.json`; the audit manifests and statement lists; `lean/checkers.lock`; the trust tables; route cases |
| DF-4 | — | `lean/VE/EnglishGrammar/*` (in SYNTHESIS 4.2's queue, in landing order) or `ve/surface/softnorms.py` and `ve/norm_english.py`; `tests/test_english_unambiguity.py` fixtures | grammar and lexicon ids as their tools regenerate them |
| DF-5 | `lean/VE/Defaults/{Zone,ZoneExamples}.lean` | PK-1's kind table (one row); shapes and encoders; `lean/VE.lean` (WG-6's enumeration is called, not edited) | as DF-1a |
| DF-6 | — | `lean/VE/Defaults/{Premises,Meaning}.lean` (own) | the audit manifests and statement lists; `lean/checkers.lock`; the trust tables |
| DF-7 | — | Q2's English rows and relay (question-answering's files) | route cases |

### 6.3 How the batches avoid conflicts

- Everything new is in `lean/VE/Defaults/`, `ve/defaults.py` and new test files, which no other plan touches.
- `Layered.lean` (or PK-1's table): DF adds one kind-table row and no pack line, so it does not enter SYNTHESIS 4.2's
  pack queue (AT-2/AT-3a → WG-3 → ET-4 → QT-B2); it rebases onto whichever of those landed first. Its place in the
  queues of SYNTHESIS 4.2 is the DRI's (section 11, issue 4).
- `NormDefaults/Evidence.lean`: DF never edits it (WG-6's only, SYNTHESIS 4.2).
- `ResponseShape` files and generated schemas: rows are appended; generated files are regenerated with
  `tools/response_schemas.py --write` and `tools/regen_generated.py --write`, and a merge whose only conflicts are
  generated files is finished with `tools/regen_generated.py --resolve`.
- `ve/document.py` and the Lean document mode: DF-1b and DF-3 join SYNTHESIS 4.2's document-mode queue in landing order.
- The constitution translation: DF writes no unit of it. P-1 to P-3 are probe documents; P-5 is DF-E2's translation
  attempt, which follows the pilot's own process.

## 7. Measures, and what is reported

- **Probe counts** (DF-1b, DF-3): questions asked, strict answers, default answers, UNKNOWN by reason, each verbatim.
  They are answers, not coverage, and are never reported as coverage.
- **The gate**: per document, colliding pairs and how many are resolved, collide, or are unknown with no exception
  (DF-1b on `CE4`; DF-3 on the pilot translation once it uses soft norms).
- **Cost**: wall and CPU time per default answer against the strict answer on the same question, with host load (one
  run each is not a controlled comparison and is reported as such; speed is measured in `tools/bench/test_perf.py`,
  never asserted in the suite).
- **Bytes**: only DF-4, after DF-E2, as claimed bytes with the pilot's usual audit; no figure is predicted beyond the
  estimate above.

## 8. Risks and open questions

- **The gate may fail often.** Once the constitution has many default rules, unranked collisions with no exception may
  be common; default answers then say UNKNOWN with DE7. That is the honest answer (the text leaves the choice open);
  DF-3 measures how often.
- **The meaning theorem's (→) proof.** Draft 1's `hfill` was false whenever a default rule sits on a pair member
  (DF-π). Draft 2 lets the unsaid tables vary (D15) and proves (→) through `replace_admissible` under the computed
  check `replacementSafe`; the route rests on `fill_extends`, which is on `main`. If DF-S cannot confirm it, the
  fallback of 3.4 applies: Astra's restriction, answers explicitly conditional on `Dflt_T`, and no minimality claim
  anywhere. Documents that fail `replacementSafe` (another pack's premise names a decision or a pair member's unsaid
  predicate) get that treatment under the main plan.
- **DF-5's enumeration is small.** Without cone pruning, `maxDefaultAtoms` (12) bounds every open atom of the
  situation, so larger situations answer `unknown (budget)` until `cone_minimal_iff` is proved; the budget is Lean's
  and is reported, never raised silently.
- **The short form may go.** If DF-E1 finds that "Unless an exception applies" reads no better than "Under the
  assumptions listed below", every default answer uses the long form; the pilot number of P-1 is unchanged (the
  answers are the same, only their first words differ).
- **PK-1's names may change.** DF-1a's statements are over `UDoc`, `SoftDoc` and premise lists, with `DefaultsView`
  the only place that reads `LayeredU`; a PK-1 rename touches that structure only.
- **"Unless an exception applies" in DE9 against W1's carve-out "unless <condition>".** "an exception applies" is a
  fixed phrase that no vocabulary formula produces; W7's all-derivations gate decides in DF-4, and a clash is a refusal,
  never a guess.
- **Readers may over-read the marker** (as "the text says there are exceptions"). DE2's "the text names no case" says
  otherwise; DF-E1 measures both directions.
- **Open question for the DRI**: whether DF-4 needs a `defaults@0` profile (D7), and whether NORTH-STAR row 6's estimate
  should be revised as research 6 suggests.

## 9. Review checklist (for DF-S)

1. `dfltOf` and `dfltLabelled` regenerate exactly 2.1's premises, in the stated order, with soft's names and sorts.
2. `entailsX_mono`, `strict_of_withoutDefaults`, `basis_strict_sound` and `basis_needs_sound`: true as stated; the
   basis cannot be strict when a default premise is needed, and is `needs` only with a strict countermodel checked by
   `modelCheckX` on the document's own `X` (DF-α′: never `needs` without one).
3. `assumptions_sound`: the split of `premisesX U (defaultX D X) Γ` around `Dflt_T` matches RD-9's `premisesX` order
   (`background ++ X ++ Fill_T ++ elaborate ++ Γ`, with `Dflt_T` at the end of `X`).
4. `DefaultCoherent` is the gate D3 describes, and `defaultCoherenceCheck_sound` checks against the right list (no
   `Coh_T` in it).
5. `DefaultBase` and `DefaultCompletion` both minimise decisions with the unsaid tables varied and the facts, domain
   and constants fixed (D15). `replace_admissible` and `default_entails_minimal`: true under their hypotheses, with
   `replacementSafe` computed, not assumed; the proof route of 3.4 (`fill_extends` after replacing the decisions,
   `Exc_T`'s conditions over the unchanged facts, `Dflt_T` and `Exc_T` free of unsaid names) checks. DF-π's two
   `example`s are in the stub (draft 1's fixed-filling base is minimal, and it is not a default base). The
   counterexample that shows the gate is needed (DF-γ without `hcoh`: the left side holds vacuously at the collision,
   the right side does not) is in the stub. If the (→) proof is not confirmed, the fallback of 3.4 is recorded.
6. `defaultBase_of_dflt` needs no gate.
7. D5's refusal covers every regulated and decision predicate, and its text names the rule, not a generated name.
8. DE1 to DE12: one reading each; no non-wording; DE2 and DE2′ say who decides and what the text states. The long
   forms DE1′ and DE6′ and the form choice: `followsForm` is short only when every kept assumption is a bare exception
   (`followsForm_short`), so DF-ε and DF-δ get DE1′; DE6 only with `forced` empty, so DF-β (i) gets DE6′ with DE11;
   DE5 names the deciders; DE8 claims each reading's conclusion only under that reading's listed assumptions.
9. The fixtures of 4.1 as computed in the stub; P-1 to P-3 derived from `CE4`.
10. Conservativity: `defaultsCase_other`; F-DF0 to F-DF2. The non-vacuity conjunct of `defaults_certificate_sound`
    (FOLLOWS implies a checked situation where the premises hold with `Dflt_T`). DF-ρ's default-fold CONFLICT, with its
    expected English (DE7 per choice, never RD-9's contradiction wording), and no default member when the strict fold
    is not FREE.
11. Every batch's deletion list, and that no batch leaves a Python computation of anything section 3 defines.
12. DF-5's statements against WG-6 as reviewed, and `defaultZone_eq_noException` against weighing's Z-ε. The
    enumeration is over every typed open atom (`openAtomsAll`), observations and constraints included, `unknown`
    beyond `maxDefaultAtoms`; `cone_minimal_iff` is stated and no cone pruning is called before it is proved; DF-π′.

## 10. Shared pieces

Abstractions several topics could share. The cross-plan review decides owners; this plan's proposal is given for each.

| # | Piece | Who else needs it | Proposal |
|---|---|---|---|
| S1 | **The "no exception" record**: a situation's open decisions minimal (exceptions only where the facts force them, no switch on, no override), with the unsaid tables varied: circumscription of the decisions with the unsaid predicates varied, the facts fixed (D15), the same comparison as DF-2's `DefaultBase` | weighing (its record "assuming no exception applies", Z-ε; zone answers), attitudes (presumptions: "assume X unless …") | one definition, DF-5's `DefaultCompletion`, on WG-6's enumeration; weighing's record and its English become the instance (`defaultZone_eq_noException`, which needs the varied comparison, DF-π′); one sentence, owned once in the catalogue. Ownership against weighing's record: section 11, issue 2 |
| S2 | **`basis` on every answer that may rest on stated assumptions** (strict; needs, with a checked countermodel without them; or unsettled; and the list of assumptions used) | judgment-terms ("whatever the judgment" answers), weighing (zones under a record), attitudes, events (calendar completion), question answering | one response-shape member and one plain-English pattern ("This assumes …", and DE12 for unsettled), with each provider's assumption kinds as rows |
| S3 | **A view of a layered document's `X` split by pack** (`DefaultsView`: the soft pack, its exception and coherence parts, and the rest `R`, so that the gate reads `Exc_T ++ R ++ Dflt_T` and answers read `X ++ Dflt_T`) | PK-1; weighing records; judgment-terms' bounded judgments | PK-1 exposes each pack's premises, the soft pack's exception and coherence parts separately, and a typed "pack names no decision" flag; DF reads them and adds no pack row. Not in SYNTHESIS 2.1's `Pack`: section 11, issue 5 |
| S4 | **RD-9's generic fold over `ChoiceSem`** | DF-3 (`dSem`); weighing records across readings; judgment-terms | stays RD-9's; each topic adds an instance, never a fold |
| S5 | **Reading sets for frequency words** ("normally", "typically", "usually", "generally", "in most cases", "as a rule") | quantities (frequency candidate, QT-A6), soft-norms (deontic predicates), this plan (plain predicates) | one catalogue row per word in english-lean's catalogue, with the candidates supplied by soft, DF-4 and QT-A6 |
| S6 | **Presumptions** ("Claude should assume X unless …", "might reasonably trust … unless there's clear evidence …") | attitudes (typed "assume", "trust"), judgment-terms ("clear evidence", "evident from context"), soft (the default rule and its sufficient conditions) | no new construct: a soft default rule on an attitude act with sufficient exception conditions; DF answers it; attitudes owns the act |
| S7 | **Defeasible priority over data** ("later instructions take precedence, but not always", u0081.s05) | events (time order), soft (default rules), this plan (DF-4's rules about facts) | a default rule on a plain "prevails over" predicate with events' order in its guard; no priority logic of its own |
| S8 | **A "more specific than" check** (one rule's guard implies another's) | weighing (rank suggestions), scope (governed rules), IDE (W8) | one Lean entailment helper, used only as a suggestion, after DF-E3 |
| S9 | **The two-rule conflict sentence** (DE7; soft's weighing point; weighing's "left to") | soft-norms, weighing, this plan | one wording owned in the catalogue; each answer kind fills it |
| S10 | **"The question states facts only"** (D5's check) | question answering (what a question may state), weighing records (decisions fixed by the record, not the question) | one Lean check over a question's predicates, with each kind's allowed predicate classes as a parameter |
| S11 | **`usedLabels`** (which labelled premises a certificate needs) | DF (assumptions), readings (conditions), judgment-terms (which judgments an answer rests on) | stays in `Readings/Verdicts.lean`; others import it |

## 11. Cross-plan issues for the DRI

Checked against `SYNTHESIS.md` (owners O1 to O19, PK-1 in 2.1, the queues of 4.2) and `DRI-DECISIONS-PHASE2.md`, for
the shared owners this plan uses: weighing (WG-3, WG-6, WG-7; its PLAN draft 5 and spec draft 4 on
`research/weighing-p1`), readings-defaults' RD-9 (`rd-9/integrate`, not yet merged into `main` at `f98183bf`) and PK-1
(not started). SYNTHESIS reviewed seven other plans, so none of its owners was assigned with this plan in view. The DRI
decisions that touch this plan are applied in draft 2: SC2 and ET1 in DF-E2, ET2 in DF-4. The others (AP1 to AP4, AT1
to AT4, QT1 to QT3, SC1, SC3, ET3, ET4, ME1 to ME5, WG1) do not touch it. Seven issues need a ruling:

| # | Issue | Where it conflicts | Recommendation |
|---|---|---|---|
| 1 | **DF-5 needs an enumeration that WG-6 does not expose.** The agreed DF-5 enumerates every typed open atom of the situation, not the query's cone (D10, 3.6) | WG-6's reviewed functions (`coneValuesO`, `enumerateSettledO`, weighing-PLAN 3.4) enumerate the cone only, and SYNTHESIS O18 makes `NormDefaults/Evidence.lean`, owned by WG-6, the only place a three-valued enumeration may live. DF-5 may not write a second one | WG-6's statement review adds the atom list as a parameter of its enumeration, with the cone as today's argument (its answers unchanged, by `rfl`), and DF-5 passes `openAtomsAll`. Until then DF-5 is blocked |
| 2 | **Who owns "no exception".** S1 proposes DF-5's `DefaultCompletion` as the one definition, with weighing's record "assuming no exception applies" as its instance and one sentence in the catalogue | Weighing's plan (draft 5, 2.6) owns its record and its sentence ("assuming no rule's exception applies here") and does not mention this plan. The two differ where a stated sufficient condition holds (weighing: the record is "ruled out"; DF: the exception is forced and the rest minimal) and on switches and rankings (weighing leaves them open; DF turns switches off and keeps the ranking). They agree under `defaultZone_eq_noException`'s hypotheses. S9 (DE7 against weighing's "left to") has the same question | DF owns the comparison (D15), `DefaultCompletion`, DE10 and DE11; weighing keeps its record and its sentence as a separate, user-chosen record, proved equal to DF's answer where `defaultZone_eq_noException` applies; the catalogue holds one row per wording. The DRI decides whether weighing's record sentence is later rendered from DF's |
| 3 | **DF-4 has no slot in the English queue, and three plans write rows for the same words.** D13's reading-set row for "normally", "typically", "usually", "generally", "in most cases" and "as a rule" on a plain predicate needs QT-A6's frequency candidate | SYNTHESIS 4.1 step 7 and 4.2 serialise `lean/VE/EnglishGrammar/*` (AP-1's hunk, then AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7; ET-5 and WG-4 in landing order); DF-4 is not in it. Weighing's edit 10 puts soft's reading sets for the same words (deontic predicates) in the same catalogue | DF-4 joins the queue right after QT-A6, so that each word's row is written once with every candidate (soft's, DF-4's, QT-A6's), never with a pending candidate a later batch rewrites. DF-4 then waits on QT-E, which gates QT-A6, later than step 4 of the batch order; DF-E2 moves with it. The alternative is landing order with the frequency candidate pending (W2), which D13 allows |
| 4 | **DF's edits to queued shared files have no place in SYNTHESIS 4.2** | DF-1a and DF-5 add kind rows to PK-1's layered kind table (`Layered.lean` or `Packs.lean`); DF-1a appends four rows to the layered route's response-shape files, which WG-7 also extends (weighing edit 3); DF-1b and DF-3 edit `ve/document.py` or the Lean document mode (queue: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10); DF-3 adds one dispatch line to RD-9's `Readings/SoftVerdicts.lean` | Add DF-1a and DF-5 to the `Layered.lean`/`Packs.lean` row after PK-1, as kind rows in landing order (no pack line); DF-1b and DF-3 to the document-mode queue in landing order; the response-shape rows and RD-9's dispatch line in landing order, generated files regenerated with `tools/regen_generated.py`, never hand-merged |
| 5 | **S3 asks PK-1 for more than SYNTHESIS 2.1's `Pack` has** | S3 proposes that PK-1 expose the soft pack's exception and coherence parts separately and a typed "names no decision" flag; SYNTHESIS 2.1's `Pack` has `labelled` and `origins` only | No change to PK-1. DF does not need it: the gate reads soft's own `excPremises D` (3.2), `R` is X after the soft pack (soft is first in `packOrder`, `assemble_order`), and decision-freeness is DF's computed `decisionFree` and `replacementSafe`. S3 is withdrawn as a request and stays a description of `DefaultsView` |
| 6 | **`Dflt_T` on the superposed readings route** | DF-3 runs on RD-9's enumerated route only (at most 64 choices). Weighing's spec (draft 4, section 6) records that the constitution's translation is under `readings@1` and needs the superposed route, where each pack proves `Transfers` (PK-1 provider obligation 4). `Dflt_T` is not a pack, so no obligation covers it, and DF-3 cannot measure default answers on that translation | No batch now: DF-3 measures on `CE4` and enumerable documents and says so (DF-3's pilot line). A later batch proves `Transfers` for `Dflt_T` with PK-1's `transfers_append`, only if the pilot needs default answers across the constitution's readings; whether DF or PK-1 owns that proof is the DRI's call |
| 7 | **PK-1's witness rule and DF's collision witness** | PK-1 guarantees that every reported witness or countermodel satisfies the whole assembled X (SYNTHESIS 2.1, C3). DF's collision witness (`collisionCheck`, shown by DE7) is by design a base where `Exc_T`, every other pack's premises and `Dflt_T` hold and one soft coherence premise fails, so it does not satisfy X's coherence part. DF's countermodels (`defaults-model`) do satisfy the whole X with `Dflt_T` | PK-1's guarantee is worded for countermodels and admissible witnesses, and names the collision witness as the one kind checked against X without the soft pack's coherence premises, which DE7's English already states ("conflict here unless one of them gives way"). If the DRI wants the rule unqualified, DE7 drops its situation and names only the two rules and the tuple |
