# Writable English surface, version 1

`ve_english` is a controlled drafting language for human oversight. Its ordinary
clauses use determiners, relative clauses, and definite noun references. Its
complex clauses use enumerated provisions. It is deliberately smaller than
unrestricted English: authors write the same forms that the renderer produces.
There are no formula parentheses, implicit witnesses, pronoun resolution rules,
passive argument reversals, omitted conditions, reassociation, or simplification.
List markers such as `(a)` and `(i)` are structural labels, not formula brackets.

The strict AST and serialization remain canonical. Environment, meaning, model,
and certificate identities, Lean proofs, and all five historical views are
unchanged. An English source has its own exact-byte source ID, just as a renamed
strict source does. The parser returns the same checked De Bruijn AST. Nothing in
this surface upgrades an experimental acceptance record into a proof or confirms
that the author intended the parsed meaning.

## Reading and writing

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env examples/fluent/environment.json examples/fluent/examples.ve

UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve check \
  --env examples/fluent/environment.json --surface english statement.txt
```

`parse`, `check`, `render`, `evaluate`, and `countermodel` accept `--surface
english`. Omitted `--surface` retains strict input compatibility and selects
English display. Explicit `--surface strict` selects strict input and display.
`--view ve_english` and `--view ve_strict` select render output independently of
input. `format` always emits strict canonical text. Historical `import-fol`
defaults and the five-view length-comparison cohort remain unchanged; the full
view registry is `ve.printer.RENDERING_VIEWS`.

The Python entry points are `render(value, env, "ve_english")`,
`parse_english(env, source)`, `parse_english_with_metadata(env, source)`, and
`check(env, source, surface="english")`. The richer parse result contains the
original input, strict canonical text, and the deterministic English paraphrase.
Acceptance JSON shows both input and paraphrase and a `changed` flag. The render
and format commands report a differing paraphrase to stderr, leaving stdout
usable as a document. Countermodel JSON includes paraphrases for each input file.
Sentence-initial capitalization and inter-word whitespace may vary. Statements
end with a period. Diagnostics include a character offset, line, column, and a
plain-language account of what was expected. Type and scope errors also reject.

One active entity of a sort is `that person` or `that service`. If two entities
of that sort can be simultaneously in scope anywhere in the statement, their
declarations and references use `first` and `second` throughout the statement.
These designations **do not assert that the entities are distinct**. Beyond two,
the statement uses the sort's distinct letter and a scope-depth number, such as
`S1`, `S2`, `S3`. The English legend explicitly describes this fallback and maps
letters to sorts. Sibling scopes can reuse names; references never cross a scope
boundary. Both existing naming-policy arguments are accepted, but English noun
references always restart per statement because their meaning is lexical scope,
not document numbering.

Constants retain their declared identifier names. Simple nonreserved names are
bare; reserved or compound names are double-quoted. A quote identifies a name,
not a proposition or an English interpretation of that identifier. Vocabulary
metadata cannot insert statement punctuation or structure. Rejected sort nouns
use `entity of sort "identifier"`. Rejected predicate templates use `is classified
as "identifier"` or `has the recorded relation "identifier" to`. These explicit
fallbacks keep every constructor available without inventing semantic aliases.
Single-word formal unary identifiers can retain their atomic spelling when safe.
Undeclared binary verbs use bare spelling only for the finite transitive set
`owns`, `audits`, `undermines`, `performs`, `follows`, `benefits`, `outranks`,
and `exceeds`; a spelling ending in `s` alone does not establish transitivity. Missing metadata is distinguished from rejected data.

An existential relative clause uses `who` for the selected noun `person` and
`that` for other sorts. Neither is a cross-clause pronoun. Universal guards are
contracted only when one accepted positive or validated negative atom has the
new binder as its subject. A relative guard reconstructs an implication, not a
conjunction. An existential relative clause reconstructs just its body, with no
implicit guard. Rejected templates and more complicated guards retain explicit
clauses. Negation uses a declared, mechanically validated negative template or
`it is not the case that`. No `No ...` contraction is currently emitted.

For closure, `starting from SOURCE, DESTINATION is reachable by one or more
"relation" steps` keeps the source before the destination. `zero or more`
denotes reflexive transitive closure. A body-defined step introduces its source
and destination in that order, then gives a scoped enumerated definition; outer
parameters remain available. Reachability is never inferred from an ordinary
predicate or an English-looking relation name.

## Grammar and inverse

The following EBNF describes the syntactic envelope. `atom`, `relative`, `noun`,
`constant`, `relation-name`, and `letter` are instantiated from the checked
environment by `english_lark_grammar`. Templates are separate grammar
productions, not an opaque atom token. `space` is one or more whitespace
characters. The implementation accepts whitespace between the shown words;
the renderer uses one space except for indented list boundaries.

```ebnf
document       = sentence, { space, sentence }, [ space ] ;
sentence       = formula, "." ;
formula        = atom | negation | compact | listing
               | universal | existential | reach ;
