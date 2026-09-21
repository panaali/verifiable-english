# Deterministic rendering views, version 1

`ve.render(ast, env, view)` returns text for a closed formula or a `Document`.
`view` is `fol_symbols`, `fol_keywords`, `ve_strict`, or `ve_natural`. A single
formula has no final punctuation. Documents append a period and LF to every
statement; natural documents capitalize each statement's first letter.
`print_formula` and `print_document` retain the exact strict canonical bytes.
`natural_formula` and `natural_document` additionally return environment and
meaning IDs with renderer `ve.ace-explicit`, version `1`.

All four surfaces use **one recursive traversal** in `ve/printer.py`. It assigns
`x0`, `x1`, ... to binders in preorder, resets at each statement, resolves every
variable through the same nearest-first scope stack, and visits operands in AST
order. Every immediate **formula operand**, including an atomic operand, is
parenthesized. No surface changes this grouping policy or elides a binder,
operand, statement, or condition. FOL predicate application `p(t)` / `r(t,u)`
has additional lexical argument-list delimiters; these do not group formulas.
The natural surface retains the common grouping, even where fluent prose could
omit parentheses. None of these views reorders or simplifies the AST.

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

Use the same environment, AST, renderer version, and grouping policy in all E1
cells. Record the actual view alongside claim/environment IDs. A display-only
metadata change still changes the environment identity and requires regenerating
all cells consistently. The natural grammar is read-only; only `ve_strict` is
accepted by the VE source parser.
Freeze and independently review the vocabulary before generating attacked claims;
template accuracy must not be chosen by the attacker for a particular cell.
