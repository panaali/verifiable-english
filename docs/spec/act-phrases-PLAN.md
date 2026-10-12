# Action phrases inside rights and norms: plan

> Status: plan, draft 1 (2026-10-12), branch `design/act-phrases` from `main` at `49de179e`; DRI research wave of
> 2026-10-12. It builds design D2 of the research note [docs/research/act-phrases.md](../research/act-phrases.md)
> (sections 4 to 6), which holds the measurements, the prior art and the alternatives. Docs only. No batch starts
> before the cross-plan review of the seven research-wave plans, its own specification and statement review, and a
> DRI decision. Every number is measured (method in the research note, Appendix A) or labelled *estimate*.

## 0. Summary

A rule regulates an act: "Everyone has the right **to take part in the government of their country, directly or
through freely chosen representatives**." Today the act is a string of at most 80 characters with no *and*, *or*,
*for* or comma, and VE treats it as a name. This plan turns act phrases into parsed English, in five steps:

1. **AP-1, long single acts.** An act may be long and may hold declared **fixed phrases**: groups of words, possibly
   with *and*, *or* or *for*, that name one thing and are not analysed. Its slots bind the rule's arguments, at most
   two today. A plain entitlement gets an honest English wording ("has the right to …") instead of "classified as …".
   Lean decides acceptance; nothing an AP-1 document says changes meaning later.
2. **AP-2, the act grammar** (Lean only). It reads an act phrase against the document's declared **frames** (a verb
   and the prepositions that introduce its arguments), on the proved grammar engine.
3. **AP-3, joined acts.** Acts joined by *and* / *or* become rules on simple acts, by one fixed table per modal word
   (*must*, *must not*, *may*, *has the right to*). The result is an ordinary `norms@0` document, so every existing
   theorem applies.
4. **AP-4, readings from derivations.** Where the English gives more than one structure (a modifier over a list, a
   prepositional phrase that can attach in two places, *may* or *right to* with *or*), the readings are the phrase's
   derivations, each read through the table. A reading set that names its source phrase is checked to be exactly
   those readings, and the separating situations are built by Lean.
5. **AP-5, specialisation premises.** Acts with more modifiers specialise acts with fewer, with the premises standard
   deontic logic licenses, for permission and obligation.

AP-0 is a measured baseline with no code. AP-6 to AP-8 are experiments with pre-registered bars.

| Batch | What | Hours (*estimate*) | Moves a pilot number | UDHR bytes (*estimate*) |
|---|---|---|---|---|
| AP-0 | baseline: re-try the 11 units under today's language; count "classified as" sentences; tag constitution workarounds | 2, pilot job, no product code | M1 (if any unit is expressible today), M3 measured | measured, not estimated |
| AP-1 | `acts@0`: long single acts, fixed phrases, entitlement wordings | 6 | M1, M2, M3, M4 | 457 (u039, u085, u106); up to 658 with u091 |
| AP-2 | the act grammar on `VE.Grammar` (Lean only) | 5 | none (enabler) | 0 |
| AP-3 | joined acts split by the table | 5 | M1, M2, M4 | 76 (u079b) |
| AP-4 | readings from derivations; exact reading sets | 6 | M1, M2, M5 | 288 (u076, u092) |
| AP-5 | specialisation premises | 4 | answers, not bytes | 0 |
| AP-6 | experiment: n-ary bound slots (two routes) | 4 | decision | (u019, u057 co-blocked: 389) |
| AP-7 | experiment: do derivations find the auditors' readings? | 3 | decision | — |
| AP-8 | experiment: frames proposed from sense packs | 3 | decision | — |

Total about 38 h (*estimate*). UDHR claimed coverage is 43.90% today; after AP-1, AP-3 and AP-4 it would be about
51.4% to 53.3% (*estimate*, before audits).

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
| D1 | How `acts@0` enters | A decoding extension of `norms@0`: the act check and the elaboration are chosen by the document's profiles inside the existing decoders. It is not a composition wrapper: no new route head, response or service mode until AP-4's proposal tool. | AP-1 |
| D2 | Budgets | Act phrase ≤ 400 bytes; fixed phrase ≤ 300 bytes; ≤ 128 fixed phrases and ≤ 128 frames per document; parser cap 2 when one reading is required, 64 when listing readings (= the `readings@1` limit); a parse over budget is a refusal, never a choice. | AP-1 |
| D3 | The modal × connective table (2.3) | as written; frozen when AP-3 merges | AP-3 |
| D4 | The edge rule for modifiers (2.4) | as written; frozen when AP-4 merges, after AP-7's first measurement | AP-4 |
| D5 | Specialisation premises for plain entitlements | no: permission and obligation only (licensed by standard deontic logic); entitlements stay UNKNOWN between related acts | AP-5 |
| D6 | n-ary route | decided by AP-6's pre-registered bar | after AP-6 |
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

In authoring, the writer picks one. The chosen paraphrase has one reading by AP-2's `read_normal`. In translation,
both stay, as a reading set whose source is the original phrase (AP-4). Nobody sees brackets, slots or frames. The
IDE asks in plain words ("Is 'a fair and public hearing by an independent and impartial tribunal' one thing?").

### 2.2 The act grammar (AP-2)

Tokens are words, declared fixed phrases (longest match, read as one token), slots `{i}` and commas. A curly
apostrophe is read as `'`. A **frame** is a head with its **markers**: the words that may introduce its arguments.
The head is a verb of one or more words ("take part"), or, after *has the right to* / *is entitled to*, a noun
("security", "protection"). `""` stands for the direct object (`["", "from", "in"]` for *seek*). A frame also lists
the markers whose joined fillers read as joined acts (its `split` markers, 2.3).

The grammar, informally (the specification writes the rule table):

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
("to seek and to enjoy"). A simple act is a head, its arguments (marker and filler) and its modifiers.

