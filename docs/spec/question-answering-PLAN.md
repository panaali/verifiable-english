# Question answering in VE, parts Q1 and Q2: buildable plan

**Status:** plan, draft 1, 2026-10-08, branch `design/question-answering` at `c85797de` (`main` after the E2.6 flip).

**Brief:** the lead-approved item "Question answering in VE" (2026-10-08), parts Q1 and Q2. Sources: `ve-northstar/NORTH-STAR.md`, the section of that name, and `manage-agents/ARCH-ROADMAP.md` line 53.
- Q1: questions written as English questions and read by the Lean English grammar.
- Q2: answers written in English, with reasons, rendered by Lean.

**What was done for this draft.**
- Planning only. No code, proof or test changed.
- No VE model call was made (no translator, reader or judge). The repository was read by hand and with read-only search agents.
- **The Lean statements below were not elaborated.** Every name they use was read at `c85797de`. Where a name exists only on the unmerged RD-3 branch (`readings-defaults/rd3`, worktree `ve-rd-3`), the text says so. Elaborating them is Q0's first step.
- Every fixture value is *derived*: it was worked out by reading the sources and was not run. Q0 computes it.

**Builds on:**
- **English E2.6.** `english.admission` is Lean-authoritative ([E2.6.md](../lean-first/e2/E2.6.md)). This plan uses the reader `VE.EnglishGrammar.read` and its statements, and the diagnosis `VE.EnglishGrammar.diagnose` ([english-lean-e2.md](english-lean-e2.md) 4.5).
- **readings-defaults.** RD-1, RD-2a, RD-2b, RD-6a and RD-8 are merged. **RD-3 is not merged.** RD-3 provides `readings-verdicts`: the Lean fold, `usedLabels` and filled models ([readings-defaults-PLAN.md](readings-defaults-PLAN.md) 3.5 and RD-3). Q2 needs it (D3).
- **Speech acts' polar questions** ([speech-acts.md](speech-acts.md); `lean/VE/SpeechActs/Answer.lean`).
- **The lean-first rules** (`design/lean-first:docs/LEAN-FIRST-PLAN.md` draft 3, section 1, rules 1 to 6):
  - one owner per piece of logic;
  - Lean owns meaning and acceptance;
  - Python relays and displays;
  - generators are untrusted, and Lean checks every proposal.

## 0. Decision in brief

1. **A question is one of the document's own sentences, asked.** Q1 knows two forms:
   - `Is it the case that <sentence>?`. This is the form speech acts already use.
   - A sentence whose verb word *is*, *must* or *may* is moved to the front. Examples: "Is every member of the group a person?", "Must every person be …?", "May "a27" be performed?".

   Lean builds candidate sentences from the question. For the first form it drops the frame; for the second it puts the fronted word back at each place it can go. Lean reads each candidate with the existing reader `read`. The question's reading is the one meaning the candidates give.

   Nothing in the English grammar, the lexer, the lexicon or the six identities changes (D1, D2).
2. **One reading per question, or VE asks for a rephrasing.**
   - A question with two meanings gets one `Is it the case that …?` question per meaning, each of which VE reads one way.
   - An "a" or "an" in subject position ("May a university charge fees?") is the generic article, which English uses for both *every* and *some*. VE offers the *every* and the *some* question.
   - A question with no reading gets Lean's E2.6 diagnosis of its closest candidate, placed on the question's own words, plus advice on question forms (D5).
3. **Every answer begins with the sentence VE read:** "You asked whether every member of the group is a person." These are the asker's own words, reordered, and they read back with exactly the question's reading (theorem). This is how a reader who has had no training sees what was checked (D6).
4. **Five leads, each a checked claim** (D4):

   | Lead | Checked claim |
   |---|---|
   | **Yes.** | A certificate for the sentence. |
   | **No. The document rules this out.** | A certificate for the sentence's negation. |
   | **The text does not settle this.** | One situation, two fillings of the points the text leaves unsaid, with the sentence true under one filling and false under the other. This is norm-defaults' UNDECIDED applied to a whole sentence. |
   | **Not necessarily.** | A countermodel, shown as "Here is a situation the document allows where it fails: …". |
   | **VE could not decide this.** | Nothing settled; the reason is given. |

   A countermodel alone is never "No". This departs from the brief's wording; D4 gives the evidence for the change.
5. **The reasons are exactly the premises the certificate needs.**
   - Lean computes which premises the accepted certificate uses, with RD-3's `usedLabels`, one label per premise.
   - Lean maps each used premise to its source: a sentence of the document, the rules on one act, or a fixed VE premise.
   - The text cites exactly those sources and quotes the document's own bytes for each cited sentence.
   - The cited premises alone entail the sentence (theorem) (D7, D8).
6. **Readings.**
   - Lean makes one row per compatible choice, using RD-3's enumeration.
   - The text groups choices by answer and names only the sentences whose reading changes the answer.
   - When there is one group, the text says "Every way of reading the document gives this answer." (D9).
7. **Lean owns the question, the verdict, the answer and its text.** That covers:
   - the frames and the leads;
   - the cited sentences, quoted from the document's own bytes;
   - the situation lines and gap clauses. These come from a new module, `VE.Words`, which in Q2.4 also takes over Python's wording of the same lines.

   One kind of slot text comes from outside Lean and is marked as such: a reading's own sentence. That is RD-3's `<reading>` slot, rendered by Python until E3. Lean checks it by reading it back when the candidate is an assertion (D10, D11).
8. **What Python does: `ve ask <document> "<question>"`.**
   - It reads the file.
   - It asks Lean to read the question.
   - It runs the existing untrusted generators: the prover, the Rust countermodel search, and the norm-defaults flip search, generalised from one point to a whole sentence.
   - It asks Lean for the answer and prints Lean's text.

   There is no new trusted Python, and the relay lint covers `ve/ask.py` (D12).
9. **Nothing is duplicated** (section 5).
   - Speech acts' Python parsing of polar questions moves to the Lean reader (Q1.4).
   - Python's wording of situations and point clauses moves to `VE.Words` (Q2.4).
   - RD-3's fold and checkers, the certificate checker and Lean's document splitter are reused, not copied.
10. **Order.**
    - Q0, the statement spec and its review, comes first.
    - Then Q1.1, then Q1.2, then Q1.3 and Q1.4 in parallel.
    - Q2 starts once RD-3 has merged: Q2.1, Q2.2 and Q2.3 in turn, then Q2.4 and Q2.5 in parallel, then Q2.6.

    There are eleven batches of 2 to 6 hours each, about 47 to 59 builder hours in total. These are estimates, not evidence.

## 1. What exists today (read at `c85797de` unless marked)

| Piece | Where | What Q1 and Q2 take from it |
|---|---|---|
| English reader | `lean/VE/EnglishGrammar/Read.lean`:<br>- :38 `read (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : ReadOutcome`<br>- :50 `EnglishOneReading`<br>- :119 `read_ok`<br>- :136 `read_complete_english`<br>- :150 `read_stopped`<br>- :174 `english_reading_unique`<br>- :57 `checkRendering` and :194 `checked_rendering_exact` | Every candidate sentence goes through `read` unchanged. |
| No questions | - `EnglishGrammar/Token.lean:31` `terminators` lists only `.`.<br>- `Lexer.lean:195`: `?` is `BadCharacter`.<br>- `Lexicon.lean:284` `subjectFirst` (V3): every wording begins with `{0} `.<br>- No rule begins with *must*, *may*, *is* or *does*. | Q1 strips `?` before lexing. It puts a fronted word back in its sentence position. |
| Modal forms | - `Encode.lean:251` `modalForm` gives `{0} may <act>` and `{0} must <act>`.<br>- A modal predicate has no negative (V5, fixture lx11).<br>- "Alice may access legacy." reads as `pred "access" [alice, legacy]` (`ProfileExamples.lean:443`).<br>- There is no prohibition role (`Norms/Tree.lean:17`). | "Must …?" and "May …?" questions read as atoms of regulated predicates. |
| Diagnosis | - `EnglishGrammar/Diagnose.lean:146` `diagnose (E : Env) (L : Lexicon) (source : String) (toks : Array Spanned) : Option Diagnosis`: three texts and a byte span.<br>- `Advice.lean:66` `advice`. | The help for a question with no reading. |
| Speech-act questions | `ve/speech_english.py:150-191`:<br>- reads `Is it the case that …?`, `Is <Name> …?`, `Does it follow from these premises that …?` and which-questions;<br>- refuses `Must …` and `Can …` (`ModalQuestion`);<br>- is Python, an owned surface (`tools/relay_lint.py:61`). | Form F1 is reused. Its polar parsing moves to Lean (Q1.4). |
| A countermodel is not "no" | - `lean/VE/SpeechActs/Answer.lean:323` `countermodel_not_negative`: "A countermodel to P is evidence about that model only: it does not give ¬P over the premises".<br>- Argument edges distinguish `refuted` (a certificate for ¬C) from `gap` (a countermodel) (`ve/argument.py:412`). | D4. |
| Certificates | - `lean/VE/TableauChecker.lean:168` `checkCertificate` and :176 `checkCertificate_sound`.<br>- `lean/VE/Tableau.lean:28` `Certificate`. Its `premise_meaning_ids` field binds every premise in order. It does not list which premises were used. | Evidence for *yes* and *no*. Lean computes the used premises itself (D7). |
| Countermodels | - `lean/VE/Consequence.lean:46` `countermodelCheck` and :63 `countermodel_sound`.<br>- The search is Rust's only (`ve/search.py:283`). | Evidence for *not necessarily*. |
| Norm layers | - `lean/VE/Norms/Elaborate.lean:63` `elaborate T`: one premise per regulated predicate (`elabPremise T r`), over all of that predicate's rules.<br>- `Norms/Prefix.lean:39` `background`. | A cited layer premise is "the rules on one act" (D8). |
| UNDECIDED at a point | - `lean/VE/NormDefaults/Status.lean:310` `UndecidedAt`.<br>- `NormDefaults/Evidence.lean:90` `undecided_witness_sound`.<br>- The search flips cone atoms, starting from the canonical filling ([norm-defaults.md](norm-defaults.md) 2.5). | *The text does not settle this* lifts UNDECIDED from a point to a sentence. |
| RD-3, **unmerged** | `ve-rd-3/lean/VE/Readings/Verdicts.lean`:<br>- `ChoiceResult` :25 and `foldEntailment` :33;<br>- `CounterU` :56 and `ConsistentU` :62;<br>- `Holds` :67, `Covers` :77 and `RowsHold` :81;<br>- the fold theorems;<br>- `usedLabels` :650 and `usedLabels_sound` :662.<br><br>`VerdictsWire.lean`:<br>- `FilledModel` :85 and `NDEvidence` :92;<br>- `ndCertOk` :109 and `ndModelOk` :115;<br>- the rows :123-138, with soundness theorems :140-200;<br>- `gapsOf` :326;<br>- `NDVerdicts` :244 and `replayVerdictsND` :757;<br>- `readings_wire_verdicts_*` :763-812;<br>- `englishPlan` :567. | The rows per choice, the fold, the used labels and the filled models. |
| A document without content-bearing sets | `ve/document.py:1449-1503`: a content-bearing document goes to `readings_verdicts.context`; any other document goes to Python's `check_readings` (`ve/readings.py:483`), which folds in Python. | Q2.2's zero-set case. |
| Document splitter in Lean | - `lean/VE/Service/Document.lean:79` `split`; units and spans at :204 `sourceUnit` (lean-first 16a).<br>- Norm and fenced content are `CheckerUnavailable` there. | Quoting the bytes of a cited sentence. Only the splitter is used, not `check`. |
| Situation wording, in Python | - `ve/readings_s2_wording.py:105` `situation`.<br>- `ve/norm_defaults_english.py`: :141 `point_clause`, :199 `_negative_modal`, :304 `filling_sentence`.<br>- `ve/readings_s2_english.py:334` produces the filled-gap sentence a second time. | Moved to `VE.Words` (Q2.4). |
| CLI | - `ve/__main__.py`: prefix commands. `senses check` (:54-77) is the template for a Lean-only command.<br>- Exit codes 0 to 5 (:40-41). | `ve ask`. |

