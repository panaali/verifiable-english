# Weighing competing considerations and holistic judgment: research

> Status: research note, draft 1 (2026-10-12), branch `design/weighing` from `main` at `49de179e`; DRI research wave of
> 2026-10-12. Written before the plan, [docs/spec/weighing-PLAN.md](../spec/weighing-PLAN.md), which builds the design
> recommended in section 6. Docs only: no code, proof, test or generated file changed, and no model was called. Every
> number is either measured, with the method named beside it, or labelled *estimate*. Citations of the pinned
> constitution are by source line (`:n`) and by unit id of the run `20261012T1800Z` ledger.

## 0. The question, and the short answer

The constitution's largest blocker is normative language: 669 of its 1,074 UNFORMALISED units (62%) carry `norms` as
their primary blocker (`metrics.json`, `missing_feature_tally`). Much of that language weighs: four values in an order
that is "holistic rather than strict" (:34), costs against benefits (:325-347), operators against users (:134-139),
"in most cases", "all things considered", and the authority to switch a default off.

VE already has the right stance, merged and proved: `soft-norms@0` turns every weighing into **named open decisions**
(is this rule's exception met here; does the lower-ranked consideration outweigh the higher one here; has this party
switched the rule off), each with a named decider, and the checker certifies the structure around them: which rules
can collide, which collisions the ranks resolve, what the deciders' findings must satisfy for the rules to be jointly
followable, and that hard constraints are never weighed. It does not compute the weighing, and it should not.

This note measures how far that structure reaches on the real text, what it cannot say, and what a checker can
honestly certify about a weighing it does not perform. The short answer:

- **The constitution cannot use soft norms today at all**, for a reason unrelated to weighing: `ve document` refuses
  `soft-norms@0` beside `norm-defaults@0`, which the translation needs. RD-9 (building) removes that refusal. Until it
  lands, no weighing feature moves a pilot number.
