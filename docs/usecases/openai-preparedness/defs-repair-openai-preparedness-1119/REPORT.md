# defs-repair-openai-preparedness-1119: REPORT

Status: built; no DRI signature reserved. 48 of 48 P1 rows KEPT and carried word for word; 10 of them on another carrier
than the row names (rows 18-25 by the DRI decision of 2026-11-20 item 1a; rows 11 and 40 by the same move, for two PF
fidelity tests). C5 dry-run NOT RUN: PF has no R16 pin entry (runner refuses the plan); measured by the DRI decider 2026-11-20.
VE commit this merges at: main f21b79f71e (rebased onto it; built first on 09bea0972d). Answers touched: see "Answers".

## Verification (deliverable 0)

Pinned source: ~/code/manage-agents/pilots/openai-preparedness/source/pf-v2.txt, sha256 d2e3dd5b80e5…0d (67,418 bytes),
equal to usecases/pinned_sources.json `text_sha256` (`sha256sum`, checked before any edit). Frozen text the reader is
shown: usecases/openai-preparedness/pf_vocabulary.py and environment.d1.json at main; PF changed nowhere between the
audit pin e53db4e8fc and main (`git log e53db4e8fc..main -- usecases/openai-preparedness/` empty). No frozen or sealed
run directory under usecases/openai-preparedness (`git ls-files | grep frozen-run` lists udhr-pilot only).

Checks (scripts in /tmp/dr-pf, not committed): (a) each of the 49 inventory entries the P1 rows use is in the pinned
text at the lines below after omit_norm plus the audit's extraction repairs ("T racked", "amalicious", a line-break
hyphen, a space before punctuation, the page footer of a span that crosses a page: E06 at line 7, E47 at line 21); (b)
each row's quote equals its entries joined with one space (48 of 48); (c) the row's carrier predicate is used, by the
counter's used_predicates, by every rule the row lists or reaches it through FACTS (48 of 48); (d) the whole quote is in
no carrier legend at main (48 of 48); (e) the term occurs in the listed rules (header quote, rule text or used legends;
the 4 heuristic misses read by hand: f17-* "severe" criterion, f5-checkpoint "severe risk", f1-contrib-cyb a High level,
f1-misuse-* misuse). No row was dropped.

