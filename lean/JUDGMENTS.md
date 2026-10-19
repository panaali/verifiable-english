# Judgment terms in Lean (`lean/VE/Judgments/*`)

Specification: [docs/spec/judgment-terms.md](../docs/spec/judgment-terms.md) sections 1 to 4 (draft 3), and
[docs/spec/judgment-terms-PLAN.md](../docs/spec/judgment-terms-PLAN.md) batch JT-1 (draft 4). This file says, in plain
words, what each definition does and what each theorem proves. `lean/audit.py` audits every theorem: no `sorry`, only
`propext`, `Classical.choice` and `Quot.sound`.

A *judgment term* is a word such as "arbitrary" or "reasonable" whose application the text leaves to someone's
judgment. Under the profile `judgments@0` it is written as an ordinary W2 open term whose name is a predicate of the
environment. Lean checks that the term is bound to that predicate. Nothing here checks a judgment itself.

Item jt-1 built the records, admission and the shared scan; item jt-1b adds dependence, the unit status and the
usage map (spec section 4, `Status.lean`). No service mode, route or document check calls this code yet; the
document mode switches it on in JT-2.

## Files

| File | Contents |
|---|---|
| `Decl.lean` | `Judgment`, `Rec`, `records`, `baseEnv`, `faultOf`, `admit`, `names`; W2's flag theorem `openTermNames_sorts` |
| `Scan.lean` | `opensIn`, the one scan of open names in formulas |
| `Status.lean` | `Content`, `dependsOn`, `dependsOnC`, `UnitView`, `viewOf`, `status`, `usageMap`, and their theorems |
| `Examples.lean` | the fixtures of spec 11.1 to 11.3 and 11.9, as `#guard`s |
| `../Discourse/Loader.lean` | one change: `openTermNames` takes `sorts` (default off) |
| `../Rights/Run.lean` | rights' `nodeOpen` calls `opensIn`; `nodeOpen_eq` |

## W2 under the profile (spec 1)

`Loader.openTermNames` is W2's one validator of the `open_terms` front matter. It gains one optional flag, `sorts`.
With the flag, a record's `arguments` may repeat: they are the predicate's sorts, and a judgment between two people
has `["person", "person"]`. Without it, W2 refuses a repeated argument as before, with its own text ("invalid
open-term arguments"). Every existing caller passes nothing, so what it accepts, refuses and says is unchanged. Only
`records` passes the flag.

- `openTermNames_sorts`: the flag only relaxes. Whatever W2 accepts without the flag, it accepts with the flag, with
  the same names.
- `openTermNames_length`: W2 gives one name per record.
- `foldlM_ok_mono`, `foldlM_ok_length`: two list facts the proofs above use. A fold whose steps keep every answer
  keeps the fold's answer; a fold whose steps each add one name adds one name per item.

## Records (spec 2.1)

- `Judgment`: a bound judgment's name, its sorts (`arguments`), who decides it (`decidedBy`) and the points the text
  mentions (`factors`). The factors are shown to readers; they are never premises.
- `Rec`: one record as written: the judgment, and how many `necessary` and `sufficient` formulas it lists.
- `records`: reads `open_terms` under the profile. W2's check runs first, with the flag on. If it refuses, the refusal
  is W2's, unchanged. Otherwise `records` reads the fields W2 has just checked.
- `records_names`: the names `records` returns are W2's names, in W2's order.
- `records_refuse`: when W2 refuses, `records` gives the same refusal.

## Admission (spec 2.2)

- `baseEnv E defs`: the environment without the document's W3 definitions. A defined name such as
  `wrongful_detention` is not a base predicate here.
- `faultOf`: the first thing wrong with one record, checked in this order:
  1. `JudgmentUnbound: <term>`: no base predicate has the term's name;
  2. `JudgmentArguments: <term>`: the predicate's sorts are not the record's `arguments`;
  3. `JudgmentRegulated: <term>`: a rule regulates the predicate (one atom has one role);
  4. `JudgmentCriterionAsUnit: <term>`: `necessary` or `sufficient` is not empty (a criterion the text states is a
     sentence of its own);
  5. `JudgmentDecider: <term>`: `decided_by` is `unstated` (the one spelling for "no one named" is
     `unresolved_decider`).
- `admit`: the first fault in record order, or the judgments.
- `names`: the judgments' names.
- `faultOf_none_iff`: a record is admitted exactly when its name is a base predicate with its sorts, no rule regulates
  it, it lists no criteria, and its decider is not `unstated`.
- `admit_ok_iff`: admission succeeds exactly when no record has a fault, and then it returns the records' judgments in
  order.
- `admit_first_fault`: when admission fails, the fault is the first faulty record's first failing check, and every
  record before it is admitted.

One word over several sorts is one bound term per sort (fixture J-ω): `arbitrary_measure` over measures and
`arbitrary_interference` over interferences are two records, and one record cannot stand for the other sort.

## The one scan (spec 3)

- `opensIn J fs`: the names of `J` that the formulas `fs` mention, in `J`'s order. It is the one scan of open names in
  formulas. `Scan.lean` imports only `VE.Norms.Tree`, so rights can import it.
- `opensIn_iff`: a name is found exactly when it is in `J` and some formula mentions it.
- `opensIn_isEmpty`: the scan finds something exactly when some formula mentions some name of `J`.

Rights' `nodeOpen` (is a rule's line open?) now asks the shared scan whether the guard or a carve-out mentions an open
name, instead of scanning them itself.

