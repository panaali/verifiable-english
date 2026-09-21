# Writable English surface, version 1

`ve_english` is a controlled drafting language for human oversight. Its ordinary
clauses use determiners, relative clauses, and definite noun references. Its
complex clauses use enumerated provisions. It is deliberately smaller than
unrestricted English: authors write the same forms that the renderer produces.
There are no formula parentheses, implicit witnesses, pronoun resolution rules,
implicit argument reversals, omitted conditions, reassociation, or simplification.
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
metadata cannot insert statement boundaries or arbitrary logical structure.
Finite atomic idioms can contain internal punctuation or coordination. Rejected sort nouns
use `entity of sort "identifier"`. Rejected predicate templates use `is classified
as "identifier"` or `has the recorded relation "identifier" to`. These explicit
fallbacks keep every constructor available without inventing semantic aliases.
Single-word formal unary identifiers can retain their atomic spelling when safe.
Undeclared binary verbs use bare spelling only for the finite transitive set
`owns`, `audits`, `undermines`, `performs`, `follows`, `benefits`, `outranks`,
and `exceeds`; a spelling ending in `s` alone does not establish transitivity. Missing metadata is distinguished from rejected data.

Relative clauses use `who` for the noun `person` and `that` for other sorts.
Neither is a cross-clause pronoun. A universal guard contracts when its one,
two, or three predicate atoms (positive or validated-negative) refer to the new binder as
subject or object. Object relatives preserve argument order: `every service that
alice owns` binds the service in the second argument, while `every person who
owns legacy` binds the person in the first. Consequent contractions remain subject
relatives. Two conjuncts use `A and B`. Three preserve exact binary association:
`A and B, and C` means `(A ∧ B) ∧ C`; `A, and B and C` means `A ∧ (B ∧ C)`.
The comma records the outer conjunction. This punctuation is necessary because
VE preserves AST association, even for logically equivalent trees. An optional
repeated `who`/`that` is accepted after each conjunction. Deeper or mixed and/or
guards keep the enumerated structure. A relative guard reconstructs implication;
an existential relative reconstructs its body without an implicit guard.

Conditionals use `if FORMULA, then FORMULA`, including quantified or explicitly
negated single clauses. The renderer never splits labels across if/then and
never emits a one-item enumeration. Two atomic conjuncts use `both … and …`;
two non-atomic clauses use `Both of the following hold:`. `All of the following
hold:` is reserved for genuinely nested connective structure. Negation uses
validated wording or `it is not the case that`; no `No …` contraction is emitted.

For closure, `starting from SOURCE, DESTINATION is reachable by one or more
"relation" steps` keeps the source before the destination. `zero or more`
denotes reflexive transitive closure. A body-defined step introduces its source
and destination in that order, then gives a scoped `satisfies this condition:` definition; outer
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
               | "if ", formula, ", then ", formula ;
listing        = ("all of the following hold:" | "both of the following hold:"), space,
                 marker, space, formula, ";", space, marker, space, formula
               | "at least one of the following holds:", space,
                 marker, space, formula, ";", space, marker, space, formula
               | "if the following holds:", space, marker, space, formula,
                 ";", space, "then the following holds:", space,
                 marker, space, formula ;
universal      = "for every ", declaration, ", ", formula
               | "for every ", declaration, relative-pronoun, guard, ", ", formula
               | "every ", declaration, " ", relative
               | "every ", declaration, relative-pronoun, guard, " ", relative ;
relative-pronoun = " who " | " that " ;
guard          = guard-atom
               | guard-atom, " and ", guard-relative
               | guard-atom, " and ", guard-relative, ", and ", guard-relative
               | guard-atom, ", and ", guard-relative, " and ", guard-relative ;
guard-relative = ["who " | "that "], guard-atom ;
guard-atom     = relative | template-with-bound-object-removed ;
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
relative       = selected-template-with-new-binder-subject-removed ;
reach          = "starting from ", term, ", ", term, " is reachable by ",
                 count, " or more ", relation-name, " steps"
               | "starting from ", term, ", ", term, " is reachable by ",
                 count, " or more steps, where a step from ", article, " ",
                 declaration, " to ", article, " ", declaration,
                 " satisfies this condition: ", formula ;