There is no `ask` command and no question form in the Lean grammar anywhere in the repository. The sentence "Is every member of the group a person?" and its vocabulary occur nowhere either, so its fixture (6.1) is written for this plan.

## 2. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | **Two forms, F1 and F2 (3.2).**<br>- A question that begins with another word gets advice: *does*, *do*, *can*, *will*, *should* and the like.<br>- *Who*, *what*, *which* and the other wh-words are Q3, and their advice says so. | 3.2, 3.3 |
| D2 | **No grammar change.**<br>- Candidate sentences are read by the existing `read`, and `?` never reaches the lexer.<br>- No `ve/english_grammar/LOCK.json` entry changes, and neither do `actions_version`, `grammar_id` or `lexicon_id`.<br>- Q1 lives in `lean/VE/Question/`, outside the lock. It has its own identity, `question_version`, with its own lock list `ve/question/LOCK.json`, as senses D17 does for `senses_version`. | 3.5, 4.8 |
| D3 | **Dependencies.** Q1 needs nothing unmerged. Q2 needs RD-3 merged, and reuses RD-3's rows, fold, `usedLabels` and filled-model checks without changing them. | 7 |
| D4 | **The leads (4.1).** "No." needs a certificate for ¬ψ. A countermodel alone gives "Not necessarily."<br><br>*Why:*<br>- VE's own theorem `countermodel_not_negative` says a countermodel is not a "no".<br>- Argument edges already separate `refuted` from `gap`.<br>- "No." followed by a countermodel has two readings for an untrained reader: "the document forbids it" and "the document does not guarantee it". That is the misreading the one-reading rule exists to prevent.<br><br>The brief's sentence "Here is a situation the document allows where it fails" is kept verbatim after "Not necessarily.". The reading evaluation (Q2.6) measures both wordings. The DRI may return to the brief's wording on that evidence (question 1). | 4.1, 4.6 |
| D5 | **Rephrasing help (3.4).**<br>- *Many meanings:* one F1 question per distinct meaning.<br>- *Indefinite subject:* the *every* and the *some* questions.<br>- *No reading:* the diagnosis and the advice. | 3.4 |
| D6 | **The read-back line is always first**: `You asked whether <asked sentence>.` It reads back with the question's reading (`asked_reads_back`). | 4.6 |
| D7 | **Used premises.**<br>- RD-3's `usedLabels`, with one label per premise position, over the replay of the accepted certificate.<br>- The cited sources are the sources of the used positions.<br>- No new greedy algorithm is written. | 4.3 |
| D8 | **Sources (4.3).** A source is one of:<br>- a sentence's asserted content;<br>- the rules on one regulated act (a layer premise);<br>- a definition sentence;<br>- the word list (`Background_base`);<br>- the pair premise ("whatever must be done may be done");<br>- `Fill_T`, the same premise at a gap.<br><br>A layer premise is cited as all of its rules, because one layer formula covers every rule on that act and the certificate cannot tell them apart. The deciding rule is a follow-up (question 3). | 4.3 |
| D9 | **Readings.**<br>- Rows are grouped by lead and cited sources.<br>- `relevantSets` is computed and then checked.<br>- A situation line names the full choice its model belongs to: RD-3's rule `plan_model_names_every_set`, and composition-s2 2.3 item 3. | 4.4 |
| D10 | **Lean owns the text.**<br>- `VE.Words` (Q2.3) writes element lines, fact lines, point clauses and the filled-gap sentence.<br>- Q2.4 moves Python's producers of the same lines onto `VE.Words` and deletes their wording logic, so there is one owner. | 4.5, 5 |
| D11 | **A reading's own sentence** comes from RD-3's `<reading>` slot text, which Python's renderer produces until E3, when the statement layer moves to Lean.<br>- Lean checks it by reading it back (`checkRendering`) when the candidate is an assertion.<br>- Otherwise the response marks it `unchecked`.<br>- A reading is never shown as a candidate id or as "reading 2". | 4.4, 4.9 |
| D12 | **Python is `ve/ask.py`:**<br>- the CLI, file reading and relaying;<br>- the existing untrusted generators;<br>- the norm-defaults flip search, generalised so that one generator serves both points and sentences. | 4.8, 5 |
| D13 | **Gates.**<br>- *Yes* and *No* need a checked premise model, so a document whose sentences cannot all be true answers nothing.<br>- Every lead except *unknown* needs CONFLICT-FREE, as RD-3's review gate A2 requires. | 4.1 |
| D14 | **Unused sentences.**<br>- Any answer other than *yes* or *no* lists the sentences VE did not use because they have no formal content: UNFORMALISED, LABELLED, or a reading set without content.<br>- A *yes* or *no* stays true when more premises are added, so it needs no such list. | 4.6 |
| D15 | **Sentence numbers are display numbers**, as composition.md 2.1's `<n>` defines them.<br>- The brief's "Sentence 26.1" needs a label on each unit, which is a wire change to `ve-document@1` (question 2).<br>- The UDHR's article numbers live only in the pilot's `units.json`. | 4.6 |
| D16 | **Two service modes**, `english.question` (Q1) and `ask` (Q2).<br>- Each is pinned by an `rfl` theorem and has a response shape.<br>- The manifest operations are `question.read` and `question.answer`, both `authority: lean-only`. | 4.8 |
| D17 | **Senses.**<br>- A question is read with the same lexicon the document's sentences are read with, which for a senses document is RD-8's projection.<br>- A word the projection leaves unresolved has no wording, so the question has no reading and gets the diagnosis.<br>- Rephrasings with glosses come later (question 7). | 3.2 |
| D18 | **Scope.** Q2 answers:<br>- documents that RD-3's enumerated route answers: `readings@1` with content on the norms chain, with or without `norm-defaults@0`;<br>- documents with no content-bearing reading set, which are treated as one choice (Q2.2).<br><br>The soft and rights chains, the superposed route, components (RD-4) and `--under` give *unknown*, with the route's own abstention text relayed. | 4.8 |
| D19 | **The statement review comes before any Lean** (PLAN-EXPAND2 rule 10). Astra and Fable must converge on PASS, which requires both reviewers to accept every statement as true under its hypotheses. | Q0 |

## 3. Q1: questions in English

### 3.1 Terms

| Term | Meaning |
|---|---|
| question | a text that ends with one `?` |
| form | F1 (`Is it the case that …?`) or F2 (a fronted *is*, *must* or *may*) |
| candidate | a sentence Lean builds from the question by its form (3.2), ending with `.` |
| asked sentence | the candidate the question is read as. It is shown in the answer's first line. |
| reading of a question | the one formula all the candidates with a derivation mean (3.5) |
| auxiliary | the fronted word: *is*, *must* or *may*, written capitalised at the start of the question |

### 3.2 The two forms

- **F1.** The question is `Is it the case that <body>?`. Its one candidate is `<body>.`.
  - F1 takes precedence: a question that begins with exactly the bytes `Is it the case that ` has no other candidate.
  - This is speech acts' existing polar form, so the same words mean the same thing everywhere in VE.
- **F2.** The question is `<Aux> <rest>?`, where `<Aux>` is `Is`, `Must` or `May`.
  - The rest is lexed with the reader's lexer, `lexSpans`.
  - For each token of the rest after its first, that is not punctuation and starts at byte `g`, the candidate is `rest[0, g) ++ aux ++ " " ++ rest[g, end) ++ "."`, with `aux` in lower case.
  - Candidates come left to right.
  - No other byte changes, and the user's other words keep their case.
  - A sentence-initial lower-case keyword such as *every* is accepted by the existing `kw` terminal, which "matches exactly, or the capitalised form when sentence-initial" (`Token.lean:73`).
- **Anything else is not a question.** That includes a text without a final `?`, a text with a second `?`, and a candidate that reads as more than one sentence.

| Question | Candidates (*derived*) | Expected |
|---|---|---|
| `Is every member of the group a person?` | `every is member …` (no derivation)<br>`every member is of …` (none)<br>`every member of is the group …` (none)<br>`every member of the is group …` (none)<br>`every member of the group is a person.` (one)<br>`every member of the group a is person.` (none) | one meaning |
| `Is it the case that every member of the group is a person?` | `every member of the group is a person.` | the same meaning as above (`caseThat_reads`) |
| `May "a27" be performed?` | `"a27" may be performed.` | `pred permitted [a27]` |
| `Must every person be given equal access to higher education on the basis of merit?` | `every person must be given equal access to … merit.` and other gaps (none) | `∀ person. equal_access_to_higher_education_required` |

### 3.3 Outcomes, codes and texts

Each refusal carries Lean's code, its class and Lean's text, as English refusals already do. New codes are rows of Lean's code table, `VE.Question.Run`; each existing code gets a question variant of its text.

| Outcome | Code; class | Text (draft, fixed by Q0) |
|---|---|---|
| one | — | `english.question` returns the asked sentence, the formula and the form. `ask` goes on to answer. |
| many meanings | `AmbiguousQuestion`; `AmbiguousDerivation` | `This question can be read in more than one way. Ask one of these instead:`, then one rephrasing per line |
| a candidate with two derivations | E2's `Ambiguous`; `AmbiguousDerivation` | E2's ambiguity text, with its witnesses, on the question's spans |
| indefinite subject | `IndefiniteQuestion`; `SyntaxError` | `VE cannot tell whether "a" here means every or some. Ask one of these instead:`, then the rephrasings |
| no reading | E2's `NoDerivation`; `SyntaxError` | E2.6's diagnosis of the closest candidate, mapped onto the question's bytes, then one advice line |
| advice: another first word | — | `VE answers questions that begin with "Is", "Must" or "May", or with "Is it the case that" followed by a sentence.` |
| advice: who, what, which and the other wh-words | — | `VE answers yes-or-no questions. It does not answer who, what or which questions yet.` |
| a conclusion marker in a candidate | `QuestionWithMarker`; `SyntaxError` | `A question cannot contain "therefore", "so", "hence" or "it follows that".` |
| a derivation refused (ill-typed, rejected) | E2's code and class | E2's text, in the question variant (`The question …` in place of `Sentence <n> …`) |
| not one question | `NotOneQuestion`; `SyntaxError` | `Write one question that ends with a question mark.` |
| lexical, or the vocabulary refused | E2's code and class | E2's text, on the question's bytes |
| budget | `ResourceLimit` | `VE stopped reading this question at its work limit.` |

**The closest candidate** is the one whose diagnosis span starts furthest to the right; ties go to the leftmost.

**Mapping spans back to the question:**
- *F1:* a span moves right by the length of the frame.
- *F2:* a span before the gap moves right by `len(Aux) + 1`, and a span after the reinserted word stays where it is. A span over the reinserted word maps onto the question's first word.

