# Deterministic rendering views, version 3

The writable `ve_english` surface is specified separately in
[English surface, version 1](english-surface.md). It preserves the canonical AST
and all five historical renderings described here, while adding noun references,
drafting lists, a deterministic input parser, and English-specific lexical linting.
The `render` CLI defaults to canonical strict output, as before. Select English
explicitly with `--view ve_english` (strict input) or `--surface english` (English
input and output). An explicit `--view` takes precedence over the surface default.
The five-view experimental comparison cohort below is frozen for reproducibility.

`ve.render(ast, env, view, naming="per_statement")` returns text for a closed formula or a `Document`.
`view` is `fol_symbols`, `fol_keywords`, `ve_strict`, `ve_natural`, or `ve_fluent`. A single
formula has no final punctuation. Documents append a period and LF to every
statement. All views preserve lexical case without sentence capitalization.
`natural_formula(...).text` follows the same unpunctuated formula policy.
Every view has the same 65,536-byte UTF-8 output limit; formula checks reserve
two bytes for the period and LF of a possible one-statement document. The
legend is additional cell context and is not charged against this claim-text limit.
`print_formula` and `print_document` retain the exact strict canonical bytes.
`natural_formula` and `natural_document` additionally return environment and
meaning IDs with renderer `ve.ace-explicit`, version `3`. Version 3 tightens
lexical acceptance and unifies naming scope; regenerate prior view artifacts.

The first four surfaces use **one recursive traversal** in `ve/printer.py`. It assigns
`x0`, `x1`, ... to binders in preorder, follows the selected naming scope, resolves every
variable through the same nearest-first scope stack, and visits operands in AST
order. Every immediate **formula operand**, including an atomic operand, is
parenthesized. No surface changes this grouping policy or elides a binder,
operand, statement, or condition. FOL predicate application `p(t)` / `r(t,u)`
has additional lexical argument-list delimiters; these do not group formulas.
The natural surface retains the common grouping, even where fluent prose could
omit parentheses. The fifth surface uses `ve/fluent.py`, follows the same binder
and operand preorder, and contracts only structures with an explicit inverse
(see below). None of these views reorders or simplifies the AST. All five views default to `per_statement`: counters restart in every statement.
Select `per_document` to continue numbering across statements in **every** view.
Each render call starts a fresh scope. Choose one policy for all experimental
cells; `render_cell` records it in the identical legend. Formula-only calls have
one statement under either policy. Canonical serialization remains per-statement.
Fluent version 3 uses distinct sort letters and mechanically checked negatives.

| Constructor | FOL symbols | FOL keywords | VE strict | VE natural |
|---|---|---|---|---|
| Top / Bottom | `⊤` / `⊥` | `true` / `false` | `true` / `false` | `true` / `false` |
| Unary | `p(t)` | `p(t)` | `t is p` | template or strict atom |
| Binary | `r(t, u)` | `r(t, u)` | `t r u` | template or strict atom |
| Equality | `t = u` | `t = u` | `t equals u` | `t is equal to u` |
| Negation | `¬ (A)` | `not (A)` | `not (A)` | `it is not the case that (A)` |
| Conjunction | `(A) ∧ (B)` | `(A) and (B)` | `(A) and (B)` | `(A) and (B)` |
| Disjunction | `(A) ∨ (B)` | `(A) or (B)` | `(A) or (B)` | `(A) or (B), or both` |
| Implication | `(A) → (B)` | `(A) implies (B)` | `if (A), then (B)` | `if (A), then (B)` |
| Universal | `∀ x:s, (A)` | `forall x:s, (A)` | `for every s x, (A)` | `for every noun x: (A)` |
| Existential | `∃ x:s, (A)` | `exists x:s, (A)` | `there exists s x, (A)` | `there is a noun x such that (A)` |

FOL keywords are ASCII. Constants retain `@identifier` in every surface, so they
cannot be confused with bound variables. Sort annotations are mandatory in FOL.
Existentials assert at least one witness, never a unique witness. Universals
retain the profile's empty-domain semantics. No pronouns or implicit witnesses
are generated. An exception already encoded as `And(A, Not(E))` keeps both the
conjunction and the explicit `it is not the case that (E)` cue; there is no
unscoped `unless` rewrite. The read-only surface is ACE-style controlled English,
not an implementation of the ACE standard or an ACE parser.

