# Attitudes, phase 1: AT-0p, E1, E2 (pilots and pre-registered experiments)

> **Status.** Pre-registration, 2026-10-13, branch `research/attitudes-p1` at `2c3cdf2f` (plan draft 4, spec draft 3;
> base `49de179e`, `ve-green-ts-B1`). Phase 1 of the cross-plan synthesis (`manage-agents/debates/plan-synthesis/
> SYNTHESIS.md` 4.1: "Now, no product code. Pilots: … AT-0p … Experiments: E1, E2 …, each under its own gates").
> This section is written and committed **before** any item is run; the bars below are quoted verbatim from
> [docs/spec/attitudes-PLAN.md](../spec/attitudes-PLAN.md) (draft 4) and are not moved after the data. No product
> code (`ve/`, `lean/VE/`, `rust/`, `tools/`) is changed. No model calls. Scripts: `research/attitudes/`;
> evidence: `docs/research/evidence/attitudes/`. Pilot inputs are read, never written:
> `manage-agents/pilots/claude-constitution/run-20261012T1800Z` (the run R 2 measured).

## 1. Pre-registered bars (quoted before running)

### 1.1 AT-0p (PLAN section 4, "AT-0p. Pilot repair with the existing language")

The rewrite, quoted:

> In the constitution pilot, for each hard constraint i (seven categories `C_i`, the existing case atoms), replace
> the guard `C_i(s) ∧ restricted_action_knowing_or_quite_likely(s)` by
> `( C_i(s) ∧ knowingly_engages_<i>(c, s) ) ∨ thinks_quite_likely_<i>(c, s)`
> with fourteen binary open terms on (`claude_instance`, `situation`) […]. Delete
> `restricted_action_knowing_or_quite_likely`.

The bar, quoted:

> - **Probe points to add** (four per rule, `probes/unspecified-probe.json`): case false and thinks-quite-likely true
>   (expected SETTLED no, the audit's case); case true and knowingly true (SETTLED no); neither (UNDECIDED); case
>   false and knowingly true (UNDECIDED: an impossible situation the untyped language cannot refuse).
> - **Expected numbers (estimates until measured):** claimed bytes unchanged (2,951); the 7 units (874 B) become
>   candidates for audit verification; open terms 33 → 46; the seven audit-case points UNDECIDED → SETTLED no.

Operationalised before running (no bar is changed; these only say how each quoted item is measured):

| # | Quoted item | Measured as | PASS iff |
|---|---|---|---|
| A1 | case false and thinks-quite-likely true: SETTLED no | the run's own probe method (`probe_unspecified.py`'s point: Lean `norm-defaults-status`, one-element situation) on the AT-0p strict companion, all 7 rules | all 7 are `SETTLED no` |
| A2 | case true and knowingly true: SETTLED no | same | all 7 are `SETTLED no` |
| A3 | neither: UNDECIDED | same, at two points: case true, and case false (both attitude atoms false) | all 14 are `UNDECIDED` |
| A4 | case false and knowingly true: UNDECIDED | same | all 7 are `UNDECIDED` |
| A5 | the seven audit-case points UNDECIDED → SETTLED no | baseline: the recorded point "the case does not hold (the knowledge atom does)" of run 20261012T1800Z, reproduced here; after: A1 | baseline 7 × `UNDECIDED` reproduced, and A1 holds |
| A6 | claimed bytes unchanged (2,951) | `ve document coverage` on the rebuilt main translation: `bytes_by_status`, against the run's recorded `coverage.json` | `bytes_by_status` identical (so CHECKED + OPEN, which the run's `finish` asserts equal its claimed CHECKED + OPEN + READINGS, is unchanged) |
| A7 | open terms 33 → 46 | `len(open_terms)` in the rebuilt main translation (`translation.ve.md`), the count `metrics.json` reports | 46 |
| A8 | the 7 units (874 B) become candidates for audit verification | the next audit's verdict | not measurable without an audit: **DEFERRED** (needs the pilot audit, outside this phase) |

