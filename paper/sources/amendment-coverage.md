# Coverage

Labels follow the DIRECT / REIFIED / OPAQUE / NO scheme from
`experiments/E0/SECOND_RATER.md` (relative to the enabled profile, `relational-fol@0`
only — v0.1's `closure@0`/`order@0` are not used here since nothing in Section 1
needs transitive closure or arithmetic).

| # | Clause | Label | Notes |
|---|---|---|---|
| 1 | Citizenship Clause | REIFIED | The relational skeleton (`born_in_us`/`naturalized_in_us`/`subject_to_us_jurisdiction` ⟶ `us_citizen`, `citizen_of_state`) is faithful and direct. But "the State **wherein they reside**" is a definite description presupposing each person resides in exactly one State; v0 has no function symbols, so `resides_in` is encoded as a plain (unconstrained) binary relation. The formalisation is a mechanical reification of a function as a relation, and it silently drops the source's built-in uniqueness assumption (a model could give one person two `resides_in` states without contradiction). See GAPS.md #3. |
| 2 | Privileges or Immunities Clause | OPAQUE | The prohibition's logical shape (state × law × citizen, "no law of this state abridges...") is captured directly. But `abridges_priv_or_imm(law, person)` is a single opaque predicate standing in for the entire, historically contested legal content of "the privileges or immunities of citizens of the United States" (a phrase whose scope has been litigated since the *Slaughter-House Cases*, 1873). Nothing in the vocabulary says what would make that predicate true or false of a given law/person pair. See GAPS.md #2. |
| 3 | Due Process Clause | OPAQUE | Structure captured as `deprives(state,person) → affords_due_process(state,person)`, correctly encoding "no deprivation without due process" as a material conditional. `affords_due_process` is opaque: it hides the entire doctrinal content of what process is "due" (notice, hearing, substantive limits, etc.). See GAPS.md #2. |
| 4 | Equal Protection Clause | OPAQUE | Structure captured as `within_jurisdiction_of(person,state) → not denies_equal_protection(state,person)`. `denies_equal_protection` is opaque: it hides the tiers-of-scrutiny doctrine that determines whether a given classification counts as a denial. See GAPS.md #2. |

**Totals:** 4 clauses formalised. 0 DIRECT, 1 REIFIED, 3 OPAQUE, 0 NO.

All four `claims.ve` statements parse and `check` against `environment.json`
(`assurance: experimental`, `language: accepted`). `model-true.json` satisfies
all four; `model-false.json` differs only in adding one
`denies_equal_protection` tuple, which falsifies statement 4 alone (statements
1–3 remain `True`) — confirming the four statements are logically independent
in this vocabulary, not a single tautology.

## What "OPAQUE" means here, honestly

Every clause of Section 1 is, in practice, a delegation to future adjudication:
the constitutional text itself does not define "privileges or immunities,"
"due process," or "equal protection" — U.S. courts have spent 150+ years
filling in that content case by case, and that content changes. So labelling
statements 2–4 OPAQUE is not a shortcoming specific to this formalisation; it
reflects that the clauses are *intentionally* open-textured legal standards,
not closed rules. VE correctly exposes this: it can state the shape of the
prohibition ("no law/state action of this kind targeting this person") and
check that shape against a model, but it cannot check whether any concrete law
*is* such a law — that question is exactly what the opaque predicate stands
for. See GAPS.md for what a faithful non-opaque treatment would need.
