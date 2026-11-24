# Free in-patient stays, re-encoded (row statute-xfam-wrong-pawhp-1)

Two fresh Opus 5.5 encoder sessions (claude-opus-5-5, account claude-danielsaeedi37: the picker's pick), 2026-11-24
00:05:57-00:06:30Z, each in tools-local/xfam-enc/sandbox.sh (manage-agents; network only api.anthropic.com:443; the
sandbox refuses a stage holding any sealed answer file or questions.jsonl). Each stage held only: the prompt (same text
for both), its own set's questions-enc.jsonl, ssi-2024-351.txt and uksi-2005-3360-reg2.txt. Neither saw a sealed
directory, a questions.jsonl, the other set, the frozen cases files or any answer.

| set | questions-enc.jsonl sha256 | output | transcript sha256 |
|---|---|---|---|
| same-family | 0913f3b9845172ad... | stays-same.jsonl | 54e4a9afea3ee968... |
| cross-family | b40ded55b1ee2b93... | stays-xfam.jsonl | 09cadbe994d35f15... |

Workdirs: /home/seyran/xfam-enc-runs/fipt-enc-{same,xfam}-20261124T000529Z (stages fipt-stage-{same,xfam}-20261124T000529Z).

Only the stays with "free_in_patient": true are encoded (cases.py / xfam/cases_xfam.py field "fipt": [entered, left|None]):
same-family P027 [2025-09-21, 2026-10-15], P028 [2025-09-22, 2026-10-30]; cross-family P019 [2025-09-21, 2026-09-27],
P020 [2025-09-22, None]. These are exactly the four cases whose frozen records stated fipt_52w_before. The other stays
the seats listed (care homes, independent hospitals, a s.57 private patient) are not free in-patient treatment and were
already encoded through other facts; nothing else changed.
