# srccov-rl-question-answering-1121: REPORT

**Summary (5 lines).**
- Status: the one in-scope unit was checked and DROPPED. Nothing was carried, and no product, derived or test file changed. This REPORT is the only file in the diff.
- Base: main `cebf4fd24f`. The item merges at the commit the merge train names. It touches no answer, so no later read has to re-pin for it.
- Reason: the carrier is a hash-pinned, unchanged copy of the pilot translation. Writing u087's content would mean picking one of three readings that are deliberately left open. It would also change the checked answer U5.
- Open items: none in this item. Two other `none: translation omission` units (S0006, S0009) belong to rows that were not filed for this item; see Notes for the DRI.
- DRI signature needed: none. There are no DELTA rows, trust +0, no message sent to the DRI.

## 0. Verify table

| unit id | row id | KEPT / DROPPED | reason |
|---|---|---|---|
| S0004 | srccov-question-answering-s6-1-1119 | DROPPED | (a) The carrier is a sealed acceptance fixture: an "unchanged copy" with a pinned source SHA-256 (`usecases/question-answering/PROVENANCE.md:7-12`, `tests/test_question_fixture_sources.py:13,49-51`, and the `sha256` field of `tests/fixtures/ask/U2.json`..`U7.json`). No other file is read as this document, so the unit is NOT CARRIED. (b) Writing u087's content picks one reading from `rs_u087`, whose status is `open`, out of `entitlement`, `claim_negative` and `liberty` (`usecases/question-answering/udhr-part07.ve.md:2`). Picking one is a meaning decision, not a plain line, and the document is "never guessed" (`CLAUDE.md:9`). The map itself notes "reading not chosen (entitlement vs duty)". (c) The checked answer U5 would change (`docs/spec/question-answering.md:1373`, `tests/fixtures/ask/U5.json`, see section 3). |

Checks behind the table:
- The source text is the `.ve.md` body (map row header). Body line 4 of `usecases/question-answering/udhr-part07.ve.md` is the S0004 sentence word for word: `grep -n 'Everyone has the right to form' usecases/question-answering/udhr-part07.ve.md` → `4:4. Everyone has the right to form and to join trade unions for the protection ...`.
- The carrier has not changed since the map's pin. `sha256sum` of the file at HEAD and `git show e53db4e8fc:usecases/question-answering/udhr-part07.ve.md | sha256sum` both print `4f4e8c19c66c8232e8e34e03b53897974e5d8679b0adeef78a2fc5f1e2b825dd`, the PROVENANCE hash. `git diff --stat e53db4e8fc HEAD -- usecases/question-answering/` prints nothing.
- The unit is not carried at main. Parsing the front matter shows `u087 norm specified [0, 97]` with no `content`, and `rs_u087 open ['entitlement', 'claim_negative', 'liberty']`. Reading sets are not carriers (METHOD amendment 3). No earlier srccov/defs/fsf/rsp repair touched the file: `git log -- usecases/question-answering/udhr-part07.ve.md` lists only `fc1d84439e`.

## 1-2. Units carried, derived files

None. No line was written, so no spans or records changed and nothing was regenerated. `corpus-seal.json`, `wording-golden.json`, `tools/fidmech/manifests.py` and the `docs/question-answering/q1-3*/evidence` fixtures are untouched.

## 3. Answers touched

None changed. This answer would change if u087 got content, which is why the unit was dropped:
- **U5** "May every person form as well as join trade unions to protect their interests?" At main, `result.lead` is `by_reading`: the `liberty` reading gives yes, while `entitlement` and `claim_negative` give "the text does not settle this" (`docs/spec/question-answering.md:1373`; fixture `tests/fixtures/ask/U5.json`, pinned by `tests/test_ask_fixtures.py`). Any content for u087 settles the reading, so U5 would become one plain verdict. The source sentence is "Everyone has the right to form and to join trade unions for the protection of his interests." It does not say which reading is meant, which is the conservative reason to keep the reading open.
- U2, U3, U6 and U7 embed `rs_u087` in their recorded `case.document` and `names`, so a change to u087 would also change their recorded inputs and their sha256 binding.

