# fsf-repair-f6-sl2plus-1119 REPORT (row F6: SL2+ and SL3/SL4 descriptions on the SEC answers)

Nothing is reserved for the DRI. LANGUAGE only: one legend in `usecases/safety-framework/vocabulary.py` now quotes the
pinned source, and the files that hash the legend are regenerated. The carrier check passed (R16 C5 dry-run, below), so
the row's FALLBACK (B's unit attribution, adding `measures-sl2plus` to the SEC answers) was **not** used.

**Merge commit.** The VE text this item adds is first in commit 3cfe696a47 and was dry-run at 44100262e4. The later
commits change only `docs/` and do not touch the rendered text. The work was built on main d8758ce968, then synced with
main f5553bc894 (merge 5122cdbd6c). Main added only docs/infra files, so nothing rendered changed. The item merges at
this branch's final HEAD, and the train names the exact merge commit. A merge after the R16 diagnostic voids the diagnostic
for the touched answers, since the C2/C3 pins are per commit. The counted read re-pins at the merge commit.

SIZE: 13 product (vocabulary.py; environment.d1.json is generated), 76 tests, 149 other hand-written lines
(REPORT.md 109, DELTA.md 8, c5-dryrun.txt 32: docs and evidence). LIGHT lane: `light-lane.py check` printed "LIGHT 102 changed lines
outside generated files <= 150 (7 files), no trusted-core file, against d8758ce9". So no trust_mutants sweep was run.

## The source passages (pinned FSF 3.1 text, sha256 18e3375b…3946, read with python3 -I over the pinned file)
- **S:9** (source line 9, 2.1.1; offset 2495 in the line): `We also define and recommend "Security Level 2+," which
  uses RAND Security Level 2 (SL2) as a baseline, with additional security measures designed to address risks from
  insider threats and well-resourced non-state external actors.`
- **S:15** (source line 15, table 3.2.2.a and its footnotes):
  - the ML R&D acceleration level 1 cell, with footnote mark 12: `Security level 3 12`;
  - footnote 12: `12 This level may include mitigations aligned with SL 2+, plus additional mitigations designed to
    prevent unilateral access, harden infrastructure, and prevent data exfiltration.`;
  - the ML R&D automation level 1 sentence, with footnote mark 13: `We recommend Security level 4 13 for this
    capability threshold, but emphasize that this must be taken on by the frontier AI field as a whole.`;
  - footnote 13: `13 This level may include mitigations aligned with SL 2+ and 3, plus additional mitigations aimed to
    isolate model weights, enhanced data center security, further hardening of infrastructure and minimizing potential
    attack surface.`

All of this text was taken from the pinned source, never from a reader, a flag or an analyst page. The condition test
checks it: it reads each passage from the source and requires it to occur exactly once there.

