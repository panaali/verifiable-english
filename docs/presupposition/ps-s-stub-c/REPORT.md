# ps-s-stub-c: the stub's bodies in section 4, the soft chain in 4.7 and the plan

Spec 4.7 now holds the ten bodies PS-2a builds, with the eight helper bodies they call, copied verbatim from the
PS-S stub. All 18 are byte-identical to the stub and elaborate in the stub (115/115 `#guard`s) and against main's
`VE.Presupposition`. 4.7 says where step 5 learns the chain; 7.3 relabels A26/A27; section 5 lists step 5's
diagnostic; the plan gives the soft-chain refusal as step 5's own (DRI 2026-11-04, items 2-3). The item has no
product code, changes no statement, adds trust +0 and 0 bytes, and needs no DELTA.

Sources: DRI 2026-11-04 `reviews/dri-decisions-20261104-ps-s-stub.md` items 1-3;
`reviews/ps-s-stub/recheck-2.final.md` :27-30 (its four C findings); the PS-S stub
`reviews/ps-s-stub/SpecStubs_presupposition.lean` (manage-agents; 1,239 lines, `sha256sum` gives
`7e680563…7dc89`). It is the only copy on this host: `design/ps-s-stub` and `design/syn2-presupposition` are not
in this clone (`git rev-parse` fails for both). Base: main `ee1fb3efa`.

## Edits (file:line before → after)

| # | Before (main `ee1fb3efa`) | After (this branch) | What |
|---|---|---|---|
| 1 | `docs/spec/presupposition.md:935-938` ("…are in the stub, as written in sections 1.4 to 1.8") | `:935-941` (sentence), `:943-1024` (`lean` block), `:1026-1027` ("Draft 2 drops…", rewrapped) | Deliverable 1: the bodies of `tableOk`, `premisesBefore`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`, `unitModes`, `claimReading`, `ruleReading`, `ruleConditions`. With them come the helpers `env` and `unitOf`, and the bodies of the six signatures they or the statements call (`Carrier.root`, `Carrier.cand`, `Candidate.root`, `Candidate.core`, `Args.tuple`, `rowNames`), all with the stub's doc comments, verbatim. `claimReading` and `ruleReading` set `aliases := []` |
| 2 | `docs/spec/presupposition.md:1015` (step 5, last line) | `:1104-1108` | Deliverable 2: step 5 reads `chain` from the readings environment where it calls the separation, as `abstention` reads `re.chain` (`lean/VE/Readings/Wire.lean:567-568`). That environment is a fixed parameter of `admit`, like `fillDoc N` and σ; `PDoc` and the statements are unchanged |
| 3 | `docs/spec/presupposition.md:1324-1325` | `:1418-1419` | Deliverable 3: "A26 (soft chain), A27 (rights chain)"; "their task files must name them" |
| 4 | `docs/spec/presupposition-PLAN.md:300-301` | `:300-303` | Deliverable 4: on the soft chain PS check step 5 refuses with "UnsupportedProfile: a conditioned rule reading needs the norms chain (presupposition)"; on the rights chain `abstention` refuses |
| 5 | `docs/spec/presupposition-PLAN.md:1031` | `:1033` | Deliverable 4: the same split in the dependency row's last cell |
| 6 | `docs/spec/presupposition-PLAN.md:1077` | `:1079` | Beyond the named lines: the one-owner row said `abstention` owns "readings content beside `norm-defaults@0` off the norms chain", which item 2 makes false for the soft chain. It now says "on the rights chain" and names PS check step 5 for the soft chain |
| 7 | `docs/spec/presupposition-PLAN.md:871-872` | `:873-874` | Beyond the named lines: "A26 and A27 on the soft and rights chains" becomes "A26 on the soft chain, A27 on the rights chain" (the ambiguity recheck-2 found at spec :1324) |
| 8 | `docs/spec/presupposition.md` (after :1223, section 5) | `:1317` | Beyond the named lines: section 5's diagnostics table gets the row for step 5's own diagnostic, worded as in 4.7 and A26 |

`git diff --numstat main` gives `docs/spec/presupposition.md` +100 −6, `docs/spec/presupposition-PLAN.md` +8 −6,
and this report. No plan row was added, removed or re-scoped: edits 4-7 change wording only. No existing `lean`
block of section 4 changed; the copied bodies are a new block. No statement changed, so no statement gate applies
(DRI item 3).

**The syn2-presupposition edits** (ac20eac09 + 6de46196b; read from
`debates/syn2-apply-dri-syn2-0905{,-r2}/material/presupposition-*.diff`) touch only `presupposition-PLAN.md` and
nothing in section 4 of the spec. Their hunk at plan :1030 keeps :1031 as context and changes the profile-gate row
two lines below. The self-reviewer ran a 3-way `git merge-file` of this branch's plan against the round-2 diff, and
it merges with no conflict.

**The false-side guards are already on main** (ps-1b), so none were added. In
`lean/VE/Presupposition/Examples.lean` (the task cited :235-239; on `ee1fb3efa` they are at :237-245):
- `carried_conditioned_off`: true side at :239 (`kOwnerOnly`), false side at :240 (`kNeither`: the manager's goal
  is off, unit F = owner's goal F).
- `carried_on_goals`: true side at :244 (`kOwner`), false side at :245 (`kBothFalse`: both goals hold,
  unit F = `B` F).

`lake build VE.Presupposition.Examples` reports `Build completed successfully (112 jobs)`.

## Check 5: each copied body equals the stub's

Scratch files are in `/tmp/psc` and are never committed, like the stub. The commands, from the worktree root:

```
cp <manage-agents>/reviews/ps-s-stub/SpecStubs_presupposition.lean /tmp/psc/stub.lean
sed '21,36d' /tmp/psc/stub.lean > /tmp/psc/base0.lean
python3 -I /tmp/psc/tools/check.py docs/spec/presupposition.md /tmp/psc/base0.lean /tmp/psc/spliced.lean
cd lean && PATH=~/.elan/bin:$PATH lake env lean /tmp/psc/spliced.lean      # likewise base0, main-scratch, seed
```

1. **Baseline.** Running `lake env lean` on the unmodified stub gives 5 errors, all `has already been declared`, for
   `uniqueAt`, `assertiveAt`, `raise1`, `uniqueOpen` and `assertiveOpen`. PS-1 has since put these 4.1 builders
   into `lean/VE/Discourse/Descriptions.lean` on main. `base0.lean` is the stub without those copies (lines
   21-36). Its two `rfl` wrapper examples then run against main's builders. It gives rc 0, 0 errors and 115/115
   `#guard`s (`grep -c '^#guard'` gives 115).
