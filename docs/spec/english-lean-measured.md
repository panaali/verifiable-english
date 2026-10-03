# English in Lean: S0 measurements (partial)

**Status:** S0 deliverable of [english-lean-PLAN.md](english-lean-PLAN.md) section 5, **partial**, 2026-10-03,
branch `english-lean/py`. Every figure below was measured by a committed tool on this branch; the raw data is
`conformance/english-lean/s0-report.json`. Nothing here changes a verdict, an identity, a public code or a
frozen file. Items that S0 still owes are listed in section 6.

Tools (no model calls; none is on an admission path):

| Tool | Measures | Run |
|---|---|---|
| `conformance/english_lean_s0.py` | grammar sizes and shape, terminal classes, synthetic limit environments, token lengths, lexer probes | `uv run python -m conformance.english_lean_s0 --per-configuration 60` |
| `conformance/english_lean_engine.py` | Python reference of the item-1 engine (spec 2.4 to 2.8, 5.2 to 5.7) and the English matching (5.8) | imported by the next two |
| `conformance/english_lean_corpus.py` | the engine corpus `conformance/english-lean/engine.json` (spec 8.1 to 8.3, 8.7) | `uv run python -m conformance.english_lean_corpus` |
| `conformance/english_lean_lexer.py` | Python reference of the draft lexer (spec 2.2), fixtures `conformance/english-lean/lexer.json` (8.4) | `tests/test_english_lean_lexer.py` |

## 1. Python's generated grammar, per configuration

The 17 configurations of `conformance.english_surface` (the round-trip corpus of plan 1.6). Sizes are after
Lark's EBNF expansion (`Lark(...).rules`); `|G|` is the total length of the right-hand sides; the rank depth is
the depth of the left-corner graph, which is the largest `rank` a W3 certificate needs.

| Configuration | Rules | Nonterminals | Longest RHS | \|G\| | Rank depth | Literal / phrase / open terminals |
|---|---|---|---|---|---|---|
| ordinary | 132 | 38 | 15 | 337 | 6 | 78 / 12 / 1 |
| closure | 132 | 38 | 15 | 337 | 6 | 78 / 12 / 1 |
| colliding_aliases | 123 | 38 | 15 | 339 | 6 | 80 / 6 / 1 |
| function_words | 130 | 38 | 15 | 346 | 6 | 87 / 6 / 1 |
| function_identifiers | 120 | 38 | 15 | 327 | 6 | 81 / 4 / 1 |
| precision_templates | 128 | 38 | 15 | 332 | 6 | 76 / 11 / 1 |
| birthright-citizenship-debate | 123 | 38 | 15 | 329 | 6 | 79 / 3 / 1 |
| claude-constitution-excerpt | 181 | 38 | 15 | 461 | 6 | 93 / 29 / 1 |
| news-article | 197 | 38 | 15 | 532 | 6 | 117 / 19 / 1 |
| us-constitution-14th-s1 | 146 | 38 | 15 | 376 | 6 | 72 / 18 / 1 |
| birthright-citizenship-debate-reviewed | 135 | 38 | 15 | 335 | 6 | 73 / 14 / 1 |
| claude-constitution-excerpt-reviewed | 231 | 38 | 15 | 519 | 6 | 83 / 54 / 1 |
| news-article-reviewed | 244 | 38 | 15 | 555 | 6 | 103 / 47 / 1 |
| us-constitution-14th-s1-reviewed | 181 | 38 | 15 | 453 | 6 | 72 / 32 / 1 |
| accepted-suggestions | 124 | 38 | 15 | 320 | 6 | 77 / 9 / 1 |
| adopted-unary | 139 | 38 | 15 | 341 | 6 | 73 / 16 / 1 |
| order | 137 | 43 | 15 | 357 | 7 | 83 / 11 / 3 |

Findings.

- **No empty rule and no left recursion**, in every configuration and every synthetic environment (section 2).
  This confirms the *static* claim of plan 1.2 and 0 (change 3). The only left-corner cycle Lark's expansion
  contains is `__start_plus_0`, its left-recursive form of the document-level `(sentence ".")+`; the Lean
  design splits sentences in the lexer instead, so it is not part of the sentence grammar.
