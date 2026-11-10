# ps-7: change of state, continuation and iteration (presupposition PLAN PS-7) (build report)

No DRI signature is reserved in this item. There are no DELTA rows: the item adds new Lean that no route reads.
Status: built. All rows are in, "returns to" included (DRI ruling reviews/dri-decisions-20261110-ps-7.md item 1), and
ps-1-locate-path is closed. Trusted growth is +41 (K +0, S +41), signed by standing ruling R16 (see "Trust").
Checks: full `lake build` 0, `lean/audit.py` PASS, `trust_map --check` PASS, trust_mutants 20/20 KILLED, hand mutants
25/25 killed, selected tests (see "Tests"). Open: the chain runs the full gate on the final HEAD. Next: ps-7b (act readings, after ET-D2).

Feature item ps-7. Branch `feature/ps-7`, merge base a7659c5f1 (main at launch, no merge since). Commits
(`git log --oneline main..HEAD --no-merges`, saved here): 4292cb165, ecf6ece38, 1b48f9029, 174f28449, 293ab15c6,
b018bb556, a70be645e, 7431d107c, c8a84cace, and the docs and comment commits after them.

## Preconditions

- **Statement gate.** Decided for this item by the acting DRI (task file). The only theorem statements added are the
  six `<row>_eq` (`rfl`) and six `<row>_defined` (from `generic_defined`) in `Events.lean:64-96`. There is no other
  `theorem`, `lemma` or hypothesis (`grep -n "^theorem" lean/VE/Presupposition/Events.lean`: 12 lines, all of these).
- **Layers.** `tools/check_lean_imports.py` refuses no import from `VE.Presupposition.Events` to `VE.Events.Decl` (both
  layer 2: `lean_layer` probe). Before the `lean/VE.lean` import was added, it reported only "no default target builds"
  for the two new modules. No `layer_policy` edit was made.
- **In-flight overlap.** No branch in `feature/*`, `infra/*`, `lean-first/*` or `foundation/*` touches
  `lean/VE/Presupposition/Events*`, `Frame.lean` or `docs/presupposition/ps-1/REPORT.md` (`git diff --name-only main...<b>`).
  Shared files: `lean/VE.lean` (union-merged import list), `tools/trust-classes.json` and `docs/trust-baseline.json`
  (added entries), and the generated inventories.
- **ps-2ab** (`admit`) is not on main (`lean/VE/Presupposition/Admit.lean` absent at a7659c5f1), so P9 and P10 are at
  formula level only.

## Plan rows delivered

Lift used for every binder added: `VE.Norms.Term.shift` (`lean/VE/Norms/Basic.lean:311`). x, t and p are terms of the
hole's context. Each is shifted once per binder added above it.

