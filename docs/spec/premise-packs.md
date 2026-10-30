# PK-1: premise packs (statement spec, draft 1)

> Item pk-1s (feature feed rank 4, 2026-10-18). This is PK-1's own statement review text (SYNTHESIS 2.1, 3 and
> 4.1 item 2, with DRI decisions DF4, DF5, DF7 and JT-R2). The build is item pk-1. Owner: the RD-9 composition owner
> of `lean/VE/NormDefaults/Layered.lean`.
>
> **The exact Lean text is the stub** `docs/spec/premise-packs/SpecStubs_pk1.lean` (cited `stub:<line>`). It
> imports `main` unchanged and type-checks from `lean/` with
> `PATH=~/.elan/bin:$PATH lake env lean ../docs/spec/premise-packs/SpecStubs_pk1.lean`. Every definition there is a
> real body, every fixture is a `#guard`, and 13 theorems are left `sorry` for the build to prove (section 6).
> The stub is the only copy of each statement, so this document gives one plain-English sentence for each and does
> not repeat the Lean. Citations of `main` are at `802b8ff9b`.

## 1. What PK-1 is

Several plans add closed base premises to the layered norm-defaults route: weighing, attitudes, scales and events.
Today that route carries soft's premises and, on the rights route, the limitation premises, as one list `labelled`
with a count `rightsCount` (`Layered.lean:64–65`). Its `X` is that list's formulas (`:72`).

PK-1 replaces the list and the count with a list of **packs**. A pack is what one provider regenerates from the
decoded request. `X` is the packs' premises in one fixed order. For today's two routes, every answer, array and
diagnostic stays byte-identical. A plain norm-defaults document has the empty pack list (JT-R2).

## 2. Definitions and theorems

### 2.1 The data

- `PackKind` (stub:24). A pack either adds fresh generated names (`vocabulary`) or only constrains names that
  already exist (`constraint`).
- `RequestPath` (stub:30). A path is the object keys and array indices, as strings, from the request root to where
  a label or name comes from.
