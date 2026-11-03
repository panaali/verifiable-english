# ci-1 report: the Lean command reader

**Status:** first part built; proved, fixtures pass, trust mutants exit 0; no signature reserved. **Head:** the commit of this file, on feature/ci-1, not synced with main (92 commits behind at ec141e96a; the merge train syncs, R12).
**What changed:** `lean/VE/Commands/` (reader, texts, fixtures), `readingsBound` in `Wire.lean`, imports, layer, generated lists. No mode, so no answer changes; nothing calls the reader until CI-2.
**Open:** size is 1016 hand-written Lean and policy lines against the DRI's "about 900" (reviews/dri-decisions-20261102-ci-1-size.md); the about 120 over are the fixtures R16's mutants required, 38 of them the review fix's; the side table and evidence add 456 more. `readCommand_typed` is ci-1b's.
**Signature:** none needed. V +131 under R16; K +0.

`FOLLOW-UP: ci-1b the rest of CI-1: readCommand_typed with hw, candidate_guard, candidate_fills, guard_ambiguous, guard_limit, guard_unread, refused_classed, F0's rows, the other 50 web segments`

## Deliverables

| Task item | Delivered | Evidence |
|---|---|---|
| (1) `Texts.lean`, `Read.lean`: spec section 1 | yes, with the deviations below | `cd lean && lake build`: 1243 jobs, success |
| (2) `readingsBound`, the `64` of `readingCandidates`, no new literal | yes; only that line and the `def` change in `SpeechActs/` | `git diff main...HEAD -- lean/VE/SpeechActs`; `#guard`s on 0, 1, 2, 64, 65 readings |
| (3) Statements proved | `readCommand_prefix`, `_one_iff`, `_many`, `_complete`, `_bound`, `candidate_reads_back`, `readCommand_typed_of_facts` | `python3 lean/audit.py`: PASS, 736 files, 8208 theorems, the allowed axioms only; `grep sorry`: none |
| (4) Diagnostics, section 4, in order | all 14 rows | `Examples.lean`, the W rows; `Texts.lean` holds every text |
| (5) Fixtures | W1 to W15, W17 to W31, W32's shape on `E_web`; S3's two rows on `E_web`; each limit at its boundary | 71 `#guard`s, `lake build VE.Commands.Examples`. W16 (F0) and the other 50 segments are ci-1b's |
| (6) Imports, layer, inventories | yes | `uv run python tools/regen_generated.py --check`: 35 entries; `tools/check_lean_imports.py`: kept |

Limits: `maxWordingBytes` 400/401, `tupleCount` 4096/4097 (64 regulated predicates, 67 and 68 constants), `readingsBound` 64/65, a 100,000-byte wording stops at `limit`. Each value is read once: `readCommand` computes the phrase matches, act matches and condition once and passes them on, and no act match means no condition read (`#guard` on `conditionOf`). The one second read is the spec's: `unreadOf` reads the sentence again at `workBudget`, for its text, on a refusal only. Open: `eraseDups` is quadratic in act matches times guards, with act matches at most 4096 by the tuple cap. A condition can have two derivations: V4 lets modal predicates share a form (`Lexicon.lean:489-492`). Across sorts (`goSorts`) one reading fails decode and the reader says `IllTyped`. In one sort, with acts the speech wire keeps apart by case (`goCase`: `{0} go`, `{0} Go`), both decode: two guards, and `many`. Both are `#guard`s under W17. Whether any other condition has two guards is not proved.

**A/B:** no record to compare: `git diff --name-only main...HEAD -- ve rust` lists only `ve/assurance-manifest.json`, a pin, and no mode or schema changes.

## Deviations from the spec at 9a12df17a

1. `readCommand_typed` is false as stated: a misordered raw `Json` gives `.one` with `scopeOk` true and `commandOk` false (the counterexample was at 2937f5fcf; its guards are on wip/ci-1b-proofs). The DRI added `hw` (reviews/dri-decisions-20261102-ci-1.md item 1), and split the decoder half (size ruling items 1 and 2).
2. `VE.Commands.Read` is layer 4, not the prefix's layer 3: it imports `EnglishGrammar.Run`, and on layer 3 the lint refuses it (`new outward Lean import`). The prefix and the examples row are as the task says.
3. `ve/assurance-manifest.json` changes, though the task says nothing in `ve/`: it pins `Wire.lean` whole and must classify every JSON-handling Lean file. Data only; `docs/spec/assurance-manifest.md` regenerated.
4. `refusal se sc E L b s` is `refusalOf s p pm ms gr`, and `conditionOf`, `readingsOf`, `ofForce`, `firstMatch`, `guardList`, `unreadOf`, `noReading`, `Outcome.ofText` are factored out, so each value is read once (common rule; me-12 N1). `candidates` is the spec's on every input: `readingsOf p [] gs = []`.
5. The texts live in `Texts.lean` as pairs, and `Texts.classOf` in `Read.lean`, so `Texts.lean` imports nothing.
6. `readCommand_bound`'s `hp` is unused (a candidate implies it); the binder is `_hp`, the statement is the spec's.

## ci-1b

Proved already on the local branch `wip/ci-1b-proofs` (df2dee88b), except the decoder half: `candidate_guard`, `candidate_fills`, `guard_ambiguous`, `guard_limit`, `guard_unread`, `refused_classed`; F0, the 59 segments and the `JsonWF` guards. The DRI's conditions (i) to (iii) go with it. The statement it owes:

