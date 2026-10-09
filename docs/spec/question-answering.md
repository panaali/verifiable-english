# Question answering in VE, Q1 and Q2 (statement specification)

> Status: statement specification, draft 1 with Q0 review corrections (2026-10-09), branch `design/question-answering`. This is the item-1
> statement spec (batch Q0) of [question-answering-PLAN.md](question-answering-PLAN.md) draft 2 (the **plan**),
> which the plan review converged on (`manage-agents/debates/design-question-answering/`, Astra and Fable, round 3:
> BUILD after draft 2, with Q0's statement review as the single gate). It writes out plan sections 3 and 4 as
> definitions, English with one reading each, diagnostics in order, exact Lean statements, limits and acceptance
> fixtures. A section number written `plan 4.3` refers to the plan; `R1` to `R14` are the plan's draft-2 edits
> (plan 0.1).
> The Q0 statement review (`manage-agents/debates/question-answering-spec/`, round 3) converged on FIX overall.
> The accepted Q1 reading work may begin; the corrected span definition and guards need a targeted joint check
> before Q1.1 completes or Q1.2 starts. Q2 awaits merged RD-3 and review of these corrected statements and fixtures.
>
> **Nothing is proved and nothing is built.** The original stub runs described below predate the Q0 corrections;
> the corrected span mapper was separately elaborated and its affected fixtures recomputed. What was run for this
> draft (section 11):
> - a Q1 stub, `lean/SpecStubs_question-answering.lean`, against a build of this branch's base commit
>   `c85797de`. It holds every Q1 definition of section 2 with its body and every Q1 statement of 5.1 as a
>   definition of type `Prop`. All of them elaborate. Every Q1 fixture of section 7 marked *computed* was
>   evaluated by `#eval` through E2.6's own `lexSpans`, `lex`, `read`, `grammarFault`, `diagnose`, `advice` and
>   the vocabulary policy's lexicon (`portLex`);
> - a Q2 stub, `lean/SpecStubs_question-answering-q2.lean`, against a build of RD-3's branch
>   (`readings-defaults/rd3` at `70cc2549`; RD-3 is **not merged**). It holds the Q2 definitions of 5.2 and every
>   Q2 statement as a `Prop`. All of them elaborate (one linter warning, 11.2). The row, reason, fold and group
>   fixtures of 7.6 were evaluated by `#eval`.
>
> Neither stub is committed, and no `sorry` is (the stubs contain none). They remain untracked in the worktree.
> The original definitions and statements were sections 2 and 5 before the Q0 corrections; section 11.1 records
> the targeted span check. Not run: anything in Python, the service, the evidence generators
> (prover, Rust search, flip search), any proof. Every Q2 lead in section 7 is therefore *derived*, pending RD-3's
> merge and a run of the generators (plan Q0, R14).

## 0. Scope, and what the computation changed

A question is one of the document's own sentences, asked (plan 0). Q1 reads it with the unchanged English reader
`read`; Q2 answers it with RD-3's checked rows and renders the answer in Lean. This file fixes the terms (1), the
question reader (2), the English and its one reading (3), the diagnostics in order (4), the exact statements (5),
the limits (6), the acceptance fixtures (7), the wire (8), the review checklist (9), open points (10) and how the
figures were computed (11).

Computing the fixtures overturned parts of the plan's derived text. The statement review should read these first.

| # | Finding | Evidence | What this spec does |
|---|---|---|---|
| F1 | **The plan's G document has no reading.** Python's vocabulary policy, as Lean's port computes it, refuses the wordings `{0} is a citizen`, `{0} is a person` and `{0} is an adult` and the noun `member of the group`. The lexicon it selects is `{0} is classified as "citizen"` (and so on) and `entity of sort "member"`, so all three sentences are `.stopped 0 .noDerivation`. | 11.3, run 1 | Plan 6.1 says "Q0 rewrites the fixture, not the grammar". 7.1 rewrites G with the wordings `{0} is registered`, `{0} is eligible` and `{0} is verified` and the noun `member`, which the policy accepts and whose three sentences read. Every G question is rewritten to match. |
| F2 | **No fixture produces "many meanings".** No question of section 7 has two candidates with different meanings. The outcome is reachable by construction, but this spec has no natural example. | 7.2 to 7.5 | `readQuestion_meanings` (5.1) states what the outcome claims. Q1.3's reverse corpus measures how often it occurs (plan Q1.3). Open point 10.1. |
| F3 | **A space before `?` got a text about periods.** E2's `BadSpacing` text says "write no space before a period", but the period is the one Q1 added. | G15 | A question-specific text (4.1, row 5). |
| F4 | **Two gaps can give the same sentence.** In G11, fronting at the gaps before `is` and before `eligible` both give `every member who registered is is eligible.` | G11 | Nothing changes: the candidates differ in their gap, so `candidates` has no duplicate; both have no derivation. Recorded. |
| F5 | **The closest candidate is often the first.** When every candidate fails at the same token, the tie goes to the leftmost, whose sentence puts the moved word second (A9, U1, U8). The diagnosis is then about a sentence the user did not mean. | A9, U1, U8 | The rule stays as the plan states it, and the text names the sentence tried (`Closest sentence tried: "…"`), so nothing is hidden. A body that begins with `a` or `an` also gets the advice `Write "every" or "some" in place of "an".` Open point 10.2. |
| F6 | **The plan's U1 diagnosis was guessed wrong.** E2.6's diagnosis of the closest candidate of U1 lists `must be spared exclusion from education`, `must receive elementary education` and `is classified as "has_the_right_to_education"` as nearest wordings, not the equal-access wording. | U1 | 7.5 records the computed text. |
| F7 | **U4 confirmed: no reading.** The policy selects `{0} is classified as "has_the_right_to_education"`, so `Is it the case that every person has the right to education?` has no reading. | U4 | As the plan foresaw: the vocabulary defect is reported to the vocabulary owner. |
| F8 | **The agent policy's conflict confirmed.** `results.json`, M9: `witness:permitted` is CONFLICT; the mutant m1 (rule 3 added to rule 14's exception list, `usecases/agent-policy/mutants.py`) is CONFLICT-FREE. | 7.4 | R6's conflict-free variant is m1. 7.4 says so. |
| F9 | **The outcome type is finer than the plan's.** The plan's `Outcome.many c d rs` (with `d = c` for one candidate with two derivations) is split into `meanings` and `ambiguous`; `indefinite` carries the article; a question with another first word is `form`, not `none`; the size limits are `limit`, apart from the work budget `budget`. | 2.4 | 2.4 and 5.1 use the finer type. The statements say the same things about it. |
| F10 | **The response status is E2's `rejected`**, not the plan's `refused`, so `english.read` and `english.question` share a relay table. | 4.1, 8 | Plan 4.8's status list changes accordingly. |

## 1. Terms

| Term | Meaning |
|---|---|
| question | a text that ends with its only `?` |
| form | F1 (`Is it the case that <body>?`) or F2 (`<Aux> <rest>?`, with `<Aux>` a capitalised auxiliary) |
| auxiliary | a word of `auxs`: `is`, `must`, `may` for `ve ask`; `is` for speech acts (Q1.4) |
| body | F1's text after the frame, or F2's rest, without the `?` |
| gap | in F2, the byte offset in the rest of a token after the first that is not punctuation |
| candidate | a sentence Lean builds from the question: F1's `body ++ "."`, or F2's rest with the auxiliary put back at one gap, ending with `.` |
| asked sentence | the candidate the question is read as; the answer's first line shows it |
| meaning | the formula `φ` of a candidate that reads `[(φ, false)]`: one sentence, one derivation, a meaning, no conclusion mark |
| reading of a question | the one meaning of its candidates, under 3.5's order (`QuestionOneReading`, 5.1) |
| row | what Lean checked of the asked formula under one compatible choice (plan 4.2) |
| lead | the first sentence of an answer: yes, no, not settled, not necessarily, unknown (plan 4.1) |
| group | rows with the same lead, the same cited sources (for yes and no) and the same readings of the relevant sets (R7) |

## 2. Q1: the question reader (`lean/VE/Question/Read.lean`)

The original definitions were elaborated in the stub against `c85797de` (11.1). The corrected §2.5 mapping was
elaborated separately, with its affected fixtures recomputed. Its bounds theorems still need the targeted joint
check. Q1.1 may change a body only to prove a reviewed statement of 5.1; a statement change reopens its review.

### 2.1 Constants and the question's shape

```lean
namespace VE.Question
open Lean VE.EnglishGrammar
open VE.Grammar (Derives)

def auxiliaries : List String := ["is", "must", "may"]
def caseFrame : String := "Is it the case that "
def whWords : List String := ["Who", "What", "Which", "Whom", "Whose", "Where", "When", "Why", "How"]
def maxQuestionBytes : Nat := 4096
def maxTokens : Nat := 300
def maxCandidates : Nat := 64

inductive Form
  | caseThat
  | fronted (aux : String) (gap : Nat)
  deriving DecidableEq, Repr

structure Candidate where
  form : Form
  sentence : String
  deriving DecidableEq, Repr

inductive Shape
  | caseThat (body : String)
  | fronted (aux rest : String)
  | other (first : String)
  | notQuestion
  deriving DecidableEq, Repr

def questionMarks (q : String) : Nat := (q.toList.filter (· == '?')).length

/-- F1 takes precedence: a question whose text before the `?` begins with `caseFrame` is F1. -/
def shape (auxs : List String) (q : String) : Shape :=
  if !q.endsWith "?" || questionMarks q != 1 then .notQuestion
  else
    let s := q.dropRight 1
    if caseFrame.isPrefixOf s then .caseThat (s.drop caseFrame.length)
    else match auxs.find? (fun a => (capitalise a ++ " ").isPrefixOf s) with
      | some a => .fronted a (s.drop (a.length + 1))
      | none => .other ((s.splitOn " ").headD "")

def Shape.body : Shape → Option String
  | .caseThat t => some t
  | .fronted _ r => some r
  | _ => none

/-- Where the body starts in the question, in bytes. -/
def Shape.offset : Shape → Nat
  | .caseThat _ => caseFrame.utf8ByteSize
  | .fronted a _ => a.utf8ByteSize + 1
  | _ => 0
```

### 2.2 Gaps and candidates (R1)

```lean
def isPunct : Tok → Bool
  | .punct .. => true
  | _ => false

/-- The body's one sentence `t ++ "."` as tokens with spans; `none` unless it lexes to exactly one sentence. `lexSpans`
    refuses a final sentence without `.` (`Lexer.lean:265`), hence the added `.`. -/
def bodySentence (t : String) : Option (Array Spanned) :=
  match lexSpans (t ++ ".") with
  | .ok ss => if ss.size == 1 then ss[0]? else none
  | .error _ => none

/-- F2's gaps: the byte offsets in `rest` of every token after the first that is not punctuation. The added `.` is not
    a token, so no gap is at the end. -/
def gaps (rest : String) : List Nat :=
  match bodySentence rest with
  | some toks => (toks.toList.drop 1).filterMap fun (t, a, _) => if isPunct t then none else some a
  | none => []

def insertAt (rest a : String) (g : Nat) : String :=
  rest.extract ⟨0⟩ ⟨g⟩ ++ a ++ " " ++ rest.extract ⟨g⟩ rest.endPos ++ "."

def candidates (auxs : List String) (q : String) : List Candidate :=
  match shape auxs q with
  | .caseThat t => if (bodySentence t).isSome then [⟨.caseThat, t ++ "."⟩] else []
  | .fronted a r => (gaps r).map fun g => ⟨.fronted a g, insertAt r a g⟩
  | _ => []
```

No other byte changes: the user's words keep their case, and a sentence-initial lower-case keyword such as `every`
is accepted by the existing `kw` terminal (`Token.lean:74`).

### 2.3 What one candidate gives (R2)

```lean
inductive Got
  | none                         -- no derivation
  | one (φ : EFormula)           -- one derivation, a meaning, no conclusion mark
  | many                         -- two derivations
  | refused (o : ReadOutcome)    -- a derivation without a meaning, or a conclusion mark
  | budget
  | notOne                       -- the candidate does not lex as exactly one sentence

/-- The sentence count is checked before `read`'s outcome, so `.stopped _ o` is sentence 0's. -/
def got (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (c : Candidate) : Got :=
  match lex c.sentence with
  | .error _ => .notOne
  | .ok ws =>
    if ws.size != 1 then .notOne
    else match read E O L b c.sentence with
      | .ok [(φ, false)] => .one φ
      | .stopped _ .noDerivation => .none
      | .stopped _ (.ambiguous _ _) => .many
      | .stopped _ .budget => .budget
      | o => .refused o

def Got.isNotOne : Got → Bool | .notOne => true | _ => false
def Got.isBudget : Got → Bool | .budget => true | _ => false
def Got.isMany : Got → Bool | .many => true | _ => false
def Got.isRefused : Got → Bool | .refused _ => true | _ => false
def Got.meaning? : Got → Option EFormula | .one φ => some φ | _ => Option.none

/-- The first candidate of each distinct meaning, in candidate order. -/
def firstMeanings (gs : List (Candidate × Got)) : List (Candidate × EFormula) :=
  gs.foldl (fun acc (c, g) => match g.meaning? with
    | some φ => if acc.any (·.2 == φ) then acc else acc ++ [(c, φ)]
    | Option.none => acc) []

/-- F1's question for a candidate: `Is it the case that <sentence without its ".">?`. -/
def caseThatQuestion (c : Candidate) : String := caseFrame ++ c.sentence.dropRight 1 ++ "?"
```

