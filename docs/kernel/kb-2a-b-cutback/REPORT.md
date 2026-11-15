# kb-2a-b-cutback: the ties pass of kb-2a-b (REPORT)

**Current status (F1 review fix):** Fixed in `010c493e53`; no DRI signature reserved and no user-visible delta.
`Document.environmentOf` now calls two named refusal-site helpers. `routed_sites` proves the exception-conditioned
judgment/soft and soft/readings conditions on lowering profiles; both routing declarations tie to it. The updated
trust evidence cuts 229 counted lines. See `FIX-REPORT.md` for the probe, regression, mutation and test results.

## Original delivery report (before the F1 review fix)

**Summary.** Status: done; no DRI signature is reserved; no answer changes. Branch `feature/kb-2a-b-cutback` on pinned
main b6cbafe80a. The 15 untied trusted declarations of kb-2a-b's ties pass (13 of `Service/CoreCheck.lean`,
`DocumentFold.statuses`, `Document.decode`) are tied to theorems that state their purpose (new
`lean/VE/Service/CoreCheckProofs.lean`, P lines); measured cut **227** counted trusted lines against the target 133
(K +0, S +0, untied [V] -227; kb-2a-b's counted growth +283 falls to +56, inside R16's 150). Left untied, with reasons
below: `Document.Decoded`, `Document.encodeFields`, the schema declarations, and kb-2a's lowering (step 3). Next item:
kb-2a-c8.

SIZE: 603 product (Lean proofs and the moved round-trip proof: CoreCheckProofs.lean 549, CoreCheck.lean +33/-20,
VE.lean 1; no definition changed), 6 tests (one `#guard`; the encoder-class test of tests/test_trust_budget.py reads a tied entry's class), about 300 other hand-written lines (tools/trust-classes.json
ties +98/-15, the two evidence scripts 185, one `other_json` reason in ve/assurance-manifest.json) plus this REPORT and DELTA.md; machine-written evidence JSON excluded.

## Sources read

docs/kernel/kb-2a-b/FOLLOW-UPS.md (the ties pass), DELTA.md row 5, REPORT.md; the architect's DESIGN.md sections 2.3,
2.4 and 4; tools/trust_map.py's head comment (a tie: an entry `{"name", "tied"}` whose theorems are in
`lean/statements.txt` and whose statements use the declaration and an anchor, a K, S or untied [V] declaration);
reviews/dri-decisions-20261114-kb-2a-b.md item 1 and reviews/dri-decisions-20261115-adv1035.md item 2 (target: cut at
least 133).

## Deliverables

| # | Deliverable | Delivered | Evidence |
|---|---|---|---|
| 1 | Measure first, on the branch point | yes, a8aa0a001d (the branch's first commit, on b6cbafe80a) | `docs/kernel/kb-2a-b-cutback/trust-before.json` (`uv run python docs/kernel/kb-2a-b-cutback/trust_decls.py OUT`: trust_map's `walk`/`measure`, per file and per declaration, the 8 files) |
| 2 | The ties FOLLOW-UPS.md names | yes, all 15 declarations | the table below; `uv run python tools/trust_map.py --check` PASS; `mutants.json` |
| 3 | kb-2a's own ties pass, if shared | no: not shared (see "Left untied") | — |
| 4 | Re-measure on the final HEAD | yes | `trust-after.json`; `--check`: "against b6cbafe80a60: K +0, S +0, D +0, G +0, tied +227, unclassified +0, trusted -227 … PASS" |
| 5 | The ratchet, untouched by hand | yes (`git diff main -- docs/trust-baseline.json` empty) | budget below |

## The ties (declaration -> theorem; statements verbatim from lean/statements.txt)

