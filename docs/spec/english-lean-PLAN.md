# English in Lean: the grammar as data, one proved all-derivations parser (PLAN)

**Status:** plan only, draft 2, 2026-10-03, branch `design/english-lean` from `main` at `a093a14d`. No code or
proofs change with this document. It was written from reading the sources; **nothing was built or run** (this
session could execute neither Python nor Lean). Every number below is a figure from a committed report (cited), a
count made by reading the source (marked *static*), or a figure from the review's read-only probe (marked
*probe*). Stage S0 replaces the static and probe figures by measured ones. `file:line` references were read on
2026-10-03 and must be re-read at each step.

Draft 1 had its two frontier reviews on 2026-10-03 (`manage-agents/debates/design-english-lean/{fable,astra}.md`,
converged after round 3). The verdict: the architecture stands; revise to draft 2, then build through the staged
gates. Draft 2 applies the converged edits, which section 9 lists, and makes no other change. The DRI checks the
text against that list; there is no second full review. S0 and S1a start on draft 2. The item-1 statement spec is
[english-lean.md](english-lean.md); its statements are reviewed before any S1b proof work.

That statement review took place on 2026-10-03 (`manage-agents/debates/english-lean-spec/{fable,astra}.md`,
converged after round 3). The verdict: FIX, then build. The architecture, the scope and the frozen contracts
stand. The corrections are applied in draft 2 of the statement spec. The ones that touch this plan are applied
here and listed in section 10; nothing else in this plan changed. The DRI checks the edits; only a change of
meaning returns to the reviewers. S0 and S1a continue. S1b waits for the corrected statements, for their
elaboration in S1a and for G1a.

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
6. **The selected lexicon is input data that Lean validates and identifies.** The one-reading guarantee is stated
   for that validated, identified lexicon. Choosing among honest wordings is not meaning-neutral, so the
   vocabulary lint does not simply leave the trusted base: its meaning-relevant checks move into the Lean
   relation, and the rest stay a Python check until the DRI decides (2.4).
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
| `data@0` attribute sugar | per functional total binary relation: 1 alternative (`the R of t is t`), and 1 more per unary predicate on its value sort (`the R of t is P`, :1907–:1912). The second is a product | same |
| `alternatives@0` guards | about 10 alternatives, 1 extra reference form | same |
| Natural clauses (`some`, `no`, `every ADJ NOUN`) | 14 alternatives | `_natural_grammar` (:1972) |
| Risk wordings | 4 fixed wordings, 2 fixed negatives | `EnglishVocabulary` |
| Per predicate | up to 3 rules per wording (clause, subject relative, object relative), for the positive wording, the validated negative and input aliases | generated |
| Per constant, per sort | up to 3 spellings; 1 noun (10 declaration and 10 reference forms through fixed rules) | generated |
| Bounds | `MAX_PREDICATES` 256, `MAX_SORTS` 32: at most about 1,600 wording rules. The attribute-property product is not linear: it peaks at 128 × 128 = 16,384 alternatives (*probe*: a validated `data@0` environment with 128 functional total relations and 128 compatible properties gave 16,384 such alternatives and 16,771 atom alternatives in all) | `ve/limits.py`; review, Astra round 1 |
| Vocabulary policy | 13 unary and 25 binary idioms, 9 complement and active-phrase patterns, about 18 lint codes | `english_vocabulary.py`, `printer.py`, `english.py` |
| Advisory lexicon | 72,780 OEWN entries, used only by `ve propose`, never by the parser | `ve/lexicon/` |

The largest committed environment has 48 `verbalisation` entries (`usecases/eligibility`, *static*). The grammar
has no empty production once `?` and `*` are expanded, and no left recursion (*static*; lists and guards are
right-recursive or fixed-arity). No committed environment comes near the attribute-property product, so counts on
the corpus would not show it. S0 therefore also measures synthetic limit environments (section 5).

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
| H. Span-length-ordered table | hold in reserve, before G | fills entries by increasing span length, so it needs only "no empty rule, no unit cycle" and admits left recursion; the cap invariant and the statements of 3.2 are unchanged. The first fallback if a wording needs left recursion |
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
  function is total by structural recursion on the row and the rule list, with no fuel.
  - *Cap invariant.* Every entry is either complete (it holds every derivation of its nonterminal over its span)
    or holds exactly `cap` trees. Truncation to `cap` preserves this. `parse_complete` is proved from it (3.2).
  - *Rule-suffix memoisation.* A second table holds, for each rule suffix and start position, up to `cap` matches
    of that suffix per end position, under the same invariant. A suffix is then matched once per start position,
    not once per way of splitting the span. Without this the cost is not cubic: a cap on complete entries does
    not bound the enumeration of splits across a long right-hand side.
  - *Shared witnesses.* A stored tree refers to the stored trees of its parts. Nothing is copied.
  - *Indexing.* A keyword-led rule is indexed by its first word. Predicate wording rules start with a term hole
    (`english.py:1915–:1922`), so first-word indexing does not reach the bulk of the grammar. Indexing a hole-led
    rule by the first terminal after the hole is an optimisation that S1a measures. No cost claim rests on it.
- **Three verdicts with witnesses.** With `cap = 2` the result is none, one tree, or two distinct trees. The two
  trees are re-checked by the checking function, so an "ambiguous" verdict is self-certifying and gives the editor
  the pair that Python prints today.