negation       = "it is not the case that ", formula ;
compact        = "both ", atom, " and ", atom
               | "either ", atom, " or ", atom, ", or both"
               | "if ", atom, ", then ", atom ;
listing        = "all of the following hold:", space,
                 marker, space, formula, ";", space, marker, space, formula
               | "at least one of the following holds:", space,
                 marker, space, formula, ";", space, marker, space, formula
               | "if the following holds:", space, marker, space, formula,
                 ";", space, "then the following holds:", space,
                 marker, space, formula ;
universal      = "for every ", declaration, ", ", formula
               | "for every ", declaration, " that ", relative, ", ", formula
               | "every ", declaration, " ", relative
               | "every ", declaration, " that ", relative, " ", relative ;
existential    = "there is ", article, " ", declaration, " such that ", formula
               | "there is ", article, " ", declaration, " who ", relative
               | "there is ", article, " ", declaration, " that ", relative ;
declaration    = noun | "first ", noun | "second ", noun
               | noun, " named ", label ;
term           = constant | "that ", noun | "the first ", noun
               | "the second ", noun | label ;
label          = letter, positive-integer ;
article        = "a" | "an" ;
marker         = "(a)" | "(b)" | "(i)" | "(ii)" ;
atom           = "this holds in all cases" | "this is impossible"
               | term, " is the same as ", term
               | instantiated-positive-template
               | instantiated-validated-negative-template ;
relative       = accepted-template-with-new-binder-subject-removed ;
reach          = "starting from ", term, ", ", term, " is reachable by ",
                 count, " or more ", relation-name, " steps"
               | "starting from ", term, ", ", term, " is reachable by ",
                 count, " or more steps, where a step from ", article, " ",
                 declaration, " to ", article, " ", declaration,
                 " satisfies the following:", space, "(a) ", formula ;