| Declaration (lines) | Tied to | Anchor (K, S or untied [V]) in the statement |
|---|---|---|
| `CoreCheck.factsJson` (3), `CoreCheck.roundTrips` (8) | `facts_round_trip` (in CoreCheck.lean, beside `core_facts_round_trip`, whose proof now uses it: the existing statement does not mention either, so the step the tie needs is stated on its own) | `Route.Wire.encodeFormula` (D[V]) |
| `CoreCheck.unitStatus` (7), `CoreCheck.viewOf` (15) | `view_unit_status` | `Document.UnitStatus.name` (G[V]), `DocumentFold.Status` (S) |
| `DocumentFold.statuses` (3) | `statuses_lookup`, `view_unit_status` | `DocumentFold.UnitRow`, `Status` (S) |
| `CoreCheck.routed` (14) | `routed_iff` | `Document.environmentOf`, `listedProfiles` (D[V]) |
| `CoreCheck.routedRefusals` (5) | `routed_iff`, `routedRefusals_sites` | `environmentOf`; `Compose.layersApart` (G[V]) |
| `CoreCheck.runCaseReported` (16) | `runCaseReported_routes` | `Document.runCaseReported` (G[V]) |
| `CoreCheck.Inputs` (12), `CoreCheck.inputs` (22) | `inputs_reads`, `reads_status`, `reads_reading` | `Document.judgedViews` (G[V]), `Judgments.dependsOnC` (S) |
| `CoreCheck.reads` (11) | `reads_status`, `reads_reading` | `Judgments.dependsOnC` (S) |
| `CoreCheck.exceptionFormulas` (10) | `reads_status` | `Judgments.dependsOnC` (S) |
| `CoreCheck.tableOf` (10) | `tableOf_opens`, `document_core_sound` (existing: the answer is the fold over `tableOf`) | `DocumentFold.opens`, `UnitRow` (S) |
| `CoreCheck.statementJson` (8) | `statement_shown` | `encodeFormula` (D[V]) |
| `Document.decode` (83) | `decode_reads` | `environmentOf`, `unitsOf` (D[V]) |

The FOLLOW-UPS row asked for `viewOf`, `unitStatus` and `statementJson` to be tied to
`ResponseShape.Encoders.CoreCheck.view_fits`; no ResponseShape theorem is in `lean/statements.txt` (the dump reads the
VE tree), so `view_fits` cannot tie anything. They are tied to VE theorems instead, which state the rendering's purpose
(`view_fits` still states the shape).

What each statement says (the Lean text follows):
- `facts_round_trip`: when `roundTrips` holds, the kernel's facts decoder reads `factsJson P` as exactly `P`.
- `statuses_lookup` / `view_unit_status`: the `k`-th unit of the view's `units` shows `unitStatus` of
  `DocumentFold.status` of that unit's table row, and that name is CHECKED/OPEN/LABELLED/UNFORMALISED exactly when the
  fold's status is checked/opened/labelled/unformalised.
- `routedRefusals_sites` / `routed_iff`: `routed j` holds exactly for the documents whose environment `environmentOf`
  refuses (without the core flag) with one of the two refusals, whose profiles all have a lowering row, that list
  `judgments@0` and have no senses; the first refusal is `layersApart`'s text for `judgments@0` beside `soft-norms@0`
  (the exception-condition site), the second the soft-norms-with-readings text.
- `runCaseReported_routes`: a routed document is answered by `answer` or, when `answer` refuses for anything but a
  missing lowering row, by an error row marked `lowering`; every other document by `Document.runCaseReported`.
- `inputs_reads` / `reads_status` / `reads_reading`: under `judgments@0`, a core statement of a unit's own content reads
  exactly `Judgments.dependsOnC` of the unit's view (the view `check` gives `Judgments.status`) with the soft rule's
  exception conditions added; a statement of reading `i` of the unit's active set reads only terms
  `dependsOnC` finds in the view's `UnitView.reads` (when no earlier active set has the same id).
- `tableOf_opens`: the `k`-th table row is unit `k`'s, with its meaning, and a unit one of whose core statements (in any
  choice) reads a judgment term is OPEN whatever the kernel's rows (design 2.3).
- `statement_shown`: a statement is shown as the case carries it: its premise in the encoding `factsJson` sends, its
  rule as the norm object, a judgment by name, with feature and reading.
- `decode_reads`: `decode`'s environment is `environmentOf`'s on the front matter it read, with the `core` flag it was
  given; the document is judged exactly when that environment lists `judgments@0`, and then the environment carries the
  admitted names; the units are `unitsOf`'s.

