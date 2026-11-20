# REPORT: srccov-claude-constitution-excerpt-1119

**Summary.**
- Status: no change to any carrier. All 8 candidate rows are DROPPED. Rows 1-6 (S0004-S0007, S0020, S0021): each unit is already carried word for word at main, in the legend of a sort that claims.ve uses (defs-repair-claude-constitution-excerpt-1119 carried them). Rows 8-9 and all 4 RECORDING units (S0001, S0010, S0013, S0016): the map's only allowed record file for this document is "comments in claims.ve", and claims.ve cannot hold a comment. Writing one needs a new language feature, which this task puts out of scope. No DRI signature is outstanding.
- HEAD: branch `infra/srccov-claude-constitution-excerpt-1119`, rebased onto VE main `12cb72fa55` (the merge base). The verify step ran on `09bea0972d`. `git diff --stat 09bea0972d 12cb72fa55 -- usecases/claude-constitution-excerpt/ tests/omission_rule.py` is empty, and verify.py's output on `12cb72fa55` is byte-identical to evidence/verify.log. The branch adds only this report and its evidence. Answers touched: none (no carrier byte changes, so environment_id `467d3440...` and model-true.json / model-false.json stay the same).
- Open: one FOLLOW-UP for the unfinished RECORDING deliverable (end of report). Trust +0. No DELTA rows: nothing the user sees changes.
- I did not run the full gate. The chain runs it on the final HEAD.

SIZE: 0 product, 0 tests, about 190 other hand-written lines (this report and the two evidence scripts).

## 0. Verify first (before any edit, on main `09bea0972d`)

Inputs: METHOD.md with its challenger amendments (4, 12, 13, 15c read), claude-constitution-excerpt.md, rows-claude-constitution-excerpt.tsv, CHALLENGE.md and challenge2/RESULT.md (manage-agents, reviews/source-coverage-1119/). The source is the in-repo `usecases/claude-constitution-excerpt/source.md`. It is the same at the map pin `e53db4e8fc` and at main: `git diff --stat e53db4e8fc HEAD -- usecases/claude-constitution-excerpt/` does not list source.md. The only commit since the pin that touches the use case is `268e712f1f` (defs-repair-claude-constitution-excerpt-1119), which carried seven source definitions in the legends.

Evidence:
- `evidence/verify.py` reads each candidate unit from source.md (the "N. " list marker is dropped). It checks each unit raw and after `omit_norm` (tests/omission_rule.py) in every file the reader is shown, and lists the vocabulary entries that hold it and whether claims.ve uses them. Output: `evidence/verify.log` (`uv run python docs/infra/srccov-claude-constitution-excerpt-1119/evidence/verify.py $PWD`).
- `evidence/comment-probe.sh` puts each candidate comment form on line 1 of a copy of claims.ve and renders it with the command that rendered.md records. Output: `evidence/comment-probe.log`. All 8 forms (`#`, `--`, `//`, `;`, `%`, `/- -/`, `(* *)`, `## id | ...`) give `rc=2 "SyntaxError: expected term", "line": 1`. The unchanged control gives `rc=0`. The same parser reads claims.ve everywhere (`parse(env, (... 'claims.ve').read_bytes())`, conformance/english_lean.py:352).

### Candidate rows