## Deliverables
| # | Row / task line | Delivered | Evidence |
|---|---|---|---|
| 1 | S:9 sentence plus the S:15 SL3/SL4 sentences with their footnotes, verbatim, in legend form | `BASE["recommends"]` legend (3cfe696a47). The base text "the framework recommends {1} for models reaching {0} (tables 2.2.1.a to 3.2.2.a)" is kept, and its verbalisation and arguments are unchanged | `tests/test_fsf_repair_f6_sl2plus_1119.py::test_the_recommends_legend_quotes_the_security_level_sentences_whole` |
| 1a | CARRIER GUARD: a legend of a predicate the blocks use, not the MEASURES constant | `recommends` is used by facts.d1.ve (the FACTS unit) for every level → security level fact. All five target answers read FACTS (manifest `uses`: A-L2-EXT/SEC, G1 FACTS+CASES+f9-sec; N2 FACTS; R8/ACCEPTABLE FACTS+CASES; S4 FACTS+D2D3). `MEASURES["security_level_2_plus"]` is left as it was | `…::test_the_recommends_legend_is_a_carrier_of_the_facts_unit`; C5 dry-run below |
| 1b | C5 dry-run: each appended passage in the target prompts inside a counted carrier; max prompt size ≤ 131,000 | Passes 5/5 answers × 5/5 passages, on the `- recommends:` line of "VOCABULARY LEGENDS (environment.d1.json) of the predicates this unit uses:" after the FACTS unit. Max step-1 prompt 116,232 bytes (D3); at the merge base it was 113,909 | `c5-dryrun.txt` (this directory) |
| 1c | A legend append leaves plan.json unchanged | `--dry-run` plan.json for the five targets, merge base against this branch: only `ve_commit`, `run` (the /tmp copy), one `commit` and `written` differ | `c5-dryrun.txt`, last section |
| 1d | Regenerate generated files with their writers | 44100262e4: `results.json` (`uv run python usecases/safety-framework/run.py`; 2 `certificate_sha256` lines change, no verdict changes), `coverage.json` (`build_document.py --source /tmp/f6src/fsf-3.1.txt`; `document_sha256` only), `tests/data/route-cases.jsonl` (`docs/en-e3-norm/en-2b/route_fixtures.py --write`; the `stale` case embeds this environment), `conformance/english-lean/lexicon-report.json` (`conformance/english_lean_lexicon.py`: `{"valid": 43, "invalid": 0}`), `environment.d1.json` (`vocabulary.py`) | `uv run python tools/regen_generated.py --check`: rc=0, "checked 41 entries" |
| 2 | Condition test in a NEW file | `tests/test_fsf_repair_f6_sl2plus_1119.py`. It fails at the merge base (vocabulary.py and environment.d1.json checked out from d8758ce968: "1 failed, 1 passed"); 7cbec4b340b8 also lacks the text (`git show … \| grep -c` = 0). It passes on HEAD ("2 passed") | the commands in this report |

**How the dry-run was run.** No file under manage-agents was changed:
```
cp -r debates/uc-audit-safety-framework-20261115T1505Z /tmp/f6-run    # manifest ve_commit := 44100262e4…
UC_AUDIT_R16_PINS=/tmp/f6-pins.json python3 -I tools-local/omission-seq-read.py.reads-1119 --run /tmp/f6-run \
  --counter tools-local/uc-audit.py.reads-1119 --dry-run-all --out /tmp/f6-render-head
```
- The counter refuses a commit that has no pins entry ("pin one for this commit, never carry it").
- For this dry-run only, `/tmp/f6-pins.json` keys the da0822ae80 entry to the branch commit and to the merge base. It is a render check, not a pin: the counted read must pin its own commit through the decider.
- I ran the same command at the counted commit as is (196 answers, max 113,909, OK) and at the merge base (238 answers, max 113,909, OK) for comparison.
- Answer counts are 238 rather than 196 because main has gained answers since da0822ae80.

## Kind call your reviewer should check
The row records no "KIND CALLS STILL DIFFER" for F6. One call is still open: B's TEXT-UNITS against A's LANGUAGE for
A-L2-EXT/SEC, G1 and R8/ACCEPTABLE (converge-AB.md F6).
- I carried the text in legend form, as both analysts agreed on the action.
- N2 and S4 clear only if their reader-side flags clear (B: READER-SEPARATE). That is out of scope here.

## Seeded bugs (Python only; it is the only product language changed)
Each was planted in `usecases/safety-framework/vocabulary.py` and checked with `uv run pytest -q -rs
tests/test_fsf_repair_f6_sl2plus_1119.py`. Each was then restored with `git checkout`, and the file then gave "2 passed".
| # | Mutant (vocabulary.py, `recommends` legend) | Result |
|---|---|---|
| M1 | S:9 cut back to "… as a baseline, with additional measures." (the old paraphrase) | 2 failed: the condition test, and the carrier test (committed ≠ written) |
| M2 | footnote mark dropped: `"Security level 3 12"` → `"Security level 3"` | 2 failed |
| M3 | footnote 13 reworded: "SL 2+ and 3, plus" → "SL 2+, plus" | 2 failed |
| M4 | base legend's text changed at the join ("Security Level 2+" → "Security Level 2 +") | 1 failed (condition test) |