Its formula grammar is below. `atom` is a safe template expansion or strict
unary/binary atom, `term` is `xN` or `@constant`, and `noun` is the safe sort
noun or formal sort identifier. The `a`/`an` choice is deterministic.

```ebnf
formula = "true" | "false" | atom
        | term, " is equal to ", term
        | "it is not the case that (", formula, ")"
        | "(", formula, ") and (", formula, ")"
        | "(", formula, ") or (", formula, "), or both"
        | "if (", formula, "), then (", formula, ")"
        | "for every ", noun, " ", variable, ": (", formula, ")"
        | "there is ", article, " ", noun, " ", variable,
          " such that (", formula, ")" ;
article = "a" | "an" ;
```

## Vocabulary metadata and conservative fallback

Sort and predicate entries optionally carry `verbalisation`:

```json
{
  "sorts": {
    "service": {
      "description": "A service recorded in the inventory.",
      "verbalisation": {"singular": "service", "plural": "services"}
    },
    "person": {
      "description": "A recorded person.",
      "verbalisation": {"singular": "person", "plural": "people"}
    }
  },
  "predicates": {
    "deployed": {
      "arguments": ["service"], "description": "Recorded as deployed.",
      "verbalisation": "{0} is deployed"
    },
    "owns": {
      "arguments": ["person", "service"], "description": "Recorded ownership.",
      "verbalisation": "{0} owns {1}"
    }
  },
  "constants": {}
}
```

These are entries inside the ordinary environment's `vocabulary` object.
The complete metadata is immutable and contributes to `environment_id`, including
unused plural nouns and unsupported templates. Omitting it preserves existing
environment serialization and identities. The strict parser and denotation are
unchanged. Entries with the wrong metadata type, missing noun fields, unknown
fields, or empty strings are rejected; each metadata string is at most 256
characters. Constants keep their formal identifier and do not accept templates.

Usable lexical templates have this grammar:

```ebnf
word              = lowercase ASCII letters, one or more ;
phrase            = word, { " ", word } ;
unary_template    = "{0} is ", word ;
binary_template   = "{0} ", phrase, " {1}" ;
sort_noun         = phrase ;
```

A phrase cannot contain any word in this reserved display set:

```text
all any every some each no none not never neither nor and or both either if then
unless except without only exists forall implies true false equal equals there
such that case condition for at least most exactly does do must may can cannot
should shall will would whenever when iff otherwise always sometimes one two
three four five six seven eight nine ten a an the lacks nothing nobody everything
everybody just solely many several another but plus few might
```

Positive and negative templates are limited to **80 characters and 8
whitespace-separated words**, counting placeholders as words. Metadata may still
store longer strings up to the environment's 256-character bound; these render
with fallback. A template cannot mention **any declared sort identifier or
singular/plural noun**, as a complete word sequence, anywhere in the phrase.
This includes its own argument sorts and unused/rejected sort declarations:
arguments already carry their sorts. Substring matches inside other words do
not count. Multiword nouns are matched as complete consecutive word sequences.

Each argument placeholder occurs exactly once, in declared order. There are no
format conversions, attributes, escapes, punctuation, parentheses, embedded
variables, or executable expressions. The renderer performs literal placeholder
replacement, never evaluates supplied formatting code. A template is a declared
positive atomic relation phrase, not a place to add quantifiers or conditions.
The binary phrase must start with a word ending in `s` (e.g. `owns`,
`depends`, `has`). It must not start with `is`, `are`, `was`, `were`, `be`,
`been`, `being`, `gets`, or `got`; it must not end with `by`, `to`, `of`,
`from`, `with`, or `for`. There is no metadata override for these restrictions.
Unary templates require `is` followed by exactly one complement head word;
trailing modifiers such as `reviewed already` are rejected. This deliberately
narrow grammar can reject truthful English phrases.

