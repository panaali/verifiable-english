# Purpose and explanation (`purposes@0`): item-1 statement specification

> Status: item-1 specification, draft 2 (2026-10-28), branch `design/purpose-explanation`. It is written from
> [purpose-explanation-PLAN.md](purpose-explanation-PLAN.md) draft 3 (cited **plan n**). That draft applies the
> converged plan debate (`manage-agents/debates/design-purpose-explanation/{fable,astra}.md`: REVISE, then BUILD;
> CONVERGED after round 3) and the acting DRI's cross-plan rulings of 2026-10-28
> (`manage-agents/reviews/dri-decisions-20261028-purpose-explanation.md`, cited **DRI n**).
>
> This is the statement under the Astra + Fable statement review that gates PE-1 (plan order, step 2). Sections 1 to 6
> are the statements under review. Section 12 lists every point where this draft chose between readings of the plan,
> and section 13 maps each converged edit to the section that carries it. Theorem statements and fixtures are
> implementation obligations, not claims of completed proofs or tests, except the proofs section 11 records.
>
> Draft 2 applies the statement review's ruling (`manage-agents/debates/purpose-explanation-spec/DRI-RULING.md`,
> items 1 to 14, cited **SR n**; section 13 maps each item to its sections). The gate check compares this document and
> the plan against SR 1 to SR 13 once and reopens nothing else (SR 14). PE-1 starts after it passes; SR 5 and SR 6 are
> PE-1's statement changes, and the other items are PE-2 text or PE-5 statements.
>
> Draft 1's statements were elaborated against `main` at `6d0a10526`, and its fixture values were computed by
> `#eval`, `rfl` or `decide` (section 11). Draft 2's new and changed statements and values, listed in 11.1, were
> written in a pass with no shell, so they are not elaborated yet. Each value there is derived by hand from the
> definitions and says so; the batch that owns it confirms it by `#guard` or `rfl`.
>
> **pe-rev, DRI 2026-11-02 fp-purpose-explanation item 1.** This pass applies findings PE-R8 and PE-R11 of the
> 2026-11-02 re-pilot to the statements (`manage-agents/reviews/dri-decisions-20261102-fp-purpose-explanation.md` item
> 1; PE-R6, PE-R7, PE-R9 and PE-R10 are plan text, plan 10.3). New: `Part.readings`, `Units.packSources`,
> `holdsTarget`, `shownUnder`, `unlinkedActive`, `packsInert` (fault 6a) and their theorems (4); `linkLines`,
> `underLine`, `scopeLine` (2.3); the view's `readings` and `packSources` (5.1); the section's `under` (5.4);
> fixtures F2c–F2e, F9, F10 (9.2, 9.7). They are written without elaboration (11.1, marked †). Section 13 maps each.
>
> Inputs: [document.md](document.md) (W2), [question-answering.md](question-answering.md) (`VE.Ask`, RD-3),
> [discourse.md](discourse.md), `lean/VE/Route/Admission.lean`, `lean/VE/Ask/*`, `lean/VE/Service/Document.lean`,
> `lean/VE/Readings/Wire.lean`, `lean/VE/Norms/Admission.lean`. Nothing here changes a frozen contract, an existing
> theorem statement or an existing checker function. The additions to existing owners are new definitions in their
> namespaces (sections 3, 5.1, 5.2 and 6.1).

## 0. Scope, one paragraph

A document's own reasons and purposes ("We place X above Y because …", "This is why …", "… in order to …") are
recorded as **links** in a front-matter `purposes` block under `purposes@0`. A link joins the parts that carry the
reason or purpose, the target, and the link words (the *marker*). It adds no premise and changes no rule. Lean checks
the link's structure. It checks that the side the text does not state (a purpose, a denied reason) is **inert**:
never a premise and never a rule. Lean writes the sentence a reader sees. Where the target is one stated claim with
one formula, Lean also reports whether the stated reason is enough. It asks the target's question of the document
*without the target's own assertion*, on whichever of ask's three adapters (plain, zero-set, enumerated) ask selects
for the document. It reads the answer from the replayed certificate's cited sources, and it names every other
sentence, rule or definition the proof used. Support on soft documents (a soft chain with defaults and exceptions)
waits until ask serves them: until then a support request on one gets ask's own refusal (SR 11, 6.1). Out of scope for
item 1, by the plan: cross-unit links through discourse mentions (PE-4, plan 2.8); source-word rows and authored-text
refusals in the catalogue (PE-3); claims about the rules' own shape (PE-6, gated on S3's owner); purposes of acts on
events (PE-7b, gated on C21's bridge).

In this specification: the block (1), the English (2), nonfactivity (3), well-formedness (4), the document mode (5),
the support check (6), diagnostics (7), the guarantees in plain words (8), the acceptance fixtures (9), layers and
owners (10), the elaboration record (11), the choices this draft made (12), and the edit map (13).

## 1. The `purposes` block

### 1.1 `lean/VE/Purposes/Decl.lean` (PE-1, layer 2)

```lean
import VE.Route.Admission

namespace VE.Purposes

/-- The two W2 relations a link carries; `prevents` is events-time-causation's (plan D8). -/
inductive Relation where
  | because
  | inOrderTo
  deriving DecidableEq, Repr

def Relation.wire : Relation → String
  | .because => "because"
  | .inOrderTo => "in order to"

def Relation.ofWire? : String → Option Relation
  | "because" => some .because
  | "in order to" => some .inOrderTo
  | _ => none

theorem Relation.wire_mem (r : Relation) : r.wire ∈ VE.Route.Admission.relations
theorem Relation.ofWire_wire (r : Relation) : Relation.ofWire? r.wire = some r
theorem Relation.wire_ne_prevents (r : Relation) : r.wire ≠ "prevents"

inductive Polarity where
  | affirmed      -- "because", "in order to", "this is why"
  | denied        -- "this isn't because", "not because"
  deriving DecidableEq, Repr

/-- What the text says about other reasons for the same target. `partly`, not `partial`: `partial` is a Lean
    keyword (plan 2.1). -/
inductive Share where
  | plain         -- says nothing about other reasons
  | sole          -- "only because", "solely because", "simply because", "just because"
  | partly        -- "partly because", "in part because"
  | notSole       -- "not merely because", "not only because", "not just because"
  deriving DecidableEq, Repr

/-- What one side of a link names: a part of the checked document, or (PE-4) a discourse mention. -/
inductive Ref where
  | part (id : String)
  | mention (id : String)
  deriving DecidableEq, Repr

structure Link where
  id       : String
  relation : Relation
  polarity : Polarity
  share    : Share
  reason   : List Ref        -- for `inOrderTo`, the purpose; in source order
  target   : List Ref        -- the rule, claim, ranking or device the reason is given for
  marker   : String          -- the part whose bytes are the link words
  deriving DecidableEq, Repr

structure Block where
  links : List Link
  deriving DecidableEq, Repr

def maxLinks : Nat := 256

/-- Why a link gets no support question (plan D5), in the order `eligible` tests them (6.3). -/
inductive NotChecked where
  | purpose      -- `in order to`: whether a rule serves its purpose is never checked
  | denied       -- nothing is claimed to support
  | ruleTarget   -- the target is a rule (practical reasons are not tested)
  | readings     -- a side has an active reading set
  | noFormula    -- the target is not one stated, checked formula, or a reason part is not
  deriving DecidableEq, Repr

end VE.Purposes
```

`Decl.lean` imports nothing from `VE.Ask`, so other plans can use the link from layer 2 (S1, plan 8). `Support`
is in `Verdict.lean` (2.3), which is layer 4.

### 1.2 The wire form (`lean/VE/Purposes/Wire.lean`, PE-1)

The front-matter member `purposes`, admitted only when the environment lists `purposes@0` (5.2):

```json
{"links": [{"id": "l1", "relation": "in order to", "polarity": "affirmed", "share": "plain",
            "reason": [{"part": "u0146.s01.p3"}], "target": [{"part": "u0146.s01.p1"}],
            "marker": "u0146.s01.p2"}]}
```

- The block is an object with exactly the member `links`, an array of at most `maxLinks` links.
- A link has exactly `id`, `relation`, `polarity`, `reason`, `target` and `marker`, and may have `share`. An absent
  `share` is `plain`.
- `id` and every part or mention id is a token (`VE.Route.Admission.token`).
- `relation` is `"because"` or `"in order to"` (`Relation.ofWire?`). `"prevents"` and every other word are refused
  (plan D8, D9).
- `polarity` is `"affirmed"` or `"denied"`. `share` is `"plain"`, `"sole"`, `"partly"` or `"not_sole"`.
- A side is an array of `{"part": id}` or `{"mention": id}` objects. PE-1 refuses mentions (4.3); PE-4 resolves them.

```lean
namespace VE.Purposes
open Lean

def Share.wire : Share → String
  | .plain => "plain" | .sole => "sole" | .partly => "partly" | .notSole => "not_sole"

/-- Exact fields (`VE.Bridge.exactFields`); the texts are 7.1's. -/
def decodeBlock (j : Json) : Except String Block
/-- The canonical form: every member written, `share` included. -/
def renderBlock (B : Block) : Json

theorem decodeBlock_render (j : Json) (B : Block) (h : decodeBlock j = .ok B) :
    decodeBlock (renderBlock B) = .ok B

theorem decodeBlock_relations (j : Json) (B : Block) (h : decodeBlock j = .ok B) :
    ∀ L ∈ B.links, L.relation.wire ∈ VE.Route.Admission.relations ∧ L.relation.wire ≠ "prevents"
end VE.Purposes
```

`decodeBlock_relations` holds by the type: it follows from `Relation.wire_mem` and `Relation.wire_ne_prevents`
(the stub proves it that way, 11).

### 1.3 What a link means

A link is a statement *about the text*: "the text gives R as the reason for T" (affirmed `because`), "the text says R
is not the reason for T" (denied), or "the text gives P as the purpose of T" (`in order to`). It has no formula. No
premise, rule, verdict, status or coverage row of the document changes because of it (`checkDocPurposes_base`, 5.3).
What each side itself asserts is decided by that side's own W2 kind, as everywhere in W2. The block only adds one
condition, nonfactivity (3, 4): a side the text does not state must be inert, and (pe-rev, PE-R11) no pack may take
a premise from it (`packsInert`, 4.2). A link has no candidate field: its line is shown only under the candidates
that hold its target, and it says when the sentence has a part it leaves out (2.3, PE-R8).

## 2. English

### 2.1 Authored wordings, one reading each (PE-3; plan D11)

Each wording has exactly one reading under `purposes@0`, and the profile fixes it. The paraphrase is what a reader
with no training should take from it.

| The author writes | The one reading (paraphrase) | Formal effect |
|---|---|---|
| `<A> This is because <B>.` | The text says B, says A, and gives B as its reason for A. | link `because`, affirmed, `plain`; reason B, target A |
| `<A> This is only because <B>.` | As above, and B is the text's only reason for A. | share `sole`; refused if another affirmed link gives A a different reason |
| `<A> This is partly because <B>.` | As above, and B is part of the reason; the text need not say what the rest is. | share `partly`; needs no other link (A4) |
| `<A> This is not only because <B>.` | As above, and B is one reason, not the only one. | share `notSole`; needs no other link (A4) |
| `<A> because <B>.` (one sentence) | The text says B, says A, and gives B as its reason for A. | one MIXED unit: parts A, " because ", B; link `because`, affirmed, `plain`; reason B, target A (PE-1) |
| `<A> only because <B>.` / `<A> partly because <B>.` (one sentence) | As above, and B is the text's only reason for A / part of the reason. | the same MIXED unit; share `sole` / `partly` |
| `<A> This is not because <B>.` | The text says A, and says that B is not its reason. The text does not say B. | link denied; B inert (`explanation`), never a premise or a rule (D8a) |
| `<B> This is why <A>.` | The text says B, says A, and gives B as its reason for A. | link `because`; reason = the previous sentence (PE-4) |
| `<rule> The purpose of this rule is that <Y>.` | Y is the purpose the text gives for the rule. The rule is unchanged, and the text does not say Y is achieved. | link `in order to`; Y inert |
| `<rule>, if doing so serves the purpose that <Y>` (wording fixed by PE-E1) | The rule applies only where doing it serves Y. | a guard conjunct: an open term with its decider (no link) |

### 2.2 Refused authored wordings, with their rewrites (PE-3, rows in `SourceWords.lean`)

| Refused | Why it has more than one reading | The rewrite the refusal gives |
|---|---|---|
| "not … because" | "Claude does not refuse because the user is rude." can deny the refusal or deny the reason. | "Write which you mean: '<not A>. This is because <B>.' or '<A>. This is not because <B>.'" |
| "in order to", "so that", "so as to", "to the end that", "for the sake of", "for the purpose of" after a rule | The purpose may explain the rule or limit it. | "Write 'The purpose of this rule is that …' if the purpose does not change what the rule requires, or add the condition '…, if doing so serves the purpose that …' if it does." |
| "since", "as", "given that" in their reason sense | "since" and "as" also read as time. | "Write '<A> This is because <B>.'" The reason sense of "since" extends ET-5's canonical "since" row (C1, A6). |

The inline rows of 2.1 are affirmative only (SR 4). Any negation before an inline "because" stays under the first
row above: "Claude does not refuse because the user is rude." is refused with that row's rewrite, and so is an inline
"not only because" or "not merely because". The share `notSole` is written as 2.1's separate sentence, "This is not
only because …" (fixture in 9.8, PE-3).

In *source* text these words are not refused. They are reading sets (plan D6), and PE-E1 may add sets but never
reduces one to one reading without a textual argument per unit (A4, DRI 4).

### 2.3 The lines a reader sees (`Verdict.lean`, `English.lean`; PE-2 and PE-5; layer 4)

Lean writes every line; Python prints it (plan D10). A link row has two lines: what the text says (`says`) and what
VE found (`verdict`). The rules:
- **Quotes** follow ask's C1 rule. A side's text is the source bytes from its first part's start to its last part's
  end, trimmed (`sideText`, through `VE.Ask.bytesOf`). On a well-formed block the side's parts are adjacent and in
  order (`sidesAdjacent`, 4.2), so the quote is exactly the listed parts' bytes, trimmed (`sideText_eq`, 4.4).
- **A closing quote** gets a full stop after it unless the quoted text already ends with `.`, `!`, `?` or `:`
  (`closing`; `stop` applies the same rule to a line that ends with a quote). The source bytes are never changed.
- **Sentence numbers** are ask's (`VE.Ask.Context.displayOf`, `VE.Ask.citationText`). A part takes its parent
  unit's number. Two rules apply to a verdict's other units, in this order (SR 2):
  - A cited part whose parent is the target's parent is named by its quote (ask's C1 rule, `closing`), never by its
    sentence number, because that number is the claim's own sentence and would read as the claim proving itself.
  - The remaining parts' sentence numbers are deduplicated (`eraseDups`) before `citationText`, so two parts of
    sentence 5 print "sentence 5".
- **Reading clauses** follow ask's rule exactly (SR 3, 6.4): a line that shows a situation names every open set's
  reading of its witness row (`VE.Ask.readingSuffix`), even when every row has the same verdict; with two or more
  groups of rows, each line starts with ask's reading clause for its group.
- **No empty object** (SR 1): `without [] []` has its own sentence, so no line has two spaces in a row (9.7).
- **A situation** is `VE.Words.situation` of the replayed countermodel or split, through ask's `situationOf`.
- **UNKNOWN** is ask's `leadText .unknown`, then ask's `reasonText`.
- **Own frames where the meaning differs.** The support question is asked without the target, so its frames say
  "everything else the text says". Ask's frames ("a situation the document allows", "the document rules this out")
  would be false of the whole document, which asserts the target.
- † **Only under the candidates that hold the target (pe-rev, PE-R8; plan D10a).** `Link` has no candidate field, so
  a link's line appears only under the candidates that hold its target. When a target part has an active reading
  set, the row's lines are followed by `underLine` of `shownUnder` (4.2), and the row's `under` (5.4) names those
  candidates for the renderer. When no candidate of some target part holds the target, the link's lines are
  withheld: `linkLines` is `[]`. A candidate holds the target when its kind is the kind the marker's slot gives the
  target (`holdsTarget`): under u0014.s03's {report; rationale; limiting; in-attitude}, `report` and `in-attitude`
  hold no rule of the text, so the line "The text gives this purpose for …" is not shown under them.
