# kb-risk: runner theorems for the risk route's keyed case kinds

Status: done, no DRI signature needed; DELTA none (no answer byte changes). Branch `feature/kb-risk`, base main 0f6d59d441.
Changed: `lean/VE/Risk/WireSound.lean` (new: `risk_elaborate_wire_sound`, `risk_decision_wire_sound` on `VE.Risk.Run.runCase`, plus `runCaseReported_ok` and four helper lemmas); registry path `risk` lists the two theorems; closure baseline, Lean inventories, audit manifest and the quoted figures re-measured.
Figures: kernel 9,552 unchanged; risk path spec 6,160 -> 6,309, wrap 5,670 -> 5,670; trusted Lean K +0, S +0; every RSP S item and every risk-route item of the other keys is stated by a theorem (table below).
Open: none blocking. Two deviations from the task text, each the conservative option (Notes for the DRI 1 and 2): the answer shapes are written out inside the theorems, not as `…Answer` definitions (a definition would be S +65 with no ruling to sign it), and the four kinds no key calls are listed here, not as `uncovered` in the registry (the tool refuses `uncovered` on a candidate path).

SIZE: 248 product (Lean: WireSound.lean 247, VE.lean 1), 0 tests, 140 other hand-written lines (CALLS.md 77, seeded-bugs.json 46, registry 2, assurance manifest 1, spec and frozen-keys re-quotes 14; not counting this report).

## Step 1: what the keys call (docs/kernel/kb-risk/CALLS.md, commit b28ae39ce3)

RSP 2 `risk-elaborate` + 1 `risk-decision`; Preparedness 3 + 3; FSF 1 + 1; agent-policy and eligibility 0. No key sends `admission`, `risk-conflict`, `risk-followable`, `risk-audit` or `risk-certificate` on this route. So step 2 has two kinds: `risk-elaborate` and `risk-decision`.

## Step 2: the theorems (lean/VE/Risk/WireSound.lean)

Both have the house hypotheses `runCase j = .ok answer`, `VE.Route.Run.caseKind j = .ok "<kind>"` and `usesRiskPath j = true`.

- `risk_elaborate_wire_sound`: there are `id` and `src` with (i) `VE.Bridge.stringField j "id" = .ok id` and `Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok src`, `WellFormedRisk src.R = true`; (ii) `answer = ok id [...]`, a closed field list: `environment_id`/`document_hash` = `src.R.policy`, `risk_premises` = each `(label, formula)` of `(riskPremiseLabels src.R).zip (riskPremises src.R)` as `{"label", "ast": Wire.enc formula}`, `unranked_severities` = `Wire.unrankedSeverities src.R`, the other fields by key; (iii) the `risk:class` rows are exactly `class(h, c)` for each `(h, c)` of `src.R.risk.harmClasses`, in order, and the `risk:order` rows exactly `orderLiteral src.R p` for each pair of `classPairs src.R` (`more_severe(a, b)` when the pair is in the closed order, its negation otherwise).
- `risk_decision_wire_sound`: there are `id`, `src`, `entry`, `supplied`, `d` with (i) the same id and source decoders, `Wire.decodeEntry (j.getObjValD "decision") = .ok entry`, `Wire.decodeSupplied (j.getObjValD "entries") = .ok supplied`, `admitDecision src.R entry supplied = .ok d`; (iii) the conclusion of `risk_wire_scenario_sound` (well-formed source, `validateDecision src.R d = .ok ()`, `marginLimit src.R d = .ok ()`) and of `regenerate_sound` (for every alternative of `d` and harm: a cell is in `might` iff some completed case has the harm, in `leads` iff every completed case has it); (ii) by `VE.Alternatives.scenarioConflict (toAlt src.R) (decisionModel src.R d)`: on `some (t, vs)` the answer is the closed list with `"verdict": "CONFLICT"`, `target` `t.1` and `tuple` `vs`; on `none` it is the closed list whose `tables.might` rows are the cells of `(regenerate src.R d).might` in order (`alternative`, `harm`, and only a `witness` beside them), `tables.leads` the cells of `(regenerate src.R d).leads`, `statuses` the rows of `statuses src.R d` with `firingRules`, `lines.unexamined_possible` the cells of `cellsOf src.R d` no record addresses whose completion is `⊤`, `clear` the clear alternatives, `conditional_on` the ids of `d.cited`, and `environment_id`, `document_hash`, `decision_record_id` = `src.R.policy`, `decisionRecordId entry`.

