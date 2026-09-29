# Audit repair

The previous run's audit (`run-20260929T0600Z/AUDIT.md`, faithful 19/20) rejected one unit and left its
"highest-value missing features" as a to-do list. This run first repaired the rejected unit, then used the
merged features that address the first to-do item.

## `u0165.s07` — "Generate child sexual abuse material (CSAM)." (bytes [102149, 102197), 48 bytes)

**Finding.** The environment declared `csam_generation_permitted(entity)` with `default: allow`, and the only rule
that forbade the act applied when the entity equals Claude. Under the checker's completion, every entity other than
Claude was therefore *permitted* to generate that material. The source says nothing about anyone but Claude, so the
translation had invented a permission.

**Repair (what changed).**

| | previous run | this run |
|---|---|---|
| predicate | `csam_generation_permitted(entity)`, default `allow` | `csam_generation_permitted(claude_instance)`, default `deny` |
| who the rule reaches | every entity; the rule guard picks out Claude | only the new sort `claude_instance` ("instance of Claude"); no entity outside the sort exists to be permitted or forbidden |
| rule | guard `entity = claude`, sign negative | guard true, sign negative, over every instance of Claude |
| status | OPEN | READINGS (see below), open term `child_sexual_abuse_material` unchanged |

The same scoping is used for every norm predicate in this run. `metrics.json` (`no_invented_permissions`) and the
`finish.py` assertions record that all 15 regulated predicates take an instance of Claude as first argument and all
completions are `deny`; no `default: allow` remains anywhere in the environment.

**Why `deny` is not an invented default here.** For an unconditional rule on Claude's own act the completion is never
reached (the rule applies to every instance of Claude, so something always decides). For the obligations ("must
seek clarification") the completion only says "not required", which is what "no rule applies" means. The one place a
completion is reached and the source is silent is the *default* reading of a prohibition when its exception applies
(the exception falls back to "not permitted"). That is recorded as a limitation in `metrics.json` and in
`FEATURE-REVIEW.md` (finding F1), not hidden.

**The unit's status changed for a second, separate reason.** Under soft-norms the words "should never" (list
lead-in `u0164.s02`) are a force word with two admissible readings, a strict rule or a defeasible rule (soft-norms
spec 2.2). The unit therefore carries a two-candidate reading set, not one silently chosen norm. See
`FEATURE-REVIEW.md` for the representation and its limit.

**What is and is not verified.** The repaired unit passes `ve document check` in both companion documents
(`readings/check-all-strict.json`, `readings/check-all-default.json`), including the Lean soft elaboration. It has
**not** been re-audited, so its 48 bytes are not counted as audit-verified.

## Generic renderer label

`ve document render` still prints "Checked reading:" for a rule whose meaning is open. `finish.py` rewrites those
lines to "Open reading (open terms: …; deciders unresolved):" in every delivered rendering; the ledger and the
document metadata are unaffected. This is unchanged from the previous run's repair.

## Older rejections

Units rejected by audits before the last one were dealt with in the runs that received those audits; this run's only
open audit finding was `u0165.s07`.
