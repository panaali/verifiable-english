# kb-2a-b (4b): Python's answer before, Lean's answer after, on the acceptance document

Document: `tests/data/kb2a/rsp-mixed.ve.md` (SHA-256 in [python-before.json](python-before.json)).

- **Before** (base `4a5d3460d3`, Python fallback in place; [python-before.json](python-before.json)): Lean's document
  mode answered `CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route`
  (lean/VE/Service/Document.lean:1207-1208 on the base), so `_lean_answer` returned none and Python's own loader took
  the document and refused it: `ve document check` exit 5, `CheckerUnavailable: judgments@0 documents are checked by
  Lean's document mode` (ve/document/load.py:184 on the base). No unit status, no statement, no row.
- **After** (this branch): Lean's core path answers it (`VE.Service.CoreCheck`), exit 0; the answer is
  [the golden file](../../../tests/data/kb2a/rsp-mixed.answer.json).

Equality is not a gate; each difference below names its cause. Python decided nothing in either answer: before it
refused, after it binds and renders Lean's answer.

| Id | Unit | Python before | Lean after | Cause |
|---|---|---|---|---|
| D1 | (document) | refused, exit 5, `CheckerUnavailable: judgments@0 documents are checked by Lean's document mode` | answered, exit 0 | ve/document/load.py:184 (base) refuses every judgments@0 document it is handed; Lean now reads the document on its core path: lean/VE/Service/CoreCheck.lean:243 (`routed`: the refusal of Document.lean:1207-1208, every profile with a lowering row) and lean/VE/Service/CoreCheck.lean:224 (`answer`) |
| D2 | intro-aspire-source, t1-plan-source, t4-name-source, s35-aim-source, s35-disclose-source, s36-full-review-source | no status (document refused) | LABELLED | the fold's rule for a unit with no core statement: lean/VE/Kernel/DocumentFold.lean:44 (`baseless`, line 39: meaning specified, no content) |
| D3 | intro-aspire | no status | UNFORMALISED | lean/VE/Kernel/DocumentFold.lean:44 (`baseless`: meaning `unformalised`) |
| D4 | t1-plan | no status | OPEN | lean/VE/Kernel/DocumentFold.lean:43 (`opens`, line 33): its statement under reading `cond` reads the judgment term `crossed` (rows-cond's guard; lean/VE/Service/CoreCheck.lean:136 `reads`), and its active set rs1-t1 is open (not authored with every reading asserted) |
| D5 | t4-name | no status | CHECKED | lean/VE/Kernel/DocumentFold.lean:45: a core statement (the premise listed(automated_rd)), meaning specified, not open, every row `ok` (rule of DESIGN kb-2a 2.3) |
| D6 | s35-aim | no status | CHECKED | lean/VE/Kernel/DocumentFold.lean:45: its soft rule f13-minimize-default (a default rule; its exception names no condition, so it reads no judgment term, CoreCheck.lean:125), meaning specified, every row `ok` |
| D7 | s35-disclose | no status | CHECKED | lean/VE/Kernel/DocumentFold.lean:45: its rule f13-disclose, meaning specified, every row `ok` |
| D8 | s36-full-review | no status | OPEN | lean/VE/Kernel/DocumentFold.lean:43: its rule f14-full-review reads the judgment terms highly_capable and significantly_redacted (CoreCheck.lean:136) |
| D9 | t1-plan, t4-name, s35-aim, s35-disclose, s36-full-review | no core statements | core statements per choice (3 choices: rs1-t1 readings 0, 1, 2) | the lowering: lean/VE/Service/CoreDocument.lean:336 (`lower`; judgment declarations line 151, content line 132, readings by `planOf` line 288) |
| D10 | (document) | no kernel row | 3 rows, each `slot-admission` answered `ok` (4, 4 and 3 rules; 1 fact) | lean/VE/Service/CoreCheck.lean:83 (`casesOf`, one case per choice) and the kernel row lean/VE/Compose/SlotWire.lean:391 (`replaySlotAdmission`); choice 2 (reading `ov`) has no rule for t1-plan |
| D11 | (document) | no refusal of a unit | none | rule of DESIGN kb-2a 2.3: a refused row would refuse the document (CoreCheck.lean:224); no row was refused |

No difference is unexplained.
