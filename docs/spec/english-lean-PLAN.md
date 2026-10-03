# English in Lean: the grammar as data, one proved all-derivations parser (PLAN)

**Status:** plan only, draft 1, 2026-10-03, branch `design/english-lean` from `main` at `a093a14d`. No code or
proofs change with this document. It was written from reading the sources; **nothing was built or run** (this
session could execute neither Python nor Lean). Every number below is either a figure from a committed report
(cited) or a count made by reading the source (marked *static*). Stage S0 replaces the static counts by measured
ones. `file:line` references were read on 2026-10-03 and must be re-read at each step. The plan has not yet had its
two frontier reviews; S1 starts after them.

Inputs: the lead's decision of 2026-10-03 (the one-reading guarantee must be Lean-checked, reversing
[SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md) 1.3 and the "English surface: stays Python by decision"
row of 2.3); [verification-contract.md](verification-contract.md) P1–P3; [english-surface.md](../english-surface.md);
[PLAN-ZERO-TRAINING.md](../../PLAN-ZERO-TRAINING.md); [wire-contract-PLAN.md](wire-contract-PLAN.md) (the
generated-data pattern); `ve/assurance-manifest.json` unit `english.admission`; `lean/README.md` "Remaining
obligations and trust boundary". `docs/TRUST-MAP.md` is not on branch `docs/trust-map` (that branch is at the same
commit as `main`), so section 6 is written against the assurance manifest and lists the rows a trust map needs.

## 0. Decision in brief

**The problem.** "Every sentence has exactly one reading" is enforced by a hand-written Python parser plus a
generated Lark grammar run with a third-party Earley parser. Lean proves it for a core fragment that is not on the
admission path. For several statement-layer surfaces nothing checks the whole sentence at all (1.4).

**Verdict on the orchestrator's direction: adopt, with eight changes.** The core is right: the grammar becomes data
that Lean holds, one generic parser returns all derivations and is proved sound and complete against a derivation
relation, meanings are computed from derivations, and Python becomes an untrusted producer that is compared with
Lean and then overruled by it. Two facts make this closer than it looks. Python's uniqueness grammar is already
generated data (`english_lark_grammar`), and Lean's discourse layer already uses exactly this shape for one small
grammar: a derivation relation defined by a checking function, and an enumerator proved to list exactly the
derivations (`VE.Discourse.mem_derivs`). The changes:

1. **The guarantee is a decision per sentence, not a theorem about the grammar.** Unambiguity of a context-free
   grammar is undecidable in general, and the static W7 proof reaches only the core fragment under a restrictive
   lexical check. Lean decides, for each submitted sentence, that it has exactly one derivation; the theorem is
   that this decision is correct for every grammar. Static theorems stay as a second tier (3.6).
2. **Authoring keeps today's stricter rule: exactly one derivation**, even when two derivations give the same
   formula (PLAN-ZERO-TRAINING section 1). "The set of meanings has one element" is weaker and would turn today's
   rejections into acceptances. It is defined, proved to follow, and used for translation-mode reading sets;
   adopting it for authoring is a separate product decision.
3. **Neither CYK nor Earley.** CYK needs Chomsky normal form, and the conversion does not preserve the number of
   derivations without further proof. Earley's all-derivations proof is several times larger. The plan uses a
   right-to-left tabular parser for grammars with no empty rule and no left recursion, both checked on the data.
   The current grammar appears to satisfy both (*static*; S0 confirms).
4. **A syntactic envelope plus side conditions in the meaning function**, not features compiled to nonterminals,
   for scope, shadowing, typing and list-marker depth. That is what Python does today, so it is exactly
   conservative. One feature is compiled to nonterminals, as Python's grammar already does: integer slot versus
   object slot.
5. **The lexer moves into Lean and the grammar is over word tokens.** Regex terminals disappear; a multi-word
   wording is a sequence of word tokens, so ambiguity inside a wording becomes visible to the parser.
6. **The selected lexicon is input data that Lean validates by a small relation.** The 300-line vocabulary lint
   then only chooses between honest wordings, and leaves the trusted base.
7. **The render round trip is checked per rendered text**, for every profile, by the same reader. It holds by
   construction and needs no renderer proof. Universal renderer theorems remain for the core fragment.
8. **Order of work: formula-level English first (S0–S5), then the statement layers one at a time (S6).** The
   statement layers are where enforcement is weakest today, but each needs its own delta review.

What does not change: the strict surface, canonical text, wire and every identity; every existing Lean module (new
files only); the rule that unique parsing never establishes intent or source fidelity.

## 1. Measured inventory

### 1.1 How one reading is enforced today (formula-level English)

`_parse_english_document_uncached` (`ve/english.py:1636`) runs five steps on a source:

1. **Normalise** (`_normalise_english_source`, :165): collapse whitespace outside quoted identifiers; lower-case
   the first word of each sentence unless it starts a declared capitalised constant.
2. **Read** with `EnglishParser` (:886), a hand-written recursive-descent parser over characters and regular
   expressions. It returns the formulas. This is the reading.
3. **Audit** with `require_unique_derivation` (`ve/surface/unambiguity.py`): Lark Earley,
   `lexer="dynamic_complete"`, `ambiguity="explicit"`, over `english_lark_grammar(env)` (:1811). Any `_ambig` node
   rejects. Budgets: 10,000 characters and 30 seconds of wall clock.
4. **Correspond** (`require_correspondence`): for surface records that have a `parser_hook`, the value re-derived
   from the Earley subtree must equal the parser's value. Exactly one record has a `parser_hook`:
   `natural_clause` (:2012).
5. **Check** types and scope (`ast.check_document`), then marked conclusions by proof search (`_check_conclusions`).