| row id | KEPT / DROPPED | units kept | reason (file:line) |
|---|---|---|---|
| srccov-claude-constitution-excerpt-s6-1-1119 | DROPPED | none | S0004 (source.md:16) is already carried at main, byte for byte, in the legend of sort `property` (environment.json:26). claims.ve:7-8 use that sort (`for every property`). The reader is shown it at rendered-english.md:51. verify.log rows s6-1: raw=True norm=True. |
| srccov-claude-constitution-excerpt-s6-2-1119 | DROPPED | none | S0005 (source.md:17) is already carried at environment.json:26 (`sorts.property`, used by claims.ve:7-8) and also in `predicates.honest` (claims.ve:3). Shown at rendered-english.md:51. |
| srccov-claude-constitution-excerpt-s6-3-1119 | DROPPED | none | S0006 (source.md:18) is already carried at environment.json:26 (`sorts.property`, used by claims.ve:7-8). Shown at rendered-english.md:51. |
| srccov-claude-constitution-excerpt-s6-4-1119 | DROPPED | none | S0007 (source.md:19) is already carried at environment.json:26 (`sorts.property`, used by claims.ve:7-8). Shown at rendered-english.md:51. |
| srccov-claude-constitution-excerpt-s6-5-1119 | DROPPED | none | S0020 (source.md:32) is already carried at environment.json:23 (`sorts.overseer`, used by claims.ve:11 `for every overseer`, and the sort of `@anthropic` in claims.ve:10). Shown at rendered-english.md:49. |
| srccov-claude-constitution-excerpt-s6-6-1119 | DROPPED | none | S0021 (source.md:33) is already carried at environment.json:23 (`sorts.overseer`, claims.ve:11), the whole unit including its "(see the section ...)" pointer. Shown at rendered-english.md:49. |
| srccov-claude-constitution-excerpt-s6-8-1119 | DROPPED | none | The record named is a comment in claims.ve, which METHOD section 0 gives as this document's only allowed record file. claims.ve cannot hold a comment: every comment form gives SyntaxError at 1:1 (evidence/comment-probe.log). The record therefore needs a new language feature (comment syntax in relational-fol claims files), which is out of scope. S0001 (source.md:13) and S0016 (source.md:28) are not recorded at main: verify.log, "claims.ve comment-like lines: []". |
| srccov-claude-constitution-excerpt-s6-9-1119 | DROPPED | none | Same reason as s6-8, for S0010 (source.md:22) and S0013 (source.md:25). |

Not a candidate here: row s6-7 (needs_rule_line=yes) is out of scope by the task.

I did not move the six already-carried units into the constant legends the map names (`constants.safety` ... at environment.json:108-111, `predicates.bound_to_obey`, `predicates.undermines_check`). The text is already carried in a legend the reader is shown. A second copy would carry nothing new, and it would move environment_id and the reviewed English overlay's binding.

### RECORDING (orchestrator ruling item 2a)

| unit | RECORDED / DROPPED | record file:line or reason |
|---|---|---|
| S0001 | DROPPED | Not recorded at main (claims.ve has no comment). Not recordable in this document's record file: claims.ve refuses every comment form (evidence/comment-probe.log). Kind: rationale/motivation. No amendment-12 marker: "can" is not on the modal list, and there is no number, date, definition or condition. |
| S0010 | DROPPED | Same reason as S0001. Kind: editorial annotation. No amendment-12 marker. |
| S0013 | DROPPED | Same reason as S0001. Kind: editorial annotation. No amendment-12 marker. |
| S0016 | DROPPED | Same reason as S0001. Kind: rationale/background. Amendment-12 reading: "which means" introduces a consequence, not the definition of a term. "before they proliferate" is temporal order, not a condition (if/when/unless). "could" is not on the modal list. See the note for the DRI below. |

## 1. Rows carried

None. No carrier, record file or derived file changed: `git diff --stat main...HEAD` lists only files under docs/infra/srccov-claude-constitution-excerpt-1119/.

## 2. Derived files

None regenerated, because no carrier changed. Because nothing changed, I did not regenerate the shared conformance/english-lean/corpus-seal.json, which the siblings also write.

## 3. Condition test

Not written: there is no kept carry or kept record for it to assert. Deliverable 3 asks for one case "for each kept carry ... for each kept record", and here there are zero. A test that passes on the pre-change main as well cannot meet the "fails on the pre-change main" condition. The six carried units are already guarded at main by tests/test_defs_repair_claude_constitution_excerpt_1119.py (`test_the_source_definition_is_carried_word_for_word`, rows 1 and 9).

## Seeded bugs

