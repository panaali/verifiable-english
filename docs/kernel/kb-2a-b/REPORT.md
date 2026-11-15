# kb-2a-b: the document mode on the core document (build report)

**STOPS for one DRI signature: DELTA.md row 5, trusted Lean growth +283 (K +0, S +48, V +235), above R16's 150
lines; requested in `manage-agents/inbox/dri/20261114T185627Z-builder-kb-2a-b-76207.md`.** Everything else is
built; no status differs (part 4); every Python/Lean difference on the acceptance document has a cause (part 4b).

Code: worktree `ve-kb-2a-b`, branch `feature/kb-2a-b`, base `4a5d3460d3`. What changed: the document mode's entry is
`VE.Service.CoreCheck.runCaseReported`; documents that reached the refusals of `Document.lean` 1198-1199 or 1207-1208,
every profile with a lowering row, `judgments@0` listed and no senses, are lowered (`VE.Service.CoreDocument`, promoted from the
experimental tier), admitted by the soft route's new `slot-admission` kind one row per choice, and answered by the
kernel fold `VE.Kernel.DocumentFold` through `VE.Kernel.shell`; a lowering refusal for a feature with no row keeps
today's path; Python binds and renders the answer and never falls back for such a document.

SIZE: 1025 product, 2330 tests, 5709 other hand-written lines (`git diff --numstat 4a5d3460d3`, generated files and
the trust-mutants records excluded: 8857 lines; "tests" includes the 2,000-line acceptance document and its generator's output, "other" the
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
- **Routing.** The task routes "exactly the documents that today reach" the two refusals. Three narrowings, from
  DESIGN 2 ("one path for every document whose features have a lowering"), 2.5 and 5 (norm-defaults leaves the
  fallback in step C row 2), each keeping a document on the path that answers it today rather than taking its answer
  away: (a) every profile must have a lowering row and the document no senses, so `norm-defaults@0`, `scope@0`,
  rights and the like keep today's code; (b) the document lists `judgments@0` (`CoreCheck.routed`): a document without
  it that reaches 1207-1208 (`soft-norms@0` with `readings@1`) is decided today by Python's fallback, whose document
  `ve document readings` and the readings queries read, and the core path has no reading query yet (found by the
  selected run: five tests of `tests/test_readings_s2_document.py` lost their documents); Python's loader refuses every
  `judgments@0` document, so routing those takes nothing away; (c) a routed document whose lowering refuses
  `UnsupportedLowering` (a feature with no row: a soft reading, couplings, narrowings, a claim graph, completions)
  keeps today's answer (`noRow`; found on the FSF D1 translation, 292 units with soft default readings, before (b)
  existed). The task's four fixtures and FSF D1 keep every status. Neither refusal text could be deleted: both still
  fire for the documents (a) to (c) keep on today's path.
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
| `document` path: spec / wrap / lines | 35,023 / 12,826 / 35,849 | 35,569 / 12,824 / 36,430 |
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

`zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --budget 9300 --json
docs/kernel/kb-2a-b/trust-mutants.json --allow docs/kernel/kb-2a-b/trust-mutants-allow.json --test
lean/VE/Service/CoreCheckExamples.lean --test lean/VE/Kernel/DocumentFoldExamples.lean --test
lean/ResponseShape/CoreCheckExamples.lean --test lean/VE/Service/CoreDocumentExamples.lean --test
lean/VE/SoftNorms/SlotExamples.lean --test lean/ResponseShape/SlotExamples.lean` on 3d02a576a6 (VM, 8 jobs): **PARTIAL**,
the budget stopped it with 169 of 940 mutants judged: 124 KILLED, 40 ALLOWED, 2 INVALID, 1 SURVIVOR, 2 UNKNOWN, 771 NOT
RUN (`docs/kernel/kb-2a-b/trust-mutants-part1.json`, also `trust-mutants.json`). The survivor (`roundTrips`' level
`0 -> 1`) is killed since by the `x_permitted` guard of CoreCheckExamples.lean; the unknowns are `environmentOf`'s
`!= -> ==` at Document.lean:1208 (the tool reads ComposeExamples.lean:245 as unreadable; the `envWith` guards of
CoreCheckExamples.lean fail on it) and one more of the same definition. History: a first sweep on ve-cloud-2 (e9dcebbd2a,
no allow file, before most guards) was cut by the host at 11,399 s without a record; its log listed 109 SURVIVOR or
UNKNOWN, which the guards of e9dcebbd2a..d75a2686b6 and the allow file (40 entries, each with its one-line reason:
S propositions, mutants that do not elaborate, equivalents, default-argument flips) address. A continuation from the
partial record was a full rerun (inputs changed; 1,022 mutants since `noRow`), more than ten hours on the VM at the
measured rate (9,254 s for 169), and was stopped. Completing the sweep is open (FOLLOW-UP below).