- `Pack` (stub:33). A pack has:
  - an id, a kind and its generated predicates with their argument sorts (`decls`);
  - its generated constants with their sort (`consts`; events' named dates `date__…`);
  - its labelled closed premises, in the provider's order;
  - an origin for each label and generated name.

  A pack never adds a sort. Events' sorts are declared by the author (events.md:132–133).

### 2.2 The order

- `packOrder` (stub:42) is soft, rights, weighing, attitudes, scales, events. It is the one order of `X`; soft
  before rights is today's order (`Layered.lean:121`).
- Act specialisation has no row until AP-5b is reviewed (C5).
- Defeasible and judgment terms add no row: defeasible appends `Dflt_T` after `X` in its own kinds (DF4, DF5), and
  judgment criteria never enter `X`.

### 2.3 Reserved prefixes

- `reservedPrefixes` (stub:45) lists each reserved prefix with its owner:
  - `soft__` (`SoftNorms/Soften.lean:538`);
  - `rights__` (`Rights/Correlate.lean:230`);
  - `unsaid__` (`NormDefaults/Tree.lean:36`).
- Each provider adds its own row in its batch (`attitudes__` in AT-2, `date__` in ET-4). The stub's
  `fixturePrefixes` (stub:400) stand in for those rows.
- `reserved` (stub:49) says whether an author name begins with any reserved prefix. Every provider's decoder
  refuses such author names with today's text, `InvalidInput: reserved name <n>` (`NormDefaults/Wire.lean:97`).
- `ownPrefix` (stub:54–57) says whether a generated name begins with a prefix the pack's own provider owns.
- A `#guard` (stub:482) checks that no reserved prefix begins with another.

### 2.4 Assembly

- `ordered` (stub:62) lists the packs in `packOrder`.
- `labelledX`, `X` and `names` (stub:64–66) give the packs' labelled premises, their formulas and their generated
  names, in that order.
- `packPremises qs i` (stub:69) is pack `i`'s labelled premises, or `[]` when it is absent. Attitudes asks for this
  accessor, and today's `"soft"` and `"rights"` arrays use it.
- `extendEnv` (stub:73) adds the generated predicates and constants to an environment and changes nothing else.
- `fullEnv U` (stub:80) is the complete environment of the filled tree, layer symbols and `unsaid__` names
  included. Freshness is checked against it, not against `envAt (fill U) 0`. Otherwise a generated name could
  equal a hidden layer symbol, the case `Rights/Wire.lean:552` (`genFresh`) guards for rights.
- `envX U qs` (stub:83) is `envAt (fill U) 0` extended by every pack's names.
- `assembleIn pre E used ps` (stub:94) runs its checks in this order (the fault order) and returns the ordered
  packs. The first failing check gives the text:
  1. An unknown pack id, the first in the given order: `InvalidInput: unknown premise pack <id>`.
  2. A repeated id, the first in `packOrder`: `InvalidInput: premise pack <id> is given twice`.
  3. A repeated label, the first in `X` order: `InvalidInput: premise label <l> of pack <id> is used twice`.
  4. A generated name that `E` declares, as a predicate or a constant:
     `InvalidInput: generated name <n> of pack <id> is already declared`.
  5. A generated name that an earlier name of any pack already took:
     `InvalidInput: generated name <n> of pack <id> is declared twice`.
  6. A generated name without its own pack's prefix:
     `InvalidInput: a generated name of pack <id> lacks its reserved prefix`.
  7. More than 256 names in all, counting `used` (the count `checkAuthorN` charged, `NormDefaults/Wire.lean:100–101`):
     `ResourceLimit: vocabulary size`, today's text.
- `assemble U used ps` (stub:114) is `assembleIn reservedPrefixes (fullEnv U) used ps`.

**Change from SYNTHESIS 2.1.** SYNTHESIS sketched `assemble (E) (ps)` returning an environment and a labelled `X`.
Here `assemble` takes the source `U`, so that freshness reads the complete environment, and `used`, so that the
existing vocabulary limit covers pack names. It returns the ordered packs; the environment (`envX`) and `X` are
functions of them. The statement review fixes names and bodies (SYNTHESIS 2, first paragraph).

### 2.5 Theorems about assembly

- `extendEnv_nil` and `envX_nil` (stub:119–121, proved by `rfl`). With no generated names the environment is
  exactly today's, so every legacy proof over `envAt (fill U) 0` stands.
- `assemble_order` (stub:124). When assembly succeeds, the result is the given packs reordered, and their ids
  appear in `packOrder`'s order; so `X` is the packs' premises in `packOrder`, each pack in its own order.
- `assemble_fresh` (stub:128). When assembly succeeds:
  - labels are pairwise distinct, and so are generated names;
  - every generated name is undeclared in the complete environment and has its pack's own prefix;
  - the vocabulary stays within 256.
- `assemble_wellFormed` (stub:135). If each pack's premises are typed over the base environment and the pack's own
  names, then all of `X` is typed over `envX`. A pack's premises may not use another pack's generated names.
- `assemble_nil` (stub:140, proved). The empty pack list assembles to the empty list (JT-R2). `X [] = []` and
  `envX U [] = envAt (fill U) 0`.

### 2.6 The legacy packs

- `softPack U D` (stub:147) is soft's `Exc_T ++ Coh_T` on `fill U` (`Layered.lean:51–53`) as a `constraint` pack
  with no names. Its names are declared inside `U` by `soften`.
- `rightsPack R` (stub:150) is `limPremisesLabelled R` (`Rights/Correlate.lean:123`, used at `Layered.lean:120`),
  likewise. Its names are declared inside `U` by `correlate`.
- Both have `origins = []`. Today's relays bind the `"soft"` and `"rights"` arrays as `docs/spec/rd-9-relay-binding.md`
  says, and obligation 5 (section 3) binds new providers only.
- `legacyIds` (stub:154) are the id lists whose outputs and texts are today's: `[]`, `[soft]`, `[soft, rights]`.
- `softLabelledU_labels_nodup` and `legacy_labels_nodup_of_actKeys` (stub:157, 163). Today's labels are already distinct.
  Each assumes the well-formedness its decoder's source carries: `WellFormedSoft D` for soft (`src.wf`,
  `SoftNorms/Wire.lean:90`) and `WellFormedRights R` for rights (`src.wf`, `Rights/Wire.lean:270`). pk-1 proves them
  from checks the decoders already run:
  - soft labels: node names are distinct (`SoftNorms/Once.lean:115`), `soften` keeps them, and rule names are
    `[a-z][a-z0-9-]*` (`Norms/Tree.lean:264`), so they contain no `:` and no `,`;
  - rights labels: the keys of `condKeys` are distinct because `checkRights` refuses a repeated limitation name
    (`Rights/Correlate.lean:365`) and a repeated condition name (`:403`), and `limActs` is deduplicated
    (`Rights/Tree.lean:230`). Sorting does not make them distinct;
  - soft labels begin with `soft:` and rights labels with `rights:`.

  `legacy_labels_nodup_of_actKeys` also assumes `(hk : ∀ k ∈ VE.Rights.condKeys R, ':' ∉ k.2.1.toList)`, what the route's
  decoder enforces. It replaces the false `legacy_labels_nodup`, whose counterexample `cx`
  (`lean/VE/NormDefaults/PacksLegacyExamples.lean`) has `:` in a predicate name (DRI decision 2026-10-27, item 3:
  `reviews/dri-decisions-20261027-featureplan-gates.md`).

  `WellFormedSoft (correlate R)` is not enough for rights: it never sees limitation or condition names. Fixture F1
  (stub:497–512) is a rights document repeating a limitation, and one repeating a condition. On both,
  `WellFormedSoft (correlate R)` and `WellFormedU` hold and the labels repeat, while `WellFormedRights` refuses them
  (`DuplicateDeclaration: limitation l29`, `DuplicateDeclaration: condition determined_by_law`). The fixture also
  evaluates both statements on five well-formed rights documents from `Rights/Examples.lean`.
