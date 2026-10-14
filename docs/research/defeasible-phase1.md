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
