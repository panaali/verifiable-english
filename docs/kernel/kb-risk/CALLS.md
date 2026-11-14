# kb-risk step 1: what the five frozen keys send on the `risk` route and which answer fields they read

Measured 2026-11-13 on `feature/kb-risk` at 0f6d59d441 (main), after `lake build`. Each harness ran once under
`zsh manage-agents/iso.sh <name> 16G --` with a throwaway tracer (`/tmp/kbrisk/trace_risk.py`, not committed, no
product code changed). The tracer wraps `ve.backends.lean_service.LeanServicePool.run_bound` (the relay entry
`ve.backends.relay.rows` and `decide` both end there; `LeanService.run_bound` was wrapped too and counted no
direct call), counts each `risk`-mode case by its `kind`, and hands the harness each answer as a dict/list
subclass that records every key, index, iteration and `len` read, with the first reader's stack.

```
PYTHONPATH=. zsh iso.sh kbrisk-trace-rsp 16G -- .venv/bin/python /tmp/kbrisk/trace_risk.py OUT usecases/anthropic-rsp/run.py --check
PYTHONPATH=. zsh iso.sh kbrisk-trace-pf  16G -- .venv/bin/python /tmp/kbrisk/trace_risk.py OUT usecases/openai-preparedness/run.py --check --base-only
PYTHONPATH=. zsh iso.sh kbrisk-trace-fsf 16G -- .venv/bin/python /tmp/kbrisk/trace_risk.py OUT usecases/safety-framework/run.py --check
PYTHONPATH=. zsh iso.sh kbrisk-trace-ap  16G -- .venv/bin/python /tmp/kbrisk/trace_risk.py OUT usecases/agent-policy/check.py base
PYTHONPATH=. zsh iso.sh kbrisk-trace-el  16G -- .venv/bin/python /tmp/kbrisk/trace_risk.py OUT usecases/eligibility/run.py --no-write
```

Every run exited 0 (`--check`: results.json unchanged): RSP 110 / 126, Preparedness 236 / 239, FSF 260/262,
agent-policy exit 0, eligibility exit 0 (mutants_killed 32/32).

## Calls by key and kind

| Key | `risk-elaborate` | `risk-decision` | other risk kinds | Sent from |
|---|---:|---:|---:|---|
| Anthropic RSP | 2 | 1 | 0 | `usecases/anthropic-rsp/stage0.py` `d2` (cached by `run.py` `severity`) |
| OpenAI Preparedness | 3 | 3 | 0 | `usecases/openai-preparedness/stage0.py` `risk_probe`, once per item S6, S7, S8 (`run.py` `severity_answer`) |
| DeepMind FSF | 1 | 1 | 0 | `usecases/safety-framework/severity_and_dates.py` `d2` |
| agent-policy | 0 | 0 | 0 | — |
| eligibility | 0 | 0 | 0 | — |

The same counts as the architect seat's trace (docs/kernel/frozen-keys-20261111.md: risk 3, 6, 2, 0, 0). No key
sends `admission`, `risk-conflict`, `risk-followable`, `risk-audit` or `risk-certificate` on this route.

## Fields read, one row per (key, kind, field)

"Keyed" says whether the field feeds a value compared with the answer key; "recorded" fields only go into the
harness's saved results. Read counts are the tracer's (each row read once per element).

| Key | Kind | Answer field read | Reads | Keyed? (items) | Harness use |
|---|---|---|---:|---|---|
| RSP | risk-elaborate | `status` | 2 | yes: all S items (`admitted`) | `stage0.d2`: an error row makes `admitted` false |
| RSP | risk-elaborate | `environment_id`, `document_hash` | 2, 1 | indirectly (the decision record cites them; the decision case fails if they are wrong) | the decision record's policy pair |
| RSP | risk-elaborate | `risk_premises[].label`, `risk_premises[].ast[2][1]`, `ast[3][1]` | 8 rows | yes: S1-T1..S1-T4, S5 | `classes`: rows labelled `risk:class`, harm `ast[2][1]`, class `ast[3][1]` |
| RSP | risk-elaborate | `error` (the T4 probe case, a refusal row) | 1 | no (recorded as `with_unclassified_t4_harm`) | — |
| RSP | risk-decision | `status` | 1 | yes: all S items (`admitted`) | — |
| RSP | risk-decision | `tables.might[].alternative`, `.harm` | 16 | yes: S3 | `stated_cells[].might` |
| RSP | risk-decision | `tables.leads[].alternative`, `.harm` (empty list iterated) | 1 | yes: S4 | `stated_cells[].leads` |
| Preparedness | risk-elaborate | `status` | 6 | yes: S6, S7, S8 (`admitted`) | — |
| Preparedness | risk-elaborate | `environment_id`, `document_hash` | 3, 3 | indirectly (decision record) | — |
| Preparedness | risk-elaborate | `risk_premises[].label`, `.ast[2][1]` | 90 rows | no (`classes`, recorded) | — |
| Preparedness | risk-decision | `status` | 3 | yes: S6, S7, S8 (`admitted`) | — |
| Preparedness | risk-decision | `tables.might[].alternative`, `.harm` | 75 | yes: S7 (`bio_h_might`) | — |
| Preparedness | risk-decision | `tables.leads[]` (empty) | 3 | yes: S8 (`invented_leads`) | — |
| FSF | risk-elaborate | `status` | 1 | yes: S1-*, S2, S3, S5, S6 (a refusal stops the run) | — |
| FSF | risk-elaborate | `environment_id`, `document_hash` | 2, 2 | indirectly (decision record); recorded | — |
| FSF | risk-elaborate | `risk_premises[].label`, `.ast[0]`, `.ast[2][1]`, `.ast[3][1]` | 46 rows | yes: S1-* (`risk:class`), S2 and S3 (`risk:order` rows whose ast is `binary`), S5 (class) | `classes`, `order` |
| FSF | risk-elaborate | `unranked_severities` | 1 | no (recorded `unranked`) | — |
| FSF | risk-decision | `status` | 1 | yes (a refusal stops the run) | — |
| FSF | risk-decision | `tables.might[].alternative`, `.harm` | 72 | yes: S5 | `stated_cells[].might` |
| FSF | risk-decision | `tables.leads[]` (empty) | 1 | yes: S6 | `stated_cells[].leads` |
| FSF | risk-decision | `decision_record_id`, `conditional_on`, `lines.unexamined_possible` (length) | 1 each | no (recorded) | `d2` result |

RSP S2 reads only `admitted` and answers `undecided` (no severity order between the T1 and T2 harms); it has no
risk-route value. Preparedness S6's value is the request's own `more_severe` order (an input, not an answer
field) once both calls are `ok`. FSF S4 is not on the risk route (`s4`, a route refutation).

## What step 2 must state

- `risk-elaborate`: `status` (`ok`), `environment_id`, `document_hash`, `risk_premises` (its `risk:class` and
  `risk:order` rows), `unranked_severities`.
- `risk-decision`: `status` (`ok`), the verdict branch (CONFLICT or the tables), `tables.might`, `tables.leads`
  (each row's `alternative` and `harm`), and the recorded `environment_id`, `document_hash`,
  `decision_record_id`, `conditional_on`, `lines.unexamined_possible`.
- The `error` row RSP records is a refusal (`runCase j = .error _`); an `.ok`-hypothesis theorem asserts nothing
  about it, and no keyed value reads it.
- Kinds no key calls on this route: `risk-conflict`, `risk-followable`, `risk-audit`, `risk-certificate`
  (listed `uncovered`); `admission` already has `risk_wire_acceptance`.
