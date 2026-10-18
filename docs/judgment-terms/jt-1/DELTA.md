# User-visible deltas (jt-1)

| Item | Change | Ruling |
|---|---|---|
| Trust budget | Classified trusted Lean lines rise by 54 against the merge base `de9cfa84f`, all new Lean-owned behaviour of `judgments@0` (records and admission, the shared scan): `lean/VE/Judgments/Decl.lean` +52 (S 36: `Judgment`, `Rec`, `baseEnv`, `faultOf`, `admit`, `names`; D[V] 16: `records`), `lean/VE/Judgments/Scan.lean` +4 (S: `opensIn`), `lean/VE/Rights/Run.lean` -2 (G[V]: `nodeOpen`, now one call of the shared scan); `lean/VE/Discourse/Loader.lean` +0. K +0. `lean/VE/Judgments/Examples.lean` is T. Recorded with `tools/trust_map.py --allow` (S +40, V +14). | SIGNED by standing ruling R16 (DRI-RULINGS.md): 54 <= 150 lines, K +0, new Lean-owned behaviour; itemised per file and re-measured on this HEAD with `python3 tools/trust_map.py --check` (PASS). Every new trusted definition is exercised by a check that can fail: `#guard`s in `lean/VE/Judgments/Examples.lean` (11.1 for `records`, 11.2 for `faultOf`, `admit`, `baseEnv`, `Judgment`, 11.3's direct scan for `opensIn`) and the theorems `faultOf_none_iff`, `admit_ok_iff`, `admit_first_fault`, `records_names`, `records_refuse`, `opensIn_iff`, `opensIn_isEmpty`, `nodeOpen_eq`; seeded bugs in `mutants.json`. Ties pass: manage-agents FOLLOW-UPS.md, "## jt-1 (2026-10-18)". |

No other delta. The item adds no route, service mode, response field or diagnostic that any caller sees:

- `Loader.openTermNames` gains `sorts`, off by default; no caller passes it, so W2 accepts, refuses and words every
  `open_terms` list as before. Checked by the J-ο `#guard` (`Examples.lean`, 11.1: without the flag the repeated
  sorts are refused with "invalid open-term arguments", both with nothing passed and with `sorts := false`), the
  seeded bug `sorts-flag-default-on`, and the discourse and document tests of the selected run (`tests/test_discourse*.py`,
  `tests/test_document*.py`).
- Rights' `nodeOpen` calls the shared scan; `nodeOpen_eq` proves it equal to its earlier body, so rights' answers and
  bytes are unchanged (`tests/test_rights.py`, `tests/test_rights_lean.py`, `tests/test_rights_three_way.py`,
  `tests/test_rights_render_status.py` in the selected run; seeded bug `nodeOpen-guard-only`).
- The judgments' records, admission and diagnostics (`JudgmentUnbound` and the rest) are reached by no route until
  JT-2 switches the profile on in the document mode.