count          = "one" | "zero" ;
```

Additional constraints enforce the environment's argument sorts and lexical
scope; closure requires `closure@0`. The two list entries are ordered and never
flattened: outside short relative guards, a three-leaf conjunction retains its
original binary association as a nested list. At even list depth the two markers are `(a)`, `(b)`; at odd depth
they are `(i)`, `(ii)`. Each nested list adds two spaces of indentation. A step
definition has no list marker. Legacy single-step and split-if lists remain
accepted for backward compatibility, but are never emitted. Marker spelling and fixed arity recover
the tree independently of visual indentation. Quantifiers and negation take one
complete following formula, not an unspecified span of prose. Compact `both` and `either`
forms have atomic operands; prefix `if` accepts complete formulas. These restrictions avoid the familiar ambiguity
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
Generic templates still reject symbol/head collisions and negating prefixes.
The finite idiom set explicitly allows shared heads such as `undermines` and
`undermines the oversight role of`; each expanded grammar is audited.

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

## Reviewed overlays and explicit suggestions

Each use case has a new `environment.english.json`. It binds the unchanged
`environment_id` and contains only sort nouns and predicate wording, with
`suggested: false` for the hand-written reviewed entries. The schema rejects
arguments, descriptions, constants, and any other semantic fields. The overlay
has its own domain-separated canonical JSON digest, shown in the English legend.
It is never discovered or applied implicitly. Other views ignore display options
and retain their original bytes.

```sh
uv run python -m ve render --env usecases/birthright-citizenship-debate/environment.json \
  --english-vocabulary usecases/birthright-citizenship-debate/environment.english.json \
  --with-legend usecases/birthright-citizenship-debate/claims.ve

uv run python -m ve suggest-vocabulary --env environment.json > suggestions.json
uv run python -m ve render --env environment.json --english-vocabulary suggestions.json \
  --accept-suggested-vocabulary --with-legend claims.ve
```

`ve.suggest_vocabulary(env)` returns deterministic, lint-clean overlay candidates,
each marked `suggested: true`. It uses a finite adjective/modifier vocabulary,
`is_` and adjectival snake_case, known transitive verbs, and checked `has_` idioms
such as `has_access_to`. Exact simple descriptions can supply an adjective or
establish “United States” for `born_in_us`; it never lowercases US into the pronoun
“us”. Arbitrary descriptions, abbreviations, modality, and uncertain argument
roles produce no suggestion. This is intentionally incomplete.

Passing a suggested overlay without `--accept-suggested-vocabulary` fails. With
that flag and no overlay file, the CLI explicitly generates and accepts suggestions.
In Python, pass `vocabulary=overlay, accept_suggested_vocabulary=True` to render,
parse, check, or legend functions. Every suggested entry stays **unreviewed** in
the legend after acceptance. Acceptance permits use; it does not certify meaning.
The same overlay must accompany English parsing and rendering.

Remaining awkward cases are real: nested mixed guards still read like legal
lists; object relatives can repeat `that` in `every state that that person resides in`;
three-atom grouping commas are a controlled-language convention; multiple
same-sort binders require first/second or numbered names; quoted constant IDs
such as `"rate_decision"` and `"lower_prices_goal"` remain opaque. Reachability
still names its relation and step endpoints explicitly. The Claude priority
sentence remains long. Modal, normative, temporal, and contested legal predicates
remain atomic labels whose fuller qualifications live in the original descriptions
and use-case GAPS files. Reviewed wording supplies no modal calculus or resolution
of the citizenship dispute. Suggestions intentionally leave uncertain names unworded.

<!-- BEGIN GENERATED ENGLISH EVIDENCE -->

**75,000 distinct well-typed environment/AST pairs** round-tripped through
`render` and `parse_english`, across fifteen configurations (the original ten,
four reviewed overlays, and explicitly accepted suggestions). Each configuration
contributed 5,000 distinct ASTs: directed boundary cases followed by seeded random
draws. Directed cases cover every template, validated negatives, subject and object relatives, two-atom guards,
both three-atom associations, deeper/mixed guards, nested implications, and the
actual use-case claims. Duplicate draws are recorded, not counted twice.
**7,500 environment/text pairs** (500 per configuration) had exactly one
Earley dynamic-complete derivation, with zero ambiguity nodes. Every directed
case is in that sample. This is finite evidence, not a universal unambiguity proof.
The report records seeds, corpus/grammar hashes, overlay digests, constructor
counts, and all original environment IDs. Counts are configuration-indexed;
the same text may appear under different vocabularies.

All **706 original identity fixtures** retain English transport checks.
Original environment JSON, strict claims, identities, and historical views remain unchanged.

| Use case | Predicates | Original declared wording | Accepted original wording | Reviewed overlay wording | Overlay lint issues |
|---|---:|---:|---:|---:|---:|
| birthright-citizenship-debate | 6 | 0 | 0 | 6 | 0 |
| claude-constitution-excerpt | 18 | 0 | 0 | 18 | 0 |
| news-article | 16 | 0 | 0 | 16 | 0 |
| us-constitution-14th-s1 | 13 | 13 | 13 | 13 | 0 |

The overlays supply reviewed wording for **all 53 predicates**, including the
40 originally missing templates. Finite lexical idioms also cover the four
previously rejected constitutional templates. The original declarations are
still visible alongside the selected wording in each artifact legend.

### Ten actual use-case sentences: before and after

The baseline text and commit are stored in `conformance/english-before-after.json`.
Each after-text is generated from the same strict claim and parsed back unchanged.

#### birthright-citizenship-debate, statement 1

Before:

```text
For every person, if the following holds:
  (a) both that person is classified as "born_in_us" and that person is classified as "subject_to_jurisdiction";
