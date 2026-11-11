# The frozen keys before any kernel-boundary change (2026-11-11)

Measured by the architect seat on main `97b3c7999a` in the worktree `ve-fable-arch-1`, on the shared VM at
a load of 60 to 110 on 32 vCPU (so the wall times are upper bounds, not benchmarks). Each harness was run
once through `tools/kernel_trace.py`, which records every Lean service call by mode and case kind and
changes no product code. Every run ended with exit code 0 and left the working tree unchanged. These are
the "before" figures of every row in [the kernel boundary](../spec/kernel-boundary.md), section 7.

```
.venv/bin/python tools/kernel_trace.py OUT.json usecases/anthropic-rsp/run.py --check
.venv/bin/python tools/kernel_trace.py OUT.json usecases/openai-preparedness/run.py --check --base-only
.venv/bin/python tools/kernel_trace.py OUT.json usecases/safety-framework/run.py --check
.venv/bin/python tools/kernel_trace.py OUT.json usecases/agent-policy/check.py base
.venv/bin/python tools/kernel_trace.py OUT.json usecases/eligibility/run.py --no-write --no-mutants
```

## Answers and time

| Key | Answers on main (measured) | After the fidelity audit (sourced) | Wall time |
|---|---:|---:|---:|
| Anthropic RSP | 111 / 126 | 77 / 126 (`manage-agents/reviews/uc-audit-rsppf-20261111.md`) | 537.5 s |
| OpenAI Preparedness | 231 / 239 | 68 / 239 (same) | 198.8 s |
| DeepMind FSF | 257 / 262 | 185 / 262 (`manage-agents/reviews/uc-audit2-20261028.md`) | 405.2 s |
| agent-policy | 42 / 42 (M1 and M2) | not audited | 813.2 s |
| eligibility | 269 / 269 | not audited | 1,049 s |

## Lean service calls, by mode and case kind

| Mode, kind | RSP | Preparedness | FSF | agent-policy | eligibility | Path status (section 1.2 of the specification) |
|---|---:|---:|---:|---:|---:|---|
| `route`, certificate | 5,918 | 2,842 | 3,980 | 6 | 0 | kernel: proved from the wire |
| `route`, dependency-order / background | 2,023 | 1,178 | 728 | 87 | 1 | kernel path, non-verdict kinds |
| `norms`, norms-conflict | 0 | 0 | 0 | 1 | 0 | kernel: proved from the wire |
| `soft-norms`, soft-elaborate | 182 | 206 | 154 | 0 | 0 | kernel path, a kind no theorem covers (registry `uncovered`): outside the kernel; its `soft_status` is `CHECKED` or `OPEN` (`residualStatus`) |
| `metered`, evaluate-budgeted | 6,384 | 1,272 | 9,120 | 8,169 | 0 | **candidate: proved core 519 lines, 3,761 lines of wire code under no theorem** |
| `quantity` (certificate, document, countermodel, plain) | 25 | 20 | 4 | 0 | 9,403 | **candidate: proved core 613 lines, 1,804 lines of wire code under no theorem** |
| `risk` (risk-decision, risk-elaborate) | 3 | 6 | 2 | 0 | 0 | candidate: spec 6,159, wrap 5,669 |
| `check` | 18,448 | 8,722 | 12,337 | 688 | 4,916 | validator, no theorem (3,461 lines run) |
| `model` | 26 | 12 | 427 | 453 | 0 | validator, no theorem (7,195 lines run) |
| `environment` | 14 | 12 | 14 | 86 | 2 | validator, no theorem (5,912 lines run) |
| `english.read` | 11 | 19 | 16 | 1 | 89 | reader of the rule text (shell) |

What the table shows:

1. The five keys call 9 of the service's 43 modes. None calls the `document`, `readingsRoute` or
   `discourse` mode, whose code is 35,142, 20,356 and 35,782 lines: the largest wrappers carry no keyed
   answer.
2. All Lean code under the keys' answers is **16,607 distinct lines** (spec and wrap of the ten paths
   above, the three validators counted in full; the registry's `keys`, measured by `tools/kernel_closure.py`
   as `keyed_lines`). The proved kernel is 8,732 of them. (The first measurement, 17,355 and 9,565, also
   counted the `checkCertificate` path, which no key calls and which is now a candidate; the second,
   16,831 and 8,956, also read the route's `bundle` and `admission` runners, which no theorem covers,
   through `runCase_dispatch`.)
3. The gap between the two is wire code around a proved core: `metered` (every "no" answer and every
   countermodel: 24,945 calls across the keys), `quantity` (eligibility's 9,403 calls), `risk`, and the
   three validators. Rows `kb-7` (metered) and `kb-8` (quantity) close the first two.
4. In every harness the Python side holds the premises between `soft-elaborate` and `route certificate`:
   the harness is the shell and already works by the carry rule (elaborate, then let the kernel replay a
   certificate over the premises shown). The audit's losses (RSP 111 to 77, Preparedness 231 to 68) are
   in what the rules say, which no path above can see.