- † **A scope the line cannot name (PE-R8).** When the link's unit has a part that no link of the block names and
  whose kind is not inert (`unlinkedActive`, 4.2), the quotes may leave out a scope that part puts over the link
  (u0289.s05's "Sometimes"). `scopeLine` then says so. A scope from another unit reaches a link only through PE-4's
  resolved sides, where PE-4 applies `shownUnder` and `unlinkedActive` to the resolved units (plan 2.8).

```lean
namespace VE.Purposes

/-- What VE found about one link (6). NEW under PLANS-INDEX D8 (E6). -/
inductive Support where
  | alone                                   -- a reason unit is cited, and nothing else the author wrote
  | together (units definitions : List String)  -- a reason unit and these others are cited
  | without (units definitions : List String)   -- no reason unit is cited; these are
  | notEnough
  | ruledOut
  | notSettled
  | unknown (reason : VE.Ask.Reason)
  | notChecked (why : NotChecked)
  deriving DecidableEq, Repr

def NotChecked.wire : NotChecked → String
  | .purpose => "purpose" | .denied => "denied" | .ruleTarget => "rule_target" | .readings => "readings"
  | .noFormula => "no_formula"

/-- `{"verdict": "alone"}`, `{"verdict": "together", "units": [..], "definitions": [..]}`, `{"verdict": "without",
    "units": [..], "definitions": [..]}`, `{"verdict": "not_enough"}`, `{"verdict": "ruled_out"}`,
    `{"verdict": "not_settled"}`, `{"verdict": "unknown", "reason": VE.Ask.reasonFrame r}`,
    `{"verdict": "not_checked", "why": NotChecked.wire w}`. -/
def renderSupport (s : Support) : Lean.Json
def decodeSupport (j : Lean.Json) : Except String Support

theorem decodeSupport_render (s : Support) : decodeSupport (renderSupport s) = .ok s
end VE.Purposes

namespace VE.Purposes.English
open VE.Purposes

def quoted (q : String) : String := "\"" ++ q ++ "\""

/-- Ends a line with a full stop, unless it ends with a quote whose text already ends with `.`, `!`, `?` or `:`. -/
def stop (s : String) : String := if [".\"", "!\"", "?\"", ":\""].any s.endsWith then s else s ++ "."

/-- A closing quote: draft 1's function, now `stop` of the quote (the same value for every `q`, 9.7). -/
def closing (q : String) : String := stop (quoted q)

def says (L : Link) (reason target : String) : String :=
  match L.relation, L.polarity, L.share with
  | .because,   .affirmed, .plain   => s!"The text gives this reason for \"{target}\": {closing reason}"
  | .because,   .affirmed, .sole    => s!"The text says this is the only reason for \"{target}\": {closing reason}"
  | .because,   .affirmed, .partly  => s!"The text gives this as part of the reason for \"{target}\": {closing reason}"
  | .because,   .affirmed, .notSole =>
    s!"The text gives this as one reason, not the only one, for \"{target}\": {closing reason}"
  | .because,   .denied,   _        => s!"The text says this is not the reason for \"{target}\": {closing reason}"
  | .inOrderTo, .affirmed, _        => s!"The text gives this purpose for \"{target}\": {closing reason}"
  | .inOrderTo, .denied,   _        => s!"The text says this is not the purpose of \"{target}\": {closing reason}"

/-- A side's text: the source bytes from its first part's start to its last part's end, trimmed. -/
def sideText (U : Units) (s : List Ref) : Option String := do
  let ps ← s.mapM fun r => r.partId? >>= U.find?
  let a ← (ps.head?).map (·.span.1)
  let b ← (ps.getLast?).map (·.span.2)
  (VE.Ask.bytesOf U.source a b).map String.trim

/-- SR 6: on an adjacent side (`sideAdjacent`, 4.2) whose parts are whole characters, the quote is exactly the listed
    parts' bytes, in order, trimmed: no unlisted text, and never the empty interval of a reversed side. -/
theorem sideText_eq (U : Units) (s : List Ref) (ps : List Part) (bs : List String)
    (hs : (s.mapM fun r => r.partId? >>= U.find?) = some ps) (ha : sideAdjacent U s = true) (hne : ps ≠ [])
    (hb : ps.mapM (fun p => VE.Ask.bytesOf U.source p.span.1 p.span.2) = some bs) :
    sideText U s = some (String.join bs).trim

/-- A unit's or a part's display number: ask's, a part taking its parent's. -/
def displayOf (U : Units) (ctx : VE.Ask.Context) (i : String) : Option Nat :=
  ctx.displayOf (((U.find? i).bind (·.parent)).getD i)

/-- How a verdict line names a cited unit (SR 2). -/
structure Naming where
  number : String → Option Nat      -- the sentence number, `displayOf U ctx`
  quote  : String → Option String   -- a part's text, `sideText U [.part i]`
  own    : String → Bool            -- the part's parent is the target's parent

/-- A part is in the target's own sentence when its parent is the target's parent. -/
def ownSentence (U : Units) (t i : String) : Bool :=
  match (U.find? t).bind (·.parent) with
  | some p => (U.find? i).bind (·.parent) == some p
  | none => false

def Naming.of (U : Units) (ctx : VE.Ask.Context) (t : String) : Naming :=
  ⟨displayOf U ctx, fun i => sideText U [.part i], ownSentence U t⟩

/-- The other units and definitions a verdict names. E-c first: a part of the target's own sentence is named by its
    quote (ask's C1 rule), never by that sentence's number. Then E-b: the remaining parts' numbers, each once
    (`eraseDups`), through `VE.Ask.citationText`. Then the definitions. -/
def others (n : Naming) (us ds : List String) : Option String := do
  let qs ← (us.filter n.own).mapM n.quote
  let ns := (← (us.filter (!n.own ·)).mapM n.number).eraseDups
  let defs := if ds.isEmpty then [] else
    [(if ds.length == 1 then "the definition of " else "the definitions of ") ++ VE.Senses.andList ds]
  pure (" and ".intercalate ((if ns.isEmpty then [] else [VE.Ask.citationText ns]) ++ defs ++ qs.map quoted))

def verdict (n : Naming) (situation : Option String) : Support → String
  | .notChecked .purpose    => "VE does not check whether it serves this purpose."
  | .notChecked .ruleTarget => "VE does not check whether a reason is good enough for a rule."
  | .notChecked .denied     => ""
  | .notChecked .noFormula  => "VE cannot check this reason yet: a side has no formal reading."
  | .notChecked .readings   => "VE cannot check this reason yet: a side has more than one reading."
  | .alone => "VE checked that this reason is enough to conclude the claim."
  | .together us ds => match others n us ds with
    | some o => stop s!"VE checked that this reason is enough to conclude the claim together with {o}"
    | none => ""
  | .without [] [] => "VE checked that the claim follows without this reason, from nothing else the text says."
  | .without us ds => match others n us ds with
    | some o => s!"VE checked that the claim follows from {o} without this reason."
    | none => ""
  | .notEnough => match situation with
    | some s => "VE found that this reason is not enough: in this situation, everything else the text says is " ++
        s!"true and the claim is false: {s}."
    | none => ""
  | .ruledOut => "VE found that everything else the text says rules the claim out."
  | .notSettled => match situation with
    | some s => "VE found that everything else the text says does not settle the claim: in this situation, it " ++
        s!"depends on what the text leaves unsaid: {s}."
    | none => ""
  | .unknown r => VE.Ask.leadText .unknown ++ (if VE.Ask.reasonText r == "" then "" else " " ++ VE.Ask.reasonText r)

/-- The support answer's lines (SR 3; 12, choice 5): ask's grouping and reading clauses, exactly. `v` is the
    adapter's view of the reduced context (6.4), so `VE.Ask.groups v.ids v.rows v.key` groups the rows by lead and,
    for yes or no, by the reduced cited sources. Each group gives `verdict` of its rows' verdict (`verdictOf`); an
    UNKNOWN group gives one line per distinct reason of its rows, in order, as ask's `reasonLines`. The situation of a
    `notEnough` or `notSettled` line is its group's first witness row's (S1: `query = .refuted`; S2: `split`),
    followed by `VE.Ask.readingSuffix` of every open set's reading of that row (`VE.Ask.named (VE.Ask.assignment
    v.ids r)`), as ask's witness lines are, whether or not the rows' verdicts differ. With two or more groups, each
    line starts with "If " ++ the group's readings of the relevant sets (`VE.Ask.readingClause` over
    `VE.Ask.named g.on`, joined by " and ") ++ ", ", as ask's R1 lines do. Empty lines are dropped. -/
def supportLines (n : Naming) (ctx : VE.Ask.Context) (v : VE.Ask.View) (verdictOf : VE.Ask.Row → Support) :
    List String

/-- † PE-R8: the readings line for one target part with an active set: its quote and the names of the candidates
    that hold the target. -/
def underLine (U : Units) (u : String × List String) : Option String := do
  let q ← sideText U [.part u.1]
  pure s!"This holds only under these readings of {quoted q}: {VE.Senses.andList u.2}."

/-- † PE-R8: the line for the parts of the link's unit that no link names and that are not inert. -/
def scopeLine (U : Units) (is : List String) : Option String := do
  if is.isEmpty then none
  let qs ← is.mapM fun i => sideText U [.part i]
  pure (s!"The quotes above leave out {VE.Senses.andList (qs.map quoted)} from the same sentence, " ++
    "which may limit what they say.")

/-- † PE-R8: a link's lines. Withheld (`[]`) when some target part's set has no candidate that holds the target;
    otherwise `says`, then `verdict` when not empty, then one `underLine` per target part with a set, then
    `scopeLine`. Empty lines are dropped. -/
def linkLines (U : Units) (B : Block) (L : Link) (says verdict : String) : List String :=
  let su := shownUnder U L
  if su.any (·.2.isEmpty) then []
  else ([says, verdict] ++ su.filterMap (underLine U) ++ (scopeLine U (unlinkedActive U B L)).toList).filter
    (· ≠ "")

/-- † A target with no active set and a unit with no unlinked active part keep 2.3's lines as they were. -/
theorem linkLines_plain (U : Units) (B : Block) (L : Link) (s v : String) (h1 : shownUnder U L = [])
    (h2 : unlinkedActive U B L = []) : linkLines U B L s v = [s, v].filter (· ≠ "")

/-- † A withheld link shows no line. -/
theorem linkLines_withheld (U : Units) (B : Block) (L : Link) (s v : String)
    (h : ∃ u ∈ shownUnder U L, u.2 = []) : linkLines U B L s v = []
end VE.Purposes.English
```

An empty line is never shown. `.notChecked .denied` has none, because a denial supports nothing. A line whose unit
has no display number, or whose situation Lean could not word, is empty: the relay then shows the `says` line alone,
never a guessed number. `VE.Senses.andList` and `VE.Ask.citationText` are existing joiners; no third one is written.

Every line (9.7). Sentence 1 is `u1`, sentence 3 is `u3` and sentence 5 is `u5`'s; no cited part is in the target's
sentence unless the row says so; the situation is shown as `S`. Rows marked † are new in draft 2 and derived by hand
(11.1); the others were computed by the stub:

| `Support` | The line |
|---|---|
| `alone` | VE checked that this reason is enough to conclude the claim. |
| `together ["u1"] []` | VE checked that this reason is enough to conclude the claim together with sentence 1. |
| `together ["u1","u3"] ["adult"]` | VE checked that this reason is enough to conclude the claim together with sentences 1 and 3 and the definition of adult. |
| `together [] ["adult","minor"]` | VE checked that this reason is enough to conclude the claim together with the definitions of adult and minor. |
| † `together ["u5.p1","u5.p3"] []` (E-b) | VE checked that this reason is enough to conclude the claim together with sentence 5. |
| † F3's l1, `together ["c.p5"] []`, `c.p5` in the target's sentence (E-c) | VE checked that this reason is enough to conclude the claim together with "values that are merely imposed on us by others seem likely to be brittle." |
| `without ["u1"] []` | VE checked that the claim follows from sentence 1 without this reason. |
| † `without [] []` (E-a) | VE checked that the claim follows without this reason, from nothing else the text says. |
| † F3's l1, `without ["c.p5"] []`, `c.p5` in the target's sentence (E-c) | VE checked that the claim follows from "values that are merely imposed on us by others seem likely to be brittle." without this reason. |
| `notEnough` | VE found that this reason is not enough: in this situation, everything else the text says is true and the claim is false: S. |
| `ruledOut` | VE found that everything else the text says rules the claim out. |
| `notSettled` | VE found that everything else the text says does not settle the claim: in this situation, it depends on what the text leaves unsaid: S. |
| `unknown .noResult` | VE could not decide this. VE found neither a proof nor a situation where it fails, within its limits. |
| `unknown .tooMany` (function level only: no support row has it, because past 64 choices the request is refused, SR 13, 7.3) | VE could not decide this. There are more than 64 ways to read this document's open sentences. VE did not check them all. |
| `unknown .conflict` | VE could not decide this. |
| `notChecked .purpose` | VE does not check whether it serves this purpose. |
| `notChecked .ruleTarget` | VE does not check whether a reason is good enough for a rule. |
| `notChecked .noFormula` | VE cannot check this reason yet: a side has no formal reading. |
| `notChecked .readings` | VE cannot check this reason yet: a side has more than one reading. |
| `notChecked .denied`; `together ["u9"] []` with `u9` unnumbered; `notEnough` or `notSettled` with no situation | (empty) |

## 3. Nonfactivity: `VE.Route.Admission.Kind.inert` (owner: route admission; PE-1)

A new file, `lean/VE/Route/Inert.lean`, in route admission's namespace. `Route/Admission.lean` is not edited. The
predicate is positive (A2): it lists the kinds whose content no route ever reads as a premise or a rule, instead of
refusing only `asserted` (draft 1's `factiveOk` let `norm` and `definition` through).

```lean
import VE.Route.Admission
import VE.Norms.Admission
import VE.Readings.Wire

namespace VE.Route.Admission

/-- A kind whose content is never a premise and never a rule. -/
def Kind.inert : Kind → Bool
  | .explanation | .exposition | .«example» | .analogy | .«meta» => true
  | _ => false

theorem Kind.inert_active (k : Kind) (h : k.inert = true) :
    k ≠ .asserted ∧ k ≠ .norm ∧ k ≠ .definition ∧ k.quoted = false

/-- Admission's leaf provenance: no admitted node names an inert unit, neither as the unit it formalises nor as the
    unit of a bridge leaf. -/
theorem inert_unnamed (D : Doc) (w : WireNode) (i : String)
    (hi : ∀ x ∈ D.units, x.id = i → x.kind.inert = true) (hw : NodeAdmitted D w) :
    w.unit ≠ some i ∧ ∀ a, parseLabel w.claim.label ≠ some (.bridge a i)

/-- The same for every node of an admitted document, so no assumption of its report comes from an inert unit. -/
theorem admit_inert (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (res : Admitted) (h : admitDocument profiles environment rv j = .ok res) (i : String)
    (hi : ∀ x ∈ res.doc.units, x.id = i → x.kind.inert = true) :
    ∀ w ∈ res.wires, w.unit ≠ some i ∧ ∀ a, parseLabel w.claim.label ≠ some (.bridge a i)

/-- The norm-role table gives an inert kind no role: its norm content is never a rule. -/
theorem normRole_inert (k : Kind) (c : Json) (h : k.inert = true) :
    ∃ m, VE.Norms.Admission.normRole k c = .error m

/-- The readings route never puts an inert unit's or candidate's content in force. -/
theorem inForce_inert (k : Kind) (s : String) (hs : renderKind k = .str s) (h : k.inert = true)
    (c : VE.Compose.Content) : VE.Readings.Wire.inForce (some s) c = false
end VE.Route.Admission
```

Why these four theorems cover "never a premise or a rule":
- On the W2 route, a premise is an admitted leaf. An `asserted` leaf must be an `asserted` unit's formula, and a
  bridge leaf must name a quoted unit (`LeafAdmitted`, `Route/Admission.lean:326`). Every other leaf names no unit.
  `inert_unnamed` and `admit_inert` say exactly this for inert units.
- A rule comes from norm content, which `normRole` makes active only under kind `norm`, or quoted under a quoted kind
  (`Norms/Admission.lean:25`). `normRole_inert` says an inert kind gets neither.
- On the readings route, a unit's or a candidate's content is in force only under `asserted`, `norm` or a rights kind
  (`Readings/Wire.lean:235`). `inForce_inert` says an inert kind is none of them.
- The wrapper equality `checkDocPurposes_base` (5.3) is *not* used for this guarantee (Astra round 2).

## 4. Well-formedness (`lean/VE/Purposes/WellFormed.lean`, PE-1, layer 2)

### 4.1 The input: the checked units and parts

Purposes compiles nothing (A3). Its input is a projection of the document model's checked view (5.1): every unit and
part *after* the status fold, with its W2 kind, its status, its parent (for a part of a MIXED unit), its formula when
its content is one, and the kinds of the candidates of an active reading set on it.

```lean
namespace VE.Purposes
open VE.Route.Admission (Kind)

structure Part where
  id         : String
  span       : Nat × Nat
  kind       : Kind
  status     : String          -- the W2 status name: CHECKED, OPEN, LABELLED or UNFORMALISED
  parent     : Option String   -- the MIXED unit a part belongs to
  formula    : Option VE.Formula
  candidates : List Kind       -- the kinds of the candidates of an active reading set on it; [] when none
  readings   : List String := []  -- † PE-R8: those candidates' names, in the same order
  deriving Repr

structure Units where
  source : String
  parts  : List Part
  packSources : List String := []  -- † PE-R11: the unit and part ids the list's pack premises in `X` are sourced to
  deriving Repr

def Units.find? (U : Units) (i : String) : Option Part := U.parts.find? (·.id == i)
def Units.kind? (U : Units) (i : String) : Option Kind := (U.find? i).map (·.kind)
```

### 4.2 The parts of the check

```lean
def Ref.partId? : Ref → Option String
  | .part i => some i
  | .mention _ => none

def Link.partIds (L : Link) : List String := L.marker :: (L.reason ++ L.target).filterMap Ref.partId?

/-- Plan D3: the sides in W2's slot order, `causal r c e`. -/
def Link.slots (L : Link) : List Ref × List Ref :=
  match L.relation with
  | .because => (L.reason, L.target)
  | .inOrderTo => (L.target, L.reason)

def sideOfKind (U : Units) (s : List Ref) (k : Kind) : Bool :=
  !s.isEmpty && s.all fun r => match r.partId? with
    | some i => U.kind? i == some k
    | none => true

def markerAgrees (U : Units) (L : Link) : Bool :=
  match U.kind? L.marker with
  | some (.causal r c e) => r == L.relation.wire && sideOfKind U L.slots.1 c && sideOfKind U L.slots.2 e
  | _ => false

/-- PE-1: the marker and every side are distinct parts of one MIXED unit. PE-4 replaces it (A3). -/
def sameUnit (U : Units) (L : Link) : Bool :=
  (L.reason ++ L.target).all (·.partId?.isSome) && decide L.partIds.Nodup &&
  match (U.find? L.marker).bind (·.parent) with
  | some p => L.partIds.all fun i => (U.find? i).bind (·.parent) == some p
  | none => false

/-- SR 6: each side's parts are in source order and each part starts where the previous one ends. A mention fails
    it; PE-4 replaces it on resolved sides, as it replaces `sameUnit` (A3). -/
def sideAdjacent (U : Units) (s : List Ref) : Bool :=
  match s.mapM fun r => r.partId? >>= U.find? with
  | some ps => ps.all (fun p => p.span.1 ≤ p.span.2) && (ps.zip ps.tail).all fun (a, b) => a.span.2 == b.span.1
  | none => false

def sidesAdjacent (U : Units) (L : Link) : Bool := sideAdjacent U L.reason && sideAdjacent U L.target

/-- Other affirmed links with the same relation and target and a *different* reason list (A4). -/
def rivals (B : Block) (L : Link) : List Link :=
  B.links.filter fun M => M.id != L.id && M.polarity == .affirmed && M.relation == L.relation &&
    M.target == L.target && M.reason != L.reason

/-- A4 and SR 5 (E-d): `sole` is refused against a rival, and against any other affirmed link with the same relation
    and target whose share is `partly` or `notSole` ("only because B" with "not only because B"). -/
def shareOk (B : Block) (L : Link) : Bool :=
  match L.share with
  | .sole => (rivals B L).isEmpty && B.links.all fun M => M.id == L.id || M.polarity != .affirmed ||
      M.relation != L.relation || M.target != L.target || M.share == .plain || M.share == .sole
  | _ => true

/-- Under `purposes@0` every part of kind `causal because|in order to _ _` marks some link. -/
def markersLinked (U : Units) (B : Block) : Bool :=
  U.parts.all fun p => match p.kind with
    | .causal r _ _ => r == "prevents" || B.links.any (·.marker == p.id)
    | _ => true

def covered (U : Units) (s : List Ref) : Bool :=
  s.all fun r => match r.partId? >>= U.find? with
    | some p => p.status == "CHECKED" || p.status == "OPEN"
    | none => false

/-- The side the text does not state: a purpose, or the reason of a denied link (plan D8a). -/
def unstated (L : Link) : List Ref :=
  if L.relation == .inOrderTo || L.polarity == .denied then L.reason else []

/-- D8a, positively: every part on the unstated side, and every candidate of an active reading set on it, is inert.
    A mention there is refused until PE-4 resolves it. -/
def nonfactive (U : Units) (L : Link) : Bool :=
  (unstated L).all fun r => match r.partId? >>= U.find? with
    | some p => p.kind.inert && p.candidates.all Kind.inert
    | none => false

/-- Plan D4: a LABELLED marker marks a link whose two sides are CHECKED or OPEN. -/
def markerHonest (U : Units) (B : Block) : Bool :=
  U.parts.all fun p => p.status != "LABELLED" || !(B.links.any (·.marker == p.id)) ||
    B.links.any fun L => L.marker == p.id && covered U L.reason && covered U L.target

/-- † PE-R11 (plan D8a): no pack premise is sourced to a part on the unstated side, or to that part's unit, which
    holds its bytes. -/
def packsInert (U : Units) (L : Link) : Bool :=
  (unstated L).all fun r => match r.partId? >>= U.find? with
    | some p => !(U.packSources.contains p.id) && !(p.parent.any U.packSources.contains)
    | none => false

/-- † PE-R8: the kind the marker's slot gives the target (`slots`: the second slot for `because`, the first for
    `in order to`). -/
def targetKind (U : Units) (L : Link) : Option Kind :=
  match U.kind? L.marker with
  | some (.causal _ c e) => some (if L.relation == .because then e else c)
  | _ => none

/-- † PE-R8: a candidate of a target part's active set holds the target when its kind is that kind. -/
def holdsTarget (U : Units) (L : Link) (k : Kind) : Bool := targetKind U L == some k

/-- † PE-R8: for each target part with an active set, the names of the candidates that hold the target. -/
def shownUnder (U : Units) (L : Link) : List (String × List String) :=
  (L.target.filterMap fun r => r.partId? >>= U.find?).filterMap fun p =>
    if p.candidates.isEmpty then none
    else some (p.id, ((p.readings.zip p.candidates).filter (holdsTarget U L ·.2)).map (·.1))

/-- † PE-R8: the parts of the marker's unit that no link of the block names and whose kind is not inert, in view
    order: a scope the link's quotes may leave out. -/
def unlinkedActive (U : Units) (B : Block) (L : Link) : List String :=
  match (U.find? L.marker).bind (·.parent) with
  | some u => (U.parts.filter fun p => p.parent == some u && !p.kind.inert &&
      !(B.links.any fun M => M.partIds.contains p.id)).map (·.id)
  | none => []
```

Under `purposes@0`, `markersLinked` refuses a part of kind `causal because …` or `causal in order to …` that marks
no link. So another family's causal "because" that this plan does not link (u0133.s03, inside a definition's body)
cannot carry main's `causal` label under `purposes@0`: it takes its owner's kind, or `unformalised` with its reason.
This is a refusal with a working route (pe-rev, C point; plan 8), and the check is unchanged.

### 4.3 The check, in its fault order

```lean
def check (U : Units) (B : Block) : Except String Unit := do
  unless B.links.length ≤ maxLinks do throw s!"ResourceLimit: purposes links exceed {maxLinks}"
  unless decide (B.links.map (·.id)).Nodup do throw "InvalidPurposes: two links have the same id"
  for L in B.links do
    for i in L.partIds do
      unless (U.find? i).isSome do throw s!"InvalidPurposes: link {L.id} names unknown unit {i}"
    unless sameUnit U L do throw s!"InvalidPurposes: link {L.id} must join distinct parts of one unit"
    unless sidesAdjacent U L do
      throw s!"InvalidPurposes: link {L.id} has a side whose parts are not adjacent and in order"
    unless markerAgrees U L do
      throw s!"InvalidPurposes: unit {L.marker} is not marked as this link's reason or purpose"
    unless nonfactive U L do
      throw s!"InvalidPurposes: link {L.id} would make a purpose or a denied reason a premise or a rule"
    unless packsInert U L do  -- † fault 6a, PE-R11
      throw s!"InvalidPurposes: link {L.id} has a side the text does not state, and a pack takes a premise from it"
    if L.polarity == .denied && L.share != .plain then
      throw s!"InvalidPurposes: link {L.id} denies a reason and also says how much of the reason it is"
    unless shareOk B L do
      throw s!"InvalidPurposes: link {L.id} says this is the only reason, and the text gives another"
  unless markersLinked U B do throw "InvalidPurposes: a unit marked as a reason or purpose has no link"
  unless markerHonest U B do
    throw "InvalidPurposes: link words are counted as covered, but what they link is not formalised"
```

### 4.4 What the check decides

```lean
def WellFormed (U : Units) (B : Block) : Prop :=
  B.links.length ≤ maxLinks ∧ (B.links.map (·.id)).Nodup ∧
  (∀ L ∈ B.links, (∀ i ∈ L.partIds, (U.find? i).isSome = true) ∧ sameUnit U L = true ∧
    sidesAdjacent U L = true ∧ markerAgrees U L = true ∧ nonfactive U L = true ∧ packsInert U L = true ∧
    (L.polarity = .denied → L.share = .plain) ∧ shareOk B L = true) ∧
  markersLinked U B = true ∧ markerHonest U B = true

/-- The characterization; its right side has SR 6's conjunct `sidesAdjacent` and (†, PE-R11) `packsInert`. -/
theorem check_ok_iff (U : Units) (B : Block) : check U B = .ok () ↔ WellFormed U B

theorem sameUnit_parent (U : Units) (L : Link) (h : sameUnit U L = true) :
    (∀ r ∈ L.reason ++ L.target, ∃ i, r = .part i) ∧ L.partIds.Nodup ∧
      ∃ p, ∀ i ∈ L.partIds, ∃ x, U.find? i = some x ∧ x.parent = some p

/-- SR 6: a side passes exactly when its refs are parts of the view, each part's span is ordered, and each part
    starts where the previous one ends. -/
theorem sideAdjacent_iff (U : Units) (s : List Ref) :
    sideAdjacent U s = true ↔ ∃ ps, (s.mapM fun r => r.partId? >>= U.find?) = some ps ∧
      (∀ p ∈ ps, p.span.1 ≤ p.span.2) ∧ ∀ (i : Nat) (h : i + 1 < ps.length), ps[i].span.2 = ps[i + 1].span.1

/-- A4 and SR 5: only `sole` constrains other links. It is refused against an affirmed link with the same relation
    and target and a different reason list, or with the same reason list and the share `partly` or `notSole`;
    `plain`, `partly` and `notSole` need no other link. -/
theorem shareOk_iff (B : Block) (L : Link) :
    shareOk B L = true ↔
      (L.share = .sole → ∀ M ∈ B.links, M.id ≠ L.id → M.polarity = .affirmed → M.relation = L.relation →
        M.target = L.target → M.reason = L.reason ∧ (M.share = .plain ∨ M.share = .sole))

theorem markerAgrees_kind (U : Units) (L : Link) (h : markerAgrees U L = true) :
    ∃ c e, U.kind? L.marker = some (.causal L.relation.wire c e) ∧
      (∀ i ∈ L.slots.1.filterMap Ref.partId?, U.kind? i = some c) ∧
      (∀ i ∈ L.slots.2.filterMap Ref.partId?, U.kind? i = some e)

theorem unstated_eq (L : Link) :
    unstated L = if L.relation = .inOrderTo ∨ L.polarity = .denied then L.reason else []

/-- D8a exactly: the unstated side is all parts, each inert, each with only inert candidates. -/
theorem nonfactive_iff (U : Units) (L : Link) :
    nonfactive U L = true ↔ ∀ r ∈ unstated L, ∃ i p, r = .part i ∧ U.find? i = some p ∧
      p.kind.inert = true ∧ ∀ k ∈ p.candidates, k.inert = true

theorem markerHonest_labelled (U : Units) (B : Block) (h : markerHonest U B = true) (p : Part)
    (hp : p ∈ U.parts) (hl : p.status = "LABELLED") (hm : ∃ L ∈ B.links, L.marker = p.id) :
    ∃ L ∈ B.links, L.marker = p.id ∧ covered U L.reason = true ∧ covered U L.target = true

/-- † PE-R11: no part on the unstated side, and not its unit, is a pack premise's source. -/
theorem packsInert_iff (U : Units) (L : Link) :
    packsInert U L = true ↔ ∀ r ∈ unstated L, ∃ i p, r = .part i ∧ U.find? i = some p ∧
      p.id ∉ U.packSources ∧ ∀ u, p.parent = some u → u ∉ U.packSources

/-- † PE-R11: with no pack on the list, the conjunct adds nothing beyond `nonfactive`'s parts. -/
theorem packsInert_nil (U : Units) (L : Link) (h : U.packSources = []) (hn : nonfactive U L = true) :
    packsInert U L = true

/-- † PE-R8: exactly the target parts with an active set, each with exactly the names of its candidates whose kind is
    the target's slot kind. The view gives one name per kind (`checkDocSetsView_readings`, 5.1), so no candidate is
    cut by the zip. -/
theorem shownUnder_iff (U : Units) (L : Link) (i : String) (ns : List String) :
    (i, ns) ∈ shownUnder U L ↔ ∃ r ∈ L.target, ∃ p, r = .part i ∧ U.find? i = some p ∧ p.candidates ≠ [] ∧
      ns = ((p.readings.zip p.candidates).filter fun x => targetKind U L = some x.2).map (·.1)

/-- † PE-R8: a part is listed exactly when it is in the marker's unit, is not inert, and no link names it. -/
theorem unlinkedActive_iff (U : Units) (B : Block) (L : Link) (i : String) :
    i ∈ unlinkedActive U B L ↔ ∃ u p, (U.find? L.marker).bind (·.parent) = some u ∧ p ∈ U.parts ∧ p.id = i ∧
      p.parent = some u ∧ p.kind.inert = false ∧ ∀ M ∈ B.links, i ∉ M.partIds
end VE.Purposes
```

Together with section 3, `nonfactive_iff` gives the guarantee in plain words: when the block is well formed, no part
on a purpose side or a denied reason's side, and no reading of it, is ever a premise or a rule of the document.
† (PE-R11) Section 3's theorems cover admission's leaves, norm roles and the readings route; packs put premises in
`X` outside them. `packsInert_iff` covers the packs, given the obligation that every pack premise names its source
(`packSources_complete`, 5.1), which each `layerCovers` entry of `purposes@0` whose list holds a pack carries (5.3).
`shownUnder` and `unlinkedActive` are not conjuncts: they decide only which lines show (2.3), so no well-formed
block changes. The
link words of a LABELLED marker are covered only when both sides are expressed (`markerHonest_labelled`). A side's
quote is the text of exactly the parts the link lists (`sideAdjacent_iff` here, `sideText_eq` in 2.3). `sideText_eq`
is in `English.lean` (layer 4, PE-2), because `sideText` reads `VE.Ask.bytesOf`; PE-1 proves `sideAdjacent_iff` and
the new conjunct of `check_ok_iff`.

## 5. The document mode under `purposes@0` (PE-2)

### 5.1 The checked view (owner: the document model, `VE.Service.Document`; DRI 2(d))

One refactor in the document-mode queue, delivered before PE-2 (plan order step 3). It changes no answer.

```lean
namespace VE.Service.Document

/-- The typed checked document after the status fold (scope's governor fold included): the answer's rows, its source,
    and each unit under an active reading set with its candidates' kinds. NEW under W2. -/
structure CheckedView where
  source : String
  rows : List RowUnit
  candidates : List (String × List VE.Route.Admission.Kind)
  /-- † PE-R8: the same sets' candidate names, in the same order as `candidates`. -/
  readings : List (String × List String) := []
  /-- † PE-R11: the unit and part ids that the premises the list's packs put in `X` name as their source. -/
  packSources : List String := []

/-- One run of the document mode, two outputs: the answer and its view. -/
def checkDocSetsView (j : Json) : Except String (Json × CheckedView)

/-- The kinds of each active reading set's candidates, from the same `Loader.activeOf` the fold reads. -/
def activeKinds (j : Json) : Except String (List (String × List VE.Route.Admission.Kind))

/-- The refactor changes no answer. -/
theorem checkDocSetsView_answer (j : Json) : (checkDocSetsView j).map (·.1) = checkDocSets j

/-- The view is the answer: its rows render to the answer's `units`, and its source is the answer's. -/
theorem checkDocSetsView_rows (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    a.getObjValD "units" = toJson (V.rows.map unitJson) ∧ a.getObjValD "source" = .str V.source

theorem checkDocSetsView_candidates (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    activeKinds j = .ok V.candidates

/-- † PE-R8: one name per candidate kind, for the same units in the same order. -/
theorem checkDocSetsView_readings (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    V.readings.map (·.1) = V.candidates.map (·.1) ∧
      ∀ i ns ks, (i, ns) ∈ V.readings → (i, ks) ∈ V.candidates → ns.length = ks.length

/-- † PE-R11: a list with no pack gives no pack source. -/
theorem checkDocSetsView_packs (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V))
    (hn : ∀ p ∈ ["weighing@0", "attitudes@0", "scales@0", "events@0"], p ∉ profilesOf j) :
    V.packSources = []
end VE.Service.Document
```

† **Pack sources (PE-R11; plan D8a).** `packSources` is empty on a list with no pack. For a list holding a pack
(`weighing@0`, `attitudes@0`, `scales@0`, `events@0`), its content is the pack owner's to supply, and the obligation
`packSources_complete` is stated here, not designed: every premise the pack's assembly puts in `X` for the request
names the unit or part it formalises, and that id is in `packSources`. A premise with no source cannot meet it. Its
exact statement is written over the pack's own assembly function by the pack's owner when its list is first covered
(plan 8, request rows); until then no `layerCovers` entry of `purposes@0` names a list holding that pack (5.3), so
the layer rule refuses it and no pack premise reaches a `purposes@0` answer unchecked.

### 5.2 Front-matter keys (owner: W2's loader, `VE.Discourse.Loader`)

```lean
namespace VE.Discourse.Loader

/-- The keys a listed profile admits; Python's `_split` decides `scope` by hand today. -/
def profileKeys : List (String × String) := [("scope@0", "scope"), ("purposes@0", "purposes")]

def documentMetadataFor (format : String) (profiles : List String) : List String :=
  documentMetadata format ++ (profileKeys.filter (profiles.contains ·.1)).map (·.2)

theorem purposes_key_iff (format : String) (profiles : List String)
    (hf : "purposes" ∉ documentMetadata format) :
    "purposes" ∈ documentMetadataFor format profiles ↔ "purposes@0" ∈ profiles
end VE.Discourse.Loader
```

A Lean main exports `documentMetadataFor`'s table to the generated `ve/document_metadata.json`; Python's `_split`
reads it and loses its hand-written set (plan 6).

### 5.3 The wrapper (`lean/VE/Service/DocumentPurposes.lean`)

```lean
namespace VE.Service.Document

/-- The view's rows as purposes reads them; a rights kind is refused, because the profile row does not admit
    `rights@0` yet. -/
def purposesUnits (V : CheckedView) : Except String VE.Purposes.Units := do
  let parts ← V.rows.mapM fun r => match r.kind with
    | .route k =>
      let formula := match r.content with
        | some (.formula f) => some f
        | _ => none
      pure ({ id := r.id, span := r.span, kind := k, status := r.status.name, parent := r.parent, formula,
              candidates := (V.candidates.lookup r.id).getD [],
              readings := (V.readings.lookup r.id).getD [] } : VE.Purposes.Part)  -- † PE-R8
    | .rights _ => throw (unavailable "purposes@0 with a rights kind needs its composed route")
  pure { source := V.source, parts, packSources := V.packSources }  -- † PE-R11

/-- The request without the `purposes` block and without `purposes@0` in the environment's profiles. -/
def lowerPurposes (j : Json) : Json
/-- The front matter's `purposes` member, `null` when absent (which `decodeBlock` refuses, 7.1). -/
def purposesBlockJson (j : Json) : Json
/-- The `purposes` section (5.4). -/
def purposesSection (U : VE.Purposes.Units) (B : VE.Purposes.Block) (a : Json) : Json

def checkDocPurposes (j : Json) : Except String Json :=
  if "purposes@0" ∈ profilesOf j then do
    let _ ← VE.Compose.gateOf VE.Compose.profileTable (profilesOf j)
    let (a, V) ← checkDocSetsView (lowerPurposes j)
    let U ← purposesUnits V
    let B ← VE.Purposes.decodeBlock (purposesBlockJson j)
    VE.Purposes.check U B
    pure (a.setObjVal! "purposes" (purposesSection U B a))
  else checkDocSets j

theorem checkDocPurposes_absent (j : Json) (h : "purposes@0" ∉ profilesOf j) :
    checkDocPurposes j = checkDocSets j

/-- No premise, verdict, status or coverage row changes: the answer is the base answer plus `purposes`. -/
theorem checkDocPurposes_base (j r : Json) (hp : "purposes@0" ∈ profilesOf j) (h : checkDocPurposes j = .ok r) :
    ∃ a V U B, checkDocSetsView (lowerPurposes j) = .ok (a, V) ∧ purposesUnits V = .ok U ∧
      VE.Purposes.decodeBlock (purposesBlockJson j) = .ok B ∧ VE.Purposes.WellFormed U B ∧
      r = a.setObjVal! "purposes" (purposesSection U B a)
end VE.Service.Document
```

`checkDocPurposes_absent` is proved in the stub (11). The profile row: `purposes@0` requires `documents@1`, its slot
is the document mode's outer wrapper (after scope), and `checkDocPurposes_base` is its composition proof for each
admitted combination. PE-2 admits none of `rights@0`, `alternatives@0`, `ve.discourse@1`, `events@0` or
`speech-acts@0`; later batches extend the row in landing order (plan 5). † (pe-rev) PE-3 adds `judgments@0`, the
first batch to emit D6 (a)'s limiting candidate (PE-R10, plan 2.5, with its composes argument); PE-7b adds only
`events@0`. PE-3's entries cover the lists holding `documents@1`, `judgments@0` and `readings@1` (plan 2.5). A list
holding `attitudes@0`, `hedges@0`, `modality@0`, `scales@0`, `weighing@0` or `commitments@0` is
named by no batch here, so the layer rule refuses it until a batch names it with its argument. An entry whose list
holds a pack also carries `packSources_complete` for that pack (5.1, PE-R11).

### 5.4 The `purposes` section, its binding and its contract

```json
"purposes": {
  "purposes_id": "<64 hex digits>",
  "links": [
    {"id": "l1", "relation": "in order to", "polarity": "affirmed", "share": "plain",
     "reason": ["u0146.s01.p3"], "target": ["u0146.s01.p1"], "marker": "u0146.s01.p2",
     "support": {"verdict": "not_checked", "why": "purpose"},
     "lines": ["The text gives this purpose for \"We want Claude to figure out the most plausible interpretation of a query\": \"give the best response.\"",
               "VE does not check whether it serves this purpose."]}],
  "markers": [{"unit": "u0146.s01.p2", "links": ["l1"]}]
}
```

- One row per link, in block order. The sides are part ids (PE-4 adds resolved mentions). `lines` are Lean's: `says`,
  then `verdict` when it is not empty; † (pe-rev, PE-R8) they are `linkLines` (2.3): empty when some target part's set
  has no candidate that holds the target, and followed by `underLine` and `scopeLine` where they apply.
- † `under` (PE-R8): present when `shownUnder` is not empty, `[{"part": p, "readings": [names]}, …]`, its value. The
  renderer shows the row's lines only beside those readings of `p`; Python decides nothing. The binding (below)
  checks it.
- `support` is `renderSupport` of `notChecked w` when `eligible` refuses the link (6.3). For an eligible link it is
  `{"ask": {"target": t, "reasons": [...]}}`, the question PE-5 relays, and the link has no second line until
  that answer arrives (12, choice 4).
- `markers`: each marker part once, with the links it marks, in block order. `ve/document/render.py` prints the
  marked links' `says` lines for that part instead of W2's kind description. † (PE-R8) A row with `under` is printed
  only beside those readings, never unconditionally, and a marker whose links' `lines` are all empty keeps W2's kind
  description.
- `purposes_id` is the SHA-256 of the canonical JSON text of `{"block": renderBlock B, "document_id": <the base
  answer's document_id>}`, the same canonical serialisation the document identities use. The base answer runs on the
  lowered request, so the block is bound here (12, choice 6).
- **Binding** (Python relay, ROUTE-RECIPE step 7): every link id, side id and marker id equals the request block's;
  every `markers` entry names a marker of the block; no row is empty, duplicated or extra; `support` decodes; `lines`
  are strings. † (PE-R8) `under` has exactly one entry per target part with an active set (none when there is no
  such part), each `part` one of the row's target parts and each name a candidate of that part's set; and `lines`
  is empty exactly when some entry's `readings` is empty. Anything else is `CheckerUnavailable`.
- **rd-9 inventory** (D9, DRI 3(d)): the member's rows are added to `tests/test_relay_binding_inventory.py`, each bound
  and fuzzed.
- **Contract** (C6, DRI 3(c)): the wire-contract owner ships the diagnostics contract of section 7 in shadow mode, off
  the verdict and identity paths, before PE-2 admits the profile.

## 6. The support check (PE-5)

### 6.1 The reduced support context (owner: question-answering, `VE.Ask`; DRI 2(b))

The target's question is asked of the document without the target unit's assertion (E1). Every assertion entry
sourced to the target is removed, and every other authored unit stays, a formula-equal statement included (Astra
round 3). The rules, fills, pairs and background stay exactly as they are.

**One shared adapter (synthesis round 2).** `VE.Ask.withoutAssertion D t` is the singleton case `withoutUnits [t]` of
the one shared adapter `VE.Ask.withoutUnits N X` (with `replayReduced` and `withoutUnitsPlain`). Whichever of
PE-1/PE-2 and definitions' PD-2 lands first builds the adapter; the other reuses it. There is no second copy.

**Ask's case (Q1, SR 7).** The support question goes to whichever of ask's three adapters ask selects for the
document (`VE.Ask.Run.routeOfDocument`): the plain adapter (`relational-fol@0`, no norms, no reading set;
`Ask/PlainWire.lean`), the zero-set adapter (`norms@0` under `norm-defaults@0`, no `readings@1`; `Ask/ZeroWire.lean`)
or the enumerated adapter (`readings@1`; `Ask/Wire.lean`). A document with no reading set is never sent to the
enumerated adapter. The query's units are the flattened parts: the loader flattens a MIXED unit's parts into units
(`ve/document/source.py:94`), so a part id is a `Source.unit` id, and removing the target removes the target part
alone; the reason parts and the rest of its sentence stay.

**One reduction.** It is defined once, over sourced premises (`dropTarget`). Each adapter's reduced premises are its
own sourced premises filtered by it, with each premise's source kept beside it, so the positions a certificate uses
name their sources exactly as ask's `cited` reads them.

**No soft premise (SR 11).** Support is answered only through ask's three adapters, and on each of them the soft
premises (the exception and coherence premises of a soft chain) are empty:
- the enumerated adapter admits only `normsShaped` documents (`admitNDFull`, `Readings/UnspecifiedWire.lean:316`), so
  every row's soft premises are `choiceX N c = []` (`choiceX_normsShaped`, `Readings/SoftDefaults.lean:47`, with
  `normsShaped_of_ND`, `Readings/VerdictsWire.lean:392`);
