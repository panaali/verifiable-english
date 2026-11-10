# ps-2ac: Run.lean, the presuppositions report value (spec 4.7, PS-2a part 4) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): no route reads the report until PS-4.
Status: built; HEAD in "Final checks". `lean/VE/Presupposition/Run.lean`: `shown`, the `presuppositions` field PS-4 puts
in the document mode's answer, read off `admit`, with 38 guards. Trust V +109, K +0 (R16); R16 sweep 132 KILLED,
0 SURVIVOR, 0 UNKNOWN. Selected tests: 117 units, 0 failed (2966efed3). DRI rulings: reviews/dri-decisions-20261110-ps-2ac-layer.md
items 1-2, -ps-2ac-report.md items 1-2, -ps-2ac-size.md item 1. Next: ps-4.

Task prompts/task-ps-2ac.txt (deliverable (4) of task-ps-2ab.txt); plan `docs/spec/presupposition-PLAN.md` PS-2a
(:847-864) and 4.6 (:498-501); spec `docs/spec/presupposition.md` 4.7 (:837-839), 2.3 (:345-363), 5 (:1303-1321).
Branch `feature/ps-2ac`, merge base a5088a09b (main, ps-2ab merged). Command outputs: `evidence/tests.txt`.

## Preconditions

- **ps-2ab merged.** `admit`, `admitWith`, `admitWrapped` and A1-A28 are on main; no type Run.lean needs was missing.
- **Statement gate.** PASSED, as the task states. `evidence/probe.py` (output in `evidence/tests.txt`): none of Run.lean's
  43 declarations is named in the spec's Lean blocks or the PS-S stub, so none can differ; ps-2ab's probe rerun: the
  19 statements are 19/19 equal to spec 4.7. This item adds no theorem.
- **Read-only files** (Admit, Wire, Frame, Reading, Rows, Rules, Agree, `Protocol.lean`, `service_schema.py`):
  unchanged (changed-file list in "Final checks").
- **In-flight overlap.** No branch in flight touches Run.lean. feature/cmp-s3-cfr-1, feature/en-e3a and feature/ps-7
  also add entries to `tools/trust-classes.json` and `docs/trust-baseline.json`; this item's trust-classes entry sits
  beside Admit.lean's, away from the end where they append.

## Plan rows delivered

| Row (plan PS-2a :854-858; task "Deliver") | Run.lean | Guards (Run.lean lines) |
|---|---|---|
| one row per obligation, block order | `shownOf` | :166, reversed :168 |
| `id`, `unit`, `carrier` | `checkedRow` | :166, :173 |
| `goal`: P0 formula and the English line rendered by Lean | `Goal`, `Line`, `englishLine`, `lineOf`, `lexiconOk` | :173-226 |
| `outcome` (checked, or the diagnostic) | `Outcome`, `outcomeOf`, on `Shown` (DRI ruling) | :170, :229-233 |
| unresolved: emitted readings with aliases | `checkedRow` | :241, :248, alias :264 |
| `PresuppositionRefuted` lines from the existing inconsistency report | `Inconsistency`, `docPremise`, `refutedLines` | :280-305 |
| no runMode, MODES entry, schema or Python relay (PS-C9) | — | changed-file list |
| trust-classes rows, `lean/VE.lean` import, generated inventories | side table, `regen_generated.py` | "Trust", "Final checks" |

## What the value is

`shown L inc D := shownOf L inc D (admit D)`, absent without the block (as `admitWrapped`; :238). PS-4 passes the
request's lexicon `L` (`VE.English.Run.decodeLexicon`) and the document's inconsistency report; for the document's
situations it calls `shownOf` on `admitWith`.

- **Outcome on the field (deviation from the plan text, DRI ps-2ac-report item 1, ACCEPTED).** `admit` is all or
  nothing, so `Shown.outcome` is `checked`, `refused <admit's diagnostic>` or
  `unknown "ResourceLimit: presuppositions"` (UNKNOWN, never a refusal). Not every refusal names the obligation
  at fault (review F1): steps 2 and 4 name it; steps 3 and 5 name the unit's or rule's first obligation; step 5's
  tree check names the block's first rule act, else its first obligation, so on an empty block it reads
  `PresuppositionMismatch: : rule` and names none; step 5's readings refusals (`needsModelText`, `notSeparatedText`,
  `softText`) name no obligation and no unit.
  Guards :309-340 pin each case (text, obligation quoted, unit quoted). Rows exist only under `checked`; a refused or
  unknown block has none and is not walked (:229-233). Run.lean writes no diagnostic text of its own.