- `assemble_legacy_soft` and `assemble_legacy_rights` (stub:168, 173). Assembly accepts today's soft and rights
  sources unchanged, in either listed order, and returns them soft first. So the repeated-label check refuses no
  document today's routes accept.
- `X_legacy` (stub:181, proved). On a two-pack list, `X` is the concatenated premises' formulas, today's
  `L.labelled.map (·.2)`.
- `legacy_take` and `legacy_drop` (stub:186–191, proved). Today's expressions `take (length − rightsCount)` and
  `drop (length − rightsCount)` are exactly the soft pack's and the rights pack's premises. They are used at
  `Layered.lean:150`, `:152` and `:289`, and at `LayeredAdmission.lean:105`.
- `packPremises_legacy` and `packPremises_absent` (stub:195, 200, proved). On a legacy rights list, `packPremises`
  returns soft's and rights' lists, and an absent pack gives `[]`.
- `X_soft_first` (stub:207). `X` is soft's premises followed by the other packs'. Defeasible's
  `DefaultsView.hX : L.X = softLabelled… ++ R` reads this (DF5).

### 2.7 Elaborate entries

- `elaborateArrays` (stub:227). In pk-1 it writes the `"soft"` and `"rights"` arrays exactly as today
  (`Layered.lean:150–153`), and nothing else, whatever the pack list.
- `elaborateArrays_keys` (stub:232, proved by `rfl`). Its keys are `soft` and `rights` for every pack list. The
  response shape `layered_elaborate` is closed (`ResponseShape/Schemas/NormDefaults.lean:124–135`), and
  `layeredCase_fits` quantifies over every `LayeredU` (`ResponseShape/Encoders/NormDefaults.lean:52`), including
  pack lists no decoder builds yet. So the encoder theorem goes through unchanged only if the keys do not depend on
  the packs. Fixture A9′ (stub:484–495) reads the closed keys from the shape itself: it has the keys pk-1 writes,
  and no further pack's id.