### 2.4 The order, and the outcome (R3, F9)

The order is the plan's (3.5, kept by R3): the vocabulary, the question's shape, its size, the lexing of its body,
the candidates; then any candidate that is not one sentence, any budget, any candidate with two derivations, the
meanings (one, or many), any refusal, else none, with the indefinite help (3.2) when it applies.

```lean
inductive Outcome
  | one (c : Candidate) (φ : EFormula)
  | meanings (firsts : List (Candidate × EFormula)) (rephrasings : List String)
  | ambiguous (c : Candidate)
  | indefinite (article : String) (rephrasings : List String)
  | none (closest : Option Candidate)
  | refused (c : Candidate) (o : ReadOutcome)
  | form (wh : Bool)
  | text (o : ReadOutcome)        -- the vocabulary refused, or the body's lexing
  | notQuestion
  | limit
  | budget (c : Candidate)

/-- 6's limits on a question: its bytes, the tokens of its body, its candidates. -/
def withinLimits (auxs : List String) (q : String) : Bool :=
  decide (q.utf8ByteSize ≤ maxQuestionBytes) &&
  (match (shape auxs q).body with
   | some t => match bodySentence t with
     | some toks => decide (toks.size ≤ maxTokens)
     | none => true
   | none => true) &&
  decide ((candidates auxs q).length ≤ maxCandidates)

def classify (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Outcome :=
  match grammarFault E O L with
  | some g => .text (.invalidGrammar g)
  | none =>
    match shape auxs q with
    | .notQuestion => .notQuestion
    | .other w => .form (whWords.contains w)
    | sh =>
      if q.utf8ByteSize > maxQuestionBytes then .limit else
      match lexSpans ((sh.body.getD "") ++ ".") with
      | .error r => .text (.lexical r)
      | .ok ss =>
        if ss.size != 1 then .notQuestion
        else if ss.any (·.size > maxTokens) then .limit
        else
          let cs := candidates auxs q
          if cs.length > maxCandidates then .limit
          else
            let gs := cs.map fun c => (c, got E O L b c)
            if gs.any (·.2.isNotOne) then .notQuestion
            else match gs.find? (·.2.isBudget) with
            | some (c, _) => .budget c
            | none => match gs.find? (·.2.isMany) with
              | some (c, _) => .ambiguous c
              | none =>
                match firstMeanings gs with
                | [(c, φ)] => .one c φ
                | [] => match gs.find? (·.2.isRefused) with
                  | some (c, .refused o) => .refused c o
                  | _ => .none (closest E L cs)
                | fs => .meanings fs (fs.map fun x => caseThatQuestion x.1)

/-- The every and the some questions, when the body begins with the token `a` or `an`. -/
def swap (frame t : String) : Option (String × String × String) :=
  if "a ".isPrefixOf t then some ("a", frame ++ "every " ++ t.drop 2 ++ "?", frame ++ "some " ++ t.drop 2 ++ "?")
  else if "an ".isPrefixOf t then some ("an", frame ++ "every " ++ t.drop 3 ++ "?", frame ++ "some " ++ t.drop 3 ++ "?")
  else none

def indefiniteSwaps (auxs : List String) (q : String) : Option (String × String × String) :=
  match shape auxs q with
  | .caseThat t => swap caseFrame t
  | .fronted a r => swap (capitalise a ++ " ") r
  | _ => none

/-- The questions of `qs` that read with one meaning, each meaning once, in order. -/
def offered (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (qs : List String) : List String :=
  (qs.foldl (fun (acc : List (String × EFormula)) r => match classify auxs E O L b r with
    | .one _ φ => if acc.any (·.2 == φ) then acc else acc ++ [(r, φ)]
    | _ => acc) []).map (·.1)

def readQuestion (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Outcome :=
  match classify auxs E O L b q with
  | .none cl =>
    match indefiniteSwaps auxs q with
    | some (art, qe, qs) =>
      let rs := offered auxs E O L b [qe, qs]
      if rs.isEmpty then .none cl else .indefinite art rs
    | none => .none cl
  | o => o
```

### 2.5 The closest candidate, and spans on the question

```lean
def diagnosisOf (E : Env) (L : Lexicon) (c : Candidate) : Option Diagnosis :=
  match lexSpans c.sentence with
  | .ok ss => (ss[0]?).bind (diagnose E L c.sentence)
  | .error _ => none

/-- The candidate whose diagnosis span starts furthest right, in its own bytes; ties go to the leftmost. Candidates
    without a diagnosis (the budget did not allow finding it) are skipped. -/
def closest (E : Env) (L : Lexicon) (cs : List Candidate) : Option Candidate :=
  (cs.foldl (fun (best : Option (Candidate × Nat)) c => match diagnosisOf E L c, best with
    | some d, some (_, k) => if d.span.1 > k then some (c, d.span.1) else best
    | some d, none => some (c, d.span.1)
    | none, _ => best) none).map (·.1)

/-- A candidate's byte offset on the question. F1: moved right by the frame. F2: before the gap, moved right by the
    auxiliary and its space; the put-back word maps to the question's first word, its following space to the
    question's first space, and the suffix stays at the same byte offsets. -/
def mapPoint (c : Candidate) (off x : Nat) : Nat :=
  match c.form with
  | .caseThat => x + off
  | .fronted a g =>
    let n := a.utf8ByteSize
    let k := n + 1
    if x < g then x + k else if x < g + n then x - g
    else if x < g + k then n + (x - (g + n)) else x

/-- The image of the intersection of `[start, stop)` with one candidate region `[lo, hi)`, whose image begins at
    `dst`. The four F2 regions are each order-preserving, though their concatenation is not. -/
def mappedPiece (start stop lo hi dst : Nat) : Option (Nat × Nat) :=
  let s := max start lo
  let t := min stop hi
  if s < t then some (dst + (s - lo), dst + (t - lo)) else none

/-- Split a diagnosis interval at the F2 movement boundaries, map each piece, and enclose all of their images.
    An empty interval maps its point. The candidate's final `.` occupies the question's final `?` position. -/
def mapSpan (c : Candidate) (off : Nat) (span : Nat × Nat) : Nat × Nat :=
  match c.form with
  | .caseThat => (span.1 + off, span.2 + off)
  | .fronted a g =>
    let n := a.utf8ByteSize
    let k := n + 1
    let pieces := ([mappedPiece span.1 span.2 0 g k,
      mappedPiece span.1 span.2 g (g + n) 0,
      mappedPiece span.1 span.2 (g + n) (g + k) n,
      mappedPiece span.1 span.2 (g + k) c.sentence.utf8ByteSize (g + k)] : List (Option (Nat × Nat)))
        |>.filterMap id
    match pieces with
    | [] => let x := mapPoint c off span.1; (x, x)
    | p :: ps => ps.foldl (fun acc v => (min acc.1 v.1, max acc.2 v.2)) p

/-- A lexer rejection's offset, moved from the body onto the question. -/
def shiftReject (k : Nat) : Reject → Reject
  | .badCharacter o => .badCharacter (o + k)
  | .openQuote o => .openQuote (o + k)
  | .badNumeral o => .badNumeral (o + k)
  | .badSpacing o => .badSpacing (o + k)
  | r => r
end VE.Question
```

The response converts both bounds of `mapSpan` to code points of the question, as `english.read` does
(`Run.codepointsBefore`). A diagnosis span must lie inside its candidate sentence. The mapped byte span then has
`start ≤ stop ≤ q.utf8ByteSize`, and every emitted code-point span has `start ≤ stop ≤ q.length`. An interval that
crosses the moved word can cover intervening question text; sorting the old endpoint images would omit diagnosed
bytes. The bounds statements assume capitalization preserves each allowed auxiliary's UTF-8 byte length; both
`["is", "must", "may"]` and speech acts' `["is"]` satisfy that condition.

## 3. The English, one reading each

### 3.1 Questions

A question is read only through `read`, the E2.6 reader, on its candidates; no grammar rule, lexer row, lexicon
entry or identity of E2.6 changes (plan D2). Its one reading is a theorem, not a convention:

- `readQuestion_one` (5.1): when VE reads a question with formula `φ`, every candidate has at most one derivation, the
  asked sentence reads `[(φ, false)]`, every earlier candidate has no reading, and every other candidate reads `φ` or
  has no reading. A candidate that VE refuses (rejected, ill-typed, or marked as a conclusion) has no reading, so it
  neither blocks nor changes the question's reading (R3).
- `question_reading_unique` (5.1): two such readings of one question are the same candidate and formula.
- `asked_reads_back` (5.1): the sentence shown in A0 reads back with exactly `φ`.

| Form | Wording | Its one reading |
|---|---|---|
| F1 | `Is it the case that <sentence without its ".">?` | exactly `<sentence>.`'s reading (`caseThat_reads`) |
| F2 | `Is <rest>?`, `Must <rest>?`, `May <rest>?` | the one meaning of the sentences formed by putting `is`, `must` or `may` back at a gap of `<rest>` |

F2 can read odd English: in G11 the auxiliary moves out of a relative clause (plan 4.9). The A0 line shows the
sentence actually checked, and Q1.3 counts how often this happens.

### 3.2 Rephrasings VE offers

| Case | Offered | Why each reads one way |
|---|---|---|
| two or more meanings | `Is it the case that <the first candidate of that meaning, without its ".">?`, one per meaning, in candidate order | `rephrasings_read`: each reads with its meaning, and no two mean the same |
| no candidate reads, and the body begins with the token `a` or `an` | the question with `every` in that token's place, then with `some`; only those that read, each meaning once | the same theorem; each is checked by `classify` before it is offered |
| one candidate with two derivations | nothing | no Lean renderer exists for the two derivations; E2's text and witnesses are relayed |

### 3.3 The answer's sentences

The frames are plan 4.6's, with draft 2's edits (R8, R9). Each is a sentence VE says, never one an author writes.
Each has one derivation because it begins with a fixed lead that no other registered production begins with and
its slots are closed classes, and each passes W7's all-derivations gate before it is shown, with its rows
registered in Q2.3 (plan 4.6, question 9).

| # | Wording | The one reading |
|---|---|---|
| A0 | `You asked whether <asked sentence without its final ".">.` | VE read the question as this sentence, and the answer below is about this sentence. |
| A1 | `Yes.` | In every situation the document allows (under the named readings), the asked sentence is true. |
| A2 | `No. The document rules this out.` | In every situation the document allows, the asked sentence is false. |
| A3 | `The text does not settle this.` | There is a situation the document allows in which the answer depends on points the text leaves unsaid. |
| A4 | `Not necessarily.` | There is a situation the document allows in which the asked sentence is false. Nothing more is claimed. |
| A5 | `VE could not decide this.` | No verdict. The next sentence gives the reason. |
| C1 | `Sentence <n> says: "<bytes>"` | Sentence n is one of the premises the answer uses, and these are its exact words. |
| C2 | `Sentences <citation> say when <generic clause>.` | Together these sentences are the rules that decide the act, and the answer uses them. |
| C3 | `VE also used what the document's word list declares.` | A declaration of the document's vocabulary is used. |
| C4 | `VE also used its rule that whatever must be done may be done: <pair sentence>` | The pair premise, or `Fill_T` at a gap, is used. |
| S1 | `Here is a situation the document allows where it fails: <situation>[, reading <readings>].` | A checked countermodel, under the named choice. |
| S2 | `Here is a situation where the answer depends on what the text leaves unsaid: <situation>[, reading <readings>].` then one `The text does not say whether <clause>.` per point where the two fillings differ | A checked split: one base, and the gap points that differ. |
| S3 | `Here the text does not say whether <clause>; this situation answers 'no'.` | The filled-gap sentence after S1, one per gap the failure depends on. |
| R1 | `If sentence <n> means "<reading>"[ (VE has not checked this wording)][ and sentence <m> means "<reading>"], <lead phrase>.` | The lead holds under every compatible choice that reads the named sentences this way (`group_claim`). The parenthesis follows every reading whose wording Lean did not read back. |
| R2 | `Every way of reading the document gives this answer.` | Every compatible choice has the same lead (and the same cited sentences, for yes and no). |
| U1 | `VE did not use <k> sentences of this document that it could not read formally: <citation>.` | Those units have no formal content; the answer is about the other sentences only. Shown once per answer, after all its blocks, for every kind of lead (D14). |
| X1 | `The document's rules or defaults conflict in this situation, so VE cannot answer: <situation>.` | A checked conflict witness under this choice, including a conflict caused by defaults without two rules. |
| X2 | `VE could not check that the rules never contradict each other.` | The conflict row is unknown. |
| X3 | `The sentences of this document cannot all be true together, so VE does not answer questions about it.` | A certificate of ⊥ under this choice. |
| X4 | `VE found neither a proof nor a situation where it fails, within its limits.` | No row result. |
| X5 | `There are more than 64 ways to read this document's open sentences. VE did not check them all.` | The enumeration budget. |
| X6 | `VE found a proof but could not check that the document's sentences can all be true together, so it does not answer.` | A checked certificate for the asked sentence or its negation, and no checked premise model. |

