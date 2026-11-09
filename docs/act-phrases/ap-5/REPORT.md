# ap-5 report: specialisation, definitions and generator only

**Summary.** Status: built, all checks passed; selected tests in section 9. What changed: new
`lean/VE/Acts/Specialise.lean` holds `Restrictive`, `Modifier.restrictive`, `specialises`, `specPremises` and spec 8's
four statements, proved with no `sorry`. New `lean/VE/Acts/SpecialiseExamples.lean` holds 11.5's fixtures and a guard
for each seeded bug. Both are registered in `lean/VE.lean`, `tools/layer_policy.py` and `tools/trust-classes.json`.
Open items: none in this item; ap-5b (the base-level bridge) is next. DRI signature needed: none; the trust growth
(+32, K +0) is under R16 (section 5).

## 1. Statement gate

The spec's statement review accepted section 8 (debates/act-phrases-spec/, applied in plan draft 3), including C21
(`specPremises_plain` without its free `p`, `docs/spec/act-phrases.md:1919`).
`python3 docs/act-phrases/ap-5/check_statements.py` splits section 8's Lean block at each `structure`, `def`, `theorem`
and docstring. It finds each item, whitespace-normalised, in `Specialise.lean` and prints `10 of 10 items verbatim`
(exit 0). Section 8 gives `specPremises` only as a signature and a docstring; its body is this item's (section 2).

## 2. Design

- **`specialises`** is section 8's text. `specialises_trans` holds because an argument or modifier that `a` has beyond
  `c` is either beyond `b` too (restrictive by `a ⊑ b`) or in `b` and beyond `c` (restrictive by `b ⊑ c`).
- **`specPremises E ρ acts`** looks up each act's predicate once (`declaredOnce`: its one regulated declaration).
  Over every ordered pair `x`, `y` of the found ones, in `acts` order, it emits
  `bindAll x.sorts (.implies (atom x.name x.sorts) (atom y.name x.sorts))` exactly when:
  - the role is not `.plain`, and the two roles are equal;
  - the two sorts are equal;
  - the two atoms differ;
  - `specialises ρ x.2 y.2` holds.

  `bindAll` and `atom` are `VE.Norms.Basic`'s. So a premise is `∀x:s. pa(x) → pb(x)`, or `∀x:s. ∀y:t. pa(x, y) →
  pb(x, y)` (guard 115).
- **`declaredOnce`** is what makes `specPremises_plain` hold with no well-formedness hypothesis (C21 states none). A
  plain `r` named like `x` would be `x`'s one declaration, which is not plain; the same holds for `y`, whose role is
  `x`'s. On a well-formed document no name is declared twice anyway: `check` refuses a duplicate with
  `DuplicateDeclaration` (`lean/VE/Norms/Tree.lean:306`).
- **`specPremises_typed`** reads `VE.Norms.valid_of_wellFormed`. Its `decl` field says each regulated predicate is
  declared in `E.E` with its sorts, of arity 1 or 2, over declared sorts. `atom_wellFormed`, `bindAll_wellFormed`
  and `check_iff_wellFormed` then give `φ.check E.E [] = true`.
- **No hook.** AP-5 is not a premise pack and has no Background hook. A carried premise over a regulated predicate
  is refused (`lean/VE/Readings/SupExtra.lean:14-19`), so these premises cannot be used until AP-5b's bridge over
  base predicates.

## 3. Plan rows delivered and not delivered

| Plan or task row | Delivered by |
|---|---|
| AP-5 goal: `specialises` over the declared restrictive markers and modifiers, and `specPremises`, as Lean definitions with proved properties | `lean/VE/Acts/Specialise.lean` |
| New file `Specialise.lean` (`specialises`, `specialises_refl`, `specialises_trans`, `specPremises`, `specPremises_typed`, `specPremises_plain`) | all four proved, no `sorry`; `python3 lean/audit.py` PASS (section 5) |
| `SpecialiseExamples.lean`, with `#guard`s on the generator | `lake build` builds it (section 5) |
| 11.5: `specialises ⟨["in"], []⟩ a b = true`, `⟨[], []⟩ a b = false`, `⟨["in"], []⟩ b a = false` | `SpecialiseExamples.lean:51-53`; `a` and `b` built by `analyse` (`act`, line 23), their atoms pinned at 41-42 |
| 11.5: two permission predicates give exactly one premise `∀ x. pa x → pb x`; two plain none; two obligation one | lines 93-94, 100, 95 |
| Task extras: undeclared "nearly" false; a different head false; `a = b` no premise; different sorts no premise | lines 55, 57, 104, 106-107 |
| Shared files: none | only the registries the task names: `lean/VE.lean`, `tools/layer_policy.py`, `tools/trust-classes.json`, plus generated files |
| Moves: nothing until AP-5b | no route, request, answer, pack, profile, Python or Rust change (`git diff --stat` of the merge base: `ve/`, `rust/`, `tests/` untouched) |

