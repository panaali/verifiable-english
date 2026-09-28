# Rights and claim-rights in VE: plan (`rights@0`)

> Status: planning draft 3 (2026-09-28), North Star rank 2, transcribing the converged Astra/Fable design debate
> (`manage-agents/debates/design-rights/{astra,fable}.md`, CONVERGED after round 3): Astra 1–6, Fable 1–12, the
> coupling narrowings, the scoped Art. 30 theorem, the restricted invariance theorem, the distinct
> conflict/blocking/weighing classifications, and one packed `lim` carve-out with six author slots; and applying the
> converged statement review of rights.md draft 1 (`manage-agents/debates/rights-spec/{astra,fable}.md`, FIX,
> CONVERGED after round 3; section 8's second table), no design change. The item-1 statement spec
> [rights.md](rights.md) draft 2 is written from this draft and goes to one statement-only Astra + Fable
> verification round, which checks definitions, paraphrases, theorem hypotheses and fixtures before items 2–4 and
> before any implementation starts; a new draft alone opens nothing. Inputs: the pinned UDHR (`manage-agents/pilots/udhr/source/udhr.md`, SHA-256
> `d6495201…d3a`, cited "Art. n") and its pilot `run-20260927T1800Z` (116 units; 70 unformalised units blocked by
> norms/rights; 14 open terms; 5 unelaborated reading inventories; zero substantive checked bytes); [norms.md](norms.md)
> (W1, merged); [soft-norms.md](soft-norms.md) (item-1 spec, unmerged); [document.md](document.md) (W2);
> [VISION.md](../../VISION.md). Nothing here changes a frozen contract, a `norms@0` or `soft-norms@0` hash, a W1 or
> soft theorem statement or a checker function. Theorems and fixtures below are obligations, not results. Effort
> figures are the draft-1 estimates, unchanged.

## 0. Problem and stance

W1 writes duties from the bearer's side and rejects "is entitled to" (norms.md 2). The Declaration writes from the
holder's side: "Everyone has the right to X", "No one shall be subjected to X", with the duty-bearer unnamed, the duty's
polarity (do not interfere, or provide) unstated, its force ("shall") unstated and the deciding standard ("arbitrary",
"fair", "degrading") open. The pilot audit warns against both cheap fixes: an entitlement reduced to a permission, and
every "shall" read as a strict duty on an invented bearer.

Stance: **a right is the holder-side view of duties and permissions; it adds no deontic primitive.** A right block names
a holder sort, a holder guard `H_R`, and Hohfeldian *incident lines*, each an ordinary W1 rule or soft default rule: a
**claim** is a duty on a bearer with the holder in an object slot; a **liberty** is a permission with the holder as
subject; an **immunity** is a prohibition on a bearer's act that would alter the holder's status; a **power** is two
explicit rules, a liberty over a constitutive act plus a claim that bearers recognise its result (the static shadow of
power/liability; an act changing which norms hold is stage-3 material). Correlativity is by construction: the
holder's claim and the bearer's duty are one rule read from two ends, so "who owes what to whom here" is a projection
of which lines select, with the completed outcome a corollary. `rights@0` elaborates by `correlate` into a
`soft-norms@0` document over the author's vocabulary plus fresh open *limitation*, *condition* and *bar* predicates.
What that buys, exactly (the soft-norms 0 pattern): W1's and the soft route's definitions and per-structure theorems
are reused as lemmas; the soft route's document-wide theorems are **restated** with one extra base premise, the
declared limitation conditions `Lim_D`, and every rights result is conditional on `Coh_T` and `Lim_D`. Draft 1's
"adds no background premise" was false as written (Astra 1): a limitation's necessary and sufficient conditions are
premises, exactly as a soft exception's are (soft-norms 6.1), and they are regenerated, identity-bound, admitted as
base formulas and checked for vacuity. The ambiguity the source leaves (bearer, polarity, incident, force) lives in
per-unit W2 reading sets; a document-wide uniform reading is an explicit, attributed **coupling narrowing** that every
dependent certificate names, never a checker default (Astra 4). Legal standards are open terms with the W2 schema,
never predicates the checker decides.

## 1. Semantics

### 1.1 A rights document

```text
environment `rights` block (identity-bound like `regulated` and `soft`):
  holder sorts H, bearer sorts B ⊆ sorts(E)   "person"; "state", "person", "group"
  protected ⊆ base predicates                the Art. 2 list (race, colour, sex, language, religion, opinion, …)
  alters : act key ↦ {holder_slot, status, recognition}
                                             acts that change a holder's status (marry, deprive of nationality):
                                             holder_slot the argument index of the affected holder (a holder sort),
                                             status a base predicate over that sort, recognition the declared
                                             recognition act for a power's second rule (required where a power uses
                                             the act, null otherwise)
right R       := stable name; holder sort h ∈ H; holder guard H_R(h) (Art. 11(1) "charged with a penal offence");
                 incident lines; display number = document order
incident line := source kind ∈ {claim, liberty, immunity, power}; one W1/soft rule N whose shape matches the kind;
                 it elaborates to line instances of instance kind ∈ {claim, liberty, immunity, powerLiberty,
                 powerRecognition} (a power two, a fan-out one per bearer sort), each keeping the source kind so a
                 limitation's `kinds: [power]` covers both halves; holder slot := for claims, immunities and
                 powerRecognition the unique object slot of sort h (HolderSlotAmbiguous otherwise), for liberties
                 and powerLiberty the subject slot (IncidentShape otherwise); an immunity's or power's holder slot
                 must equal its act's declared holder_slot
limitation L  := stable name; scope ⊆ rights or `all`; per act a in scope one fresh open base predicate lim_{L,a}
                 with a's sorts (rights__lim__<k>, k its position in the canonical order; rights.md 1.6) carrying
                 the full W2 open-term schema: decider (or `unstated`), conditions (named open predicates
                 cond_{L,c,a} with a's sorts, rights__cond__<k>, and a role necessary | sufficient, each
                 verbalised), factors (English phrases, no premise), and an English verbalisation of lim_{L,a}
                 itself so an adopter can write a rule that entails it (Fable 12)
bar           := an Art. 30 unit: reading set {rule, query}; under either, per right-derived permission predicate m
                 one fresh open predicate aimed_m (rights__bar__<k>, "aimed at the destruction of a right",
                 decider or `unstated`); under the rule reading also one hard rule per m, named rights-bar-<k> (1.2)
```

Shapes: a **claim** line's subject has a bearer sort, its holder slot is an object, its predicate is an obligation
(`must`, `+`; `should` for a default line) or a permission of sign `−` (`must not`, `should not`). A **liberty**
line's subject is the holder, its predicate a permission of sign `+` (`may`, `generally may`; a release `need not`
fits no shape and is rejected). An **immunity** is a claim of sign `−` on an `alters` act whose holder slot is the
act's declared `holder_slot` (Art. 15(2), 17(2): `deprive_of_nationality(state, person)`, slot 1). A **power** is a
liberty on an `alters` act whose `holder_slot` is the subject slot plus one claim that every bearer recognise the
result through the act's declared recognition predicate, which the entry must then declare (Art. 15(1), 16(1),
23(4)). `IncidentShape` rejects a mismatch; labels carry no semantics beyond the rules they type. `No one` or
`Everyone` as the subject of a line fans out into one rule per declared bearer sort, named `rights-fan-<k>` and
rendered with its source line and sort, each on the regulated predicate declared for that bearer sort and the line's
act phrase (distinct acts by W1's act identity; `FanOutUndeclared` when a bearer sort has none). Every generated
rule or predicate name is indexed into a canonical order under the reserved prefixes `rights-` and `rights__`
(rights.md 1.6): W1's rule grammar admits no `_`, identifiers are capped at 64 bytes, and delimiter maps over
authored names are not injective, so names are never built from authored names.

### 1.2 Elaboration `correlate(D) = (E″, T″, Lim_D)` and the direct semantics

`T″` is a soft tree (soft-norms 1): every line's rule with three changes and three additions.

```text
guard of N in T″      := G_N ∧ H_R(x_slot)     the holder guard conjoined at the line's holder slot (object for claims
                                               and immunities, subject for liberties); omitted when H_R is
                                               syntactically ⊤, so unguarded rights elaborate byte for byte (Astra 3)
carve-outs of N in T″ := U_N ++ [limpack_N]    limpack_N := ⋁_{L : R ∈ scope(L)} lim_{L,a_N}(x̄), one packed carve-out
                                               (omitted when no limitation is in scope); it occupies one of W1's eight
                                               slots and the soft derived carve-out another, so a right-derived line
                                               keeps six author carve-outs (Fable 11)
mode, exception, rank, alterable, hard         as written on the line (a default line is a soft rule, unchanged)
power                 := its liberty node and its recognition claim node, both with H_R and limpack
fan-out               := one node per bearer sort, names rights-fan-<k>
bar (rule reading)    := per right-derived permission predicate m: node bar_m (rights-bar-<k>), ¬m(x̄) if aimed_m(x̄),
                         strict, no switch, `hard: true`, over := every right-derived positive node on m (Fable 1)
node order of T″      := the line instances in instance order, then the norm units outside rights, then the bars
precedence of T″      := the author's `over` edges among lines, plus the bar's edges; nothing else is derived
E″                    := E + {lim_{L,a}} + {cond_{L,c,a}} + {aimed_m}, the soft input vocabulary of T″, regenerated
                         at every site, never from the wire; soft's decision predicates are added once, by soften:
                         E″′ := envPrime(correlate D) = E″ + decisions(T″) is the vocabulary of T″′ = soften(T″)
Lim_D                 := per limitation L, act a in scope and condition c:  necessary: ∀x̄. lim_{L,a}(x̄) → cond_{L,c,a}(x̄)
                         sufficient: ∀x̄. cond_{L,c,a}(x̄) → lim_{L,a}(x̄);  label rights:limitation:<L>:<act key>:<role>:<c>;
                         the `rights` Background slot after `soft`; Background_base″ := Background_base′(T″) ++ Lim_D;
                         BaseAdmissible″ D B := BaseAdmissible′ (correlate D) B ∧ Sat B Lim_D
```

With no limitation, power, fan-out or bar, `E″ = E` and `T″` is the lines with the `H_R` conjunct only
(`correlate_identity`); when every `H_R` is `⊤` as well, `correlate D` is byte for byte the soft document that lists
the lines before the outside rules (`correlate_identity_top`: `correlate D = flattenTop D`), so `E″′` is that
document's `E′` and decisions are generated exactly once. `ValueRight` is `ValueSoft` (soft-norms 4.2) read
directly on the lines, with step 0 `live_N := G_N ∧ H_R ∧ ¬⋁U_N ∧ ¬limpack_N ∧ ¬switch_N ∧ [default] ¬excepted_N`
and, under the rule reading of the bar, `barred_N := aimed_m(x̄)` for every right-derived positive line on `m`
counted as a strict decision `N^s_m` and as a further condition on `selects_N`; `SoftNorms.ValueSoft (correlate D) =
ValueRight D` by unfolding (`correlate_faithful`). A carve-out never grants anything: where `limpack_N` holds the line
is silent and "the other rules and the default then decide" (norms.md 10.1(i,w); Astra 2).

Right-level answers are projections of **which lines select**, attributed to their right and line, with the completed
outcome a corollary (Fable 2, Astra 3):

```text
owes_N(v̄)(S)     := N a claim, immunity or powerRecognition instance and selects″_N holds at v̄ (bearer v̄_0, holder v̄_slot)
free_N(v̄)(S)     := N a liberty or powerLiberty instance and selects″_N holds at v̄ (holder v̄_0)
rightsOf(h, S)   := {(R, N, v̄) : N a line of R, v̄ typed, v̄_slot(N) = h, selects″_N at v̄}
dutiesOf(b, S)   := {(R, N, v̄) : N a duty line of R, v̄ typed, v̄_0 = b, selects″_N at v̄}
owes_outcome     := N a line instance of D ∧ v̄ typed ∧ owes_N(v̄) ∧ no opposite-sign rule on p_N selects at v̄
                    →  ValueSoft_{p_N}(S, v̄) = some sign(N)
```

The projections are of selection: where a strict rule of the same effect blocks a default line (1.4) the line is
absent from `rightsOf`/`dutiesOf` although its effect holds, and the report says "effect delivered by strict rule
M" beside the holder (`same_effect_delivered`: a strict decision of the line's sign, with no strict decision of the
opposite sign, fixes the outcome).

