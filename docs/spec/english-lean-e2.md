# English in Lean, E2: Lean decides English admission (statement specification)

> Status: statement specification, draft 2 with py1 run (2026-10-06), branch `design/english-lean-e2`. This is
> the item-1 statement spec of [english-lean-E2-PLAN.md](english-lean-E2-PLAN.md) draft 3 (the **plan**). It writes
> out stages E2.0 to E2.5 on top of `english-lean-s3.md` draft 2 (the **S3 spec**) as built on
> `english-lean-s3/integrate` at `531f2789` (the **S3 build**). The S3 build, the S3 spec, `english-lean-S3-PLAN.md`
> and `english-lean-s3-report.md` (the **S3 report**) are on that branch and reach `main` when S3 merges; `S3 2.9`
> refers to the S3 spec, `S2 2.6` to `english-lean-s2.md`, `base 2.12` to `english-lean.md`. Their definitions and
> statements are not repeated.
>
> **Draft 2 applies the statement review.** The review of draft 1 (`manage-agents/debates/english-lean-e2-spec/`)
> converged on FIX after round 3. Its joint position is Fable's six items of round 2, with the precisions of round 3
> (constants are never refused; an overlay refusal has its own code, of class `VEError`; the stage gates; a bounded
> round on draft 2). Draft 2 carries all six, and changes nothing else:
>
> 1. *Enumeration.* The port enumerates the declared symbols where Python does; the generated ones stay in V6's
>    domain (2.3, lx32).
> 2. *The overlay check.* Python's three overlay refusals become a Lean check, O1 to O3 (D17, 2.3, 8.11).
> 3. *The boundary.* Modal forms under `norm-defaults@0` come through an adapter (D7, part 4). Modal forms come
>    before role wordings in `Env.decode` (D18; Q7 of draft 1).
> 4. *Guards and responses.* The translation and grammar guards are defined, with the service's order: boundary,
>    overlay check, V6, then V1 to V5 (2.5). `english.check` answers `invalidGrammar` when the vocabulary is refused.
>    `NotOneSentence` has a class (4.2).
> 5. *`unaryPhrase`.* It follows `re.I` (2.3, lx31c to lx31f), and section 9 is corrected.
> 6. *Claims and texts.* Three rows of 8.10 are scoped. The `unproved` text carries the prover's status (4.2).
>
> Before any stage starts, both reviewers check draft 2 in one bounded round: the new definitions (the overlay
> check, the adapter, the guards), the order, and that each new fixture's expectation was computed (plan, section 1).
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
> For draft 2 the same file also elaborated draft 2's text of 5.2, 5.3 and 5.5, proved the three new statements,
> and computed the new fixtures of 8.3 and 8.11 to 8.13. It kept draft 1's port beside the new text, so each
> correction is shown against the draft-1 value it replaces. Draft 2's text reproduces Python's recorded
> `lexicon_id` on all 22 rows.
>
> **Python.** For the fixtures of draft 1, a Python outcome named here was read from `ve/english.py`,
> `ve/printer.py` and `ve/english_vocabulary.py`, or recovered from an identity Python recorded (pt1). Every
> `file:line` was read on 2026-10-06 in the S3 build's worktree and must be re-read at each step.
>
> **py1 is discharged.** The review required that each new fixture's Python expectation be computed by running
> Python, before the bounded round. The script `lean/SpecStubs_english-lean-e2.py` (scratch, beside the stub) was run
> on 2026-10-06 against the S3 build's worktree (section 12). Every Python outcome of a new fixture in 8.3, 8.11 and
> 8.12 is now Python's printed output. Python agreed with draft 2 on every new fixture but four, and these rows are
> corrected:
>
> - **lx31e and lx31f.** The suggested path refuses the wording, as draft 2 said. But the entry is an overlay's, so
>   the producer does not stop at the fallback: its final comparison raises at `:517`. The overlay check refuses
>   both with O3 (computed), as it refuses lx31b (8.3).
> - **ov8 and ov9.** Draft 2's two overlays rewrote the fixed wording of the role `available`. Python refuses them
>   before the producer's main loop: `display_environment` builds the display environment, and its validation
>   raises `AlternativesVerbalisation: available must read "{0} is available to {1}"` (`english_vocabulary.py:131`,
>   `environment.py:243`). That check stays in Python and runs before any Lean call (2.8, 2.9). ov8 and ov9 now keep
>   the role's fixed wording, so they reach `:374` and `:399` as intended. Draft 2's two overlays are now ov11a and
>   ov11b (8.11).
>
> The second correction has consequences, and they are the only other edits. No definition or statement of
> section 5 changes:
>
> - The ledger row of `display_environment` (2.9) and the relay (2.8) name its validation of the display
>   environment.
> - A paragraph after the overlay check (2.3) states that the check reads an overlay `display_environment` admitted.
> - 8.10's overlay claim takes that as its premise, with ov11 as the premise's fixture.
> - The overlay parity harness (2.10) compares neither the raise nor the site for a mutant that
>   `display_environment` refuses.
> - rl8 covers ov11a.
> - Section 9 states the limit.
>
> md4's Python column is now computed as well. Python's `Environment` refuses that environment, so py1 ran the
> producer on an environment object whose role is regulated after validation (8.12).

## 0. Scope, one paragraph

E2 moves `english.admission` from Python to Lean. Lean gets three service modes (`english.read`, `english.grammar`,
`english.check`), and the boundary fixes that make every corpus environment and every overlay readable. Python's
vocabulary policy becomes a Lean check, V6, stated as Lean's port of Python's selection. The producer's three
refusals of an overlay become a Lean check too, the overlay check. A request-level admission runs the overlay
check, V6 and then `admit`, and the same holds for translation, for the grammar export and for the check of
rendered candidates; the senses mode, which takes no overlay, runs V6. Lean's codes, classes, texts and advice are
the ones shown. Python relays and proves each obligation with the existing entailment operation. Its hand parser
and Lark audit become a comparator that decides nothing. A deletion ledger maps each Python decision site of
formula-level admission. The evidence is the G3 comparisons S3 left open and the lean-first corpus A/B.
Statement-layer English stays for E3, and the comparator is deleted in the next stage.

