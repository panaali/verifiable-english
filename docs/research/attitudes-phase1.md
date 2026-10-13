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

## 2. AT-0p: result

**Result status.** Run 2026-10-13 after the pre-registration above (commit `c0cf207c`). Script
`research/attitudes/at0p.py`, end to end `research/attitudes/run_at0p.sh` (5 to 20 min, by machine load). Evidence:
`docs/research/evidence/attitudes/at0p-probe.json`, `at0p-measure.json` and `at0p-render-diff.json` (written by the
script); `at0p-rendered.md` and `at0p-reproduction.json` (assembled by hand from the script's outputs; what they
claim is checked by the script: the `cmp` steps in `run_at0p.sh`, and `at0p.py render`).

**Method.** The pilot run was copied to two working copies (`research/attitudes/run-baseline/`, `run-at0p/`,
untracked), whose scripts then run against this checkout's VE (Lean built from `49de179e` sources, Rust binary
pinned in `lean/checkers.lock`). Every VE run had a 6 GiB address-space limit. The pilot directory was not written,
with one exception, now repaired: the first `apply` imported the run's `spec.py` from the pilot path, which wrote
`__pycache__/spec.cpython-314.pyc` into it. That file was deleted (the directory had no `__pycache__` before), the
script now imports from the working copy, and `run_at0p.sh` checks that no `__pycache__` appears.

1. **Reproduction (control).** On the unmodified copy, the run's own `nd.py all` rebuilt a main translation
   byte-identical to the run's `translation.ve.md`, and the run's own `probe_unspecified.py` wrote a file
   byte-identical to the recorded `probes/unspecified-probe.json`. So this checkout gives the run's recorded answers.
   They include the audit's case: "the case does not hold (the knowledge atom does)" is UNDECIDED for all 7 rules.