- **Documents.** The lexer splits sentences at the terminator token, and no rule may mention that token (a check
  of the English instance, run beside the generic well-formedness check), so a document's derivations are
  exactly the lists of its sentences' derivations. Cost is linear in the
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

**One product is factored.** Python's grammar has one alternative for each pair of a functional total relation and
a unary predicate on its value sort (1.2). Lean's grammar has one rule per relation, over a property nonterminal
of the value sort, and one rule per unary predicate under the nonterminal of its sort. Each pair still has exactly
one derivation, and the size is the sum of the two counts, not their product. The correspondence is part of the
tree correspondence of section 4, and S0 measures it on synthetic limit environments. If the factoring turns out
not to be one-to-one, the DRI reviews a new resource limit instead.

### 2.4 The lexicon: validated and identified, not yet out of the trusted base

Python's `EnglishVocabulary` decides, per symbol, whether the declared wording passes the lint or is replaced by
the quoted fallback (`is classified as "name"`). That policy is long and special-cased. Draft 1 said that it only
affects which sentences are convenient to write. **That claim is withdrawn.** Choosing among honest wordings is
not meaning-neutral. When two predicates declare the same template, Python demotes both to the fallback
(`english.py:263`, `:368`); a producer free to keep the template for either one would make the same text read
uniquely as `P(a, b)` under one lexicon and as `Q(a, b)` under another. A negative wording is admitted today only
if it equals `negative_template` of the positive one (`english.py:384`, `english_vocabulary.py:58`). So:

- Python (or anyone) proposes the selected lexicon. It is sent with the request and bound to an identity.
- Lean checks `Lexicon.valid`, three conditions:
  1. every selected wording is the wording declared in the environment or overlay, the wording fixed by a profile
     block, the mechanical wording of a bare identifier, or the quoted fallback; arities and holes match the
     declaration;
  2. no selected wording, negative or alias equals, by `wording_key`, a declared wording, negative, alias or
     profile wording of another symbol. The condition names sort nouns and constant spellings as well as
     predicate wordings, on both sides of the comparison (statement spec 2.9, V4);
  3. a selected negative equals a Lean `negativeTemplate` of the selected wording (a port of
     `negative_template`, listed in section 6), or is a negative that a profile block fixes (statement spec
     2.9, V5; accepted by the statement review).
- **The guarantee is per validated, identified lexicon.** Lean proves P1 for a fixed lexicon (3.5). It does not
  prove that two valid lexicons give a text the same reading: sort nouns and constant spellings are selected too.
  Only a proved theorem that quantifies over two valid lexicons would restore draft 1's claim. None is scheduled.
- **S0 sorts every lint code** into one of three classes: subsumed by per-sentence uniqueness; meaning-relevant,
  and ported into `valid`; or reader protection, which stays a retained Python check until the DRI decides.
  Retiring `EnglishParser` (S7) is gated on that decision.
- **Lexicon mutation replay is an empirical gate** (section 5): under a changed valid lexicon a corpus text may
  lose its reading, but it must never get a different formula. This is evidence, not proof.

The legend already shows the selected wording per symbol; it remains the reader's reference. Declared templates
remain trusted semantic declarations, as today: Lean cannot tell that `disowns` was declared to mean `owns`.

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

The blocks below are sketches. The statement spec ([english-lean.md](english-lean.md), section 5) holds the
exact statements and governs where the two differ; its section 11.1 lists each difference. Four differences
come from the statement review. The engine of 3.1 to 3.4, with `Embeds` and `extension_safe`, is generic in the
token type, the terminal type and the matching function. `Tok`, `Terminal`, `Terminal.accepts` and the
condition that no rule mentions the terminator belong to the English instance, and `read` checks that
condition. The start symbol of `grammar E L` is proved to have the type `sentence`, because the typing check
does not say so. An English instance of `extension_safe` is deferred until its premise has a reviewed
definition.

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
recursion and no unit cycle). Linear in the grammar. That no rule mentions the sentence terminator is a
separate check of the English instance. -/
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

`parse_complete` is proved from the **cap invariant** of the table (2.2): every entry, for a nonterminal or for a
rule suffix, is a duplicate-free list of derivations of its span, and it is either complete or of length exactly
`cap`. An entry shorter than `cap` is therefore complete, which is the hypothesis `ts.length < cap`.

**Cost.** With rule-suffix memoisation and shared witnesses, a sentence of `n` tokens over a grammar whose
right-hand sides have total length `|G|` takes at most a constant times `|G| · n³ · cap²` steps, and the tables
hold at most `|G| · n² · cap` references. Without the memoisation neither bound holds. These are bounds on the
specified algorithm; S1a measures steps, peak memory and latency (section 5).

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
/-- One derivation, and its complete result: the formula, the conclusion mark and the successor state. -/
def OneReading (G) (ty) (acts) (st : DState) (w : List Tok) (A : Formula) (c : Bool) (st2 : DState) : Prop :=
  ∃ t, Derives G S w t ∧ (∀ u, Derives G S w u → u = t) ∧ meaning G ty acts st t = .ok (A, c, st2)

