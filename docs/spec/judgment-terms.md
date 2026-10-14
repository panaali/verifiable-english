# Judgment terms (`judgments@0`), item 1: statement specification

> **Status.** Draft 3 (2026-10-14), branch `research/judgment-terms-p1`, with
> [judgment-terms-PLAN.md](judgment-terms-PLAN.md) draft 4. It applies phase 1's results
> ([docs/research/judgment-terms-phase1.md](../research/judgment-terms-phase1.md)) to this spec. **No definition,
> theorem statement, diagnostic or existing fixture value changes.**
>
> **Changes in this draft (3).**
> - New 0.2: what phase 1 found that bears on the statements, and why none of them changes.
> - New fixture J-ω (11.2, 11.3, 11.8). One word over two sorts is two bound terms that share their words (plan D2).
>   Each term has its own usage row, and one record cannot stand for the other sort. Its values were computed by
>   `#eval` in the re-elaborated stub.
> - 9: the declaration line is one line per bound term, and a template the lint rejects falls back to today's wording.
> - 10: the pilot points updated with phase 1's measurements. JT-5 is now JT-5a, JT-5r and JT-5b (plan section 5).
> - Stub: J-ω added at the end of its fixture section, and the whole stub re-elaborated with no error (see "Checked,
>   not proved").
>
> **Draft 2** (2026-10-14), written by JT-0 from [judgment-terms-PLAN.md](judgment-terms-PLAN.md) draft 3,
> which carries the converged Astra/Fable debate (`manage-agents/debates/design-judgment-terms/`, rounds 1 to 3:
> REVISE to draft 2, then BUILD). Draft 2 applies the statement review's converged joint position
> (`manage-agents/debates/judgment-terms-spec/`, rounds 1 to 3: **FIX**, then PASS once the corrected statements
> elaborate and the changed fixtures are recomputed): Astra's A1 to A5 and Fable's F2, F3′ and F4, with Astra's
> precision on completeness, and the F3 wording; it changes nothing else. It states, for the plan's item 1 (JT-1 to
> JT-4, with JT-3's report): the definitions, the exact Lean statements, the diagnostics, the English wordings with
> their one reading, and the acceptance fixtures with their values. It changes no frozen W1, W2, soft, rights or P0
> semantics; the two frozen files it touches (section 1, section 3) keep every existing caller's bytes.
>
> **Checked, not proved.** Every definition and theorem statement below was elaborated in an untracked stub
> (`lean/SpecStubs_judgment-terms.lean`, never committed) with `lake env lean`, against this branch at `eb3d6bf1`,
> whose `lean/` tree equals `main` at `f98183bf` (`git diff` empty). Draft 2 re-elaborated the whole stub with
> `lake --dir <ve-nightly>/lean env lean`, a build at `f98183bf` (this branch's `lean/` tree still equals it), with no
> error. Draft 3 added J-ω and re-elaborated the whole stub the same way: `lake --dir <ve-nightly>/lean env lean`, from
this branch's `lean/`, whose tree still equals `f98183bf`. The run had no error, and every earlier `#eval` output was
unchanged; the only new output was J-ω's four lines. The stub stays untracked. Draft 3's copy is kept outside the
repository, at `manage-agents/judgment-terms-SpecStubs-draft3.lean`, because `lean/audit.py` scans every `.lean` file
under `lean/`. In the stub, `Loader.openTermNames`
with JT-1's one hunk is a copy of today's function with the hunk applied
> (section 1); everything else is written as below. Fourteen statements were proved outright in the stub, and two more from the stated `status_eq` (section 12
> lists them; among them `nodeOpen_eq`, `faultOf_none_iff`, `status_legacy`, `viewOf_legacy`, `usageMap_unused`,
> `conflictFree_given` and `leftToPair_differ_ne_nil`); the others are the batches' obligations. Every fixture value in
> section 11 was computed by `#eval` in the same stub; none was computed by hand, and no model was called.
>
> **Interfaces not on `main`.** WG-6's zone answer (`VE.Weighing`: `openNames`, `AdmissibleCompletion`, `SettledZ`,
> `LeftToZ`, `ZoneAnswer`, and `completionOf`, which its `zone_notSaid_sound` names) was written in the stub from
> weighing-PLAN.md draft 4, section 3.4, with request R1's explicit `opens` (`zoneOfOpens`, an opaque stand-in, and
> `zoneOf` its `openNames L` instance) and R1's certified pair (`LeftToPair`, 6.1; `completionOf` an opaque stand-in).
> english-lean's catalogue rows for evaluative words do not exist yet; `EvaluativeRow` (section 7) is the shape this
> spec needs, and JT-3 binds it to english-lean's single catalogue. Every statement that names them is re-elaborated when the item
> lands; the batch that consumes it does that first.

## 0. What the stub found

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| F1 | Draft 1's `deciders` ("in first-occurrence order" over the differing atoms) is complete only when record names are distinct: with two records named `arbitrary` (deciders `court`, `unresolved_decider`) it names `court` only | 11.7: `decidersFirst` gives `["court"]`, `deciders` gives `["court", "unresolved_decider"]` | `deciders` reads the records in declaration order (6.2); `deciders_complete` needs no hypothesis. On admitted documents the two agree, since W2 refuses a repeated name; the two-record row is therefore an internal input to `deciders`, not a service fixture (11) |
| F2 | J-ι as draft 1 wrote it ("a rule **requiring** the arrest where `court_ordered(a)`") has no conflict on `subjects`: two rules conflict on one regulated predicate when they have opposite signs; an obligation's conflict is the pair conflict `required ∧ ¬permitted` | 11.5: the conflict formula of `subjects` with a forbidding and a **permitting** rule is true at exactly one of the eight assignments | J-ι is written with a permitting rule ("An arrest ordered by a court is permitted") |
| F3 | **Settled by the statement review.** Dependence through rule chains is not tracked. A rule unit whose guard reads a regulated predicate (`subjects`) that another unit's rule decides on a judgment is CHECKED, and the usage map omits it | 11.3, J-χ: `u2`'s status `CHECKED`; usage map `[("arbitrary", ["u1"])]` | kept, with the narrower guarantee the review agreed: dependence is syntactic use, directly or through W3 definitions (plan D3, D4). A unit's status is about its own meaning, which its W3 definitions are part of and another unit's rule is not; that other unit (`u1`) is already OPEN. An outcome downstream can still vary with a judgment (section 13); the zone answer (JT-4) answers that over the whole cone. J-χ stays as the fixture that shows the limit, and JT-5 records each such unit |
| F4 | `LayeredU`, `ConflictFreeX`, `BaseAdmissibleX` and `conflictFreeX` live in `VE.NormDefaults.Wire` (`Layered.lean:59`, `:159`, `Report.lean:201`). Draft 1 and WG-6's plan write `VE.NormDefaults.LayeredU` | elaboration | the statements use the `Wire` names |
| F5 | `layeredElaborate` and `filledX` split `L.labelled` into soft and rights premises by `rightsCount` (`Layered.lean:150-153`, `:289-290`). A source with the criteria appended would mislabel them | reading of the two functions | `withCriteria` (5.2) is read only by the conditional conflict check (`conflictFreeX`, `firstFailureX`); a witness under the criteria is JT-4's own check |
| F6 | Draft 1's separate `setStatus` is not needed: with one view per unit (plan fix 2) one `status` covers both cases, and its legacy value is `Loader.foldStatus`'s | `viewOf_legacy`, proved | one function, `status` (4.3) |
| F7 | `VE/Discourse/Loader.lean` and `VE/Rights/Run.lean` are both in the frozen-sources inventory (`lean/VE/Route/frozen-sources.sha256`, lines 88 and 283) | the inventory | JT-1 regenerates it with `tools/regen_generated.py --write`, after both hunks |
| F8 | Admission must read the W3 definitions to compute the base vocabulary, so `admit` takes them | elaboration of `JudgmentUnbound` through `hide` | `admit E defs regulated rs` (2.2) |

### 0.1 The statement review's corrections (draft 2)

The review (`manage-agents/debates/judgment-terms-spec/`) converged on FIX with these edits. Each changed statement was
re-elaborated, and each changed fixture recomputed by `#eval`, in the stub; the rows below are the ones to re-check.

