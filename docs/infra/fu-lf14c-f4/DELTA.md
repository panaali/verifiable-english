# fu-lf14c-f4: family norms with n-ary definitions (lf-14c review F4)

## Scope and owner

A norm document on the closure or core family was regenerated over the environment's FOL view
(`VE.Service.FamilyNorms.folView`), which keeps only unary and binary predicates. A definition with a
three- to six-argument head was dropped from that view, and a definition whose body mentions an
n-ary atom did not decode there (`invalid indexed formula`). Lean now sends such documents to the
family's reader: `VE.Norms.Family.firstOrder` also requires every definition to be one the view
carries (`firstOrderDefinition`: a head of at most two arguments and a first-order body). The family
reader's Background comes from `VE.Core.Layers`, which elaborates definitions of every arity in one
dependency order. The family-norms response schema now types those Background rows with the family
formula grammar (`familyFormula`, which has `atom`), generated from `ResponseShape.Schemas.Norms.elaborateWith`.

N-ary definitions are carried, not refused: the family reader already elaborates them, and its
answers equal the retained Python reference's on every new case.

Base 85b20fcba (`git merge-base HEAD main`). Lean owns every decision; Python is unchanged.

## User-visible deltas

| # | Delta | Ruling |
|---|---|---|
| 1 | Trusted Lean lines: K +0, S +0, untied V +13 against 85b20fcba, by file: `VE/Norms/Family.lean` +12 (`firstOrderDefinition`, new, 9 lines, G[V]; `firstOrder` +3, G[V]), `VE/Core/Layers.lean` +1 (the `completeModel` docstring now says what the code does and is one line longer, D[V]). Measured with `tools/trust_map.py --since 85b20fcba` on the final code (2b8aff333); recorded as an allowance in `docs/trust-baseline.json`; `trust_map.py --check` passes. `firstOrderDefinition` and the new `firstOrder` conjunct are exercised by `test_nary_definitions_on_the_core_family_match_python` (seeded bugs 1 and 2 in `evidence/mutants.json` make it fail). A FOLLOW-UPS ties-pass row is in the report. | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | A core-family norm document whose definition has an n-ary head, or a body over an n-ary atom, that was referenced by a guard: `premises()`, `prove_norm_entailment`, `check_norm_entailment_certificate` and `check_conflict` raised `VEError: invalid indexed formula`; they now answer, and each answer equals the retained Python reference's (`test_a_definition_over_a_ternary_predicate_has_its_premises`, `test_nary_definitions_on_the_core_family_match_python[3-body, 4-body, 3-head, 4-head]`). | Directed by the task (acting DRI, fu-lf14c-f4 item 1: "passes with the right premises"); an availability change, no standing ruling covers it |
| 3 | A core-family norm document with an n-ary definition that no guard references: the regenerated Background lacked its biconditional, so the certificate of `Top` was invalid and `check_conflict(prove=True)` was UNKNOWN. Now the certificate is valid and the conflict check is CONFLICT-FREE, as the retained Python reference answers (`test_nary_definitions_on_the_core_family_match_python[3-unused, 4-unused]`). | Directed by the task (acting DRI, fu-lf14c-f4 item 1: "the family view must carry defined predicates of any arity"); a verdict change outside R5, DRI confirmation asked in the report |
| 4 | Response schema `family-norms.json`: Background `ast` is `familyFormula` (was `generated_formula`), regenerated from the Lean shape. Rows the old schema accepted are still accepted (`generated_formula` is a subset); a retyped n-ary row is refused (`test_the_family_background_refuses_retyped_nary_rows`). | SIGNED by standing ruling R8 (DRI-RULINGS.md): typed to the leaves; R12 for the generated schema and census |

No diagnostic text, fault order or path changed for any other input.

## Corpus A/B

`evidence/ab.json` (`python -m tools.evidence ab`, base 85b20fcba, head 2b8aff333): the seven corpora
lf-14c used (probe, conformance, readings, pilots, discourse, rights, quantity), **94,749 records**:
94,738 identical, 11 unavailable on both sides with identical outputs, **0 unlisted differences**.
The 11 (seven `translation-companions-with_source_word` constitution pilots, `CheckerUnavailable:
ReadingsConstruction ... KeyError`; four UDHR `translation-whole` pilots, 600 s pilot timeout on both
sides) are listed in `evidence/ab-delta.json`, each SIGNED by standing ruling R7 (DRI-RULINGS.md).
The pilots corpus was recorded twice to one output path, base then head, so the scratch path that
the sense-pack error texts quote is the same on both sides (a first recording with two paths showed
seven wording-only rows that differed in that path alone).

## Seeded bugs

`evidence/mutants.json`: three Lean faults, each made a named test fail and each was restored:
`firstOrderDefinition` ignoring the body (`lean/VE/Norms/Family.lean`), ignoring the head's arity
(same file), and the Background rows typed with the FOL grammar (`lean/ResponseShape/Schemas/Norms.lean`).
No Python or Rust product code changed.

## Cost

200 family-norms elaborations of the unchanged FOL-view document (`flagged(definitions=True)` on
closure + nary), base vs head on the same host, three runs each: wall 0.376/0.392/0.376 s base,
0.336/0.300/0.410 s head; client CPU 0.27-0.29 s vs 0.22-0.30 s. `firstOrder` makes one more pass
over the predicates; no regression.
