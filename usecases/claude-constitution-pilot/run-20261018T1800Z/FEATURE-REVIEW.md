# Feature review: what `ve-green-tarch-histdep` adds over `ve-green-fu-ar2-decoders`

Source: the pinned 184,893-byte constitution, unchanged (`../source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261017T1800Z` (`prev/`), whose audit found 28 of 28 units faithful.

| Merged (first-parent order, newest first) | What it is | Changes what a constitution unit can say? |
|---|---|---|
| infra/tarch-histdep, tarch-slowtail, fix/fsmonitor-gate, fu-docs-1017, dri-sign-1017b | test architecture, gate tooling, comments and DELTA text | No |
| infra/ties-fu-1017, ties-lf-16f, ties-jt-crossplan, ties-rights-licence-relay, ties-qs-1 | theorems tying existing definitions; no behaviour | No |
| readings-defaults/rd7 (rd-7) | the superposed `readings-verdicts` route: Lean assembles ALL/SOME/NONE over reading sets (certificate, one complete choice, countermodels); fewer prover searches | No: same verdicts, a different owner and cost. The 21 hard-constraint queries and both conclusion queries give identical answers |
| lean-first/b16f (lf-16f), b16g (lf-16g) | the `document` mode decides soft-norms, plain norm content, senses and fenced content in Lean; 16g stopped at its precondition | No |
| infra/me-1a | `VE.Numbers` core (decimal, rounding, comparison phrases) and the generated `ve/numbers_phrases.json`; DELTA says "Public output: none" | No: no service mode, command or profile reaches it. Graded quantities (119 UNFORMALISED units) stay blocked |
| foundation/qs-1 | `VE.Closure.Order` (an order closure with caps and theorems) | No: no service mode or relay |
| infra/fu-lf14c-f4, fu-rd9-checks, fix/jt-crossplan | n-ary defined predicates in the family view; relay checks; English head-word lint fixed point | No: the translation uses no definitions and its rendering is byte-identical |

Checked with `git diff ve-green-fu-ar2-decoders..HEAD --shortstat -- ve lean rust conformance` (see `metrics.json`, `language_changes_since_previous_tag`): the changed Lean and Python files are the document service, the readings route, the Numbers and Order modules, the English lint and generated tables and shapes. Result: **units upgraded by features: 0; reading sets upgraded by features: 0.**

## Measurements at this tag (all re-run)
* **Build**: `lean/.lake` copied from `ve-integration` at the identical commit; `lake build` rebuilt all 973 jobs (18 minutes) and finished; the Rust binary rebuilt by `tools/rust_build.py` (25 s) and equal to the pin in `lean/checkers.lock`.
* **Translation**: `nd.py all` rebuilds it, cmp-identical. `ve document check` passes (premises model, superposed route, 32 choices CONFLICT-FREE); `check.json`, `coverage.json` and `rendered-raw.md` are byte-identical to the previous run's; coverage 100% of bytes accounted, 51 open terms, 4 unresolved reading sets, 9 separations.
* **Probes**: unspecified, risk, s1, senses, senses_document, discourse, rights, frame and hard-conclusions probes are byte-identical to the previous run's; the companion probe differs only in the run directory inside its paths; the denial and claim-to-be-human queries are ALL as JSON objects (member order differs); the five `ve ask` questions give no answer as before (only `actions_version` 30, was 28).
* **Hard-constraint queries**: the same 12 ALL with certificates and 9 UNKNOWN, all answered on the first run at the default Rust limit, 54 minutes for the 21 (previous run about 60).
* **Soft chain** (`probe_soft_chain.py`): unchanged. Admitted, every pair separated, both conclusion queries ALL, but `ve document check` still raises `UnsupportedProfile`, so the three "should" sets keep their `exception_to_*` workaround.
* **Time** (one run each, load 5 to 8 at the start, not controlled): `ve document check` 63.5 s (was 51.5), coverage 72.9 s (64.7).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged). Gaps recorded in earlier runs stay: `other:english-nested-guard`, `other:scope`.
Next, in order of unlock: a scope construct (352 units, 29.9% of the text; would also give u0156.s03's frame a situation argument); the soft chain through `ve document check`; typed modals and belief; graded quantities once the Numbers core is reachable from a document; an English round trip for nested guards.