- `nodeOpen_eq` (in `Rights/Run.lean`): `nodeOpen` equals the body it had before the switch, so rights' answers and
  output bytes do not move. Rights' other checks (the default mode, the alterable parties, limitations and bars) are
  not touched.

## Dependence, status and the usage map (spec 4)

`Status.lean` decides a unit's status under the profile. It does not read the document format: the document mode
(JT-2) hands it each unit as a `UnitView`.

### Dependence

A unit *depends on* a bound judgment when its content uses the judgment's name, either directly or through the
document's W3 definitions. If `wrongful_detention` is defined as "detention that is arbitrary", a sentence about
wrongful detention depends on `arbitrary`. Dependence is about the words used. It does not follow one rule's outcome
into another rule's guard (fixture J-χ).

- `Content`: what one unit says, either a formula or a rule. A rule is read through its guard and its carve-outs, as
  rights reads it.
- `Content.formulas`: the formulas a content reads.
- `defEdges defs`: the definition graph. Each defined name points at every predicate its body uses.
- `reachedBodies defs fs`: the bodies of the definitions the formulas mention, directly or through other
  definitions.
- `dependsOn defs J fs`: the bound judgments `J` that the formulas use, directly or through definitions. It runs the
  one shared scan, `opensIn`, over the formulas and the bodies they reach.
- `dependsOnC defs J cs`: the same, for a list of contents.
- `dependsOn_iff`: a judgment is found exactly when it is bound and some formula uses a predicate that is the
  judgment, or that leads to it through a chain of definitions.
- `dependsOn_no_defs`: with no definitions, dependence is the direct scan.
- Helpers: `path_last` (a chain of definitions ends with one last step), `mem_defEdges` (what an edge of the graph
  means), `dependsOnC_sub` (what a list of contents depends on is bound).

### One reading of each unit

Each unit is read once, and its status and the usage map read the same list.

- `ActiveSet`: a unit's active reading set, as the loader keeps it. It records whether the set is authored, whether
  every reading is asserted, and the readings in order. A reading still pending is kept as "none".
- `UnitView`: one unit as the status reads it: its id, its meaning (`specified`, `open`, `contextual` or
  `unformalised`), the judgment names an `open` meaning lists, whether it is asserted, its own content, and its active
  set if it has one.
- `UnitView.reads`: what the unit says. With an active set, that set's readings (pending ones left out); otherwise the
  unit's own content. The active set takes precedence.
- `UnitView.complete`: whether that list is everything the unit says. With an active set, it has at least one reading
  and none is pending; without one, the unit has its own content.
- `UnitView.legacy`: the status the unit has today, without the profile.
- `viewOf`: builds a unit's view, taking the active set the loader found for that unit.
- `viewOf_legacy`: the view's legacy status is exactly the status the loader computes today.

### Status

- `status defs J u`: the unit's status under the profile. Three refusals come first, in this order:
  1. `JudgmentNotChecked: <unit> <term>`: a `specified` unit uses a judgment. A judgment cannot be checked.
  2. `JudgmentNotListed: <unit> <term>`: an `open` unit uses a judgment its meaning does not list.
  3. `JudgmentListedUnused: <unit> <term>`: an `open` unit lists a bound judgment it does not use. This is checked
     only when the unit is complete, since a pending reading might still use it.

  If no refusal applies, a unit that uses a judgment is OPEN, and any other unit keeps today's status.