In this specification: the decisions (1), the definitions (2), the English of the new outcomes and claims (3), the
diagnostics (4), the Lean definitions and the exact statements (5), files and gates (6), what is consumed and
returned (7), the acceptance fixtures (8), limits (9), the statement review checklist (10), open points (11), and
how the figures were computed (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | V6 is Lean's port of Python's selection (`EnglishVocabulary`, `english.py:230–527`, with the lint of `printer.py:183–338`). A lexicon passes V6 when each wording is Python's choice or the quoted fallback, each noun Python's or the fallback noun, each spelling Python's or the quoted name, and each negative Python's, beside Python's wording. Where Python enumerates `env.sorts`, `env.predicates` or `env.constants`, the port enumerates the declared symbols only, as `_ProfilePredicates` does; the generated symbols are looked up, get their fixed forms and stay in V6's domain | 2.3, 5.2, lx32 |
| D2 | V6 is checked beside `Lexicon.valid`, not inside it: `Lexicon.valid`, `read`, `admit`, `EnglishOneReading`, `Extends` and every S2, S3 and senses statement stay word for word | 2.4, lx30 |
| D3 | V6 is checked on the request's own environment, overlay and lexicon, in every mode that receives a producer's lexicon (`english.read`, `english.check`, `english.grammar`, `senses.read`), and never on a projection that Lean computes | 2.4, 5.3 |
| D4 | V6 covers what S3 2.9 named (the code set with the rescue, the idiom branch, the reserved risk wordings) and the four selections S3 did not name: mechanical wordings, negatives, nouns and spellings. It does not cover letters or aliases | 2.3, lx25 to lx28, Q2 |
| D5 | `SortDecl.plural`, `PredDecl.suggested`, `AltBlock.optional` and the `generated` flag of `SortDecl`, `PredDecl` and `ConstDecl` are new fields, all with defaults. V6 and the overlay check read them; no rule and no action does | 2.2 |
| D6 | The lexicon names the environment it was selected for: with an overlay, the display environment (the overlay merged in, as `display_environment` builds it). `decodeLexicon` checks the lexicon's `environment_id` against that identity. The response's `environment_id` stays the submitted environment's | 2.2, ev15 |
| D7 | The boundary of S3 2.3 is extended to `norm-defaults@0`, `soft-norms@0` and W6 units outside `risk@0`. Each set of declarations is validated as submitted, the typed check reads a reduced view, and the identity is computed over the submitted environment. Part four: under `norm-defaults@0`, `Env.decode` takes each modal form from the `regulated` entry with `unspecified` read as the placeholder `deny` (`placeholderEntry`), and the frozen decoders are not edited | 2.2, ev14, md1 to md5 |
| D8 | `admitRequest` is V6, then `admit`; `translateRequest` is V6, then `translate`; `grammarFault` guards `english.grammar` and `english.check` with V6, then `read`'s three checks; `checkRequest` is V6, then `firstChecked`; `sensesRequest` is V6 on the request's own environment and lexicon, then `readWithSenses`. The service's order is the boundary, the overlay check, V6, then V1 to V5. A refused vocabulary is `invalidGrammar` with fault `lexicon` and the first failure of V6, else of V1 to V5 (`lexiconFailure`). `english.check` answers `{}` only when the grammar guard passes | 2.5, 5.3, lx24 |
| D9 | Every response that is not `one` carries `class`, the Python error class the relay raises, from Lean's class table. The relay holds no class table and no text. `NotOneSentence` has the class `SyntaxError` and `InvalidOverlay` the class `VEError` | 4.2 |
| D10 | `IllTyped` has the class `TypeMismatch`. The typed check's messages carry no class (computed: `ill-typed or unbound formula`, `invalid indexed formula`), so where Python raised `UnknownSymbol` or `UnsupportedProfile`, `DELTA.md` lists a `wording` row | 4.2, Q4 |
| D11 | The `one` response carries the obligations, each with the Lean text the relay raises if its proof is not found, and the sentence spans in code points. The text has the slot `{status}`, which the relay fills with the entailment operation's status verbatim | 4.2, 4.4 |
| D12 | The advice table of S3 4.3 is completed with the two `allows` messages, one of them a pattern with free words | 4.3 |
| D13 | `english.check` decodes wire formulas with `EFormula.decode`, a left inverse of `EFormula.encode` | 5.3 |
| D14 | The service keeps prepared grammars per process, keyed by `environment_id`, `overlay_digest` and `lexicon_id`. The response is a function of the request alone | 2.7 |
| D15 | After the flip, Python's hand parser, the Lark audit and Python's premise check run only as the comparator: switched on by `VE_ENGLISH_COMPARATOR=1`, logged, never returned, never raising. The next stage deletes them | 2.8 |
| D16 | Python's producer of the lexicon stays (untrusted; V6 checks it). The ledger lists its selection logic as kept, with its callers. On the admission path it does not raise at its three overlay refusals, which the overlay check owns (D17); every other caller keeps them | 2.8, 2.9, Q1 |
| D17 | The overlay check: Lean owns the producer's three refusals of an overlay, in Python's order. O1 is a duplicate wording (`english.py:373–375`), O2 a reused risk wording (`:442–443`) and O3 an entry that the final comparison refuses (`:511–517`). A refusal is `invalidGrammar` with the code `InvalidOverlay`, of class `VEError`, and the failure `("O1"` to `"O3", kind, name)`. A constant entry is never refused | 2.3, 5.2, 8.11 |
| D18 | `Env.decode` lists the modal forms before the role wordings, so a predicate that is both gets its modal form, as Python gives it (`english.py:521–527` runs last; run by py1). This was Q7 of draft 1 | 2.2, md4 |

## 2. Definitions

### 2.1 Terms

| Term | Meaning |
|---|---|
| producer | Python's `EnglishVocabulary`, which proposes the lexicon a request carries |
| Python's choice | what the producer selects for a symbol: wording and negative, noun, spelling (2.3) |
| port | the Lean functions of 5.2 that compute Python's choice |
| declared symbol | a sort, predicate or constant of the environment's `vocabulary`: what Python's `env.sorts`, `env.predicates` and `env.constants` enumerate (`_ProfilePredicates`, `environment.py:126–146`, `:685–689`) |
| generated symbol | a symbol a profile block adds: the four `alternatives@0` words, and under `risk@0` the five `risk__…` predicates, the severity sort and the severity classes (`environment.py:656–680`). Python looks them up but never enumerates them |
| overlay check | Lean's check of the three refusals the producer makes of an overlay, O1 to O3 (D17) |
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
| `SortDecl.generated`, `PredDecl.generated`, `ConstDecl.generated : Bool := false` | the symbol is generated (2.1), not declared | set by `blockSymbols` for every symbol it adds |

`Env.roles E` is `[B.available, B.leadsTo] ++ B.optional` for the block `B`, and `[]` without one. Python's role
list is `('available', 'leads_to', 'inaction', 'taken', 'proximate')` (`english.py:396`, `:435`).
`Env.declaredSorts`, `Env.declaredPreds` and `Env.declaredConsts` are the symbols whose `generated` flag is false:
what Python enumerates (2.3).

**The overlay as submitted.** `Env.decode` merges the overlay into `Env`, and the reader keeps receiving the empty
`Overlay` (S3 record L11). The overlay check also needs to know which entries the overlay has, so the modes decode
it a second time, with `Overlay.decode` (5.3), into S3's `Overlay` structure: the sort entries with their singular
noun, the predicate entries with their wording and negative, and the constant entries with their display form. Lean's
JSON objects are ordered by key, so the entries come in key order, not in the overlay's source order. Python's
`display_environment` accepts an overlay constant entry for any name that `env.constants` contains, the severity
classes included (`english_vocabulary.py:122–124`). `Env.decode` therefore reads a display form from the overlay for
the generated constants too.

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
   them under `risk@0`: over S3's `blockRouteView`, with an empty document, as `Run.validateDeclarations` does. For
   `norm-defaults@0` the decoder is `NormDefaults.Wire.decodeSourceU`. It admits the agent-policy environment
   (md1c), refuses a malformed default (md2), and refuses `unspecified` without the profile (md3), all computed.
   Without `blockRouteView` it refuses the environment's data flags (md1c).
2. **The typing view.** It removes what the typed check of formulas does not read, as `riskNormsView` removes the
   unit annotations.
3. **The identity.** It is computed over the submitted environment.
4. **The lexical decoding.** `Env.decode` reads each modal form through `modalForm`, which calls the frozen
   `Norms.Wire.decodeRegulated`. That decoder refuses a `default` of `unspecified`. md1a computes the refusal on the
   agent-policy environment: `InvalidInput: invalid regulated role or default for permitted`. Under
   `norm-defaults@0`, `Env.decode` therefore passes `modalForm` the entry with `unspecified` read as the placeholder
   `deny` (`placeholderEntry`, 5.3). This is the reading of `NormDefaults.Wire.placeholderJson`, entry by entry. A
   modal form depends on the role and the act only, so the placeholder changes no form, and the submitted values
   still reach part 1 and the identity. md1b computes the two forms, `{0} may be performed` and
   `{0} must be reported to the user`. A default that is neither `allow`, `deny` nor `unspecified` is still refused,
   by part 1 and by `Env.decode` alike (md2). Without the profile, part 1 refuses `unspecified` (md3).

With parts 3 and 4 the port's `lexicon_id` equals Python's on all four rows (md5, computed). Part 1 is computed for
`norm-defaults@0` only, and part 2 is not computed (ev14b).

**Modal forms first** (D18). `Env.decode` appends the modal forms after the role wordings in `forms.wordings`, so
`forms.wordings.lookup` gives a predicate that is both a role and modal its role wording, while Python gives it the
modal form (`english.py:521–527` runs last; py1 ran the producer on it, md4). E2.0 lists the modal forms first. md4
computes both orders on a direct `Env.decode`. The boundary refuses such an environment today (`AlternativesRegulated: available available`), so the
change alters no admitted environment; it makes `Env.decode` agree with Python on its own.

`Route.Gate.decodeEnvelope` and the frozen decoders are not edited. If the lean-first batch 12b lands first, its
`environment` mode is called instead (plan, question 6).

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

**Enumeration** (D1). Python's `env.sorts`, `env.predicates` and `env.constants` are `_ProfilePredicates` under the
profiles that generate symbols: looking a name up finds a generated symbol, but enumerating lists the declared ones
only (`environment.py:126–146`, `:685–689`). So the generated symbols own no word, head or noun, and Python never
compares a declared symbol with them. `Env.decode` lists both, so the port enumerates `E.declaredSorts`,
`E.declaredPreds` and `E.declaredConsts` at each site where Python enumerates:

- in `lintCodes`, every owner, head, noun, negated head and the duplicate count (`printer.py:196–216`, `:250`);
- in `templateCodes`, the nouns (`:206–211`);
- in `acceptsDeclared`, the rescue's names and heads, the `is` heads, the noun words, the idiom branch's constants
  and predicates, the suggested path's constants, heads and wordings, and `duplicateWording` (`english.py:259–372`);
- in `policyNouns`, the symbols a noun may not equal and the sorts that are deduplicated (`:239–252`);
- in `policySpellings`, the constants whose display form is selected (`:476–488`).

The generated symbols stay in V6's domain, in the initial spellings and the fixpoint (`:460–470`, `:500–510`), and in
the severity noun (`:419`). The fixpoint quotes any constant that the overlay names, a severity class included
(`self.declared_constants`, `:474–475`). lx32 computes what draft 1 got wrong: `{0} is fully avoidable` under
`alternatives@0`, `{0} is fully minor` under `risk@0`, and a declared noun equal to the severity sort's name. Draft
1's port refuses Python's choice in each; draft 2's selects it.

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
| `SORT_NOUN` | one or two arguments: the tokens of a declared sort's name, singular or plural occur in a row in the wording's tokens (`templateCodes`, which also gives `TEMPLATE_LENGTH`) |
| `DUPLICATE_TEMPLATE` | another predicate declares exactly the same wording |
| `TEMPLATE_SHAPE` | the wording is not `{0} ` + phrase (+ ` {1}`), the phrase being non-empty and on one line; or, for one argument, the phrase does not begin with `is` followed by a word; or, for more arguments, `template_parts` refuses it |
| `PHRASE_SYNTAX` | the phrase is not lower-case ASCII words separated by single spaces |
| `LOGICAL_WORD` | a token is a logical word, with the closure words under `closure@0`; `at` alone is allowed as an n-ary connector |
| `VARIABLE_TOKEN` | a token is `x` followed by digits, or capitals followed by digits |
| `SYMBOL_COLLISION` | a token is owned by another declared symbol. A declared symbol owns its name. A declared predicate owns the head of its declared wording, or of its strict wording when it declares none. A declared sort owns the last token of its singular and of its plural |
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
   - no `[a-z][a-z0-9_-]*` word of the lower-cased phrase is a negated head;
   - it carries no `NEGATED_HEAD`.

   This path is the one place where Python's case rules reach an accepted wording. `unary_phrase` matches its pattern
   under `re.I` (`english_phrases.py:24`), and so does the constants test (`english.py:351`). Under `re.I` the class
   `[A-Za-z]` also matches four letters beyond ASCII, `İ` (U+0130), `ı` (U+0131), `ſ` (U+017F) and the Kelvin sign
   (U+212A). The literal `i` also matches `İ` and `ı`, and `s` matches `ſ` (the `re` documentation of `IGNORECASE`;
   `re/_casefix.py`). py1 ran Python over every code point and printed exactly these letters; `a` and `n` match
   only themselves. The port follows: `reILetter` is the letter class, `reIFold` folds a character to the ASCII
   letter it is matched as, `wordOccursI` compares under that folding with these letters counted as word characters,
   and the negated-head words are taken from `pyLower` of the phrase, Python's `phrase.lower()`. lx31c computes the
   difference from draft 1 on `{0} is Keen` with the Kelvin sign: Python accepts it (py1), and draft 2 does; draft 1
   did not.
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
  - For each declared sort, the base noun is the declared noun, else the sort's name. It is kept when it is ASCII
    letter words, none of them reserved once lower-cased, and the lower-cased noun is no declared predicate's or
    constant's name; otherwise the noun is the fallback `entity of sort "s"`.
  - Every declared sort's noun whose key another declared sort's noun shares becomes the fallback.
  - A profile-fixed noun, `severity`, replaces the result; the generated severity sort gets it.
- **`policySpellings`.**
  - For every constant, generated ones included, the bare name is used when it is lower-case letters, not reserved
    and not `is` or `has`; otherwise the quoted name. A declared constant with a display form starts quoted.
  - A declared constant's display form is kept when it is ASCII letter words, has no reserved word other than
    `the`, has no selected noun's key, and is the only such form with its key.
  - Then, until nothing changes, every constant that has a display form, is not quoted and shares a spelling key
    with another constant is quoted. A value's spelling keys are those of itself, of `The …` when it begins with
    `the `, and of `the …` when it is lower-case letters.

**V6** (`Lexicon.policyFailures`, D1). Each of the following is a failure:

- `("V6", "predicate", p)`: the selected wording of a predicate `p` is neither Python's choice nor
  `fallbackWording p k`;
- `("V6", "negative", p)`: a selected negative of `p` is not Python's negative for `p`, or `p`'s selected wording is
  not Python's;
- `("V6", "sort", s)`: the selected noun of `s` is neither Python's nor `entity of sort "s"`;
- `("V6", "constant", c)`: the selected spelling of `c` is neither Python's nor the quoted name.

`Lexicon.policyOk E O L` holds when there is none.

The freedom V6 leaves is the conservative one: a producer may write any symbol in its quoted form, and may omit a
negative. It cannot select a wording, noun or spelling that Python refuses. V6 alone still widens one thing: Python
refuses an overlay whose entry it would not select as written, while V6 accepts the same lexicon with that entry on
its fallback. The overlay check below closes that. With both, and with `display_environment` still run first in
Python (2.8), nothing becomes a warning, and nothing Python refuses today is admitted (S3 D14, R4).

**The overlay check** (`overlayCheck`, D17). For an overlay, Python's producer raises `VEError` at three sites, and
the selected lexicon cannot show their decisions: the first runs before the role wordings are restored, and the
last runs before the modal forms are put in and counts linter issues left under an entry's path. The check states
each site in Python's order, and the first that fails is the refusal.

1. **O1, a duplicate wording** (`english.py:368–375`, in the main loop). A predicate entry of one or two arguments
   whose wording or negative has the key of another declared predicate's wording or negative (`duplicateWording`,
   the fourth stage of `acceptsDeclared`). A role predicate is no exception, although `:399` would restore its
   wording (ov8).
2. **O2, a reused risk wording** (`:436–443`). Under `risk@0`, a predicate entry that is not exempt (a role,
   `risk__…`, one of the four words) and whose main selection has the key of a risk template (`riskKeyed`).
3. **O3, the final comparison** (`:511–517`). A sort entry whose selected noun is not its singular. A predicate entry,
   other than a role, whose declared wording `acceptsDeclared` refuses, or whose declared negative is left with a
   linter issue (`negativeLeft`): for one or two arguments, a negative that is not selected; for more, a negative the
   linter reports. Sort entries come before predicate entries.

