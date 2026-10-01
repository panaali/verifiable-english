# Feature composition: the stack contract, the base-premise slot, the dispatcher and candidate content (stage S0)

> Status: item-1 specification, draft 1 (2026-10-01), written from [composition-PLAN.md](composition-PLAN.md) draft
> 2, the transcription of the converged Astra + Fable design debate
> (`manage-agents/debates/design-compose/{astra,fable}.md`, CONVERGED after round 3: REVISE to draft 2, then BUILD
> through statement review; the Astra seat was held by Sol xhigh as the recorded cross-family stand-in). It is the
> statement under the Astra + Fable item-1 review that gates S0's Lean and the item-1 specifications of the later
> stages (PLAN-EXPAND2 rule 10): a draft alone opens nothing. **Scope** (13.1): the contract every layer of the
> stack signs, and everything stage S0 builds (`VE.Compose`: the slot, the dispatcher, the content type). Stages
> S1, S3 and S4 get their own specifications (`readings.md`, `right-clauses.md`, an amendment of
> [discourse.md](discourse.md)) and S2's follows S1's merge (plan section 9); this file fixes what those must
> instantiate (section 6) and the English they share (section 2), and restates none of their theorems. Sections 4,
> 5 and 9 are the statements under review; section 13 lists every point where this draft chose between readings of
> the plan. Theorem statements and fixtures are implementation obligations, not claims of completed proofs or
> tests. Inputs: the plan; [norms.md](norms.md) (W1), [soft-norms.md](soft-norms.md), [rights.md](rights.md),
> [document.md](document.md) (W2), [discourse.md](discourse.md); and, read at `main` `2205be39`,
> `lean/VE/Semantics.lean`, `lean/VE/Norms/{Basic,Tree,Prefix,Conflict,Replay}.lean`,
> `lean/VE/SoftNorms/{Tree,Soften,Semantics,Coherence}.lean`, `lean/VE/Rights/{Tree,Correlate,Semantics,Route,Examples}.lean`,
> `lean/VE/Route/{Gate,Layer,Route,Readings}.lean`, `lean/VE/Discourse/Admission.lean`, `ve/profiles.py`,
> `ve/readings.py`, `ve/admission.py`, `ve/backends/lean_runner.py`. Nothing here changes a frozen contract, a
> canonical byte, an identity, an existing theorem statement, a checker function or the answer of any executable.

## 0. Scope, one paragraph

Every merged feature of VE is a wrapper with its own route, and the wrappers were never given one order. The plan
fixes one order, **the stack** (RESOLVE, STRUCTURE, SUPERPOSE, CHAIN, CHECK), and six rules a layer signs to be
placed in it. This specification states that contract so that it can be checked, and specifies the three things
every later stage imports. First, the **base-premise slot**: the soft route relative to an arbitrary list `P` of
closed base formulas, proved once, of which the rights route is the instance `P := Lim_D` and the full stack the
instance `P := Lim_D ++ Choice_D ++ gated Rel_D`. Second, the **dispatcher**: one function from a profile list to
its route, which returns today's route on every list that has one and today's diagnostic on every list today's
gate rejects, the head of the stack on a chain list, and a named abstention only for a stack wrapper beside a
route outside the chain. Third, the **candidate content type** shared by readings and reference resolution. S0
changes no behaviour: it adds Lean definitions and theorems and one Python test, wires nothing, and adds no
executable, no case kind and no profile. What it buys: a new layer restates no route theorem, the order of layers
is one reviewed definition instead of five call sites, and S3 and S4 can be built without S1 or S2.

In this specification: definitions (1), the English (2), wire and identity (3), the semantics (4), what the slot
route certifies (5), what each later stage must instantiate (6), the report (7), diagnostics (8), the Lean
definitions and every theorem as a statement (9), the item-1 acceptance fixtures (10), limits and regeneration
(11), the review checklist (12), the resolved choices (13).

Out of scope, by the plan: `sup`, `Choice_D`, separation and every verdict across readings (S1, S2); `plain`,
`Rel_D` and the relation theorems (S3); position-wise resolution and the composed admission (S4); any composition
with `alternatives@0`, `risk@0`, `speech-acts@0`, `reports@0`, definitions, data or quantities (plan 2.9: the
dispatcher keeps each of those routes as it is and names the abstention); any coverage number.

## 1. Definitions

### 1.1 The stack

```text
rank  step        profile            owns                         hands its successor
 1    RESOLVE     ve.discourse@1     references                   the same document, every formula position closed
 2    STRUCTURE   right-clauses@0    line shape                   rights@0 lines with larger guards; Rel_D
 3    SUPERPOSE   readings@1         readings                     one reading-free document sup D; Choice_D
 4    CHAIN       rights@0           holders, incidents,          a soft document; Lim_D
                                     limitations, the bar
                  soft-norms@0       force, exceptions, ranks     a W1 tree; Soft_T
                  norms@0            applicability, conflict      layer premises
 5    CHECK       relational-fol@0   truth, proof, countermodels  certificate or finite model
```

A **wrapper profile** is a profile of ranks 1 to 3; a **chain profile** is one of the three of rank 4. A wrapper
validates and strips its own profile and hands the remaining list to `dispatch` (4.2); it never calls a route by
name. `norm-defaults@0` is unmerged and has no position here; plan 2.9 says where it and the other profiles would
attach.

### 1.2 Profile lists

```text
registered        the fifteen names of ve/profiles.py REGISTRY: alternatives@0, closure@0, data@0, definitions@0,
                  documents@1, nary@0, norms@0, soft-norms@0, order@0, relational-fol@0, speech-acts@0, reports@0,
                  risk@0, rights@0, time@0
wrapperProfiles   [ve.discourse@1, right-clauses@0, readings@1]            in stack order
base ps           ps without its wrapper profiles
today's list      a list today's gate accepts: TodayList ps (4.2), the acceptance set of ve/profiles.py
                  checker_family
chain list        a strictly increasing list whose base is a today's list with route norms, soft or rights, and
                  each of whose wrapper profiles sits on that route (4.2)
```

A list is always compared as written: strictly increasing in code point order, which is what "sorted and unique"
means in Python and `List.Pairwise (· < ·)` in Lean.

### 1.3 Routes

A **route** is the entry that checks a document under a profile list. The first eight exist today and are what
today's gate chooses between. The last three are the heads of the stack's wrappers: the discourse wrapper exists
today over `frozen` only, and the other two are built by S3 and S1.

| Route | Today | Entry |
|---|---|---|
| `frozen` | yes | P0: `ve_conformance` / service mode `route`, with its four checker families; with a `ve-units@1` environment the same lists go to `ve_quantity`, which is this head's own choice and stays so |
| `norms` | yes | `ve_norms_route` / service mode `norms`; a case without a norm construct is delegated to P0 unchanged (`usesNormsPath`, norms 11.4) |
| `soft` | yes | `ve_soft_norms_route` |
| `rights` | yes | `ve_rights_route` |
| `alternatives` | yes | `ve_alternatives_route` |
| `risk` | yes | `ve_risk_route` |
| `speechActs` | yes | `ve_speech_acts_route` |
| `reports` | yes | `ve_reports_route` |
| `discourse` | yes, over `frozen` only | `ve_discourse_route`; S4 lets it sit on the chain |
| `clauses` | no (S3) | the head of `right-clauses@0` |
| `readings` | no (S1) | the head of `readings@1` |

### 1.4 A base-premise slot

For a soft document `X` (soft-norms 1; `VE.SoftNorms.SoftDoc`), with `soften X` its W1 document and
`E′_base := envAt (soften X) 0` the base vocabulary of the soft route:

```text
slot P                  a list of formulas, each closed and well-formed over E′_base        SlotWellFormed X P
BaseAdmissibleP X P B   := BaseAdmissible′ X B ∧ B satisfies every formula of P
backgroundBaseP X P     := Background_base′(X) ++ P
backgroundP X P         := background′(X) ++ P
ConflictFreeP X P       := for every B with BaseAdmissibleP X P B, ConflictFree (soften X) B
```

A slot is the only way a layer above the chain adds a premise: as a closed base formula that narrows the
admissible base structures, exactly as `Soft_T` narrows W1's and `Lim_D` narrows soft's (soft-norms 6.1, rights
5.1). A slot is regenerated from the decoded document at every trusted site and is never read from the wire. The
empty slot is the soft route itself; `P := Lim_D` over `X := correlate D` is the rights route, by definition
(9.2).

### 1.5 Labels, gating and the combined slot

```text
labelled slot     a list of (label, formula); labels pairwise distinct; the slot is its formulas, in order
label families    soft:exception:…, soft:coherence:…      existing; not in a slot (Soft_T is inside BaseAdmissible′)
                  rights:limitation:<L>:<act key>:<necessary|sufficient>:<c>          Lim_D   (existing, rights 1.3)
                  readings:<set>@<v>:one, readings:<set>@<v>:<i>:quiet, readings:quiet:<source key>,
                  coupling:<id>, constraint:<n>, narrowing:<id>                         Choice_D (S2)
                  rights:relation:<line>:total                                          Rel_D    (S3)
gate χ P          the list of χ → ρ for ρ in P, for a closed base formula χ
combined slot     Lim_D ++ Choice_D ++ gated Rel_D, in this order: the totality premise ρ of a relation on a line of
                  candidate a_{s,i} enters as χ_{s,i} → ρ, a fixed line's ρ as it is
```

**The gating rule.** `sup` gates everything a candidate owns or causes: its guards, its exception conditions, the
predicates generated for it, the premises it brings and the nodes generated because of it (plan 2.3). In slot
terms: a premise a candidate brings is gated by the candidate's atom; a predicate `g` generated because of
candidates gets the quiescence premise `∀x̄. g(x̄) → ⋁ χ(owners(g))`; a node the chain generates because of a
candidate (the bar's node on an act that is right-derived only through candidate liberties) is silenced through
the quiescence of the predicate that guards it (`aimed_m`), and the chain's generating function is not changed.

**Model correspondence.** A layer that adds a slot owes, per compatible choice `c`, both directions: the base
structures that satisfy the combined slot and in which exactly `c`'s atoms hold restrict to base structures of
`c`'s own document, and every base structure of `c`'s document with at least one element extends to one of them
(plan S2, `base_down` and `base_up`). 4.4 gives the two generic facts about `gate` this rests on.

### 1.6 Candidate content

The content of a reading candidate under `readings@1` (plan 2.2), and of a unit whose references the stack
resolves (plan 2.8), is one of five existing unit contents in their existing wire forms:

```text
assertion φ           a formula                                 kind "asserted"
norm N                a soft norm object (soft-norms 3.2);      kind "norm"          needs norms@0
                      a W1 norm when soft is off is the
                      rule with mode strict, no alterable party
right R               rights 3.2                                kind "right"         needs rights@0
rightLines r ls       rights 3.2, lines added to right r        kind "right_lines"   needs rights@0
limitation L          rights 3.2                                kind "limitation"    needs rights@0
```

A content **declares** names: a norm its rule name; a right its own name and the rule names of its lines (both
units of a power); a `rightLines` the rule names of its lines; a limitation its own name. Declared names are what
the closure and cross-set checks of plan 2.2 and the copy mapping of plan 2.3 range over. A quantity statement and
a bar unit are not contents: quantity sets stay on W2's and W6's routes (plan 2.5), and the bar is the one
enumerated axis, fixed before a document reaches `sup` (plan 2.6).

### 1.7 Reserved names

Reserved by this contract and rejected in author input by the stage that introduces each: the prefix `ve__` on
sorts, constants and predicates and the prefix `rd-` on rule, right and limitation names (S1, `InvalidInput`, as
`soft__` and `rights-` are today); the label prefixes `readings:`, `coupling:`, `constraint:`, `narrowing:` and
`rights:relation:` on author leaf labels. S0 enforces none of them, since no executable changes.

## 2. The English (one reading each)

Nothing in this section is a norm word, and no sentence here can be written by an author as document content:
these are the sentences VE **says** about a composed document. Each has one derivation because it begins with a
fixed lead that no other registered production begins with, and its slots are closed classes defined in 2.1. W7
registers each template with the stage named in the last column, and each passes the all-derivations gate before
it is shown. S0 itself shows only the two abstention sentences.

### 2.1 Wordings

Slots: `<n>` is a unit's display number (its position among the document's units in source order; reports print
the unit id beside it). `<k>` is a count. `<reading>` names a candidate of the set of the sentence just mentioned:
it is `reading <i>`, with `<i>` the candidate's 1-based position in the set, except when the candidates of the set
differ only in their deontic verb, where it is that verb in italics as the candidate's own VE sentence has it
(*must*, *should*, *must not*, *should not*, *may*, *generally may*). `<decider>` is the declared decider's name,
or the words `the decider` when the declaration says `unstated`. `<feature>` is the one name of a profile in the
table of 2.2.