- the plain and zero-set adapters carry no soft premises in their types (`PlainParts`; `ZeroParts`, over `SourceU`).

So no support request reaches a soft premise, and 6.2's theorems need none. A soft document's support request gets
the refusal ask gives the same case, word for word (7.3 adds no text; fixture S10). Support on soft documents waits
until ask serves them; extending ask is question-answering's work (DRI 2(b)), not this batch's.

```lean
namespace VE.Ask
open VE.Readings

/-- SR 7: the one reduction, the sourced premises without those sourced to the target `t`. -/
def dropTarget (t : String) (as : List (Source × VE.Formula)) : List (Source × VE.Formula) :=
  as.filter (·.1 != .unit t)

/-- Exactly the target's entries go: every other entry stays, in order. -/
theorem mem_dropTarget (t : String) (as : List (Source × VE.Formula)) (x : Source × VE.Formula) :
    x ∈ dropTarget t as ↔ x ∈ as ∧ x.1 ≠ .unit t

/-- No premise of the support question comes from the target. -/
theorem dropTarget_target (t : String) (as : List (Source × VE.Formula)) : ∀ x ∈ dropTarget t as, x.1 ≠ .unit t

/-- VE's own premises (definitions, background, pairs, fills, rules) are never a unit's, so the reduction commutes
    with ask's `sourced`. -/
theorem sourced_dropTarget (U : UDoc) (t : String) (as : List (Source × VE.Formula)) :
    dropTarget t (sourced U as) = sourced U (dropTarget t as)

/-! The plain adapter: Γ is the Background, then the asserted units' formulas in unit order. -/

def PlainParts.without (p : PlainParts) (t : String) : PlainParts := { p with units := p.units.filter (·.1 != t) }

/-- Its reduced premises are its premises filtered, each with its source. -/
theorem PlainParts.sourced_without (p : PlainParts) (t : String) : (p.without t).sourced = dropTarget t p.sourced

/-- Source to formula: the reduced case's sources and Γ are the two columns of the filtered list, over the same
    environment and conclusion. -/
theorem PlainParts.without_columns (p : PlainParts) (t : String) :
    (p.without t).sources = (dropTarget t p.sourced).map (·.1) ∧
    (p.without t).Γ = (dropTarget t p.sourced).map (·.2) ∧ (p.without t).V = p.V ∧ (p.without t).ψ = p.ψ

/-! The zero-set adapter: Γ is the asserted units' formulas; the premises are `premisesU U Γ`. -/

def ZeroParts.without (p : ZeroParts) (t : String) : ZeroParts := { p with units := p.units.filter (·.1 != t) }

theorem ZeroParts.assertions_without (p : ZeroParts) (t : String) :
    (p.without t).assertions = dropTarget t p.assertions

theorem ZeroParts.sourced_without (p : ZeroParts) (t : String) : (p.without t).sourced = dropTarget t p.sourced

theorem ZeroParts.without_columns (p : ZeroParts) (t : String) :
    (p.without t).U = p.U ∧ (p.without t).E = p.E ∧ (p.without t).ψ = p.ψ ∧
    (p.without t).Γ = (dropTarget t p.assertions).map (·.2) ∧
    (p.without t).premises = (dropTarget t p.sourced).map (·.2)

/-! The enumerated adapter: one row per compatible choice, over the choice's filled document. -/

/-- The document without unit `u`'s assertion: each fixed item of `u` whose content is an assertion is dropped. -/
def withoutAssertion (D : Doc) (u : String) : Doc :=
  { D with items := D.items.filter fun
      | .fixed v (.assertion _) _ => v != u
      | _ => true }

def withoutAssertionN (N : NDoc) (u : String) : NDoc := ⟨withoutAssertion N.D u, N.unspec⟩

theorem withoutAssertion_sets (D : Doc) (u : String) : (withoutAssertion D u).sets = D.sets
theorem withoutAssertion_rules (D : Doc) (u : String) (c : Choice) :
    (choiceDoc (withoutAssertion D u) c).1 = (choiceDoc D c).1
theorem choiceU_withoutAssertion (N : NDoc) (u : String) (c : Choice) :
    choiceU (withoutAssertionN N u) c = choiceU N c
theorem ruleUnits_withoutAssertion (D : Doc) (u : String) (c : Choice) (p : String) :
    ruleUnits (withoutAssertion D u) c p = ruleUnits D c p

/-- Exactly the target's assertions go: every other entry stays, in order. -/
theorem sourcedAssertions_withoutAssertion (D : Doc) (u : String) (c : Choice)
    (hu : ∀ R ∈ D.sets, R.unit ≠ u) :
    sourcedAssertions (withoutAssertion D u) c = dropTarget u (sourcedAssertions D c)

/-- The support question's premises under choice `c`, each with its source. -/
def supportSourced (N : NDoc) (u : String) (c : Choice) : List (Source × VE.Formula) :=
  sourced (choiceU (withoutAssertionN N u) c) (sourcedAssertions (withoutAssertionN N u).D c)

/-- Its reduced premises are ask's row premises (`rowSourced`'s list) filtered, each with its source. -/
theorem supportSourced_eq (N : NDoc) (u : String) (c : Choice) (hu : ∀ R ∈ N.D.sets, R.unit ≠ u) :
    supportSourced N u c = dropTarget u (sourced (choiceU N c) (sourcedAssertions N.D c))

/-- No premise of the support question comes from the target. -/
theorem supportSourced_target (N : NDoc) (u : String) (c : Choice) (hu : ∀ R ∈ N.D.sets, R.unit ≠ u) :
    ∀ x ∈ supportSourced N u c, x.1 ≠ Source.unit u

/-- Source to formula: the second column is `premisesU` of the reduced choice document. -/
theorem supportSourced_premises (N : NDoc) (u : String) (c : Choice) :
    (supportSourced N u c).map (·.2) =
      VE.NormDefaults.Wire.premisesU (choiceU N c) (choiceDoc (withoutAssertion N.D u) c).2
end VE.Ask
```

