# Action phrases inside rights and norms: plan

> Status: plan, draft 3 (2026-10-13), branch `design/act-phrases` from `main` at `49de179e`. Draft 1 (`ef82b0a4`,
> 2026-10-12) was revised in draft 2 (`02a57b4e`) by two converged reviews:
>
> 1. the design debate (`manage-agents/debates/design-act-phrases/{fable,astra}.md`, CONVERGED after round 3:
>    REVISE, then BUILD in the order of section 4);
> 2. the cross-plan review of the seven research-wave plans (`manage-agents/debates/plan-synthesis/edits-act-phrases.md`,
>    2026-10-13), appended to both debate files as part of the final joint position.
>
> Draft 3 applies the statement review of the specification (`manage-agents/debates/act-phrases-spec/{astra,fable}.md`,
> CONVERGED after round 2 on **FIX**) where it touches this plan, and nothing else. Section 10 maps every edit to the
> place it was applied. The plan builds design D2 of the research note
> [docs/research/act-phrases.md](../research/act-phrases.md) (sections 4 to 6), which holds the measurements, the prior
> art and the alternatives. Docs only. The specification is [act-phrases.md](act-phrases.md), draft 2 (this commit). It
> writes the definitions, the grammar's rule table, the exact statements, the diagnostics and the fixtures. Where it
> sharpens a statement of section 3 it lists the change (its section 14). No batch except AP-0 starts before the
> bounded re-check of draft 2 (the specification's 13, item 14) and a DRI decision. Every number is measured (method in
> the research note, Appendix A) or labelled *estimate*.

## 0. Summary

A rule regulates an act: "Everyone has the right **to take part in the government of their country, directly or
through freely chosen representatives**." Today the act is a string of at most 80 characters with no *and*, *or*,
*for* or comma, and VE treats it as a name. This plan turns act phrases into parsed English, in five steps:

1. **AP-1, long single acts.** An act may be long and may hold declared **fixed phrases**: groups of words, possibly
   with *and*, *or* or *for*, that name one thing and are not analysed. Its slots bind the rule's arguments, at most
   two today. A plain entitlement gets an honest English wording ("has the right to …") instead of "classified as …".
   Lean decides acceptance. An act AP-1 accepts keeps its canonical string as its identity and its meaning for ever: it
   never enters the act grammar (2.5).
2. **AP-2, the act grammar** (Lean only). It reads an act phrase against the document's declared **frames** (a verb
   and the prepositions that introduce its arguments), on the proved grammar engine. A phrase has a reading only when
   Lean has enumerated every derivation within its budgets. A phrase over a budget is refused, never read one way (D2).
3. **AP-3, joined acts.** Acts joined by *and* / *or* become rules on simple acts, by one fixed table per modal word
   (*must*, *must not*, *may*, *has the right to*). The result is an ordinary `norms@0` document, so every existing
   theorem applies. A mandatory relay, `acts-elaborate`, gives Python the elaborated document and the map from each
   generated predicate and rule to its source, so Python's conflict search runs on what Lean elaborated.
4. **AP-4, readings from derivations.** Where the English gives more than one structure (a modifier over a list, a
   prepositional phrase that can attach in two places, *may* or *right to* with *or*), the readings are the phrase's
   derivations, each read through the table. A reading set that names its source phrase and its source rule is checked
   to be exactly those readings: one choice per reading, each with the source rule's modal, sign, guard, carve-outs,
   precedence and completion. The separating situations are built by Lean.
5. **AP-5, specialisation (definitions only).** Lean defines when one simple act is a way of doing another. It counts
   only the markers and modifiers the document declares restrictive, and generates the premises standard deontic logic
   licenses for permission and obligation. Nothing uses them until **AP-5b**, a separately reviewed bridge over base
   predicates, passes. Only then may they enter the layered route, as the last premise pack of PK-1, under the opt-in
   profile `act-specialise@0`.

AP-0 is a measured baseline with no code; it also measures the raw derivation budget N (D2). AP-6 to AP-8 are
experiments with pre-registered bars.

**Exactness is relative to the declared vocabulary.** A reading set is exact with respect to the document's declared
fixed phrases and frames, which readers see and audits check (8.2). AP-7's percentages are evidence about that
vocabulary, not a one-reading guarantee. A known ambiguity the grammar does not model is refused or rephrased.
Measured recall does not establish completeness for unrestricted English.

| Batch | What | Hours (draft 1, withdrawn) | Moves a pilot number | UDHR bytes (*estimate*) |
|---|---|---|---|---|
| AP-0 | baseline: re-try the 11 units under today's language; count "classified as" sentences; tag constitution workarounds; measure N | 2, pilot job, no product code | M1 (if any unit is expressible today), M3 measured | measured, not estimated |
| AP-1 | `acts@0`: long single acts, fixed phrases, entitlement wordings | 6 | M1, M2, M3, M4 | 457 (u039, u085, u106); up to 658 with u091 |
| AP-2 | the act grammar on `VE.Grammar` (Lean only) | 5 | none (enabler) | 0 |
| AP-3 | joined acts split by the table; the `acts-elaborate` relay | 5 | M1, M2, M4 | 76 (u079b) |
| AP-4 | readings from derivations; exact reading sets | 6 | M1, M2, M5 | 163 (u092); u076's 125 wait for the readings elaboration (spec F11) |
| AP-5 | specialisation: `Specialise.lean` and its examples only | 4 | nothing until AP-5b | 0 |
| AP-5b | design and review: the base-level bridge for `act-specialise@0` | — | nothing by itself | 0 |
| AP-6 | experiment: n-ary bound slots (two routes) | 4 | decision | (u019, u057 co-blocked: 389) |
| AP-7 | experiment: do derivations find the auditors' readings? | 3 | decision | — |
| AP-8 | experiment: frames proposed from sense packs | 3 | decision | — |

The hours are draft 1's figures. The design debate withdrew them (and its own 41 h correction): the build estimate is
redone once the specification's contracts pass the statement review. Draft 1's total was about 38 h (*estimate*,
withdrawn). UDHR claimed coverage is 43.90% today; after AP-1, AP-3 and AP-4 it would be about 50.3% to 52.1%
(*estimate*, before audits; draft 2 said 51.4% to 53.3% before the statement review deferred u076, spec F11).

Pilot metrics (values at run `20261012T1800Z`):

| Metric | Value now |
|---|---|
| M1: UDHR bytes whose primary blocker is act-phrase grammar | 1,860 B, 11 units |
| M2: covered UDHR units carrying an act approximation | 5 units, 669 B |
| M3: natural-view sentences reading "classified as …" or "has the recorded relation …" | unmeasured; AP-0 |
| M4: constitution norm units on a pointer, folded or shortened act | 18 units, 2,580 B |
| M5: hand-made reading sets for coordination or modifier scope that Lean does not check against the English | 3 sets: rs_u055, rs_u105b, rs_u105c |

## 1. Decisions this plan asks for (DRI)

| # | Decision | Recommendation | Needed before |
|---|---|---|---|
| D1 | How `acts@0` enters | A decoding extension of `norms@0`: the act check and the elaboration are chosen by the document's profiles inside the existing decoders. It is not a composition wrapper: no new route head. The only new responses are AP-3's mandatory `acts-elaborate` relay and AP-4's `act-readings` proposal mode, each through the relayed-route recipe. | AP-1 |
| D2 | Budgets | Act phrase ≤ 400 bytes; fixed phrase ≤ 300 bytes; ≤ 128 fixed phrases and ≤ 128 frames per document. Two separate parse limits: a **raw derivation budget N** (the parser's cap; AP-0 measures the largest raw count over the pilots' act phrases and N is fixed above it) and a **public limit of 64 distinct readings** (= the `readings@1` limit), beside the engine's step budget. `read` (one reading required) and `readings` (listing) use the same limits. A reading is certified only from a complete enumeration: fewer than N raw derivations, within the step budget. Raw-cap saturation, an exhausted step budget, or more than 64 readings is an explicit **limit** outcome: a refusal, never a choice. Exactly 64 readings are accepted when the enumeration is complete. | AP-1 |
| D3 | The modal × connective table (2.3) | as written; its equations stay provisional until AP-7 passes; frozen when AP-3 merges, which is after AP-7 | AP-3 |
| D4 | The edge rule for modifiers (2.4) | as written; provisional until AP-7 passes; frozen when AP-4 merges, after AP-7 | AP-4 |
| D5 | Specialisation premises | permission and obligation only, licensed by standard deontic logic, and only through markers and modifiers the `acts` block declares restrictive (visible semantic assumptions); entitlements stay UNKNOWN between related acts. The premises take effect only under the opt-in profile `act-specialise@0`, after AP-5b | AP-5 (definitions); AP-5b (use) |
| D6 | n-ary route | decided by AP-6's pre-registered bar; route (a) reifies over `events@0`'s event sorts | after AP-6 |
| D7 | Reading-set sources | optional under `acts@0`; mandatory in the UDHR and constitution pilots once AP-4 merges | AP-4 |
| D8 | Trust budget | AP-1 to AP-5 add proved Lean only; if `trust_map.py` reports growth beyond the signed budget, the DRI signs a reason (`trust_map.py --write --reason`) | each batch |

## 2. Design

### 2.1 What people write and read

A translator writes the source sentence as a VE unit, as today. Its rule names a regulated predicate whose
declaration carries the act phrase, now in full:

```json
"has_the_right_to_a_hearing": {
  "arguments": ["person", "determination"],
  "description": "The person is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in the determination",
  "regulated": {"role": "plain", "default": "unspecified", "form": "is entitled",
                "act": "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"}
}
```