| # | Wording | The one reading | Formal content | Stage |
|---|---|---|---|---|
| E1 | `This document turns on <feature a> and <feature b>. VE cannot check these two together yet. Nothing in this document was checked.` | The two named features are both enabled and no route checks them together. No verdict of any kind was produced. | `UnsupportedProfile: <a> with <b>` (4.2) | S0 |
| E2 | `This document turns on <feature a>, which needs <feature b>. Nothing in this document was checked.` | Feature a is enabled and feature b, which it is built on, is not. | `UnsupportedProfile: <a> requires <b>` | S0 |
| E3 | `This holds provided that:` followed by one sentence per line | The result above is proved only for situations in which every listed sentence is true. VE does not say that they are true. | the used slot premises, by label (`conditional_on`, 7) | each slot's stage |
| E4 | `Sentence <n> is read in exactly one of its <k> listed ways.` | One candidate of the set is in force, the same one everywhere in the document. | `readings:<set>@<v>:one` and the bit encoding of plan 2.3 | S2 |
| E5 | `Sentences <n>[, <n>]* and <n> are read with the same <axis>, because of sentence <n>[, <n>]*.` | The listed sets take candidates that carry the same label on the axis. The cited sentences are the reason given for this choice; they do not prove it. | `coupling:<id>`; rights documents keep rights 2.1's coupling sentence unchanged | S1 |
| E6 | `If sentence <n> is read as <reading>, sentence <n> is read as <reading>.` / `Sentence <n> is not read as <reading> while sentence <n> is read as <reading>.` | `requires` / `excludes` between two named candidates (discourse 1.5). | `constraint:<n>` | S2 |
| E7 | `Sentence <n> is not read as <reading>, because of sentence <n>[, <n>]*.` | A recorded narrowing drops that candidate. The cited sentences are its stated reason. | `narrowing:<id>` | S2 |
| E8 | `A way of reading a sentence that is not taken adds nothing: its exception, switch, limitation and bar conditions hold nowhere.` | Under each choice, every decision table that exists only because of an unchosen candidate is empty. | every quiescence premise used | S2 |
| E9 | `If sentence <n> is read as <reading>: <totality sentence>` | The totality sentence of a relation (the plan's instance: *Every person has at least one country.*) is assumed only under that reading. Under the other readings nothing is assumed. | `χ_{s,i} → ρ`, label `rights:relation:<line>:total` | S3 with S2 |
| E10 | `Under every reading of the <k> open sentences, <result sentence>` | For every compatible choice of one candidate per open sentence, and every situation of that choice's document, the result holds. | plan S2 `superpose_all`, `superpose_conflict_free` | S2 |
| E11 | `Under every reading with at least one individual, <result sentence>` | As E10, restricted to situations in which something exists. Used **only** if the lifting lemma (4.5) fails in statement review; then E10 is never used for an entailment. | `superpose_all` with the non-emptiness hypothesis | S2, fallback |
| E12 | `Read sentence <n> as <reading>[ and sentence <n> as <reading>]*: <result sentence>` | The result holds, or the conflict occurs, under exactly the named candidates and whatever the other open sentences are read as, unless they are named too. | a certificate or countermodel with those atoms assumed (plan 2.5) | S2 |
| E13 | `This does not depend on how sentence <n> is read.` | The certificate uses no premise that mentions the set of that sentence. | no used leaf mentions the set | S2 |
| E14 | `This sentence says <source word>. (1) <strict paraphrase> (2) <default paraphrase> They differ here: suppose <decider> decides the exception applies to <subject>. Under (1) <outcome sentence>. Under (2) <outcome sentence>.` | The two candidates give different outcomes in the shown situation once the exception's decision table holds there. The decision is supposed, and attributed to who decides; it is not a fact of the situation. | a checked separating situation with the default candidate's decision, and its probe's two values (plan 2.4) | S1 (W8) |
| E15 | `These two readings differ only where <decider> decides that the exception applies. No situation separates them without that decision.` | Finding `SeparatedByDecisionOnly`. The set is admitted. | plan 2.4 | S1 |
| E16 | `These two readings are about different acts: <act phrase> / <act phrase>. No situation separates them on a shared act.` | Finding `SeparatedByActOnly`. The set is admitted. | plan 2.4 | S1 |
| E17 | `No compatible way of reading the open sentences reads sentence <n> as <reading>.` | Finding `DeadReading`: the couplings, constraints and narrowings exclude the candidate. | a certificate of `¬χ_{s,i}` from `Choice_D` | S2 |
| E18 | `"<surface>" in sentence <n> is taken to refer to <target>: resolved by the translator, not checked.` | A provenance mention. It is attributed to who recorded it, counted apart from checked resolutions, and changes no status. | plan 2.8; only if S4's specification admits provenance mentions | S4 |

The two outcome sentences of E14 state the checked value of the probed act under each candidate in the shown
situation; they are never inferred from the verb. For an obligation they are `<subject> still must` and `<subject>
is not required to` (the plan's instance: "Under (1) Ruritania still must. Under (2) it is not required to.");
for a permission, `<subject> may` and `<subject> may not`. Which candidate gets which is read off the probe: where
a default prohibition is excepted, the other rules and the declared default decide the act, and they may still
forbid it. In a document, the strict and the default reading of one rule also differ where a strict rule decides
the act and where the strict twin blocks other default rules (plan S1: `force_agrees_off_exception` is about a
rule alone); S1's specification adds one sentence for each to E14, behind the W8 fidelity gate (plan open
question 3).

### 2.2 Feature names, synonyms and non-wordings

One name per profile, pairwise distinct, used only in E1 and E2:

| Profile | `<feature>` |
|---|---|
| `ve.discourse@1` | resolved references |
| `right-clauses@0` | clauses on right lines |
| `readings@1` | readings that carry rules |
| `norms@0` | rules |
| `rights@0` | rights |
| `alternatives@0` | alternatives |
| `risk@0` | risk statements |
| `speech-acts@0` | commands and questions |
| `reports@0` | reports of what someone said |

No synonyms are accepted or produced. Not wordings, and never produced:

- A decision stated as a fact: "Ruritania lacks the resources and the exception applies." E14 says "suppose
  `<decider>` decides the exception applies".
- "Under every reading" for an entailment when the fallback of E11 is in force.
- Any generated name: a choice atom, `ve__here`, a bit predicate, an `rd-` name, a generated decision predicate.
  Reports say "sentence 12 read as *must*", never an atom (plan 2.3).
- "checked", "verified" or "resolved" without "by the translator, not checked" for a provenance mention.
- A result sentence without E3 when a slot premise was used: the proviso is part of the result.
- "The two readings are equivalent" for a rejected set: the rejection text is the diagnostic of section 8, and it
  says only that the supplied situation does not separate them.

### 2.3 The reader's checklist (norms 2.5, soft-norms 2.3 and rights 2.3, extended)

For a composed document the IDE shows, in English only: for every open sentence, its candidates in order with
their paraphrases and E4; for every pair of candidates the separating situation in the form of E14, and E15 or E16
when the finding applies; every coupling (E5), constraint (E6) and narrowing (E7) with its cited sentences; under
every result, E3 with the premises used, limitation sentences in rights 2.1's wording and coherence premises in
soft-norms 2.1's; for a result that needed no reading premise of a set, E13; for an abstention, E1 or E2 and
nothing else.

### 2.4 Examples from the pinned sources

- Constitution `u0156.s03` [95093, 95193), "Claude shouldn't actively deceive the user …" (plan F1: the rule
  `no-system-prompt-deception` on the obligation predicate `system_prompt_deception_avoidance_required`). E14:
  "This sentence says *shouldn't*. (1) *Every Claude instance must `<act>` each user.* (2) *Every Claude instance
  should `<act>` each user.* They differ here: suppose the decider decides the exception applies to this instance
  and this user. Under (1) this instance still must. Under (2) it is not required to." `<act>` is the predicate's
  declared act phrase in the translation; this specification fixes the frame, not the phrase. The decider is the
  rule's declared one, and the words are `the decider` when it is `unstated`.
- Constitution main document, 14 force sets (plan F3). E10: "Under every reading of the 14 open sentences, no two
  rules on the same act contradict each other." followed by E3 with the coherence premises used and, if a
  quiescence premise was used, E8.
- Constitution `u0165.s03` with `narrow-u0165-s03`, which keeps the strict candidate (plan F2). E7: "Sentence
  `<n>` is not read as *should*, because of sentences `<m>` and `<m′>`." with the display numbers of `u0165.s03`,
  `u0166.s01` and `u0166.s04`, and the dropped candidate's own verb.
- UDHR `u054` [5239, 5284), Art. 15(1) (plan F13). E9: "If sentence `<n>` is read as reading 3: every person has
  at least one responsible state." Under readings 1 and 2 (the two assertions) the sentence is not among the
  provisos.
- A document with profiles `alternatives@0, norms@0, readings@1, relational-fol@0`. E1: "This document turns on
  readings that carry rules and alternatives. VE cannot check these two together yet. Nothing in this document was
  checked."

## 3. Wire form and identity

S0 adds no wire field, no case kind, no profile, no label on any existing wire and no identity. Fixed here for
the later stages:

- A slot is never on the wire as authority. A case may carry premises marked `untrusted: true` for Rust (11); Lean
  and Python regenerate the slot from the decoded document and bind it to the document hash.
- `conditional_on` lists the labels of the slot premises a certificate's used leaves contain, after the existing
  `soft:coherence:*` entries, in slot order: `rights:limitation:*`, then the `Choice_D` families in the order of
  1.5, then `rights:relation:*`. A gated premise is listed under its own label with the reading appended:
  `rights:relation:<line>:total under <set>@<v>:<i>`.
- S0 fixes no identity rule for a wrapper profile. The discourse wrapper's is discourse 3.5 and stays: inner
  identities are computed under the stripped profile list and the outer report binds the full list. Each new
  wrapper's specification states its own rule, and none may change an identity of a document that does not turn
  the wrapper on (PLAN-EXPAND2 rule 3).

## 4. Semantics

### 4.1 The layer contract

A layer is placed in the stack by meeting six obligations. The third column is what S0 provides for it; the
fourth is the theorem or check the layer's own specification must state.

| Rule | Obligation | S0 provides | The layer supplies |
|---|---|---|---|
| 1. One position | its profile has one rank; it strips its profile and calls `dispatch` on the rest | `dispatch`, `dispatch_descends` | the wiring, and "unchanged when off" for its route |
| 2. Source in, same kind out | its output is a document its successor accepts; it reads no generated vocabulary of a later layer, except the quiescence premises of `Choice_D` (plan 2.1 rule 2) | — | a well-formedness theorem into the successor's check (`sup_wellFormed`, `plain_wellFormed`, `resolve_no_new_symbols`) |
| 3. Regenerated | every derived object is recomputed at every trusted site and bound to the document hash | — | an `-elaborate` case kind compared byte for byte between Python and Lean |
| 4. Premises through slots | its premises are a labelled slot; candidate-owned premises are gated | 1.4, 1.5, the slot theorems (9.2), `gate` | the slot, `SlotWellFormed`, its labels and sentences (2.1), the model correspondence of 1.5 |
| 5. Identity when unused | a Lean theorem | `slot_empty`, `dispatch_today` | `sup_no_sets`, `plain_identity`, `resolve_identity`, `composed_base_unchanged` |
| 6. Abstention is named | no block is dropped silently | `dispatch`'s refusals (4.2) | its content-level abstentions, by name |

### 4.2 `dispatch`

`dispatch ps` is computed in three steps.

**Step 1, order.** If `ps` is not strictly increasing: `UnsupportedProfile: profiles must be sorted and unique`.

**Step 2, today's gate on `base ps`.** `today` is `ve/profiles.py` `checker_family`, check for check and text for
text, followed by the head. The checks, in order; the first that fires is the answer, each text prefixed
`UnsupportedProfile: `:

| # | Fires when | Text |
|---|---|---|
| 1 | not strictly increasing | `profiles must be sorted and unique` |
| 2 | `alternatives@0` without `norms@0` | `alternatives@0 requires norms@0` |
| 3 | `alternatives@0` with `soft-norms@0` | `alternatives@0 with soft-norms@0` |
| 4 | `risk@0` without `alternatives@0` | `risk@0 requires alternatives@0` |
| 5 | some profile is not registered (the first such, in list order) | `Unsupported profile <p>` |
| 6 | `speech-acts@0` without `norms@0` | `speech-acts@0 requires norms@0` |
| 7 | `speech-acts@0` with a profile outside `relational-fol@0`, `norms@0`, `speech-acts@0` (the first such) | `speech-acts@0 with <p>` |
| 8 | `relational-fol@0` missing | `Missing profile relational-fol@0` |
| 9 | `reports@0` with the first present of `norms@0`, `definitions@0`, `data@0` | `reports@0 with <p> layers` |
| 10 | `reports@0` with the first present of `closure@0`, `nary@0`, `order@0` | `reports@0 requires the fol checker, not <p>` |
| 11 | `order@0` with `closure@0`; else `order@0` with `nary@0` | `Unsupported profile combination closure@0 x order@0` / `… nary@0 x order@0` |
| 12 | `nary@0` without `closure@0` | `Unsupported profile nary@0 without closure@0` |
| 13 | `risk@0` with `closure@0`, `nary@0` or `order@0` | `the risk norms route admits FOL documents only` |
| 14 | `rights@0` without `soft-norms@0` | `rights@0 requires soft-norms@0` |
| 15 | `soft-norms@0` without `norms@0` | `soft-norms@0 requires norms@0` |

An accepted list has the route of the first line that applies:

```text
risk@0 ∈ ps → risk          alternatives@0 ∈ ps → alternatives     speech-acts@0 ∈ ps → speechActs
reports@0 ∈ ps → reports    rights@0 ∈ ps → rights                 soft-norms@0 ∈ ps → soft
norms@0 ∈ ps → norms        otherwise → frozen
```

So `alternatives@0`, `risk@0` and `speech-acts@0` lists, which all contain `norms@0`, keep their own routes, and
`reports@0` keeps its own. The checker family (FOL, closure, closure with n-ary, order) is not part of the route:
it stays the head's own choice, as do the head's content-level abstentions (`the norms route admits FOL documents
only`, `rights route with definitions is not implemented`), which are unchanged.

**Step 3, the wrappers.** With `r` the route of `base ps`, each wrapper profile of `ps` must sit on `r`:

| Wrapper | Sits on | Otherwise |
|---|---|---|
| `ve.discourse@1` | `frozen`, `norms`, `soft`, `rights` | `ve.discourse@1 with <b>` |
| `right-clauses@0` | `rights` | `right-clauses@0 requires rights@0`, or `right-clauses@0 with <b>` |
| `readings@1` | `norms`, `soft`, `rights` | `readings@1 requires norms@0`, or `readings@1 with <b>` |

`<b>` is the profile that names `r` when `r` is outside the chain: `reports@0`, `speech-acts@0`, `alternatives@0`
or `risk@0`. The `requires` form is used when `r` is `frozen` or a chain route below the one the wrapper needs.
The wrappers are examined in stack order and the first refusal is the answer. With no refusal, the result is the
head of the first wrapper present in stack order (`discourse`, then `clauses`, then `readings`), or `r` when `ps`
has no wrapper.

Consequences, each a theorem of 9.3: on a list without wrapper profiles `dispatch` is `today` (so on today's
lists it is today's route and on today's rejections today's diagnostic); on a chain list it is the stack's head;
after a wrapper strips its own profile, `dispatch` on the rest succeeds with the next head; every error is the
order error, today's error on the base, or one of the refusals above. The frozen gate's answers on its own
registry are `today`'s (`today_classify`).

What `dispatch` does not decide: whether a wrapper's stage is merged. Until S1 registers `readings@1` (and S3
`right-clauses@0`), Python's and Lean's registries reject the name before any route is chosen (`Unsupported
profile readings@1`), and the discourse wrapper keeps calling the frozen gate until S4. `dispatch` is the
function they will call; S0 calls it nowhere.

### 4.3 The route relative to a slot

Everything the soft route proves for `BaseAdmissible′` holds with a slot `P` added, by the proof the rights route
already has for `P := Lim_D` (`lean/VE/Rights/Route.lean`), in which `Lim_D` is used only through two facts: it is
a list of formulas satisfied by the base, and each is closed and well-formed over `E′_base`.

- **Unique expansion.** Over the bases admissible relative to `P`, every base has exactly one expansion to the
  complete vocabulary exactly when `ConflictFreeP X P` (`slot_coherent_expands_all`).
- **Conflict-freedom, certified.** One accepted certificate per W1 conflict target of `soften X` for
  `backgroundBaseP X P ⊢ ∀x̄. ¬conflict` over `E′_base` gives `ConflictFreeP X P` (`slot_conflict_free`). A typed
  finite base model that passes `backgroundValidP` and satisfies a target refutes it and is classified as soft
  classifies it (`slot_conflict_witness_sound`).
- **Acceptance.** A certificate accepted from `backgroundP X P ++ layer premises ++ Γ` proves its conclusion in
  every structure with the intended soft meaning that satisfies the background, the soft premises, `P` and `Γ`
  (no conflict-freedom needed), and, when `ConflictFreeP X P` and `Γ`, `φ` are base formulas, in every base
  admissible relative to `P` that satisfies `Γ` (`slot_route_acceptance`).
- **Countermodel.** Under the same hypotheses a base admissible relative to `P` that satisfies `Γ` and refutes `φ`
  expands to a full structure that does (`slot_route_countermodel`).
- **Exactness.** Entailment from the checked premises is the same as truth in every admissible base
  (`slot_route_entails_iff`).
- **Monotonicity.** A longer slot admits fewer bases: `ConflictFreeP X P` gives `ConflictFreeP X (P ++ Q)`, so a
  conflict-free result for `Lim_D` survives adding `Choice_D` and `Rel_D`; the converse is false and is not
  claimed.

### 4.4 Gating

For a closed base formula `χ` and a slot `P`, `gate χ P` is a slot (`gate_wellFormed`); in a base where `χ` holds,
satisfying `gate χ P` is satisfying `P` (`sat_gate_on`); in a base where `χ` fails, `gate χ P` is satisfied
whatever `P` says (`sat_gate_off`). This is the whole content of "a candidate's premise enters as `χ → ρ`": under
the choice that takes the candidate the premise is in force, under every other choice it imposes nothing. An
ungated candidate premise breaks model correspondence in the upward direction: a base of another choice's
document in which the premise fails has no extension (plan fixture F13).

### 4.5 The empty structure

A structure may have an empty carrier (`Structure.constant : String → Option Carrier`; no sort is assumed
inhabited). Three statements settle what this means for the stack.

1. `ConflictFree` is vacuous on an empty carrier: W1's well-formedness gives every regulated predicate arity 1 or
   2 (`semanticCheck`, `lean/VE/Norms/Tree.lean`), so both clauses of `ConflictFree` quantify over typed tuples of
   length at least 1, and there are none. So a conflict-freedom claim across readings needs no non-emptiness
   hypothesis on the per-choice side; on the superposed side every admissible structure interprets the constant
   `ve__here` and so has an element.
2. **The lifting lemma.** For any structure `B`, `adjoinOne B` is `B` with one new element that lies in no sort
   and in no tuple. Every formula has the same truth value in `adjoinOne B` as in `B`, under any valuation of `B`
   (`adjoin_denote`), because quantifiers range over the sort domains and the new element is in none; hence
   `adjoinOne B` is admissible for an environment, and admissible relative to a slot, exactly when `B` is
   (`adjoin_admissible`, `adjoin_baseAdmissibleP`), and it has an element. With it an entailment claim across
   readings covers structures with no element, matching W2's `Entails`, which ranges over them. The statement is
   fixed in 9.5 and is an obligation of this review; it is expected to hold and is not proved.
3. If the lemma fails in review, the non-emptiness hypothesis stays in the entailment theorem and every report
   uses E11, never E10, for an entailment. The upward correspondence (`base_up`) keeps the hypothesis either way.

## 5. What the slot route certifies, and vacuity

1. A certified conclusion holds in every situation whose decision and exception tables satisfy the coherence
   premises and whose base satisfies **every formula of the slot**. The report lists the slot premises used (E3,
   `conditional_on`). Nothing is claimed for a situation that violates one.
2. A countermodel is a finite base model that satisfies the regenerated base background and the whole slot, not
   only the used part (`backgroundValidP`): a model that violates a slot premise is not a countermodel but an
   invalid model, as PLAN-EXPAND2 rule 5 requires of every generated premise.
3. The P0 vacuity report runs over `backgroundBaseP X P ++ layer premises ++ Γ`. A slot that is unsatisfiable
   with the background makes every dependent certificate `vacuous`, visibly. A CONFLICT-FREE report exhibits one
   checked base model of `backgroundBaseP X P ++ Γ` or says UNKNOWN with the budget (soft-norms 6.5, rights 5.3).
4. A slot premise alone proves nothing about any act; a result that uses none is reported without E3.
5. No slot premise is ever discharged, hidden or reordered by a layer above it (discourse 5 for coherence
   premises; plan S4 `conditions_retained` for the whole slot).

## 6. What each later stage must instantiate

| Stage | Slot it adds | Gated? | Identity theorem | Dispatch wiring | Sentences it registers |
|---|---|---|---|---|---|
| S1 `readings@1`, part A | none | — | sets without content-bearing candidates validate as today (`separation_conservative`) | registers `readings@1`; the head `readings` validates sets and hands the rest to `dispatch` | E5, E14, E15, E16 |
| S2a, S2b `readings@1`, part B | `Choice_D` (labels of 1.5), appended after `Lim_D` | quiescence by owners; no premise of `Choice_D` is itself gated | `sup_no_sets`; formula-only documents keep W2's route | the head `readings` checks `sup D` on `dispatch`'s next route | E4, E6, E7, E8, E10 (or E11), E12, E13, E17 |
| S3 `right-clauses@0` | `Rel_D` (`rights:relation:<line>:total`), appended last | a candidate line's premise by its atom, once S2 is in | `plain_identity` | registers `right-clauses@0`; the head `clauses` elaborates and calls `dispatch` | E9, the clause and relation sentences |
| S4 `ve.discourse@1` on the chain | none | — | `resolve_identity`, `composed_base_unchanged` | the wrapper calls `dispatch` on the base list instead of the frozen gate | E18, if admitted |

Each stage's specification states: `SlotWellFormed` for its slot; the label of every premise and its sentence;
the two directions of model correspondence (1.5) for a superposing layer; that its slot is appended, never
inserted before an existing one; and the three-way agreement it offers (Lean authority, a Python differential on
its `-elaborate` kind, Rust evaluating regenerated formulas marked untrusted). When a stage registers a wrapper
profile, Python's `checker_family` is extended so that it equals `dispatch` on every list containing that profile,
and the differential of fixture D-all (10.1) is extended to those lists.

The order S0, then S1, S2a, S2b in one lane, with S3 and S4 as independent lanes, depends on `Content` and the
slot being S0's: S3 imports `VE.Compose.Slot`, S4 imports `VE.Compose.Content` and `VE.Compose.Dispatch`, and
neither imports `VE.Readings`.

## 7. The report

S0 changes no report. The contract for the stages:

```text
conditional_on        soft:coherence:<a>,<b> …, then the slot labels used, in slot order (3)
status text           CONFLICT-FREE among rules on the same act, conditional on <k> coherence premises, <l>
                      limitation premises, <m> reading premises and <n> relation premises (<labels>)
                      [, under couplings <ids>]; <j> weighing points open; situation exhibited: yes | UNKNOWN (<budget>)
                      a family with count 0 is omitted, so a rights document without reading sets prints
                      rights 7.3's line unchanged
abstention            the diagnostic of 8 and its sentence E1 or E2; no status, no coverage line
residual lines        slot_premises_used (per certificate, by family); for S2: reading_premises, dead_readings;
                      for S3: relation_premises, elided_bytes; for S4: provenance_mentions, counted apart from
                      checked resolutions
```

Every English line of a report about readings is one of 2.1; a result with a non-empty `conditional_on` is
followed by E3.

## 8. Diagnostics

New in S0 as texts of `dispatch`; no executable raises them until a wrapper's stage wires `dispatch`:

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: <a> with <b>` | a stack wrapper `<a>` beside a route outside the chain, named by `<b>` ∈ {`reports@0`, `speech-acts@0`, `alternatives@0`, `risk@0`} | error |
| `UnsupportedProfile: readings@1 requires norms@0` | `readings@1` over the `frozen` route | error |
| `UnsupportedProfile: right-clauses@0 requires rights@0` | `right-clauses@0` over `frozen`, `norms` or `soft` | error |

Unchanged, and returned by `dispatch` verbatim: the texts of 4.2's fifteen checks, in that order. Unchanged and not
`dispatch`'s: every head's own texts, the discourse wrapper's (`ve.discourse@1 requires ve-document@2`,
`discourse admission requires the FOL family`), and every W1, soft, rights and P0 diagnostic.

Named by the plan and raised by a later stage; the text is fixed here so that the stage specifications agree:

| Text | Raised by | Kind |
|---|---|---|
| `ReadingInterface: <set>: <name>` | S1: a fixed unit names something not every candidate of the set declares | error |
| `DuplicateDeclaration: <name> in reading sets <s> and <t>` | S1: candidates of two sets declare one name, or a candidate redeclares a fixed name (then `<t>` is `the document`) | error |
| `InvalidInput: name <n> begins with ve__` / `begins with rd-` | S1: reserved names (1.7) | error |
| `distinguishing model does not separate readings` | S1: today's text, unchanged (`ve/readings.py`) | error |
| `ResourceLimit: decision assignments` | S1: more than 2¹² assignments on the other side | error, never a verdict |
| `ReadingsNotSuperposable: <sets>` | S2: candidates stratify alone and cycle together; the enumerated fallback then decides | finding |
| `DeadReading: <set>:<i>` | S2 | finding |
| `SeparatedByActOnly: <set>: <i>, <j>` / `SeparatedByDecisionOnly: <set>: <i>, <j>` | S1 | finding |
| `fragment: no (rights:relation:<line>:total)` | S3: an existential slot premise leaves norms 7's fragment | report line |

Order: stack order (RESOLVE, STRUCTURE, SUPERPOSE, then the chain's existing order), then each layer's own table.
Within `dispatch` the order is 4.2's. A refused list is never partly checked.

## 9. Lean (S0): definitions and the exact statements to prove

### 9.1 Files

`lean/VE/Compose/Slot.lean` (9.2), `Dispatch.lean` (9.3), `Content.lean` (9.4), `Examples.lean` (the `#guard`
fixtures of section 10), and `lean/COMPOSE.md` listing each theorem in plain words. `VE.lean` and `VE/Audit.lean`
gain imports and audit entries only; `lakefile.toml` is unchanged (no new target); the audit allowlist is
unchanged (`propext`, `Classical.choice`, `Quot.sound`); no new name contains a prime or one of the audit's banned
words. Frozen `Norms/*`, `SoftNorms/*`, `Rights/*`, `Route/*`, `Discourse/*` and all P0 sources are untouched
(`python3 VE/Route/frozen.py` passes). Names below have prefix `VE.Compose.`; `VE.SoftNorms.BaseAdmissible'`,
`background'` and `backgroundBase'` are the existing names. The blocks are statement schemata: binders shown once
are repeated where a later statement abbreviates them as `(X) (h) (P)`.

