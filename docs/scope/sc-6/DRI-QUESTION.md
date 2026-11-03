# sc-6: question for the DRI decider (2026-11-02)

## What is asked

SC-6 fills rights@0's `Limitation.scope` from a reach (plan SC-6 at b2e050be2, spec 5.8). The Lean part, which is
`Pinned.rightNames`, `Pinned.withReach` and `limitation_scope_of_reach`, plus F14, F14′ and F14″ as Lean fixtures on
UDHR part documents, fits this item. Wiring it into the document route does not fit. Every way for a document to put
a rights reach on a limitation or bar unit is blocked inside this item:

| Wire form | Blocked by |
|---|---|
| (a) a new effect word (e.g. `"limits"`) or a new block member (e.g. `rights_reach`) | `decodeEffect` and `decodeParts` (`lean/VE/Scope/Wire.lean`) are unfolded step by step in `decodeEffect_wf` and `decodeParts_wf`, which live in `lean/VE/Service/ScopeAdmission.lean`. That file belongs to pc-1, which is in flight, and the task forbids it. |
| (b) an existing graph governor (`precedes`) whose unit is the limitation | A limitation unit has no base rule, so its edges are empty. The approved `no_effect_refused` (5.6) then requires `govern` to refuse with `ScopeNoEffect: <g>`, which is what main answers today. Accepting it means changing an approved statement. |
| (c) a reach written in the limitation's own `scope`, with no governor | `govern_identity` (5.1): with no governor, `govern` returns the document unchanged. |

Any of these also widens what the document mode accepts: main refuses such a document. No standing ruling covers
widening.

Also, no product code produces the stand-in `rights_and_freedoms_set_forth` (`grep` over `ve/`, `lean/`, `rust/`,
`tools/`). It appears only in recorded data: the frozen pilot translation
`usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md` (units u100b and u112, plus open_terms) and
`usecases/question-answering/udhr-part07.ve.md`.

## Proposal

- **sc-6 (this item):** delivers the Lean definitions, the theorem, F14/F14′/F14″ as `#guard`s over UDHR part
  documents (Art. 29–30 with right units; no stand-in term in them), the Python statement gate for 5.8, (5) the
  u0218.s18 regression and (6) the `list_names` check. It has no user-visible delta: no route changes, and a document
  without a rights reach answers byte for byte as main, with a fixture.
- **sc-6b (after pc-1 merges):** delivers the route: an effect word for the rights reach in `Wire.lean`, with
  `ScopeAdmission.lean`'s two proofs extended; `govern` writing the unit's `scope` through `Pinned.withReach`; the
  document-level F14/F14′ fixtures; and the widening row for the DRI. The pilot's next UDHR translation then writes
  the reach in place of the stand-in.

Is this move acceptable (R9), or do you rule otherwise?
