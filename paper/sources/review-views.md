# Claude-side review of codex/views — VERDICT: changes-required

## BLOCKING

1. ve/printer.py:79-82 and :93-99. ve_natural accepts templates that change the argument order or the predicate a
   judge reads. It is also the only view that never shows the predicate identifier.
   - Reproduction: `owns(person, service)` with template `"{0} is owned by {1}"` is accepted, because the first word
     `is` ends in "s". It renders "x1 is owned by x0", while both FOL views show `owns(x1, x0)`.
   - Also accepted: `"{0} belongs to {1}"` and `"{0} lacks {1}"`; `"{0} audits carefully {1}"` on `owns` while a
     predicate `audits` exists (the collision check is exact-string only); `"{0} is undeployed"` and
     `"{0} is reviewed already"` on `deployed`; sort nouns service→"owner" and person→"asset"; nouns "x" and
     "service x", which render as "for every service x x0:".
   - Correctly rejected, with strict fallback: `{1}…{0}`, missing or repeated placeholders, parentheses, newlines,
     capitals, double spaces, format specs, `{0.__class__}`, "and", bare "is", exact duplicate templates, and a template
     equal to another predicate's strict form.
   - Why it matters for E1: a passive or converse phrase works as an argument-reversal attack that only the ve_natural
     cell sees. It also contradicts related-systems section 2.4 ("no passive").
   - Minimal fix: reject a binary phrase that starts with "is", "are" or "was", or ends in "by", "to" or "of". Reject
     any phrase containing another declared identifier as a word. Alternatively, show the identifier next to the phrase.

2. ve/search.py:150-166 and :185. `_models` enumerates relations for every declared predicate, including ones neither
   formula uses.
   - Reproduction: 2 sorts, 4 binary and 3 unary predicates, ∀s∃p vs ∃p∀s with `max_domain_size=2`. Result is
     `ResourceLimit` at the default `max_models=10000`, and still `ResourceLimit` at `max_models=10**6` (evaluation cap
     hit after 76,096 models). With 5 predicates the same swap needs 8,697 of the 10,000 default models.
   - Why it matters for E1: every attack has to be validated by a distinguishing model. With a realistic fresh
     vocabulary the main attack family cannot be validated. The failure is safe (never NotFound).
   - Fix: enumerate only the predicates occurring in a, b and nonvacuous_for, and fix the rest as empty.

## NON-BLOCKING
- The CLI exits with code 2 for both InvalidInput and ResourceLimit.
- ve_strict is limited to 64 KB and the other views to 16 MB, so an oversized AST would lose one cell.
- Only ve_natural capitalises the first letter of each statement.
- `natural_formula` appends "." but `render(formula)` does not.
- The 30 lines of option validation in `find_countermodel` and `find_distinguishing_model` are duplicated.

## What was checked and passed
158 tests; injectivity on 17,132 random ASTs in all four views; an independent ve_natural parser from the EBNF gave
parse(render(f)) == f on 17,132/17,132 (default-safe templates); 8 minimal pairs differ in all views and are
distinguishable; 2,000 documents keep statement count/order; FOL export/import round trip 2,000/2,000;
find_distinguishing_model on 400 random pairs vs brute force: 237 Found all correct and non-vacuous, 77 NotFound all
true, 86 ResourceLimit none had a qualifying model; trace vs no-trace identical on 3,000 triples.

## SCIENCE
- Length is confounded with view. Mean characters per formula: 123 (fol_symbols), 145 (fol_keywords), 156 (ve_strict),
  194 (ve_natural). Report length as a covariate. Real tokenizers will charge more for ∀ and ∧.
- Three views show raw identifiers and ve_natural shows phrases, so "same information" holds only if the vocabulary is
  frozen and reviewed; nothing in code enforces it. For E5, where the attacker authors the vocabulary, the natural view
  is strictly weaker than the others.
- Non-vacuity is syntactic (implications and quantifiers only). A model for `∀s(¬dep(s) ∨ rev(s))` with no deployed
  service passes as "non-vacuous". The "vacuous domain" attack family needs a semantic check.
- Full bracketing of atoms helps injectivity but makes every view unnatural; E1 results will not transfer to ACE-style
  prose.