### 9.2 `Slot.lean`

```lean
import VE.Rights.Route

namespace VE.Compose
open VE.Norms (Sat ConflictFree envAt size elaborate targets targetConclusion tupleVal)
open VE.SoftNorms (SoftDoc soften WellFormedSoft BaseAdmissible' background' backgroundBase' softPremises holdsSoft
  SoftConflictFree softConflictFreeCheck NoStrictCollision NoHardPairConflict)
universe u

/-! ## Definitions (1.4) -/

/-- Every formula of the slot is closed and well-formed over the base vocabulary of the soft route. -/
def SlotWellFormed (X : SoftDoc) (P : List VE.Formula) : Prop := ∀ a ∈ P, a.WellFormed (envAt (soften X) 0) []
def slotCheck (X : SoftDoc) (P : List VE.Formula) : Bool := P.all (fun a => a.check (envAt (soften X) 0) [])
theorem slotCheck_sound (X : SoftDoc) (P : List VE.Formula) (h : slotCheck X P = true) : SlotWellFormed X P

def BaseAdmissibleP (X : SoftDoc) (P : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissible' X B ∧ Sat B P
def backgroundBaseP (X : SoftDoc) (P : List VE.Formula) : List VE.Formula := backgroundBase' X ++ P
def backgroundP (X : SoftDoc) (P : List VE.Formula) : List VE.Formula := background' X ++ P
def ConflictFreeP (X : SoftDoc) (P : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleP X P B → ConflictFree (soften X) B

/-! ## Identity when unused, and monotonicity -/

theorem slot_empty (X : SoftDoc) (B : VE.Structure.{u}) : BaseAdmissibleP X [] B ↔ BaseAdmissible' X B
theorem slot_empty_conflictFree (X : SoftDoc) : ConflictFreeP.{u} X [] ↔ SoftConflictFree.{u} X
theorem slot_empty_background (X : SoftDoc) : backgroundP X [] = background' X ∧ backgroundBaseP X [] = backgroundBase' X
theorem baseAdmissibleP_append (X : SoftDoc) (P Q : List VE.Formula) (B : VE.Structure.{u}) :
  BaseAdmissibleP X (P ++ Q) B ↔ BaseAdmissibleP X P B ∧ Sat B Q
theorem slotWellFormed_append (X : SoftDoc) (P Q : List VE.Formula) :
  SlotWellFormed X (P ++ Q) ↔ SlotWellFormed X P ∧ SlotWellFormed X Q
theorem conflictFreeP_append (X : SoftDoc) (P Q : List VE.Formula) (hc : ConflictFreeP.{u} X P) :
  ConflictFreeP.{u} X (P ++ Q)

/-! ## Gating (1.5, 4.4) -/

def gate (χ : VE.Formula) (P : List VE.Formula) : List VE.Formula := P.map (fun ρ => .implies χ ρ)
theorem gate_wellFormed (X : SoftDoc) (χ : VE.Formula) (P : List VE.Formula)
    (hχ : χ.WellFormed (envAt (soften X) 0) []) (hP : SlotWellFormed X P) : SlotWellFormed X (gate χ P)
theorem sat_gate_on (B : VE.Structure.{u}) (χ : VE.Formula) (P : List VE.Formula) (h : χ.denote B []) :
  Sat B (gate χ P) ↔ Sat B P
theorem sat_gate_off (B : VE.Structure.{u}) (χ : VE.Formula) (P : List VE.Formula) (h : ¬ χ.denote B []) :
  Sat B (gate χ P)

/-! ## Labels (1.5) -/

abbrev Labelled := List (String × VE.Formula)
def Labelled.formulas (L : Labelled) : List VE.Formula := L.map (·.2)
def Labelled.wellLabelled (L : Labelled) : Bool := decide (L.map (·.1)).Nodup

/-! ## Unique expansion and conflict-freedom relative to a slot (4.3) -/

theorem slot_coherent_expands_all (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula) :
  (∀ B : VE.Structure.{u}, BaseAdmissibleP X P B →
     VE.Route.Unique (VE.Norms.DocumentExpansion (soften X) B)) ↔ ConflictFreeP.{u} X P

/-- W1's conflictFreeCheck on soften X with backgroundBaseP X P in place of Background_base. -/
def slotConflictFreeCheck (X : SoftDoc) (P : List VE.Formula) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (soften X)).length == certs.length &&
    ((targets (soften X)).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (soften X) 0) (backgroundBaseP X P) (targetConclusion t) c
      | none => false)
theorem slot_empty_check (X : SoftDoc) (certs : List (Option VE.Tableau.Certificate)) :
  slotConflictFreeCheck X [] certs = softConflictFreeCheck X certs
theorem slot_conflict_free (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) (hc : slotConflictFreeCheck X P certs = true) :
  ConflictFreeP.{u} X P

/-- Soft's backgroundValid' and the finite evaluation of every slot premise. -/
def backgroundValidP {α : Type u} [DecidableEq α] (X : SoftDoc) (P : List VE.Formula) (M : VE.FiniteModel α) : Bool :=
  VE.SoftNorms.backgroundValid' X M && P.all (fun a => a.eval M [])
theorem baseAdmissibleP_of_valid {α : Type u} [DecidableEq α] (X : SoftDoc) (P : List VE.Formula)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften X) 0)) (hb : backgroundValidP X P M = true) :
  BaseAdmissibleP X P M.asStructure
theorem slot_conflict_witness_sound {α : Type u} [DecidableEq α] (X : SoftDoc) (h : WellFormedSoft X = true)
    (P : List VE.Formula) (t : String × List String × VE.Formula) (ht : t ∈ targets (soften X))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften X) 0)) (hb : backgroundValidP X P M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
  ¬ ConflictFree (soften X) M.asStructure ∧ ¬ ConflictFreeP.{u} X P ∧
  (¬ NoStrictCollision X M.asStructure ∨ ¬ NoHardPairConflict X M.asStructure)

/-! ## The route relative to a slot (4.3) -/

/-- The composed frozen P0 layers of soften X with BaseAdmissibleP X P as input admissibility. -/
def slotRoute (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula) (hc : ConflictFreeP.{u} X P) :
  { L : VE.Route.Layer VE.Route.fol.{u} Unit // L.E_in = envAt (soften X) 0 ∧
    (∀ B, L.Admissible_in B ↔ BaseAdmissibleP X P B) ∧ L.E_out = envAt (soften X) (size (soften X)) ∧
    L.premises () = elaborate (soften X).T }
theorem slot_route_backgroundSound (X) (h) (P) (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) :
  VE.Route.BackgroundSound (slotRoute X h P hc).1 (backgroundP X P)
theorem slot_route_backgroundComplete (X) (h) (P) (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) :
  VE.Route.BackgroundComplete (slotRoute X h P hc).1 (backgroundP X P)

/-- The first half of slot_route_acceptance: no conflict-freedom, no typing of the slot. -/
theorem slot_route_intended (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
                  (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible (envAt (soften X) (size (soften X)))) (hsoft : holdsSoft X S)
    (hdef : VE.Norms.definitionsHold (soften X) S) (hprof : VE.Norms.profileHold (soften X) S)
    (hbase : Sat S (VE.Norms.backgroundBase (soften X))) (hsp : Sat S (softPremises X)) (hslot : Sat S P)
    (hΓ : Sat S Γ) :
  φ.denote S []

/-- One statement for every base-premise slot: the soft route relative to P. -/
theorem slot_route_acceptance (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
                  (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure.{u}, S.Admissible (envAt (soften X) (size (soften X))) → holdsSoft X S →
     VE.Norms.definitionsHold (soften X) S → VE.Norms.profileHold (soften X) S →
     Sat S (VE.Norms.backgroundBase (soften X)) → Sat S (softPremises X) → Sat S P → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) → φ.WellFormed (envAt (soften X) 0) [] →
     ∀ B : VE.Structure.{u}, BaseAdmissibleP X P B → Sat B Γ → φ.denote B [])

theorem slot_route_countermodel (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) (hφ : φ.WellFormed (envAt (soften X) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissibleP X P B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, VE.Norms.DocumentExpansion (soften X) B S ∧ Sat S (softPremises X) ∧ Sat S P ∧ Sat S Γ ∧ ¬ φ.denote S []

theorem slot_route_entails_iff (X : SoftDoc) (h : WellFormedSoft X = true) (P : List VE.Formula)
    (hP : SlotWellFormed X P) (hc : ConflictFreeP.{u} X P) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften X) 0) []) (hφ : φ.WellFormed (envAt (soften X) 0) []) :
  VE.Entails.{u} (envAt (soften X) (size (soften X))) (backgroundP X P ++ elaborate (soften X).T ++ Γ) φ ↔
    ∀ B : VE.Structure.{u}, BaseAdmissibleP X P B → Sat B Γ → φ.denote B []

/-! ## The existing routes are instances -/

open VE.Rights (RightsDoc correlate limPremises WellFormedRights BaseAdmissibleR RightsConflictFree backgroundR
  backgroundBaseR rightsConflictFreeCheck backgroundValidR)

theorem rights_is_slot (D : RightsDoc) (B : VE.Structure.{u}) :
  BaseAdmissibleR D B ↔ BaseAdmissibleP (correlate D) (limPremises D) B
theorem rights_conflictFree_is_slot (D : RightsDoc) :
  RightsConflictFree.{u} D ↔ ConflictFreeP.{u} (correlate D) (limPremises D)
theorem rights_background_is_slot (D : RightsDoc) :
  backgroundR D = backgroundP (correlate D) (limPremises D) ∧
  backgroundBaseR D = backgroundBaseP (correlate D) (limPremises D)
theorem rights_check_is_slot (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) :
  rightsConflictFreeCheck D certs = slotConflictFreeCheck (correlate D) (limPremises D) certs
theorem rights_valid_is_slot {α : Type u} [DecidableEq α] (D : RightsDoc) (M : VE.FiniteModel α) :
  backgroundValidR D M = backgroundValidP (correlate D) (limPremises D) M
theorem rights_slot_wellFormed (D : RightsDoc) (h : WellFormedRights D = true) :
  SlotWellFormed (correlate D) (limPremises D)

/-- rights_route_acceptance and rights_route_countermodel, their statements copied unchanged from
    lean/VE/Rights/Route.lean, proved here from the slot theorems alone. The originals are not touched. -/
theorem rights_acceptance_from_slot (D : RightsDoc) (h : WellFormedRights D = true) (hc : RightsConflictFree.{u} D)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (soften (correlate D)) (size (soften (correlate D))))
                  (backgroundR D ++ elaborate (soften (correlate D)).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure.{u}, S.Admissible (envAt (soften (correlate D)) (size (soften (correlate D)))) →
     holdsSoft (correlate D) S → VE.Norms.definitionsHold (soften (correlate D)) S →
     VE.Norms.profileHold (soften (correlate D)) S → Sat S (VE.Norms.backgroundBase (soften (correlate D))) →
     Sat S (softPremises (correlate D)) → Sat S (limPremises D) → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (envAt (soften (correlate D)) 0) []) →
     φ.WellFormed (envAt (soften (correlate D)) 0) [] →
     ∀ B : VE.Structure.{u}, BaseAdmissibleR D B → Sat B Γ → φ.denote B [])
theorem rights_countermodel_from_slot (D : RightsDoc) (h : WellFormedRights D = true)
    (hc : RightsConflictFree.{u} D) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (soften (correlate D)) 0) [])
    (hφ : φ.WellFormed (envAt (soften (correlate D)) 0) [])
    (B : VE.Structure.{u}) (hB : BaseAdmissibleR D B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, VE.Norms.DocumentExpansion (soften (correlate D)) B S ∧ Sat S (softPremises (correlate D)) ∧
    Sat S (limPremises D) ∧ Sat S Γ ∧ ¬ φ.denote S []
end VE.Compose
```