The grammar also has one fallback rule: a run of AP-1-acceptable tokens with no join word and no comma reads as one
simple act whose words are as written. This is what makes `reads_lexical` hold for every act AP-1 accepted. Two
derivations with equal act trees are one reading; two with different trees are two readings.

**Clause words** are refused anywhere in an act, fixed phrases included: *true false is equals not if then every
there exists believes must eventually no*. That is today's `actReserved` without *and*, *or* and *for*. A finite
clause ("of which he is the author", "if necessary") belongs in the rule's guard, written in guard English. This is
the same division `right-clauses@0` makes between act phrase and clause. **Join words** (*and, or, nor, for*) and
commas may stand outside fixed phrases only in AP-2's grammar positions (`join`, list commas, *for* as a marker or a
modifier), from AP-3 on. *Either*, *neither* and *both* are ordinary words until a join word follows them.

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
specification fixes. A name over the length limit is refused, never shortened silently. Each source rule becomes one
rule per simple act, named `<rule>-a<i>`, with the same guard, carve-outs and completion. An `unspecified` predicate's
parts are `unspecified` too. Precedence follows the simple acts (`M over N` gives `M-a<i> over N-a<i>`). An obligation
and its permission dual split together, so `actChecks` sees matching acts.

### 2.4 Modifier scope and attachment (AP-4; decision D4)

- A modifier **before** a list of joined items reads over the first item or over all of them.
- A modifier **after** the list, or a prepositional phrase in the last item before a shared object, reads over the
  last item or over all of them.
- A modifier inside a middle item reads over that item only.
- **No skipped middle:** a modifier never reads over some of the items but not one between them.

So u105's *freely* has two readings, which is what its 2026-10-10 audit required. u055's *arbitrarily* has two,
the pilot's `both_acts` and `deprivation_only`. u051's "in other countries" has two. Several edge modifiers multiply
their readings, up to the 64-reading cap; beyond it the phrase is refused ("too many readings to list; split the
sentence"), never read one way.

### 2.5 Nothing accepted earlier changes meaning

AP-1 accepts only acts with no join word or comma outside fixed phrases (`Lexical.check_no_join`). AP-2 reads every
such act as exactly one simple act whose words are as written (`reads_lexical`). AP-3 and AP-4 give meaning only to
phrases AP-1 refused. Every act `canonicalAct` accepts today, `acts@0` accepts with the same canonical string
(`Lexical.check_extends`), with one exception. An act containing *nor* is one opaque act today, and AP-3 gives
*nor* a meaning, so `acts@0` refuses it outside a fixed phrase rather than let its meaning change. Act identity stays `(sorts, canonical act, role)` with the canonical act **as written**.
The normal order (`Atom.normal` in section 3: head, object, marked arguments in frame order, modifiers) is used only
for generated paraphrases and for the simple acts of a split, never to rename a declared act.

### 2.6 Specialisation (AP-5; decision D5)

Simple act *a* specialises simple act *b* (`a ⊑ b`) when:

- they have the same head;
- every argument of *b* is an argument of *a* with the same filler;
- every modifier of *b* is a modifier of *a*.

For two declared simple acts with the same role and argument sorts and `a ⊑ b`, Lean adds the premise
`∀ x̄. p_a(x̄) → p_b(x̄)`:

- **permission:** may seek asylum in other countries → may seek asylum;
- **obligation:** must seek asylum in other countries → must seek asylum.

Both are the RM rule of standard deontic logic: doing *a* is a way of doing *b*. The contrapositive of the
permission premise is "must not *b* → must not *a*". Plain entitlements get no premise (D5). The legend shows each
premise as one plain sentence.

### 2.7 Arguments: fixed, bound, and more than two

A filler is a slot bound to one of the rule's arguments (a situation variable, universally quantified as every rule
variable is) or fixed words. A regulated predicate keeps one or two arguments in AP-1 to AP-5. A finite clause about
a bound filler goes into the guard. More than two bound slots ("a duty of a bearer to a person on a ground", u019 and
u057) waits for AP-6.

### 2.8 Wire (AP-1, extended by AP-2 and AP-4)

Under `acts@0` only (D1):

- the vocabulary gains `"acts": {"fixed": [...], "frames": [...], "sources": [...]}`;
- a regulated declaration's `act` is checked by `VE.Acts.Lexical.check` (AP-1) or `VE.Acts.read` (AP-2 on) instead
  of `canonicalAct`;
- a plain declaration may carry `act` and `form` ∈ {"has the right", "is entitled"}.

Every field is part of the canonical environment bytes, so `environment_id` changes when any of them changes and is
unchanged for every existing environment. Without `acts@0` the decoders are today's (`decodeRegulated_without_acts`).

### 2.9 Who owns what

| Piece | Owner | Others |
|---|---|---|
| Accepting acts, fixed phrases, frames; reading acts; the table; elaboration; readings; source exactness; specialisation premises; honest wordings | Lean (`lean/VE/Acts/*`, the hooks listed per batch) | — |
| Loading the `acts` block, registering the profile name, CLI, display of Lean's wordings and paraphrases, relaying AP-4's proposal mode | Python | no check, no split, no paraphrase computed in Python |
| Fast checks | Rust | under `acts@0` Rust skips its act lint (Lean's admission has run) and treats acts as opaque identity strings, as it does today; no copy of the grammar |

**Not duplicated:** the reserved list (Lean's `actReserved`, filtered), verb morphology (`conjugatedAct` and
`verbBase` in Lean), the wording lint (Lean V6), and the reading-set separation (`separates`).

**Retired for `acts@0` documents:** Python's display fallback for plain predicates (their wording is Lean's) and
Rust's act lint. **Not touched:** Python's norm-sentence matcher. It matches a declared act as one exact terminal
today and keeps doing so; moving it to Lean is E3's.

