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
  - Documents: `admit_quantity_report_sound` and `cites_discharged` (citations rest on checked lemmas).
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

## Loop recheck 1 (2026-09-28)

Each finding was fixed as a class, in Python, Lean and Rust where relevant, with regressions in `tests/test_w6a_looprecheck1.py`, `tests/test_w6a_documents.py` and `tests/test_fret_w6a_rerating.py`.

- **Renderings read back as themselves (P1, decimal P2).** Constant verbalisations must be whitespace-normalized (the display-string rule), and pairwise distinct up to sentence-initial ASCII capitalization (`VerbalisationCollision`), in all three decoders. Sentence-initial capitalization is ASCII-only in the parser. Decimal literals are bounded by 40 digits, with sign and point uncounted, so every admitted coordinate renders on every declared scale and reparses.
- **Evaluation budget (P2).** `VE.Time.Budget.evalB` charges exactly as Python `tick` and Rust `eval`, and `refutesB` does the same for countermodels. `evalB_sound` and `refutesB_sound` show that a budgeted answer is the reference answer. The pinned seven-entity fixtures are UNKNOWN in Lean too, and the six- and eight-entity fixtures report the pinned evaluation counts. Python `quantity_countermodel` raises on exhaustion instead of returning "does not refute".
- **Calendar (P2).** `civilOf_num : D.Valid → civilOf D.num = some D`, via `civilOf_complete`, `civilCandidate_spec`, `findYear_spec` and `findMonth_spec`. The month fold became a bounded search with the same results.
- **Documents (P1).** `VE.Time.Document` admits the P0 admission input with every formula a `ve-quantity@1` statement (`ve_quantity` case `document`). `admit_quantity_report_sound`: the root holds in every admissible tagged structure where the report's leaves hold, and every leaf is a submitted node satisfying its provenance rule with its label. Python (`ve.quantity_admission`) produces the same report and report id. Rust (`mode: document`) regenerates every statement. The `ve-document@1` loader takes quantity content, treats legacy `ast` content as dimensionless input to annotated admission, and checks graphs on this route.
- **Whole-grammar English (P1).** `parse_w6_sentence` reads a fence with the quantity wordings and with the frozen English grammar over the erased target. Frozen-grammar readings are dimensionless input and must pass annotated admission. Distinct admitted readings across the grammars reject as ambiguous.
- **Evaluation work (P1).** The news article is the Lean-admitted document `usecases/news-article/news-w6a.ve.md`. `usecases/news-article/coverage-w6a.md` refreshes the table from that run, beside the unchanged dated audit `coverage.md`: rows 7, 13, 21, 22 and 23 are DIRECT, and the totals are recounted from the rows. The measured partition is `coverage.json`, and `tools/coverage_dashboard.py` shows both in ROADMAP. The 30-item FRET sample is re-rated in `experiments/E0/FRET-W6A-RERATING.md` (b 8 → 10, c 18 → 16).

## Loop fix 2 (2026-09-28)

- **Citations (P1, directive).** Quantity documents take checked lemmas: each carries a `ve-quantity-certificate@1` from exactly its transitive leaves to its conclusion, checked by Lean when decoded. A `cite:<bundle>/<lemma>` leaf is admitted when it states that conclusion, and the report must carry the lemma's leaves with their labels. `cites_discharged` proves the report root holds wherever the report's non-citation leaves hold; `admit_quantity_report_sound` now includes this and citation closure. Python mirrors each diagnostic, and Rust regenerates every lemma statement (`lemma_meaning_ids`). `tests/test_w6a_citations.py` checks 19 binding classes in Python and Lean, including reordered, dropped or changed leaves, relabelling to money, raw and stale certificates, and cite leaves that state another statement. The core `ve-bundle@0` checker still refuses extended environments.
- The earlier loop recheck 1 fixes (whitespace names, decimal round trips, the Lean evaluation budget and the unconditional calendar inverse) were re-verified against the recheck's reproducers on a freshly built `ve_quantity`.

## Loop fix 3 (2026-09-28)

- **Domain order under the budget (P2).** Python and Rust sort every submitted domain when they load a model. Lean kept the input order, so a budgeted quantifier could stop at a different first decisive entity. On domain `["b","a"]`, Lean answered `∃x.(p(x) ∨ ∀y₁…∀y₁₉.⊤)` true after three evaluations, and a countermodel for its negation refuted, where Python and Rust exhausted `MAX_EVALUATIONS`. Below the budget, only the reported `evaluations` count differed. The frozen decoders are unchanged. The quantity runner now sorts each domain before `evalB` and `refutesB` (`VE.Time.Wire.sortDomains`). The same class was also in the relational route: the defined-table budget (`computeDefined`) now runs over sorted domains (`sortModelData`). `eval_domains_perm` and `countermodelCheck_domains_perm` prove that reordering a domain never changes a reference value, and `evalB_sorted_sound` and `refutesB_sorted_sound` state the runners' answers against the submitted model. `tests/test_w6a_looprecheck2.py` checks, three ways, the reviewer's reproducer in both orders, the countermodel route, evaluation counts on every permutation of a four-entity domain, premise short-circuiting, and the defined-table budget.