Notes for the review. `rights_is_slot`, `rights_conflictFree_is_slot`, `rights_background_is_slot`,
`rights_check_is_slot` and `rights_valid_is_slot` hold by unfolding (`BaseAdmissibleR D B` is by definition
`BaseAdmissible' (correlate D) B ∧ Sat B (limPremises D)`, `backgroundR D` is `background' (correlate D) ++
limPremises D`); they are stated so that the instance is a checked fact and not a remark.
`rights_slot_wellFormed` is `RightsValid.limTyped`. `slot_conflict_free` and `slotRoute` take no `hP`: the
certificate check and the layer chain use the slot only as satisfied formulas; typing is used where a premise is
moved between a structure and its base restriction (`slot_route_backgroundSound`, `_backgroundComplete`, the second
half of acceptance, the countermodel, `slot_route_entails_iff`). The premise list of `accepted` is
`((background' X ++ P) ++ layer premises) ++ Γ`, which for the rights instance is the list of
`rights_route_acceptance` syntactically.

### 9.3 `Dispatch.lean`

```lean
import VE.Route.Gate
import VE.SpeechActs.Wire

namespace VE.Compose

def unsupported (message : String) : String := "UnsupportedProfile: " ++ message

def registered : List String :=
  ["alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1", "nary@0", "norms@0", "soft-norms@0",
   "order@0", "relational-fol@0", "speech-acts@0", "reports@0", "risk@0", "rights@0", "time@0"]
def speechAllow : List String := ["relational-fol@0", "norms@0", "speech-acts@0"]
/-- The stack's wrapper profiles, in stack order (ranks 1, 2, 3). -/
def wrapperProfiles : List String := ["ve.discourse@1", "right-clauses@0", "readings@1"]

inductive Route
  | frozen | reports | speechActs | alternatives | risk
  | norms | soft | rights
  | readings | clauses | discourse
  deriving DecidableEq, Repr

/-- ve/profiles.py checker_family as a gate: the fifteen checks of 4.2 in order, with its texts. -/
def todayGate (ps : List String) : Except String Unit :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else if ps.contains "alternatives@0" && !ps.contains "norms@0" then
    .error (unsupported "alternatives@0 requires norms@0")
  else if ps.contains "alternatives@0" && ps.contains "soft-norms@0" then
    .error (unsupported "alternatives@0 with soft-norms@0")
  else if ps.contains "risk@0" && !ps.contains "alternatives@0" then
    .error (unsupported "risk@0 requires alternatives@0")
  else match ps.find? (fun p => !registered.contains p) with
  | some p => .error (unsupported s!"Unsupported profile {p}")
  | none =>
  if ps.contains "speech-acts@0" && !ps.contains "norms@0" then
    .error (unsupported "speech-acts@0 requires norms@0")
  else match (if ps.contains "speech-acts@0" then ps.find? (fun p => !speechAllow.contains p) else none) with
  | some p => .error (unsupported s!"speech-acts@0 with {p}")
  | none =>
  if !ps.contains "relational-fol@0" then .error (unsupported "Missing profile relational-fol@0")
  else match (if ps.contains "reports@0" then ["norms@0", "definitions@0", "data@0"].find? ps.contains
              else none) with
  | some p => .error (unsupported s!"reports@0 with {p} layers")
  | none =>
  match (if ps.contains "reports@0" then ["closure@0", "nary@0", "order@0"].find? ps.contains else none) with
  | some p => .error (unsupported s!"reports@0 requires the fol checker, not {p}")
  | none =>
  if ps.contains "order@0" && ps.contains "closure@0" then
    .error (unsupported "Unsupported profile combination closure@0 x order@0")
  else if ps.contains "order@0" && ps.contains "nary@0" then
    .error (unsupported "Unsupported profile combination nary@0 x order@0")
  else if ps.contains "nary@0" && !ps.contains "closure@0" then
    .error (unsupported "Unsupported profile nary@0 without closure@0")
  else if ps.contains "risk@0" && (ps.contains "closure@0" || ps.contains "nary@0" || ps.contains "order@0") then
    .error (unsupported "the risk norms route admits FOL documents only")
  else if ps.contains "rights@0" && !ps.contains "soft-norms@0" then
    .error (unsupported "rights@0 requires soft-norms@0")
  else if ps.contains "soft-norms@0" && !ps.contains "norms@0" then
    .error (unsupported "soft-norms@0 requires norms@0")
  else .ok ()

def todayHead (ps : List String) : Route :=
  if ps.contains "risk@0" then .risk else if ps.contains "alternatives@0" then .alternatives
  else if ps.contains "speech-acts@0" then .speechActs else if ps.contains "reports@0" then .reports
  else if ps.contains "rights@0" then .rights else if ps.contains "soft-norms@0" then .soft
  else if ps.contains "norms@0" then .norms else .frozen

def today (ps : List String) : Except String Route := (todayGate ps).map (fun _ => todayHead ps)

/-- The independent specification of a list today's gate accepts. -/
def TodayList (ps : List String) : Prop :=
  ps.Pairwise (· < ·) ∧ (∀ p ∈ ps, p ∈ registered) ∧ "relational-fol@0" ∈ ps ∧
  ("alternatives@0" ∈ ps → "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps) ∧
  ("risk@0" ∈ ps → "alternatives@0" ∈ ps ∧ "closure@0" ∉ ps ∧ "nary@0" ∉ ps ∧ "order@0" ∉ ps) ∧
  ("speech-acts@0" ∈ ps → "norms@0" ∈ ps ∧ ∀ p ∈ ps, p ∈ speechAllow) ∧
  ("reports@0" ∈ ps → ∀ p ∈ ["norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"], p ∉ ps) ∧
  ("order@0" ∈ ps → "closure@0" ∉ ps ∧ "nary@0" ∉ ps) ∧ ("nary@0" ∈ ps → "closure@0" ∈ ps) ∧
  ("rights@0" ∈ ps → "soft-norms@0" ∈ ps) ∧ ("soft-norms@0" ∈ ps → "norms@0" ∈ ps)

theorem today_sound (ps : List String) (r : Route) (h : today ps = .ok r) : TodayList ps ∧ r = todayHead ps
theorem today_complete (ps : List String) (h : TodayList ps) : today ps = .ok (todayHead ps)

/-- On the frozen gate's own registry, today's gate is the frozen classifier: same acceptance, same text. -/
theorem today_classify (ps : List String) (h : ∀ p ∈ ps, VE.Route.Gate.known p = true) :
  (todayGate ps = .ok () ↔ ∃ f, VE.Route.Gate.classify ps = .ok f) ∧
  (∀ e, todayGate ps = .error e ↔ VE.Route.Gate.classify ps = .error e)

/-- What each of today's heads may rely on; these are the requirements of the heads' own Lean gates. -/
theorem today_frozen (ps) (h : today ps = .ok .frozen) :
  ∀ p ∈ ["norms@0", "soft-norms@0", "rights@0", "reports@0", "speech-acts@0", "alternatives@0", "risk@0"], p ∉ ps
theorem today_norms (ps) (h : today ps = .ok .norms) :
  "norms@0" ∈ ps ∧ ∀ p ∈ ["soft-norms@0", "rights@0", "speech-acts@0", "alternatives@0", "risk@0"], p ∉ ps
theorem today_soft (ps) (h : today ps = .ok .soft) : "soft-norms@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "rights@0" ∉ ps
theorem today_rights (ps) (h : today ps = .ok .rights) : "rights@0" ∈ ps ∧ "soft-norms@0" ∈ ps ∧ "norms@0" ∈ ps
theorem today_alternatives (ps) (h : today ps = .ok .alternatives) :
  "alternatives@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps ∧ "risk@0" ∉ ps
theorem today_risk (ps) (h : today ps = .ok .risk) :
  "risk@0" ∈ ps ∧ "alternatives@0" ∈ ps ∧ "norms@0" ∈ ps ∧ "soft-norms@0" ∉ ps
theorem today_speech (ps) (h : today ps = .ok .speechActs) : VE.SpeechActs.Wire.profileGate ps = .ok ()
theorem today_reports (ps) (h : today ps = .ok .reports) :
  "reports@0" ∈ ps ∧ ∀ p ∈ ["norms@0", "definitions@0", "data@0", "closure@0", "nary@0", "order@0"], p ∉ ps

/-! ## The stack -/

def base (ps : List String) : List String := ps.filter (fun p => !wrapperProfiles.contains p)

def sitsOn (w : String) (r : Route) : Bool :=
  if w == "ve.discourse@1" then r == .frozen || r == .norms || r == .soft || r == .rights
  else if w == "right-clauses@0" then r == .rights
  else if w == "readings@1" then r == .norms || r == .soft || r == .rights
  else false

def wrapperHead (w : String) : Route :=
  if w == "ve.discourse@1" then .discourse else if w == "right-clauses@0" then .clauses else .readings

/-- The profile that names a route outside the chain. -/
def outside : Route → Option String
  | .reports => some "reports@0" | .speechActs => some "speech-acts@0"
  | .alternatives => some "alternatives@0" | .risk => some "risk@0" | _ => none

def refusal (w : String) (r : Route) : String :=
  match outside r with
  | some b => unsupported s!"{w} with {b}"
  | none => unsupported (if w == "right-clauses@0" then s!"{w} requires rights@0" else s!"{w} requires norms@0")

def dispatch (ps : List String) : Except String Route :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else match today (base ps) with
  | .error e => .error e
  | .ok r =>
    let ws := wrapperProfiles.filter ps.contains
    match ws.find? (fun w => !sitsOn w r) with
    | some w => .error (refusal w r)
    | none => match ws.head? with
      | some w => .ok (wrapperHead w)
      | none => .ok r

def ChainList (ps : List String) : Prop :=
  ps.Pairwise (· < ·) ∧ ∃ r, today (base ps) = .ok r ∧ (r = .norms ∨ r = .soft ∨ r = .rights) ∧
    ∀ w ∈ wrapperProfiles, w ∈ ps → sitsOn w r = true
def stackHead (ps : List String) : Route :=
  match (wrapperProfiles.filter ps.contains).head? with
  | some w => wrapperHead w
  | none => todayHead (base ps)

/-- Today's lists keep today's route, and today's rejections keep today's diagnostic. -/
theorem dispatch_today (ps : List String) (h : ∀ w ∈ wrapperProfiles, w ∉ ps) : dispatch ps = today ps
theorem dispatch_chain (ps : List String) (h : ChainList ps) : dispatch ps = .ok (stackHead ps)
/-- A wrapper that strips its own profile hands dispatch a list it accepts. -/
theorem dispatch_descends (ps : List String) (w : String) (hw : w ∈ wrapperProfiles)
    (h : dispatch ps = .ok (wrapperHead w)) :
  dispatch (ps.filter (· != w)) = .ok (stackHead (ps.filter (· != w)))
/-- Today's discourse lists: the wrapper is the head and what it sits on is today's frozen route. -/
theorem dispatch_discourse_frozen (ps : List String) (hs : ps.Pairwise (· < ·)) (hd : "ve.discourse@1" ∈ ps)
    (hn : "right-clauses@0" ∉ ps ∧ "readings@1" ∉ ps) (hb : today (base ps) = .ok .frozen) :
  dispatch ps = .ok .discourse ∧ dispatch (base ps) = .ok .frozen
/-- Every error is the order error, today's error on the base list, or a named refusal of a wrapper. -/
theorem dispatch_error (ps : List String) (e : String) (h : dispatch ps = .error e) :
  e = unsupported "profiles must be sorted and unique" ∨ today (base ps) = .error e ∨
  ∃ w ∈ wrapperProfiles, w ∈ ps ∧ ∃ r, today (base ps) = .ok r ∧ sitsOn w r = false ∧ e = refusal w r
/-- A refusal names two profiles of the list (with), or one of the list and one it lacks (requires). -/
theorem refusal_names (ps : List String) (w : String) (r : Route) (hw : w ∈ ps) (hr : today (base ps) = .ok r)
    (hn : sitsOn w r = false) (hwp : w ∈ wrapperProfiles) :
  (∃ b ∈ ps, refusal w r = unsupported (w ++ " with " ++ b)) ∨
  (∃ b, b ∉ ps ∧ refusal w r = unsupported (w ++ " requires " ++ b))
end VE.Compose
```

