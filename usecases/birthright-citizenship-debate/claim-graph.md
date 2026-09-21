# Claim graph: "Should America End Birthright Citizenship?"

Source: see `source.md` (Open to Debate, ASU/Arizona PBS debate, recorded
2025-10-09; assigned URL was a thin framing post, so argument content is
drawn from the companion transcript post — both cited there). This document
does **not** formalise the article; per the brief, it extracts the argument
structure as a claim graph, formalising only what is genuinely first-order
(`environment.json`, `claims.ve`, `countermodel/`), and naming the rest as
gaps.

## Motion

**"Should America end birthright citizenship?"**
FOR (end it): Mark Krikorian, Horace Cooper. AGAINST (keep it): Kris Mayes,
Chris Newman.

## Shared deductive core (both sides use this, in VE)

Both sides argue from the same textual starting point and the same
accepted precedent, which `claims.ve` states as:

```
for every person x0, (if ((x0 is born_in_us) and (x0 is subject_to_jurisdiction)), then (x0 is us_citizen)).
for every person x0, (if (x0 is has_noncitizen_domiciled_parent), then (x0 is subject_to_jurisdiction)).
```

(Fluent: "for every person P such that (both P is born_in_us and P is
subject_to_jurisdiction), P is us_citizen." / "...such that P is
has_noncitizen_domiciled_parent, P is subject_to_jurisdiction." — see
`rendered.md`.)

Neither debater disputes these two rules. **Every substantive disagreement in
the debate is about the extension of one predicate: `subject_to_jurisdiction`,
for people who are not `has_noncitizen_domiciled_parent`.** This is the
single most important finding of this exercise (see "What VE added," below).

## FOR ending birthright citizenship (Krikorian, Cooper)

### Claim F1 — the "subject to the jurisdiction" argument (definitional)

"Subject to the jurisdiction thereof" was designed to mean complete,
*exclusive* political allegiance — the way it excluded Native Americans
(members of tribes, hence under a separate jurisdiction) despite their being
physically present and even criminally prosecutable. Krikorian: undocumented
immigrants and temporary visitors are not "subject to *exclusive*
jurisdiction" in that sense, whatever their exposure to U.S. law enforcement.

**VE statement (the FOR side's implicit extension premise, not asserted in
`claims.ve` — see `countermodel/test5-premises.ve`):**
`for every person x0, (if (x0 is has_noncitizen_undocumented_parent), then (not (x0 is subject_to_jurisdiction))).`
(and the parallel statement for `has_noncitizen_temporary_parent`, not separately tested).

**Premises:** (i) "subject to the jurisdiction" = exclusive political
allegiance [a *definitional* premise about original meaning]; (ii) parents
without legal status or with only temporary status do not give their
children that exclusive allegiance [empirical/definitional]. **Conclusion:**
children of such parents are outside the Citizenship Clause.

### Claim F2 — original intent (historical/definitional)

The 14th Amendment's Citizenship Clause was drafted to settle the status of
freed slaves, not to grant universal jus soli to the children of any foreign
national. Cooper cites Justice Harlan's dissents (Plessy; also invoked
regarding Wong Kim Ark) as evidence the framers' understanding was narrower
than modern practice. **This directly conflicts with A2** (below) over how
much weight *Wong Kim Ark*'s actual holding carries and how far it
generalizes — a **legal-authority / historical-fact** dispute, not something
`check`/`countermodel` can adjudicate (there is no finite structure that
settles "what the 1868 framers intended").

### Claim F3 — changed scale creates perverse incentives (empirical/predictive)