`status` is `"ok"` in both: `ok id fields` is `VE.Route.Wire.ok` (`lean/VE/Route/Wire.lean:562`: `{"id", "status": "ok"} ++ fields`), and no stated list holds a second `id` or `status` key. Fields no key reads (`text`, `worst_cases`, `margins`, `legend`, the regenerated vocabulary, ...) are stated by key only, inside the closed list, so none can override a stated one (kb-7 F1). A refusal (`runCase j = .error _`) asserts nothing; RSP's T4 probe refusal row is recorded, not keyed (CALLS.md).

Every field step 1 found a key reading is stated from existing definitions; no field needed `statusText` or `diagnosisOf`. Nothing was left unstated, so there is no stop for the architect seat.

## Per item: which theorem states the field it reads

| Key | Item | Fields read (CALLS.md) | Stated by |
|---|---|---|---|
| RSP | S1-T1, S1-T2, S1-T3, S1-T4 | `admitted` (both answers' `status`); `classes` from `risk_premises` rows labelled `risk:class`, harm `ast[2][1]`, class `ast[3][1]` | `risk_elaborate_wire_sound` (ii) status and `risk_premises`, (iii) the `risk:class` rows are `class(h, c)` for the decoded `harmClasses`; `Wire.enc` = `VE.Route.Wire.encodeFormula`, whose `.binary p t u` is `["binary", p, enc t, enc u]` and `.const c` is `["const", c]` (`lean/VE/Route/Wire.lean:280,286`), so `ast[2][1]` is `h` and `ast[3][1]` is `c`; the decision answer's `status` by `risk_decision_wire_sound` (ii) |
| RSP | S2 | `admitted` only (answers `undecided`) | `risk_elaborate_wire_sound` and `risk_decision_wire_sound` (ii), `status` |
| RSP | S3 | `tables.might[].alternative`, `.harm` | `risk_decision_wire_sound` (ii) `none` branch, rows of `(regenerate src.R d).might`; meaning by (iii) `regenerate_sound` |
| RSP | S4 | `tables.leads[]` | `risk_decision_wire_sound` (ii) rows of `(regenerate src.R d).leads`; (iii) |
| RSP | S5 | `classes` (as S1) | `risk_elaborate_wire_sound` (iii) `risk:class` rows |
| Preparedness | S6 | `status` of both answers (its value is the request's `more_severe` order) | both theorems (ii), `status` |
| Preparedness | S7 | `status`; `tables.might[]` (`bio_h_might`) | `risk_decision_wire_sound` (ii), (iii) |
| Preparedness | S8 | `status`; `tables.leads[]` (`invented_leads`) | `risk_decision_wire_sound` (ii), (iii) |
| FSF | S1-* | `status`; `risk:class` rows (`ast[2][1]`, `ast[3][1]`) | `risk_elaborate_wire_sound` (ii), (iii) |
| FSF | S2, S3 | `risk:order` rows whose `ast[0]` is `binary` | `risk_elaborate_wire_sound` (iii): the `risk:order` rows are `orderLiteral src.R p` over `classPairs src.R`: `binary` exactly when the pair is in `closure src.R` (`lean/VE/Risk/Background.lean:38`) |
| FSF | S5 | `classes`; `tables.might[]` | both theorems (iii) and (ii) |
| FSF | S6 | `tables.leads[]` | `risk_decision_wire_sound` (ii), (iii) |
| all three | (decision record) | `environment_id`, `document_hash` | `risk_elaborate_wire_sound` (ii) = `src.R.policy` |
| FSF | (recorded) | `unranked_severities`; `decision_record_id`, `conditional_on`, `lines.unexamined_possible` | elaborate (ii) `Wire.unrankedSeverities`; decision (ii) `decisionRecordId entry`, `d.cited`, the unexamined `⊤` cells |

Agent-policy and eligibility send nothing on this route.

## Step 3: registry and measurement

`tools/kernel-paths.json` path `risk`: `risk_elaborate_wire_sound` and `risk_decision_wire_sound` added to `theorems`; `runCase` stays the subject; tier stays `candidate`. The saved measurement now lists them under `stated["VE.Risk.Run.runCase"]` with `risk_wire_acceptance`.

On the final Lean, `uv run python tools/kernel_closure.py --out docs/kernel/closure-baseline.json` (the risk row) and `uv run python tools/kernel_closure.py --check /tmp/kbrisk-base-before.json`, against main's saved baseline (`git show 0f6d59d441:docs/kernel/closure-baseline.json`):

```
risk          candidate          8    6309    5670    7989  risk
kernel (distinct lines of every path of tier kernel): 9552
under the frozen keys' answers: 16347, of them in the kernel: 9552
definitions that write a verdict token: 57, of them outside the kernel: 56 in 28 modules
PASS: kernel 9552 <= 9552
PASS: verdict writers outside the kernel 56 <= 56
```

| risk path | theorems | spec | wrap | lines |
|---|---:|---:|---:|---:|
| before (main 0f6d59d441) | 6 | 6,160 | 5,670 | 7,840 |
| after | 8 | 6,309 | 5,670 | 7,989 |

Spec +149: `VE.Risk.WireSound` +111 (the two statements), `VE.Risk.Run` +16, `VE.Risk.Cond` +13, `VE.Risk.Wire` +6, `VE.Risk.Record` +3 (definitions the statements newly read). Keyed lines 16,198 -> 16,347 (the same +149); re-quoted in docs/spec/kernel-boundary.md (sections 0, 1.2, 1.3) and docs/kernel/frozen-keys-20261111.md; `tests/test_kernel_closure.py -k "records_quote or spec_claims"`: 2 passed.

Ten largest spec modules of the risk path after (lines): VE.Risk.Record 763, VE.Route.Admission 369, VE.Risk.Wire 349, VE.Norms.Tree 273, VE.Norms.Wire 259, VE.Risk.Decl 214, VE.Alternatives.Decl 200, VE.Route.Wire 200, VE.Grammar.Table 197, VE.Acts.Grammar 159 (before: the same list, Record 760 and Wire 343).

Kinds no key calls get no runner theorem here: `risk-conflict` (`runConflict`), `risk-followable` (`runFollowable`), `risk-audit` (`runAudit`), `risk-certificate` (`runCertificate`). They are not written as `uncovered` in the registry (Notes for the DRI 2).

## Checks run (final Lean, commit 12a668d54f unless said)

The first selected run (on 80da452520) stopped at `tools/check_lean_imports.py`: `new outward Lean import: VE.Risk.WireSound -> VE.Risk.Run (layer 2 -> 4)`. 12a668d54f declares the layer on the file's first line (`-- ve-layer: 4 (...)`, as `lean/VE/Readings/SoftSupRunExamples.lean:1` does; no Python change); the lint then reports `Lean layer graph kept`. The build, regen, audit, closure, trust map and trust mutants below were rerun on it; the harness runs, statement checks and seeds were not rerun: the edit adds a comment line, and the `ve_service` built on it is the pinned one (sha256 9c3315ce..., in `lean/checkers.lock`).

- `lake build` (full, on 12a668d54f): `Build completed successfully (1439 jobs)`, exit 0. No `sorry` in WireSound.lean (`grep -n sorry`: none).
- `python3 lean/audit.py` (run by `regen_generated.py --write --only lean-statements --only lean-audit-manifests --only lean-roots --only trust-tables`): `PASS: 873 source files; 9972 named theorem declarations audited ...; only the declared standard axiom allowlist`. New axioms lines are `propext`, `Classical.choice`, `Quot.sound` only (`lean/axioms.txt`).
- `uv run python tools/trust_map.py --check`: `against 0f6d59d44107: K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS`.
- Trust mutants: light lane `NOT` (new Lean file), so `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/kernel/kb-risk/trust-mutants.json` on ceb580f8c8, then `--rescore` of that record on 12a668d54f: `0 definitions, 0 mutants ... 0 KILLED, 0 SURVIVOR, 0 UNKNOWN`, exit 0 both times (no trusted declaration added or changed).
- Five frozen keys, each through `zsh iso.sh <name> 16G --` with the pinned `ve_service` (sha256 9c3315ce..., listed in `lean/checkers.lock`): RSP `run.py --check` exit 0, `110 / 126`; Preparedness `run.py --check` exit 0, `236 / 239`; FSF `run.py --check` exit 0, `260/262` (C3 and C-doc disagree, as on main, CALLS.md); agent-policy `check.py base` exit 0; eligibility `run.py --no-write` exit 0, `mutants_killed 32/32`. `sha256sum usecases/*/results.json` before and after: identical (`diff` empty).
- `tools/check_*_statements.py` (all eight): exit 0 (none covers Risk).
- `uv run python tools/gate_collection.py --check --prebuilt`: `0 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed`.
- Selected tests: see "Selected run" below.

## Seeded bugs (docs/kernel/kb-risk/seeded-bugs.json)

| Seed | File | Mutation | Fails |
|---|---|---|---|
| S1 (task a) | lean/VE/Risk/Run.lean | `runDecision` answers with the opposite branch (tables on a conflict, CONFLICT on none) | `risk_decision_wire_sound` does not build (WireSound.lean:229, the closed-list `rfl`) |
| S2 (task b) | lean/VE/Risk/Wire.lean | `regenerated` drops the last `risk_premises` row (a `risk:class` row) | `risk_elaborate_wire_sound` does not build (WireSound.lean:124, `case eq`) |
| S3 (task c) | lean/VE/Risk/Wire.lean | `decodeSupplied` drops its last entry | no proof (exit 0); `tests/test_risk_lean_route.py::test_k10_decision_17` fails: `MissingEntry: E2` |
| S4 | lean/VE/Risk/WireSound.lean | the statement's `leads` table reads `might` | `risk_decision_wire_sound` does not build (WireSound.lean:229) |

The Lean failures are heartbeat timeouts at the `rfl` that equates the runner's answer with the stated list. Each seeded statement is false for the seeded runner (S1: on a model without conflict the answer has `verdict`, the statement `tables`; S2: one row fewer; S4: a different table on any record where `might` and `leads` differ), so no budget would make the proof succeed. S3 is caught by a test, not a proof: the theorems state that `decodeSupplied` returned `supplied` and that `admitDecision` admitted `d` from it, not what the decoder keeps. `tools/select_tests.py --paths lean/VE/Risk/Wire.lean` selects `tests/test_risk_lean_route.py`. Every file was restored byte for byte (`git diff --quiet HEAD` on Run.lean and Wire.lean).

## Spec re-read

- Hypotheses and conclusion shape against the task's step 2 and `VE.Norms.Run.norms_wire_acceptance` / `VE.Time.Wire.quantity_certificate_wire_sound`: the three hypotheses, decoders named, answer fields as definitions of the decoded objects, the replay theorem's conclusion. Done.
- `subject` rule against docs/spec/kernel-boundary.md section 2 (the `subject` row): `runCase … = .ok answer` with `answer` used again; the measurement lists both theorems under `stated["VE.Risk.Run.runCase"]`.
- Verdict-writer census against kernel-boundary.md section 6 item 3 (`docs/spec/kernel-boundary.md:388`): no rise. A first draft defined `DecisionAnswer` holding the literal `"CONFLICT"`; the census counted it (57 outside); the word now sits in the theorem statement as in `lean/VE/Norms/FlaggedSpec.lean:944`, and the count is 56.
- `uncovered` against section 2 and `tools/kernel_closure.py:144-146`: kernel paths only.

## Notes for the DRI

1. **Answer predicates are written inside the theorems.** The task asks for an `…Answer` predicate per kind, as `VE.SoftNorms.Run.SelectedAnswer` does. A draft did that (`ElaborateAnswer`, `DecisionAnswer` and six helpers: S +65 by `tools/trust_map.py --check`, `S grew from 14935 to 15000 (signed allowance 0)`). R16 signs trust growth only for new Lean behaviour; these definitions specify existing code, so the growth would need a DRI signature. kb-8, which the task names as the model, chose to write its predicates out (docs/kernel/kb-8/REPORT.md, note 2). I did the same: S +0, and the statements stay readable with one field per line. If the architect prefers named predicates, that is an S +65 row for the DRI to sign.
2. **The four kinds no key calls are not written as `uncovered`.** The task says to list them as `uncovered` in tools/kernel-paths.json the way kb-8 did. kb-8 listed no `uncovered` entry: its unproved kinds carry no verdict and are under `nonverdict`. `tools/kernel_closure.py` refuses `uncovered` on a candidate path (`registry_problems`: "uncovered on a candidate path"). These four do carry verdicts, so `nonverdict` would be wrong. They are listed here instead. On promotion, the architect seat would add `uncovered` entries `VE.Risk.Run.runConflict` [`risk-conflict`], `runFollowable` [`risk-followable`], `runAudit` [`risk-audit`] and `runCertificate` [`risk-certificate`]. Each already has a replay theorem on an inner function (`risk_wire_conflict_sound`, `risk_wire_followable_sound`, `risk_wire_audit_sound`; certificate none), but none has a runner theorem.
3. **The risk path's wrap (5,670 lines) is not under these theorems.** It is the `else` branch of `runCaseReported` (`lean/VE/Risk/Run.lean:632`): a case with `usesRiskPath j = false` goes to `VE.Alternatives.Run.runCaseReported`, the `alternatives` path's entry, which the `risk` path does not list as a delegate. Every keyed case takes the risk branch (`runCaseReported_ok`). Listing it as a delegate would remove the wrap. That shrinks the route, which is out of scope here.
4. Promotion size: the risk path is 7,989 distinct lines (spec 6,309 + wrap 5,670, overlapping). This is the figure the architect seat weighs against the "up to about 5,800" estimate; the kernel overlap was not measured here.

## Notes

- Code map: `docs/codemap/lean__VE__Risk.md` has no line for the new module (the codemap check is advisory on branches; left to its generator, as the task asked).
- Pre-existing failures: see "Selected run".

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay, schema or answer byte changed; no Python changed).
2. Every deliverable built: PASS. Step 1 CALLS.md (b28ae39ce3); step 2 theorems (ceb580f8c8); step 3 registry and figures (ceb580f8c8 and the report commit); acceptance items in "Checks run". The two deviations are recorded in Notes for the DRI 1 and 2. No Python copy of a Lean decision; no new report test.
3. Tests and gates can fail: PASS. Seeds S1-S4, each with its failing proof or test; trust mutants 0 definitions (nothing trusted added).
4. Python/Lean/Rust agree: PASS. Five harness `results.json` byte-identical; the service binary is the pinned one.
5. R8 binding: N.A. (no field read from a Lean answer added or changed).
6. Gate evidence matches final HEAD: PASS. The selected run is on the committed final tree. The full gate is the chain's job.
7. No unsigned item: PASS. DELTA none; trust K +0, S +0; kernel 9,552 = signed total.
8. Every user-visible change in DELTA: PASS. No user-visible change (`results.json` identical; the service binary is unchanged: same pinned sha256).
9. Test selection finds the tests: PASS. `select_tests.py --base 0f6d59d441` selects `tests/test_kernel_closure.py`, the trust tests and `tests/test_assurance_manifest.py`; `--paths lean/VE/Risk/Wire.lean` selects `tests/test_risk_lean_route.py` (S3's test).
10. Lean statements say what is claimed: PASS. S4 (wrong statement does not build); the theorems are about `runCase`'s returned answer (`h : runCase j = .ok answer`); `tools/check_*_statements.py` all exit 0; no hypothesis added beyond the task's three.
11. Budgets fail closed: N.A. (no budget or limit code changed; a refusal asserts nothing).
12. No CPU or memory regression: N.A. (no executable code changed; harness times are in "Checks run").
13. Test-removed trailers: PASS. None removed; `gate_collection.py --check --prebuilt` 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Each seed shows that a wrong runner or statement fails, and the restored tree builds. Claims cite their commands above. Spec re-read listed.
15. No overclaim, no silent cut: PASS. The words "every" and "all" in this report are tied to the measurement output or to a theorem conjunct. The uncalled kinds are listed as without a runner theorem, not as covered. No deliverable cut; each deviation is explained.
