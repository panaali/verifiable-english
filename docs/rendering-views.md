# Deterministic rendering views, version 2

`ve.render(ast, env, view)` returns text for a closed formula or a `Document`.
`view` is `fol_symbols`, `fol_keywords`, `ve_strict`, `ve_natural`, or `ve_fluent`. A single
formula has no final punctuation. Documents append a period and LF to every
statement; natural documents capitalize each statement's first letter.
`print_formula` and `print_document` retain the exact strict canonical bytes.
`natural_formula` and `natural_document` additionally return environment and
meaning IDs with renderer `ve.ace-explicit`, version `1`.

The first four surfaces use **one recursive traversal** in `ve/printer.py`. It assigns
`x0`, `x1`, ... to binders in preorder, resets at each statement, resolves every
variable through the same nearest-first scope stack, and visits operands in AST
order. Every immediate **formula operand**, including an atomic operand, is
parenthesized. No surface changes this grouping policy or elides a binder,
operand, statement, or condition. FOL predicate application `p(t)` / `r(t,u)`
has additional lexical argument-list delimiters; these do not group formulas.
The natural surface retains the common grouping, even where fluent prose could
omit parentheses. The fifth surface uses `ve/fluent.py`, follows the same binder
and operand preorder, and contracts only structures with an explicit inverse
(see below). None of these views reorders or simplifies the AST. The existing
four views and `ve.ace-explicit` renderer version remain byte-for-byte unchanged.

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
unary_template    = "{0} is ", phrase ;
binary_template   = "{0} ", phrase, " {1}" ;
sort_noun         = phrase ;
```

A phrase cannot contain any word in this reserved display set:

```text
all any every some no none not never neither nor and or both either if then
unless except without only exists forall implies true false equal equals there
such that case condition for at least most exactly does do must may can cannot
should shall will would whenever when iff otherwise always sometimes one two
three four five six seven eight nine ten a an the
```

Each argument placeholder occurs exactly once, in declared order. There are no
format conversions, attributes, escapes, punctuation, parentheses, embedded
variables, or executable expressions. The renderer performs literal placeholder
replacement, never evaluates supplied formatting code. A template is a declared
positive atomic relation phrase, not a place to add quantifiers or conditions.
The binary phrase must start with a word ending in `s` (the supported finite
verb spelling, e.g. `owns`, `depends`, `has`, `is`); bare `is` is excluded to
avoid an implicit equality rendering. Unary templates require an explicit
copula and nonempty complement. These lexical restrictions do not constitute
an English grammar checker: vocabulary authors remain responsible for selecting
grammatical, accurate atomic phrases. Unsupported forms use strict fallback.
Plural nouns are retained for vocabulary display but are not used to replace
explicitly bound singular variables. The existential article is `an` for a noun
beginning with `a/e/i/o/u`, otherwise `a`; authors should use nouns for which this
simple rule is appropriate.

A candidate predicate template is used only if it is unique among the usable
templates in the complete vocabulary and does not equal another predicate's
strict atomic template. Otherwise that atom uses the strict rendering. A sort
noun must be unique and must not equal a different sort identifier; otherwise
its sort identifier is used. Unsafe or unsupported template syntax also falls
back to strict text. These checks apply across the complete environment,
including symbols absent from the current formula. Thus two symbols cannot
collapse to one displayed atom or binder sort. Logical constructs always have
an explicit representation in the table above; none is paraphrased away.

For the example above, the natural document is:

```text
For every service x0: (if (x0 is deployed), then (there is a person x1 such that (x1 owns x0))).
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
Freeze and independently review the vocabulary before generating attacked claims;
template accuracy must not be chosen by the attacker for a particular cell.

## Fifth view: `ve_fluent` (renderer `ve.fluent`, version `1`)

`render(formula, env, "ve_fluent")` and
`render_fol(env, document, view="ve_fluent")` provide a deterministic read-only
surface. Fluent formulas capitalize their first letter; documents additionally
append a period and LF per statement. Constants still retain `@identifier`.
Every bound scope remains visible in surface order. There are only global
quantifiers: `For every ...` and `There is a ... such that ...`. In particular,
the E1 passive **“Every service is owned by a person” is never generated**.
Relational templates headed by `is`, `was`, or `gets`, or containing ` by `,
use strict atomic fallback. Unsupported lexical syntax and collisions use the
same conservative vocabulary policy as the natural view. Atomic phrases remain
declared vocabulary assertions, not mechanically verified descriptions of the world.

The changes from the four explicit surfaces are:

- Names use the initial capital letter of the selected sort noun, with numeric
  suffixes on collisions: `S`, `P`, `S2`, `P2`. Allocation follows binder preorder
  across sibling scopes, with a fresh counter for each statement. **The binder
  declaration counts as the first mention:** its name is included exactly when
  the body refers to that binder. Thus an unused existential reads `There is a
  person such that true`; an existential occurring once in the body reads `There
  is a person P such that P owns S`. Removing that `P` would need `who`, another
  pronoun, or a nonglobal existential contraction, all excluded by this grammar.
  Unused binders retain their sort, operator, scope, and existence meaning.
- A single universal whose body is an implication with a conjunctive guard uses
  `For every service S that is deployed, ...`. Each guard leaf must be an atom
  or negated atom mentioning the bound variable. Relative clauses omit only the
  bound subject; object occurrences remain explicit. One literal or exactly two
  relative literals can be spelled `that ... [and that ...]`. Larger guard trees
  and object-position guards use `such that <unit>`, preserving every binary
  conjunction node. Guards always decode to an **implication**, never to a
  conjunction or an existential.
- Consecutive universals are listed in order: `For every person P and every
  service S, if P owns S then P audits S`. The list means nested universals in
  exactly that order. A multi-binder list keeps its antecedent in the explicit
  `if` clause; it does not attach a relative clause to an uncertain binder.
- Equality is `P is the same person as P2`; its negation is `P is not the same
  person as P2`. The noun is the checked term sort, with the same safe aliases.
  Argument order is retained even for symmetric equality.
- Negation otherwise uses `it is false that <unit>`. **The current environment
  schema supplies only positive templates** (`verbalisation: string`), and has no
  negative-template field. Therefore v1 does not guess inflections such as
  `owns` → `does not own`, nor treat a declared negative-looking positive
  predicate as logical negation. Even `not reviewed` uses the explicit form.
  Adding identity-bound negative templates belongs to a later vocabulary-schema
  change; no schema or identity change is part of this renderer task.
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

The grammar below describes the lowercase internal surface. Capitalize only the
first character for a complete formula; remove that capitalization before
decoding reserved initial words. Document framing is `sentence, ".", LF`,
repeated with independent binder counters. Lexical expansions come from the
fixed environment, selected using the collision policy above.

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
atom = "true" | "false" | positive_atom
     | term, " is the same ", noun, " as ", term
     | term, " is not the same ", noun, " as ", term ;
guard = relative, [ " and ", relative ] | "such that ", unit ;
relative = "that ", atomic_tail ;
declaration = noun, [ " ", variable ] ;
term = variable | "@", identifier ;
variable = uppercase_ASCII_letter, [ positive_integer_suffix ] ;
article = "a" | "an" ;
```

`noun` is a safe sort noun or formal identifier, `positive_atom` is a selected
positive template or strict fallback, and `atomic_tail` is that selected atom
without its subject, or the tail of a typed (in)equality. Relative templates are
used only when the environment actually supplies the supported positive form.
`identifier` is the environment's ASCII identifier syntax. Suffixes start at 2;
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
`Not(Eq(...))`. Nearest-first scope lookup reconstructs each de Bruijn index.
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
24,000 seeded draws, all-pairs consistency of the five recovered ASTs, and exact
binder preorder including unnamed binders. Other checks cover 21 minimal pairs,
80 adversarial vocabularies, same-initial sort names, sibling scopes, equality
reversal, unused quantifiers, and maximum-depth structural fallback. Association
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
| 1 | For every service S that is deployed, S is reviewed. | Global universal and explicit reused subject. |
| 2 | For every service S that is deployed, there is a person P such that P owns S. | Global existential; no `who` pronoun. |
| 3 | There is a person P such that for every service S that is deployed, P owns S. | Universal stays in global form and in scope order. |
| 4 | It is false that (there is a service S such that both S is deployed and (it is false that S is reviewed)). | Explicit global witness, binary grouping, and no undeclared negative template. |
| 5 | For every service S that is deployed, it is false that S is reviewed. | `No service ...` is excluded; preserves `Forall(Implies(..., Not(...)))`. |
| 6 | It is false that (for every service S that is deployed, S is reviewed). | Global universal and grouped complex negation. |
| 7 | For every service S that is deployed and that is not the same service as @legacy, S is reviewed. | Global universal, named subject, and typed inequality. |
| 8 | For every person P and every service S, if P owns S then P audits S. | Exact. |
| 9 | For every person P and every service S, if P owns S then S audits P. | Exact sentence; separate typed environment as explained above. |
| 10 | For every service S and every person P and every person P2, if (both P owns S and P2 owns S) then P is the same person as P2. | `P2` replaces `Q`; explicit binary conjunction, uniform binder list, and typed equality. |

Reproduce all ten examples across all five views (50 renderings):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python tests/test_fluent.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run pytest -q tests/test_fluent.py tests/test_views.py
```
