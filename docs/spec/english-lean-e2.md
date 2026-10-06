# English in Lean, E2: Lean decides English admission (statement specification)

> Status: statement specification, draft 1 (2026-10-06), branch `design/english-lean-e2`. This is the item-1
> statement spec of [english-lean-E2-PLAN.md](english-lean-E2-PLAN.md) draft 2 (the **plan**). It writes out stages
> E2.0 to E2.5 on top of `english-lean-s3.md` draft 2 (the **S3 spec**) as built on `english-lean-s3/integrate` at
> `531f2789` (the **S3 build**). The S3 build, the S3 spec, `english-lean-S3-PLAN.md` and `english-lean-s3-report.md`
> (the **S3 report**) are on that branch and reach `main` when S3 merges; `S3 2.9` refers to the S3 spec, `S2 2.6`
> to `english-lean-s2.md`, `base 2.12` to `english-lean.md`. Their definitions and statements are not repeated.
>
> **Nothing was built for this draft.** What was run: a scratch file elaborated against the S3 build (section 12).
> It did four things:
>
> - It ported Python's vocabulary policy into Lean, with the three new carriers beside `Env`. Then it elaborated the
>   text of 5.2, 5.3 and 5.5 of this spec verbatim in the build's namespace, with the three new fields at their
>   defaults, and checked that it agrees with the port.
> - It proved six of the statements of 5.5 on that text. Two more statements were checked as shapes, the senses
>   statement over a parameterised signature and the three service statements against a local copy of the mode
>   type.
> - It computed every value marked *computed* in section 8, by the port, the S3 reader, `admit` and `firstChecked`.
> - It recomputed Python's recorded `lexicon_id` for the 22 use-case rows of
>   `conformance/english-lean/lexicon-report.json`, from the port's selection.
>
> **Python was not run.** A Python outcome named here was read from `ve/english.py`, `ve/printer.py` and
> `ve/english_vocabulary.py`, or recovered from an identity Python recorded. Every `file:line` was read on
> 2026-10-06 in the S3 build's worktree and must be re-read at each step.

## 0. Scope, one paragraph

E2 moves `english.admission` from Python to Lean. Lean gets three service modes (`english.read`, `english.grammar`,
`english.check`), and the boundary fixes that make every corpus environment and every overlay readable. Python's
vocabulary policy becomes a Lean check, V6, stated as Lean's port of Python's selection. A request-level
admission runs V6 and then `admit`, and the same holds for the check of rendered candidates and for the senses
mode. Lean's codes, classes, texts and advice are the ones shown. Python relays and proves each obligation with
the existing entailment operation. Its hand parser and Lark audit become a comparator that decides nothing. A
deletion ledger maps each Python decision site of formula-level admission. The evidence is the G3 comparisons S3
left open and the lean-first corpus A/B. Statement-layer English stays for E3, and the comparator is deleted in
the next stage.

