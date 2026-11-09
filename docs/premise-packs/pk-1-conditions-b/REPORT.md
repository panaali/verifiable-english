# pk-1-conditions-b: the empty-conditions fixtures (REPORT)

Summary: READY FOR REVIEW; tested HEAD 93721ae78 (selected tests passed; later commits docs only). Fixtures:
`eventsPack_conditions`, `choiceLayeredG_conditions`/`choiceLayered_conditions` (both readings branches, over `.ok`),
events@0 owned-case guards (adv1416 item 4). Seeded bugs M1-M7 each fail a named theorem or `#guard`. Trust +0.
Pilot bytes 0. Open: row 6b (HUMAN, owner DRI). Next: sa-pack-conditions (G1b). No DRI signature reserved; no DELTA.

## Commits

`git log --oneline main..HEAD --no-merges`, base `c2ff64751` (`git merge-base HEAD main`, after merging main at
c2ff64751; the first commits were made on base 5fc9d8c7f):

- 3ae4a780c: `eventsPack_conditions`, the readings-route fixture and the events@0 owned-case guards.
- e74c8065b, 26cc26def: the doc and comment corrections of (5).
- 6ebd14c49: the owned-case guard split, so the `layeredOf` refusal is its own guard.
- b132f912b, 22cdfa918: the seeded-bug evidence and the REPORT draft.
- a95fa911e: the self-review fixes (the legacy-hypothesis wording, a member-wise proof, the owned guards on one `Env`).
- f5a5dba65: the seeded bugs rerun on the synced HEAD with exact edits.
- 9d1a62e29: `regen_generated.py --write`.
- cd494c88f: the five owned-case helpers classed `T` (trust +0).
- Later commits: this REPORT and mutants.json M5-M7 (docs and evidence only).

## Deliverables