The hypothesis `∀ R ∈ D.sets, R.unit ≠ u` is what `eligible`'s `readings` refusal guarantees (6.3), and Lean checks it
on the request (7.3). Lean cannot tell which other unit an author derived from the target, so none is removed on that
ground; any other unit the proof uses is named (E1, Astra round 3).

The adapter-level reductions (`PlainParts.without`, `ZeroParts.without`, `withoutAssertionN`) agree with `dropTarget`
by `PlainParts.sourced_without`, `ZeroParts.sourced_without` and `supportSourced_eq`, so the three adapters share one
reduction and differ only in the premises ask already assembles for them.

### 6.2 The verdict (`lean/VE/Purposes/Support.lean`, layer 4)

```lean
namespace VE.Purposes
open VE.Ask (Lead Source Reason)

/-- What a cited source names for the reader (E2): a sentence itself; an author's rule its units (`VE.Ask.ruleUnits`
    under the row's choice); a definition its name, until the definitions owner supplies its unit; VE's own
    background, pair and fill premises nothing. -/
def named (ru : String → List String) : Source → List String × List String
  | .unit i => ([i], [])
  | .rules p => (ru p, [])
  | .definition n => ([], [n])
  | .background => ([], [])
  | .pair _ _ => ([], [])
  | .fill _ _ => ([], [])

def citedUnits (ru : String → List String) (cs : List Source) : List String :=
  (cs.flatMap fun s => (named ru s).1).eraseDups

def citedDefinitions (ru : String → List String) (cs : List Source) : List String :=
  (cs.flatMap fun s => (named ru s).2).eraseDups

def supportOf (reasons : List String) (ru : String → List String) (lead : Lead) (cs : List Source)
    (why : Option Reason) : Support :=
  match lead with
  | .yes =>
    let us := citedUnits ru cs
    let os := us.filter fun v => !reasons.contains v
    let ds := citedDefinitions ru cs
    if us.any reasons.contains then (if os.isEmpty && ds.isEmpty then .alone else .together os ds)
    else .without os ds
  | .no => .ruledOut
  | .notSettled => .notSettled
  | .notNecessarily => .notEnough
  | .unknown => .unknown (why.getD .noResult)

theorem mem_citedUnits (ru : String → List String) (srcs : List Source) (used : List Nat) (v : String) :
    v ∈ citedUnits ru (VE.Ask.cited srcs used) ↔ ∃ i ∈ used, ∃ s, srcs[i]? = some s ∧ v ∈ (named ru s).1

theorem mem_citedDefinitions (ru : String → List String) (srcs : List Source) (used : List Nat) (n : String) :
    n ∈ citedDefinitions ru (VE.Ask.cited srcs used) ↔ ∃ i ∈ used, ∃ s, srcs[i]? = some s ∧ n ∈ (named ru s).2

theorem supportOf_alone_iff (reasons : List String) (ru : String → List String) (lead : Lead) (cs : List Source)
    (why : Option Reason) :
    supportOf reasons ru lead cs why = .alone ↔
      lead = .yes ∧ (∃ v ∈ citedUnits ru cs, v ∈ reasons) ∧ (∀ v ∈ citedUnits ru cs, v ∈ reasons) ∧
        citedDefinitions ru cs = []

theorem supportOf_together_iff (reasons : List String) (ru : String → List String) (lead : Lead)
    (cs : List Source) (why : Option Reason) (os ds : List String) :
    supportOf reasons ru lead cs why = .together os ds ↔
      lead = .yes ∧ (∃ v ∈ citedUnits ru cs, v ∈ reasons) ∧
        os = (citedUnits ru cs).filter (fun v => !reasons.contains v) ∧ ds = citedDefinitions ru cs ∧
        (os ≠ [] ∨ ds ≠ [])

theorem supportOf_without_iff (reasons : List String) (ru : String → List String) (lead : Lead)
    (cs : List Source) (why : Option Reason) (os ds : List String) :
    supportOf reasons ru lead cs why = .without os ds ↔
      lead = .yes ∧ (∀ v ∈ citedUnits ru cs, v ∉ reasons) ∧ os = citedUnits ru cs ∧
        ds = citedDefinitions ru cs

/-- Honest leads: each outcome comes from exactly one lead, and UNKNOWN exactly from an unknown row. -/
theorem supportOf_lead (reasons : List String) (ru : String → List String) (lead : Lead) (cs : List Source)
    (why : Option Reason) :
    (supportOf reasons ru lead cs why = .notEnough ↔ lead = .notNecessarily) ∧
    (supportOf reasons ru lead cs why = .ruledOut ↔ lead = .no) ∧
    (supportOf reasons ru lead cs why = .notSettled ↔ lead = .notSettled) ∧
    ((∃ x, supportOf reasons ru lead cs why = .unknown x) ↔ lead = .unknown)

theorem supportOf_checked (reasons : List String) (ru : String → List String) (lead : Lead) (cs : List Source)
    (why : Option Reason) (w : NotChecked) : supportOf reasons ru lead cs why ≠ .notChecked w

/-- `alone`: the used premises entail the target; some used premise comes from a reason unit; every unit a used
    premise names is a reason unit, and none names a definition. -/
theorem alone_sound (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate)
    (srcs : List Source) (reasons : List String) (ru : String → List String)
    (hk : VE.Ask.replayOk E P ψ k = true)
    (h : supportOf reasons ru .yes (VE.Ask.cited srcs (VE.Ask.usedPositions E P ψ k)) none = .alone) :
    VE.Entails.{u} E ((VE.Ask.usedPositions E P ψ k).filterMap (P[·]?)) ψ ∧
    (∃ i ∈ VE.Ask.usedPositions E P ψ k, ∃ s, srcs[i]? = some s ∧ ∃ v ∈ (named ru s).1, v ∈ reasons) ∧
    (∀ i ∈ VE.Ask.usedPositions E P ψ k, ∀ s, srcs[i]? = some s →
      (∀ v ∈ (named ru s).1, v ∈ reasons) ∧ (named ru s).2 = [])

/-- `together os ds`: the same entailment, a reason unit is used, and `os` and `ds` are exactly the other units and
    the definitions the used premises name. -/
theorem together_exact (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate)
    (srcs : List Source) (reasons : List String) (ru : String → List String) (os ds : List String)
    (hk : VE.Ask.replayOk E P ψ k = true)
    (h : supportOf reasons ru .yes (VE.Ask.cited srcs (VE.Ask.usedPositions E P ψ k)) none = .together os ds) :
    VE.Entails.{u} E ((VE.Ask.usedPositions E P ψ k).filterMap (P[·]?)) ψ ∧
    (∃ i ∈ VE.Ask.usedPositions E P ψ k, ∃ s, srcs[i]? = some s ∧ ∃ v ∈ (named ru s).1, v ∈ reasons) ∧
    (∀ v, v ∈ os ↔ (∃ i ∈ VE.Ask.usedPositions E P ψ k, ∃ s, srcs[i]? = some s ∧ v ∈ (named ru s).1) ∧
      v ∉ reasons) ∧
    (∀ n, n ∈ ds ↔ ∃ i ∈ VE.Ask.usedPositions E P ψ k, ∃ s, srcs[i]? = some s ∧ n ∈ (named ru s).2)

/-- `without os ds` (E2): the same entailment, no used premise comes from a reason unit, and `os`, `ds` are exactly
    what the used premises name. It describes this proof's independence of the reason, not the reason's irrelevance. -/
theorem without_sound (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate)
    (srcs : List Source) (reasons : List String) (ru : String → List String) (os ds : List String)
    (hk : VE.Ask.replayOk E P ψ k = true)
    (h : supportOf reasons ru .yes (VE.Ask.cited srcs (VE.Ask.usedPositions E P ψ k)) none = .without os ds) :
    VE.Entails.{u} E ((VE.Ask.usedPositions E P ψ k).filterMap (P[·]?)) ψ ∧
    (∀ i ∈ VE.Ask.usedPositions E P ψ k, ∀ s, srcs[i]? = some s → ∀ v ∈ (named ru s).1, v ∉ reasons) ∧
    (∀ v, v ∈ os ↔ ∃ i ∈ VE.Ask.usedPositions E P ψ k, ∃ s, srcs[i]? = some s ∧ v ∈ (named ru s).1) ∧
    (∀ n, n ∈ ds ↔ ∃ i ∈ VE.Ask.usedPositions E P ψ k, ∃ s, srcs[i]? = some s ∧ n ∈ (named ru s).2)

/-! The negative outcomes, one theorem per adapter (SR 8), each over that adapter's row on its Γ after `dropTarget`. -/

/-- The plain adapter: `notEnough` is a checked failure of entailment from everything else the text says. -/
theorem notEnough_sound_plain (p : VE.Ask.PlainParts) (t : String) (r : VE.Ask.PlainRow) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.PlainRowOk.{u} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .notEnough) :
    r.lead = .notNecessarily ∧ ¬ VE.Entails.{0} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) p.ψ

theorem ruledOut_sound_plain (p : VE.Ask.PlainParts) (t : String) (r : VE.Ask.PlainRow) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.PlainRowOk.{u} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .ruledOut) :
    r.lead = .no ∧ VE.Ask.Consistent p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) ∧
      VE.Entails.{u} p.V ((VE.Ask.dropTarget t p.sourced).map (·.2)) (.not p.ψ)

/-- The plain adapter never splits (`plain_never_split`), so its support is never `notSettled`. -/
theorem notSettled_never_plain (r : VE.Ask.PlainRow) (reasons : List String) (ru : String → List String)
    (cs : List Source) (why : Option VE.Ask.Reason) : supportOf reasons ru r.lead cs why ≠ .notSettled

open VE.Readings VE.NormDefaults in
/-- The zero-set adapter: a checked situation of the conflict-free document in which everything else the text says
    is true and the claim is false. -/
theorem notEnough_sound_zero (p : VE.Ask.ZeroParts) (t : String) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOkU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .notEnough) :
    r.lead = .notNecessarily ∧ ConflictFreeU.{u} p.U ∧ CounterU p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ

open VE.Readings VE.NormDefaults in
theorem ruledOut_sound_zero (p : VE.Ask.ZeroParts) (t : String) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOkU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .ruledOut) :
    r.lead = .no ∧ ConflictFreeU.{u} p.U ∧ ConsistentU p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) ∧
      EntailsU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) (.not p.ψ)

open VE.Readings VE.NormDefaults in
theorem notSettled_sound_zero (p : VE.Ask.ZeroParts) (t : String) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOkU.{u} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ r)
    (h : supportOf reasons ru r.lead cs why = .notSettled) :
    r.lead = .notSettled ∧ ConflictFreeU.{u} p.U ∧
      VE.Ask.SplitU p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) p.ψ

open VE.Readings VE.NormDefaults in
/-- The enumerated adapter, per compatible choice: `notEnough` (E1) is a checked situation of the conflict-free
    document in which everything else the text says is true and the claim is false. -/
theorem notEnough_sound (N : NDoc) (t : String) (ψ : VE.Formula) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOk.{u} (VE.Ask.withoutAssertionN N t) ψ r)
    (h : supportOf reasons ru r.lead cs why = .notEnough) :
    r.lead = .notNecessarily ∧ ConflictFreeU.{u} (choiceU N r.choice) ∧
      CounterU (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 ψ

open VE.Readings VE.NormDefaults in
theorem ruledOut_sound (N : NDoc) (t : String) (ψ : VE.Formula) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOk.{u} (VE.Ask.withoutAssertionN N t) ψ r)
    (h : supportOf reasons ru r.lead cs why = .ruledOut) :
    r.lead = .no ∧ ConflictFreeU.{u} (choiceU N r.choice) ∧
      ConsistentU (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 ∧
      EntailsU.{u} (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 (.not ψ)

open VE.Readings VE.NormDefaults in
theorem notSettled_sound (N : NDoc) (t : String) (ψ : VE.Formula) (r : VE.Ask.Row) (reasons : List String)
    (ru : String → List String) (cs : List Source) (why : Option VE.Ask.Reason)
    (hr : VE.Ask.RowOk.{u} (VE.Ask.withoutAssertionN N t) ψ r)
    (h : supportOf reasons ru r.lead cs why = .notSettled) :
    r.lead = .notSettled ∧ ConflictFreeU.{u} (choiceU N r.choice) ∧
      VE.Ask.SplitU (choiceU N r.choice) (choiceDoc (VE.Ask.withoutAssertion N.D t) r.choice).2 ψ
end VE.Purposes
```