Gaps in this enforcement:

- **G1. The reading and the uniqueness check come from different artefacts.** For every construct except
  `natural_clause`, nothing checks that the formula returned by the hand parser is the meaning of the unique Earley
  derivation. The Earley tree carries no meaning.
- **G2. The envelope claim is an argument, not a check.** The grammar drops scope, sorts and indentation "so
  removing constraints can only add derivations" (:1811 docstring). Nothing shows that every text the hand parser
  accepts is derived by the grammar with the same structure.
- **G3. Third-party completeness is trusted:** Lark's forest construction and Python's `re`. Each multi-word wording
  is one regex terminal, so structure inside a wording is invisible to the audit.
- **G4. The budget is wall clock**, reported as `ResourceLimit` (a conflation the assurance manifest records).
- **G5. Lean's proofs are off the admission path.** The `english` service mode has no caller under `ve/`
  (manifest: `authority: python`, `lean_call_sites: []`).
- **G6. Outside formula-level English, enforcement is weaker** (1.4).

### 1.2 The grammar as it stands

| Part | Size (*static*) | Where |
|---|---|---|
| Fixed productions, base | 82 alternatives over 20 nonterminals | `english_lark_grammar` |
| `order@0` | 9 integer-term alternatives, 5 comparison clauses | same; `_COMPARISONS` |
| `data@0` attribute sugar | 2 clause schemas per functional total relation | same |
| `alternatives@0` guards | about 10 alternatives, 1 extra reference form | same |
| Natural clauses (`some`, `no`, `every ADJ NOUN`) | 14 alternatives | `_natural_grammar` (:1972) |
| Risk wordings | 4 fixed wordings, 2 fixed negatives | `EnglishVocabulary` |
| Per predicate | up to 3 rules per wording (clause, subject relative, object relative), for the positive wording, the validated negative and input aliases | generated |
| Per constant, per sort | up to 3 spellings; 1 noun (10 declaration and 10 reference forms through fixed rules) | generated |
| Bounds | `MAX_PREDICATES` 256, `MAX_SORTS` 32: at most about 1,600 wording rules | `ve/limits.py` |
| Vocabulary policy | 13 unary and 25 binary idioms, 9 complement and active-phrase patterns, about 18 lint codes | `english_vocabulary.py`, `printer.py`, `english.py` |
| Advisory lexicon | 72,780 OEWN entries, used only by `ve propose`, never by the parser | `ve/lexicon/` |

The largest committed environment has 48 `verbalisation` entries (`usecases/eligibility`, *static*). The grammar
has no empty production once `?` and `*` are expanded, and no left recursion (*static*; lists and guards are
right-recursive or fixed-arity).

Three neighbours are out of scope. `ve/parser.py` is the strict surface: deterministic, already decided by Lean in
`parse` mode except the `definitions@0` sugar, which is a recorded gap. `ve/grammar.py` exports strict grammars for
constrained decoding; its output is re-checked by the parser and is not on any trust path. `ve propose` changes the
environment while it parses a proposal; its adopted text is re-parsed through ordinary admission, so only that
second parse matters here.

### 1.3 What is not a plain context-free grammar (formula level)

| Mechanism | Where (`ve/english.py`) | Treatment in the data model |
|---|---|---|
| Whitespace, sentence-initial capitals, case-insensitive vocabulary words, exact quoted identifiers | :122–:197, `_content_pattern` | Lean lexer and a terminal-matching relation (3.1) |
| Word-boundary guard on literals | `take` | follows from word tokens |
| Open token classes: labels `S1`, numerals, coefficients | `declaration`, `int_leaf` | terminal classes, a finite list |
| Scope stack, shadowing, nearest-first references | `declaration`, `term_options` | side condition in the meaning function |
| Sorts of arguments | `ast.check_document` | side condition (the existing checker) |
| Integer versus object slots | `slots`; `int_term` nonterminal | feature compiled to two nonterminals (as today) |
| Bracketed integer terms, depth limit, canonical numerals | `_mask_brackets`, `int_syntax`, `int_term` | context-free rules; limits are side conditions |
| List markers by depth, legacy word markers, split-`if` lists | `formula` | free in the grammar; depth is a side condition |
| `a`/`an`, `who`/`that`, `is`/`are` | `formula`, `coordination` | free on input; separate rules; no feature needed |
| Three-atom guards with comma-encoded association | `guard` | four fixed rules (as today) |
| Longest match among wordings; "extends existing wording" rejection | `atom` | all derivations replace longest match; the rejection is a shadow-comparison item (7.3) |
| Pronoun `it`: sole constant of all earlier sentences, blocked after any quantifier | `term_options`, `document` | document state threaded through the meaning function |
| Blocked wordings (risk, alternatives, plural pronouns) | `_RISK_*`, `unknown_atom`, `alternatives_guard` | most fire only when nothing parses; the rest are side conditions with stable codes |
| `data@0` sugar needs `functional` and `total` | `atom` | rules instantiated only for such relations |
| Conclusion markers decided by proof search | `_check_conclusions` | grammar yields the mark; the proof search stays outside, unchanged |
| Vocabulary selection and lint | `EnglishVocabulary` (:230–:535) | producer of the lexicon, validated in Lean (2.4) |
| Renderer tries three settings and re-parses each | `render_english` (:809) | per-output check in Lean (3.5) |

The hand parser has 49 rejection sites (*static*). S0 classifies each as implied by the grammar, a side condition,
or diagnostic wording only.

### 1.4 Statement-layer and display English