| # | Correction | Where |
|---|---|---|
| A1 | J-ξ broke W2: an authored set has exactly one signed reading (`Loader.lean:512-513`), and draft 1's two candidates were equivalent formulas, so no model could separate them. J-ξ is now an authored set with one reading; J-ξ′ an open set of u055's two scopes, which really differ, with a model that separates them. "order 1"'s last record is `unreasonable [person]` (a repeated name is W2's refusal, "duplicate or invalid open term", `Loader.lean:378`, before admission). Inputs that W2 refuses on the wire are marked *internal* | 11.2, 11.3, 11.7, 11.8; plan 4.1, 4.2 |
| A2 | `zone_leftTo` concluded the existential `LeftToZ`, which nothing ties to the returned `w₁`, `w₂` and `differ`, so an empty `differ` satisfied it. It now concludes the certified pair `LeftToPair`: both shown assignments complete `M` admissibly, their outcomes are opposite, they agree on every unsaid atom, and `differ` is exactly the atoms on which they differ. Request R1 asks WG-6 for it; JT-4 adds a wrong-witness and an empty-`differ` mutation | 6.1, 12; plan 3.4, JT-4, 11 (R1) |
| A3 | "Unconditional" and "whatever is judged" are kept for the plain theorem `conflictFreeU_consistent` only. On the layered route the answer assumes the route's own premises `L.X` (soft coherence, rights limitations): its line names them and says "without additional judgment criteria". `conflictFree_unconditional_given` is renamed `conflictFree_given_mono` | 5.2, 9.4, 11.6, 11.8, 12, 13; plan D6, 2.3, 2.4, 2.5, 3.4, 3.6, 4.1, JT-4 |
| A4 | `status_eq` says "judgment dependence forces OPEN; otherwise the legacy status applies", not "OPEN exactly when dependent": a legacy OPEN needs no judgment | 4.3, 11.8; plan D3, 2.2 |
| A5 | The relay checks order: terms in declaration order, unit ids in unit order, so a reordered `judgments` answer is `CheckerUnavailable` | 8.3; plan JT-2 |
| F2 | A `contextual` or `unformalised` unit whose content uses a judgment moves from LABELLED or UNFORMALISED to OPEN, which JT-5's draft-1 bar ("moves from CHECKED to OPEN") rejected. New bar: every claimed unit keeps its status or moves to OPEN; none moves to CHECKED. Fixture J-υ | 4.3, 11.3, 11.8; plan 4.1, JT-5 |
| F3 | Dependence stays definition-only, with the narrower guarantee (row F3 above) | 0, 4.3, 13; plan D3, 2.2, 3.6, 9, JT-5 |
| F3′ | Lean's `preds` (section 7) kept regulated predicates while the relay (8.4) refused them, so a genuine answer naming one was `CheckerUnavailable`. Both now include them: an evaluative word inside a regulated act is the hidden case D15 targets (C u0052.s01). The report never makes a regulated predicate admissible as a judgment | 7, 8.4, 11.7; plan D15, JT-3 |
| F4 | `JudgmentListedUnused` refused units whose list cannot show a judgment unused: no own content, or an active set with a pending reading. The check, and its conjunct of `status_ok_iff`, now apply only to a complete unit (`UnitView.complete`). Completeness follows `reads`' precedence: with an active set, the set has a reading and none is pending, whatever the unit's own content; without one, the unit has its own content. The pending readings are kept in the traversal (`none`) and omitted by `reads`. The other two unit checks, and today's checks on asserted content, are unchanged. Fixture J-τ′ | 4.2, 4.3, 8.1, 8.2, 11.3, 11.8; plan 2.1, 2.2, 3.3, 4.1 |

### 0.2 Phase 1 (draft 3)

Phase 1 ran JT-0p on copies of the pinned pilot run, and measured the pilots' records against the admission checks of
2.2. It changed no code. Its results that bear on this spec:

| # | Phase-1 result | Evidence | Consequence here |
|---|---|---|---|
| P-a | The UDHR's `arbitrary` is four predicates over four sorts in two parts: `is_arbitrary(measure)`, `is_arbitrary_u045a(interference)`, `is_arbitrary_u046(intrusion)`, and in part 2 `is_arbitrary_u064(deprivation)` | phase 1, 2.6 | No statement changes. `Judgment.arguments` is one sort list, W2 refuses a repeated name, and `faultOf` compares the sorts exactly, so one word over n sorts is n records (plan D2). Fixture J-ω shows it: two terms admitted, one usage row each, and the other sort refused as `JudgmentArguments` |
| P-b | Admission forecast. The UDHR: 52 of 52 records unbound (no predicate has a term's exact name), all `unstated`. The constitution: 31 of 33 admitted; `good_judgment` unbound and `child_sexual_abuse_material` `JudgmentArguments` | `admission-forecast.json` | No statement changes: `faultOf`'s checks and their order are what the forecast applied. The pilots' work goes to the plan's JT-5a, JT-5r and JT-5b |
| P-c | No CHECKED unit with content, in either pilot, uses an open-term predicate or a catalogue word (0 hits in 20; control 35 of 49) | `integrity.json` | No statement changes. `status_eq` is expected to move no pilot unit (plan JT-5) |
| P-d | JT-0p's two templates are rejected by the wording lint, and the units render with identifiers | phase 1, 2.2 | 9: the lines fall back to today's wording when a template is rejected |
| P-e | Any change to the environment changes every reading-set id | phase 1, F3 | No statement changes. The pilots rebuild their sets at each profile switch (plan JT-5) |

## 1. W2 under the profile (JT-1: one hunk in `lean/VE/Discourse/Loader.lean`)

`Loader.openTermNames` gains one optional parameter. Line 380 today:

```lean
    unless args.all token && args.eraseDups.length == args.length do throw "invalid open-term arguments"
```

becomes

```lean
    unless args.all token && (sorts || args.eraseDups.length == args.length) do throw "invalid open-term arguments"
```

with `(sorts : Bool := false)` after `formula` in the signature. Every existing caller passes nothing, so its bytes do
not move; only `Judgments.records` (2.1) passes `sorts := true`, and only under the profile.

```lean
/-- The flag only relaxes: what W2 admits without it, it admits with it, with the same names. -/
theorem openTermNames_sorts (rv j python data formula ns)
    (h : VE.Discourse.Loader.openTermNames rv j python data formula (sorts := false) = .ok ns) :
    VE.Discourse.Loader.openTermNames rv j python data formula (sorts := true) = .ok ns
```

Fixture (11.1, J-ο on the wire): `[person, person]` is refused without the flag, with today's text, and admitted with
it; `["act"]` gives the same answer all three ways.

## 2. Records and admission (JT-1: `lean/VE/Judgments/Decl.lean`)

```lean
import VE.Discourse.Loader
import VE.Definitions.Layer

namespace VE.Judgments

/-- A bound judgment: a W2 open term whose name is a base predicate (D1, D2). `factors` are shown, never premises. -/
structure Judgment where
  name      : String
  arguments : List String
  decidedBy : String
  factors   : List String
  deriving DecidableEq, Repr

/-- One record as written, after W2's check: the judgment and the lengths of `necessary` and `sufficient`. -/
abbrev Rec := Judgment × Nat × Nat
```

### 2.1 Records

W2 stays the one validator: `records` runs `Loader.openTermNames` (with `python`, and `sorts := true`) first, and only
then reads the fields it has checked.

```lean
def records (rv : VE.Route.Wire.RouteVocabulary) (j : Json) (data : Bool)
    (formula : Option (Json → Except String Unit)) : Except String (List Rec) := do
  let names ← VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula)
    (sorts := true)
  let items := match j with
    | .arr xs => xs.toList
    | _ => []
  let str := fun (item : Json) (k : String) => (item.getObjValD k).getStr?.toOption.getD ""
  let strs := fun (item : Json) (k : String) => (VE.Bridge.strings (item.getObjValD k)).toOption.getD []
  let len := fun (item : Json) (k : String) => ((item.getObjValD k).getArr?.toOption.getD #[]).size
  pure ((items.zip names).map fun (item, name) =>
    (⟨name, strs item "arguments", str item "decided_by", strs item "factors"⟩,
      len item "necessary", len item "sufficient"))

theorem records_names (rv j data formula rs) (h : records rv j data formula = .ok rs) :
    VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula) (sorts := true) =
      .ok (rs.map (·.1.name))

theorem records_refuse (rv j data formula e)
    (h : VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula)
      (sorts := true) = .error e) :
    records rv j data formula = .error e
```

### 2.2 Admission

Admission reads the **base** vocabulary, `hide E (names defs)`: a W3-defined name is not a base predicate, so it is
unbound. `defs` is the route vocabulary's compiled W3 list, `rv.definitions` (dependency order; the list the norms tree
copies, `lean/VE/Norms/Wire.lean:304`). `regulated` is the names the environment declares with a `regulated` entry.

```lean
def baseEnv (E : VE.Environment) (defs : List VE.Definitions.Def) : VE.Environment :=
  VE.Definitions.hide E (VE.Definitions.names defs)

/-- The checks of plan 2.1, items 1–5, in that order, for one record. -/
def faultOf (E : VE.Environment) (defs : List VE.Definitions.Def) (regulated : List String) (r : Rec) :
    Option String :=
  match (baseEnv E defs).predicates r.1.name with
  | none => some s!"JudgmentUnbound: {r.1.name}"
  | some ss =>
    if ss != r.1.arguments then some s!"JudgmentArguments: {r.1.name}"
    else if regulated.contains r.1.name then some s!"JudgmentRegulated: {r.1.name}"
    else if r.2.1 != 0 || r.2.2 != 0 then some s!"JudgmentCriterionAsUnit: {r.1.name}"
    else if r.1.decidedBy == "unstated" then some s!"JudgmentDecider: {r.1.name}"
    else none

/-- `judgments@0`'s admission: the first fault in record order. -/
def admit (E : VE.Environment) (defs : List VE.Definitions.Def) (regulated : List String) (rs : List Rec) :
    Except String (List Judgment) :=
  match rs.findSome? (faultOf E defs regulated) with
  | some e => .error e
  | none => .ok (rs.map (·.1))

def names (js : List Judgment) : List String := js.map (·.name)

/-- A record is admitted exactly when it is bound to a base predicate with its sorts, no rule regulates it, it
    carries no criterion lists, and its decider is not `unstated`. -/
theorem faultOf_none_iff (E defs regulated r) :
    faultOf E defs regulated r = none ↔
      (baseEnv E defs).predicates r.1.name = some r.1.arguments ∧ r.1.name ∉ regulated ∧
        r.2.1 = 0 ∧ r.2.2 = 0 ∧ r.1.decidedBy ≠ "unstated"

theorem admit_ok_iff (E defs regulated rs js) :
    admit E defs regulated rs = .ok js ↔ js = rs.map (·.1) ∧ ∀ r ∈ rs, faultOf E defs regulated r = none

/-- The fault is the first faulty record's first failing check. -/
theorem admit_first_fault (E defs regulated rs e) (h : admit E defs regulated rs = .error e) :
    ∃ pre r post, rs = pre ++ r :: post ∧ (∀ q ∈ pre, faultOf E defs regulated q = none) ∧
      faultOf E defs regulated r = some e

end VE.Judgments
```

## 3. The one scan of open names (JT-1: `lean/VE/Judgments/Scan.lean`, and one hunk in `lean/VE/Rights/Run.lean`)

`Scan.lean` imports only `VE.Norms.Tree`, so rights can import it.

