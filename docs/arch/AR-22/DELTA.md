# AR-22: deltas

None. No verdict, refusal text, step count, wire field or fault order changed. The corpus A/B over the nine
corpora of the lean-first gate found 0 differences: 100,538 records the same and 22 unavailable on both sides with
identical outputs (R7, below), 0 unlisted; the base and head recordings are byte-identical (`evidence/ab.json`). One
whole-UDHR pilot record that the concurrent recording left timed out (600 s) on the head side only was re-run on both
sides with the recorder's own `pilot_check` (`docs/arch/AR-20/pilot_rerun.py`); it answered, the same on both sides,
and equal to the base's recorded answer (`evidence/pilot-rerun.json`). The Lean output differential (OUT) over 441
invocations of every `lean_exe` found no output change (`evidence/out.json`: its one listed difference is the
backtrace addresses after two pre-existing PANIC lines that are the same on both builds).

The only rows the A/B lists are records unavailable on both sides with identical outputs. None is a delta. Each is in
`evidence/ab-delta.json` with its reason.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 18 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same pre-existing `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-22/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 2 | 1 `pilots/default` `document_check` record of a whole-UDHR translation | The same pre-existing 600 s recorder time-out (L75), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-22/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 3 | 1 `pilots/default` `document_check` record, `udhr-20261102T1800Z` `translation-whole.et0.ve.md` | The same pre-existing `CheckerUnavailable` (`readings-verdicts: more than 64 compatible readings`), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-22/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 4 | 2 `discourse/default` records of text `2757af3b2b5456b1` (`document_check`, `document_render`) | The same pre-existing `CheckerUnavailable` (the norms route refuses a norm object: fields do not match), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-22/evidence/ab-delta.json` (PASS, 0 unlisted) |

## Removed theorems and their covers (not deltas)

`lean/statements.txt`: 8181 → 8060 entries, 0 added, 121 removed, 24 changed. Every removed theorem
is about a deleted copy: closure's tableau (`VE/TableauExtended*`, `Closure/{PathRules,Induction,Substitution,Congruence}`)
or AR-21's lemmas equating that copy's `replay` with Core's. The 24 changed entries keep their statement text and
`expr` hash byte for byte; only the defining module of moved constants on their `-- uses` line differs
(`evidence/statements.json`, `changed`). No approved statement changed.

Cover kinds. **Core twin** (61 theorems): the same-named theorem of `VE.Core` (`VE.Closure.Tableau.X` →
`VE.Core.Tableau.X`, `VE.Closure.X` → `VE.Core.X`), in the head's `statements.txt`. It states the lemma for Core's
tableau, which closure's checker now runs; `checkCertificate_sound` itself now applies `VE.Core.Tableau.replay_sound`.
**Defining equation** (60 theorems): AR-21's lemmas that closure's `replay`, or a function it calls, equals
Core's on the embedding. Closure's own `replay` is deleted and its checker is defined as Core's replay of the embedded
certificate, so `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` (now `rfl`, statement unchanged) covers them.

