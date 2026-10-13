# Action phrases (`acts@0`): specification

> Status: item-1 statement specification, draft 1 (2026-10-13), written from
> [act-phrases-PLAN.md](act-phrases-PLAN.md) draft 2. That draft applies the converged design debate
> (`manage-agents/debates/design-act-phrases/{fable,astra}.md`, CONVERGED after round 3) and the cross-plan review's
> edits (`manage-agents/debates/plan-synthesis/edits-act-phrases.md`); its section 10 maps them. This document gates
> every build batch except AP-0: the statement review (Astra and Fable) reads it first, then the DRI decides.
>
> Sections 4 to 8 are the statements. Section 14 lists every place where this draft chose between readings of the
> plan or sharpened one of its statements, and the findings the review must decide. Theorem statements and fixtures
> are obligations of the batches, not claims of finished proofs or tests.
>
> **Verification status.** Every statement of sections 4 to 8 that names only existing modules was type-checked in
> the scratch stub `lean/SpecStubs_act-phrases.lean` (51 statements, no `sorry`), and every fixture number of
> section 11 is computed there by a `#guard` (161 guards, all passing, on 2026-10-13 against `main` at `49de179e`).
> The numbers were first derived by hand; the stub confirmed all of them but one: A14 as the source words it is
> refused, because *false* is a clause word (finding F10). Section 15 says what the stub holds and what it does not
> (the AR-10 row, the response shapes and the AP-6 statements, whose modules do not exist yet).
>
> Inputs: [norms.md](norms.md) (W1), [norm-defaults.md](norm-defaults.md), [composition-s2.md](composition-s2.md)
> (`readings@1`), [english-lean.md](english-lean.md) (the grammar engine), `lean/VE/Norms/{Wire,Tree,Elaborate}.lean`,
> `lean/VE/Grammar/{Basic,Derives,Table,TableProofs,Reading}.lean`, `lean/VE/Readings/{Doc,Choice,Separate}.lean`,
> `lean/VE/Compose/Dispatch.lean`, `lean/VE/EnglishGrammar/{Encode,Policy}.lean`, the research note
> [docs/research/act-phrases.md](../research/act-phrases.md) and the cross-plan synthesis (`SYNTHESIS.md` 2.1, 2.2).
> Nothing here changes a frozen contract, a `norms@0` hash or a W1 theorem statement.

## 0. Scope, one paragraph

A rule regulates an act, and the act is written in its predicate's declaration as an **act phrase**: `{0} to take part
in {1} directly or through freely chosen representatives`. Under the profile `acts@0`, Lean reads act phrases in four
steps. **AP-1** accepts long single acts: up to 400 bytes, with declared **fixed phrases** (word groups that name one
thing), no clause word, and no *and*, *or*, *nor*, *for* or comma outside a fixed phrase; such an act keeps its
canonical string as its identity and meaning for ever, and a plain entitlement gets the honest wording "has the
right …". **AP-2** reads every other act phrase with a small grammar on Lean's proved engine, against declared
**frames** (a head word and the prepositions that introduce its arguments and modifiers) and declared adverbs; a
phrase's meaning is an **act tree** (one simple act, or simple acts joined by *and*, *or* or *nor*), and Lean
certifies a meaning only from a complete enumeration of derivations. **AP-3** turns a rule on a joined act into rules
on its simple acts by a fixed table per modal word, refusing every rule the table gives zero or several readings,
and exports the map from each generated predicate and rule to its source. **AP-4** lists the readings of an
ambiguous phrase and checks that a reading set naming the phrase holds exactly those readings. **AP-5** defines when
one simple act is a way of doing another, using only declared restrictive words; nothing uses it until AP-5b.

In this specification: definitions (1), the English people read and write (2), the wire form (3), the Lean
statements per batch (4 to 9), diagnostics (10), acceptance fixtures (11), limits and generated files (12), the
review checklist (13), choices and findings (14), and the stub (15).

Out of scope, by the plan: more than two bound slots (AP-6, an experiment); conditions and participles inside an
object (research R4); acts as events (events-time-causation's ET-D2); attitudes over acts; any change to Python's
norm-sentence matcher (E3's).

## 1. Definitions

### 1.1 Act phrases, tokens and fixed phrases (AP-1)

An **act phrase** is a JSON string in a regulated declaration's `act` field. Its **canonical act** is the string with
every curly apostrophe U+2019 replaced by `'` and every run of whitespace (Python `str.isspace`, as `canonicalAct`
splits) replaced by one space, with no leading or trailing space.

A canonical act is read as a list of **tokens**:

- a **slot** `{i}`: a word that is exactly `{`, decimal digits and `}`;
- a **comma**: a `,` written at the end of a word, which then must be followed by another word;
- a **fixed phrase**: an occurrence of a declared fixed phrase, read as one token;
- a **word**: anything else between spaces.

A document declares its fixed phrases in the `acts` block (3.1). The list is acceptable (`fixedOk`) when:

1. it has at most 128 phrases;
2. each phrase, canonicalised like an act, is at most 300 bytes;
3. each phrase reads as words and commas only (no slot, commas placed as above), every word made of ASCII letters with
   inner `'` or `-` (`actWord`), and no word a clause word (1.2);
4. each phrase holds at least two words, and begins and ends with a word that is not *and*, *or*, *nor* or *for*;
5. no phrase is declared twice;
6. no phrase holds another, and no two occurrences can overlap: no proper suffix of one phrase's tokens is a prefix
   of another's (or of its own), and no phrase's tokens occur inside another's.

Condition 6 makes the grouping of a token list unique: every occurrence of a declared phrase becomes one `fixed`
token, and there is never a choice between two groupings. It replaces the plan's "longest match" (14, C13).

### 1.2 Word lists

- **Join words** (AP-1): *and, or, nor, for*. In AP-1 they may stand only inside a fixed phrase.
- **Clause words**: today's `actReserved` without the join words: *true, false, is, equals, not, if, then, every,
  there, exists, believes, must, eventually, no* (14 words). They may not stand anywhere in an act or a fixed phrase.
- **Grammar join words** (AP-2 on): *and, or, nor*. *For* is an ordinary marker word in the grammar ("for the
  protection of their interests").
- **Function words** (AP-2 on): *to* and *be*, read by the grammar itself, never part of a head or a filler.

### 1.3 Lexical acts (AP-1)

`check fx name k raw` accepts a lexical act exactly when (the independent statement is `Accepts`, 4.3):

1. `raw` is a string; its canonical act starts with `{0} `;
2. the slots, in order of occurrence, are `{0}` to `{k-1}`, each once (as `canonicalAct`, with `scanSlots`);
3. with every slot replaced by the word `slot`, it has at least two words, and every word, without a final comma, is
   an `actWord`;
4. it is at most 400 bytes;
5. no word is a clause word;
6. its tokens contain no join word and no comma outside a fixed phrase, and it does not end with a comma.

It returns the canonical act. Conditions 1 to 3 are `canonicalAct`'s, so every act today's check accepts and that has
no *nor* passes them with the same string (`check_extends`). An accepted act **never enters the grammar**: its
identity, `(sorts, canonical act, role)`, and its meaning are its canonical string, permanently.

### 1.4 Frames, adverbs and the grammar's vocabulary (AP-2)

A **frame** declares a head and its prepositions:

| Field | Meaning | Example (u092) |
|---|---|---|
| `head` | one or more words, not *to* or *be* | `security` |
| `markers` | argument markers: `""` is the direct object, which is then **required**; others are words ("in the event of") | `["in the event of"]` |
| `split` | argument markers whose joined fillers read as joined acts (2.3 of the plan); a subset of `markers` | `["in the event of"]` |
| `modifiers` | modifier markers: prepositions that introduce how, where, why or by what means the act is done | `["in circumstances"]` |

The document also declares its **adverbs**: single words that say how an act is done ("freely", "arbitrarily",
"directly"). The frames and adverbs together are the **vocabulary** `V` of the act grammar.

`framesOk V` holds when: at most 128 frames; heads distinct and none a word-prefix of another; each head word an
`actWord` in lower case and not a join, function or clause word; in each frame the markers are distinct, the modifiers
distinct and non-empty, no string is both an argument marker and a modifier marker, `split ⊆ markers`, every marker
word an `actWord` in lower case and not a grammar join word, *be* or a clause word, and no marker of the frame (argument
or modifier) a word-prefix of another; the adverbs distinct lower-case `actWord`s, none a join, function or clause
word, a marker word or a head word; and no head begins with a marker word.

**Filler words of a frame**: every word except the grammar join words, *to*, *be*, the adverbs, the first words of
the frame's markers and modifier markers, and the first words of all heads. A **filler** is one slot, one fixed phrase,
or a run of filler words.

These conditions are what makes the grammar of 5.2 give one derivation per reading: a run of filler words ends at a
known word, an argument and a modifier are never confused, and two markers never compete for the same words.

### 1.5 Act trees

```text
Part     := slot i | fixed i | words w₁ … wₙ
Filler   := one Part | joined (and|or|nor) Part₁ … Partₙ          -- n ≥ 2; a non-split marker's list
Modifier := adverb w | prep m Part                                  -- a modifier marker with its filler
Atom     := [to] [be] head, arguments (marker, Filler)…, modifiers…   -- a simple act
Act      := one Atom | all shared split Atom₁ … Atomₙ | any nor split Atom₁ … Atomₙ    -- n ≥ 2
```

`all` is a join by *and*; `shared` says the atoms share one *to* (the second and later items have no *to* of their
own). `any` is a join by *or*, or by *nor* when `nor`. `split` says the join is a split marker's (the frame declares
the argument distributive). An act tree has **one join level**: a phrase with a join inside a joined item, or with
two join words in one list, has no reading (14, C2).

A **simple act of a reading** is an atom, or a whole join read as one act ("A or B" under *must*; "A and B" done
together): `Simple := atom Atom | whole Act`.

### 1.6 Derivations, readings and limits

The **derivations** of a token list are the trees of `VE.Grammar.Derives (grammar V)` from the start symbol. Each
derivation has at most one **meaning** (an act tree), computed by `meaning V` (5.3). The **readings** are the distinct
meanings, in derivation order.

Three limits apply, each with a constant fixed by AP-0 (D2):