```lean
import VE.Norms.Tree

namespace VE.Judgments

/-- The names of `J` that the formulas `fs` mention, in `J`'s order: the one scan of open names in formulas. -/
def opensIn (J : List String) (fs : List VE.Formula) : List String :=
  J.filter fun j => fs.any fun φ => (VE.Norms.preds φ).contains j

theorem opensIn_iff (J fs j) : j ∈ opensIn J fs ↔ j ∈ J ∧ ∃ φ ∈ fs, j ∈ VE.Norms.preds φ

theorem opensIn_isEmpty (J : List String) (fs : List VE.Formula) :
    (!(opensIn J fs).isEmpty) = fs.any (fun f => (VE.Norms.preds f).any J.contains)

end VE.Judgments
```

Rights' `nodeOpen` (`lean/VE/Rights/Run.lean:159-162`) becomes:

```lean
def nodeOpen (openNames : List String) (N : SoftNode) : Bool :=
  N.mode == .default || !N.alterable.isEmpty || !(VE.Judgments.opensIn openNames (N.guard :: N.carveOuts)).isEmpty
```

and JT-1 states, in `Run.lean`, today's body as an equation, so that the switch is visibly byte-neutral:

```lean
theorem nodeOpen_eq (openNames : List String) (N : SoftNode) :
    nodeOpen openNames N =
      (N.mode == .default || !N.alterable.isEmpty ||
        (VE.Norms.preds N.guard).any openNames.contains ||
        N.carveOuts.any (fun f => (VE.Norms.preds f).any openNames.contains))
```

The stub proved it (as `nodeOpenNew = VE.Rights.Run.nodeOpen` over today's definition) from `opensIn_isEmpty`. Rights'
frozen fixtures must pass unchanged, and the frozen-sources inventory is regenerated (F7). Rights' separate checks (the
default mode, the alterable parties, the limitations and bars of `unitOpen`) are not touched.

## 4. Dependence, status and the usage map (JT-1: `lean/VE/Judgments/Status.lean`)

`Status.lean` does not import `VE.Service.Document`: the document mode calls it (JT-2), so the content type it reads is
its own, and the document mode maps its `UnitContent` onto it in one line (`.formula f ↦ .formula f`,
`.norm n ↦ .rule n`).

### 4.1 Dependence (D4)

```lean
import VE.Judgments.Decl
import VE.Judgments.Scan
import VE.Closure.Paths

namespace VE.Judgments

/-- What one content reads: a formula, or a rule (its guard and carve-outs, as rights' `nodeOpen` reads them). -/
inductive Content
  | formula (φ : VE.Formula)
  | rule (N : VE.Norms.Node)
  deriving DecidableEq, Repr

def Content.formulas : Content → List VE.Formula
  | .formula φ => [φ]
  | .rule N => N.guard :: N.carveOuts

/-- The definition graph: a defined name points at each predicate of its body. -/
def defEdges (defs : List VE.Definitions.Def) : List (String × String) :=
  defs.flatMap fun d => (VE.Norms.preds d.body).map (d.name, ·)

/-- The bodies of the definitions the formulas reach: each definition whose name a formula mentions, or reaches
    through other definitions. -/
def reachedBodies (defs : List VE.Definitions.Def) (fs : List VE.Formula) : List VE.Formula :=
  let ps := fs.flatMap VE.Norms.preds
  (defs.filter fun d => ps.any fun p => p == d.name || VE.Closure.reachEval .plus (defEdges defs) p d.name).map
    (·.body)

/-- The judgments the formulas depend on: used directly, or reached through W3 definitions. One scan, `opensIn`. -/
def dependsOn (defs : List VE.Definitions.Def) (J : List String) (fs : List VE.Formula) : List String :=
  opensIn J (fs ++ reachedBodies defs fs)

theorem dependsOn_iff (defs J fs j) :
    j ∈ dependsOn defs J fs ↔
      j ∈ J ∧ ∃ φ ∈ fs, ∃ p ∈ VE.Norms.preds φ, p = j ∨
        VE.Closure.Reachable .plus (fun a b => (a, b) ∈ defEdges defs) p j

/-- Without definitions, dependence is the direct scan. -/
theorem dependsOn_no_defs (J fs) : dependsOn [] J fs = opensIn J fs

/-- The judgments a list of contents depends on. -/
def dependsOnC (defs : List VE.Definitions.Def) (J : List String) (cs : List Content) : List String :=
  dependsOn defs J (cs.flatMap Content.formulas)
```

Proof note: `dependsOn_iff` is `opensIn_iff` with `reachEval_iff` (`lean/VE/Closure/Paths.lean:190`), and the last edge
of a path in `defEdges` names the definition whose body is scanned.

### 4.2 One traversal per unit (plan fix 2)

Each unit gives one list of contents: its own content, or, when an active reading set speaks for it, that set's
candidates. The status and the usage map read only this list. The traversal keeps each pending reading as `none`, so
that `complete` can see it before `reads` omits it (F4).

```lean
/-- The active reading set of a unit, as the loader folds it: its two flags and its candidates, in order; a pending
    reading (`content: null`) is `none`. -/
structure ActiveSet where
  authored    : Bool
  allAsserted : Bool
  candidates  : List (Option Content)
  deriving DecidableEq, Repr

/-- A unit as the status reads it. `meaning` is `Loader.meaningStatus`'s value; `listed` the names of an `open`
    meaning (empty otherwise); `asserted` whether the unit's kind is `asserted`. -/
structure UnitView where
  id       : String
  meaning  : String
  listed   : List String
  asserted : Bool
  own      : Option Content
  set      : Option ActiveSet
  deriving DecidableEq, Repr

/-- The one list a unit's status and usage read: the active set's elaborated candidates, or the unit's own content. -/
def UnitView.reads (u : UnitView) : List Content :=
  match u.set with
  | some s => s.candidates.filterMap fun c => c
  | none => u.own.toList

/-- Whether `reads` is all the unit's content, so that a listed judgment it does not use is really unused. With an
    active set (which takes precedence, as in `reads`): the set has a reading and none is pending, whatever the unit's
    own content. Without one: the unit has its own content. -/
def UnitView.complete (u : UnitView) : Bool :=
  match u.set with
  | some s => !s.candidates.isEmpty && s.candidates.all Option.isSome
  | none => u.own.isSome

/-- Today's status: `w2SetStatus` with an active set, `w2Status` without. -/
def UnitView.legacy (u : UnitView) : String :=
  match u.set with
  | some s => VE.Discourse.Loader.w2SetStatus s.authored s.allAsserted
  | none => VE.Discourse.Loader.w2Status u.own.isSome u.meaning

/-- A unit's view: the active set is the one `Loader.foldStatus` finds in `Loader.activeOf`'s list. -/
def viewOf (active : List (VE.Discourse.FrontSet × List Bool))
    (candidates : VE.Discourse.FrontSet → List (Option Content))
    (unit meaning : String) (listed : List String) (asserted : Bool) (own : Option Content) : UnitView :=
  { id := unit, meaning, listed, asserted, own,
    set := (active.find? (·.1.unit == unit)).map fun (rs, kinds) =>
      ⟨rs.status == "authored", kinds.all id, candidates rs⟩ }

theorem viewOf_legacy (active candidates unit meaning listed asserted own) :
    (viewOf active candidates unit meaning listed asserted own).legacy =
      VE.Discourse.Loader.foldStatus active unit (VE.Discourse.Loader.w2Status own.isSome meaning)
```

The rules of the traversal, which JT-2's `candidates` function implements (8.1):

- **Active versions.** Only the active set is read: the one `Loader.activeOf` keeps, the latest version per unit.
  Superseded versions are not read.
- **Candidates.** Every reading of the active set, in order: an AST content is `some (.formula φ)`, a `norm` content is
  `some (.rule N)` (decoded as a norm unit is, `VE.Norms.Wire.decodeNorm`), a pending reading (`content: null`) is
  `none`: `reads` omits it and `complete` counts it. A norm candidate is never read through `readingsSets`' W2
  projection, which substitutes `top` for it (`lean/VE/Service/Document.lean:985-990`).
- **Authored choices.** An authored set has one signed reading (`compileSets` refuses any other, `Loader.lean:512-513`),
  so its list is that reading. A set holds 1 to 64 readings (`Loader.lean:510`), so on admitted documents `complete`
  with an active set is "no reading is pending".
- **History.** `rejected_history` and narrowings are not read: a narrowing does not change the active set's
  candidates, so a set some narrowing would keep to a judgment-free reading stays OPEN (the conservative side).

### 4.3 Status (D3)

```lean
/-- The status under `judgments@0`: the unit refusals of plan 2.1, item 6, in that order (the third only on a
    complete unit), then OPEN if the unit's list depends on a bound judgment, else today's status. -/
def status (defs : List VE.Definitions.Def) (J : List String) (u : UnitView) : Except String String := do
  let deps := dependsOnC defs J u.reads
  if u.meaning == "specified" then
    if let some j := deps.head? then throw s!"JudgmentNotChecked: {u.id} {j}"
  if u.meaning == "open" then
    if let some j := deps.find? (!u.listed.contains ·) then throw s!"JudgmentNotListed: {u.id} {j}"
    if u.complete then
      if let some j := u.listed.find? (fun j => J.contains j && !deps.contains j) then
        throw s!"JudgmentListedUnused: {u.id} {j}"
  pure (if deps.isEmpty then u.legacy else "OPEN")

/-- The value: judgment dependence forces OPEN; otherwise the legacy status applies. -/
theorem status_eq (defs J u s) (h : status defs J u = .ok s) :
    s = if dependsOnC defs J u.reads = [] then u.legacy else "OPEN"

/-- "Never present a judgment as checked": a judgment used in the unit's own content or its definitions. -/
theorem status_never_checked (defs J u s) (h : status defs J u = .ok s) (hd : dependsOnC defs J u.reads ≠ []) :
    s = "OPEN"

theorem status_checked (defs J u) (h : status defs J u = .ok "CHECKED") : dependsOnC defs J u.reads = []

/-- The refusals, exactly: `specified` content uses no judgment, and an `open` list names every judgment the content
    depends on and, when the unit is complete, no bound judgment it does not. -/
theorem status_ok_iff (defs J u) :
    (∃ s, status defs J u = .ok s) ↔
      (u.meaning = "specified" → dependsOnC defs J u.reads = []) ∧
      (u.meaning = "open" → (∀ j ∈ dependsOnC defs J u.reads, j ∈ u.listed) ∧
        (u.complete = true → ∀ j ∈ u.listed, j ∈ J → j ∈ dependsOnC defs J u.reads))

/-- Without bound judgments, today's status. -/
theorem status_legacy (defs u) : status defs [] u = .ok u.legacy
```