How the pieces bind. `alone_sound`, `together_exact` and `without_sound` hold for any premise list, so each adapter
instantiates them with its reduced sourced premises (`srcs` the first column, `P` the second, both from one list):

| Adapter | `E` | `srcs`, `P` | `ru` |
|---|---|---|---|
| plain | `p.V` | `VE.Ask.dropTarget t p.sourced` (`PlainParts.without_columns`) | `fun _ => []` (no rules) |
| zero-set | `p.E` | `VE.Ask.dropTarget t p.sourced` (`ZeroParts.without_columns`) | `VE.Ask.zeroRuleUnits case` |
| enumerated, choice `c` | `VE.Readings.Wire.fullEnv (VE.Ask.withoutAssertionN N t) c` | `VE.Ask.supportSourced N t c` (`supportSourced_eq`, `supportSourced_premises`) | `VE.Ask.ruleUnits N.D c` |

So the used premises never include the target (`dropTarget_target`), and every author-supplied premise the proof
uses is named. The negative theorems follow from each adapter's own lead soundness on its reduced Γ:
`plain_lead_sound` and `plain_never_split` (plain), `leadU_sound` (zero-set), and `VE.Ask.lead_sound` with
`choiceU_withoutAssertion` (enumerated). Each reduced Γ is "everything else the text says": the original assertions
minus the target's (`PlainParts.without_columns`, `ZeroParts.without_columns`, and
`sourcedAssertions_withoutAssertion` with `sourcedAssertions_formulas`). `support_wire_sound` (6.4) gives every row of
an accepted request exactly these hypotheses.

### 6.3 Which links get a question (`eligible`, in `Verdict.lean`, used from PE-2)

```lean
namespace VE.Purposes

def eligible (U : Units) (L : Link) : Except NotChecked (String × VE.Formula × List String) := do
  if L.relation == .inOrderTo then throw .purpose
  if L.polarity == .denied then throw .denied
  let parts := fun (s : List Ref) => s.filterMap fun r => r.partId? >>= U.find?
  if (parts L.target).any (·.kind == .norm) then throw .ruleTarget
  if (parts (L.reason ++ L.target)).any (!·.candidates.isEmpty) then throw .readings
  let stated := fun (p : Part) =>
    p.kind == .asserted && p.formula.isSome && (p.status == "CHECKED" || p.status == "OPEN")
  match L.target with
  | [.part t] => match U.find? t with
    | some p => match p.formula with
      | some ψ =>
        if stated p && !L.reason.isEmpty && (parts L.reason).length == L.reason.length &&
            (parts L.reason).all stated then pure (t, ψ, (parts L.reason).map (·.id))
        else throw .noFormula
      | none => throw .noFormula
    | none => throw .noFormula
  | _ => throw .noFormula

theorem eligible_ok (U : Units) (L : Link) (t : String) (ψ : VE.Formula) (rs : List String)
    (h : eligible U L = .ok (t, ψ, rs)) :
    L.relation = .because ∧ L.polarity = .affirmed ∧ L.target = [.part t] ∧ L.reason = rs.map Ref.part ∧ rs ≠ [] ∧
    (∃ p, U.find? t = some p ∧ p.kind = .asserted ∧ p.formula = some ψ ∧ p.candidates = [] ∧
      (p.status = "CHECKED" ∨ p.status = "OPEN")) ∧
    ∀ i ∈ rs, ∃ p, U.find? i = some p ∧ p.kind = .asserted ∧ p.formula.isSome = true ∧ p.candidates = [] ∧
      (p.status = "CHECKED" ∨ p.status = "OPEN")

theorem eligible_purpose (U : Units) (L : Link) (h : L.relation = .inOrderTo) : eligible U L = .error .purpose

theorem eligible_denied (U : Units) (L : Link) (h : L.relation = .because) (hd : L.polarity = .denied) :
    eligible U L = .error .denied
end VE.Purposes
```

### 6.4 The request and the answer

- **The route** (Q1, resolved as ask's case, SR 7). A support request is an `ask` request with `support` in place of
  `question`: `{"id", "document", "support": {"target": t, "reasons": [r, …]}, "lexicon", "case", "names"}`. Ask's
  runner gains one hunk (`VE.Ask.Run.askCase`): it selects the adapter by `routeOfDocument`, exactly as `answered`
  does, and calls `replaySupport` below. The `case` is that adapter's own case: `environment`, `document`,
  `conclusion` and `evidence` for the plain and zero-set adapters; RD-3's readings case, with `question` `"query"`, for
  the enumerated adapter. Each is bound to the document by the adapter's own binding (`PlainCaseBinding`,
  `CaseBinding`). Its `conclusion` is the target part's formula; no English question is read. The case's units are the
  flattened parts, so `t` and each `r` are part ids and `Source.unit` ids (SR 7). Python takes `t` and the reasons
  from the section's `ask` member (5.4), builds the case as ask's relay does, and computes nothing itself. The
  existing producer supplies evidence for the reduced premises, and Lean replays it there (Astra round 3).
- **Lean's request checks** (7.3, in that order): `support` has exactly `target` and `reasons`; each is a unit of the
  case's document; no reading set is on the target; the case's conclusion is the target's formula; the case has no
  premises and assumes no reading. Lean then replays the adapter's case on the reduced context: `PlainParts.without p
  t`, `ZeroParts.without p t`, or `withoutAssertionN N t` under each compatible choice. Every refusal the adapter
  gives is ask's, word for word. Past 64 compatible choices it is `replayError`'s `ResourceLimit` text, and the answer
  has no support rows (SR 13). No aggregate UNKNOWN is added: the support shape carries verdicts only inside rows, and
  exhaustion is never a negative verdict. A soft document gets ask's refusal (SR 11, 6.1).
- **The answer** gains `support`:

  ```json
  "support": {"target": "u2.p1", "reasons": ["u2.p3"],
              "rows": [{"choice": [], "verdict": {"verdict": "together", "units": ["u1"], "definitions": []}}],
              "lines": ["VE checked that this reason is enough to conclude the claim together with sentence 1."]}
  ```

  `rows` is one row per replayed row of the adapter, in its order: one row with choice `[]` on the plain and zero-set
  adapters, one per compatible choice on the enumerated adapter. Each row's verdict is `SupportRow.verdict` below:
  `supportOf` over that row's reduced sources, the positions its certificate uses, its lead and its reason. `lines`
  is `English.supportLines` (2.3), which groups the rows and writes the reading clauses as ask does (SR 3; 12,
  choice 5).

```lean
namespace VE.Purposes
open Lean VE.Ask (Lead Source Reason Row)

/-- The adapter ask selected (`VE.Ask.Run.routeOfDocument`), with what Lean decoded for it. -/
inductive Adapter
  | plain (p : VE.Ask.PlainParts)
  | zero (p : VE.Ask.ZeroParts) (case : Json)
  | enumerated (N : VE.Readings.NDoc)

def Adapter.route : Adapter → String
  | .plain _ => "plain" | .zero _ _ => "norm-defaults" | .enumerated _ => "readings"

/-- One answered row of a support request: the adapter's row, its reduced sourced premises under its choice, the
    environment its certificates replay in, the units of the rules on each predicate, and, for a yes or no lead, the
    certificate's conclusion (ψ or ¬ψ) and certificate. -/
structure SupportRow where
  row     : Row
  sources : List (Source × VE.Formula)
  E       : VE.Environment
  ru      : String → List String
  cert    : Option (VE.Formula × VE.Tableau.Certificate)

/-- SR 12: the row's verdict is `supportOf` over the row's reduced sources. -/
def SupportRow.verdict (reasons : List String) (x : SupportRow) : Support :=
  supportOf reasons x.ru x.row.lead
    (match x.cert with
     | some (φ, k) => VE.Ask.cited (x.sources.map (·.1)) (VE.Ask.usedPositions x.E (x.sources.map (·.2)) φ k)
     | none => [])
    x.row.reason

/-- A yes or no row rests on a certificate for the claim or its negation that replays on exactly the row's reduced
    premises; no other row has one. -/
def CertOk (ψ : VE.Formula) (x : SupportRow) : Prop :=
  (x.row.lead = .yes → ∃ k, x.cert = some (ψ, k)) ∧ (x.row.lead = .no → ∃ k, x.cert = some (.not ψ, k)) ∧
  (x.row.lead ≠ .yes → x.row.lead ≠ .no → x.cert = none) ∧
  ∀ φ k, x.cert = some (φ, k) → VE.Ask.replayOk x.E (x.sources.map (·.2)) φ k = true

/-- What a row claims, by adapter (SR 8): its sources are the adapter's sourced premises after `dropTarget`, and its
    row holds on that reduced Γ, so 6.2's theorems for the adapter apply to it. -/
def SupportRowOk (t : String) (ψ : VE.Formula) : Adapter → SupportRow → Prop
  | .plain p, x => p.ψ = ψ ∧ x.sources = VE.Ask.dropTarget t p.sourced ∧ x.E = p.V ∧ x.ru = (fun _ => []) ∧
      ∃ r : VE.Ask.PlainRow, x.row = r.toRow ∧ VE.Ask.PlainRowOk.{0} p.V (x.sources.map (·.2)) ψ r
  | .zero p case, x => p.ψ = ψ ∧ x.sources = VE.Ask.dropTarget t p.sourced ∧ x.E = p.E ∧
      x.ru = VE.Ask.zeroRuleUnits case ∧ x.row.choice = [] ∧
      VE.Ask.RowOkU.{0} p.U ((VE.Ask.dropTarget t p.assertions).map (·.2)) ψ x.row
  | .enumerated N, x => x.sources = VE.Ask.supportSourced N t x.row.choice ∧
      x.E = VE.Readings.Wire.fullEnv (VE.Ask.withoutAssertionN N t) x.row.choice ∧
      x.ru = VE.Ask.ruleUnits N.D x.row.choice ∧ VE.Ask.RowOk.{0} (VE.Ask.withoutAssertionN N t) ψ x.row

