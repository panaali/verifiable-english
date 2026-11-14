# kb-8b: the `quantity` case kinds the five frozen keys send, and the fields they read

Measured on main `9a3fd7a9f9` (branch `infra/kb-8b`, no product change), 2026-11-13. Each harness ran once,
in parallel, each in its own scope (`zsh manage-agents/iso.sh kb8b-<key> 16G -- .venv/bin/python <command>`), with
a throwaway recorder on `PYTHONPATH` (`/tmp/kb8b/site/sitecustomize.py`, not committed). The recorder wraps
`ve.backends.lean_service.LeanService._run_chunk`, the one function every case goes through
(`LeanService.run_bound` and `LeanServicePool.run_bound`, hence `relay.rows`, `relay.decide`, `relay.answer` and
`relay.decide_once`, all send each chunk through it), logs every case of mode `quantity` with its `kind` and `id`,
and hands back each answer row as a dict that logs every field read with the frame that reads it. A
`sitecustomize` covers the harnesses' `forkserver` worker processes too; the one-shot runner
(`ve.backends.lean.run`) was wrapped as well and saw no `quantity` call. Raw figures:
[calls.json](calls.json).

| Key | Command | Exit | Answers |
|---|---|---:|---|
| eligibility | `usecases/eligibility/run.py --no-write` | 0 | `mutants_killed` 32/32, `open` [] |
| Anthropic RSP | `usecases/anthropic-rsp/run.py --check` | 0 | 110 / 126 |
| OpenAI Preparedness | `usecases/openai-preparedness/run.py --check` | 0 | 236 / 239 |
| DeepMind FSF | `usecases/safety-framework/run.py --check` | 0 | 260/262 |
| agent policy | `usecases/agent-policy/check.py base` | 0 | no `quantity` call |

The five `results.json` files (and the three others under `usecases/*/`) had the same SHA-256 after the runs as
before (`sha256sum -c` printed no mismatch) and `git status` was clean.

## One row per (key, kind)

"Fields read" are the answer fields read after the relay returned the row; the reading frame is in
[calls.json](calls.json). `status` is read by `ve/backends/relay.py` `decided` (a rejection row raises) in the
`decide` callers and by the harness itself in eligibility, which uses `relay.rows`.

| Key | Kind (case `kind`) | Calls | Fields read (by) | Theorem that states the answer |
|---|---|---:|---|---|
| eligibility | admission (no `kind` field) | 6,781 (6,780 ok, 1 rejection: probe `P1`) | `id` (run.py `lean`, `main`, `lean_admits`); `status`, `value` (run.py:468-471, `model_premises_true` and `model_premises_not_true`); `error` (run.py:521 `lean_admits`, the rejection row of probe P1 only) | `VE.Time.Wire.quantity_admission_wire_sound` |
| eligibility | certificate | 2,353 | `id`; `status`, `valid` (run.py:464 `certificates_accepted`; run.py:489 `b1_certified`) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| eligibility | document | 269 | `id`; `status`, `assurance` (run.py:465 `documents`, which decide whether an answer counts or is OPEN) | `VE.Time.Wire.quantity_document_wire_sound` |
| Anthropic RSP | certificate | 26 | `status` (relay); `valid` (ve/units.py:422 `check_quantity_certificate`) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| OpenAI Preparedness | certificate | 30 | `status` (relay); `valid` (ve/units.py:422) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| DeepMind FSF | certificate | 3 | `status` (relay); `valid` (ve/units.py:422) | `VE.Time.Wire.quantity_certificate_wire_sound` |
| DeepMind FSF | countermodel | 1 | `status` (relay); `refutes` (ve/units.py:431 `quantity_countermodel`) | `VE.Time.Wire.quantity_countermodel_wire_sound` |
| agent policy | (none) | 0 | | |

No key sent `count` (registry: `nonverdict`, `VE.Time.Wire.runCount`) or a conversion kind `day`, `civil`, `lower`
or `render` (`nonverdict`, `VE.Time.Wire.runConversion`). So no key reads a keyed value from a `nonverdict` or
uncovered kind: condition (c) of the task does not hold.

The one rejection row read (eligibility probe `P1`, an admission refused with `DateRange(1960-06-27)`, as the
probe expects) is the `runCaseReported` error branch; the four theorems state `.ok` answers only, and a refusal
carries no verdict. The probe's text goes into `results.json` `probes`, not into the 269 keyed answers.

## The promotion was measured, and not made

With `quantity` set to tier `kernel` and a `kinds` table (admission, countermodel, certificate, document to their
theorems; count, day, civil, lower, render nonverdict), `VE_NATIVE_PREBUILT=1 .venv/bin/python
tools/kernel_closure.py` printed ([promotion-attempt.txt](promotion-attempt.txt)):

```
quantity      kernel             5    2267      75    2274  quantity
kernel (distinct lines of every path of tier kernel): 10673
under the frozen keys' answers: 16198, of them in the kernel: 10673
problem: quantity: a statement leaves answer fields open (state them by key): VE.Time.Wire.quantity_admission_wire_sound
```

The rise, 9,552 to 10,673 (+1,121), is within the signed +1,300, but the tool exits 1 on the problem line, so
the kernel check could not pass against a baseline regenerated with the promotion. The statement
(lean/VE/Time/WireSound.lean:41-56) quantifies `∃ … (value : List (String × Json))` and states
`answer = ok id ([…seven fields…] ++ value)`; it then fixes `value` to `[]` or to
`[("value", .bool b), ("evaluations", toJson work)]`, but the Lean half's `hasOpenFields`
(tools/kernel_closure.lean:154) flags every existential over a field list (rule KB-7 F1), and kb-8's path was a
candidate, where the rule is not applied. Closing it needs the admission statement written with the answer
fields by key (or as two closed answers), which is a Lean change this item may not make. The registry,
`closure-baseline.json`, `ALLOWANCES.md` and `frozen-keys-20261111.md` are therefore unchanged.
