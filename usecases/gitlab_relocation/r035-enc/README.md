# Fresh encoder fields for the R035 fix (row statute-corpus-gitlab-relocation-wrong-r035)

The fix (translation R17 / condition (i), encode.py E5) reads two fields the frozen encoder (1847cd06dc) never entered: the
written VP/PBP pre-approval of a relocation request ("wpre") and the stated facts with no predicate ("nopred"). They come
from fresh Opus 5.5 encoder seats (claude-opus-5-5, the picker's pick each time), each run in manage-agents
tools-local/xfam-enc/sandbox.sh (network only api.anthropic.com:443; the sandbox refuses a stage holding any sealed answer
file or questions.jsonl, by name or by content). Each stage held only: the prompt, questions-enc.jsonl (sha256 539ee4c5...,
the frozen encoder file), units.jsonl (the 34 units) and predicates.txt (the fix's vocabulary, generated from translation.py;
9964045b... in every stage). No seat saw a sealed directory, questions.jsonl, the frozen cases.py, a run or grade file, or
any answer: no re-run is void.

| pass | account | prompt | output | when (UTC) | transcript sha256 |
|---|---|---|---|---|---|
| first (superseded) | claude-saeedi-danial | prompt-first-pass.txt | enc-first-pass.jsonl | 2026-11-25 20:31:45-20:33:18 | 4436438d0fb74b1e... |
| second (superseded) | claude-saeedi-danial | prompt-second-pass.txt | enc-second-pass.jsonl (b05b2a14...) | 20:34:12-20:36:16 | 0dad3cf56027bf51... |
| third (USED) | claude-panaali2 | prompt.txt | enc.jsonl (ccc8a87a...) | 22:13:32-22:16:19 | 5ee371ccb708c62c... |

Why three passes. The first asked only for each no-predicate fact's unit; at unit level its facts would have refused
answers whose unit merely mentions the fact's subject (every acceptance answer, through "takes a company-owned laptop" on
unit 16, whose embargo list condition (c) reads), so a second pass added "turns_on". The second pass's flag on R016
("Pia never asked about France or Belgium.", unit 7, citing a "could result in" clause) refused six correct answers; the
fix's review found none of the six refusals required by the text (the fact is the existing predicate mgr = false, the
cited clause states no outcome, and the fact was applied to every stay). After the review E5 was narrowed (encode.py E5:
item scope, written clauses only, the answer must not still follow without the rules) and a third fresh seat encoded both
fields with a stricter prompt: rule out every predicate first (including a negated one), name the item, cite the clause,
and turns_on only for a clause that states an outcome. Only the third pass is used.

wpre: all three passes agree (R022-R034 true, R035 false, R001-R021 no request). The third says "several" for R025 (three
alternative requests: China, Ethiopia, Belarus) with "this sentence applies to each of them, so wpre is true for each
request"; cases.py enters wpre true on each R025 request sub-case on exactly that statement (asserted).

Third pass, nopred with turns_on true: unit 6 "has not contacted the People Operations Team" (and the same with "has not
obtained Trade Compliance Counsel approval or ..."; clause "contact the People Operations Team immediately"), unit 3 "...
discussed the move with the manager" (clause "Discuss the proposed move with your manager and seek business approval before
submitting a formal relocation request"): both clauses are ones the translation does not write (duties with no outcome,
the ledger's other:norm), so E5 reports them (run file, sub "e5": "unwritten") and refuses nothing. Unit 8 "travels as a
digital nomad" (R011-R014) and unit 34 "a voluntary change of permanent residency" (request cases) cite written clauses,
but no question of those cases reads those clauses' names (mx, rem, pl; spons): no answer changes.

Workdirs: ~/xfam-enc-runs/r035-enc-20261125T203106Z, r035-enc2-20261125T203355Z, r035-enc3-20261125T221303Z (stages
r035-stage-20261125T203106Z, r035-stage2-20261125T203355Z, r035-stage3-20261125T221303Z).
