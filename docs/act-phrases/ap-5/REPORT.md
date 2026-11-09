# ap-5 report: specialisation, definitions and generator only

**Summary.** Status: built; selected tests and the chain gate are recorded in section 9. What changed: new
`lean/VE/Acts/Specialise.lean` (`Restrictive`, `Modifier.restrictive`, `specialises`, `specPremises`, and spec 8's
four statements, proved with no `sorry`) and `lean/VE/Acts/SpecialiseExamples.lean` (spec 11.5's fixtures and one guard
per seeded bug), registered in `lean/VE.lean`, `tools/layer_policy.py` and `tools/trust-classes.json`. Open items: none
in this item; AP-5b (the base-level bridge) is next. DRI signature needed: none (trust growth under R16, section 5).

## 1. Statement gate

The spec's statement review (debates/act-phrases-spec/, applied in plan draft 3) accepted section 8, including the
C21 restatement of `specPremises_plain` without its free `p` (`docs/spec/act-phrases.md:1919`). Each definition and
statement of section 8 is in `Specialise.lean` unchanged after whitespace normalisation: a script that splits
section 8's Lean block (`docs/spec/act-phrases.md:1438-1465`) at each `structure`, `def`, `theorem` and docstring and
looks for each whitespace-normalised item in the normalised source printed `OK` for all 10 items. `specPremises` has
only a signature and a docstring in section 8; its body is this item's (section 2).

## 2. Design

- `specialises` is section 8's text. `specialises_refl` and `specialises_trans` are proved over `List.contains` and
  `List.filter` (trans: an extra argument or modifier of `a` over `c` is either extra over `b`, restrictive by `a ⊑ b`,
  or in `b` and extra over `c`, restrictive by `b ⊑ c`).
- `specPremises E ρ acts` takes every ordered pair `(pa, a)`, `(pb, b)` of `acts`, in `acts` order, and emits
  `bindAll ra.sorts (.implies (atom ra.name ra.sorts) (atom rb.name ra.sorts))` exactly when `pa` and `pb` each have
  one regulated declaration `ra`, `rb` (`declaredOnce`), `ra.role` is not `.plain`, `ra.role = rb.role`,
  `ra.sorts = rb.sorts`, `a ≠ b` and `specialises ρ a b`. `bindAll` and `atom` are the norms layer's
  (`VE.Norms.Basic`), so a premise is `∀x:s. pa(x) → pb(x)`, or `∀x:s. ∀y:t. pa(x, y) → pb(x, y)` for two sorts.
- `declaredOnce` (one declaration of the name, else none) is what makes `specPremises_plain` true without a
  well-formedness hypothesis (C21 states it without one): a plain `r` whose name is `ra.name` is `ra` itself, which is
  not plain, and likewise for `rb`, whose role is `ra`'s. Under `WellFormed` names are unique anyway
  (`DuplicateDeclaration`), so on a well-formed document it is the plain lookup.
- `specPremises_typed` reads `Valid` (`VE.Norms.valid_of_wellFormed`): each regulated predicate is declared in `E.E`
  with its sorts, of arity 1 or 2, over declared sorts; then `atom_wellFormed`, `bindAll_wellFormed` and
  `check_iff_wellFormed` give `φ.check E.E [] = true`.
- No hook: AP-5 is not a premise pack and has no Background hook. A carried premise over a regulated predicate is
  refused (`lean/VE/Readings/SupExtra.lean:14-19`), which is why using these premises waits for AP-5b's bridge over
  base predicates.

## 3. Plan rows delivered and not delivered

| Plan or task row | Delivered by |
|---|---|
| AP-5 goal: `specialises` over the declared restrictive markers and modifiers, and `specPremises`, as Lean definitions with proved properties | `lean/VE/Acts/Specialise.lean` (commit "ap-5: specialises and specPremises ...") |
| New file `Specialise.lean` (`specialises`, `specialises_refl`, `specialises_trans`, `specPremises`, `specPremises_typed`, `specPremises_plain`) | same; all four proved, no `sorry`; `python3 lean/audit.py` (section 5) |
| `SpecialiseExamples.lean`, with `#guard`s on the generator | `lean/VE/Acts/SpecialiseExamples.lean`, built by `lake build VE.Acts.SpecialiseExamples` |
| 11.5: `specialises ⟨["in"], []⟩ a b = true`, `specialises ⟨[], []⟩ a b = false`, `specialises ⟨["in"], []⟩ b a = false` | `SpecialiseExamples.lean:37-39`; `a`, `b` built by `analyse` (`act`, line 20), their atoms pinned at lines 30-31 |
| 11.5: two permission predicates give one premise `∀ x. pa x → pb x`; two plain none; two obligation one | lines 63-64, 67, 65 |
| Task extras: undeclared "nearly" false; a different head false; `a = b` no premise; different sorts no premise | lines 41, 43, 71, 73 |
| Shared files: none | only the registries the task names: `lean/VE.lean`, `tools/layer_policy.py`, `tools/trust-classes.json` |
| Moves: nothing until AP-5b | no route, request, answer, pack, profile or Python change (`git diff --stat` of the merge base) |

