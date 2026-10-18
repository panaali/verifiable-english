# Judgment terms in Lean (`lean/VE/Judgments/*`)

Specification: [docs/spec/judgment-terms.md](../docs/spec/judgment-terms.md) sections 1 to 3 (draft 3), and
[docs/spec/judgment-terms-PLAN.md](../docs/spec/judgment-terms-PLAN.md) batch JT-1 (draft 4). This file says, in plain
words, what each definition does and what each theorem proves. `lean/audit.py` audits every theorem: no `sorry`, only
`propext`, `Classical.choice` and `Quot.sound`.

A *judgment term* is a word such as "arbitrary" or "reasonable" whose application the text leaves to someone's
judgment. Under the profile `judgments@0` it is written as an ordinary W2 open term whose name is a predicate of the
environment. Lean checks that the term is bound to that predicate. Nothing here checks a judgment itself.

This item (jt-1) builds the records, admission and the shared scan. Dependence, the unit status and the usage map
(spec section 4, `Status.lean`) are item jt-1b. No service mode, route or document check calls this code yet; the
document mode switches it on in JT-2.

## Files

| File | Contents |
|---|---|
| `Decl.lean` | `Judgment`, `Rec`, `records`, `baseEnv`, `faultOf`, `admit`, `names`; W2's flag theorem `openTermNames_sorts` |
| `Scan.lean` | `opensIn`, the one scan of open names in formulas |
| `Examples.lean` | the fixtures of spec 11.1, 11.2 and the direct scan of 11.3, as `#guard`s |
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

## Fixtures (`Examples.lean`)

Each `#guard` reproduces one row of spec 11 with the value the spec's stub computed:

- 11.1, on the wire, through Lean's own environment and front-matter readers: J-ο (`["person", "person"]` is
  refused without the flag, with W2's text, and admitted with it); J-α (`["act"]`, the same answer all three ways,
  with the factor kept by `records`).
- 11.2: J-α, J-δ, J-π, J-ε, J-ρ, J-ζ, J-ζ′, J-η, J-ο, J-ν, J-θ, "order 1" (record order), "order 2" (check order),
  J-ω and J-ω′.
- 11.3, the direct scan: `opensIn` on `arrest ∧ arbitrary`, `arrest` and J-γ's formula, and the order of its answer.

## Deviations from the plan

- The plan's JT-1 also lists `Status.lean`: dependence through W3 definitions, the one traversal per unit, the status,
  the usage map and removal (spec 4), with fixtures J-α to J-χ of 11.3, the removal rows and the norms check of every
  replayed rule fixture of 11.9. They are item jt-1b, to keep this item merge-sized; see
  `docs/judgment-terms/jt-1/REPORT.md`.
- The plan asks for a rehash of the frozen-sources inventory after the `Loader.lean` and `Rights/Run.lean` hunks. The
  narrow freeze (architecture decision D2) no longer lists either file, so the inventory does not change
  (`python3 VE/Route/frozen.py` passes).
