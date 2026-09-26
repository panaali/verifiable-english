# `ve-document@1` statement review

This is W2's document wrapper over the frozen P0 route. The wrapper does not
change a formula's meaning, its canonical bytes, or the checker. The prose
source is all UTF-8 bytes after JSON front matter except `ve` fences. Unit
spans use byte offsets into that source, in source order, and must partition
it exactly. This is a stronger mechanical rule than ignoring punctuation or
whitespace: they are accounted for too. A unit can be explicitly
`unformalised(reason)`; it cannot disappear.

~~~~text
---
{"format":"ve-document@1","environment":{...},"units":[...]}
---
Original prose, including spaces and punctuation.
```ve unit_id
One English VE sentence.
```
~~~~

Each unit has `id`, `span`, recursive `kind`, `meaning`, `support`, and optional
`content`. Kinds use exactly the P0 admission encoding: strings for atomic
kinds; lists for `attributed`, `hedged`, `causal`, and `unformalised`. Meaning is
`specified`, `{"contextual":"name"}`, `{"open":["term"]}`, or
`{"unformalised":"reason"}`. Support is `assumption`, `certificate`,
`observation`, `calculation`, `statistical`, `testimony`, `adapter`, or `none`.
These fields are independent: a question with no formula is still a unit.
`content` is `{"ast":[...]}` for an existing formula or
`{"fence":"unit_id"}` with `surface` set to `english` or `strict`. An English
fence goes through the existing all-derivations parser. The optional
`meaning_id` must match the environment-bound formula identity.

An open term declares `name`, `arguments`, `decided_by`, `necessary`,
`sufficient`, `factors`, `precedents`, `jurisdiction`, and `version`. Conditions
are existing closed VE formulas; precedents are pinned meaning IDs. An open
term is counted in the residual even if the surrounding logic is exact.
Decision criteria are not invented by the checker.

A reading set records its source `unit`, stable `id`, `version`, `status`, and
candidate readings. Each candidate has a kind, meaning ID, content if already
elaborated, and admission (`who`, `why`, distinguishing model IDs). An `authored`
set has one signed live reading and may retain rejected history. An `open` set
keeps all candidates. Narrowings cite a set and version, keep named readings,
and cite source units for their reason. They never modify the set. Weights are
separate removable intent annotations and are ignored by all checks.

For assertion readings in one environment, `ve document readings --conclusion`
uses fixed assertions and the latest reading-set version for each source unit.
Authored singleton choices are premises too. It first proves ALL from fixed
assertions and one conjunction of per-unit disjunctions, with
certificate replay. It proves NONE with one checked finite model that satisfies
every reading and fixed assertion and refutes the conclusion. SOME needs a named choice proof and
a checked model for another choice. Search exhaustion is UNKNOWN. Other kinds
are planned as complete choices up to 64; until their W1/W3 elaborators land,
the verdict is UNKNOWN. The reading set is only the readings considered so far,
not a claim that every plausible source interpretation has been found.

If a claim graph is present, `ve document check` sends the compiled unit kinds,
content, labels, background, citations and graph to P0 `admit_document`.
Unsupported non-assertion readings cannot enter that P0 route. Quoted content
needs an explicit bridge leaf there. The wrapper report identity binds the full
source document and preserves the P0 identity as `core_report_id`. A check also reports the
premise set's model, inconsistency certificate, or UNKNOWN, with vacuity
visible for dependent proof reports. Coverage reports source bytes by kind,
reason codes, and the residual: open terms, assumptions, bridge leaves, and
unresolved reading sets. Coverage percentage is exactly 100 only after the
partition has passed validation.

## Lean statement for review

`VE.Route.readings_all_iff`: for one fixed structure and one fixed background,
satisfying the disjunction of each assertion reading set is equivalent to
being able to choose one reading from each set so that all chosen readings
hold in that same structure. This justifies the ALL proof input. It does not
justify using the shortcut for norms, definitions, or readings with different
backgrounds.

## Authoring status

Document kinds, open terms, and reading-set metadata are **strict only** in
this baseline. W8 owns `ve assist` hooks `add_unit`, `add_reading`, and `narrow`
plus fidelity gates before any is offered as zero-training English authoring.
The existing English formula fence remains writable today and is checked for
one derivation. The three source pilots, second-rater kind agreement, and blind
rendering fidelity measurements remain W2 acceptance gates. They are pending
under the dated scope amendment in `PLAN-EXPAND2.md`; this code checkpoint
claims no pilot coverage or fidelity number. W8 still owns the authoring workflow.