Notes for the review. `todayGate` is a transcription of a Python function and is checked three ways: against the
declarative `TodayList` (`today_sound`, `today_complete`), against the frozen classifier on its registry
(`today_classify`), and against Python on every list (fixture D-all). `VE.SpeechActs.Wire.profileGate` is the
existing gate of `lean/VE/SpeechActs/Wire.lean` (the statement uses its namespace as that file declares it). The
alternatives, risk, rights and reports gates take the environment JSON, so their requirements are stated as
membership facts; each is the list of `unless … contains` checks of that route's `profileGate` or decoder. In
`refusal_names` the `requires` case has `b = "rights@0"` or `"norms@0"`, absent because the base route is below it.

### 9.4 `Content.lean`

```lean
import VE.Rights.Tree

namespace VE.Compose

/-- The content of a reading candidate (plan 2.2) and of a unit whose references are resolved (plan 2.8). -/
inductive Content
  | assertion (φ : VE.Formula)
  | norm (N : VE.SoftNorms.SoftNode)
  | right (R : VE.Rights.Right)
  | rightLines (right : String) (ls : List VE.Rights.SourceLine)
  | limitation (L : VE.Rights.Limitation)
  deriving DecidableEq, Repr

/-- The W2 kind word of a content. -/
def Content.kind : Content → String
  | .assertion _ => "asserted" | .norm _ => "norm" | .right _ => "right"
  | .rightLines _ _ => "right_lines" | .limitation _ => "limitation"

/-- The chain profile a content needs; none for a formula. -/
def Content.needs : Content → Option String
  | .assertion _ => none | .norm _ => some "norms@0" | _ => some "rights@0"

def lineRuleNames (S : VE.Rights.SourceLine) : List String :=
  (S.norm.toList ++ S.liberty.toList ++ S.recognition.toList).map (·.name)

/-- The names a content declares, each with its kind of name: "rule", "right" or "limitation" (1.6). -/
def Content.declared : Content → List (String × String)
  | .assertion _ => []
  | .norm N => [("rule", N.name)]
  | .right R => ("right", R.name) :: (R.lines.flatMap lineRuleNames).map (fun n => ("rule", n))
  | .rightLines _ ls => (ls.flatMap lineRuleNames).map (fun n => ("rule", n))
  | .limitation L => [("limitation", L.name)]

theorem needs_chain (c : Content) (p : String) (h : c.needs = some p) : p = "norms@0" ∨ p = "rights@0"
theorem assertion_declares_nothing (φ : VE.Formula) : (Content.assertion φ).declared = []
end VE.Compose
```

