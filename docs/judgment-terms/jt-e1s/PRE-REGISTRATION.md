# JT-E1s pre-registration (2026-10-31)

Status: frozen before any reader call. Main renderer pin: `4d9a0eeb0`. This is the plan's one wording revision after JT-E1r's FAIL (section 6, JT-E1 "Then"), rerun on a fresh frame. It is proxy readability from Sonnet 5.5, not human comprehension; a human reader audit remains a separate acceptance item.

## The one revision, and why

**Failure being addressed.** JT-E1r ([`RESULTS.md`](../jt-e1r/RESULTS.md)) scored 20/40 in both arms. All 20 missed rows had a `turns` key and were read as `CONDITIONAL`. Its RESULTS infer the cause: section 2.4's declaration row says only that something is a judgment and who decides it. It never says whether the conclusion is settled, left to someone, or holds only given a criterion. Those are 2.4's zone and conflict rows, which JT-E1r did not render. One atom can be settled for one conclusion and turn for another (JT-E1r's U01 and U02 share one), so no rewording of a per-term declaration can carry the class.

**What changes.** In the English arm, JT-E1r's declaration line stays word for word. Below it, the generator adds section 2.4's answer row for the named conclusion, using 2.4's texts:

- settled: `Settled: whatever is judged here, the text requires that <conclusion>.`
- turns: `Left to <decider>: these two admissible completions give different answers and differ on whether <atom> (a judgment for <decider>).`
- conditional: `These rules conflict where <atom>.`, then `Conflict-free, given these sentences: <criterion sentence>`. Section 2.4 shows the "given" line beside the line without the criterion, never instead of it.

Nothing else changes. The prompt, the shared lines, the control, the fallback, the scoring, the caps and the bars are JT-E1r's. [`render.py`](render.py) and [`runner.py`](runner.py) load JT-E1r's frozen generator and runner and replace only `english()`. The new `english()` is `declaration()`, which is JT-E1r's line, followed by `answer()`.

**How it addresses the failure.** The reader now sees 2.4's own statement of whether the conclusion is settled, left to a decider, or certified only given a criterion. This was JT-E1's original design: section 6 compares "today's rendering" with "2.4's English", and 2.4's English includes these rows. JT-E1r measured the declaration row alone.

**What this can and cannot show.** The answer row displays the frozen answer as the checker would state it. In the product, Lean computes that answer (WG-7, extended in JT-4). So a PASS shows that readers read 2.4's answer wording correctly: the class, the decider, and no dependent answer read as settled. It does not show that the declaration line lets a reader infer the class; JT-E1r already showed that it does not. The control has no answer row because main's renderer has none today.

## Frame

[`items.tsv`](items.tsv) has 40 new rows: 20 inspired by the UDHR (U01–U20) and 20 by Claude's constitution (C01–C20). These are synthetic probes about judgments in those sources, not claims that the sources contain these sentences. No source sentence or predicate is reused from JT-E1 or JT-E1r. The composition is JT-E1r's, row for row. Each source has five predicates of four rows each, in the pattern turns (named decider), settled (`unstated`), conditional (the same named decider), turns (a second named decider). So each source has 10 turns, 5 settled and 5 conditional rows. The fifth predicate in each source is the fallback group:

- U17–U20 have no template (`absent`);
- C17–C20 have the template `{0} is every`, which the actual lint rejects with `LOGICAL_WORD`.

Both arms of those eight rows show identical identifier bytes. They are reported separately and give no evidence of a wording advantage. Every `turns` row names its decider, because 2.4 has no `Left to` head for an unstated decider. Every conditional row adds a `criterion` column, and its sentence appears verbatim in the row's source. The frame freezes the source, conclusion, answer key, bound predicate and atom, decider, candidate template, actual lint result and criterion. The key is withheld from readers.

The control is the byte-for-byte stdout of `python -m ve render --view ve_english` at the pin, for each saved `.ve` statement and environment. The environment omits the template, so main produces its identifier fallback. `render.audit()` recomputes the lint, both displays, the shared information, the fallback identity and the criterion placement before calls. The saved displays are under [`captures/`](captures/).

**Arithmetic, stated before calls.** Bar (a) needs at least 36 of 40 English rows fully correct. The eight fallback rows are identical in both arms, and JT-E1r's eight scored 4/8. If that rate repeats, the English arm needs all 32 template rows correct.

**Verbatim reader prompt (JT-E1r's, unchanged):**

> Read only the source and displayed lines below as a reader of this document. For the named conclusion, answer in exactly this format: `CLASS: SETTLED|TURNS|CONDITIONAL; DECIDER: <name or NONE>; WHY: <one sentence>`. SETTLED means it holds whatever is judged. TURNS means two admissible judgments can change it. CONDITIONAL means it is certified only given a judgment criterion. Name the decider if the text names one; otherwise say NONE. Do not use outside knowledge.

The runner appends the shared lines and one captured display. Each row gets one independent, blinded call in each arm. `CLASS` and `DECIDER` are scored against the frozen key, and `WHY` is retained. A `turns` or `conditional` item read as settled or checked is critical. Missing or malformed answers are incorrect, and prose that declares a dependent conclusion settled or checked is critical. Class and decider must both be correct. For a settled key with no named decider, the expected decider is `NONE`. A failed call counts incorrect and not critical, and its answer is never scored (reviews/dri-decisions-20261030-jt-e1r.md item 2).

## Frozen bars (verbatim from JT-E1's pre-registration)

> (a) At least 90% correct with 2.4's English, and at least 15 points above the identifier arm.
>
> (b) No critical misreading in 40: an answer that turns on a judgment read as settled or checked.

Bar (a) requires at least 36 of 40 English responses fully correct and at least six more correct than control. Bar (b) applies to all 40 English responses. The caps are at most 100 Sonnet 5.5 calls and 3M reported CW, subscription only, with accounts from the picker and no paid fallback.

**Then.** On PASS, JT-3's conformance test compares its declaration lines with `declaration()` in this directory's `render.py` on every row of this `items.tsv`, and JT-4's zone and conflict rows follow `answer()`. On FAIL there is no second revision. The plan's fallback applies: identifier wording. The result goes to the DRI.