then the following holds:
  (b) that person is classified as "us_citizen".
```

After:

```text
Every person who is born in the United States and is subject to US jurisdiction is a US citizen.
```

#### birthright-citizenship-debate, statement 2

Before:

```text
For every person, if that person is classified as "has_noncitizen_domiciled_parent", then that person is classified as "subject_to_jurisdiction".
```

After:

```text
Every person who has a noncitizen parent domiciled in the United States is subject to US jurisdiction.
```

#### claude-constitution-excerpt, statement 1

Before:

```text
For every entity of sort "claude_model", if that entity of sort "claude_model" is classified as "current_claude_model", then that entity of sort "claude_model" is classified as "ought_have_core_values".
```

After:

```text
Every Claude model that is current is expected to have the core values.
```

#### claude-constitution-excerpt, statement 2

Before:

```text
For every mechanism, if the following holds:
  (a) that mechanism is appropriate;
then the following holds:
  (b) it is not the case that claude undermines that mechanism.
```

After:

```text
For every mechanism that is appropriate, claude does not undermine that mechanism.
```

#### claude-constitution-excerpt, statement 3

Before:

```text
All of the following hold:
  (a) claude is honest;
  (b) for every action, if the following holds:
    (i) that action is classified as "inappropriately_harmful";
  then the following holds:
    (ii) it is not the case that claude performs that action.
```

After:

```text
Both of the following hold:
  (a) claude is honest;
  (b) for every action that is inappropriately dangerous or harmful, claude does not perform that action.
```

#### news-article, statement 1

Before:

```text
Fed has the recorded relation "raised_on" to "sept16".
```

After:

```text
Fed raised its policy rate on "sept16".
```

#### news-article, statement 2

Before:

```text
Both "rate_decision" is unanimous and warsh has the recorded relation "voted_for" to "rate_decision".
```

After:

```text
Both "rate_decision" is unanimous and warsh voted for "rate_decision".
```

#### news-article, statement 3

Before:

```text
Trump has the recorded relation "promised" to "lower_prices_goal".
```

After:

```text
Trump promised "lower_prices_goal".
```

#### us-constitution-14th-s1, statement 1

Before:

```text
For every person, if the following holds:
  (a) all of the following hold:
    (i) either that person was born in the United States or that person was naturalized in the United States, or both;
    (ii) that person is subject to the jurisdiction of the United States;
then the following holds:
  (b) all of the following hold:
    (i) that person is a citizen of the United States;
    (ii) for every state, if that person resides in that state, then that person has the recorded relation "citizen_of_state" to that state.
```

After:

```text
For every person, if all of the following hold:
  (a) either that person was born in the United States or that person was naturalized in the United States, or both;
  (b) that person is subject to the jurisdiction of the United States, then both of the following hold:
  (a) that person is a citizen of the United States;
  (b) for every state that that person resides in, that person is a citizen of that state.
```

#### us-constitution-14th-s1, statement 2

Before:

```text
For every state, for every law, for every person, if the following holds:
  (a) all of the following hold:
    (i) either that state makes that law or that state enforces that law, or both;
    (ii) that person is a citizen of the United States;
then the following holds:
  (b) it is not the case that that law has the recorded relation "abridges_priv_or_imm" to that person.
```

After:

```text
For every state, for every law, for every person, if all of the following hold:
  (a) either that state makes that law or that state enforces that law, or both;
  (b) that person is a citizen of the United States, then that law does not abridge the privileges or immunities of that person.
```


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
For every person, for every service that that person owns, that person audits that service.
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
For every service, if both of the following hold:
  (a) that service is deployed;
  (b) it is not the case that that service is the same as legacy, then that service is reviewed.
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
If at least one of the following holds:
  (a) both legacy is deployed and legacy is not reviewed;
  (b) every service that is deployed is reviewed, then both of the following hold:
  (a) there is a person such that for every service, that person owns that service;
  (b) it is not the case that either legacy is deployed or legacy is reviewed, or both.
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
For every service named S1, starting from S1, legacy is reachable by zero or more steps, where a step from a service named S2 to a service named S3 satisfies this condition: both of the following hold:
  (a) S2 depends on S3;
  (b) it is not the case that S3 is the same as S1.
```