| Surface | What enforces one reading today | Stage |
|---|---|---|
| Norm rule blocks, precedence lines (`norm_english.py`) | Earley over the whole block (`_block_grammar`); the consequence must equal exactly one enumerated wording; no correspondence between the hand split and the tree | S6 |
| Norm-defaults legend sentences | Earley with `legend_grammar`, then equality with exactly one candidate | S6 |
| English fences in documents; natural presentations | the formula-level path | S2–S5 |
| Definition sentences, glossary, citations (`surface/definitions.py`) | head and body each audited; the sentence is split at the one `exactly when` outside quotes and the last `", "`; glossary and citation prefix are regex and table lookup | S6 |
| Speech acts, 8 frames (`speech_english.py`) | ordered if-chain; Earley only for embedded statements; the copular shortcut and commands by exact-match counting | S6 |
| Report sentences, about 14 frames (`report_english.py`) | its own exhaustive enumerator; an embedded statement that is Earley-ambiguous counts as no derivation (`_parse_formula` catches every `VEError`) | S6 |
| Quantity sentences, about 13 forms (`surface/time.py`) | its own enumerator over connector splits, filtered by typing, budget 10,000; plus the core parser on the erased environment | S6 |
| Soft-norm source, declarations (`surface/softnorms.py`) | regex; only the rewritten rule block and guards are audited | S6 |
| Risk wordings, 10 (`surface/risk.py`) | exact string match over label maps, count must be 1 | S6 |
| Rights incident prefix | regex; the rest is a rule block | S6 |
| Discourse references | **Lean is the authority**: own lexer (`Discourse/Access.lean`, a named trust boundary), hand-written grammar with `mem_derivs`, `accepted_unique` | keep |
| Display-only English: rights units and limitations, status sentences, legends, risk gap lines, reading-set sentences, document frames, the five historical views | never parsed back; no reading check exists | S7 |

Nothing in `ve/` returns a set of readings from a parse. Reading sets are author-supplied JSON or come from the
assist catalogue (`ve/assist/ambiguity_patterns.py`, 7 patterns).

### 1.5 What Lean already has

- **Core English (W7), `lean/VE/English/*`:** token level, a hand-written deterministic parser, and proofs of
  `core_unique_derivation`, `core_parse_sound`, `core_parse_render`, `core_render_injective`, `core_one_reading`,
  with `admissible_sound` for the finite lexical check. Standard axioms only. Lexing is done by the Python harness.
- **Reach of the core:** in `conformance/english-lean-report.json`, 57,765 of 85,000 Python renderings (68.0%) are
  core wording and Lean's reading agrees on all of them; 14 of 17 vocabularies pass `admissible`. Templates
  containing `or` or a comma fail it.
- **Discourse English:** the checking-function-plus-proved-enumerator pattern, for one hand-written grammar.
- **No generic grammar code.** No production, chart or derivation type exists outside those two modules.
- **Strict surface:** character-level parsers with `parse_print` and `print_injective`; P1–P3 for an independent
  grammar relation are unproved for every surface (`lean/README.md`, `lean/METATHEORY.md`).
- **Constraints on new Lean code:** Lean 4.24.0, no Mathlib; `lean/audit.py` forbids `sorry`, `axiom`,
  `native_decide`, `partial`, `unsafe`, `implemented_by` (even inside comments) and primed theorem names; every
  theorem needs a `#print axioms` line in `VE/Audit.lean`; every file is listed in the frozen inventory and the
  layer map. All `VE/English/*` files are frozen, so this plan adds files and edits none.

### 1.6 Corpus and timings on record

| Item | Figure | Source |
|---|---|---|
| Round-trip ASTs | 85,000 (17 vocabularies × 5,000), 0 failures | `conformance/english-surface-report.json` |
| Earley audit texts | 8,500 prefix + 4,250 random; 850 multi-statement documents; 0 ambiguous | same |
| Mixed-profile texts | 6,757, 0 with multiple derivations | `conformance/english-mixed-report.json` |
| Natural-view statements | 1,220 (600 natural, 620 fallback) | `conformance/natural-view-report.json` |
| Call sites of the English entry points | 320 in 37 files of tests, conformance, use cases and bench | *static* |
| Use cases; pilots | 14 directories; Claude constitution, UDHR, BlueDot (pinned by `bench/PROFILE-GOLDEN.json`) | repository |
| Longest admitted sentence | 150 tokens; parse plus natural display 64.2 / 95.0 ms (p50 / p95, Python) | `bench/PROFILE-ENGLISH-AFTER.md` |
| Document checks (Python) | BlueDot 1,043.8 ms; Claude 50.3 ms; UDHR 3.1 ms (p50) | same |
| Compiled Lean, ordinary checks | 47–152 ms one-shot medians; 200 ms target | SEMANTICS-MIGRATION-PLAN section 0 |

**Not measured here:** instantiated grammar sizes per environment, sentence-length distribution, Earley time per
sentence, and any Lean timing for this design. These are S0 and S1a deliverables.

## 2. Design

### 2.1 Alternatives considered

| Option | Verdict | Reason |
|---|---|---|
| A. Grammar as data, generic all-derivations parser proved against a derivation relation | **adopt**, as changed in section 0 | one proof serves every environment, profile and future wording; matches what Python already does |
| B. Extend W7: prove the whole grammar unambiguous, deterministic parser | reject as the main route; keep as second tier | needs a lexical condition that real vocabularies fail (3 of 17 today); every new wording needs new proof; W7's trigger has never fired because wording keeps changing |
| C. Python sends its derivation, Lean checks it | reject | checks soundness only; uniqueness needs a complete search, which is option A |
| D. Certify each environment's grammar as LR(k) or LL(k) | reject | wordings share prefixes and have term holes, so conflicts are routine; a verified table construction is heavier than A |
| E. An untrusted fast parser emits a chart, Lean checks its closure | reject | the closure check costs as much as parsing and its proof is the completeness proof of A |
| F. CYK over a normal form | reject | the normal-form transformation must be proved to preserve derivation counts, and cubic time is unconditional |
| G. Verified Earley | hold in reserve | needed only if left recursion or empty rules become necessary; the proof is far larger |