```lean
theorem VE.Service.CoreCheck.facts_round_trip
  ∀ (src : VE.SoftNorms.Wire.SoftSource) (P : List VE.Formula),
    VE.Service.CoreCheck.roundTrips src P = Bool.true →
      VE.Compose.SlotWire.decodeFacts src (Lean.Json.mkObj [("facts", VE.Service.CoreCheck.factsJson P)]) =
        Except.ok (P, List.map VE.Route.Wire.encodeFormula P)
```
```lean
theorem VE.Service.CoreCheck.statuses_lookup
  ∀ (table : List VE.Kernel.DocumentFold.UnitRow) (rows : List VE.Kernel.Row) (id : String),
    List.lookup id (VE.Kernel.DocumentFold.statuses table rows) =
      Option.map (fun x => VE.Kernel.DocumentFold.status x rows) (List.find? (fun x => x.id == id) table)
```
```lean
theorem VE.Service.CoreCheck.view_unit_status
  ∀ (I : VE.Service.CoreCheck.Inputs) (docs : List (VE.Service.CoreDocument.Choice × VE.Service.CoreDocument.CoreDoc))
    (table : List VE.Kernel.DocumentFold.UnitRow) (rows : List VE.Kernel.Row) (k : Nat) (hk : k < I.rows.length)
    (u : VE.Kernel.DocumentFold.UnitRow),
    List.find? (fun x => x.id == I.rows[k].id) table = Option.some u →
      ∃ x,
        ((VE.Service.CoreCheck.viewOf I docs (VE.Kernel.DocumentFold.statuses table rows)).getObjValD "units").getArrVal?
              k =
            Except.ok x ∧
          x.getObjValD "status" =
              Lean.Json.str (VE.Service.CoreCheck.unitStatus (VE.Kernel.DocumentFold.status u rows)).name ∧
            (x.getObjValD "status" = Lean.Json.str "CHECKED" ↔
                VE.Kernel.DocumentFold.status u rows = VE.Kernel.DocumentFold.Status.checked) ∧
              (x.getObjValD "status" = Lean.Json.str "OPEN" ↔
                  VE.Kernel.DocumentFold.status u rows = VE.Kernel.DocumentFold.Status.opened) ∧
                (x.getObjValD "status" = Lean.Json.str "LABELLED" ↔
                    VE.Kernel.DocumentFold.status u rows = VE.Kernel.DocumentFold.Status.labelled) ∧
                  (x.getObjValD "status" = Lean.Json.str "UNFORMALISED" ↔
                    VE.Kernel.DocumentFold.status u rows = VE.Kernel.DocumentFold.Status.unformalised)
```
```lean
theorem VE.Service.CoreCheck.routedRefusals_sites
  VE.Compose.layersApart ["judgments@0", "soft-norms@0"] ["soft-norms@0"] =
      Except.error VE.Service.CoreCheck.routedRefusals[0] ∧
    VE.Service.CoreCheck.routedRefusals[1] =
        VE.Service.Document.unavailable "soft-norms with readings, alternatives or risk needs its composed Lean route" ∧
      VE.Service.CoreCheck.routedRefusals.length = 2
```
```lean
theorem VE.Service.CoreCheck.routed_iff
  ∀ (j : Lean.Json),
    VE.Service.CoreCheck.routed j = Bool.true ↔
      ∃ front body e,
        VE.Service.Document.frontOf j = Option.some (front, body) ∧
          (front.getObjVal? "senses").isOk = Bool.false ∧
            (∀ (p : String),
                p ∈ VE.Service.Document.listedProfiles (front.getObjValD "environment") →
                  p ∈ VE.Service.CoreDocument.rowProfiles) ∧
              "judgments@0" ∈ VE.Service.Document.listedProfiles (front.getObjValD "environment") ∧
                VE.Service.Document.environmentOf (front.getObjValD "environment") (front.getObjValD "units") Bool.false
                      (Option.some (VE.Discourse.Loader.optionalList front "open_terms")) =
                    Except.error e ∧
                  e ∈ VE.Service.CoreCheck.routedRefusals
```
```lean
theorem VE.Service.CoreCheck.runCaseReported_routes
  ∀ (j : Lean.Json),
    (VE.Service.CoreCheck.routed j = Bool.false →
        VE.Service.CoreCheck.runCaseReported j = VE.Service.Document.runCaseReported j) ∧
      (∀ (a : Lean.Json),
          VE.Service.CoreCheck.routed j = Bool.true →
            VE.Service.CoreCheck.answer j = Except.ok a → VE.Service.CoreCheck.runCaseReported j = a) ∧
        (∀ (m : String),
            VE.Service.CoreCheck.routed j = Bool.true →
              VE.Service.CoreCheck.answer j = Except.error m →
                VE.Service.CoreCheck.noRow m = Bool.true →
                  VE.Service.CoreCheck.runCaseReported j = VE.Service.Document.runCaseReported j) ∧
          ∀ (m : String),
            VE.Service.CoreCheck.routed j = Bool.true →
              VE.Service.CoreCheck.answer j = Except.error m →
                VE.Service.CoreCheck.noRow m = Bool.false →
                  (VE.Service.CoreCheck.runCaseReported j).getObjValD "status" = Lean.Json.str "error" ∧
                    (VE.Service.CoreCheck.runCaseReported j).getObjValD "lowering" = Lean.Json.bool Bool.true
```
```lean
theorem VE.Service.CoreCheck.inputs_reads
  ∀ {j : Lean.Json} {I : VE.Service.CoreCheck.Inputs},
    VE.Service.CoreCheck.inputs j = Except.ok I →
      I.active = VE.Discourse.Loader.activeOf I.d.all ∧
        (I.d.judged = Bool.true →
            VE.Service.Document.judgedViews I.d.E I.d.front I.d.names I.active I.d.units
                ((I.d.S.bind fun x => x.rules) <|> I.d.R.bind fun x => x.rules) I.d.R =
              Except.ok I.views) ∧
          I.meanings.length = I.d.units.length ∧
            I.sets.length = I.active.length ∧
              ∀ (k : Nat) (hk : k < I.active.length),
                ∃ c,
                  I.sets[k]? = Option.some (I.active[k].fst, c) ∧
                    VE.Service.Document.setCandidates I.d.E I.d.front I.active[k].fst = Except.ok c
```
```lean
theorem VE.Service.CoreCheck.reads_status
  ∀ {j : Lean.Json} {I : VE.Service.CoreCheck.Inputs},
    VE.Service.CoreCheck.inputs j = Except.ok I →
      I.d.judged = Bool.true →
        ∀ (k : Nat) (hk : k < I.d.units.length) (st : VE.Service.CoreDocument.Statement),
          st.origin.reading = Option.none →
            (∀ (t : VE.Judgments.Judgment), st.body ≠ VE.Service.CoreDocument.Body.judgment t) →
              ∃ v,
                I.views[k]? = Option.some v ∧
                  v.id = I.d.units[k].id ∧
                    VE.Service.CoreCheck.reads I I.d.units[k] st =
                        VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J
                          (v.own.toList ++
                            List.map VE.Judgments.Content.formula
                              (VE.Service.CoreCheck.exceptionFormulas
                                ((I.d.S.bind fun x => x.rules) <|> I.d.R.bind fun x => x.rules) I.d.units[k].content)) ∧
                      (v.set = Option.none →
                        VE.Service.CoreCheck.reads I I.d.units[k] st =
                          VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J
                            (v.reads ++
                              List.map VE.Judgments.Content.formula
                                (VE.Service.CoreCheck.exceptionFormulas
                                  ((I.d.S.bind fun x => x.rules) <|> I.d.R.bind fun x => x.rules) I.d.units[k].content)))
```
```lean
theorem VE.Service.CoreCheck.reads_reading
  ∀ {j : Lean.Json} {I : VE.Service.CoreCheck.Inputs},
    VE.Service.CoreCheck.inputs j = Except.ok I →
      I.d.judged = Bool.true →
        ∀ (k : Nat) (hk : k < I.d.units.length) (st : VE.Service.CoreDocument.Statement) (rs : VE.Discourse.FrontSet)
          (kinds : List Bool) (i : Nat),
          List.find? (fun x => x.fst.unit == I.d.units[k].id) I.active = Option.some (rs, kinds) →
            Option.map (fun x => x.fst) (List.find? (fun x => x.fst.id == rs.id) I.sets) = Option.some rs →
              st.origin.reading = Option.some (rs.id, i) →
                (∀ (t : VE.Judgments.Judgment), st.body ≠ VE.Service.CoreDocument.Body.judgment t) →
                  ∃ v,
                    I.views[k]? = Option.some v ∧
                      v.id = I.d.units[k].id ∧
                        v.set.isSome = Bool.true ∧
                          ∀ (x : String),
                            x ∈ VE.Service.CoreCheck.reads I I.d.units[k] st →
                              x ∈ VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J v.reads
```
```lean
theorem VE.Service.CoreCheck.tableOf_opens
  ∀ (I : VE.Service.CoreCheck.Inputs) (docs : List (VE.Service.CoreDocument.Choice × VE.Service.CoreDocument.CoreDoc))
    (k : Nat) (hk : k < I.d.units.length) (hm : k < I.meanings.length)
    (c : VE.Service.CoreDocument.Choice × VE.Service.CoreDocument.CoreDoc),
    c ∈ docs →
      ∀ (st : VE.Service.CoreDocument.Statement),
        st ∈ c.snd.statements →
          st.origin.unit = I.d.units[k].id →
            VE.Service.CoreCheck.reads I I.d.units[k] st ≠ [] →
              ∃ row,
                (VE.Service.CoreCheck.tableOf I docs)[k]? = Option.some row ∧
                  row.id = I.d.units[k].id ∧
                    row.meaning = I.meanings[k] ∧
                      VE.Kernel.DocumentFold.opens row = Bool.true ∧
                        ∀ (rows : List VE.Kernel.Row),
                          VE.Kernel.DocumentFold.status row rows = VE.Kernel.DocumentFold.Status.opened
```
```lean
theorem VE.Service.CoreCheck.statement_shown
  ∀ (st : VE.Service.CoreDocument.Statement),
    (VE.Service.CoreCheck.statementJson st).getObjValD "feature" = Lean.Json.str st.origin.feature ∧
      (∀ (φ : VE.Formula),
          st.body = VE.Service.CoreDocument.Body.premise φ →
            (VE.Service.CoreCheck.statementJson st).getObjValD "premise" = VE.Route.Wire.encodeFormula φ ∧
              Lean.Json.arr #[(VE.Service.CoreCheck.statementJson st).getObjValD "premise"] =
                VE.Service.CoreCheck.factsJson [φ]) ∧
        (∀ (r : Lean.Json),
            st.body = VE.Service.CoreDocument.Body.soft r →
              (VE.Service.CoreCheck.statementJson st).getObjValD "rule" = r) ∧
          (∀ (t : VE.Judgments.Judgment),
              st.body = VE.Service.CoreDocument.Body.judgment t →
                (VE.Service.CoreCheck.statementJson st).getObjValD "judgment" = Lean.Json.str t.name) ∧
            ∀ (s : String) (i : Nat),
              st.origin.reading = Option.some (s, i) →
                (VE.Service.CoreCheck.statementJson st).getObjValD "reading" =
                  Lean.Json.mkObj [("set", Lean.Json.str s), ("index", Lean.ToJson.toJson i)]
```
```lean
theorem VE.Service.CoreCheck.decode_reads
  ∀ (text : String) (lexicon packs governed governedSets parent : Option Lean.Json) (core : Bool)
    (d : VE.Service.Document.Decoded),
    VE.Service.Document.decode text lexicon packs governed governedSets parent core = Except.ok d →
      ∃ E,
        VE.Service.Document.environmentOf (d.whole.getObjValD "environment") (d.whole.getObjValD "units") d.senses
              (if (d.whole == d.doc.front) = Bool.true then
                Option.some (VE.Discourse.Loader.optionalList d.whole "open_terms")
              else Option.none)
              core =
            Except.ok E ∧
          d.senses = (d.whole.getObjVal? "senses").isOk ∧
            d.judged = E.profiles.contains "judgments@0" ∧
              (d.E =
                  if d.judged = Bool.true then
                    { json := E.json, checked := E.checked, rv := E.rv, profiles := E.profiles, envId := E.envId,
                      block := E.block, generated := E.generated, legacy := E.legacy, cardinality := E.cardinality,
                      boundNames := Option.some (Lean.ToJson.toJson d.J), events := E.events }
                  else E) ∧
                ∃ raw,
                  VE.Service.Document.unitsOf d.E d.R d.S d.N d.doc.source d.doc.fences lexicon d.names raw =
                    Except.ok d.units
```

