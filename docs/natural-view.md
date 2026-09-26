# Audited natural view

`ve render --view ve_natural` renders one checked formula at a time. It tries
ordinary English, parses that sentence with the writable English parser, and
enumerates every derivation with the independent Lark Earley grammar. It accepts
the wording only when the parser returns exactly the source AST and Earley finds
one derivation. An unsuccessful candidate gets a per-sentence reason and a
symbol-free explicit English fallback. `render_natural_sentence` also retains
the original fluent text in `fluent_text` for review of fallbacks. No checker,
Lean source, canonical strict printer, or semantic identity changes.

The former explicit `ve_natural` experiment is available as `ve_explicit`.
The frozen five-view measurement cohort uses that name. `natural_formula` and
`natural_document` now return the audited view with renderer
`ve.natural-audited`, version `1`.

## Before and after

Each after sentence below comes from a checked formula. The first six use
`examples/fluent/examples.ve`; the last four use reviewed vocabulary from
the named use case.

| Source | Fluent before | Natural after |
|---|---|---|
| Fluent 1 | For every service S that is deployed, S is reviewed. | Every deployed service is reviewed. |
| Fluent 2 | For every service S that is deployed, there is a person P such that P owns S. | Every deployed service has an owner. |
| Fluent 3 | There is a person P such that for every service S that is deployed, P owns S. | There is a person such that for every service that is deployed, that person owns that service. |
| Fluent 4 | It is false that (there is a service S such that both S is deployed and S is not reviewed). | It is not the case that there is a service such that both that service is deployed and that service is not reviewed. |
| Fluent 5 | For every service S that is deployed and that is not the same service as @legacy, @alice does not own S. | For every service, if both of the following hold: first, that service is deployed; second, it is not the case that that service is the same as legacy, then alice does not own that service. (fallback) |
| Fluent 6 | For every service S and every person P and every person P2, if (both P owns S and P2 owns S) then P is the same person as P2. | For every service, for every first person, for every second person, if both the first person owns that service and the second person owns that service, then the first person is the same as the second person. |
| Birthright | For every person P such that (both P is born_in_us and P is subject_to_jurisdiction), P is us_citizen. | Every person who is born in the United States and is subject to US jurisdiction is a US citizen. |
| Birthright | For every person P such that P is has_noncitizen_domiciled_parent, P is subject_to_jurisdiction. | Every person who has a noncitizen parent domiciled in the United States is subject to US jurisdiction. |
| Claude constitution | For every claude_model L such that L is current_claude_model, L is ought_have_core_values. | Every current Claude model is expected to have the core values. |
| News | @fed raised_on @sept16. | Fed raised its policy rate on the named sept16. |

The writable natural forms include “Some service is deployed”, “No contractor
may access the server” when the environment declares that atomic relation,
and “Every deployed service is reviewed and has an owner”. The ownership
shortening is licensed only by the literal `{0} owns {1}` predicate template,
with the owner and service in their declared argument positions. It does not
infer a converse relation. “At least 3” and “more than 3” are also writable
comparison wordings in `order@0`; “more than twice the budget” is writable for
literal doubling of a named integer constant. A counting quantifier is not in this branch's
AST, so the view cannot invent one.

## Coverage

Reproduce with `uv run python -m conformance.natural_surface`. The committed
report is `conformance/natural-view-report.json`. The round-trip row samples
100 unique seeded ASTs for each of eleven environments, including `order@0`.

| Corpus | Natural | Total | Coverage |
|---|---:|---:|---:|
| `examples/` | 10 | 11 | 90.9% |
| `docs/fluent-examples.md` source | 5 | 6 | 83.3% |
| `usecases/` | 58 | 96 | 60.4% |
| `tests/data/fluent-items.jsonl` | 5 | 6 | 83.3% |
| Seeded round-trip corpora | 309 | 1,100 | 28.1% |
| **Total** | **387** | **1,219** | **31.7%** |

All 832 fallbacks were recorded as `symbols_or_variable_names`: their first
English candidate needed structural list markers, arithmetic brackets,
numbered variable labels, or quoted predicate identifiers. There were zero
accepted sentences with multiple
derivations or a different AST, and no skipped corpus source. The final
reader-facing fallback spells out those markers. The 4,096-byte Earley budget
fails closed; over-budget candidates fall back with an explicit reason.

## Reader-facing notation audit

The historical `ve_fluent` printer puts `@` before constants in
`ve/fluent.py:term`, parentheses around compound operands in `unit`, and
brackets around closure step bodies in `Reach`. Arithmetic terms use the
bracketed canonical spelling. The writable `ve_english` renderer removes `@`
but can emit `(a)`/`(b)` list markers, bracketed arithmetic, and numbered
letters for three or more entities of one sort. Those characters come from
`EnglishTraversal._markers`, `render_int_term`, and `binding`. They remain
useful for editing and historical comparison. The audited `ve_natural` view
provides symbol-free claim text for readers, including fallback sentences.
The web app is outside this branch; its reader-facing claim selector should
use `ve_natural` when integrated and keep `ve_strict` for the strict inspector.