### 2.2 Architecture

```
text ─lex─▶ sentences of tokens ─parse (table, all derivations up to a cap)─▶ trees ─meaning─▶ formula or rejection
             Lean definition        Lean, PROVED against Tree.derives          Lean definition (actions)
grammar = fixed rules (generated table literals) + rules instantiated from the validated lexicon
```

- **Derivation relation.** A tree is a derivation when a small checking function accepts it. That function is the
  specification (`ParseSpec` of the verification contract, as a relation between text and tree).
- **Parser.** For positions from the end of the sentence to the start, and nonterminals in increasing left-corner
  rank, it fills a table entry with the derivations of that nonterminal starting at that position, at most `cap`
  per end position. Because no rule is empty, every symbol after the first reads rows already filled; because the
  rank decreases to a leading nonterminal, the first symbol reads entries already filled in the same row. The
  function is total by structural recursion on the row and the rule list, with no fuel. Rules are indexed by their
  first word, so a keyword-led rule costs nothing at positions where its keyword is absent.
- **Three verdicts with witnesses.** With `cap = 2` the result is none, one tree, or two distinct trees. The two
  trees are re-checked by the checking function, so an "ambiguous" verdict is self-certifying and gives the editor
  the pair that Python prints today.
- **Documents.** The lexer splits sentences at the terminator token, and no rule may mention that token (a grammar
  check), so a document's derivations are exactly the lists of its sentences' derivations. Cost is linear in the
  number of sentences.
- **Meaning.** Each rule names an action. Actions are a small hand-written Lean library, typed so that a derivation
  always has a meaning or a *declared* rejection (unbound reference, shadowed name, sort mismatch, marker depth,
  limits, blocked wording). Document state for the `it` rule is threaded through sentence meanings.

### 2.3 What is data and what is code

Data: the fixed rules per profile; the lexicon; the instantiated grammar; token classes by name. Code, written once
in Lean: the lexer; the derivation checker; the parser; the instantiation of wordings into rules; the action
library; the lexicon validity relation. **Honest limit:** meanings are not data. A rule is only as reviewable as
its action, and the library is the largest reviewed item (estimate 70–90 actions for formula-level English).

Fixed rules follow the wire-contract precedent: a JSON source under `ve/english_grammar/`, one file per profile,
from which a tool generates Lean modules that are table literals with no theorems, and `--check` keeps them in
step in the commit hook. A rule looks like:

```json
{"tag": "exists.such-that", "lhs": "existential", "act": "exists",
 "rhs": ["there", "is", {"n": "article"}, {"n": "declaration"}, "such", "that", {"n": "formula"}]}
```

Extensions the plain model needs, all listed in 1.3: a terminal-matching relation instead of token equality;
terminal classes; one compiled feature (slot sort); side conditions in meanings; threaded document state. Nothing
found needs context-sensitive rules.

### 2.4 The lexicon leaves the trusted base

Python's `EnglishVocabulary` decides, per symbol, whether the declared wording passes the lint or is replaced by
the quoted fallback (`is classified as "name"`). That policy is long and special-cased. It affects which sentences
are convenient to write, not whether a reading is unique, because uniqueness is decided per sentence. So:

- Python (or anyone) proposes the selected lexicon. It is sent with the request and bound to an identity.
- Lean checks `Lexicon.valid`: every selected wording is the wording declared in the environment or overlay, the
  wording fixed by a profile block, the mechanical wording of a bare identifier, or the quoted fallback; arities
  and holes match the declaration.
- A producer can therefore only choose among honest wordings of the same symbol. The legend already shows the
  selected wording per symbol; it remains the reader's reference.

Declared templates remain trusted semantic declarations, as today: Lean cannot tell that `disowns` was declared to
mean `owns`.

### 2.5 Statement layers and display text

Statement-layer forms (1.4) are sentences with a fixed frame around formulas, names and numbers. They fit the same
data model: frame rules plus the formula nonterminal, with actions that build the layer's object. Moving a layer
onto the engine replaces its private splitter or enumerator by whole-sentence derivation uniqueness. That is a
behaviour change wherever the private check was weaker, so each layer is its own step with its own delta report
(S6). Dates, decimals, percentages and unit affixes become terminal classes of the lexer (ISO date, `D Month YYYY`,
decimal, labelled amount); the calendar range and unit display injectivity stay as the existing static checks.
Semantic filters that are not grammar (unit typing, tense bound to a manifest, role checks) stay as side
conditions or downstream checks. Display-only text has no reading check today; S7 can give each frame a rule and
require the per-output check of 3.5 before the text is labelled a checked reading.

## 3. Lean objects and theorem statements

New modules only. Names avoid primes; no function is declared with a totality escape. `S` abbreviates the start
symbol `.n G.start`.

### 3.1 Tokens, grammar, derivations (`VE/Grammar/Basic.lean`, `Derives.lean`)