- **Goal.** The formula stays typed; PS-4's encoder writes P0's wire form. The English line is `shown <text>`,
  `notShown` or `unknown`. The text is the core renderer's clause without the full stop (2.3's lines quote it). It is
  shown only when the lexicon passes `lexiconOk` and the sentence parses back, in the document's environment, to
  exactly the goal (checklist 9). `lexiconOk`, once per report: at most `maxLexicon` (512) entries and no template of
  more than two places (else UNKNOWN), then `VE.English.admissible`, the hypothesis of `checked_parse_render`
  (lean/VE/English/Proofs.lean:179). Guards: uncovered predicate :192; "ready" worded as "owner" and the reverse
  :196-197 (the second would read "… is ready" for an owner); 200 and 201 nodes :207; 512 and 513 entries :214-218;
  three places :214, :224; a predicate without a template :226.
- **Refuted.** The existing inconsistency report is P0's: premises and a certificate of `⊥` (`PremiseStatus.inconsistent`,
  lean/VE/SpeechActs/Run.lean:242-246). When every premise is the document's (background or asserted claim) and the
  certificate checks, an admitted assumed obligation gets `PresuppositionRefuted: <o>: <unit>` if the refutation uses
  its goal: the certificate no longer checks with that premise replaced by `⊤`. The other premises then refute it.
  Lines (:280-296): both goals used, one, a background premise, any order. No line (:291-305): a contradiction that
  uses neither goal, a premise not the document's or only in an unasserted unit, a certificate that does not close, no
  report, a proved carrier, a refused block. No line claims nothing.
- **Readings.** An admitted unresolved obligation's row lists its unit's readings (`RReading` with aliases), which
  `admit` checked are exactly `expectedReadings`; any other row lists none (:248).

## DRI rulings