## Trust
`uv run python tools/trust_map.py --check`: "against d8758ce96837: K +0, S +0, D +0, G +0, tied +0, unclassified +0,
trusted +0 … PASS". There is no new trusted definition, so no R16 mutants or FOLLOW-UPS row is needed.

## Tests
- Selected run: `mac-pytest.sh --select -- --base d8758ce968 --run`. It ran on the VM ("no mac-pytest slot on ve-mac-1"), with exit=0 in 7242 s: "recorded 75 units … 0 failed".
  - It included tests/test_fsf_repair_f6_sl2plus_1119.py, tests/test_safety_framework.py, tests/test_safetyfw_usecases.py and tests/test_route_row_schemas.py.
  - One file was deferred to the chain gate: tests/test_relay_binding_inventory.py, "selected only for weak reasons" (log /tmp/f6-select.log).
- Pre-existing red tests: none met.

## Pilot bytes expected to move (estimate; nothing is claimed before a pilot audit)
- The legend grows by 995 bytes (80 → 1,075 in environment.d1.json).
- Each prompt that reads FACTS grows by about 1 kB. A-L2-EXT/SEC: 90,852 → 91,847. The max (D3): 113,909 → 116,232.
- Answers this could clear: 4 alone (A-L2-EXT/SEC, G1, N2, R8/ACCEPTABLE), or 3 strictly by B's count. S4 adds 1 by weights.

## Notes for the DRI
- This item takes the narrower reading of "the S:15 SL3/SL4 sentences with their footnotes". It carries:
  - the SL3 cell and the SL4 recommendation sentence, with their marks 12 and 13;
  - the two footnotes.
- It does not carry the table's rationale sentences ("Unrestricted access to models …").
- It does not carry the S:9 follow-on list ("These additional measures may include, for example: …"). The row names only the one S:9 sentence.
- The MEASURES constant `security_level_2_plus` keeps its short text. C5 does not render constants, and the row puts the sentence in a legend.
- Sibling overlap: only feature/fsf-repair-f5-lowrisk-1119 touches vocabulary.py, at `low_risk`, a different hunk. Both items regenerate the same four hash files, so whichever merges second regenerates them with their writers.

## Self-review against BUILDER-CHECKLIST
1. Typed/contained Lean answers: N.A. (no relayed route or Lean answer changed).
2. Deliverables built, no rule broken: PASS (Deliverables table; `git diff --name-only` stays within the task's paths plus the four regenerated hash files; no Python copy of a Lean decision, no report test).
3. Tests can fail: PASS (seeded bugs M1-M4; base run "1 failed, 1 passed").
4. Python/Lean/Rust agree: N.A. (no checker code changed; results.json verdicts unchanged, 2 certificate hashes only).
5. R8 binding: N.A. (no relay field).
6. Gate evidence matches final HEAD: PASS (`c5-dryrun.txt` was taken at 44100262e4, and the later commits change only docs. The chain gate runs on the final HEAD).
7. No unsigned item: PASS (DELTA.md has no rows; trust +0, `tools/trust_map.py --check` PASS).
8. Every user-visible change in DELTA: PASS (DELTA.md: no VE-visible delta; `git diff -U0 results.json` shows hashes only).
9. Test selection finds the tests: PASS (the selected log "changed: … vocabulary.py …" selected test_fsf_repair_f6_sl2plus_1119.py and test_safety_framework.py).
10. Lean statements: N.A. (no Lean change).
11. Budgets/limits fail closed: N.A. (no evaluator, runner or limit).
12. CPU/memory: N.A. (no code path changed; prompt size measured: max 116,232 ≤ 131,000, `c5-dryrun.txt`).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS (the condition test fails at base and passes at HEAD; the carrier test passes at both, since it is a guard. Each claim cites a command. Spec re-read: the row F6 text in the task and converge-AB.md:38-47 against the legend, the passages and the fallback condition).
15. No overclaim, no silent cut, checks can fail, limits: PASS (nothing is cut; the fallback was not needed and this report says so; M1-M4; no limit added).