## 3. Lean statements

These are the statements the specification and the statement review start from. Names follow the existing modules.
Each block's header names its file and batch. Bodies are omitted; every theorem is proved in its batch, with no
`sorry` and only the allowed axioms (`lean/audit.py`).

```lean
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

/-- Every act today's check accepts and that has no "nor" is accepted with the same canonical string. An act with
    "nor" (one unanalysed act today) is refused under `acts@0` until AP-3 gives "nor" its meaning (2.5). -/
theorem check_extends (fx : List String) (h : fixedOk fx = true) {name : String} {k : Nat} {raw : Lean.Json} {a : String}
    (hc : VE.Norms.Wire.canonicalAct name k raw = .ok a)
    (hn : ∀ w ∈ VE.Norms.Wire.words a, w.toLower ≠ "nor") : check fx name k raw = .ok a
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

/-! lean/VE/Norms/Wire.lean, one change (AP-1): the act check is chosen by the document's profiles. -/
def VE.Norms.Wire.decodeRegulatedIn (profiles : List String) (fx : List String) :
    String → List String → Lean.Json → Except String VE.Norms.Regulated
theorem VE.Norms.Wire.decodeRegulated_without_acts (ps fx : List String) (h : "acts@0" ∉ ps) :
    decodeRegulatedIn ps fx = decodeRegulated

/-! lean/VE/Compose/Dispatch.lean, one row (AP-1): `acts@0` is registered and requires `norms@0`;
    `TodayList` gains `("acts@0" ∈ ps → "norms@0" ∈ ps)`; `todayGate_sound` and `todayGate_complete` re-proved. -/

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

/-- `all shared xs`: joined by "and"; `shared` when the items share one "to" (2.2). -/
inductive Act | one (a : Atom) | all (shared : Bool) (xs : List Act) | any (xs : List Act)

def framesOk (fs : List Frame) : Bool
def Term : Type                                  -- the grammar's terminals over `Lexical.Tok`
instance : VE.Grammar.Accepts Term Lexical.Tok
def grammar (fs : List Frame) : VE.Grammar.Grammar Term
def meaning (fs : List Frame) : VE.Grammar.Meaning Lexical.Tok Unit String Act

theorem grammar_wf (fs : List Frame) (h : framesOk fs = true) : (grammar fs).wf = true

/-- One reading required (authoring, and every declared act). -/
def read (fs : List Frame) (b : Nat) (ts : Array Lexical.Tok) : VE.Grammar.Outcome Lexical.Tok String Act
/-- Every reading, equal act trees once, in derivation order (translation). -/
def readings (fs : List Frame) (cap b : Nat) (ts : Array Lexical.Tok) : Option (List Act)

theorem read_one (fs) (h : framesOk fs = true) {b ts A c} (hr : read fs b ts = .ok A c) :
    VE.Grammar.OneReading (grammar fs) (meaning fs) () ts.toList A c ()
theorem readings_exact (fs) (h : framesOk fs = true) {cap b ts As} (hp : readings fs cap b ts = some As)
    (hl : As.length < cap) (A : Act) :
    A ∈ As ↔ ∃ d c, VE.Grammar.Derives (grammar fs) (.n (grammar fs).start) ts.toList d ∧ meaning fs () d = .ok (A, c, ())
theorem readings_nodup (fs) {cap b ts As} (hp : readings fs cap b ts = some As) : As.Nodup

/-- 2.5: an act AP-1 accepted reads as one simple act whose words are as written. -/
def Atom.ofLexical (ts : List Lexical.Tok) : Atom
theorem reads_lexical (fs) (h : framesOk fs = true) {fx name k raw a ts}
    (hc : Lexical.check fx name k raw = .ok a) (hl : Lexical.lex fx a = .ok ts) :
    ∃ b0, ∀ b, b0 ≤ b → read fs b ts.toArray = .ok (.one (Atom.ofLexical ts)) false

/-- Render round trip: the normal form of a simple act (verb, object, marked arguments in frame order, modifiers)
    reads back with one derivation as the same act in normal order. -/
def Atom.normal (fs : List Frame) (a : Atom) : List Lexical.Tok
def Atom.canon (fs : List Frame) (a : Atom) : Atom
def atomOk (fs : List Frame) (a : Atom) : Bool
theorem read_normal (fs) (h : framesOk fs = true) (a : Atom) (ha : atomOk fs a = true) :
    ∃ b0, ∀ b, b0 ≤ b → read fs b (a.normal fs).toArray = .ok (.one (a.canon fs)) false
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
theorem table_must_all (fs s xs as) (h : simple xs = some as) : table fs .must (.all s xs) = [as]
theorem table_must_any (fs xs) (h : 2 ≤ xs.length) : table fs .must (.any xs) = [[Atom.joined fs (.any xs)]]
theorem table_mustNot_any (fs xs as) (h : simple xs = some as) : table fs .mustNot (.any xs) = [as]
theorem table_mustNot_all (fs s xs as) (h : simple xs = some as) (h2 : 2 ≤ xs.length) :
    table fs .mustNot (.all s xs) = [as, [Atom.joined fs (.all s xs)]]
theorem table_may_all_own (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as) :
    table fs op (.all false xs) = [as]
theorem table_may_all_shared (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as)
    (h2 : 2 ≤ xs.length) : table fs op (.all true xs) = [as, [Atom.joined fs (.all true xs)]]
theorem table_may_any (fs xs as) (op) (hop : op = .may ∨ op = .right) (h : simple xs = some as)
    (h2 : 2 ≤ xs.length) : table fs op (.any xs) = [as, [Atom.joined fs (.any xs)]]
theorem table_needNot (fs A) (h : ∀ a, A ≠ .one a) : table fs .needNot A = []

/-- A document whose acts@0 predicates carry their read act trees; `U` is the `norm-defaults@0` form
    (`unspec = []` for a plain `norms@0` document). -/
structure ActsDoc where
  U : VE.NormDefaults.UDoc
  frames : List Frame
  acts : List (String × Act)

def WellFormedActs (D : ActsDoc) : Bool
/-- AP-3: every rule on an act with exactly one reading becomes rules on its simple acts; any other count refuses. -/
def elaborate (D : ActsDoc) : Except String VE.NormDefaults.UDoc

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

/-- Every reading of a phrase under a modal: each derivation's act tree through the table, equal lists once. -/
def phraseReadings (fs : List Frame) (op : Op) (cap b : Nat) (ts : Array Lexical.Tok) : Option (List (List Atom))
theorem phraseReadings_exact (fs) (h : framesOk fs = true) {op cap b ts Rs} (hp : phraseReadings fs op cap b ts = some Rs)
    (hl : Rs.length < cap) (R : List Atom) :
    R ∈ Rs ↔ ∃ As A, readings fs cap b ts = some As ∧ A ∈ As ∧ R ∈ table fs op A

/-- A source: an act phrase as the source words it, its modal, and the reading sets (with their couplings) it is
    read into. -/
structure Source where
  phrase : String
  op : Op
  form : Option Lexical.Form
  sets : List String

/-- The choices of `D` restricted to the listed sets, one per combination their couplings allow
    (`VE.Readings.choices`, projected). -/
def choicesOn (D : VE.Readings.Doc) (sets : List String) : List (List (String × Nat))
/-- The simple acts the rules of one such choice regulate, after elaboration. -/
def choiceActs (D : VE.Readings.Doc) (fs : List Frame) (c : List (String × Nat)) : List Atom
def sourceCheck (D : VE.Readings.Doc) (fs : List Frame) (fx : List String) (cap b : Nat) (s : Source) :
    Except String Unit
/-- Exactness: the sets hold one choice per reading of the phrase and nothing else, and each choice regulates
    exactly the simple acts of its reading (as sets of acts). -/
theorem sourceCheck_exact (D fs fx cap b) (s : Source) (h : sourceCheck D fs fx cap b s = .ok ()) :
    ∃ ts Rs, Lexical.lex fx s.phrase = .ok ts ∧ phraseReadings fs s.op cap b ts.toArray = some Rs ∧
      (∀ R ∈ Rs, ∃ c ∈ choicesOn D s.sets, ∀ a, a ∈ choiceActs D fs c ↔ a ∈ R) ∧
      (∀ c ∈ choicesOn D s.sets, ∃ R ∈ Rs, ∀ a, a ∈ choiceActs D fs c ↔ a ∈ R)

/-- A separating situation built from simple acts: the status of an act in one reading and not the other holds,
    every other generated status is false. It is checked by the existing `VE.Readings.separates`, whose
    `separates_separated` gives `Separated`; no new soundness theorem is needed. -/
def atomSituation (D : VE.Readings.Doc) (s : String) (i j : Nat) : VE.Readings.Situation Nat
end VE.Acts

/-! lean/VE/Acts/Specialise.lean (AP-5) -/
namespace VE.Acts
def specialises (a b : Atom) : Bool
theorem specialises_refl (a : Atom) : specialises a a = true
theorem specialises_trans {a b c : Atom} : specialises a b = true → specialises b c = true → specialises a c = true
/-- One premise `∀ x̄. p_a x̄ → p_b x̄` per pair of declared simple acts of one permission or obligation role, equal
    sorts, a ⊑ b, a ≠ b. -/
def specPremises (E : VE.Norms.Doc) (acts : List (String × Atom)) : List VE.Formula
theorem specPremises_typed (E : VE.Norms.Doc) (acts : List (String × Atom)) (h : VE.Norms.WellFormed E = true) :
    ∀ φ ∈ specPremises E acts, φ.check E.E [] = true
theorem specPremises_plain (E acts) (p : String) (r : VE.Norms.Regulated) (hr : r ∈ E.T.regulated)
    (hp : r.role = .plain) : ∀ φ ∈ specPremises E acts, p ∉ VE.Norms.preds φ ∨ r.name ≠ p
end VE.Acts
```

