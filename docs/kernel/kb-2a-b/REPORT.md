# kb-2a-b: the document mode on the core document (build report)

**STOPS for one DRI signature: DELTA.md row 5, trusted Lean growth +268 (K +0, S +48, V +220), above R16's 150
lines; requested in `manage-agents/inbox/dri/20261114T185627Z-builder-kb-2a-b-76207.md`.** Everything else is
built; no status differs (part 4); every Python/Lean difference on the acceptance document has a cause (part 4b).

Code: worktree `ve-kb-2a-b`, branch `feature/kb-2a-b`, base `4a5d3460d3`. What changed: the document mode's entry is
`VE.Service.CoreCheck.runCaseReported`; documents that reached the refusals of `Document.lean` 1198-1199 or 1207-1208,
every profile with a lowering row and no senses, are lowered (`VE.Service.CoreDocument`, promoted from the
experimental tier), admitted by the soft route's new `slot-admission` kind one row per choice, and answered by the
kernel fold `VE.Kernel.DocumentFold` through `VE.Kernel.shell`; a lowering refusal for a feature with no row keeps
today's path; Python binds and renders the answer and never falls back for such a document.

SIZE: 1008 product, 2200 tests, 5369 other hand-written lines (`git diff --numstat 4a5d3460d3 HEAD`, generated files
excluded: 6670 lines; "tests" includes the 2,000-line acceptance document and its generator's output, "other" the
docs, records, probes (JT-a, SC-a: 1,400 lines), status comparison, trust classes and registry).

## Deliverables

| Part | Where | Evidence |
|---|---|---|
| (1) kernel row `slot-admission` | `lean/VE/Compose/SlotWire.lean` (`SlotAdmission`, `replaySlotAdmission`, `SlotAdmitted`, `replaySlotAdmission_sound`), `lean/VE/SoftNorms/Run.lean` (`slotAdmissionAnswer`, the kind in `runSoftKind`), `lean/VE/SoftNorms/SlotSound.lean` (`slot_wire_admission`); registry `softNorms` | `lake build`; `#guard`s in `SlotExamples.lean` and `ResponseShape/SlotExamples.lean`; kernel +18 (ALLOWANCES) |
| (2) the fold | `lean/VE/Kernel/DocumentFold.lean` (44 code lines; `fold_checked_iff`, `fold_reads_rows_only`); registry `document.fold` | `lean/VE/Kernel/DocumentFoldExamples.lean`; seeded bug (a) |
| (3) the shell | `lean/VE/Service/CoreCheck.lean` (`document_core_sound`, `core_facts_round_trip`, `casesOf_ok`, `firstRefused_none`); `CoreDocument.lean` moved to `VE.Service` | `lean/VE/Service/CoreCheckExamples.lean`; seeded bug (b) |
| (4) routing | `Document.lean`: `check`'s decode stage as `decode` (same code, same order), `environmentOf`'s `core` flag (the two refusals skipped, the soft source read without `readings@1`), `encodeFields`; `Protocol.lean` dispatches to `CoreCheck.runCaseReported` | `status-compare.json`: 0 differing statuses; `test_judgments_chain.py`'s pinned test replaced in the same commit (67aacfbbb4) |
| (4b) Python before | `docs/kernel/kb-2a-b/python-before.json`, `python-vs-lean.md` | `tests/test_kb2a_document.py::test_kb2a_python_before_recorded` |
| (5) Python | `ve/document/core.py` (bind, render), `ve/document/lean.py` (no fallback for a `lowering` refusal), `ve/document/load.py` (`_core_document`, `lean_answer`), `ve/document/report.py`, `ve/document/cli.py` (`--json`), `ve/backends/relay.py` (the mark) | `tests/test_kb2a_document.py`; seeded bug (d) |
| (6) acceptance | `tests/data/kb2a/rsp-mixed.ve.md` (`docs/kernel/kb-2a-b/build_rsp_mixed.py`), golden `tests/data/kb2a/rsp-mixed.answer.json`, `tests/test_kb2a_document.py`, `docs/kernel/kb-2a-b/audit-packet.md` | 10 tests pass (`uv run pytest -q tests/test_kb2a_document.py`: "10 passed in 9.68s") |
| (7) measurements | `docs/kernel/kb-2a-b/latency.json` (`latency.py`), `docs/kernel/closure-baseline.json`, `docs/kernel/ALLOWANCES.md` (the two lines of DESIGN 4) | below |

## Theorems (verbatim)

`lean/VE/SoftNorms/SlotSound.lean`:

```lean
theorem slot_wire_admission (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "slot-admission") (hn : usesSoftPath j = true) :
    ∃ (id : String) (r : SlotAdmission),
      VE.Bridge.stringField j "id" = .ok id ∧ (j.getObjVal? "facts").toBool = true ∧
      replaySlotAdmission j = .ok r ∧
      decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
      WellFormedSoft r.src.D = true ∧ r.src.D.E = r.src.se.ne.rv.environment ∧
      r.src.D.lits = r.src.se.ne.rv.literals ∧
      decodeFacts r.src j = .ok (r.facts, r.items) ∧ VE.Compose.SlotWellFormed r.src.D r.facts ∧
      answer = slotAdmissionAnswer id r
```

`lean/VE/Compose/SlotWire.lean`:

```lean
theorem replaySlotAdmission_sound (j : Json) (r : SlotAdmission) (h : replaySlotAdmission j = .ok r) :
    SlotAdmitted j r
```

`lean/VE/Kernel/DocumentFold.lean`:

```lean
theorem fold_checked_iff (u : UnitRow) (rows : List Row) :
    status u rows = .checked ↔
      u.statements ≠ [] ∧ opens u = false ∧ asserted u = true ∧ ∀ r ∈ rows, r.result.isOk = true
```

`lean/VE/Kernel/DocumentFold.lean`:

```lean
theorem fold_reads_rows_only (p : Path) (elaborate : Json → Except String (List Json))
    (view : List (String × Status) → Json) (table : List UnitRow) (request answer : Json)
    (h : shell p elaborate (fold view table) request = .ok answer) :
    ∃ rows : List Row, (∀ r ∈ rows, p.Ran r) ∧ answer = fold view table request rows
```

`lean/VE/Service/CoreCheck.lean`:

```lean
theorem casesOf_ok {docs : List (Choice × CoreDoc)} {cases : List Json} (h : casesOf docs = .ok cases) :
    cases.length = docs.length ∧
      ∀ k (hk : k < docs.length), cases[k]? = some (caseOf k docs[k].2) ∧ caseFault docs[k].2 = none
```

`lean/VE/Service/CoreCheck.lean`:

```lean
theorem core_facts_round_trip {docs : List (Choice × CoreDoc)} {cases : List Json} (h : casesOf docs = .ok cases)
    (k : Nat) (hk : k < docs.length) (src : VE.SoftNorms.Wire.SoftSource)
    (hs : VE.SoftNorms.Wire.decodeSoftSource ((caseOf k docs[k].2).getObjValD "environment")
      ((caseOf k docs[k].2).getObjValD "norms") = .ok src) :
    cases[k]? = some (caseOf k docs[k].2) ∧
      decodeFacts src (caseOf k docs[k].2) =
        .ok (docs[k].2.premises, docs[k].2.premises.map VE.Route.Wire.encodeFormula)
```

`lean/VE/Service/CoreCheck.lean`:

```lean
theorem document_core_sound (j row : Json) (h : answer j = .ok row) :
    ∃ p : Prepared, prepare j = .ok p ∧
      lower p.I.d.E p.I.d.senses p.I.d.records p.I.views p.I.d.units p.I.sets [] = .ok p.docs ∧
      p.cases.length = p.docs.length ∧ (∀ k (hk : k < p.docs.length), p.cases[k]? = some (caseOf k p.docs[k].2)) ∧
      ∃ rows : List Row, rows = p.cases.map softNormsPath.row ∧
        (∀ r ∈ rows, softNormsPath.Ran r ∧ ∃ x, r.result = .ok x ∧ softNormsPath.Meaning r.case x) ∧
        row = VE.Route.Wire.ok p.I.id
          [("view", (fold (viewOf p.I p.docs) (tableOf p.I p.docs) j rows).getObjValD "view"),
           ("rows", (fold (viewOf p.I p.docs) (tableOf p.I p.docs) j rows).getObjValD "rows")]
```


The fold's rule (DESIGN 2.3), `lean/VE/Kernel/DocumentFold.lean`:

```lean
def opens (u : UnitRow) : Bool := u.statements.any (!·.reads.isEmpty) || u.set == some false || u.rightsOpen

/-- The unit asserts its statements: its active set decides it, or, with none, its meaning is specified. -/
def asserted (u : UnitRow) : Bool := u.set == some true || (u.set.isNone && u.meaning == "specified")

/-- A status that no core statement decides, as today (`Loader.w2Status` without content). -/
def baseless (meaning : String) : Status :=
  if meaning == "open" then .opened else if meaning == "unformalised" then .unformalised else .labelled

def status (u : UnitRow) (rows : List Row) : Status :=
  if opens u then .opened
  else if u.statements.isEmpty || !asserted u then baseless u.meaning
  else if rows.all Row.ok then .checked else .opened
```