2. **Rewrite.** `at0p.py apply` makes the PLAN's rewrite in both documents `nd.py` reads (`translation-without-content.ve.md`
   and `readings/all-strict.ve.md`). For each u0165.s0i the guard becomes
   `["or", ["and", C_i(var 0), knowingly_engages_i(var 1, var 0)], thinks_quite_likely_i(var 1, var 0)]`
   (de Bruijn: `var 0` is the situation, `var 1` the instance of Claude). The 14 binary predicates on
   (`claude_instance`, `situation`) are added, each with a W2 open-term record (`decided_by: unresolved_decider`;
   factors "what counts as knowingly and intentionally engaging in an action of the category" and "how likely
   counts as quite likely"). `restricted_action_knowing_or_quite_likely` is deleted from the vocabulary, the
   open-term list and each unit's `meaning.open`. The run's `nd.py all` then rebuilt the main translation, which
   VE admitted and checked.
3. **Probe.** The plan's points were asked as the run's probe asks them (Lean `norm-defaults-status` at a
   one-element situation, with the run's fallback for UNKNOWN). The run's 21 other points were asked again.
   *Correction after review:* the first version of `at0p.py` did not repeat the run's conflict check, which the run
   adds at each `operator_input_permitted` point (10 of the 21), nor the run's conflict section (three witness
   situations and a whole-document proof attempt). So its "21 of 21 the same as recorded" could not have caught a new
   conflict on those points. The probe now repeats both, as the run does (`93c41310`); the rerun gives the same
   statuses at every point, and all four conflict checks equal the recorded ones.

| # | Bar (quoted in 1.1) | Measured | Verdict |
|---|---|---|---|
| A1 | case false, thinks-quite-likely true: SETTLED no | 7 of 7 `SETTLED no` | **PASS** |
| A2 | case true, knowingly true: SETTLED no | 7 of 7 `SETTLED no` | **PASS** |
| A3 | neither: UNDECIDED | 14 of 14 `UNDECIDED` (7 with the case true, 7 with it false) | **PASS** |
| A4 | case false, knowingly true: UNDECIDED | 7 of 7 `UNDECIDED` | **PASS** |
| A5 | the seven audit-case points UNDECIDED → SETTLED no | before: 7 × `UNDECIDED` (reproduced); after: 7 × `SETTLED no` (A1) | **PASS** |
| A6 | claimed bytes unchanged (2,951) | `bytes_by_status` identical to the run's: CHECKED 73, LABELLED 349, OPEN 2,529, UNFORMALISED 181,942. The claimed 2,951 is CHECKED + LABELLED + OPEN (73 + 349 + 2,529); CHECKED + OPEN, the sum 1.1's note names, is 2,602. Both are unchanged, because every status is | **PASS** |
| A7 | open terms 33 → 46 | 46 in the main translation: 14 added (`knowingly_engages_1..7`, `thinks_quite_likely_1..7`), 1 removed (`restricted_action_knowing_or_quite_likely`). The strict companion has 44 | **PASS** |
| A8 | the 7 units (874 B) become candidates for audit verification | needs the next audit | **DEFERRED** (section 4) |

Not bars, also measured:

- The informative points both give `SETTLED no`: case true with thinks-quite-likely true, and case false with both
  attitudes true.
- All 21 other probe points give the run's recorded status (21 of 21; the 10 `operator_input_permitted` points with
  the run's conflict check). The run's four conflict checks give the recorded results (three witness situations
  UNKNOWN, the whole document CONFLICT-FREE).
- The main translation keeps the run's own assertions: premises `model`, reading plan `enumerate` with 8 choices,
  readings CONFLICT-FREE, coverage 100 %. The strict companion's premises are `model`.
- `ve document render` is byte-identical outside the seven rules. Checked by script: this checkout's render of the
  unmodified run is byte-identical to the run's recorded `rendered-raw.md` (`cmp` in `run_at0p.sh`), and against it
  the AT-0p render changes 7 lines (1278, 1280, …, 1290), each the "Open reading" line of one rule naming the deleted
  term, each replaced by three lines (`at0p.py render`, `at0p-render-diff.json`). `at0p-rendered.md` is a hand-made
  excerpt of those lines.

**Observation (not a bar).** The rendering names the new open terms by their identifiers, not by their
verbalisations: "(b) that instance of Claude has the recorded relation "thinks_quite_likely_1" to that situation".
The run rendered the old term the same way ("… is classified as "restricted_action_knowing_or_quite_likely""). So
an auditor who reads only the rendering sees the name, not the description or the factors.

**What A4 shows.** The untyped repair is not faithful at the impossible point. Where the case does not hold but
Claude knowingly engages in it, the rules answer UNDECIDED, because nothing ties knowing to the category. That is
the gap typed attitudes close (D-A4 premise 1, factivity, makes that point unreachable). The plan predicted this
("an impossible situation the untyped language cannot refuse"); it is now measured.

## 3. E1 and E2: prepared, not run

Neither experiment was run: both are defined by model readers, and this phase makes no model calls (**DEFERRED**,
section 4). Everything that needs no reader is done and committed (`cd6af1cb`):

| Piece | Where | What |
|---|---|---|
| E1 items | `evidence/attitudes/e1-items.json` | 28 pair items in E1's list order plus 8 certainty items = 36. Ids follow the spec stub (`E1.pair.<a>.<b>`, `E1.cert.<w>`). 40 call orders from `random.Random("attitudes-E1")`. 1,440 calls |
| E2 items | `evidence/attitudes/e2-items.json` | 3 factivity, 3 knows → believes, 8 knows → thinks it *w* (all eight words, G3), 3 negated "know", 3 "unless", 3 "P, and X does not know that P" = 23 items. Seed `attitudes-E2`. 920 calls |
| Protocol | both files, `protocol` | reader `claude-sonnet-5-5`; one fresh context per call (G2); the prompt text and item labels (this phase's choice, G5); the parsing rule (first line: yes / no / cannot tell, anything else invalid, which counts as neither yes nor no; its effects are in G6) |
| Scoring | `research/attitudes/experiments.py score-e1`, `score-e2` | the quoted bars as constants (`PAIR_YES, PAIR_MAX_NO = 36, 2`; `CERT_YES = 34`; `E2_REACH = 36`). An answer set must hold exactly one answer per item and session, or it is refused and not scored |
| Frozen table | `experiments.py table` | emits the Lean `Table` literal (spec 2.1) and evaluates `Table.reviewed` with `lake env lean` on a copy of the AT-0 stub (`ve-design-attitudes/lean/SpecStubs_attitudes.lean`, read only), so the closure review is Lean's, not Python's. The stub is untracked in that worktree and still draft 1; its `Table` and `Table.reviewed` are spec draft 3's (section 2.1) apart from comments (compared by hand, 2026-10-13). It is pinned by sha256 `2178fb6eb1dfc2be9e908643538190a17da0b78a346954418d247e386b6a35e8` (`STUB_SHA256`), and a stub with another hash is refused (`8538355c`), so a later edit cannot silently change the review. The review also uses this checkout's `VE.Closure.Order.atLeast` (QS-1's closure, `lean/` at `49de179e`) |
| Self-check | `experiments.py selfcheck`; `evidence/attitudes/e-selfcheck.json` | 22 checks on synthetic counts (no reader): each bar at its boundary (pair 36/2 in, 35/0 out, 36/3 out; certainty 34 in, 33 out; factivity 36 in, 35 out, with premises 2 and 3 dropped too); refusal of missing and duplicate answers; parsing (including that "Not necessarily." is invalid under the current rule, G6); through Lean, a table with a failed derived pair is not reviewed, the resolved one is, and an all-pass table is; and a stub with another hash is refused. All 22 hold (20 at `cd6af1cb`; the last two added at `8538355c`) |
| Seeded bug | `PAIR_YES` 36 → 35 | the self-check fails ("pair yes=35 no=0": false, exit 1); restored |

**Found while preparing (no data involved).** The item design makes the debate-round-3 clause empty. E1 asks all
28 pairs directly, in list order, and every lower-bound word has its own knows → thinks item. So the closure of the
passing pairs can never reach a pair, or a premise-3 word, that has *no* direct item. It can only reach one whose
direct item *failed*. "One item for each pair the closure derives without a direct E1 item, and for each premise-3
word reached only through the closure" therefore adds no items. What remains is the plan's resolution rule for a
failed derived entry, and that rule has two options (G4).

## 4. DEFERRED

| Item | Why it is not done here | What is ready |
|---|---|---|
| E1 run | needs 1,440 model calls (Sonnet 5.5 readers); this phase makes none | items, orders, protocol, scorer, self-check |
| E2 run | needs 920 model calls; same reason | same |
| Closure review on real data and freezing `table` (spec 2.1) | needs E1's and E2's answers | `experiments.py table`, reviewed by Lean through the stub |
| AT-0p A8: the next audit's verdict on the seven units (874 B) | needs the pilot's next audit, outside this phase; it is also the DRI's go/no-go input after AT-6a (F7) | the AT-0p documents (rebuilt by `run_at0p.sh`), the before/after rendering |
| Landing AT-0p in the pilot (the next constitution run) | the pilot directory is read only for this task; the pilot runner applies it | `research/attitudes/at0p.py` (copy, apply) on that run's inputs |
| AT-0 PASS (SR-8 order) | waits on E1, E2 and the closure review | — |

The UDHR run was not used: no phase-1 item touches it (the plan gives UDHR 0 B for this design, R 2.5).

## 5. Consequences for draft 2

**Confirmed.**

- **AT-0p, as specified.** Every measurable bar passes, and every estimate matches the measurement exactly:
  2,951 B claimed and unchanged, open terms 33 → 46, and the seven audit-case points UNDECIDED → SETTLED no. Draft 2
  can mark AT-0p's row in the section-7 table and its numbers as measured, citing this report. The queue (edit 10,
  synthesis 4.4) is unchanged: AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5. SC-1b starts from the AT-0p translation
  (open terms `knowingly_engages_i` and `thinks_quite_likely_i`, synthesis C23).
- **The motivation for AT-1 to AT-3b and AT-6a.** A4 measures the untyped repair's limit: the impossible point is
  UNDECIDED. Nothing in phase 1 cancels a product batch. The go/no-go after AT-6a still waits on A8.

**Changed (to make before E1 and E2 run; each is a gap in the pre-registration, not a moved bar).** Each needs the
DRI's decision, recorded in the plan before any answer exists:

- **G1. Pair direction.** "28 pairs" fixes one direction per pair, but the plan does not say which. Proposal (used
  in `e1-items.json`): the earlier word in E1's list is the first sentence, so a passing item is the scale pair
  (earlier, later).
- **G2. Independence.** "40 independent sessions with no shared context" and "1,440 short calls" do not say whether
  a session's 36 items share one context. If they do, earlier items prime later ones, and the 40 answers to an item
  are not 40 independent readers. Proposal: one fresh context per call. The seeded order then fixes only the call
  order.
- **G3. E1 ∥ E2.** The pilot path runs E1 and E2 in parallel, but E2's per-word items are defined by E1's
  `lowerBound`. Proposal: E2 asks the knows → thinks item for all eight words (8 items, 320 calls) and scores only
  the lower-bound words. Then E2 does not wait for E1.
- **G4. The closure resolution has two outcomes.** "The weaker word leaves `lowerBound`, or the scale pair is
  dropped" is a choice, and the frozen meaning depends on it. Proposal (implemented as `resolve` in
  `experiments.py`, output reviewed by Lean): until the closure is clean, the weaker word of a derived entry whose
  item failed leaves `lowerBound`, with every pair and premise that names it. This is the only one of the two
  options with a unique outcome. Also, by section 3, the debate-round-3 closure items are empty by construction, so
  draft 2 can say so instead of listing them.
- **G5. Unspecified framing, wordings and questions.**
  - *Framing (E1 and E2).* The plan gives E1's two sentences and its question, but no preamble and no layout. Both
    item files add a preamble, "Read the text and answer the question as an ordinary reader of English. Answer with
    exactly one of: yes, no, cannot tell." (`PROMPT` in `experiments.py`, the `protocol.prompt` of both files). E1's
    pair items label their parts "First sentence:", "Second sentence:", "Question:"; its certainty items and every
    E2 item label only "Question:" (`e1_items`, `e2_items`). These are this phase's choices, not the plan's, and
    they can move answers (what "an ordinary reader" invites, and offering exactly three answers), so the DRI fixes
    them before any answer exists.
  - *E2's wordings.* The plan gives no text for the knows → believes, knows → thinks *w* and "P, and X does not
    know that P" items. Proposals are in `e2-items.json`.
  - *"P, and X does not know that P".* The plan does not say which question its items ask, nor which answer
    "reaches 36 of 40". The current items ask "Must P?" and expect "yes". That tests that P is read as asserted,
    not how "does not know" is read, so **the current items cannot admit the form**: a pass would admit it without
    testing it. The scorer still computes the plan's bar on them (`must_p_items_reach_36`), but its decision is
    "refused" whatever the counts (`8538355c`). Proposal: draft 2 adds three items "P, and Claude does not know
    that P. Question: Does Claude know that P?" (expected "no"; 120 calls), and the form is admitted only if all
    six reach 36 of 40. If draft 2 does not add them, the form stays refused, with its rewrites.
- **G6. Reader settings, and answers that are not yes, no or cannot tell.** Temperature, output limit and extended
  thinking are not stated. Nor is the treatment of other answers. The current rule (`parse` in `experiments.py`)
  reads the first line; anything but yes, no or cannot tell is "invalid", counted as neither yes nor no. That rule
  has three effects, not one:
  - (a) An invalid answer counts against every yes bar (it is not a yes).
  - (b) It loosens E1's "at most 2 answer no". "Not necessarily." parses as invalid, not as no (the self-check
    records this). So a pair with 36 yes and 4 "Not necessarily." passes, although the bar's intent refuses it.
  - (c) For the negated-"know" items, `agreed_36` takes the largest of the four counts, invalid included. So 36
    invalid answers would be recorded as "36 of 40 agree on one reading". The form is refused either way, so only
    what AT-0 records is affected.

  Proposal: for (b), count invalid answers as no for the no cap. That is conservative, and unlike mapping clear
  negatives ("not necessarily", "it need not") to no, it needs no list of phrases. For (c), leave invalid answers
  out of agreement. In both, report the invalid count per item. The scorer implements the current rule until the
  DRI decides, and it changes only with that decision, recorded in the plan before the run.