- **What soft norms already express covers the frame of the value order** (ranks, the holistic flag, hard
  constraints, switches, factor lists). Five things the text says are missing: how strong a priority step is ("even
  if Claude is confident", :40), conditions on an override, conditions on a switch and delegated switches (:138),
  collisions between *different* acts ("help" against "refuse"), and a choice of the best response among options.
  The first three are buildable now as conditions on open decisions, without new semantics. The last two are research.
- **What a checker can certify about a weighing it does not perform**: that the weighing is needed at all at a given
  situation (or that every admissible way of deciding gives the same answer), which named questions the answer turns
  on, and whether a recorded judgment stays inside the document's bounds. These "zone" answers are buildable now on
  norm-defaults' three-valued machinery.
- **What stays residual forever**: the findings themselves, whether the decider weighed what it should, and "the
  spirit of the document" (:44).

## 1. What VE already has

### 1.1 Merged on `main`

| Piece | What it gives weighing | Where |
|---|---|---|
| `norms@0` (W1) | strict rules with exception trees (Catala-style precedence `over`), completions, conflict checking with witnesses | [norms.md](../spec/norms.md), `lean/VE/Norms/*` |
| `soft-norms@0` | default rules (`should`, `generally may`) with an open exception `excepted_N` and a decider; sufficient and necessary exception conditions; factor lists; ranks (`Rule n serves <rank>`, `<a> outranks <b>`, declared ties); the strict or holistic flag with open `outweighs_{act,L,H}` findings; switches (`(users may turn off)`) with attribution of instructions to parties; derived `hard` rules; the coherence premises `Coh_T`; per-pair classification RANK-RESOLVED / DISJOINT / WEIGHING POINT / UNKNOWN; conflict-freedom conditional on coherence | [soft-norms.md](../spec/soft-norms.md); `lean/VE/SoftNorms/*`; every theorem of its section 9 proved ([lean/SOFT-NORMS.md](../../lean/SOFT-NORMS.md)); switched to Lean first by lean-first batch lf-6 (merged 2026-10-07) |
| Proved properties used here | `soften_faithful`, `hard_over_soft`, `hard_never_weighed` (strict selection reads no weighing symbol), `rank_resolves`, `eligible_effective`, `weighing_points_complete`, `soft_conflict_decomposition`, `authority_independent` (declared attribution only) | `lean/VE/SoftNorms/{Semantics,Coherence,Status}.lean` |
| `norm-defaults@0` | the `unspecified` completion: SETTLED yes / SETTLED no / UNDECIDED ("the text does not say"), with Kleene evaluation, cones and bounded enumeration in Lean (`kleene_sound`, `settled_of_enumeration`); a soft branch (`Layered.lean`: `fill (soften D)` with soft's premises as extra base premises `X`) for the elaborate, conflict, status and report kinds; `excepted_lifts`: where a default rule's exception holds on an unspecified act, the act is unsaid | [norm-defaults.md](../spec/norm-defaults.md); `lean/VE/NormDefaults/*` |
| `readings@1` | reading sets in translation; per-choice checking (64 choices); separation; "force twins" (the strict and default readings of one "should") | [readings-defaults.md](../spec/readings-defaults.md) |
| `rights@0` | claim-rights correlated onto soft rules | [rights.md](../spec/rights.md) |
| `alternatives@0`, `risk@0` (stage A) | choosers with explicit alternatives, followability (FOLLOWABLE / DILEMMA), harm classes ordered by severity with a named decider, "has a less severe worst case than", decision records for one choice; **not combinable with `soft-norms@0`** (refused at profile validation) | [alternatives.md](../spec/alternatives.md), [risk.md](../spec/risk.md) |
| Open-term schema | named open predicates with a decider, necessary and sufficient conditions, factors | [document.md](../spec/document.md) |

### 1.2 Building

- **RD-9, the soft chain under the completion** (`rd-9/lean`, `rd-9/integrate`, `rd-9/py`; plan
  `docs/spec/rd-9-soft-chain-PLAN.md` on `design/rd-9`). It lets a soft document sit beside `norm-defaults@0` and
  `readings@1`: generic extra premises `X` on the layered route (`EntailsX`, `acceptanceX`,
  `conflictFreeCheckX_sound`, `modelCheckX_sound`, read on `rd-9/integrate`), the layered branch's certificate and
  admission kinds (SC-6), `ve document` on such documents (SC-8), and the constitution's four "should" sets rewritten
  as real default rules (SC-9). RD-9 says plainly what it does not give: with no exception conditions on the four
  sets, their default readings mean what today's workaround means.
- **The research wave's siblings** (DRI decision 2026-10-12): `attitudes` (knowingly, intends, "thinks it quite
  likely"; `design/attitudes`), `act-phrases`, `quantities` ("serious uplift", "vast majority"), `events-time-causation`,
  `scope` and `math-evidence`. Boundaries with this note: typed attitudes inside a hard constraint's guard are
  `attitudes`; "most", "rarely", "very high bar" as frequencies or degrees are `quantities`; act identity ("is ignoring
  an instruction the same act as not complying with it?") is `act-phrases`; inaction and preventable harm are
  `events-time-causation`. Weighing uses their results as guards and act identities and owns none of them.

### 1.3 Planned only

- soft-norms-PLAN items 5 to 7: coverage residual lines (partly present: the Lean route reports `weighing_points` and
  `override_cycles`), the W8 authoring hooks, and the pilot re-run with a split-only baseline and blind review. Item 7
  never ran: the pilot's main document has never enabled `soft-norms@0` (measured: `metrics.json`,
  `document_profiles.main`).
- soft 4.5's "stage 3": collisions between different acts ("help with the request" against "refuse the request").
- NORTH-STAR's unranked row "Action alternatives / priority across different obligations" (planned, no estimate),
  and its row 1, "Soft norms, weighing, authority to override" (0 to 124,480 B on the constitution, an upper bound at
  older unit boundaries).
- VISION's research track: "defeasible 'normally'".

### 1.4 Why the constitution does not use soft norms today (measured)

The main translation's profiles are `documents@1`, `norm-defaults@0`, `norms@0`, `readings@1`, `relational-fol@0`
(`metrics.json`, `document_profiles`). Adding `soft-norms@0` is refused with `UnsupportedProfile: norm-defaults@0
documents on the soft and rights routes await the Lean route` (`profile_combination_probe`; the refusal is
`ve/document.py:618-622`). So the four "should" sets carry their default reading as a strict rule plus an `unless`
over a named open term, and every ranked or holistic sentence stays UNFORMALISED. This is RD-9's work (1.2), and every
pilot-moving batch of this plan waits for its SC-8.

## 2. The need, measured

MEASUREMENTS-PENDING

## 3. Prior art

Marks: *(unsure)* where a date or detail is from memory and not checked.

### 3.1 Prima facie duties and weighing in ethics and law

- **Ross, *The Right and the Good* (1930)**: prima facie duties that can be overridden, and the duty proper "all
  things considered", reached by judgment, not by rule. This is exactly the constitution's picture; Ross gives no
  procedure for the weighing, and neither should a checker.
- **Raz, *Practical Reason and Norms* (1975)**: exclusionary reasons, reasons not to act on certain other reasons.
  The hard constraints' "rather than being weighed against other considerations, they act more like boundaries or
  filters" (:445) is an exclusionary structure; soft's `hard_never_weighed` is its formal counterpart.
- **Dancy, *Ethics without Principles* (2004)**: particularism, the view that holistic judgment cannot be codified.
  It is the honest limit for VE: the residual of section 5.3 is what particularism says stays uncodified.
- **Alexy's weight formula** (*A Theory of Constitutional Rights*, English 2002; "On balancing and subsumption",
  *Ratio Juris* 2003): proportionality balancing with an ordinal three-step scale (light, moderate, serious) turned into
  numbers. Right: weighing has structure (the importance of each side, the reliability of the premises). In conflict
  with VE: the numbers are a model choice the source never makes; in translation they would be invented precision.
- **Chang (ed.), *Incommensurability, Incomparability and Practical Reason* (1997)**; **Sen, "Maximization and the
  act of choice", *Econometrica* (1997)**: when options are incomparable, a rational choice is a *maximal* one (no
  option better), not an optimal one. This is the shape of "choose a response that no alternative beats" in 4.7.

