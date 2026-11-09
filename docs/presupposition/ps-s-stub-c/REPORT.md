# ps-s-stub-c: the stub's ten bodies in section 4, the soft chain in 4.7 and the plan

Spec section 4.7 now has the ten bodies PS-2a builds (plus the helpers `env` and `unitOf`), copied verbatim from
the PS-S stub. A scratch check shows all twelve are byte-identical to the stub, and they elaborate both in the stub
(115/115 `#guard`s) and against main's built `VE.Presupposition` modules. 4.7 now says where check step 5 learns the
chain. 7.3 and the plan now give the soft-chain refusal as PS check step 5's own (DRI 2026-11-04, items 2-3). The
item has no Lean, Python or Rust change, no statement change, trust +0, no DELTA and 0 bytes.

Sources: DRI 2026-11-04 `reviews/dri-decisions-20261104-ps-s-stub.md` items 1-3;
`reviews/ps-s-stub/recheck-2.final.md` :27-30 (its four C findings); the PS-S stub
`reviews/ps-s-stub/SpecStubs_presupposition.lean` (manage-agents; 1,239 lines, sha256 `7e680563…7dc89`; the only
copy on this host: `design/ps-s-stub` and `design/syn2-presupposition` are not in this clone). Base: main `ee1fb3efa`.

## Edits (file:line before → after)

| # | Before (main `ee1fb3efa`) | After (this branch) | What |
|---|---|---|---|
| 1 | `docs/spec/presupposition.md:935-938` ("…are in the stub, as written in sections 1.4 to 1.8") | `:935-939` (sentence), `:941-995` (`lean` block), `:997-998` ("Draft 2 drops…", unchanged text, rewrapped) | Deliverable 1: the bodies of `tableOk`, `env`, `unitOf`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`, `premisesBefore`, `unitModes`, `claimReading`, `ruleReading`, `ruleConditions`, with the stub's doc comments, verbatim. `claimReading` and `ruleReading` set `aliases := []` |
| 2 | `docs/spec/presupposition.md:1015` (step 5, last line) | `:1075-1078` | Deliverable 2: step 5 reads `chain` from the readings environment where it calls the separation, as `abstention` reads `re.chain` (`lean/VE/Readings/Wire.lean:567-568`). `PDoc` is unchanged |
| 3 | `docs/spec/presupposition.md:1324-1325` | `:1387-1388` | Deliverable 3: "A26 (soft chain), A27 (rights chain)"; "their task files must name them" |
| 4 | `docs/spec/presupposition-PLAN.md:300-301` | `:300-303` | Deliverable 4: on the soft chain PS check step 5 refuses with "UnsupportedProfile: a conditioned rule reading needs the norms chain (presupposition)"; on the rights chain `abstention` refuses |
| 5 | `docs/spec/presupposition-PLAN.md:1031` | `:1033` | Deliverable 4: the same split in the dependency row's last cell |
| 6 | `docs/spec/presupposition-PLAN.md:1077` | `:1079` | Beyond the lines the task names (see Deviations): the one-owner row said `abstention` owns "readings content beside `norm-defaults@0` off the norms chain", which item 2 makes false for the soft chain. It now says "on the rights chain" and names PS check step 5 for the soft chain |
| 7 | `docs/spec/presupposition-PLAN.md:871-872` | `:873-874` | Beyond the lines the task names: "A26 and A27 on the soft and rights chains" becomes "A26 on the soft chain, A27 on the rights chain". This is the same ambiguity recheck-2 found at spec :1324 |

Diff: `docs/spec/presupposition.md` +69 −6, `docs/spec/presupposition-PLAN.md` +8 −6, plus this report. No plan row
was added, removed or re-scoped (edits 4-7 change wording only), and no `lean` block of section 4 changed except the
new block of copied bodies. No statement changed, so no statement gate applies (DRI item 3).

**The syn2-presupposition edits** (ac20eac09 + 6de46196b; read from
`debates/syn2-apply-dri-syn2-0905{,-r2}/material/presupposition-*.diff`) touch only `presupposition-PLAN.md` and
nothing in section 4 of the spec. Their hunk at plan :1030 leaves :1031 as context and changes the profile-gate row
two lines below, so edit 5 sits one unchanged line away from it. Neither commit is on main yet.

**The false-side guards are already on main** (ps-1b), so none were added again. In
`lean/VE/Presupposition/Examples.lean`, `carried_conditioned_off` has its true side at :239 (`kOwnerOnly`) and its
false side at :240 (`kNeither`: manager's goal off, unit F = owner's goal F). `carried_on_goals` has its true side
at :244 (`kOwner`) and its false side at :245 (`kBothFalse`: both goals hold, unit F = `B` F).
`lake build VE.Presupposition.Examples` succeeds on this branch (112 jobs).

## Check 5: each copied body equals the stub's

The scratch files live in `/tmp/psc` and are never committed, like the stub itself.

1. **Baseline.** The stub, run as it is on main: `lake env lean` gives 5 errors, all `has already been declared`
   for `uniqueAt`, `assertiveAt`, `raise1`, `uniqueOpen` and `assertiveOpen`. PS-1 has since put these 4.1 builders
   into `lean/VE/Discourse/Descriptions.lean` on main. With the stub's 4.1 copies deleted (lines 21-36; the two
   `rfl` wrapper examples then run against main's builders), `base0.lean` elaborates with rc 0, 0 errors and
   115/115 `#guard`s.