- `elaborateArrays_legacy` (stub:240). On a legacy list the two arrays are today's expressions over `labelled` and
  `rightsCount`.
- **Not in pk-1:** `packEntry` and `furtherEntries` (stub:217, 236). A further pack's entry is its id with
  `{"premises": [{label, ast, origin}], "names": [{name, arguments | sort, origin}]}`, one per further pack in
  `packOrder`; a legacy list has none. They land with the first provider (AT-2), in the same change as that
  provider's optional key in `layered_elaborate`, the generated schema and the relay.
- No other pk-1 output depends on the packs beyond today's shapes: the status, conflict and report rows read `X`
  only through `extraValid`, and `packFault` and `dispatch` only change error texts.

### 2.8 Diagnostics

- `firstFailing` (stub:250) finds the first premise of `X`, in `X` order, that fails, with its pack and label.
- `packFault` (stub:255) is the text `filledX` throws when `X` fails.
  - On a legacy list it is today's text, `InvalidModel(<pack>): the model violates a background premise`.
  - Otherwise it is that text followed by `: <label>`.
  - Both use `VE.Route.Wire.invalidModel` (`Route/Wire.lean:301`).
- `firstFailing_some` (stub:262). When `X` fails, a first failing premise exists, so `packFault`'s fallback text is
  unreachable.
- `packFault_legacy_rights` and `packFault_legacy_soft` (stub:266, 274). On today's lists the text is exactly
  today's (`Layered.lean:289–290`): `rights` when soft's part holds, otherwise `soft`.
- **Providers align their plans:**
  - attitudes.md:911–914 put the label inside the parentheses;
  - events.md:520–521 already has the pack inside, but carries the label as a separate detail.
- The `unsaid` text (`Layered.lean:291`) and the situation texts (`:257`, `:262–263`) do not change.

### 2.9 What PK-1 guarantees about witnesses (DF7)