## Trust before and after (per file, per class)

`trust-before.json` (branch point b6cbafe80a) and `trust-after.json` (final code), both by
`uv run python docs/kernel/kb-2a-b-cutback/trust_decls.py OUT` (trust_map's own `walk` and `measure`, problems: 0).

| File | K | S | D[V] | G[V] | tied | trusted before | trusted after | change |
|---|---|---|---|---|---|---|---|---|
| `lean/VE/Service/CoreCheck.lean` | 0 → 0 | 6 → 6 | 38 → 38 | 161 → 161 | 58 → 199 | 147 | 6 | -141 |
| `lean/VE/Kernel/DocumentFold.lean` | 0 → 0 | 31 → 31 | 0 → 0 | 12 → 12 | 9 → 12 | 34 | 31 | -3 |
| `lean/VE/Service/Document.lean` | 0 → 0 | 76 → 76 | 1228 → 1228 | 540 → 540 | 36 → 119 | 1808 | 1725 | -83 |
| `lean/ResponseShape/Schemas/Document.lean` | 0 → 0 | 0 → 0 | 0 → 0 | 300 → 300 | 0 → 0 | 300 | 300 | +0 |
| `lean/ResponseShape/Schemas/SoftNorms.lean` | 0 → 0 | 0 → 0 | 0 → 0 | 389 → 389 | 0 → 0 | 389 | 389 | +0 |
| `lean/VE/Compose/SlotWire.lean` | 0 → 0 | 12 → 12 | 51 → 51 | 36 → 36 | 87 → 87 | 12 | 12 | +0 |
| `lean/VE/SoftNorms/Run.lean` | 0 → 0 | 61 → 61 | 58 → 58 | 218 → 218 | 41 → 41 | 296 | 296 | +0 |
| `lean/VE/Service/CoreDocument.lean` | 0 → 0 | 0 → 0 | 0 → 0 | 202 → 202 | 55 → 55 | 147 | 147 | +0 |
| total | 0 → 0 | 186 → 186 | | | 286 → 513 | 3133 | 2906 | -227 |

Per declaration (counted before, tied after): `CoreCheck`: `factsJson` 3, `roundTrips` 8, `Inputs` 12, `inputs` 22, `exceptionFormulas` 10, `reads` 11, `tableOf` 10, `statementJson` 8, `unitStatus` 7, `viewOf` 15, `routedRefusals` 5, `routed` 14, `runCaseReported` 16 (141); `DocumentFold.statuses` 3; `Document.decode` 83. Classes are unchanged (the side table only adds `tied` lists); the counted lines fall because a validated tie is not counted.

Measured cut: **227** counted trusted lines (K + S + untied [V]) of the eight files, against the target 133. K +0,
S +0. No other file's trusted count changes (`trust_map.py --files` before and after: the only other files whose counts
change are `VE.lean` (+1 o), `VE/Audit.lean` (+21 T, generated) and the new `CoreCheckProofs.lean` (551 P, 29 o)).
kb-2a-b's counted growth, +283 (K +0, S +48, V +235), falls to +56.