Krikorian, on scale: "200 million foreign students, tourists, foreign
workers... every year. Nothing like this was possible in the past." He adds
that roughly 10% of U.S. births now involve a non-citizen parent, and
describes "birth tourism": wealthy foreign nationals purchasing "package
deals" to give birth in the U.S. for a citizenship passport, without intending
the child to reside there. **Premises:** modern international mobility is
orders of magnitude greater than in 1868 [empirical]; some non-citizens
exploit unconditional jus soli for citizenship-by-birth-tourism with no
residency intent [empirical]. **Conclusion:** applying an 1868 rule
unmodified to 2026 conditions produces outcomes the framers could not have
intended and would not endorse. This is a **factual/predictive** claim (rates
of birth tourism, size of the affected population) that VE has no way to
check — it is not stateable as a claim about one supplied finite model; it is
a claim about the actual world's statistics.

### Claim F4 — a prospective, administrable fix exists (policy/comparative)

Congress could legislate a change applying only to future births (not
retroactively stripping existing citizens), citing Australia's and France's
more conditional jus soli regimes as evidence this is workable elsewhere.
**Conclusion:** ending unconditional birthright citizenship is not a radical
or unadministrable step. This is a **predictive/comparative-policy** claim
(would U.S. administrative practice work like Australia's), again outside
what a finite relational check can verify.

## AGAINST ending birthright citizenship (Mayes, Newman)

### Claim A1 — plain text (definitional/textualist)

Mayes: "The 14th Amendment states... All persons born... in the United
States... are citizens. Full stop." The clause has no textual carve-out for
parental immigration status. **VE statement:** this is exactly the shared
core rule above, read by Mayes as if `subject_to_jurisdiction` were
effectively universal for anyone born in U.S. territory — i.e., Mayes's
reading effectively asserts
`for every person x0, (if (x0 is born_in_us), then (x0 is subject_to_jurisdiction))`,
which is the widest possible extension and is the logical **contrary** of
Krikorian's F1 restriction. This is the same "same word, different sense"
split as F1: both sides accept the Citizenship Clause's conditional shape;
they disagree about what makes the jurisdiction antecedent true.

### Claim A2 — settled precedent (legal-authority)

*United States v. Wong Kim Ark* (1898) already held that a child born in the
U.S. to non-citizen parents (Chinese nationals statutorily ineligible for
naturalization) is a citizen — decided by justices contemporaneous with the
amendment's ratification, and settled for 127 years. Mayes further rebuts F1
directly: prosecuting drug-cartel members for U.S. crimes shows undocumented
immigrants are already "subject to" U.S. jurisdiction in the ordinary,
law-enforcement sense. **VE statement:** the shared-core Wong Kim Ark rule
(`has_noncitizen_domiciled_parent → subject_to_jurisdiction`) plus the
implicit extension premise tested in `countermodel/test4-premises.ve`
(`has_noncitizen_undocumented_parent → subject_to_jurisdiction`). Whether that
extension is a faithful reading of Wong Kim Ark's actual holding (which
concerned *domiciled*, not undocumented, parents) or an analogical stretch is
exactly what Krikorian disputes — **countermodel confirms it is a genuine
extension, not a restatement** (`test3`, below).

### Claim A3 — moral/values claim: punishing children, creating an underclass

Newman: "you don't blame the child for the actions of the parents. That's
fundamentally American." Ending birthright citizenship would create "a
permanent underclass of vulnerable stateless children," denied "rights of
full citizens, such as healthcare and education." **Premises:** a child's
legal status should not depend on a parent's conduct [**value** premise];
removing birthright citizenship would produce statelessness and an
underclass [**predictive/empirical** premise, itself contested — statelessness
depends on the specific implementing statute, e.g. whether the other parent's
country grants citizenship]. VE has no representation for either premise: the
first is a moral "ought," the second is a prediction about a policy not yet
enacted.

### Claim A4 — historical continuity and inclusive founding values

Birthright citizenship predates the 14th Amendment (British common law,
colonial practice) and was deliberately extended after the Civil War to
people of all races; Newman invokes Frederick Douglass's opposition to
race-based limits on migration/citizenship, framing universal jus soli as
core to post-Civil War reconciliation, not an incidental technical rule. This
is a **historical/values** claim about the amendment's purpose, overlapping
with F2 but drawing the opposite normative conclusion from similar historical
material — both sides cite history; they weight and read it differently.

