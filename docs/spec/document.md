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
Apart from the root reason rule, these fields are independent: a question with
no formula is still a unit.
For a root kind `["unformalised", reason]`, meaning must be
`{"unformalised": reason}` with the same reason. A disagreement is
`InvalidInput`; the unit has one reason in coverage, counted once. Nested
unformalised kinds under other roots carry their own reasons.
`content` is `{"ast":[...]}` for an existing formula or
`{"fence":"unit_id"}` with `surface` set to `english` or `strict`. An English
fence goes through the existing all-derivations parser. The optional
`meaning_id` must match the environment-bound formula identity.

With `norms@0`, a unit of kind `norm` may instead carry the W1 `{"norm":{...}}`
block from [the norm specification](norms.md#32-norm-units-document-content).
The loader validates all active rules together, including precedence and
typing, and passes their canonical blocks to the W1 document admission route.
Quoted norm content retains its kind and source provenance but contributes no
active layer. `ve document check` includes regenerated norm layers in its
premise check; graph leaves may cite them with `layer:norms:<predicate>`.
The compiled norm unit's `meaning_id` binds its canonical W1 block as `ast`
and the environment ID under the shared `ve-meaning-<identity-version>` digest
domain. Every active norm block is validated even when the environment has no
regulated predicates; norm content requires `norms@0`.

With a `ve-units@1` environment (`documents@1`, `order@0`, `relational-fol@0`,
`time@0`), `content` is `{"quantity":{...}}`: a `ve-quantity@1` statement
admitted before erasure. Legacy `ast` content is dimensionless source input to
the same admission, and an English fence is read once across the whole
grammar (`parse_w6_sentence`). Graph nodes carry `quantity` instead of `ast`,
and deductions carry `ve-quantity-certificate@1`. Lean `VE.Time.Document`
admits the graph with the base provenance rules and no Background, and binds
the report to the annotated meaning ids (`admit_quantity_report_sound`).
A quantity lemma is `{"name", "conclusion", "leaves", "certificate"}`: leaves
are `{"quantity", "label"}` with no `cite` label, and the certificate is a
`ve-quantity-certificate@1` from exactly the leaves, in order, to the
conclusion, checked when the lemma is decoded. A `cite:<bundle>/<lemma>` leaf
states that conclusion and the report carries every lemma leaf with its label,
so the root holds wherever the report's non-citation leaves hold
(`cites_discharged`).

A source unit that contains both checked and unresolved text has
`{"id", "span", "status":"MIXED", "parts":[...]}`. Each part has the ordinary
unit fields plus a unique ID and one status: `CHECKED`, `OPEN`, `LABELLED`, or
`UNFORMALISED`. Part spans use absolute byte offsets and exactly partition the
parent span in order, including whitespace and punctuation. The parent has no
independent content. Admission uses the part IDs; the checked document identity
binds the parent and parts, and the loader retains `parent_id` on each compiled
part. Coverage reports `bytes_by_status` alongside `bytes_by_kind`; the two
tables each total the source byte count. Existing unsplit units may also set a
status; otherwise it is inferred from content and meaning. An active reading
set determines the compiled status: an open or non-assertion choice is `OPEN`,
and an authored assertion singleton with content is `CHECKED`.

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
separate removable intent annotations and are ignored by all checks and report identities.

For assertion readings in one environment, `ve document readings --conclusion`
uses fixed assertions, validated active norm layers, and the latest reading-set
version for each source unit. A pending norm reading leaves the premise status
and norm layer admission unresolved until its choice can be elaborated.
When a recorded narrowing removes every pending norm choice, the query
recomputes fixed premises from the retained readings, restoring validated
active norm layers. Retained pending norm choices still leave the query unknown.
Authored singleton choices are premises too. It first proves ALL from fixed
assertions and one conjunction of per-unit disjunctions, with
certificate replay. It proves NONE with one checked finite model that satisfies
every reading and fixed assertion and refutes the conclusion. SOME needs a named choice proof and
a checked model for another choice; its vacuity report describes the proved choice's premises.
Search exhaustion is UNKNOWN. Other kinds
are planned as complete choices up to 64; until their W1/W3 elaborators land,
the verdict is UNKNOWN. The reading set is only the readings considered so far,
not a claim that every plausible source interpretation has been found.

After W3, an embedded environment may pin `defined` declarations and a unit
may carry the `definition` kind. Python validates the declared bodies and
computes definition Background for document premise checks. The unit's formula
content does not itself declare or redefine a predicate; the environment is
the versioned authority. Graph admission for documents with defined
environments remains explicitly unsupported by both the Python and Lean
routes. Definition readings also remain UNKNOWN until each choice can be
elaborated against its own environment and bound to a certificate.

If a claim graph is present, `ve document check` sends the compiled unit kinds,
content, labels, background, citations and graph to P0 `admit_document`.
Unsupported non-assertion readings cannot enter that P0 route. Quoted content
needs an explicit bridge leaf there. The wrapper report identity binds canonical
validated metadata, the source bytes, and VE fence content. It omits removable
weights and ignores JSON layout. Its payload key is `document`; the P0 identity
is preserved as `core_report_id`. A check also reports the
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
