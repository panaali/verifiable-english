# Soft norms (`soft-norms@0`): defeasible rules, ranks and instruction authority over `norms@0`

> Status: item-1 specification, draft 1 (2026-09-27), written from [soft-norms-PLAN.md](soft-norms-PLAN.md) draft 3,
> the transcription of the converged Astra/Fable debate (`manage-agents/debates/soft-norms/{astra,fable}.md`). It is
> the statement under the Astra + Fable item-1 review that gates items 2, 3 and 4 (PLAN-EXPAND2 rule 10). Sections 4
> to 6 and 9 are the statements under review; section 13 lists every point where this draft chose between readings of
> the plan. Theorem statements and fixtures are implementation obligations, not claims of completed proofs or tests.
> Inputs: [norms.md](norms.md) (W1, cited as `norms.md n`), [document.md](document.md) (W2),
> [VISION.md](../../VISION.md), `lean/VE/Norms/*` and [lean/NORMS.md](../../lean/NORMS.md) (the W1 Lean names this
> spec reuses), the pinned constitution (`manage-agents/pilots/claude-constitution/source/claude-constitution.md`,
> cited by line as `:n`). Nothing here changes a frozen contract, a `norms@0` hash, a W1 theorem statement or a
> checker function.

## 0. Scope, one paragraph

A soft norm is **a strict rule plus a named open exception**. "Every assistant should X" means "X is required unless
this rule's exception applies here", and whether it applies is an open term with a decider (W2 schema). Weighing is
never a consequence relation inside the checker; it is a set of named open decisions whose *structure* the checker
certifies: which rules can collide, which collisions the declared ranks resolve, which are left to a decider, and
that hard constraints are never weighed. Every soft document elaborates by `soften` into a `norms@0` tree `T′` over an
extended vocabulary `E′`, and the elaboration is Lean-proved faithful to a direct terminating procedure `ValueSoft`
defined on the soft tree itself. What that buys, exactly: W1's definitions and per-structure theorems are reused as
lemmas; W1's document-wide route theorems are **restated** with one extra base premise, the coherence `Coh_T` of the
deciders' findings, and every soft result is conditional on it. "All things considered" is exactly what the checker
does not compute: it computes the outcome given the deciders' findings and lists what those findings must satisfy for
the rules to be jointly followable.

In this specification: the three attributes and the environment declarations (1), the English (2), the wire form
(3), `ValueSoft` (4), `soften` (5), decision assignments, coherence and the conditional contract (6), the report (7),
diagnostics (8), the Lean definitions and every item-4 theorem as a statement (9), the item-1 acceptance fixtures
(10), limits (11), the review checklist (12) and the resolved choices (13).

Out of scope, by the plan: numerical weights and any consequence relation over them; cross-act practical
incompatibility ("help" versus "refuse" are different acts; stage 3); an operator restriction on a user switch
(removed from `@0` pending specified semantics; debate group 7); adjudication of any open decision; the coverage
counting protocol (plan section 4, items 5 and 7); the surface registrations (item 3) and W8 hooks (item 6) beyond
the wordings fixed in section 2.

## 1. What a soft-norm document is

A soft-norm document is a W1 tree `T` (norms.md 1: regulated predicates, situation variables `x̄`, rules with
predicate, sign, guard `G_N`, carve-outs `U_N`, author precedence `over`, the two DAGs) whose rules carry three
further attributes, plus soft declarations in the environment. Everything W1 requires of `T` still holds
(norms.md 3.1, 4.1); the soft checks come on top (4.1 below).

### 1.1 Three independent attributes: defeasibility, instruction authority, rank

```text
mode(N)       ∈ {strict, default}
                strict  = a W1 rule: no exception term.
                default = defeasible: N carries an open exception term excepted_N(x̄) with a decider.
alterable(N)  ⊆ Parties(E)
                the parties who may switch N off by instruction, each through its own base predicate
                off_{N,π}(x̄); switch_N(x̄) := ⋁_{π ∈ alterable(N)} off_{N,π}(x̄) (the empty disjunction is ⊥).
rank(N)       ∈ Ranks(E) ∪ {none}
                a declared name ("safety", "helpfulness"); it affects only default rules (theorem
                hard_never_weighed, 9.3). A rank on a strict rule is accepted and inert; the paraphrase says so.
hard(N)       := mode(N) = strict ∧ alterable(N) = ∅               (derived, never declared as a mode)
                no exception decision, no instruction switch; only a strict exception rule written in the document
                can override it (W1 precedence). A rule may additionally carry the declared assertion `hard: true`
                (3.2), set by a cited narrowing in translation; it is checked against the two attributes
                (HardConstraintAltered) and adds no semantics.
exception(N)  present iff mode(N) = default: decider (named at the rule, inherited from the document, or the
                literal `unstated`), `necessary` and `sufficient` conditions (base formulas over x̄), `factors`
                (English phrases, no premise).
```

The three attributes vary independently. A strict rule may be user-alterable (:185-192 read as strict, rule 20 in
2.4); a default rule may have no switch (:166, rule 4); a default rule may be ranked or not; a hard rule is what is
left when a rule is strict and has no switch. Nothing else is derived from the mode: in particular "strict rules have
no switch" is false and not assumed anywhere (review B1).

### 1.2 Parties, ranks and the outranking flag (environment, identity-bound)

```text
Parties(E)     a finite list of identifiers (at most 8); alterable(N) ⊆ Parties(E); a base predicate may carry
               `instruction_of: π` with π ∈ Parties(E), rendered in the legend as
               "<verbalisation> records an instruction of <π>."
Ranks(E)       a finite list of identifiers (at most 16)
outranks       declared edges (a, b), "a outranks b"; closed transitively into outranks⁺, which must be a strict
               partial order: a cycle is DependencyCycle over the rank names (via dependencyOrder, the shared
               diagnostic); a rank not in Ranks(E) is UnknownRank
ties           declared pairs "a and b are not ranked": both ranks must be incomparable in outranks⁺
               (TieAgainstOrder otherwise); incomparable pairs that are not declared are listed as undeclared ties
               in the report (a warning, :347 "in no particular order"); ties add no edge
outranking     one flag per document: `strict` or `holistic` (:34); `holistic` names a decider for the override
               terms (or `unstated`)
exception_decider  the document-level decider a default rule inherits when its own is absent
```

`Comparable(M, N)` holds when both rules are ranked and `rank(M) outranks⁺ rank(N)` or the converse; two rules with
incomparable ranks, or one unranked rule, are not comparable.

### 1.3 Decision predicates and the extended vocabulary `E′`

`E′ = E + decisions`, regenerated at every site from `E` and `T` (never taken from the wire). The decision predicates
are fresh base predicates:

| Predicate | Exists for | Argument sorts | Meaning (open) |
|---|---|---|---|
| `excepted_N` | every default rule `N` | the sorts of `N`'s predicate | rule `N`'s exception applies at `x̄` |
| `off_{N,π}` | every rule `N` and every `π ∈ alterable(N)` | the sorts of `N`'s predicate | party `π` has switched `N` off for `x̄` |
| `outweighs_{a,L,H}` | every act `a` and every ordered rank pair `L` below `H` (`H outranks⁺ L`) used by some colliding pair on `a` (1.4), under the `holistic` flag | the sorts of act `a` | on act `a` at `x̄`, the `L`-ranked consideration outweighs the `H`-ranked one |

Below, `outweighs_{a,N,M}` abbreviates `outweighs_{a,rank(N),rank(M)}` for rules `N`, `M` on act `a` with
`rank(M) outranks⁺ rank(N)`; it is the same atom for every colliding pair on `a` with those two ranks, not a
rule-pair predicate. Act identity, ordered ranks and the argument sorts are identity-bound in `E′` (3.4). Two acts
with different argument sorts that share a rank pair have two distinct predicates, each with its act's sorts
(fixture ν); this is why the predicate is indexed by the act and not by the rule pair (debate group 5).

Canonical names (identifiers of the existing grammar `[a-z][a-z0-9_]*`): `soft__excepted__<rule>`,
`soft__off__<rule>__<party>`, `soft__outweighs__<L>__<H>__<act key>`, where a rule name's `-` becomes `_` (rule names
contain no `_`, so this is injective) and the act key is the act's permission predicate when declared, else the act's
only regulated predicate. Under `soft-norms@0` an author predicate beginning with `soft__` and a rank, party or
act-key predicate name containing `__` are rejected (`InvalidInput`), so the generated names are collision-free.
Rule formulas (guards, carve-outs, exception conditions) are over `E`, never over the decision predicates.
Premises `Γ` and W2 premise units may mention decision predicates as separately identified **decision findings**,
typed over `E′`; the English renders each decision predicate in document terms ("rule 12 is excepted here").

Decision predicates carry no attribution: what a decider considers is outside the checker (VISION.md, converged rule
item 8). `off_{N,π}` records that `π` exercised a declared switch; the environment's `instruction_of` attributes
ordinary base facts to a party; neither says anything about what `excepted_N` or `outweighs` take into account.

### 1.4 Effects, acts and colliding pairs

Each rule has an *effect* on its act, determined by its predicate's role and its sign:

| Role of `N`'s predicate | sign `+` | sign `−` |
|---|---|---|
| obligation `r` | `require` | `release` |
| permission `m` | `permit` | `forbid` |
| plain `p` | `+p` | `−p` |

The act of a rule is its predicate's act identity (norms.md 3.1: ordered argument sorts and canonical act phrase);
a plain regulated predicate is its own act. Two rules `M`, `N` are **incompatible** when they regulate the same act
and either regulate the same predicate with opposite signs, or one requires (`+r`) and the other forbids (`−m`)
across the declared dual pair `(r, m)` of that act. `release` and `permit` are compatible ("need not" and "may"),
as are `require`/`permit` and `release`/`forbid`. Incompatibility is therefore opposite polarity on one act, with
polarity the sign; the relation is bipartite ({require, permit, +p} against {release, forbid, −p}).

```text
CP(T) := { {M, N} : M, N default rules, incompatible }          the colliding default pairs (unordered)
```

Strict–default incompatibility is handled by blocking (4.2 step 2), strict–strict incompatibility by W1's conflict
check on `T′`; only default–default pairs are weighing material. This replaces the same-predicate-only notion of the
first plan draft (review A2).

## 2. The English (one reading each; rejected as today when `soft-norms@0` is off)

### 2.1 Wordings

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `Rule n. Every <noun> should <act>[, if C][, unless U].` | In every situation of the kind, the act is required unless rule n's exception applies there; <decider> decides whether it applies. | default, obligation `+`; `excepted_n` |
| `... should not <act>` | ... the act is not permitted unless rule n's exception applies there. | default, permission `−` |
| `... generally may <act>` / `... generally need not <act>` | ... permitted / not required unless rule n's exception applies there. | default `+` permission / `−` obligation |
| `... must` / `must not` / `may` / `need not` | as W1 (norms.md 2.1): strict. | strict |
| `The exception to rule n is decided by <decider>.` | Names who decides whether rule n is excepted in a situation. | `exception.decided_by` |
| `Exceptions to rules in this document are decided by <decider>, unless a rule says otherwise.` | Document-level decider. | `exception_decider` |
| `Rule n is excepted when C.` / `Rule n is excepted only when C.` | C is sufficient / necessary for rule n's exception. | `sufficient` / `necessary` premise (6.1) |
| `The exception to rule n takes account of <consideration>[, <consideration>]*.` | These considerations bear on whether rule n is excepted; none is by itself decisive. | `factors` (no premise) |
| `Rule n serves <rank>.` | Rule n counts as a <rank> consideration where it collides with a rule of another rank. On a strict rule: recorded; a strict rule is never weighed. | `rank(n)` |
| `<Rank a> outranks <rank b>.` | Where two rules of these ranks collide on one act, the lower rule gives way to an effective higher rule, subject to the holistic override if declared. This is pairwise defeat, not a guarantee that the higher rule finally decides. | `outranks` edge |
| `<Rank a> and <rank b> are not ranked.` | Neither outranks the other; a disagreement between rules of these ranks is a weighing point. | declared tie (checked) |
| `Outranking in this document is strict.` | A lower rule gives way to an effective higher opponent. No guarantee of final selection. | flag `strict` |
| `Outranking in this document is holistic; <decider> decides when a lower-ranked rule outweighs a higher-ranked one in a situation.` | A lower rule gives way to an effective higher opponent unless the decider finds that it outweighs that opponent; a higher rule gives way to an eligible lower opponent found to outweigh it, even where that lower rule itself gives way. No guarantee of final selection. | flag `holistic`; `outweighs_{act,L,H}` |
| `Rule n (operators may turn off).` / `(users may turn off)` / `(operators and users may turn off)` | The rule holds unless the named party has turned it off for the situation; no other party has a switch. Combines with the W1 header as `Rule n (exception to rule m; users may turn off).` | `off_{n,π}`; authority report |
| `"<verbalisation> records an instruction of <party>."` (environment legend) | This fact is an instruction of that party. | `instruction_of` |

The rule's mode is fixed by its deontic verb: `should`, `should not`, `generally may`, `generally need not` are
default; `must`, `must not`, `may`, `need not` are strict. There is no wording for `hard`: it is derived, and the
paraphrase states it (2.3).

### 2.2 Synonyms and non-synonyms

Input synonyms rendered canonically: `generally must` → `should`; `generally must not` → `should not`. Nothing else.
`should generally` and `should generally not` are rejected in authoring; in translation both have one reading
(default).

`normally`, `typically`, `usually`, `as a rule` are **not** synonyms (review B3): each also expresses frequency
("Claude can typically help" is an assertion about most cases). In authoring the IDE shows both paraphrases (a
default rule; a hedged frequency claim) with a situation, and the author picks; in translation the unit is a READINGS
set of the two. Bare `generally <verb>` without a deontic verb is not a norm wording. `By default,` remains the W1
completion legend, never a rule marker; a sentence-initial "By default, Claude should ..." is rewritten by the IDE to
a `should` rule or an alterable rule, showing both paraphrases with a situation. `must` stays strict. In translation
any force word (`should`, `must`, `always`, `never`) is a READINGS unit `{strict, default}` unless a cited source unit
narrows it; `should generally` and `generally may` have one reading (default).