The lead phrases inside R1 are `yes`, `no: the document rules this out`, `the text does not settle this`, `not
necessarily` and `VE could not decide this`.

**Never shown:** a unit, set or candidate id, or `reading <i>`; an `unsaid__` or `ve__` name, or a generated
predicate; "No." in front of a countermodel; A1 or A2 without a premise model; R2 when any choice is unchecked; a
situation that names fewer open sets than its model's choice; an unchecked wording without its parenthesis; an
ordinal in place of a wording.

## 4. Diagnostics, in order

### 4.1 Q1 (`english.question`)

The rows are in `classify`'s order (2.4); the first that applies decides. Codes new to VE are rows of Lean's code
table in `VE.Question.Run`; the others are E2's, with E2's class. A span is in code points of the question.

| # | When | Status | Code; class | Text | Span; advice |
|---|---|---|---|---|---|
| 1 | the vocabulary is refused (`grammarFault E O L = some g`) | `invalidGrammar` | `InvalidGrammar`; `CheckerUnavailable` | E2's `invalidGrammarText "english.question"`: `The vocabulary selection was not accepted (invalidGrammar <fault>[: <code> <kind> <name>]). No text was read.` | — |
| 2 | no final `?`, or a second `?` | `notQuestion` | `NotOneQuestion`; `SyntaxError` | `Write one question that ends with a question mark.` | the question |
| 3 | the first word is a wh-word (`Who`, `What`, `Which`, `Whom`, `Whose`, `Where`, `When`, `Why`, `How`) | `none` | `QuestionForm`; `SyntaxError` | `VE answers yes-or-no questions. It does not answer who, what or which questions yet.` | the question |
| 3 | any other first word | `none` | `QuestionForm`; `SyntaxError` | `VE answers questions that begin with "Is", "Must" or "May", or with "Is it the case that" followed by a sentence.` The quoted words are `auxs`, capitalised. | the question |
| 4 | more than 4,096 bytes | `budget` | `QuestionTooLong`; `ResourceLimit` | `The question is longer than VE reads. Ask a shorter question.` | the question |
| 5 | `body ++ "."` does not lex, at a space before the `?` | `rejected` | `BadSpacing`; `SyntaxError` | `The spacing at position <p> is not allowed: write no space before the question mark.` | the `?` |
| 5 | `body ++ "."` does not lex, any other rejection `r` | `rejected` | `r`'s code and class | E2's `rejectText 0 r`, its offset moved onto the question, and `Sentence 1 ` written `The question ` | E2's `lexicalSpan`, moved |
| 6 | the body lexes as more than one sentence | `notQuestion` | `NotOneQuestion`; `SyntaxError` | as row 2 | the question |
| 7 | more than 300 tokens in the body, or more than 64 candidates | `budget` | `QuestionTooLong`; `ResourceLimit` | as row 4 | the question |
| 8 | a candidate does not lex as one sentence | `notQuestion` | `NotOneQuestion`; `SyntaxError` | as row 2 | the question |
| 9 | a candidate reaches the work budget | `budget` | `Budget`; `ResourceLimit` | `VE stopped reading this question at its work limit.` | the question |
| 10 | a candidate has two derivations | `many` | `Ambiguous`; `AmbiguousDerivation` | `The sentence "<candidate>" can be read in more than one way. Two of the ways are shown.`, with E2's two witness trees | the question |
| 11 | one meaning | `one` | — | — (the answer begins with A0) | — |
| 12 | two or more meanings | `many` | `AmbiguousQuestion`; `AmbiguousDerivation` | `This question can be read in more than one way. Ask one of these instead:`, then the rephrasings | the question |
| 13 | a refusal: a conclusion mark (`read` gives `.ok [(φ, true)]`) | `rejected` | `QuestionWithMarker`; `SyntaxError` | `A question cannot contain "therefore", "so", "hence" or "it follows that".` | the question |
| 13 | a refusal: ill-typed | `rejected` | `IllTyped`; `TypeMismatch` | `The question was read, and its formula does not pass the type check.` | the question |
| 13 | a refusal: a rejected derivation `r` | `rejected` | `r`'s code and class | E2's `rejectionText` for sentence 0, with `Sentence 1 ` written `The question ` | the question |
| 14 | no candidate reads, the body begins with `a` or `an`, and a rephrasing reads | `indefinite` | `IndefiniteQuestion`; `SyntaxError` | `VE cannot tell whether "<a or an>" here means every or some. Ask one of these instead:`, then the rephrasings | the question |
| 15 | no candidate has a derivation | `none` | `NoDerivation`; `SyntaxError` | `The question has no reading with the current vocabulary.` When the closest candidate's diagnosis is found: ` Closest sentence tried: "<candidate>". <E2.6's diagnosis text>` | the diagnosis span, mapped (2.5); advice `Write "every" or "some" in place of "<a or an>".` when the body begins with `a` or `an`, else E2's advice row for the candidate's tokens, if any |

The refusal of row 13 is the first refused candidate's. Row 13 applies only when no candidate has a meaning: a
refused candidate beside a candidate that reads does not refuse the question (R3).

### 4.2 Q2 (`ask`)

In order: (1) the question is read by `readQuestion`; any outcome but `one` is the response, with row 1 to 15's
fields. (2) The binding (5.2, `CaseBinding`); on failure, `CheckerUnavailable: the case is not this document's`. (3)
The case's conclusion must be the question's formula and `assumed` empty; otherwise `InvalidInput: the case does
not ask this question`. (4) RD-3's replay; more than 64 compatible choices gives lead *unknown* with X5, and RD-3's
own refusals are relayed. (5) Every reading name of an asserted candidate is read back; a failure gives
`CheckerUnavailable: VE could not check the wording of a reading of sentence <n>` (R8). (6) The rows give the
leads; an *unknown* lead gives its reason by `Row.reason` (X1 to X4, X6). Routes outside plan D18 give *unknown*
with the route's own abstention text relayed.

## 5. The Lean statements

### 5.1 Q1 (`VE.Question`)

The original reading statements are the stub's `def … : Prop`, written as theorems, and elaborate against
`c85797de`. The two span bounds statements were added after Q0 review and await the targeted check.

```lean
namespace VE.Question
open VE.EnglishGrammar
open VE.Grammar (Derives)

/-- A candidate sentence lexes as one sentence and has no derivation. -/
def NoDerivation (E : Env) (L : Lexicon) (s : String) : Prop :=
  ∃ w, lex s = .ok #[w] ∧ ∀ t, ¬ Derives (grammar E L) (.n (grammar E L).start) w.toList t

/-- A candidate sentence lexes as one sentence and has at most one derivation. -/
def AtMostOneDerivation (E : Env) (L : Lexicon) (s : String) : Prop :=
  ∃ w, lex s = .ok #[w] ∧ ∀ t u, Derives (grammar E L) (.n (grammar E L).start) w.toList t →
    Derives (grammar E L) (.n (grammar E L).start) w.toList u → t = u

/-- An accepted one-sentence unmarked reading. -/
def HasReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) : Prop :=
  ∃ φ, EnglishOneReading E O L s [(φ, false)]

/-- R3: (a) every candidate lexes as one sentence with at most one derivation; (b) `c` is the first candidate that
    reads `[(φ, false)]`; (c) every other candidate reads `[(φ, false)]` or has no accepted one-sentence unmarked
    reading. -/
def QuestionOneReading (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (q : String) (c : Candidate)
    (φ : EFormula) : Prop :=
  c ∈ candidates auxs q ∧
  (∀ d ∈ candidates auxs q, AtMostOneDerivation E L d.sentence) ∧
  EnglishOneReading E O L c.sentence [(φ, false)] ∧
  (∀ d ∈ (candidates auxs q).takeWhile (fun d => d != c), ¬ HasReading E O L d.sentence) ∧
  (∀ d ∈ candidates auxs q, EnglishOneReading E O L d.sentence [(φ, false)] ∨ ¬ HasReading E O L d.sentence)

/-- `read_complete_english`'s hypotheses on the grammar. -/
def GrammarChecks (E : Env) (L : Lexicon) : Prop :=
  (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
    (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence

theorem readQuestion_one :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate) (φ : EFormula),
    readQuestion auxs E O L b q = .one c φ → L.policyOk E O = true ∧ QuestionOneReading auxs E O L q c φ

/-- Completeness (R4): under the reader's hypotheses, the limits, and no candidate at its budget. -/
theorem readQuestion_complete :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate) (φ : EFormula),
    L.policyOk E O = true → GrammarChecks E L → withinLimits auxs q = true →
    (∀ d ∈ candidates auxs q, ∀ i, read E O L b d.sentence ≠ .stopped i .budget) →
    QuestionOneReading auxs E O L q c φ → readQuestion auxs E O L b q = .one c φ

theorem question_reading_unique :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (q : String) (c c' : Candidate) (φ φ' : EFormula),
    QuestionOneReading auxs E O L q c φ → QuestionOneReading auxs E O L q c' φ' → c = c' ∧ φ = φ'

/-- The step from `.stopped _ .noDerivation` to `NoDerivation` (R2: the candidate is one sentence). -/
theorem got_none :
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (c : Candidate), got E O L b c = .none → NoDerivation E L c.sentence

/-- What "no reading" claims: no candidate has a derivation, and the closest one is a candidate. -/
theorem readQuestion_none :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (cl : Option Candidate),
    readQuestion auxs E O L b q = .none cl →
    (∀ d ∈ candidates auxs q, NoDerivation E L d.sentence) ∧ ∀ d, cl = some d → d ∈ candidates auxs q

theorem readQuestion_indefinite :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q art : String) (rs : List String),
    readQuestion auxs E O L b q = .indefinite art rs → ∀ d ∈ candidates auxs q, NoDerivation E L d.sentence

/-- What "more than one way" claims: at least two different meanings, each a candidate's whole reading. -/
theorem readQuestion_meanings :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String)
    (fs : List (Candidate × EFormula)) (rs : List String),
    readQuestion auxs E O L b q = .meanings fs rs →
    2 ≤ fs.length ∧ (fs.map (·.2)).Nodup ∧
    (∀ x ∈ fs, x.1 ∈ candidates auxs q ∧ read E O L b x.1.sentence = .ok [(x.2, false)]) ∧
    rs = fs.map (fun x => caseThatQuestion x.1)

theorem readQuestion_ambiguous :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate),
    readQuestion auxs E O L b q = .ambiguous c → c ∈ candidates auxs q ∧
    ∃ w t u, lex c.sentence = .ok #[w] ∧ t ≠ u ∧ Derives (grammar E L) (.n (grammar E L).start) w.toList t ∧
      Derives (grammar E L) (.n (grammar E L).start) w.toList u

theorem asked_reads_back :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (c : Candidate) (φ : EFormula),
    readQuestion auxs E O L b q = .one c φ → checkRendering E O L b [(φ, false)] c.sentence = true

/-- F1 reads exactly as its sentence (R4: within the limits). -/
theorem caseThat_reads :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (t : String) (φ : EFormula),
    L.policyOk E O = true → '?' ∉ t.toList → withinLimits auxs (caseFrame ++ t ++ "?") = true →
    (readQuestion auxs E O L b (caseFrame ++ t ++ "?") = .one ⟨.caseThat, t ++ "."⟩ φ ↔
      read E O L b (t ++ ".") = .ok [(φ, false)])

/-- F1 precedence: an F1 question has no other candidate. -/
theorem caseThat_candidates :
  ∀ (auxs : List String) (t : String), '?' ∉ t.toList →
    ∀ c ∈ candidates auxs (caseFrame ++ t ++ "?"), c = ⟨.caseThat, t ++ "."⟩

/-- F2: a candidate is its question with the fronted word put back in the rest, bytes included. -/
theorem fronted_text :
  ∀ (auxs : List String) (q a : String) (g : Nat) (s : String),
    (⟨.fronted a g, s⟩ : Candidate) ∈ candidates auxs q →
    a ∈ auxs ∧ caseFrame.isPrefixOf q = false ∧ ∃ rest, q = capitalise a ++ " " ++ rest ++ "?" ∧ g ∈ gaps rest ∧
      s = rest.extract ⟨0⟩ ⟨g⟩ ++ a ++ " " ++ rest.extract ⟨g⟩ rest.endPos ++ "."

/-- Every candidate diagnosis interval maps to an ordered byte interval inside the question. The response then
    converts both endpoints with `Run.codepointsBefore`; its emitted span must satisfy
    `start ≤ stop ≤ q.length` in code points. -/
theorem mapSpan_valid :
  ∀ (auxs : List String) (q : String) (c : Candidate) (start stop : Nat),
    (∀ a ∈ auxs, (capitalise a).utf8ByteSize = a.utf8ByteSize) →
    c ∈ candidates auxs q → start ≤ stop → stop ≤ c.sentence.utf8ByteSize →
    let span := mapSpan c caseFrame.utf8ByteSize (start, stop)
    span.1 ≤ span.2 ∧ span.2 ≤ q.utf8ByteSize

theorem mapSpan_codepoints_valid :
  ∀ (auxs : List String) (q : String) (c : Candidate) (start stop : Nat),
    (∀ a ∈ auxs, (capitalise a).utf8ByteSize = a.utf8ByteSize) →
    c ∈ candidates auxs q → start ≤ stop → stop ≤ c.sentence.utf8ByteSize →
    let span := mapSpan c caseFrame.utf8ByteSize (start, stop)
    VE.EnglishGrammar.Run.codepointsBefore q span.1 ≤
      VE.EnglishGrammar.Run.codepointsBefore q span.2 ∧
    VE.EnglishGrammar.Run.codepointsBefore q span.2 ≤ q.length

/-- Every rephrasing reads with one meaning, and no two mean the same (R4: each within the limits). -/
theorem rephrasings_read :
  ∀ (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) (rs : List String),
    ((∃ fs, readQuestion auxs E O L b q = .meanings fs rs) ∨ (∃ art, readQuestion auxs E O L b q = .indefinite art rs)) →
    (∀ r ∈ rs, withinLimits auxs r = true) →
    (∀ r ∈ rs, ∃ c φ, readQuestion auxs E O L b r = .one c φ) ∧
    rs.Pairwise (fun r r' => ∀ c₁ φ₁ c₂ φ₂, readQuestion auxs E O L b r = .one c₁ φ₁ →
      readQuestion auxs E O L b r' = .one c₂ φ₂ → φ₁ ≠ φ₂)
end VE.Question
```