### 3.4 Rephrasing help

- **Two or more meanings.** For each distinct meaning, in candidate order, VE offers `Is it the case that <the first candidate with that meaning, without its ".">?`. By `caseThat_reads`, each offered question reads with exactly that meaning.
- **A candidate with two derivations.** No rephrasing is offered, because no Lean renderer exists. E2's ambiguity text is relayed with the question's spans.
- **An indefinite subject.** This applies when the body (after the frame or the auxiliary) begins with the token `a` or `an` and no candidate reads.
  - VE builds the two questions with `every` and with `some` in that token's place.
  - Those that read are offered, in that order.
  - If neither reads, VE gives the no-reading help.

  The indefinite article is genuinely two-way in English questions ("May a university charge fees?" usually means every university, but can mean some). VE never picks one silently.

### 3.5 Lean (Q1): `lean/VE/Question/Read.lean`

```lean
namespace VE.Question
open VE.EnglishGrammar

/-- The fronted words of F2, in lower case (3.2). Speech acts pass `["is"]` (Q1.4). -/
def auxiliaries : List String := ["is", "must", "may"]
/-- F1's frame. -/
def caseFrame : String := "Is it the case that "

inductive Form
  | caseThat
  | fronted (aux : String) (gap : Nat)   -- `gap`: the byte offset in the rest where the word goes back
  deriving DecidableEq, Repr

structure Candidate where
  form : Form
  sentence : String                      -- ends with "."
  deriving DecidableEq, Repr

/-- The candidates of `q`, in order (3.2): F1's one candidate when `q` begins with `caseFrame`, otherwise F2's, one
    per word-token start of the rest after its first token, left to right; `[]` when `q` is not one question. -/
def candidates (auxs : List String) (q : String) : List Candidate

/-- What one candidate gives. -/
inductive Got
  | none                         -- no derivation
  | one (φ : EFormula)           -- one derivation, a meaning, no conclusion mark
  | many                         -- two derivations
  | refused (o : ReadOutcome)    -- a derivation without a meaning, a mark, or more than one sentence
  | budget

def got (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (c : Candidate) : Got :=
  match read E O L b c.sentence with
  | .ok [(φ, false)] => .one φ
  | .stopped _ .noDerivation => .none
  | .stopped _ (.ambiguous _ _) => .many
  | .stopped _ .budget => .budget
  | o => .refused o

inductive Outcome
  | one (c : Candidate) (φ : EFormula)
  | many (c d : Candidate) (rephrasings : List String)   -- `d = c`: one candidate with two derivations
  | indefinite (rephrasings : List String)
  | none (closest : Option Candidate)
  | refused (c : Candidate) (o : ReadOutcome)
  | text (o : ReadOutcome)        -- the vocabulary (V6, V1 to V5) or a character refused, before any candidate
  | notQuestion
  | budget

/-- 3.3's order: the vocabulary policy (`Lexicon.policyOk`, as `admitRequest`), the question's shape, the lexing of
    its body, then the candidates: any budget, any candidate with two derivations, the meanings (one, or many),
    any refusal, else none with the indefinite help or the diagnosis. -/
def readQuestion (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Outcome

/-- A candidate sentence has no derivation in the document's grammar. -/
def NoDerivation (E : Env) (L : Lexicon) (s : String) : Prop :=
  ∀ ws, lex s = .ok ws → ∀ w ∈ ws.toList, ∀ t,
    ¬ VE.Grammar.Derives (grammar E L) (.n (grammar E L).start) w.toList t

/-- One reading (3.5): `c` is the first candidate with a meaning, its meaning is `φ`, and every other candidate either
    has no derivation or has exactly one, meaning `φ`. -/
def QuestionOneReading (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (q : String)
    (c : Candidate) (φ : EFormula) : Prop :=
  c ∈ candidates auxs q ∧ EnglishOneReading E O L c.sentence [(φ, false)] ∧
  (∀ d ∈ candidates auxs q, EnglishOneReading E O L d.sentence [(φ, false)] ∨ NoDerivation E L d.sentence) ∧
  (∀ d ∈ (candidates auxs q).takeWhile (· ≠ c), NoDerivation E L d.sentence)

theorem readQuestion_one {auxs E O L b q c φ} (h : readQuestion auxs E O L b q = .one c φ) :
    QuestionOneReading auxs E O L q c φ
/-- Completeness, under the reader's own hypotheses (`read_complete_english`'s) and no candidate at its budget. -/
theorem readQuestion_complete {auxs E O L b q c φ} (hp : L.policyOk E O = true)
    (hg : (grammar E L).wf = true ∧ terminatorFree (grammar E L) = true ∧
      (grammar E L).typed sig (ty E L) (acts E L) = true ∧ ty E L (grammar E L).start = .sentence)
    (hb : ∀ d ∈ candidates auxs q, ∀ i, read E O L b d.sentence ≠ .stopped i .budget)
    (h : QuestionOneReading auxs E O L q c φ) : readQuestion auxs E O L b q = .one c φ
theorem question_reading_unique {auxs E O L q c c' φ φ'} (h₁ : QuestionOneReading auxs E O L q c φ)
    (h₂ : QuestionOneReading auxs E O L q c' φ') : c = c' ∧ φ = φ'

/-! ## The round trip -/

/-- The sentence VE shows as the question it read reads back with exactly the question's reading. -/
theorem asked_reads_back {auxs E O L b q c φ} (h : readQuestion auxs E O L b q = .one c φ) :
    checkRendering E O L b [(φ, false)] c.sentence = true
/-- F1: "Is it the case that S?" reads exactly as the sentence S. -/
theorem caseThat_reads (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (t : String)
    (φ : EFormula) (hp : L.policyOk E O = true) (ht : '?' ∉ t.toList) :
    readQuestion auxs E O L b (caseFrame ++ t ++ "?") = .one ⟨.caseThat, t ++ "."⟩ φ ↔
      read E O L b (t ++ ".") = .ok [(φ, false)]
/-- F2: a candidate is its question with the fronted word put back in the rest. -/
theorem fronted_text {auxs q a g s} (h : (⟨.fronted a g, s⟩ : Candidate) ∈ candidates auxs q) :
    a ∈ auxs ∧ ∃ rest, q = capitalized a ++ " " ++ rest ++ "?" ∧ g ∈ gaps rest ∧
      s = (rest.extract 0 ⟨g⟩) ++ a ++ " " ++ (rest.extract ⟨g⟩ rest.endPos) ++ "."
/-- Every rephrasing VE offers is a question it reads with one meaning, and two offered rephrasings mean different
    things. -/
theorem rephrasings_read {auxs E O L b q c d rs} (hp : L.policyOk E O = true)
    (h : readQuestion auxs E O L b q = .many c d rs ∨ readQuestion auxs E O L b q = .indefinite rs) :
    (∀ r ∈ rs, ∃ c' φ', readQuestion auxs E O L b r = .one c' φ') ∧
    rs.Pairwise (fun r r' => ∀ c₁ φ₁ c₂ φ₂, readQuestion auxs E O L b r = .one c₁ φ₁ →
      readQuestion auxs E O L b r' = .one c₂ φ₂ → φ₁ ≠ φ₂)
end VE.Question
```

**Notes for the stub.**
- `gaps`, `capitalized` and the `String.extract` positions are fixed by the stub.
- `readQuestion_one` follows from `read_ok` and from `read_stopped` together with the generic `read_sound` and `read_complete` (`VE/Grammar/Reading.lean`:80 and :97); the step from `.stopped _ .noDerivation` to `NoDerivation` is a lemma of Q1.1.
- `caseThat_reads` holds because F1 has exactly one candidate.
- The mode's case and response are in 4.8.

### 3.6 Limits (Lean-owned, `VE.Question`)

| Limit | Value | Reason |
|---|---|---|
| Question bytes | 4,096 | far above any corpus sentence. Longer is `ResourceLimit`. |
| Tokens | 300 | E2's design point (DRI ruling R5) |
| Candidates | 64 | an F2 question with more is `ResourceLimit` |
| Work per candidate | E2's budget, 2,100,000 steps | each candidate is one `read` |
| Latency, measured in Q1.3 and a pass gate | p95 ≤ 100 ms for a corpus question; ≤ 1 s at 64 candidates | `read` is at most 20 ms p95 per sentence (GE2 item 9). Viability pruning is not on the trusted path unless proved (question 5). |

## 4. Q2: answers in English, with reasons

### 4.1 The leads