Every phrase and both singular/plural sort nouns are checked against the entire
environment, including unused symbols and rejected declarations. They may not
contain another predicate/sort/constant identifier or another declaration's
template head as a word. Predicate heads are the first phrase word after the
unary `is`, or the first binary phrase word; noun heads are the last noun word.
A declaration may use its own identifier/head. `un`, `non`, `un-`, or `non-`
prefixed to any predicate identifier/head is rejected, including its own head
(e.g. `deployed` → `undeployed`). Variable tokens `x`, `xN`, and capital letters with optional numeric
suffixes (such as `S` and `S2`) are rejected. Capitals are also excluded by the lowercase grammar.
Exact duplicate predicate templates are rejected for all owners. A sort noun
must not equal another sort identifier or another sort's singular/plural noun.

Unsupported templates use the strict atom; a rejected singular **or plural**
noun makes the sort use its identifier. Plurals remain in metadata but do not
replace bound variables. The existential article is `an` for a selected noun
starting with `a/e/i/o/u`, otherwise `a`.

`lint_vocabulary(env)` returns a deterministic tuple of `VocabularyLint` records,
sorted by JSON `path` then `code`. Each record has `.path`, `.code`, and
`.to_dict()`. Missing optional metadata is supported fallback, not a warning.
Multiple diagnostics may identify the same rejected entry. Stable codes are:

| Code | Rejection |
|---|---|
| `TEMPLATE_LENGTH` | More than 80 characters or 8 whitespace-separated words |
| `SORT_NOUN` | Template mentions a declared sort identifier or singular/plural noun |
| `TEMPLATE_SHAPE` | Missing, misplaced, or unsupported placeholder/copula structure |
| `PHRASE_SYNTAX` | Unsupported characters, placeholders in a phrase, spacing, or case |
| `LOGICAL_WORD` | Reserved quantifier, connective, negation, or other display word |
| `VARIABLE_TOKEN` | `x`, `xN`, or a capital letter with optional numeric suffix |
| `SYMBOL_COLLISION` | Word equals another identifier or lexical head |
| `NEGATED_HEAD` | Negating prefix applied to a predicate identifier/head |
| `BINARY_AUXILIARY` | Forbidden leading copula/auxiliary |
| `BINARY_CONVERSE` | Forbidden final preposition |
| `BINARY_VERB` | Binary first word does not end in `s` |
| `UNARY_MODIFIER` | More than one complement word after unary `is` |
| `DUPLICATE_TEMPLATE` | More than one predicate declares the same template |
| `SORT_COLLISION` | Noun equals another sort's identifier or noun |
| `NEGATIVE_WITHOUT_POSITIVE` | Negative metadata lacks an accepted declared positive template |
| `NEGATIVE_NOT_NEGATION` | Negative metadata differs from the mechanically derived exact negation, or its binary verb has no supported inflection |

Predicate entries may also carry an optional `negative_verbalisation` string,
with the same type, 256-character limit, immutability, and identity binding as
`verbalisation`. It is selected only after its declared positive template passes
**all** checks above. Selection requires an exact byte match to this derivation:

- Unary: `{0} is HEAD` becomes `{0} is not HEAD`, copying `HEAD` unchanged.
- Binary: replace only the first verb with `does not BASE`, preserving the rest
  of the phrase and both placeholders exactly. Regular consonant + `ies` becomes
  `y` (`carries/carry`); `ches`, `shes`, `sses`, `xes`, `zzes` lose `es`
  (`watches/watch`, `passes/pass`); otherwise a final `s` is removed, except
  unsupported `ss`, `us`, `is`, `ous`, `oes` endings. Explicit irregular/spelling
  exceptions take precedence: `has/have`, `does/do`, `goes/go`, `says/say`,
  `dies/die`, `lies/lie`, `ties/tie`, `unties/untie`, `vies/vie`, `quizzes/quiz`,
  `gases/gas`, `biases/bias`, `buses/bus`, `focuses/focus`, `echoes/echo`,
  `vetoes/veto`, `aches/ache`, `caches/cache`, `niches/niche`, `axes/axe`,
  `shoes/shoe`, `toes/toe`, `tiptoes/tiptoe`. The positive-template restrictions
  still apply first (e.g. reserved `does` cannot introduce a positive template).
  This spelling convention is not a dictionary or a general English inflector;
  unsupported or mismatched declared negatives keep explicit fallback.

