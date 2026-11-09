# ci-3a: the step reader (commands-imperatives section 7, CI-3's first part)

Status: built; 6 of section 7's 8 statements proved. `preposed_eq` and `readStep_conservative` move whole to ci-3
(reviews/dri-decisions-20261109-ci-3a.md item 2). No route calls `readStep`, so no verdict, wording or pilot byte
changes. DELTA row 1 is signed. Next item: ci-3.

## Delivered (spec 9a12df17a section 7)

- Steps.lean has `Shape` through `reads` as section 7 writes them: a probe of the 14 definitions and the 6
  statements found 20 of 20 equal. Exceptions:
  - `Form` comes from section 10 (reviews/dri-decisions-20261109-ci-3a-form.md);
  - `readStep`'s byte charge and the `hb` hypothesis (wording ruling item 1, DELTA row 1).
- The product is charged: `shapeOutcomeCharged` counts `productSize` before it builds the product. The kernel-checked
  `@[csimp] shapeOutcome_charged` sits before `readStep`, so compiled code calls the charged form (ruling item 1).
- Proved with no `sorry`, standard axioms only (`python3 lean/audit.py` PASS): `after_eq`, `seq_eq`,
  `shapes_ambiguous`, `seq_ambiguous`, `shapes_limit` and `shapes_complete`.
- StepsExamples.lean has:
  - every `E_web` row and the constructed aggregation rows;
  - finding (d), with the code only (O8);
  - the charges: the gate (line 144), 8×64 readings (148), 6 KB, and 400 and 401 bytes (164-165).
- Other files: lean/VE.lean (import), tools/layer_policy.py (layer 4) and tools/trust-classes.json (G[V]; two ties).

**Does W1's act linter make `hs` unnecessary?** ci-3a proved nothing about `readStep_conservative`, so the spec's
computed answer stands: `hs` stays. ci-3 proves it. `preposed_eq` needs `String.splitOn` lemmas that core Lean 4.24
lacks.

## Seeded bugs and mutants (Lean only)

`mutants.json` has 21 hand mutants, each with its `old` and `new` text, and each fails a fixture (StepsExamples
lines). The four the task names:
- `shapes` without `preposed`'s condition: 60-61;
- the generic refusal for one shape: 64;
- `many` beside a `limit`: 88;
- first-step-only tuples: 107-109.

The trust-mutants sweep (`mac-pytest.sh --trustmut`): `trust-mutants-full.json` has 175 KILLED, 20 SURVIVOR,
107 UNKNOWN and 36 INVALID. With `trust-mutants-allow.json`, `--rescore` gives `trust-mutants.json`: 175 KILLED,
127 ALLOWED and 36 INVALID, exit 0.

The allowed mutants:
- are equivalent;
- are text Lean refuses;
- break the `@[csimp]` lemma, which every check computes through (the hand mutants with the lemma blanked show the
  fixtures kill them);
- or come from `shapeAlts` being inlined.

## Trust (R16), size

`tools/trust_map.py --check` against d55d24faab75 gives K +0, S +0 and trusted +136 (Steps.lean). The allowance in
docs/trust-baseline.json is SIGNED by standing ruling R16; FOLLOW-UPS.md "## ci-3a" asks for the ties pass.
Hand-written lines: 890 (`git diff --numstat` against the merge base, without generated files or tool
output), accepted by reviews/dri-decisions-20261109-ci-3a-size.md item 1. Pilot bytes moved: 0.
