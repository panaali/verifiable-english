# ps-7: change of state, continuation and iteration (presupposition PLAN PS-7) (build report)

No DRI signature is reserved in this item. There are no DELTA rows: the item adds new Lean that no route reads.
Status: fix round 1 done (review F1). "returns to" carries the amended ruling's guards (f)-(l), the ps-7c latest-stay record and its contract (reviews/dri-decisions-20261110-ps-7-returns.md items 1-3). ps-1-locate-path is closed.
Trusted growth is unchanged at +41 (K +0, S +41), signed by standing ruling R16 (see "Trust"). The new guards are class T.
Checks: `lake build` 0, `lean/audit.py` PASS, `trust_map --check` PASS, trust_mutants 20/20 KILLED (full run), hand mutants
26/26 killed, selected tests (see "Tests"). Open: the full gate on the final HEAD (the chain runs it). Next: ps-7b, then ps-7c.

Feature item ps-7. Branch `feature/ps-7`, merge base a7659c5f1 (main at launch, no merge since). Commits
(`git log --oneline main..HEAD --no-merges`, saved here): 4292cb165, ecf6ece38, 1b48f9029, 174f28449, 293ab15c6,
b018bb556, a70be645e, 7431d107c, c8a84cace, and the docs and comment commits after them. Fix round 1 (review
ps-7-review.final.md F1): c7cdcd3ee (guards and contract), 197bc0ac1 (mutant replay, trust classes, inventories),
c253e8880 (trust-mutants sweep), and this report's commits.

## Preconditions

- **Statement gate.** Decided for this item by the acting DRI (task file). The only theorem statements added are the
  six `<row>_eq` (`rfl`) and six `<row>_defined` (from `generic_defined`) in `Events.lean:71-103`. There is no other
  `theorem`, `lemma` or hypothesis (`grep -n "^theorem" lean/VE/Presupposition/Events.lean`: 12 lines, all of these).
- **Layers.** `tools/check_lean_imports.py` refuses no import from `VE.Presupposition.Events` to `VE.Events.Decl` (both
  layer 2: `lean_layer` probe). Before the `lean/VE.lean` import was added, it reported only "no default target builds"
  for the two new modules. No `layer_policy` edit was made.
- **In-flight overlap.** No branch in `feature/*`, `infra/*`, `lean-first/*` or `foundation/*` touches
  `lean/VE/Presupposition/Events*`, `Frame.lean` or `docs/presupposition/ps-1/REPORT.md` (`git diff --name-only main...<b>`).
  Shared files: `lean/VE.lean` (union-merged import list), `tools/trust-classes.json` and `docs/trust-baseline.json`
  (added entries), and the generated inventories.
- **Not run by me:** the full release gate. The chain runs it on the final HEAD.
- **ps-2ab** (`admit`) is not on main (`lean/VE/Presupposition/Admit.lean` absent at a7659c5f1), so P9 and P10 are at
  formula level only.

## Plan rows delivered

Lift used for every binder added: `VE.Norms.Term.shift` (`lean/VE/Norms/Basic.lean:311`). x, t and p are terms of the
hole's context. Each is shifted once per binder added above it.