### 3.2 Defaults and priorities in logic

- **Reiter's default logic (1980)**; **McCarthy's circumscription (1980) with abnormality predicates (1986)**. VE's
  `excepted_N` is McCarthy's abnormality predicate, but left open with a decider instead of minimised. That is the one
  design difference that keeps VE monotone and its certificates checkable.
- **Poole's Theorist (1988)**: defaults as hypotheses, an explanation is a consistent set of assumed hypotheses. The
  closest prior art to VE's `conditional_on` lists and to the "assuming no exception applies" record of 4.2.
- **Brewka, preferred subtheories (IJCAI 1989) and prioritized default logic (1994)**; **Horty, *Reasons as Defaults*
  (2012)**: priorities among defaults, conflicts resolved by priority, several "proper scenarios" where priorities run
  out, and variable priorities derived by defaults. Horty's scenarios correspond to VE's decision assignments and his
  proper scenarios to coherent ones; his credulous/skeptical choice is exactly what VE refuses to make silently (it
  becomes `left to` or a reading set).
- **Defeasible logic**: Nute (1994); Antoniou, Billington, Governatori and Maher, "Representation results for
  defeasible logic", *ACM TOCL* (2001); Governatori and Rotolo on reparational obligations (2006). Rules with a
  superiority relation, polynomial for the propositional case, with variants that declare *conflicting literals*
  beyond complementary pairs *(unsure which paper introduced the declaration)*: the precedent for 4.1's exclusive acts.
- **Argumentation**: Dung (1995); ASPIC+ (Prakken 2010; Modgil and Prakken, *AIJ* 2013) with rule and premise
  preferences; value-based argumentation (Bench-Capon 2003), where arguments promote values and an *audience* ranks
  the values. Right: conflicts and priorities are first-class, and audience-relative orders mirror reading sets over a
  rank order. In conflict with VE: acceptance is non-monotone and depends on the absence of attackers, so a checker
  would have to certify a negative; extensions are many and choosing a semantics is choosing a reading.