count          = "one" | "zero" ;
```

Additional constraints enforce the environment's argument sorts and lexical
scope; closure requires `closure@0`. The two list entries are ordered and never
flattened: a three-leaf conjunction retains its original binary association as
a nested list. At even list depth the two markers are `(a)`, `(b)`; at odd depth
they are `(i)`, `(ii)`. Each nested list adds two spaces of indentation. A step
definition has exactly one `(a)` entry. Marker spelling and fixed arity recover
the tree independently of visual indentation. Quantifiers and negation take one
complete following formula, not an unspecified span of prose. Compact binary
forms have atomic operands only. These restrictions avoid the familiar ambiguity
of unbracketed `A and B or C` or a quantifier followed by an unscoped conjunction.

The deterministic parser resolves declarations into a nearest-first scope stack,
matches finite lexical templates, and reconstructs constructors without
normalization. The independent Earley grammar deliberately drops type, reference,
indentation, and contraction-selection restrictions; uniqueness in this larger
syntactic language implies at most one derivation in its checked subset for
each tested text. It uses `lexer="dynamic_complete"` and
`ambiguity="explicit"`, and rejects any `_ambig` node anywhere in the forest.
It does not use a prioritized lexer, collapse atoms into a single token, or
pretend that one successful deterministic parse rules out other derivations.

The intended general round-trip argument is structural induction: disjoint
prefix forms recover the constructor; list arity preserves operand association;
the finite lexicon identifies the predicate and ordered arguments; declarations
and unique references invert scope-stack extension; each contracted guard has
one prescribed inverse. From `parse(render(A)) = A`, injectivity follows by
applying `parse` to an assumed equality of rendered texts. **This argument has
not been mechanized, and the tests below are finite evidence, not a universal
proof over every future vocabulary.**

## Lexical precision and remaining limits

`lint_english_vocabulary` (also `lint_vocabulary(env, surface="english")`)
reports the policy used by English. The historical
`lint_vocabulary` and five old renderers retain their exact policy and bytes.
The precision pass keeps their shape, placeholder order, negation, collision,
and injection defenses, and adds a finite grammar of ordinary complements:
`is fully/newly/currently/publicly ADJECTIVE`, `is ADJECTIVE in good standing`,
`is ADJECTIVE under review`, `was born/naturalized in the United States`, and
`is subject to the jurisdiction of/a citizen of the United States`. Active
relational phrases additionally include `reports/contributes/responds to`,
`communicates/collaborates with`, `affords due process of law to`, and
`denies the equal protection of the laws to`. This is a versioned lexical
allowlist, not a general English part-of-speech recognizer. Fixed nominal
complements may contain articles or a sort word without introducing a binder.
Predicate/constant/head collisions and negating prefixes still reject.

Templates remain trusted semantic declarations. Lexical checks cannot discover
that an author has used `disowns` to mean `owns`, or that a sort alias misdescribes
its domain. The legend preserves raw declarations, selected wording, identifiers,
descriptions, and argument order for oversight. Acceptance is not evidence of
faithfulness to the world or to a source document.

There is **no Lean proof for this surface**. The needed theorem is a round trip
for the environment-indexed English grammar and its scope/typing judgments,
`parseEnglish Γ (renderEnglish Γ A) = A` for every admitted checked AST, together
with uniqueness of grammar derivations; renderer injectivity then follows.
Existing Lean theorems concern canonical syntax and semantics, not this parser.
There is **no human readability evidence**: no reader study, comprehension
measurement, or comparison with strict/fluent prose has been run. Missing lexical
metadata still produces conspicuous quoted identifiers. General morphology,
plural agreement, arbitrary English input, and free pronouns are out of scope.
Every checked constructor has an English production, subject to the existing
64 KiB source/output, 64-level AST depth, and 10,000-node resource envelope.

## Reproducible evidence and worked examples

The generated sections below are refreshed by
`uv run python -m conformance.english_artifacts` after the audit:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m conformance.english_surface
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m conformance.english_artifacts
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run pytest -q
```

<!-- BEGIN GENERATED ENGLISH EVIDENCE -->

**50,000 random well-typed environment/AST pairs** round-tripped through the public
`render` and `parse_english` APIs across ten vocabularies. Each vocabulary
contributed 5,000 distinct ASTs; duplicate generator draws are counted separately
in [the committed report](../conformance/english-surface-report.json).
**5,000 rendered environment/text pairs** (500 distinct texts per vocabulary) had exactly one
Earley derivation, with zero ambiguity nodes. The sample includes closure,
duplicate aliases, structural function words in nouns and verbs, structural
identifiers/constants, expanded templates, and all four real vocabularies.
Seeds, environment IDs, corpus hashes, grammar hashes, and constructor counts
are recorded. Counts are environment-indexed; simple formulas can recur in
different vocabularies. This sample is not a uniform distribution over all ASTs.

