# fid-account-1: source accounting for the translated safety-framework cases (REPORT)

No DRI signature needed. No DELTA row: no `ve` command, verdict, diagnostic, schema or relay changed. The item adds a
stdlib tool, two sidecars, their saved reports and tests (nothing under `ve/`, `lean/` or `rust/`).

Prerequisite: `git log --oneline main | grep -i fidelity-fix` lists both merges. The RSP's (8ffec99188) was on main
at the start. Preparedness's (08f3c2af9b) merged during the build. I reviewed its translation at the fix branch's
tip (910a7d95a2), merged main (58c123285a), confirmed that main's `rules.d1.ve`, `facts.d1.ve`,
`environment.d1.json` and `PLAN.md` were byte-identical to the files I had reviewed (`cmp`), and then committed the
sidecar.

## Deliverables

| # | Deliverable | Where | Evidence |
|---|---|---|---|
| 1 | `usecases/safetyfw_accounting.py`, stdlib only | f607ecb84f | `tests/test_safetyfw_accounting.py` (40 tests) |
| 1a-e | quotes, span, words, accounted words, unaccounted words | `quotes`, `Source.anchor`, `words`, `legends`/`used_names`, `account` | `test_elided_quote_*`, `test_unanchored_quotes_are_problems`, `test_words_are_account_py_words`, `test_accounted_words_come_from_text_and_the_legends_it_uses` |
| 2 | sidecars, one line per block | `usecases/anthropic-rsp/accounting.d1.txt` (87), `usecases/openai-preparedness/accounting.d1.txt` (97) | `test_case_sidecar_passes_in_form[*]` |
| 3 | `--check`, `--report` | `main()` | `test_sidecar_form_problems`, `test_reason_arguments_resolve`, `test_a_missing_line_is_a_problem`, `test_report_totals_and_score` |
| 4 | `--score VERDICTS.md` | `score()` | `test_report_totals_and_score`; the re-audit does not exist yet (below) |
| 5 | both sidecars checked with `--source` on this VM, reports saved | `docs/usecases/safetyfw/<case>/accounting.json` | the two commands below, exit 0 |
| 6 | hermetic tests | `tests/test_safetyfw_accounting.py` | `uv run pytest -q tests/test_safetyfw_accounting.py`: 40 passed |
| 7 | this REPORT | here | |

The two runs (exit 0 each; output quoted):

    python3 usecases/safetyfw_accounting.py anthropic-rsp --source manage-agents/pilots/anthropic-rsp/source/rsp-3.4.txt --check --report docs/usecases/safetyfw/anthropic-rsp/accounting.json
    anthropic-rsp: 87 blocks, 226 unaccounted words in 51 blocks, 9 blocks with a loss {'1': 9, 'limit 4': 1, 'limit 9': 1}, 0 of 94 quotes unanchored
    python3 usecases/safetyfw_accounting.py openai-preparedness --source manage-agents/pilots/openai-preparedness/source/pf-v2.txt --check --report docs/usecases/safetyfw/openai-preparedness/accounting.json
    openai-preparedness: 97 blocks, 604 unaccounted words in 83 blocks, 17 blocks with a loss {'1': 23, '3': 1, 'limit 21': 1}, 0 of 113 quotes unanchored

The source hashes in the saved reports are the pinned ones: RSP `c7de7fe2…`, Preparedness `d2e3dd5b…` (README:
`d2e3dd5b80e5…`).

Acceptance: `git diff main --stat -- usecases/*/rules.d1.ve usecases/*/facts.d1.ve usecases/*/environment.d1.json
usecases/*/answer-key.json` prints nothing. No rule, legend, key or harness was edited.

## Per case

| | anthropic-rsp | openai-preparedness |
|---|---:|---:|
| blocks (rules + facts) | 87 (76 + 11) | 97 (86 + 11) |
| quotes anchored in the pinned source | 94 of 94 | 113 of 113 |
| unaccounted words before any sidecar | 226 in 51 blocks | 604 in 83 blocks |
| entries: restates | 54 | 99 |
| entries: exposition | 12 | 35 |
| entries: rule | 4 | 18 |
| entries: open | 5 | 0 |
| entries: reading | 7 | 30 |
| entries: loss | 11 (in 9 blocks) | 25 (in 17 blocks) |

