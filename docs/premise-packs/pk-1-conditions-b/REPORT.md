# pk-1-conditions-b: the empty-conditions fixtures (REPORT)

Summary: READY FOR REVIEW at HEAD (see "Commits"). The fixtures are `eventsPack_conditions` and
`choiceLayeredG_conditions` / `choiceLayered_conditions` (both readings branches, a universal statement over the `.ok`
result), plus the events@0 owned-case guards (DRI adv1416 item 4). Seeded bugs M1-M4 each fail a named theorem or
`#guard`. Trust: TRUST. Pilot bytes expected 0. Open items: the DRI finding on the owned case's unnamed refusal
(below; not blocking). Next item: sa-pack-conditions (G1b). No DRI signature is reserved, and there is no DELTA.

## Deliverables

| # | Row (task) | Tag | Delivered by |
|---|---|---|---|
| 1 | `eventsPack_conditions : ∀ d, (eventsPack d).conditions = []` beside the events wire fixtures | AGENT | lean/VE/Events/WireExamples.lean:294 (`fun _ => rfl`), with a `#guard` on the decoded block (:295). No new module: WireExamples already imports `VE.Events.Wire`, so there is no cycle |
| 2 | A readings-route fixture over the function's result, both branches | AGENT | lean/VE/Readings/UnspecifiedExamples.lean:192 `choiceLayeredG_conditions`: from `choiceLayeredG b N c wfc hN = .ok L`, every pack of `L.1.packs` has empty `conditions`. The norms@0 branch's list is `[]`; the soft-norms@0 branch's one pack is closed by `softPack_conditions`. :217 `choiceLayered_conditions` is the same over `choiceLayered`, the mapped source the readings verdict routes read. The statement is universal, so the `#guard` fallback was not needed. UnspecifiedExamples now imports `VE.NormDefaults.PacksExamples` (no cycle: only SoftSeparateExamples, VerdictsExamples and VE.lean import UnspecifiedExamples) |
| 3 | Seeded bugs (a) and (b) | AGENT | M1 and M2 below; docs/premise-packs/pk-1-conditions-b/mutants.json |
| 4 | statements.txt, axioms.txt, declarations.txt only through regen; standard axioms only | AGENT | REGEN |
| 5a | PacksExamples.lean module doc names its real imports | AGENT | lean/VE/NormDefaults/PacksExamples.lean :5-7 before ("on `Packs.lean` alone") → :5-9 after (it names `Packs.lean`, `VE.Rights.Examples` and `VE.Defaults.Examples`, and says the fixtures are not on `Packs.lean` alone). Comment only |
| 5b | pk-1-conditions REPORT: checkers.lock wording, summary, tags (review F2, F4) | AGENT | docs/premise-packs/pk-1-conditions/REPORT.md :61 before ("`rust_build.py`, which pinned it in lean/checkers.lock") → :66-68 after (the one hash the item added, 4bb19d2fd at :252, is a `ve_service` pin; `rust_jsonl` is unchanged). That was the only such claim in the file (`grep -n 'pinned\|checkers.lock'`). Summary added at :3-6. The Tag column is added to the deliverables table at :23-29 (rows 1-5 AGENT) |
| 5c | spec line on the pk-1 stub | AGENT | docs/spec/premise-packs.md :8-9 before ("imports `main` unchanged and type-checks from `lean/`") → :8-10 after (it imports the tree before pk-1, `49a926ee7`, and type-checks from that tree's `lean/`, as the stub's header :6-9 says) |
| 6 | REQUIRED TEST (DRI 2026-11-08, adv1416 item 4): a soft document with events@0 owned gets a case or a refusal, never a silent empty result | AGENT | lean/VE/Events/RouteExamples.lean:390-414 (finding below) |

### Part (1) after et-4b

