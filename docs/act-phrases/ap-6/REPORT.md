# AP-6: more than two bound slots (decision D6): report

No DRI signature is reserved in this item. No DELTA row: nothing merged changes a verdict, a route or a trusted file.

**D6 outcome: "not yet"** under the conservative reading of bar row 2 taken here (section 5). u019 and u057 stay
co-blocked (389 B). Route (a) proves its statement with no new axiom and changes no existing theorem statement. It
checks the fixtures within 1.25× only when its hypothesis `OneEventPerTuple` is left out of the checked premises
(ratios 1.05, 1.09, 1.17). With the hypothesis stated as premises, the ratios are 1.29, 1.29 and 1.29. Route (b) was
not finished in the timebox: one of the 25 `VE.Norms` modules was re-proved over `VE.Core.Formula`.

Plan and spec: `docs/spec/act-phrases-PLAN.md` "AP-6" (lines 1045–1072), D6 (line 169), section 3's route statements
(lines 695–705), the register row (line 1394); `docs/spec/act-phrases.md` section 9. The spec on this branch differs
from 476b99b92's only outside section 9. Section 9 marks the AP-6 statements "not for build review": they are the
experiment's own, and the task assigns the item. Nothing on `main`'s product files changes; the routes live on the local
branches `scratch/ap-6-route-a` and `scratch/ap-6-route-b` (not pushed, not merged), saved as `route-a.patch` and
`route-b.patch`.

## 1. Step 0: u057's act phrase (MEASURED)

Probe, run with `cd lean && lake env lean <file>` on this branch's base (8eda0371fd), vocabulary `ap 3` of
`lean/VE/Acts/GrammarExamples.lean:392` (`marry` takes no object, `found` a direct one):

```lean
import VE.Acts.MeaningExamples
open VE.Acts VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.MeaningExamples
#eval rawOf (ap 3) [] "{0} to marry and to found a family"      -- some 1
#eval n (ap 3) [] "{0} to marry and to found a family"          -- some 0
#eval rd1 (ap 3) [] "{0} to marry and to found a family"        -- VE.Acts.ReadOutcome.none
#eval rawOf (ap 3) [] "{0} to found a family and to marry"      -- some 1
#eval n (ap 3) [] "{0} to found a family and to marry"          -- some 1
#eval rd1 (ap 3) [] "{0} to found a family and to marry"
-- .ok (.all false false [{toWord := true, head := ["found"], args := [("", .one (.words ["a", "family"]))]},
--                        {toWord := true, head := ["marry"], args := []}])
```

- The source phrase still has no reading on `main`: one raw derivation, no meaning, `read` → `none` (as X057 pins at
  `MeaningExamples.lean:95` and `RuleExamples.lean:82`). No grammar pattern is added in this item.
- The plan's rewording "to found a family and to marry" reads with exactly one meaning: an `all` join (no modal word)
  of *found a family* and *marry*. u057 stays in the fixture set, reworded.

## 2. The fixtures (`fixtures/`, written by `fixtures/make.py`)

| Fixture | Source | Act with two bound non-subject slots | Rules |
|---|---|---|---|
| u019 | UDHR Article 2 ("without distinction of any kind, such as race, …") | `distinguish(bearer, person, ground)` | r019: must not, if the ground is listed |
| u057 | UDHR 16(1), reworded per step 0 | `limit(bearer, person, ground)`, beside the two parts of "to found a family and to marry" | the two parts (if of full age); r057-l: must not limit, if of full age and the ground is race, nationality or religion |
| μ | `docs/spec/rights.md:1360`, `publish_about(person, item, person)` | `publish_about(person, item, person)` | r19 (liberty of right 19) with right 12's claim as its condition: may publish, unless the item attacks the honour of the person it is about |

Each fixture is written three ways, in AST form (`ve-document@1`), each with its facts and one claim:

- `<f>.binary.ve.md`: the binary route, as today's language can state it: the act's last bound slot dropped (u019 and
  u057: the ground; μ: the person the item is about), with the guard conjunct on it dropped (μ's guard is rewritten
  over the item alone).