## Runs (each once on the code as committed, unless noted)

- `lake build`: "Build completed successfully (1461 jobs)" (/tmp/kb2ab/lake-full.log, at 0f12aeacf9; later Lean commits
  rebuilt their modules and `ve_service`, and `tools/lean_statements.py` built the whole tree each time).
- `python3 lean/audit.py`: PASS (above), at bfb587712b.
- `uv run python tools/regen_generated.py --write`: "wrote 41 entries", last at e9dcebbd2a.
- `uv run python tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: "PASS: kernel 10041 <= 10041",
  "PASS: verdict writers outside the kernel 56 <= 56".
- `uv run python tools/trust_map.py --check`: exit 1 only on the budget (row 5, awaiting the DRI's signature): "against
  4a5d3460d36c: K +0, S +48, D +86, G +290, tied +80, unclassified +0, trusted +283".
- Tests while iterating: `tests/test_kb2a_document.py` (10 passed), `tests/test_judgments_chain.py` (46 passed),
  `tests/test_kernel_closure.py` (after fixes), `tests/test_relay_binding_inventory.py::test_every_schema_field_is_classified`
  (19 passed).
- Selected tests, on the committed tree 2b39f8ac99 (`MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select --
  --base $(git merge-base HEAD main) --run`, ve-cloud-2, 8,288 s): "recorded 555 units ...; 4 failed":
  `tests/test_trust_budget.py::test_trust_map_check_passes_on_the_live_tree` and
  `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check` (the trust budget: they pass once the DRI signs
  DELTA row 5 and the allowance is recorded; the stop reason), `tests/test_b16b_evidence.py::test_every_seeded_fault_still_applies_to_the_tree`
  (b16b's seeded fault `load_admits` reads `load_document`'s line, which the core refusal had changed: the refusal moved
  into `_load`) and `tests/test_lean_document_wrapper.py::test_large_question_fixtures_are_compared_as_seeds_without_mutants`
  (the unmutated seeds include `LEAN_CORE`). The two fixed ids, rerun with the loader's tests
  (`uv run pytest -q` on them, `tests/test_document_lean_switch.py::test_load_does_not_admit_the_graph_and_check_does` and
  `tests/test_kb2a_document.py`): "13 passed". Earlier selected runs on this branch (each stopped at 5 failures) found
  what the commits 2b1f154ef9..ba73c845d3 fix: the enum-domain inventory, the conformance harness's core answer, the
  readings S2 documents (routing narrowed), the open vocabulary object, the route corpus, the fuzzer's seeds, the
  package module list and `statementJson`'s class.
- `uv run python tools/gate_collection.py --check --prebuilt`: "21 added, 8 removed by a trailer, 0 refused, 0 stale and
  0 malformed trailers".
- `uv run python tools/regen_generated.py --check`: only `trust-tables` fails (the unsigned budget).
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
8. **Soft-norms with readings, without judgments@0.** They reach 1207-1208 today and keep Python's fallback here
   (routing (b)): `ve document readings` and the readings queries (`ve/readings_verdicts.py`, the S2 components) read
   Python's document object, which the core path does not build; their row needs those queries on the core answer
   (the carried rows are the cases they would ask). FSF D1 is one, and also needs group 2's soft readings.
9. **The matrix.** The two refusal texts still fire (part 4); tests and examples pinning them read `Document.*` functions
   directly (Lean: DocumentChainExamples.lean:173, DocumentChainChecks.lean:83-88, Compose/Examples.lean:736,
   Judgments/ChainExamples.lean:178) or saved evidence (`test_safety_framework.py`), or documents with
   `norm-defaults@0` (`test_document_chain.py`).

## Notes for the DRI

- Part (4)'s routing is narrower than "exactly the documents that reach the refusals" in three ways (Decisions,
  above); each keeps a document on the path that answers it today. The soft-norms-with-readings documents without
  `judgments@0` move with a step C row that gives the core path the readings queries.
- `CoreCheck.lean` is 419 lines (the task said at most 300; standing override 1): about 150 are its theorems.
- The kernel fold is not in `kernel_lines` while the `document` path is a candidate; it enters when the architect seat
  makes the path a kernel path.
- kb-2a's own ties pass (its FOLLOW-UPS.md) is still open: the module was promoted, not tied.

FOLLOW-UP: kb-2a-b-tm complete the trust-mutants sweep of kb-2a-b on its final HEAD (1,022 mutants; partial record docs/kernel/kb-2a-b/trust-mutants-part1.json, 169 judged) until it exits 0, on a pool that shards it

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: PASS. `document.json` `core_view`, `core_row`, `core_statement`, `core_choices`,
   `core_statements`, `lowering`; `soft-norms.json` `slot_admission`; `ResponseShape.Encoders.CoreCheck.runCaseReported_fits`;
   `tests/test_kb2a_document.py::test_core_answer_retyped_fields_are_unavailable`; `lean/ResponseShape/CoreCheckExamples.lean`.
2. Deliverables built, no rule broken: PASS for (1) to (7) and (4b); the trust-mutants sweep is partial (FOLLOW-UP
   kb-2a-b-tm); DESIGN 3 item 3's audit is the DRI's, its packet is `audit-packet.md`.
3. Tests and gates can fail: PASS. Seeded bugs (a) to (f) (`seeded-bugs.json`); the partial sweep: 124 KILLED.
4. Python, Lean and Rust agree: PASS for Python and Lean (`python-vs-lean.md`, the golden file, status-compare.json);
   Rust: N.A. (no Rust code changed; the pinned binary is unchanged).
5. R8 binding: PASS. `ve/document/core.py::bind_core_answer`; `::test_core_answer_rebound_fields_are_unavailable`
   (over 100 members shifted, rows dropped, added, reversed, refused).
6. Gate evidence matches the final HEAD: PASS for the selected run (on 2b39f8ac99, its failures fixed and rerun); the
   full gate is the chain's.
7. No unsigned item: one reserved, DELTA row 5 (trust +283, above R16), the stop reason on the first line.
8. Every user-visible change in DELTA: PASS. Rows 1 to 4 (the kind, the core answer, its refusals and today's path for
   no-row features, `--json`), 6 (generated files).
9. Test selection: PASS. The selected runs selected `tests/test_kb2a_document.py`, `test_judgments_chain.py`,
   `test_readings_s2_document.py`, `test_lean_document_wrapper.py`, `test_difffuzz.py`, `test_trust_budget.py`.
10. Lean statements say what is claimed: PASS. Statements quoted from the source above; seeded (a), (b), (c) break
    `fold_checked_iff`, `casesFrom_ok`, `replaySlotAdmission_sound`.
11. Budgets fail closed: PASS. The lowering refuses more than 64 choices before enumerating (step A); the round trip's
    gates (depth 64, 10,000 nodes) are checked before a case is built (`roundTrips` #guards at 63/64 levels and
    10,000/10,001 nodes).
12. No CPU or memory regression: PASS. `latency.json`: 0.91x and 0.93x on the two existing documents (a-rules over
    120 s before and after on the loaded VM).
13. Removed tests have a trailer: PASS. `Test-removed:` in ba73c845d3; `gate_collection.py --check --prebuilt` 0 refused,
    0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Each refusal test has its accepted twin (a Lean refusal vs the
    answered document; an exception read OPEN vs no term CHECKED; routed vs not routed for each narrowing; roundTrips
    true at 63/10,000, false at 64/10,001). Spec re-read: `slot_wire_admission` against DESIGN.md:55-60 (2.2); the fold
    against DESIGN.md:62-68 (2.3), which led to the `asserted` conjunct; the answer against DESIGN.md:70-74 (2.4); no
    Python decision against DESIGN.md:76-77 (2.5); routing against DESIGN.md:79-87 (2.6) and the task's part (4); the
    tests' names against DESIGN.md:106-113.
15. No overclaim, no silent cut, checks can fail, limits charged first: PASS with one open item (the sweep, a
    FOLLOW-UP, not a cut deliverable: it ran and its record is committed); "every" and "none" in this report name their
    command or test.
