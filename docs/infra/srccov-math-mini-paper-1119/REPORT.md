# srccov-math-mini-paper-1119 REPORT

DRI signature needed: none. The one DELTA row cites R3; trust is +0.

- **Status:** 1 of 5 candidate rows KEPT and carried word for word (S0001). Rows 2-5 and all 5 recording units are
  DROPPED. The record form the map assumes for this document, a comment in a theorem's `.ve` file, does not exist in
  VE. Ready for the chain gate.
- **Base / merges at:** rebased on VE main `12cb72fa55` (defs-repair-math-mini-paper-1119 merged at `274b5489f6`,
  an ancestor). The map was read at pin e53db4e8fc; every unit was re-checked at main.
- **Changed:** the `lists` legend (`usecases/math-mini-paper/environment.json:45`). Derived files were regenerated
  with the project's tools. New condition test: `tests/test_srccov_math_mini_paper_1119.py`.
- **Answers touched (re-pin later reads):** T1 and T2 use `lists` (`theorems/{T1,T2}/conclusion.ve`;
  `grep -l -w lists theorems/*/*.ve`). The new `environment_id` is re-pinned in 11 certificates (C2, T1-T8, T7a, T7b).
  Every verdict.json is byte-identical to main.
- SIZE: 1 product, 81 tests, 212 other hand-written lines (this report, DELTA.md, mutants.json).

## 0. Verify first

The source is `usecases/math-mini-paper/paper.template.md` at main. It has no hash pin (METHOD section 0, math row).
The carriers and records allowed for this document are "theorems/*/premises.ve + conclusion.ve, ...;
environment.json, environment-closure.json" and "comments in those .ve files"
(manage-agents `reviews/source-coverage-1119/METHOD.md:19`).

Comment probe (`/tmp/smmp-comment-probe.log`): `ve.parser.parse(env, prefix + T6/premises.ve)` with prefix
`# ...`, `-- ...` or `// ...` raises `SyntaxError: expected term` for all three. VE's `.ve` grammar has no comment.
Each theorem's `premises.ve` is also a generated file: `verify.py:111` writes it from `theory.py`, and
`tests/test_closure_induction.py:48` parses it. A hand comment would be overwritten on the next `verify.py` run.
Until then it would break that replay test. Adding comment syntax is a new language feature, which is out of scope.

