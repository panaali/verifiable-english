# Feature review: what `ve-green-lf-16c` adds over `ve-green-rd-3`

Source: the pinned 184,893-byte constitution, unchanged (`source/SOURCE.md`, SHA-256 `fa10ed48…50dd`). Start: the translation of run `20261009T1800Z` (`prev/`). One first-parent merge since `ve-green-rd-3`.

| Merged | What it is | Changes what a document can say? |
|---|---|---|
| `lean-first/b16c` (lf-16c) | Lean's document mode reads the `ve-document@1` JSON boundary itself: `null` where Python reads it as absent, number forms and lone surrogates refused or failed closed, response units and narrowings typed. The batch says it is incomplete: Lean decides 4 of 412 pilot inputs (norm-defaults, rights, soft norms, senses and norm content are still Python-side) | No |

Result: **no unit changes status because of a feature, and no unit is newly expressible.** The four status changes of this run (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03: READINGS -> OPEN) are audit repairs, and claimed coverage does not move.

## What the measurement shows
* **Same verdicts.** `ve document check` of the unchanged previous translation at lf-16c (`check-baseline.json`): premises `model`, enumerated plan, 32 choices, conflict-free, as at rd-3. It took 148 s here (83 s last run on another machine load; not a language property).
* **Translation after repair:** admitted, 16 choices (four sets), conflict-free, premises `model`; the denial query gives the same answers as before; the claim-to-be-human query is now ALL.
* **Lean-decided share stays 0.00%.** lf-16c reports its own share per corpus (`docs/lean-first/b16c/DELTA.md`: pilots 4/412 inputs), and the constitution's norm-defaults content is a listed residue; no route or CLI output reports `decided_units` for a document.
* **Probes:** the seven carried probes re-run; six are byte-identical to the previous run's JSON. The discourse probe differs in one refusal sentence (`UnsupportedProfile: Unsupported profile norm-defaults@0` where it read `unknown document metadata`); verdicts equal. The rights probe no longer shows last run's KeyError in its recorded diagnostics.

## Costs and limits (unchanged)
* A defeasible rule beside norm-defaults@0 is still refused (probe c); the defeasible candidates are the strict rule with an `unless` over an open term the translator names (four `exception_to_*` terms).
* `ve document` still refuses a reading with `companion` (RD-4b is not merged).
* Open terms 34 -> 33 (the wide-scope term is gone).

## Missing features, ledger tally (`UNFORMALISED`)
norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50, counting 31, modality/belief 25, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1 (unchanged).
Next, in order of unlock: reporting decided units; typed modals and authority ("cannot", "can", "may", "unlocked by": ability, permission or authority); graded quantities ("serious uplift", "vast majority"); context-sensitive defeasible obligations beside norm-defaults@0.