None, because no product code or carrier changed in any language (Lean, Python or Rust). The per-carry-kind seeded bug (remove one carried sentence, show the condition test fails) does not apply: no carry was made. The light lane and the trust_mutants sweep are not needed (no Lean change, and the task asks for no trust_mutants record).

## Tests run

- Selected run: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on commit `b4cd2b203b` (base `09bea0972d`). It ran on GitHub Actions in 6 shards, 53 units, 53 passed, 0 failed, exit 0 (run srccov-claude-constitution-excerpt-1119-b4cd2b20-t166195; shard lines "SHARD 1/6: ... 13 units, 13 passed" through "SHARD 6/6: ... 6 units, 6 passed"). After the rebase onto `12cb72fa55` the branch diff is the same (docs/infra only), so I did not repeat the run. The chain's gate runs on the final HEAD.
- No test in main-known-red.txt was touched.

## Notes for the DRI

1. METHOD section 0 gives "comments in claims.ve" as this document's only written out-of-scope record. No relational-fol claims file can hold a comment (evidence/comment-probe.log). The same is likely true for the other rows of that table that name comments in a `.ve` file read by this parser (us-constitution-14th-s1 and birthright claims.ve, asimov rules.ve, math premises). I did not probe those. Two ways to record the class: a comment form in the claims syntax (a language feature, for the architect's feature page), or a record file the DRI names for these documents. That is the FOLLOW-UP below.
2. S0016 sits on the amendment-12 edge ("which means", "before they proliferate", "it's important for humans to be able to identify and correct"). I read it as rationale, as the map does. Once a record form exists, a reviewer may still want it treated as ABSENT rather than recorded.
3. The map's rows 1-6 were read at pin `e53db4e8fc`, before defs-repair merged (`268e712f1f`). Its counts for this document (CARRIED-OTHER-WORDS 1, ABSENT 16) are stale by those six units. They are now CARRIED-VERBATIM via:legend.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer, schema or route touched).
2. Deliverables built, no rule broken: PASS. Deliverable 0 is the verify table (evidence/verify.log, evidence/comment-probe.log). Deliverables 1-3 are N.A. by the verify result, and RECORDING is dropped with its reason and a FOLLOW-UP. The diff holds no Python copy of a Lean decision and no permanent report test (`git diff --stat main...HEAD`: docs/infra only).
3. Tests and gates can fail: N.A. (no new check, test or gate).
4. Py/Lean/Rust agree: N.A. (no code changed).
5. R8 binding: N.A. (no field read from a Lean answer).
6. Gate evidence matches final HEAD: PASS. The branch sits on current main. The chain runs the gate on the committed final HEAD, and I ran no gate here.
7. No unsigned item: PASS. There is no DELTA row and no trust growth (no Lean file changed).
8. Every user-visible change in DELTA: N.A. (no carrier, output or derived file changed).
9. Test selection: PASS. The selected run under "Tests run" chose 53 units for a docs-only diff, not every unit.
10. Lean statements: N.A. (no Lean change).
11. Budgets fail closed: N.A. (no code).
12. No CPU or memory regression: N.A. (no code).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS. Each verify-table claim cites verify.log or comment-probe.log, which includes the parse control in the accepting direction. Spec re-read: the drop rule against the task text "Drop a row or unit that does not hold (unit already carried at main ... or it needs ... a new language feature ...)". The record file against METHOD.md:16 (section 0 table row claude-constitution-excerpt). The class-4 kinds against METHOD.md:35 and amendment 12 (METHOD.md:43).
15. Overclaim and silent cuts: PASS. "Not recorded at main" is shown by verify.log ("claims.ve comment-like lines: []"). "Already carried" is shown by verify.log, raw=True norm=True. "Every comment form refused" covers the 8 forms in comment-probe.log only, and the report says so. The cut of the RECORDING deliverable is not silent: it is in the table and in the FOLLOW-UP.

FOLLOW-UP: srccov-claude-constitution-excerpt-record-1119 Record S0001, S0010, S0013, S0016 as out of scope once claims.ve can hold a record (a comment form in the relational-fol claims syntax, or a record file the DRI names)