For example, `{0} is reviewed` permits only `{0} is not reviewed`, and
`{0} owns {1}` permits only `{0} does not own {1}`. An attacker-supplied
`{0} is not unreviewed`, positive-looking phrase, changed verb, reordered term,
extra modifier, or format expression is rejected as a display template. It stays
JSON-quoted in the environment and legend with a lint diagnostic; fluent uses
`it is false that <positive unit>` instead. Malformed field types and oversized
strings are environment errors. Missing metadata produces the same explicit
fallback without a lint warning. No negative is guessed from a formal predicate
identifier or a rejected positive. A declared negative never changes positive
atomic rendering, and the four explicit views retain their ordinary negation
syntax. The legend shows both raw and selected negative templates in every view.

These checks are a **heuristic, not a proof** of English meaning or injectivity.
Templates and sort nouns are **trusted vocabulary data**, as are descriptions.
An arbitrary alias, for example `service` → `owner` or `person` → `asset`, can
remain accepted if it collides with no declaration. The linter cannot establish
its truthfulness. Converses/antonyms without a preposition, such as `precedes`
for `follows` or `disowns` for `owns`, **cannot be caught lexically**. The identical
legend exposing raw predicate identity and argument order is the defence;
it does not guarantee that a judge notices a semantic lie.
Experiments must not treat an empty lint report as validation
of vocabulary meaning.

For the example above, the natural document is:

```text
for every service x0: (if (x0 is deployed), then (there is a person x1 such that (x1 owns x0))).
```

The witness `x1` remains inside the scope of `x0` and its antecedent. Changing
`∀x ∃y` to `∃y ∀x` changes the display; swapping a relation's arguments changes
the displayed terms. Templates are identity-bound vocabulary assertions, just
like descriptions: the renderer does not establish that `owns` truthfully names
a real-world relation. A misleading declared phrase can still misdescribe the
world. This is separate from preserving the supplied AST's operators and scope.

## Validation and experiment use

`tests/test_views.py` checks the four exact surfaces, deterministic naming and
identical formula grouping, and injectivity on more than 6,000 distinct ASTs
from 24,000 seeded random draws. It also tests template collisions and fallback.
It also exercises 80 seeded combinations of colliding templates and sort nouns.
The adversarial family covers quantifier swaps, argument reversals, scope
changes, and/or swaps, implication reversal, dropped conjuncts, exceptions, and
existence conditions. Each tested pair differs in text and has a separately
evaluated finite distinguishing structure. Existing strict parse/print properties
remain in force. These checks are empirical evidence, not a proof of global
injectivity, grammatical correspondence, or readability.

Use the same environment and AST in all E1 cells. Freeze each view's version and
grouping policy, and record the actual view alongside claim/environment IDs. A display-only
metadata change still changes the environment identity and requires regenerating
all cells consistently. The natural grammar is read-only; only `ve_strict` is
accepted by the VE source parser.

## Fifth view: `ve_fluent` (renderer `ve.fluent`, version `3`)

`render(formula, env, "ve_fluent")` and
`render_fol(env, document, view="ve_fluent")` provide a deterministic read-only
surface. It follows the same lexical-case, punctuation, and 65,536-byte limit
as every other view. Documents append a period and LF per statement; formulas
have no final punctuation. Constants retain `@identifier`.
Every bound scope remains visible in surface order. There are only global
quantifiers: `for every ...` and `there is a ... such that ...`. In particular,
the E1 passive **“Every service is owned by a person” is never generated**.
Fluent uses exactly the same hardened lexical codebook as natural and the
shared legend, including all auxiliary, converse, logical-word, head-collision,
and modifier checks. Unsupported lexical syntax uses strict atomic fallback. Atomic phrases remain
declared vocabulary assertions, not mechanically verified descriptions of the world.

The changes from the four explicit surfaces are:

- Sorts are processed by formal identifier in sorted order. Prefer the initial
  capital of the selected noun, then its next unused consonant in reading order,
  then the fixed list `BCDEFGHJKLMNPQRSTUVWXYZ`. Never use `A`, `I`, `O`, or a
  letter matching **any** declared identifier, case-insensitively. A declared
  identifier such as `s2` also reserves `S` to prevent a later suffixed collision.
  Each sort has a distinct letter: `specialist` and `service` become `S` and `R`,
  rather than sharing odd/even suffixes. With more sorts/reservations than usable
  single letters, continue with alphabetic codes `BB`, `BC`, ... in the same
  fixed alphabet order. This keeps all 32 permitted sorts renderable without
  encoding sort identity in numeric suffixes. The legend lists every assignment
  in `fluent_variables.letters_by_sort`.
  Within the selected naming scope, each sort's named binders count up in preorder:
  `S`, `S2`, `S3`, ... . Default `per_statement` resets in each statement;
  `per_document` continues across the document. Dictionary order and first-use
  order do not change the sort-to-letter map. Constants retain `@`; lexical words
  remain lowercase and cannot capture names.
  **The binder declaration counts as the first mention:** its name appears
  exactly when its body refers to it; unnamed binders do not consume a suffix.
  An unused existential reads `there is a person such that true`; a used one
  reads `there is a person P such that P owns S`. Unused binders retain their
  sort, operator, scope, and existence meaning.
- A single universal whose body is an implication with a conjunctive guard uses
  `for every service S that is deployed, ...`. Each guard leaf must be an atom
  or negated atom mentioning the bound variable. Relative clauses omit only the
  bound subject; object occurrences remain explicit. One literal or exactly two
  relative literals can be spelled `that ... [and that ...]`. Larger guard trees
  and object-position guards use `such that <unit>`, preserving every binary
  conjunction node. Guards always decode to an **implication**, never to a
  conjunction or an existential.
- Consecutive universals are listed in order: `for every person P and every
  service S, if P owns S then P audits S`. The list means nested universals in
  exactly that order. A multi-binder list keeps its antecedent in the explicit
  `if` clause; it does not attach a relative clause to an uncertain binder.
- Equality is `P is the same person as P2`; its negation is `P is not the same
  person as P2`. The noun is the checked term sort, with the same safe aliases.
  Argument order is retained even for symmetric equality.
- Negated unary/binary atoms use a declared, strictly validated negative template
  when available, including in relative guards. For example, `S is not reviewed`
  decodes to `Not(Unary(reviewed, S))`; `P does not own S` decodes to
  `Not(Binary(owns, P, S))`. Validation is the exact derivation above, not a
  negative-looking phrase heuristic. Every other negation uses
  `it is false that <unit>`. Double negations remain distinct AST nodes.
- Conjunction uses `both A and B`; inclusive disjunction uses `either A or B,
  or both`; implication uses `if A then B`. Their atomic operands have no
  parentheses. Every complex operand is grouped. Quantifier bodies extend to
  the end of the enclosing formula; a quantifier used as an operand is grouped.
  Consequently mixed operators, nested implications, and different associations
  retain distinct, explicitly bounded trees. There is no reassociation, logical
  simplification, quantifier movement, implicit witness, or pronoun reference.

This is a total structural fallback for every checked, closed AST constructor
within the usual resource envelope. It does not rely on a heuristic prose
generator or a partial list of recognized sentence shapes. Unsupported guards
remain ordinary implications; unsupported atomic phrasing uses strict atoms;
complex formulas use explicit grouping. The fallback therefore never has to
switch binder naming systems in the middle of a scope.

### Fluent EBNF and inverse

The grammar below describes the emitted lexical case: reserved words and
lexical phrases are lowercase, while bound names have capital initials.
Document framing is `sentence, ".", LF`, repeated with the selected naming
scope (per-statement by default). Lexical expansions come from the fixed environment, selected using
the collision and exact-negation policy above.