| row id | KEPT / DROPPED | units kept | reason |
|---|---|---|---|
| srccov-math-mini-paper-s6-1-1119 | KEPT | S0001 | The source holds the sentence at paper.template.md:123 ("A point *y* is **self-listing** for a relation *R* when *R(y, y)*."). It equals the map quote once `*` emphasis is dropped. The `lists` legend at environment.json:45 (main) reads "The first point lists the second point; an arbitrary binary relation." and does not hold it. The condition test failed on main: /tmp/smmp-t1.log, 1 failed. `lists` is used by T1 (theorems/T1/conclusion.ve:1, `(x1 lists x1)` is the self-listing atom) and T2. This is a legend carry under METHOD section 3: no rule line, no formula change. |
| srccov-math-mini-paper-s6-2-1119 | DROPPED | none | S0004 (paper.template.md:125-126, "Definitions only become axioms when they would name a compound formula (D2–D5 below).") holds a condition ("when"). Under amendment 12 it is never out of scope, so it cannot be recorded. The row's carrier is a comment in theorems/T5/premises.ve. A comment carries nothing (amendment 4), and VE has none (probe above). No legend of a used symbol glosses it: it is about VE practice. |
| srccov-math-mini-paper-s6-3-1119 | DROPPED | none | S0002 (paper.template.md:123-124) and S0003 (paper.template.md:124-125). The carrier, a comment in theorems/T1/premises.ve, cannot be written: there is no `.ve` comment syntax, and verify.py:111 regenerates the file. S0003 also holds modals ("cannot", "does not have to"). See the RECORDING lines. |
| srccov-math-mini-paper-s6-4-1119 | DROPPED | none | S0011 (paper.template.md:235-236) and S0012 (paper.template.md:236-238). The carrier, a comment in theorems/T5/premises.ve, cannot be written (same reason). S0012 also holds a modal ("would have to"). |
| srccov-math-mini-paper-s6-5-1119 | DROPPED | none | S0015 (paper.template.md:282). The carrier, a comment in theorems/T6/premises.ve, cannot be written (same reason). |
| RECORDING S0002 | DROPPED | none | "There is no VE text for this definition: it is not needed." It holds no modal, definition, number, date or condition, so it is recordable in kind. It is not recorded at main: no math `.ve` file has a comment, and no other record file is allowed for this document (METHOD.md:19). The only allowed form cannot be written (probe above). Not recorded: FOLLOW-UP below. |
| RECORDING S0003 | DROPPED | none | "VE cannot abbreviate x lists x, but it does not have to, because the phrase is a single atom." "cannot" and "does not have to" are modals of possibility and necessity ("have to" = must). I took the conservative reading of amendment 12: absent, not recordable. The record form is also missing (S0002). |
| RECORDING S0011 | DROPPED | none | "In VE this is an axiom: the unary symbol greatest is uninterpreted, and D2 is the biconditional premise that pins it down." It is recordable in kind (editorial note on the encoding), but no allowed record form can be written (S0002). |
| RECORDING S0012 | DROPPED | none | "It appears in the hypothesis list of T5 and would have to appear in the hypothesis list of every further theorem about greatest elements." "would have to" is a necessity modal. Conservative reading of amendment 12: absent, not recordable. The record form is also missing. |
| RECORDING S0015 | DROPPED | none | "Again an axiom, on the uninterpreted binary symbol sim." It is recordable in kind, but no allowed record form can be written (S0002). |

No rows of my own were added.

## 1. Carried (deliverable 1)

- `usecases/math-mini-paper/environment.json`, `lists`, `description`: "A point y is self-listing for a relation R
  when R(y, y)." is appended after the old text, which stays unchanged. The text is the source's own; only markdown
  emphasis `*`/`**` is left out. The carrier is a hand-written input that `theory.py:18` reads. It is not in a frozen
  or sealed run directory. No rule formula or theorem statement changed: premises.ve and conclusion.ve came out
  byte-identical from `verify.py`, and `git status` shows no change.
- Records: none written (section 0).

## 2. Regenerated (deliverable 2), only with the project's tools

- `uv run python usecases/math-mini-paper/verify.py`, then `make_paper.py` (verify.sh's steps; the boundary probe was
  skipped because its inputs are unchanged). These ran on the freshly built Lean (`lake build`, 1478 jobs, ok).
  - 11 certificates were re-pinned: C2, T1-T8, T7a, T7b. A field diff against HEAD (`/tmp/smmp/jsondiff.py`) shows
    changes only in `environment_id`, `conclusion_meaning_id` and `premise_meaning_ids`. No `trace` field differs.
  - `results.json`, the 19 `verdict.json`, `report.md` and `paper.md` differed only in wall-clock fields: the field
    diff shows `prove_seconds`, `necessity[].seconds` and `refutation_seconds` only, and a float-masked compare of
    paper.md and report.md shows 0 lines. These were kept at their committed bytes, the same conservative choice as
    defs-repair-math-mini-paper-1119: no keyed-answer churn. `paper.md` does not render legends.
  - premises.ve, conclusion.ve, countermodels and vocabulary-lint.json came out identical.
- `uv run python -m conformance.english_lean_lexicon`: `lexicon-report.json` changed only in the math-mini-paper
  `lexicon_id`. It was rerun after the rebase, with no further change.
- `uv run python -m conformance.english_lean_seal`: `corpus-seal.json` was resealed before and after the rebase. Each
  time `--check` showed one other stale entry (`usecases/safety-framework/environment.d1.json`), which the tool renews
  too because it has no per-file mode. Afterwards `--check` prints `0 difference(s)`.
