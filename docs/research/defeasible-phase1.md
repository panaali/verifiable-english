# Defeasible consequence, phase 1: DF-0 and DF-E3

> Status: phase 1 of [docs/spec/defeasible-PLAN.md](../spec/defeasible-PLAN.md) (draft 3, `632bc4ed`), branch
> `research/defeasible-p1`. Measurement only: no product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) changed and no
> model was called. Scripts are in `research/defeasible/`, evidence in `docs/research/evidence/defeasible/` (the
> DRI's instruction for this run; the plan's 6.2 named `docs/research/defeasible-phase1/*`). DF-E1 and DF-E2 are later
> batches and are not run here.
>
> This file was committed in two steps. Section 1 (pre-registration) was committed **before** any script below was
> run; sections 2 onward were added after the runs. Nothing in section 1 was edited after data was seen.

## 1. Pre-registration (committed before any run)

### 1.0 Inputs, pinned

Read-only. The two pilot runs the plan names (plan header, line 21: "the two pilot runs `20261012T1800Z`"), and the
use cases DF-E3 names, at this branch's commit.

| Input | SHA-256 |
|---|---|
| `manage-agents/pilots/claude-constitution/source/claude-constitution.md` (184,893 B) | `fa10ed48…d50dd` |
| `…/claude-constitution/run-20261012T1800Z/units.json` (1,132 units) | `353a7528…5ec4c` |
| `…/claude-constitution/run-20261012T1800Z/translation.ve.md` | `adecddd3…145c0` |
| `manage-agents/pilots/udhr/run-20261012T1800Z/units.json` (130 units) | `0a43de59…96686` |
| `…/udhr/run-20261012T1800Z/translation.ve.md` | `85db1157…a7a22` |
| `…/udhr/run-20261012T1800Z/translation-part01..04.ve.md` | `a32f0019…`, `01872146…`, `20437df2…`, `ae330230…` |
| `usecases/{agent-policy,safety-framework,eligibility,asimov-laws,asimov-extended}/` | this branch's tree |
| `ve/lexicon/oewn-2025.json` (word classes for the bare-generic screen, read as data) | `5285df7b…eb5b` |

The joint review's `edits-defeasible.md` named in the brief does not exist in
`manage-agents/debates/plan-synthesis/` (there are edit files for seven other plans only). Phase 1 follows
SYNTHESIS 4.1 phase 1 ("now, no product code: pilots and experiments, each under its own gates") and the DRI's
phase-2 decisions DF1 to DF7 (`DRI-DECISIONS-PHASE2.md`), none of which changes DF-0 or DF-E3.

### 1.1 DF-0 item 1: the second reader

Plan, quoted: "A second reader (a pilot auditor, blind to section 2.3's classes) classifies the 99 screened
constitution units into the nine classes of research 2.3. **Bar, fixed now**: agreement on "G or not G" on at least 90
of 99 units; if not, research 2.3's G-class figures are withdrawn and replaced by the second reader's."

Pre-registered handling: **DEFERRED**. The reader must be blind to 2.3's assignments; this session has read them and
may not call a model, so it cannot be that reader. Done now, without moving the bar:

- `research/defeasible/screen_markers.py` re-runs research 2.3's screen mechanically (the 14 marker words and phrases,
  case-insensitive, whole words, over each unit's `source_excerpt`), to check the hand count. Expected from research
  2.3: 99 units, 19,857 B. This is a reproduction check, not a bar.
- It writes the blind packet for the deferred reader: unit id, bytes and the unit's full source text, with the nine
  class definitions of research 2.3 and **no** assignment, plus a key file (research 2.3's 18 G units) kept apart for
  scoring. The scorer, `research/defeasible/score_second_reader.py`, applies the bar exactly as quoted.

### 1.2 DF-0 item 2: bare generics

Plan, quoted: "Bare generics: units whose first clause has a bare plural or a mass-noun subject and a present-simple
verb, no marker word, and no deontic verb (a stated screen, committed before it runs), counted and classified like 1."

No bar: the output is a count (and the units feed DF-E2, "the 19 G-class units of research 2.3 (and DF-0's bare
generics, if any)"). The classification "like 1" needs the same blind reader: **DEFERRED** with item 1; the units are
added to the packet as a second, separately scored list.

The screen, `research/defeasible/screen_bare_generics.py`, fixed here:

1. **Population.** All 1,132 constitution units; a unit's text is the source bytes `[span[0], span[1])` (the full unit,
   not the 180-byte excerpt). Supplementary, reported separately: the 130 UDHR units over `udhr/source/udhr.md`.
