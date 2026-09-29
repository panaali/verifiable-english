# Rights (`rights@0`): holders, incident lines, limitations and the bar over `soft-norms@0`

> Status: item-1 specification, draft 4 (2026-09-28), written from [rights-PLAN.md](rights-PLAN.md) draft 5, the
> transcription of the converged Astra/Fable design debate (`manage-agents/debates/design-rights/{astra,fable}.md`),
> applying the converged statement review of draft 1 (`manage-agents/debates/rights-spec/{astra,fable}.md`: FIX,
> CONVERGED after round 3), the statement-only verification of draft 2 (`manage-agents/rights-verify-astra.final.md`:
> FAIL, five corrections, no redesign) and the statement-only verification of draft 3
> (`manage-agents/rights-verify1b-astra.final.md`: FAIL, three corrections, no redesign); section 14 maps each finding
> of the three rounds to its change. It is the statement
> under the Astra + Fable item-1 review that gates items 2, 3 and 4 (PLAN-EXPAND2 rule 10) and any implementation:
> draft 4 goes back to statement-only verification, and a new draft alone opens nothing. Sections 4 to 6 and 9 are the statements
> under review; section 13 lists every point where this draft chose between readings of the plan. Theorem
> statements and fixtures are implementation obligations, not claims of completed proofs or tests. Inputs: [norms.md](norms.md) (W1, cited `norms.md n`), [soft-norms.md](soft-norms.md)
> (cited `soft-norms n`; its Lean names are reused), [document.md](document.md) (W2), [VISION.md](../../VISION.md),
> `lean/VE/Norms/*` and [lean/NORMS.md](../../lean/NORMS.md), the pinned Universal Declaration
> (`manage-agents/pilots/udhr/source/udhr.md`, SHA-256 `d6495201…d3a`, cited "Art. n") and its pilot
> `run-20260927T1800Z` (reading-set ids `rs_u…`). Nothing here changes a frozen contract, a `norms@0` or
> `soft-norms@0` hash, a W1 or soft theorem statement or a checker function.

## 0. Scope, one paragraph

A right is **the holder-side view of duties and permissions**; it adds no deontic primitive. A right block names a
holder sort, a holder guard and Hohfeldian *incident lines*, each an ordinary `norms@0` rule or `soft-norms@0`
default rule whose shape the checker types: a claim (a duty on a bearer with the holder in an object slot), a liberty
(a permission with the holder as subject), an immunity (a prohibition on a status-changing act) and a power (a liberty
over a status-changing act plus a claim that bearers recognise its result). A limitation is a named open predicate
per act with declared necessary and sufficient conditions, carved out of every line in scope; the bar of Art. 30 is a
hard rule with precedence over every right-derived liberty on its act. Every rights document elaborates by
`correlate` into a soft document `(E″, T″)` plus the limitation-condition premises `Lim_D`, and the elaboration is
Lean-proved faithful to a direct semantics `ValueRight` on the rights document itself. What that buys, exactly: W1's
and the soft route's definitions and per-structure theorems are reused as lemmas; the soft route's document-wide
theorems are **restated** with one extra base premise, `Lim_D`, and every rights result is conditional on the
coherence premises `Coh_T` and on `Lim_D`. "Who owes what to whom" is a projection of which lines select, attributed
to right and line; the completed outcome is a corollary. Where the source leaves the bearer, the polarity, the
incident or the force open, the unit is a reading set; a document-wide uniform choice is an attributed coupling
narrowing named on every dependent certificate. Legal standards, limitation and condition tables and the deciders'
findings are open and never certified.

In this specification: the rights document (1), the English (2), the wire form (3), the semantics (4), the
limitation premises and the conditional contract (5), readings and couplings (6), the report (7), diagnostics (8),
the Lean definitions and every item-4 theorem as a statement (9), the item-1 acceptance fixtures (10), limits (11),
the review checklist (12), the resolved choices (13) and the statement-review response table (14).

Out of scope, by the plan: the dynamic effect of a power or of a forbidden status change (stage 3); fulfilment and
time (`violation`, `breach` are W3 definitions above the norms); cross-act practical incompatibility between rights
(soft-norms 4.5); adjudication of any open term; the coverage counting protocol (plan section 5, items 5 and 7); the
surface registrations (item 3) and W8 hooks (item 6) beyond the wordings fixed in section 2.

## 1. What a rights document is

A rights document is a soft-norm document `(E, T)` (soft-norms 1: regulated predicates, situation variables `x̄`,
rules with predicate, sign, guard `G_N`, carve-outs `U_N`, precedence `over`, the three soft attributes) whose norm
units are grouped into rights, plus limitation and bar units, plus a `rights` block in the environment. Everything
W1 and soft-norms require of `T` still holds; the rights checks come on top (4.1).

### 1.1 The environment `rights` block (identity-bound like `regulated` and `soft`)

```text
holders     ⊆ sorts(E)          the holder sorts ("person"; "community" only if a right names it)
bearers     ⊆ sorts(E)          the bearer sorts ("state", "person", "group"); a sort may be both
protected   ⊆ base predicates   the Art. 2 list: race, colour, sex, language, religion, opinion, origin, property,
                                birth, status; each a base predicate of E with a holder sort among its arguments
alters      act key ↦ {holder_slot, status, recognition}
                                acts that change a holder's status: holder_slot is the argument index of the act's
                                permission predicate whose sort is the holder sort of the status that changes (0 for
                                marry(person, person), 1 for deprive_of_nationality(state, person)); status is a base
                                predicate with an argument of that holder sort (married, has_nationality);
                                recognition is null or an obligation-role regulated predicate whose subject has a
                                bearer sort and whose act phrase is the recognition act ("{0} recognise the marriage
                                of {1}"), and is required (non-null) for every act some power line uses; the act key
                                is the act's permission predicate
```

### 1.2 Rights and incident lines

```text
right R        := stable name; holder sort h ∈ holders; holder guard H_R, a base formula over context [h] (⊤ when
                  absent); incident lines; `includes` units add lines to a named right; display number = document order
incident line  := source kind ∈ {claim, liberty, immunity, power}; a soft norm unit N (soft-norms 3.2) whose shape
                  matches the kind (below); a power is two units; a line belongs to exactly one right
line instance  := what a line elaborates to and what every projection, audit and theorem ranges over: instance kind
                  ∈ {claim, liberty, immunity, powerLiberty, powerRecognition}; a claim, liberty or immunity line is
                  one instance of its own kind (a fan-out line one per bearer sort); a power is two instances,
                  powerLiberty (its liberty unit) then powerRecognition (its recognition unit); every instance keeps
                  its source kind, which is what a limitation's `kinds` matches (`kinds: [power]` covers both halves)
holder slot    := claim, immunity, powerRecognition: an object slot (index ≥ 1) of sort h, the unique one, or the one
                  the unit names as holder_slot when several exist (HolderSlotAmbiguous otherwise; only reachable
                  with nary@0); liberty, powerLiberty: the subject slot 0, of sort h (IncidentShape otherwise)
fan-out line   := a claim or immunity whose subject is "No one" / "Everyone": one instance per declared bearer sort b,
                  named rights-fan-<k> (1.6), on the regulated predicate the unit maps b to (same act phrase, same
                  sorts except slot 0 = b); a bearer sort with no mapped predicate is FanOutUndeclared
```

Shapes (`IncidentShape` on a mismatch):

| Kind | Subject sort | Holder slot | Predicate role and sign | Source examples |
|---|---|---|---|---|
| claim | a bearer sort | object | obligation `+` (`must`, `should`) or permission `−` (`must not`, `should not`) | Art. 3, 5, 9, 22, 25 |
| liberty | the holder sort | subject | permission `+` (`may`, `generally may`) | Art. 13, 18, 19, 20(1) |
| immunity | a bearer sort | object, equal to the act's declared `holder_slot` | permission `−` on the permission predicate of an `alters` act | Art. 15(2), 17(2) |
| power | holder (powerLiberty), bearer (powerRecognition) | subject, equal to the act's declared `holder_slot` (so 0); object | permission `+` on an `alters` act's permission predicate, plus obligation `+` on that act's declared `recognition` predicate (non-null for the act) | Art. 15(1), 16(1), 23(4) |

Labels carry no semantics beyond the rules they type: a claim is exactly its rule, read from the holder's end. A
liberty of `−` sign, a claim whose subject is not a bearer, an immunity on a non-`alters` act, an immunity or power
whose holder slot is not the act's declared `holder_slot`, a power on an act with no `recognition` declaration, a
power whose recognition claim is on any other predicate, and a release (`need not`, `generally need not`: obligation
`−`) in any position are rejected, never reinterpreted.

### 1.3 Limitations and conditions

```text
limitation L   := stable name; scope ⊆ rights or `all`; kinds ⊆ {claim, liberty, immunity, power} or `all`;
                  decider (a string or `unstated`); conditions; factors (strings, no premise); an English
                  verbalisation template (generated, 2.1)
condition c    := name; role ∈ {necessary, sufficient}; decider (or inherited from L); verbalisation
per act a in scope (the act of some line N of a right R with R ∈ scope(L) and kind(N) ∈ kinds(L), 4.2):
  lim_{L,a}     a fresh open base predicate with a's argument sorts,   name rights__lim__<k>    (k by 1.6)
  cond_{L,c,a}  a fresh open base predicate with a's argument sorts,   name rights__cond__<k>   (k by 1.6)
premises Lim_D  necessary c:  ∀x̄. lim_{L,a}(x̄) → cond_{L,c,a}(x̄)      label rights:limitation:<L>:<act key>:necessary:<c>
                sufficient c: ∀x̄. cond_{L,c,a}(x̄) → lim_{L,a}(x̄)      label rights:limitation:<L>:<act key>:sufficient:<c>
```

The act key is the act's permission predicate when declared, else its only regulated predicate (soft-norms 1.3).
Conditions are named open predicates instantiated per act, not formulas (13.1): Art. 29(2)'s "determined by law" and
"solely for a permitted purpose" are judgements about the limitation of a given act at a given situation, so each
gets a predicate with the act's sorts and a decider. Every generated name is fixed by 1.6: an identifier of the
existing grammar, bounded in length, injective and regenerable without a table; every report renders the source keys
(limitation, act, condition) beside each generated name, and the subscript notation of this specification is that
rendering. Author formulas (guards, carve-outs, exception conditions, document premises) may mention `lim_{L,a}` and
`cond_{L,c,a}` under their generated English (2.1): that is how an adopter writes a licensed narrowing (4.5). The `lim` and `cond` predicates carry the W2 open-term schema (`decided_by`,
`necessary`, `sufficient`, `factors`) and enter the residual as open terms.

### 1.4 The bar (Art. 30)

```text
bar            := at most one unit; reading ∈ {rule, query}; decider (or `unstated`)
per right-derived permission predicate m (the predicate of some liberty or powerLiberty instance):
  aimed_m       a fresh open base predicate with m's sorts,   name rights__bar__<k>   (k by 1.6)
  bar_m         (rule reading only) a strict node: ¬m(x̄) if aimed_m(x̄); no carve-out; alterable = ∅; hard = true;
                over := every right-derived positive node on m; rule name rights-bar-<k> (the rule prefix rights- is
                reserved, 1.6, so no author `over` can cite it and no author rule can bear the name)
```

Under the query reading no node is added; the report asks, per `m`, whether `∀x̄. aimed_m(x̄) → ¬m(x̄)` is entailed
(7.1). `aimed_m` exists under both readings so that the query is statable and the two readings share vocabulary.

### 1.5 The extended vocabularies `E″` and `E″′`

`E″ = E + {lim_{L,a}} + {cond_{L,c,a}} + {aimed_m}` is the soft input vocabulary of `T″`: the author's `E` plus the
rights-generated predicates and nothing else (`envR`, 9.1; `(correlate D).E = E″`). The soft decision predicates
(`excepted`, `off`, `outweighs` for the lines' and the outside rules' soft attributes, soft-norms 1.3) are added
once, by `soften`: `E″′ = envPrime(correlate D) = E″ + decisions(T″)` is the W1 vocabulary of `T″′ = soften(T″)`,
the one every structure, outcome substitution (`E″′_base`) and certificate ranges over. Both are regenerated at every
site from `E`, the rights block and the decoded units, never taken from the wire. Every generated predicate is open:
it has a decider and no table the checker computes. With no limitation and no bar, `E″ = E`; with every `H_R` top as
well, `E″′` is the `E′` of the soft document that lists the lines before the outside rules (`correlate_identity_top`,
9.2).

### 1.6 Generated names

Generated rule names use the reserved rule prefix `rights-`; generated predicate names use the reserved predicate
prefix `rights__`. Each carries a 1-based index `k` into a canonical order of the regenerated document, so every
name is an identifier of the existing grammar (rule names `[a-z][a-z0-9-]*`, predicates `[a-z][a-z0-9_]*`), at most
19 bytes long, injective over its namespace and regenerable without a table:

```text
instance order    line instances in document order: rights in document order, an `includes` unit appending to its
                  right at the unit's own position; a fan-out line one instance per declared bearer sort, by sort
                  name; a power its powerLiberty then its powerRecognition instance
rights-fan-<k>    the k-th fan-out instance in instance order (its source line and bearer sort rendered beside it)
rights-bar-<k>    the bar node on the k-th right-derived permission predicate m, by predicate name
rights__bar__<k>  aimed_m, the same k
rights__lim__<k>  lim_{L,a}: the k-th pair (L, a) over the limitations and the act keys in their scope, sorted by
                  (limitation name, act key)
rights__cond__<k> cond_{L,c,a}: the k-th triple (L, a, c), sorted by (limitation name, act key, condition name)
```

A source line that is not a fan-out keeps its author name; a power's two units keep theirs. Under `rights@0` an
author rule, right, limitation or bar name beginning with `rights-` and an author predicate beginning with
`rights__` are rejected (`InvalidInput: name <n> begins with rights-` / `author predicate <p> begins with
rights__`), so generated and author names never collide and no author `over`, `cites` or formula can name a
generated node. Soft's names derived from a generated rule name are formed as soft-norms 1.3 forms them from a
14-byte author rule name (`-` becomes `_`): `soft__excepted__rights_fan_<k>` is at most 30 bytes; a bar node is hard
and unswitchable and derives no name; a switch name `soft__off__rights_fan_<k>__<party>` is 24 + digits(k) + |party|
bytes and, since a party identifier may itself be 64 bytes, can exceed the 64-byte identifier limit (89 bytes for
`rights_fan_1` and a 64-byte party). Such a name is rejected when `E″′` is formed (`ResourceLimit: identifier <n>
exceeds 64 bytes`, the identifier validator every environment passes; 4.1 step 5, fixture υ), never truncated,
renamed or admitted. The bound this section guarantees is on the generated names themselves and on the party-free
derived names, not on a derived name that embeds an author party. Indices are positions in the regenerated
document, so adding a limitation, a condition, a bearer sort
or a line may renumber; every certificate is already invalidated by such a change (3.5), and author formulas that
mention a generated predicate (1.3) do so under its English, which the surface prints and parses by source key
(limitation number, act phrase, condition phrase), so the English is stable and the wire is canonical. Every report
and residual line renders the source keys beside each generated name (`rights__lim__3` as `limitation 29,
arrest_permitted`); `lim_{L,a}`, `cond_{L,c,a}`, `aimed_m`, `bar_m` and `<line>/<sort>` in this specification are
that rendering.

## 2. The English (one reading each; rejected as today when `rights@0` is off)