All **706 existing identity fixtures** have an additional English
transport regression: English round trip preserves their strict bytes and
stored environment/meaning IDs. The original fixture regression still checks
all preimages, model IDs, and formula IDs. Minimal pairs test quantifier order,
argument reversal, scope, and/or, implication reversal, dropped conjuncts,
moved negation, and guard versus consequent.

| Current use-case environment | Predicates | Declared templates | Accepted before | Accepted after | Missing metadata |
|---|---:|---:|---:|---:|---:|
| birthright-citizenship-debate | 6 | 0 | 0 | 0 | 6 |
| claude-constitution-excerpt | 18 | 0 | 0 | 0 | 18 |
| news-article | 16 | 0 | 0 | 0 | 16 |
| us-constitution-14th-s1 | 13 | 13 | 3 | 9 | 0 |

In total: **3/13 before, 9/13 after**. Forty of the 53 predicates
have no declared template in the current integration files. Their absence
is not a rejection and is not counted as an accepted template. The old
`rendered.md` snapshots are not a substitute for current environment JSON.
No environment was edited to improve these numbers or its identities.

Still rejected:

- `citizen_of_state` — `{0} is a citizen of {1}`. Binary copula with a nominal complement; no validated active argument-order template is declared. Codes: BINARY_AUXILIARY, BINARY_CONVERSE, LOGICAL_WORD, SYMBOL_COLLISION.
- `abridges_priv_or_imm` — `{0} abridges the privileges or immunities of {1}`. Contains a lexical coordination using “or”; the linter does not decide whether this is an atomic idiom or a disjunction. Codes: BINARY_CONVERSE, LOGICAL_WORD.
- `deprives` — `{0} deprives {1} of life, liberty, or property`. Places extra coordinated, punctuated content after the second argument; unsupported placeholder shape. Codes: TEMPLATE_SHAPE.
- `within_jurisdiction_of` — `{0} is within the jurisdiction of {1}`. Binary copula with a prepositional complement; outside the active-relation grammar. Codes: BINARY_AUXILIARY, BINARY_CONVERSE, LOGICAL_WORD, SYMBOL_COLLISION.

Missing template identifiers (all retained explicitly in the report and legends):

- birthright-citizenship-debate: `born_in_us`, `has_noncitizen_domiciled_parent`, `has_noncitizen_temporary_parent`, `has_noncitizen_undocumented_parent`, `subject_to_jurisdiction`, `us_citizen`.
- claude-constitution-excerpt: `appropriate`, `benefits`, `bound_to_obey`, `contends_for`, `current_claude_model`, `follows`, `honest`, `inappropriately_harmful`, `interacts`, `ought_follow`, `ought_have_core_values`, `outranks`, `performs`, `relevant`, `sanctioned_check`, `undermines`, `undermines_check`, `violates_hard_constraint`.
- news-article: `appointed_by`, `attributes_to`, `exceeds`, `is_first_under`, `pledged`, `projected_for`, `projected_year`, `promised`, `raised_on`, `raised_to`, `scheduled_for`, `stated`, `submitted_projection`, `took_office_in`, `unanimous`, `voted_for`.

### Twenty-five worked examples

The example vocabulary is reproducible through `conformance.english_artifacts.examples()`.
It extends the existing fluent vocabulary with active `audits` and `depends on`
templates and enables closure. Each block is generated from the **same AST**;
all 25 English blocks are parsed back during generation.

#### 1. Simple universal

Strict:

```text
for every service x0, (x0 is reviewed).
```

Fluent:

```text
for every service S, S is reviewed.
```

English:

```text
Every service is reviewed.
```

#### 2. Relative guard

Strict:

```text
for every service x0, (if (x0 is deployed), then (x0 is reviewed)).
```

Fluent:

```text
for every service S that is deployed, S is reviewed.
```

English:

```text
Every service that is deployed is reviewed.
```

#### 3. A potentially different owner per service

Strict:

```text
for every service x0, (if (x0 is deployed), then (there exists person x1, (x1 owns x0))).
```

Fluent:

```text
for every service S that is deployed, there is a person P such that P owns S.
```

