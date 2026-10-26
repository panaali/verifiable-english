# ap-1f build report: `decodeRegulated_plain`, the last theorem of act-phrases 4.3

**No DRI signature is reserved; nothing stops the item.** `decodeRegulated_plain` is proved exactly as spec 4.3
states it on main's decoder (ap-1b and ap-1bb merged). Trust +0, bytes 0, no answer changes. Spec 4.3 is complete.

Plan and spec on `main` at `a547f2141`: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1" and 2.1;
[act-phrases.md](../../spec/act-phrases.md) 4.3 and 14.3. Read first: [ap-1e's REPORT](../ap-1e/REPORT.md) section 6,
[ap-1b's](../ap-1b/REPORT.md) and [ap-1bb's](../ap-1bb/REPORT.md), and `manage-agents/FOLLOW-UPS.md` "## ap-1a",
"## ap-1d" and "## ap-1e".

## 1. Statement gate

The gate is the same one ap-1a to ap-1e passed. The statement review converged, draft 2 applied its edits (14.3,
SR1-SR16), and none of them touches `decodeRegulated_plain`. The statement in `lean/VE/Norms/Wire.lean` equals spec
4.3's after whitespace normalisation. The probe below prints `True`; it compares the spec text from
`theorem decodeRegulated_plain` to `end VE.Norms.Wire` with the Lean text up to `:= by`:

    python3 -c "s=open('docs/spec/act-phrases.md').read();i=s.index('theorem decodeRegulated_plain');t=open('lean/VE/Norms/Wire.lean').read();j=t.index('theorem decodeRegulated_plain');n=lambda x:' '.join(x.split());print(n(s[i:s.index('end VE.Norms.Wire',i)])==n(t[j:t.index(':= by',j)]))"

No definition changed: `git diff main...HEAD -- lean/` adds only the two theorems and the regenerated inventories.
`decodeRegulated`, `decodeRegulatedWith` and `decodeRegulatedIn`, and everything ap-1a and ap-1b pinned, are
unchanged. The statement is true on main's decoder, because `decodeRegulated` is `decodeRegulatedWith false
canonicalAct`. Without `acts@0`, a plain declaration may not carry an `act` key (`allowed`), and its act is `pure none`.
So no counterexample `#guard` was needed.

## 2. Task rows delivered

| Task deliverable | Status | Where |
|---|---|---|
| (1) `decodeRegulated_plain` in `lean/VE/Norms/Wire.lean` | **done** (`984eba107`), with the helper `ite_ok_cases` (the branch an `if` that answered `.ok` took, with its condition). The proof walks the decoder's binds, `if`s and `match`es (it reuses `VE.Order.ProfileGate.bind_ok`); `split` on an `if` hits simp's step limit on this decoder | `Wire.lean:100-121` |
| (1) its `#print axioms` line in `lean/VE/Audit.lean` and the regenerated inventories | **done** by `tools/regen_generated.py --write` (Audit.lean, axioms.txt, statements.txt, declarations.txt, checkers.lock). `ve/assurance-manifest.json` re-pins `Wire.lean` (lines, sha256, range end, `total_lines` +23), and `tools/assurance_manifest.py --write` regenerates its doc table. `lean/audit.py` PASS. `decodeRegulated_plain` depends on `[propext, Quot.sound]` | `984eba107` |
| (2) seeded bugs: decoder mutants that set an act on a plain predicate and break the theorem, in `mutants.json` | **done**: 3 decoder mutants and 1 helper mutant, all KILLED inside the named theorem (section 4) | `a4a891cdf` |
| (3) the tie of `decodeRegulated` in `tools/trust-classes.json`, if the ties pass asks for it | **not needed**: "## ap-1a" asks for ties of `check`, `group`/`lex`/`decodeFixed`, `decodeRegulatedIn` and `canonicalActIn`, not of `decodeRegulated` (section 5) | — |

## 3. Deviations

None from the plan or spec. `ite_ok_cases` is a helper theorem that spec 4.3 does not name. It is not a definition,
so it adds no trusted lines.

## 4. Seeded bugs (Lean; no Python or Rust product code changed)

`uv run python docs/act-phrases/ap-1f/seed_bugs.py` writes each mutant into `lean/VE/Norms/Wire.lean` and builds
`VE.Norms.Wire`. A mutant counts as killed only when an error lies inside the theorem it names. It then restores the
file and checks that the restored tree builds. Output is in [mutants.json](mutants.json); 4/4 are killed.

| Id | Behaviour broken | Mutation (in `lean/VE/Norms/Wire.lean`) | Failing test |
|---|---|---|---|
| plain-some | a plain predicate decodes with no act | `decodeRegulatedWith`: the plain branch `pure none` becomes `pure (some name)` | `decodeRegulated_plain` (Wire.lean:110, unsolved goals) |
| acts-on | today's decoder reads no plain act | `decodeRegulated := decodeRegulatedWith true canonicalAct` | `decodeRegulated_plain` (Wire.lean:121, simp fails) |
| plain-act-key | without `acts@0`, an `act` key on a plain predicate is refused, never read | `decodeRegulatedWith`: `allowed` and the act condition drop `acts &&` | `decodeRegulated_plain` (Wire.lean:110, unsolved goals) |
| ite-swap | `ite_ok_cases` names the branch taken | branches swapped in the statement | `ite_ok_cases` (Wire.lean:104-105) |

R16 mutants: N.A., because the item adds no trusted definition (`trust_map.py --check`, section 5).

## 5. Trust, DELTA, bytes

- `uv run python tools/trust_map.py --check` at the final HEAD against `a547f2141`: K +0, S +0, D +0, G +0, tied +0,
  trusted +0, PASS. No allowance and no FOLLOW-UPS R16 row were needed.
- No tie added. `decodeRegulated_plain` pins one property of `decodeRegulated` (a plain role means no act), not its
  meaning; tying the decoder to it would drop the decoder's lines from the trusted count unread. The ties pass's
  request for `decodeRegulatedIn` (through `decodeRegulated_without_acts`) is unchanged.
- [DELTA.md](DELTA.md): no rows. No definition changed, so no output, diagnostic, verdict, limit, fault order or byte
  changes.
- Pilot bytes expected to move: 0. What it unlocks: spec 4.3 is closed. `Tree.check`'s dropped refusal of a plain
  act is now backed for documents without `acts@0`, which ap-3 and ap-4 build on (M7).

## 6. Tests

- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, ve-mac-1, HEAD `a4a891cd`):
  369 units recorded, 0 failed, exit 0. They include `tests/test_acts_lexical.py`, `tests/test_assurance_manifest.py`,
  `tests/test_norms*.py` and `tests/test_trust_budget.py`. No test from `main-known-red.txt` failed.
