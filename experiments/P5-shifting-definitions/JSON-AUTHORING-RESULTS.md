# VE JSON-schema authoring feasibility probe (v13) — results, 2026-09-22

Prespecified in `JSON-AUTHORING-AMENDMENT.md` (including its v13 addendum).
DEV only; Gemini `gemini-3.1-pro-preview` author plus one repair on failure;
no judges, critics, ratings or scored items. Raw replies, imported FOL,
canonical VE and checker output: `runs/ve-json-author-feasibility-v13/`.

## Result

**0/12 replay** (initial 0/12, after one repair 0/12). Below the 6/12
threshold, so the VE DEV cell rerun is **not** prepared. Under this interface
and budget, VE authoring is **infeasible for these items**.

The JSON interface removed surface-syntax failures: all 12 author outputs
validated against the local schema and imported through
`document_from_named_fol` (0 schema/AST/import errors, compared with 24/30
parse errors in v10). The remaining failures are content and budget
failures.

| Category (all 24 attempts) | Author | Repair |
|---|---|---|
| Schema / AST reference / import error | 0 | 0 |
| JSON truncated at the 5,000-token cap (`MAX_TOKENS`) | 0 | 6 |
| Imported, but ≥1 edge unproved (no certificate) | 12 | 6 |

Final per item: 6 unproved-edge, 6 truncated repairs. An offline re-search
(10,000 steps per edge, no model calls) found `NotFound` for all 252
unproved edges across the 18 checker-reaching attempts, with no
`ResourceLimit`. Unproved edges are not refutations.

Of those 18 imported graphs, **11 collapsed the declared premises**. The
declared rule groups were never formalised: 1–2 distinct formulas across six
premises, usually the fact conjunction reused, and no conditional in any
premise. All 16 edges then failed. The other **7 formalised all six premises
distinctly** (five rule groups each) but still left 2–16 edges unproved.
Paragraph formulas asserted content the parents do not entail, such as
conditional alternatives restated as consequences or mismatched predicate
senses. The best attempt, the i248c407 repair, left 2 of 16 edges
unproved. Truncated repairs spent up to 4,798 of the 5,000 tokens on
thinking despite LOW thinking. Source fidelity was not assessed.

## Spend (task cap $2.50)

| Ledger | USD |
|---|---|
| v12 (one 400 call, settled at full ceiling) | 0.092768 |
| smoke 1 (400, full ceiling) | 0.038912 |
| flash-lite bisection allowance | 0.001 |
| smoke 2 (accepted) | 0.006110 |
| v13 probe, 24 completed calls + 1 interrupted call charged at ceiling | 1.827890 |
| **Total** | **1.966680** |

Nothing is outstanding. Full-ceiling charges for calls whose billing is
unknown total $0.224448. No completed call was re-bought: the resumed run
reused the cached replies for items 1–3.

## Recommendation

Report VE authoring as infeasible for these 12 DEV items at this budget.
Frontier authoring now reaches the checker, but it does not produce
entailing claim graphs, and one repair does not fix that. Do not run the
VE DEV cells.