**Not in this item** (each waits for AP-5b):
- the wire key `restrictive` and `VE.Acts.Wire.decodeRestrictive` (spec 1.9, and the wire table's row "AP-5 (used
  only under `act-specialise@0`, after AP-5b)");
- the IDE question;
- any Background hook, pack or profile.

So no route, request or answer changes, and no Python changes. AP-5b's tests (the conflict fixture, "may a person
seek asylum?") and its seeded bug are AP-5b's in the plan itself.

## 4. Seeded bugs and mutants

`python3 docs/act-phrases/ap-5/seed_bugs.py` works on `Specialise.lean` with its theorems cut, so a fixture must catch
each plant, not a proof. It first builds that cut text with no plant, as a control, then plants each bug in turn,
builds `VE.Acts.SpecialiseExamples`, records the failing `#guard` lines and restores the file. Its output is
[mutants.json](mutants.json): control build exit 0; 35 plants, 35 KILLED; restored build exit 0. Lean is the only
language changed.

| Seeded bug (task) | Guard that fails |
|---|---|
| `specialises` without the restrictive test on extra modifiers | 55 (the "nearly" guard), also 52, 54, 56, 65, 69, 109 |
| `specialises` without `a.head == b.head` | 57 (the different-head guard) |
| `specPremises` reversing the premise to `p_b → p_a` | 93 (the one-premise guard, exact formula), also 94, 95, 97, 115 |
| `specPremises` emitting a premise for plain entitlements | 100 (the plain guard) |

Mutants per new trusted definition (the common rule); mutants.json lists each with its guard lines:

- `Restrictive`: fields swapped.
- `Modifier.restrictive`: an adverb always restrictive; a marker read among the adverbs; only the first marker read;
  only the last adverb read.
- `specialises`, 18 plants:
  - the *to*, *be* and reflexivity checks;
  - the argument and modifier subsets, each also cut to its first or last element;
  - the restrictive tests, each also cut to the first extra, the last extra, or the first declared marker.
- `declaredOnce`: the first of two declarations read; the last read.
- `specPremises`, 11 plants: two roles; unequal sorts; sorts compared only by length; `a = b`; no `specialises`
  test; binders reversed; only the first premise kept; only the last premise kept.

**trust_mutants** ran as `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/act-phrases/ap-5/trust-mutants-allow.json --rescore docs/act-phrases/ap-5/trust-mutants.json --json
docs/act-phrases/ap-5/trust-mutants.json`. It exited 0 on ve-cloud-3 at 23048700: 153 mutants, 121 KILLED,
0 SURVIVOR, 0 UNKNOWN, 12 INVALID, 20 ALLOWED ([trust-mutants.json](trust-mutants.json)).

- The first run, at 0e4ec44f, left 3 survivors. M059 and M108 kept only the first or the last premise; guard 97 (three
  acts, three premises) now kills them. M132 dropped `a`'s first argument from the extras; guard 78 now kills it.
  seed_bugs.py's `premises-first-only`, `premises-last-only` and `extra-args-drop-first` show both guards killing
  them.
- The 20 ALLOWED mutants ([trust-mutants-allow.json](trust-mutants-allow.json)) are the cuts Lean refuses as
  ill-typed: an `Option` sliced as a list, a `[]` with no expected type under a projection, or the `r` bound by
  `[r]`. Their recorded details are `Invalid projection`, `Invalid field notation` and `Unknown identifier`.

