# srccov-birthright-citizenship-debate-1119: report

- **Status:** nothing carried and nothing recorded. Both candidate rows (s7-2, s7-3) and all 8 RECORDING units are DROPPED. The only record form the map allows for this document is a comment in its `.ve` files (METHOD section 0), and the strict parser accepts no comment line in any syntax. A record would need a new language feature, which is out of scope.
- **HEAD:** branched from VE main `09bea0972d`. This change touches no carrier, no derived file and no answer.
- **What changed:** this REPORT and `evidence/comment-probe.txt` (the parser probe). No product code, no test and no generated file changed.
- **Open:** three FOLLOW-UP lines at the end: the record form, and S0001 and S0006 (absent, not recordable).
- **DRI signature needed:** none. There is no DELTA row, and trust changes by +0.

## 0. Verify (before any edit)

Sources checked: the pinned source `usecases/birthright-citizenship-debate/source.md`. `git diff --quiet e53db4e8fc HEAD -- usecases/birthright-citizenship-debate/source.md` exits 0, so the source is unchanged since the pin. The carrier `usecases/birthright-citizenship-debate/claims.ve` at main has 2 lines, both statements; `git diff --stat e53db4e8fc HEAD -- usecases/birthright-citizenship-debate/` is empty. Also checked: its legends `environment.json` / `environment.english.json` and `countermodel/*.ve` (case premises, not carriers: METHOD amendment 4).

The drop reason: `docs/spec/v0-language.md:47` says "Each statement ends with a period and LF, including the last. No comments, tabs, CRLF, or alternate Unicode punctuation are accepted by the strict parser." The probe in `evidence/comment-probe.txt` puts one line `<prefix> test comment` in front of the unchanged `claims.ve`, for each of the prefixes `#`, `--`, `//`, `%` and `;`. `uv run python -m ve render` returns `InvalidInput SyntaxError 'SyntaxError: expected term' line 1 col 1` for every prefix, and the unchanged `claims.ve` renders. The record files METHOD allows for this document are "comments in those .ve files" (`reviews/source-coverage-1119/METHOD.md:14`). Writing such a comment needs comment syntax for relational-fol `.ve` files, which is a new language feature (task: "Drop a row or unit that ... needs ... a new language feature"). No other record form is allowed for this document. A legend is a carrier, not a record (METHOD amendment 4), and putting out-of-scope prose into a legend would change what the reader is shown.

### Rows

| row id | KEPT / DROPPED | units kept | reason |
|---|---|---|---|
| srccov-birthright-citizenship-debate-s7-2-1119 | DROPPED | none (S0004, S0008, S0009, S0010, S0011 all dropped) | the change is "comment (rationale)" in `usecases/birthright-citizenship-debate/claims.ve:1-2`, and the strict parser refuses any comment line (`docs/spec/v0-language.md:47`; `evidence/comment-probe.txt`): needs a new language feature |
| srccov-birthright-citizenship-debate-s7-3-1119 | DROPPED | none (S0006 dropped) | the change is "comment (editorial annotation)" in `claims.ve`; same parser refusal. S0006 also holds the ordinal "14th" (amendment 12, conservative reading; see S0006 below) |

Not in scope and not touched: srccov-birthright-citizenship-debate-s7-1-1119 (needs_rule_line=yes; S0003, S0005, S0012).

### RECORDING (orchestrator ruling 2a: every OUT-OF-SCOPE-UNRECORDED unit)

Every unit text below occurs at the cited `source.md` line, as checked by `grep -n -F` on source.md. None of them occurs in `claims.ve`, `environment.json`, `environment.english.json` or `countermodel/*.ve`, as checked by `grep -l -F` on the phrases "Should America", "Mayes, on the text", "Nothing like this", "Full stop", "blame the child", "fundamentally American", "Harlan", "Plessy" and "14th Amendment states": no hits. The one "Krikorian" hit, in `environment.json`, is the `subject_to_jurisdiction` legend's reading. It is not S0002's participants and affiliations. So no unit is carried or recorded at main.

| unit | RECORDED / DROPPED | record file:line or reason |
|---|---|---|
| S0001 | DROPPED | `source.md:35` "Should America end birthright citizenship?": holds the modal "Should", so amendment 12 forbids class 4 and it may not be recorded (FOLLOW-UP below). In any case the record form does not exist (parser refusal) |
| S0002 | DROPPED | `source.md:37` (metadata: participants): no record form; the comment record would need comment syntax (`docs/spec/v0-language.md:47`; `evidence/comment-probe.txt`) |
| S0004 | DROPPED | `source.md:42` (rationale): no record form, same reason |
| S0006 | DROPPED | `source.md:44` (editorial annotation): no record form, same reason. It also holds the ordinal "14th" in "The 14th Amendment". The conservative reading of amendment 12 ("a number") keeps it out of class 4 (FOLLOW-UP below) |
| S0008 | DROPPED | `source.md:44` (rationale): no record form, same reason |
| S0009 | DROPPED | `source.md:45` (rationale): no record form, same reason |
| S0010 | DROPPED | `source.md:45` (rationale): no record form, same reason |
| S0011 | DROPPED | `source.md:46` (rationale): no record form, same reason |

