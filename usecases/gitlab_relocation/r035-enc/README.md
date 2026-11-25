# Fresh encoder fields for the R035 fix (row statute-corpus-gitlab-relocation-wrong-r035)

The fix (translation R17 / condition (i), encode.py E5) reads two fields the frozen encoder (1847cd06dc) never entered: the
written VP/PBP pre-approval of a relocation request ("wpre") and the stated facts with no predicate ("nopred", with the
unit each is about and whether that unit's outcome turns on it). They come from fresh Opus 5.5 encoder seats
(claude-opus-5-5, account claude-saeedi-danial: the picker's pick), each run in manage-agents
tools-local/xfam-enc/sandbox.sh (network only api.anthropic.com:443; the sandbox refuses a stage holding any sealed answer
file or questions.jsonl, by name or by content). Each stage held only: the prompt, questions-enc.jsonl (sha256 539ee4c5...,
the frozen encoder file), units.jsonl (the 34 units) and predicates.txt (the fix's vocabulary, generated from translation.py).
No seat saw a sealed directory, questions.jsonl, the frozen cases.py, a run or grade file, or any answer: the re-run is not
void.

| pass | prompt | output | when (UTC) | transcript sha256 |
|---|---|---|---|---|
| first (superseded) | prompt-first-pass.txt | enc-first-pass.jsonl | 2026-11-25 20:31:45-20:33:18 | 4436438d0fb74b1e... |
| second (USED) | prompt.txt | enc.jsonl (b05b2a14...) | 2026-11-25 20:34:12-20:36:16 | 0dad3cf56027bf51... |

The first pass asked only for the unit of each no-predicate fact. Applied at unit level, its facts would have refused
answers whose unit merely mentions the fact's subject (every acceptance answer through "takes a company-owned laptop",
unit 16, whose embargo list (c) reads), so E5 gained "turns_on" (does the unit's stated outcome depend on the fact; when
in doubt, true) and a second fresh seat encoded both fields again; only its output is used. The two passes agree on every
wpre value: R022-R034 true, R035 false, R001-R021 "n/a".

Applied mechanically by cases.py (FIX_ENC, sha256-checked): wpre on every request sub-case; every listed fact as
Sub.nopred(unit, fact, turns_on) on every sub-case of its case. Facts with turns_on true: unit 8 "travels as a digital
nomad" (R011-R014), unit 7 "Pia never asked about France or Belgium" (R016), unit 5 "has not obtained Trade Compliance
Counsel approval or contacted the People Operations Team" (R022-R035). Only R016's reaches a covered unit (unit 7, the
work rule): its six questions are refused.

Workdirs: ~/xfam-enc-runs/r035-enc-20261125T203106Z, ~/xfam-enc-runs/r035-enc2-20261125T203355Z (stages
r035-stage-20261125T203106Z, r035-stage2-20261125T203355Z; predicates.txt 9964045b... in both).