O3's two tests are Python's comparison (`selected != expected`, or an issue left under the entry's path), derived
from the source:

- *Sorts.* A sort entry's issues are removed exactly when its deduplicated noun is its singular (`:255–258`). An
  overlay sort is declared, so no profile replaces its noun, and the comparison fails exactly when the selected noun
  is not the singular.
- *Accepted wordings.* A predicate entry, other than a role, whose wording is accepted keeps it to `:511`, and the
  issues under `…/verbalisation` are removed (`:272`, `:378`). An entry that O2 would change has already been refused.
- *Refused wordings.* An entry whose wording is refused gets the fallback, which is not its wording. If the wording
  were the fallback text itself, its quote would carry `PHRASE_SYNTAX`, an issue left under the path. Either way the
  comparison fails.
- *Roles.* A role's wording is restored and every issue under its path removed (`:396–400`), so O3 never refuses a
  role.
- *Negatives.* The issues under `…/negative_verbalisation` are removed only when the negative is selected (`:389`).
  For an accepted wording of one or two arguments, the linter's negative of the wording equals the producer's
  (`printer.py:119–135`, `english_vocabulary.py:58–71`), so a declared negative is left with an issue exactly when it
  is not selected. A negative of more arguments is never selected (`:269–273`), so it is left with an issue exactly
  when the linter reports one: `templateCodes`, or not `negateVerb` of the wording (`printer.py:309–322`).

A constant entry is never refused: a bad display form keeps its quoted name (`english.py:471–510`).
`overlayCheck_constants` states this (5.5), and ov6 computes it.

The check reads an overlay that `display_environment` has already admitted. That function stays in Python (2.9) and
refuses some overlays before the producer's main loop: an unknown symbol, a malformed entry, a suggested entry
without consent, and an overlay whose display environment Python's `Environment` refuses. An example of the last is
an overlay that rewrites the fixed wording of an `alternatives@0` role (ov11a, ov11b, run by py1). Lean does not
repeat these checks.

The refusal is the failure `("O1", "predicate", p)`, `("O2", "predicate", p)`, `("O3", "sort", s)` or
`("O3", "predicate", p)`. Within one site the entries come in Lean's order (2.2). When two entries fail at one site,
the entry named may therefore differ from Python's; the site and the verdict do not. The response is 4.4's
`InvalidOverlay`, of class `VEError`, Python's class today. An overlay refusal is the author's input error, so it is
not `CheckerUnavailable`.

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
math closure environment. The other 4 are the environments the boundary refuses (2.2), so the S3 build reads no
lexicon for them. Decoded as E2.0 decodes them (part 4), with the identity over the submitted environment, they give
Python's `lexicon_id` too (md5), so the port reproduces all 22. The overlay check refuses none of the four corpus
overlays, which Python's producer admitted (ovc). The 17 round-trip configurations of the report are built in
Python and were not reproduced (Q3).

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
  `.refused (.invalidGrammar .lexicon)`. `english.read` in authoring mode runs it.
- **The translation guard, `translateRequest E O L cap b s`,** is `translate E O L cap b s` when `L.policyOk E O`, and
  otherwise `.invalidGrammar .lexicon`. `english.read` in translation mode runs it (tg1, tg2).
- **The grammar guard, `grammarFault E O L`,** is the first refusal of V6, then of `read`'s three checks of the
  grammar (V1 to V5, well formed, typed), or `none`. `english.grammar` exports `grammar E L` only when it is `none`,
  and otherwise answers `invalidGrammar` with the fault (gg1, gg2).
- **`checkRequest E O L b rs cs`** is `firstChecked E O L b rs cs` when `L.policyOk E O`, and otherwise `none`.
  `english.check` runs it after the grammar guard. A refused vocabulary is therefore `invalidGrammar`, and `{}` means
  only that no candidate reads back (ev4d). The renderer displays the candidate it names, or the source for `{}`; for
  `invalidGrammar` the relay raises the class (2.8).
- **`sensesRequest D E L b s`** is `readWithSenses D E L b s` when `L.policyOk E {}`, and otherwise
  `.invalidGrammar .lexicon`. `senses.read` runs it, on the document's own environment and lexicon.
- **The order.** Every mode checks, in this order, and answers with the first refusal:
  1. the boundary: the case decodes, the environment is admitted (2.2), the lexicon names its environment (D6);
  2. the overlay check, on the decoded overlay (2.3);
  3. V6;
  4. V1 to V5, then the grammar's well-formedness and typing.

  The request functions give 3 and 4. An `invalidGrammar lexicon` response names the first failure of
  `L.policyFailures E O ++ L.failures E O` (`lexiconFailure`). For lx24, which fails V2, V5 and V6, that is
  `("V6", "negative", "hazard")`. This is the order of Python's producer, whose overlay refusals precede the
  selection that V6 checks.
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
| `english.grammar` | `{id, environment, overlay?, lexicon}` | the export of S3's `grammarCase`, plus `codes` (the class table) and `advice` (the advice rows), when `grammarFault` is `none`; else `invalidGrammar` |
| `english.check` | `{id, environment, overlay?, lexicon, formulas, marks, candidates}` | when `grammarFault` is `none`, `{"index": i}` or `{}`; else `invalidGrammar`. Each with the five identities other than `source_sha256` |

Each mode decodes the case (S3's `decodeCase`, with D6 and D7), then decodes the overlay with `Overlay.decode` and
runs `overlayCheck` on it, then its request function, in the order of 2.5. An overlay refusal is the response
`InvalidOverlay` of 4.4 in every mode.

`english.check` decodes each formula with `EFormula.decode` (5.3), which refuses a formula it cannot decode as
`InvalidInput`. It requires one mark per formula.

**The cache** (D14). The prepared grammar is kept per process, keyed by `environment_id`, `overlay_digest` (empty
without an overlay) and `lexicon_id`. With the build, which fixes `actions_version`, these cover every input of
preparation, since the overlay changes the declared wordings that V2, V4 and V6 read and the entries that the
overlay check reads. The response is a function of
the request alone, and a cache hit only skips work (ev3, ev3b). This is the handle pattern of lean-first batch 2,
already on `main`.

**Retired.** The `ve_english_route` executable and its transport in `ve/backends/lean.py` are deleted. ev2 checks the
service mode against S2's route fixtures first.

### 2.8 The relay and the comparator (Python)

- **The producer on the admission path.** The relay builds `EnglishVocabulary` with its three overlay refusals
  (`english.py:373–375`, `:442–443`, `:511–517`) switched off, so that the producer selects the fallback where it
  would raise and the request reaches Lean, whose overlay check refuses it (D16, D17). Every other caller of the
  producer keeps the three refusals. `display_environment`'s own checks of the overlay, its consent gate and its
  validation of the display environment run first, unchanged (2.9, kept).
- **Admission** (`parse_english`, `parse_english_with_metadata`, `parse_english_argument`). The relay sends the
  environment, the overlay, the producer's lexicon and the source to `english.read`. For any status but `one`, it
  raises `ERRORS[response["class"]](response["text"])`, with the span of 4.4. For `one`, it calls
  `prove_entailment(env, premises, conclusion)` for each obligation and, when the result is not `Found`, raises
  `SyntaxError` with the obligation's `unproved` text, its slot `{status}` replaced by the result's status, verbatim.
  `parse_english_argument` builds its claim graph from the obligations' premises and the certificates.
  `_check_conclusions`' premise computation goes; its entailment call is what the relay keeps.
- **Rendering.** `render_english` sends, for each formula, its three candidate sentences (with `Therefore ` when
  marked) to `english.check` and keeps the named one, or raises the existing `ValueError` when the answer is `{}`.
  It then sends the assembled document as the one candidate for all formulas and marks. `parse_english_with_metadata`
  sends the rendering as the one candidate, and displays the source when the answer is `{}`. An `invalidGrammar`
  answer is raised with its class, as for admission. Python's re-parse of its own renderings (`english.py:833`,
  `:855`, `:1780`) is deleted.
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
  tokens; `display_environment`'s checks of the overlay, with the `accept_suggested_vocabulary` consent gate and the
  validation of the display environment; and,
  until E3, the statement layers that construct `EnglishParser` themselves.

### 2.9 The deletion ledger

`docs/lean-first/e2/LEDGER.md` has one row per decision site, each with a disposition: *owned by Lean* (the Lean
check named), *comparator* (off the admission path, deleted in the next stage), or *kept* (its caller named).

| Site | Disposition |
|---|---|
| `english.py:1673–1695` `_python_reading`: hand parser, Lark audit, `check_document` | comparator |
| `english.py:1718–1722` `dispatch.shadowed('english.admission', …)` | owned by Lean: `admitRequest` via the relay; `SHADOW_ONLY` entry removed |
| `english.py:1712–1713` the source byte limit | owned by Lean: `sourceTooLong` |
| `english.py:1765–1766` `A conclusion needs an earlier premise.` | owned by Lean: `noPremise` (`ConclusionWithoutPremise`) |
| `english.py:1767–1770`, `:1817–1819` the entailment refusal | kept (relay; D10 of S3): the text is Lean's `unproved`, with the prover's status in its slot |
| `english.py:1811–1812`, `:1816` the premises of each marked conclusion | owned by Lean: `obligations` |
| `english.py:833`, `:855`, `:1780` re-parse of renderings | owned by Lean: `checkRequest` |
| `english.py:888–1636` `EnglishParser` | comparator for admission; kept for `norm_english.py` and `norm_defaults_english.py` until E3 |
| `surface/unambiguity.py` `require_unique_derivation`, `require_correspondence` | comparator for admission; kept for the statement layers that call them until E3 |
| `english.py:230–527` `EnglishVocabulary` selection, `_RESERVED` | kept: the producer, checked by V6 (Q1) |
| `english.py:373–375` the duplicate wording of an overlay entry | owned by Lean: O1 of `overlayCheck`; off on the admission path, kept for the other callers |
| `english.py:442–443` an overlay entry's reused risk wording | owned by Lean: O2; off on the admission path, kept for the other callers |
| `english.py:511–517` the final comparison of the overlay's sort and predicate entries | owned by Lean: O3; off on the admission path, kept for the other callers |
| `english_vocabulary.py:90–132` `display_environment`: the overlay's format, identity, symbols and fields, the `accept_suggested_vocabulary` consent gate (`:113–114`), and the validation of the display environment by `Environment(data)` (`:131`), which refuses, for instance, a rewritten `alternatives@0` role wording | kept: it decides whether a suggested entry may be used at all, and whether the display environment is an environment, before any Lean call (rl8, ov11) |
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
  those of lx27 and lx28. Under `alternatives@0` and `risk@0` it adds wordings and nouns made of the generated names:
  each of the four words, each severity class and the severity sort's name, in a wording as lx32a and lx32b write
  them and as a noun as lx32c does. It adds the suggested wordings of lx31. A difference is a port defect or a signed
  `DELTA.md` row.
- **The overlay parity harness.** On every corpus overlay, and on overlay mutants over every corpus environment,
  Python's producer with its refusals on and `overlayCheck` are compared: raise against no raise, and the site (O1 to
  O3). A mutant replaces or adds one overlay entry: a predicate entry with a wording of 8.1, with such a wording and
  a negative that is not its negation, with a risk template under `risk@0`, or with another predicate's wording; a
  sort entry with a noun of lx27; or a constant entry from lx28. The expectations come from running Python, never
  from the port. A mutant that `display_environment` refuses (ov11) is refused before any Lean call on the admission
  path too: the harness records it and compares neither the raise nor the site for it.
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
| Trusted definitions | the port (`Policy.lean`: word lists, pattern tables, scanners, lint, acceptance, selection, V6, the overlay check); `displayJson`; `Overlay.decode`; the boundary extension (a link to existing decoders) with `placeholderEntry`; `admitRequest`, `translateRequest`, `grammarFault`, `lexiconFailure`, `checkRequest`, `sensesRequest`; `EFormula.decode`; the class table, the texts and the advice table |
| Proved | `policy_iff_no_failure`, `policy_selection`, `admitRequest_ok`, `admitRequest_exact`, `admitRequest_policy`, `translateRequest_policy`, `grammarFault_none`, `overlayCheck_constants`, `checkRequest_some`, `sensesRequest_policy`, `codeClasses_total`, `decode_encode`, the three `runMode` equations |
| Checked per request | the overlay check on the request's overlay; V6 on the request's own inputs; the lexicon's identity against the display environment |
| Tested only | the port against Python (pt1, the parity harness); the overlay check against Python (the overlay parity harness); the boundary extension (ev14, md1 to md5); the cache's transparency (ev3, ev3b); the relay and the comparator (rl1 to rl11, ev6, ev7); the corpus evidence; latency |
| Outside | the proof of each obligation (the entailment operation); the producer's choice beyond V6; `rights@0` wordings; letters |

## 3. English: one reading each

E2 adds no wording to the grammar, and every form of S3 3.1 keeps its meaning. What changes is who decides, and
the texts shown.

**Claim sentences.** From the flip, a record of an admitted document carries C2 with the six identities, C4 when a
mark is present, and C5 (S3 3.2) when every obligation was proved.

**The texts added** are those of 4.2. Each says what happened, in the reader's terms, and names the sentence from
one, or the overlay entry.

**The theorems, in plain words.**

| Statement | Plain English | It does not say |
|---|---|---|
| `policy_iff_no_failure` | The vocabulary policy passes exactly when it reports no failure. | |
| `policy_selection` | If the policy passes, every selected wording, noun and spelling is Python's choice or the quoted form, and every selected negative is Python's beside Python's wording. | that Python's choice is the port's on every environment: that is tested (pt1) |
| `admitRequest_ok` | If admission succeeds, the vocabulary passed the policy, the text has one reading per sentence, the obligations are those of the reading, and each has a premise. | that an obligation is provable |
| `admitRequest_exact` | Admission succeeds exactly when the vocabulary passes the policy, the reader returns the reading, and every marked sentence has an earlier unmarked one. | |
| `admitRequest_policy` | A vocabulary that fails the policy is refused before any text is read. | |
| `translateRequest_policy` | In translation mode too, a vocabulary that fails the policy is refused before any text is read. | |
| `grammarFault_none` | If the grammar guard lets a vocabulary through, it passed the policy and conditions V1 to V5. | that the grammar is unambiguous |
| `overlayCheck_constants` | Whether an overlay is refused does not depend on its constant entries. | anything about the constants' spellings |
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
| `BadCharacter`, `OpenQuote`, `BadNumeral`, `EmptyDocument`, `EmptySentence`, `Unterminated`, `BadSpacing`, `UnboundReference`, `ShadowedName`, `SortMismatch`, `MarkerDepth`, `CoefficientNotNumeral`, `PronounUnresolved`, `BlockedWording`, `CoordinationRepeated`, `CoordinationForm`, `NaturalScoped`, `RelativeForm`, `NoDerivation`, `ConclusionWithoutPremise`, `ConclusionNotDerived`, `NotOneSentence` | `SyntaxError` |
| `Ambiguous` | `AmbiguousDerivation` |
| `IllTyped` | `TypeMismatch` (D10) |
| `InvalidGrammar`, `Internal` | `CheckerUnavailable` |
| `InvalidOverlay` | `VEError` (D17) |

