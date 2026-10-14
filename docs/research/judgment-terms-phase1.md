# Judgment terms: phase 1 (JT-0p)

> **Status.** Phase 1 of [judgment-terms-PLAN.md](../spec/judgment-terms-PLAN.md) draft 3, 2026-10-14, branch
> `research/judgment-terms-p1` from `main` at `f98183bf`. Measurement only: no product code (`ve/`, `lean/VE/`,
> `rust/`, `tools/` untouched), no test, no generated file, no model call. Scripts are under
> [research/judgment-terms/](../../research/judgment-terms/); their outputs are under
> [evidence/judgment-terms/](evidence/judgment-terms/). Inputs are the pinned pilot runs, read only (1.3).
>
> The brief names SYNTHESIS 4.1 (phase 1) and `edits-judgment-terms.md`. SYNTHESIS 4.1 predates this plan (research
> wave 2) and lists no judgment-terms item; `manage-agents/debates/plan-synthesis/edits-judgment-terms.md` does not
> exist (the directory has edit files for the seven wave-1 plans only). The DRI's phase-2 decisions
> (`DRI-DECISIONS-PHASE2.md`, "Judgment terms (wave 2)") adopt the plan's requests R1 to R4 and note R5; none of them
> changes JT-0p. So the item and its bar below are the plan's own, draft 3.

## 1. Pre-registration

This section was written and committed before any script in `research/judgment-terms/` existed and before any count,
check or rendering below was run. Before writing it I had read the two ledgers' field names, the open-term records of
both pilots (names, arguments, deciders, factors, and the first unit each term is annotated on), the u010, u020, u037
and u060 entries, and the recorded `parts-check.json` of the UDHR run, to learn the schema and to choose the
encoding of 1.3.2. No count in section 2 had been taken.

### 1.1 The item and its bar, quoted from the plan (section 5, JT-0p)

> ### JT-0p. Pilot: measure judgment terms; asserted judgments (2 h; pilot; first batch)
>
> - **What.** Text for the DRI's merged pilot prompts (`manage-agents/prompts/pilot-additions.txt`,
>   `udhr-additions.txt`, and their audit additions). No repository file.
>   1. **Instrument, both ledgers.**
>      - Each declared or annotated open term gets a class in `metrics.json` under `open_term_class`, by R2.1's rule:
>        `judgment`, `classification`, `exception`, `attitude` or `proportion`.
>      - Each unit gets `judgment_terms` (its open terms of class `judgment`).
>      - `metrics.json` gets `judgment_term_units` and `judgment_term_bytes`, by status and by `missing_feature`.
>   2. **UDHR u010 and u060 as asserted judgments.** This batch adds no profile, so W2's profile-off validator applies.
>      - u010: binary `of_greatest_importance_for` between two named things. W2 refuses repeated `arguments` without
>        the profile, so the record lists two distinct legacy argument labels, never `["thing", "thing"]`; the
>        predicate keeps its sorts `(thing, thing)`. JT-5 replaces the labels by the sorts when the profile is switched
>        on. No sort is invented and the arity does not change.
>      - u060: unary `natural_and_fundamental_group_unit_of_society` on `the_family`.
>      - Both have `decided_by: "unresolved_decider"` and factors from the words. Each is a ground assertion with the
>        meaning `{"open": [...]}`, so its status is OPEN.
>      - u060's note says that "the" (uniqueness) is not represented and is presupposition's. u060 is written and
>        audited, but its bytes stay unclaimed, recorded as `missing_feature: presupposition`: a unit whose meaning is
>        admittedly partly missing contributes no whole-unit FAITHFUL bytes.
>   3. **Audit addition.** A targeted blind audit of u010 and u060. On the sampled units, auditors also check that no
>      CHECKED unit's content uses an open-term predicate, or an evaluative word of 2.4's catalogue written as an
>      undeclared predicate (by hand, until JT-3's `undeclared_evaluative` lands; D15).
> - **Pre-registered bar.** The four UDHR parts load and check as before, with u010 and u060 OPEN.
>   - **PASS** if the targeted audit finds u010 FAITHFUL: claimed bytes +132 (4,792 → 4,924 B, 43.90% → 45.11%).
>   - **FAIL** otherwise: u010 reverts and the reason is recorded.
>   - u060's audit verdict is recorded; it claims no bytes either way.
>   - The instrument has no bar; its numbers start a series. JT-E3 tests its reliability.
> - **Bytes.** UDHR +132 B (**estimate**, until the audit). Constitution 0 B.

The catalogue the audit addition names is the plan's 2.4 row, quoted:

> "reasonable", "appropriate(ly)", "arbitrary/arbitrarily", "fair", "just", "legitimate", "genuine(ly)", "adequate",
> "effective", "necessary", "due", "good judgment", "overly <adj>": in translation, a bound judgment; never a
> definition the checker chooses. Each row is tied to its evaluative sense: "just" is not the "just" of "just as real"
> (C u0031.s03), "necessary" not that of "necessary condition", "due" not that of "due date" or "due to", "effective"
> not that of "effective date".

R2.1's rule, quoted (the instrument's classes):

