# W6a implementation status (2026-09-28)

This branch contains a **regeneration-only first slice** of W6a. It does not certify quantity statements. In particular, the Lean `route` decoder still rejects `unit_schema` environments, and `order@0` document admission remains deferred. Raw erased order certificates are not W6 certificates. The Python core checker rejects extended environments so they cannot bypass annotation admission.

Implemented:

- Identity-bound `ve-units@1` declarations, integer slot and constant tags, complete ground term annotations, exact decimal lowering, seven quantifier-free date operations, tagged `Q` regeneration and a separately identified erased environment.
- Canonical bounded user-sort counting expansion, with the pinned finite-evaluation results and caps. Integer-sort counting remains gated on numbers2.
- A restricted quantity wording parser and renderer, including ISO and long-date aliases, percent/money input, inclusive/strict comparisons, explicit intervals, elapsed days and same-grid percentage-point differences. Its ambiguity check is local to that grammar; it is not integrated with the whole English all-derivations gate.
- Rust regeneration and evaluation for the ground family and user-sort quantifier expansions, with Python/Rust differential tests. Rust reports `assurance: regeneration-only`.
- Four audited Lean arithmetic lemmas in `VE.Time.Arithmetic`: exact grid-coordinate value, equality of tags for an accepted comparison, the zero-day inclusive window, and signed elapsed duration. These are not the W6 admission, erasure, fidelity or calendar-conversion theorems.
- Pinned news numeric inputs and explicit residuals; authored age and large-count negative controls; independent seven-weekday deadline enumeration. The news coverage table is unchanged because no W6 claim has completed the admission and source-fidelity gates.

Still required for W6a certification: Lean decoding of the annotated environment and pre-lowering statement, proof of `units_admit_sound`, `erase_wellTyped` and tagged semantic fidelity, binding of annotated and erased identities to certificates/models/documents/citations, order-family document admission, complete Rust route parity, whole-grammar English all-derivations correspondence, and three-way conformance. `sunday`, `excluded_sundays`, date/integer binders, traces and the certified Art. I §7 result remain W6b and reject until the proved numbers2 integer-quantifier route exists. The FRET re-rating and source-span coverage refresh also remain open.

Gates run: `lake build` passed (228 jobs); `lean/audit.py` passed (127 sources, 884 theorem declarations, standard axiom allowlist only); `lean/VE/Route/frozen.py` passed; `cargo test -p ve-core` passed; 36 focused W6 tests passed; the repository pytest run passed 2,173 tests with 5 skips and 1 live test deselected. No model calls or push were made.