`RelativeForm` was `SyntaxError` or a typing class depending on the text (`english_lean.py:64`); it is
`SyntaxError`. Where Python raised another class, that is a `wording` row, and the comparator keeps the tolerance.
`NotOneSentence` is translation mode's refusal of a source with more than one sentence (S3 build, `Run.lean:278`);
draft 1's table missed it (cn19). `InvalidOverlay` keeps the class Python raises at the three overlay sites today. An
overlay refusal is the author's input error, so it is not `CheckerUnavailable`, which `InvalidGrammar` keeps (rl6).

**Texts added.** The texts of `rejectText` (S3 build, `Run.lean:40–69`) stand. E2 adds the following.

| Code | Text (computed for cn3 and an obligation of sentence 2) | Python today |
|---|---|---|
| `ConclusionWithoutPremise` | `Sentence 1 is marked as a conclusion, and no earlier sentence is a premise.` | `A conclusion needs an earlier premise.` |
| `ConclusionNotDerived` (the obligation's `unproved`) | `Sentence 2 is marked as a conclusion, and no checked derivation from the earlier premises was found: {status}`, the relay putting the entailment operation's status for `{status}` | `The marked conclusion has no checked derivation from earlier premises: <status>` (`english.py:1769–1770`); the same without the status from `parse_english_argument` (`:1819`) |
| `InvalidGrammar` with a V6 failure | S3's text, with `failure` `["V6", kind, name]` | no error: Python's producer selects the quoted fallback |
| `InvalidOverlay`, O1 | `The vocabulary overlay gives p a wording that another symbol already has. No text was read.` | `Duplicate English wording '<wording>' for 'p'; existing symbol(s): …` (`english.py:374–375`) |
| `InvalidOverlay`, O2 | `The vocabulary overlay gives p a wording that risk@0 reserves. No text was read.` | `English wording for 'p' reuses a risk@0 wording` (`:443`) |
| `InvalidOverlay`, O3 | `The vocabulary overlay entry for n cannot be used as written. No text was read.` | `English vocabulary entry fails the template linter: sorts/n` or `predicates/n` (`:517`) |
| `NotOneSentence` | S3's text: `This text has more than one sentence. Translation mode reads exactly one.` | none: Python has no translation mode |

The three `InvalidOverlay` texts were computed for `inspected`, `hazard` and `item` (ov1b, ov2b, ov5b). The
`unproved` text keeps the prover's status, so a prover fault does not read like "not derivable" (GE2 item 4). Every
text that differs from Python's is a `wording` row of `DELTA.md`.

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
| `one` | `obligations`: `[{"conclusion": i, "premises": [j, …], "unproved": text}]`, empty without marks, `text` with the slot `{status}`; `spans`: one `[start, end)` per sentence, in code points of the source as sent |
| `rejected` | `class`; `span`, the sentence's `[start, end)` in code points, or the offending character's for a lexical rejection; code `ConclusionWithoutPremise` with `sentence` 0; code `NotOneSentence` in translation mode |
| `none`, `many`, `budget` | `class`; `span`; for `none`, `advice` (`{"id", "text"}`) when the table gives one |
| `invalidGrammar` | `class`. With code `InvalidGrammar`: `fault`, and for fault `lexicon` the `failure` that `lexiconFailure` names, V6 before V1 to V5. With code `InvalidOverlay`: the overlay check's `failure`, `["O1", "predicate", p]`, `["O2", "predicate", p]`, `["O3", "sort", s]` or `["O3", "predicate", p]`, and no `fault` |

`english.check` returns `{"index": i}` or `{}` with five identities when the grammar guard passes, and the
`invalidGrammar` response otherwise. `english.grammar` adds `codes` (pairs of code and class) and `advice` (the rows of
4.3, with the profile and patterns).

## 5. Lean: definitions and the exact statements

### 5.1 Modules and conventions

Conventions are as in S2 5.1. The stub elaborated everything below in one namespace, with the three new fields held
beside `Env` (section 12).

| Module | Change |
|---|---|
| `Lexicon.lean` | the fields of 2.2; `Env.roles`, `Env.pluralOf`, `Env.suggestedPred`, `Env.declaredSorts`, `Env.declaredPreds`, `Env.declaredConsts`, `Env.generatedSorts` |
| `Policy.lean` (new) | 5.2, the overlay check included |
| `Advice.lean` (new) | the advice table and `advice` (5.3) |
| `Encode.lean` | the decoding of the new fields; the `generated` flags in `blockSymbols`; `placeholderEntry` and the modal forms first in `Env.decode` (D7, D18); `Overlay.decode`; `EFormula.decode`; `displayJson` |
| `Read.lean` | `admitRequest`, `translateRequest`, `grammarFault`, `lexiconFailure`, `checkRequest` |
| `Run.lean` | the modes' cases, with the order of 2.5; the class table and texts; D6 in `decodeCase`; the boundary of D7 |
| `Service/Protocol.lean` | three constructors of `Mode` with their `rfl` theorems |
| `ResponseShape/Encoders.lean` | `runMode_fits` for the three modes |
| `Senses/Read.lean` | `sensesRequest`; the senses mode calls it |

### 5.2 The fields, and `Policy.lean`

```lean
namespace VE.EnglishGrammar

-- SortDecl gains:   plural : Option String := none
--                   generated : Bool := false          -- the severity sort
-- PredDecl gains:   suggested : Bool := false
--                   generated : Bool := false          -- the four alternatives@0 words, the five risk__ predicates
-- ConstDecl gains:  generated : Bool := false          -- the severity classes
-- AltBlock gains:   optional : List String := []       -- inaction, taken, proximate, where present

def Env.roles (E : Env) : List String :=
  match E.alternatives with
  | some B => [B.available, B.leadsTo] ++ B.optional
  | none => []
def Env.pluralOf (E : Env) (s : String) : Option String := (E.sorts.find? (·.name == s)).bind (·.plural)
def Env.suggestedPred (E : Env) (p : String) : Bool := ((E.predicate? p).map (·.suggested)).getD false
/-- What Python enumerates (`_ProfilePredicates`, environment.py:126–146): the declared symbols. -/
def Env.declaredSorts (E : Env) : List SortDecl := E.sorts.filter (!·.generated)
def Env.declaredPreds (E : Env) : List PredDecl := E.predicates.filter (!·.generated)
def Env.declaredConsts (E : Env) : List ConstDecl := E.constants.filter (!·.generated)
def Env.generatedSorts (E : Env) : List SortDecl := E.sorts.filter (·.generated)

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

/-- The letters `[A-Za-z]` matches under `re.I` beyond ASCII: `İ`, `ı`, `ſ` and the Kelvin sign. -/
def reIExtra : List Char := [Char.ofNat 0x130, Char.ofNat 0x131, Char.ofNat 0x17F, Char.ofNat 0x212A]
def reILetter (c : Char) : Bool := isLetter c || reIExtra.contains c
/-- The ASCII letter a character is matched as under `re.I`: `İ` and `ı` as `i`, `ſ` as `s`, the Kelvin sign as `k`. -/
def reIFold (c : Char) : Char :=
  if isUpper c then Char.ofNat (c.toNat + 32)
  else if c.toNat == 0x130 || c.toNat == 0x131 then 'i'
  else if c.toNat == 0x17F then 's'
  else if c.toNat == 0x212A then 'k'
  else c

/-- `re.search(r'\b' + re.escape(tok) + r'\b', phrase, re.I)` on a phrase of `unaryPhrase`: characters compared
as `reIFold` folds them, `reIExtra`'s letters counted as word characters. -/
def wordOccursI (tok phrase : String) : Bool :=
  let t := tok.toList.map reIFold
  let p := phrase.toList
  let w (i : Nat) : Bool := match p[i]? with | some c => isW c || reIExtra.contains c | none => false
  let wb (i : Nat) : Bool := if i == 0 then false else w (i - 1)
  !t.isEmpty && (List.range (p.length + 1)).any fun i =>
    i + t.length ≤ p.length && ((p.drop i).take t.length).map reIFold == t &&
    wb i != w i && wb (i + t.length) != w (i + t.length)

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

/-- `template_parts` (`ve/surface/nary.py:13–34`): subject first, as V3 requires (S3 D8). -/
def templateParts (v : String) (k : Nat) : Option (List String) :=
  if braceSlots v != (List.range k).map (fun i => "{" ++ toString i ++ "}") then none else
  let parts := splitSlots v
  if parts.length != k + 1 then none else
  let mids := (parts.drop 1).take (k - 1)
  if !mids.all (·.startsWith " ") then none else
  let first := parts.headD ""
  if !first.isEmpty then none else
  if !mids.all (connector · true) then none else
  let last := parts.getLastD ""
  if !(last.isEmpty || connector last false) then none else
  if !(splitWs (parts.getD 1 "")).any naryHeads.contains then none else
  some parts

/-- A phrase against a pattern: `some adjective?` when it matches. -/
def matchPattern (phrase : String) (pat : List PatWord) : Option (Option String) :=
  let parts := phrase.splitOn " "
  if parts.length != pat.length then none
  else if (parts.zip pat).all (fun (w, p) => match p with | .lit s => w == s | .adj => lowerWord w) then
    some ((parts.zip pat).findSome? fun (w, p) => match p with | .adj => some w | _ => none)
  else none

/-- `unary_phrase` (english_phrases.py:23–31). Its pattern is matched under `re.I`: `is` as `reIFold` folds it, and
`reILetter`'s letters. -/
def unaryPhrase (t : String) : Option String :=
  if t.length > 80 || !t.startsWith "{0} " then none else
  let rest := t.drop 4
  if (rest.take 3).toList.map reIFold != ['i', 's', ' '] then none else
  let body := rest.drop 3
  let tokOk (w : String) : Bool := match w.toList with
    | c :: cs => reILetter c && cs.all fun d => reILetter d || isDigit d || d == '_'
    | [] => false
  let phraseOk (s : String) : Bool := !s.isEmpty && ((s.splitOn " ").flatMap (·.splitOn "-")).all tokOk
  let candidates : List String :=
    (if asciiLower (body.take 2) == "a " then [body.drop 2] else []) ++
    (if asciiLower (body.take 3) == "an " then [body.drop 3] else []) ++ [body]
  match candidates.find? phraseOk with
  | none => none
  | some phrase =>
    let low := pyLower phrase
    if low == "a" || low == "an" || (splitWs low).any (fun w => boundaryWords.contains w || blockedWords.contains w)
    then none else some phrase

/-! Python's vocabulary policy (english.py:230–527, printer.py:183–338) -/
def sortNouns (E : Env) (O : Overlay) (s : SortDecl) : List String :=
  match E.declaredNoun O s.name with
  | some n => [n] ++ (E.pluralOf s.name).toList
  | none => []

/-- `template_checks` (printer.py:223–232): the length and sort-noun codes of a wording or a negative. -/
def templateCodes (E : Env) (O : Overlay) (value : String) : List String :=
  let nouns := E.declaredSorts.map (·.name) ++ E.declaredSorts.flatMap (sortNouns E O)
  let tw := tokens value
  (if value.length > 80 || (splitWs value).length > 8 then ["TEMPLATE_LENGTH"] else []) ++
  (if nouns.any (fun n => let ts := tokens n; !ts.isEmpty &&
      (List.range (tw.length + 1)).any fun i => (tw.drop i).take ts.length == ts) then ["SORT_NOUN"] else [])

/-- The lint codes of a declared wording `value` of predicate `name` (`_NaturalVocabulary`). -/
def lintCodes (E : Env) (O : Overlay) (name value : String) (k : Nat) : List String :=
  let predNames := E.declaredPreds.map (·.name)
  let names := E.declaredSorts.map (·.name) ++ predNames ++ E.declaredConsts.map (·.name)
  let heads : List (String × String) := E.declaredPreds.filterMap fun d =>
    (templateHead ((E.declaredWording O d.name).getD (strictWording d.name d.arity)) d.arity).map (·, d.name)
  let nounTexts : List (String × String) := E.declaredSorts.flatMap fun s => (sortNouns E O s).map (·, s.name)
  let owned (w : String) : Bool :=
    names.any (fun x => x == w && x != name) || heads.any (fun (h, p) => h == w && p != name) ||
    nounTexts.any fun (n, s) => (tokens n).getLast? == some w && s != name
  let predicateHeads := predNames ++ heads.map (·.1)
  let negatedHeads := ["un", "non", "un-", "non-"].flatMap fun pre => predicateHeads.map (pre ++ ·)
  let forbidden := logicalWords ++ (if E.profiles.contains "closure@0" then closureWords else [])
  let phraseCodes (phrase : String) (conn : Bool) : List String :=
    let wds := tokens phrase
    let forb := if conn && phrase == "at" then forbidden.filter (· != "at") else forbidden
    (if wordsPhrase phrase then [] else ["PHRASE_SYNTAX"]) ++
    (if wds.any forb.contains then ["LOGICAL_WORD"] else []) ++
    (if wds.any variableWord then ["VARIABLE_TOKEN"] else []) ++
    (if wds.any owned then ["SYMBOL_COLLISION"] else []) ++
    (if wds.any negatedHeads.contains then ["NEGATED_HEAD"] else [])
  let dup := if (E.declaredPreds.filter fun d => E.declaredWording O d.name == some value).length > 1
    then ["DUPLICATE_TEMPLATE"] else []
  if k > 2 then
    let len := if value.length > 160 || (splitWs value).length > 24 then ["TEMPLATE_LENGTH"] else []
    match templateParts value k with
    | none => dup ++ ["TEMPLATE_SHAPE"] ++ len
    | some parts => dup ++ len ++ (parts.drop 1).flatMap fun ph =>
        let s := stripWs ph
        if s.isEmpty then [] else phraseCodes s true
  else
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
    (templateCodes E O value ++ dup ++ shape).eraseDups

/-- Step 4 of `acceptsDeclared` (english.py:368–372): the key of `p`'s declared wording or negative is the key of
another declared predicate's wording (its strict wording when it declares none) or declared negative. -/
def duplicateWording (E : Env) (O : Overlay) (p : String) : Bool :=
  let ownTexts (d2 : PredDecl) : List String :=
    [(E.declaredWording O d2.name).getD (strictWording d2.name d2.arity)] ++ (E.declaredNegative O d2.name).toList
  let mine := (E.declaredWording O p).toList ++ (E.declaredNegative O p).toList
  (E.declaredPreds.filter (·.name != p)).any fun d2 =>
    (ownTexts d2).any fun x => mine.any fun y => wordingKey x == wordingKey y

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
    let others := E.declaredPreds.filter (·.name != name)
    let collision :=
      ((E.declaredPreds.map (·.name) ++ E.declaredConsts.map (·.name)).filter (· != name)).any
        (wordOccurs · phrase) ||
      others.any fun d2 => match templateHead ((E.declaredWording O d2.name).getD "") d2.arity with
        | some h => !["is", "was", "a", "an"].contains h && wordOccurs h phrase
        | none => false
    let isHeads := E.declaredPreds.filterMap fun d2 => match E.declaredWording O d2.name with
      | some v => if v.startsWith "{0} is " then (splitWs v)[2]? else none
      | none => none
    let negated := (splitWs phrase).any fun w =>
      (E.declaredPreds.map (·.name) ++ isHeads).any fun h => w == "un" ++ h || w == "non" ++ h
    let ms := (if k == 1 then complementPatterns else activePatterns).filterMap (matchPattern phrase)
    let nounWords := E.declaredSorts.map (·.name) ++ E.declaredSorts.flatMap fun s => (sortNouns E O s).flatMap splitWs
    let safeAdj := ms.all fun a => match a with
      | some w => !(reserved ++ auxiliaries ++ nounWords).contains w
      | none => true
    let rescue := shaped && codes.all eligibleCodes.contains && !collision && !negated && t.length ≤ 80 &&
      !ms.isEmpty && safeAdj
    let content := contentWords t
    let anchored := content.any (contentWords (name ++ " " ++ d.description)).contains
    let idiomCollision := E.declaredConsts.any (fun c => wordOccurs c.name phrase) ||
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
        let sHeads := (E.declaredPreds.map (·.name)) ++
          E.declaredPreds.filterMap fun d2 => templateHead ((E.declaredWording O d2.name).getD "") d2.arity
        let negHeads := ["un", "non", "un-", "non-"].flatMap fun pre => sHeads.map (pre ++ asciiLower ·)
        let phWords := (runs (fun c => isLower c || isDigit c || c == '_' || c == '-') (pyLower ph)).filterMap
          fun w => let cs := w.toList.dropWhile (fun c => !isLower c)
                   if cs.isEmpty then none else some (String.mk cs)
        !E.declaredConsts.any (fun c => wordOccursI c.name ph) &&
        !E.declaredPreds.any (fun d2 => d2.name != name &&
          ((E.declaredWording O d2.name).map wordingKey) == some (wordingKey t)) &&
        !phWords.any negHeads.contains && !codes.contains "NEGATED_HEAD"
    let accepted2 := accepted1 || suggestedOk
    let accepted3 := accepted2 && (idiom || !(runs isLower t).any extraReserved.contains)
    let accepted4 := accepted3 && !(E.profiles.contains "order@0" &&
      (runs isLower (pyLower t)).any comparisonWords.contains)
    accepted4 && !duplicateWording E O name
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
  let symbols := E.declaredPreds.map (·.name) ++ E.declaredConsts.map (·.name)
  let first := E.declaredSorts.map fun s =>
    let base := (E.declaredNoun O s.name).getD s.name
    let ok := letterWords base && !(splitWs (asciiLower base)).any reserved.contains &&
      !symbols.contains (asciiLower base)
    (s.name, if ok then base else fallbackNoun s.name)
  let deduped := first.map fun (s, n) =>
    if (first.filter fun (_, m) => wordingKey m == wordingKey n).length > 1 then (s, fallbackNoun s) else (s, n)
  let generated := E.generatedSorts.map fun s => (s.name, fallbackNoun s.name)
  (deduped ++ generated).map fun (s, n) => (s, (E.forms.nouns.lookup s).getD n)

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
  let named (c : String) : Bool := (E.declaredSpelling O c).isSome        -- `self.declared_constants`
  let declared := E.declaredConsts.filterMap fun c => (E.declaredSpelling O c.name).map (c.name, ·)
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
    let collided := cur.filter fun (c, v) => named c && v != jsonQuote c &&
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

/-! The overlay check: the producer's three refusals (english.py:373–375, :442–443, :511–517) -/

/-- Whether a wording or the negative of `d`'s main selection has the key of a risk template (english.py:437–441). -/
def riskKeyed (E : Env) (O : Overlay) (d : PredDecl) : Bool :=
  let (w, n) := mainSelection E O d
  ((w :: n.toList).map wordingKey).any (riskTemplates.map wordingKey).contains

/-- Whether a linter issue stays at the path of `d`'s declared negative once `d`'s declared wording is accepted
(printer.py:309–322, english.py:382–389): for one or two arguments when the negative is not selected; for more,
when the linter reports it. -/
def negativeLeft (E : Env) (O : Overlay) (d : PredDecl) : Bool :=
  match E.declaredNegative O d.name, E.declaredWording O d.name with
  | some n, some t =>
    if d.arity ≤ 2 then (mainSelection E O d).2 != some n
    else !(templateCodes E O n).isEmpty || negateVerb t != some n
  | _, _ => false

/-- The producer's first refusal of the overlay `O`, in Python's order: O1, a duplicate wording, in the main loop;
O2, a reused risk wording; O3, the final comparison, sort entries before predicate entries. `E` has `O` merged in
(`Env.decode`). A constant entry is never refused (english.py:471–508). -/
def overlayCheck (E : Env) (O : Overlay) : Option Failure :=
  let named (p : String) : Bool := O.predicates.any (·.1 == p)
  let exempt (p : String) : Bool := E.roles.contains p || p.startsWith "risk__" || altWords.contains p
  let duplicate := E.declaredPreds.find? fun d => named d.name && d.arity ≤ 2 && duplicateWording E O d.name
  let risk := E.declaredPreds.find? fun d => E.risk && named d.name && !exempt d.name && riskKeyed E O d
  let sortEntry := O.sorts.find? fun (s, noun) => (policyNouns E O).lookup s != some noun
  let predEntry := O.predicates.find? fun (p, _, _) => match E.predicate? p with
    | some d => !E.roles.contains p && (!acceptsDeclared E O p || negativeLeft E O d)
    | none => false
  match duplicate, risk, sortEntry, predEntry with
  | some d, _, _, _ => some ("O1", "predicate", d.name)
  | none, some d, _, _ => some ("O2", "predicate", d.name)
  | none, none, some (s, _), _ => some ("O3", "sort", s)
  | none, none, none, some (p, _, _) => some ("O3", "predicate", p)
  | none, none, none, none => none
```

The fixpoint of `policySpellings` runs `#constants + 1` rounds. Each round that changes anything quotes at least one
more constant, so it reaches Python's fixpoint.

`overlayCheck` takes `E` decoded with the overlay (`Env.decode environment overlay`) and `O` decoded from the same
overlay (`Overlay.decode`). Every `E.declaredX O` it calls then reads the same text as `E.declaredX {}`, so it agrees
with V6, which the modes run with `{}`.

### 5.3 Admission, candidates, senses, decoding, classes, texts, advice

```lean
def admitRequest (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : AdmitOutcome :=
  if L.policyOk E O then admit E O L b s else .refused (.invalidGrammar .lexicon)

def checkRequest (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (rs : List (EFormula × Bool))
    (candidates : List String) : Option Nat :=
  if L.policyOk E O then firstChecked E O L b rs candidates else none

/-- The translation guard (2.5). -/
def translateRequest (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String) : TranslateOutcome :=
  if L.policyOk E O then translate E O L cap b s else .invalidGrammar .lexicon

/-- The grammar guard of `english.grammar` and `english.check` (2.5): V6, then `read`'s three checks, in that order. -/
def grammarFault (E : Env) (O : Overlay) (L : Lexicon) : Option GrammarFault :=
  if !L.policyOk E O then some .lexicon
  else if !L.valid E O then some .lexicon
  else if !((grammar E L).wf && terminatorFree (grammar E L)) then some .notWellFormed
  else if !((grammar E L).typed sig (ty E L) (acts E L) && decide (ty E L (grammar E L).start = .sentence)) then
    some .notTyped
  else none

/-- The failure an `invalidGrammar lexicon` response names: the first of V6, else the first of V1 to V5. -/
def lexiconFailure (E : Env) (O : Overlay) (L : Lexicon) : Option Failure :=
  (L.policyFailures E O ++ L.failures E O).head?

/-- The overlay as submitted (2.2), for the overlay check. `display_environment` has validated it in Python. -/
def Overlay.decode (overlay : Json) : Except String Overlay := do
  let sorts ← (← optFields overlay "sorts").mapM fun (s, e) => do
    pure (s, ← VE.Bridge.stringField (← e.getObjVal? "verbalisation") "singular")
  let predicates ← (← optFields overlay "predicates").mapM fun (p, e) => do
    pure (p, ← VE.Bridge.stringField e "verbalisation", optString e "negative_verbalisation")
  let constants ← (← optFields overlay "constants").mapM fun (c, e) => do
    pure (c, ← VE.Bridge.stringField e "verbalisation")
  pure { sorts, predicates, constants }

def overlayText : Failure → String
  | ("O1", _, n) => s!"The vocabulary overlay gives {n} a wording that another symbol already has. No text was read."
  | ("O2", _, n) => s!"The vocabulary overlay gives {n} a wording that risk@0 reserves. No text was read."
  | (_, _, n) => s!"The vocabulary overlay entry for {n} cannot be used as written. No text was read."

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
   ("ConclusionNotDerived", "SyntaxError"), ("IllTyped", "TypeMismatch"), ("NotOneSentence", "SyntaxError"),
   ("InvalidOverlay", "VEError")]

def noPremiseText (i : Nat) : String :=
  s!"Sentence {i + 1} is marked as a conclusion, and no earlier sentence is a premise."
/-- The obligation's `unproved`: the relay puts the entailment operation's status for `{status}`, verbatim. -/
def unprovedText (i : Nat) : String :=
  s!"Sentence {i + 1} is marked as a conclusion, and no checked derivation from the earlier premises was found: " ++
    "{status}"

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

`senses.read` takes no overlay, so it runs no overlay check.

In `Encode.lean`, `Env.decode` changes in three places, and nowhere else (D7 part 4, D18, 2.2):

```lean
/-- The `regulated` entry with a `default` of `unspecified` read as the placeholder `deny`, as
`NormDefaults.Wire.placeholderJson` reads it. Only the modal form is taken from it (D7, part 4). -/
def placeholderEntry (entry : Json) : Json :=
  match entry.getObjVal? "regulated" with
  | .ok r => if r.getObjValD "default" == .str "unspecified" then
      entry.setObjVal! "regulated" (r.setObjVal! "default" (.str "deny")) else entry
  | .error _ => entry

-- in Env.decode, for each predicate entry:
    let modal ← if profiles.contains "norms@0" then
        modalForm name args (if profiles.contains "norm-defaults@0" then placeholderEntry entry else entry)
      else pure none
-- the generated constants read their display form from the overlay, as the declared ones do:
  let gConsts := gConsts.map fun c => { c with display := (VE.Bridge.lookup oConsts c.name).bind (optString · "verbalisation") }
-- the modal forms come first (D18):
         forms := { forms with wordings := modalForms ++ forms.wordings }
```

`blockSymbols` sets `generated := true` on every sort, predicate and constant it returns.

`IllTyped`, `NoDerivation`, `Ambiguous`, `Budget`, `InvalidGrammar`, `InvalidOverlay`, `NotOneSentence` and the two
conclusion codes are status codes, not `Reject` codes. `codeClasses_total` covers the `Reject` codes, and the
response-shape test covers the rest.

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

theorem translateRequest_policy : ∀ (E : Env) (O : Overlay) (L : Lexicon) (cap b : Nat) (s : String),
  L.policyOk E O = false → translateRequest E O L cap b s = .invalidGrammar .lexicon

theorem grammarFault_none : ∀ (E : Env) (O : Overlay) (L : Lexicon),
  grammarFault E O L = none → L.policyOk E O = true ∧ L.valid E O = true

theorem overlayCheck_constants : ∀ (E : Env) (O : Overlay) (cs : List (String × String)),
  overlayCheck E { O with constants := cs } = overlayCheck E O

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

- *Proved in the stub*, on this text verbatim (the new fields replaced by accessors, section 12) and again over the
  stub's carrier: `policy_iff_no_failure`, `admitRequest_ok`, `admitRequest_exact`, `admitRequest_policy`,
  `checkRequest_some`, `codeClasses_total`. Draft 2 adds three, proved on the text verbatim only:
  `translateRequest_policy`, `grammarFault_none` and `overlayCheck_constants`.
- *Proved over a parameterised signature*: `sensesRequest_policy`, with `readWithSenses` and the outcome type as
  parameters, a shape check against `senses.md` 5.2.
- *Proved as `rfl` against a local copy of the mode type*: the three `runMode` equations.
- *Elaborated as definitions of type `Prop`*: `policy_selection` and `decode_encode`. `decode_encode` was also
  checked on four formulas, all true.

### 5.6 By construction, and by test

- **By construction.** `policy_iff_no_failure` is `List.isEmpty_iff`. `policy_selection` unfolds the four
  `filterMap`s of `policyFailures`, with `E.predicate? p` some exactly when `p` is a predicate name. The request
  statements split on `policyOk` and use `admit_ok`, `admit_exact` and `first_checked`. `translateRequest_policy`
  is `simp` on the guard. `grammarFault_none` splits on `policyOk` and `valid`. `overlayCheck_constants` is `rfl`:
  no function the check calls reads `O.constants`. `codeClasses_total` is `cases r <;> rfl`. `decode_encode` is an
  induction on `EFormula`, with a lemma for `ETerm` and for the `mapM` of an `atom`.
- **By test.** The port and the overlay check against Python (pt1 and the two parity harnesses), the boundary
  extension, the cache, the relay, the comparator, the advice table, the texts against `DELTA.md`, and the response
  shapes (`runMode_fits`).

## 6. Files, generated artefacts and gates

| Artefact | Rule |
|---|---|
| `lean/VE/EnglishGrammar/Policy.lean`, `Advice.lean`; the modules of 5.1 | frozen-inventory lines, `Audit.lean` lines for the statements of 5.5, the generated lists regenerated, `LOCK.json` and `actions_version` |
| `lean/VE/EnglishGrammar/E2Examples.lean` | the computed fixtures of section 8 as `#guard` checks, in the default build |
| `ve/backends/english_lean.py`, `ve/english.py`, `ve/natural.py`, `ve/backends/dispatch.py`, `ve/assurance-manifest.json` | E2.3 (2.8) |
| `conformance/english_lean_{g3,reverse,mutate,policy,overlay}.py` | E2.5 (2.10) |
| `docs/spec/english-lean-e2-report.md`; `docs/lean-first/e2/DELTA.md`, `LEDGER.md` | GE2 |

Gates:

- *The bounded round.* Both reviewers check draft 2 before any stage starts: the new definitions (the overlay
  check, `placeholderEntry`, the two guards, `lexiconFailure`), the order of 2.5, and that each new fixture's
  expectation was computed, by Python for selections and raises (py1) and by the stub for Lean. Nothing else
  reopens.
- *Per stage* (the review's gates): E2.0 needs the boundary and modal edits and the guards and responses (items 3
  and 4 of the status note); E2.1 needs the enumeration, the overlay check and `unaryPhrase` (items 1, 2 and 5);
  E2.2 needs the overlay check, the guards and responses, and the claims and texts (items 2, 4 and 6).
- The statement review of this specification (section 10) before any proof of 5.5; the bounded review of the port's
  tables (items 1 to 6, and 14 to 16) before the flip; GE2 as the plan states it.

## 7. What this stage consumes and returns

| From | Delivery | Used in |
|---|---|---|
| S3 build | the reader, `admit`, `obligations`, `firstChecked`, their proofs; `Env.decode`, the boundary, the fixture environments | everywhere |
| S3 report | the measured `safe` finding; G3 open | lx29, E2.5 |
| lexicon report | Python's `lexicon_id` per corpus environment | pt1 |
| senses (`ve-senses-int`) | `senseDecl`, `project`'s call of `Lexicon.failures`; `readWithSenses`' signature | 2.4, lx30, 5.3 |
| LEAN-FIRST | the gate of 5.1; batch 2's handles; batch 12b's environment mode; DRI answers 3 and 5 | GE2, 2.2, 2.7 |
| norm-defaults | `NormDefaults.Wire.decodeSourceU` and the reading of `placeholderJson` | D7 part 1 and part 4 |
| returns | `english.admission` with `authority: lean`; V6 as Lean's port of Python's selection, which a later stage can use to produce the lexicon; the overlay check; the class table; the ledger | the next stage; E3 |

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
row is the S3 report's measured Python finding, reproduced by the port. lx24 fails V2, V5 and V6, and its response
names `("V6", "negative", "hazard")`: `lexiconFailure` takes V6 first (computed).

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

**Draft 2's corrections** (computed; Python's choice run by py1). Each row gives Python's choice, then the choice of
draft 1's port and of draft 2's text. The last column is V6 on the lexicon that selects the declared wording or
noun, by draft 1 and by draft 2; V1 to V5 accept that lexicon in every row. K is the Kelvin sign, U+212A.