```ebnf
formula = atom
        | "it is false that ", unit
        | "both ", unit, " and ", unit
        | "either ", unit, " or ", unit, ", or both"
        | "if ", unit, " then ", unit
        | "for every ", declaration, { " and every ", declaration },
          ", ", formula
        | "for every ", declaration, " ", guard, ", ", formula
        | "there is ", article, " ", declaration, " such that ", formula ;
unit = atom | "(", formula, ")" ;
atom = "true" | "false" | positive_atom | negative_atom
     | term, " is the same ", noun, " as ", term
     | term, " is not the same ", noun, " as ", term ;
guard = relative, [ " and ", relative ] | "such that ", unit ;
relative = "that ", atomic_tail ;
declaration = noun, [ " ", variable ] ;
term = variable | "@", identifier ;
variable = allowed_uppercase_letter, { allowed_uppercase_letter },
           [ positive_integer_suffix ] ;
article = "a" | "an" ;
```

`noun` is a safe sort noun or formal identifier, `positive_atom` is a selected
positive template or strict fallback, `negative_atom` is an accepted negative
template expansion, and `atomic_tail` is a selected atom without its subject or
the tail of a typed (in)equality. Predicate relative clauses require an accepted
declared positive template and, for negated predicates, an accepted negative.
`identifier` is the environment's ASCII identifier syntax. Allowed uppercase letters
exclude A/I/O; codes are the distinct assignments in the legend. Suffixes start at 2;
the article is `an` before a noun beginning with `a/e/i/o/u`, otherwise `a`.
An omitted binder name is allowed only if the body has no reference to it. A
guard must meet the syntactic/typing conditions above. These side conditions
define the canonical generated subset; the test parser can accept some other
equivalent spellings without the renderer generating them.

The constructive unambiguity argument is a left inverse: selected lexical
templates distinguish symbols and preserve all terms; prefix operator words
and balanced `unit` delimiters determine immediate children; quantifier lists
decode in the written order; guard syntax inserts exactly `Implies`; two
relative clauses insert exactly one `And`; typed inequality inserts exactly
`Not(Eq(...))`; validated negative atoms insert exactly `Not` around their
corresponding positive atom. Nearest-first scope lookup reconstructs each de Bruijn index.
Induction over those productions gives `decode(encode(A)) = A`, provided the
lexical codebook is injective. This is a grammar-level argument, **not a
machine-checked theorem about the Python implementation or about unrestricted
English readers**.

`tests/fluent_inverse.py` implements a deterministic recursive-descent inverse.
It receives only text and environment, never a source AST or a rendered-formula
lookup table. It shares the lexical codebook selection, but no structural
traversal with the renderer. `tests/explicit_inverse.py` independently decodes
the other four surfaces. `tests/test_fluent.py` checks exact AST recovery and
injectivity for all five views on **6,846 distinct well-typed ASTs** from
24,000 seeded draws, in both positive-only and checked-negative environments
(68,460 inverse checks total), all-pairs consistency of the five recovered ASTs,
and exact binder preorder including unnamed binders. Other checks cover 21 minimal pairs,
80 adversarial vocabularies, attacker-authored false negative templates,
same-initial sort names (up to all 32 permitted sorts), sibling scopes, multiple
statements, equality reversal, unused quantifiers, and maximum-depth fallback. Association
pairs are deliberately retained even when logically equivalent: the contract
preserves syntax, not just truth values. This empirical coverage complements
the inverse construction; neither is human readability evidence.

### Related-systems §2.4: ten rows and deviations

The examples use formal sort identifiers `item`/`agent` with nouns
`service`/`person`, and `active` with template `{0} is deployed`. Row 9 uses a
separate `audits(item, agent)` signature: rows 8 and 9 are not both well typed
under one `audits(agent, item)` declaration. Their displayed argument reversal
is intentional; cross-environment outputs do not establish semantic equivalence.

| Row | Fluent sentence | Deviation from the recommendation |
|---|---|---|
| 1 | for every service S that is deployed, S is reviewed. | Global universal and explicit reused subject. |
| 2 | for every service S that is deployed, there is a person P such that P owns S. | Global existential; no `who` pronoun. |
| 3 | there is a person P such that for every service S that is deployed, P owns S. | Universal stays in global form and in scope order. |
| 4 | it is false that (there is a service S such that both S is deployed and (it is false that S is reviewed)). | Explicit global witness, binary grouping, and no undeclared negative template. |
| 5 | for every service S that is deployed, it is false that S is reviewed. | `No service ...` is excluded; preserves `Forall(Implies(..., Not(...)))`. |
| 6 | it is false that (for every service S that is deployed, S is reviewed). | Global universal and grouped complex negation. |
| 7 | for every service S that is deployed and that is not the same service as @legacy, S is reviewed. | Global universal, named subject, and typed inequality. |
| 8 | for every person P and every service S, if P owns S then P audits S. | Exact. |
| 9 | for every person P and every service S, if P owns S then S audits P. | Exact sentence; separate typed environment as explained above. |
| 10 | for every service S and every person P and every person P2, if (both P owns S and P2 owns S) then P is the same person as P2. | `P2` replaces `Q`; explicit binary conjunction, uniform binder list, and typed equality. |