| Row (task "Deliver") | Commit | Evidence (Events/Examples.lean lines; E = Events.lean) |
|---|---|---|
| (1) IP_S(x, t) (`inProgress`, events' "is in progress on" formula) | 4292cb165 | :43-44, :102 (variable stay) |
| (1) "stops"/"ceases" `stops`, "continues"/"remains" `continues`, "no longer" `noLonger`: pre `inProgressBefore` | 4292cb165 | :49-59 |
| (1) "resumes" `resumes`: pre `endedBefore` (∃y:S. ∃u. ends_S(y,u) ∧ before(u,t)) | 4292cb165 | :64-69 |
| (1) "again" `again`: pre `occurredBefore` (∃y:E. ∃u. on_E(y,u) ∧ before(u,t)) | 4292cb165 | :75-78 |
| (1) "returns to" `returnsTo`: pre `endedAtBefore` (DRI ruling item 1; conditions (a)-(e)) | 1b48f9029 | (a) :85, (b) :86, (c) :87-88, (d) :89, (e) :93-94 |
| (1) `_eq` by `rfl`, `_defined` via `generic_defined` | 4292cb165, 1b48f9029 | E:64-96; `lean/axioms.txt`: none uses any axiom |
| (2) both directions per row; no-end state (persistence not assumed); state beginning on t | ecf6ece38, b018bb556 | :43 (noEnd vs endA), :46, :49 (onT false) |
| (2) variable day under a universal, variable stay or place under an existential | ecf6ece38, 293ab15c6 | :99-114 |
| (2) `continues.strong` holds exactly where the state is in progress before and on t | ecf6ece38 | :54-55 |
| (3) P9 within the phrase (one reading); contrast where "ongoing" is read as `ip` | ecf6ece38, b018bb556 | :122-130 |
| (3) P10 {assumed, conditioned} differ where the firmness begins on t | ecf6ece38 | :135-136 |
| (4) UDHR u055 / u067 "change" as "stops" on the earlier state | ecf6ece38 | :144-145 |
| (5) ps-1-locate-path: `locate` reclassed S; path guards; dated correction in ps-1 REPORT | 174f28449, b018bb556 | :155-157; `docs/presupposition/ps-1/REPORT.md` row "(6) correction" |
| (6) `lean/VE.lean` imports, Audit.lean, trust classes, inventories via `regen_generated.py --write` | 7431d107c | regen "wrote 38 entries", exit 0 |
| situations satisfy events' premises; an end before the begin is refused | b018bb556 | :149-153 |

**ps-1-locate-path: closed.** `tools/trust-classes.json` now classes `VE.Presupposition.Frame.locate` as S. The new guards
:155 (orL arm) and :156-157 (the `.and` arm at path [0] and at [1]) fail for a path-ignoring `locate`, the review's
mutant (hand mutants M-locate-path and M-locate-orL-none). No theorem statement was added.

Not built here (task): "still" and "stop … from" are not rows. The act readings ("Claude stops doing A", "does A
again", "continues to do A") need ET-D2 and go to **ps-7b**, a backlog row that already exists (blocked on ET-D2).

## Deviations and readings chosen

- **P9 (u0220.s06).** The task's test is "body entails pre on every fixture situation". With the trigger's body as
  IP_S(x, t), that is false on `onT`, where the action begins on t. I read "an ongoing action" as "in progress before
  t", the phrase's left conjunct, with the trigger "continuing" in its right conjunct (frame `andR ongoing hole`). The
  projected goal `ongoing → pre` then holds on every situation, and asserted, conditioned and in place all equal the
  weak plug (:122-124). The phrase's content `ongoing ∧ IP` entails the pre on every situation (:127). The one reading
  rests on this choice: :128-130 show that with "ongoing" read as `ip` the goal fails on `onT` and asserted and
  conditioned differ there. P9 is a state reading (the action as a state instance, spec 2.1's example). Its agent
  part ("Claude continuing with") is ps-7b's.
- **The "ended before every earlier day" fixture.** Task (2) asks for a pre that fails where the state ended. Under
  events' premises a state is in progress on its own begin day (an end is never before the begin,
  `events:not_before_begin`). So "in progress before t" holds exactly when the state began before t, and no stated end
  can make it false. The guard at :46 pins this (noEnd and endA give the same pre). Persistence is shown where it
  applies: IP at t (:43, noEnd true and endA false), `continues.strong` (:54) and `noLonger.strong` (:58). The pre
  fails where the state begins on t (`onT`) or never begins (`none0`) (:49).
- **"stops" and "no longer" share a pre, and here a body (`¬IP_S(x, t)`).** The pre does not place the stopping at t,
  so on `endA` "s stops on c" is true for a stay that ended on a. Placing it at t is the translator's body (English
  queue).
- **UDHR "change" (4).** This is expressed with existing rows: "stops" on the earlier nationality or religion state,
  plus a new state that begins on t. The guards: true on `changed`; false and the pre unmet on `stateless`, where weak
  holds vacuously. The agent ("everyone … to change") and the right around it are ps-7b's and the act phrases'. No
  row was added.
- **P10's assumed reading at formula level.** It is `close pre ∧ plug strong` (the before part as its own unit, then
  the clause) at the hole. ps-2ab's `admit` checks it when it lands.

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json`: 25 hand mutants, all killed. To replay one, apply its find/replace, run
`lake build VE.Presupposition.Events.Examples`, then restore the file. The task's five:

| Seeded bug (task) | Mutant | File | Fails |
|---|---|---|---|
| "stops" pre without before(u, t) | M-stops-no-before | lean/VE/Presupposition/Events.lean | Events/Examples.lean:49 (onT) and 7 others |
| IP_S without the ends clause | M-ip-no-ends | lean/VE/Presupposition/Events.lean | :43 (noEnd/endA), :54, :58 and others |
| "resumes" with before(t, u) | M-resumes-reversed | lean/VE/Presupposition/Events.lean | :64, :65, :67, :107 |
| "again" with another event sort | M-again-sort | lean/VE/Presupposition/Events.lean | :75, :110 |
| a missing lift under a binder | M-ipb-lift-t | lean/VE/Presupposition/Events.lean | :99 (variable day), :106, :114 |

Each new trusted definition has its own mutants:
- `inProgress`: 5 mutants (incl. M-ip-lift-x-inner, killed by :102, the fixture added for that survivor).
- `inProgressBefore`: 3.
- `endedBefore`: 3.
- `occurredBefore`: 3.
- `endedAtBefore`: the DRI's three (M-ret-no-at, M-ret-reversed, M-ret-lift-p) and M-ret-ends-begins.
- each reading row: 1 (`_eq` fails to elaborate).
- `Frame.locate`: 2.

**R16 sweep** (`trust-mutants.json`, through `mac-pytest.sh --trustmut -- --max-mutants 1000 --test
lean/VE/Presupposition/Events/Examples.lean`): 5 definitions, 20 mutants, 20 KILLED, 0 SURVIVOR, exit 0. It was
rescored after the last Lean edit, a comment, and all 20 verdicts carried. No allow file was needed.

## Trust

`uv run python tools/trust_map.py --check`: PASS. The measurement against a7659c5f12ae: K +0, S +41, G +20 (tied +20),
trusted +41:
- `lean/VE/Presupposition/Events.lean` +28: S `inProgress`, `inProgressBefore`, `endedBefore`, `occurredBefore`,
  `endedAtBefore`. The six readings are G[V], tied by their `_eq` statements to `generic` and their pre.
- `lean/VE/Presupposition/Frame.lean` +13: `locate`, C → S.

The allowance is in `docs/trust-baseline.json`: "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-7, 2026-11-10",
with the per-file counts in its reason. The ties-pass row is in /home/seyran/code/manage-agents/FOLLOW-UPS.md under
"## ps-7".

## Size, bytes, evaluators

- **Size.** `git diff --numstat a7659c5f1`, hand-written lines only. Generated inventories, codemap,
  `trust-mutants.json` and `trust-baseline.json` are excluded. Counts: Events.lean 96, Events/Examples.lean 159,
  VE.lean 2, trust-classes.json 85, ps-1 REPORT 1, DELTA.md 13, mutants.json 30, and this report. The total is under
  the ~600 limit, and nothing was cut.
- **Bytes.** 0 claimed. The plan estimates 36-46 constitution units (6,887-9,641 B) become expressible once the English
  rows (English queue, after PS-6) and ps-7b land. That is an estimate; no pilot audit was run.
- **Evaluators.** N.A.: no evaluator, runner or mode is added. The guards use the existing `Formula.eval`.

## Tests

Selected tests: the final run is on the committed tree (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select`); its result is
recorded below.