2. **Byte comparison.** `check.py` extracts each of the 18 defs from the spec's `lean` blocks and from the stub,
   each with its directly preceding doc comment and only the definition that has a body. It prints `identical` for
   all 18 and ends `ALL IDENTICAL`. Line counts: `Carrier.root` 4, `Carrier.cand` 7, `Candidate.root` 4,
   `Candidate.core` 3, `Args.tuple` 2, `rowNames` 1, `tableOk` 3, `env` 1, `unitOf` 1, `unitContent` 4,
   `unitAsserted` 1, `unitReadings` 4, `nodeCertificate` 2, `premisesBefore` 6, `unitModes` 2, `claimReading` 9,
   `ruleReading` 7, `ruleConditions` 3.
3. **Spliced elaboration.** `check.py` writes `spliced.lean`, which is the stub with each def replaced by the spec's
   text. `diff` shows it is identical to `base0.lean`. `lake env lean` on it gives rc 0, 0 errors and 115/115
   `#guard`s.
4. **Against main's definitions.** `main-scratch.lean` imports main's `VE.Presupposition.{Frame,Reading,Rules}`
   (ps-1, ps-1b) for `Frame`, `Frame.close`, `PositionClass`, `Reading`, `Root`, `carried` and `conditionNode`. It
   takes the 4.7 types from the stub with their bodies removed, since none of those types is on main yet. The 18
   bodies come from the spec's new block, verbatim. It elaborates with rc 0 and 0 errors. This file has no
   `#guard`, so it shows only that the bodies type-check against main's definitions. Separately, a text comparison
   shows main's `Root` (`Reading.lean:65`), `carried` (`Reading.lean:71`), `Frame.close` (`Frame.lean:50`) and
   `conditionNode` (`Rules.lean:20`) are byte-identical to the stub's (stub :239, :245, :95, :345). No body had to
   stop.

### Seeded check (each spec alteration made on HEAD `bae566e00`, then the spec restored with `git checkout`)

The guard lines below are stub lines (the scratch line + 16).

| Seed | Alteration in `docs/spec/presupposition.md` | `check.py` | Stub `#guard` that fails |
|---|---|---|---|
| S1b | `premisesBefore`: drop `D.background ++` | `premisesBefore DIFFERS` | :1036 `premisesBefore docS17 "u2" == [.top, .unary "earlier" (.const "c")]` |
| S2 | `tableOk`: drop `.negated` from the position list | `tableOk DIFFERS` | :1023 `!tableOk rowNames (fun _ pc => if pc == .negated then [.inPlace] else [])` |
| S3 | `claimReading`: `.assumed => none` for `.assumed => some c.goal` | `claimReading DIFFERS` | :1161 `(claimReading rep26 outer26 b26 .assumed).premise == some q26 && !ev m26 q26` |
| S4b | `Candidate.root`: `.asserted => .bare` | `Candidate.root DIFFERS` | :1160 `!ev m26 (contentOf (claimReading rep26 outer26 b26 .asserted))` |
| S1 | `premisesBefore`: `.claim a => some a` (drop the `x.asserted` test) | `premisesBefore DIFFERS` | none: survives (rc 0) |
| S4 | `Candidate.root`: `.conditioned => .bare` | `Candidate.root DIFFERS` | none: survives (rc 0) |