- **Reason-based logic and accrual**: Hage, *Reasoning with Rules* (1997); Verheij (1996); Carneades (Gordon, Prakken
  and Walton, *AIJ* 2007) with proof standards and weights. Right: "weigh reasons for against reasons against" is
  modelled as an explicit, open step. Carneades' weights are numbers; Hage's weighing is a primitive judgment, which
  is VE's `outweighs`.
- **Deontic logic**: von Wright (1951), Chisholm's contrary-to-duty paradox (1963), Hansson's preference semantics
  (1969), Goble's conflict-tolerant systems (Handbook of Deontic Logic, 2013), Horty, *Agency and Deontic Logic*
  (2001). Right: "ought" can be read as "best among the available options", the basis of 4.7. In conflict with VE:
  modal semantics would be a new consequence relation in the checker (VISION's converged rule, item 5).

### 3.3 Precedent and factors in AI and law

- **HYPO** (Ashley, 1990), **CATO** (Aleven, 1997 *(unsure of year)*), and the formal accounts of **precedential
  constraint**: Horty, "Rules and reasons in the theory of precedent", *Legal Theory* (2011); Horty and Bench-Capon,
  "A factor-based definition of precedential constraint", *AI and Law* (2012); Prakken, "A formal analysis of some
  factor- and precedent-based accounts of precedential constraint", *AI and Law* (2021) *(unsure of year)*. A decided
  case with its factors constrains later decisions a fortiori: a case at least as strong for the same outcome must
  be decided the same way. This is decidable, needs no weights, and constrains a decider by its own record without
  performing the weighing: the best-fitting prior art for "what a checker can certify about a weighing it does not
  perform". It compiles into exactly the necessary and sufficient conditions VE already has (plan WG-9).

### 3.4 Controlled languages, legal DSLs, proof assistants

- **Attempto Controlled English** (Fuchs, Kaljurand and Kuhn, 2008): one reading per sentence by interpretation
  rules, monotone first-order logic, no defaults and no weighing. Kuhn's survey of controlled natural languages
  (*Computational Linguistics*, 2014) finds no CNL with holistic weighing.
- **PENG and PENG-ASP** (Schwitter 2002; 2013; Guy and Schwitter 2017 *(unsure)*): defeasible "normally" through
  answer set programming's negation as failure. Right: readable defaults. In conflict with VE: the conclusion depends
  on what is not stated, which is the "silent choice" VE refuses; VE writes the exception as an open decision instead.
- **Logical English** (Kowalski, 2020; Kowalski and Datoo, *AI and Law* 2022): legal English over logic programming,
  defaults by negation as failure; same contrast.
- **Grammatical Framework** (Ranta, 2004, 2011): multilingual grammars, no reasoning about norms.
- **Catala** (Merigoux, Chataing and Protzenko, ICFP 2021), after Lawsky's default logic for tax law (2017): a default
  calculus where exceptions carry explicit priorities and two applicable exceptions with no priority are a **runtime
  conflict error**. Right: priorities are written, never guessed. VE differs in one place: an unprioritised collision
  is a WEIGHING POINT, named and left to a decider, not an error, and the conflict check is conditional on the
  decider's coherence.
- **LegalRuleML** (OASIS; Athan, Governatori, Palmirani, Paschke and Wyner, 2013-2015 *(unsure of the standard's
  year)*): defeasible rules, an `overrides` relation, reparations, and **authority** metadata (who issued a rule).
  Right: authority is metadata on rules, as VE's `instruction_of` and switches are. It specifies no checker.
- **s(CASP)** (Arias et al., *TPLP* 2018) and Blawx *(unsure of dates)*: goal-directed answer set programming with
  English justifications; non-monotone.
- **LogiKEy** (Benzmüller, Parent and van der Torre, *AIJ* 2020): deontic logics embedded in Isabelle/HOL to build
  "explicit ethical reasoners". Right: a proof assistant checks normative reasoning. In conflict with VE: the logic is
  chosen per theory and readers see formulas, not English.

### 3.5 AI value specifications

- **Constitutional AI** (Bai et al., 2022): principles used by a model to critique its own outputs; nothing checks the
  principles' structure. **The instruction hierarchy** (Wallace et al., 2024) and the **OpenAI Model Spec's chain of
  command** (2024): a priority among principals, trained into the model. Right: authority to override is central to
  an AI's specification. VE's contribution is to make that authority a checked structure (switches, attribution, the
  delegation bound of 4.1) rather than a trained disposition.

### 3.6 What carries over, and what conflicts with VE's constraints

| Idea | Keep | Conflict with VE |
|---|---|---|
| Abnormality predicates, Theorist's assumptions | yes: `excepted_N` open with a decider; `conditional_on` | minimising them silently (circumscription, negation as failure) is a silent choice |
| Priorities among defaults (Brewka, Horty, defeasible logic, Catala) | yes: ranks, `over`, the flag | none, while collisions are on one act |
| Conflicting-literal declarations | as an experiment (4.1 c) | changes `ValueSoft`: a new profile |
| Argumentation semantics | no | non-monotone acceptance; many extensions; certificates of absence |
| Numeric weights (Alexy, MCDA, Carneades) | no | invented precision in translation; symbols in what people read |
| Factor-based precedent | yes, as an experiment (4.3) | none: it compiles into existing conditions |
| Maximal choice under incomparability | research (4.7) | needs alternatives combined with soft norms |
| Authority as rule metadata (LegalRuleML, instruction hierarchy) | yes: switches, grants, attribution | a general authority logic would be new semantics |

## 4. Candidate designs

Each candidate is judged against VE's constraints: **one reading** per sentence (ambiguity in a source becomes a
reading set, never a silent choice); **zero-training English** (no symbols, precision machinery hidden by default);
a **small Lean core** that grows only by proved conservative extensions; **honest UNKNOWN**; and **open-textured words
stay named open terms** with a decider.