- `status_eq`: the status is OPEN when the unit uses a judgment, and today's status otherwise. A unit that uses no
  judgment can still be OPEN today.
- `status_never_checked`: a unit that uses a judgment, in its own content or through a definition, is never shown as
  checked. Its status is OPEN.
- `status_checked`: a unit shown as CHECKED uses no judgment.
- `status_ok_iff`: the exact conditions for no refusal. A `specified` unit uses no judgment. An `open` unit lists
  every judgment it uses, and, when complete, uses every bound judgment it lists.
- `status_legacy`: with no bound judgments, every unit keeps today's status. Documents without the profile do not
  change.

### The usage map

- `usageMap defs J units`: for each bound judgment, the units that use it, in unit order. The bound judgments that no
  unit uses are listed separately. Both lists keep declaration order.
- `usageMap_sound`: every unit the map names really uses that judgment.
- `usageMap_complete`: every unit that uses a judgment is named in that judgment's row.
- `usageMap_unused`: a judgment is in the unused list exactly when it is bound and no unit uses it.
- `usageMap_rows`: no row of the map is empty.

### Removing an unused judgment

- `dependsOnC_remove`: removing a bound judgment that the content does not use leaves the dependence unchanged.
- `status_remove_unused`: a judgment that the unit does not use and does not list can be removed without changing the
  unit's status or its refusal. Both conditions are needed. Removing a used judgment can hide `JudgmentNotChecked`
  (J-β), and removing a listed one can hide `JudgmentListedUnused` (J-τ).
- Helpers: `filter_remove` (a list fact), `find_congr_mem` (two searches agree when their tests agree on the list).

## Fixtures (`Examples.lean`)

Each `#guard` reproduces one row of spec 11 with the value the spec's stub computed:

- 11.1, on the wire, through Lean's own environment and front-matter readers: J-ο (`["person", "person"]` is
  refused without the flag, with W2's text, and admitted with it); J-α (`["act"]`, the same answer all three ways,
  with the factor kept by `records`).
- 11.2: J-α, J-δ, J-π, J-ε, J-ρ, J-ζ, J-ζ′, J-η, J-ο, J-ν, J-θ, "order 1" (record order), "order 2" (check order),
  J-ω and J-ω′. Three more pin each later check of order 2 under the next one's fault. J-ω's admitted records
  also check `names`, by a `#guard` and the theorem `names_omega` (by `decide`).
- 11.3, the direct scan: `opensIn` on `arrest ∧ arbitrary`, `arrest` and J-γ's formula, and the order of its answer;
  dependence through definitions, with and without them.
- 11.3, status and usage: J-α, J-β, J-γ, J-γ′, J-γ″, J-θ, J-μ, J-ξ, J-ξ′ (with the model that tells its two readings
  apart), J-υ, J-σ, J-τ, J-τ′ (a) to (e), J-λ, J-χ, the asserted criterion unit of 11.4, and J-ω's two usage rows.
- 11.9, removal: J-β, J-τ and J-μ, with and without the removed judgment. Each rule fixture that JT-2 replays is also
  a norm document that `VE.Norms.validate` accepts; draft 3's J-ω is refused (`UnknownSymbol: regulated predicate
  subjects`); each formula fixture type-checks in 11's environment.
- Rows this build adds, which are in no table of spec 11 and are not replayed: a rule whose carve-out alone uses
  `arbitrary` (`formulas_carve`), a definition reached through another (`reachedBodies_chain`), and `viewOf` building
  J-ξ's view (`viewOf_xi`). Each pins a definition that no spec row tests on its own.

## Deviations from the plan

- The plan's JT-1 was built in two items, to keep each merge-sized: jt-1 (records, admission, the scan) and jt-1b
  (`Status.lean` and its fixtures); see `docs/judgment-terms/jt-1/REPORT.md` and `docs/judgment-terms/jt-1b/REPORT.md`.
- The plan asks for a rehash of the frozen-sources inventory after the `Loader.lean` and `Rights/Run.lean` hunks. The
  narrow freeze (architecture decision D2) no longer lists either file, so the inventory does not change
  (`python3 VE/Route/frozen.py` passes).