ψ is the question's formula, as a `VE.Formula`: `VE.Bridge.decodeFormula (φ.encode)`. U is the choice's filled document and Γ its assertions (RD-3's `choiceU N c` and `(choiceDoc N.D c).2`).

| Lead | Checked evidence under the choice | What it means (4.7) | Lead sentence |
|---|---|---|---|
| yes | CONFLICT-FREE; a checked premise model; an accepted certificate for ψ | ψ holds in every situation the document allows | `Yes.` |
| no | CONFLICT-FREE; a checked premise model; an accepted certificate for ¬ψ | ψ fails in every situation the document allows | `No. The document rules this out.` |
| notSettled | CONFLICT-FREE; one base model with two fillings, both checked (`ndModelOk`), with ψ true under one and false under the other | in one situation the answer turns on points the text leaves unsaid (`SplitU`) | `The text does not settle this.` |
| notNecessarily | CONFLICT-FREE; a checked countermodel (`ndModelOk … false`) | ψ fails in some situation the document allows (`CounterU`) | `Not necessarily.` |
| unknown | anything else | nothing is claimed beyond the reason | `VE could not decide this.` and one reason sentence (4.6) |

**Priority.** When several pieces of evidence are checked, the lead is the first that applies in this order: yes, no, notSettled, notNecessarily, unknown.
- An accepted proof for ψ excludes a checked model with ψ false, because the document is CONFLICT-FREE (`no_certificate_countermodel_conflict`, `Consequence.lean:73`).
- A countermodel whose failure depends on no gap (`gapsOf = []`) is *Not necessarily*, and no flip is sought.
- A countermodel that depends on gaps is passed to the flip search. If the flip is checked, the lead is *notSettled*. If it is not, the lead stays *Not necessarily*, and the existing filled-gap sentence is shown: "Here the text does not say whether …; this situation answers 'no'.".

The search is untrusted and its order is Python's. Every lead Lean gives rests only on checked evidence.

### 4.2 Rows, and agreement with the existing verdict

There is one row per compatible choice, exactly RD-3's rows (`NDVerdicts.evs`):
- a conflict row and a premise row, from RD-3;
- a query row for ψ, from RD-3;
- a negation row: RD-3's `ndCertOk` with `.not ψ`;
- a split flag: two `ndModelOk` checks on one `FilledModel`'s base.

The lead of a row is a function of these alone (`Row.lead`, 4.7). The answer is proved never to contradict the existing per-choice result:
- *Yes* only where RD-3's query row is `proved`.
- No negative lead where it is `proved`.
- Every choice *yes* is exactly RD-3's ALL, when every choice has a premise model.

For a document with no content-bearing reading set, the rows have one choice, `[]` (Q2.2). Agreement with Python's W2 fold on those documents is measured in Q2.6.

### 4.3 Reasons: exactly the premises of the certificate

1. **The premises.** For a *yes* or *no* row, the premises are RD-3's `premisesU (choiceU N c) Γ`: Background, then `Fill_T`, then the layers, then the assertions, in that function's order, which the stub reads. `sourcesU` maps each position to its source:

   | Source | Premise | Cited as |
   |---|---|---|
   | `unit u` | an asserted formula of unit `u`, or of the chosen reading of `u` | `Sentence <n> says: "<the unit's bytes>"` |
   | `rules p us` | the layer premise of regulated predicate `p`, `elabPremise T p` over all its rules | at most three rules: one quote per rule's unit. More than three: `Sentences <citation> say when <generic clause>.` |
   | `definition u` | a W3 biconditional | as `unit u` |
   | `background` | `Background_base`: sorts, constants, data flags and attribute laws | `VE also used what the document's word list declares.` |
   | `pair r m` and `fill r m` | the pair premise, or `Fill_T` at a gap | `VE also used its rule that whatever must be done may be done: <pair sentence>` |

2. **The used positions** are RD-3's `usedLabels`, labelling each premise by its position, over the certificate's replay. The replay is the binding-free trace replay that RD-3's caller uses; the meaning-id binding is checked once, on the full list. A position is dropped when the certificate still replays with that premise replaced by `⊤`.
   - `usedPositions_sufficient`: the used premises alone entail ψ (or ¬ψ for *no*).
   - `render_cites_exact`: the text cites exactly the sources of the used positions, once each, in order.

   Nothing claims the cited set is minimal, because the greedy order decides which of two interchangeable premises is kept.
3. **Quotes.** A cited unit's text is the document's own bytes in that unit's span, as Lean's `VE.Service.Document.split` reads them, without leading or trailing white space. For a fenced unit, the text is the fence's sentence. Lean checks that the readings case it received is this document's: every unit's `content` and every reading set's entries in the case must equal the front matter's, as canonical JSON. Otherwise the answer is `CheckerUnavailable: the case is not this document's`.

### 4.4 Readings

- **Rows** are RD-3's compatible choices, at most 64. Beyond 64, the answer is *unknown*, and its reason says how many ways of reading exist.
- **Groups.** The key of a row is `(lead, cited)` for *yes* and *no*, and `lead` otherwise. `relevantSets` is computed greedily: it drops a set whenever every two rows that agree on the remaining sets have the same key. It is then checked over all the rows; if the check fails, it returns every set. `relevantSets_sound` proves the property.
- **Text.**
  - When there is one group and the document has open sets, the text is the lead and its reasons, then `Every way of reading the document gives this answer.`
  - Otherwise there is one block per group: `If sentence <n> means "<reading>"[ and sentence <m> means "<reading>"], <lead phrase>.`, then that group's reasons.
- **Situations.** A shown situation belongs to one choice. When the document has open sets, its line adds `, reading sentence <n> as "<reading>"` for **every** open set. A model is one reading, so naming fewer sentences would claim the result for readings the model does not show (composition-s2 2.3 item 3).
- **Reading names** come from RD-3's `<reading>` slot, rendered by Python's `reading_names` and sent in the request (D11).
  - An asserted candidate's name is checked with `checkRendering` against the candidate's formula.
  - A norm candidate's name cannot be checked until E3 and is listed in the response as `unchecked_names`.
  - A name that fails its check is not shown. The block then says `If sentence <n> is read the <k>-th way VE lists, …`, and the response lists the failure.

### 4.5 Words: situations and clauses, with one owner

`lean/VE/Words/Situation.lean` (namespace `VE.Words`) fills templates from the request's validated lexicon, which is the same selection Python's renderers read today. It produces:

| Function | Text | Python producer it replaces in Q2.4 |
|---|---|---|
| `elementLine` | `<name> is a/an <noun>`. The article follows the noun's first letter. | `readings_s2_wording.py:115-116` |
| `factLine` | a true base atom by its wording, with the element names in its holes | `readings_s2_wording.py:118-121` |
| `pointClause` | `<subject> may/must <act>` at a tuple, or `must not` / `need not` (`modalForm`); a plain predicate's wording | `norm_defaults_english.py:141` `point_clause`, :199 `_negative_modal` |
| `fillingSentence` | `Here the text does not say whether <clause>; this situation answers 'yes'.` (or `'no'`) | `norm_defaults_english.py:304` `filling_sentence`; `readings_s2_english.py:334` |
| `situation` | the elements by sort, then the true author atoms, sorted as Python sorts them, joined by `; `. `nothing exists` when empty. | the base part of `readings_s2_wording.py:105` `situation` |
| `genericClause` | `a/an <noun> may/must <act>`, each hole filled with an indefinite noun phrase (for 4.3's `rules` line) | new |
| `pairSentence` | `Whenever a <noun> must <act>, it may <act>.` (norm-defaults 4.1) | the Python producer of that sentence, found and listed by Q0 |

An element's name follows Python's `element_name`: the spelling of a constant that denotes the element, else the element's id.

The soft and rights suppositions (`suppose …`, `readings_s2_wording.py:124-134`) stay in Python. Q2 does not answer on those chains (D18). They move to `VE.Words` with the batch that brings those chains into Q2's scope.

### 4.6 The answer's sentences (one reading each)

These are sentences VE says. None of them can be written by an author as document content.

Each sentence has one derivation because it begins with a fixed lead that no other registered production begins with, and its slots are closed classes. Each goes through W7's all-derivations gate before it is shown (composition.md 2), with its new rows registered by Q2.3.

| # | Wording | The one reading |
|---|---|---|
| A0 | `You asked whether <asked sentence without its final ".">.` | VE read the question as this sentence, and the answer below is about this sentence. |
| A1 | `Yes.` | In every situation the document allows (under the named readings), the asked sentence is true. |
| A2 | `No. The document rules this out.` | In every situation the document allows, the asked sentence is false. |
| A3 | `The text does not settle this.` | There is a situation the document allows in which the answer depends on points the text leaves unsaid. |
| A4 | `Not necessarily.` | There is a situation the document allows in which the asked sentence is false. Nothing more is claimed. |
| A5 | `VE could not decide this.` | No verdict. The next sentence gives the reason. |
| C1 | `Sentence <n> says: "<bytes>"` | Sentence n of the document is one of the premises the answer uses, and these are its exact words. |
| C2 | `Sentences <citation> say when <generic clause>.` | Together these sentences are the rules that decide the act, and the answer uses them. |
| C3 | `VE also used what the document's word list declares.` | A declaration of the document's vocabulary (a sort, constant, flag or attribute law) is used. |
| C4 | `VE also used its rule that whatever must be done may be done: <pair sentence>` | The pair premise, or `Fill_T` at a gap, is used. |
| S1 | `Here is a situation the document allows where it fails: <situation>[, reading <readings>].` | A checked countermodel, under the named choice. This is the brief's sentence, unchanged. |
| S2 | `Here is a situation where the answer depends on what the text leaves unsaid: <situation>[, reading <readings>].` then one `The text does not say whether <clause>.` per point where the two fillings differ | A checked split: the situation's base, and the gap points that differ. |
| S3 | `Here the text does not say whether <clause>; this situation answers 'no'.` | norm-defaults 3.2's filled-gap sentence after S1, one per gap the failure depends on (`gapsOf`). |
| R1 | `If sentence <n> means "<reading>"[ and sentence <m> means "<reading>"], <lead phrase>.` | The lead holds under every compatible choice that reads the named sentences this way. |
| R2 | `Every way of reading the document gives this answer.` | Every compatible choice has the same lead (and the same cited sentences, for yes and no). |
| U1 | `VE did not use <k> sentences of this document that it could not read formally: <citation>.` | Those units have no formal content, and the answer is about the other sentences only. |
| X1 | `Two rules contradict each other in this situation, so VE cannot answer: <situation>.` | Reason after A5: a checked conflict witness under this choice. |
| X2 | `VE could not check that the rules never contradict each other.` | Reason after A5: the conflict row is unknown. |
| X3 | `The sentences of this document cannot all be true together, so VE does not answer questions about it.` | Reason after A5: a certificate of ⊥ under this choice. |
| X4 | `VE found neither a proof nor a situation where it fails, within its limits.` | Reason after A5: no row result. |
| X5 | `There are more than 64 ways to read this document's open sentences. VE did not check them all.` | Reason after A5: the enumeration budget. |

The lead phrases inside R1 are: `yes`, `no: the document rules this out`, `the text does not settle this`, `not necessarily` and `VE could not decide this`.

**Never shown:**
- a unit id, a set id, a candidate id or `reading <i>`;
- an `unsaid__` name, a `ve__` name or a generated predicate;
- "No." in front of a countermodel;
- A1 or A2 without a premise model;
- R2 when any choice is unchecked;
- a situation that names fewer open sets than the choice its model belongs to.

**A worked example (*derived*, fixture U3)** on the UDHR part 7 document:

```text
You asked whether every person must be spared exclusion from education.
If sentence 10 means "Every person must be spared exclusion from education", yes. Sentence 10 says: "1. Everyone has the right to education."
If sentence 10 means "<the entitlement reading's sentence>", the text does not settle this. Here is a situation where the answer depends on what the text leaves unsaid: <situation>, reading sentence 1 as "<…>" and sentence 10 as "<…>". The text does not say whether <element> must be spared exclusion from education.
VE did not use 9 sentences of this document that it could not read formally: sentences 3, 5, 6, 7, 8, 11, 17, 18 and 19.
```

### 4.7 Lean (Q2): `lean/VE/Ask/`

The names from `VE.Readings`, `VE.Readings.Wire`, `VE.NormDefaults` and `VE.Norms` are read on the RD-3 branch and on `main`. Q0 elaborates them against RD-3's merged build.

```lean
namespace VE.Ask
open VE.Readings VE.NormDefaults
open VE.Norms (Sat restrictAll DocumentExpansion)
universe u

inductive Lead | yes | no | notSettled | notNecessarily | unknown
  deriving DecidableEq, Repr

/-- What Lean checked for the question's formula under one compatible choice (4.2). -/
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

/-- The text does not settle ψ: one base situation, two admissible fillings of its gaps, the premises true in both
    expansions, ψ true in the first and false in the second (norm-defaults 2.5's `UndecidedAt`, for a closed formula). -/
def SplitU (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) : Prop :=
  ∃ (B : VE.Structure.{0}) (F₁ F₂ : FillTables U B) (S₁ S₂ : VE.Structure.{0}),
    restrictAll (fill U).T S₁ = withFill U B F₁ ∧ restrictAll (fill U).T S₂ = withFill U B F₂ ∧
    BaseAdmissibleU U (withFill U B F₁) ∧ BaseAdmissibleU U (withFill U B F₂) ∧
    DocumentExpansion (fill U) (withFill U B F₁) S₁ ∧ DocumentExpansion (fill U) (withFill U B F₂) S₂ ∧
    Sat S₁ Γ ∧ Sat S₂ Γ ∧ ψ.denote S₁ [] ∧ ¬ ψ.denote S₂ []

/-- What a row's lead says of its choice. -/
def LeadHolds (N : NDoc) (ψ : VE.Formula) (r : Row) : Prop :=
  let U := choiceU N r.choice
  let Γ := (choiceDoc N.D r.choice).2
  match r.lead with
  | .yes => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ ψ
  | .no => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ (.not ψ)
  | .notSettled => ConflictFreeU.{u} U ∧ SplitU U Γ ψ
  | .notNecessarily => ConflictFreeU.{u} U ∧ CounterU U Γ ψ
  | .unknown => True

/-- The row's hypotheses: each component holds of its choice, as RD-3's rows do (`nd*Row_holds`). -/
def RowOk (N : NDoc) (ψ : VE.Formula) (r : Row) : Prop :=
  Holds.{u} N [] .bottom r.choice r.conflict ∧ Holds.{u} N [] .bottom r.choice r.premise ∧
  Holds.{u} N [] ψ r.choice r.query ∧ Holds.{u} N [] (.not ψ) r.choice r.negation ∧
  (r.split = true → SplitU (choiceU N r.choice) (choiceDoc N.D r.choice).2 ψ)

theorem lead_sound (N : NDoc) (ψ : VE.Formula) (r : Row) (h : RowOk.{u} N ψ r) : LeadHolds.{u} N ψ r
theorem split_counter {U : UDoc} {Γ : List VE.Formula} {ψ : VE.Formula} (h : SplitU U Γ ψ) : CounterU U Γ ψ
/-- The split check: one checked base model, two checked fillings with opposite values of ψ. -/
theorem splitOk_sound {N : NDoc} {c : Choice} (e : VE.Readings.Wire.NDEvidence N c) (ψ : VE.Formula)
    (m₁ m₂ : VE.Readings.Wire.FilledModel (choiceU N c)) (hM : m₁.M = m₂.M)
    (h₁ : VE.Readings.Wire.ndModelOk N c [] ψ m₁ true = true)
    (h₂ : VE.Readings.Wire.ndModelOk N c [] ψ m₂ false = true) :
    SplitU (choiceU N c) (choiceDoc N.D c).2 ψ

/-! ## Agreement with the existing verdict (RD-3's fold) -/

def conflictRows (rs : List Row) : List (Choice × ChoiceResult) := rs.map fun r => (r.choice, r.conflict)
def queryRows (rs : List Row) : List (Choice × ChoiceResult) := rs.map fun r => (r.choice, r.query)

theorem lead_agrees (r : Row) :
    (r.lead = .yes → r.query = .proved) ∧
    (r.lead = .no ∨ r.lead = .notSettled ∨ r.lead = .notNecessarily → r.query ≠ .proved)
theorem all_yes_iff_fold (rs : List Row) (hne : rs ≠ []) (hm : ∀ r ∈ rs, r.premise = .model) :
    (∀ r ∈ rs, r.lead = .yes) ↔ foldEntailment (conflictRows rs) (queryRows rs) = .all

/-! ## Reasons (4.3) -/

inductive Source
  | unit (id : String) | rules (pred : String) (units : List String) | definition (id : String)
  | background | pair (r m : String) | fill (r m : String)
  deriving DecidableEq, Repr

/-- Where each premise comes from, position by position, in `premisesU`'s order. -/
def sourcesU (U : UDoc) (assertions : List (Source × VE.Formula)) : List Source
theorem sourcesU_length (U : UDoc) (assertions : List (Source × VE.Formula)) :
    (sourcesU U assertions).length = (VE.NormDefaults.Wire.premisesU U (assertions.map (·.2))).length

/-- The positions the certificate needs: RD-3's `usedLabels`, one label per position (its numeral), over the replay
    that `checkCertificate` runs after its binding check (`replayOk`; the stub names it). -/
def usedPositions (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate) :
    List Nat :=
  (usedLabels (fun Q => replayOk E Q ψ k) [] (((List.range P.length).zip P).map fun (i, f) => (toString i, f)) []).filterMap
    String.toNat?
theorem usedPositions_sufficient (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula)
    (k : VE.Tableau.Certificate) (h : replayOk E P ψ k = true) :
    VE.Entails.{u} E ((usedPositions E P ψ k).filterMap (P[·]?)) ψ
def cited (srcs : List Source) (used : List Nat) : List Source := (used.filterMap (srcs[·]?)).eraseDups

/-! ## Readings (4.4) -/

def relevantSets (D : Doc) (rows : List Row) (key : Row → Lead × List Source) : List String
theorem relevantSets_sound (D : Doc) (rows : List Row) (key : Row → Lead × List Source) :
    ∀ r ∈ rows, ∀ r' ∈ rows,
      (∀ s ∈ relevantSets D rows key, r.choice.lookup s = r'.choice.lookup s) → key r = key r'

/-! ## The text (4.6) -/

structure Line where
  frame : String                         -- A0 … X5
  text : String
  source : Option Source := none         -- C1 to C4
  quote : Option (String × String) := none   -- (unit id, the unit's bytes)
  readings : List (String × Nat) := []   -- R1, S1, S2: the candidates named, in source order

structure Answer where
  asked : VE.Question.Candidate
  rows : List Row
  cites : Row → List Source              -- `cited (sourcesU …) (usedPositions …)` of the row's accepted certificate
  sets : List String                     -- `relevantSets`

/-- Every quoted sentence is the document's own bytes for that unit, trimmed (`Context.textOf` reads `Document.split`). -/
theorem render_quotes_bytes (ctx : Context) (a : Answer) :
    ∀ l ∈ render ctx a, ∀ u t, l.quote = some (u, t) → ctx.textOf u = some t
/-- The first line is A0 over the asked sentence. -/
theorem render_asked (ctx : Context) (a : Answer) :
    (render ctx a).head? = some (askedLine a.asked.sentence)
/-- The source lines of a yes or no group are exactly its rows' cited sources, once each, in order. -/
theorem render_cites_exact (ctx : Context) (a : Answer) (g : Group) (hg : g ∈ groups a)
    (hl : g.lead = .yes ∨ g.lead = .no) :
    (renderGroup ctx a g).filterMap (·.source) = a.cites g.first
/-- Each group's first sentence is its lead's (A1 to A5, or R1 with the lead phrase). -/
theorem render_lead (ctx : Context) (a : Answer) (g : Group) (hg : g ∈ groups a) :
    leadOfLine ((renderGroup ctx a g).head?) = some g.lead
/-- A situation line names every open set's candidate of its model's choice (RD-3's `plan_model_names_every_set`). -/
theorem render_model_names_choice (ctx : Context) (a : Answer) :
    ∀ l ∈ render ctx a, l.frame ∈ ["S1", "S2", "X1"] → l.readings.map (·.1) = ctx.D.sets.map (·.id)

/-! ## The wire (4.8) -/

/-- A replayed `ask` case: the question read by Lean itself (the request's formula is not trusted), RD-3's replayed
    case with ψ as its conclusion and nothing assumed, and one row per replayed choice. -/
structure Asked where
  q : String
  c : VE.Question.Candidate
  φ : VE.EnglishGrammar.EFormula
  ψ : VE.Formula
  x : VE.Readings.Wire.NDVerdicts
  rows : List Row
  hread : VE.Question.QuestionOneReading VE.Question.auxiliaries x.E x.O x.L q c φ   -- the stub binds E, O, L
  hψ : VE.Bridge.decodeFormula φ.encode = .ok ψ
  hx : x.φ = ψ ∧ x.Γ = [] ∧ x.A = []
  hrows : rows.map (·.choice) = x.evs.map (·.1)
  hok : ∀ r ∈ rows, RowOk.{0} x.r.N ψ r

def replayAsk (j : Lean.Json) : Except String Asked
theorem ask_wire_sound (j : Lean.Json) (a : Asked) (h : replayAsk j = .ok a) :
    (∀ r ∈ a.rows, LeadHolds.{0} a.x.r.N a.ψ r) ∧
    (∀ c, Compatible a.x.r.N.D c ↔ c ∈ a.rows.map (·.choice))
end VE.Ask
```

**`VE.Words`** (4.5) has no correctness theorem beyond its `#guard` fixtures. Its functions fill templates from a lexicon that V1 to V6 validated. Q2.4's A/B shows they produce Python's bytes. Situation lines are not read back: element names are not lexicon constants, and Python's lines are not read back today either. The share of shown lines that read back is measured instead (8).

**The zero-set case (Q2.2).** For a document with no content-bearing reading set, Q0 establishes from the stub whether RD-3's admission `admitNDFullJ` and `replayVerdictsND` accept zero sets. Then `choices D = [[]]` and `choiceU N []` is the document itself.
- If they do, Q2.2 only states `choiceU_nil`.
- If they do not, Q2.2 extends the admission to zero sets, with a conservativity theorem: every document with a set is admitted as before.

For a document without norms (`relational-fol@0` only), Q0 decides between two routes:
- the same route, with an empty rule tree; or
- a plain adapter over `checkCertificate_sound` and `countermodel_sound`, in which `LeadHolds` reads `VE.Entails` and a finite model.

The second adds one `LeadHoldsPlain` with the same five cases and no `SplitU`, since such a document has no gaps.

### 4.8 Wire, service modes and the CLI

- **`english.question`** (Q1.2): `lean/VE/Question/Run.lean`; `Mode.englishQuestion`; `runMode_englishQuestion : runMode .englishQuestion j = VE.Question.Run.caseReported j := rfl`.
  - *Case:* `english.read`'s case fields (`id`, `environment`, `lexicon`, `overlay?`, `generated?`, `cap`) plus `question`, decoded by `VE.EnglishGrammar.Run`'s own decoder, which is imported and not copied.
  - *Result:* `status` (`one`, `many`, `indefinite`, `none`, `refused`, `notQuestion`, `budget`, `invalidGrammar`) together with:
    - `form`, `sentence`, `ast` (the `EFormula` wire) and `spans`;
    - `code`, `class`, `text`, `span`, `advice` and `rephrasings`;
    - `identities`: E2's six (`source_sha256` over the question) plus `question_version`.
- **`ask`** (Q2.2): `lean/VE/Ask/Run.lean`; `Mode.ask`; `runMode_ask … := rfl`.
  - *Case:*
    - `document`: the text;
    - `question`;
    - the English fields (as above);
    - `case`: the `readings-verdicts` case Python's readings relay builds for this document, with `conclusion` set to the formula `english.question` returned. Lean re-reads the question and refuses a case whose conclusion differs.
    - `evidence`: RD-3's per-choice evidence, plus `negation` (a certificate) and `split` (a model with two fillings) per choice;
    - `names`: `{set, index, text}` for each candidate, from RD-3's `<reading>` slot.
  - *Result:* the Q1 result, plus:
    - `rows`: `choice`, `lead`, `cited` and `shown`;
    - `lead`: the uniform lead, or `by_reading`;
    - `text`: the lines;
    - `unused`;
    - `unchecked_names`;
    - `identities`: the Q1 identities plus the case's `document_id` and RD-3's identities.
- **Shapes and registration.** Each mode has a schema in `ResponseShape/Schemas/`, a skeleton row and a branch of `runMode_fits`. Each also has the `Protocol.lean` entries, `ve/backends/service_schema.py` `MODES`, a `lean_service.py` `DEADLINES` entry, `lean/checkers.lock`, the generated JSON schema and the `VE/Audit.lean` lines (the recipe of commit 8b18d286).
- **CLI.** The command is `ve ask DOCUMENT QUESTION [--json]`, wired in `ve/__main__.py` as a prefix command like `senses check`.
  - It prints Lean's `text` lines, nothing else. `--json` prints Lean's whole result, with the honesty fields `ve senses check` prints.
  - Exit codes:

    | Code | When |
    |---|---|
    | 0 | a lead other than unknown, or `by_reading` |
    | 3 | unknown |
    | 2 | the question is not read (Lean's code, class and text are printed) |
    | 4 | `ResourceLimit` |
    | 5 | `CheckerUnavailable` |

### 4.9 What an answer does not claim

- An answer is about the document's **formal content** only. Sentences VE could not read formally are not used, and U1 lists them.
- *Yes* is about every situation the document allows. It says nothing about the world, nor about what the author intended.
- *Not necessarily* does not say the document makes the sentence false anywhere.
- *The text does not settle this* says the answer turns on unsaid points in one allowed situation. It does not say the text is silent in every situation.
- Cited sentences are sufficient, not minimal. A cited group of rules on one act (C2) is cited as a whole, not by the rule that decides.
- A reading's own sentence for a norm candidate is Python's rendering, unchecked until E3, and the response marks it.
- A question VE reads may be odd English. Fronting a word inside a relative clause can make a candidate read (fixture G11). The A0 line shows the sentence actually checked. Q1.3 measures how often this happens.
- No claim about readers is made before Q2.6. Zero-training readability is a target, and proxy readers give an upper bound.

## 5. One owner per piece of logic; what is deleted, not duplicated

| Logic | Owner after this plan | Python | Batch |
|---|---|---|---|
| Question forms, candidates, the one-reading rule, rephrasings, question texts and codes | Lean `VE.Question` | relays | Q1.1, Q1.2 |
| Reading each candidate | the existing `VE.EnglishGrammar.read` (unchanged) | — | — |
| Speech acts' polar questions (`Is it the case that …?`, `Is <Name> …?`) and their `ModalQuestion` refusal | Lean `VE.Question` with `auxs := ["is"]`; the refusal text moves to Lean | `speech_english.py`'s polar branches (`:169-175`), the polar use of `_copular` and the `Must`/`Can` refusal (`:187-188`) are **deleted**; Python relays. `_copular` stays for which-questions and `follows` (Q3) and is listed in the ledger | Q1.4 |
| Per-choice checks, the fold, `usedLabels`, filled models | RD-3, reused | — | — |
| Leads, the split check, groups, relevant sets, cited sources | Lean `VE.Ask` | — | Q2.1, Q2.2 |
| Answer text, frames, quotes | Lean `VE.Ask.Render` | prints | Q2.3 |
| Situation lines, point clauses, filled-gap sentence, pair sentence | Lean `VE.Words` | `readings_s2_wording.situation`'s base part, `norm_defaults_english.point_clause`, `_negative_modal`, `filling_sentence`, `readings_s2_english` `gap_sentences` and the pair-sentence producer are **deleted** and replaced by relays of Lean's lines. The frames around them (`status_sentence` and the others) stay Python's until their own move and are listed | Q2.4 |
| Splitting the document, unit spans | Lean `VE.Service.Document.split`, reused | — | — |
| A reading's own sentence | Python's renderer (`reading_names`, RD-3's slot) until E3; Lean checks asserted ones | unchanged | — |
| Evidence: proofs, countermodels, premise models, flips | untrusted generators, Python and Rust (lean-first rule 3) | the existing generators. The norm-defaults flip search (`ve/norm_defaults.py` `_point_statuses` and its UNDECIDED witness search) is **generalised** to a target formula, and the point search calls it, so there is one generator | Q2.5 |
| CLI, files, display | Python `ve/ask.py`, added to `tools/relay_lint.py` `RELAYED` and mapped to layer 4 in `tools/layer_policy.py` | — | Q1.2, Q2.5 |

Each batch's `LEDGER.md` lists every Python site it deletes or turns into a relay, with the Lean definition that owns it.

## 6. Fixtures

All expected values are *derived*. Q0 computes them, with the stub for the Lean side and by running the generators for evidence. Display numbers are unit positions.

### 6.1 G: the group document (written for this plan; `usecases/question-answering/group.ve.md`)

- **Profiles:** `documents@1`, `relational-fol@0`.
- **Sort:** `member`, noun "member of the group", plural "members of the group".
- **Predicates:**
  - `citizen(member)` with wording "{0} is a citizen";
  - `person(member)` with wording "{0} is a person";
  - `adult(member)` with wording "{0} is an adult".
- **Constants:** `ann` ("Ann") and `bo` ("Bo").
- **Sentences** (English fences):
  1. "Every member of the group is a citizen."
  2. "Every member of the group who is a citizen is a person."
  3. "Ann is an adult."

  If the stub finds a sentence without a reading, Q0 rewrites the fixture, not the grammar.

| # | Question | Q1 (*derived*) | Q2 (*derived*) |
|---|---|---|---|
| G1 | `Is every member of the group a person?` | one, F2; asked "every member of the group is a person." | **Yes.** C1 for sentence 1 and C1 for sentence 2; not sentence 3. |
| G2 | `Is it the case that every member of the group is a person?` | one, F1, the same formula (`caseThat_reads`) | the same as G1 after A0 |
| G3 | `Is every member of the group an adult?` | one | **Not necessarily.** S1 with a situation in which Bo is not an adult. The elements are the search's. |
| G4 | `Is it the case that no member of the group is a person?` | one ("no member of the group is a person.") | **No.** C1 for 1 and 2 (Ann exists, and is a citizen, hence a person). C3 if the certificate uses the constant's declaration. |
| G5 | `Is a member of the group a person?` | indefinite: `Is every member of the group a person?` and `Is some member of the group a person?` | — |
| G6 | `Is every member of the group a person` | notQuestion | — |
| G7 | `Does every member of the group vote?` | none, with the first-word advice | — |
| G8 | `Who is a person?` | none, with the wh advice | — |
| G9 | `Must Ann be a person?` | none (no modal form). E2.6's diagnosis of "Ann must be a person." | — |
| G10 | `Is Ann a person?` | one ("Ann is a person.") | **Yes.** C1 for 1 and 2. |
| G11 | `Is every member of the group who a citizen is a person?` | one, through the gap after "who": odd English, accepted. The A0 line shows the sentence. This fixture records the limitation in 4.9. | **Yes.** |
| G12 | `Is every member of the group a person and?` | none: no candidate reads, the closest is diagnosed, and its span is on the question's bytes | — |

### 6.2 A: the agent policy (`usecases/agent-policy`)

**The documents.** `usecases/question-answering/agent-policy/build.py` (pilot tooling, untrusted) writes two `ve-document@1` files from four inputs: `policy.ve`, `policy.manifest.json`, the records `a10`, `a13`, `a25`, `a26` and `a27` of `log.ve`, and an environment.

| Document | Environment |
|---|---|
| `a-unspecified.ve.md` | `environment.unspecified.json` |
| `a-deny.ve.md` | `environment.lean.json` (deny/deny) |

Inside each document:
- The rules are units 1 to 26, with the JSON norm content `ve.norm_english` already produces.
- The record sentences follow, as English fences or AST content (Q0 decides).
- The body is the original text, so every cited unit is quoted in its own words.

The expected statuses come from `usecases/agent-policy/results.json`, unspecified section:
- a25: permitted, SETTLED yes;
- a26: permitted, SETTLED no;
- a27: permitted, UNDECIDED (this is the seeded defect D2: a confirmed email to a colleague, which no rule permits);
- a13: `report_required`, SETTLED yes;
- a10: CONFLICT.

| # | Question | Document | Q2 (*derived*) |
|---|---|---|---|
| A1 | `May "a27" be performed?` | unspecified | **The text does not settle this.** S2: a27's situation, then "The text does not say whether "a27" may be performed." |
| A1d | the same | deny | **No. The document rules this out.** C2 (sentences 1 to 24 say when an action may be performed); C1 for each of a27's record sentences the certificate uses |
| A2 | `May "a25" be performed?` | unspecified | **Yes.** C2 for `permitted`; C1 for the a25 sentences used |
| A3 | `May "a26" be performed?` | unspecified | **No. The document rules this out.** |
| A4 | `Must "a13" be reported to the user?` | unspecified | **Yes.** C2 or C1 for rules 25 and 26; C1 for the a13 sentences used |
| A5 | `May "a10" be performed?` | unspecified | **VE could not decide this.** X1 with the conflict witness |
| A6 | `May an action be performed?` | either | Q1 indefinite: `May every action be performed?` and `May some action be performed?` |
| A7 | `May every action be performed?` | the policy without records | **Not necessarily.** S1 (for example an action whose tool is purchase, unconfirmed) |
| A8 | `Must every action be reported to the user?` | unspecified | **The text does not settle this** (a split on `report_required` for an action that deletes nothing and buys nothing) |
| A9 | `Must an agent not send email unless the user confirms?` | either | Q1 none. The diagnosis: no sort "agent", no wording "send email". |

### 6.3 U: the UDHR pilot, part 7 (Articles 23 to 26)

**Source:** `manage-agents/pilots/udhr/run-20261008T1800Z/translation-part07.ve.md`. It is copied to `usecases/question-answering/udhr-part07.ve.md` with its SHA-256 and run id recorded in a provenance note.

**Content:**
- Profiles: `documents@1`, `norm-defaults@0`, `norms@0`, `readings@1`, `relational-fol@0`.
- 19 units, `u087` to `u103`, which are sentences 1 to 19.
- Reading set `rs_u087` (sentence 1): `entitlement`, `claim_negative`, `liberty`.
- Reading set `rs_u096` (sentence 10): `entitlement` (asserted: every person `has_the_right_to_education`) and `claim_negative` (a norm on `education_spared_required`).
- Fixed norms: u098 (sentence 12), u099a (13), u099b (14), u100a (15), u100b (16).
- Six choices; every regulated predicate is `unspecified`.

The pilot's recorded results: part 7 is CONFLICT-FREE, its premises have a `model`, and u099a has row `c2` UNDECIDED (`metrics.json`).

| # | Question | Q1 (*derived*) | Q2 (*derived*) |
|---|---|---|---|
| U1 | `Must every qualified person be given access to higher education?` (the brief's) | none. "qualified" is not a word of this document, and "be given access to higher education" is not a wording. The diagnosis lists the nearest wordings, among them `{0} must be given equal access to higher education on the basis of merit`. | — |
| U2 | `Must every person be given equal access to higher education on the basis of merit?` | one | **Yes.** C1: Sentence 14 says: "and higher education shall be equally accessible to all on the basis of merit." Then R2. |
| U3 | `Must every person be spared exclusion from education?` | one | by reading of sentence 10: `claim_negative` gives **yes** (C1 for sentence 10); `entitlement` gives **the text does not settle this** (S2). Then U1. `relevantSets = [rs_u096]`. The example of 4.6. |
| U4 | `Is it the case that every person has the right to education?` | one, **if** the lexicon selects "{0} has the right to education". The rendered readings show `classified as "has_the_right_to_education"`, the quoted fallback. If so, U4 has no reading, and the vocabulary defect is reported to the vocabulary owner. | if read: `entitlement` gives **yes**; `claim_negative` gives **not necessarily** (a plain predicate, no gap) |
| U5 | `May every person form as well as join trade unions to protect their interests?` | one | by reading of sentence 1: `liberty` gives **yes**; `entitlement` and `claim_negative` give **the text does not settle this** (the obligation and the permission are not a declared pair) |
| U6 | `Must every person receive elementary education?` | one | **Yes.** C1 for sentence 12, then R2. |
| U7 | `Must every education kind be made generally available?` | one | **The text does not settle this.** S2: an education kind neither technical nor professional (consistent with u099a's recorded UNDECIDED row) |
| U8 | `May a university charge fees?` (the brief's) | none. "university" is not a noun of this document, and its fee sentence u097 is UNFORMALISED. The indefinite rule does not apply, because no rephrasing reads. | — |
| U9 | `Does every person have the right to education?` | none, with the first-word advice | — |

### 6.4 Q1 and speech acts (Q1.4)

- Every speech-act fixture with a polar question gets the same content: the existing tests in `tests/test_speech_acts*.py`, and the conformance cases that use `Is it the case that` or `Is <Name>`. The content must be byte-identical, or the difference is listed in `DELTA.md` as `wording` or `verdict` and signed.
- A `Must …` question to a speech act still gets the `ModalQuestion` refusal, now with Lean's text.

### 6.5 Mutants and negative fixtures (the build checklist's seeded bugs)

Each mutant names the test it must fail:

| Mutant | Must fail |
|---|---|
| F1 precedence removed | `caseThat_reads`'s `#guard`s; G2 |
| an F2 gap allowed before punctuation | the gap fixtures |
| `got` counting `refused` as a reading | G-refused fixtures |
| `Row.lead` letting a countermodel give `.no` | the A7 and G3 tests; `lead_agrees` |
| the premise-model gate removed | X3 fixtures on an inconsistent document |
| `usedPositions` returning every position | G1 (sentence 3 cited) |
| a quote taken from the case instead of the document | the binding test |
| R2 shown with one unchecked choice | the gate test |
| a situation naming one set of two | `render_model_names_choice`'s `#guard` |
| the split check not comparing the base models | a fixture with two different bases |

## 7. Batches

**What every batch carries:**
- 2 to 6 hours for one builder, from the build checklist (`manage-agents/prompts/build-checklist.txt`).
- The lean-first gate of LEAN-FIRST-PLAN 5.1:
  - the full suite, in chunks;
  - the corpus A/B over the English, readings and pilot corpora, with every change listed in `DELTA.md` by class;
  - the deletion ledger;
  - the latency budgets;
  - the relay lint.
- `lean/audit.py`, the frozen inventory, the assurance manifest, trust classes, gate collection (`tools/gate_collection.py --write`), and `tools/lean_statements.py` (additions only).
- Every new Lean and Python module mapped to its layer: `tools/layer_policy.py`, including `lean_layer` for `VE.Question.*`, `VE.Ask.*` and `VE.Words.*`.
- A statement that changes during a build reopens only that statement's review.

| # | Batch | Hours | Owner | Needs |
|---|---|---:|---|---|
| Q0 | Statement spec `docs/spec/question-answering.md`, the stub, computed fixtures, the statement review | 3–4 | planner | — |
| Q1.1 | `VE.Question`: candidates, `readQuestion`, rephrasings, texts, theorems, `#guard`s | 5–6 | Lean | Q0 PASS |
| Q1.2 | `english.question` mode, shapes, relay, `question.read` manifest operation, `ve ask --reading` | 4–5 | Lean, Python | Q1.1 |
| Q1.3 | Q1 evidence: the reverse question corpus, the odd-English measure, latency | 3–4 | Python | Q1.2 |
| Q1.4 | Speech acts' polar questions read by Lean; the Python polar parsing deleted | 4–5 | Lean, Python | Q1.2 |
| Q2.1 | `VE.Ask` core: rows, leads, `SplitU`, soundness, agreement, used positions, sources | 5–6 | Lean | RD-3 merged, Q0 PASS |
| Q2.2 | `ask` wire: the case binding, the zero-set case, negation and split evidence, groups, `ask_wire_sound`, the mode | 5–6 | Lean | Q2.1, Q1.2 |
| Q2.3 | `VE.Words` and `VE.Ask.Render`: frames, quotes, names checks, W7 rows, render theorems | 5–6 | Lean | Q2.2 |
| Q2.4 | One owner of situation wording: Python's producers relay `VE.Words`; deleted; A/B | 4–6 | Lean, Python | Q2.3 |
| Q2.5 | `ve ask`: CLI, evidence generation, flip generator generalised, fixture documents, end-to-end tests | 5–6 | Python | Q2.3 |
| Q2.6 | Evidence and measurement: fixtures, agreement with W2, latency, reading and writing evaluation, report | 4–5 | Python, evaluation | Q2.4, Q2.5 |

**Order.**
- Q0 first.
- Q1 runs now (it needs only E2.6, which is merged): Q1.1, then Q1.2, then Q1.3 and Q1.4 in parallel.
- Q2 waits for RD-3's merge: Q2.1, then Q2.2, then Q2.3, then Q2.4 and Q2.5 in parallel, then Q2.6.
- Q1.3 and Q1.4 may overlap with Q2.

In total: about 47 to 59 builder hours, of which Q1 is 16 to 20.

### Q0. Statement spec and review (planner, 3–4 h)

- **The spec.** `docs/spec/question-answering.md` writes sections 3 and 4 as a statement spec: definitions, English with one reading each, wire, diagnostics in order, Lean statements, fixtures, limits, and a review checklist (10).
- **The stub.** `lean/SpecStubs_question.lean`, untracked: every definition with its body, and every statement as `def … : Prop`.
  - It is elaborated with `lake env lean` against a build of `main`, and against a build of RD-3's branch for section 4.7.
  - Every elaboration failure is fixed in the spec, not in merged code.
- **What the stub computes:**
  - every Q1 value of 6.1 to 6.3 (each candidate's `read` outcome, each diagnosis text and span);
  - whether RD-3's admission accepts zero sets (4.7);
  - the choice between the two routes for `relational-fol@0` documents;
  - the name of the binding-free replay (`replayOk`);
  - `premisesU`'s order for `sourcesU`.
- **What running the generators computes:** the Q2 values, through RD-3's Python generators on the fixture documents. If RD-3 is not merged, Q0 computes Q1's values and marks Q2's as *derived* pending RD-3.
- **The review.** Astra and Fable must converge on PASS, which requires both to accept each statement as true under its hypotheses; that the stub elaborates is not enough. Sections 3.5 and 4.7, D4 and the frames of 4.6 are the review's subject.
- **Done when** the stub elaborates, the spec is committed, and the review has converged on PASS.

### Q1.1. The question reader (Lean, 5–6 h)

- **Files:**
  - `lean/VE/Question/Read.lean`: 3.5's definitions and theorems, and the gap computation over `lexSpans`.
  - `lean/VE/Question/Help.lean`: the closest candidate, the span mapping, `rephrasings` and the advice table.
  - `lean/VE/Question/Texts.lean`: 3.3's codes, classes and texts, and the question variants of E2's texts.
  - `lean/VE/Question/Examples.lean`: `#guard`s.
- **Imports:** `VE.EnglishGrammar.Read`, `.Diagnose`, `.Advice` and `.Lexer`. Nothing in `lean/VE/EnglishGrammar/` changes.
- **The new lock list** `ve/question/LOCK.json` covers `lean/VE/Question/*.lean`, and `question_version` is defined as 1.
- **Statements:** `readQuestion_one`, `readQuestion_complete`, `question_reading_unique`, `asked_reads_back`, `caseThat_reads`, `fronted_text`, `rephrasings_read`, and the lemma from `.stopped _ .noDerivation` to `NoDerivation`.
- **Fixtures:** the Q1 columns of G1 to G12, A1, A6 and A9, and U1 to U9, as `#guard`s over the fixture environments and lexicons. The lexicons are copied from Python's producer for each fixture environment and pinned by `lexicon_id`.
- **Deleted, not duplicated:** nothing yet. Speech acts move in Q1.4.
- **Done when:** the statements are proved, the `#guard`s pass, the audit is clean, and the A/B shows no change, since no existing mode changes.

### Q1.2. The `english.question` mode, the relay and `ve ask --reading` (Lean and Python, 4–5 h)

- **Lean:** `lean/VE/Question/Run.lean` (the case decoder reuses `VE.EnglishGrammar.Run`'s), with the `Protocol.lean` entries, `runMode_englishQuestion`, the schema, the skeleton row, a branch of `runMode_fits`, and the `VE/Audit.lean` lines.
- **Python:**
  - `ve/backends/english_lean.py` gains `read_question`, which builds the same request `english.read` gets, from the same lexicon producer, plus `question`, and raises Lean's code and text verbatim. It is in the relay lint.
  - `ve/ask.py` is the CLI, with `--reading`, which prints A0 or Lean's refusal.
  - The manifest operation is `question.read`: `authority: lean-only`, `python: []`, with call site `ve.backends.english_lean:read_question`.
  - The layer policy maps `ve.ask` to layer 4.
- **Fixtures:** the Q1 columns through the CLI, as subprocess tests, with exit codes 0 and 2.
- **Deleted, not duplicated:** none; this is a new mode.
- **Done when:** the gate passes, `tests/test_lean_service.py`'s mode list check passes, the CLI fixtures pass, and the A/B shows no change.

### Q1.3. Q1 evidence (Python, 3–4 h)

**The reverse question corpus.** For every corpus sentence with one reading (the sealed English corpus and the use-case documents), `conformance/question_reverse.py` builds:
- the F1 question;
- where the sentence begins with a quantified or named subject followed by *is*, *must* or *may*, the F2 question with that word fronted;
- spacing and capitalisation mutants.

It records the outcome of `english.question` for each.

**Measured:**
- the share of F1 questions that read with the sentence's formula. `caseThat_reads` says every one does, and a miss is a bug.
- the share of F2 questions that read with the sentence's formula, or are `many`, and each `many`'s cause;
- **the odd-English measure:** for each F2 question, the word is moved to every other gap and the acceptances are counted. Each acceptance is listed. This bounds the over-generation of 4.9.
- latency: p95 and the maximum per question, against 3.6's budgets.

**Report:** `docs/spec/question-answering-q1-report.md`. Every number cites the command that produced it.

**Done when:** the report is committed, and every F1 miss is fixed or explained.

### Q1.4. Speech acts read polar questions through Lean (Lean and Python, 4–5 h)

- **Lean:** `VE.Question` with `auxs := ["is"]` reads speech acts' `Is it the case that …?` and `Is <Name> …?`. The `ModalQuestion` refusal of a question that begins with `Must` or `Can` becomes a Lean text in `VE.Question.Texts`, for the speech-acts caller only.
- **Python:** `ve/speech_english.py`'s polar branches call `read_question`, and the polar use of `_copular` and the `Must`/`Can` refusal are deleted. `_copular` stays for which-questions and `follows`, which are Q3's, and the ledger lists it with its remaining callers.
- **Fixtures:** 6.4.
- **A/B:** the speech-acts corpus. Content is byte-identical, or each difference is listed in `DELTA.md` as `wording` or `verdict` and signed. One expected source of difference is `_copular`'s match on a declared verbalisation against Lean's lexicon wording.
- **Done when:** the gate passes, the ledger is signed, and the relay lint passes on the speech surface's polar path.

### Q2.1. The answer core (Lean, 5–6 h)

- **Files:**
  - `lean/VE/Ask/Basic.lean`: `Lead`, `Row`, `Row.lead`, `SplitU`, `LeadHolds`, `RowOk`.
  - `lean/VE/Ask/Sound.lean`: `lead_sound`, `split_counter`, `splitOk_sound`, `lead_agrees`, `all_yes_iff_fold`. `splitOk_sound` needs a variant of RD-3's `expansion_of_modelCheck` that exposes the expansion's base equation; it is added as a new theorem, and RD-3's statement is not edited.
  - `lean/VE/Ask/Sources.lean`: `Source`, `sourcesU`, `sourcesU_length`, `usedPositions`, `usedPositions_sufficient` (through RD-3's `usedLabels_sound` and a lemma that `⊤` premises change no entailment), `cited`.
  - `lean/VE/Ask/Examples.lean`.
- **Fixtures:** `Row.lead` on every combination of row values. `usedPositions` on G1's certificate gives positions whose sources are sentences 1 and 2.
- **Deleted, not duplicated:** none. RD-3's functions are imported.
- **Done when:** the statements are proved and the audit is clean.

### Q2.2. The `ask` wire (Lean, 5–6 h)

- **Files:**
  - `lean/VE/Ask/Wire.lean`: `replayAsk` and `ask_wire_sound`.
    - It reads the question with `VE.Question.readQuestion`, so the request's formula is not trusted.
    - It replays the case with RD-3's `replayVerdictsND`, or the lower route's replay, after checking that the case's conclusion is ψ, `assumed` is empty, and the case's units and sets are the document's (4.3).
    - It decodes `negation` and `split` per choice with RD-3's decoders, then builds the rows, the groups and `relevantSets` (`relevantSets_sound`).
  - The zero-set case (4.7), with `choiceU_nil` or the admission extension and its conservativity theorem.
  - The plain adapter, if Q0 chose it.
  - `lean/VE/Ask/Run.lean`: `runMode_ask`, the schema, the skeleton row, a branch of `runMode_fits`, and the audit lines.
- **Fixtures:** the leads of G1 to G4, A1 to A5, U2, U3 and U6 from recorded evidence files (no generator in the test). Also: a case whose conclusion is not the question's; a case whose unit content differs from the document; a split whose two models differ in a base atom.
- **Deleted, not duplicated:** none.
- **Done when:** the gate passes and the A/B shows no change outside the new mode.

### Q2.3. Words and the answer text (Lean, 5–6 h)

- **Files:**
  - `lean/VE/Words/Situation.lean`: 4.5's functions and their `#guard`s against Python's current output on the readings and norm-defaults corpora, recorded.
  - `lean/VE/Ask/Render.lean`: 4.6's frames, 4.3's citation rules, the quotes from `VE.Service.Document.split`, and the reading names. The names come from the request, are checked with `checkRendering` for asserted candidates, and are listed in `unchecked_names` otherwise.
  - The render theorems: `render_quotes_bytes`, `render_asked`, `render_cites_exact`, `render_lead`, `render_model_names_choice`.
- **W7:** the frames A0 to X5 are registered with W7's all-derivations gate, and the stage that owns W7 at build time is named in the ledger (question 9).
- **Fixtures:** the text columns of 6.1 to 6.3 from recorded evidence, and the mutants of 6.5.
- **Deleted, not duplicated:** none yet. Python's producers move in Q2.4, and Q2.3's `#guard`s pin byte equality first.
- **Done when:** the statements are proved, the `#guard`s pass, and the W7 rows are registered.

### Q2.4. One owner of situation wording (Lean and Python, 4–6 h)

- **Lean:** the Lean routes that answer `ve document readings` and the norm-defaults report include `VE.Words`' lines in their answers: each shown model's situation, each gap clause and filled-gap sentence, and each pair sentence. This is a new field per line. Existing fields are unchanged.
- **Python:** `readings_s2_wording.situation`'s base part, `norm_defaults_english.point_clause`, `_negative_modal`, `filling_sentence`, `readings_s2_english` `gap_sentences` and the pair-sentence producer are replaced by reading Lean's lines; their wording logic is deleted. `tools/relay_lint.py` gains a rule that no `is a ` or `is an ` element-line literal and no `does not say whether` literal may appear in `ve/readings*.py` or `ve/norm_defaults*.py`.
- **A/B:** the readings, norm-defaults and pilot corpora. The target is byte-identical English. Any change is a `wording` row of `DELTA.md`, signed by the DRI.
- **Done when:** the gate passes, the ledger is signed, and the A/B has no unsigned row.

### Q2.5. `ve ask` (Python, 5–6 h)

- **`ve/ask.py`:** the full command.
  1. Read the document and the question.
  2. Call `read_question`.
  3. Build the readings case with the existing readings relay (`ve/readings_route.py`), with conclusion ψ.
  4. Generate evidence per choice with RD-3's generators: certificates for ψ and for ¬ψ, a countermodel, a premise model, and conflict packages.
  5. When a countermodel depends on gaps (Lean's `gapsOf`) and no ¬ψ certificate is found, run the flip search.
  6. Collect the reading names from `reading_names`.
  7. Call `ask` and print Lean's lines.
- **The flip search:** `ve/norm_defaults.py`'s UNDECIDED witness search is generalised to a target formula, and the point search becomes its instance (one generator).
- **Fixture documents:**
  - `usecases/question-answering/group.ve.md`;
  - `udhr-part07.ve.md`, with its provenance note;
  - `agent-policy/build.py` and the two A documents it writes.
- **Tests:** `tests/test_ask_cli.py` runs every Q2 fixture of 6.1 to 6.3 end to end and checks the exit codes. Every test name is added to gate collection.
- **Manifest:** the operation `question.answer` (`authority: lean-only`, call site `ve.ask:_answer`).
- **Deleted, not duplicated:** the flip search's point-only copy.
- **Done when:** the fixtures pass, the relay lint passes, and the gate passes.

### Q2.6. Evidence and measurement (Python and evaluation, 4–5 h)

**Report:** `docs/spec/question-answering-report.md`, with every number generated from saved records:
- **Fixtures:** each of 6.1 to 6.3, expected against got.
- **Agreement with the existing check:** for every fixture question, and for every query of the readings and norm-defaults conformance corpora asked as an F1 question of its document, Lean's leads are compared with `ve document readings --conclusion` (RD-3's fold, or Python's W2 fold on a document without content-bearing sets). *Yes* must be ALL; a negative lead must be NONE or one side of SOME. Every difference is a bug, or a row of `DELTA.md` with a reason.
- **Latency:** `english.question` and `ask` CPU, and `ve ask` wall time on U3 and A1 at the gate's load. The budgets are pass gates: `ask` Lean CPU at most 2 s; `ve ask` on U3 at most 60 s wall. Each is met, or its revision is reviewed.
- **Zero-training readability.** This uses the frozen readability protocol (2026-10-03: Claude Sonnet 5.5 as a proxy reader and writer, given only what a human gets), with bars registered before the run.
  - *Reading:* the share of answers whose lead the proxy reads correctly. The "Not necessarily." and "No." wordings are both shown, to measure D4. Also measured: the share of critical misreadings, where "not necessarily" is taken for "forbids" or the reverse.
  - *Writing:* the share of tasks in which the proxy writes a question VE reads with the intended meaning, first try and within three tries using VE's help.

  These model calls happen in this batch only.
- **Wording counts:** the answers that show a quoted fallback wording (for example `classified as "…"`), and the shown situation lines that read back.
- **Done when:** the report is committed and every bar is reported as met or not met, with no rounding up.

## 8. What is measured, and how

| Claim | Measure | Where |
|---|---|---|
| A question has one reading or is refused | theorems 3.5; the reverse corpus | Q1.1, Q1.3 |
| Odd English is rarely accepted | acceptances of moved-word mutants, counted and listed | Q1.3 |
| Answers never contradict the existing verdict | `lead_agrees`, `all_yes_iff_fold`; the agreement A/B | Q2.1, Q2.6 |
| Reasons are the certificate's premises | `usedPositions_sufficient`, `render_cites_exact` | Q2.1, Q2.3 |
| One owner of situation wording | the A/B of Q2.4; the relay lint rule | Q2.4 |
| Zero-training reading and writing | the proxy evaluation, with bars registered before the run | Q2.6 |
| Latency | the budgets of 3.6 and Q2.6, measured on the service | Q1.3, Q2.6 |

Nothing in this plan states a coverage gain. The UDHR and agent-policy fixtures show what the feature does on real text. They are not a byte measure of any use case.

## 9. Honest open questions

1. **"No." against "Not necessarily."** The brief says "No. Here is a situation the document allows where it fails". This plan says "Not necessarily." in front of that sentence and keeps "No." for a refuted sentence (D4). The reasons are the theorem `countermodel_not_negative` and the one-reading rule. Q2.6 measures both wordings. *Recommendation:* keep D4 unless the reading evaluation shows "No." read correctly as "not guaranteed" at the registered bar.
2. **"Sentence 26.1."** Display numbers are positions within the file (sentence 14 of part 7). Article and paragraph labels need a `label` field on units in `ve-document@1`, a signed wire change. *Recommendation:* a separate small design item. Until then, the quote of the cited sentence is what makes the citation findable.
3. **Which rule decides.** A layer premise covers every rule on one act, so C2 cites them all. For a question about one ground point, norm-defaults' status row already names the deciding rules (`norm_defaults_english.status_sentence` reads Lean's `rules`). *Recommendation:* a follow-up batch that cites those rules when the asked sentence is a ground atom of a regulated predicate, with its own statement: that the named rules decide the point.
4. **Questions with *does*.** "Does every agent read a file?" needs the base form of each verb wording. *Recommendation:* add base forms to sense packs (senses D2), then add form F3. Until then the advice points to F1.
5. **Odd English through movement.** If Q1.3 finds acceptances worth stopping, two fixes are available:
   - a main-clause condition on the derivation tree: the fronted word may not land under a restrictor nonterminal, and the stub names which ones;
   - pruning with `viable`, once a completeness lemma for it is proved.
6. **Scope.** Not covered yet: the soft and rights chains, the superposed route (RD-7), components (RD-4), and `--under` (assumed readings). Each needs its Lean verdicts first.
7. **Senses.** A question word that the document's senses leave unresolved has no reading today. Rephrasings with glosses ("funny (meaning strange)") would follow senses D6's candidates.
8. **Reading names for norm candidates** stay Python's until E3 moves the statement layer, and are marked `unchecked`.
9. **Who owns W7.** The all-derivations gate for VE's own sentences is named in composition.md 2. Q0 establishes whether it is still Python's after E2.6, and registers A0 to X5 with whichever owner holds it.
10. **Element names in situations.** UDHR situations name elements by their sort ("person is a person"). Element names come from the search. Clearer display names would be a change to `VE.Words` and to the generators, with its own A/B.

## 10. Statement review checklist (Astra and Fable, Q0)

1. Is `QuestionOneReading` the right notion of one reading? The question accepts several candidates that all mean φ, and the first is shown. Is "first" stable under the gap order?
2. Is `caseThat_reads` true as stated, including when the body itself begins with `Is it the case that`?
3. Does `fronted_text` pin the question text to the candidate exactly, bytes included?
4. Is `rephrasings_read` provable from F1 precedence, and are offered rephrasings distinct in meaning?
5. Do `SplitU`'s equations put both structures on one base, and does `splitOk_sound` follow from `ndModelOk_sound`'s construction?
6. Is `Row.lead`'s priority honest? Can any combination of rows that `RowOk` admits give a lead that `LeadHolds` contradicts?
7. Is `all_yes_iff_fold` true with RD-3's gate (conflict rows first)?
8. Does `usedPositions_sufficient` hold when the meaning-id binding is checked once on the full list and the replays are binding-free? Is blanking with `⊤` index-stable for the tableau trace?
9. Does `render_cites_exact` say "exactly": every source line is a used source, and every used source has a line?
10. Does the case binding (4.3) stop Python from quoting one document while proving another?
11. Does every frame of 4.6 have one reading, and does none begin with another registered production's lead?
12. Do the non-wordings of 4.6 and the non-claims of 4.9 cover every way an answer could overclaim?
13. Is anything in sections 3 to 5 decided in Python?