In this specification: the decisions (1), the definitions (2), the English of the new outcomes and claims (3), the
diagnostics (4), the Lean definitions and the exact statements (5), files and gates (6), what is consumed and
returned (7), the acceptance fixtures (8), limits (9), the statement review checklist (10), open points (11), and
how the figures were computed (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | V6 is Lean's port of Python's selection (`EnglishVocabulary`, `english.py:230–527`, with the lint of `printer.py:183–338`). A lexicon passes V6 when each wording is Python's choice or the quoted fallback, each noun Python's or the fallback noun, each spelling Python's or the quoted name, and each negative Python's, beside Python's wording | 2.3, 5.2 |
| D2 | V6 is checked beside `Lexicon.valid`, not inside it: `Lexicon.valid`, `read`, `admit`, `EnglishOneReading`, `Extends` and every S2, S3 and senses statement stay word for word | 2.4, lx30 |
| D3 | V6 is checked on the request's own environment, overlay and lexicon, in every mode that receives a producer's lexicon (`english.read`, `english.check`, `english.grammar`, `senses.read`), and never on a projection that Lean computes | 2.4, 5.3 |
| D4 | V6 covers what S3 2.9 named (the code set with the rescue, the idiom branch, the reserved risk wordings) and the four selections S3 did not name: mechanical wordings, negatives, nouns and spellings. It does not cover letters or aliases | 2.3, lx25 to lx28, Q2 |
| D5 | `SortDecl.plural`, `PredDecl.suggested` and `AltBlock.optional` are new fields, all with defaults. V6 reads them; no rule and no action does | 2.2 |
| D6 | The lexicon names the environment it was selected for: with an overlay, the display environment (the overlay merged in, as `display_environment` builds it). `decodeLexicon` checks the lexicon's `environment_id` against that identity. The response's `environment_id` stays the submitted environment's | 2.2, ev15 |
| D7 | The boundary of S3 2.3 is extended to `norm-defaults@0`, `soft-norms@0` and W6 units outside `risk@0`. Each set of declarations is validated as submitted, the typed check reads a reduced view, and the identity is computed over the submitted environment | 2.2, ev14 |
| D8 | `admitRequest` is V6, then `admit`; `checkRequest` is V6, then `firstChecked`; `sensesRequest` is V6 on the request's own environment and lexicon, then `readWithSenses`. A V6 failure is `invalidGrammar` with fault `lexicon` and the failure `("V6", kind, name)` | 2.5, 5.3 |
| D9 | Every response that is not `one` carries `class`, the Python error class the relay raises, from Lean's class table. The relay holds no class table and no text | 4.2 |
| D10 | `IllTyped` has the class `TypeMismatch`. The typed check's messages carry no class (computed: `ill-typed or unbound formula`, `invalid indexed formula`), so where Python raised `UnknownSymbol` or `UnsupportedProfile`, `DELTA.md` lists a `wording` row | 4.2, Q4 |
| D11 | The `one` response carries the obligations, each with the Lean text the relay raises if its proof is not found, and the sentence spans in code points | 4.4 |
| D12 | The advice table of S3 4.3 is completed with the two `allows` messages, one of them a pattern with free words | 4.3 |
| D13 | `english.check` decodes wire formulas with `EFormula.decode`, a left inverse of `EFormula.encode` | 5.3 |
| D14 | The service keeps prepared grammars per process, keyed by `environment_id`, `overlay_digest` and `lexicon_id`. The response is a function of the request alone | 2.7 |
| D15 | After the flip, Python's hand parser, the Lark audit and Python's premise check run only as the comparator: switched on by `VE_ENGLISH_COMPARATOR=1`, logged, never returned, never raising. The next stage deletes them | 2.8 |
| D16 | Python's producer of the lexicon stays (untrusted; V6 checks it). The ledger lists its selection logic as kept, with its callers | 2.9, Q1 |

## 2. Definitions

### 2.1 Terms

| Term | Meaning |
|---|---|
| producer | Python's `EnglishVocabulary`, which proposes the lexicon a request carries |
| Python's choice | what the producer selects for a symbol: wording and negative, noun, spelling (2.3) |
| port | the Lean functions of 5.2 that compute Python's choice |
| display environment | the environment with the overlay's sort and predicate entries merged in, as `display_environment` builds it (`english_vocabulary.py:99–118`) |
| request's own lexicon | the lexicon the request carries, before any senses projection |
| obligation | a marked sentence with the earlier unmarked sentences (S3 2.1) |
| comparator | Python's hand parser with the Lark audit and Python's premise check, run beside Lean and never returned |
| decision site | a Python line that decides acceptance, a class, a text, a count or an identity (LEAN-FIRST 5.1, item 3) |

### 2.2 The reader's inputs

**New fields, all with defaults** (D5). No producer, fixture or S3 statement changes.

| Field | Meaning | Decoded from |
|---|---|---|
| `SortDecl.plural : Option String := none` | the declared plural | the overlay's sort entry, else the environment's (`verbalisation.plural`) |
| `PredDecl.suggested : Bool := false` | the overlay's entry for the predicate is marked suggested | the overlay's predicate entry, `suggested` |
| `AltBlock.optional : List String := []` | the predicates the `alternatives` block names as `inaction`, `taken`, `proximate`, in that order, where present | the block |

`Env.roles E` is `[B.available, B.leadsTo] ++ B.optional` for the block `B`, and `[]` without one. Python's role
list is `('available', 'leads_to', 'inaction', 'taken', 'proximate')` (`english.py:396`, `:435`).

**The lexicon names the display environment** (D6). Python's `export(words)` writes `words.env.environment_id`
(`ve/english_grammar/__init__.py:34`), where `words.env` is the display environment. The S3 build's `decodeCase`
compares that identity with `environmentId` of the submitted environment (`Run.lean:170–172`). With an overlay the two
differ, so every request with an overlay is refused. ev15a computes this on the birthright use case: Python's
lexicon gets `InvalidInput: the lexicon names another environment`, while the same lexicon written with the
submitted identity reads to `one` (ev15b). E2.0 changes the check. With an overlay, the lexicon's
`environment_id` must equal `environmentId (displayJson environment overlay)`. `displayJson` merges each overlay
sort entry's fields and each predicate entry's fields into the environment JSON, minus `suggested`, after dropping
the entry's old `negative_verbalisation`. The stub's `displayJson` reproduces Python's display identity: with it the
port's `lexicon_id` equals Python's on all four overlay rows (pt1). The response's `environment_id` stays the
submitted environment's, and the overlay stays bound by `overlay_digest`.

**The boundary** (D7). The S3 build's `Run.environmentId` refuses 4 of the 22 use-case rows of the lexicon report
(computed, ev14):

| Environment | Refusal |
|---|---|
| `usecases/agent-policy/environment.unspecified.json` | `UnsupportedProfile: Unsupported profile norm-defaults@0` |
| `usecases/agent-policy/environment.unspecified.lean.json` | `UnsupportedProfile: Unsupported profile norm-defaults@0` |
| `usecases/eligibility/environment.json` | `fields do not match: expected [language, profiles, spec_revision, vocabulary], got [language, profiles, spec_revision, unit_schema, units, vocabulary]` |
| `usecases/safety-framework/environment.d1.json` | `UnsupportedProfile: Unsupported profile soft-norms@0` |

E2.0 extends S3 2.3's three parts to these:

1. **Validated as submitted.** The `norm-defaults@0` and `soft-norms@0` declarations go through those routes' own
   source decoders, and the W6 units through `Time.Wire`'s unit decoders, as `Risk.Wire.decodeRiskSource` applies
   them under `risk@0`.
2. **The typing view.** It removes what the typed check of formulas does not read, as `riskNormsView` removes the
   unit annotations.
3. **The identity.** It is computed over the submitted environment.

`Route.Gate.decodeEnvelope` is not edited. If the lean-first batch 12b lands first, its `environment` mode is called
instead (plan, question 6).

### 2.3 V6: Python's selection, by its tables

V6 ports what the producer selects. Python computes the selection in this order, and the port follows it:

1. **The lint** (`_NaturalVocabulary`, `printer.py:183–338`): codes for each declared predicate wording at its
   path.
2. **The main loop** (`english.py:264–389`): per predicate, a wording and a negative.
3. **The profile steps.**
   - `alternatives@0` (`:393–414`): the role predicates keep their declared wording; the four words get their fixed
     forms; the aliases.
   - `risk@0` (`:415–447`): the risk forms and negatives, then the reservation of the risk wordings.
   - `rights@0` (`:453–457`): not ported (S3 Q5).
   - `norms@0` (`:521–527`): a modal predicate's wording is its modal form, and it has no negative.
4. **Nouns** (`:239–252`, `:419`): the base noun or the fallback, deduplicated by key; `severity` under `risk@0`.
5. **Spellings** (`:460–510`): the bare name or the quoted name; a declared display form when unique; then a
   fixpoint that quotes every declared form that shares a spelling key with another constant.

**Word lists.** These are `printer.py:93–105`, `english.py:31–49`, `:214`, `:283–285` and `:342`, and
`english_phrases.py:7–8`, copied as data.

| List | Words |
|---|---|
| `logicalWords` | `_LOGICAL_WORDS` (`printer.py:93–99`): 82 entries, 81 distinct (`implies` twice) |
| `closureWords` | `reachable reachability steps satisfying zero more from`, under `closure@0` (`printer.py:238`) |
| `auxiliaries` | `is are was were be been being gets got` |
| `converseEndings` | `by to of from with for` |
| `extraReserved` | `_EXTRA_RESERVED` with the ordinals `first` to `eighth` (`english.py:44–46`) |
| `reserved` | `logicalWords ++ extraReserved` (`_RESERVED`) |
| `comparisonWords` | `less more than least most same` |
| `contentStop` | `_CONTENT_STOP` (`english.py:214`) |
| `mechanicalVerbs` | `owns audits undermines performs follows benefits outranks exceeds` (`:342`) |
| `eligibleCodes` | the ten codes of `:283–285` |
| `boundaryWords`, `blockedWords` | `BOUNDARIES`, `BLOCKED` (`english_phrases.py:7–8`) |
| `naryHeads` | `reports records has is at maps relates links` (`surface/nary.py:30`) |
| `riskTemplates` | the 17 templates of `english.py:71–76` |

**The two pattern tables of the rescue** (`english.py:31–43`). Each pattern is a list of words, and `adj` stands for
one run of lower-case ASCII letters, the regex's `(?P<adjective>[a-z]+)`. A phrase matches a pattern when its parts
at single spaces are the pattern's words.

| Table | Patterns |
|---|---|
| `complementPatterns` (one argument) | `is subject to the jurisdiction of the United States`; `is a citizen of the United States`; `was born in the United States`; `was naturalized in the United States`; `is fully adj`, `is newly adj`, `is currently adj`, `is publicly adj`; `is adj in good standing`; `is adj under review` |
| `activePatterns` (two arguments) | `affords due process of law to`; `denies the equal protection of the laws to`; `reports to`; `contributes to`; `responds to`; `communicates with`; `collaborates with`; `has access to`; `has authority over`; `has responsibility for` |

**The lint codes of a declared wording** (`lintCodes`, `printer.py:223–307`). Here the phrase is the part between
`{0} ` and, for two arguments, ` {1}`. The words are `tokens`, the matches of `[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z]+)?`.

| Code | Holds when |
|---|---|
| `TEMPLATE_LENGTH` | one or two arguments: more than 80 characters, or more than 8 whitespace-separated words; more arguments: more than 160 or 24 |
| `SORT_NOUN` | one or two arguments: the tokens of a sort's name, singular or plural occur in a row in the wording's tokens |
| `DUPLICATE_TEMPLATE` | another predicate declares exactly the same wording |
| `TEMPLATE_SHAPE` | the wording is not `{0} ` + phrase (+ ` {1}`), the phrase being non-empty and on one line; or, for one argument, the phrase does not begin with `is` followed by a word; or, for more arguments, `template_parts` refuses it |
| `PHRASE_SYNTAX` | the phrase is not lower-case ASCII words separated by single spaces |
| `LOGICAL_WORD` | a token is a logical word, with the closure words under `closure@0`; `at` alone is allowed as an n-ary connector |
| `VARIABLE_TOKEN` | a token is `x` followed by digits, or capitals followed by digits |
| `SYMBOL_COLLISION` | a token is owned by another symbol. A symbol owns its name. A predicate owns the head of its declared wording, or of its strict wording when it declares none. A sort owns the last token of its singular and of its plural |
| `NEGATED_HEAD` | a token is `un`, `non`, `un-` or `non-` joined to a predicate's name or head |
| `UNARY_MODIFIER` | one argument and more than two words in the phrase |
| `BINARY_AUXILIARY`, `BINARY_CONVERSE`, `BINARY_VERB` | two arguments: the first word is an auxiliary; the last word is a converse ending; the first word does not end in `s` |

**Python's acceptance of a declared wording** (`acceptsDeclared`, `english.py:264–372`). A wording of more than two
arguments is accepted when it carries no code. A wording of one or two arguments goes through four stages.

1. **Initial verdict.** A wording that carries no code and is not an idiom of its arity is accepted. Otherwise it is
   decided by the rescue, or, if it is an idiom, by the idiom branch.
   - **The rescue** (`:274–309`) accepts when all of these hold:
     - the wording is exactly `{0} ` + phrase (+ ` {1}`);
     - its codes are among the eligible ten;
     - no other predicate's or constant's name occurs in the phrase as a whole word (`\b…\b`);
     - no other predicate's declared head occurs there either, `is`, `was`, `a` and `an` excepted;
     - no word is `un` or `non` joined to a predicate's name or to the word after `{0} is` of a declared wording;
     - the wording has at most 80 characters;
     - a pattern of its arity matches;
     - a matched adjective is not reserved, not an auxiliary, and not a word of a sort's name, singular or plural.
   - **The idiom branch** (`:310–340`) accepts when all of these hold:
     - its codes are among the eligible ten and `VARIABLE_TOKEN`, and `DUPLICATE_TEMPLATE` is not among them;
     - it is anchored: a content word of the idiom is a content word of the predicate's name and description;
     - no constant's name occurs in the phrase;
     - for no other predicate does its name, or its head when the idiom's content words are all content words of
       that predicate's wording, occur in the phrase, unless the word is a `_`-part of both names; `is`, `was`, `a`,
       `an` and `has` are never heads;
     - a phrase ending in ` by` belongs to a predicate whose name ends in `_by`;
     - no word is a negated head.
2. **The suggested path** (`:345–361`). A suggested overlay entry of one argument whose wording passes
   `unary_phrase` is accepted when:
   - no constant's name occurs in the phrase, ignoring case;
   - no other predicate declares a wording with its key;
   - no `[a-z][a-z0-9_-]*` word of the phrase is a negated head;
   - it carries no `NEGATED_HEAD`.
3. **Structure words.** An accepted wording that is not an idiom is refused when one of its `[a-z]+` words is in
   `extraReserved` (`ENGLISH_STRUCTURE_WORD`, `:362–364`). Under `order@0`, a wording is refused when one of its
   lower-cased words is a comparison word (`:365–367`).
4. **Duplicates.** A wording is refused when its key, or its declared negative's key, is the key of another
   predicate's declared wording, of its strict wording when it declares none, or of its declared negative
   (`:368–372`).

**The selection.** These definitions follow Python's steps.

- **`mainSelection`.**
  - With a declared wording: the declared wording when accepted, else the fallback; for more than two arguments,
    the strict wording. A negative goes with an accepted wording of one or two arguments, when it is the declared
    negative, equals `negativeTemplate` of the wording, and has at most 120 characters and 18 words.
  - Without a declared wording: the strict wording for more than two arguments, and for a name of lower-case letters
    that is not reserved, of one argument or one of the `mechanicalVerbs`; else the fallback.
- **`policyPredicate`.**
  - A profile-fixed wording replaces the main selection, except for a modal predicate, and a profile-fixed negative
    replaces the negative.
  - Under `risk@0`, a predicate that is not a role, not `risk__…`, not one of the four `alternatives@0` words and not
    modal, and whose wording or negative has the key of a risk template, gets the fallback and no negative.
  - A modal predicate gets its modal form and no negative.
- **`policyNouns`.**
  - The base noun is the declared noun, else the sort's name. It is kept when it is ASCII letter words, none of them
    reserved once lower-cased, and the lower-cased noun is no predicate's or constant's name; otherwise the noun is
    the fallback `entity of sort "s"`.
  - Every noun whose key is shared becomes the fallback.
  - A profile-fixed noun, `severity`, replaces the result.
- **`policySpellings`.**
  - The bare name is used when it is lower-case letters, not reserved and not `is` or `has`; otherwise the quoted
    name. A constant with a declared display form starts quoted.
  - A declared form is kept when it is ASCII letter words, has no reserved word other than `the`, has no selected
    noun's key, and is the only such declared form with its key.
  - Then, until nothing changes, every declared constant that is not quoted and shares a spelling key with another
    constant is quoted. A value's spelling keys are those of itself, of `The …` when it begins with `the `, and of
    `the …` when it is lower-case letters.

**V6** (`Lexicon.policyFailures`, D1). Each of the following is a failure:

- `("V6", "predicate", p)`: the selected wording of a predicate `p` is neither Python's choice nor
  `fallbackWording p k`;
- `("V6", "negative", p)`: a selected negative of `p` is not Python's negative for `p`, or `p`'s selected wording is
  not Python's;
- `("V6", "sort", s)`: the selected noun of `s` is neither Python's nor `entity of sort "s"`;
- `("V6", "constant", c)`: the selected spelling of `c` is neither Python's nor the quoted name.

`Lexicon.policyOk E O L` holds when there is none.

The freedom V6 leaves is the conservative one: a producer may write any symbol in its quoted form, and may omit a
negative. It cannot select a wording, noun or spelling that Python refuses. Nothing becomes a warning, so V6 widens
nothing Python refuses today (S3 D14, R4).

**What V6 does not cover.**

- *Letters.* A label is a run of capitals with a number, so no letter makes a word a label. Two sorts sharing a letter
  give two derivations, which the per-sentence check refuses. `_fluent_variable_letters` is ported in the stub only
  to recompute `lexicon_id` (Q2).
- *Aliases.* V2 already requires exactly the profile-fixed ones.
- *`rights@0` wordings.* V2 already fails them (S3 Q5).

**Measured parity** (pt1). For each of the 22 use-case rows of the lexicon report, the stub built Python's
selection with the port. It added the letters and the profile aliases, wrote the export with the display identity
of D6, and digested it. 18 rows give Python's recorded `lexicon_id`. That covers the agent-policy norms
environments, the alternatives and risk use cases, the 14th-amendment, constitution and news overlays, and the
math closure environment. The other 4 are the environments the boundary refuses (2.2), so no lexicon is read for
them. The 17 round-trip configurations of the report are built in Python and were not reproduced (Q3).

### 2.4 Where V6 is checked, and why not inside `Lexicon.valid`

S3 D14 made V6 a condition of `Lexicon.valid`. This draft keeps its content and moves it beside `valid` (D2, D3),
for three reasons.

1. **The senses projection.** `senseDecl` declares each sense with its selected wording, and `project` calls
   `Lexicon.failures` on the projection (`ve-senses-int`, `lean/VE/Senses/Project.lean:133–135`, `:239`). The
   policy refuses these wordings: lx30 computes the joke fixture's projection. `{0} is funny` carries
   `SYMBOL_COLLISION`, because the other sense owns the head `funny`. `{0} is funny (meaning strange)` carries
   `PHRASE_SYNTAX`, `SYMBOL_COLLISION` and `UNARY_MODIFIER`. Python's choice is the quoted fallback for all three
   senses. With V6 inside `valid`, `project` would fail on every document that uses a word of two senses, against
   DRI ruling 7.
2. **Extensions.** `Extends` requires `valid` on both sides (S3 5.4). V6 is not monotone: a new predicate whose head
   is a word of an old wording makes the old wording collide. Inside `valid`, V6 would cut `grammar_extension` and
   the senses' `project_extends` short on growth that is a true grammar extension.
3. **What V6 is.** V1 to V5 are what a reading depends on. V6 is the producer's policy, a reader-protection check
   that DRI answer 5 puts in Lean because it changes acceptance. It belongs where the producer's lexicon enters: the
   request.

So `read`, `admit`, `EnglishOneReading` and every S2, S3 and senses statement keep their text. V6 is run by the
request functions of 5.3, which the modes call, on the request's own `E`, `O` and `L`. The senses mode runs it on
the document's own environment and lexicon before it projects. The projection's own validity stays V1 to V5,
checked by `project` as before.

### 2.5 Admission, candidates, senses

- **`admitRequest E O L b s`** is `admit E O L b s` when `L.policyOk E O`, and otherwise
  `.refused (.invalidGrammar .lexicon)`. `english.read` in authoring mode runs it. Translation mode runs `translate`
  under the same V6 guard.
- **`checkRequest E O L b rs cs`** is `firstChecked E O L b rs cs` when `L.policyOk E O`, and otherwise `none`.
  `english.check` runs it. The renderer displays the candidate it names, or the source when there is none.
- **`sensesRequest D E L b s`** is `readWithSenses D E L b s` when `L.policyOk E {}`, and otherwise
  `.invalidGrammar .lexicon`. `senses.read` runs it, on the document's own environment and lexicon.
- **Obligations.** The `one` response lists each obligation with its premises and the text the relay raises if no
  checked derivation is found (4.2). The relay proves each one with the existing entailment operation, as S3 D10
  split the work.

### 2.6 Codes, classes and texts

Section 4 gives the tables. Lean's codes and texts are shown, and each response that is not `one` names its class
(D9). The class table, the texts that take parameters, and the advice table are Lean data. `english.grammar` exports
them, so the editor needs no copy.

### 2.7 The service

**Modes.** `ve_service` gains three constructors of `Mode`, each pinned by an `rfl` theorem as `runMode_route` is.

| Mode | Case | Result |
|---|---|---|
| `english.read` | `{id, environment, overlay?, lexicon, source, mode, cap}` (S2 4.3) | the response of 4.4 |
| `english.grammar` | `{id, environment, overlay?, lexicon}` | the export of S3's `grammarCase`, plus `codes` (the class table) and `advice` (the advice rows), or `invalidGrammar` when V1 to V6 refuse the lexicon |
| `english.check` | `{id, environment, overlay?, lexicon, formulas, marks, candidates}` | `{"index": i}` or `{}`, with the five identities other than `source_sha256` |

`english.check` decodes each formula with `EFormula.decode` (5.3), which refuses a formula it cannot decode as
`InvalidInput`. It requires one mark per formula.

**The cache** (D14). The prepared grammar is kept per process, keyed by `environment_id`, `overlay_digest` (empty
without an overlay) and `lexicon_id`. With the build, which fixes `actions_version`, these cover every input of
preparation, since the overlay changes the declared wordings that V2, V4 and V6 read. The response is a function of
the request alone, and a cache hit only skips work (ev3, ev3b). This is the handle pattern of lean-first batch 2,
already on `main`.

**Retired.** The `ve_english_route` executable and its transport in `ve/backends/lean.py` are deleted. ev2 checks the
service mode against S2's route fixtures first.

### 2.8 The relay and the comparator (Python)

- **Admission** (`parse_english`, `parse_english_with_metadata`, `parse_english_argument`). The relay sends the
  environment, the overlay, the producer's lexicon and the source to `english.read`. For any status but `one`, it
  raises `ERRORS[response["class"]](response["text"])`, with the span of 4.4. For `one`, it calls
  `prove_entailment(env, premises, conclusion)` for each obligation and raises `SyntaxError(obligation["unproved"])`
  when the result is not `Found`. `parse_english_argument` builds its claim graph from the obligations'
  premises and the certificates. `_check_conclusions`' premise computation goes; its entailment call is what the
  relay keeps.
- **Rendering.** `render_english` sends, for each formula, its three candidate sentences (with `Therefore ` when
  marked) to `english.check` and keeps the named one, or raises the existing `ValueError`. It then sends the
  assembled document as the one candidate for all formulas and marks. `parse_english_with_metadata` sends the
  rendering as the one candidate, and displays the source when the answer is `{}`. Python's re-parse of its own
  renderings (`english.py:833`, `:855`, `:1780`) is deleted.
- **Structure.** `_parse_english_document(..., _with_structure=True)` (`natural.py:63`) takes the sentence spans
  from the response (D11) and computes paragraph breaks from the source between them, as `english.py:1726–1727` does
  today.
- **The comparator** (D15). With `VE_ENGLISH_COMPARATOR=1`, which the suite, the corpus harness and the nightly
  run set and which is never set by default, the relay also runs `_python_reading` and Python's premise check. It
  writes one record per call: the six identities, Lean's outcome (returned), Python's outcome (compared), and the
  classes of S2 4.5 under S3 2.11's correspondence. The record is never returned, and its failure never raises.
  Without the switch, no admission entry point calls Python's parser (ev6).
- **What Python keeps.** File I/O and UTF-8 decoding; spans for display, from Lean's offsets; the producer of the
  lexicon (D16); the renderer as a producer of candidates; the nearest-wording suggestion as editor help over Lean's
  tokens; the `accept_suggested_vocabulary` consent gate; and, until E3, the statement layers that construct
  `EnglishParser` themselves.

### 2.9 The deletion ledger

`docs/lean-first/e2/LEDGER.md` has one row per decision site, each with a disposition: *owned by Lean* (the Lean
check named), *comparator* (off the admission path, deleted in the next stage), or *kept* (its caller named).

| Site | Disposition |
|---|---|
| `english.py:1673–1695` `_python_reading`: hand parser, Lark audit, `check_document` | comparator |
| `english.py:1718–1722` `dispatch.shadowed('english.admission', …)` | owned by Lean: `admitRequest` via the relay; `SHADOW_ONLY` entry removed |
| `english.py:1712–1713` the source byte limit | owned by Lean: `sourceTooLong` |
| `english.py:1765–1766` `A conclusion needs an earlier premise.` | owned by Lean: `noPremise` (`ConclusionWithoutPremise`) |
| `english.py:1767–1770`, `:1817–1819` the entailment refusal | kept (relay; D10 of S3): the text is Lean's `unproved` |
| `english.py:1811–1812`, `:1816` the premises of each marked conclusion | owned by Lean: `obligations` |
| `english.py:833`, `:855`, `:1780` re-parse of renderings | owned by Lean: `checkRequest` |
| `english.py:888–1636` `EnglishParser` | comparator for admission; kept for `norm_english.py` and `norm_defaults_english.py` until E3 |
| `surface/unambiguity.py` `require_unique_derivation`, `require_correspondence` | comparator for admission; kept for the statement layers that call them until E3 |
| `english.py:230–527` `EnglishVocabulary` selection, `_RESERVED` | kept: the producer, checked by V6 (Q1) |
| `backends/english_lean.py` `CLASSES`, `STATUS_CLASSES`, `_verdict` | owned by Lean: the class table (4.2); the comparator keeps its class tolerance for `RelativeForm` |
| `backends/english_lean.py` `_transport` over `ve_english_route` | owned by Lean: the `ve_service` mode |
| `english.py:1868–2022` `english_lark_grammar` | comparator; if an editor reads it, regenerated from the `english.grammar` export (LEAN-FIRST 5.2) |
| `conformance/english_lean_{engine,lexer,lexicon}.py` | deleted once nothing compares against them (LEAN-FIRST 6.3) |

`tools/relay_lint.py` runs over the admission path of `ve/english.py` and `ve/backends/english_lean.py`.

### 2.10 Evidence

These are the harness items of E2.5, which GE2 reads.

- **G3 at the dispatched boundary.** S3 2.11's comparison on every sealed corpus text of every profile, under
  Python authority, with the per-profile delta of S3. It compares verdict class, formulas, canonical text, marks and
  witness multiplicity, and lists the three classes of S3 2.11.
- **The reverse corpus.** Texts are sampled from the `english.grammar` export of every corpus lexicon, with spacing
  and word-split mutants, and compared against the hand parser and Lark.
- **The lexicon mutation replay.** S3.5's mutations are run, and V6 is added to the check: a mutant that V1 to V6
  refuse is refused, and a mutant they accept changes no corpus formula.
- **The port parity harness (pt1 at scale).** For every corpus environment, Python's `EnglishVocabulary` and the
  port's choice are compared symbol by symbol. The mutation set is the corpus environments with each predicate's
  wording replaced in turn by each wording of 8.1, and each sort's noun and each constant's display form replaced by
  those of lx27 and lx28. A difference is a port defect or a signed `DELTA.md` row.
- **The three-way differential** on the 57,765 core texts, with fourteen fresh date seeds of the generated streams.
- **Coverage.** Every lexical family and every fixed rule of every profile occurs in at least one compared text;
  the report lists the rules that the corpora do not reach and the texts written for them.
- **Readability.** Each item of the readability evaluation keeps its verdict and keeps or improves its message.
- **The corpus A/B** of GE2 item 3, between the base commit and the batch head.

### 2.11 Identities, and what the senses layer relies on

- `Lexicon`, `Overlay`, the wire form `ve.english-lexicon@1` and the preimage of each of the six identities are
  unchanged. D6 changes the check against the lexicon's `environment_id`, not what is hashed.
- `actions_version` rises with E2. The lock lists `Policy.lean`, `Advice.lean` and every edited definition file.
- Every new field has a default. A producer that sets none gets S3's `Env`, and V6 reads the defaults, the way
  Python's policy reads an absent plural or a non-suggested entry.
- The senses layer reads `Env`, `Overlay`, `Lexicon` and the identities, which are unchanged, and its projections
  are not checked against V6 (2.4). Its mode adds V6 on its own inputs, a check the document's own lexicon passes
  whenever Python's producer made it (pt1).

### 2.12 What is trusted, proved and tested in this stage

| Layer | Items added |
|---|---|
| Trusted definitions | the port (`Policy.lean`: word lists, pattern tables, scanners, lint, acceptance, selection, V6); `displayJson`; the boundary extension (a link to existing decoders); `admitRequest`, `checkRequest`, `sensesRequest`; `EFormula.decode`; the class table, the texts and the advice table |
| Proved | `policy_iff_no_failure`, `policy_selection`, `admitRequest_ok`, `admitRequest_exact`, `admitRequest_policy`, `checkRequest_some`, `sensesRequest_policy`, `codeClasses_total`, `decode_encode`, the three `runMode` equations |
| Checked per request | V6 on the request's own inputs; the lexicon's identity against the display environment |
| Tested only | the port against Python (pt1, the parity harness); the boundary extension (ev14); the cache's transparency (ev3, ev3b); the relay and the comparator (rl1 to rl8, ev6, ev7); the corpus evidence; latency |
| Outside | the proof of each obligation (the entailment operation); the producer's choice beyond V6; `rights@0` wordings; letters |

## 3. English: one reading each

E2 adds no wording to the grammar, and every form of S3 3.1 keeps its meaning. What changes is who decides, and
the texts shown.

**Claim sentences.** From the flip, a record of an admitted document carries C2 with the six identities, C4 when a
mark is present, and C5 (S3 3.2) when every obligation was proved.

**The texts added** are those of 4.2. Each says what happened, in the reader's terms, and names the sentence from
one.

**The theorems, in plain words.**

| Statement | Plain English | It does not say |
|---|---|---|
| `policy_iff_no_failure` | The vocabulary policy passes exactly when it reports no failure. | |
| `policy_selection` | If the policy passes, every selected wording, noun and spelling is Python's choice or the quoted form, and every selected negative is Python's beside Python's wording. | that Python's choice is the port's on every environment: that is tested (pt1) |
| `admitRequest_ok` | If admission succeeds, the vocabulary passed the policy, the text has one reading per sentence, the obligations are those of the reading, and each has a premise. | that an obligation is provable |
| `admitRequest_exact` | Admission succeeds exactly when the vocabulary passes the policy, the reader returns the reading, and every marked sentence has an earlier unmarked one. | |
| `admitRequest_policy` | A vocabulary that fails the policy is refused before any text is read. | |
| `checkRequest_some` | If the check of candidates names one, the vocabulary passed the policy and that candidate is the first that reads back as exactly the given formulas and marks. | that some candidate passes |
| `sensesRequest_policy` | When the document's own vocabulary passes the policy, the senses mode is the senses reader. | anything about the projection's vocabulary |
| `codeClasses_total` | Every rejection code has a class. | |
| `decode_encode` | Decoding the wire form of a formula gives the formula back. | that every wire form decodes |

## 4. Diagnostics

### 4.1 Statuses

S2 4.1 and S3 4.1 stand. From the flip, the public class is the response's `class` (D9).

### 4.2 Codes, classes and texts

**The class table** (`codeClasses`, 5.3). Each code maps to the class the relay raises.

| Codes | Class |
|---|---|
| `SourceTooLong`, `TextTooLong`, `NestingLimit`, `NumeralBound`, `Budget` | `ResourceLimit` |
| `BadCharacter`, `OpenQuote`, `BadNumeral`, `EmptyDocument`, `EmptySentence`, `Unterminated`, `BadSpacing`, `UnboundReference`, `ShadowedName`, `SortMismatch`, `MarkerDepth`, `CoefficientNotNumeral`, `PronounUnresolved`, `BlockedWording`, `CoordinationRepeated`, `CoordinationForm`, `NaturalScoped`, `RelativeForm`, `NoDerivation`, `ConclusionWithoutPremise`, `ConclusionNotDerived` | `SyntaxError` |
| `Ambiguous` | `AmbiguousDerivation` |
| `IllTyped` | `TypeMismatch` (D10) |
| `InvalidGrammar`, `Internal` | `CheckerUnavailable` |

`RelativeForm` was `SyntaxError` or a typing class depending on the text (`english_lean.py:64`); it is
`SyntaxError`. Where Python raised another class, that is a `wording` row, and the comparator keeps the tolerance.

**Texts added.** The texts of `rejectText` (S3 build, `Run.lean:40–69`) stand. E2 adds the following.

| Code | Text (computed for cn3 and an obligation of sentence 2) | Python today |
|---|---|---|
| `ConclusionWithoutPremise` | `Sentence 1 is marked as a conclusion, and no earlier sentence is a premise.` | `A conclusion needs an earlier premise.` |
| `ConclusionNotDerived` (the obligation's `unproved`) | `Sentence 2 is marked as a conclusion, and no checked derivation from the earlier premises was found.` | `The marked conclusion has no checked derivation from earlier premises: <status>` |
| `InvalidGrammar` with a V6 failure | S3's text, with `failure` `["V6", kind, name]` | the producer's own `VEError` for an overlay entry (`english.py:517`), or no error (the quoted fallback) |

Every text that differs from Python's is a `wording` row of `DELTA.md`.

### 4.3 Advice for a sentence without a reading

S3 4.3 stands, with the two rows it left as obligations. The table in order is:

| Id | Profile | Patterns | Text |
|---|---|---|---|
| `risk-may` … `risk-condition` | `risk@0` | S3 4.3 | S3 4.3 |
| `alternatives-causes` … `alternatives-inaction` | `alternatives@0` | S3 4.3 | S3 4.3 |
| `alternatives-human-harm` | `alternatives@0` | `allows a harm to a human being to happen` | `Write the long form: there is a harm such that both that harm is a harm to a human being and that action allows that harm to happen.` (`english.py:1263–1264`) |
| `alternatives-person` | `alternatives@0` | `allows` *w* `to` *w′*, where *w* is any word and *w′* any word but `happen` | `Permission for a person uses the W1 'may' wording, not causal 'allows'.` (`:1265–1266`) |
| `plural-pronoun`, `negated-existential` | any | S3 4.3 | S3 4.3 |

The free words of `alternatives-person` match a word token and no other token. Python's test is
`allows\s+\w+\s+to\s+\w+` on the cut phrase and not `… to happen` at its end. The port compares words, and advice
decides nothing, so a difference is a `wording` row.

### 4.4 The responses

Every response keeps S2 4.3's fields and the six identities, with these additions.

| Status | Added |
|---|---|
| `one` | `obligations`: `[{"conclusion": i, "premises": [j, …], "unproved": text}]`, empty without marks; `spans`: one `[start, end)` per sentence, in code points of the source as sent |
| `rejected` | `class`; `span`, the sentence's `[start, end)` in code points, or the offending character's for a lexical rejection; code `ConclusionWithoutPremise` with `sentence` 0 |
| `none`, `many`, `budget` | `class`; `span`; for `none`, `advice` (`{"id", "text"}`) when the table gives one |
| `invalidGrammar` | `class`; `failure` may be a V6 failure |

`english.check` returns `{"index": i}` or `{}` with five identities. `english.grammar` adds `codes` (pairs of code and
class) and `advice` (the rows of 4.3, with the profile and patterns).

## 5. Lean: definitions and the exact statements

### 5.1 Modules and conventions

Conventions are as in S2 5.1. The stub elaborated everything below in one namespace, with the three new fields held
beside `Env` (section 12).

| Module | Change |
|---|---|
| `Lexicon.lean` | the fields of 2.2; `Env.roles`, `Env.pluralOf`, `Env.suggestedPred` |
| `Policy.lean` (new) | 5.2 |
| `Advice.lean` (new) | the advice table and `advice` (5.3) |
| `Encode.lean` | the decoding of the new fields; `EFormula.decode`; `displayJson` |
| `Read.lean` | `admitRequest`, `checkRequest` |
| `Run.lean` | the modes' cases; the class table and texts; D6 in `decodeCase`; the boundary of D7 |
| `Service/Protocol.lean` | three constructors of `Mode` with their `rfl` theorems |
| `ResponseShape/Encoders.lean` | `runMode_fits` for the three modes |
| `Senses/Read.lean` | `sensesRequest`; the senses mode calls it |

### 5.2 The fields, and `Policy.lean`

```lean
namespace VE.EnglishGrammar

-- SortDecl gains:  plural : Option String := none
-- PredDecl gains:  suggested : Bool := false
-- AltBlock gains:  optional : List String := []        -- inaction, taken, proximate, where present

def Env.roles (E : Env) : List String :=
  match E.alternatives with
  | some B => [B.available, B.leadsTo] ++ B.optional
  | none => []
def Env.pluralOf (E : Env) (s : String) : Option String := (E.sorts.find? (·.name == s)).bind (·.plural)
def Env.suggestedPred (E : Env) (p : String) : Bool := ((E.predicate? p).map (·.suggested)).getD false

/-! Word lists (printer.py:93–105, english.py:31–49, :214, :283–285, :342; english_phrases.py:7–8) -/
def wordList (s : String) : List String := splitWs s
def logicalWords : List String := wordList "all any every some each no none not never neither nor
    and or both either if then unless except without only exists forall implies
    true false equal equals there such that case condition for at least most
    exactly does do must may can cannot should shall will would whenever when
    implies iff otherwise always sometimes one two three four five six seven
    eight nine ten a an the lacks nothing nobody everything everybody just solely
    many several another but plus few might"
def closureWords : List String := wordList "reachable reachability steps satisfying zero more from"
def auxiliaries : List String := wordList "is are was were be been being gets got"
def converseEndings : List String := wordList "by to of from with for"
def ordinals : List String := wordList "first second third fourth fifth sixth seventh eighth"
def extraReserved : List String := wordList "this it holds impossible classified recorded relation entity sort named
    first second following hold who where step steps source destination from reachable using starting ending
    definition end therefore so hence" ++ ordinals
def reserved : List String := logicalWords ++ extraReserved
def comparisonWords : List String := wordList "less more than least most same"
def contentStop : List String := wordList "a an the is was are be been being has have its in on at to of for from by
    with and or as that this recorded predicate first second"
def mechanicalVerbs : List String := wordList "owns audits undermines performs follows benefits outranks exceeds"
def eligibleCodes : List String := ["LOGICAL_WORD", "PHRASE_SYNTAX", "UNARY_MODIFIER", "TEMPLATE_SHAPE",
  "TEMPLATE_LENGTH", "SORT_NOUN", "SYMBOL_COLLISION", "BINARY_CONVERSE", "BINARY_AUXILIARY", "BINARY_VERB"]
def boundaryWords : List String := wordList "is does not and or if then that who which both either every some for"
def blockedWords : List String := wordList "than by no never longer neither nor without true false equals equal"
def naryHeads : List String := wordList "reports records has is at maps relates links"
def altWords : List String := ["avoidable", "unavoidable", "allows", "prevents"]
def riskTemplates : List String :=
  ["{0} might lead to {1}", "{0} cannot lead to {1}", "{0} might not lead to {1}", "{0} is {1}",
   "{0} is {1} or worse", "{0} has a less severe worst case than {1}", "{0} is more severe than {1}",
   "{0} might prevent {1}", "{0} does not lead to {1}", "{0} may lead to {1}", "{0} could lead to {1}",
   "{0} risks {1}", "{0} is likely to lead to {1}", "{0} increases the risk of {1}",
   "{0} certainly leads to {1}", "{0} prevents {1}", "{0} is safer than {1}"]

/-! The two pattern tables of the rescue (english.py:31–43) -/
inductive PatWord where
  | lit (w : String)
  | adj
  deriving DecidableEq, Repr
def lits (s : String) : List PatWord := (s.splitOn " ").map PatWord.lit
def complementPatterns : List (List PatWord) :=
  [lits "is subject to the jurisdiction of the United States", lits "is a citizen of the United States",
   lits "was born in the United States", lits "was naturalized in the United States"] ++
  (["fully", "newly", "currently", "publicly"].map fun a => [.lit "is", .lit a, .adj]) ++
  [[.lit "is", .adj, .lit "in", .lit "good", .lit "standing"], [.lit "is", .adj, .lit "under", .lit "review"]]
def activePatterns : List (List PatWord) :=
  ["affords due process of law to", "denies the equal protection of the laws to", "reports to",
   "contributes to", "responds to", "communicates with", "collaborates with", "has access to",
   "has authority over", "has responsibility for"].map lits

/-! Character classes and scanners -/
def isLower (c : Char) : Bool := 'a' ≤ c && c ≤ 'z'
def isUpper (c : Char) : Bool := 'A' ≤ c && c ≤ 'Z'
def isLetter (c : Char) : Bool := isLower c || isUpper c
def isDigit (c : Char) : Bool := '0' ≤ c && c ≤ '9'
def isTokChar (c : Char) : Bool := isLetter c || isDigit c || c == '_'
def isW (c : Char) : Bool := isTokChar c                                   -- Python's `\w`, on ASCII
-- `lowerWord` (a non-empty run of `a` to `z`) is `Rules.lean:210`'s

/-- The maximal runs of characters satisfying `p` (`re.findall('[a-z]+', s)` for `isLower`). -/
def runs (p : Char → Bool) (s : String) : List String :=
  let rec go : List Char → List Char → List String
    | [], cur => if cur.isEmpty then [] else [String.mk cur.reverse]
    | c :: cs, cur => if p c then go cs (c :: cur) else
        if cur.isEmpty then go cs [] else String.mk cur.reverse :: go cs []
  go s.toList []

/-- `_TOKENS.findall` (printer.py:102): `[A-Za-z][A-Za-z0-9_]*(?:-[A-Za-z]+)?`. -/
def tokens (s : String) : List String :=
  let rec go : Nat → List Char → List String
    | 0, _ => []
    | _ + 1, [] => []
    | n + 1, c :: rest =>
      if isLetter c then
        let body := rest.takeWhile isTokChar
        let after := rest.drop body.length
        match after with
        | '-' :: d :: more =>
          if isLetter d then
            let ls := (d :: more).takeWhile isLetter
            String.mk (c :: body ++ '-' :: ls) :: go n ((d :: more).drop ls.length)
          else String.mk (c :: body) :: go n after
        | _ => String.mk (c :: body) :: go n after
      else go n rest
  go (s.length + 1) s.toList

/-- Python's `str.lower` on what `[a-z]+` can see: ASCII capitals, the Kelvin sign, `İ`. -/
def pyLower (s : String) : String :=
  String.join (s.toList.map fun c =>
    if isUpper c then String.singleton (Char.ofNat (c.toNat + 32))
    else if c == '\u212A' then "k"                          -- the Kelvin sign
    else if c == '\u0130' then "i\u0307"                     -- `İ`: `i` and a combining dot
    else String.singleton c)
def asciiLower (s : String) : String := s.map fun c => if isUpper c then Char.ofNat (c.toNat + 32) else c

/-- `re.search(r'\b' + re.escape(tok) + r'\b', phrase)`, with `\w` on ASCII. -/
def wordOccurs (tok phrase : String) : Bool :=
  let t := tok.toList
  let p := phrase.toList
  let w (i : Nat) : Bool := match p[i]? with | some c => isW c | none => false
  let wb (i : Nat) : Bool := if i == 0 then false else w (i - 1)
  !t.isEmpty && (List.range (p.length + 1)).any fun i =>
    i + t.length ≤ p.length && (p.drop i).take t.length == t &&
    wb i != w i && wb (i + t.length) != w (i + t.length)
def wordOccursI (tok phrase : String) : Bool := wordOccurs (asciiLower tok) (asciiLower phrase)

/-- `_content_words` (english.py:217–219). -/
def contentWords (text : String) : List String :=
  ((runs isLower (pyLower text)).filter (!contentStop.contains ·)).eraseDups.map fun w =>
    if w.endsWith "ing" then w.dropRight 3 else if w.endsWith "ed" then w.dropRight 2
    else if w.endsWith "s" then w.dropRight 1 else w

def wordsPhrase (s : String) : Bool := (s.splitOn " ").all lowerWord        -- `_WORDS`
def variableWord (w : String) : Bool :=                                      -- `_VARIABLE`
  match w.toList with
  | 'x' :: ds => ds.all isDigit
  | cs =>
    let up := cs.takeWhile isUpper
    !up.isEmpty && (cs.drop up.length).all isDigit

/-- `_template_head` (printer.py:176–180). -/
def templateHead (value : String) (k : Nat) : Option String :=
  let words := tokens value
  let words := if k == 1 && words.head? == some "is" then words.drop 1 else words
  words.head?

/-- Python's strict wording (printer.py:190–194), for every name. -/
def strictWording (name : String) (k : Nat) : String :=
  if k == 1 then "{0} is " ++ name
  else if k == 2 then "{0} " ++ name ++ " {1}"
  else "{0} has recorded relation " ++ name ++ " with " ++ " and ".intercalate
    ((List.range (k - 1)).map fun i =>
      "argument " ++ (["two", "three", "four", "five", "six"].getD i "") ++ " {" ++ toString (i + 1) ++ "}")

/-- The phrase of `\{0\} (.+)` (one argument) or `\{0\} (.+) \{1\}` (two); `.` excludes a line break. -/
def shapePhrase (v : String) (k : Nat) : Option String :=
  if !v.startsWith "{0} " then none else
  let rest := v.drop 4
  if k == 1 then (if rest.isEmpty || rest.contains '\n' then none else some rest)
  else if rest.endsWith " {1}" then
    let mid := rest.dropRight 4
    if mid.isEmpty || mid.contains '\n' then none else some mid
  else none

/-- `re.findall(r"\{[^{}]*\}", v)`. -/
def braceSlots (v : String) : List String :=
  let rec go : Nat → List Char → List String
    | 0, _ => []
    | _ + 1, [] => []
    | n + 1, c :: rest =>
      if c == '{' then
        let inner := rest.takeWhile fun d => d != '{' && d != '}'
        match rest.drop inner.length with
        | '}' :: more => String.mk ('{' :: inner ++ ['}']) :: go n more
        | _ => go n rest
      else go n rest
  go (v.length + 1) v.toList

/-- `re.split(r"\{[0-5]\}", v)`. -/
def splitSlots (v : String) : List String :=
  let rec go : Nat → List Char → List Char → List String
    | 0, _, cur => [String.mk cur.reverse]
    | _ + 1, [], cur => [String.mk cur.reverse]
    | n + 1, '{' :: d :: '}' :: rest, cur =>
      if '0' ≤ d && d ≤ '5' then String.mk cur.reverse :: go n rest [] else go n (d :: '}' :: rest) ('{' :: cur)
    | n + 1, c :: rest, cur => go n rest (c :: cur)
  go (v.length + 1) v.toList []

/-- `(?: [a-z]+)+ ?` (`trail`) and `(?: [a-z]+)+`, as full matches. -/
def connector (s : String) (trail : Bool) : Bool :=
  let s := if trail && s.endsWith " " && s.length ≥ 2 && !(s.dropRight 1).endsWith " " then s.dropRight 1 else s
  s.startsWith " " && ((s.drop 1).splitOn " ").all lowerWord

/-- `template_parts` (`ve/surface/nary.py:13–33`). -/
def templateParts (v : String) (k : Nat) : Option (List String) :=
  if braceSlots v != (List.range k).map (fun i => "{" ++ toString i ++ "}") then none else
  let parts := splitSlots v
  if parts.length != k + 1 then none else
  let mids := (parts.drop 1).take (k - 1)
  if !mids.all (·.startsWith " ") then none else
  let first := parts.headD ""
  if !(first.isEmpty || first == "the value of ") then none else
  if !mids.all (connector · true) then none else
  let last := parts.getLastD ""
  if !(last.isEmpty || connector last false) then none else
  if !((splitWs (parts.getD 1 "")).any naryHeads.contains || first.startsWith "the value of ") then none else
  some parts

/-- A phrase against a pattern: `some adjective?` when it matches. -/
def matchPattern (phrase : String) (pat : List PatWord) : Option (Option String) :=
  let parts := phrase.splitOn " "
  if parts.length != pat.length then none
  else if (parts.zip pat).all (fun (w, p) => match p with | .lit s => w == s | .adj => lowerWord w) then
    some ((parts.zip pat).findSome? fun (w, p) => match p with | .adj => some w | _ => none)
  else none

/-- `unary_phrase` (english_phrases.py:23–31). -/
def unaryPhrase (t : String) : Option String :=
  if t.length > 80 || !t.startsWith "{0} " then none else
  let rest := (t.drop 4)
  if asciiLower (rest.take 3) != "is " then none else
  let body := rest.drop 3
  let phraseOk (s : String) : Bool :=
    let parts := (s.splitOn " ").flatMap (·.splitOn "-")
    !s.isEmpty && parts.all fun w => match w.toList with
      | c :: cs => isLetter c && cs.all isTokChar
      | [] => false
  let candidates : List String :=
    (if asciiLower (body.take 2) == "a " then [body.drop 2] else []) ++
    (if asciiLower (body.take 3) == "an " then [body.drop 3] else []) ++ [body]
  match candidates.find? phraseOk with
  | none => none
  | some phrase =>
    let low := asciiLower phrase
    if low == "a" || low == "an" || (splitWs low).any (fun w => boundaryWords.contains w || blockedWords.contains w)
    then none else some phrase

/-! Python's vocabulary policy (english.py:230–527, printer.py:183–338) -/
def sortNouns (E : Env) (O : Overlay) (s : SortDecl) : List String :=
  match E.declaredNoun O s.name with
  | some n => [n] ++ (E.pluralOf s.name).toList
  | none => []

/-- The lint codes of a declared wording `value` of predicate `name` (`_NaturalVocabulary`). -/
def lintCodes (E : Env) (O : Overlay) (name value : String) (k : Nat) : List String :=
  let predNames := E.predicates.map (·.name)
  let names := E.sorts.map (·.name) ++ predNames ++ E.constants.map (·.name)
  let heads : List (String × String) := E.predicates.filterMap fun d =>
    (templateHead ((E.declaredWording O d.name).getD (strictWording d.name d.arity)) d.arity).map (·, d.name)
  let nounTexts : List (String × String) := E.sorts.flatMap fun s => (sortNouns E O s).map (·, s.name)
  let owned (w : String) : Bool :=
    names.any (fun x => x == w && x != name) || heads.any (fun (h, p) => h == w && p != name) ||
    nounTexts.any fun (n, s) => (tokens n).getLast? == some w && s != name
  let predicateHeads := predNames ++ heads.map (·.1)
  let negatedHeads := ["un", "non", "un-", "non-"].flatMap fun pre => predicateHeads.map (pre ++ ·)
  let nounKeys := E.sorts.map (·.name) ++ nounTexts.map (·.1)
  let forbidden := logicalWords ++ (if E.profiles.contains "closure@0" then closureWords else [])
  let phraseCodes (phrase : String) (conn : Bool) : List String :=
    let wds := tokens phrase
    let forb := if conn && phrase == "at" then forbidden.filter (· != "at") else forbidden
    (if wordsPhrase phrase then [] else ["PHRASE_SYNTAX"]) ++
    (if wds.any forb.contains then ["LOGICAL_WORD"] else []) ++
    (if wds.any variableWord then ["VARIABLE_TOKEN"] else []) ++
    (if wds.any owned then ["SYMBOL_COLLISION"] else []) ++
    (if wds.any negatedHeads.contains then ["NEGATED_HEAD"] else [])
  let dup := if (E.predicates.filter fun d => E.declaredWording O d.name == some value).length > 1
    then ["DUPLICATE_TEMPLATE"] else []
  if k > 2 then
    let len := if value.length > 160 || (splitWs value).length > 24 then ["TEMPLATE_LENGTH"] else []
    match templateParts value k with
    | none => dup ++ ["TEMPLATE_SHAPE"] ++ len
    | some parts => dup ++ len ++ (parts.drop 1).flatMap fun ph =>
        let s := stripWs ph
        if s.isEmpty then [] else phraseCodes s true
  else
    let tw := tokens value
    let len := if value.length > 80 || (splitWs value).length > 8 then ["TEMPLATE_LENGTH"] else []
    let sortNoun := if nounKeys.any (fun n => let ts := tokens n; !ts.isEmpty &&
        (List.range (tw.length + 1)).any fun i => (tw.drop i).take ts.length == ts)
      then ["SORT_NOUN"] else []
    let shape := match shapePhrase value k with
      | none => ["TEMPLATE_SHAPE"]
      | some phrase =>
        let pw := splitWs phrase
        phraseCodes phrase false ++
        (if k == 1 then
          (if pw.head? != some "is" || pw.length < 2 then ["TEMPLATE_SHAPE"]
           else if pw.length != 2 then ["UNARY_MODIFIER"] else [])
         else match pw.head?, pw.getLast? with
          | some first, some last =>
            (if auxiliaries.contains first then ["BINARY_AUXILIARY"] else []) ++
            (if converseEndings.contains last then ["BINARY_CONVERSE"] else []) ++
            (if !first.endsWith "s" then ["BINARY_VERB"] else [])
          | _, _ => [])
    (len ++ sortNoun ++ dup ++ shape).eraseDups

/-- Whether Python accepts the declared wording of `name` (english.py:264–372). -/
def acceptsDeclared (E : Env) (O : Overlay) (name : String) : Bool :=
  match E.predicate? name, E.declaredWording O name with
  | some d, some t =>
    let k := d.arity
    let codes := lintCodes E O name t k
    if k > 2 then codes.isEmpty else
    let idiom := (idioms k).contains t
    let p0 := if t.startsWith "{0} " then t.drop 4 else t
    let phrase := if k == 1 then p0 else if p0.endsWith " {1}" then p0.dropRight 4 else p0
    let shaped := t == "{0} " ++ phrase ++ (if k == 1 then "" else " {1}")
    let others := E.predicates.filter (·.name != name)
    let collision :=
      ((E.predicates.map (·.name) ++ E.constants.map (·.name)).filter (· != name)).any (wordOccurs · phrase) ||
      others.any fun d2 => match templateHead ((E.declaredWording O d2.name).getD "") d2.arity with
        | some h => !["is", "was", "a", "an"].contains h && wordOccurs h phrase
        | none => false
    let isHeads := E.predicates.filterMap fun d2 => match E.declaredWording O d2.name with
      | some v => if v.startsWith "{0} is " then (splitWs v)[2]? else none
      | none => none
    let negated := (splitWs phrase).any fun w =>
      (E.predicates.map (·.name) ++ isHeads).any fun h => w == "un" ++ h || w == "non" ++ h
    let ms := (if k == 1 then complementPatterns else activePatterns).filterMap (matchPattern phrase)
    let nounWords := E.sorts.map (·.name) ++ E.sorts.flatMap fun s => (sortNouns E O s).flatMap splitWs
    let safeAdj := ms.all fun a => match a with
      | some w => !(reserved ++ auxiliaries ++ nounWords).contains w
      | none => true
    let rescue := shaped && codes.all eligibleCodes.contains && !collision && !negated && t.length ≤ 80 &&
      !ms.isEmpty && safeAdj
    let content := contentWords t
    let anchored := content.any (contentWords (name ++ " " ++ d.description)).contains
    let idiomCollision := E.constants.any (fun c => wordOccurs c.name phrase) ||
      others.any fun d2 =>
        let other := (E.declaredWording O d2.name).getD ""
        let head := templateHead other d2.arity
        [some d2.name, head].any fun tok? => match tok? with
          | none => false
          | some tok =>
            !tok.isEmpty && !["is", "was", "a", "an", "has"].contains tok &&
            let shared := (name.splitOn "_").contains tok && (d2.name.splitOn "_").contains tok
            let headCollision := some tok == head && content.all (contentWords other).contains
            !shared && (tok == d2.name || headCollision) && wordOccurs tok phrase
    let converse := phrase.endsWith " by" && !name.endsWith "_by"
    let idiomOk := codes.all (eligibleCodes ++ ["VARIABLE_TOKEN"]).contains && anchored && !idiomCollision &&
      !converse && !negated && !codes.contains "DUPLICATE_TEMPLATE"
    let accepted1 := if !codes.isEmpty || idiom then (if idiom then idiomOk else rescue) else true
    let suggestedOk := E.suggestedPred name && k == 1 && match unaryPhrase t with
      | none => false
      | some ph =>
        let sHeads := (E.predicates.map (·.name)) ++
          E.predicates.filterMap fun d2 => templateHead ((E.declaredWording O d2.name).getD "") d2.arity
        let negHeads := ["un", "non", "un-", "non-"].flatMap fun pre => sHeads.map (pre ++ asciiLower ·)
        let phWords := (runs (fun c => isLower c || isDigit c || c == '_' || c == '-') (asciiLower ph)).filterMap
          fun w => let cs := w.toList.dropWhile (fun c => !isLower c)
                   if cs.isEmpty then none else some (String.mk cs)
        !E.constants.any (fun c => wordOccursI c.name ph) &&
        !E.predicates.any (fun d2 => d2.name != name &&
          ((E.declaredWording O d2.name).map wordingKey) == some (wordingKey t)) &&
        !phWords.any negHeads.contains && !codes.contains "NEGATED_HEAD"
    let accepted2 := accepted1 || suggestedOk
    let accepted3 := accepted2 && (idiom || !(runs isLower t).any extraReserved.contains)
    let accepted4 := accepted3 && !(E.profiles.contains "order@0" &&
      (runs isLower (pyLower t)).any comparisonWords.contains)
    let ownTexts (d2 : PredDecl) : List String :=
      [(E.declaredWording O d2.name).getD (strictWording d2.name d2.arity)] ++ (E.declaredNegative O d2.name).toList
    let mine := [t] ++ (E.declaredNegative O name).toList
    let duplicates := others.any fun d2 => (ownTexts d2).any fun x => mine.any fun y => wordingKey x == wordingKey y
    accepted4 && !duplicates
  | _, _ => false

/-- Python's wording and negative for a predicate before the profile steps (english.py:264–389). -/
def mainSelection (E : Env) (O : Overlay) (d : PredDecl) : String × Option String :=
  let k := d.arity
  match E.declaredWording O d.name with
  | none =>
    if k > 2 then (strictWording d.name k, none)
    else if lowerWord d.name && !reserved.contains d.name && (k == 1 || mechanicalVerbs.contains d.name) then
      (strictWording d.name k, none)
    else ((fallbackWording d.name k).getD (strictWording d.name k), none)
  | some t =>
    if k > 2 then (if acceptsDeclared E O d.name then (t, none) else (strictWording d.name k, none))
    else if acceptsDeclared E O d.name then
      let neg := match E.declaredNegative O d.name with
        | some n => if negativeTemplate t k == some n && n.length ≤ 120 && (splitWs n).length ≤ 18 then some n else none
        | none => none
      (t, neg)
    else ((fallbackWording d.name k).getD t, none)

/-- Python's selected wording and negative of a predicate (english.py:390–527). -/
def policyPredicate (E : Env) (O : Overlay) (p : String) : Option (String × Option String) :=
  let F := E.forms
  match E.predicate? p with
  | none => none
  | some d =>
    let (w, n) := mainSelection E O d
    let (w, n) := match F.wordings.lookup p with                  -- roles, the four words, risk forms
      | some fw => if E.modal p then (w, n) else (fw, n)
      | none => (w, n)
    let n := match F.negatives.lookup p with
      | some fn => some fn
      | none => n
    let exempt := E.roles.contains p || p.startsWith "risk__" || altWords.contains p   -- english.py:432–447
    let riskKeys := riskTemplates.map wordingKey
    let (w, n) :=
      if E.risk && !exempt && ([some w, n].any fun f => match f with
          | some x => riskKeys.contains (wordingKey x) | none => false) then
        ((fallbackWording p d.arity).getD w, none)
      else (w, n)
    if E.modal p then                                              -- english.py:521–527
      match F.wordings.lookup p with
      | some fw => some (fw, none)
      | none => some (w, none)
    else some (w, n)

def fallbackNoun (s : String) : String := "entity of sort " ++ jsonQuote s
def letterWords (s : String) : Bool := (s.splitOn " ").all fun w => !w.isEmpty && w.all isLetter

/-- Python's selected noun of every sort (english.py:239–252, :419). -/
def policyNouns (E : Env) (O : Overlay) : List (String × String) :=
  let symbols := E.predicates.map (·.name) ++ E.constants.map (·.name)
  let first := E.sorts.map fun s =>
    let base := (E.declaredNoun O s.name).getD s.name
    let ok := letterWords base && !(splitWs (asciiLower base)).any reserved.contains &&
      !symbols.contains (asciiLower base)
    (s.name, if ok then base else fallbackNoun s.name)
  let deduped := first.map fun (s, n) =>
    if (first.filter fun (_, m) => wordingKey m == wordingKey n).length > 1 then (s, fallbackNoun s) else (s, n)
  deduped.map fun (s, n) => (s, (E.forms.nouns.lookup s).getD n)

/-- The spelling forms of a constant's value whose keys are compared (english.py:492–498). -/
def spellingKeys (value : String) : List String :=
  let capital := if value.startsWith "the " then ["T" ++ value.drop 1] else []
  let article := if lowerWord value then ["the " ++ value] else []
  (([value] ++ capital ++ article).map wordingKey).eraseDups
def bareOk (c : String) : Bool := lowerWord c && !reserved.contains c && !["is", "has"].contains c

/-- Python's selected spelling of every constant (english.py:460–510). -/
def policySpellings (E : Env) (O : Overlay) : List (String × String) :=
  let nounKeys := (policyNouns E O).map fun (_, n) => wordingKey n
  let initial := E.constants.map fun c => (c.name, if bareOk c.name then c.name else jsonQuote c.name)
  let declared := E.constants.filterMap fun c => (E.declaredSpelling O c.name).map (c.name, ·)
  let quotedDeclared := initial.map fun (c, v) => if (declared.lookup c).isSome then (c, jsonQuote c) else (c, v)
  let candidates := declared.filter fun (_, form) =>
    letterWords form && !(splitWs (asciiLower form)).any (fun w => w != "the" && reserved.contains w) &&
    !nounKeys.contains (wordingKey form)
  let unique := candidates.filter fun (_, form) =>
    (candidates.filter fun (_, f2) => wordingKey f2 == wordingKey form).length == 1
  let start := quotedDeclared.map fun (c, v) => match unique.lookup c with
    | some form => (c, form)
    | none => (c, v)
  let step (cur : List (String × String)) : List (String × String) :=
    let owners := cur.flatMap fun (c, v) => (spellingKeys v).map (·, c)
    let collided := cur.filter fun (c, v) => (declared.lookup c).isSome && v != jsonQuote c &&
      (spellingKeys v).any fun key => ((owners.filter (·.1 == key)).map (·.2)).eraseDups.length > 1
    cur.map fun (c, v) => if collided.any (·.1 == c) then (c, jsonQuote c) else (c, v)
  (List.range (E.constants.length + 1)).foldl (fun cur _ => step cur) start

/-! V6 -/
def Lexicon.policyFailures (E : Env) (O : Overlay) (L : Lexicon) : List Failure :=
  let preds := E.predicates.map (·.name)
  let nouns := policyNouns E O
  let spellings := policySpellings E O
  (L.wordings.filterMap fun (p, w) =>
    if !preds.contains p then none else
    match policyPredicate E O p with
    | some (pw, _) => if w == pw || some w == fallbackWording p (E.arity p) then none else some ("V6", "predicate", p)
    | none => none) ++
  (L.negatives.filterMap fun (p, n) =>
    if !preds.contains p then none else
    match policyPredicate E O p with
    | some (pw, pn) => if pn == some n && L.wordings.lookup p == some pw then none else some ("V6", "negative", p)
    | none => none) ++
  (L.nouns.filterMap fun (s, n) =>
    match nouns.lookup s with
    | some pn => if n == pn || n == fallbackNoun s then none else some ("V6", "sort", s)
    | none => none) ++
  (L.spellings.filterMap fun (c, sp) =>
    match spellings.lookup c with
    | some ps => if sp == ps || sp == jsonQuote c then none else some ("V6", "constant", c)
    | none => none)

def Lexicon.policyOk (E : Env) (O : Overlay) (L : Lexicon) : Bool := (L.policyFailures E O).isEmpty
```

The fixpoint of `policySpellings` runs `#constants + 1` rounds. Each round that changes anything quotes at least one
more constant, so it reaches Python's fixpoint.

### 5.3 Admission, candidates, senses, decoding, classes, texts, advice

```lean
def admitRequest (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : AdmitOutcome :=
  if L.policyOk E O then admit E O L b s else .refused (.invalidGrammar .lexicon)

def checkRequest (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) : Option Nat :=
  if L.policyOk E O then firstChecked E O L b rs candidates else none

def ETerm.decode : Json → Option ETerm
  | .arr #[.str "var", i] => (i.getNat?.toOption).map ETerm.var
  | .arr #[.str "const", .str x] => some (.const x)
  | .arr #[.str "num", .str v] => v.toInt?.map ETerm.num
  | .arr #[.str "add", a, b] => do pure (.add (← ETerm.decode a) (← ETerm.decode b))
  | .arr #[.str "scale", .str k, t] => do pure (.scale (← k.toInt?) (← ETerm.decode t))
  | _ => none

def reachRefl : Json → Option Bool
  | .str "star" => some true
  | .str "plus" => some false
  | _ => none

def EFormula.decode : Json → Option EFormula
  | .arr #[.str "top"] => some .top
  | .arr #[.str "bottom"] => some .bottom
  | .arr #[.str "unary", .str p, t] => do pure (.pred p [← ETerm.decode t])
  | .arr #[.str "binary", .str p, t, u] => do pure (.pred p [← ETerm.decode t, ← ETerm.decode u])
  | .arr #[.str "atom", .str p, .arr ts] => do pure (.pred p (← ts.toList.mapM ETerm.decode))
  | .arr #[.str "eq", t, u] => do pure (.eq (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "lt", t, u] => do pure (.lt (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "le", t, u] => do pure (.le (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "not", a] => do pure (.not (← EFormula.decode a))
  | .arr #[.str "and", a, b] => do pure (.and (← EFormula.decode a) (← EFormula.decode b))
  | .arr #[.str "or", a, b] => do pure (.or (← EFormula.decode a) (← EFormula.decode b))
  | .arr #[.str "implies", a, b] => do pure (.implies (← EFormula.decode a) (← EFormula.decode b))
  | .arr #[.str "forall", .str s, a] => do pure (.all s (← EFormula.decode a))
  | .arr #[.str "exists", .str s, a] => do pure (.ex s (← EFormula.decode a))
  | .arr #[.str "reach", k, .arr #[.str "named", .str r], t, u] => do
      pure (.reachNamed (← reachRefl k) r (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "reach", k, .arr #[.str "body", .str s, a], t, u] => do
      pure (.reachBody (← reachRefl k) s (← EFormula.decode a) (← ETerm.decode t) (← ETerm.decode u))
  | _ => none

def codeClasses : List (String × String) :=
  [("SourceTooLong", "ResourceLimit"), ("TextTooLong", "ResourceLimit"), ("BadCharacter", "SyntaxError"),
   ("OpenQuote", "SyntaxError"), ("BadNumeral", "SyntaxError"), ("EmptyDocument", "SyntaxError"),
   ("EmptySentence", "SyntaxError"), ("Unterminated", "SyntaxError"), ("BadSpacing", "SyntaxError"),
   ("UnboundReference", "SyntaxError"), ("ShadowedName", "SyntaxError"), ("SortMismatch", "SyntaxError"),
   ("MarkerDepth", "SyntaxError"), ("NestingLimit", "ResourceLimit"), ("NumeralBound", "ResourceLimit"),
   ("CoefficientNotNumeral", "SyntaxError"), ("PronounUnresolved", "SyntaxError"),
   ("BlockedWording", "SyntaxError"), ("CoordinationRepeated", "SyntaxError"), ("CoordinationForm", "SyntaxError"),
   ("NaturalScoped", "SyntaxError"), ("RelativeForm", "SyntaxError"), ("Internal", "CheckerUnavailable"),
   ("NoDerivation", "SyntaxError"), ("Ambiguous", "AmbiguousDerivation"), ("Budget", "ResourceLimit"),
   ("InvalidGrammar", "CheckerUnavailable"), ("ConclusionWithoutPremise", "SyntaxError"),
   ("ConclusionNotDerived", "SyntaxError"), ("IllTyped", "TypeMismatch")]

def noPremiseText (i : Nat) : String :=
  s!"Sentence {i + 1} is marked as a conclusion, and no earlier sentence is a premise."
def unprovedText (i : Nat) : String :=
  s!"Sentence {i + 1} is marked as a conclusion, and no checked derivation from the earlier premises was found."

-- Advice.lean
inductive AdvWord where
  | w (s : String)
  | any
  | anyBut (s : String)
  deriving DecidableEq, Repr

structure AdviceRow where
  id : String
  profile : String
  patterns : List (List AdvWord)
  text : String

def aw (s : String) : List AdvWord := (splitWs s).map AdvWord.w

def riskConditionText : String :=
  "A condition wording ('cannot lead to … unless …', 'leads to … exactly when …', 'If …, … leads to …') is a " ++
  "record statement. In a rule, 'unless' is the rule's carve-out: write ', unless …', or move the condition into " ++
  "the decision record."
def pluralText : String := "Plural or possessive reference needs an explicit-name or scoped-referent confirmation."
def negExistText : String :=
  "A sentence that begins with \"no\" cannot use \"that\" or \"who\" after the noun. Write \"it is not the case that there is ... such that ...\" instead."

def adviceRows : List AdviceRow :=
  [⟨"risk-may", "risk@0", [aw "may lead to"], "Use 'might lead to': 'may' is permission."⟩,
   ⟨"risk-does-not", "risk@0", [aw "does not lead to"], "Choose 'cannot lead to' or 'might not lead to'."⟩,
   ⟨"risk-degree", "risk@0", [aw "could lead to", aw "risks", aw "is likely to lead to", aw "increases the risk of"],
     "Use 'might lead to' for possibility under the declared record."⟩,
   ⟨"risk-certainly", "risk@0", [aw "certainly leads to"], "Use 'leads to' for certainty under the declared record."⟩,
   ⟨"risk-prevents", "risk@0", [aw "prevents"], "Use 'might prevent' in a risk environment."⟩,
   ⟨"risk-safer", "risk@0", [aw "is safer than"], "Use 'has a less severe worst case than'."⟩,
   ⟨"risk-condition", "risk@0", [aw "unless", aw "exactly when"], riskConditionText⟩,
   ⟨"alternatives-causes", "alternatives@0", [aw "causes"],
     "The proximate cause wording needs a declared proximate role; declare it or write 'leads to'."⟩,
   ⟨"alternatives-results", "alternatives@0", [aw "results in", aw "brings about"],
     "Use the declared Boolean wording 'leads to' for this outcome."⟩,
   ⟨"alternatives-degree", "alternatives@0", [aw "could lead to", aw "risks", aw "increases the risk of",
     aw "contributes to", aw "provides uplift to"],
     "This outcome wording is not Boolean. State a supported leads-to cell or label the degree of risk as open."⟩,
   ⟨"alternatives-inaction", "alternatives@0", [aw "through inaction allows"],
     "Through inaction allows has two readings. State whether inaction leads to the harm, or whether an avoidable harm is allowed."⟩,
   ⟨"alternatives-human-harm", "alternatives@0", [aw "allows a harm to a human being to happen"],
     "Write the long form: there is a harm such that both that harm is a harm to a human being and that action allows that harm to happen."⟩,
   ⟨"alternatives-person", "alternatives@0", [[.w "allows", .any, .w "to", .anyBut "happen"]],
     "Permission for a person uses the W1 'may' wording, not causal 'allows'."⟩]

def advWords (toks : List Tok) : List (Option String) :=
  toks.map fun t => match t with
    | .word x _ => some (fold x)
    | _ => none
def advPrefix (ws : List (Option String)) : List AdvWord → Bool
  | [] => true
  | p :: ps => match ws with
    | [] => false
    | w :: rest => (match p, w with
        | .w s, some x => x == s
        | .any, some _ => true
        | .anyBut s, some x => x != s
        | _, none => false) && advPrefix rest ps
def advice (profiles : List String) (toks : List Tok) : Option (String × String) :=
  let ws := advWords toks
  if ws.head? == some (some "no") && (ws.contains (some "that") || ws.contains (some "who")) then
    some ("negated-existential", negExistText)
  else if (["they", "them", "their", "her", "him", "his"].map some).contains (ws.headD none) then
    some ("plural-pronoun", pluralText)
  else (List.range ws.length).findSome? fun i =>
    (adviceRows.find? fun r => profiles.contains r.profile && r.patterns.any (advPrefix (ws.drop i))).map
      fun r => (r.id, r.text)
```

In `Senses/Read.lean`, on the request's own environment and lexicon, before the projection:

```lean
def sensesRequest (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String) : SensesOutcome :=
  if L.policyOk E {} then readWithSenses D E L b s else .invalidGrammar .lexicon
```

`IllTyped`, `NoDerivation`, `Ambiguous`, `Budget`, `InvalidGrammar` and the two conclusion codes are status codes,
not `Reject` codes. `codeClasses_total` covers the `Reject` codes, and the response-shape test covers the rest.

### 5.4 The service modes

```lean
-- Service/Protocol.lean: Mode gains  englishRead | englishGrammar | englishCheck,
-- named "english.read", "english.grammar", "english.check"
theorem runMode_englishRead (j : Json) : runMode .englishRead j = VE.EnglishGrammar.Run.readCaseReported j := rfl
theorem runMode_englishGrammar (j : Json) :
  runMode .englishGrammar j = VE.EnglishGrammar.Run.grammarCaseReported j := rfl
theorem runMode_englishCheck (j : Json) : runMode .englishCheck j = VE.EnglishGrammar.Run.checkCaseReported j := rfl
```

### 5.5 The statements

The S2 and S3 statements keep their text (D2). Added:

```lean
theorem policy_iff_no_failure : ∀ (E : Env) (O : Overlay) (L : Lexicon),
  L.policyOk E O = true ↔ L.policyFailures E O = []

theorem policy_selection : ∀ (E : Env) (O : Overlay) (L : Lexicon), L.policyOk E O = true →
  (∀ p w, (p, w) ∈ L.wordings → (E.predicate? p).isSome →
    (policyPredicate E O p).map (·.1) = some w ∨ fallbackWording p (E.arity p) = some w) ∧
  (∀ p n, (p, n) ∈ L.negatives → (E.predicate? p).isSome →
    ∃ w, policyPredicate E O p = some (w, some n) ∧ L.wordings.lookup p = some w) ∧
  (∀ s n, (s, n) ∈ L.nouns → ∀ m, (policyNouns E O).lookup s = some m → n = m ∨ n = fallbackNoun s) ∧
  (∀ c sp, (c, sp) ∈ L.spellings → ∀ m, (policySpellings E O).lookup c = some m → sp = m ∨ sp = jsonQuote c)

theorem admitRequest_ok : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List (EFormula × Bool)) (obs : List (Nat × List Nat)),
  admitRequest E O L b s = .ok rs obs →
  L.policyOk E O = true ∧ EnglishOneReading E O L s rs ∧ obs = obligations rs ∧ ∀ o ∈ obs, o.2 ≠ []

theorem admitRequest_exact : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List (EFormula × Bool)),
  (∃ obs, admitRequest E O L b s = .ok rs obs) ↔
    (L.policyOk E O = true ∧ read E O L b s = .ok rs ∧ ∀ o ∈ obligations rs, o.2 ≠ [])

theorem admitRequest_policy : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String),
  L.policyOk E O = false → admitRequest E O L b s = .refused (.invalidGrammar .lexicon)

theorem checkRequest_some : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) (i : Nat),
  checkRequest E O L b rs candidates = some i →
  L.policyOk E O = true ∧ ∃ s, candidates[i]? = some s ∧ read E O L b s = .ok rs ∧
    ∀ j t, j < i → candidates[j]? = some t → read E O L b t ≠ .ok rs

theorem sensesRequest_policy : ∀ (D : Dictionary) (E : Env) (L : Lexicon) (b : Nat) (s : String),
  L.policyOk E {} = true → sensesRequest D E L b s = readWithSenses D E L b s

theorem codeClasses_total : ∀ r : Reject, (codeClasses.lookup r.code).isSome = true

theorem decode_encode : ∀ A : EFormula, EFormula.decode A.encode = some A
```

**Elaboration status** (section 12):

- *Proved in the stub*, on this text verbatim (the three new fields at their defaults) and again over the stub's
  carrier: `policy_iff_no_failure`, `admitRequest_ok`, `admitRequest_exact`, `admitRequest_policy`,
  `checkRequest_some`, `codeClasses_total`.
- *Proved over a parameterised signature*: `sensesRequest_policy`, with `readWithSenses` and the outcome type as
  parameters, a shape check against `senses.md` 5.2.
- *Proved as `rfl` against a local copy of the mode type*: the three `runMode` equations.
- *Elaborated as definitions of type `Prop`*: `policy_selection` and `decode_encode`. `decode_encode` was also
  checked on four formulas, all true.

### 5.6 By construction, and by test

- **By construction.** `policy_iff_no_failure` is `List.isEmpty_iff`. `policy_selection` unfolds the four
  `filterMap`s of `policyFailures`, with `E.predicate? p` some exactly when `p` is a predicate name. The request
  statements split on `policyOk` and use `admit_ok`, `admit_exact` and `first_checked`. `codeClasses_total` is
  `cases r <;> rfl`. `decode_encode` is an induction on `EFormula`, with a lemma for `ETerm` and for the
  `mapM` of an `atom`.
- **By test.** The port against Python (pt1 and the parity harness), the boundary extension, the cache, the
  relay, the comparator, the advice table, the texts against `DELTA.md`, and the response shapes (`runMode_fits`).

## 6. Files, generated artefacts and gates

| Artefact | Rule |
|---|---|
| `lean/VE/EnglishGrammar/Policy.lean`, `Advice.lean`; the modules of 5.1 | frozen-inventory lines, `Audit.lean` lines for the statements of 5.5, the generated lists regenerated, `LOCK.json` and `actions_version` |
| `lean/VE/EnglishGrammar/E2Examples.lean` | the computed fixtures of section 8 as `#guard` checks, in the default build |
| `ve/backends/english_lean.py`, `ve/english.py`, `ve/natural.py`, `ve/backends/dispatch.py`, `ve/assurance-manifest.json` | E2.3 (2.8) |
| `conformance/english_lean_{g3,reverse,mutate,policy}.py` | E2.5 (2.10) |
| `docs/spec/english-lean-e2-report.md`; `docs/lean-first/e2/DELTA.md`, `LEDGER.md` | GE2 |

Gates: the statement review of this specification (section 10) before any proof of 5.5; the bounded review of the
port's tables (items 1 to 6) before the flip; GE2 as the plan states it.

## 7. What this stage consumes and returns

| From | Delivery | Used in |
|---|---|---|
| S3 build | the reader, `admit`, `obligations`, `firstChecked`, their proofs; `Env.decode`, the boundary, the fixture environments | everywhere |
| S3 report | the measured `safe` finding; G3 open | lx29, E2.5 |
| lexicon report | Python's `lexicon_id` per corpus environment | pt1 |
| senses (`ve-senses-int`) | `senseDecl`, `project`'s call of `Lexicon.failures`; `readWithSenses`' signature | 2.4, lx30, 5.3 |
| LEAN-FIRST | the gate of 5.1; batch 2's handles; batch 12b's environment mode; DRI answers 3 and 5 | GE2, 2.2, 2.7 |
| returns | `english.admission` with `authority: lean`; V6 as Lean's port of Python's selection, which a later stage can use to produce the lexicon; the class table; the ledger | the next stage; E3 |

## 8. Acceptance fixtures

Every fixture is an obligation on the implementation. A value marked *computed* was computed by the stub (section
12). The rest are *obligations* and were not computed. The environment `F` is the base fixture: the sorts `person`
and `service` without nouns; `deployed` (`{0} is deployed`), `reviewed` (`{0} is reviewed`, negative
`{0} is not reviewed`) and `owns` (`{0} owns {1}`, negative `{0} does not own {1}`); the constants `alice` and
`legacy`. "F + p" adds the predicate `p` with the wording given and the description `A predicate.`. For each
predicate fixture, the table gives:

- **Python's choice**, by the port;
- the **V1–V5 failures** of the lexicon that is Python's choice except that the predicate selects its declared
  wording and negative;
- that lexicon's **V6 failures**.

### 8.1 V6: declared wordings (computed)

| Id | Case | Python's choice | V1–V5 | V6 |
|---|---|---|---|---|
| lx15a | F + `stable` (service) `{0} never fails` | fallback | none | `("V6", "predicate", "stable")` |
| lx15b | F, `deployed` | `{0} is deployed` | none | none |
| lx16a | F + `archived` `{0} is legacy` (a constant's name) | fallback | none | V6 |
| lx16b | F + `archived` `{0} is archived` | declared | none | none |
| lx17a | F + `undeployed` `{0} is undeployed`, beside `deployed` | fallback | none | V6 |
| lx17b | the same without `deployed` | declared | none | none |
| lx18a | F + `managed_by` (service, person) `{0} is managed by {1}` | fallback | none | V6 |
| lx18b | F + `manages` (person, service) `{0} manages {1}` | declared | none | none |
| lx19a | F + `reports_to` `{0} reports to {1}` | declared, by the rescue | none | none |
| lx19b | F + `belongs_to` `{0} belongs to {1}` | fallback | none | V6 |
| lx20a | F + `manage` `{0} manage {1}` (`BINARY_VERB`) | fallback | none | V6 |
| lx20b | F + `supervises`, 84 characters and 9 words (`TEMPLATE_LENGTH` alone) | fallback | none | V6 |
| lx20c | F + `denies_protection` `{0} denies the equal protection of the laws to {1}` | declared, by the rescue | none | none |
| lx20d | F + `recorded` `{0} is recorded` (`ENGLISH_STRUCTURE_WORD`) | fallback | none | V6 |
| lx20e | F + `logged` `{0} is logged` | declared | none | none |
| lx20f | F under `order@0` + `same` `{0} is same` | fallback | none | V6 |
| lx20g | F + `same` `{0} is same`, without `order@0` | declared | none | none |
| lx20h | F + `compliant` `{0} is v1.2 compliant` (`PHRASE_SYNTAX`) | fallback | `V3` | V6 |
| lx20i | F + `compliant` `{0} is compliant` | declared | none | none |
| lx20j | F + `checked` `{0} is checked daily` (`UNARY_MODIFIER`) | fallback | none | V6 |
| lx20k | F + `checked` `{0} is checked` | declared | none | none |
| lx20l | F + `running` `{0} runs` (`TEMPLATE_SHAPE`) | fallback | none | V6 |
| lx20m | F + `relates` (person, service) `{0} relates X1 {1}` (`VARIABLE_TOKEN`) | fallback | none | V6 |
| lx20n | F + `relates` `{0} relates {1}` | declared | none | none |
| lx20o | F + `ready` `{0} is service ready` (`SORT_NOUN`) | fallback | none | V6 |
| lx20p | F + `checked` and `inspected`, both `{0} is checked` (`DUPLICATE_TEMPLATE`), for `checked` | fallback | `V4` | V6 |
| lx20q | F + `inspected` `{0} is inspected` | declared | none | none |
| lx21a | F + `voted_for` (person, person) `{0} voted for {1}` | declared (anchored by the name) | none | none |
| lx21b | F + `ballot` `{0} voted for {1}`, described `A member voted for a proposal.` | declared (anchored by the description) | none | none |
| lx21c | F + `ballot` `{0} voted for {1}`, described `A recorded choice.` | fallback (`IDIOM_UNRELATED`) | none | V6 |
| lx22a | F + `appointed` `{0} was appointed by {1}` | fallback (direction) | none | V6 |
| lx22b | F + `appointed_by` `{0} was appointed by {1}` | declared | none | none |
| lx22c | F + `undermines` `{0} undermines {1}` beside `erodes` `{0} undermines the oversight role of {1}` | fallback (ownership) | none | V6 |
| lx22d | F + `undermines` beside `undermines_check` with that wording | declared (shared family) | none | none |
| lx22e | F + `undocumented_parent` `{0} has an undocumented noncitizen parent` beside `documented` (`{0} is documented`) | fallback (negated head) | none | V6 |
| lx22f | the same without `documented` | declared | none | none |

lx20b's wording is `{0} supervises abcdefghij abcdefghij abcdefghij abcdefghij abcdefghij abcdefghij {1}`. Every row
whose V1–V5 column is "none" while V6 fails is a lexicon that S3's `Lexicon.valid` accepts and Python's producer
never makes.

### 8.2 V6: risk, and the S3 fixture lexicons (computed)

`FA`, `FR`, `LA` and `LR` are S3's (S3 build, `ProfileExamples.lean:75–111`). `laSafe` and `lrSafe` are `LA` and
`LR` with `safe` on its fallback `{0} is classified as "safe"`.

| Id | Case | V1–V5 | V6 |
|---|---|---|---|
| lx23a | `FR` + `hazard` (action, harm) declared `{0} risks {1}`, selected | none | `("V6", "predicate", "hazard")` (Python's choice: fallback) |
| lx23b | the same, `hazard` on its fallback (`lrSafe` with it) | none | none |
| lx23c | `FR` + `hazard` declared `{0} endangers {1}`, selected | none | none |
| lx23d | `lrSafe` with `prevents` on the mechanical `{0} prevents {1}` | none | `("V6", "predicate", "prevents")` |
| lx23e | `laSafe` under `FA`, where `{0} prevents {1}` is the fixed form | none | none |
| lx24 | lx23b with the negative `{0} cannot lead to {1}` for `hazard` | `("V2", "negative", "hazard")`, `("V5", "negative", "hazard")` | `("V6", "negative", "hazard")` |
| lx29 | `LF`/`F`, `LO`/`FO`, `LD`/`FD`, `LM`/`FM` | none, each | none, each |
| | `LA`/`FA`, `LR`/`FR` | none, each | `("V6", "predicate", "safe")`, each |
| | `laSafe`/`FA`, `lrSafe`/`FR` | none, each | none, each |

lx23d is a lexicon that V1 to V5 accept and that makes the refused risk form `prevents` readable. lx29's `safe`
row is the S3 report's measured Python finding, reproduced by the port.

### 8.3 V6: the selections S3 did not name (computed)

Each row replaces one selection of Python's choice.

| Id | Case | V1–V5 | V6 |
|---|---|---|---|
| lx25a | F + `likes` (person, service) without a wording; `{0} likes {1}` | none | `("V6", "predicate", "likes")` |
| lx25b | the same, the fallback | none | none |
| lx25c | F + `audits` without a wording; `{0} audits {1}` (one of the eight verbs) | none | none |
| lx25d | F + `archived` (service) without a wording; `{0} is archived` | none | none |
| lx25e | F + `holds` (service) without a wording; `{0} is holds` (`holds` is reserved) | none | `("V6", "predicate", "holds")` |
| lx26a | F + `assigns` (person, service, person) without a wording, with the declared negative `{0} does not have recorded relation assigns with argument two {1} and argument three {2}` selected | none | `("V6", "negative", "assigns")` |
| lx26b | S2's `LFv3`: `owns` on its fallback with the declared negative | `("V5", "negative", "owns")` | `("V6", "negative", "owns")` |
| lx27a | F + sort `item` with the noun `every item`, selected | none | `("V6", "sort", "item")` |
| lx27b | the same, `entity of sort "item"` | none | none |
| lx27c | F + sort `item` with the noun `deployed service`, selected | none | none |
| lx27d | the same, the sort's name `item` selected | none | `("V6", "sort", "item")` |
| lx28a | F + constant `hence` (service), spelled `hence` | none | `("V6", "constant", "hence")` |
| lx28b | the same, spelled `"hence"` | none | none |
| lx28c | F + constant `api` displayed `the api`, spelled `the api` | none | none; Python's spellings `alice`, `the api`, `legacy` |
| lx28d | lx28c + constant `api2` displayed `api`; `api` spelled `the api` | none | `("V6", "constant", "api")`; Python's spellings quote both |
| lx31a | F + `fast` (service) with an overlay entry `{0} is a fast service`, suggested | none | none (accepted by the suggested path) |
| lx31b | the same, not suggested | none | `("V6", "predicate", "fast")` |

### 8.4 Why V6 is outside `Lexicon.valid` (computed)

lx30 is a projection of the senses joke written as an environment: the sorts `joke` and `person`, and three sense
predicates as `senseDecl` declares them.

| Predicate | Wording | Lint codes | Python's choice | V1–V5 | V6 |
|---|---|---|---|---|---|
| `sense__funny_1` | `{0} is funny`, negative `{0} is not funny` | `SYMBOL_COLLISION` | fallback | none | predicate and negative |
| `sense__funny_2` | `{0} is funny (meaning strange)` | `PHRASE_SYNTAX`, `SYMBOL_COLLISION`, `UNARY_MODIFIER` | fallback | none | predicate and negative |
| `sense__tells_1` | `{0} tells (meaning says aloud) {1}` | | fallback | none | predicate and negative |

### 8.5 Port parity on the corpus (pt1, computed)

| Rows of `lexicon-report.json` | Port's `lexicon_id` equals Python's |
|---|---|
| the 18 use-case rows that the boundary admits, 4 with overlays | 18 of 18 (with D6's display identity; 14 of 18 with the submitted identity, the 4 overlay rows differing) |
| the 4 rows the boundary refuses (2.2) | not computed: no lexicon is read |
| the 17 round-trip configurations | not computed (built in Python) |

*Obligation* pt2: the parity harness of 2.10, symbol by symbol, on every row and every mutant.

### 8.6 Advice (computed)

The profiles are `risk`, which names `alternatives@0`, `norms@0`, `relational-fol@0` and `risk@0`; `alternatives`,
the same without `risk@0`; and `base`, which names `relational-fol@0`.

| Id | Profiles; sentence | Advice |
|---|---|---|
| ad1 to ad7 | risk; `Wait may lead to injury.`, `… does not lead to …`, `… could lead to …`, `… certainly leads to …`, `Wait prevents injury.`, `Wait is safer than proceed.`, `Wait cannot lead to injury unless robot is safe.` | `risk-may`, `risk-does-not`, `risk-degree`, `risk-certainly`, `risk-prevents`, `risk-safer`, `risk-condition` |
| ad8 | risk; `Wait causes injury.` | `alternatives-causes` |
| ad9 | alternatives; `Wait could lead to injury.` | `alternatives-degree` |
| ad10 | base; `Wait may lead to injury.` | none |
| ad11 | base; `No service that is deployed is not reviewed.` | `negated-existential` |
| ad12 | base; `No service is deployed.` | none |
| ad13 | base; `They are deployed.` | `plural-pronoun` |
| ad14 | base; `Every sevice is reviewed.` | none |
| ad15 | alternatives; `Wait allows a harm to a human being to happen.` | `alternatives-human-harm` |
| ad16 | alternatives; `Wait allows robot to leave.` | `alternatives-person` |
| ad17 | alternatives; `Wait allows injury to happen.` | none |
| ad18 | alternatives; `Wait through inaction allows injury.` | `alternatives-inaction` |

### 8.7 Admission and the check of candidates (computed)

| Id | Case | Outcome |
|---|---|---|
| cn10 | `admitRequest` under `F`, `LF`: `Legacy is deployed. Therefore legacy is deployed.` | `ok`, the two formulas, obligations `[(1, [0])]` |
| cn11 | `admitRequest` under `FA`, `LA`: `Wait is available to robot.` | `refused (invalidGrammar lexicon)`: V6 (`safe`) |
| cn12 | the same with `laSafe` | `ok`, `available(wait, robot)`, no obligation |
| cn13 | `checkRequest` under `FA`, `LA`, for `available(wait, robot)`, candidate `Wait is available to robot.` | none |
| cn14 | the same with `laSafe` | `some 0` |
| cn15 | the texts of 4.2 for `noPremise 0` and the obligation of sentence index 1 | as 4.2 |
| cn16 | `admitRequest` under `F`, `LF`: `Therefore legacy is deployed.` | `noPremise 0` |
| cn17 | the same: `Therefore legacy is deployed. So legacy is deployed.` | `noPremise 0` |
| cn18 | the same: `Every sevice is reviewed.` | `refused`: sentence 0 has no derivation |

### 8.8 The service and the boundary

| Id | Case | Expected |
|---|---|---|
| ev2 | *obligation*: `english.read` as a service mode on S2's 89 route fixtures and on S3's 200 comparison cases | the answers of `ve_english_route`, plus the fields of 4.4 |
| ev3 | *obligation*: two requests with one `environment_id`, `overlay_digest` and `lexicon_id` | the second does not instantiate the grammar |
| ev3b | *obligation*: the same environment and lexicon with two overlays, one making the lexicon fail V2 | the second is refused; the cache is not hit |
| ev4a | `english.check` under `F`, `LF` for `deployed(legacy)`, unmarked, candidates `Legacy is reviewed.`, `Legacy is deployed`, `Legacy is deployed.`, `legacy is deployed.` | computed: index 2 |
| ev4b | the one candidate `Legacy is reviewed.` | computed: none |
| ev4c | `deployed(legacy)` twice, marks `[false, true]`, candidates `Legacy is deployed. Legacy is deployed.` and `Legacy is deployed. Therefore legacy is deployed.` | computed: index 1 |
| ev14a | the four environments of 2.2 under the S3 build's `Run.environmentId` | computed: refused, with the messages of 2.2 |
| ev14b | *obligation*: the same after E2.0 | admitted; the port's `lexicon_id` equals the report's for each |
| ev15a | `english.read` on the birthright use case with its overlay and Python's lexicon (display identity), S3 build | computed: `InvalidInput: the lexicon names another environment` |
| ev15b | the same lexicon written with the submitted identity, S3 build | computed: status `one` |
| ev15c | *obligation*: ev15a after E2.0 | status `one`, `environment_id` the submitted environment's |
| ev16 | *obligation*: a source with a non-ASCII character before its second sentence | `spans` in code points, equal to Python's `sentence_spans` mapped through `boundaries` |

### 8.9 The relay, the comparator and the ledger (obligations)

| Id | Case | Expected |
|---|---|---|
| rl1 | `parse_english` on cn10's text under `F` | Lean's reading; one entailment call with premises `[0]` |
| rl2 | an obligation whose entailment is not `Found` | `SyntaxError` with the obligation's `unproved` text |
| rl3 | each status and code of 4.2 | the class of `codeClasses`, the text verbatim; no Python text on the path (`relay_lint`) |
| rl4 | `render_english` of cn10's document | candidates checked by `english.check`; no call of `_parse_english_document` |
| rl5 | `parse_english_with_metadata` when the rendering does not read back | `english_text` is the source |
| rl6 | a request that fails V6 | `CheckerUnavailable` with `invalidGrammar lexicon: V6 …` |
| rl7 | the natural view of a two-paragraph document | the same paragraph breaks as before the flip |
| rl8 | the producer raises for a suggested overlay entry without `accept_suggested_vocabulary` | the same `VEError` before any Lean call |
| ev6 | the comparator off | `_python_reading` is not called |
| ev7 | the comparator on, with a Python reading that disagrees | one record; the result returned is Lean's |
| lg1 | `relay_lint` over the admission path | passes; every row of 2.9 is in `LEDGER.md` |

### 8.10 The iff claims, both directions

| Claim | Direction | Fixture |
|---|---|---|
| V6 passes exactly when each selection is Python's choice or its quoted form (and each negative Python's) | Python's choice → passes | lx15b, lx16b, lx19a, lx21a, lx22b, lx29 (`LF`) |
| | quoted form → passes | lx23b, lx25b, lx27b, lx28b |
| | neither → fails | lx15a to lx22e (the V6 rows), lx25a, lx27a, lx28a |
| | a negative not Python's → fails | lx24, lx26a, lx26b |
| a declared wording is Python's choice exactly when `acceptsDeclared` holds of it | holds | lx15b to lx22f (the "declared" rows) |
| | does not hold | the "fallback" rows of 8.1 |
| an idiom is accepted exactly when it is anchored, owned, directed and not negated | all four | lx21a, lx21b, lx22b, lx22d, lx22f |
| | one fails | lx21c (anchor), lx22c (ownership), lx22a (direction), lx22e (negated head) |
| the rescue accepts exactly a wording with eligible codes, no collision, at most 80 characters and a matching pattern | accepted | lx19a, lx20c |
| | refused | lx19b (no pattern), lx20b (length and no pattern) |
| a mechanical wording is Python's exactly for an unreserved lower-case name of one argument, or one of the eight verbs | Python's | lx25c, lx25d |
| | not | lx25a, lx25e |
| under `risk@0` a risk wording is Python's exactly when the profile fixes it for that symbol | fixed | lx23e, lx29 (`lrSafe`) |
| | declared or mechanical | lx23a, lx23d |
| a declared display form is Python's exactly when it is unique and collides with no spelling | unique | lx28c |
| | collides | lx28d |
| a suggested entry is accepted by the suggested path exactly when it is suggested and passes `unary_phrase` and the three checks | suggested | lx31a |
| | not suggested | lx31b |
| `admitRequest` is `ok` exactly when V6 passes, `read` is `ok` and every obligation has a premise | all three | cn10, cn12 |
| | V6 fails | cn11 |
| | `read` not `ok`; a mark without a premise | cn18; cn16, cn17 |
| `checkRequest` names an index exactly when V6 passes and some candidate reads back | both | cn14, ev4a, ev4c |
| | V6 fails; no candidate reads back | cn13; ev4b |
| a lexicon decodes exactly when it names the environment it was selected for | display identity, overlay | ev15c (*obligation*) |
| | submitted identity, overlay (S3 build) | ev15a, ev15b |
| advice of an `alternatives@0` row is given exactly when the profile is named and a pattern occurs | both | ad8, ad9, ad15, ad16, ad18 |
| | no pattern (`to happen`); no profile | ad17; ad10 |
| the comparator runs exactly when its switch is set | set | ev7 (*obligation*) |
| | not set | ev6 (*obligation*) |

## 9. Limits, and what is not claimed

The limits of S2 section 9 and S3 section 9 stand. In addition:

- **The port is trusted and tested, not proved against Python.** pt1 is 18 rows by identity. The parity harness
  is the gate, and nothing proves that `policyPredicate` is Python's on an environment not tested.
- **`\w` and `str.lower` are ported on ASCII.** The port also handles the Kelvin sign and `İ` for content words.
  Python's `\w` is wider on non-ASCII letters, so on a phrase with such letters the port finds a whole-word
  collision Python does not. Such a phrase already carries `PHRASE_SYNTAX`, and no rescue pattern or idiom matches
  it, so it is refused either way.
- **V6 does not cover letters**, and `rights@0` wordings are outside the reader.
- **The producer still proposes**, and the next stage removes it.
- **Advice is wider than Python's hints and proves nothing.** Two hints are still lost (S3 4.3).
- **`IllTyped` has one class** (D10).
- **The obligations' proofs are outside the English statements** (claim C4 stays).
- **`EnglishParser` stays for the statement layers.**
- **The latency budgets are unmeasured.**
- **The boundary extension is a link to existing decoders** and is tested, not proved.
- **What the stub could not elaborate as the build will write it:**
  - the three new fields, held beside `Env` and at their defaults in the verbatim run;
  - the senses statement, checked over parameters;
  - the service equations, checked against a local mode type (section 12).

## 10. Statement review checklist (Astra + Fable, before any proof of 5.5)

1. The word lists and pattern tables of 2.3 are Python's, with nothing missing and nothing added.
2. `lintCodes` is `_NaturalVocabulary`'s report for a predicate path: the owners, nouns and negated heads, and the
   n-ary branch through `templateParts`.
3. `acceptsDeclared` is the main loop's `accepted` for a declared wording: the rescue, the idiom branch, the
   suggested path, the structure and comparison words, and the duplicates, in Python's order.
4. `mainSelection` and `policyPredicate` give Python's wording and negative, the order of the profile steps
   included: the risk reservation before the modal overwrite, and its exemptions.
5. `policyNouns` and `policySpellings` are Python's, the deduplication and the spelling fixpoint included.
6. V6's freedom (the quoted form, an omitted negative) is safe, and nothing it allows is a wording, noun or
   spelling that Python refuses.
7. Checking V6 beside `valid` (2.4) loses nothing that V6 inside `valid` would give: every mode that receives a
   producer's lexicon runs it, and only Lean-computed projections skip it.
8. The display identity of D6 is Python's, and the boundary extension of D7 admits exactly the environments
   Python's `Environment` admits for these profiles.
9. The class table, the texts and the advice rows are right; `IllTyped`'s one class (D10) is acceptable.
10. The response additions of 4.4 suffice for the relay, which needs no text, class or span of its own.
11. The ledger of 2.9 lists every decision site of formula-level admission.
12. The computed fixtures of section 8 are the right expectations, and the obligations are the right ones.
13. Every name passes the audit's rules, and no public message, code or identity changes before the flip.

## 11. Open points

| # | Point | Recommendation |
|---|---|---|
| Q1 | Lean as the producer of the lexicon: the port computes Python's selection | not in E2; the next stage, with the renderers reading Lean's export (plan, question 3) |
| Q2 | letters in V6 | leave to V1 (2.3); the port exists if the review wants them |
| Q3 | the 17 round-trip configurations of the lexicon report | E2.1's parity harness runs them in Python against the port |
| Q4 | `IllTyped`'s class | `TypeMismatch` (D10); the alternative is a Lean classification of the typing failure, which repeats the typed check's logic |
| Q5 | the identity fix on Lean's side (D6) or Python's | Lean's: no identity value changes (plan, question 5) |
| Q6 | the boundary extension against lean-first 12b | call 12b's mode if it lands first (plan, question 6) |
| Q7 | a role predicate that is also modal: `Env.decode` lists role wordings before modal forms, so `forms.wordings.lookup` gives the role wording, while Python gives the modal form | append the modal forms first in `Env.decode` (an S3 build fix); the port follows Python (`policyPredicate` reads `E.modal` before the fixed form) |
| Q8 | the `alternatives-person` row compares words, Python a regex on the cut phrase | accept: advice decides nothing; differences are `wording` rows |
| Q9 | `english.grammar` now refuses an invalid lexicon | adopt: a sampled reverse corpus never comes from a grammar Lean would not read with |

## 12. How the figures were computed

The scratch file `lean/SpecStubs_english-lean-e2.lean` was not committed. It was elaborated with
`lake --dir /home/seyran/code/ve-english-lean-s3-int/lean env lean <file>`: this worktree has no Lean build, the S3
build lives in that worktree, and E2 builds on it. The toolchain was Lean 4.24.0. The file imported
`VE.EnglishGrammar.Run` and `VE.EnglishGrammar.ProfileExamples` and did the following:

- It declared a structure `PEnv` holding an S3 `Env` and the three new carriers: a list of plurals, the suggested
  predicates, and the role list. It wrote the port over `PEnv`, and computed every fixture with that form. The
  carriers were read from the environment JSON and the overlay JSON (`penvOf`), as `Env.decode` will read the
  fields.
- It then copied the code of 5.2 and 5.3 (`sensesRequest` excepted) and the statements of 5.5 into the namespace
  `VE.EnglishGrammar`, verbatim except for the three accessors of 2.2. Since the S3 build has no `plural`,
  `suggested` or `optional` field, `Env.pluralOf` returned none, `Env.suggestedPred` returned false, and `Env.roles`
  read `available` and `leads_to` only. That text elaborated, and the six proofs of 5.5 went through on it. On seven
  cases where the carriers are at their defaults (lx15a, lx19a, lx22c, lx21a, lx25e, lx30, lx28d), its
  `policyPredicate`, `policyNouns`, `policySpellings`, `lintCodes` and `Lexicon.policyFailures` equal the `PEnv`
  port's. On `LA`/`FA` and `LR`/`FR` it fails `safe`, and on `LM`/`FM` it passes, as 8.2 states.
- It computed 8.1 to 8.4 with `policyPredicate`, `lintCodes`, `policyFailures` and the S3 build's
  `Lexicon.failures`. The environments were written as `ve.core@0.2` JSON and decoded by the S3 build's
  `Env.decode`. The S3 fixtures `FA`, `FR`, `FM`, `FO`, `FD` and their lexicons were imported from
  `ProfileExamples`.
- It computed pt1 by reading each use-case environment file of the S3 worktree, and its overlay when the row has
  one. It built the port's selection with a port of `_fluent_variable_letters` and the profile aliases, wrote the
  export as `ve.english_grammar.export` does (lists sorted by symbol), took the environment identity from
  `Run.environmentId` of `displayJson environment overlay`, and digested with
  `VE.CertificateWire.digest "ve-english-lexicon-v1\n"`. The result was compared with the row's `lexicon_id`. With
  the submitted identity instead, 14 rows agreed, all four overlay rows differing, which is how D6 was found. ev15
  ran the S3 build's `Run.readCase` on both lexicons.
- It computed 8.6 with the advice port over the S3 lexer.
- It computed 8.7 with `admitRequest` and `checkRequest` over the S3 build's `admit` and `firstChecked`.
- It computed ev4 with a `checkCase` that decodes the case with `Run.decodeCase` and the formulas with
  `EFormula.decode`.
- It computed ev14a with `Run.environmentId`.
- It ran `typedCheck` on three ill-typed formulas under `F` for D10. The messages were `ill-typed or unbound formula`
  (twice) and `invalid indexed formula`.
- It proved the statements listed in 5.5, and checked `decode_encode` on four formulas.

All checks passed on 2026-10-06, and the elaboration reported no error.

**What the stub does not show:**

- that the build's fields decode as `penvOf` read them;
- anything about Python beyond the 18 recorded identities;
- the 17 round-trip configurations;
- the boundary extension (ev14b);
- the relay;
- latency.