## Predicates shared vs. senses that split

**Shared, undisputed predicates:** `born_in_us`, `us_citizen` (as a target
status — both sides want a fact of the matter about who has it),
`has_noncitizen_domiciled_parent` (both accept Wong Kim Ark's holding for
this profile).

**Same word, different sense — the crux:** `subject_to_jurisdiction`
("subject to the jurisdiction thereof"). Krikorian/Cooper: complete, exclusive
political allegiance (excludes tribal members historically; excludes
undocumented/temporary-status parents' children today). Mayes/Newman: bound
by and enforceable under U.S. law while physically present (satisfied by
essentially everyone born on U.S. soil, including undocumented immigrants,
evidenced by ordinary criminal prosecution). `environment.json` documents
both readings directly in the predicate's `description` field rather than
picking one, because picking one would silently resolve the debate by
vocabulary choice — exactly the move the project brief warns against ("never
force a sentence into VE by hiding its substance... without saying so").

A second, smaller same-word split: "underclass"/"stateless" (A3) vs.
"perverse incentives"/"birth tourism" (F3) are not the same word, but both
sides use "citizenship" itself with different implicit theories — Mayes
frames it as a **right** ("a right, not a privilege"); Krikorian/Cooper frame
it as a **conferred legal status** contingent on jurisdiction. VE cannot
represent this framing difference at all (see Gaps, below): both usages type-check
identically as the unary predicate `us_citizen`.

## Deductive steps tested with `countermodel`

See `countermodel/RESULTS.md` for full commands, premises, and returned
models. Summary:

| Test | Premises | Conclusion | Result | Reading |
|---|---|---|---|---|
| 1 | Shared core + `@child` born & jurisdiction-subject | `@child` is a citizen | **Valid** (`NotFound`) | Plain modus ponens both sides accept |
| 2 | Shared core + `@child` born (jurisdiction premise dropped) | `@child` is a citizen | **Invalid** (`Found`) — countermodel has `subject_to_jurisdiction`, `us_citizen` both empty | Isolates the crux: "born" alone never entails citizenship in this vocabulary |
| 3 | Wong Kim Ark rule + `@child` has undocumented parent | `@child` is jurisdiction-subject | **Invalid** (`Found`) | The AGAINST side's analogy from Wong Kim Ark to undocumented parents is not a deductive restatement; it needs an extra premise |
| 4 | Wong Kim Ark rule + AGAINST's extension premise + `@child` undocumented | `@child` is jurisdiction-subject | **Valid** (`NotFound`) | Once granted, AGAINST's conclusion follows validly |
| 5 | FOR's (contrary) extension premise + `@child` undocumented | `@child` is **not** jurisdiction-subject | **Valid** (`NotFound`) | FOR's conclusion *also* follows validly, from FOR's own premise |

Tests 4 and 5 together are the payoff: **both sides argue validly**; the
entire dispute is located at one pair of mutually contradictory universal
premises about the extension of `subject_to_jurisdiction` for
undocumented/temporary-status parents. No amount of additional deduction
inside v0 can settle which premise is correct — that requires historical and
legal-interpretive judgment outside a finite relational structure.

## Classifying the disagreements

| Claim(s) | Kind of disagreement |
|---|---|
| F1 vs. A1/A2 (jurisdiction extension) | **Definitional.** Same predicate, different accepted extension; countermodel shows both readings are internally valid syllogisms once assumed. |
| F2 vs. A2/A4 (original intent vs. precedent weight) | **Fact + legal-authority.** What the framers intended (historical fact) and how much a 127-year-old precedent should constrain current interpretation (legal-interpretive, not a fact VE can check). |
| F3 (scale, birth tourism rates) | **Fact/predictive.** Empirical claims about the present world; not stateable as a claim VE checks in a stipulated model. |
| F4 vs. A3-administrability | **Predictive/comparative-policy.** Would a U.S. prospective-only regime work like Australia's or France's; would implementation cause hospital/DNA-testing chaos. Neither side's claim here is checkable by VE. |
| A3 (moral: don't punish children; underclass) | **Value** (the moral premise) **+ predictive** (the underclass/statelessness consequence). |
| A1 ("right, not privilege") vs. implicit F-side framing (citizenship as conferred/contingent status) | **Value/framing**, invisible to VE's unary `us_citizen` predicate either way. |

## What VE added

1. It forced an exact statement of the shared deductive core (two rules,
   above) and showed both sides actually agree on it — the debate is not,
   contrary to surface appearance, a disagreement about logic or about the
   text's grammar.
2. `countermodel` **located the single predicate** (`subject_to_jurisdiction`,
   restricted to undocumented/temporary-status parents) that the entire
   dispute reduces to, and proved, not just asserted, that "born in the U.S."
   alone is logically insufficient for citizenship in this vocabulary (test
   2) and that the Wong Kim Ark analogy needs an extra, contested premise to
   reach the AGAINST side's conclusion (test 3) — this is a real, checked
   result, not a paraphrase of what the debaters said.
3. It showed **both sides are internally valid** (tests 4 and 5): this is a
   genuinely useful, somewhat surprising finding — a purely rhetorical read of
   the transcript could easily leave the impression that one side is "just
   asserting" its jurisdiction reading while the other "proves" it from
   precedent. Formally, both moves have exactly the same shape (a universal
   premise plus modus ponens); precedent (A2) supplies a premise for one
   profile (`domiciled`) but not for the disputed one (`undocumented`), and
   that gap is symmetric for both sides.
4. Writing `subject_to_jurisdiction`'s two glosses into one vocabulary entry's
   `description` field, side by side, is a small but real way VE forces
   honesty about equivocation that prose debate summaries often paper over.

## What VE could not touch

- The actual **definitional** question (whose reading of "jurisdiction" is
  correct) — VE can isolate it exactly but not settle it; that needs
  historical/legal argument, not a countermodel.
- Every **empirical/predictive** claim (F3's birth-tourism rates, F4/A4's
  administrability, A3's underclass prediction) — v0 checks formulas against
  a *stipulated* finite model; it has no channel to real-world statistics or
  forecasts, and turning them into predicates (`high_noncitizen_birth_rate`,
  `causes_underclass`) would be exactly the OPAQUE move the project brief
  warns against, so no such predicates are declared here.
- **Values** (A3's "don't blame the child," A1's "right not privilege") — no
  deontic or normative construct exists in v0 (see GAPS.md).
- **Legal-authority weighting** (how binding is Wong Kim Ark; how much does
  original intent constrain current meaning) — this is jurisprudential
  reasoning about *sources* of law, categorically different from first-order
  consequence within one stipulated vocabulary.
- **Attribution/quotation** ("Krikorian said X," "Cooper cited Harlan's
  dissent") — v0 has no quotation or reported-speech construct; this document
  represents claims as if asserted directly, losing who-said-what and hedging
  ("Krikorian focused on...", "Cooper dismissed...").

## Honest verdict

This is the closest real test of VE's "debate" story in this pair of
use cases, and it worked better than the constitution formalisation at
*revealing structure*: instead of four independent OPAQUE clauses, one
predicate's contested extension turned out to explain the entire surface
disagreement, and `countermodel` produced a concrete, checked demonstration
of that rather than an assertion. It did not — and given v0's scope, could
not — adjudicate the debate, verify any empirical premise, or represent the
moral and framing disagreements that make up roughly half of each side's
case (A3, A4, F3, F4). The honest summary is: **VE is a good tool for finding
exactly where a definitional argument's hinge is and proving both sides
reason validly from their own premises; it is not a tool for winning the
argument over what the hinge should be, and it is silent on everything in
the debate that is not deductive (which, by claim count, is roughly half).**
