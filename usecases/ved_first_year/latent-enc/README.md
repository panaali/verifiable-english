# Fresh encoder field for the 1GA(1A) fix (row statute-latent-ved-first-year-I1, latent departures I1 and I2)

The fix (translation R7 / unit 42, encode.py C6) reads one fact neither frozen encoder ever entered: `mcaravan` (1GA(2A):
the certificate on the basis of which the vehicle was first registered identifies it as a motor caravan). It comes from
one fresh Opus 5.5 encoder seat (claude-opus-5-5, the picker's pick: claude-panaali2), run in manage-agents
tools-local/xfam-enc/sandbox.sh (network only api.anthropic.com:443; the sandbox refuses a stage holding any sealed answer
file or questions.jsonl, by name or by content). The stage held only: prompt.txt, set-a.jsonl (= questions-enc.jsonl,
sha256 19493bd2..., the same-family encoder file), set-b.jsonl (= xfam/questions-enc.jsonl, sha256 2e5541f3..., the
cross-family encoder file) and source.txt (the pinned law; staged.sha256 here). The seat saw no sealed directory, no
questions.jsonl, no cases.py, no run or grade file and no answer: the re-run is not void.

| pass | account | prompt | output | when (UTC) | transcript sha256 |
|---|---|---|---|---|---|
| only (USED) | claude-panaali2 | prompt.txt | enc.jsonl (479ae219...) | 2026-11-25 23:40:50-23:41:16 | a3f0bc557900bb6d... |

Result: 70 in-scope cases (35 per set), 108 vehicles (35 + 73): mcaravan **false for all 108** (true 0, unknown 0); the
seat read every case's facts and searched them for caravan / motorhome / camper / living accommodation / special purpose /
category wording; no in-scope sentence bears on it (the only motor caravan, V039 in both sets, is an out-of-scope probe).
`build_record.py` turns enc.jsonl into mcaravan.json (vehicles matched by order, set-b owners checked against
xfam/cases_xfam.V; each case keyed by id + sha256 of its encoded vehicles). Workdir ~/xfam-enc-runs/ved-mc-enc-20261125T233457Z
(stage ~/xfam-enc-runs/ved-mc-stage-20261125T233457Z).