| Id | Case | Python's choice | Draft 1 | Draft 2 | V6 of the declared selection: draft 1; draft 2 |
|---|---|---|---|---|---|
| lx32a | `FA` + `preventable` (harm) `{0} is fully avoidable` (a generated name) | declared | fallback | declared | `("V6", "predicate", "preventable")`; none |
| lx32b | `FR` + `slight` (harm) `{0} is fully minor` (a severity class) | declared | fallback | declared | `("V6", "predicate", "slight")`; none |
| lx32c | `FR` with the severity sort named `level`, + sort `grade` with the noun `level` | `level` | `entity of sort "grade"` | `level` | `("V6", "sort", "grade")`; none |
| lx31c | F + `keen` (service), suggested overlay entry `{0} is Keen` with K | declared | fallback | declared | `("V6", "predicate", "keen")`; none |
| lx31d | the same with `{0} IS keen` | declared | declared | declared | none; none |
| lx31e | F + `known` (`{0} is known`) + `obscure`, suggested `{0} is unKnown` with K | fallback (`unknown` is a negated head once lower-cased), then the raise at `:517` | fallback | fallback; O3 | `("V6", "predicate", "obscure")` both |
| lx31f | F + constant `kelp` + `green`, suggested `{0} is Kelp green` with K | fallback (`kelp` occurs under `re.I`), then the raise at `:517` | fallback | fallback; O3 | `("V6", "predicate", "green")` both |