| row id | KEPT / DROPPED | reason (file:line) |
|---|---|---|
| defs-openai-preparedness-1-1119 | KEPT | severe harm: pf-v2.txt:2 (E01), verbatim after normalisation; `high` legend (pf_vocabulary.py:62 at main) does not hold the whole quote |
| defs-openai-preparedness-2-1119 | KEPT | High capability thresholds: pf-v2.txt:5, pf-v2.txt:15 (E14, E16), verbatim after normalisation; `high` legend (pf_vocabulary.py:62 at main) does not hold the whole quote |
| defs-openai-preparedness-3-1119 | KEPT | Critical capability thresholds: pf-v2.txt:5, pf-v2.txt:15 (E15, E17), verbatim after normalisation; `critical` legend (pf_vocabulary.py:63 at main) does not hold the whole quote |
| defs-openai-preparedness-4-1119 | KEPT | BIO-H level (Table 1): pf-v2.txt:6 (E21), verbatim after normalisation; `high` legend (pf_vocabulary.py:62 at main) does not hold the whole quote |
| defs-openai-preparedness-5-1119 | KEPT | CYB-H level (Table 1): pf-v2.txt:6 (E23), verbatim after normalisation; `high` legend (pf_vocabulary.py:62 at main) does not hold the whole quote |
| defs-openai-preparedness-6-1119 | KEPT | AIS-H level (Table 1): pf-v2.txt:7 (E25), verbatim after normalisation; `high` legend (pf_vocabulary.py:62 at main) does not hold the whole quote |
| defs-openai-preparedness-7-1119 | KEPT | BIO-C level (Table 1): pf-v2.txt:6 (E22), verbatim after normalisation; `critical` legend (pf_vocabulary.py:63 at main) does not hold the whole quote |
| defs-openai-preparedness-8-1119 | KEPT | CYB-C level (Table 1): pf-v2.txt:7 (E24), verbatim after normalisation; `critical` legend (pf_vocabulary.py:63 at main) does not hold the whole quote |
| defs-openai-preparedness-9-1119 | KEPT | AIS-C level (Table 1); recursively self improving: pf-v2.txt:7 (E26), verbatim after normalisation; `critical` legend (pf_vocabulary.py:63 at main) does not hold the whole quote |
| defs-openai-preparedness-10-1119 | KEPT | CDC Class A biological agent: pf-v2.txt:6 (E27), verbatim after normalisation; `critical` legend (pf_vocabulary.py:63 at main) does not hold the whole quote |
| defs-openai-preparedness-11-1119 | KEPT | Tracked Categories: pf-v2.txt:2, pf-v2.txt:5 (E02, E03), verbatim after normalisation; `in_category` legend (pf_vocabulary.py:61 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-12-1119 | KEPT | Biological and Chemical (category): pf-v2.txt:6 (E18), verbatim after normalisation; `in_category` legend (pf_vocabulary.py:61 at main) does not hold the whole quote |
| defs-openai-preparedness-13-1119 | KEPT | Cybersecurity (category): pf-v2.txt:6 (E19), verbatim after normalisation; `in_category` legend (pf_vocabulary.py:61 at main) does not hold the whole quote |
| defs-openai-preparedness-14-1119 | KEPT | AI Self-improvement (category): pf-v2.txt:7 (E20), verbatim after normalisation; `in_category` legend (pf_vocabulary.py:61 at main) does not hold the whole quote |
| defs-openai-preparedness-15-1119 | KEPT | Research Categories: pf-v2.txt:2, pf-v2.txt:5, pf-v2.txt:7-8, pf-v2.txt:15 (E04, E05, E06, E07), verbatim after normalisation; `research_review` legend (pf_vocabulary.py:241 at main) does not hold the whole quote |
| defs-openai-preparedness-16-1119 | KEPT | Research Categories: pf-v2.txt:2, pf-v2.txt:5, pf-v2.txt:7-8, pf-v2.txt:15 (E04, E05, E06, E07), verbatim after normalisation; `research_category_review` legend (pf_vocabulary.py:131 at main) does not hold the whole quote |
| defs-openai-preparedness-17-1119 | KEPT | Research Categories: pf-v2.txt:2, pf-v2.txt:5, pf-v2.txt:7-8, pf-v2.txt:15 (E04, E05, E06, E07), verbatim after normalisation; `ara_tracking` legend (pf_vocabulary.py:282 at main) does not hold the whole quote |
| defs-openai-preparedness-18-1119 | KEPT | capability thresholds: pf-v2.txt:5 (E13), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-19-1119 | KEPT | Safety Advisory Group (SAG): pf-v2.txt:4 (E40), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-20-1119 | KEPT | covered (deployments): pf-v2.txt:10 (E36), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-21-1119 | KEPT | Preparedness Framework: pf-v2.txt:2 (E49), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-22-1119 | KEPT | OpenAI Leadership: pf-v2.txt:16 (E42), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-23-1119 | KEPT | malicious user / misaligned model: pf-v2.txt:11 (E44), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-24-1119 | KEPT | Safeguards Report (content): pf-v2.txt:11 (E39), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-25-1119 | KEPT | Capabilities Reports and Safeguards Reports (change log 8): pf-v2.txt:15 (E38), verbatim after normalisation; `reached` legend (pf_vocabulary.py:68 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-26-1119 | KEPT | Capabilities Report: pf-v2.txt:10 (E37), verbatim after normalisation; `capabilities_report` legend (pf_vocabulary.py:211 at main) does not hold the whole quote |
| defs-openai-preparedness-27-1119 | KEPT | Capabilities Report: pf-v2.txt:10 (E37), verbatim after normalisation; `third_party_evaluation` legend (pf_vocabulary.py:301 at main) does not hold the whole quote |
| defs-openai-preparedness-28-1119 | KEPT | Plausible (criterion): pf-v2.txt:5 (E08), verbatim after normalisation; `criteria_tracking` legend (pf_vocabulary.py:137 at main) does not hold the whole quote |
| defs-openai-preparedness-29-1119 | KEPT | Measurable (criterion): pf-v2.txt:5 (E09), verbatim after normalisation; `criteria_tracking` legend (pf_vocabulary.py:137 at main) does not hold the whole quote |
| defs-openai-preparedness-30-1119 | KEPT | Severe (criterion): pf-v2.txt:5 (E10), verbatim after normalisation; `criteria_tracking` legend (pf_vocabulary.py:137 at main) does not hold the whole quote |
| defs-openai-preparedness-31-1119 | KEPT | Net new (criterion): pf-v2.txt:5 (E11), verbatim after normalisation; `criteria_tracking` legend (pf_vocabulary.py:137 at main) does not hold the whole quote |
| defs-openai-preparedness-32-1119 | KEPT | Instantaneous or irremediable (criterion): pf-v2.txt:5 (E12), verbatim after normalisation; `criteria_tracking` legend (pf_vocabulary.py:137 at main) does not hold the whole quote |
| defs-openai-preparedness-33-1119 | KEPT | Long-range Autonomy: pf-v2.txt:8 (E28), verbatim after normalisation; `misalignment_report` legend (pf_vocabulary.py:276 at main) does not hold the whole quote |
| defs-openai-preparedness-34-1119 | KEPT | Sandbagging: pf-v2.txt:8 (E29), verbatim after normalisation; `sandbagging_response` legend (pf_vocabulary.py:277 at main) does not hold the whole quote |
| defs-openai-preparedness-35-1119 | KEPT | Autonomous Replication and Adaptation: pf-v2.txt:8 (E30), verbatim after normalisation; `ara_tracking` legend (pf_vocabulary.py:282 at main) does not hold the whole quote |
| defs-openai-preparedness-36-1119 | KEPT | Undermining Safeguards: pf-v2.txt:8 (E31), verbatim after normalisation; `robust_case` legend (pf_vocabulary.py:283 at main) does not hold the whole quote |
| defs-openai-preparedness-37-1119 | KEPT | Nuclear and Radiological: pf-v2.txt:8 (E32), verbatim after normalisation; `nuclear_safeguards` legend (pf_vocabulary.py:287 at main) does not hold the whole quote |
| defs-openai-preparedness-38-1119 | KEPT | Scalable Evaluations: pf-v2.txt:9, pf-v2.txt:15 (E33, E34), verbatim after normalisation; `evaluations_before_deployment` legend (pf_vocabulary.py:208 at main) does not hold the whole quote |
| defs-openai-preparedness-39-1119 | KEPT | Scalable Evaluations: pf-v2.txt:9, pf-v2.txt:15 (E33, E34), verbatim after normalisation; `capabilities_report_submitted` legend (pf_vocabulary.py:213 at main) does not hold the whole quote |
| defs-openai-preparedness-40-1119 | KEPT | Deep Dives: pf-v2.txt:9, pf-v2.txt:15 (E35, E34), verbatim after normalisation; `third_party_evaluation` legend (pf_vocabulary.py:301 at main) does not hold the whole quote; carried on `existing_at_publication` (pf_vocabulary.py:96 at main) instead, see Carriers |
| defs-openai-preparedness-41-1119 | KEPT | SAG Chair: pf-v2.txt:16 (E41), verbatim after normalisation; `chair_coordination` legend (pf_vocabulary.py:298 at main) does not hold the whole quote |
| defs-openai-preparedness-42-1119 | KEPT | Board (OpenAI Board of Directors): pf-v2.txt:16 (E43), verbatim after normalisation; `board_finds_necessary` legend (pf_vocabulary.py:115 at main) does not hold the whole quote |
| defs-openai-preparedness-43-1119 | KEPT | High standard against misuse (Appendix C.1): pf-v2.txt:17 (E45), verbatim after normalisation; `misuse_safeguards` legend (pf_vocabulary.py:176 at main) does not hold the whole quote |
| defs-openai-preparedness-44-1119 | KEPT | High standard against misalignment (Appendix C.2): pf-v2.txt:19 (E46), verbatim after normalisation; `alignment_safeguards` legend (pf_vocabulary.py:184 at main) does not hold the whole quote |
| defs-openai-preparedness-45-1119 | KEPT | High standard against misalignment (Appendix C.2): pf-v2.txt:19 (E46), verbatim after normalisation; `misalignment_risk_minimized` legend (pf_vocabulary.py:264 at main) does not hold the whole quote |
| defs-openai-preparedness-46-1119 | KEPT | security controls meeting High standard (Appendix C.3): pf-v2.txt:21-22 (E47), verbatim after normalisation; `security_controls` legend (pf_vocabulary.py:182 at main) does not hold the whole quote |
| defs-openai-preparedness-47-1119 | KEPT | security practices (Appendix C.3): pf-v2.txt:21-22 (E47), verbatim after normalisation; `security_practices` legend (pf_vocabulary.py:207 at main) does not hold the whole quote |
| defs-openai-preparedness-48-1119 | KEPT | another developer scenario (4.3): pf-v2.txt:13 (E48), verbatim after normalisation; `adjustment_confirmed` legend (pf_vocabulary.py:80 at main) does not hold the whole quote |

## What changed

- `usecases/openai-preparedness/pf_vocabulary.py`: 24 predicate entries. Each legend keeps its old text and appends
  "; the Framework's words, " then, per row in row order, the row's section label, ": " and its quote, as implicitly
  concatenated string literals (the counter's legend_raw reads literal strings only, at most 41 lines per entry: the
  largest entries, existing_at_publication, security_controls and security_practices, use 37, 36 and 36 lines;
  `security_practices`' old description moved to its own line for that).
- Derived, each by its own tool: environment.d1.json (`uv run python usecases/openai-preparedness/pf_vocabulary.py`),
  coverage.json (`build_document.py`; one line; content not opened under the SEAL; `--check` exit 0), lexicon-report.json
  (`uv run python -m conformance.english_lean_lexicon`: valid 43, invalid 0), corpus-seal.json (`uv run python -m
  conformance.english_lean_seal`). None is in tools/regen_generated.py's list. results.json was not regenerated: it is
  sealed for this item and not in the rows' derived_files; the selected run found nothing stale.
- New test `tests/test_defs_repair_openai_preparedness_1119.py` (52 tests). Stores the 49 sentences with their
  pf-v2.txt lines and section and the 48 rows with their carriers. Per row: the quote, after its label, is in the
  committed and the built `description` (equal), and in a counted string of the entry (the counter's own legend_raw and
  _omit_legend_segments from tools/defs_carried_counter.py). It also checks the old legend is kept and, with the pinned
  text present (tests/pinned_source.py, never downloads), each sentence at its lines. On main's pf_vocabulary.py and
  environment.d1.json: 49 failed, 3 passed (the 48 rows and the append check fail; /tmp/dr-pf/t-main.log); here 52 passed.
- Shared tests (the change required them; both keep their check):
  - `tests/test_pf_fidelity_fix.py::test_retagged_legend_quotes_are_verbatim_source_text` pinned the whole
    existing_at_publication legend with `==`. It now checks the same text as a prefix, followed by
    "; the Framework's words, ". Its 4.4 quote and source checks are unchanged and pass with the new quotes.
  - `tests/test_fidmech_records.py`: Appendix C.3's "ensuring resilience against unknown vulnerabilities" (rows 46,
    47) made the security legends third-value strings for the kill-rule scan. `SOURCE_QUOTES` lists that phrase as
    quoted source, and the test asserts the phrase is seen. Seeded bug M5 shows another "unknown" string still fails.

## Carriers (rows not on the carrier the row names)

- Rows 18-25 (thresholds, SAG, covered, Preparedness Framework, OpenAI Leadership, malicious user, Safeguards Report,
  Capabilities and Safeguards Reports): from `reached` to `existing_at_publication`, by the DRI decision
  (manage-agents reviews/dri-decisions-20261120-defs-repair-openai-preparedness-1119.md item 1a). existing_at_publication
  is the one predicate only the FACTS unit uses (no rule block: the counter's used_predicates). It is shown once with
  every answer and counted for every rule. `reached` is used by 34 rule blocks and would repeat 2.7 KB in each.
- Rows 11 (Tracked Categories, E02+E03) and 40 (Deep Dives, E35+E34): also moved to existing_at_publication. That is
  the same move for a different cause, taken as the conservative option (overrides rule 2) and recorded here:
  - On `in_category`, E03's "measuring them during each covered deployment" fails
    `test_pf_fidelity_fix.py::test_f3_development_units_read_no_coverage_condition`. Rules f3-* read in_category, and
    that DRI fidelity rule forbids "covered" in any legend they read.
  - On `third_party_evaluation`, E34's quotation marks (“scalable evaluations,” “deep dive”) fail
    `::test_f15_third_party_act_is_openais_work_with_third_parties`. Its legend's quotations must be exactly the 5.2
    sentence.
  - Both rows reach every rule they list through FACTS. The DRI ruling's "every other carrier stays" predates these two
    failures (first selected run, /tmp/dr-pf/select.log: 4 failed).
- Row 20 stays off `covered`: the counter matches no block to `covered` (it has no verbalisation), so its legend is never
  counted.

## Prompt size (C5)

C5 dry-run NOT RUN: PF has no R16 pin entry (runner refuses the plan); measured by the DRI decider 2026-11-20. I did not
run it either: omission-seq-read.py needs a PF uc-audit debate directory (a read output) and its documented invocations
are under reviews/pathf-q3/, both outside this item's SEAL. Measured instead, with the counter's own renderer
(uc-audit.py.reads-1120 `seq_unit_text`, no read output), every unit at main and here:
- evidence/prompt-units.json (all rows on the rows' carriers, 9a3fa50db7): FACTS 3,271 -> 10,644 (+7,373), the three
  security units +8,809 each, 69 of 103 units grow.
- evidence/prompt-units-moved.json (final carriers, fd322bf099; the same at f21b79f71e): FACTS 3,271 -> 11,339
  (+8,068, every answer); no-critical-models +6,227; f1-security-default, f1-security-strict, f4-security +5,969 each;
  rs2-nest +3,722; f12-undermining(-unscoped) +3,466; 64 of 103 units grow; D2D3 unchanged (24,211).
- Upper bound from the last published PF maximum (110,338 bytes, T2, docs/infra/oseq-pf-d2d3-unit/REPORT.md:43):
  110,338 + 8,068 = 118,406; + one security unit 5,969 = 124,375; + a second = 130,344; + a third = 136,313, over
  131,000. Which answers use which units is in the sealed plan, so the largest prompt is not known here. Per the ruling
  (item 1c) the runner's limit check is fail-closed, and the PF pin step runs --dry-run-all and cuts any answer over
  131,000 with its numbers.
- Pilot bytes the item is expected to move (estimate, nothing claimed before a pilot audit): 48 pairs' definitions,
  30,354 bytes of source text in the audit's sizing; FACTS +8,068 bytes per answer.

## Answers

Rows' answers_touched (k of 239 keyed, from the audit TSV; later reads re-pin at this item's merge commit):
1: 51; 2: 174; 3: 134; 4: 59; 5: 84; 6: 30; 7: 38; 8: 28; 9: 30; 10: 38; 11: 180; 12: 85; 13: 101; 14: 55; 15: 2; 16: 3;
17: 3; 18: 7; 19: 199; 20: 84; 21: 13; 22: 6; 23: 67; 24: 17; 25: 26; 26: 2; 27: 3; 28: 2; 29: 2; 30: 2; 31: 2; 32: 2;
33: 9; 34: 3; 35: 3; 36: 3; 37: 4; 38: 2; 39: 10; 40: 3; 41: 3; 42: 3; 43: 31; 44: 32; 45: 4; 46: 31; 47: 30; 48: 34.
The environment hash moves (DELTA row 2), so every PF answer's environment identity changes.

## Seeded bugs (Python; usecases/openai-preparedness/pf_vocabulary.py; all restored; evidence/seeded-bugs.log, mutants.json)

- M1 shown: "death or grave injury" -> "death or injury", regenerated: `test_each_row_quote_is_shown_and_counted_in_its_carrier_legend[1]` and the append test fail.
- M2 counted only: five empty literals push existing_at_publication past legend_raw's 41 lines, shown text unchanged: `...[40]` fails.
- M3 old legend changed ("is a High level" -> "is a high level"): `test_each_carrier_keeps_its_old_legend_and_appends_the_rows_in_order` fails.
- M4 not regenerated (M1 without environment.d1.json): `...[1]`, `[2]`, `[4]`, `[5]`, `[6]` fail (committed != built).
- M5 a legend with "result unknown": `test_fidmech_records.py::test_every_third_value_spelling_in_an_adapted_documents_sources_is_recognised_by_the_kill_rule` fails.
No Lean or Rust product code changed.

## Trust

`uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0; PASS.
`uv run python tools/trust_mutants.py --plan`: definitions 0, mutants 0 (no trusted Lean definition changed), so no
sweep (light-lane.py printed NOT: 1,919 changed lines, most of them verbatim source text). No R16 growth, no FOLLOW-UPS row.

## Test runs

- Selected run 1 (mac-pytest.sh --select, HEAD 3821953f48, /tmp/dr-pf/select.log): 4 failed, 941 passed in the fast units:
  test_fidmech_records third-value scan; test_pf_fidelity_fix f4-security, f3-development, f15-third-party. Fixed by
  the carrier move and the two shared-test changes above.
- Selected run 2 (HEAD 49c843e3ff, before the rebase; /tmp/dr-pf/select2.log): exit 0; fast units passed; shard 1/2
  30 units passed, shard 2/2 27 units passed; 2,042 s. The new test file was in it ("changed" order line).
- After the rebase onto f21b79f71e (no conflict; corpus seal regenerated): the new test file, test_english_lean_seal.py,
  the lexicon environment test and the five shared tests named above: 59 passed (/tmp/dr-pf/post-rebase.log).
- Full gate: left to the chain on the final HEAD.

SIZE: 305 product, 482 tests, 311 other hand-written lines (`git diff --numstat` against the merge base; pf_vocabulary.py
is product, 281 of its lines verbatim source text; plus 1,044 lines of script-written unit-size evidence JSON and 34
lines of generated files).

## Notes for the DRI

- Overlap: infra/srccov-openai-preparedness-1119 (in flight, 3 commits ahead of main at 471f12cc1d) also appends PF
  source definitions to pf_vocabulary.py legends, partly the same ones (high and critical with 2.2's threshold
  sentences, LEVELS strings with the Table 1 cells, covered with 3.2), plus environment.d1.json, coverage.json,
  spans.json and results.json. The two will conflict textually in pf_vocabulary.py, and merged naively the same
  sentences would be carried twice (more prompt bytes). Whichever merges second should drop the sentences the first
  already carries on the same rule's surface. I did not change my carriers for it: SYNTHESIS 4.2 has no queue for
  these 11-19 items, and the task's rows name pf_vocabulary.py.
- Shared-test edits outside the item's Paths list: tests/test_pf_fidelity_fix.py (one assertion `==` -> prefix) and
  tests/test_fidmech_records.py (SOURCE_QUOTES). Both are required by the carriers; neither weakens the check it names.
- main's corpus seal predates the FSF repair merges (FSF environment.d1.json 4c18fadd… in the seal, 6e7a75e3… on disk);
  the seal tool's rewrite here fixes it (DELTA row 2).
- P2 rows 49 (SSC) and 50 (published information) are not taken (task). No candidate of my own.
- The source text is duplicated where two carriers each need it counted (E04-E07 on research_review,
  research_category_review and ara_tracking; E47 on security_controls and security_practices; E46 on alignment_safeguards
  and misalignment_risk_minimized). The counter counts only an entry's own literal strings, so a shared constant would
  be shown but not counted.

## Merge of ve-integration 92d8ec4986 (srccov-openai-preparedness-1119 landed first)

- pf_vocabulary.py conflicted with srccov-openai-preparedness-1119, which also appends PF source text to legends.
  Resolution: main's file, plus this item's appended lines on the 24 carriers, added after main's text. On 17 carriers
  main changed nothing, so they are as on this branch. On the 7 both changed (high, critical, research_category_review,
  evaluations_before_deployment, misuse_safeguards, alignment_safeguards, security_practices), each legend is main's
  legend, then "; the Framework's words, " and this item's labelled quotes. Main's legend is kept whole as the prefix
  (its R1 prefix test and passage tests pass). Every other field of environment.d1.json equals main's (checked by
  script). The prefix test of this item reads those 7 old legends from evidence/legends-before-merge.json (saved
  from 92d8ec4986). It also checks that each one starts with its 09bea0972d legend.
- security_practices: main's 61 lines plus this item's 34 lines went past legend_raw's 41-line window, so row 47
  was shown but not counted (`test_each_row_quote_is_shown_and_counted_in_its_carrier_legend[47]` failed). The
  entry's literal was rewrapped to 38 lines, up to 296 characters wide. The text is unchanged and the built
  description is byte-equal.
- GAP (as the Notes predicted): on those 7 legends some source sentences now appear twice. Main quotes them one by
  one in “…” and this item quotes each row as one joined string. Neither copy can go. The counter counts a row only
  when its whole joined quote is in one literal, and main's tests require main's quoted passages. Bytes this item
  adds on the 7: alignment_safeguards 1,301; critical 1,881; evaluations_before_deployment 617; high 1,292;
  misuse_safeguards 1,035; research_category_review 1,849; security_practices 4,677 (12,652 in all, most of it a
  repeat of main's sentences). The C5 sizes above were measured before the merge, without main's additions. Still
  open for the DRI: one quoting form both counters accept, then deduplicate.
- Regenerated: environment.d1.json (pf_vocabulary.py), coverage.json (build_document.py), lexicon-report.json
  (regen_generated --resolve) and corpus-seal.json (conformance.english_lean_seal). The FSF environment hash in main's
  seal was stale again (e5a580e5… sealed, 42865a83… at 92d8ec4986, unchanged by this merge). The rewrite fixes it.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer or route changed).
2. Deliverables built, no rule broken: PASS. Deliverables 0-3 above, each with its commit and test; no Python copy of a
   Lean decision. Overlap (`git diff --name-only main...<branch>` over feature/infra/lean-first/foundation branches,
   2026-11-20): infra/srccov-openai-preparedness-1119 edits pf_vocabulary.py (hand-written; see Notes for the DRI);
   the other hits are generated files only (corpus-seal.json, lexicon-report.json: R12).
3. Tests can fail: PASS, M1-M5 (mutants.json); the condition test fails on main (49 failed).
4. Python, Lean and Rust agree: N.A. (no decision path; only descriptions differ in environment.d1.json, checked).
5. R8 binding: N.A. (no relayed field).
6. Gate evidence matches final HEAD: PASS for what I ran (rebased on main f21b79f71e, regenerated); full gate is the chain's.
7. No unsigned item: PASS, DELTA rows 1-2 cite R3 with tests; no reserved signature.
8. Every user-visible change in DELTA: PASS (24 descriptions, 5 ids; environment compared apart from descriptions: equal).
9. Test selection finds the tests: PASS (both selected runs included the new file and the shared tests that failed).
10. Lean statements: N.A. (no Lean).
11. Budgets and deadlines: N.A. (no limit or deadline code; tests use no sleep or timing).
12. No CPU or memory regression: N.A. (legend text only; prompt size reported under C5).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS (M2 shown-but-not-counted and M5 other-unknown refusals next to
    the passing cases; claims cite their command or log; METHOD amendments re-read for the carrier rule).
15. Four classes: no overclaim PASS (the "does not hold the whole quote" wording; prompt maximum stated as not known);
    no silent cut PASS (48 of 48 carried; C5 per the DRI ruling); every new check can fail PASS (M1-M5); limits charged
    before work N.A. (no evaluator or limit added).