## The ratchet

`docs/trust-baseline.json` is not edited (`git diff main -- docs/trust-baseline.json` is empty). Budget before (main):
K 1018, S 15000, V 48390 (64408 trusted). The count this HEAD would write with `tools/trust_map.py --write` on main:
K 1018, S 15000, V 48163 (`trusted 64181` in `--check`'s report: V = 64181 - 1018 - 15000), so the ratchet falls by
227 V lines against the 11-15 raise of S +48 / V +235.

## Left untied, and why

- `Document.Decoded` (23 lines, D[V]): `decode_reads` states the role of the fields the core path relies on (E, judged,
  senses, units), not of `records`, `openNames`, `R`, `S`, `N`, `all` or `attached`; tying the structure to it would
  claim more than it states. Conservative choice: left untied.
- `Document.encodeFields` (15 lines, G[V]): its purpose is the shape of the answer, which `ResponseShape`'s fits theorems
  state; those are outside `lean/statements.txt`, and a VE theorem about it would restate its body.
- `ResponseShape/Schemas/Document.lean` (`answerFields`, `core_view`, `core_row`) and `Schemas/SoftNorms.lean`: schema
  values; no theorem of `lean/statements.txt` reads them (the dump covers the VE tree only), so no tie is possible.
- `CoreCheck.AdmissionMeaning` (6 lines, S): a meaning, trusted by definition; not a tie target.
- Step 3, kb-2a's own ties pass (`Service/CoreDocument.lean`'s lowering, 147 trusted lines, to `slot_wire_admission`
  and `decodeSoftSource`): none of the theorems written here is about the lowering (they take its output, `docs`, as
  given), so they are not shared; left to its own item, as the task says.

