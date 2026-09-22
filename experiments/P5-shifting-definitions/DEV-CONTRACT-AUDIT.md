# Superseded dev contract audit — 2026-09-22

All **15 dev completions**, costing **$0.1476830522**, are retained in
`runs/study/costs.jsonl`. Only **8/96 final judgments** ran: four per judge.
The reported compliance rates are 2/48 = 0.041667 (pro) and 4/48 = 0.083333
(replication), not the fraction of observed responses that were malformed.
Observed legacy compliance was **2/4 pro, 4/4 replication**. There are
**88 missing judgments**, not 88 contract-violating model responses.
No X call and no VE final judgment ran.

## Counts (overlapping causes)

| Cause/check | Count | Interpretation |
| --- | ---: | --- |
| MAX_TOKENS | 6/15 | VE author/repair/critic/defender 4; S author 1; pro lone 1 |
| Invalid final-judgment JSON | 1/8 | Same truncated pro lone response |
| Rule ID in locations | 1/8 | pro lone `i206…`: `["n02","r02"]` |
| Wire-schema / legacy-validator domain mismatch | 8 requests; 1 observed rejection | Schema accepts strings; legacy parser additionally requires node membership |
| Invalid verdict vocabulary | 0/7 complete judge JSON objects | Two `unknown` verdicts are explicitly allowed |
| Invalid issue-type vocabulary | 0/7 | A wrong but allowed diagnosis is a scoring error |
| Extra/missing fields | 0/7 | All complete judge JSON has exactly four required fields |
| Location type/count/duplicate violations | 0/7 | The one location error is membership only |
| Empty/nonstring explanation | 0/7 | Complete explanations have 158–589 characters |
| Explanation length violation | 0 | There is no maximum explanation length in the contract |
| Judge structured schema absent | 0/8 | Vertex 4/4; OpenRouter `json_schema` 4/4 |
| Nonjudge VE formal schema absent | 4/4 | These roles requested JSON in prose; they did not use the verdict schema |
| Billed output exceeds cap | 1/15 | VE defender 1,095 > 1,024; primary-panel halt |

Vertex HTTP requests were not independently dumped. Its schema-attachment
finding uses each retained request, the unchanged provider wire builder,
and the provider's parsed JSON in complete responses. OpenRouter additionally
records `_p1_response_format=json_schema` for all four judgments. New offline
transport tests capture the actual `generate_content` config and HTTP JSON.

## Each completion

IDs below abbreviate the packet hash; full request identity, response digest,
JSON error, finish reason, schema evidence and token counts are recorded in
`checks/dev-contract-audit.json`. V/T means visible/thinking tokens.

| Packet | Arm/model/stage | Finish | V/T | Legacy contract / diagnosis |
| --- | --- | --- | --- | --- |
| ie1d380… | L/pro/lone | STOP | 125/805 | Pass |
| ie1d380… | L/replication/lone | stop | 147/0 | Pass; allowed unknown |
| i206f6b… | L/pro/lone | STOP | 90/536 | Fail: r02 is a record ID in locations |
| i206f6b… | L/replication/lone | stop | 161/0 | Pass; allowed unknown |
| ia16a76… | L/pro/lone | MAX_TOKENS | 31/979 | Fail: unterminated explanation string |
| ia16a76… | L/replication/lone | stop | 134/0 | Pass; correctness remains scored |
| i0e03b7… | S/pro/author | MAX_TOKENS | 333/687 | Truncated table; verdict contract inapplicable |
| i0e03b7… | S/pro/critic | STOP | 76/191 | Free-text audit; verdict contract inapplicable |
| i0e03b7… | S/pro/defender | STOP | 91/222 | Free-text audit; verdict contract inapplicable |
| i0e03b7… | S/pro/judge | STOP | 119/223 | Pass |
| i0e03b7… | S/replication/judge | stop | 123/0 | Pass; allowed but wrong issue type stays scored |
| ia16a76… | VE/pro/author | MAX_TOKENS | 41/979 | Fenced, incomplete formal JSON |
| ia16a76… | VE/pro/repair | MAX_TOKENS | 167/853 | Fenced, incomplete formal JSON |
| ia16a76… | VE/pro/critic | MAX_TOKENS | 316/704 | Fenced, incomplete formal JSON |
| ia16a76… | VE/pro/defender | MAX_TOKENS | 40/1,055 | Fenced/incomplete; 1,095 billed tokens halt panel |

VE prefixes also use a string for `environment`, where the oracle needs an
object, and some claim sources contain ordinary prose. These model-authored
formalisation problems are not repaired from gold or counted as judge-contract
failures. Removing a code fence would not repair the truncated artifacts.
Increasing the cap does not guarantee successful formalisation.

## Harness amendment and rerun

See the dated v9 entry in `AMENDMENTS.md`. No outcomes are rescued or re-scored
as new dev results. Historical trials and analysis remain under `runs/dev/`;
its original gate remains in `checks/dev-superseded-v8.json`. New requests use
`study-v9/` identities and `runs/dev-v9/`, so old successes and failures cannot
be silently reused. Costs count toward the same study and item/arm ceilings.
Only the specifically evidenced old 1,095/1,024 halt is acknowledged; a new
4,096-token overrun remains a halt. The unused old block reservation is released,
without refunding any call or labelling the incomplete block completed.

Offline audit and checks:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run --offline python -m experiments.p5_contract
uv run --offline pytest -q tests/test_p5*.py tests/test_p1*.py
uv run --offline python experiments/P5-shifting-definitions/run_p5.py inventory
uv run --offline python experiments/P5-shifting-definitions/run_p5.py freeze --scenario dual_judge
uv run --offline python experiments/P5-shifting-definitions/run_p5.py preflight --offline
uv run --offline python experiments/P5-shifting-definitions/run_p5.py probe --offline
```

The amended worst-case schedule is **$69.8036611616**, before the historical
costs/envelopes not included in that schedule. Maximum combined VE item/arm
reservation is **$0.3753408992**. The unchanged **$40 / $0.16** limits therefore
block dispatch. These are reservation bounds, not estimated actual spending.
Changed configs also require genuine billing calibration and free native token
counts; old receipts are not transferred to changed configs. A new external
timestamp is required after the final executable freeze. Historical timestamp
receipts remain under `checks/pre-v9/`. No paid calibration is authorized here.

After a separately approved resolution of these prerequisites and explicit
paid dev authorization, the rerun command is:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run --offline python experiments/P5-shifting-definitions/run_p5.py dev --cap-usd 40
```

This command currently fails closed on the budget gate. `uv --offline` controls
package installation; the `dev` command itself makes paid provider calls.
This repair session made **zero generation calls and spent $0**.

## Offline validation

The final P5 plus shared P1 harness regression selection passed **232 tests**.
The broader P5/P1 run passed 305 tests and failed two pre-existing historical
P1 ledger assertions (`test_p1_amendment13::test_scored_gate_and_cap_reach_only_qwen_attacker_backends`
and `test_p1_amendment14::test_recover_and_reconstruct_every_retained_scored_call_without_dispatch`).
Both failures reproduce using unmodified HEAD versions of `p1.py` and `paid.py`
against the same retained P1 data: later amendment-15 ledger entries invalidate
the older block/spending expectations. No P1 data or those tests were changed.

All material, review, scoring-fixture, Lean replay, packet safety, role-boundary
and leakage checks are rerun offline. Six of twelve current Gemini configs have
matching old calibrations; the other six remain blocked. The existing provider
smokes are replayed from billing evidence without generation. No test, restored
smoke or local timestamp is used to waive an outstanding execution gate.