```lean
inductive Tok where
  | word (text : String) (initial : Bool)   -- `initial`: first word of a sentence, or after a conclusion marker
  | quoted (name : String)                  -- "identifier", exact bytes
  | label (letter : String) (index : Nat)   -- S1, S2, …
  | numeral (value : Int)                   -- canonical decimal
  | punct (text : String)                   -- , ; : ( ) [ ] + - * and the list markers

inductive Terminal where
  | kw (s : String)        -- structure word: exact, or capitalised when `initial`
  | content (s : String)   -- vocabulary word: equal after case folding
  | exact (t : Tok)        -- punctuation, a quoted identifier, a capitalised constant spelling
  | cls (c : TokClass)     -- finite list: any numeral, a coefficient, a label of a given letter

def Terminal.accepts : Terminal → Tok → Bool

inductive Sym where | t (a : Terminal) | n (A : Nat)
structure Rule where (lhs : Nat) (rhs : List Sym) (act : Nat) (tag : String)
structure Grammar where (rules : Array Rule) (start : Nat) (rank : Array Nat)

/-- No empty rule; `rank` strictly decreases from a left-hand side to a leading nonterminal (so no left
recursion and no unit cycle); no rule mentions the sentence terminator. Linear in the grammar. -/
def Grammar.wf (G : Grammar) : Bool

inductive Tree where | leaf (tok : Tok) | node (rule : Nat) (kids : List Tree)
def Tree.yield : Tree → List Tok
def Tree.derives (G : Grammar) : Sym → Tree → Bool            -- the grammar relation, as a checking function
def Derives (G : Grammar) (X : Sym) (w : List Tok) (t : Tree) : Prop := t.derives G X = true ∧ t.yield = w
```

### 3.2 Parser soundness and completeness (`Table.lean`, `TableProofs.lean`)

```lean
/-- Up to `cap` derivations of the start symbol over `w`; `none` when the work budget is exhausted. -/
def parse (G : Grammar) (cap budget : Nat) (w : Array Tok) : Option (List Tree)

theorem parse_sound    : parse G cap b w = some ts → t ∈ ts → Derives G S w.toList t
theorem parse_nodup    : parse G cap b w = some ts → ts.Nodup
theorem parse_complete : G.wf = true → parse G cap b w = some ts → ts.length < cap →
                         Derives G S w.toList t → t ∈ ts
theorem parse_adequate : G.wf = true → ∃ b0, ∀ b, b0 ≤ b → (parse G cap b w).isSome = true

inductive Verdict where | none | one (t : Tree) | many (t u : Tree)
def decide (G : Grammar) (budget : Nat) (w : Array Tok) : Option Verdict      -- `parse` with cap 2

theorem decide_one  : G.wf = true → decide G b w = some (.one t) →
                      Derives G S w.toList t ∧ ∀ u, Derives G S w.toList u → u = t
theorem decide_none : G.wf = true → decide G b w = some .none → ∀ u, ¬ Derives G S w.toList u
theorem decide_many : decide G b w = some (.many t u) →
                      Derives G S w.toList t ∧ Derives G S w.toList u ∧ t ≠ u
```

These are P2 and P3 of the verification contract for an independent grammar relation, with the budget rule of that
contract: completeness within the budget, an explicit resource outcome outside it, and `parse_adequate` to exclude
a reject-everything parser. `parse_sound` and `decide_many` hold because `parse` re-checks each returned tree with
`Tree.derives`; they do not depend on the table invariant. **The one hard theorem is `parse_complete`.**

### 3.3 Meaning and its totality (`Meaning.lean`, `VE/EnglishGrammar/Actions.lean`)

```lean
inductive Reject where        -- declared side conditions; each has a fixed public code
  | unboundReference | shadowedName | sortMismatch | markerDepth | nestingLimit | numeralBound
  | pronounUnresolved | blockedWording (id : String)      -- the list is closed in S0 from the 49 sites

inductive Ty where | formula | term | intTerm | declaration | guard | relative | sentence   -- and a few more
def Sem : Ty → Type           -- Sem .formula = Scope → Nat → Except Reject Formula   (scope stack, list depth)
                              -- Sem .term    = Scope → Except Reject Term
structure Action where (args : List Ty) (out : Ty) (run : Args args → Sem out)
def Grammar.typed (G : Grammar) (ty : Nat → Ty) (acts : Array Action) : Bool   -- each rule's action fits both sides
def Tree.sem (G) (ty) (acts) : (X : Sym) → Tree → Option (SemOf ty X)

theorem sem_total : G.typed ty acts = true → t.derives G X = true → (t.sem G ty acts X).isSome = true

structure DState where (referents : List String) (binderSeen : Bool)           -- state of the `it` rule
def meaning (G) (ty) (acts) (st : DState) (t : Tree) : Except Reject (Formula × Bool × DState)
```

`sem_total` is the totality statement: under the decidable typing check, a derivation never lacks a meaning for an
internal reason. It either denotes a formula or is rejected with a declared code. The `Bool` is the conclusion mark.

### 3.4 The one-reading decision (`Reading.lean`)

```lean
def OneReading (G) (ty) (acts) (st : DState) (w : List Tok) (A : Formula) : Prop :=
  ∃ t, Derives G S w t ∧ (∀ u, Derives G S w u → u = t) ∧ ∃ c st2, meaning G ty acts st t = .ok (A, c, st2)

inductive Outcome where
  | ok (A : Formula) (conclusion : Bool) | noDerivation | ambiguous (t u : Tree) | rejected (r : Reject) | budget
def readSentence (G) (ty) (acts) (st : DState) (b : Nat) (w : Array Tok) : Outcome × DState

theorem read_sound    : G.wf = true → G.typed ty acts = true →
    (readSentence G ty acts st b w).1 = .ok A c → OneReading G ty acts st w.toList A
theorem read_complete : G.wf = true → G.typed ty acts = true → OneReading G ty acts st w.toList A →
    (∃ c, (readSentence G ty acts st b w).1 = .ok A c) ∨ (readSentence G ty acts st b w).1 = .budget

/-- Translation mode: the meanings of all derivations, when the list is below the cap. -/
theorem readings_exact : G.wf = true → G.typed ty acts = true → parse G cap b w = some ts → ts.length < cap →
    (A ∈ readingSet G ty acts st ts ↔
       ∃ t c st2, Derives G S w.toList t ∧ meaning G ty acts st t = .ok (A, c, st2))
theorem one_reading_single : OneReading G ty acts st w A →
    (∃ t c st2, Derives G S w t ∧ meaning G ty acts st t = .ok (B, c, st2)) → B = A
```

