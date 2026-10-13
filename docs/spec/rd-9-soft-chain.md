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
  as decoded; no `F_p` unit on the soft chain, since `F_p` is a rule of each filled tree).
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
| SC-10 | `Readings/SoftSup.lean` (new; sketch) | 6.11 |

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

It elaborates; it is not reviewed for PASS here (plan 4.11).

## 7. What is not claimed

- No completeness of separation: an unseparated pair is equal meaning or a search miss.
- No theorem relates `separatesS` on a norms-shaped document to RD-1's `separates (fillDoc N)` with `fillHolds` (Q3).
- No minimality of a pair's or a result's gaps. If SC-A does not prove `coneEval_sound` and `coneEval_definite`, the
  selection itself is not claimed sound either, and the answer says nothing more than today's verdict lines do.
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
| SC-10's `sd_superpose_conflict_free` | reviewed with SC-10 | reviewed with SC-10 |

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
