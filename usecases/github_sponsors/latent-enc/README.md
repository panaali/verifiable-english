# Fresh encoder field for the latent fix U8 (row statute-latent-github-sponsors-developer-U8)

The fix (translation._ban: each ban of units 9-15 needs "rf", the act allows payments or raises funds) reads a fact the
frozen encoder (60d692157a) never entered. It comes from ONE fresh Opus 5.5 encoder seat (claude-opus-5-5, account
claude-danielsaeedi37, the picker's pick), run in manage-agents tools-local/xfam-enc/sandbox.sh (network only
api.anthropic.com:443; the sandbox refuses a stage holding any sealed answer file or questions.jsonl, by name or by
content). The stage held only: prompt.txt, questions-enc.jsonl (sha256 b690d65b..., the frozen encoder file), units.jsonl
(833af075..., the 45 units) and predicates.txt (133c01af9dc6e338..., the act vocabulary generated from translation.py). The seat
saw no sealed directory, questions.jsonl, cases.py, run or grade file, or any answer: the re-run is not void.

| pass | account | prompt | output | when (UTC) | transcript sha256 |
|---|---|---|---|---|---|
| one (USED) | claude-danielsaeedi37 | prompt.txt | enc.jsonl (21ea460fd2fd1f34...) | 2026-11-25 23:58:07-23:58:46 | 9c03add40ba3111a... |

Result: every act of S005, S006, S007 and S008 (the only cases with act items in cases.py) has rf true, quoting the
question's "raise funds for ..." (S005-3: "soliciting funds for a library"; S008: "raising funds for / by ..."); no act
rf false or null among them. cases.py enters "rf" on exactly those twelve acts. The seat also listed acts in S001, S020,
S021 and S035 (offers, a laptop purchase, a monetization feature): none of them is an act item of cases.py (their
questions use other forms), so nothing is entered for them.

Workdir: ~/xfam-enc-runs/latent-sponsors-enc-20261125T235806Z (stage latent-sponsors-stage-20261125T235747Z).