- `filledX_whole` (stub:299, proved on `main`'s `FilledX`). Every filled situation the layered route accepts, as a
  countermodel or an admissible witness (a CONFLICT witness, a status filling, a report witness), satisfies the
  **whole** assembled `X`. This is `filledX`'s `extraValid L.U L.X` (`Layered.lean:287`).
- The one exception is defeasible's **collision witness**. It is checked against `xWithout X (coherenceLabels D)`
  (stub:281, 285): `X` without the soft pack's coherence premises, because a collision is exactly a base where a
  coherence premise is false.
  - `xWithout_nil` and `xWithout_sub` (stub:288, 292, proved) say that dropping nothing gives `X`, and that what
    remains is part of `X`.
  - DE7 keeps its situation.
- A calendar witness also needs ET-2's completion-preservation theorem (SYNTHESIS 2.8).
- There is no global conservativity claim. A chain lemma, if stated, is applied only where every pack's expansion
  step (obligation 1) is proved. Weighing never meets that, and events meets it only with ET-2's theorem (C3).

### 2.10 The kind table

- `KindRow` and `dispatch` (stub:325, 331). A row names a kind, the pack it needs (if any) and its runner. A kind
  whose pack is absent is refused with `UnsupportedProfile: case kind <k> needs the <pack> premise pack`. A kind
  with no row returns `none`, so `runLayered`'s existing refusal stands (`Layered.lean:444`).
- `dispatch_legacy` (stub:352). For today's four kinds, dispatch through the table answers exactly as
  `layeredCase` does today (`Layered.lean:410–437`). In the build today's `layeredCase` is kept, body unchanged, as
  `legacyCase`; the four rows call it, and `layeredCase` becomes `dispatch legacyRows` over the source's pack ids.
- `KindRow` is generic in the source type, so that it and `dispatch` sit below `Layered.lean` (section 5).
- The kind table lands in **pk-1b** (section 5), before the first provider row.

| Kind | Pack | Owner | Lands in |
|---|---|---|---|
| `norm-defaults-elaborate`, `-conflict`, `-status`, `-report` | none | RD-9 (today) | pk-1b (rows only; the bodies stay as `legacyCase`) |
| `admission`, `norm-defaults-certificate` | soft | RD-9 SC-6 (today) | stays in `softCase`, dispatched first (`LayeredAdmission.lean`, `Run.runCase`) |
| `weighing-zone`, `weighing-record` | weighing | weighing | WG-3, WG-7 |
| `attitudes-elaborate` (plan: also `-status`, `-conflict`, `-report`) | attitudes | attitudes | AT-3a; the three duplicates of today's kinds go to AT-0's review (see 7) |
| `scales-coherence` | scales | quantities | QT-B2 |
| `defaults-elaborate`, `-coherence`, `-certificate`, `-model` | soft | defeasible | DF-1a (DF4) |
| `defaults-zone` | soft | defeasible | DF-5 |
| (none: events adds report fields) | events | events | ET-4 |

### 2.11 `transfers_append` (on the superposed readings route)

- `transfers_append` (stub:363, proved). Two carried families that each transfer
  (`Readings/SupExtra.lean:33–36`) transfer when appended.
- `transfers_X` (stub:374, proved). If each pack's premises transfer, `X` transfers, with the families
  concatenated in `X` order. `transfers_nil` (`SupExtra.lean:281`) is the empty case.

## 3. What every provider must prove (in its own plan)

1. **Kind.**
   - A `vocabulary` pack proves `ExpandsOn U earlier p` (stub:310). Every admissible base of the base and the
     earlier packs expands, changing only the pack's own names, to a typed structure that is still admissible and
     satisfies the pack's premises.
   - A `constraint` pack keeps its own local checks and makes no conservativity claim.
2. **Typing.** Its premises are typed over `extendEnv (envAt (fill U) 0) p.decls p.consts`, the hypothesis of
   `assemble_wellFormed`.
3. **Freshness.**
   - Its decoder refuses author names that begin with its prefix.
   - Its generated names begin with its own prefix row.
   - `assemble` checks the rest (2.4).
4. **Transfer.** On the superposed readings route, it proves `Transfers D Q Q'` for its premises under
   candidate-gated choices (`∀ x ∈ A, (candidate D x.1 x.2).isSome`). `transfers_X` combines the packs.
5. **Origins.** It proves `OriginsExact p` (stub:320): every label and generated name has exactly one origin, and
   nothing else has one. The relay binds each origin to the request.

`ExpandsOn` and `OriginsExact` land with the first provider that proves them (AT-2), not in pk-1. Nothing in pk-1
uses them, and R16 asks that every new trusted definition be exercised by a test.

## 4. Acceptance fixtures

The stub checks fixtures A1–A9 by `#guard` (stub:416–482), and the F1 and A9′ checks by `#guard` (stub:484–512). pk-1 keeps them as `#guard`s in
`lean/VE/NormDefaults/PacksExamples.lean` and adds the corpus checks (L1, L2).

| # | Fixture | Expected |
|---|---|---|
| L1 | Today's soft corpus: every `norm-defaults-*` case in `tests/data/route-cases.jsonl` and the layered tests (`tests/test_norm_defaults_layered.py`, `tests/test_route_transport.py`), on the soft route | Every answer byte-identical, base vs head (saved A/B evidence) |
| L2 | The same on the soft+rights corpus, including the `InvalidModel(rights)` and `InvalidModel(soft)` cases | Byte-identical |
| A1 | `[soft, rights]`, `[rights, soft]`, `[weighing, soft]` | Soft first, then `packOrder`; labels in each pack's order |
| A2 | A repeated id | `InvalidInput: premise pack soft is given twice` |
| A3 | A repeated label, within one pack and across two | `… premise label soft:coherence:r1,r2 of pack <id> is used twice`, naming the later pack |
| A4 | A generated name the environment declares (an author's `attitudes__knows__1`, or `helps`); one another pack declares; one without its prefix | `… is already declared`; `… is declared twice` (naming the later pack); `… lacks its reserved prefix` |
| A4′ | Fresh, prefixed names from two packs | Accepted; `extendEnv` declares them and keeps `helps` |
| A5 | The empty pack list | `ok []`, `X = []`, `envX = envAt (fill U) 0` (`assemble_nil`, `envX_nil`) |
| A6 | An unknown id (`acts`); the limit at 255+2, 256 and 257 | `unknown premise pack acts`; `ResourceLimit: vocabulary size` above 256 only |
| A7 | Diagnostics: legacy soft failing, legacy rights failing, `[soft, weighing]` failing | Today's two texts; `InvalidModel(weighing): …: weigh:strength:a:b:x_permitted` |
| A8 | `packPremises`, absent pack, `xWithout` | Rights' labels; `[]`; coherence dropped |
| A9 | Elaborate keys: legacy, empty, `[soft, weighing, events]`; further entries (AT-2) of a legacy list and of `[soft, weighing, events]` | `soft, rights` on all three; today's soft array JSON; none; `weighing, events` |
| A9′ | The closed keys of `layered_elaborate`, read from the shape | They hold `soft`, `rights` and every key `[soft, weighing, events]`'s elaborate writes, and no further pack's id |
| F1 | A rights document repeating a limitation, one repeating a condition, and five well-formed ones (`Rights/Examples.lean`) | The first two: `WellFormedSoft (correlate R)` and `WellFormedU` hold, the labels repeat, `WellFormedRights` refuses. On all seven, both nodup statements hold |

## 5. Build plan for pk-1 and pk-1b

**Files.** `Readings.SupExtra` imports `NormDefaults.Layered` (through `SupFill` and `Unspecified`), and
`Layered.lean` must import the core, so the core cannot hold `transfers_X`, and it cannot hold what reads
`Layered.lean`'s `softLabelledU`, `layeredCase` or `FilledX`. The stub's `planFiles` (stub:534) is this list. It gives
every stub declaration its file, and a check (stub:603) fails when a declaration uses a module its file cannot
import, or a declaration of a later file, or when a file's importer is among its imports. Seeded bugs M12–M16 show
that the check fails on the draft's placement (`transfers_X` in the core) and on each kind of misplacement.

| File, in import order | Imports | Imported by | Holds |
|---|---|---|---|
| `lean/VE/NormDefaults/Packs.lean` (new, the core) | `Layered.lean`'s own imports: `VE.NormDefaults.Explain`, `VE.Rights.Wire` | `Layered.lean` | 2.1–2.5; `legacyIds`; 2.6's `X_legacy`, `legacy_take`, `legacy_drop`, `packPremises_absent`, `X_soft_first`; 2.7's `labelledJson`, `elaborateArrays`, `elaborateArrays_keys`, `elaborateArrays_legacy`; 2.8 without the legacy theorems; 2.9 without `filledX_whole`; pk-1b: `KindRow`, `dispatch` |
| `lean/VE/NormDefaults/Layered.lean` (hunks below) | unchanged, plus `Packs` | as today | `softPack`, `rightsPack` (after `softLabelledU`, before `LayeredU`); pk-1b: `legacyKinds`, `legacyRows` (before `layeredCase`) |
| `lean/VE/NormDefaults/PacksLegacy.lean` (new, theorems) | `VE.NormDefaults.Layered` | `LayeredAdmission.lean`, `Readings/UnspecifiedWire.lean` | `softLabelledU_labels_nodup`, `legacy_labels_nodup_of_actKeys`, `assemble_legacy_soft`, `assemble_legacy_rights`, `packPremises_legacy`, `packFault_legacy_rights`, `packFault_legacy_soft`, `filledX_whole`; pk-1b: `dispatch_legacy` |
| `lean/VE/Readings/SupPacks.lean` (new, theorems) | `VE.Readings.SupExtra` | nothing yet | `transfers_append`, `transfers_X` |
| `lean/VE/NormDefaults/PacksExamples.lean` (new) | `PacksLegacy`, `VE.Rights.Examples`, `ResponseShape.Schemas.NormDefaults` | nothing | fixtures A1–A9, A9′ and F1 |
| The first provider (AT-2) | above all of these | | `packEntry`, `furtherEntries` (with its shape row), `expandBy`, `ExpandsOn`, `OriginsExact` |

**Shared-file hunks** (queue SYNTHESIS 4.2: PK-1 is first on `Layered.lean`; no branch in flight edits these files):

| File | Hunk |
|---|---|
| `NormDefaults/Layered.lean` | `import VE.NormDefaults.Packs`. `softPack` and `rightsPack` after `softLabelledU` (`:51–53`). `LayeredU`: `packs : List Packs.Pack` replaces `labelled` and `rightsCount` (`:64–65`). `LayeredU.X := Packs.X L.packs` (`:72`). `decodeSoftU`: `[softPack U src.D]` (`:101`). `decodeRightsU`: `[softPack U D, rightsPack src.D]` (`:121`), each through `assemble` (used = `checkAuthorN`'s count). `layeredElaborate` uses `elaborateArrays` (`:150–153`). `filledX`'s else branch uses `packFault` (`:289–290`). pk-1b: `layeredCase` is renamed `legacyCase`, and the new `layeredCase` is `dispatch` over the four rows (`:410–437`) |
| `NormDefaults/LayeredAdmission.lean` | `import VE.NormDefaults.PacksLegacy`. `decodeSoftU_source`: `L.packs = [softPack L.U src.D]` replaces the `labelled`/`rightsCount` conjuncts (`:35`), by `assemble_legacy_soft`. `SoftLeafX` reads `packPremises L.packs "soft"` (`:105`) |
| `Readings/UnspecifiedWire.lean` | `choiceLayeredG`: the norms chain gets `[]`, the empty pack list (`:509`, today `softXL N X, 0` with `choiceX_normsShaped`). The soft chain gets `[softPack U (correlate X)]` (`:527`). It imports `PacksLegacy` if a proof there needs a legacy theorem |
| `ResponseShape/Encoders/NormDefaults.lean` | Unfold `elaborateArrays` and `packPremises` in the `fits` proof (`:61`). The shape is unchanged: by `elaborateArrays_keys` the keys do not depend on `L.packs`, so `layeredCase_fits` still holds for every `LayeredU`. pk-1b: unfold `dispatch`, `legacyRows` and `legacyCase`; the `UnsupportedProfile` refusal is an error, which `OkP` does not constrain |
| `Audit.lean`, statements and trust classes | Regenerated (`tools/regen_generated.py --write`); `tools/trust-classes.json` entries for the new declarations, tying `assemble` and `packFault` to `assemble_order`/`assemble_fresh` and the legacy theorems |

**What pk-1 does not change.**
- Every checker stays over `envAt (fill U) 0`: certificates, `situationX`, `sitVocab` and `baseEnv`.
- No decoder builds a pack with names until the first vocabulary provider (AT-2) threads `envX` into situations,
  certificates and `BaseAdmissibleX`, under AT-0's review. A premise over an undeclared name cannot be accepted by
  a certificate check over `envAt (fill U) 0`: `checkCertificate` checks every premise's typing first
  (`Order/Tableau.lean:959`).
- No response shape, generated schema or relay changes, in pk-1 or pk-1b. The first provider adds its key.
- No Python and no Rust changes. Outputs are byte-identical.

**Seeded bugs for pk-1 (Lean)**, each with the test that must fail:

| Bug | Fails |
|---|---|
| `packOrder` with rights first | L2 and A1 |
| `firstRepeat` without the seen list | A3 |
| `declaredIn` ignoring constants | A4 with an author constant `date__d` (a pk-1 fixture) |
| `packFault`'s legacy branch removed | L2 (`InvalidModel(rights)` case) and A7 |
| `elaborateArrays` writing a further pack's entry | `elaborateArrays_keys`, A9 and A9′ |
| `choiceLayeredG` giving the soft pack on the norms chain | A5 and the readings tests |
| pk-1b: `dispatch` running a row whose pack is absent | a pk-1b fixture with a row that needs an absent pack |

**Expected trust growth** (`tools/trust_map.py`, K+S+untied V, before the ties pass). Measured on the stub's
definitions with their docstrings; `trust_map` also counts the blank line after each declaration, about +1 each.
Theorems are P and fixtures T, so `PacksLegacy.lean`, `SupPacks.lean` and `PacksExamples.lean` add none.

| File | pk-1 | pk-1b |
|---|---|---|
| `Packs.lean` | about +125 (28 definitions of 2.1–2.9: 100 lines with docstrings, and about 25 blank lines) | about +17 (`KindRow`, `dispatch`) |
| `Layered.lean` | about +7 (`softPack`, `rightsPack`; the `LayeredU` fields, the `packFault` call and the elaborate arrays swap one for one) | about +12 (`legacyKinds`, `legacyRows`, the new `layeredCase`) |
| `LayeredAdmission.lean`, `UnspecifiedWire.lean` | about 0 | 0 |
| Total | about +132, K +0 | about +29, K +0 |

With the kind table, pk-1 would be about +160, over R16's 150 lines. So the cut is made now: **pk-1b** is the kind
table (2.10), and it lands before the first provider row. The further-pack entries (2.7) land with the first provider.
Both items fit R16 (at most 150 lines, no K); each DELTA row asks for the ties pass in FOLLOW-UPS. pk-1 measures on its final
HEAD, and if it is still over 150 it moves 2.8 (`firstFailing`, `packFault`, about 12 lines) to pk-1b as well,
keeping today's `filledX` text.

## 6. Status of the statements

- **Proved in the stub (13):** `extendEnv_nil`, `envX_nil`, `assemble_nil`, `X_legacy`, `legacy_take`,
  `legacy_drop`, `packPremises_legacy`, `packPremises_absent`, `xWithout_nil`, `xWithout_sub`, `filledX_whole`,
  `elaborateArrays_keys`, `transfers_append`.
- **Proved, extra (1):** `transfers_X`.
- **`sorry`, for pk-1 to prove (13):** `assemble_order`, `assemble_fresh`, `assemble_wellFormed`,
  `softLabelledU_labels_nodup`, `legacy_labels_nodup_of_actKeys`, `assemble_legacy_soft`, `assemble_legacy_rights`,
  `X_soft_first`, `elaborateArrays_legacy`, `firstFailing_some`, `packFault_legacy_rights`,
  `packFault_legacy_soft`, `dispatch_legacy` (pk-1b).
- If pk-1 finds one false, it stops and reports with a mechanised counterexample; it never adds a hypothesis
  (DRI-RULINGS, never covered).

Seeded bugs in the stub: `docs/spec/premise-packs/mutants.json`, nineteen mutants, each failing a `#guard`, a proof
or the file check. `uv run python docs/spec/premise-packs/mutants.py` regenerates it on the tree before pk-1 (M11: F1's
hypothesis; M12–M16: the file split; M17: the closed elaborate shape; M18–M19: `hk`).

## 7. Requests from the provider plans that PK-1 does not take

Provider-plan citations are on each plan's `research/<plan>-p1` branch.

- **Attitudes' point check in `replayStatusX` for all packs** (attitudes.md:1476–1478). Checking legacy soft
  premises at the point would change today's status answers. AT-2 adds the check for its own pack's premises, under
  AT-0's review.
- **Attitudes' three kinds that duplicate today's** (`attitudes-status`, `-conflict`, `-report`, PLAN:1132–1135).
  Today's kinds already read the whole `X`. Whether a second row is needed is AT-0's question, so that one owner
  answers each kind.
- **Weighing's joint size budget** (weighing.md:638). PK-1 bounds only the vocabulary, its one shared limit. Each
  provider's decoder bounds its own premises, and the joint bound is their sum.
- **Events' namespace `VE.Packs`** (events.md:366). It is `VE.NormDefaults.Packs`, as SYNTHESIS 2.1 says. Events'
  constant encoding is `consts`, not `decls`.
- **Scales' labels without a prefix** (quantities.md:1005). These are allowed, but they must not repeat another
  pack's label. `assemble` refuses a repeat (A3), so `scales:` is recommended.