`projections_agree`: for a duty line `N` of `R`, `(R, N, v̄) ∈ rightsOf(v̄_slot)` iff `(R, N, v̄) ∈ dutiesOf(v̄_0)`, the
same `R`, `N` and `v̄` on both sides. It is definitional, and that is the content: a claim and its duty are one rule.
Under a deny completion `¬O_m(v̄)` holds with no claim line at all; that is an outcome, not a duty, and `owes` never
reports it (draft 1's `owes := ¬O_{a_permitted}` withdrawn). The checker never *infers* a positive duty from a negative
one, a bearer from a holder, or a claim from a liberty; those are readings.

### 1.3 Readings (translation mode): per-unit base, couplings as narrowings

Four axes stay open where the source leaves them (VISION.md 3): **bearer** (every state; the state of jurisdiction or
nationality; every person; every party; the community), **polarity** (negative: do not deprive or interfere;
positive: secure, provide, protect against third parties; both), **incident** (claim; liberty; liberty plus
protective claim; power) and **force** ({strict, default} for every "shall" and "has the right to", soft-norms 2.2;
Fable 3). A candidate is a complete right block with elaborated lines and a distinguishing checked situation; a
candidate without lines is an inventory and counts nothing (North Star). The base is **one reading set per unit**
with candidates labelled on each open axis (`labels: {bearer, polarity, incident, force}`); a cited narrowing closes
an axis the text fixes ("protection by society and the State", Art. 16(3): bearer and positive; "No one shall be
subjected to", Art. 5, 9: negative; "by the competent national tribunals", Art. 8: positive, the state).

Sharing a choice across articles removes mixed combinations, so it is never the base (Astra 4). A **coupling** is a
new attributed W2 narrowing kind, gated under `rights@0` (`couplings` list beside `narrowings`, existing narrowing
identities unchanged; Fable 7): it names an axis, the reading sets it couples and the source units it cites, and it
requires every coupled set to take the same label on that axis. Couplings on one axis whose set lists overlap act
as one connected component, and the enumeration assigns one label per component of each axis, not one per axis;
a joint assignment for which some set has no consistent candidate contributes nothing, and a family of couplings
admitting no complete choice is rejected at admission (`CouplingUnsatisfiable`), never counted as a vacuous verdict
(rights.md 6.2). A certificate obtained under a coupling lists `coupling:<id>` in `conditional_on`, and its paraphrase says "reading every
article with the same bearer / polarity / force". The pilot applies three, each citing the Preamble (bearer: "every
individual and every organ of society … Member States have pledged"; polarity: "to secure their universal and
effective recognition and observance"; force: "a common standard of achievement"); the citation records the
interpretation's rationale, it does not prove that mixed readings are impossible, and the report says so. Uncoupled,
the choices are the independent product and a conclusion depending on more than 64 is UNKNOWN with the units named.
Worked example, Art. 3 and 22 (the Art. 25 resource exception of draft 1 is withdrawn: Art. 25(1) has no resources
clause, Art. 22 does; Astra 4):

```text
Right 3. Every person has the right to life.
  Claim of right 3 (rs_u022: bearer). Every state must not deprive each person of life.
  Claim of right 3 (rs_u022: polarity positive). Every state must protect each person within its jurisdiction
    against deprivation of life.                             ("within its jurisdiction" open; separating situation: a
                                                              state that fails to protect but does not deprive)
Art. 5: Claim of right 5. No one may subject each person to treatment that is torture or is cruel, inhuman or
  degrading.    (fan-out over the bearer sorts; `degrading`, `cruel`, `inhuman` open; decider unstated)
Art. 22: Claim of right 22 (default, narrowing n22 citing "in accordance with the organization and resources of
  each State"). Every state should secure for each person social security. Claim of right 22 is excepted only when
  securing it exceeds the organisation and resources of that state.   (necessary condition of the exception; open)
Art. 25: Claim of right 25 (rs_u091: force {strict, default}). Every state must | should secure for each person a
  standard of living that is adequate …   (`adequate` open; no source clause narrows the force; both candidates
  elaborated; conclusions per choice)
```

### 1.4 Limitations, the bar and non-discrimination (Art. 29, 30, 2)

**Art. 29(2)** is one limitation `L29`, scope `all`: `lim_{L29,a}` is open, decider unstated (a narrowing may cite
Art. 8's tribunals), with two **necessary** conditions (Astra 1, round 3): `determined_by_law` and
`solely_for_permitted_purpose`, the latter an open predicate whose schema verbalises the permitted purposes ("securing
due recognition and respect for the rights and freedoms of others; meeting the just requirements of morality, public
order and the general welfare in a democratic society", `just` and `democratic society` open), and with those same
considerations additionally as factors. `Lim_D` therefore contains, per act `a`, `∀x̄. lim_{L29,a}(x̄) →
determined_by_law_a(x̄)` and `∀x̄. lim_{L29,a}(x̄) → solely_for_permitted_purpose_a(x̄)`: the checker enforces the
implications and decides neither predicate. English, the soft-norms three-sentence pattern:

```text
Limitation 29 (on every right). A right in this document is limited in a situation only where limitation 29 holds.
Limitation 29 holds only where the limitation is determined by law.
Limitation 29 holds only where the limitation is solely for a permitted purpose.
Limitation 29 takes account of the rights and freedoms of others, the just requirements of morality, public order
  and the general welfare in a democratic society.
```

The word **"only"** in the first sentence is the executable check `limitationScope`, now over a defined relation
`Narrows` (Astra 2, Fable 6): a *narrowing* of a right-derived line `N` in scope of `L` is any mechanism of `T″′ =
soften(T″)` that stops `N` selecting where its own guard `G_N ∧ H_R` holds: an author carve-out, an exception
subtree, the packed `lim` carve-out, the soft exception `excepted_N`, a switch `off_{N,π}`, a blocking strict rule
(soft-norms 4.2 step 2 at its full width: a strict rule selecting on the line's predicate with either sign, or
against its effect across the dual pair), a dominating ranked rule, or the bar (whose `over` edges and blocking are
one mechanism, attributed to Art. 30). Licensed: the `lim` carve-out and the bar (by construction); a source-cited
carve-out, exception, exception term or switch (Art. 14(2), 29(3), 22); a carve-out or exception whose condition is
certified to entail the packed `limpack_N` (some limitation covering the line) over `Background_base″`; a default
line's `excepted_N` whose `necessary` conditions are certified to entail `limpack_N`; blocking by a strict rule of
the **same effect**, inside or outside rights, which silences the default line while delivering its effect and is
licensed by construction, reported "effect delivered by strict rule M" (only where no strict rule of the opposite
sign decides there; otherwise W1's conflict is reported), never a finding and never a collision; blocking or
dominance by **another right's line of the opposite effect**, which is a same-act collision and is classified under
1.5, never a limitation. Everything else is the finding `UnlicensedLimitation: <mechanism> of rule <n> on right <R>`
(a report line, never an admission error; Fable 5). `limitation_scope_sound`: with no finding, a line in scope that
does not select where its own guard holds is at a point where some limitation covering it holds (`limpack_N`, not
one named limitation: under two limitations with only the second true the line is rightly silent), a cited narrowing
is active, another right's line collides, a strict rule of its own effect selects, or the bar applies; every
mechanism condition is read through W1's outcome substitution on the base structure, as the guard and selection
hypotheses are. The check bites when an adopter's norms
document is composed with the Declaration: "does this policy narrow a right the Declaration does not license?" is
answered structurally, and lawfulness stays with the decider: a certified entailment certifies a declared condition,
never lawfulness. **Art. 14(2)** is the pilot's `rs_u052`: {carve-out on every line of right 14 ("right
inapplicable"), on the claim line only ("invocation barred")}, `genuine` open, cited. **Art. 29(3)** is a second
limitation on liberty lines, `contrary_to_un_purposes`, reading set {liberty lines, all lines} (`rs_u112`).
**Art. 29(1)** ("duties to the community") names no act and is not a W1 rule; it stays UNFORMALISED with reason
`norms` (Fable 10). **Art. 30** is `rs_u114` = {rule reading: the hard bar `bar_m` with precedence over every
right-derived liberty on `m`; query reading: no rule, and per `m` the checked entailment `∀x̄. aimed_m(x̄) →
¬m(x̄)` or a countermodel exhibiting the liberty}. Under the rule reading `bar_blocks` is a theorem of `correlate`
scoped to its own output: no right-derived permission line selects where `aimed_m` holds and the bar decides `¬m`
there; where every positive rule on `m` is right-derived, `m` is false there (`bar_value`). Composition assumptions
are stated, not assumed away: an adopter's positive rule on `m` and a strict obligation on the same act (a claim
line or an adopter's rule, soft-norms :385–386's dual pair) stay under W1's ordinary intra-predicate and pair
conflict checks and are reported CONFLICT, not silently resolved (Astra round 3). **Art. 2 and 7** ("without
distinction of any kind") are the executable check `noDistinction`: per right-derived predicate `p`, whether a
protected predicate occurs in `cone(p)`; where none does, `no_distinction_sound` is exactly soft-norms
`cone_independent` with `Q := protected`: every outcome on `p` is invariant under the protected predicates. The
Declaration itself distinguishes (Art. 16(1) "men and women of full age", 25(2) "motherhood and childhood"), so a
hit is a **finding**, `distinction_hits`, cited (the set `E` of lines carrying a source-cited distinction) or
uncited (Fable 5); the theorem is restricted to predicates none of whose rules is in `E` and whose cone is
protected-free, the report lists `E` with citations beside the result and the sentence "outcomes of the listed lines
may depend on the protected predicates", and no unrestricted invariance claim is made (Astra round 3). Beside every
`no_distinction` and `limitation_scope` result the report states: the theorem says nothing about whether the decider
of `lim`, of an exception, or of `arbitrary` or `degrading` discriminates; those tables are open (Fable 4, Astra 6).
Substantive equality stays the pilot's open term `equal_before_law`.

### 1.5 Same-act collisions, static incidents, other limits

Positive social rights (Art. 22, 25(1), 26(1)) are **not** automatically default lines (Astra 4): force is the
per-unit READINGS set {strict, default}; Art. 22's "in accordance with the organization and resources of each State"
and Art. 26(1) "shall be made generally available" are cited narrowings to `default` with the clause as the
exception's `necessary` condition or factor; Art. 25(1) keeps both candidates. The Declaration ranks nothing.
Collisions between right lines are same-act (soft-norms 4.5) and are classified exactly as the reused semantics
classifies them (Astra 5): **strict–strict** is CONFLICT with a witness situation (W1); **strict–default** is
blocking, the default line gives way (`hard_over_soft`) and the report shows it under the default line; **default–
default** is a colliding pair of `CP(T″)`, RANK-RESOLVED only under an adopter's cited ranking, else DISJOINT by
certificate, a WEIGHING POINT with a witness, or UNKNOWN; Art. 29(2)'s "rights and freedoms of others" names the
weighing points. Art. 19's liberty to impart and Art. 12's claim against attacks on honour collide only if both
regulate one declared act; the status text says "among rules on the same act". Powers and immunities are static and
the representation is explicitly incomplete (Astra 6): the checker knows that marrying is permitted and that its
result must be recognised, and that an arbitrary deprivation of nationality is forbidden; it does not know what
duties follow a marriage or whether a forbidden deprivation has effect, and the residual line `power_shadows` says
"recognition required; later effects not modelled" per power and "prohibition on the act; its effect on status not
modelled" per immunity (stage-3 trigger: a recorded inference that needs the change, converged rule item 3). No
fulfilment or time: `violation := required ∧ ¬done` and `breach := ¬permitted ∧ done` are W3 above the norms.
"Peoples" and "the family" need declared sorts or stay open. Preamble "have pledged" is W2 attribution. Whether a
right is respected in the world is never certified.

## 2. English wordings (one reading each; rejected as today when `rights@0` is off)

| Wording | The one reading (the IDE's paraphrase); formal effect |
|---|---|
| `Right n. Every <holder>[ that C] has the right to <phrase>.` | Names the holder and the right; requires or permits nothing by itself: the right means exactly its lines (`RightWithoutIncident` if none). Every line of this right applies only to holders that C. Right `R`, `H_R`. |
| `Claim of right n. Every <bearer> must <act> each <holder> …` / `must not …` / `should …` / `should not …` `[, if C][, unless U]` | The bearer owes this to the holder in every situation of the kind (a `should` line: unless this line's exception applies there; <decider> decides). Soft-norms 2.1 wordings apply. A W1/soft rule of kind `claim`; `H_R` conjoined at the holder slot. |
| `Claim of right n. No one may <act> each <holder> …` / `Everyone must <act> each <holder> …` | Every bearer of every declared bearer sort owes this; one rule per bearer sort. Fan-out. |
| `Liberty of right n. Every <holder> may <act> …` / `generally may` | The holder is permitted; no duty on anyone follows from this line. Permission `+`, kind `liberty`; `H_R` at the subject. |
| `Immunity of right n. Every <bearer> must not <alter-act> each <holder> …` | The bearer must not change the holder's status this way; whether an attempted change has effect is not modelled. Kind `immunity` (Fable 9). |
| `Power of right n.` + one liberty sentence + one `… must recognise …` claim | The holder may perform the act and every bearer must recognise its result; later effects are not modelled. Two rules. |
| `Right n includes:` + lines | Adds lines to the named right ("this right includes", Art. 18, 19). |
| `Limitation m (on every right \| on rights a and b). A right in this document is limited in a situation only where limitation m holds.` | Every line in scope gives way where the limitation holds, and the other rules and the default then decide; no other mechanism narrows a right in scope unless written here or in another limitation covering the line, cited, certified to entail some limitation covering the line, or structural (another right's line collides, a strict rule of the same effect decides, or the bar applies); <decider> decides whether it holds. `L`, `lim_{L,a}`, `limitationScope`. |
| `Limitation m holds only where <condition>.` / `Limitation m holds where <condition>.` | The condition is necessary / sufficient for the limitation; the checker enforces the implication and decides neither side. `cond_{L,c,a}`, a premise in `Lim_D`. |
| `Limitation m takes account of <consideration>[, <consideration>]*.` | These considerations bear on whether the limitation holds; none is by itself decisive. `factors`, no premise. |
| `Nothing in this document gives any bearer a right to <act> aimed at the destruction of a right.` (Art. 30, rule reading) | No liberty in this document permits such an act; whether an act is so aimed is decided by <decider>; an obligation or an outside permission for the act is reported as a conflict, not overridden. `bar_m` with precedence. |
| `Reading every right in this document with the same <bearer \| polarity \| force>, because <cited units>.` | A coupling: the named axis is chosen once for every listed right; every result under it says so. `coupling:<id>`. |
| `No <holder> shall be <passive act>.` (input only) | Not a line: the bearer is missing. The IDE offers a `Claim of right n` per bearer sort or the `No one may` fan-out; translation records the set. |

Input synonyms: `is entitled to` → `has the right to`; `freedom of <noun>` becomes a liberty only through a declared act
phrase. `shall` is not a norm word: in translation a "shall" unit is a READINGS set {strict claim, default claim}
(soft-norms 2.2). The reader's checklist adds, per right: the holder and its guard; each bearer and what it owes in
the example situation ("Texas owes Ann: not to deprive her of life; nobody owes Ann protection under this reading");
each applicable limitation, its conditions and its decider; every narrowing mechanism and whether it is licensed; for
a reading set, the separating situation; for a coupling, the sentence "reading every article with the same …".

## 3. What the checker certifies and what stays open

**Certified** (certificate or theorem bound to `environment_id`, the rights document hash, the reading choice and
the active couplings): (1) `correlate_wellFormed`, `correlate_identity`, `correlate_faithful`; (2)
`projections_agree` and `owes_outcome`; (3) conflict-freedom of `T″` under `BaseAdmissible″` by the unchanged W1/soft
machinery, or a witness situation, with every same-act collision between right lines classified conflict / blocking
/ weighing (1.5); (4) `limitation_scope_sound`: no finding means every narrowing of a right in scope is some
covering limitation (the pack), a cited narrowing, a collision with another right, a strict rule of the same effect,
or the bar; a certified case is a mechanism condition certified to entail the packed limitation predicate, never a
certified lawful limitation; (5) `no_distinction_sound`, restricted to
predicates with a protected-free cone, with `E` listed; (6) `bar_blocks` and `bar_value` under the rule reading, or
the per-`m` entailment or countermodel under the query reading; (7) restated route theorems `rights_route_acceptance`
and `rights_route_countermodel` with `BaseAdmissible″`, and wire theorems in the norms.md 11.4 shape; certificates
stale under any change to a line, holder guard, scope, limitation schema, condition, protected list, reading choice
or coupling.

**Open, never certified:** every legal standard (`arbitrary`, `fair`, `degrading`, `adequate`, `genuine`, `effective
remedy`, `independent and impartial`, `determined by law`, `solely for a permitted purpose`, `aimed at destruction`);
the limitation and condition tables themselves and whether their deciders, or the deciders of any exception or
standard, discriminate; who bears the duty, whether it is positive and whether it is strict, where the source is
silent; that a coupling is the right interpretation; the weighing between rights; whether a limitation is lawful in
fact; the effect of a power or of a forbidden status change; whether any duty is fulfilled.

## 4. Lean obligations (`lean/VE/Rights/*`; frozen `Norms/*`, `Route/*` untouched; soft names as in soft-norms.md 9)

```lean
namespace VE.Rights   -- RightsDoc = SoftDoc + rights block, rights (lines), limitations, bars, couplings are W2-side
def WellFormedRights (D : RightsDoc) : Bool          -- shapes, holder slots, scopes, protected/alters typing, fan-out
def correlate (D : RightsDoc) : SoftNorms.SoftDoc    -- H_R conjuncts, limpack carve-outs, power/fan-out nodes, bars
def limPremises (D : RightsDoc) : List VE.Formula    -- Lim_D, regenerated
def BaseAdmissibleR (D) (B : VE.Structure) : Prop := SoftNorms.BaseAdmissible' (correlate D) B ∧ Sat B (limPremises D)
def ValueRight (D) (r : Regulated) (S : VE.Structure) (vs : List S.Carrier) : Option Bool
def SelectsR (D) (S) (ρ) (N : Line) : Prop           -- SoftNorms.SelectsSoftD (correlate D) S ρ (fuel) (nodeOf D N)
def limitationScope (D) (certs : List (Option Certificate)) : List Finding     def noDistinction (D) : List Finding

theorem correlate_wellFormed (D) (h : WellFormedRights D = true) : SoftNorms.WellFormedSoft (correlate D) = true
def flattenTop (D : RightsDoc) : SoftNorms.SoftDoc :=   -- the lines as written before the outside rules, nothing else
  { D.soft with T := { D.soft.T with nodes := (linesOf D).map (·.2.node) ++ D.soft.T.nodes } }
theorem correlate_identity (D) (h) (hn : D.limits = [] ∧ noPowers D ∧ noFanOut D ∧ D.bars = []) :
  (correlate D).E = D.soft.E ∧
  (correlate D).T.nodes = (linesOf D).map (fun RN => { RN.2.node with guard := holderConj D RN.2 RN.2.node.guard }) ++ D.soft.T.nodes
theorem correlate_identity_top (D) (h) (hn) (ht : ∀ R ∈ D.rs, R.guard = .top) : correlate D = flattenTop D
theorem correlate_identity_top_env (D) (h) (hn) (ht) :
  envR D = D.soft.E ∧ SoftNorms.envPrime (correlate D) = SoftNorms.envPrime (flattenTop D)   -- by rewriting
theorem correlate_faithful (D) (h) (r) (hr) (S) (vs) : SoftNorms.ValueSoft (correlate D) r S vs = ValueRight D r S vs
theorem projections_agree (D) (h) (S) (R) (N) (vs) (hN : (R, N) ∈ linesOf D) (hk : dutyKind N) (typed) :
  (R, N, vs) ∈ rightsOf D S (vs.get (holderSlot D N)) ↔ (R, N, vs) ∈ dutiesOf D S vs.head
theorem owes_outcome (D) (h) (S) (R) (N) (vs) (hN : (R, N) ∈ linesOf D) (typed) (hs : SelectsR D S (tupleVal vs) N)
    (hno : ¬ SoftNorms.DecidesSoftD (correlate D) S (tupleVal vs) N.node.pred (!N.node.sign)) :
  SoftNorms.ValueSoft (correlate D) (regOf D N.node.pred) S vs = some N.node.sign
theorem same_effect_delivered (D) (h) (S) (R) (N) (vs) (hN : (R, N) ∈ linesOf D) (typed)
    (hsd : SoftNorms.StrictDecidesD (correlate D) S (tupleVal vs) N.node.pred N.node.sign)
    (hno : ¬ SoftNorms.StrictDecidesD (correlate D) S (tupleVal vs) N.node.pred (!N.node.sign)) :
  SoftNorms.ValueSoft (correlate D) (regOf D N.node.pred) S vs = some N.node.sign
theorem bar_blocks (D) (h) (hb : ruleReading D) (m) (hm : rightPermission D m) (S) (ρ) (ha : (aimedF D m).denote S ρ) :
  (∀ N ∈ rightPositiveOn D m, ¬ SelectsR D S ρ N) ∧ SoftNorms.StrictDecidesD (correlate D) S ρ m false
theorem bar_value (D) (h) (hb) (m) (hm) (honly : ∀ N ∈ positiveOn (correlate D) m, rightDerived D N) (S) (vs)
    (ha : (aimedF D m).denote S (tupleVal vs)) : SoftNorms.ValueSoft (correlate D) (regOf D m) S vs = some false
theorem limitation_scope_sound (D) (h) (certs) (hc : limitationScope D certs = []) (L) (hL : L ∈ D.limits) (R) (N)
    (hN : (R, N) ∈ linesOf D) (hs : inScope D L R N)      -- the witness that limpack_N is non-empty
    (B) (hB : BaseAdmissibleR D B) (vs) (typed)
    (hown : (ownGuard D N)°.denote B (tupleVal vs)) (hns : ¬ (selectsR D N)°.denote B (tupleVal vs)) :
  (limPack D N).denote B (tupleVal vs)                                                       -- some limitation in scope holds
  ∨ (∃ n ∈ narrowings D N, cited D N n ∧ (condF D N n)°.denote B (tupleVal vs))              -- a cited mechanism is active
  ∨ (∃ n ∈ narrowings D N, rightCollision D N n ∧ (condF D N n)°.denote B (tupleVal vs))     -- another right's line collides
  ∨ (∃ M, sameEffectStrict D N M ∧ (condF D N (.blockedBy M))°.denote B (tupleVal vs))        -- a same-effect strict rule selects
  ∨ (ruleReading D ∧ rightPermission D N.node.pred ∧ (aimedF D N.node.pred).denote B (tupleVal vs))  -- the bar
theorem licensed_certified_sound (D) (h) (N) (n) (c)
    (acc : checkCertificate (envAt (soften (correlate D)) 0) (backgroundBaseR D)
             (bindAll (sortsOf D N) (.imp (condF D N n)° (limPack D N))) c = true)
    (B) (hB : BaseAdmissibleR D B) (vs) (typed) (hact : (condF D N n)°.denote B (tupleVal vs)) :
  (limPack D N).denote B (tupleVal vs)
theorem rightDerived_regulated (D) (h) (p) (hp : rightDerived D p) : p ∈ VE.Norms.regulatedNames (correlate D).T
theorem no_distinction_sound (D) (h) (p) (hp : rightDerived D p)
    (hcone : ∀ q ∈ SoftNorms.cone (correlate D) p, q ∉ D.rights.protected)
    (B) (R) (hR : ∀ q vs, q ∉ D.rights.protected → (R q vs ↔ B.relation q vs)) (vs) :
  (outcomeBase (soften (correlate D)) p).denote { B with relation := R } (tupleVal vs) ↔
    (outcomeBase (soften (correlate D)) p).denote B (tupleVal vs)
  -- := SoftNorms.cone_independent (correlate D) _ p (rightDerived_regulated D h p hp) D.rights.protected hcone B R hR vs
theorem rights_conflict_free (D) (h) (certs) (hc : rightsConflictFreeCheck D certs = true) :
  ∀ B, BaseAdmissibleR D B → VE.Norms.ConflictFree (soften (correlate D)) B
-- rights_route_acceptance, rights_route_countermodel: soft_route_acceptance / _countermodel restated with
-- BaseAdmissibleR and backgroundR := background' (correlate D) ++ limPremises D (per-structure lemmas reused).
-- rights_wire_acceptance, rights_wire_conflict_sound: norms.md 11.4 shape from raw JSON through `ve_rights_route`,
-- every checker call delegated to unchanged W1/soft functions on the regenerated E″, T″, Lim_D.
```

`correlate_faithful` is by unfolding (the holder conjunct and the packed carve-out are ordinary, the bar is an ordinary
strict node with ordinary precedence); `no_distinction_sound` is `cone_independent` with `Q := protected`, its
regulated-name hypothesis supplied by `rightDerived_regulated`; `limitation_scope_sound` composes the syntactic
`Narrows` audit with the accepted entailment certificates, whose target is `cond_n° → limpack_N`. `Line` is the line
instance (instance kind, source kind, node); `linesOf D` lists `(right, instance)` pairs in instance order; `envR D`
is `E″` before `soften` and `envPrime (correlate D)` is `E″′`; the global `soft_coherent_expands_all` is restated
over `BaseAdmissibleR` as `rights_coherent_expands_all`. The route theorems are restated, not inherited (Astra 1): `Lim_D` enters through the first layer's
`Admissible_in`, as `Soft_T` does. Audit: existing allowlist, no `sorry`; `lean/RIGHTS.md`.

## 5. Coverage accounting

Statuses stay CHECKED / LABELLED / OPEN / READINGS / UNFORMALISED. A right whose active lines are strict rules over
declared vocabulary with no open term is CHECKED; one with an open standard in a guard, act, limitation or condition
is OPEN (`{"open": ["arbitrary", "rights__lim__1", "rights__cond__1"]}`, each generated name rendered with its
source keys beside it: `limitation 29, arrest_permitted`; `limitation 29, arrest_permitted, determined by law`);
one whose bearer, polarity, incident or force is unsettled is READINGS only when every candidate has elaborated lines
and a distinguishing situation; Art. 29(1), headers and Preamble "Whereas" units stay UNFORMALISED, LABELLED or
attribution. New residual lines: `bearer_readings`, `polarity_readings`, `incident_readings`, `force_readings` (per
unit), `couplings` (with axis, coupled units and citations; a coupled axis counted once), `limitation_terms` (with
decider, conditions and their deciders), `power_shadows`, `unlicensed_limitations` and `distinction_hits` (findings,
each cited or uncited), `narrowings` (with citations), `limitation_premises_used` (per certificate, beside
`coherence_premises_used`). Open standards count once per term; deciders are `unstated` unless a source unit names
one, so the pilot's `applicable_court` and `human_rights_interpreter` become cited narrowings or `unstated`. No gain
is counted without the soft-norms plan's three gates: end-to-end `ve document check` admission of right units, a
split-only baseline under `norms@0` alone, and blind whole-span fidelity review auditing every bearer, polarity and
force choice and every coupling. North Star's 0–8,800 B is an upper bound on tagged spans, not a forecast; this plan
predicts no number.

## 6. Work items

| # | Item | Owner, effort |
|---|---|---|
| 0 | Prerequisites: soft-norms items 0 (document-level norm admission), 2 and 4 merged (rights reuse `SoftDoc`, `ValueSoft`, `cone_independent`, `BaseAdmissible′`, the soft route); W1 fixtures green | soft-norms owners |
| 1 | `docs/spec/rights.md` (written with this draft): 1.1–1.5 as definitions; exact grammar for section 2; `Narrows` and the licensing table; couplings; diagnostics (`IncidentShape`, `HolderSlotAmbiguous`, `RightWithoutIncident`, `UnknownRight`, `FanOutUndeclared`, `CouplingLabelMissing`; findings `UnlicensedLimitation`, `ProtectedInCone`); fixtures; Astra + Fable statement review before 2–4 (PLAN-EXPAND2 rule 10) | spec, 3 days |
| 2 | Profile `rights@0` requiring `soft-norms@0` and `norms@0`: `rights` block; W2 unit kinds `right`, `right_lines`, `limitation`, `bar`; candidate `labels` and the `couplings` list in W2 under the profile gate; `correlate` and `Lim_D` in `ve/rights.py`; the `rights` Background slot; `ve document check` through the soft route with `Background_base″`; `norms@0` and `soft-norms@0` fixtures and hashes unchanged | Python, 5 days |
| 3 | Surface registrations (`Right n.`, `Claim/Liberty/Immunity/Power of right`, `includes:`, `Limitation m`, the three limitation sentences, the Art. 30 sentence, the coupling sentence, `has the right to`, `is entitled to`, `No one may`/`Everyone must` fan-out, passive rewrite; `Rule ` and `Right ` distinct keywords); W7 harness; `tests/test_english_unambiguity.py` | `ve/surface/rights.py`, 3 days |
| 4 | Lean `lean/VE/Rights/{Tree,Correlate,Semantics,Projections,Scope,Distinction,Bar,Wire,Admission,Run}.lean`, section 4 theorems, executable `ve_rights_route`; `lean/RIGHTS.md`; frozen files untouched | Lean, 5 to 7 days |
| 5 | Coverage residual lines; per-unit and coupled enumeration accounting; `conditional_on` with `coupling:<id>` and `rights:limitation:*` (metrics schema addition only) | Python, 2 days |
| 6 | W8: `add_right`, `add_line`, `add_limitation`, `add_coupling`; "who owes what to whom" paraphrase from `rightsOf`/`dutiesOf`; translation rule for `has the right to` and `shall` (never collapse; propose the bearer set and the force set); fidelity gate | `ve/assist/*` |
| 7 | UDHR rerun: Art. 2–3, 5, 8–10, 12, 14, 16, 18–19, 22, 25–26, 29–30 with per-unit sets, the three Preamble couplings and cited narrowings; both enumerations reported; split-only baseline; blind fidelity review; measured deltas only. Spot checks: 14th-s1 clauses 2–4 as claims of persons against states (L); two rights claims of the birthright debate (B) | pilot, 3 days |

Fixtures for item 1 (deterministic; Python and Lean where a case kind exists; full statements in rights.md 10):
(α) Art. 3 negative claim, no limitation: `owes_N(Texas, Ann)` is true in every situation, including one where Texas
deprives nobody (a duty is not a breach; `breach` needs `done`); `rightsOf`/`dutiesOf` agree with the same `R`, `N`;
`O_{deprive_permitted}(Texas, Ann)` false as the corollary. (β) Art. 5 fan-out to `state` and `person`: two nodes
`rights-fan-1`, `rights-fan-2` on two predicates, one header, the source line and sort rendered beside each; an
undeclared bearer predicate is `FanOutUndeclared`. (γ) Limitation 29 on Art. 9 with
`arrest_permitted` allow-by-default: where `arbitrary ∧ lim` the line is silent and arrest is permitted by the
default; with deny-by-default it is forbidden by the default; "permitted where `lim` holds" only once an adopter's
`lim`-guarded permission is composed; dropping `determined_by_law` from the conditions breaks the certificate for
"arrest without law is forbidden" (allow-by-default variant); an adopter's `Rule 7 (exception to claim of right 9).
Every state may arrest each person, if that person is a journalist` is `UnlicensedLimitation: exception 7 of rule
<n> on right 9`, and the finding disappears once the guard also requires `lim_{L29,arrest}` (certified case); the
same sentence without `(exception to …)` is a CONFLICT witness, not a narrowing; the certified guard's target is
`limpack_N`. (δ) A claim guarded by `religion(h, r)` without citation: `ProtectedInCone` finding, no invariance
claim for that predicate; the Art. 16(1) line with the citation: listed in `E`, still no claim; a predicate with a
protected-free cone: the invariance witness. (ε) Art. 16 power on `marry_permitted(person, person)` (`alters`:
`holder_slot` 0, `status` married, `recognition` declared): powerLiberty plus powerRecognition instance, both with
`H_R` "of full age", both covered by `kinds: [power]`; a refusing state's recognition duty selects (`owes`);
`free_{marry}` holds for the powerLiberty instance; nothing post-marriage is derivable; Art. 15(2)'s immunity on
`deprive_of_nationality_permitted(state, person)` (`holder_slot` 1, `recognition` null) is admitted and its
paraphrase says "must not", never "cannot". (ζ) Art. 3 under the
per-unit polarity set: both candidates elaborated; "Texas owes Ann protection" holds under SOME with the choice named;
under the Preamble polarity coupling the answer is conditional on `coupling:polarity`. (η) Art. 30 rule reading: a
strict liberty on `m` does not select where `aimed_m`; a default liberty likewise; a strict obligation on the same act
selecting there is a pair CONFLICT with a witness; an adopter's hard `may` on `m` without precedence is an
intra-predicate CONFLICT with a witness; query reading: the entailment fails and the countermodel exhibits the
liberty. (θ) `correlate_identity` and `correlate_identity_top`: every norms.md 10.1 and soft-norms 10 row whose rule
fits a shape of 1.1 within the rights limits, wrapped as a one-line right with `H_R = ⊤`, gives `correlate D =
flattenTop D` and identical statuses, witnesses and premise lists, default rows included; rows that fit no shape
are listed as skipped. (ι) Budget: 40 right units, each a set of four candidates (one per bearer × polarity label
pair), with couplings on bearer and polarity (binary) plus four uncoupled binary per-unit sets enumerate 2·2·2⁴ =
64 choices, admissible; a fifth uncoupled binary set makes 128 and a document-wide conclusion UNKNOWN with the five
units named; with no coupling the 40 four-candidate sets alone are UNKNOWN naming the 40 units; with all three
couplings over eight-candidate sets and no residual axis, 8. (κ) Art. 25 force set {strict, default}: both
candidates elaborated, `adequate` open under both; Art. 22 narrowed to default by citation with the resources
clause as a necessary condition: `excepted` is a licensed narrowing; the same default line without the citation:
`UnlicensedLimitation: exception of rule <n>`; without the citation but with limitation 29 declaring a sufficient
condition and the exception's necessary condition written as that condition's `cond` atom, the certificate for
`excepted_N → limpack_N` licenses it. (λ) Sole
purpose: `Γ` fixing `lim_{L29,arrest}(Texas, Ann)` true and `solely_for_permitted_purpose_arrest(Texas, Ann)` false
makes `Background_base″ ++ Γ` inconsistent and every dependent certificate `vacuous`; removing the necessary
condition admits that assignment. (μ) Collisions on one ternary act `publish_about(person, item, person)` under
`nary@0`, right 12's claim with `holder_slot: 2`: two strict right lines of opposite effect on one act: CONFLICT
with a witness; strict against default: the default gives way, CONFLICT-FREE, shown as blocking; default against
default, unranked: WEIGHING POINT, `conditional_on` the coherence premise; with an adopter's cited ranking:
RANK-RESOLVED with the narrowing named. (ν) Narrows over soft mechanisms: a user switch on a right line is a finding
unless cited; a strict adopter rule of the opposite sign on the same act blocking a default right line is a finding
unless cited or certified; blocking by another right's strict line is a collision, not a finding; a strict adopter
rule of the same sign blocking a default right line is "effect delivered", no finding. (ξ) Art. 29(1) is
UNFORMALISED; `Everyone has duties to the community` is not a line. (ο) Slots: a right-derived line with seven
author carve-outs is `ResourceLimit: carve-outs of rule <n>` (six allowed); with six a default or switchable line
carries eight in `T″′` and a strict unswitchable line seven; an ordinary rule keeps seven. (ρ) Two limitations over
one line, the first false and the second true: the line is silent, no finding, `limpack_N` holds while `lim_{L1}`
fails; a certificate for one limitation alone is not the licensing target. (σ) Same-effect strict blocking: an
adopter's strict `may` guarded on journalists over a default liberty line: blocked, licensed by construction,
"effect delivered by strict rule M", the line absent from `rightsOf` there while the outcome is `some true`; with a
strict `must not` also selecting, W1's CONFLICT and no "effect delivered" line; a default negative claim on `m`
blocked by `bar_m` under the rule reading: `bar`, no finding. (τ) The certified target: a carve-out certified as
`(own_N ∧ U)° → limpack_N` is licensed; where the own guard fails no mechanism is active and nothing is concluded;
a certificate to one limitation alone under two limitations does not license. (υ) Generated names: a 62-byte
limitation name is admitted and yields `rights__lim__1`, `rights__cond__1`; author names `rights-x`, `rights-9` and
an author predicate `rights__lim__1` are `InvalidInput`; an author `over: ["rights-bar-1"]` is `UnknownSymbol`;
adding a limitation renumbers and stales every certificate while the English stays unchanged; four fan-out instances
are `rights-fan-1` to `rights-fan-4`. (φ) `alters` typing: `deprive_of_nationality_permitted(state, person)` with
`holder_slot: 1` admits the immunity; `holder_slot: 0` is `InvalidInput: alters …`; a power on it is
`IncidentShape`; `marry_permitted` with `holder_slot: 1` or `recognition: null` under a power line is
`IncidentShape`. (χ) Coupling components: `c1` over `{S1, S2}` and `c2` over `{S3, S4}` on bearer give 2·2 = 4
choices, not 2; a joining `c3` gives 2; a second axis coupled over sets that lack some label pairs counts only the
consistent joint assignments; a family admitting none is `CouplingUnsatisfiable`, an error.

Review questions for the item-1 review: is the static, explicitly incomplete power shadow acceptable, or should
powers stay UNFORMALISED until stage 3? Is a default right line's uncited `excepted_N` rightly a finding under
Art. 29(2)'s "only"? Should the licensing table treat an authored precedence between two rights' lines as a
narrowing needing a citation (as drafted) or as a collision resolution?

## 7. Risks

1. **Entitlement read as permission.** A header with only a liberty line says less than the source. The IDE shows
   "nobody owes the holder anything under this reading"; translation sets always include a claim candidate where the
   source is passive; item 7 audits per unit.
2. **Invented bearers and invented uniformity.** "Every state" is a choice the Declaration never makes, and "every
   article with the same bearer" is a second one; both are attributed narrowings with the Preamble citation, listed on
   every dependent certificate, never a checker default.
3. **Reading explosion.** Per-unit sets over 55 units with four axes exceed 64 choices at once; the honest answer is
   UNKNOWN naming the units, and couplings are the disclosed way to get a document-wide answer (fixture ι).
4. **Hohfeld labels overclaim.** Labels are shape-checked types; powers and immunities are static and incomplete, and
   the report says so per line.
5. **Rule budget and same-act blindness.** Fan-out and positive candidates can approach W1's 256 rules (only the active
   choice is elaborated; measured in item 7); most inter-right conflicts are practical, not same-act, and stay invisible.
6. **Conditional read as unconditional.** Rights results are conditional on `Coh_T` and `Lim_D`; `conditional_on` and
   the exhibited situation are on every report, and a `Γ` contradicting a condition makes certificates visibly
   vacuous (fixture λ).
7. **Open standards read as decided; no measurable gain.** Standards are the residual headline, grouped by decider,
   and the report states that no theorem covers the deciders' tables. The 70 blocked units are labels, most with open
   standards and some with attribution, causation, time or metaphor co-blockers; the pilot number is reported as
   measured, including zero.

## 8. Review response table (finding → change)

| Finding | Change in this draft | Where | Regression |
|---|---|---|---|
| Astra 1 — "no background premise" false; limitations need executable conditions; sole purpose must be necessary | `lim` carries the full open-term schema; `Lim_D` premises regenerated, identity-bound, admitted in `BaseAdmissible″`, vacuity per soft-norms 6.5; `determined_by_law` and `solely_for_permitted_purpose` both necessary; route theorems restated; "certified lawful limitation" → "certified to entail the limitation predicate" | 0, 1.1, 1.2, 1.4, 3, 4 | (γ), (λ) |
| Astra 2 — a carve-out grants no permission; define `Narrows` over every mechanism | fixture γ under both completions; paraphrase "gives way; the other rules and the default then decide"; `Narrows` over author carve-outs, exceptions, `lim`, `excepted`, switches, blocking, dominance, bar with a licensing table | 1.2, 1.4, 2 | (γ), (ν) |
| Astra 3 — holder and right identity; same `R` in `projections_agree`; fixture α wrong | `H_R` conjoined at the holder slot (object / subject); powers two explicit rules; `correlate_identity` restated (`_top` for byte identity); `owes_N`, `rightsOf`, `dutiesOf` over selecting lines with the same `R`, `N`, `v̄`; outcome a corollary; α corrected | 1.2, 4 | (α), (ε), (θ) |
| Astra 4 — shared sets remove mixed combinations; Art. 25–26 not automatically default; fixture ι | per-unit base with axis labels; couplings as attributed narrowings in `conditional_on`; uncoupled independence and UNKNOWN beyond budget; force READINGS per unit; Art. 22 and 26(1) cited narrowings; Art. 25 example withdrawn; ι = 64 admissible, fifth set UNKNOWN | 1.3, 1.5, 2, 5 | (ζ), (ι), (κ) |
| Astra 5 — collisions follow the reused semantics | strict–strict CONFLICT, strict–default blocking, default–default `CP` classification; "every collision is a WEIGHING POINT" replaced | 1.5, 3 | (μ) |
| Astra 6 — labels exceed guarantees; `noDistinction` limits | powers and immunities explicitly incomplete with `power_shadows`; decider limitation stated beside every result | 1.5, 1.4, 3, 5 | (ε), (δ) |
| Fable 1 (Astra round 2/3) — Art. 30 bar conflicts with strict liberties | `bar_m` with precedence over right-derived positive lines; "no derived precedence" → "none except the bar's"; `bar_blocks`, `bar_value` scoped to `correlate`'s output with composition assumptions; query reading kept | 1.1, 1.2, 1.4, 4 | (η) |
| Fable 2 — `owes` on completed outcomes | as Astra 3 | 1.2 | (α) |
| Fable 3 — force is a fourth axis | force axis per unit; `force` coupling citing the Preamble as a narrowing, never automatic | 1.3 | (κ), (ι) |
| Fable 4 — theorems silent on deciders | stated beside every `no_distinction` and `limitation_scope` result and under "open" | 1.4, 3 | report text |
| Fable 5 — findings, not admission errors; the Declaration distinguishes | `UnlicensedLimitation`, `distinction_hits` are report lines; cited set `E` | 1.4, 5 | (δ), (γ) |
| Fable 6 — `Narrows` over soft-derived carve-outs | as Astra 2 | 1.4 | (ν) |
| Fable 7 — `shared_by` changes the W2 schema | replaced by `labels` on candidates and the `couplings` list, gated under `rights@0`, existing identities unchanged | 1.3, item 2 | (ι) |
| Fable 8 — fixture ι arithmetic | corrected | 6 | (ι) |
| Fable 9 — immunity paraphrase | "must not"; effect not modelled | 2 | (ε) |
| Fable 10 — Art. 29(1) | UNFORMALISED | 1.4, 5 | (ξ) |
| Fable 11 — carve-out slots | one packed `lim` carve-out; six author slots stated | 1.2 | (ο) |
| Fable 12 — `lim` verbalisation | part of the limitation schema | 1.1, 2 | (γ) |
| Astra round 3 — restricted invariance theorem | `no_distinction_sound` over protected-free cones with `E` listed; no unrestricted claim | 1.4, 4 | (δ) |

Statement review of rights.md draft 1 (`manage-agents/debates/rights-spec`, FIX, CONVERGED after round 3; applied
in this draft and in rights.md draft 2, no design change; rights.md 14 carries the full table):

| Finding | Change in this draft | Where | Regression |
|---|---|---|---|
| Astra 1, Fable round 2 — several limitations falsify `limitation_scope_sound` | first disjunct and certification target `limpack_N`; "some limitation in scope holds"; the "only" paraphrase over every covering limitation | 1.4, 2, 3, 4 | (ρ), (τ) |
| Astra 2, round 3 — same-sign strict selection blocks a default; bar surfaces | blocking at soft-norms 4.2 step 2's width; same-effect licensed by construction, "effect delivered", never a finding or collision, `same_effect_delivered`; the bar's edges and blocking one mechanism; a fifth case | 1.2, 1.4, 4 | (σ), (ν) |
| Astra 3, Fable 4 — `owes_outcome` hypotheses; activation on `B`; `cone_independent`'s hypothesis | line membership and typing; every mechanism condition outcome-substituted; `ruleReading` on the bar case; `rightDerived_regulated` | 1.2, 4 | (τ) |
| Astra 4, Fable 1, round 2 — generated names violate W1's grammar and the 64-byte limit | index names under reserved prefixes `rights-` / `rights__`; source keys rendered beside them | 1.1, 1.2, 5 | (υ), (β) |
| Astra 5, Fable 2, 3 — incident typing; split powers | `alters.holder_slot`; instance kinds with the source kind kept | 1.1, 4 | (ε), (φ) |
| Astra 6, Fable 5, round 3 — environment identity; θ; μ | `E″` before and `E″′` after `soften`; `correlate D = flattenTop D`; θ restricted; μ ternary under `nary@0` | 1.2, 4, 6 | (θ), (μ) |
| Astra 7 — coupling enumeration | per component; `CouplingUnsatisfiable` | 1.3 | (χ), (ι) |
| Fable precision — `need not`, ι, κ, ο, node order, `coherent_expands` | releases rejected; four candidates per set; κ through a declared sufficient condition; ο on a hard line; node order stated; `rights_coherent_expands_all` restated | 1.1, 1.2, 4, 6 | (ι), (κ), (ο) |
| Plan questions | kept as drafted (both reviewers): static power shadow with `power_shadows`; uncited `excepted` a finding; authored precedence or rank between rights' lines needs a citation | 6 | (ε), (κ), (μ) |

## Summary

Rights enter VE as the holder-side view of W1 and soft-norm rules: a right block names a holder sort and guard and
lists Hohfeldian incident lines (claim, liberty, immunity, power), each an ordinary rule whose shape the checker
types, so correlativity is a theorem by construction and "who owes what to whom" is a projection of which lines
select. `correlate` adds only the holder conjunct, one packed limitation carve-out, power recognition claims, bearer
fan-out and the Art. 30 bar with its precedence, plus the declared limitation-condition premises; W1's and the soft
route's per-structure theorems are reused as lemmas and the route theorems are restated with that one extra premise.
Article 29 becomes an open limitation term with two necessary conditions and an executable "only such limitations"
audit over every narrowing mechanism, Article 2 a non-discrimination check restricted to protected-free cones with
cited distinctions listed, Article 30 a hard bar over right-derived liberties with a scoped theorem or a
non-entailment query. Bearer, polarity, incident and force stay per-unit reading sets; document-wide uniformity is an
attributed coupling narrowing named on every dependent certificate; collisions are classified as the reused semantics
classifies them. Coverage counts a unit only after end-to-end admission, a split-only baseline and blind fidelity
review; no number is predicted.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Initial plan: rights as holder-side view of W1/soft rules; incident shapes; `correlate`, `ValueRight`; shared reading sets; Art. 29/30/2 as limitation term, scope check, bar and non-discrimination check; Lean statements; coverage lines; work items; fixtures; risks. Plan only. |
| 2026-09-27 | Draft 2 | Transcribed the converged design-rights debate (Astra 1–6, Fable 1–12, round-3 shapes): limitation conditions as regenerated, admitted, identity-bound premises with sole purpose necessary and route theorems restated; `Narrows` with a licensing table and findings instead of admission errors; `H_R` in every line, explicit two-rule powers, `owes_N`/`rightsOf`/`dutiesOf` over selecting lines with the same `R`; per-unit reading sets with axis labels and attributed coupling narrowings (bearer, polarity, force) in `conditional_on`; conflict/blocking/weighing classification; Art. 30 bar with precedence and the scoped `bar_blocks`/`bar_value`; restricted `no_distinction_sound` with cited distinctions listed and decider limits stated; immunity "must not"; Art. 29(1) UNFORMALISED; one packed `lim` carve-out with six author slots; corrected fixtures α, γ, ι and new fixtures κ–ο; Art. 25 example withdrawn for Art. 22; response table. Item-1 spec rights.md written. Plan only; estimates unchanged. |
| 2026-09-28 | Draft 3 | Applied the converged rights-spec statement review (FIX, round 3), no design change: `limpack_N` as the first case and certification target of `limitation_scope_sound`; blocking at soft-norms 4.2 step 2's width with same-effect blocking licensed by construction (`same_effect_delivered`); `owes_outcome` with membership and typing; mechanism conditions outcome-substituted; `rightDerived_regulated`; generated names by index under reserved prefixes; `alters.holder_slot`; instance kinds with the source kind kept; `E″`/`E″′` staging and `correlate_identity_top` as `correlate D = flattenTop D`; couplings per component with `CouplingUnsatisfiable`; releases rejected; fixtures β, ε, θ, ι, κ, μ, ν, ο corrected and ρ–χ added; second response table. rights.md draft 2 written from this draft; one statement-only verification round before items 2–4. Plan only; estimates unchanged. |