/-- A support request Lean accepted (7.3) and replayed on the reduced context. -/
structure SupportAsked where
  request  : Json
  adapter  : Adapter
  target   : String
  reasons  : List String
  ψ        : VE.Formula          -- the target's formula, the case's conclusion
  replayed : List Row            -- the adapter's rows on the reduced context, in its order
  rows     : List SupportRow

/-- The support request of ask's runner, on the adapter `route` names. -/
def replaySupport (route : String) (j : Json) : Except String SupportAsked

/-- SR 12: what an accepted support request establishes. The target and reasons are the request's; the case has no
    premises and assumes no reading; the answer's rows are the replayed rows, as lists, so order and multiplicity
    both count; the replayed choices are exactly `[[]]` on a one-choice adapter and exactly the compatible choices
    on the enumerated adapter; and every row satisfies its adapter's `SupportRowOk` and `CertOk`. With
    `SupportRow.verdict`, each row's verdict is `supportOf` over that row's reduced sources, and 6.2's theorems apply
    to it. -/
theorem support_wire_sound (route : String) (j : Json) (a : SupportAsked) (h : replaySupport route j = .ok a) :
    a.request = j ∧ a.adapter.route = route ∧
    (j.getObjValD "support").getObjValD "target" = .str a.target ∧
    (j.getObjValD "support").getObjValD "reasons" = Json.arr (a.reasons.map Json.str).toArray ∧
    ((j.getObjValD "case").getObjValD "premises" = .null ∨
      (j.getObjValD "case").getObjValD "premises" = Json.arr #[]) ∧
    ((j.getObjValD "case").getObjValD "assumed" = .null ∨
      (j.getObjValD "case").getObjValD "assumed" = Json.arr #[]) ∧
    a.rows.map (·.row) = a.replayed ∧
    (match a.adapter with
     | .enumerated N => ∀ c, VE.Readings.Compatible N.D c ↔ c ∈ a.replayed.map (·.choice)
     | _ => a.replayed.map (·.choice) = [[]]) ∧
    ∀ x ∈ a.rows, SupportRowOk a.target a.ψ a.adapter x ∧ CertOk a.ψ x

/-- The `support` member: each row's choice and verdict, then the lines. -/
def supportJson (a : SupportAsked) (lines : List String) : Json

theorem supportJson_rows (a : SupportAsked) (lines : List String) :
    (supportJson a lines).getObjValD "rows" = Json.arr (a.rows.map fun x =>
      Json.mkObj [("choice", VE.Readings.choiceJson x.row.choice),
        ("verdict", renderSupport (x.verdict a.reasons))]).toArray
end VE.Purposes
```

- **Binding** (Python, D9): `target` and `reasons` equal the request's; `rows` is not empty. Each row's choice decodes
  and names only open sets and candidate indices of the request's document, and no choice repeats. A plain or
  zero-set answer (by `routeOfDocument`'s profiles) has exactly one row, with choice `[]`. `verdict` decodes
  (`decodeSupport`); every unit a verdict names is a unit of the request's document; `lines` are strings, none
  extra. That the rows are the replayed rows is Lean's (`support_wire_sound`); Python never recomputes it. The rows
  go into the rd-9 inventory.

## 7. Diagnostics

Every text is Lean's; Python relays it verbatim. The order within each table is the fault order.

### 7.1 Decoding the block (`decodeBlock`)

| Fault | Text |
|---|---|
| `purposes@0` listed, no block | `InvalidPurposes: purposes@0 needs a purposes block` |
| not an object with exactly `links` | `InvalidPurposes: purposes must be an object whose only member is links` |
| more than 256 links | `ResourceLimit: purposes links exceed 256` |
| link `n` (from 1) with a missing or extra field | `InvalidPurposes: link n must have id, relation, polarity, reason, target and marker, and may have share` |
| an id that is not a token | `InvalidPurposes: invalid id <id>` |
| relation not `because` or `in order to` (`prevents` included) | `InvalidPurposes: link <id> has relation <r>; a purposes link's relation is because or in order to` |
| polarity | `InvalidPurposes: link <id> has polarity <p>; it must be affirmed or denied` |
| share | `InvalidPurposes: link <id> has share <s>; it must be plain, sole, partly or not_sole` |
| a side | `InvalidPurposes: link <id> has a side that is not a list of parts or mentions` |

A `purposes` key without `purposes@0` is refused earlier, by the loader's existing text
`unknown document metadata` (through `documentMetadataFor`, 5.2).

### 7.2 Checking the block (`check`, 4.3)

| # | Fault | Text (computed, 9.2) |
|---|---|---|
| 1 | more than 256 links | `ResourceLimit: purposes links exceed 256` |
| 2 | duplicate link id | `InvalidPurposes: two links have the same id` |
| 3 | per link, in order: a part id not in the checked view | `InvalidPurposes: link <id> names unknown unit <i>` |
| 4 | not distinct parts of one MIXED unit (a mention included, before PE-4) | `InvalidPurposes: link <id> must join distinct parts of one unit` |
| 4a | a side whose parts are not in source order, or not each starting where the previous one ends (SR 6) | `InvalidPurposes: link <id> has a side whose parts are not adjacent and in order` |
| 5 | the marker's kind is not `causal <relation> c e` with the sides' kinds in slot order | `InvalidPurposes: unit <marker> is not marked as this link's reason or purpose` |
| 6 | a part, or a reading candidate, on the unstated side is not inert | `InvalidPurposes: link <id> would make a purpose or a denied reason a premise or a rule` |
| † 6a | a pack premise is sourced to a part on the unstated side, or to its unit (PE-R11) | `InvalidPurposes: link <id> has a side the text does not state, and a pack takes a premise from it` |
| 7 | denied with a share other than `plain` | `InvalidPurposes: link <id> denies a reason and also says how much of the reason it is` |
| 8 | `sole` with a rival, or with an affirmed link of the same relation and target whose share is `partly` or `notSole` (SR 5) | `InvalidPurposes: link <id> says this is the only reason, and the text gives another` |
| 9 | a `causal because`/`in order to` part marks no link | `InvalidPurposes: a unit marked as a reason or purpose has no link` |
| 10 | a LABELLED marker whose links' sides are not all CHECKED or OPEN | `InvalidPurposes: link words are counted as covered, but what they link is not formalised` |

Fault 4a, after fault 4 (SR 6), is numbered so that every other text keeps its number; "text 8" in SR 5 is row 8.
Fault 6a (pe-rev) is numbered the same way.

The document mode adds `CheckerUnavailable: purposes@0 with a rights kind needs its composed route`
(`purposesUnits`), and the profile table's existing `UnsupportedProfile` texts (`gateOf`).

### 7.3 The support request (PE-5)

| Fault | Text |
|---|---|
| `support` without exactly `target` and `reasons` | `InvalidInput: support needs exactly a target and reasons` |
| the target is not a unit of the document | `InvalidInput: support target <t> is not a unit of the document` |
| a reason is not a unit of the document | `InvalidInput: support reason <r> is not a unit of the document` |
| a reading set is on the target | `InvalidInput: support target <t> has a reading set` |
| the conclusion is not the target's formula | `InvalidInput: support target <t> does not state the conclusion` |
| the case has `premises` other than `[]`, or an `assumed` reading (SR 12) | `InvalidInput: the case does not ask this question (premises or assumed readings)`: ask's text (`Ask/Wire.lean:333`), reused |
| more than 64 compatible choices (SR 13) | `ResourceLimit: There are more than 64 ways to read this document's open sentences. VE did not check them all.`: ask's `replayError` (`Ask/Run.lean:82`); no support rows |
| any other refusal of the adapter's binding, admission or replay, a soft document's included (SR 11) | the adapter's text, as ask gives it for the same case, word for word |

The first five texts are new; every other row is ask's text, so 7.3 adds no text for a case ask already refuses. A
plain or zero-set case cannot carry `premises` or `assumed`: `oneChoiceCase` refuses any member beyond its four, with
its own text.

## 8. The guarantees, in plain words

1. **A link adds nothing to the document** (`checkDocPurposes_base`, `checkDocPurposes_absent`). With `purposes@0`, the
   answer is the base answer plus a `purposes` member. Without it, the answer is the document mode's, byte for byte.
2. **What the text does not state is never used as stated** (`nonfactive_iff` with section 3's four theorems). A
   purpose, a denied reason, and every reading of either, is never a premise and never a rule, on the W2 route, the
   norms route or the readings route. † No pack takes a premise from it either (`packsInert_iff`, PE-R11), on every
   list `purposes@0` covers, because a list holding a pack is covered only with `packSources_complete`.
3. **"Enough" means a checked proof that uses the reason and nothing else the author wrote** (`alone_sound`, built on
   `usedPositions_sufficient`). The proof never uses the claim itself (`dropTarget_target`, `supportSourced_target`).
4. **"Together with …" names everything else** (`together_exact`). Every other sentence and definition the proof uses
   is named, and nothing more is: an author's rule by its sentences, a definition by its name, and another part of
   the claim's own sentence by its words, never by the claim's sentence number.
5. **"Follows without this reason" is said when the proof uses no reason** (`without_sound`). It describes that proof,
   not the reason.
6. **"Not enough" shows a real situation** (`notEnough_sound` and its plain and zero-set forms). In it, every other
   thing the text says is true and the claim is false, under rules that never contradict each other.
7. **Every answered row is the adapter's own row, on the claim's reduced context** (`support_wire_sound`). The rows
   are exactly the rows ask's adapter replays, in its order, and each verdict is computed from that row's reduced
   premises.
8. **UNKNOWN is never a no** (`supportOf_lead`). An exhausted budget or an unchecked proof is UNKNOWN, with ask's
   reason sentence. It is never "not enough". Past 64 readings VE answers with ask's limit and no verdict at all.
9. **Soft documents wait** (6.1). Support never reaches a soft premise: ask's adapters carry none
   (`choiceX_normsShaped`, `normsShaped_of_ND`). A soft document's support request is refused with ask's text until
   ask serves soft documents.
10. † **A link's line says no more than its readings and its sentence** (`linkLines_withheld`, `shownUnder_iff`,
   `unlinkedActive_iff`; PE-R8). It is shown only under the candidates that hold its target, and when the sentence has
   a part the quotes leave out that may scope over the link, the line says so.

## 9. Acceptance fixtures

Every value below was computed by the stub (11), except those marked †, which draft 2 adds and derives by hand from
the definitions (11.1); the owning batch confirms each by `#guard` or `rfl`. A fixture marked *(PE-n)* is a
route-level fixture the batch builds; its function-level counterpart is given here.

### 9.1 `Kind.inert` (exactly the five kinds)

| Kind | `inert` |
|---|---|
| `asserted`, `norm`, `definition`, `attributed a says asserted`, `hedged likely asserted`, `causal because asserted asserted`, `question`, `instruction`, `unformalised x` | `false` |
| `example`, `exposition`, `analogy`, `explanation`, `meta` | `true` |

`normRole_inert` and `inForce_inert` are proved over all five inert kinds (11).

### 9.2 The check (PE-1, `Examples.lean`)

Parts are written `p1`, `p2`, … of the unit named; statuses are UNFORMALISED unless stated.

| # | Fixture | `check` |
|---|---|---|
| F1 | u0146.s01 "We want Claude to figure out the most plausible interpretation of a query in order to give the best response." (109 B): p1 [0,73) `norm`; p2 [73,86) " in order to " `causal "in order to" norm explanation`; p3 [86,109) `explanation`; l1 `inOrderTo`, affirmed, plain, reason [p3], target [p1], marker p2 | `.ok ()` |
| F1a | the marker's slots swapped (`causal "in order to" explanation norm`) | unit u0146.s01.p2 is not marked as this link's reason or purpose |
| F1b | p3 `asserted` (marker slot `asserted`) | link l1 would make a purpose or a denied reason a premise or a rule |
| F1c | p3 `norm` (marker slot `norm`) | the same (A2) |
| F1d | p3 `definition` (marker slot `definition`) | the same (A2) |
| F1e | p3 under an active set with candidates [`explanation`, `asserted`] | the same (A2: reading candidates) |
| F1f | p3 under an active set with candidates [`explanation`, `exposition`] | `.ok ()` |
| F1g | p2 LABELLED | link words are counted as covered, but what they link is not formalised |
| F1h | l1 dropped | a unit marked as a reason or purpose has no link |
| F2 | u0019.s01 "Although we're asking Claude …, this isn't because we think being overseeable takes precedence over being good.": p1 `norm`; p2 `causal because explanation norm`; p3 `explanation`; l1 `because`, denied, plain | `.ok ()` |
| F2a | l1 share `sole` | link l1 denies a reason and also says how much of the reason it is |
| F2b | p3 `asserted` (marker `causal because asserted norm`) | link l1 would make a purpose or a denied reason a premise or a rule |
| F3 | [176186,176365) "… matters not only because it is good for Claude itself but because values … seem likely to be brittle.": p1, p3, p5 `asserted`; p2, p4 `causal because asserted asserted`; l1 `notSole` [p3]→[p1] marker p2; l2 `plain` [p5]→[p1] marker p4 | `.ok ()` |
| F3a | l1 share `sole` | link l1 says this is the only reason, and the text gives another |
| F3b | l2 dropped | a unit marked as a reason or purpose has no link (p4 is unlinked; `notSole` alone is fine, F6) |
| F4 | [125508,125756) "… warrant caution before acting unilaterally—not because Claude's reasoning is inherently worse than a human's, but because Claude's situation differs in important ways:": p1 `norm`; p2 `causal because explanation norm`; p3 `explanation`; p4 `causal because asserted norm`; p5 `asserted`; l1 denied [p3]→[p1] marker p2; l2 affirmed [p5]→[p1] marker p4 | `.ok ()` |
| F5a | `Relation.ofWire?` of "prevents", "because", "in order to" | `none`, `some because`, `some inOrderTo` (D8) |
| F5b | reason a part of another unit (b.p1) | link l1 must join distinct parts of one unit |
| F5c | reason a.p9, not in the view | link l1 names unknown unit a.p9 |
| F5d | the same link twice | two links have the same id |
| F5e | a.p1 as both reason and target | link l1 must join distinct parts of one unit |
| F5f | reason a mention (before PE-4) | link l1 must join distinct parts of one unit |
| F6 | "A, partly because B." with one link, share `plain`, `sole`, `partly`, `notSole` | `.ok ()` for each (A4) |
| F7a | `sole` l1 [g.p3]→[g.p1], and affirmed l2 with the *same* reason [g.p3] | `.ok ()` (a duplicate is not a second reason, A4) |
| F7b | l2's reason g.p5 instead | link l1 says this is the only reason, and the text gives another |
| F7c | l2 denied, reason g.p5 (`explanation`) | `.ok ()` (only affirmed links are rivals) |
| F7d | l1 `plain`, l2 reason g.p5 | `.ok ()` |
| † F7e | l1 `sole` [g.p3]→[g.p1], and affirmed l2 `notSole` with the *same* reason [g.p3] (SR 5) | link l1 says this is the only reason, and the text gives another (text 8) |
| † F7f | l2 `partly` instead, same reason | the same (text 8) |
| † F8 | h "A because B, C." (15 B): p1 [0,1) "A" `asserted`; p2 [1,10) " because " `causal because asserted asserted`; p3 [10,12) "B," `asserted`; p4 [12,15) " C." `asserted`; l1 `because`, affirmed, plain, reason [h.p3, h.p4], target [h.p1], marker h.p2 | `.ok ()`; its reason quotes "B, C." (`sideText_eq`) |
| † F8a | reason [h.p4, h.p3], reversed (SR 6) | link l1 has a side whose parts are not adjacent and in order |
| † F8b | h "A because B, C.": p3 [10,11) "B", p4 [11,12) "," `unformalised x`, p5 [12,15) " C." `asserted`; reason [h.p3, h.p5], separated by p4, which the link does not list (SR 6) | the same |
| † F2c | F2 with `packSources = ["u0019.s01.p3"]`: a pack premise sourced to the denied reason (PE-R11) | link l1 has a side the text does not state, and a pack takes a premise from it |
| † F2d | F2 with `packSources = ["u0019.s01"]`, the reason's unit | the same |
| † F2e | F2 with `packSources = ["u0019.s01.p1"]`, the target part | `.ok ()` |
| † F9 | f "In order to be safe, we believe every model should be honest." (61 B, u0014.s03's shape; PE-R7, PE-R8): p1 [0,12) "In order to " `causal "in order to" norm explanation`; p2 [12,21) "be safe, " `explanation`; p3 [21,61) `norm` under an active set, readings [`report`, `rationale`, `limiting`, `in-attitude`], kinds [`asserted`, `norm`, `norm`, `asserted`]; l1 `inOrderTo`, affirmed, plain, reason [f.p2], target [f.p3], marker f.p1 | `.ok ()`; `shownUnder = [("f.p3", ["rationale", "limiting"])]`; `unlinkedActive = []` |
| † F9a | F9 with every candidate kind `asserted` | `.ok ()`; `shownUnder = [("f.p3", [])]` (lines withheld, 9.7) |
| † F10 | g "Sometimes we may choose to keep a promise because we value our word." (68 B, u0289.s05's shape; PE-R8, PE-R9): p1 [0,10) "Sometimes " `asserted`; p2 [10,41) `exposition`; p3 [41,50) " because " `causal because exposition exposition`; p4 [50,68) `exposition` under D6 (c)'s set, readings [`reason`, `motive`], both `exposition`; l1 `because`, affirmed, plain, reason [g.p4], target [g.p2], marker g.p3 | `.ok ()`; `shownUnder = []`; `unlinkedActive = ["g.p1"]` |

Both directions of `check_ok_iff` are covered: F1, F1f, F2, F3, F4, F6, F7a, F7c, F7d and F8 are well formed. Each
conjunct of `WellFormed` fails alone in F5c (existence), F5b, F5e and F5f (`sameUnit`), F8a and F8b
(`sidesAdjacent`), F1a (`markerAgrees`), F1b–F1e and F2b (`nonfactive`), F2a (denied share), F3a, F7b, F7e and F7f
(`shareOk`), F1h and F3b (`markersLinked`), F1g (`markerHonest`) and F5d (ids). PE-1's `Examples.lean` adds the count
limit, with 257 links. Every earlier fixture has one part per side, so `sidesAdjacent` holds there and their values
are unchanged. † (pe-rev) `packsInert` fails alone in F2c and F2d, and holds in F2e, F9, F9a and F10. Every earlier
fixture has `packSources = []`, so by `packsInert_nil` its value is unchanged; F2e, F9, F9a and F10 are well formed.
`shownUnder` is `[]` and `unlinkedActive` is `[]` on F1, F2, F3, F4 and F8 (no set on a target part; every part of
the unit is named by a link), so the lines 9.7 gives for them are unchanged (`linkLines_plain`).

### 9.3 `shareOk_iff`, both directions

- The right side holds and `shareOk` is true: F6 with `sole` (no other link), F7a (same reason), F7c (the other link
  is denied), F7d (not `sole`), F3 (`notSole`).
- The right side fails and `shareOk` is false: F3a and F7b (an affirmed link, same relation and target, different
  reason); † F7e and F7f (same reason, share `notSole` or `partly`, SR 5).
- F7a stays well formed: its second link has the same reason and share `plain`, so it is a duplicate, not a claim
  that the reason is not the only one.

### 9.4 `nonfactive_iff`, both directions

- True: F1 (p3 `explanation`), F1f (inert candidates), F2, F4 (the denied reason `explanation`), F3 (`unstated` is
  empty: computed `unstated f3l1 = []`).
- False: F1b, F1c, F1d (the part's kind), F1e (a candidate), F2b; and a mention on the unstated side. `unstated`
  computed: F1 → [p3], F2 → [p3], F3 → [], F1 with polarity denied → [p3].

### 9.5 Front-matter keys (`purposes_key_iff`, both directions)

| Format, profiles | `"purposes" ∈ documentMetadataFor …` |
|---|---|
| `ve-document@1`, [`documents@1`, `purposes@0`] | `true` |
| `ve-document@1`, [`documents@1`] | `false` |
| `ve-document@2`, [`scope@0`] — `"scope"` | `true` |

`documentMetadata "ve-document@1"` is today's 16 keys (`format` … `completions`, `senses`), and does not contain
`purposes`, so the hypothesis of `purposes_key_iff` holds.

### 9.6 Support

**Function level** (`supportOf ["u2.p3"] ru lead cs why`, with `ru "logged_required" = ["u3"]` and `ru _ = []`):

| `lead`, cited sources `cs` | Result | Covers |
|---|---|---|
| yes, [unit u2.p3, unit u1] | `together ["u1"] []` | together ⇐ |
| yes, [unit u2.p3, background, pair a b] | `alone` | alone ⇐ (machinery names nothing) |
| yes, [unit u2.p3, fill a b] | `alone` | the same |
| yes, [unit u2.p3, rules logged_required] | `together ["u3"] []` | E2: a rule is named by its units |
| yes, [unit u2.p3, rules unwritten] (no unit) | `alone` | a word-list rule names no unit |
| yes, [unit u2.p3, definition adult] | `together [] ["adult"]` | E2: a definition is named |
| yes, [unit u2.p3, unit u1, definition adult] | `together ["u1"] ["adult"]` | both lists |
| yes, [unit u1] | `without ["u1"] []` | without ⇐; alone ⇏ (E2) |
| yes, [definition adult] | `without [] ["adult"]` | without, definitions only |
| yes, [] | `without [] []` | the claim needed nothing the author wrote |
| no, [unit u1] | `ruledOut` | lead ⇒ outcome |
| notSettled, [] | `notSettled` | |
| notNecessarily, [] | `notEnough` | |
| unknown, [], none | `unknown noResult` | UNKNOWN ⇐ |
| unknown, [], some conflictUnchecked | `unknown conflictUnchecked` | ask's reason kept |

Each iff has both directions here: `alone` holds in rows 2, 3 and 5 and fails in rows 1, 4, 6–10 (another unit or
definition named, or no reason cited). `together` holds in rows 1, 4, 6 and 7 and fails in rows 2, 3, 5 and 8–10.
`without` holds in rows 8–10 and fails in rows 1–7. The leads map one to one (rows 11–15), and a `yes` lead is never
`notEnough`, `ruledOut`, `notSettled` or `unknown`.

`citedUnits` and `citedDefinitions` (both directions of `mem_citedUnits`): over the sources [unit u2.p3, rules
logged_required, background, definition adult, rules unwritten, pair a b, fill a b, unit u1] they give (["u2.p3",
"u3", "u1"], ["adult"]). With used positions [0, 1, 2] they give (["u2.p3", "u3"], []): `u1` and `adult` are not
used, so not named. With [3, 7, 7, 0] they give (["u1", "u2.p3"], ["adult"]), in order of first use, once each.

**`eligible`** (S1's document as `Units`):

| Link or view | `eligible` |
|---|---|
| S1's link (u2.p3 → u2.p1, both asserted, CHECKED, with formulas) | `ok u2.p1 [u2.p3]` |
| relation `in order to` | `purpose` |
| denied | `denied` |
| target `norm` | `ruleTarget` |
| target under an active set | `readings` |
| reason without a formula (UNFORMALISED) | `noFormula` |
| target LABELLED | `noFormula` |
| two target parts | `noFormula` |
| a mention as target | `noFormula` |

**The reduced context** (a readings document with fixed assertions u1 "message(r)", t "logged(r)", u3 "logged(r)" —
the same formula as t — and p3 "message(r)"; choice `[]`; each proved by `rfl` for every frame):
- before: sources [u1, t, u3, p3];
- `withoutAssertion … "t"`: sources [u1, u3, p3], and exactly `filter (· ≠ unit t)` of the original;
- the formula-equal unit u3 is kept, with its formula `logged(r)`;
- 3 items remain.

† **The flattened parts** (E-f, SR 9; `rfl` in PE-5): the same document with fixed assertions over the flattened
parts u1 "message(r)", u2.p1 "logged(r)" (the target) and u2.p3 "message(r)". `withoutAssertion … "u2.p1"` keeps
u2.p3 and u1: sources [u1, u2.p3], exactly `dropTarget "u2.p1"` of [u1, u2.p1, u2.p3]. On the plain adapter,
`PlainParts.without p "u2.p1"` keeps the same two units, and its sources are the Background's followed by
[u1, u2.p3] (`PlainParts.sourced_without`).

**Route level** *(PE-5; sentence numbers are front-matter positions)*. Each fixture names its adapter (SR 9). The
plain fixtures share one environment and vocabulary, pinned here (SR 10):
- **Environment**: `relational-fol@0` with `documents@1` and `purposes@0`; no `norms@0` and no `readings@1`, so
  `routeOfDocument` gives `plain`. One sort, `item`, which may be empty (P0); unary predicates `request`, `from_user`,
  `message` and `logged` on `item`.
- **Formulas**: ψ (u2.p1, the target) `∀x:item. request(x) ∧ from_user(x) → logged(x)`; ρ (u2.p3, the reason)
  `∀x:item. request(x) ∧ from_user(x) → message(x)`. u2.p2 " because " has no content.
- **Models** (domains and true atoms; every other atom false): M1 `{i1}`, request, from_user, message and logged of
  i1. M2 `{i1}`, request, from_user and message of i1, not logged.
- **Evidence** is the plain case's (`certificate`, `negation`, `unsat`, `countermodel`, `model`), each bound to the
  reduced Γ′: the Background followed by the listed units' formulas in unit order. PE-5 records each certificate's
  bytes from the producer, as `tools/ask_fixtures.py` records ask's.

| # | Adapter | Document | Γ′ and the evidence it replays | Expected |
|---|---|---|---|---|
| S1 | plain | u1 "Every message is logged." `∀x:item. message(x) → logged(x)`; u2 "Every request from a user is logged because every request from a user is a message." (83 B; p1 [0,35) target, p2 [35,44) " because ", p3 [44,83) reason) | [u1, ρ]; `certificate` for ψ using u1 and u2.p3; `model` M1 | `together ["u1"] []`; lines: "The text gives this reason for "Every request from a user is logged": "every request from a user is a message."" and "VE checked that this reason is enough to conclude the claim together with sentence 1." |
| S2 | plain | S1 without u1 | [ρ]; `countermodel` M2 | `notEnough`, with M2's situation |
| S3 | plain | S1's u2, with u0 "Some request is from a user." `∃x:item. request(x) ∧ from_user(x)` and u1 "No request from a user is logged." `∀x:item. request(x) ∧ from_user(x) → ¬logged(x)` (SR 10) | [u0, u1, ρ]; `negation` certificate for ¬ψ using u0 and u1; `model` M2 | `ruledOut` (lead `no`: from everything else the text says, which includes that a qualifying request exists) |
| S3′ | plain | S3 without u0 (SR 10) | [u1, ρ]; `countermodel` M2, which contains a qualifying, unlogged request; no `negation` certificate exists, because with no qualifying request both ψ and u1 hold | `notEnough` (lead `notNecessarily`), with M2's situation. Never `notSettled`: `plain_never_split` |
| S4 | — (`eligible`) | a link whose target is a rule | no request is sent | `notChecked ruleTarget`; "VE does not check whether a reason is good enough for a rule." |
| S5 | plain | S1, with the producer's budget exhausted | [u1, ρ]; `model` M1 only | `unknown noResult`, with ask's reason sentence |
| S6 | plain | S1 with u1 "Every request is logged." `∀x:item. request(x) → logged(x)` | [u1, ρ]; `certificate` for ψ using u1 only; `model` M1 | `without ["u1"] []`; "VE checked that the claim follows from sentence 1 without this reason." |
| S7 | zero-set | `norms@0` under `norm-defaults@0`, no `readings@1`; S1's u2 with ρ, and a norm unit u3 "Logging a message is required." (an obligation on `logging_required(item)` under the guard `message(x)`); ψ `∀x:item. request(x) ∧ from_user(x) → logging_required(x)` | `premisesU` of [ρ]; `certificate` for ψ using ρ and `rules logging_required`; `conflict` packages; `model` | `together ["u3"] []`: the rule is named by its unit (`zeroRuleUnits`) |
| S8 | plain | S1 plus u3 "Every request from a user is logged." (ψ itself) | [u1, ρ, u3] | the target u2.p1 is never cited; u3 may be; the recorded verdict is `together` or `without`, as the producer's certificate uses ρ or u3 |
| † S9 | enumerated | `readings@1`, `norms@0` and `norm-defaults@0`; S2's u2 (sentence 1) and u3 (sentence 2) with the open set `rs_u3`: candidate 0 "Some request is a message" `∃x:item. request(x) ∧ message(x)`, candidate 1 "Some message is logged" `∃x:item. message(x) ∧ logged(x)` (SR 9) | per choice, `premisesU` of [ρ, the candidate]; choice `[(rs_u3, 0)]`: `countermodel` M2; choice `[(rs_u3, 1)]`: `countermodel` M2 with i2, message and logged; `conflict` packages for each | both rows `notEnough`, one group, one line, naming the witness row's reading although the verdicts coincide (SR 3): "VE found that this reason is not enough: in this situation, everything else the text says is true and the claim is false: S, reading sentence 2 as "Some request is a message"." |
| † S9b | enumerated | S9 with candidate 0 "Every message is logged" `∀x:item. message(x) → logged(x)` | choice 0: `certificate` for ψ using ρ and u3; choice 1: as S9 | two groups (12, choice 5): "If sentence 2 means "Every message is logged", VE checked that this reason is enough to conclude the claim together with sentence 2." and "If sentence 2 means "Some message is logged", VE found that this reason is not enough: in this situation, everything else the text says is true and the claim is false: S, reading sentence 2 as "Some message is logged"." |
| † S10 | enumerated (by profiles) | `readings@1`, `norms@0`, `soft-norms@0` and `norm-defaults@0`, the soft chain; u1 a default rule "Logging a message is required, unless the message is private." (mode `default`, with that exception); S1's u2, whose link is eligible; S9's u3 (SR 11) | — | refused with the text ask gives the same case, word for word: `admitNDFull`'s `InvalidInput: norm-defaults document is not well formed` (`Readings/UnspecifiedWire.lean:322`); no support rows. The fixture also replays ask on the same case and compares the two texts |
| † S11 | zero-set | `norms@0` under `norm-defaults@0`, with `documents@1` and `purposes@0`, no `readings@1`; the vocabulary above plus `checked` and `logging_required` on `item`; a norm unit u1 "Logging a message is required." (an obligation on `logging_required(item)` under the guard `message(x)`, default `unspecified`, so the text leaves it unsaid outside its guard); u2 "Logging every request from a user is required because every request from a user is checked.": ψ `∀x:item. request(x) ∧ from_user(x) → logging_required(x)`, reason `∀x:item. request(x) ∧ from_user(x) → checked(x)` (SR 10) | `premisesU` of [the reason]; `conflict` packages; `split`: base model `{i1}`, request, from_user and checked of i1, not message; filling `true` sets `logging_required`'s unsaid entry at i1 to true, filling `false` to false; `model`: the base model with filling `false` | `notSettled`, with the split's situation: "VE found that everything else the text says does not settle the claim: in this situation, it depends on what the text leaves unsaid: S." |
| † S12 | enumerated | S9 with seven further two-candidate open sets on other units: 128 compatible choices (SR 13) | — | refused with `ResourceLimit: There are more than 64 ways to read this document's open sentences. VE did not check them all.` (`replayError`); no support rows, and no verdict |
| † S13 | enumerated | S9's request with the case's `premises` `[ψ]` (SR 12) | — | `InvalidInput: the case does not ask this question (premises or assumed readings)` |
| † S14 | enumerated | S9's request with the case's `assumed` `[["rs_u3", 0]]` (SR 12) | — | the same text |

S3 and S3′ separate the two outcomes Astra's point needs. With an existence premise, everything else the text says
rules the claim out. Without one, it does not entail the claim's negation, because with no qualifying request both
universals hold, so the outcome is the countermodel's. S11 gives `notSettled` its route-level fixture, on the
zero-set adapter, where a split is one base situation with two admissible fillings of what the text leaves unsaid.

### 9.7 Lines

`says` (computed):
- F1 (the source's own bytes): The text gives this purpose for "We want Claude to figure out the most plausible
  interpretation of a query": "give the best response."
- F2: The text says this is not the reason for "Although we're asking Claude to prioritize not undermining human
  oversight of AI above being broadly ethical,": "we think being overseeable takes precedence over being good."
- F3 l1: The text gives this as one reason, not the only one, for "We think this kind of self-endorsement matters":
  "it is good for Claude itself".
- F4 l1: The text says this is not the reason for "warrant caution before acting unilaterally": "Claude's reasoning
  is inherently worse than a human's".
- F4 l2: The text gives this reason for "warrant caution before acting unilaterally": "Claude's situation differs in
  important ways:"
- `sole`: The text says this is the only reason for "A": "B". `partly`: The text gives this as part of the reason
  for "A": "B".
- `closing` on "a", "a.", "a?", "a:", "a,": `"a".`, `"a."`, `"a?"`, `"a:"`, `"a,".` † The same five values after
  draft 2's refactor (`closing q = stop (quoted q)`).

`sideText` on S1's 83-byte source: reason u2.p3 → "every request from a user is a message."; target u2.p1 → "Every
request from a user is logged"; marker u2.p2 → "because". `displayOf` with ask's numbers u1 ↦ 1, u2 ↦ 2: part u2.p3
→ 2 (its parent's), u1 → 1, u9 → none. The verdict lines are 2.3's table.

† Draft 2's line fixtures (`#guard` in PE-2's `Examples.lean`, PE-5's for the support lines):
- **No two spaces** (SR 1): no line of 2.3's table, of this section's `says` lines, or of S1 to S11 contains two
  consecutive spaces. Draft 1's `without [] []` line, "VE checked that the claim follows from  without this reason.",
  fails this check; draft 2's passes.
- **E-b** (SR 2): `together ["u5.p1","u5.p3"] []`, with `u5.p1` and `u5.p3` parts of sentence 5 and the target
  elsewhere, prints "sentence 5", not "sentences 5 and 5".
- **E-c** (SR 2): F3 with both reasons asserted, link l1 (reason c.p3), and a proof that cites c.p3 and c.p5:
  `together ["c.p5"] []`, and because c.p5 is in the target's sentence, the line quotes it: "VE checked that this
  reason is enough to conclude the claim together with "values that are merely imposed on us by others seem likely to
  be brittle."" `sideText` of c.p5 ends with ".", so `stop` adds nothing.
- **F8** (SR 6): `sideText` of [h.p3, h.p4] on "A because B, C." is "B, C.".

† pe-rev's line fixtures (PE-R8; `#guard` in PE-2's `Examples.lean`), `linkLines` with `says` and `verdict` as 2.3
writes them:
- **F9**: "The text gives this purpose for "we believe every model should be honest.": "be safe,"."; "VE does not
  check whether it serves this purpose."; "This holds only under these readings of "we believe every model should be
  honest.": rationale and limiting."
- **F9a**: `[]` (no candidate holds the rule: the lines are withheld).
- **F10**: "The text gives this reason for "we may choose to keep a promise": "we value our word.""; "VE cannot check
  this reason yet: a side has more than one reading."; "The quotes above leave out "Sometimes" from the same
  sentence, which may limit what they say."
- F1 to F4 and F8: the lines above, unchanged.

### 9.8 Fixtures each later batch adds

- PE-2: F1–F8 as documents through `ve document check`; every existing document fixture byte-identical without
  `purposes@0` (`checkDocPurposes_absent`); `checkDocSetsView_answer` over every recorded document case; the section's
  binding fuzz (each member dropped, emptied, retyped, duplicated, reordered, an index pushed out of range →
  `CheckerUnavailable` or no visible change); 9.7's line fixtures; † F9, F9a and F10 as documents, the `under`
  member bound and fuzzed with the others (PE-R8). F2c–F2e stay function-level until a list holding a pack is
  covered (PE-7b's `events@0` first), which then adds them as documents (PE-R11).
- † PE-3 (pe-rev): u0146.s01's D6 (a) set with the third candidate `in-attitude`, pending (PE-R7); a synthetic rule
  in its shape whose `limiting` candidate holds the bound judgment, on a list with `documents@1`, `judgments@0`,
  `purposes@0` and `readings@1`, admitted with no E1 and its answer without the `purposes` member byte-identical
  (PE-R10, plan 2.5); D6 (c)'s
  "may choose to" frame on F10's source, and "We decided to keep the promise because we value our word." as the
  named GAP `motive_frame` with no link (PE-R9).
- PE-3 (SR 4): authored S1's u2, "Every request from a user is logged because every request from a user is a
  message.", is one MIXED unit with an affirmed, `plain` `because` link from p3 to p1; "… only because …" gives
  `sole` and "… partly because …" gives `partly`. Authored "Claude does not refuse because the user is rude." is
  refused with 2.2's first row and both rewrites, and so is "Claude refuses not only because the user is rude.".
- PE-5: S1–S14, each on its named adapter; the support binding fuzz (each member of `support` dropped, retyped,
  duplicated, reordered; a row's choice naming another set or repeated; a plain answer with two rows →
  `CheckerUnavailable`); a request whose target has a reading set → 7.3's text.

## 10. Layers, files and owners

| File | Layer | Owner | Batch |
|---|---|---|---|
| `lean/VE/Purposes/Decl.lean`, `Wire.lean`, `WellFormed.lean`, `Examples.lean` | 2 (default) | purposes | PE-1 |
| `lean/VE/Route/Inert.lean` (namespace `VE.Route.Admission`) | 2 | route admission | PE-1 |
| `lean/VE/Purposes/Verdict.lean` (`Support`, its wire, `eligible`), `English.lean` | 4 (new row in `tools/layer_policy.py`: they import `VE.Ask`) | purposes | PE-2 |
| `lean/VE/Service/DocumentPurposes.lean` | 4 (`VE.Service.`) | purposes, in the document mode | PE-2 |
| `checkDocSetsView`, `CheckedView`, `activeKinds` in `lean/VE/Service/Document.lean` | 4 | the document model | the checked-view refactor, before PE-2 |
| `profileKeys`, `documentMetadataFor` in `lean/VE/Discourse/Loader.lean` | 2 | W2's loader | PE-2 |
| `dropTarget`, `sourced_dropTarget`, `PlainParts.without`, `ZeroParts.without`, `withoutAssertion`, `supportSourced` and their theorems in `VE.Ask` | 4 | question-answering | PE-5 |
| `lean/VE/Purposes/Support.lean` (the verdict, the adapter theorems, `SupportRow`, `replaySupport`, `support_wire_sound`) | 4 (the same row) | purposes | PE-5 |
| one hunk in `VE.Ask.Run.askCase` (`support` in place of `question`; it calls `replaySupport` with `routeOfDocument`) | 4 | question-answering | PE-5 |

## 11. Elaboration record

- **Stub**: `lean/SpecStubs_purpose-explanation.lean`, scratch, never committed (it holds `sorry`). The sandbox
  refused `rm`, so the file stays untracked in the worktree and no commit adds it. The modules were built with
  `lake build VE.Ask.Render VE.Ask.Sound VE.Discourse.Loader VE.Norms.Admission` on this branch (`main` at
  `6d0a10526` plus documents only). The stub was then checked from `lean/` with
  `lake env lean SpecStubs_purpose-explanation.lean`.
- **Result**: exit 0. Every statement in sections 1–6 elaborates; the only warnings are `declaration uses 'sorry'`
  for the unproved statements and their stub bodies.
- **Proved in the stub** (no `sorry`): `Kind.inert_active`, `normRole_inert`, `inForce_inert`,
  `Relation.wire_mem`, `Relation.ofWire_wire`, `Relation.wire_ne_prevents`, `decodeBlock_relations`,
  `supportOf_checked` and `checkDocPurposes_absent`; the reduced-context fixtures of 9.6 by `rfl`.
- **Found by the stub, and fixed here**:
  - `Share.partial` cannot be declared, because `partial` is a Lean keyword. It is now `partly` (draft 1's 2.1 would
    not have compiled).
  - `VE.Readings.Reason` and `VE.Ask.Reason` are ambiguous under `open VE.Readings`, so the soundness theorems name
    `VE.Ask.Reason`.
  - A quote that ends the sentence would get a second full stop (`…good."."`); `closing` (2.3) fixes it.
  - Draft 1's `Decl.lean` imported `VE.Ask.Basic` (layer 4) into a layer-2 file, which `tools/check_lean_imports.py`
    refuses. `Support` moved to `Verdict.lean`.

### 11.1 Draft 2: written without elaboration

Draft 2 was written in a pass whose sandbox refused every shell command, so neither `lake env lean` nor `#eval` ran.
The stub was not changed. The following are new or changed in draft 2 and **not yet elaborated**. Every value they
give is derived by hand and marked †:
- 2.3: `quoted`, `stop`, `closing` (refactored), `sideText_eq`, `Naming`, `ownSentence`, `Naming.of`, `others`,
  `verdict`, `supportLines`; the † rows of the line table.
- 4.2 to 4.4: `sideAdjacent`, `sidesAdjacent`, `shareOk`, the `check` step 4a, `WellFormed`, `sideAdjacent_iff`,
  `shareOk_iff`.
- 6.1: `dropTarget`, `mem_dropTarget`, `dropTarget_target`, `sourced_dropTarget`, `PlainParts.without` and its two
  theorems, `ZeroParts.without` and its three theorems, and the restated `sourcedAssertions_withoutAssertion` and
  `supportSourced_eq`.
- 6.2: the five plain and zero-set theorems.
- 6.4: `Adapter`, `SupportRow`, `SupportRow.verdict`, `CertOk`, `SupportRowOk`, `SupportAsked`, `replaySupport`,
  `support_wire_sound`, `supportJson`, `supportJson_rows`.
- 9.2, 9.3, 9.6 and 9.7: the † fixtures.
- pe-rev (2026-11-02, also written with no Lean run): `Part.readings`, `Units.packSources`, `packsInert`,
  `targetKind`, `holdsTarget`, `shownUnder`, `unlinkedActive`, the `check` step 6a, `WellFormed`'s new conjunct,
  `packsInert_iff`, `packsInert_nil`, `shownUnder_iff`, `unlinkedActive_iff` (4); `underLine`, `scopeLine`,
  `linkLines`, `linkLines_plain`, `linkLines_withheld` (2.3); `CheckedView.readings`, `CheckedView.packSources`,
  `checkDocSetsView_readings`, `checkDocSetsView_packs` and the obligation `packSources_complete` (5.1); `purposesUnits`' two new fields (5.3);
  fixtures F2c–F2e, F9, F9a, F10 and their lines (9.2, 9.7).

Every name these statements use from `main` was checked by reading the source at `545ca9685`: `PlainParts`,
`PlainRow`, `PlainRowOk`, `PlainRow.toRow`, `plain_lead_sound`, `plain_never_split`, `Consistent` (`Ask/Plain.lean`,
`Ask/PlainWire.lean`, `Ask/PlainAnswer.lean`); `ZeroParts`, `ZeroParts.assertions`, `ZeroParts.sourced`,
`ZeroParts.premises`, `RowOkU`, `leadU_sound`, `zeroRuleUnits` (`Ask/ZeroWire.lean`, `Ask/ZeroAnswer.lean`); `Row`,
`RowOk`, `SplitU` (`Ask/Basic.lean`); `sourced`, `cited`, `usedPositions` (`Ask/Sources.lean`); `readingClause`,
`readingSuffix`, `named`, `View` (`Ask/Lines.lean`); `groups`, `assignment` (`Ask/Groups.lean`); `routeOfDocument`,
`replayError` (`Ask/Run.lean`); `VE.Readings.Wire.fullEnv` and `normsShaped_of_ND` (`Readings/VerdictsWire.lean`);
`choiceX_normsShaped` (`Readings/SoftDefaults.lean`); `admitNDFull` (`Readings/UnspecifiedWire.lean`);
`VE.Readings.Compatible` (`Readings/Choice.lean`); `VE.Readings.choiceJson` (`Readings/Route.lean`). Before PE-1
starts, the stub gains these statements and is elaborated once; any statement that fails is fixed in this document
first. That run checks the gate's text and does not reopen it (SR 14).

## 12. Choices this draft made (for the statement review)

1. **The inert kinds** are `explanation`, `exposition`, `example`, `analogy` and `meta`. `question` and `instruction`
   are excluded because speech-acts gives them roles (`SpeechActs/Wire.lean:493-498`). `unformalised _` is excluded
   because it is not needed.
2. **`sole` against a `partly` or `notSole` link with the same reason** is refused, by the statement review (SR 5,
   E-d). A text that says both "only because B" and "not only because B" of one target has no one reading of how many
   reasons it gives. A4 settled duplicate links, which stay accepted (F7a): the same reason given twice with share
   `plain` or `sole` is one reason.
3. **An eligible link's reasons must themselves be stated, checked formulas** (kind `asserted`, CHECKED or OPEN,
   with a formula). Otherwise "not enough" would only report that a side was never formalised. A reason that is a
   rule (kind `norm`) gets `noFormula` for now.
4. **`eligible` lands with PE-2**, in `Verdict.lean`. It reads only the checked view, so the section can say which
   links get a question (`ask`) before PE-5 relays the answer. Until then an eligible link shows its `says` line
   alone.
5. **Several rows** (other units' reading sets): one verdict per row, and the lines follow ask's grouping and reading
   clauses exactly (SR 3, `supportLines`). With two or more groups, each line starts with ask's R1 clause for its
   group. A line that shows a situation names every open set's reading of its witness row, even when every row has the
   same verdict (S9, S9b).
6. **Identities**: the base answer runs on the lowered request, so its `document_id` excludes the block, and
   `purposes_id` binds the block. The alternative is scope's rule ("identities are the document's as written"),
   which would need the document mode to take the block as written. This draft keeps the plan's form.
7. **Quotes are not cut.** Ask's C1 rule quotes the whole trimmed text, so draft 1's 160-byte cut is dropped.
8. **Diagnostics are new texts** under `InvalidPurposes:`; the C6 contract registers them.

Draft 2 made these further choices while applying the review's ruling. Each one is the smallest reading of its item.
9. **Where an own-sentence quote goes** (SR 2). `others` names the other sentences first, then the definitions,
   then the quoted parts, each bare. `stop` ends a `together` line, so a final quote gets `closing`'s full stop. The
   `without` line keeps draft 1's wording, so its quote stays mid-line.
10. **Fault 4a** (SR 6). The adjacency fault sits after fault 4 and is numbered 4a, so every other text keeps its
    number.
11. **The support request** (SR 7). It is ask's request with `support` in place of `question`, so the adapter's
    case, binding and refusals are ask's unchanged. The premises and assumed-reading row reuses ask's text
    (`Ask/Wire.lean:333`), because it is ask's check.

## 13. Converged edits and DRI rulings → sections

| Edit or ruling | Where |
|---|---|
| E1 (target removed; "everything else the text says") | 6.1, 6.2 (`notEnough_sound` and its siblings), 2.3 |
| E2 (rules by `ruleUnits`; definitions named; a reason must be cited for `alone`; the "without" outcome) | 6.2 (`named`, `supportOf`, `without_sound`), 9.6 |
| E3 (PE-7a removed; u111 to rights' `L29`) | 0 (out of scope); plan 0, 3 |
| E4 (PE-6: explicit audited rule list; no bytes) | plan 2.7, PE-6 |
| E5 (rd-9 inventory rows) | 5.4, 6.4 |
| E6 (`Support` NEW under D8; lines reuse ask and `VE.Words`) | 2.3 |
| E7 (C2 named) | plan PE-0p |
| A2 (positive nonfactivity, proved from provenance, over candidates and mentions) | 3, 4.2, 4.4 |
| A3 (the checked view; `sameUnit` replaced by PE-4) | 4.1, 5.1, 5.3 |
| A4 (`partly`/`notSole` need no other link; duplicates are one reason; PE-E1 never narrows) | 4.2, 4.4, 9.2, 9.3, 2.2 |
| A5 (CI-7 and speech-acts × `documents@1`: C21) | plan 8; out of scope here |
| A6 ("since" extends ET-5's row; C6; no `supportOfFollowable`) | 2.2, 5.4; plan 2.7 |
| Astra round 3 (formula-equal units kept; evidence bound to the reduced context; FOLLOWABLE shown separately; S10 contract) | 6.1, 6.4, 9.6 (S8); plan 2.7; 5.4 |
| DRI 2 (owners) | 3, 5.1, 5.2, 6.1, 10 |
| DRI 3 (C21, C2, C6, D9, C1, rights, boundaries, Q4) | plan 8 |
| DRI 4 (order; PE-E1 authorised, never narrowing) | plan 0, PE-E1 |

The statement review's ruling (`manage-agents/debates/purpose-explanation-spec/DRI-RULING.md`), item by item. The
plan carries each item too (plan 9).

| Item | Where in this document |
|---|---|
| SR 1 (E-a: `without [] []` sentence; no two spaces) | 2.3 (`verdict`, rules, table), 9.7 |
| SR 2 (E-c before E-b: own-sentence parts quoted; numbers deduplicated) | 2.3 (`Naming`, `ownSentence`, `others`, `stop`, table), 9.7, 12 (choice 9) |
| SR 3 (reading clauses exactly as ask's; witness lines name every open set's reading) | 2.3 (rules, `supportLines`), 6.4, 9.6 (S9, S9b), 12 (choice 5) |
| SR 4 (E-e: inline `<A> because <B>.` rows, affirmative only; negation refused) | 2.1, 2.2, 9.8 (PE-3) |
| SR 5 (E-d: `sole` against `partly` or `notSole`; `shareOk_iff`; F7e) | 4.2, 4.4, 7.2 (text 8), 9.2 (F7e, F7f), 9.3, 12 (choice 2) |
| SR 6 (`sidesAdjacent`; `WellFormed` and `check_ok_iff`; fault after 4; `sideText_eq`; two fixtures) | 4.2, 4.3, 4.4, 2.3 (`sideText_eq`), 7.2 (fault 4a), 9.2 (F8, F8a, F8b), 9.7, 12 (choice 10) |
| SR 7 (Q1 as ask's case; flattened parts; `dropTarget`) | 0, 6.1, 6.4, 9.6, 12 (choice 11) |
| SR 8 (adapter theorems in full; reduced premises filtered; source to formula) | 6.1, 6.2 |
| SR 9 (fixtures name their adapter; S9; E-f `rfl` fixture) | 9.6 |
| SR 10 (S3 with existence; S3′ `notEnough`; a genuine split fixture; all pinned) | 9.6 (S3, S3′, S11, the pinned environment) |
| SR 11 (soft support deferred; no new text; S10) | 0, 6.1, 6.4, 7.3, 8 (item 9), 9.6 (S10) |
| SR 12 (no premises, no assumed; rows equal as lists; `support_wire_sound`; two refusals) | 6.4, 7.3, 8 (item 7), 9.6 (S13, S14) |
| SR 13 (past 64 choices: ask's `ResourceLimit`, no rows, no aggregate UNKNOWN) | 2.3 (table note), 6.4, 7.3, 8 (item 8), 9.6 (S12) |
| SR 14 (the gate: one check against SR 1–13) | header, 11.1 |

The 2026-11-02 re-pilot's findings (`manage-agents/reviews/dri-decisions-20261102-fp-purpose-explanation.md` item 1;
pe-rev). The plan carries each too (plan 10.3).

| Finding | Where in this document |
|---|---|
| PE-R6 (a purpose only being considered: commands-imperatives' question object, a named GAP) | plan only (PE-7b, 4, 8); no statement here changes |
| PE-R7 (D6 (a) beside an attitude: the `in-attitude` candidate, attitudes' slot, pending) | 2.3 (the line not shown under it), 9.2 (F9), 9.8 (PE-3) |
| PE-R8 (a link's line only under the candidates that hold its target; a scope the line cannot name) | 1.3, 2.3 (rules, `underLine`, `scopeLine`, `linkLines`), 4.1 (`readings`), 4.2 (`targetKind`, `holdsTarget`, `shownUnder`, `unlinkedActive`), 4.4, 5.1 (`readings`), 5.3, 5.4 (`under`), 8 (item 10), 9.2 (F9, F9a, F10), 9.7, 9.8 |
| PE-R9 (D6 (c)'s frames, "may choose to" included; other frames a named GAP) | 9.2 (F10), 9.8 (PE-3); the frames are plan D6 (c) |
| PE-R10 (`judgments@0` in PE-3 with its composes argument; no other list named) | 5.3, 9.8 (PE-3); plan 2.5 |
| PE-R11 (pack premises: `packsInert`, fault 6a; `checkDocSetsView_packs`; `packSources_complete`) | 1.3, 4.1 (`packSources`), 4.2, 4.3, 4.4, 5.1, 5.3, 7.2 (6a), 8 (item 2), 9.2 (F2c–F2e) |
| C (`markersLinked` and an unlinked causal "because") | 4.2 (prose) |
| C (rule 12's placement on the rule's part) | plan D6 (a) |