**Proof notes for Q1.1** (obligations, not proofs).
- `readQuestion_one`: `.one` is reached only after `grammarFault = none` (so `policyOk`), no `notOne`, no budget
  and no `many`. For (a): `got` is `one`, `none` or `refused`, and each fixes the derivations of the one sentence:
  `read_ok`, then `doc_sound`, gives a unique tree; `.stopped 0 .noDerivation` gives none (`read_stopped`, then
  `read_none`); a refusal is `.ok` with a mark, `.illTyped` (the document read), or `.stopped 0 (.rejected r)`
  (`read_rejected`); `.lexical` and `.invalidGrammar` cannot occur after `got`'s and `classify`'s checks. (b) and
  (c): a candidate with `HasReading` that is not `one` would contradict `read_complete_english`, since no budget
  occurred.
- `readQuestion_complete`: `policyOk`, `GrammarChecks` and `L.valid` (from `EnglishOneReading`) give
  `grammarFault = none`; `c ∈ candidates` gives the shape and one body sentence; `withinLimits` passes the three
  size checks; (a) excludes `notOne` and, with `read_ambiguous`, `many`; `hb` excludes `budget`; (b) and (c) make
  `firstMeanings = [(c, φ)]`.
- `question_reading_unique`: two first-reading candidates of one list are equal (each is outside the other's
  `takeWhile`), then `english_reading_unique`.
- `caseThat_reads`: F1 has one candidate (`caseThat_candidates`), and `read … = .ok [(φ, false)]` implies one lexed
  sentence (`readDocument` returns one result per sentence).
- `rephrasings_read`: an offered F1 rephrasing's only candidate is the candidate it came from, whose `read` is
  already `.ok [(φ, false)]`; `withinLimits` passes its size checks. An indefinite rephrasing is offered only after
  `classify` gave `one`.

### 5.2 Q2 (`VE.Ask`)

The original Q2 definitions elaborated against RD-3's unmerged branch (11.2). The corrected definitions and
statement types below also elaborate in a temporary stub against that branch, but await statement review against
merged RD-3 before Q2.1. The text functions (`render`,
`renderGroup`, `askedLine`, `leadOfLine`, `contextOf`, `checkedCites`, `checkedWitness`, `lineText`) and the replay
functions are Q2.3's and Q2.2's; they require bodies before their claims have force.