## No answer changes

- No definition changed: `git diff main...HEAD -- lean/VE/Service/CoreCheck.lean` changes only proofs (the proof of
  `core_facts_round_trip` now uses `facts_round_trip`; its statement is unchanged in `lean/statements.txt`); no change
  to `Document.lean`, `DocumentFold.lean`, `CoreDocument.lean`, the encoders or the schemas.
- `CoreCheckExamples.lean`: existing examples unchanged; one `#guard` added (the answer's id is the request's, its view's
  `document_id` is not), which kills the `Inputs` mutant.
- `uv run python docs/kernel/kb-2a-b/status_compare.py --phase after`: the four fixtures' recomputed statuses are
  identical to kb-2a-b's recorded `after` (saved: `status-compare.json`; comparison "differing_statuses": 0); kb-2a-b's
  file restored unchanged.
- `zsh docs/kernel/kb-2a-b/frozen_keys.sh docs/kernel/kb-2a-b-cutback/frozen-keys.json`: rsp, preparedness, fsf,
  agent-policy and eligibility each exit 0 in check mode, `tree_changed_files` 0.
- `uv run python tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: "PASS: kernel 10101 <= 10101",
  "PASS: verdict writers outside the kernel 56 <= 56".
- `python3 lean/audit.py`: "PASS: 896 source files; 10113 named theorem declarations audited …; only the declared
  standard axiom allowlist." The new theorems use only propext, Classical.choice and Quot.sound (`lean/axioms.txt`).
- tests/test_kb2a_document.py and tests/test_judgments_chain.py: unchanged files, in the selected run (below).

## Seeded bugs and mutants

`uv run python docs/kernel/kb-2a-b-cutback/run_mutants.py OUT.json [ID …]` plants each one (an exact text replaced once),
runs `lake build VE.Service.CoreCheckProofs VE.Service.CoreCheckExamples`, restores the file, and maps each error to its
theorem or `#guard`. All 15 killed (`mutants.json`; the four seeded bugs also in `seeded-bugs.json`). Language: Lean only
(no Python or Rust product code changed).