- `<f>.reified.ve.md`: route (a), the act reified as the event sort `distinction` / `limitation` / `publication` with
  one role predicate per slot; each guard is `reifyFormula` of the source guard (the shape `NaryExamples.lean` pins).
- `<f>.reified-otp.ve.md`: the same, with route (a)'s hypothesis `OneEventPerTuple` stated as six premises (each role
  functional and total on the event sort, an event for every filler pair, at most one).

A `ve-document@1` environment carries no `events` block today: `ve document check` refuses one with `fields do not
match: expected [language, profiles, spec_revision, vocabulary], got [events, …]` (probe on a draft of u019.reified).
So the reified documents declare the event sort and roles as plain vocabulary, and the `events@0` pack's own premises
(one `on` day per event) are not in them. The six μ statements of rights.md (CONFLICT, weighing, ranks) need
`rights@0`; this fixture keeps only its act and the honour condition.

## 3. Route (a): reification over `events@0` event sorts (scratch/ap-6-route-a, `route-a.patch`)

**Statement as built** (`lean/VE/Acts/Nary.lean:431` on the scratch branch), section 3's text unchanged:

```lean
theorem VE.Acts.Nary.reify_faithful (D : ActsDoc) (S : VE.Structure.{u}) (hc : OneEventPerTuple D S) :
    VE.Norms.holdsCatala (reify D).T S ↔ NaryIntended D S
```

**Definitions written** (none existed; spec section 9 and `lean/VE/Core/NARY.md` give only their names and intent):

- `NaryReg`: an act with k ≥ 2 bound non-subject slots: name, holder sort, slot sorts, default, role, act, permission,
  the event sort, and one role predicate per slot. `NaryReg.reg` is the act at its source arity k + 1;
  `NaryReg.reified` is the same predicate over `[holder, event]`.
- `Valid` and `ActsDoc`. `ActsDoc` holds the environment, the `events@0` block (`VE.Events.EventsEnv`), the binary
  regulated predicates, the n-ary acts, the definitions and the rules as written. It carries `valid : Valid …`: names
  distinct; 2 to 5 slots; one role per slot; the event sort is one of the block's event sorts; each role is declared
  `(event, slot sort)` and is not the act's name. This is a new `VE.Acts.Nary.ActsDoc`, not AP-3's `VE.Acts.ActsDoc`,
  which has no n-ary act.
- `reifyFormula a φ := exRoles 0 a.pairs (liftAt k φ)`: `∃x₁ … ∃xₖ. role₁(e, x₁) ∧ … ∧ roleₖ(e, xₖ) ∧ φ`.
  `reifyNode` applies it to a rule's guard and carve-outs on an n-ary act and leaves every other rule as written.
  `source D` is the tree as written; `reify D` is the binary document.
- `RolesHold S e rs xs`: the event's fillers, each of its slot's sort. `ActHolds S a h xs`: some event of the act's
  sort has the fillers `xs`, and `h` stands in the act to it.
- `OneEventPerTuple D S`: for each n-ary act, every event of its sort has exactly one filler tuple, and every typed
  filler tuple exactly one event.
- `NaryIntended D S`: the binary predicates are read by `IntendedAt (source D)`. For each n-ary act, on every typed
  tuple `h :: xs` the source rules, read below the act (`forget [a.name] S`), give a value `b` (`VE.Norms.Value`), and
  `ActHolds S a h xs ↔ b = true`.

**Proof status: proved, no `sorry`.** The proof uses a tracking lemma (`decides_track`): two trees whose node lists
correspond node by node (same name, predicate, sign and `over`) decide alike when each node applies alike. It also
uses `liftAt_denote`, `exRoles_denote`, `reifyFormula_denote` and `value_nary`: 27 theorems in all.

**Axioms** (MEASURED, `python3 lean/audit.py` on the scratch branch after `tools/lean_statements.py` and
`audit.py --write`): `PASS: 856 source files; 9587 named theorem declarations audited …; only the declared standard
axiom allowlist.` `reify_faithful` depends on `[propext, Classical.choice, Quot.sound]` (`lean/axioms.txt` line 184 on
the scratch branch, in `route-a.patch`).

