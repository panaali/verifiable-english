# Audited natural view

`ve render --view ve_natural` renders one checked formula at a time. It tries
ordinary English and parses the exact displayed sentence with the writable English
parser, including P0's unconditional Earley all-derivations check. It accepts
the wording only when the parser returns exactly the source AST and Earley finds
one derivation. An unsuccessful candidate gets a per-sentence reason and an
audited, writable explicit English form, which may contain exact quoted identifiers
or structural notation. `render_natural_sentence` also retains
the original fluent text in `fluent_text` for review of fallbacks. No checker,
Lean source, canonical strict printer, or semantic identity changes.

The former explicit `ve_natural` experiment is available as `ve_explicit`.
The frozen five-view measurement cohort uses that name. `natural_formula` and
`natural_document` now return the audited view with renderer
`ve.natural-audited`, version `2`. Each sentence in the UI data has a `form`
field of `natural` or `explicit form` and a fallback reason where applicable.

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
| Fluent 5 | For every service S that is deployed and that is not the same service as @legacy, @alice does not own S. | For every service, if both of the following hold: first clause: that service is deployed; end first clause; second clause: it is not the case that that service is the same as legacy; end second clause, then alice does not own that service. |
| Fluent 6 | For every service S and every person P and every person P2, if (both P owns S and P2 owns S) then P is the same person as P2. | For every service, for every first person, for every second person, if both the first person owns that service and the second person owns that service, then the first person is the same as the second person. |
| Birthright | For every person P such that (both P is born_in_us and P is subject_to_jurisdiction), P is us_citizen. | Every person who is born in the United States and is subject to US jurisdiction is a US citizen. |
| Birthright | For every person P such that P is has_noncitizen_domiciled_parent, P is subject_to_jurisdiction. | Every person who has a noncitizen parent domiciled in the United States is subject to US jurisdiction. |
| Claude constitution | For every claude_model L such that L is current_claude_model, L is ought_have_core_values. | Every current Claude model is expected to have the core values. |
| News | @fed raised_on @sept16. | Fed raised its policy rate on "sept16". (explicit form) |

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

| Corpus | Natural | Total | Natural share | Fallback share |
|---|---:|---:|---:|---:|
| `examples/` | 11 | 11 | 100% | 0% |
| `docs/fluent-examples.md` source | 6 | 6 | 100% | 0% |
| `usecases/` | 73 | 96 | 76.0% | 24.0% |
| `tests/data/fluent-items.jsonl` | 6 | 6 | 100% | 0% |
| Seeded round-trip corpora | 503 | 1,100 | 45.7% | 54.3% |
| **Total** | **599** | **1,219** | **49.1%** | **50.9%** |

Of the 620 explicit forms, 618 needed structural notation or quoted identifiers;
one candidate changed the AST and one failed the English audit. The final output
was independently checked sentence by sentence for exact AST identity and one
derivation, with zero wrong readings and no skipped corpus source.

## Reader-facing notation audit

The historical `ve_fluent` printer puts `@` before constants in
`ve/fluent.py:term`, parentheses around compound operands in `unit`, and
brackets around closure step bodies in `Reach`. Arithmetic terms use the
bracketed canonical spelling. The writable `ve_english` renderer removes `@`
but can emit `(a)`/`(b)` list markers, bracketed arithmetic, and numbered
letters for three or more entities of one sort. Those characters come from
`EnglishTraversal._markers`, `render_int_term`, and `binding`. They remain
useful for editing and historical comparison. The audited `ve_natural` view
uses word-marked nested lists and ordinal references through the eighth entity
when the one-reading check accepts them. Explicit forms retain exact writable
notation, including underscores and depth-specific list markers.
The web app is outside this branch; its reader-facing claim selector should
use `ve_natural` when integrated and keep `ve_strict` for the strict inspector.