## Loop fix 4: limits directive (2026-09-28)

The orchestrator's limits directive (`w6a-limits-directive.md`) grouped the remaining findings into one class: Lean checked resource limits lazily, after or during unbounded work, so it answered or hung where Python and Rust return `ResourceLimit`. Both loop-review reproducers are fixed, and the class is fixed wherever it occurred in Lean, Python or Rust. Regressions are in `tests/test_w6a_limits.py`, `tests/test_w6a_route_limits.py`, `tests/test_w6a_certificate_steps.py` and `tests/test_w6a_limit_generator.py`.

- **Static limits first, one stage per wire mode, same order in all three.**
  - Each statement's own limits come first (10,000 source nodes, counted before elaboration in Python too, and in Rust including arrays in the operator position; formula and term depth 64).
  - Then the problem's aggregate: at most 10,000 core nodes across premises and conclusion (Lean `quantityLimits`, Python `check_quantity_limits`, Rust `quantity_limits`). Lean used to skip it on the quantity countermodel and certificate modes, so `[F₁₂, F₁₂] ⊢ ⊥` (16,383 nodes) refuted in Lean. Document lemmas and graph edges now go through the same check. On the relational route the countermodel aggregate now counts the conclusion as well as the premises.
  - Then the model's static limits, after its shape and before any entity is read: at most 1,000 entities per domain, then at most 100,000 supplied rows (Lean `modelLimits`, Python `_model_limits`, Rust `model_limits`). Python used to check duplicate entities first, and Rust's order route checked identifiers first.
  - Every route family checks its formulas before decoding the model.
- **Every construction that can grow is metered.**
  - Defined tables are built one candidate row at a time, in Python `product` order, under one shared evaluation budget and the tuple limit (`VE.Route.Budget.computeDefinedB`). The reviewer's 30-binder body now stops in under a second.
  - Every route family evaluates under the Python/Rust charges: relational `evalF`, order `VE.Time.evalB` on sorted domains, closure `evalC` and closure with n-ary atoms `evalN`. The n-ary family now sorts domains too. Each is proved to return the reference value whenever it returns a value.
  - Closures are built as Python and Rust build them, charged the same, and cached by edge and outer bindings (`VE.Route.Closure`). `warshallH_iff` proves each cached set is exactly the finite paths of its edges, so closure values are the reference values (`evalC_sound`, `evalN_sound`). An 816-entity named chain fits the budget (998,377 units) and 817 does not, in all three.
  - The definitions Background is evaluated per premise under its own budget, as Python `_valid_definitions` does. Rust skipped this check and validated flags and literals before building tables; it now follows Python's order. Flags are checked in one pass (`VE.Route.Flags`, proved equal to `flagsValid`).
  - Certificates replay within Python's 10,000 steps, one per trace node (`VE.Route.Steps`). The frozen checkers bound only depth. Route and quantity certificate cases report the limit, and admission edges, bundle lemmas and document lemmas are not established.
- **No superlinear work on tables.** Lean's frozen decoders deduplicated with `eraseDups` before checking limits (a 100,000-row table took about two minutes). `VE.Route.Decode` decodes route and quantity models with the same diagnostics and hash-set duplicate checks, and its admissibility checks are proved equal to `ModelData.valid` and `validModel?`. Every metered evaluator reads tables through a hash index built once per model (`memIn_relIndex`).
- **Differential generator.** Seeded families (doubling conjunctions, deep binder stacks, large domains, the order-sensitive budget, an oversized closure and both reproducers) run on the quantity runner and every route family. All three backends report `ResourceLimit` within 60 s per batch: 41 cases take 0.8 s on the Lean quantity runner, 2.7 s on the Lean route, 4.1 s in Rust and 29 s in Python.
- **Frozen contracts.** The frozen `ve_conformance` subcommands (v0, closure, order) and their decoders are unchanged (`lean/VE/Route/frozen.py`), so they keep their unbudgeted reference evaluation. W6 and route evidence go through the `quantity` and `route` runners above.

## Loop fix 5: static limits recheck (2026-09-29)

The recheck of loop fix 4 found three more static-limit gaps. Each is fixed as a class. Regressions are in `tests/test_w6a2_looprecheck1.py`, and the differential generator gained all three families.