### 2.3 The reader's checklist (norms.md 2.5, extended)

For every default rule the IDE shows, in English only: the deterministic paraphrase naming the exception and its
decider (or "the source names none"); a situation in which the rule decides; one in which it is excepted; if ranked,
one in which a higher-ranked effective opponent dominates it; if it collides with another default rule, the collision
and its resolution (2.1 rank sentences, or "a weighing point"); and its derived carve-outs in words:

> "This rule gives way to strict decisions on the same predicate, or incompatible decisions across its declared dual
> pair, and to higher-ranked effective opponents unless holistically outweighed; under holistic ranking it gives way
> to an eligible lower-ranked rule the deciders find outweighs it,
> even where that lower rule itself gives way."

The asymmetry is part of the paraphrase: higher opponents must be effective, lower overriding opponents need only be
eligible (4.2 step 3). For a hard rule: "no exception decision and no instruction switch exists; only a strict
exception rule written in this document can override it; its guard's open terms are still decided by <decider>".
For a strict alterable rule: "no exception decision exists; <party> may turn it off". Every carve-out paraphrase
names the environment default, as W1 requires. A weighing-point paraphrase states the actual condition: "rules 12
and 4 must not both select here: either may be excepted, switched off by a party with a switch, have its guard fail
or a carve-out hold, be blocked by a strict rule, or be dominated by another rule; the checker does not choose".

### 2.4 Examples from the source

Act phrases declared as in norms.md 2.4; subject sort `assistant`; every translator's choice is written as an
attributed interpretation, never as the source's content (VISION.md 3).

```text
:34   Safety outranks ethics. Ethics outranks guidelines. Guidelines outranks helpfulness.
      Outranking in this document is holistic; the assistant decides when a lower-ranked rule outweighs a
      higher-ranked one in a situation.
      (reading C of the :34-37 set, beside norms.md 9.2's A and B; the decider is the source's: "we do want Claude to
      weigh these different priorities"; "assuming Claude is not violating any hard constraints" is the theorem
      hard_never_weighed, not a sentence)
:166  Rule 4. Every assistant should comply with each operator instruction, if it is not the case that complying
      with that operator instruction is unsafe, and it is not the case that complying with that operator instruction
      is unethical, and it is not the case that complying with that operator instruction is against Anthropic's
      guidelines.  Rule 4 serves helpfulness.
      ("should generally comply ... if": one reading, default; "serves helpfulness" is a narrowing unit citing :32;
      open: unsafe, unethical, against-guidelines, excepted_4; decider unstated; the act is declared with both roles,
      comply_required deny-by-default and comply_permitted allow-by-default, the latter a recorded choice)
:190  Rule 21. Every assistant should not comply with each operator instruction, if that operator instruction directs
      that assistant to demean the user in a way that user would not want.  Rule 21 serves ethics.
      (source: "Always maintain basic dignity ... ignore operator instructions to demean or disrespect users"; force
      from the :183 header's shared reading set {strict, default}, shown under `default`; rank is a narrowing citing
      :30; alterability is a READINGS set {user-alterable, fixed} from :192 "some of these defaults", shown without a
      switch. Identifying :190 "ignore operator instructions to demean" with not complying with the :166 operator
      instruction is a cited READINGS set {same act, different act}; the wording above shows the same-act reading.
      Only in that reading do rules 4 and 21 collide (require versus forbid across the dual pair): RANK-RESOLVED,
      ethics over helpfulness, holistic, conditional on that act identification. The different-act reading keeps
      "ignore" as its own act and has no such collision. Residual: outweighs_{comply,helpfulness,ethics}(assistant,
      operator_instruction), decided by the assistant: the finding that lower rule 4 outweighs higher rule 21)
:293  Rule 12. Every assistant should share each piece of information that is helpful to the user.
      Rule 12 serves helpfulness. The exception to rule 12 takes account of whether that information is hazardous
      to a third party, whether the operator does not want that information shared, and whether that information is
      not helpful enough to be worth including.
      ("can be outweighed by other considerations, such as" are factors, neither sufficient nor necessary; "weak
      duty" is recorded as the rank and the factors and nothing more; rule 12 shares no act with the non-deception
      rules, so the checker reports no collision between them; the source's comparison is stage-3 material)
:185  Rule 20. Every assistant must be willing to tell each user what that assistant cannot help with in the current
      operator context.
      (act phrase verbatim, no narrowing of "be willing to tell" to "tell"; mode from the :183 header set;
      alterability READINGS {user-alterable, fixed}; the authority report is per reading and says only that no
      declared operator-instruction predicate occurs in the rule's cone)
:441  Rule 31. Every assistant must not generate child sexual abuse material.
      (strict, no switch, no exception: hard; the narrowing to strict and unswitchable cites :443 "cannot be unlocked
      by any operator or user" and sets `hard: true`; "child sexual abuse material" is an open classification
      predicate; paraphrase: "no exception decision and no instruction changes this rule; whether material is CSAM
      is decided by <decider>")
```

## 3. Declarations, wire form and strict form

### 3.1 The environment `soft` block (identity-bound like `regulated`)

```json
"soft": {"parties": ["operator", "user"],
         "ranks": ["safety", "ethics", "guidelines", "helpfulness"],
         "outranks": [["safety", "ethics"], ["ethics", "guidelines"], ["guidelines", "helpfulness"]],
         "ties": [],
         "outranking": {"mode": "holistic", "decided_by": "assistant"},
         "exception_decider": "assistant"},
"predicates": {"operator_instructs": {"arguments": ["assistant", "instruction"], "description": "...",
                                      "verbalisation": "{0} is instructed by the operator to carry out {1}",
                                      "instruction_of": "operator"}, ...}
```

`parties` and `ranks` are lists of distinct identifiers (`DuplicateDeclaration: rank <a>` / `party <π>`); `outranks`
and `ties` name declared ranks (`UnknownRank`); `outranking.mode` is mandatory when the block is present and
`decided_by` is mandatory under `holistic` (a string of at most 64 bytes, or `unstated`; `MissingExceptionDecider:
outranking` if absent); `exception_decider` is optional; `instruction_of` names a declared party (`UnknownSymbol:
party <π>`) and is allowed on base predicates only (`InvalidInput` on a regulated or defined predicate). The whole
block is part of the canonical environment bytes, so `environment_id` changes when any of it changes and is unchanged
for every existing environment (none has the block). `soft-norms@0` requires `norms@0`
(`UnsupportedProfile: soft-norms@0 requires norms@0`); the block is rejected when the profile is off.

### 3.2 Norm content fields (W2 unit of kind `norm`, extending norms.md 3.2)

```json
{"norm": {"name": "share-helpful", "predicate": "share_required", "sign": true,
          "guard": ["binary", "helpful_to", ["var", 0], ["var", 1]], "unless": [], "over": [],
          "mode": "default", "rank": "helpfulness", "alterable": [],
          "exception": {"decided_by": null,
                        "sufficient": [], "necessary": [],
                        "factors": ["whether that information is hazardous to a third party",
                                    "whether the operator does not want that information shared",
                                    "whether that information is not helpful enough to be worth including"]},
          "hard": false}}
```

`mode` defaults to `strict` when absent, so every existing `norms@0` unit is a valid soft unit with unchanged
meaning. `rank` is a declared rank or absent. `alterable` is a sorted list of distinct declared parties. `exception`
is mandatory when `mode` is `default` and forbidden when `strict` (`InvalidInput: rule <n> is strict and declares an
exception`); its `decided_by` is a string, `unstated`, or `null` to inherit the environment's `exception_decider`;
when both are absent the diagnostic is `MissingExceptionDecider: rule <n>`. `sufficient` and `necessary` are
formulas in the P0 wire form over the context of the predicate's argument sorts (as `guard`), over the base
vocabulary of `E` only: a condition mentioning a regulated, defined or decision predicate is
`InvalidInput: exception condition of rule <n> mentions <q>`. `factors` are strings of at most 200 bytes. `hard`
defaults to `false`; `hard: true` with `mode: default` or a non-empty `alterable` is `HardConstraintAltered: rule
<n>`. The author never has to write `hard`; a translation's cited narrowing sets it so that a later switch or force
change is caught rather than silently accepted.

### 3.3 Strict text (the fallback of P0 3.2)

```ebnf
rule       = "rule ", name, [ " over ", name, { ", ", name } ], [ " default" ], [ " serves ", rank ],
             [ " alterable by ", party, { ", ", party } ], ": ", binders, ", ", literal,
             [ " if (", formula, ")" ], { " unless (", formula, ")" }, "." ;
exception  = "exception of ", name, [ " decided by ", decider ], { " sufficient (", formula, ")" },
             { " necessary (", formula, ")" }, { " factor ", quoted-string }, "." ;
```

Parties, ranks, the flag and attributions are environment JSON, as `regulated` is; they have no strict text.
`print(parse(s)) = s` on canonical text; English and strict forms round-trip through the same AST with W1's
preserved name metadata (norms.md 10.6, 11.2).

### 3.4 Identity

`environment_id` binds the `soft` block and every `instruction_of` (3.1) beside `regulated`. A soft norm unit's
`meaning_id` is W1's (`sha256("ve-meaning-<identity_version>\n" + canonical({"environment_id", "ast"}))`) with `ast`
the norm object of 3.2 including the new fields. The canonical object omits every soft field at its default value
(`mode: strict`, no `rank`, empty `alterable`, no `exception`, `hard: false`), so a `norms@0` unit's canonical bytes
and `meaning_id` are unchanged and a strict unswitchable soft unit has the same identity under either profile. The
soft document hash is the canonical array of soft norm objects in document order
under `environment_id`. `E′`, `T′`, the exception premises and `Coh_T` are regenerated from these at every site. A
conflict or classification package has an outer binding `(environment_id, soft_document_hash, target)` and an inner
certificate bound to the canonical **regenerated** `E′_base` and, for conflict, `Background_base′`, or, for
classification, `Background_base(E′) ++ Exc_T` with all coherence conjuncts excluded (norms.md 11.4 step 4).
Classification witnesses are checked against that same coherence-free background. An entailment certificate binds
the full regenerated `E′` and `background′ ++ layer premises ++ Γ` (6.1). Changing a
rank, an `outranks` edge, the flag, a party, a switch, an exception condition, a decider or a mode invalidates every
certificate of the document.

## 4. Semantics

### 4.1 Well-formedness (`WellFormedSoft`)

A soft document `(E, T)` is well-formed when, in this order:

1. `E` enables `soft-norms@0` and `norms@0`; the `soft` block and the norm fields decode (3.1, 3.2).
2. `T` without the soft fields is W1 well-formed over `E` (norms.md 4.1), including both DAGs.
3. Every rank named by a rule is declared (`UnknownRank: rule <n>, <rank>`); every party in `alterable` is declared
   (`UnknownSymbol: party <π>`); every default rule has a decider by inheritance or its own
   (`MissingExceptionDecider: rule <n>`); `holistic` names a decider (`MissingExceptionDecider: outranking`).
4. `outranks⁺` is a strict partial order: `dependencyOrder` over the rank nodes (edge `a → b` for each declared
   `a outranks b`) succeeds, else `DependencyCycle: <sorted rank names>`; every declared tie is incomparable
   (`TieAgainstOrder: <a>, <b>`).
5. **SoftOverHard.** No default rule takes precedence over a strict rule: for every default `N` and every
   `M ∈ over(N)`, `M` is default (`SoftOverHard: rule <N> over <M>`). Hence every descendant of a strict rule is
   strict, and a strict rule's `selects` is the same whether computed among the strict rules alone or in the whole
   tree. A strict child of a default parent is allowed.
6. `hard: true` implies `mode = strict` and `alterable = ∅` (`HardConstraintAltered: rule <n>`).
7. Exception conditions are typed over the rule's context and mention base predicates of `E` only (3.2).
8. The elaborated `T′` (section 5) is within `MAX_NODES` per formula (`ResourceLimit: derived carve-out of rule
   <n>`), and is W1 well-formed over `E′`: the stratification of norms.md 4.1(4) computed on `T′` succeeds, with the
   `DualGuardCycle` hint when the cycle is absent on `T` (5.2).

Warnings (reported, never rejecting): `RankAgainstPrecedence: rule <N> over <M>` when `M ∈ over(N)`,
`{M, N} ∈ CP(T)` and `rank(M) outranks⁺ rank(N)` (legal; inert when `N` has no descendants, since `N` is effective
only where `M` is not; otherwise `N`'s yielding descendants can still silence `M` through the edge even when `N` is
dominated; fixtures θ and υ); undeclared ties; `Overlap(N, N′)` between two default rules of the same sign
both selecting (norms.md 4.2, unchanged).

### 4.2 The direct semantics `ValueSoft`: a terminating decision procedure on `T`

`ValueSoft_p(S, v̄)` is defined on the soft tree `T` itself, for a structure `S` over the symbols of `E′` strictly
below `p` in the dependency order of `T′` (5.2) and a typed tuple `v̄`, evaluated under W1's `tupleVal`. It never
refers to the elaboration. Every step is a finite Boolean evaluation: step 1 and step 4 recurse on the author
precedence DAG (well-founded by norms.md 4.1(3)); step 3 recurses strictly upward in the finite rank order.