```lean
namespace VE.Ask
open Lean VE.Readings VE.NormDefaults
open VE.Norms (Sat restrictAll DocumentExpansion)
universe u

inductive Lead | yes | no | notSettled | notNecessarily | unknown
  deriving DecidableEq, Repr

structure Row where
  choice   : Choice
  conflict : ChoiceResult   -- RD-3's conflict row: `.free`, `.conflict` or `.unknown`
  premise  : ChoiceResult   -- RD-3's premise row: `.model`, `.inconsistent` or `.unknown`
  query    : ChoiceResult   -- RD-3's query row for ψ: `.proved`, `.refuted` or `.unknown`
  negation : ChoiceResult   -- `.proved` (a certificate for ¬ψ, `ndCertOk`) or `.unknown`
  split    : Bool           -- one base model, two fillings, both `ndModelOk`, ψ true and false
  deriving DecidableEq, Repr

def Row.lead (r : Row) : Lead :=
  if r.conflict != .free then .unknown
  else if r.query == .proved then (if r.premise == .model then .yes else .unknown)
  else if r.negation == .proved then (if r.premise == .model then .no else .unknown)
  else if r.split then .notSettled
  else if r.query == .refuted then .notNecessarily
  else .unknown

/-- The reason sentence after A5: X1 `conflict`, X2 `conflictUnchecked`, X3 `inconsistent`, X4 `noResult`,
    X5 `tooMany` (no rows), X6 `unchecked` (R9). -/
inductive Reason | conflict | conflictUnchecked | inconsistent | noResult | tooMany | unchecked
  deriving DecidableEq, Repr

def Row.reason (r : Row) : Option Reason :=
  if r.lead != .unknown then none
  else if r.conflict == .conflict then some .conflict
  else if r.conflict != .free then some .conflictUnchecked
  else if r.premise == .inconsistent then some .inconsistent
  else if r.query == .proved || r.negation == .proved then some .unchecked
  else some .noResult

/-- One base situation, two admissible fillings of its gaps, the premises true in both expansions, ψ true in the
    first and false in the second. -/
def SplitU (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) : Prop :=
  ∃ (B : VE.Structure.{0}) (F₁ F₂ : FillTables U B) (S₁ S₂ : VE.Structure.{0}),
    restrictAll (fill U).T S₁ = withFill U B F₁ ∧ restrictAll (fill U).T S₂ = withFill U B F₂ ∧
    BaseAdmissibleU U (withFill U B F₁) ∧ BaseAdmissibleU U (withFill U B F₂) ∧
    DocumentExpansion (fill U) (withFill U B F₁) S₁ ∧ DocumentExpansion (fill U) (withFill U B F₂) S₂ ∧
    Sat S₁ Γ ∧ Sat S₂ Γ ∧ ψ.denote S₁ [] ∧ ¬ ψ.denote S₂ []

def LeadHolds (N : NDoc) (ψ : VE.Formula) (r : Row) : Prop :=
  let U := choiceU N r.choice
  let Γ := (choiceDoc N.D r.choice).2
  match r.lead with
  | .yes => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ ψ
  | .no => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ (.not ψ)
  | .notSettled => ConflictFreeU.{u} U ∧ SplitU U Γ ψ
  | .notNecessarily => ConflictFreeU.{u} U ∧ CounterU U Γ ψ
  | .unknown => True

def ReasonHolds (N : NDoc) (ψ : VE.Formula) (r : Row) : Reason → Prop
  | .conflict => ¬ ConflictFreeU.{0} (choiceU N r.choice)
  | .inconsistent => ConflictFreeU.{u} (choiceU N r.choice) ∧
      EntailsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 .bottom
  | .unchecked => ConflictFreeU.{u} (choiceU N r.choice) ∧
      (EntailsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 ψ ∨
        EntailsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 (.not ψ))
  | _ => True

/-- The row's hypotheses: each component holds of its choice, as RD-3's rows do (`nd*Row_holds`). -/
def RowOk (N : NDoc) (ψ : VE.Formula) (r : Row) : Prop :=
  Holds.{u} N [] .bottom r.choice r.conflict ∧ Holds.{u} N [] .bottom r.choice r.premise ∧
  Holds.{u} N [] ψ r.choice r.query ∧ Holds.{u} N [] (.not ψ) r.choice r.negation ∧
  (r.split = true → SplitU (choiceU N r.choice) (choiceDoc N.D r.choice).2 ψ)

theorem lead_sound : ∀ (N : NDoc) (ψ : VE.Formula) (r : Row), RowOk.{u} N ψ r → LeadHolds.{u} N ψ r
theorem reason_sound : ∀ (N : NDoc) (ψ : VE.Formula) (r : Row) (x : Reason),
  RowOk.{u} N ψ r → r.reason = some x → ReasonHolds.{u} N ψ r x
theorem reason_exact : ∀ r : Row, r.lead = .unknown ↔ r.reason.isSome
theorem split_counter : ∀ (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula), SplitU U Γ ψ → CounterU U Γ ψ
/-- Needs a variant of RD-3's `expansion_of_modelCheck` that exposes the base equation (plan Q2.1); `e` supplies
    `WellFormedU`. -/
theorem splitOk_sound : ∀ (N : NDoc) (c : Choice) (e : VE.Readings.Wire.NDEvidence N c) (ψ : VE.Formula)
    (m₁ m₂ : VE.Readings.Wire.FilledModel (choiceU N c)), m₁.M = m₂.M →
    VE.Readings.Wire.ndModelOk N c [] ψ m₁ true = true → VE.Readings.Wire.ndModelOk N c [] ψ m₂ false = true →
    SplitU (choiceU N c) (choiceDoc N.D c).2 ψ

/-! ## Agreement with RD-3's fold (plan 4.2) -/

def conflictRows (rs : List Row) : List (Choice × ChoiceResult) := rs.map fun r => (r.choice, r.conflict)
def queryRows (rs : List Row) : List (Choice × ChoiceResult) := rs.map fun r => (r.choice, r.query)

theorem lead_agrees : ∀ r : Row,
  (r.lead = .yes → r.query = .proved) ∧
  (r.lead = .no ∨ r.lead = .notSettled ∨ r.lead = .notNecessarily → r.query ≠ .proved)
theorem all_yes_iff_fold : ∀ rs : List Row, rs ≠ [] → (∀ r ∈ rs, r.premise = .model) →
  ((∀ r ∈ rs, r.lead = .yes) ↔ foldEntailment (conflictRows rs) (queryRows rs) = .all)

/-! ## Reasons (plan 4.3) -/

inductive Source
  | unit (id : String)
  | rules (pred : String)          -- the layer premise of one regulated predicate; its units are named at render
  | definition (name : String)
  | background
  | pair (req perm : String)
  | fill (req perm : String)
  deriving DecidableEq, Repr

/-- Where each premise of `premisesU U Γ` comes from, in its order: `background (fill U)` (definitions, then
    `Background_base`, then the pair premises), then `fillPremises U`, then `elaborate (fill U).T`, then the
    assertions, whose sources are given. -/
def sourcesU (U : UDoc) (assertions : List Source) : List Source :=
  let T := (fill U).T
  (VE.Norms.syms T).filterMap (fun | .defn d => some (Source.definition d.name) | .reg _ => none) ++
  (VE.Norms.backgroundBase (fill U)).map (fun _ => Source.background) ++
  (VE.Norms.pairs T).map (fun pr => Source.pair pr.req pr.perm) ++
  ((VE.Norms.pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)).map
    (fun pr => Source.fill pr.req pr.perm) ++
  (VE.Norms.syms T).filterMap (fun | .reg r => some (Source.rules r.name) | .defn _ => none) ++
  assertions

theorem sourcesU_length : ∀ (U : UDoc) (as : List Source) (Γ : List VE.Formula), as.length = Γ.length →
  (sourcesU U as).length = (VE.NormDefaults.Wire.premisesU U Γ).length

def positions (P : List VE.Formula) : VE.Compose.Labelled :=
  ((List.range P.length).zip P).map fun (i, f) => (toString i, f)

/-- R10: the replay without the meaning-id binding, which `ndBoundCert` checks once when the certificate is decoded. -/
def replayOk (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate E P ψ k

def usedPositions (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate) :
    List Nat :=
  (usedLabels (fun Q => replayOk E Q ψ k) [] (positions P) []).filterMap String.toNat?

theorem usedPositions_sufficient : ∀ (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula)
  (k : VE.Tableau.Certificate), replayOk E P ψ k = true →
    VE.Entails.{u} E ((usedPositions E P ψ k).filterMap (P[·]?)) ψ

def cited (srcs : List Source) (used : List Nat) : List Source := (used.filterMap (srcs[·]?)).eraseDups

/-! ## Readings: relevant sets and groups (plan 4.4, R7) -/

def assignment (sets : List String) (r : Row) : List (String × Option Nat) := sets.map fun s => (s, r.choice.index s)

def separates (rows : List Row) (key : Row → Lead × List Source) (sets : List String) : Bool :=
  rows.all fun r => rows.all fun r' => assignment sets r != assignment sets r' || key r == key r'

/-- Greedy, in set order: a set is dropped while the rest still separates; checked, else every set. -/
def relevantSets (ids : List String) (rows : List Row) (key : Row → Lead × List Source) : List String :=
  let greedy := ids.foldl (fun S s => if separates rows key (S.erase s) then S.erase s else S) ids
  if separates rows key greedy then greedy else ids

theorem relevantSets_sound : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
  ids.Nodup → (∀ r ∈ rows, r.choice.map (·.1) = ids) →
  (∀ r ∈ rows, ∀ r' ∈ rows, r.choice = r'.choice → key r = key r') →
  ∀ r ∈ rows, ∀ r' ∈ rows, (∀ s ∈ relevantSets ids rows key, r.choice.index s = r'.choice.index s) → key r = key r'

structure Group where
  lead : Lead
  cited : List Source
  on : List (String × Option Nat)
  rows : List Row

/-- One group per distinct key and assignment on the relevant sets, in order of first row. -/
def groups (ids : List String) (rows : List Row) (key : Row → Lead × List Source) : List Group :=
  let sets := relevantSets ids rows key
  rows.foldl (fun gs r =>
    let k := key r
    let a := assignment sets r
    if gs.any (fun g => (g.lead, g.cited) == k && g.on == a) then
      gs.map (fun g => if (g.lead, g.cited) == k && g.on == a then { g with rows := g.rows ++ [r] } else g)
    else gs ++ [⟨k.1, k.2, a, [r]⟩]) []

theorem groups_cover : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
  ∀ r ∈ rows, ∃ g ∈ groups ids rows key, r ∈ g.rows ∧ ∀ g' ∈ groups ids rows key, r ∈ g'.rows → g' = g
theorem group_rows : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
  ∀ g ∈ groups ids rows key, ∀ r ∈ g.rows,
    r ∈ rows ∧ key r = (g.lead, g.cited) ∧ g.on = assignment (relevantSets ids rows key) r
/-- What an R1 block claims: every row that reads the named sets as the block names them has its lead and
    citations. -/
theorem group_claim : ∀ (ids : List String) (rows : List Row) (key : Row → Lead × List Source),
  ids.Nodup → (∀ r ∈ rows, r.choice.map (·.1) = ids) →
  (∀ r ∈ rows, ∀ r' ∈ rows, r.choice = r'.choice → key r = key r') →
  ∀ g ∈ groups ids rows key, ∀ r ∈ rows, assignment (relevantSets ids rows key) r = g.on → key r = (g.lead, g.cited)

/-! ## The text (plan 4.6; Q2.3 writes the bodies) -/

structure Line where
  frame : String
  text : String
  source : Option Source := none
  quote : Option (String × String) := none
  readings : List (String × Nat) := []
  witness : Option Choice := none   -- S1, S2 and X1: the checked row choice, not printed as an id
  unchecked : Bool := false       -- the line carries "(VE has not checked this wording)"
  deriving Repr, Inhabited

/-- A reading's own sentence, as the request names it, and whether Lean read it back (D11). -/
structure Name where
  set : String
  index : Nat
  text : String
  checked : Bool

structure Answer where
  request : Json
  text : String
  case : Json
  x : VE.Readings.Wire.NDVerdicts
  asked : VE.Question.Candidate
  ids : List String
  rows : List Row
  cites : Row → List Source
  names : List Name
  unused : List String

def Answer.key (a : Answer) (r : Row) : Lead × List Source :=
  (r.lead, if r.lead == .yes || r.lead == .no then a.cites r else [])
def Answer.groups (a : Answer) : List Group := VE.Ask.groups a.ids a.rows a.key

structure Context where
  text : String
  units : List (String × Nat × Nat)
  textOf : String → Option String
  displayOf : String → Option Nat

def contextOf : String → Except String Context             -- Q2.3: `Document.split`, unit spans and display numbers
def checkedCites : Json → VE.Readings.Wire.NDVerdicts → Row → List Source
  -- Q2.3: the accepted ψ or ¬ψ certificate from this request's evidence, then
  -- `cited (sourcesU …) (usedPositions …)`; the ¬ψ certificate is outside RD-3's `x.evs`
def documentUnused : String → List String                  -- Q2.3: unit ids lacking formal content, in document order
def checkedWitness : Json → VE.Readings.Wire.NDVerdicts → Row → String → Prop
  -- Q2.2: the row's accepted model, split or conflict witness in this request supplies S1, S2 or X1
def lineText : Context → Answer → Line → String             -- Q2.3: exact frame and slot rendering from metadata
def citationText : List Nat → String                        -- Q2.3: document display numbers in citation style

/-- Only replayed evidence and the document's own split may supply render inputs. `contextOf` extracts each
    `textOf` value from `split.source` at the front-matter unit span (or from its named fence), trimmed as the
    document loader trims it; `displayOf` is that unit's display position. -/
def RenderInputBound (ctx : Context) (a : Answer) : Prop :=
  contextOf a.text = .ok ctx ∧
  a.request.getObjValD "case" = a.case ∧
  VE.Readings.Run.replayVerdictsND a.case = .ok a.x ∧
  a.rows.map (·.choice) = a.x.evs.map (·.1) ∧
  (∀ r ∈ a.rows, a.cites r = checkedCites a.request a.x r) ∧
  a.unused = documentUnused a.text

def render : Context → Answer → List Line                 -- Q2.3
def renderGroup : Context → Answer → Group → List Line    -- Q2.3
def askedLine : String → Line                             -- A0
def leadOfLine : Option Line → Option Lead

def named (on : List (String × Option Nat)) : List (String × Nat) := on.filterMap fun (s, i) => i.map (s, ·)

theorem render_quotes_bytes : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
  ∀ l ∈ render ctx a, ∀ u t, l.quote = some (u, t) → ctx.textOf u = some t
theorem render_text_matches_metadata : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
  ∀ l ∈ render ctx a, l.text = lineText ctx a l
theorem render_asked : ∀ (ctx : Context) (a : Answer), (render ctx a).head? = some (askedLine a.asked.sentence)
theorem render_cites_exact : ∀ (ctx : Context) (a : Answer) (g : Group), RenderInputBound ctx a → g ∈ a.groups →
  (g.lead = .yes ∨ g.lead = .no) → (renderGroup ctx a g).filterMap (·.source) = g.cited
theorem render_lead : ∀ (ctx : Context) (a : Answer) (g : Group), g ∈ a.groups →
  leadOfLine (renderGroup ctx a g).head? = some g.lead
/-- R7, with `groups_cover`: each row's one block names exactly its readings of the relevant sets. -/
theorem render_covers_rows : ∀ (ctx : Context) (a : Answer) (g : Group), g ∈ a.groups → 2 ≤ a.groups.length →
  ((renderGroup ctx a g).head?.map (·.readings)) = some (named g.on)
/-- R8: an unchecked wording is marked in the line that shows it. -/
theorem render_marks_unchecked : ∀ (ctx : Context) (a : Answer), ∀ l ∈ render ctx a,
  (∃ n ∈ a.names, n.checked = false ∧ (n.set, n.index) ∈ l.readings) → l.unchecked = true
theorem render_model_names_choice : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
  ∀ l ∈ render ctx a, l.frame ∈ ["S1", "S2", "X1"] →
    ∃ r ∈ a.rows, l.witness = some r.choice ∧ checkedWitness a.request a.x r l.frame ∧
      l.readings = named (assignment a.ids r)
/-- D14, R8: one U1 after all answer blocks, with the document-derived count and citation; none for an empty list. -/
theorem render_unused_once : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
  (a.unused = [] → ∀ l ∈ render ctx a, l.frame ≠ "U1") ∧
  (a.unused ≠ [] → ∃ pre u, render ctx a = pre ++ [u] ∧
    (∀ l ∈ pre, l.frame ≠ "U1") ∧ u.frame = "U1" ∧
    u.text = lineText ctx a u ∧ u.quote = none ∧ u.source = none ∧
    u.readings = [] ∧ u.witness = none ∧
    u.text = s!"VE did not use {a.unused.length} sentences of this document that it could not read formally: " ++
      citationText (a.unused.filterMap ctx.displayOf) ++ ".")

/-! ## The binding and the wire (plan 4.3, 4.8; R5) -/

/-- Canonical JSON: `compress` writes an object's keys in sorted order. -/
def Same (a b : Json) : Prop := a.compress = b.compress

/-- The document-level front-matter inputs the readings case carries besides its environment and units. -/
def boundKeys : List String := ["reading_sets", "couplings", "narrowings", "completions"]

/-- Unit `i` of the case is the compiled form of front-matter unit `i`. `{"ast": φ}` compiles to bare `φ`;
    `{"norm": …}` keeps its norm object. A fence compiles to one bare formula, read through its declared surface.
    `V` is the replayed document's formula environment. -/
def UnitBound (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment)
    (fences : List (String × String))
    (cu fu : Json) : Prop :=
  Same (cu.getObjValD "id") (fu.getObjValD "id") ∧ Same (cu.getObjValD "kind") (fu.getObjValD "kind") ∧
  let authored := fu.getObjValD "content"
  let compiled := cu.getObjValD "content"
  if authored.getObjValD "fence" != .null then
    ∃ f, authored.getObjValD "fence" = fu.getObjValD "id" ∧
      fences.lookup ((fu.getObjValD "id").getStr?.toOption.getD "") = some f ∧
      ((fu.getObjValD "surface" = .str "english" ∧
        ∃ φ, VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget f = .ok [(φ, false)] ∧
          Same compiled φ.encode) ∨
       (fu.getObjValD "surface" = .str "strict" ∧
        ∃ ψ, VE.Surface.parse V f = some [ψ] ∧ Same compiled (VE.Route.Wire.encodeFormula ψ)))
  else if authored.getObjValD "ast" != .null then Same compiled (authored.getObjValD "ast")
  else Same compiled authored

/-- The case is this document's: its environment and every listed input equal the front matter's, its units are the
    front matter's in order, `E` is the environment Lean decodes from the front matter, and `L` passes the vocabulary
    policy for it (so it is the policy's selection, `policy_selection`). -/
def CaseBinding (text : String) (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) : Prop :=
  ∃ (sp : VE.Discourse.Loader.Split) (re : VE.Readings.Wire.ReadingsEnvironment),
    VE.Service.Document.split text = .ok sp ∧
    Same (case.getObjValD "environment") (sp.front.getObjValD "environment") ∧
    VE.Readings.Wire.decodeEnvironment (case.getObjValD "environment") = .ok re ∧
    (∀ k ∈ boundKeys, Same ((case.getObjValD "document").getObjValD k) (sp.front.getObjValD k)) ∧
    VE.EnglishGrammar.Env.decode (sp.front.getObjValD "environment") (Json.mkObj []) = .ok E ∧
    L.policyOk E {} = true ∧
    ∃ cus fus : Array Json, (case.getObjValD "document").getObjValD "units" = .arr cus ∧
      sp.front.getObjValD "units" = .arr fus ∧ cus.size = fus.size ∧
      ∀ i (h₁ : i < cus.size) (h₂ : i < fus.size),
        UnitBound E L re.se.ne.rv.environment sp.fences cus[i] fus[i]

def candidateContent (case : Json) (s : String) (i : Nat) : Option Json :=
  match (case.getObjValD "document").getObjValD "reading_sets" with
  | .arr rs => (rs.toList.find? (fun R => R.getObjValD "id" == .str s)).bind fun R =>
      match R.getObjValD "readings" with
      | .arr cs => cs[i]?.map (·.getObjValD "content")
      | _ => none
  | _ => none

/-- A reading's own sentence that Lean checked (D11): it reads, with one meaning, as the candidate's content. -/
def NameReadsBack (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (n : Name) : Prop :=
  ∃ φn : VE.EnglishGrammar.EFormula,
    VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget (n.text ++ ".") = .ok [(φn, false)] ∧
    candidateContent case n.set n.index = some φn.encode

structure Asked where
  request : Json
  text : String
  q : String
  case : Json
  E : VE.EnglishGrammar.Env
  L : VE.EnglishGrammar.Lexicon
  c : VE.Question.Candidate
  φ : VE.EnglishGrammar.EFormula
  x : VE.Readings.Wire.NDVerdicts
  rows : List Row
  names : List Name
  hbind : CaseBinding text case E L
  hrequest : request.getObjValD "document" = .str text ∧
    request.getObjValD "question" = .str q ∧ request.getObjValD "case" = case
  hreplay : VE.Readings.Run.replayVerdictsND case = .ok x
  hread : VE.Question.QuestionOneReading VE.Question.auxiliaries E {} L q c φ
  hψ : case.getObjValD "question" = .str "query" ∧
    Same (case.getObjValD "conclusion") φ.encode ∧
    VE.Route.Wire.decodeClosed (VE.Readings.Wire.fullEnv x.r.N ((x.evs.map (·.1)).headD []))
      (case.getObjValD "conclusion") = .ok x.φ
  hx : x.Γ = [] ∧ x.A = []
  hrows : rows.map (·.choice) = x.evs.map (·.1)
  hok : ∀ r ∈ rows, RowOk.{0} x.r.N x.φ r
  hnames : ∀ n ∈ names, n.checked = true → NameReadsBack case E L n

def replayAsk : Json → Except String Asked   -- Q2.2
def answerFor : Asked → Except String (Context × Answer)  -- Q2.3; the `ask` route renders only this result

theorem answerFor_bound : ∀ (asked : Asked) (ctx : Context) (a : Answer),
  answerFor asked = .ok (ctx, a) → RenderInputBound ctx a ∧
    a.request = asked.request ∧ a.text = asked.text ∧ a.case = asked.case ∧ a.x = asked.x ∧
    a.asked = asked.c ∧ a.rows = asked.rows ∧ a.names = asked.names

theorem ask_wire_sound : ∀ (j : Json) (a : Asked), replayAsk j = .ok a →
  a.request = j ∧ a.text = (j.getObjValD "document").getStr?.toOption.getD "" ∧
  a.q = (j.getObjValD "question").getStr?.toOption.getD "" ∧ a.case = j.getObjValD "case" ∧
  VE.Readings.Run.replayVerdictsND a.case = .ok a.x ∧
  (∀ r ∈ a.rows, LeadHolds.{0} a.x.r.N a.x.φ r) ∧
  (∀ r ∈ a.rows, ∀ x, r.reason = some x → ReasonHolds.{0} a.x.r.N a.x.φ r x) ∧
  (∀ c, Compatible a.x.r.N.D c ↔ c ∈ a.rows.map (·.choice)) ∧
  CaseBinding a.text a.case a.E a.L ∧
  VE.Question.QuestionOneReading VE.Question.auxiliaries a.E {} a.L a.q a.c a.φ

/-! ## The plain adapter (R13): `relational-fol@0` documents, no layers, no gaps -/

structure PlainRow where
  premise : ChoiceResult
  query : ChoiceResult
  negation : ChoiceResult
  deriving DecidableEq, Repr

def PlainRow.lead (r : PlainRow) : Lead := Row.lead ⟨[], .free, r.premise, r.query, r.negation, false⟩

def Consistent (E : VE.Environment) (Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0}, S.Admissible E ∧ ∀ a ∈ Γ, a.denote S []

def LeadHoldsPlain (E : VE.Environment) (Γ : List VE.Formula) (ψ : VE.Formula) (r : PlainRow) : Prop :=
  match r.lead with
  | .yes => Consistent E Γ ∧ VE.Entails.{u} E Γ ψ
  | .no => Consistent E Γ ∧ VE.Entails.{u} E Γ (.not ψ)
  | .notNecessarily => ¬ VE.Entails.{0} E Γ ψ
  | .notSettled => False
  | .unknown => True

def PlainRowOk (E : VE.Environment) (Γ : List VE.Formula) (ψ : VE.Formula) (r : PlainRow) : Prop :=
  (r.premise = .model → Consistent E Γ) ∧ (r.premise = .inconsistent → VE.Entails.{u} E Γ .bottom) ∧
  (r.query = .proved → VE.Entails.{u} E Γ ψ) ∧ (r.query = .refuted → ¬ VE.Entails.{0} E Γ ψ) ∧
  (r.negation = .proved → VE.Entails.{u} E Γ (.not ψ))

theorem plain_lead_sound : ∀ (E : VE.Environment) (Γ : List VE.Formula) (ψ : VE.Formula) (r : PlainRow),
  PlainRowOk.{u} E Γ ψ r → LeadHoldsPlain.{u} E Γ ψ r
theorem plain_never_split : ∀ r : PlainRow, r.lead ≠ .notSettled

/-- The plain adapter has the same file-to-case unit conversion and source-byte binding as `CaseBinding`, but
    replays through the lower `relational-fol@0` checker. -/
def PlainCaseBinding (text : String) (case : Json) (E : VE.EnglishGrammar.Env)
    (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment) : Prop :=
  ∃ sp : VE.Discourse.Loader.Split, VE.Service.Document.split text = .ok sp ∧
    Same (case.getObjValD "environment") (sp.front.getObjValD "environment") ∧
    (∀ k ∈ boundKeys, Same ((case.getObjValD "document").getObjValD k) (sp.front.getObjValD k)) ∧
    VE.EnglishGrammar.Env.decode (sp.front.getObjValD "environment") (Json.mkObj []) = .ok E ∧
    L.policyOk E {} = true ∧
    ∃ cus fus : Array Json, (case.getObjValD "document").getObjValD "units" = .arr cus ∧
      sp.front.getObjValD "units" = .arr fus ∧ cus.size = fus.size ∧
      ∀ i (h₁ : i < cus.size) (h₂ : i < fus.size), UnitBound E L V sp.fences cus[i] fus[i]

structure PlainVerdict where
  V : VE.Environment
  Γ : List VE.Formula
  ψ : VE.Formula
  row : PlainRow
  hok : PlainRowOk.{0} V Γ ψ row

def replayPlain : Json → Except String PlainVerdict  -- Q2.2: the lower checker and its accepted evidence

structure PlainAsked where
  request : Json
  text : String
  q : String
  case : Json
  E : VE.EnglishGrammar.Env
  L : VE.EnglishGrammar.Lexicon
  c : VE.Question.Candidate
  φ : VE.EnglishGrammar.EFormula
  x : PlainVerdict
  hrequest : request.getObjValD "document" = .str text ∧
    request.getObjValD "question" = .str q ∧ request.getObjValD "case" = case
  hbind : PlainCaseBinding text case E L x.V
  hreplay : replayPlain case = .ok x
  hread : VE.Question.QuestionOneReading VE.Question.auxiliaries E {} L q c φ
  hψ : Same (case.getObjValD "conclusion") φ.encode ∧
    VE.Route.Wire.decodeClosed x.V (case.getObjValD "conclusion") = .ok x.ψ

def replayPlainAsk : Json → Except String PlainAsked
theorem plain_ask_wire_sound : ∀ (j : Json) (a : PlainAsked), replayPlainAsk j = .ok a →
  a.request = j ∧ a.text = (j.getObjValD "document").getStr?.toOption.getD "" ∧
  a.q = (j.getObjValD "question").getStr?.toOption.getD "" ∧ a.case = j.getObjValD "case" ∧
  replayPlain a.case = .ok a.x ∧ PlainCaseBinding a.text a.case a.E a.L a.x.V ∧
  VE.Question.QuestionOneReading VE.Question.auxiliaries a.E {} a.L a.q a.c a.φ ∧
  LeadHoldsPlain.{0} a.x.V a.x.Γ a.x.ψ a.x.row
end VE.Ask
```