| # | Row (task) | Tag | Delivered by |
|---|---|---|---|
| 1 | `eventsPack_conditions : ∀ d, (eventsPack d).conditions = []` beside the events wire fixtures | AGENT | 3ae4a780c, a95fa911e. lean/VE/Events/WireExamples.lean:295 (`fun _ => rfl`), with a `#guard` on the decoded block (:296). No new module was needed: WireExamples already imports `VE.Events.Wire`, so there is no cycle |
| 2 | A readings-route fixture over the function's result, both branches | AGENT | 3ae4a780c, a95fa911e. lean/VE/Readings/UnspecifiedExamples.lean:192 `choiceLayeredG_conditions`: from `choiceLayeredG b N c wfc hN = .ok L`, every pack of `L.1.packs` has empty `conditions`. The norms@0 branch's list is `[]` (`simp`). The soft-norms@0 branch is closed by `simp [softPack_conditions]` over the list's members, not its length (M2-control). :217 `choiceLayered_conditions` gives the same over `choiceLayered`, which `replayChoiceAt` (readings-choice, UnspecifiedWire.lean:555) and Ask (Ask/Wire.lean:117, Ask/Render.lean:150, :169) read; the verdict routes read `choiceLayeredG` itself. The statement is universal, so the `#guard` fallback was not needed. UnspecifiedExamples now imports `VE.NormDefaults.PacksExamples`. There is no cycle: only SoftSeparateExamples, VerdictsExamples and VE.lean import UnspecifiedExamples, and the full `lake build` passes |
| 3 | Seeded bugs (a) and (b) | AGENT | M1 and M2 below (docs/premise-packs/pk-1-conditions-b/mutants.json) |
| 4 | statements.txt, axioms.txt, declarations.txt only through regen; standard axioms only | AGENT | 9d1a62e29. `regen_generated.py --write` wrote 37 entries. axioms.txt gained 3 rows: `eventsPack_conditions` [propext]; `choiceLayeredG_conditions` and `choiceLayered_conditions` [propext, Classical.choice, Quot.sound]. Audit.lean gained the same 3 `#print axioms` lines. The codemap files it rewrote were stale on main |
| 5a | PacksExamples.lean module doc names its real imports | AGENT | e74c8065b, 26cc26def. lean/VE/NormDefaults/PacksExamples.lean :5-7 before ("on `Packs.lean` alone") → :5-9 after. It names `Packs.lean`, `VE.Rights.Examples` and `VE.Defaults.Examples`, and says the fixtures are not on `Packs.lean` alone. Comment only |
| 5b | pk-1-conditions REPORT: checkers.lock wording, summary, tags (review F2, F4) | AGENT | e74c8065b. docs/premise-packs/pk-1-conditions/REPORT.md :61 before ("`rust_build.py`, which pinned it in lean/checkers.lock") → :66-68 after: the one hash that item added (4bb19d2fd, :252) is a `ve_service` pin, and the `rust_jsonl` list is unchanged (checked with `git show 4bb19d2fd -- lean/checkers.lock`: `rust_jsonl` is lines 2-33, `ve_service` starts at :34). That was the only such claim in the file (`grep -n 'pinned\|checkers.lock'`). Summary added at :3-6. A Tag column was added to the deliverables table at :23-29 (rows 1-5, AGENT) |
| 5c | spec line on the pk-1 stub | AGENT | e74c8065b. docs/spec/premise-packs.md :8-9 before ("imports `main` unchanged and type-checks from `lean/`") → :8-10 after: it imports the tree before pk-1 (`49a926ee7`) and type-checks from that tree's `lean/`, as the stub's header (:6-9) says |
| 6a | REQUIRED TEST (DRI 2026-11-08, adv1416 item 4): a soft document with events@0 owned gets a case or a refusal, never a silent empty result | AGENT | 3ae4a780c, 6ebd14c49, a95fa911e. lean/VE/Events/RouteExamples.lean:390-426 (below) |
| 6b | Whether the owned case must refuse *by name* at `layeredOf` (today: `object expected`) | HUMAN (owner: DRI; deferred) | Finding sent: inbox/dri/20261109T023212Z-pk-1-conditions-b-1139238.md and 20261109T032614Z-pk-1-conditions-b-1241158.md. Fixing it needs a definition change, which this item may not make |

### Part (1) after et-4b