AP-6 compares two routes and builds neither on `main` before D6. Their statements are part of the experiment:

```lean
-- route (a), reification: an act with k ≥ 2 bound non-subject slots becomes a binary predicate over the subject and
-- a case, plus k functional, total role relations of the case; faithful when one case exists per argument tuple.
theorem VE.Acts.Nary.reify_faithful (D : ActsDoc) (S : VE.Structure.{u}) (hc : OneCasePerTuple D S) :
    VE.Norms.holdsCatala (reify D).T S ↔ VE.Core.NaryIntended D S
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

### AP-0. Baseline (pilot job, no product code; 2 h)

- **Goal:** know which bytes truly need the language before any batch claims them (research 2.1, caveat).
- **Work** (in the UDHR and constitution pilot directories, by the orchestrator's pilot job):
  1. Re-try the 11 UDHR units of M1 as plain entitlements under today's language (`ve-green-ts-B1` or later),
     recording per unit `expressible_today: yes/no` and the reason.
  2. Count M3 in the four UDHR parts and the constitution's main document.
  3. Add `act_workaround ∈ {pointer, folded, shortened, none}` to the constitution's 18 norm units.
- **Pre-registered:** the "before" values are the research note's (M1 1,860 B, M2 5 units, M4 18 units). A unit made
  expressible by AP-0 is credited to AP-0, not to a later batch.
- **Moves:** possibly M1 (pilot repair). M3 gets measured.

### AP-1. Long single acts, fixed phrases, entitlement wordings (6 h)

- **Goal:** acts up to 400 bytes, holding declared fixed phrases, on every role. A plain predicate may carry an act
  and a form, and gets the wording "{0} has the right …" or "{0} is entitled …". No join word or comma outside a
  fixed phrase. Meaning unchanged: an act is still a canonical string with slots.
- **New files:**
  - `lean/VE/Acts/Lexical.lean` and `lean/VE/Acts/LexicalExamples.lean` (`#guard` fixtures A1 to A6, A13, A15 to
    A19);
  - `docs/spec/acts.md` (the specification, written before the batch);
  - `ve/wire_contract/acts@0.json` (contract source);
  - `tests/test_acts_lexical.py`.