| Removed theorem | Covered by | Cover kind |
|---|---|---|
| `VE.Closure.CoreEquiv.add_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.at_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.atomMatches_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.checkChildren_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.closed_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.closes_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.complementary_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.composeKind_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.composeStep_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.dedup_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.deriveExtra_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.edgeCheck_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.edgeStep_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.embedBranch_expanded` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.embedBranch_instantiated` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.embedSigned_bindings` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.embedToken_inj` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.endEdge_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.endStep_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.equalities_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.equivalent_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.extra_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.getElem?_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.groundMatch_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.ground_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.grow_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.induct_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.inductionStep_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.initial_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.invariantAt_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.isReach_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.known_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.liftMatch_eq` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.liftSub_eq` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.liftTerm_eq` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.literals_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.map_embedToken_inj` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.matches_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.mem_instantiated` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.mem_map_embedToken` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.namedStep_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.next_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.parse_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.reachClosed_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.reachable_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.replay_certificate_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.replay_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.rule_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.scoped_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.shift_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.sortOf_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.sortsOf_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.step_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.substTerm_eq` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.subst_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.tag_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.termToken_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.unfoldAt_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.unfold_embed` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.CoreEquiv.unlift_eq` | `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` | Defining equation |
| `VE.Closure.Path.first` | `VE.Core.Path.first` | Core twin |
| `VE.Closure.Path.last` | `VE.Core.Path.last` | Core twin |
| `VE.Closure.Tableau.add_holds` | `VE.Core.Tableau.add_holds` | Core twin |
| `VE.Closure.Tableau.bindings_extend` | `VE.Core.Tableau.bindings_extend` | Core twin |
| `VE.Closure.Tableau.bindings_get` | `VE.Core.Tableau.bindings_get` | Core twin |
| `VE.Closure.Tableau.checkChildren_member` | `VE.Core.Tableau.checkChildren_member` | Core twin |
| `VE.Closure.Tableau.closed_sound` | `VE.Core.Tableau.closed_sound` | Core twin |
| `VE.Closure.Tableau.closes_sound` | `VE.Core.Tableau.closes_sound` | Core twin |
| `VE.Closure.Tableau.closure_holds` | `VE.Core.Tableau.closure_holds` | Core twin |
| `VE.Closure.Tableau.complementary_sound` | `VE.Core.Tableau.complementary_sound` | Core twin |
| `VE.Closure.Tableau.composeStep_sound` | `VE.Core.Tableau.composeStep_sound` | Core twin |
| `VE.Closure.Tableau.delta_witness` | `VE.Core.Tableau.delta_witness` | Core twin |
| `VE.Closure.Tableau.edgeStep_sound` | `VE.Core.Tableau.edgeStep_sound` | Core twin |
| `VE.Closure.Tableau.endStep_sound` | `VE.Core.Tableau.endStep_sound` | Core twin |
| `VE.Closure.Tableau.equalities_sound` | `VE.Core.Tableau.equalities_sound` | Core twin |
| `VE.Closure.Tableau.equivalent_sound` | `VE.Core.Tableau.equivalent_sound` | Core twin |
| `VE.Closure.Tableau.extra_sound` | `VE.Core.Tableau.extra_sound` | Core twin |
| `VE.Closure.Tableau.gamma_holds` | `VE.Core.Tableau.gamma_holds` | Core twin |
| `VE.Closure.Tableau.ground_denote` | `VE.Core.Tableau.ground_denote` | Core twin |
| `VE.Closure.Tableau.grow_sound` | `VE.Core.Tableau.grow_sound` | Core twin |
| `VE.Closure.Tableau.holds_extend` | `VE.Core.Tableau.holds_extend` | Core twin |
| `VE.Closure.Tableau.induct_sound` | `VE.Core.Tableau.induct_sound` | Core twin |
| `VE.Closure.Tableau.known_bindings` | `VE.Core.Tableau.known_bindings` | Core twin |
| `VE.Closure.Tableau.literals_hold` | `VE.Core.Tableau.literals_hold` | Core twin |
| `VE.Closure.Tableau.matches_sound` | `VE.Core.Tableau.matches_sound` | Core twin |
| `VE.Closure.Tableau.mem_dedup` | `VE.Core.Tableau.mem_dedup` | Core twin |
| `VE.Closure.Tableau.namedStep_sound` | `VE.Core.Tableau.namedStep_sound` | Core twin |
| `VE.Closure.Tableau.next_sound` | `VE.Core.Tableau.next_sound` | Core twin |
| `VE.Closure.Tableau.one_holds` | `VE.Core.Tableau.one_holds` | Core twin |
| `VE.Closure.Tableau.reachClosed_sound` | `VE.Core.Tableau.reachClosed_sound` | Core twin |
| `VE.Closure.Tableau.reachable_sound` | `VE.Core.Tableau.reachable_sound` | Core twin |
| `VE.Closure.Tableau.replay_sound` | `VE.Core.Tableau.replay_sound` | Core twin |
| `VE.Closure.Tableau.rule_closure_formula` | `VE.Core.Tableau.rule_closure_formula` | Core twin |
| `VE.Closure.Tableau.step_sound` | `VE.Core.Tableau.step_sound` | Core twin |
| `VE.Closure.Tableau.termToken_denote` | `VE.Core.Tableau.termToken_denote` | Core twin |
| `VE.Closure.Tableau.token_defined` | `VE.Core.Tableau.token_defined` | Core twin |
| `VE.Closure.Tableau.two_holds` | `VE.Core.Tableau.two_holds` | Core twin |
| `VE.Closure.Tableau.typed_extend` | `VE.Core.Tableau.typed_extend` | Core twin |
| `VE.Closure.Tableau.unfoldAt_sound` | `VE.Core.Tableau.unfoldAt_sound` | Core twin |
| `VE.Closure.closure_induction` | `VE.Core.closure_induction` | Core twin |
| `VE.Closure.edge_at_denote` | `VE.Core.edge_at_denote` | Core twin |
| `VE.Closure.edge_inclusion` | `VE.Core.edge_inclusion` | Core twin |
| `VE.Closure.edge_shift_denote` | `VE.Core.edge_shift_denote` | Core twin |
| `VE.Closure.edge_typed` | `VE.Core.edge_typed` | Core twin |
| `VE.Closure.endEdge_sound` | `VE.Core.endEdge_sound` | Core twin |
| `VE.Closure.formula_matches_sound` | `VE.Core.formula_matches_sound` | Core twin |
| `VE.Closure.inductionStep_denote` | `VE.Core.inductionStep_denote` | Core twin |
| `VE.Closure.invariantAt_denote` | `VE.Core.invariantAt_denote` | Core twin |
| `VE.Closure.liftMatch_sound` | `VE.Core.liftMatch_sound` | Core twin |
| `VE.Closure.liftSub_denote` | `VE.Core.liftSub_denote` | Core twin |
| `VE.Closure.liftTerm_denote` | `VE.Core.liftTerm_denote` | Core twin |
| `VE.Closure.named_body_denote` | `VE.Core.named_body_denote` | Core twin |
| `VE.Closure.pair_values` | `VE.Core.pair_values` | Core twin |
| `VE.Closure.reach_compose` | `VE.Core.reach_compose` | Core twin |
| `VE.Closure.reach_denote` | `VE.Core.reach_denote` | Core twin |
| `VE.Closure.reachable_induction` | `VE.Core.reachable_induction` | Core twin |
| `VE.Closure.reachable_trans` | `VE.Core.reachable_trans` | Core twin |
| `VE.Closure.substTerm_denote` | `VE.Core.substTerm_denote` | Core twin |
| `VE.Closure.subst_denote` | `VE.Core.subst_denote` | Core twin |
| `VE.Closure.unfold_denote` | `VE.Core.unfold_denote` | Core twin |
| `VE.Closure.unlift_denote` | `VE.Core.unlift_denote` | Core twin |