Also checked (regressions, not bars): the rebuilt main translation and the strict companion are admitted by
`ve document check` with the run's own assertions (premises `model`, reading plan `enumerate` with 8 choices,
readings CONFLICT-FREE, coverage 100 %); every probe point not about the seven rules gives the status the run
recorded.

### 1.2 E1 (PLAN section 4, "E1. Likelihood words: order and lower bounds")

Quoted:

> Pre-registered. Readers: Sonnet 5.5 as human proxy (`claude-sonnet-5-5`), 40 independent sessions with no shared
> context, items in a seeded random order (seed `attitudes-E1`). Words: almost certain, very likely, quite likely,
> likely, more likely than not, as likely as not, unlikely, very unlikely (8 words, 28 pairs), each pair as two
> sentences "Claude thinks it *a* that the file is safe" / "… *b* …", question: "If the first sentence is true, must the
> second be true?" (yes / no / cannot tell). Plus 8 items "If Claude is certain that the file is safe, does Claude
> think it *w* that the file is safe?".
>
> - **A pair enters the scale table** (`table.above`, with its item) iff at least 36 of 40 answer yes and at most 2
>   answer no.
> - **The lower-bound reading of a word** is confirmed iff at least 34 of 40 answer yes to its certainty item; the
>   word then enters `Scale.lowerBound` (with its item). A word that fails is refused by `attitudes@0` (A1), and no
>   pair names it.
> - Nothing else is concluded. This measures agreement among proxy readers, not truth and not human readers. Cost
>   **estimate**: 40 × 36 = 1,440 short calls, under the usage cap rules.

### 1.3 E2 (PLAN section 4, "E2. Factivity and the knowing entailments")

Quoted:

> Same protocol. Items: three factivity items ("Claude knows that the file is safe. Must the file be safe?"); three
> "knows → believes"; one "knows → thinks it *w*" item per lower-bound word (A1); one item for each pair the closure
> of E1's pairs derives without a direct E1 item, and for each premise-3 word reached only through the closure
> (debate round 3); three negated-"know" items ("Claude does not know that the file is safe. Must the file be
> safe?", where the expected answer splits); three "unless X knows that P" items (for example, "… unless Claude knows
> that the user is an adult. The user is not an adult. Must Claude not share the file?"); three "P, and X does not
> know that P" items (A4).
>
> - Frame premise 1 ships iff all three factivity items reach 36 of 40. (If not, `knows` is not admitted at all.)
> - Frame premise 2 ships iff its three items reach 36 of 40. Premise 3 ships per word, iff that word's item reaches
>   36 of 40.
> - **Closure review**, then freezing. The frozen table records, for each admitted entry, the item that passed it. A
>   Lean `#guard` (`Table.reviewed`, evaluated through QS-1's closure) checks that the reflexive-transitive closure of
>   the frozen pairs adds no pair, and no premise-3 word, without its own passing item. If a derived entry's item
>   failed or is missing, the weaker word leaves `lowerBound`, or the scale pair is dropped, before freezing.
> - The negated-"know" items are expected to split (that is why D-A7 refuses the form); if instead 36 of 40 agree on
>   one reading, AT-0 records it and keeps the refusal anyway (one reading must not depend on a majority).
> - "P, and X does not know that P" is admitted only if its three items reach 36 of 40; otherwise it is refused, with
>   its rewrites. The "unless" items are evidence only: the form stays refused whatever they show, and a later
>   admission needs its own statement review (debate round 3).

### 1.4 What this phase can run

The task forbids model calls. E1 and E2 are defined by their readers ("Sonnet 5.5 as human proxy … 40 independent
sessions"), so neither can be run here; they are **DEFERRED** (section 4), and the closure review with them,
because it needs E1's pairs and E2's items. What this phase does for them is everything that does not need a reader:
the item sets, the seeded orders, and the scoring scripts with the bars above written in, tested at the bars'
boundaries, so that the run, when authorised, is mechanical and cannot choose its bars after the data.