A W1 rule under `norms@0` without `soft-norms@0` is the `SoftNode` with `mode := .strict` and `alterable := []`,
the case in which `soften` changes nothing (`soften_hard_identity`). The wire decoder of a content is S1's
(`lean/VE/Readings/Wire.lean`): it is the existing unit-content decoder of the chain's head, and S0 adds none.

### 9.5 Statements fixed here for later stages (not built in S0)

**The lifting lemma** (4.5), owned by S2a (plan S2), stated now because E10 and E11 depend on it:

```lean
namespace VE.Compose
universe u

/-- B with one new element that lies in no sort and in no tuple. -/
def adjoinOne (B : VE.Structure.{u}) : VE.Structure.{u} where
  Carrier := Option B.Carrier
  domain s v := ∃ x, v = some x ∧ B.domain s x
  constant c := (B.constant c).map some
  relation p vs := ∃ xs, vs = xs.map some ∧ B.relation p xs

theorem adjoin_term (B : VE.Structure.{u}) (ρ : VE.Valuation B) (t : VE.Term) :
  t.denote (adjoinOne B) (ρ.map some) = (t.denote B ρ).map some
theorem adjoin_denote (B : VE.Structure.{u}) (φ : VE.Formula) (ρ : VE.Valuation B) :
  φ.denote (adjoinOne B) (ρ.map some) ↔ φ.denote B ρ
theorem adjoin_admissible (E : VE.Environment) (B : VE.Structure.{u}) : (adjoinOne B).Admissible E ↔ B.Admissible E
theorem adjoin_nonempty (B : VE.Structure.{u}) : Nonempty (adjoinOne B).Carrier
theorem adjoin_baseAdmissibleP (X : VE.SoftNorms.SoftDoc) (P : List VE.Formula) (B : VE.Structure.{u}) :
  BaseAdmissibleP X P (adjoinOne B) ↔ BaseAdmissibleP X P B
end VE.Compose
```