- `tools/gate_collection.py --check --prebuilt`: 19,392 collected at both ends; 0 added, 0 refused, 0 stale,
  0 malformed.
- Full gate: not run by the builder, per the task (the chain runs it on the final HEAD).

## 7. Next item

ap-3 (running), then ap-4 (after ap-3 and, in SYNTHESIS 4.2's protocol queue, qt-a3).

## 8. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer changes; no Python or Rust code changed.
2. PASS: section 2 copies each task row with its commit. The diff has no Python copy of a Lean decision and no new
   report test. Of the files in flight, only `tools/trust-classes.json` overlaps (ap-3, jt-2, me-2b, q1-4, sc-1b,
   me-1, arch-20261026-2), and this item leaves it unchanged.
3. PASS: `docs/act-phrases/ap-1f/seed_bugs.py`, 4/4 KILLED inside the named theorem (`mutants.json`). No trusted
   growth, so no `trust_mutants` run (R16 N.A.).
4. N.A.: no executable behaviour changed (bytes 0); the definitions are unchanged.
5. N.A.: no field read from a Lean answer is added.
6. N.A.: the gate is the chain's, on the final HEAD.
7. PASS: DELTA has no rows and no reserved signature; trust +0 (`tools/trust_map.py --check`).
8. PASS: no user-visible change, because no definition changed (`git diff main...HEAD -- lean/VE` adds theorems only).
9. PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects `tests/test_acts_lexical.py`,
   `tests/test_assurance_manifest.py` and the norms tests, not every unit. A changed theorem's failure is a build
   failure of `VE.Norms.Wire`, which the selected Lean-building tests run.
10. PASS: each of the theorem's claims breaks under a mutant (section 4). The statement equals spec 4.3 (section 1
    probe) with no added hypothesis; `lean/audit.py` PASS.
11. N.A.: no budget, limit or deadline touched.
12. N.A.: no executable code changed; the proof adds about 10 s to the build of `VE.Norms.Wire`.
13. PASS: no test removed or renamed. `tools/gate_collection.py --check --prebuilt` gives 0 refused, 0 stale and
    0 malformed.