- **Definition premises (P2).** Python checks each definition's generated biconditional after its body, in dependency order. A body of 8,191 nodes gives a 16,390-node premise, and a body of 61 binders gives a premise 65 levels deep; Python reports `ResourceLimit` for both. Lean and Rust checked only the body and evaluated `⊤` over such an environment. Rust now type-checks each generated premise after its body, and Lean's elaboration (`premiseWithin`) reports the first definition whose body is ill-typed or whose premise exceeds 10,000 nodes or 64 levels, in Python's order. Lean also decodes bodies last, each within its own limits, as `compile_definitions` does. Tests pin both reproducers, the node and depth boundaries for unary and binary definitions, and the order of the limit and a typing error across two definitions.
- **Reach bodies in Python's aggregate (P2).** Python's search count skipped Reach body edges, so `[P, P, P] ⊢ ⊥` with `P = ∃s. reach⁺(body F₁₁)(x, x)` (12,298 nodes) counted as 13 and was checked. The count now matches the type checker's for every constructor. This covers `check_countermodel`, `find_countermodel`, `find_distinguishing_model` and the quantity aggregate.
- **Limits before typing (P2).** Python's decoder counts nodes in preorder and reports `ResourceLimit` before anything is typed. Lean typed first on every route family, because the frozen `decodeFormulas` count after typing: `["and", ["eq", x₀, x₀], F₁₃]` was ill-typed in Lean. Lean did not count admission claims, lemmas or readings at all. Rust's order route typed while it counted. `VE.Route.AstLimit` (Lean) and `ast_limit` (Rust) walk a case's raw formulas as Python's decoder reads them, across a document or across premises and conclusion. Each reports the limit, or stops at the first node Python rejects for its shape so the family decoder reports it. The walk runs before decoding and typing in every route family and on each closed claim. The frozen `ve_conformance` subcommands keep their order.

## Still open

- **W8 fidelity: an open measurement, not a W6a merge gate.** The orchestrator's directive scopes W8 out of W6a: it is recorded here to be run separately. It needs live model calls: 20 sealed model-written sentences per construct, authoring by Opus 5.5 and Haiku 4.5, and a blind Astra audit. This work makes no model calls. Until it runs, quantity constructs stay out of `ve assist` (strict-only authoring). `render_quantity_witness` supplies the measurement's deterministic witness input (units restored). Document fences are checked for one reading across the whole grammar, as existing English fences are.
- **Premise status of quantity documents.** `ve document check` searches small finite models and does not choose integer values, so it reports UNKNOWN for the news document. The fixture model is the non-vacuity evidence: Lean evaluates the report's leaves and root true in it.
- **Relational and quantity content in one document.** The news document's relational clauses stay in `claims.ve`, because the quantity route's profile set differs from the relational document's.
- **W6b (gated on numbers2).** `sunday`, `excluded_sundays`, date/integer binders, traces (`Time.excludedDays_iff`, the guarded Sunday equivalence, `Time.trace_iff`), and the certified Art. I §7 result reject until the proved numbers2 integer-quantifier route exists.

## Gates run

- Loop fix 4:
  - `lake build` passed (256 jobs).
  - `lean/audit.py` passed (140 sources, 1,081 theorem declarations, standard axiom allowlist only).
  - `lean/VE/Route/frozen.py` passed: the frozen sources and `Main.lean` subcommands are unchanged.
  - `cargo build --release` and `cargo test` passed for the workspace.
  - The full pytest run had 2,484 passed, 5 skipped, 1 live test deselected and 1 failure, in 65 minutes on a shared machine at load average ~10. The failure was `test_assist_deadline.py::test_approval_sealing_is_inside_the_operation_deadline` again, the wall-clock test in unchanged `ve/assist` code. Rerun with `test_nary_differential.py` against the rebuilt Rust debug binary, both files passed (43/43).
  - No model calls or push were made.
- Loop fix 3: `lake build` passed (246 jobs). `lean/audit.py` passed (135 sources, 1,014 theorem declarations, standard axiom allowlist only). `lean/VE/Route/frozen.py` passed, and the fix leaves the frozen decoders unchanged. Rust was not changed.
- Loop fix 3 full pytest run: 2,435 passed, 5 skipped, 1 live test deselected, 1 failure. The failure was `test_assist_deadline.py::test_approval_sealing_is_inside_the_operation_deadline` again, the wall-clock test in unchanged `ve/assist` code. Its file passed 35/35 when rerun alone.

Loop fix 2:

- `lake build` passed (246 jobs).
- `lean/audit.py` passed (135 sources, 1,008 theorem declarations, standard axiom allowlist only).
- `lean/VE/Route/frozen.py` passed.
- `cargo build --release` and `cargo test -p ve-core` passed.
- The full repository pytest run had 2,429 passed, 5 skipped, 1 live test deselected and 1 failure. The failure was `test_assist_deadline.py::test_approval_sealing_is_inside_the_operation_deadline` again. It is a wall-clock deadline test in unchanged `ve/assist` code and ran under load average ~20–30. Its file passed 35/35 when rerun alone.
- No model calls or push were made.
