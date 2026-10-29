# SC-3ac delta

No computed answer, refusal, diagnostic, or byte output changes: this item proves an existing Lean behavior.

| Delta | Condition evidence | Ruling |
|---|---|---|
| `title_identity` gains `JsonWF D.doc`; its other text matches spec 5.5. | `Examples.lean` proves the parsed-form fixture well formed, refuses F-raw-title, and guards both title-only outputs; dropping the premise leaves `JsonWF D.doc` unprovable. | SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 2) |
| Trusted V +6, K +0, S +0: `Theorems.lean` +3 (`insertBy`), `Examples.lean` +3 (title-order fixtures). | `tools/trust_map.py --check`; `trust-mutants.json` has 5 killed, 0 survivors/unknowns; `mutants.json` records the hand guards. | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