### 4.1 Candidate A: constrain the open decisions

Keep soft's stance and add sentences that **constrain** its open decisions, each elaborated into a labelled base
premise appended to the layered route's extra premises `X`:

- (a) **Strength of a priority step**: "Safety always outranks ethics." against "Ethics generally outranks
  guidelines." A rank pair is strict when some chain of declared steps between them contains an `always` step; a
  strict pair forbids the `outweighs` finding for every act its rules collide on. Per-step strictness alone would let
  guidelines outweigh safety while ethics cannot, which no reader expects; the closure rule is one sentence a reader
  can apply ("a lower rank can outweigh a higher one only if every step between them says *generally*").
- (b) **Conditions on an override, and on a switch**: "<l> outweighs <h> on <act> only when …" (necessary), "… when
  …" (sufficient), "<party> may turn off rule n only when …", with factor lists. These are soft's exception conditions
  applied to the other two kinds of decision.
- (c) **Delegated switches** (:138): "Users may turn off rule n only where the operator allows it", with a checked
  bound: a grantor must itself hold the switch it grants.
- (d) Extension, research only: **exclusive acts** ("Helping with a request and refusing it are exclusive"), so that
  rules on *different* acts can collide and ranks can resolve them. Unlike (a) to (c) this changes `ValueSoft`'s
  blocking and dominance steps, so it is a new semantics with its own faithfulness theorem.

| Constraint | (a)-(c) | (d) |
|---|---|---|
| One reading | each wording has one paraphrase; "always"/"generally" are not synonyms of plain "outranks", which keeps the document flag's meaning | one reading, but which acts are exclusive is a translator's reading set |
| Zero-training English | plain sentences; no names of decisions shown | plain |
| Small Lean core | premises only; RD-9 already proves the checkers sound for any typed `X`; new proofs: typing, meaning of the premises, conservativity | new semantics, new faithfulness proof |
| Honest UNKNOWN | unchanged | unchanged |
| Open terms | conditions are base formulas; open words in them stay open terms | unchanged |

### 4.2 Candidate B: answer where the weighing matters (zone answers and decision records)