Reproduce all ten examples across all five views (50 renderings):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python tests/test_fluent.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run pytest -q tests/test_fluent.py tests/test_views.py
```

**Every experimental cell must use `ve.printer.render_cell(ast_or_document, env,
view, naming="per_statement", style="json")`, which always returns legend + rendering.**
The legend is byte-identical across all five views for a fixed style and naming
policy. `style="json"` is the unchanged default; `style="compact"` emits deterministic
plain text with one line per entry. Both styles use the same
`ve.vocabulary-legend@3` data, including the environment ID, all sort/predicate/constant
identifiers and descriptions, predicate argument sorts **in declared order**,
raw positive/negative metadata, selected templates/nouns (including fallback),
the naming scope and fluent letter-to-sort map and allocation rule, lint diagnostics,
and closure notes when applicable. Metadata is quoted data, not instructions
to the judge. Vocabulary ordering is independent of dictionary insertion order.
The low-level `render` still returns only claim text. `render_cell` cannot omit
the legend. CLI: `python -m ve render --env ENV.json --view ve_fluent --with-legend
--legend-style compact --naming per_statement CLAIM.ve`. The same options work with
`import-fol`. `--legend-style compact|json` selects the legend format; it does not
add a legend without `--with-legend`.
The legacy `natural` alias emits its JSON wrapper without `--with-legend`; with
that flag it emits the same complete plain-text cell as `ve_natural`.

`render_vocabulary(env, view="ve_strict", naming="per_statement", style="compact")`
returns just the compact legend. For example, entry lines can look like:

```text
Sorts:
  person (noun: "person"/"people") — "A recorded person."
  service (noun: "service"; declared: none) — "A recorded service."
Constants:
  @legacy : service — "The named legacy service."
Predicates:
  deployed(service) — "{0} is deployed" — "Recorded as deployed."
  owns(person, service) — "{0} owns {1}" — "Recorded ownership."; negative: "{0} does not own {1}"
  reviewed(service) — "{0} is reviewed" (strict fallback; declared: none) — "Recorded as reviewed."
Fluent variable letters: person = P, service = S
```

The first noun/template is always the selected rendering. A noun pair gives the
declared singular/plural, with the singular selected. Identical declared and
selected values appear once. `declared: none` records missing metadata; a differing
declaration is shown separately, including rejected positive/negative templates
and sort nouns. An omitted negative field means both negative values are absent;
`negative: none (declared: "...")` retains a rejected negative declaration.
Lint diagnostics remain authoritative when a rejected declaration happens to
have the same spelling as its strict fallback. Empty sections say `none`.
The complete legend also includes its format/environment ID, fluent variable rule,
naming policy and rule, lint diagnostics, and any closure context.

Compact metadata uses JSON string escaping for quotes, backslashes and C0 controls,
plus escapes for C1 controls, Unicode format controls (including bidi controls),
and Unicode line/paragraph separators. These escapes preserve the original values
while preventing an attacker-authored description or rejected template from
forging extra legend lines. Ordinary Unicode text remains readable. This is a
display safeguard; it does not establish the truth of a description.

Example legend lengths, in Unicode characters including the final newline, with
`naming="per_statement"`:

| Environment | JSON | Compact |
|---|---:|---:|
| `examples/environment.json` | 2,071 | 1,206 |
| `examples/fluent/environment.json` | 2,355 | 1,208 |

Reproduce the lengths and check information parity:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-views uv run pytest -q -s tests/test_legend.py -k example_legend_lengths
```

