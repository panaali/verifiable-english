# Gaps

Ranked by (frequency in this document) × (importance to the clause's meaning).

## 1. Obligation / prohibition (deontic modality) — occurs 3 times, very high importance

**Smallest example:** "No State shall make or enforce any law which shall
abridge the privileges or immunities of citizens of the United States."

**Why v0 cannot express it faithfully.** All three prohibitions in Section 1
("No State shall...", "nor shall any State...", "nor deny...") are legal
commands: they make a class of state action *invalid* or *unconstitutional*,
not merely factually rare. v0 has no modal operator, so `claims.ve` reifies
each prohibition as a plain universal negative — `for every state x, for
every law y, for every citizen z, if (P), then not (Q)`. That formula is true
in exactly the models where no state ever actually does the forbidden thing;
it is equally true in a world where states are legally free to abridge
privileges/immunities but simply choose not to, and in the real constitutional
world where such a law would be struck down as void. The two situations are
extensionally identical to a `check`/`evaluate` run but normatively opposite.
v0's own grammar anticipates this gap: `must` is already a reserved
identifier (`docs/spec/v0-language.md`, surface grammar) with no defined
semantics yet.

**Proposed surface syntax:** a deontic operator on a formula, e.g.
`it is prohibited that (A)` / `it is obligatory that (A)` / `it is permitted
that (A)`, parallel to `not (A)`. For this document specifically:
`it is prohibited that ((x0 makes_law x1) and (x1 abridges_priv_or_imm x2)).`

**Semantics sketch:** a deontic accessibility relation over admissible
structures — `S ⊨ prohibited(A)` iff for every structure `S'` reachable from
`S` under the "legally permissible" relation, `S' ⊭ A` — or, more simply for a
first pass, a distinguished unary "valid law" predicate plus an axiom
"`abridges_priv_or_imm(l,p) → not valid_law(l)`", making unconstitutionality
an explicit, checkable consequence rather than folding it into the same
extensional layer as ordinary facts. Either design needs a proof-theoretic
treatment (soundness w.r.t. some deontic logic) before it can be a checked
v0.1 profile, analogous to how `closure@0` needed its own fixed-point and Lean
soundness proofs.

**Rendering across views (sketch, `it is prohibited that (A)`):**

| View | Sketch |
|---|---|
| `fol_symbols` | `O¬(A)` or a dedicated `Prohibited(A)` |
| `fol_keywords` | `prohibited (A)` |
| `ve_strict` | `it is prohibited that (A)` |
| `ve_natural` | `it is prohibited that (A)` |
| `ve_fluent` | `A must not happen` / `S1 must not (verbalised A)` |

## 2. Definitions / open-textured legal standards — occurs 3 times, very high importance

**Smallest example:** "...abridge the privileges or immunities of citizens of
the United States" (also: "due process of law," "the equal protection of the
laws").

**Why v0 cannot express it faithfully.** These are not vague in the sense of
fuzzy predicates ("tall"); they are legal terms of art whose content is fixed
by an external, evolving body of case law and is not stateable as a
first-order closed formula over `person`/`state`/`law` at all — it involves
weighing government interests, historical practice, and precedent. `claims.ve`
had to name a single opaque predicate (`abridges_priv_or_imm`,
`affords_due_process`, `denies_equal_protection`) for each. That is an honest
OPAQUE label (see coverage.md), not a defect fixable by better v0 syntax; even
a hypothetical v1 with definitions would only push the problem one level down
to *defining* those predicates, which is exactly the unsettled legal question.
This is closer to "definitions" and "vagueness" from the brief's example gap
list than to a missing logical connective.

**Proposed direction, not a full fix:** a `definition` construct that lets a
vocabulary entry cite the specific doctrinal test it stands for (e.g. "strict
scrutiny: predicate is true iff no `compelling_interest` and `narrowly_tailored`
tuple exists for this law") would at least make the *current* legal test
checkable given further opaque facts about compelling interests, without
resolving whether that test is the right one. This does not remove the
opacity; it relocates and documents it, which is itself valuable for honesty.

## 3. Functions / definite descriptions — occurs 1 time, moderate importance

**Smallest example:** "...are citizens ... of the State **wherein they
reside**."

**Why v0 cannot express it faithfully.** v0 is function-free; "the State
wherein X resides" is a definite description presupposing a function
`residence : person → state`. `claims.ve` reifies it as a relation
`resides_in(person, state)` with no uniqueness constraint, so nothing stops a
model from giving one person two states of residence, silently weakening the
clause (a person could then be a "citizen of the State" in two states at
once, which the source clearly does not intend).

**Proposed surface syntax:** either (a) a general function-symbol extension
(`Fun(f, t)` terms, à la `order@0`'s `Add`/`Scale`), or (b) a lighter
"functional relation" declaration in the vocabulary schema
(`"resides_in": {"functional": true}`) that the checker enforces on submitted
models as an extra well-formedness condition, without adding function terms
to the term grammar.

**Semantics sketch:** for (b), `asStructure(M)` would additionally require,
for each functional binary predicate `r : (s1, s2)`, that for every `a : s1`
there is at most one `b : s2` with `r(a,b)` — a model-validity check, not a
new formula constructor.

**Rendering:** unaffected for (b) (same binary-predicate surface); for (a),
`ve_fluent` would read "the state that P resides in" instead of introducing a
second bound variable.

## Summary

| Gap | Occurrences in this document | Importance |
|---|---:|---|
| 1. Deontic modality (obligation/prohibition) | 3 | Very high — this is the entire normative force of Section 1's last two clauses |
| 2. Open-textured legal definitions | 3 | Very high — this is what the clauses are actually litigated about |
| 3. Functions / definite descriptions | 1 | Moderate — affects only "the State wherein they reside" |

No arithmetic, counting, n-ary relations, time/tense, attribution/quotation,
belief/intent, causation, generics, or questions/imperatives are needed by
this document; the source has none of them within Section 1.