2. **Normalise.** Strip leading whitespace, blockquote `>`, list markers (`-`, `*`, `+`, `1.`, `(a)`, `a)`) and
   emphasis characters `*` and `_`. A unit whose text then starts with `#` is a heading and is skipped.
3. **First clause.** The normalised text up to the first of `, ; : . ? ! ( ) — –`, a straight or curly double quote,
   ` - `, or a newline.
4. **Marker words.** If the unit's whole text contains any of research 2.3's 14 marker words or phrases (as in 1.1),
   the unit is excluded (counted as "has a marker").
5. **Deontic or modal verb.** If the first clause contains a modal (`must should shall may might can could will would
   ought`, with `cannot`, `can't`, `won't`, `shouldn't`, `mustn't`) or a deontic verb form (`need needs require requires
   required permit permits permitted allow allows allowed forbid forbids forbidden prohibit prohibits prohibited oblige
   obliges obliged obligated`), the unit is excluded.
6. **Subject and verb.** Words are `[A-Za-z][A-Za-z'’-]*`. A unit matches if, for the smallest `k` in 1..4, the first
   clause's words `w0..w(k-1)` form a bare noun phrase and `wk` (or `w(k+1)` after one adverb: a word ending in `ly`, or
   one of `often also always never sometimes rarely still only even already just`) is a present-simple verb agreeing
   with it:
   - `w0` is not a closed-class word (determiners, quantifiers, pronouns, prepositions, conjunctions, subordinators,
     wh-words, negation, numerals, `there`, `here`, as listed in the script) and not a proper name (a word that never
     occurs in all-lowercase form anywhere in the same source text);
   - every `w0..w(k-1)` is an OEWN noun or adjective lemma, or a plural of an OEWN noun lemma (`+s`, `+es`, `y→ies`, or
     one of `people children men women data media criteria`), and not a closed-class word;
   - the head `w(k-1)` is a noun: **plural** (a plural form as above) or **singular** (a noun lemma: the mass-noun
     candidate; a bare singular count noun is not a grammatical subject, so the reader's class decides);
   - the verb: after a plural head, an OEWN verb lemma (base form) or `are have do don't`; after a singular head, an
     OEWN third-person form or `is has does doesn't`.
7. **Output.** Count and bytes of matching units, each with its first clause and which head form matched, in
   `docs/research/evidence/defeasible/bare-generics.json`.

### 1.3 DF-0 item 3: baseline

Plan, quoted: "Baseline: on RD-9 SC-9's probe translation, P-1's and P-2's questions with today's kinds, answers
recorded verbatim." Plan table 5: "RD-9 SC-9 for the baseline (the rest now)".

Pre-registered handling: **DEFERRED**. RD-9 is not merged: `main` (`dccd9cf5`) has no RD-9 commit and no `CE4`
(`tests/ce4.py` is on `rd-9/integrate` only). The brief excludes anything not on `main`.

### 1.4 DF-0 item 4: the plain-default probe

Plan, quoted: "The plain-default probe: a soft document with DF-λ's rule as JSON content, through `ve document check`
and `render`; record what each does today (expected: check passes, render refuses with `ve/norm_english.py:398`'s
text)."

No bar; the plan states an expectation, recorded against the observation. DF-λ (spec 8.1, draft 2): a plain regulated
predicate `instructs(operator)` with completion `unspecified`, and rule g1 "Every operator instructs, unless an
exception applies." as a default rule decided by the operator. The plan's table 4.1 spells the same rule over
`instructs_via_system_prompt(operator)` with verbalisation "{0} gives its instructions in the system prompt"; both
spellings are probed. `research/defeasible/probe_plain_default.py` writes each `ve-document@1` (profiles
`documents@1`, `norm-defaults@0`, `norms@0`, `relational-fol@0`, `soft-norms@0`; one unit of kind `norm` whose
content is g1 with `mode: default`) and runs `ve document check` and `ve document render` on it, each under
`prlimit --as=6442450944`, recording exit status, stdout and stderr verbatim. As a control (labelled as such, not part
of the plan's item), the same document with g1 on a declared obligation instead of a plain predicate.

### 1.5 DF-E3: specificity

Plan, quoted: "Pre-registered now. Across the constitution and UDHR translations, the agent-policy,
safety-framework, eligibility and Asimov use cases: colliding default pairs (or W1 pairs on one predicate) where one
rule's guard implies the other's (one entailment each) and the text writes no precedence or rank. **Bar**: build an IDE
check that suggests "Rule m (exception to rule n)." only if at least 5 such pairs exist; automatic specificity is not
built whatever the count (D8)."

Operational definition, `research/defeasible/specificity_pairs.py`, fixed here:

1. **Rule sets** (rules that are present together):
   - constitution and UDHR (`translation.ve.md`; for the UDHR also `translation-part01..04.ve.md`): the base set is
     every unit of kind `norm` with norm content; each reading choice (one reading per reading set, every combination
     when there are at most 4,096, otherwise one set at a time with the base) adds that choice's norm readings;
   - agent-policy: `policy.ve` parsed with VE's own `parse_english` in the environment its manifest is bound to;
   - safety-framework: `translation.document(choice)` for every choice of its reading switches;
   - Asimov: `asimov-laws/rules.ve` and `asimov-extended/rules.ve` (with `base.ve` where the use case loads it), each
     parsed in its own environment;
   - eligibility: its rules are formulas, not norms; if no norm is found, it contributes no rule set (reported).
2. **Colliding pair.** Two distinct rules of one set that are incompatible as soft-norms 1.4 defines it: same predicate
   with opposite signs, or a `+r` on an obligation and a `−m` on its declared dual permission (same act). Every mode
   counts (the plan's "colliding default pairs (or W1 pairs on one predicate)"); the result is broken down into
   default–default and the rest.
3. **Written precedence or rank.** The pair is excluded if either rule reaches the other through `over` edges
   (transitively) in that set, or both have soft ranks and one outranks the other (transitively).
4. **Guard implication.** `G_M ⊨ G_N`, where `G` is the rule's `guard` field (not its `unless` carve-outs), both over
   the predicate's argument context. Decided as follows: if both guards are quantifier-free and mention no defined
   predicate, by a truth table over their atoms (exact); otherwise by VE's tableau (`ve.entailment.prove_entailment` on
   the closed implication in the base environment; a certificate means "implies"), and failing a certificate the
   direction is **unknown**.
5. **Qualifying pair.** Colliding, no written precedence or rank, and the implication holds in **exactly one**
   direction (one rule strictly more specific). Equivalent guards are reported separately (neither is more specific,
   so the suggestion could not say which is the exception), as are implied pairs that already have written precedence
   (the authors wrote the exception).
6. **Count.** Pairs are de-duplicated per corpus by their content (predicates, signs, guards; unordered) and summed
   over corpora.
7. **Verdict.** Bar met if the qualifying count is at least 5. If the certain count is below 5 and the certain count
   plus the pairs with an unknown direction is at least 5, the result is **UNKNOWN**, not met.

## 2. Results (added after the runs; section 1 unchanged)

Commits: pre-registration `e6345192`; item 1 `770823a5`; item 2 `01dfd617`; item 4 `ab6dbb1d`; DF-E3 `268d5e38`.

**Binaries.** This worktree had no Lean build. `ve_service` was copied from `ve-integration`, whose `lean/` tree is the
same as this branch's (`e48a0277`, clean). Its SHA-256, `05cc6b90…`, is pinned in `lean/checkers.lock`. The other
default Lean executables (`ve_metered` among them) came from the same build; they are not hash-pinned. The Rust
binary was rebuilt by `tools/rust_build.py --check` to the pinned `3ec83dee…`. All hashes are in
`evidence/defeasible/binaries.sha256`.

### 2.1 DF-0 item 1: the second reader — DEFERRED

- **Bar** (quoted in 1.1): agreement on "G or not G" on at least 90 of 99 units.
- **Not run.** The bar needs a blind reader. This session has read research 2.3's assignments and calls no model.
- **Reproduction (no bar).** Research 2.3's hand count holds exactly: the screen matches **99 units, 19,857 B**. All
  18 of research 2.3's screened G units are among them (`marker-screen.json`).
- **Ready to run.** `second-reader-packet.json` holds the 99 units with their full text and the nine class
  definitions, and no assignment. `second-reader-key.json` holds the 18 G units and is kept apart from the reader. When
  the reader has answered, `research/defeasible/score_second_reader.py ANSWERS.json` applies the bar exactly as quoted
  (90 of 99).

### 2.2 DF-0 item 2: bare generics — counted; classification DEFERRED

There is no bar. The screen ran exactly as committed in 1.2 (`bare-generics.json`):

| Constitution, 1,132 units | Units |
|---|---:|
| headings | 39 |
| a marker word anywhere in the unit (excluded) | 107 |
| a modal or deontic word in the first clause (excluded) | 256 |
| no bare subject with a present-simple verb | 714 |
| **match** | **16 (2,433 B, 1.32% of the source)** |

The UDHR has **0** matches: 32 headings, 1 with a marker, 27 modal or deontic, 70 no match.

The 16 matches: u0010.s02 "Clear rules have certain benefits"; u0010.s06 "Clear rules and decision procedures make
the most sense when …"; u0018.s02 "AI training is still far from perfect"; u0018.s04 "Supporting human oversight
doesn't mean doing whatever individual users say"; u0043.s01 "Different principals are given different levels of
trust …"; u0075.presupposition "Handling conflicts between operators and users"; u0109.s01 "Honesty is a core aspect
of our vision …"; u0111.s01 "Honesty also has a role in Claude's epistemology"; u0113.s02 "Deception involves
attempting to create false beliefs …"; u0113.s03 "Manipulation involves attempting to influence …"; u0125.s01
"Honesty operates at the level of the overall system"; u0137.s04 "Indirect costs include …"; u0165.s04 "Take actions
that clearly and substantially undermine …"; u0170.s05 "Hard constraints are meant to be a clear"; u0181.s02 "Key
questions include"; u0210.s02 "Current AI models".

These defects were seen after the run and are reported, not corrected. The count above is the count of the committed
screen.

- **Segmentation.** The smallest-`k` rule sometimes splits the subject in the wrong place. It reads "Clear rules have"
  as subject "clear" with verb "rules". This does not change which units match.
- **False positives.** Fragments that are not sentences: u0075.presupposition (a heading phrase), u0165.s04 (an
  imperative list item), u0181.s02 and u0210.s02 (lead-ins).
- **Recall.** Subjects with a post-modifier are missed. Examples from a diagnostic run (labelled post hoc, not counted):
  u0029.s04 "People with access to such friends are very lucky", u0024.s04 "Helpfulness that creates serious risks …
  is undesirable to us", u0020.s04 "Exceptions to this are …", u0134 "Things that are relevant to … include". The
  screen's count is therefore neither an upper nor a lower bound on bare generics; it is the stated screen's count.

Classifying the 16 needs the same blind reader as item 1. They are in `second-reader-packet-bare.json`, a separate
list scored separately.

### 2.3 DF-0 item 3: baseline — DEFERRED

RD-9 SC-9's probe translation (`CE4`) is not on `main` (`dccd9cf5`). RD-9 is in fix rounds on `rd-9/integrate`.

### 2.4 DF-0 item 4: the plain-default probe — expectation NOT met

Expected (plan): check passes, render refuses with `ve/norm_english.py:398`'s text. Observed
(`plain-default-probe.json`, documents in `plain-default-probe/`):

| Variant | `ve document check` | `ve document render` |
|---|---|---|
| DF-λ, spec 8.1 (`instructs`, `unspecified`) | **refused**, exit 1: `UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes await the Lean route` (`ve/document.py:633`) | the same refusal, at load |
| DF-λ, plan 4.1 spelling (`instructs_via_system_prompt`) | the same | the same |
| control: g1 on a declared obligation, `unspecified` | the same | the same |
| *post hoc*: DF-λ (spec spelling) completed by `deny`, without `norm-defaults@0` | **passes**, exit 0: CHECKED 55/55 B, `default_exceptions` 1 (decided by the operator), `soft_status` OPEN | **refused**, exit 1: `A default rule needs a declared obligation or permission act` (`ve/norm_english.py:398`) |
| *post hoc*: plan 4.1 spelling, `deny` | passes (89/89 B) | the same refusal |
| *post hoc*: control, `deny` | passes | exit 0: "Every operator should instruct." and the open-rule reading |

What it means:

- **The expectation fails on `main` today.** DF-λ needs `unspecified`, so `norm-defaults@0` must sit beside
  `soft-norms@0`, and `ve document` refuses that pair when it loads the document, for check and render alike. Opening
  that combination is RD-9 SC-8's job.
- **The English refusal is real.** Without the completion, the rule checks, and render stops at exactly
  `ve/norm_english.py:398`'s text. The deontic control renders. So the line DF-4 plans to delete is the only English
  obstacle once SC-8 lands.
- **Side finding (product code, not changed here).** `ve document` lets a `VEError` escape as a Python traceback
  (exit 1). Every other subcommand prints a JSON `InvalidInput` status with exit 2. The cause is that
  `ve/__main__.py:119-121` calls `document_main` outside the `except VEError` handler. Reported for the DRI; it is not
  DF's to fix.

### 2.5 DF-E3: specificity — pre-registered verdict UNKNOWN; post hoc 0 pairs, bar not met

**Bar** (quoted in 1.5): build the IDE check only if at least 5 colliding pairs, with no written precedence or rank,
have one guard implying the other. Results are in `specificity-pairs.json`.

| Corpus | Rules | Colliding pairs | Without written precedence | One guard strictly implies the other, unwritten |
|---|---:|---:|---|---:|
| constitution (`20261012T1800Z`) | 21 | 3 | 3: neither implies (truth table) | 0 |
| UDHR (`20261012T1800Z`, whole and 4 parts) | 24 | 0 | — | 0 |
| agent-policy | 26 | 144 | 1: both directions unknown (tableau `ResourceLimit`) | 0 certain |
| safety-framework (all reading choices) | 44 | 9 | 8: both directions unknown (tableau `NotFound`) | 0 certain |
| eligibility | 0 (format `wfp-rules@1`, formulas only; no `norms@0`) | 0 | — | 0 |
| Asimov (v2 and extended, de-duplicated) | 42 | 16 | 5: neither implies (truth table) | 0 |
| **Total** | 157 | 172 | 17 | **0 certain, 9 undecided** |

- **Pre-registered verdict: UNKNOWN.** There are 0 certain pairs. With the 9 undecided pairs the total could reach
  9 ≥ 5. The pre-registered method can refute an implication only by truth table, and those 9 pairs have quantified
  guards.
- **Post hoc (`resolve_unknown_directions.py`, `specificity-unknown-resolved.json`).** Every undecided direction was
  refuted by a finite countermodel. Each countermodel passed VE's model check (background premises included) and VE's
  evaluator found the closed implication false. All 9 pairs are "neither", so **0 pairs qualify and the bar is not
  met**. Under either verdict the IDE check is not built: the bar opens the build only when at least 5 pairs are shown.
- **No default–default pair exists anywhere.** Every colliding pair is a W1 or strict pair. The pinned translations
  contain no soft default rules, because RD-9 SC-9 has not merged. The safety framework's default readings (f16-ds,
  f19, f20) collide with nothing.
- **Where one guard does imply another, the authors already wrote the precedence**, and not always in the specific
  rule's favour. In agent-policy, rule 20 ("must not … if the tool is purchase, unless that action is confirmed") is
  written as the exception *over* rule 10 ("may … if the tool is purchase and that action is confirmed"). Rule 10's
  guard is the more specific one. Taken with its carve-out, rule 20 applies only where rule 10 does not. Rules
  credential-read and credential-read-confirmed have equivalent guards and a written exception. Like u0100.s04, this is
  evidence that a derived "more specific wins" would be a reading the text does not give.
- **Method note.** The first DF-E3 run had a bug in my script: it decoded each open guard before closing it, so the
  tableau reported scope errors. Those were not tableau answers. The script was fixed to close the wire form first, as
  1.5 states ("the closed implication"), and only the fixed run's evidence is committed. The agent-policy tableau ran
  at VE's default budget (10,000 steps); 1.5 named no budget.

## 3. Consequences for draft 2

These are for the plan's next draft. The DRI decides which to adopt; no bar was moved.

| Result | Batches it confirms | Batches it changes | Batches it cancels |
|---|---|---|---|
| Item 1 reproduced the screen exactly; the second reader is deferred | none yet | research 2.3's G figures (18 units, 3,631 B) and DF-4's 98–572 B estimate stay *unconfirmed* until the reader runs. DF-S does not use them, so the plan could say that DF-S needs only DF-0 items 3 and 4, and item 1 gates DF-E2 and DF-4's byte claims. As written, "DF-S needs DF-0" would block the statement review on a model call | — |
| Item 2: 16 constitution units (2,433 B), 0 UDHR | — | DF-E2's population becomes the 19 G units plus up to 16 bare generics (at most 35 units), after the reader classifies them. The screen's recall gap (subjects with post-modifiers) should be stated in DF-E2 | — |
| Item 3 deferred | — | the baseline must be recorded on `main` after RD-9 merges and **before** DF-1a or DF-1b changes any answer, or P-1's "0 → 3" has no measured "0". Add that ordering to the batch order | — |
| Item 4: DF-λ is refused at load on `main`; with `deny`, render stops at `norm_english.py:398` | DF-4's deletion target (`ve/norm_english.py:397-398`) is the right line, and it is the only English obstacle seen | DF-4 gains an explicit need: **RD-9 SC-8** (`norm-defaults@0` beside `soft-norms@0` in `ve document`). Today it inherits SC-8 only through DF-1b. DF-0 item 4's expected outcome in the plan ("check passes") should be corrected | — |
| DF-E3: no qualifying pair; no default–default pair at all | D8: no automatic specificity | DF-E3 should be re-run, under the same bar, once RD-9 SC-9's default rules are in a pinned translation: today's count covers W1 pairs only. The re-run's pre-registration should add a refutation step (a finite countermodel confirmed by VE's evaluator), because the tableau cannot refute and quantified guards otherwise stay UNKNOWN | the IDE check "Rule m (exception to rule n)." (D8's suggestion) is **not built**. DF's need for shared piece **S8** (the "more specific than" helper) is withdrawn. Weighing and scope may still ask for S8, on their own evidence |

Also for the DRI, outside this plan: the `ve document` traceback (2.4) is a small product fix for its own branch.

## 4. Item status

| Item | Bar | Result | Status |
|---|---|---|---|
| DF-0.1 second reader | ≥ 90/99 agree on G or not G | not run (needs a blind reader; screen reproduced: 99 units, 19,857 B) | **DEFERRED** (model call) |
| DF-0.2 bare generics | none (count) | 16 constitution units, 2,433 B; 0 UDHR; classification pending | **done (count)**; classification **DEFERRED** (model call) |
| DF-0.3 baseline | none (record) | — | **DEFERRED** (RD-9 SC-9 `CE4` not on `main`) |
| DF-0.4 plain-default probe | none (expected: check passes, render refuses at `norm_english.py:398`) | check and render refused at load (`document.py:633`); post hoc with `deny`: check passes, render refuses at `:398` | **done; expectation not met** |
| DF-E3 specificity | IDE check only if ≥ 5 pairs | pre-registered: UNKNOWN (0 certain, 9 undecided); post hoc: 0 | **FAIL** (bar not met; IDE check not built) |
| DF-E1, DF-E2 | — | later batches | not in phase 1 |

## 5. Reproduce

```
uv run python research/defeasible/screen_markers.py
uv run python research/defeasible/screen_bare_generics.py
uv run python research/defeasible/probe_plain_default.py          # runs ve under prlimit --as=6442450944
prlimit --as=6442450944 uv run python research/defeasible/specificity_pairs.py
prlimit --as=6442450944 uv run python research/defeasible/resolve_unknown_directions.py   # post hoc
```

The probe and DF-E3 need the Lean service and the Rust binary at their pinned hashes (see 2, Binaries).

No product code was changed. As checks that the new `research/` files trip no repository-wide lint,
`tests/test_hang_guards.py`, `tests/test_english_e2_ledger_sites.py`, `tools/test_layer_policy.py` and
`tests/test_assurance_manifest.py` were run (`-n 4`, prebuilt binaries): 234 passed and 3 errored. The 3 errors are
one `test_assurance_manifest.py` fixture that runs `lake build` in this worktree. That build failed under the 6 GB
address-space limit, which the compiler inherits; no Lean file differs from `main`'s merge base. The full gate was
not run: there is no product change to gate. `tools/layer_policy.py` assigns no layer to `research/`, so test
selection treats these files as unknown paths, as it does for the sibling phase-1 branches' `research/<topic>/`.