- **Shared files** (one hunk each):

  | File | Change | Overlapping branch |
  |---|---|---|
  | `lean/VE/Norms/Wire.lean` | `decodeRegulatedIn` plus `decodeRegulated_without_acts` | `lean-first/b14b` edits this file: build after it merges |
  | `lean/VE/Compose/Dispatch.lean` | register `acts@0`; requires `norms@0`; re-prove `todayGate_sound` and `todayGate_complete` | checked with `git diff main...rd-9/integrate`: no overlap on 2026-10-12; re-check at build time |
  | `lean/VE/EnglishGrammar/Policy.lean` | the selected wording of a plain predicate with an act is `Lexical.wording`, beside the modal-form case at :504-507 | `question-answering/q2` does not touch it (measured) |
  | `ve/profiles.py` | the registry row and the gate mirror line | — |
  | `ve/environment.py` | load the `acts` block and the plain `act` / `form` fields as data, no check | — |
  | `ve/printer.py` (the natural renderer) | for a plain predicate with an act under `acts@0`, render with the wording Lean selected; Python's own lint makes no decision for it | — |
  | `rust/ve-kernel/src/environment.rs` | skip the act lint when the profiles contain `acts@0`; then `python3 tools/rust_build.py` | — |
  | `tools/layer_policy.py` | assign the new modules | — |
- **Generated:** wire-contract tables, `lean/VE.lean` (roots), `lean/VE/Audit.lean`, frozen inventory if touched,
  `lean/axioms.txt`, `lean/statements.txt` / `predicates.txt` / `declarations.txt`, trust tables (D8),
  `lean/checkers.lock`, `ve/assurance-manifest.json` (decoder pins reviewed by hand, as its note says),
  `tools/gate-collection.json`.
- **Statements:** all of `VE.Acts.Lexical`, `decodeRegulated_without_acts`, the re-proved gate theorems.
- **Tests:**
  - Python reads Lean's verdicts only: a document with `acts@0` and fixtures A1 to A3 checks; A5 and A6 are refused
    with Lean's diagnostic text, relayed.
  - Without `acts@0`, byte-identical decodes over the existing norms corpus (`tests/data/route-cases.jsonl` norms
    rows).
  - A plain predicate with an act renders its Lean wording, never "classified as".
- **Seeded bugs:**
  - Lean: let a comma pass outside a fixed phrase; fixture A5 must fail.
  - Python: drop the `form` field when loading; the wording test must fail.
  - Rust: keep the lint under `acts@0`; the A1 document must fail to load.
- **Deleted for `acts@0` documents:** the display fallback for plain predicates with an act; Rust's act lint. No
  check is copied into Python.
- **Moves** (*estimates*, after AP-0):
  - M1: u039, u085 and u106 (457 B), and possibly u091 (201 B).
  - M2: u020 and u059 (364 B). "Country or territory" and "the free and full consent of the intending spouses" are
    kept as fixed phrases or guards instead of a shorter wording.
  - M3: entitlements with an act render in English.
  - M4: the 7 Group C units' wordings are restored (the curly apostrophe, and *or* inside a fixed phrase).

### AP-2. The act grammar (Lean only; 5 h)

- **Goal:** `VE.Acts.grammar fs`, `meaning`, `read` and `readings` on the generic engine; frames in the `acts`
  block; the render round trip. The grammar is a Lean value, not a JSON table: Lean is its only reader, so it needs
  no `english_grammar_gen.py` entry and no `--actions-version`.
- **New files:**
  - `lean/VE/Acts/{Syntax,Grammar,Meaning,Read,Linearize}.lean`;
  - `lean/VE/Acts/GrammarExamples.lean`, with every fixture of section 5 as a `#guard` on its derivation count and
    act tree.
- **Shared files:** none. Frames are parsed by AP-1's decoder hook only once AP-3 uses them, so AP-2 changes no
  route.
- **Generated:** roots, `Audit.lean`, axioms, statements, pins, gate collection.
- **Statements:** `grammar_wf`, `read_one`, `readings_exact`, `readings_nodup`, `reads_lexical`, `read_normal`.
- **Seeded bug (Lean):** add a rule attaching a premodifier to a middle item; the u105 fixture (A8) must report 3
  readings and fail.
- **Moves:** nothing (enabler). The constitution's hidden demand becomes measurable: AP-7 parses its 669 "norms"
  sentences' act parts with this grammar.

### AP-3. Joined acts (5 h)

- **Goal:** the table (2.3) and `elaborate`. Under `acts@0`, a declared act is read with `VE.Acts.read`: one
  derivation required (cap 2). A rule on it must have exactly one reading by the table. That reading's simple acts
  become predicates and rules. A rule with two or more readings is refused, with every reading as a plain
  paraphrase ("this rule has two readings: …"). In authoring the writer picks one; in translation the reading set
  arrives with AP-4's sources.
- **New files:**
  - `lean/VE/Acts/{Table,Elaborate,Faithful}.lean` and `lean/VE/Acts/ElaborateExamples.lean`;
  - `tests/test_acts_elaborate.py`.
- **Shared files:** `lean/VE/Norms/Wire.lean`, one more line: after decoding, `VE.Acts.elaborate` when `acts@0` is
  present (after `lean-first/b14b`).