**Theorem-statement diff** (MEASURED): `git diff feature/ap-6 scratch/ap-6-route-a -- lean/statements.txt` adds 179
lines (27 `theorem` entries, all `VE.Acts.Nary.*`) and removes 0. `tools/lean_statements.py` reported `removed: 0`,
`changed: 0`. The only other source change is two `import` lines in `lean/VE.lean`.

**Fixture guards** (`lean/VE/Acts/NaryExamples.lean`, scratch). Each fixture's `ActsDoc` is built with
`valid := by decide`. `#guard fixtures.all (fun D => WellFormed (reify D))`: each reified fixture passes today's binary
norms check. Other guards pin the reified guards of r019 and of μ's two rules, check that u057's binary parts are
untouched, and give the arities (reified 2, source 3).

Size: `Nary.lean` 481 lines, `NaryExamples.lean` 82 lines (scratch; not counted).

## 4. Route (b): arity lifted over `VE.Core.Formula` (scratch/ap-6-route-b, `route-b.patch`)

Stopped at the timebox. How far it got:

- **B1, the lift alone** (commit afc49cb06a; MEASURED by building `VE` after each step):
  - `Arity` became `1 ≤ n ∧ n ≤ 6`. The four executable copies of the check moved with it (`Tree.lean` `check` and
    `semanticCheck`, `Once.lean`, `Family.lean`).
  - Two `VE.Norms` theorems no longer build: `atom_denote` (`Basic.lean`) and `atom_wellFormed` (`Elaborate.lean`).
    Both are false for arity 3 to 6 over `VE.Formula`, whose atoms are unary or binary only (`atom` gives `bottom`),
    so the formula type has to change.
  - Outside `VE.Norms`, `VE.NormDefaults.Check` stopped next (`check_eq := rfl` at line 150: "Not a definitional
    equality"). The probe stopped there.
- **B2, `VE.Norms.Basic` re-proved over `VE.Core.Formula`** (commit 798a08fc49; MEASURED). `lake build VE.Norms.Basic`
  succeeds with no `sorry`: `atom` gives `.atom p (vars n)` for arity 3 to 6, and `atom_denote` holds for 1 to 6.
  - Each of the five formula inductions (`wf_mono`, `denote_forget`, `inst`, `inst_denote`, `inst_wellFormed`) gains
    the `atom`, `reachNamed` and `reachBody` cases.
  - Seven helper theorems are new (`vars_mapM`, `mapM_sortOf_congr`, `forget_relation'`, `term_denote_forget`,
    `mapM_inst_denote`, `mapM_inst_sortOf`, `lift_sortOf`).
  - Size: `git diff --numstat feature/ap-6 scratch/ap-6-route-b -- lean/VE/Norms/Basic.lean` gives **+180 −45** (the
    45 are the renamed type).
- **B3, the type renamed in 18 more `VE.Norms` files** (commit db114f6a20, a probe: 165 lines renamed).
  `lake build VE.Norms.Elaborate` stops in `Tree.lean` on three executable definitions, not theorems:
  - `preds` and `typeDiagnostic` lack the new cases. `typeDiagnostic`'s texts are Python's, so a new case is a
    cross-language diagnostic change.
  - `check`'s node budget calls `VE.Bridge.formulaNodes`, which is over `VE.Formula`.

  Nothing downstream of `Tree.lean` was built.

**Break count** (MEASURED from this branch's `lean/statements.txt` and `lean/declarations.txt`):

| Class | Theorems | Theorem lines |
|---|---|---|
| `VE.Norms` theorems with a source range | 384 | 4,202 |
| statement mentions `VE.Formula`, `VE.Term` or `VE.Valuation` (restated over `VE.Core.Formula`) | 158 | 2,143 |
| statement over `VE.Norms` data only (proofs may need the new cases) | 199 | 1,563 |
| neither | 27 | 496 |

The script is reproduced in section 8.

**Re-proof lines: an ESTIMATE from B2.** Re-proving Basic changed 225 lines, its definitions included. Its 21
formula-statement theorems span 297 lines, so the rate is 0.76 changed lines per line of such theorems.

| Part | Lines (ESTIMATE) |
|---|---|
| the other 137 formula-statement theorems (1,846 lines × 0.76) | about 1,400 |
| the 199 data-only theorems | 0 to about 1,190 |
| the executable definitions that match on formulas (B3's three, `Family.lean`, `Wire.lean`, `Checks.lean`) | 200 to 600 |
| **total** | **about 1,600 to 3,200** |

The definitions row is not measured. Python's `ve/norms.py` and Rust's parity code are not counted. B2 is the module
with the most inductions over formulas, so the rate may be high for the rest.

**Faithfulness statement**: not proved. Route (b)'s statement is "every existing theorem of `VE.Norms` re-proved over
`VE.Core.embedClosure`", and 1 of 25 modules was done.

**Timing**: not measured. Today's norms check refuses an arity-3 regulated predicate (`VE.Norms.check`:
`UnsupportedArity`), and so does `ve document check`. A probe with a ternary `distinguish_permitted` is refused by Lean's
decoder: `invalid signature: distinguish_permitted`. Route (b) on scratch does not reach a decoder.

## 5. Bar row 2: timing (MEASURED)

`uv run python docs/act-phrases/ap-6/measure.py --runs 21 --out docs/act-phrases/ap-6/timing.json`:

- Each run is one `ve document check` (Lean admission, norm layers regenerated and validated, the premise set's model).
- Cost is CPU seconds of the check and its children (`ChildCPU`, tests/subprocesses.py, as tools/bench measures).
- 21 runs each, interleaved, after one warm-up. Every run is admitted with a model.
- Machine: `multi-agent-lab`, AMD EPYC 7B12, 32 CPUs, Linux 7.0.0-1014-gcp, Python 3.14.7, at commit 8eda0371fd.
- Load average: 99.40 / 97.32 / 62.85 before, 104.00 / 97.58 / 70.35 after (a shared, heavily loaded VM).
- `--verify timing.json` recomputes the verdict from the saved raw rows.

| Fixture | binary (s CPU, median) | reified (s) | ratio | reified-otp (s) | ratio |
|---|---|---|---|---|---|
| u019 | 0.6705 | 0.7034 | 1.049 | 0.8666 | 1.293 |
| u057 | 0.7746 | 0.8459 | 1.092 | 0.9958 | 1.286 |
| μ | 0.6796 | 0.7932 | 1.167 | 0.8795 | 1.294 |

The raw runs are in `timing.json` (`rows`). An earlier 9-run measurement gave 1.05/1.14/1.17 and 1.31/1.28/1.29
(same machine, load 93–126).

Caveats:

- The one-rule floor document (`tests/data/rd9-docroute.ve.md`) costs a median of about 0.7 s CPU in this run
  (`floor` in `timing.json`). That is about the binary fixtures' own cost, so the ratios measure mostly the CLI's fixed
  cost plus the premise-model search.
- The reified documents are reified by hand, by `make.py`, along `reifyFormula`'s shape. `reify` itself is a linear
  pass and is not timed.
- The existence premise (an event for every filler pair) makes models hold one event per tuple. Its cost grows with
  the product of the slot domains, which three one-constant fixtures understate.

**Reading of row 2 taken: the conservative one.** `reify_faithful` makes the reified rules faithful only on structures
where `OneEventPerTuple` holds. A checker that reasons over every model of the reified premises without it stays sound
for the n-ary reading, but it can miss n-ary consequences (UNKNOWN where the n-ary reading decides). So route (a), as a
faithful route, is checked with its hypothesis as premises (`reified-otp`): 1.29 for each fixture, above 1.25. The
other reading (the hypothesis left as a stated assumption, outside the premises) gives 1.05 to 1.17, within the bar.
The plan does not say which one it meant (Notes for the DRI).

## 6. Verdict per bar row

| Bar row (plan line 1056, verbatim) | Route (a) | Route (b) |
|---|---|---|
| proves its faithfulness statement (section 3) with no new axiom | **PASS** (MEASURED: proved; audit PASS; `[propext, Classical.choice, Quot.sound]`) | **FAIL** (not proved: 1 of 25 modules re-proved in the timebox) |
| checks the three fixtures within 1.25× the binary route's time on the same machine | **FAIL** under the reading taken (MEASURED 1.293, 1.286, 1.294 with `OneEventPerTuple` as premises); within the bar without them (MEASURED 1.049, 1.092, 1.167) | **not measured** (the checker refuses arity 3 today; route (b) did not reach the decoders) |
| changes no existing theorem statement (a) / re-proves all of `VE.Norms` over the embedding within 4,000 lines (b) | **PASS** (MEASURED: 0 statement lines removed or changed, 27 added) | **not met** (ESTIMATE 1,600 to 3,200 lines; not done) |

**D6: "not yet".** Neither route meets every row. u019 and u057 stay co-blocked (389 B). This is the expected, honest
outcome the plan names, not a failure of the item. Under the other reading of row 2, route (a) meets all three rows.
Its build would then be ap-6b, touching:

- `lean/VE/Acts/Nary.lean` (from `route-a.patch`);
- the `events@0` block's role declarations (`lean/VE/Events/Decl.lean`, `Wire.lean`);
- the decoder for n-ary acts under `acts@0`;
- the relay schema.

This report does not file it: the bar as read here does not elect it.

## 7. Seeded bugs (each restored; `git status` clean after each)

| # | Language, file | Bug | Fails |
|---|---|---|---|
| S1 | Lean, `lean/VE/Acts/Nary.lean` (route a) | `exRoles` reads the role at `var d`, not the event's `var (d + 1)` | `lake build VE.Acts.NaryExamples`: `exRoles_denote` (Nary.lean:189, :197) |
| S2 | Lean, `lean/VE/Acts/Nary.lean` | `reifyNode` leaves the carve-outs unreified | `reifyNode_of_some` (Nary.lean:362, unsolved goals) |
| S3 | Lean, `lean/VE/Acts/Nary.lean` | `OneEventPerTuple`'s "at most one event per tuple" replaced by `True` | `reify_faithful`, both directions (Nary.lean:452, :479) |
| S6 | Lean, `lean/VE/Norms/Basic.lean` (route b) | `vars` in ascending order | `lake build VE.Norms.Basic`: `vars_mapM` (Basic.lean:124), used by `atom_denote` |
| S4 | Python, `docs/act-phrases/ap-6/measure.py` | ratio inverted (binary over reified) | `measure.py --verify timing.json`: exit 1, "verdict differs from the saved one" |
| S5 | Python, `measure.py` | a fixture within the bar if any route (a) variant is | `--verify`: exit 1 |
| S7 | Python, `measure.py` | the `reified-otp` variant dropped from the verdict | `--verify`: exit 1 |

An earlier S3 (the uniqueness clause deleted) failed only on a pattern's shape, so S3 keeps the shape and drops the
content. No product code changes on the feature branch (`ve/`, `tools/`, `conformance/`, `rust/`, `lean/` untouched),
so no product mutant applies.

## 8. Reproduction of the counts

```sh
git show feature/ap-6:lean/statements.txt > st.txt; git show feature/ap-6:lean/declarations.txt > de.txt
python3 - st.txt de.txt <<'EOF'
import re, sys
st, de = open(sys.argv[1]).read(), open(sys.argv[2]).read()
rng = {m[2]: int(m[1]) - int(m[0]) + 1 for m in re.findall(r'^(\d+):\d+-(\d+):\d+ theorem (\S+)@(VE\.Norms\.\w+)$', de, re.M)}
uses = {m[0]: m[1].split() for m in re.findall(r'^theorem (\S+)\n.*?\n  -- uses (.*?)\n  -- expr', st, re.M | re.S)}
f = lambda n: any(re.match(r'VE\.(Formula|Term|Valuation)\b', u) for u in uses.get(n, []))
d = lambda n: any(u.startswith('VE.Norms.') for u in uses.get(n, []))
for k, sel in (('all', lambda n: True), ('formula', f), ('data', lambda n: not f(n) and d(n))):
    ns = [n for n in rng if sel(n)]; print(k, len(ns), sum(rng[n] for n in ns))
EOF
```

It prints `all 384 4202`, `formula 158 2143` and `data 199 1563`, as run on this branch.

## 9. Trust, DELTA, size

- `uv run python tools/trust_map.py --check` on this branch: `against 8eda0371fd7f: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`. No trusted file changes; no R16 row.
- DELTA: none. No verdict, route, wording or trusted file changes.
- SIZE: 0 product, 0 tests, 608 other hand-written lines (this report 321, `measure.py` 120, `fixtures/make.py`
  167 lines). Generated or evidence files, not hand-written: the nine fixture documents (from `make.py`), `timing.json`
  (from `measure.py`) and the two patches (scratch code).
- Pilot bytes expected to move: 0 (D6 "not yet"; an estimate, nothing claimed before a pilot audit).
- Overlap: no branch in flight (`lean-first/*`, `feature/*`, `infra/*`, `foundation/*`) touches `docs/act-phrases/ap-6/`.

Spec re-read:

- `reify_faithful`'s statement against `docs/spec/act-phrases-PLAN.md:701-702` (names, binder order, `.{u}`, `hc`).
- Route (b)'s lift against `:703-704`.
- The bar against `:1056-1062`.
- Step 0's rewording against `:1064-1072` and spec F14.

## Notes for the DRI

- **Bar row 2 is ambiguous for route (a)**, and D6 turns on it. Route (a)'s faithfulness is relative to
  `OneEventPerTuple`. With the hypothesis as premises the measured ratio is 1.29 (bar 1.25); as a stated assumption
  outside the premises it is 1.05 to 1.17. The conservative reading was taken (D6 "not yet").
- If the DRI reads the row the other way, route (a) meets every row on this report's evidence and ap-6b is its build
  (section 6).
- The margin is small. The fixtures' cost is dominated by a fixed ~0.7 s CLI floor, on a loaded machine.
- `ve-document@1` has no `events` block today (section 2). Route (a)'s documents would need one, or an equivalent, to
  name their event sorts as `events@0`'s.
- The statement gate: spec section 9 marks AP-6's statements "not for build review". The item went ahead because the
  task assigns it and the statements are the experiment's own.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer, route or schema changes).
2. Every deliverable built: PASS. Step 0 is section 1. Both routes are built on scratch branches, with `route-a.patch`
   and `route-b.patch` (`git apply --check` passes on `feature/ap-6`). The fixtures are in `fixtures/`, the script is
   `measure.py`, and this report gives the verdict per row. Route (b)'s stop is the task's own cut ("where you stop,
   an ESTIMATE").
3. Tests and gates can fail: PASS (seeded bugs S1 to S7, section 7, each with its failing build or `--verify` run).
4. Python, Lean and Rust agree: N.A. (no product code changes).
5. R8 binding: N.A. (no relay).
6. Gate evidence matches the final HEAD: PASS. The chain gates the final HEAD. `timing.json` is checked by
   `measure.py --verify`, which reruns nothing.
7. No unsigned item: PASS (no DELTA row; none reserved).
8. Every user-visible change in DELTA: N.A. (none).
9. Test selection: N.A. (no test or product file changes; only `docs/act-phrases/ap-6/`).
10. Lean statements say what is claimed: PASS. `reify_faithful` matches plan:701-702 (spec re-read, section 9). The
    definitions it names are listed in section 3, including `ActsDoc`'s `valid` field.
11. Budgets fail closed: N.A. (no evaluator or limit added).
12. No CPU or memory regression: N.A. (no product change). The timings are evidence, measured outside the suite.
13. Test-removed trailers: N.A. (no test removed).
14. Both directions, cited evidence, spec re-read: PASS. Row 2 is reported both ways (with and without the hypothesis).
    Each number names its command (sections 1, 3, 4, 5, 8). The spec re-read is in section 9.
15. Four classes:
    - No overclaim: PASS. The universal words were checked against probes: "no `sorry`" (`lake build`), "0 removed"
      (statements diff), "every run admitted with a model" (`measure.py` raises otherwise).
    - No silent cut: PASS. Route (b)'s stop is named, with how far it got.
    - Every new check can fail: PASS (`--verify`: S4, S5, S7; `NaryExamples` guards: S1 breaks their module).
    - Limits charged before work: N.A.