### 2.1 Wordings

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `Right n. Every <holder>[ that C] has the right to <phrase>.` | Names the holder and the right; requires or permits nothing by itself: the right means exactly its lines. Every line of this right applies only to holders that C. | right `R`, holder sort, `H_R := C`; `RightWithoutIncident` if no line follows |
| `Claim of right n. Every <bearer> must <act> each <holder> …[, if C][, unless U].` | In every situation of the kind, the bearer owes the act to the holder. | claim, obligation `+`, `H_R` at the holder slot |
| `Claim of right n. Every <bearer> must not <act> each <holder> …` | … the bearer must not do this to the holder. | claim, permission `−` |
| `Claim of right n. Every <bearer> should <act> each <holder> …` / `should not …` | … unless this line's exception applies there; <decider> decides whether it applies (soft-norms 2.1). | claim, default |
| `Claim of right n. No one may <act> each <holder> …` / `Everyone must <act> each <holder> …` | Every bearer of every declared bearer sort must not / must do this to the holder; one rule per bearer sort. | fan-out |
| `Liberty of right n. Every <holder> may <act> …` / `generally may …` | The holder is permitted; no duty on anyone follows from this line. | liberty, permission `+`, `H_R` at the subject |
| `Immunity of right n. Every <bearer> must not <alter-act> each <holder> …` | The bearer must not change the holder's status this way; whether an attempted change has effect is not modelled. | immunity, permission `−` on an `alters` act |
| `Power of right n. Every <holder> may <alter-act> …  Every <bearer> must <recognise-act> each <holder> …` | The holder may perform the act and every bearer must recognise its result; what follows from the result is not modelled. | two rules |
| `Right n includes:` followed by lines | Adds lines to the named right. | `includes` |
| `Limitation m (on every right \| on rights a and b \| on the liberties of every right). A right in this document is limited in a situation only where limitation m holds.` | Every line in scope gives way where the limitation holds, and the other rules and the default then decide; no other mechanism narrows a right in scope unless written here or in another limitation covering the line, cited, certified to entail some limitation covering the line, or structural (another right's line collides, a strict rule of the same effect decides, or the bar applies); <decider> decides whether it holds. | `L`, `lim_{L,a}`; the audit `limitationScope` (4.5) |
| `Limitation m holds only where <condition phrase>.` | The condition is necessary: where it fails the limitation does not hold; the checker enforces this and decides neither side. | `cond_{L,c,a}`, necessary premise |
| `Limitation m holds where <condition phrase>.` | The condition is sufficient. | sufficient premise |
| `Limitation m takes account of <consideration>[, <consideration>]*.` | These considerations bear on whether the limitation holds; none is by itself decisive. | `factors`, no premise |
| `The limitation of <act phrase instance> is decided by <decider>.` / `Limitations in this document are decided by <decider>.` | Names who decides `lim` for that act / for every act. | `decided_by` |
| `limitation m holds where <act phrase instance>` (guard atom) | The limitation of this act holds here. | atom `lim_{L,a}(x̄)` |
| `<condition phrase> where <act phrase instance>` (guard atom) | The condition holds for this act here. | atom `cond_{L,c,a}(x̄)` |
| `Nothing in this document gives any bearer a right to <act phrase> aimed at the destruction of a right.` | No liberty in this document permits such an act; whether an act is so aimed is decided by <decider>. A default permission or prohibition of the act, and a default duty to do it, give way to the bar there (blocked, 4.3). A strict duty to do the act, or a strict permission for it written outside any right, that applies where the bar applies is reported as a conflict with its situation, not overridden. | bar, rule reading |
| `Whether any right in this document permits an act aimed at the destruction of a right is checked, not ruled.` | The checker reports, per act, whether such a permission is derivable. | bar, query reading |
| `Reading every right in this document with the same <bearer \| polarity \| incident \| force>, because <unit>[, <unit>]*.` | A coupling: the named axis is chosen once for every listed right; every result under it says so. | `coupling:<id>` (6) |
| `No <holder> shall be <passive act>.` (input only) | Not a line: the bearer is missing. | rewrite to a `Claim of right n` per bearer sort or the `No one may` fan-out |

The line's mode is fixed by its deontic verb exactly as in soft-norms 2.1; `must`, `must not`, `may` are strict,
`should`, `should not`, `generally may` are default. `need not` and `generally need not` (a release, obligation `−`)
fit no shape of 1.2 and are rejected in a line with `IncidentShape`; a release is written from the bearer's end as a
rule outside rights. A line may carry the W1 and soft
header options (`(exception to claim 3 of right 12)`, `(users may turn off)`), the rank sentence and the exception
sentences of soft-norms 2.1, each of which is a narrowing mechanism audited in 4.5.

Generated English for the open predicates (W7 registers the productions from the act phrase): `lim_{L,a}` renders as
`limitation <m> holds where {0} <act> {1}`; `cond_{L,c,a}` as `<condition phrase> where {0} <act> {1}`, the phrase
being the condition's declared verbalisation ("the limitation is determined by law", "the limitation is solely for a
permitted purpose"); `aimed_m` as `{0} <act> {1} aimed at the destruction of a right`. Every generated predicate has
exactly one wording, so an adopter can write `Rule 7 (exception to claim 1 of right 9). Every state may arrest each
person, if that person is a journalist and limitation 29 holds where that state arrests that person.`

### 2.2 Synonyms and non-synonyms

Input synonyms rendered canonically: `is entitled to` → `has the right to`; W1's and soft-norms' synonyms inside
lines. Nothing else. `freedom of <noun>` is not a wording: a liberty needs a declared act phrase (`freedom of
movement` becomes `may move within the borders of each state` only through the environment). `shall` is not a norm
word: in translation a "shall" unit is a READINGS set on force, {strict, default} (soft-norms 2.2); in authoring the
IDE shows both paraphrases with a situation and the author picks. `Everyone has the right to` in a header is rejected
with a rewrite naming the declared holder sorts; the holder sort is the translator's declaration, recorded. `cannot`
is not a wording: an immunity says `must not` (2.1), never that a change is void.

### 2.3 The reader's checklist (norms.md 2.5 and soft-norms 2.3, extended)

For every right the IDE shows, in English only: the holder sort and guard; each line's deterministic paraphrase;
for the example situation, who owes what to whom ("Texas owes Ann: not to deprive her of life; nobody owes Ann
protection under this reading") computed from `rightsOf`/`dutiesOf` (4.4); each applicable limitation with its
conditions and their deciders; every narrowing mechanism of each line and whether it is the limitation, cited,
certified, a collision, delivered by a strict rule of the same effect, the bar, or a finding ("this line gives way
where limitation 29 holds; it is also switched off by the user under rule 7, which cites nothing: unlicensed"; "Ann
is permitted here by rule 4, not by right 19"); for a power or immunity the sentence "recognition required; later effects not modelled"
or "prohibition on the act; its effect on status not modelled"; for a reading set, the separating situation; for a
coupling, "reading every article with the same <axis>". Every carve-out paraphrase names the environment default, as
W1 requires: "where limitation 29 holds this line is silent; other rules may decide; if none does, arrest is
permitted by default".

### 2.4 Examples from the source

Act phrases declared as in norms.md 2.4; holder sort `person`; bearer sorts `state`, `person`; every translator's
choice is an attributed interpretation, never the source's content (VISION.md 3).

```text
Art. 3   Right 3. Every person has the right to life.
         Claim of right 3. Every state must not deprive each person of life.
           (rs_u022, labels bearer: state, polarity: negative, force: strict; the coupled Preamble readings cite
           "Member States have pledged" for the bearer and "a common standard of achievement" for the force)
         Claim of right 3. Every state must protect each person within its jurisdiction against deprivation of life.
           (the polarity: positive candidate; "within its jurisdiction" open; separating situation: a state that
           fails to protect but does not deprive)
Art. 5   Claim of right 5. No one may subject each person to treatment that is torture or is cruel, inhuman or
         degrading.   (fan-out to state and person; `torture`, `cruel`, `inhuman`, `degrading` open, decider unstated;
                       "No one shall be subjected to" narrows the polarity to negative by citation)
Art. 9   Right 9. Every person has the right to liberty of person.
         Claim of right 9. Every state must not arrest each person, if that arrest is arbitrary.
           (`arbitrary` open; the packed carve-out `limitation 29 holds where that state arrests that person` is
           generated, not written)
Art. 11  Right 11. Every person that is charged with a penal offence has the right to be presumed innocent.
           (H_R = charged_with_penal_offence(h); every line of right 11 carries it)
Art. 15  Power of right 15. Every person may change the nationality of that person.  Every state must recognise
         the nationality change of each person.   (static; residual: "later effects not modelled")
         Immunity of right 15. Every state must not deprive each person of nationality, if that deprivation is
         arbitrary.   (`must not`, never "cannot")
Art. 16  Right 16. Every person that is of full age has the right to marry.
         Power of right 16. Every person may marry each person.  Every state must recognise the marriage of each
         person.   ("Men and women of full age": H_R cites Art. 16(1); the line mentions no protected predicate,
                     `sex` being absent from the guard; if a translation reads "men and women" as sex(h, ·), the
                     line is listed in E with the citation, 4.6)
Art. 22  Claim of right 22. Every state should secure for each person social security.
         Claim of right 22 is excepted only when securing social security exceeds the organisation and resources of
         that state.   (force narrowed to default by narrowing n22 citing "in accordance with the organization and
                        resources of each State"; the necessary condition is open; the exception is a licensed
                        narrowing because n22 cites u082)
Art. 25  Claim of right 25. Every state must secure for each person a standard of living that is adequate for the
         health and well-being of that person.   (rs_u091, force {strict, default}; no source clause narrows it;
         the default candidate's exception is uncited and reported as UnlicensedLimitation under that choice;
         `adequate` open under both)
Art. 29  Limitation 29 (on every right). A right in this document is limited in a situation only where limitation
         29 holds.  Limitation 29 holds only where the limitation is determined by law.  Limitation 29 holds only
         where the limitation is solely for a permitted purpose.  Limitation 29 takes account of the rights and
         freedoms of others, the just requirements of morality, public order and the general welfare in a
         democratic society.  Limitations in this document are decided by unstated.
           (`solely_for_permitted_purpose` verbalises the permitted purposes in its schema; `just`, `democratic
           society` open; decider unstated, a narrowing may cite Art. 8's tribunals)
         Art. 29(1) "Everyone has duties to the community …" names no act: UNFORMALISED, reason norms.
         Art. 29(3): Limitation 29b (on the liberties of every right). … only where limitation 29b holds.
         Limitation 29b holds where the exercise is contrary to the purposes and principles of the United Nations.
           (rs_u112: {liberties, every line}; the sufficient condition is open)
Art. 30  rs_u114: {rule reading: Nothing in this document gives any bearer a right to perform any act aimed at the
         destruction of a right.; query reading: Whether any right in this document permits an act aimed at the
         destruction of a right is checked, not ruled.}
```

## 3. Declarations, wire form, strict form and identity

### 3.1 The environment `rights` block

```json
"rights": {"holders": ["person"], "bearers": ["state", "person"],
           "protected": ["race", "colour", "sex", "language", "religion", "opinion"],
           "alters": {"marry_permitted": {"holder_slot": 0, "status": "married",
                                          "recognition": "recognise_marriage_required"},
                      "deprive_of_nationality_permitted": {"holder_slot": 1, "status": "has_nationality",
                                                           "recognition": null}}}
```

`holders` and `bearers` are non-empty lists of distinct declared sorts (`UnknownSymbol: sort <s>`,
`DuplicateDeclaration: holder <s>`); `protected` names base predicates with at least one holder-sort argument
(`InvalidInput: protected <q>` on a regulated, defined or decision predicate, or one without a holder-sort argument);
each `alters` key is a permission-role regulated predicate; its `holder_slot` is an argument index of that predicate
whose sort is a holder sort (the affected holder), `status` a base predicate with an argument of that sort,
`recognition` null or an obligation-role regulated predicate whose subject has a bearer sort and whose arguments
include that holder sort (`InvalidInput: alters <act>` otherwise); a power line on the act additionally requires
`holder_slot` 0 and a non-null `recognition`, and an immunity line on it a holder slot equal to `holder_slot`
(`IncidentShape` otherwise, 4.1). The block is part of the canonical
environment bytes, so `environment_id` changes when any of it changes and is unchanged for every existing
environment (none has the block). `rights@0` requires `soft-norms@0` and `norms@0` (`UnsupportedProfile: rights@0
requires soft-norms@0`); the block, the unit kinds of 3.2, candidate `labels` and `couplings` (3.3) are rejected
when the profile is off.

### 3.2 Unit contents (W2 units of kinds `right`, `right_lines`, `limitation`, `bar`)

```json
{"right": {"name": "r9", "holder": "person", "guard": ["top"],
           "lines": [{"kind": "claim", "holder_slot": null,
                      "norm": {"name": "no-arbitrary-arrest", "predicate": "arrest_permitted", "sign": false,
                               "guard": ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]],
                               "unless": [], "over": []},
                      "cites": {}}]}}

{"right_lines": {"right": "r18", "lines": [ ... ]}}

{"right": {"name": "r5", "holder": "person", "guard": ["top"],
           "lines": [{"kind": "claim", "fan_out": {"state": "torture_permitted_state", "person": "torture_permitted_person"},
                      "norm": {"name": "no-torture", "predicate": null, "sign": false, "guard": ["top"], "unless": [], "over": []},
                      "cites": {}}]}}

{"right": {"name": "r16", "holder": "person", "guard": ["unary", "of_full_age", ["var", 0]],
           "lines": [{"kind": "power",
                      "liberty":     {"name": "may-marry", "predicate": "marry_permitted", "sign": true, "guard": ["top"], "unless": [], "over": []},
                      "recognition": {"name": "recognise-marriage", "predicate": "recognise_marriage_required", "sign": true, "guard": ["top"], "unless": [], "over": []},
                      "cites": {"guard": ["u057"]}}]}}

{"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated",
                "conditions": [{"name": "determined_by_law", "role": "necessary",
                                "verbalisation": "the limitation is determined by law", "decided_by": null},
                               {"name": "solely_for_permitted_purpose", "role": "necessary",
                                "verbalisation": "the limitation is solely for a permitted purpose", "decided_by": null,
                                "purposes": ["securing due recognition and respect for the rights and freedoms of others",
                                             "meeting the just requirements of morality, public order and the general welfare in a democratic society"]}],
                "factors": ["the rights and freedoms of others", "the just requirements of morality", "public order",
                            "the general welfare in a democratic society"]}}

{"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated"}}
```

Rules: `name` tokens as W1 (`[a-z][a-z0-9-]*`, at most 64 bytes, not beginning with the reserved `rights-` (1.6,
`InvalidInput`), unique among rights, limitations, bars and rules; `DuplicateDeclaration`); `holder` a declared
holder sort; `guard` a base formula over context `[holder]`; each line's
`norm` is a soft norm object (soft-norms 3.2, every soft field allowed) with `predicate` null exactly when `fan_out`
is present; `fan_out` maps every declared bearer sort to a regulated predicate (`FanOutUndeclared: <line>, <sort>`
when one is missing) sharing the line's act phrase, role and sorts except slot 0; `holder_slot` an argument index or
null (4.1); a `power` line has `liberty` and `recognition` norm objects and no `norm`; `cites` maps a narrowing
mechanism key to a non-empty list of source unit ids (validated as W2 `reason_spans`): keys `guard` (a distinction in
the guard, 4.6), `unless:<i>`, `exception`, `alterable:<party>`, `rank`, `over:<rule>`; a norm unit outside any
right may carry `cites` with key `narrows:<line name>` to license its own effect on a right line (4.5). `scope` is
`all` or a non-empty list of right names (`UnknownRight: <r>`); `kinds` is `all` or a non-empty list of source kinds;
a condition's `name` is an identifier (`[a-z][a-z0-9_]*`, unique within its limitation; it never enters a generated
name, 1.6), its `role` is `necessary` or `sufficient`, `decided_by` a string, `unstated` or null (inherit the
limitation's), `purposes` an optional list of strings rendered in the open term's schema; at most one `bar`
(`DuplicateDeclaration: bar`), `reading` mandatory. A `right` or `right_lines` unit is a norm-bearing unit for W2:
its lines contribute active layers exactly as norm units do (document.md), under the same quoted/hedged/reading
provenance rules.

### 3.3 W2 additions under `rights@0`: candidate labels and couplings

A candidate reading of a reading set may carry `labels`, an object from axis names (`bearer`, `polarity`,
`incident`, `force`; other tokens allowed) to tokens; the key is optional and absent from canonical bytes when
absent, so existing reading sets and identities are unchanged. A `couplings` list sits beside `narrowings`:

```json
"couplings": [{"id": "c-force", "axis": "force",
               "sets": [{"set": "rs_u022", "version": 1}, {"set": "rs_u027", "version": 1}],
               "by": "translator", "reason_spans": ["u013a"]}]
```

Each coupling names an axis, at least two active reading-set versions every one of whose candidates carries a label
on that axis (`CouplingLabelMissing: <id>, <set>`), an author and cited source units. Its meaning is in 6: the
coupled sets take the same label; couplings on one axis whose set lists overlap act as one (a component, 6.2), and
a family of couplings that admits no complete choice is `CouplingUnsatisfiable: <ids>`. Couplings never modify a set; they are attributed, removable and listed on every
dependent certificate as `coupling:<id>`. The existing `narrowings` validator and the P0 identities are untouched;
`couplings` under a document whose environment does not enable `rights@0` is `UnsupportedProfile`.

### 3.4 Strict text (the fallback of P0 3.2)

```ebnf
right       = "right ", name, " holder ", sort, [ " guard (", formula, ")" ], ":" ;
line        = kind, " ", rule ;                                (* rule: the soft-norms strict rule, 3.3 *)
kind        = "claim" | "liberty" | "immunity" | "power" ;
power       = "power ", rule, " ; ", rule ;
limitation  = "limitation ", name, " on ", ( "all" | name, { ", ", name } ), [ " kinds ", kind, { ", ", kind } ],
              [ " decided by ", decider ], { " necessary ", identifier, " \"", text, "\"" },
              { " sufficient ", identifier, " \"", text, "\"" }, { " factor \"", text, "\"" }, "." ;
bar         = "bar ", name, " ", ( "rule" | "query" ), [ " decided by ", decider ], "." ;
```

`name` is W1's rule-name token (`[a-z][a-z0-9-]*`, 3.2), used for rights, limitations, bars and rules; `identifier`
is the predicate identifier grammar (`[a-z][a-z0-9_]*`, at most 64 bytes), used for condition names exactly as 3.2
declares them, so `necessary determined_by_law "…"` prints and parses and a hyphenated condition name is a parse
error. Fan-out, `holder_slot`, `cites`, labels and couplings are JSON metadata as W1's names are; strict text
carries the per-bearer predicate names by writing one rule per bearer sort. `print(parse(s)) = s` on canonical text;
English and strict forms round-trip through the same AST with W1's preserved name metadata (norms.md 10.6, 11.2).

### 3.5 Identity

`environment_id` binds the `rights` block beside `regulated` and `soft`. A right unit's `meaning_id` is W1's digest
over `{"environment_id", "ast"}` with `ast` the right object of 3.2 (lines included, every soft field at its default
omitted as soft-norms 3.4 does); `right_lines`, `limitation` and `bar` units likewise. The rights document hash is
the canonical array of right, right_lines, limitation and bar objects in document order under `environment_id`,
together with the active norm units outside rights; `E″`, `T″`, `Lim_D`, `Exc_T`, `Coh_T` and every conflict and
audit target are regenerated from it at every site. A conflict, audit or classification package has an outer
binding `(environment_id, rights_document_hash, reading choice and couplings, target)` and an inner certificate bound
to the regenerated `E″′_base` and `Background_base″` (norms.md 11.4 step 4); an entailment certificate binds the full
regenerated `E″′` and `background″ ++ layer premises ++ Γ`. Changing a line, a holder guard, a scope, a condition, a
decider, the protected list, an `alters` entry, a bar reading, a reading choice or a coupling invalidates every
certificate of the document.

## 4. Semantics

### 4.1 Well-formedness (`WellFormedRights`)

A rights document `D` is well-formed when, in this order:

1. `E` enables `rights@0`, `soft-norms@0` and `norms@0`; the `rights` block and the unit contents decode (3.1, 3.2).
2. Every line's predicate is regulated; the shape table of 1.2 holds for every line instance (`IncidentShape: <line>
   on right <R>`); the holder slot is determined (`HolderSlotAmbiguous: <line>` when two object slots have the holder
   sort and none is named; `IncidentShape` when none has it); a fan-out map covers every bearer sort; an immunity's
   holder slot is its `alters` act's declared `holder_slot`; a power's two predicates are an `alters` act with
   `holder_slot` 0 and a non-null `recognition`, and that recognition predicate.
3. Every right has at least one line (`RightWithoutIncident: <R>`); `right_lines`, scopes and `cites` name declared
   rights and units (`UnknownRight`, `UnknownSymbol`); at most one bar.
4. Conditions and factors decode; every limitation and condition has a decider by inheritance or its own
   (`MissingExceptionDecider: limitation <L>`); no author predicate begins with `rights__` and no author name with
   `rights-` (1.6).
5. The elaborated `(E″, T″)` (4.2) is `WellFormedSoft` (soft-norms 4.1), including `SoftOverHard`, the unfolded size
   and both DAGs on `T″′ = soften(T″)`; a right-derived line has at most six author carve-outs
   (`ResourceLimit: carve-outs of rule <n>`; the seventh is the packed limitation, the eighth the soft derived one);
   every name of `E″′`, the soft decision predicates derived from generated rule names included, is within the
   64-byte identifier limit (`ResourceLimit: identifier <n> exceeds 64 bytes`, 1.6).

Findings (reported, never rejecting): `UnlicensedLimitation` (4.5), `ProtectedInCone` (4.6), soft-norms' warnings on
`T″`.

### 4.2 Elaboration `correlate(D) = (E″, T″)` and `Lim_D`

`T″` is a soft tree over `E″` whose nodes are, in this order (`correlate_shape`, 9.2):

```text
for every line instance N of right R in instance order (1.6; a fan-out line one node per bearer sort, named
rights-fan-<k>; a power its powerLiberty node then its powerRecognition node):
  guard      := G_N ∧ H_R[slot(N)]          H_R instantiated at the holder slot's de Bruijn index (capture-free, W1's
                                            inst); the conjunct is omitted when H_R is syntactically top
  carve-outs := U_N ++ [limpack_N]          limpack_N := ⋁_{L : R ∈ scope(L), kind(N) ∈ kinds(L)} lim_{L,a_N}(x̄), packed
                                            into one formula; omitted when no limitation is in scope
  predicate, sign, over, mode, rank, alterable, exception, hard := as written
then for every norm unit outside rights, in document order: unchanged
then, under the rule reading, for every right-derived permission predicate m by name: the node bar_m of 1.4
precedence := the author's `over` edges plus, for each bar_m, bar_m over every right-derived positive node on m
regulated, definitions, completions, soft block := those of D;  E″ as in 1.5
Lim_D := the premises of 1.3, in the order (limitation, act key, condition) sorted by name
```

`correlate` is total: on an ill-formed input it returns a junk document that `WellFormedSoft` rejects. It adds no
rank, no exception, no switch and no premise other than `Lim_D`; the only derived precedence is the bar's. Facts
proved in 9.2: `correlate_wellFormed`, `correlate_shape`, `correlate_identity` (no limitation, power, fan-out or bar:
`E″ = E` and the lines with the holder conjunct only), `correlate_identity_top` (and every `H_R` top: `correlate D`
is byte for byte the soft document `flattenTop D` that lists the lines before the outside rules, so `E″′` is its
`E′`).

### 4.3 The direct semantics `ValueRight`

`ValueRight_p(S, v̄)` is `ValueSoft` (soft-norms 4.2) read directly on the lines and units of `D`, for a structure
`S` over the symbols of `E″′` strictly below `p` and a typed tuple `v̄`, with two changes and no reference to `T″`:

```text
Step 0  In force.  live_N(x̄) := G_N(x̄) ∧ H_R(x_slot) ∧ ¬⋁U_N(x̄) ∧ ¬limpack_N(x̄) ∧ ¬switch_N(x̄) ∧ [default] ¬excepted_N(x̄)
        A line is live by its own terms: guard, holder guard, author carve-outs, the limitations in scope, its
        switches, its exception. No other rule occurs. A unit outside rights has W1's/soft's live.

Bar     Under the rule reading, for a right-derived positive line N on permission predicate m:
        barred_N(x̄) := aimed_m(x̄), and in W1's recursion on the author precedence DAG
          yields_N  := applies_N ∨ barred_N ∨ ⋁_{children} yields_E       the bar decides beneath N
          selects_N := applies_N ∧ ¬barred_N ∧ ¬⋁_{children} yields_E
        and the strict negative decision on m gains a disjunct:  N^s_m(x̄) := (soft's N^s_m) ∨ aimed_m(x̄).
        Every other line and every unit outside rights uses W1's yields/selects unchanged.

Steps 1–4  as soft-norms 4.2 with these live, yields, selects and N^s: strict rules decide; a default line is blocked
        by a strict decision on its act, on its own predicate with either sign or against its effect across the
        declared dual pair (so a default liberty on m is blocked where aimed_m holds, through N^s_m, and so is a
        default obligation `+` line on m's dual r: the bar's `forbid` against the line's `require`, soft-norms 1.4);
        dominance by rank; default rules decide; ValueRight_p := some true | some false | some d_p | none.
```

`correlate_faithful` (9.2): `Norms.Value (soften (correlate D)) = ValueSoft (correlate D) = ValueRight D`. The first
equality is `soften_faithful`; the second is by unfolding: the holder conjunct and the packed carve-out are ordinary
guard and carve-out material, and the node `bar_m` applies exactly where `aimed_m` holds (no carve-out, no switch, no
exception), has no children, so it selects exactly there, giving the extra disjunct of `N^s_m`; its `over` edges make
it a child of every right-derived positive node on `m`, so W1's `yields`/`selects` on `T″` acquire exactly the
`barred_N` disjunct and conjunct above. Where `limpack_N` holds a line is silent: it neither selects nor yields, and
"the other rules and the default then decide" (norms.md 10.1(i, w)); a carve-out never grants anything.

### 4.4 Projections: who owes what to whom

```text
SelectsR(N, v̄)(S) := SelectsSoftD (correlate D) S (tupleVal v̄) (fuel) (node of N)     line N's node selects at v̄
duty line          := instance kind ∈ {claim, immunity, powerRecognition}
liberty line       := instance kind ∈ {liberty, powerLiberty}
owes_N(v̄)(S)       := N a duty line ∧ SelectsR(N, v̄)         bearer v̄_0 owes the act of N to holder v̄_slot(N) here
free_N(v̄)(S)       := N a liberty line ∧ SelectsR(N, v̄)      holder v̄_0 is at liberty here
rightsOf(h, S)     := {(R, N, v̄) : N a line of R, v̄ typed for p_N, v̄_slot(N) = h, SelectsR(N, v̄)}
dutiesOf(b, S)     := {(R, N, v̄) : N a duty line of R, v̄ typed, v̄_0 = b, SelectsR(N, v̄)}
```

`projections_agree` (9.2): for a duty line `N` of `R`, `(R, N, v̄) ∈ rightsOf(v̄_slot(N))` iff `(R, N, v̄) ∈
dutiesOf(v̄_0)`: the same right, line and tuple on both sides. The theorem is definitional, and that is its content:
a claim and the bearer's duty are one rule read from two ends; nothing is inferred. `owes_outcome`: for a line
instance `N` of `D` and a typed `v̄`, if `owes_N(v̄)` (or `free_N(v̄)`) and no rule of the opposite sign on `p_N`
selects at `v̄`, then `ValueSoft_{p_N}(S, v̄) = some sign(N)` (W1's `catalaValue_spec`); the line's membership in `D`
is a hypothesis, since a selecting node of some other document decides nothing here. At a point where both select
the document has a conflict and the projection still reports the duty. The projections are of selection: where a
strict rule of the same effect blocks a default line (4.5) the line is absent from `rightsOf`/`dutiesOf` although its
effect holds, and the report says "effect delivered by strict rule M" beside the holder. The projections say nothing a completion says: under a deny completion `¬O_m(v̄)` holds with no claim line at
all, which `owes` never reports; `O_r ∧ ¬done` and `¬O_m ∧ done` are the W3 definitions `violation` and `breach`
above the norms, and a duty is not a breach.

### 4.5 `Narrows`, licensing and the audit `limitationScope`

For a right-derived line instance `N` (node in `T″′ = soften(T″)`), a **narrowing mechanism** is any way `N` can fail
to select at a point where its own guard `own_N := G_N ∧ H_R[slot]` holds. `selects″_N = own_N ∧ ¬⋁U_N ∧ ¬limpack_N ∧
¬derived_N ∧ ¬⋁yields_children`, and `derived_N` unfolds to `excepted_N ∨ switch_N ∨ blocked_N ∨ dominated_N`
(soft-norms 5.1), so the mechanisms are exactly:

| Mechanism `n` | Active at `x̄` (`NarrowsAt`) | Condition `cond_n` | Licensed when |
|---|---|---|---|
| `carveOut i` (author `unless`) | `U_i(x̄)` | `own_N ∧ U_i` | cited (`cites["unless:i"]`) or certified |
| `exception M` (a node `M ≠ bar_m` in `N`'s exception subtree) | `yields_M(x̄)` | `yields_M` | cited (`cites["over:M"]` on `M`, or `M`'s `cites["narrows:N"]`) or certified |
| `limPack` | `limpack_N(x̄)` | | always: it is the limitation |
| `excepted` (`N` default) | `excepted_N(x̄)` | `excepted_N` | cited (`cites["exception"]`) or certified (through `Exc_T`'s necessary premises) |
| `switch π` | `off_{N,π}(x̄)` | `off_{N,π}` | cited (`cites["alterable:π"]`) or certified |
| `blockedBy M` (`N` default; strict `M ≠ bar_m` selects on `N`'s predicate with either sign, or against `N`'s effect across the dual pair: soft-norms 4.2 step 2; a bar's blocking, on `m` or across the dual pair, is the mechanism `bar` below) | `selects_M(x̄)` | `selects_M` | `M` of `N`'s sign on `N`'s predicate (same effect): always, by construction, reported "effect delivered by strict rule `M`"; `M` right-derived of the opposite effect: a collision, classified in 7.1, never a limitation; else cited (`M`'s `cites["narrows:N"]`) or certified |
| `dominatedBy M` (ranked colliding default `M`) | `dom(M, N)(x̄)` | `dom(M, N)` | `M` right-derived and the rank sentences cited: a collision resolved by a cited narrowing; else cited or certified |
| `bar` (rule reading; `N` on a right-derived permission predicate `m`, or `N` a default obligation `+` line whose predicate's permission dual is a right-derived permission predicate `m`: `barReach D N = some m`, 9.1) | `aimed_m(x̄)` | | always: Art. 30 by construction |

The bar surfaces in `T″′` as `exception bar_m` on every positive `N` on `m` (the `over` edges), as `blockedBy bar_m`
on every default `N` on `m` (soft-norms 4.2 step 2, same predicate) and as `blockedBy bar_m` on every default
obligation `+` line `N` on `m`'s dual `r` (soft-norms 4.2 step 2 across the dual pair: `bar_m` decides `forbid`
strictly, against `N`'s `require`); `narrowings D N` lists each as the one mechanism `bar`, attributed to Art. 30,
never as a separate exception or blocking entry, which is why `blockedBy M` and `sameEffectStrict` exclude `bar_m`.
The bar's reach is `barReach D N` (9.1): `N`'s own predicate when it is a right-derived permission predicate; else
the permission dual of `N`'s predicate when `N` is a default obligation `+` line and that dual is a right-derived
permission predicate; else none. A strict obligation `+` line on `r` is not blocked and is the pair conflict of 4.7
(fixture ψ). **Same-effect blocking**: soft-norms 4.2 step
2 blocks a default rule whenever a strict rule selects on its predicate with either sign, so a strict rule `M` of
`N`'s own sign, inside or outside rights, silences a default `N` while delivering its effect. It is a listed mechanism
(`narrowings_complete` needs it), licensed by construction, never a finding and never a `rightCollision`: the holder
stays permitted or the bearer stays bound. The report writes "effect delivered by strict rule `M`" only where no
strict rule of the opposite sign also decides there (`same_effect_delivered`, 9.2); otherwise W1's conflict is
reported as usual. `N` disappears from `rightsOf`/`dutiesOf` at such points, since the projections are of selection
(4.4), and the checklist says so.

"Certified" means an accepted tableau certificate for `Background_base″ ⊢ ∀x̄. cond_n°(x̄) → limpack_N(x̄)`: some
limitation with `N` in scope holds wherever the mechanism's condition does (° is W1's outcome substitution to
`E″′_base`). The target is the pack, not one limitation: under two limitations a mechanism whose condition entails
either is licensed, and a certificate for one limitation alone is not the target (fixture ρ). Certification concerns
the declared conditions, never lawfulness. A line in scope of no limitation has nothing to license; its mechanisms
are reported under the reader's checklist only. The audit `limitationScope(D, certs)` lists every unlicensed
mechanism as a finding `UnlicensedLimitation: <mechanism> of rule <n> on right <R>`; it is a report line and never an
admission error, so a policy composed with the Declaration can be checked and answered (Fable 5). Authored precedence
and rank between two rights' lines are the author's resolutions and need a citation (13.6); blocking by another
right's strict line and dominance by a cited ranking are structural consequences of the reused semantics and are
classified, not licensed.

`limitation_scope_sound` (9.2), in words: with no finding, for every base-admissible situation and every line `N` in
scope of some limitation, if `N`'s own guard holds and `N` does not select, then some limitation covering `N` holds
there (`limpack_N`), or a cited mechanism is active, or another right's line collides, or a strict rule of `N`'s own
effect selects, or the bar applies (`aimed_m` for the `m` of `barReach D N`, on `N`'s predicate or across the dual
pair; fixture ψ). The first disjunct is the pack: with `N` under `L1` and `L2` and only `lim_{L2}`
true the line is rightly silent, and a conclusion naming `lim_{L1}` would be false (fixture ρ). Every mechanism
condition is evaluated through the outcome substitution on the base structure, as the guard and selection hypotheses
are; the certified case folds into the first disjunct through the certificates' soundness over `Background_base″`.

### 4.6 `noDistinction` and the restricted invariance claim

Let `cone(p)` be soft-norms 7.4's cone on `T″′`: the predicates reachable from the rules on `p` through guards,
carve-outs (including the packed and derived ones), definition bodies and the rules of lower regulated predicates.
For every right-derived predicate `p`, `noDistinction` reports `independent` when `cone(p) ∩ protected = ∅`, else
the lines on or below `p` whose guard or carve-outs mention a protected predicate, each **cited** (`cites["guard"]`,
the set `E`: Art. 16(1) "men and women of full age", 25(2) "motherhood and childhood") or **uncited** (the finding
`ProtectedInCone: <q> in rule <n> on right <R>`, a report line). The invariance theorem `no_distinction_sound` (9.2)
is exactly `cone_independent` with `Q := protected` on the predicates whose cone is protected-free (its hypothesis
`p ∈ regulatedNames T″` is supplied by `rightDerived_regulated` from well-formedness): on those, every completed
outcome is invariant under the protected predicates. No claim is made for the other predicates: the report
lists `E` with citations and the uncited hits beside the result and says "outcomes of the listed lines may depend on
the protected predicates". Beside every result, cited or not, the report states: this says nothing about whether the
decider of `lim`, of a condition, of an exception, or of a standard such as `arbitrary` or `degrading`
discriminates; those tables are open. Substantive equality (Art. 7) stays the open term `equal_before_law`.

### 4.7 The bar: scoped theorem and composition assumptions

Under the rule reading, `bar_blocks` (9.2): at every point where `aimed_m` holds, no right-derived positive node on
`m` selects and the strict negative decision `N^s_m` holds. `bar_value`: if every positive rule on `m` in `T″` is
right-derived, then `ValueSoft_m = some false` wherever `aimed_m` holds. `bar_blocks` also states the bar's reach
across the dual pair: a default obligation `+` line whose predicate's permission dual is `m` is blocked where
`aimed_m` holds (soft-norms 4.2 step 2, `forbid` against `require`), which 4.5 attributes to the mechanism `bar`
through `barReach` (fixture ψ). Its third conjunct ranges over every default node of `T″`, right-derived or
outside rights: a default rule on `m` of either sign and a default obligation `+` rule on `m`'s dual are blocked by
the bar's strict decision wherever `aimed_m` holds (soft-norms 4.2 step 2), so a default outside permission or
prohibition of the act and a default duty to do it are never in conflict with the bar (fixture η). Both are
theorems about `correlate`'s own output. What they do not cover is stated as the composition assumption, and it
concerns **selecting strict rules only**: an adopter's strict positive rule on `m` (no bar edge over it) selecting
where the bar selects is W1's intra-predicate conflict; a strict obligation on the same act (a claim line of another
right whose bearer sort is the holder sort, or an adopter's rule; soft-norms 1.4's dual pair) selecting there is a
pair conflict `O_r ∧ ¬O_m`, since a strict rule is never blocked; both are reported CONFLICT with a witness by the
unchanged conflict check, never silently resolved. The paraphrase of 2.1 and the report row of 7.1 state exactly
this division: default rules give way, selecting strict rules conflict. Under the query reading the report runs, per `m`, the entailment
`background″ ++ layer premises ⊢ ∀x̄. aimed_m(x̄) → ¬m(x̄)` and shows the certificate or a coherent countermodel
"exhibiting the liberty".

## 5. Limitation premises, admissibility and the conditional contract

### 5.1 Definitions

```text
Lim_D                 the premises of 1.3, universal base formulas over E″, regenerated at every site, bound to the
                      rights document hash, never taken from the wire; the `rights` Background generator slot after `soft`
Rights_D              := Lim_D
Background_base″      := Background_base′(correlate D) ++ Lim_D       (flags, literals, soft slot, rights slot)
background″           := background′(correlate D) ++ Lim_D
BaseAdmissible″ D B   := BaseAdmissible′ (correlate D) B ∧ Sat B Lim_D
RightsConflictFree D  := ∀B. BaseAdmissible″ D B → ConflictFree E″ T″′ B
```

`Lim_D` enters base admissibility exactly as `Exc_T` does (soft-norms 6.1): it is the author's declared constraint on
the open limitation and condition tables. Every formula in it is universal over base symbols, so the fragment and
small-model machinery of norms.md 7 apply to `T″′` unchanged.

### 5.2 What the rights route certifies

- `coherent_expands` and `soft_conflict_decomposition` are reused on `correlate D` (W1's `BaseAdmissible` on `E″′`),
  not restated; the global `soft_coherent_expands_all` is restated with `BaseAdmissible″` as
  `rights_coherent_expands_all` (9.3), since `Lim_D` narrows the admissible bases.
- `rights_conflict_free`: `RightsConflictFree D`, checked by W1's unchanged conflict machinery on `T″′` over
  `Background_base″`. In words: under any decision assignment that resolves the listed weighing points, satisfies the
  declared exception conditions and satisfies the declared limitation conditions, every situation has exactly one
  outcome for every regulated act. A witness is classified as soft-norms 6.3 classifies it (strict collision; pair
  conflict with a strict rule or a completion), and when both sides are right lines the report names both rights.
- The route theorems `rights_route_acceptance` and `rights_route_countermodel` are the soft route's restated with
  `BaseAdmissible″` and `background″` (9.3): `Lim_D` enters through the first layer's `Admissible_in`, as `Soft_T`
  does; `BackgroundSound`/`BackgroundComplete` hold for `background″`. A certified conclusion holds in every situation
  whose decision, exception and limitation tables satisfy the report's assumptions; a countermodel is such a
  situation, rendered in document terms ("limitation 29 holds here for Texas arresting Ann; it is determined by law
  and solely for a permitted purpose; the claim of right 9 is silent; by default a state may arrest").
- Every rights report lists `conditional_on` with the undischarged coherence premises used (`soft:coherence:*`) and
  the limitation premises used (`rights:limitation:*`) among the certificate's leaves, and the active couplings
  (`coupling:<id>`).

### 5.3 Vacuity

1. The P0 vacuity report runs over `Background_base″ ++ layer premises ++ Γ`, so a `Γ` that fixes `lim_{L,a}` true
   and a necessary condition false makes every dependent certificate `vacuous`, visibly (fixture λ); removing the
   condition admits that assignment.
2. A CONFLICT-FREE report exhibits one situation as a checked finite base model of `Background_base″ ++ Γ` (with its
   decision, exception and limitation tables) or reports that line UNKNOWN with the budget (soft-norms 6.5).
3. A limitation alone proves nothing about any act unless the premises constrain `lim_{L,a}`; a default line alone
   proves nothing unless they constrain `excepted_N`; the report says so.

## 6. Readings and couplings

### 6.1 Axes and per-unit sets

In translation a right unit whose bearer, polarity, incident or force the source leaves open is a W2 reading set
whose candidates are complete right blocks with elaborated lines, each labelled on every open axis (3.3) and
separated from the others by a checked situation; a candidate without lines is an inventory and counts nothing. A
cited narrowing closes an axis the text fixes (Art. 5, 9 "No one shall be subjected to": negative; Art. 8 "by the
competent national tribunals": positive, the state; Art. 16(3) "protection by society and the State": bearer and
positive; Art. 22, 26(1): force default). The base is per unit: no choice is shared unless a coupling says so.

### 6.2 Couplings

A coupling `c` on axis `A` over sets `S_1, …, S_k` restricts the complete choices to those in which the chosen
candidates of `S_1, …, S_k` carry the same label on `A`. Two couplings on one axis whose set lists share a set
constrain each other, so the unit of choice is a **component**: a connected component of the graph on the sets of
axis `A` whose edges are the couplings on `A`; every set of a component takes one label, and distinct components of
the same axis are chosen independently (fixture χ). The admissible label values of a component are those carried by
some candidate in every set of the component; if none is, `CouplingLabelMissing`. Enumeration (W2 `plan_choices`,
extended): a joint assignment gives one admissible value to every component of every axis; the number of complete
choices is the sum over joint assignments of the product over sets of the number of candidates consistent with every
value assigned to a component containing the set; a set coupled on two axes may have no candidate for some joint
assignment, and that assignment contributes zero; when every joint assignment contributes zero the couplings are
unsatisfiable together, `CouplingUnsatisfiable: <ids>` (an error at admission, never a vacuous verdict). Beyond 64
the verdict is UNKNOWN and the report names the units whose sets still hold more than one consistent candidate. A conclusion checked under couplings carries
`coupling:<id>` for each, its paraphrase says "reading every article with the same <axis>, because <units>", and the
citation is recorded as the interpretation's rationale, not as a proof that mixed readings are impossible. The pilot
applies three couplings, each citing the Preamble: bearer ("every individual and every organ of society … Member
States have pledged"), polarity ("to secure their universal and effective recognition and observance"), force ("a
common standard of achievement"); uncoupled, the same document's conclusions are UNKNOWN with the units named.

### 6.3 Per-choice checking

A right reading is a norm-kind reading (document.md): each complete choice is elaborated separately through
`correlate` and the soft route and the verdict is ALL / SOME / NONE / UNKNOWN across choices, a choice being global
per unit. A cited result carries its choices and couplings; citing it under incompatible ones is rejected.

## 7. The report

### 7.1 The five questions

| Question | Method | Result |
|---|---|---|
| Who owes what to whom here? | `rightsOf`, `dutiesOf` on the example situation (4.4) | per holder: (right, line, bearer, act); per bearer: (right, line, holder, act); "nobody owes the holder anything under this reading" when empty |
| Can the rights and duties contradict each other? | W1 conflict check on `T″′` over `Background_base″`; soft classification of `CP(T″)` (soft-norms 6.2) | CONFLICT (strict collision between two right lines or with an outside rule, or a pair conflict with a strict rule or a completion; both rights named) / CONFLICT-FREE conditional on `Coh_T` and `Lim_D` / UNKNOWN; per default pair RANK-RESOLVED (cited ranking named) / DISJOINT / WEIGHING POINT / UNKNOWN; strict–default blocking shown under the default line |
| Is every narrowing of a right licensed? | `limitationScope` (4.5) | per line: each mechanism licensed by (limitation / cited / certified / collision / effect delivered by strict rule `M` / bar) or `UnlicensedLimitation` |
| Do outcomes depend on the protected predicates? | `noDistinction` (4.6) | per right-derived predicate: `independent` / depends: cited lines `E`, uncited `ProtectedInCone`; the decider sentence beside every result |
| Does any right permit a destructive act? | rule reading: `bar_blocks`, `bar_value`, composition conflicts; query reading: per-`m` entailment | rule, per `m`: every right-derived positive line on `m` barred; every default rule on `m` and every default obligation `+` rule on its dual blocked (shown under the default rule, never a conflict); each strict obligation on the act and each strict outside permission on `m` that selects where `aimed_m` holds listed as CONFLICT with its witness (4.7); query: certificate or countermodel per `m` |

### 7.2 Residual lines (W2 coverage, item 5)

Beside open terms, assumptions, bridge leaves, unresolved reading sets and the soft lines: `bearer_readings`,
`polarity_readings`, `incident_readings`, `force_readings` (per unit), `couplings` (axis, coupled units, citations;
a coupled axis counted once), `limitation_terms` (each `lim` and `cond` with decider; `unstated` counted
separately), `limitation_premises_used` (per certificate), `unlicensed_limitations` and `distinction_hits` (findings,
cited or uncited), `power_shadows` (per power "recognition required; later effects not modelled"; per immunity
"prohibition on the act; its effect on status not modelled"), `narrowings` (with citations). A right whose active
lines are strict rules over declared vocabulary with no open term is CHECKED; one with an open standard in a guard,
act, limitation or condition is OPEN; one whose axes are unsettled is READINGS only when every candidate has
elaborated lines and a distinguishing situation; Art. 29(1) is UNFORMALISED. No new status.

### 7.3 Status text

```text
CONFLICT-FREE among rules on the same act, conditional on <k> coherence premises and <l> limitation premises
  (<labels>)[, under couplings <ids>]; <j> weighing points open; situation exhibited: yes | UNKNOWN (<budget>)
CONFLICT: <witness kind> at <situation>            witness kind ∈ {strict collision on <p> between right <R> and
                                                   right <R′> | rule <n>, pair conflict on <act> with <strict rule |
                                                   completion> against <line of right R>}
UNLICENSED: <m> narrowing mechanisms without licence (<lines>)      a finding beside the status, never a status
NO DISTINCTION: independent on <predicates>; depends on protected predicates through <lines> (cited: …; uncited: …);
  nothing is claimed about the deciders of open terms
UNKNOWN: <target>, <budget>
```

## 8. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `IncidentShape: <line> on right <R>` | shape table of 1.2 violated | error |
| `HolderSlotAmbiguous: <line>` | two object slots of the holder sort and no `holder_slot` | error |
| `RightWithoutIncident: <R>` | a right with no line after all `includes` | error |
| `UnknownRight: <r>` | a scope or `right_lines` names an undeclared right | error |
| `FanOutUndeclared: <line>, <sort>` | a fan-out map misses a bearer sort, or a mapped predicate differs in act, role or non-subject sorts | error |
| `MissingExceptionDecider: limitation <L>` / `condition <c>` | no decider at any level | error |
| `DuplicateDeclaration: right <R>` / `limitation <L>` / `bar` / `holder <s>` | duplicates | error |
| `UnknownSymbol: sort <s>` / `unit <u>` | undeclared sort in the block; an unknown cited unit | error |
| `InvalidInput: protected <q>` / `alters <act>` / `author predicate <p> begins with rights__` / `name <n> begins with rights-` / `line <n> has predicate and fan_out` | field consistency (1.6, 3.1, 3.2) | error |
| `CouplingLabelMissing: <id>, <set>` | a coupled set lacks the axis label on some candidate, or a component has no common label value | error |
| `CouplingUnsatisfiable: <ids>` | the couplings together admit no complete choice (6.2) | error |
| `ResourceLimit: carve-outs of rule <n>` (six on a right line) / `rights` / `limitations` / `conditions` / `identifier <n> exceeds 64 bytes` (a switch name derived from a generated rule name and a party, 1.6) | limits (11) | error |
| `UnsupportedProfile: rights@0 requires soft-norms@0` | profile gate | error |
| soft-norms 8 and norms.md 11.1 on `T″`, `T″′` | unchanged | as there |
| `UnlicensedLimitation: <mechanism> of rule <n> on right <R>` | audit 4.5 | finding |
| `ProtectedInCone: <q> in rule <n> on right <R>` | audit 4.6, uncited | finding |

Diagnostics follow soft-norms' check order, then the rights checks in document order (block, rights and lines,
limitations, bar, couplings), then the elaborated `T″` through `WellFormedSoft`. Findings are report lines with the
line's span. Existing P0, W1 and soft diagnostics are unchanged.

## 9. Lean (item 4): definitions and the exact statements to prove

Files: `lean/VE/Rights/Tree.lean` (syntax, `WellFormedRights`, the rights vocabulary, `E″`), `Correlate.lean`
(`correlate`, `limPremises`, shape lemmas), `Semantics.lean` (`ValueRight`, the direct predicates, faithfulness),
`Projections.lean` (`SelectsR`, `owes`, `rightsOf`, `dutiesOf`), `Scope.lean` (`Narrowing`, `NarrowsAt`,
`limitationScope`, soundness), `Distinction.lean` (`noDistinction`, the restricted invariance), `Bar.lean`
(`bar_blocks`, `bar_value`), `Route.lean` (`BaseAdmissibleR`, the restated route), `Wire.lean`, `Admission.lean`,
`Run.lean` (the `ve_rights_route` executable), and `lean/RIGHTS.md` listing each theorem in plain words. Frozen
`Norms/*`, `SoftNorms/*` (once merged), `Route/*` and all P0 sources are untouched; `VE.lean`, `VE/Audit.lean` and
`lakefile.toml` gain imports, audit entries and the new target only; the audit allowlist is unchanged and no name
contains a prime or the audit's banned words. Names below have prefix `VE.Rights.`; soft names are
`VE.SoftNorms.*` as in soft-norms.md 9, W1 names `VE.Norms.*`. The blocks are statement schemata.

### 9.1 Definitions

```lean
namespace VE.Rights
open VE.Norms (Regulated Node tupleVal Sat forget outcomeBase subst restrictAll size before)
open VE.SoftNorms (SoftNode SoftDoc soften envPrime WellFormedSoft ValueSoft SelectsSoftD DecidesSoftD
  StrictDecidesD cone backgroundBase' background' BaseAdmissible' softPremises)

inductive Kind | claim | liberty | immunity | power                       -- source kind, as authored; a limitation's `kinds` matches it
inductive IKind | claim | liberty | immunity | powerLiberty | powerRecognition   -- instance kind, what linesOf produces (1.2)
inductive Reading | rule | query

structure Condition where
  name          : String
  necessary     : Bool                 -- false = sufficient
  verbalisation : String
  decidedBy     : Option String
structure Limitation where
  name       : String
  scope      : Option (List String)    -- none = all
  kinds      : Option (List Kind)      -- none = all
  decidedBy  : Option String
  conditions : List Condition
  factors    : List String
structure Bar where
  name      : String
  reading   : Reading
  decidedBy : Option String
structure SourceLine where               -- a line as authored (3.2)
  kind        : Kind
  norm        : Option SoftNode          -- claim, liberty, immunity; its predicate is none exactly when fanOut ≠ []
  liberty     : Option SoftNode          -- power only
  recognition : Option SoftNode          -- power only
  fanOut      : List (String × String)   -- bearer sort ↦ predicate, empty when not a fan-out
  holderSlot  : Option Nat
  cites       : List (String × List String)
structure Line where                     -- a line instance (1.2): what every projection, audit and theorem ranges over
  right       : String
  source      : SourceLine
  kind        : Kind                     -- = source.kind; inScope matches it
  ikind       : IKind
  node        : SoftNode                 -- the instance's rule as written: the norm; a fan-out instance on its bearer
                                         -- sort's predicate, named rights-fan-<k>; a power's liberty or recognition unit
  bearer      : Option String            -- the bearer sort of a fan-out instance
structure Right where
  name   : String
  holder : String
  guard  : VE.Formula                    -- context [holder]
  lines  : List SourceLine
structure AltersEntry where              -- 1.1
  actKey      : String
  holderSlot  : Nat                      -- the affected holder's argument index
  status      : String
  recognition : Option String
structure RightsEnv where
  holders   : List String
  bearers   : List String
  protected : List String
  alters    : List AltersEntry
structure RightsDoc where
  soft   : SoftDoc                       -- E, lits, soft block, the norm units outside rights (T)
  rights : RightsEnv
  rs     : List Right
  limits : List Limitation
  bars   : List Bar                      -- length ≤ 1

def linesOf (D : RightsDoc) : List (String × Line)       -- (right name, line instance) in instance order (1.6)
def holderSlot (D : RightsDoc) (N : Line) : Nat           -- 1.2, resolved from the instance kind and N.source.holderSlot
def dutyKind (N : Line) : Bool :=                         -- claim, immunity, powerRecognition
  match N.ikind with | .claim | .immunity | .powerRecognition => true | _ => false
def libertyKind (N : Line) : Bool :=                      -- liberty, powerLiberty
  match N.ikind with | .liberty | .powerLiberty => true | _ => false
def rightDerived (D : RightsDoc) (p : String) : Bool      -- p is the predicate of some line instance
def rightPermission (D : RightsDoc) (m : String) : Bool   -- m is the predicate of some liberty or powerLiberty instance
def barReach (D : RightsDoc) (N : Line) : Option String   -- 4.5: the right-derived permission predicate whose bar reaches N:
                                                          -- some N.node.pred when rightPermission D N.node.pred; else some m when
                                                          -- N.node.mode = .default, N.node.sign = true, VE.SoftNorms.dualPerm
                                                          -- (correlate D) N.node.pred = some m and rightPermission D m; else none
def fanIndex (D : RightsDoc) (N : Line) : Option Nat      -- k of 1.6 for a fan-out instance
def barIndex (D : RightsDoc) (m : String) : Nat           -- k of 1.6: position of m among the right-derived permission predicates by name
def limIndex (D : RightsDoc) (L : Limitation) (actKey : String) : Nat            -- k of 1.6 over (L, a) by name
def condIndex (D : RightsDoc) (L : Limitation) (c : Condition) (actKey : String) : Nat   -- k of 1.6 over (L, a, c) by name
def fanName (k : Nat) : String := s!"rights-fan-{k}"
def barRuleName (k : Nat) : String := s!"rights-bar-{k}"
def limName (k : Nat) : String := s!"rights__lim__{k}"
def condName (k : Nat) : String := s!"rights__cond__{k}"
def aimedName (k : Nat) : String := s!"rights__bar__{k}"
def ruleReading (D : RightsDoc) : Bool
def WellFormedRights (D : RightsDoc) : Bool               -- 4.1, then WellFormedSoft (correlate D)

/-- 4.2: total; on a well-formed input the real elaboration, otherwise a junk document. -/
def holderConj (D : RightsDoc) (N : Line) (G : VE.Formula) : VE.Formula   -- G ∧ H_R at the holder slot; G when H_R = top
def limPack (D : RightsDoc) (N : Line) : VE.Formula                        -- limpack_N: ⋁ of limF D L N over the L with inScope D L N.right N (right and
                                                                           -- source kind both filtered, 4.2); .bot when no limitation is in scope
def limPackList (D : RightsDoc) (N : Line) : List VE.Formula               -- [limPack D N], or [] when no limitation is in scope
def nodeOf (D : RightsDoc) (N : Line) : SoftNode                           -- guard, carve-outs, name, over as 4.2
def barNodes (D : RightsDoc) : List SoftNode                               -- by predicate name, rule names rights-bar-<k>
def envR (D : RightsDoc) : VE.Environment                                  -- E″ = D.soft.E + lim + cond + aimed (1.5); envPrime (correlate D) adds soft's decisions once
def correlate (D : RightsDoc) : SoftDoc
def flattenTop (D : RightsDoc) : SoftDoc :=                                -- the lines as written before the outside rules, nothing else
  { D.soft with T := { D.soft.T with nodes := (linesOf D).map (·.2.node) ++ D.soft.T.nodes } }
def outcomeSubst (D : RightsDoc) (φ : VE.Formula) : VE.Formula :=          -- φ°: W1's outcome substitution to E″′_base, as soft-norms 9 writes it
  subst (soften (correlate D)).T (size (soften (correlate D))) φ
def limPremises (D : RightsDoc) : List VE.Formula                          -- Lim_D
def aimedF (D : RightsDoc) (m : String) : VE.Formula                       -- the atom aimed_m(x̄)
def limF (D : RightsDoc) (L : Limitation) (N : Line) : VE.Formula          -- the atom lim_{L,a_N}(x̄)
def ownGuard (D : RightsDoc) (N : Line) : VE.Formula                       -- G_N ∧ H_R
def selectsR (D : RightsDoc) (N : Line) : VE.Formula :=                    -- selects″_N as a formula on T″′
  VE.Norms.selects (soften (correlate D)).T (VE.Norms.fuel (soften (correlate D)).T) (VE.SoftNorms.primeNode (correlate D) (nodeOf D N))

/-- 5.1 -/
def backgroundBaseR (D : RightsDoc) : List VE.Formula := backgroundBase' (correlate D) ++ limPremises D
def backgroundR (D : RightsDoc) : List VE.Formula := background' (correlate D) ++ limPremises D
def BaseAdmissibleR (D : RightsDoc) (B : VE.Structure) : Prop := BaseAdmissible' (correlate D) B ∧ Sat B (limPremises D)
def RightsConflictFree (D : RightsDoc) : Prop :=
  ∀ B : VE.Structure, BaseAdmissibleR D B → VE.Norms.ConflictFree (soften (correlate D)) B

/-- 4.3: the direct semantics as propositions, soft's with the rights live and the bar. -/
section Direct
variable (D : RightsDoc) (S : VE.Structure) (ρ : VE.Valuation S)
def LiveR (N : Line) : Prop :=
  (ownGuard D N).denote S ρ ∧ ¬ (∃ U ∈ N.node.carveOuts, U.denote S ρ) ∧ ¬ (limPack D N).denote S ρ ∧
  ¬ (VE.SoftNorms.switchF (correlate D) (nodeOf D N)).denote S ρ ∧
  (N.node.mode = .default → ¬ (VE.SoftNorms.exceptedF (correlate D) (nodeOf D N)).denote S ρ)
def BarredR (N : Line) : Prop :=
  ruleReading D = true ∧ N.node.sign = true ∧ rightPermission D N.node.pred = true ∧ (aimedF D N.node.pred).denote S ρ
def StrictYieldsR : Nat → Line → Prop          -- soft's StrictYieldsD with LiveR, plus BarredR as a yielding disjunct
def StrictSelectsR (f : Nat) (N : Line) : Prop  -- soft's StrictSelectsD with LiveR ∧ ¬ BarredR
def StrictDecidesR (p : String) (sign : Bool) : Prop :=
  (∃ N ∈ (linesOf D).map (·.2), N.node.pred = p ∧ N.node.sign = sign ∧ StrictSelectsR D S ρ (fuelR D) N) ∨
  (∃ M ∈ outsideRules D, M.pred = p ∧ M.sign = sign ∧ VE.SoftNorms.StrictSelectsD (correlate D) S ρ (fuelR D) M) ∨
  (sign = false ∧ ruleReading D = true ∧ rightPermission D p = true ∧ (aimedF D p).denote S ρ)
-- BlockedR, EligibleR, EffR, DominatedR, AppliesR, YieldsR, SelectsR, DecidesR: soft-norms 9.1's definitions with
-- StrictDecidesR in place of StrictDecidesD, LiveR in place of LiveD, and BarredR in YieldsR/SelectsR of right lines.
end Direct

noncomputable def ValueRight (D : RightsDoc) (r : Regulated) (S : VE.Structure) (vs : List S.Carrier) : Option Bool :=
  VE.Norms.catalaValue (DecidesR D S (tupleVal vs) r.name true) (DecidesR D S (tupleVal vs) r.name false) r.allowByDefault

/-- 4.4 -/
def SelectsRN (D : RightsDoc) (S : VE.Structure) (ρ : VE.Valuation S) (N : Line) : Prop :=
  SelectsSoftD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) (nodeOf D N)
def owes (D) (S) (N : Line) (vs : List S.Carrier) : Prop := dutyKind N = true ∧ SelectsRN D S (tupleVal vs) N
def free (D) (S) (N : Line) (vs : List S.Carrier) : Prop := libertyKind N = true ∧ SelectsRN D S (tupleVal vs) N
def rightsOf (D) (S) (h : S.Carrier) : Set (String × Line × List S.Carrier) :=
  { t | ∃ R N vs, t = (R, N, vs) ∧ (R, N) ∈ linesOf D ∧ VE.TupleTyped S (sortsOf D N) vs ∧
        vs.get? (holderSlot D N) = some h ∧ SelectsRN D S (tupleVal vs) N }
def dutiesOf (D) (S) (b : S.Carrier) : Set (String × Line × List S.Carrier) :=
  { t | ∃ R N vs, t = (R, N, vs) ∧ (R, N) ∈ linesOf D ∧ dutyKind N = true ∧ VE.TupleTyped S (sortsOf D N) vs ∧
        vs.head? = some b ∧ SelectsRN D S (tupleVal vs) N }

/-- 4.5 -/
inductive Narrowing
  | carveOut (i : Nat) | exception (M : String) | limPack | excepted | switch (party : String)
  | blockedBy (M : String) | dominatedBy (M : String) | bar
def narrowings (D : RightsDoc) (N : Line) : List Narrowing           -- syntactic, from T″′; exception bar_m and blockedBy bar_m fold into bar,
                                                                     -- on m and across the dual pair (bar listed iff barReach D N = some m)
def condF (D : RightsDoc) (N : Line) : Narrowing → VE.Formula        -- cond_n of the table (blockedBy M: selects_M on T″′)
def NarrowsAt (D) (S) (ρ) (N : Line) : Narrowing → Prop              -- the mechanism is active at ρ (a full structure)
def cited (D : RightsDoc) (N : Line) : Narrowing → Bool
def rightCollision (D : RightsDoc) (N : Line) : Narrowing → Bool     -- blockedBy/dominatedBy a right-derived line of the opposite effect
def sameEffectStrict (D : RightsDoc) (N : Line) (M : String) : Bool  -- N default; M ≠ bar_m a strict node of T″ on N's predicate with N's sign
def inScope (D : RightsDoc) (L : Limitation) (R : String) (N : Line) : Bool   -- R ∈ scope(L) ∧ N.kind ∈ kinds(L), the source kind
def licensed (D) (certs : List (Option VE.Tableau.Certificate)) (N : Line) : Narrowing → Bool
def limitationScope (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) : List Finding

/-- 4.6 -/
def distinctionHits (D : RightsDoc) (p : String) : List (Line × String × Bool)   -- line, protected predicate, cited
def noDistinction (D : RightsDoc) : List Finding
```

`fuelR D` is `(correlate D).T.nodes.length`; `outsideRules D` are the norm units outside rights; `sortsOf D N` the
argument sorts of `N`'s predicate; `Finding` is a structure of code, rule, right and span. `φ°` below abbreviates
`outcomeSubst D φ`, as soft-norms 9 writes it. The tuple convention is W1's.

### 9.2 Theorems: elaboration, the direct semantics, projections, scope, distinction, bar

```lean
/-- 4.1 ⇒ soft well-formedness of T″ over E″. -/
theorem correlate_wellFormed (D : RightsDoc) (h : WellFormedRights D = true) : WellFormedSoft (correlate D) = true

/-- 4.2: what correlate changes and what it keeps. -/
theorem correlate_shape (D : RightsDoc) (h : WellFormedRights D = true) :
  (correlate D).E = envR D ∧ (correlate D).lits = D.soft.lits ∧ (correlate D).soft = D.soft.soft ∧
  (correlate D).T.regulated = D.soft.T.regulated ∧ (correlate D).T.definitions = D.soft.T.definitions ∧
  (correlate D).T.nodes = (linesOf D).map (fun RN => nodeOf D RN.2) ++ D.soft.T.nodes ++ barNodes D

theorem correlate_identity (D : RightsDoc) (h : WellFormedRights D = true)
    (hn : D.limits = [] ∧ (∀ R ∈ D.rs, ∀ N ∈ R.lines, N.kind ≠ .power ∧ N.fanOut = []) ∧ D.bars = []) :
  (correlate D).E = D.soft.E ∧
  (correlate D).T.nodes =
    (linesOf D).map (fun RN => { RN.2.node with guard := holderConj D RN.2 RN.2.node.guard }) ++ D.soft.T.nodes

/-- Every H_R top as well: the whole soft document, not only its nodes, so the vocabulary identities are corollaries.
    envR adds nothing without limitations and bars; soft's decisions are generated once, by soften, on both sides. -/
theorem correlate_identity_top (D : RightsDoc) (h) (hn) (ht : ∀ R ∈ D.rs, R.guard = .top) :
  correlate D = flattenTop D
theorem correlate_identity_top_env (D : RightsDoc) (h) (hn) (ht) :
  envR D = D.soft.E ∧ envPrime (correlate D) = envPrime (flattenTop D)
  -- by rewriting with correlate_identity_top and correlate_shape

/-- Generated formulas denote their direct counterparts (W1's *_denote pattern). -/
theorem liveR_denote (D) (N) (S) (ρ) :
  (VE.SoftNorms.liveF (correlate D) (nodeOf D N)).denote S ρ ↔ LiveR D S ρ N
theorem bar_denote (D) (h) (hb : ruleReading D = true) (m) (hm : rightPermission D m = true) (S) (ρ) :
  VE.SoftNorms.StrictSelectsD (correlate D) S ρ (fuelR D) (barNode D m) ↔ (aimedF D m).denote S ρ
theorem strictDecidesR_denote (D) (h) (p) (sign) (S) (ρ) :
  StrictDecidesD (correlate D) S ρ p sign ↔ StrictDecidesR D S ρ p sign

/-- 4.3: W1's Value on T″′ is ValueSoft on T″ is ValueRight on D. -/
theorem correlate_faithful (D : RightsDoc) (h : WellFormedRights D = true) (r : Regulated)
    (hr : r ∈ (correlate D).T.regulated) (S : VE.Structure) (vs : List S.Carrier) :
  ValueSoft (correlate D) r S vs = ValueRight D r S vs
theorem correlate_value (D) (h) (r) (hr) (S) (vs) :
  VE.Norms.Value (soften (correlate D)).T r S vs = ValueRight D r S vs
  -- := (VE.SoftNorms.soften_faithful (correlate D) (correlate_wellFormed D h) r hr S vs).trans (correlate_faithful D h r hr S vs)

/-- 4.4: correlativity by construction, the same R, N and tuple on both sides. -/
theorem projections_agree (D : RightsDoc) (h : WellFormedRights D = true) (S : VE.Structure)
    (R : String) (N : Line) (vs : List S.Carrier) (hN : (R, N) ∈ linesOf D) (hk : dutyKind N = true)
    (typed : VE.TupleTyped S (sortsOf D N) vs) (hh : vs.get? (holderSlot D N) = some hv) (hb : vs.head? = some bv) :
  (R, N, vs) ∈ rightsOf D S hv ↔ (R, N, vs) ∈ dutiesOf D S bv

/-- The completed outcome is a corollary of a selecting duty or liberty line of the document. -/
theorem owes_outcome (D : RightsDoc) (h : WellFormedRights D = true) (S : VE.Structure) (R : String) (N : Line)
    (hN : (R, N) ∈ linesOf D) (vs : List S.Carrier) (typed : VE.TupleTyped S (sortsOf D N) vs)
    (hs : SelectsRN D S (tupleVal vs) N)
    (hno : ¬ DecidesSoftD (correlate D) S (tupleVal vs) N.node.pred (!N.node.sign)) :
  ValueSoft (correlate D) (regOf D N.node.pred) S vs = some N.node.sign

/-- "Effect delivered" (4.5): a strict decision of N's sign fixes the outcome to N's sign unless a strict decision of
    the opposite sign is also present, in which case W1's conflict is reported instead. Soft-norms 4.2 steps 2 and 4:
    every default on the predicate is blocked, so the completed decisions are the strict ones. -/
theorem same_effect_delivered (D : RightsDoc) (h : WellFormedRights D = true) (S : VE.Structure) (R : String)
    (N : Line) (hN : (R, N) ∈ linesOf D) (vs : List S.Carrier) (typed : VE.TupleTyped S (sortsOf D N) vs)
    (hsd : StrictDecidesD (correlate D) S (tupleVal vs) N.node.pred N.node.sign)
    (hno : ¬ StrictDecidesD (correlate D) S (tupleVal vs) N.node.pred (!N.node.sign)) :
  ValueSoft (correlate D) (regOf D N.node.pred) S vs = some N.node.sign

/-- 4.7: scoped to correlate's own output; the third conjunct is soft-norms 4.2 step 2 under the bar's strict
    decision, over every default node of T″ (a right line or a rule outside rights): a default rule on m of either
    sign, and a default `require` on m's dual blocked by the bar's strict `forbid`; on a right line the dual-pair
    case is the reach 4.5 attributes to the mechanism `bar` (barReach). -/
theorem bar_blocks (D : RightsDoc) (h : WellFormedRights D = true) (hb : ruleReading D = true)
    (m : String) (hm : rightPermission D m = true) (S : VE.Structure) (ρ : VE.Valuation S)
    (ha : (aimedF D m).denote S ρ) :
  (∀ RN ∈ linesOf D, RN.2.node.pred = m → RN.2.node.sign = true → ¬ SelectsRN D S ρ RN.2) ∧
  StrictDecidesD (correlate D) S ρ m false ∧
  (∀ M ∈ (correlate D).T.nodes, M.mode = .default →
     (M.pred = m ∨ (M.sign = true ∧ VE.SoftNorms.dualPerm (correlate D) M.pred = some m)) →
     ¬ SelectsSoftD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) M)
-- For a right line N the third conjunct at M := nodeOf D N is ¬ SelectsRN D S ρ N (definitional).
theorem bar_value (D) (h) (hb) (m) (hm)
    (honly : ∀ M ∈ (correlate D).T.nodes, M.pred = m → M.sign = true → ∃ RN ∈ linesOf D, nodeOf D RN.2 = M)
    (S : VE.Structure) (vs : List S.Carrier) (ha : (aimedF D m).denote S (tupleVal vs)) :
  ValueSoft (correlate D) (regOf D m) S vs = some false
-- Composition (not a theorem, the stated assumption; selecting strict rules only): a strict positive rule on m
-- outside honly, or a strict obligation on m's act, selecting where aimed_m holds is a W1 conflict point of T″′ and
-- is reported by the unchanged check. A default one is blocked there by the third conjunct and is never a conflict.

/-- 4.5: with no finding, a line in scope gives way only where some limitation covering it holds (the pack), a cited
    mechanism is active, another right's line collides, a strict rule of its own effect selects, or the bar applies,
    on the line's own permission predicate or across the dual pair (barReach). L, hL and hs witness that the pack is
    non-empty; every mechanism condition is read through the outcome substitution on B, as the guard and selection
    hypotheses are. -/
theorem limitation_scope_sound (D : RightsDoc) (h : WellFormedRights D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : limitationScope D certs = [])
    (L : Limitation) (hL : L ∈ D.limits) (R : String) (N : Line) (hN : (R, N) ∈ linesOf D)
    (hs : inScope D L R N = true) (B : VE.Structure) (hB : BaseAdmissibleR D B)
    (vs : List B.Carrier) (typed : VE.TupleTyped B (sortsOf D N) vs)
    (hown : (ownGuard D N)°.denote B (tupleVal vs)) (hns : ¬ (selectsR D N)°.denote B (tupleVal vs)) :
  (limPack D N).denote B (tupleVal vs)                                                            -- some limitation in scope holds
  ∨ (∃ n ∈ narrowings D N, cited D N n = true ∧ (condF D N n)°.denote B (tupleVal vs))           -- a cited mechanism is active
  ∨ (∃ n ∈ narrowings D N, rightCollision D N n = true ∧ (condF D N n)°.denote B (tupleVal vs))  -- another right's line collides
  ∨ (∃ M, sameEffectStrict D N M = true ∧ (condF D N (.blockedBy M))°.denote B (tupleVal vs))      -- a same-effect strict rule selects
  ∨ (ruleReading D = true ∧ ∃ m, barReach D N = some m ∧ (aimedF D m).denote B (tupleVal vs))       -- the bar, on N's predicate or across the dual pair

/-- Its syntactic completeness: not selecting where the own guard holds means some mechanism is active. -/
theorem narrowings_complete (D) (h) (N) (hN : N ∈ (linesOf D).map (·.2)) (S) (ρ)
    (hown : (ownGuard D N).denote S ρ) (hns : ¬ SelectsRN D S ρ N) :
  ∃ n ∈ narrowings D N, NarrowsAt D S ρ N n

/-- The certified case: an accepted certificate for cond_n° → limpack_N over Background_base″. For a carve-out,
    condF already carries the own guard (own_N ∧ U_i), so no separate guard hypothesis is needed. -/
theorem licensed_certified_sound (D) (h) (N) (n) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (VE.Norms.envAt (soften (correlate D)) 0) (backgroundBaseR D)
             (VE.Norms.bindAll (sortsOf D N) (.imp (condF D N n)° (limPack D N))) c = true)
    (B) (hB : BaseAdmissibleR D B) (vs) (typed) (hact : (condF D N n)°.denote B (tupleVal vs)) :
  (limPack D N).denote B (tupleVal vs)

/-- Well-formedness puts every right-derived predicate among T″'s regulated names (cone_independent's hypothesis). -/
theorem rightDerived_regulated (D : RightsDoc) (h : WellFormedRights D = true) (p : String)
    (hp : rightDerived D p = true) : p ∈ VE.Norms.regulatedNames (correlate D).T

/-- 4.6: exactly cone_independent with Q := protected, on a protected-free cone. -/
theorem no_distinction_sound (D : RightsDoc) (h : WellFormedRights D = true) (p : String)
    (hp : rightDerived D p = true)
    (hcone : ∀ q ∈ cone (correlate D) p, q ∉ D.rights.protected)
    (B : VE.Structure) (R : String → List B.Carrier → Prop)
    (hR : ∀ q vs, q ∉ D.rights.protected → (R q vs ↔ B.relation q vs)) (vs : List B.Carrier) :
  (outcomeBase (soften (correlate D)) p).denote { B with relation := R } (tupleVal vs) ↔
    (outcomeBase (soften (correlate D)) p).denote B (tupleVal vs)
  -- := VE.SoftNorms.cone_independent (correlate D) (correlate_wellFormed D h) p (rightDerived_regulated D h p hp)
  --      D.rights.protected hcone B R hR vs

/-- The audit agrees with the hypothesis: `independent` is reported for p iff the cone is protected-free. -/
theorem noDistinction_sound (D) (h) (p) (hp) (hi : independentReported D p = true) :
  ∀ q ∈ cone (correlate D) p, q ∉ D.rights.protected
```

### 9.3 Theorems: the conditional contract and the wire

```lean
/-- Reused on correlate D, not restated: soft-norms 9.3's per-structure instance of W1's conflictFree_expands_document. -/
theorem coherent_expands (D) (h) (B) (hB : VE.Norms.BaseAdmissible (soften (correlate D)) B) :
  VE.Route.Unique (VE.Norms.DocumentExpansion (soften (correlate D)) B) ↔ VE.Norms.ConflictFree (soften (correlate D)) B
  -- := VE.SoftNorms.coherent_expands (correlate D) (correlate_wellFormed D h) B hB

/-- The global form is restated, since BaseAdmissibleR adds Lim_D: soft_coherent_expands_all's shape over the
    rights-admissible bases; from coherent_expands by restriction. -/
theorem rights_coherent_expands_all (D) (h) :
  (∀ B, BaseAdmissibleR D B → VE.Route.Unique (VE.Norms.DocumentExpansion (soften (correlate D)) B)) ↔ RightsConflictFree D

/-- 5.2, the certified statement: W1's conflictFreeCheck on T″′ with Background_base″. -/
theorem rights_conflict_free (D : RightsDoc) (h : WellFormedRights D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : rightsConflictFreeCheck D certs = true) :
  RightsConflictFree D
theorem rights_conflict_witness_sound {α} [DecidableEq α] (D) (h) (t) (ht : t ∈ VE.Norms.targets (soften (correlate D)))
    (M : VE.FiniteModel α) (valid : M.Valid (VE.Norms.envAt (soften (correlate D)) 0))
    (hb : backgroundValidR D M = true) (vs : List α) (typed) (hw : t.2.2.eval M (tupleVal vs) = true) :
  ¬ VE.Norms.ConflictFree (soften (correlate D)) M.asStructure ∧ ¬ RightsConflictFree D ∧
  (¬ VE.SoftNorms.NoStrictCollision (correlate D) M.asStructure ∨ ¬ VE.SoftNorms.NoHardPairConflict (correlate D) M.asStructure)

/-- Restated route pieces: the soft route's with BaseAdmissibleR and backgroundR; per-structure lemmas reused. -/
def rightsRoute (D) (h) (hc : RightsConflictFree D) :
  { L : VE.Route.Layer VE.Route.fol Unit // L.E_in = VE.Norms.envAt (soften (correlate D)) 0 ∧
    (∀ B, L.Admissible_in B ↔ BaseAdmissibleR D B) ∧ L.premises () = VE.Norms.elaborate (soften (correlate D)).T }
theorem rights_route_backgroundSound (D) (h) (hc) : VE.Route.BackgroundSound (rightsRoute D h hc).1 (backgroundR D)
theorem rights_route_backgroundComplete (D) (h) (hc) : VE.Route.BackgroundComplete (rightsRoute D h hc).1 (backgroundR D)

theorem rights_route_acceptance (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree D)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D))))
                  (backgroundR D ++ VE.Norms.elaborate (soften (correlate D)).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure, S.Admissible (VE.Norms.envAt (soften (correlate D)) (size (soften (correlate D)))) →
     VE.SoftNorms.holdsSoft (correlate D) S → VE.Norms.definitionsHold (soften (correlate D)) S →
     VE.Norms.profileHold (soften (correlate D)) S → Sat S (VE.Norms.backgroundBase (soften (correlate D))) →
     Sat S (softPremises (correlate D)) → Sat S (limPremises D) → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) []) →
     φ.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [] →
     ∀ B : VE.Structure, BaseAdmissibleR D B → Sat B Γ → φ.denote B [])

theorem rights_route_countermodel (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree D)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [])
    (hφ : φ.WellFormed (VE.Norms.envAt (soften (correlate D)) 0) [])
    (B : VE.Structure) (hB : BaseAdmissibleR D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, VE.Norms.DocumentExpansion (soften (correlate D)) B S ∧ Sat S (softPremises (correlate D)) ∧
       Sat S (limPremises D) ∧ Sat S Γ ∧ ¬ φ.denote S []

/-- The wire (norms.md 11.4 shape): decodeRightsSource decodes the environment with its rights block, the right,
    right_lines, limitation and bar units and the norm units outside rights; res.src.D is the decoded RightsDoc. -/
theorem rights_wire_conflict_sound (j : Json) (res : RightsConflictReplay) (h : replayRightsConflict j = .ok res)
    (hv : res.conflictFree = true) :
  Wire.decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedRights res.src.D = true ∧ RightsConflictFree res.src.D
theorem rights_wire_acceptance (j : Json) (r : RightsEntailmentReplay) (h : replayRightsEntailment j = .ok r)
    (hv : r.valid = true) :
  Wire.decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok r.src ∧
  (∀ S : VE.Structure, S.Admissible (VE.Norms.envAt (soften (correlate r.src.D)) (size (soften (correlate r.src.D)))) →
     VE.SoftNorms.holdsSoft (correlate r.src.D) S → VE.Norms.definitionsHold (soften (correlate r.src.D)) S →
     VE.Norms.profileHold (soften (correlate r.src.D)) S → Sat S (VE.Norms.backgroundBase (soften (correlate r.src.D))) →
     Sat S (softPremises (correlate r.src.D)) → Sat S (limPremises r.src.D) → Sat S r.premises →
     r.conclusion.denote S []) ∧
  (RightsConflictFree r.src.D →
     (∀ a ∈ r.premises, a.WellFormed (VE.Norms.envAt (soften (correlate r.src.D)) 0) []) →
     r.conclusion.WellFormed (VE.Norms.envAt (soften (correlate r.src.D)) 0) [] →
     ∀ B : VE.Structure, BaseAdmissibleR r.src.D B → Sat B r.premises → r.conclusion.denote B [])
theorem rights_wire_scope_sound (j : Json) (res : RightsScopeReplay) (h : replayRightsScope j = .ok res)
    (hv : res.findings = []) :
  Wire.decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    limitationScope res.src.D res.certs = []
theorem Run.rights_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : Run.usesRightsPath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.RightsAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
```

`backgroundValidR D M` is soft's `backgroundValid'` on `correlate D` conjoined with the finite evaluation of every
formula in `limPremises D`. `RightsAdmissionAnswer` is soft's `SoftAdmissionAnswer` with the rights decoder, the
`rights:limitation:*` leaves admitted only when equal to the regenerated formulas, `coupling:<id>` labels admitted
only when the coupling exists and the choice respects it, and the report consequence stated over `backgroundR D ++
elaborate (soften (correlate D)).T`. The soft route's document-wide theorems are restated (as they restate W1's)
because `Lim_D` is a new base premise; every per-structure lemma (`soften_faithful`, `hard_over_soft`,
`rank_resolves`, `cone_independent`, `soft_conflict_decomposition`, `coherent_expands`) is reused verbatim on
`correlate D`.

### 9.4 The executable `ve_rights_route`

`lean/.lake/build/bin/ve_rights_route <cases.json>`, root `RightsMain.lean`, a new Lake target; `Run.main` is the
executable root and no frozen file changes. On raw input it runs the frozen envelope and profile gate, requires
`rights@0`, `soft-norms@0` and `norms@0`, decodes the environment with its `rights` block through the soft decoder
plus a strict rights decoder (unknown fields rejected; the original complete environment hashed), decodes the right,
right_lines, limitation, bar and norm units and the active reading choice with its couplings, runs
`WellFormedRights`, regenerates `E″`, `T″`, `Lim_D`, `Exc_T`, `Coh_T`, `Background_base″`, `background″`, the layer
premises on `T″′`, every conflict, classification, scope and distinction target, validates bindings, and delegates
every checker call to the unchanged W1 and soft functions on the regenerated data. Case kinds:

| Kind | Extra input | Output |
|---|---|---|
| `rights-elaborate` | none | `environment_pp` (canonical `E″`), `lines` (per line instance: right, source kind, instance kind, node with its generated name and source keys, holder slot), `limitations` (per act: `lim`, conditions, premises, generated names with source keys), `bars`, `derived` (soft), `order`, `background` (with `soft` and `rights` slots), `premises`, `colliding_pairs`, `conflict_targets`, `narrowings` (per line, each mechanism with its licence), `distinction` (per predicate), `fragment`, `warnings` |
| `rights-projections` | a finite base model and optionally a holder or bearer constant | `rights_of`, `duties_of` in document terms |
| `rights-scope` | `certificates` per uncited mechanism | findings, or `licensed` with the licence per mechanism |
| `rights-conflict` | `packages` per target over `Background_base″`, or `witness` | `CONFLICT-FREE` (with `conditional_on`) / `CONFLICT` (classified, rights named) / `UNKNOWN` |
| `rights-bar` | rule reading: none; query reading: per `m` a certificate or countermodel | per `m`: barred right lines, blocked default rules (on `m` or its dual), strict composition conflicts with witnesses (7.1); or certificate / countermodel |
| `rights-certificate` | `premises`, `conclusion`, `certificate` | `valid`, `background`, `layers`, `conditional_on` |
| `admission` | W2 document with right units, reading sets, couplings and graph | `admitted`, `report`, `report_id`, `kinds`, `conditional_on` |

P0, W1 and soft cases without rights constructs delegate unchanged to `SoftNorms.Run.runCase`; malformed rights
inputs never fall back after a failed rights decode.

### 9.5 What is not claimed

No completeness of the conflict check or the classification outside norms.md 7 applied to `T″′`. No theorem about
the English surface (item 3). No claim that `ValueRight` matches an author's intent: that is this statement review
and W8's fidelity gate. No theorem about deciders: `lim`, every condition, `aimed`, every exception and every legal
standard are open, and no theorem says a decider ignores or honours a protected predicate or a party's instruction.
No theorem that a coupling is the right interpretation. No theorem about the effect of a power or of a forbidden
status change. No enumeration completeness.

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind, from
Lean (`tests/test_rights*.py`, the `rights` conformance family). Unless a fixture says otherwise: sorts `state`,
`person`; holders `person`; bearers `state`, `person`; acts declared with both roles as norms.md 3.1 (`<act>_required`
obligation deny-by-default with `permission: <act>_permitted`, `<act>_permitted` permission allow-by-default, "the
Declaration restricts, it does not license"); no soft block beyond the required fields; all guards `⊤` unless
stated; `Γ` empty; "selects" means `selects″` at the named situation. `lim_{l29,arrest}`, `determined_by_law_arrest`
and the like are the source-key renderings (1.6) of the generated predicates `rights__lim__<k>`, `rights__cond__<k>`;
the expected wire and residual bytes carry the generated names with the rendering beside them.

- **(α) A duty is not a breach.** `Right 3. Every person has the right to life. Claim of right 3. Every state must
  not deprive each person of life.`, no limitation. Situation 1: `deprives(Texas, Ann)` false; situation 2: true.
  `owes_N(Texas, Ann)` is true in both (the line selects unconditionally); `rightsOf(Ann) = {(r3, N, [Texas, Ann])}
  = dutiesOf(Texas)` with the same `R`, `N`, tuple; `O_{deprive_permitted}(Texas, Ann)` false in both by
  `owes_outcome`; `breach(Texas, Ann)` (W3, `¬permitted ∧ deprives`) false in 1 and true in 2. The paraphrase reads
  "Texas owes Ann: not to deprive her of life" in both situations.
- **(β) Fan-out.** `Claim of right 5. No one may subject each person to torture.` with `fan_out: {state:
  torture_permitted_state, person: torture_permitted_person}`: two instances `rights-fan-1` (no-torture, person) and
  `rights-fan-2` (no-torture, state), bearer sorts by name, on two predicates, one header, one right; every report
  renders the source line and sort beside the generated name; `rightsOf(Ann)` lists both bearers; the map without
  `person` is `FanOutUndeclared: no-torture, person`; a mapped predicate with a different act phrase likewise.
- **(γ) Limitation 29 on Art. 9, both completions.** `Claim of right 9. Every state must not arrest each person, if
  that arrest is arbitrary.`; `Limitation 29 (on every right)` with the two necessary conditions. Situation:
  `arbitrary(Texas, Ann)` and `lim_{l29,arrest}(Texas, Ann)` true. `arrest_permitted` allow-by-default: the line is
  silent, arrest permitted by the default, CONFLICT-FREE; deny-by-default: forbidden by the default. "Permitted
  where limitation 29 holds" is provable only once an adopter's rule `Every state may arrest each person, if
  limitation 29 holds where that state arrests that person` is composed (no conflict: the line is silent there).
  Certificate for `∀s p. arbitrary(s,p) ∧ ¬determined_by_law_arrest(s,p) → ¬arrest_permitted(s,p)` replays over
  `background″` (allow-by-default variant, through the necessary premise `lim → determined_by_law`); dropping that
  condition makes the same certificate fail, with a countermodel where `lim` holds and `determined_by_law` fails.
  Adopter's `Rule 7 (exception to claim 1 of right 9). Every state may arrest each person, if that person is a
  journalist`: `UnlicensedLimitation: exception 7 of rule no-arbitrary-arrest on right r9`; with the guard
  `… and limitation 29 holds where that state arrests that person` and the certificate for `yields_7° → lim`, no
  finding; the same sentence without `(exception to …)` is a W1 intra-predicate CONFLICT witness (arbitrary,
  journalist, `lim` false), not a narrowing. The generated English of `lim_{l29,arrest}` is `limitation 29 holds
  where {0} arrest {1}`.
- **(δ) Distinction.** A claim line guarded by `religion(h, r)` with no `cites["guard"]`: `ProtectedInCone:
  religion in rule <n> on right <R>`, the predicate reported `depends`, no invariance claim for it; the Art. 16(1)
  line with `cites["guard"]: ["u057"]` and a translation reading "men and women" as `sex(h, ·)`: listed in `E`,
  still no claim; right 3's predicate with a protected-free cone: `independent`, and the invariance witness (two
  base structures differing only on `religion` give equal outcomes). Every result carries the decider sentence.
- **(ε) Power and immunity.** Art. 16 power with `H_R = of_full_age(h)` on `marry_permitted(person, person)`
  (`alters`: `holder_slot` 0, `status` married, `recognition` recognise_marriage_required): two instances,
  powerLiberty then powerRecognition, both guarded by `of_full_age`, both matched by a limitation with `kinds:
  [power]` and neither by `kinds: [liberty]`; a strict claim line added to right 16 by `includes` (`Every state must
  register the marriage of each person`) is matched by `kinds: [claim]` and by neither `kinds: [power]` nor `kinds:
  [liberty]`, so its `limpack` omits a power-only limitation that both power instances carry (4.2's source-kind
  filter); situation: Ann of full age, Texas does not recognise:
  `owes_{recognise}(Texas, Ann)` true (powerRecognition is a duty line), `free_{marry}(Ann, Bob)` true (powerLiberty
  is a liberty line); `O_{recognise_marriage_required}(Texas, Ann)` true; nothing about post-marriage duties is
  derivable (no such predicate exists); Ann not of full age: neither instance selects. Art. 15(2) immunity on
  `deprive_of_nationality_permitted(state, person)` (`holder_slot` 1, `recognition` null), holder the object slot
  1: paraphrase "Every state must not deprive each person of nationality, if that deprivation is arbitrary; whether
  an attempted deprivation has effect is not modelled"; `power_shadows` lists both. `cannot` in the input is
  rejected with the `must not` rewrite.
- **(ζ) Polarity readings and a coupling.** Art. 3 as `rs_u022` with candidates labelled `polarity: negative` and
  `polarity: positive`, each with lines and a separating situation (a state that fails to protect but does not
  deprive): "Texas owes Ann protection" is SOME with the choice `rs_u022:positive` named; under a coupling
  `c-polarity` over `rs_u022` and `rs_u027` (Art. 5, narrowed to negative by citation), the choice `positive` is
  inadmissible (Art. 5 has no positive candidate) and the conclusion is NONE under the coupling, `conditional_on:
  coupling:c-polarity`; a candidate without lines is rejected as an inventory (counts nothing).
- **(η) The bar.** Rule reading; `Liberty of right 19. Every person may impart each idea.` (strict) and, in a
  second document, the same as `generally may` (default); `aimed_{impart}(Ann, I)` true: neither liberty selects;
  `N^s_{impart_permitted}` holds; `ValueRight = some false` (`bar_value`, all positive rules right-derived). Add a
  strict obligation on the same act (`Every person must impart each idea` as an adopter's rule outside rights; a
  claim line needs the holder in an object slot, which `impart(person, idea)` lacks, so the claim-line form of the
  same conflict is fixture ψ's): pair CONFLICT `O_r ∧ ¬O_m` at `(Ann, I)` with the witness; add instead an adopter's
  hard `Every person may impart each idea` without `(exception to …)`: intra-predicate CONFLICT at the same point;
  neither is silently resolved. Add instead an adopter's default `Every person generally may impart each idea`,
  or a default `Every person should not impart each idea`, or a default `Every person should impart each idea`
  (obligation `+` on the dual `impart_required`), each outside rights and uncited: at `(Ann, I)` the bar's strict
  decision blocks it (soft-norms 4.2 step 2; `bar_blocks`'s third conjunct at that node), it does not select, no
  conflict is reported, `ValueRight_{impart_permitted} = some false` and, for the third, `ValueRight_{impart_required}
  = some false` (the deny default); the report shows the blocking under the default rule and lists no
  `UnlicensedLimitation`, since the audit ranges over right lines only; as strict rules the same three give the two
  conflicts above and, for `must not`, the bar's own effect and no conflict. Query reading: the entailment
  `∀x̄. aimed(x̄) → ¬impart_permitted(x̄)` fails and the countermodel exhibits the liberty (`aimed` true, permitted).
- **(θ) Identity.** Every row of norms.md 10.1 and soft-norms 10 whose rule fits a shape of 1.2 (subject sort a
  declared bearer or holder sort, role and sign of a claim, liberty or immunity, at most six author carve-outs) and
  the limits of 11, wrapped as a one-line right with `H_R = ⊤`, no limitation, no bar: `correlate_identity_top`
  gives `correlate D = flattenTop D`, so `E″ = E`, `E″′ = E′` of the flattened document, and identical statuses,
  witnesses, diagnostics and premise lists, including the rows with default rules (their decision predicates are
  generated once, by `soften`, on both sides); rows that fit no shape are listed as skipped, never wrapped; with
  `H_R = charged(h)` the nodes differ exactly by the conjunct (`correlate_identity`).
- **(ι) Budget.** 40 right units, each a reading set with four candidates, one per pair of a binary `bearer` and a
  binary `polarity` label, and no other axis; couplings `c-bearer` and `c-polarity` over all 40 (one component per
  axis); four further units with binary uncoupled sets: complete choices 2·2·2⁴ = 64, admissible, `plan_choices`
  enumerates them; a fifth uncoupled binary set: 128, UNKNOWN naming the five uncoupled units; no coupling at all:
  4⁴⁰ choices, UNKNOWN naming the 40 units; three couplings (bearer, polarity, force) over 40 units each with 8
  labelled candidates, one per label triple, and no residual axis: 8 choices.
- **(κ) Force.** Art. 25 as a reading set {`must secure`, `should secure`} (labels `force: strict`, `force:
  default`): both candidates elaborated, `adequate` open under both; under the default choice the line's `excepted`
  mechanism is uncited: `UnlicensedLimitation: exception of rule <n> on right r25` under that choice, absent under
  the strict choice. Art. 22 with narrowing `n22` (`keeps: [default]`, `reason_spans: [u082]`) and the line's
  `cites["exception"]: ["u082"]` and necessary condition `exceeds_resources(s, p)`: the exception is licensed
  (cited); with the citation removed the finding returns; with the citation removed, limitation 29 declaring the
  sufficient condition `required_by_resources` ("the limitation is required by the organisation and resources of
  the state") and the exception's necessary condition written as that condition's atom `cond_{l29,required_by_resources,secure}`
  (`the limitation is required by the organisation and resources of the state where that state secures social
  security for that person`), the certificate for `excepted_N → limpack_N` replays through `Exc_T`'s necessary
  premise and `Lim_D`'s sufficient premise: licensed (certified).
- **(λ) Sole purpose.** `Γ` fixing `lim_{l29,arrest}(Texas, Ann)` true and `solely_for_permitted_purpose_arrest
  (Texas, Ann)` false: the P0 premise-set check reports `Background_base″ ++ Γ` inconsistent, every dependent
  certificate `vacuous`, and the exhibited-situation line says so; with `solely_for_permitted_purpose` removed from
  the conditions, the same `Γ` is consistent (a model exists) and nothing is vacuous. Symmetric for
  `determined_by_law`.
- **(μ) Collisions.** Under `nary@0`, the act `publish_about(person, item, person)` declared once, `person` both
  holder and bearer. Strict `Liberty of right 19. Every person may publish each item about each person.` (holder
  the subject slot 0) and strict `Claim of right 12. Every person must not publish each item about each person, if
  that item attacks the honour of the second person` (`holder_slot: 2`, the object slot of sort `person`; without it
  `HolderSlotAmbiguous` is not raised, since slot 0 is the subject, but the fixture names it for the paraphrase):
  CONFLICT with the witness (an attacking item), both rights named. The claim as `should not`: the default gives way where the
  liberty selects, CONFLICT-FREE, reported as blocking under right 12's line. Both default, unranked: `CP` pair,
  WEIGHING POINT with the witness, `conditional_on: soft:coherence:…`; with an adopter's `Claim of right 12 serves
  dignity. Liberty of right 19 serves expression. Dignity outranks expression.` cited (`cites["rank"]`):
  RANK-RESOLVED with the narrowing named; uncited: RANK-RESOLVED and `UnlicensedLimitation: dominatedBy … on right
  r19`.
- **(ν) Narrows over soft mechanisms.** A right line with `(users may turn off)` and no `cites["alterable:user"]`:
  `UnlicensedLimitation: switch user of rule <n> on right <R>`; cited: licensed. An adopter's strict `must not
  publish` on the same act blocking a default liberty line: finding unless the adopter's unit carries
  `cites["narrows:<line>"]` or a certificate for `selects_M° → limpack_N`; the same blocking by another right's
  strict line: a collision (μ), no finding; an adopter's strict `may publish` (same sign) blocking the default
  liberty: no finding, "effect delivered by strict rule <M>" (σ).
- **(ξ) Art. 29(1).** `Everyone has duties to the community …` is admitted as UNFORMALISED with reason `norms` and
  no line; writing `Claim of right 29. Every person must <?> the community` is rejected (`IncidentShape`: no act).
- **(ο) Slots.** A right line with seven author carve-outs: `ResourceLimit: carve-outs of rule <n>`; with six:
  accepted, and `T″′` carries eight on a default or switchable line (six author, `limpack`, `derived`) and seven on
  a strict unswitchable line, which has no derived carve-out (soft-norms 5.1); an ordinary rule with seven: accepted
  as in soft-norms 11.
- **(π) Deciders and readings of the bar.** A limitation without `decided_by` and no condition decider:
  `MissingExceptionDecider: limitation l29`; `unstated`: accepted and counted separately; two bars:
  `DuplicateDeclaration: bar`; `rs_u114` with both readings elaborated: results per choice, and the query reading's
  countermodel is shown as the separating situation.
- **(ρ) Two limitations.** Right 9's claim under `Limitation 29 (on every right)` and `Limitation 29b (on rights 9
  and 19)`, no other mechanism. Situation: own guard true, `lim_{l29,arrest}` false, `lim_{l29b,arrest}` true: the
  packed carve-out `limpack_N = lim_{l29,arrest} ∨ lim_{l29b,arrest}` holds, the line is silent, no finding, and the
  first disjunct of `limitation_scope_sound` holds as `limpack_N` although `lim_{l29,arrest}` is false; the
  paraphrase reads "this line gives way where limitation 29 or limitation 29b holds". A certificate for `cond_n° →
  lim_{l29,arrest}` alone is not the licensing target; `cond_n° → limpack_N` is, and one whose condition entails
  `lim_{l29b,arrest}` licenses the mechanism.
- **(σ) Same-effect strict blocking.** `Liberty of right 19. Every person generally may impart each idea.`
  (default) and an adopter's strict `Rule 4. Every person may impart each idea, if that person is a journalist.`
  outside rights, no citation. Where Ann is a journalist: rule 4 selects, the default liberty is blocked (soft-norms
  4.2 step 2, same predicate, same sign), `blockedBy 4` is listed, licensed by construction, no finding; the report
  reads "effect delivered by strict rule 4"; `free_N(Ann, I)` is false and `rightsOf(Ann)` omits the line there
  while `ValueRight_{impart_permitted}(Ann, I) = some true` (`same_effect_delivered`); the checklist says "Ann is
  permitted here by rule 4, not by right 19". Add a strict `Rule 5. Every person must not impart each idea, if that
  idea is secret.` and a secret idea by a journalist: rules 4 and 5 collide, the report shows W1's CONFLICT witness
  and no "effect delivered" line. The same rule 4 as `must not impart` (opposite sign, outside rights): `blockedBy
  4` is `UnlicensedLimitation` unless rule 4 carries `cites["narrows:<line>"]` or a certificate for `selects_4° →
  limpack_N`; as another right's strict `must not` line: a collision (μ), no finding. Rule reading of the bar on
  μ's ternary act under `nary@0` (`impart(person, idea)` has no holder object slot for a claim): `Liberty of right
  19. Every person generally may publish each item about each person.` (default) and a default `Claim of right 12.
  Every person should not publish each item about each person, if that item attacks the honour of the second
  person` (`holder_slot: 2`): where `aimed_{publish_about}` holds the claim is blocked by `bar_m` (same predicate,
  same sign): listed as `bar`, no finding.
- **(τ) The certified target.** Right 9's claim (`Every state must not arrest each person, if that arrest is
  arbitrary`, own guard `arbitrary(s, p)`) under limitation 29, which in this fixture additionally declares the
  sufficient condition `diplomatic_immunity` (`Limitation 29 holds where the arrest is barred by diplomatic
  immunity.`; illustrative, no source clause; the pattern of κ), so `Lim_D` contains `∀s p.
  cond_{l29,diplomatic_immunity,arrest}(s, p) → lim_{l29,arrest}(s, p)` with label
  `rights:limitation:l29:arrest_permitted:sufficient:diplomatic_immunity`. The line's author carve-out is `unless that
  person is a diplomat and the arrest is barred by diplomatic immunity where that state arrests that person`, `U_1 =
  diplomat(p) ∧ cond_{l29,diplomatic_immunity,arrest}(s, p)`, uncited. The target `(own_N ∧ U_1)° → limpack_N` is
  entailed over `Background_base″` through that sufficient premise alone (`°` is the identity on these base atoms):
  its certificate is accepted, the mechanism `carveOut 1` is licensed (certified), the certificate's leaves name the
  premise above and the report lists it under `limitation_premises_used`; without the sufficient condition no
  premise of `Background_base″` mentions `lim_{l29,arrest}` positively and no certificate for the target exists.
  Situation A: own guard false (the arrest is not arbitrary), `diplomat` true, `cond_{l29,diplomatic_immunity,arrest}`
  true, hence `lim_{l29,arrest}` true in every admissible base (the sufficient premise); the line is silent by its
  own guard and by the pack; `NarrowsAt(carveOut 1)` is true there, since the table's activity is the unguarded
  `U_1`, but `narrowings_complete` says nothing (its own-guard hypothesis fails), `limitation_scope_sound` says
  nothing (likewise) and `licensed_certified_sound` concludes nothing, because its activation hypothesis is the
  guarded certification condition `cond_n° = (own_N ∧ U_1)°`, false there, not the bare activity; the audit lists no
  finding, the certificate standing. Situation B: own guard false, `diplomat` true, the condition false and `lim`
  false: base-admissible (`Lim_D` is satisfied), `U_1` false, the line silent by its own guard only. Situation B is
  a countermodel to the stronger `diplomat → limpack_N`, so a certificate submitted for that formula is rejected
  (`checkCertificate` is sound over `Background_base″`); the audit consults certificates for the target formula
  only, and the unguarded `U_1° → limpack_N`, entailed here because `U_1` carries the sufficient atom, is neither
  the target nor consulted. Under two limitations (ρ) a certificate for `(own_N ∧ U_1)° → lim_{l29,arrest}` is not
  the target and does not license.
- **(υ) Generated names.** A limitation named `l-` followed by sixty `a` (62 bytes) over act `arrest_permitted`
  with condition `determined_by_law`: admitted; the predicates are `rights__lim__1` and `rights__cond__1` and the
  residual renders them as `limitation 29, arrest_permitted` and `limitation 29, arrest_permitted, determined by
  law`. An author rule named `rights-x`, a right named `rights-9`, a predicate `rights__lim__1` declared in `E`:
  `InvalidInput`. An author `over: ["rights-bar-1"]`: `UnknownSymbol`. Adding a second limitation `l0` renumbers
  `l29`'s predicates to `rights__lim__2`; every certificate is stale by 3.5 and the English of every guard that
  mentions `limitation 29 holds where …` is unchanged. Two fan-out lines over `{person, state}`: `rights-fan-1` to
  `rights-fan-4` in instance order, each rendered with its source line and sort. A fan-out line carrying `(users may
  turn off)` under a party named with 64 bytes: the derived switch name `soft__off__rights_fan_1__<party>` is 89
  bytes and elaboration is rejected, `ResourceLimit: identifier soft__off__rights_fan_1__… exceeds 64 bytes`, no
  truncation and no renaming; with a 39-byte party the name is exactly 64 bytes and admitted; the default variant's
  `soft__excepted__rights_fan_1` is 28 bytes and never overflows.
- **(φ) `alters` typing.** `deprive_of_nationality_permitted(state, person)` with `holder_slot: 1`, `status:
  has_nationality`, `recognition: null`: admitted, and Art. 15(2)'s immunity line on it (holder the object slot 1)
  is admitted; with `holder_slot: 0` (sort `state`, not a holder sort): `InvalidInput: alters
  deprive_of_nationality_permitted`; a power line on it: `IncidentShape` (`holder_slot` is not the subject slot and
  `recognition` is null); `marry_permitted(person, person)` with `holder_slot: 1` and a power line: `IncidentShape`
  (the liberty's subject slot is 0); with `holder_slot: 0`, `recognition: null` and a power line: `IncidentShape`;
  with `status: married` declared over `state`: `InvalidInput: alters marry_permitted`; an immunity on
  `marry_permitted` with the holder at slot 1 while `holder_slot` is 0: `IncidentShape`.
- **(χ) Coupling components.** Sets `S1` to `S4`, each with two candidates labelled `bearer: state` and `bearer:
  person`. Couplings `c1` over `{S1, S2}` and `c2` over `{S3, S4}` on `bearer`: two components, 2·2 = 4 complete
  choices, not 2; adding `c3` over `{S2, S3}` joins them: one component, 2 choices. A second document labels every
  candidate on `polarity` too, `S1`, `S2` and `S4` with all four (bearer, polarity) pairs and `S3` with only
  `(state, negative)` and `(person, positive)`; with `c1` to `c3` on `bearer` and `c4` over `{S1, S3}` on
  `polarity`: the joint assignments `(state, negative)` and `(person, positive)` contribute 1·2·1·2 = 4 each and
  the other two contribute zero, 8 choices; with `S1` restricted to `(state, positive)` and `(person, negative)`
  every joint assignment contributes zero: `CouplingUnsatisfiable: c1, c2, c3, c4`, an error, no verdict.
- **(ψ) The bar across the dual pair.** Rule reading; μ's ternary act under `nary@0` with both roles declared
  (`publish_about_required` obligation deny-by-default with `permission: publish_about_permitted`). Strict `Liberty
  of right 19. Every person may publish each item about each person.` (so `publish_about_permitted` is right-derived
  and `bar_m` exists) and a default positive claim on the dual obligation predicate, `Claim of right 12. Every person
  should publish each item about each person, if that item is a correction that the second person requests.`
  (`holder_slot: 2`; illustrative, no source article), with `cites["exception"]` and limitation 29 in scope.
  Situation: Bob requests the correction `I` of Ann (own guard true), `lim_{l29,publish_about}(Ann, I, Bob)` false,
  `excepted_N(Ann, I, Bob)` false, `aimed_{publish_about}(Ann, I, Bob)` true. `bar_m` selects and decides
  `¬publish_about_permitted` strictly; the claim is blocked across the dual pair (soft-norms 4.2 step 2: the bar's
  strict `forbid` against the line's default `require`) and does not select: `owes_N(Ann, I, Bob)` false,
  `dutiesOf(Ann)` omits the line there, `ValueRight_{publish_about_required} = some false` (the deny default) and
  `ValueRight_{publish_about_permitted} = some false` (`bar_value`), no conflict. `narrowings D N` lists `blockedBy
  bar_m` as the one mechanism `bar` (`barReach D N = some publish_about_permitted`), licensed by construction, no
  finding; the pack is false and the cited exception inactive, so the bar disjunct is the only disjunct of
  `limitation_scope_sound` that holds, `narrowings_complete` names `bar`, and `bar_blocks`'s third conjunct is the
  fact used; the checklist reads "this claim gives way where the act is aimed at the destruction of a right (Art.
  30)". The same claim as strict `must publish`: not blocked, pair CONFLICT `O_r ∧ ¬O_m` at `(Ann, I, Bob)` with the
  witness (4.7), never a narrowing. With the liberty of right 19 removed, `publish_about_permitted` is not
  right-derived, no `bar_m` exists, `barReach D N = none`, and the claim selects: `owes_N(Ann, I, Bob)` true.

Beside these: norms.md 10.6 to 10.10 and soft-norms 10's generated suites repeated on generated rights documents
(surface round trip with the new fields and metadata; identity of every existing fixture unchanged; certificate
binding against a changed holder guard, scope, condition, decider, protected list, `alters` entry, reading choice or
coupling; differential `correlate` Python versus Lean on 1,000 generated rights documents; DAG diagnostics on `T″′`).

## 11. Limits, regeneration, Rust

Rights ≤ 128, lines ≤ 256 in total with the other rules (W1's rule limit on `T″`, fan-out and bar nodes included),
limitations ≤ 16, conditions ≤ 8 per limitation, one bar, couplings ≤ 8, author carve-outs ≤ 6 on a right-derived
line, each unfolded formula within `MAX_NODES`; generated names are at most 19 bytes by construction and the
party-free derived soft names at most 30 (1.6), so neither can reach the 64-byte identifier limit; a derived switch
name `soft__off__rights_fan_<k>__<party>` is 24 + digits(k) + |party| bytes and is rejected as `ResourceLimit:
identifier <n> exceeds 64 bytes` when it exceeds the limit, never truncated (fixture υ); witness search uses the
existing bounds and `MAX_EVALUATIONS`; every overflow is `ResourceLimit` with the limit named, never a truth value. `E″`, `T″`, `Lim_D`, `Exc_T`, `Coh_T` and every
premise are regenerated from the decoded units and declarations at every trusted site (norms.md 11.3); a finite model
supplies base tables including limitation, condition, `aimed` and decision tables, and a supplied regulated table is
rejected as in W1. Rust never elaborates rights: on the `elaborated-document` family a rights case carries the
Python-generated `T″′` premises, `Soft_T` and `Lim_D` marked `untrusted: true`, and its verdict must agree with
Python's and Lean's regenerated ones (regression evidence; the trust path is Lean).

## 12. Statement review checklist (Astra + Fable, before items 2, 3 and 4)

1. The shape table (1.2) with instance kinds and the source kind kept; the holder slot rule; `alters` with its
   `holder_slot` (1.1, 3.1); fan-out through explicit per-bearer predicates.
2. Limitations as open predicates per act with named condition predicates per act (1.3), `Lim_D` as admitted base
   premises (5.1), sole purpose necessary; the generated English of `lim`, `cond` and `aimed`; the generated names
   by index with the reserved prefixes and the rejection of an overflowing derived switch name (1.6, 11).
3. `correlate` (4.2): the holder conjunct omitted when top, one packed limitation carve-out, six author slots, the
   bar's precedence as the only derived precedence, the node order of `correlate_shape`; `E″` before and `E″′`
   after `soften` (1.5); `correlate_identity` and `_top` as `correlate D = flattenTop D`.
4. `ValueRight` (4.3): soft's four steps with the rights live and the bar as a yielding/selecting condition and a
   strict negative disjunct; `correlate_faithful` by unfolding.
5. Projections (4.4): `owes` over selecting line instances, the same `R`, `N`, tuple in `projections_agree`;
   `owes_outcome` with membership and typing; `same_effect_delivered`; no projection from completions.
6. `Narrows` (4.5): the eight mechanisms with `blockedBy` at soft-norms 4.2 step 2's width, `narrowings_complete`,
   the licensing table (limitation / cited / certified / collision / same effect / bar), the bar's surfaces folded
   with its reach across the dual pair (`barReach`), findings not errors, `limitation_scope_sound`'s five disjuncts
   with `limpack_N` first and every condition outcome-substituted, the certification target `cond_n° → limpack_N`.
7. The restricted invariance claim (4.6): `cone_independent` with `Q := protected` on protected-free cones only;
   `E` listed; the decider sentence.
8. The bar (4.7): `bar_blocks` with its blocking conjunct over every default node on `m` or on `m`'s dual,
   `bar_value`, the composition assumption restricted to selecting strict rules and the matching paraphrase (2.1)
   and report row (7.1), the query reading.
9. The restated route (5.2, 9.3) with `BaseAdmissible″`; `conditional_on` with `rights:limitation:*` and
   `coupling:<id>`; vacuity (5.3).
10. Readings and couplings (3.3, 6): per-unit base, candidate labels, the coupling semantics and enumeration per
    component, `CouplingUnsatisfiable`, UNKNOWN naming units, the paraphrase and the citation's status as rationale.
11. The English table (2.1): one reading per wording; `is entitled to`; `shall` as a force reading set; `must not`
    for immunities; the three limitation sentences; the two bar sentences; the coupling sentence; the strict-text
    grammar (3.4) with `identifier` for condition names.
12. The diagnostics (8) and the fixtures (10), each against the definitions.
13. The plan's review questions: the static, explicitly incomplete power shadow; an uncited `excepted` on a default
    right line as a finding; authored precedence and rank between rights' lines as narrowings needing a citation.
14. The resolved choices of section 13 and the response table of section 14, each change against its finding and
    its regression fixture.

## 13. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **Conditions are named open predicates instantiated per act**, never formulas over the act's variables, so that
   a limitation of scope `all` types against every act; a formula condition would need per-act typing and is left
   to a later profile version.
2. **Fan-out uses an explicit per-bearer predicate map** in the unit, so the wire is canonical and act identity is
   W1's; the English `No one may` / `Everyone must` renders and parses the map.
3. **The holder conjunct is omitted when `H_R` is syntactically top**, so unguarded rights elaborate byte for byte
   and W1 and soft fixtures transfer verbatim (fixture θ), mirroring soft-norms 13.6.
4. **The bar's `over` edges cover default liberties too**, although blocking already silences them; the redundancy
   keeps one rule ("bar over every right-derived positive node on `m`") and one paraphrase.
5. **Couplings are a separate `couplings` list** with candidate `labels`, not a `shared_by` field on reading sets,
   so the existing narrowing validator, reading-set canonical bytes and identities are untouched.
6. **Authored precedence and rank between two rights' lines need a citation**; blocking by another right's strict
   line and dominance under a cited ranking are collisions. The plan's review question 3 asks whether the first
   should instead be a collision resolution.
7. **An uncited `excepted_N` on a default right line is a finding** under Art. 29(2)'s "only": the default force is
   a reading, and under that reading the source has not licensed the exception unless a clause is cited
   (Art. 22, 26(1)).
8. **The `rights` Background slot follows `soft`** in `ve/background.py` `HOOKS` order, so `background″` is
   definitions, literals, profile, soft, rights; the certificate premise order is `background″ ++ layer premises ++ Γ`.
9. **`aimed_m` is generated under both bar readings**, so the query reading is statable in the same vocabulary and
   the two readings differ by one node per `m` only.
10. **The recognition line of a power is a claim line** typed by the `alters` entry's `recognition` predicate; it is
    listed under `dutiesOf` like any claim and carries the "later effects not modelled" residual.
11. **Generated English for `lim`, `cond` and `aimed`** is derived from the act phrase by fixed templates, so every
    generated predicate has exactly one wording and no author template is needed.
12. **The rights document hash** covers the right, right_lines, limitation and bar units and the norm units outside
    rights; reading choices and couplings are W2 report metadata bound through the report identity, as W2 narrowings
    are today.
13. **Findings are report lines**: `UnlicensedLimitation` and `ProtectedInCone` never reject a document, so the
    composition question ("does this policy narrow a right the Declaration does not license?") is answerable.
14. **`rights@0` requires `soft-norms@0`** even for a document with only strict lines: `correlate` always produces a
    soft document, and the derived carve-out slot is reserved whether or not it is used.
15. **Generated names are indexed, not encoded or rejected** (1.6): the review offered both an injective encoding
    and collision-freedom by rejection; indices over the canonical orders 4.2 already fixes are bounded, injective
    and regenerable, so a long limitation name can never fail admission and no frozen validator changes; the
    reserved prefixes remain, so authored references to generated nodes are still impossible.
16. **`alters` carries an explicit `holder_slot`** rather than deriving the affected holder from the line: the block
    is checked on its own (3.1), and the immunity and power shapes are checked against it (4.1), which admits the
    state-to-person immunity and keeps the typing connection explicit.
17. **Same-effect strict blocking is licensed by construction and reported as an effect**, never as a finding or a
    `rightCollision`: a finding would be a false positive, since the holder's position is unchanged; the "effect
    delivered" sentence is asserted only in the absence of an opposite strict decision (`same_effect_delivered`).
18. **Releases are rejected, not admitted as liberties**: `need not` fits no shape and the bar ranges over
    permission predicates only; admitting a release as a liberty would be a design change.

## 14. Statement-review response tables (drafts 1 to 4)

The rights-spec review (`manage-agents/debates/rights-spec/{astra,fable}.md`, FIX, CONVERGED after round 3). Where
the two round-3 formulations differed (names by index or by rejection; `holder_slot` as a field or derived), this
draft takes the formulation that both reviewers proposed at some round and that the final Fable round adopted, and
records it in 13.15 and 13.16 for the verification round.

| Finding | Change in this draft | Where | Regression |
|---|---|---|---|
| Astra 1 (rounds 1–3), Fable round 2 — several limitations falsify `limitation_scope_sound`; the per-limitation "only" and certification target | first disjunct and certification target `limpack_N`, English "some limitation in scope holds"; `L`, `hL`, `hs` kept as the witness that the pack is non-empty; the "only" paraphrase over every covering limitation | 2.1, 4.5, 9.2 | (ρ), (τ) |
| Astra 2, round 3 item 1 — inventory incomplete: same-sign strict selection blocks a default; bar surfaces uncited | `blockedBy` widened to soft-norms 4.2 step 2 either sign; same-effect licensed by construction, "effect delivered by strict rule M", never a finding or `rightCollision`, asserted only without an opposite strict decision (`same_effect_delivered`); `exception bar_m` and `blockedBy bar_m` folded into `bar`; a fifth disjunct | 4.4, 4.5, 7.1, 9.1, 9.2 | (σ), (η), (ν) |
| Astra 3, Fable 4 — `owes_outcome` lacks membership and typing; activation on `B` through raw regulated tables; own-guard gap in `licensed_certified_sound`; `cone_independent`'s hypothesis | `(R, N) ∈ linesOf D` and `typed`; every disjunct and `hact` as `(condF D N n)°.denote B`; `ruleReading` on the bar disjunct; `rightDerived_regulated` supplies `p ∈ regulatedNames` | 4.4, 4.6, 9.2 | (τ), (α) |
| Astra 4, Fable 1, round 2 — generated names violate W1's grammar and the 64-byte limit; delimiter maps not injective | `rights-fan-<k>`, `rights-bar-<k>`, `rights__lim__<k>`, `rights__cond__<k>`, `rights__bar__<k>` over canonical orders; reserved prefixes `rights-` and `rights__`; ≤ 19 bytes; source keys rendered beside every generated name; condition names never enter a predicate name | 1.3, 1.4, 1.6, 3.2, 4.1, 4.2, 8, 11 | (υ), (β) |
| Astra 5, Fable 2 and 3 — incident typing rejects the state-to-person immunity; `Line` cannot represent a split power | `alters.holder_slot` checked in 3.1 and against the immunity and power shapes; instance kinds {claim, liberty, immunity, powerLiberty, powerRecognition} with the source kind kept so `kinds: [power]` covers both halves; `dutyKind`, `libertyKind`, `rightPermission`, `free` over instances | 1.1, 1.2, 3.1, 4.1, 4.4, 9.1 | (ε), (φ) |
| Astra 6, Fable 5, round 3 item 4 — `envR D = envPrime D.soft` false; `E″` staged decisions twice; θ overclaims; μ ill-formed | `E″` = input vocabulary plus rights predicates, `E″′ = envPrime(correlate D)` adds soft's decisions once; `correlate_identity_top` as `correlate D = flattenTop D` with the vocabulary identities as corollaries; θ restricted to shape-compatible rows within the limits; μ on ternary `publish_about` under `nary@0`, `holder_slot: 2` | 1.5, 3.5, 4.2, 4.3, 9.1, 9.2, 10 | (θ), (μ) |
| Astra 7 — coupling enumeration per axis loses combinations; empty joint choice space | labels per connected component of each axis; joint assignments with an empty product contribute zero; `CouplingUnsatisfiable` | 3.3, 6.2, 8 | (χ), (ι) |
| Fable precision — `hp`'s type; `correlate_shape`'s order versus "document order"; `need not`; ι's candidates; κ's certified case; ο's eight on a hard line; `coherent_expands` | `hp` kept with `rightDerived_regulated`; 4.2 states `correlate_shape`'s order; releases rejected; four candidates per set; κ's certified case through a declared sufficient condition written as the `cond` atom; ο seven on a strict unswitchable line; `coherent_expands` kept as soft-norms 9.3's per-structure instance and the global form restated as `rights_coherent_expands_all` | 2.1, 4.2, 5.2, 9.3, 10 | (ι), (κ), (ο) |
| Plan questions (kept as drafted, both reviewers) | static power shadow with `power_shadows`; an uncited `excepted` is a finding; authored precedence or rank between rights' lines needs a citation | 13.6, 13.7, 7.2 | (ε), (κ), (μ) |

Statement-only verification of draft 2 (`manage-agents/rights-verify-astra.final.md`: FAIL, five corrections, no
unrelated redesign, no objection to the plan's three choices; applied in draft 3, no design change):

| Finding | Change in this draft | Where | Regression |
|---|---|---|---|
| Bar coverage — `bar_m` blocks a default obligation `+` line on `m`'s dual `r` (soft-norms 4.2 step 2), `blockedBy` excludes bars and the bar disjunct required a permission predicate, so `limitation_scope_sound` failed with no finding | the mechanism `bar` reaches every line with `barReach D N = some m` (the line's own right-derived permission predicate, or the permission dual of a default obligation `+` line); `blockedBy bar_m` across the dual pair folds into `bar`; fifth disjunct `∃ m, barReach D N = some m ∧ aimed_m`; `bar_blocks` gains the dual-pair conjunct; 4.3 names the dual-pair blocking; 4.7 separates the blocked default from the strict pair conflict | 4.3, 4.5, 4.7, 9.1, 9.2 | (ψ), (σ), (η) |
| Generated-name bounds — `soft__off__rights_fan_1__` plus a 64-byte party is 89 bytes, while 1.6 and 11 claimed every derived name bounded | a derived switch name may overflow and is rejected as `ResourceLimit: identifier <n> exceeds 64 bytes` when `E″′` is formed (4.1 step 5), never truncated or renamed; the guarantee restated for the generated names (≤ 19 bytes) and the party-free derived names (≤ 30); the `rights_bar` example removed, a bar node being hard and unswitchable | 1.6, 4.1, 8, 11 | (υ) |
| Fixture σ — its negative claim on `impart(person, idea)` has no holder object slot | σ's bar case on μ's ternary act under `nary@0` with `holder_slot: 2`; η's claim-line parenthetical points to ψ for the same reason | 10 | (σ), (η) |
| Condition grammar — strict text used the hyphen-only `name` for condition names against 3.2's underscore identifiers | `identifier` (the predicate grammar of 3.2) for condition names in 3.4, with the two tokens distinguished in words | 3.4 | round-trip suite (10, generated) |
| Fixture τ — `NarrowsAt(carveOut)` stays true where `diplomat` holds; only the guarded certification condition fails | τ restated: the activity is true, `narrowings_complete` and `limitation_scope_sound` are silent because their own-guard hypothesis fails, and `licensed_certified_sound` is inapplicable through its guarded activation hypothesis | 10 | (τ) |

Statement-only verification of draft 3 (`manage-agents/rights-verify1b-astra.final.md`: FAIL, three corrections, no
unrelated redesign, no objection to the plan's three choices; applied in draft 4, no design change):

| Finding | Change in this draft | Where | Regression |
|---|---|---|---|
| Bar paraphrases — 2.1 and the 7.1 report row promised a conflict for any obligation or outside permission on the act, while a default obligation `+` on `m`'s dual and a default outside permission on `m` are blocked by the bar's strict decision | the conflict claim restricted to selecting strict rules (a strict obligation on the act; a strict permission outside any right), default rules stated to give way; 7.1's row and 9.4's `rights-bar` output synchronised; 4.7 states the division; `bar_blocks`'s third conjunct widened to every default node of `T″` on `m` (either sign) or a default obligation `+` on `m`'s dual, right-derived or outside, so the blocking claim is theorem-backed | 2.1, 4.7, 7.1, 9.2, 9.4, 12 | (η) extended with the three default outside rules |
| Fixture τ — accepted the stronger `diplomat → limpack_N` although its own situation (`diplomat` true, `lim` false) refutes it, and named no premise under which the guarded target is entailed | τ rebuilt: limitation 29 declares the sufficient condition `diplomatic_immunity`, the carve-out carries that condition's atom beside `diplomat`, so the guarded target is entailed through the `Lim_D` sufficient premise (its label listed); situation A (activity true, own guard false, `lim` forced true) keeps the theorems' silence; situation B (condition false, `lim` false) is the admissible countermodel under which the stronger certificate is rejected; the unguarded `U_1° → limpack_N` noted as entailed but neither the target nor consulted | 10 | (τ) |
| Plan 1.2 — `limpack_N` omitted the source-kind filter `kind(N) ∈ kinds(L)` of 4.2, so a power-only limitation would narrow the other kinds of the same right | the filter added to the plan's `limpack_N` and `kinds` to its limitation definition (plan 1.1, 1.2); 1.3 names both filters where it says "in scope"; the `limPack` comment in 9.1 written over `inScope` | 1.3, 9.1; plan 1.1, 1.2 | (ε) (`kinds: [power]` matches neither a claim nor a liberty of the same right) |

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Item-1 specification from plan draft 2: the rights block, rights and incident lines with the shape table and holder slots, fan-out, limitations with per-act open predicates, named condition predicates and `Lim_D`, the bar under two readings, `E″`; the English table with the three limitation sentences, the bar sentences, the coupling sentence and the generated wordings; wire form, candidate labels, couplings, strict text, identity; `WellFormedRights`, `correlate`, `ValueRight`, projections, `Narrows` with the licensing table, the restricted `noDistinction`, the scoped bar; the conditional contract with `BaseAdmissible″`; readings and couplings; report, status text, diagnostics; every item-4 theorem as a statement in W1/soft conventions; fixtures α to π; limits; review checklist; resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-28 | Draft 2 | Applied the converged rights-spec statement review (FIX, round 3), no design change: `limpack_N` as the first disjunct and certification target of `limitation_scope_sound`; `blockedBy` at soft-norms 4.2 step 2's width with same-effect blocking licensed by construction and `same_effect_delivered`, the bar's surfaces folded into `bar`; `owes_outcome` with membership and typing; every mechanism condition outcome-substituted on `B`; `rightDerived_regulated`; generated names by index under reserved prefixes (1.6); `alters.holder_slot`; instance kinds with the source kind kept; `E″`/`E″′` staging and `correlate_identity_top` as `correlate D = flattenTop D`; couplings per component with `CouplingUnsatisfiable`; releases rejected; fixtures β, ε, θ, ι, κ, μ, ν, ο corrected and ρ to χ added; response table (14). Spec only. |
| 2026-09-28 | Draft 3 | Applied the statement-only verification of draft 2 (FAIL, five corrections), no design change: the bar's reach across the dual pair (`barReach`; the mechanism `bar` covers a default obligation `+` line on `m`'s dual; `limitation_scope_sound`'s fifth disjunct and `bar_blocks` extended; 4.3 and 4.7 state the dual-pair blocking); derived switch names may overflow the 64-byte identifier limit and are rejected as `ResourceLimit`, the 1.6 and 11 guarantees corrected; `identifier` for condition names in the strict-text grammar; fixtures σ (ternary act for the bar case), η (parenthetical) and τ (activity versus guarded certification condition) corrected, υ extended, ψ added; second table in 14. Spec only. |
| 2026-09-28 | Draft 4 | Applied the statement-only verification of draft 3 (FAIL, three corrections), no design change: the bar paraphrase (2.1) and report row (7.1) restrict the conflict claim to selecting strict rules and state that default rules on `m` or its dual give way; `bar_blocks`'s third conjunct widened to every default node of `T″` (right-derived or outside) and 4.7, 9.4 and 12 synchronised; fixture η extended with default outside rules; fixture τ rebuilt over a declared sufficient condition of limitation 29 whose `Lim_D` premise entails the guarded target, with the stronger unguarded certificate rejected by an admissible countermodel; 1.3 and the `limPack` comment name the source-kind filter (the plan's `limpack_N` corrected); third table in 14. Spec only. |