English:

```text
For every service that is deployed, there is a person who owns that service.
```

#### 4. One owner before the service quantifier

Strict:

```text
there exists person x0, (for every service x1, (if (x1 is deployed), then (x0 owns x1))).
```

Fluent:

```text
there is a person P such that for every service S that is deployed, P owns S.
```

English:

```text
There is a person such that for every service that is deployed, that person owns that service.
```

#### 5. Guard versus consequence

Strict:

```text
for every person x0, (for every service x1, (if (x0 owns x1), then (x0 audits x1))).
```

Fluent:

```text
for every person P and every service S, if P owns S then P audits S.
```

English:

```text
For every person, for every service, if that person owns that service, then that person audits that service.
```

#### 6. Existential relative

Strict:

```text
there exists service x0, (x0 is deployed).
```

Fluent:

```text
there is a service S such that S is deployed.
```

English:

```text
There is a service that is deployed.
```

#### 7. Named constants

Strict:

```text
@alice owns @legacy.
```

Fluent:

```text
@alice owns @legacy.
```

English:

```text
Alice owns legacy.
```

#### 8. Validated negative

Strict:

```text
not (@legacy is reviewed).
```

Fluent:

```text
@legacy is not reviewed.
```

English:

```text
Legacy is not reviewed.
```

#### 9. Negative consequence

Strict:

```text
for every service x0, (if (x0 is deployed), then (not (x0 is reviewed))).
```

Fluent:

```text
for every service S that is deployed, S is not reviewed.
```

English:

```text
Every service that is deployed is not reviewed.
```

#### 10. Negated existential

Strict:

```text
not (there exists service x0, ((x0 is deployed) and (not (x0 is reviewed)))).
```

Fluent:

```text
it is false that (there is a service S such that both S is deployed and S is not reviewed).
```

English:

```text
It is not the case that there is a service such that both that service is deployed and that service is not reviewed.
```

#### 11. Two entities of the same sort

Strict:

```text
for every person x0, (there exists person x1, (x0 equals x1)).
```

Fluent:

```text
for every person P, there is a person P2 such that P is the same person as P2.
```

English:

```text
For every first person, there is a second person such that the first person is the same as the second person.
```

#### 12. Ordered relation arguments

Strict:

```text
for every service x0, (there exists service x1, (x0 links x1)).
```

Fluent:

```text
for every service S, there is a service S2 such that S depends on S2.
```

English:

```text
For every first service, there is a second service such that the first service depends on the second service.
```

#### 13. Reversed relation arguments

Strict:

```text
for every service x0, (there exists service x1, (x1 links x0)).
```

Fluent:

```text
for every service S, there is a service S2 such that S2 depends on S.
```

English:

```text
For every first service, there is a second service that depends on the first service.
```

#### 14. Simple conjunction

Strict:

```text
(@legacy is deployed) and (@legacy is reviewed).
```

Fluent:

```text
both @legacy is deployed and @legacy is reviewed.
```

English:

```text
Both legacy is deployed and legacy is reviewed.
```

#### 15. Inclusive disjunction

Strict:

```text
(@legacy is deployed) or (@legacy is reviewed).
```

Fluent:

```text
either @legacy is deployed or @legacy is reviewed, or both.
```

English:

```text
Either legacy is deployed or legacy is reviewed, or both.
```

#### 16. Simple conditional

Strict:

```text
if (@legacy is deployed), then (@legacy is reviewed).
```

Fluent:

```text
if @legacy is deployed then @legacy is reviewed.
```

English:

```text
If legacy is deployed, then legacy is reviewed.
```

#### 17. Negation moved outside a conjunction

Strict:

```text
not ((@legacy is deployed) and (@legacy is reviewed)).
```

Fluent:

```text
it is false that (both @legacy is deployed and @legacy is reviewed).
```

English:

```text
It is not the case that both legacy is deployed and legacy is reviewed.
```

#### 18. Left-associated conjunction

