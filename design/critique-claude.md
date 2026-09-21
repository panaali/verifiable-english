# Critique of PLAN.md experiments E0-E6 (Worker C)

## 1. Three most serious flaws, and fixes

**F1. Model judges read FOL natively, so the central contrast is confounded with judge competence, and
"weak" is only assumed.** VE's surface exists for readers who cannot read `∀x(D(x)→∃y O(y,x))`. Haiku and Luna can.
A null in E1 then says nothing about VE, and a positive result may be a tokenisation or prompt-format effect.
Also, nothing in the plan shows that the weak judges are actually worse than the attackers on these items; without
that gap there is no sandwich. *Fix:* (a) a gate before E1: measure each judge's unaided accuracy on the dev split
and keep only judges with a measured gap to the strong models, reported as such; (b) treat rendering as a
*presentation* factor with a fixed prompt template, and add a nuisance-format control (FOL with verbose ASCII
keywords, `forall service x0. ...`) so "English words" is separated from "not symbols"; (c) state the claim as
"for model judges of measured capability c", never as readability.

**F2. The attacker and the item generator share a model family with the judges, and the attacks are optimised
against nothing.** A weakening written by Fable is validated only for semantic difference, not for difficulty. If
attacks are easy, every condition hits the floor on false approval and the contrasts are empty; if the attacker sees
which view the judge gets, conditions differ in attack strength. Self-preference also cuts both ways: a Claude judge
may approve Claude-written explanations. *Fix:* generate each attack once, blind to condition, and reuse it across
all conditions (paired by item). Calibrate on dev so raw-FOL false approval is 30-60%, freeze the attack
recipe, then regenerate on scored items. Include a mechanical attack family (quantifier swap, dropped conjunct,
antecedent strengthening, argument reversal, vacuous domain) that owes nothing to either family. Report every
contrast per judge and per attacker family; pool only when the per-judge signs agree.

**F3. Several experiments are true by construction, and the forking paths are wide.** E2's "review cost stays flat"
is guaranteed when the judge sees a constant-size checker result; E4's checked countermodel is correct by
construction, so a judge who simply trusts the label scores perfectly. Those measure prompt compliance. With seven
experiments, two views, two scenario settings, and four judges, some contrast will come out "significant". *Fix:* each
PREREG names one primary contrast and one refutation condition; everything else is labelled exploratory. E2 must
put the error where the checker cannot see it (a false leaf premise or a wrong specification) in half the items, so
the VE arm can fail. E4 must include dishonest critics with *valid-looking but unchecked* countermodels and measure
whether the judge distinguishes checked from asserted. Verdict parsing failures count as wrong for the condition's
worst case (rejection of good, approval of bad), not dropped.

## 2. Most likely to show a benefit, and to refute

**Benefit: E1, the contrast VE-strict versus FOL + untrusted explanation.** This is the one place where
determinism does work that a better prompt cannot do: the attacker's explanation can assert the faithful reading
while the formula says otherwise. I expect a real drop in false approval there. I do not expect VE to beat raw FOL.

**Refutation: E1, VE versus raw FOL, and E5.** If raw FOL matches VE for model judges, the English surface has no
demonstrated value in the only setting we can test. E5 is the likeliest *harm*: a "proof checked" label should
raise approval of badly grounded arguments, since models defer to authority markers. E3's merged-vocabulary variant
is a known blind spot by construction and will show zero benefit; report it as a limit, not a finding.

## 3. Datasets (licences to be confirmed from files in `experiments/E0/SURVEY.md`)

- **FOLIO** (CC-BY-SA-4.0, ~1.4k stories with gold FOL). Premises are already NL + FOL pairs: the NL sentence is the
  "intended requirement", the gold FOL imports to v0 (single sort `entity`; items with arity above 2 or functions
  count as no-fit in E0). Contamination risk is high, so E1 uses FOLIO only for sentences, with fresh attacks.
- **ProofWriter** (CC-BY-4.0). Unary/binary Datalog-like rules; near-total fit; supplies E2 derivations with known
  depth and E4 invalid inferences (OWA split only, since v0 entailment is classical).
- **Cedar examples** (Apache-2.0) and **Alloy models**. Principal/action/resource map to sorts and binary
  relations; string and numeric conditions become opaque predicates, which E0 must count separately.
- **Synthetic v0 generator** (ours): the only contamination-free source, and the main scored set for E1.

## 4. Add and cut under the budget

At roughly 0.8 s effective per call with concurrency 6, six hours gives at most about 25k calls; plan for 10k.
**Cut E6** (debate rounds; least VE-specific, most tokens) and **fold E3 into a small exploratory demo**.
**Shrink E2** to three sizes (4, 32, 256) with 40 items each. **Spend the budget on E1**: 200 scored items x 6
conditions x 2 judges = 2.4k calls, plus the same with scenarios. **Add E1b, a comprehension control**: with no requirement shown, the
judge says whether the formal text holds in each of two small finite models, scored by the evaluator; this separates
comprehension of a view from approval bias. Keep E5 (cheap, 600 calls, honest harm test)
and E4 with the dishonest-critic arm.
