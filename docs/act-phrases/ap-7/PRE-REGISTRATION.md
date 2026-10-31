# AP-7 pre-registration: do derivations find the auditors' readings?

Plan: `docs/spec/act-phrases-PLAN.md` at `80f056f9e`, "AP-7" (D3, D4; D9 decided: option (i), refuse). Committed
before Lean's readings are dumped and before any model call; nothing below changes after the first call.

## Sample (46 phrases)

- **UDHR, the plan's list:** u020, u027, u045a, u051, u055, u059, u076, u079b, u087, u092, u105a–c, u106. The plan
  says "15 units"; its list names 14 unit ids, and u105a–c are one sentence, so they are one phrase (`u105`, the
  spec's G8): 12 phrases.
- **Draft 4's additions:** u037, u101, u0062.s01, u0156.s03: 4 phrases.
- **Constitution, 30 drawn:** [draw.py](draw.py). Population: the 669 units of run `20261012T1800Z` whose
  `missing_feature` is `norms` (units.json sha256 `353a7528…`; full text from the pinned source's span, sha256
  `fa10ed48…`), saved in [population.json](population.json). Eligible ("*and* or *or* inside the verb phrase",
  made mechanical): the excerpt has *and*, *or* or *nor* after its first modal or wish word (should, shouldn't,
  must, mustn't, may, can, cannot, can't, never, ought, need, needs, want, wants): 195 units. Drawn with
  `random.Random("act-phrases-AP7").sample(sorted(eligible), 30)` ([draw.json](draw.json)): u0199.s03 u0056.s01
  u0142.s01 u0291.s05 u0267.s02 u0065.s02 u0019.s07 u0263.s03 u0183 u0223.s03 u0193.s04 u0211.s03 u0038.s06
  u0203.s03 u0241.s01 u0194.s01 u0215.s03 u0067.s07 u0191.s04 u0054.s03 u0209.s07 u0253.s04 u0137.s03 u0099.s03
  u0007.s03 u0187.s03 u0155.s03 u0114.s03 u0141.s05 u0283.s04. Neither u0062.s01 nor u0156.s03 was drawn, so
  none is counted twice.

## Declared vocabularies and Lean's side

[sample.json](sample.json) gives each phrase its modal, its bearer (what `{0}` stands for), the DEMAND the auditors
read (the source's own words) and its vocabulary:

- **Registered:** a phrase with a row in the AP-2 corpus (`docs/act-phrases/ap-2/evidence/n-measurement.json`,
  spec 11.2 and 11.2b) takes that row's act phrase, fixed phrases, frames and adverbs, unchanged: u027 G6, u051 G5,
  u055 G9, u076 G11, u079b G7, u087 G12, u092 G10, u105 G8; the D9 rows u037 X037, u045a X045a, u101 X101,
  u0062.s01 X0062, u0156.s03 X0156. So the D9 units carry no fixed phrase, and D9 (i) is what they test.
- **Written by rule V** (u020, u059, u106 and the 30 draws), by the builder from the source text only:
  - V1 modal: the clause of the first modal or wish word; *should*, *must*, *shall*, *need(s) to*, *ought to*,
    *want(s) X to* give *must*; with *not*, *n't*, *never*, *neither … nor* or a *no* subject, *must not*; *may*,
    *can* and *feel free to* give *may*; *has the right to*, *has the right*. A wish word that governs no act, or a
    modal only quoted, gives the sentence's main clause, read as *must*.
  - V2 bearer: the clause's subject (the object of *want*) is `{0}`; the voice is the source's.
  - V3 act phrase: `{0}` and the source's words after the modal (keeping a *to* after *want*, *need* or *ought*) to
    the end of the clause, verbatim; the clause ends at the sentence's end, a colon or a dash, before *while*,
    *when*, *where*, *whether*, *if*, *even*, *unless*, *because*, *since*, *rather than*, *such as*, *given* or
    *so that*, and before a comma followed by *but*, or by *and* with a new subject. u106 takes spec A3's phrase
    and fixed phrase.
  - V4 vocabulary: one frame per verb item (the first head, and each head after a join word or list comma), with
    `""` when an object follows and each preposition that follows it in its item; no split marker, no modifier
    marker, no fixed phrase (except A3's); the adverbs are the single adverbs that modify a head.
- Before this commit only `checkVocab` ran (all 46 pass, `dump.py --vocab-only`). After it,
  [dump.py](dump.py) runs, per phrase, `checkVocab`, the act check's conditions 1 to 5 and lexing (`checkWith`), and
  `phraseReadings V op rawCap stepBudget` with the phrase's modal, and writes each reading in Lean's words
  (`paraphrase`) to `lean-readings.json`, committed before the first call. `refused`, `limit` and `none` are no
  reading. No vocabulary changes after the dump.

## Calls (at most 160 calls and 4M CW in total, no paid fallback, no Sonnet proxy)

[runner.py](runner.py) holds the three prompts. Every call is `claude -p --model claude-opus-5-5 --effort high
--max-turns 1 --restricted --no-session-persistence`, its account from its own `pick-claude-account.sh` call, never
Fable. Codex was at its credit cap (resets 2026-11-04), so both listing seats are Claude Opus 5.5 in separate
sessions (DRI ruling reviews/dri-decisions-20261031-ap-7.md item 1); the 'both auditors list' readings therefore come
from one model family, which can share blind spots; cross-family review is optional (lead 2026-10-10).

- **Three distinct sessions:** seat A and seat B (the two blind listing auditors) and seat M (the matcher). Each call
  is its own session; none resumes another or shares a transcript or a directory.
- **Listing** (seats A and B, one call per phrase, the same prompt for both, 92 calls): the sentence, the DEMAND and
  the bearer; never Lean's readings or the other seat's list.
- **Judging** (seats A and B, after every listing call; phrases with a Lean reading, 8 per call): each Lean reading,
  YES (a reading of this English) or NO.
- **Matching** (seat M, one call per phrase, 46 calls): A's list, B's list and Lean's list. It pairs A's and B's
  readings that say the same thing (each at most once), names for each pair the Lean reading that says the same
  thing or NONE (each Lean reading at most once), and names every Lean reading with a skipped middle.
- A failed call (CLI error, a non-Opus model, unparsable or unbound output, or not made because a cap was reached)
  is recorded and scored as no reading listed: a listing lists none; a judgement says NO to all its readings; a
  failed matching counts min(|A|, |B|) agreed readings for the phrase, none matched, and no skipped middle. No call
  is repeated. The run stops after three failed calls in a row for inspection and goes on with the next call.

## Frozen bars (verbatim from the plan)

- recall ≥ 90% of the readings both auditors list;
- ≤ 10% of Lean's readings judged "not a reading of this English" by both;
- no skipped-middle reading.

A sample phrase with no reading under its declared vocabulary (refused, or `none`) contributes zero matched
readings: it counts against recall for every reading the auditors list.

Scoring (`runner.py --score`, from the saved records only): recall = matched pairs / pairs over all phrases; the
second bar counts Lean's readings both seats judged NO, over all of Lean's readings; the third, the matcher's
skipped-middle names. Reported beside the bars, with no bar of their own: the share of phrases with at least one
reading, and the phrases D9 refuses (those that parse but have no meaning: D9 (i), or an atom that does not fit its
frame, which Lean's counts do not tell apart; only option (i) is built, so no other option is measured). AP-7 runs once: on FAIL there is no second run. Its percentages are evidence about
the declared vocabulary, not a one-reading guarantee.
