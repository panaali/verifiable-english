# cmp-s3: questions for the DRI (2026-11-04)

## Q1. `elaborate_plain` (spec 8.5) is false as stated

`elaborate_plain` concludes `decodeRightsSource (stripProfile environment) (elaborateJson D document) = .ok src` from
`WellFormedClauses D` and `WellFormedRights (plain D)`. The rights decoder reads every norm guard through
`VE.Norms.Wire.budgetFormula VE.Limits.maxDepth` (`lean/VE/Norms/Wire.lean:272`), which refuses a formula deeper than
64 (`ResourceLimit: formula depth exceeds 64`). `WellFormedRights` bounds nodes (W1, 10,000) but never depth
(`Norms/Tree.lean:330-347`, `SoftNorms/Soften.lean:500-512`).

Counterexample: one clause whose formula has depth 64 (it decodes: each clause is read with the same depth limit) on a
line with guard `top`. `plain` writes `.and .top c`, depth 65. `WellFormedClauses D` and `WellFormedRights (plain D)`
hold, but the plained JSON does not decode, so no `src` exists. The same happens for a guard of depth 60 with five
clauses. Nothing in the statement's hypotheses bounds the plain guard's depth.

Options (the statement is unchanged in A2):
- A1 (recommended): add one hypothesis, `(hd : PlainOnWire D)`: every plain guard has depth at most
  `VE.Limits.maxDepth` and at most `VE.Limits.maxNodes` nodes as the wire counts them. The head's fault order of 4.1
  stays as written: the inner route reports the decoder's own `ResourceLimit` at step 6.
- A2: keep the statement word for word; `decodeClauseDoc` refuses such a line itself, with the decoder's text
  `ResourceLimit: formula depth exceeds 64`. That moves the refusal from 4.1 step 6 to step 2 (before the clause checks
  of step 3), so it changes section 7's order.

## Q2. Registering `right-clauses@0` before any runner reads it

Task (2) puts `right-clauses@0` into the registered list (`VE.Compose.environmentProfiles`, the `environment` key of
ve/profile_table.json, Python's `BY_NAME`). No service mode runs the `.clauses` head yet. The `clauses-elaborate` mode
(Registry, Protocol, response shape and its encoder theorem, the relay) does not fit this item's size and goes to
cmp-s3b. Registered alone, the entry changes a profile-on text: with `readings@1` listed, Lean's environment mode
already admits the list (`Standalone.lean:310`), Python's `model_environment` stops refusing it ("Unsupported profile
right-clauses@0"), and the readings route answers "readings@1 is not the head of this profile list". That is not the
signed row ("read by the new head").

Plan unless the DRI rules otherwise: the registration lands in cmp-s3b with the head's mode, so this item changes no
answer and has no DELTA row.
