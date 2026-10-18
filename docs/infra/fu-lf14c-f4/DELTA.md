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
| 2 | A core-family norm document whose definition has an n-ary head, or a body over an n-ary atom, that was referenced by a guard: `premises()`, `prove_norm_entailment`, `check_norm_entailment_certificate` and `check_conflict` raised `VEError: invalid indexed formula`; they now answer, and each answer equals the retained Python reference's (`test_a_definition_over_a_ternary_predicate_has_its_premises`, `test_nary_definitions_on_the_core_family_match_python[3-body, 4-body, 3-head, 4-head]`). | Directed by the task (acting DRI, fu-lf14c-f4 item 1: "passes with the right premises"); an availability change. SIGNED by the DRI 2026-10-17 (dri-decisions-20261017b.md #2), after the fact: the head equals the retained Python reference, and the base lacked a declared definition's biconditional. |
| 3 | A core-family norm document with an n-ary definition that no guard references: the regenerated Background lacked its biconditional, so the certificate of `Top` was invalid and `check_conflict(prove=True)` was UNKNOWN. Now the certificate is valid and the conflict check is CONFLICT-FREE, as the retained Python reference answers (`test_nary_definitions_on_the_core_family_match_python[3-unused, 4-unused]`). | Directed by the task (acting DRI, fu-lf14c-f4 item 1: "the family view must carry defined predicates of any arity"); a verdict change outside R5. SIGNED by the DRI 2026-10-17 (dri-decisions-20261017b.md #2), after the fact: the head equals the retained Python reference, and the base lacked a declared definition's biconditional. |
| 4 | Response schema `family-norms.json`: Background `ast` is `familyFormula` (was `generated_formula`), regenerated from the Lean shape. Rows the old schema accepted are still accepted (`generated_formula` is a subset); a retyped n-ary row is refused (`test_the_family_background_refuses_retyped_nary_rows`). | SIGNED by standing ruling R8 (DRI-RULINGS.md): typed to the leaves; R12 for the generated schema and census |
| 5 | Trust ties pass for row 1 (R16's FOLLOW-UP, FOLLOW-UPS "## fu-lf14c-f4"; infra item ties-fu-1017, 2026-10-17). New theorems in `lean/VE/Norms/FamilySpec.lean` (proofs only; `ve_service` is not rebuilt) tie, in `tools/trust-classes.json`, `firstOrderDefinition` (9 lines, all row 1's) and `firstOrder` (17 lines, row 1's +3 among them), and with them the three older checks they are built from, `firstOrderFormula` (10), `orderFol` (8) and `orderTermFol` (5). Untied V falls by their 49 lines, from 39,971 to 39,922 on main b5248038e; row 1's V +13 becomes +1, the `completeModel` docstring line, which no theorem ties ("Trust ties pass" below). Evidence: `python3 tools/trust_map.py --check` PASS before (b5248038e: "tied +0 … trusted +0") and after ("tied +49, … trusted -49, VE/Norms/Family.lean: trusted -49"); the per-file counts and seeded bugs below | The ties pass that standing ruling R16 (DRI-RULINGS.md) asks for. It only lowers V: it raises or adds no allowance and writes no trusted line or signature |

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

## Trust ties pass (row 5; infra item ties-fu-1017, 2026-10-17)

Method. `tools/trust_map.py` was run on main with the item merged (b5248038e) and against row 1's base (85b20fcba).
Row 1's V +13 is `firstOrderDefinition` (new, 9 lines), three new lines of `firstOrder` (`VE/Norms/Family.lean`) and one
docstring line of `completeModel` (`VE/Core/Layers.lean`). No theorem of `lean/statements.txt` named any of them, so the
ties are new theorems, in a new proofs-only module `lean/VE/Norms/FamilySpec.lean`. The service does not import that
module, so `ve_service` builds byte-identical and `lean/checkers.lock` is unchanged. It adds no trusted line: its 131
declaration lines are theorems (P), and `trust_map.py` counts the module trusted 0. A theorem added to
`VE/Service/FamilyNorms.lean` would have changed the pinned `ve_service` build. Each statement fixes what its
declaration means in terms of K: an accepted definition, body, guard or carve-out is the embedding of an FOL formula
(`VE.Core.embed`, whose meaning `VE.Core.conservativity_without_reach` keeps; `VE.Order.embed`, `VE.Order.conservativity`).
An accepted head passes `VE.Core.Layers.folEntry`, the filter `VE.Service.FamilyNorms.folView` keeps.

### Ties added (commit 670a9f329; theorems f4c6ab414)

| File | Declaration (lines) | Tying theorem | What the statement fixes |
| --- | --- | --- | --- |
| `VE/Norms/Family.lean` | `firstOrderDefinition` (9, row 1's) | `VE.Norms.Family.firstOrderDefinition_fol` | An entry it accepts that has a `defined` payload has a head `folEntry` accepts (at most two arguments: `folView` keeps it). Its body, wherever the family decoder (`VE.Core.Bridge.decodeFormula`, or `VE.Order.Wire.decodeFormula` under `order@0`) decodes it, is `VE.Core.embed φ` (or `VE.Order.embed φ`) of an FOL formula `φ`. Row 1's two seeded bugs (body ignored, arity ignored) each make it fail to prove (L1 below) |
| `VE/Norms/Family.lean` | `firstOrder` (17; row 1's +3) | `VE.Norms.Family.firstOrder_fol` | A document it sends to the FOL view has no `$int` declaration (`usesInt` false), every predicate entry of the environment that has a definition satisfies the conclusion of `firstOrderDefinition_fol`, and every guard and every carve-out of every norm is the embedding of an FOL formula wherever its family decodes it. `order` is the `order@0` test it reads. Without row 1's three lines (the definitions conjunct) it fails to prove (L2) |
| `VE/Norms/Family.lean` | `firstOrderFormula` (10) | `VE.Norms.Family.firstOrderFormula_fol` | A formula it accepts is, wherever its family decodes it, the embedding of an FOL formula. A formula the family decoder refuses still counts as first-order, as its docstring says; the statement claims nothing about it |
| `VE/Norms/Family.lean` | `orderFol` (8) | `VE.Norms.Family.orderFol_embed` | An order formula it accepts is `VE.Order.embed φ` of an FOL formula (no comparison, no arithmetic term) |
| `VE/Norms/Family.lean` | `orderTermFol` (5) | `VE.Norms.Family.orderTermFol_embed` | A term it accepts is `VE.Order.embedTerm s` of an FOL term (a variable or a constant) |

Every theorem states one direction: what acceptance guarantees, the direction on which sending a document to the
view relies. A document the test refuses goes to the family's reader (`genericRun`); the statements claim nothing
about that route. `firstOrderFormula`, `orderFol` and `orderTermFol` are not row 1's lines. They are tied because the theorems for row 1's
declarations are built from them and fix their meaning too. Their 23 lines and the 14 older lines of `firstOrder`
(37 lines beyond row 1's 12) are counted in the drop.

### Per-file counts (untied V lines, `trust_map.py`; base = 85b20fcba, before = b5248038e (main with the item merged), after = 670a9f329 (the ties commit))

| File | V base | V before | Row 1's V | V after | Ties | Row 1's V after the ties |
| --- | --- | --- | --- | --- | --- | --- |
| `VE/Norms/Family.lean` | 436 | 448 | +12 | 399 | -49 | 0 (and -37 below the base) |
| `VE/Core/Layers.lean` | 282 | 283 | +1 | 283 | 0 | +1 |
| `VE/Norms/FamilySpec.lean` (new) | – | – | – | 0 | 0 | 0 (131 P lines) |
| **All files (main)** | | **39,971** | **+13** | **39,922** | **-49** | **+1** |

K (997) and S (10,152) are unchanged. Tied lines go from 263 to 312 and the trusted total from 51,120 to 51,071.
Against 85b20fcba, `trust_map.py --check` shows "VE/Norms/Family.lean: trusted -37, VE/Core/Layers.lean: trusted +1"
for this row's files. Row 1's allowance (V 13) is not touched. The consolidation ledger (`trust_map.py --ledger`)
prints the same before and after: no step selects these declarations.

### Declarations no theorem ties

| File | Declaration (row 1's lines) | Why no theorem ties it | A theorem that would |
| --- | --- | --- | --- |
| `VE/Core/Layers.lean` | `completeModel` (+1 of 37: its docstring is one line longer) | No theorem names it. `naryCheck_ok` proves the n-ary biconditionals hold on the model it builds, but that model is internal to the do-block. The answer is JSON, and no theorem decodes it back | `completeModel_sound`: `completeModel L environment model = .ok out` implies that the model decoded from `out` (`VE.Route.Decode.decodeModelData` over the core vocabulary) satisfies every definition's premise (`(L.nary.map NaryDef.premise).all (·.eval M [])` and the FOL definitions' biconditionals), and that its base relations are `model`'s. The work is walking the do-block (`naryCheck_ok` covers the last step) and a `tableJson`/`decodeModelData` round trip. Not written here: it ties a 37-line declaration for a one-line growth, and it needs a JSON round trip this pass does not have |

### Seeded bugs (each restored; `docs/infra/ties-fu-1017/mutants.json`)

| Seed | Temporary change | Failure |
| --- | --- | --- |
| L1 | `firstOrderDefinition` without `VE.Core.Layers.folEntry entry &&` (row 1's seeded bug 2) | `lake build VE.Norms.FamilySpec`: `firstOrderDefinition_fol` fails (FamilySpec.lean:101) |
| L2 | `firstOrder` without the definitions conjunct (row 1's three lines) | `firstOrder_fol` fails (FamilySpec.lean:129) |
| L3 | `firstOrderFormula`'s core branch `\| .ok _ => true` | `firstOrderFormula_fol` fails (FamilySpec.lean:83) |
| L3b | `orderFol` accepts `lt` and `le` | `orderFol_embed` fails (FamilySpec.lean:47) |
| L3c | `orderTermFol` accepts every term | `orderTermFol_embed` fails (FamilySpec.lean:23) |
| T1 | `firstOrderDefinition_fol`'s `-- uses` line without `VE.Norms.Family.firstOrderDefinition@VE.Norms.Family` (`lean/statements.txt`) | `trust_map.py --check` exit 1: "the statement of VE.Norms.Family.firstOrderDefinition_fol does not mention VE.Norms.Family.firstOrderDefinition of VE.Norms.Family"; `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` fails |
| T2 | `firstOrder` tied to an unrelated theorem, `VE.Core.embed_of_erase` (`tools/trust-classes.json`) | `trust_map.py --check` exit 1: "the statement of VE.Core.embed_of_erase does not mention VE.Norms.Family.firstOrder of VE.Norms.Family"; the same test fails |