`one_reading_single` is the link asked for in the direction: one derivation implies a one-element meaning set. The
converse is false, which is why authoring keeps the stricter criterion (section 0, change 2). When the list reaches
the cap, translation mode reports an incomplete set, never a complete one.

### 3.5 The English instance, the render round trip, conservativity (`VE/EnglishGrammar/*`)

```lean
structure Lexicon where …     -- per sort: noun, letter; per predicate: wording, negative, aliases;
                              -- per constant: spellings
def Lexicon.valid (E : Environment) (O : Overlay) (L : Lexicon) : Bool          -- section 2.4
def fixedRules (profiles : List String) : Array Rule                            -- generated table literals
def lexRules (E : Environment) (L : Lexicon) : Array Rule                       -- wordings, nouns, spellings
def grammar (E : Environment) (L : Lexicon) : Grammar
def lex : String → Except Reject (Array (Array Tok))                            -- sentences of tokens
def read (E) (O) (L) (b : Nat) (s : String) : DocOutcome
  -- checks Lexicon.valid, wf and typed (else `invalidGrammar`), folds readSentence, then `Formula.check`

def EnglishOneReading (E) (L) (s : String) (As : List Formula) : Prop :=
  ∃ sents, lex s = .ok sents ∧ DocOneReading (grammar E L) sents As ∧ ∀ A ∈ As, A.check E [] = true

theorem read_ok : read E O L b s = .ok As marks → EnglishOneReading E L s As

def checkRendering (E) (O) (L) (b : Nat) (As : List Formula) (s : String) : Bool   -- `read … s` returns exactly `As`
theorem checked_rendering : checkRendering E O L b As s = true → EnglishOneReading E L s As

/-- Adding rules (a profile, a predicate, a wording) never changes an accepted sentence's formula:
the sentence keeps its reading or becomes visibly ambiguous. -/
theorem extension_safe : Embeds G G2 → OneReading G ty acts st w A →
    OneReading G2 ty2 acts st w A ∨ ∃ t u, Derives G2 S w t ∧ Derives G2 S w u ∧ t ≠ u
```