et-4b's `decodeLayered_conditions` (PacksExamples.lean) unfolds `VE.Events.eventsPack` through `Wire.hookPacks`, so
it covers the events pack on the layered route. It does not state the fact for every `d`, so there was no named
theorem to reuse. Part (1) is one line, `fun _ => rfl`, in WireExamples.lean (the task's first choice).

### The REQUIRED TEST (RouteExamples.lean:390-414)

events@0 is not in `ownedProfiles` on this branch. The owned case is therefore built explicitly, the way et-4b's
`requestCase` builds it: an `Env` decoded with `[norm-defaults@0, norms@0, relational-fol@0, soft-norms@0]`, then
listing events@0 (first or last), passed to `DocumentChain.layeredOf` (`layeredCase`, :399). That is the call
`check`'s soft branch makes (Document.lean:2410).

- :405 today: `environmentOf` refuses the list by name, `CheckerUnavailable: document checks under events@0 need its
  Lean profile route`. The silent path is not reachable today.
- :409 owned: `layeredOf` refuses it (`.toOption.isNone`) for both orders. It is never `.ok`, so it is never a
  silent empty result.
- :410 owned: `requestOf` is `null` there (the path the ruling names).
- :412 the refusal text is the decoder's on `null`, `object expected`.
- :414 control: without events@0 the same `Env` gives a case whose one pack is `soft`. So :409 does not pass
  because of an earlier refusal.

**Finding (sent to the DRI, inbox/dri/20261109T023212Z-pk-1-conditions-b-1139238.md).** In the owned case the
refusal does not name events@0 (`object expected`). It is a refusal, not a silent empty result, so the item did not
stop. Changing it needs a definition change (`requestOf` or `layeredOf`), which this item may not make. The ruling's
second acceptable outcome, a refusal naming events@0, is therefore not met in the owned case. :412 pins today's
text, so a fix has to update that guard.

## Seeded bugs (docs/premise-packs/pk-1-conditions-b/mutants.json)

Only Lean changed (fixtures and comments). No Python or Rust product code changed. Each mutant was planted, built with
`lake build <target>` and restored (`git checkout <file>`).

- **M1** (lean/VE/Events/Wire.lean, `eventsPack` exports `[(.excepted "x", .top)]`, task 3a): fails
  `eventsPack_conditions` (WireExamples.lean:294, `Type mismatch`) and the `#guard` at :295.
- **M2** (lean/VE/Readings/UnspecifiedWire.lean:524, the soft branch's pack list holds a pack with one condition,
  task 3b): fails `choiceLayeredG_conditions` (UnspecifiedExamples.lean:211, `Type mismatch`). The mutant gives
  the one `softPack` a condition instead of appending a second pack. Appending one breaks UnspecifiedWire.lean's own
  `X_single` proof before the fixture is reached.
- **M3** (lean/VE/Service/Document.lean `requestOf`, events@0 silently erased from the case's profiles instead of
  `null`; adv1416 item 4): fails `#guard` RouteExamples.lean:409 (and :410, :412, and et-4b's :383-385). To reach
  the fixture module, DocumentChain.lean's `requestOf_environment` and `layeredOf_soft` proofs were `sorry` for that
  run only. Without that, they fail first (DocumentChain.lean:25, :39, :54).
- **M4** (lean/VE/Events/RouteExamples.lean, a changed file: `layeredCase` erases events@0 before `layeredOf`): fails
  `#guard` :409 and :412.

## Trust

TRUSTDETAIL

## Checks (commands run)

CHECKS

## Size, pilot bytes, next item

- Size: SIZE
- Pilot bytes: 0 expected. No definition changes, so no answer changes.
- Next: sa-pack-conditions (G1b), before the first pack with non-empty decls.
- In-flight overlap: no branch in `lean-first/* feature/* infra/* foundation/*` touches a file this item changes
  (`git diff --name-only main...<b>` loop, no hits).

## Self-review against BUILDER-CHECKLIST

SELFREVIEW