These are the `totals` of the two saved `accounting.json` files.

### Losses and the fix I would make (the fix rows' work list; nothing here is edited)

anthropic-rsp:

| Block | Words of the source | Class | Fix I would make |
|---|---|---|---|
| rows-cond | "We will maintain or improve on our ASL-3 protections" | 1 | `plans_in_place`'s description quotes each row's plan; today it says only "the middle column's plans of the row of {1}" |
| rows-cond | "We will apply protections at least as strong as our ASL-3 protections (see previous row) to an expanded set of potential use cases" | 1 | the same |
| rows-cond | "We will detail the state of our AI systems' capabilities and propensities, our monitoring practices, and the overall level of risk in our Risk Reports" | 1 | the same (row T4's five bullets too) |
| f6-keep-past | "at that link" | 1 | `past_roadmaps_kept`'s description: "past Roadmaps kept available at the Roadmap's link" |
| f9-internal | "Within 30 days of" | limit 9 | D1 has no day count (D3 holds it). Put "within thirty days" in the act, as F16's act has it, or quote it in the legend |
| f11-analyses | "We will provide our reasoning and conclusions regarding both specific threat models and overall risk levels" | 1 | `risk_analysed`'s description quotes the sentence ("the four risk analyses of 3.3" names none) |
| f11-review | "and decisions" | 1 | `past_reviewed`'s description: "review of past Risk Reports and decisions" |
| f11-goal-missed | "Changes to our Frontier Safety Roadmap" | 1 | review item 3's first half: a sibling act or `goal_miss_addressed`'s legend covers the Roadmap's changes |
| f16-ask-commentary | "to memorialize its findings on the topics above in a written report that is made public" | limit 4 | `commentary_asked`'s description adds 3.6.3's sentence; a separate predicate once the 64-predicate limit allows (PLAN 12 item 4 calls this a restatement; it is narrower: a written report on the 3.6.3 topics) |
| f18-rso | "a designated member of staff who is responsible for the implementation of this policy" | 1 | `rso_maintained`'s description quotes the apposition |
| f19-unredacted | "final" | 1 | the act or legend says "final, unredacted Risk Reports" |

openai-preparedness:

| Block | Words of the source | Class | Fix I would make |
|---|---|---|---|
| f1-halt-strict | "we have specified safeguards and security controls that would meet a Critical standard" | 1 | `critical_standard_unspecified`: "OpenAI has not yet specified safeguards and security controls that would meet a Critical standard" (today: "the Critical standard has not yet been specified", a different condition) |
| f3-develop, f3-develop-forecast, f3-develop-inuse, f3-develop-inuse-forecast | "and should be treated with extreme caution" | 1 | an RS9 should-rule (strict and default) or the legend of `safeguards_during_development` |
| the same four | "Such models require additional safeguards" | 1 | `safeguards_during_development`: "additional safeguards (beyond the High safeguards)"; the act says "sufficient", from 4.2's reminder |
| f9-report | "We compile the information on the planned safeguards needed to minimize the risk of severe harm into" | 1 | `safeguards_report`'s description quotes it (today "4.1 and 4.2") |
| f9-residual-strict, f9-residual-default | "Identified ways a risk of severe harm can be realized for the given deployment, each mapped to the associated security controls and safeguards" | 1 | the report's other three items get acts, or the act's legend lists all four bullets |
| the same two | "Details about the efficacy of those safeguards" | 1 | the same |
| the same two | "Any notable limitations with the information provided" | 1 | the same |
| c3-access-strict, c3-access-default | "and may require additional approvals for access" | 1 | `access_limited`'s description adds it (a "may": probably harmless) |
| f16-ssc-visibility | "and can review decisions and otherwise require reports and information from OpenAI Leadership as necessary to fulfill the Board's oversight role" | 1 | a permission rule for the SSC, or the legend |
| f16-chair-strict, f16-chair-default | "we can request a fast track for the SAG to process the report urgently" | 1 | a permission rule over `fast_track_requested` (the predicate exists; no rule uses it) |
| f16-year | "the Preparedness Framework for continued sufficiency" | 1 | `annual_review`'s description names what is reviewed and why (today "Appendix B: at least once a year") |
| f11-within | "but only if" | 3 | `adjustment_permission`'s default is `allow`, so "may adjust if the conditions hold" leaves the adjustment allowed without them. Make the default `deny`, or add "must not have its required safeguards adjusted unless …" under RS5 = within |
| f13-results | "and evaluate whether there is sufficient evidence to recommend updates to our internal practices or to the Preparedness Framework" | 1 | a second act for the SAG's evaluation |
| fn5-indicator | "we will prioritize" | limit 21 | PLAN 12 item 21 keeps this duty UNFORMALISED; a rule if it should be checked |

## Score (deliverable 4)

There is no re-audit newer than the fidelity-fix merges yet: `ls -d manage-agents/debates/uc-audit-anthropic-rsp-2026111*` and
`…openai-preparedness-2026111*` list only the 20261110T2249Z and 20261110T2300Z audits, which predate both
merges (merge commits 04:06Z and 10:55Z on 2026-11-11). When the re-audits exist, the decider runs:

    python3 usecases/safetyfw_accounting.py anthropic-rsp --source manage-agents/pilots/anthropic-rsp/source/rsp-3.4.txt --check --report /tmp/rsp-accounting-score.json --score manage-agents/debates/uc-audit-anthropic-rsp-<RE-AUDIT>/VERDICTS.md
    python3 usecases/safetyfw_accounting.py openai-preparedness --source manage-agents/pilots/openai-preparedness/source/pf-v2.txt --check --report /tmp/pf-accounting-score.json --score manage-agents/debates/uc-audit-openai-preparedness-<RE-AUDIT>/VERDICTS.md

It prints two lines: the UNFAITHFUL units with a loss entry, with the list of those without one, and the FAITHFUL
units with a loss entry. Write the score report to /tmp, not over the saved evidence, unless the batch decides to
save it.

As a baseline only, I scored the pre-fix verdicts (the old audit judged the old translation, which the fixes
rewrote). RSP: 2 of 29 UNFAITHFUL units have a loss (f9-internal, f16-ask-commentary). 7 of 47 FAITHFUL units have
one: rows-cond, f6-keep-past, f11-analyses, f11-review, f11-goal-missed, f18-rso, f19-unredacted. Preparedness: 9 of
50 UNFAITHFUL and 7 of 34 FAITHFUL. My reading of the 7 RSP FAITHFUL-with-loss units:
- rows-cond, f11-analyses, f11-review, f11-goal-missed and f18-rso: an opaque act whose legend does not state its
  content. This is harmless for the key, whose questions ask whether the act is done, but a reader cannot see what
  the act requires.
- f6-keep-past ("at that link") and f19-unredacted ("final"): small dropped qualifiers that the auditors missed or
  judged harmless.

The re-audit should decide which.

## Choices and deviations (each a conservative option or required by a fixed input; recorded here, not asked)

1. **Anchoring beyond account.py's `norm()`.** account.py's normalisation left 28 of the RSP's 94 quotes and at
   least 10 of Preparedness's unanchored. I may not edit the headers, so the matcher also handles four things:
   - the PDF ligatures (ﬁ, ﬂ, ﬀ, ﬃ, ﬄ);
   - case and punctuation, so a quote's `'highly capable'` matches the source's `"highly capable"`;
   - a footnote marker of one or two digits, or the RSP page footer "Responsible Scaling Policy, Anthropic <n>",
     between two words of a quote, which is cut out of the span;
   - a quoted word split by a line-end hyphen in the source ("con- trols").

   A number or word of the quote is never skipped: `test_anchoring_skips_layout_but_not_words` checks that "within
   60 days" does not match the source's "30 days" and that a dropped word does not anchor.
2. **Act slots.** In "a predicate whose `regulated.act`, with "{0} " removed, occurs in the text", every other
   placeholder stands for a non-empty phrase. Otherwise an act with a second slot (`plans_in_place`: "have the plans
   of the company about {1} in place") never occurs. Placeholder digits are not legend words.
3. **Legend fields** are the three the task names (description, verbalisation, regulated act). account.py also
   read `negative_verbalisation`. The narrower set accounts fewer words.
4. **`open`** resolves when the predicate's description contains "decided by" (the RSP: "Open term OTn, decided by
   …") or "decides" (Preparedness: "SAG decides this"). `reading` resolves on the block's `when` set ids or the
   first column of PLAN 3.1's table (`RSn`, `Nn`). `loss limit n` resolves on a numbered item of PLAN section 12.
   Class numbers 1 to 11 are the checklist's; the tool keeps them as a constant because the checklist is outside
   the repository.
5. **Further refusals:** an entry with no content word, a `rule` pointing at its own block, a second line for a
   block, and lines out of file order.
6. **Without `--source`,** entries of a block with an elided quote are not checked against the span ("elided, needs
   the source"). With `--source` they are. On main six RSP quotes and no Preparedness quote contain an elision.
7. **`rule <id>` is checked literally** (the words must be among the target's accounted words). The pinned stemmer
   does not join "assess" with "assessment", "share" with "shared" or "acknowledge" with "acknowledged". So nine
   Preparedness entries for words a sibling block carries in another inflection say `restates`, not `rule`:
   - f11-exception-deploy "capability threshold until the associated risks that they pose are sufficiently
     minimized" (f2-no-deploy carries it);
   - f11-acknowledge "we assess that doing so" (f11-within) and "and share information to validate this claim"
     (f11-share);
   - f11-protect "we assess that doing so" (f11-within), "we publicly acknowledge that we are making the
     adjustment" (f11-acknowledge) and "and share information to validate this claim" (f11-share);
   - f11-share "we assess that doing so" (f11-within) and "we publicly acknowledge that we are making the
     adjustment" (f11-acknowledge).

   Relaxing the check to accept a target's own `restates` words would be the less conservative reading, so I did
   not.
8. **Blocks with no quote.** Seven RSP blocks quote nothing of 12 characters or more ("the same plans", "the same
   'should'"): rows-uncond, f5-default, f10-attempt-default, f15-revenue-default, t4-only-if, s2-only-if-result and
   s2-only-if-third. Their span is empty and their line is `omits: nothing`, but the sibling's losses apply to them
   too (rows-uncond has rows-cond's three). Fix: each such header quotes its own sentence.

safety-framework (out of scope; the tool runs on it unchanged): 34 of 36 quotes anchor with
`--source manage-agents/pilots/safety-framework/source/fsf-3.1.txt`. 26 of its 60 blocks quote nothing, and the two
failures in f16-ds and f16-ds-strict pair a short quote with the next opening quote. Its headers would need each
block to quote its own source sentence in full (at least 12 characters), with no bare short quotes next to it.

## Seeded bugs (each planted, its one test run and seen to fail, then restored with `git checkout`)

Recorded in `docs/usecases/safetyfw/accounting-seeded-bugs.json`. Only Python and data changed (no Lean, no Rust).

| | File | Bug | Failing test |
|---|---|---|---|
| a | usecases/safetyfw_accounting.py | `Source.anchor` returns an elided quote as written | `test_elided_quote_spans_the_source_between_its_fragments` |
| b | usecases/safetyfw_accounting.py | `rule <id>` accepted without the target's accounted words | `test_reason_arguments_resolve["audited every year" rule r-keep-False]` |
| c | usecases/anthropic-rsp/accounting.d1.txt | f11-review's line deleted | `test_case_sidecar_passes_in_form[anthropic-rsp]` |
| d | usecases/anthropic-rsp/accounting.d1.txt | f18-rso's `loss 1` changed to `restates` | `test_saved_report_totals_are_the_sidecars[anthropic-rsp]` |
| e | usecases/safetyfw_accounting.py | no line-end hyphen tolerance | `test_anchoring_skips_layout_but_not_words` |
| f | usecases/safetyfw_accounting.py | `open` accepted without a decider | `test_reason_arguments_resolve["every year" open minor-False]` |

## Notes for the DRI

- The decider adds each unit's sidecar line to the audit material (manage-agents/tools-local/uc-audit.py
  `_safetyfw_prepare`); this item does not touch uc-audit.
- The losses are the next fix round's list, not FOLLOW-UPs. I did not check whether any of them changes a keyed
  answer. f11-within's class-3 loss (an `allow` default on a conditional permission) is the one most likely to.
- `test_saved_report_totals_are_the_sidecars` compares the saved evidence with the committed sidecar. It does not
  use a live `git diff`, and the task (6) asks for it.
- SIZE: 482 product (usecases/safetyfw_accounting.py), 274 tests, 184 other hand-written lines (the two sidecars)
  plus this REPORT. The two accounting.json files are tool output.