## 4. Condition test and seeded bug

N.A.: no unit was kept. The task asks for one assertion per kept unit, and that assertion must fail on pre-change main. With zero kept units, any file would hold no assertion that could fail on main, so `tests/test_srccov_rl_question_answering_1121.py` was not created. Nothing was cut for size. There is no seeded bug because no product code changed in any language (Lean, Python or Rust). Light-lane and trust_mutants were not run, since no product code changed and no sweep is needed.

## Freeze

The item merges at whatever commit the merge train records; the base is `cebf4fd24f`. It touches no answers, so the Monday 2026-11-23 FSF freeze is not affected.

SIZE: 0 product, 0 tests, 1 other hand-written file (this REPORT).

## Notes for the DRI

- The map's other `none: translation omission` units for this document sit in rows this item was not filed for: S0006 (row s6-3, Art. 25(1), units u091/u092) and S0009 (row s6-4, Art. 26(1), u096, open set `rs_u096`). The same carrier freeze stops both of them. S0009 also has the same open reading-set problem as S0004, and it feeds U3 (`docs/spec/question-answering.md:1371`). S0006 is an `unformalised: other_act_phrase_grammar` known gap. I did not add them to this item.
- Pattern for the four question-answering rows: `udhr-part07.ve.md` is a hash-pinned acceptance fixture copied from `pilots/udhr/run-20261008T1800Z`, so no srccov row can add lines to it in place. Changing it would take a decision to re-pin the fixture and re-record U1-U9. That decision belongs with the question-answering fixtures, not with srccov. The UDHR text itself is covered by the sibling srccov-rl-udhr-pilot-1121.
- Conservative choices taken without asking: drop rather than choose a reading; no vacuous test file.

## Spec re-read

- "ONLY the units tagged 'none: translation omission'", and the row list naming only `srccov-question-answering-s6-1-1119`: checked against `reviews/source-coverage-1119/rows-question-answering.tsv` (row 1, tag `none: translation omission`, units `S0004`) and `part-question-answering-s6.tsv` (S0004 note `partial 0/1; reading not chosen (entitlement vs duty); also:modality`).
- "A carrier inside a frozen or sealed ... never rewrite sealed artefacts ... or report the unit NOT CARRIED": checked against the task text and `PROVENANCE.md:7-12`.
- "An existing CHECKED answer that would change status or verdict stops that unit": checked against U5 (`docs/spec/question-answering.md:1373`).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relay or schema changed.
2. Every deliverable built: PASS. Deliverable 0 is the table above. Deliverables 1-4 are N.A. with reasons, because there are zero kept units. The REPORT is at the required path.
3. Tests can fail: N.A., no test or check was added and no product code changed.
4. Py/Lean/Rust agree: N.A., no code changed.
5. R8 binding: N.A., no binding changed.
6. Gate evidence matches final HEAD: PASS once the chain's gate-result.json on the final HEAD passes; I did not run the gate myself (task rule).
7. No unsigned item: PASS, there is no DELTA row and no SIGNED cell (`git diff main...HEAD --stat` shows only this REPORT).
8. Every user-visible change in DELTA: N.A., there is no user-visible change.
9. Test selection: PASS, the selected run on this branch (see below).
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: N.A., no budget code.
12. No CPU or memory regression: N.A., no code.
13. Test-removed trailers: N.A., no test was removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Every claim above names its command or file:line, and the spec re-read is listed.
15. Overclaim, silent cut, new checks fail, limits: PASS for overclaim (each "none" or "unchanged" above cites `git diff --stat` or `sha256sum`) and for silent cut (section 4 states the N.A. reason). New checks and limits: N.A.

Selected tests: `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on `add3a109f3` exited 0 (ran on ve-cloud-2 in 1501 s, "0 failed"; log /tmp/qa1121-select.log). `tools/regen_generated.py --check` fails only `route-cases` and `checker-pins`, and both need the Rust release binary, which this worktree has not built ("the Rust release binary is missing or not pinned"). This REPORT feeds neither check. The chain's gate runs with the built binaries.