**Cancelled.** Nothing. E1 and E2 have produced no data, so no batch is confirmed or cancelled by them. Until they
report, `table` admits nothing (spec fixture D0), and AT-0's PASS stays blocked (SR-8).

**Cost, for the DRI's scheduling.** E1 is 1,440 calls (as the plan estimates). With G3, E2 is 920 calls
(23 items × 40), against the plan's implied 40 × (15 + |`lowerBound`|); with G5's three extra items, 1,040.

## 6. Commits

| Commit | What |
|---|---|
| `c0cf207c` | pre-registration: section 1, the bars quoted before any run |
| `0c3be928` | AT-0p script, probe, measurements, evidence |
| `cd6af1cb` | E1/E2 items, orders, scorers, Lean-reviewed table emitter, self-check |
| `25f7e9fa` | results, DEFERRED list, consequences |
| `8538355c` | review fixes: the AT-0 stub pinned by sha256; the asserted-not-know items do not admit the form; self-check 22 of 22 |
| `93c41310` | review fixes: the AT-0p probe repeats the run's conflict checks; the render diff is checked by script; timeouts for a loaded machine. The rerun gives the same A1–A7 results, and `at0p-measure.json` is byte-identical |
| (this commit) | review fixes in this report: G5 (framing; the asserted-not-know items), G6 (the three effects of "invalid"), the probe method, the A6 sums, what was checked by hand |
