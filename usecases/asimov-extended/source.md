# Sources

## Asimov's laws (unchanged)

Rules 1–13 in [base.ve](base.ve) translate the Three Laws and the Zeroth Law
exactly as the merged v2 use case does. Its [source text](../asimov-laws/source.md)
pins the wording: Isaac Asimov, "Runaround", *Astounding Science Fiction*
(March 1942), p. 100, and the Zeroth Law from *Robots and Empire* (1985).
No file under `usecases/asimov-laws/` is changed. `base.ve` is v2's `rules.ve`
with one forced rewording: a risk environment rejects the bare word
`prevents`, so rules 9 and 13 say `might prevent`. The meaning of the word
does not change (risk.md 2.2).

## The additions (authored, not Asimov's)

Rules 14–29 in [additions.ve](additions.ve) are **this project's additions**,
written by "the Asimov extension author" for this use case. Asimov states none
of them. The Three Laws rank laws, not harms, and say nothing about orders
that conflict with each other. The additions are:

- the severity classes and their order: a harm to humanity, then death, then
  injury, then property damage, with the robot's own destruction counted as
  property damage (`environment.json`, decided by the Asimov extension author);
- a precaution against possible harm when a candidate action has a less
  severe worst case (rules 17, 18 and 25);
- a permission for an action whose worst case no candidate beats, when every
  action breaks a law (rule 19);
- precedence between competing orders: more authority prevails, and between
  orders whose authority is not ranked, the earlier one stands (rules 20–24);
- definitions used by those rules (rules 14–16 and 26–29).

Which harms an action might or does lead to, each harm's class, who gave an
order, the orders' time order and their relative authority are judgments of
"the Asimov case annotator" in each decision record.
