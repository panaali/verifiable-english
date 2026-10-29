# JT-E3 preregistration — 2026-10-29

This file and `SAMPLE.tsv` are committed before either rater is called. The frame is
`research/judgment-terms-p1` (`64339b6ce`),
`research/judgment-terms/open_term_class.tsv`: 91 rows, 89 distinct terms.
The two superseded UDHR placeholders `greatest_importance` and
`natural_group_unit` are excluded in favour of their JT-0p names
`of_greatest_importance_for` and
`natural_and_fundamental_group_unit_of_society`. Each other pilot/term pair is
one sampling unit.

## Sample, fixed before ratings

Seed: `20261029`, Python `random.Random`. Stratify by `(pilot, class)` in the
frame. For each stratum, allocate `floor(60 * stratum_size / 89)` places, then
allocate remaining places by descending fractional remainder, with lexical
`(pilot, class)` ties. Include all five required constitution terms first within
their stratum: `ethical_harm`, `broad_safety`, `genuine_helpfulness`,
`appropriate_oversight`, `good_judgment`. For each stratum, sample the remaining
places with `rng.sample` from frame order, visiting strata in lexical order.
`SAMPLE.tsv` fixes the resulting 60 pilot/term pairs and their sampling strata
(SHA-256 `2e5e2987484ea74d84dd9b379889c8d79dcac8d9346e1879ebf71a283313617f`).
Its `stratum_class` is for the sampling audit only and is never sent to a rater.

| Stratum | Frame | Sample |
|---|---:|---:|
| constitution/attitude | 1 | 1 |
| constitution/classification | 13 | 9 |
| constitution/exception | 4 | 3 |
| constitution/judgment | 18 | 12 |
| constitution/proportion | 1 | 1 |
| udhr/attitude | 1 | 1 |
| udhr/classification | 18 | 12 |
| udhr/judgment | 32 | 21 |
| udhr/proportion | 1 | 0 |

## Blind rater prompt

Each rater receives the following fixed instructions and records containing
`id`, `pilot`, `term`, and one source sentence. The existing `class`,
`borderline`, `reason`, other rater's answers, and sampling stratum are hidden.
The sentence is drawn from the pinned pilot source text containing or
illustrating the term. `INPUT.json` freezes all 60 sentences before calls
(SHA-256 `4a4a16073c9d4d3f548aabfda270186276b2350c26bc83ffdb7a953503050ddf`).
The constitution source SHA-256 is
`fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd`;
the UDHR source SHA-256 is
`d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a`.

> Classify each record independently into exactly one of `judgment`,
> `classification`, `exception`, `attitude`, or `proportion`. Return only a JSON
> array of objects with `id` and `class`, in input order. Use the rule below.
>
> **What counts as a judgment term.** A word or phrase whose application to a fully described case still needs an
> evaluative or threshold judgment against a standard the text does not state, so that two informed people who agree
> on every fact can still disagree. Not judgment terms:
> - classification words the text leaves undefined but that facts settle ("persona", "slavery", "member of society");
> - exception placeholders ("exception_to_…");
> - attitudes ("knowingly", "thinks it quite likely"), which are attitudes';
> - proportion words ("vast majority"), which are quantities'.
>
> Graded judgment words ("serious", "significant") are judgment terms whose order is quantities'.
>
> Apply these class rules in order: a mental-state term is `attitude`; an
> exception placeholder is `exception`; a share of a collection is
> `proportion`; an evaluative or threshold term is `judgment`; otherwise use
> `classification`. For a term mixing classification and judgment, use
> `judgment`. Do not infer labels from the identifier alone when the sentence
> supplies the meaning.

Two different models rate all 60 terms independently: one Claude via the
account picker and one Codex only if `codex-allowed.sh` allows it. Use
subscription CLIs, no API key or paid credits. Batch to at most 10 total rater
calls and 1M CW; stop on either cap. The runner checks one complete, typed,
unique answer per id and records raw outputs. No cross-rater discussion or
repair of a class is permitted.

## Analysis fixed before ratings

Use the two fresh raters as the two kappa columns; the frame's original class
is not one of the raters. For all 60, compute the five-by-five confusion table,
observed agreement `Po = diagonal / 60`, expected agreement
`Pe = sum(row_total * column_total) / 60²`, and Cohen's
`kappa = (Po - Pe) / (1 - Pe)`. The bar is verbatim: **Cohen's κ at least 0.7.**
`PASS` iff kappa is at least 0.7. On a fail, **the instrument reports only
"open term", and judgment-term counts are not published as measured.**

Report each pilot's original instrument judgment-term units and bytes, then
recompute them excluding all units whose judgment-term membership depends
solely on a term the two raters disagree on; give counts with and without
the frame's `borderline` flag as a second axis. Only sampled disagreement can
be identified by this experiment; unsampled terms retain the frame's original
class and this limitation is explicit in the results.