## 5. Trust, size, tests and checks

- **Trust:** `uv run python tools/trust_map.py --check` reports `against 33fe04615107: K +0, S +26, D +0, G +6, tied
  +0, unclassified +0, trusted +32`, and `PASS`. All the growth is in `VE/Acts/Specialise.lean`:
  - S +26: `Restrictive` 4, `Modifier.restrictive` 3, `specialises` 8, `specPremises` 11;
  - untied G[V] +6: `declaredOnce` 6.

  It is recorded with `trust_map.py --allow` as "SIGNED by standing ruling R16 (DRI-RULINGS.md), ap-5, 2026-11-09"
  in `docs/trust-baseline.json`. The R16 conditions:
  - at most 150 lines, no K growth;
  - every new trusted definition has a guard that fails (section 4);
  - the ties-pass row is in manage-agents FOLLOW-UPS.md, under "## ap-5 (2026-11-09)".

  The examples' 20 declarations are class T. The theorems and `declaredOnce_mem`, `mem_specPremises`,
  `preds_bindAll` and `mem_preds_atom` are P by kind. Plan D8 (proved Lean only) holds.
- **Lean:** `cd lean && lake build`: `Build completed successfully (1344 jobs)`. `python3 lean/audit.py`: `PASS: 812
  source files; 9089 named theorem declarations audited ...; only the declared standard axiom allowlist`. The four
  statements use `propext` and `Quot.sound`, and `specialises_refl` also uses `Classical.choice` (`lean/axioms.txt`).
- **Generated files:** written only by `uv run python tools/regen_generated.py --write` (38 entries, exit 0), run again
  after the fixtures grew. It also brought `docs/codemap/` up to date with earlier merges on main (rights-cfr-4's
  `scan_open_acts.py` and test files); that is generator output, not a hand edit.
- **Size:** `git diff --numstat $(git merge-base HEAD main)` without the generated files and the script outputs
  (mutants.json, trust-mutants.json, trust-baseline.json) is about 600 hand-written lines:
  - Specialise.lean 134, SpecialiseExamples.lean 122;
  - seed_bugs.py 128 (35 plants), check_statements.py 18, the allow file 9;
  - docs about 150;
  - registries 40.

  This is at the common rule's cap and above the task's 300-500 estimate. The excess is the fixtures and plants that
  the self-review and the trust-mutants survivors asked for.
- **In-flight overlap**, checked at the start against every `feature/*`, `lean-first/*`, `infra/*` and
  `foundation/*` branch with `git diff --name-only main...<branch>`. No branch touches `lean/VE/Acts/Specialise*`.
  The shared registries do overlap:
  - `feature/ci-3b` and `feature/et-5` edit `tools/layer_policy.py`, in other hunks;
  - `feature/ci-3b`, `feature/sc-7` and `foundation/me-1` add other imports to `lean/VE.lean`;
  - seven branches edit `tools/trust-classes.json`, in other modules' entries.

  These are append-style lines the task names as this item's files.

## 6. Next items

- ap-5b: design and review of the base-level bridge (`act-specialise@0`). It covers AP-5b's obligations (a)-(c) and
  spec section 8's last paragraph, and carries the wire key `restrictive`, `decodeRestrictive` and the IDE question.
- Then ap-6 (the D6 experiment, after ap-4).