| Row (task "Deliver") | Commit | Evidence (Events/Examples.lean lines; E = Events.lean) |
|---|---|---|
| (1) IP_S(x, t) (`inProgress`, events' "is in progress on" formula) | 4292cb165 | :43-44, :150 (variable stay) |
| (1) "stops"/"ceases" `stops`, "continues"/"remains" `continues`, "no longer" `noLonger`: pre `inProgressBefore` | 4292cb165 | :49-59 |
| (1) "resumes" `resumes`: pre `endedBefore` (∃y:S. ∃u. ends_S(y,u) ∧ before(u,t)) | 4292cb165 | :64-69 |
| (1) "again" `again`: pre `occurredBefore` (∃y:E. ∃u. on_E(y,u) ∧ before(u,t)) | 4292cb165 | :75-78 |
| (1) "returns to" `returnsTo`: pre `endedAtBefore` (DRI ruling item 1; conditions (a)-(e)) | 1b48f9029 | (a) :85, (b) :86, (c) :87-88, (d) :89, (e) :93-94 |
| "returns to", amended ruling (reviews/dri-decisions-20261110-ps-7-returns.md items 1-2; note ps-7-dri-note-20261110-next.md): guards (f)-(l), each body value where the guard involves the body | c7cdcd3ee | (f) :117, (g) :119, (h) :121, (i) :123, (j) :127-129, (k) :132, :134 (occupancy), (l) :136-138 |
| latest-stay limit (ruling item 3): today's value in structure (k) for "returns to" and "resumes", marked "row ps-7c" | c7cdcd3ee | :141-142 |
| (1) `_eq` by `rfl`, `_defined` via `generic_defined` | 4292cb165, 1b48f9029 | E:71-103; `lean/axioms.txt`: none uses any axiom |
| (2) both directions per row; no-end state (persistence not assumed); state beginning on t | ecf6ece38, b018bb556 | :43 (noEnd vs endA), :46, :49 (onT false) |
| (2) variable day under a universal, variable stay or place under an existential | ecf6ece38, 293ab15c6 | :147-162 |
| (2) `continues.strong` holds exactly where the state is in progress before and on t | ecf6ece38 | :54-55 |
| (3) P9 within the phrase (one reading); contrast where "ongoing" is read as `ip` | ecf6ece38, b018bb556 | :170-178 |
| (3) P10 {assumed, conditioned} differ where the firmness begins on t | ecf6ece38 | :183-184 |
| (4) UDHR u055 / u067 "change" as "stops" on the earlier state | ecf6ece38 | :192-193 |
| (5) ps-1-locate-path: `locate` reclassed S; path guards; dated correction in ps-1 REPORT | 174f28449, b018bb556 | :204-206; `docs/presupposition/ps-1/REPORT.md` row "(6) correction" |
| (6) `lean/VE.lean` imports, Audit.lean, trust classes, inventories via `regen_generated.py --write` | 7431d107c, 197bc0ac1 | regen "wrote 38 entries", exit 0; `--check` exit 0 |
| situations satisfy events' premises (structures (f)-(k) included, (i) too); an end before the begin is refused | b018bb556, c7cdcd3ee | :197-201 |

**ps-1-locate-path: closed.** `tools/trust-classes.json` now classes `VE.Presupposition.Frame.locate` as S. The new guards
:204 (orL arm) and :205-206 (the `.and` arm at path [0] and at [1]) fail for a path-ignoring `locate`, the review's
mutant (hand mutants M-locate-path and M-locate-orL-none). No theorem statement was added.

Not built here (task): "still" and "stop … from" are not rows. The act readings ("Claude stops doing A", "does A
again", "continues to do A") need ET-D2 and go to **ps-7b**, a backlog row that already exists (blocked on ET-D2).

## Deviations and readings chosen

- **"returns to": contract (reviews/dri-decisions-20261110-ps-7-returns.md item 1; also the `returnsTo` doc comment,
  `Events.lean:61-67`).** "X returns to P on t" takes for granted an earlier stay of X at P that ended before t, and
  asserts a new arrival at P on t. The caller supplies an arrival body; occupancy is not a return (guard (k) :134: an
  occupancy body gives strong T where X never arrived on t). The instances of S are the subject's own stays. Stays that
  end on t itself are a limit of the day-level model (guard (h) :121: pre F, weak T). The reason for ENDS is that
  departure projects: "X did not return to P" said of an X who never left is not true, and "if X returns to P on t, ..."
  commits the writer to X having left (guards (f) :117 and (l) :136-138). It is not "conservative": ENDS and BEGINS are
  not ordered (guard (i) :123: an end with no begin day satisfies ENDS only). The definition is unchanged.
- **The latest-stay limit (ruling item 3), shared with "resumes", goes to row ps-7c.** Both pres ask for some earlier
  stay that ended, not that X was away just before t. In structure (k) (a stay at p ended on a, a new stay at p from b
  with no end day) the pre is T today, so weak follows the body. Guard :141-142, marked "latest-stay limit, row ps-7c",
  records today's values for both rows, so a "latest stay ended" pre flips it visibly. The `resumes` doc comment names
  the limit.
- **The arrival body in guards (f)-(l)** is `arrives(p, t)`, the subject's own arrival with the subject left implicit
  (VE's formulas have no ternary atom; the note allows a stand-in). Each structure is built without and with the arrival
  fact (`ret r false` / `ret r true`), so body F and body T are two structures, not two constant bodies. G in (j) is
  "the subject is at p", true on the never-left structure, so the carrier is not vacuous. (j) is checked both as the
  literal `G → (pre → body)` (`(impR G hole).plug weak`) and as the reviewed `conditionedAt (impR G hole)`.
- **P9 (u0220.s06).** The task's test is "body entails pre on every fixture situation". With the trigger's body as
  IP_S(x, t), that is false on `onT`, where the action begins on t. I read "an ongoing action" as "in progress before
  t", the phrase's left conjunct, with the trigger "continuing" in its right conjunct (frame `andR ongoing hole`). The
  projected goal `ongoing → pre` then holds on every situation, and asserted, conditioned and in place all equal the
  weak plug (:170-172). The phrase's content `ongoing ∧ IP` entails the pre on every situation (:175). The one reading
  rests on this choice: :176-178 show that with "ongoing" read as `ip` the goal fails on `onT` and asserted and
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

`mutants.json`: 26 hand mutants, all killed (all replayed on c7cdcd3ee after guards (f)-(l) went in; each `test` list is
that replay's error locations). To replay one, apply its find/replace, run
`lake build VE.Presupposition.Events.Examples`, then restore the file. The task's five:

| Seeded bug (task) | Mutant | File | Fails |
|---|---|---|---|
| "stops" pre without before(u, t) | M-stops-no-before | lean/VE/Presupposition/Events.lean | Events/Examples.lean:49 (onT) and 7 others |
| IP_S without the ends clause | M-ip-no-ends | lean/VE/Presupposition/Events.lean | :43 (noEnd/endA), :54, :58 and others |
| "resumes" with before(t, u) | M-resumes-reversed | lean/VE/Presupposition/Events.lean | :64, :65, :67, :141 (ps-7c record), :155 |
| "again" with another event sort | M-again-sort | lean/VE/Presupposition/Events.lean | :75, :158 |
| a missing lift under a binder | M-ipb-lift-t | lean/VE/Presupposition/Events.lean | :147 (variable day), :154, :162 |

Each new trusted definition has its own mutants:
- `inProgress`: 5 mutants (incl. M-ip-lift-x-inner, killed by :150, the fixture added for that survivor).
- `inProgressBefore`: 3.
- `endedBefore`: 4 (M-resumes-ends-begins added in fix round 1: the M-ret-ends-begins class in the shared "resumes" pre;
  killed by :64-65, :69, :155).
- `occurredBefore`: 3.
- `endedAtBefore`: the DRI's three (M-ret-no-at, M-ret-reversed, M-ret-lift-p) and M-ret-ends-begins (`ends_S` → `begins_S`,
  the amended ruling's condition). M-ret-ends-begins is killed by (f) :117, (h) :121, (i) :123, (j) :127 and (l) :136, as
  well as (a) :85, (d) :89 and (e) :93. Guard (k) cannot kill it: in structure (k) the current stay z begins at p on b,
  before t, so the BEGINS pre is true there as the ENDS pre is (through y), and every (k) value agrees. The note asks for
  (f), (i) or (k); the ruling's condition line says "(f), (i) and (k)", and (f) and (i) are what can kill it.
- each reading row: 1 (`_eq` fails to elaborate).
- `Frame.locate`: 2.

**R16 sweep** (`trust-mutants.json`, through `mac-pytest.sh --trustmut -- --max-mutants 1000 --test
lean/VE/Presupposition/Events/Examples.lean`): 5 definitions, 20 mutants, 20 KILLED, 0 SURVIVOR, exit 0. Full run (not
rescored) on 197bc0ac1, after the fix round's Lean edits (ran on ve-cloud-3, 138 s). No allow file was needed.

## Trust

`uv run python tools/trust_map.py --check`: PASS. The measurement against a7659c5f12ae: K +0, S +41, G +27 (tied +27),
unclassified +0, trusted +41 (unchanged by fix round 1):
- `lean/VE/Presupposition/Events.lean` +28: S `inProgress`, `inProgressBefore`, `endedBefore`, `occurredBefore`,
  `endedAtBefore`. The doc comments added in fix round 1 sit on the G rows `resumes` and `returnsTo` (G +7), not
  on an S definition. The six readings are G[V], tied by their `_eq` statements to `generic` and their pre.
- `lean/VE/Presupposition/Frame.lean` +13: `locate`, C → S.

The allowance is in `docs/trust-baseline.json`: "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-7, 2026-11-10",
with the per-file counts in its reason. The ties-pass row was filed under "## ps-7" in FOLLOW-UPS.md on the
ve-cloud-3 mirror. This host's /home/seyran/code/manage-agents/FOLLOW-UPS.md has no "## ps-7" section (review F3, C: a
sync follow-up, not done here).
The new fixture definitions of guards (f)-(l) (`ret`, `arrival`, `retR`, `retV`, the five structures, `retCases`,
`stayingAtP`, `occupancy`) are class T in `tools/trust-classes.json`.

## Size, bytes, evaluators

- **Size.** `git diff --numstat a7659c5f1`, hand-written lines only. Generated inventories, codemap,
  `trust-mutants.json` and `trust-baseline.json` are excluded. Counts: Events.lean 96, Events/Examples.lean 159,
  VE.lean 2, trust-classes.json 85, ps-1 REPORT 1, DELTA.md 13, mutants.json 30, and this report. The total is under
  the ~600 limit, and nothing was cut.
- **Bytes.** 0 claimed. The plan estimates 36-46 constitution units (6,887-9,641 B) become expressible once the English
  rows (English queue, after PS-6) and ps-7b land. That is an estimate; no pilot audit was run.
- **Evaluators.** N.A.: no evaluator, runner or mode is added. The guards use the existing `Formula.eval`.

## Tests

Selected tests on the committed tree d91f40626 (`MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base a7659c5f1 --run`):
exit 0, run on GitHub Actions in 5 shards (ps-7-d91f4062-t296721): 24 + 26 + 25 + 25 + 16 = 116 units, all passed, 0
failed. The Lean condition guards (Events/Examples.lean and the existing Presupposition and Events Examples) are
checked by the full `lake build` (exit 0). After that run, only this report changed.

## Spec re-read

- `inProgress` against `docs/spec/events-time-causation-PLAN.md:352` and `lean/VE/Events/Examples.lean:109`: same
  formula, with the constants replaced by lifted terms. :114 checks that a variable-0 day agrees with the constant.
- The readings against `docs/spec/presupposition.md:100`: `generic pre body` = (pre, pre ∧ body, pre → body).
  `Rows.lean:22` gives the same, by `rfl`.
- The rows against `docs/spec/presupposition-PLAN.md:993-1003`. "continues" = "before and on" is checked at :54-55.
  "no longer" = "before, not on" at :58-59.
- "returns to" against reviews/dri-decisions-20261110-ps-7.md item 1: the formula, x unused, p lifted, and (a)-(e).
- "returns to" against reviews/dri-decisions-20261110-ps-7-returns.md items 1-3 and reviews/ps-7-dri-note-20261110-next.md:
  each of (f)-(l) has the values the note gives, in the same order (pre, strong, weak), for each body value it names;
  the structures pass events' premises (:197-200), (i) included; no definition and no statement changed.
- P9 and P10 against `docs/spec/presupposition-PLAN.md:583-584`: see "Deviations".

## Self-review against BUILDER-CHECKLIST

1. Typed and contained answers: N.A., no relayed answer or schema changes (DELTA.md).
2. Deliverables: PASS, the "Plan rows delivered" table; the one task-directed cut (act rows) goes to ps-7b.
3. Tests can fail: PASS, `mutants.json` 26/26 and `trust-mutants.json` 20/20.
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
15. No overclaim or silent cut, new checks can fail: PASS. The self-review B findings are fixed (P9 contrast :176, pre/end
    pin :46), and every guard family has a killing mutant.

SELF-REVIEW: 0 A, 2 B, 6 C; fixed 7