Add no syntax. At a situation, for an act, Lean answers **settled** (every admissible way of taking the open decisions
gives the same answer), **left to** a named decider (two admissible ways differ, with the same filling of the text's
gaps; the questions are named in document terms), **not said** (norm-defaults' UNDECIDED), or **unknown** with the
budget. A **decision record** (a decider's findings) is checked the same way with the findings fixed: admissible, with
the answer it gives, or ruled out by a named sentence. "Assuming no exception applies" is the record that sets every
exception false, which is the honest form of a presumptive "normally" conclusion (Theorist, 3.2).

Constraints: one reading (no new sentence); zero-training English ("Left to the assistant: this depends on whether
rule 12's exception applies here"); Lean: the open set of norm-defaults' Kleene evaluation and enumeration widens from
unsaid atoms to unsaid and decision atoms, in its owner file, with today's functions as the special case; UNKNOWN is
the budget's answer; open terms untouched. This is what the checker can certify about a weighing it does not perform.

### 4.3 Candidate C: precedents bind the decider

Worked examples become **precedents** of one open decision: the factors present (with their polarity, from the
source's own factor lists) and the outcome. By the result model of precedential constraint (3.3), each precedent
compiles into a necessary or sufficient condition (a case at least as strong for the outcome must have it), and the
precedent set is checked for consistency. Constraints: one reading per precedent, but choosing the factors of a prose
example is interpretation, so each precedent is an attributed unit and a reading set where readers differ; plain
English ("The household-chemicals example is decided as: help, because …"); Lean: compiled premises join candidate
A's conditions, plus one decidable consistency check; open terms stay open. Risk: inventing factors. Hence an
experiment first, with a bar that fails on any invented factor (plan WG-E2).

### 4.4 Candidate D: a defeasible-logic engine inside the checker

Compute conclusions of prioritized defaults (defeasible logic with superiority and conflicting literals, or ASPIC+)
inside the checker, so "normally X" yields X unless a defeater is shown. Constraints: one reading fails twice (the
choice of semantics, and the silent closure "no defeater is stated, so none applies"); the core grows by a new,
non-monotone consequence relation, against the converged rule's item 5 ("non-monotone systems enter only as sealed
content"); a NO answer would need a certificate that no defeater applies, which is a certificate of absence. Rejected
for the core. A sealed sibling checker remains possible later if a pilot needs an inference that elaboration cannot
give (the converged rule's item 3), and nothing here measures such a need.

### 4.5 Rejected without a candidate

- **Numeric weights** (Alexy's formula, multi-criteria analysis, Carneades' weights): the source never gives numbers,
  so in translation they are invented precision; in authoring they would be symbols in what people read. An author who
  wants an order writes ranks; one who wants grades writes ranks with "always" and "generally".
- **A reading set over orders for "holistic"**: "the text leaves it to Claude" is not "the text could mean A or B".
  Ambiguity of the text and discretion granted by the text are different things in VE (reading sets against open
  decisions), and conflating them would misstate the source.

### 4.6 Authority beyond switches

The constitution's authority structure (:134-139, :405-423) is switches with conditions and delegation, which
candidate A covers. A general logic of authority (who may change which norm, by which act, with what nested
permissions) is not needed by the measured text and is not proposed.

### 4.7 Research frontier: the best response among options

"Claude should try to identify the response that correctly weighs and addresses the needs of those it is helping"
asks for a **maximal** response among alternatives under an open comparison "is better than" (3.1, Sen). A checker
could certify that, under declared coherence of the comparison (irreflexive, transitive), a maximal option exists at
every choice (as `risk@0`'s `precaution_has_maximal` does for severity), that rank-dominance conditions on the
comparison are respected, and that a recorded choice is maximal relative to recorded comparisons. It needs
`alternatives@0` combined with `soft-norms@0`, which is refused today, and explicit alternatives for abstract policy
text, which the constitution does not enumerate. Research; no batch in this plan.

## 5. Buildable, research, residual

RESIDUAL-PENDING

## 6. Recommendation

Build candidates A (a) to (c) and B, as one new profile; test candidate C and 4.1 (d) by experiment first; keep
candidate D out of the core. The plan, [docs/spec/weighing-PLAN.md](../spec/weighing-PLAN.md), builds this. Its draft 1
was reviewed by Astra and Fable (`manage-agents/debates/design-weighing/`, converged in round 3 on REVISE) and by the
cross-plan review of 2026-10-13 (`manage-agents/debates/plan-synthesis/SYNTHESIS.md`); draft 2 carries both, and the
recommendation below is the one they converged on.

1. **First, with no product code: the value order in today's `soft-norms@0`** (plan WG-0). Ranks, the holistic flag
   with its decider, and the hard constraints' immunity, written once RD-9's SC-8 lets a soft document sit beside
   `norm-defaults@0` (1.4). This is the first step that can move a pilot number. Its effect is measured by WG-0, not
   estimated here: section 2 is not filled, and the plan withdrew the estimates that cited it.
2. **Candidate A (a) to (c) as `weighing@0`** (plan WG-2 to WG-5): `always` on a rank edge, necessary and sufficient
   conditions on an override, necessary conditions on a switch, and delegated switches. Each is a labelled premise on
   an open decision that already exists, in the `weighing` pack of the layered route's extra premises `X`; `ValueSoft`,
   `soften` and `fill` are unchanged. The review narrowed the candidate in four places:
   - "generally outranks" is an input synonym of a plain "outranks", and only `always` edges are on the wire, so every
     construct has a formal effect;
   - weighing constrains decisions, never the world: a condition on a strict pair is refused, a sufficient condition
     must be shown to imply each necessary condition on its target, and a switch takes no sufficient condition;
   - a grantee's switch carries every condition on the grantor's own switch along the whole grant chain, which is
     what :138 means and what the structural bound alone does not give;
   - the guarantee is that the weighing premises alone never constrain the world (`weigh_alone_base_free`), not
     conservativity: through soft's coherence, conditions can leave a situation with no admissible decision, and the
     answer then says "inconsistent at this situation".
3. **Candidate B: zone answers and decision records** (plan WG-6 to WG-8), as two kinds of the layered route rather
   than a new service mode, on norm-defaults' three-valued machinery widened in its owner file. "Settled" is claimed
   only with one admissible completion checked, the enumeration discards what the whole `X` refutes, and "left to" and
   "not said" are kept apart and reported together where both hold.
4. **Experiments with bars fixed before any data is read** (plan WG-E1, WG-E2). Precedents (candidate C) are built
   only if every worked example can be written with factors the source lists, the precedents are consistent, and the
   compiled conditions force at least half of the held-out outcomes and contradict none. Collisions between different
   acts (4.1 d) are built only if enough sampled units need them and they would change a checked answer, and then as
   `alternatives@0` composed with soft norms (plan WG-10), never as an exclusivity relation of weighing's own.
5. **Not recommended**: candidate D inside the checker (4.4), numeric weights and a reading set over orders (4.5),
   and a general logic of authority (4.6). The best response among options (4.7) stays research.

**Why.**

- **It adds what the text says without new semantics.** A's sentences are premises, and RD-9 already proves the
  checkers sound for any typed `X`, so the new proof obligations are typing, the meaning of the premises and the local
  checks. B adds no sentence at all. Candidate D and 4.1 (d) would each add a semantics with its own faithfulness
  proof; D's would be non-monotone and need certificates that no defeater applies.
- **It keeps discretion as discretion.** The source grants judgment (:34); the design names each decision and its
  decider and bounds what the decider may find, instead of choosing a weighing the source never states (D, numeric
  weights) or misreading granted judgment as ambiguity (4.5).
- **B is what a checker can honestly certify about a weighing it does not perform**: whether the weighing matters at
  all, which named questions the answer turns on, and whether a recorded judgment stays inside the document's bounds.
  It also corrects a wrong message today: the unclear cases :457 sends to holistic judgment come out "the text does
  not say", where the right answer is "left to the assistant".
- **The order follows the dependencies.** Nothing moves a pilot number before RD-9's SC-8; WG-0 needs no code; A
  comes before B because A is what the constitution's translation writes (WG-5) and B reports answers on the result
  (WG-8).
- **The two extensions wait on evidence** because their need is unmeasured: the cross-act class of section 2 is not
  yet written, and a precedent is only as good as its factors, so the experiments fail on any invented factor.
