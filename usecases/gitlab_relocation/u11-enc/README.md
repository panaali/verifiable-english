# Fresh encoder field for the U11 mail fix (row statute-latent-tour-gitlab-relocation-U11-mail)

The fix (translation R19: unit 11's "no change to compensation" NO also requires that the mail will not go to an address in
the place) reads "mail" on the comp sub-cases (cases.py need "comp": R012-2, R014-2, R015-2), which the frozen encoder
entered with chg only. The field comes from one fresh Opus 5.5 encoder seat (claude-opus-5-5, the picker's pick:
claude-panaali2, main allowed in the 11-27 window, decide1742 item 3), run in manage-agents tools-local/xfam-enc/sandbox.sh
(network only api.anthropic.com:443; the sandbox refuses a stage holding any sealed answer file or questions.jsonl, by name
or by content). The stage held only: prompt.txt (this directory), questions-enc.jsonl (539ee4c5..., the frozen encoder
file), units.jsonl (b12c5f4f..., the 34 units) and predicates.txt (9964045b..., the vocabulary, same file as r035-enc). The
seat saw no sealed directory, no questions.jsonl, no cases.py, no run or grade file and no answer: the replay is not void.

| pass | account | prompt | output | when (UTC) | transcript sha256 |
|---|---|---|---|---|---|
| one (USED) | claude-panaali2 | prompt.txt | enc.jsonl (e75c17da...) | 2026-11-26 18:02:59-18:03:34 | 83a97a7fd467531e... |

Result: 56 (case, place) lines, mail true 17 / false 39 / null 0. For every stay case (R001-R021) the seat's value equals
the place facts cases.py already carried (pf "mail", default false): R015 Spain true ("will have mail delivered to the
Spain address"), every other stay place false ("will have mail delivered only to Toronto" / "mail remain in Toronto").
cases.py comp_mail() asserts that agreement on the three comp sub-cases it enters (R012 Spain false, R014 Spain false,
R015 Spain true). The request cases (R022-R035, true) are not used: no comp question there.

Workdir: ~/xfam-enc-runs/u11mail-enc-20261126T180241Z (stage ~/xfam-enc-runs/u11mail-stage-20261126T180241Z).
