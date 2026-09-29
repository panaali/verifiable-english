# W6: quantities, unit identity, and calendar conventions

> Status: **converged REVISE applied**, 2026-09-28; repository baseline
> `9db5a20`, original draft `6923008`. This specifies W6 of [PLAN-EXPAND2](../../PLAN-EXPAND2.md#w6-quantities-in-documents-dates-scaled-decimals-counting-sugar-and-finite-traces-on-top-of-order0).
> This revision applies [Astra round 2](/home/seyran/code/manage-agents/debates/design-units/astra.md#round-2-2026-09-27t2354z)
> plus [Fable round 3(a–c)](/home/seyran/code/manage-agents/debates/design-units/fable.md#round-3-2026-09-28t0001z),
> as selected by the writing task. Rule 10 and decision 9.3 still require
> section re-review of the amended contracts before build. No implementation,
> Lean proof, or coverage gain is claimed. This revision uses no model calls.
>
> Priority: [NORTH-STAR, rank 3](/home/seyran/code/ve-northstar/NORTH-STAR.md#feature-priority),
> commit `01b1090`: quantities/units and graded comparisons, with separate open
> treatment of vague degrees. NORTH-STAR is in that sibling worktree, not yet
> this baseline. Its 119 primary quantity blockers / 17,530 opportunity bytes
> in the full Claude constitution are an upper-bound planning inventory, not
> W6's promised gain. Counting (rank 9) and time (rank 11) retain their own limits.

## 1. Scope and the statement the author approves

A quantity is an exact integer coordinate together with a declared unit tag.
The tag says how the coordinate is read and displayed. For example, `375:bp`
means `3.75%`; `375:usd_cent` means `USD 3.75`. Equal coordinates do not make
these interchangeable quantities. The checked statement includes the tags,
the declaration of each named quantity, and any calendar conventions used.

W6 adds exact finite decimals, date literals, homogeneous linear arithmetic,
explicit comparisons, bounded counting sugar, and the calendar elaborations
below. It adds no real-number solver, dimensional algebra, automatic unit
conversion, measurement evidence, probability logic, or numerical semantics
for words such as “high”, “slightly”, or “more important”. A reported number
can be represented exactly without asserting that its measurement is exact
or that the reported claim is true.

The checker remains `order@0`. `time@0` is the planned statement-layer profile
for this slice, including decimal/unit syntax; no new `units@0` checker or
`Count` AST node is introduced. The quantity route requires `ve.core@0.2`,
`order@0`, `relational-fol@0`, and `time@0`, with the usual sorted profiles.
Documents additionally enable `documents@1`. Existing envelopes, AST encodings,
strict printers, identities and certificates stay byte-identical. W6 uses a
separate annotated statement representation and erases it into the existing
integer AST only after admission.

`order@0` with `nary@0` or `closure@0` remains unsupported. Numeric news examples
can use named integer constants or existing unary/binary integer slots; a
ternary `value(signal, integer_time, integer_value)` is not a W6 shortcut.
W4 stage 1 event/time relations use user sorts. Integer-time n-ary relations
and combined closure/order reasoning await W4 stage 2.

## 2. Declarations and exact values

### 2.1 Unit declarations

The new environment extension is `unit_schema: "ve-units@1"` and `units`, a
map from unit identifiers to records. These fields are admitted only on the
W6 route. An absent extension preserves the old environment bytes and enables
none of this syntax. An explicit but empty extension is a distinct environment.
These are `document.environment.unit_schema` and `document.environment.units`;
`document.units` remains the array of source units. There is no field collision
and no `unit_tags` rename. One complete nested front-matter example, for the
source bytes `3.75% < 4.00%.\n` (15 UTF-8 bytes), is:

```json
{
  "format": "ve-document@1",
  "environment": {
    "language": "ve.core@0.2",
    "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {"sorts": {}, "predicates": {}, "constants": {}},
    "unit_schema": "ve-units@1",
    "units": {"bp": {"scale": "100", "display": {"kind": "percent"}}}
  },
  "units": [{
    "id": "bounds", "span": [0, 15], "kind": "asserted",
    "meaning": "specified", "support": "assumption",
    "content": {"quantity": {
      "format": "ve-quantity@1", "traces": [],
      "formula": ["lt", ["decimal", "bp", "3.75"], ["decimal", "bp", "4.00"]]
    }}
  }]
}
```

This is proposed W6 input, not currently accepted input. Section 3 defines
the submitted literal forms and their canonical identity representation.
The two fields must occur together. In an extended environment, legacy-shaped
formula content is interpreted only as dimensionless source input and must
pass the same annotated admission; it cannot bypass tagged signature checks.
The record is the plan's `(integer scale, display form)`, made executable:

```json
{
  "unit_schema": "ve-units@1",
  "units": {
    "bp": {"scale": "100", "display": {"kind": "percent"}},
    "usd_cent": {"scale": "100", "display": {"kind": "money", "currency": "USD", "input_symbol": "$"}},
    "day": {"scale": "1", "display": {"kind": "iso_date"}},
    "elapsed_day": {"scale": "1", "display": {"kind": "decimal", "label": "days"}},
    "calendar_year": {"scale": "1", "display": {"kind": "decimal", "label": "calendar year", "placement": "prefix"}},
    "age_year": {"scale": "1", "display": {"kind": "decimal", "label": "completed years of age"}}
  }
}
```

This is an environment **fragment**, not a complete environment or currently
accepted input. The reviewed implementation must expose it through P0's
environment hook, without editing existing `ve/ast.py` constructors.

* Tags obey the existing identifier rules. `dimensionless` is reserved and
  implicit, with scale 1 and bare-integer display; it cannot be redeclared.
  Calendar operations additionally reserve `day` and `elapsed_day`: when
  present, their declarations must be exactly the records shown above.
  `iso_date` display is permitted only for `day`. Other tags, including
  `calendar_year` and `age_year`, have no built-in calendar/age semantics.
* `scale` is a positive power of ten, serialized as a canonical integer string.
  Zero, negative scales, fractions, booleans and floating-point JSON are errors.
  W6 narrows the plan's unspecified integer scales to powers of ten so every
  coordinate has a terminating decimal display. The existing 40-character
  integer-literal limit also bounds scales and lowered literals.
* `display` is data from the closed kinds above, never executable formatting.
  Decimal precision is `log10(scale)`; decimal rendering emits that many digits
  after the point. Scale 1 emits none. Date display requires scale 1 and uses
  section 6's fixed calendar/epoch. `percent` appends `%`; `money` prefixes the
  declared three-uppercase-ASCII-letter currency and a space; `decimal`
  appends a space and its label unless `placement: "prefix"` is declared,
  in which case it prefixes the label and a space. For `decimal`, the optional
  placement is exactly `prefix` or `suffix`, defaulting to `suffix`.
  Labels must be nonempty, bounded strings
  under the existing verbalisation limit. `money.input_symbol` is an optional
  nonempty input prefix under that same limit, and is identity-bound.
  Unknown fields/kinds are rejected. These formatting records assert no
  exchange rate, currency equivalence or physical interpretation.
* Tag equality is identifier equality in **one environment identity**, not
  equality of scales, labels or an inferred physical dimension. Two tags with
  identical declarations remain incompatible. Different currencies need
  different tags. `%` is not a universally shared quantity type.
* Environment admission requires injective display forms on the enabled
  surface: at most one `percent` tag, one tag per currency code, one tag per
  `input_symbol`, and pairwise distinct `decimal` labels. Other collisions
  between enabled forms also reject; a unit identifier is never an English
  disambiguation escape. `$3.75` in the example binds to USD and canonically
  renders `USD 3.75`. The parser never guesses a tag from context.

Unit declarations, including unused ones and display labels, enter
`environment_id`. The source claim's context (which estimate, whose age, which
forecast date) belongs in identity-bound vocabulary declarations and document
content. A unit tag alone does not identify a measured property or its evidence.

### 2.2 Signature slots, constants and binders

Every `$int` predicate slot has a tag. Extend a predicate declaration with
`argument_units`, a map from zero-based slot indices written as canonical
decimal strings to declared tags. Only `$int` slots may occur in this map;
omitted `$int` slots mean `dimensionless`. For example, a binary predicate with
`arguments: ["estimate", "$int"]` and `argument_units: {"1": "bp"}` takes a
percentage coordinate in its second slot. This does not make it functional or
total; those are separate W5 declarations with their own integration gates.

An integer constant may similarly declare `unit: "bp"`; omission means
`dimensionless`. A non-integer constant cannot carry `unit`. Reusing a constant
under a new tag at one occurrence is rejected. Each integer binder specifies
one tag, and every occurrence of its de Bruijn variable must have that tag.
User-sort binders/terms have no unit annotation. Nested scopes and substitution
preserve both index and tag; variable names never establish compatibility.

Unannotated integer source terms/binders are dimensionless. The surface may
lower a `%` or currency token to an explicit tag, but cannot infer a missing
tag from the other operand or from a predicate slot. Thus bare `375` cannot
silently become `3.75%`. Explicit and omitted dimensionless annotations
canonicalize identically within the new representation.

### 2.3 Decimal lowering and arithmetic

For signed decimal text with significand integer `m` and `p` decimal places,
and tag scale `s`, lowering succeeds exactly when `m * s / 10^p` is an integer.
Use integer arithmetic, never binary floating point. There is no rounding,
clamping, guessed precision, or implicit tolerance. Trailing zeros may be
discarded on input; scientific notation and thousands separators are outside
the first surface. Negative zero canonicalizes to zero before identity.

| Input | Tag / integer | Canonical display or rejection |
|---|---|---|
| `3.75%` | `bp / 375` | `3.75%` |
| `3.7%`, `3.700%` | `bp / 370` | `3.70%`; same annotated meaning |
| `3.755%` | — | `UnitPrecision(bp, scale=100)`; never `3.76%` |
| `USD 12.30` | `usd_cent / 1230` | `USD 12.30` |
| `-0.25%` | `bp / -25` | `-0.25%` |
| bare `375` | `dimensionless / 375` | `375` |

Equality and every order comparison require identical tags. Negation and
integer scaling preserve the tag; the coefficient is a literal integer, not
a quantity or a second variable. Addition/subtraction require identical tags
and return that tag. This is the existing linear integer fragment: no products
of variables, division of quantities, general ratios, cross-tag arithmetic or
comparison. Zero has a tag too; bare zero is not a universal neutral operand.
Date coordinates are the exception to generic addition/scaling: point-plus-
point and scaled calendar dates are rejected; section 6 supplies explicit
date-shift/difference elaborations.

A percentage *level* and a percentage-point *change* use the same `bp` grid:
`3.75% - 3.50%` is a difference of 25 ticks, displayed in that expression as
`0.25 percentage points`. This is same-tag subtraction, not a conversion to
a new tag. The renderer recognizes the difference expression; a standalone
change quantity needs an identity-bound declaration naming it as a change.
“N percentage points” is an input alias for a `bp` literal only on the
right-hand side of an equality stating a same-tag difference, as in section 4;
it renders with the same wording there and rejects elsewhere. This alias does
not introduce a new tag or authorize relative-percentage arithmetic.
“Increased by 0.25%” is not rewritten to “increased by 0.25 percentage points”:
the former may be a relative change. No rate baseline is invented.

## 3. Annotated statements, identity and admission

### 3.1 Canonical representation

A W6 document submits
`{"quantity":{"format":"ve-quantity@1","formula":S,"traces":T}}`.
`S` is the pre-lowering statement tree supplied to Lean, not merely the
already-lowered coordinates. It uses the annotated grammar below plus the
literal forms `["decimal", tag, decimal_string]` (arity 2) and
`["date", iso_date_string]` (arity 1, fixed tag `day`). Decimal strings carry
the signed value in the declared display unit, without a percent/currency
suffix; date strings use section 6.1's ISO form. Lean executes the exact
decimal conversion underlying `Time.decimal_exact` and the proved date
conversion, rejecting invalid or off-grid literals, to regenerate `Q`.
Already-coordinate `["num", tag, integer_string]` input is permitted but
asserts only that coordinate, not correspondence to a different source literal.

`T` is the trace-declaration array specified in section 6.4; omission
canonicalizes to `[]`. An optional `Q` field in the submitted quantity object
is an untrusted claimed lowered tree and must equal regeneration structurally.
It is omitted from the canonical identity payload. The latter is exactly
`{"format":"ve-quantity@1","formula":Q,"traces":T}` with canonical `T`.
Unknown fields reject. Counting sugar has already expanded before `S` and
identity; it has no separate counting wire node. `Q` is a separate
statement-layer tree: existing formula constructors are retained, but each
integer term and integer binder carries its tag. In this tree alone:

```text
integer term: ["num", tag, integer_string]
              ["const", tag, name]
              ["var", tag, de_Bruijn_index]
              ["add", tag, left, right]
              ["scale", tag, coefficient_string, term]
integer binder: ["forall", "$int", tag, body]
                ["exists", "$int", tag, body]
formula example:
  ["lt", ["num", "bp", "360"], ["num", "bp", "370"]]
erased formula:
  ["lt", ["num", "360"], ["num", "370"]]
```

Object terms/binders keep the existing representation. Missing annotations
are completed to `dimensionless` by source elaboration; the canonical wire
tree requires all integer annotations explicitly. There is no sparse map
whose omitted entry can be interpreted differently by two readers. Decoders
select this grammar only under `ve-quantity@1`; legacy AST decoders must not
accept these extra fields. Temporal forms are specified in section 6 and are
regenerated in Lean; a sender cannot substitute their claimed expansion.
The literal-only `decimal` and `date` nodes never survive in `Q`.

The quantity `meaning_id` uses the existing environment-bound v0.2 meaning
domain, with the entire canonical `ve-quantity@1` object as its `ast` payload,
following the precedent of the W1 norm block. The erased formula has its own
existing core meaning identity. These are distinct artifacts. Canonical
decimal spelling differences disappear before quantity identity, while
`source_id` still distinguishes the original text. General arithmetic is not
normalized: commuted sums retain distinct AST identities, as under `order@0`.

Binding only the environment is insufficient: in an environment declaring
both `bp` and `usd_cent`, two occurrences of `375` can have different meanings.
Changing an occurrence or binder tag must change the quantity `meaning_id`
even when the erased AST and `environment_id` remain unchanged.

### 3.2 The gate before erasure

For each premise, conclusion, active definition/background formula, and
formula reached through a reading or citation, the W6 route must:

1. Decode the environment and annotated statement; reject unsupported profile
   combinations, unknown tags, malformed fields and exhausted resource limits.
2. Reconstruct scope and check every term, constant, binder, signature slot,
   comparison, and arithmetic operation. Check calendar operations separately.
   Python provides early diagnostics; Lean `Time.units_admit` is authoritative.
3. From submitted `S`, regenerate literal lowering in Lean and require any
   supplied `Q` to equal that annotated result structurally. Regenerate the
   calendar/trace operations retained in `Q`, then obtain the erased formula
   and target environment. Decode no user-supplied erased formula as authority;
   if one accompanies the source, require structural equality with regeneration.
4. Verify the quantity identity, erased identity, environments, profiles,
   generated premises, and checker-build bindings on the composed P0 route.
   Replay the existing order certificate only for that regenerated problem.
5. Bind the report and transitive support to the approved annotated statement,
   including reading choices, open-term versions and bridge leaves. Render
   quantities from those annotations, including counterexample values.

The English route must derive `S` uniquely from the text, and any accompanying
`S`, `Q`, or `meaning_id` must agree with that derivation and its regeneration.
In particular, `3.75%` supplies `["decimal", "bp", "3.75"]`: pairing it with
an individually well-typed `376:bp` in a supplied `Q` rejects in Lean, before
erasure. Hashing both objects does not establish correspondence. Text-to-`S`
fidelity remains the surface/W8 gate, with Python/Rust differential checks;
Lean checks the submitted literals, not the original English bytes. Retain
the counting theorem and substitution tests without claiming that Lean can
recover original counting sugar from its already-expanded input.

Raw order certificates remain valid for their old raw order claims. They
cannot by themselves certify a W6 quantity statement. Relabelling an erased
proof from percent to money must fail the outer binding even if the inner
integer proof is valid. The same rule covers model evaluation, countermodel
replay, equivalence, citation and document composition. No call site may erase
first and check tags later. Unsupported definition/norm/data combinations
remain explicitly gated; recognizing all profile names does not prove their
joint route sound.

The erased target environment retains the vocabulary's symbols, sorts and
profile envelope, removing only this extension's declaration fields. Its
identity is recomputed, not copied from the annotated environment. The outer
route binds the source/target environment pair and each premise/conclusion
pair; it must check this relation rather than trust supplied target IDs.

Rust must decode/validate the same declarations and annotated inputs for the
W6 conformance family, then evaluate regenerated integer formulas. It may
reject an unsupported route, but must not silently ignore annotations.
Python/Rust success alone cannot upgrade a quantity claim to Lean-checked.

Unit tags are nominal copies of the integer coordinate domain, not refined
subsets: `bp` does not implicitly assert `0 <= value <= 10000`, positivity,
measurement accuracy, or probability. Explicit bounds are ordinary premises.
The units-only layer generates no new logical background premises. Its
restriction/expansion maps are the identity on underlying structures; term
interpretation keeps the coordinate and its admitted tag. Calendar guards
are visible formula content, never hidden model-validity assumptions.

## 4. One-reading English and the boundary of grading

The following are proposed controlled wordings, to register and test under
P0/W7; their presence here does not claim parser support. Quantity names such
as “the September PCE estimate” stand for single declared constants with
approved verbalisation, not an unproved functional lookup.

| English | Sole admitted reading |
|---|---|
| “The September PCE estimate equals 3.70%.” | equality to `370:bp` |
| “The September PCE estimate is greater than the June PCE estimate.” | June `<` September, same tag |
| “The lower target bound is at least 3.75%.” | `375:bp <= lower`; inclusive |
| “The upper target bound is at most 4.00%.” | `upper <= 400:bp`; inclusive |
| “The reported rate is from 3.75% through 4.00%, including both bounds.” | conjunction of the two inclusive inequalities |
| “The September estimate minus the June estimate equals 0.10 percentage points.” | September minus June `= 10:bp`; ordered subtraction |
| “For every integer n, n is at most n.” | dimensionless binder and occurrences; **gated on numbers2** |
| “For every percentage q, q is at most 4.00%.” | all integer coordinates in the sole percent-display tag (`bp` here); no hidden finite domain; **gated on numbers2** |
| “The return date is after 2026-09-16.” | section 6's guarded strict date-coordinate comparison |

“Between”, “by”, “over”, “higher”, “within a month”, bare “always”, and an
unqualified percentage change do not acquire a default numerical reading.
Use an explicit wording, an admitted reading set, or an unformalised residual.
As elsewhere, every accepted English input must have exactly one derivation
in the enabled whole grammar. Multiple derivations reject with both parses;
budget exhaustion rejects naming the budget. Round-trip examples alone do
not establish unambiguity. Existing English environments render unchanged.

There are three separate cases for graded language:

* **Declared numeric measure and comparison:** an inequality between two
  same-tag values has exact meaning. The measurement method and the truth of
  supplied values still need support. “Higher” is numerical only after its
  measure, compared objects, direction and context are explicit.
* **Declared ordinal relation:** a named relation such as `preferred_to(a,b)`
  can express an authored ordering over user objects. Transitivity, totality,
  distances and weights do not follow merely from the name. This is existing
  relational vocabulary, not a W6 decimal interpretation of source prose.
* **Vague degree or evaluative comparison:** “substantially higher standards”,
  “vast majority”, “sufficient speed”, and “very high priority” have no supplied
  metric/cutoff. Keep a W2 open term with its decider, factors, jurisdiction and
  version, or keep the span unformalised if no reading is admitted. The schema
  never chooses 90%, a weight of 10, an epsilon, or a time limit on the author's
  behalf. Normative priority remains the norms/soft-norms workstream.

For “growth rose slightly from 2.2% to 2.3%”, the values and strict increase
can have a checked numeric spine. “Slightly” retains its own residual. Source
partitioning must preserve those bytes and their scope; a checked subclaim
does not promote the whole sentence. Hypotheticals, forecasts, attributed
claims and obligations keep their W2 kinds. Extracting a number never licenses
an assertion that its surrounding proposition holds in the actual world.

## 5. Counting and ratios remain separate from scalar quantities

An integer value `1000` fits W6. A claim that 1,000 **distinct people** satisfy
a property needs counting semantics; storing `1000` in a field does not prove
that cardinality. Preserve the plan's expansion, with fresh, capture-avoiding
binders and each distinctness test nested under the binder it constrains:

```text
atLeast(0, P) = true
atLeast(n, P) = exists x1. P(x1) and
                 exists x2. x2 != x1 and P(x2) and ...
                   exists xn. (and over i < n: xn != xi) and P(xn)
exactly(n, P) = atLeast(n, P) and not atLeast(n+1, P)
atMost(n, P)  = not atLeast(n+1, P)
n of the m S are P = exactly(m, S) and exactly(n, S and P)
```

Canonical conjunctions are right-associated, with no trailing `true`. Under
binder `xj`, list `xj != x1`, ..., `xj != x(j-1)` in that order, then `P(xj)`,
then the next existential if present. Each inequality is `not (xj = xi)`;
the predicate comes after distinctness tests. Preserve the displayed order
of the two conjuncts in `exactly` and `n of the m`, and of `S and P`.
Fresh binders shift outer indices capture-safely. This fixes the expanded
AST identity as well as the evaluator's traversal; equivalent reassociation
is not the canonical expansion.

Counts are nonnegative integer literals. Admit `at least n` for `n <= 8`,
`exactly n` / `at most n` for `n <= 7`, and `n of the m` only for
`0 <= n <= 7` and `0 <= m <= 7`. The case `n > m` remains an expressible
contradiction, not a value to repair or a parsing error. Reject excess at
parse/admission with the named bound;
do not attempt a large expansion and present search exhaustion as a result.
Counting sugar is expanded before identity and certification. Quantification
over an integer sort still ranges over all integers, never a model's listed
sample. Ordinary resource limits apply after expansion; a failed search is
UNKNOWN, not a certificate of nonexistence.

The caps are **admission bounds, not evaluation guarantees**. With this
expansion and the current `MAX_EVALUATIONS = 1,000,000`, `exactly 7` and
`7 of the 7` cannot evaluate true in any finite model: a true instance has
at least seven satisfying entities, and refuting the embedded `at least 8`
already exceeds the budget on those entities alone. They may evaluate false,
report UNKNOWN naming the exhausted budget, or be certified on the proof
route. Section 8 gate 4 pins positive six-entity evaluation fixtures and
seven-entity UNKNOWN fixtures. Restoring guaranteed positive evaluation at
seven requires a separately reviewed evaluator/expansion change; no budget
increase is adopted here. User-sort counting belongs to W6a; counting over
`$int` is **gated on numbers2** and never uses a finite sample as its domain.

Ratios are not division terms. A source “1 in 1,000” might describe a finite
population, an illustrative scenario, or a statistical claim. W6 must preserve
that reading and its denominator. As an independent arithmetic illustration,
the exact scalar `0.1%` is `10:bp`; `0.0001%` cannot be represented by `bp`
without loss. In a **separate environment**, whose only percent-display tag
has scale 1,000,000, the latter has coordinate 100. That environment does not
also declare `bp`; section 2.1's display-injectivity rule still holds. There is
no conversion or comparison across the two environments/tags. This does not
license treating the constitution's hypothetical ratios as measured probabilities.

Similarly, a two-thirds voting threshold is not `66.67%`. If independently
supported integer counts `yes` and `eligible` are supplied in the same tag,
`3 * yes >= 2 * eligible`, with explicit count validity bounds and a specified
denominator, is linear integer arithmetic. W6 does not establish those counts,
choose who is eligible/present, or infer the rest of a legal rule. General
cardinality and evaluation-only `count@0` stay deferred; news row 8 is already
the plan's trigger, not permission to exceed the sugar bound.

## 6. Dates, durations and finite horizons

### 6.1 Calendar coordinates

Use the proleptic Gregorian day calculation, epoch **1970-01-01 = 0**, no time
of day and no timezone. This draft chooses **1970-01-01 through 9999-12-31**
inclusive as the supported date-literal/display interval (`0..2932896`). This
makes the plan's rejection of negative day numbers explicit; pre-Gregorian
dates are also outside it. Using a proleptic algorithm does not promise input
support for historical dates. Earlier dates require a reviewed extension,
not a different epoch selected by locale.

`2026-09-16` lowers to `20712:day`. Parse ISO `YYYY-MM-DD` only; a long English
spelling such as “16 September 2026” is an input alias of the same date. Reject
invalid month/day combinations, non-leap February 29, dates outside the
interval, locale-dependent `09/10/2026`, and negative encoded date literals.
Day 0 is Thursday; Sunday is residue 3 modulo 7. Include century exceptions:
2000 is a leap year, 2100 is not.

The `day` unit does not silently restrict an integer variable's domain. A
quantifier over “integer day coordinates” ranges over all integers. English
“for every date d” expands with the visible guard
`validDate(d) := 0 <= d and d <= 2932896`; existential date quantification
conjoins that guard. This is a formula abbreviation, not a new predicate
whose truth a model may supply. Both forms of date quantification are
**gated on numbers2**. Named day coordinates can likewise be out
of display range in an unconstrained integer model: report the coordinate
and `DateRange` diagnostic, never fabricate a calendar date or discard a
counterexample. Date operations below contain explicit guards, so any model
satisfying them assigns dates within range.

### 6.2 Exact temporal operations and endpoints

The statement layer admits the following typed operations on `day` operands.
They are canonical operations in the annotated tree, not raw English strings;
literal aliases are lowered before identity. All expand before core identity.
The direct temporal meaning and regenerated integer formula must agree.
`G(d,t)` abbreviates `validDate(d) and validDate(t)`.

| Canonical operation / controlled wording | Regenerated integer meaning |
|---|---|
| `date_on(t,d)` / “t is on d” | `G(d,t) and t = d` |
| `date_before(t,d)` / “t is before d” | `G(d,t) and t < d` |
| `date_after(t,d)` / “t is after d” | `G(d,t) and d < t` |
| `date_no_later(t,d)` / “t is no later than d” | `G(d,t) and t <= d` |
| `within_days(t,d,n)` / “t is on or after d and on or before n days after d” | `G(d,t) and d <= t and t <= d+n` |
| `shift_days(t,d,n)` / “t is n days after d” | `G(d,t) and t = d+n` |
| `elapsed_days(d,t,v)` / “The elapsed duration from d to t equals v days” | `G(d,t) and v = t-d`; `v:elapsed_day` |
| `sunday(t)` / “t is a Sunday” | `validDate(t) and exists q:dimensionless. t = 7*q+3`; **gated on numbers2** |
| `["excluded_sundays", D, d, n]` / section 6.3's wording | Arity 3; `D,d:day`, literal `n >= 0`; section 6.3's guarded disjunction; **gated on numbers2** |
| `["forall_date", body]` / “For every date d, ...” | Arity 1; binds `d:day` at de Bruijn index 0; `forall d. validDate(d) -> body`; **gated on numbers2** |
| `["exists_date", body]` / “For some date d, ...” | Arity 1; binds `d:day` at index 0; `exists d. validDate(d) and body`; **gated on numbers2** |
| `["trace_all", name, body]` / section 6.4's universal wording | Arity 2; trace reference plus formula; binds position `t` at index 0 with the referenced tick tag; section 6.4's bounded universal; **gated on numbers2** |
| `["trace_some", name, body]` / section 6.4's existential wording | Arity 2; same reference/scope, bounded existential; **gated on numbers2** |

Wire operations are arrays `[operation, operands...]` with the names and
operand order in this table. `date_on`, `date_before`, `date_after` and
`date_no_later` have arity 2 and two `day` terms; `within_days` and `shift_days`
have arity 3 with two `day` terms and `n`, a canonical nonnegative integer
literal string. `elapsed_days` has arity 3 (`day`, `day`, `elapsed_day`);
`sunday` has arity 1 (`day`). The first seven operations are quantifier-free
and belong to W6a. The additional rows specify their own operand types.
`body` is an annotated formula, not a term; `name` is an identifier resolving
only in the containing quantity object's `traces` array. Missing references
reject; there is no implicit current trace or lookup in another claim.
Date and trace binders scope over their body only, shift outer indices by
one, and require every occurrence to match the bound tag. Lean generates
guards and fresh residue binders capture-safely. `elapsed_days` uses a tagged
quantity for `v`; its signed value distinguishes duration from the nonnegative deadline offset.
The fixed literal offset `n` is part of the operation, not a day-valued date.

These checked operations permit date shifting and date subtraction despite
the different date/duration tags. They are not a general cast or implicit
unit conversion. Lean first admits the operation's unit signature, then
generates the integer additions/equalities itself. This generated arithmetic
is not a user-authored exception to the homogeneous arithmetic rule. Supplying
a date-plus-money expression or manually retagging a date as days is rejected.

The explicit “on or after d and on or before n days after d” wording denotes
the plan's **forward** interval `[d,d+n]`; bare “within n days of d” is not an
alias. At `n=0` only `d` is included. “After” excludes its bound;
“no later than” includes it. An offset may cross a leap day or a year boundary.
For an exact shift or excluded-day deadline, if the computed date leaves the
supported display interval, there is no satisfying endpoint assignment;
report inconsistency/UNKNOWN through the
ordinary premise-status gate rather than wrapping or clamping the date.
An inclusive window may still contain valid dates when its upper arithmetic
bound exceeds the display interval; its formula in the table governs that case.

Days here count civil dates. They do not mean 24-hour intervals across a
timezone transition. Months, years as durations, clock times, leap seconds,
timezones and daylight-saving conversion are outside this slice. A
`calendar_year` is an integer year label, not an elapsed duration, an exact
January 1 timestamp or 365 days. “Late May” and “coming months” retain their
imprecision; news row 20's EDT/GMT equality remains its existing relational
model rather than a new W6 timezone theorem.

### 6.3 Sundays excepted

This entire operation is **gated on numbers2**; the baseline must reject it
with `UnsupportedProfile` naming `$int` quantification and the missing
numbers2 route before certification.

`excluded_sundays(D,d,n)` says that `D` is the deadline **n non-Sundays after
d**, excluding the starting date and including the ending date. Its direct
definition is the least `D >= d` for which the number of non-Sundays in
`(d,D]` is `n`. Define `n=0` to give `D=d`; all inputs use literal `n >= 0`.
The English must expose both the exclusion and the counting origin:
“The deadline is 10 days after the presentment date, excluding Sundays and
not counting the presentment date.”

Lean regenerates seven offsets `off(k,n)` and admits:

```text
validDate(d) and validDate(D) and
  or over k=0..6:
    (exists q:dimensionless. d = 7*q+k and D = d+off(k,n))
```

The disjunction is right-associated in residue order 0 through 6, with a
fresh `q` in each branch and both date guards retained. This is the canonical
expansion, replacing the plan's conjunction of residue implications. Require
a Lean equivalence lemma between the guarded disjunction and guarded
implication form, as well as `Time.excludedDays_iff`; equivalent truth alone
does not make their wire identities interchangeable.

This is fixed-coefficient integer arithmetic after expansion, with no trusted
table of deadlines on the wire. The offset function must have a bounded
implementation under the existing resource limits; a huge literal cannot
cause an unbounded day-by-day loop. Its proof connects the offsets to the
direct counting definition, including minimality, zero, and Sunday endpoints.

The Art. I §7 timing acceptance below is the plan's **isolated calendar
reading**, not a formalisation of enactment, adjournment, veto, or legal effect.
“Timely” in that fixture means `d <= return_date <= D`. The separate norm and
legal exceptions cannot be inferred from this calendar calculation.

### 6.4 Finite traces

Finite traces are **gated on numbers2**. Each trace is declared in the
containing `ve-quantity@1` object's `traces` array, with exactly these fields:

```json
{"name":"review_window","tick_tag":"elapsed_day","origin":"presentment","horizon":"10"}
```

`name` is a unique identifier within that quantity object; canonical `T`
sorts declarations by name. `tick_tag` resolves to `dimensionless` or a
declared scale-1 non-date unit. `origin` resolves to a constant in the
identity-bound environment vocabulary naming a reference event in a user
sort; it is not a free string, date coordinate, variable, or trace reference.
`horizon` is a canonical nonnegative integer literal string under the existing
numeral-length limit. Reject unknown fields, duplicate names, unresolved or
ill-typed references, and invalid horizons. All declarations, including unused
ones, enter quantity identity. They cannot be shared by name across claims.

`["trace_all", "review_window", body]` or
`["trace_some", "review_window", body]` explicitly selects that declaration.
Each binds one integer position with its tick tag at de Bruijn index 0 in
`body`; nesting obeys the usual index shifts and does not rebind trace names.
The scope is `[0,H]`, inclusive, so there are `H+1` positions. Write “At every position from 0 through H, ...” and
“At some position from 0 through H, ...”, naming the selected trace by its
approved wording; ambiguous selection rejects. Standalone unbounded “always” and
“eventually” are not offered as interchangeable wordings.

The tick unit is `dimensionless` or a declared scale-1 non-date unit. A trace
origin names a declared reference event; relating it to a calendar date or
another trace requires explicit premises. No timezone or elapsed-year
conversion is smuggled in by that name.

Elaborate to `forall t. (0 <= t and t <= H) -> phi(t)` and
`exists t. 0 <= t and t <= H and phi(t)` with same-tag bounds and capture-safe
substitution. `H=0` contains position 0; negative horizons reject. The bounds
are in the formula, never a finite interpretation of the entire integer sort.
Changing `H`, origin or tick unit changes the approved document/claim identity.
In particular, replacing only `origin` with another declared reference-event
constant leaves the erased formula unchanged but changes quantity identity
and invalidates the old approval, proof/model wrapper and citations.
No infinite-trace, real-time or liveness conclusion follows. Any `phi` requiring
the deferred mixed n-ary/order route remains unsupported. FRET must be
re-rated using user-sort time separately, as the plan requires.

## 7. Acceptance fixtures from pinned sources

These are implementation and fidelity obligations, not passing test results.
Every successful numeric case needs tagged admission, canonical English
round-trip, regenerated core, checked evidence for each claimed consequence,
and a non-vacuity model or explicit UNKNOWN/inconsistency report. A source fact
is an assumption/testimony leaf unless separately evidenced; proving its
arithmetic consequences does not establish its truth.

### 7.1 News article

Use [source.md](../../usecases/news-article/source.md), SHA-256
`b905818ecbc38c479a273d1503430745d1f2c9697215752572922ccedd73545b`
(5,448 bytes), with [coverage row IDs](../../usecases/news-article/coverage.md).
This is the repository's pinned paraphrase/excerpts, not a newly verified
current-news claim. Define each named quantity with its source sentence,
estimate subject, projection period and old/new role; never reuse one unnamed
“rate” constant for several indicators.

| Fixture / source row | Proposed admitted numerical wording and core | Required result / residual |
|---|---|---|
| N01 / row 1, S1 | “The decision date is on 2026-09-16.” `decision_date = 20712:day`, with date guards. | Date payload direct in W6a; the certified weekday check (Wednesday) is **gated on numbers2**. No inference about who voted or future increases. |
| N07 / row 7, S2 | “The new target lower bound equals 3.75%. The new target upper bound equals 4.00%.” Coordinates `375`, `400`, tag `bp`. | Numeric bounds DIRECT; certify `375 < 400`. A range is two bounds, not a single midpoint or an asserted realised rate. |
| N07b / row 7b, S2 | Quarter-percentage-point move: magnitude token `25:bp`. | **NO for the old/new comparison**, as required by the plan: no old endpoint is supplied. Do not insert 3.50% or derive it from an invented equality. The magnitude token alone is representable. |
| N08 / row 8, S3 | “Exactly 16 of the 18 policymakers ...”, and “2 of the 18 ...”. | Direct count rejected: denominator 18 exceeds 7 for exact counting. Plan target remains REIFIED, explicitly with an unchecked count; not DIRECT or certified cardinality. No silent enumeration of 18 witnesses. |
| N13 / row 13, S6 | Projected bounds `400:bp`, `425:bp`; year labels `2026`, `2027` in `calendar_year`. | Exact numeric payload; projection, “by the end”, and “remain ... through” retain their own temporal/kind obligations. Not an observed future rate. |
| N21 / row 21, S11 | “The September PCE estimate equals 3.70%. The June PCE estimate equals 3.60%.” | Numeric comparison DIRECT; certify `370 > 360` and ordered difference `10:bp`. Preserve projected-inflation context and the named June estimate. |
| N22 / row 22, S12 | “The target rate equals 2.00%.” In the selected forecast reading: “The first projected target year equals calendar year 2029.” | Numeric payload DIRECT: `200:bp`, `2029:calendar_year`. Keep projected/first-reaching scope. If “not ... until” is admitted only as a lower bound, use `year >= 2029` in a separate reading; do not strengthen it silently to equality. |
| N22b / row 22b, S12 | “A year later than previously expected.” | **NO for the comparison**: previous expectation is absent, just as in N07b. Do not supply 2028 or treat a year label as 365 elapsed days. |
| N23 / row 23, S13 | Growth: `220:bp` to `230:bp`. Unemployment: `430:bp` to `410:bp`. | Comparisons DIRECT; certify increases/decreases of `10` / `20` ticks, with operands in the correct order. “Slightly” remains open/unformalised. |
| N15/N24 / rows 15, 24, S7/S14 | Goal token `200:bp`; “timelier”, “clearly”, “at sufficient speed”. | Exact goal token, with attribution/pledge retained; no numeric deadline or probability assigned to vague wording. |

The historical coverage file calls row 8 NO, while W6's plan specifies a
REIFIED target; report that transition as reification, not a counting gain.
Its published totals also disagree with its row labels, as NORTH-STAR records.
Recount actual rows and source bytes on the new run instead of inheriting
those totals. W6's required DIRECT numeric rows are 7, 21, 22 and 23; a
partially unresolved source row must expose its residual and cannot count as
wholly checked merely because those numbers are direct.

### 7.2 Full Claude constitution: numerical versus vague

Use the [pinned constitution text](/home/seyran/code/manage-agents/pilots/claude-constitution/source/claude-constitution.md)
and [run-20260927T1800Z ledger](/home/seyran/code/manage-agents/pilots/claude-constitution/run-20260927T1800Z/units.json).
Text SHA-256 is `fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd`
(184,893 bytes). Ranges below are UTF-8 byte offsets `[start,end)` into that
text, not character indices or offsets into the older short excerpt.
These external fixtures are not vendored in this worktree; preserve the hashes
and ledger IDs when moving them into the eventual conformance suite.

| Fixture / source anchor | Numeric handling and one-reading candidate | Required result / residual |
|---|---|---|
| C18 / `u0057.s02`, `[33341,33738)` | Source says users “are over the age of 18”. Token `18` is exact. Under an explicitly **authored completed-years reading**, “The user's age in completed years is greater than 18 completed years of age” gives `18:age_year < age`. | Check boundary 18 false, 19 true under that reading. Do not claim source fidelity: completed-years `>18` differs from elapsed age `>18` (18½) and from eligibility `>=18`. Retain alternatives/age convention, attributed requirement, minors and judgment clause. No inferred birth date, adulthood predicate, or normative duty from the scalar. |
| C1000 / `u0146.s03`, `[88891,89049)` | Hypothetical message sent by “1,000 different users”. The scalar 1000 is representable after lexical transcription to `1000`. | **Unsupported exact cardinality**: 1000 exceeds the counting cap. Keep hypothetical scope and distinctness; do not replace the source with a measured total field. |
| CRATIO / `u0147.s04`, `[90379,90549)` | “1 in 1,000 (or 1 in 1 million)” within a conditional harm example. | Both denominators exceed bounded counting. Preserve the alternatives and conditional/normative scope. No observed frequency or numerical risk cutoff is supplied. The percent calculations in section 5 are illustrative arithmetic only, not a formalisation of this unit. |
| CGRADE / `u0109.s02`, `[64650,64926)` | Standards of honesty “substantially higher” than many human standards. | Keep the compared standards and normative attribution in an open reading if admitted; no numeric honesty scale, ratio, margin or tolerance. Otherwise UNFORMALISED. |
| CMAJORITY / `u0017.s02`, `[7789,8038)` | “The vast majority” of interactions. | No denominator or threshold supplied. Do not translate to `>50%`, `>=90%`, or a small count. |
| CORDER / `u0046.s01`, `[25663,25862)` | “Greater trust”, “greater importance”, “roughly” the listed order. | No conversion of priority order to numerical weights. Preserve defaults/vagueness and soft-norm interpretation; a declared ordinal comparison is only an authored alternative. |

These are acceptance **negative controls** as well as positive scalar cases.
No entire constitution unit above is promised to become CHECKED through W6
alone. Refresh its existing source partition and co-blockers after integration;
do not subtract all 119 quantity-tagged units from the residual.

### 7.3 Art. I §7 calendar regression required by the plan

This fixture uses the timing phrase and convention specified in PLAN-EXPAND2
W6(3), not a new legal-source translation. For `n=10`, independently enumerating
non-Sundays in `(d,D]` gives:

| Presentment weekday / example date | Day-number residue modulo 7 | Offset in elapsed days | Deadline |
|---|---:|---:|---|
| Monday / 2026-09-14 | 4 | 11 | 2026-09-25 |
| Tuesday / 2026-09-15 | 5 | 11 | 2026-09-26 |
| Wednesday / 2026-09-16 | 6 | 12 | 2026-09-28 |
| Thursday / 2026-09-17 | 0 | 12 | 2026-09-29 |
| Friday / 2026-09-18 | 1 | 12 | 2026-09-30 |
| Saturday / 2026-09-19 | 2 | 12 | 2026-10-01 |
| Sunday / 2026-09-20 | 3 | 11 | 2026-10-01 |

Residues use the declared epoch: Thursday=0 and Sunday=3 throughout.
The elaboration, checked models and certified entailment in this fixture are
**gated on numbers2**; independent calendar enumeration alone does not lift it.
Every row needs a checked model agreeing with the brute-force calendar.
Given valid presentment/return/deadline dates, certify that return on elapsed
day 11 is always timely. Refute “return on elapsed day 12 is always timely”
with Sunday 2026-09-20: the deadline is October 1 and day 12 is October 2.
There is exactly one excluded Sunday in days 1–12 of that counterexample.

## 8. Proof obligations and implementation gates

All names below are proposed obligations, not existing theorem claims. The
statement review must assess these meanings before implementation starts.

| Lean obligation | Plain-language statement |
|---|---|
| `Time.units_admit_sound` | Successful executable admission implies every integer occurrence/binder, signature slot and canonical time operation has the declared compatible tag; no unchecked field or operation reaches erasure. |
| `Time.erase_wellTyped` | Erasing an admitted quantity statement yields a well-typed formula in the selected, supported core environment. |
| `Time.units_faithful` | Evaluation of an admitted annotated statement in its direct tagged semantics equals evaluation of its regenerated core formula; the units-only environment maps give a unique corresponding tagged interpretation for each admissible lower structure. This preserves truth, not measurement accuracy. |
| `Time.decimal_exact` | Decimal lowering succeeds iff the input is on the declared integer grid, and canonical rendering recovers exactly that value/tag without rounding. Lean executes this conversion on submitted `S` and checks structural correspondence with any supplied `Q`; original text-to-`S` fidelity is a separate W8 obligation. |
| `Time.dayNumber` inverse / monotonicity | Every accepted date has its unique day coordinate, inverse rendering recovers it, and chronological order agrees with integer order throughout the supported interval. |
| `Time.temporal_iff` | Guarded endpoint, shift and elapsed-duration formulas express exactly section 6's direct calendar meanings, including signed differences and range boundaries. |
| `Time.excludedDays_iff` | The seven-case deadline equals the least day with n non-Sundays in `(d,D]`, including n=0. |
| Guarded Sunday-expansion equivalence | With both date guards retained, section 6.3's disjunction of existential residue cases is equivalent to the previous conjunction of residue implications. |
| `expand_atLeast_iff` and substitution lemmas | The nested fresh-binder expansion holds iff at least n distinct witnesses satisfy the property, in finite and general structures, with outer scopes preserved. |
| `Time.trace_iff` | Bounded universal/existential expansion quantifies exactly over the inclusive trace positions and preserves substitution and units. |
| W6 composed admission/report soundness | An accepted W6 report refers to the bound annotated claims and their admitted readings/support, and its regenerated core evidence justifies those claims. Raw erased evidence alone cannot produce this report. |

Required conformance and authoring gates:

1. **Identity/hostile input:** `$3.75` versus `3.75%` is rejected as
   `UnitMismatch(usd_cent,bp)` by Python and Lean before integer erasure even
   though both coordinates are 375. Test inequality, equality, addition,
   predicate-slot mismatch, constant retagging and binder-occurrence mismatch.
   Rust agrees on acceptance/error class and operand tags. Human diagnostics
   name both quantities. Missing/deleted annotations, unknown tags, altered
   scale/display, unused new declarations, changed horizons, and wrong erased
   payloads either change the appropriate identity or reject; none preserve a
   reusable approval. Include the same erased AST under two different tags in
   the same environment, and mutated citations/proofs/models. Pair submitted
   `3.75%` / `["decimal", "bp", "3.75"]` with a well-typed `376:bp` in supplied
   `Q`: Python, Rust and Lean must reject the mismatch. Mutate only a trace's
   origin to another valid event constant: the erased formula stays the same,
   but quantity identity changes and old approval/citations/proof/model wrappers
   fail. Reject duplicate/unresolved trace references and wrong binder tags.
2. **Exact arithmetic:** round-trip all section 2 examples; reject excess
   precision, cross-currency comparison, raw integer-to-unit coercion, and
   rounding to `66.67%`. Show that a literal zero also needs the right tag.
   Compare Python/Lean lowering and Rust evaluation over deterministic signed
   decimals and values near the existing numeral-length limit. Reject
   environments with colliding percent, currency-code, input-symbol or decimal
   label displays. Test the percentage-point alias in its sole allowed
   difference position and reject it elsewhere; the fine-percent fixture uses
   a separate environment with one percent-display tag.
3. **Calendar:** compare `dayNumber` with Python `datetime` on 10,000
   deterministic accepted dates, including both range endpoints, year ends,
   2000-02-29 and the 2100 exception. Reject invalid/pre-epoch/pre-Gregorian
   literals; test signed elapsed differences, date-versus-duration comparison,
   `n=0`, start exclusion, Sunday endpoints and all seven deadline residues.
   Date binders, weekday/Sunday cases and section 7.3's proof/witness checks
   are **gated on numbers2**; quantifier-free conversion/date cases are W6a.
   Separately check proof/witness requirements in section 7.3; brute-force
   agreement is evidence for the implementation, not the Lean theorem.
4. **Counting/trace:** retain admission caps 8/7/7, separately from evaluation
   guarantees. Pin the section 5 canonical expansion and finite models with
   one user sort `item`, exactly the listed entities `e1` through `eN`, no
   others, no constants, and unary predicates `P` and `S` true of every entity.
   The predicate bodies are single unary atoms; `S and P` is that ordered
   two-atom conjunction. Use the current evaluator with `trace=False` and
   `max_evaluations=MAX_EVALUATIONS=1,000,000`; no trace-node budget participates.
   These counts were reproduced locally while applying the revision and must
   be asserted by the build's regression fixtures:

   | Input | N | Required finite-evaluation result | Evaluations |
   |---|---:|---|---:|
   | `at least 8 P` | 8 | true (`Satisfied`) | 359 |
   | `exactly 6 P` | 6 | true (`Satisfied`) | 120,536 |
   | `6 of the 6 S are P` | 6 | true (`Satisfied`) | 244,997 |
   | `exactly 7 P` | 7 | `ResourceLimit`, value absent; report UNKNOWN naming `MAX_EVALUATIONS` | 1,000,000 |
   | `7 of the 7 S are P` | 7 | `ResourceLimit`, value absent; report UNKNOWN naming `MAX_EVALUATIONS` | 1,000,000 |
   | `at least 8 P` | 7 | `ResourceLimit`, value absent; report UNKNOWN naming `MAX_EVALUATIONS` | 1,000,000 |

   The positive seven-count fixtures must never be reported false or as
   successfully evaluated. Under this expansion and budget, `exactly 7` and
   `7 of the 7` cannot evaluate true in any model; false/UNKNOWN or a separately
   checked proof-route result remain possible. The six-entity positive envelope
   is fixture-specific, not a guarantee for arbitrary predicates or domains.
   `at least 9`, `exactly 8`, `at most 8` and `16 of the 18` reject at admission
   naming the bound; both numerator and denominator bounds are tested.
   Include zero, the admitted but inconsistent `2 of the 1`, repeated witnesses,
   outer-variable references, nested counts and same-spelled binder names.
   Mixed integer-unit binders, traces, `H=0` and out-of-horizon witnesses are
   **gated on numbers2**. Unexpanded counting never certifies. These fixtures
   amend W6(4), subject to decision 9.3 section re-review.
5. **Source fidelity:** N07/N21/N22/N23 gain direct numeric representations;
   N07b/N22b keep their missing-operand residuals; N08 remains uncertified
   cardinality. Preserve the C fixtures' hypotheticals, kinds, readings and
   vague degrees. Re-run the 30-item FRET sample using user-sort time; identify
   integer-time/real-valued exclusions individually. Recompute source-span
   coverage only after an admitted run, not from this specification.
6. **Surface/route:** all-derivations admission, unchanged old English and
   identity fixtures, Python/Lean differential elaboration, Rust parity,
   mixed-profile rejection, and theorem-statement review. W8 must show the
   approved wording, paraphrase, satisfying example and rejected alternative
   with units restored in every witness. Until its fidelity gate passes a
   construct remains strict-only; an internal annotated wire tree is not a
   user-facing English feature. Strict-only is an authoring gate, never
   permission to admit an unsupported route. Baseline integer-quantifier
   constructs must reject with `UnsupportedProfile` naming `$int`
   quantification and the missing numbers2 route until that proved route
   is available.

Use the existing source/package/node/depth/evaluation budgets and diagnostics;
resource limits cannot produce acceptance or a false logical result. Exact
new resource caps, if needed, must be published and tested before enablement.
Preserve the Lean audit allowlist, frozen parser/identity fixtures and every
enabled route's end-to-end theorem requirements.

## 9. Review decisions and build hand-off

The reviewers must explicitly settle these concretisations of the plan:

* Powers-of-ten scales, complete statement annotations, named-constant tags,
  the versioned environment/content fields, and binding **both** annotated and
  erased identities. Environment identity alone does not close the tag hole.
* Date epoch/range, guarded date quantification, signed duration differences,
  date-specific operations, and the distinction between a year label and a
  duration. An integer coordinate outside calendar display is never rounded
  into a date or used to hide a witness.
* Same-grid percentage-point differences versus relative percentage changes;
  explicit ordinal/open treatment of vague degrees; retention of source kinds
  and absent operands. The C18 completed-years example is an authored reading,
  not an endorsed translation of the age policy.
* The canonical annotated operation tree and outer admission binding alongside
  unchanged, fully expanded core identities. Surface aliases and decimal/date
  literal spelling are absent from meaning identity; temporal operation
  parameters remain bound so Lean can regenerate and justify their erasure.

The selected REVISE changes W6(4)'s evaluation acceptance, the canonical Sunday
expansion, and W6 scheduling. Those amendments are recorded in PLAN-EXPAND2's
change log and affected passages. Obtain the section re-review required by
decision 9.3 before building the amended contracts; applying these edits is
not that re-review. Admission caps remain 8/7/7.

The adopted split is W6a (sections 2–3's ground quantities, section 5's
user-sort counting, and the seven quantifier-free date operations) and W6b
(`sunday`, `excluded_sundays`, date/integer binders, finite traces, and section
7.3's certified timing fixture). W6a can start without numbers2 under the
existing P0 admission, section-review, proof, conformance and English-fidelity
gates. W6b waits for numbers2; W4 stage 1 remains required for n-ary relations
over user sorts. Neither profile registration nor strict authoring lifts an
unsupported route.

After review, the W6 owner implements `ve/units.py`, `ve/surface/time.py`,
`ve/surface/count.py`, `lean/VE/Time/*`, and the news fixtures. Coordinate
environment/content decoding, identity and route admission through the P0/W2
owners; Rust must receive the matching W6 boundary. Do not edit `ve/ast.py`
or `ve/evaluate.py` to add a new logical constructor. For the dependent slice,
confirm numbers2's integer-quantifier route and W4 stage 1 are actually merged
and supported:
the baseline's order documentation still describes the earlier ground-only
boundary, so registration alone is not that evidence. Gate calendar/trace
forms requiring integer quantifiers until the proved route exists.

Deliverables at build completion are the implementation, reviewed theorem
statements and audited proofs, local deterministic acceptance results, W8
status, and refreshed source coverage with residuals. Conversions, unbounded
counting, real-number measures, probabilities in formulas, timezones and
W4 stage 2 retain the plan's deferred status and triggers. No model call or
new section re-review has been run as part of applying this revision.

## 10. Change log

* **2026-09-28 — selected converged REVISE.** Applied
  [Astra round 2](/home/seyran/code/manage-agents/debates/design-units/astra.md#round-2-2026-09-27t2354z)
  plus [Fable round 3 additions (a)–(c)](/home/seyran/code/manage-agents/debates/design-units/fable.md#round-3-2026-09-28t0001z)
  from the [design-units debate](/home/seyran/code/manage-agents/debates/design-units/result.txt).
  Retained caps 8/7/7, separated admission from evaluation, pinned positive
  six-entity and UNKNOWN seven-entity fixtures, and recorded the inability of
  positive exact-seven counts to evaluate within the current budget. Specified
  submitted literals and Lean regeneration of `Q`, the mismatch rejection,
  trace declarations/references and date-binder/deadline wire forms. Added
  display injectivity, English without tag identifiers, the percentage-point
  alias, signed subtraction and explicit forward-window wording, a nested
  `units` example, and the isolated fine-percent environment. Adopted the
  guarded disjunctive Sunday expansion with equivalence proof, explicit
  numbers2 rejection and W6a/W6b scheduling. Updated the plan's affected
  contracts and change log; decision 9.3 section re-review remains required.
  This applies the task's selected combination, not Astra round 3's different
  cap-6/Q-only proposal. Local evaluator checks supply exact fixture costs;
  no model calls, new review, implementation or coverage gain is claimed.