2. **Byte comparison.** A scratch script extracts each of the twelve defs, with its directly preceding doc comment,
   from the `lean` blocks of the edited spec and from the stub. All twelve are `identical`: `tableOk` 3 lines,
   `env` 1, `unitOf` 1, `unitContent` 4, `unitAsserted` 1, `unitReadings` 4, `nodeCertificate` 2,
   `premisesBefore` 6, `unitModes` 2, `claimReading` 9, `ruleReading` 7, `ruleConditions` 3.
3. **Spliced elaboration.** The script replaces each stub def with the spec's text, giving `spliced.lean`. It is
   identical to `base0.lean`, and `lake env lean spliced.lean` gives rc 0, 0 errors and 115/115 `#guard`s.
4. **Against main's definitions.** `main-scratch.lean` imports main's `VE.Presupposition.{Frame,Reading,Rules}`
   (ps-1, ps-1b) for `Frame`, `Frame.close`, `PositionClass`, `Reading`, `Root`, `carried` and `conditionNode`. It
   takes the 4.7 types from the stub (`Carrier` … `Report`, `cellOk`; none of them is on main yet) and the twelve
   copied bodies straight from the spec's new block. It elaborates with rc 0 and 0 errors, so no copied body
   differs from what main built, and no body or statement had to stop.

### Seeded check (each spec alteration made, then the spec restored with `git checkout`)

| Seed | Alteration in `docs/spec/presupposition.md` | Comparison | Stub `#guard` that fails (scratch line) |
|---|---|---|---|
| S1b | `premisesBefore`: drop `D.background ++` | `premisesBefore DIFFERS` | `#guard premisesBefore docS17 "u2" == [.top, .unary "earlier" (.const "c")]` (:1020) |
| S2 | `tableOk`: drop `.negated` from the position list | `tableOk DIFFERS` | `#guard !tableOk rowNames (fun _ pc => if pc == .negated then [.inPlace] else [])` (:1007) |
| S3 | `claimReading`: `.assumed => none` for `.assumed => some c.goal` | `claimReading DIFFERS` | `#guard (claimReading rep26 outer26 b26 .assumed).premise == some q26 && !ev m26 q26` (:1145) |
| S1 | `premisesBefore`: `.claim a => some a` (drop the `x.asserted` test) | `premisesBefore DIFFERS` | none: survives the stub's guards |

S1 survives because every unit of the stub's `docS17` is asserted, so no stub `#guard` reads the `asserted` filter.
The byte comparison still catches S1. The spec's own A7 fixture and checklist item 6 (`premisesBefore` against
S17 and A7) give PS-2a the case to cover; this item adds no guard (no Lean files).

## Not delivered, deviations, pre-existing

- All five deliverables are delivered. Edits 6 and 7 go beyond the lines the task names. They are wording only, in
  the file the task names, and they fix the same false claim (6) and the same ambiguity (7). A reviewer who wants
  them out can revert those two hunks alone.
- The task cites spec :931-934 and :1015-1022. On main `ee1fb3efa` the sentence is at :935-938 and step 5's chain
  sentence is at :1015, with the soft-chain paragraph at :1017-1023.
- No Lean product file changed, so `lean/VE/Presupposition/` stays ps-1c's. Regen, `lean/audit.py`,
  trust_mutants and a mutants JSON do not apply (no product code; trust +0). Seeded bugs in a changed language:
  none apply, because the item changes no product code in any language. The seeded check above is the one the
  task asks for.
- Pilot bytes: 0 (spec text only).

## Next item

PS-2a. Its task file names A5u-allow, A5u-deny, A19-A21 and A24-A28 as condition tests (DRI item 1), A26 on the
soft chain with PS check step 5's diagnostic and A27 on the rights chain with `abstention`'s.