/-- A document: its sentences read in order, the state threaded. Every formula and mark is exposed. -/
def DocOneReading (G) (ty) (acts) : DState → List (List Tok) → List (Formula × Bool) → DState → Prop
  | st, [], [], st2 => st2 = st
  | st, w :: ws, (A, c) :: rs, st2 =>
      ∃ st1, OneReading G ty acts st w A c st1 ∧ DocOneReading G ty acts st1 ws rs st2
  | _, _, _, _ => False

inductive Outcome where
  | ok (A : Formula) (conclusion : Bool) | noDerivation | ambiguous (t u : Tree) | rejected (r : Reject) | budget
def readSentence (G) (ty) (acts) (st : DState) (b : Nat) (w : Array Tok) : Outcome × DState
def readDocument (G) (ty) (acts) (st : DState) (b : Nat) (ws : List (Array Tok)) : DocOutcome × DState

theorem read_sound    : G.wf = true → G.typed ty acts = true →
    readSentence G ty acts st b w = (.ok A c, st2) → OneReading G ty acts st w.toList A c st2
theorem read_complete : G.wf = true → G.typed ty acts = true → OneReading G ty acts st w.toList A c st2 →
    readSentence G ty acts st b w = (.ok A c, st2) ∨ (readSentence G ty acts st b w).1 = .budget
theorem doc_sound     : G.wf = true → G.typed ty acts = true →
    readDocument G ty acts st b ws = (.ok rs, st2) → DocOneReading G ty acts st (ws.map (·.toList)) rs st2
theorem doc_complete  : G.wf = true → G.typed ty acts = true →
    DocOneReading G ty acts st (ws.map (·.toList)) rs st2 →
    readDocument G ty acts st b ws = (.ok rs, st2) ∨ ∃ i, (readDocument G ty acts st b ws).1 = .stopped i .budget

/-- Translation mode: the complete results of all derivations, when the list is below the cap. -/
theorem readings_exact : G.wf = true → G.typed ty acts = true → parse G cap b w = some ts → ts.length < cap →
    (r ∈ readingSet G ty acts st ts ↔ ∃ t, Derives G S w.toList t ∧ meaning G ty acts st t = .ok r)
theorem one_reading_single : OneReading G ty acts st w A c st2 →
    Derives G S w t → meaning G ty acts st t = .ok (B, d, st3) → B = A ∧ d = c ∧ st3 = st2
