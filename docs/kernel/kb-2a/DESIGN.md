# kb-2a: the document mode on the core document (architect seat, round 4, 2026-11-13)

Labels: (M) measured, (S: file) sourced, (A) assumed. Decision owner: architect seat. Asked by the DRI
(inbox 20261112T1620Z, 20261112T1729Z, 20261113T1505Z). The spec this applies: docs/spec/kernel-boundary.md
decisions 3 to 5, section 3 (carry rule), section 4 (core document, composition by construction).
kb-2a OWNS replacing the feature-combination matrix. Line numbers are VE main 9a3fd7a9f9.

## 1. What is there today (S: survey of 2026-11-13; M where marked)
- `lean/VE/Service/Document.lean`: 3,081 lines; the path `document` measures spec 34,821, wrap 12,818 (M:
  docs/kernel/closure-baseline.json). Entry: `runCaseReported` (2987) -> `checkDocSets` (2819) -> `checkCore`
  (2682) -> `check` (2529-2650).
- A unit's status is one of CHECKED, OPEN, LABELLED, UNFORMALISED. It is NOT a verdict of a route. It is
  computed in four places: `Loader.w2Status` (content present + meaning class; `sourceUnit` 1782-1832);
  `Loader.foldStatus` (reading set: CHECKED only if the set is authored and every reading asserted; `check`
  2608); `VE.Judgments.status` (OPEN if the unit reads a judgment term; 2611-2614); the rights route's
  `opens` (2616-2618). An authored status that differs is refused (2619).
- The norm routes are called accept-or-throw (`checkNorms` 2181, `checkNormDefaults` 2166, `admitGraph` 2021,
  `readingsSets` 2101): the route's answer is DISCARDED. The answer shows each unit's own content
  (`UnitContent`: formula, norm, rights block, soft rule, cardinality statement) but not the document that
  was admitted, its premises, the reading choices or any kernel case.
- Combinations are admitted or refused by name in 13 places of `environmentOf` (1174-1208) and `check`
  (2535, 2561, 2597), in `RightsDoc.unowned` (1428), 1627, 1731, and in `VE.Compose.profileTable`
  (Dispatch.lean:767-834) with `listedStacks` (Stack.lean:27). 22 test files pin the refusal texts.
- When Lean answers `CheckerUnavailable` (every pair refusal does), `ve document check` lets PYTHON decide
  the document (ve/document/lean.py:102 `_lean_answer`, `_python_decides_mixed_readings`). So a mixed-feature
  document is today decided by unproved Python, not refused. The UDHR pilot translation is one of these;
  usecases/question-answering/udhr-part07.ve.md is the UDHR document Lean decides.