```text
Step 0  In force.
        live_N(x̄) := G_N(x̄) ∧ ¬⋁U_N(x̄) ∧ ¬switch_N(x̄) ∧ [mode(N) = default] ¬excepted_N(x̄)
        A rule is live by its own terms only: guard, author carve-outs, its switches, its exception. No other rule
        occurs.

Step 1  Strict rules decide.
        T_s := the strict rules of T with the author precedence among them (by SoftOverHard, children(N) in T_s
        equals children(N) in T for strict N). With applies_N := live_N, W1's yields/selects over T_s give
          P^s_p(x̄) := ⋁_{N strict on p, sign +} selects_N(x̄)        N^s_p(x̄) := ⋁_{N strict on p, sign −} selects_N(x̄)

Step 2  Hard over soft.  A default rule N on p is blocked at x̄ when a strict rule decides the same act
        incompatibly or on the same predicate either way:
        blocked_N(x̄) := P^s_p(x̄) ∨ N^s_p(x̄)
                        ∨ [N requires, dual m declared]  N^s_m(x̄)        a strict rule forbids the act
                        ∨ [N forbids, dual r declared]   P^s_r(x̄)        a strict rule requires the act
        A strict rule that is itself overridden by a strict exception does not select and blocks nothing. A
        strict release does not block a default prohibition, and a strict permission does not block a default
        release: those effects are compatible (1.4).

Step 3  Dominance by rank.
        eligible_N(x̄) := live_N(x̄) ∧ ¬blocked_N(x̄)
        eff_N(x̄)      := eligible_N(x̄) ∧ ¬dominated_N(x̄)
        For {M, N} ∈ CP(T) on act a with Comparable(M, N), M dominates N at x̄, dom(M, N)(x̄), iff
          rank(M) outranks⁺ rank(N):   flag strict:    eff_M(x̄)
                                        flag holistic:  eff_M(x̄) ∧ ¬outweighs_{a,N,M}(x̄)
          rank(N) outranks⁺ rank(M):   flag strict:    never
                                        flag holistic:  eligible_M(x̄) ∧ outweighs_{a,M,N}(x̄)
        dominated_N(x̄) := ⋁_{M : {M,N} ∈ CP(T), Comparable(M,N)} dom(M, N)(x̄)
        Higher opponents must be effective; lower overriding opponents need only be eligible. eff_N depends on
        eff_M only for M strictly higher in outranks⁺, so the recursion is well-founded. An unranked default rule,
        or one whose opponents are all incomparable with it, is never dominated.

Step 4  Default rules decide.
        applies′_N := eff_N for default N, live_N for strict N; W1's yields′/selects′ over the author precedence
        DAG among all rules on p, where yields′_N ranges over all children of N, explicitly including strict
        children of default parents:
          yields′_N(x̄)  := applies′_N(x̄) ∨ ⋁_{E ∈ children(N)} yields′_E(x̄)
          selects′_N(x̄) := applies′_N(x̄) ∧ ¬⋁_{E ∈ children(N)} yields′_E(x̄)
        For strict N, selects′_N = selects_N of step 1 (its subtree is strict).
          P^d_p(x̄) := ⋁_{N default on p, sign +} selects′_N(x̄)     N^d_p(x̄) := ⋁_{N default on p, sign −} selects′_N(x̄)
          P′_p := P^s_p ∨ P^d_p                                    N′_p := N^s_p ∨ N^d_p
        ValueSoft_p(S, v̄) := some true   if P′_p and not N′_p at v̄
                            | some false  if N′_p and not P′_p
                            | some d_p    if neither                  (d_p the declared completion, norms.md 4.3)
                            | none        if both
```

Where a strict rule decides (`P^s_p ∨ N^s_p`), step 2 makes every default rule on `p` inapplicable, so `none` at a
point with a strict rule is a strict–strict collision, and `none` without one is a **weighing point**: two live,
unblocked, undominated default rules of opposite effect, neither excepted, both selecting after author precedence.
`some d_p` applies when no rule selects on `p`.

### 4.3 Existence: an eligible default guarantees an effective default

At a fixed act `a` and tuple `x̄`, if some default rule on `a` is eligible then some default rule on `a` is effective.
Proof: suppose none were effective. Among the eligible rules on `a` choose one, `N`, with no eligible rule on `a` of
strictly lower rank (it exists: the rank order is finite and acyclic, and unranked rules are never dominated, so if
one is eligible it is effective and we are done). `N` cannot be dominated by a higher opponent, since that requires an
effective rule; it cannot be dominated by a lower opponent, since that requires an eligible rule of lower rank. So
`N` is effective, a contradiction. This establishes existence before author precedence; it identifies no predetermined
winner and guarantees no selection on each predicate of the act (author precedence and same-sign overlap still
apply). The all-dominated case is unreachable, so `ValueSoft` needs no rule for it. The earlier claim "the
minimal-ranked eligible rule is never dominated" is false (under the strict flag a higher effective rule dominates
it) and is not used.

### 4.4 Why this is not circular (review A1)

The first plan draft made the higher rule an exception node of the lower one and gave the higher rule a carve-out
mentioning the lower rule's `selects`, so each rule's applicability depended on the other's selection: with both live
and `outweighs` true the equations were `H = ¬L`, `L = ¬H`, two solutions. Here blocking depends only on strict
selection (step 1, which never sees a default rule), and dominance depends on higher *effectiveness* and lower
*eligibility*, never on default selection after author precedence. With just `H` and `L` eligible on act `a`,
`rank(H) outranks⁺ rank(L)`, holistic, `outweighs_{a,L,H}` true: `H` is dominated (`eligible_L ∧ outweighs_{a,L,H}`),
`L` is not (`eff_H ∧ ¬outweighs_{a,L,H}` is false); `L` alone applies. One winner, by evaluation, not by fixpoint.
Two further cases the debate settled: a strictly blocked rule must not defeat a lower default (fixture λ), and a
defeated higher rule must not defeat a lower default (fixture κ); both follow from requiring `eff_M` of a higher
dominator.

### 4.5 Limit: collisions are same-act

Collisions are same-act: one predicate, or the declared obligation/permission pair of one act. "Help with the
request" versus "refuse the request" are different acts; their practical incompatibility is stage-3 material
(actions, fulfilment). This limit bites on the constitution: its hard constraints regulate their own acts (generate
CSAM, provide serious uplift), while most soft rules regulate complying, sharing, deceiving; `hard_over_soft`
resolves something there only where a soft rule regulates the same declared act. Status text always says "among
rules on the same act" (7.3). The four-property ordering has two encodings: ranks on rules over shared acts (this
profile), or norms.md 9.2's reified `follow(situation, property)` over `outranks(property, property)`; both stay in
the :34-37 reading set.

## 5. Elaboration `soften(T) = T′` over `E′`

### 5.1 One derived carve-out per rule, no derived precedence

`T′` keeps every rule's predicate, sign, guard and author `over` edges and adds at most one derived carve-out per
rule:

```text
derived_N := switch_N(x̄)                                                          strict N
derived_N := excepted_N(x̄) ∨ switch_N(x̄) ∨ blocked_N(x̄) ∨ dominated_N(x̄)           default N
carve-outs of N in T′ := U_N ++ [derived_N]      (omitted when derived_N is syntactically ⊥: a hard rule)
precedence of T′      := author precedence of T; no derived edges
regulated, definitions, completions of T′ := those of T; E′ as in 1.3
```

`blocked_N` and `dominated_N` are the formulas of 4.2, unfolded: `P^s_p`, `N^s_p`, `P^s_r`, `N^s_m` are W1's
selection formulas over the strict rules with `switch` as an extra carve-out; `dominated_N` inlines `eff_M` for every
comparable colliding `M`, in increasing rank height, and `eff_M` inlines `dominated_M` in turn until a rule with no
higher comparable opponent is reached. Author precedence is applied afterward, by W1's `yields`/`selects` on `T′`.
The derived carve-out is packed into one formula, so W1's limit of eight carve-outs per rule leaves seven to the
author. On a document whose rules are all hard, `T′ = T` byte for byte and `E′ = E` (fixture ξ).

`applies_{T′}(N) = G_N ∧ ¬⋁U_N ∧ ¬derived_N`, which is `live_N` for strict `N` and `eff_N` for default `N`; that is
`applies′_N` of step 4, and the precedence DAG is the same, so W1's `yields`/`selects` on `T′` are `yields′`/`selects′`
and W1's `Value` on `T′` is `ValueSoft` (theorem `soften_faithful`, 9.3).

### 5.2 Stratification on `T′` and `DualGuardCycle`

`T′` is a `norms@0` tree over `E′` and its stratification (norms.md 4.1(4)) is computed on `T′`. `blocked_N` and
`dominated_N` mention the guards, carve-outs, switch and decision atoms of other rules, including rules on the dual
predicate: a default rule on `r` whose derived carve-out mentions the strict rules on `m` needs those rules' guards to
lie strictly below `r`, and symmetrically. Guards over base predicates always satisfy this; a guard that mentions the
dual predicate itself can create a cycle on `T′` that is absent on `T`. Example: a strict `must not X` on `m` guarded
by "if it is not the case that S must X" (mentions `r`) and a default `should X` on `r`: on `T`, `m` sits above `r`;
on `T′` the default rule's `blocked` carve-out inlines `N^s_m`, hence the strict rule's guard, which mentions `r`, a
self-edge on `r`. (A strict `may X` with the same guard creates no cycle: a permission does not block a default
obligation, 4.2 step 2.) Same-predicate inlining never adds an edge, since a rule's guard already lies below its
predicate; the case is specific to the dual pair. The shared diagnostic text is W1's `DependencyCycle: <sorted
names>` (identical in Python and Lean); when the cycle is absent on `T`, the English layer attaches the rewrite hint
`DualGuardCycle`: "rule <k>'s guard mentions whether S must X, and rule <n> gives way to rule <k> on the same act;
restate rule <k>'s guard over the facts".

### 5.3 Size

Unfolded size is subject to `MAX_NODES` (10,000 nodes per formula, `ve/limits.py`); overflow is `ResourceLimit:
derived carve-out of rule <n>`, never a verdict. "Carve-out growth stays under `MAX_NODES`" is a pilot expectation,
not a theorem: `dominated_N` inlines `eff_M` for every higher colliding rule.

## 6. Decision assignments, coherence and what CONFLICT-FREE means (review A3)

### 6.1 Definitions

```text
decision assignment   the tables of the decision predicates (1.3) in a base structure B over E′
Exc_T                 the exception premises, one universally closed base formula per condition:
                        sufficient C of N:  ∀x̄. C(x̄) → excepted_N(x̄)         label soft:exception:<N>:sufficient:<i>
                        necessary  C of N:  ∀x̄. excepted_N(x̄) → C(x̄)         label soft:exception:<N>:necessary:<i>
Coh_T                 := ⋀_{{M,N} ∈ CP(T)} ∀x̄. ¬(selects′_M°(x̄) ∧ selects′_N°(x̄))
                        one universal base formula per colliding pair (° is W1's outcome substitution to E′_base,
                        norms.md 4.5), labelled soft:coherence:<a>,<b> with a < b the two rule names; regenerated from
                        the decoded document at every site and bound to the soft document hash, never taken from
                        the wire; defined over the whole syntactic CP(T), independently of any budget
Soft_T                := Exc_T ++ Coh_T                       the `soft` Background generator slot, after `profile`
Background_base′      := Background_base(E′) ++ Soft_T        (flags, literals, then the soft slot)
background′           := background(E′) ++ Soft_T             (definitions, literals, profile pairs, soft)
coherent B            := B ⊨ Coh_T                            all colliding default pairs have disjoint selections
BaseAdmissible′ E T B := BaseAdmissible E′ B ∧ Sat B Soft_T
```

`fragment: yes` iff `(E′, T′)` passes norms.md 7.1 and every generated `Exc_T`/`Coh_T` formula, after outcome
substitution and definition expansion, lies in the ordinary universal, function-free relational fragment with W1's
exclusions: no `Reach`, `$int` term, `Lt`/`Le` atom or adapter predicate. The syntactic gate for this version requires
every exception condition to be quantifier-free after definition expansion; `(E′, T′)` alone does not inspect these
separately stored conditions. Otherwise report `fragment: no (<first reason>)`, with an exception-condition failure
labelled `soft:exception:<N>:<kind>:<i>:<reason>`, retaining W1's three-valued status. Universal closure alone is
insufficient: a necessary condition `∃y. R(x,y)` yields `∀x. excepted_N(x) → ∃y. R(x,y)`, which need not survive
substructures. Under the complete gate, preservation of `Soft_T` under substructures is a proof obligation (9.3)
for applying norms.md 7's small-model machinery. `Exc_T` enters base admissibility exactly as flags do: it is the
author's declared constraint on base facts.

### 6.2 Classification of colliding pairs

```text
for {M, N} ∈ CP(T):
  RANK-RESOLVED   Comparable(M, N)                             theorem rank_resolves; no search; the conjunct is valid
  DISJOINT        certificate  Background_base(E′) ++ Exc_T ⊢ ∀x̄. ¬(selects′_M°(x̄) ∧ selects′_N°(x̄))
                                                               no coherence conjunct is assumed
  WEIGHING POINT  checked witness (B, ā) over E′_base, B ⊨ Background_base(E′) ++ Exc_T, both selecting;
                  shown as a situation with its decision assignment in document terms
  UNKNOWN         neither within budget; the budget named
