# P0-Py contracts and status

This file records the Python/Rust side of PLAN-EXPAND2.md §3. It does not
change legacy `ve.core@0` or `ve.core@0.1` identities or the English report.

## Wire decisions for P0-Lean

- New envelope: `language: "ve.core@0.2"`, sorted unique `profiles`, and
  `spec_revision: "ve-v0.2-expand2-2026-09-25"`. The base profile
  `relational-fol@0` is required. The identity suffix is
  `v0.2:<comma-joined sorted profiles>`; for example
  `ve-environment-v0.2:relational-fol@0\n`. The same suffix is used for
  model, meaning and source IDs. No existing identity suffix changes.
- Checker family dispatch is FOL, closure, closure+n-ary or order. The
  combination `nary@0` without `closure@0` is rejected until a separately
  gated checker exists. `order@0` cannot combine with either closure or n-ary.
  Statement profiles in the registry are `documents@1`, `definitions@0`,
  `norms@0`, `data@0` and `time@0`.
- For P0 literal cases, a constant with sort `$string` is declared under
  `vocabulary.constants`; its description is optional on the new route.
  `$string` is a built-in model sort with an explicit
  `domains["$string"]` array. It cannot be quantified over. Every pair of
  declared literal constants contributes `Not(Eq(Const(a), Const(b)))` to
  `Background`, in sorted name order; models in which they denote the same
  entity fail with `InvalidModel`, generator `literals`. The other hook slots
  are deliberately empty until W5, W3 and W1 provide their schemas.
- Certificate premises are `Background(env)` followed by the caller's ordered
  premises. A certificate's premise meaning IDs bind that expanded list.
  Python omits the default `Claim.label == "asserted"` on the wire and in the
  claim hash, preserving old graph bytes. A non-default label is a claim-ID and
  graph-ID input. New composition assumption entries for background have
  `label: "background:<generator>"`, `ast`, and `meaning_id`.
- The two fixture families are `conformance/elaborated-document.json` and
  `conformance/invalid-background-model.json`. The latter has one active
  literal case and two explicitly pending cases for W5 and W3.

## Conservative readings of ambiguous points

1. The plan does not name an exact v0.2 spec revision or profile separator.
   Python and Rust use the revision and comma-separated suffix above. Lean
   must match these bytes before an integrated route is enabled.
2. The plan calls `$string` a built-in sort but does not state its model wire
   domain. P0 uses an explicit `$string` domain, while forbidding binders over
   it. This makes finite models and literal non-aliasing directly checkable.
3. `nary@0` alone has no listed checker family; P0 rejects it. The allowed
   combined route is `closure@0` plus `nary@0`, gated by W4.
4. An English source longer than `MAX_NODES` characters is rejected with a
   named derivation-budget diagnostic before Earley parsing. This conservative
   admission guard bounds the untrusted parser's input as well as its result.

## P0-Py status

- Implemented: the v0.2 envelope/profile registry in Python and Rust;
  literal Background hooks and model validity; premise insertion for Python
  tableau proof and replay; background-aware Python/Rust finite-model search;
  claim labels with default-wire compatibility; Python vacuity reports for
  `ve check` and argument checking; the keyword registry and per-input Earley
  admission check; active P0 conformance fixtures and focused tests.
- Interfaces awaiting other owners: Lean `Layer`, `CertificateSound`, route
  admission and `route` subcommand (P0-Lean); W2 document command and W8 assist
  status use the P0 vacuity helper when their owned modules land; W3/W5/W1
  populate their respective Background hooks. The flag and defined-table
  conformance cases remain pending for those schemas.
- Remaining P0-Py review: migrate the remaining legacy constructor dispatch
  sites to the surface registry; run the complete suite and corpus replay;
  compare active fixture cases with the integrated Lean route. The acceptance
  status should not be read as a sign-off until these checks pass.
