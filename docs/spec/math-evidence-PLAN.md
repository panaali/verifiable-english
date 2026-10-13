# Science papers in VE (`calc@0`, physical dimensions, `arith@0` with proof imports): buildable plan

> **Status.** Plan draft 1 (2026-10-13), branch `design/math-evidence` from `main` at `49de179e`. DRI research wave,
> docs only: no code, proof, test or generated file changed, and no model was called. It is the plan for the design
> recommended in [docs/research/math-evidence.md](../research/math-evidence.md) (cited `research n`), which holds the
> evidence, the measured need, the prior art and the comparison of candidates. The Lean blocks of section 3 are the
> statements the batches prove. They were written against `main` at `49de179e` and were **not elaborated** (this
> session could not run Lean); batch ME-S elaborates them in an untracked stub before any Lean batch starts, as RD-9's
> SC-0 and events' ET-2 do. They are statement schemata: a helper name not found on `main` is defined by the batch
> that proves the statement. Every number is measured (method named) or labelled **estimate**.
>
> **Siblings read.** `design/quantities` (research and plan, read 2026-10-13), `design/attitudes`,
> `design/events-time-causation`, `design/act-phrases`, `design/weighing` (plan), `design/scope` (shared pieces). Where
> this plan needs what they own it names a dependency; section 10 lists the shared pieces. The cross-plan review may
> move any of them.

## 0. Summary

The pinned constitution and UDHR pilots have **no unit** blocked by this topic (research 2.2), so no batch claims a
byte there. The need is in three new use cases (NORTH-STAR rows M, H, DL, weight 3 each, unmeasured) and VE's own
paper (row V, weight 3): their checkable spine is calculations, tables, derivations, physical dimensions, statistics
and, for mathematics, theorems about whole numbers.

| # | Batch | Hours | Owner | Moves a pilot number? |
|---|---|---:|---|---|
| ME-0 | Pin the targets; baseline partition with today's language | 3-4 | pilot runner | **yes**: H, M, V (and DL if a licence is confirmed) go from unmeasured to measured; H 1.5-2.5 KB checked via W6a (**estimate**) |
| ME-S | Statement spec, Lean stub, statement review | 4-5 | planner | no |
| ME-1 | Lean core of `calc@0`: exact values, rounding, claims, verdicts, rendering | 5-6 | Lean | no |
| ME-2 | Wire and service mode `calc`, shapes, identities | 5-6 | Lean | no |
| ME-3 | Python relay `ve/calc.py`, `ve calc check`, fuzz tests | 4-5 | Python | no |
| ME-P1 | Pilot: physics and VE paper, ground calculations as companion cases | 2-3 | pilot runner | H +0.6-1.0 KB, V +0.8-1.5 KB |
| ME-4 | Tables pinned by SHA-256; data handles; counts, sums, means | 5-6 | Lean, Python | no |
| ME-5 | Derivations over rational unknowns: Farkas certificates, the square rule | 5-6 | Lean | no |
| ME-6 | Physical dimensions and unit-change invariance (after the cross-plan review) | 4-5 | Lean | no |
| ME-P2 | Pilot: physics tables, bounds, dimensions; VE paper counts from data | 3 | pilot runner | H +3.0-4.5 KB, V +1-2 KB |
| ME-7 | Exact statistics: mean, variance, SD by squared bounds, sign-flip p, binomial, kappa | 5-6 | Lean | no |
| ME-8 | Consistency of printed numbers: witnesses, enclosures, granularity | 4-5 | Lean | no |
| ME-9 | Algebraic identities: a proved normaliser over ℚ | 5-6 | Lean | no |
| ME-10 | Calculation content in `ve-document@1`; the `calc:` leaf label | 5-6 | Lean, Python | no (turns companions into document units) |
| ME-11 | English: arithmetic phrases, rounding, tables, derivations in Lean's engine | 5-6 | Lean | no (readability) |
| ME-P3 | Pilot: physics complete, VE paper statistics, DL if pinned | 3-4 | pilot runner | H +1.5-2.5 KB, V +10-16 KB, DL +5-8.5 KB |
| ME-12 | Lean core of `arith@0`: statements, meaning, bounded evaluation | 5-6 | Lean | no |
| EX-1 | **Experiment**: Mathlib proofs of VE's own statements (Bertrand's postulate) | 4-6 | planner, Lean | decides ME-13 |
| ME-13 | Import records (only if EX-1 passes) | 4-5 | Lean, Python | no |
| ME-P4 | Pilot: mathematics | 2-3 | pilot runner | M +0.5-1.0 KB |
| EX-2 | **Experiment**: approximations with error bounds; square-root and sum-of-squares certificates | 5-6 | Lean | research |
| EX-3 | **Experiment**: tensor shapes for deep-learning equations | 4-5 | Lean | research |
| EX-4 | **Trigger**: folds over lists and induction inside `arith@0` | — | — | trigger only |
| EX-5 | **Experiment**: a 21 MB data file through the service in chunks | 3-4 | Lean, Python | V's raw recounts |