WP(T)             := the WEIGHING POINT and UNKNOWN pairs (the undischarged conjuncts)
```

`Coh_T` has exactly one conjunct per pair in `CP(T)` whatever the budget. RANK-RESOLVED conjuncts are theorems and
DISJOINT conjuncts follow from their certificates over `Background_base(E′) ++ Exc_T`, excluding **all** coherence
conjuncts so that none can discharge another circularly (fixture τ). Conflict checking still uses full
`Background_base′`. Classification marks these as *discharged* without changing the
route's coherence condition or requiring classifications to be replayed to regenerate it (debate group 2). A
WEIGHING POINT witness is exactly a countermodel to the *unconditional* conflict-freedom claim, and the report shows
it as such.

### 6.3 What the soft route certifies

The first plan draft claimed W1's guarantees would be inherited by replaying the strict core and the DISJOINT
certificates. That was wrong: at a weighing point with both exceptions false, `T′` elaborates to contradictory
requirements, `elab_p` is false there, and W1's unique-expansion premise fails for that base structure; no report
restores it. What holds, and what the soft route certifies, is the following.

- `coherent_expands` (W1's pointwise `conflictFree_expands_document` applied to `T′`; reused, not restated): for every
  base `B` over `E′` with `BaseAdmissible E′ B`, `Unique(DocumentExpansion E′ T′ B) ↔ ConflictFree E′ T′ B`. A
  coherent assignment that also avoids the conflicts below has exactly one expansion; an incoherent one has none.
  The hypothesis is W1's `BaseAdmissible` (Astra round 1, item 1), not `BaseAdmissible′`.
- `soft_conflict_decomposition`: for `B` with `BaseAdmissible E′ B`,
  `ConflictFree E′ T′ B ↔ NoStrictCollision(B) ∧ NoHardPairConflict(B) ∧ Sat B Coh_T`, where

  ```text
  NoStrictCollision(B)   := ∀p ∀x̄. ¬(P^s_p°(x̄) ∧ N^s_p°(x̄))
  NoHardPairConflict(B)  := ∀(r,m) ∀x̄. ¬(O_r°(x̄) ∧ ¬O_m°(x̄) ∧ ¬(P^d_r°(x̄) ∧ N^d_m°(x̄)))
                            no pair conflict point unless both sides come from default rules
  ```

  The `→` direction: an intra-predicate conflict is strict–strict or default–default by `hard_over_soft`, and a
  default–default one is a same-predicate pair of `CP(T)` both selecting (`weighing_points_complete`); a pair conflict
  with both sides default is a cross pair of `CP(T)` both selecting. The `←` direction: `Coh_T` excludes exactly the
  default–default cases. Hence every collision in a coherent `B` is strict–strict on one predicate, or a pair conflict
  with a strict rule or a completion on at least one side; and no default–default collision is at a discharged pair in
  an admissible base.
- **What CONFLICT-FREE certifies.** `soft_conflict_free := ∀B. BaseAdmissible′ E T B → ConflictFree E′ T′ B`, checked
  by W1's unchanged conflict machinery (tableau per target, witness search, evaluator) on `T′` over
  `Background_base′`. In words: under any decision assignment that resolves the listed weighing points and satisfies
  the declared exception conditions, every situation has exactly one outcome for every regulated act. By the
  decomposition this is exactly "no strict collision and no hard pair conflict in any coherent situation".

### 6.4 Conditional guarantees

The soft route's acceptance and countermodel theorems are W1's `norms_route_acceptance` and `norms_route_countermodel`
restated with `BaseAdmissible′` (9.3). The frozen P0 `Layer` takes the first layer's `Admissible_in` as a parameter,
so `Soft_T` enters through it: the soft chain's prefix admissibility is W1's with `Sat (restrictAll S) Soft_T`
conjoined at every prefix, and `BackgroundSound`/`BackgroundComplete` hold for `background′`. A certified conclusion
holds in every situation whose decision assignment is coherent and satisfies the report's other assumptions; a
countermodel is a coherent base situation, rendered with its decision assignment in document terms ("rule 12 is
excepted here; rule 4 is not; on complying with this operator instruction, helpfulness outweighs ethics", the
act-indexed atom for rules 4 and 21).

Every soft report states the route's full `Coh_T` separately from `conditional_on: soft:coherence:<a>,<b> ...`, which
lists only the undischarged coherence premises (`WP(T)`) among the certificate's used leaves. The used-leaf list
records those dependencies, as bridge leaves are shown today.

### 6.5 Vacuity

1. The P0 vacuity report (PLAN-EXPAND2 3.8; document.md) runs over the certificate's actual premise set,
   `background′ ++ layer premises ++ Γ` in full `E′`, including definitions and profile constraints. A `Γ` that
   fixes decision facts incompatible with `Coh_T` or `Exc_T` makes dependent certificates `vacuous`, visibly
   (fixture ι).
2. A CONFLICT-FREE report also exhibits a checked finite model of `background′ ++ layer premises ++ Γ` in full
   `E′` (the P0 premise-set model), displaying its `E′_base` restriction as the coherent decision assignment.
   It reports inconsistent or UNKNOWN with the budget when appropriate; without a model the conditional claim
   could be about no situation at all. The status text carries the answer (7.3).
3. A default rule alone proves nothing about its act unless the premises constrain `excepted_N`; that is the intended
   content of "should", and the report says so rather than hiding it (plan risk 7).

### 6.6 Completion outcomes

Pair conflicts in which one side is a completion default are CONFLICT, as in W1 10.1(a,b): a default obligation that
selects where the act's permission is deny-by-default and nothing permits it, or a default prohibition that selects
where the act is required by default. `soften` does not carve defaults out on completions; doing so would make every
default obligation vacuous under a deny default, and the completion is the environment's legend, not a rule that can
dominate (plan 7.1). The witness names the completion ("rule 12 requires sharing here; by default an assistant may
not share; no rule permits it"); the author's fix is one sentence (`may X`, or an allow default).

### 6.7 Override cycles

Under the holistic flag define the findings tournament on colliding comparable pairs at `x̄`:

```text
pref_a(M, N)(x̄) := rank(M) outranks⁺ rank(N) ∧ ¬outweighs_{a,N,M}(x̄)      the higher M is preferred as ranked
                 ∨ rank(N) outranks⁺ rank(M) ∧  outweighs_{a,M,N}(x̄)      the lower M is found to outweigh N
```

An **override cycle** at a situation is a cycle of `pref_a` among eligible default rules on `a` where consecutive
rules collide. Example: four eligible defaults on `a`, ranks `A > B > C > D`, `A`/`C` requiring and `B`/`D`
releasing (colliding pairs `A–B`, `B–C`, `C–D`, `A–D`: an alternating collision cycle, not four pairwise-colliding
rules, which the bipartite relation excludes), findings `outweighs_{a,B,A} ∧ outweighs_{a,C,B} ∧ outweighs_{a,D,C} ∧
¬outweighs_{a,D,A}`. `pref` runs `B ≻ A`, `C ≻ B`, `D ≻ C`, `A ≻ D`. `ValueSoft` is still determined: `D` alone is
effective (fixture ε). The report's `override_cycles` line is a diagnostic warning with the witness situation, not an
additional assumed obligation; `Coh_T` contains no ban on such cycles (debate group 4).

## 7. The report

### 7.1 The four questions

| Question | Method | Result |
|---|---|---|
| Which default rules can collide, and is each collision resolved? | for each `{M, N} ∈ CP(T)`: `rank_resolves`, else certificate, else witness (6.2) | per pair RANK-RESOLVED / DISJOINT / WEIGHING POINT (situation; condition `¬(selects′_M ∧ selects′_N)` there) / UNKNOWN; the discharged conjuncts of the budget-independent `Coh_T` and the remaining `WP(T)` |
| Can the rules contradict each other under a coherent decision assignment? | W1 conflict check on `T′` over `Background_base′`, unchanged functions | CONFLICT (witness classified: strict collision / pair conflict with a strict rule or a completion) / CONFLICT-FREE conditional on `Coh_T` (certificates, `conditional_on`, one coherent model or UNKNOWN) / UNKNOWN |
| Are the priorities consistent? | closure of `outranks` through `dependencyOrder`; declared ties; author edges against rank | acyclic / `DependencyCycle: <ranks>`; `TieAgainstOrder`; undeclared ties listed; `RankAgainstPrecedence` warnings |
| Who can change each rule? | switches; attribution cone check (7.4) | per rule: the parties with a switch; per other party: whether any predicate attributed to it occurs in the rule's cone |

Weighing points and coherence premises are residual items (VISION.md 2), each with its resolution: `open` (the two
rules must not both select; exceptions, switches, guard or author carve-out conditions, strict blocking, dominance by
other rules or author precedence can prevent selection), `rank: ethics over helpfulness (holistic)` (pairwise defeat
resolved by structure; the act-indexed `outweighs` term is in the residual), `strict` (no residual). Reports show the
actual selection-disjointness condition, never a requirement that one exception must hold. The checker does not
invent decision criteria (document.md).

### 7.2 Residual lines (W2 coverage, item 5)

Beside open terms, assumptions, bridge leaves and unresolved reading sets: `default_exceptions` (distinct
`excepted_N` terms, grouped by decider, `unstated` counted separately), `weighing_points` (each with resolution and
its selection-disjointness condition), `holistic_overrides` (distinct `outweighs_{a,L,H}` terms, by decider),
`override_cycles` (warnings with situations), `coherence_premises_used` (per certificate, the `conditional_on` list),
`narrowings` (with citations). A default rule is OPEN with `{"open": ["excepted_n", ...]}`; ranking sentences are
CHECKED; the holistic flag with its `outweighs` terms is OPEN. No new status.

### 7.3 Status text

```text
CONFLICT-FREE among rules on the same act, conditional on <k> coherence premises (<labels>); <j> weighing points open;
coherent situation exhibited: yes | UNKNOWN (<budget>)
CONFLICT: <witness kind> at <situation>            witness kind ∈ {strict collision on <p>, pair conflict on <act> with
                                                   <strict rule | completion> against <rule>}
