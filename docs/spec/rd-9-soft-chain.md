# The soft chain under the unspecified completion (`readings@1` × `soft-norms@0` × `norm-defaults@0`): statement spec (RD-9)

> Status: item-1 statement spec, draft 2 (2026-10-11), branch `design/rd-9`, written from
> [rd-9-soft-chain-PLAN.md](rd-9-soft-chain-PLAN.md) draft 3, which applies the converged plan review
> (`manage-agents/debates/design-rd-9/`). This is what SC-0 reviews: definitions (1), the English (2), the wire (3),
> the semantics in order (4), the diagnostics (5), the exact Lean statements (6) and the acceptance fixtures (8).
>
> Draft 2 applies the statement review (`manage-agents/debates/rd-9-spec/`, Astra and Fable, converged in round 3 on
> FIX with no redesign). The edits are A1 to A4 and F1 to F6, and 12.19 to 12.23 list them:
> **A1** admission keeps its source correspondence: `AdmittedX` gains `graphJson` and `nodes`, and `SourceDecodedX`
> restates today's `SourceDecoded` conjunct by conjunct (6.10), with three substitution fixtures (8.3).
> **A2** the force-twin claim is "only where", the unsaid claim states `excepted_lifts`' three hypotheses, and
> UNDECIDED is claimed only with two opposite admissible fillings (1.6, 8.2).
> **A3** a certificate replayed against a changed conclusion gets diagnostic 11; `valid: false` gets its own case
> (8.3). **A4** the comprehension questions match 2.6 in the plan.
> **F1** `choiceLayeredG` and `ChoiceReplayS` carry `X`'s well-formedness (6.8, 4.4).
> **F2** a fixture isolates `fillHoldsS` (8.1, 8.2). **F3** `probeFormulaOn_eval` ties the gaps to the shown value
> (6.2). **F4** the soft runner's `conflict_free` is stated (3, 4.3, 6.8).
> **F5** `decided_units: []` is pinned, and F-SD2 lists its answers per request kind (8.3). **F6** the gap
> sentence's place in E14 is stated (2.2).
> What remains is the bounded re-check the debate set: only the changed statements (A1, F1, F3) and the new fixture
> values (F2, F5, and A3's four SC-6 cases).
>
> **Elaborated.** Every Lean declaration of section 6 was elaborated against a build of this branch's base
> (`main` at `8b9927f2`; the branch changes only docs) in a scratch stub, `lean/SpecStubs_rd-9.lean`, which is not
> committed (it stays untracked in the worktree). Definitions were elaborated with their bodies. Each theorem a batch must prove was elaborated as
> `def T : Prop := C`. The functions whose bodies are build work (`admitSD`, the replays, `choiceLayeredG`,
> `admitDocumentX`, the soft dispatch) were elaborated as `opaque` declarations of the exact type. Thirty-four short
> statements were also proved in the stub, to check that they hold; 6 marks each *proved in the stub*, and each is
> re-proved in its batch. Draft 2 added three of them: `probeFormulaOn_eval` and its two evaluation lemmas.
> Six `example`s checked that the norms chain's existing definitions are instances (6.5, 6.9, 6.10). Draft 2 added
> five more:
> - `choiceLayered` is still `choiceLayeredG` with conjuncts dropped (6.8);
> - `XEvidence.hX` comes from the source's new conjunct (6.8);
> - `readings_wire_sd_choice_entails` follows from the replay's fields, `acceptanceX` and the conflict theorem (6.8);
> - today's two document decoders are W2's `decodeDoc` (6.10, two examples).
>
> The draft 2 stub was elaborated again in full, with no error. No `sorry` was written. `D1` to `D14` and `E1` to
> `E5` are the plan's decisions and the debate's edits.
>
> **Computed.** Every value marked *computed* in section 8 was evaluated in that stub with `#eval`, and the expression
> is given beside it. Values marked *derived* need the service, Python's generators or the constitution's files, and
> were worked out by reading the sources. Values marked *recorded* are copied from the record named beside them.
>
> No model was called. No code, proof or test changed.
>
> **2026-10-31:** section 13 adds SC-10's statement spec (superposition under the soft completion), which replaces
> the sketch of 6.11. It was written on branch `design/spec-rd9-sc10` from `main` at `09fca5013`.

## 0. Scope, one paragraph

A readings document on the soft chain whose environment holds `norm-defaults@0` beside `readings@1` and
`soft-norms@0`, with a reading set that has content, is admitted and checked on the enumerated route (at most 64
compatible choices). Each document of the route is read as norm-defaults reads a soft document,
`fill (soften (correlate X))`, with soft's premises regenerated on the filled tree as extra base premises `X`
(D1, D2). Separation runs S1's pair check on filled sides (D4). Verdicts fold per-choice rows by one generic fold whose
norms-chain instance is RD-3's (D6, D7). The layered branch of norm-defaults answers the soft branch's `admission` and
`norm-defaults-certificate` through a new dispatch (D8), and one binder binds every certificate (D14). Before any of
that, SC-A gives the norms chain one gap sentence per separation line and `decided_units` without companion sets (D9,
D10). On the constitution's four sets `X = []`, so they gain four fewer invented open terms and the force-twin
finding, not contextual exceptions (plan 0, E2); the conditioned u0073.s05 probe is where `X ≠ []` (C9).

## 1. Definitions

### 1.1 Where this applies

A document is **under the soft completion** exactly when its environment's lower profiles contain `norm-defaults@0`,
its chain is the soft chain, and some reading set is content-bearing (`underSoftCompletion re D`, 6.8). Its route is
the enumerated row (`routeOf`'s abstention row is removed for the soft chain). A document fails the definition in
three ways, each with its route kept:

- on the norms chain it is under RD-2a's completion (`underCompletion`), unchanged;
- on the rights chain it keeps the abstention (`UnsupportedProfile: readings@1 content with norm-defaults@0 is not
  implemented`);
- with no content-bearing set it takes the W2 route; a plain soft document under `norm-defaults@0` reaches the layered
  branch (1.13), where it was refused before.

### 1.2 The documents of the route and their extra premises

`N : NDoc` is RD-1's pair of the decoded document `N.D` and the frame's `unspecified` predicates `N.unspec`. For any
document `X` of the route (`(free N.D).1`, `(one N.D s i).1`, `(choiceDoc N.D c).1`):

- its **norm-defaults document** is `asU N X = ⟨soften (correlate X), N.unspec⟩` (RD-1, unchanged), and its **filled
  tree** is `fill (asU N X)`;
- its **extra base premises**, labelled, are `softXL N X = softLabelledU (asU N X) (correlate X)`: soft's `Exc_T`
  (labels `soft:exception:<rule>:<sufficient|necessary>:<i>`), then `Coh_T` (labels `soft:coherence:<a>,<b>`) with each
  selection read on the filled tree. `softX N X` is the formulas. `freeX`, `oneX N s i` and `choiceX N c` are `softX`
  of the free, the reading's and the choice's document.

`softX N X = []` when `X` has no rights block and only strict rules (`softX_strict`): `Exc_T` comes from default rules
with exception conditions only, and `Coh_T` from colliding pairs of default rules only. So on the norms chain
`choiceX N c = []` (`choiceX_normsShaped`). The converse does not hold: a default rule with no exception condition and
no colliding partner also has `X = []` (F-SD1's default reading, *computed*), which is the case of the constitution's
four sets.

### 1.3 The filled author vocabulary

`filledAuthorEnv N` is the frame's base vocabulary with every `unsaid__p` added (`fillFrameEnv N`), read off the frame
alone. It equals RD-1's `authorEnv (fillDoc N)` by definition (`filledAuthorEnv_eq`, `rfl`), but names no `fillDoc`,
which is not well formed on the soft chain (D1, F-SD5). A separating situation's base is over it: its `unsaid__`
tables are the shared filling.

### 1.4 Admission's facts

- `softShaped D`: the soft chain, a frame with no rule and no rights block, every content an assertion or a rule
  (strict or default, with parties, ranks and exceptions); no bar item.
- `fillRest N`: the names `fill` adds are free (`fillNamesFree`), the free document is `WellFormedU`, and so is every
  reading's document with content. RD-2a's `ndRest N` is `normsShaped N.D && fillRest N` (`ndRest_eq_fillRest`).
- `WellFormedSD N := WellFormedDoc N.D && softShaped N.D && fillRest N` (`wellFormedSD_eq`).
- `decisionCount X`: the number of decision predicates `X` generates, `(decisions (correlate X)).length`, the count
  the layered branch charges `checkAuthorN`'s vocabulary limit with (`decodeSoftU`). It is 0 on a strict document.

### 1.5 Separation on filled sides

- A reading's **filled side** `sideOfS N (one N.D s i)` is S1's `Side` with `S := fill (asU N X)`, its layers
  `layersOf S` and its hidden base environment. S1's executable functions read a side and nothing else.
- On a filled side `backgroundValidOn` evaluates the filled tree's base background and exactly `softX N X`
  (`softPremisesIn_fill`, an equality, *proved in the stub*), and the limitation premises, which are none on the soft
  chain.
- `fillHoldsS N s i M T`: the witness's `Fill_T` holds on its own completion (the base with the witness's tables).
- `separatesS N s i j σ`: the other reading's cells within `maxCells`, S1's pair check `pairEval` (the function the
  route runs) on the two filled sides, and `fillHoldsS` for the witness. The other reading's `Fill_T` is not
  evaluated; that is sound, since `AchievesS` requires it of every completion it admits (plan 3.4).
- `AchievesS N s i B F q v`: `B` is admissible over `filledAuthorEnv N`, and some completion `G` of reading `i`'s own
  decision tables, agreeing with `F` off the keys `i` owns, is base-admissible for the reading's filled document with
  its `X` and `Fill_T` (`BaseAdmissibleX (oneU N s i) (oneX N s i)`) and gives `q` the value `v`, read in the canonical
  expansion of the filled tree (`ObservesF`, S1's `Observes` with `fill (asU N X)` for `soften (correlate X)`).
- `SeparatedS N s i j`: some base, shared tables, probe and value that one reading achieves and the other does not.

### 1.6 Force twins

`AchievesQuietS` is `AchievesS` with the table of the exception key `k₀` empty. The strict and default readings of one
rule differ only where the exception applies (`decision_only_soundS`, SC-3, off the path): with the default twin's
table empty, the two achieve the same values. That is the one direction proved. The converse is not claimed: where the
exception applies the two readings may still agree (F-SD1 with the filling yes, 8.2).

Where the exception applies, the default reading leaves the act unsaid: that is `excepted_lifts` (merged) at
`oneU N s j`, no new statement. It needs three hypotheses:

- the regulated predicate `r` is unspecified (`r.name ∈ N.unspec`);
- the default twin is the only rule on `r` (`rulesOn … r.name = [N]`, which `decisionOnly` checks);
- the excepted formula holds at the tuple.

Its conclusion is `Value3 = .unsaid` (no rule decides the act). That is not the checked status UNDECIDED, which needs
two admissible fillings that give opposite values (F-SD1.status, 8.3).

### 1.7 Entailment and models with `X`

- `premisesX U X Γ := background (fill U) ++ X ++ fillPremises U ++ elaborate (fill U).T ++ Γ`: `X` before `Fill_T`, as
  `LayeredU.background` orders the base. At `X = []` it is `premisesU U Γ` (`premisesX_nil`).
- `BaseAdmissibleX U X B` (merged, `Report.lean`) is `BaseAdmissibleU U B ∧ Sat B X`. `ConflictFreeX U X` (merged,
  `Layered.lean`) is conflict freedom over every such base.
- `EntailsX U X Γ φ`: `φ` holds in every document expansion of a base admissible with `X` where `Γ` holds.
  `CounterX U X Γ φ` and `ConsistentX U X Γ` are RD-3's `CounterU` and `ConsistentU` with `X`. Each is its `U`
  counterpart at `X = []` (the four `_nil` iffs, *proved in the stub*).
- `modelCheckX U X M F Γ φ`: `modelCheckU` with `X` evaluated on the filled model (`extraValid`); at `X = []` it is
  `modelCheckU` (`modelCheckX_nil`).
- `conflictFreeCheckX U X certs`: `conflictFreeCheckU` with the certificates checked over
  `Background_base(E‴) ++ X ++ Fill_T`; at `X = []` it is `conflictFreeCheckU` (`conflictFreeCheckX_nil`).

### 1.8 The one certificate binder

`bindCertX environment U X A own conclusion j` decodes the certificate `j` and binds it (`bindingOk`) to the source
environment canonical under its own profiles, the regenerated premises `premisesX U X A` (encoded) followed by `own`
(the case's premises as written), and `conclusion` as written. `A` is the document's regenerated assertions: a choice's
`(choiceDoc N.D c).2`, or `[]` for a layered source. RD-2a's `ndCertificate`, RD-3's `ndBoundCert` and SC-6's layered
certificate kind are all `bindCertX` (D14). A certificate whose binding leaves out or adds an assertion fails
`bindingOk` (F-SD11).

### 1.9 Per-choice semantics and the fold

`ChoiceSem` collects what a per-choice result claims of a choice: `compat`, `free`, `notFree`, `entails`, `counter`,
`consistent`. `HoldsG S Γ φ c r` is what result `r` claims (RD-3's `Holds` with `S` for `N`); `CoversG S A rs` says the
rows are exactly the compatible choices taking `A`; `RowsHoldG` is the fold theorems' shared hypothesis. The seven
`foldG_*` theorems are RD-3's fold theorems over any `S` (*proved in the stub*).

- `ndSem N` is RD-3's semantics: `Holds N = HoldsG (ndSem N)` (`holds_iff_holdsG`, *proved*) and
  `Covers N = CoversG (ndSem N)` (`covers_iff_coversG`, `Iff.rfl`). RD-3's seven `fold_*_sound` keep their statements
  and become instances.
- `xSem N Xf` is the semantics with an extra base-premise family `Xf : Choice → List Formula`; at `Xf = fun _ => []` it
  is `ndSem` (`xSem_nil`, *proved*). The soft chain's is `sdSem N := xSem N (choiceX N)`, which on a norms-shaped
  document is `ndSem` (`sdSem_normsShaped`).

### 1.10 Evidence with `X`

`XEvidence U X` is one choice's decoded evidence: its conflict certificates (decoded against `L.background`, which holds
`X`), a checked layered witness of `¬ ConflictFreeX U X`, a query certificate or a filled countermodel, a certificate of
`⊥` or a filled model, and the facts `WellFormedU U` and `X` closed over the filled base vocabulary. Its rows
(`xConflictRow`, `xQueryRow e A Γ φ`, `xPremiseRow e A`) are RD-3's rules with `X`. RD-3's `NDEvidence N c` is
`XEvidence (choiceU N c) []`, and its row functions are the rows at `X = []`, value for value (6.9, two `example`s
checked in the stub).

### 1.11 Gaps (D9)

- `probeFormulaOn P q` is the formula `observeOn` evaluates for probe `q` on side `P`, with the tuple it reads it at:
  the outcome base of `p`; the disjunction of the kind's selections on `p`; the conjunction of the assertions.
- `pairGapsOn U P M T q := gapsOf U (tablesModelOn P M T) (tupleVal vs) ψ` with `(ψ, vs) := probeFormulaOn P q`: the
  unsaid atoms the Kleene value of the witness's shown value reads with nothing filled, each with its regulated
  predicate, the tuple's ids and the filling's answer; none where the value is definite.
- A pair's **gaps** lists `pairGapsOn (oneU N s w)` on the witness's side and completion, followed by the other side's
  `pairGapsOn` when `other_value` is shown, with duplicate atoms removed. The other side uses its fixed tables, as
  `other_value` does. `probeFormulaOn_eval`: where `observeOn` shows a value, `probeFormulaOn`'s formula has that value
  at its tuple, so the gaps are read off the formulas of both values the line shows (*proved in the stub*).
  `coneEval_sound`: two fillings that agree on the listed
  atoms give the formula the same value. `coneEval_definite`: a definite value is the value under every filling. No
  minimality is claimed: an atom may be listed that a cleverer selection would drop.

### 1.12 Lean-decided units (D10)

Readings-defaults 1.10, unchanged: a fixed unit with content counts when its conflict status is CONFLICT-FREE or
CONFLICT and its premise status `model` or INCONSISTENT (`fixedDecided`); an open set's unit counts when every
compatible choice's conflict row is CONFLICT-FREE or CONFLICT and every reading's premise status is `model`,
INCONSISTENT, `dead` or `narrowed` (`setDecided`). On the enumerated route without components, under the completion
(either chain), `decided_units` is `partDecided` on the main case's rows, in the document's order (`documentOrder`),
when the request has no `assumed` field (or has `assumed: null`). An explicit `assumed: []` still supplies that field,
so `decided_units` is `[]`, as it is for every supplied list of readings; beyond 64 choices it is `[]`.
The same presence rule applies to each completion subanswer in a component product; the product fold only takes
decided units from a case whose own `assumed` is absent.

### 1.13 The layered branch's soft kinds (D8)

- **The dispatch.** `softCase id kind j` (`NormDefaults/LayeredAdmission.lean`, namespace
  `VE.NormDefaults.Admission`) answers `admission` (by `admitDocumentX`) and
  `norm-defaults-certificate` (by `replayLayeredEntailment`: `bindCertX` and the check over `premisesX L.U L.X`), and
  `none` for any other kind. `NormDefaults/Run.lean`'s `runCase` calls it first when `Wire.hasProfile` holds and
  `Wire.layeredRoute environment = some "soft-norms@0"`, before the `runAdmission` branch.
- **Leaves.** A soft-branch claim graph's leaves may be, beside W2's ordinary provenance: a regenerated layer premise
  of the filled tree (`layer:norms:<p>`, `LayerLeafU`), a pair premise (`background:profile`, `ProfileLeafU`), a
  regenerated soft premise on the filled tree (`soft:exception:…`, `soft:coherence:…`, `SoftLeafX`) or a `Fill_T`
  premise (`unsaid:pair:<r>,<m>`, `FillLeafU`). `LayerLeafU`, `ProfileLeafU`, `FillLeafU` are today's `LayerLeaf`,
  `ProfileLeaf`, `FillLeaf` over the `UDoc` they read (`LayerLeaf s w ↔ LayerLeafU s.U w`, `Iff.rfl`).
- **Bindings.** Certificates in the graph bind the regenerated soft `E‴` JSON (`filledJsonX`: soft's `E′` over the
  placeholder environment with every `unsaid__p` added) under the source profiles without `norm-defaults@0`.
- **The answer.** `encodeAdmittedX`: `admitted`, `report`, `report_id` (bound to the source environment, as
  `runAdmission` binds it), `kinds`, and `conditional_on` (the open coherence labels the report uses, as the soft
  route's admission answer lists them).

## 2. The English (one reading each)

### 2.1 No new sentence (D12)

Every sentence an answer here gets already exists and has passed W7's all-derivations gate. None is an IDE question.

| Sentence | Where it is defined | Used here for |
|---|---|---|
| E14 `This sentence says <source word>. (1) <strict paraphrase> (2) <default paraphrase> They differ here: suppose <decider> decides the exception applies to <subject>. Under (1) <outcome sentence>. Under (2) <outcome sentence>.` | composition 2.2 (S1, W8) | a separation line of force twins under the soft completion, under S1's four conditions |
| The filled-gap sentence `Here the text does not say whether <clause>; this situation answers 'yes'.` (or `'no'`) | norm-defaults 3.2 | after a shown situation, one per entry of the pair's or the result's `gaps`; now also on separation lines (both chains, D9) |
| E25 `It is not certified that these two readings differ only where <decider> decides that the exception applies.`; E15 when certified | composition-s1 2.4; composition 2.2 | the finding `SeparatedByDecisionOnly`, by S1's rule (E25 until the DRI signs S1's flip and, under the completion, `decision_only_soundS` is proved) |
| E12 with R2, R3 and R7 | composition 2.2; readings-defaults 2.1 | verdict lines per reading; R7 for an UNDECIDED point under a reading |
| E3 lines: soft-norms 2.1's exception-condition sentence, soft-norms 2.3's weighing-point sentence | soft-norms 2.1, 2.3 | a used `soft:exception:<rule>:<kind>:<i>` or `soft:coherence:<a>,<b>` label in a CONFLICT-FREE or ALL answer's `conditional_on` |
| E29 `The readings of <citation> were checked one way at a time, not together.` | composition-s2 2.1 | `ReadingsNotSuperposable` with cause `the unspecified completion` |

### 2.2 Which sentences an answer gets

1. **A separation line under the completion (both chains).** S1's line for the pair (E14 for force twins), with
   exactly one filled-gap sentence per entry of the pair's `gaps`, and none for a gap outside it (D9). The gap
   sentences come right after the shown situation. In E14 that is after the supposition ("suppose <decider> decides
   the exception applies to <subject>.") and before "Under (1)", as in 2.5's F-SD1 example, which SC-9 reads. Today
   Python lists every point of every filled table (`filled_gaps`); the constitution's lines show 15 sentences, 14 about
   other acts (*recorded*). After SC-A each shows the one its value reads (C2).
2. **Verdict lines.** Readings-defaults 2.4, unchanged, plus an E3 line for each used soft label. A countermodel under
   a default reading shows its decision with S1's `<decision>` slot and its filled gaps by the cone.
3. **The finding** `SeparatedByDecisionOnly` follows the line, worded by S1's rule (E25 or E15).

### 2.3 The `<reading>` slot

Readings-defaults 2.3, unchanged. On the constitution's four sets the candidates differ only in the verb, so the slot
is the italic verb: *must not* against *should not* (*derived*).

### 2.4 Non-wordings

Readings-defaults 2.5's, and: any `soft__` name, an exception predicate's name, "excepted", "default rule", "X",
"filled side", "cone".

### 2.5 Examples (*derived* wording over *computed* values; the renderers fix the exact sentences)

- **F-SD1** (K1 with `avoid_required` unspecified; the default reading separated from the strict one, `separatesS …
  1 0` true, one gap `avoid_required (a, u)` answered no): "This sentence says *should*. (1) *Every agent must avoid
  deceiving each user.* (2) *Every agent should avoid deceiving each user.* They differ here: suppose the decider
  decides the exception applies to a and u. Here the text does not say whether a must avoid deceiving u; this
  situation answers 'no'. Under (1) a still must. Under (2) a is not required to." Then E25.
- **C2** (u0036.s05's shape, C2′ *computed*: separated with the ambiguity, not without it): the line's one filled-gap
  sentence is "Here the text does not say whether c must seek clarification in s; this situation answers 'no'."
- **C1** verdict line under the default reading (the denial query): "Read sentence *n* as *should not*: the conclusion
  does not follow. It fails here: c is an instance of Claude; suppose the decider decides the exception applies to c.
  Here the text does not say whether c may directly deny being Claude; this situation answers 'yes'."

### 2.6 The comprehension check (E5, SC-9)

The line "Under (2) a is not required to" combines existing wording in a new way, close to the line audit
20261003T0600Z rejected ("deny completions assert 'not required' outside the stated conditions"). SC-9 asks Sonnet 5.5,
as the zero-training reader, one question per rendered separation line of C1 to C4:

- for an obligation (C2, C4): "Does the text say that <subject> need not <act>?";
- for a permission (C1, C3): "Does the text say that <subject> may <act>?".

The expected answer is "no" on all four: the line says what one supposed situation answers, not what the text says.
Each answer is recorded verbatim; a "yes" is reported as a failure of the line, never worked around.

## 3. Wire form and identity

- **`readings-validate`, `readings-separate`** under the soft completion answer S1's rows, computed on filled sides.
  Per reading with content: `fill_premises` (RD's: label `unsaid:pair:<r>,<m>` and AST, on the reading's document) and
  `soft_premises` (`softXL`: label and AST, on the reading's filled tree). Per pair: `gaps`, encoded as `gapsJson`
  (`[[<predicate>, [<id>, …], <value>], …]`). Once: `filled` with `environment` (the lower environment, `unspecified`
  read as `deny`, `norm-defaults@0` removed, each `unsaid__p` added, `withUnsaid`) and `units` (the document's units
  as decoded; no `F_p` unit on the soft chain, since `F_p` is a rule of each filled tree), and `chain` (`soft`, the
  chain the completion took, `Chain.text`; `norms` under 3's norms completion). The client reads `chain` to know which
  completion fields the row carries and derives no chain itself (review F25, DRI condition B1(d)).
- **On the norms chain under the completion** (SC-A), per pair: `gaps`, the same encoding, beside today's fields.
- **`readings-elaborate`**: the enumerated row, with the finding `ReadingsNotSuperposable: <every open set>` and cause
  `the unspecified completion`.
- **`readings-choice`**: the inner kinds of 4.3. For `norm-defaults-certificate` the answer adds `conflict_free`
  and `accepted` (`conflict_free` and `valid`), as today. On the norms chain `conflict_free` is
  `conflictFreeCheckX L.U L.X` on the replayed packages (today's value). On the soft chain it is
  `conflictFreeX x.L (conflictPackages inner)`, the hypothesis of `readings_wire_sd_choice_conflict` and
  `readings_wire_sd_choice_entails` (6.8).
- **`readings-verdicts`**: RD-3's request and answer, plus `decided_units` (1.12) on both chains under the completion.
- **The `norm-defaults` route, soft branch.** `admission`: request `environment`, `document`; answer
  `encodeAdmittedX`. `norm-defaults-certificate`: request `environment`, `norms`, `premises`, `conclusion`,
  `certificate`; answer `valid` and `premises` (the number of regenerated premises, `(premisesX L.U L.X []).length`).
  The rights branch keeps today's answers for both kinds.
- **Identity**: nothing changes. Every filled document, its `X`, every compatible choice and every layered source is
  regenerated from the decoded document at every trusted site and bound to the chain's document hash (DRI D7).
  Certificates and models are evidence, checked against the regenerated premises (DRI D1).

## 4. Semantics, in order

### 4.1 Admission under the soft completion (`admitSD`), stopping at the first error

1. `admitS2 environment document`: S1's and S2a's admission on the soft chain, each `unspecified` read as the
   placeholder `deny` (DRI ruling 4); its texts as today. The abstention no longer applies to the soft chain.
2. `underSoftCompletion b.a.re b.D`, else `UnsupportedProfile: the document is not under the unspecified completion`
   (RD-2a's text; reached only by a request routed here wrongly). `N := ⟨b.D, unspecOf b.a.re b.D⟩`, each reading's
   document read from the request's table (`b.a.side s i = one N.D s i`).
3. `ndTextWith re N b.a.side` (its new body, 6.8): reserved names (`InvalidInput: reserved name <n>`); then `checkAuthorN` with
   `decisionCount` and `WellFormedU` on the free document; then the same on each reading's document with content, in
   admission order (`activeOf`), its text suffixed ` under <set>@<v>:<i>`.
4. `softShaped N.D`, else `InvalidInput: norm-defaults document is not well formed`.
5. When the compatible choices number at most 64, each in canonical order: `sdChoiceText re N c` (S2a's chain text on
   the choice, then step 3's checks on `choiceU N c` with its decision count, suffixed ` under <choice>`).

No filled readings document is admitted (RD-2a's step 4 does not exist here; Q1). The result carries
`WellFormedSD N`, established by steps 1, 3 and 4.

### 4.2 Separation

`replaySeparateS`: `admitSD`; the pair and its situation replayed as S1 replays them, the situation decoded over
`filledEnvironment b.a.re N` (RD-2a's: the frame's author vocabulary with every `unsaid__p`), its base valid over
`filledAuthorEnv N`. The pair is separated when `separatesS` holds (`readings_wire_sd_separate_sound`). The answer's
`gaps` contains the witness side's `pairGapsOn` and, when `other_value` is shown, the other side's, with duplicate
atoms removed. Both sides use their admitted candidate documents and the tables their displayed values read.

### 4.3 Each choice (`readings-choice`)

`replayChoiceS`: `admitSD`; `decodeChoice`; `compatible`, else `InvalidInput: the choice is not a compatible complete
choice`; `sdChoiceText` on this choice (any replayed choice, beyond 64 too), refusing with its text; then
`choiceLayeredG`, the choice's layered source: route `soft-norms@0`, `D := correlate (choiceDoc N.D c).1`,
`U := choiceU N c`, `labelled := softXL N (choiceDoc N.D c).1`, the situation vocabulary soft's prime vocabulary of
`D` (base and decision predicates), and packages bound to the case's environment id, the choice's document hash
(`choiceHash`) and `E‴_base` with the decisions (`withUnsaid U (basePrimeJson D env')`). Beside `L.U = choiceU N c`
and `L.X = choiceX N c`, the source carries `X`'s well-formedness over the filled base vocabulary, which `acceptanceX`
needs. The replay keeps it as `ChoiceReplayS.hXw` (6.8). On the norms chain `choiceLayeredG` is RD-2a's
`choiceLayered` (route `norms@0`, `labelled = []` since `choiceX = []`, so the new conjunct holds vacuously).

The inner kind, by `choiceInnerX`, on both chains:

| Inner kind | Lean check | Theorem it rests on |
|---|---|---|
| `norm-defaults-certificate` (needs the choice's conflict packages), answered first | `bindCertX re.lowerJson L.U L.X (choiceDoc N.D c).2 own conclusion`, then `checkCertificate` over `premisesX L.U L.X ((choiceDoc N.D c).2 ++ Γ)` | `acceptanceX`; `readings_wire_sd_choice_entails` |
| `norm-defaults-elaborate`, `-conflict` (packages or a filled witness), `-status`, `-report` | `layeredCase L` (unchanged) | `layered_conflict_sound`, `witnessConflictX`, `StatusX`'s `sound₁` and `sound₂`, `layered_report_sound` |
| `choice-model` (a base model with decisions and a separate `filling`) | `modelCheckX L.U L.X` | `modelCheckX_sound` |
| any other | `UnsupportedProfile: case kind <k> is not available on the norm-defaults route` | — |

For a certificate, `accepted` also needs `conflict_free`. The soft runner computes it as
`conflictFreeX x.L (conflictPackages inner)`, the hypothesis of the two `sd_choice` theorems; the norms chain keeps
`conflictFreeCheckX L.U L.X x.certs` (3, 6.8).

### 4.4 Verdicts (`readings-verdicts`)

`replayVerdictsSD`: `admitSD`; `supReady`; at most 64 compatible choices (else W2's budget answer and E28, as RD-3);
the choices taking `assumed` (else `ReadingsUnsatisfiable: no compatible reading takes <choice>`); `sdChoiceText` none
on each (else its text); each choice's evidence decoded on its own `choiceLayeredG` source as `XEvidence (choiceU N c)
(choiceX N c)`: packages by `decodePackageX L` (bound to `L.background = Background_base ++ X ++ Fill_T`), the
witness by `witnessConflictX L` (kept as the layered witness), certificates by `bindCertX`, models by `situationX L`
and `decodeFilling`. `XEvidence.hX` comes from the source's well-formedness conjunct (`choiceLayeredG`'s third),
rewritten by its first two; `ChoiceReplayS.hXw` carries the same fact for a single choice. Rows: `xConflictRow`, `xQueryRow`, `xPremiseRow`. Then RD-3's unchanged `foldConflict`,
`foldEntailment` (with its gate) and `foldPremises`; conditions (`restrictionsFor`; `usedLabels` over slot, `Fill_T`
and soft labels in label order); the English plan; and `decided_units` (1.12).

### 4.5 Documents and claim graphs (the layered branch)

`runCase` on a case with the profile and `layeredRoute environment = some "soft-norms@0"` calls `softCase` first:

- `admission`: `admitDocumentX environment document`, with W2's and W1's admission texts in today's order:
  1. W2's document split (`splitDocument`).
  2. `decodeSoftU environment norms`: the soft decoder over the placeholder completions, `checkAuthorN` with the
     decision count, `WellFormedU`. Its soft source `src` is `decodeSoftSource` over `placeholderJson environment`.
  3. Each quoted norm checked as the soft route checks it (`SoftNorms.Admission.checkQuoted src`).
  4. The units decoded by W2's `decodeDoc` over `(fill L.U).E`, with `src`'s literals and flags (today's
     `decodeFilledDoc` is this decoder over its own `fill s.U`).
  5. The graph's `root` and `nodes` read from the submitted `graph`, and its nodes decoded over `(fill L.U).E`.
  6. Certificates bound to `filledJsonX environment L` under `filledProfilesX environment`.
  7. Every node admitted by `NodeAdmittedX`.
  8. The graph checked (`checkGraph`), citations closed and choices compatible.

  `SourceDecodedX` (6.10) states steps 1 to 5 conjunct by conjunct, as today's `SourceDecoded` does.
- `norm-defaults-certificate`: `replayLayeredEntailment`: `decodeSoftU environment norms`; `premises` and `conclusion`
  decoded over `envAt (fill L.U) (size (fill L.U))`; the certificate bound by `bindCertX environment L.U L.X [] premises
  conclusion`; `valid` is `checkCertificate` over `premisesX L.U L.X premises`.
- Every other kind falls through to today's branches (`runOtherCase`, which sends `norm-defaults-*` kinds on a layered
  source to `runLayered`).

### 4.6 Conservativity

Plan 3.14, as amended: only documents under the soft completion reach the soft runners (an `availability` change:
K18 is admitted on the enumerated row, with K1's validate and separate rows and the answers F-SD2 lists per request
kind); the norms chain's answers are byte-identical except the signed `gaps` and
`decided_units` additions (SC-A); `layeredCase` is unchanged and `Layered.lean` changes in one comment;
`normDefaults_wire_admission` gains one signed hypothesis, its only statement change.

## 5. Diagnostics, in order

| # | Text | When |
|---|---|---|
| 1 | S1's and S2a's admission texts on the soft chain | as today (4.1 step 1) |
| 2 | `InvalidInput: reserved name <n>` | a unit id, rule name or declared name begins `unsaid--` (4.1 step 3) |
| 3 | `checkAuthorN`'s texts in its order, then `InvalidInput: norm-defaults document is not well formed`; a reading's suffixed ` under <set>@<v>:<i>` | the free document, then each reading's (4.1 step 3); `ResourceLimit: vocabulary size` counts that document's decision predicates (F-SD7, *computed*) |
| 4 | `InvalidInput: norm-defaults document is not well formed` | `softShaped` fails (4.1 step 4) |
| 5 | S2a's chain text on the choice, then row 3's texts on `choiceU N c`, suffixed ` under <choice>` | each compatible choice, at most 64 (4.1 step 5), and any replayed choice (4.3) |
| 6 | `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` | the rights chain (unchanged) |
| 7 | `UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented` | a companion on the soft chain (RD-4a, unchanged) |
| 8 | `UnsupportedProfile: norm-defaults@0 documents on the rights route await the Lean route` | `ve document` on the rights route (text narrowed from "soft and rights routes"; SC-8) |
| 9 | S1's situation texts (`InvalidInput: invalid situation <id>`, `distinguishing model violates a generated premise`) | a separation's base names a decision predicate, or the witness's `Fill_T` fails (`fillHoldsS`) |
| 10 | `InvalidModel(norm-defaults): <n> is a filling; supply it as a filling, not a table` | an `unsaid__` table in a layered situation's `relations` (`situationX`, unchanged) |
| 11 | `certificate is stale or bound to different inputs` | a certificate whose binding is not `bindCertX`'s (F-SD11), including one replayed against a changed conclusion; a claim-graph certificate whose node was substituted (SC-6). `bindingOk`'s text, unchanged |
| 12 | `InvalidInput: a reading's certificate needs the choice's conflict packages` | a choice certificate without `conflict` (unchanged) |
| 13 | `ReadingsUnsatisfiable: no compatible reading takes <choice>` | RD-3, unchanged |
| 14 | `UnsupportedProfile: case kind <k> is not available on the norm-defaults route` | an inner kind `choiceInnerX` does not answer (unchanged) |

When AR-13's `Code` enumeration lands (DRI D6), each text gets its code, with the text unchanged.

## 6. Lean: definitions and the exact statements to prove

### 6.1 Files, placement and import order

Placement (D13): each general definition with `X` goes in the file that owns its `X = []` case; new `Soft*` files hold
only soft-specific code.

| Batch | File | Declarations |
|---|---|---|
| SC-A | `NormDefaults/Evidence.lean` | `coneEval_sound`, `coneEval_definite` (6.2) |
| SC-A | `Readings/VerdictsWire.lean` | `probeFormulaOn`, `pairGapsOn`, `probeFormulaOn_eval` (with `anyF_eval`, `conj_eval`); `readingPremise`, `partDecided`, `documentOrder` moved after `droppedBy`; adds `import VE.Readings.Components` (6.2) |
| SC-1 | `NormDefaults/LayeredEntail.lean` (new; imports `NormDefaults.Layered`) | 6.3 |
| SC-1 | `Readings/SoftDefaults.lean` (new; imports `Readings.Unspecified`, `NormDefaults.LayeredEntail`) | 6.4 |
| SC-1 | `Readings/Verdicts.lean` after `covers_mem` | 6.5 |
| SC-2 | `Readings/SoftSeparate.lean` (new; imports `SoftDefaults`, `Scan`) | 6.6 |
| SC-3 | `Readings/SoftForce.lean` (new; imports `SoftSeparate`, `Force`) | 6.7 |
| SC-6 | `NormDefaults/LayeredAdmission.lean` (new; imports `LayeredEntail`, `NormDefaults.Admission`, `SoftNorms.Wire`); `NormDefaults/Run.lean` (imports it); `NormDefaults/Admission.lean` (leaves over a `UDoc`) | 6.10 |
| SC-4 | `Readings/UnspecifiedWire.lean` (adds `import VE.Readings.SoftDefaults`; `ndDocTextG`, `decisionCount`, `ndTextWith`'s new body, `fillRest`, `choiceLayeredG`, `choiceCertificateX`, `choiceModelX`, `choiceInnerX`); `Readings/SoftWire.lean` (new; imports `SoftSeparate`, `UnspecifiedWire`: `underSoftCompletion`, `sdChoiceText`, `AdmittedSD`, `admitSD`, the replays and the wire theorems) | 6.8 |
| SC-5 | `Readings/VerdictsWire.lean` (`XEvidence` and its rows); `Readings/SoftVerdicts.lean` (new; imports `SoftWire`, `VerdictsWire`) | 6.9 |
| SC-10 | `Readings/SoftSup.lean` (new; imports `SoftVerdicts`, `SupExtra`) | 13 |

The import graph stays acyclic: `LayeredEntail` imports nothing from `Readings`; `SoftDefaults` imports `Unspecified`
(which does not import `UnspecifiedWire`); `UnspecifiedWire` → `SoftDefaults` adds no back edge; `Components`
imports only `Verdicts`, so `VerdictsWire` → `Components` adds none; `LayeredAdmission` imports `Layered` and is
imported by `NormDefaults/Run.lean` only, so `Layered.lean` never calls it.

### 6.2 SC-A: the cone and the norms chain's gains

```lean
namespace VE.NormDefaults
universe u

/-- Two fillings that agree on the atoms the cone lists give the formula the same value. -/
theorem coneEval_sound {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (ρ : List α)
    (ψ : VE.Formula) (F G : FiniteFill U α) (hFG : ∀ a ∈ (coneEval U M ρ ψ).2, a.2 ∈ F a.1 ↔ a.2 ∈ G a.1) :
    ψ.eval (M.withFill F) ρ = ψ.eval (M.withFill G) ρ
/-- A definite Kleene value is the value under every filling. -/
theorem coneEval_definite {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (ρ : List α)
    (ψ : VE.Formula) (b : Bool) (h : (coneEval U M ρ ψ).1 = some b) (F : FiniteFill U α) :
    ψ.eval (M.withFill F) ρ = b
end VE.NormDefaults

namespace VE.Readings
open VE.Rights (correlate)

/-- The formula a probe reads on a side and the tuple it is read at (D9): `observeOn`'s formulas. -/
def probeFormulaOn {α : Type} (P : Side) : Probe α → VE.Formula × List α
  | .outcome p vs => (VE.Norms.outcomeBaseIn P.S P.L p, vs)
  | .selects k p vs => (VE.Norms.anyF ((selectable P.X k p).map (fun N =>
      VE.Norms.substIn P.L P.L.syms.length (VE.SoftNorms.selectsOn P.S (correlate P.X) N))), vs)
  | .holds => (conj (P.A.map (VE.Norms.substIn P.L P.L.syms.length)), [])

/-- A pair's `gaps` (D9): the filled gaps of the witness's shown value, by `gapsOf` on the witness's completion. -/
def pairGapsOn (U : VE.NormDefaults.UDoc) (P : Side) (M : VE.FiniteModel VE.Bridge.Entity)
    (T : List (GenKey × List (List VE.Bridge.Entity))) (q : Probe VE.Bridge.Entity) :
    List (String × List String × Bool) :=
  Wire.gapsOf U (tablesModelOn P M T) (VE.Norms.tupleVal (probeFormulaOn P q).2) (probeFormulaOn P q).1

/-- The selection case's formula evaluates as `observeOn`'s `any`. -/
theorem anyF_eval {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (ρ : List α) (l : List VE.Formula) :
    (VE.Norms.anyF l).eval M ρ = l.any (·.eval M ρ)                                     -- proved in the stub
/-- The assertion case's formula evaluates as `observeOn`'s `all`. -/
theorem conj_eval {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (ρ : List α) :
    ∀ l : List VE.Formula, (conj l).eval M ρ = l.all (·.eval M ρ)                        -- proved in the stub
/-- The gaps describe the value the line shows (D9): where `observeOn` gives a value, `probeFormulaOn`'s formula has
    that value at its tuple. -/
theorem probeFormulaOn_eval {α : Type} [DecidableEq α] (P : Side) (M : VE.FiniteModel α) (q : Probe α) (v : Bool)
    (h : observeOn P M q = some v) :
    (probeFormulaOn P q).1.eval M (VE.Norms.tupleVal (probeFormulaOn P q).2) = v       -- proved in the stub
end VE.Readings
```

The placement is the stub's; in the build `probeFormulaOn`, `pairGapsOn` and the three theorems sit in
`VerdictsWire.lean` beside `gapsOf`. `probeFormulaOn_eval` is a case split on the probe:
- outcome probes: when the regulated predicate is missing or in conflict, `observeOn` returns `none`, so the hypothesis
  excludes them;
- the selection case uses `anyF_eval`;
- the assertion case uses `conj_eval`.

With `M := tablesModelOn P M T` it reads `sideValueOn P M T q = some v`, the value the line shows, and
`pairGapsOn` evaluates the same formula at the same tuple on the same model. The moved functions keep their types (checked in the stub):
`readingPremise : Doc → List RowInfo → List (String × Nat) → ReadingSet → Nat → Premise`,
`partDecided : Doc → List RowInfo → List (String × Nat) → List String`,
`documentOrder : Json → List String → List String`. The answer's member, in `runVerdicts` under the completion:
`("decided_units", toJson (documentOrder (j.getObjValD "document") (if assumed.isNone then partDecided D infos dead else
[])))` with `infos := ndInfos x` and `dead := ((deadOf D infos deadJ).1).getD []`; `[]` on the over-64 branch.
Per pair, `readings-validate` and `readings-separate` under the completion add the witness's `pairGapsOn`, followed
by the other side's when `other_value` is shown, with duplicate atoms removed. Each side uses the tables its displayed
value reads.

If SC-A does not prove `coneEval_sound` and `coneEval_definite`, it adds neither, and the selection is listed under 7.

### 6.3 SC-1: entailment and models with `X` (`NormDefaults/LayeredEntail.lean`)

```lean
namespace VE.NormDefaults
open VE.Norms
universe u

def Wire.premisesX (U : UDoc) (X Γ : List VE.Formula) : List VE.Formula :=
  background (fill U) ++ X ++ fillPremises U ++ elaborate (fill U).T ++ Γ
theorem Wire.premisesX_nil (U : UDoc) (Γ : List VE.Formula) : Wire.premisesX U [] Γ = Wire.premisesU U Γ
  -- proved in the stub

def EntailsX (U : UDoc) (X Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) →
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

theorem baseAdmissibleX_nil (U : UDoc) (B : VE.Structure.{u}) :
    Wire.BaseAdmissibleX U [] B ↔ BaseAdmissibleU U B                                  -- proved in the stub
theorem entailsX_nil (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U [] Γ φ ↔ EntailsU.{u} U Γ φ                                          -- proved in the stub
theorem conflictFreeX_nil (U : UDoc) : Wire.ConflictFreeX.{u} U [] ↔ ConflictFreeU.{u} U -- proved in the stub

theorem acceptanceX (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesX U X Γ) φ cert = true) :
    EntailsX.{u} U X Γ φ

/-- Every target's certificate accepted over `Background_base(E‴) ++ X ++ Fill_T`. -/
def Wire.conflictFreeCheckX (U : UDoc) (X : List VE.Formula) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (fill U)).length == certs.length &&
    ((targets (fill U)).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (fill U) 0) (backgroundBase (fill U) ++ X ++ fillPremises U)
          (targetConclusion t) c
      | none => false)
theorem Wire.conflictFreeCheckX_nil (U : UDoc) (certs : List (Option VE.Tableau.Certificate)) :
    Wire.conflictFreeCheckX U [] certs = Wire.conflictFreeCheckU U certs                 -- proved in the stub
theorem Wire.conflictFreeCheckX_sound (U : UDoc) (h : WellFormed (fill U) = true) (X : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) (hc : Wire.conflictFreeCheckX U X certs = true) :
    Wire.ConflictFreeX.{u} U X

def modelCheckX (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : FiniteFill U VE.Bridge.Entity) (Γ : List VE.Formula) (φ : VE.Formula) : Bool × Bool :=
  ((modelCheckU U M F Γ φ).1 && Wire.extraValid U X M F, (modelCheckU U M F Γ φ).2)
theorem modelCheckX_nil (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity) (F : FiniteFill U VE.Bridge.Entity)
    (Γ : List VE.Formula) (φ : VE.Formula) : modelCheckX U [] M F Γ φ = modelCheckU U M F Γ φ -- proved in the stub
theorem modelCheckX_sound (U : UDoc) (h : WellFormedU U = true) (X : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0)) (F : FiniteFill U VE.Bridge.Entity)
    (Γ : List VE.Formula) (φ : VE.Formula) (hm : (modelCheckX U X M F Γ φ).1 = true) :
    Wire.BaseAdmissibleX U X (withFill U M.asStructure (finFill M F)) ∧
    (∀ a ∈ Γ, (subst (fill U).T (size (fill U)) a).denote (withFill U M.asStructure (finFill M F)) []) ∧
    ((subst (fill U).T (size (fill U)) φ).denote (withFill U M.asStructure (finFill M F)) [] ↔
      (modelCheckX U X M F Γ φ).2 = true)
end VE.NormDefaults

namespace VE.NormDefaults.Wire
open Lean
open VE.Norms

/-- The one certificate binder (D14). -/
def bindCertX (environment : Json) (U : UDoc) (X A : List VE.Formula) (own : List Json) (conclusion : Json)
    (j : Json) : Except String VE.Tableau.Certificate := do
  let cert ← VE.CertificateWire.decodeCertificate j
  VE.Route.Wire.bindingOk (profilesOf environment) (← canonicalEnvironmentJsonU environment)
    ((premisesX U X A).map enc ++ own) conclusion cert.environment_id cert.premise_meaning_ids
    cert.conclusion_meaning_id
  pure cert
end VE.NormDefaults.Wire
```

`ndCertificate` and `ndBoundCert` bind through `bindCertX re.lowerJson (choiceU N c) [] (choiceDoc N.D c).2 own
conclusion`, whose premise list is today's (`premisesX_nil`).

### 6.4 SC-1: the soft chain's documents (`Readings/SoftDefaults.lean`)

```lean
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
def softShaped (D : Doc) : Bool :=
  D.chain == .soft && D.frame.soft.T.nodes.isEmpty && noRights D.frame &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => contentSoft c
    | .bar _ _ => false
    | .set R => R.candidates.all (fun a => (a.content.map contentSoft).getD true))

def softXL (N : NDoc) (X : RightsDoc) : List (String × VE.Formula) :=
  VE.NormDefaults.Wire.softLabelledU (asU N X) (correlate X)
def softX (N : NDoc) (X : RightsDoc) : List VE.Formula := (softXL N X).map (·.2)
def freeX (N : NDoc) : List VE.Formula := softX N (free N.D).1
def oneX (N : NDoc) (s : String) (i : Nat) : List VE.Formula := softX N (one N.D s i).1
def choiceX (N : NDoc) (c : Choice) : List VE.Formula := softX N (choiceDoc N.D c).1

theorem softX_strict (N : NDoc) (X : RightsDoc) (hr : noRights X = true) (hs : allStrict X = true) :
    softX N X = []                                                                       -- proved in the stub
theorem choiceX_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) :
    choiceX N c = []                                                                     -- proved in the stub
theorem softX_wellFormed (N : NDoc) (X : RightsDoc) (hs : VE.SoftNorms.WellFormedSoft (correlate X) = true)
    (hw : VE.NormDefaults.WellFormedU (asU N X) = true) :
    ∀ a ∈ softX N X, a.WellFormed (envAt (VE.NormDefaults.fill (asU N X)) 0) []

def filledAuthorEnv (N : NDoc) : VE.Environment :=
  envAt { N.D.frame.soft with E := fillFrameEnv N }.base 0
theorem filledAuthorEnv_eq (N : NDoc) : filledAuthorEnv N = authorEnv (fillDoc N)  -- `rfl`, in the stub

def WellFormedSD (N : NDoc) : Bool :=
  WellFormedDoc N.D && softShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))
end VE.Readings
```

`fillRest` (in `UnspecifiedWire.lean`, 6.8) states the shared conjuncts once: `ndRest_eq_fillRest` and
`wellFormedSD_eq` (*proved in the stub*).

### 6.5 SC-1: one fold over a per-choice semantics (`Readings/Verdicts.lean`, after `covers_mem`)

```lean
namespace VE.Readings
open VE.Norms (Sat restrictAll DocumentExpansion)
open VE.NormDefaults (UDoc fill EntailsU)
universe u

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

theorem coversG_row {S : ChoiceSem} {A : Choice} {rs : List (Choice × ChoiceResult)} (hc : CoversG S A rs)
    {c : Choice} (hcc : S.compat c) (hA : ∀ x ∈ A, x ∈ c) : ∃ r, (c, r) ∈ rs        -- proved in the stub
theorem coversG_mem {S : ChoiceSem} {A : Choice} {rs : List (Choice × ChoiceResult)} (hc : CoversG S A rs)
    {x : Choice × ChoiceResult} (hx : x ∈ rs) : S.compat x.1 ∧ ∀ y ∈ A, y ∈ x.1      -- proved in the stub

-- The seven generic fold theorems, each proved in the stub (RD-3's proof with `S` for `N`):
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

def CounterX (U : UDoc) (X Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0}, VE.NormDefaults.Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) ∧
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S ∧ Sat S Γ ∧ ¬ φ.denote S []
def ConsistentX (U : UDoc) (X Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0}, VE.NormDefaults.Wire.BaseAdmissibleX U X (restrictAll (fill U).T S) ∧
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S ∧ Sat S Γ
theorem counterX_nil (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) :
    CounterX U [] Γ φ ↔ CounterU U Γ φ                                                  -- proved in the stub
theorem consistentX_nil (U : UDoc) (Γ : List VE.Formula) : ConsistentX U [] Γ ↔ ConsistentU U Γ  -- proved

def ndSem (N : NDoc) : ChoiceSem where
  compat c := Compatible N.D c
  free c := VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
  notFree c := ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
  entails c Γ φ := EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  counter c Γ φ := CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  consistent c := ConsistentU (choiceU N c) (choiceDoc N.D c).2
theorem holds_iff_holdsG (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) (r : ChoiceResult) :
    Holds.{u} N Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r                                 -- proved in the stub
theorem covers_iff_coversG (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) :
    Covers N A rs ↔ CoversG (ndSem.{u} N) A rs                                         -- `Iff.rfl`, in the stub

def xSem (N : NDoc) (Xf : Choice → List VE.Formula) : ChoiceSem where
  compat c := Compatible N.D c
  free c := VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU N c) (Xf c)
  notFree c := ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU N c) (Xf c)
  entails c Γ φ := VE.NormDefaults.EntailsX.{u} (choiceU N c) (Xf c) ((choiceDoc N.D c).2 ++ Γ) φ
  counter c Γ φ := CounterX (choiceU N c) (Xf c) ((choiceDoc N.D c).2 ++ Γ) φ
  consistent c := ConsistentX (choiceU N c) (Xf c) (choiceDoc N.D c).2
theorem xSem_nil (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) (r : ChoiceResult) :
    HoldsG (xSem.{u} N (fun _ => [])) Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r          -- proved in the stub
end VE.Readings
```

RD-3's seven `fold_*_sound` keep their statements; each proof becomes `foldG_*_sound (ndSem N)` through
`holds_iff_holdsG` (checked in the stub for `fold_all_sound`). The generic lemmas are named `coversG_row` and
`coversG_mem`; RD-3's `covers_row` and `covers_mem` keep their names and statements.

### 6.6 SC-2: separation on filled sides (`Readings/SoftSeparate.lean`)

```lean
namespace VE.Readings
open VE.Norms (Regulated tupleVal envAt)
open VE.SoftNorms (SoftNode canon)
open VE.Rights (RightsDoc correlate)
universe u

def sideOfS (N : NDoc) (X : RightsDoc × List VE.Formula) : Side :=
  let S := VE.NormDefaults.fill (asU N X.1)
  let L := VE.Norms.layersOf S
  ⟨X.1, X.2, genKeys X.1, S, L, VE.Norms.hide S.E L.names⟩

theorem excLabels_length (D : VE.SoftNorms.SoftDoc) :
    (VE.SoftNorms.Wire.excLabels D).length = (VE.SoftNorms.excPremises D).length       -- proved in the stub
theorem softPremisesIn_fill (N : NDoc) (X : RightsDoc) :
    VE.SoftNorms.softPremisesIn (correlate X) (VE.NormDefaults.fill (asU N X))
      (VE.Norms.layersOf (VE.NormDefaults.fill (asU N X))) = softX N X                  -- proved in the stub

def fillHoldsS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  (VE.NormDefaults.fillPremises (oneU N s i)).all (fun φ => φ.eval (tablesModel (one N.D s i).1 M T) [])

def separatesS {α : Type} [DecidableEq α] (N : NDoc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  let Pi := sideOfS N (one N.D s i)
  let Pj := sideOfS N (one N.D s j)
  decide (cellsOn N.D s j Pj σ.base ≤ maxCells) &&
  (pairEval (m := Id) (pure ()) (pure ()) N.D s i j Pi Pj σ).1 &&
  fillHoldsS N s i σ.base (tablesForOf Pi.X (σ.fixed ++ σ.decisions))

def ObservesF (N : NDoc) (X : RightsDoc) (A : List VE.Formula) (B : VE.Structure.{u}) :
    Probe B.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ VE.TupleTyped B r.sorts vs ∧
      VE.Norms.Value (VE.NormDefaults.fill (asU N X)).T r (canon (VE.NormDefaults.fill (asU N X)) B) vs = some v
  | .selects k p vs, v => VE.TupleTyped B (VE.SoftNorms.sortsOf (correlate X) p) vs ∧
      ((∃ M ∈ selectable X k p, VE.Norms.SelectsD (VE.NormDefaults.fill (asU N X)).T
          (canon (VE.NormDefaults.fill (asU N X)) B) (tupleVal vs)
          (VE.Norms.fuel (VE.NormDefaults.fill (asU N X)).T) (VE.SoftNorms.primeNode (correlate X) M)) ↔ v = true)
  | .holds, v => ((∀ a ∈ A, a.denote (canon (VE.NormDefaults.fill (asU N X)) B) []) ↔ v = true)

def AchievesS (N : NDoc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (filledAuthorEnv N) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned N.D s i k = false → ∀ vs, G k vs ↔ F k vs) ∧
    VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s i) (oneX N s i) (withTables (one N.D s i).1 B G) ∧
    ObservesF N (one N.D s i).1 (one N.D s i).2 (withTables (one N.D s i).1 B G) q v
def SeparatedS (N : NDoc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (AchievesS N s i B F q v ∧ ¬ AchievesS N s j B F q v) ∨ (AchievesS N s j B F q v ∧ ¬ AchievesS N s i B F q v)

theorem separatesS_sound {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (hj : (candidate N.D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (filledAuthorEnv N)) (h : separatesS N s i j σ = true) :
    AchievesS N s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
      ¬ AchievesS N s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value
theorem separatesS_separated {α : Type} [DecidableEq α] (N : NDoc) (hN : WellFormedSD N = true) (s : String)
    (i j : Nat) (hi : (candidate N.D s i).bind (·.content) ≠ none) (hj : (candidate N.D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (filledAuthorEnv N)) (h : separatesS N s i j σ = true) :
    SeparatedS.{0} N s i j

-- The two lemmas that replace S1's side lemmas; the first proved in the stub.
theorem sideValidOn_sideOfS_iff {α : Type} [DecidableEq α] (N : NDoc) (X : RightsDoc × List VE.Formula)
    (hr : noRights X.1 = true) (M : VE.FiniteModel α) (T : List (GenKey × List (List α))) :
    sideValidOn (sideOfS N X) M T = true ↔
      tablesTypedOn (sideOfS N X) M T = true ∧
      VE.Norms.backgroundValid (VE.NormDefaults.fill (asU N X.1)) (tablesModelOn (sideOfS N X) M T) = true ∧
      ∀ a ∈ softX N X.1, a.eval (tablesModelOn (sideOfS N X) M T) [] = true
theorem observeOn_sideOfS_sound {α : Type} [DecidableEq α] (N : NDoc) (X : RightsDoc × List VE.Formula)
    (hw : VE.NormDefaults.WellFormedU (asU N X.1) = true)
    (hA : ∀ a ∈ X.2, a.WellFormed (envAt (VE.NormDefaults.fill (asU N X.1))
      (VE.Norms.size (VE.NormDefaults.fill (asU N X.1)))) [])
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (VE.NormDefaults.fill (asU N X.1)) 0))
    (hb : VE.Norms.backgroundValid (VE.NormDefaults.fill (asU N X.1)) M = true)
    (q : Probe α) (hq : probeTyped X.1 M q = true) (v : Bool) :
    observeOn (sideOfS N X) M q = some v ↔ ObservesF N X.1 X.2 M.asStructure q v
end VE.Readings
```

Proof notes, from the plan's 4.5: `separates_witness` and `separates_other` read only S1's table lemmas and the side's
admissibility and observation, so the proof reuses them with `sideValidOn_sideOfS_iff` and
`observeOn_sideOfS_sound` for S1's side lemmas, `pairEval_id`'s argument for the first component, and `fillHoldsS`
for the witness's `Fill_T`.

### 6.7 SC-3: force twins under the completion (`Readings/SoftForce.lean`, off the path)

```lean
namespace VE.Readings
universe u

def AchievesQuietS (N : NDoc) (s : String) (j : Nat) (k₀ : GenKey) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (filledAuthorEnv N) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned N.D s j k = false → ∀ vs, G k vs ↔ F k vs) ∧ (∀ vs, ¬ G k₀ vs) ∧
    VE.NormDefaults.Wire.BaseAdmissibleX (oneU N s j) (oneX N s j) (withTables (one N.D s j).1 B G) ∧
    ObservesF N (one N.D s j).1 (one N.D s j).2 (withTables (one N.D s j).1 B G) q v

theorem decision_only_soundS (N : NDoc) (hN : WellFormedSD N = true) (s : String) (i j : Nat) (k₀ : GenKey)
    (h : decisionOnly N.D s i j = some k₀) (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier)
    (v : Bool) : AchievesS N s i B F q v ↔ AchievesQuietS N s j k₀ B F q v
end VE.Readings
```

### 6.8 SC-4: admission, route, separation and each choice

In `Readings/UnspecifiedWire.lean` (the norms chain's owner, D13) and `Readings/SoftWire.lean` (soft-specific):

```lean
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Norms (envAt size)
open VE.Rights (RightsDoc correlate)
universe u

-- UnspecifiedWire.lean
def ndDocTextG (re : ReadingsEnvironment) (generated : Nat) (U : VE.NormDefaults.UDoc) : Option String :=
  match VE.NormDefaults.Wire.checkAuthorN re.lowerJson generated U with
  | .error e => some e
  | .ok () => if VE.NormDefaults.WellFormedU U then none else some "InvalidInput: norm-defaults document is not well formed"
theorem ndDocText_eq_G (re : ReadingsEnvironment) (U : VE.NormDefaults.UDoc) :
    ndDocText re U = ndDocTextG re 0 U                                     -- `rfl` against today's `ndDocText`, in the stub
theorem wellFormedU_of_ndDocTextG {re : ReadingsEnvironment} {g : Nat} {U : VE.NormDefaults.UDoc}
    (h : ndDocTextG re g U = none) : VE.NormDefaults.WellFormedU U = true               -- proved in the stub
def decisionCount (X : RightsDoc) : Nat := (VE.SoftNorms.decisions (correlate X)).length
/-- 4.1 step 3 on both chains: `ndTextWith`'s new body (one definition, elaborated in the stub under the name
    `sdTextWith`); on the norms chain every `decisionCount` is 0 (`decisions_strict`), so its value is today's. -/
def ndTextWith (re : ReadingsEnvironment) (N : NDoc) (side : String → Nat → RightsDoc × List VE.Formula) :
    Option String :=
  ((reservedUnsaid N).map (s!"InvalidInput: reserved name {·}")).or <|
  (ndDocTextG re (decisionCount (free N.D).1) (freeU N)).or <|
  firstSome (activeOf N.D) (fun c =>
    (ndDocTextG re (decisionCount (side c.1.id c.2).1) (asU N (side c.1.id c.2).1)).map
      (· ++ s!" under {c.1.id}@{c.1.version}:{c.2}"))
def fillRest (N : NDoc) : Bool :=
  fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))
theorem ndRest_eq_fillRest (N : NDoc) : ndRest N = (normsShaped N.D && fillRest N)        -- proved in the stub
theorem wellFormedSD_eq (N : NDoc) :
    WellFormedSD N = (WellFormedDoc N.D && softShaped N.D && fillRest N)                 -- proved in the stub

/-- The choice's document as the layered branch's source, on either chain (4.3). -/
def choiceLayeredG (b : Admitted2) (N : NDoc) (c : Choice)
    (wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true) :
    Except String {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU N c ∧ L.X = choiceX N c ∧
      ∀ a ∈ L.X, a.WellFormed (envAt (VE.NormDefaults.fill L.U) 0) []}

-- SoftWire.lean
def underSoftCompletion (re : ReadingsEnvironment) (D : Doc) : Bool :=
  re.lower.contains normDefaultsProfile && re.chain == .soft && D.sets.any contentBearing
/-- 4.1 step 5 on the soft chain: S2a's chain text on the choice of the unfilled document (the norms chain's runs on
    `fillDoc N`, `choiceStepText`), then step 3's checks on `choiceU N c`. -/
def sdChoiceText (re : ReadingsEnvironment) (N : NDoc) (c : Choice) : Option String :=
  (choiceChainText N.D c).or
    ((ndDocTextG re (decisionCount (choiceDoc N.D c).1) (choiceU N c)).map (· ++ " under " ++ choiceText N.D c))

structure AdmittedSD where
  b : Admitted2
  N : NDoc
  hN : N.D = b.D
  wf : WellFormedSD N = true
  side : ∀ s i, b.a.side s i = one N.D s i
/-- 4.1. -/
def admitSD (environment document : Json) : Except String AdmittedSD

structure SeparateReplayS where
  r : AdmittedSD
  set : String
  witness : Nat
  other : Nat
  hw : (candidate r.N.D set witness).bind (·.content) ≠ none
  ho : (candidate r.N.D set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  valid : σ.base.Valid (filledAuthorEnv r.N)
/-- 4.2. -/
def replaySeparateS (j : Json) : Except String SeparateReplayS

theorem readings_wire_sd_separate_sound (j : Json) (x : SeparateReplayS) (h : replaySeparateS j = .ok x)
    (hs : separatesS x.r.N x.set x.witness x.other x.σ = true) :
    AchievesS x.r.N x.set x.witness x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value ∧
      ¬ AchievesS x.r.N x.set x.other x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value

structure ChoiceReplayS where
  r : AdmittedSD
  c : Choice
  hc : Compatible r.N.D c
  wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true
  L : VE.NormDefaults.Wire.LayeredU
  hU : L.U = choiceU r.N c
  hX : L.X = choiceX r.N c
  hXw : ∀ a ∈ L.X, a.WellFormed (envAt (VE.NormDefaults.fill L.U) 0) []
/-- 4.3: `sdChoiceText` on its own choice, refusing with its text, then `choiceLayeredG`. -/
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

-- UnspecifiedWire.lean, the runners: the choice inner kinds on both chains (4.3).
namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Norms (envAt size)
open VE.NormDefaults (fill)

def choiceCertificateX (re : ReadingsEnvironment) (L : VE.NormDefaults.Wire.LayeredU) (A : List VE.Formula)
    (inner : Json) : Except String (List (String × Json)) := do
  unless (inner.getObjVal? "conflict") matches .ok (.obj _) do
    throw "InvalidInput: a reading's certificate needs the choice's conflict packages"
  let E := envAt (fill L.U) (size (fill L.U))
  let (Γ, φ) ← choiceFormulas E (if inner.getObjValD "premises" == .null then inner.setObjVal! "premises" (.arr #[])
    else inner)
  let own ← match inner.getObjValD "premises" with
    | .null => pure []
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: premises must be an array"
  let cert ← VE.NormDefaults.Wire.bindCertX re.lowerJson L.U L.X A own (inner.getObjValD "conclusion")
    (← inner.getObjVal? "certificate")
  let valid := VE.Tableau.checkCertificate E (VE.NormDefaults.Wire.premisesX L.U L.X (A ++ Γ)) φ cert
  pure [("valid", .bool valid), ("premises", toJson (VE.NormDefaults.Wire.premisesX L.U L.X (A ++ Γ)).length)]

def choiceModelX (L : VE.NormDefaults.Wire.LayeredU) (A : List VE.Formula) (id : String) (inner : Json)
    (assertions : Nat) : Except String Json := do
  let S ← VE.NormDefaults.Wire.situationX L (← inner.getObjVal? "model")
  let F ← VE.NormDefaults.Wire.decodeFilling L.U S.M (inner.getObjValD "filling")
  let E := envAt (fill L.U) (size (fill L.U))
  let (Γ, φ) ← choiceFormulas E (if inner.getObjValD "premises" == .null then inner.setObjVal! "premises" (.arr #[])
    else inner)
  let res := VE.NormDefaults.modelCheckX L.U L.X S.M F (A ++ Γ) φ
  pure (modelAnswer id res.1 res.2
    ((A ++ Γ).map (fun a => (VE.Norms.subst (fill L.U).T (size (fill L.U)) a).eval (S.M.withFill F) [])) assertions)

def choiceInnerX (re : ReadingsEnvironment) (L : VE.NormDefaults.Wire.LayeredU) (A : List VE.Formula)
    (id kind : String) (inner : Json) (assertions : Nat) : Except String Json := do
  if kind == "norm-defaults-certificate" then return VE.Route.Wire.ok id (← choiceCertificateX re L A inner)
  if let some a ← VE.NormDefaults.Wire.layeredCase L id kind inner then return a
  if kind == "choice-model" then return ← choiceModelX L A id inner assertions
  throw s!"UnsupportedProfile: case kind {kind} is not available on the norm-defaults route"
end VE.Readings.Run
```

The definition changes of plan 4.7, each changing no statement: `abstention` (`re.chain != .norms` becomes
`re.chain == .rights`); `routeOf` (`if D.chain == .norms then .enumerated else .abstention` becomes
`if D.chain != .rights then .enumerated else .abstention`; `routeND` unchanged); `ndDocText re U := ndDocTextG re 0 U`;
`ndTextWith`'s body as above (`decisionCount`, 0 on the norms chain); `ndRest N := normsShaped N.D && fillRest N`;
`choiceLayered r c wfc := (choiceLayeredG r.b r.N c wfc).map (fun L => ⟨L.1, L.2.1⟩)` (it drops the new conjunct;
checked in the stub); `ndCertificate x inner := choiceCertificateX x.r.b.a.re L (choiceDoc x.r.N.D x.c).2 inner` and
`ndChoiceModel` by `choiceModelX`, `ndInner x L := choiceInnerX x.r.b.a.re L (choiceDoc x.r.N.D x.c).2` (certificate
first); `runChoiceND`'s `conflict_free` by `conflictFreeCheckX L.U L.X x.certs` (today's value at `X = []`,
`conflictFreeCheckX_nil`); the three readings kinds dispatch to the soft runners under `underSoftCompletion`.

The soft chain's `readings-choice` runner answers as `runChoiceND` does. For a `norm-defaults-certificate` inner case
it adds `conflict_free := conflictFreeX x.L (conflictPackages inner)` (`Layered.lean`'s `conflictFreeX` on the case's
conflict packages, read by `UnspecifiedWire.lean`'s `conflictPackages`) and `accepted := conflict_free && valid`.
That `conflict_free` is exactly the hypothesis `hv`, or `hcf`, of `readings_wire_sd_choice_conflict` and
`readings_wire_sd_choice_entails`.

`replayChoiceS` fills `hXw` from `choiceLayeredG`'s third conjunct. `readings_wire_sd_choice_entails` then follows
from the replay's fields alone, without unfolding `choiceLayeredG`: `acceptanceX` gets its `hX` from `hXw`
rewritten by `hU` and `hX`, and the conflict half comes from `readings_wire_sd_choice_conflict`. The stub checks this
derivation as an `example` over the two statements.

### 6.9 SC-5: verdicts under the soft completion

In `Readings/VerdictsWire.lean` (D13) and `Readings/SoftVerdicts.lean`:

```lean
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Norms (envAt size targets)
open VE.NormDefaults (UDoc fill)
universe u

-- VerdictsWire.lean
structure XEvidence (U : UDoc) (X : List VE.Formula) where
  wfc : VE.NormDefaults.WellFormedU U = true
  hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []
  certs : List (Option VE.Tableau.Certificate)
  witness : Option (PLift (¬ VE.NormDefaults.Wire.ConflictFreeX.{0} U X))
  cert : Option VE.Tableau.Certificate
  counter : Option (FilledModel U)
  unsat : Option VE.Tableau.Certificate
  model : Option (FilledModel U)

def xFree {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) : Bool :=
  VE.NormDefaults.Wire.conflictFreeCheckX U X e.certs
def xCertOk (U : UDoc) (X A Γ : List VE.Formula) (φ : VE.Formula) (k : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (VE.NormDefaults.Wire.premisesX U X (A ++ Γ)) φ k
def xModelOk (U : UDoc) (X A Γ : List VE.Formula) (φ : VE.Formula) (m : FilledModel U) (v : Bool) : Bool :=
  ((A ++ Γ) ++ [φ]).all (·.check (envAt (fill U) (size (fill U))) []) &&
    (VE.NormDefaults.modelCheckX U X m.M m.F (A ++ Γ) φ).1 &&
    (VE.NormDefaults.modelCheckX U X m.M m.F (A ++ Γ) φ).2 == v &&
    localFree U m.M m.F
def xConflictRow {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) : ChoiceResult :=
  if xFree e then .free else if e.witness.isSome then .conflict else .unknown
def xQueryRow {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) (A Γ : List VE.Formula) (φ : VE.Formula) :
    ChoiceResult :=
  if (e.cert.map (xCertOk U X A Γ φ)).getD false && xFree e then .proved
  else if (e.counter.map (xModelOk U X A Γ φ · false)).getD false then .refuted
  else .unknown
def xPremiseRow {U : UDoc} {X : List VE.Formula} (e : XEvidence U X) (A : List VE.Formula) : ChoiceResult :=
  if (e.unsat.map (xCertOk U X A [] .bottom)).getD false && xFree e then .inconsistent
  else if (e.model.map (xModelOk U X A [] .bottom · false)).getD false then .model
  else .unknown
-- Checked in the stub: `xCertOk (choiceU N c) [] (choiceDoc N.D c).2 Γ φ k = ndCertOk N c Γ φ k` and
-- `xModelOk (choiceU N c) [] (choiceDoc N.D c).2 Γ φ m v = ndModelOk N c Γ φ m v`.

theorem xConflictRow_holds {N : NDoc} {Xf : Choice → List VE.Formula} {c : Choice}
    (e : XEvidence (choiceU N c) (Xf c)) : HoldsG (xSem.{u} N Xf) [] .bottom c (xConflictRow e)
theorem xQueryRow_holds {N : NDoc} {Xf : Choice → List VE.Formula} {c : Choice}
    (e : XEvidence (choiceU N c) (Xf c)) (Γ : List VE.Formula) (φ : VE.Formula) :
    HoldsG (xSem.{u} N Xf) Γ φ c (xQueryRow e (choiceDoc N.D c).2 Γ φ)
theorem xPremiseRow_holds {N : NDoc} {Xf : Choice → List VE.Formula} {c : Choice}
    (e : XEvidence (choiceU N c) (Xf c)) : HoldsG (xSem.{u} N Xf) [] .bottom c (xPremiseRow e (choiceDoc N.D c).2)

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
theorem x_premiseRowsHold (x : XVerdicts) :
    CoversG (xSem.{u} x.N x.Xf) x.A x.premiseRows ∧
      ∀ y ∈ x.premiseRows, HoldsG (xSem.{u} x.N x.Xf) [] .bottom y.1 y.2

-- SoftVerdicts.lean
def sdSem (N : NDoc) : ChoiceSem := xSem.{u} N (choiceX N)
theorem sdSem_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (c : Choice) (r : ChoiceResult) : HoldsG (sdSem.{u} N) Γ φ c r ↔ HoldsG (ndSem.{u} N) Γ φ c r

structure SDVerdicts where
  r : AdmittedSD
  x : XVerdicts
  hN : x.N = r.N
  hX : x.Xf = choiceX r.N
/-- 4.4. -/
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
theorem readings_wire_sd_verdicts_conflict_free (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldConflict y.x.conflictRows = .free) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c)
theorem readings_wire_sd_verdicts_conflict (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldConflict y.x.conflictRows = .conflict) :
    ∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU y.r.N c) (choiceX y.r.N c)
theorem readings_wire_sd_verdicts_model (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldPremises y.x.premiseRows = .model) :
    ∃ c, Compatible y.r.N.D c ∧ (∀ z ∈ y.x.A, z ∈ c) ∧
      ConsistentX (choiceU y.r.N c) (choiceX y.r.N c) (choiceDoc y.r.N.D c).2
theorem readings_wire_sd_verdicts_inconsistent (j : Lean.Json) (y : SDVerdicts) (h : replayVerdictsSD j = .ok y)
    (hv : foldPremises y.x.premiseRows = .inconsistent) :
    ∀ c, Compatible y.r.N.D c → (∀ z ∈ y.x.A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU y.r.N c) (choiceX y.r.N c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU y.r.N c) (choiceX y.r.N c) (choiceDoc y.r.N.D c).2 .bottom
end VE.Readings.Wire
```

Consolidation (D7): `NDEvidence N c := XEvidence (choiceU N c) []`; `ndFree`, `ndCertOk`, `ndModelOk` and the three
`nd*Row` functions become the `x*` functions at `X = []` with `A := (choiceDoc N.D c).2`; `ndConflictRow_holds`,
`ndQueryRow_holds`, `ndPremiseRow_holds`, `nd_rowsHold` and `nd_premiseRowsHold` keep their statements and are
re-proved through `x*Row_holds`, `xSem_nil` and `holds_iff_holdsG` (an `NDVerdicts x` is the `XVerdicts`
`⟨x.r.N, fun _ => [], x.A, x.Γ, x.φ, x.ready, x.hle, x.evs, x.hevs, x.notes⟩`). `ndEvidenceOf` keeps the layered
witness itself (no `notFreeU_of_notFreeX`) and supplies `hX` vacuously. On the soft chain each choice's `hX` is its
`choiceLayeredG` source's third conjunct, rewritten by `L.U = choiceU N c` and `L.X = choiceX N c` (checked in the
stub as an `example`). The answer's `decided_units` is SC-A's computation on `SDVerdicts`' rows.

### 6.10 SC-6: the layered branch's soft kinds

In `NormDefaults/LayeredAdmission.lean`, `NormDefaults/Admission.lean` and `NormDefaults/Run.lean`:

```lean
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms
universe u

theorem decodeSoftU_X_wellFormed (environment norms : Json) (L : LayeredU) (h : decodeSoftU environment norms = .ok L) :
    ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []

structure LayeredEntailment where
  L : LayeredU
  hX : ∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate
  valid : Bool
  hvalid : valid = VE.Tableau.checkCertificate (envAt (fill L.U) (size (fill L.U)))
    (premisesX L.U L.X premises) conclusion cert
/-- 4.5: `decodeSoftU`, the formulas over `envAt (fill L.U) (size (fill L.U))`, `bindCertX environment L.U L.X []`. -/
def replayLayeredEntailment (j : Json) : Except String LayeredEntailment

theorem layered_wire_acceptance (j : Json) (r : LayeredEntailment) (h : replayLayeredEntailment j = .ok r)
    (hv : r.valid = true) : VE.NormDefaults.EntailsX.{u} r.L.U r.L.X r.premises r.conclusion
end VE.NormDefaults.Wire

namespace VE.NormDefaults.Admission
open Lean
open VE.Norms
open VE.Route.Admission
universe u

-- Admission.lean: the leaves over the `UDoc` they read; `LayerLeaf s w := LayerLeafU s.U w`,
-- `ProfileLeaf s w := ProfileLeafU s.U w` and `FillLeaf s w := FillLeafU s.U w` (each `Iff.rfl` in the stub).
def LayerLeafU (U : UDoc) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    ((syms (fill U).T).filterMap (fun | .reg r => some r | .defn _ => none)).any
      (fun r => decide (w.claim.label = "layer:norms:" ++ r.name ∧
        w.claim.formula = elabPremise (fill U).T r))) = true
def ProfileLeafU (U : UDoc) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone && w.claim.label == "background:profile" &&
    (pairPremises (fill U).T).any (fun a => decide (w.claim.formula = a))) = true
def FillLeafU (U : UDoc) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (fillLabelled U).any (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true

-- LayeredAdmission.lean
def SoftLeafX (L : Wire.LayeredU) (w : WireNode) : Prop :=
  (w.deduction.isNone && w.unit.isNone &&
    (L.labelled.take (L.labelled.length - L.rightsCount)).any
      (fun (l, a) => decide (w.claim.label = l ∧ w.claim.formula = a))) = true
-- (each of the four leaf predicates gets a `Decidable` instance by `unfold; infer_instance`, as today's do)
def NodeAdmittedX (L : Wire.LayeredU) (D : VE.Route.Admission.Doc) (w : WireNode) : Prop :=
  VE.Route.Admission.NodeAdmitted D w ∨ LayerLeafU L.U w ∨ ProfileLeafU L.U w ∨ SoftLeafX L w ∨ FillLeafU L.U w

structure AdmittedX where
  L : Wire.LayeredU
  doc : VE.Route.Admission.Doc
  filled : Json
  graphJson : Json
  nodes : Array Json
  decoded : List (WireNode × Json)
  wires : List WireNode
  graph : VE.Graph.ClaimGraph VE.Tableau.Certificate
  report : VE.Graph.Report
  kinds : List Json
/-- 4.5. -/
def admitDocumentX (environment document : Json) : Except String AdmittedX

def otherAssumptionsX (res : AdmittedX) : List VE.Graph.Claim :=
  res.report.assumptions.filter (fun c =>
    !VE.Norms.Admission.backgroundLeaf c && !decide (∃ w ∈ res.wires, w.claim = c ∧
      (decide (LayerLeafU res.L.U w) || decide (FillLeafU res.L.U w) || decide (SoftLeafX res.L w)) = true))
def ReportAdmittedX (res : AdmittedX) : Prop :=
  VE.Graph.SoundReport.{0} (fill res.L.U).E res.graph res.report ∧
  (∀ w ∈ res.wires, NodeAdmittedX res.L res.doc w) ∧
  (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
    w.claim = leaf ∧ w.deduction = none ∧ NodeAdmittedX res.L res.doc w) ∧
  CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report
def filledJsonX (environment : Json) (L : Wire.LayeredU) : Except String Json := do
  Wire.withUnsaid L.U (← VE.SoftNorms.Wire.primeJson L.D (← Wire.placeholderJson environment))
def filledProfilesX (environment : Json) : List String := (Wire.profilesOf environment).filter (· != Wire.profile)
/-- Today's `SourceDecoded` (`Admission.lean:168–185`) over `res.L`, conjunct by conjunct. The soft source `src` is
    the one `decodeSoftU` builds `L` from, over the placeholder completions. -/
def SourceDecodedX (environment document : Json) (res : AdmittedX) : Prop :=
  (∃ clean norms quoted env' src, VE.Norms.Admission.splitDocument document = .ok (clean, norms, quoted) ∧
    Wire.decodeSoftU environment norms = .ok res.L ∧
    Wire.placeholderJson environment = .ok env' ∧ VE.SoftNorms.Wire.decodeSoftSource env' norms = .ok src ∧
    res.L.D = src.D ∧
    (∀ q ∈ quoted, VE.SoftNorms.Admission.checkQuoted src q = .ok ()) ∧
    (∃ D₀, VE.Route.Admission.decodeDoc src.se.ne.rv (src.se.profiles.contains "data@0") clean (fill res.L.U).E =
        .ok D₀ ∧ res.doc = { D₀ with literals := src.se.ne.rv.literals }) ∧
    (fill res.L.U).lits = src.se.ne.rv.literals ∧
    (∀ x ∈ res.decoded, ∃ j ∈ res.nodes.toList,
      VE.Route.Admission.decodeNode (fill res.L.U).E (src.se.profiles.contains "data@0") j = .ok x ∧
      j.getObjVal? "ast" = .ok x.2 ∧
      VE.Route.Wire.decodeClosed (fill res.L.U).E x.2
        ((src.se.profiles.contains "data@0") && !x.1.claim.label.startsWith "background:") =
          .ok x.1.claim.formula)) ∧
  Wire.layeredRoute environment = some "soft-norms@0" ∧ WellFormed (fill res.L.U) = true ∧
  document.getObjVal? "graph" = .ok res.graphJson ∧
  res.graphJson.getObjVal? "nodes" = .ok (Json.arr res.nodes) ∧
  VE.Bridge.stringField res.graphJson "root" = .ok res.graph.root ∧
  res.wires = res.decoded.map Prod.fst ∧ res.graph.nodes = res.wires.map WireNode.toNode
def CertificatesBoundX (environment : Json) (res : AdmittedX) : Prop :=
  filledJsonX environment res.L = .ok res.filled ∧
  ∀ x ∈ res.decoded, VE.Norms.Admission.CertificateBound (filledProfilesX environment) res.filled res.decoded x

theorem admitDocumentX_spec (environment document : Json) (res : AdmittedX)
    (h : admitDocumentX environment document = .ok res) :
    SourceDecodedX environment document res ∧ CertificatesBoundX environment res ∧
    VE.Graph.SoundReport.{u} (fill res.L.U).E res.graph res.report ∧
    (∀ w ∈ res.wires, NodeAdmittedX res.L res.doc w) ∧
    (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
      w.claim = leaf ∧ w.deduction = none ∧ NodeAdmittedX res.L res.doc w) ∧
    CitationsClosed res.doc res.report ∧ ChoicesCompatible res.report
theorem wire_report_consequenceX (environment document : Json) (res : AdmittedX)
    (h : admitDocumentX environment document = .ok res) (S : VE.Structure.{u}) (hS : S.Admissible (fill res.L.U).E)
    (hflags : Sat S (VE.Data.Background.generate res.doc.flags))
    (hregen : Sat S (background (fill res.L.U) ++ res.L.X ++ fillPremises res.L.U ++ elaborate (fill res.L.U).T))
    (hother : Sat S ((otherAssumptionsX res).map (·.formula))) :
    res.report.root.formula.denote S []

def conditionalOnX (res : AdmittedX) : List String :=
  (VE.SoftNorms.Wire.openCoherence res.L.D).filter (fun l => res.report.assumptions.any (fun c => c.label == l))
def encodeAdmittedX (id reportId : String) (res : AdmittedX) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", VE.Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson (conditionalOnX res))]
def AdmissionAnswerX (id : String) (environment document answer : Json) : Prop :=
  ∃ res : AdmittedX, ∃ reportId : String,
    admitDocumentX environment document = .ok res ∧
    answer = encodeAdmittedX id reportId res ∧
    SourceDecodedX environment document res ∧
    CertificatesBoundX environment res ∧
    ReportAdmittedX res ∧
    (∃ canonical envId, Wire.canonicalEnvironmentJsonU environment = .ok canonical ∧
      VE.Route.Wire.environmentId (Wire.profilesOf environment) canonical = .ok envId ∧
      VE.CertificateWire.digest (VE.Norms.Run.reportDomain (Wire.profilesOf environment))
        (VE.Norms.Run.reportPayload envId document res.report) = .ok reportId) ∧
    (∀ S : VE.Structure.{0}, S.Admissible (fill res.L.U).E →
      Sat S (VE.Data.Background.generate res.doc.flags) →
      Sat S (background (fill res.L.U) ++ res.L.X ++ fillPremises res.L.U ++ elaborate (fill res.L.U).T) →
      Sat S ((otherAssumptionsX res).map (·.formula)) →
      res.report.root.formula.denote S [])

/-- The soft branch's two kinds `layeredCase` lacks: `admission` and `norm-defaults-certificate`; `none` otherwise. -/
def softCase (id kind : String) (j : Json) : Except String (Option Json)
end VE.NormDefaults.Admission

namespace VE.NormDefaults.Run
open Lean

-- Run.lean: `runCase` after SC-6 (elaborated in the stub under the name `runCaseX`).
def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  let env := j.getObjValD "environment"
  if Wire.hasProfile env && Wire.layeredRoute env == some "soft-norms@0" then
    if let some a ← Admission.softCase id kind j then return a
  if kind == "admission" && Wire.hasProfile env then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  runOtherCase id kind j

/-- Changed statement (signed at SC-0): today's, with the one hypothesis `hs` added. -/
theorem normDefaults_wire_admission (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission")
    (hp : Wire.hasProfile (j.getObjValD "environment") = true)
    (hs : Wire.layeredRoute (j.getObjValD "environment") ≠ some "soft-norms@0") :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      AdmissionAnswerU id (j.getObjValD "environment") (j.getObjValD "document") answer
theorem normDefaults_wire_admissionX (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission")
    (hp : Wire.hasProfile (j.getObjValD "environment") = true)
    (hs : Wire.layeredRoute (j.getObjValD "environment") = some "soft-norms@0") :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      Admission.AdmissionAnswerX id (j.getObjValD "environment") (j.getObjValD "document") answer
end VE.NormDefaults.Run
```

`SourceDecodedX` against today's `SourceDecoded`, conjunct by conjunct (debate A1):

| Today (`res : Admitted`, `res.s : SourceU`) | Soft branch (`res : AdmittedX`) |
|---|---|
| `splitDocument … = .ok (clean, norms, quoted)`, `decodeSourceU environment norms = .ok res.s` | the same split; `decodeSoftU environment norms = .ok res.L`, and `src` decoded over `placeholderJson environment` with `res.L.D = src.D` |
| `∀ q ∈ quoted, checkQuoted res.s q = .ok ()` | `∀ q ∈ quoted, SoftNorms.Admission.checkQuoted src q = .ok ()` (the soft route's check) |
| `decodeFilledDoc res.s clean = .ok D₀`, `res.doc = { D₀ with literals := … }` | `decodeDoc src.se.ne.rv data clean (fill res.L.U).E = .ok D₀`, the same `res.doc` equation; `decodeFilledDoc` is this decoder over `fill s.U` (`rfl`, checked in the stub) |
| `res.s.profiled = true` | `layeredRoute environment = some "soft-norms@0"` |
| `WellFormed (fill res.s.U) = true`, `(fill res.s.U).lits = res.s.src.ne.rv.literals` | `WellFormed (fill res.L.U) = true`, `(fill res.L.U).lits = src.se.ne.rv.literals` |
| the graph JSON, its `nodes` array and its `root` | the same three equations, over the new fields `res.graphJson` and `res.nodes` |
| `res.wires`, `res.graph.nodes` | the same |
| each decoded node: its source JSON in `res.nodes`, `decodeNode` and `decodeClosed` over `fill res.s.U` | the same over `fill res.L.U`, with `src`'s `data@0` flag |

`admitDocumentX_spec` and `AdmissionAnswerX` keep `SourceDecodedX` as written above. So `CertificatesBoundX`
binds certificates to nodes that are the submitted graph's nodes, decoded from the submitted ASTs, under the submitted
root and beside the submitted units. The three substitution fixtures of 8.3's SC-6 row test this.

`layeredCase`'s docstring, the one change to `Layered.lean`, becomes: "The `norm-defaults-*` kinds of a layered document
that this branch answers itself, `none` for any other kind; the dispatch of a choice's inner case under the readings
completion (`Readings.Run.choiceInnerX`) uses it too, so both answer each kind alike. The soft branch's `admission` and
`norm-defaults-certificate` are dispatched before it, by `NormDefaults.Admission.softCase` (`Run.runCase`)."

### 6.11 SC-10 (sketch, off the path; re-reviewed before its build)

```lean
namespace VE.Readings
universe u
def supX (N : NDoc) : List VE.Formula := softX N (sup N.D).1
theorem sd_superpose_conflict_free (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (A : Choice)
    (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    (∀ B : VE.Structure.{u}, VE.NormDefaults.Wire.BaseAdmissibleX (supU N) (supX N ++ slotUnder N.D A) B →
        VE.Norms.ConflictFree (VE.NormDefaults.fill (supU N)) B) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU N c) (choiceX N c)
end VE.Readings
```

It elaborates; it is not reviewed for PASS here (plan 4.11). Section 13 (2026-10-31) is SC-10's statement spec and
replaces this sketch; 13.4 lists the differences.

## 7. What is not claimed

- No completeness of separation: an unseparated pair is equal meaning or a search miss.
- No theorem relates `separatesS` on a norms-shaped document to RD-1's `separates (fillDoc N)` with `fillHolds` (Q3).
- No minimality of a pair's or a result's gaps. If SC-A does not prove `coneEval_sound` and `coneEval_definite`, the
  selection itself is not claimed sound either, and the answer says nothing more than today's verdict lines do.
- Not claimed: the gap selection is not proved sound. Until `coneEval_sound` and `coneEval_definite` are proved,
  the F-ND1, F-ND2 and CE4 unlisted-gap flip tests are bounded evidence only; they are not a general theorem.
- No superposition under the soft completion before SC-10, nothing about the rights chain under the completion or
  about companions on the soft chain.
- The four constitution sets do not show "defeasible duties with contextual exceptions": with `X = []` they mean what
  today's workaround means (plan 0, E2). The removal of the deny completion's "not required" is `norm-defaults@0`'s.
- No speed, coverage figure or audit outcome, and nothing about what Python's generators find within budget.

## 8. Acceptance fixtures

### 8.1 Lean fixtures, *computed* in the stub

The documents are S1's environment K (`VE.Readings.Examples`: sorts `agent`, `user`; `asks`; `avoid_required`,
`help_required`; `S` the strict `no-deception`, `Df` its default twin, set `rs1 = {strict, default}`; `m0` one agent
`a`, one user `u`), read as `NDoc`s with the unspecified predicates named. `mFill fl` is `m0` with
`unsaid__avoid_required = fl`; `σDef fl v` has the default reading's table `excepted no-deception = {(a, u)}`, outcome
probe `avoid_required (a, u)` with value `v`; `σNone fl v` has no table.

| # | Expression | Value |
|---|---|---|
| F-SD1 facts | `(WellFormedSD NSD1, softShaped NSD1.D, (oneX NSD1 "rs1" 0).length, (oneX NSD1 "rs1" 1).length, decisionOnly NSD1.D "rs1" 0 1, choices NSD1.D)`, `NSD1 := ⟨K1, ["avoid_required"]⟩` | `(true, true, 0, 0, some (excepted "no-deception" none), [[("rs1", 0)], [("rs1", 1)]])` |
| F-SD1 separation | `separatesS NSD1 "rs1" 1 0 (σDef [] false)`, `… (σDef [["a","u"]] false)`, `separatesS NSD1 "rs1" 0 1 (σNone [] true)`, `… (σNone [["a","u"]] true)` | `true, false, false, false` |
| F-SD1 sides | the default side's validity with the table, its value with filling `[]` and with `[["a","u"]]`, the strict side's value, the witness's `fillHoldsS` | `true, some false, some true, some true, true` |
| F-SD1 quiet | for both fillings, every probe of `probesOf K1` and both values, neither direction separates with no table | `true` |
| F-SD3 | `NSD3 := ⟨K5, ["avoid_required","help_required"]⟩`: `WellFormedSD`, `cellsOn` of readings 0 and 1, `owned` of `excepted be-kind` by each, `separatesS NSD3 "rs1" 1 0` with fixed `excepted be-kind = {(a,u)}` and the default's table | `true, 0, 1, false, false, true` |
| F-SD4 | `coherent` (frame `assistant`, `c`, `x_required`, `x_permitted`, `y_permitted` unspecified; fixed default `need-not-x`; set `{strict must-x, default must-x}` with `must-x` guarded by `y_permitted` and sufficient condition `c`): `WellFormedDoc`, `WellFormedSD`, the labels of `softXL` for each reading | `true, true, [], ["soft:exception:must-x:sufficient:0", "soft:coherence:must-x,need-not-x"]` |
| F-SD4 coherence | whether each premise of the default reading's `softXL` mentions `unsaid__y_permitted`; the same for soft's own `cohPremises` | `[false, true]`; `[false]` |
| F-SD5 | `Wire.chainText .soft (one (fillDoc NSD1) "rs1" 1)`, `WellFormedDoc (fillDoc NSD1)` | `some "SoftOverHard: rule no-deception over unsaid--avoid-required"`, `false` |
| F-SD7 | `decisionCount` of the strict and default readings; `checkAuthorN` over an environment of 252 declared predicates with 4 unspecified, generated count = each reading's | `0, 1, none, some "ResourceLimit: vocabulary size"` (252 + 0 + 4 = 256 passes; 252 + 1 + 4 = 257 fails) |
| F-SD10 | K1 with three more unspecified permissions and no rule on them, over an `Entity` model: `WellFormedSD`, `separatesS … 1 0` (default table, value false), `pairGapsOn (oneU NSD10 "rs1" 1) P10 (mE []) T10 qE`, the number of unsaid atoms | `true, true, [("avoid_required", ["a","u"], false)], 4` |
| F-SD10 strict | `pairGapsOn` on the strict reading's side | `[]` (its rule decides) |
| F-ND1 gaps | the norms chain's F-ND1 (`separates (fillDoc ND1) "rs_1" 1 0 …` with filling `unsaid__help_permitted = {(a,u)}`, value false): `separates`, gaps of witness 1, gaps of witness 0's side, unsaid atoms | `true, [("help_required", ["a","u"], false)], [], 2` |
| K2 sides | `NSD2 := ⟨K2, ["avoid_required"]⟩` (a necessary condition `⊥`): `sideValidOn` of the default side with no table and with `excepted = {(a,u)}`; `(oneX NSD2 "rs1" 1).length` | `true, false, 1` |
| `fillHoldsS` | `NSDp`: F-ND1's frame (`help_required` with its dual `help_permitted`, both unspecified) on the soft chain, set `{strict must-help, default must-help}`: `WellFormedSD`; the number of `Fill_T` premises; `fillHoldsS … 0` with `unsaid__help_permitted = {(a,u)}` and with it empty; `separatesS … 0 1` (value true) on each base | `true, 1, true, false, false, false` |
| `fillHoldsS` isolated (F2) | `NSDq`: F-ND1's frame plus one regulated act `greet_required(agent, user)`, not unspecified, on the soft chain. Its set is `{strict must-help, default must-greet}`, so the other reading regulates a different act. Witness 0, outcome `help_required (a, u)`, value true. Evaluated: `WellFormedSD`; the number of the witness's `Fill_T` premises; `pairEval`'s first component (`separatesS`'s pair check) with `unsaid__help_permitted = {(a,u)}` and with it empty; `fillHoldsS … 0` on each base; `separatesS … 0 1` on each base | `true, 1, true, true, true, false, true, false` |
| F-SD2 route | `routeOf false K1` (K1 without the profile); `routeOf true K1` (with the profile, today); `K1.chain != .rights` (so the new `routeOf` body gives `.enumerated`); `completionFinding K1` | `superposed, abstention, true, ("rs1", "the unspecified completion")` |
| F-SD2 fields | `N18 := ⟨K1, []⟩` (K18: nothing unspecified). Evaluated: `WellFormedSD`; `oneX` length of readings 0 and 1; the number of `Fill_T` premises of each reading's document; the default reading's unsaid atoms; `pairGapsOn` on the default witness's side with `excepted = {(a,u)}` | `true, 0, 0, 0, 0, 0, []` |
| F-SD2 = K1 | First: for each reading and each table in `{[], excepted = {(a,u)}}`, `sideValidOn` on `sideOfS N18`, and `sideValueOn` for every probe of `probesOf K1 m0`, equal S1's on `sideOf K1`. Second: for both orders, both tables, every probe and both values, `separatesS N18` equals S1's `separates K1`. Third: S1's `separates K1 "rs1" 1 0` with the default's table, outcome `avoid_required (a,u)`, value false | `true, true, true` |
| C1′ | u0125.s04.p2's shape (permission `denial_permitted(claude_instance)` unspecified; strict and default `no-denying-being-claude`, sign −): `WellFormedSD`, `oneX` length, `decisionOnly`, `separatesS … 1 0` with `excepted = {c}` and filling `{c}` (value true), the same with filling `[]`, the strict side's value | `true, 0, some (excepted "no-denying-being-claude" none), true, false, some false` |
| C2′ | u0036.s05's shape (`clarification_required(claude_instance, situation)` unspecified, guard `genuine_ambiguity`): `WellFormedSD`, `oneX` length, `separatesS … 1 0` with ambiguity `{s}` and `excepted = {(c,s)}` (value false), the same without ambiguity, the strict side's value | `true, 0, true, false, some true` |
| C9′ | u0073.s05's shape (`compliance_required(claude_instance, instruction)`, default `comply` with sufficient conditions `unsafe`, `unethical`, `against_guidelines`): `WellFormedSD`; the default reading's `softXL` labels; `decisionOnly`; `sideValidOn` with `unsafe = {i}` and no table / full table; the default and strict values there; `separatesS` there (value false); `sideValidOn` and `separatesS` with nothing unsafe and no table | `true`; `["soft:exception:comply:sufficient:0", "…:1", "…:2"]`; `none`; `false, true`; `some false, some true`; `true`; `true, false` |
| Decided units | `partDecided ND1.D` on rows `[free/model, free/model]` and `[free/model, unknown/model]`; `partDecided K1` on `[free/model, conflict/inconsistent]` and `[free/model, free/unknown]` | `["u1"], [], ["u1"], []` |
| Cone | `coneEval` of the default reading's outcome formula on F-SD10 (`U10`, `M10`), and its value under fillings: empty; empty with `unsaid__p1_permitted = {(a,u)}`; `unsaid__avoid_required = {(a,u)}` | atoms `[("unsaid__avoid_required", [("agent","a"), ("user","u")])]`; `false, false, true` |
| Cone definite | `coneEval` of the strict reading's outcome formula | `(some true, [])` |

### 8.2 Every "exactly when" and iff claim, with a fixture for each direction

| Claim | One direction | The other |
|---|---|---|
| Under the soft completion exactly when `norm-defaults@0`, the soft chain and a content-bearing set (1.1) | F-SD2: K18 (K1 with the profile) is admitted on the enumerated row, with K1's validate and separate rows (F-SD2 = K1, *computed*) and the per-kind answers of 8.3 (*derived*) | F-SD6 (rights chain): the abstention; F-SD0 (K1 without the profile): S2a's route, `superposed` (F-SD2 route, *computed*); a soft document under the profile without content: the layered branch's W2 route (*derived*) |
| The readings differ only where the exception applies (`decision_only_soundS`, D5). This is not "exactly where": only one direction is proved | the theorem's direction: with the default twin's table empty, no probe separates them, F-SD1 quiet `true` (*computed*) | non-vacuity examples, not a converse. With the table nonempty and the filling no, they separate (F-SD1 separation, first value `true`). With the table nonempty and the filling yes, they do not (the matching filling, F-SD1 separation, second value `false`). Both *computed* |
| `softPremisesIn_fill` (an equality) | the filled side's coherence premise reads the unsaid atom (F-SD4 coherence `true`, *computed*) | soft's own premise does not (`false`, *computed*); the equality is *proved in the stub* |
| `sideValidOn_sideOfS_iff` | valid: K2's default side with no table, `true` (*computed*) | invalid: with `excepted = {(a,u)}` against the necessary condition `⊥`, `false` (*computed*); *proved in the stub* |
| `observeOn_sideOfS_sound` | value `some false`: F-SD1's default side with filling `[]` (*computed*) | value `some true` with filling `{(a,u)}` (*computed*) |
| `separatesS_sound` (a `true` check proves `AchievesS` of the witness and not of the other) | F-SD1 `true`, C1′ `true`, C2′ `true`, C9′ `true` (*computed*) | the checks that do not hold: F-SD1 with the filling, the strict witness; C1′ without the filling; C2′ without the ambiguity (*computed*) |
| `fillHoldsS` (the witness's `Fill_T`) | holds: F-SD1's witness, and `NSDp`'s and `NSDq`'s strict witness with the permission filled, `true`; on `NSDq`, `separatesS` is then `true` (*computed*) | fails: the strict witness without the permission, `false`. On `NSDq`, `pairEval` is `true` on both bases, so `separatesS` turns from `true` to `false` by `fillHoldsS` alone (*computed*). On `NSDp` both `separatesS` values were already `false`, since the default twin with its table empty matches the strict witness |
| X is empty on strict documents (`softX_strict`; not an iff) | strict readings: F-SD4's strict reading `[]` (*computed*) | the converse fails: F-SD1's default reading also has `X = []` (*computed*); F-SD4's and C9′'s default readings have `X ≠ []` |
| `conflictFreeCheckX_nil`, `modelCheckX_nil`, `premisesX_nil` (equalities) and the `_nil` iffs, `holds_iff_holdsG`, `xSem_nil` | *proved in the stub* (both directions at once) | the norms chain's A/B byte-identical (F-SD0′) |
| One gap sentence per gap in the cone, none outside it (D9); the cone is read off the shown value's formula (`probeFormulaOn_eval`, *proved in the stub*) | in: F-SD10's one entry for `avoid_required (a,u)` (*computed*) | out: the three other unspecified predicates' atoms at `(a,u)` are not listed (4 atoms, 1 gap, *computed*); a definite value lists none (F-SD10 strict, *computed*) |
| `coneEval_sound` (agreeing on the listed atoms gives the same value) | fillings that differ only off the cone give the same value (`false, false`, *computed*) | a filling that differs on the listed atom changes it (`true`, *computed*): the listed atom is read |
| A unit is decided exactly when its rows are (1.12) | `["u1"]` with every row decided, both chains (*computed*) | `[]` with one conflict row or one premise row `unknown` (*computed*) |
| `normDefaults_wire_admission` (route ≠ soft) and `normDefaults_wire_admissionX` (route = soft) | a profiled norms-route admission answers byte-identically through `runAdmission` (F-SD0″, *derived*) | a soft admission is answered by `softCase` (SC-6's `coherent` claim graph, *derived*) |
| The vocabulary limit counts each document's decision predicates | the strict reading at 256 passes (*computed*) | the default reading at 257 fails (*computed*) |
| SC-10's `sd_superpose_conflict_free` and its transfers | 13.5 | 13.5 |

### 8.3 Wire fixtures (through the service; *derived*)

| # | Case | Expected | Batch |
|---|---|---|---|
| F-SD1 | K1 with `norm-defaults@0`, `avoid_required` unspecified: validate, separate, elaborate, choice | admitted; choices `[(rs1,0)]`, `[(rs1,1)]`; `soft_premises` empty on both readings; the pair separated with 8.1's σ, `gaps` one entry; elaborate: enumerated, `ReadingsNotSuperposable: rs1`, cause `the unspecified completion` | SC-4 |
| F-SD1.status | `norm-defaults-status` on `(rs1,1)`, base with `excepted = {(a,u)}`, fillings yes `{(a,u)}` and no `{}` | UNDECIDED, because the two admissible fillings give opposite values. This is the one place the spec claims UNDECIDED for a force twin (1.6); `excepted_lifts`' `.unsaid` alone does not give it. On `(rs1,0)`: SETTLED yes by `table3` | SC-4 |
| F-SD1.verdicts | conflict; query `∀ agent ∀ user. avoid_required`; `--under rs1:0`, `--under rs1:1` | CONFLICT-FREE under both; SOME (choice 0 `proved`, choice 1 `refuted` by `excepted = {(a,u)}` and the filling no); ALL; NONE. `decided_units`: `["u1"]` (the set's unit) without `--under` when every row is decided (8.1's decided units); `[]` under `--under rs1:0` and under `--under rs1:1` (1.12: with `assumed` the rows cover only some choices) | SC-5 |
| F-SD2 | K18 (K1 with `norm-defaults@0`, `avoid_required` deny, so `unspec = []` and `fill` is the identity), per request kind | Before: the abstention text for every kind. After, K18 takes the enumerated row (F-SD2 route), not K1's superposed one. Per kind:<br>• `readings-validate`, `readings-separate`: K1's rows and pair answers (F-SD2 = K1, *computed*), plus the completion's fields, each empty: `fill_premises: []` and `soft_premises: []` per reading, `gaps: []` per pair (F-SD2 fields, *computed*). `filled` names K1's lower environment without `norm-defaults@0`, with no `unsaid__` predicate, and K1's units.<br>• `readings-elaborate`: the enumerated row with `ReadingsNotSuperposable: rs1` and cause `the unspecified completion`, as F-SD1's; not K1's superposed row.<br>• `readings-choice`: the inner kinds of 4.3 on `choiceLayeredG` (route `soft-norms@0`, `labelled = []`); not K1's S2a inner kinds.<br>• `readings-verdicts`: RD-3's request and answer on the two choices: CONFLICT-FREE; the query `∀ agent ∀ user. avoid_required` SOME (choice 0 `proved`, choice 1 `refuted` by `excepted = {(a,u)}`, the act not required by the deny default); ALL under `rs1:0`; NONE under `rs1:1`; `decided_units` as F-SD1.verdicts. These are not K1's superposed answer | SC-4, SC-5 |
| F-SD4 | `coherent` beside its strict twin | `soft_premises` as 8.1; a CONFLICT-FREE answer under the default reading has `conditional_on: ["soft:coherence:must-x,need-not-x"]` with soft-norms 2.3's sentence as its E3 line | SC-4, SC-5 |
| F-SD6 | K19 (rights chain) with `norm-defaults@0` | the abstention text, unchanged | SC-4 |
| F-SD8 | a package bound to `(rs1,0)` replayed for `(rs1,1)`; an `unsaid__` table in a layered model's `relations`; a `soft__excepted__` table as a separation base relation (K2b) | refused or UNKNOWN, never CONFLICT-FREE, `proved` or `model`: diagnostics 10 and 9 | SC-4, SC-5 |
| F-SD9 | 7 sets each as `rs1` | enumerated, `choice_count: "over 64"`; a query UNKNOWN (budget), E28; `decided_units: []` (1.12: beyond 64 choices) | SC-4, SC-5 |
| F-SD11 | F-SD1 with a fixed assertion unit; a certificate for `(rs1,1)` whose binding lists the regenerated premises without that assertion, and one whose binding adds an assertion the choice does not take | `readings-choice`: the inner answer is diagnostic 11, `accepted: false`; `readings-verdicts`: the piece refused, the row `unknown` | SC-4, SC-5 |
| SC-6 kinds | the layered tests' u2 and u8 sources, `coherent`, a rights source | Certificates:<br>• A certificate of "where the exception does not apply, the act is not permitted" is `valid`.<br>• The same certificate replayed against the conclusion without that condition is refused with diagnostic 11 (A3): its `conclusion_meaning_id` no longer matches, and `bindingOk` runs before the check.<br>• A certificate whose ids bind that changed conclusion (the regenerated premises, the case's premises and the new conclusion's meaning id) but whose proof does not close answers `valid: false` (A3).<br>• With its binding missing one regenerated premise: diagnostic 11.<br>Claim graphs:<br>• A claim graph with a `soft:coherence` leaf is admitted on `coherent`, with `conditional_on` naming the leaf when it is open.<br>• A leaf with no regenerated premise is refused with W1's text.<br>Substitutions in the admitted `coherent` document (A1, each against `SourceDecodedX`):<br>• A substituted root (the graph's `root` names another of its nodes): the answer's `report` is rooted at that node, not the original root, and its `report_id` differs.<br>• A substituted node (one node's `ast` replaced, its certificate kept): `certificate is stale or bound to different inputs` (diagnostic 11, `checkBindings` on the submitted ASTs).<br>• A substituted unit (a unit's content replaced, the leaf citing it kept): W2's `AdmissionError: node <n> is not admitted under label <l>`.<br>Rights source: the certificate kind gives `runLayered`'s refusal, and `admission` gives today's answer | SC-6 |

### 8.4 The constitution (`CE4`, plan 5.2; *derived*, measured in SC-8 and SC-9)

C1 to C8 as plan 5.2, with C1′ and C2′ above as their *computed* miniatures, and:

- **C9** (required): u0073.s05 as one default rule with three sufficient exception conditions, replacing the
  `general_exception_to_complying` open term. Expected as C9′: three `soft:exception` premises; where a condition
  holds, the empty exception table is inadmissible and the default reading leaves compliance unsaid; no force-twin
  finding.
- **C10** (required): the comprehension check of 2.6 on C1 to C4, expected "no" four times.
- **R14.** C1 to C10 are results about the pilot's translation, not the constitution's text. A conflict the route
  reports about the constitution is a CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP) until SC-9's independent source check has run, and is never presented
  as a conflict in the source (`tests/test_rd9_r14_candidates.py`).

### 8.5 Conservativity

| # | Case | Expected |
|---|---|---|
| F-SD0 | S1's K1 to K22 without `norm-defaults@0`; S2a's M1 to M20 | byte-identical verdicts, identities and English |
| F-SD0′ | readings-defaults' F-ND0 to F-ND10, RD-3's, RD-4b's and RD-6b's fixtures | byte-identical verdicts and identities; the English identical except the gap selection (SC-A, pending item-specific DRI signature); F-ND1's line keeps its one gap (8.1) |
| F-SD0″ | `tests/test_norm_defaults_layered.py`; a profiled norms-route admission | unchanged answers; the two new kinds answer on the soft fixtures (u2, u3, u8, `coherent`) |

## 9. Limits

As readings-defaults 3.8, with one change: `checkAuthorN`'s vocabulary limit (declared predicates plus generated plus
unspecified, at most 256) counts each document's own decision predicates (`decisionCount`, F-SD7). Compatible choices
checked one at a time: 64. Cells of the other reading's owned tables: 12 (`maxCells`). Unsaid atoms in a status
enumeration: 12 (`MAX_UNSAID_ATOMS`). Rules plus unspecified predicates: 256 per document, choices included. AST nodes
with the `F_p` guards: 10,000 per document, soft's derived carve-outs included.

## 10. The measure

Readings-defaults 3.9's Lean-decided share: the span bytes of Lean's `decided_units`, summed by
`tools/lean_decided_share.py`, which decides nothing. SC-A makes it readable on the norms-chain translation, SC-5 on
the soft form; SC-9 reports it before and after, beside the unchanged claimed and audit-verified shares, with
readings-defaults E2's qualifiers. Each of the four sets regulates its own act with one rule, so a rise from them
measures checks routed into Lean, not new assurance. No figure is predicted.

## 11. Statement review checklist (Astra + Opus, SC-0)

The plan's 9, items 1 to 18, and:

1. The stub elaborates as recorded; the thirty-four statements *proved in the stub* are true as stated (re-proved in
   their batches).
2. Each `theorem` of 6 is true under its hypotheses (not only well typed). In particular: `acceptanceX` needs `hX`;
   `layered_wire_acceptance` reads `hX` from `LayeredEntailment`; `separatesS_sound` needs `WellFormedSD` and the
   base's validity over `filledAuthorEnv N`; `decision_only_soundS` holds with the twin alone on its act and no
   sufficient condition; `coneEval_sound` and `coneEval_definite` mirror `Formula.eval` case by case.
3. `admitSD` (4.1) reaches `WellFormedSD N` from its steps, in order, with no step 4.
4. `choiceLayeredG`'s soft case binds packages to `L.background` (with `X`), and its norms case is RD-2a's
   `choiceLayered` byte for byte.
5. `choiceInnerX` answers the certificate kind before `layeredCase`, and every norms-chain choice answer is
   byte-identical (`premisesX_nil`, `modelCheckX_nil`, `conflictFreeCheckX_nil`).
6. `XEvidence`'s rows at `X = []` are RD-3's (the two `example`s), and `nd_rowsHold`'s re-proof goes through
   `x_rowsHold`.
7. The soft dispatch: `runCase` calls `softCase` only when `layeredRoute … = some "soft-norms@0"`; the two runner
   theorems partition profiled admissions; `layeredCase` and the rest of `Layered.lean` are unchanged but for the
   docstring.
8. `decided_units` is `[]` with `assumed` and beyond 64, and `partDecided` on all rows otherwise.
9. The English: no new sentence; the filled-gap sentence's new use on separation lines; the comprehension check's
   questions (2.6).
10. The differences of 12 are each accepted or sent back.
11. **The bounded re-check of draft 2** (debate `rd-9-spec`, round 3). It covers only the following; nothing else is
    reopened.
    - The changed statements:
      - A1: `AdmittedX`'s two new fields and `SourceDecodedX` (6.10), kept in `admitDocumentX_spec` and
        `AdmissionAnswerX`;
      - F1: `choiceLayeredG`'s third conjunct and `ChoiceReplayS.hXw` (6.8);
      - F3: `probeFormulaOn_eval` with `anyF_eval` and `conj_eval` (6.2).
    - The new fixture values:
      - F2: `fillHoldsS` isolated (8.1, 8.2);
      - F5: F-SD2's route, fields and K1 comparison (8.1), F-SD2's per-kind answers, and `decided_units: []` in
        F-SD1.verdicts and F-SD9 (8.3);
      - A3 and A1: the SC-6 row's new `valid: false` case, the diagnostic 11 replay, and the three substitution
        cases (8.3).

    If it passes, the verdict is PASS and the build may start.

## 12. Differences from the plan's Lean blocks (found by elaboration or applied from the debate)

1. **No `VerdictsGen.lean`** (debate): the generic fold is in `Verdicts.lean` after `covers_mem`. The generic lemmas
   are `coversG_row` and `coversG_mem`, since RD-3's `covers_row` and `covers_mem` keep their names. `sdSem` and
   `sdSem_normsShaped` are in `SoftVerdicts.lean`.
2. **`filledAuthorEnv N`** (debate) replaces `authorEnv (fillDoc N)` in `AchievesS`, `AchievesQuietS`,
   `separatesS_sound`, `separatesS_separated` and `SeparateReplayS.valid`; `filledAuthorEnv_eq` is `rfl`.
3. **`softPremisesIn_fill` holds as an equality** (debate asked SC-0 to check): proved in the stub, through the new
   `excLabels_length` (`Exc_T`'s labels and premises have equal lengths, so the zip loses nothing) and
   `substIn_eq`/`layersOf_syms` (soft's `cohPremiseIn` on the filled tree's layers is `cohPremiseU`).
4. **`baseAdmissibleX_nil`** added: the lemma the four `_nil` iffs rest on.
5. **`conflictFreeCheckX`, `conflictFreeCheckX_nil`, `conflictFreeCheckX_sound`** added: `ndFree` and `runChoiceND`'s
   `conflict_free` read `conflictFreeCheckU`, whose premise list has no `X`; on the soft chain the packages are bound to
   `L.background`, which has it.
6. **`modelCheckX_nil`** added (the norms chain's model rows are value-identical).
7. **`bindCertX`** (debate E1), with its exact signature; `ndCertificate`, `ndBoundCert` and the layered certificate
   kind call it.
8. **`AdmittedSD` gains `side`**, the fact that each reading's document is read from the request's table, as
   `AdmittedNDFull` carries it.
9. **`choiceLayeredG (b) (N) (c) (wfc)`**: the plan's `re` is `b.a.re`, and its `wfs` (`WellFormedSoft`) is dropped
   from the signature, because the norms chain's caller has no such fact; the soft case checks what it needs inside,
   in `Except`. `labelled := softXL N (choiceDoc N.D c).1` on both chains (`[]` on the norms chain).
10. **Named helpers the plan described in prose**: `decisionCount`, `ndTextWith`'s new body (one function for both
    chains; the stub elaborated it as `sdTextWith`), `sdChoiceText` (soft-specific: the chain text on the unfilled
    choice), `fillRest` (with `ndRest_eq_fillRest` and `wellFormedSD_eq`), and the choice inner kinds
    `choiceCertificateX`, `choiceModelX`, `choiceInnerX`, of which `ndCertificate`, `ndChoiceModel` and `ndInner`
    become instances.
11. **The `x*` rows take the assertions `A`** (an `XEvidence U X` no longer knows its `N` and `c`): `xFree`, `xCertOk`,
    `xModelOk` named; `x_premiseRowsHold` added; the four wire theorems the plan left as "the same shape" written
    out. `readings_wire_sd_verdicts_inconsistent` states `(choiceDoc …).2 .bottom`, without `++ []`, as RD-3's does.
12. **`LayeredEntailment` gains `hX`**, which `layered_wire_acceptance` needs for `acceptanceX`; the replay fills it
    from `decodeSoftU_X_wellFormed`.
13. **SC-6's admission written out** (the plan left `admitDocumentX_spec` to SC-0): `LayerLeafU`, `ProfileLeafU`,
    `FillLeafU` over a `UDoc` (today's leaves are these at `s.U`), `SoftLeafX`, `NodeAdmittedX`, `otherAssumptionsX`,
    `ReportAdmittedX`, `filledJsonX`, `filledProfilesX`, `SourceDecodedX`, `CertificatesBoundX`, `admitDocumentX_spec`,
    `encodeAdmittedX` (with `conditional_on`, as the soft route's admission answer has it), `AdmissionAnswerX`. The
    plan's `AdmittedX` gains `decoded` and `kinds`.
14. **The runner's change** (debate): `runCase` with the soft dispatch first; `normDefaults_wire_admission` with
    `hs : layeredRoute … ≠ some "soft-norms@0"` (the value `layeredRoute` returns, `Layered.lean:131`, not `"soft"`);
    `normDefaults_wire_admissionX`.
15. **SC-A's statements** (debate E3, E4): `probeFormulaOn`, `pairGapsOn`, `coneEval_sound`, `coneEval_definite`; the
    decided-unit move (`VerdictsWire.lean` imports `Components.lean`).
16. **`decided_units` under the completion only, and `[]` with `assumed`**: the plan's 3.14 said "every
    enumerated-route answer". The lower route's rows are the lower route's answers, which 1.10's rule was not stated
    for, and with `assumed` the rows cover only some choices, so `setDecided` would read a subset. Plan draft 2's 3.10
    and 3.14 say "under the completion".
17. **F-SD7**: computed on K1's set `rs1`, so the default reading's text would be `ResourceLimit: vocabulary size under
    rs1@1:1` (the plan wrote `rs_1`).
18. **Universes**: as the plan's, checked: `separatesS_separated` concludes `SeparatedS.{0}`; `ndSem`, `xSem` and
    `sdSem` take `.{u}` for `free` and `entails` and `.{0}` for `notFree`, `counter` and `consistent`, as RD-3's
    `Holds` does.

Draft 2 (the statement review, `manage-agents/debates/rd-9-spec/`):

19. **Admission keeps its source correspondence** (A1, extends 13). `AdmittedX` gains `graphJson` and `nodes`, as
    today's `Admitted` has them. `SourceDecodedX` restates today's `SourceDecoded` over `res.L`, conjunct by conjunct:
    - the quoted checks, by the soft route's `checkQuoted` on the soft source over the placeholder completions;
    - `res.doc` from W2's `decodeDoc` of `clean` over `(fill res.L.U).E` with that source's literals and flags;
    - `WellFormed (fill res.L.U)` and the lits equality;
    - the graph JSON, the node array and the root;
    - the node, AST and `decodeClosed` correspondence.

    Draft 1's `SourceDecodedX` tied only `res.L` to the source, so `CertificatesBoundX` bound certificates to a
    `res.decoded` that nothing tied to the submitted graph. The table in 6.10 compares the two conjunct by conjunct.
    The stub checks, by `rfl`, that today's `decodeFilledDoc` and the soft route's `decodeSoftDoc` are `decodeDoc`
    over their own environments. The soft source is named by an existential, not a new field, so `AdmittedX` gains
    only the two fields the debate named.
20. **`X`'s well-formedness travels with the choice's source** (F1, extends 9). `choiceLayeredG`'s subtype gains
    `∀ a ∈ L.X, a.WellFormed (envAt (fill L.U) 0) []`, and `ChoiceReplayS` gains the field `hXw`, as difference 12
    gave `LayeredEntailment` its `hX`. Without it, `readings_wire_sd_choice_entails` could be proved only by unfolding
    `choiceLayeredG`'s body, and `XEvidence.hX` had no stated source (4.4, 6.9). On the norms chain the conjunct is
    vacuous (`X = []`), and `choiceLayered` drops it (6.8). The stub checks three things: `choiceLayered`'s
    derivation, `XEvidence.hX`'s source, and the derivation of `readings_wire_sd_choice_entails` from the fields.
21. **`probeFormulaOn_eval`** (F3, extends 15), with `anyF_eval` and `conj_eval`, all proved in the stub. Without it,
    D9's claim that the gaps are those of the shown value rested on a docstring.
22. **The soft runner's `conflict_free`** (F4) is `conflictFreeX x.L (conflictPackages inner)`, the hypothesis of
    the two `sd_choice` theorems (3, 4.3, 6.8). Draft 1 stated only `runChoiceND`'s.
23. **Prose and fixtures, no Lean** (A2 to A4, F2, F5, F6):
    - A2: "only where", with `excepted_lifts`' three hypotheses and UNDECIDED only through F-SD1.status (1.6, 8.2,
      8.3; plan 0, 3.5, 4.6, C1.4);
    - A3: diagnostic 11 for the changed-conclusion replay, with a separate `valid: false` case (8.3; plan SC-6);
    - A4: the plan's comprehension questions follow 2.6 (plan C10, SC-9);
    - F2: `NSDq` isolates `fillHoldsS` (8.1, 8.2);
    - F5: `decided_units: []` pinned, and F-SD2 per request kind (8.1, 8.3; plan 5.1);
    - F6: the gap sentence's place in E14 (2.2).

    The debate's wording nit on section 0 ("one binder binds every certificate") needed no edit: 1.8 is precise.

Build (SC-4), pending the bounded re-check of 11 item 11:

24. **`choiceLayeredG` gains `(hN : N.D = b.D)`** after `wfc`. The soft case types its situation vocabulary by soft's
    `primeModel_valid`, which needs the choice's soft document's `E` to be the request's environment
    (`re.se.ne.rv.environment`); `Environment` holds functions, so a run-time check under the signature `(b) (N)` of
    6.8 cannot establish it, and the norms case needs the same fact for `baseModel_valid` (RD-2a's `choiceU_E`). Every
    caller has it: `AdmittedSD.hN` (`replayChoiceAtS`) and `AdmittedND.hN` (`choiceLayered`). No approved theorem
    states `choiceLayeredG`; `ChoiceReplayS` and the two `sd_choice` theorems are unchanged.
    `tools/check_rd9_sc1_statements.py` lists it as pending with this reason.
25. **`ndTextWith` builds the free document once** (`let freeDoc := free N.D`, then `decisionCount freeDoc.1` and
    `asU N freeDoc.1`), where 6.8's body writes `decisionCount (free N.D).1` and `freeU N`. `freeU N` is
    `asU N (free N.D).1` by definition, so the value is the same; the route builds one free document per request,
    which `tests/test_readings_lean_sharing.py` checks on the compiled call graph. Pending with this reason.

## 13. SC-10: superposition under the soft completion (statement spec, 2026-10-31)

> Status: SC-10's statement spec, written 2026-10-31 on branch `design/spec-rd9-sc10` from `main` at `09fca5013`,
> from plan 4.11, D3, D11 and the SC-10/SC-11 batch text (plan 6). It replaces the sketch of 6.11, which plan 9 item
> 15 left for SC-10 to review. SC-11 (the route, the wire, the generators and the differential) is not specified
> here.
>
> **Elaborated.** Every declaration of 13.3 was elaborated in an untracked scratch stub (not committed) against an
> existing build whose `lean/VE/{Readings,NormDefaults,SoftNorms,Norms,Compose,Rights}` equal `main`'s at
> `09fca5013`. Definitions were elaborated with their bodies. Each theorem was elaborated as `def T : Prop := C`.
> Three `example`s were checked by `rfl`/`Iff.rfl` and one lemma was proved: the sketch's left side is
> `ConflictFreeX` by definition, and the order of the extra premises does not change `BaseAdmissibleX`
> (`baseAdmissibleX_swap`, *proved in the stub*). No `sorry` was written, and no theorem of 13.3 was proved.
> **Computed.** Each value marked *computed* in 13.5 was evaluated there with `#eval` on the merged fixtures of
> `Readings/SoftSeparateExamples.lean`, with the expression given beside it. *Derived* values were worked out by
> reading the sources and were not run.
>
> **Review round 1** (`manage-agents/debates/spec-rd9-sc10/`, two Opus seats, 2026-10-31): FIX. Its edits are
> applied: `hl : localFree` in `sd_superpose_countermodel` (E1); the CONFLICT-FREE fixture moved to `NSD4c`/`NSD4a`
> (E2, F2); necessary-condition premises read no bit (E3, F1, S-4′ *computed*); true/false fixtures (E4, F3); the
> `fill_sim_author` paraphrase (F4). The changed statement was elaborated again.

### 13.1 Definitions

`N : NDoc` is RD-1's pair of the decoded document `N.D` and the frame's `unspecified` predicates `N.unspec`, as in
1.2. `A : Choice` lists some candidates, each one a candidate of its set (`hA`), and a compatible choice `c` **takes
`A`** when every pair of `A` is in `c`.

- **The superposed document under the soft completion** is `supU N = asU N (sup N.D).1 =
  ⟨soften (correlate (sup N.D).1), N.unspec⟩` (merged, `Unspecified.lean`). It is S2a's superposed soft document
  read as norm-defaults reads a soft document. Its **filled tree** is `fill (supU N)`: `fill` runs after `soften`,
  on the superposed document, never on the readings document (D1).
- **Its extra base premises** are `supX N = softX N (sup N.D).1` (new). They are soft's `Exc_T` of the superposed
  document, then its `Coh_T` with each selection read on the filled tree, by the layered branch's one definition
  (`softLabelledU`, D2). A candidate's sufficient-condition and coherence premises read its bit (S-4); its
  necessary-condition premises do not (S-4′). At a slot-admissible base encoding `c`, a premise of a candidate not in
  `c` holds by its bit or, if it is a necessary condition, because the slot's `quietOwn` premise empties that
  candidate's `excepted` table.
- **The superposed base under `A`.** A structure `B` is admissible for the superposed document under `A` when
  `BaseAdmissibleX (supU N) (slotUnder N.D A ++ supX N) B` (merged definition). That means four things:
  - `B` is admissible for the base vocabulary of `fill (supU N)`, which holds the choice vocabulary and every
    `unsaid__p`;
  - `B` satisfies the filled tree's base background and `Fill_T` of `supU N`;
  - `B` satisfies S2a's slot premises and the atoms of `A`;
  - `B` satisfies `supX N`.

  The slot comes before `supX N`, which comes before `Fill_T` in `premisesX`, as the slot comes before the carried
  family in RD-6b's `slotUnder (fillDoc N) A ++ fillPremises (supU N)`.
- **An encoded filled base.** A structure `B` with `BaseAdmissible (fill (supU N)) B`, `Sat B (slotP N.D)`, and
  `Encodes N.D c B` for a compatible `c`. The bits of `B` name exactly `c` (merged `Encodes`).
- **The filled pull** `pullF N c B` (new) is S2a's `pull N.D c B` with the filled choice's vocabulary in place of the
  unfilled one. It keeps a relation `p` exactly when the full vocabulary of `fill (choiceU N c)` declares `p`, and
  reads it as `B` reads `nameMap N.D c p`. S2a's `pull` keeps only the predicates of `choiceEnvFull N.D c`, which is
  the unfilled choice's vocabulary and declares no `unsaid__p` (*computed*, 13.5 S-5). So `pull` would erase the
  filling. `nameMap` leaves `unsaid__p` unchanged (*computed*), so `pullF` carries the filling's tables across as they
  are.
- **The per-choice notions are the merged ones that SC-5's `sdSem` folds:**
  - `ConflictFreeX (choiceU N c) (choiceX N c)` is `sdSem`'s `free`;
  - `EntailsX (choiceU N c) (choiceX N c) ((choiceDoc N.D c).2 ++ Γ) φ` is its `entails`;
  - `CounterX (choiceU N c) (choiceX N c) ((choiceDoc N.D c).2 ++ Γ) φ` is its `counter`.
- **The filled shared vocabulary** `sharedEnvSD N = envAt (fill (freeU N)) (size (fill (freeU N)))` (new). It is the
  free document's filled full vocabulary: S2a's `sharedEnv N.D` plus every `unsaid__p`. RD-6b's
  `sharedEnv (fillDoc N)` plays the same part on the norms chain (OPEN-SC10-1).
- **The superposed certificate check** `supCertificateCheckSD N A Γ φ cert` (new) checks the certificate over the
  filled superposed document's full vocabulary. The premises are
  `premisesX (supU N) (slotUnder N.D A ++ supX N) ((sup N.D).2 ++ Γ)`: the filled tree's background, the slot, the
  atoms of `A`, `supX N`, `Fill_T`, the filled tree's layer definitions, the superposed (gated) assertions, then `Γ`.
- **The superposed model check** is the merged `modelCheckX (supU N) (slotUnder N.D A ++ supX N) M F
  ((sup N.D).2 ++ Γ) φ` on a finite model `M` and filling `F`. No new definition.

### 13.2 What each statement says (one reading each)

- **`fill_sim`.** Take an encoded filled base `B` of choice `c`. At any assignment `ρ`, for any regulated predicate
  `q` of the frame and either sign, the filled superposed tree decides `q` with that sign on its canonical
  interpretation of `B` exactly when the filled tree of `c`'s document decides it on its canonical interpretation of
  `pullF N c B`.
- **`fill_sim_author`.** The same, with "decides" asked only of the author rules (each document's `soften` rules,
  not `fill`'s `F_p` rules), which still read lower layers on the filled tree's canonical interpretation. The gap
  formula of `Fill_T` (`gapF`) reads this restriction.
- **`fillPremisesSD_pull`.** At an encoded filled base `B` of `c`, `B` satisfies `Fill_T` of the superposed document
  exactly when `pullF N c B` satisfies `Fill_T` of `c`'s document.
- **`supX_pull`.** At an encoded filled base `B` of `c`, `B` satisfies `supX N` exactly when `pullF N c B` satisfies
  `choiceX N c`.
- **`sd_superpose_conflict_free`.** Under `A`, the filled superposed document with its slot, `A`'s atoms, `supX N`
  and its `Fill_T` is conflict-free over every admissible base exactly when the following holds of every compatible
  choice that takes `A`: its filled document, with that choice's own extra premises `choiceX N c` and its own
  `Fill_T`, is conflict-free over every admissible base.
- **`sd_superpose_all`.** Suppose the superposed document under `A` is conflict-free in that sense, and a certificate
  over the superposed premises proves `φ` from `Γ`, where `Γ` and `φ` are written in the filled shared vocabulary.
  Then, for every compatible choice that takes `A`, `φ` holds in every expansion of the choice's filled document
  where its admissible base satisfies `choiceX N c` and the expansion satisfies the choice's assertions and `Γ`.
- **`sd_superpose_countermodel`.** Suppose a finite model `M` with a filling `F` passes the superposed model check
  under `A` (its admissibility, `Fill_T`, slot, atoms, `supX N`, the superposed assertions and `Γ` hold) and `φ` is
  false there, and no conflict formula of the filled superposed tree holds at any of its tuples (`localFree`). Then the model's bits name a compatible choice `c` that takes `A`, and that choice has a countermodel:
  some structure meets the choice's admissibility with `choiceX N c`, expands the choice's filled document, satisfies
  its assertions and `Γ`, and falsifies `φ`.

### 13.3 Lean: definitions and the exact statements to prove (`Readings/SoftSup.lean`, new)

`SoftSup.lean` imports `VE.Readings.SoftVerdicts` (for `CounterX`, `ConflictFreeX`, `EntailsX`, `choiceX`) and
`VE.Readings.SupExtra` (S2a and RD-6b). Neither imports it, so the graph stays acyclic. In the elaborated stub every
binder below was a `∀` of a `def … : Prop`; the build states each as a `theorem` with the binders as written.

```lean
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size)
open VE.NormDefaults (fill)
universe u

/-- The superposed document's extra base premises under the soft completion (D2 on `sup`). -/
def supX (N : NDoc) : List VE.Formula := softX N (sup N.D).1

/-- S2a's `pull` onto the filled choice's full vocabulary: keeps the `unsaid__` tables. -/
def pullF (N : NDoc) (c : Choice) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs =>
      (envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p ≠ none ∧ S.relation (nameMap N.D c p) vs }

/-- The free document's filled full vocabulary: the queries' vocabulary on the superposed route (OPEN-SC10-1). -/
def sharedEnvSD (N : NDoc) : VE.Environment := envAt (fill (freeU N)) (size (fill (freeU N)))

/-- A certificate on the filled superposed document under `A`: slot, atoms, `supX`, then `Fill_T` (`premisesX`). -/
def supCertificateCheckSD (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill (supU N)) (size (fill (supU N))))
    (VE.NormDefaults.Wire.premisesX (supU N) (slotUnder N.D A ++ supX N) ((sup N.D).2 ++ Γ)) φ cert

/-- `fill_sim`: the filled trees decide alike at an encoded filled base (S2a's `sim_decides`, `pull_canon` through
    `fill`). -/
theorem fill_sim (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (q : Regulated) (hq : q ∈ N.D.frame.soft.T.regulated)
    (ρ : VE.Valuation B) (sign : Bool) :
    VE.Norms.DecidesD (fill (supU N)).T (VE.SoftNorms.canon (fill (supU N)) B) ρ q.name sign ↔
      VE.Norms.DecidesD (fill (choiceU N c)).T (VE.SoftNorms.canon (fill (choiceU N c)) (pullF N c B)) ρ q.name sign

/-- The author rules (no `F_p`) decide alike: what `gapF` reads. -/
theorem fill_sim_author (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (q : Regulated) (hq : q ∈ N.D.frame.soft.T.regulated)
    (ρ : VE.Valuation B) (sign : Bool) :
    VE.Norms.DecidesD (supU N).D.T (VE.SoftNorms.canon (fill (supU N)) B) ρ q.name sign ↔
      VE.Norms.DecidesD (choiceU N c).D.T (VE.SoftNorms.canon (fill (choiceU N c)) (pullF N c B)) ρ q.name sign

/-- `Fill_T` transfers at an encoded filled base. -/
theorem fillPremisesSD_pull (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) :
    Sat B (VE.NormDefaults.fillPremises (supU N)) ↔ Sat (pullF N c B) (VE.NormDefaults.fillPremises (choiceU N c))

/-- `supX` transfers at an encoded filled base: a non-chosen candidate's premise holds by its bit or, for a necessary
    condition, by the slot's quiet premise. -/
theorem supX_pull (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) :
    Sat B (supX N) ↔ Sat (pullF N c B) (choiceX N c)

/-- Superposition under the soft completion: CONFLICT-FREE under `A` exactly when every compatible choice taking
    `A` is, each read with its own `X` and `Fill_T`. -/
theorem sd_superpose_conflict_free (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (A : Choice)
    (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    VE.NormDefaults.Wire.ConflictFreeX.{u} (supU N) (slotUnder N.D A ++ supX N) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU N c) (choiceX N c)

/-- ALL under `A`: a certificate on the filled superposed document proves `φ` in every compatible choice taking
    `A`, read in that choice's filled document with its own `X` (`sdSem`'s `entails`). -/
theorem sd_superpose_all (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (A : Choice)
    (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (hcf : VE.NormDefaults.Wire.ConflictFreeX.{u} (supU N) (slotUnder N.D A ++ supX N))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnvSD N) [])
    (hφ : φ.WellFormed (sharedEnvSD N) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckSD N A Γ φ cert = true) :
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
      VE.NormDefaults.EntailsX.{u} (choiceU N c) (choiceX N c) ((choiceDoc N.D c).2 ++ Γ) φ

/-- A checked filled model on the superposed document is a countermodel of the choice its bits encode
    (`sdSem`'s `counter`). -/
theorem sd_superpose_countermodel (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnvSD N) [])
    (hφ : φ.WellFormed (sharedEnvSD N) []) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt (supU N).D 0)) (F : VE.NormDefaults.FiniteFill (supU N) VE.Bridge.Entity)
    (hm : (VE.NormDefaults.modelCheckX (supU N) (slotUnder N.D A ++ supX N) M F ((sup N.D).2 ++ Γ) φ).1 = true)
    (hn : (VE.NormDefaults.modelCheckX (supU N) (slotUnder N.D A ++ supX N) M F ((sup N.D).2 ++ Γ) φ).2 = false)
    (hl : VE.Readings.Wire.localFree (supU N) M F = true) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧
      Encodes N.D c (VE.NormDefaults.withFill (supU N) M.asStructure (VE.NormDefaults.finFill M F)) ∧
      CounterX (choiceU N c) (choiceX N c) ((choiceDoc N.D c).2 ++ Γ) φ
end VE.Readings
```

What the proofs need, as guidance (not statements to freeze; helpers are the builder's):
- Downward (superposed to choice) is `fill_sim`'s route. An admissible base under `A` encodes a unique compatible
  `c` that takes `A` (S2a's `encodes_unique`, `encodes_atoms`). Its filled pull is admissible for `c`'s filled
  document. It satisfies `Fill_T` (`fillPremisesSD_pull`) and `choiceX N c` (`supX_pull`), and its conflict formulas
  agree with the superposed ones (`fill_sim`, as `superpose_conflict_iff` does on the unfilled trees).
- Upward is S2a's lift `upB`. Its third disjunct (`upRel`) keeps every relation that is not a choice decision, so
  the `unsaid__` tables cross unchanged. The non-chosen candidates' decision tables are empty, so their premises hold by
  their bits or, for a necessary condition, because the table is empty.
- `fill_sim` needs `fill` to read only the author roots' yields and the `unsaid__` tables. `SupFill.lean`'s
  `decidesBy_pull_canon`, `sim_decidesBy` and the `AuthorLite` lemmas are the norms-chain pieces.
  `fill (supU N)` is not `soften` of any superposed document, so RD-6b's `fill_supU` has no soft-chain counterpart.
  That is D3's reason why S2a's theorems are restated here and not reached by `Transfers`.
- The empty-carrier case of the upward direction is `conflictFree_empty`, as in S2a.

### 13.4 Differences from the sketch (plan 4.11 and 6.11)

1. **The left side is written `ConflictFreeX (supU N) (…)`.** The sketch wrote `∀ B, BaseAdmissibleX … B →
   ConflictFree (fill (supU N)) B`, which is the same proposition (`Iff.rfl`, checked in the stub).
2. **The premise order is `slotUnder N.D A ++ supX N`**, where the sketch had `supX N ++ slotUnder N.D A`. The two
   give the same `BaseAdmissibleX` (`baseAdmissibleX_swap`, *proved in the stub*). This order matches the plan's SC-11
   text ("`supX ++ Fill_T` after the slot"), RD-6b's order, and `premisesX`'s byte order for SC-11's certificates.
3. **`pullF` is new.** The sketch's "pulled to `c`" would, with S2a's `pull`, drop every `unsaid__p` table (13.1,
   *computed* S-5). On the norms chain, RD-6b did not need it, because there `fillDoc N` puts the `unsaid__`
   predicates in the frame.
4. **`fill_sim` is stated twice:** for the filled trees, and for the author rules that `Fill_T`'s gap formula reads.
   These are RD-6b's `decides_fill_pull` and `decides_author_pull` moved to the soft chain. The supX transfer the
   sketch described in prose is the iff `supX_pull`. It is an iff because a premise of a candidate not chosen holds at every
   encoded base (by its bit, S-4; by the quiet premise, S-4′).
5. **`sd_superpose_all` and `sd_superpose_countermodel` are written out.** The sketch only named them. Their
   per-choice conclusions are `sdSem`'s `entails` and `counter` (SC-5), so the soft fold can consume them unchanged.
   They are not S2a's named-structure form. The countermodel names the choice by the filled model's bits (`Encodes`),
   as S2a's does. `hcf` in `sd_superpose_all` is kept as S2a and RD-6b have it. `hl` is added: `CounterX` needs an
   expansion, which exists only at a conflict-free base; the per-choice route's `xModelOk` checks `localFree` for the
   same reason.
6. **Queries are typed over `sharedEnvSD N`** (OPEN-SC10-1).
7. **`superposable N.D` is the S2a check on the unfilled soft document, plus `WellFormedU (supU N)`.** This is the
   pair plan 6 names for SC-11's route. It is not `superposable (fillDoc N)` (RD-6b), since `fillDoc N` is not well
   formed on the soft chain (F-SD5).

### 13.5 Fixtures

*Computed* in the stub (build at `09fca5013`'s Lean sources), on the merged fixtures of `SoftSeparateExamples.lean`.
`facts N` is `(WellFormedSD N, superposable N.D, WellFormedU (supU N), (choices N.D).length,
(choices N.D).map (fun c => (choiceX N c).length), (softXL N (sup N.D).1).map (·.1))`. The build pins each with
`#guard` in a new `Readings/SoftSupExamples.lean`.

| # | Expression | Value |
|---|---|---|
| S-1 | `facts NSD1` (F-SD1: K1, `avoid_required` unspecified) | `(true, true, true, 2, [0, 0], [])` |
| S-2 | `facts NSD4` (F-SD4's `coherent`, a default reading with `X ≠ []`) | `(true, true, true, 2, [0, 2], ["soft:exception:rd-2-must-x:sufficient:0", "soft:coherence:need-not-x,rd-2-must-x"])` |
| S-2′ | `facts NC9` (C9′, three sufficient conditions); `facts NSD2` (K2, a necessary condition); `facts NSDq` | `(true, true, true, 2, [0, 3], ["soft:exception:rd-2-comply:sufficient:0", "…:1", "…:2"])`; `(true, true, true, 2, [0, 1], ["soft:exception:rd-2-no-deception:necessary:0"])`; `(true, true, true, 2, [0, 0], [])` |
| S-3 (D3) | on `NSD4`, whether each premise of `softXL NSD4 (sup NSD4.D).1` mentions `unsaid__y_permitted`; the same for S2a's own `cohPremises (correlate (sup NSD4.D).1)` | `[false, true]`; `[false]`: the superposed coherence premise on the filled tree reads the gap, and S2a's does not |
| S-4 (gating) | `predsOf` of each premise of `supX NSD4` | `[["c", "ve__bit__1__0", "soft__excepted__rd_2_must_x"], ["soft__excepted__need_not_x", "unsaid__y_permitted", "ve__bit__1__0", "unsaid__y_permitted", "ve__bit__1__0", "soft__excepted__rd_2_must_x", "unsaid__y_permitted", "ve__bit__1__0"]]`: each premise reads the candidate's bit |
| S-4′ (necessary) | `predsOf` of each premise of `supX NSD2`; whether it names a `ve__bit__` predicate | `[["soft__excepted__rd_2_no_deception"]]`; `[false]`: the necessary-condition premise reads no bit |
| S-5 (`pullF`) | for each choice `c` of `NSD1`: `((choiceEnvFull NSD1.D c).predicates "unsaid__avoid_required").isSome`, the same on `envAt (fill (choiceU NSD1 c)) (size …)`, `nameMap NSD1.D c "unsaid__avoid_required"`; and on `envAt (fill (supU NSD1)) 0` | `[(false, true, "unsaid__avoid_required"), (false, true, "unsaid__avoid_required")]`; `true` |
| S-6 (`Fill_T`) | `(fillPremises (supU N)).length` and each choice's, on `NSDq` and on `NSD1` | `(1, [1, 1])`; `(0, [0, 0])` |
| S-7 (pairs) | colliding pairs of `correlate (sup NSD4.D).1` and of each choice's document; the choices' `softXL` labels on `NSD4` and on `NC9` | `[("need-not-x", "rd-2-must-x")]` and `[[], [("must-x", "need-not-x")]]`; `[[], ["soft:exception:must-x:sufficient:0", "soft:coherence:must-x,need-not-x"]]`; `[[], ["soft:exception:comply:sufficient:0", "…:1", "…:2"]]` |

Each iff with a fixture per direction (the 8.2 rule):

| Claim | One direction | The other |
|---|---|---|
| `sd_superpose_conflict_free` | CONFLICT-FREE on both sides: `NSD4c` under `A = [(rs1,1)]`: the strict `need-not-x` blocks the default `must-x`, so neither `x_required` nor `x_required→x_permitted` is reached (*derived*). `NSD4a` (`NSD4` with `x_permitted` allowed by default, as the merged F-SD4 test sets it) under `A = [(rs1,1)]`: CONFLICT-FREE on both sides, resting on `supX`'s coherence premise; the same document with `[]` for `supX N` is CONFLICT (*derived*) | CONFLICT on both sides: `NSD4c`, which is `NSD4a` with the fixed unit `need-not-x` made strict (`strictNode "need-not-x" "x_required" false`). Under `A = []`, choice `(rs1,0)` (strict `must-x`, guard `y_permitted`) conflicts with it wherever the filling says `y_permitted`, so the superposed side is not CONFLICT-FREE (*derived*); `NSD4` under `A = []`: a pair conflict wherever the filling says `y_permitted` (*derived*) |
| `supX_pull` | `NSD4`, choice `(rs1,1)`: two premises on each side (S-2, S-7, *computed*) | choice `(rs1,0)`: two superposed premises, gated off by the bit, against zero choice premises (S-2, S-4, *computed*) |
| `supX_pull`, both sides false | `NSD4`, `(rs1,1)`, `c = {a}`, `soft__excepted__rd_2_must_x = ∅`: the sufficient-condition premise fails on both sides (*derived*) | — |
| `supX_pull`, `hsl` needed | `NSD2`, bits naming `(rs1,0)`, `soft__excepted__rd_2_no_deception = {(a,u)}`: the slot is broken, `supX` is false while `choiceX = []` holds (*derived*; S-4′) | — |
| `fillPremisesSD_pull` | `NSDq`: one `Fill_T` premise on each side (S-6, *computed*) | `NSD1`: none on either side (S-6, *computed*) |
| `fillPremisesSD_pull`, both sides false | `NSDq` at `base1 []` (`!fillHoldsS … (base1 [])`, `SoftSeparateExamples.lean`) (*derived*) | — |
| `fill_sim` (with `pullF`, not `pull`) | `F_p` reads `unsaid__p`, which the filled choice vocabulary declares (S-5, *computed*) | with S2a's `pull` the table is dropped (S-5 `false`), so `F_p` would never apply on the choice side: the statement would be false at any filling that says yes (*derived*) |
| `fill_sim`, a pair of truth values | `NSD1`, bits naming `(rs1,1)`, `soft__excepted__rd_2_no_deception = {(a,u)}`. With the filling yes, both filled trees decide `avoid_required (a,u)` positively, and on both sides the author rules decide it neither way (*derived*) | With the filling empty, neither filled tree decides it positively (*derived*) |
| `fill_sim_author`, both sides true | `NSD1`, `(rs1,0)`, empty tables: the strict `no-deception` decides `avoid_required (a,u)` positively on both sides (*derived*) | — |
| `sd_superpose_all`, `sd_superpose_countermodel` | `NSD1` under `A = [(rs1,0)]`, query `∀ agent ∀ user. avoid_required`: a certificate exists and the choice's row is `proved` (F-SD1.verdicts, *derived*) | under `A = []`: no certificate (choice `(rs1,1)` is `refuted`), and a filled model with `soft__excepted__rd_2_no_deception = {(a,u)}` and the filling no, with the `rs1` bit on 1, is a countermodel whose bits name `(rs1,1)` (*derived*); `localFree` true. Without `hl`: `NSD4`, `A = [(rs1,0)]`, `Γ = [∃a. y_permitted a]`, `φ = ⊥`, one assistant `a`, bits naming `(rs1,0)`, `unsaid__y_permitted = {a}`, every `excepted` table empty: the model passes `modelCheckX`, and no `CounterX` exists (*derived*) |

The *derived* rows are checked through the existing per-choice soft route (`readings-choice`, `readings-verdicts`) in
SC-10's build. SC-11's 200-document differential then compares the routes. No superposed route answer exists before
SC-11.

### 13.6 Not claimed

- No theorem relates `sd_superpose_*` on a norms-shaped document to RD-6b's `nd_superpose_*`, which reaches it through
  `fillDoc` (the same gap as Q3).
- Nothing about the route, the wire, labels, generators or English. Those are SC-11's. In particular, `supX`'s labels
  name the superposed document's qualified rules (`rd-2-must-x`), and they order a coherence pair by those names
  (S-2, S-7). Nothing here maps them to the choices' labels (OPEN-SC10-2).
- No superposition on the rights chain under the completion, and nothing about companions on the soft chain.
- No speed, and no claim that a superposed answer is ever found within budget.

### 13.7 OPEN

- **OPEN-SC10-1 (the queries' vocabulary).** `Γ` and `φ` are typed over `sharedEnvSD N`, the free document's filled
  vocabulary. So a query may name a filled gap `unsaid__p`, as RD-6b's `sharedEnv (fillDoc N)` allows on the norms
  chain. The plan does not say which vocabulary the superposed soft route's queries use. The narrower `sharedEnv N.D`
  (no `unsaid__`) would give weaker statements that are also true. Either choice fixes SC-11's wire check. This spec
  takes the RD-6b analogue, and the review or the DRI confirms it.
- **OPEN-SC10-2 (SC-11, out of SC-10's scope).** A superposed answer's `soft_premises` and `conditional_on` would list
  `supX`'s labels, which differ from every choice's (S-2, S-7). Whether SC-11 shows the superposed labels, maps them
  through `nameMap` to each choice's, or shows the per-choice labels is SC-11's decision. The plan leaves it open.
  SC-10's statements do not depend on it.
- SC-11's statement spec is section 14: 14.4 applies the DRI's direction on OPEN-SC10-2, and 14.15 lists SC-11's own OPEN lines.

### 13.8 Review checklist (SC-10's statement review)

1. Each statement of 13.3 is true under its hypotheses, not only well typed. In particular:
   - `supX_pull` is an iff because a premise of a candidate not chosen holds at every encoded base (by its bit, S-4;
     by the quiet premise, S-4′);
   - `fill_sim` needs `pullF`, not `pull` (S-5);
   - the upward direction of `sd_superpose_conflict_free` goes through `upB`, which keeps the `unsaid__` tables.
2. The per-choice sides are `sdSem`'s `free`, `entails` and `counter` (SC-5), and universes match: `ConflictFreeX.{u}`
   and `EntailsX.{u}` as in `xSem`, and `CounterX` at universe 0, as in `xSem`.
3. The differences of 13.4 are each accepted or sent back.
4. The fixtures of 13.5: each *computed* value is as recorded, and each iff has a fixture per direction.
5. OPEN-SC10-1 and OPEN-SC10-2 are stated, not decided.
6. Placement and imports (D13): `SoftSup.lean` holds only soft-chain code; no general definition with `X` moves.

## 14. SC-11: the superposed route under the soft completion (statement spec, 2026-11-03)

> Status: SC-11's statement spec, written 2026-11-03 on branch `design/spec-sc11` from `main` at `90807e7f7`, from plan
> D3, D11, 3.3 step 5, S2a's DRI ruling 5 (composition-s2 4.1 step 3), the SC-10/SC-11 batch text (plan 6), section 13,
> DRI decisions `reviews/dri-decisions-20261031-sc-10.md` items 1 and 2, and edit 5 of synthesis round 2.
>
> **Not elaborated.** This item ran no Lean and no Python, by its task. The statements of 14.8 are written against the
> sources at `90807e7f7`, and every name they use was read there, except the three theorems of 13.3 that sc-10b builds.
> The builder elaborates each one first, before proving anything. A statement that does not elaborate, or is false as
> written, goes back to the DRI with its counterexample. Fixture values are *derived*, except where marked *pinned*
> (already a `#guard` on main).

### 14.1 Definitions

`N`, `A`, `supU N`, `supX N`, `pullF`, `sharedEnvSD N` and `supCertificateCheckSD` are as in 13.1. `re` is the case's
`ReadingsEnvironment`, and `r : AdmittedSD` is the case's one admission.

- **A superposable soft document** (`sdSuperposable N`): `superposable N.D` and `WellFormedU (supU N)` (13.4 item 7).
- **The per-choice check** (`sdChecked re N`) is S2a's DRI ruling 5 extended by 3.3 step 5. The compatible choices number
  at most `maxChoiceChecks` (1024), `sdCheckWork N` is within `maxSdCheckWork` (14.11), and `sdChoiceText re N c` is
  `none` for each of them. `sdChoiceText` is the merged check of 3.3 step 5, S2a's chain text and then step 3's
  checks on `choiceU N c`.
- **The superposed labelled premises** are `softXL N (sup N.D).1`, the labelled form of `supX N`. A **superposed label**
  is the first component of one of them (S-2: `soft:coherence:need-not-x,rd-2-must-x`). A **choice label** of `c` is a
  first component of `softXL N (choiceDoc N.D c).1` (S-7: `soft:coherence:must-x,need-not-x`).
- **The label image** `labelImage N c` pairs each choice label of `c` with the superposed label of the same premise.
  A rule of `c`'s document is sent to its name in `sup D` by `fmap N.D c`, the node form of `qName`. `nameMap` itself maps
  generated *predicate* names, and it reads rule names through `qName` (`qualifyKey`). A label carries rule names, so
  the DRI's "through `nameMap`" is stated at `fmap`, the rule-name layer that `nameMap` is built on. An exception
  label keeps its role and index. A coherence label is rebuilt with the two image names ascending (`collidingPairs`
  orders by name), which is why S-7's pair changes order.
- **A dead premise of `c`** is a superposed labelled premise whose label is in no pair of `labelImage N c`: an exception
  premise of a candidate `c` does not take, or a coherence pair with a member `c` does not take. A pair of two candidates
  of one set is dead in every choice. A dead premise holds at every encoded filled base of `c`, by `supLabel_other`.
- **The shown labels** `sdShown N A used` take the superposed labels `used` that an accepted piece of evidence depends
  on. They are the choice labels whose image is in `used`, read over the compatible choices taking `A` in canonical
  order, each once. A used label with no image under `A` is dead in every choice taking `A`. It is not shown, and no
  other name is shown in its place.
- **The soft row**: the `readings-elaborate` row of a document whose `routeSD` is superposed (14.3).

### 14.2 The route condition

`routeSD re N` is `routeOf true N.D` with one change: its `enumerated` row becomes `superposed` exactly when
`sdSuperposable N` and `sdChecked re N` hold. Otherwise that row stays enumerated, as today, with at most 64 compatible
choices and the finding `ReadingsNotSuperposable: <sets>` with cause `the unspecified completion` (D3, OPEN-SC11-3).
The `w2`, `pending` and abstention rows are unchanged. `routeOf` and `routeND` are not edited: the norms chain keeps
`routeND`, and the rights chain keeps the abstention. `routeSD` is read only under `underSoftCompletion`.

- **When the check can fail on a document admission accepted.** Admission already refuses a failing choice at most 64
  (3.3 step 5, with its text). So `sdChecked` can fail only past 64 choices: a choice from 65 to 1024 that fails,
  more than 1024 choices, or `sdCheckWork` over the limit. Each of these gives the enumerated row (`choice_count:
  "over 64"`, verdicts UNKNOWN by budget), never a verdict over an unchecked choice. This differs from RD-6b, whose row
  stays superposed and refuses with the text. The batch text makes the check part of the route's condition, and an
  UNKNOWN from the enumerated row is the answer the document already has today.
- **No compatible choice.** `unsatText` first on every kind, as today (4.1 step 3), whichever row `routeSD` gives.
- **What ends synthesis edit 5.** Edit 5 says a soft-chain document's readings route enumerates until SC-10/11 land.
  That holds until the merge that switches the dispatch (sc-11b, 14.13). From that merge, on a document under the soft
  completion, the superposed route answers exactly in the kinds below when `routeSD re N = .superposed`. sc-10b and
  sc-11 alone change no answer.

| Kind | `routeSD` superposed | `routeSD` enumerated |
| --- | --- | --- |
| `readings-validate`, `readings-separate`, `readings-dead` | as today, byte-identical (they read no route) | as today |
| `readings-choice` | as today, byte-identical (4.3: `choiceLayeredG`) | as today |
| `readings-elaborate` | the soft row (14.3) | as today, byte-identical |
| `readings-conflict`, `-certificate`, `-model` | answered (14.3, 14.8) | today's `sdRefusal` text |
| `readings-verdicts` with `budget` | the superposed answer (14.3) | RD-3's answer, `runVerdictsSD` |
| `readings-verdicts` without `budget` | RD-3's answer, `runVerdictsSD` (the service contract `runS2ND` keeps on the norms chain) | as today |

### 14.3 The wire

**Order.** Each premise list is the slot, then `A`'s atoms, then `supX N`, then `Fill_T`: 13.4 item 2's
`slotUnder N.D A ++ supX N` as `X`, with `Fill_T` after it in `premisesX`. A conflict certificate is checked over
`backgroundBase (fill (supU N)) ++ slotUnder N.D A ++ supX N ++ fillPremises (supU N)`
(`conflictFreeCheckX (supU N) (slotUnder N.D A ++ supX N)`) for each target of `fill (supU N)`. A query certificate is
checked by `supCertificateCheckSD` and bound by `bindCertX` (D14, F-SD11): a certificate whose binding leaves out a
regenerated premise, or adds one, is diagnostic 11. A model is `modelCheckX (supU N) (slotUnder N.D A ++ supX N)` with
a separate `filling`, and an `unsaid__` table in `relations` is refused (F-SD8). A reported model also has `localFree`.
Queries are typed over `sharedEnvSD N` (DRI item 1).

**Requests.** The superposed kinds keep S2a's and RD-6b's members. A model gains `filling`, as `choice-model` has it.
No other request member changes.

**The soft row.** `readings-elaborate` on `routeSD = .superposed` gives:

- as RD-6b's row, read on `N.D` and not on `fillDoc N` (F-SD5): `route: "superposed"`, `generated_predicates`,
  `finding: null`, `narrowings_stale`, `vocabulary`, `units`, `slot`, `names`, the choices (`choicesJson`),
  `choices_checked`, `sizes`, `fill` (`fillLabelled (supU N)`);
- the completion's fields, unchanged and byte-identical to the enumerated row's: `fill_premises`, `soft_premises`, `filled`;
- new, because Python builds no `fill`, `X` or `Coh_T` (D12): `soft`, a list of `{label, ast}`, one entry per premise of
  `supX N` in its order; and the filled superposed tree's `base_environment`, `filled_premises` (layers), `conflict_targets`
  and `unsaid`, in the shapes `norm-defaults-elaborate` gives them for a choice (`_FilledChoiceDocument`).
  `soft[].label` is the choice label the premise is the image of (14.4), or `null` for a premise dead in every
  compatible choice. Two entries may share a label (fixture W-4).

**The verdict answer.** `readings-verdicts` with `budget` has `runSupVerdicts`' shape, with the `nd` behaviour of
`supResult`: per-choice statuses in `choices`, and the fold under named readings (SOME, NONE), never "NOT ALL" (the RD-6b
review's finding). On the soft chain these members differ from RD-6b's:

- `conditional_on` (also on each `proofs[]`) is `sdShown` of the used `supX` labels, then the used `Fill_T` labels,
  then `restrictionsFor D A`, each once. Slot labels are not conditions here: the enumerated route never lists them,
  and they stay in `reading_premises_used`.
- `reading_premises_used`, `scopes[].used` and `english[].label` show a soft premise only by its shown label.
- `decided_units` is present, as on the enumerated row (OPEN-SC11-6). With no named reading and at most 64 choices, it is
  1.12's rule on the rows the scopes establish: `setDecided` and `fixedDecided`, with a choice's conflict row `free` when the
  global scope is CONFLICT-FREE and else that choice's own scope's, and each reading's status from its candidate scope, dead
  and narrowed as in `readingPremise`. The premises question under no named reading therefore lists the complete choices
  too while the global conflict status is open (`supOpen`, on the soft chain only). Otherwise `[]`.
- `english`: `supPlan`, with each used soft label through `conditionItems`, the lines the enumerated route gives it (D12: no
  new wording), and `Fill_T` labels by `P1`. A gated UNKNOWN gets its E12 line (R8 or R4), which RD-6b's planner lacks
  (readings-defaults 2.4 records that gap): the soft chain has that line today, so it may not lose it.

**What changes and what stays byte-identical**, for a document that moves from the enumerated to the superposed row:

| Field | After |
| --- | --- |
| `soft_premises`, `fill_premises`, `filled`, per-pair `gaps`, `choice_count`, `choices`, `narrowings_stale` on `readings-elaborate` | byte-identical |
| every `readings-validate`, `readings-separate`, `readings-dead`, `readings-choice` answer | byte-identical |
| `readings-verdicts` without `budget` | byte-identical |
| `route`, `finding`, `choices_checked` on `readings-elaborate` | `superposed`, `null`; `choices_checked` counts up to 1024 |
| `vocabulary`, `units`, `slot`, `names`, `sizes`, `fill`, `soft`, `base_environment`, `filled_premises`, `conflict_targets`, `unsaid` on `readings-elaborate` | new on this row |
| `readings-conflict`, `-certificate`, `-model` | answered, not `sdRefusal` |
| verdict `status`, `verdict`, per-choice and per-candidate statuses, `conditional_on` as a set, `decided_units` | the same as the enumerated answer at most 64 choices (14.6) |
| verdict `route`, `status_text`, `evidence`, `reading_premises_used`, `scopes`, `model_proposals`, `model`, `countermodel`, `english` | the superposed route's own; the "checked one at a time" sentence would be false here and is dropped, as in RD-6b |
| a query naming a decision predicate of one reading (for example `soft__excepted__must_x`) | refused as outside `sharedEnvSD N` (DRI item 1); the enumerated route types it over the first choice's vocabulary (OPEN-SC11-4) |

Past 64 choices the verdicts are new answers where today's are UNKNOWN (OPEN-SC11-4).

### 14.4 The label mapping (DRI item 2)

A superposed answer shows each choice's own labels. `supX`'s labels are read through `labelImage`, and no label field
carries a qualified `rd-<k>-` name. By 14.8's label theorems the mapping is total in the sense the ruling needs:

- every choice label has exactly one image, and that image is a superposed label (`labelImage_fst`, `labelImage_snd_mem`);
- at an encoded base of `c`, a premise and its image hold together (`supLabel_pull`);
- every other superposed premise holds at that base (`supLabel_other`), so leaving it out of `conditional_on` hides no
  condition the answer rests on under `c`;
- one superposed label has one choice label in every choice that has it (`labelImage_functional`), so `soft[].label` is
  well defined.

So no document needs the ruling's refusal, and `ReadingsNotSuperposable` is not added for labels. If elaboration or
proof shows one of these four false, the build stops at that theorem and the fallback applies: a new OPEN line, and the
route enumerates on those documents. It does not show an unmapped name.

`Fill_T` labels (`unsaid:pair:<r>,<m>`) name predicates and are the same on the superposed document and on every
choice (`fillLabels_choice`). Slot labels (`readings:<set>@<v>:<i>:quiet`, `:one`, `coupling:`, `narrowing:`,
`readings:quiet:outweighs:…`) name sets and keys, never a qualified rule.

The ruling's scope is read as *labels*. `names`, `units`, `vocabulary`, `generated_predicates`, ASTs and a shown model's
`relations` are machine fields that carry qualified names on S2a's and RD-6b's rows today, and a generator needs them
(OPEN-SC11-1). No English line prints one (`supRuleName`, fixture W-1).

### 14.5 The generators

**Evidence.** Python's prover and model search stay untrusted generators (`ve/readings_verdicts/superposed.py`). On the
soft chain they run on Lean's row and nothing Python builds: `Superposed` takes the base environment, the extended
environment, the layers, the targets and the premises from the soft row, as `_FilledChoiceDocument` does for a choice,
and does not call `superposed_document`, whose soft elaborator reads the placeholder `deny`. The premise list is
`_labelled`'s in 14.3's order, with `soft` between the atoms and `fill`. `_prove`'s labelled minimisation runs over the
slot, `soft` and `fill` entries; a `null`-labelled `soft` entry counts as labelled there, so a dead premise is dropped
from a proof when the proof holds without it. `_lifted` is not used, as under RD-6b. Lean checks each piece. A refusal of
evidence Python's own check accepted is `CheckerUnavailable`. `context` needs no change, since it reads `route`.

**Documents.** `generated(index)` in `tests/test_readings_sc11_differential.py` (new), in the shape of
`tests/test_readings_rd6b_differential.py`, seeded `sc11-differential:<index>`, independent per index:

- environment: one or two regulated pairs, each with an unspecified member, the two conditions `c1`, `c2`, on the soft chain
  under `norm-defaults@0`;
- sets: one, two or three, with two or three readings each, drawn from strict duty, default duty, default duty with a
  sufficient condition, default duty with a necessary condition, default duty under a guard on an unspecified permission,
  and permission; three documents at exactly 64 choices (six sets of two), which run only the implication query;
- fixed unit: none, a default `need-not` (a coherence pair, `X ≠ []`), a strict prohibition under a condition, or a permission;
- a separating situation for each pair of readings, over `filledAuthorEnv N`, found by `ve.readings_s1.search`;
- query: as RD-6b's three, in the shared vocabulary, with or without `--under` a reading of the first set; the general
  queries where the choices are at most 4, the implication elsewhere.

A generated document that admission or `routeSD` does not send to the soft row is not skipped: the test fails, naming it.

### 14.6 The differential

200 documents, at most 64 compatible choices each, answered on both routes. The superposed route is `Superposed(loaded)`.
The enumerated oracle is `Enumerated({**loaded, "readings_s2": enumerated_row})` with today's enumerated row, as in RD-6b's test.

**Identical means**, per document:

1. `conflict` status, and each compatible choice's status in canonical order;
2. `premises` status, and each candidate's status and index;
3. the query's `verdict`;
4. `conditional_on`, as a **set of strings**, on every CONFLICT-FREE, ALL and INCONSISTENT answer. This is the DRI's "the
   same strings"; its order is not compared, because each route lists a label at the first choice or premise that used it;
5. `soft_premises` and `fill_premises`, byte-identical;
6. `decided_units` of the premises question under no named reading.

**On the superposed side only:** every label in `conditional_on`, `reading_premises_used`, `scopes[].used`,
`english[].label` is a slot label, a `Fill_T` label, a restriction, or a choice label of a compatible choice taking `A`; no
such field contains the `rd-<k>-` of any qualified name in the row's `names`.

**Not compared:** the fields 14.3 calls the route's own; a witness's or countermodel's model and named choice (each route
shows its own checked one, and each is checked).

**Guards.** ≥ 100 distinct shapes, none repeated more than 6 times; both conflict statuses and at least two verdicts in every
chunk; `X ≠ []` on at least a third of the documents; an answer listing a coherence label, a sufficient label and a
necessary label each at least once; the choice counts include 2, 3, 4, 6, 9 and 64; `--under` on 60 to 140 documents; 15
chunks, as RD-6b.

`conditional_on` equality is **checked here and not proved**: each route's list is what its own certificate used, and both
are sound. A UNKNOWN on one side and a decided answer on the other is a difference too. A seed that differs fails the
test; no seed is dropped and no generator narrowed without a DRI ruling (OPEN-SC11-5).

### 14.7 What each statement says (one reading each)

- **`labelImage_fst`.** The first components of `labelImage N c` are exactly `c`'s choice labels, in their order.
- **`labelImage_snd_mem`.** Every second component of `labelImage N c`, for a compatible `c`, is a superposed label.
- **`labelImage_functional`.** If two compatible choices each pair a choice label with the same superposed label, those two
  choice labels are the same string.
- **`supLabel_pull`.** At an encoded filled base `B` of `c`, a superposed premise holds at `B` exactly when the choice's premise
  it is the image of holds at `pullF N c B`.
- **`supLabel_other`.** At an encoded filled base `B` of `c`, a superposed premise whose label is no image for `c` holds at `B`.
- **`sdShown_mem`.** A shown label under `A` is a choice label of some compatible choice taking `A`.
- **`sdShown_image`.** If a used superposed label is the image of a choice label of a compatible choice taking `A`, that choice
  label is shown.
- **`fillLabels_choice`.** A compatible choice's `Fill_T` labels are the superposed document's, in the same order.
- **`routeSD_superposed_iff`.** The route is superposed exactly when `routeOf true N.D` is enumerated, `sdSuperposable N` holds
  and `sdChecked re N` holds.
- **`sdChecked_spec`.** If the check passes, every compatible choice has `sdChoiceText` none and its `choiceU N c` is `WellFormedU`.
- **`sdCheck_of_admitted`.** On an admitted document with at most 64 compatible choices, whose work is within the limit, the
  check passes, so it need not be run a second time.
- **`readings_wire_sd_choices`.** A replayed superposed case has a compatible choice, and every compatible choice is `sdChecked`'s
  conclusion.
- **`readings_wire_sd_conflict_sound`.** If the conflict certificates are accepted under `A`, every compatible choice taking `A`
  is conflict-free, read in its own filled document with its own `choiceX`.
- **`readings_wire_sd_all_sound`.** If in addition a certificate of `φ` from `Γ` is accepted under `A`, then every compatible
  choice taking `A` entails `φ` from its assertions and `Γ`, with its own `choiceX`.
- **`readings_wire_sd_model_sound`.** If a filled model passes the check under `A`, with `φ` false there and no conflict at any
  tuple, its bits name a compatible choice taking `A`, and that choice has a countermodel.
- **`readings_wire_sd_consistent_sound`.** The same model with `φ = ⊥` and `Γ = []` shows that choice's assertions consistent.
- **`readings_wire_sd_witness_sound`.** If a filled model passes the base checks under `A` and a target of the filled superposed
  tree holds at a typed tuple, its bits name a compatible choice taking `A`, and that choice is not conflict-free.

### 14.8 Lean: the exact statements (no proofs; D13 placement)

Two new files, soft-chain code only; no general definition with `X` moves. `lean/VE/Readings/SoftSupLabels.lean` imports
`VE.Readings.SoftSup`. `lean/VE/Readings/SoftSupWire.lean` imports `VE.Readings.SoftSupLabels` and
`VE.Readings.SupVerdictsWire`, and `Readings/Run.lean` imports it. Neither `SoftSup.lean` nor `SupVerdictsWire.lean` imports
these, so the graph stays acyclic. `SupVerdictsWire.lean` may gain the parameters its soft use needs (the `nd` flag's reading,
`supOpen`'s premises row, the gated-UNKNOWN line), each leaving the norms chain's bytes unchanged. `#guard`s go in
`Readings/SoftSupWireExamples.lean`.

```lean
-- lean/VE/Readings/SoftSupLabels.lean
namespace VE.Readings
open VE.Norms (Sat)
universe u

/-- One rule's exception labels (the node form of `excLabels`). -/
def nodeExcLabels (M : VE.SoftNorms.SoftNode) : List String :=
  match M.mode, M.exception with
  | .default, some e =>
    (List.range e.sufficient.length).map (fun i => s!"soft:exception:{M.name}:sufficient:{i}") ++
      (List.range e.necessary.length).map (fun i => s!"soft:exception:{M.name}:necessary:{i}")
  | _, _ => []

/-- (choice label, superposed label) of each soft premise of `c`'s document. -/
def labelImage (N : NDoc) (c : Choice) : List (String × String) :=
  let Y := (choiceDoc N.D c).1.soft
  Y.T.nodes.flatMap (fun M => (nodeExcLabels M).zip (nodeExcLabels (fmap N.D c M))) ++
    (VE.SoftNorms.collidingPairs Y).map (fun x =>
      let a := fmap N.D c x.1
      let b := fmap N.D c x.2
      (VE.SoftNorms.Wire.cohLabel x.1 x.2,
        if a.name < b.name then VE.SoftNorms.Wire.cohLabel a b else VE.SoftNorms.Wire.cohLabel b a))

/-- What an answer shows for the superposed labels `used`: choice labels of the compatible choices taking `A`. -/
def sdShown (N : NDoc) (A : Choice) (used : List String) : List String :=
  VE.SoftNorms.dedup (((checkedChoices N.D).filter (fun c => A.all (c.contains ·))).flatMap (fun c =>
    (labelImage N c).filterMap (fun p => if used.contains p.2 then some p.1 else none)))

theorem labelImage_fst (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c) :
    (labelImage N c).map (·.1) = (softXL N (choiceDoc N.D c).1).map (·.1)

theorem labelImage_snd_mem (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (p : String × String) (hp : p ∈ labelImage N c) :
    p.2 ∈ (softXL N (sup N.D).1).map (·.1)

theorem labelImage_functional (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c₁ c₂ : Choice) (h₁ : Compatible N.D c₁)
    (h₂ : Compatible N.D c₂) (l₁ l₂ s : String) (hp₁ : (l₁, s) ∈ labelImage N c₁) (hp₂ : (l₂, s) ∈ labelImage N c₂) :
    l₁ = l₂

theorem supLabel_pull (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (VE.NormDefaults.fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (l s : String) (a a' : VE.Formula) (hp : (l, s) ∈ labelImage N c)
    (ha : (l, a) ∈ softXL N (choiceDoc N.D c).1) (ha' : (s, a') ∈ softXL N (sup N.D).1) :
    a'.denote B [] ↔ a.denote (pullF N c B) []

theorem supLabel_other (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c)
    (B : VE.Structure.{u}) (hB : VE.Norms.BaseAdmissible (VE.NormDefaults.fill (supU N)) B) (hsl : Sat B (slotP N.D))
    (he : Encodes N.D c B) (s : String) (a' : VE.Formula) (ha' : (s, a') ∈ softXL N (sup N.D).1)
    (hn : ∀ p ∈ labelImage N c, p.2 ≠ s) :
    a'.denote B []

theorem sdShown_mem (N : NDoc) (hr : supReady N.D = true) (hle : (checkedChoices N.D).length ≤ maxChoiceChecks)
    (A : Choice) (used : List String) (l : String) (hl : l ∈ sdShown N A used) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ l ∈ (softXL N (choiceDoc N.D c).1).map (·.1)

theorem sdShown_image (N : NDoc) (hr : supReady N.D = true) (hle : (checkedChoices N.D).length ≤ maxChoiceChecks)
    (A : Choice) (used : List String) (c : Choice) (hc : Compatible N.D c) (hA : ∀ x ∈ A, x ∈ c)
    (l s : String) (hp : (l, s) ∈ labelImage N c) (hu : s ∈ used) :
    l ∈ sdShown N A used

theorem fillLabels_choice (N : NDoc) (hN : WellFormedSD N = true) (hs : superposable N.D = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true) (c : Choice) (hc : Compatible N.D c) :
    VE.NormDefaults.Admission.fillLabels (choiceU N c) = VE.NormDefaults.Admission.fillLabels (supU N)
end VE.Readings
```

```lean
-- lean/VE/Readings/SoftSupWire.lean
namespace VE.Readings.Wire
open VE.Readings
open VE.Bridge (Entity)
open VE.Norms (targets)
open VE.NormDefaults (fill)
universe u

def sdSuperposable (N : NDoc) : Bool := superposable N.D && VE.NormDefaults.WellFormedU (supU N)

/-- 14.11: the compatible choices times the superposed premises and rule nodes each check reads. -/
def maxSdCheckWork : Nat := 4194304
def sdCheckWork (N : NDoc) : Nat :=
  (checkedChoices N.D).length * ((softXL N (sup N.D).1).length + ((sup N.D).1.soft.T.nodes.map
    (fun M => (M.guard :: M.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum)

/-- DRI ruling 5 extended by 3.3 step 5, within its limits. -/
def sdChecked (re : ReadingsEnvironment) (N : NDoc) : Bool :=
  decide ((checkedChoices N.D).length ≤ maxChoiceChecks) && decide (sdCheckWork N ≤ maxSdCheckWork) &&
    (checkedChoices N.D).all (fun c => (sdChoiceText re N c).isNone)

def routeSD (re : ReadingsEnvironment) (N : NDoc) : Route :=
  match routeOf true N.D with
  | .enumerated => if sdSuperposable N && sdChecked re N then .superposed else .enumerated
  | r => r

/-- A superposed case on the soft chain: the case's one admission, its route, a compatible choice. -/
structure SupReplaySD where
  r : AdmittedSD
  route : routeSD r.b.a.re r.N = .superposed
  sat : (choices r.N.D).isEmpty = false

theorem routeSD_superposed_iff (re : ReadingsEnvironment) (N : NDoc) :
    routeSD re N = .superposed ↔
      routeOf true N.D = .enumerated ∧ sdSuperposable N = true ∧ sdChecked re N = true

theorem sdChecked_spec (re : ReadingsEnvironment) (N : NDoc) (hr : supReady N.D = true)
    (hw : sdChecked re N = true) (c : Choice) (hc : Compatible N.D c) :
    sdChoiceText re N c = none ∧ VE.NormDefaults.WellFormedU (choiceU N c) = true

theorem sdCheck_of_admitted (r : AdmittedSD) (hr : supReady r.N.D = true)
    (hle : (checkedChoices r.N.D).length ≤ maxChoices) (hw : sdCheckWork r.N ≤ maxSdCheckWork) :
    sdChecked r.b.a.re r.N = true

theorem readings_wire_sd_choices (x : SupReplaySD) :
    (∃ c, Compatible x.r.N.D c) ∧ ∀ c, Compatible x.r.N.D c →
      sdChoiceText x.r.b.a.re x.r.N c = none ∧ VE.NormDefaults.WellFormedU (choiceU x.r.N c) = true

theorem readings_wire_sd_conflict_sound (x : SupReplaySD) (A : Choice)
    (hA : ∀ z ∈ A, (candidate x.r.N.D z.1 z.2).isSome) (certs : List (Option VE.Tableau.Certificate))
    (hc : VE.NormDefaults.Wire.conflictFreeCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) certs = true) :
    ∀ c, Compatible x.r.N.D c → (∀ z ∈ A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N c) (choiceX x.r.N c)

theorem readings_wire_sd_all_sound (x : SupReplaySD) (A : Choice)
    (hA : ∀ z ∈ A, (candidate x.r.N.D z.1 z.2).isSome) (certs : List (Option VE.Tableau.Certificate))
    (hc : VE.NormDefaults.Wire.conflictFreeCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) certs = true)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnvSD x.r.N) [])
    (hφ : φ.WellFormed (sharedEnvSD x.r.N) []) (cert : VE.Tableau.Certificate)
    (ha : supCertificateCheckSD x.r.N A Γ φ cert = true) :
    ∀ c, Compatible x.r.N.D c → (∀ z ∈ A, z ∈ c) →
      VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N c) (choiceX x.r.N c) ∧
        VE.NormDefaults.EntailsX.{u} (choiceU x.r.N c) (choiceX x.r.N c) ((choiceDoc x.r.N.D c).2 ++ Γ) φ

theorem readings_wire_sd_model_sound (x : SupReplaySD) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnvSD x.r.N) [])
    (hφ : φ.WellFormed (sharedEnvSD x.r.N) []) (M : VE.FiniteModel Entity)
    (valid : M.Valid (VE.Norms.envAt (supU x.r.N).D 0)) (F : VE.NormDefaults.FiniteFill (supU x.r.N) Entity)
    (hm : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      ((sup x.r.N.D).2 ++ Γ) φ).1 = true)
    (hn : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      ((sup x.r.N.D).2 ++ Γ) φ).2 = false)
    (hl : localFree (supU x.r.N) M F = true) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ z ∈ A, z ∈ c) ∧
      Encodes x.r.N.D c (VE.NormDefaults.withFill (supU x.r.N) M.asStructure (VE.NormDefaults.finFill M F)) ∧
      CounterX (choiceU x.r.N c) (choiceX x.r.N c) ((choiceDoc x.r.N.D c).2 ++ Γ) φ

theorem readings_wire_sd_consistent_sound (x : SupReplaySD) (A : Choice) (M : VE.FiniteModel Entity)
    (valid : M.Valid (VE.Norms.envAt (supU x.r.N).D 0)) (F : VE.NormDefaults.FiniteFill (supU x.r.N) Entity)
    (hm : (VE.NormDefaults.modelCheckX (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F
      (sup x.r.N.D).2 .bottom).1 = true)
    (hl : localFree (supU x.r.N) M F = true) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ z ∈ A, z ∈ c) ∧
      ConsistentX (choiceU x.r.N c) (choiceX x.r.N c) (choiceDoc x.r.N.D c).2

theorem readings_wire_sd_witness_sound (x : SupReplaySD) (A : Choice)
    (t : String × List String × VE.Formula) (ht : t ∈ targets (fill (supU x.r.N))) (M : VE.FiniteModel Entity)
    (valid : M.Valid (VE.Norms.envAt (supU x.r.N).D 0)) (hbg : VE.Norms.backgroundValid (supU x.r.N).D M = true)
    (F : VE.NormDefaults.FiniteFill (supU x.r.N) Entity)
    (hf : VE.NormDefaults.fillValid (supU x.r.N) M F = true)
    (hX : VE.NormDefaults.Wire.extraValid (supU x.r.N) (slotUnder x.r.N.D A ++ supX x.r.N) M F = true)
    (vs : List Entity)
    (typed : VE.TupleTyped (VE.NormDefaults.withFill (supU x.r.N) M.asStructure (VE.NormDefaults.finFill M F)) t.2.1 vs)
    (hw : t.2.2.eval (M.withFill F) (VE.Norms.tupleVal vs) = true) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ z ∈ A, z ∈ c) ∧
      Encodes x.r.N.D c (VE.NormDefaults.withFill (supU x.r.N) M.asStructure (VE.NormDefaults.finFill M F)) ∧
      ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU x.r.N c) (choiceX x.r.N c)
end VE.Readings.Wire
```

Namespaces above are as read at `90807e7f7`; an `open` the elaborator asks for is the builder's, and it changes no statement.

What the proofs need, as guidance: `supLabel_pull` and `supLabel_other` are the per-premise halves of `exc_pullF` and
`coh_pullF` (`SoftSup.lean`), whose list forms are `supX_pull`. Take the pieces from the merged lemmas (`F3`, `F4`, `dead_extra`,
`pattern_off`, `quiet_holds`) and do not edit `SoftSup.lean` unless sc-10b has merged and a lemma must be exposed.
`readings_wire_sd_conflict_sound` is `conflictFreeCheckX_sound` then `sd_superpose_conflict_free`.
`readings_wire_sd_witness_sound` needs the downward half of `sd_superpose_conflict_free` at the named base, since the
answer names the encoded choice. The superposed kinds can reuse the layered source: a `LayeredU` with `U = supU N` and `X =
slotUnder N.D A ++ supX N`, whose `conflictFreeX`, `witnessConflictX` and `xEvidenceOf` already read as 14.3 states. That is the
builder's choice, not frozen.

### 14.9 Fixtures

The per-choice route on the same input is the oracle for every *derived* verdict. Each iff has a fixture per direction.

| # | Case | Expected | Pins |
| --- | --- | --- | --- |
| W-1 (DRI item 2's condition) | `NSD4`, `readings-elaborate` | `soft[].label` is exactly `["soft:exception:must-x:sufficient:0", "soft:coherence:must-x,need-not-x"]` (S-7, *pinned* as choice labels) and `soft_premises` of `(rs1,1)` is the same list, byte-identical to the enumerated row; no label contains `rd-2-must-x`, while S-2's labels do (*pinned*). `NSD4`, `readings-verdicts`, `--under rs1:1`: CONFLICT (13.5, DRI item 3), on both routes, and no English line contains `rd-2-` or `rd_2_` (OPEN-SC11-2) | `labelImage`, 14.4 |
| W-1a (the same, on an answer that lists them) | `NSD4a`, `--under rs1:1`: conflict; then the query `∀ a. c a → ¬ x_required a` | CONFLICT-FREE, `conditional_on: ["soft:coherence:must-x,need-not-x"]` on both routes (F-SD4's line). ALL on both routes, `conditional_on` as a set is exactly `{soft:exception:must-x:sufficient:0, soft:coherence:must-x,need-not-x}`; never `rd-2-must-x` (*derived*) | `sdShown`, 14.6 item 4 |
| W-2 | `labelImage NSD4 (rs1,0)`; `labelImage NSD4 (rs1,1)` | `[]`; `[("soft:exception:must-x:sufficient:0", "soft:exception:rd-2-must-x:sufficient:0"), ("soft:coherence:must-x,need-not-x", "soft:coherence:need-not-x,rd-2-must-x")]` (the pair's order flips; S-2, S-7 *pinned*) | `labelImage_fst`, `labelImage_snd_mem` |
| W-2′ | `labelImage` on `NC9`, `NSD2` | three `…:sufficient:i` pairs; one `…:necessary:0` pair, its `supX` premise bit-free (S-4′ *pinned*) | exception labels, both roles |
| W-3 | `NSDd`: one set of two defaults on one act with opposite signs, no fixed unit | the sup pair `(rd-1-…, rd-2-…)` is a superposed label, `labelImage` is `[]` on both choices, `soft[].label` `null`; `sdShown` of it is `[]`; the premise holds at each encoded base (*derived*) | `supLabel_other`; dead in every choice |
| W-4 | `NSDm`: one set of two defaults `x` under different guards, a fixed default `need-not-x` | two superposed labels, one choice label: `soft[]` has `soft:coherence:need-not-x,x` twice; `sdShown` under `[]` lists it once (*derived*) | `labelImage_functional`, not injective across choices |
| W-5 | `supLabel_pull`: `NSD4`, `(rs1,1)`, `c = {a}`, `soft__excepted__rd_2_must_x = ∅`, and the same table `{a}` | the sufficient premise false on both sides; true on both sides (as 13.5 *derived*) | each direction |
| W-5′ | `supLabel_other`, `hsl` needed: `NSD2`, bits naming `(rs1,0)`, `soft__excepted__rd_2_no_deception = {(a,u)}` | the slot is broken and the premise is false (13.5, *derived*) | no weaker hypothesis |
| W-6 | `routeSD`: `NSD1`, `NSD4`, `NSD4a`, `NSD4c`, `NC9`, `NSD2`, `NSDq` (`facts` all true, *pinned*) | superposed | `routeSD_superposed_iff`, → |
| W-6′ | `routeSD`: a document failing each conjunct alone: non-uniform precedence under a rule (`superposable` false); `WellFormedU (supU N)` false with `superposable` true; a choice at position 65 or later whose `sdChoiceText` is `some`; `F-SD9` with 11 sets (2048 choices); `w2`; `pending` | each of the first four enumerated, with today's finding and bytes; `w2`; `pending` | ← , one row per conjunct |
| W-7 | `F-SD1`: elaborate, conflict, query, `--under rs1:0`, `--under rs1:1`, each answered as F-SD1.verdicts | route superposed; CONFLICT-FREE; SOME; ALL; NONE, with choice 1's countermodel `excepted = {(a,u)}` and the filling no; `decided_units: ["u1"]` then `[]` under each `--under` (*derived*) | RD-6b review's "NOT ALL" |
| W-8 | certificates: 13.5's `sd_superpose_all` and `_countermodel` rows through the wire, and a certificate whose binding drops a `supX` premise or adds an assertion (F-SD11's form) | accepted; refused with diagnostic 11 (*derived*) | `bindCertX`, D14 |
| W-9 | the `Fill_T` premise on `NSDq`: `fill[]` one entry, after `soft[]` in the premise list; the same request with `fill` applied before `soft`, or `supX` before the slot | a certificate generated for the wrong order fails `supCertificateCheckSD` (order is byte-level, though `BaseAdmissibleX` is unchanged by 13.4 item 2) | 14.3's order |
| W-10 | a query over `sharedEnvSD`: `∀ agent ∀ user. unsaid__avoid_required agent user → avoid_required agent user` on `NSD1` (DRI item 1's guard); `soft__excepted__must_x` in a query on `NSD4` | decoded and answered; refused by the decoder | `decodeShared` over `sharedEnvSD N` |
| W-11 | a model with an `unsaid__` table in `relations`; a filling that fails `Fill_T`; a model with `localFree` false (13.5's without-`hl` case) | refused or UNKNOWN, never `model` (F-SD8) | `hl`, F-SD8 |
| W-12 | 7 sets each as `rs1` (F-SD9) | superposed, `choices_checked: 128`, `choice_count: "over 64"`, decided verdicts (F-ND3's analogue); `decided_units: []` (1.12); budget zero stays UNKNOWN (*derived*) | past 64 |
| W-13 (large, well formed) | `NSDbig`: 10 sets of 2, each a default with a sufficient condition, one fixed unit (1024 choices at the limit); the same with 11 sets; the 10-set document with enough guard nodes that `sdCheckWork > maxSdCheckWork` | superposed, a conflict answer in one proof, `choices_checked: 1024`; enumerated, "over 64"; enumerated, "over 64" | 14.11 |
| W-14 (read once) | `readings-verdicts` on `NSD4a` with conflict, certificate and model evidence, under `VE_READINGS_STAGE_TIMES=1` | one `admitSDOf` and one route check per case, however many pieces | 14.11 |

Seeded bugs the build plants (each must fail a fixture): `labelImage` returning the superposed label as its first component
(W-1, W-2); `sdShown` over all choices and not those taking `A` (W-7 under `--under`); `routeSD` without `sdChecked` (W-6′); the
`nd` behaviour off (W-7); `Fill_T` dropped from the list (W-9); `null` shown as an empty string (W-3).

### 14.10 Python relay-binding rows

Python checks the schema and binds what the request fixes (R8); it recomputes no label, route or status. The rows go in
`docs/spec/rd-9-relay-binding.md` with their fields in `tests/test_relay_binding_inventory.py` when the build adds them (synthesis
edit 3), through `_bind_completion_superposed` and `_check_sup_answer`. If `sa-binder` has merged, they are rows of its one
binder and no new binder is written (edit 2). A failed check is `CheckerUnavailable`.

| Field | Request binding or Lean-derived value | Regression (names the build uses) |
| --- | --- | --- |
| `route`, `finding`, `choices_checked` (soft row) | `superposed` with `finding` null and `choices_checked` an integer, or the enumerated row's existing binding | `test_sc11_soft_row_route_fields_are_bound` |
| `soft[].label` | null, or a `soft_label` over `soft_rules` of the request's own bodies: author names, never the `names` map's qualified names; each `soft_premises` label of a reading occurs here | `test_sc11_a_qualified_soft_label_is_unavailable` |
| `soft[].ast`, `filled_premises[]`, `conflict_targets[].ast` | Lean-derived, typed by the generated schema | `test_route_row_schemas` |
| `fill[].label` | `unsaid:pair:<r>,<m>` of a declared pair, equal as a set to `fill_premises`' labels, each once (RD-6b's row) | `test_sc11_fill_labels_are_bound` |
| `base_environment`, `unsaid[].name` | as `_FilledChoiceDocument`'s row: the request's vocabulary plus the regenerated names of `unsaid__p` for its unspecified `p` and the elaborated decisions | `test_sc11_soft_row_environment_is_bound` |
| `conflict_targets[].target`, `.sorts` | the regulated predicates and declared pairs, once, with their sorts (the `conflict_targets` row) | `test_sc11_soft_row_targets_are_bound` |
| `result.conditional_on`, `proofs[].conditional_on`, `reading_premises_used`, `scopes[].used`, `english[].label` | closed list: a slot label of the row, a `fill` label, a `soft[].label` not null, a restriction of the document; each once per list; a qualified label is `CheckerUnavailable` | `test_sc11_answer_labels_are_the_rows_labels` |
| `decided_units` | present; each a unit of the document, once, in document order (`binding.py`'s row) | `test_sc11_decided_units_are_bound` |
| `result.choices`, `proofs`, `countermodels` | the compatible choices taking `A`, in canonical order, at most 64 (`_check_sup_answer`) | `test_readings_sup_verdicts` rows |
| `model`, `filling` (shown) | equal to the scope's shown model; `gaps` bound by `_bound_gaps` | `test_sc11_shown_model_and_filling_are_bound` |

### 14.11 Evaluation limits

Each value is computed once per case, and its size is charged before it is used.

| Value | Read | Charged against |
| --- | --- | --- |
| the compatible choices (`search`) | once per case; `choices` is read from the same cut | `maxChoiceChecks` 1024 (past it: enumerated) |
| `sdChoiceText` per choice | at most 64 choices: admission's result, not run again (`sdCheck_of_admitted`); past 64: once, in the route | `sdCheckWork N ≤ maxSdCheckWork`, checked before the first `sdChoiceText` (over: enumerated, no choice read) |
| `sup N.D`, `supU N`, `fill (supU N)`, `softXL N (sup N.D).1`, `premisesX`, `targets` | once per case; every piece of a `readings-verdicts` case runs on that value (as `conflictReplay` does), never re-admitting per piece as `x.run` does on the norms chain | 256 rules plus unspecified predicates; 10,000 AST nodes (section 9) on `supU N` |
| `labelImage N c`, per choice taking `A` | once per scope, and only when a piece was accepted | within `sdCheckWork` |
| `usedLabels` | per accepted piece, one replay per label of slot, `supX` and `Fill_T` | the labels within `sdCheckWork`; each replay is the piece's own certificate, within `max_steps` |
| a request's JSON members (evidence, model, certificates) | decoded once; the input bytes charged by the existing admission memo | the existing limits |

`maxSdCheckWork` = 4,194,304 is 1024 choices × 4096 premises and rule nodes. It is this spec's value from that arithmetic,
not a measurement (OPEN-SC11-7). W-13 is the large well-formed request; the build records its Lean CPU, and R4's absolute
budgets are the bar. Exceeding the limit is the enumerated row, not an error.

### 14.12 Existing text and tests that sc-11b changes

This section supersedes them from sc-11b's merge. This item edits no earlier section. 8.3's F-SD4 sentence stays with row
`sc-fsd4-text`, DRI item 3.

| Where | Today | After |
| --- | --- | --- |
| 1.1, D3, D11 (plan), 6.8's `routeOf` note | the soft chain's route is the enumerated row | the route is `routeSD`, 14.2 |
| 8.3 F-SD1 (elaborate) | enumerated, `ReadingsNotSuperposable: rs1` | the soft row |
| 8.3 F-SD1.verdicts, F-SD4 | RD-3's answer | same verdicts and labels (14.6), the superposed shape when `budget` is sent |
| 8.3 F-SD2 (K18), elaborate and superposed kinds | enumerated; refusal | the soft row with `soft` and `fill` empty, not K1's S2a row; `readings-validate`, `-separate`, `-choice`, budget-free `-verdicts` unchanged |
| 8.3 F-SD9 | enumerated, query UNKNOWN | W-12 |
| 8.1 F-SD2 route | `routeOf` values | unchanged (`routeOf` not edited) |
| `sdRefusal`'s docstring, `SoftWire.lean`'s and `Run.lean`'s "the route is the enumerated one" | | updated with the switch |
| `tests/test_readings_sd_lean.py` (:134-151, :173-195, :316, :579), `tests/test_readings_sd_document.py` (:71-86), `tests/test_readings_sd_ce4.py` (:215-238), `tests/test_rd9_chain_relay.py` (:49) | enumerated | as above; none deleted, each asserting the new row or the budget-free answer |

Each document the A/B comparison sees change is a DELTA row of the build (OPEN-SC11-4 for the kinds no standing ruling
covers). `CE4`'s sets are read by `routeSD` like any other; whether they move is measured, not assumed here.

### 14.13 Build items and the sc-10b dependency

Two items, on the ~600-line rule; this is the plan's estimate of 5–6 h, not a measurement.

- **sc-11 (Lean, no byte moves):** `SoftSupLabels.lean`, `SoftSupWire.lean` with every statement of 14.8, the soft runners
  (`readings-conflict`, `-certificate`, `-model`, the soft row and the verdict scopes) reached only from `SoftSupWireExamples.lean`,
  W-2 to W-6′ and W-13's route values as `#guard`s. The dispatch stays as today.
- **sc-11b (the switch):** `runS2ND`, `runSDKind` and `runElaborateSD` read `routeSD`; the row in the response schema; Python
  (14.5), relay rows (14.10); the changes of 14.12; the differential (14.6); the wire fixtures; DELTA and A/B. **The seam is
  that commit:** before it no answer changes.

**sc-10b must be on main before sc-11 builds** for `readings_wire_sd_conflict_sound`, `readings_wire_sd_all_sound`,
`readings_wire_sd_model_sound`, `readings_wire_sd_consistent_sound`, `readings_wire_sd_witness_sound`, which read
`sd_superpose_conflict_free`, `sd_superpose_all`, `sd_superpose_countermodel` as 13.3 states them. The rest of 14.8 needs only what
is merged (`fillPremisesSD_pull`, `supX_pull` and their lemmas), and it could start first, but it is one item with the rest. sc-11 and
sc-10b both read `SoftSup.lean`, and only sc-10b writes it, so run sc-10b first.

### 14.14 Not claimed

- No theorem that the two routes' `conditional_on` agree, or their verdicts: 14.6 checks them on 200 seeds, and
  `readings_wire_sd_*` show each superposed answer true of the per-choice semantics, which is what the enumerated route folds.
- No completeness: a superposed UNKNOWN says nothing, and no claim that an answer is found within budget. No speed claim.
- No companions, no readings with their own vocabulary (RD-4a's refusal stays, D11), nothing on the rights chain under the completion.
- `routeSD` says nothing about a document in a product (`readings_components`): those cases keep their own route.
- No new English wording (D12).

### 14.15 OPEN (for the DRI)

- **OPEN-SC11-1 (scope of "no qualified names on the wire").** Item 2 is read as about labels (14.4). `names`, `units`,
  `vocabulary`, `generated_predicates`, ASTs and a shown model's `relations` keep qualified names, as S2a's and RD-6b's rows do; a
  generator needs them, and English prints none. The stricter reading, a shown model pulled into the choice's vocabulary, would
  need a wire statement on the pulled model and more build. This spec takes the narrow reading.
- **OPEN-SC11-2 (where item 2's condition is checked).** The condition says a superposed answer on `NSD4` under the default
  reading lists exactly S-7's labels. `NSD4` under the default reading is CONFLICT (13.5, DRI item 3), and a CONFLICT answer has no
  `conditional_on`. So W-1 checks `NSD4` on `soft[].label` and `soft_premises`, and W-1a checks the verdict's `conditional_on` on
  `NSD4a`, the fixture with the filling the merged F-SD4 test uses. Confirm this meets the condition.
- **OPEN-SC11-3 (the enumerated row's cause).** Kept byte-identical: `the unspecified completion` (D3), though a document may now
  fail for a named cause such as non-uniform precedence. RD-6b's `ndNotSuperposable` names the cause; adopting its analogue changes
  today's bytes on documents that stay enumerated, and needs a ruling.
- **OPEN-SC11-4 (DELTA rows no standing ruling covers).** A verdict change other than R5 and any loss of information are never
  standing (DRI-RULINGS). Three kinds arrive at sc-11b: (a) past 64 choices, UNKNOWN becomes a decided verdict (W-12; RD-6b's F-ND3 had this);
  (b) a query naming one reading's decision predicate, typed today over the first choice's vocabulary, is refused (W-10; follows item 1);
  (c) soft documents on the constitution's path may move routes at the merge, so `CE4` and SC-9's recorded output change wording (not
  verdicts, by 14.6, at at most 64 choices), and the plan calls SC-11 off that path. The batch text has no flag, and this spec adds none. The
  DRI signs these rows or rules before sc-11b's task file is written. No row is signed here.
- **OPEN-SC11-5 (a differential seed that differs on `conditional_on`).** Both lists are sound and neither is a theorem's (14.6). Default:
  the test fails and the build stops on that seed for the DRI; no seed is dropped. The alternative is comparing `conditional_on` by inclusion
  in the union of the choice labels.
- **OPEN-SC11-6 (`decided_units` on the superposed answer).** The plan does not name it, and RD-6b's answer has none. Default: keep it on
  the soft chain (14.3), because dropping it would be a loss of information and would change SC-9's measure. It costs `supOpen`'s
  extra premises scopes while the global conflict status is open.
- **OPEN-SC11-7 (`maxSdCheckWork`).** 4,194,304 is arithmetic, not a measurement (14.11). Confirm or set it after W-13's CPU figure.

### 14.16 Review checklist (SC-11's statement review)

1. Each statement of 14.8 is true under its hypotheses, not only well typed, and each 14.7 paraphrase has one reading. In particular
   `supLabel_other` (the slot is needed: W-5′) and `labelImage_functional` (a qualified name fixes its candidate).
2. The route condition is plan 6's, D3's and DRI ruling 5's; `routeND` and `routeOf` are untouched; the fall-through past 64 is conservative.
3. 14.3's order agrees with 13.3's statements, `premisesX` and D14; the queries are typed as DRI item 1 settled.
4. Item 2's direction and condition hold: no label field carries a qualified name, and W-1 and W-1a pin it.
5. 14.6 says what identical means, labels included, and what is not compared.
6. The fixtures of 14.9 have a row per direction, each with something that would fail it.
7. 14.10's rows only bind (R8); no row recomputes a Lean value.
8. 14.11 charges each value once, with a stated limit and a large well-formed fixture.
9. D13: no general definition with `X` moves; the split of 14.13 builds within the size rule.
10. 14.15 decides nothing that the plan and rulings leave open.
