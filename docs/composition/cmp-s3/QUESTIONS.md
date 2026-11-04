# cmp-s3: questions for the DRI (2026-11-04)

Answered 16:05Z (reviews/dri-decisions-20261104-cmp-s3.md): Q1 A1 signed, Q2 plan accepted, Q3 B1 signed.

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

## Q3. `clauseSlot_labelled` (spec 8.4) is false as stated

Its hypotheses are `WellFormedClauses D` and `WellFormedRights (plain D)`. `Lim_D`'s own labels can repeat on a
well-formed rights document: `cx` (`lean/VE/NormDefaults/PacksLegacyExamples.lean:113`, the F1′ counterexample of
reviews/dri-decisions-20261027-featureplan-gates.md item 3) has limitations `x`, `x:p` and act keys `p:q`, `q`. At
`D := ⟨cx, [], []⟩` both hypotheses hold and `clauseSlotLabelled D = limPremisesLabelled cx` repeats
`rights:limitation:x:p:q:necessary:c`. Checked by `#guard` (scratch file, both true):
`WellFormedClauses dcx && WellFormedRights (plain dcx)` and `!wellLabelled (limPremisesLabelled (plain dcx))`.
Q1's depth corner is checked the same way: `budgetFormula 64` accepts a depth-64 formula and refuses it under one `and`.

Options:
- B1 (recommended): add `(hl : VE.Compose.Labelled.wellLabelled (limPremisesLabelled D.doc) = true)`. The theorem then
  says what S3 adds: the `Rel_D` labels are distinct, and none is a `Lim_D` label (prefix `rights:relation:`). The
  proof is short.
- B2: the precedent's hypothesis, `∀ k ∈ VE.Rights.condKeys D.doc, ':' ∉ k.2.1.toList`. Its proof
  (`legacy_labels_nodup_of_actKeys`) uses lemmas of `VE.Readings` (`rightsNames_of_chainWF`, `nodup_flatMap_iff`),
  which S3 may not import (spec 0). The proof would have to be copied without them, about 100 lines over the size cap.