- kb-3a (the slot on the soft route's wire: `decodeFacts`, kinds `slot-certificate`, `slot-conflict`) is
  queued and has no commit yet (M: branch feature/kb-3a has no Lean diff from main).

## 2. The design
One path for every document whose features have a lowering:

```
document --lower--> for each compatible reading choice c:  core(c) = (X_c : SoftDoc, P_c : List Formula)
         --kernel--> one admission row per choice (soft route, with facts)
         --fold--> unit statuses;   the answer CARRIES the core documents and the rows
```

2.1 **Lowering** (shell tier, pure, no verdict). Each feature contributes statements to the core document and
nothing else. A lowering has no "admitted" flag of its own and never decides anything.

| Feature | Lowers to | Refuses (the lowering's own diagnostics) |
|---|---|---|
| soft-norms@0, norms@0 | each rule unit: one `SoftNode` (a strict rule is a node without exceptions) | what the soft decoder refuses today |
| facts, thresholds, classifications (formula units over base predicates) | premises of `P` | a formula over a regulated predicate: `UnsupportedLowering` (it is a claim about the rules, not a premise) |
| judgments@0 | the term is a base predicate with its decider and contributes NO premise (a judgment record carries no criteria: `Judgments.admit` refuses non-empty `necessary` / `sufficient`, `JudgmentCriterionAsUnit`, Judgments/Decl.lean:128-143). A determination the document itself states about the term ("X has been judged significantly redacted") is an ordinary fact unit: one premise of `P` with that unit as origin | every refusal of `Judgments.admit` and the three unit refusals of `Judgments.status`, unchanged |
| readings@1 | one core document per compatible choice of the active reading sets (couplings respected) | two readings of one set that lower to the same statements: `ReadingsCollapsed`; more than 64 choices: `ResourceLimit` |
| register labels | no statement (status LABELLED) | - |

Every statement of a core document records its ORIGIN: the unit id, the feature, and for a reading the set
and reading index. Every name a statement or an origin mentions (unit, part, term, predicate, target of a
purpose or marker) must exist in the document with the category the reference needs; otherwise `UnknownPart`.

2.2 **Kernel rows.** One row per choice: the soft route's admission of `(X_c, P_c)`: kind `slot-admission`
(new, beside kb-3a's kinds in lean/VE/Compose/SlotWire.lean), whose theorem says: the answer is `ok` only if
the source decodes to `X_c` with `WellFormedSoft X_c = true` (what `runAdmission_sound` says today) and the
facts decode to `P_c` with `SlotWellFormed X_c P_c`. It says nothing about consistency: no document answer
uses the words CONFLICT-FREE or valid. Conflict and entailment questions are asked later of the carried
case through kb-3a's kinds, which refuse inconsistent facts (kb-3a T5).

2.3 **The fold** (kernel code, written once, at most 60 lines): a unit is
- LABELLED / UNFORMALISED exactly as today (no core statement);
- OPEN if a statement of the unit reads a judgment term (directly or through a definition), or its active
  reading set is not authored-and-all-asserted, or the rights rule opens it (unchanged rules, but computed on
  the unit's CORE STATEMENTS, which is what removes the pair problem: there is one place to look);
- CHECKED otherwise, and only if EVERY choice's admission row is `ok`. One refused row: the document is
  refused with that row's diagnostic and the choice that produced it.

2.4 **The answer** = `VE.Kernel.Carry.carry`: `view` holds today's fields (units, statuses, coverage) plus,
per unit, its core statements per choice; `rows` holds each choice's case and the kernel's answer, verbatim.
Theorem (an instance of `shell_sound`, lean/VE/Kernel/Carry.lean): the answer is the fold of rows that the
softNorms kernel path ran. Public wording stays: CHECKED = "the core statements shown for this unit were
admitted by the checker".

2.5 **No Python decision on this path.** A document that takes the lowering path is answered by Lean or
refused by Lean; `_lean_answer`'s fallback does not apply to it.

2.6 **Which documents take the path, and how the matrix goes away.** Step B routes onto it exactly the
documents that today end in the refusals "judgments@0 with soft-norms@0 … needs its composed Lean route"
(Document.lean:1198-99) and "soft-norms with readings …" (1207-08, readings only): the features an RSP unit
needs together. Every other document keeps today's code and today's bytes. Then one row per feature group
(step C, section 5) moves that feature's documents onto the path with its fixtures' statuses and coverage
bytes unchanged, and DELETES its refusal sites and its old route call. The matrix is gone when the last
group has moved; `profileTable`'s `refuses` rows for document features, `layersApart` and `listedStacks`
are deleted in that last row.

## 3. Acceptance test (fixed here; the DRI's Nov 23 warning sign: acceptance test agreed 2026-11-13, CONFIRMED as written plus item 6, orchestrator inbox/dri 20261113T212153Z)
File tests/data/kb2a/rsp-mixed.ve.md, made of at least five units copied from the RSP translation
(usecases/anthropic-rsp/; each header quotes the FULL source sentence): (i) a rule with an exception
(soft norm); (ii) a rule whose guard or exception condition uses a judgment term (the RSP's "significantly
redacted" term of probe P8 is the first candidate), so that the unit is OPEN by the judgment rule;
(iii) one sentence with an authored two-reading set (the RS3 outer choice is the first candidate);
(iv) a fact or threshold list; (v) an aspiration (LABELLED). Profiles: documents@1, relational-fol@0,
soft-norms@0, judgments@0, readings@1.
1. `python -m ve document check tests/data/kb2a/rsp-mixed.ve.md` exits 0 and is answered by Lean's document
   mode (the test asserts `_lean_answer` returned an answer and no Python path decided).
2. The answer has each unit's status, its core statements per reading choice with origins, and one carried
   admission row per choice; it is a committed golden file, byte-stable.
3. Faithfulness: the standard cross-family unit audit (uc-audit) is run on this document's units; its result
   is recorded as it comes out. A unit judged unfaithful is listed with the finding; it is not re-labelled.
4. Measured, median of 5, through iso.sh: wall time and peak memory of `ve document check` on this document,
   on usecases/question-answering/udhr-part07.ve.md and on usecases/question-answering/agent-policy/a-rules.ve.md,
   before and after. Bound for the two existing documents: at most 1.25x before and at most 120 s (the bound
   docs/lean-first/b18/latency.py already uses).
5. Refusal tests, each on a one-line variation of the same document: `test_document_lowering_keeps_reading_sets_distinct`
   (two readings that lower to the same statements: `ReadingsCollapsed`; and a lowering never reports success
   while a premise of its own is unchecked: it has no success flag at all); `test_document_lowering_refuses_unknown_part`
   (a judgment record, purpose, marker or origin naming a unit, part or term that does not exist or has the
   wrong category: `UnknownPart`); `test_document_lowered_facts_inconsistent_no_verdict` (facts p(a) and
   not p(a) lowered from the document: the document answer contains neither CONFLICT-FREE nor valid, and the
   carried case sent to `slot-conflict` and `slot-certificate` gets kb-3a's refusal); and
   `test_document_lowering_never_falls_back_to_python`.
6. (DRI 2026-11-13) Before step B removes the Python fallback for the lowering path, record once what Python
   decides today for tests/data/kb2a/rsp-mixed.ve.md and list every difference from the Lean answer with its
   cause. Equality is not a gate; an unexplained difference is (task prompts/task-kb-2a-b.txt part (4b)).

## 4. Budget of trusted lines (signed by the architect seat; goes into docs/kernel/ALLOWANCES.md with step B)
- kernel: `slot-admission` up to +60 lines, the status fold up to +60. Nothing else.
- shell (not kernel, measured as the document path's own modules): lowering at most 500 lines, case
  building and answer at most 300.
- Step B does not yet shrink `Document.lean`; each step C row must delete more lines than it adds, and the
  path's spec target stays "at most 1,500 lines" (spec section 6) for the end state.

## 5. Step C rows (NOT filed yet; the architect seat writes each after step B is on main)
In this order, each "move the feature's documents onto the lowering path, fixtures' statuses and coverage
bytes unchanged, delete its refusals and its old route call": (1) soft-norms alone and norms alone;
(2) norm-defaults (the largest: constitution and UDHR documents; the UDHR pilot translation leaves the Python
fallback here); (3) rights (`limPremises` is already a slot instance: `rights_acceptance_from_slot`);
(4) definitions; (5) scope and senses; (6) alternatives and risk (their blocks lower to rules over the
option predicates; needs its own design note first); (7) cardinality and events (different logic: stay
refused beside other features until CONSOLIDATION-PLAN step 3, as spec 4.2 says); (8) delete
`profileTable`'s document refusals, `layersApart`, `listedStacks`, `RouteFacts`, and Python's
`_python_decides_mixed_readings`.