The plan's `adjoin_baseAdmissible` for a rights document is `adjoin_baseAdmissibleP` at `rights_is_slot`. The
argument the review should attack: every case of `Formula.denote` (`lean/VE/Semantics.lean`) is preserved,
because an atom is true only on tuples of old elements, equality compares terms whose values are old elements,
and both quantifiers range over `domain s`, which the new element is never in; `BaseAdmissible'` is admissibility
plus satisfaction of closed formulas. Nothing in it uses readings.

**The superposition statements** (`sup_wellFormed`, `choice_wellFormed`, `encodes_unique`, `superpose_faithful`,
`base_down`, `base_up`, `superpose_conflict_free`, `superpose_all`, `superpose_countermodel`,
`superpose_assertions`), the separation statements (`separates_sound`, `separation_conservative`,
`force_agrees_off_exception`), the clause statements (`plain_identity`, `plain_guard`, `plain_wellFormed`,
`relation_some_bearer`) and the resolution statements (`resolve_identity`, `resolve_position_faithful`,
`resolve_no_new_symbols`, `composed_admission`, `composed_base_unchanged`, `conditions_retained`) are the plan's
sketches (plan section 4). They are not statements under this review; each stage's specification states them
exactly against the code that exists when it is written, using `BaseAdmissibleP`, `ConflictFreeP`, `gate`,
`Content` and `dispatch` as defined here.

### 9.6 What is not claimed

No theorem about `sup`, about any reading set, or that superposition is faithful: that is S2, and for rights it
is unproved until S2b. No claim that the slot theorems hold for a slot that is not closed over the base
vocabulary. No converse of monotonicity. No claim that `dispatch`'s chain heads exist as executables: three of
its eleven routes are built by later stages. No claim that `todayGate` equals the Python function beyond the
tested lists and the two specifications it is proved against; Python is not verified. No theorem about the
English of section 2: one reading per wording is W7's all-derivations gate and W8's fidelity gate, per stage. No
completeness of any conflict check outside norms 7. No coverage number.

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results. Lean fixtures are `#guard` lines of
`lean/VE/Compose/Examples.lean` or the theorems of section 9; Python fixtures are `tests/test_compose_dispatch.py`.
Review protocol: each reviewer derives the expectation of every fixture from sections 1, 4 and 9 before reading
the expected column. Every expected value below was derived by reading the sources at `2205be39`; none has been
executed, and a builder who finds one wrong reports it against this section instead of changing the fixture.

### 10.1 `dispatch`

Lists are written as they are passed. "ok r" is `.ok r`; a text is the complete error string.