Order: ME-0 now (no code, no dependency). ME-S after the plan converges. ME-1 to ME-3, then ME-P1. ME-4 and ME-5 in
parallel; ME-6 after the cross-plan review settles the unit registry; ME-P2. ME-7, ME-8 and ME-9 in parallel; ME-10
after `lean-first/b16g` (or its successor) gives the `document` mode a content hook; ME-11 after english-lean's E3
quantities step (quantities' QT-E). ME-12 and EX-1 can start after ME-S, independent of the calculation batches.
**Pilot order: physics, then deep learning, then mathematics** (research 7).

**The first batch that moves a pilot number** is ME-0: it pins the texts, partitions every byte, and records what
today's VE checks (W6a quantities and linear comparisons, attributions, labels; the 1887 dates are outside W6's
calendar). It needs no product code.

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | A new profile **`calc@0`** with its own mode `calc` and namespace `VE.Calc` | `order@0` is frozen (`lean/VE/Route/frozen-sources.sha256` lines 191-206), integer-valued, and uses integer cuts that are unsound for real-valued quantities; W6a's `ve-units@1` and its linear integer typing are frozen by the meaning-freeze rule | widening `order@0` or W6a in place |
| D2 | Values are **exact rationals**: core `Rat` (`import Std`, as `lean/Iceberg.lean` uses it with `grind`); no floating point anywhere | exactness is the point; the pinned toolchain has `Rat` and ring automation without Mathlib | binary floats; a VE-defined fraction type (duplicate of `Rat`) |
| D3 | Decimal literals are read by W6a's `VE.Time.parseDecimal` into `VE.Time.Dec`; one new lemma gives its exact value (`decValue`) | one decimal grammar (W6) | a second decimal parser |
| D4 | A **named value** has one source: *stated* (the text gives it), *defined* (an expression over earlier names), *counted* (an aggregate of a pinned table), or *free* (an unknown, for derivations only) | a reader sees where every number comes from; definitions are non-recursive by construction | implicit values; recursive definitions |
| D5 | A printed number keeps its **written places** ("0.30" is two places, "0.3" one); the scientific form "2 times ten to the power 7" has the places of its last written digit (here minus 7) | the precision a reader sees is part of the claim | a default precision; significant-figure guessing |
| D6 | **One rounding definition, explicit tie rule.** The default rule is ties upward, the meaning quantities' QT-A2 gives `roundHalfUp`; a case may declare *half to even* ("as Python prints"); in translation an exact tie under an undeclared rule is a reading set (fixture V-8). The definition lives in one module shared with quantities (section 10, piece 2) | one reading per rounded number; Python's formatting rounds exact binary ties to even, so VE's own tables need it | a tie-tolerant "either neighbour" meaning (two readings in one); a second rounding definition |
| D7 | Verdicts: **holds**, **fails**, **undefined** (a missing value, a zero divisor), **unknown** (a budget). In translation, a claim that fails is a **finding about the source**, reported with exact values; in authoring it is an error to fix | statcheck and GRIM report inconsistencies, they never repair them (research 3.5); "undefined" is not "false" | turning a failed source calculation into a rejected translation |
| D8 | Ratios of **counts of vocabulary objects** ("16 of the 18 policymakers") belong to quantities' `cardinality@0` and its wording "X out of Y"; `calc@0` ratios are of stated or table-derived **numbers**, worded "X divided by Y" | one owner per wording; both share D6's rounding | two wordings for one meaning |
| D9 | **Tables pinned by SHA-256**: Lean computes the digest (`VE.CertificateWire.sha256`) of bytes the relay transports; the service keeps data handles like its environment handles; CSV and JSON-lines subsets; filters and count, sum, mean, minimum, maximum | a number bound to bytes anyone can hash; Python transports, never computes | Python-side aggregation; trusting a supplied digest |
| D10 | JSON numbers in data are read by their **written digits** as exact decimals; derived float files (`paper/generated/posthoc-e1.json`'s `-0.14999999999999997`) are not used for exact recomputation; exact work starts from integer counts | binary floats carry noise that flips exact ties | re-deriving exact values from floats |
| D11 | **Derivations over rational unknowns** by Farkas certificates that a Fourier-Motzkin search in Lean produces and a proved checker replays; no integer cuts; plus one proved nonlinear rule ("from 0 ≤ x, x² < a, a ≤ b², 0 < b infer x < b") | linear reasoning over ℚ is complete with Farkas certificates; `order@0`'s frozen integer module cannot be reused for rational unknowns, so a rational module is a different owner's logic, not a copy | Python certificate search (the directive keeps Python to CLI, files, display); cuts |
| D12 | **Physical dimensions**: a unit declares integer exponents over declared base dimensions and an exact positive factor to the coherent unit; sums and comparisons need equal dimensions; the theorem is **unit-change invariance**. Affine units (degrees Celsius) and logarithmic units (decibels) are refused by name. Declared in the one `ve-units@2` shared with quantities' QT-A7, where a conversion between two units of one dimension becomes a corollary of their factors | Buckingham and Bridgman (research 3.4); one unit registry | a second unit schema; conversions without dimensions |
| D13 | Called **physical dimension** in prose and `base_exponents` on the wire | quantities' `scales@0` already uses "dimension" for a comparison scale | reusing the word for two things |
| D14 | **Statistics**: only procedures with an exact rational meaning (counts, rates, means, sample variance, exact sign-flip and binomial tail probabilities, Cohen's kappa) or a rational characterisation (a square root by squared bounds). Quantiles of continuous distributions (Student's t) are *stated* constants with their source. Each procedure carries its **assumptions as named residual leaves** | exact recomputation; no floating special functions in the trusted core; the paper itself names its assumptions (`paper/analysis/README.md`) | a statistics library in Lean; hiding assumptions |
| D15 | **Consistency of printed numbers**: given that inputs were printed rounded, a *witness* (exact inputs inside their rounding intervals reproducing every printed output) proves consistency; an *enclosure* (exact interval arithmetic over the boxes) proves inconsistency; otherwise unknown | GRIM and statcheck in Lean, with certificates both ways | float re-computation |
| D16 | **Algebraic identities** by a proved normaliser for polynomials and rational functions over ℚ; the side conditions are exactly the nonzero divisors `Denotes` already requires | derivation steps in physics are mostly identities ("D/(V − v) + D/(V + v) = 2DV/(V² − v²)") | trusting a computer-algebra system |
| D17 | **English**: words only; fixed phrases ("the product of A and B", "A divided by B", "the square of A", "rounded to three decimal places"); a **name for every intermediate value** instead of nested formulas; a formula view is an optional display, never input. "About", "approximately", "roughly", "nearly" are refused in authoring with rewrites and become reading sets in translation. Lean renders claim lines from ME-1 (display only); input wordings join Lean's English engine after english-lean E3 (ME-11) | zero-training English; one reading per sentence | symbols in VE text; a Python English parser |
| D18 | **Documents**: `calculation` content in `ve-document@1` goes through Lean's `document` mode; a claim-graph leaf labelled `calc:<case>/<claim>` is discharged by the calc route; `support: calculation` counts as checked only when Lean recomputed it | the support field exists (`document.md`) and is only a label today | a Python document branch |
| D19 | **Mathematics** is a separate profile **`arith@0`**: whole numbers and integers, addition, subtraction, multiplication, divisibility, order, functions and predicates defined by non-recursive terms and formulas, bounded and unbounded quantifiers; meaning `VE.Arith.Holds` in core Lean; **bounded evaluation** decides statements whose quantifiers are all bounded | finite checks ("by actual verification ... for smaller values") are decidable; the rest needs proofs VE does not search for | function symbols, recursion or induction inside the tableau (research D4, rejected) |
| D20 | **Proof imports**: a Lake project outside `lean/` (`imports/mathlib/`) requires Mathlib and VE and proves `VE.Arith.Holds ... s` for VE's own statement `s`; VE records toolchain, Mathlib revision, declaration and axioms; the import enters reports only as a leaf labelled `import:<project>@<revision>/<declaration>`, counted in the residual (VISION rule 6). Never linked into `ve_service`. Built only if EX-1 passes | the statement a reader approves is the statement Lean proves; VE's trusted runtime does not grow | Mathlib inside `lean/`; hand-written Lean statements reviewed against English (the iceberg's gap) |
| D21 | **Rust: none.** Python: the `ve calc` and `ve arith` commands, file reading, relays, display; no arithmetic, no search | `CLAUDE.md` ownership; exact arithmetic is cheap in Lean | a Rust accelerator before a measured need |
| D22 | **Targets** (research 2.4): physics = Michelson and Morley 1887 (public domain); mathematics = Ramanujan 1919 (public domain); deep learning = the first of the ranked candidates whose CC-BY licence ME-0 confirms by reading the licence field of its abstract page with a plain HTTP fetch and no model; VE's own paper is the in-repository fixture source | measured claims only; no copied text without a licence | storing a text whose licence is unconfirmed |

## 2. Design

### 2.1 A calculation case

A case is a JSON object of format `ve-calc@0`. Example (fixture V-2, VE paper `04-e1.md`):

```json
{"format": "ve-calc@0",
 "rounding": "ties-up",
 "values": [
   {"name": "approved_strict", "words": "the number of weakening attacks approved in strict VE", "stated": "52"},
   {"name": "approved_symbols", "words": "the number of weakening attacks approved in symbols", "stated": "31"},
   {"name": "attacks", "words": "the number of weakening attacks", "stated": "243"},
   {"name": "rate_strict", "words": "the false-approval rate in strict VE",
    "defined": ["div", ["val", "approved_strict"], ["val", "attacks"]]},
   {"name": "rate_symbols", "words": "the false-approval rate in symbols",
    "defined": ["div", ["val", "approved_symbols"], ["val", "attacks"]]},
   {"name": "increase", "words": "the increase in percentage points",
    "defined": ["mul", ["lit", "100"], ["sub", ["val", "rate_strict"], ["val", "rate_symbols"]]]}],
 "claims": [
   {"id": "c1", "claim": ["rounds", ["val", "rate_strict"], "0.214"]},
   {"id": "c2", "claim": ["rounds", ["val", "rate_symbols"], "0.128"]},
   {"id": "c3", "claim": ["rounds", ["val", "increase"], "8.6"]}]}
```

- `values` are in order; a `defined` value uses only earlier names; names are unique identifiers; `words` follow W6's
  verbalisation rules (whitespace-normalised, distinct up to sentence-initial capitalisation, diagnostic
  `VerbalisationCollision`), checked by the Lean check W6a already runs, reused rather than copied.
- Expressions: `["lit", decimal]`, `["sci", decimal, exponent]` ("2 times ten to the power 7"), `["val", name]`,
  `["add", a, b]`, `["sub", a, b]`, `["mul", a, b]`, `["div", a, b]`, `["pow", a, natural]`.
- Claims: `["eq" | "lt" | "le", a, b]`, `["within", e, low, high]` (inclusive), `["rounds", e, printed]` (places from
  the printed spelling; the case's `rounding` gives the tie rule: `ties-up`, the default, or `half-even`;
  `["rounds-down", e, printed]` and `["rounds-up", e, printed]` for printed bounds).
- Each `stated` value may carry `"support"` (`observation`, `testimony`, `assumption`) and `"span"` (bytes in the
  pinned source); the report lists them as the residual a claim rests on.
- Limits, checked first and in this order: 10,000 JSON nodes, expression depth 64, 512 values, 512 claims, exponents
  at most 64, literals at most 40 digits (W6's numeral limit); a `pow` or `div` chain whose exact result would exceed
  4,096 digits in numerator or denominator gives **unknown** with the limit named.

### 2.2 Identity

The case's `meaning_id` is the environment-bound identity (the `ve-meaning-…` domain W6a uses, `Admission.meaningId`)
over the canonical case with `words` excluded: value literals in canonical form ("0.30" and "0.3" as values are one
value), printed numbers with their written places ("0.30" and "0.3" as rounding targets are two claims). A renamed
verbalisation does not change the meaning; the approved wording is bound separately, as for W6a constants. Each claim has its own id: the case id plus the claim's
canonical JSON. Changing a value, a source, a tie rule or a printed spelling changes the id and voids every approval
or citation of it.

### 2.3 Values and printed numbers

A printed number is a pair `(D, k)` read from its spelling: "0.296" is (296, 3), "8.6" is (86, 1), "0.40" is (40, 2),
"2 times ten to the power 7" is (2, −7). Its value is D / 10^k. Rounding a value x to the printed (D, k):

- ties upward: (2D − 1)/2 ≤ x·10^k < (2D + 1)/2;
- half to even: the same, except that x·10^k = (2D − 1)/2 or (2D + 1)/2 counts only when D is even;
- rounded down (a printed lower bound): D ≤ x·10^k < D + 1; rounded up: D − 1 < x·10^k ≤ D.

### 2.4 Claims, verdicts and findings

A claim **holds** or **fails** when every value it mentions denotes; it is **undefined** when a value is free or
missing or a divisor is zero, and **unknown** when a limit is reached. Lean reports, for each claim, the verdict, the
exact value of every side as a reduced fraction, its decimal display at the printed places, the names it depends on
with their sources and supports, and one English line (2.11). In a translated document a failed claim is reported as
"The source's numbers disagree: 52 divided by 243 is 0.21399…, which rounds to 0.214, not 0.213", and the unit stays
CHECKED with a **finding**; nothing is repaired.

### 2.5 Tables and data handles

- A case may declare `"data": [{"handle": sha256, "format": "csv" | "jsonl", "columns": {name: "text" | "number" |
  "bool"}}]`. A request registers the bytes under their SHA-256 (as environment handles are registered,
  `VE.Service.Handles`); Lean recomputes the digest and refuses a mismatch. The relay reads the file and sends its bytes;
  it never parses them.
- CSV subset: comma separator, double-quote quoting, a header row, LF or CRLF line ends; JSON lines: one object per
  line, columns read by top-level key. Numbers are read by their written digits (D10); "true"/"false" for booleans;
  a missing key or empty field is *absent*.
- A `counted` value is `{"data": sha256, "filter": F, "aggregate": A}` with filters `["is", column, text]`,
  `["equals", column, number]`, `["true", column]`, `["not", F]`, `["and", F, F]`, `["or", F, F]`, `["all"]` and
  aggregates `"count"`, `["sum", column]`, `["mean", column]`, `["min", column]`, `["max", column]`. An aggregate over an
  empty selection, or over a selection with an absent or non-number cell in its column, is **undefined**, never zero.
- Limits: 16 MB per handle in this batch (the service's line cap; EX-5 adds chunks), 1,000,000 rows, 64 columns, and
  the same evaluation budget as W6a (1,000,000 evaluations, `VE.Time.Budget`); exhaustion is **unknown**.

### 2.6 Derivations over unknowns

A case may declare `free` values (unknowns) and **premise** claims about them, and ask whether a claim **follows**:
`{"id", "follows": claim, "from": [claim ids], "square_links": [[square, root], …]}`. Lean substitutes known values,
linearises (a premise that is not linear in the unknowns is refused, naming the term), searches Farkas multipliers by
Fourier-Motzkin elimination within a budget, and checks them; a square link `s = r²` with `0 ≤ r` allows one proved
step of the square rule (D11). Outcomes: **follows** (with the replayed certificate), **does not follow** (with exact
values of the unknowns satisfying every premise and refuting the claim, checked by evaluation; for purely linear
premises Fourier-Motzkin yields such values whenever no certificate exists, and across a square link the search tries
the claimed bound itself), or **unknown** (budget, or a nonlinear step the rule does not cover). Physical laws ("the displacement is proportional to the square of the
velocity") enter as named premises with `support: assumption`, never as truths.

### 2.7 Physical dimensions

The environment carries `ve-units@2` (shared with quantities, section 10 piece 3): base dimensions (identifiers,
for example `length`, `time`, `mass`, and document-declared ones such as `fringe`), and units with `base_exponents`
(for example `{"length": 1, "time": -1}`) and an exact positive `factor` to the coherent unit of that physical dimension.
A unit is also a value: "11 meters" is `["mul", ["lit", "11"], ["val", "meter"]]`. Each value declares its physical
dimension; literals are dimensionless. Lean infers the physical dimension of every expression and refuses a sum,
difference or comparison of different physical dimensions (`DimensionMismatch`, naming both) and a rounding claim on a
non-dimensionless expression (the printed number must say its unit: "the displacement divided by one fringe width
rounds to 0.4"). Conversions are no extra declaration: two units of one physical dimension convert by the ratio of
their factors.

### 2.8 Statistics

New expression forms over a table column or a list of values: `["mean", xs]`, `["variance", xs]` (sample, divisor
n − 1), `["population-variance", xs]` (divisor n), `["sign-flip-p", xs]` (two-sided, exact over all 2^n sign vectors,
n ≤ 16), `["binomial-tail", n, k, p]` (P(X ≥ k)), `["kappa", table]` (Cohen's kappa of a square agreement table). A
square root appears only in claims: `["sqrt-rounds", e, printed]` means "the square root of e, rounded, is printed",
defined by squared bounds (exact). Each form carries its assumption leaves, rendered in the residual: sign-flip,
"the differences are independent and their signs exchangeable under the null"; binomial, "the trials are independent
with one success probability"; t-based half-width, "the stated quantile is the 97.5% point of Student's t with 11
degrees of freedom" (a stated constant with `support: testimony` and its source).

### 2.9 Consistency of printed numbers

`["consistent", inputs, outputs]`: the inputs are printed values (each with its rounding interval), the outputs are
claims. Two certificates, both checked exactly: a **witness** (exact inputs inside their intervals under which every
output claim holds) proves *consistent*; an **enclosure** (interval evaluation over the input boxes for `add`, `sub`,
`mul`, `div` with a divisor interval not containing zero, `pow`, and squared bounds for square roots) that misses an
output's printed interval proves *inconsistent*. A granularity rule covers enumeration counts: an exact sign-flip p over
n values is a multiple of 1/2^n, so a printed p with no such multiple in its rounding interval is inconsistent.
Otherwise *unknown*. Lean searches witnesses by trying the printed values themselves and the interval endpoints; a
witness from elsewhere is replayed the same way.

### 2.10 Algebraic identities

`["identity", a, b]` over free values: Lean normalises both sides to polynomials over ℚ (sorted monomials, merged
coefficients, zeros dropped) or, with division, to numerator and denominator, compares cross-multiplied normal forms,
and reports **identity** or **not shown** (with a rational point where the sides differ when one is found by trying
small values; otherwise unknown). Soundness needs only that equal normal forms mean equal values wherever both sides
denote; the nonzero-divisor side conditions are those of `Denotes`.

### 2.11 English

Reader-facing wordings (one reading each; rendered by Lean from ME-1, readable as input after ME-11):

| Wording | Meaning |
|---|---|
| "The path length is 11 meters." | stated value with unit |
| "The expected displacement is twice the path length divided by the wavelength, times the square of the speed ratio." | **refused**: two parses; rewrite: "Let the path in wavelengths be the path length divided by the wavelength. The expected displacement is twice the product of the path in wavelengths and the square of the speed ratio." |
| "Let the speed ratio be the orbital speed divided by the speed of light." | defined value |
| "A equals B", "A is less than B", "A is at most B", "A is from L through H" | comparisons (W6's wordings, reused) |
| "The false-approval rate is 0.296 when rounded to three decimal places." | `rounds`, ties upward unless the document says "Numbers in this document are rounded half to even." |
| "The lower bound is 0.019 rounded down to three decimal places." | `rounds-down` |
| "In the trial table, the number of rows whose judge is the 32B judge, whose view is symbols, whose explanation is none, whose label is bad and that are approved is 176." | counted value; the table's digest is shown on request |
| "The standard deviation of the twelve differences, with divisor eleven, is 0.108 when rounded to three decimal places." | `sqrt-rounds` of the sample variance; "standard deviation" alone is a reading set {divisor n − 1, divisor n} in translation and refused in authoring |
| "From these, it follows that the velocity ratio is less than one fourth." | a derivation; the premises are listed above it as numbered sentences |
| "The round-trip time is the sum of the path length divided by the difference between the speed of light and the speed and the path length divided by the sum of the speed of light and the speed." | **refused**: "and" at two levels gives several parses; rewrite: "Let the outward time be the path length divided by the difference between the speed of light and the speed. Let the return time be the path length divided by the sum of the speed of light and the speed. The round-trip time is the sum of the outward time and the return time." |

Arithmetic phrases: "the sum of A and B", "the difference between A and B" (A minus B), "the product of A and B", "A
divided by B", "twice A", "half of A", "the square of A", "the cube of A", "A to the power N", "D times ten to the power
N". Operands are names, numbers or one of these phrases with name or number operands; deeper nesting is refused with
the rewrite "Let ... be ..." naming the inner value. Refused words with rewrites: "about", "approximately", "roughly",
"nearly", "on the order of" (rewrite: the rounding sentence or an inclusive range); "on par", "comparable" (an open term
with a decider); every symbol (`+`, `×`, `/`, `^`, `=`, `≈`) in VE text. The formula view (`2D v²/V²`) is a display
generated from the meaning and never parsed.

### 2.12 Documents, statuses and the residual

A unit with `calculation` content is CHECKED when Lean decided every claim (holds or fails; a failure is a finding in
the ledger's `findings` list), OPEN when a claim is unknown (the limit named), and UNFORMALISED with reason
`missing-input` when a value is undefined. Its residual lines are its stated values' supports, its data digests, its
procedures' assumptions, its free values' premises and, for imports, the import label. A claim-graph leaf
`calc:<case>/<claim>` may stand in a document's claim graph; Lean's `document` mode discharges it by running the case
and requiring **holds**; a W6a or relational claim may not cite it until a bridge between the profiles is designed
(out of scope).

### 2.13 Mathematics: `arith@0` and proof imports

Statements about whole numbers (0, 1, 2, …) and integers: terms are numerals, variables, sum, difference, product,
calls of defined functions and bounded counts ("the number of primes from 1 through x"); formulas are equality, order,
divisibility, calls of defined predicates, connectives, quantifiers over whole numbers and integers, and bounded
quantifiers ("for every whole number n from 1 to 161"). A count's condition must itself be bounded. Definitions are
non-recursive: a function by a term, a predicate by a formula, each over earlier names only ("a whole number p is
prime exactly when p is at least 2 and no whole number from 2 to p minus 1 divides p"). Meaning:
`VE.Arith.Holds`, in core Lean. Lean decides a statement whose every quantifier is bounded, by evaluation within a
budget (true, false with the deciding values, or unknown). An unbounded statement is stated, rendered and identified;
it is proved only by an import (ME-13, if EX-1 passes): an import record names the statement's `meaning_id`, the import
project, the Lean toolchain, the Mathlib revision, the declaration and its axioms. `tools/lean_import_check.py` (a
tool, not the service) builds the import project and prints axioms; Lean's `arith` mode admits the record (identity,
axiom allowlist, names) and the report carries the leaf `import:imports/mathlib@<revision>/<declaration>`. The
residual line reads "Proved in Lean with Mathlib at revision …, declaration …; VE did not replay this proof."

### 2.14 One owner; deleted or not duplicated

| Piece | Owner | This plan |
|---|---|---|
| Decimal literals and their exact value | `VE.Time.Decimal` (`parseDecimal`, `Dec`, `lower`, `decimal_exact`) | reused; `decValue` and the lemma `decValue_lower` (the exact value agrees with W6's coordinate) added in a new file, nothing copied |
| Rounding with a tie rule | one shared module (section 10, piece 2): quantities' `roundHalfUp` for integer ratios is its special case | ME-1 builds it if it lands first, else imports quantities' and proves `roundsTo_ratio_agree` |
| Verbalisation rules for named values | W6a (`VerbalisationCollision`, `VE.Time.Wire`) | reused |
| SHA-256 and canonical JSON | `VE.CertificateWire.sha256`, `VE.CertificateWire.canonical` | reused |
| Handle tables | `VE.Service.Handles` (environment handles) | extended with a data kind in the same table, not a second table |
| Linear arithmetic over integers with cuts | `order@0` (frozen) | not touched; rational linear forms are new (D11) and say why in their file header |
| Counts of vocabulary objects, "X out of Y" | quantities' `cardinality@0` | not duplicated (D8) |
| Unit tags, unit declarations, conversions | W6a `ve-units@1`; quantities' `ve-units@2` `converts` | one `ve-units@2` with physical dimensions added (D12); `convert_iff` becomes a corollary |
| Open terms, reading sets, kinds, `support` | W2 (`document.md`) | reused; `support: calculation` gains a check (D18) |
| Attribution of cited results | `reports@0` | reused for citations |
| Likelihood words ("probably") | attitudes | not built; hedged calc units stay `hedged` labels until attitudes lands |
| Dates of observation sessions | W6a dates; events-time-causation for events | reused; no new date code |
| English engine and lexicon | english-lean (E3); quantities' QT-E moves W6's wordings | ME-11 adds rules there; no Python English |
| Profile registration | `VE.Compose.Dispatch` | one row and gate lemmas per profile (`calc@0`, `arith@0`) |
| Proof checking of imports | the Lean kernel in the import project's build | VE checks the record, not the proof (D20) |

**Deleted:** nothing on `main` duplicates this topic's logic. The plan adds no Python arithmetic, so nothing in Python
needs deleting. Paper reanalysis scripts (`paper/analysis/*.py`) are experiment tooling, not product logic; VE's
recomputation is an independent check of the paper's text against its data, so it is not a second owner of the
paper's analysis.

### 2.15 What stays open (never certified)

The truth of stated values and of data files (a digest binds a claim to bytes, not bytes to the world); the
applicability of a physical law or a statistical model; the choice of a test; a stated quantile's correctness; whether
an imported Mathlib proof is correct beyond the pinned build's acceptance; every interpretive sentence ("it seems fair
to conclude"); likelihood hedges (attitudes); exposition, which stays LABELLED.

## 3. Lean statements

Schemata, not elaborated (status note). Names follow `main`'s conventions; `Rat` is core's (via `import Std`).

### 3.1 ME-1: values, rounding, claims, verdicts

```lean
import Std
import VE.Time.Decimal

namespace VE.Calc

/-- The exact value of a written decimal: its significand over ten to its number of places. -/
def decValue (d : VE.Time.Dec) : Rat := (d.significand : Rat) / ((10 : Rat) ^ d.places)

/-- One meaning for decimals: where W6 lowers a literal onto the grid of scale `10^k`, the coordinate over `10^k` is
the literal's exact value. -/
theorem decValue_lower (d : VE.Time.Dec) (k : Nat) (q : Int) (h : VE.Time.lower d k = some q) :
    decValue d = (q : Rat) / ((10 : Rat) ^ k)

/-- Ten to an integer power, exactly. -/
def tenPow : Int → Rat
  | .ofNat n => (10 : Rat) ^ n
  | .negSucc n => 1 / (10 : Rat) ^ (n + 1)

/-- A printed number `D / 10^k`, with the places `k` read from its spelling ("0.30" is (30, 2); "2 times ten to the
power 7" is (2, -7)). -/
structure Printed where
  digits : Int
  places : Int
  deriving Repr, DecidableEq

def Printed.value (p : Printed) : Rat := (p.digits : Rat) / tenPow p.places

inductive Rounding where
  | tiesUp | halfEven | down | up
  deriving Repr, DecidableEq

/-- `x` rounds to `p` under rule `r`. Ties upward is the default (quantities' `roundHalfUp`). -/
def RoundsTo (r : Rounding) (p : Printed) (x : Rat) : Prop :=
  let y := x * tenPow p.places
  let D : Rat := p.digits
  match r with
  | .tiesUp => 2 * D - 1 ≤ 2 * y ∧ 2 * y < 2 * D + 1
  | .halfEven => (2 * D - 1 < 2 * y ∧ 2 * y < 2 * D + 1) ∨
      ((2 * y = 2 * D - 1 ∨ 2 * y = 2 * D + 1) ∧ p.digits % 2 = 0)
  | .down => D ≤ y ∧ y < D + 1
  | .up => D - 1 < y ∧ y ≤ D

instance (r : Rounding) (p : Printed) (x : Rat) : Decidable (RoundsTo r p x)

/-- Rounding to `k` places moves a value by at most half a unit of the last place. -/
theorem roundsTo_close (p : Printed) (x : Rat) (h : RoundsTo .tiesUp p x) :
    -(1 / 2) ≤ x * tenPow p.places - p.digits ∧ x * tenPow p.places - p.digits < 1 / 2

/-- One printed number per value and rule: two different printed numbers with the same places cannot both be the
nearest rounding of one value (ties upward). -/
theorem roundsTo_unique (x : Rat) (p q : Printed) (hk : p.places = q.places)
    (hp : RoundsTo .tiesUp p x) (hq : RoundsTo .tiesUp q x) : p = q

inductive Expr where
  | lit (q : Rat)
  | val (name : String)
  | add (a b : Expr)
  | sub (a b : Expr)
  | mul (a b : Expr)
  | div (a b : Expr)
  | pow (a : Expr) (k : Nat)
  deriving Repr, DecidableEq

abbrev Values := String → Option Rat

/-- The independent meaning of an expression: the value it denotes, when every name has a value and no divisor is 0. -/
inductive Denotes (σ : Values) : Expr → Rat → Prop
  | lit {q} : Denotes σ (.lit q) q
  | val {n q} : σ n = some q → Denotes σ (.val n) q
  | add {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.add a b) (x + y)
  | sub {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.sub a b) (x - y)
  | mul {a b x y} : Denotes σ a x → Denotes σ b y → Denotes σ (.mul a b) (x * y)
  | div {a b x y} : Denotes σ a x → Denotes σ b y → y ≠ 0 → Denotes σ (.div a b) (x / y)
  | pow {a x k} : Denotes σ a x → Denotes σ (.pow a k) (x ^ k)

def Expr.eval (σ : Values) : Expr → Option Rat

theorem Expr.eval_iff (σ : Values) (e : Expr) (q : Rat) : e.eval σ = some q ↔ Denotes σ e q
theorem Denotes.unique {σ : Values} {e : Expr} {x y : Rat} (hx : Denotes σ e x) (hy : Denotes σ e y) : x = y

inductive Rel where
  | eq | lt | le
  deriving Repr, DecidableEq

def Rel.Holds : Rel → Rat → Rat → Prop
  | .eq, x, y => x = y
  | .lt, x, y => x < y
  | .le, x, y => x ≤ y

inductive Claim where
  | compare (r : Rel) (a b : Expr)
  | within (e lo hi : Expr)
  | rounds (r : Rounding) (e : Expr) (p : Printed)
  deriving Repr, DecidableEq

def Claim.Holds (σ : Values) : Claim → Prop
  | .compare r a b => ∃ x y, Denotes σ a x ∧ Denotes σ b y ∧ r.Holds x y
  | .within e lo hi => ∃ x l h, Denotes σ e x ∧ Denotes σ lo l ∧ Denotes σ hi h ∧ l ≤ x ∧ x ≤ h
  | .rounds r e p => ∃ x, Denotes σ e x ∧ RoundsTo r p x

/-- Every expression of the claim denotes. -/
def Claim.Defined (σ : Values) : Claim → Prop

inductive Verdict where
  | holds | fails | undefined
  deriving Repr, DecidableEq

def Claim.decide (σ : Values) (c : Claim) : Verdict

theorem Claim.decide_holds (σ : Values) (c : Claim) : c.decide σ = .holds ↔ c.Holds σ
theorem Claim.decide_fails (σ : Values) (c : Claim) : c.decide σ = .fails ↔ c.Defined σ ∧ ¬ c.Holds σ
theorem Claim.decide_undefined (σ : Values) (c : Claim) : c.decide σ = .undefined ↔ ¬ c.Defined σ

/-- Where a named value comes from (counted values arrive in ME-4). -/
inductive Source where
  | stated (q : Rat)
  | defined (e : Expr)
  | free

structure Decl where
  name : String
  source : Source

/-- Unique names; each defined value mentions only earlier names. -/
def WellFormed (ds : List Decl) : Prop

/-- The values the declarations give, in order: stated values as written, defined values by evaluation, free values
none. -/
def values (ds : List Decl) : Values

theorem values_stated (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (q : Rat)
    (hs : d.source = .stated q) : values ds d.name = some q
theorem values_defined (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds) (e : Expr)
    (hs : d.source = .defined e) (q : Rat) : values ds d.name = some q ↔ Denotes (values ds) e q
theorem values_free (ds : List Decl) (h : WellFormed ds) (d : Decl) (hd : d ∈ ds)
    (hs : d.source = .free) : values ds d.name = none

end VE.Calc
```

If quantities' QT-A2 has landed first, ME-1 also proves the agreement (otherwise QT-A2 proves it against this
definition):

```lean
theorem VE.Calc.roundsTo_ratio_agree (a b D : Int) (k : Nat) (hb : 0 < b) :
    VE.Calc.RoundsTo .tiesUp ⟨D, (k : Int)⟩ ((a : Rat) / b) ↔ VE.Cardinality.roundHalfUp a b k = D
```

### 3.2 ME-2: wire, runner, shapes

```lean
namespace VE.Calc

/-- A decoded case: declarations, claims, and the case's tie rule. -/
structure Case where
  decls : List Decl
  claims : List (String × Claim)
  ties : Rounding

/-- Decodes `ve-calc@0`: limits first (2.1), then fields, names, order of definitions, literals by
`VE.Time.parseDecimal`. -/
def Wire.decodeCase : Lean.Json → Except String Case

theorem Wire.decodeCase_wellFormed (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) : WellFormed c.decls

/-- The runner's row for claim `i` reports exactly `Claim.decide` of the decoded claim under the declared values. -/
theorem Run.verdict_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat) (hi : i < c.claims.length) :
    Run.verdictAt (Run.runCaseReported j) i = some ((c.claims[i]'hi).2.decide (values c.decls))

end VE.Calc

namespace VE.Service
theorem runMode_calc (j : Lean.Json) : runMode .calc j = VE.Calc.Run.runCaseReported j := rfl
end VE.Service

namespace ResponseShape.Encoders.Calc
theorem runCaseReported_fits (j : Lean.Json) :
    ResponseShape.Fits j ResponseShape.Skeletons.calc (VE.Calc.Run.runCaseReported j)
end ResponseShape.Encoders.Calc
```

(`Run.verdictAt` reads the verdict word of row `i`; `ResponseShape.Fits` stands for the predicate the existing
encoder theorems use, as in `ResponseShape.Encoders.Discourse.runCaseReported_fits`; ME-S fixes both names.)

### 3.3 ME-4: tables and data

```lean
namespace VE.Calc

inductive Cell where
  | num (q : Rat) | text (s : String) | bool (b : Bool) | absent
  deriving Repr, DecidableEq

structure Table where
  columns : List String
  rows : List (List Cell)

inductive Filter where
  | all | isText (col v : String) | equals (col : String) (q : Rat) | isTrue (col : String)
  | not (f : Filter) | and (f g : Filter) | or (f g : Filter)

inductive Agg where
  | count | sum (col : String) | mean (col : String) | min (col : String) | max (col : String)

def Filter.Selects (T : Table) : Filter → List Cell → Prop
def Table.select (T : Table) (f : Filter) : List (List Cell)

theorem Table.select_iff (T : Table) (f : Filter) (row : List Cell) :
    row ∈ T.select f ↔ row ∈ T.rows ∧ f.Selects T row

/-- The numbers in a column of the selected rows, or none if a selected cell there is not a number. -/
def Table.numbers (T : Table) (f : Filter) (col : String) : Option (List Rat)

def Agg.run (T : Table) (f : Filter) : Agg → Option Rat

theorem Agg.run_count (T : Table) (f : Filter) : Agg.run T f .count = some ((T.select f).length : Rat)
theorem Agg.run_sum (T : Table) (f : Filter) (col : String) (q : Rat) :
    Agg.run T f (.sum col) = some q ↔ ∃ xs, T.numbers f col = some xs ∧ q = xs.sum
theorem Agg.run_mean (T : Table) (f : Filter) (col : String) (q : Rat) :
    Agg.run T f (.mean col) = some q ↔ ∃ xs, T.numbers f col = some xs ∧ xs ≠ [] ∧ q = xs.sum / xs.length

/-- Decoders: the CSV and JSON-lines subsets of 2.5. -/
def decodeTable (format : String) (columns : List (String × String)) (bytes : ByteArray) : Except String Table

/-- A counted value is computed only from bytes whose SHA-256 is the declared handle. -/
theorem counted_bound (handles : List (String × ByteArray)) (d : String) (f : Filter) (a : Agg) (q : Rat)
    (h : runCounted handles d f a = some q) :
    ∃ bytes T, handles.lookup d = some bytes ∧ VE.CertificateWire.sha256 bytes = d ∧
      decodeTable (formatOf d) (columnsOf d) bytes = .ok T ∧ Agg.run T f a = some q

end VE.Calc
```

(`runCounted`, `formatOf` and `columnsOf` are ME-4's; SHA-256 is trusted code without a refinement theorem, as for
the risk log, and the plan does not claim more.)

### 3.4 ME-5: derivations over rational unknowns

```lean
namespace VE.Calc

/-- A linear form over unknowns with rational coefficients. A separate module from the frozen integer `VE.Order.Lin`:
its unknowns range over ℚ and it has no cuts. -/
structure QLin where
  const : Rat
  coeffs : List (String × Rat)

def QLin.eval (κ : String → Rat) (L : QLin) : Rat

/-- A fact `0 ≤ L`, or `0 < L` when strict. -/
structure QFact where
  form : QLin
  strict : Bool

def QFact.Holds (κ : String → Rat) (f : QFact) : Prop :=
  if f.strict then 0 < f.form.eval κ else 0 ≤ f.form.eval κ

/-- Nonnegative weights whose combination cancels every unknown and leaves a negative constant (or zero, with a
positive weight on a strict fact). -/
structure Farkas where
  weights : List Rat

def Farkas.check (fs : List QFact) (c : Farkas) : Bool

theorem Farkas.check_sound (fs : List QFact) (c : Farkas) (h : c.check fs = true) :
    ∀ κ : String → Rat, ¬ ∀ f ∈ fs, f.Holds κ

/-- The proved square rule. -/
theorem lt_of_sq_lt (x a b : Rat) (hx : 0 ≤ x) (hb : 0 < b) (h : x * x < a) (hab : a ≤ b * b) : x < b

/-- A derivation step list is accepted only if each step is a checked Farkas refutation of (premises and the negated
step) or one square-rule step; then the conclusion holds wherever the premises and square links hold. -/
theorem Derivation.check_sound (P : List QFact) (links : List (String × String)) (C : QFact) (d : Derivation)
    (h : d.check P links C = true) :
    ∀ κ : String → Rat, (∀ f ∈ P, f.Holds κ) →
      (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) → C.Holds κ

/-- A reported counterexample is checked by evaluation. -/
theorem Counterexample.check_sound (P : List QFact) (C : QFact) (κ : String → Rat)
    (h : counterexampleCheck P C κ = true) : (∀ f ∈ P, f.Holds κ) ∧ ¬ C.Holds κ

end VE.Calc
```

### 3.5 ME-6: physical dimensions

```lean
namespace VE.Calc

/-- A physical dimension: an exponent per base dimension; normal form sorted by name, no zero exponent. -/
structure PhysDim where
  exps : List (String × Int)
  deriving Repr, DecidableEq

def PhysDim.Normal (d : PhysDim) : Prop
def PhysDim.one : PhysDim := ⟨[]⟩
def PhysDim.mul (a b : PhysDim) : PhysDim
def PhysDim.inv (a : PhysDim) : PhysDim
def PhysDim.npow (a : PhysDim) (k : Nat) : PhysDim

/-- The physical dimension of an expression, given each name's; literals are dimensionless; sums need equal ones. -/
def Expr.dimOf (Γ : String → Option PhysDim) : Expr → Option PhysDim

/-- A change of base units: a positive factor per base dimension. -/
structure Rescale where
  factor : String → Rat
  pos : ∀ b, 0 < factor b

def zpowR (q : Rat) : Int → Rat
  | .ofNat n => q ^ n
  | .negSucc n => 1 / q ^ (n + 1)

def Rescale.of (ρ : Rescale) (d : PhysDim) : Rat := (d.exps.map fun e => zpowR (ρ.factor e.1) e.2).foldl (· * ·) 1

theorem Rescale.of_pos (ρ : Rescale) (d : PhysDim) : 0 < ρ.of d
theorem Rescale.of_mul (ρ : Rescale) (a b : PhysDim) (ha : a.Normal) (hb : b.Normal) :
    ρ.of (a.mul b) = ρ.of a * ρ.of b

/-- Every named value rescaled by its own physical dimension's factor. -/
def Rescale.apply (ρ : Rescale) (Γ : String → Option PhysDim) (σ : Values) : Values :=
  fun n => match σ n, Γ n with
    | some q, some d => some (q * ρ.of d)
    | v, _ => v

theorem denotes_rescale (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (e : Expr) (d : PhysDim) (x : Rat)
    (hΓ : ∀ n, (Γ n).isSome → (Γ n).get!.Normal) (hd : e.dimOf Γ = some d) (hx : Denotes σ e x) :
    Denotes (ρ.apply Γ σ) e (x * ρ.of d)

/-- **Unit-change invariance**: a comparison between two expressions of one physical dimension has the same truth in
every system of base units. -/
theorem compare_invariant (Γ : String → Option PhysDim) (ρ : Rescale) (σ : Values) (r : Rel) (a b : Expr)
    (d : PhysDim) (hΓ : ∀ n, (Γ n).isSome → (Γ n).get!.Normal)
    (ha : a.dimOf Γ = some d) (hb : b.dimOf Γ = some d) :
    (Claim.compare r a b).Holds σ ↔ (Claim.compare r a b).Holds (ρ.apply Γ σ)

/-- Units are values (their factor in the coherent unit): an amount `q` in unit `u` is the amount `q · fu / fv` in unit
`v` of the same physical dimension, so quantities' `convert_iff` becomes a corollary. -/
theorem convert_by_factors (σ : Values) (u v : String) (fu fv q x : Rat) (hu : σ u = some fu) (hv : σ v = some fv)
    (hfv : fv ≠ 0) :
    Denotes σ (.mul (.lit q) (.val u)) x ↔ Denotes σ (.mul (.lit (q * fu / fv)) (.val v)) x

end VE.Calc
```

(`ve-units@2`'s unit record is decoded in ME-6 or by quantities' QT-A7, whichever lands first; the other extends it.)

### 3.6 ME-7: statistics

```lean
namespace VE.Calc

def mean? (xs : List Rat) : Option Rat := if xs = [] then none else some (xs.sum / xs.length)

/-- Sample variance (divisor n − 1); none below two values. -/
def sampleVariance? (xs : List Rat) : Option Rat

/-- Population variance (divisor n). -/
def populationVariance? (xs : List Rat) : Option Rat

/-- "The square root of v, rounded, is p" for 0 ≤ v, by squared bounds; this is the definition. -/
def SqrtRoundsTo (r : Rounding) (p : Printed) (v : Rat) : Prop

/-- Agreement with rounding the root whenever the root is rational. -/
theorem sqrtRoundsTo_of_square (r : Rounding) (p : Printed) (s v : Rat) (hs : 0 ≤ s) (hv : s * s = v)
    (hp : 0 ≤ p.digits) : SqrtRoundsTo r p v ↔ RoundsTo r p s

/-- All sign vectors of length n. -/
def signs : Nat → List (List Int)
  | 0 => [[]]
  | n + 1 => (signs n).flatMap fun s => [1 :: s, -1 :: s]

theorem signs_length (n : Nat) : (signs n).length = 2 ^ n
theorem mem_signs (n : Nat) (s : List Int) : s ∈ signs n ↔ s.length = n ∧ ∀ k ∈ s, k = 1 ∨ k = -1

def absR (x : Rat) : Rat := if x < 0 then -x else x

/-- The exact two-sided sign-flip p value: the share of sign vectors whose signed mean is at least the observed mean
in absolute value (the observed vector counted), as `paper/analysis/README.md` defines it. -/
def signFlipP (d : List Rat) : Rat :=
  let obs := absR (d.sum / d.length)
  let hits := (signs d.length).filter fun s =>
    decide (obs ≤ absR ((List.zipWith (fun k x => (k : Rat) * x) s d).sum / d.length))
  (hits.length : Rat) / (2 ^ d.length : Nat)

/-- An enumeration p value is a multiple of 1/2^n. -/
theorem signFlipP_grain (d : List Rat) : ∃ m : Nat, signFlipP d = (m : Rat) / (2 ^ d.length : Nat)

def binomialTail (n k : Nat) (p : Rat) : Rat :=
  ((List.range (n + 1)).filter (k ≤ ·)).foldl (fun acc i => acc + (Nat.choose n i : Rat) * p ^ i * (1 - p) ^ (n - i)) 0

/-- Cohen's kappa of a square agreement table; none when chance agreement is 1. -/
def kappa? (t : List (List Nat)) : Option Rat

end VE.Calc
```

(`Nat.choose` is core's if present in the pinned toolchain; otherwise ME-7 defines it with `choose_succ_succ`.)

### 3.7 ME-8: consistency of printed numbers

```lean
namespace VE.Calc

/-- A printed input stands for every value in its rounding interval. -/
def InBox (r : Rounding) (inputs : List (String × Printed)) (σ : Values) : Prop :=
  ∀ i ∈ inputs, ∃ x, σ i.1 = some x ∧ RoundsTo r i.2 x

/-- Witness: exact inputs inside their boxes under which every output claim holds. -/
theorem witness_sound (r : Rounding) (inputs : List (String × Printed)) (outs : List Claim) (σ : Values)
    (h : witnessCheck r inputs outs σ = true) : InBox r inputs σ ∧ ∀ c ∈ outs, c.Holds σ

/-- Exact interval evaluation over the boxes encloses every value the expression can take. -/
theorem enclose_sound (r : Rounding) (inputs : List (String × Printed)) (e : Expr) (lo hi : Rat)
    (h : enclose r inputs e = some (lo, hi)) :
    ∀ σ x, InBox r inputs σ → (∀ n, σ n ≠ none → n ∈ inputs.map Prod.fst) → Denotes σ e x → lo ≤ x ∧ x ≤ hi

/-- An enclosure that misses an output's printed interval proves the printed numbers inconsistent. -/
theorem inconsistent_of_enclosure (r : Rounding) (inputs : List (String × Printed)) (c : Claim)
    (h : refuteByEnclosure r inputs c = true) :
    ¬ ∃ σ, InBox r inputs σ ∧ (∀ n, σ n ≠ none → n ∈ inputs.map Prod.fst) ∧ c.Holds σ

end VE.Calc
```

### 3.8 ME-9: algebraic identities

```lean
namespace VE.Calc

/-- A monomial: a coefficient and variables with positive exponents, sorted by name. -/
structure Mono where
  coeff : Rat
  vars : List (String × Nat)

/-- A normal polynomial: monomials sorted by their variable lists, no repeated list, no zero coefficient. -/
abbrev Poly := List Mono

def Poly.eval (κ : String → Rat) (p : Poly) : Rat
def Poly.ofExpr? : Expr → Option Poly   -- division-free expressions only

theorem Poly.ofExpr_sound (κ : String → Rat) (e : Expr) (p : Poly) (h : Poly.ofExpr? e = some p) :
    Denotes (fun n => some (κ n)) e (p.eval κ)

/-- Numerator and denominator of an expression with division. -/
def Frac.ofExpr? : Expr → Option (Poly × Poly)

theorem Frac.ofExpr_sound (κ : String → Rat) (e : Expr) (n d : Poly) (x : Rat)
    (h : Frac.ofExpr? e = some (n, d)) (hx : Denotes (fun v => some (κ v)) e x) :
    d.eval κ ≠ 0 ∧ x = n.eval κ / d.eval κ

/-- **Identity**: equal cross-multiplied normal forms mean equal values wherever both sides denote. -/
theorem identity_sound (a b : Expr) (h : identityCheck a b = true) (κ : String → Rat) (x y : Rat)
    (hx : Denotes (fun v => some (κ v)) a x) (hy : Denotes (fun v => some (κ v)) b y) : x = y

end VE.Calc
```

### 3.9 ME-12 and ME-13: `arith@0` and imports

```lean
namespace VE.Arith

mutual
/-- Terms: numerals, variables (de Bruijn), sum, difference, product, calls of defined functions, and bounded counts
("the number of whole numbers p from lo through hi such that φ"). -/
inductive Term where
  | var (i : Nat) | num (n : Int) | add (a b : Term) | sub (a b : Term) | mul (a b : Term)
  | call (f : String) (args : List Term)
  | countFromTo (lo hi : Term) (φ : Formula)

inductive Formula where
  | eq (a b : Term) | lt (a b : Term) | le (a b : Term) | dvd (a b : Term)
  | call (p : String) (args : List Term)
  | not (φ : Formula) | and (φ ψ : Formula) | or (φ ψ : Formula) | imp (φ ψ : Formula)
  | allNat (φ : Formula) | exNat (φ : Formula) | allInt (φ : Formula) | exInt (φ : Formula)
  | allFromTo (lo hi : Term) (φ : Formula) | exFromTo (lo hi : Term) (φ : Formula)
end

/-- Non-recursive definitions, each over earlier names only. -/
structure Defs where
  funs : List (String × Nat × Term)
  preds : List (String × Nat × Formula)

/-- Inline every call (definitions are acyclic, so this terminates); none on an unknown name or a wrong arity. -/
def Defs.expand (D : Defs) : Formula → Option Formula

/-- Every quantifier of the formula is bounded (checked at admission for every count's condition). -/
def Formula.Bounded : Formula → Prop

/-- The meaning, over call-free terms and formulas, defined together with a structural Boolean evaluation of bounded
formulas (no budget). Whole-number binders range over 0, 1, 2, …; `allFromTo lo hi` over the integers from lo
through hi; `countFromTo lo hi φ` is the number of integers i from lo through hi with `evalB (i :: ρ) φ = some true`
(0 when hi < lo). -/
def Term.value (ρ : List Int) : Term → Option Int
def Formula.evalB (ρ : List Int) : Formula → Option Bool
def Holds (ρ : List Int) : Formula → Prop

/-- On bounded formulas the Boolean evaluation is the meaning. -/
theorem holds_iff_evalB (ρ : List Int) (φ : Formula) (hb : φ.Bounded) (v : Bool) (h : φ.evalB ρ = some v) :
    Holds ρ φ ↔ v = true

def Defs.Means (D : Defs) (φ : Formula) : Prop := ∃ ψ, D.expand φ = some ψ ∧ Holds [] ψ

/-- Bounded evaluation: none on an unbounded binder or an exhausted budget. -/
def decideBounded (budget : Nat) (ρ : List Int) : Formula → Option Bool

theorem decideBounded_sound (budget : Nat) (ρ : List Int) (φ : Formula) (v : Bool)
    (h : decideBounded budget ρ φ = some v) : Holds ρ φ ↔ v = true

/-- An import record, admitted by identity, axioms and names; its truth rests on the external build. -/
structure Import where
  statementId : String
  project : String
  toolchain : String
  mathlibRev : String
  declaration : String
  axioms : List String

def allowedAxioms : List String := ["propext", "Classical.choice", "Quot.sound"]

def Import.admit (D : Defs) (φ : Formula) (i : Import) : Except String Unit

theorem Import.admit_axioms (D : Defs) (φ : Formula) (i : Import) (h : i.admit D φ = .ok ()) :
    i.statementId = statementId D φ ∧ ∀ a ∈ i.axioms, a ∈ allowedAxioms

/-- A report that uses an admitted import lists the leaf `import:<project>@<rev>/<declaration>` among its
assumptions; no `arith` report concludes an unbounded statement without such a leaf or a bounded decision. -/
theorem report_import_labelled (r : Report) (h : r.Accepted) :
    ∀ φ ∈ r.conclusions, r.decidedBounded φ ∨ ∃ i ∈ r.imports, importLabel i ∈ r.assumptions

end VE.Arith
```

The import project's proof for EX-1 has this shape (Mathlib side; `Nat.bertrand` is from memory and ME-S checks the
name):

```lean
import Mathlib.NumberTheory.Bertrand
import VE.Arith.Examples

theorem VEImports.bertrand_holds : VE.Arith.Examples.bertrandDefs.Means VE.Arith.Examples.bertrand := by
  rw [VE.Arith.Examples.bertrand_means_iff]          -- core-Lean unfolding lemma, proved in VE
  intro n hn
  obtain ⟨p, hp, h1, h2⟩ := Nat.bertrand n (by omega)
  exact ⟨p, (VEImports.isPrime_iff_nat_prime p).mpr hp, h1, h2⟩

/-- The one bridge lemma for this vocabulary: VE's definition of prime is Mathlib's. -/
theorem VEImports.isPrime_iff_nat_prime (p : Nat) :
    VE.Arith.Examples.IsPrime p ↔ Nat.Prime p
```

## 4. Fixtures

Expected results were computed by hand in exact arithmetic for this plan; ME-S recomputes every one with `#eval` in the
stub and the batches pin them as `#guard`s and route cases. Target sentences marked *paraphrase* are from memory and
are re-anchored to the pinned text's byte spans in ME-0; their arithmetic does not depend on the exact wording.

### 4.1 VE's own paper and documentation (in the repository; exact quotes)

| Id | Source | Case | Expected |
|---|---|---|---|
| V-1 | `paper/sections/04-e1.md`: "Its scored baseline, 176/594 = .296, is outside the gate band" (the band is 30-60%) | 176/594 = 8/27; rounds to 0.296 (ties up: 591 ≤ 2,000 × 8/27 = 592.59 < 593); and 8/27 < 0.30 (80 < 81) | holds, holds |
| V-1n | the same with "0.297" | 593 ≤ 592.59 is false | **fails** (seeded-bug target) |
| V-2 | `04-e1.md`: "false approval is 52/243 (.214) versus 31/243 (.128), an 8.6-point pooled increase" | 52/243 → 0.214 (427 ≤ 427.98 < 429); 31/243 → 0.128 (255 ≤ 255.14 < 257); 100 × 21/243 = 8.642 → 8.6 (171 ≤ 172.84 < 173) | holds ×3 |
| V-3 | `05-e4.md`: "For 7B, prose rejects 56/60 valid inferences; checked feedback increases HA from 4/60 to 52/60" | premise (assumption leaf): every reply is an approval or a rejection; 60 − 56 = 4 | holds, with the leaf in the residual |
| V-4 | `04-e1.md`: "The 32B symbolic/no-explanation baseline was 34/110 false approvals, only one candidate inside the primary 30--60% gate" | 34/110 within [0.30, 0.60] | holds |
| V-5 | `paper/generated/posthoc-weakening-rates.md`, 20 rows "Approved / weakening" against "Pooled FA" | e.g. 151/243 → 0.621, 155/243 → 0.638, 136/243 → 0.560, 90/243 → 0.370, 43/243 → 0.177, 37/243 → 0.152 | all 20 hold (hand-checked) |
| V-6 | `paper/sections/10-appendices.md`, row "14B AWQ, P1 attacker": twelve printed per-template differences, "SD between templates 0.108", "SE with 12 templates 0.031", "97.5% half-width with 12 (t = 2.593) 0.081" | values in thousandths: Σx = −545 (thousandths), Σx² = 152,053 (millionths), n = 12; sample variance v = 1,527,611 / 132,000,000; `sqrt-rounds` v to 0.108 (1,525,425 ≤ 1,527,611 < 1,553,937 in units of 1/132,000,000, the squares of 0.1075 and 0.1085); v/12 to 0.031; 2.593² × v/12 to 0.081 (0.00648430 against the lower bound 0.0805² = 0.00648025) | holds ×3; t = 2.593 is a stated constant with its source |
| V-6r | the same printed SD under the population reading (divisor 12) | 0.127301/12 = 0.010608; its root 0.1030 prints as 0.103 | **fails**: the calculation distinguishes the two readings of "SD" |
| V-7 | `paper/generated/posthoc-weakening-contrasts.md`, column "Two-sided p", 9 templates | granularity: a printed p must be within rounding of a multiple of 1/512 (0.812500 = 416/512, 0.687500 = 352/512, 0.359375 = 184/512, 0.125000 = 64/512, 0.875000 = 448/512; 0.085938 from 44/512 and 0.679688 from 348/512, both exact ties at the lower end of their intervals) | consistent for 7 of 8 under ties upward; the eighth is V-8 (ME-8) |
| V-8 | the same table, row "14B F − S attacker", printed "0.007812" | 4/512 = 0.0078125 is an exact tie at six places: half to even gives 0.007812 (holds), ties up gives 0.007813 (fails) | holds only under "rounded half to even"; in translation without a declared rule, a **reading set** whose distinguishing value is this row |
| D-1 | ROADMAP: "Math mini paper: **17/19** current verified outcomes (15 tableau certificates plus T9 and T9e by closure induction)" | 15 + 2 = 17 | holds |
| D-2 | UDHR pilot SUMMARY (copied into the test data with its path and digest): "claimed covered bytes 4,792 (43.90%)" of 10,916 | 100 × 4,792/10,916 = 43.899 → 43.90 (8,779 ≤ 8,779.8 < 8,781) | holds |
| D-3 | constitution pilot SUMMARY: "Claimed coverage is unchanged at 2,951 bytes (1.60%)", with `coverage.json` bytes CHECKED 73, LABELLED 349, OPEN 2,529 | 73 + 349 + 2,529 = 2,951; 100 × 2,951/184,893 = 1.596 → 1.60 | holds ×2 |

### 4.2 Physics (Michelson and Morley 1887; paraphrases until ME-0 anchors them)

| Id | Sentence (paraphrase) | Case | Expected |
|---|---|---|---|
| H-1 | "T = D/(V − v), T₁ = D/(V + v); the whole time of going and coming is T + T₁ = 2DV/(V² − v²)" | `identity` over free D, V, v | identity (ME-9), side conditions V ≠ v, V ≠ −v |
| H-2 | "the distance traveled in this time is 2DV²/(V² − v²) = 2D(1 + v²/V²), neglecting terms of the fourth order" | the exact remainder: 2DV²/(V² − v²) − 2D(1 + v²/V²) = 2Dv⁴/(V²(V² − v²)) | identity (ME-9); "neglecting" becomes the exact remainder, bounded numerically at v/V = 10⁻⁴ by ME-1 (EX-2 for the general bound) |
| H-3 | "the difference is therefore Dv²/V²" | 2D(1 + v²/V²) − 2D(1 + v²/(2V²)) = Dv²/V² | identity (ME-9) |
| H-4 | "the displacement ... should be 2Dv²/V² ... this would be 2D × 10⁻⁸" | with v/V = 10⁻⁴ stated and D free: 2D × (10⁻⁴)² = 2D × 10⁻⁸ | identity in D (ME-9); with D stated, holds (ME-1) |
| H-5 | "D ... 2 × 10⁷ wave-lengths of yellow light; hence the displacement to be expected was 0.4 fringe" | 2 × (2 × 10⁷) × (10⁻⁴)² = 0.4 | holds (ME-1) |
| H-6 | "certainly less than the twentieth part of this ... the relative velocity ... certainly less than one-fourth [of the orbital velocity]" | premises: displacement = 0.4 fringe × r² (assumption: proportional to the square), r ≥ 0, displacement < 0.4/20 fringe; claim r < 1/4 | **follows** (ME-5: Farkas gives r² < 1/20; square rule with 1/20 ≤ 1/16) |
| H-6p | the "probably" pair: fortieth part, one sixth | r² < 1/40 and 1/40 ≤ 1/36 | follows; the hedge "probably" stays a `hedged` label until attitudes lands |
| H-6n | negative control: "less than one fifth" from "less than the twentieth part" | 1/20 ≤ 1/25 is false | **does not follow**; counterexample r = 1/5 (r² = 1/25 < 1/20; the search tries the claimed bound itself first) |
| H-7 | physical dimensions: "D/(V − v)" is a time; "D/λ" is dimensionless; negative "D + T" | ME-6 | time; dimensionless; `DimensionMismatch(length, time)` |
| H-8 | "about eleven meters, or 2 × 10⁷ wave-lengths of yellow light" | with the external premise "the wavelength of yellow light is 5.89 × 10⁻⁷ meters" (stated, `support: testimony`, cited): 11 m / λ = 1.868 × 10⁷, rounds to 2 × 10⁷ at places −7 (3 ≤ 3.735 < 5) | holds; "about" is a reading set in translation; the wavelength is a residual leaf |
| H-9 | the two observation tables: readings at 16 azimuths per session and their printed means | `counted` means over the transcribed table (ME-4) against the printed means | whatever exact arithmetic gives; a mismatch is a finding (no outcome is presumed here) |
| H-10 | the observation dates (July 8, 9, 11 and 12, 1887) | W6a date literals start at 1970-01-01 (W6 6.1), so these are refused | refused today; a question for events-time-causation (section 10, piece 8) |

### 4.3 Mathematics (Ramanujan 1919; paraphrases)

| Id | Sentence or case | Expected |
|---|---|---|
| M-1 | "by actual verification ... true for smaller values": "for every whole number n from 1 to 161, there is a prime p with n < p and p at most twice n" | bounded evaluation: holds (ME-12) |
| M-2 | the standard check of the small cases (not Ramanujan's wording): the chain 2, 3, 5, 7, 13, 23, 43, 83, 163, each prime and each less than twice the one before | holds (3 < 4, 5 < 6, 7 < 10, 13 < 14, 23 < 26, 43 < 46, 83 < 86, 163 < 166) |
| M-3 | Bertrand's postulate, whole-number reading: "for every whole number n that is at least 1 there is a prime p with n < p and p at most twice n" | unbounded: no bounded decision; proved only by import (EX-1) |
| M-3r | the same with a real x (Ramanujan's x is real) | a reading set {whole number, real}; `arith@0` has no reals, so the real reading stays residual |
| M-4 | "π(x) − π(x/2) ≥ 2 if x ≥ 11", bounded part for whole x from 11 to 1,000 | holds by evaluation (at x = 10 the difference is 1, at x = 11 it is 2); the unbounded remainder is residual or import |
| M-5 | negative control: strict "n < p < 2n" from 1 to 161 | **fails** at n = 1 |

### 4.4 Deep learning (after ME-0 pins a CC-BY text; shapes only, no numbers presumed)

DL-1 "our method has the highest score in column C" (maximum over the table's rows equals the method's cell); DL-2 "on
average across the eight tasks" (mean of a row); DL-3 "reduces the number of trainable parameters by about N times"
(a ratio of stated counts; "about" a reading set {rounded to the written digits, open tolerance}); DL-4 a parameter
count from a stated formula and stated sizes; DL-5 "on par with" (refused in authoring; an open term in translation).

### 4.5 Negative controls from the pinned pilots, and regressions

- Constitution u0203.s02, u0112.s03 and u0147.s04 stay as they are: their "evidence" and "probability" are epistemic
  standards in norms (research 2.2). A calc case cannot carry a norm, an open term or a reading of them (`Unsupported`).
- W6a's news fixtures (`tests/test_news_w6a_fixtures.py`) and the math mini-paper's 18/19 are unchanged by every batch.

## 5. Batches

Every batch follows the rules quantities' plan 1.3 also lists: the selected tests while iterating, the full gate once on
the final HEAD, `python3 lean/audit.py` (standard axioms only, no forbidden words even in comments, theorem names under
about 57 characters), generated files regenerated with `uv run python tools/regen_generated.py --write` and merges
finished with `--resolve`, new trusted Lean lines with a signed allowance (`tools/trust_map.py --write --reason`, a
person) and a ROADMAP trust-cost line, hermetic tests, three-valued verdicts, and a seeded bug in each changed language.

### ME-0. Pin the targets; baseline partition (pilot runner, 3-4 h, no product code)

- **Pin**: for each target, fetch the text with a plain HTTP client (no model), record URL, retrieval time, licence
  evidence (publication date and authors' deaths for the public-domain texts; the licence link of the abstract page
  for a CC-BY one) and SHA-256 in `SOURCE.md`. New directories: `usecases/physics-michelson-morley/`,
  `usecases/math-ramanujan-bertrand/`, `usecases/ve-paper-e1/` (pins `paper/sections/04-e1.md` and the appendix table
  rows by SHA-256 at the batch's commit), and `usecases/dl-<slug>/` only for a confirmed CC-BY licence. Transcribe
  formulas into words in the translation, never into the source file.
- **Partition** every byte into units with kinds (exposition, definition, theorem, proof step, equation, quantity,
  table, empirical claim, comparison, hedge, citation, caption, meta) and today's statuses: W6a quantity facts and
  linear comparisons with unit tags (CHECKED), attributions (`reports@0`), labels (LABELLED), and UNFORMALISED with one
  `missing_feature` from: `calc`, `calc-data`, `calc-derive`, `calc-dimension`, `calc-stats`, `calc-algebra`,
  `arith`, `arith-import`, `approximation`, or a sibling's tag (`quantities`, `attitudes`, `events`, `attribution`).
- **Measure**: `coverage.json` with bytes by status and kind; a sentence-kind count replacing research 2.5's estimates;
  the NORTH-STAR rows M, H, DL, V refreshed from measurements.
- Shared files: none (new directories). Estimated: H 1.5-2.5 KB CHECKED, 13-16 KB LABELLED; V-E1 0.3-0.8 KB CHECKED;
  M 0 CHECKED; DL 2-4 KB if pinned (all **estimates**). Constitution and UDHR: 0.
- Done when the four (or three) ledgers account for 100% of their source bytes and `SUMMARY.md` states the numbers.

### ME-S. Statement spec, Lean stub, statement review (planner, 4-5 h)

Write `docs/spec/math-evidence.md` (statements of section 3 made exact, wire forms of section 2, diagnostics, the
fixtures of section 4 with definitions separated from expected results); elaborate section 3 in an untracked
`lean/SpecStubs_math_evidence.lean` against `main` (or a build at the same `lean/` tree); recompute every fixture with
`#eval` over `Rat`; settle the names `ResponseShape.Fits`, `Run.verdictAt`, `Nat.choose`, `Nat.bertrand`; record
which of quantities' QT-A2 and ME-1 provides the rounding module. Statement review by the reviewer pair (section 9).

### ME-1. Lean core of `calc@0` (Lean, 5-6 h)

- New files: `lean/VE/Calc/{Syntax,Round,Eval,Decls,Render,Examples}.lean`, `lean/CALC.md` (statement review notes,
  as `lean/RISK.md`). `Round.lean` moves to the shared module if the cross-plan review places it there.
- Proves 3.1. `Render.lean` gives the English line of each claim from `words` and the fixed phrases of 2.11 (display
  only; parse-back arrives with ME-11).
- `#guard` fixtures: V-1, V-1n, V-2, V-4, D-1, H-5, and H-4 with D stated.
- Hand-written shared: none. Generated: `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements,
  predicates, declarations, trust tables (signed).
- Seeded bug (Lean): `eval` computes `sub a b` as `b - a`; V-2's third claim fails its `#guard`.
- Bytes: 0 (no pilot run).

### ME-2. Wire and service mode `calc` (Lean, 5-6 h)

- New files: `lean/VE/Calc/{Wire,Run}.lean`, `lean/ResponseShape/Schemas/Calc.lean`,
  `lean/ResponseShape/Encoders/Calc.lean`.
- Proves 3.2 and the decoder limits of 2.1 in order; identities of 2.2.
- Hand-written shared: `lean/VE/Service/Protocol.lean` (constructor, name, list entry, dispatch line,
  `runMode_calc`), `ve/backends/service_schema.py` (`MODES`), `lean/VE/Compose/Dispatch.lean` (the `calc@0` row and
  its gate lemmas; `#guard` examples in `lean/VE/Compose/Examples.lean`), `ve/profiles.py` (one row),
  `ve/assurance-manifest.json` (decoder pins, by hand), `ROADMAP.md` (trust-cost line). Generated:
  `ve/backends/lean_service_schema/calc.json`, `lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`,
  `lean/checkers.lock`, `docs/spec/assurance-manifest.md`, `lean/VE/Route/examples/route-cases.json`, and ME-1's list.
- Route cases: V-1, V-2, V-5 (20 claims in one case), a hostile set (unknown name, a name defined after its use,
  `pow` above the limit, a literal of 41 digits, a printed spelling with a sign error, a forged `meaning_id`).
- Seeded bug (Lean): the runner reports claim i + 1's verdict for claim i; the route-case test fails.
- Bytes: 0.

### ME-3. Python relay, command, fuzz tests (Python, 4-5 h)

- New files: `ve/calc.py` (sends cases with `rows` from `ve/backends/relay.py`; binds every claim id, value name and
  data handle in the answer to the request; displays Lean's English lines and exact values), `tests/test_calc_lean.py`,
  `tests/test_calc_answer.py` (fuzz: each member dropped, emptied, retyped, duplicated, reordered, an index out of
  range, one and two faults at a time; every mutant is `CheckerUnavailable` or changes nothing shown).
- Hand-written shared: `ve/__main__.py` (subcommand `ve calc check FILE`), `tools/layer_policy.py` (one row),
  `tests/data/route-cases.jsonl` (recorded by `tests/route_case_recorder.py`, append-only). Generated: `.importlinter`,
  `tools/gate-collection.json`.
- Seeded bug (Python): the binding check skips claim ids; a fuzz mutant that swaps two claim ids is accepted and the
  fuzz test fails.
- Bytes: 0.

### ME-P1. Pilot: ground calculations (pilot runner, 2-3 h)

Companion calc cases beside the ME-0 ledgers (as the UDHR pilot's companion documents): physics H-5, H-4 with D
stated, H-8 and the theory section's other numeric substitutions; VE paper V-1 to V-4 and the other ratio sentences of `04-e1.md` and `05-e4.md`.
A unit is CHECKED when every claim of its companion case is decided by Lean. Estimated: H +0.6-1.0 KB, V +0.8-1.5 KB.
Shared files: pilot directories only.

### ME-4. Tables and pinned data (Lean and Python, 5-6 h)

- New files: `lean/VE/Calc/{Table,Csv,Jsonl,Data}.lean`, `tests/test_calc_tables.py`, `tests/data/calc/*.csv` and
  `*.jsonl` (small, committed).
- Proves 3.3. The service's handle table gains a data kind (`lean/VE/Service/Protocol.lean`, the `Handles` structure:
  hand-written shared, additive); the relay registers file bytes by SHA-256 and sends them; Lean recomputes the digest.
- Fixtures: a 30-row synthetic trial table with counts by filter; V-5 recomputed from a committed table of the
  20 rows' counts; H-9 when ME-0 has transcribed the observation tables; an absent cell making a mean undefined; a wrong
  digest refused.
- Seeded bugs: Lean, `not` in a filter selects the same rows as its operand (a count fixture fails); Python, the
  relay sends the bytes of the wrong handle (the digest refusal test fails).
- Bytes: 0 (lands in ME-P2).

### ME-5. Derivations over rational unknowns (Lean, 5-6 h)

- New files: `lean/VE/Calc/{Linear,FourierMotzkin,Derive}.lean`, `tests/test_calc_derive.py`.
- Proves 3.4. Fourier-Motzkin elimination with multiplier tracking, within a budget (64 facts, 16 unknowns, 10,000
  combination steps); its output is replayed by `Farkas.check`; counterexamples are checked by evaluation.
- Fixtures: H-6, H-6p, H-6n; a linear system with no solution and its certificate; a forged certificate with a
  negative weight refused.
- Seeded bug (Lean): `Farkas.check` accepts a negative weight; a forged certificate for a false conclusion is accepted
  and its regression fails.
- Bytes: 0.

### ME-6. Physical dimensions (Lean, 4-5 h; after the cross-plan review)

- New files: `lean/VE/Calc/{Dimension,Units}.lean`, `tests/test_calc_dimensions.py`.
- Proves 3.5. Decodes `ve-units@2`'s base dimensions, `base_exponents` and `factor` (or reads quantities' QT-A7
  decoder if it landed first and extends it in place, one owner); refuses affine and logarithmic units by name;
  proves `ve-units@1` environments mean what they meant (no `base_exponents`: every tag dimensionless, as today).
- Fixtures: H-7; meters against kilometers converted by factors; a sum of a length and a time refused with both names.
- Seeded bug (Lean): `dimOf` of `div` adds exponents instead of subtracting; H-7's "D/λ is dimensionless" fails.
- Bytes: 0.

### ME-P2. Pilot: tables, bounds and dimensions (pilot runner, 3 h)

Physics: the observation tables (H-9), the velocity bounds (H-6, H-6p), dimensions of the theory section (H-7). VE
paper: counts recomputed from committed count tables (V-5). Estimated: H +3.0-4.5 KB, V +1-2 KB.

### ME-7. Exact statistics (Lean, 5-6 h)

- New files: `lean/VE/Calc/Stats.lean`, `tests/test_calc_stats.py`.
- Proves 3.6. Assumption leaves per procedure (2.8).
- Fixtures: V-6, V-6r; a sign-flip p over 12 synthetic differences checked against exhaustive hand enumeration; a
  binomial tail; Cohen's kappa of a 2 × 2 table.
- Seeded bug (Lean): the sample variance divides by n; V-6's SD claim fails (it would print 0.103).
- Bytes: 0.

### ME-8. Consistency of printed numbers (Lean, 4-5 h)

- New files: `lean/VE/Calc/{Interval,Consistency}.lean`, `tests/test_calc_consistency.py`.
- Proves 3.7 and `signFlipP_grain`'s use as a granularity check.
- Fixtures: V-7 (granularity), V-8 (tie rule), V-6 from the printed per-template values (a witness: the printed values
  themselves), and an inconsistent synthetic table (a mean of five integer scores printed as 3.47, impossible since
  5 × 3.47 = 17.35 has no integer within rounding: GRIM).
- Seeded bug (Lean): the enclosure of `sub` uses [lo − lo, hi − hi]; the consistent fixture V-6 is refuted and fails.
- Bytes: 0.

### ME-9. Algebraic identities (Lean, 5-6 h)

- New files: `lean/VE/Calc/Poly.lean`, `tests/test_calc_algebra.py`.
- Proves 3.8.
- Fixtures: H-1, H-2, H-3, H-4 with D free; the false "(a + b)² = a² + b²" not shown, with the point a = b = 1; a division by an
  expression that can be zero denotes nothing at that point.
- Seeded bug (Lean): monomials with different variable lists are merged; "(a + b)² = a² + b²" is reported an identity
  and its regression fails.
- Bytes: 0.

### ME-10. Calculation content in documents (Lean and Python, 5-6 h)

- New files: `lean/VE/Calc/Document.lean`, `tests/test_calc_document.py`.
- `calculation` content in `ve-document@1` goes through Lean's `document` mode; the `calc:` leaf label (2.12); statuses
  and findings; coverage counts `support: calculation` units as checked only with a Lean verdict.
- Hand-written shared: the `document` mode's content dispatch (`lean/VE/Service/Document.lean`, one branch; after
  `lean-first/b16g` or its successor adds a content hook, rebased onto it), `lean/VE/ClaimGraph.lean` is **not**
  edited: the label is a string the existing `Claim.label` carries; `ve/document.py` only if the hook is not yet in
  Lean (one dispatch line).
- Seeded bugs: Lean, a `calc:` leaf accepted when its claim fails (the document test fails); Python, the relay drops a
  finding from the display (the binding test fails).
- Bytes: 0 new (companions become document units).

### ME-11. English in Lean's engine (Lean, 5-6 h; after english-lean E3's quantities step, quantities' QT-E)

- Rules for the wordings of 2.11 in Lean's English engine, whole-sentence derivation uniqueness, parse-back of every
  rendered line to the same canonical case, refusals with rewrites in Lean's diagnostic table (the nested-phrase
  refusal, "about", "approximately", "roughly", "nearly", "on par", every symbol).
- Hand-written shared: `lean/VE/EnglishGrammar/*` (additive rules; act-phrases, attitudes and quantities add rules to
  the same files, rebased in turn). Generated: `lean/VE/EnglishGrammar/Fixed/*.lean`, `ve/english_grammar/LOCK.json`
  (a person's `--actions-version`), `ve/english_grammar/codes.json`.
- Fixtures: every wording of 2.11 round-trips; the two refused sentences give their rewrites; "standard deviation"
  alone is refused in authoring.
- Seeded bug (Lean): "the difference between A and B" built as B minus A; the round-trip fixture fails.
- Bytes: 0 (readability).

### ME-P3. Pilot: physics complete, VE paper statistics, deep learning (pilot runner, 3-4 h)

Physics H-1 to H-3 and the theory section; VE paper V-6 to V-8 and the appendix tables' rows (consistency and
recomputation); the DL target's tables, comparisons and parameter counts if ME-0 pinned one. Estimated: H +1.5-2.5 KB,
V +10-16 KB (most of it appendix table rows), DL +5-8 KB.

### ME-12. Lean core of `arith@0` (Lean, 5-6 h; independent of ME-1 to ME-11)

- New files: `lean/VE/Arith/{Syntax,Holds,Defs,Bounded,Examples,Wire,Run,Render}.lean`,
  `lean/ResponseShape/Schemas/Arith.lean`, `lean/ResponseShape/Encoders/Arith.lean`, `lean/ARITH.md`, `ve/arith.py`,
  `tests/test_arith_lean.py`, `tests/test_arith_answer.py`.
- Proves 3.9's meaning and bounded-evaluation theorems; mode `arith`.
- Hand-written shared: as ME-2 and ME-3 (`Protocol.lean`, `service_schema.py`, `Dispatch.lean`, `ve/profiles.py`,
  `ve/__main__.py`, `tools/layer_policy.py`, the assurance manifest, ROADMAP). Generated: as ME-2 and ME-3.
- Fixtures: M-1, M-2, M-4, M-5; a definition that calls itself refused; an unbounded statement reported "stated, not
  decided".
- Seeded bugs: Lean, a bounded quantifier from lo to hi ranges up to hi + 1 (M-5 fails); Python, the relay accepts a
  row for a statement it did not send (the binding fuzz test fails).
- Bytes: 0.

### EX-1. Experiment: Mathlib proofs of VE's own statements (planner and Lean, 4-6 h)

- **Pre-registered bar** (all must hold): (1) VE generates the statements and identities of Bertrand's postulate
  (whole-number reading, M-3), "there is no largest prime", and "every prime greater than 2 is odd"; (2) a new Lake
  project `imports/mathlib/` at the toolchain `leanprover/lean4:v4.24.0` and the Mathlib revision built for it proves
  `Defs.Means` of each; (3) `#print axioms` of each is within `propext`, `Classical.choice`, `Quot.sound`; (4) on the
  VM, a clean build takes at most 3 hours with Mathlib's prebuilt cache or 6 hours without, and uses at most 15 GB of
  disk; (5) the bridge lemmas (VE's definitions against Mathlib's) total at most 150 lines; (6) a blind independent
  audit by the reviewer pair finds that the English rendering of M-3 states Ramanujan's theorem under the whole-number
  reading.
- Pass: build ME-13. Fail: record which item failed; mathematics stays at bounded evaluation; the M row's "after the
  plan" estimate drops to 6-12%.
- Files: `imports/mathlib/{lakefile.toml,lean-toolchain,VEImports/*.lean,README.md}`, `experiments/math-evidence-EX1/`
  (report and measurements). Shared files: none. No test in the suite builds Mathlib (hermetic tests).

### ME-13. Import records (Lean and Python, 4-5 h; only if EX-1 passes)

- New files: `lean/VE/Arith/Import.lean`, `tools/lean_import_check.py` (builds the import project, reads `#print axioms`,
  writes the record; not a test), `tests/test_arith_import.py` (record admission and labels only, hermetic).
- Proves `Import.admit_axioms` and `report_import_labelled`.
- Hand-written shared: none beyond ME-12's mode (a new case kind). Generated: as ME-2.
- Seeded bug (Lean): `admit` skips the axiom check; a record listing an extra axiom is admitted and its test fails.
- Bytes: 0.

### ME-P4. Pilot: mathematics (pilot runner, 2-3 h)

M-1 to M-4 in the Ramanujan ledger; the main theorem by import if ME-13 landed. Estimated: M +0.5-1.0 KB.

### EX-2. Experiment: approximations with error bounds (Lean, 5-6 h)

Square roots by squared bounds in derivations (for example "the square root of 1 + y is at most 1 + y/2 for y ≥ 0",
by squaring and the nonnegativity of (y/2)²), sums-of-squares certificates checked by ME-9's normaliser (Harrison 2007),
and exact remainders. **Bar**: certify, with Lean-checked certificates each replayed in under one second, (a) H-2's
remainder bound for |v/V| ≤ 10⁻³, (b) the transverse path "2D√(1 + v²/V²) differs from 2D(1 + v²/(2V²)) by at most
D(v/V)⁴/4", and (c) the Einstein alternate's "1/√(1 − β²) − 1 − β²/2 is between 0 and β⁴ for 0 ≤ β² ≤ 1/2". Pass:
plan an `approximation` batch. Fail: these sentences stay residual with the reason named.

### EX-3. Experiment: tensor shapes (Lean, 4-5 h)

Shapes as a second dimension-like type (rows by columns) for products, transposes and sums of declared matrices.
**Bar**: on the pinned DL text, at least 80% of its method equations with matrix operands receive a shape, and a
planted shape error in each is reported. Pass: plan a shapes batch beside ME-6. Fail: method equations stay definitions
with prose types.

### EX-4. Trigger: folds and induction in `arith@0`

Trigger: a pinned text needs a product over an unknown list (Euclid's N) or an induction VE must check itself (the
Dedekind alternate). Until then, imports cover unbounded proofs.

### EX-5. Experiment: large data through the service (Lean and Python, 3-4 h)

Chunked data handles (each chunk at most 8 MB with its own digest; the whole by its digest). **Bar**: the
20,975,471-byte E1 trial file (`experiments/E1/runs/e1-scored-0921/trials.jsonl`) registered and verified by Lean, the
20 counts of V-5 recounted from it in at most 60 seconds on the VM, and equal to the printed counts (or each difference
listed as a finding). Pass: V's counts bind to raw trials. Fail: they stay bound to the committed count table.

## 6. In-flight work, dependencies and merge conflicts

| Batch | Waits for (branch where known) | Hand-written shared files | Generated (regenerate) |
|---|---|---|---|
| ME-0 | — | `usecases/` new directories only | — |
| ME-S | plan converged; cross-plan review for D6 and D12 | `docs/spec/math-evidence.md` (new) | — |
| ME-1 | ME-S PASS; quantities QT-A2 (`design/quantities`) if it lands first, for the rounding module | none | `lean/VE.lean`, `lean/VE/Audit.lean` (union merges), frozen inventory, axioms, statements, predicates, declarations, trust tables |
| ME-2 | ME-1; `fix/main-relay` (main is red since ts-B1); `lean-first/b14d`, `question-answering/q2` and quantities' QT-A3, each of which edits `Protocol.lean` and `service_schema.py`: merged or rebased onto | `lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py`, `lean/VE/Compose/Dispatch.lean`, `lean/VE/Compose/Examples.lean`, `ve/profiles.py`, `ve/assurance-manifest.json`, `ROADMAP.md` | response schemas, `lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`, checker pins, assurance doc, route cases, gate collection |
| ME-3 | ME-2; `mig3/py` if it touches `ve/backends/relay.py` | `ve/__main__.py`, `tools/layer_policy.py`, `tests/data/route-cases.jsonl` | `.importlinter`, gate collection |
| ME-P1 | ME-3 | pilot directories | — |
| ME-4 | ME-2 | `lean/VE/Service/Protocol.lean` (`Handles`, additive) | as ME-2 |
| ME-5 | ME-1 | none | as ME-1 |
| ME-6 | ME-1; the cross-plan review's decision on `ve-units@2`; quantities QT-A7 if it lands first | the W6a unit decoder's version switch (`lean/VE/Time/Wire.lean`) only if `ve-units@2` is decoded there | as ME-1 |
| ME-P2 | ME-4, ME-5, ME-6 | pilot directories | — |
| ME-7, ME-8, ME-9 | ME-1 (ME-8 also ME-7 for granularity) | none | as ME-1 |
| ME-10 | ME-2; `lean-first/b16g` (or the batch after `b16e` that gives the `document` mode a content hook) | `lean/VE/Service/Document.lean` (one branch), else one line in `ve/document.py` | as ME-2 |
| ME-11 | english-lean E3's quantities step (quantities' QT-E; no branch yet); the english-lean E2 flip | `lean/VE/EnglishGrammar/*` (shared with act-phrases, attitudes, quantities; additive) | English `Fixed/*.lean`, `LOCK.json` (a person's `--actions-version`), English codes |
| ME-P3 | ME-7 to ME-9 (ME-10, ME-11 for display) | pilot directories | — |
| ME-12 | ME-S PASS | as ME-2 and ME-3 | as ME-2 and ME-3 |
| EX-1 | ME-12 | `imports/` (new), `experiments/math-evidence-EX1/` (new) | — |
| ME-13 | EX-1 PASS | none | as ME-2 |
| ME-P4 | ME-12 (ME-13 if built) | pilot directories | — |
| EX-2, EX-3 | ME-9 (EX-3: ME-6 and a pinned DL text) | new experiment directories | as ME-1 if Lean is added |
| EX-5 | ME-4 | `lean/VE/Service/Protocol.lean` (`Handles`) | as ME-2 |

How conflicts are avoided: all Lean is in new directories (`lean/VE/Calc/`, `lean/VE/Arith/`) and new response-shape
files; all Python in new modules (`ve/calc.py`, `ve/arith.py`) and new test files; the import project and the pilots in
new top-level and `usecases/` directories. The hand-written shared files are `Protocol.lean` (additive lines, after
its in-flight editors merge), `service_schema.py`, `Dispatch.lean` and its examples, `ve/profiles.py`,
`ve/__main__.py`, `tools/layer_policy.py`, the assurance manifest, `ROADMAP.md`, the `document` mode's dispatch and the
English grammar files. Two profile rows (`calc@0`, `arith@0`) in `Dispatch.lean` are added in separate batches, each
after rebasing. Generated inventories are never edited or merged by hand (`regen_generated.py --write`, then
`--resolve`). Before each batch, overlap is checked with `git diff --name-only main...<branch>` against the branches
above.

## 7. The measure

- **Denominators**: the pinned texts' bytes as `SOURCE.md` records them (ME-0); VE's paper sections by SHA-256 at the
  ME-0 commit (73,801 B at `49de179e`, measured with `wc -c`).
- **Statuses**: CHECKED when every claim of the unit's companion case or document content is decided by Lean (holds,
  or fails with a finding); OPEN when a claim is unknown; UNFORMALISED with a reason otherwise; LABELLED for exposition
  and meta; MIXED units split into parts as W2 specifies. A unit whose numbers are checked but whose hedge or causal
  framing is not is MIXED, never wholly CHECKED.
- **Reported each pilot run**: bytes and units by status and kind; findings (source arithmetic that fails); the
  residual (stated values by support, data digests, assumptions, imports); and the NORTH-STAR rows M, H, DL, V
  refreshed. The constitution and UDHR runs are not touched by these batches.

### Expected effect per batch (all **estimates** until a pilot run measures them)

| Batch | Constitution | UDHR | Physics | VE paper | Deep learning | Mathematics |
|---|---|---|---|---|---|---|
| ME-0 | 0 | 0 | measured; 1.5-2.5 KB checked | measured; 0.3-0.8 KB | measured if pinned; 2-4 KB | measured; 0 |
| ME-P1 | 0 | 0 | +0.6-1.0 KB | +0.8-1.5 KB | — | — |
| ME-P2 | 0 | 0 | +3.0-4.5 KB | +1-2 KB | — | — |
| ME-P3 | 0 | 0 | +1.5-2.5 KB | +10-16 KB | +5-8.5 KB | — |
| ME-P4 | 0 | 0 | — | — | — | +0.5-1.0 KB |
| After the plan (research 6 and 7) | 0 | 0 | 20-31% | 16-28% | 14-25% | 10-20% (6-12% if EX-1 fails) |

## 8. Not claimed, risks, open questions

- **Not claimed**: any byte before a pilot run measures it; that any stated value, data file or imported proof is true
  beyond what is checked; that a passing calculation makes a source's conclusion true; that readers follow worded
  equations (unmeasured; it needs human or proxy readers, which this plan does not call); any DL licence.
- **Risks**: the paper texts' sizes and sentence kinds are estimates from memory until ME-0; exact arithmetic on large
  powers or long tables may hit limits (UNKNOWN, never a wrong verdict; measured in `tools/bench`); the tie rule of
  printed tables varies by software (D6 makes it a declared convention or a reading set); Mathlib's build cost may fail
  EX-1's bar; english-lean E3 may be scheduled late, which delays input wordings (cases stay writable as JSON and
  display through Lean's rendered lines); physics dates before 1970 are outside W6's calendar (H-10), a question for
  events-time-causation.
- **Open for ME-S**: the exact names of the response-shape fit predicate and the runner's verdict reader; whether core
  has `Nat.choose`; Mathlib's name for Bertrand's postulate; whether `Handles` can take a data kind without changing
  its existing theorems.
- **Open for the cross-plan review**: the owner of the rounding module (D6) and of `ve-units@2` (D12); quantities' note
  that "the Lean tree depends on no library, so there is no ... rational type" (its plan 2.3) should be revisited,
  since `lean/Iceberg.lean` uses core `Rat` with `import Std` at the pinned toolchain.

## 9. Review checklist (ME-S)

- `Denotes`, `Claim.Holds`, `RoundsTo`, `SqrtRoundsTo`, `Agg.run`'s specification and `Arith.Holds` state meanings
  without reference to the executable functions they are proved against.
- `RoundsTo` keeps the written places; the tie rule is explicit and agrees with quantities' `roundHalfUp` (or the
  shared module); `roundsTo_unique` holds.
- `compare_invariant` has no hypothesis beyond equal physical dimensions, normal forms and positive factors.
- `Farkas.check_sound` and `Derivation.check_sound` quantify over every rational assignment; linear infeasibility over
  ℚ with rational coefficients is infeasibility over the reals, so the soundness also holds for real-valued quantities
  (stated in `lean/CALC.md`, not as a theorem).
- The statistics definitions match `paper/analysis/README.md`'s stated procedures (sample variance, exact sign flips
  with the observed vector counted).
- `decideBounded_sound` is an equivalence; bounded quantifiers range exactly from lo through hi.
- Import admission checks identity and axioms; every unbounded `arith` conclusion carries a bounded decision or an
  import leaf.
- No symbol appears in any wording or diagnostic; every refusal names a rewrite.
- Every new trusted line has a signed allowance and a ROADMAP trust-cost line.

## 10. Shared pieces

Abstractions this plan thinks several of the seven research-wave designs could share. The cross-plan review may move
any of them.

| # | Shared piece | Who would use it | Proposal |
|---|---|---|---|
| 1 | **Exact numbers**: one exact value function for written decimals (`VE.Time.Dec` → `Rat`), written places kept, the scientific form | quantities (`cardinality@0`), math-evidence, risk (estimates), events (durations) | one lemma file beside `VE.Time.Decimal`; core `Rat` via `import Std` (contrary to quantities' plan 2.3, a rational type exists without Mathlib) |
| 2 | **One rounding definition with an explicit tie rule** (ties up by default; half to even declared; bounds rounded down or up) | quantities QT-A2 (`roundHalfUp` over integer ratios), math-evidence ME-1 (any exact value) | one module (`VE.Numbers.Round` or `VE.Calc.Round`), the integer-ratio form proved equal to it (`roundsTo_ratio_agree`); an undeclared tie in a translated source is a reading set |
| 3 | **One unit registry `ve-units@2`**: W6 tags, quantities' declared conversions, physical dimensions and factors | quantities QT-A7, math-evidence ME-6, events (days, weeks) | one schema; a conversion between two units of one physical dimension is the ratio of their factors; "physical dimension" in prose so that quantities' comparison "dimension" keeps its name |
| 4 | **Pinned inputs by digest**: the service's handle table for environments and data, W5's adapter records, risk's hash-chained log, import records, VEX's evidence snapshots | math-evidence (data, imports), weighing and risk (records), events (dated evidence), attribution (quoted sources) | one handle table and one record shape: inputs by digest, parameters, a Lean-recomputed output or an external-support label |
| 5 | **A residual line for external support**: stated values with a support kind, data digests, procedure assumptions, imports, adapter outputs | math-evidence, events (causal links' support), weighing (decisions), attitudes (attributed beliefs) | one line format and one place in the report, as events' piece "named open relations with a decider and support" |
| 6 | **Approximation words** ("about", "approximately", "roughly", "nearly", "on the order of") | quantities (refuses "about"), math-evidence, events ("around noon") | one catalogue entry: refused in authoring with the rounding or range rewrite; in translation a reading set {rounded to the written digits, an open tolerance with a decider} |
| 7 | **Hedged quantitative claims** ("probably less than one sixth") | attitudes (likelihood words), math-evidence (the bound and its derivation) | the hedge wraps a calc claim unit; attitudes owns the word, math-evidence the bound; neither copies the other |
| 8 | **Procedures and dated sessions** ("observations at noon on July 8, 9, 11 and 12, 1887") | events-time-causation, math-evidence | events owns events and the calendar; dates before 1970 (W6's lower limit) need a decision there |
| 9 | **Arithmetic noun phrases and number words in Lean's English engine** | quantities, math-evidence, act-phrases, attitudes, scope | one lexicon of number words and arithmetic phrases, additive rules, one owner per wording |
| 10 | **Readings distinguished by a number** ("SD" with divisor n or n − 1; "x" a whole number or a real; "a/2b"; an undeclared tie rule) | math-evidence, quantities ("16 of the 18": exactly or at least), scope | reading sets whose distinguishing situation is an exact value computed by `calc@0`, a service to any design with numeric readings |
| 11 | **Section-scoped declarations** (scope's piece: "all lengths in this section are in meters") | scope, quantities, math-evidence | calc cases read a section's declared units through scope's anchor reach once it exists |
| 12 | **Profile registration** in `VE.Compose.Dispatch`: every new profile edits its list and gate lemmas | all seven designs | a table-driven registry with one generic gate lemma, as a consolidation item, so new profiles stop editing proofs |
| 13 | **VE statements as Lean propositions** (`VE.Arith.Holds` as the target of imports) | math-evidence, question answering (citing proved facts), ROADMAP's "Lean statement layer for mathematics" | one meaning function per profile that an external Lean project can import and prove, with one import-record format |

## Change log

- Draft 1 (2026-10-13): first plan, from the research note of 2026-10-12; aligned with quantities' plan draft 1
  (rounding, units, the "X out of Y" wording, the word "dimension").