- **The response question:** simple acts reach the display through the elaborated environment's lexicon (their
  wordings are Lean's), so no response row changes. If the specification finds a response must name a simple act's
  source predicate, that field is added with its shape (`lean/ResponseShape/Schemas/…`), encoder theorem, generated
  schema, relay binding and fuzz tests (the CLAUDE.md recipe), for about 2 h more.
- **Generated:** as AP-2, plus response schemas if a shape changes.
- **Statements:** `table_*`, `elaborate_identity`, `elaborate_wellFormed`, `elaborate_one_reading`,
  `elaborate_faithful`.
- **Tests:**
  - A6 (u027) gives two prohibitions; A7 (u079b) gives one obligation on "held by secret vote or by equivalent free
    voting procedures"; A14 (u0123.s03) gives six prohibitions.
  - Precedence and duals split pairwise.
  - Documents whose acts are all simple are byte-identical to AP-1's.
- **Seeded bugs:**
  - Lean: let `must` distribute over *or*; A7 must fail.
  - Python: display one row per source rule instead of Lean's per-simple-act wordings; the display test must fail.
- **Deleted:** nothing new; Python computes no split.
- **Moves:**
  - M1: u079b, 76 B (*estimate*: needs its subject carried from u079a, as u045b's is from u045a).
  - M2: u027 and u045a (197 B) lose their approximations: the lists become separate prohibitions instead of
    "ill-treatment" and "private life".
  - M4: the 4 Group B units and the 7 Group A units are on real acts. Group A's faithfulness still needs `attitudes`.

### AP-4. Readings from derivations; exact reading sets (6 h)

- **Goal:**
  - the edge rule (2.4) in the grammar, with `modifier_edges`;
  - `Source` and `sourceCheck`: a `readings@1` set that names its source phrase must hold exactly the phrase's
    readings (`sourceCheck_exact`);
  - `atomSituation`, built by Lean and checked by `separates`;
  - a proposal mode that lists the readings (and their paraphrases) of an act phrase, so the translator's tool writes
    the set Lean then checks.
- **New files:**
  - `lean/VE/Acts/{Readings,Sources,Situation,Run}.lean` and `ReadingsExamples.lean`;
  - `lean/ResponseShape/Schemas/ActReadings.lean` and `lean/ResponseShape/Encoders/ActReadings.lean` (with
    `runActReadings_fits`);
  - `ve/acts.py` (relay: schema and binding only, R8);
  - `tests/test_acts_readings_lean.py` and `tests/test_acts_readings_answer.py` (fuzz: each member dropped, emptied,
    retyped, duplicated, reordered, an index pushed out of range).
- **Shared files:**

  | File | Change | Overlapping branches |
  |---|---|---|
  | `lean/VE/Service/Protocol.lean` | the `act-readings` mode | `lean-first/b14d` and `question-answering/q2` both edit it (measured): build after both merge |
  | `ve/backends/service_schema.py` | `MODES` | — |
  | `ve/__main__.py` | `ve acts readings` | — |
  | `lean/VE/Readings/Run.lean` (admission, :222-243) | one call to `sourceCheck` per source when `acts@0` is present | `lean-first/b14d` does not touch it (measured); re-check at build time |
- **Generated:** response schemas, route cases (`tests/data/route-cases.jsonl` via `tests/route_case_recorder.py`),
  roots, `VE/Audit.lean`, `ResponseShape/Audit.lean`, axioms, statements, pins, assurance manifest, gate collection.
- **Statements:** `modifier_edges`, `phraseReadings_exact`, `sourceCheck_exact`.
- **Tests:**
  - A5 (u051), A8 (u105), A9 (u055), A10 (u092) and A11 (u076) give exactly 2 readings each.
  - A12 (u087) gives 2.
  - The pilot's rs_u055 and rs_u105b/rs_u105c with their coupling pass `sourceCheck`.
  - A set with a skipped-middle candidate is refused. A set missing a reading is refused.
- **Seeded bugs:**
  - Lean: drop the "all" reading of a pre-modifier; rs_u105b/c must be refused.
  - Python: relay a reading list with one reading removed; the binding test must report `CheckerUnavailable`.
- **Deleted:** the pilot's hand-built separating situations for these sets. Lean's `atomSituation` builds them, the
  proposal tool writes them into the document, and admission checks them with `separates`, as for any set.
- **Moves:**
  - M1: u076 and u092, 288 B (*estimate*).
  - M2: u055 checked exact.
  - M5: 3 sets checked against the English.

### AP-5. Specialisation premises (4 h)

- **Goal:** `specialises`, `specPremises`, entering the premises the route already threads for `Background` (the
  specification names the generator; today's pair premises are the model), and one legend sentence per premise.
- **New files:** `lean/VE/Acts/Specialise.lean` and `SpecialiseExamples.lean`; `tests/test_acts_specialise.py`.
- **Shared files:** the Background premise generator (one hook). The weighing and attitudes plans also want act
  relations there, so the cross-plan review should fix one owner first.
- **Statements:** `specialises_refl`, `specialises_trans`, `specPremises_typed`, `specPremises_plain`.
- **Tests:**
  - "may seek asylum from persecution in other countries" and "must not seek asylum from persecution" report a
    conflict.
  - "may a person seek asylum?" answers yes from the specific permission.
  - A plain entitlement gets no premise.
- **Seeded bug (Lean):** reverse the premise direction; the conflict fixture must fail.
- **Moves:** answers, not bytes.

### AP-6. Experiment: more than two bound slots (4 h; decision D6)

- **Question:** for u019 ("no distinction by a bearer between persons on a ground"), u057 and rights.md's
  `publish_about(person, item, person)`, which route gives faithful three-place rules at the lower cost?
  - Route (a): reify a case with role relations inside binary norms.
  - Route (b): lift regulated arity to 6 over `VE.Core`.
- **Work:** build both on a scratch branch (not merged), after `lean-first/b14c` (n-ary core definitions) merges.
- **Pre-registered bar:** a route wins if it:
  - proves its faithfulness statement (section 3) with no new axiom;
  - checks the three fixtures within 1.25× the binary route's time on the same machine (measured by
    `tools/bench/test_perf.py`, never in the suite);
  - changes no existing theorem statement (route a) or re-proves all of `VE.Norms` over the embedding within
    4,000 lines (route b).

  If neither meets the bar, D6 is "not yet", and u019 and u057 stay co-blocked.

### AP-7. Experiment: do derivations find the auditors' readings? (3 h, after AP-4)

- **Sample** (fixed now): every UDHR unit with a coordinated act or an edge modifier (u020, u027, u045a, u051, u055,
  u059, u076, u079b, u087, u092, u105a–c, u106) and 30 constitution norm sentences drawn with
  `random.Random("act-phrases-AP7")` from the units whose excerpt contains *and* or *or* inside the verb phrase.
- **Method:**
  - Two blind auditors (the pilot audit protocol; a Sonnet proxy only under the lead's rules for proxies) list each
    sentence's readings in plain English before seeing Lean's.
  - Lean's `readings` lists its own.
  - Matching is by paraphrase, done by a third auditor.
- **Pre-registered bar:**
  - recall ≥ 90% of the readings both auditors list;
  - ≤ 10% of Lean's readings judged "not a reading of this English" by both;
  - no skipped-middle reading.

  Below the bar, D4 is revised before `acts@0` ships AP-4.

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
phrase. Expected results are what the batch must show.

| # | Unit | Act phrase under `acts@0` | Batch | Expected |
|---|---|---|---|---|
| A1 | u039 | `{0} in full equality to [a fair and public hearing by an independent and impartial tribunal] in {1}`, form "is entitled"; guard: the determination is of the person's rights and obligations or of a criminal charge against the person | AP-1 | accepted (97 bytes, over today's 80); wording "… is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in …" |
| A2 | u085 | `{0} to [equal pay for equal work] without any discrimination`, form "has the right"; open terms `discrimination`, `equal_pay_for_equal_work` | AP-1 | accepted |
| A3 | u106 | `{0} to the protection of [the moral and material interests] resulting from {1}`, sorts person and production; guard: the person is the author of the production, and the production is scientific, literary or artistic | AP-1 | accepted |
| A4 | u051 (today's wording) | `{0} to seek as well as enjoy in other countries asylum from persecution` | AP-1, AP-2 | accepted; reads as one simple act (`reads_lexical`) |
| A5 | u051 (source) | `{0} to seek and to enjoy in other countries asylum from persecution` | AP-1; AP-4 | AP-1: refused, *and* outside a fixed phrase. AP-4: 2 readings ("in other countries" on *enjoy* or on both) |
| A6 | u027 | `{0} be subjected to torture or to [cruel, inhuman or degrading treatment or punishment]`, permission, sign false; frame `be subjected` with `split: ["to"]` | AP-1; AP-3 | AP-1: refused. AP-3: two prohibitions |
| A7 | u079b | `{0} be held by secret vote or by [equivalent free voting procedures]`, obligation | AP-1; AP-3 | AP-1: refused (or accepted with the two ways as one fixed phrase). AP-3: one obligation on the whole act; "by" is not a split marker |
| A8 | u105a–c | `{0} freely to participate in [the cultural life of the community], to enjoy the arts and to share in [scientific advancement and its benefits]`, form "has the right" | AP-4 | exactly 2 readings (*freely* on the first act, or on all); the pilot's coupled rs_u105b/rs_u105c pass `sourceCheck` |
| A9 | u055 | `{0} be arbitrarily deprived of their nationality nor denied [the right to change their nationality]`, permission, sign false | AP-4 | exactly 2 readings = rs_u055's `deprivation_only` and `both_acts` |
| A10 | u092 | `{0} to security in the event of unemployment, sickness, disability, widowhood, old age or [other lack of livelihood] in circumstances beyond their control`, frame *security* with `split: ["in the event of"]` | AP-4 | 2 readings ("in circumstances beyond their control" on the last cause, or on all) |
| A11 | u076 | `{0} to take part in {1} directly or through [freely chosen representatives]`, form "has the right"; the country slot as u077 | AP-4 | 2 act readings (each way, or one of the ways) × u077's 2 country readings |
| A12 | u087 | `{0} to form and to join trade unions for the protection of their interests` | AP-4 | 2 readings ("for the protection …" on *join* or on both); the split itself (*to … and to …*) is AP-3's |
| A13 | u0156.s03 | `{0} actively deceive {1} about [the existence of a system prompt or its content]` | AP-1 | accepted; replaces "existence-or-content" |
| A14 | u0123.s03 | the six acts after "cannot instruct Claude to", joined by *or*, permission, sign false; *while* and *when* clauses move to guards | AP-3 | six prohibitions; "instruct" stays `speech-acts@0`'s |
| A15 | u024, u037 | two predicates with act `{0} take place` and different sorts | AP-1 | accepted (act identity includes sorts); the specification decides whether wording distinctness may also use sorts (open question 8.3) |
| A16 | u041 | `{0} to be presumed innocent until proved guilty according to law in [a public trial at which they have had all the guarantees necessary for their defence]` | AP-1 | accepted as words; not counted in M1 (time is events-time-causation's) |
| A17 | — | `{0} take part if {1} is open` | AP-1 | refused: clause word (*if*, *is*); "write the condition in the guard" |
| A18 | — | fixed phrase "the court that is competent" | AP-1 | refused: clause word in a fixed phrase |
| A19 | u0263.s04.p2 | `{0} comply with [the operator’s instructions] in {1}` | AP-1 | accepted; `’` read as `'` |
| A20 | — | `{0} must seek asylum` | AP-1 | refused: clause word *must* |

A1's byte count was counted by hand on the act string above; the `#guard`s pin every count.

## 6. Dependencies on other work

| Needs | From | Used by | If it is late |
|---|---|---|---|
| `lean-first/b14b` merged (edits `Norms/Wire.lean`) | lean-first | AP-1, AP-3 | AP-1 builds its new files first and adds the decoder hunk last |
| `lean-first/b14d`, `question-answering/q2` merged (edit `Service/Protocol.lean`) | lean-first, QA | AP-4's proposal mode | AP-4 ships `sourceCheck` first; the mode follows |
| `lean-first/b14c` merged (n-ary core definitions) | lean-first | AP-6 | AP-6 waits |
| `rd-9/integrate` | readings-defaults | none directly; the constitution's soft rules get structured acts only once both exist | no effect on the UDHR batches |
| senses B6 (packs) | senses | AP-8 | frames stay declared |
| time ("until proved guilty", u041), modality ("can be fully realized", u108) | events-time-causation, attitudes | M1's remaining 345 B | those units stay counted under the siblings |
| typed attitudes on acts (Group A) | attitudes | constitution faithfulness | Group A stays on real acts but unfaithful |
| rights as objects and limitations (u082) | composition S2b, `right-clauses@0` | M1's remaining 277 B | stays residual |
| `right-clauses@0` | composition S3 | right lines with structured acts | independent: clauses keep finite clauses; acts keep verbs and fillers |

Every new Lean module is a new file under `lean/VE/Acts/`. The shared source files, in total:

- `lean/VE/Norms/Wire.lean` (AP-1, AP-3);
- `lean/VE/Compose/Dispatch.lean` (AP-1);
- `lean/VE/EnglishGrammar/Policy.lean` (AP-1);
- `lean/VE/Service/Protocol.lean` (AP-4);
- `lean/VE/Readings/Run.lean` (AP-4);
- the Background generator (AP-5);
- `ve/profiles.py`, `ve/environment.py`, `ve/printer.py` (AP-1);
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
| AP-3 | u079b → OPEN | +76 | 48.8% to 50.6% | Groups A and B on real acts (1,838 B, faithfulness; A still needs attitudes) |
| AP-4 | u076, u092 → READINGS | +288 | 51.4% to 53.3% | — |
| AP-5 | — | 0 | — | answers |
| beyond this plan | u041, u108 (siblings), u086 (research), u082 (rights as objects) | up to +838 | — | — |

The NORTH-STAR-style score (UDHR weight 4) is 0.30 to 0.37 after AP-4 (*estimate*), against an upper bound of 0.68
for all 1,860 B.

## 8. Risks and open questions

1. **AP-0 may shrink the credit.** That is its purpose; the faithfulness gains (M2, M4, M5) do not depend on it.
2. **Fixed phrases and frames are declarations an audit must check.** A fixed phrase hides its own coordination by
   design, and a frame without a marker removes an attachment reading. AP-7 measures the second. The audit checklist
   gains "fixed phrases name one thing; frames list the source's prepositions".
3. **Wording distinctness across sorts** (u024 and u037 both "take place"). Lexicon V4 compares wordings without
   sorts. Allowing equal wordings with different subject sorts needs a typed reading, which is the specification's
   call. AP-1 does not depend on it.
4. **Shallow separations.** Readings that differ in which simple acts they regulate separate in a trivial situation
   until AP-5 relates the acts. That is honest but weak, and the legend says so.
5. **Python's norm-sentence matcher** still matches long acts as exact terminals. That is safe for one reading (a
   terminal is literal), but it may be slow for very long acts (not measured). E3 moves it to Lean; if the gate shows
   a regression, AP-1 caps acts lower (D2).
6. **Freezing.** The table and the edge rule become part of `acts@0`'s meaning when AP-3 and AP-4 merge. AP-7 runs
   before AP-4 merges, on the AP-4 branch.
7. **Lean audit words.** `lean/audit.py` refuses the words *sorry, axiom, unsafe, partial, opaque, extern* (with word
   boundaries) even in comments and strings. Fixture strings are checked for them. "Impartial" passes (no word
   boundary), but a fixture or comment saying "opaque" would not: the plan's Lean text avoids it.

## 9. Shared pieces

The research note (section 8) lists ten abstractions several of the seven research-wave designs could share. The
plan's position on each:

| Shared piece | This plan builds | Others would use |
|---|---|---|
| Structured simple acts, act identity | `VE.Acts.Atom`, canonical act as written (AP-1 to AP-3) | weighing (same act?), attitudes ("knowingly provide …"), events-time-causation, speech acts' content |
| Act-performance predicate ("x does A") | not built; the review should place it (likely events-time-causation) | attitudes, causation |
| Readings from derivations, exact sets, Lean-built separations | `readings`, `sourceCheck`, `atomSituation` (AP-2, AP-4) | scope, attitudes, quantities, events |
| Edge rule for modifiers over a list, couplings | `modifier_edges` (AP-4) | attitudes, quantities, scope |
| Frames as n-ary relation schemas with English | `VE.Acts.Frame` (AP-2); n-ary via AP-6 | math-evidence, events, quantities |
| Modal × connective table | `VE.Acts.table` (AP-3) | weighing (soft "should A or B"), attitudes |
| Specialisation premises | `specPremises` (AP-5) | weighing, question answering |
| Fixed words as one thing; open terms for open words | fixed phrases (AP-1) | quantities, weighing |
| Finite clauses become guards | the clause-word rule (AP-1) | `right-clauses@0`, scope |
| Honest Lean wordings for every regulated predicate | `Lexical.wording` (AP-1) | every design adding predicates |
