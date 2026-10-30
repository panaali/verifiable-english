# JT-E1 pre-registration

Committed before the first reader call. Frozen frame: [`items.tsv`](items.tsv), 40 rows, U01–U20 and C01–C20. Each row has the source/context shown to the reader, one conclusion, its judgment atom and decider, the expected classification, and whether a usable judgment template is supplied. A `turns` key means the conclusion turns on the listed atom. A `settled` key means the conclusion holds whatever is judged. A `conditional` key means conflict freedom is certified only given the criterion; it is not unconditional. For `unstated`, the text names no decider. The answer key is never sent to the reader.

## Deviation fixed before any call

QT-B4 is not on main, so C07–C12 and C16–C20 use current main/pilot hard-constraint form and explicitly marked synthetic variants, rather than QT-B4's future representation. The named UDHR and constitution units are source anchors; synthetic variants are probes, not claims that the live pilots already contain those translations or answers. JT-4's zone lines do not yet exist on main, so the identifier arm uses the current renderer's identifier/fallback *wording* and the same answer shape rendered with identifiers. This is a proxy wording study, not a differential check of two live CLI routes.

## Two frozen arms for every row

The runner fills only the row fields in these fixed forms. Every row has exactly one independent reader call in each arm. The same source, conclusion, atom and answer key are used across arms. The reader sees the source and displayed lines, never this pre-registration or the key.

**Identifier arm (today's fallback wording):** `Open reading: "<subject>" is classified as "<predicate>".` This is the fallback pattern in the main English renderer (`ve/english.py`) and the plan's observed JT-0p rendering. The answer line is `left_to(<predicate>; decider=<decider>): <conclusion>` for `turns`, `settled: <conclusion>` for `settled`, or `conflict_free_given(<predicate>): <conclusion>` for `conditional`. The decider field is `unstated` when the source names none.

**English arm (plan 2.4):** `Whether <atom> is a judgment; the text does not say who makes it.` if the decider is unstated; otherwise `Whether <atom> is a judgment for <decider>.` The answer line is `Left to <decider>: these two admissible completions give different answers and differ on whether <atom> (a judgment for <decider>).` for `turns` with a decider, with `(the text does not say who makes it)` when unstated; `Settled: whatever is judged here, the text requires <conclusion>.` for `settled`; or `Conflict-free, given these sentences: <source>. <conclusion>.` for `conditional`. These are concrete fillings of plan 2.4, not an implemented JT-3 renderer.

**Verbatim reader prompt:**

> Read only the source and displayed lines below as a reader of this document. For the named conclusion, answer in exactly this format: `CLASS: SETTLED|TURNS|CONDITIONAL; DECIDER: <name or NONE>; WHY: <one sentence>`. SETTLED means it holds whatever is judged. TURNS means two admissible judgments can change it. CONDITIONAL means it is certified only given a judgment criterion. Name the decider if the text names one; otherwise say NONE. Do not use outside knowledge.

The runner appends `SOURCE: ...`, `CONCLUSION: ...`, then the arm's two display lines. `CLASS` and `DECIDER` are judged against the frozen key; `WHY` is retained for critical-misreading review. `turns` and `conditional` read as SETTLED or CHECKED are critical. A missing or malformed class is incorrect; if its prose asserts settled/checked despite a dependent key, it is critical. Incorrect decider is incorrect but not independently critical.

## Frozen bars, verbatim from plan section 6

> (a) At least 90% correct with 2.4's English, and at least 15 points above the identifier arm.
>
> (b) No critical misreading in 40: an answer that turns on a judgment read as settled or checked.

Score per arm is fully correct rows / 40, requiring both class and decider. Difference is English minus identifier in percentage points. Bar (a) requires at least 36/40 English correct and at least six more correct than the identifier arm. Bar (b) is checked on the 40 English answers. A model error, call failure or missing answer counts incorrect and is reported separately; it is not silently dropped.

## Frame and template count

U01–U20 cover u037, u045a, u046, u055, u064, u111, J-ι's court-order criterion and variants. C01–C20 cover u0052.s01, u0168.s01, current hard constraints and variants. The 40 exact rows and expected answers are in `items.tsv`; `template=no` identifies 20 constitution rows for which this synthetic frame supplies no template accepted by today's wording lint. They therefore have no validated template to fill. The count is **20/40**; this is a frame count, not a census of the pilot's declarations. An English line for those rows is an experimental filling and must not be treated as current JT-3 output.

## Limits and next step

One fresh Sonnet 5.5 CLI call per item and arm, 80 planned calls; no more than 100 calls or 3M CW for this item. The picker chooses the subscription account each time. No API key or paid-credit fallback is allowed. If either bar fails, propose one JT-3 wording revision without applying it. A rerun on fresh items is a separate `jt-e1b` item. Results are labelled proxy readability, not human comprehension.