| # | List | Expected |
|---|---|---|
| D1 | `relational-fol@0` | ok `frozen` |
| D2 | `closure@0, nary@0, relational-fol@0` | ok `frozen` |
| D3 | `order@0, relational-fol@0, time@0` | ok `frozen` (the quantity route is this head's own choice by `unit_schema`) |
| D4 | `norms@0, relational-fol@0` | ok `norms` |
| D5 | `norms@0, relational-fol@0, soft-norms@0` | ok `soft` |
| D6 | `norms@0, relational-fol@0, rights@0, soft-norms@0` | ok `rights` |
| D7 | `alternatives@0, norms@0, relational-fol@0` | ok `alternatives` |
| D8 | `alternatives@0, norms@0, relational-fol@0, risk@0` | ok `risk` |
| D9 | `norms@0, relational-fol@0, speech-acts@0` | ok `speechActs` |
| D10 | `relational-fol@0, reports@0` | ok `reports` |
| D11 | `documents@1, norms@0, relational-fol@0, soft-norms@0` | ok `soft` |
| D12 | `definitions@0, norms@0, relational-fol@0` | ok `norms` |
| D13 | `relational-fol@0, norms@0` | `UnsupportedProfile: profiles must be sorted and unique` |
| D14 | `alternatives@0, relational-fol@0` | `UnsupportedProfile: alternatives@0 requires norms@0` |
| D15 | `alternatives@0, norms@0, relational-fol@0, soft-norms@0` | `UnsupportedProfile: alternatives@0 with soft-norms@0` |
| D16 | `norms@0, relational-fol@0, risk@0` | `UnsupportedProfile: risk@0 requires alternatives@0` |
| D17 | `relational-fol@0, zzz@0` | `UnsupportedProfile: Unsupported profile zzz@0` |
| D18 | `relational-fol@0, speech-acts@0` | `UnsupportedProfile: speech-acts@0 requires norms@0` |
| D19 | `norms@0, relational-fol@0, soft-norms@0, speech-acts@0` | `UnsupportedProfile: speech-acts@0 with soft-norms@0` |
| D20 | `norms@0` | `UnsupportedProfile: Missing profile relational-fol@0` |
| D21 | `norms@0, relational-fol@0, reports@0` | `UnsupportedProfile: reports@0 with norms@0 layers` |
| D22 | `order@0, relational-fol@0, reports@0` | `UnsupportedProfile: reports@0 requires the fol checker, not order@0` |
| D23 | `closure@0, order@0, relational-fol@0` | `UnsupportedProfile: Unsupported profile combination closure@0 x order@0` |
| D24 | `nary@0, relational-fol@0` | `UnsupportedProfile: Unsupported profile nary@0 without closure@0` |
| D25 | `alternatives@0, norms@0, order@0, relational-fol@0, risk@0` | `UnsupportedProfile: the risk norms route admits FOL documents only` |
| D26 | `norms@0, relational-fol@0, rights@0` | `UnsupportedProfile: rights@0 requires soft-norms@0` |
| D27 | `relational-fol@0, soft-norms@0` | `UnsupportedProfile: soft-norms@0 requires norms@0` |
| D28 | `norms@0, readings@1, relational-fol@0, soft-norms@0` | ok `readings`; with `readings@1` removed: ok `soft` |
| D29 | `norms@0, readings@1, relational-fol@0, right-clauses@0, rights@0, soft-norms@0, ve.discourse@1` | ok `discourse`; removing `ve.discourse@1`: ok `clauses`; then `right-clauses@0`: ok `readings`; then `readings@1`: ok `rights` |
| D30 | `relational-fol@0, ve.discourse@1` | ok `discourse`; with `ve.discourse@1` removed: ok `frozen` (today's discourse list) |
| D31 | `norms@0, relational-fol@0, soft-norms@0, ve.discourse@1` | ok `discourse`; with `ve.discourse@1` removed: ok `soft`. Today's wrapper answers this list `UnsupportedProfile: Unsupported profile soft-norms@0` from the frozen gate (plan section 1, failure 1); it keeps doing so until S4 wires `dispatch` |
| D32 | `readings@1, relational-fol@0` | `UnsupportedProfile: readings@1 requires norms@0` |
| D33 | `norms@0, relational-fol@0, right-clauses@0, soft-norms@0` | `UnsupportedProfile: right-clauses@0 requires rights@0` |
| D34 | `alternatives@0, norms@0, readings@1, relational-fol@0` | `UnsupportedProfile: readings@1 with alternatives@0` |
| D35 | `alternatives@0, norms@0, readings@1, relational-fol@0, risk@0` | `UnsupportedProfile: readings@1 with risk@0` |
| D36 | `norms@0, relational-fol@0, speech-acts@0, ve.discourse@1` | `UnsupportedProfile: ve.discourse@1 with speech-acts@0` |
| D37 | `relational-fol@0, reports@0, ve.discourse@1` | `UnsupportedProfile: ve.discourse@1 with reports@0` |
| D38 | `norms@0, readings@1, relational-fol@0, speech-acts@0` | `UnsupportedProfile: readings@1 with speech-acts@0` |
| D39 | `norms@0, readings@1, relational-fol@0, rights@0` | `UnsupportedProfile: rights@0 requires soft-norms@0` (today's text for the base list passes through) |
| D40 | `readings@1, norms@0, relational-fol@0` | `UnsupportedProfile: profiles must be sorted and unique` |
| D41 | `readings@1, relational-fol@0, right-clauses@0` | `UnsupportedProfile: right-clauses@0 requires rights@0` (two wrappers refuse; the first in stack order answers) |

- **D-all (Python against the specification).** For every strictly increasing sublist of the fifteen registered
  profiles (32,768 lists), `ve.profiles.checker_family` raises exactly when the Python transcription of `TodayList`
  in the test is false, and when it raises, its text equals the text of the first check of 4.2 that fires. Text
  comparison: Python's message with `UnsupportedProfile: ` prefixed unless it already starts with it (the two
  speech-act messages do). The same test asserts rows D1 to D27 on Python and reads rows D1 to D41 from one table
  that `Examples.lean` repeats as `#guard dispatch [...] == ...`, so that the Lean and Python expectations are one
  text. Python has no single routing function, so the head table of 4.2 is not a Python differential: it is
  checked by review against the call sites (`ve/document.py` `_environment`, `ve/admission.py` `admit_document`,
  `ve/backends/lean_runner.py`) and, in Lean, by the `today_<route>` facts against each route's own gate. The
  expected values of this section were derived by reading `checker_family`; no row has been executed yet.
- **D-unsorted.** For 200 seeded permutations of accepted lists that are not increasing, and 50 lists with a
  repeated profile: `profiles must be sorted and unique` from both.
- **D-frozen.** `python3 VE/Route/frozen.py` passes and no file under `conformance/` changes.

### 10.2 The slot

On the documents of `lean/VE/Rights/Examples.lean` (`alpha`: Art. 3, no limitation; `gamma`: Art. 9 under
limitation 29 with two necessary conditions, generated predicates `rights__lim__1`, `rights__cond__1`,
`rights__cond__2`; `eta`: Art. 19 with the bar) and its `model` helper (one state `Texas`, persons `Ann`, `Bob`).

| # | Input | Expected |
|---|---|---|
| L1 | `alpha`, slot `[]` | `limPremises alpha = []`; `backgroundP (correlate alpha) [] = background' (correlate alpha)`; `slotCheck (correlate alpha) [] = true` |
| L2 | `gamma`, slot `limPremises gamma` | `slotCheck = true`; `backgroundP (correlate gamma) (limPremises gamma) = backgroundR gamma`; `backgroundBaseP … = backgroundBaseR gamma` (both `#guard`s on formula lists) |
| L3 | `gamma`, model `M₁` = `arbitrary_arrest`, `rights__lim__1`, `rights__cond__1`, `rights__cond__2` all at (Texas, Ann) | `backgroundValidP (correlate gamma) (limPremises gamma) M₁ = true`, equal to `backgroundValidR gamma M₁` |
| L4 | `gamma`, `M₂` = `M₁` without `rights__cond__2` | `backgroundValidP … (limPremises gamma) M₂ = false` while `VE.SoftNorms.backgroundValid' (correlate gamma) M₂ = true`: the slot, not the soft background, rejects the model (the necessary premise `lim → cond` fails) |
| L5 | `gamma`, slot `limPremises gamma ++ Q` with `Q := [bindAll ["state", "person"] (.not (atom "rights__lim__1" ["state", "person"]))]` ("limitation 29 holds for no arrest") | `slotCheck = true`; `backgroundValidP … M₁ = false`; on `model [("arbitrary_arrest", [["Texas", "Ann"]])]` it is `true`. A longer slot admits fewer bases |
| L6 | `gamma`, slot `[.unary "undeclared" (.var 0)]` | `slotCheck = false`: an open formula over an undeclared predicate is not a slot, and no theorem applies to it |
| L7 | `gamma`, `gate χ (limPremises gamma)` with `χ := .bottom` | `slotCheck = true`; `backgroundValidP (correlate gamma) (gate .bottom (limPremises gamma)) M₂ = true`: a premise gated by a false atom imposes nothing (`sat_gate_off`); with `χ := .top` the value is `false`, as in L4 (`sat_gate_on`) |
| L8 | `eta`, slot `limPremises eta` (empty: no limitation) with the bar | `backgroundValidP (correlate eta) [] aimed = true`; the instance theorems hold with a bar present |
| L9 | theorems | `rights_acceptance_from_slot` and `rights_countermodel_from_slot` compile with statements identical, token for token after `open`, to `VE.Rights.rights_route_acceptance` and `rights_route_countermodel`; the audit lists them with the unchanged allowlist |

### 10.3 Content

| # | Input | Expected |
|---|---|---|
| C1 | `.norm (strictNode "no-deprivation" "deprive_permitted" false)` | kind `norm`; needs `norms@0`; declared `[("rule", "no-deprivation")]` |
| C2 | `.right r9` with `r9` the right of `gamma` | kind `right`; needs `rights@0`; declared `[("right", "r9"), ("rule", "no-arbitrary-arrest")]` |
| C3 | `.rightLines "r9" [arrestClaim]` | kind `right_lines`; declared `[("rule", "no-arbitrary-arrest")]`: the target right is named, not declared |
| C4 | `.limitation l29` | kind `limitation`; needs `rights@0`; declared `[("limitation", "l29")]`: condition names are scoped to their limitation and are not declared names |
| C5 | `.assertion .top` | kind `asserted`; needs nothing; declares nothing |
| C6 | a power line (rights fixture ε) inside `.right` | declared lists the right, then both rule names of the power, liberty first |

### 10.4 The English

Each wording of 2.1 with one instance, checked by the stage that registers it; S0 checks E1 and E2 only.

| # | Instance | Expected |
|---|---|---|
| G1 | E1 for D34 | "This document turns on readings that carry rules and alternatives. VE cannot check these two together yet. Nothing in this document was checked." One derivation |
| G2 | E2 for D33 | "This document turns on clauses on right lines, which needs rights. Nothing in this document was checked." One derivation |
| G3 | the nine feature names of 2.2 | pairwise distinct; none is a prefix of another followed by a space |
| G4 | E14 on plan fixture F1 with decider `unstated` | contains "suppose the decider decides the exception applies"; does not contain "and the exception applies" (S1) |
| G5 | E10 and E11 | never both in one report; E11 only with the fallback of 4.5 (S2) |
| G6 | any sentence of 2.1 rendered for a real document | contains no `ve__`, no `rd-` and no `soft__` or `rights__` substring |

### 10.5 The plan's fixtures

The plan's F1 to F22 (plan section 5) are the acceptance fixtures of the later stages, each stated in full in the
stage's own specification: F1, F2, F4, F5, F15, F19, F22 and the admission half of F6 in `readings.md` (S1); F3
and F18 in S2a's; F6 to F10 and F21 in S2b's; F11 to F14 in `right-clauses.md`, with F13's gated premise as fixture
L7's shape; F16 and F17 in the discourse amendment. S0's share of F20 ("the new profiles off: identities, statuses
and verdicts byte-identical") is D-frozen: S0 turns nothing on.

## 11. Limits, regeneration, Python, Rust

`dispatch` is linear in the list and total; a list longer than the registry plus three wrappers is rejected by
check 1 or check 5. The slot theorems hold for a slot of any length; executables bound a slot by the limits of the
layer that generates it, and every overflow is `ResourceLimit` with the limit named, never a truth value. A slot is
regenerated from the decoded units at every trusted site (norms 11.3); a finite model supplies base tables
including every table the slot mentions, and `backgroundValidP` evaluates the whole slot on it. Python in S0: one
test file, no change to `ve/profiles.py` and no new module. Rust in S0: nothing. From S1 on, Rust never elaborates
a layer: it evaluates the Python-generated formulas of the slot marked `untrusted: true`, and its verdict must
agree with Python's and Lean's regenerated ones (regression evidence; the trust path is Lean). So three-way
agreement for the stack is Lean authority plus two differentials, not three independent implementations (plan open
question 12).

## 12. Statement review checklist (Astra + Fable, before S0's Lean and before any stage specification)

1. The stack (1.1) and the six obligations (4.1): one rank per profile; rule 2's single exception; what S0
   provides against what each layer supplies.
2. `todayGate` (4.2, 9.3) against `ve/profiles.py` `checker_family` line by line: the fifteen checks, their order,
   their texts, the first-offender choices in checks 5, 7, 9, 10 and 11; `TodayList` as its declarative form;
   `today_classify` against `VE.Route.Gate.classify`.
3. The heads (4.2): `alternatives@0`, `risk@0`, `speech-acts@0` lists keep their routes although they contain
   `norms@0`; `reports@0` keeps its own; the checker family and `unit_schema` stay the head's business.
4. The wrappers (4.2): `sitsOn`, the refusal texts, stack order among refusals, `dispatch_descends`,
   `dispatch_discourse_frozen`; that no list today's gate accepts changes route, and no list it rejects changes text.
5. The slot (1.4, 4.3, 9.2): each theorem against its rights original in `lean/VE/Rights/Route.lean`; where `hP`
   is needed and where it is not; the syntactic identity of the premise list; `slot_route_entails_iff` as the
   generalisation of `soft_route_entails_iff`.
6. The instances (9.2): the five definitional facts; `rights_acceptance_from_slot` and
   `rights_countermodel_from_slot` with statements identical to the originals.
7. Monotonicity and gating (4.3, 4.4): `conflictFreeP_append` and its false converse; `sat_gate_on`,
   `sat_gate_off`; the combined slot's order; the gating rule of 1.5 against plan 2.3 and fixture F21.
8. The empty structure (4.5, 9.5): the vacuity argument for `ConflictFree` against W1's arity check; `adjoinOne`
   and `adjoin_denote` case by case against `Formula.denote`; the fallback wording.
9. `Content` (1.6, 9.4): five constructors against plan 2.2's wire; why a bar and a quantity are not contents;
   `declared` against the closure and cross-set rules of plan 2.2.
10. The English (2): one reading per wording; the `<reading>` and `<decider>` slots; E10 against E11; E14 against
    the debate's wording; the non-wordings of 2.2.
11. The report contract (3, 7): `conditional_on` order; the status text with zero-count families omitted.
12. The diagnostics (8) and the fixtures (10), each against the definitions; D1 to D41 derived by hand.
13. Section 6: that S3 and S4 need nothing of S1 or S2.
14. The resolved choices of section 13.

## 13. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **This file is the specification of the stack contract and S0, not of all five stages.** The plan gives each
   stage its own item-1 specification and names three of the files; the converged debate sends S0 to statement
   review first. The later stages' theorems stay in the plan as sketches (9.5).
2. **`dispatch` returns a head for the three wrappers** (`readings`, `clauses`, `discourse`), although two of
   those heads do not exist until S1 and S3. The alternative, a dispatcher that knows only today's eight routes,
   would have each stage redefine the order, which is what the stack exists to prevent.
3. **A missing lower layer is `<a> requires <b>`, not `<a> with <b>`.** The plan's rule 6 names only the `with`
   form for a combination outside the stack. A wrapper over a list that merely lacks its base is not such a
   combination, and today's convention for it is `requires` (`rights@0 requires soft-norms@0`).
4. **`readings@1` requires `norms@0`.** Without it the profile could add only formula candidates, which W2 has
   today without a profile. S1's specification may relax this.
5. **`ve.discourse@1` sits on `frozen` and on the three chain routes, and on nothing else.** Today's discourse
   lists are FOL-family lists over the frozen gate's registry, which includes `norms@0`; on those with `norms@0`
   the route below the wrapper becomes `norms`, whose own identity case delegates a document without a norm
   construct to P0 unchanged, so no document admitted today should change. That is an obligation of S4's
   specification, which must state it for the lists with `norms@0` beside `composed_base_unchanged` for those
   without; S0 proves only `dispatch_discourse_frozen`. The FOL-family requirement stays in the wrapper, with
   today's text.
6. **The checker family and `unit_schema` are not part of the route.** `frozen` covers the four families and the
   quantity route as today; a chain head keeps its own "FOL documents only" abstention.
7. **`todayGate` transcribes Python rather than calling the Lean gates.** No single Lean gate knows all fifteen
   profiles (`VE.Route.Gate.registry` has nine; each statement route checks its own list), and the public behaviour
   to preserve is Python's. The Lean gates are tied in by `today_classify` and the `today_<route>` facts.
8. **`slot_conflict_free` and `slotRoute` take no typing hypothesis**, following the rights proof, which uses
   `limTyped` only for restriction. The plan's sketch carried `hP` on every statement.
9. **`gate` and the labelled slot are S0's.** The debate's combined-slot contract needs gating stated once, and it
   is a fact about closed formulas, not about readings.
10. **`Content` has five constructors, as in the plan's sketch.** A bar candidate is handled by enumeration before
    `sup` and a quantity candidate by W2's route, so neither is a constructor. `declared` is added because the
    converged cross-set check and copy mapping need one definition of a declared name; condition names are scoped
    to their limitation and are not declared names.
11. **The lifting lemma is stated here and built in S2a**, where the converged plan puts it. Recommendation to the
    orchestrator, not applied: prove 9.5's five statements with S0. They import only `VE.Semantics` and 9.2's
    definitions, and proving them first settles E10 against E11 before `readings.md` registers either.
12. **The feature names of 2.2 and the `<reading>` naming rule of 2.1 are proposals** of this draft; the plan
    gives example sentences, not a naming rule. Each goes through W7 with its stage.
13. **`conditional_on` appends the reading to a gated premise's label** (`… under <set>@<v>:<i>`), so that one
    relation line read under two candidates gives two distinguishable entries.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-01 | Draft 1 | First statement specification, from plan draft 2: the stack contract with its six obligations; today's gate transcribed with fifteen checks and its eight routes; `dispatch` with three wrapper heads and named refusals; the base-premise slot with unique expansion, certified conflict-freedom, witness, acceptance, countermodel and exactness relative to a slot; monotonicity; gating; the rights route as the instance `P := Lim_D`; the candidate content type with its declared names; the lifting lemma stated for S2a; eighteen report sentences with their one reading; diagnostics; fixtures D1 to D41 with the exhaustive Python differential, L1 to L9, C1 to C6, G1 to G6; thirteen resolved choices. No code, Lean or frozen contract changes. |