UNKNOWN: <target>, <budget>
```

A witness of the unconditional claim (a weighing point) is shown under the first question, never as CONFLICT.

### 7.4 Authority, scoped (review B1)

For each rule, exactly the declared parties have a switch: there is no other `off` predicate to set, and a `Γ` that
names one is `UnknownSymbol`. Separately, an attribution check per regulated `p` and party `π`: let `cone(p)` be the
set of predicates reachable from the rules on `p` in `T′` through guards, carve-outs (including derived ones),
definition bodies and the rules of lower regulated predicates, also closing transitively over the predicates in
every declared sufficient or necessary condition of each `excepted_N` in the cone. Let `Q_π` be the predicates with
`instruction_of = π` together with every `off_{N,π}`. If `Q_π ∩ cone(p) = ∅` then `O_p°` is invariant under changes to `Q_π`
(`authority_independent`, a non-mention lemma); the report line is `independent of <π>`. Otherwise the line lists the
`Q_π` predicates in the cone and makes no claim. The certificate is about *declared* attribution only. It says nothing
about whether a decider of `excepted_N` or `outweighs` takes `π`'s instructions into account, and nothing about base
facts the environment did not attribute; the report states both limits next to the result.

## 8. Diagnostics

Soft rejection responses carry a stable `code` alongside the human-readable `error`.
Python soft validation exceptions expose the same value as `VEError.code` and in
`VEError.to_dict()`. The code, rather than message wording or embedded names, is
the Python/Lean conformance contract. Existing P0 and W1 responses keep their
codes. This is the complete soft code table; the last row covers inherited W1
and malformed-input diagnostics on the soft route.

| Code | Rejection class |
|---|---|
| `SOFT_MISSING_EXCEPTION` | Default rule has no complete exception object. |
| `SOFT_INVALID_TIES_PAIR` | Malformed, reflexive, or repeated ordered ties pair. |
| `SOFT_INVALID_OUTRANKS_PAIR` | Malformed, reflexive, or repeated outranks pair. |
| `SOFT_INVALID_BLOCK` | Soft block has invalid fields or shape. |
| `SOFT_INVALID_OUTRANKING` | Outranking flag has invalid fields, shape, or mode. |
| `SOFT_INVALID_DECIDER` | Present decider has invalid type, length, or value. |
| `SOFT_MISSING_DECIDER` | Required outranking or exception decider is absent. |
| `SOFT_STRICT_OUTRANKING_DECIDER` | Strict outranking declares a decider. |
| `SOFT_INVALID_NAME` | Invalid soft declaration or reserved name. |
| `SOFT_DUPLICATE_DECLARATION` | Duplicate party, rank, or unordered tie. |
| `SOFT_UNKNOWN_RANK` | Rank reference is undeclared. |
| `SOFT_TIE_AGAINST_ORDER` | Tie contradicts strict outranking. |
| `SOFT_DEPENDENCY_CYCLE` | Rank or unfolded norm dependency cycle. |
| `SOFT_UNKNOWN_PARTY` | Party reference is undeclared. |
| `SOFT_STRICT_EXCEPTION` | Strict rule declares an exception. |
| `SOFT_EXCEPTION_ARRAY` | Sufficient or necessary field is not an array. |
| `SOFT_INVALID_FACTORS` | Exception factors have invalid shape or size. |
| `SOFT_INVALID_ALTERABLE` | Alterable parties are unsorted, repeated, or malformed. |
| `SOFT_HARD_CONSTRAINT` | A hard rule is default or alterable. |
| `SOFT_INVALID_EXCEPTION_CONDITION` | Exception condition mentions a forbidden predicate. |
| `SOFT_OVER_HARD` | Default rule takes precedence over strict rule. |
| `SOFT_RESOURCE_LIMIT` | A soft route resource limit is exceeded. |
| `SOFT_UNSUPPORTED_PROFILE` | Soft route profile gate fails. |
| `SOFT_INVALID_ARRAY` | A soft block list has the wrong shape. |
| `SOFT_INVALID_RULE_FIELDS` | Mode, rank, hard, or another typed soft rule field is invalid. |
| `SOFT_INVALID_INPUT` | Other invalid input, including inherited W1 checks. |

The code table is ordered: where several descriptions match an error, the
first applicable class wins. New soft rejection paths must be assigned a
specific code or intentionally use `SOFT_INVALID_INPUT` in both validators.

### Human-readable diagnostics

| Text | When | Kind |
|---|---|---|
| `SoftOverHard: rule <n> over <m>` | default `n` takes precedence over strict `m` (4.1(5)) | error |
| `UnknownRank: rule <n>, <rank>` / `UnknownRank: <rank>` | undeclared rank on a rule / in `outranks` or `ties` | error |
| `MissingExceptionDecider: rule <n>` / `MissingExceptionDecider: outranking` | default rule with no decider at rule or document level / `holistic` without a decider | error |
| `TieAgainstOrder: <a>, <b>` | declared tie between comparable ranks | error |
| `DependencyCycle: <sorted rank names>` | `outranks` not acyclic (W1's shared text) | error |
| `DependencyCycle: <sorted names>` + hint `DualGuardCycle` (English layer only) | stratification cycle on `T′` absent on `T` (5.2) | error |
| `HardConstraintAltered: rule <n>` | `hard: true` with `mode: default` or a switch | error |
| `UnknownSymbol: party <π>` | undeclared party in `alterable` or `instruction_of` | error |
| `DuplicateDeclaration: rank <a>` / `party <π>` | duplicate names in the `soft` block | error |
| `InvalidInput: rule <n> is strict and declares an exception` / `exception condition of rule <n> mentions <q>` / `invalid soft fields for <n>` / `instruction_of on <p>` | field consistency (3.1, 3.2) | error |
| `ResourceLimit: derived carve-out of rule <n>` / `ResourceLimit: ranks` / `ResourceLimit: parties` | `MAX_NODES` on unfolding; more than 16 ranks; more than 8 parties | error |
| `UnsupportedProfile: soft-norms@0 requires norms@0` | profile gate | error |
| `RankAgainstPrecedence: rule <n> over <m>` | author edge against the ranks (4.1) | warning |
| `Overlap(<n>, <m>)` | two same-sign rules both selecting (W1) | warning |
| undeclared ties, `override_cycles` | report lines (1.2, 6.7) | warning |

Diagnostics follow W1's check order (norms.md 11.1, `lean/NORMS.md` conventions): environment declarations, then
W1's rule checks, then the soft rule checks in document order (mode and fields, rank, parties, decider, `hard`,
exception typing), then `over` against modes, then ranks and ties, then the unfolded `T′` size and its DAG. English
diagnostics carry the span and the plain-language expectation as today. Existing P0 and W1 diagnostics are unchanged.

## 9. Lean (item 4): definitions and the exact statements to prove

Files: `lean/VE/SoftNorms/Tree.lean` (syntax, `WellFormedSoft`, decision vocabulary, `E′`), `Soften.lean`
(`soften`, derived carve-outs, shape lemmas), `Semantics.lean` (`ValueSoft`, the direct predicates, `hard_over_soft`,
`rank_resolves`, existence, independence), `Coherence.lean` (`Exc_T`, `Coh_T`, `BaseAdmissible′`, decomposition,
`soft_conflict_free`, the restated route), `Status.lean` (classification and its soundness), `Wire.lean`,
`Admission.lean`, `Run.lean` (the `ve_soft_norms_route` executable), and `lean/SOFT-NORMS.md` listing each theorem in
plain words. Frozen `Norms/*`, `Route/*` and all P0 sources are untouched; `VE.lean`, `VE/Audit.lean` and
`lakefile.toml` gain imports, audit entries and the new target only; the audit allowlist is unchanged. Names below
have prefix `VE.SoftNorms.`; W1 names are `VE.Norms.*` as in `lean/NORMS.md`. The blocks are statement schemata:
helper names are defined here, not already implemented Lean.

### 9.1 Definitions

```lean
namespace VE.SoftNorms
open VE.Norms (Regulated Definition Node Tree Doc Pair pairs rulesOn children tupleVal Sat forget hide
  atom bindAll anyF allF catalaValue envAt size before subst restrictAll outcomeBase conflict pairConflict)

inductive Mode | strict | default
inductive Outranking | strict | holistic

structure Exception where
  decidedBy  : Option String        -- none = inherit; some "unstated" allowed
  sufficient : List VE.Formula      -- context (sorts pred).reverse, base predicates of E only
  necessary  : List VE.Formula
  factors    : List String

structure SoftNode extends Node where
  mode      : Mode
  rank      : Option String
  alterable : List String           -- sorted, distinct declared parties
  exception : Option Exception      -- some iff mode = default
  hard      : Bool

structure SoftEnv where
  parties          : List String
  ranks            : List String
  outranks         : List (String × String)
  ties             : List (String × String)
  outranking       : Outranking
  outrankingDecider : Option String
  exceptionDecider : Option String
  instructionOf    : List (String × String)   -- base predicate ↦ party

structure SoftTree where
  regulated   : List Regulated
  definitions : List Definition
  nodes       : List SoftNode

structure SoftDoc where
  E    : VE.Environment
  lits : List String
  soft : SoftEnv
  T    : SoftTree

def outranksPlus (env : SoftEnv) : String → String → Bool          -- transitive closure of the declared edges
def rankHeight (D : SoftDoc) (N : SoftNode) : Nat                 -- longest ascending outranks⁺ chain above rk N
def rankNodes (env : SoftEnv) : List VE.Route.DepNode              -- a → b for each "a outranks b"
def Comparable (D : SoftDoc) (M N : SoftNode) : Bool
def actKey (D : SoftDoc) (p : String) : String                     -- 1.3
def Incompatible (D : SoftDoc) (M N : SoftNode) : Bool             -- 1.4
def collidingPairs (D : SoftDoc) : List (SoftNode × SoftNode)      -- CP(T), each unordered pair once, names sorted
def exceptedName (N : SoftNode) : String                           -- soft__excepted__<rule>
def offName (N : SoftNode) (π : String) : String                   -- soft__off__<rule>__<party>
def outweighsName (a L H : String) : String                        -- soft__outweighs__<L>__<H>__<act key>
def decisions (D : SoftDoc) : List (String × List String)          -- every decision predicate with its sorts
def envPrime (D : SoftDoc) : VE.Environment                        -- E′ = E + decisions
def decisionNames (D : SoftDoc) : List String
def weighingSyms (D : SoftDoc) : List String                       -- excepted, outweighs, off of default rules
def attributed (D : SoftDoc) (π : String) : List String            -- instruction_of = π, plus every off_{N,π}

/-- 4.1: the soft checks, then Norms.WellFormed on the unfolded T′ (so DualGuardCycle and size surface there). -/
def WellFormedSoft (D : SoftDoc) : Bool

/-- 5.1: total; on a well-formed input the real elaboration, otherwise a junk document. -/
def switchF (D : SoftDoc) (N : SoftNode) : VE.Formula
def exceptedF (D : SoftDoc) (N : SoftNode) : VE.Formula
def strictPos (D : SoftDoc) (p : String) : VE.Formula              -- P^s_p, W1 selects over the strict rules with switch carve-outs
def strictNeg (D : SoftDoc) (p : String) : VE.Formula
def blockedF (D : SoftDoc) (N : SoftNode) : VE.Formula
def eligibleF (D : SoftDoc) (N : SoftNode) : VE.Formula
def effF (D : SoftDoc) : Nat → SoftNode → VE.Formula               -- fuel = ranks.length + 1
def dominatedF (D : SoftDoc) : Nat → SoftNode → VE.Formula
def derived (D : SoftDoc) (N : SoftNode) : VE.Formula
def derivedList (D : SoftDoc) (N : SoftNode) : List VE.Formula     -- [] when N is strict and unswitchable
def soften (D : SoftDoc) : Doc                                     -- ⟨envPrime D, D.lits, T′⟩

/-- 6.1 -/
def excPremises (D : SoftDoc) : List VE.Formula
def primeNode (D : SoftDoc) (N : SoftNode) : Node := { N.toNode with carveOuts := N.carveOuts ++ derivedList D N }
def selects' (D : SoftDoc) (N : SoftNode) : VE.Formula :=          -- selects′_N, W1's selects on T′
  VE.Norms.selects (soften D).T (VE.Norms.fuel (soften D).T) (primeNode D N)
def cohPremise (D : SoftDoc) (M N : SoftNode) : VE.Formula :=
  bindAll (actSorts D M) (.not (.and (subst (soften D).T (size (soften D)) (selects' D M))
                                     (subst (soften D).T (size (soften D)) (selects' D N))))
def cohPremises (D : SoftDoc) : List VE.Formula := (collidingPairs D).map (fun (M, N) => cohPremise D M N)
def softPremises (D : SoftDoc) : List VE.Formula := excPremises D ++ cohPremises D
/-- The complete syntactic fragment gate of 6.1, including the separately generated soft premises. -/
def InFragment (D : SoftDoc) : Bool
def backgroundBase' (D : SoftDoc) : List VE.Formula := VE.Norms.backgroundBase (soften D) ++ softPremises D
def background' (D : SoftDoc) : List VE.Formula := VE.Norms.background (soften D) ++ softPremises D
def BaseAdmissible' (D : SoftDoc) (B : VE.Structure) : Prop :=
  VE.Norms.BaseAdmissible (soften D) B ∧ Sat B (softPremises D)
def PrefixAdmissible' (D : SoftDoc) (k : Nat) (S : VE.Structure) : Prop :=
  VE.Norms.PrefixAdmissible (soften D) k S ∧ Sat (restrictAll (soften D).T S) (softPremises D)

/-- 4.2, the direct semantics as propositions, mirroring W1's AppliesD/YieldsD/SelectsD/DecidesD. -/
section Direct
variable (D : SoftDoc) (S : VE.Structure) (ρ : VE.Valuation S)
def LiveD (N : SoftNode) : Prop :=
  N.guard.denote S ρ ∧ ¬ (∃ U ∈ N.carveOuts, U.denote S ρ) ∧ ¬ (switchF D N).denote S ρ ∧
  (N.mode = .default → ¬ (exceptedF D N).denote S ρ)
def StrictYieldsD : Nat → SoftNode → Prop
  | 0, N => N.mode = .strict ∧ LiveD D S ρ N
  | f + 1, N => (N.mode = .strict ∧ LiveD D S ρ N) ∨ ∃ C ∈ children D N, StrictYieldsD f C
def StrictSelectsD (f : Nat) (N : SoftNode) : Prop :=
  N.mode = .strict ∧ LiveD D S ρ N ∧ ¬ ∃ C ∈ children D N, StrictYieldsD D S ρ f C
def StrictDecidesD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn D p, N.sign = sign ∧ StrictSelectsD D S ρ (fuel D) N
def BlockedD (N : SoftNode) : Prop :=
  StrictDecidesD D S ρ N.pred true ∨ StrictDecidesD D S ρ N.pred false ∨
  (N.sign = true  ∧ ∃ m, dualPerm D N.pred = some m ∧ StrictDecidesD D S ρ m false) ∨
  (N.sign = false ∧ ∃ r, dualOblig D N.pred = some r ∧ StrictDecidesD D S ρ r true)
def EligibleD (N : SoftNode) : Prop := N.mode = .default ∧ LiveD D S ρ N ∧ ¬ BlockedD D S ρ N
def OutweighsD (a L H : String) : Prop := (atom (outweighsName a L H) (actSortsOf D a)).denote S ρ
mutual
  def EffD : Nat → SoftNode → Prop
    | 0, N => EligibleD D S ρ N
    | g + 1, N => EligibleD D S ρ N ∧ ¬ DominatedD g N
  def DominatedD : Nat → SoftNode → Prop
    | g, N => ∃ M ∈ D.T.nodes, Incompatible D M N ∧ M.mode = .default ∧ Comparable D M N ∧
      ((higher D M N ∧ EffD g M ∧ (D.soft.outranking = .holistic → ¬ OutweighsD D S ρ (act N) (rk N) (rk M))) ∨
       (D.soft.outranking = .holistic ∧ higher D N M ∧ EligibleD D S ρ M ∧ OutweighsD D S ρ (act N) (rk M) (rk N)))
end
def AppliesSoftD (N : SoftNode) : Prop :=
  match N.mode with | .strict => LiveD D S ρ N | .default => EffD D S ρ (rankFuel D) N
def YieldsSoftD : Nat → SoftNode → Prop
  | 0, N => AppliesSoftD D S ρ N
  | f + 1, N => AppliesSoftD D S ρ N ∨ ∃ C ∈ children D N, YieldsSoftD f C
def SelectsSoftD (f : Nat) (N : SoftNode) : Prop :=
  AppliesSoftD D S ρ N ∧ ¬ ∃ C ∈ children D N, YieldsSoftD D S ρ f C
def DecidesSoftD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn D p, N.sign = sign ∧ SelectsSoftD D S ρ (fuel D) N
def DefaultDecidesD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn D p, N.mode = .default ∧ N.sign = sign ∧ SelectsSoftD D S ρ (fuel D) N
end Direct

noncomputable def ValueSoft (D : SoftDoc) (r : Regulated) (S : VE.Structure) (vs : List S.Carrier) : Option Bool :=
  catalaValue (DecidesSoftD D S (tupleVal vs) r.name true) (DecidesSoftD D S (tupleVal vs) r.name false)
    r.allowByDefault
def IntendedSoftAt (D : SoftDoc) (r : Regulated) (S : VE.Structure) : Prop :=
  ∀ vs, VE.TupleTyped S r.sorts vs →
    ∃ b, ValueSoft D r (forget [r.name] S) vs = some b ∧ (S.relation r.name vs ↔ b = true)
def holdsSoft (D : SoftDoc) (S : VE.Structure) : Prop := ∀ r ∈ D.T.regulated, IntendedSoftAt D r S

/-- 6.3 -/
def NoStrictCollision (D : SoftDoc) (B : VE.Structure) : Prop :=
  ∀ r ∈ D.T.regulated, ∀ vs, VE.TupleTyped B r.sorts vs →
    ¬ ((subst (soften D).T (size (soften D)) (.and (strictPos D r.name) (strictNeg D r.name))).denote B (tupleVal vs))
def NoHardPairConflict (D : SoftDoc) (B : VE.Structure) : Prop :=
  ∀ pr ∈ pairs (soften D).T, ∀ vs, VE.TupleTyped B pr.sorts vs →
    ¬ ((pairConflict (soften D) pr).denote B (tupleVal vs) ∧
       ¬ (subst (soften D).T (size (soften D)) (.and (defaultPos D pr.req) (defaultNeg D pr.perm))).denote B (tupleVal vs))
def SoftConflictFree (D : SoftDoc) : Prop :=
  ∀ B : VE.Structure, BaseAdmissible' D B → VE.Norms.ConflictFree (soften D) B

/-- 7.4: predicates reached through T′ guards, carve-outs, definitions and lower regulated rules;
    transitively include predicates of every sufficient/necessary condition of each excepted_N reached. -/
def cone (D : SoftDoc) (p : String) : List String
```

`fuel D` is `D.T.nodes.length` (W1's precedence fuel); `rankFuel D` is `D.soft.ranks.length + 1`; `higher D M N`
is `outranksPlus D.soft (rk M) (rk N)` on ranked rules; `rk`, `act`, `actSorts`, `dualPerm`, `dualOblig` read the
declarations. `defaultPos`/`defaultNeg` are `P^d_p`/`N^d_p` as formulas on `T′` (W1 `selects` restricted to default
rules). The tuple convention is W1's: relation tuples in argument order, `tupleVal` for valuations, `[]` for closed
formulas. `rankHeight D N` is the maximum number of strict ascending `outranks⁺` steps starting at `rk N`,
over declared ranks (zero for an unranked rule or a rank with no higher rank). For a well-formed document and
`N ∈ D.T.nodes`, `rankHeight D N < rankFuel D`; node-specific fuel stability assumes that same membership.

### 9.2 Theorems: elaboration and the direct semantics

```lean
/-- 4.1 ⇒ W1 well-formedness of T′ over E′. -/
theorem soften_wellFormed (D : SoftDoc) (h : WellFormedSoft D = true) :
  VE.Norms.WellFormed (soften D) = true

/-- 5.1: what soften changes and what it keeps. -/
theorem soften_shape (D : SoftDoc) (h : WellFormedSoft D = true) :
  (soften D).E = envPrime D ∧ (soften D).lits = D.lits ∧
  (soften D).T.regulated = D.T.regulated ∧ (soften D).T.definitions = D.T.definitions ∧
  (soften D).T.nodes = D.T.nodes.map (fun N => { N.toNode with carveOuts := N.carveOuts ++ derivedList D N })

/-- All-hard documents elaborate to themselves (fixture ξ). -/
theorem soften_hard_identity (D : SoftDoc) (h : WellFormedSoft D = true)
    (hh : ∀ N ∈ D.T.nodes, N.mode = .strict ∧ N.alterable = []) :
  envPrime D = D.E ∧ (soften D).T.nodes = D.T.nodes.map SoftNode.toNode

/-- Every generated soft formula denotes its direct-semantics counterpart (W1's *_denote pattern). -/
theorem live_denote (D) (N) (S) (ρ) : (liveF D N).denote S ρ ↔ LiveD D S ρ N
theorem strictDecides_denote (D) (p) (sign) (S) (ρ) : (strictDecidesF D p sign).denote S ρ ↔ StrictDecidesD D S ρ p sign
theorem blocked_denote (D) (N) (S) (ρ) : (blockedF D N).denote S ρ ↔ BlockedD D S ρ N
theorem eff_denote (D) (g) (N) (S) (ρ) : (effF D g N).denote S ρ ↔ EffD D S ρ g N
theorem derived_denote (D) (N) (S) (ρ) :
  (VE.Norms.applies { N.toNode with carveOuts := N.carveOuts ++ derivedList D N }).denote S ρ ↔ AppliesSoftD D S ρ N

/-- Fuel stability: for a well-formed document the rank recursion is stable at rankFuel. -/
theorem eff_fuel (D : SoftDoc) (h : WellFormedSoft D = true) (S) (ρ) (N : SoftNode) (hN : N ∈ D.T.nodes)
    (g : Nat) (hg : rankHeight D N < g) : EffD D S ρ g N ↔ EffD D S ρ (rankFuel D) N

/-- 5.1: W1's Value on T′ is ValueSoft on T, on every structure and tuple. -/
theorem soften_faithful (D : SoftDoc) (h : WellFormedSoft D = true) (r : Regulated) (hr : r ∈ D.T.regulated)
    (S : VE.Structure) (vs : List S.Carrier) :
  VE.Norms.Value (soften D).T r S vs = ValueSoft D r S vs

theorem soft_intended_iff (D) (h) (r) (hr) (S) : VE.Norms.IntendedAt (soften D).T r S ↔ IntendedSoftAt D r S
theorem soft_elaborate_iff (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure) :
  Sat S (VE.Norms.elaborate (soften D).T) ↔ holdsSoft D S

/-- 4.3: an eligible default guarantees an effective default on the same act, before author precedence. -/
theorem eligible_effective (D : SoftDoc) (h : WellFormedSoft D = true) (S) (ρ) (a : String)
    (hex : ∃ N ∈ rulesOnAct D a, EligibleD D S ρ N) :
  ∃ N ∈ rulesOnAct D a, EffD D S ρ (rankFuel D) N

/-- 4.2 step 2 as a theorem about soften: a strict decision silences every default on the predicate, and a strict
    decision against a default's effect across the pair silences it. -/
theorem hard_over_soft (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure) (ρ : VE.Valuation S) :
  (∀ p sign, StrictDecidesD D S ρ p sign → ¬ DefaultDecidesD D S ρ p true ∧ ¬ DefaultDecidesD D S ρ p false) ∧
  (∀ pr ∈ pairs (soften D).T, StrictDecidesD D S ρ pr.perm false → ¬ DefaultDecidesD D S ρ pr.req true) ∧
  (∀ pr ∈ pairs (soften D).T, StrictDecidesD D S ρ pr.req true → ¬ DefaultDecidesD D S ρ pr.perm false)

/-- Its base-formula corollary: no conflict point of T′ has a strict rule on one side and a default rule on the
    other, on one predicate or across a pair. -/
theorem hard_over_soft_base (D) (h) (B : VE.Structure) (vs) :
  (∀ r ∈ D.T.regulated, ¬ ((strictPos D r.name)° ∧ (defaultNeg D r.name)°).denote B (tupleVal vs) ∧
                        ¬ ((defaultPos D r.name)° ∧ (strictNeg D r.name)°).denote B (tupleVal vs)) ∧
  (∀ pr ∈ pairs (soften D).T, ¬ ((defaultPos D pr.req)° ∧ (strictNeg D pr.perm)°).denote B (tupleVal vs) ∧
                              ¬ ((strictPos D pr.req)° ∧ (defaultNeg D pr.perm)°).denote B (tupleVal vs))
  -- φ° abbreviates subst (soften D).T (size (soften D)) φ

/-- Local weighing independence: strict selection on p reads neither ranks, the flag, outweighs, exceptions nor the
    switches of default rules. (i) syntactically; (ii) semantically, in the form of W1's denote_relation_congr. -/
theorem hard_never_weighed (D : SoftDoc) (h : WellFormedSoft D = true) (p : String) (sign : Bool) :
  (∀ q ∈ VE.Norms.preds (strictDecidesF D p sign), q ∉ weighingSyms D) ∧
  (∀ (D₂ : SoftDoc), sameStrictCore D D₂ → strictDecidesF D₂ p sign = strictDecidesF D p sign) ∧
  (∀ (S : VE.Structure) (R : String → List S.Carrier → Prop)
     (hR : ∀ q vs, q ∉ weighingSyms D → (R q vs ↔ S.relation q vs)) (ρ : VE.Valuation S),
     StrictDecidesD D { S with relation := R } ρ p sign ↔ StrictDecidesD D S ρ p sign)
  -- sameStrictCore: same E, lits, regulated, definitions, and same nodes up to rank, exception and the
  -- alterable lists of default rules; ranks, outranks, ties and the flag may differ.

/-- The general non-mention lemma behind the two global claims. -/
theorem cone_independent (D : SoftDoc) (h : WellFormedSoft D = true) (p : String) (hp : p ∈ VE.Norms.regulatedNames D.T)
    (Q : List String) (hQ : ∀ q ∈ cone D p, q ∉ Q)
    (B : VE.Structure) (R : String → List B.Carrier → Prop) (hR : ∀ q vs, q ∉ Q → (R q vs ↔ B.relation q vs))
    (vs : List B.Carrier) :
  (outcomeBase (soften D) p).denote { B with relation := R } (tupleVal vs) ↔
    (outcomeBase (soften D) p).denote B (tupleVal vs)

/-- Global weighing independence needs a decision-free cone; strictness or hardness alone does not give it
    (fixture μ). -/
theorem hard_never_weighed_global (D) (h) (p) (hp) (hcone : ∀ q ∈ cone D p, q ∉ decisionNames D) (B) (R)
    (hR : ∀ q vs, q ∉ decisionNames D → (R q vs ↔ B.relation q vs)) (vs) :
  (outcomeBase (soften D) p).denote { B with relation := R } (tupleVal vs) ↔
    (outcomeBase (soften D) p).denote B (tupleVal vs)

/-- 7.4: declared attribution only. -/
theorem authority_independent (D) (h) (p) (hp) (π : String) (hπ : π ∈ D.soft.parties)
    (hcone : ∀ q ∈ cone D p, q ∉ attributed D π) (B) (R)
    (hR : ∀ q vs, q ∉ attributed D π → (R q vs ↔ B.relation q vs)) (vs) :
  (outcomeBase (soften D) p).denote { B with relation := R } (tupleVal vs) ↔
    (outcomeBase (soften D) p).denote B (tupleVal vs)

/-- 1.2 -/
theorem rank_acyclic (D : SoftDoc) (h : WellFormedSoft D = true) :
  VE.Route.DagAcyclic (rankNodes D.soft) ∧
  (∀ a, outranksPlus D.soft a a = false) ∧
  (∀ a b c, outranksPlus D.soft a b = true → outranksPlus D.soft b c = true → outranksPlus D.soft a c = true)

/-- 4.2 step 3: comparable colliding defaults never both select. -/
theorem rank_resolves (D : SoftDoc) (h : WellFormedSoft D = true) (M N : SoftNode)
    (hc : (M, N) ∈ collidingPairs D) (hcmp : Comparable D M N = true) (S : VE.Structure) (ρ : VE.Valuation S) :
  ¬ (SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N)

/-- Its base form: the RANK-RESOLVED conjunct of Coh_T is valid. -/
theorem coh_rank_valid (D) (h) (M N) (hc) (hcmp) (B : VE.Structure) : (cohPremise D M N).denote B []

/-- 6.3: every default–default collision is at a colliding pair; such a pair is not comparable. -/
theorem weighing_points_complete (D : SoftDoc) (h : WellFormedSoft D = true) (S : VE.Structure) (ρ : VE.Valuation S) :
  (∀ p, DefaultDecidesD D S ρ p true → DefaultDecidesD D S ρ p false →
     ∃ M N, (M, N) ∈ collidingPairs D ∧ M.pred = p ∧ N.pred = p ∧
       SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N ∧ Comparable D M N = false) ∧
  (∀ pr ∈ pairs (soften D).T, DefaultDecidesD D S ρ pr.req true → DefaultDecidesD D S ρ pr.perm false →
     ∃ M N, (M, N) ∈ collidingPairs D ∧
       ((M.pred = pr.req ∧ N.pred = pr.perm) ∨ (M.pred = pr.perm ∧ N.pred = pr.req)) ∧
       SelectsSoftD D S ρ (fuel D) M ∧ SelectsSoftD D S ρ (fuel D) N ∧ Comparable D M N = false)
```

### 9.3 Theorems: coherence, the conditional contract and the wire

```lean
/-- A sort-respecting substructure of E′_base: constants retained, base relations restricted. -/
def BaseSubstructure (D : SoftDoc) (B₀ B : VE.Structure) : Prop

/-- 6.1: the complete fragment gate makes every generated soft premise survive substructures. -/
theorem soft_premises_substructure (D : SoftDoc) (h : WellFormedSoft D = true) (hf : InFragment D = true)
    (B₀ B : VE.Structure) (hsub : BaseSubstructure D B₀ B) (hs : Sat B (softPremises D)) :
  Sat B₀ (softPremises D)

/-- W1's pointwise document iff on T′, instantiated (reused, not restated). -/
theorem coherent_expands (D : SoftDoc) (h : WellFormedSoft D = true) (B : VE.Structure)
    (hB : VE.Norms.BaseAdmissible (soften D) B) :
  VE.Route.Unique (VE.Norms.DocumentExpansion (soften D) B) ↔ VE.Norms.ConflictFree (soften D) B
  -- := VE.Norms.conflictFree_expands_document (soften D) (soften_wellFormed D h) B hB

/-- 6.3 -/
theorem soft_conflict_decomposition (D : SoftDoc) (h : WellFormedSoft D = true) (B : VE.Structure)
    (hB : VE.Norms.BaseAdmissible (soften D) B) :
  VE.Norms.ConflictFree (soften D) B ↔
    NoStrictCollision D B ∧ NoHardPairConflict D B ∧ Sat B (cohPremises D)

/-- Over coherent bases the check is exactly "no strict collision and no hard pair conflict". -/
theorem soft_conflict_free_iff (D) (h) :
  SoftConflictFree D ↔ ∀ B, BaseAdmissible' D B → NoStrictCollision D B ∧ NoHardPairConflict D B

/-- A conflict witness in a coherent base is strict–strict or involves a strict rule or a completion. -/
theorem soft_witness_classified (D) (h) (B) (hB : BaseAdmissible' D B) (hn : ¬ VE.Norms.ConflictFree (soften D) B) :
  ¬ NoStrictCollision D B ∨ ¬ NoHardPairConflict D B

/-- Unique expansion over coherent bases. -/
theorem soft_coherent_expands_all (D) (h) :
  (∀ B, BaseAdmissible' D B → VE.Route.Unique (VE.Norms.DocumentExpansion (soften D) B)) ↔ SoftConflictFree D

/-- 6.3, the certified statement: W1's conflictFreeCheck on T′ with Background_base′ in place of Background_base. -/
theorem soft_conflict_free (D : SoftDoc) (h : WellFormedSoft D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : softConflictFreeCheck D certs = true) :
  SoftConflictFree D
  -- softConflictFreeCheck: for every target of (soften D) (each p and each pair), an accepted certificate for
  -- backgroundBase' D ⊢ ∀x̄. ¬conflict over envAt (soften D) 0

/-- A typed finite base witness over E′_base passing the extended Background check refutes the conditional claim. -/
theorem soft_conflict_witness_sound {α} [DecidableEq α] (D) (h) (t) (ht : t ∈ VE.Norms.targets (soften D))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften D) 0)) (hb : backgroundValid' D M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
  ¬ VE.Norms.ConflictFree (soften D) M.asStructure ∧
  ¬ VE.Route.Unique (VE.Norms.DocumentExpansion (soften D) M.asStructure) ∧ ¬ SoftConflictFree D ∧
  (¬ NoStrictCollision D M.asStructure ∨ ¬ NoHardPairConflict D M.asStructure)

/-- 6.2 soundness of the classification. -/
theorem disjoint_sound (D) (h) (M N) (hc : (M, N) ∈ collidingPairs D) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (envAt (soften D) 0) (VE.Norms.backgroundBase (soften D) ++ excPremises D)
             (cohPremise D M N) c = true) :
  ∀ B, VE.Norms.BaseAdmissible (soften D) B → Sat B (excPremises D) →
    (cohPremise D M N).denote B []
theorem weighing_point_sound {α} [DecidableEq α] (D) (h) (M N) (hc) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid (envAt (soften D) 0)) (hb : classificationBackgroundValid D Mo = true)
    (vs : List α) (typed) (hw : (.and (selects'° M) (selects'° N)).eval Mo (tupleVal vs) = true) :
  ¬ (cohPremise D M N).denote Mo.asStructure [] ∧ ¬ (∀ B, VE.Norms.BaseAdmissible (soften D) B → VE.Norms.ConflictFree (soften D) B)

/-- Restated route pieces (W1's Layer.lean shape with PrefixAdmissible′ and background′; per-structure lemmas reused). -/
theorem soft_prefix_satisfaction (D) (h) (i) (hi : i ≤ size (soften D)) (S) :
  PrefixAdmissible' D i S ↔ S.Admissible (envAt (soften D) i) ∧ BaseAdmissible' D (restrictAll (soften D).T S) ∧
    Sat S (VE.Norms.PrefixPremises (soften D) i)
theorem soft_conflictFree_prefix (D) (h) (r) (hr) (hc : SoftConflictFree D) (S₀) (h₀ : PrefixAdmissible' D (before (soften D) r.name) S₀) :
  VE.Norms.ConflictFreeAt (soften D) r.name S₀
def softRoute (D) (h) (hc : SoftConflictFree D) : { R : VE.Route.Layer VE.Route.fol Unit // R.E_in = envAt (soften D) 0 ∧ (∀ B, R.Admissible_in B ↔ BaseAdmissible' D B) ∧ R.E_out = envAt (soften D) (size (soften D)) ∧ R.premises () = VE.Norms.elaborate (soften D).T }
theorem soft_route_backgroundSound (D) (h) (hc) : VE.Route.BackgroundSound (softRoute D h hc).1 (background' D)
theorem soft_route_backgroundComplete (D) (h) (hc) : VE.Route.BackgroundComplete (softRoute D h hc).1 (background' D)

/-- 6.4: W1's norms_route_acceptance restated with BaseAdmissible′ and background′. -/
theorem soft_route_acceptance (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree D)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften D) (size (soften D)))
                  (background' D ++ VE.Norms.elaborate (soften D).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure, S.Admissible (envAt (soften D) (size (soften D))) → holdsSoft D S →
     VE.Norms.definitionsHold (soften D) S → VE.Norms.profileHold (soften D) S →
     Sat S (VE.Norms.backgroundBase (soften D)) → Sat S (softPremises D) → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (envAt (soften D) 0) []) → φ.WellFormed (envAt (soften D) 0) [] →
     ∀ B : VE.Structure, BaseAdmissible' D B → Sat B Γ → φ.denote B [])

/-- 6.4: W1's norms_route_countermodel restated. -/
theorem soft_route_countermodel (D : SoftDoc) (h : WellFormedSoft D = true) (hc : SoftConflictFree D)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften D) 0) []) (hφ : φ.WellFormed (envAt (soften D) 0) [])
    (B : VE.Structure) (hB : BaseAdmissible' D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, VE.Norms.DocumentExpansion (soften D) B S ∧ Sat S (softPremises D) ∧ Sat S Γ ∧ ¬ φ.denote S []

theorem soft_route_entails_iff (D) (h) (hc) (Γ) (φ) (hΓ) (hφ) :
  VE.Entails (envAt (soften D) (size (soften D))) (background' D ++ VE.Norms.elaborate (soften D).T ++ Γ) φ ↔
    ∀ B, BaseAdmissible' D B → Sat B Γ → φ.denote B []

/-- The wire (norms.md 11.4 shape). `decodeSoftSource` decodes the environment with its soft block and the soft norm
    objects; `res.src.D` is the decoded SoftDoc, well-formed by construction of a successful replay. -/
theorem soft_wire_conflict_sound (j : Json) (res : SoftConflictReplay) (h : replaySoftConflict j = .ok res)
    (hv : res.conflictFree = true) :
  Wire.decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.src ∧
    WellFormedSoft res.src.D = true ∧ SoftConflictFree res.src.D

theorem soft_wire_conflict_witness_sound (j : Json) (src : Wire.SoftSource) (w : WitnessData src)
    (h : replaySoftWitness j = .ok ⟨src, w⟩) (hw : w.conflict = true) :
  Wire.decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok src ∧
    ¬ VE.Norms.ConflictFree (soften src.D) w.M.asStructure ∧ ¬ SoftConflictFree src.D ∧
    (¬ NoStrictCollision src.D w.M.asStructure ∨ ¬ NoHardPairConflict src.D w.M.asStructure)

theorem soft_wire_acceptance (j : Json) (r : SoftEntailmentReplay) (h : replaySoftEntailment j = .ok r)
    (hv : r.valid = true) :
  Wire.decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
  (∀ S : VE.Structure, S.Admissible (envAt (soften r.src.D) (size (soften r.src.D))) → holdsSoft r.src.D S →
     VE.Norms.definitionsHold (soften r.src.D) S → VE.Norms.profileHold (soften r.src.D) S →
     Sat S (VE.Norms.backgroundBase (soften r.src.D)) → Sat S (softPremises r.src.D) →
     Sat S r.premises → r.conclusion.denote S []) ∧
  (SoftConflictFree r.src.D →
     (∀ a ∈ r.premises, a.WellFormed (envAt (soften r.src.D) 0) []) → r.conclusion.WellFormed (envAt (soften r.src.D) 0) [] →
     ∀ B : VE.Structure, BaseAdmissible' r.src.D B → Sat B r.premises → r.conclusion.denote B [])

/-- W2 admission from the public entry point, as Norms.Run.norms_wire_acceptance: a successful soft `admission`
    answer is exactly the encoding of a checked admission whose bindings equal the recomputed digests and the
    regenerated E′, T′, layer, `background:profile` and `soft:*` leaves. -/
theorem Run.soft_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : Run.usesSoftPath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.SoftAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
```

`backgroundValid' D M` is W1's `backgroundValid` on `soften D` conjoined with the finite evaluation of every formula
in `softPremises D`; `classificationBackgroundValid D M` instead conjoins W1's `backgroundValid` with finite
evaluation of `excPremises D` only, excluding all coherence conjuncts. Thus both classification certificates and
witnesses bind `Background_base(E′) ++ Exc_T`. `SoftAdmissionAnswer` is W1's
`AdmissionAnswer` with the soft decoder, `soft:coherence:*` and `soft:exception:*` leaves admitted only when equal to
the regenerated formulas, and the report consequence stated over `background' D ++ elaborate (soften D).T`.

### 9.4 The executable `ve_soft_norms_route`

`lean/.lake/build/bin/ve_soft_norms_route <cases.json>`, root `SoftNormsMain.lean`, a new Lake target; `Run.main`
is the executable root and no frozen file changes. On raw input it runs the frozen envelope and profile gate,
requires `soft-norms@0` and `norms@0`, decodes the environment with its `soft` block through the W1 norms decoder
plus a strict soft decoder (unknown fields rejected; the original complete environment hashed), decodes the soft norm
objects, runs `WellFormedSoft`, regenerates `E′`, `T′`, `Exc_T`, `Coh_T`, `Background_base′`, `background′`, the
layer premises on `T′` and every conflict and classification target, and validates bindings. It reuses the unchanged
W1 leaves `checkCertificate`, `targets`, `targetConclusion`, `conflict`, `pairConflict`, `conflictFreeAt_of_base`,
`expansion_unique`, `documentExpansion_iff` and the witness evaluator on regenerated data. Two shells are newly
instantiated: `softConflictFreeCheck` supplies `Background_base′` where W1's `conflictFreeCheck` fixes
`backgroundBase D`; the soft layer constructor supplies `PrefixAdmissible′` where W1's `symLayer` fixes
`PrefixAdmissible D k`. Case kinds:

| Kind | Extra input | Output |
|---|---|---|
| `soft-elaborate` | none | `environment_prime` (canonical), `decisions`, `derived` (per rule, the derived carve-out), `order`, `background` (with the `soft` slot), `premises` (`layer:norms:<p>` on `T′`), `colliding_pairs` (pair, act, comparable, `soft:coherence:<a>,<b>` ast), `conflict_targets`, `fragment`, `warnings` |
| `soft-pairs` | per pair: `certificate` or `witness` over `Background_base(E′) ++ Exc_T`, with all coherence conjuncts excluded | per pair RANK-RESOLVED / DISJOINT / WEIGHING POINT / UNKNOWN with detail |
| `soft-conflict` | `packages` per target over `Background_base′`, or `witness` (base model over `E′_base` including decision tables, tuple) | `CONFLICT-FREE` (with `conditional_on` per target) / `CONFLICT` (classified) / `UNKNOWN` |
| `soft-certificate` | `premises`, `conclusion`, `certificate` bound to `background′ ++ layer premises ++ premises` | `valid`, `background`, `layers`, `conditional_on` |
| `admission` | W2 document with soft norm units and graph | `admitted`, `report`, `report_id`, `kinds`, `conditional_on` |

P0 and W1 cases without soft constructs delegate unchanged to `Norms.Run.runCase`; malformed soft inputs never fall
back after a failed soft decode.

### 9.5 What is not claimed

No completeness of the pair classification or the conflict check outside norms.md 7 applied to `T′`. No theorem
about the English surface (item 3). No claim that `IntendedSoftAt` matches an author's intent: that is this statement
review and W8's fidelity gate. No theorem about deciders: `excepted_N` and `outweighs` are open, and no theorem says a
decider ignores or honours anyone's instruction. No theorem about override cycles beyond the determinacy of
`ValueSoft`. No enumeration completeness (`conflict_complete` remains unstated, as in W1).

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind, from
Lean (`tests/test_soft_norms*.py`, the `soft-norms` conformance family). Unless a fixture says otherwise: one sort
`assistant`; act X declared with `x_required` (obligation, deny-by-default, `permission: x_permitted`) and
`x_permitted` (permission, allow-by-default), act `{0} do x`; parties `operator`, `user`; all guards `⊤`, no author
carve-outs or `over` edges; `Γ` empty. "Selects" means `selects′` at the one situation `a`.

- **(α) A1 regression.** Default `H`: `should X` (`+x_required`), rank `a`; default `L`: `generally need not X`
  (`−x_required`), rank `b`; `a outranks b`; holistic. Both eligible. With `outweighs_{X,b,a}(a)` true: `L` alone
  selects, `ValueSoft_{x_required} = some false`; false: `H` alone selects, `some true`. `Norms.Value T′` equals
  `ValueSoft` at both assignments; each base structure has exactly one expansion. `CP(T) = {{H, L}}`,
  RANK-RESOLVED; document CONFLICT-FREE with empty `conditional_on`.
- **(β) A2 mixed.** Default `should X` (`+x_required`) and strict `must not X` (`−x_permitted`), both live: the
  default is blocked by `N^s_{x_permitted}`; X neither required nor permitted; CONFLICT-FREE. Strict `must X` and
  default `should not X`: the default is blocked by `P^s_{x_required}`; required and permitted; CONFLICT-FREE.
  Same predicate: strict `must X` and default `generally need not X`: default blocked, required; strict `need not
  X` and default `should X`: default blocked, not required. In all four the witness search finds nothing and
  `hard_over_soft` is the certificate's content.
- **(γ) Completions.** Default `should X`, `x_permitted` deny-by-default, no rule on `x_permitted`: CONFLICT, pair
  conflict at `a` with witness "rule not excepted, not switched off; by default an assistant may not do x; no rule
  permits it". `x_permitted` allow-by-default: CONFLICT-FREE. Default `should not X` with `x_required`
  allow-by-default and no rule on it: CONFLICT ("required by default; rule forbids").
- **(δ) Soft–soft across the dual.** Default `A`: `should X` (`+x_required`); default `B`: `should not X`
  (`−x_permitted`); both unranked. `CP(T) = {{A, B}}`: WEIGHING POINT with the witness situation `a`, both
  exceptions false, no switches, both selecting (X required, not permitted). Under `Background_base′` the pair
  target and both predicate targets certify: CONFLICT-FREE, `conditional_on: soft:coherence:a,b` (the names sorted).
  Dropping `Coh_T` from the background makes the same pair certificate fail to replay. Ranked (`a outranks b`, either
  flag): RANK-RESOLVED, `conditional_on` empty. Running the classification with both the tableau and the witness
  search budgets at zero yields UNKNOWN for the pair and leaves `Coh_T` (one conjunct, same bytes) and the
  CONFLICT-FREE certificates unchanged.
  The paraphrase names resolution by exception, switch, guard, carve-out, blocking or dominance, and says the checker
  does not choose.
- **(ε) Alternating collision cycle.** Four defaults on `x_required`: `A`, `C` requiring, `B`, `D` releasing; ranks
  `A > B > C > D` (three `outranks` edges); holistic; all eligible; findings `outweighs_{X,B,A}`, `outweighs_{X,C,B}`,
  `outweighs_{X,D,C}` true, `outweighs_{X,D,A}` false. `D` alone is effective and selects: `some false`.
  `CP(T) = {A–B, B–C, C–D, A–D}`, all RANK-RESOLVED; CONFLICT-FREE; `override_cycles` names the situation and the
  `pref` cycle `B ≻ A ≻ D ≻ C ≻ B` and adds no premise.
- **(ζ) Authority.** Strict `must X` on `x_required`, `alterable: [user]`. Variant 1: guard `operator_instructs(a)`
  with `instruction_of: operator`; variant 2: guard over an unattributed base predicate. Report: `user: switch`
  in both; `operator: mentions operator_instructs` in variant 1, `operator: independent` in variant 2
  (`authority_independent`). `off_{N,operator}` does not exist: a `Γ` naming it is `UnknownSymbol`.
- **(η) Trees.** W1 10.1(q) diamond and 10.1(d) grandchild with every rule default and unranked, at assignments with
  every `excepted_N` false: same selections and outcomes as W1; CONFLICT-FREE. Strict child `E` of default parent `M`:
  where `E` is live it selects and `M` is blocked; where `E`'s guard fails `M` applies. Default child of a strict parent: `SoftOverHard`. Default rule with
  author `unless U` and exception: `live` false when `U` holds and when `excepted` holds; otherwise it selects.
- **(θ) Diagnostics.** `ties: [[a, b]]` with `a outranks b`: `TieAgainstOrder: a, b`. `a > b > c > a`:
  `DependencyCycle: a, b, c`. `N over M`, `{M, N} ∈ CP(T)`, `rank(M) outranks rank(N)`: `RankAgainstPrecedence: rule
  n over m`; the edge is inert when `N` has no descendants (see υ for the descendant regression). Dual guard: strict
  `must not X` on `x_permitted` with guard "it is not the case that S must X", default `should X` on `x_required`: `DependencyCycle: x_permitted, x_required`
  with the `DualGuardCycle` hint in Python's English diagnostic; the mirrored orientation (strict `must X` guarded on
  "it is not the case that S may X", default `should not X`) likewise reports `DependencyCycle: x_permitted, x_required`; the same documents with
  base-only guards are accepted; strict `may X` with the first guard beside default `should X` is accepted (no
  block, no cycle).
- **(ι) Vacuity.** Take (δ) unranked, replacing its true guards with explicit base guards `g_A(x)` and `g_B(x)`.
  `Γ` fixing `excepted_A(a)` and `excepted_B(a)` false together with `g_A(a)` and `g_B(a)` true, no carve-out,
  no switch (the two rules therefore both select): the P0 premise-set check reports
  `background′ ++ layer premises ++ Γ` in full `E′` inconsistent, every dependent certificate `vacuous`, and the
  coherent-model exhibit says so. `Γ` fixing only the two exceptions false: consistent (a model with a guard false),
  not vacuous; the exhibit displays the full premise-set model's `E′_base` restriction.
- **(κ) Chain.** `A` requires X (rank `a`), `B` forbids X (`b`), `C` permits X (`c`), `a > b > c`, strict flag, all
  live, no strict rules, `x_permitted` deny-by-default. `B` is dominated by effective `A`; `C` is not dominated by
  ineffective `B`. `A` and `C` select: required and permitted; CONFLICT-FREE. (Liveness-based dominance would report
  CONFLICT with the false witness "no rule permits it".)
- **(λ) Blocked dominator.** Strict `need not X` (`−x_required`), default `should X` (`+x_required`, rank high),
  default `should not X` (`−x_permitted`, rank low), `high > low`, strict flag, all live, `x_permitted`
  allow-by-default. The strict release blocks the obligation (same predicate); the release does not block the
  prohibition (compatible effects); the blocked obligation does not dominate the prohibition; the prohibition
  selects. X neither required nor permitted; CONFLICT-FREE.
- **(μ) Hard parent, switchable strict exception.** Hard `H`: `must X`; strict `E` (exception to `H`): `need not X`,
  `alterable: [user]`. With `off_{E,user}(a)` false `E` selects and `H` does not; true, `H` selects. Local
  independence (`hard_never_weighed`) holds; `off_{E,user} ∈ cone(x_required)`, so the hypothesis of
  `hard_never_weighed_global` fails and the report says "depends on the user switch of rule E".
- **(ν) Differently typed acts.** Act X over `(assistant)` and act Y over `(assistant, user)`; on each a colliding
  default pair with ranks `L < H`; holistic. `E′` contains `soft__outweighs__l__h__x_permitted(assistant)` and
  `soft__outweighs__l__h__y_permitted(assistant, user)`; elaboration, identity binding and rendered witnesses keep
  the act and rank pair apart; renaming either act's phrase changes `environment_id` and invalidates the
  certificates.
- **(ξ) W1 repeated.** Every row of norms.md 10.1 as a soft document with `mode: strict` and no switches: identical
  statuses, witnesses, diagnostics and premise lists; `T′ = T` and `E′ = E` byte for byte
  (`soften_hard_identity`); `CP(T) = ∅`, no `soft` premises, `conditional_on` empty.
- **(ο) Same-sign defaults.** Two default `should X` rules both selecting: `Overlap` naming both and a situation;
  CONFLICT-FREE; `CP(T) = ∅`.
- **(π) Deciders.** A default rule with `decided_by: null` and no `exception_decider`: `MissingExceptionDecider: rule
  <n>`; with `unstated`: accepted, counted under `default_exceptions: unstated`; with a document decider: inherited
  and shown. `outranking: holistic` without `decided_by`: `MissingExceptionDecider: outranking`.
- **(ρ) Exception conditions.** Default `should X` with `sufficient: [C]` and no other rule: the certificate for
  `∀a. C(a) → ¬x_required(a)` replays over `background′ ++ layer premises`; with the sufficient condition removed the
  same certificate fails; a countermodel exists and is rendered with `excepted` false. A condition mentioning
  `x_permitted`: `InvalidInput: exception condition of rule <n> mentions x_permitted`.
- **(σ) Hard flag.** `hard: true` with `alterable: [user]`: `HardConstraintAltered: rule <n>`; with `mode: default`:
  the same; with `mode: strict` and no switch: accepted and inert.
- **(τ) Circular discharge.** Unranked default `A` requires X; unranked defaults `B`, `C` release X. For each rule,
  `sufficient: [Q]` and `necessary: [Q]` impose `excepted_N(x) ↔ Q(x)` for base predicate `Q`; guards are true,
  no precedence. `CP(T) = {A–B, A–C}`; both coherence conjuncts are equivalent to `∀x. Q(x)`. Classification over
  `Background_base(E′) ++ Exc_T` marks both WEIGHING POINT, witnessed by `Q(a)` false, all three exceptions false
  and all three rules selecting. Neither conjunct may certify the other as DISJOINT. Conflict checking over full
  `Background_base′` is CONFLICT-FREE; any used undischarged coherence leaf remains in `conditional_on`.
- **(υ) Yield through a dominated rule.** Live defaults `M` requires X at high rank, `N` releases X at low rank,
  `K` releases X unranked; `high outranks low`, strict ranking, all exceptions false; `N over M`, `K over N`.
  `M` and `K` are effective; `N` is dominated. `K` yields through `N` and suppresses `M`; `K` alone selects,
  `ValueSoft_{x_required} = some false`. Removing only `N over M` leaves effectiveness unchanged but makes `M`
  and `K` both select, `ValueSoft_{x_required} = none`, a conflict at this assignment. The M–K coherence conjunct
  excludes that assignment from the full coherent background; the `RankAgainstPrecedence` edge is not redundant.

Beside these: norms.md 10.6 to 10.10 repeated on generated soft documents (surface round trip with the new fields
and metadata; identity of every existing fixture unchanged; certificate binding against a changed rank, edge, flag,
switch, decider, exception condition or mode; differential `soften` Python versus Lean on 1,000 generated soft trees;
DAG diagnostics on `T′`).

## 11. Limits, regeneration, Rust

Rules ≤ 256, regulated predicates ≤ 64, ranks ≤ 16, parties ≤ 8, precedence depth ≤ 16, author carve-outs ≤ 7 per
rule (the eighth is derived), each unfolded formula within `MAX_NODES`; witness search uses the existing bounds and
`MAX_EVALUATIONS`; every overflow is `ResourceLimit` with the limit named, never a truth value. `E′`, `T′`, `Exc_T`,
`Coh_T` and every premise are regenerated from the decoded units and declarations at every trusted site (norms.md
11.3); a finite model supplies base tables including decision tables, and a supplied regulated table is rejected as
in W1. Rust never elaborates soft norms: on the `elaborated-document` family a soft case carries the Python-generated
`T′` premises and `Soft_T` marked `untrusted: true`, and its verdict must agree with Python's and Lean's regenerated
ones (regression evidence; the trust path is Lean).

## 12. Statement review checklist (Astra + Fable, before items 2, 3 and 4)

1. `ValueSoft` (4.2): the four steps, `blocked` on same predicate either way and across the pair for incompatible
   effects only, dominance by higher effectiveness and lower eligibility, `yields′` over all children.
2. The existence statement and proof (4.3), replacing the withdrawn corollary.
3. `soften` (5.1): one derived carve-out, omitted when `⊥`; no derived precedence; `soften_faithful` by unfolding.
4. `Coh_T` over all of `CP(T)`, `Exc_T`, `Soft_T`, `Background_base′`, `BaseAdmissible′` (6.1); `coherent_expands`
   with W1's `BaseAdmissible`; `soft_conflict_decomposition` and the definition of `NoHardPairConflict` (6.3).
5. The conditional route contract (6.4) and its Lean statements (9.3): `Soft_T` through the first layer's
   `Admissible_in`; used-premise `conditional_on`; the three vacuity measures (6.5).
6. Completion outcomes kept CONFLICT (6.6); override cycles as warnings via `pref` (6.7).
7. `hard_never_weighed` local with strict switches fixed; `cone_independent`; the global and authority instances
   and their stated limits (7.4, 9.2).
8. `outweighs` indexed by act and ordered rank pair with the act's sorts (1.3); canonical names.
9. The English table (2.1): one reading per wording; the two synonyms; the frequency words; the asymmetry sentence
   and the selection-disjointness paraphrase (2.3).
10. The diagnostics (8) and the fixtures (10), each against the definitions.
11. Remaining questions from the plan: is `Coh_T` in base admissibility, with results marked conditional, an
    acceptable reading of "check under all admitted interpretations or identify the chosen one"? Is the attribution
    check the right scope for "authority"?
12. The resolved choices of section 13.

## 13. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **`unstated` is a checker-level value.** The checker never knows whether a unit is authored or translated; the
   `decided_by` field accepts a decider or `unstated`, `MissingExceptionDecider` fires only when neither the rule nor
   the environment names one, and W8 (item 6) never offers `unstated` in authoring. The plan's "in authoring
   (MissingExceptionDecider); in translation the decider may be `unstated`" is realised by the assistant, not by a
   mode flag.
2. **Parties are declared** in the environment `soft.parties`; `alterable` and `instruction_of` name declared
   parties. The plan used "operator" and "user" as examples without saying where the set lives.
3. **Exception conditions are base formulas and their premises enter `BaseAdmissible′`** as `Exc_T`, beside `Coh_T`.
   The plan wrote `BaseAdmissible′ := BaseAdmissible E′ B ∧ Sat B Coh_T`; with no conditions the two agree.
   Conditions over regulated predicates are rejected rather than placed in a layer.
4. **Canonical decision-predicate names** with the reserved `soft__` prefix and the `__` ban (1.3), so `E′` is
   collision-free and regenerable without a table.
5. **`hard: true` is a declared assertion** with no English wording; `HardConstraintAltered` is its consistency
   check. The plan named the diagnostic without saying how "narrowed hard by citation" reaches the checker.
6. **The derived carve-out is omitted when syntactically `⊥`**, so all-hard soft documents elaborate to W1 trees byte
   for byte and W1's fixtures transfer verbatim (fixture ξ).
7. **A rank on a strict rule is accepted and inert** (needed because translation reading sets may make the same
   ranked unit strict or default).
8. **Override cycles are cycles of the findings tournament `pref_a`** among eligible colliding rules (6.7); the plan
   gave the example and the status (warning) but not the definition.
9. **`DualGuardCycle` is an English-layer hint** on W1's shared `DependencyCycle` text, keeping Python and Lean
   diagnostic strings identical.
10. **The `soft` generator slot** follows `profile` in `ve/background.py` `HOOKS` order, so `background′` is
    definitions, literals, profile, soft; the certificate premise order is `background′ ++ layer premises ++ Γ`.
11. **The act key** for `outweighs` is the permission predicate when the act has one, else the act's only
    predicate.
12. **The document-level decider** lives in the environment `soft` block (`exception_decider`), as the completion
    legend does; the English sentence of 2.1 renders it.
13. **The coherent-model exhibit** is the P0 premise-set model of `background′ ++ layer premises ++ Γ` in full `E′`,
    with its `E′_base` restriction displayed as the coherent assignment, reported in the P0 vacuity vocabulary
    (model / inconsistent / UNKNOWN); CONFLICT-FREE is not downgraded when the exhibit is UNKNOWN, the status text
    says so.
14. **`weighing_points_complete` also asserts non-comparability** of the exhibited pair, folding `rank_resolves`
    into the statement, so the classification's "cannot be a discharged pair" is a theorem and not a remark.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Item-1 specification from plan draft 3: attributes and environment declarations; decision vocabulary indexed by act and rank pair; effect-based collisions; the English table with the asymmetry and selection-disjointness paraphrases; wire form; `ValueSoft` with higher-effective/lower-eligible dominance and the existence lemma; `soften` with one derived carve-out and `DualGuardCycle`; `Exc_T`, `Coh_T` over all of `CP(T)`, `BaseAdmissible′`, decomposition and the conditional contract; report, residual lines and status text; diagnostics; every item-4 theorem as a statement in W1's Lean conventions; fixtures α to σ; resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-27 | Converged item-1 FIX | Applied exactly the joint FIX set in `manage-agents/debates/soft-spec/fable.md` round 3 and `manage-agents/debates/soft-spec/astra.md` rounds 1–3: Astra’s seven and Fable’s three as amended, with the four final resolutions. Document-node dominance and fuel hypotheses; coherence-free classification and bindings; decision findings and full-premise vacuity exhibit; complete soft fragment gate and preservation obligation; exception-condition cone closure; authoring rejection of `should generally` forms; precise blocking and precedence prose; `rankHeight` and W1 reuse boundaries; corrected ι, ρ, η, θ and added circular-discharge and M/N/K regressions. Core semantics, `soften`, `Coh_T`, decomposition and route theorem statements unchanged; this agreed correction set satisfies the statement gate for items 2–4. |