**What changed from plan 4.7.** `Row.reason`, `ReasonHolds`, `reason_sound` and `reason_exact` carry X6 (R9).
`Asked` carries the request, document bytes, case, `E`, `L`, binding and names. `hreplay` ties `x` to that case's
RD-3 replay; `hrequest` and `ask_wire_sound` tie the document, question and case to the request. `ψ` is RD-3's
decoded conclusion `x.φ`, tied to the question's `φ` by the case's actual `conclusion` bytes and `decodeClosed` over
the first choice's environment, as RD-3's `queryFormulas` does. The plain route must use the same request-field,
document binding and replay equations before it renders a `PlainRow`.
`Source.rules` carries the predicate only; its units are named at render. `groups`, `groups_cover`, `group_rows`,
`group_claim`, `render_covers_rows`, `render_marks_unchecked` and `render_unused_once` are new (R7, R8).
`relevantSets_sound` gains `ids.Nodup`, `r.choice.map (·.1) = ids` and "the key is a function of the choice":
without them the fallback to every set is not a separating set. The plain adapter is chosen (R13).

**Proof notes for Q2.1 and Q2.2.** `lead_sound` and `reason_sound` read `Holds` (RD-3) case by case, with
`List.append_nil` for `Γ ++ []`. `split_counter` takes `S₂`. `splitOk_sound` takes `B := m₁.M.asStructure` and
the two `finFill`s, by the base equation that `expansion_of_modelCheck`'s proof establishes (`hr`). `all_yes_iff_fold`
reads `foldConflict` and `foldEntailment`. `usedPositions_sufficient` is `usedLabels_sound` (the labels `toString i`
are distinct), then `checkCertificate_sound`, then a lemma that `⊤` premises change no entailment.
`relevantSets_sound` holds for the greedy result by `separates`, and for the fallback because a row's choice is
fixed by its indices on `ids`. `group_claim` is `group_rows` and `relevantSets_sound`.

## 6. Limits (Lean-owned, `VE.Question`)

| Limit | Value | Over it |
|---|---|---|
| Question bytes | 4,096 (`maxQuestionBytes`) | `QuestionTooLong` |
| Tokens of the body | 300 (`maxTokens`) | `QuestionTooLong` |
| Candidates | 64 (`maxCandidates`) | `QuestionTooLong` |
| Work per candidate | E2's `workBudget`, 2,100,000 steps; each candidate is one `read` | `Budget` |
| Rephrasings | each offered rephrasing is subject to the same limits; `rephrasings_read` assumes them (R4) | the theorem does not apply (open point 10.3) |
| Compatible choices (Q2) | RD-3's 64 (`maxChoices`) | lead *unknown*, X5 |
| Latency | p95 ≤ 100 ms for a corpus question; ≤ 1 s for a 64-candidate question. Two gates, each measured on whole questions; each met, or its revision reviewed (R12). Provisional targets: no per-sentence figure is multiplied out. | Q1.3 reports it |

## 7. Acceptance fixtures

*Computed* means evaluated by `#eval` in a stub (section 11). *Derived* means worked out by reading, not run.
Formulas are `EFormula`s written without their namespace: `all s φ`, `ex s φ`, `not φ`, `implies φ ψ`,
`pred p [args]`, `var i`, `const c`.
Q1.1's `#guard`s check every emitted fixture span in code points with `start ≤ stop ≤ q.length`, including
G25's crossing interval and G26's Unicode conversion. The correction's targeted joint review precedes acceptance
of those guards.

### 7.1 G: the group document, rewritten (F1)

`usecases/question-answering/group.ve.md` (written in Q2.5):
- **Profiles:** `documents@1`, `relational-fol@0`.
- **Sort:** `member`, noun `member`, plural `members`.
- **Predicates:** `registered(member)`, `{0} is registered`; `eligible(member)`, `{0} is eligible`;
  `verified(member)`, `{0} is verified`.
- **Constants:** `ann`, `bo` (sort `member`).
- **Sentences** (English fences): 1. `Every member is registered.` 2. `Every member who is registered is eligible.`
  3. `Ann is verified.`

*Computed:* the policy's lexicon (`portLex`) is nouns `[(member, member)]`, wordings as declared, no negatives,
spellings `ann`, `bo`; `policyOk` is true and `grammarFault` is `none`. The sentences read
`all member (pred registered [var 0])`, `all member (implies (pred registered [var 0]) (pred eligible [var 0]))` and
`pred verified [const ann]`.

### 7.2 G: the questions (Q1 computed, Q2 derived)