- `uv run python tools/regen_generated.py --check` exits 0 (41 entries).
- Not regenerated, with reasons:
  - `usecases/math-mini-paper/t7-definitions-bundle.json` embeds a copy of environment.json. Its tool,
    `verify_definitions.py`, exits 1 with `VEError: Citation hypothesis is absent from the citing branch`, both with
    this change and with main's environment.json (`/tmp/smmp-vdef.log`, `/tmp/smmp-vdef-main.log`). This is the seam
    already filed as FOLLOW-UP defs-repair-math-mini-paper-1119b. A hand edit is not allowed.
  - `conformance/difffuzz-baseline.json` and `tests/data/relay-gate-cases.jsonl` (named by the map from
    `git grep -l`) are recorded fuzz and relay inputs, not outputs of this legend. They hold an older environment
    snapshot without `sim`. The previous `sim` legend change left them as they were, and the selected run passed
    without touching them.
  - `results.json`, `paper.md` and `verdict.json` are timing-only (above).

## 3. Condition test (deliverable 3)

`tests/test_srccov_math_mini_paper_1119.py` has 2 tests. The D1 sentence is read from paper.template.md with emphasis
stripped. It must equal the map quote, and after `tests/omission_rule.py:omit_norm` it must be contained in the
`lists` legend. The second test checks that T1/T2 use `lists`. No record test is written because no record was kept.
- Pre-change main (the test commit alone on 09bea0972d): 1 failed, 1 passed (`/tmp/smmp-t1.log`).
- After the change: passing (`/tmp/smmp-t2.log`). On the rebased HEAD it passed with the defs-repair, seal, lexicon
  and replay tests: `64 passed` (`/tmp/smmp-t3.log`).
- Stays selected: `select_tests.py --paths usecases/math-mini-paper/environment.json
  usecases/math-mini-paper/paper.template.md --static --explain` selects it for both paths (`/tmp/smmp-sel-paths.log`).

## Seeded bugs

No Lean, Python or Rust product code changed. `tools/trust_mutants.py --plan` lists 0 definitions and 0 mutants
(saved: `trust-mutants-plan.json`). Light lane printed `LIGHT 113 changed lines ... no trusted-core file`, so there
was no sweep. Four seeded bugs were planted, run and restored (`mutants.json`; log `/tmp/smmp-mutants.log`):

| bug | file | failing test |
|---|---|---|
| m1 drop the carried sentence (carry kind: legend append) | usecases/math-mini-paper/environment.json | `test_srccov_math_mini_paper_1119.py::test_source_unit_is_carried_in_the_rules_legend[srccov-math-mini-paper-s6-1-1119]` |
| m2 `R(y, y)` -> `R(y, x)` in the legend | usecases/math-mini-paper/environment.json | same test |
| m3 T1 stops using `lists` on the diagonal | usecases/math-mini-paper/theorems/T1/conclusion.ve | `test_srccov_math_mini_paper_1119.py::test_carrier_legend_belongs_to_a_symbol_the_rules_use` |
| m4 T1 certificate keeps the old environment_id | usecases/math-mini-paper/theorems/T1/certificate.json | `test_defs_repair_math_mini_paper_1119.py::test_certificates_pin_the_carrier_environments` |

## Runs

- Selected run (`mac-pytest.sh --select`, on e22a1a2b81 before the rebase, base 09bea0972d): exit 0, `0 failed`, ran
  on ve-cloud-2 in 1885 s (`/tmp/smmp-select.log`). It picked the new test, `test_english_lean_lexicon.py`,
  `test_english_lean_seal.py` and `test_closure_induction.py`. After the rebase, only the seal entry changed; the
  focused tests above passed on it. The chain gate runs on the final HEAD.
- `tools/gate_collection.py --check --prebuilt`: 2 added, 0 removed, 0 refused, 0 stale, 0 malformed
  (`/tmp/smmp-coll.log`).