- **Render round trip.** `checked_rendering` is the theorem: any text that passes the check has exactly one
  derivation, and that derivation means the rendered formulas. It follows directly from `read_ok`. It covers every
  profile and both renderers (Python's `render_english` today, a Lean renderer later), because the renderer is an
  untrusted producer. It does **not** say the renderer always succeeds; today that is also a run-time failure
  ("No writable English form passed the one-reading check").
- **Conservativity** has three parts, and only the first is a theorem:
  1. `extension_safe` (Lean): growth of the grammar cannot silently change a meaning.
  2. Replay gate (executed, sections 5 and 6): every sealed corpus item that Python accepts today gets the same
     formulas, canonical text and identities from Lean; every item rejected today is rejected, in the mapped class.
  3. By construction: no existing Lean module, wire form, canonical text or identity is edited.
- **Lexer.** `lex` is a definition, so string-level determinism is immediate. No lexer theorem is needed for the
  statements above. A lexing round trip for renderer output is needed only for 3.6.

### 3.6 Second tier: static theorems (later, S7)

`core_embeds`: for an `Admitted` lexicon, the W7 trees and the generic derivations over the core rules correspond
one to one, with equal yields and meanings. Then `checked_parse_render` transfers: for vocabularies passing
`admissible`, the core renderer's output always passes `checkRendering`. W7's files are not edited. Extending the
static tier to more constructs remains optional work whose absence no longer weakens the per-sentence guarantee.

## 4. Python's role and the wire

- **New service mode `english.read`.** Request: environment, overlay, selected lexicon, source text, mode
  (`authoring` or `translation`), cap. Response: status (`one`, `none`, `many`, `rejected`, `budget`,
  `invalidGrammar`), formulas in wire form, canonical strict text, conclusion marks, the derivation as rule tags
  with token spans, and for `many` the two witness trees. The service caches the instantiated grammar by
  environment and lexicon identity. A second mode, `english.grammar`, exports the instantiated grammar as JSON.
- **Shadow, then authority**, through the existing dispatch (`ve/backends/dispatch.py`, `VE_AUTHORITY_OVERRIDES`).
  In shadow, Python's result is returned and every difference is logged. Under Lean authority Python follows the
  `_parse_lean` precedent: Lean decides acceptance; Python's own reading must equal Lean's formulas and canonical
  text, and a difference fails closed as `CheckerUnavailable`.
- **What Python keeps:** spans and messages for the editor, nearest-wording suggestions, `ve propose`, the
  vocabulary policy as lexicon producer, rendering as a producer whose output Lean checks, caching, and the IDE's
  rephrasing flows. The `many` witnesses and translation-mode sets give the IDE exact alternatives to phrase.
- **Python's grammar is generated from Lean's.** After S5 the Lark grammar used for editor diagnostics and
  constrained decoding is a mechanical conversion of the `english.grammar` export, and the `grammar_hook`s are
  deleted. Before that, S2 adds a structural parity check: for each corpus environment, Python's generated grammar
  and Lean's are compared as rule sets after a mechanical word-level translation. Equal rule sets give evidence of
  equal languages that does not depend on sampling sentences.
- **Lexicon identity.** Records gain a `lexicon_id` as an additive field. No existing identity changes; S0
  confirms this against the wire freeze.

## 5. Migration: stages, gates, budgets

| Stage | Content | Gate | Effort |
|---|---|---|---|
| S0 Measure and seal | run the inventory (below); seal the corpus; baseline timings | G0: formula-level English fits the model with only the extensions of 2.3, or the misfits are reviewed | 4–5 d |
| S1a Prototype | executable `parse` on tokens, no proofs; timing on the corpus and on synthetic worst cases | G1a: budgets below are met, or the table strategy changes before any proof is written | 4 d |
| S1b Generic proofs | 3.1–3.4 theorems; audit, frozen-inventory and layer entries | G1b: audit clean, standard axioms only | 2–3 w |
| S2 English instance | lexer, fixed-rule JSON and generator, `lexRules`, actions, `english.read`, shadow wiring; base constructs, contractions, validated negatives, coordination, closure, natural clauses | G2: grammar parity on every corpus environment; zero unexplained differences on the sealed corpus | 2–3 w |
| S3 Formula-level profiles | `order@0`, `data@0` sugar, alternatives guards, risk wordings and blocked forms, modal atoms | G3: as G2, per profile, with a delta report | 1–1.5 w |
| S4 Shadow | default-on shadow; nightly generators | G4: 14 consecutive clean days; every difference dispositioned | 1 w + window |
| S5 Authority | `english.admission` authority becomes Lean; renderer outputs checked by Lean; Lark leaves the admission path; Python's grammar generated from Lean's | G5: support-matrix diff empty for S and R cells; manifest and trust rows updated | 3–5 d |
| S6 Statement layers | one layer per step, in the order of 1.4 | per layer: delta report reviewed; changed rejections decided by the DRI | about 1 w each |
| S7 Later, each a separate decision | static tier (3.6); meaning-set criterion for authoring; retiring `EnglishParser`; display-only text; P1–P3 for the strict surface on the same engine | — | — |

**S0 inventory deliverable** (`docs/spec/english-lean-measured.md`): per corpus environment, the number of rules,
nonterminals and the longest right-hand side; the token-length histogram of corpus sentences; confirmation that
the expanded grammar has no empty rule and no left recursion; every regex terminal that is not a word sequence;
the classification of the 49 rejection sites; Earley time per sentence; and character-versus-token probes (7.2).

**Shadow corpus (sealed with hashes in S0).** Every English text in the test suite (the 37 files of 1.6); the
conformance generators (85,000 round-trip ASTs with their renderings, 12,750 Earley texts, 850 documents, 6,757
mixed texts, 1,220 natural statements); every use-case document and rendering; the pilot documents pinned by
`bench/PROFILE-GOLDEN.json` (they live in sibling checkouts, so S0 copies or pins them); the rejection fixtures,
including the constructed two-derivation cases of `tests/test_english_unambiguity.py`. The existing 85,000-pair
Python–W7 differential gains the new reader as a third arm: on the 57,765 core texts all three must agree.

**Comparison rule.** Accepted by both: equal formulas (wire form), equal canonical strict text, equal document
identity, equal conclusion marks. Rejected by both: classes map as `AmbiguousDerivation` ↔ `many`; `SyntaxError` ↔
`none` or a syntactic side condition; `UnknownSymbol` and `TypeMismatch` ↔ the corresponding `Reject`. Wall-clock
`ResourceLimit` outcomes are excluded and listed. Anything else is a difference. A difference is closed only as a
Lean fix, a Python fix, or a recorded product decision under SEMANTICS-MIGRATION-PLAN 2.3 (made in Python first,
with a release note, so that shadow stays exact).

**Performance budgets** (targets; none is measured yet):

| Quantity | Budget | Basis |
|---|---|---|
| Document size | 64 KiB source, 10,000 normalised characters | today's limits, unchanged |
| Sentence length | no separate cap below the document limit; 150 tokens is the design point | longest admitted sentence on record |
| Grammar size | at most 8,192 rules after instantiation; fixed part at most 400 | 256 predicates × 6 plus constants plus fixed |
| Work budget | a deterministic step count, set in S1a at 10× the largest corpus need | replaces the 30-second wall clock |
| Latency, warm service | corpus sentence p95 ≤ 20 ms; 150-token sentence ≤ 50 ms; BlueDot document ≤ 1 s | Python today: 95 ms and 1.04 s |
| Grammar instantiation | ≤ 100 ms per environment, cached by identity | one-shot Lean medians of 47–152 ms |
| Lean build | generated rule modules add ≤ 60 s to `lake build` | to be measured in S2 |

Stop rule at G1a: if the prototype misses a latency budget by more than 5× on the corpus, add first-token and
left-corner filtering and re-measure; if it still misses, stop and re-plan with option G before proving anything.

## 6. Trusted base and the trust map

**What must be trusted for "this text has exactly one reading, and it is A", after S5:**

| Item | Size (estimate) | Kind |
|---|---|---|
| `Tree.derives`, `Grammar`, `Terminal.accepts` | about 80 lines | definition: what a derivation is |
| Fixed rules (generated table literals; JSON source) | 150–250 rules, formula level | data |
| `lexRules`, `Lexicon.valid` | about 200 lines | definition: how wordings become rules |
| `lex` | about 150 lines | definition: what the tokens of a text are |
| Action library, `meaning` | 70–90 actions, about 600 lines | definition: what a derivation means |
| Theorem statements of 3.2–3.5 | — | reviewed statements |
| Lean kernel, compiler, runtime; JSON decoding; service glue; the Python adapter that carries the text and shows the answer | as for every Lean-decided unit | existing boundary |
| Declared templates; the reader's understanding of them | — | unchanged: semantic declarations |

**No longer trusted for this claim:** `EnglishParser` (about 750 lines), source normalisation, `english_lark_grammar`
and the hooks, the vocabulary lint (about 300 lines plus the printer lint), the audit and registry modules, Lark's
Earley implementation, Python's `re`, and the parser implementation in Lean (it is proved). The base goes from
roughly 2,000 lines of Python (*static*) plus a third-party parser and regex engine to roughly 1,000 lines of Lean
definitions and 150–250 rules of data, with one proved parser.

**Rows for the trust map** (to add when `docs/TRUST-MAP.md` lands; until then they go in the assurance manifest):

- `english.admission`: authority `python` → `lean` at S5. `trusted` changes from `python:implementation`,
  `python:surface` to `lean:kernel`, `lean:compiler`, `lean:decoders`, `lean:runner-glue`,
  `lean:english-definitions` (lexer, rules, actions) and `python:backend-adapter`.
- `assurance` stays `experimental` until the 3.2–3.5 theorems are in the audit inventory. After that the
  one-reading claim may be labelled as proved **relative to the grammar definitions**. Until then records say
  "Lean-executed, uniqueness proof pending", never "Lean-verified".
- New row, definitions: the English grammar data and action library, with their identities in a lock file.
- New row, producers: vocabulary policy, renderer, Python parser. Untrusted; outputs checked by Lean.
- Unchanged rows: intent and source fidelity; templates as declarations; display of text not yet covered (1.4,
  last row), which keeps the label of trusted display.
- Statement layers keep their current rows until their S6 step.

## 7. Open questions and risks

1. **Proof effort for `parse_complete`.** No generic parser proof exists in this code base, and there is no
   Mathlib. The estimate of 2–3 weeks could double. Mitigations: soundness and the ambiguous verdict are
   self-certifying and need no table proof; the algorithm is chosen for a short proof; the discourse proof is a
   worked model. If the proof slips, shadow can still run on the executable, with the honest label of section 6.
2. **Characters versus tokens.** Lark's scannerless matching can split inside words; a word lexer cannot. Texts
   may exist that Python rejects as ambiguous and Lean accepts, or the reverse. S0 probes for them; each class
   needs a decision. The token-level definition is the principled one, but changing a rejection is a product
   decision.
3. **Procedural rejections with no grammatical counterpart.** The "extends existing wording" check, ordered
   commitment to a keyword, and some blocked wordings reject texts that the generated grammar may derive. Each
   becomes a side condition, a rule change, or an accepted difference. The count is unknown until S0.
4. **Today's two artefacts may already disagree (G1).** Shadow may show sentences whose hand-parsed formula is not
   the meaning of their unique derivation. Those are present-day defects and are fixed in Python first.
5. **Meanings are code.** The action library is hand-written and reviewed, not generated. An error there is a wrong
   meaning with a correct uniqueness proof. Mitigation: the corpus replay, the three-way differential on core
   texts, and the per-output render check, which exercises parse and meaning together on every displayed sentence.
6. **Well-formedness of instantiated grammars is checked at run time**, not proved for all environments. A lexicon
   that makes the grammar ill-formed is rejected as `invalidGrammar`. A theorem that `lexRules` preserves
   well-formedness is desirable and not scheduled.
7. **Performance is unmeasured.** The worst case of the table parser is cubic in sentence length. The design
   relies on keyword-led rules and first-word indexing. A deterministic budget may reject a pathological document
   that Python's 30-second limit would accept.
8. **Statement layers will show real differences.** Several have no whole-sentence check today; `report_english`
   treats an ambiguous embedded statement as no derivation. Moving them onto the engine will reject some texts
   accepted today. That is the point of the lead's decision, but each case needs review and a release note.
9. **The `it` rule is kept exactly**, although PLAN-ZERO-TRAINING calls it insufficient and the discourse profile
   supersedes it. This plan does not improve discourse; it stops the rule from being Python-only.
10. **Marked conclusions** are still accepted or rejected by a bounded proof search outside the grammar (a recorded
    conflation). Out of scope here.
11. **Source of truth for fixed rules.** JSON with generated Lean literals (recommended, as for wire contracts) or
    Lean-first with a JSON export. Reviewers should pick one before S2.
12. **Non-ASCII input.** English sources are UTF-8. The lexer must define case folding beyond ASCII; the discourse
    lexer already has such a table (`foldChar`). Whether to share it or keep two is undecided.
13. **Frozen files and layers.** The new modules need frozen-inventory lines, audit lines and a layer assignment
    (proposed: `VE.Grammar.*` and `VE.EnglishGrammar.*` in layer 3, the service mode in layer 4). A bridge to W7
    (3.6) needs a layer exception like the existing discourse ones.
14. **Display-only English stays unverified** until S7. A reader of a rights unit or a status sentence still relies
    on fixed Python frames.
15. **Two English grammars remain in Lean** for a time: this one and the discourse grammar. Re-hosting discourse on
    the generic engine is possible and not planned.
16. **Zero-training English is not solved by this.** Arbitrary English still has zero derivations. The plan gives
    the IDE exact witness pairs and reading sets to drive rephrasing; coverage remains the catalogue's job.

## 8. Effort and order

Formula-level English reaches Lean authority in about 8–11 weeks elapsed, including the 14-day shadow window:
S0 (1 week), S1 (3–4 weeks, with S2's Python and JSON work in parallel once S1a passes), S2–S3 (3–4 weeks), S4–S5
(3 weeks). S6 is about one week per layer and can run two layers at a time after S5. The proof work (S1b) is the
largest uncertainty; the largest unknown in scope is the number of differences S0 and S4 uncover.

Hard Lean (S1b, actions) goes to the Lean implementer; Python, generator and harness work to the Python
implementer; the theorem statements of section 3 get a statement review before S1b starts, as the wire-contract
statement spec did.
