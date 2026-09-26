# Audited natural view

`ve render --view ve_natural` renders checked statements as prose paragraphs.
Sentence boundaries remain in the `Document` AST and the view's `sentences` data;
they are spaces rather than forced line breaks in the display. Callers can pass
`paragraph_breaks=(2,)` to begin a new paragraph before sentence index 2; the
view records each paragraph's sentence range. Every proposed
sentence and the complete displayed document pass the writable English parser,
including its Earley all-derivations check. Acceptance requires the exact source
AST and one derivation. An unsuccessful candidate gets a per-sentence reason and
an audited explicit English form. `render_natural_sentence` retains the original
fluent text in `fluent_text` for fallback review. The strict printer and formula
semantics are unchanged.

The former explicit `ve_natural` experiment is available as `ve_explicit`.
The frozen five-view measurement cohort uses that name. `natural_formula` and
`natural_document` now return the audited view with renderer
`ve.natural-audited`, version `3`. Each sentence in the UI data has a `form`
field of `natural` or `explicit form`, a `role` of `premise` or `conclusion`, and
a fallback reason where applicable.

For the web app's first example, the old three line display was “Every reviewed
service is safe. / Api is reviewed. / Api is safe.” The
`examples/assist/environment.english.json` display lexicon declares `the API`
for the unchanged assist environment. A checked document with its third
statement marked as a conclusion
now displays:

> Every reviewed service is safe. The API is reviewed. Therefore the API is safe.

`natural_document(env, document, conclusions=(2,), vocabulary=lexicon)`
produces this text; the equivalent `render(..., view='ve_natural',
conclusions=(2,), vocabulary=lexicon)` does too. The
writable parser accepts it with the same three formula ASTs. The API
`parse_english_argument` builds a claim graph with a certificate-backed edge
from the first two sentences to the third. An unproved marked conclusion is
rejected. `Therefore`, `So`, `Hence`, and `It follows that` have the same checked
role. They are never interpreted as assumptions.

**Preceding premises** means every earlier *unmarked* sentence in the same
document, including earlier paragraphs. Earlier conclusions are excluded from
the premise set. There is no implicit section reset. A marker requires at least
one earlier premise and a replayable entailment certificate; an inconclusive
proof search does not license it. The graph's only assumption leaves are the
unmarked sentences.

Constant display forms are declared once as optional `constants` entries in an
English vocabulary overlay, each with a `verbalisation` string: `the API`,
`Alice`, and `the European Union` are examples. The overlay names the exact
`environment_id` and is passed to both renderer and parser.
They change spelling, articles, and casing, while every parsed term remains the
same declared `Const` symbol. Invalid or colliding names use the quoted
identifier fallback. The logical environment and its identity remain unchanged.

Three item distributive lists are writable for distinct constant subjects with
one unary adjective predicate (“The API, Beta and Gamma are reviewed”) and for
one constant with three distinct unary adjective predicates (“The API is
reviewed, deployed and safe”). `or` has the corresponding fixed right
association in the AST. The parser audits the full sentence and rejects a
different association or a competing reading. Existing `who` and `that`
relative clauses bind their locally introduced quantifier; they do not search
the preceding paragraph for an antecedent. A simple “It is safe” resolves only
when exactly one constant has been mentioned earlier in the document. With zero
or multiple named referents, the parser rejects `It`, and the renderer uses the
explicit name. Marked conclusions keep their explicit subject name.

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
The report also records the three statement web app example as a complete
paragraph: exact document round trip, one English derivation, and replay of its
single claim graph deduction all pass. That prose probe is reported separately
from the 1,219 formula samples.

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
The web app is outside this branch; its reader-facing claim selector can use
`ve_natural` with conclusion indices when integrated and keep `ve_strict` for
the strict inspector.