Dependence is syntactic use, directly or through W3 definitions (D3, D4); it does not follow one rule's outcome into
another rule's guard (F3, J-χ, section 13). A legacy OPEN needs no judgment (J-τ′'s units are OPEN with none), so
`status_eq` is not "OPEN exactly when dependent".

A unit with a `contextual` or `unformalised` meaning whose list depends on a judgment is OPEN too (`status_eq`): it
moves from LABELLED or UNFORMALISED to OPEN (J-υ). No refusal applies to it, since its meaning names no terms. A stated
`status` in the front matter that disagrees is refused by today's check ("unit status contradicts content, meaning, or
active reading set"), which JT-2 runs after this one (8.2).

`JudgmentListedUnused` applies only to a complete unit (F4): a unit with no own content and no active set, or whose
active set has a pending reading, reads nothing that could show a listed judgment unused, and is OPEN today and under
the profile alike. The first two checks apply whether or not the unit is complete, and so do today's checks on
asserted content.

### 4.4 The usage map (plan 2.2)

```lean
/-- For each bound judgment that some unit depends on, the ids of those units, in unit order; then the bound
    judgments no unit depends on. Both in declaration order. -/
def usageMap (defs : List VE.Definitions.Def) (J : List String) (units : List UnitView) :
    List (String × List String) × List String :=
  let rows := J.map fun j => (j, (units.filter fun u => (dependsOnC defs J u.reads).contains j).map (·.id))
  (rows.filter (!·.2.isEmpty), (rows.filter (·.2.isEmpty)).map (·.1))

theorem usageMap_sound (defs J units j ids) (h : (j, ids) ∈ (usageMap defs J units).1) (id) (hid : id ∈ ids) :
    ∃ u ∈ units, u.id = id ∧ j ∈ dependsOnC defs J u.reads

theorem usageMap_complete (defs J units u j) (hu : u ∈ units) (hj : j ∈ dependsOnC defs J u.reads) :
    ∃ ids, (j, ids) ∈ (usageMap defs J units).1 ∧ u.id ∈ ids

theorem usageMap_unused (defs J units j) :
    j ∈ (usageMap defs J units).2 ↔ j ∈ J ∧ ∀ u ∈ units, j ∉ dependsOnC defs J u.reads

/-- No row is empty. -/
theorem usageMap_rows (defs J units j ids) (h : (j, ids) ∈ (usageMap defs J units).1) : ids ≠ []

end VE.Judgments
```

A unit represented only by a reading set appears in the map through its elaborated candidates (J-ξ, J-ξ′); a pending
reading contributes nothing.

## 5. Criteria and "conflict-free, given …" (JT-4: `lean/VE/Judgments/Zone.lean`)

### 5.1 Criteria

A criterion is an asserted unit with its own formula content (no active reading set), over base predicates only, that
depends on a bound judgment. Its label is `judgment:<unit id>`. A reading-set candidate is never a criterion: an
undecided reading is not a premise. `base` is the layered route's situation vocabulary, `L.sitVocab.predicates`.

```lean
def criteria (defs : List VE.Definitions.Def) (J : List String) (base : List String) (units : List UnitView) :
    List (String × VE.Formula) :=
  units.filterMap fun u => match u.set, u.own with
    | none, some (.formula φ) =>
      if u.asserted && (VE.Norms.preds φ).all base.contains && !(dependsOn defs J [φ]).isEmpty then
        some ("judgment:" ++ u.id, φ)
      else none
    | _, _ => none

theorem criteria_iff (defs J base units l φ) :
    (l, φ) ∈ criteria defs J base units ↔
      ∃ u ∈ units, l = "judgment:" ++ u.id ∧ u.asserted = true ∧ u.set = none ∧ u.own = some (.formula φ) ∧
        (∀ p ∈ VE.Norms.preds φ, p ∈ base) ∧ dependsOn defs J [φ] ≠ []
```

An asserted judgment (D11, J-θ) is a criterion by this definition: the document asserts it, so the conditional answer
assumes it.

### 5.2 The conditional answer

```lean
/-- The layered source with the criteria after its own premises. Read only by the conditional conflict check
    (`conflictFreeX`, `firstFailureX`), never by `layeredElaborate` or `filledX` (F5). -/
def withCriteria (L : VE.NormDefaults.Wire.LayeredU) (C : List (String × VE.Formula)) :
    VE.NormDefaults.Wire.LayeredU :=
  { L with labelled := L.labelled ++ C }

/-- "Conflict-free, given <sentences>": accepted certificates over the background with the route's own premises `L.X`
    and the criteria. -/
theorem conflictFree_given (L : VE.NormDefaults.Wire.LayeredU) (C : List (String × VE.Formula)) (packages : Json)
    (h : VE.NormDefaults.Wire.conflictFreeX (withCriteria L C) packages = true) :
    VE.NormDefaults.Wire.ConflictFreeX.{0} L.U (L.X ++ C.map (·.2))

/-- The answer without additional judgment criteria implies the one given them; the converse fails (J-ι). -/
theorem conflictFree_given_mono (U : VE.NormDefaults.UDoc) (X C : List VE.Formula)
    (h : VE.NormDefaults.Wire.ConflictFreeX.{0} U X) : VE.NormDefaults.Wire.ConflictFreeX.{0} U (X ++ C)
```

Both were proved in the stub: `conflictFree_given` is `layered_conflict_sound` (`Layered.lean:227`) at
`withCriteria L C`. The certificates for the conditional answer are bound to the extended background, so the search
produces them separately; the answer without additional judgment criteria and its certificates are unchanged. The
display shows both lines (9.4).

Both layered answers assume `L.X`, the route's own premises (the soft norms' coherence premises and the rights'
limitations), so neither is worded "unconditional" or "whatever is judged" (A3). The line without additional judgment
criteria names those conditions, and the "given" line adds the criteria `C`. Only the plain norm-defaults line is
unconditional, "Conflict-free, whatever is judged.", and it cites `conflictFreeU_consistent`
(`lean/VE/NormDefaults/Status.lean:293`) itself; draft 1's `conflictFree_every_judgment` is dropped (it restated that
theorem with an unused hypothesis).

On the UDHR's plain norm-defaults route a `LayeredU` needs request R2 (plan 11); until then J-ι runs on the layered
route only.

## 6. Zone answers with judgments (JT-4: `lean/VE/Judgments/Zone.lean`, after WG-6)

### 6.1 The zone

WG-6's names below are its plan's (weighing-PLAN.md draft 4, 3.4), with request R1: `zoneOfOpens` takes the open names
explicitly, and `VE.Weighing.zoneOf L X M record r vs proposed` is `zoneOfOpens L X M (openNames L) record r vs
proposed` with `openNames L = VE.SoftNorms.decisionNames L.D ++ VE.NormDefaults.unsaidNames L.U`.

WG-6's `LeftToZ` is existential: nothing in it ties the shown `w₁`, `w₂` and `differ` to its two completions, so an
empty `differ` satisfied draft 1's `zone_leftTo` (A2). R1 therefore also asks WG-6 for the certified pair below, in its
file, over its own `completionOf M record w` (the completion `zone_notSaid_sound` already names), and for
`zone_leftTo_sound` to conclude it.

