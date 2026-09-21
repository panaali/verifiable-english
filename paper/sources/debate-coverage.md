# Coverage

This document does not formalise the source text clause-by-clause (the brief
explicitly asks for a claim graph instead), so this table is claim-level, one
row per claim identified in `claim-graph.md`, using DIRECT/REIFIED/OPAQUE/NO
from `experiments/E0/SECOND_RATER.md` where the label is meaningful for an
argumentative claim (rather than a legal-text clause), plus a
fact/definition/value tag.

| Claim | Side | VE treatment | Label | Fact/Definition/Value |
|---|---|---|---|---|
| Shared core (Citizenship Clause rule + Wong Kim Ark rule) | both | `claims.ve` statements 1–2 | DIRECT | Definition (of the clause's own conditional shape; uncontested) |
| F1 — jurisdiction = exclusive allegiance | FOR | `countermodel/test5-premises.ve` (one universal, not asserted as fact) | DIRECT (as a formalised premise) | Definition |
| A1 — jurisdiction ≈ universal for anyone born here | AGAINST | implicit in Mayes's reading; contrary of F1's premise | DIRECT (as a formalised premise) | Definition |
| A2 — Wong Kim Ark extends to undocumented parents | AGAINST | `countermodel/test4-premises.ve` added premise | DIRECT (as a formalised premise) but shown NOT to follow from the accepted precedent alone (`test3`) | Definition + legal-authority (fact about what the precedent actually held) |
| F2 — original intent narrower than modern practice | FOR | not formalised | NO | Fact (historical) + legal-authority |
| F3 — scale/birth tourism | FOR | not formalised | NO | Fact/predictive |
| F4 — prospective administrable reform exists | FOR | not formalised | NO | Predictive/comparative-policy |
| A3 — don't punish children / underclass risk | AGAINST | not formalised | NO | Value (premise) + predictive (consequence) |
| A4 — historical continuity, inclusive founding values | AGAINST | not formalised | NO | Fact (historical) + value (framing) |

**Totals:** 9 claims identified. 4 have a direct VE statement (the shared
core plus the three competing/tested extension premises); 5 are NO — not
because v0's grammar is too narrow for their surface form, but because their
content is empirical, predictive, evaluative, or about the weight of legal
authority, none of which a finite relational check can settle. This is a
different NO than a missing connective: even an arbitrarily expressive VE
could not verify F3's birth-tourism rate or A3's "fundamentally American"
premise from within the language — those need external evidence or
normative argument, not more expressive logic. See `claim-graph.md`,
"What VE could not touch."