```lean
theorem readCommand_typed (j : Lean.Json) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hw : VE.Scope.JsonWF j)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : readCommand se sc E L b s = .one r)
    (hE : D.E = se.ne.rv.environment) (hS : D.scope = sc) (hR : D.regulated = se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) :
    VE.SpeechActs.commandOk D (r.command u) = true
```

It reduces to `readCommand_typed_of_facts` by a proof of `declared se = true` from `hw` and `hd`. The 59 list's bytes sum to 2,573 by program against R 2.1's hand 2,563; the nine that read sum to 273, R's figure.

## Seeded bugs

`mutants.json`: nine in `Read.lean`, each in a scratch overlay with the proofs cut, so each fails its `#guard` and not a proof, control clean. The plan's five and three of the spec's: W9 and W22, W10, W8, W17, W18, W28, S3's `TypeMismatch`, W31; and `conditionOf` reading with no act match. Python: `VE.Commands.Read` on layer 3 fails `tools/check_lean_imports.py`.

## Trust and mutants

`uv run python tools/trust_map.py --check`: PASS, K +0, S +0, V +131, all `VE/Commands/Read.lean`, unclassified +0. Nine definitions are tied (`candidates`, `parts`, `roleOf`, `filled`, `fold`, `phraseMatches`, `ofForce`, `readCommand`, `Reading.command`, to `candidate_reads_back`, `mem_phraseMatches`, `mem_ofForce`, `readCommand_one_iff`, `readCommand_typed_of_facts`); diagnostics are G[R].

`trust-mutants.json`, at ec141e96a (a full run, `--rescore` found the classes file changed; no Lean file changed since): exit 0, 248 mutants over 16 definitions: 175 killed, 24 invalid, 49 allowed, 0 left. The allow file gives each reason; each of the 16 raw survivors was checked against its reason, and two false reasons were replaced by fixtures: that the decoder refuses `{0} {1}`, and that `guardsOf` never holds two guards (M094 and M175, now killed at `Examples.lean:167`). The reason "a decoded environment has at most two argument sorts" was rerun on three sorts: the decoder says `invalid signature`.

## Review fixes (ci-1-review.final.md)

F1 (A): the report and the allow file said a V4 lexicon gives no condition two derivations. It does, and the review's proposed reason, that one reading always fails decode, is false too: `goCase` gives two guards. So the two allow entries are gone and the fixtures kill their mutants; no reason was restated. Probe F1 passes. It is not a permanent test, since it greps batch prose (D4, R11); the `#guard`s under W17 are the regression.

`FOLLOW-UP: ci-rev spec W17's "grammar's actions separate" is false: goSorts and goCase are its counterexamples`
`FOLLOW-UP: ci-rev the speech wire's DuplicateActRole compares acts exactly, so {0} go and {0} Go both decode and share a modal form; the reader answers many, no guess; decide whether the wire should refuse them`
`FOLLOW-UP: ci-2 the review's F3 to F8 (C), F3 for its A/B, and goCase's row there`

## Pilot bytes

Estimate, nothing claimed: the plan's +9 units / +273 B on the web fixture is CI-2's to reach.

## Tests

`mac-pytest.sh --select` at ec141e96a: exit 0, 417 units, no failed id. No test in main-known-red.txt failed. After it only this report and the mutant evidence changed. `tools/layer_policy.py` is in the diff, so selection widens to the policy's rule; the cause is the task's own edit. Not run: the full gate (the chain's); `gate_collection --check --prebuilt`: 0 added, 0 refused. Shared files: `tools/layer_policy.py` overlaps feature/cmp-s4 and feature/pc-1; `lean/VE.lean`, `lean/VE/Audit.lean`, `tools/trust-classes.json` and `ve/assurance-manifest.json` also changed on main, for the merge train's sync.

## Self-review against BUILDER-CHECKLIST

1. Lean answer typed: N.A., no relayed answer until CI-2.
2. Deliverables: PASS, the table above; the rest named ci-1b by the DRI's size ruling.
3. Tests can fail: PASS, `mutants.json`, `trust-mutants.json` exit 0.
4. Py/Lean/Rust agree: N.A., no route; CI-2's A/B.
5. R8 binding: N.A., no relay.
6. Gate evidence: PASS for what a builder runs: `gate_collection --check --prebuilt`; not synced with main, stated above; the gate is the chain's.
7. Nothing unsigned: PASS, `DELTA.md`'s one row cites R16.
8. User-visible change: PASS, none: `git diff --name-only main...HEAD -- ve rust`.
9. Selection: PASS, `tools/select_tests.py --base`; widened by `tools/layer_policy.py`, the known cause.
10. Statements say what is claimed: PASS, `readCommand_typed_of_facts` is about `readCommand`'s value; the `addressed` and `manyOf` seeds break their proofs (first run of the seeded bugs).
11. Limits fail closed: PASS, W18 (budget 0), `limit` rows at each boundary; `readCommand_bound`.
12. No CPU regression: N.A., no caller; `Examples.lean` builds in about 40 s.
13. Test-removed trailers: N.A., no test removed; `gate_collection`: 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS, each limit has both sides, W1 reads and W10 does not for `_one_iff`, the section 3 statements kept were compared with the spec word by word.

Next item: ci-1b, then ci-2 (`english.command`), then ci-5.