```lean
namespace VE.Weighing
open VE.Norms VE.NormDefaults

variable {α : Type} [DecidableEq α]

/-- R1: the pair a `left to` answer shows, certified. Both assignments complete `M` to admissible completions, their
    outcomes are opposite, they agree on every unsaid atom, and `differ` is exactly the atoms on which they differ. -/
def LeftToPair (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α) (unsaid : List String)
    (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool)) : Prop :=
  AdmissibleCompletion U X M opens record (completionOf M record w₁) ∧
    AdmissibleCompletion U X M opens record (completionOf M record w₂) ∧
    (∀ n ∈ unsaid, ∀ ws, completionOf M record w₁ n ws ↔ completionOf M record w₂ n ws) ∧
    OutcomeIn U M (completionOf M record w₁) r vs ∧ ¬ OutcomeIn U M (completionOf M record w₂) r vs ∧
    ∀ a, a ∈ differ ↔ ¬ (completionOf M record w₁ a.1 a.2 ↔ completionOf M record w₂ a.1 a.2)

/-- The certified pair witnesses `LeftToZ`. -/
theorem leftToPair_leftTo (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α) (unsaid : List String)
    (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool))
    (h : LeftToPair U X M opens record r vs unsaid differ w₁ w₂) :
    LeftToZ U X M opens record r vs unsaid

/-- An empty `differ` is never certified: the outcomes differ, so the two completions differ somewhere. -/
theorem leftToPair_differ_ne_nil (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α) (unsaid : List String)
    (w₁ w₂ : List ((String × List α) × Bool)) :
    ¬ LeftToPair U X M opens record r vs unsaid [] w₁ w₂

end VE.Weighing

namespace VE.Judgments
open VE.Norms VE.NormDefaults

variable {α : Type} [DecidableEq α]

/-- The open names with judgments: WG-6's, then the bound judgments. -/
def opens (L : VE.NormDefaults.Wire.LayeredU) (J : List String) : List String := VE.Weighing.openNames L ++ J

def zone (L : VE.NormDefaults.Wire.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (J : List String) (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) : VE.Weighing.ZoneAnswer α :=
  VE.Weighing.zoneOfOpens L X M (opens L J) record r vs proposed

theorem zone_settled (L : VE.NormDefaults.Wire.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt L.U.D 0)) (hb : backgroundValid L.U.D M = true) (J : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (hr : r ∈ L.U.D.T.regulated) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (proposed : List (List ((String × List α) × Bool)))
    (b : Bool) (w : List ((String × List α) × Bool))
    (hz : zone L X M J record r vs proposed = .settled b w) :
    VE.Weighing.SettledZ L.U (X.map (·.2)) M (opens L J) record r vs b

/-- The pair shown, certified: its two assignments complete `M` admissibly, agree on every unsaid atom and give
    different answers, and `differ` is exactly the atoms on which they differ; each is a decision atom or a judgment
    atom. -/
theorem zone_leftTo (L : VE.NormDefaults.Wire.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt L.U.D 0)) (hb : backgroundValid L.U.D M = true) (J : List String)
    (record : List ((String × List α) × Bool)) (r : Regulated) (hr : r ∈ L.U.D.T.regulated) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (proposed : List (List ((String × List α) × Bool)))
    (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool))
    (ns : Option (List ((String × List α) × Bool) × List ((String × List α) × Bool)))
    (hz : zone L X M J record r vs proposed = .notSettled (some (differ, w₁, w₂)) ns) :
    VE.Weighing.LeftToPair L.U (X.map (·.2)) M (opens L J) record r vs (unsaidNames L.U) differ w₁ w₂ ∧
      ∀ a ∈ differ, a.1 ∈ VE.SoftNorms.decisionNames L.D ∨ a.1 ∈ J

/-- Without judgments, WG-6's answer. -/
theorem zone_no_judgments (L : VE.NormDefaults.Wire.LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) :
    zone L X M [] record r vs proposed = VE.Weighing.zoneOf L X M record r vs proposed
```

`zone_no_judgments` was proved in the stub from R1's definition of `zoneOf`; `leftToPair_leftTo` and
`leftToPair_differ_ne_nil` were proved there too, over `completionOf` as an opaque stand-in. `zone_settled` and
`zone_leftTo` are WG-6's soundness theorems at `opens L J`; R1 asks WG-6 to state them over any `opens`, with
`zone_leftTo_sound` concluding `LeftToPair` (instead of `LeftToZ`, which follows by `leftToPair_leftTo`) and "every
differing atom is in `opens` and not unsaid" as its last conjunct, so that these follow by instantiation. The English
line of 9.4 ("these two admissible completions give different answers and differ on …") is what `LeftToPair` certifies.

JT-4 adds two mutations of a genuine `left to` answer (J-α's): a wrong witness (`w₂` replaced by `w₁`, or one atom of
a witness flipped) and an empty `differ`. In Lean each is a seeded bug in `zone` that fails J-α's zone fixture; through
the relay each is `CheckerUnavailable` (an empty `differ` is an empty row; a `differ` that is not exactly the atoms on
which the two shown witnesses differ is unbound) or changes nothing shown.

### 6.2 Deciders

```lean
/-- The deciders a `left to` answer names: the `decided_by` of each bound judgment with a differing atom, in
    declaration order, without repeats (F1). -/
def deciders (js : List Judgment) (differ : List (String × List α)) : List String :=
  ((js.filter fun j => differ.any (·.1 == j.name)).map (·.decidedBy)).eraseDups

theorem deciders_sound (js : List Judgment) (differ : List (String × List α)) (d : String)
    (h : d ∈ deciders js differ) : ∃ a ∈ differ, ∃ j ∈ js, j.name = a.1 ∧ j.decidedBy = d

theorem deciders_complete (js : List Judgment) (differ : List (String × List α)) (a : String × List α) (j : Judgment)
    (ha : a ∈ differ) (hj : j ∈ js) (hn : j.name = a.1) : j.decidedBy ∈ deciders js differ

end VE.Judgments
```