| # | Question | Candidates and `got` (*computed*) | Q1 (*computed*) | Q2 (*derived*, plain adapter) |
|---|---|---|---|---|
| G1 | `Is every member eligible?` | `every is member eligible.` none; `every member is eligible.` one | **one**, F2 `is` at gap 13 (the gaps are 6 and 13); asked `every member is eligible.`; `all member (pred eligible [var 0])` | **Yes.** C1 for sentences 1 and 2; not 3. |
| G2 | `Is it the case that every member is eligible?` | `every member is eligible.` one | **one**, F1; the same formula as G1 | as G1, after A0 |
| G3 | `Is every member verified?` | `every is member verified.` none; `every member is verified.` one | **one**; `all member (pred verified [var 0])` | **Not necessarily.** S1: a situation where Bo is not verified (elements are the search's). |
| G4 | `Is it the case that no member is eligible?` | `no member is eligible.` one | **one**; `not (ex member (pred eligible [var 0]))` | **No.** C1 for 1 and 2 (Ann exists, is registered, hence eligible). |
| G5 | `Is a member eligible?` | `a is member eligible.` none; `a member is eligible.` none | **indefinite**, `IndefiniteQuestion`: `VE cannot tell whether "a" here means every or some. Ask one of these instead:`; rephrasings `Is every member eligible?`, `Is some member eligible?`; span (0, 21) | — |
| G6 | `Is every member eligible` | — | **notQuestion**, `NotOneQuestion`; span (0, 24) | — |
| G7 | `Does every member vote?` | — | **none**, `QuestionForm`: `VE answers questions that begin with "Is", "Must" or "May", or with "Is it the case that" followed by a sentence.`; span (0, 23) | — |
| G8 | `Who is eligible?` | — | **none**, `QuestionForm`: `VE answers yes-or-no questions. It does not answer who, what or which questions yet.`; span (0, 16) | — |
| G9 | `Must Ann be eligible?` | `Ann must be eligible.` none; `Ann be must eligible.` none | **none**, `NoDerivation`: `The question has no reading with the current vocabulary. Closest sentence tried: "Ann must be eligible.". Unknown English phrase 'must be eligible'. Nearest declared wordings: 'is eligible'; 'member'; 'is verified'.`; span (0, 20); no advice | — |
| G10 | `Is Ann eligible?` | `Ann is eligible.` one | **one**; `pred eligible [const ann]` | **Yes.** C1 for 1 and 2. |
| G11 | `Is every member who registered is eligible?` | five candidates; only `every member who is registered is eligible.` reads; the gaps before `is` and before `eligible` both give `every member who registered is is eligible.` (F4) | **one**, odd English accepted (plan 4.9); `all member (implies (pred registered [var 0]) (pred eligible [var 0]))` | **Yes.** C1 for sentence 2 only. |
| G12 | `Is every member eligible and?` | `every is member eligible and.`, `every member is eligible and.`, `every member eligible is and.`, all none | **none**: `… Closest sentence tried: "every member is eligible and.". Expected '.' here. Use the English paraphrase as a writing example.`; span (24, 28) | — |

### 7.3 Every other Q1 outcome (computed)

| # | Question, and its document | Q1 (*computed*) |
|---|---|---|
| G13 | `Is it the case that therefore Ann is eligible?` (G) | **rejected**, `QuestionWithMarker`: `A question cannot contain "therefore", "so", "hence" or "it follows that".`; span (0, 46). `read` of the body gives `.ok [(pred eligible [const ann], true)]`. |
| G14 | `Is it eligible?` (G) | **rejected**, `PronounUnresolved`: `The question uses "it", and it is not settled what "it" refers to. Repeat the name.`; asked candidate `it is eligible.`; span (0, 15) |
| G15 | `Is every member eligible ?` (G) | **rejected**, `BadSpacing`: `The spacing at position 25 is not allowed: write no space before the question mark.`; span (25, 26) (F3) |
| G16 | `Is every member eligible? Is Ann eligible?` (G) | **notQuestion** (two `?`); span (0, 42) |
| G17 | `Is it the case that every member is happy?` (G) | **none**: `… Closest sentence tried: "every member is happy.". Unknown English phrase 'is happy'. Nearest declared wordings: 'ann'; 'bo'; 'member'.`; span (32, 41). `read` of the body: `.stopped 0 .noDerivation`. |
| G18 | `Is Ann eligible. Bo eligible?` (G) | **notQuestion** (the body is two sentences); span (0, 29) |
| G19 | `Is every member eligible!?` (G) | **rejected**, `BadCharacter`: `The character at position 24 cannot appear outside a quoted name.`; span (24, 25) |
| G20 | `Is every member` followed by ` eligible` 70 times, then `?` (G) | **budget**, `QuestionTooLong`; 646 bytes, 71 candidates; `withinLimits` is false |
| G21 | `Is every member eligible?` (G) at budget `b = 0` | **budget**, `Budget`: `VE stopped reading this question at its work limit.`; the first candidate `every is member eligible.`; span (0, 25) |
| G22 | `Is every deployed service reviewed?` (base 8.1's `FD`, with the policy's lexicon, whose nouns include `deployed service`) | **many**, `Ambiguous`: `The sentence "every deployed service is reviewed." can be read in more than one way. Two of the ways are shown.`; candidate `every deployed service is reviewed.`; span (0, 35). Control: `Is every service reviewed?` on `FD` is **one**. |
| G23 | `Is legacy deployed?` (base 8.3's `F` with `LFv3`, a lexicon that fails V5) | **invalidGrammar**: `The vocabulary selection was not accepted (invalidGrammar lexicon: V6 negative owns). No text was read.` |
| G24 | speech acts' `auxs = ["is"]` (Q1.4) on G: `Is Ann eligible?`; `Must Ann be eligible?`; `Is it the case that Ann is eligible?` | **one** (`Ann is eligible.`); **none**, `QuestionForm`: `VE answers questions that begin with "Is", or with "Is it the case that" followed by a sentence.`; **one**. Q1.4 maps the second to speech acts' `ModalQuestion` refusal, with Lean's text. |
| G25 | `Is every and?` (G): closest `every is and.`, diagnosis span (5, 8) in candidate bytes | **none**, `NoDerivation`; interval images [8, 9) and [0, 2) enclose to question span **(0, 9)**. This crosses the movement boundary; the old endpoint rule returned (8, 2). |
| G26 | `Is "é" and?` (G): first candidate `"é" is and.`, diagnosis span (0, 4) in candidate bytes | The interval maps to question bytes (3, 7), then to code points **(3, 6)**. This pins the byte-to-code-point conversion with a non-ASCII character. |

### 7.4 A: the agent policy (R6)

**Q1** (*computed*) on the environment of the A documents: `usecases/agent-policy/environment.unspecified.json` with
the constants of `log.vocabulary.json`. The policy's lexicon passes (`policyOk` true, `grammarFault` none). Q1
depends only on the vocabulary, so it is the same on all four A documents.

**The documents.** Plan 6.2's four documents. The conflict-free variant of R6 is the agent policy's mutant m1
(`usecases/agent-policy/mutants.py`: rule 3, write-workspace, added to rule 14's exception list), which
`results.json` (M9, `packages:mutant m1`) records as CONFLICT-FREE while the original rules have a checked witness
(`witness:permitted`, CONFLICT) (F8). The fixture actions a13 (`delete_file`) and a25 to a27 (`send_email`) are not
writes, so m1 should not change their statuses; Q2.5 confirms it by running the check on the variant.

| # | Question | Document | Q1 (*computed*) | Q2 (*derived*) |
|---|---|---|---|---|
| A1 | `May "a27" be performed?` | unspecified | **one**; asked `"a27" may be performed.`; `pred permitted [const a27]` | **The text does not settle this.** S2: a27's situation, then `The text does not say whether "a27" may be performed.` |
| A1d | the same | deny | the same | **No. The document rules this out.** C2, and C1 for each a27 record sentence the certificate uses |
| A2 | `May "a25" be performed?` | unspecified | **one**; `pred permitted [const a25]` | **Yes.** C2 for `permitted`; C1 for the a25 sentences used |
| A3 | `May "a26" be performed?` | unspecified | **one**; `pred permitted [const a26]` | **No. The document rules this out.** |
| A4 | `Must "a13" be reported to the user?` | unspecified | **one**; asked `"a13" must be reported to the user.`; `pred report_required [const a13]` | **Yes.** C2 or C1 for rules 25 and 26; C1 for the a13 sentences used |
| A5 | `May "a10" be performed?` | conflict | **one**; `pred permitted [const a10]` | **VE could not decide this.** X1 with the conflict witness |
| A6 | `May an action be performed?` | any | **indefinite**: `VE cannot tell whether "an" here means every or some. Ask one of these instead:`; rephrasings `May every action be performed?`, `May some action be performed?`; span (0, 27) | — |
| A7 | `May every action be performed?` | rules | **one**; asked `every action may be performed.`; `all action (pred permitted [var 0])` | **Not necessarily.** S1 (for example an unconfirmed purchase) |
| A8 | `Must every action be reported to the user?` | unspecified | **one**; `all action (pred report_required [var 0])` | **The text does not settle this** (a split on `report_required`) |
| A9 | `Must an agent not send email unless the user confirms?` | any | **none**: `… Closest sentence tried: "an must agent not send email unless the user confirms.". Unknown English phrase 'an must agent'. Nearest declared wordings: '"spawn_agent"'; 'messages {1}'; '"f_env"'.`; span (0, 13); advice `Write "every" or "some" in place of "an".` (F5) | — |

Every Q2 answer above ends with U1 if the document has unformalised sentences (D14).

### 7.5 U: the UDHR pilot, part 7

**Q1** (*computed*) on the environment of the front matter of
`manage-agents/pilots/udhr/run-20261008T1800Z/translation-part07.ve.md`, with the policy's lexicon (`policyOk`
true, `grammarFault` none). Sentence numbers are display numbers: units `u087` to `u103`, with `u099a`, `u099b`,
`u100a` and `u100b`, are sentences 1 to 19; the unformalised ones are 3, 5, 6, 7, 8, 11, 17, 18 and 19.

| # | Question | Q1 (*computed*) | Q2 (*derived*) |
|---|---|---|---|
| U1 | `Must every qualified person be given access to higher education?` | **none**: `… Closest sentence tried: "every must qualified person be given access to higher education.". Unknown English phrase 'must qualified person be given access to higher education'. Nearest declared wordings: 'must be spared exclusion from education'; 'must receive elementary education'; 'is classified as "has_the_right_to_education"'.`; span (0, 63) (F5, F6) | — |
| U2 | `Must every person be given equal access to higher education on the basis of merit?` | **one**; `all person (pred equal_access_to_higher_education_required [var 0])` | **Yes.** C1: `Sentence 14 says: "and higher education shall be equally accessible to all on the basis of merit."`; R2; U1 |
| U3 | `Must every person be spared exclusion from education?` | **one**; `all person (pred education_spared_required [var 0])` | by sentence 10's reading: `claim_negative` gives **yes**, with "(VE has not checked this wording)" (a norm candidate); `entitlement` gives **the text does not settle this** (S2). `relevantSets = [rs_u096]`; U1. Plan 4.6's worked example. |
| U4 | `Is it the case that every person has the right to education?` | **none** (F7): `… Unknown English phrase 'has the right to education'. Nearest declared wordings: 'is classified as "has_the_right_to_education"'; 'course of education'; 'is classified as "asylum_right_covers_case"'.`; span (32, 59) | — |
| U5 | `May every person form as well as join trade unions to protect their interests?` | **one**; `all person (pred person_may_form_and_join_trade_unions [var 0])` | by sentence 1's reading: `liberty` gives **yes**; `entitlement` and `claim_negative` give **the text does not settle this**; U1 |
| U6 | `Must every person receive elementary education?` | **one**; `all person (pred elementary_education_received_required [var 0])` | **Yes.** C1 for sentence 12; R2; U1 |
| U7 | `Must every education kind be made generally available?` | **one**; `all education_kind (pred education_generally_available_required [var 0])` | **The text does not settle this.** S2: an education kind neither technical nor professional; U1 |
| U8 | `May a university charge fees?` | **none**: closest `a may university charge fees.`, E2.6's `Expected …` list; span (4, 5); advice `Write "every" or "some" in place of "a".` Neither `May every university charge fees?` nor `May some university charge fees?` reads, so the indefinite help does not apply. | — |
| U9 | `Does every person have the right to education?` | **none**, `QuestionForm` (another first word); span (0, 46) | — |

### 7.6 Q2: rows, reasons, folds and groups (computed against RD-3's branch)

- **Every row.** All 4,802 rows (7 results for each of the four rows, two split flags, choice `[]`):
  `lead_agrees` holds on every one, and so does `reason_exact` (both directions: the 4,482 rows with lead
  *unknown* all have a reason; the 320 others have none). Leads: yes 14, no 12, not settled 252, not necessarily
  42, unknown 4,482. Reasons: X1 686, X2 3,430, X3 56, X6 130, X4 180.
- **Decisive rows.** (free, model, proved, unknown, no split) is *yes*. (free, unknown, proved, unknown) has reason
  X6. (free, model, unknown, proved) is *no*. (free, model, refuted, unknown, split) is *not settled*; without the
  split, *not necessarily*. (conflict, model, proved) has X1. (free, inconsistent, proved) has X3. In particular,
  `(free, model, unknown, proved, false)` has lead *no* while the query row and its fold may stay UNKNOWN; a checked
  ¬ψ certificate is a different kind of evidence from a checked query countermodel.
- **Defaults conflict without two rules.** W1's required-by-default and forbidden-by-default pair can produce a
  checked CONFLICT with zero rules. The corresponding row has X1 and prints `The document's rules or defaults
  conflict in this situation, so VE cannot answer: …`.
- **`all_yes_iff_fold`.** On all 155 lists of one to three rows drawn from five sample rows: the two sides agree on
  every list; both hold on 3 lists and both fail on 152.
- **Groups, two sets (R7).** Two binary sets `a`, `b`, *yes* on (0, 0) and (1, 1), *not necessarily* elsewhere:
  `relevantSets = [a, b]`; `separates` is false for `[a]` and for `[b]`, true for `[a, b]`; four groups of one row
  each, so the two *yes* rows are two R1 blocks.
- **Groups, U3's shape.** Six rows over `rs_u087` (3 candidates) and `rs_u096` (2): `relevantSets = [rs_u096]`
  (`separates` true for it, false for `[rs_u087]`); two groups of three rows: *not settled* on `rs_u096 = 0`,
  *yes* on `rs_u096 = 1`.

### 7.7 Each direction of every "exactly when" claim

| Claim | Both sides hold | Both sides fail | At a hypothesis's edge |
|---|---|---|---|
| `readQuestion_one` with `readQuestion_complete` (one exactly when `QuestionOneReading`, under the hypotheses) | G1, G2, G10, G11, A1, U2 | G9, G12, G17 (no candidate reads) | G21 (budget 0: G1's question, whose `QuestionOneReading` holds, is `budget`); G20 (`withinLimits` false) |
| `caseThat_reads` | G2, G4 | G17 (the body has no derivation); G13 (the body reads with a conclusion mark, not `[(φ, false)]`) | — |
| `reason_exact` | the 4,482 *unknown* rows | the 320 others | — |
| `all_yes_iff_fold` | 3 lists | 152 lists | — |
| `CaseBinding` (exactly the document's case) | the fixture documents' own cases, including a front-matter `{"ast": φ}` compiled to bare `φ`, an English fence and a strict fence each compiling to one bare formula, and preserved norm content (Q2.2) | a changed bare AST, a fence with no or two formulas, a fence whose bare compiled formula differs, a changed norm, and another environment (Q2.2) | — |
| `Asked` replay and request binding | `replayVerdictsND a.case = .ok a.x`, with `a.text`, `a.q`, `a.case` equal to the request's fields (Q2.2) | a replayed case from another document, a substituted question, a changed conclusion, or unrelated evidence; the plain adapter has corresponding cases | — |
| `Compatible c ↔ c ∈ rows` (`ask_wire_sound`) | every compatible choice of U3 and U5 (Q2.2, from RD-3's replay) | a choice an excluded narrowing removes (Q2.2) | — |

The Q2 rows of this table are *derived* until Q2.2 records the cases.

### 7.8 Mutants and negative fixtures

| Mutant | Must fail |
|---|---|
| F1 precedence removed | `caseThat_candidates`; G2 |
| a gap allowed before punctuation, or at the end | `fronted_text`'s `#guard`s; G1's candidate list |
| `got` without its sentence-count check | G18 |
| `got` counting `refused` as a reading | G13 |
| a refused candidate blocking a question that reads (the draft-1 order) | `readQuestion_complete`; a question with one refused and one reading candidate (Q1.1 builds one; none of section 7 has both) |
| `Row.lead` letting a countermodel give `.no` | A7 and G3; `lead_agrees` |
| the premise-model gate removed | X3 on an inconsistent document; `reason_exact` |
| X6 merged into X4 | the (free, unknown, proved) row |
| `usedPositions` returning every position | G1 (sentence 3 cited) |
| a quote taken from the case instead of the document | the binding fixtures of 7.7 |
| a fenced unit's content not re-read | the fence fixture of 7.7 |
| `{"ast": φ}` compared to the compiled content without unwrapping | the successful AST fixture of 7.7 |
| a strict fence passed through the English reader | the successful strict-fence fixture of 7.7 |
| `Asked.x` replayed from another case | the request/replay binding fixtures of 7.7 |
| groups keyed by lead and citations only | the two-set example of 7.6 (one *yes* block instead of two) |
| an unchecked wording shown without its parenthesis | `render_marks_unchecked`; U3 |
| an ordinal shown in place of a failed wording | the name-check fixture (Q2.3) |
| U1 dropped after *yes* | U2, U6 |
| U1 printed twice for a grouped answer, or with the wrong count or units | U3's grouped answer; `render_unused_once` |
| R2 shown with one unchecked choice | the gate test |
| a situation naming one set of two | `render_model_names_choice` |
| a situation naming the right set ids but the wrong candidate indices, or using an unchecked witness | `render_model_names_choice` |
| `Line.text` disagreeing with its quote, citation, readings or witness metadata | `render_text_matches_metadata` |
| the split check not comparing the base models | a fixture with two different bases (Q2.2) |

## 8. Wire

- **`english.question`** (Q1.2): case = `english.read`'s case fields plus `question`, decoded by
  `VE.EnglishGrammar.Run.decodeCase`. Result: `status` (`one`, `many`, `indefinite`, `none`, `rejected`,
  `notQuestion`, `budget`, `invalidGrammar`; F10), with `form`, `sentence`, `ast` and `spans` for `one`; `code`,
  `class`, `text`, `span`, `advice`, `rephrasings` and, for `Ambiguous`, `witnesses` otherwise; `identities` (E2's
  six with `source_sha256` over the question, plus `question_version`). The fields per status are 4.1's.
- **`ask`** (Q2.2): plan 4.8, with the binding of 5.2. `unchecked_names` stays in the response, and the printed
  text marks the same names (R8).

## 9. Statement review checklist (Astra and Fable)

1. Is `QuestionOneReading` (R3) the right notion: does a refused candidate beside a reading one correctly leave the
   reading, and does an ambiguous candidate correctly block it?
2. Does `readQuestion_complete` need any hypothesis it lacks, or carry one it does not need?
3. Is `caseThat_reads` true as stated, including a body that itself begins with `Is it the case that`, a body with a
   leading space, and a body with a conclusion marker (G13)?
4. Does `fronted_text` pin the candidate's bytes exactly? Is `caseFrame.isPrefixOf q = false` right for F2?
5. Are `rephrasings_read`'s limit hypotheses (R4) acceptable, given open point 10.3?
6. Is 4.1's order of diagnostics right, and is each text one-reading English for a reader with no training?
7. Is `Row.reason` right, X6 included (R9)? Is `reason_sound`'s X6 claim (a proof, conflict-free) the honest one?
8. Does `CaseBinding` implement the compiler's bare AST, norm and one-formula fence conversions on both surfaces,
   and do `hreplay`, `hrequest` and `hψ` bind the checked verdict to this request? Does the plain adapter meet the
   same binding contract?
9. Do `groups_cover`, `group_claim` and `render_covers_rows` together give coverage and correctness (R7)? Are the
   hypotheses of `relevantSets_sound` true of RD-3's rows?
10. Do `render_marks_unchecked`, `render_unused_once`, `render_model_names_choice` and
    `render_text_matches_metadata` put the checked content into the printed text (R8)?
11. Is the plain adapter's `LeadHoldsPlain` the right claim for `relational-fol@0` documents (R13)?
12. Does any statement about an opaque Q2.3 function (`render`, `renderGroup`) need a property of its body that the
    statement does not name?

## 10. Open points

1. **No "many meanings" fixture** (F2). Q1.1 constructs one if a vocabulary gives one; Q1.3 measures the outcome
   on the reverse corpus. If it never occurs, the review may accept the theorem alone.
2. **The closest candidate** (F5). Ties go to the leftmost, which in A9, U1 and U8 is the candidate with the moved
   word second. Q1.3 counts how often the diagnosed sentence is not the one a reader would pick; a better tie rule
   (for example, the candidate whose gap follows the subject's noun phrase) needs a statement of its own.
3. **Rephrasings near the limits.** An F1 rephrasing is 20 bytes longer than its question and has one more token,
   so a question within 20 bytes or one token of a limit can offer a rephrasing that is itself over the limit.
   `rephrasings_read` assumes the limits (R4). Q1.1 may instead drop such rephrasings, which would make the
   hypothesis unnecessary; either is honest.
4. **Content conversion closed by Q0 review.** Python compiles `{"ast": φ}` and a one-formula fence to bare `φ`;
   norm content remains the norm object. Q2.2 checks that the Lean binding matches the compiler on AST, English
   fence, strict fence and norm fixtures before the Q2 statement review.
5. **Q2 computation.** Every Q2 lead in section 7 is derived. When RD-3 merges, the Q2 stub is elaborated against
   the merged build, the generators run on the fixture documents, and the Q2 statements go to review (R14).

## 11. How the figures were computed

### 11.1 The Q1 stub

`lean/SpecStubs_question-answering.lean`, importing `VE.EnglishGrammar.E2Examples` (for base 8's environments and
`portLex`, the port of Python's vocabulary choice). Before the Q0 review it held sections 2.1 to 2.5 verbatim and
the then-current statements of 5.1 as `def … : Prop`, with a `summarize` function implementing 4.1's table. Run with Lean
4.24.0 as

```text
lake -d /home/seyran/code/ve-testmap/lean env lean lean/SpecStubs_question-answering.lean
```

`ve-testmap` is a worktree detached at `c85797de`, this branch's base, with a built `.lake`; this worktree has no
build. The command the brief gives (`cd lean && PATH=… lake env lean …`) was refused by this session's permission
mode, while `lake` itself was allowed, so the stub was elaborated against that build of the same commit. Result:
no errors. The A environment was read from `usecases/agent-policy/environment.unspecified.json` and
`log.vocabulary.json`, the U environment from the pilot file's front matter, both by `IO.FS.readFile` in `#eval`.

After the Q0 review, a copy at `/tmp/qa-span-check.lean` replaced the old endpoint functions with section 2.5's
`mapPoint`, `mappedPiece` and `mapSpan`, and used the mapped pair in `summarize`. It elaborated without errors
against the same build. Its `#eval` recomputed G9 (0, 20), A9 (0, 13), U1 (0, 63), G25 (0, 9), and the G26
Unicode byte interval (3, 7), corresponding to code points (3, 6). This check did not prove `mapSpan_valid` or
`mapSpan_codepoints_valid`; both new statements were also elaborated as `def … : Prop` against the same build. The
targeted joint span review and Q1.1 still have to establish their truth.

### 11.2 The Q2 stub

`lean/SpecStubs_question-answering-q2.lean`, importing `VE.Readings.VerdictsWire`, `VE.Service.Document` and
`VE.EnglishGrammar.Read`, with a copy of the part of 2.1 to 2.3 that `QuestionOneReading` needs (RD-3's branch
predates E2.6's `Diagnose`). Before the Q0 corrections it held 5.2's definitions, its statements as `def … : Prop`,
and the `#eval`s of 7.6.
Run as

```text
lake -d /home/seyran/code/ve-rd-3/lean env lean lean/SpecStubs_question-answering-q2.lean
```

against RD-3's branch at `70cc2549` (not merged). Result for the pre-correction draft: no errors; one linter warning,
the unused variable `e` in `splitOk_sound`, which the proof needs for `WellFormedU`. The text functions and
`replayAsk` were declared `opaque` there (no `sorry`). A later temporary copy at `/tmp/qa-q2-types.lean` replaced
the text and wire section with the Q0-corrected definitions, used `opaque` for the Q2.2/Q2.3 functions, and
elaborated the theorem types as axioms against the same RD-3 branch. It had no errors and the same unused-variable
warning. This established type consistency only; neither the corrected statements nor binding fixtures have been
reviewed against merged RD-3.

### 11.3 Run 1: the plan's G document

With the plan's environment (`{0} is a citizen`, `{0} is a person`, `{0} is an adult`, noun `member of the group`),
`portLex` selects `entity of sort "member"` and `{0} is classified as "…"` for all three predicates. A hand-written
lexicon with the declared wordings fails the policy (`V6` for all three predicates and the sort). Under the policy's
lexicon, all three sentences of plan 6.1 are `.stopped 0 .noDerivation` (F1).

### 11.4 Not run

Python, the service and its modes, the relay, the evidence generators, the readability evaluation, and every proof.
Neither stub is committed; both are untracked worktree files outside this document edit.