## Spec re-read

- `inProgress` against `docs/spec/events-time-causation-PLAN.md:352` and `lean/VE/Events/Examples.lean:109`: same
  formula, with the constants replaced by lifted terms. :114 checks that a variable-0 day agrees with the constant.
- The readings against `docs/spec/presupposition.md:100`: `generic pre body` = (pre, pre ∧ body, pre → body).
  `Rows.lean:22` gives the same, by `rfl`.
- The rows against `docs/spec/presupposition-PLAN.md:993-1003`. "continues" = "before and on" is checked at :54-55.
  "no longer" = "before, not on" at :58-59.
- "returns to" against reviews/dri-decisions-20261110-ps-7.md item 1: the formula, x unused, p lifted, and (a)-(e).
- P9 and P10 against `docs/spec/presupposition-PLAN.md:583-584`: see "Deviations".

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A., no relayed answer or schema changes (DELTA.md).
2. Deliverables: PASS, the "Plan rows delivered" table; the one task-directed cut (act rows) goes to ps-7b.
3. Tests can fail: PASS, `mutants.json` 25/25 and `trust-mutants.json` 20/20.
4. Py/Lean/Rust agreement: N.A., no Python or Rust product code changes.
5. R8 binding: N.A., no relay.
6. Gate evidence: PASS. The chain runs the gate on the final HEAD; the selected run is on the committed tree.
7. Unsigned items: PASS. `trust_map --check` exits 0 with the R16 allowance; DELTA has no rows.
8. DELTA: PASS, no route reads the new modules (DELTA.md grep).
9. Test selection: PASS, the `--select` run on this branch (see "Tests").
10. Statements: PASS, 12 statements (only `rfl` and `generic_defined`); `lean/audit.py` PASS; `lean/axioms.txt` lists no
    axioms for them. Mutating a reading breaks its `_eq` (M-*-row).
11. Budgets and limits: N.A., no evaluator or limit.
12. CPU/memory: N.A., new fixture module only. Built in about 4 s (`lake build VE.Presupposition.Events.Examples`).
13. Test-removed trailers: N.A., no test removed.
14. Both directions, cited evidence, spec re-read: PASS. Each row has true and false guards (table), with the "Spec
    re-read" section above.
15. No overclaim or silent cut, new checks can fail: PASS. The self-review B findings are fixed (P9 contrast :128, pre/end
    pin :46), and every guard family has a killing mutant.

SELF-REVIEW: 0 A, 2 B, 6 C; fixed 7