- **Ranks are shallow:** a certificate needs depth 6 (7 with `order@0`).
- **The longest right-hand side is 15 symbols** (the split-`if` listing rules), counted over Lark terminals;
  over word tokens it is longer (spec O10).
- **Open regex terminals** are only `LABEL` (one upper-case letter per sort, then a positive number),
  `NUMERAL` (`-?(?:0|[1-9][0-9]*)`, signed) and, with `order@0`, `INT_OP` (`+ - *`, a finite set). Every
  other regex terminal is a fixed word sequence. The signed `NUMERAL` is spec O2 as predicted.
- **Phrases split into tokens:** every phrase terminal lexes with the draft lexer; up to 11 tokens per phrase
  (reviewed overlays). The one terminal the lexer refuses is `.`, the terminator, which W4 keeps out of the
  sentence grammar.
- **Sizes differ from plan 1.2's static count** (82 alternatives over 20 nonterminals) because Lark's
  expansion of `?`, `*` and inlined rules adds rules and nonterminals. The tree correspondence (section 6)
  must map them.

## 2. Synthetic limit environments

`MAX_PREDICATES` is 256. Wordings are generated words (`qucaba`, …) with mechanical or declared templates
that pass the vocabulary lint (`{0} is W`, `{0} Ws {1}`). The factored count applies spec 2.10 (D13):
Python's `pairs` alternatives `the R of t is P` become one rule per relation and one per property.

| Environment | Predicates | Declared wordings kept | Rules (Python) | \|G\| | Attribute pairs | Rules after factoring | Rank depth |
|---|---|---|---|---|---|---|---|
| unary-256-mechanical | 256 | 0 (mechanical) | 1,644 | 2,344 | 0 | 1,644 | 6 |
| unary-256-declared | 256 | 256 | 1,644 | 2,344 | 0 | 1,644 | 6 |
| binary-256-declared | 256 | 256 | 1,134 | 2,346 | 0 | 1,134 | 6 |
| data-128x128 | 256 | 0 | 17,771 | 102,055 | 16,384 | 1,643 | 6 |
| order-256-int-slots | 256 | 256 | 639 | 1,617 | 0 | 639 | 7 |

Findings.

- **The attribute-property product is confirmed** at 16,384 alternatives for 128 × 128 (plan 1.2, *probe*),
  now measured: 17,771 expanded rules and `|G|` = 102,055. Building that Lark grammar took 94 to 160 s on a
  loaded machine.
- **Factoring brings it to 1,643 rules**, the size of a plain 256-predicate environment. The other shapes are
  linear in the vocabulary: about 6.4 rules per unary predicate (clause, relative, adjective and coordination
  forms) and 4.4 per binary predicate.
- **Grammar-size ceiling.** With factoring, the largest synthetic grammar has 1,644 expanded Lark rules. The
  Lean rule count over word tokens will differ (phrases become sequences, not rules); S2 measures it on the
  `english.grammar` export. These figures are the input for the DRI's ceiling; this report sets none.

## 3. Sentences in tokens

1,020 texts (60 per configuration: the directed formulas of `english_surface` first, then random formulas of
depth 2 to 7), rendered by `render(..., 've_english')` and lexed by the reference lexer. Each text is one
sentence.

| Percentile | p50 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|
| Tokens per sentence | 28 | 67 | 86 | 156 | 266 |

| Tokens | 1–25 | 26–50 | 51–75 | 76–100 | 101–125 | 126–150 | 151–175 | 176–200 | 201–225 | 251–275 |
|---|---|---|---|---|---|---|---|---|---|---|
| Sentences | 479 | 335 | 135 | 31 | 20 | 8 | 5 | 5 | 1 | 1 |

The random generator reaches sentences beyond plan 1.6's 150-token design point (12 of 1,020). The
performance budget of plan section 5 sets no sentence cap below the document limit, so S1a must measure such
sentences too.

## 4. Lexer probes (plan 7.2; spec O1 to O3)

- **Rejections:** the draft lexer accepted all 1,020 rendered texts. No `badCharacter`, `badNumeral` or quote
  error occurred on Python's own renderings.
- **Token adjacency (O1): the class is not empty.** For each text, token-preserving spacing mutants were
  read by Python's full pipeline (`parse_english`):