> **What counts as a judgment term.** A word or phrase whose application to a fully described case still needs an
> evaluative or threshold judgment against a standard the text does not state, so that two informed people who agree
> on every fact can still disagree. Not judgment terms:
> - classification words the text leaves undefined but that facts settle ("persona", "slavery", "member of society");
> - exception placeholders ("exception_to_…");
> - attitudes ("knowingly", "thinks it quite likely"), which are attitudes';
> - proportion words ("vast majority"), which are quantities'.
>
> Graded judgment words ("serious", "significant") are judgment terms whose order is quantities'.

The bar has two parts, which are reported separately and are never merged into one verdict:

- **Bar part A (precondition).** "The four UDHR parts load and check as before, with u010 and u060 OPEN." This needs
  only the checker, so it runs now and gets PASS or FAIL (criteria fixed in 1.3.3).
- **Bar part B (bytes).** "PASS if the targeted audit finds u010 FAITHFUL … FAIL otherwise." This needs a blind
  audit by a model that did not write the units. This phase makes no model call, and the writer of the units cannot
  audit them blind, so part B is **DEFERRED**. Until it runs, the +132 B stay an estimate and are not claimed.

### 1.2 What runs now and what is deferred

| Item | Now or deferred | Why |
|---|---|---|
| JT-0p item 1, the instrument | **Now, retrospectively**: applied by script to the pinned ledgers, with one hand classification table (1.3.4). The live addition to the pilot prompts is deferred | The prompts live in `manage-agents/prompts/` (outside the repository) and are merged by the DRI; the live runs are model runs. A draft of the prompt text is written to the evidence directory |
| JT-0p item 2, u010 and u060 | **Now**, on copies of the four UDHR parts; bar part A | Needs only the checker; the pilot run is never written |
| JT-0p item 3, the targeted blind audit | **Deferred** (bar part B) | A model call, and a blind auditor must not be the writer |
| JT-0p item 3, the by-hand integrity check | **Now**, over every unit with content whose status is not OPEN or READINGS, in both pilots (more than the audit's sample) | Needs no model: a scan, then a hand reading of each hit (1.3.5) |
| JT-E1, JT-E2, JT-E3 | **Not this phase** | Reader and rater experiments with model calls, run later under their own authorisation (the brief) |
| JT-0 | Done before this phase | Spec draft 2 and plan draft 3 (commit `85d6372d`) |
| JT-1 to JT-5 | Not this phase | Product code |

One descriptive measurement is added that the plan does not ask for, with **no bar**: a forecast of what JT-5's
admission checks (2.1, checks 1 to 5) would say of the pilots' records as they stand (1.3.6). It is labelled a
forecast everywhere: Lean owns admission, and this script only reads the records.

### 1.3 Definitions fixed before the run

#### 1.3.1 Inputs and checker

- UDHR: `manage-agents/pilots/udhr/run-20261012T1800Z/` (`units.json` sha256 `0a43de59…6686`; the four
  `translation-part0N.ve.md`; `parts-check.json`), source `pilots/udhr/source/udhr.md` (sha256 `d6495201…7d3a`,
  10,916 B).
- Constitution: `manage-agents/pilots/claude-constitution/run-20261012T1800Z/` (`units.json` sha256 `353a7528…ec4c`,
  `translation.ve.md` sha256 `adecddd3…45c0`), source `pilots/claude-constitution/source/claude-constitution.md`
  (sha256 `fa10ed48…50dd`, 184,893 B).
- The checker is this branch's `ve` package. The Lean service and the Rust binary are the builds in the
  `ve-integration` worktree (at `main` `dccd9cf5`, whose `lean/` and `rust/` are identical to this branch's), used
  read only through `VE_LEAN_SERVICE` and `VE_RUST_JSONL`; both hashes are pinned in this branch's
  `lean/checkers.lock`, and the script records them. Every run is under `prlimit --as=6442450944`.

#### 1.3.2 The u010 and u060 encoding (the treatment)

Applied to copies of the four parts in `research/judgment-terms/run-jt0p/`; the baseline copies are in
`research/judgment-terms/run-baseline/`.

- **Open-term records.** The four parts carry one identical list of 52 records. Two of them are unused placeholders
  for exactly these units: `greatest_importance` (no arguments; factors "comparison class", "measure of importance")
  and `natural_group_unit` (no arguments; factors "meaning of natural", "meaning of fundamental", "what counts as
  family"). Each is replaced in place, in all four parts, by the record the plan names, so the list stays one list of
  52 and no second record holds the same words:
  - `of_greatest_importance_for`: arguments `["understanding", "realization"]` (two distinct legacy labels, 1.1),
    `decided_by` `unresolved_decider`, factors "comparison class", "measure of importance", jurisdiction `universal`,
    version 1, empty `necessary`, `sufficient`, `precedents`;
  - `natural_and_fundamental_group_unit_of_society`: arguments `["thing"]`, `decided_by` `unresolved_decider`,
    factors "meaning of natural", "meaning of fundamental", "what counts as a group unit of society", jurisdiction
    `universal`, version 1, empty lists.
- **Vocabulary.** Part 1 gains the sort `thing` ("a thing the text names: an understanding, an aim or an
  institution"), the constants `common_understanding_of_these_rights_and_freedoms` and
  `full_realization_of_this_pledge` (sort `thing`; descriptions name their antecedent, the Member States' pledge of
  u009) and the predicate `of_greatest_importance_for` (`thing`, `thing`; verbalisation
  `{0} is of the greatest importance for {1}`). Part 2 gains the sort `thing`, the constant `the_family` (sort
  `thing`; "the family, the institution the Article names, not any one family") and the predicate
  `natural_and_fundamental_group_unit_of_society` (`thing`; verbalisation
  `{0} is the natural and fundamental group unit of society`). Parts 3 and 4 change only in the two records.
- **Units.** u010 and u060 keep their ids and spans; `kind` becomes `asserted`, `meaning` becomes
  `{"open": [<the term>]}`, `support` stays `none`, and the content is the ground atom:
  `["binary", "of_greatest_importance_for", ["const", "common_understanding_of_these_rights_and_freedoms"],
  ["const", "full_realization_of_this_pledge"]]` and
  `["unary", "natural_and_fundamental_group_unit_of_society", ["const", "the_family"]]`.
- **Ledger copy** (`research/judgment-terms/run-jt0p/units.json`): u010 status OPEN, `open_terms`
  `["of_greatest_importance_for"]`, no `missing_feature`, a note that the recital function of "Whereas" is not
  represented; u060 status OPEN, `open_terms` `["natural_and_fundamental_group_unit_of_society"]`, `missing_feature`
  `presupposition`, `claimed: false`, and the plan's note on "the". Neither carries an audit verdict.

If the checker refuses this encoding, the refusal is recorded verbatim, and any change made to get past it is listed in
section 2 as a deviation from this pre-registration, with its reason.

#### 1.3.3 "Load and check as before" (bar part A)

Each of the four parts, baseline and JT-0p copy, is checked, loaded and rendered as the pilot's own `check_parts.py`
does (`check_document`, `load_document`, `render_document`). Bar part A is PASS exactly when all of these hold:

1. **A1.** All four JT-0p parts load and check without error.
2. **A2.** u010 and u060 have status OPEN in the JT-0p parts.
3. **A3.** Every other unit has the same status in the JT-0p part as in the baseline part.
4. **A4.** For each part, the check's premises status, readings status and conflict status are equal between
   baseline and JT-0p.
5. **A5.** For each part, the coverage differs from the baseline only by the moved units: `bytes_by_status` moves 132
   B (part 1) and 66 B (part 2) from UNFORMALISED to OPEN; `bytes_by_kind` moves the same bytes from `unformalised` to
   `asserted`; `unformalised_reasons.other_evaluative_open_claim` drops by 1 in parts 1 and 2; `residual.open_terms`
   stays 52; every other coverage member is equal. Parts 3 and 4 are equal in every coverage member.

The baseline itself is compared with the recorded `parts-check.json` (reproduction check P1 in 1.4); a baseline that
does not reproduce the recorded run is reported, and A1 to A5 are still judged against the baseline as checked now.

**Claimed bytes.** The pilot's claimed bytes are the bytes of every unit whose ledger status is not UNFORMALISED (the
ledger's 4,792 B). After JT-0p, u060 is OPEN in the checker but `claimed: false` in the ledger, so the claim moves by
u010's bytes only. The claim is reported as an estimate until bar part B runs.

#### 1.3.4 The instrument (no bar)

- **Terms.** Every open term declared in a pilot's document front matter or annotated in a unit's ledger
  `open_terms`: 52 declared in the UDHR (identical in the four parts) and, in the constitution, the union of the 33
  declared and the ledger's annotated names.
- **Classes.** One hand table, `research/judgment-terms/open_term_class.tsv`, written and committed before the script
  aggregates anything: one row per term, with its class, a `borderline` flag and a one-line reason that cites the
  term's words. Rules, in order:
  1. a term whose words name a mental state of an agent (knowing, intending, thinking likely) is `attitude`;
  2. a term named `exception_to_…` or `…_exception…`, or whose record says it is an unstated exception, is `exception`;
  3. a term whose words name a share of a collection ("most", "vast majority") is `proportion`;
  4. a term whose application to a fully described case still needs an evaluative or threshold standard the text
     does not state is `judgment` (R2.1), and graded words are `judgment`;
  5. every other term is `classification`.

  A term that mixes a classification with a judgment (R2.3's "borderline") is classed by rule 4 (the judgment part
  makes two informed people able to disagree on one fully described case) and flagged `borderline`. The table is one
  rater's: JT-E3 measures whether a second rater agrees, so no count below is published as a measured judgment-term
  count until JT-E3 passes (plan, JT-E3 "Then").
- **Per unit.** `judgment_terms`: the unit's ledger `open_terms` of class `judgment`, in ledger order.
- **Aggregates.** `judgment_term_units` and `judgment_term_bytes` (unit span bytes), by ledger status and by
  `missing_feature` (the key `none` where the unit has none), plus totals, and `open_term_class` as a map; computed for
  the UDHR baseline ledger, the UDHR JT-0p ledger copy and the constitution ledger. The constitution's annotated terms
  on UNFORMALISED units are counted as they are (an annotation says which open term the unit would need).
- **Catalogue units** (descriptive): units whose source text (the pinned source sliced by the unit's span) contains a
  word of 2.4's catalogue in a form listed in 1.3.5, by status, split by whether the unit has a judgment term.

#### 1.3.5 The by-hand integrity check (JT-0p item 3, without the model audit)

- **Units.** Every unit, in both pilots, that has content in the document (an `ast`, a norm or reading candidates)
  and whose checker status is CHECKED or LABELLED.
- **Scan.** For each predicate the content reads (and, for norm content, the regulated predicate), flag:
  - **(a) open-term predicate**: its name equals a declared open-term name, or contains one as a whole `_`-separated
    token run, or its description contains the words "open term";
  - **(b) catalogue word**: its name (split at `_`), description or verbalisation contains, as a whole word,
    `reasonable`, `reasonably`, `unreasonable`, `appropriate`, `appropriately`, `inappropriate`, `arbitrary`,
    `arbitrarily`, `fair`, `fairly`, `unfair`, `just`, `legitimate`, `illegitimate`, `genuine`, `genuinely`,
    `adequate`, `adequately`, `effective`, `effectively`, `necessary`, `due`, `overly`, or the phrase
    `good judgment`.
- **Hand reading.** Each flagged predicate is read with its unit's source sentence and gets one verdict:
  `hidden judgment` (an evaluative word written as an undeclared predicate in a CHECKED or LABELLED unit: the D15
  case), `other sense` (2.4's sense rows: "just as", "necessary condition", "due to", …), or `not a judgment` (with the
  reason). The scan's hits and the verdicts are both saved.
- The integrity check has **no bar** in the plan; its result is a finding for the audit and for JT-3 and JT-5.

#### 1.3.6 Admission forecast (descriptive; no bar)

For every declared record in both pilots, as the records stand (and for the UDHR JT-0p copy), the script reports
which of 2.1's checks 1 to 5 would fire first, reading the document's own vocabulary (neither pilot declares W3
definitions, so `hide E (names defs)` is `E`):
1. `JudgmentUnbound`: no predicate with exactly the term's name;
2. `JudgmentArguments`: the predicate's sorts are not the record's `arguments`;
3. `JudgmentRegulated`: the predicate is regulated;
4. `JudgmentCriterionAsUnit`: `necessary` or `sufficient` is not empty;
5. `JudgmentDecider`: `decided_by` is `unstated`.

It also counts, independently of fault order, how many records fail each check. For each `JudgmentUnbound` record it
lists the predicates whose names contain the term's name as a token run (rename candidates for JT-5), without
judging them.

### 1.4 Reproduction checks and their expected values

These figures were fixed by the research note and the plan (commits up to `85d6372d`) before this work began; none is
chosen here. Each passes only on exact equality; a failure is reported with the measured value, and no expected
value or definition changes after the run.

| # | Check | Expected | Source |
|---|---|---|---|
| P1 | The four baseline parts, checked now, reproduce the recorded `parts-check.json`: every unit status, and each part's coverage | equal | the run |
| P2 | UDHR claimed bytes in the pinned ledger (units not UNFORMALISED) | 4,792 B, 43.90% of 10,916 | plan JT-0p, 8 |
| P3 | u010's span, u060's span | 132 B, 66 B | plan JT-0p, 8 |
| P4 | Claimed bytes with u010 added | 4,924 B, 45.11% | plan JT-0p |
| P5 | Declared open terms | UDHR 52 (each part), constitution 33 | R0 |
| P6 | UDHR covered units carrying a judgment open term, with R2.3's own term list (`ill_treatment`, `effective`, `arbitrary`, `genuine`, `just_and_favourable_conditions_of_work`, `merit`, `just_requirements`, `morality`, `general_welfare`, `due_recognition_and_respect`, `democratic_society`) | 11 units, 1,333 B (8 OPEN 706 B, 3 READINGS 627 B) | R2.3 |
| P7 | With R2.3's borderline terms (`discrimination`, `persecution`, `free_and_full_consent`, `full_development_of_the_human_personality`, `free_and_full_development`) | 18 units, 1,945 B | R2.3, plan JT-5 |
| P8 | Constitution source lines (non-empty) containing a word of R2.1's base lexicon | 203 of 454 | R0, R2.1 |
| P9 | UDHR UNFORMALISED units whose source contains a word of R2.1's lexicon with the UDHR additions, excluding u043 and u093 (R2.3 puts graded comparisons outside its table) | 12 units, 1,942 B | R2.3 |

P6 and P7 count a unit once however many listed terms it carries. P8 and P9 use R2.1's lexicon exactly as written:
case-insensitive whole words, `*` a stem (any word continuing the stem), and "good judgment" as a phrase.

### 1.5 Outputs

- `evidence/judgment-terms/bar-a.json`: A1 to A5, each true or false, with the values compared.
- `evidence/judgment-terms/parts-check-baseline.json`, `parts-check-jt0p.json`, and the render diff of the parts.
- `evidence/judgment-terms/instrument-{udhr,udhr-jt0p,constitution}.json`: the metrics addition each ledger would
  carry (`open_term_class`, `judgment_term_units`, `judgment_term_bytes`, per-unit `judgment_terms`).
- `evidence/judgment-terms/integrity.json`: the scan's hits and the hand verdicts.
- `evidence/judgment-terms/admission-forecast.json`.
- `evidence/judgment-terms/reproduction.json`: P1 to P9.
- `evidence/judgment-terms/prompt-additions.md`: the draft prompt text for the DRI.

## 2. Results

Everything below was measured after section 1 was committed (`ee233169`, then the class table `9c9f72b3`). The
end-to-end script is [research/judgment-terms/run_jt0p.sh](../../research/judgment-terms/run_jt0p.sh); the checks
ran on this branch's `ve` with `ve_service` sha256 `05cc6b90…` and the Rust binary `3ec83dee…`, both pinned in
`lean/checkers.lock` (hard links to the `ve-integration` builds at the default paths, recorded in
`jt0p-inputs.json`). Each `ve` run was under `prlimit --as=6442450944`.

### 2.1 Deviations from the pre-registration

Each was forced by a refusal or by a missing record, and each is listed here before any result is read against a bar.

| # | What changed | Why |
|---|---|---|
| D1 | The reading sets of parts 1 and 2 are rebuilt: every meaning id, distinguishing-model id and S1 situation id recomputed over the new environment by VE's own identity functions (`jt0p.py`, `reidentified`). Each model and situation base gains the domain `thing` (one element), the new constants on it and empty relations for the new predicates | The first JT-0p check was refused, verbatim: part 1 `VEError: distinguishing model id does not match model`, part 2 `VEError: reading meaning id does not match content`. All three kinds of id are digests over the environment id (`ve/identity.py`, `ve/model.py`, `ve/readings_s1.py:113`), so any new sort, constant or predicate changes them; the pilot's own build recomputes them the same way (`tools/readings_s1_pilot.py`, `_reidentified`). Self-test: with no added vocabulary the rebuild reproduces all 11 reading sets of the four baseline parts byte for byte. The checker recomputes every id and Lean replays every situation at load, so the rebuild cannot pass a wrong id |
| D2 | The three constants carry `sort` and `description` only, no `verbalisation` | Refused next, verbatim: `CheckerUnavailable: ReadingsConformance: Rust did not evaluate the model shown: expected exactly fields ["sort", "description"]`. The spec agrees with Rust: "constant entries contain `sort` and `description` … unknown fields are rejected" (`docs/spec/v0-language.md:23`). Python's loader accepted the field (finding F2) |
| D3 | `of_greatest_importance_for` has no `verbalisation` | Not a refusal: the check passed with it, but the render diff showed 13 other predicates of part 1 losing their wording (section 2.6, F1). The template is rejected by the wording lint anyway (`BINARY_AUXILIARY`, `BINARY_CONVERSE`, `LOGICAL_WORD`, `SYMBOL_COLLISION`), so u010 renders the same without it. Bar part A was re-run after D3 and is reported for the final encoding; it was PASS before D3 as well |
| D4 | The integrity scan reads the constitution's unit statuses from its ledger | The run's `check.json` records no unit statuses. For the UDHR, P1 shows that the ledger's and the checker's statuses agree on every unit |
| D5 | The scan also reports, for the record, each scanned unit's predicates and a positive control over OPEN and READINGS units | A count of zero is only informative if the same scanner finds the cases it looks for. No definition of 1.3.5 changed |

### 2.2 JT-0p against its bar

| Bar part | Bar (quoted in 1.1) | Measured | Verdict |
|---|---|---|---|
| A | "The four UDHR parts load and check as before, with u010 and u060 OPEN" | A1: all four JT-0p parts load and check. A2: u010 UNFORMALISED → OPEN (part 1), u060 UNFORMALISED → OPEN (part 2). A3: no other unit's status changes (130 units). A4: premises `model`, readings `CONFLICT-FREE among rules on the same act, conditional on 0 coherence premises` (parts 1, 2, 4; part 3 has none), conflict `CONFLICT-FREE`, each equal to the baseline. A5: coverage equal to the baseline except the moved bytes (part 1: UNFORMALISED 3,135 → 3,003, OPEN 1,132 → 1,264; part 2: 66 B likewise; `other_evaluative_open_claim` 1 → 0 in each; `residual.open_terms` 52 in every part); parts 3 and 4 equal in every member | **PASS** (`bar-a.json`) |
| B | "PASS if the targeted audit finds u010 FAITHFUL: claimed bytes +132 (4,792 → 4,924 B, 43.90% → 45.11%). FAIL otherwise" | Not run: it needs a blind audit by a model that did not write the units | **DEFERRED** |
| u060 | "u060's audit verdict is recorded; it claims no bytes either way" | Not run (same audit) | **DEFERRED** |
| Instrument | "no bar; its numbers start a series" | 2.4 | no bar |

So the UDHR's claimed bytes stay 4,792 B (43.90%) until the audit. If it finds u010 FAITHFUL they become 4,924 B
(45.11%; P4 reproduces the arithmetic). The checker's own OPEN bytes rise by 198 B, because u060 is OPEN in the
document. The ledger copy holds u060 back with `claimed: false`, so the pilot's claimed-bytes rule must read that field
(section 3, item 1).

**The rendering** (not part of the bar; `render.diff`, 19 lines after D3) changes in three places. u010 becomes
'Open reading: "common_understanding_of_these_rights_and_freedoms" has the recorded relation
"of_greatest_importance_for" to "full_realization_of_this_pledge".' u060 becomes 'Open reading: "the_family" is
classified as "natural_and_fundamental_group_unit_of_society".' And u025's distinguishing-situation line gains "thing
is a thing", because a situation base must now cover the new sort. Neither new template is accepted by the wording
lint (u060's: `LOGICAL_WORD`, `TEMPLATE_LENGTH`, `UNARY_MODIFIER`), so both units show identifiers, as the research
note found for unary predicates (R1.1). This is today's arm of JT-E1.

**What the auditor should look at** (recorded in the ledger copy's `jt0p_note`). The recital function of "Whereas"
(a reason given for the proclamation) is not represented in u010. In u060, "the family" is one constant (the
institution), while u061 reads the same subject distributively ("every family is entitled to protection"). And "the"
(uniqueness) is presupposition's.

### 2.3 Reproduction checks (pre-registered in 1.4)

| # | Expected | Measured | Verdict |
|---|---|---|---|
| P1 | the recorded `parts-check.json` | every unit status and every coverage member of the four parts equal (`reproduction-p1.json`) | PASS |
| P2 | 4,792 B, 43.90% | 4,792 B, 43.90% | PASS |
| P3 | u010 132 B, u060 66 B | 132 B, 66 B | PASS |
| P4 | 4,924 B, 45.11% | 4,924 B, 45.11% (from the JT-0p ledger copy, u060 held back) | PASS |
| P5 | UDHR 52 in each part, constitution 33 | 52, 52, 52, 52; 33 | PASS |
| P6 | 11 units, 1,333 B (8 OPEN 706 B, 3 READINGS 627 B) | the same | PASS |
| P7 | 18 units, 1,945 B | 18 units, 1,945 B | PASS |
| P8 | 203 of 454 lines | 203 of 454 | PASS |
| P9 | 12 units, 1,942 B | **17 units, 2,792 B** | **FAIL** |

P9 fails. R2.3's twelve units are all among the seventeen, so R2.3's table is a hand-selected subset of the
lexicon's hits, not a lexicon count. The five extra units:
- "fundamental human rights" (u008a, 199 B) and "fundamental freedoms" (u009, 196 B), both names;
- "without any limitation due to race" (u057, 138 B), 2.4's "due to" sense;
- "the elementary and fundamental stages" (u097, 76 B), a classification;
- "universal and effective recognition and observance" (u013bb, 241 B, `norms`), which reads as an evaluative
  "effective" that R2.3's table omits.

So the measured figure is 12 units and 1,942 B by R2.3's reading, 13 units and 2,183 B with u013bb, and 17 units and
2,792 B by the bare lexicon. The expected value stands as pre-registered, and the check is reported as failed.

### 2.4 The instrument (no bar; one rater)

Classes, from the hand table (`open_term_class.tsv`, one line of reason per term):

| Pilot | Terms | judgment (borderline) | classification | exception | attitude | proportion |
|---|---:|---:|---:|---:|---:|---:|
| UDHR | 52 | 32 (10) | 18 | 0 | 1 | 1 |
| Constitution | 37 | 18 (4) | 13 | 4 | 1 | 1 |

Units and bytes carrying a judgment term (`judgment_term_units`, `judgment_term_bytes`):

| Ledger | Total | By status | By `missing_feature` |
|---|---|---|---|
| UDHR, run 20261012T1800Z | 18 units, 1,945 B | OPEN 14 (1,200 B), READINGS 4 (745 B) | none 18 |
| UDHR, JT-0p copy | 20 units, 2,143 B | OPEN 16 (1,398 B), READINGS 4 (745 B) | none 19 (2,077 B), presupposition 1 (66 B) |
| Constitution, run 20261012T1800Z | 507 units, 88,989 B | UNFORMALISED 493 (86,820 B), OPEN 12 (2,082 B), READINGS 1 (68 B), LABELLED 1 (19 B) | norms 361 (68,076 B), quantities 43 (5,430 B), causation 32 (5,599 B), defaults 27 (4,209 B), other:discourse 21 (1,775 B), none 14 (2,169 B), counting 7 (1,475 B), attribution 2 (256 B) |

- **UDHR.** The instrument's 18 units and 1,945 B equal R2.3's "judgment plus borderline" set (P7) unit for unit,
  because the table classes R2.3's borderline terms as `judgment` with the flag. No UDHR ledger annotates an open
  term on an UNFORMALISED unit, so all 18 are covered units.
- **Constitution.** The ledger annotates open terms on UNFORMALISED units: what each unit would need. Five terms carry
  almost all of it: `ethical_harm` (275 units), `broad_safety` (222), `genuine_helpfulness` (88),
  `appropriate_oversight` (60) and `good_judgment` (42). So the constitution's counts turn on five class decisions,
  which JT-E3 should weigh. The covered units carrying a judgment term are 13 units, 2,150 B (OPEN 12, READINGS 1).
  Without the units whose only judgment terms are borderline (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03), they
  are 9 units, 1,186 B. These figures fill the research note's unfilled placeholders `CONSTITUTION-OPEN-UNITS` and
  `CONSTITUTION-OPEN-JUDGMENT` (R5.1, plan JT-5). The LABELLED unit is the heading "### Avoiding harm" (u0126),
  annotated `ethical_harm`; it has no content.
- **Catalogue words** (raw word matches, other senses included). Every covered unit whose source contains a catalogue
  word carries a judgment term: UDHR 8 of 8, constitution 4 of 4. Units that contain a catalogue word without
  carrying a judgment term are all UNFORMALISED: UDHR 8 units (1,433 B), constitution 80 units (16,755 B). These 80
  are where D15's `undeclared_evaluative` report will matter once they are formalised.

### 2.5 The by-hand integrity check (JT-0p item 3, without the model audit)

- **Scanned.** 20 units: the UDHR's 18 CHECKED units and the constitution's 2. No LABELLED unit in either pilot has
  content. Predicates read: the UDHR's are rights and regulated acts (`has_the_right_to_life`,
  `compel_association_membership_permitted`, …); the constitution's are `denial_of_being_claude_permitted`, and u0248
  reads none. All are listed in `integrity-scan.json`.
- **Hits: 0.** No CHECKED unit's content uses an open-term predicate or a catalogue word, by name, description or
  wording. No CHECKED unit's source sentence contains a catalogue word either (2.4).
- **Control.** The same scanner over the 49 OPEN and READINGS units hits 35 of them, among them every `is_arbitrary*`
  predicate (u037, u045a, u046, u055, u064) and u0052.s01's "good judgment".
- **So** neither pilot shows a judgment as checked today: the translators already route every judgment to OPEN by
  hand. D3's gap (OPEN is author-declared) is real in the language, but these pilots do not exercise it.

### 2.6 Admission forecast (descriptive, no bar) and findings

What 2.1's checks 1 to 5 would say of the records as they stand (`admission-forecast.json`):

| Document | Records | First fault | Fails the check (any order) |
|---|---:|---|---|
| UDHR, each of the four parts | 52 | `JudgmentUnbound` 52 | Unbound 52, Decider 52 (`unstated`), Arguments 0, Regulated 0, CriterionAsUnit 0 |
| UDHR JT-0p, part 1 / part 2 | 52 | Unbound 51 and Arguments 1 (u010's labels, as JT-0p intends) / Unbound 51, admitted 1 (u060) | Decider 50 |
| Constitution | 33 | admitted 31, `JudgmentUnbound` 1 (`good_judgment`), `JudgmentArguments` 1 (`child_sexual_abuse_material`: record `[material, context]`, predicate `[situation]`) | Decider 0 |

- **UDHR: no term is bound.** No predicate in any part has an open term's exact name.
  - 17 of the 52 terms have a predicate that contains the name as a token run (rename candidates).
  - Read by hand, only five used terms have a predicate that is the term itself under another name:
    `is_arbitrary*`, `is_slavery*`, `is_servitude`, `is_slave_trade`, `is_determined_by_law`.
  - The other used terms sit inside a larger predicate, a right, a regulated act or a relation (`effective` inside
    `has_the_right_to_an_effective_remedy`; `persecution` inside `has_the_right_to_seek_and_enjoy_asylum`), or
    in no predicate.
  - 16 of the 52 declared terms are used by no unit.
- **`arbitrary` spans four sorts.** In part 1 it is three predicates over three sorts: `is_arbitrary(measure)`,
  `is_arbitrary_u045a(interference)` and `is_arbitrary_u046(intrusion)`. Part 2 adds `is_arbitrary_u064(deprivation)`.
- **Constitution: binding-ready.**
  - 31 of 33 records already name a predicate with their sorts.
  - `good_judgment` has no predicate. u0052.s01's judgment sits inside the regulated `judgment_use_required` ("use
    good judgment" is the act), which is exactly the role question the plan's JT-5 asks the runner to settle.

**Findings** (owners outside this plan; no product code was changed):

- **F1 (renderer, english-lean).** A rejected binary template still claims its head word. `ve/printer.py:201-204`
  registers each template's head as owned by its predicate. The rejected "{0} is of the greatest importance for {1}"
  has head "is", so 14 one-word "{0} is X" templates of part 1 gain `SYMBOL_COLLISION`; the 13 of them that were
  accepted before now render as 'classified as "…"' (`is_slave_trade` was already rejected). A rejected template should not take other predicates' wording.
- **F2 (environment decoder).** Python accepts a constant `verbalisation`, which the spec says is rejected
  (`v0-language.md:23`); Rust refuses it. The disagreement surfaced only as `CheckerUnavailable` on the readings
  conformance path.
- **F3 (any change to the environment).** Every reading-set id is a digest over the environment id. JT-5's profile
  switch changes the profile list and so the environment id, so every reading set of both pilots must be rebuilt
  (D1's mechanism), not only the units that change.

## 3. Consequences for draft 2

The plan is at draft 3; this section lists what its next draft should take from phase 1, batch by batch. Nothing
here moves a bar.

1. **JT-0p: confirmed, with additions to its prompt text.** Bar part A passed; the byte claim waits for the audit.
   The next draft and the prompt text (`prompt-additions.md`) should add:
   - the sort `thing` is declared in parts 1 and 2: neither part had it, and the plan's `(thing, thing)` needs it;
     "no sort is invented" should read "no sort beyond `thing`";
   - the two new records replace the unused placeholders `greatest_importance` and `natural_group_unit`, so no second
     record holds the same words;
   - the reading sets of parts 1 and 2 are rebuilt (D1), constants carry no `verbalisation` (D2), and
     `of_greatest_importance_for` gets no template (D3, F1);
   - the ledger's claimed bytes exclude units marked `claimed: false`; without this, u060's 66 B, which the checker
     counts as OPEN, would be claimed.
2. **JT-5: changed in scope and size; its bar stands.**
   - **Binding is a re-translation, not a rename, for the UDHR.** All 52 records would be refused, first as
     `JudgmentUnbound`. Only five used terms have a predicate of their own to rename. For the others the judgment
     must first be split out of a larger predicate (`has_the_right_to_an_effective_remedy` →
     `remedy(x) ∧ effective(x)`), which changes audited units and is act-phrases' attachment work (AP; plan D10).
   - Draft 3's "rename either the predicate or the term" and 2–3 h hold for the constitution (31 of 33 bound), not
     for the UDHR.
   - **Proposed:** JT-5 switches the constitution first. The UDHR switches only after a re-translation step (owned
     with act-phrases) that gives every used judgment its own predicate, with a fresh audit of the changed units.
   - **Unused declarations.** 16 UDHR records are used by no unit, yet the profile refuses an unbound record. The
     bar "no declaration removed … to reach CHECKED" should say whether an unused record may be removed, with its
     reason recorded, to pass admission. Proposed: yes for unused records only; a used term is never removed.
   - **Deciders.** All 52 UDHR records say `unstated`, which `JudgmentDecider` refuses (D7). JT-5's prompt must
     rewrite them to `unresolved_decider`.
   - **Rebuild.** Switching the profile on changes every reading-set id in both pilots (F3).
   - **Constitution.** `good_judgment` (u0052.s01) has no predicate of its own, and its judgment is inside the
     regulated act. The plan already says to record the limit, not work around it; phase 1 confirms the limit
     exists. `child_sexual_abuse_material` needs its record's arguments aligned with its predicate's sort.
   - **Expected moves.** No CHECKED or LABELLED unit in either pilot uses a judgment (2.5), so JT-5 should expect
     no unit to move to OPEN. A move would be a finding, as the bar says.
3. **D2 and section 4.2: one judgment word over several sorts.**
   - Under D2 a bound term has one sort list, but `arbitrary` is applied to four sorts.
   - The 4.2 row "the usage map lists u037, u045a, u046, u055, u064 under one term" cannot hold as written. The
     units span two documents (parts 1 and 2), and a usage map is per document.
   - Within part 1, three sorts would need three terms, a shared supersort, or sort-polymorphic terms (a language
     change D2 does not make).
   - Proposed for the next draft: say that a word used over n sorts is n bound terms that share their words, each
     with its own usage-map row, and that english-lean's legend may group them. Correct 4.2's row to "one row per
     sort and per part".
4. **D3, D15 and JT-1 to JT-3: unchanged, and the value is preventive.**
   - The integrity gap is not exercised by either pilot (2.5): no unit's status changes from it today.
   - Their case is what the research note says, integrity for new translations and authoring, readable answers, and
     the `undeclared_evaluative` report. The 80 constitution units (16,755 B) that contain a catalogue word without a
     judgment term mark where D15's report will first matter.
5. **JT-3 and JT-E1: unchanged.** Today's arm of JT-E1 is confirmed: the asserted judgments render with identifiers
   (2.2). F1 goes to english-lean, which owns the renderer; JT-3's declaration and legend lines are not predicate
   templates, so F1 does not block them.
6. **JT-E3: unchanged; its input exists.** The 89 pilot-term pairs of `open_term_class.tsv` are the frame for its 60
   stratified terms. The constitution's counts turn on five heavily annotated terms (2.4), so the report should give
   the counts with and without disagreed terms.
7. **The research note: fill R2.2.** The constitution placeholders (`CONSTITUTION-LEDGER-SUMMARY`,
   `CONSTITUTION-LEDGER-SECTION`, `CONSTITUTION-OPEN-UNITS`, `CONSTITUTION-OPEN-JUDGMENT`) were never filled. Section
   2.4 and `instrument-constitution.json` supply them, and JT-5's byte row should read "13 units, 2,150 B (9 units,
   1,186 B without borderline-only units)". R2.3's unformalised table should say that it is a hand selection
   (P9), and should consider u013bb.
8. **JT-0, JT-1, JT-2, JT-4, JT-E2: unchanged** by anything measured here. **No batch is cancelled.**

## 4. Deferred

| Item | Reason |
|---|---|
| JT-0p bar part B: the targeted blind audit of u010, and with it the +132 B claim | A model call, and the auditor must not be the writer. The units, their notes and the ledger copy are ready in `research/judgment-terms/run-jt0p/` |
| u060's audit verdict | The same audit |
| Merging the prompt additions into `manage-agents/prompts/` | Outside the repository; the DRI merges one file per pilot (SC2). Draft text in `prompt-additions.md` |
| The instrument in the live 06:00/18:00 runs | Pilot runs are model runs. The retrospective values on run 20261012T1800Z are the series' first point |
| JT-E1, JT-E2, JT-E3 | Reader and rater experiments with model calls, authorised separately (the brief). JT-E2 also needs AT-3a on `main` |
| JT-0p on later pilot runs (20261013T0600Z, the 20261013T1800Z worktrees) | The plan names run 20261012T1800Z; later runs exist but were not used, so the numbers stay comparable with R2 |

**Process notes.**
- No product code, test or generated file was changed, and no model was called.
- The pilot runs were only read: nothing under them is newer than this report's first commit.
- The full release gate was not run: this branch adds only `docs/research/` and `research/judgment-terms/`, which
  `tools/layer_policy.py` assigns no layer, so test selection would choose the whole suite (as scope's phase 1
  recorded).
- I ran `tests/test_hang_guards.py`, `test_repo_map.py`, `test_inventory_lint.py` and `test_identity_lint.py` with
  `-n 4`: 197 passed; the 3 `test_repo_map.py` failures came from an uncommitted file, and all 28 pass once it was
  committed.
- My first attempt at those tests ran without `VE_NATIVE_PREBUILT=1`, so the test setup started a `lake build` in
  this worktree that ran for about 30 minutes before its timeout. The pinned binaries were not changed (same hashes);
  its partial objects remain in the git-ignored `lean/.lake/build/{ir,lib}`.

(Written after the run.)
