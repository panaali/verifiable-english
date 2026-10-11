# Soft chain under the completion (`readings@1` × `soft-norms@0` × `norm-defaults@0`): design, statement spec draft and buildable plan (RD-9)

> Status: draft 1 (2026-10-11), branch `design/rd-9` from `main` at `8b9927f2` (RD-6b merged). This is RD-9 of
> [readings-defaults-PLAN.md](readings-defaults-PLAN.md): a design batch for the constitution's strict and default
> readings. It holds the design (sections 1 to 3), a statement spec draft (section 4), fixtures from real
> constitution units (section 5) and the build batches SC-0 to SC-11 (section 6).
>
> Read at `8b9927f2`: [readings-defaults-PLAN.md](readings-defaults-PLAN.md) (RD-6a, RD-6b, RD-7, RD-9 and D2),
> [readings-defaults.md](readings-defaults.md), [soft-norms.md](soft-norms.md) (1, 2, 4.2, 5, 6),
> [norm-defaults.md](norm-defaults.md) (2, 3.3), [composition-s1.md](composition-s1.md) (2, 9.2),
> `lean/VE/SoftNorms/{Soften,Coherence,Once}.lean`, `lean/VE/NormDefaults/{Tree,Premises,Wire,Report,Layered,Routes,
> Admission}.lean`, `lean/VE/Readings/{Doc,Choice,Route,Wire,Separate,Scan,Force,Unspecified,UnspecifiedWire,SupFill,
> Verdicts,VerdictsWire,Components}.lean`, `ve/document.py`, `ve/norm_defaults.py`, `ve/softnorms.py`,
> `ve/readings_verdicts.py`, `ve/readings_s2_wording.py`, `tests/test_norm_defaults_layered.py`,
> `docs/lean-first/b10a/DELTA.md`, `docs/lean-first/b10b/DELTA.md`, the DRI decisions D1 to D8
> (`manage-agents/arch-dri-decisions.md`), and the constitution pilot: `pilots/claude-constitution/TREND.md`,
> `pilot-translate-20261010T1800Z.final.md`, `pilot-audit-20261010T1800Z.final.md`, and the run directory
> `pilots/claude-constitution/run-20261010T1800Z/` (pilot commit `76922d6c` on `pilot/cc-20261010T1800Z`).
>
> Planning only: no code, proof or test changed, and no model was called. **The Lean statements below were not
> elaborated in this session.** Every name they use was read in the merged sources; elaborating them against a build
> of `main` is SC-0's first step, and any elaboration failure is fixed in this file, not in merged code. Fixture
> values marked *derived* were worked out by reading the sources and were not run. Numbers marked *recorded* are
> copied from the record named beside them.

## 0. Summary

The constitution says most of what it asks of Claude with "should". VE reads a "should" sentence as a reading set of
two VE sentences, a strict rule ("must") and a default rule ("should": required unless the rule's exception applies,
decided by someone the text names or does not name). The constitution also leaves most cases unsaid, so its
translation needs the `unspecified` completion (`norm-defaults@0`). Today the two cannot meet: `ve document` refuses
`norm-defaults@0` beside `soft-norms@0`, and the readings route refuses content beside `norm-defaults@0` off the
norms chain. So the constitution's four "should" sets are written on the norms chain, with the default reading faked
as a strict rule plus an `unless` over a named open term ("exception to asking for clarification"). The audits accept
that workaround as faithful, and still rank "defeasible duties with contextual exceptions" among the three most
valuable missing features (audit 20261010T1800Z, *recorded*).

This plan lets the default reading be VE's own `should` rule beside the `unspecified` completion, inside a reading
set, checked by Lean:

1. **`fill` after `soften`, per document.** Each document of the route (a reading's, the free one, a choice's) is
   read as norm-defaults reads a soft document: `fill (soften (correlate X))`, with soft's premises (`Exc_T`, and
   `Coh_T` regenerated on the filled tree) and `Fill_T` as base premises. RD-1's `choiceU N c` is already that
   document; what the soft chain adds is the extra premises `X`, which are empty on a strict document, so the norms
   chain is the instance `X = []`.
2. **Separation on filled sides.** S1's own pair check (`pairEval`) runs on each reading's filled document. The
   shared filling and the witness's `Fill_T` are readings-defaults' D4 rule, and decisions stay the readings' own
   keys (S1). For the
   strict and default readings of one rule, the readings differ exactly where the exception applies, and there the
   default reading leaves the act unsaid: the strict reading settles it, the default reading does not.
3. **Verdicts with `X`.** The fold of RD-3 is stated once over a per-choice semantics, and the norms chain's and the
   soft chain's theorems are its instances. Each choice is checked by the layered branch's own checkers with `X`.
4. **Documents through `ve document`.** The layered branch of norm-defaults gains the two kinds the soft chain needs
   (`norm-defaults-certificate`, `admission`), so soft documents under `norm-defaults@0` are admitted through
   `Layered.lean`. Lean decides which filled gaps a separation line shows. `decided_units` is reported on the
   enumerated route without companion sets, so the constitution's Lean-decided share can be read off the translation
   itself.
5. **The constitution, measured.** The four sets are rewritten with the default reading as a `should` rule on a pilot
   branch, checked and measured at one commit, and audited before the translation adopts them.

The route is the enumerated one (64 compatible choices at most). The constitution's four sets have 16 choices
(*recorded*). Superposition under the soft completion needs S2a's theorems restated over `fill ∘ soften`, not only a
carried premise family (D3). That work is off the constitution's path and comes last (SC-10, SC-11). No new English
wording is needed: one selection rule changes (D9).

## 1. Evidence

### 1.1 The constitution (recorded)

| Measure | Value | Source |
|---|---|---|
| Units; statuses | 1,132; 1 CHECKED, 39 LABELLED, 14 OPEN, 4 READINGS, 1,074 UNFORMALISED | TREND.md, run 20261010T1800Z |
| Claimed covered; audit-verified | 2,951 bytes (1.60%); 764 bytes (0.41%) | the same |
| Reading sets | 4, all "should": `force-u0036-s05`, `force-u0125-s04-p2`, `force-u0156-s03`, `force-u0263-s04-p2`, readings `strict` and `default`, each with a `source_word` span | `translation.ve.md` (run 20261010T1800Z) |
| Main document profiles | `documents@1`, `norm-defaults@0`, `norms@0`, `readings@1`, `relational-fol@0` (no `soft-norms@0`) | the same |
| The `default` readings | the strict rule plus `unless` over one named open term each (`exception_to_asking_for_clarification`, `exception_to_never_denying_being_claude`, `exception_to_not_deceiving_about_system_prompt`, `exception_to_complying_with_exploit_instruction`) | the same; FEATURE-REVIEW.md "Costs and limits" |
| Check of the translation | 16 choices, conflict-free, premises `model`, 54.6 s | FEATURE-REVIEW.md |
| Lean-decided share | translation 0.00%; the four sets rewritten as companion sets (a probe): 19 units, 2,602 bytes, 1.41% | FEATURE-REVIEW.md |
| A soft document beside `norm-defaults@0` | refused: `UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes await the Lean route` | `probes/s1-probe.json` (c); `ve/document.py:568-572` |
| Separation English on the norms chain under the completion | one separation line shows 15 filled-gap sentences, one per point of every filled table | `run-20261010T0600Z/rendered.md:268` and `:2046` |
| Earlier rejections this plan addresses | audit 20261003T0600Z rejected u0036.s05, u0073.s05, u0263.s04.p2 ("deny completions assert 'not required' outside the stated conditions") and u0156.s03 ("the defeasible companion converts an exception into 'not required'") | TREND.md |
| Top missing features, last audit | "typed permission, capability, and authority; defeasible duties with contextual exceptions; graded quantities and causal possibility without invented thresholds" | pilot-audit-20261010T1800Z.final.md |

The four regulated predicates of the sets are `unspecified`: `clarification_required(claude_instance, situation)`
(obligation), `denial_of_being_claude_permitted(claude_instance)` (permission),
`system_prompt_deception_permitted(claude_instance, user)` (permission) and
`exploit_instruction_compliance_required(claude_instance, situation)` (obligation) (`probes/unspecified-probe.json`,
its `gaps` block lists each with `completion: unspecified`). Their rules are `clarify-ambiguity` (guard
`genuine_ambiguity(situation)`), `no-denying-being-claude` (sign −, guard ⊤), `no-system-prompt-deception` (sign −,
guard ⊤) and `comply-no-exploit-instruction` (guard `explicit_instruction_against_exploits(claude_instance,
situation)`).

### 1.2 What the code does today (read at `8b9927f2`)

- **The abstention.** `Readings/Wire.lean:514` `abstention` refuses content beside `norm-defaults@0` when
  `re.chain != .norms`. `Readings/Route.lean:36` `routeOf` gives the soft and rights chains `.abstention`. S1's
  fixture K18 (K1 with `norm-defaults@0`) pins the text.
- **The layered branch exists for one document.** `NormDefaults/Layered.lean` reads a soft source as
  `U = (soften D, unspec)` with base premises `X = softLabelledU U D` (soft's `Exc_T`, and `Coh_T` whose selections
  are read on `fill U`), `BaseAdmissibleX U X` and `ConflictFreeX U X`, and answers the kinds `-elaborate`,
  `-conflict`, `-status` and `-report` (`layeredCase`). It has no `-certificate`, `-gaps` or `admission` kind
  (b10a DELTA "Not done"; b10b DELTA follow-up: "documents on these branches are still refused").
- **The readings completion reuses it per choice.** RD-2a's `choiceLayered` builds a `LayeredU` for `choiceU N c`
  with `labelled := []`, and `ndInner` answers each inner kind through `layeredCase`
  (`UnspecifiedWire.lean:440-449, 681`).
- **The recorded difference the soft chain needs.** `tests/test_norm_defaults_layered.py:52-55`: "where the exception
  holds, strict is SETTLED no and default UNDECIDED; the deny variant keeps the collapse (SETTLED no)". Lean proves
  the default side as `excepted_lifts` (`NormDefaults/Routes.lean:54`).
- **Force twins.** S1's `decisionOnly` finds the strict and default readings of one rule (`Separate.lean:481`), and
  `decision_only_sound` proves that they reach the same probe values when the exception table is empty
  (`Force.lean:1193`). The finding is shown as E25 ("not certified").
- **The fold.** RD-3's seven fold theorems are stated over `Holds N` and the norms chain's notions (`ConflictFreeU`,
  `EntailsU`, `CounterU`, `ConsistentU`). Each is a short wrapper over a row lemma that reads the fold alone
  (`Verdicts.lean:200-300`).
- **Gap sentences.** Python's `filled_gaps` (`ve/readings_s2_wording.py:567`) lists every point of every filled table
  for a separation. Verdict lines already use Lean's selection (`gapsOf`, the result's cone, RD-3).
- **Decided units.** `decided_units` is computed only on the product route of companion sets
  (`ComponentsWire.lean:564`).

### 1.3 Why the norms chain's construction does not carry over

On the norms chain RD-1 applied `fill` to the readings document itself (`fillDoc`), because `soften` is the identity
on strict rules. On the soft chain that fails twice:

- `fillDoc` gives every root rule on an unspecified `p` the parent `unsaid--p`, a strict rule. A default rule whose
  `over` names a strict rule is `SoftOverHard` (S1's K11 text). So `fillDoc` of a soft document with a default root
  on an unspecified predicate is not even well formed (fixture F-SD5).
- Inside `soften`, a strict `F_p` would block every default rule on `p` wherever no strict rule decides
  (soft-norms 4.2 step 2). That is why norm-defaults 2.3 runs `fill` last.

So on the soft chain `fill` belongs to each document of the route, after `soften`, and every check that RD-1 ran on
`fillDoc N` must run on each document's filled tree.

## 2. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | On the soft chain, `fill` runs after `soften` on each document of the route (the free one, each reading's, each choice's), never on the readings document. The document is RD-1's `asU N X = (soften (correlate X), N.unspec)` | norm-defaults 2.3's order; 1.3 | `fillDoc` on the soft chain; a synthetic default rule in place of `F_p` (it would collide with author rules and be weighed) |
| D2 | Each document carries extra base premises `X`: soft's `Exc_T`, then `Coh_T` regenerated on its filled tree, by the layered branch's one definition (`softLabelledU`). `Fill_T` comes after `X`, as `LayeredU.background` orders them. On a strict document `X = []` (`softX_strict`), so every soft-chain statement here is the norms chain's at `X = []` | norm-defaults 3.3: `Coh_T`'s selections read unsaid atoms where guards mention unspecified predicates; soft's own `Coh_T` reads the placeholder `deny` (`test_coherence_is_regenerated_on_the_filled_tree`) | soft's own `Coh_T`, which would decide gaps by the invented `deny` |
| D3 | The enumerated route only, at most 64 compatible choices per document, with `ReadingsNotSuperposable: <sets>` and cause `the unspecified completion` (E29). Superposition under the soft completion is SC-10 and SC-11, off the constitution's path | the constitution has 16 choices (*recorded*). RD-6a's `Transfers` carries a premise family through S2a's theorems about `soften (sup)`. Under the soft completion the conflict targets are those of `fill (soften (sup))`, which differ from `soften (sup)`'s wherever a guard reads a lower gap. So S2a's theorems must be restated over `fill ∘ soften` (a `fill_sim` lemma), not only given `X ++ Fill_T` as a family | superposition first; RD-6a's `Transfers` alone (the readings-defaults plan's RD-9 sketch) |
| D4 | Separation runs S1's pair check (`pairEval`) on **filled sides**: S1's `Side` with the reading's filled tree `fill (asU N X)` and its layers in place of `soften (correlate X)`. The base is over the filled author vocabulary, and its `unsaid__` tables are the shared filling (readings-defaults D4). Decision tables stay the readings' own keys (S1 1.5). The witness's `Fill_T` is checked on its own completion | one pair check for every chain; readings-defaults D4 and S1's key ownership unchanged | a second pair check for the soft chain |
| D5 | Force twins keep S1's finding (`decisionOnly`, unchanged). Under the completion the twins differ exactly where the exception applies (`decision_only_soundS`), and there the default reading leaves the act unsaid (`excepted_lifts`, already proved): the strict reading settles the point, the default reading answers UNDECIDED. The finding's wording follows S1's rule (E25 while S1 shows E25; E15 only when the DRI signs S1's flip and `decision_only_soundS` is proved) | this is the content of the constitution's "should" sets, and it removes the "not required" that the deny completion invented (audit 20261003T0600Z) | a "should"-specific sentence |
| D6 | One fold over a per-choice semantics (`ChoiceSem`). RD-3's seven fold theorems become one-line instances (`ndSem`, statements unchanged), and the soft chain's are instances too (`sdSem`) | one owner of fold soundness | seven copied fold theorems for the soft chain |
| D7 | One per-choice evidence structure with `X` (`XEvidence`). RD-3's `NDEvidence N c` becomes `XEvidence (choiceU N c) []`, and its row functions become this structure's at `X = []`. One choice-source builder (`choiceLayeredG`) serves both chains | one owner; `X = []` adds no premise byte, so the norms chain stays byte-identical (A/B) | a soft copy of RD-2a's and RD-3's per-choice code |
| D8 | The layered branch gains its two missing kinds that the soft chain uses: `norm-defaults-certificate` (`EntailsX`, `acceptanceX`) and `admission` (claim graphs with soft and fill leaves). Soft documents under `norm-defaults@0` are then admitted through `Layered.lean`, as b10b's follow-up asks. `ve document`'s refusal stays for the rights route only | the constitution's main document has a claim graph (root `¬human(claude)`, unit u0248, *recorded*), and Python must not build `fill` | Python soft-fill code; keeping the refusal |
| D9 | A separation line under the completion (both chains) shows one filled-gap sentence per gap in the cone of the witness's shown value, selected by Lean (`gapsOf`, as RD-3's verdict lines already are). Python's enumeration (`filled_gaps`) is deleted | Lean selects and Python renders (D1 of the DRI decisions; lean-first rule 1). The constitution's separation lines show 15 gap sentences, 14 of them about other acts (*recorded*). Zero-training English: precision machinery stays out of sight unless the result depends on it | keeping Python's list of every point |
| D10 | `decided_units` on the enumerated route without companion sets: the main case as the one component, by readings-defaults 1.10's rule (`partDecided`) | the pilot's ask ("decided units reported for documents without companion sets", FEATURE-REVIEW.md); the share is otherwise 0.00% on the translation itself, whatever Lean checks | measuring through companion probes only |
| D11 | Out of scope, each kept with today's text: the rights chain under the completion (the abstention), readings with their own vocabulary on the soft chain (RD-4a's refusal), the superposed route under the soft completion (SC-10, SC-11) | scope: the constitution needs none of them | — |
| D12 | No new wording. E14 with its `<decision>` slot ("suppose the decider decides the exception applies to c"), E15 or E25, E12 with R2, R3 and R7, E3 lines (soft's exception and coherence sentences for used soft labels), E29 and the filled-gap sentence cover every answer here | each has one reading and passes W7's gate already | new "should" sentences |

## 3. Design

### 3.1 Where this applies

A document is **under the soft completion** when its environment's profiles contain `readings@1`, `soft-norms@0`
and `norm-defaults@0`, its chain is the soft chain (no `rights@0`), and some reading set has a candidate with
content. For such a document, `routeOf`'s abstention row becomes the enumerated row (D3). Every other document keeps
its route. A soft document under `norm-defaults@0` without reading content takes the W2 route through the layered
branch (3.8), where it is refused today.

### 3.2 One document of the route

For a readings document `N` (RD-1's `NDoc`: the decoded `Doc` and the frame's unspecified predicates) and any
document `X` of the route (`free N.D`, `one N.D s i`, `choiceDoc N.D c`):

- the **norm-defaults document** is `asU N X = (soften (correlate X), N.unspec)` (RD-1), filled as `fill (asU N X)`;
- the **extra base premises** are `softX N X`: soft's `Exc_T`, then `Coh_T` with each selection read on
  `fill (asU N X)`, by `softLabelledU`, the layered branch's definition (labels `soft:exception:<rule>:<kind>:<i>` and
  `soft:coherence:<a>,<b>`);
- **admissible bases** are `BaseAdmissibleX (asU N X) (softX N X)`: W1's base admissibility on the filled tree,
  `Fill_T`, and `softX N X`;
- **CONFLICT-FREE** is `ConflictFreeX (asU N X) (softX N X)`, **entailment** is `EntailsX` (new, 4.2), and a
  **countermodel** or **model** is an admissible filled situation where the premises hold (`CounterX`,
  `ConsistentX`, new, 4.4).

`softX N X = []` when `X` has only strict rules and no rights block (`softX_strict`): `Exc_T` comes from default
rules only, and `Coh_T` from colliding pairs of default rules only. Hence on the norms chain `choiceX N c = []`
(`choiceX_normsShaped`), and RD-2a's and RD-3's checks are this design's checks at `X = []`.

### 3.3 Admission, stopping at the first error

1. S1's and S2a's admission on `N.D` as today, on the soft chain, with each `unspecified` read as the placeholder
   `deny` (DRI ruling 4). The abstention no longer applies to the soft chain.
2. Reserved names: a unit id, rule name or declared name beginning `unsaid--` is `InvalidInput: reserved name <n>`
   (RD's step 2, `reservedUnsaid`, unchanged).
3. For the free document, then each reading's document with content in set and index order: norm-defaults' author
   checks (`checkAuthorN`, its texts and order), counting that document's generated decision predicates as the
   layered branch counts them (`(decisions (correlate X)).length`), then `WellFormedU`
   (`InvalidInput: norm-defaults document is not well formed`). A reading's text carries ` under <set>@<v>:<i>`.
4. No fourth step. On the norms chain step 4 ran S1's checks on `fillDoc N`. On the soft chain there is no filled
   readings document, and the layered branch checks no limit on a filled tree beyond `checkAuthorN`'s (open question
   Q1).
5. Each compatible choice, when they number at most 64, in canonical order: S2a's chain text on the choice
   (`choiceChainText N.D c`), then step 3's checks on `choiceU N c` with its decision count, suffixed
   ` under <choice>`. `replayChoiceS` runs the same checks on its own choice.

`AdmittedSD` carries `WellFormedSD N`: S1's `WellFormedDoc`, `softShaped`, `fillNamesFree`, and `WellFormedU` of the
free document and of each reading's document.

### 3.4 Separation

A situation's base is over the filled author vocabulary (`authorEnv (fillDoc N)`, which reads only `fillDoc`'s frame:
the frame with every `unsaid__p` added). Its `unsaid__` tables are the shared filling. Its `fixed` and `decisions`
tables are S1's: shared generated keys and the witness's own keys.

Each reading has a **filled side** `sideOfS N (one N.D s i)`: S1's `Side` record with `S := fill (asU N X)`, its layers
and its hidden environment. S1's executable functions read a side and nothing else. On a filled side,
`backgroundValidOn` evaluates the filled tree's base background and soft's premises built on the filled tree, which
are `softX N X` (`softPremisesIn_fill`), and `observeOn` evaluates the probe on the filled tree. `separatesS` is
S1's pair check (`pairEval`, the function the route runs) on the two filled sides, with the other reading's cells
within `maxCells`, and with the witness's `Fill_T` true on its own completion (`fillHoldsS`). `separatesS_sound` gives
`AchievesS` for the witness and its negation for the other reading.

The other reading's `Fill_T` is not evaluated by the check. That is sound: a completion of the other reading that
fails its `Fill_T` is not admissible in `AchievesS`, so ruling out every completion without it rules out every
admissible one. It is the readings-defaults D4 rule, unchanged.