Draft 1's V6 in lx31c follows from its choice, the fallback. lx31e and lx31f pin the two other parts of `re.I` on the
suggested path, `pyLower` and `wordOccursI`: Python refuses both wordings, and draft 2 does too. In lx32c the severity
sort itself gets `severity` in both drafts.

py1 printed Python's outcome for each row. Each lx31 case carries its wording as an overlay entry, so a wording that
the suggested path refuses does not stop at the fallback. The producer's final comparison then raises:
`English vocabulary entry fails the template linter: predicates/obscure`, and `…/green` for lx31f. Draft 2's
overlay check refuses both with `("O3", "predicate", "obscure")` and `("O3", "predicate", "green")` (computed). A
request with either overlay is therefore `InvalidOverlay` before V6 is reached (2.5). The same holds of lx31b in the
first table: Python raises at `:517`, and the check gives `("O3", "predicate", "fast")`. lx31a, lx31c and lx31d are
admitted by both, with the overlay's wording selected. The V6 columns above stay what V6 says of each lexicon.

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
| the 4 rows the S3 boundary refuses (2.2) | 4 of 4 when decoded as E2.0 decodes them, with the identity over the submitted environment (md5) |
| all 22, by draft 2's text of 5.2 verbatim | 22 of 22 |
| the 17 round-trip configurations | not computed (built in Python) |

The overlay check refuses none of the four corpus overlays, which Python's producer admitted (ovc, computed).

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
| ad19 | alternatives; `They allows robot to leave.` | `plural-pronoun`: it wins over `alternatives-person`, whose pattern also occurs |

ad3 is the same kind of case within the table: under `risk`, `could lead to` is a pattern of `risk-degree` and of
`alternatives-degree`, and the earlier row wins.

### 8.7 Admission and the check of candidates (computed)

| Id | Case | Outcome |
|---|---|---|
| cn10 | `admitRequest` under `F`, `LF`: `Legacy is deployed. Therefore legacy is deployed.` | `ok`, the two formulas, obligations `[(1, [0])]` |
| cn11 | `admitRequest` under `FA`, `LA`: `Wait is available to robot.` | `refused (invalidGrammar lexicon)`: V6 (`safe`) |
| cn12 | the same with `laSafe` | `ok`, `available(wait, robot)`, no obligation |
| cn13 | `checkRequest` under `FA`, `LA`, for `available(wait, robot)`, candidate `Wait is available to robot.` | none; the mode answers `invalidGrammar`, not `{}` (ev4d) |
| cn14 | the same with `laSafe` | `some 0` |
| cn15 | the texts of 4.2 for `noPremise 0` and the obligation of sentence index 1 | as 4.2, the second with the slot `{status}` |
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
| ev4d | `english.check` under `FA`, `LA` (cn13's case) | `invalidGrammar`, fault `lexicon`, failure `["V6", "predicate", "safe"]`, not `{}`; the guard computed (gg1), the mode an *obligation* |
| ev14a | the four environments of 2.2 under the S3 build's `Run.environmentId` | computed: refused, with the messages of 2.2 |
| ev14b | *obligation*: the same after E2.0 | admitted; the port's `lexicon_id` equals the report's for each (the decoding and the identity computed, md5) |
| ev15a | `english.read` on the birthright use case with its overlay and Python's lexicon (display identity), S3 build | computed: `InvalidInput: the lexicon names another environment` |
| ev15b | the same lexicon written with the submitted identity, S3 build | computed: status `one` |
| ev15c | *obligation*: ev15a after E2.0 | status `one`, `environment_id` the submitted environment's |
| ev15d | the lexicon of F with the right identity and the format `x` | computed: `InvalidInput: the lexicon format is not ve.english-lexicon@1` |
| ev16 | *obligation*: a source with a non-ASCII character before its second sentence | `spans` in code points, equal to Python's `sentence_spans` mapped through `boundaries` |
| ev17 | *obligation*: an overlay that the overlay check refuses (ov3b), sent with a lexicon that fails V6 | `InvalidOverlay`, class `VEError`: the overlay check comes before V6 |

### 8.9 The relay, the comparator and the ledger (obligations)

| Id | Case | Expected |
|---|---|---|
| rl1 | `parse_english` on cn10's text under `F` | Lean's reading; one entailment call with premises `[0]` |
| rl2 | an obligation whose entailment is not `Found` | `SyntaxError` with the obligation's `unproved` text, the status in its slot verbatim; from `parse_english_argument` too |
| rl3 | each status and code of 4.2 | the class of `codeClasses`, the text verbatim; no Python text on the path (`relay_lint`) |
| rl4 | `render_english` of cn10's document | candidates checked by `english.check`; no call of `_parse_english_document` |
| rl5 | `parse_english_with_metadata` when the rendering does not read back | `english_text` is the source |
| rl6 | a request that fails V6 | `CheckerUnavailable` with `invalidGrammar lexicon: V6 …` |
| rl7 | the natural view of a two-paragraph document | the same paragraph breaks as before the flip |
| rl8 | the producer raises for a suggested overlay entry without `accept_suggested_vocabulary`, or for ov11a's overlay, whose display environment `Environment` refuses | the same `VEError` before any Lean call |
| rl9 | `parse_english` with each overlay of ov1b, ov2b, ov3b, ov4b, ov5b | the producer does not raise; Lean answers `InvalidOverlay`; the relay raises `VEError` with Lean's text |
| rl10 | each other caller of `EnglishVocabulary` with the same overlays | the producer's own `VEError`, as today |
| rl11 | `render_english` when `english.check` answers `invalidGrammar` (a lexicon that fails V6, as in ev4d) | the response's class, `CheckerUnavailable`, with Lean's text; not the rendering `ValueError` |
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
| for a predicate that no profile step selects (not a role, not modal, not one of the four words, not `risk__…`, not reserved by `risk@0`), a declared wording is Python's choice exactly when `acceptsDeclared` holds of it | holds | lx15b to lx22f (the "declared" rows), lx32a, lx32b |
| | does not hold | the "fallback" rows of 8.1 |
| | the premise matters: a profile step selects | lx33a: `available` under `FA`, where `acceptsDeclared` fails and Python's choice is the declared wording, a role's; lx33b: a modal predicate worded `{0} accesses {1}`, where `acceptsDeclared` holds and Python's choice is `{0} may access {1}` (both computed) |
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
| a suggested entry is accepted by the suggested path exactly when it is suggested and passes `unary_phrase` and the three checks | suggested | lx31a, lx31c, lx31d |
| | not suggested; a check fails | lx31b; lx31e, lx31f |
| for an overlay that `display_environment` admits, the overlay check refuses it exactly when Python's producer raises for it, at the same site | refused (O1; O2; O3) | ov1b, ov7, ov8; ov2b, ov10; ov3b, ov4b, ov5b, lx31b, lx31e, lx31f |
| | admitted | ov4c, ov6, ov9, lx31a, lx31c, lx31d, ovc (the corpus overlays) |
| | the premise matters: `display_environment` refuses first | ov11a, ov11b (Python raises before the main loop; the check alone gives O1 and none) |
| a request is answered with the first refusal in the order boundary, overlay check, V6, V1 to V5 | each pair | ev14a and ev15a (boundary); ev17 (overlay before V6); lx24 (V6 before V2 and V5) |
| `admitRequest` is `ok` exactly when V6 passes, `read` is `ok` and every obligation has a premise | all three | cn10, cn12 |
| | V6 fails | cn11 |
| | `read` not `ok`; a mark without a premise | cn18; cn16, cn17 |
| `checkRequest` names an index exactly when V6 passes and some candidate reads back | both | cn14, ev4a, ev4c |
| | V6 fails; no candidate reads back | cn13; ev4b |
| `english.check` answers `{}` exactly when the grammar guard passes and no candidate reads back | both | ev4b |
| | the guard refuses | ev4d (`invalidGrammar`) |
| for an environment the boundary admits and a lexicon of the right format and fields, the lexicon decodes exactly when its `environment_id` is the display environment's identity (the environment's, without an overlay) | display identity, overlay | ev15c (*obligation*) |
| | submitted identity, overlay (S3 build) | ev15a, ev15b |
| | the premises matter: the boundary refuses; the format is wrong | ev14a; ev15d |
| advice of an `alternatives@0` row is given exactly when the profile is named, a pattern occurs, and no earlier check or row wins (the negated existential and the plural pronoun first, then the first position, then table order) | all three | ad8, ad9, ad15, ad16, ad18 |
| | no pattern (`to happen`); no profile | ad17; ad10 |
| | an earlier check or row wins | ad19 (`plural-pronoun`); ad3 (`risk-degree` before `alternatives-degree`) |
| the comparator runs exactly when its switch is set | set | ev7 (*obligation*) |
| | not set | ev6 (*obligation*) |