| Id | Definition (file) | Mutation | Killed by |
|---|---|---|---|
| a (seeded) | `reads` (CoreCheck.lean) | drops the exception formulas | `reads_status` |
| b (seeded) | `unitStatus` (CoreCheck.lean) | labelled rendered UNFORMALISED | `view_unit_status` |
| c (seeded) | `routed` (CoreCheck.lean) | also accepts a soft-norms@0 document with alternatives@0 | `routed_iff` |
| d (seeded) | `factsJson` (CoreCheck.lean) | drops the last formula | `facts_round_trip` |
| m-roundTrips | `roundTrips` | no soft-decision-predicate check | `facts_round_trip` |
| m-viewOf | `viewOf` | renders the unit's own status | `view_unit_status` |
| m-statuses | `DocumentFold.statuses` (DocumentFold.lean) | folds over no rows | `statuses_lookup` |
| m-routedRefusals | `routedRefusals` | first text loses "Lean" | `routedRefusals_sites` |
| m-runCaseReported | `runCaseReported` | refusal not marked `lowering` | `runCaseReported_routes` |
| m-Inputs | `Inputs` | fields `id` and `documentId` swap | CoreCheckExamples.lean:63 `#guard` (answer id) |
| m-inputs | `inputs` | reads no judgment views | `inputs_reads` |
| m-exceptionFormulas | `exceptionFormulas` | drops the sufficient conditions | CoreCheckExamples.lean:66 `#guard` (u3 OPEN) |
| m-tableOf | `tableOf` | keeps, for a non-asserting unit, the statements that read nothing | `tableOf_opens` |
| m-statementJson | `statementJson` | premise shown as null | `statement_shown` |
| m-decode | `Document.decode` (Document.lean) | environment read without the core flag | `decode_reads` |