`fold_checked_iff` has one conjunct more than the task's wording: `asserted u = true` (the unit's meaning class
asserts its statements: its active set decides it, or with none its meaning is `specified`). DESIGN 2.3 keeps
"LABELLED / UNFORMALISED exactly as today", and today an `open`-meaning unit with content and no set is OPEN
(`Loader.w2Status`), so the meaning class is part of the rule; without the conjunct such a unit would be CHECKED.

`python3 lean/audit.py`: "PASS: 884 source files; 10058 named theorem declarations audited (headline results and helper
lemmas); only the declared standard axiom allowlist." (/tmp/kb2ab/audit2.log; no new axiom.)

## Decisions taken (conservative, recorded here; not asked)

- **The `slot-admission` case is `{environment, norms, facts}`**, not the soft `admission` kind's `{environment, document}`:
  a core document (step A's `CoreDoc`) carries a soft source and premises, no W2 claim graph, and `admitDocument` needs
  one. Its theorem states the source part of `runAdmission_sound`'s conclusion (`SourceDecoded`: decoded,
  `WellFormedSoft`, vocabulary and literals) plus `decodeFacts src j = .ok (P, items)` and `SlotWellFormed src.D P`, as
  DESIGN 2.2 words it. The answer is `{id, status, rules, facts}`: no verdict word.
- **Routing.** The task routes "exactly the documents that today reach" the two refusals. Two narrowings, both from
  DESIGN 2 ("one path for every document whose features have a lowering") and 5 (norm-defaults leaves the fallback in
  step C row 2): (a) every profile must have a lowering row and the document no senses (`CoreCheck.routed`), so
  `norm-defaults@0`, `scope@0`, rights and the like keep today's code; (b) a routed document whose lowering refuses
  `UnsupportedLowering` (a feature with no row: a soft reading, couplings, narrowings, a claim graph, completions)
  keeps today's answer (`noRow`). (b) was found on the FSF D1 translation (292 units, soft default readings): without
  it Lean refused the document that Python decided before. With both, the task's four fixtures and FSF D1 keep every
  status. Neither refusal text could be deleted: both still fire for the documents (a) and (b) keep on today's path.
- **The judgment condition reads a soft rule's exception conditions** (`CoreCheck.exceptionFormulas`): DESIGN 2.3 says
  OPEN "if a statement of the unit reads a judgment term", and a rule reads its exception; `Judgments.softContent`
  reads only the guard and carve-outs (pc-1 review F1). `Judgments.status`'s own refusals run unchanged in the
  lowering, so a term listed and read only in an exception is refused `JudgmentListedUnused`.