For E1, freeze and independently review the vocabulary before generating attacked
claims. Where the attacker authors vocabulary (E5), **the identical legend is
the defence**: every judge can inspect raw predicate identity, argument order,
and any misleading aliases. Lexical filtering alone does not defeat an arbitrary
semantic lie in trusted metadata. Do not claim that the natural phrase alone
carries all raw identity information, or that the legend guarantees a judge
will notice every mismatch.

```python
from ve import lint_vocabulary
from ve.printer import render_cell, measure_view_lengths, measure_jsonl_lengths
from ve.fluent import contraction_stats

issues = [issue.to_dict() for issue in lint_vocabulary(env)]
cell_text = render_cell(document, env, view, naming="per_statement", style="compact")
length_rows = measure_view_lengths(items, env, include_vocabulary=True, style="compact")
file_rows = measure_jsonl_lengths("items.jsonl", env, field="ast", style="compact")
guard_counts = contraction_stats(items, env)
```

`measure_view_lengths(items, env, include_vocabulary=False, naming="per_statement", style="json")` returns one row per
item per view, in input order then `VIEWS` order. Rows contain `item_index`, `view`,
`characters`, `tokenish`, and `includes_vocabulary`. Characters count Unicode
code points (including punctuation/newlines), not UTF-8 bytes. Token-ish length
counts matches of Unicode regex `\w+|[^\w\s]`: word runs or individual
non-whitespace symbols. With `include_vocabulary=True` it measures exactly
`render_cell(item, env, view, naming, style=style)`. Use the cell's legend style
when measuring it; measurement also defaults to JSON. Report these lengths as
covariates, and separately record counts from the actual model tokenizer when
available; this heuristic does not predict BPE charges for `∀` or `∧`.

`measure_jsonl_lengths(path, env, field="ast", source_format="ast",
include_vocabulary=True, naming="per_statement", style="json")` measures a real JSONL file.
Each line must be an object with the selected top-level field. Unrelated
metadata may contain JSON null and finite numbers; duplicate keys and nonfinite
numbers are rejected. AST fields accept
one tagged formula array or a document array of tagged formulas; `source_format="ve"`
accepts strict VE source including statement punctuation. Optional `id` becomes
`item_id`; a present `environment_id` must match. Rows retain `item_index` and
1-based `line`. Invalid/blank lines fail the operation, never disappear from the
denominator. The supplied environment must apply to the whole file. The helper
counts the actual rendered text and defaults to including the legend.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve view-lengths \
  --env ENV.json --field claim --source-format ve --naming per_statement \
  --legend-style compact items.jsonl
```

`contraction_stats(items, env, naming="per_statement")` in `ve.fluent` reports
`relative_guards`, `structural_guards`, and the subset `structural_both_guards`
(`such that (both ...)`), plus shares with all emitted universal guards as the
denominator. A two-relative-literal guard counts once. Uncontracted universal
groups are separate; existential `such that` does not count as a guard.
Negation counts visit every `Not` occurrence once: `whitelisted_negations`
(validated declared predicate negatives), `equality_negations` (typed inequality),
and `fallback_negations` (`it is false that`). Their shares use all `Not` nodes;
`whitelisted_predicate_negations_share` instead uses only predicate-atom
negations. Empty denominators produce `0.0`. The sample and exact denominators
are recorded in [the polish report](views-polish-report.md).

Full formula bracketing is shared by the four explicit views. Fluent contracts
only the reversible structures documented above. These checks do not establish
human readability or transfer to unrestricted English.
Review regressions and their precise limits are recorded in
[the review resolution](views-review-resolution.md).

Six reproducible examples in all five views, including checked negative atoms,
are recorded with the complete shared legend in [fluent examples](fluent-examples.md).
Regenerate the outputs with `examples/fluent_views.py`. Its historical banner
is outside this task's edit scope; correct that one sentence when regenerating:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run --frozen python examples/fluent_views.py | \
  sed 's/are unique across statements\./restart in each statement under the default naming policy./' \
  > docs/fluent-examples.md
```

`test_committed_item_file_lengths_and_example_documentation` checks the current
renderings, legend, and corrected banner against this committed document.
