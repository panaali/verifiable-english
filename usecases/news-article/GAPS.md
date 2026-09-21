# Gaps

Ranked by (frequency in this document) × (importance to the article's meaning).

## 1. Numbers and arithmetic — 7 occurrences, very high importance

**Smallest example:** "...raised the estimate of PCE inflation to 3.7%, up
from the 3.6% projected at the June 2026 meeting."

**Why v0 cannot express it faithfully.** This document's brief explicitly
notes that `docs/spec/v0.1-profiles.md` section B (`order@0`, linear integer
arithmetic) "is designed but NOT implemented" in the actual checker. So even
though v0.1's design chapter shows exactly how `3.7` and `3.6` and `<`/`add`
would work (`Num(z)`, `Lt(t,u)`, etc.), none of that is available to
`ve check` today. `claims.ve` #12 (`exceeds(@pce_sep, @pce_jun)`) works
around this by treating each specific reported figure as an opaque named
entity and manually asserting a ground `exceeds` fact for exactly the one
pair the article compares. That is honestly REIFIED, not DIRECT: the checker
can confirm the *asserted* direction of change, but the relation carries no
numeric content at all — nothing stops a model from setting
`exceeds(@pce_jun, @pce_sep)` too (both directions true at once, which real
`<` could never allow), and nothing lets a checker derive
`exceeds(@pce_sep, @unemployment_sep)` or any fact about a number not
already named as a constant. Two related sub-cases are outright NO because
even this workaround does not reach them: (a) the exact **magnitude** of a
change — "a quarter-percentage-point" (row 7b) — since there is no
representation of the old range at all, only the resulting range `r375_400`,
so there is nothing to subtract from; (b) an implicit, unstated comparandum —
"a year later than previously expected" (row 22b) — where the *previous*
projected year is never given a name in this excerpt, so there is no second
entity to compare against even under the opaque-tag trick.

**Proposed surface syntax:** exactly `order@0`'s design in
`docs/spec/v0.1-profiles.md` section B: built-in sort `$int`, terms `Num(z)`,
`Add(t,u)`, `Scale(z,t)`, and atoms `Lt(t,u)`/`Le(t,u)`, with `Eq` reused for
equality — e.g. `add(#36, #1) equals #37` or
`@pce_jun < @pce_sep` becoming a genuine numeric comparison once `pce_jun`
and `pce_sep` are declared as `$int`-sorted terms (in tenths of a percentage
point, to stay integral) rather than opaque `figure`-sorted constants.

**Semantics sketch:** already fully specified in `v0.1-profiles.md` section
B (standard ℤ interpretation, Presburger-arithmetic decision procedure for
the finite-presentation evaluator, LIA/SMT-backed tableau leaves for
entailment) — the gap is implementation, not design, per the brief's framing.

**Rendering across views:** already specified in `v0.1-profiles.md` section
B's table, e.g. `ve_fluent`: "I is less than (the sum of I2 and 3)".

**Frequency:** 7 of 26 coverage rows (7, 7b, 8-adjacent, 21, 22, 22b, 23) are
numeric claims; this is a wire economics story, so numbers are its
substance, not incidental detail.

## 2. Counting / cardinality quantifiers — 1 occurrence, high importance

**Smallest example:** "16 of the 18 FOMC policymakers expect at least one
more... increase..., with only 2 of the 18 expecting rates to stay."

**Why v0 cannot express it faithfully.** v0 has only ∀ and ∃; there is no
"exactly n of m" or "at least n" quantifier. Technically, for a small fixed
`n`, "at least 16 of the (fixed, enumerable) FOMC policymakers satisfy P" is
expressible in pure function-free FOL with equality via an Ackermann-style
encoding: `there exist p1, ..., p16 (all of sort policymaker), pairwise not
equal, each satisfying P, and for every other policymaker q satisfying P, q
equals one of p1...p16`. For n=16 this needs `16 choose 2 = 120` pairwise
inequality conjuncts plus 16 existentials — syntactically legal v0 but
absurd to author or read, and it still could not name the 16 individuals,
since the article never identifies them (fabricating 18 named FOMC voters
not in the source text would misrepresent it). So this is labelled NO, not a
forced encoding: per the brief's instruction, "never force a sentence into
VE by hiding its substance in an opaque predicate" — and an unreadable
Ackermann blow-up hides the substance just as much as an opaque predicate
would, without even the honesty of naming what it hides.

**Proposed surface syntax:** a counting-quantifier extension, e.g.
`there exist at least 16 policymaker x, (φ)` / `there exist exactly 16
policymaker x, (φ)`, parallel to `order@0`'s numeral literals but binding a
quantifier count rather than a term value.

**Semantics sketch:** `⟦AtLeast(n, s, φ)⟧(ρ) = |{d ∈ D_s : ⟦φ⟧(d::ρ)}| ≥ n`
— a straightforward finite-cardinality semantics requiring no fixed-point or
modal machinery, but it does need integer literals (natural overlap with
gap #1's `order@0`) and a finite-domain evaluator extension (counting matched
elements, which the existing finite Boolean evaluator could do directly by
extending its existing quantifier-enumeration loop with a counter).

**Rendering across views (sketch, `AtLeast(16, policymaker, φ)`):**

| View | Sketch |
|---|---|
| `fol_symbols` | `∃^{≥16} x:policymaker, (φ)` |
| `fol_keywords` | `at_least(16, policymaker, x, φ)` |
| `ve_strict` | `there exist at least 16 policymaker x, (φ)` |
| `ve_natural` | `there are at least 16 policymakers x such that (φ)` |
| `ve_fluent` | `at least 16 policymakers P are such that (verbalised φ)` |

**Frequency:** one occurrence in this article, but it is the sentence that
carries the article's main forward-looking policy signal (whether the Fed
will hike again), so its importance is disproportionate to its frequency.