A decision atom (soft's `excepted`, `outweighs`, `off`) contributes no decider here; its decider is WG-7's, as today.

## 7. Undeclared evaluative words (JT-3, D15)

```lean
namespace VE.Judgments

/-- One catalogue row for an evaluative word, tied to its evaluative sense: the word, and the phrases in which it
    has another sense. JT-3 reads the rows from english-lean's single catalogue; there is no second list. -/
structure EvaluativeRow where
  word        : String
  otherSenses : List (List String)

def hasPhrase (ph ws : List String) : Bool :=
  (List.range (ws.length + 1)).any fun i => (ws.drop i).take ph.length == ph

def EvaluativeRow.matches (row : EvaluativeRow) (ws : List String) : Bool :=
  ws.contains row.word && !row.otherSenses.any (hasPhrase · ws)

/-- The base predicates whose words match a row and that are not bound, in declaration order. `preds` is every
    predicate of the base environment `baseEnv E defs` (W3-defined names excluded, regulated predicates included),
    each with its words (its name split at `_`, then its template's words, lower case), read by Lean from the
    environment. -/
def undeclaredEvaluative (rows : List EvaluativeRow) (preds : List (String × List String)) (J : List String) :
    List String :=
  (preds.filter fun (p, ws) => !J.contains p && rows.any (·.matches ws)).map (·.1)

theorem undeclaredEvaluative_iff (rows preds J p) :
    p ∈ undeclaredEvaluative rows preds J ↔
      ∃ ws, (p, ws) ∈ preds ∧ p ∉ J ∧ ∃ row ∈ rows, row.word ∈ ws ∧ ∀ ph ∈ row.otherSenses, ¬ ph <:+: ws

end VE.Judgments
```

The report says only "these words match the catalogue; review them". It is never a refusal, and it never says that a
unit uses no other judgment: a judgment written in words the catalogue lacks is not found.

Regulated predicates are scanned (F3′): D2 forbids binding one, so an evaluative word inside a regulated act
(`make_reasonable_efforts`; C u0052.s01's `good_judgment` if it were written as the act) is exactly the hidden judgment
this report exists to catch. Listing one does not make it admissible as a judgment: declaring it is still
`JudgmentRegulated` (11.7).

## 8. The document mode (JT-2, and JT-3's field)

### 8.1 The hook

In `VE.Service.Document.check`, when the environment lists `judgments@0`:

1. `Loader.openTermNames` is replaced by `Judgments.records E.rv (Loader.optionalList front "open_terms") E.data
   (some (formulaCheck E))`; `openNames` is `rs.map (·.1.name)` (`records_names`), so W2's texts come first.
2. `Judgments.admit E.rv.environment E.rv.definitions regulated rs`, where `regulated` is the predicates of
   `E.json`'s vocabulary with a `regulated` entry. Its error is the answer.
3. The units are compiled as today (`unitsOf`), the reading sets as today, and the fold as today
   (`Loader.foldStatus`).
4. Each unit's view: `viewOf active candidates u.id m listed (u.kind == .str "asserted") (u.content.map toContent)`,
   where `m` is `Loader.meaningStatus openNames u.meaning`'s value, `listed` the names of its `open` meaning, and
   `candidates` reads the active set's raw readings from the front matter by `(id, version)`, a pending reading as
   `none` (4.2).
5. `Judgments.status E.rv.definitions (names js) v` for each unit in unit order; the first error is the answer, and
   otherwise its value is the unit's status.
6. Then today's explicit-status check, and the rest of `check` unchanged.
7. The report gains `judgments` (8.3).

With the profile off, none of this runs and every answer is byte-identical (J-λ, `status_legacy`).

### 8.2 Diagnostics, and their order

| Code | Text | When | Fixture |
|---|---|---|---|
| (W2) | `invalid open-term arguments` | repeated `arguments` **without** the profile; unchanged text | J-ο (wire) |
| `JudgmentUnbound` | `JudgmentUnbound: <term>` | no base predicate of that name (a W3-defined name included) | J-δ, J-π |
| `JudgmentArguments` | `JudgmentArguments: <term>` | the base predicate's sorts are not `arguments` | J-ε |
| `JudgmentRegulated` | `JudgmentRegulated: <term>` | the environment declares the predicate regulated | J-ρ |
| `JudgmentCriterionAsUnit` | `JudgmentCriterionAsUnit: <term>` | `necessary` or `sufficient` is not empty | J-ζ, J-ζ′ |
| `JudgmentDecider` | `JudgmentDecider: <term>` | `decided_by` is `unstated` | J-η |
| `JudgmentNotChecked` | `JudgmentNotChecked: <unit> <term>` | meaning `specified`, and the unit's list depends on `<term>` (the first such judgment in declaration order) | J-β, J-γ, J-γ′ |
| `JudgmentNotListed` | `JudgmentNotListed: <unit> <term>` | meaning `open`, and `<term>` (the first in declaration order) is depended on but not listed | J-σ |
| `JudgmentListedUnused` | `JudgmentListedUnused: <unit> <term>` | meaning `open`, the unit is complete (`UnitView.complete`: with an active set, it has a reading and none is pending; without one, the unit has its own content), and `<term>` (the first in the meaning's list) is a bound judgment the unit's list does not depend on | J-τ, J-τ′ (e); not J-τ′ (a) to (d) |

Order: W2's schema check over the whole list first; then admission, the first faulty record in record order and its
first failing check in the table's order; then the units in unit order, each unit's three checks in the table's order
(the third only on a complete unit).

### 8.3 The report field `judgments` (JT-2)

```json
{"judgments": {"used": [{"term": "arbitrary", "units": ["u037", "u045a"]}], "unused": ["reasonable"]}}
```

Lean's `usageMap`, rendered: `used` from its first list, `unused` from its second. The response shape types every leaf
(strings, lists of strings), and the encoder theorem proves the rendered rows fit it. The Python relay checks the
schema and the binding only (R8):

- every `term` and every `unused` name is a declared open term of the request, and no name appears twice across
  `used` and `unused`;
- every declared open term appears exactly once;
- every unit id is a unit of the request, and no `units` list is empty or repeats an id;
- the order is Lean's (A5): the `used` terms in declaration order (the order of `open_terms`), the `unused` names in
  declaration order, and each `units` list in the request's unit order.

Fuzz tests in `tests/test_judgments_answer.py` drop, empty, retype, duplicate and reorder each member, and push a unit id
out of range: every mutant is `CheckerUnavailable` or changes nothing shown. A reordered list is `CheckerUnavailable` by
the order check; membership checks alone would let it through and change what is shown.

### 8.4 The report field `undeclared_evaluative` (JT-3)

`{"undeclared_evaluative": ["reasonable_grounds"]}`: `undeclaredEvaluative` over english-lean's catalogue rows. Typed
(a list of strings). The relay binds it: each name is a base predicate of the request's environment (not W3-defined;
a regulated predicate included, as in section 7) and is not a declared open term, and no name repeats. A genuine
answer naming the regulated `make_reasonable_efforts` (11.7) is accepted: JT-3's relay test records it. Fuzz tests
retype and rebind it as above.

## 9. English: wordings and their one reading

Every text below is a row for english-lean (JT-3) or WG-7's display (JT-4); JT-E1 gates them, and measures proxy
readability only (a model standing in for a reader), not human comprehension. `<atom>` is the predicate's template
filled with the sort nouns ("an act is arbitrary"); when two arguments share a sort, the second is written "a person
(the same or another)", so that the line does not say they differ. When the wording lint rejects the predicate's
template, there is no wording to fill. The line then shows today's fallback wording with identifiers, and no second
source of templates is added (phase 1: both of JT-0p's templates are rejected, 0.2 P-d).

### 9.1 Declarations (legend; also the authoring line that declares one)

| Text | Its one reading |
|---|---|
| "Whether an act is arbitrary is a judgment; the text does not say who makes it." | `arbitrary(act)` is a bound open term with `decided_by: unresolved_decider` |
| "Whether an act is arbitrary is a judgment for the governance function." | the same, with `decided_by: governance_function` |
| "Whether a person treats a person (the same or another) unfairly is a judgment; the text does not say who makes it." | `treats_unfairly(person, person)`, repeated sorts allowed under the profile (J-ο) |
| "The text mentions these points: the Declaration gives no test for arbitrariness." | the record's `factors`, shown and never used as premises |
| "Whether a measure is arbitrary is a judgment; the text does not say who makes it." and "Whether an interference is arbitrary is a judgment; the text does not say who makes it." | J-ω: two bound terms, `arbitrary_measure(measure)` and `arbitrary_interference(interference)`, which share the template "{0} is arbitrary"; one line per term. english-lean may group the two lines when the terms share their words and their decider. The grouped line is then a JT-E1 item, and its reading is still two records |

### 9.2 Unit lines

| Text | Its one reading |
|---|---|
| "Open: this uses the judgment whether an act is arbitrary." | the unit's list mentions `arbitrary`, directly or through a W3 definition (`dependsOnC`); it says nothing about whether the unit's truth turns on it |
| "Open: this uses the judgments whether an act is arbitrary and whether an act is unreasonable." | two judgments, in declaration order |

The line is neutral on purpose: the criterion unit "No arrest ordered by a court is arbitrary." uses the judgment to
limit it, and does not depend on it.

### 9.3 Sentences and the readings Lean keeps

| Sentence | Reading |
|---|---|
| "No one shall be subjected to arbitrary arrest." | a rule forbidding `subjects(p, a)` where `arrest(a) ∧ arbitrary(a)` (D10: a conjunction, no generated premise) |
| "No arrest ordered by a court is arbitrary." | `∀a:act. arrest(a) ∧ court_ordered(a) → ¬arbitrary(a)`: a criterion unit (5.1) |
| "An arrest ordered by a court is permitted." | a rule permitting `subjects(p, a)` where `arrest(a) ∧ court_ordered(a)` (J-ι) |
| "The family is a natural and fundamental group unit of society." | `natural_and_fundamental_group_unit(the_family)`, OPEN (D11). The source's "the … unit" (uniqueness) is presupposition's and is not represented; JT-0p claims no bytes for it |
| "No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality." | two readings of the adverb's scope, which differ: "arbitrarily" over both acts, or over the deprivation only (then every denial is forbidden). An open reading set with a model that separates them; the unit OPEN (J-ξ′) |
| "The risks … are just as real …" | "just" here means "equally": not the evaluative row (7, `["just", "as"]`) |

### 9.4 Zone, record and conflict lines (WG-7's display, JT-4)

| Text | What Lean checked |
|---|---|
| "Settled: whatever is judged here, the text requires …" | `zone_settled` with judgment atoms in the cone |
| "Left to no one the text names: these two admissible completions give different answers and differ on whether the arrest is arbitrary (the text does not say who makes it)." | `zone_leftTo`: the certified pair `LeftToPair` (the two shown completions are admissible, agree on every unsaid atom and give different answers), and exactly the atoms on which they differ, each with its decider (`deciders`); never that each atom alone controls the answer |
| "Given the court's judgment that the arrest is arbitrary, the text requires …" / "Ruled out: this judgment that … contradicts <premise sentence>." | WG-6's record answers |
| "Conflict-free, whatever is judged." | `conflictFreeU_consistent`, on the plain norm-defaults route only: every base situation, so every way of judging. The only unconditional line |
| "Conflict-free under the document's own conditions: <condition sentence>; …" | the layered route's CONFLICT-FREE, `ConflictFreeX L.U L.X`: every base situation that satisfies `L.X` (the soft norms' coherence premises and the rights' limitations), without additional judgment criteria. Never worded "whatever is judged" |
| "Conflict-free, given these sentences: No arrest ordered by a court is arbitrary." (when `L.X` is not empty: "Conflict-free under the document's own conditions and these sentences: …") | `conflictFree_given`, `ConflictFreeX L.U (L.X ++ C)`; shown beside the line without additional judgment criteria, never instead of it |
| "These rules conflict where an arrest ordered by a court is judged arbitrary." | a CONFLICT witness with `arbitrary(a)` true (J-ι) |

### 9.5 Refusal in authoring (JT-3)

"'Reasonable' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it ('In this document,
a reasonable limit means …')." In translation the same word is bound, never defined (D13), and an unbound one is only
reported (8.4).

## 10. Units and pilots

The pilot fixtures are plan 4.2's. Two points the statements fix:

- **JT-0p, u010.** Without the profile W2 refuses repeated arguments, so u010's record lists two distinct argument
  labels, never `["thing", "thing"]` (phase 1 used `["understanding", "realization"]`); the predicate keeps its sorts
  `(thing, thing)`. JT-5b replaces the labels by the sorts when the profile is switched on. No sort is invented beyond
  `thing`, which the UDHR's parts did not declare. The arity does not change. Phase 1's forecast confirms the labels'
  effect: without the profile the record would be `JudgmentArguments` (part 1), and u060's record is admitted (part 2).
- **JT-0p bytes, computed.** u010 alone: 4,792 + 132 = 4,924 B of 10,916 B, 43.90% → 45.11%. u060 is written and
  audited but its 66 B stay unclaimed (`missing_feature: presupposition`, `claimed: false`); draft 1's 45.71% is
  withdrawn. Phase 1 measured bar part A as PASS. The checker's OPEN bytes rise by 198 B, since u060 is OPEN in the
  document. The claim waits for the blind audit (bar part B, DEFERRED).
- **JT-5a, C u0052.s01.** `good_judgment` must sit in a guard, not be the regulated act (`JudgmentRegulated` otherwise).
  If it cannot sit in an admitted role, the limit is recorded; no declaration is removed to reach CHECKED. Phase 1:
  the run has no predicate `good_judgment`, so today the record is `JudgmentUnbound`; the judgment sits inside the
  regulated `judgment_use_required`.
- **JT-5r and JT-5b, the UDHR's `arbitrary`.** Four bound terms, one per sort (J-ω's shape), with usage rows per
  sort and per part. Part 1 has three: measure (u037), interference (u045a) and intrusion (u046). Part 2 has two:
  measure (u055's two readings) and deprivation (u064).

## 11. Fixtures, with the values the stub computed

The environment of 11.2 to 11.7: sorts `person`, `act`, `thing`; base predicates `arrest`, `arbitrary`,
`unreasonable`, `detention`, `unlawful`, `court_ordered`, `gives_serious_uplift`, `deprivation`, `denial` (all over
`act`), `natural_and_fundamental_group_unit(thing)`, `treats_unfairly(person, person)`; regulated `subjects(person,
act)`, `reports(person, act)` and `make_reasonable_efforts(person, act)`; W3 definitions `wrongful_detention(a) :↔
detention(a) ∧ arbitrary(a)` and `unlawful_detention(a) :↔ detention(a) ∧ unlawful(a)`; constant `the_family : thing`.
Records have `decided_by: unresolved_decider`, empty lists, unless a row says otherwise. Rules on `subjects` are typed in
`[act, person]`, so the act is `.var 0`. JT-1's `Examples.lean` reproduces each row as a `#guard`; JT-2 reproduces the
rows through the service, except the rows marked *internal*: inputs to one Lean function that W2 refuses on the wire
before that function runs (A1). They stay `#guard`s and are never replayed through the service.

J-ω (draft 3) has its own environment: sorts `measure`, `interference`; base predicates `measure_taken(measure)`,
`interference_with_privacy(interference)`, `arbitrary_measure(measure)` and `arbitrary_interference(interference)`.
It has no W3 definitions, and admission is given an empty regulated list.

### 11.1 W2 under the profile (on the wire, decoded by Lean's own readers)

| # | Record | Today's `openTermNames` | With the hunk, flag off | Flag on | `records` |
|---|---|---|---|---|---|
| J-ο (wire) | `treats_unfairly`, `["person", "person"]` | error `invalid open-term arguments` | the same error | ok `["treats_unfairly"]` | ok, one record, `(person, person)`, lengths 0, 0 |
| J-α (wire) | `arbitrary`, `["act"]`, one factor | ok `["arbitrary"]` | ok `["arbitrary"]` | ok `["arbitrary"]` | ok, factor kept |

### 11.2 Admission

| # | Records | `admit` |
|---|---|---|
| J-α | `arbitrary [act]` | ok `[arbitrary]` |
| J-δ | `reasonable_limitation [act]` | `JudgmentUnbound: reasonable_limitation` |
| J-π | `wrongful_detention [act]` (W3-defined; `E.predicates` gives `some [act]`) | `JudgmentUnbound: wrongful_detention` |
| J-ε | `arbitrary [person]` | `JudgmentArguments: arbitrary` |
| J-ρ | `subjects [person, act]` (regulated) | `JudgmentRegulated: subjects` |
| J-ζ | `arbitrary [act]`, one `necessary` | `JudgmentCriterionAsUnit: arbitrary` |
| J-ζ′ | `arbitrary [act]`, two `sufficient` | `JudgmentCriterionAsUnit: arbitrary` |
| J-η | `arbitrary [act]`, `decided_by: unstated` | `JudgmentDecider: arbitrary` |
| J-ο | `treats_unfairly [person, person]` | ok |
| J-ν | `gives_serious_uplift [act]` (a `scales@0` grade) | ok |
| J-θ | `natural_and_fundamental_group_unit [thing]` | ok |
| order 1 | `arbitrary [act]`, `reasonable_limitation [act]`, `unreasonable [person]` | `JudgmentUnbound: reasonable_limitation` (the first faulty record; the third, `JudgmentArguments`, is not reached) |
| order 2 | `arbitrary [person]`, `unstated`, one `necessary` | `JudgmentArguments: arbitrary` (the first failing check) |
| J-ω | `arbitrary_measure [measure]`, `arbitrary_interference [interference]` (J-ω's environment) | ok `[arbitrary_measure, arbitrary_interference]` |
| J-ω′ | `arbitrary_measure [interference]` (J-ω's environment) | `JudgmentArguments: arbitrary_measure` |

### 11.3 Status and usage

`J₁ = [arbitrary]`, `J₂ = [arbitrary, unreasonable]`. `u1`'s rule unless stated: forbid `subjects` where
`arrest(a) ∧ arbitrary(a)`.

| # | Unit | `status` | `usageMap` |
|---|---|---|---|
| J-α | `u1`, `open [arbitrary]` | ok `OPEN` | `([(arbitrary, [u1])], [])` |
| J-β | `u1`, `specified` | `JudgmentNotChecked: u1 arbitrary` | — |
| J-γ | formula `∀a. wrongful_detention(a) → ¬court_ordered(a)`, `specified` | `JudgmentNotChecked: u1 arbitrary` | — |
| J-γ′ | rule guarded by `wrongful_detention(a)`, `specified` | `JudgmentNotChecked: u1 arbitrary` | — |
| J-γ″ | formula `∀a. unlawful_detention(a) → ¬court_ordered(a)`, `specified` | ok `CHECKED` | — |
| J-θ | asserted formula `natural_and_fundamental_group_unit(the_family)`, `open [that term]` | ok `OPEN` | `([(natural_and_fundamental_group_unit, [u1])], [])` |
| J-μ | rule guarded by `arrest(a)` only, `specified`; `arbitrary` declared | ok `CHECKED` | `([], [arbitrary])` |
| J-ξ | `u055`, no content, `open [arbitrary]`; an active **authored** set with its one signed, asserted reading `∀a. deprivation(a) ∧ arbitrary(a) → ⊥` | ok `OPEN` (legacy `CHECKED`) | `([(arbitrary, [u055])], [])` |
| J-ξ′ | `u055`, no content, `open [arbitrary]`; an active **open** set of u055's two scopes, both asserted: wide `∀a. (deprivation(a) ∨ denial(a)) ∧ arbitrary(a) → ⊥`, narrow `∀a. (deprivation(a) ∧ arbitrary(a) → ⊥) ∧ (denial(a) → ⊥)`. Distinguishing model: one act `a`, `denial(a)` true, `deprivation` and `arbitrary` false: wide **true**, narrow **false** | ok `OPEN` (legacy `OPEN`) | `([(arbitrary, [u055])], [])` |
| J-υ | `u1`, meaning `contextual`; formula `∀a. arrest(a) ∧ arbitrary(a) → ⊥` | ok `OPEN` (legacy `LABELLED`) | — |
| J-σ | `J₂`; guard `arrest ∧ arbitrary ∧ unreasonable`; `open [arbitrary]` | `JudgmentNotListed: u1 unreasonable` | — |
| J-τ | `J₂`; guard `arrest ∧ arbitrary`; `open [arbitrary, unreasonable]` | `JudgmentListedUnused: u1 unreasonable` | — |
| J-τ′ (a) | `J₂`; `open [arbitrary, unreasonable]`; no own content, no active set | `complete` false; ok `OPEN` (legacy `OPEN`) | — |
| J-τ′ (b) | the same list; no own content; an open set whose two readings are both pending | `complete` false; ok `OPEN` (legacy `OPEN`) | — |
| J-τ′ (c) | the same list; no own content; an open set of J-υ's formula and one pending reading | `complete` false; ok `OPEN` (legacy `OPEN`) | — |
| J-τ′ (d) | the same list; own content J-α's rule, beneath an open set whose one reading is pending (the set takes precedence) | `complete` false; ok `OPEN` (legacy `OPEN`) | — |
| J-τ′ (e) | the same list; no own content; an authored set of J-υ's formula, asserted (complete) | `complete` true; `JudgmentListedUnused: u1 unreasonable` (legacy `CHECKED`) | — |
| J-λ | each of J-α, J-β, J-γ, J-θ, J-μ, J-ξ, J-ξ′, J-υ with `J = []` | `OPEN`, `CHECKED`, `CHECKED`, `OPEN`, `CHECKED`, `CHECKED`, `OPEN`, `LABELLED`: each equal to `legacy` | — |
| J-χ (F3) | J-α's `u1`, and `u2`: a rule on `reports` guarded by `subjects(p, a)`, `specified` | `u2`: ok `CHECKED` | `([(arbitrary, [u1])], [])` |
| J-ω | `J = [arbitrary_measure, arbitrary_interference]`, no definitions; `u037`: rule guarded by `measure_taken ∧ arbitrary_measure`, `open [arbitrary_measure]`; `u045a`: rule guarded by `interference_with_privacy ∧ arbitrary_interference`, `open [arbitrary_interference]` | each ok `OPEN` | `([(arbitrary_measure, [u037]), (arbitrary_interference, [u045a])], [])`: one row per term |

Dependence directly: `opensIn J₁ [arrest ∧ arbitrary] = [arbitrary]`, `opensIn J₁ [arrest] = []`,
`opensIn J₁ [J-γ's formula] = []`. Through definitions: `dependsOn defs J₁ [J-γ's formula] = [arbitrary]`,
`dependsOn [] J₁ [J-γ's formula] = []`.

### 11.4 Criteria

`base` = the base predicates of 11 (no regulated or defined name).

| Units | `criteria` |
|---|---|
| J-α's `u1` (a rule), `u2` "No arrest ordered by a court is arbitrary." (asserted), J-ξ's `u055` (a set), J-μ's unit | `[("judgment:u2", ∀a:act. arrest(a) ∧ court_ordered(a) → ¬arbitrary(a))]`; `u2`'s status ok `OPEN` |
| J-θ's `u1` | `[("judgment:u1", natural_and_fundamental_group_unit(the_family))]` |
| `u2` with kind not `asserted` | `[]` |
| an asserted unit over `wrongful_detention` (defined, so not in `base`) | `[]` |

### 11.5 J-ι on the norms route

Document: sorts `person`, `act`; base `arrest`, `arbitrary`, `court_ordered` over `act`; a permission `subjects(person,
act)`; rules `ban` (sign false, guard `arrest ∧ arbitrary`) and `allow` (sign true, guard `arrest ∧ court_ordered`),
with no precedence. `WellFormed` is true. On the situation with one person `p` and one act `a`, over the eight
assignments of `(arrest, arbitrary, court_ordered)` at `a`:

| Assignment | `conflict subjects` at `(p, a)` | the criterion |
|---|---|---|
| `(true, true, true)` | **true** | **false** |
| the seven others | false | true |

So without the criterion the document is in CONFLICT, with the witness "an arrest ordered by a court, judged arbitrary";
with the criterion as a premise, none of the eight assignments that satisfy it is a conflict (0 of 8). The general
answer "conflict-free, given …" is `conflictFree_given` on a certificate JT-4's search supplies; the stub does not
produce that certificate.

### 11.6 Zone (JT-4; values computed there, on WG-6)

| # | Expected |
|---|---|
| J-α | at one person, one arrest: `left to` (no one named), differing atom `arbitrary(a)`, deciders `[unresolved_decider]`; record `arbitrary(a)` → settled no; record `¬arbitrary(a)` → not said |
| J-κ | 17 bound judgments in one guard over one tuple: 17 open atoms, over WG-6's limit 16 → `unknown`, budget |
| J-μ | settled whatever is judged |
| J-ν | `gives_serious_uplift`'s atoms are judgment atoms in the zone |
| J-α (pair) | the `left to` answer's `differ` and witnesses satisfy `LeftToPair`; the two mutations of 6.1 (a wrong witness, an empty `differ`) each fail the fixture in Lean and are `CheckerUnavailable` through the relay |
| J-ι | "Conflict-free, given …" beside the answer without additional judgment criteria (CONFLICT), never instead of it |

### 11.7 Deciders and undeclared words

| Input | Value |
|---|---|
| `deciders [arbitrary ↦ unresolved_decider, reasonable_grounds ↦ we] [arbitrary(a), soft__excepted__r1(a)]` | `[unresolved_decider]` |
| the same records, `[reasonable_grounds(s)]` | `[we]` |
| the same records, `[soft__excepted__r1(a)]` (a decision atom only) | `[]` |
| *internal*: two records named `arbitrary` (`court`, `unresolved_decider`), `[arbitrary(a)]` (W2 refuses the repeated name, "duplicate or invalid open term") | `deciders`: `[court, unresolved_decider]`; draft 1's first-occurrence form: `[court]` (F1) |
| `undeclaredEvaluative` with rows `reasonable`, `arbitrary`, `due` (not "due date", "due to"), `just` (not "just as"), `necessary` (not "necessary condition"), `effective` (not "effective date"); predicates `reasonable_grounds`, `due_date`, `arbitrary`, `just_as_real`, `just_requirement`, `necessary_condition`, `arrest`; `J = [arbitrary]` | `[reasonable_grounds, just_requirement]` |
| the same, `J = []` | `[reasonable_grounds, arbitrary, just_requirement]` |
| F3′, regulated: `(baseEnv E defs).predicates make_reasonable_efforts` | `some [person, act]`: a regulated predicate stays in the base environment |
| the rows and `J = [arbitrary]` above, with the regulated `make_reasonable_efforts` (words `make reasonable efforts`) appended to the predicates | `[reasonable_grounds, just_requirement, make_reasonable_efforts]`; the relay accepts this answer (8.4) |
| `admit` of `make_reasonable_efforts [person, act]` | `JudgmentRegulated: make_reasonable_efforts`: listing it for review does not make it admissible |

### 11.8 Each "exactly when" claim, both directions

| Claim | Holds (→) | Fails (←) |
|---|---|---|
| `openTermNames_sorts` (only relaxes) | J-ο wire: off refuses, on admits | J-α wire: all three agree |
| `faultOf_none_iff` / `admit_ok_iff` | J-α, J-ο, J-ν, J-θ, J-ω admitted | one fixture per conjunct: J-δ and J-π (base predicate), J-ε and J-ω′ (sorts), J-ρ (regulated), J-ζ (`necessary`), J-ζ′ (`sufficient`), J-η (decider) |
| `opensIn_iff` | `arrest ∧ arbitrary` gives `[arbitrary]` | `arrest` gives `[]` |
| `dependsOn_iff` | J-α (direct), J-γ and J-γ′ (through a definition) | J-γ″ (a definition that does not reach), `dependsOn []` on J-γ's formula |
| `status_eq` (judgment dependence forces OPEN; otherwise the legacy status applies) | dependence: J-α, J-θ, J-ξ (legacy `CHECKED`), J-ξ′, J-υ (legacy `LABELLED`), u2 of 11.4: OPEN | no dependence: J-μ, J-γ″ (legacy `CHECKED`), J-τ′ (a), (b), (d) (legacy `OPEN`, with no judgment): the legacy value |
| `status_ok_iff` (refused exactly when) | J-α, J-θ, J-μ, J-ξ, J-ξ′, J-υ accepted; J-τ′ (a) to (d) accepted (not complete, so a listed judgment they do not use is no refusal) | J-β, J-γ, J-γ′ (`specified`), J-σ (not listed), J-τ and J-τ′ (e) (complete, listed, unused) |
| `usageMap_unused` | J-μ: `arbitrary` unused | J-α: `arbitrary` used |
| `usageMap_sound` / `_complete` | J-α, J-θ, J-ξ, J-ξ′ (a set-only unit is listed), J-ω (one row per term) | J-χ's `u2` (no dependence) is not listed; in J-ω, `u045a` is not in `arbitrary_measure`'s row |
| `criteria_iff` | `u2` and J-θ's unit | a rule unit, a set unit, a CHECKED unit, a non-asserted unit, a unit over a defined name |
| `deciders_sound` / `_complete` | `[unresolved_decider]`, `[we]` | a decision atom only: `[]` |
| `undeclaredEvaluative_iff` | `reasonable_grounds`, `just_requirement`, the regulated `make_reasonable_efforts` (and `arbitrary` when unbound) | `due_date`, `just_as_real`, `necessary_condition` (other sense), `arrest` (no row), `arbitrary` (bound) |
| `conflictFree_given_mono` (one direction only) | — | J-ι: conflict-free given the criterion, not without it |
| `zone_leftTo` (the certified pair, JT-4) | J-α's pair | a wrong witness, an empty `differ` (`leftToPair_differ_ne_nil`) |

## 12. Obligations

| Statement | In the stub | Owner |
|---|---|---|
| `records_refuse`, `faultOf_none_iff`, `opensIn_iff`, `opensIn_isEmpty`, `nodeOpen_eq`, `dependsOn_no_defs`, `viewOf_legacy`, `status_legacy`, `usageMap_unused`, `conflictFree_given`, `conflictFree_given_mono`, `zone_no_judgments` | proved | JT-1, JT-4 restate them in the product files |
| `leftToPair_leftTo`, `leftToPair_differ_ne_nil` | proved, over `completionOf` as a stand-in | WG-6 with `LeftToPair` (R1); JT-4 if WG-6 lands without them |
| `status_never_checked`, `status_checked` | proved from `status_eq` | JT-1 |
| `openTermNames_sorts`, `records_names`, `admit_ok_iff`, `admit_first_fault`, `dependsOn_iff`, `status_eq`, `status_ok_iff`, `usageMap_sound`, `usageMap_complete`, `usageMap_rows` | stated | JT-1 |
| `criteria_iff`, `deciders_sound`, `deciders_complete` | stated | JT-4 |
| `zone_settled`, `zone_leftTo` (concluding `LeftToPair`) | stated over WG-6's planned names | JT-4, by instantiating WG-6's theorems (R1) |
| `undeclaredEvaluative_iff` | stated | JT-3 |

For the audit (`lean/audit.py`): the function name `admit` is allowed (`audit.py:30-34`, applied as `admit E …`), and
no product file may declare `zoneOfOpens` or `completionOf` as the stub did (`opaque` stand-ins): WG-6 defines them.

## 13. What is not claimed

- No theorem says a judgment is right, that a decider weighed the factors, or where a vague boundary lies.
- **Declared terms only.** An evaluative word written as an ordinary base predicate is not bound, and its unit can be
  CHECKED. `undeclared_evaluative` lists catalogue matches for review; it never says a unit has no other judgment.
- **Rule chains are not tracked** (F3, settled by the statement review). Dependence is syntactic use, directly or
  through W3 definitions; it does not follow one rule's outcome into another rule's guard. So an outcome downstream can
  still vary with a judgment while its unit is CHECKED: J-χ's `u2` reads `subjects`, which `u1` decides on `arbitrary`.
  `status_never_checked` covers a judgment in the unit's own content or its definitions only. The zone answer (JT-4)
  is the full answer at a situation, and JT-5 records each such unit.
- **`left to` is a witnessed pair.** The listed atoms are exactly those on which the two shown admissible completions
  differ (`LeftToPair`); no minimality and no claim that each atom alone controls the answer.
- **"Given" is not "whatever".** `conflictFree_given` assumes the criterion sentences, on top of the layered route's
  own premises `L.X`; the answer without additional judgment criteria is reported apart and is never replaced. Only the
  plain route's `conflictFreeU_consistent` is unconditional.
- No completeness beyond WG-6's budget: beyond it the answer is UNKNOWN with the budget as reason.
- No claim that a criterion written as a unit is faithful to the source: that is the audit's job.
- JT-E1's result is proxy readability, not human comprehension.

## Change log

| Date | Draft | Change |
|---|---|---|
| 2026-10-14 | 1 | First statement spec, from plan draft 2: W2's profile flag, records and base-predicate admission, the shared scan with rights' switch, one traversal per unit, status, usage map, criteria and the conditional conflict answer, zone answers on WG-6's planned names, deciders, the undeclared-word report; diagnostics, English wordings, fixture values computed in the stub; findings F1 to F8 (F3 open). |
| 2026-10-14 | 2 | The statement review's joint position (FIX; `manage-agents/debates/judgment-terms-spec/`, section 0.1). A1: J-ξ an authored set with one reading, J-ξ′ an open set of u055's two scopes with a separating model, "order 1" ends with `unreasonable [person]`, *internal* rows marked. A2: `zone_leftTo` concludes R1's certified pair `LeftToPair` (with `leftToPair_leftTo` and `leftToPair_differ_ne_nil`, proved), wrong-witness and empty-`differ` mutations. A3: unconditional wording only for `conflictFreeU_consistent`; layered lines name `L.X` and say "without additional judgment criteria"; `conflictFree_unconditional_given` renamed `conflictFree_given_mono`. A4: `status_eq` worded "judgment dependence forces OPEN; otherwise the legacy status applies". A5: the relay checks declaration and unit order. F2: J-υ (LABELLED → OPEN). F3: settled, definition-only with the narrower guarantee. F3′: regulated predicates scanned and accepted by the relay, fixture rows. F4: `UnitView.complete` guards `JudgmentListedUnused`, pending readings kept as `none`; J-τ′ (a) to (e). Stub re-elaborated with no error; every changed fixture recomputed by `#eval`. |
| 2026-10-14 | 3 | Phase 1 (`docs/research/judgment-terms-phase1.md`), with plan draft 4. New 0.2 (P-a to P-e: phase 1's results and why no statement changes). Fixture J-ω (and J-ω′): one word over two sorts is two bound terms, one usage row each, and the other sort is refused as `JudgmentArguments` (11.2, 11.3, 11.8; 9.1's declaration rows). 9: the fallback when the lint rejects a template. 10: the pilot points with phase 1's measurements, and JT-5 split into JT-5a, JT-5r and JT-5b. Stub re-elaborated with no error; earlier outputs unchanged; J-ω's values by `#eval`. |