| Limit | Constant | Provisional value | What happens at the limit |
|---|---|---|---|
| raw derivation budget | `rawCap` (N) | 256 | the parser's cap: a parse that returns N trees is **saturated** and may hide more |
| step budget | `stepBudget` | 2,100,000 (the order of `VE.EnglishGrammar.workBudget`; a separate constant, measured with N) | the parse stops |
| public listing limit | `maxReadings` | 64 (= `readings@1`'s `maxChoices`) | more readings than this are not listed |

A listing is `ok xs` only when the parse finished within the step budget, returned fewer than N trees, and gave at
most 64 distinct meanings. Every other case is `limit`: a refusal, never a choice. Exactly 64 readings are listed.

### 1.7 Modal words, ops and readings of a rule (AP-3)

A rule's **op** is fixed by its predicate's role and its sign (`opOf`): obligation true *must*, obligation false *need
not*, permission true *may*, permission false *must not*, plain true *has the right to* (or *is entitled to*, by the
declaration's form). Plain false has no op: a joined act under it is refused.

The **table** (5 of the plan's 2.3; 6.2 here) gives, for an op and an act tree, the list of readings, each a list of
simple acts. A rule on a joined act is **elaborated** only when the table gives it exactly one reading and every rule
on its predicate and on its predicate's dual gives the same one. A reading of two or more atoms **splits** the
predicate `p` into **parts** `p__1 … p__n` (one per atom, in order) and every rule `r` on it into `r-a1 … r-an`. A
reading of one simple act keeps `p` as it is.

### 1.8 Sources (AP-4)

A **source** names an act phrase as the source words it, an explicit **source template** (the role and sign, which fix
the op; the guard, exceptions and precedence; the completion), the units every reading shares, and the reading sets
the phrase is read into. A source is **exact** when its sets' choices correspond one to one to the phrase's readings,
complete against the grammar, and every choice's rules regulate exactly its reading's simple acts with the template's
context.

### 1.9 Restrictive declarations (AP-5)

The `acts` block may declare **restrictive** markers and adverbs: those that, added to an act, give a way of doing it
("in other countries" for *seek asylum*). They are visible semantic assumptions the audit checks. Nothing else
narrows an act.

## 2. The English (one reading each)

### 2.1 Wordings

| Predicate | Wording | Example |
|---|---|---|
| plain, with an act and a form (AP-1) | `Lexical.wording`: `{0} has the right` or `{0} is entitled`, then the act after its `{0} ` | `{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}` (A1) |
| permission or obligation | unchanged: `{0} may`, `must`, `must not`, `need not`, then the act after its `{0} ` | `{0} must not be subjected to torture` |
| a part `p__i` (AP-3) | as its source's role gives, over the part's act: the rendering of its atom in normal order (5.5) | `{0} be subjected to cruel, inhuman or degrading treatment or punishment` |

A reader never sees "classified as …" for a plain predicate with an act under `acts@0`. Lexicon V4 (wording
distinctness) is not changed: two predicates whose wordings are equal stay a V4 duplicate (A15; 14, C24).

### 2.2 Paraphrases of readings

Each reading is shown as one plain sentence, built by `paraphrase` (6.2) from the subject slot, the modal words and
the rendered simple acts:

- **one simple act** `a`: `{0} <modal> <a>.`;
- **a split** `a₁ … aₙ`: the sentences for each part, joined by `, and ` when there are two, and as `s₁; s₂; …; and
  sₙ.` when there are more;
- **a whole join by *and***: `{0} <modal> <the source act>, as one act done together (not each on its own).`;
- **a whole join by *or***: `{0} <modal> <the source act>, as one act done in any one of these ways (not each way on its
  own).`

`<modal>` is *must*, *need not*, *may*, *must not*, *has the right* or *is entitled*; `<a>` is the act's rendering
without its `{0} `. The display replaces `{0}` by the subject noun ("Everyone", "No one"), as for every rule today.

For u051 (A5), under *has the right*:

> This sentence has two readings.
> 1. Everyone has the right to seek asylum from persecution, and everyone has the right to enjoy asylum from
>    persecution in other countries.
> 2. Everyone has the right to seek asylum from persecution in other countries, and everyone has the right to enjoy
>    asylum from persecution in other countries.

For u076 (A11):

> This sentence has two readings.
> 1. Everyone has the right to directly take part in the government of their country, and everyone has the right to
>    take part in the government of their country through freely chosen representatives.
> 2. Everyone has the right to take part in the government of their country directly or through freely chosen
>    representatives, as one act done in any one of these ways (not each way on its own).

(The slot `{1}` shows as its filler's words; u077's two readings of "their country" multiply these, by u077's set.)

In authoring, a rule whose act has two or more readings is refused with this list, headed "This act has two readings.
Which do you mean?" (10, D-15). In translation the readings become a reading set whose source is the phrase (AP-4).

### 2.3 What the IDE asks, in plain words

| Declaration | Question |
|---|---|
| a fixed phrase | Is "a fair and public hearing by an independent and impartial tribunal" one thing? |
| an argument marker or a modifier marker | In "take part … through freely chosen representatives", does "through" say what the taking part is in, or how it is done? |
| a split marker | Does "subjected to torture or to cruel … treatment" mean two acts, "subjected to torture" and "subjected to cruel … treatment"? |
| an adverb | Does "freely" say how something is done? |
| a restrictive word (AP-5) | Is to seek asylum in other countries one way to seek asylum? |
| a reading (authoring) | This act has two readings. Which do you mean? (then the paraphrases) |

No question shows brackets, slots, markers or frames.

### 2.4 The reader's and auditor's checklist

1. Each fixed phrase names one thing; its own *and* or *or* is not a choice between acts.
2. Each frame lists the source's prepositions, and says which introduce what the act is about (arguments) and which
   say how, where or why (modifiers). A preposition left out removes an attachment reading.
3. Each split marker really is distributive in the source.
4. Each adverb says how the act is done.
5. Each restrictive declaration (AP-5) is true of the source's acts.
6. Each part's wording (2.1) says what the source says of that act.

Exactness is relative to these declarations (plan section 0); the audit checks them.

## 3. Wire form and identity

### 3.1 The `acts` block

Under `acts@0` only, the vocabulary may carry:

```json
"acts": {
  "fixed": ["a fair and public hearing by an independent and impartial tribunal"],
  "frames": [{"head": "seek", "markers": [""], "split": [], "modifiers": ["in"]},
             {"head": "enjoy", "markers": [""], "split": [], "modifiers": ["in"]}],
  "adverbs": ["freely"],
  "sources": [{"phrase": "{0} to seek and to enjoy in other countries asylum from persecution",
               "role": "plain", "sign": true, "form": "has the right", "default": "unspecified",
               "template": {"guard": ["top"], "unless": [], "over": []},
               "units": [], "sets": ["rs_u051"]}],
  "restrictive": {"markers": ["in"], "adverbs": []}
}
```

| Field | From | Decoder |
|---|---|---|
| `fixed` | AP-1 | `Lexical.decodeFixed` |
| `frames`, `adverbs` | AP-3 (AP-2 has them as Lean values only and changes no route) | `VE.Acts.Wire.decodeVocab`: `framesOk` |
| `sources` | AP-4 | `VE.Acts.Wire.decodeSource` |
| `restrictive` | AP-5 (used only under `act-specialise@0`, after AP-5b) | `VE.Acts.Wire.decodeRestrictive` |

Unknown fields are refused. A field whose batch has not landed is refused as unknown, so `acts@0` grows only by
accepting documents it refused before. An absent block is the empty block. The block is refused without `acts@0`, as
today (the frozen vocabulary decoder refuses the field).

### 3.2 Regulated declarations

Under `acts@0`:

- a permission's or obligation's `act` is checked by `Lexical.check` (AP-1), and from AP-3 on by `Wire.checkAct`
  (a lexical act, or a joined act with one meaning, 6.4);
- a plain declaration may carry both `act` and `form` (`"has the right"` or `"is entitled"`), or neither; a plain act
  is stored in `Regulated.act` like any act, and `Norms.Tree.check` admits it (4.1);
- every other field is as in `norms@0`.

### 3.3 Identity

`canonicalEnvironmentJson` replaces each `act` by its canonical act through `canonicalActIn`, which is `Lexical.check`
(AP-1) or `Wire.checkAct` (AP-3 on) under `acts@0` and `canonicalAct` otherwise (`canonicalActIn_without_acts`). The
`acts` block is kept as written. So `environment_id` changes when any `acts` field or act changes, and it is
unchanged for every environment without `acts@0`.

## 4. AP-1: Lean statements

### 4.1 Modules and hunks

| File | Kind | Content |
|---|---|---|
| `lean/VE/Acts/LexicalBase.lean` | new | `Wire.lean` lines 24–70 moved verbatim, in namespace `VE.Norms.Wire`, so every name is unchanged: `actReserved`, `scanSlotsAux`, `scanSlots`, `pyWhitespace`, `words`, `asciiLetter`, `actWord` |
| `lean/VE/Acts/Lexical.lean` | new | 4.2 and 4.3, importing `LexicalBase` only |
| `lean/VE/Acts/Compat.lean` | new | `check_extends`, importing `Norms.Wire` and `Acts.Lexical` |
| `lean/VE/Norms/Wire.lean` | hunk | imports `LexicalBase` and `Lexical`; `decodeRegulatedIn`; `decodeNormsEnvironment` calls it with the envelope's profiles and the block's `fixed`; `canonicalActIn` and its use in `canonicalEnvironmentJson` |
| `lean/VE/Norms/Tree.lean` | hunk | `check` drops its refusal of `.plain, some _` (`Tree.lean:314`) |
| `lean/VE/Norms/Plain.lean` | hunk (finding F1) | `decodeRegulatedAllIn ps fx`, and `decodeRegulatedAll = decodeRegulatedAllIn [] []` |
| `lean/VE/EnglishGrammar/Encode.lean` | hunk (F1) | `regulatedView` and `modalForm` read the environment's profiles and use the profile-aware decoders |
| `lean/VE/EnglishGrammar/Policy.lean` | hunk | the selected wording of a plain predicate with an act is `Lexical.wording`, beside the modal-form case at :504–507 |
| `lean/VE/Service/Standalone.lean` | hunk (F1) | its `regulated` validation uses `decodeRegulatedAllIn` with the environment's profiles |
| `lean/VE/Compose/Dispatch.lean` | AR-10 row | 4.4 |

`Wire.lean`, `Tree.lean` and `Plain.lean` are listed in `lean/VE/Route/frozen-sources.sha256`; their hunks regenerate
that inventory (12).

### 4.2 Definitions

```lean
namespace VE.Acts.Lexical
open VE.Norms.Wire (actReserved words actWord scanSlots)

def joinWords : List String := ["and", "or", "nor", "for"]
def clauseWords : List String := actReserved.filter (fun w => !joinWords.contains w)

inductive Tok | word (w : String) | fixed (i : Nat) | slot (i : Nat) | comma
  deriving DecidableEq, Repr

def maxActBytes : Nat := 400
def maxPhraseBytes : Nat := 300
def maxPhrases : Nat := 128

/-- U+2019 read as `'`. -/
def fold (s : String) : String := s.map (fun c => if c.toNat == 0x2019 then '\'' else c)
/-- The canonical form of an act or a fixed phrase: folded, whitespace normalised as `canonicalAct` does. -/
def normal (s : String) : String := " ".intercalate (words (fold s))
def dropComma (w : String) : String := if w.endsWith "," then w.dropRight 1 else w

/-- Words, slots and commas of a normal string (no fixed phrases). -/
def rawLex (s : String) : Except String (List Tok)
/-- A declared phrase's tokens, with the diagnostics of 1.1 conditions 2 to 4. -/
def phraseToks (p : String) : Except String (List Tok)
/-- `q` can start inside an occurrence of `p` (or at its start, for `p ≠ q`). -/
def clash (p q : List Tok) : Bool :=
  (List.range p.length).any (fun k => let r := p.drop k; (k != 0 || p != q) && (r.isPrefixOf q || q.isPrefixOf r))
/-- 1.1: the declared phrases' tokens, or the first diagnostic. -/
def decodeFixed (fx : List String) : Except String (List (List Tok))
def fixedOk (fx : List String) : Bool := (decodeFixed fx).isOk
/-- Every occurrence of a declared phrase becomes one `fixed` token (fuel: the length). -/
def group (ps : List (List Tok)) : Nat → List Tok → List Tok
def lex (fx : List String) (s : String) : Except String (List Tok) := do
  let ps ← decodeFixed fx
  let ts ← rawLex (normal s)
  pure (group ps ts.length ts)

/-- 1.3: AP-1 acceptance; the canonical act, or the diagnostic of 10. -/
def check (fx : List String) (name : String) (arity : Nat) (raw : Lean.Json) : Except String String := do
  let act := normal ((raw.getStr?).toOption.getD "")
  let (slots, replaced) := scanSlots act.toList
  let ws := words (String.mk replaced)
  unless act.startsWith "{0} " && slots == (List.range arity).map toString && ws.length ≥ 2 &&
      ws.all (fun w => actWord (dropComma w)) do
    throw s!"InvalidInput: invalid act phrase for {name}"
  unless act.utf8ByteSize ≤ maxActBytes do throw s!"ResourceLimit: act phrase for {name} is over 400 bytes"
  if let some w := ws.find? (fun w => w != "slot" && clauseWords.contains (dropComma w).toLower) then
    throw s!"InvalidInput: act phrase for {name} uses the clause word '{dropComma w}'; write the condition in the rule's guard"
  let ts ← match lex fx act with
    | .ok ts => pure ts
    | .error e => if e == "comma" then throw s!"InvalidInput: act phrase for {name} ends with a comma" else throw e
  match ts.find? (fun t => match t with | .word w => joinWords.contains w.toLower | .comma => true | _ => false) with
  | some (.word w) => throw s!"InvalidInput: act phrase for {name} joins acts with '{w}' outside a fixed phrase"
  | some _ => throw s!"InvalidInput: act phrase for {name} has a comma outside a fixed phrase"
  | none => pure act

inductive Form | right | entitled
  deriving DecidableEq, Repr
def Form.text : Form → String | .right => "has the right" | .entitled => "is entitled"
def Form.ofText? (s : String) : Option Form
def wording (f : Form) (act : String) : String := "{0} " ++ f.text ++ " " ++ act.drop 4
end VE.Acts.Lexical

namespace VE.Norms.Wire
/-- `decodeRegulated` with `acts@0`'s act check, and a plain declaration's `act` and `form` (both or neither). -/
def decodeRegulatedActs (fx : List String) (name : String) (args : List String) (raw : Lean.Json) :
    Except String VE.Norms.Regulated
def decodeRegulatedIn (profiles fx : List String) (name : String) (args : List String) (raw : Lean.Json) :
    Except String VE.Norms.Regulated :=
  if profiles.contains "acts@0" then decodeRegulatedActs fx name args raw else decodeRegulated name args raw
def canonicalActIn (profiles fx : List String) (name : String) (k : Nat) (raw : Lean.Json) : Except String String :=
  if profiles.contains "acts@0" then VE.Acts.Lexical.check fx name k raw else canonicalAct name k raw
end VE.Norms.Wire
```

The bodies of `rawLex`, `phraseToks`, `decodeFixed`, `group`, `Form.ofText?` and `decodeRegulatedActs` are in the stub
(15); the diagnostics they raise are in 10. From AP-3 on, `decodeRegulatedActs` and `canonicalActIn` call
`VE.Acts.Wire.checkAct` (6.4) where they call `check` here.

### 4.3 Theorems

```lean
namespace VE.Acts.Lexical
/-- The independent statement of 1.3. -/
def Accepts (fx : List String) (k : Nat) (raw : Lean.Json) (a : String) : Prop :=
  let ws := words (String.mk (scanSlots a.toList).2)
  a = normal ((raw.getStr?).toOption.getD "") ∧ a.startsWith "{0} " = true ∧
  (scanSlots a.toList).1 = (List.range k).map toString ∧ 2 ≤ ws.length ∧
  (∀ w ∈ ws, actWord (dropComma w) = true) ∧ a.utf8ByteSize ≤ maxActBytes ∧
  (∀ w ∈ ws, w ≠ "slot" → clauseWords.contains (dropComma w).toLower = false) ∧
  ∃ ts, lex fx a = .ok ts ∧ ∀ t ∈ ts, t ≠ .comma ∧ ∀ w, t = .word w → joinWords.contains w.toLower = false

theorem check_spec (fx : List String) (h : fixedOk fx = true) (name : String) (k : Nat) (raw : Lean.Json)
    (a : String) : check fx name k raw = .ok a ↔ Accepts fx k raw a
theorem check_no_join {fx name k raw a} (hc : check fx name k raw = .ok a) {ts : List Tok} (hl : lex fx a = .ok ts) :
    ∀ t ∈ ts, (∀ w, t = .word w → joinWords.contains w.toLower = false) ∧ t ≠ .comma
theorem check_no_clause {fx name k raw a} (hc : check fx name k raw = .ok a) :
    ∀ w ∈ words a, clauseWords.contains w.toLower = false
theorem fixedOk_unique (fx : List String) (h : fixedOk fx = true) (ts : List Tok) :
    -- the grouping is the only one: no two occurrences of declared phrases overlap
    ∀ ps, decodeFixed fx = .ok ps → ∀ i j (hi : i < ps.length) (hj : j < ps.length) (m n : Nat),
      (ps[i]).isPrefixOf (ts.drop m) = true → (ps[j]).isPrefixOf (ts.drop n) = true → (i, m) ≠ (j, n) →
      m + (ps[i]).length ≤ n ∨ n + (ps[j]).length ≤ m
theorem wording_subject_first (f : Form) (act : String) (h : act.startsWith "{0} " = true) :
    (wording f act).startsWith "{0} " = true
end VE.Acts.Lexical

/-! lean/VE/Acts/Compat.lean -/
theorem VE.Acts.Lexical.check_extends (fx : List String) (h : fixedOk fx = true) {name : String} {k : Nat}
    {raw : Lean.Json} {a : String} (hc : VE.Norms.Wire.canonicalAct name k raw = .ok a)
    (hn : ∀ w ∈ VE.Norms.Wire.words a, w.toLower ≠ "nor") : check fx name k raw = .ok a

namespace VE.Norms.Wire
theorem decodeRegulated_without_acts (ps fx : List String) (h : "acts@0" ∉ ps) :
    decodeRegulatedIn ps fx = decodeRegulated
theorem canonicalActIn_without_acts (ps fx : List String) (h : "acts@0" ∉ ps) :
    canonicalActIn ps fx = canonicalAct
/-- Today's decoder never produces an act on a plain predicate, so `Tree.check`'s dropped refusal admits only
    `acts@0` documents. -/
theorem decodeRegulated_plain {name : String} {args : List String} {raw : Lean.Json} {r : VE.Norms.Regulated}
    (h : decodeRegulated name args raw = .ok r) (hp : r.role = .plain) : r.act = none
end VE.Norms.Wire
```

The plan's `check_no_join` and `check_no_clause` used `!… .contains`; here they are stated as `= false` (14, C13).
`check_spec` and `fixedOk_unique` are new; the review may drop `fixedOk_unique` if `group`'s definition is judged clear
enough.

### 4.4 The `acts@0` row of AR-10's profile-gate table

Stated against AR-10's interface as the synthesis writes it (SYNTHESIS 2.2: `ProfileRow`, `profileTable`, `gateOf`,
`routeOf`); it is type-checked when that table lands.

```lean
-- the row
{ profile := "acts@0", requires := ["norms@0"],
  refuses := [("soft-norms@0", "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"),
              ("rights@0", "UnsupportedProfile: acts@0 with rights@0 is not implemented"),
              ("alternatives@0", "UnsupportedProfile: acts@0 with alternatives@0 is not implemented"),
              ("closure@0", "UnsupportedProfile: acts@0 on the closure family is not implemented"),
              ("order@0", "UnsupportedProfile: acts@0 on the order family is not implemented"),
              ("ve.discourse@1", "UnsupportedProfile: acts@0 with ve.discourse@1 is not implemented")],
  slot := "decoder" }    -- a decoding extension of norms@0, like data@0 and definitions@0

-- its composition theorem: acts@0 changes no route
theorem gate_acts (ps : List String) (h : "acts@0" ∈ ps) (r : VE.Compose.Route)
    (hg : VE.Compose.gateOf VE.Compose.profileTable ps = .ok r) :
    VE.Compose.gateOf VE.Compose.profileTable (ps.erase "acts@0") = .ok r ∧
      (r = .norms ∨ r = .normDefaults ∨ r = .readings)
```

The refusals cover every decoder `acts@0` does not hook (finding F2): the soft and rights chains and the alternatives
route decode norms with their own extensions, and the closure and order families use `Plain.decodeRegulatedAll` on the
family route. `speech-acts@0` and `reports@0` already exclude `acts@0` (the speech-acts allowlist; reports refuse
`norms@0`). Python reads the generated table; no `ve/profiles.py` row is written by hand.

## 5. AP-2: Lean statements (the act grammar)

### 5.1 Terminals

```lean
namespace VE.Acts
open Lexical (Tok)

structure Frame where
  head : List String
  markers : List String
  split : List String
  mods : List String
  deriving DecidableEq, Repr
structure Vocab where
  frames : List Frame
  adverbs : List String
  deriving DecidableEq, Repr

inductive Term
  | subj | slot | fixed | comma | never
  | kw (w : String)               -- a word equal to `w`, case-insensitively: heads, markers, to, be, and, or, nor
  | adv (ws : List String)        -- an adverb
  | fill (excl : List String)     -- a filler word: any word whose lower case is not in `excl`
  deriving DecidableEq, Repr
def Term.accepts : Term → Tok → Bool
  | .subj, .slot 0 => true
  | .slot, .slot (_ + 1) => true
  | .fixed, .fixed _ => true
  | .comma, .comma => true
  | .kw w, .word v => v.toLower == w
  | .adv ws, .word v => ws.contains v.toLower
  | .fill ex, .word v => !ex.contains v.toLower
  | _, _ => false
instance : VE.Grammar.Accepts Term Tok := ⟨Term.accepts⟩
```

`never` accepts nothing; it closes nonterminals a vocabulary leaves without rules (5.2, last paragraph).

### 5.2 The rule table

The grammar `grammar V` is generated from `V` by the schema below. In Lean the schema is `schema V : List RuleS` (a
`RuleS` is a left side, a right side over named symbols and a `Kind`, the rule's semantic action), and `build V` numbers
the nonterminals, adds the `never` rules and computes the ranks. `h` ranges over the frames, `m` over a frame's
non-empty argument markers (`m*` over its split markers, `m°` over the others), `μ` over its modifier markers. Each
rule has a **kind** (its semantic action, 5.3); "pass" means the node's value is its children's. Ranks are computed:
a nonterminal's rank is one more than the largest rank of a nonterminal that starts one of its rules, so condition W3
(`Rule.wf`) holds, and every rule's right side is non-empty. Reading the table: `X → Y Z | W` lists rules of `X`;
lower case in quotes are `kw` terminals; `FILLh` is `fill (fillerExcl V h)`; `ADV` is `adv V.adverbs`.

**Start, items and coordinations**

| Nonterminal | Rules | Kind |
|---|---|---|
| `S` | `subj SINGLE` \| `subj COORD` | start |
| `J` | `"and"` \| `"or"` \| `"nor"` | pass |
| `FW` | `"to"` \| `"be"` \| `"to" "be"` | function words |
| `TOK` | `slot` \| `fixed` | pass |
| `ADVO` | `ADV` | prefix adverb, own |
| `ADVSO` | `ADVO` \| `ADVO ADVSO` | pass |
| `E1X` | `ADV` (first) \| `ADV` (all) | prefix adverb, edge: **two derivations** |
| `E1S` | `E1X` \| `E1X E1S` | pass |
| `MK:m` | the words of `m` | pass |
| `SINGLE` | `SC` \| `ADVSO SC` \| `FW SC` \| `ADVSO FW SC` \| `FW ADVSO SC` \| `ADVSO FW ADVSO SC` | single item → act |
| `SC` | `HDh` \| `HDh SMh` (each h) | core |
| `CB`, `CO`, `CL`, `CR` | `HDh`; `HDh OWNMh`; `HDh LFMh`; `HDh RMh` (each h) | core: bare; full, own material; last of a full list; last of a shared-object list |
| `F1S:c` (c ∈ CB, CO) | `c` \| `E1S c` \| `FW c` \| `E1S FW c` \| `FW E1S c` \| `E1S FW E1S c` | item (first item, shared *to*) |
| `LS:c` (c ∈ CB, CO, CL, CR) | `c` \| `ADVSO c` | item (later item, no function word) |
| `F1O:c` (c ∈ CB, CO) | `FW c` \| `E1S FW c` \| `FW ADVSO c` \| `E1S FW ADVSO c` | item (first item, own *to*) |
| `LO:c` (c ∈ CB, CO, CL, CR) | `FW c` \| `ADVSO FW c` \| `FW ADVSO c` \| `ADVSO FW ADVSO c` | item (later item, own function word) |
| `COORD` | for M ∈ {S, O}: `F1M:CB TM:B` (all bare) \| `F1M:CB TM:R` (shared object) \| `F1M:CO TM:F` (full) | coordination (shared = M is S; shared object = the R rule) |
| `TM:B` | `J LM:CB` \| `comma J LM:CB` \| `comma LM:CB TM:B` | pass |
| `TM:R` | `J LM:CR` \| `comma J LM:CR` \| `comma LM:CB TM:R` | pass |
| `TM:F` | `J LM:CL` \| `J LM:CB` \| `comma J LM:CL` \| `comma J LM:CB` \| `comma LM:CO TM:F` | pass |

**Per frame h**

| Nonterminal | Rules | Kind |
|---|---|---|
| `HDh` | the words of the head | head |
| `WRh` | `FILLh` \| `FILLh WRh` | pass |
| `FLh` | `WRh` \| `TOK` | part |
| `PLh`, `PTh` | `FLh PTh`; `J FLh` \| `comma J FLh` \| `comma FLh PTh` | pass |
| `ARh:m` | `MK:m FLh` | argument m |
| `RLh:m`, `RTh:m` | `ARh:m RTh:m`; `J ARh:m` \| `comma J ARh:m` \| `comma ARh:m RTh:m` | pass (marker repeated) |
| `OLh:m` | `MK:m PLh` | pass (marker once) |
| `FSh:m*` / `FNh:m°` | `RLh:m` \| `OLh:m` | list m, split / not split |
| `Oh` (object frames) | `FLh` (argument "") \| `PLh` (list "", not split; only when "" is not split) | argument / list |
| `OSh` (when "" is split) | `PLh` | list "", split |
| `EEh` | `ARh:m` \| `FNh:m°` \| `ADV` (adverb, own) \| `MK:μ FLh` (modifier μ, own) | pass for the first two |
| `ERh`, `NMh`, `ERNh` | `EEh` \| `EEh ERh`; `ARh:m` \| `FNh:m°`; `NMh` \| `EEh ERNh` | pass |
| `OWNMh` | object frames: `Oh` \| `Oh ERh`; others: `ERh` | pass |
| `TEh` | `ADV` (last) \| `ADV` (all) \| `MK:μ FLh` (last) \| `MK:μ FLh` (all) | trailing edge: **two derivations** |
| `TRh` | `TEh` \| `TEh TRh` | pass |
| `LFMh` | object frames: `Oh` \| `Oh ERNh` \| `Oh TRh` \| `Oh ERNh TRh`; others: `ERNh` \| `TRh` \| `ERNh TRh` | pass |
| `REh` / `REth` | as `TEh` / as `TEh` with `TOK` in place of `FLh` | shared-object edge: **two derivations** |
| `REPh` | `REth` \| `REh REPh` | pass |
| `RXh`, `RRh` | `ARh:m` \| `FNh:m°` \| `REh`; `RXh` \| `RXh RRh` | pass |
| `RMh` | object frames: `Oh` \| `Oh RRh` \| `REPh Oh` \| `REPh Oh RRh`; others: `RRh` | pass |
| `SPLh` | `FSh:m*` \| `MGh` | pass |
| `PXh` | `ARh:m` \| `FNh:m°` \| as `TEh` | after a split: arguments shared; modifiers **two derivations** |
| `POh` | `PXh` \| `PXh POh` | pass |
| `SMh` | object frames: `OWNMh` \| `OWNMh SPLh` \| `OWNMh SPLh POh`, and when "" is split also `OSh` \| `OSh POh`; others: `ERh` \| `ERh SPLh` \| `ERh SPLh POh` \| `SPLh` \| `SPLh POh` | pass |
| `MELh` | `ADV` \| `MK:μ FLh` | modifier |
| `MGTh` | `J MELh` \| `comma J MELh` \| `comma MELh MGTh` | pass |
| `MGh` | `MELh MGTh` | joined modifiers |

Every nonterminal that appears on a right side but has no rule (an empty `MELh` when a frame has no modifier markers
and the document no adverbs, for example) gets the rule `X → never`, which derives nothing.

What the table says, in words:

- **A single item** may hold one split construct: a split marker's joined fillers, a joined object of a frame whose
  object is split, or joined modifiers ("directly or through freely chosen representatives"). Arguments after it are
  shared by every part; every modifier after it reads over the **last part or all parts** (two derivations).
- **A coordination** is a list of items joined by one join word, with commas. Either every later item has its own
  function word (`F1O`, `LO`: "to form and to join") or none has (`F1S`, `LS`: "to seek and enjoy"); a mix has no
  derivation. Three patterns, disjoint by which items are bare (head only):
  - **all bare**: no item has material;
  - **shared object**: every item but the last is bare and the last is not; the last item's arguments and object belong
    to every item, and each of its modifiers reads over the **last item or all items**;
  - **full**: every item but the last has material; the last item's trailing modifiers (after its last argument) read
    over the **last item or all items**.
- The first item's adverbs before its head read over the **first item or all items** (`E1X`), when the function
  words are shared or the adverb stands before the first function word; an adverb after the first item's own *to* is
  that item's.
- **No item of a coordination** holds a split construct (one join level).
- **The object** comes right after the head, except in the last item of a shared-object coordination, where it may
  follow modifiers whose last one ends with a slot, a fixed phrase or an adverb (u051's "enjoy in [other countries]
  asylum from persecution").
- Every other element reads over its own item only, one derivation.

So the only places where one token list has several derivations are the five edge rules (`E1X`, `TEh`, `REh`,
`REth`, `PXh`), each a binary choice, and the readings of a phrase are the products of its edge choices (fixtures in
11.2 check this for every pilot phrase).

### 5.3 Meaning

`meaning V : VE.Grammar.Meaning Tok Unit String Act` computes, bottom-up, a list of **pieces** for each node from its
children's pieces and its rule's kind: words for word nodes, a part for `FLh`, an element for an argument, list,
adverb, modifier or modifier group, a core for `HDh …`, an item for a prefixed item, and an act for `SINGLE` and
`COORD`. The two act-building steps are:

- **single item** (`singleAct`): the atom of the item (its function words, head, own arguments and own modifiers);
  with a split construct, one part per list member (the member's argument, or the member's modifier, added to the
  atom), arguments after it added to every part, and each later modifier added to the last part or to all parts as its
  derivation says. Joined by *and* → `all true split`; by *or* → `any false split`; by *nor* → `any true split`, where
  `split` is true for a split marker's list and false for joined modifiers.
- **coordination** (`coordAct shared rnr`): one atom per item; with shared function words, later items take the first
  item's *to* and *be*; the first item's edge adverbs go to the first atom or to all; in a shared-object list the last
  item's arguments go to every atom; edge modifiers go to the last atom or to all. Joined by *and* → `all shared false`;
  by *or* / *nor* → `any nor false`.

The meaning is refused (the derivation has no meaning) unless every atom fits its frame (`atomOk`): the head is
declared; the object is present exactly when the frame lists `""`; every argument marker is the frame's; every
modifier marker is one of the frame's modifier markers; every adverb is declared. A join has at least two atoms. The
full definitions (`Piece`, `applyKind`, `piecesOf`, `singleAct`, `coordAct`) are in the stub.

### 5.4 Readings, reading and analysis

```lean
inductive Join | and | or | nor  deriving DecidableEq, Repr
inductive Part | slot (i : Nat) | fixed (i : Nat) | words (ws : List String)  deriving DecidableEq, Repr
inductive Filler | one (p : Part) | joined (j : Join) (ps : List Part)  deriving DecidableEq, Repr
inductive Modifier | adv (w : String) | prep (m : String) (p : Part)  deriving DecidableEq, Repr
structure Atom where
  toWord : Bool
  beWord : Bool
  head : List String
  args : List (String × Filler)
  mods : List Modifier
  deriving DecidableEq, Repr
inductive Act
  | one (a : Atom)
  | all (shared split : Bool) (parts : List Atom)
  | any (nor split : Bool) (parts : List Atom)
  deriving DecidableEq, Repr

def framesOk (V : Vocab) : Bool                         -- 1.4
def grammar (V : Vocab) : VE.Grammar.Grammar Term       -- 5.2
def meaning (V : Vocab) : VE.Grammar.Meaning Tok Unit String Act   -- 5.3
def atomOk (V : Vocab) (a : Atom) : Bool

def rawCap : Nat := 256          -- provisional: AP-0 measures it
def stepBudget : Nat := 2100000  -- provisional: AP-0 measures it
def maxReadings : Nat := 64

inductive Listing (α : Type) | ok (xs : List α) | limit
/-- First occurrences, in order. -/
def firsts {α : Type} [DecidableEq α] : List α → List α
  | [] => []
  | x :: xs => x :: (firsts xs).filter (· ≠ x)
/-- From a parse (`none`: step budget exhausted) and a meaning: the distinct meanings, or `limit`. -/
def listing {α : Type} [DecidableEq α] (N L : Nat) (parsed : Option (List (VE.Grammar.Tree Tok)))
    (μ : VE.Grammar.Tree Tok → Option α) : Listing α :=
  match parsed with
  | none => .limit
  | some ts => if N ≤ ts.length then .limit else
      let ms := firsts (ts.filterMap μ)
      if L < ms.length then .limit else .ok ms
def readings (V : Vocab) (N b : Nat) (ts : Array Tok) : Listing Act :=
  listing N maxReadings (VE.Grammar.parse (grammar V) N b ts)
    (fun t => match meaning V () t with | .ok (A, _, _) => some A | .error _ => none)

inductive ReadOutcome | ok (A : Act) | none | many (A B : Act) | limit
def read (V : Vocab) (N b : Nat) (ts : Array Tok) : ReadOutcome :=
  match readings V N b ts with
  | .limit => .limit
  | .ok [] => .none
  | .ok [A] => .ok A
  | .ok (A :: B :: _) => .many A B
/-- For AP-5 only: a simple act exactly when the phrase has one meaning and it is `one`; it renames nothing. -/
def analyse (V : Vocab) (N b : Nat) (ts : Array Tok) : Option Atom :=
  match read V N b ts with
  | .ok (.one a) => some a
  | _ => none
```

### 5.5 Rendering

The **normal form** of an atom, `Atom.normal`, is the token list `{0}`, *to* if `toWord`, *be* if `beWord`, its adverbs,
its head, its object, its other arguments in their order (marker words, then the filler; a joined filler as
`A, B or C` after its marker once), then its prepositional modifiers. `Atom.canon` reorders an atom as the normal form
reads back: object first, adverbs before prepositional modifiers. The **rendering** of an atom is its normal form as
text: tokens separated by spaces, a comma attached to the token before it, a fixed phrase as declared (canonical).
`normalOk V a` is `atomOk V a` plus: every words part is non-empty and made of the frame's filler words, and no joined
filler sits under a split marker or as a split object.

### 5.6 Theorems

```lean
/-- A meaning of the token list: some derivation means `A`. -/
def Derived (V : Vocab) (ts : List Tok) (A : Act) : Prop :=
  ∃ d, VE.Grammar.Derives (grammar V) (.n (grammar V).start) ts d ∧ ∃ c, meaning V () d = .ok (A, c, ())

theorem grammar_wf (V : Vocab) (h : framesOk V = true) : (grammar V).wf = true
/-- One meaning (design debate): some derivation means `A`, and every derivation that has a meaning means `A`. -/
theorem read_unique (V : Vocab) (h : framesOk V = true) {N b : Nat} {ts : Array Tok} {A : Act}
    (hr : read V N b ts = .ok A) :
    Derived V ts.toList A ∧ ∀ d B c, VE.Grammar.Derives (grammar V) (.n (grammar V).start) ts.toList d →
      meaning V () d = .ok (B, c, ()) → B = A
theorem read_none (V : Vocab) (h : framesOk V = true) {N b ts} (hr : read V N b ts = .none) :
    ∀ A, ¬ Derived V ts.toList A
theorem read_many (V : Vocab) (h : framesOk V = true) {N b ts A B} (hr : read V N b ts = .many A B) :
    A ≠ B ∧ Derived V ts.toList A ∧ Derived V ts.toList B
/-- Complete enumeration: no length hypothesis, because `.ok` already means fewer than `N` raw derivations. -/
theorem readings_exact (V : Vocab) (h : framesOk V = true) {N b : Nat} {ts : Array Tok} {As : List Act}
    (hp : readings V N b ts = .ok As) (A : Act) : A ∈ As ↔ Derived V ts.toList A
theorem readings_nodup (V : Vocab) {N b ts As} (hp : readings V N b ts = .ok As) : As.Nodup
/-- The limit outcome, exactly: an exhausted step budget, a saturated parse, or more than 64 meanings. -/
theorem readings_limit (V : Vocab) (N b : Nat) (ts : Array Tok) :
    readings V N b ts = .limit ↔
      (VE.Grammar.parse (grammar V) N b ts = none ∨
       ∃ trees, VE.Grammar.parse (grammar V) N b ts = some trees ∧
         (N ≤ trees.length ∨ maxReadings < (firsts (trees.filterMap (fun t => match meaning V () t with
            | .ok (A, _, _) => some A | .error _ => none))).length))
/-- The generic listing, for the boundary fixtures (N−1 and N raw trees; 63, 64 and 65 meanings). -/
theorem listing_ok {α : Type} [DecidableEq α] (N L : Nat) (parsed : Option (List (VE.Grammar.Tree Tok)))
    (μ : VE.Grammar.Tree Tok → Option α) (xs : List α) :
    listing N L parsed μ = .ok xs ↔
      ∃ ts, parsed = some ts ∧ ts.length < N ∧ xs = firsts (ts.filterMap μ) ∧ xs.length ≤ L
/-- Render round trip: the normal form reads back with one meaning, the atom in canonical order. -/
theorem read_normal (V : Vocab) (h : framesOk V = true) (a : Atom) (ha : normalOk V a = true) :
    ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read V N b a.normal.toArray = .ok (.one a.canon)
theorem analyse_one (V : Vocab) {N b ts a} (h : analyse V N b ts = some a) : read V N b ts = .ok (.one a)
```

These replace the plan's `read_one`, `readings_exact` with a length hypothesis on the deduplicated list, and
`reads_lexical` (14, C5, C6; plan G1–G3, G6).

## 6. AP-3: Lean statements (the table and elaboration)

### 6.1 Ops

```lean
inductive Op | must | needNot | may | mustNot | right  deriving DecidableEq, Repr
def opOf (r : VE.Norms.Regulated) (sign : Bool) : Option Op :=
  match r.role, sign with
  | .obligation, true => some .must
  | .obligation, false => some .needNot
  | .permission, true => some .may
  | .permission, false => some .mustNot
  | .plain, true => some .right
  | .plain, false => none
```

### 6.2 The table and paraphrases

```lean
inductive Simple | atom (a : Atom) | whole (A : Act)  deriving DecidableEq, Repr

/-- *may* and *has the right to*. -/
def freeTable : Act → List (List Simple)
  | .one a => [[.atom a]]
  | .all false _ ps => [ps.map Simple.atom]                                  -- own "to": split
  | .all true true ps => [ps.map Simple.atom]                                -- split marker: each
  | .all true false ps => [ps.map Simple.atom, [.whole (.all true false ps)]]  -- each, or both together
  | .any true _ _ => []                                                      -- nor: refused
  | .any false true ps => [ps.map Simple.atom]                               -- split marker: each
  | .any false false ps => [ps.map Simple.atom, [.whole (.any false false ps)]] -- free choice, or one act

/-- The plan's 2.3, for the five deontic modals only (never `intends` or `believes`). -/
def table : Op → Act → List (List Simple)
  | _, .one a => [[.atom a]]
  | .needNot, _ => []
  | .must, .all _ _ ps => [ps.map Simple.atom]
  | .must, .any nor sp ps => if nor || sp then [] else [[.whole (.any nor sp ps)]]
  | .mustNot, .any _ _ ps => [ps.map Simple.atom]
  | .mustNot, .all s sp ps => if sp then [ps.map Simple.atom] else [ps.map Simple.atom, [.whole (.all s sp ps)]]
  | .may, A => freeTable A
  | .right, A => freeTable A

def paraphrase (fx : List String) (phrase : String) (op : Op) (f : Option Lexical.Form) : List Simple → String
```

The table's equations, each a theorem (all by case analysis):

```lean
theorem table_one (op : Op) (a : Atom) : table op (.one a) = [[.atom a]]
theorem table_must_all (s sp : Bool) (ps : List Atom) : table .must (.all s sp ps) = [ps.map Simple.atom]
theorem table_must_any (ps : List Atom) : table .must (.any false false ps) = [[.whole (.any false false ps)]]
theorem table_must_any_refused (n sp : Bool) (ps : List Atom) (h : n = true ∨ sp = true) :
    table .must (.any n sp ps) = []
theorem table_mustNot_any (n sp : Bool) (ps : List Atom) : table .mustNot (.any n sp ps) = [ps.map Simple.atom]
theorem table_mustNot_all (s : Bool) (ps : List Atom) :
    table .mustNot (.all s false ps) = [ps.map Simple.atom, [.whole (.all s false ps)]]
theorem table_mustNot_all_split (s : Bool) (ps : List Atom) : table .mustNot (.all s true ps) = [ps.map Simple.atom]
theorem table_free_all_own (op : Op) (hop : op = .may ∨ op = .right) (sp : Bool) (ps : List Atom) :
    table op (.all false sp ps) = [ps.map Simple.atom]
theorem table_free_all_shared (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.all true false ps) = [ps.map Simple.atom, [.whole (.all true false ps)]]
theorem table_free_all_split (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.all true true ps) = [ps.map Simple.atom]
theorem table_free_any (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.any false false ps) = [ps.map Simple.atom, [.whole (.any false false ps)]]
theorem table_free_any_split (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.any false true ps) = [ps.map Simple.atom]
theorem table_free_nor (op : Op) (hop : op = .may ∨ op = .right) (sp : Bool) (ps : List Atom) :
    table op (.any true sp ps) = []
theorem table_needNot (A : Act) (h : ∀ a, A ≠ .one a) : table .needNot A = []
```

They stay provisional until AP-7 passes (D3).

### 6.3 Elaboration

```lean
structure ActsDoc where
  U : VE.NormDefaults.UDoc
  V : Vocab
  fixed : List String
  acts : List (String × Act)      -- each joined act's predicate and its one meaning (from `read`)

structure SplitMap where
  preds : List (String × String × Nat)   -- generated `p__i`, its source predicate, i
  rules : List (String × String × Nat)   -- generated `<rule>-a<i>`, its source rule, i
  deriving DecidableEq, Repr

def partPred (p : String) (i : Nat) : String := p ++ "__" ++ toString i
def partRule (n : String) (i : Nat) : String := n ++ "-a" ++ toString i
/-- An obligation's permission dual, or the obligation a permission is the dual of. -/
def dualOf (T : VE.Norms.Tree) (p : String) : Option String
/-- The one reading of a predicate's act: `[[atom a]]` for `one a`; for a join, every rule on `p` and on its dual has
    exactly one reading by the table, and all are equal. -/
def readingOf (D : ActsDoc) (p : String) (A : Act) : Except String (List Simple)
/-- AP-3: split every predicate whose reading has two or more atoms; refuse a formula naming a split predicate;
    check the generated names; backstop: the result is `WellFormedU`. -/
def elaborateMap (D : ActsDoc) : Except String (VE.NormDefaults.UDoc × SplitMap)
def elaborate (D : ActsDoc) : Except String VE.NormDefaults.UDoc := (elaborateMap D).map (·.1)
```

`elaborateMap` builds the result as follows; every other field is unchanged (6.5 is the full table):

- `E.predicates`: each part `p__i` has `p`'s sorts; a split `p` is undeclared;
- `T.regulated`: each split `r` becomes `r__1 … r__n`, with `act := some (rendering of atom i)` and
  `permission := r.permission.map (· ++ "__" ++ i)`;
- `T.nodes`: each rule `N` on a split `p` becomes `N-a1 … N-an` on the parts, `over := N.over.map (partRule · i)`, in
  source order, parts in index order;
- `unspec`: a split `p` is replaced by its parts.

It refuses (10): a joined act with no rule; a rule with no op, or with zero or two readings; a predicate whose rules or
dual rules read its act differently; a guard, exception or definition naming a split predicate; a part name already
declared or over 64 bytes; a part rule name already used or not a rule name (`ruleName`: at most 64 bytes); and any
result that is not `WellFormedU`.

### 6.4 The decoder after AP-3

```lean
/-- The act check under `acts@0` from AP-3 on: a lexical act (`Lexical.check`), or a joined act: every condition of
    1.3 except 6, every slot standing alone as a word, and exactly one meaning (`read V rawCap stepBudget`). Returns
    the canonical act and, for a joined act, its act tree. -/
def VE.Acts.Wire.checkAct (fx : List String) (V : Vocab) (name : String) (arity : Nat) (raw : Lean.Json) :
    Except String (String × Option Act)
theorem VE.Acts.Wire.checkAct_lexical (fx V name k raw a) (h : Lexical.check fx name k raw = .ok a) :
    VE.Acts.Wire.checkAct fx V name k raw = .ok (a, none)
theorem VE.Acts.Wire.checkAct_joined (fx V name k raw a A) (h : VE.Acts.Wire.checkAct fx V name k raw = .ok (a, some A)) :
    ∃ ts, Lexical.lex fx a = .ok ts ∧ read V rawCap stepBudget ts.toArray = .ok A
```

`checkAct_lexical` is the formal form of "an act AP-1 accepts never enters the grammar" (2.5 of the plan).

### 6.5 Every place a split predicate can be named (the reference table)

| Field | Treatment |
|---|---|
| `Doc.E` (`predicates`) | `p` undeclared; `p__i` declared with `p`'s sorts; sorts and constants unchanged |
| `Doc.lits` | unchanged |
| `Tree.regulated` | `p` replaced by `p__1 … p__n` |
| `Regulated.name` / `sorts` / `allowByDefault` / `role` | `p__i` / same / same / same |
| `Regulated.act` | the rendering of atom i |
| `Regulated.permission` | `m__i` when the dual `m` splits with the same reading (guaranteed by `readingOf`); otherwise refused |
| `Tree.pairs` (derived) | follows `permission` |
| `Tree.definitions` (`name`, `args`) | unchanged |
| `Definition.body` | naming `p`: refused, "name one of its parts" |
| `Tree.nodes` | a rule on `p` replaced by its parts; others unchanged |
| `Node.name` / `pred` / `sign` | `N-ai` / `p__i` / same |
| `Node.guard`, `Node.carveOuts` | same; naming a split predicate anywhere: refused, "name one of its parts" |
| `Node.over` | each entry `m` becomes `m-ai` (precedence stays within one predicate, so `m` is on `p` too) |
| `UDoc.unspec` | `p` replaced by `p__1 … p__n` |
| W2 norm units on `p` | elaborated like any rule on `p` |
| `readings@1` candidates (AP-4) | a candidate's rule on `p` is elaborated like any rule on `p` |
| models, `data@0` facts, questions and queries (Python inputs) | naming `p`: refused, "name one of its parts" |
| conflict witnesses and certificates | computed on the relayed elaborated document (its targets name parts) |
| `actChecks` identity | checked on the parts: two parts of one predicate with equal renderings are refused |

A test (`tests/test_acts_elaborate.py::test_reference_table_complete`) enumerates the fields of `Node`, `Regulated`,
`Definition`, `Tree`, `Doc` and `UDoc` from the Lean structures (via `#print` output recorded as a fixture) and fails on
any field this table leaves out.

### 6.6 Theorems

```lean
universe u
/-- `S` with `p` read as `q`. -/
def readAs (p q : String) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs => if r = p then S.relation q vs else S.relation r vs }
/-- The names a source predicate stands for after elaboration: its parts, or itself. -/
def partNames (D : ActsDoc) (p : String) : List String
/-- The source's meaning per the table: part i of `p` means what the source rules on `p` mean, read of `p__i`. -/
def IntendedActs (D : ActsDoc) (S : VE.Structure.{u}) : Prop :=
  ∀ r ∈ D.U.D.T.regulated, ∀ q ∈ partNames D r.name, VE.Norms.IntendedAt D.U.D.T r (readAs r.name q S)

theorem elaborateMap_fst (D : ActsDoc) : (elaborateMap D).map (·.1) = elaborate D
theorem splitMap_exact (D : ActsDoc) {U' : VE.NormDefaults.UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∀ q, (q ∈ U'.D.T.regulated.map (·.name) ∧ q ∉ D.U.D.T.regulated.map (·.name)) ↔ ∃ p i, (q, p, i) ∈ M.preds) ∧
    (∀ n, (n ∈ U'.D.T.nodes.map (·.name) ∧ n ∉ D.U.D.T.nodes.map (·.name)) ↔ ∃ m i, (n, m, i) ∈ M.rules) ∧
    (∀ q p i, (q, p, i) ∈ M.preds →
      q = partPred p i ∧ p ∈ D.U.D.T.regulated.map (·.name) ∧ p ∉ U'.D.T.regulated.map (·.name) ∧ 1 ≤ i) ∧
    (∀ n m i, (n, m, i) ∈ M.rules →
      n = partRule m i ∧ m ∈ D.U.D.T.nodes.map (·.name) ∧ m ∉ U'.D.T.nodes.map (·.name) ∧ 1 ≤ i) ∧
    (∀ q p i j, (q, p, i) ∈ M.preds → 1 ≤ j → j ≤ i → ∃ q', (q', p, j) ∈ M.preds) ∧
    (M.preds.map (·.1)).Nodup ∧ (M.rules.map (·.1)).Nodup
theorem elaborate_identity (D : ActsDoc) (h : ∀ p A, (p, A) ∈ D.acts → ∃ a, A = .one a)
    (h0 : VE.NormDefaults.WellFormedU D.U = true) : elaborate D = .ok D.U
theorem elaborate_wellFormed (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    VE.NormDefaults.WellFormedU U' = true
theorem elaborate_one_reading (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    ∀ p A, (p, A) ∈ D.acts → (∃ a, A = .one a) ∨ ∃ R, readingOf D p A = .ok R ∧
      ∀ N ∈ D.U.D.T.nodes, (N.pred = p ∨ some N.pred = dualOf D.U.D.T p) →
        ∃ r op, D.U.D.T.regulated.find? (·.name == N.pred) = some r ∧ opOf r N.sign = some op ∧ table op A = [R]
theorem elaborate_unspec (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    U'.unspec = D.U.unspec.flatMap (partNames D)
/-- Faithfulness: the elaborated document's intended reading is the table's reading of the source. -/
theorem elaborate_faithful (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U')
    (S : VE.Structure.{u}) : VE.Norms.holdsCatala U'.D.T S ↔ IntendedActs D S
```

`elaborate_one_reading`'s first disjunct covers a `one` act, which `readingOf` reads without the table, so a `one`
act under a rule with no op (plain, sign false) is not refused. `norm-defaults@0`'s fill is applied to `U'` as to any `UDoc`, so the
parts of an unspecified predicate each get their own gap (`elaborate_unspec`).

### 6.7 The `acts-elaborate` relay

A case kind `acts-elaborate` of the existing `norms` and `norm-defaults` modes (14, C18), answered by
`VE.Acts.Run.runElaborate` (one runner for both). The request is the mode's usual case (environment and norm
objects). The row:

| Member | Shape |
|---|---|
| `id`, `status` | as every row |
| `environment_id` | `hex64` |
| `verdict` | `"ELABORATED"` or `"REFUSED"` |
| `diagnostic` | text; only with `REFUSED` |
| `predicates` | array of `{name, source, index, sorts, role, default, act, permission}`, one per part; `default` ∈ `allow`, `deny`, `unspecified` |
| `rules` | array of `{name, source, index, pred, sign, guard, unless, over}`, one per part rule; `guard` and `unless` in the generated-formula shape |
| `kept` | the source predicates with joined acts that did not split (one simple act) |

Recipe obligations (CLAUDE.md, "a relayed Lean route"):

1. `lean/ResponseShape/Schemas/Norms.lean` and `NormDefaults.lean` gain the `acts-elaborate` row shape;
2. `lean/ResponseShape/Encoders/Norms.lean` and `NormDefaults.lean` prove `runElaborate_fits`, listed in
   `lean/ResponseShape/Audit.lean`;
3. the schemas regenerate (`tools/response_schemas.py --write`);
4. `ve/norms.py` binds the row (R8): every `source` names a predicate or rule of the request; for each source the
   indices are exactly 1 to n; each part rule's `sign`, `guard` and `unless` equal its source rule's and its `over` is
   the source's mapped by index; each part's `sorts`, `role` and `default` equal its source's; no row is empty or
   extra; no generated name is declared in the request; every split source is absent from the relayed document;
5. route cases recorded from the suite; `tests/test_acts_elaborate_answer.py` mutates genuine answers one and two
   faults at a time (each member dropped, emptied, retyped, duplicated or reordered; an index pushed out of range; a
   source renamed): every mutant is `CheckerUnavailable` or changes nothing the relay shows.

Python's conflict-witness search and prover then run on the relayed document; `_lean_route` is true for `acts@0`
documents, and the retained Python path refuses them.

## 7. AP-4: Lean statements (readings from derivations, exact sets)

```lean
/-- 2.4: a rule that attaches a modifier beyond its own item does so at an edge: `first` only in the first item's
    prefix (`E1X`), `last` and `all` only in trailing positions (`TE`, `RE`, `REt`, `PX`). -/
def attachOf : Kind → Option Attach
def edgeLhs (x : String) : Attach → Bool
theorem modifier_edges (V : Vocab) : ∀ r ∈ schema V, ∀ a, attachOf r.kind = some a → edgeLhs r.lhs a = true

def phraseReadings (V : Vocab) (op : Op) (N b : Nat) (ts : Array Tok) : Listing (List Simple) :=
  match readings V N b ts with
  | .limit => .limit
  | .ok As =>
    let Rs := firsts (As.flatMap (table op))
    if maxReadings < Rs.length then .limit else .ok Rs
/-- Characterised by the grammar's derivations, not by a possibly truncated list. -/
theorem phraseReadings_exact (V : Vocab) (h : framesOk V = true) {op : Op} {N b : Nat} {ts : Array Tok}
    {Rs : List (List Simple)} (hp : phraseReadings V op N b ts = .ok Rs) (R : List Simple) :
    R ∈ Rs ↔ ∃ A, Derived V ts.toList A ∧ R ∈ table op A

structure Source where
  phrase : String
  role : VE.Norms.Role
  sign : Bool
  form : Option Lexical.Form
  template : VE.Norms.Node        -- guard, carve-outs and precedence every reading keeps; `name` and `pred` unused
  allow : Bool                    -- the completion every part keeps
  units : List String             -- fixed units every reading shares (u105a)
  sets : List String

/-- What a rule says, for comparison: its predicate's act, role and completion; its sign, guard, carve-outs, over. -/
abbrev View := String × VE.Norms.Role × Bool × VE.Formula × List VE.Formula × List String × Bool
def ruleView (D : VE.Readings.Doc) (N : VE.SoftNorms.SoftNode) : Option View
def expected (fx : List String) (s : Source) (x : Simple) : View
def choicesOn (D : VE.Readings.Doc) (sets : List String) : List (List (String × Nat)) :=
  firsts ((VE.Readings.choices D).map (fun c => c.filter (fun x => sets.contains x.1)))
def choiceRules (D : VE.Readings.Doc) (s : Source) (c : List (String × Nat)) : List VE.SoftNorms.SoftNode
def opOfSource (s : Source) : Option Op
def sourceCheck (D : VE.Readings.Doc) (V : Vocab) (fx : List String) (N b : Nat) (s : Source) : Except String Unit

def SourceExact (D : VE.Readings.Doc) (V : Vocab) (fx : List String) (N b : Nat) (s : Source) : Prop :=
  ∃ ts op Rs, Lexical.lex fx s.phrase = .ok ts ∧ opOfSource s = some op ∧
    phraseReadings V op N b ts.toArray = .ok Rs ∧
    (∀ R, R ∈ Rs ↔ ∃ A, Derived V ts A ∧ R ∈ table op A) ∧
    ((choicesOn D s.sets).map (fun c => (choiceRules D s c).map (ruleView D))).Nodup ∧
    List.Perm ((choicesOn D s.sets).map (fun c => (choiceRules D s c).map (ruleView D)))
      (Rs.map (fun R => R.map (fun x => some (expected fx s x))))
/-- Exactness: a bijection between the phrase's readings, complete against the grammar, and the listed choices;
    each choice's rules regulate exactly its reading's simple acts with the template's sign, guard, carve-outs,
    precedence, role and completion. -/
theorem sourceCheck_exact (D V fx N b s) (h : framesOk V = true) (hc : sourceCheck D V fx N b s = .ok ()) :
    SourceExact D V fx N b s
theorem sourceCheck_complete (D V fx N b s) (h : framesOk V = true) (he : SourceExact D V fx N b s) :
    sourceCheck D V fx N b s = .ok ()

/-- A separating situation built from simple acts, checked by `VE.Readings.separates` (no new soundness theorem). -/
def atomSituation (D : VE.Readings.Doc) (s : String) (i j : Nat) : VE.Readings.Situation Nat
```

`List.Perm` with the `Nodup` conjunct is the bijection: each reading has exactly one choice and each choice is a
reading. `expected` renders an atom (5.5) or, for a whole join, the source phrase's canonical act. On the
norm-defaults readings route the completion compared is `deny`, `allow` or `unspecified`.

**The `act-readings` mode** (AP-4; registered through AR-10's mode registry; the relayed-route recipe): request
`{phrase, fixed, frames, adverbs, role, sign, form}`; row `{id, status, verdict ∈ {LISTED, LIMIT, REFUSED}, readings:
[{acts: [{act, text}], paraphrase}], diagnostic}`. Binding: `readings` non-empty with `LISTED`; at most 64; each `act`
lexes under the request's `fixed`; fuzz as in 6.7.

## 8. AP-5: Lean statements (specialisation; used only after AP-5b)

```lean
structure Restrictive where
  markers : List String
  adverbs : List String
  deriving DecidableEq, Repr
def Modifier.restrictive (ρ : Restrictive) : Modifier → Bool
  | .adv w => ρ.adverbs.contains w
  | .prep m _ => ρ.markers.contains m
/-- `a ⊑ b`: same function words and head; every argument and modifier of `b` is one of `a`; every argument or
    modifier `a` has beyond `b` is restrictive. -/
def specialises (ρ : Restrictive) (a b : Atom) : Bool :=
  a.toWord == b.toWord && a.beWord == b.beWord && a.head == b.head &&
  b.args.all (a.args.contains ·) && b.mods.all (a.mods.contains ·) &&
  (a.args.filter (fun x => !b.args.contains x)).all (fun x => ρ.markers.contains x.1) &&
  (a.mods.filter (fun x => !b.mods.contains x)).all (Modifier.restrictive ρ)
theorem specialises_refl (ρ : Restrictive) (a : Atom) : specialises ρ a a = true
theorem specialises_trans {ρ : Restrictive} {a b c : Atom} :
    specialises ρ a b = true → specialises ρ b c = true → specialises ρ a c = true

/-- One premise `∀ x̄. p_a x̄ → p_b x̄` per ordered pair of declared simple acts of one permission or obligation role,
    equal sorts, `a ⊑ b`, `a ≠ b`. -/
def specPremises (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)) : List VE.Formula
theorem specPremises_typed (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom))
    (h : VE.Norms.WellFormed E = true) : ∀ φ ∈ specPremises E ρ acts, φ.check E.E [] = true
theorem specPremises_plain (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)) :
    ∀ r ∈ E.T.regulated, r.role = .plain → ∀ φ ∈ specPremises E ρ acts, r.name ∉ VE.Norms.preds φ
```

`acts` is built from `analyse` on each declared act and from the parts of a split; `analyse` renames nothing.

**AP-5b obligations** (design and review; not reviewed here). A separate statement review fixes them. They must:
(a) state `act-specialise@0`'s meaning over base predicates, by substituting each regulated predicate's completed
outcome formula (`VE.Norms.outcome`) in the premises; (b) prove that substitution sound under the intended reading
(`IntendedAt` gives `p ↔ outcome`); (c) prove that conflict-freedom with the premises is not vacuous: the base
premises with the substituted specialisation premises have a model. Only then may specialisation become PK-1's last
pack.

## 9. AP-6: experiment statements (not for build review)

Route (a) reifies an act with two or more bound non-subject slots as an event sort of `events@0`, with its participant
roles added to that sort as role predicates; `reify_faithful (D) (S) (hc : OneEventPerTuple D S) : holdsCatala (reify
D).T S ↔ NaryIntended D S` over those event sorts and roles. Route (b) lifts regulated arity to 6 over `VE.Core`. Both
wait for `lean-first/b14c`, route (a) also for ET-3; the experiment states them exactly when it starts.

## 10. Diagnostics

Every text is Lean's; Python relays it. "D-n" numbers the rows for the fixtures.

| # | Code and text | Raised by |
|---|---|---|
| D-1 | `InvalidInput: invalid act phrase for {name}` | `check` 1.3 conditions 1–3 (today's text, unchanged) |
| D-2 | `ResourceLimit: act phrase for {name} is over 400 bytes` | `check` |
| D-3 | `InvalidInput: act phrase for {name} uses the clause word '{w}'; write the condition in the rule's guard` | `check`, `checkAct` |
| D-4 | `InvalidInput: act phrase for {name} joins acts with '{w}' outside a fixed phrase` | `check` (AP-1 only; from AP-3 such an act goes to the grammar) |
| D-5 | `InvalidInput: act phrase for {name} has a comma outside a fixed phrase` | `check` (AP-1 only) |
| D-6 | `InvalidInput: act phrase for {name} ends with a comma` | `check`, `checkAct` |
| D-7 | `ResourceLimit: more than 128 fixed phrases` | `decodeFixed` |
| D-8 | `ResourceLimit: fixed phrase '{p}' is over 300 bytes` | `phraseToks` |
| D-9 | `InvalidInput: fixed phrase '{p}' has a comma that does not follow a word` | `phraseToks` |
| D-10 | `InvalidInput: fixed phrase '{p}' holds a slot` | `phraseToks` |
| D-11 | `InvalidInput: fixed phrase '{p}' has '{w}', which is not a word of letters` | `phraseToks` |
| D-12 | `InvalidInput: fixed phrase '{p}' uses the clause word '{w}'` | `phraseToks` |
| D-13 | `InvalidInput: fixed phrase '{p}' must hold two words or more` / `… must begin and end with a word other than and, or, nor and for` | `phraseToks` |
| D-14 | `InvalidInput: fixed phrase '{p}' is declared twice` / `InvalidInput: fixed phrases '{p}' and '{q}' overlap, or one holds the other` | `decodeFixed` |
| D-15 | `InvalidInput: act phrase for {name} has more than one reading: 1. … 2. …` (paraphrases, 2.2) | `checkAct` (`read` → `many`) |
| D-16 | `InvalidInput: act phrase for {name} has no reading under the declared frames` | `checkAct` (`read` → `none`) |
| D-17 | `ResourceLimit: act phrase for {name} has too many readings to list; split the sentence` | `checkAct`, `phraseReadings` users (`limit`) |
| D-18 | `InvalidInput: act phrase for {name} has a slot joined to a word` | `checkAct` |
| D-19 | `InvalidInput: a plain act for {name} needs its form, and a form needs its act` / `InvalidInput: invalid form for {name}` | `decodeRegulatedActs` |
| D-20 | `InvalidInput: the joined act of {p} has no rule to read it by` | `readingOf` |
| D-21 | `InvalidInput: rule {r} has no modal word for a joined act` | `readingOf` (plain, sign false) |
| D-22 | `InvalidInput: rule {r} has no reading of its act; rewrite it` | `readingOf` (table `[]`: *need not*, *nor* under *must*, *may* or *has the right to*, a split marker's *or* under *must*) |
| D-23 | `InvalidInput: rule {r} has more than one reading: 1. … 2. …` | `readingOf` |
| D-24 | `InvalidInput: the rules on {p} and its dual read its act differently; write the parts as separate predicates` | `readingOf` |
| D-25 | `InvalidInput: rule {r} names a predicate that is split into parts; name one of its parts` / the same for a definition | `elaborateMap` |
| D-26 | `InvalidInput: the part name {q} is already declared` / `ResourceLimit: the part name {q} is over 64 bytes` / `InvalidInput: the part rule name {n} is already used` / `ResourceLimit: the part rule name {n} is not a rule name of at most 64 bytes` | `elaborateMap` |
| D-27 | `InvalidInput: two parts of {p} are the same act` | `elaborateMap` (via `actChecks`'s duplicate) |
| D-28 | `name one of its parts: {p} is split into {p__1}, …` | Python binding of models, data and questions (relayed text from the elaborated document's map) |
| D-29 | `InvalidInput: the reading sets give {k} choices for a phrase with {n} readings` / `… a reading of the source phrase has no choice: {paraphrase}` / `… a choice is not a reading of the source phrase, or changes the source rule's modal, guard, exceptions, precedence or completion` / `… two choices give the same reading` | `sourceCheck` |
| D-30 | `UnsupportedProfile: acts@0 …` (4.4) | AR-10's row |
| D-31 | the frame diagnostics of `decodeVocab`: one text per `framesOk` condition, `InvalidInput: frame '{head}' …` | `VE.Acts.Wire.decodeVocab` |

Rows D-3, D-15 to D-17 and D-22 are refusals of authored text; they also go into english-lean's catalogue as rows if
it holds refusals by then (plan S7).

## 11. Acceptance fixtures

Bytes are UTF-8 bytes of the canonical act. "Raw" is the number of derivations `parse (grammar V) rawCap stepBudget`
returns; "readings" is `readings`; "phrase readings" is `phraseReadings` under the rule's op. Every number and every
diagnostic text below is computed by a `#guard` in the stub (section 15); the column headings still say *hand* where
the number was first derived by hand and then confirmed. In act phrases, `[...]` marks a declared fixed phrase (not
part of the string).

### 11.1 AP-1 (lexical acts, fixed phrases, wordings)

| # | Unit | Act phrase; declarations | Expected (*hand*) |
|---|---|---|---|
| A1 | u039 | `{0} in full equality to [a fair and public hearing by an independent and impartial tribunal] in {1}`, arity 2, form `is entitled` | accepted, 97 B (over today's 80), 8 tokens; fixed phrase 66 B; wording `{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}`, 109 B |
| A2 | u085 | `{0} to [equal pay for equal work] without any discrimination`, arity 1, form `has the right` | accepted, 58 B, 6 tokens; wording `{0} has the right to equal pay for equal work without any discrimination`, 72 B |
| A3 | u106 | `{0} to the protection of [the moral and material interests] resulting from {1}`, arity 2 | accepted, 76 B, 9 tokens |
| A4 | u051 (today's wording) | `{0} to seek as well as enjoy in other countries asylum from persecution` | `canonicalAct` and `check` both accept it, with the same 71 B string (`check_extends`); `checkAct` returns `(a, none)`: it never enters the grammar |
| A5 | u051 (source) | `{0} to seek and to enjoy in other countries asylum from persecution`, no fixed phrase | refused, D-4 with `'and'` |
| A6 | u027 | `{0} be subjected to torture or to [cruel, inhuman or degrading treatment or punishment]` | refused, D-4 with `'or'`; fixed phrase 51 B; act 85 B |
| A7 | u079b | `{0} be held by secret vote or by [equivalent free voting procedures]` | refused, D-4 with `'or'`; act 66 B |
| A13 | u0156.s03 | `{0} actively deceive {1} about [the existence of a system prompt or its content]` | accepted, 78 B; fixed phrase 47 B |
| A15 | u024, u037 | two plain predicates with act `{0} take place` (14 B), sorts differing | both accepted; act identity includes sorts, so `actChecks` passes; if both carry the same form, their wordings are equal and V4 reports the duplicate (2.1) |
| A16 | u041 | `{0} to be presumed innocent until proved guilty according to law in [a public trial at which they have had all the guarantees necessary for their defence]` | accepted, 152 B; fixed phrase 84 B; not counted in M1 |
| A17 | — | `{0} take part if {1} is open`, arity 2 | refused, D-3 with `'if'` (the first clause word); 28 B |
| A18 | — | fixed phrase `the court that is competent` | refused, D-12 with `'is'` |
| A19 | u0263.s04.p2 | `{0} comply with [the operator’s instructions] in {1}`, arity 2 | accepted; canonical act `{0} comply with the operator's instructions in {1}`, 50 B (the source string is 52 B) |
| A20 | — | `{0} must seek asylum` | refused, D-3 with `'must'`; 20 B |
| A21 | — | `{0}` followed by 131 times ` ab` and 2 times ` a` | accepted, exactly 400 B |
| A22 | — | A21 with its last word `a` changed to `ab` | refused, D-2; 401 B |
| A23 | — | `{0} meet {1}` with arity 1 | refused, D-1 |
| A24 | — | `{0} neither seek nor enjoy asylum` | `canonicalAct` accepts it; `check` refuses it, D-4 with `'nor'` (the one exception of `check_extends`) |
| A25 | — | fixed phrases `equal pay for` and `for equal work` | refused, D-14 (overlap) |
| A26 | — | fixed phrases `equal pay` and `equal pay for equal work` | refused, D-14 (one holds the other) |
| A27 | — | fixed phrase `or its content` | refused, D-13 (begins with a join word) |
| A28 | — | `{0} seek asylum ,freely` | refused, D-1 |
| A29 | — | `{0} seek asylum,` | refused, D-6 |
| A30 | — | a plain declaration with `act` and no `form`; one with `form` and no `act`; one with `form: "may"` | refused, D-19 (twice), D-19 (invalid form) |
| A31 | corpus | every norms row of `tests/data/route-cases.jsonl` without `acts@0` | `decodeRegulatedIn` and `canonicalEnvironmentJson` give byte-identical results to today's (a Python test in AP-1; not in the stub) |
| A32 | u0123.s03 | the six fixed phrases of A14 (11.2), among them `false information that could deceive the user` | refused, D-12 with `'false'` (finding F10) |

`check_spec` holds in both directions on these: A1–A4, A13, A15, A16, A19 and A21 satisfy `Accepts` and are accepted;
A5–A7, A17, A20, A22–A24, A28 and A29 each fail exactly one conjunct of `Accepts` and are refused (the failing
conjunct: join word; join word; join word; clause word; clause word; bytes; slots; join word; word shape; the trailing
comma, which makes `lex` fail).

### 11.2 AP-2 (the grammar: derivations and readings)

Vocabularies (frames written `head: markers / split / modifiers`; adverbs after the frames):

- **V5** (u051): `seek: [""] / [] / ["in"]`, `enjoy: [""] / [] / ["in"]`; no adverbs; fixed `other countries`.
- **V6** (u027): `subjected: ["to"] / ["to"] / []`; fixed `cruel, inhuman or degrading treatment or punishment`.
- **V7** (u079b): `held: ["by"] / [] / []`; fixed `equivalent free voting procedures`.
- **V8** (u105): `participate: ["in"]`, `enjoy: [""]`, `share: ["in"]` (no split, no modifiers); adverbs `freely`; fixed
  `the cultural life of the community`, `scientific advancement and its benefits`.
- **V9** (u055): `deprived: ["of"]`, `denied: [""]`; adverbs `arbitrarily`; fixed `the right to change their
  nationality`.
- **V10** (u092): `security: ["in the event of"] / ["in the event of"] / ["in circumstances"]`; fixed `other lack of
  livelihood`.
- **V11** (u076): `take part: ["in"] / [] / ["through"]`; adverbs `directly`; fixed `freely chosen representatives`.
- **V12** (u087): `form: [""] / [] / ["for"]`, `join: [""] / [] / ["for"]`.
- **V14** (u0123.s03): `abandon`, `claim`, `use`, `provide`, `endanger`: `[""]`; `act: ["against"]`; fixed `its core
  identity or principles`, `to be human`, `genuinely deceptive tactics that could harm users`, `false information that
  could deceive the user`, `health or safety`, `Anthropic’s guidelines` (refused as a list: A32); G14v drops the fourth
  phrase.
- **VL** (limits): `seek` and `enjoy` as in V5; fixed `the first city`, …, `the eighth city`.

| # | Act phrase | Raw | Readings (*hand*) | The readings |
|---|---|---|---|---|
| G5 | `{0} to seek and to enjoy in [other countries] asylum from persecution` (67 B) | 2 | 2 | `all false false [seek+obj, enjoy+obj+in]` and the same with `in [other countries]` on both; the edge is `REt` |
| G5b | the same without the fixed phrase | 0 | 0 (`none`, D-16) | no derivation: in a shared-object last item the object may follow `in other countries` only if that phrase ends with a slot, a fixed phrase or an adverb (5.2), and `enjoy`'s object is required |
| G6 | `{0} be subjected to torture or to [cruel, …]` (85 B) | 1 | 1 | `any false true [subjected to torture, subjected to [cruel …]]`, both with *be* |
| G7 | `{0} be held by secret vote or by [equivalent …]` (66 B) | 1 | 1 | `one (be held, by: joined or [secret vote, [equivalent …]])` |
| G8 | `{0} freely to participate in [the cultural life …], to enjoy the arts and to share in [scientific …]` (138 B) | 2 | 2 | `all false false`: *freely* on `participate` only, or on all three; never on a middle item alone |
| G9 | `{0} be arbitrarily deprived of their nationality nor denied [the right …]` (97 B) | 2 | 2 | `any true false`: *arbitrarily* on `deprived` only (`deprivation_only`), or on both (`both_acts`); `denied` takes *be* from the first item |
| G10 | `{0} to security in the event of unemployment, sickness, disability, widowhood, old age or [other lack of livelihood] in circumstances beyond their control` (152 B) | 2 | 2 | `any false true` of 6 atoms; the modifier on the sixth only, or on all six |
| G11 | `{0} to take part in {1} directly or through [freely chosen representatives]` (73 B) | 1 | 1 | `any false false [take part in {1} directly, take part in {1} through [freely …]]` |
| G12 | `{0} to form and to join trade unions for the protection of their interests` (74 B) | 2 | 2 | `all false false`: the object *trade unions* on both; *for the protection …* on `join` only, or on both |
| G14 | the six acts as the source words them (238 B, folded) | 0 | — | the fixed-phrase list is refused (A32), so `lex` fails and no derivation exists |
| G14v | the other five acts: `{0} abandon [its core identity or principles], claim [to be human], use [genuinely deceptive tactics that could harm users], endanger [health or safety], or act against [Anthropic’s guidelines]` (183 B) | 1 | 1 | `any false false` of 5 atoms |
| G38 | `{0} to seek asylum or to enjoy asylum and to keep asylum` (V5 plus `keep: [""]`) | 0 | `none` | two join words in one list (one join level) |
| G39 | `{0} to seek, enjoy and to keep asylum` (same vocabulary) | 0 | `none` | a mix of own and shared *to* |
| L6 | `{0} to seek and to enjoy asylum in [the first city] … in [the sixth city]` (VL) | 64 | 64 | each `in [..]` on `enjoy` only or on both: 2⁶ |
| L7 | the same with seven cities | 128 | `limit` | 128 meanings > 64; raw 128 < 256, so the listing limit is the cause |
| L8 | the same with eight cities | 256 | `limit` | raw 256 = N: the parse is saturated |
| L0 | G5 with step budget 0 | — | `limit` | the parse returns `none` |

Generic listing boundaries (`listing_ok`, on synthetic trees `t_k` with `μ t_k = some k`, or all `some 0`):

| # | N, L | Trees | Expected |
|---|---|---|---|
| LG1 | 10, 64 | 9 trees, distinct meanings | `ok` of 9 (N−1 raw) |
| LG2 | 10, 64 | 10 trees | `limit` (N raw: saturated) |
| LG3 | 256, 64 | 63 trees, distinct | `ok` of 63 |
| LG4 | 256, 64 | 64 trees, distinct | `ok` of 64 |
| LG5 | 256, 64 | 65 trees, distinct | `limit` (65 > 64) |
| LG6 | 10, 64 | 10 trees, all meaning 0 | `limit`: ten derivations with one meaning may hide another, so no single reading is certified |
| LG7 | 10, 64 | 9 trees, all meaning 0 | `ok [0]` |
| LG8 | 10, 64 | `none` (budget) | `limit` |

`readings_exact` in both directions: in G8 the two listed trees are derived (left to right); the tree with *freely* on
`enjoy` alone, and the tree with *freely* on `participate` and `share` but not `enjoy`, are not derived and not listed
(right to left). In G12 the tree with `form` and no object is not derived (the shared-object pattern gives it the
object) and not listed. `read_unique`: G6, G7, G11, G14v return `ok`; G5, G8–G10, G12 return `many`; G5b, G38, G39
return `none`. The stub checks the listed trees of G8, G9 and G12 by value, and the two non-derived G8 trees by
absence.

Render round trip (`read_normal`): the two parts of G6 render as `{0} be subjected to torture` and `{0} be subjected to
cruel, inhuman or degrading treatment or punishment` and each reads back as `one` of itself; G7's atom renders as
`{0} be held by secret vote or equivalent free voting procedures` (the marker once) and reads back as itself.

### 11.3 AP-3 (the table and elaboration)

The table, per cell (`table` on the act trees of 11.2):

| # | Op, tree | Readings (*hand*) |
|---|---|---|
| T1 | *must not*, G6 (`any false true`) | 1: two atoms (two prohibitions) |
| T2 | *must*, G7 (`one`) | 1: the atom (one obligation; the act unchanged) |
| T3 | *must not*, G9's trees (`any true false`) | 1 each: two atoms |
| T4 | *may*, G9's trees | 0 each (*nor* under *may*: D-22) |
| T5 | *has the right to*, G11 (`any false false`) | 2: two atoms (each way), or `whole` (one act) |
| T6 | *has the right to*, G12's trees (`all false false`) | 1 each: two atoms |
| T7 | *has the right to*, G10's trees (`any false true`) | 1 each: six atoms |
| T8 | *must*, G6 (`any false true`) | 0 (a split marker's *or* under *must*: D-22) |
| T9 | *must not*, `all false false` (G12's first tree read as a prohibition) | 2: two atoms, or `whole` (only doing both) |
| T10 | *need not*, any join | 0 |

Elaboration (on `UDoc`s built in `ElaborateExamples.lean`; sorts `person`, guards `top`):

| # | Document | Expected (*hand*) |
|---|---|---|
| E1 | permission `p027` (deny), act G6, rule `r027` sign false | parts `p027__1` (act `{0} be subjected to torture`) and `p027__2`; rules `r027-a1`, `r027-a2`; `SplitMap` = `preds [(p027__1, p027, 1), (p027__2, p027, 2)]`, `rules [(r027-a1, r027, 1), (r027-a2, r027, 2)]` |
| E2 | obligation `p079` (deny), act G7, rule sign true | unchanged (`elaborate D = .ok D.U`); empty `SplitMap` |
| E3 | permission `p123`, act G14v, rule sign false | five parts `p123__1` … `p123__5`, five rules |
| E4 | E1 plus rule `r027b` sign true (*may*: each, by the split marker) with `over := ["r027"]` | parts as E1; `r027b-a1` over `r027-a1`, `r027b-a2` over `r027-a2` |
| E5 | E1 with `p027` unspecified | `unspec = [p027__1, p027__2]` |
| E6 | E1 plus obligation `s` whose rule's guard mentions `p027` | refused, D-25 |
| E7 | obligation `q` with dual `qm` (same act `{0} use [the tool] or provide [the data]`), rule on `q` sign true (*must*: one act) and rule on `qm` sign false (*must not*: split) | refused, D-24 |
| E8 | E1 with the predicate named by 62 bytes | refused, D-26 (part name 65 bytes) |
| E9 | permission `p` with act G11's tree, rule sign true (*may*) | refused, D-23 (two readings) |
| E10 | plain predicate, act G6's phrase under *has the right*, rule sign false | refused, D-21 |
| E11 | E1 with a model naming `p027` (Python) | refused, D-28 |

`splitMap_exact` in both directions on E1: every generated name is in the map with its source and index, and
`p027` (a source name) and `r027` are not generated names and not in the map. E11 and the `elaborate_faithful` check
are Python and model tests of AP-3, not in the stub: with finite models in `tests/test_acts_elaborate.py`, a model
where the prohibition on torture holds and the one on cruel treatment fails makes both sides false; a model where
both hold makes both sides true.

### 11.4 AP-4 (phrase readings and sources)

| # | Phrase, op | Phrase readings (*hand*) |
|---|---|---|
| P5 | G5, *has the right to* | 2 (split in each, with `in other countries` on `enjoy` or on both) |
| P8 | G8, *has the right to* | 2 |
| P9 | G9, *must not* | 2 = `deprivation_only`, `both_acts` |
| P9m | G9, *may* | 0 (refused, D-22) |
| P10 | G10, *has the right to* | 2 |
| P11 | G11, *has the right to* | 2 (each way; or one act) |
| P12 | G12, *has the right to* | 2 |
| P64 | L6, *has the right to* | 64 (listed) |
| P65 | L6, *must not* with the join read as *and* (each tree gives 2 readings) | `limit` (128 > 64) |

`phraseReadings_exact` in both directions: P11's two readings are listed and derived; the reading "only through freely
chosen representatives" (one atom) is neither (checked by value in the stub, with the `whole` reading's paraphrase of
2.2). `sourceCheck` (in `ReadingsExamples.lean`, on the pilot sets re-written in `acts@0` form, finding F3; these
need a readings document and are AP-4's, not in the stub):

| # | Sets | Expected |
|---|---|---|
| S1 | rs_u105b and rs_u105c coupled, u105a fixed, source G8 under *has the right to* | passes |
| S2 | S1 with the "all" candidate removed from both sets | refused: a reading has no choice (D-29) |
| S3 | S1 plus a candidate putting *freely* on `enjoy` only | refused: a choice is not a reading (the skipped middle) |
| S4 | rs_u055 re-written, source G9 under *must not* | passes |
| S5 | S4 with one candidate's sign flipped to *may* | refused: the choice changes the source rule's modal |

`sourceCheck_complete` is S1 and S4 read from right to left: their sets are exact, so the check passes.

### 11.5 AP-5 (specialisation)

`a` = `seek asylum in [other countries]`, `b` = `seek asylum` (both `to`, object `asylum`): `specialises ⟨["in"], []⟩ a
b = true`; `specialises ⟨[], []⟩ a b = false` (nothing declared, so nothing narrows); `specialises ⟨["in"], []⟩ b a =
false`. `specPremises` on two permission predicates with these acts and equal sorts gives one premise, `∀ x. pa x →
pb x`; on two plain predicates it gives none.

## 12. Limits, generated files, Python and Rust

| Limit | Value | Where |
|---|---|---|
| act phrase | 400 bytes | `Lexical.maxActBytes` |
| fixed phrase | 300 bytes; 128 per document | `maxPhraseBytes`, `maxPhrases` |
| frames | 128 per document | `framesOk` |
| raw derivations | `rawCap` = 256 (provisional, AP-0) | 1.6 |
| step budget | `stepBudget` = 2,100,000 (provisional, AP-0) | 1.6 |
| readings | 64 | `maxReadings` |
| part names | 64 bytes (predicate), `ruleName` (rule) | `elaborateMap` |
| join levels | one per act phrase | 5.2 |

**Generated files** (never edited by hand; `uv run python tools/regen_generated.py --write`): per batch as the plan's
section 4 lists, plus `lean/VE/Route/frozen-sources.sha256` for the `Wire.lean`, `Tree.lean` and `Plain.lean` hunks
(AP-1), AR-10's generated profile data (AP-1) and mode registry (AP-4), and the `norms` / `norm-defaults` response
schemas (AP-3).

**Python** loads the `acts` block and the plain `act` / `form` fields as data (no check), renders Lean's wordings and
paraphrases, relays `acts-elaborate` and `act-readings` (schema and binding only), refuses models, data and questions
that name a split predicate with Lean's text (D-28), and runs its conflict search on the relayed document.

**Rust** skips its act lint when the profiles contain `acts@0`, and treats acts as identity strings.

**Re-estimate** (plan G16; *estimate*, for the DRI, replacing draft 1's withdrawn figures): AP-1 7 h (four more hunks
than draft 1, F1); AP-2 8 h (the rule table and meaning are larger than draft 1 assumed); AP-3 8 h (the relay and the
reference table); AP-4 7 h; AP-5 3 h; AP-5b 4 h (design and review); total about 37 h before the experiments.

## 13. Statement review checklist (Astra and Fable)

1. Does `check` accept exactly what 1.3 says (`check_spec`), and is `check_extends` true as stated, without a
   hypothesis on glued slots (`a{1}` passes `canonicalAct` and `check` alike)?
2. Does `fixedOk`'s overlap rule make grouping unique (`fixedOk_unique`), and is it too strict for real documents?
3. Is the rule table of 5.2 free of derivations other than the five edge rules? (The fixtures of 11.2 test the pilot
   phrases; the review should look for a counterexample.)
4. Is the meaning of 5.3 the plan's 2.3 and 2.4: first-or-all before a list, last-or-all after it and in a
   shared-object last item, never a skipped middle?
5. Are `read_unique` and `readings_exact` the debate's contract: one meaning, from a complete enumeration?
6. Do the table equations (6.2) match the plan's 2.3, including the split-marker and *nor* cells?
7. Is `elaborate_faithful` the right faithfulness statement (part i means what the source rules mean, read of
   `p__i`)? Is `IntendedActs` independent enough of `elaborateMap`?
8. Is the reference table (6.5) complete?
9. Is `SourceExact` the bijection the debate asked for, bound to an explicit template?
10. Are the AR-10 row's refusals (4.4) right, and is the decoder reach (F1) complete?
11. Choices C1–C27 (14): accept, or change.
12. Finding F10: keep *true*, *false*, *no* and *every* out of fixed phrases, or allow them there.
13. Re-run the stub (15) after any change to a definition here; it is the measurement.

## 14. Choices made in this draft, and findings

### 14.1 Choices (where the plan left room, or a statement is sharpened)

| # | Choice | Why |
|---|---|---|
| C1 | Frames gain `mods` (modifier markers); the vocabulary is `V : Vocab` with declared `adverbs`, in place of the plan's `fs : List Frame` | one reading needs known ends for word fillers, and the argument/modifier difference decides sharing against the edge rule (u087's purpose phrase is an edge; u105's "share in" is an argument) |
| C2 | One join level: `Act` is `one`, `all` or `any` over atoms; the plan's `List Act`, `simple` and the `2 ≤ length` hypotheses go | the pilot needs no nesting, and nested joins multiply readings past what auditors can check; refusing them is honest |
| C3 | `Atom.joined fs A` becomes `Simple.whole A`; the table returns `List (List Simple)` | a whole join is not an atom; it keeps its predicate and its phrase |
| C4 | `Atom` has `toWord`, `beWord`, `head`, `args` (with `Filler.joined`) and `mods : List Modifier` | *to* and *be* are shared across items and must be rendered in parts; a non-split marker's list is one filler |
| C5 | `read` returns `ReadOutcome` (`ok`, `none`, `many`, `limit`) over meanings, not `VE.Grammar.Outcome` over trees | the debate's `read` is about meanings |
| C6 | `read` and `readings` take `N` and `b`; the product uses `rawCap` and `stepBudget`, both measured by AP-0 | the plan's D2 and AP-0 item 4 |
| C7 | `opOf` returns `Option Op` | plain with sign false has no modal in the table |
| C8 | Heads exclude *to* and *be*; A6's frame head is `subjected` (the plan wrote `be subjected`) | *be* is shared across items ("be arbitrarily deprived … nor denied") and carries an adverb inside it |
| C9 | `""` in `markers` makes the object required; the object comes first, except in a shared-object last item after a modifier ending in a slot, fixed phrase or adverb | without it, a word filler can swallow the object silently (G5b) |
| C10 | A5 declares `other countries` as a fixed phrase (G5) | C9; the alternative is the object first |
| C11 | A10's modifier marker is `in circumstances` | a frame's markers must not be word-prefixes of each other (`in` and `in the event of` would compete) |
| C12 | A14's *while* and *when* clauses: splitting copies one guard to every part, so a clause that belongs to one item must not be the shared guard; the faithful translation writes those items as their own rules. G14v tests the split with guard `top`, on five acts (F10) | the plan's "move to guards" is right only per item |
| C13 | `check` mirrors `canonicalAct`'s shape test on slot-replaced words (commas stripped), then checks tokens; fixed phrases may not overlap; `check_no_join` and `check_no_clause` stated with `= false`; `check_spec` added | `check_extends` must hold for every act today's check accepts, glued slots included |
| C14 | The canonical act is folded (`’` → `'`) and normalised; A19's is 50 B | identity must not depend on the apostrophe |
| C15 | A plain act is stored in `Regulated.act` (the `Tree.check` admission); `form` stays in the declaration JSON and is read only for the wording | one place for acts; `Regulated` keeps its fields |
| C16 | `WellFormedActs` is dropped: `elaborateMap` checks its own conditions and ends with `WellFormedU` | one owner for well-formedness |
| C17 | `elaborate_faithful` is stated with `readAs` and `partNames` | an independent statement of "each part means what the source rules mean" |
| C18 | `acts-elaborate` is a case kind of the `norms` and `norm-defaults` modes, not a new mode | keeps D1 (no new mode until AP-4) and keeps `Protocol.lean` out of AP-3 |
| C19 | `Source` carries an explicit template (`Node`), role, sign, completion and shared units; `sourceCheck_complete` added | the debate's "bound to an explicit source template"; the exactness claim is an "exactly when" |
| C20 | `Restrictive` has `markers` and `adverbs` | 1.9 |
| C21 | `specPremises_plain` restated without its free `p` | the plan's version was vacuous for most `p` |
| C22 | One join word per list; mixing *and* and *or* has no derivation | the classic ambiguity; refused, not read |
| C23 | Coordination patterns all-bare, shared-object and full; own-*to* and shared-*to* modes; mixes refused | disjoint patterns give one derivation per reading |
| C24 | Wording distinctness (V4) is unchanged | english-lean owns V4; open question 8.3 of the plan stays open |
| C25 | The five edge contexts of 5.2 are the only sources of several derivations | the plan's 2.4, made exact |
| C26 | `modifier_edges` is stated over the schema's kinds (`attachOf`, `edgeLhs`) | the `Attach` type has no middle position; the theorem pins where each edge kind may occur |
| C27 | New fixtures A21–A32, G5b, G14v, G38, G39, L0, L6–L8, LG1–LG8, T1–T10, E1–E11, P5–P65, S1–S5 | each "exactly when" gets a fixture in each direction |

### 14.2 Findings for the review

| # | Finding | Proposed resolution |
|---|---|---|
| F1 | `decodeRegulated` has callers beyond `Norms/Wire.lean`: `Norms/Plain.lean` (`decodeRegulatedAll`, used by `EnglishGrammar/Encode.lean:127`, `Service/Family.lean:59`, `Service/Standalone.lean:30,598,715`) and `EnglishGrammar/Encode.lean:255` (`modalForm`). Under `acts@0` the English typing view and the standalone services would refuse every long or plain act | AP-1 adds hunks to `Plain.lean`, `Encode.lean` (with `Policy.lean`, first in the `EnglishGrammar` queue) and `Standalone.lean`; `Family.lean` is unreachable once the row refuses `closure@0` and `order@0` |
| F2 | The plan's row has only `requires := ["norms@0"]`; the soft, rights, alternatives, closure and order routes decode norms without `acts@0`'s hook | the refusals of 4.4 |
| F3 | The pilot's rs_u055 and rs_u105b/c encode the readings with a case sort and duties (`udhr_specs.py:388-410`), not with structured acts, so they cannot pass `sourceCheck` as they are | AP-4's fixtures S1–S5 use the sets re-written in `acts@0` form (candidates on predicates whose acts are the rendered simple acts); the pilot re-writes them when AP-4 merges (D7) |
| F4 | The plan's A5 has no fixed phrase; under C9 it has no reading (G5b) | declare `other countries` (C10), or put the object first |
| F5 | Clause words do not catch relative clauses without a listed word ("that could harm users"); such clauses pass inside fillers and fixed phrases | an audit item (2.4); a longer clause-word list would break `check_extends` for today's acts |
| F6 | `Norms/Tree.lean`, `Wire.lean` and `Plain.lean` are hash-pinned in `lean/VE/Route/frozen-sources.sha256` | regenerate with the batch (12) |
| F7 | Elaborated documents hold acts that are not AP-1 acts (a part with a joined filler; a whole join) | they are internal and never re-decoded; the relay carries them as data |
| F8 | The synthesis's protocol queue does not list AP-3's relay | resolved by C18; if the review prefers a mode, it joins the queue before AP-4 |
| F9 | Not every statement could be type-checked: the AR-10 row (4.4), the response shapes (6.7, 7) and AP-6 (9) name modules that do not exist yet | each is type-checked by the batch that adds it |
| F10 | *False* is a clause word (today's `actReserved`), and the clause words also hold *true*, *no*, *not* and *every*, which occur as ordinary words in act phrases. u0123.s03's fourth act, "provide false information that could deceive the user", is therefore refused even as a fixed phrase (A32), so the plan's A14 ("six prohibitions") cannot pass as written; the stub measured this, the hand draft had missed it | either keep the rule (the translator rephrases, and A14 gives five prohibitions plus one act left unformalised), or let a fixed phrase hold *true*, *false*, *no* and *every* as adjectives while still refusing the clause-forming words (*is*, *if*, *then*, *not*, *must* …). The second changes 1.1 condition 3 only; `check_extends` is unaffected, since today's check accepts none of these words. For the review and the DRI |

## 15. The stub

`lean/SpecStubs_act-phrases.lean` (scratch, about 1,700 lines, no `sorry`; never committed, and left untracked in the
`design/act-phrases` worktree because the session could not delete files) contains:

- full bodies of every AP-1 definition (`rawLex`, `phraseToks`, `decodeFixed`, `group`, `lex`, `check`,
  `decodeRegulatedActs`, `wording`), the grammar schema, `build`, `grammar`, `meaning`, `listing`, `readings`, `read`,
  `analyse`, the rendering, `table`, `paraphrase`, `readingOf`, `elaborateMap`, `checkAct`, `phraseReadings`,
  `sourceCheck` and `specialises` / `specPremises`;
- 51 theorems of sections 4 to 8 as `def <name>_stmt : Prop := <statement>`, each elaborated (the statements that
  name AR-10's table, the response shapes or AP-6 are not among them, F9);
- 161 `#guard`s: every number and diagnostic of section 11 except those marked as Python, model or AP-4 tests.

It was run from `lean/` with `lake env lean SpecStubs_act-phrases.lean` after `lake build` of its imports
(`VE.Norms.Wire`, `VE.NormDefaults.Tree`, `VE.Readings.Choice`, `VE.Readings.Separate`, `VE.Grammar.Reading`), with
no error and no warning. The first run found one syntax slip in the stub and the A14 number (F10), and both were
corrected before the final run. AP-2's `GrammarExamples.lean` and AP-3's `ElaborateExamples.lean` should start from
it; the worktree copy should be deleted once it is no longer needed.

## Change log

- Draft 1 (2026-10-13): first draft, from the plan's draft 2; statements and fixtures checked in the stub (15).