The byte comparison catches all six seeds. Two of them survive the stub's guards:
- S1 survives because no fixture has an earlier claim unit that is not asserted. Every unit of S17 (`docS17`) is
  asserted, and A7 is about a certificate citing its own or a later unit, so neither the spec nor the stub tests
  this filter.
- S4 survives because no guard reads a reading's content with conditioned as its root.

This item has no Lean files, so it adds no guard. The follow-up below asks PS-2a for both fixtures.

## Not delivered, deviations, pre-existing

- All five deliverables are delivered. Edits 6, 7 and 8 go beyond the lines the task names. They are wording only,
  in the files the task names: 6 fixes the same false claim, 7 the same ambiguity, and 8 lists the diagnostic that
  item 2 adds. Each can be reverted as its own hunk.
- Line drift: the task cites spec :931-934 and :1015-1022. On main `ee1fb3efa` the sentence is at :935-938, step
  5's chain sentence at :1015 and the soft-chain paragraph at :1017-1023. It also cites `Examples.lean` :235-239
  (now :237-245).
- No Lean, Python or Rust file changed (`git diff --name-only main` lists only the three docs). So
  `lean/VE/Presupposition/` stays ps-1c's. Regen, `lean/audit.py`, trust_mutants and a mutants JSON do not apply.
  `uv run python tools/regen_generated.py --owner docs/spec/presupposition.md` prints `-`, meaning the spec is not
  an input of any generated file. Seeded bugs per changed language: none apply. The seeded check above is the one
  the task asks for.
- Trust: `uv run python tools/trust_map.py --check` prints `trusted +0` and `PASS`.
- Pilot bytes: 0 (spec text only).

## Spec re-read

- spec re-read: the step 5 chain sentence against recheck-2.final.md :27 and `lean/VE/Readings/Wire.lean:567-568`
  (`re.chain == .rights`).
- spec re-read: the plan's soft-chain refusal and its diagnostic text against `dri-decisions-20261104-ps-s-stub.md`
  item 2 and spec :1110-1115 / A26 :1451.
- spec re-read: "A26 (soft chain), A27 (rights chain)" against the 7.3 table rows A26 (:1451, soft chain) and A27
  (:1452, rights chain).
- spec re-read: the 18 bodies against the stub, by `check.py` (byte comparison).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. (no relayed answer; docs only).
2. Every deliverable built: PASS. Deliverables 1-5 are in the edits table; check 5 output is above.
3. Tests and gates can fail: PASS. Seeds S1b, S2, S3 and S4b each fail a named stub `#guard` (seeded table).
4. Python, Lean and Rust agree: N.A. (no code).
5. R8 binding: N.A. (no relay).
6. Gate evidence matches HEAD: PASS. The final selected run is on the committed HEAD (MAC_PYTEST_NO_DEFER run,
   after this report).
7. No unsigned item: PASS. No DELTA and no signature is reserved.
8. Every user-visible change in DELTA: N.A. (spec text only; DELTA: none, as the task says).
9. Test selection: N.A. (no code; `select_tests` runs on the docs diff).
10. Lean statements say what is claimed: PASS. No statement changed; the copied bodies are byte-identical to the
    stub (`check.py`: ALL IDENTICAL).
11. Budgets fail closed: N.A. (no evaluator).
12. No CPU or memory regression: N.A. (no code).
13. `Test-removed` trailers: N.A. (no test removed).
14. Both directions, cited evidence, spec re-read: PASS. Every claim cites a command; spec re-read lines are above;
    the seeds show both the passing and the failing side.
15. Overclaim: PASS ("no statement changed": the `lean` blocks of the base are unchanged in `git diff`; "all 18
    identical": `check.py`). Silent cut: PASS (none cut). Every new check can fail: PASS (S1b, S2, S3, S4b).
    Limits: N.A. (no evaluator).

SELF-REVIEW: 0 A, 2 B, 9 C; fixed 11 (B1, B2; C3-C11). For C9 the row was added to section 5 rather than filed as a
follow-up.

## Next item

ps-2aa (`prompts/task-ps-2aa.txt`, which reads this spec text on main), then the rest of PS-2a. Their task files
must name A5u-allow, A5u-deny, A19-A21 and A24-A28 as condition tests (DRI item 1): A26 on the soft chain with PS
check step 5's diagnostic, A27 on the rights chain with `abstention`'s.

FOLLOW-UP: ps-2a-premfix S17 variant with an unasserted earlier unit (premisesBefore omits it) and a conditioned-root claimReading content guard, for PS-2a