### 8.11 The overlay check (computed; Python run, py1)

Each `a` row is a declaration, with no overlay: Python's choice by the port, and no refusal. Each `b` row puts the
same wording in an overlay entry, the environment declaring a plain wording for the symbol. The Lean column is
`overlayCheck` on the decoded overlay. The Python column is what `EnglishVocabulary` did when py1 ran it.

| Id | Case | Lean | Python |
|---|---|---|---|
| ov1a | F + `inspected` declared `{0} is reviewed`, the key of `reviewed`'s wording | none; the fallback is selected | no raise; the fallback |
| ov1b | F + `inspected` (`{0} is inspected`), overlay `inspected` → `{0} is reviewed` | `("O1", "predicate", "inspected")` | raises at `:374` |
| ov2a | lx23a: `FR` + `hazard` declared `{0} risks {1}` | none; the fallback | no raise; the fallback |
| ov2b | `FR` + `hazard` (`{0} endangers {1}`), overlay `hazard` → `{0} risks {1}` | `("O2", "predicate", "hazard")` | raises at `:443` |
| ov3a | lx15a: F + `stable` declared `{0} never fails` | none; the fallback | no raise; the fallback |
| ov3b | F + `stable` (`{0} is stable`), overlay `stable` → `{0} never fails` | `("O3", "predicate", "stable")` | raises at `:517` |
| ov4a | F + `checked` declared `{0} is checked` with the negative `{0} is never checked` | none; the wording is selected, without a negative | no raise; the same |
| ov4b | F + `checked`, overlay `checked` → that wording and negative | `("O3", "predicate", "checked")`: the negative is left with an issue | raises at `:517` |
| ov4c | the same overlay with the negative `{0} is not checked` | none | no raise; the negative is selected |
| ov5a | lx27a: F + sort `item` with the noun `every item` | the fallback noun | no raise; the fallback noun |
| ov5b | F + sort `item`, overlay sort entry `item` → `every item` | `("O3", "sort", "item")` | raises at `:517` |
| ov6 | F + constants `api`, `api2`, overlay constant entries `api` → `the api`, `api2` → `api` | none; both spellings quoted | no raise; both quoted (lx28d) |
| ov7 | overlay with ov3b's and ov1b's entries | `("O1", "predicate", "inspected")`: O1 runs first | raises at `:374` |
| ov8 | `FA`, overlay `available` → its fixed wording `{0} is available to {1}`, with the negative `{0} leads to {1}` (a role; the negative has the key of `leads_to`'s wording) | `("O1", "predicate", "available")` | raises at `:374` (existing symbol `leads_to`), before `:399` would restore the role |
| ov9 | `FA`, overlay `available` → its fixed wording `{0} is available to {1}` (a role the linter refuses: `acceptsDeclared` is false) | none; Python's choice `{0} is available to {1}` | no raise; the role's wording is restored, without a negative |
| ov10 | `FR` + sort `item`, overlay `hazard` → `{0} risks {1}` and sort `item` → `every item` | `("O2", "predicate", "hazard")`: O2 before O3 | raises at `:443` |
| ov11a | `FA`, overlay `available` → `{0} leads to {1}` (draft 2's ov8) | `("O1", "predicate", "available")`, not reached | raises in `display_environment`, before the main loop: `AlternativesVerbalisation: available must read "{0} is available to {1}"` (`english_vocabulary.py:131`, `environment.py:243`) |
| ov11b | `FA`, overlay `available` → `{0} can use {1}` (draft 2's ov9) | none, not reached; the port's choice would be `{0} can use {1}` | the same raise |
| ovc | the four corpus overlays (birthright, constitution, news, 14th amendment) | none, each | no raise: their `lexicon_id`s are recorded |

The texts of the three sites, computed for `inspected`, `hazard` and `item`, are 4.2's. Python's messages, as py1
printed them, are `Duplicate English wording '{0} is reviewed' for 'inspected'; existing symbol(s): reviewed` (O1),
`English wording for 'hazard' reuses a risk@0 wording` (O2) and
`English vocabulary entry fails the template linter: predicates/stable` (O3). The texts differ, so they are
`wording` rows of `DELTA.md`.

ov11a and ov11b are refused by `display_environment`'s validation of the display environment. That validation stays
in Python and runs before any Lean call (2.8, 2.9), so the overlay check never sees these overlays on the admission
path. Their Lean column is the check applied on its own (computed). On its own it would admit ov11b (section 9).

### 8.12 E2.0: the boundary's part 4 and the modal forms (computed)

| Id | Case | Expected |
|---|---|---|
| md1a | the S3 build's `Env.decode` on `usecases/agent-policy/environment.unspecified.json` | `InvalidInput: invalid regulated role or default for permitted` |
| md1b | draft 2's `Env.decode` (5.3) on the same | the modal forms `{0} may be performed` (`permitted`) and `{0} must be reported to the user` (`report_required`); Python's (py1: the producer gives these two, with no raise) |
| md1c | part 1, `NormDefaults.Wire.decodeSourceU` with an empty document, on the same | admitted over `blockRouteView`; without it, `UnsupportedProfile: norms route with data flags is not implemented` |
| md2 | the same with the `default` of `permitted` set to `sometimes` | part 1 and `Env.decode` both refuse: `InvalidInput: invalid regulated role or default for permitted`. Python's `Environment` refuses with the same message (py1) |
| md3 | the same without `norm-defaults@0` | part 1 refuses: `UnsupportedProfile: unspecified completion requires norm-defaults@0`. Python's `Environment` refuses with the same message (py1) |
| md4 | `FA` with `available` regulated as a permission, act `{0} choose {1}`, under `Env.decode` directly | the S3 build gives `available` the role wording `{0} is available to {1}`; draft 2 gives the modal form `{0} may choose {1}`, Python's (D18). The boundary refuses the environment: `AlternativesRegulated: available available`, and so does Python's `Environment` (py1). py1 therefore regulated the role on a validated environment object and ran the producer: `{0} may choose {1}`, with no negative |
| md5 | the four rows of ev14a, decoded by draft 2's `Env.decode`, the identity `Standalone.environmentIdOf` over the submitted environment | the port's `lexicon_id` equals Python's recorded one, 4 of 4 |

### 8.13 Guards, codes and texts (computed)

| Id | Case | Expected |
|---|---|---|
| gg1 | `grammarFault FA {} LA` | `some lexicon` (V6 refuses `safe`) |
| gg2 | `grammarFault FA {} laSafe` | `none` |
| tg1 | `translateRequest FA {} LA 2 workBudget "Wait is available to robot."` | `invalidGrammar lexicon` |
| tg2 | the same with `laSafe` | one reading, complete |
| cn19 | translation mode under F, `LF`: `Legacy is deployed. Legacy is reviewed.` | `rejected`, code `NotOneSentence`, S3's text; class `SyntaxError` |
| lx24′ | `lexiconFailure` of lx24 | `("V6", "negative", "hazard")` |
| cl1 | `codeClasses.lookup "InvalidOverlay"` | `VEError` |
| lx33a | `available` under `FA`: `acceptsDeclared`, and Python's choice | `false`; `{0} is available to {1}` (the role's wording) |
| lx33b | `FM`'s `access` worded `{0} accesses {1}` and regulated as a permission, act `{0} access {1}` | `true`; `{0} may access {1}` (the modal form) |
| ad19 | 8.6 | `plural-pronoun` |

## 9. Limits, and what is not claimed

The limits of S2 section 9 and S3 section 9 stand. In addition:

- **The port and the overlay check are trusted and tested, not proved against Python.** pt1 is 22 rows by identity,
  and the overlay check meets four corpus overlays. The two parity harnesses are the gate, and nothing proves that
  `policyPredicate` or `overlayCheck` is Python's on an environment not tested.
- **Python's case and word rules are ported where they decide.** Outside the suggested path, `\w` and `str.lower`
  are ported on ASCII, with the Kelvin sign and `İ` handled for content words. Python's `\w` is wider on non-ASCII
  letters, so on such a phrase the port can find a whole-word collision that Python does not. That decides nothing:
  the rescue accepts only a phrase of `[a-z]+` words, and an idiom is a fixed ASCII text. The suggested path is the
  exception, since `unary_phrase` and its constants test match under `re.I` and can accept a non-ASCII letter (lx31c).
  There the port follows `re.I` (2.3). Draft 1 claimed the ASCII port decided nothing anywhere; that was wrong on
  this path.
- **The order within one overlay site** follows Lean's key order, not the overlay's source order (2.3). When two
  entries fail at one site, the entry named can differ from Python's.
- **py1 ran Python on the new fixtures only.** Draft 1's fixtures meet Python through the port and the 22 recorded
  identities (pt1). The two parity harnesses run Python at scale.
- **The overlay check relies on `display_environment`.** That function stays in Python (2.9) and refuses some
  overlays before any Lean call, among them one whose display environment Python's `Environment` refuses (ov11).
  Lean does not repeat those checks. A request that reached `english.read` without the relay could carry such an
  overlay, and the overlay check would not refuse it (ov11b). On the admission path the relay always runs
  `display_environment` first.
- **V6 does not cover letters**, and `rights@0` wordings are outside the reader.
- **The producer still proposes**, and the next stage removes it.
- **Advice is wider than Python's hints and proves nothing.** Two hints are still lost (S3 4.3).
- **`IllTyped` has one class** (D10).
- **The obligations' proofs are outside the English statements** (claim C4 stays).
- **`EnglishParser` stays for the statement layers.**
- **The latency budgets are unmeasured.**
- **The boundary extension is a link to existing decoders** and is tested, not proved.
- **What the stub could not elaborate as the build will write it:**
  - the new fields, replaced in the verbatim run by accessors that read the environment JSON (section 12);
  - the senses statement, checked over parameters;
  - the service equations, checked against a local mode type (section 12);
  - the modes' order of 2.5 and the `InvalidOverlay` response, stated in prose for `Run.lean` (ev17, rl9).

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

Draft 2 adds the items of the bounded round:

14. The enumeration of 2.3 is Python's: each site of 5.2 that enumerates reads `declaredSorts`, `declaredPreds` or
    `declaredConsts` exactly where Python iterates `env.sorts`, `env.predicates` or `env.constants`, and the
    generated symbols stay where 2.3 keeps them.
15. `overlayCheck` is the producer's three refusals in Python's order: O1 as `:368–375`, O2 as `:432–443`, O3 as
    `:511–517` with the derivation of 2.3; constants are never refused.
16. `unaryPhrase`, `wordOccursI` and the negated-head words follow `re.I` with Python's letters (py1 ran them).
17. `placeholderEntry` and the modal forms first (D7 part 4, D18) change no frozen decoder and no identity.
18. `translateRequest`, `grammarFault` and `lexiconFailure`, with the order of 2.5, give each response of 4.4.
19. Each new fixture's expectation was computed: by Python (py1) for selections and raises, by the stub for Lean.
    py1's four corrections (lx31e and lx31f; ov8 and ov9, with ov11) are right, and the ledger row of
    `display_environment` covers its validation of the display environment.

## 11. Open points

| # | Point | Recommendation |
|---|---|---|
| Q1 | Lean as the producer of the lexicon: the port computes Python's selection | not in E2; the next stage, with the renderers reading Lean's export (plan, question 3) |
| Q2 | letters in V6 | leave to V1 (2.3); the port exists if the review wants them |
| Q3 | the 17 round-trip configurations of the lexicon report | E2.1's parity harness runs them in Python against the port |
| Q4 | `IllTyped`'s class | `TypeMismatch` (D10); the alternative is a Lean classification of the typing failure, which repeats the typed check's logic |
| Q5 | the identity fix on Lean's side (D6) or Python's | Lean's: no identity value changes (plan, question 5) |
| Q6 | the boundary extension against lean-first 12b | call 12b's mode if it lands first (plan, question 6) |
| Q7 | a role predicate that is also modal | resolved in draft 2: E2.0 lists the modal forms first (D18, md4). The boundary refuses such an environment today, so no admitted environment changes |
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

**Draft 2.** The same file, now also importing `VE.NormDefaults.Wire`, was changed in three ways.

- *The text.* The copy in `VE.EnglishGrammar` is now draft 2's text of 5.2, 5.3 and 5.5, verbatim except for the
  accessors of the new fields. Each accessor reads the environment JSON (the display JSON for an overlay), which is
  where the build's decoding will read the field: `declaredSorts`, `declaredPreds` and `declaredConsts` keep the
  symbols named in the `vocabulary`, `generatedSorts` the others; `pluralOf` reads `verbalisation.plural`;
  `suggestedPred` reads a `suggested` flag that a fixture writes into the predicate entry; `roles` reads all five
  role names of the `alternatives` block. The text elaborated, and the nine proofs of 5.5 went through on it, the
  three new ones included.
- *The comparison.* Draft 1's port over `PEnv` was kept as it was, so each correction is computed against the draft-1
  value it replaces (8.3). On the seven cases of draft 1, draft 2's text still equals draft 1's port. On `LA`/`FA`,
  `LR`/`FR` and `LM`/`FM` it gives draft 1's V6 results.
- *The new fixtures.* It computed lx31c to lx31f and lx32 (8.3), ov1 to ov11 and ovc (8.11), md1 to md5 (8.12),
  and gg1 to cl1, lx33 and ad19 (8.13), with draft 2's text, `Overlay.decode` and a copy of the S3 build's
  `Env.decode` carrying draft 2's three changes. It recomputed pt1 with draft 2's text on all 22 rows, from the
  display JSON, with the identity of `Run.environmentId` or, for the four rows the S3 boundary refuses,
  `Standalone.environmentIdOf`: 22 of 22.

All checks passed on 2026-10-06, and the last full elaboration exited cleanly with no error.

**py1.** Python was run with `python3 -I lean/SpecStubs_english-lean-e2.py`. The script is untracked beside the
stub, and it imports `ve` from the S3 build's worktree. That worktree's head has since moved to `18a3e055`, which
merges `ve-integration` into `531f2789`. `git diff 531f2789 18a3e055` is empty for `ve/english.py`, `ve/printer.py`,
`ve/english_vocabulary.py`, `ve/english_phrases.py` and `ve/environment.py`, so Python's outcome is the S3 build's.
The script prints two things:

- for each new fixture, what `EnglishVocabulary` selects or raises, or what `Environment` raises;
- the code points that `re.I` matches for `[A-Za-z]`, `i`, `s`, `a` and `n`.

Every printed value is the one 8.3, 8.11 and 8.12 now state. Four rows of draft 2 differed, and they were corrected
(the header lists them). The run added these cases:

- lx31a and lx31b, whose Python outcome draft 2 had not stated;
- ov8 and ov9 in their new form;
- md4's producer run. `Environment` refuses that declaration, so the script builds `FA`, replaces the declared
  `available` with a copy regulated as a permission, and runs `EnglishVocabulary` on that object.

The stub gained a matching section, which computes `overlayCheck` and the choice for lx31a to lx31f and for the new
ov8 and ov9. It was elaborated once more over the worktree at `18a3e055`. Its other printed values were unchanged,
and it exited with no error. None of the Lean files changed by the merge holds a line this spec cites.

**What the stub does not show:**

- that the build's fields decode as the accessors read them;
- anything about Python beyond the 22 recorded identities, the four corpus overlays' admission, and py1's run of the
  new fixtures;
- the 17 round-trip configurations;
- the boundary extension's parts 1 and 2 (ev14b), except part 1 for `norm-defaults@0` (md1c to md3);
- the modes' order in `Run.lean`, and the relay;
- latency.

## 13. Changes made by the review fix round of the integration (2026-10-07)

The reviews of the integrated build (`manage-agents/english-lean-e2-review-astra.final.md`,
`manage-agents/reviews/english-lean-e2-review-fable.md`) found the gaps below. Each change is listed with the section
it amends; no statement of 5.5 changed, and `decode_encode` is now proved. The fixtures named are in
`lean/VE/EnglishGrammar/E2Examples.lean` and the tests named in `docs/lean-first/e2/LEDGER.md`.

- **5.5, `decode_encode`.** `ETerm.encode` writes an integer with `intText`, the text `toString` writes:
  `toString` of a negative `Int` joins its sign with `String.Internal.append`, a runtime primitive with no definition
  the logic can unfold, so the round trip could not be proved of it. `E2Examples` checks `intText v = toString v` on
  the compiled code; the proof computes `String.toInt?`'s byte-position loops over character lists.
- **4.4, spans.** A lexical rejection with an offset spans that character in code points (`Run.lexicalSpan`);
  `IllTyped` names the first sentence whose formula, with the formulas before it, fails the typed check, and its text
  names that sentence (`illTypedText`); a refusal that names no sentence spans the whole source, never sentence 1.
  `english.read` and `senses.read` add the span and the advice by one function (`refusalExtras`); the senses reader
  names no sentence for its `IllTyped`.
- **4.2 and 4.4, texts.** `InvalidGrammar`'s text names its fault and first failure and says what the mode did not
  do (`english.read` reads no text, `english.grammar` exports no grammar, `english.check` checks no candidate); the
  overlay texts end the same way (`notDone`). `BlockedWording` `risk-every-cannot` gives Python's two rewrites with
  the sentence's own chooser and harm (`riskEveryCannotText`) instead of the identifier.
- **4.3, advice.** Advice is also given for a sentence the reader refused (a `rejected` response that names a
  sentence); the row `alternatives-another` (`another action`, Python's `Another action needs a rule on an action
  as its reference.`) is added.
- **2.6 and 2.7, the code contract.** `english.grammar` also exports `statuses` (`statusCodes`: the codes each
  status may carry; `rejectCodes_total` and `statusCodes_classed` are proved), `unsentenced` (the rejection codes
  that name no sentence) and `policy` (the port's selection, for the parity harness). The relay holds no class or
  code table: it reads `ve/english_grammar/codes.json`, generated from that export by `tools/english_codes.py` and
  checked against the service by the suite, and raises the class Lean names, taken from `ve.errors` by name (so
  `Internal` is `CheckerUnavailable`).
- **D7 and 2.2, the boundary.** The declarations of `speech-acts@0`, `reports@0` and `readings@1`, which the typing
  view drops, are validated as submitted by their routes' environment decoders (`SpeechActs.Wire
  .decodeSpeechEnvironmentFull`, `Reports.Wire.decodeEnvironment`, `Readings.Wire.decodeEnvironment`) in part 1.
- **5.2, the port's cost.** Spec 5.2's functions re-derived, for every symbol, tables that depend only on the
  environment and the overlay, which made V6 cubic (1.5 s at 256 predicates against GE2 item 9's 100 ms).
  `PolicyCtx.of E O` computes them once; each function is 5.2's body reading those tables, with 5.2's signature kept
  as a wrapper, and a word-boundary search of a token of word characters compares it with the phrase's maximal word
  runs. `PolicyReference.lean` holds 5.2's text verbatim; `E2Examples` checks that the two agree on 34 environments.
  V6 at 256 predicates: 61 ms.
- **2.8, the relay.** One validator checks every transport, the test override included; `parse_english_argument`
  takes premises from Lean's obligations only; the nearest-wording help is given over Lean's sentence span; the
  comparator runs in the suite (`tests/conftest.py`), and its records compare Python's public outcome (its source
  limit first, its premise check against `ConclusionWithoutPremise`).
- **S3 2.2 and 2.5, the spacing of the integer marks** (found by the E2.5 reverse corpus, not by the
  reviews). S3's table let `[` and a sign be glued before and `]` glued after to anything, so Lean read
  `costs-5`, `is at least[budget - 24]`, `[budget + 1]and` and `[budget + 1]- 2`, which the hand parser refuses:
  152 texts of the reverse corpus, all in `order`. The class is an integer mark's spacing on the side away from
  its term. The lexer's `gluedFlags` counts `[` and a sign as free before when the character before opens a term
  too (`[`, `-`), and `]` as glued after only to a word character; `order@0` keeps one row per mark (22 rows).
  The rule is the lexer's one table, mirrored in `conformance/english_lean_lexer.py` and the Lark conversion
  (`conformance/english_lean_tokens.py`); `tests/test_english_e2_integer_marks.py` compares both readers on
  every spacing mutant at every mark. `actions_version` 22.
- **2.9, the ledger.** Definition and citation sentences are read by Lean again; the Python statement readers are
  the operation `english.statement` until E3; the producer's overlay refusals stay on in the statement reader and
  the statement-layer renderer, where no Lean overlay check runs; `tools/relay_lint.py` covers the admission path.

## 14. Changes made by the fix round of recheck 1 (2026-10-07)

`manage-agents/english-lean-e2-looprecheck1.final.md` found one A and two B items. Each is fixed as a class, with
the section it amends; no statement of 5.5 changed.

- **2.3, the typed check (A).** `typedCheck` decoded an `nary@0` environment as submitted while every other family
  decoded its typing view, so beside `norms@0`, `data@0` or `definitions@0` every sentence was `IllTyped` in Lean
  and read by Python. The class is two copies of the family typing dispatch: `VE/Route/Typed.lean` holds the one
  dispatch (`check`, `legacy`, `routeVocabulary`, `typingEnvironment`), and both the standalone typing service
  (`Service.Standalone.decodeTyped`, `legacyTyped`) and `typedCheck` call it. `tests/test_english_e2_profile_matrix.py`
  compares the two readers on every predicate of every family and layer subset of the probe matrix that Python
  admits (112 environments). `actions_version` 24.
- **5.2 and S3 D8, subject first (B).** Python's `template_parts` admitted an n-ary wording beginning `the value
  of`, which V3 refuses, so every text of such an environment was `CheckerUnavailable`; an edited test hid it.
  `template_parts` and the port's `templateParts` now refuse text before `{0}`, so the mechanical form is selected
  (DELTA V1). `tests/test_english_e2_selection.py` requires Lean to accept every selection Python makes over
  generated wordings of arity one to four, and the original test wording is restored with its new outcome.
  `actions_version` 25.
- **2.9, the ledger (B).** `render_citation` and `wordings` asked Python's statement-layer reader to check their
  renderings; they now go through `english.check`, which the first item makes pass on the hidden `nary@0` case.
  `tests/test_english_e2_ledger_sites.py` lists every caller of Python's reader from the source (`ast`) and requires
  each to be a row of `LEDGER.md`.
