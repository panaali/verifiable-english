# Deterministic rendering views, version 2

`ve.render(ast, env, view)` returns text for a closed formula or a `Document`.
`view` is `fol_symbols`, `fol_keywords`, `ve_strict`, or `ve_natural`. A single
formula has no final punctuation. Documents append a period and LF to every
statement. All views preserve lexical case without sentence capitalization.
`natural_formula(...).text` follows the same unpunctuated formula policy.
Every view has the same 65,536-byte UTF-8 output limit; formula checks reserve
two bytes for the period and LF of a possible one-statement document.
`print_formula` and `print_document` retain the exact strict canonical bytes.
`natural_formula` and `natural_document` additionally return environment and
meaning IDs with renderer `ve.ace-explicit`, version `2`. Version 2 changes
natural case/punctuation and template acceptance; regenerate prior natural views.

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
three four five six seven eight nine ten a an the lacks
```

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
(e.g. `deployed` → `undeployed`). Variable tokens `x`, `xN`, and single capital
letters are rejected. Capitals are also excluded by the lowercase grammar.
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
| `TEMPLATE_SHAPE` | Missing, misplaced, or unsupported placeholder/copula structure |
| `PHRASE_SYNTAX` | Unsupported characters, placeholders in a phrase, spacing, or case |
| `LOGICAL_WORD` | Reserved quantifier, connective, negation, or other display word |
| `VARIABLE_TOKEN` | `x`, `xN`, or a single capital letter |
| `SYMBOL_COLLISION` | Word equals another identifier or lexical head |
| `NEGATED_HEAD` | Negating prefix applied to a predicate identifier/head |
| `BINARY_AUXILIARY` | Forbidden leading copula/auxiliary |
| `BINARY_CONVERSE` | Forbidden final preposition |
| `BINARY_VERB` | Binary first word does not end in `s` |
| `UNARY_MODIFIER` | More than one complement word after unary `is` |
| `DUPLICATE_TEMPLATE` | More than one predicate declares the same template |
| `SORT_COLLISION` | Noun equals another sort's identifier or noun |

These checks are a **heuristic, not a proof** of English meaning or injectivity.
Templates and sort nouns are **trusted vocabulary data**, as are descriptions.
An arbitrary alias, for example `service` → `owner` or `person` → `asset`, can
remain accepted if it collides with no declaration. The linter cannot establish
its truthfulness. Experiments must not treat an empty lint report as validation
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

Use the same environment, AST, renderer version, and grouping policy in all E1
cells. Record the actual view alongside claim/environment IDs. A display-only
metadata change still changes the environment identity and requires regenerating
all cells consistently. The natural grammar is read-only; only `ve_strict` is
accepted by the VE source parser.

**Every experimental cell must show `render_vocabulary(env, view)` alongside its
claim text.** This API returns byte-identical deterministic JSON text for all
four views. It includes the environment ID, all sort/predicate/constant
identifiers and descriptions, predicate argument sorts **in declared order**,
raw verbalisation metadata, the selected natural template/noun (including strict
fallback), and lint diagnostics. Metadata is JSON-quoted data, not instructions
to the judge. Vocabulary ordering is independent of dictionary insertion order.
The legend is separate from `render`; callers are responsible for displaying it.

For E1, freeze and independently review the vocabulary before generating attacked
claims. Where the attacker authors vocabulary (E5), **the identical legend is
the defence**: every judge can inspect raw predicate identity, argument order,
and any misleading aliases. Lexical filtering alone does not defeat an arbitrary
semantic lie in trusted metadata. Do not claim that the natural phrase alone
carries all raw identity information, or that the legend guarantees a judge
will notice every mismatch.

```python
from ve import lint_vocabulary, render, render_vocabulary, measure_view_lengths

issues = [issue.to_dict() for issue in lint_vocabulary(env)]
cell_text = render_vocabulary(env, view) + render(document, env, view)
length_rows = measure_view_lengths(items, env, include_vocabulary=True)
```

`measure_view_lengths(items, env, include_vocabulary=False)` returns one row per
item per view, in input order then `VIEWS` order. Rows contain `item_index`, `view`,
`characters`, `tokenish`, and `includes_vocabulary`. Characters count Unicode
code points (including punctuation/newlines), not UTF-8 bytes. Token-ish length
counts matches of Unicode regex `\w+|[^\w\s]`: word runs or individual
non-whitespace symbols. With `include_vocabulary=True` it measures exactly
`render_vocabulary(env, view) + render(item, env, view)`. Report these lengths as
covariates, and separately record counts from the actual model tokenizer when
available; this heuristic does not predict BPE charges for `∀` or `∧`.

Full formula bracketing is shared by all views and is deliberately explicit.
Results do not establish transfer to fluent ACE prose or unbracketed English.
Review regressions and their precise limits are recorded in
[the review resolution](views-review-resolution.md).
