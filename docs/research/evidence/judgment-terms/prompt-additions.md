# JT-0p: draft prompt additions (for the DRI to merge)

Draft text for `manage-agents/prompts/pilot-additions.txt`, `udhr-additions.txt` and their audit additions (plan
JT-0p, "What"). Not merged: the prompts live outside the repository, and the DRI merges them into one file per pilot
(DRI SC2). Section 2 of `docs/research/judgment-terms-phase1.md` gives the measurements behind each line.

## Both pilots: the judgment-term instrument

> For every open term you declare in the front matter or list in a unit's ledger `open_terms`, write its class in
> `metrics.json` under `open_term_class`, one of `judgment`, `classification`, `exception`, `attitude`, `proportion`.
> Decide in this order: a mental state of an agent ("knowingly", "thinks it quite likely", "aimed at") is `attitude`;
> an `exception_to_…` placeholder is `exception`; a share of a collection ("most", "the vast majority",
> "generally available") is `proportion`; a word whose application to a fully described case still needs an
> evaluative or threshold standard the text does not state ("arbitrary", "reasonable", "serious uplift", "genuine") is
> `judgment`, graded words included; everything else ("slavery", "persona", "member of society") is
> `classification`. A term that mixes a classification with a judgment ("persecution", "discrimination") is
> `judgment`; add it to `open_term_class_borderline`. Keep last run's class for every term you keep; give a reason in
> one line for every new term or changed class.
>
> Give every unit `judgment_terms` (its open terms of class `judgment`). In `metrics.json`, write
> `judgment_term_units` and `judgment_term_bytes`, each by status and by `missing_feature` (`none` where the unit has
> none), and their totals.

The retrospective values on run 20261012T1800Z, which the first live run should reproduce for unchanged units, are in
`instrument-udhr.json` and `instrument-constitution.json` of this directory.

## UDHR: u010 and u060 as asserted judgments

> Write u010 and u060 as asserted judgments, each OPEN, with no new profile:
> - u010: the binary predicate `of_greatest_importance_for(thing, thing)` between the constants
>   `common_understanding_of_these_rights_and_freedoms` and `full_realization_of_this_pledge` (sort `thing`). Its
>   open-term record replaces the unused `greatest_importance` and lists two distinct argument labels
>   (`["understanding", "realization"]`), never `["thing", "thing"]`, which W2 refuses without the profile.
> - u060: the unary predicate `natural_and_fundamental_group_unit_of_society(thing)` of the constant `the_family`
>   (the institution, not any one family). Its record replaces the unused `natural_group_unit`. Note that "the"
>   (uniqueness) is not represented and is presupposition's; record `missing_feature: presupposition` and
>   `claimed: false`: u060 is written and audited, but its bytes are not claimed.
> - Both records: `decided_by: "unresolved_decider"`, factors from the words, empty `necessary`, `sufficient`,
>   `precedents`. Each unit's meaning is `{"open": [<its term>]}`, kind `asserted`, content the ground atom.
> - Change the one shared record list in all four parts. Rebuild the reading sets of parts 1 and 2 as your build
>   does: every meaning, model and situation id is a digest over the environment, and the new sort, constants and
>   predicates change it.
> - A constant entry has only `sort` and `description` (no `verbalisation`; the Rust checker refuses one).
> - Give `of_greatest_importance_for` no `verbalisation`. The wording lint rejects "{0} is of the greatest importance
>   for {1}", and its head "is" then takes every one-word "{0} is X" wording in part 1 away (14 predicates fall back to
>   'classified as "…"').
> - Check that the four parts load and check as before, with u010 and u060 OPEN, and that the rendering changes only
>   at u010, u060 and the one line of u025's distinguishing situation that now names `thing`.

## Audit additions

> Targeted, blind (an auditor that did not write them): u010 and u060, FAITHFUL or not, each with its reason. u010's
> 132 bytes are claimed only if it is FAITHFUL; otherwise u010 reverts and the reason is recorded. u060's verdict is
> recorded; it claims no bytes either way.
>
> On every sampled unit: does any CHECKED unit's content use an open-term predicate, or an evaluative word of the
> catalogue ("reasonable", "appropriate(ly)", "arbitrary/arbitrarily", "fair", "just", "legitimate", "genuine(ly)",
> "adequate", "effective", "necessary", "due", "good judgment", "overly …") written as a predicate that is not
> declared as an open term? Read each word in its sense: "just as", "due to", "necessary condition" and "effective
> date" are not the evaluative rows.