The document's vocabulary gains an `acts` block (2.8). It lists the fixed phrases, here "a fair and public hearing
by an independent and impartial tribunal", and from AP-2 on the frames. The unit's guard says which determinations
count ("the determination is of the rights and obligations of the person or of a criminal charge against the
person"), in the guard English VE already reads.

A reader sees the sentence "Every person is entitled in full equality to a fair and public hearing by an independent
and impartial tribunal in each determination that …". Where the English has two structures, the reader also sees
one plain sentence per reading. For u051:

> This sentence has two readings.
> 1. Everyone has the right to seek asylum from persecution in other countries, and everyone has the right to enjoy
>    asylum from persecution in other countries.
> 2. Everyone has the right to seek asylum from persecution, and everyone has the right to enjoy asylum from
>    persecution in other countries.

In authoring, the writer picks one. Each simple act of the chosen reading reads back with one meaning, by AP-2's
`read_normal`; the paraphrases of one listing are pairwise distinct (the specification's 6.2). In translation,
both stay, as a reading set whose source is the original phrase (AP-4). Nobody sees brackets, slots or frames. The
IDE asks in plain words ("Is 'a fair and public hearing by an independent and impartial tribunal' one thing?").

### 2.2 The act grammar (AP-2)

Tokens are words, declared fixed phrases (longest match, read as one token), slots `{i}` and commas. A curly
apostrophe is read as `'`. A **frame** is a head with its **markers**: the words that may introduce its arguments.
The head is a verb of one or more words ("take part"), or, after *has the right to* / *is entitled to*, a noun
("security", "protection"). `""` stands for the direct object (`["", "from", "in"]` for *seek*). A frame also lists
the markers whose joined fillers read as joined acts (its `split` markers, 2.3).

The grammar, informally (the specification's rule table is the grammar):

```text
act      := [premods] item { "," item } [","] join item [postmods] | [premods] item [postmods]
join     := "and" | "or" | "nor"
item     := ["to"] [premods] head { arg } [postmods]       -- head: a declared frame's head
arg      := [marker] filler                                -- marker: one of the frame's markers
filler   := slot | fixedphrase | word { word }             -- words: no join word, no comma, no clause word
premods  := modword { modword }                            -- e.g. "freely", "arbitrarily", "actively"
postmods := post { post } | post { "," post } [","] join post
post     := modword | marker filler                        -- a prepositional modifier: "in other countries"
```

A shared object or argument after the last joined item belongs to every item ("to seek and to enjoy … **asylum from
persecution**"). The meaning of a derivation is an **act tree**: `one` simple act, `all` (joined by *and*) or `any`
(joined by *or* or *nor*). `all` records whether its items share one *to* ("to seek and enjoy") or each has its own
("to seek and to enjoy"). Both `all` and `any` record whether the join is a split marker's (2.3), and `any` records
whether it is *nor*. A simple act is a head, its arguments (marker and filler) and its modifiers.

**There is no fallback rule.** An act AP-1 accepts never enters the grammar: its identity and its meaning are its
canonical string, permanently. The grammar reads only phrases that AP-1 refuses for their join words or commas. Where
AP-5 needs the structure of an unjoined act, it calls a separate `analyse`, which returns a simple act only when the
phrase has exactly one meaning, and renames nothing. Two derivations with equal act trees are one reading; two with
different trees are two readings. So `read` requires one **meaning**, not one derivation tree, and certifies it only
from a complete enumeration (D2).

**Clause words** are refused anywhere in an act, fixed phrases included: *true false is equals not if then every
there exists believes must eventually no*. That is today's `actReserved` without *and*, *or* and *for*. A finite
clause ("of which he is the author", "if necessary") belongs in the rule's guard, written in guard English. This is
the same division `right-clauses@0` makes between act phrase and clause. **Join words** (*and, or, nor, for*) and
commas may stand outside fixed phrases only in AP-2's grammar positions (`join`, list commas, *for* as a marker or a
modifier), from AP-3 on. *Either*, *neither* and *both* are ordinary words until a join word follows them. The
refusals AP adds for authored text (clause words in an act, *nor* under *may*, *must* and *has the right to*, "too
many readings") go into english-lean's catalogue as rows, if that catalogue holds refusals by then.

### 2.3 The modal × connective table (AP-3; decision D3)

A rule's modal word is fixed by its role and sign:

- *must*: obligation, sign true;
- *need not*: obligation, sign false;
- *may*: permission, sign true;
- *must not*: permission, sign false;
- *has the right to* / *is entitled to*: plain, sign true.

For each modal and each join, the table gives the **readings**: one or more lists of simple acts the rule stands for.
A single reading is applied by AP-3. Two readings make the sentence ambiguous; AP-4 handles that.

| Modal | "A and B" | "A or B" / "A nor B" |
|---|---|---|
| *must* | one reading, split: must A; must B (obligation distributes over *and*) | one reading, **one act** "A or B": the bearer chooses the way (obligation does not distribute over *or*) |
| *must not* | two readings: each is forbidden (split), or only doing both (one act "A and B") | one reading, split: must not A; must not B (prohibition distributes over *or*) |
| *may*, *has the right to* | one reading, split, when every item has its own *to* ("to form and to join"); otherwise ("to seek and enjoy", "may form and join") two readings: each (split), or both together (one act) | two readings: each way (free choice, split), or one act "A or B" |
| *need not* | no reading: refused (no pilot case; rewrite) | no reading: refused |

**Nor** reads only under *must not*, where prohibition distributes over it. Under *must*, *may* and *has the right
to* it has no reading, and the writer rewrites. The table's theorems take the split-marker and *nor* flags of the act
tree as conditions (section 3). Its equations stay provisional until AP-7 passes (D3).

The table holds the deontic distribution equations for the five modals of `VE.Acts.Op`. It is never reused for
`intends` or `believes`, and a joined act under an attitude verb is not split by it.

Readings multiply over nested joins and with the derivations of 2.4. Equal lists of simple acts are one reading.

**Joined modifiers** ("directly or through freely chosen representatives") read as joined acts, one per modifier,
and go through the table.

**Joined fillers of a frame's `split` markers** go through the table too: "subjected to torture or to cruel …
treatment" reads as "subjected to torture" or "subjected to cruel … treatment". There is one difference. A split
marker has no "one act" or "together" reading, because the frame declares that argument distributive. So:

- under *may* or *has the right to*, its *or* has one reading, each (u092's causes);
- under *must not*, it splits as any *or* does;
- under *must*, its *or* has no reading and the writer rewrites.

Other markers keep a joined filler as one filler inside one simple act: u079b's "by secret vote or by equivalent free
voting procedures" is one act. The `split` list is how a frame says an argument is distributive; "the consent of the
intending spouses" is not split, which is u059's point.

Splitting gives one regulated predicate per simple act, named `<pred>__<i>` with the reserved prefix the
specification fixes. A name over the length limit is refused, never shortened silently. The elaborated document passes
the route's own limits again (regulated predicates, rules, vocabulary with the parts and unsaid predicates counted,
unspecified names), with their existing diagnostics (specification 6.3). Two parts of one predicate with the same act
are refused for every role, plain entitlements included. Each source rule becomes one
rule per simple act, named `<rule>-a<i>`, with the same guard, carve-outs and completion. An `unspecified` predicate's
parts are `unspecified` too. Precedence follows the simple acts (`M over N` gives `M-a<i> over N-a<i>`). The source
predicate is removed; a later reference to it is refused with "name one of its parts" (the specification's reference
table lists every place a predicate can be named).

An obligation and its permission dual must read alike. AP-3 refuses a predicate unless every rule on it and on its
dual gives the same list of simple acts ("write the parts as separate predicates"), so `actChecks` sees matching acts.
An obligation on "A or B" keeps one act while a prohibition on its dual splits, so that combination is refused.
Relations between an aggregate act and its components are deferred.

### 2.4 Modifier scope and attachment (AP-4; decision D4)

- A modifier **before** a list of joined items reads over the first item or over all of them.
- A modifier **after** the list, or a prepositional phrase in the last item before a shared object, reads over the
  last item or over all of them.
- A modifier inside a middle item reads over that item only.
- **No skipped middle:** a modifier never reads over some of the items but not one between them.

So u105's *freely* has two readings, which is what its 2026-10-10 audit required. u055's *arbitrarily* has two,
the pilot's `both_acts` and `deprivation_only`. u051's "in other countries" has two. Several edge modifiers multiply
their readings, up to the 64-reading limit. Beyond it, or when the enumeration reaches the raw derivation budget N or
the step budget, the phrase is refused ("too many readings to list; split the sentence"), never read one way. The
edge rule stays provisional until AP-7 passes (D4).

### 2.5 Nothing accepted earlier changes meaning

AP-1 accepts only acts with no join word or comma outside fixed phrases (`Lexical.check_no_join`). Such an act never
enters the grammar: its identity and its meaning are its canonical string, permanently (there is no fallback rule,
2.2). AP-3 and AP-4 give meaning only to phrases AP-1 refused. Every act `canonicalAct` accepts today, `acts@0`
accepts with the same canonical string (`check_extends`, stated in a module above both `Norms.Wire` and
`Acts.Lexical`), with one exception. An act containing *nor* is one unanalysed act today, and AP-3 gives *nor* a
meaning, so `acts@0` refuses it outside a fixed phrase rather than let its meaning change. Act identity stays
`(sorts, canonical act, role)` with the canonical act **as written**. The normal order (`Atom.normal` in section 3:
head, object, marked arguments in frame order, modifiers) is used only for generated paraphrases and for the simple
acts of a split, never to rename a declared act.

### 2.6 Specialisation (AP-5, AP-5b; decision D5)

Simple act *a* specialises simple act *b* (`a ⊑ b`) when:

- they have the same head;
- every argument of *b* is an argument of *a* with the same filler;
- every modifier of *b* is a modifier of *a*;
- every argument or modifier that *a* has beyond *b* is introduced by a marker or modifier that the `acts` block
  declares **restrictive**.

Syntax alone supplies no implication. "Nearly destroy the records", "destroy the records in a simulation" or "in
name only" do not narrow the act, so such words never count unless declared, and a declaration is a visible semantic
assumption that the audit checks. The IDE asks in plain words: "Is seeking asylum in other countries a way of seeking
asylum?"

For two declared simple acts with the same role and argument sorts and `a ⊑ b`, Lean generates the premise
`∀ x̄. p_a(x̄) → p_b(x̄)`:

- **permission:** may seek asylum in other countries → may seek asylum;
- **obligation:** must seek asylum in other countries → must seek asylum.

Both are the RM rule of standard deontic logic: doing *a* is a way of doing *b*. The contrapositive of the
permission premise is "must not *b* → must not *a*". Plain entitlements get no premise (D5).

These premises mention regulated permission and obligation predicates. The layered route's extra premises `X`, and
every carried premise slot, need closed **base** formulas; `lean/VE/Readings/SupExtra.lean:14–19` records that a
carried premise over a regulated predicate makes the approved statement false. So AP-5 builds only the definitions
and the generator: it has no Background hook and is not a premise pack. **AP-5b**, a separately reviewed base-level
bridge, (a) states the opt-in `act-specialise@0` meaning over base predicates, (b) justifies any substitution of
outcome formulas for regulated predicates and (c) proves that conflict-freedom with the specialisation premises is not
vacuous. Only after AP-5b passes may specialisation become PK-1's last pack, under `act-specialise@0`, so no accepted
document's consequences change without the opt-in. The legend then shows each premise as one plain sentence.

### 2.7 Arguments: fixed, bound, and more than two

A filler is a slot bound to one of the rule's arguments (a situation variable, universally quantified as every rule
variable is) or fixed words. A regulated predicate keeps one or two arguments in AP-1 to AP-5. A finite clause about
a bound filler goes into the guard. More than two bound slots ("a duty of a bearer to a person on a ground", u019 and
u057) waits for AP-6.

### 2.8 Wire (AP-1, extended by AP-2, AP-4 and AP-5)

Under `acts@0` only (D1):

- the vocabulary gains `"acts": {"fixed": [...], "frames": [...], "sources": [...]}`, and from AP-5 the restrictive
  declarations;
- a regulated declaration's `act` is checked by `VE.Acts.Lexical.check` (AP-1) or `VE.Acts.read` (AP-2 on) instead
  of `canonicalAct`, and `canonicalEnvironmentJson` applies the same check;
- a plain declaration may carry `act` and `form` ∈ {"has the right", "is entitled"}, and `Norms.Tree.check` admits an
  act on a plain predicate.

Every field is part of the canonical environment bytes, so `environment_id` changes when any of them changes and is
unchanged for every existing environment. Without `acts@0` the decoders are today's (`decodeRegulated_without_acts`).

### 2.9 Who owns what

| Piece | Owner | Others |
|---|---|---|
| Accepting acts, fixed phrases, frames; reading acts; the table; elaboration and its source map; readings; source exactness; specialisation premises; honest wordings | Lean (`lean/VE/Acts/*`, the hooks listed per batch) | — |
| Loading the `acts` block, reading AR-10's generated profile data, CLI, display of Lean's wordings and paraphrases, relaying AP-3's `acts-elaborate` answer and AP-4's proposal mode (schema and binding only), and running the conflict-witness search on the relayed document | Python | no check, no split, no paraphrase computed in Python |
| Fast checks | Rust | Rust refuses every `acts@0` environment with `UnsupportedProfile`, as it refuses an `unspecified` completion today, and Lean answers it; no copy of the grammar (draft 2's "skip the act lint" was not enough: Rust also refuses the `acts` key and a plain `act`, and does not fold `’`) |

**Not duplicated:** the reserved list (Lean's `actReserved`, filtered), verb morphology (`conjugatedAct` and
`verbBase` in Lean), the wording lint (Lean V6), and the reading-set separation (`separates`).

**Retired for `acts@0` documents:** Python's display fallback for plain predicates (their wording is Lean's), Rust's
decoding (it refuses them), and the retained Python norms path: `_lean_route` is true for `acts@0` documents and the
retained path refuses them. Python lexes no act and composes no act diagnostic: it binds Lean's token spans and indices,
and relays the "name one of its parts" text Lean writes. **Not touched:** Python's norm-sentence matcher. It matches a declared act as one exact terminal today
and keeps doing so; moving it to Lean is E3's.

## 3. Lean statements

These are the statements the specification and the statement review start from. Names follow the existing modules.
Each block's header names its file and batch. Bodies are omitted; every theorem is proved in its batch, with no
`sorry` and only the allowed axioms (`lean/audit.py`). The specification writes each statement exactly; where it
differs from this section it says so (its section 14). Its draft 2 adds, from the statement review (its 14.3):
`elaborate_parts`, `distinctTexts_ok`, `paraphrases_nodup`, `checkAuthorN_split`, `decodeElaboratedU_source`,
`decodeElaboratedU_wellFormed`, `decodeElaboratedU_lexical` and `readings_lexical_only`; and it changes `Source` (a
three-valued completion), `SourceExact` (rules compared up to order), `elaborate_identity`'s hypotheses, and the
definitions `framesOk` and `normalOk` that `grammar_wf` and `read_normal` assume. The blocks below are draft 2's and
are not rewritten.

```lean
/-! lean/VE/Acts/LexicalBase.lean (AP-1): below `Norms.Wire`. It holds `actReserved` and `words` (and the
    helpers they need), so that `Acts.Lexical` and `Norms.Wire` do not import each other. -/

/-! lean/VE/Acts/Lexical.lean (AP-1) -/
namespace VE.Acts.Lexical

/-- Words an act may hold only inside a declared fixed phrase in AP-1 (and in AP-2's join positions later). Of these,
    `canonicalAct` already refuses all but "nor". -/
def joinWords : List String := ["and", "or", "nor", "for"]
/-- Words no act may hold, fixed phrases included: today's `actReserved` without the join words. -/
def clauseWords : List String := VE.Norms.Wire.actReserved.filter (fun w => !joinWords.contains w)

inductive Tok | word (w : String) | fixed (i : Nat) | slot (i : Nat) | comma
  deriving DecidableEq, Repr

/-- Declared fixed phrases: each non-empty, ≤ 300 bytes, no slot, no clause word, none inside another, ≤ 128. -/
def fixedOk (fx : List String) : Bool
/-- Tokens: fixed phrases by longest match, slots, words, commas; `’` read as `'`. -/
def lex (fx : List String) (s : String) : Except String (List Tok)
/-- AP-1 acceptance: `{0} ` first, slots `{0}…{k-1}` once each in order, ≤ 400 bytes, ≥ 2 tokens, words of letters
    with inner `'` or `-`, no clause word, no join word or comma outside a fixed phrase. Returns the canonical act. -/
def check (fx : List String) (name : String) (arity : Nat) (raw : Lean.Json) : Except String String

theorem check_no_join {fx name k raw a} (hc : check fx name k raw = .ok a) {ts : List Tok} (hl : lex fx a = .ok ts) :
    ∀ t ∈ ts, (∀ w, t = .word w → !joinWords.contains w.toLower) ∧ t ≠ .comma
theorem check_no_clause {fx name k raw a} (hc : check fx name k raw = .ok a) :
    ∀ w ∈ VE.Norms.Wire.words a, !clauseWords.contains w.toLower

inductive Form | right | entitled
/-- The honest wording of a plain predicate with an act: "{0} has the right …" or "{0} is entitled …", then the act
    after its `{0} `. -/
def wording (f : Form) (act : String) : String
theorem wording_subject_first (f : Form) (act : String) (h : act.startsWith "{0} ") :
    (wording f act).startsWith "{0} " = true
end VE.Acts.Lexical

/-! lean/VE/Acts/Compat.lean (AP-1): above both `Norms.Wire` and `Acts.Lexical`. -/
/-- Every act today's check accepts and that has no "nor" is accepted with the same canonical string. An act with
    "nor" (one unanalysed act today) is refused under `acts@0` until AP-3 gives "nor" its meaning (2.5). -/
theorem VE.Acts.Lexical.check_extends (fx : List String) (h : fixedOk fx = true) {name : String} {k : Nat}
    {raw : Lean.Json} {a : String} (hc : VE.Norms.Wire.canonicalAct name k raw = .ok a)
    (hn : ∀ w ∈ VE.Norms.Wire.words a, w.toLower ≠ "nor") : check fx name k raw = .ok a

/-! lean/VE/Norms/Wire.lean, three changes (AP-1): the act check is chosen by the document's profiles in the
    decoder, and `canonicalEnvironmentJson` applies the same check; `Norms.Tree.check` admits an act on a plain
    predicate (its refusal at `Tree.lean:314`). -/
def VE.Norms.Wire.decodeRegulatedIn (profiles : List String) (fx : List String) :
    String → List String → Lean.Json → Except String VE.Norms.Regulated
theorem VE.Norms.Wire.decodeRegulated_without_acts (ps fx : List String) (h : "acts@0" ∉ ps) :
    decodeRegulatedIn ps fx = decodeRegulated

/-! lean/VE/Compose/Dispatch.lean, one row of AR-10's profile-gate table (AP-1): `acts@0` with
    `requires := ["norms@0"]`, and the composition theorem for every combination the row newly admits. Python reads
    the generated data. -/

/-! lean/VE/Acts/Syntax.lean and Grammar.lean (AP-2) -/
namespace VE.Acts

structure Frame where
  head : List String         -- a verb, or a noun after "has the right to" / "is entitled to"
  markers : List String      -- "" is the direct object
  split : List String        -- markers whose joined fillers read as joined acts (2.3)
  deriving DecidableEq, Repr

inductive Filler | slot (i : Nat) | fixed (i : Nat) | words (ws : List String)
  deriving DecidableEq, Repr

structure Atom where
  head : List String
  args : List (String × Filler)      -- marker and filler, as written
  mods : List (List Lexical.Tok)     -- modifiers, as written
  deriving DecidableEq, Repr

/-- `all shared split xs`: joined by "and"; `shared` when the items share one "to" (2.2); `split` when the join is
    a split marker's (2.3). `any nor split xs`: joined by "or", or by "nor" when `nor`. -/
inductive Act | one (a : Atom) | all (shared split : Bool) (xs : List Act) | any (nor split : Bool) (xs : List Act)

def framesOk (fs : List Frame) : Bool
def Term : Type                                  -- the grammar's terminals over `Lexical.Tok`
instance : VE.Grammar.Accepts Term Lexical.Tok
def grammar (fs : List Frame) : VE.Grammar.Grammar Term
def meaning (fs : List Frame) : VE.Grammar.Meaning Lexical.Tok Unit String Act

theorem grammar_wf (fs : List Frame) (h : framesOk fs = true) : (grammar fs).wf = true

/-- A listing: every reading, complete; or the limit outcome (raw derivation budget `N` reached, step budget `b`
    exhausted, or more than 64 readings), which is a refusal. -/
inductive Listing (α : Type) | ok (xs : List α) | limit
/-- Every reading, equal act trees once, in derivation order (translation). -/
def readings (fs : List Frame) (N b : Nat) (ts : Array Lexical.Tok) : Listing Act
/-- One reading required (authoring, and every declared act): `readings` with exactly one element. -/
def read (fs : List Frame) (N b : Nat) (ts : Array Lexical.Tok) : VE.Grammar.Outcome Lexical.Tok String Act

/-- One meaning: some derivation means `(A, c)`, and every derivation that has a meaning means `(A, c)`. -/
theorem read_unique (fs) (h : framesOk fs = true) {N b ts A c} (hr : read fs N b ts = .ok A c) :
    (∃ d, VE.Grammar.Derives (grammar fs) (.n (grammar fs).start) ts.toList d ∧ meaning fs () d = .ok (A, c, ())) ∧
    ∀ d B c', VE.Grammar.Derives (grammar fs) (.n (grammar fs).start) ts.toList d →
      meaning fs () d = .ok (B, c', ()) → B = A ∧ c' = c
/-- Complete enumeration: no length hypothesis; `.ok` already means fewer than `N` raw derivations. -/
theorem readings_exact (fs) (h : framesOk fs = true) {N b ts As} (hp : readings fs N b ts = .ok As) (A : Act) :
    A ∈ As ↔ ∃ d c, VE.Grammar.Derives (grammar fs) (.n (grammar fs).start) ts.toList d ∧ meaning fs () d = .ok (A, c, ())
theorem readings_nodup (fs) {N b ts As} (hp : readings fs N b ts = .ok As) : As.Nodup

/-- The structure of an unjoined act, for AP-5 only: a simple act exactly when the phrase has one meaning and it is
    `one`. It renames nothing (2.2). -/
def analyse (fs : List Frame) (N b : Nat) (ts : Array Lexical.Tok) : Option Atom

/-- Render round trip: the normal form of a simple act (verb, object, marked arguments in frame order, modifiers)
    reads back with one meaning as the same act in normal order. -/
def Atom.normal (fs : List Frame) (a : Atom) : List Lexical.Tok
def Atom.canon (fs : List Frame) (a : Atom) : Atom
def atomOk (fs : List Frame) (a : Atom) : Bool
theorem read_normal (fs) (h : framesOk fs = true) (a : Atom) (ha : atomOk fs a = true) :
    ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read fs N b (a.normal fs).toArray = .ok (.one (a.canon fs)) false
end VE.Acts

/-! lean/VE/Acts/Table.lean and Elaborate.lean (AP-3) -/
namespace VE.Acts

inductive Op | must | needNot | may | mustNot | right
  deriving DecidableEq, Repr
def opOf (r : VE.Norms.Regulated) (sign : Bool) : Op

/-- 2.3: the readings of a rule with modal `op` on act `A`, each the list of simple acts it stands for.
    `[]`: no reading (refused); two or more: the English is ambiguous (AP-4). -/
def table (fs : List Frame) : Op → Act → List (List Atom)
/-- The one act a join stands for when it is not split ("A or B" under must; "A and B" done together). -/
def Atom.joined (fs : List Frame) (A : Act) : Atom
def simple : List Act → Option (List Atom)        -- `some` when every item is `one`

theorem table_one (fs op a) : table fs op (.one a) = [[a]]
theorem table_must_all (fs s sp xs as) (h : simple xs = some as) : table fs .must (.all s sp xs) = [as]
theorem table_must_any (fs xs) (h : 2 ≤ xs.length) : table fs .must (.any false false xs) = [[Atom.joined fs (.any false false xs)]]
theorem table_must_any_refused (fs n sp xs) (h : n = true ∨ sp = true) : table fs .must (.any n sp xs) = []
theorem table_mustNot_any (fs n sp xs as) (h : simple xs = some as) : table fs .mustNot (.any n sp xs) = [as]
theorem table_mustNot_all (fs s xs as) (h : simple xs = some as) (h2 : 2 ≤ xs.length) :
    table fs .mustNot (.all s false xs) = [as, [Atom.joined fs (.all s false xs)]]
theorem table_mustNot_all_split (fs s xs as) (h : simple xs = some as) : table fs .mustNot (.all s true xs) = [as]
theorem table_may_all_own (fs sp xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as) :
    table fs op (.all false sp xs) = [as]
theorem table_may_all_shared (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as)
    (h2 : 2 ≤ xs.length) : table fs op (.all true false xs) = [as, [Atom.joined fs (.all true false xs)]]
theorem table_may_all_split (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as) :
    table fs op (.all true true xs) = [as]
theorem table_may_any (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as)
    (h2 : 2 ≤ xs.length) : table fs op (.any false false xs) = [as, [Atom.joined fs (.any false false xs)]]
theorem table_may_any_split (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as) :
    table fs op (.any false true xs) = [as]
theorem table_may_nor (fs sp xs) (op) (hop : op = .may ∨ op = .right) : table fs op (.any true sp xs) = []
theorem table_needNot (fs A) (h : ∀ a, A ≠ .one a) : table fs .needNot A = []

/-- A document whose acts@0 predicates carry their read act trees; `U` is the `norm-defaults@0` form
    (`unspec = []` for a plain `norms@0` document). -/
structure ActsDoc where
  U : VE.NormDefaults.UDoc
  frames : List Frame
  acts : List (String × Act)

def WellFormedActs (D : ActsDoc) : Bool
/-- AP-3: every rule on an act with exactly one reading becomes rules on its simple acts; any other count refuses,
    and so does a predicate whose rules, or whose dual's rules, give different lists of simple acts. -/
def elaborate (D : ActsDoc) : Except String VE.NormDefaults.UDoc

/-- The source-to-generated map the `acts-elaborate` relay binds (cross-plan edit 1). -/
structure SplitMap where
  preds : List (String × String × Nat)   -- generated `p__i`, its source predicate, i
  rules : List (String × String × Nat)   -- generated `<rule>-a<i>`, its source rule, i
def elaborateMap (D : ActsDoc) : Except String (VE.NormDefaults.UDoc × SplitMap)
theorem elaborateMap_fst (D : ActsDoc) : (elaborateMap D).map (·.1) = elaborate D
theorem splitMap_exact  -- every generated predicate or rule of the result appears with its source and index,
                        -- and no other entry appears

theorem elaborate_identity (D : ActsDoc) (h : ∀ p A, (p, A) ∈ D.acts → ∃ a, A = .one a) :
    elaborate D = .ok D.U
theorem elaborate_wellFormed (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U')
    (hw : WellFormedActs D = true) (h0 : VE.NormDefaults.WellFormedU D.U = true) :
    VE.NormDefaults.WellFormedU U' = true
theorem elaborate_one_reading (D : ActsDoc) {U'} (h : elaborate D = .ok U') :
    ∀ p A, (p, A) ∈ D.acts → ∀ N ∈ VE.Norms.rulesOn D.U.D.T p, (table D.frames (opOfRule D p N) A).length = 1

/-- The source's meaning, per the table: every source rule on an act holds of each simple act of its one reading. -/
def IntendedActs (D : ActsDoc) (S : VE.Structure.{u}) : Prop
/-- Faithfulness: the elaborated document's intended reading is the table's reading of the source. -/
theorem elaborate_faithful (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U')
    (hw : WellFormedActs D = true) (S : VE.Structure.{u}) :
    VE.Norms.holdsCatala U'.D.T S ↔ IntendedActs D S
end VE.Acts

/-! lean/VE/Acts/Readings.lean and Sources.lean (AP-4) -/
namespace VE.Acts

/-- 2.4: every grammar rule that places a modifier attaches it to the first item, the last item or the whole join. -/
def modRule (R : VE.Grammar.Rule Term) : Bool
def attachesAtEdge (R : VE.Grammar.Rule Term) : Bool
theorem modifier_edges (fs : List Frame) : ∀ R ∈ (grammar fs).rules.toList, modRule R = true → attachesAtEdge R = true

/-- Every reading of a phrase under a modal: each derivation's act tree through the table, equal lists once; the
    limit outcome as in `readings`, and when more than 64 lists result. -/
def phraseReadings (fs : List Frame) (op : Op) (N b : Nat) (ts : Array Lexical.Tok) : Listing (List Atom)
/-- Characterised by the grammar's derivations, not by a possibly truncated intermediate list. -/
theorem phraseReadings_exact (fs) (h : framesOk fs = true) {op N b ts Rs}
    (hp : phraseReadings fs op N b ts = .ok Rs) (R : List Atom) :
    R ∈ Rs ↔ ∃ d A c, VE.Grammar.Derives (grammar fs) (.n (grammar fs).start) ts.toList d ∧
      meaning fs () d = .ok (A, c, ()) ∧ R ∈ table fs op A

/-- A source: an act phrase as the source words it, the source rule (or an explicit source template) whose modal,
    sign, guard, carve-outs, precedence and completion every reading keeps, and the reading sets (with their
    couplings) it is read into. -/
structure Source where
  phrase : String
  op : Op
  form : Option Lexical.Form
  rule : String
  sets : List String

/-- The choices of `D` restricted to the listed sets, one per combination their couplings allow
    (`VE.Readings.choices`, projected). -/
def choicesOn (D : VE.Readings.Doc) (sets : List String) : List (List (String × Nat))
def sourceCheck (D : VE.Readings.Doc) (fs : List Frame) (fx : List String) (N b : Nat) (s : Source) :
    Except String Unit
/-- Exactness: a bijection between the phrase's readings (complete against the grammar) and the listed choices; each
    choice's elaborated rules are exactly its reading's simple acts, each with the source rule's modal, sign, guard,
    carve-outs, precedence and completion. The specification writes the statement in full. -/
theorem sourceCheck_exact (D fs fx N b) (s : Source) (h : sourceCheck D fs fx N b s = .ok ()) : SourceExact D fs fx N b s

/-- A separating situation built from simple acts: the status of an act in one reading and not the other holds,
    every other generated status is false. It is checked by the existing `VE.Readings.separates`, whose
    `separates_separated` gives `Separated`; no new soundness theorem is needed. -/
def atomSituation (D : VE.Readings.Doc) (s : String) (i j : Nat) : VE.Readings.Situation Nat
end VE.Acts

/-! lean/VE/Acts/Specialise.lean (AP-5; used only after AP-5b) -/
namespace VE.Acts
/-- The `acts` block's restrictive declarations: the markers and modifiers that, added to an act, give a way of
    doing it. Only these count. -/
structure Restrictive where
  markers : List String
  mods : List (List Lexical.Tok)
def specialises (ρ : Restrictive) (a b : Atom) : Bool
theorem specialises_refl (ρ : Restrictive) (a : Atom) : specialises ρ a a = true
theorem specialises_trans {ρ : Restrictive} {a b c : Atom} :
    specialises ρ a b = true → specialises ρ b c = true → specialises ρ a c = true
/-- One premise `∀ x̄. p_a x̄ → p_b x̄` per pair of declared simple acts of one permission or obligation role, equal
    sorts, a ⊑ b, a ≠ b. -/
def specPremises (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)) : List VE.Formula
theorem specPremises_typed (E : VE.Norms.Doc) (ρ acts) (h : VE.Norms.WellFormed E = true) :
    ∀ φ ∈ specPremises E ρ acts, φ.check E.E [] = true
theorem specPremises_plain (E ρ acts) (p : String) (r : VE.Norms.Regulated) (hr : r ∈ E.T.regulated)
    (hp : r.role = .plain) : ∀ φ ∈ specPremises E ρ acts, p ∉ VE.Norms.preds φ ∨ r.name ≠ p
end VE.Acts
```

AP-6 compares two routes and builds neither on `main` before D6. Their statements are part of the experiment:

```lean
-- route (a), reification: an act with k ≥ 2 bound non-subject slots becomes an event sort of `events@0`; its
-- participant roles are added to that sort as role predicates (events' rule: other topics add roles to the same sorts
-- and define no reification scheme of their own); faithful when one event exists per argument tuple.
theorem VE.Acts.Nary.reify_faithful (D : ActsDoc) (S : VE.Structure.{u}) (hc : OneEventPerTuple D S) :
    VE.Norms.holdsCatala (reify D).T S ↔ VE.Core.NaryIntended D S   -- over events@0's event sorts and roles
-- route (b), lifting: `VE.Norms.Arity` becomes `1 ≤ n ∧ n ≤ 6` over `VE.Core.Formula`; every existing theorem of
-- VE.Norms re-proved over the embedding `VE.Core.embedClosure` (`VE.Core.conservativity`).
```

## 4. Batches

Each batch lists:

- its goal and its new files;
- the shared files it must touch, with the in-flight branch that touches the same file;
- the generated files it regenerates (never by hand: `uv run python tools/regen_generated.py --write`);
- its Lean statements (section 3), its fixtures (section 5) and tests;
- seeded bugs, what is deleted, and the pilot number it moves.

The CLAUDE.md rules hold throughout:

- run the selected tests while iterating, and the full gate once on the final commit;
- plant a bug in each claimed behaviour, in each changed language;
- no literal sleeps;
- hermetic tests;
- regenerate `tools/gate-collection.json` after adding tests.

**Build order** (design debate; cross-plan review). Act-phrases lands first among the seven research-wave plans
(AP → AT → SC-1/SC-2 → QT → WG → ET → SC-3…SC-7 → ME), subject to explicit dependencies: AR-10's table before AP-1's
row, and AP-5b before any integration of AP-5.

1. AP-0 runs now. It also measures N.
2. `LexicalBase`, then AP-1. AP-1's new files and AP-2 are Lean-core work in parallel with the other plans' cores;
   AP-1's row waits for AR-10's table, and its decoder hunk for `lean-first/b14b`.
3. AP-2, merged: it changes no route.
4. AP-3 (with the relay and the reference table) and an AP-4 prototype, each on its own branch.
5. AP-7, run on `phraseReadings`. The table equations and the edge rule stay provisional until it passes.
6. Merge AP-3, then AP-4. AP-3 changes `_lean_route`, so merging it is already a release.
7. AP-5, once the restrictive declarations are specified; AP-5b before any integration of it.
8. AP-6 and AP-8, as experiments.

### AP-0. Baseline (pilot job, no product code; 2 h)

- **Goal:** know which bytes truly need the language before any batch claims them (research 2.1, caveat).
- **Work** (in the UDHR and constitution pilot directories, by the orchestrator's pilot job):
  1. Re-try the 11 UDHR units of M1 as plain entitlements under today's language (`ve-green-ts-B1` or later),
     recording per unit `expressible_today: yes/no` and the reason.
  2. Count M3 in the four UDHR parts and the constitution's main document.
  3. Add `act_workaround ∈ {pointer, folded, shortened, none}` to the constitution's 18 norm units.
  4. Measure the raw derivation budget N (D2): the largest raw derivation count over the pilots' act phrases, read
     with the specification's rule table, and fix N above it.
- **Pre-registered:** the "before" values are the research note's (M1 1,860 B, M2 5 units, M4 18 units). A unit made
  expressible by AP-0 is credited to AP-0, not to a later batch.
- **Moves:** possibly M1 (pilot repair). M3 gets measured.

### AP-1. Long single acts, fixed phrases, entitlement wordings (6 h)

- **Goal:** acts up to 400 bytes, holding declared fixed phrases, on every role. A plain predicate may carry an act
  and a form, and gets the wording "{0} has the right …" or "{0} is entitled …". No join word or comma outside a
  fixed phrase. Meaning unchanged: an act is still a canonical string with slots.
- **New files:**
  - `lean/VE/Acts/LexicalBase.lean` (below `Norms.Wire`: `actReserved`, `words` and their helpers, moved);
  - `lean/VE/Acts/Lexical.lean` and `lean/VE/Acts/LexicalExamples.lean` (`#guard` fixtures A1 to A6, A13, A15 to
    A19, and the specification's A21 to A30, A32 and A33);
  - `lean/VE/Acts/Compat.lean` (above both `Norms.Wire` and `Acts.Lexical`: `check_extends`);
  - `docs/spec/act-phrases.md` (the specification, written before the batch);
  - `ve/wire_contract/acts@0.json` (contract source);
  - `tests/test_acts_lexical.py`.
- **Shared files** (one hunk each):

  | File | Change | Overlapping branch |
  |---|---|---|
  | `lean/VE/Norms/Wire.lean` | `decodeRegulatedIn` plus `decodeRegulated_without_acts`; `canonicalEnvironmentJson` applies the same check; `actReserved` and `words` move to `LexicalBase` | `lean-first/b14b` edits this file: build after it merges. AP-1's and AP-3's hunks come first on this file; attitudes' AT-3a then adds its guard-node hook to the chain's norm decoder, if AT-0 places it here |
  | `lean/VE/Norms/Tree.lean` | `check` admits an act on a plain predicate (the refusal at :314) | — |
  | `lean/VE/NormDefaults/Check.lean` | `regBody` (:73) and `fieldsOK` (:158) drop the same refusal, so `check_eq := rfl` (:151) still holds; `regBody_ok` and the proofs over `RegOK` re-proved (statement review, spec 4.1) | — |
  | `lean/VE/NormDefaults/FillCheck.lean` | `fill_regOK` (:318) re-proved over the new `fieldsOK` | — |
  | `lean/VE/Norms/Plain.lean`, `lean/VE/EnglishGrammar/Encode.lean`, `lean/VE/Service/Standalone.lean` | the profile-aware decoders where `decodeRegulated` is called (spec finding F1, 4.1) | `Encode.lean` joins the `EnglishGrammar` queue with `Policy.lean` |
  | `lean/VE/Compose/Dispatch.lean` | one row of AR-10's profile-gate table: `acts@0`, `requires := ["norms@0"]`, with its composition proof | after AR-10's table lands (rows in landing order) |
  | `lean/VE/EnglishGrammar/Policy.lean` | the selected wording of a plain predicate with an act is `Lexical.wording`, beside the modal-form case at :504-507 | `question-answering/q2` does not touch it (measured). This hunk is the first edit in the serialised `lean/VE/EnglishGrammar/*` queue, before `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7` |
  | `ve/environment.py` | load the `acts` block and the plain `act` / `form` fields as data, no check | — |
  | `ve/printer.py` (the natural renderer) | for a plain predicate with an act under `acts@0`, render with the wording Lean selected; Python's own lint makes no decision for it | — |
  | `rust/ve-kernel/src/environment.rs` | refuse every environment whose profiles contain `acts@0` with `UnsupportedProfile`, as for an `unspecified` completion (:405–408); then `python3 tools/rust_build.py` | — |
  | `tools/layer_policy.py` | assign the new modules | — |
- **Order:** AP-1 builds its new files first, then adds the `Norms/Wire.lean` hunk after `lean-first/b14b` and the
  profile row after AR-10's table.
- **Generated:** wire-contract tables, `lean/VE.lean` (roots), `lean/VE/Audit.lean`, frozen inventory if touched,
  `lean/axioms.txt`, `lean/statements.txt` / `predicates.txt` / `declarations.txt`, trust tables (D8),
  `lean/checkers.lock`, `ve/assurance-manifest.json` (decoder pins reviewed by hand, as its note says), AR-10's
  generated profile data, `tools/gate-collection.json`.
- **Statements:** all of `VE.Acts.Lexical` (with `check_extends` in `Compat`), `decodeRegulated_without_acts`, and the
  `acts@0` row's composition theorem.
- **Tests:**
  - Python reads Lean's verdicts only: a document with `acts@0` and fixtures A1 to A3 checks; A5 and A6 are refused
    with Lean's diagnostic text, relayed.
  - Without `acts@0`, byte-identical decodes over the existing norms corpus (`tests/data/route-cases.jsonl` norms
    rows).
  - A plain predicate with an act renders its Lean wording, never "classified as".
- **Seeded bugs:**
  - Lean: let a comma pass outside a fixed phrase; fixture A33 (u092's phrase, refused for its first comma) must fail.
    Draft 2 seeded it on A5, which has no comma, so it could not fail.
  - Python: drop the `form` field when loading; the wording test must fail.
  - Rust: drop the `acts@0` refusal; the test that Rust answers `UnsupportedProfile` for an `acts@0` environment must
    fail.
- **Deleted for `acts@0` documents:** the display fallback for plain predicates with an act; Rust's decoding of them
  (it refuses). No check is copied into Python, and no `ve/profiles.py` row is written by hand: Python reads AR-10's
  generated data.
- **Moves** (*estimates*, after AP-0):
  - M1: u039, u085 and u106 (457 B), and possibly u091 (201 B).
  - M2: u020 and u059 (364 B). "Country or territory" and "the free and full consent of the intending spouses" are
    kept as fixed phrases or guards instead of a shorter wording.
  - M3: entitlements with an act render in English.
  - M4: the 7 Group C units' wordings are restored (the curly apostrophe, and *or* inside a fixed phrase).

### AP-2. The act grammar (Lean only; 5 h)

- **Goal:** `VE.Acts.grammar fs`, `meaning`, `read` and `readings` on the generic engine, with the two limits of D2
  and the explicit limit outcome; `analyse`; frames in the `acts` block; the render round trip. The grammar is a Lean
  value, not a JSON table: Lean is its only reader, so it needs no `english_grammar_gen.py` entry and no
  `--actions-version`.
- **New files:**
  - `lean/VE/Acts/{Syntax,Grammar,Meaning,Read,Linearize}.lean`;
  - `lean/VE/Acts/GrammarExamples.lean`, with every fixture of section 5 as a `#guard` on its derivation count and
    act tree.
- **Shared files:** none. Frames are parsed by AP-1's decoder hook only once AP-3 uses them, so AP-2 changes no
  route, and it merges on its own.
- **Generated:** roots, `Audit.lean`, axioms, statements, pins, gate collection.
- **Statements:** `grammar_wf`, `read_unique`, `readings_exact`, `readings_nodup`, `read_normal`.
- **Tests** (the specification writes the fixtures): both boundaries of each limit, that is N−1 and N raw
  derivations, and 63, 64 and 65 readings; duplicate derivations that would hide another meaning; raw-cap saturation
  and an exhausted step budget, each a limit outcome; the statement review's counterexamples to `framesOk` and
  `normalOk` (spec FR1 to FR7: a marker of spaces, two spellings of one marker, the subject slot as a filler, a
  repeated marker) and the round trips of the forms a modal uses (N1 to N5).
- **Seeded bug (Lean):** add a rule attaching a premodifier to a middle item; the u105 fixture (A8) must report 3
  readings and fail.
- **Moves:** nothing (enabler). The constitution's hidden demand becomes measurable: AP-7 parses its 669 "norms"
  sentences' act parts with this grammar.

### AP-3. Joined acts (5 h)

- **Goal:** the table (2.3) and `elaborate`. Under `acts@0`, a declared act that AP-1 refuses for its join words or
  commas is read with `VE.Acts.read`: one meaning required, from a complete enumeration (D2). A rule on it must have
  exactly one reading by the table. That reading's simple acts become predicates and rules. A rule with two or more
  readings is refused, with every reading as a plain paraphrase ("this rule has two readings: …"). In authoring the
  writer picks one; in translation the reading set arrives with AP-4's sources. A predicate whose rules, or whose
  dual's rules, give different lists of simple acts is refused ("write the parts as separate predicates").
- **New files:**
  - `lean/VE/Acts/{Table,Elaborate,Faithful,Decode}.lean` and `lean/VE/Acts/ElaborateExamples.lean` (`Decode.lean`:
    `ElaboratedU` and `decodeElaboratedU`, spec 6.4);
  - the `acts-elaborate` relay (below);
  - `tests/test_acts_elaborate.py`.
- **Shared files** (statement review: elaboration runs after `decodeSourceU`, not inside `Norms/Wire.lean`; spec 6.4):
  - `lean/VE/Norms/Wire.lean`: the act check calls `VE.Acts.Wire.checkAct` and the `acts` block's frames are decoded
    (after `lean-first/b14b`; AP-1's and AP-3's hunks come first on this file). It elaborates nothing: draft 2's "after
    decoding, `VE.Acts.elaborate`" broke `Source.env` and lost the parts' `unspecified` completions.
  - `lean/VE/NormDefaults/Wire.lean`: `checkAuthorN` factored through `authorLimits`, which `elaborateMap` re-runs on
    the elaborated document (`checkAuthorN_split`).
  - Every entry point an `acts@0` norms document reaches calls `decodeElaboratedU` and runs on the elaborated
    document; each reached soundness theorem gains a twin over it. The callers of `decodeSource` and `decodeSourceU`
    measured on `49de179e` are listed in the specification (6.4); AP-3 classifies their reach at build time.
  - `lean/VE/Readings/Wire.lean`: the frame decoder refuses joined acts under `acts@0` (D-33,
    `readings_lexical_only`), until a readings elaboration is specified and reviewed.
  - `ve/norms.py`: `_lean_route` is true for `acts@0` documents, and the retained Python path refuses them.
- **The `acts-elaborate` relay (mandatory).** It goes through the full CLAUDE.md recipe for a relayed Lean route:
  - a shape, an encoder theorem and a generated schema;
  - binding: each generated `p__i` and `<rule>-a<i>` names its source predicate or rule in the request, plus an index,
    as `SplitMap` exports them (section 3); the row's `split` member carries, per split source, its parts and the
    "name one of its parts" text Lean writes, which Python relays verbatim (spec 6.7, D-28);
  - fuzz tests.

  Python's conflict-witness search and its prover then run on the relayed document, so their witnesses and
  certificates name the targets Lean has. The source predicate is removed. Any reference to it, in a formula, a model,
  data or a question, is refused with "name one of its parts". The specification's reference table covers every place
  a predicate can be named in `Norms.Tree` and in the Python inputs, and a test enumerates the fields of `Node`,
  `Regulated`, `Definition` and `Doc` and fails on any field the table leaves out. Scope uses the map for the
  provenance of governed rules that the chain's decoder splits, and weighing uses it for decision targets that name
  split rules or acts; neither re-derives a split.
- **Generated:** as AP-2, plus the relay's response schema and its route cases.
- **Statements:** `table_*`, `elaborate_identity`, `elaborate_wellFormed`, `elaborate_one_reading`,
  `elaborate_faithful`, `elaborateMap_fst`, `splitMap_exact`, `elaborate_parts`, `distinctTexts_ok`,
  `paraphrases_nodup`, `checkAuthorN_split`, `decodeElaboratedU_source`, `decodeElaboratedU_wellFormed`,
  `decodeElaboratedU_lexical`, `readings_lexical_only`, and the twins of the reached soundness theorems.
- **Tests:**
  - A6 (u027) gives two prohibitions; A7 (u079b) gives one obligation on "held by secret vote or by equivalent free
    voting procedures"; A14 (u0123.s03) gives five prohibitions (the specification's G14v and E3) and leaves "provide
    false information that could deceive the user" as an explicit residual: *false* is a clause word, and the
    statement review kept the rule (spec F10).
  - Precedence splits pairwise. A predicate whose rules or dual rules give different lists of simple acts is refused.
  - Documents whose acts are all simple are byte-identical to AP-1's (`decodeElaboratedU_lexical`).
  - An unspecified predicate decoded from JSON splits into unspecified parts (spec E5j).
  - The route limits hold after a split, each at its boundary (spec E12 to E15); two equal parts of a plain
    entitlement are refused (E16).
  - A rule with two readings is refused with Lean's numbered paraphrases (E9); the paraphrases of one listing are
    pairwise distinct (G12 under *must not*: four, spec P12n).
  - Every reference to a split predicate is refused (the reference table's test).
- **Seeded bugs:**
  - Lean: let `must` distribute over *or*; the table fixture T8 (G6 under *must*: no reading) must fail. Draft 2
    seeded it on A7, a single act the table never splits, so it could not fail.
  - Python: display one row per source rule instead of Lean's per-simple-act wordings; the display test must fail.
- **Deleted:** nothing new; Python computes no split.
- **Order:** stays on its branch until AP-7 has run; then merges before AP-4.
- **Moves:**
  - M1: u079b, 76 B (*estimate*: needs its subject carried from u079a, as u045b's is from u045a).
  - M2: u027 and u045a (197 B) lose their approximations: the lists become separate prohibitions instead of
    "ill-treatment" and "private life".
  - M4: the 4 Group B units and the 7 Group A units are on real acts. Group A's faithfulness needs `attitudes` **and**
    the reviewed act-performance bridge (events-time-causation, ET-D2); act-phrases' acts alone do not supply
    "knowingly/intentionally does A".

### AP-4. Readings from derivations; exact reading sets (6 h)

- **Goal:**
  - the edge rule (2.4) in the grammar, with `modifier_edges`;
  - `Source` and `sourceCheck`: a `readings@1` set that names its source phrase and source rule must hold exactly the
    phrase's readings (`sourceCheck_exact`): a bijection between readings and choices, complete against the grammar,
    each choice's rules keeping the source rule's modal, sign, guard, carve-outs, precedence and completion. The
    completion is three-valued (`deny`, `allow`, `unspecified`), read from the original metadata, not from the frame's
    placeholder; a choice's rules are compared with its reading's simple acts up to order (statement review, spec 7);
  - `atomSituation`, built by Lean and checked by `separates`;
  - a proposal mode that lists the readings (and their paraphrases) of an act phrase, so the translator's tool writes
    the set Lean then checks. Lean lexes the phrase and returns each act's token indices; Python binds them (in range,
    none repeated in an act, readings distinct) and lexes nothing.
  - Binding cannot detect a reading dropped with its row: that is a fault in Lean's content, covered by
    `phraseReadings_exact`; in translation `sourceCheck` refuses a set that lacks a reading. No test claims more.
  - On the readings route only AP-1's single acts may be declared (AP-3's D-33). A reading whose simple act is a whole
    join, or an atom with a joined filler, therefore has no candidate, and its source cannot pass until a readings
    elaboration is specified and reviewed (spec F11). Of the pilot sets this affects u076 only.
- **New files:**
  - `lean/VE/Acts/{Readings,Sources,Situation,Run}.lean` and `ReadingsExamples.lean`;
  - `lean/ResponseShape/Schemas/ActReadings.lean` and `lean/ResponseShape/Encoders/ActReadings.lean` (with
    `runActReadings_fits`);
  - `ve/acts.py` (relay: schema and binding only, R8);
  - `tests/test_acts_readings_lean.py` and `tests/test_acts_readings_answer.py` (fuzz: each member dropped, emptied,
    retyped, duplicated, reordered, an index pushed out of range, a token span pushed past the phrase, two readings
    made equal; spec AR1 to AR5).
- **Shared files:**

  | File | Change | Overlapping branches |
  |---|---|---|
  | `lean/VE/Service/Protocol.lean` | the `act-readings` mode, registered through AR-10's mode registry | joins the protocol queue after `lean-first/b14d` and `question-answering/q2` (both edit it, measured), then after AR-10's registry, ME-2, QT-A3 and SC-1c, in landing order |
  | `ve/backends/service_schema.py` | `MODES` | the same queue |
  | `ve/__main__.py` | `ve acts readings` | — |
  | `lean/VE/Readings/Run.lean` (admission, :222-243) | one call to `sourceCheck` per source when `acts@0` is present | `lean-first/b14d` does not touch it (measured); re-check at build time |
- **Generated:** response schemas, route cases (`tests/data/route-cases.jsonl` via `tests/route_case_recorder.py`),
  roots, `VE/Audit.lean`, `ResponseShape/Audit.lean`, axioms, statements, pins, assurance manifest, gate collection.
- **Statements:** `modifier_edges`, `phraseReadings_exact`, `sourceCheck_exact`.
- **Tests:**
  - A5 (u051), A8 (u105), A9 (u055), A10 (u092) and A11 (u076) give exactly 2 readings each.
  - A12 (u087) gives 2.
  - The pilot's rs_u055 and rs_u105b/rs_u105c with their coupling pass `sourceCheck`.
  - A set with a skipped-middle candidate is refused. A set missing a reading is refused. A set whose choice turns a
    permission into a prohibition is refused. A set whose choice changes only `unspecified` to `deny` is refused (spec
    S7); one whose rules come in another order passes (S8).
  - The boundaries of `phraseReadings`: 64 readings listed, 65 refused; raw-cap saturation refused.
- **Seeded bugs:**
  - Lean: drop the "all" reading of a pre-modifier; rs_u105b/c must be refused.
  - Python: drop the token-index range check from the binding; the fuzz mutant with an index pushed out of range (spec
    AR2) is then accepted, so its test fails. (Draft 2's "relay a reading list with one reading removed" was a claim
    binding cannot meet: spec AR5.)
- **Deleted:** the pilot's hand-built separating situations for these sets. Lean's `atomSituation` builds them, the
  proposal tool writes them into the document, and admission checks them with `separates`, as for any set.
- **Order:** a prototype on its own branch until AP-7 has run; merges after AP-3.
- **Moves:**
  - M1: u092, 163 B (*estimate*). u076 (125 B) waits for the readings elaboration: its one-act reading is a joined
    act, which the readings route refuses until then (spec F11).
  - M2: u055 checked exact.
  - M5: 3 sets checked against the English.

### AP-5. Specialisation: definitions and generator only (4 h)

- **Goal:** `specialises` over the declared restrictive markers and modifiers, and `specPremises`, as Lean
  definitions with proved properties. AP-5 has no Background hook and is not a premise pack (2.6).
- **New files:** `lean/VE/Acts/Specialise.lean` (`specialises`, `specialises_refl`, `specialises_trans`,
  `specPremises`, `specPremises_typed`, `specPremises_plain`) and `SpecialiseExamples.lean`, with `#guard`s on the
  generator.
- **Shared files:** none.
- **Statements:** `specialises_refl`, `specialises_trans`, `specPremises_typed`, `specPremises_plain`.
- **Moves:** nothing until AP-5b.

### AP-5b. The base-level bridge for `act-specialise@0` (design and review; act-phrases)

- **Goal:** a separately reviewed bridge that:
  - (a) states the opt-in `act-specialise@0` meaning over base predicates;
  - (b) justifies any substitution of outcome formulas for regulated predicates;
  - (c) proves that conflict-freedom with the specialisation premises is not vacuous.
- **Then:** only after AP-5b passes may specialisation become PK-1's last pack.
- **Tests** (moved from AP-5):
  - "may seek asylum from persecution in other countries" and "must not seek asylum from persecution" report a
    conflict.
  - "may a person seek asylum?" answers yes from the specific permission.
  - A plain entitlement gets no premise.
- **Seeded bug (Lean)** (moved from AP-5): reverse the premise direction; the conflict fixture must fail.

### AP-6. Experiment: more than two bound slots (4 h; decision D6)

- **Question:** for u019 ("no distinction by a bearer between persons on a ground"), u057 and rights.md's
  `publish_about(person, item, person)`, which route gives faithful three-place rules at the lower cost?
  - Route (a): reify an act with two or more bound non-subject slots as an event sort of `events@0`, with its
    participant roles added to that sort as role predicates, inside binary norms. Events' rule is that other topics
    add roles to the same sorts and define no reification scheme of their own; `reify_faithful` is stated over those
    event sorts and roles.
  - Route (b): lift regulated arity to 6 over `VE.Core`.
- **Work:** build both on a scratch branch (not merged), after `lean-first/b14c` (n-ary core definitions) merges;
  route (a) also needs events' ET-3 (`lean/VE/Events/Decl.lean`).
- **Pre-registered bar:** a route wins if it:
  - proves its faithfulness statement (section 3) with no new axiom;
  - checks the three fixtures within 1.25× the binary route's time on the same machine (measured by
    `tools/bench/test_perf.py`, never in the suite);
  - changes no existing theorem statement (route a) or re-proves all of `VE.Norms` over the embedding within
    4,000 lines (route b).

  If neither meets the bar, D6 is "not yet", and u019 and u057 stay co-blocked.

### AP-7. Experiment: do derivations find the auditors' readings? (3 h, before AP-3 or AP-4 merges)

- **Sample** (fixed now): every UDHR unit with a coordinated act or an edge modifier (u020, u027, u045a, u051, u055,
  u059, u076, u079b, u087, u092, u105a–c, u106) and 30 constitution norm sentences drawn with
  `random.Random("act-phrases-AP7")` from the units whose excerpt contains *and* or *or* inside the verb phrase.
- **Method:**
  - Two blind auditors (the pilot audit protocol; a Sonnet proxy only under the lead's rules for proxies) list each
    sentence's readings in plain English before seeing Lean's.
  - Lean's `phraseReadings` lists its own, the modal included, so the two-reading cells of the table (*may* with
    *or*, *may* with a shared *and*, *must not* with *and*) are tested.
  - Matching is by paraphrase, done by a third auditor.
- **Pre-registered bar:**
  - recall ≥ 90% of the readings both auditors list;
  - ≤ 10% of Lean's readings judged "not a reading of this English" by both;
  - no skipped-middle reading.

  It runs on the AP-3 and AP-4 branches, before either merges. Below the bar, D3 or D4 is revised before AP-3 or AP-4
  merges. Its percentages are evidence about the declared vocabulary, not a one-reading guarantee.

### AP-8. Experiment: frames without declaration (3 h, after senses B6)

- **Question:** can the IDE propose a document's frames from a sense pack (verb and markers) well enough that writers
  never declare one?
- **Sample:** the UDHR's 46 unformalised units and the agent-policy use case's 26 rules.
- **Pre-registered bar:**
  - ≥ 90% of the frames the AP-1 to AP-4 fixtures need come from the pack unchanged;
  - no proposed frame removes an attachment reading that the AP-7 auditors listed.

  Below the bar, frames stay declared vocabulary and the IDE asks for them.

## 5. Fixtures (from the pilot sentences)

Source text is from the pinned UDHR and constitution ledgers. In the act-phrase column, `[...]` marks a declared fixed
phrase. Expected results are what the batch must show. The specification writes each fixture in full, with its
declarations, its derivation and reading counts and its diagnostics, and adds the boundary fixtures of D2.

| # | Unit | Act phrase under `acts@0` | Batch | Expected |
|---|---|---|---|---|
| A1 | u039 | `{0} in full equality to [a fair and public hearing by an independent and impartial tribunal] in {1}`, form "is entitled"; guard: the determination is of the person's rights and obligations or of a criminal charge against the person | AP-1 | accepted (97 bytes, over today's 80); wording "… is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in …" |
| A2 | u085 | `{0} to [equal pay for equal work] without any discrimination`, form "has the right"; open terms `discrimination`, `equal_pay_for_equal_work` | AP-1 | accepted |
| A3 | u106 | `{0} to the protection of [the moral and material interests] resulting from {1}`, sorts person and production; guard: the person is the author of the production, and the production is scientific, literary or artistic | AP-1 | accepted |
| A4 | u051 (today's wording) | `{0} to seek as well as enjoy in other countries asylum from persecution` | AP-1 | accepted; it never enters the grammar: its identity and meaning are its canonical string (2.5) |
| A5 | u051 (source) | `{0} to seek and to enjoy in other countries asylum from persecution` | AP-1; AP-4 | AP-1: refused, *and* outside a fixed phrase. AP-4: 2 readings ("in other countries" on *enjoy* or on both) |
| A6 | u027 | `{0} be subjected to torture or to [cruel, inhuman or degrading treatment or punishment]`, permission, sign false; frame `be subjected` with `split: ["to"]` | AP-1; AP-3 | AP-1: refused. AP-3: two prohibitions |
| A7 | u079b | `{0} be held by secret vote or by [equivalent free voting procedures]`, obligation | AP-1; AP-3 | AP-1: refused (or accepted with the two ways as one fixed phrase). AP-3: one obligation on the whole act; "by" is not a split marker |
| A8 | u105a–c | `{0} freely to participate in [the cultural life of the community], to enjoy the arts and to share in [scientific advancement and its benefits]`, form "has the right" | AP-4 | exactly 2 readings (*freely* on the first act, or on all); the pilot's coupled rs_u105b/rs_u105c pass `sourceCheck` |
| A9 | u055 | `{0} be arbitrarily deprived of their nationality nor denied [the right to change their nationality]`, permission, sign false | AP-4 | exactly 2 readings = rs_u055's `deprivation_only` and `both_acts` |
| A10 | u092 | `{0} to security in the event of unemployment, sickness, disability, widowhood, old age or [other lack of livelihood] in circumstances beyond their control`, frame *security* with `split: ["in the event of"]` | AP-4 | 2 readings ("in circumstances beyond their control" on the last cause, or on all) |
| A11 | u076 | `{0} to take part in {1} directly or through [freely chosen representatives]`, form "has the right"; the country slot as u077 | AP-4 | 2 act readings (each way, or one of the ways) × u077's 2 country readings; its reading set passes `sourceCheck` only after the readings elaboration (spec F11) |
| A12 | u087 | `{0} to form and to join trade unions for the protection of their interests` | AP-4 | 2 readings ("for the protection …" on *join* or on both); the split itself (*to … and to …*) is AP-3's |
| A13 | u0156.s03 | `{0} actively deceive {1} about [the existence of a system prompt or its content]` | AP-1 | accepted; replaces "existence-or-content" |
| A14 | u0123.s03 | the six acts after "cannot instruct Claude to", joined by *or*, permission, sign false; *while* and *when* clauses move to guards | AP-3 | five prohibitions plus one explicit residual: "provide false information that could deceive the user" holds the clause word *false*, refused even in a fixed phrase, and the statement review kept that rule (spec F10, G14v); "instruct" stays `speech-acts@0`'s |
| A15 | u024, u037 | two **permission** predicates with act `{0} take place` and different sorts | AP-1 | accepted (act identity includes sorts, and `actChecks` checks permissions); the specification decides whether wording distinctness may also use sorts (open question 8.3). Draft 2 left the role open; as plain predicates `actChecks` would skip them and the wording would read "has the right take place" |
| A16 | u041 | `{0} to be presumed innocent until proved guilty according to law in [a public trial at which they have had all the guarantees necessary for their defence]` | AP-1 | accepted as words; not counted in M1 (time is events-time-causation's) |
| A17 | — | `{0} take part if {1} is open` | AP-1 | refused: clause word (*if*, *is*); "write the condition in the guard" |
| A18 | — | fixed phrase "the court that is competent" | AP-1 | refused: clause word in a fixed phrase |
| A19 | u0263.s04.p2 | `{0} comply with [the operator’s instructions] in {1}` | AP-1 | accepted; `’` read as `'` |
| A20 | — | `{0} must seek asylum` | AP-1 | refused: clause word *must* |

A1's byte count was counted by hand on the act string above; the `#guard`s pin every count.

Boundary fixtures (AP-2 and AP-4; the specification writes them): N−1 and N raw derivations; 63, 64 and 65 readings;
duplicate derivations that would hide another meaning; an exhausted step budget.

## 6. Dependencies on other work

| Needs | From | Used by | If it is late |
|---|---|---|---|
| `lean-first/b14b` merged (edits `Norms/Wire.lean`) | lean-first | AP-1, AP-3 | AP-1 builds its new files first and adds the decoder hunk last |
| AR-10's profile-gate table and mode registry | AR-10 | AP-1's row; AP-4's mode | AP-1 builds its new files first and adds the row after the table lands |
| `lean-first/b14d`, `question-answering/q2` merged (edit `Service/Protocol.lean`) | lean-first, QA | AP-4's proposal mode | AP-4 ships `sourceCheck` first; the mode follows |
| `lean-first/b14c` merged (n-ary core definitions) | lean-first | AP-6 | AP-6 waits |
| ET-3 (`lean/VE/Events/Decl.lean`) | events-time-causation | AP-6 route (a) | route (a) waits |
| PK-1 and AP-5b | RD-9 composition owner; act-phrases | AP-5's integration (as PK-1's last pack) | AP-5 stays definitions only |
| `rd-9/integrate` | readings-defaults | none directly; the constitution's soft rules get structured acts only once both exist | no effect on the UDHR batches |
| senses B6 (packs) | senses | AP-8 | frames stay declared |
| time ("until proved guilty", u041), modality ("can be fully realized", u108) | events-time-causation, attitudes | M1's remaining 345 B | those units stay counted under the siblings |
| typed attitudes and the reviewed act-performance bridge (ET-D2) (Group A) | attitudes, events-time-causation | constitution faithfulness | Group A stays on real acts but unfaithful |
| rights as objects and limitations (u082) | composition S2b, `right-clauses@0` | M1's remaining 277 B | stays residual |
| `right-clauses@0` | composition S3 | right lines with structured acts | independent: clauses keep finite clauses; acts keep verbs and fillers |

Every new Lean module is a new file under `lean/VE/Acts/`. The shared source files, in total:

- `lean/VE/Norms/Wire.lean` (AP-1, AP-3; first in its queue, after `lean-first/b14b`);
- `lean/VE/Norms/Tree.lean` (AP-1);
- `lean/VE/NormDefaults/Check.lean` and `FillCheck.lean` (AP-1: the plain-act refusal `check_eq := rfl` repeats);
- `lean/VE/Norms/Plain.lean`, `lean/VE/EnglishGrammar/Encode.lean`, `lean/VE/Service/Standalone.lean` (AP-1; spec F1);
- `lean/VE/NormDefaults/Wire.lean` (AP-3: `authorLimits`);
- `lean/VE/Readings/Wire.lean` (AP-3: joined acts refused on the readings route);
- the entry points that call `decodeSource` or `decodeSourceU` and that an `acts@0` document reaches (AP-3: they call
  `decodeElaboratedU`; the specification's 6.4 lists the callers measured on `49de179e`);
- `lean/VE/Compose/Dispatch.lean` (AP-1: one row of AR-10's table);
- `lean/VE/EnglishGrammar/Policy.lean` (AP-1; first in the `EnglishGrammar` queue);
- `lean/VE/Service/Protocol.lean` (AP-4, through AR-10's registry and the protocol queue);
- `lean/VE/Readings/Run.lean` (AP-4);
- `ve/environment.py`, `ve/printer.py` (AP-1);
- `ve/norms.py` (AP-3);
- `ve/backends/service_schema.py` and `ve/__main__.py` (AP-4);
- `rust/ve-kernel/src/environment.rs` (AP-1);
- `tools/layer_policy.py` (each batch with new modules).

Generated inventories are regenerated, never edited: `uv run python tools/regen_generated.py --write`, or
`--resolve` after a `git merge --no-commit`.

## 7. Estimated unlock per batch

All values are *estimates* on the pinned run `20261012T1800Z`. A pilot rerun and an audit decide each unit.

| Batch | UDHR units → status | UDHR bytes | UDHR claimed coverage | Constitution |
|---|---|---|---|---|
| now | — | — | 43.90% | 2,951 B claimed |
| AP-0 | measured | measured | measured | M4 tagged |
| AP-1 | u039, u085, u106 → OPEN; u091 → OPEN (high) | +457 to +658 | 48.1% to 49.9% | Group C wordings restored (742 B, faithfulness) |
| AP-3 | u079b → OPEN | +76 | 48.8% to 50.6% | Groups A and B on real acts (1,838 B, faithfulness; A still needs attitudes and the act-performance bridge) |
| AP-4 | u092 → READINGS | +163 | 50.3% to 52.1% | — |
| the readings elaboration (a later statement review; spec F11) | u076 → READINGS | +125 | 51.4% to 53.3% | — |
| AP-5 | — | 0 | — | nothing until AP-5b |
| beyond this plan | u041, u108 (siblings), u086 (research), u082 (rights as objects) | up to +838 | — | — |

The NORTH-STAR-style score (UDHR weight 4) is 0.25 to 0.33 after AP-4 (*estimate*), and 0.30 to 0.37 once u076
follows, against an upper bound of 0.68 for all 1,860 B.

## 8. Risks and open questions

1. **AP-0 may shrink the credit.** That is its purpose; the faithfulness gains (M2, M4, M5) do not depend on it.
2. **Fixed phrases and frames are declarations an audit must check.** A fixed phrase hides its own coordination by
   design, and a frame without a marker removes an attachment reading. AP-7 measures the second. The audit checklist
   gains "fixed phrases name one thing; frames list the source's prepositions". Exactness is stated relative to these
   declarations, which readers see; AP-7's numbers are evidence, not a guarantee.
3. **Wording distinctness across sorts** (u024 and u037 both "take place"). Lexicon V4 compares wordings without
   sorts. Allowing equal wordings with different subject sorts needs a typed reading, which is the specification's
   call. AP-1 does not depend on it.
4. **Shallow separations.** Readings that differ in which simple acts they regulate separate in a trivial situation
   until AP-5's premises relate the acts, which needs AP-5b. That is honest but weak, and the legend says so.
5. **Python's norm-sentence matcher** still matches long acts as exact terminals. That is safe for one reading (a
   terminal is literal), but it may be slow for very long acts (not measured). E3 moves it to Lean; if the gate shows
   a regression, AP-1 caps acts lower (D2).
6. **Freezing.** The table and the edge rule become part of `acts@0`'s meaning when AP-3 and AP-4 merge. AP-7 runs
   before either merges, on their branches; until it passes, the table equations and the edge rule are provisional.
7. **Lean audit words.** `lean/audit.py` refuses the words *sorry, axiom, unsafe, partial, opaque, extern* (with word
   boundaries) even in comments and strings. Fixture strings are checked for them. "Impartial" passes (no word
   boundary), but a fixture or comment saying "opaque" would not: the plan's Lean text avoids it.
8. **Joined acts on the readings route** (statement review). Nothing elaborates a reading set's candidates, so the
   readings route accepts only AP-1's single acts until a readings elaboration, with its own candidate elaboration and
   preservation theorems, passes a statement review of its own. Until then u076's reading set waits (spec F11), and
   any source with a whole-join reading cannot be checked exact.

## 9. Shared pieces

The research note (section 8) lists ten abstractions several of the seven research-wave designs could share. The
plan's position on each:

| Shared piece | This plan builds | Others would use |
|---|---|---|
| Structured simple acts, act identity | `VE.Acts.Atom`, canonical act as written (AP-1 to AP-3); exports `SplitMap` to scope and weighing | weighing (same act?), attitudes ("knowingly provide …"), events-time-causation, speech acts' content |
| Act-performance predicate ("x does A") | not built here. events-time-causation designs the bridge (ET-D2); attitudes keeps intentional action residual until it is reviewed. | attitudes, causation |
| Readings from derivations, exact sets, Lean-built separations | `readings`, `sourceCheck`, `atomSituation` (AP-2, AP-4) | scope, attitudes, quantities, events |
| Edge rule for modifiers over a list, couplings | `modifier_edges` (AP-4) | attitudes, quantities, scope |
| Frames as n-ary relation schemas with English | `VE.Acts.Frame` (AP-2); n-ary via AP-6 | math-evidence, events, quantities |
| Modal × connective table | `VE.Acts.table` (AP-3), deontic modals only | weighing (soft "should A or B") |
| Specialisation premises | `specPremises` (AP-5); used only after AP-5b, as PK-1's last pack | weighing, question answering |
| Fixed words as one thing; open terms for open words | fixed phrases (AP-1) | quantities, weighing |
| Finite clauses become guards | the clause-word rule (AP-1) | `right-clauses@0`, scope |
| Honest Lean wordings for every regulated predicate | `Lexical.wording` (AP-1) | every design adding predicates |

## 10. Edit map (drafts 2 and 3)

**Design debate** (`debates/design-act-phrases`, final joint position, round 3; Fable's and Astra's points as both
accepted them):

| # | Edit | Applied in |
|---|---|---|
| G1 | `read` means one meaning, not one derivation tree | 0 item 2; 2.2; 3 (`read`, `read_unique`); AP-2 |
| G2 | Two separate limits: a raw derivation budget N (AP-0 measures it) and the 64-reading listing limit; an explicit limit outcome when either is reached, or the step budget is exhausted; a refusal, never a choice; 64 readings accepted when the enumeration is complete | D2; 2.4; 3 (`Listing`, `readings`, `readings_exact` without a length hypothesis); AP-0 item 4 |
| G3 | `read_one` becomes `read_unique` | 3; AP-2 statements |
| G4 | `sourceCheck_exact`: completeness against `Derives`; a bijection between readings and choices; each choice keeps op, sign, guard, carve-outs, precedence and completion, bound to an identified source rule or an explicit source template | 0 item 4; 3 (`Source.rule`, `sourceCheck_exact`); AP-4 goal and tests |
| G5 | Tests at both boundaries (N−1 and N raw derivations; 63, 64 and 65 readings); duplicate derivations hiding another meaning; `phraseReadings_exact` characterises grammar-derived meanings | 3 (`phraseReadings_exact`); AP-2 tests; AP-4 tests; 5 (boundary fixtures) |
| G6 | No fallback rule: acts AP-1 accepts never enter the grammar; `analyse` gives structure only for AP-5; `reads_lexical` and `Atom.ofLexical` removed | 0 item 1; 2.2; 2.5; 3 (`analyse`); A4 |
| G7 | Duals: a predicate whose rules or dual rules give different lists of simple acts is refused; aggregate/component premises deferred | 2.3 (last paragraph); 3 (`elaborate`); AP-3 goal and tests |
| G8 | Inventory: `LexicalBase` below `Norms.Wire`; `check_extends` in a module above both; `canonicalEnvironmentJson`; the `.plain` admission in `Tree.check`; AP-1 lists all three hunks | 2.5; 2.8; 3 (`LexicalBase`, `Compat`, the `Norms/Wire.lean` block); AP-1 new and shared files; 6 |
| G9 | Specialisation counts only markers and modifiers the `acts` block declares restrictive (visible assumptions); every deletion used in narrowing covered; the premises only under the opt-in `act-specialise@0`; the IDE's question | 0 item 5; D5; 2.6; 2.8; 3 (`Restrictive`); AP-5 |
| G10 | Freezing: AP-7 runs before AP-3 or AP-4 merges; equations provisional until it passes; AP-2 merges on its own | D3; D4; 2.3; 2.4; 4 (build order); AP-2; AP-3; AP-4; AP-7; 8.6 |
| G11 | Mandatory `acts-elaborate` relay through the full recipe (shape, encoder theorem, schema; binding of each `p__i` and `<rule>-a<i>` to its source and index; fuzz); Python's searches on the relayed document; `_lean_route` true for `acts@0` and the retained path refuses; references to a split `p` refused; `p` removed | 0 item 3; D1; 2.3; 2.9; AP-3 (the relay, shared files, tests); 6 (`ve/norms.py`) |
| G12 | One reference table for every place a split predicate can be named; a test over the fields of `Node`, `Regulated`, `Definition` and `Doc` | 2.3; AP-3 (the relay, tests); the specification writes the table |
| G13 | `Act.any` and `Act.all` carry a split-marker flag, used in the table's conditions; *nor* refused under *may*, *must* and *has the right to* | 2.2; 2.3; 3 (`Act`, `table_*`) |
| G14 | AP-7 compares against `phraseReadings` | AP-7 method |
| G15 | Exactness relative to declared frames and phrases; AP-7's numbers are evidence; unsupported ambiguity refused or rephrased; recall does not establish completeness | 0; AP-7; 8.2 |
| G16 | The build estimate is redone after the contracts are written; 41 h withdrawn | 0 (hours table and note) |
| G17 | Build order: AP-0 (measures N); `LexicalBase`, AP-1; AP-2 merged; AP-3 (relay, reference table) and an AP-4 prototype on branches; AP-7 on `phraseReadings`; merge AP-3, then AP-4; AP-5 under `act-specialise@0`; AP-6 and AP-8 as experiments | 4 (build order); AP-3 and AP-4 "Order" |

**Cross-plan review** (`plan-synthesis/edits-act-phrases.md`):

| # | Edit | Applied in |
|---|---|---|
| S1 | `SplitMap`, `elaborateMap`, `elaborateMap_fst`, `splitMap_exact`; scope and weighing use the map; "name one of its parts"; §9 row 1 | 3 (Table/Elaborate block); AP-3 (the relay); 9 row 1 |
| S2 | AP-5 has no Background hook and is not a premise pack; it builds only `Specialise.lean` and `SpecialiseExamples.lean`; its behavioural tests and seeded bug move to AP-5b; AP-5b's goals (a) to (c); PK-1's last pack only after AP-5b; AP-5 moves nothing until AP-5b | 0 item 5 and table; D5; 2.6; 3 (Specialise header); AP-5; AP-5b; 6 (dependencies; shared files without the Background generator); 7 AP-5 row; 8.4; 9 row 7 |
| S3 | No performance predicate here; ET-D2; Group A needs attitudes and the reviewed bridge | 9 row 2; 6 (Group A row); AP-3 moves; 7 AP-3 row |
| S4 | The table is for deontic modals only; never reused for `intends` or `believes` | 2.3; 9 row 6 |
| S5 | AP-6 route (a) reuses events' reification (event sorts of `events@0`, role predicates); `reify_faithful` over them; needs ET-3 | D6; 3 (AP-6 block); AP-6; 6 |
| S6 | Registration through AR-10: `acts@0` is one row (`requires := ["norms@0"]`) with its composition proof; no re-proof of `todayGate_sound`/`todayGate_complete`, no hand-written `ve/profiles.py` row; AP-1 adds the row after AR-10's table lands; AP-4's mode registers through AR-10's registry and joins the protocol queue after `lean-first/b14d` and `question-answering/q2` | 3 (Dispatch block); AP-1 (shared files, order, statements, deleted); AP-4 (shared files); 6 |
| S7 | AP-1's `Policy.lean` hunk is the first edit in the `EnglishGrammar` queue; AP's refusals go into english-lean's catalogue as rows | 2.2 (clause words paragraph); AP-1 shared files; 6 |
| S8 | `Norms/Wire.lean` queue: AP-1's and AP-3's hunks first, after `lean-first/b14b`; then AT-3a's guard-node hook if AT-0 places it there | AP-1 and AP-3 shared files; 6 |
| S9 | Landing order: AP-0 now; AP-1's new files and AP-2 in parallel with the other cores; act-phrases lands first among the seven plans, subject to AR-10 before AP-1's row and AP-5b before AP-5's integration; the debate's order unchanged | 4 (build order) |

Three places where the edits do not say everything, recorded here and in the specification's section 14 for the
statement review and the DRI:

- **A14 as written.** *False* is a clause word, so u0123.s03's "provide false information that could deceive the
  user" is refused even inside a fixed phrase, and A14 gives five prohibitions, not six (the specification's finding
  F10, measured in its stub). *Decided by the statement review (draft 3, SR13): the rule stays; five prohibitions plus
  one explicit residual.*

- **The relay's place in the protocol queue.** The debate makes AP-3's `acts-elaborate` relay mandatory; the
  cross-plan queue for `Protocol.lean` and `service_schema.py` (SYNTHESIS 4.2) does not list it, because it predates
  the debate's last round. The specification places it as a case kind of the existing norms modes, which touches
  those modes' response shapes and not `Protocol.lean`; if the review prefers a mode of its own, it joins the protocol
  queue in landing order, before AP-4. *The statement review raised no objection; the case kind stands.*
- **AP-1's decoder reach.** `decodeRegulated` has callers beyond `Norms/Wire.lean` (`Norms/Plain.lean`,
  `EnglishGrammar/Encode.lean`, `Service/Standalone.lean`, `Service/Family.lean`). The specification (its section 4.1)
  lists them and which ones `acts@0` documents reach. *Draft 3 adds them to AP-1's shared files, with
  `NormDefaults/Check.lean` and `FillCheck.lean`, which the statement review found (SR4).*

**Statement review of the specification** (`debates/act-phrases-spec/{astra,fable}.md`, CONVERGED after round 2 on
**FIX**; the specification's 14.3 maps each edit there, this table maps where it touches the plan). Draft 3 applies
them and makes no other change. Build stays blocked, except AP-0, until a bounded re-check of the specification's
draft 2 against a fresh run of its stub passes and the DRI signs (SR16).

| # | Edit | Applied in the plan |
|---|---|---|
| SR1 | `framesOk` requires canonical markers; `normalOk` excludes the subject slot and repeated markers; the counterexamples as fixtures | AP-2 tests |
| SR2 | Modal rendering without infinitive *to*; whole readings rendered from their trees; paraphrases of a listing pairwise distinct (`paraphrases_nodup`) | 3 (preamble); AP-2 tests; AP-3 statements and tests |
| SR3 | Three-valued completion in `Source` and its comparison, from the original metadata; the `unspecified → deny` mutation | 3 (preamble); AP-4 goal and tests |
| SR4 | AP-1 inventory: `NormDefaults/Check.lean` and `FillCheck.lean`; an explicit check of duplicate parts for every role | 2.3; AP-1 shared files; AP-3 tests; 6 (shared files); this section's third note |
| SR5 | The `act-readings` relay claims only what binding shows; a concrete Python seeded bug | AP-4 goal, new files, seeded bugs |
| SR6 | Elaboration after `decodeSourceU`, with an explicit `ElaboratedU` beside the decoded source; E5 from JSON | AP-3 new files, shared files, statements, tests; 6 (shared files) |
| SR7 | Route limits re-checked after a split, with their existing texts; boundary fixtures | 2.3; AP-3 shared files and tests |
| SR8 | Joined acts refused on the readings route until a readings elaboration is reviewed; u076's set waits | 0 (table, coverage); AP-3 shared files; AP-4 goal and moves; A11; 6; 7; 8.8 |
| SR9 | `elaborate_parts` | 3 (preamble); AP-3 statements |
| SR10 | Rust refuses `acts@0` with `UnsupportedProfile`; its seeded bug | 2.9; AP-1 shared files, seeded bugs, deleted |
| SR11 | Exact D-15, D-23 and D-31 texts with guards | AP-3 tests (E9) |
| SR12 | Lean lexes and writes the "name one of its parts" text; Python binds | 2.9; AP-3 relay; AP-4 goal |
| SR13 | F10 decided: the clause words stay refused | A14; AP-3 tests; this section's first note |
| SR14 | A15's predicates are permissions; rules compared up to order; the stub's run record | A15; AP-4 goal and tests |
| SR15 | Seeded bugs that can fail: the comma bug on A33, the *must*/*or* bug on T8 | AP-1 and AP-3 seeded bugs |
| SR16 | Bounded re-check, then the DRI | status; this section |