## 3. Attribution and quotation ("X said/pledged/promised that...") — 3 occurrences, very high importance

**Smallest example:** "'Today's policy action will support a timelier
return to the Committee's 2% goal,' the central bank said in its policy
statement..."

**Why v0 cannot express it faithfully.** v0 terms and atoms cannot take a
*formula* as an argument — there is no quotation or propositional-content
term. `claims.ve` #9 (`stated(@fed, @statement_timelier)`) reifies the
*event* of attribution faithfully (an institution did, in fact, issue a
statement) but the constant `@statement_timelier` is an inert token: nothing
in the checked vocabulary says what the statement *claims*, so a model could
set `stated(@fed, @statement_timelier)` true while nothing else the article
reports about the Fed's intentions is derivable from it. This is exactly the
"attribution" gap the brief names, and it recurs for every direct quote in
hard news (here: the FOMC statement, row 15, and Warsh's pledge, row 24).

**Proposed surface syntax:** a `says`/`quotes` relation whose second
argument is a *formula*, not a term — e.g. `@fed says (A)` — breaking v0's
strict term/formula separation, or, more conservatively, a reified
"content" sort whose members are linked to formulas by a separate
`expresses(text, formula)` predicate declared per-document (letting the
checker treat `expresses` facts as additional premises rather than changing
the term grammar).

**Semantics sketch:** for the conservative route, no new formula constructor
is needed — `expresses(t, φ)` is just an ordinary binary-shaped extension
if `φ` is itself reified as a `formula`-sorted entity via a Gödel-style
quoting map from the document's own closed formulas to fresh constants (this
needs a term-to-entity encoding, which is a nontrivial but self-contained
addition, unlike full higher-order embedding). The unrestricted route
(`says(a, φ)` with `φ` a first-class argument) requires a genuine
higher-order or hybrid-logic semantics and its own soundness metatheory,
comparable in scope to gap #1 of the constitution-excerpt `GAPS.md`.

**Rendering across views:** `ve_strict`/`ve_natural`: `@fed says (A)`;
`ve_fluent`: `Fed says that (verbalised A)` (parallel to the constitution
excerpt's proposed `believes` rendering).

**Frequency:** 3 of 26 rows are direct attribution; every hard-news article
depends on attribution for essentially all of its authoritative content, so
this gap is central to the genre even when its raw count in one short
article is modest.

## 4. Hedged claims and reporter inference — 5 occurrences, moderate importance

**Smallest example:** "...a unanimous decision that effectively acknowledges
the Trump administration's inability so far to control inflation."

**Why v0 cannot express it faithfully.** Distinct from attribution (gap #3,
where the article reports *someone else's* claim), this is the reporter's
*own* inferential gloss, marked by hedges like "effectively," "is likely
to," and "a nod to" — Reuters is not asserting these as flat fact, but
signalling an inference with residual uncertainty. v0's material biconditional
gives no way to mark a claim as "the reporter's own confident-but-hedged
reading" versus a flatly asserted fact; both would have to be written as the
same unconditional atom, erasing a distinction the source text is careful to
preserve.

**Proposed surface syntax:** reuse the possibility/evidentiality operator
sketched in the constitution excerpt's `GAPS.md` gap #5
(`it is possible that (A)`), plus a source-tagged variant,
`@reuters infers (A)`, combining gaps #3 and #5 from that document.

**Semantics sketch / rendering:** as in the constitution excerpt's gap #3/#5
sketches (this is the same underlying construct, evidenced independently in
a second, unrelated document type — see the parent report).

**Frequency:** 5 of 26 rows (2, 4, 16, 17, 19).

## Note: a workaround that worked — reifying "before" and "after" as entities

Row 18 ("The new statement dropped a reference... present in the previous
statement") needed no new construct at all: reifying the FOMC's two
successive policy statements as two distinct named `text` entities
(`@prev_statement`, `@new_statement`) and asserting `attributes_to` for one
but not the other gave a clean, checkable REIFIED claim
(`claims.ve` #10) with no opacity. This is the standard "reify time-slices as
entities" technique for working around v0's lack of primitive tense — it
works well for one-off, explicitly-flagged before/after facts like this one,
but it does not scale to a document with continuous narrative tense (a
long article narrating a sequence of many events in order would need a fresh
named entity, and fresh ordering facts, for every distinguishable moment,
with no primitive "before" borrowed from the language itself — `before` as
an ordinary binary predicate is directly expressible, as noted in the
constitution excerpt's `GAPS.md` gap #5, but nothing forces its intended
irreflexive/transitive reading without being declared and asserted by hand
each time).

## Summary

| Gap | Occurrences (of 26 rows) | Importance |
|---|---:|---|
| 1. Numbers and arithmetic | 7 | Very high — the article's substance is economic statistics |
| 2. Counting / cardinality quantifiers | 1 | High — carries the article's main forward-looking signal |
| 3. Attribution and quotation | 3 | Very high — central to how hard news establishes any claim at all |
| 4. Hedged claims / reporter inference | 5 | Moderate |
| (causation, 1 occurrence; figurative language, 1 occurrence) | 2 | Low-moderate — see coverage.md rows 6 and 14 |

Not needed by this document in a way v0 cannot already handle: named
entities, dates-as-tags, and simple ground facts (v0's core strength, as the
one DIRECT and eleven REIFIED rows show); deontic modality and priority
ordering (the dominant gap in the companion `claude-constitution-excerpt`
document) barely appear here at all — this article reports what happened,
not what should happen, which is a genuinely different distribution of
missing constructs from a normative/constitutional text. See the parent
report for that cross-document comparison.
