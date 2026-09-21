# Critique of PLAN.md experiments E0-E6 (Worker C)

## 1. Three most serious flaws, and fixes

**F1. Model judges read FOL natively, and "weak" is only assumed.** VE's surface exists for readers who cannot
read `∀x(D(x)→∃y O(y,x))`. Haiku and Luna can, so a null in E1 says little about VE and a positive result may be a
prompt-format effect. Nothing in the plan shows the weak judges are actually worse than the attackers on these
items; without that gap there is no sandwich. *Fix:* (a) gate E1 on a measured dev-split gap between each judge's
unaided accuracy and the strong models'; (b) fix one prompt template and add a nuisance-format control (FOL with
ASCII keywords, `forall service x0. ...`) to separate "English words" from "not symbols"; (c) state claims as "for
model judges of measured capability", never as readability.

**F2. Attacks are optimised against nothing, and attacker, generator and judge share families.** A weakening is
validated only for semantic difference, not difficulty. If attacks are easy, every condition sits at the floor and the
contrasts are empty; if the attacker knows the judge's view, conditions differ in attack strength. *Fix:* generate each attack once, blind to
condition, and reuse it in all conditions. Calibrate on dev so raw-FOL false approval is 30-60%,
freeze the recipe, then regenerate on scored items. Add a mechanical attack family (quantifier swap, dropped
conjunct, argument reversal, vacuous domain) that owes nothing to either family. Report every contrast per judge and
per attacker family; pool only when signs agree.

**F3. Several experiments are true by construction, and the forking paths are wide.** E2's flat review cost is
guaranteed when the judge sees a constant-size checker result; E4's checked countermodel is correct by
construction, so a judge who trusts the label scores perfectly. With seven experiments and many
views and judges, some contrast will look significant. *Fix:* each
PREREG names one primary contrast and one refutation condition; the rest is exploratory. E2 must put the error where
the checker cannot see it (false leaf premise, wrong specification) in half the items, so the VE arm can fail. E4
must include dishonest critics with asserted but unchecked countermodels. Unparseable verdicts count as the worst
case for their condition, never dropped.

## 2. Most likely to show a benefit, and to refute

**Benefit: E1, VE-strict versus FOL + untrusted explanation.** This is the one place where determinism does work
that a better prompt cannot: the attacker's explanation can assert the faithful reading while the formula says
otherwise. I expect a real drop in false approval there, and none against raw FOL.

**Refutation: E1, VE versus raw FOL, and E5.** If raw FOL matches VE for model judges, the English surface has no
demonstrated value in the only setting we can test. E5 is the likeliest *harm*: models defer to authority markers,
so a "proof checked" label should raise approval of badly grounded arguments.

## 3. Datasets (licences from memory; `experiments/E0/SURVEY.md` checks them)

- **FOLIO** (CC-BY-SA-4.0, ~1.4k stories with gold FOL). The NL premise is the "intended requirement"; the gold FOL
  imports to v0 with one sort `entity`; arity above 2 or functions count as no-fit. Contamination is likely, so E1
  uses FOLIO sentences only with fresh attacks.
- **ProofWriter** (CC-BY-4.0). Unary/binary rules, near-total fit; supplies E2 derivations of known depth and E4
  invalid inferences (OWA split only, since v0 entailment is classical).
- **Cedar examples** (Apache-2.0) and **Alloy models**. Principal/action/resource map to sorts and binary relations;
  string and numeric conditions become opaque predicates, which E0 counts separately.
- **Synthetic v0 generator** (ours): contamination-free; the main scored set for E1.

## 4. Add and cut under the budget

Six hours at concurrency 6 gives at most 25k calls; plan for 10k.
**Cut E6** (least VE-specific, most tokens) and **reduce E3 to an exploratory demo**. **Shrink E2** to three sizes
(4, 32, 256), 40 items each. **Spend on E1**: 200 scored items x 6 conditions x 2 judges = 2.4k calls, doubled with
scenarios. **Add E1b, a comprehension control**: with no requirement shown, the judge says whether the formal text
holds in each of two small finite models, scored by the evaluator; this separates comprehension of a view from
approval bias. Keep E4 and E5.