Pilot bytes this item is expected to move: 0 (plan section 0's table). This is an estimate: nothing uses the generator
until AP-5b.

## 7. Deviations (recorded here, not in the copied plan)

1. **`specPremises`' body.** Section 8 gives only its signature and docstring. A predicate is read through
   `declaredOnce`, so a name declared twice (in either order) or not at all gives no premise (guards 111-113).
   Reason: `specPremises_plain` has no well-formedness hypothesis (C21). Each name is looked up once.
2. **"`a ≠ b`"** is read as "the two atoms differ". So two predicates with one act give no premise (guard 104), and
   no premise runs from an act to itself.
3. **Layer, against the task's wording** ("the new modules in the layer of `VE.Acts.Readings`"). Only
   `VE.Acts.Specialise` joins that layer-2 set in `tools/layer_policy.py`. `VE.Acts.SpecialiseExamples` stays at the
   default layer 3 of `VE.Acts.*`, as `MeaningExamples` and `ReadingsExamples` do. It imports `MeaningExamples`
   (layer 3) for `toks`, so layer 2 would be an upward import (`tools/test_layer_policy.py` passes).
4. **Proof helpers** in `Specialise.lean`: `declaredOnce_mem`, `mem_specPremises`, `preds_bindAll`, `mem_preds_atom`.
5. **Two fixture atoms are built by hand,** not by `analyse`: `b` with *be*, and `fromOnly` (*seek from persecution*,
   with no object, which `Vsp`'s frame does not read). Every other act is `analyse`'s, pinned by guards 41-45.

## 8. Self-review against BUILDER-CHECKLIST

Spec re-read:
- `Restrictive`, `Modifier.restrictive`, `specialises` and the four statements against `docs/spec/act-phrases.md:1438-1464`
  (check_statements.py);
- `specPremises`' conditions against the docstring at `:1456`, plan 2.6 (`act-phrases-PLAN.md:354-372`) and D5 (`:168`);
- the fixtures against 11.5 (`:1815-1820`).

1. Typed and contained answers: N.A., since no route, relay or response changes.
2. Deliverables: PASS. Every plan and task row is in section 3, with "not in this item" as the task lists it;
   `git diff --name-only main...HEAD | grep -E "^(ve|rust|tests)/"` finds nothing.
3. Tests can fail: PASS. mutants.json (35 KILLED, with a control build); trust-mutants.json exits 0.
4. Python, Lean and Rust agree: N.A., since only Lean changed and nothing is called.
5. R8 binding: N.A., since nothing is relayed.
6. Gate evidence on the final HEAD: PASS. The chain runs the gate; the selected run is on committed code (section 9).
7. No unsigned item: PASS. DELTA has no rows; the trust growth cites R16 with its conditions met (section 5).
8. DELTA: PASS. There is no user-visible change, because no route reaches the new modules (DELTA.md).
9. Test selection: PASS. `tools/select_tests.py` selects 459 of 561 test files because of the Lean library change
   (the Lean-dependent tests), not every unit. `tools/test_layer_policy.py` is in the selection.
10. Lean statements: PASS. check_statements.py prints 10 of 10 verbatim; seed_bugs.py's plants with the theorems cut
    show the guards, not the proofs, catch each one.
11. Budgets fail closed: N.A., since no budgeted operation is added (`specPremises` reads no budget; no route
    exposes it).
12. CPU and memory: N.A. for routes. The evaluator rule applies once AP-5b exposes `specPremises`: it looks up each
    name once and is quadratic in `acts`; ap-5b charges it.
13. Test-removed trailers: N.A., since no test is removed.
14. Both directions and cited evidence: PASS. Each check has an accept and a refuse guard (for example 51 against 52;
    56; 60; 72; 93 against 100-113), and each claim here names its command.
15. Overclaims, cuts, failing checks and limits: PASS. The docstring was reworded after self-review C1; no
    deliverable was cut; every guard is in mutants.json; limits are N.A. (nothing is exposed).

SELF-REVIEW: 0 A, 2 B, 8 C; fixed 10. B1: fixtures with two-element lists in both orders. B2: the FOLLOW-UPS row.
The C findings: docstring, equal-length sorts, plain-first duplicate, control build, saved statement script,
`DuplicateDeclaration` cite, overlap record, and the lookup done once.

## 9. Selected tests and gate

`MAC_PYTEST_NO_DEFER=1 zsh /home/seyran/code/manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main)
--run` on committed HEAD d356aa22 (tree clean) ran on ve-mac-1 in 2758 s and exited 0. Besides the Lean build,
`lean/audit.py`, the Rust build and `tools/test_layer_policy.py`, it ran 475 units with 0 failed, and the log ends
`failed/error ids=0`. No test failed, so none from main-known-red.txt came up. Only this section changed after that
run (docs only). The full gate runs in the chain on the final HEAD.