```

`OneReading` no longer hides the conclusion mark and the successor state behind an existential, and
`DocOneReading` is the fold that the document theorems are stated against: formulas, marks and state transitions
all correspond. `one_reading_single` is the link asked for in the direction: one derivation implies a one-element
meaning set. The converse is false, which is why authoring keeps the stricter criterion (section 0, change 2).
When the parser's list of trees reaches the cap, translation mode reports an incomplete set, never a complete
one. The count is taken on the trees, before meanings are computed. Translation mode reads one sentence.

### 3.5 The English instance, the render round trip, conservativity (`VE/EnglishGrammar/*`)

```lean
structure Lexicon where …     -- per sort: noun, letter; per predicate: wording, negative, aliases;
                              -- per constant: spellings
def wordingKey : String → String                                                -- port of `wording_key`
def negativeTemplate (wording : String) (arity : Nat) : Option String           -- port of `negative_template`
def Lexicon.valid (E : Environment) (O : Overlay) (L : Lexicon) : Bool          -- section 2.4, conditions 1 to 3
def fixedRules (profiles : List String) : Array Rule                            -- generated table literals
def lexRules (E : Environment) (L : Lexicon) : Array Rule                       -- wordings, nouns, spellings
def grammar (E : Environment) (L : Lexicon) : Grammar
def lex : String → Except Reject (Array (Array Tok))                            -- sentences of tokens
def read (E) (O) (L) (b : Nat) (s : String) : DocOutcome
  -- checks Lexicon.valid, wf, the terminator condition and typed (else `invalidGrammar`), folds readSentence,
  -- then `Formula.check`

/-- `rs` lists each sentence's formula with its conclusion mark. The lexicon's validity is part of the claim. -/
def EnglishOneReading (E) (O) (L) (s : String) (rs : List (Formula × Bool)) : Prop :=
  L.valid E O = true ∧
  ∃ sents st2, lex s = .ok sents ∧
    DocOneReading (grammar E L) ty acts DState.init (sents.toList.map (·.toList)) rs st2 ∧
    ∀ r ∈ rs, r.1.check E [] = true

theorem read_ok : read E O L b s = .ok rs → EnglishOneReading E O L s rs

/-- P1, for one validated, identified lexicon. It says nothing about a second lexicon. -/
theorem english_reading_unique : EnglishOneReading E O L s rs → EnglishOneReading E O L s rs2 → rs = rs2

def checkRendering (E) (O) (L) (b : Nat) (rs : List (Formula × Bool)) (s : String) : Bool
  -- `read … s` returns exactly `.ok rs`: the formulas and the marks
theorem checked_rendering : checkRendering E O L b rs s = true → EnglishOneReading E O L s rs

/-- An embedding of `G` into `G2` (start symbols `S`, `S2`): a map on trees that is injective, preserves
yields, and preserves every successful meaning under the same initial state: the formula, the conclusion
mark and the successor state. An injective rule map that preserves both sides of each rule, its action
and its types induces one. -/
structure Embeds (G G2) (ty ty2) (acts acts2) (emb : Tree → Tree) : Prop where
  derives   : Derives G S w t → Derives G2 S2 w (emb t)
  injective : emb t = emb u → t = u
  meaning   : Derives G S w t → meaning G ty acts st t = .ok r → meaning G2 ty2 acts2 st (emb t) = .ok r

/-- Adding rules (a profile, a predicate, a wording) never changes an accepted sentence's reading:
the sentence keeps its formula, mark and successor state, or becomes visibly ambiguous. -/
theorem extension_safe : Embeds G G2 ty ty2 acts acts2 emb → OneReading G ty acts st w A c st2 →
    OneReading G2 ty2 acts2 st w A c st2 ∨ ∃ t u, Derives G2 S2 w t ∧ Derives G2 S2 w u ∧ t ≠ u
```

- **Render round trip.** `checked_rendering` is the theorem: any text that passes the check has exactly one
  derivation, and that derivation means the rendered formulas, with their marks. It follows directly from
  `read_ok`. It covers every profile and both renderers (Python's `render_english` today, a Lean renderer later), because the renderer is an
  untrusted producer. It does **not** say the renderer always succeeds; today that is also a run-time failure
  ("No writable English form passed the one-reading check").
- **Conservativity** has three parts, and only the first is a theorem:
  1. `extension_safe` (Lean): growth of the grammar cannot silently change a meaning. Its premise is semantic,
     not only syntactic: `Embeds` must preserve types, actions and successful meanings, with `ty2` and `acts2`
     tied to `ty` and `acts` by the embedding. **Reselecting vocabulary is not an extension.** When an added
     declaration makes the producer select a different wording for an existing symbol, the old rule is gone, no
     embedding exists, and the theorem says nothing. That case is covered only by the mutation replay gate.
  2. Replay gate (executed, sections 5 and 6): every sealed corpus item that Python accepts today gets the same
     formulas, canonical text and identities from Lean; every item rejected today is rejected, in the mapped class.
     This is measured compatibility on the corpus, not universal conservativity.
  3. By construction: no existing Lean module, wire form, canonical text or identity is edited.
- **P1 and the lexicon.** `english_reading_unique` is P1 of the verification contract for a fixed, validated
  lexicon. Independence from the choice of lexicon is not claimed (2.4).
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
  with token spans, and for `many` the two witness trees. Translation mode reads exactly one sentence, from the
  initial state; a longer text is rejected. Its reading set is marked complete exactly when the parser returned
  fewer trees than the cap. The service caches the instantiated grammar by environment and lexicon identity. A
  second mode, `english.grammar`, exports the instantiated grammar as JSON.
- **Evidence is bound to what was decided.** Every response carries the identities of the exact source, the
  environment, the overlay, the selected lexicon, the grammar tables and the version of the reader's
  definitions. That version, `actions_version`, covers the action library and every other trusted definition
  file: tokens and matching, lexer, lexicon validity, rule construction, AST encoding. A lock file hashes each
  file, and the version rises on any change to one. The service computes the identities from the request it
  decided; it does not echo the caller's. A record that cites a reading cites
  all six, and a change to any of them invalidates it.
- **Shadow, then authority**, through the existing dispatch (`ve/backends/dispatch.py`, `VE_AUTHORITY_OVERRIDES`).
  In shadow, Python's result is returned and every difference is logged. Under Lean authority Python follows the
  `_parse_lean` precedent: Lean decides acceptance; Python's own reading must equal Lean's formulas and canonical
  text, and a difference fails closed as `CheckerUnavailable`.
- **What Python keeps:** spans and messages for the editor, nearest-wording suggestions, `ve propose`, the
  vocabulary policy as lexicon producer, rendering as a producer whose output Lean checks, caching, and the IDE's
  rephrasing flows. The `many` witnesses and translation-mode sets give the IDE exact alternatives to phrase.
- **Python's grammar is generated from Lean's.** After S5 the Lark grammar used for editor diagnostics and
  constrained decoding is a mechanical conversion of the `english.grammar` export, and the `grammar_hook`s are
  deleted.
- **Parity before that is derivation parity, not rule-set equality.** The acceptance criterion counts
  derivations, and the factoring of 2.3 makes the two rule sets differ on purpose. S0 defines the **tree
  correspondence** between a Lark derivation and a Lean derivation: how EBNF expansion (`?`, `*`, `+`, inlined
  rules), duplicate productions, overlapping terminals, phrase terminals split into word tokens, and the
  factoring of 2.3 map one to the other. S2 then compares, for each corpus text: the verdict (zero, one or many),
  the formulas, and the witness multiplicity. Equal languages alone do not establish that rejections agree.
  Adversarial lexical cases are part of the corpus. A change that cannot be avoided goes through the delta
  process of section 5.
- **Identities.** Records gain a `lexicon_id`, a grammar-table identity and the version of the reader's
  definitions (`actions_version`) as additive fields. No existing identity changes; S0 confirms this against the wire freeze.

## 5. Migration: stages, gates, budgets

| Stage | Content | Gate | Effort |
|---|---|---|---|
| S0 Measure and seal | run the inventory (below), including synthetic limit environments, the tree correspondence and the lint-code sort; seal the corpus; baseline timings | G0: formula-level English fits the model with only the extensions of 2.3, or the misfits are reviewed; the grammar-size ceiling is set from measurement | 4–5 d |
| S1a Prototype | executable `parse` on tokens with rule-suffix memoisation and shared witnesses, no proofs; generic in the token and terminal types, and run with the draft English tokens; a step counter that charges every rule attempt, failed or not, as well as every combination; steps, peak memory and latency on ordinary inputs, long failing prefixes and highly ambiguous inputs, on the corpus and at limit sizes. It also elaborates the generic definitions and theorem types of the statement spec under Lean 4.24.0, each unproved statement as a definition of type `Prop`, and lists the corrections that elaboration forces; a change of meaning returns to the reviewers | G1a, a pass gate: every budget below is met, or a revision of the budgets or of the strategy is reviewed and then passes measurement. No proof is written before it passes | 4 d |
| S1b Generic proofs | 3.1–3.4 theorems, after the statement review's corrections, their elaboration in S1a and G1a; audit, frozen-inventory and layer entries | G1b: audit clean, standard axioms only | 2–3 w |
| S2 English instance | lexer, fixed-rule JSON and generator, `lexRules`, `Lexicon.valid`, actions, `english.read`, shadow wiring; base constructs, contractions, validated negatives, coordination, closure, natural clauses | G2: derivation parity on every corpus text under the tree correspondence (verdict, formulas, witness multiplicity); the reverse corpus and the lexicon mutation replay clean; zero unexplained differences on the sealed corpus | 2–3 w |
| S3 Formula-level profiles | `order@0`, `data@0` sugar, alternatives guards, risk wordings and blocked forms, modal atoms | G3: as G2, per profile, with a delta report | 1–1.5 w |
| S4 Shadow | default-on shadow; nightly generators with fresh seeds | G4: 14 consecutive clean days, and the fresh-seed volume and coverage targets met; zero undispositioned differences | 1 w + window |
| S5 Authority | `english.admission` authority becomes Lean; renderer outputs checked by Lean; Lark leaves the admission path and stays a logged, non-authoritative comparator until S7; Python's grammar generated from Lean's | G5: support-matrix diff empty for S and R cells; manifest and trust rows updated | 3–5 d |
| S6 Statement layers | one layer per step, in the order of 1.4 | per layer: delta report reviewed; changed rejections decided by the DRI | about 1 w each |
| S7 Later, each a separate decision | static tier (3.6); meaning-set criterion for authoring; retiring `EnglishParser` (gated on the DRI's decision on the reader-protection lint class, 2.4); retiring the Lark comparator; a two-lexicon theorem; display-only text; P1–P3 for the strict surface on the same engine | — | — |

**S0 inventory deliverable** (`docs/spec/english-lean-measured.md`): per corpus environment, the number of rules,
nonterminals and the longest right-hand side; the same for **synthetic limit environments** (256 predicates,
across the profiles and across declaration shapes: unary, binary, functional total, integer slots), before and
after the factoring of 2.3; the token-length histogram of corpus sentences; confirmation that the expanded grammar
has no empty rule and no left recursion; every regex terminal that is not a word sequence; the **tree
correspondence** of section 4, written out; the classification of the 49 rejection sites; the **sort of every
lint code** into the three classes of 2.4; Earley time per sentence; character-versus-token probes (7.2); and the
G4 volume and coverage targets.

**Shadow corpus (sealed with hashes in S0).** Every English text in the test suite (the 37 files of 1.6); the
conformance generators (85,000 round-trip ASTs with their renderings, 12,750 Earley texts, 850 documents, 6,757
mixed texts, 1,220 natural statements); every use-case document and rendering; the pilot documents pinned by
`bench/PROFILE-GOLDEN.json` (they live in sibling checkouts, so S0 copies or pins them); the rejection fixtures,
including the constructed two-derivation cases of `tests/test_english_unambiguity.py`. The existing 85,000-pair
Python–W7 differential gains the new reader as a third arm: on the 57,765 core texts all three must agree.

**Reverse corpus.** The items above are almost all Python renderings or Python-accepted fixtures, so they test
one direction: what Python accepts, Lean accepts. The unsafe direction is a text that Lean accepts and Python
rejects (7.2). From S2, when the `english.grammar` export exists, the corpus therefore gains texts **sampled from
Lean's exported grammar**, each with spacing mutants and word-split mutants, and each is compared against both the
hand parser and Lark. G4 draws them with fresh seeds. After S5 Lark stays in this role, as a logged comparator
with no authority, until S7.

**Lexicon mutation replay.** For each corpus environment, the selected lexicon is mutated to other valid
lexicons (one symbol at a time moved to another honest wording) and the corpus texts are read again. A text may
lose its reading. It must never get a different formula. This is an empirical gate of G2 and G3; it is not a
theorem (2.4).

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
| Grammar size | no ceiling is fixed in this draft: draft 1's 8,192 excluded an environment that is valid today (1.2). S0 measures the expanded size on synthetic limit environments, with the factoring of 2.3 as the default, and sets the ceiling from that; fixed part at most 400 | measurement in S0; without the factoring the DRI reviews a new limit |
| Work budget | a deterministic step count, set in S1a at 10× the largest corpus need. A failed rule attempt is a step, like a combination, so the budget bounds time | replaces the 30-second wall clock |
| Latency, warm service | corpus sentence p95 ≤ 20 ms; 150-token sentence ≤ 50 ms; BlueDot document ≤ 1 s | Python today: 95 ms and 1.04 s |
| Grammar instantiation | ≤ 100 ms per environment, cached by identity | one-shot Lean medians of 47–152 ms |
| Lean build | generated rule modules add ≤ 60 s to `lake build` | to be measured in S2 |

**G1a is a pass gate.** S1a measures deterministic steps, peak memory and latency, on ordinary inputs, on long
failing prefixes and on highly ambiguous inputs, on the corpus and on the synthetic limit environments. Any missed
budget, by any factor, means optimise (first-token and left-corner filtering, indexing of hole-led rules) and
measure again. Proof work starts only when every budget is met, or when a revision of the budgets or of the
strategy has been reviewed and then passes measurement. A miss by more than 5× is the threshold for escalation:
investigate, and re-plan with option H or G before proving anything. The threshold decides escalation, never
acceptance.

## 6. Trusted base and the trust map

**What must be trusted for "this text has exactly one reading, and it is A", after S5:**

| Item | Size (estimate) | Kind |
|---|---|---|
| `Tree.derives`, `Grammar`, `Terminal.accepts` | about 80 lines | definition: what a derivation is |
| Fixed rules (generated table literals; JSON source) | 150–250 rules, formula level | data |
| `lexRules`, `Lexicon.valid`, `wordingKey`, `negativeTemplate` (with the idiom and irregular-verb tables it reads) | about 300 lines; S0 re-estimates after the lint sort | definition: how wordings become rules, and which selections are valid |
| Lint checks that S0 classes as reader protection | a part of the 300-line lint; S0 measures it | retained Python check, trusted until the DRI decides |
| `lex` | about 150 lines | definition: what the tokens of a text are |
| Action library, `meaning` | 70–90 actions, about 600 lines | definition: what a derivation means |
| Theorem statements of 3.2–3.5 | — | reviewed statements |
| Lean kernel, compiler, runtime; JSON decoding; service glue; the Python adapter that carries the text and shows the answer | as for every Lean-decided unit | existing boundary |
| Declared templates; the reader's understanding of them | — | unchanged: semantic declarations |

**No longer trusted for this claim:** `EnglishParser` (about 750 lines), source normalisation, `english_lark_grammar`
and the hooks, the audit and registry modules, Lark's Earley implementation, Python's `re`, and the parser
implementation in Lean (it is proved). **The vocabulary lint is not in this list** (about 300 lines plus the
printer lint): the checks S0 classes as meaning-relevant become Lean definitions in `valid`, the checks it classes
as reader protection stay trusted Python, and only the checks it classes as subsumed leave the base. The base goes
from roughly 2,000 lines of Python (*static*) plus a third-party parser and regex engine to roughly 1,100 lines of
Lean definitions and 150–250 rules of data, with one proved parser, plus the retained lint checks. S0 re-estimates
these figures after the lint sort. The claim itself is narrower than draft 1 stated: it is "one reading under this
validated, identified lexicon".

**Rows for the trust map** (to add when `docs/TRUST-MAP.md` lands; until then they go in the assurance manifest):

- `english.admission`: authority `python` → `lean` at S5. `trusted` changes from `python:implementation`,
  `python:surface` to `lean:kernel`, `lean:compiler`, `lean:decoders`, `lean:runner-glue`,
  `lean:english-definitions` (lexer, rules, actions, lexicon validity), `python:backend-adapter`, and
  `python:vocabulary-lint` for the retained reader-protection checks, until the DRI retires them.
- `assurance` stays `experimental` until the 3.2–3.5 theorems are in the audit inventory. After that the
  one-reading claim may be labelled as proved **relative to the grammar definitions and to the identified
  lexicon**. Until then records carry claim sentence C1 of the statement spec, "Lean read this text and
  reported one reading per sentence. The reader's correctness has not yet been proved.", never "Lean-verified".
- New row, definitions: the English grammar data and every trusted definition file of the reader (tokens and
  matching, lexer, lexicon validity, rule construction, action library, AST encoding), with their hashes in a
  lock file. `actions_version` rises on any change to one of those files.
- New row, producers: vocabulary selection, renderer, Python parser. Untrusted; outputs checked by Lean
  (`Lexicon.valid`, `checkRendering`, comparison). The retained lint checks are not in this row.
- New row, comparator: Lark after S5. Logged, no authority, retired at S7.
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
   decision. The sealed corpus of draft 1 sampled this direction only through a few rejection fixtures; the
   reverse corpus (section 5) is the systematic test.
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
7. **Performance is unmeasured.** The worst case of the table parser is cubic in sentence length only with
   rule-suffix memoisation and shared witnesses (3.2); a cap on complete entries alone does not give it. The
   design cannot rely on first-word indexing: the bulk of the grammar is hole-led wording rules. Steps and peak
   memory are as unmeasured as latency, and all three are measured at limit sizes as well as on the corpus
   (G1a). A deterministic budget may reject a pathological document that Python's 30-second limit would accept.
8. **Statement layers will show real differences.** Several have no whole-sentence check today; `report_english`
   treats an ambiguous embedded statement as no derivation. Moving them onto the engine will reject some texts
   accepted today. That is the point of the lead's decision, but each case needs review and a release note.
9. **The `it` rule is kept exactly**, although PLAN-ZERO-TRAINING calls it insufficient and the discourse profile
   supersedes it. This plan does not improve discourse; it stops the rule from being Python-only.
10. **Marked conclusions** are still accepted or rejected by a bounded proof search outside the grammar (a recorded
    conflation). Out of scope here.
11. **Source of truth for fixed rules.** JSON with generated Lean literals (recommended, as for wire contracts) or
    Lean-first with a JSON export. Decided by the statement review: JSON with generated Lean literals.
12. **Non-ASCII input.** English sources are UTF-8. The lexer must define case folding beyond ASCII; the discourse
    lexer already has such a table (`foldChar`). Decided by the statement review (statement spec, R13): the
    table is copied into the English instance, with a test that the two tables agree.
13. **Frozen files and layers.** The new modules need frozen-inventory lines, audit lines and a layer assignment
    (proposed: `VE.Grammar.*` and `VE.EnglishGrammar.*` in layer 3, the service mode in layer 4). A bridge to W7
    (3.6) needs a layer exception like the existing discourse ones.
14. **Display-only English stays unverified** until S7. A reader of a rights unit or a status sentence still relies
    on fixed Python frames.
15. **Two English grammars remain in Lean** for a time: this one and the discourse grammar. Re-hosting discourse on
    the generic engine is possible and not planned.
16. **Zero-training English is not solved by this.** Arbitrary English still has zero derivations. The plan gives
    the IDE exact witness pairs and reading sets to drive rephrasing; coverage remains the catalogue's job.
17. **The guarantee is per lexicon.** One reading is proved for a validated, identified lexicon. Whether two valid
    lexicons can give one text two different formulas is tested by mutation replay and not proved. Part of the
    vocabulary lint stays trusted Python until S0's sort and the DRI's decision (2.4).
18. **Grammar size is not linear in the vocabulary.** The attribute-property product reaches 16,384 alternatives
    in an environment that is valid today (1.2). The factoring of 2.3 is the default answer; it changes the
    shape of derivations, so it depends on the tree correspondence being one-to-one. Other products may exist in
    profile combinations that no committed environment exercises; S0's synthetic limit environments look for
    them.

## 8. Effort and order

Formula-level English reaches Lean authority in about 8–11 weeks elapsed, including the 14-day shadow window:
S0 (1 week), S1 (3–4 weeks, with S2's Python and JSON work in parallel once S1a passes), S2–S3 (3–4 weeks), S4–S5
(3 weeks). S6 is about one week per layer and can run two layers at a time after S5. The proof work (S1b) is the
largest uncertainty; the largest unknown in scope is the number of differences S0 and S4 uncover.

Hard Lean (S1b, actions) goes to the Lean implementer; Python, generator and harness work to the Python
implementer; the theorem statements of section 3 get a statement review before S1b starts, as the wire-contract
statement spec did. They are written out in [english-lean.md](english-lean.md). That review is done (section
10). S1b waits for the corrected statements, for their elaboration in S1a and for G1a.

## 9. Review response (draft 2)

The review of draft 1 (`manage-agents/debates/design-english-lean/{fable,astra}.md`) converged after round 3.
Both reviewers keep the architecture. Fable's label is "BUILD, staged"; Astra's is "REVISE to draft 2, then BUILD
through the staged gates"; they differ in name only. The joint position is Fable's list of eight edits (round 3)
with Astra's three qualifications (round 3); where the two texts differ, Astra's governs. The edits that change
what S0 measures (1, 3, 4 and the lint sort of 6) had to enter before S0; the rest before S1b. All are in this
draft.

| # | Converged edit | Where applied |
|---|---|---|
| 1 | **Size.** Drop the 8,192 ceiling. S0 measures the expanded size on synthetic limit environments across profiles and declaration shapes. Default: factor the attribute-property product (`english.py:1907`) into one rule per relation over a per-sort property nonterminal, derivations one-to-one; otherwise the DRI reviews a new limit | 1.2 (two rows, last paragraph), 2.3, section 5 (S0 row, inventory, budget table), 7.18 |
| 2 | **Cost.** State the cap invariant. Specify rule-suffix memoisation and shared witnesses before claiming cubic cost. S1a measures steps, peak memory and latency on ordinary, failing-prefix and ambiguous inputs at limit sizes. Hole-led indexing is an optimisation to measure | 2.2, 3.2, section 5 (S1a row), 7.7 |
| 2a | **G1a stays a pass gate** (Astra, qualification 3). Any miss means optimise and measure again. Proof work starts only when the budgets are met, or a reviewed revision of budgets or strategy passes measurement. The 5× threshold decides escalation, not acceptance | section 5 (S1a row, G1a paragraph), section 8 |
| 3 | **Parity.** Define the tree correspondence (EBNF expansion, duplicate productions, overlapping terminals, phrase splitting, the factoring of edit 1). Compare verdicts, formulas and witness multiplicity, not rule sets | section 4, section 5 (S0 inventory, G2) |
| 4 | **Reverse corpus.** Texts sampled from Lean's exported grammar, with spacing and word-split mutants, against the hand parser and Lark. Lark stays a logged comparator until S7 | section 5 (reverse corpus, S5 and S7 rows), section 6, 7.2 |
| 5 | **`extension_safe`.** `Embeds` is an injective, yield-preserving tree embedding that preserves actions, types and successful meanings under the same state: formulas, conclusion marks and successor state (Astra, qualification 2). Vocabulary reselection is not an extension | 3.5 |
| 6 | **Lexicon.** `valid` adds cross-symbol `wording_key` distinctness and equality with a Lean `negativeTemplate`. S0 sorts each lint code: subsumed, ported, or retained Python check. P1 is stated, scoped to the validated, identified lexicon. Mutation replay is an empirical gate (Astra, qualification 1). The unconditional claim that selection is meaning-neutral is removed; only a proved two-lexicon theorem restores it | section 0 (change 6), 2.4, 3.5, section 5 (mutation replay, S0 inventory, G2, S7 row), section 6, 7.17 |
| 7 | **Contract.** `DocOneReading` is a fold over `DState`. `read_ok` and `checkRendering` conclude formulas and marks. `EnglishOneReading` includes `Lexicon.valid`. Evidence binds source, environment, overlay, lexicon, and grammar and action versions | 3.4, 3.5, section 4 |
| 8 | **Options, shadow.** Add option H (span-ordered table) before G. G4 gains a fresh-seed volume and coverage gate with zero undispositioned differences | 2.1, section 5 (S4 row, S0 inventory) |

Two notes for the DRI's check.

- **Edit 8 is the one place where the two final texts differ.** Fable's round 3 writes "G4 becomes a fresh-seed
  volume and coverage gate". Astra's round 3 writes "retain the existing grammar-family choice and shadow
  duration; I withdraw changing either as a prerequisite". Astra's text governs. So the chosen parser is
  unchanged and H is only listed in reserve, and G4 keeps the 14-day window and adds the volume and coverage
  targets to it. Neither part of edit 8 blocks S0, S1a or S1b.
- **Corpus conservativity is described as measured evidence** (Astra, rounds 1 and 2): 3.5 says so. The separate
  statement-layer gates of S6 are unchanged.

Not changed: sections 1.1, 1.3 to 1.6, 2.5, 3.1, 3.3, 3.6, the other risks of section 7, the effort estimates of
section 8, and every figure taken from a committed report. The statement spec may sharpen a statement of section 3
(a name, a hypothesis that is not needed); it lists each such change, and the statement review decides it.

## 10. Statement review response

The statement review of [english-lean.md](english-lean.md) draft 1
(`manage-agents/debates/english-lean-spec/{fable,astra}.md`) converged after round 3 on FIX, then build. The
statement spec's section 12 lists every correction with the place it was applied there. This table lists the
corrections that touch this plan. A correction that is not in the table changed the statement spec only: the
false fixture g18 and the new g20, the condition columns of v4 and v5, the paraphrases of the theorems.

| # | Converged correction | Where applied in this plan |
|---|---|---|
| 1 | **Generic engine.** The engine is generic in the token type, the terminal type and the matching. Tokens, terminals, case folding and the terminator condition belong to the English instance. `Grammar.wf` no longer contains the terminator condition; `read` checks it | 2.2 (documents), section 3 (opening note), 3.1 (`Grammar.wf`), 3.5 (`read`), section 5 (S1a row), 7.12 |
| 2 | **Elaboration.** S1a elaborates the generic definitions and theorem types under Lean 4.24.0, each unproved statement as a definition of type `Prop`. Corrections that elaboration forces are listed; a change of meaning returns to the reviewers. S1b waits for the corrected statements, their elaboration and G1a | status, section 5 (S1a and S1b rows), section 8 |
| 3 | **Step counter.** A failed rule attempt is charged like a combination. G1a keeps its latency and memory gates | section 5 (S1a row, work budget) |
| 4 | **Start type.** The typing check does not fix the type of the start symbol. The statement spec adds the theorem `start_sentence`, with a check in `read` as the approved fallback | section 3 (opening note) |
| 5 | **Identity of the definitions.** `actions_version` covers every trusted definition file of the reader, not only the action library. The lock file hashes each | section 4 (evidence, identities), section 6 (definitions row) |
| 6 | **Translation mode.** It reads exactly one sentence, from the initial state, and rejects a longer text. Its set is complete exactly when the parser returned fewer trees than the cap | 3.4 (last paragraph), section 4 (service mode) |
| 7 | **Distinctness.** Condition 2 of `Lexicon.valid` names sort nouns and constant spellings on both sides, with predicate wordings | 2.4 (condition 2) |
| 8 | **Claim sentence.** Before the proofs are in the audit, a record says: "Lean read this text and reported one reading per sentence. The reader's correctness has not yet been proved." | section 6 (assurance row) |
| 9 | **English extension theorem.** Deferred until its premise `Extends` has a body with explicit preservation premises that the reviewers can assess. `extension_safe` itself is unchanged | section 3 (opening note) |
| 10 | **Accepted as proposed.** JSON as the source of the fixed rules; the copied case-folding table; the profile-fixed negatives and aliases in `Lexicon.valid` | 2.4 (condition 3), 7.11, 7.12 |

The sketches of section 3 keep their draft 2 form apart from the two comments named in row 1. The statement
spec governs, and its section 11.1 (R1 to R16) lists each difference from them.

Not changed by the statement review: sections 0, 1, 2.1, 2.3, 2.5, 3.2, 3.3, 3.6, the gates and budgets of
section 5 other than the S1a, S1b and work-budget rows, the trusted-base table of section 6, the other risks
of section 7, the effort estimates, and section 9.
