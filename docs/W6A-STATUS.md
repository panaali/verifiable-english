# W6a implementation status (2026-09-28)

W6a quantity statements are now admitted and certified by Lean through a separate `ve_quantity` executable (`lean/QuantityMain.lean`, `VE.Time.Wire`). The frozen `ve_conformance` subcommands are unchanged, and the generic `route` still rejects `unit_schema` environments. Raw erased order certificates therefore remain non-W6 evidence. The Python core checker also rejects extended environments, so they cannot bypass annotated admission.

## Lean (authoritative)

- **Environment admission.** `VE.Time.Wire.decodeEnvironment` decodes `ve-units@1` environments. It checks power-of-ten scales, closed display kinds, reserved `day`/`elapsed_day`, and exact W6 profile lists (`documents@1` optional). It rejects `$string` literals and tags spelled like sorts. Display strings must use single spaces; only an input symbol may end with one space. Display injectivity treats canonical displays and input aliases as one class, including the percentage-point alias: no affix may extend another on its side or touch the amount. All legacy declaration rules come from the frozen order decoder, applied to the regenerated target environment. Both environment identities are recomputed from the submitted and regenerated JSON.
- **Statement admission.** `elabFormula` decodes `S`. It lowers `decimal`/`date` literals with `Time.lower` and `parseIso`, regenerates `Q`, rejects any differing claimed `Q`, and admits with the proved `QFormula.admits`. It then erases and re-checks the core with the frozen order decoder. Formula depth and term depth are each capped at 64, and nodes at 10,000, as in Python and Rust.
- **Proved obligations** (all in `lean/audit.py`, standard axioms only):
  - `units_admit_sound` / `units_admit_complete`: executable admission equals the independent `Admitted` relation.
  - `erase_wellTyped`: an admitted statement erases to a well-typed core formula.
  - `units_faithful`: direct tagged semantics equal core truth, with date operations read as civil-calendar relations. `lift_admissible`, `lower_lift` and `lift_unique` give each admissible core structure its unique tagged interpretation on declared symbols.
  - `decimal_exact` (iff), `lower_none_iff` and `lower_render`: exact decimal lowering, with rendering as its inverse.
  - Calendar: `num_injective`, `exists_valid_of_le`, `before_iff`, `num_succ`, `valid_iff`, `civilOf_num`.
  - `temporal_iff`, one lemma per operation: `on_iff`, `before_iff_lt`, `after_iff_lt`, `noLater_iff_le`, `shift_iff`, `within_iff`, `elapsed_iff`, plus `within_zero_iff_on`.
  - Counting: `expand_atLeast_iff` (every structure and outer scope), `expand_atLeast_eval_iff`, `expand_exactly_iff`, `expand_atMost_iff`.
  - `checkW6Certificate_sound`: an accepted `ve-quantity-certificate@1` is bound to the annotated environment and quantity meaning ids, and the statements are entailed over every admissible tagged structure. Relabelling percent to money changes the meaning ids and fails.
- **Route cases:** admission/evaluation, countermodel (bound to annotated and core ids), certificate, the canonical counting expansion with caps 8/7/7, and `day`/`civil`/`lower`/`render` conversions.

## Python and Rust

- Python mirrors every admission rule for early diagnostics, keeps the submitted environment spelling as its identity (explicit empty `argument_units` included), and gates nonempty `traces`. It produces `ve-quantity-certificate@1` evidence (`prove_quantity`) and checks it early (`check_quantity_certificate`).
- The restricted English wording parser tries every rule at every connector occurrence under a named derivation budget, and rejects multiple readings. Only a sentence-initial constant name is capitalized; literals are never case-folded.
- Rust validates the same declarations and statements with the same diagnostics. It regenerates, evaluates and checks countermodels, and rejects certificate requests with `UnsupportedProfile` (assurance `regeneration-only`).
- Three-way tests (`tests/test_units_lean_w6a.py`, `tests/test_units_rust_w6a.py`, `tests/test_w6a_review_regressions.py`, `tests/test_news_w6a_fixtures.py`) cover:
  - identities and values on the news fixture;
  - hostile statements, including a forged `Q`;
  - every review class of environment rejection;
  - 10,000 dates in both directions;
  - deterministic decimals near the 40-character limit;
  - canonical counting expansions and bounds;
  - certified news consequences, relabelled/raw/mutated certificates, and countermodels.

## News fixture

Every §7.1 row with a numeric payload (N01, N07, N13, N15/N24, N21, N22, N23) has a Lean-admitted case with a round-tripping wording. The fixture model satisfies all cases and consequences. These consequences have Lean-checked certificates over the cases they cite: N07 and N13 orders, the N13 years, the N15/N24 goal equality, the N21 order and 0.10-point difference, and the N23 differences. N07b/N22b stay NO, N08 stays REIFIED, and the projected and vague wording is OPEN. Source facts remain assumption/testimony leaves.

## Still open

- **Document route.** `ve-document@1` admission of `{"quantity": ...}` units, and citation/report binding, need the order-family document route; the base route still defers order-family admission for every document. The coverage table is therefore unchanged.
- **Whole-grammar English.** The quantity wording grammar is all-derivations only locally. It is not yet part of the whole English all-derivations gate or the W8 fidelity gate, so quantity constructs stay strict-only.
- **W6b (gated on numbers2).** `sunday`, `excluded_sundays`, date/integer binders, traces (`Time.excludedDays_iff`, the guarded Sunday equivalence, `Time.trace_iff`), and the certified Art. I §7 result reject until the proved numbers2 integer-quantifier route exists.
- **Evaluation work.** The FRET re-rating and the source-span coverage refresh.

## Gates run

- `lake build` passed (242 jobs).
- `lean/audit.py` passed (132 sources, 988 theorem declarations, standard axiom allowlist only).
- `lean/VE/Route/frozen.py` passed.
- `cargo test -p ve-core` passed.
- The repository pytest run (8 chunks) had 2,301 passed, 5 skipped, 1 live test deselected and 1 failure. The failure was `test_assist_deadline.py::test_approval_sealing_is_inside_the_operation_deadline`, a wall-clock deadline test in unchanged `ve/assist` code, run under load average ~9.5; its file passed 35/35 when rerun alone.
- No model calls or push were made.