*Derived example* (fixture F-SD1, S1's K1 with `avoid_required` unspecified). Readings: strict `must avoid deceiving`,
default `should avoid deceiving`, decided by `unstated`. Base: one agent `a`, one user `u`, empty filling. The
default reading's decision table `excepted no-deception = {(a, u)}`. The probe is the outcome of `avoid_required` at
`(a, u)`, value false, with the default reading as witness. Under the default reading the rule is excepted and no
rule decides, so the filling answers: no. Under the strict reading the rule applies, so the value is true. Separated.
With the filling `{(a, u)}`, the default reading reaches true, and nothing separates the pair with value false.

### 3.5 Force twins: the strict and default readings of one rule

S1's finding `SeparatedByDecisionOnly` is computed from the documents (`decisionOnly`) and does not change. Under the
completion:

- **They differ only where the exception applies** (`decision_only_soundS`, SC-3): with the default twin's exception
  table empty, the two readings reach the same probe values on every base and filling. It is `decision_only_sound`
  for filled sides. Its proof adds one step to S1's: `fill` reads only the author rules' decisions
  (`fill_soft_value`), and those agree off the exception (`Twin.decides`).
- **Where it applies, the default reading leaves the act unsaid**: `excepted_lifts` (merged) applied to
  `oneU N s j`, which is `(soften (correlate (one N.D s j).1), N.unspec)`, so it needs no new statement. The
  per-choice status replay shows it: strict SETTLED, default UNDECIDED (fixture C1.4).

The English is E14 with S1's `<decision>` slot. A separation line under the completion adds the one filled-gap
sentence the witness's value depends on (D9). On F-SD1, *derived*: "This sentence says *should*. (1) *Every agent
must avoid deceiving each user.* (2) *Every agent should avoid deceiving each user.* They differ here: suppose the
decider decides the exception applies to a and u. Here the text does not say whether a must avoid deceiving u; this
situation answers 'no'. Under (1) a still must. Under (2) a is not required to." The finding's sentence (E25 or E15)
follows, as D5 says.

### 3.6 Each choice

For each compatible choice, at most 64, Lean regenerates `choiceU N c` and builds its layered source with
`choiceLayeredG`. The route is `soft-norms@0` and the labelled premises are `softXL N (choiceDoc N.D c).1`. The
situation vocabulary is the soft branch's prime vocabulary (base and decision predicates). Packages are bound to the
case's environment id, the choice's document hash (`choiceHash`) and `E‴_base` with the decisions
(`withUnsaid (basePrimeJson …)`). The inner kinds of `readings-choice`:

| Inner kind | Lean check | Theorem it rests on |
|---|---|---|
| `norm-defaults-elaborate`, `-conflict` (packages or a filled witness), `-status`, `-report` | `layeredCase L` (unchanged dispatch) | `layered_conflict_sound`; a witness's proof carried by `witnessConflictX` (`target_not_conflictFree`); `StatusX`'s `sound₁` and `sound₂`; `layered_report_sound` |
| `norm-defaults-certificate` (needs the choice's conflict packages) | `checkCertificate` over `premisesX U L.X ((choiceDoc N.D c).2 ++ Γ)` | `acceptanceX` |
| `choice-model` (a base model with decisions and a separate `filling`) | `modelCheckX U L.X` | `modelCheckX_sound` |

RD-2a's `ndCertificate` and `ndChoiceModel` become these checks. With `L.X = []` on the norms chain, their premise
lists and model checks are the same bytes and values as today.

### 3.7 Verdicts across readings

`readings-verdicts` under the soft completion is RD-3's kind with `X`: Lean enumerates the compatible choices taking
`assumed` (at most 64; beyond that W2's budget answer and E28), decodes each choice's evidence (`XEvidence`) on its
own layered source, computes the rows, and folds with RD-3's unchanged `foldConflict`, `foldEntailment` (with its
conflict gate) and `foldPremises`. The rows hold of `sdSem N` (`x_rowsHold`), so the generic fold theorems give the
wire theorems `readings_wire_sd_verdicts_*`.

Conditions: `restrictionsFor` is unchanged. `usedLabels` drops slot, `Fill_T` and soft labels in label order. The E3
line for a used `soft:exception:<rule>:<kind>:<i>` label is soft-norms 2.1's exception-condition sentence, and for a
used `soft:coherence:<a>,<b>` label it is soft-norms 2.3's weighing-point sentence for that pair. Both are existing
wording.

### 3.8 Documents through `ve document`

- **The refusal.** `ve/document.py:568` keeps refusing `norm-defaults@0` on the rights route. On the soft route the
  document loads, with the text changed to name the rights route only (a diagnostic text change, listed in DELTA).
- **No Python fill and no Python soft premises under the completion.** As on the norms chain under the completion,
  where `norms` is `None`, Python adds no layer or soft premise of its own to a premise set. The premise status of a
  document with content-bearing sets is the readings route's (Lean). A plain soft document under `norm-defaults@0`
  takes its premises from Lean's layered elaboration: the filled layers, `softX`, then `Fill_T`.
- **Claim graphs.** The claim graph goes to the layered branch's new `admission` kind (SC-6). Its leaves may name a
  regenerated layer premise of the filled tree, a regenerated soft premise on it, a pair premise or a `Fill_T` premise.
- **Report and coverage.** These come from the layered `norm-defaults-report`, which exists. The containers in
  `ve/norm_defaults.py` and `ve/softnorms.py` read Lean's layered row for display.

### 3.9 English

No new wording (D12). What changes:

- **The `<reading>` slot.** On the constitution's sets the candidates differ only in the verb, so readings-defaults
  A4 keeps the italic verb: *must not* against *should not* (*derived*).
- **Separation lines (D9, both chains under the completion).** After the shown situation comes exactly one filled-gap
  sentence per gap in the cone of the witness's shown value, and none for a gap outside it. Lean computes the list
  per pair (`gaps`: predicate, tuple, value) with `gapsOf` on the witness's filled document. Python renders it. On
  the constitution this replaces 15 sentences by one (*derived*, fixture F-SD10). This is a selection change on the
  norms chain's English as well, so it is a signed `wording` change in DELTA.
- **Verdict lines.** Unchanged rules (RD-3). A countermodel under a default reading shows its decision with S1's
  `<decision>` slot and its filled gaps by the cone. Example on C1, *derived*: "Read sentence *n* as *should not*:
  the conclusion does not follow. It fails here: c is an instance of Claude; suppose the decider decides the
  exception applies to c. Here the text does not say whether c may directly deny being Claude; this situation
  answers 'yes'."
- **Non-wordings,** beyond readings-defaults 2.5: any `soft__` name, an exception predicate's name, "excepted",
  "default rule".

### 3.10 Wire and identity

- `readings-validate` and `readings-separate` under the soft completion answer S1's rows, computed on filled sides,
  with these additions. Per reading: `fill_premises` (RD's labels) and `soft_premises` (`softXL`: label and AST, on
  the reading's filled tree). Per pair: `gaps` (D9). Once: `filled`, which holds `environment`, the lower
  environment with `unspecified` read as `deny`, `norm-defaults@0` removed and each `unsaid__p` added (10a's
  `withUnsaid`), and `units`, the document's units as decoded. No `F_p` unit is listed on the soft chain: `F_p` is a
  rule of each document's filled tree, not a unit. On the norms chain `gaps` is added beside today's fields.
- `readings-elaborate`: the enumerated row with the finding `ReadingsNotSuperposable: <every open set>` and cause
  `the unspecified completion`.
- `readings-choice`: the inner kinds of 3.6.
- `readings-verdicts`: RD-3's request and answer. `decided_units` is added on the enumerated route without
  components, on both chains (D10).
- Layered branch (`norm-defaults` route): `norm-defaults-certificate` and `admission` on the soft branch. The rights
  branch keeps refusing them with `runLayered`'s existing text.

Identity: nothing changes. Each filled document, its `X`, every compatible choice and every layered source are
regenerated from the decoded document at every trusted site and bound to the chain's document hash (DRI D7: Lean owns
meaning, environment, document hash and report identities). Certificates and models are evidence, checked against the
regenerated premises (DRI D1: Python recomputes no derived value).

### 3.11 Diagnostics, in order

| # | Text | When |
|---|---|---|
| 1 | S1's and S2a's admission texts on the soft chain | as today (3.3 step 1) |
| 2 | `InvalidInput: reserved name <n>` | a unit id, rule name or declared name begins `unsaid--` (step 2) |
| 3 | `checkAuthorN`'s texts in its order, then `InvalidInput: norm-defaults document is not well formed`, a reading's suffixed ` under <set>@<v>:<i>` | the free document, then each reading's (step 3); `ResourceLimit: vocabulary size` counts that document's decision predicates (F-SD7) |
| 4 | S2a's chain text on the choice, then row 3's texts on `choiceU N c`, suffixed ` under <choice>` | each compatible choice, at most 64 (step 5) |
| 5 | `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` | the rights chain (unchanged) |
| 6 | `UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented` | a companion on the soft chain (RD-4a, unchanged) |
| 7 | `UnsupportedProfile: norm-defaults@0 documents on the rights route await the Lean route` | `ve document` on the rights route (text narrowed from "soft and rights routes") |
| 8 | S1's situation texts (`invalid situation <id>`, `distinguishing model violates a generated premise`) | a separation's base names a decision predicate, or the witness's `Fill_T` fails (`fillHoldsS`) |
| 9 | `ReadingsUnsatisfiable: no compatible reading takes <choice>` | RD-3, unchanged |

When AR-13's `Code` enumeration lands (DRI D6), each text gets its code, with the text unchanged.

### 3.12 Limits

As readings-defaults 3.8, with one change: the vocabulary limit of `checkAuthorN` (declared predicates plus generated
plus unspecified, at most 256) counts each document's own decision predicates. Compatible choices checked one at a
time: 64. Cells of the other reading's owned tables: 12 (S1). Unsaid atoms in a status enumeration: 12
(`MAX_UNSAID_ATOMS`). Rules plus unspecified predicates: 256 per document, choices included. AST nodes with the `F_p`
guards: 10,000 per document. That count includes soft's derived carve-outs, as on the layered branch.

### 3.13 One owner per piece of logic

| Logic | Owner | Python |
|---|---|---|
| `soften`, `fill`, `Exc_T`, `Coh_T` on the filled tree, `Fill_T` | Lean (`SoftNorms`, `NormDefaults`, `softLabelledU`) | none |
| Admission under the soft completion | Lean `admitSD` | relays the text |
| Separation (pair check, filled sides, witness's `Fill_T`) | Lean `pairEval` on `sideOfS`, `fillHoldsS` | proposes situations (decision tables and filling) over Lean's rows |
| Per-choice checks with `X` | Lean `layeredCase`, `acceptanceX`, `modelCheckX` | proposes certificates, packages, witnesses and models over Lean's formulas |
| Fold, gate, conditions, wording selection, gap selection, decided units | Lean (`foldG_*`, `restrictionsFor`, `usedLabels`, `englishPlan`, `gapsOf`, `partDecided`) | renders |
| Documents and claim graphs under the soft completion | Lean layered branch (`admission`, `-certificate`, `-report`) | loads files, relays |
| Files, CLI, rendering, the constitution migration | Python and pilot tooling | — |

### 3.14 Conservativity

- **Soft completion support (SC-4, SC-5).** Only a document under the soft completion (3.1) reaches it. Such a
  document reached the abstention before, so the change is an `availability` change (K18 becomes admitted with K1's
  answers, F-SD2). Documents on the soft chain without `norm-defaults@0` keep S2a's route and answers. The rights
  chain keeps the abstention.
- **Consolidation (SC-1, SC-4, SC-5).** RD-3's fold theorems, `NDEvidence` and its row functions, `ndDocText`, and
  RD-2a's `choiceLayered`, `ndCertificate` and `ndChoiceModel` become instances at `X = []` or at zero decisions.
  Statements are unchanged, and every norms-chain answer is byte-identical (the A/B claim of those batches;
  F-ND0 to F-ND10, M1 to M20).
- **Layered kinds (SC-6) and `ve document` (SC-8).** Only soft documents under `norm-defaults@0` reach them, and they
  were refused before.
- **Wording (SC-8).** The gap selection of separation lines changes the English of documents under the completion on
  both chains (D9), a signed `wording` change. `decided_units` without components (SC-7) adds a field to every
  enumerated-route answer, a signed `field added` change. Verdicts are byte-identical.
- No frozen file, canonical byte, existing identity or approved theorem statement changes. New statements go in new
  files. Definitions that change (`abstention`, `routeOf`, `underCompletion`'s callers, `layeredCase`, the
  consolidated definitions) change no statement. `Layered.lean` is a pinned decoder: its re-pin and the
  frozen-inventory update are part of SC-6 (DRI D2).

## 4. Statement spec draft (Lean)

Not elaborated in this session (status block). Each block is meant to be elaborated as written inside its namespace;
SC-0 records every change.

### 4.1 Files and placement

| Batch | File | Declarations |
|---|---|---|
| SC-1 | `lean/VE/NormDefaults/LayeredEntail.lean` (new) | 4.2 |
| SC-1 | `lean/VE/Readings/SoftDefaults.lean` (new) | 4.3 |
| SC-1 | `lean/VE/Readings/VerdictsGen.lean` (new); `Verdicts.lean`'s fold proofs re-proved as instances | 4.4 |
| SC-2 | `lean/VE/Readings/SoftSeparate.lean` (new), `SoftSeparateExamples.lean` (new, `#guard`s) | 4.5 |
| SC-3 | `lean/VE/Readings/SoftForce.lean` (new) | 4.6 |
| SC-4 | `lean/VE/Readings/SoftWire.lean` (new); definition changes in `Readings/Wire.lean` (`abstention`), `Readings/Route.lean` (`routeOf`), `UnspecifiedWire.lean` (`choiceLayered`, `ndDocText`, `ndCertificate`, `ndChoiceModel` as instances) | 4.7 |
| SC-5 | `lean/VE/Readings/SoftVerdicts.lean` (new); `VerdictsWire.lean`'s `NDEvidence` and row functions as instances | 4.8 |
| SC-6 | `lean/VE/NormDefaults/LayeredAdmission.lean` (new); `layeredCase` gains two kinds | 4.9 |
| SC-7 | `lean/VE/Readings/VerdictsWire.lean` (the answer's `decided_units`) | 4.10 |
| SC-10 | `lean/VE/Readings/SoftSup.lean` (new; sketch only, re-reviewed before its build) | 4.11 |

### 4.2 SC-1: entailment and models with `X` (`VE.NormDefaults`)

```lean
import VE.NormDefaults.Layered

namespace VE.NormDefaults
open VE.Norms
universe u

/-- The premises a certificate on a document of the layered branch binds: the filled document's background, the
    route's extra base premises `X` (soft's, then rights'), `Fill_T`, the filled layers, then `Γ`. This is
    `premisesU` with `X` placed where `LayeredU.background` places it in the base (soft, rights, norm-defaults). -/
def Wire.premisesX (U : UDoc) (X Γ : List VE.Formula) : List VE.Formula :=
  background (fill U) ++ X ++ fillPremises U ++ elaborate (fill U).T ++ Γ

theorem Wire.premisesX_nil (U : UDoc) (Γ : List VE.Formula) : Wire.premisesX U [] Γ = Wire.premisesU U Γ

/-- Entailment on a filled document whose admissible bases also satisfy the route's extra base premises `X`. -/
def EntailsX (U : UDoc) (X Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) →
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

theorem entailsX_nil (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U [] Γ φ ↔ EntailsU.{u} U Γ φ
theorem conflictFreeX_nil (U : UDoc) : Wire.ConflictFreeX.{u} U [] ↔ ConflictFreeU.{u} U

/-- `acceptanceU` with `X`: a certificate over `premisesX` proves entailment over every admissible base that also
    satisfies `X`, each formula of `X` closed over the filled base vocabulary. -/
theorem acceptanceX (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesX U X Γ) φ cert = true) :
    EntailsX.{u} U X Γ φ

/-- `modelCheckU` with `X` evaluated on the filled model. -/
def modelCheckX (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula) : Bool × Bool :=
  ((modelCheckU U M F Γ φ).1 && Wire.extraValid U X M F, (modelCheckU U M F Γ φ).2)

theorem modelCheckX_sound (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0)) (F : FiniteFill U VE.Bridge.Entity)
    (Γ : List VE.Formula) (φ : VE.Formula) (hm : (modelCheckX U X M F Γ φ).1 = true) :
    Wire.BaseAdmissibleX U X (withFill U M.asStructure (finFill M F)) ∧
    (∀ a ∈ Γ, (subst (fill U).T (size (fill U)) a).denote (withFill U M.asStructure (finFill M F)) []) ∧
    ((subst (fill U).T (size (fill U)) φ).denote (withFill U M.asStructure (finFill M F)) [] ↔
      (modelCheckX U X M F Γ φ).2 = true)
end VE.NormDefaults
```

Proof notes. `acceptanceX` is `acceptance_of_fillTyped`'s proof with `X` among the premises. `X` holds at the base by
`BaseAdmissibleX`, and holds in `S` because it is closed over the base vocabulary (`hX`; restriction lemma of W1).
`modelCheckX_sound` is `modelCheckU_sound` and `eval_withFill` on `X`. The `_nil` theorems follow from
`Sat B [] = True` and `List.append_nil`.

### 4.3 SC-1: the soft chain's documents (`VE.Readings`)

```lean
import VE.Readings.Unspecified
import VE.NormDefaults.LayeredEntail

namespace VE.Readings
open VE.Norms (envAt)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

def contentSoft : Content → Bool
  | .assertion _ => true
  | .norm _ => true
  | _ => false
/-- What the soft chain's decoder guarantees of a readings document: the soft chain, no rule and no rights block in
    the frame, every content an assertion or a rule (strict or default, with parties, ranks and exceptions). -/
def softShaped (D : Doc) : Bool :=
  D.chain == .soft && D.frame.soft.T.nodes.isEmpty && noRights D.frame &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => contentSoft c
    | .bar _ _ => false
    | .set R => R.candidates.all (fun a => (a.content.map contentSoft).getD true))

/-- A document of the route's extra base premises under the completion, labelled: soft's `Exc_T`, then `Coh_T` with
    each selection read on `fill (asU N X)` (norm-defaults 3.3), by the layered branch's own `softLabelledU`. -/
def softXL (N : NDoc) (X : RightsDoc) : List (String × VE.Formula) :=
  VE.NormDefaults.Wire.softLabelledU (asU N X) (correlate X)
def softX (N : NDoc) (X : RightsDoc) : List VE.Formula := (softXL N X).map (·.2)
def freeX (N : NDoc) : List VE.Formula := softX N (free N.D).1
def oneX (N : NDoc) (s : String) (i : Nat) : List VE.Formula := softX N (one N.D s i).1
def choiceX (N : NDoc) (c : Choice) : List VE.Formula := softX N (choiceDoc N.D c).1

/-- On a strict document there is no exception and no colliding pair of default rules: `X` is empty. -/
theorem softX_strict (N : NDoc) (X : RightsDoc) (hr : noRights X = true) (hs : allStrict X = true) :
    softX N X = []
/-- So on the norms chain every choice's `X` is empty, and the soft chain's statements are RD-2a's and RD-3's. -/
theorem choiceX_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) : choiceX N c = []
theorem softX_wellFormed (N : NDoc) (X : RightsDoc) (hs : VE.SoftNorms.WellFormedSoft (correlate X) = true)
    (hw : VE.NormDefaults.WellFormedU (asU N X) = true) :
    ∀ a ∈ softX N X, a.WellFormed (envAt (VE.NormDefaults.fill (asU N X)) 0) []

/-- Admitted under the soft completion: S1's well-formedness, the soft chain's shape, the names `fill` adds free, and
    norm-defaults' `WellFormedU` on the free document and on every reading's document with content. The last three
    conjuncts are RD-2a's `ndRest` without `normsShaped`; SC-1 states `ndRest` through them (one definition). -/
def WellFormedSD (N : NDoc) : Bool :=
  WellFormedDoc N.D && softShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))
end VE.Readings
```

`softX_strict`: `noRights X` gives `correlate X = X.soft` (`correlate_noRights`). Every node strict gives
`excPremises = []` and `excLabels = []` (both come from default nodes only) and `collidingPairs = []` (pairs of default
rules only).

### 4.4 SC-1: one fold over a per-choice semantics (`VE.Readings`)

```lean
namespace VE.Readings
open VE.Norms (Sat restrictAll DocumentExpansion)
open VE.NormDefaults (UDoc fill EntailsU)
universe u

/-- What a per-choice result claims, for one reading of the choices' documents: compatibility, conflict freedom and
    its failure (read at universe 0, as `Layered.lean`'s witnesses are), entailment of a conclusion from the choice's
    assertions and `Γ`, a countermodel, and a model of the assertions. -/
structure ChoiceSem where
  compat : Choice → Prop
  free : Choice → Prop
  notFree : Choice → Prop
  entails : Choice → List VE.Formula → VE.Formula → Prop
  counter : Choice → List VE.Formula → VE.Formula → Prop
  consistent : Choice → Prop

def HoldsG (S : ChoiceSem) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) : ChoiceResult → Prop
  | .proved => S.free c ∧ S.entails c Γ φ
  | .refuted => S.counter c Γ φ
  | .free => S.free c
  | .conflict => S.notFree c
  | .model => S.consistent c
  | .inconsistent => S.free c ∧ S.entails c [] .bottom
  | .unknown => True
def CoversG (S : ChoiceSem) (A : Choice) (rs : List (Choice × ChoiceResult)) : Prop :=
  ∀ c, (S.compat c ∧ ∀ x ∈ A, x ∈ c) ↔ c ∈ rs.map (·.1)
def RowsHoldG (S : ChoiceSem) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) : Prop :=
  CoversG S A cs ∧ CoversG S A rs ∧ (∀ x ∈ cs, HoldsG S [] .bottom x.1 x.2) ∧ ∀ x ∈ rs, HoldsG S Γ φ x.1 x.2

theorem foldG_all_sound (S : ChoiceSem) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHoldG S A Γ φ cs rs) (h : foldEntailment cs rs = .all) :
    ∀ c, S.compat c → (∀ x ∈ A, x ∈ c) → S.free c ∧ S.entails c Γ φ
theorem foldG_none_sound (S : ChoiceSem) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHoldG S A Γ φ cs rs) (h : foldEntailment cs rs = .none) :
    ∀ c, S.compat c → (∀ x ∈ A, x ∈ c) → S.free c ∧ S.counter c Γ φ
theorem foldG_some_sound (S : ChoiceSem) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHoldG S A Γ φ cs rs) (h : foldEntailment cs rs = .some) :
    (∀ c, S.compat c → (∀ x ∈ A, x ∈ c) → S.free c) ∧
    (∃ c, S.compat c ∧ (∀ x ∈ A, x ∈ c) ∧ S.entails c Γ φ) ∧
    (∃ c, S.compat c ∧ (∀ x ∈ A, x ∈ c) ∧ S.counter c Γ φ)
theorem foldG_conflict_free_sound (S : ChoiceSem) (A : Choice) (cs : List (Choice × ChoiceResult))
    (hc : CoversG S A cs) (hr : ∀ x ∈ cs, HoldsG S [] .bottom x.1 x.2) (h : foldConflict cs = .free) :
    ∀ c, S.compat c → (∀ x ∈ A, x ∈ c) → S.free c
theorem foldG_conflict_sound (S : ChoiceSem) (A : Choice) (cs : List (Choice × ChoiceResult))
    (hc : CoversG S A cs) (hr : ∀ x ∈ cs, HoldsG S [] .bottom x.1 x.2) (h : foldConflict cs = .conflict) :
    ∃ c, S.compat c ∧ (∀ x ∈ A, x ∈ c) ∧ S.notFree c
theorem foldG_premises_model_sound (S : ChoiceSem) (A : Choice) (ps : List (Choice × ChoiceResult))
    (hc : CoversG S A ps) (hr : ∀ x ∈ ps, HoldsG S [] .bottom x.1 x.2) (h : foldPremises ps = .model) :
    ∃ c, S.compat c ∧ (∀ x ∈ A, x ∈ c) ∧ S.consistent c
theorem foldG_premises_inconsistent_sound (S : ChoiceSem) (A : Choice) (ps : List (Choice × ChoiceResult))
    (hc : CoversG S A ps) (hr : ∀ x ∈ ps, HoldsG S [] .bottom x.1 x.2) (h : foldPremises ps = .inconsistent) :
    ∀ c, S.compat c → (∀ x ∈ A, x ∈ c) → S.free c ∧ S.entails c [] .bottom

/-- A countermodel and a model of a filled document whose bases also satisfy `X` (RD-3's `CounterU`, `ConsistentU`
    at `X = []`). -/
def CounterX (U : UDoc) (X Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0}, VE.NormDefaults.Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) ∧
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S ∧ Sat S Γ ∧ ¬ φ.denote S []
def ConsistentX (U : UDoc) (X Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0}, VE.NormDefaults.Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) ∧
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S ∧ Sat S Γ
theorem counterX_nil (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : CounterX U [] Γ φ ↔ CounterU U Γ φ
theorem consistentX_nil (U : UDoc) (Γ : List VE.Formula) : ConsistentX U [] Γ ↔ ConsistentU U Γ

/-- RD-3's semantics: `Holds N` and `Covers N` are `HoldsG (ndSem N)` and `CoversG (ndSem N)`. -/
def ndSem (N : NDoc) : ChoiceSem where
  compat c := Compatible N.D c
  free c := VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
  notFree c := ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
  entails c Γ φ := EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  counter c Γ φ := CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  consistent c := ConsistentU (choiceU N c) (choiceDoc N.D c).2
theorem holds_iff_holdsG (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) (r : ChoiceResult) :
    Holds.{u} N Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r
theorem covers_iff_coversG (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) :
    Covers N A rs ↔ CoversG (ndSem.{u} N) A rs

/-- The semantics with an extra base-premise family `Xf`: the soft chain's is `xSem N (choiceX N)`. -/
def xSem (N : NDoc) (Xf : Choice → List VE.Formula) : ChoiceSem where
  compat c := Compatible N.D c
  free c := VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU N c) (Xf c)
  notFree c := ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU N c) (Xf c)
  entails c Γ φ := VE.NormDefaults.EntailsX.{u} (choiceU N c) (Xf c) ((choiceDoc N.D c).2 ++ Γ) φ
  counter c Γ φ := CounterX (choiceU N c) (Xf c) ((choiceDoc N.D c).2 ++ Γ) φ
  consistent c := ConsistentX (choiceU N c) (Xf c) (choiceDoc N.D c).2
def sdSem (N : NDoc) : ChoiceSem := xSem.{u} N (choiceX N)

/-- With no extra premise the two semantics agree (`conflictFreeX_nil`, `entailsX_nil`, `counterX_nil`,
    `consistentX_nil`); on a norms-shaped document `sdSem` is that case (`choiceX_normsShaped`). -/
theorem xSem_nil (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) (r : ChoiceResult) :
    HoldsG (xSem.{u} N (fun _ => [])) Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r
theorem sdSem_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (c : Choice) (r : ChoiceResult) :
    HoldsG (sdSem.{u} N) Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r
end VE.Readings
```

RD-3's `fold_*_sound` keep their statements. Each proof becomes `foldG_*_sound (ndSem N)` through `holds_iff_holdsG`
and `covers_iff_coversG`, so the fold soundness is proved once. `holds_iff_holdsG` is `Iff.rfl` on every case except
`.inconsistent`, where `List.append_nil` rewrites `(choiceDoc N.D c).2 ++ []`.

### 4.5 SC-2: separation on filled sides (`VE.Readings`)

```lean
import VE.Readings.SoftDefaults
import VE.Readings.Scan

namespace VE.Readings
open VE.Norms (Regulated tupleVal envAt)
open VE.SoftNorms (SoftNode canon)
open VE.Rights (RightsDoc correlate)
universe u

/-- A reading's filled side: S1's side with the document's filled tree `fill (asU N X)` in place of
    `soften (correlate X)`, its layers and its base environment, where `unsaid__p` and the decision predicates are base
    predicates. S1's checks (`sideValidOn`, `sideValueOn`, `pairEval`) read it unchanged. -/
def sideOfS (N : NDoc) (X : RightsDoc × List VE.Formula) : Side :=
  let S := VE.NormDefaults.fill (asU N X.1)
  let L := VE.Norms.layersOf S
  ⟨X.1, X.2, genKeys X.1, S, L, VE.Norms.hide S.E L.names⟩

/-- `backgroundValidOn` on a filled side evaluates exactly the document's `X`. -/
theorem softPremisesIn_fill (N : NDoc) (X : RightsDoc) :
    VE.SoftNorms.softPremisesIn (correlate X) (VE.NormDefaults.fill (asU N X))
      (VE.Norms.layersOf (VE.NormDefaults.fill (asU N X))) = softX N X

/-- The witness's `Fill_T` on its own completion of the base: on the soft chain `gap_p` reads the default rules'
    selections, hence the decision tables. -/
def fillHoldsS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  (VE.NormDefaults.fillPremises (oneU N s i)).all (fun φ => φ.eval (tablesModel (one N.D s i).1 M T) [])

/-- S1's pair check, as the route runs it (`pairEval`), on the two filled sides, with the other reading's cells
    within `maxCells` and the witness's `Fill_T`. -/
def separatesS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  let Pi := sideOfS N (one N.D s i)
  let Pj := sideOfS N (one N.D s j)
  decide (cellsOn N.D s j Pj σ.base ≤ maxCells) &&
  (pairEval (m := Id) (pure ()) (pure ()) N.D s i j Pi Pj σ).1 &&
  fillHoldsS N s i σ.base (tablesForOf Pi.X (σ.fixed ++ σ.decisions))

/-- Probe `q` has value `v` on a reading's filled document over `B`, read in its canonical expansion: W1's value of
    the probed predicate on `fill (asU N X)` (an outcome), a selection by a rule of the kind (`selects`), or the
    assertions (`holds`). S1's `Observes` with `fill (asU N X)` in place of `soften (correlate X)`. -/
def ObservesF (N : NDoc) (X : RightsDoc) (A : List VE.Formula) (B : VE.Structure.{u}) :
    Probe B.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ VE.TupleTyped B r.sorts vs ∧
      VE.Norms.Value (VE.NormDefaults.fill (asU N X)).T r (canon (VE.NormDefaults.fill (asU N X)) B) vs = some v
  | .selects k p vs, v => VE.TupleTyped B (VE.SoftNorms.sortsOf (correlate X) p) vs ∧
      ((∃ M ∈ selectable X k p, VE.Norms.SelectsD (VE.NormDefaults.fill (asU N X)).T
          (canon (VE.NormDefaults.fill (asU N X)) B) (tupleVal vs)
          (VE.Norms.fuel (VE.NormDefaults.fill (asU N X)).T) (VE.SoftNorms.primeNode (correlate X) M)) ↔ v = true)
  | .holds, v => ((∀ a ∈ A, a.denote (canon (VE.NormDefaults.fill (asU N X)) B) []) ↔ v = true)

/-- Reading `i` achieves value `v` of probe `q` on base `B`: `B` is admissible over the filled author vocabulary (its
    `unsaid__` tables the shared filling), and some completion of the reading's own decision tables, agreeing with
    `F` off the keys it owns, is admissible for the reading's filled document with its soft premises and `Fill_T`
    (`BaseAdmissibleX`) and gives `q` the value `v`. -/
def AchievesS (N : NDoc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (authorEnv (fillDoc N)) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned N.D s i k = false → ∀ vs, G k vs ↔ F k vs) ∧
    VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s i) (oneX N s i) (withTables (one N.D s i).1 B G) ∧
    ObservesF N (one N.D s i).1 (one N.D s i).2 (withTables (one N.D s i).1 B G) q v
def SeparatedS (N : NDoc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (AchievesS N s i B F q v ∧ ¬ AchievesS N s j B F q v) ∨ (AchievesS N s j B F q v ∧ ¬ AchievesS N s i B F q v)

theorem separatesS_sound {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (hj : (candidate N.D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (authorEnv (fillDoc N))) (h : separatesS N s i j σ = true) :
    AchievesS N s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
      ¬ AchievesS N s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value
theorem separatesS_separated {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (hj : (candidate N.D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (authorEnv (fillDoc N))) (h : separatesS N s i j σ = true) :
    SeparatedS.{0} N s i j
end VE.Readings
```

Proof notes. The proof follows `separates_witness` and `separates_other`, which read only S1's table lemmas
(`tablesModel_rel`, `mem_assignments_foldr`, the `tableOf` lemmas; these are about `genKeys X` and are unchanged), the
side's admissibility check and its observation. Two lemmas replace the last two for a filled side:

- `sideValidOn_sideOfS_iff`: on a model valid over the filled base environment, `sideValidOn (sideOfS N X) M T` holds
  exactly when the tables are typed and the completion satisfies the filled tree's base background and `softX N X`.
  Proved by `softPremisesIn_fill` and `eval_iff_denote`.
- `observeOn_sideOfS_sound`: `observeOn (sideOfS N X) M q = some v` iff `ObservesF N X A M.asStructure q v`, for a
  well-formed filled tree. This is S1's `observe_sound` with W1's lemmas applied to `fill (asU N X)`, which is a W1
  document (`fill_wellFormed`).

`pairEval_id`'s argument shows that `(pairEval Id …).1` is S1's composition on the given sides. The witness's
`Fill_T` comes from `fillHoldsS`. The other side needs no `Fill_T`, because `AchievesS` requires it.

### 4.6 SC-3: force twins under the completion (`VE.Readings`)

```lean
namespace VE.Readings
universe u

/-- `AchievesS` with the table of `k₀` empty (S1's `AchievesQuiet` on filled sides). -/
def AchievesQuietS (N : NDoc) (s : String) (j : Nat) (k₀ : GenKey) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (authorEnv (fillDoc N)) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned N.D s j k = false → ∀ vs, G k vs ↔ F k vs) ∧ (∀ vs, ¬ G k₀ vs) ∧
    VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s j) (oneX N s j) (withTables (one N.D s j).1 B G) ∧
    ObservesF N (one N.D s j).1 (one N.D s j).2 (withTables (one N.D s j).1 B G) q v

/-- With the default twin's exception table empty, the strict and the default reading reach the same probe values on
    every base and every filling: under the completion they differ only where the exception applies. -/
theorem decision_only_soundS (N : NDoc) (hN : WellFormedSD N = true) (s : String) (i j : Nat) (k₀ : GenKey)
    (h : decisionOnly N.D s i j = some k₀) (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier)
    (v : Bool) :
    AchievesS N s i B F q v ↔ AchievesQuietS N s j k₀ B F q v
end VE.Readings
```

Proof notes. Reuse `decisionOnly_twin`, `TwinDocs.correlate_eq` and `Twin.decides`: off the exception the two soft
documents decide alike. `fill` reads only the author rules' decisions: `fill_soft_value` gives `Value3` from
`DecidesSoftD`, and `fill_selects_author` gives the author rules' selections. So the filled trees decide alike, and the
canonical expansions agree on every formula of the strict document (as `canon_relax`). `softX` agrees as well: the
twin is alone on its act, so it is in no colliding pair, and its exception has no sufficient condition, so with its
table empty its necessary conditions hold vacuously. `Fill_T` agrees because `gap_p` reads the author decisions.

No statement is added for "where the exception applies, the default reading leaves the act unsaid": it is
`excepted_lifts` at `oneU N s j` (`rulesOn (correlate (one N.D s j).1) p = [Nd]`, which `decisionOnly` checks).

### 4.7 SC-4: admission, route, separation and each choice (`VE.Readings.Wire`)

```lean
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Norms (envAt size)
open VE.Rights (correlate)
universe u

/-- Under the soft completion (3.1). -/
def underSoftCompletion (re : ReadingsEnvironment) (D : Doc) : Bool :=
  re.lower.contains normDefaultsProfile && re.chain == .soft && D.sets.any contentBearing

/-- norm-defaults' author checks on one document of the route, counting the predicates its chain generates (none on
    the norms chain; the decision predicates on the soft chain, as `decodeSoftU` counts them), then `WellFormedU`.
    RD-2a's `ndDocText re U` is `ndDocTextG re 0 U`. -/
def ndDocTextG (re : ReadingsEnvironment) (generated : Nat) (U : VE.NormDefaults.UDoc) : Option String :=
  match VE.NormDefaults.Wire.checkAuthorN re.lowerJson generated U with
  | .error e => some e
  | .ok () => if VE.NormDefaults.WellFormedU U then none else some "InvalidInput: norm-defaults document is not well formed"
theorem wellFormedU_of_ndDocTextG {re : ReadingsEnvironment} {g : Nat} {U : VE.NormDefaults.UDoc}
    (h : ndDocTextG re g U = none) : VE.NormDefaults.WellFormedU U = true

structure AdmittedSD where
  b : Admitted2
  N : NDoc
  hN : N.D = b.D
  wf : WellFormedSD N = true

/-- 3.3: S1's and S2a's admission as today; reserved names; `ndDocTextG` with each document's decision count on the
    free document and on each reading's document with content (a reading's text suffixed ` under <set>@<v>:<i>`);
    then each compatible choice, at most 64: S2a's chain text and `ndDocTextG` on `choiceU N c`, suffixed
    ` under <choice>`. -/
def admitSD (environment document : Json) : Except String AdmittedSD

/-- A replayed separation under the soft completion; the situation is decoded over the filled author vocabulary
    (`filledEnvironment`, RD-2a). -/
structure SeparateReplayS where
  r : AdmittedSD
  set : String
  witness : Nat
  other : Nat
  hw : (candidate r.N.D set witness).bind (·.content) ≠ none
  ho : (candidate r.N.D set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  valid : σ.base.Valid (authorEnv (fillDoc r.N))
def replaySeparateS (j : Json) : Except String SeparateReplayS

theorem readings_wire_sd_separate_sound (j : Json) (x : SeparateReplayS) (h : replaySeparateS j = .ok x)
    (hs : separatesS x.r.N x.set x.witness x.other x.σ = true) :
    AchievesS x.r.N x.set x.witness x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value ∧
      ¬ AchievesS x.r.N x.set x.other x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value

/-- A choice's document as the layered branch's source, on either chain (RD-2a's `choiceLayered` is the norms
    chain's case, with no extra premise): route `norms@0` or `soft-norms@0`, the labelled premises
    `softXL N (choiceDoc N.D c).1`, the situation vocabulary with the choice's decision predicates, and packages bound
    to the case's environment id, the choice's document hash and `E‴_base` with the decisions. -/
def choiceLayeredG (re : ReadingsEnvironment) (b : Admitted2) (N : NDoc) (c : Choice)
    (wfs : VE.SoftNorms.WellFormedSoft (correlate (choiceDoc N.D c).1) = true)
    (wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true) :
    Except String {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU N c ∧ L.X = choiceX N c}

structure ChoiceReplayS where
  r : AdmittedSD
  c : Choice
  hc : Compatible r.N.D c
  wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true
  L : VE.NormDefaults.Wire.LayeredU
  hU : L.U = choiceU r.N c
  hX : L.X = choiceX r.N c
/-- Runs 3.3 step 5's checks on its own choice and refuses with their text, then builds `choiceLayeredG`. -/
def replayChoiceS (j : Json) : Except String ChoiceReplayS

theorem readings_wire_sd_choice_conflict (j : Json) (x : ChoiceReplayS) (h : replayChoiceS j = .ok x)
    (packages : Json) (hv : VE.NormDefaults.Wire.conflictFreeX x.L packages = true) :
    Compatible x.r.N.D x.c ∧ VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N x.c) (choiceX x.r.N x.c)
theorem readings_wire_sd_choice_entails (j : Json) (x : ChoiceReplayS) (h : replayChoiceS j = .ok x)
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill (choiceU x.r.N x.c))
            (size (VE.NormDefaults.fill (choiceU x.r.N x.c))))
            (VE.NormDefaults.Wire.premisesX (choiceU x.r.N x.c) (choiceX x.r.N x.c)
              ((choiceDoc x.r.N.D x.c).2 ++ Γ)) φ cert = true)
    (packages : Json) (hcf : VE.NormDefaults.Wire.conflictFreeX x.L packages = true) :
    VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N x.c) (choiceX x.r.N x.c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU x.r.N x.c) (choiceX x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ) φ
end VE.Readings.Wire
```

Definition changes in the same batch. They change no statement.

- `abstention`: `re.chain != .norms` becomes `re.chain == .rights`.
- `routeOf`: `if D.chain == .norms then .enumerated else .abstention` becomes
  `if D.chain != .rights then .enumerated else .abstention`. On the soft chain the enumerated row stays the route
  until SC-11; `routeND` is unchanged.
- `ndDocText re U := ndDocTextG re 0 U`.
- `choiceLayered r c wfc` is `choiceLayeredG` on the norms chain.
- `ndCertificate` binds and checks `premisesX U L.X`, and `ndChoiceModel` checks `modelCheckX U L.X`.
- `readings-validate`, `readings-separate` and `readings-elaborate` dispatch to the soft completion's runners when
  `underSoftCompletion` holds.
- Per pair, both chains under the completion, the answer adds `gaps`: `gapsOf (oneU N s w)` on the witness's
  completion model, with the probe's formula.

### 4.8 SC-5: verdicts under the soft completion (`VE.Readings.Wire`)

```lean
namespace VE.Readings.Wire
open VE.Readings
open VE.NormDefaults (UDoc fill)
universe u

/-- One compatible choice's decoded evidence with the route's extra base premises `X`. RD-3's `NDEvidence N c` is
    `XEvidence (choiceU N c) []` (D7). -/
structure XEvidence (U : UDoc) (X : List VE.Formula) where
  wfc : VE.NormDefaults.WellFormedU U = true
  hX : ∀ a ∈ X, a.WellFormed (VE.Norms.envAt (fill U) 0) []
  certs : List (Option VE.Tableau.Certificate)
  witness : Option (PLift (¬ VE.NormDefaults.Wire.ConflictFreeX.{0} U X))
  cert : Option VE.Tableau.Certificate
  counter : Option (FilledModel U)
  unsat : Option VE.Tableau.Certificate
  model : Option (FilledModel U)

/-- RD-3's row rules with `X`: CONFLICT-FREE with every target's package accepted over
    `Background_base(E‴) ++ X ++ Fill_T`, CONFLICT with a checked witness; `proved` with a certificate over
    `premisesX` and the conflict packages; `refuted` with a checked countermodel (`modelCheckX`, locally
    conflict-free); INCONSISTENT and `model` likewise. `A` is the choice's regenerated assertions. -/
def xConflictRow {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) : ChoiceResult
def xQueryRow {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) (A Γ : List VE.Formula) (φ : VE.Formula) :
    ChoiceResult
def xPremiseRow {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) (A : List VE.Formula) : ChoiceResult

theorem xConflictRow_holds {N : NDoc} {Xf : Choice → List VE.Formula} {c : Choice}
    (e : XEvidence (choiceU N c) (Xf c)) : HoldsG (xSem.{u} N Xf) [] .bottom c (xConflictRow e)
theorem xQueryRow_holds {N : NDoc} {Xf : Choice → List VE.Formula} {c : Choice}
    (e : XEvidence (choiceU N c) (Xf c)) (Γ : List VE.Formula) (φ : VE.Formula) :
    HoldsG (xSem.{u} N Xf) Γ φ c (xQueryRow e (choiceDoc N.D c).2 Γ φ)
theorem xPremiseRow_holds {N : NDoc} {Xf : Choice → List VE.Formula} {c : Choice}
    (e : XEvidence (choiceU N c) (Xf c)) : HoldsG (xSem.{u} N Xf) [] .bottom c (xPremiseRow e (choiceDoc N.D c).2)

/-- A replayed `readings-verdicts` case with an extra base-premise family: exactly the compatible choices taking `A`
    (at most 64), each with its evidence. -/
structure XVerdicts where
  N : NDoc
  Xf : Choice → List VE.Formula
  A : Choice
  Γ : List VE.Formula
  φ : VE.Formula
  ready : supReady N.D = true
  hle : (choices N.D).length ≤ maxChoices
  evs : List ((c : Choice) × XEvidence (choiceU N c) (Xf c))
  hevs : evs.map (·.1) = chosenOf N.D A
  notes : List (List PieceNote)
def XVerdicts.conflictRows (x : XVerdicts) : List (Choice × ChoiceResult) :=
  x.evs.map (fun e => (e.1, xConflictRow e.2))
def XVerdicts.queryRows (x : XVerdicts) : List (Choice × ChoiceResult) :=
  x.evs.map (fun e => (e.1, xQueryRow e.2 (choiceDoc x.N.D e.1).2 x.Γ x.φ))
def XVerdicts.premiseRows (x : XVerdicts) : List (Choice × ChoiceResult) :=
  x.evs.map (fun e => (e.1, xPremiseRow e.2 (choiceDoc x.N.D e.1).2))
theorem x_rowsHold (x : XVerdicts) : RowsHoldG (xSem.{u} x.N x.Xf) x.A x.Γ x.φ x.conflictRows x.queryRows

/-- The replay under the soft completion: `admitSD`, at most 64 compatible choices, those taking `A` (else
    `ReadingsUnsatisfiable`), each choice's evidence decoded on its own layered source (`choiceLayeredG`). -/
structure SDVerdicts where
  r : AdmittedSD
  x : XVerdicts
  hN : x.N = r.N
  hX : x.Xf = choiceX r.N
def replayVerdictsSD (j : Lean.Json) : Except String SDVerdicts

theorem readings_wire_sd_verdicts_all (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldEntailment y.x.conflictRows y.x.queryRows = .all) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ
theorem readings_wire_sd_verdicts_none (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldEntailment y.x.conflictRows y.x.queryRows = .none) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ∧
      CounterX (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ
theorem readings_wire_sd_verdicts_some (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldEntailment y.x.conflictRows y.x.queryRows = .some) :
    (∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c)) ∧
    (∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ) ∧
    (∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      CounterX (choiceU y.r.N c) (choiceX y.r.N c) ((choiceDoc y.r.N.D c).2 ++ y.x.Γ) y.x.φ)
-- `readings_wire_sd_verdicts_conflict_free`, `_conflict`, `_model` and `_inconsistent`: RD-3's four, read through
-- `x_rowsHold` and `foldG_*_sound` at `sdSem`, in the same shape as the three above.
end VE.Readings.Wire
```

Consolidation in the same batch (D7). `NDEvidence N c` becomes `XEvidence (choiceU N c) []`. `ndFree`, `ndCertOk`,
`ndModelOk`, `ndConflictRow`, `ndQueryRow` and `ndPremiseRow` become the `X = []` instances. `ndConflictRow_holds`,
`ndQueryRow_holds`, `ndPremiseRow_holds` and `nd_rowsHold` keep their statements and are re-proved through
`x*Row_holds`, `xSem_nil` and `holds_iff_holdsG`. `ndEvidenceOf` stops converting witnesses with
`notFreeU_of_notFreeX`, because `XEvidence` holds the layered witness itself. The norms chain's A/B must be
byte-identical.

### 4.9 SC-6: the layered branch's certificate and admission kinds (`VE.NormDefaults`)

```lean
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms
universe u

/-- The base premises of a decoded soft source are closed over its filled base vocabulary. -/
theorem decodeSoftU_X_wellFormed (environment norms : Json) (L : LayeredU) (h : decodeSoftU environment norms = .ok L) :
    ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []

/-- The `norm-defaults-certificate` kind on the soft branch: a certificate over `premisesX L.U L.X Γ`, bound as the
    norms route binds one (`bindingOk` over the source environment and the premises' and conclusion's meaning ids). -/
structure LayeredEntailment where
  L : LayeredU
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate
  valid : Bool
  hvalid : valid = VE.Tableau.checkCertificate (envAt (fill L.U) (size (fill L.U)))
    (premisesX L.U L.X premises) conclusion cert
def replayLayeredEntailment (j : Json) : Except String LayeredEntailment

theorem layered_wire_acceptance (j : Json) (r : LayeredEntailment) (h : replayLayeredEntailment j = .ok r)
    (hv : r.valid = true) :
    VE.NormDefaults.EntailsX.{u} r.L.U r.L.X r.premises r.conclusion
end VE.NormDefaults.Wire

namespace VE.NormDefaults.Admission
open Lean
open VE.Norms
universe u

/-- W2 admission on the soft branch: W1's `Norms.Admission` on the filled tree of the soft source. Graph leaves may
    name, beside W2's ordinary provenance, a regenerated layer premise of `fill U` (`layer:norms:<p>`), a regenerated
    soft premise on the filled tree (`soft:exception:…`, `soft:coherence:…`), a pair premise (`background:profile`)
    or a `Fill_T` premise (`unsaid:pair:<r>,<m>`). Certificates bind the regenerated `E‴` with the decision
    predicates. -/
structure AdmittedX where
  L : VE.NormDefaults.Wire.LayeredU
  doc : VE.Route.Admission.Doc
  filled : Json
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
def admitDocumentX (environment document : Json) : Except String AdmittedX

/-- `wire_report_consequence` with `X`: in every structure admissible for `E‴` satisfying the filled tree's
    background, `X`, `Fill_T` and the filled layers, the remaining assumptions entail the root. -/
theorem wire_report_consequenceX (environment document : Json) (res : AdmittedX)
    (h : admitDocumentX environment document = .ok res) (S : VE.Structure.{u})
    (hS : S.Admissible (fill res.L.U).E)
    (hflags : Sat S (VE.Data.Background.generate res.doc.flags))
    (hregen : Sat S (background (fill res.L.U) ++ res.L.X ++ fillPremises res.L.U ++ elaborate (fill res.L.U).T))
    (hother : Sat S ((otherAssumptionsX res).map (·.formula))) :
    res.report.root.formula.denote S []
end VE.NormDefaults.Admission
```

`otherAssumptionsX` is `otherAssumptions` with soft leaves excluded too. `admitDocumentX_spec` is
`admitDocument_spec`'s shape with `SoftLeaf` among the admitted leaf kinds, and SC-0 writes it out once
`admitDocumentX`'s body is fixed. `layeredCase` gains `norm-defaults-certificate` and `admission` on the soft branch.
The rights branch answers `runLayered`'s existing refusal for both.

### 4.10 SC-7: decided units without companions

No new theorem. The `readings-verdicts` answer on the enumerated route without components adds `decided_units`,
computed by `partDecided` (RD-4b) on the main case as the one component, in the document's order (`documentOrder`).
The rule is readings-defaults 1.10: a fixed unit with content counts when its conflict status and premise status are
decided, and an open set's unit counts when every compatible choice's conflict row is decided and every reading's
premise status is decided. The batch adds `#guard`s on `partDecided` for one main case (both chains).

### 4.11 SC-10 (sketch, off the constitution's path; re-reviewed before its build)

```lean
namespace VE.Readings
universe u
/-- The superposed document's extra premises under the soft completion. -/
def supX (N : NDoc) : List VE.Formula := softX N (sup N.D).1
/-- Superposition under the soft completion: the filled superposed document with its soft premises, `Fill_T` and
    the slot under `A` is CONFLICT-FREE exactly when every compatible choice taking `A` is, read with its own `X`. -/
theorem sd_superpose_conflict_free (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    (∀ B : VE.Structure.{u}, VE.NormDefaults.Wire.BaseAdmissibleX (supU N) (supX N ++ slotUnder N.D A) B →
        VE.Norms.ConflictFree (VE.NormDefaults.fill (supU N)) B) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU N c) (choiceX N c)
end VE.Readings
```

The lemma it needs is `fill_sim`: at a slot-admissible base encoding `c`, the filled superposed tree's layer meanings,
pulled to `c`, are the filled choice tree's. It extends S2a's `sim_decides` and `pull_canon` through `fill`, which reads
only the author roots' yields, and `SupFill.lean`'s `decidesBy_pull_canon` and `fillPremises_pull` are its pieces on
the norms chain. `supX` transfers by the same lemma: a coherence conjunct between two candidates of one set holds at
every encoded base, since a non-chosen candidate's gated rule never applies there. `sd_superpose_all` and
`sd_superpose_countermodel` follow S2a's statements in the same way. These statements are drafts; their review is
part of SC-10.

## 5. Fixtures

### 5.1 Synthetic, from S1's environment K (composition-s1 9.2)

Environment K with `norm-defaults@0` added and `avoid_required` `unspecified` unless said. `S` is the strict rule
`no-deception` on `+avoid_required`, guard ⊤, and `Df` is `S` as a default rule decided by `unstated`. Set `rs1` is
{0: `S`, 1: `Df`}. Model `m0` has one agent `a`, one user `u`, and `asks` empty.

| # | Case | Expected (*derived*) | Batch |
|---|---|---|---|
| F-SD1 | `rs1` | admitted; choices `[(rs1,0)]`, `[(rs1,1)]`; `oneX` = `choiceX` = `[]` (no condition, no colliding pair); `separatesS … 1 0 σ = true` for σ = (`m0`, filling empty, decisions `excepted no-deception` = {(a, u)}, outcome `avoid_required (a, u)`, false); with the filling {(a, u)}: `false`; with witness 0, value true, no decision: `false` (the default reading reaches true with the empty table); `decisionOnly = some (excepted no-deception)` | SC-2, SC-4 |
| F-SD1.status | `norm-defaults-status` on choice `(rs1,1)`, base with `excepted` {(a, u)}, fillings yes {(a, u)} and no {} | UNDECIDED; on `(rs1,0)`: SETTLED yes by `table3` (as `u2-unspecified-*` in `test_norm_defaults_layered.py`) | SC-4 |
| F-SD1.verdicts | conflict; query `∀ agent ∀ user. avoid_required`; the same `--under rs1:0` and `--under rs1:1` | CONFLICT-FREE under both; SOME (choice 0 `proved`, choice 1 `refuted` by `excepted` {(a, u)} and the filling no); ALL; NONE. English: E12 R2 for *must*, E12 R3 for *should* with "suppose the decider decides the exception applies to a and u" and one filled-gap sentence | SC-5, SC-8 |
| F-SD2 | K18 (K1 with `norm-defaults@0`, `avoid_required` deny) | before: the abstention text; after: admitted with K1's answers (`unspec = []`, `fill` the identity): an `availability` change in DELTA | SC-4 |
| F-SD3 | K5 under the completion: a fixed default rule `be-kind` on `+help_required` (unspecified); σ with fixed `excepted be-kind` = {(a, u)} | `excepted be-kind` shared and owned by neither reading; `separatesS = true`; `cellsOn … 0 = 0`, `cellsOn … 1 = 1` | SC-2 |
| F-SD4 | the `coherent` fixture of `test_norm_defaults_layered.py` (`must-x` with a sufficient exception condition and `need-not-x`, a guard on `y_permitted` unspecified) placed in a set beside its strict twin | `soft_premises` of the default reading lists `soft:exception:must-x:sufficient:0` and `soft:coherence:must-x,need-not-x`; the coherence AST mentions `unsaid__y_permitted` (soft's own would not); a CONFLICT-FREE answer under the default reading is `conditional_on: ["soft:coherence:must-x,need-not-x"]` with soft-norms 2.3's sentence as its E3 line | SC-4, SC-5 |
| F-SD5 | `fillDoc` of F-SD1 (D1's reason, `#guard`) | `chainText .soft (one (fillDoc N) "rs1" 1)` is `SoftOverHard: rule no-deception over unsaid--avoid-required` | SC-2 |
| F-SD6 | K19 (rights chain) with `norm-defaults@0` | the abstention text, unchanged | SC-4 |
| F-SD7 | 252 declared predicates of which 4 `unspecified`, one set {strict, default} on one of them | the strict reading's document passes `checkAuthorN` (252 + 0 + 4 = 256); the default reading's fails, `ResourceLimit: vocabulary size under rs_1@1:1` (252 + 1 + 4 = 257) | SC-4 |
| F-SD8 | tampering: a package bound to choice `(rs1,0)` replayed for `(rs1,1)`; an `unsaid__` table in a layered model's `relations`; a `soft__excepted__` table as a separation base relation (K2b) | refused or UNKNOWN, never CONFLICT-FREE, `proved` or `model`: `InvalidModel(norm-defaults): … is a filling`; `InvalidInput: invalid situation <id>` | SC-4, SC-5 |
| F-SD9 | 7 sets each as `rs1` | enumerated, `choice_count: "over 64"`; a query: UNKNOWN (budget), E28 | SC-4, SC-5 |
| F-SD10 | the cone (D9): F-SD1 with three more unspecified predicates in the frame, no rule on them | the separation line has one filled-gap sentence (for `avoid_required (a, u)`), not four; Lean's `gaps` lists one entry | SC-4, SC-8 |

### 5.2 Constitution units (real)

`CE4` is the four sets of run 20261010T1800Z (`translation.ve.md` at pilot commit `76922d6c`) in a small document. Its
frame has the sorts `claude_instance`, `situation`, `user`, the base predicates `genuine_ambiguity(situation)` and
`explicit_instruction_against_exploits(claude_instance, situation)`, and the four regulated predicates of 1.1,
each `unspecified`, with act phrases and verbalisations copied from the translation. Its profiles add
`soft-norms@0`. Each `default` candidate is rewritten from "strict rule + `unless` over an `exception_to_*` open term"
to the same rule with `mode: default`, `exception: {decided_by: "unstated", sufficient: [], necessary: [],
factors: []}` and `unless: []`, and the four open terms are dropped. The `strict` candidates and the `source_word`
spans are unchanged. SC-8's test builds `CE4` from the pinned translation; nothing is retyped.

| # | Unit and source words | Expected (*derived*) |
|---|---|---|
| C1 | u0125.s04.p2, "Claude should never directly deny that it is Claude" (`force-u0125-s04-p2`) | admitted; σ: witness `default`, decisions `excepted no-denying-being-claude` = {c}, filling `unsaid__denial_of_being_claude_permitted` = {c}, outcome `denial_of_being_claude_permitted (c)`, true. The strict reading reaches only false (its rule forbids everywhere), so separated. Finding `SeparatedByDecisionOnly: force-u0125-s04-p2: 0, 1` with S1's wording rule (D5); E14 with source word *should* |
| C1.4 | the status of `denial_of_being_claude_permitted (c)` with `excepted` {c} | under `default`: UNDECIDED, R7 "the text does not say whether c may directly deny being Claude: no rule decides this situation."; under `strict`: SETTLED no |
| C2 | u0036.s05, "Claude should ask for clarification in cases of genuine ambiguity" | σ: witness `default`, base `genuine_ambiguity` = {s}, decisions `excepted clarify-ambiguity` = {(c, s)}, filling empty, outcome `clarification_required (c, s)`, false. The strict reading's guard holds, so it reaches only true. Separated. One filled-gap sentence: "Here the text does not say whether c must seek clarification in s; this situation answers 'no'." (today: 15 sentences, 1.1) |
| C3 | u0156.s03, "Claude shouldn't actively deceive the user about the existence of a system prompt or its content" | as C1 with the tuple (c, u) on `system_prompt_deception_permitted`; E14 with source word *shouldn't* |
| C4 | u0263.s04.p2, "in situations where Claude has explicitly been instructed not to engage in unintended exploits, it should comply" | as C2 with base `explicit_instruction_against_exploits` = {(c, s)} on `exploit_instruction_compliance_required` |
| C5 | `CE4`, conflict | 16 compatible choices, each CONFLICT-FREE (each regulated predicate has one rule, so no rule collides; `choiceX = []` for every choice); `conditional_on: []` |
| C6 | `CE4`, query "∀ c. ¬ denial_of_being_claude_permitted(c)" (the pilot's denial query) | SOME (the 8 choices with `strict` `proved`, the 8 with `default` `refuted`); `--under force-u0125-s04-p2:0`: ALL; `:1`: NONE, shown with "suppose the decider decides the exception applies to c" and "Here the text does not say whether c may directly deny being Claude; this situation answers 'yes'." The norms-chain workaround's plain route gave UNKNOWN across readings and under the defeasible reading (*recorded*, FEATURE-REVIEW.md), for a cause not analysed. SC-9 measures what the generators find here and reports any UNKNOWN with its reason |
| C7 | `CE4`, query "∀ c ∀ s. genuine_ambiguity(s) → clarification_required(c, s)" | SOME; `--under force-u0036-s05:0`: ALL |
| C8 | `CE4` with `decided_units` (SC-7) | the four sets' units, when C5's rows are all decided and every reading's premise status is `model`; any unit whose evidence is missing is absent (readings-defaults SR4) |

These are semantic expectations. Whether Python's generators find each situation, certificate and countermodel
within budget is measured (SC-8 on `CE4`, SC-9 on the translation), never assumed.

### 5.3 Conservativity

| # | Case | Expected |
|---|---|---|
| F-SD0 | S1's K1 to K22 without `norm-defaults@0`; S2a's M1 to M20 | byte-identical verdicts, identities and English |
| F-SD0′ | readings-defaults' F-ND0 to F-ND10 and the RD-3, RD-4b and RD-6b fixtures | byte-identical verdicts and identities. The English is identical except the separation lines' gap selection (D9), a signed `wording` change; F-ND1's line keeps its one gap |
| F-SD0″ | `tests/test_norm_defaults_layered.py` | unchanged answers. The two new kinds answer on the soft fixtures (u2, u3, u8, `coherent`) |

## 6. Batches

Every batch takes 2 to 6 hours for one builder, works from the build checklist, and passes the lean-first gate of
LEAN-FIRST-PLAN 5.1: the full suite in chunks, the corpus A/B over the probe matrix, the conformance and readings
corpora and every historical pilot document, changes listed in `DELTA.md` by class, the deletion ledger, and latency
within section 4's budgets. Each batch also runs the audit, the frozen-inventory and assurance-manifest updates
(DRI D2), trust classes with any budget rise signed in the same merge (DRI D3), and `tools/lean_statements.py`
(additions only). Batch evidence is checked at the gate, and evidence over 1 MB lives on the evidence branch (DRI D4).
New Python respects the layer map (DRI D5). New diagnostics take AR-13's codes when they land (DRI D6), and every
identity stays Lean's (DRI D7); DRI D8 (AR-10 after lf-18) does not bear on these batches. The statement review comes
before any Lean build: SC-0 reviews every statement of section 4, and a batch whose statement changes during its
build reopens only that statement.

| # | Batch | Hours | Owner | Needs |
|---|---|---:|---|---|
| SC-0 | Statement review: the stub elaborated against `main`, this file corrected, review by Astra and Opus until converged (Fable arbitrates only an unconverged debate) | 3–4 | planner | — |
| SC-1 | `EntailsX`, `acceptanceX`, `modelCheckX`; `softX`, `WellFormedSD`; the generic fold, with RD-3's fold proofs re-proved as instances | 5–6 | Lean | SC-0 |
| SC-2 | Separation on filled sides: `sideOfS`, `separatesS`, `AchievesS`, `separatesS_sound` | 5–6 | Lean | SC-1 |
| SC-3 | `decision_only_soundS` | 4–6 | Lean | SC-2 |
| SC-4 | Wire: abstention and route, `admitSD`, separation replay, `choiceLayeredG`, the choice inner kinds with `X`, per-pair `gaps` | 5–6 | Lean | SC-2 |
| SC-5 | Wire: `XEvidence`, `XVerdicts`, `readings-verdicts` under the soft completion; `NDEvidence` and its rows as `X = []` instances | 5–6 | Lean | SC-1, SC-4 |
| SC-6 | Layered branch: `norm-defaults-certificate` and `admission` on the soft branch | 3–4 | Lean | SC-1 |
| SC-7 | `decided_units` on the enumerated route without companions (both chains) | 2–3 | Lean, Python | SC-5 |
| SC-8 | Python: `ve document` on soft documents under `norm-defaults@0`, relay and generators, English from Lean's selections; `CE4` through the CLI | 4–5 | Python | SC-4, SC-5, SC-6 |
| SC-9 | The constitution: migration on a pilot branch, checks, queries, measurements, audit of the changed units | 4–5 | pilot tooling, measurement | SC-7, SC-8 |
| SC-10 | Superposition under the soft completion, theory (`fill_sim`, 4.11) | 5–6 | Lean | SC-5 |
| SC-11 | Superposition under the soft completion: route, wire, generators, differential | 5–6 | Lean, Python | SC-10 |

**The constitution's path:** SC-0 → SC-1 → SC-2 → SC-4 → SC-5 → SC-8 → SC-9, with SC-6 beside SC-2 to SC-5 and SC-7
after SC-5. That is about 36 to 45 builder-hours by these estimates (estimates, not evidence of buildability or
speed). SC-3 is off the path: until it is proved, the finding keeps E25 ("not certified"), which is what S1 shows
today. SC-10 and SC-11 are off the path, and their statements are re-reviewed before their build.

### SC-0. Statement review (planner, 3–4 h)

- Elaborate section 4 in an untracked stub, `lean/SpecStubs_rd9.lean`, with each `theorem T b : C` written as
  `def T b : Prop := C`, against a build of `main`. Every failure is fixed here, and the fixes are listed in a new
  section, "Differences found by elaboration".
- Compute with `#eval` every *derived* value of 5.1 that the stub can compute: F-SD1's `separatesS` cases, F-SD5,
  F-SD7, `softX` on F-SD1 and F-SD4. Mark them *computed*.
- Statement review by Astra and Opus, until converged. PASS requires both reviewers to accept each statement as true
  under its hypotheses; that the stub elaborates is not enough. The checklist is section 9.
- Done when the stub elaborates, this file is committed with the review's edits, and the review has converged on
  PASS.

### SC-1. Semantics with `X` and one fold (Lean, 5–6 h)

Files: `NormDefaults/LayeredEntail.lean`, `Readings/SoftDefaults.lean`, `Readings/VerdictsGen.lean` (new), with
`#guard`s in `Readings/SoftDefaultsExamples.lean`. `Verdicts.lean`'s seven fold proofs are replaced by instances of
`foldG_*`, and `UnspecifiedWire.lean`'s `ndRest` is restated through `WellFormedSD`'s shared conjuncts.

Fixtures: `softX` of F-SD1 is `[]` and of F-SD4 is two labelled premises, one of them reading `unsaid__y_permitted`.
`softX_strict` and `choiceX_normsShaped` are checked as `#guard`s on F-ND1. `premisesX_nil` is checked on F-ND1's
choice.

Deleted, not duplicated: the bodies of RD-3's seven fold proofs. The fold soundness is proved once, over
`ChoiceSem`. No second `Exc_T` or `Coh_T`: `softXL` calls `softLabelledU`.

Done when: builds with no `sorry` and standard axioms only, `tools/lean_statements.py` shows additions only (RD-3's
statements unchanged, their proofs shorter), `lean/READINGS.md` lists every new theorem in plain words, and the gate
passes. No answer can change, since nothing new is called.

### SC-2. Separation on filled sides (Lean, 5–6 h)

Files: `Readings/SoftSeparate.lean`, `Readings/SoftSeparateExamples.lean` (new).

Fixtures (`#guard`): F-SD1's four separation cases, F-SD3's cells, F-SD5, and `softPremisesIn_fill` on F-SD4.

Deleted, not duplicated: no second pair check. `separatesS` is `pairEval` on filled sides, the function the route
runs. The proof reuses S1's table lemmas and replaces only the side's admissibility and observation lemmas.

Done when: builds, the fixtures pass, `separatesS_sound` is proved with standard axioms, and the gate passes.

### SC-3. Force twins under the completion (Lean, 4–6 h)

File: `Readings/SoftForce.lean` (new). Fixtures: on F-SD1, `AchievesS` against `AchievesQuietS`; in `#guard` form,
`separatesS` with the exception table empty is false for every probe of `probesOf` and both values, as S1's K1 checks.

Deleted, not duplicated: `decision_only_soundS` reuses `Force.lean`'s twin lemmas and adds only the step through
`fill`.

Done when: proved, and the DRI is told that the E25 → E15 flip can now cover the completion (D5); the flip itself is
not part of the batch.

### SC-4. Wire: admission, separation and each choice (Lean, 5–6 h)

Files: `Readings/SoftWire.lean` (new), the definition changes of 4.7, and response shapes with their `*_fits`
theorems for the new fields (`soft_premises`, `gaps`).

Fixtures (`tests/test_readings_sd_lean.py` through the service): F-SD1 (validate, separate, elaborate, choice),
F-SD1.status, F-SD2, F-SD4, F-SD6, F-SD7, F-SD8, F-SD9, and F-SD10's `gaps`. C1 to C4 through `readings-validate` on
`CE4`. F-ND1, F-ND2 and F-ND10 are byte-identical except the new `gaps` field.

Deleted, not duplicated: RD-2a's `choiceLayered` body (now `choiceLayeredG` on the norms chain), `ndDocText`'s body
(now `ndDocTextG re 0`), and the X-free premise lists of `ndCertificate` and `ndChoiceModel`. No readings function
evaluates `X` or `Fill_T` except through `sideOfS`, `fillHoldsS` and the layered checkers.

Done when: the fixtures pass, the corpus A/B lists only `availability` changes for documents that reached the soft
abstention (K18; no corpus document is expected, *derived*: the committed constitution and UDHR documents are on the
norms chain) and the added `gaps` field, the DRI signs them, and the gate passes.

### SC-5. Wire: verdicts under the soft completion (Lean, 5–6 h)

Files: `Readings/SoftVerdicts.lean` (new), and in `VerdictsWire.lean` `NDEvidence` and its rows as `X = []`
instances. The `readings-verdicts` runner dispatches to `replayVerdictsSD` under the soft completion.

Fixtures: F-SD1.verdicts, F-SD4's `conditional_on`, F-SD8 (a certificate for one choice given as another's: that
choice `unknown`, never ALL), F-SD9, and C5 to C7 on `CE4`. All of RD-3's enumerated fixtures must stay
byte-identical.

Deleted, not duplicated: `ndFree`, `ndCertOk`, `ndModelOk`, `ndConflictRow`, `ndQueryRow`, `ndPremiseRow` as separate
bodies, and the witness conversion `notFreeU_of_notFreeX` in `ndEvidenceOf`. The ledger records the lines.

Done when: the fixtures pass, the norms chain's A/B is byte-identical, and the gate passes.

### SC-6. The layered branch's certificate and admission kinds (Lean, 3–4 h)

Files: `NormDefaults/LayeredAdmission.lean` (new). `layeredCase` gains the two kinds; `Layered.lean` is re-pinned in
the assurance manifest and the frozen inventory is updated (DRI D2). Fixtures: on the layered tests' u2 and u8
sources, a certificate of "where the rule's exception does not apply, the act is not permitted" is accepted, and the
same certificate replayed against the conclusion without that condition is not (`valid: false`). A claim graph with a `soft:coherence` leaf is
admitted on `coherent`, and a leaf with a label no regenerated premise has is refused with W1's admission text. Both
kinds on a rights source give `runLayered`'s refusal.

Deleted, not duplicated: the kinds reuse W1's `Norms.Admission` and the norms branch's `admitNodes` with one more
leaf kind; nothing is copied. The frozen oracle's `UnspecifiedSoftDocument` differential stays. It is test-only and
frozen, and its retirement is the DRI's call (b10b DELTA).

Done when: the fixtures pass, the A/B is identical (no corpus document reaches these kinds), and the gate passes.

### SC-7. Decided units without companions (Lean and Python, 2–3 h)

Lean: the answer field of 4.10. Python: `tools/lean_decided_share.py` reads `decided_units` from the enumerated route
as it does from the product route.

Fixtures: F-SD1's decided units, F-ND1's (norms chain), and C8.

Deleted, not duplicated: nothing. `partDecided` is RD-4b's, unchanged.

Done when: the A/B lists the added field on every enumerated-route answer as one signed change, and the gate passes.

### SC-8. Python: documents, relay, generators and English (4–5 h)

- `ve/document.py`: the refusal of 3.8 for the rights route only, with the narrowed text (3.11 row 7). Under the
  soft completion, no Python layer or soft premise enters a premise set. The norm-defaults container is built from
  Lean's layered row, and claim graphs go to the layered `admission` kind.
- `ve/norm_defaults.py`, `ve/softnorms.py`: display containers read the layered elaboration row (`order`, `premises`,
  `soft`, `fill`, `unsaid`, `base_environment`). No W1 `NormDocument` is built over soft units.
- `ve/readings_verdicts.py` (`_FilledChoiceDocument`): reads the chain and `soft` from Lean's row instead of the
  `chain = "norms"` constant. Packages are bound to Lean's `L.background` (`literals ++ soft ++ fill`). Models carry
  decision tables in the base and the filling apart. `side` holds the choice's decision tables for the wording.
- `ve/readings_s1.py`: under the soft completion the search proposes the witness's decision tables and the shared
  filling, over Lean's `filled` environment and each reading's `soft_premises`.
- English: separation lines render Lean's per-pair `gaps`. `ve/readings_s2_wording.py`'s `filled_gaps` is deleted.
  The E3 lines for soft labels use soft-norms 2.1 and 2.3's renderers.
- `tools/relay_lint.py`: no `soft__` or `unsaid__` literal in `ve/readings*.py`.

Fixtures: F-SD1 and `CE4` through `ve document load`, `check`, `render` and `readings --conclusion` (C6, C7);
F-SD10's rendered line with one gap sentence; a generator run on `CE4` that finds C1 to C4's situations, recorded as
found or not found.

Deleted, not duplicated: `filled_gaps`; the soft half of `document.py`'s refusal; `_FilledChoiceDocument`'s norms-only
constants. Python builds no `fill`, `X` or `Coh_T`.

Done when: the CLI fixtures pass, the relay lint passes, the A/B lists only the signed changes of 3.14, and the gate
passes.

### SC-9. The constitution (pilot tooling and measurement, 4–5 h)

On a pilot branch, with scripts under `usecases/claude-constitution-pilot/run-<stamp>/`, all at one commit, in the
foreground, with host load recorded:

1. `migrate_soft.py` reads run 20261010T1800Z at `76922d6c` and writes a probe translation: `soft-norms@0` added; each
   `default` candidate rewritten as in 5.2; the four `exception_to_*` open terms removed; situations re-proposed by
   SC-8's search and checked by Lean; every `meaning_id` taken from Lean's answer. Units, spans and `source_word`
   stay as they are.
2. Checks: `ve document load`, `check`, `render`, and the queries C6, C7 and the pilot's claim-to-be-human query,
   each answer recorded verbatim.
3. Measurements, before (the translation as committed, at the same commit) and after (the probe translation):

   | Measure | Before | After |
   |---|---|---|
   | `ve document check` wall and CPU | measured (54.6 s recorded at arch-AR-6) | measured, within lean-first section 4's budget |
   | Route; choices; conflict; premises | enumerated, 16, CONFLICT-FREE, `model` (*recorded*) | measured |
   | Lean-decided units, bytes, share (SC-7) | measured | measured |
   | Open terms | 33 (*recorded*) | measured |
   | Gap sentences in the four separation lines | measured (15 per line recorded on two lines) | measured |
   | Pairs separated; pairs the search did not separate | 4 (*recorded*) | measured, listed |
   | Claimed covered; audit-verified | 2,951 (1.60%); 764 (0.41%) (*recorded*) | unchanged unless a status changes; the four units are listed as `changed_units` for the next audit |

4. The translation adopts the soft form only after an audit accepts the changed units. That decision belongs to the
   pilot, not to this batch.

Optional probe, not the translation: u0073.s05 ("should generally comply … if doing so is not unsafe, unethical, or
against Anthropic's guidelines") as one default rule (soft-norms 2.4's rule 4 form), replacing the
`general_exception_to_complying` open term; its statuses recorded.

Done when: the table is filled with measured values, `DELTA.md` and the pilot's `SUMMARY.md` report before and after,
and every pair the search did not separate, every UNKNOWN answer and every failed check is listed rather than worked
around.

### SC-10, SC-11. Superposition under the soft completion (off the path)

SC-10 builds 4.11's statements in `Readings/SoftSup.lean`, re-reviewed first. SC-11 adds the route: superposed when
`superposable N.D` and `WellFormedU (supU N)` hold, with DRI ruling 5's check of every compatible choice extended by
3.3 step 5's checks. It also covers the wire with `supX ++ Fill_T` after the slot, the generators, and a 200-document
differential of generated soft documents under the completion, with at most 64 choices, giving identical verdicts on
both routes.

## 7. The measure

The Lean-decided share is readings-defaults 3.9's: the span bytes of Lean's `decided_units`, summed by
`tools/lean_decided_share.py`, which decides nothing. SC-7 makes the share readable on the translation itself. SC-9
reports it before and after the soft form, beside the unchanged claimed and audit-verified shares, with
readings-defaults E2's qualifiers. Those are the maximum rules in one choice's document, and the sentence that a rule
checked by itself is CONFLICT-FREE by construction. Each of the four sets regulates its own act with one rule, so a
rise from the four sets measures checks routed into Lean, not new assurance, and the report says so. No figure is
predicted here.

## 8. Not claimed, open questions, risks

- **Not claimed.** No completeness of separation (an unseparated pair is equal meaning or a search miss). No theorem
  relates `separatesS` on a norms-shaped document to RD-1's `separates (fillDoc N)` with `fillHolds` (Q3). No
  superposition under the soft completion before SC-10. Nothing about the rights chain or about companions on the
  soft chain. No speed for any batch. No coverage figure and no audit outcome.
- **Q1, limits on the filled tree.** The layered branch checks no generated-layer limit on `fill U` beyond
  `checkAuthorN`'s, and neither does this plan (3.3 step 4). If one is added, the layered branch owns it for every
  caller.
- **Q2, E25 → E15.** S1 still emits `SeparatedByDecisionOnly: <set>: <i>, <j> (not certified)` and shows E25
  (`Readings/Run.lean:256`), although `decision_only_sound` is proved. The flip is the DRI's. Under the completion it
  also needs `decision_only_soundS` (SC-3). Until then the constitution's render gains E25 under each of its four
  sets (the sets become force twins), a readability cost that SC-9 reports.
- **Q3, one separation mechanism.** On the norms chain under the completion, separation runs S1's check on
  `fillDoc N`, and RD-6b's superposed route needs `fillDoc` anyway. Moving the norms chain to filled sides would leave
  `fillDoc` only for superposition. That needs the equality theorem named above; it is a consolidation candidate, not
  part of this plan.
- **Q4, signed changes.** `decided_units` without components adds a field to every enumerated-route answer (SC-7),
  and the gap selection changes separation English on both chains (SC-8). Each needs the DRI's signature.
- **Risk: generator coverage.** The constitution's frame has 15 unspecified predicates and 7 sorts (*recorded*,
  `probes/unspecified-probe.json`). The search must find each pair's decision table and filling, and each choice's
  certificates and countermodels, within budget. A miss leaves a pair unseparated or an answer UNKNOWN. It is
  reported, never worked around (SC-9).
- **Risk: size.** `limitsU` counts soft's derived carve-outs in the AST budget, so a document with many colliding
  default rules may meet `ResourceLimit: AST exceeds 10,000 nodes` sooner under the completion than without it.
  F-SD7's pattern is the test.
- **Risk: the consolidation (SC-1, SC-4, SC-5)** changes merged definitions on the norms chain. The A/B must be
  byte-identical, and any difference stops the batch.

## 9. Review checklist (SC-0)

1. D1's reason: `fillDoc` on a soft document with a default root on an unspecified predicate is `SoftOverHard`
   (F-SD5), and `asU N X` is norm-defaults 2.3's order.
2. `softX`: `softXL` is `softLabelledU` itself; `softX_strict` and `choiceX_normsShaped` are true; `X` precedes
   `Fill_T` in `premisesX` as in `LayeredU.background`.
3. `EntailsX`, `acceptanceX` (with `hX`), `modelCheckX_sound` and the four `_nil` iffs are true under their
   hypotheses.
4. `ChoiceSem` and `HoldsG`: RD-3's `Holds` and `Covers` are `ndSem`'s (`holds_iff_holdsG`), every `foldG_*` is true,
   and universes match RD-3's (witnesses at 0).
5. `sideOfS`: S1's executable reads only the side, `softPremisesIn_fill` holds, and `ObservesF` is S1's `Observes`
   with the filled tree.
6. `separatesS_sound`: the witness's `Fill_T` on its own completion, the other side's not checked (sound, 3.4), the
   base over `authorEnv (fillDoc N)`, and `pairEval`'s first component.
7. `decision_only_soundS`: the twin alone on its act, no sufficient condition; `softX` and `Fill_T` agree with the
   table empty.
8. `admitSD`: the order of 3.3, the decision count in `checkAuthorN`, and no step 4 (Q1).
9. `choiceLayeredG`: `L.U = choiceU N c`, `L.X = choiceX N c`, the norms chain's case byte-identical to RD-2a's.
10. `XEvidence` and `NDEvidence = XEvidence (choiceU N c) []`: RD-3's statements stay true and its A/B stays
    byte-identical.
11. The layered kinds (SC-6): `layered_wire_acceptance` and `wire_report_consequenceX` true; the rights branch
    refused.
12. English: no new wording (D12); the gap selection by the cone (D9); E14's `<decision>` slot; the non-wordings of
    3.9.
13. Conservativity (3.14): K18's `availability` change, and every other fixture of 5.3.
14. Every batch's deletion list, and that no batch leaves a Python fallback for logic it moves into Lean.
15. 4.11 is a sketch: it is not reviewed for PASS here, and SC-10 reviews it before its build.