et-4b's `decodeLayered_conditions` (PacksExamples.lean) unfolds `VE.Events.eventsPack` through `Wire.hookPacks`, so
it covers the events pack on the layered route. It does not state the fact for every `d`, so there was no named
theorem to reuse. Part (1) is therefore one line, `fun _ => rfl`, in WireExamples.lean (the task's first choice).

### The REQUIRED TEST (RouteExamples.lean:390-426)

events@0 is not in `ownedProfiles` on this branch. The owned case is therefore built explicitly, the way et-4b's
`requestCase` builds it. `ownedEnv` (:399) decodes the `Env` over `[norm-defaults@0, norms@0, relational-fol@0,
soft-norms@0]` and then lists events@0, first or last (`ownedLists`, :413). `layeredCase` (:404) passes that `Env`
to `DocumentChain.layeredOf`, the call `check`'s soft branch makes (Document.lean:2410). `ownedRequestIsNull` (:407)
runs `requestOf` on the same `Env`.

- :416 today: `environmentOf` refuses the list by name, `CheckerUnavailable: document checks under events@0 need its
  Lean profile route`. The silent path is not reachable today.
- :420 owned: `layeredOf` refuses both lists (`.toOption.isNone`). It is never `.ok`, so it is never a silent empty
  result.
- :421 owned: `requestOf` on that `Env` is `null` (the path the ruling names).
- :423 the refusal text is the decoder's on `null`, `object expected`.
- :425-426 control: without events@0 the same `Env` gives a case whose one pack is `soft`, and `requestOf` is not
  `null`. So :420 does not pass because of an earlier refusal.

**Finding (sent to the DRI; row 6b).** When every gate before `layeredOf` is bypassed (the fixture), the refusal
does not name events@0 (`object expected`). It is a refusal, not a silent empty result, so the item did not stop.
With events@0 really added to `ownedProfiles` (mutant M6, a probe on `environmentOf`), the document is still refused
by name before `requestOf`: `UnsupportedProfile: Unsupported profile events@0`. :423 pins today's `layeredOf` text,
so a fix has to update that guard.

## Seeded bugs (docs/premise-packs/pk-1-conditions-b/mutants.json)

Only Lean changed: fixtures and comments, plus the trust side table (tools/trust-classes.json, data). No Python or
Rust product code changed. Each mutant was planted from the exact strings recorded in mutants.json, built with
`lake build <target>` and restored with `git checkout`. M1-M4 ran on f5a5dba65's code and M5-M7 on cd494c88f's (the
Lean is the same).

- **M1** (lean/VE/Events/Wire.lean, `eventsPack` exports `[(.excepted "x", .top)]`, task 3a): fails
  `eventsPack_conditions` (WireExamples.lean:295, `Type mismatch`) and the `#guard` at :296.
- **M2** (lean/VE/Readings/UnspecifiedWire.lean:524, the soft branch's list gains a second pack with one condition,
  task 3b): fails `choiceLayeredG_conditions` (UnspecifiedExamples.lean:207, the soft branch, `unsolved goals`).
  UnspecifiedWire.lean's own `X_single` and well-formedness proofs for that branch were `sorry` for this run only.
- **M2-control** (the same, but the appended pack states no condition): the fixture builds (exit 0). The proof reads
  the members, not the list's length.
- **M2b** (the one `softPack` gains a condition): fails `choiceLayeredG_conditions` (:207).
- **M3** (lean/VE/Service/Document.lean `requestOf`: events@0 erased from the case's profiles instead of `null`, the
  silent path): fails `#guard` RouteExamples.lean:420, and also :421, :423 and et-4b's :383-385. To reach the fixture,
  DocumentChain.lean's `requestOf_environment` and `layeredOf_soft` proofs were `sorry` for this run only; otherwise
  they fail first.
- **M4** (lean/VE/Events/RouteExamples.lean, a changed file: `ownedEnv` erases events@0): fails `#guard` :420, :421
  and :423.
- **M5** (Document.lean, `requestOf` always `null`, with the same `sorry` proofs): fails the controls `#guard` :425
  and :426, and et-4b's :387-388.
- **M6** (Document.lean:59, events@0 added to `ownedProfiles`): fails `#guard` :416.
- **M7** (UnspecifiedWire.lean `choiceLayered` appends a pack with one condition): fails `choiceLayered_conditions`
  (UnspecifiedExamples.lean:222).

## Trust

`uv run python tools/trust_map.py --check` against c2ff647518b6: `K +0, S +0, D +0, G +0, tied +0, unclassified +0,
trusted +0`, `PASS: K, S and untied [V] within c2ff647518b6 and the allowances introduced since`. The first run
showed `unclassified +19` (RouteExamples.lean: the five owned-case helpers). cd494c88f classes them `T` in
tools/trust-classes.json, as et-4b did for `requestCase` (ee7646c4d). Since there is no R16 growth, there is no
allowance, no FOLLOW-UPS row and no trust-mutants run (checklist 13a applies to trusted growth only).

## Checks (commands run)

- `lake build VE.<Module>` for each edited module while iterating; full `lake build` on the synced tree:
  `Build completed successfully (1337 jobs)`.
- `python3 tools/rust_build.py`: the binary's hash was already pinned (no checkers.lock change). Regen needed it.
- `uv run python tools/regen_generated.py --write`: `wrote 37 entries` (9d1a62e29).
- `python3 lean/audit.py`: `PASS: 798 source files; 8831 named theorem declarations audited …; only the declared
  standard axiom allowlist.`
- `uv run python tools/trust_map.py --check`: PASS, trusted +0 (above).
- Selected tests, once, on committed 93721ae78 (clean tree): `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base
  c2ff64751 --run`. It ran on the VM, because ve-mac-1 was unreachable (`Could not resolve hostname`). Result: exit 0 in
  4331 s, 117 units with 0 non-zero exits (`recorded 108 units for tree ebff9d6f98; … 0 failed`). It included its
  own `lake build` (`Build completed successfully (1337 jobs)`), so every `#guard` and theorem above was checked.
- Not run: the full gate (the chain runs it on the final HEAD), and trust_mutants (no trusted growth).

## Size, pilot bytes, next item

- Size (`git diff --numstat c2ff64751`, hand-written, outside generated files and evidence): Lean fixtures +83
  (RouteExamples 38, UnspecifiedExamples 39, WireExamples 6), comments +5 −3 (PacksExamples), docs +18 −10 (the
  pk-1-conditions REPORT and the spec line), tools/trust-classes.json +6 −1, plus this REPORT and mutants.json.
- Pilot bytes: 0 expected. No definition changes, so no answer changes.
- Next: sa-pack-conditions (G1b), before the first pack with non-empty decls.
- In-flight overlap: no branch in `lean-first/* feature/* infra/* foundation/*` touches a file this item changes
  (`git diff --name-only main...<b>` loop, no hits).
- Pre-existing red: none involved (main-known-red.txt).

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 1 A, 4 B, 4 C; fixed 9. A: the WireExamples doc overclaimed what the `*_legacy` theorems give. B: the
sync with main, M2 as the task's appended pack, row 6's open part tagged, the Commits section. C: `choiceLayered`
readers, "first or last", `requestOf` on the same `Env`, exact mutant edits.

1. N.A.: no relayed answer, schema or response field changes (`git diff --name-only c2ff64751 -- ve/backends lean/ResponseShape`: empty).
2. PASS: deliverables 1-6a in the table, each with its commit. 6b is tagged HUMAN with the DRI as owner. No product
   definition changed (`git diff --name-only c2ff64751 -- lean/VE/Events/Wire.lean lean/VE/Readings/UnspecifiedWire.lean lean/VE/Defaults`: empty).
3. PASS: M1-M7 in mutants.json each fail a named theorem or `#guard`, and M2-control shows the fixture is not shape-bound.
4. N.A.: no answer changes (fixtures only). Existing corpora: the selected tests (Checks).
5. N.A.: Python reads no new field.
6. PASS: no gate run by me. The commit list is `main..HEAD --no-merges`, and evidence lines cite the commits they ran on.
7. PASS: trust +0 (trust_map --check PASS). No signature is reserved.
8. PASS: no user-visible change, so there is no DELTA.md. No definition changed (item 2's empty diff).
9. PASS: the selection ran on this branch's changes (Checks: exit 0, 117 units).
10. PASS: each theorem breaks under its mutant: M1 `eventsPack_conditions`; M2, M2b `choiceLayeredG_conditions`; M7
    `choiceLayered_conditions`. The statements are over the functions' `.ok` results, not over one input.
11. N.A.: no budget, limit or deadline is touched.
12. N.A.: no evaluator added. The fixtures are `rfl`, `simp` and a handful of `#guard`s.
13. N.A.: no test removed or renamed.
14. PASS: both directions are covered. A condition is refused (M1, M2, M2b, M7) and a pack without one passes
    (M2-control). Owned events@0 is refused (:420), and the control is a case (:425-426, M5). Spec re-read: the
    task's (5) lines were checked against the files they cite (5a-5c rows).
15. PASS: overclaim: each universal word in this REPORT and in the new doc comments cites its test or mutant. Row
    6b is written as open, not done. No silent cut: deliverables 1-5 and the REQUIRED TEST are all built. Every new
    check can fail: the guards at :416, :420, :421, :423, :425 and :426 and all three theorems have mutants (M1-M7).
    Limits: N.A. (none touched).