Not in this item (all wait for AP-5b): the wire key `restrictive` and `VE.Acts.Wire.decodeRestrictive` (spec 1.9 and
the wire table's row "AP-5 (used only under `act-specialise@0`, after AP-5b)"), the IDE question, any Background hook,
pack or profile. So no route, request or answer changes and no Python changes. AP-5b's tests (the conflict fixture,
"may a person seek asylum?") and its seeded bug moved to AP-5b in the plan itself.

## 4. Seeded bugs and mutants

`python3 docs/act-phrases/ap-5/seed_bugs.py` plants each in `Specialise.lean` with its theorems cut (so a fixture
catches it, not a proof), builds `VE.Acts.SpecialiseExamples`, records the failing `#guard` lines and restores the file;
its output is [mutants.json](mutants.json): 17 mutants, 17 KILLED, restored build exit 0. Line numbers are
`SpecialiseExamples.lean`'s.

The task's four seeded bugs (Lean):

| Bug | Guard that fails |
|---|---|
| `specialises` without the restrictive test on extra modifiers | 41 (the "nearly" guard), also 38, 40, 42, 75 |
| `specialises` without `a.head == b.head` | 43 (the different-head guard) |
| `specPremises` reversing the premise to `p_b → p_a` | 63 (the one-premise guard with its exact formula), also 64, 65, 80 |
| `specPremises` emitting a premise for plain entitlements | 67 (the plain guard) |

One mutant per new trusted definition (common rules): `Restrictive` (fields swapped: 37, 40, ...), `Modifier.restrictive`
(an adverb always restrictive: 41, 42; a marker read among the adverbs: 37, 40, ...), `specialises` (also without *to*
44, *be* 45, the argument subset 47, the modifier subset 39, the restrictive test on extra arguments 46),
`declaredOnce` (the first of two declarations read: 77), `specPremises` (also two roles 69, unequal sorts 73, `a = b`
63-80, no `specialises` test 63-65, 75, 80). No language other than Lean changed.

## 5. Trust, size, tests and checks

TRUST-NUMBERS

## 6. Next items

- ap-5b: design and review of the base-level bridge (`act-specialise@0`), AP-5b's obligations (a)-(c), spec section
  8's last paragraph; it also carries the wire key `restrictive`, `decodeRestrictive` and the IDE question.
- Then ap-6 (D6 experiment, after ap-4).

Pilot bytes this item is expected to move: 0 (plan section 0's table; nothing uses the generator until AP-5b).

## 7. Deviations from the plan and the spec (recorded here, not in the copied plan)

1. `specPremises`' body (section 8 gives the signature and docstring): a predicate is read through `declaredOnce`, so a
   name declared twice or not at all gives no premise (guards 77, 78). Reason: `specPremises_plain` has no
   well-formedness hypothesis (C21).
2. "`a ≠ b`" is read as the two atoms differ (`pa.2 != pb.2`), so two predicates with one act give no premise
   (guard 71), and no premise runs from an act to itself.
3. Layer: `VE.Acts.Specialise` joins `VE.Acts.Readings`' layer-2 set in `tools/layer_policy.py`.
   `VE.Acts.SpecialiseExamples` stays at the default layer 3 of `VE.Acts.*`, as `VE.Acts.MeaningExamples` and
   `VE.Acts.ReadingsExamples` do: it imports `MeaningExamples` (layer 3) for `toks`, so layer 2 would be an upward
   import.
4. Proof helpers in `Specialise.lean` (class P by kind): `declaredOnce_mem`, `mem_specPremises`, `preds_bindAll`,
   `mem_preds_atom`.

## 8. Self-review against BUILDER-CHECKLIST

SELF-REVIEW-LINES

## 9. Selected tests and gate

SELECTED-TESTS