No trust-mutants sweep: build checklist 13a applies to trusted growth (R16) and this item has none; the light-lane check
printed NOT only because of the new proofs file. The task asks for hand mutants per tied definition, above.

## Tests

- Selected run, `MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`
  on the committed tree 6f73ffcc56 (HEAD 7093d0ea40, before the fix commit 4ea32f1aa3; ran on ve-cloud-2, 6707 s): 557 units, 2 failed:
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (the new proofs file had no
  `other_json` reason) and `tests/test_trust_budget.py::test_formula_and_report_encoders_are_verdict_bearing` (it read a
  tied table entry as a class string). Both fixed in the next commit and rerun alone:
  `zsh manage-agents/mac-pytest.sh -- <the two ids>`: "2 passed". tests/test_kb2a_document.py (exit 0, 534 functions),
  tests/test_judgments_chain.py (exit 0), tests/test_trust_ratchet.py (exit 0) passed unchanged in the selected run.
- Not run by me: the full gate (the chain runs it on the final HEAD).

## Notes for the DRI

- The FOLLOW-UPS row's `view_fits` tie is impossible as written (ResponseShape theorems are not in the dump); the VE
  theorems above tie the same declarations.
- `regen_generated.py --write` was run with `--skip route-cases`: that generator needs the Rust release binary, which
  this worktree has not built, and none of its inputs changed; the gate's `--check` covers it.
- kb-2a-b's own docs (FOLLOW-UPS.md) are left as they were; this REPORT records the ties pass as done.

## Next item

kb-2a-c8 (blocked by this item): the next growth on the CoreCheck shell. Its own ties now have the theorems above to
extend (`routed_iff` for its routing change, `reads_status` for the fold's reads).

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no answer, schema or relay changed.
2. Every required deliverable built: PASS, the Deliverables table (step 3 not shared, said so; `run_mutants.py`, `trust_map.py --check`).
3. Tests and gates can fail: PASS, 15 mutants killed (`mutants.json`, `seeded-bugs.json`); no R16 growth, so no trust-mutants sweep.
4. Python, Lean and Rust agree: PASS, no answer changed: `status-compare.json` (0 differing), `frozen-keys.json` (5 exit 0).
5. R8 binding: N.A., no binding changed.
6. Gate evidence matches the final HEAD: PASS, evidence regenerated on the final code; the gate runs on the final HEAD (chain).
7. No unsigned item: PASS, DELTA.md has one R12 row; trust falls, no allowance.
8. Every user-visible change in DELTA: PASS, none (status comparison and frozen keys unchanged).
9. Test selection finds the tests: PASS, `tools/select_tests.py --base $(git merge-base HEAD main)` selects tests/test_kb2a_document.py, tests/test_judgments_chain.py, tests/test_trust_budget.py.
10. Lean statements say what is claimed: PASS, each tie theorem broken by a mutant of its definition (`mutants.json`); no approved statement changed (`git diff main -- lean/statements.txt` adds only); no `tools/check_*_statements.py` covers these modules.
11. Budgets, limits, deadlines: N.A., no evaluator or limit changed.
12. No CPU or memory regression: N.A., proofs only; no executable code changed.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS, the iff theorems (`routed_iff`, `view_unit_status`) state both directions; claims cite commands above; spec re-read: FOLLOW-UPS.md row and the task's (2) list, statement by statement in "What each statement says".
15. Four classes: no overclaim PASS (each "unchanged"/"all" above names its command); no silent cut PASS (untied list with reasons); every new check can fail PASS (`mutants.json`, incl. the new `#guard`); limits charged before work N.A. (no evaluator).