- **Statuses are typed in the fold** (`DocumentFold.Status`, rendered by `Document.UnitStatus`): the measure's verdict
  writers outside the kernel stay 56 (`tools/kernel_closure.py --check`: "PASS: verdict writers outside the kernel 56 <=
  56").
- **The acceptance document** (`build_rsp_mixed.py`'s docstring lists each difference from D1): RS3o (the first candidate
  for iii) cannot be lowered (its reading `iff` is two rules; a reading carries one content); RS8 (strict or default)
  cannot either (a reading's rule is lowered as a strict W1 rule only); so (iii) is t1-plan with RS1 (cond, uncond,
  ov pending; probe P2's set). W2 calls a set `authored` only with one signed reading, so the two-reading set is
  `open`. s35-aim (i) carries its RS12 default reading as content (probe DF-b's collapse): no D1 unit has a soft rule as
  its own content. OT1, OT4, OT5 are declared on the predicates the rules read (probe JT-c's re-expression; P8 shows the
  D1 tokens are `JudgmentUnbound`). Each unit is preceded by a `meta` unit quoting its full source sentence. intro-aspire,
  the aspiration (v), is UNFORMALISED as D1 marks it; the LABELLED units are the six headers.
- **`python-before.json`** was first recorded on a draft of the document (s32-strong-attempt with RS8) and re-recorded
  on the final document in a worktree of the base: the same exit code and answer.

## Status comparison (part 4)

`docs/kernel/kb-2a-b/status-compare.json` (`status_compare.py`, `ve document check`'s statuses, base and final code):

| Fixture | Before (Python's fallback) | After | Units differing |
|---|---|---|---|
| tests/data/rd9-docroute.ve.md | u1, u2 CHECKED | the same (not routed: norm-defaults@0) | 0 |
| JT-a (fsf-r2) | refused: `CheckerUnavailable: judgments@0 documents are checked by Lean's document mode` | refused by Lean: `JudgmentUnbound: ot1_level_reached` | 0 (no status either side) |
| SC-a (fsf-r2) | refused: `UnsupportedProfile: Unsupported profile scope@0` | the same (not routed: scope@0) | 0 |
| probe-translation.probe.md | 4 sets of statuses (LABELLED, UNFORMALISED, OPEN, CHECKED) | the same (not routed: norm-defaults@0) | 0 |
| FSF D1 (found while building; pinned source) | 292 statuses | the same (no row for its soft readings) | 0 |

## Python and Lean on the acceptance document (part 4b)

Before: Lean `CheckerUnavailable` (1207-1208), then Python's loader refused (`ve document check` exit 5). After: Lean's
answer, exit 0. `python-vs-lean.md` lists 11 differences, each with its file:line or rule; none unexplained.

## Measurements (part 7)

Latency (`docs/kernel/kb-2a-b/latency.json`, `python3 docs/kernel/kb-2a-b/latency.py --before <base worktree> --after
.`, median of 5, each run in its own scope through `manage-agents/iso.sh`; VM 5-min load 41 to 66 on 32 vCPU):

| Document | Before | After | Ratio | Peak memory before / after |
|---|---:|---:|---:|---:|
| tests/data/kb2a/rsp-mixed.ve.md | 0.61 s (exit 5, Python's refusal) | 2.26 s (exit 0) | 3.7 | 104.6 / 107.5 MB |
| usecases/question-answering/udhr-part07.ve.md | 8.19 s | 7.47 s | 0.91 | 105.8 / 109.2 MB |
| usecases/question-answering/agent-policy/a-rules.ve.md | 143.58 s | 133.86 s | 0.93 | 105.3 / 109.3 MB |

The 1.25x bound holds for both existing documents; the 120 s bound is missed by a-rules before and after alike on the
loaded VM (not by this change: ratio 0.93). Peak memory is `/usr/bin/time -v`'s maximum resident set of the command.

Kernel and paths (`uv run python tools/kernel_closure.py`, base `docs/kernel/closure-baseline.json` and the regenerated
one):

| Figure | Before | After |
|---|---:|---:|
| `kernel_lines` | 10,023 | 10,041 (+18) |
| softNorms path: spec / wrap / lines | 5,368 / 35 / 5,376 | 5,386 / 35 / 5,394 |
| `document` path: spec / wrap / lines | 35,023 / 12,826 / 35,849 | 35,567 / 12,816 / 36,420 |
| verdict writers outside the kernel (`verdict_writers`) | 56 | 56 |
| keyed lines (frozen keys) | 16,777 | 16,795 |

The fold (44 code lines) sits on the `document` path, a candidate, so `kernel_lines` does not count it (ALLOWANCES.md
row: +0, signed up to +60). The task's "within the signed +120": +18.

The five frozen keys (`docs/kernel/kb-2a-b/frozen-keys.json`, `frozen_keys.sh`): `anthropic-rsp/run.py --check`,
`openai-preparedness/run.py --check --base-only`, `safety-framework/run.py --check`, `agent-policy/check.py base`,
`eligibility/run.py --no-write --no-mutants`: each exit 0 (every saved result recomputed byte for byte), the tree clean
after them.

## Seeded bugs (`docs/kernel/kb-2a-b/seeded-bugs.json`; Lean and Python, each planted alone and restored)

| Bug | File | Caught by |
|---|---|---|
| (a) the fold reports CHECKED with a refused row | lean/VE/Kernel/DocumentFold.lean | `fold_checked_iff` fails to build (DocumentFold.lean:56) |
| (b) the shell sends only the first choice's core document | lean/VE/Service/CoreCheck.lean | the theorem: `casesFrom_ok` (so `casesOf_ok`, `document_core_sound`) fails to build; the golden test was not needed |
| (c) `slot-admission` answers ok without decoding the facts | lean/VE/Compose/SlotWire.lean | `replaySlotAdmission_sound` (so `slot_wire_admission`) fails to build (SlotWire.lean:410) |
| (d) Python falls back when Lean refuses | ve/document/lean.py | `tests/test_kb2a_document.py::test_document_lowering_never_falls_back_to_python` |
| (e) the carried rows omit `facts` | lean/VE/Kernel/DocumentFold.lean | the build (`ResponseShape.Encoders.CoreCheck.fold_eq`), and with that proof stubbed `::test_document_lowered_facts_inconsistent_no_verdict` |
| (f) the judgment condition ignores exceptions | lean/VE/Service/CoreCheck.lean | `tests/test_judgments_chain.py::test_a_judgment_term_read_only_in_an_exception_makes_the_unit_open` |

## Trust mutants

TRUSTMUT_PLACEHOLDER

## Runs (each once on the code as committed, unless noted)

- `lake build`: "Build completed successfully (1461 jobs)" (/tmp/kb2ab/lake-full.log, at 0f12aeacf9; later Lean commits
  rebuilt their modules and `ve_service`, and `tools/lean_statements.py` built the whole tree each time).
- `python3 lean/audit.py`: PASS (above), at bfb587712b.
- `uv run python tools/regen_generated.py --write`: "wrote 41 entries", last at e9dcebbd2a.
- `uv run python tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: "PASS: kernel 10041 <= 10041",
  "PASS: verdict writers outside the kernel 56 <= 56".
- `uv run python tools/trust_map.py --check`: exit 1 only on the budget (row 5, awaiting the DRI's signature): "against
  4a5d3460d36c: K +0, S +48, D +86, G +283, tied +80, unclassified +0, trusted +268".
- Tests while iterating: `tests/test_kb2a_document.py` (10 passed), `tests/test_judgments_chain.py` (46 passed),
  `tests/test_kernel_closure.py` (after fixes), `tests/test_relay_binding_inventory.py::test_every_schema_field_is_classified`
  (19 passed).
- SELECTED_PLACEHOLDER
- Not run by me: the full gate (the chain runs it on the final HEAD).

## For each step C group (DESIGN section 5): what the code shows

1. **soft-norms alone, norms alone.** Neither reaches a routed refusal today, so moving them needs a routing rule other
   than the refusal texts. The lowering embeds a strict norm only where the environment lists `soft-norms@0`
   (`CoreDocument.strictRule`): a plain `norms@0` document's norms are `UnsupportedLowering`, so its row needs either the
   soft decoder without `soft-norms@0` or a norms kernel row.
2. **norm-defaults.** No row; rd9 and the constitution probe reach 1207-1208 today and keep Python's fallback
   (`_python_decides_mixed_readings` decides pending readings under it). Soft (default) readings, as in FSF D1, need a
   candidate type the lowering has not (`Judgments.Content` has no soft rule; `Document.setCandidates` reads W1 rules
   only): this is the row that moves FSF D1.
3. **rights.** Rights documents never reach 1207 (`soft` excludes `rights@0`). The fold already takes the rights route's
   `opens` (`UnitRow.rightsOpen`); the lowering refuses a rights block (no row).
4. **definitions.** The lowering refuses non-empty `E.rv.definitions`; the fold's `reads` already goes through
   `Judgments.dependsOn` with the definitions, so only the lowering needs the row.
5. **scope and senses.** A `scope@0` document is decoded through `checkDocSets`' scope branch (`withUnits`), and
   `Scope.foldGovernors` reads the plain answer's top-level `units`; the core answer has them under `view`, so the
   governor fold needs the view. Senses: `decode` reads them (`sensesLayer`), the routing excludes them.
6. **alternatives and risk.** `environmentOf` refuses them beside `judgments@0` (`judgmentsApart`) and at 1207-1208; the
   view already writes a block's coverage line (`blockCoverage`).
7. **cardinality and events.** `environmentOf` returns early for `cardinality@0`; `eventsView` refuses `readings@1`.
8. **The matrix.** The two refusal texts still fire (part 4); tests and examples pinning them read `Document.*` functions
   directly (Lean: DocumentChainExamples.lean:173, DocumentChainChecks.lean:83-88, Compose/Examples.lean:736,
   Judgments/ChainExamples.lean:178) or saved evidence (`test_safety_framework.py`), or documents with
   `norm-defaults@0` (`test_document_chain.py`).

## Notes for the DRI

- Part (4)'s routing is narrower than "exactly the documents that reach the refusals" in two ways (Decisions, above);
  both keep a document Python decided on Python's path rather than refuse it.
- `CoreCheck.lean` is 419 lines (the task said at most 300; standing override 1): about 150 are its theorems.
- The kernel fold is not in `kernel_lines` while the `document` path is a candidate; it enters when the architect seat
  makes the path a kernel path.
- kb-2a's own ties pass (its FOLLOW-UPS.md) is still open: the module was promoted, not tied.

FOLLOWUP_PLACEHOLDER

## Self-review against BUILDER-CHECKLIST

SELFREVIEW_PLACEHOLDER