- **Layer (-ps-2ac-layer items 1-2).** The only Lean renderer of a formula is `VE.English.render` (layer 3). Item 1
  signed a layer-3 declaration; `tools/check_lean_imports.py` refused it ("role fixes its layer at 4",
  `tools/layer_policy.py:357`); item 2: no declaration, layer 4 by role, an inward import. No `layer_policy` edit, no
  ledger exception, no layer-2 importer (DELTA.md's grep); the check passes; renderer and lexicon mutants
  (M-englishLine, M-lexicon) break :173.
- **Outcome (-ps-2ac-report item 1).** Conditions: refused A-fixture with its diagnostic and no rows (:229, :231); A15
  `unknown`, no rows (:233); admitted, `checked`, rows in block order (:166, :170); M-rows-under-refusal and
  M-shownOf-error break them. FOLLOW-UPS row: align the plan text.
- **Shallow frame (-ps-2ac-report item 2).** At a negated or antecedent frame `¬U` entails `B`, so the assumed `B` and
  the conditioned `U → B` are equivalent and step 5 never separates them: the fixture table's negated cell
  `[assumed, conditioned, inPlace]` gives an open set never admitted (:258, both witness orders, `notSeparatedText`).
  The alias guard uses `[conditioned, asserted, inPlace]` (:263-264). Design row ps-shallow-sep.

## Seeded bugs (Lean only; no Python or Rust product code changed)

36 hand mutants (`mutants.json`), each applied alone with `lake build VE.Presupposition.Run`, then restored
(`evidence/tests.txt`): **31 break a named guard, 5 are INVALID** (data types `Outcome`, `Line`, `Goal`, `Shown`,
`Inconsistency` with a constructor or field dropped: they do not elaborate, which BUILDER-CHECKLIST item 3 does not
count; those types are read by the guards at :170, :192-207, :173, :229-233, :280-305). Every other new definition has
one that breaks a guard; `Row` has one too (fields `id` and `unit` swapped, :173).

| Id | Behaviour | Definition | Breaks |
|---|---|---|---|
| S1-drop-row (task) | one row per obligation, block order | `shownOf` | :166 |
| S2-unit-carrier (task) | unit and carrier are the obligation's (a literal swap does not elaborate: unit read off the carrier) | `checkedRow` | :166 |
| S3-no-refuted (task) | the PresuppositionRefuted line | `refutedLines` | :280 |
| M-rows-under-refusal | no rows when refused | `shownOf` | :229 |
| M-refuted-unused | only a goal the refutation uses | `refutedLines` | :284 |
| M-englishLine-parse | shown only if it parses back | `englishLine` | :192 |
| M-lexiconOk-admissible | the lexicon is admissible | `lexiconOk` | :196 |
| M-englishLine-nodes | a goal is charged before rendering | `englishLine` | :203 |

## Trust

`tools/trust_map.py --check` PASS against a5088a09b523: trusted +109 (all untied G[V] in Run.lean: `Outcome`, `Line`,
`Goal`, `Row`, `Shown`, `Inconsistency`, `lexiconOk`, `lineOf`, `englishLine`, `outcomeOf`, `checkedRow`, `docPremise`,
`refutedLines`, `shownOf`, `shown`), K +0, S +0, unclassified +0; G[R] `maxLexicon`, `maxLineNodes`; T 26 guard
fixtures. `docs/trust-baseline.json`: allowance V +109, "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-2ac,
2026-10-18" (within 150, no K growth, every new trusted definition broken by a guard: the sweep below). FOLLOW-UPS.md
"## ps-2ac" has the ties-pass row.

**R16 sweep** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json trust-mutants.json --test
lean/VE/Presupposition/Run.lean`, on the VM: no Mac slot). Run 1 (fb4406aaf, 772 s): 117 KILLED, 18 SURVIVOR,
30 UNKNOWN, 28 INVALID. The survivors were list positions and boundaries the guards did not move; each now has a guard
(:185, :207, :218-226, :292-296). The UNKNOWNs do not elaborate. Run 2 (0763bcc70, full: Run.lean changed, 784 s) and
the rescore after an allow-only edit (111 s): **132 KILLED, 0 SURVIVOR, 0 UNKNOWN, 28 INVALID, 33 ALLOWED, exit 0**.
`trust-mutants-allow.json`: 30 do not elaborate; 3 equivalent `lineOf` mutants (`(s.take 1).isEmpty` is `s.isEmpty`;
in the punctuation branch the word is one character, so `w.take 1` is `w`; applied by hand, the build passes).

## Size, bytes, evaluators

- **Size** (`git diff --numstat a5088a09b`, without generated files and the sweep's output `trust-mutants.json`):
  Run.lean 305 (product 136, guards and fixtures 169), REPORT 145, `trust-classes.json` 51, `evidence/` 74,
  `mutants.json` 38, `trust-mutants-allow.json` 16, DELTA 10, `trust-baseline.json` 7, `VE.lean` 1: **647**, over the ~600
  guide. The growth past it is guards the R16 sweep required (18 survivors to 0) and the self-review's four A fixes;
  the deliverable is one file with no coherent cut. Accepted: reviews/dri-decisions-20261110-ps-2ac-size.md item 1.
- **Pilot bytes.** 0: no route reads the report yet.
- **Evaluators** (rule of 2026-10-27). `shown` reads `admit`'s answer once; `admit` has charged the block (256) and each
  goal (W1's 10,000 nodes); a refused or unknown block is not walked. The lexicon is charged once per report before any
  line, and each goal against `maxLineNodes` (200) before it is rendered: rendering and the parse back grow faster than
  the goal (interpreted probe, not a benchmark: parsing back a 9,611-node goal took 3.5 s, a 611-node one 55 ms; the
  self-reviewer measured 10.5 s to render 8,003 nodes). The parser tries `pool ^ arity` tuples per template, so a
  template of more than two places is refused first. Fixtures: 256 obligations, 256 lines (:235); 257, no rows (:233).
  The certificate is checked once, plus once per assumed obligation whose goal is a premise (at most 256).

## Spec re-read

- Plan PS-2a `:854-858`, against the rows above: id, unit, carrier; goal with wire formula and Lean's English line;
  outcome (on the field, ruled); unresolved readings with aliases; the Refuted lines.
- `PresuppositionRefuted: <o>: <unit>` (`presupposition.md:361-362`, `:1321`): obligation id, then the assumed unit;
  "the premises refute an assumed goal"; a report line, not a diagnostic (in `refuted`, not in `outcome`).
- `:837-839`: no mode, runner or schema; absent without the block (Admit.lean:293, :238). Spec 5 `:1320`: ResourceLimit
  is UNKNOWN (:233). 2.3 `:345-363`: no symbols or ids in the line; ids are row fields for the provenance view.

## Final checks

- **Changed files** (`git diff --name-only main...HEAD`, without the regenerated `docs/codemap/`): the six files under
  `docs/presupposition/ps-2ac/`, `docs/trust-baseline.json`, `lean/VE.lean`, `lean/VE/Presupposition/Run.lean`,
  `lean/declarations.txt`, `lean/predicates.txt`, `tools/trust-classes.json`. No Python, Rust, `Protocol.lean`,
  `Document.lean` or schema file.
- **Regenerated files.** `uv run python tools/regen_generated.py --write --skip route-cases`: rc 0, "wrote 37 entries"
  (fb4406aaf). `route-cases` needs the Rust release binary, which this worktree lacks, and reads no presupposition
  file (ps-2ab skipped it the same way). `lean/VE.lean`'s import list has no writer (`lean-roots`, union-merged): one
  hand-added line, as ps-2ab did. `lean/declarations.txt` refreshed by `tools/lean_statements.py` after the last Lean
  edit (87670b9cc). The `docs/codemap/tests--*` changes come from main's stale code map.
- **Lean.** `lake build`: "Build completed successfully (1356 jobs)". `python3 lean/audit.py`: "PASS: 823 source files;
  9276 named theorem declarations audited …; only the declared standard axiom allowlist". ps-2ab's condition guards
  (A5u-allow, A5u-deny, A19-A21, A24-A28 in Examples.lean) build in it.
- **Layers.** `tools/check_lean_imports.py`: "Lean layer graph kept (823 modules, 18 reviewed legacy edges)".
- **Collection.** `tools/gate_collection.py --check --prebuilt`: "33418 collected …; 0 added, 0 removed by a trailer,
  0 refused, 0 stale and 0 malformed trailers". No test removed.
- **Trust.** `tools/trust_map.py --check`: "PASS: K, S and untied [V] within a5088a09b523 and the allowances introduced
  since". R16 sweep: "Trust".
- **Selected tests** (final, on the committed tree 2966efed3, clean): `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select --
  --base a5088a09b --run`, run on GitHub Actions in 5 shards: "SHARD 1/5 … 27 passed", "2/5 … 25 passed", "3/5 … 24
  passed", "4/5 … 22 passed", "5/5 … 19 passed"; "summary: … exit=0; 2025s". No failure, so none from
  main-known-red.txt. Commits after it change only `docs/presupposition/ps-2ac/REPORT.md`.
- The full release gate is not run here; the chain runs it on the final HEAD.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 4 A, 7 B, 7 C; fixed 17 (self-reviewer agent, one call, on ada29563f). A: Refuted named goals the
refutation did not use; the line lacked `admissible`; parse and render costs were not charged before work (lexicon
arity, goal size). B: per-row outcomes on a refused block, rows for an oversize block (both: DRI ps-2ac-report item 1);
a two-valued line; premises not tied to the document; a surviving `unresolved` mutant; FOLLOW-UPS rows; the shallow-
frame finding sent to the DRI. C fixed: mutant counts, the label-first guard, DELTA's grep, decision items, long lines,
HEAD. C not fixed: a RunExamples split (a FOLLOW-UPS row; it needs a layer declaration on the new module).

1. Lean answers typed and contained: N.A. No relayed answer or schema; `Shown` is typed to the leaves for PS-4.
2. Every deliverable built: PASS. "Plan rows delivered"; the outcome placement is ruled (DRI ps-2ac-report item 1).
3. Tests can fail: PASS. 31 hand mutants break named guards (`mutants.json`); R16 sweep 132 KILLED, 0 SURVIVOR.
4. Python, Lean and Rust agree: N.A. Lean only; nothing else decides presuppositions.
5. R8 binding: N.A. No relay (ps-2b binds the field; rows only under `checked`, as ruled).
6. Gate evidence matches HEAD: PASS. Hand mutants and the sweep were rerun after the last Lean edit; the selected run is on
   the committed tree ("Final checks").
7. No unsigned item: PASS. Trust growth: R16 allowance; layer, outcome and shallow frame ruled; no DELTA row.
8. User-visible changes in DELTA: PASS. None (DELTA.md: the grep and the changed-file list).
9. Test selection: PASS. The selected run includes `lake build` and `lean/audit.py`, which build every Run.lean guard.
10. Statements: PASS. No theorem added; the probe shows 19/19 statements unchanged.
11. Budgets fail closed: PASS. 257 obligations `unknown` (:233); a goal over 200 nodes and a lexicon over 512 entries or
    with three places give `Line.unknown` (:203, :207, :214-224), never a shown line.
12. No CPU or memory regression: N.A. for pilots (no route reads it). In Run.lean each limit is charged before rendering
    or parsing ("Evaluators").
13. Test-removed trailers: N.A. No test removed (`gate_collection.py --check`).
14. Both directions, cited evidence, spec re-read: PASS. Each check has its accepted twin (:192/:193, :196/:179,
    :207 200/201, :218 512/513, :280/:291); "Spec re-read".
15. Overclaim, silent cut, checks that can fail, limits first: PASS. Universal words checked against the cited guards;
    no cut; every new check has a mutant; limits charged before work.