- Known red: no test in main-known-red.txt was touched. The gate was not run here.
- Branch commits (`git log --oneline main..HEAD --no-merges`, saved here): the condition test (red on main); the D1
  carry with the re-pinned certificates, lexicon and seal; the reseal after the rebase onto 12cb72fa55; this
  report/DELTA/mutants commit.

## Spec re-read

- The D1 legend append was checked against paper.template.md:123 and rows-math-mini-paper.tsv row 1 `change`: identical
  after emphasis removal (asserted by the test).
- The DELTA row was checked against DRI-RULINGS.md R3: information is added, nothing is removed or renamed, goldens are
  updated, a test checks the field holds the true source text, and there is nothing to bind.
- The recording deliverable was checked against METHOD amendments 4, 12 and 13 and section 0 (math row): the only
  allowed record form is a `.ve` comment, and VE's grammar has none.

## Notes for the DRI

- The map's rows 2-5 and the recording ruling (dri-ruling-srccov-features-20261119 item 2a) assume a comment record in
  the math theorems' premises.ve. VE has no comment syntax, and premises.ve is a verify.py output. I took the
  conservative option: no new record form was invented (a new record file, or a comment emitted by theory.py/verify.py),
  and nothing is recorded. Choosing a record form for math-mini-paper is a design choice for a follow-up (below).
- S0003 and S0012: amendment 12's list (must/shall/should/will/may/never) does not name "cannot", "have to" or
  "would". The map read S0003 as not modal. I read both as modal, which keeps them visible as absent rather than
  recording them away. If the DRI rules the narrower list, they join S0002/S0011/S0015 in the record-form follow-up.
- S0004 (row 2) stays ABSENT: it is a statement about VE practice with a condition. No legend of a used symbol
  glosses it.
- The seal reseal also renews the stale safety-framework entry. Siblings regenerate the same file: on a conflict, take
  main's and rerun `python -m conformance.english_lean_seal`.

## Self-review against BUILDER-CHECKLIST
1. N.A.: no Lean answer, route or relay changed.
2. PASS: deliverables 0-3 and the recording lines are above. The kept row is carried (`test_source_unit_is_carried_in_the_rules_legend`). Dropped rows and units give reasons with file:line. The bundle seam and the record-form gap are named. No Python copy of a decision, no report test.
3. PASS: 4 seeded bugs, each failing a named test (mutants.json).
4. N.A.: no Python/Lean/Rust behaviour changed. Certificate replay in Python and Lean: `test_all_committed_mini_paper_certificates_still_replay_unchanged`.
5. N.A.: no relayed field.
6. PASS: rebased on main 12cb72fa55, regenerated lexicon and seal, and reran their tests (`/tmp/smmp-t3.log`). The gate runs in the chain on the final HEAD.
7. PASS: the DELTA row cites R3 with its tests; no reserved signature.
8. PASS: DELTA row 1 covers the legend change. Verdicts, the rendered paper and the lint are unchanged (field diff and masked compare, section 2).
9. PASS: the selected run picked the lexicon, seal and replay tests and the new test. `--paths ... --explain` keeps the new test selected for the carrier and source.
10. N.A.: no Lean statement or proof.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no code path changed; the traces are identical.
13. PASS: no test removed. `gate_collection.py --check --prebuilt` reports 0 removed, 0 stale, 0 malformed.
14. PASS: both directions are covered: main fails (`/tmp/smmp-t1.log`), the change passes, and m1-m4 fail. Each claim cites a command or log. The spec re-read is listed.
15. PASS: overclaim: "identical/unchanged" claims cite the field diff, the masked compare and git status. No silent cut: the dropped rows and recordings give reasons, and the unfinished recording is a FOLLOW-UP. Every new check can fail (m1-m3). Limits: N.A.

FOLLOW-UP: srccov-math-mini-paper-record-form-1119 give math-mini-paper an out-of-scope record form (VE .ve has no comment syntax) and record S0002, S0011, S0015
FOLLOW-UP: srccov-math-mini-paper-absent-1119 absent, not recordable: S0003 and S0012 hold modals ("cannot"/"does not have to", "would have to") and need a carry, not a record