## 1. Rows carried

None.

## 2. Derived files

None were regenerated. No carrier or legend changed, so `rendered.md`, `rendered-english.md`, `conformance/english-lean/corpus-seal.json`, `conformance/english-surface-report.json`, `conformance/natural-view-report.json` and `conformance/english-lean/s0-report.json` have no input that changed.

## 3. Condition test

Not written. Deliverable 3 asserts something for each kept carry and each kept record, and must fail on the pre-change main. This item keeps none, so every possible assertion is either empty or already true on main, and neither can fail on main. `tests/test_srccov_birthright_citizenship_debate_1119.py` is therefore not added. The follow-up item that adds a record form writes it together with the records.

## Seeded bugs

None. No product code changed in any language (Lean, Python or Rust). There is no carried sentence to remove and no new test to break. `git diff --stat main...HEAD` lists only `docs/infra/srccov-birthright-citizenship-debate-1119/`.

## VE commit and answers touched

- Merges at VE main `09bea0972d`; the map was read at pin `e53db4e8fc`, and the carrier is the same at both commits.
- Answers touched: none. `claims.ve` and its legends are byte-identical to main, so no later read needs to re-pin for this item.

SIZE: 0 product, 0 tests, about 80 other hand-written lines (this REPORT and the probe evidence).

## Notes for the DRI

- The map's rows s7-2 and s7-3 assumed that claims.ve can hold a comment record. The relational-fol v0 grammar refuses comments by design (`docs/spec/v0-language.md:47`: "A future relaxation must update the lexical specification and source-correspondence obligations"). Other documents whose only record file is "comments in" `.ve` files (asimov-laws, asimov-extended, claude-constitution-excerpt, math-mini-paper and us-constitution-14th-s1; METHOD section 0) may meet the same block. This item did not probe their profiles' parsers. At main, `git grep -n -E '^\s*(#|--|//)'` over `usecases/**/*.ve` finds comment-like lines only in the FSF, RSP and PF `*.d1.ve` files, and those are `## id | ...` headers.
- Conservative choice taken without asking (override 2): drop rather than write the records somewhere METHOD does not allow (a legend, GAPS.md or a new file). The second-reader challenge (challenge2) did not cover these 8 units.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relay or route changed.
2. Every deliverable built, no rule broken: PASS. The verify table is above; deliverables 1-3 are empty because no row was kept, which is the task's own drop rule. The parser refusal is recorded in `evidence/comment-probe.txt`. There is no new report test and no new Python copy of Lean logic: the diff is docs only.
3. Tests and gates can fail: N.A., no new check or test (section 3).
4. Python, Lean and Rust agree: N.A., no code changed.
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches final HEAD: PASS. The chain runs the gate on the committed final HEAD. The selected run's result is in the build report.
7. No unsigned item: PASS. There is no DELTA row and no reserved signature.
8. Every user-visible change in DELTA: N.A., nothing the reader is shown changed.
9. Test selection still finds tests: N.A., no code or test file changed.
10. Lean statements and proofs: N.A., no Lean change.
11. Budgets and deadlines fail closed: N.A., no limit code.
12. No CPU or memory regression: N.A., no code.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Each claim above names its command: the `git diff` commands in section 0, the `grep -F` checks in the RECORDING section, and the probe file. The probe covers both directions: the comment lines are refused and the unchanged control file is accepted. Spec re-read: `docs/spec/v0-language.md:47` and METHOD section 0 and amendments 4, 12, 13 and 15c.
15. Overclaim, silent cut, new check can fail, limits: PASS. The cut is not silent: the FOLLOW-UP lines below name the unfinished recording. There is no new check and no limit code. Universal words here ("none", "every unit") each cite the grep or probe above.

FOLLOW-UP: srccov-birthright-citizenship-debate-records-1119 Record S0002, S0004, S0008-S0011 (rows s7-2, s7-3) once relational-fol .ve files have a record form; the strict parser refuses comment lines
FOLLOW-UP: srccov-birthright-citizenship-debate-s0001-1119 S0001 "Should America end birthright citizenship?" absent, not recordable (modal "Should", METHOD amendment 12)
FOLLOW-UP: srccov-birthright-citizenship-debate-s0006-1119 S0006 "Mayes, on the text: The 14th Amendment states..." absent, not recordable (ordinal "14th", METHOD amendment 12, conservative reading)