Strict:

```text
((@legacy is deployed) and (@legacy is reviewed)) and (@legacy is deployed).
```

Fluent:

```text
both (both @legacy is deployed and @legacy is reviewed) and @legacy is deployed.
```

English:

```text
All of the following hold:
  (a) both legacy is deployed and legacy is reviewed;
  (b) legacy is deployed.
```

#### 19. Right-associated conjunction

Strict:

```text
(@legacy is deployed) and ((@legacy is reviewed) and (@legacy is deployed)).
```

Fluent:

```text
both @legacy is deployed and (both @legacy is reviewed and @legacy is deployed).
```

English:

```text
All of the following hold:
  (a) legacy is deployed;
  (b) both legacy is reviewed and legacy is deployed.
```

#### 20. Mixed conjunction and disjunction

Strict:

```text
((@legacy is deployed) and (@legacy is reviewed)) or (not (@legacy is deployed)).
```

Fluent:

```text
either (both @legacy is deployed and @legacy is reviewed) or (it is false that @legacy is deployed), or both.
```

English:

```text
At least one of the following holds:
  (a) both legacy is deployed and legacy is reviewed;
  (b) it is not the case that legacy is deployed.
```

#### 21. Exception remains inside the guard

Strict:

```text
for every service x0, (if ((x0 is deployed) and (not (x0 equals @legacy))), then (x0 is reviewed)).
```

Fluent:

```text
for every service S that is deployed and that is not the same service as @legacy, S is reviewed.
```

English:

```text
For every service, if the following holds:
  (a) all of the following hold:
    (i) that service is deployed;
    (ii) it is not the case that that service is the same as legacy;
then the following holds:
  (b) that service is reviewed.
```

#### 22. Negated universal

Strict:

```text
not (for every service x0, (if (x0 is deployed), then (x0 is reviewed))).
```

Fluent:

```text
it is false that (for every service S that is deployed, S is reviewed).
```

English:

```text
It is not the case that every service that is deployed is reviewed.
```

#### 23. Deeply nested provisions

Strict:

```text
if (((@legacy is deployed) and (not (@legacy is reviewed))) or (for every service x0, (if (x0 is deployed), then (x0 is reviewed)))), then ((there exists person x1, (for every service x2, (x1 owns x2))) and (not ((@legacy is deployed) or (@legacy is reviewed)))).
```

Fluent:

```text
if (either (both @legacy is deployed and @legacy is not reviewed) or (for every service S that is deployed, S is reviewed), or both) then (both (there is a person P such that for every service S2, P owns S2) and (it is false that (either @legacy is deployed or @legacy is reviewed, or both))).
```

English:

```text
If the following holds:
  (a) at least one of the following holds:
    (i) both legacy is deployed and legacy is not reviewed;
    (ii) every service that is deployed is reviewed;
then the following holds:
  (b) all of the following hold:
    (i) there is a person such that for every service, that person owns that service;
    (ii) it is not the case that either legacy is deployed or legacy is reviewed, or both.
```

#### 24. One or more named steps

Strict:

```text
for every service x0, (tc[links](x0, @legacy)).
```

Fluent:

```text
for every service S, @legacy is reachable from S by one or more links steps.
```

English:

```text
For every service, starting from that service, legacy is reachable by one or more "links" steps.
```

#### 25. Scoped step definition and a third entity

Strict:

```text
for every service x0, (rtc[service x1, x2 | ((x1 links x2) and (not (x2 equals x0)))](x0, @legacy)).
```

Fluent:

```text
for every service S, @legacy is reachable from S by zero or more steps satisfying [service S2, S3 | (both S2 depends on S3 and S3 is not the same service as S)].
```

English:

```text
For every service named S1, starting from S1, legacy is reachable by zero or more steps, where a step from a service named S2 to a service named S3 satisfies the following:
  (a) all of the following hold:
    (i) S2 depends on S3;
    (ii) it is not the case that S3 is the same as S1.
```