| Mutant | Same tokens as the original | Python's verdict | Count |
|---|---|---|---|
| a space inserted before `,` `;` `:` | yes | rejected (`SyntaxError`) | 631 |
| the space after `,` `;` `:` removed | yes | rejected (`SyntaxError`) | 701 |
| a list marker written `( a )` | no | rejected (`SyntaxError`) | 330 |

  Every comma, semicolon or colon spacing mutant that the draft lexer reads as the original's tokens is
  rejected by Python. Example: `For every service that is deployed , it is not the case that …`. Under the
  draft token type, Lean would accept these with the original's reading. That is a widening of acceptance,
  not a change of formula: the tokens, and so the derivations and meanings, are those of the accepted
  original. Spec O1 prescribes, for a non-empty class, a `glued` flag on `punct` before S2. **For the DRI:**
  either add the flag (Lean then rejects these mutants as Python does), or record the widening as an
  accepted product difference under SEMANTICS-MIGRATION-PLAN 2.3. No hyphenated word occurred in the
  rendered corpus, so the `non-citizen` case of O1 is not yet measured; the sealed corpus (section 6) must
  include declared wordings with hyphens.
- **Whitespace (O3):** the reference lexer uses the 29 code points of Python's `str.isspace`, which is what
  `_normalise_english_source` collapses (Lean's `Char.isWhitespace` has 4 of them). The list is a literal in
  `conformance/english_lean_lexer.py`, tested against `str.isspace` over all of Unicode. The Lean lexer must
  use the same list.
- **Text length:** the reference lexer's collapsed length equals the length of `_normalise_english_source`'s
  text on the tested sources, so `textTooLong` and Python's `MAX_NODES` check measure the same quantity.
- **Offsets:** the reference lexer reports UTF-8 byte offsets, as Lean's `String.Pos`.
- **Initial words:** Python lower-cases a sentence-initial `[A-Z][A-Za-z]*` word unless it starts a declared
  capitalised constant, and does the same after `therefore`, `so`, `hence`, `it follows that`. The draft
  lexer marks the same positions `initial` and lowers nothing; the `kw` terminal then accepts a capital there.

## 5. The engine corpus on the Python reference

All 39 cases of `conformance/english-lean/engine.json` (g1 to g20, m1 to m5, r1 to r10, q1 to q4) pass on the
reference engine, so the hand-derived expectations of spec section 8 hold for one implementation of the
definitions (statement review checklist, item 15). With the step counter of spec 2.6 (one step per rule
attempt or suffix attempt at a position, failed or not, and one per combination of an entry member with a
suffix member):

| Fixture | Measured |
|---|---|
| g16 | `G3`, `a a a`: no result for budgets 0 to 48; from 49 on, always the two trees of g5 |
| g17 | 40 tokens, no derivation: 599 steps; `\|G\| · n³ · cap²` = 3,072,000; ratio 0.0002. Stored: 79 entry members, 40 suffix members |
| g18 | 200 random grammars (seed 20261003), every input up to length 6: 178 well-formed, 22 not; at most 32 derivations per input, so cap 64 never saturates; the extra caps 2 and 3 saturate in 26 grammar-input pairs and truncate correctly |
| g20 | 128 derivations by enumeration; cap 64 returns 64 distinct ones, cap 129 all 128 |

A mutation check (keeping one member fewer than the cap) fails g5, g9 and g20, so the corpus detects a broken
cap invariant. These step counts are for the Python reference; S1a measures Lean's.

## 6. What S0 still owes

| Item (plan section 5) | State |
|---|---|
| Rule, nonterminal and RHS counts per corpus environment; synthetic limit environments | done (sections 1, 2) |
| No empty rule, no left recursion | done (section 1) |
| Regex terminals that are not word sequences | done (section 1) |
| Token-length histogram | done on rendered texts (section 3); the use-case documents and pilots are not yet included |
| Character-versus-token probes | partly: spacing mutants (section 4); hyphenated wordings and word-split mutants are not yet measured |
| Sealing the shadow corpus with hashes | not done |
| The tree correspondence (Lark ↔ Lean derivations) | not done |
| Classification of the 49 rejection sites; blocked-wording ids | not done |
| Sort of every lint code into subsumed, ported, retained | not done |
| Earley time per sentence | not done |
| G4 volume and coverage targets | not done |
