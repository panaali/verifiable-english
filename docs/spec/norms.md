# W1: norms (`norms@0`): obligations, prohibitions, permissions, exceptions and priorities

> Status: W1 specification, draft 2 (2026-09-26), revised after both Astra + Fable FIX FIRST reviews required by
> [PLAN-EXPAND2.md](../../PLAN-EXPAND2.md) rule 10 and binding decision 9.3 before any Lean work in `lean/VE/Norms/*`
> starts. It applies the W1 section of PLAN-EXPAND2 v3 and the converged change list of
> `~/code/manage-agents/debates/expand2-v2/` (items 2, 5 and 6) to the P0 contracts now in the tree
> (`lean/VE/Route/*`, `ve/background.py`, `ve/profiles.py`, `docs/P0-Lean-NOTES.md`, `docs/P0-Py-NOTES.md`,
> `docs/P0-INTEGRATION.md`). Sections 4 to 7 are the statements under review; section 13 lists every point where this
> draft chose between readings of the plan; sections 15 to 17 record contract status, review responses and changes.
> The theorem statements and regression gates below are implementation obligations, not claims of completed proofs
> or tests. The goal of record is [VISION.md](../../VISION.md), whose lead principle
> (zero-training English) governs section 2.

## 0. Scope, one paragraph

A norm document says, in English, what is required, forbidden and permitted in a situation, with named exceptions
and priorities. The checker (unchanged) decides two things: what the rules require in a given situation, and whether
the rules can ever contradict each other, with a witness situation when they can. Norms elaborate into first-order
premises through one layer per regulated predicate on the P0 route; the elaboration is Lean-proved faithful to a
direct Catala-style semantics; conflict-freedom is exactly unique expansion over base structures, with local
expansion furnishing the `expands` field of the P0 `Layer`.
Everything else (defeasible weighing, "generally", "should", holistic priority) is outside: it becomes an open term,
a hedged unit or a reading set (W2), never a silently strict rule.

Out of scope this round: obligations whose object is existential ("must file some report" is written with the
object inside the act phrase, section 2.4), deadlines and fulfilment over time (W6 and stage 3), cross-predicate
"precedence" (section 2.3), norms over `$int` guards (order@0 documents can carry norms, but their conflict check
is outside the fragment of section 7), and any notion of "more important than".

## 1. What a norm document is

```text
regulated predicate p   := a vocabulary predicate with a `regulated` declaration (section 3.1): role
                           (permission | obligation | plain), a completion default (deny | allow), for an
                           obligation its permission dual whenever that act has both roles (3.1), and an act phrase
situation variables x̄   := the arguments of p, in declared order, one per sort slot; every rule on p quantifies
                           universally over exactly x̄
rule N (a norm unit)    := stable name; regulated predicate p_N; sign (p(x̄) or ¬p(x̄)); guard G_N(x̄); carve-outs
                           U_N = [U_1(x̄), ..., U_m(x̄)] ("unless"); parents ("takes precedence over"): rules on
                           the same p of which N is an exception; the display number is document order
precedence              := a DAG over rule names (a rule may take precedence over several rules); Python
                           `ve.background.dependency_order` and Lean `VE.Route.dependencyOrder` reject a cycle
                           with the shared `DependencyCycle:` diagnostic
stratification          := one dependency DAG over defined ∪ regulated predicates (PLAN-EXPAND2 3.5): a guard or
                           carve-out of a rule on p mentions regulated predicates strictly below p only; a
                           definition may sit above norms (`violation`) or below them (used in guards)
document                := the norm units of a `ve-document@1` (W2) or of a standalone `.norms.ve` file; the
                           regulated declarations live in the environment and are identity-bound
```

The checker sees: `Background(env)` (which for `norms@0` includes the profile premise of every declared dual pair)
++ the layer premises in DAG order (definitions and norm elaborations interleaved as the DAG orders them) ++ the
document's own premises. Nothing on the wire supplies an elaboration; Python and Lean regenerate it from the
decoded units and declarations (rule 5 of the plan applied to layer premises, section 11.3).

## 2. The English (VISION.md lead principle)

Every wording below has exactly one reading. The reading is stated as a sentence a non-expert can check against
the example situation the IDE shows; the formal meaning is in section 4. A wording that is not in this table is not
a norm wording: "should", "ought", "generally", "normally", "usually", "is expected to", "is entitled to",
"may" in the sense of "might" and "is more important than" are rejected with the rewrite suggestions of 2.6.

### 2.1 Rule blocks

A norm is written as a numbered rule block. Numbers are display only (document order); identity uses the stable
rule name (section 11.2), and renumbering alone changes no rule identity. There are no inline `unless` chains across
sentences: one rule, one block. The editor preserves names in block metadata; an English export that promises
identity preservation includes that metadata (11.2). Bare English alone cannot recover arbitrary hidden names.

```text
Rule 3. Every state must not deprive each person of life, liberty or property, unless that state affords that
person due process of law.

Rule 4 (exception to rule 3). Every state may deprive each person of life, liberty or property, if that person has
been convicted of a crime by a court of that state.

Rule 7 (exception to rules 2 and 5). ...
```

| Wording | The one reading | Formal effect (section 4) |
|---|---|---|
| `Rule n.` | Begins a rule. `n` is its position among the document's rules. | a node of the tree; display number only |
| `Rule n (exception to rule m).` / `(exception to rules m and k)` | Rule `n` can decide even where rule `m`'s guard fails: it has its own guard. When `n` or a descendant decides, `m` (and `k`) cannot decide. Rules `m`, `k` must regulate the same predicate. | `n` is a child of `m` (and `k`) in the precedence DAG; no inherited guard |
| `Rule n takes precedence over rule m.` (a sentence on its own) | Same as the header form; accepted on input, rendered as the header form. | same |
| `Every <noun> ... must <act>.` | In every situation of the described kind, the act is required. | consequence `required_act(x̄)` (obligation role, positive) |
| `Every <noun> ... must not <act>.` | In every situation of the described kind, the act is not permitted (forbidden). | consequence `¬permitted_act(x̄)` (permission role, negative) |
| `Every <noun> ... may <act>.` | In every situation of the described kind, the act is permitted. "May" never means "might". | consequence `permitted_act(x̄)` (permission role, positive) |
| `Every <noun> ... need not <act>.` | In every situation of the described kind, the act is not required. | consequence `¬required_act(x̄)` (obligation role, negative) |
| `..., if <condition>.` | The rule applies only in situations where the condition holds. | guard `G_N` |
| `..., unless <condition>.` / a following sentence `Except when <condition>.` | The rule does not apply in situations where the condition holds; whatever the other rules and the default say then decides. A carve-out never states a consequence of its own. | carve-out `U ∈ U_N`: `applies_N := G_N ∧ ¬⋁U` |
| `By default, a <noun> must not <act>.` (environment legend, section 3.1) | When no rule decides, the act is not permitted. | permission, deny-by-default |
| `By default, a <noun> may <act>.` | When no rule decides, the act is permitted. | permission, allow-by-default |
| `By default, a <noun> need not <act>.` | When no rule decides, the act is not required. | obligation, deny-by-default |
| `By default, a <noun> must <act>.` | When no rule decides, the act is required. | obligation, allow-by-default |

Input synonyms (accepted, rendered canonically, shown in the paraphrase): `No <noun> may <act>` for `Every <noun>
must not <act>`; `any` for `each` in object position (2.4); `except when` for `unless` inside a sentence.
Object-position `every` is rejected with a rewrite to `each`: under `must not`, it invites the reading "not every".
There are no other synonyms. Canonical rendering: one carve-out renders inline as `unless`; two or more render
as separate `Except when ...` sentences in the block, in document order.

### 2.2 Situations, subjects and objects

The subject `Every <noun>` binds the first situation variable. Further situation variables are bound in object
positions by `each <noun> [that <guard-relative>]`, with the existing English reference forms (`that state`,
`the first person`, `the second person`, labels) for later mention. All situation variables are universal: a
rule speaks about every situation of the described kind. `a <noun>` in an object slot is not a binder; it is
part of a declared act phrase (2.4). This is where English "must file a report" (some report) and "must file each
report" (every report) come apart, and the IDE says so (2.6).

Guards and carve-outs are ordinary VE formulas in the existing English surface (`docs/english-surface.md`) over
the situation variables, with two additions: a regulated predicate below `p` may be mentioned with its deontic
wording (`if that employee may enter the building`), and defined predicates (W3) with theirs. Within a guard the
negation of a deontic atom uses the standard negation wording (`it is not the case that that employee may enter
the building`); `must not`, `need not` are consequence wordings only, so every deontic phrase has one position
and one reading.

### 2.3 Precedence is nesting, not weight

`Rule 5 takes precedence over rule 2` means: when rule 5's subtree yields, rule 2 does not decide. Rule 5 has its
own guard and can decide where rule 2's guard fails; an exception does not inherit its parents' guards. It does
not mean that rule 5 matters more, and both rules must regulate the same predicate. A document that wants
"safety rules before helpfulness rules" writes the lower rules' outcomes into the higher rules' guards ("Rule 9.
Every assistant may help with each request, if it is not the case that that assistant must refuse that request."),
which the stratification of section 4.1 orders. The IDE offers exactly this rewrite when an author writes
precedence across predicates (diagnostic `PrecedenceAcrossPredicates`, section 11.1).

### 2.4 Act phrases and the four wordings

A regulated predicate declares an act phrase, a bare verb phrase with one slot per argument: `"{0} enforce
{1}"`, `"{0} file a report"`, `"{0} follow {1}"`. The profile derives the wordings from role and sign:

| Role | positive consequence | negative consequence | guard atom | default sentence |
|---|---|---|---|---|
| permission | `S may enforce L` | `S must not enforce L` | `S may enforce L` | `By default, a state may / must not enforce a law.` |
| obligation | `S must enforce L` | `S need not enforce L` | `S must enforce L` | `By default, a state must / need not enforce a law.` |
| plain | the predicate's `verbalisation` | its `negative_verbalisation` or the standard negation | `verbalisation` | `By default, <verbalisation with generic slots>.` / `By default, it is not the case that ...` |

Plain regulated predicates (Cedar's `permitted(request)` is a permission predicate; the constitution pilot's
`follow(situation, property)` is an obligation predicate; a plain one is, for example, Gatekeeper's `admitted(object)`)
keep the ordinary predicate templates. The act phrase passes the existing template linter (finite word grammar,
80 characters, no reserved words) and the P0 per-input all-derivations check on every fixture; W7 registers the
productions (2.7).

### 2.5 The reader's checklist (what the IDE shows on accept)

For every accepted rule the assistant (W8) shows, in English only: the deterministic paraphrase; an example
situation in which the rule decides; an example situation in which it does not decide (its guard fails, a carve-out
holds, or an exception decides instead); and the rejected readings with a distinguishing situation. For a document
it shows the default sentence of every regulated predicate and the conflict status of section 5 with the witness
situation rendered as "Rule 3 applies; its exception 4 does not; rule 6 also applies; rule 3 forbids and rule 6
permits".

Every carve-out paraphrase names the actual default from the environment legend, even when other rules might
decide: for a deny-default permission, "When this condition holds, this rule is silent; other rules may decide;
if none does, entry is not permitted by default." The default is never left implicit in "the default decides".
For precedence, the IDE also shows: rule 1 forbids ward entry on Mondays; rule 2, an exception to rule 1, permits
entry for on-call doctors. An on-call doctor may enter on Tuesday under rule 2 even though rule 1's guard fails.
If the author means only Mondays, the rewrite adds "and it is Monday" to rule 2's own guard.

### 2.6 How the IDE resolves ambiguity, in English

The one-reading guarantee is mechanical (P0 3.2: every English input runs the all-derivations parser; two
derivations reject). What the IDE adds is the English explanation and the rewrite. The cases the norm surface
must handle, each with the paraphrases the IDE shows:

| The author wrote | Competing readings shown as paraphrases with an example situation | Rewrites offered |
|---|---|---|
| `Every employee must file a report.` and no act phrase `file a report` is declared | (a) "For every employee and every report, the employee must file that report" (a report is a second situation variable); (b) "Every employee must file some report" (the report is inside the act) | declare the act phrase `{0} file a report` (reading b); or write `each report` and declare `{0} file {1}` (reading a) |
| `Every state must not deprive each person of liberty unless that state affords that person due process, in which case it may.` | (a) carve-out: with due process, rule 3 is silent; with no other deciding rule and the stated default `By default, a state must not deprive a person of liberty`, deprivation remains forbidden; (b) exception rule: with due process, a rule permits deprivation | keep `unless` (a); or `Rule 4 (exception to rule 3). Every state may deprive each person of liberty, if that state affords that person due process.` (b). With that deny default and no third rule, (a) forbids and (b) permits. With an independent forbidding rule, (b) is a conflict (10.1(i)) |
| `Claude should generally prioritize safety.` | not a norm wording | `must` (a strict rule, reading A of the pilot in 9.2); or a hedged unit `hedged(generally, norm)` (W2), or an open term for the weighing (9.2) |
| `Rule 5 is more important than rule 2.` | not a norm wording | `Rule 5 (exception to rule 2).` when both regulate the same predicate; else the guard rewrite of 2.3 |
| `A doctor may enter the ward.` | (a) permission for every doctor; (b) "might"; the supplied wording is not admitted | rewrite (a) as `Every doctor may enter the ward.`; the paraphrase says "is permitted to"; (b) is outside norm wordings |
| `Rule 6 (exception to rule 5). Every doctor must not enter the ward, unless that doctor is on call.` where rule 5 permits entering and the default forbids entry | one reading; for a doctor on call on Monday, rule 6 does not apply, so rule 5 permits entry. The stated default is `By default, a doctor must not enter the ward`; it decides only if no rule does | none needed; the situation is the check the author wanted |

The IDE never shows logic. The distinguishing situation is a checked finite model rendered in document terms (W8
de-elaboration: "state Texas, law L1: L1 abridges the privileges of citizen Ann; rule 2 applies").

### 2.7 Registration

`ve/surface/norms.py` registers one `SurfaceRecord` per construct with `profiles=("norms@0",)`: the rule block
(`wire_tag "norm"`, keywords `Rule `, statement-initial), the standalone precedence sentence (`Rule ` again, so
the parser hook disambiguates on the following tokens within one keyword record), the default sentence
(`By default, `), and the deontic atom forms for guards (rendered by the act-phrase renderer, parsed through the
existing template productions). Longest-match ordering and the duplicate-keyword refusal are P0's; `Rule ` and
`By default, ` conflict with no existing keyword (`ve/surface/registry.py`). Every fixture of section 10 is part
of the mixed English harness (W7) and of `tests/test_english_unambiguity.py`.

## 3. Declarations, wire form and strict form

### 3.1 Regulated declarations (environment, identity-bound)

```json
"predicates": {
  "enforce_permitted": {"arguments": ["state", "law"], "description": "...",
                        "regulated": {"role": "permission", "default": "allow", "act": "{0} enforce {1}"}},
  "enforce_required":  {"arguments": ["state", "law"], "description": "...",
                        "regulated": {"role": "obligation", "default": "deny", "act": "{0} enforce {1}",
                                      "permission": "enforce_permitted"}},
  "admitted":          {"arguments": ["object"], "description": "...", "verbalisation": "{0} is admitted",
                        "regulated": {"role": "plain", "default": "allow"}}
}
```

Rules: `default` is mandatory (no silent completion; a missing field is `InvalidInput`, never a default of
its own); `role` mandatory; `act` mandatory for permission and obligation roles and forbidden for plain; an
obligation's `permission` names a permission-role predicate with the same ordered argument sorts (`DualSortMismatch`
otherwise) and the same canonical act phrase (`DualActMismatch` otherwise). Act identity is the pair
`(ordered argument sorts, canonical act phrase)`; canonical means the linted template with whitespace normalised,
slots preserved in order, and no semantic synonym matching. At most one predicate per role may describe an act
(`DuplicateActRole`). If both obligation and permission roles describe that act, the obligation **must** name
that permission (`MissingPermissionDual` if absent); a link to another act is rejected even if its sorts match.
A dual may be absent only when no permission role for that act exists. Thus `must enter` and `must not enter`
cannot be declared independently to bypass the profile premise. Each permission predicate is named by at most
one obligation; `permission` is forbidden on other roles. A regulated predicate carries no W5 flag
(`functional`, `total`) and is not a W3 defined predicate (`RegulatedDefinedPredicate`); arity 1 or 2
today, up to 6 with `nary@0`; at most 64 regulated predicates per environment (`ResourceLimit`). The `regulated`
field (including its canonical act phrase) is part of the canonical environment bytes, so `environment_id`
changes when a default, role, dual or act phrase changes, and is unchanged for every existing environment
(no existing environment has the field).

`Background(env)`, generator `profile` (P0 hook table, `ve/background.py` slot `"profile"`): for every declared
pair `(r, m)` the premise `∀x̄. r(x̄) → m(x̄)`, in sorted order of `r`; `validate_background` rejects a finite
model whose table for `r` is not contained in its table for `m` with `InvalidModel("profile", ...)`. This is the
plan's fixed profile premise `∀a. required(a) → permitted(a)`, generalised to declared pairs of any argument
sorts; a document with no declared pair generates nothing.

### 3.2 Norm units (document content)

A norm is a unit of kind `norm` in `ve-document@1` (W2), content:

```json
{"norm": {"name": "no-deprivation", "predicate": "deprive_permitted", "sign": false,
          "guard": ["top"],
          "unless": [["binary", "affords_due_process", ["var", 1], ["var", 0]]],
          "over": []}}
```

`guard` and each `unless` entry are formulas in the P0 wire form over the context `[s_k, ..., s_1]` of the
predicate's argument sorts (de Bruijn: index 0 is the last argument, as for nested binders today; above,
`deprive_permitted(state, person)`, so `var 1` is the state and `var 0` the person); `over` lists
the stable names of the rules this rule takes precedence over; `name` is a token (`[a-z][a-z0-9-]*`, at most 64
bytes), unique in the document. The display number is the unit's position among norm units. A standalone
`.norms.ve` file is the same array of norm objects under an environment.

### 3.3 Strict text (the fallback of P0 3.2)

```text
rule no-deprivation: for every state x0, for every person x1, not (x0 deprive_permitted x1) unless (x0 affords_due_process x1).
rule convicted over no-deprivation: for every state x0, for every person x1, (x0 deprive_permitted x1) if (...).
```

Grammar (metavariables are not literal text; existing strict conventions for atoms, formulas and binders apply):

```ebnf
rule       = "rule ", name, [ " over ", name, { ", ", name } ], ": ", binders, ", ", literal,
             [ " if (", formula, ")" ], { " unless (", formula, ")" }, "." ;
binders    = "for every ", sort, " ", variable, { ", for every ", sort, " ", variable } ;
literal    = atom | "not (", atom, ")" ;   (* the atom's arguments are exactly the binders, in order *)
```

The consequence atom's arguments must be the binders in order, with no constant and no repetition
(`ConsequenceArguments` otherwise); a rule about a constant writes `if (x0 equals @view)`. The canonical printer
names binders `x0, x1, ...` as today; `print(parse(s)) = s` on canonical text; English and strict forms round
trip through the same AST with English's preserved name metadata (acceptance 10.6); strict text carries the
names itself and needs no such metadata.

## 4. Semantics

### 4.1 Well-formedness and the two DAGs

A norm document `T` over environment `E` is well-formed when:

1. every rule names a regulated predicate of `E`; rule names are unique (`DuplicateDeclaration: rule <name>`);
2. every name in `over` is a rule on the same predicate (`UnknownRule`, `PrecedenceAcrossPredicates`);
3. the precedence graph (edges `N → M` for `M ∈ over(N)`) is accepted by `dependencyOrder` over rule names
   (Python `dependency_order_nodes`, Lean `VE.Route.dependencyOrder`; `DependencyCycle: <sorted names>`);
4. every guard and carve-out of a rule on `p` is a well-formed formula over the context of `p`'s argument sorts
   and mentions, among defined and regulated predicates, only symbols strictly below `p` in the shared dependency
   DAG (P0 3.5: nodes are defined ∪ regulated predicates; an edge from a symbol to every defined or regulated
   symbol its body, guard or carve-out mentions after expansion; the graph is accepted by the same
   `dependencyOrder`). A guard of a `p`-rule that mentions `p` is a self-edge and is rejected as
   `DependencyCycle: p` (the plan's "if not p(x) then p(x)" case);
5. no guard or carve-out mentions a `$string` quantifier, an adapter predicate without a table, or a symbol of a
   profile the environment does not enable (ordinary type-checking).

The layer order of the route is the order returned by `dependencyOrder` over defined ∪ regulated predicates; the
precedence order within one predicate's rules is the order returned over rule names. Both are deterministic
(smallest ready name first) and identical in Python and Lean (P0's 200-graph differential test, extended to
generated norm documents in 10.10).

### 4.2 Applicability (Catala) and selection

For a rule `N` on `p` with situation variables `x̄`, over the symbols of the layer below `p`:

```text
applies_N(x̄) := G_N(x̄) ∧ ¬(U_1(x̄) ∨ ... ∨ U_m(x̄))                the rule applies: guard holds, no carve-out holds
yields_N(x̄)  := applies_N(x̄) ∨ ⋁_{E : N ∈ over(E)} yields_E(x̄)      N's subtree decides (Catala: the subtree yields a value)
selects_N(x̄) := applies_N(x̄) ∧ ¬⋁_{E : N ∈ over(E)} yields_E(x̄)     N itself decides: it applies and no exception subtree yields
P_p(x̄)       := ⋁_{N on p, sign +} selects_N(x̄)                      some rule decides p(x̄)
N_p(x̄)       := ⋁_{N on p, sign −} selects_N(x̄)                      some rule decides ¬p(x̄)
```

Recursion is on the precedence DAG (well-founded by 4.1(3); in Lean, fuel = number of rules). A carve-out is
part of `applies`, not a node: a rule whose carve-out holds does not itself apply or select. Its subtree can
still yield through an applicable descendant and block its parents. Only when no descendant yields is that
carved-out subtree silent (as in the doctor-on-Monday case of 2.6, which has no descendant). Two rules of the same
sign that both select at some `x̄` produce an overlap diagnostic `Overlap(N, N')` with an example situation,
never a conflict or a claim that either rule is logically redundant; this is the
stated deviation from Catala, where two applicable exceptions are an error whatever their values. Two rules of
opposite sign that both select are the intra-predicate conflict of section 5.

### 4.3 Completions and the direct semantics

Each regulated predicate has one completion, its declared default `d_p ∈ {⊥ (deny), ⊤ (allow)}`:

```text
O_p(x̄) := P_p(x̄)      if d_p = deny    (p holds exactly when some rule decides it)
O_p(x̄) := ¬N_p(x̄)     if d_p = allow   (p holds unless some rule decides against it)
```

`forbidden(x̄) := ¬permitted(x̄)` and `violation(x̄) := required(x̄) ∧ ¬done(x̄)` (and `breach(x̄) :=
¬permitted(x̄) ∧ done(x̄)`, with `done` the base predicate recording that the act happened) are W3 definitions
above the norms, never second regulated predicates: one completion per predicate, no dual to keep consistent.

The direct semantics (`holdsCatala`, statement review item 12.1) reads the tree as Catala does. For a structure
`S` over the symbols of the layer below `p` and a tuple `v̄` of the right sorts:

```text
Value_p(S, v̄) := some true     if P_p holds at v̄ and N_p does not
               | some false    if N_p holds at v̄ and P_p does not
               | some d_p      if neither holds
               | none          if both hold                           (Catala's conflict error)
Intended_p(T, S) := ∀ v̄ typed for p, ∃ b : Bool, Value_p(restrict S, v̄) = some b ∧ (S ⊨ p(v̄) ↔ b = true)
```

### 4.4 Elaboration (the layer premises)

```text
elab_p := ∀x̄. (P_p(x̄) → p(x̄)) ∧ (N_p(x̄) → ¬p(x̄)) ∧ ((¬P_p(x̄) ∧ ¬N_p(x̄)) → (p(x̄) ↔ d_p))
```

`elab_p` is one closed formula over `E_out = E_in + p`, executable from the decoded units (Python `ve/norms.py:
elaborate`, Lean `Norms.elab`), concatenated on the route in DAG order after `Background`. Two facts about it,
both theorems in section 6:

- `elaborate_iff`: `S ⊨ elab_p ↔ Intended_p(T, S)` on every structure admissible for `E_out`. In particular
  where both `P_p` and `N_p` hold, `elab_p` is false, exactly as the direct semantics has no value there.
- `elab_completion`: if `∀x̄. ¬(P_p(x̄) ∧ N_p(x̄))` holds in `S`, then `S ⊨ elab_p ↔ S ⊨ ∀x̄. p(x̄) ↔ O_p(x̄)`.
  So on conflict-free documents the elaboration is the completed-outcome biconditional the plan writes, and a
  reader may think of `p` as "defined by" `O_p`; on conflicting documents the biconditional would hide the
  conflict, which is why the three-clause form is the premise.

Rendering: the new norms admission path (11.4) shows `elab_p` under the label `layer:norms:<p>` in its own
extended label grammar; the frozen P0 parser is unchanged. `background:profile` covers the pair premise.
W8's de-elaboration renders the
premise back as the rule blocks it came from.

### 4.5 Outcome substitution

For the conflict check (and the fragment claim) the outcome formulas are pushed down to base symbols:

```text
φ°       := φ with every atom q(t̄), q regulated and below p, replaced by O_q°(t̄) (capture-avoiding), and every
            defined atom replaced by its expanded body (W3 `expand`); terminating by the shared DAG
E_base   := E minus its defined and regulated predicates (the vocabulary the author's situations are about)
base structure := a structure admissible for E_base satisfying Background_base := flags ++ literal distinctness
            (the definitions and the profile premise mention symbols outside E_base and are not part of it)
```

`subst_sound` (section 6): for an explicit DAG prefix, a formula well-formed over that prefix and a typed
valuation, on any structure satisfying that prefix's premises, `φ°` and `φ` agree. Hence the
check can be stated and witnessed over base structures, where a witness is a plain situation with no derived
tables, and the same formulas are what the fragment theorem measures.

## 5. The conflict check

### 5.1 The formula

```text
conflict_p(x̄)      := P_p°(x̄) ∧ N_p°(x̄)                                for every regulated p
conflict_(r,m)(x̄)  := O_r°(x̄) ∧ ¬O_m°(x̄)                              for every declared pair (r obligation, m permission)
conflict_T         := ∃x̄. conflict_p(x̄)  for some p, or ∃x̄. conflict_(r,m)(x̄) for some pair
```

evaluated over base structures, that is, without assuming the completions or the profile premise being tested
(debate item 5, Astra round 2 §3). The pair formula uses the completed outcomes, so it catches required-by-default
as well as a rule that selects `required`; both reviewer counterexamples are in 10.1.

### 5.2 Status, three-valued

| Status | Evidence | Where it is checked |
|---|---|---|
| CONFLICT-FREE | one accepted tableau certificate per `p` and per pair for `Background_base ⊢ ∀x̄. ¬conflict_p(x̄)` (respectively `¬conflict_(r,m)`), bound to the source `environment_id` and norm document hash by the new admission path (11.4) | Python replay, Lean `norms-route` wrapping the unchanged family's certificate checker over the regenerated `E_base` |
| CONFLICT | a checked witness: a valid finite base model `M` (Background_base validated) and a tuple `ā` typed in argument order, with `conflict_p` (or the pair formula) true under `tupleVal ā` by the finite evaluator; rendered as a situation (2.5) | Python search + evaluation, Lean `norms-route` wrapping the family's countermodel checker with conclusion `∀x̄. ¬conflict`, Rust evaluation of the supplied elaborated formula |
| UNKNOWN | neither within budget; the report names the budget (`MAX_EVALUATIONS`, the tableau budget, the search bound) | every site |

A document's status is CONFLICT if any `p` or pair has a witness; CONFLICT-FREE if every `p` and pair is
certified; UNKNOWN otherwise, with the per-predicate table shown. CONFLICT-FREE is never concluded from an
exhausted enumeration until section 7's theorem is proved and audited (binding decision 9.4); a checked witness
of any size is CONFLICT whether or not the document is in the fragment (Astra round 2 §4). The vacuity report
(P0 3.8) is separate and also shown: a CONFLICT document's elaborated premises are inconsistent with some base
facts, and any certificate depending on them at those facts is `vacuous`.

### 5.3 What CONFLICT-FREE means (the theorem, in words)

For every base structure (every situation the author's vocabulary can describe, with the declared flags and
literal distinctness), there is exactly one way to fill in every regulated predicate that satisfies all the
rules, their defaults and the profile premise, together with the uniquely determined defined predicates.
This is an iff for each base structure, including those with no full expansion; its universally quantified
form is the document-wide claim. Proof and countermodel results on the route then transfer to the
document's own vocabulary through the P0 route theorems: a certified conclusion over `E_base` holds in every
situation satisfying the premises, and every countermodel in the author's vocabulary expands to one the checker
sees. That is `Norms.conflictFree_expands_document` and `conflictFree_expands_all`, with
`conflictFree_expands` furnishing each P0 `Layer.expands`, plus `route_acceptance`,
`route_base`, `route_countermodel_expands` (`lean/VE/Route/Route.lean`).

## 6. Lean: definitions and the exact statements to prove

Files: `lean/VE/Norms/Tree.lean` (syntax, `WellFormed`, both DAG checks through `VE.Route.dependencyOrder`),
`Semantics.lean` (`Value`, `holdsCatala`), `Elaborate.lean` (`yields`, `selects`, `pos`, `neg`, `outcome`,
`elab`, `elaborate`), `Subst.lean` (`tupleVal`, prefix substitution), `Conflict.lean` (local and document-wide
expansion), `Layer.lean` (P0 instances and route theorems), `Wire.lean`, `Admission.lean`, `Run.lean` (11.4),
`SmallModel.lean` (7, gated), `Cedar.lean` (8), `Checks.lean` (executable audit guards), and `lean/NORMS.md`
listing each theorem in plain words. All frozen P0 contracts and `lean/VE/Route/*` sources remain unchanged.
The blocks below are statement schemata: helper names are defined here; they are not already implemented Lean.

### 6.1 Definitions, tuple convention and prefix satisfaction

```lean
namespace VE.Norms

structure Node where
  name      : String
  pred      : String
  sign      : Bool
  guard     : VE.Formula        -- context (sorts pred).reverse; otherwise closed
  carveOuts : List VE.Formula   -- same context
  over      : List String

inductive Role | permission | obligation | plain

structure Regulated where
  name           : String
  sorts          : List String
  allowByDefault : Bool
  role           : Role
  act            : Option String -- canonical act phrase; required except for plain
  permission     : Option String -- mandatory if this act has both roles (3.1)

structure Tree where
  regulated : List Regulated
  nodes     : List Node

/-- Declaration checks (3.1), 4.1, guard/carve-out typing, and both DAG checks. -/
def WellFormed (E : VE.Environment) (T : Tree) : Bool

/-- Relation tuples stay in declared argument order; formulas use de Bruijn valuation order. -/
def tupleVal {α : Type} (vs : List α) : List α := vs.reverse

def applies (T : Tree) (N : Node) : VE.Formula
def yields  (T : Tree) : Nat → Node → VE.Formula -- fuel = T.nodes.length
def selects (T : Tree) : Nat → Node → VE.Formula
def pos     (T : Tree) (p : String) : VE.Formula
def neg     (T : Tree) (p : String) : VE.Formula
def outcome (T : Tree) (p : String) : VE.Formula
def elab    (T : Tree) (p : String) : VE.Formula -- closed three-clause formula
def elaborate (E : VE.Environment) (T : Tree) : List VE.Formula
  -- norm elaborations in DAG order; layerPremises also interleaves W3 biconditionals

def Value (T : Tree) (p : String) (S : VE.Structure) (vs : List S.Carrier) : Option Bool
  -- direct rule recursion, evaluating each guard/carve-out under tupleVal vs
def IntendedAt (T : Tree) (p : String) (S : VE.Structure) : Prop :=
  ∀ vs, VE.TupleTyped S (sorts p) vs →
    ∃ b : Bool, Value T p (forget p S) vs = some b ∧ (S.relation p vs ↔ b = true)
def holdsCatala (E) (T) (S : VE.Structure) : Prop :=
  ∀ p ∈ regulatedNames T, IntendedAt T p S
```

Here and below `sorts p` is the declaration's argument-order signature, never its reversal. For binary
`p(state, person)`, relation tuple `[Texas, Ann]` becomes valuation `[Ann, Texas]`: guard
`r(var 1, var 0)` tests `r(Texas, Ann)`. This conversion applies to `Value`, `pos`, `neg`, `outcome`, local and
base conflict formulas, completion, finite witness evaluation and the small-model theorem. Closed formulas
use `[]`. General substitution uses its explicit typed valuation `ρ`, not another reversal. Prove
`tupleVal_typed`: `TupleTyped S ss vs → Valuation.Typed S ss.reverse (tupleVal vs)` (and the converse for
`vs.length = ss.length`). `Value` recurses on rules independently of the generated selection formulas, so
`elaborate_iff` expresses faithfulness to that direct semantics.

Fix the unique dependency order `q₁, …, qₙ` of **all** defined and regulated predicates. `E_i` contains the base
vocabulary plus the first `i` symbols; `before p` is the prefix length before `p` is introduced. All prefix
indices below satisfy `0 ≤ i ≤ n`. Define `PrefixPremises i` as the first `i` layer premises (W3 biconditionals
or norm elaborations) and every pair premise whose two members are in that prefix. `restrictTo i` forgets the
later symbols, preserving the carrier, domains, constants and all other relations. `restrictAll = restrictTo 0`.
These definitions do not require any `Layer` value or any conflict-free hypothesis.

```text
PrefixAdmissible 0 S := BaseAdmissible E S
PrefixAdmissible (i+1) S := S.Admissible E_(i+1)
  ∧ PrefixAdmissible i (forget q_(i+1) S)
  ∧ LayerMeaning_(i+1)(S)
  ∧ Sat S (pairPremisesClosedAt q_(i+1))

LayerMeaning_i(S) := IntendedAt T q_i S                       if q_i is regulated
                  | S ⊨ ∀x̄. q_i(x̄) ↔ definitionBody_i(x̄)    if q_i is defined
```

`Sat S as := ∀ a ∈ as, a.denote S []`; `BaseAdmissible` is structural admissibility over `E_base` plus
`Background_base`. Prove `prefix_satisfaction`: `PrefixAdmissible i S` iff `S.Admissible E_i`, its base
restriction is base-admissible, and `S` satisfies `PrefixPremises i`. The regulated step uses the local
`elaborate_iff`; the definition step uses W3's faithfulness theorem. Pair premises are closed at the later
member in the DAG order; they introduce no extra dependency edge.

**W3 interface requirement:** each definitions layer on this route must include its own biconditional **and**
the full input-prefix admissibility in `Admissible_out`. Structural admissibility alone, even with a correct
`expands` proof, does not ensure that an arbitrary intermediate input to a later layer satisfies lower
premises. This is an instantiation requirement on the unchanged P0 fields; `Examples.copyLayer` alone does
not supply this stronger prefix invariant.

```lean
/-- Substitute only defined/regulated symbols present in prefix i; recursively expand to base symbols. -/
def subst (E) (T) (i : Nat) : VE.Formula → VE.Formula
def outcomeBase (E) (T) (p) := subst E T (before p) (outcome T p)
def conflict (E) (T) (p) :=
  .and (subst E T (before p) (pos T p)) (subst E T (before p) (neg T p))
def pairConflict (E) (T) (r m) := .and (outcomeBase E T r) (.not (outcomeBase E T m))
def ConflictFree (E) (T) (B : VE.Structure) : Prop :=
  (∀ p ∈ regulatedNames T, ∀ vs, VE.TupleTyped B (sorts p) vs →
    ¬ (conflict E T p).denote B (tupleVal vs)) ∧
  (∀ (r, m) ∈ pairs E, ∀ vs, VE.TupleTyped B (sorts r) vs →
    ¬ (pairConflict E T r m).denote B (tupleVal vs))
```

`ConflictFreeAt E T p S₀` is different: `S₀` interprets the prefix **below** `p`; it is not a base structure.
It asserts no typed tuple satisfying `(pos T p) ∧ (neg T p)` in `S₀` under `tupleVal`, **without substitution**.
For each pair closing at `p`, it also asserts the following local condition, under the same typed tuples:

```text
p = r (obligation introduced last): ¬(outcome T r evaluated in S₀ at tupleVal vs ∧ ¬ S₀.relation m vs)
p = m (permission introduced last): ¬(S₀.relation r vs ∧ ¬ outcome T m evaluated in S₀ at tupleVal vs)
```

Only the new predicate is replaced by its local outcome; the earlier member is the actual relation in `S₀`.
The prefix invariant and typed `subst_sound`, not a change to this definition, relate these local tests to
`ConflictFree` over `restrictAll S₀`.

### 6.2 Theorems and the actual document-wide iff

```lean
theorem precedence_acyclic (E) (T) (h : WellFormed E T = true) :
  VE.Route.DagAcyclic (precedenceNodes T) ∧ VE.Route.DagAcyclic (stratumNodes E T)

/-- Local faithfulness on all structurally admissible outputs, before adding prefix satisfaction. -/
theorem elaborate_iff_at (E) (T) (h) (p) (hp : p ∈ regulatedNames T)
    (S : VE.Structure) (hS : S.Admissible E_(before p + 1)) :
  (elab T p).denote S [] ↔ IntendedAt T p S

theorem elaborate_iff (E) (T) (h : WellFormed E T = true)
    (S : VE.Structure) (hS : S.Admissible E_n) :
  Sat S (elaborate E T) ↔ holdsCatala E T S

theorem elab_completion (E) (T) (h) (p) (hp : p ∈ regulatedNames T)
    (S : VE.Structure) (hS : S.Admissible E_(before p + 1))
    (hc : ∀ vs, VE.TupleTyped S (sorts p) vs →
      ¬ ((pos T p).denote S (tupleVal vs) ∧ (neg T p).denote S (tupleVal vs))) :
  (elab T p).denote S [] ↔
    (∀ vs, VE.TupleTyped S (sorts p) vs →
      (S.relation p vs ↔ (outcome T p).denote S (tupleVal vs)))

/-- Explicit prefix, formula typing and valuation typing exclude undefined raw variables. -/
theorem subst_sound (E) (T) (h : WellFormed E T = true) (i) (hi : i ≤ n)
    (S : VE.Structure) (hS : S.Admissible E_i) (hlow : Sat S (PrefixPremises i))
    (Γ : List String) (φ : VE.Formula) (hφ : φ.WellFormed E_i Γ)
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
  (subst E T i φ).denote (restrictAll S) ρ ↔ φ.denote S ρ

/-- Local expansion; the input is an interpreted prefix, not an arbitrary base model. -/
theorem conflictFree_expands (E) (T) (h : WellFormed E T = true) (p) (hp)
    (S₀ : VE.Structure) (h₀ : PrefixAdmissible (before p) S₀) :
  VE.Route.Unique (fun S => forget p S = S₀ ∧ AdmissibleOut E T p S ∧ (elab T p).denote S []) ↔
    ConflictFreeAt E T p S₀

/-- The P0 instance, only when every admissible prefix input passes the local test. -/
def layer (E) (T) (h : WellFormed E T = true) (p) (hp)
    (hc : ∀ S₀, PrefixAdmissible (before p) S₀ → ConflictFreeAt E T p S₀) :
    VE.Route.Layer VE.Route.fol Unit
  -- E_in := E_(before p); E_out := E_(before p + 1); premises _ := [elab T p]
  -- Admissible_in := PrefixAdmissible (before p)
  -- AdmissibleOut E T p S = Admissible_out S := S.Admissible E_out
  --   ∧ Admissible_in (forget p S) ∧ IntendedAt T p S ∧ Sat S (pairPremisesClosedAt p)
  -- This is exactly PrefixAdmissible (before p + 1), including the CURRENT elaboration.
  -- restrict := forget p; Intended _ S := IntendedAt T p S
  -- faithful := elaborate_iff_at; expands := conflictFree_expands under hc

/-- The document relation is defined without assuming conflict-freedom or constructing Layers. -/
def DocumentExpansion (E) (T) (B S : VE.Structure) : Prop :=
  restrictAll S = B ∧ S.Admissible E_n ∧
    Sat S (background E ++ layerPremises E T)

/-- Pointwise iff over BASE structures, including definitions before, between and after norms. -/
theorem conflictFree_expands_document (E) (T) (h : WellFormed E T = true)
    (B : VE.Structure) (hB : BaseAdmissible E B) :
  VE.Route.Unique (DocumentExpansion E T B) ↔ ConflictFree E T B

/-- The document-wide iff; no predicate p and no intermediate-structure quantifier. -/
theorem conflictFree_expands_all (E) (T) (h : WellFormed E T = true) :
  (∀ B, BaseAdmissible E B → VE.Route.Unique (DocumentExpansion E T B)) ↔
    (∀ B, BaseAdmissible E B → ConflictFree E T B)

/-- Derive each layer's hypothesis from the base-level property via prefix satisfaction/substitution. -/
theorem conflictFree_prefix (E) (T) (h) (p) (hp)
    (hc : ∀ B, BaseAdmissible E B → ConflictFree E T B)
    (S₀ : VE.Structure) (h₀ : PrefixAdmissible (before p) S₀) :
  ConflictFreeAt E T p S₀

/-- Semantic route acceptance, distinct from wire admission (11.4). -/
theorem norms_route_acceptance (E) (T) (h) (hc : ∀ B, BaseAdmissible E B → ConflictFree E T B)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (hΓ : ∀ a ∈ Γ, a.WellFormed E_n []) (hφ : φ.WellFormed E_n [])
    (accepted : VE.Tableau.checkCertificate E_n (background E ++ layerPremises E T ++ Γ) φ c = true) :
  (∀ S, S.Admissible E_n → holdsCatala E T S → definitionsHold E S → profileHold E S →
    Sat S (Background_base E) → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed E_base []) → φ.WellFormed E_base [] →
    ∀ B, BaseAdmissible E B → Sat B Γ → φ.denote B [])

/-- Countermodels of base formulas expand; restriction is the companion route theorem. -/
theorem norms_route_countermodel (E) (T) (h) (hc) (Γ) (φ)
    (hΓ : ∀ a ∈ Γ, a.WellFormed E_base []) (hφ : φ.WellFormed E_base [])
    (B : VE.Structure) (hB : BaseAdmissible E B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, DocumentExpansion E T B S ∧ Sat S Γ ∧ ¬ φ.denote S []

/-- A typed finite BASE witness refutes the document property, not ConflictFreeAt. -/
theorem conflict_witness_sound {α} [DecidableEq α] (E) (T) (h) (p)
    (hp : p ∈ regulatedNames T) (M : VE.FiniteModel α)
    (valid : M.Valid E_base) (hb : backgroundValid M = true) (vs : List α)
    (typed : VE.TupleTyped M.asStructure (sorts p) vs)
    (hw : (conflict E T p).eval M (tupleVal vs) = true) :
  ¬ ConflictFree E T M.asStructure ∧
    ¬ VE.Route.Unique (DocumentExpansion E T M.asStructure) ∧
    ¬ (∀ B, BaseAdmissible E B → ConflictFree E T B)
-- Companion theorem conflict_pair_witness_sound uses (r,m) ∈ pairs E, sorts r and pairConflict E T r m.
```

All schematic `h` parameters are `WellFormed E T = true`; `hp` is membership in `regulatedNames T`; `hc` in
the countermodel theorem is the same universally quantified base conflict-freedom as in acceptance. `background E`
is the complete regenerated Background (flags, definitions, literals, profile); `Background_base E` contains
flags and literals only. Conflict certificates after substitution use **only** `Background_base E` (5.2):
no unexpanded definition premise is well-formed over `E_base`.

Proof plan:

1. Prove `tupleVal_typed`, typing preservation for prefix substitution, and the capture-avoiding atom substitution
   lemma for typed terms/valuations. Prove `elaborate_iff_at` by the four direct-value cases, then
   `elab_completion`, `prefix_satisfaction`, and `subst_sound` by induction over the explicit prefix. An atom
   with an undefined variable is deliberately outside the substitution theorem.
2. Prove the local iff using the actual lower tables. In the reverse direction set `p := O_p` on typed tuples
   and false on all others; preserve every other component. No `P ∧ N` point gives the elaboration; the local
   pair condition gives the newly closed profile premise. Completion forces this interpretation in any other
   expansion, giving structure equality as in `Examples.copy_expands`. In the forward direction any expansion
   rules out `P ∧ N` and satisfies the local pair condition; no arbitrary lower interpretation is substituted.
3. Prove the **pointwise document iff**, independently of the existence of globally valid `Layer` instances.
   From `ConflictFree E T B`, extend `B` in DAG order, inserting definition bodies or outcomes. At each prefix,
   substitution transfers the base tests to local tests, so the local iff supplies the norm step and W3 supplies
   the definition step. Inductively this preserves prefix satisfaction and proves uniqueness of the whole
   expansion. Conversely, a full expansion satisfies every prefix's premises; faithfulness excludes each
   intra-predicate conflict, substitution identifies every completed outcome with its interpreted relation,
   and the profile premises exclude every pair conflict. Thus even existence implies base conflict-freedom.
   Quantify this iff over `B` to obtain `conflictFree_expands_all`; merely quantifying a local iff is insufficient.
4. Given global base conflict-freedom, restrict any admissible prefix to a base structure; use
   `prefix_satisfaction` and `subst_sound` to derive `conflictFree_prefix`, hence each `layer`'s `hc`.
   Compose using the frozen `Layer.compose`: consecutive admissibility predicates agree by construction.
   Discharge both `BackgroundSound` and `BackgroundComplete` using prefix satisfaction, and apply the frozen
   acceptance and countermodel theorems. Keep `elaborate_iff_at` independent of the strengthened admissibility,
   so faithfulness is not justified solely by assuming its own conclusion.
5. Witness soundness uses typed `eval_iff_denote`, validated base Background and the document iff. The wire
   theorem of 11.4 additionally proves that these are the formulas regenerated from the document that was decoded
   and identity-bound. Every proof is audited with the existing axiom allowlist.

### 6.3 What is not claimed

No completeness of the conflict check outside section 7. No theorem about the English surface (W7). No claim
that `Intended` matches an author's intent: that is the statement review of `holdsCatala` and the fidelity gate
of W8. W1's new executable norm-document admission and its end-to-end theorem are FOL-only. Closure/order
conflict certificates use the new wrapper's regenerated base formulas and the unchanged family checkers;
full document admission for those families remains deferred to a new compatible admission implementation,
not an assumed future edit of frozen P0 decoders. The wrapper rejects unsupported modes explicitly (11.4).

## 7. The decidable fragment, as a proof-gated theorem

### 7.1 Membership

`InFragment(E, T)` holds when, after outcome substitution and definition expansion:

1. every `conflict_p` and `pairConflict` is quantifier-free (every guard, carve-out and expanded definition body
   in the cone of the norms is quantifier-free);
2. no `Reach` (closure) node and no `$int` term or `Lt`/`Le` atom occurs in them (the environment may enable
   `closure@0` or `order@0`; what matters is the formulas);
3. the admissibility theory of `E_base` is universal, function-free and relational: `functional` flags allowed
   (their premise is `∀x∀y∀z`), `total` on any predicate of `E` puts the document outside (its premise `∀x∃y` is
   existential and not preserved under substructures), literal distinctness is ground, n-ary atoms (W4) allowed;
4. no adapter predicate occurs in them (adapter truth is a labelled assumption, not a premise).

Membership is decided syntactically and reported per document (`fragment: yes | no (<first reason>)`).

### 7.2 The theorem (gates completeness; W1 acceptance 10.1 when claimed)

```lean
/-- A conflict witness in the fragment restricts to the witnesses plus constants. -/
theorem conflict_smallModel (E) (T) (h : WellFormed E T = true) (hf : InFragment E T = true) (p)
    (hp : p ∈ regulatedNames T)
    (S : VE.Structure) (hS : BaseAdmissible E S) (v̄) (typed : VE.TupleTyped S (sorts p) v̄)
    (hw : (conflict E T p).denote S (tupleVal v̄)) :
    ∃ (α : Type) (_ : DecidableEq α) (M : VE.FiniteModel α) (w̄ : List α),
      M.Valid E_base ∧ backgroundValid M = true ∧
      VE.TupleTyped M.asStructure (sorts p) w̄ ∧
      (∀ s, (M.domains s).length ≤ max 1 (constantsOfSort E s + witnessVarsOfSort T p s)) ∧
      (conflict E T p).eval M (tupleVal w̄) = true
-- and the same statement for `pairConflict E T r m` with (r,m) ∈ pairs E and the sorts of r
```

Proof sketch: let `D_s` be the set of elements of sort `s` among the denotations of the constants of sort `s`
and the components of `v̄` of sort `s`; the substructure `S|D` (relations restricted) is a structure of
`E_base`; `M.Valid` (typed tables, constants present) holds by construction; universal premises (functional
flags) and ground ones (literal distinctness) are preserved under substructures, so `backgroundValid`; the
quantifier-free `conflict_p` has the same value at `v̄` in `S|D` as in `S` (atoms only, all elements of `v̄`
present and the returned `w̄` typed). Frozen `VE.Structure` and `VE.FiniteModel.Valid` allow empty sort domains,
so the enumerator must include size zero when no constant or witness requires an inhabitant. If a later model
format requires a nonempty sort that was nonempty in `S`, retain one existing element of that sort when `D_s`
is empty; this still gives a substructure and the bound `max 1 (constants + witness variables)`. Never invent
an inhabitant of an originally empty sort: universal premises need not survive that extension. Terms of
`E_base` are constants and variables only (v0 is function-free), which the theorem's
statement relies on.

Consequence (`conflict_complete`, stated only after the proof): if `InFragment E T` and the enumerator finds no
valid finite base model within the per-sort bounds in which any conflict formula is true, then
`∀ S₀, BaseAdmissible E S₀ → ConflictFree E T S₀`. Until `conflict_smallModel` is proved and audited (no new
axioms; `lean/audit.py` allowlist unchanged), the enumerator is the oracle of acceptance 10.5 and never a source
of CONFLICT-FREE; CONFLICT-FREE needs a tableau certificate (binding decision 9.4, deferred-item trigger in the
plan's section 7).

### 7.3 The regression that must never certify

Rules `Rule 1. Every item is admitted, if it is not the case that that item relates to itself.` and `Rule 2. Every
item is not admitted, if it is not the case that that item relates to itself.` over `relates(item, item)`
declared `functional: true, total: true`. The document is outside the fragment (`total`). One-element base
structures have `relates = {(1,1)}`, so both guards are false there and enumeration to bound 1 finds nothing;
the two-element structure `relates = {(1,2),(2,1)}` is valid (functional, total) and both rules select at
`x = 1`. Expected: CONFLICT with that two-element witness; with the witness search disabled, UNKNOWN naming the
budget; never CONFLICT-FREE (there is no certificate, since the entailment is false).

## 8. Cedar adapter (`ve/adapters/cedar.py`, inside W5's `ve/adapters/` package)

The adapter turns a Cedar policy set (with template links) into a norm document and compares the elaborated
decision with the recorded Cedar decision. Reference: `experiments/P3-formalisation-tax/reference_cedar.py`
(115/115 upstream decisions reproduced), which is the oracle of both gates.

```text
sorts        request (reified), entity sorts per Cedar entity type (W5 attributes and $string literals for ids)
predicates   principal(request, entity), action(request, entity), resource(request, entity) as functional+total
             attributes (W5); parent(entity, entity) as the base hierarchy edge; `in` is rtc[parent] (closure@0,
             reflexive as Cedar specifies); has_<attr>, <attr>(entity, value) for attributes (W5)
regulated    permitted(request): role permission, default deny ("By default, a request must not be allowed."),
             act "{0} be allowed"
permit i     rule permit-<id>: permitted(r) if def_i(r) ∧ val_i(r)
forbid j     rule forbid-<id> over every permit rule: ¬permitted(r) if def_j(r) ∧ val_j(r)
             (a forbid is an exception of every permit, so a satisfied forbid blocks every permit: Cedar's
             "forbid overrides"; two satisfied forbids are same-sign overlap, not a conflict)
templates    one rule per linked instance (`instantiate` in the reference: static policies plus one instance per
             link); an unlinked template yields no rule and is listed under exclusions as `template-unlinked`
decision     allow ⇔ O_permitted(r) = P_permitted(r); by the tree shape this is
             (∃ i. applies_i(r)) ∧ ¬(∃ j. applies_j(r)): exactly `permit and not forbid` of the reference
```

Condition translation is runtime-type-aware, matching `Evaluator.bool_`, `Evaluator.in_` and `Evaluator.ev`
in the reference interpreter and the [Cedar operator semantics](https://docs.cedarpolicy.com/policies/syntax-operators.html).
For each expression `e`, retain a definedness formula `D_e`, its tagged value `V_e`, and tag tests
`Bool_e`, `Entity_e`, `Record_e`, `Set_e`. `b_e` means its Boolean payload when `Bool_e`; it is a harmless
placeholder otherwise. `B_e := D_e ∧ Bool_e`. Tags are runtime tags, not an assumption that Cedar validation
succeeded. Finite literal cases compile by case splitting; W5 attributes must retain tags/presence. A value
form whose tag/payload cannot be represented is excluded with reason `value-representation`, never silently
coerced. No strings or entities are treated as truthy. Value expressions in this table are translation
metanotation, not new VE terms or trusted predicates supplied by the policy author.

```text
expression                  definedness D                                      value V (Boolean results use b)
lit, var, slot(linked)       ⊤                                                  literal/request/linked tagged value
[e₁, ..., eₖ]               ⋀ᵢ D_eᵢ                                           finite set of the tagged V_eᵢ
e has a                     D_e ∧ (Entity_e ∨ Record_e)                        has_a(V_e)
e.a                         D_e ∧ (Entity_e ∨ Record_e) ∧ has_a(V_e)           attribute payload, with its tag
a && b                      B_a ∧ (¬b_a ∨ B_b)                                 b_a ∧ b_b
a || b                      B_a ∧ (b_a ∨ B_b)                                  b_a ∨ b_b
!a                          B_a                                                ¬b_a
if c then a else b          B_c ∧ (b_c → D_a) ∧ (¬b_c → D_b)                   chosen branch's tagged value
e in f                      D_e ∧ D_f ∧ Entity_e ∧ Entity_f                    rtc[parent](V_e, V_f)
e in [f₁, ..., fₖ]          D_e ∧ Entity_e ∧ ⋀ᵢ (D_fᵢ ∧ Entity_fᵢ)            ⋁ᵢ rtc[parent](V_e, V_fᵢ)
e == f, e != f              D_e ∧ D_f                                          tagged value equality, its negation
e is T                      D_e ∧ Entity_e                                     entity type of V_e equals T
e is T in f                 translate (e is T) && (e in f), including short-circuiting
unless { c }                B_c                                                ¬b_c
```

For a set-valued right operand other than a literal, `in` requires `Set_f` and checks **every** member's entity
tag before using the membership disjunction; an empty set has no successful member. A non-entity left operand
errors even for an empty set. Entity types may differ: the check is for entity values, not identical entity
types. A scalar right operand that is neither an entity nor a set of entities errors. Cross-tag `==` is false
and `!=` true; equality itself is not a type error. For `if`, only the condition must be Boolean; branches
retain their own tags, and only the chosen branch's definedness matters. When an expression is used as a
policy condition its result must also pass `Bool`; `unless` negates only such a defined Boolean result.

Scope constraints and `when`/`unless` clauses are combined in Cedar's evaluation order using these guarded
Boolean operations. The final policy guard is `B_condition ∧ b_condition`. An erroring policy has false
definedness, is listed under `errors`, and contributes to neither effect. In particular, a forbid with
`principal in [User::"alice", "x"]` errors and is skipped even for Alice; matching the first member cannot
hide the invalid second member. A skipped policy is still in the translated corpus; an unsupported construct
is an exclusion, which is a different outcome.

Extension functions/methods, `like`, set operations beyond the listed set construction/membership, arithmetic,
comparisons `<`, `<=`, and unrepresented values are excluded by reason (`extension-function`, `like`, `set-op`,
`arithmetic`, `comparison`, `value-representation`). W1 additionally excludes context and attribute access
(`context`, `attribute`); W5 enables their typed rows above. Decisions depending on excluded policies are
excluded too. The adapter reports decision agreement **and** the set of erroring policies; comparing allow/deny
alone could miss the same error in two translators. Deterministic error and short-circuit cases are in 10.2.

Lean `Norms/Cedar.lean`, `cedar_decision`: for a tree of the adapter's shape (every negative rule takes precedence
over every positive rule, no carve-outs, no nesting among positives or among negatives), on every structure
`O_permitted(r) ↔ (∃ i, applies_i(r)) ∧ ¬(∃ j, applies_j(r))` and `P ∧ N` is unsatisfiable, so such a document is
CONFLICT-FREE by a certificate the tableau finds without search hints. The translation table is Python only and
is tested against the reference, not proved.

Gates (plan W1(2)): W1's own gate is the no-attribute subset of `cedar-integration-tests@1999ea2` (11 scenarios,
115 decisions): every in-fragment decision equals the recorded decision and `reference_cedar.py`; exclusions listed
by reason. The joint W1+W5 gate (after W5) runs all 115 including missing-attribute and error cases, and the 143
policies of both pinned corpora mechanically, with the in-fragment fraction reported.

## 9. Pilot reformalisations

### 9.1 US Constitution, Amendment XIV section 1, clauses 2 to 4 (`usecases/us-constitution-14th-s1`)

Today's `claims.ve` states each prohibition as a universal negative over base facts (true in a world where states
never abridge and in one where they may not: `GAPS.md` gap 1). With `norms@0` the base facts stay (`makes_law`,
`enforces_law`, `deprives`, `denies_equal_protection` record what happened) and the norms regulate:

```text
regulated  make_permitted(state, law), enforce_permitted(state, law), deprive_permitted(state, person),
           deny_equal_protection_permitted(state, person): permission, allow-by-default
           ("By default, a state may make a law." and so on: the amendment restricts, it does not license)
Rule 1.  Every state must not make each law that abridges the privileges or immunities of a citizen of the United States.
Rule 2.  Every state must not enforce each law that abridges the privileges or immunities of a citizen of the United States.
Rule 3.  Every state must not deprive each person of life, liberty or property, unless that state affords that
         person due process of law.
Rule 4.  Every state must not deny the equal protection of the laws to each person who is within the
         jurisdiction of that state.
definitions (W3, above the norms)
         breach_make(s, l) := ¬make_permitted(s, l) ∧ makes_law(s, l)   (and enforce, deprive, deny likewise)
```

"abridges the privileges or immunities of a citizen" is the existing opaque predicate `abridges_priv_or_imm(law,
person)` under an existential over the citizen (a W3 definition `abridging(l) := ∃p. us_citizen(p) ∧
abridges_priv_or_imm(l, p)`), so rules 1 and 2 are outside the fragment of section 7 (three-valued status; the
document is CONFLICT-FREE by certificate, since no rule selects positively). The open-textured terms stay open
terms (W2 schema). Acceptance 10.4: a countermodel exhibiting `breach_make` (a state makes an abridging law) and a
model with no breach.

### 9.2 Claude constitution excerpt, sentences 8 and 9 (`usecases/claude-constitution-excerpt`)

The current statement 7 asserts, for every pair of contending properties, "follow the higher and do not follow
the lower", which is unsatisfiable with three contending properties (`GAPS.md` gap 1, the pairwise-shape defect).
The corrected norm asserts only the positive side and leaves the rest to the default:

```text
regulated  follow(situation, property): obligation, deny-by-default ("By default, a situation need not
           follow a property."), act "{0} follow {1}"; no permission dual declared
base       contends_for(situation, property), outranks(property, property) (the three edges), violates_hard_constraint(situation)
Rule 1.  Every situation must follow each property that that situation contends for.
         Except when there is a property that that situation contends for and that outranks that property
         by one or more outranks steps.
         Except when that situation violates a hard constraint.
```

The guard's existential and the closure step place it outside the fragment; its conflict status is three-valued
and, as a single positive rule with no dual, CONFLICT-FREE by certificate. With three contending properties the
document is satisfiable: `follow(s, safety)` is required, `follow(s, ethics)` and `follow(s, guidelines)` are not
(default), and nothing is asserted against them. Sentence 9's "holistic rather than strict" is not a norm: the
weighing is an open term `weighs_higher(s, x, y)` (decider: the constitution's authors; W2 open-term schema), and
the unit for sentences 8-9 is a reading set with two readings, (A) rule 1 above (strict dominance) and (B) rule
1 with the carve-out "unless there is a property that that situation contends for and that weighs higher than
that property in that situation" (the open-term form). Both are norm readings, so a conclusion depending on the
unit is checked per choice (W2, item 7), never by disjunction. Acceptance 10.4.

### 9.3 Gatekeeper deny templates (W1 acceptance (3))

Each of the 10 deny-style templates becomes `admitted(object)`: plain regulated, allow-by-default, one rule
`¬admitted(o)` per template with the template's violation condition as guard, and `is_exempt` (W5 adapter table)
as a rule `admitted(o) if is_exempt(o)` taking precedence over every deny rule. The template's fixture
violations are exactly the objects with `¬O_admitted`.

## 10. Acceptance tests

Each test names its expected result; every result is required from Python and, where the Lean route has a case
kind for it, from Lean (`tests/test_norms_three_way.py`, extending `conformance/p0.py` with a `norms` family).

### 10.1 The reviewers' counterexamples and the worked cases

These are deterministic regressions with hand-written expected tuples, truth values, diagnostics and premise
lists. They supplement, rather than derive their expected results from, either elaborator or the generated corpus.

| # | Document (one act, `a` the only situation) | Expected |
|---|---|---|
| a | `required` deny-by-default with an unconditional rule `must`; `permitted` deny-by-default with no rule; pair declared | CONFLICT with witness `a` (`O_required(a) ∧ ¬O_permitted(a)`); the v2-style check that looks only for a rule selecting `¬permitted` sees nothing, which is the point |
| b | `required` allow-by-default with no rule (required by default); `permitted` deny-by-default with no rule; pair declared | CONFLICT with witness `a`: no rule selects anything and the pair formula holds |
| c | as (a) plus `Rule 2. Every act may be done.` | CONFLICT-FREE (certificate); example situation shows `a` required and permitted |
| d | grandchild (Astra): rule 1 `¬p`, rule 2 (exception to 1) `¬p`, rule 3 (exception to 2) `p`, all guards true | CONFLICT-FREE; `yields_3`, so rules 2 and 1 do not select; outcome `p(a)`; the differential elaboration test includes this tree |
| e | `Rule 1. Every act is p, if it is not the case that that act is p.` | rejected at well-formedness with `DependencyCycle: p` from Python and Lean |
| f | `Rule 1 (exception to rule 2).` and `Rule 2 (exception to rule 1).` | rejected with `DependencyCycle: r1, r2` from Python and Lean |
| g | `Rule 3 takes precedence over rule 5` where rules 3 and 5 regulate different predicates | rejected, `PrecedenceAcrossPredicates` |
| h | the total-functional `¬r(x,x)` regression of 7.3 | CONFLICT with the two-element witness; UNKNOWN with search disabled; never CONFLICT-FREE; `fragment: no (total)` |
| i | carve-out versus exception (2.6 row 2): default `must not`, rule 3 forbids, rule 6 forbids in the same situation, rule 3 carries `unless C` (variant a) or rule 4 (exception to rule 3) permits under `C` (variant b) | variant (a): in a situation with `C`, outcome not permitted (rule 6); variant (b): CONFLICT (rule 4 permits, rule 6 forbids, no precedence between them) with the witness situation |
| j | doctor-on-Monday (2.6 last row) | outcome permitted on Monday for a doctor on call; not permitted for a doctor not on call; the example situations are shown |
| k | two same-sign rules selecting at one situation | CONFLICT-FREE with `Overlap` diagnostic naming both rules and a situation |
| l | a pair outside the fragment with both budgets exhausted (a guard with an existential over a sort with no constants and a large search bound disabled) | UNKNOWN naming the budget (budget-to-UNKNOWN test) |
| m | pair `a-required`, `b-permitted`, both deny-default, no rules, obligation ordered first; try an intermediate table with `a-required(a)` true | document CONFLICT-FREE; the intermediate structure fails `PrefixAdmissible 1`; the valid prefix has required false and uniquely expands to both false; Lean constructs both frozen `Layer` instances |
| n | permission ordered first, deny-default, no rules; obligation allow-default, no rules; try lower permission true | document CONFLICT; that lower structure is not prefix-admissible; the valid lower permission is false and has no full expansion; tests the document iff, not just a local iff on the invalid table |
| o | instantiate (c) as a Lean route; also insert a definition `eligible(x) ↔ permitted(x)` between permission and a required rule guarded by `eligible` | `layer` accepts its `hc` from `conflictFree_prefix`; the unique full expansion satisfies all rules and definition biconditionals; changing the intermediate defined table invalidates prefix admissibility |
| p | a required rule whose guard directly mentions its paired permission; permission has one unconditional positive rule, both defaults deny | CONFLICT-FREE; both outcomes true; permission precedes obligation; removing the permission rule makes both false, still CONFLICT-FREE |
| q | diamond: `r1` negative; `r2`, `r3` negative, each over `r1`; `r4` positive over both `r2` and `r3`; all guards true | only `r4` selects, shared descendant counted consistently; CONFLICT-FREE and positive outcome |
| r | `r1` forbids on Monday; `r2` over `r1` permits on call; on-call Tuesday, deny-default | `r2` selects and permits despite the parent guard failing; the 2.5 paraphrase explicitly shows this situation |
| s | `r1` negative; `r2` negative over `r1` has a true carve-out; `r3` positive over `r2` has true guard | `r2` does not apply/select but yields via `r3`; `r1` blocked; `r3` alone selects; CONFLICT-FREE |
| t | `p(state,person)`, disjoint singleton domains `{Texas}`, `{Ann}`, base `r={(Texas,Ann)}`, guard `r(var 1,var 0)` | positive-only rule gives exactly `p(Texas,Ann)`; add an equally guarded negative rule: CONFLICT at argument tuple `[Texas,Ann]`, evaluated with `[Ann,Texas]`; exercise completion, pair outcomes, witnesses and small-model typing, never a reversed relation tuple |
| u | allow-default lower predicate, no rules; substitute its atom containing an unbound variable, or present a witness tuple with wrong sorts/length | raw undefined atom and substituted outcome may differ; `subst_sound` requires typed formula/valuation and cannot be applied; admission rejects the malformed formula/witness; typed prefix instances agree |
| v | `must enter` and `must not enter` predicates for the same act, with the dual omitted; alternatively link `must enter` to permission to leave with matching sorts | `MissingPermissionDual` / `DualActMismatch`; after a correct link, simultaneous must/must-not gives CONFLICT; duplicate same-role act is `DuplicateActRole` |
| w | 2.6 carve-out/exception distinction with deny default and **no** independent third rule | under `C`, carve-out variant forbidden by default, exception variant permitted; adding the third rule changes only the exception variant to the conflict in (i) |

### 10.2 Cedar

W1's own gate on the no-attribute subset (section 8), decisions equal to the recorded ones and to the reference;
exclusions listed by reason; `cedar_decision` audited; a permit-only policy set is CONFLICT-FREE without hints;
a set with two overlapping forbids reports `Overlap` and the recorded deny.

For each condition below, pair an unconditional permit with a forbid carrying the condition. Check the reference
interpreter's error-policy set as well as the decision; repeat set examples in reversed member order. No adapter
implementation is accepted on corpus agreement alone.

| Forbid condition (principal Alice) | Expected condition / decision |
|---|---|
| `principal in [User::"alice", "x"]` | runtime type error, forbid skipped, allow |
| `"x" in []`; `principal in "x"` | runtime type error, forbid skipped, allow |
| `principal in []`; `principal in [User::"alice"]` | false / allow; true / deny |
| `true && "x"`; `false || "x"`; `!"x"`; `if "x" then true else false`; bare `"x"` | Boolean type error, forbid skipped, allow |
| `false && "x"`; `true || "x"` | false / allow; true / deny; neither errors |
| `if true then true else !"x"`; `if false then !"x" else false` | true / deny; false / allow; unchosen branch does not error |
| `principal is Group in "x"` | false / allow; failed type test short-circuits the invalid membership operand |
| `principal == "alice"`; `principal != "alice"` | false / allow; true / deny; equality mismatch is not an error |

With W5, also test `has` and attribute access on non-record/non-entity values, missing attributes and a
non-Boolean attribute in condition position. Unsupported value representations must be listed as exclusions,
not reported as successful translations or runtime-skipped policies.

### 10.3 Gatekeeper

The 10 deny templates reproduce their fixture violations through `admitted`; an exempt object is admitted.

### 10.4 Pilots

14th s1: the four rules parse from English and strict text to the same AST; a countermodel exhibiting
`breach_make` and a model without one; the document's status CONFLICT-FREE by certificate and `fragment: no
(quantifier)`. Constitution: rule 1 satisfiable with three contending properties (a checked model); the reading
set with readings A and B is checked per choice; removing the open-term reading changes the verdict label
(`readings:...:A` versus `all`), not the certificate.

### 10.5 Oracle and fragment

An independent brute-force finite-model enumerator (written from section 7's bounds, not from `ve/norms.py`)
agrees with the tableau on 500 generated in-fragment pairs: every CONFLICT-FREE certificate has no enumerated
witness and every enumerated witness is accepted as a CONFLICT witness; on 100 generated out-of-fragment
documents (a `total` flag or a quantified guard) every enumerator "no witness" result is reported as UNKNOWN,
never CONFLICT-FREE, unless a certificate exists.

### 10.6 Surface

2,000 generated norm documents (depth up to 4, up to 3 carve-outs, multi-parent precedence, both defaults, all
three roles) round-trip `AST → (English, metadata) → AST` exactly, including arbitrary names and `over` edges;
canonical `(English, metadata) → AST → (English, metadata)` is byte-identical. Strict text round-trips without
metadata. Every English text has exactly one grammatical derivation; the identity protocol is separate.
Renumbering preserves each existing rule's `meaning_id` (the changed document has a new document/report hash).
Each row of 2.6 produces its listed paraphrases and rewrites, with the actual default in every carve-out paraphrase.

Deterministic surface cases: both flagship `each person` rules bind `that person`; dangling `a person … that
person` rejects; object-position `every` under `must not` rejects with the `each` rewrite; subject `Every` and
object `each`/`any` accept. The bare `A doctor` example is rejected and rewritten, not claimed to parse already.

### 10.7 Identity

Every existing fixture, identity, certificate and wire hash unchanged; `conformance/english-surface-report.json`
does not move; a norm unit's `meaning_id` binds the norm AST and not its elaboration (the same AST under two
environments differing only in a default has different `environment_id` and hence different `meaning_id`; the
same environment and AST under renumbering has the same); adding a `regulated` field changes `environment_id`.

Hand-written identity regressions: arbitrary names `ward-ban`/`on-call-release` survive export/reimport; two
identical rule texts retain distinct names/handles; inserting, moving, renumbering and editing a block preserve
that block's name; a copy gets a fresh name; references to duplicate-looking blocks still resolve to the chosen
handle. Missing metadata follows the new-import path without claiming preserved identities; stale, duplicated
or hash-mismatched metadata rejects. Two ASTs differing only in stable names may render the same bare English
but must have different metadata and identities. Deleted referenced blocks produce a dangling-reference error.

### 10.8 Certificate binding

A CONFLICT-FREE certificate replayed against a document whose norm hash differs (a dropped carve-out, a flipped
default, a swapped precedence, a changed act phrase) is rejected as stale by Python and Lean; a certificate for
the entailment `Background ++ layer premises ++ Γ ⊢ φ` replayed with an elaboration supplied on the wire that
differs from the regenerated one is rejected.
Exercise the raw JSON `norms-route` entry point of 11.4, not only helpers accepting decoded formulas. Change a
norm object while retaining its old generated premises, source document hash or report id; each mismatch rejects.
Change a pair link, drop a norm unit, replace norm content with a formula, or spoof a `layer:norms:<p>` leaf:
admission rejects. A conflict certificate's regenerated `E_base` and `Background_base` contain no derived
symbol or unexpanded definition; the outer binding still names the complete original environment/document.
Valid regulated declarations and norm-object contents must reach checking through the new binary; old P0
entry points keep their current rejection. Supported non-norm P0 cases delegated by the wrapper agree exactly.

### 10.9 Differential elaboration

Python `elaborate` versus Lean `Norms.elaborate` on 1,000 generated trees (nesting depth up to 4, both
completions, carve-outs, the `¬p, ¬p, p` case, pairs): identical premise lists; the mutations of 10.8 flip a
verdict (conflict status or an entailment) and are rejected by the bound hash.

### 10.10 DAG diagnostics

Definition above a norm accepted; a norm whose guard uses a definition accepted; a definition mentioning a
regulated predicate of its own stratum rejected; cycles through a definition and a norm rejected with the same
diagnostic from Python and Lean on 200 generated graphs (P0's differential extended with norm nodes).

### 10.11 Lean

`tupleVal_typed`, `elaborate_iff_at`, `elaborate_iff`, `elab_completion`, `prefix_satisfaction`, `subst_sound`,
`precedence_acyclic`, `conflictFree_expands`, `conflictFree_expands_document`, `conflictFree_expands_all`,
`conflictFree_prefix`, `norms_route_acceptance`, `norms_route_countermodel`, `conflict_witness_sound`,
`conflict_pair_witness_sound`, `norms_wire_acceptance`, `norms_wire_conflict_sound`,
`cedar_decision` audited (`lean/audit.py`: allowlist unchanged, no `sorry`); `conflict_smallModel` when claimed;
`lean/NORMS.md` lists each in plain words; `lean/METATHEORY.md` gains the `Norms` section; frozen-source hashes of
the v0, closure, order and Route files unchanged.
Lean executable guards instantiate 10.1(m–u), including actual `Layer` values for (c), arbitrary invalid lower
tables, the diamond and mixed-sort witnesses. Small-model checks, when enabled, return typed witnesses and
include empty irrelevant sorts; if a later format requires nonempty sorts, test the retained-element case of 7.2.

## 11. Diagnostics, identity, model validity, limits, Rust

### 11.1 Diagnostics (shared text in Python and Lean)

`DependencyCycle: <sorted names>` (precedence or stratification, as P0), `DuplicateDeclaration: rule <name>`,
`UnknownRule: rule <n>` (English) / `rule <name>` (strict), `PrecedenceAcrossPredicates: rule <a> on <p>, rule <b>
on <q>`, `ConsequenceArguments: rule <name>`, `DualSortMismatch: <r>, <m>`, `DualActMismatch: <r>, <m>`,
`MissingPermissionDual: <r>, <m>`, `DuplicateActRole: <role>, <act>`, `RegulatedDefinedPredicate: <p>`,
`RegulatedFlag: <p>`, `InvalidInput` for a missing `default`/`role`/`act`, `ResourceLimit: rules` (more than 256
rules), `ResourceLimit: regulated predicates` (more than 64), `ResourceLimit: precedence depth` (more than 16),
`UnsupportedProfile: norms@0 requires relational-fol@0` (always satisfied on `ve.core@0.2`). English diagnostics
carry the span and the plain-language expectation as today.
`IdentityMetadataMismatch` covers invalid/stale English identity metadata; `UnknownRule` covers a deleted
referenced block. These are new norms diagnostics; existing P0 diagnostics are unchanged.

### 11.2 Identity

`environment_id` binds the `regulated` declarations (3.1). A norm unit's `meaning_id` is
`sha256("ve-meaning-<identity_version>\n" + canonical({"environment_id", "ast"}))` with `ast` the norm object of
3.2 (stable names, no numbers), as for every unit. The norm document hash is the canonical array of norm objects
in document order under `environment_id`; every CONFLICT-FREE certificate and every route certificate is bound to
it through the report identity of P0 3.9 (`{"environment_id", "document", "report"}`), so stripping a carve-out
or flipping a default invalidates the certificate.

**English identity protocol.** `renderEnglish(E, T)` returns an English view plus an editor/export manifest:
`environment_id`, source norm document hash, a text digest, and one entry per block containing a persistent
editor handle, stable rule `name` and current span/display number. The manifest is not shown as English and
does not add tokens to the grammar. Export carries text and manifest together; strict text and the JSON norm
objects remain self-contained alternatives. Handles are editor metadata; only rule names/ASTs, not handles or
display numbers, enter `meaning_id`.

`parseEnglish(E, text, manifest)` validates the environment/text binding, one-to-one block/handle/name mapping,
unique names and spans, then parses with those names and resolves numbered references to the named target block.
It recomputes the AST document hash and requires the supplied source hash to match. Thus
`parseEnglish(E, renderEnglish(E,T)) = T`, including names and edges, for every well-formed `T`. A stale manifest
is rejected, not heuristically matched by wording. Two identical block texts can have different names and
remain two distinct rules.

Editing uses explicit handle-based transactions: moving, renumbering or editing an existing block preserves
its name; insertion/copy creates a fresh name; deletion removes that handle and any surviving reference to it
must be repaired or rejected. The editor retains edges to handles while renumbering, regenerates their display
references, and emits a new manifest with the new text/AST hash. Existing rule `meaning_id`s remain stable
under renumbering alone; editing their guard/consequence/edges changes them. A document insertion/reordering
changes its document/report hash even when surviving rule identities do not change. Arbitrary detached text
edits are parsed as new imports unless accompanied by an explicit valid edit transaction.

Bare-English import allocates `rule-1`, `rule-2`, … in block order, skipping reserved/existing names in the
target document; copies use the first unused such name. Names once allocated persist. No equality
`parseBare(renderBare(T)) = T` is claimed for arbitrary names: bare English is a view/import format, not an
identity-preserving serialization. Text exported without metadata is labelled accordingly by the editor.

### 11.3 Regeneration and model validity

Layer premises are regenerated from the decoded units by Python and Lean at every site; a premise list on the
wire is used only by Rust (11.6) as untrusted regression input; trusted sites reject it or compare it exactly
with regeneration before checking, and bind the regenerated formulas. A finite model on a norm route supplies
base tables only: a regulated predicate's table is computed as `O_p` in the shared DAG order, interleaving
definitions, and a supplied regulated
table is rejected with `InvalidModel("norms", "<p> is regulated; its table is computed")`, mirroring W3's rule
for defined predicates; the `profile` hook then validates each declared pair. At a `P ∧ N` point the computed
model falsifies `elab_p`, which the countermodel check reports as a false premise at that tuple (never as
`InvalidModel`); the conflict check is where that situation is reported as CONFLICT.

### 11.4 Reachable decoder/admission path and wire theorem

The frozen `Route.Wire.decodeVocabulary` rejects `regulated`, and frozen `Route.Admission.decodeUnit` requires
formula content. W1 therefore adds `lean/VE/Norms/Wire.lean`, `Admission.lean`, `Run.lean` and a new Lake executable
target `ve_norms_route` (invoked as `lean/.lake/build/bin/ve_norms_route <cases.json>`, the **norms-route** path).
Its `Run.main` is the executable root: no edit to `lean/Main.lean` or any frozen `Route` file is required.
Build/conformance integration adds this target to the build list without modifying existing target behavior.
Python dispatches norm cases to its matching new decoder/admission module and this executable. Existing P0
inputs without norm constructs can delegate unchanged to `Route.Run.runCase`; malformed norm inputs never
fall back to P0 after a failed new-path decode.

The new entry point must perform the following sequence on raw input, not merely accept pre-decoded formulas:

1. Run the frozen envelope/profile gate. Require `norms@0` for regulated declarations or norm content. Decode
   the extended vocabulary with a new strict decoder, checking all fields, act/dual consistency, typing and
   W3 dependencies. It may validate the ordinary declaration fields through the old decoder after separating
   recognised extension fields, but must retain and validate those fields and hash the **original complete**
   environment; stripping them is not an admission path. Reject unknown fields. W3 syntax uses W3's new decoder.
2. Decode norm-object content (3.2), rule names, spans, unit kinds and precedence into `T`; run `WellFormed` and
   the shared DAG checks. Reuse P0 kind/graph machinery where its input type fits, but introduce norms-specific
   unit and admission types. Do not pass norm objects to `Wire.decodeClosed` or disguise them as asserted
   formulas. Preserve W2's quoted/hedged/reading-choice provenance: only active norm units for the admitted
   choice contribute layers; every such unit and choice remains in the bound source document.
3. Regenerate the full Background and interleaved layer premises, plus `E_base`, `Background_base` and every
   substituted conflict formula. The new label parser adds `layer:norms:<p>` locally. A layer-labelled leaf is
   admitted only if it equals the regenerated `elab T p` for the active, decoded rules on `p`; profile leaves
   must equal regenerated pair premises. Quoted units cannot be activated without the required bridge/choice.
   Claim-graph certificate replay uses unchanged checker functions on these regenerated typed formulas.
4. Validate certificate bindings before replay. A conflict package has an outer source binding
   `(environment_id, norm_document_hash, conflict_target)` and an inner ordinary certificate bound to the
   canonical **regenerated base environment**, `Background_base` and the closed negated conflict formula.
   Both bindings are recomputed from the raw source; an ordinary P0 base certificate alone is insufficient to
   identify a norm document. Entailment certificates bind the full source environment and regenerated
   `Background ++ layerPremises ++ Γ`. An admitted report uses P0's unchanged identity domain and canonical
   `{"environment_id", "document", "report"}` payload, with the complete validated source document, not a
   formula projection. Recompute any supplied report id; reject stale bindings and mismatched formula lists.
5. Run the selected unchanged checker. For FOL documents, return the admitted report with provenance and
   regenerated premises. For conflict packages on FOL/closure/order, replay the relevant family's checker
   against the regenerated base formulas. Unsupported document-admission families return `UnsupportedProfile`;
   closure+n-ary remains subject to W4's gate. Resource limits never become a verdict.

The acceptance obligation starts at the public entry point. In the following schematic statement, `j` is
raw JSON and `a` is a successful result for `kind = admission`:

```lean
theorem norms_wire_acceptance (j a : Json)
    (h : Norms.Run.runCase j = .ok a) (hk : caseKind j = .ok "admission")
    (hn : usesNormsPath j = true) :
  ∃ D, Norms.Wire.decodeSource j = .ok D ∧ WellFormed D.E D.T = true ∧
    a = encodeAdmitted (regeneratedAdmission D) ∧
    BindingsMatchSourceAndRegeneration j D a ∧
    Norms.Admission.ReportAdmitted D a ∧
    (∀ S, S.Admissible D.E_out → Sat S (regeneratedBackground D ++ regeneratedLayers D) →
      Sat S (reportOtherAssumptions D a) → (reportConclusion D a).denote S [])
```

`regeneratedAdmission` includes the decoded graph, checked evidence, labels and exact premise lists, not just
the tree. `usesNormsPath` is the executable dispatch test for norm profiles/constructs; delegated P0 cases
retain their existing theorem. `BindingsMatchSourceAndRegeneration` means equality to the recomputed canonical digests and regenerated
formulas (no claim that SHA-256 is mathematically injective). `ReportAdmitted` is the norms extension of P0's
independent admission relation, including exact layer-leaf origins and retained bridge/choice provenance.
`reportOtherAssumptions` retains every undischarged non-background/non-layer leaf. Neither hash matching nor
an accepted certificate alone is a proof that its leaves are admitted.

Prove a companion `norms_wire_conflict_sound` from successful raw conflict-package replay: a certified
CONFLICT-FREE result entails `∀ B, BaseAdmissible D.E B → ConflictFree D.E D.T B`; a CONFLICT result contains
a typed, valid base witness and entails its negation. For a partial check, the theorem asserts only that
target's result; document CONFLICT-FREE requires all targets. Compose the complete conflict-free result with
`conflictFree_expands_all` and `norms_route_acceptance` to obtain the base-vocabulary report conclusion.
The proof follows decoder soundness → exact regeneration → binding equality → leaf admission → checker
soundness → document iff; the theorem over already-decoded formulas in 6.2 cannot replace this chain.

### 11.5 Limits

Rules ≤ 256 per document, regulated predicates ≤ 64, precedence depth ≤ 16, carve-outs ≤ 8 per rule, guard size
within `MAX_NODES`; witness search uses the existing search bounds and `MAX_EVALUATIONS`; every overflow is
`ResourceLimit` with the limit named, never a truth value.

### 11.6 Rust (P0 3.7)

Rust never elaborates norms. On the `elaborated-document` family a norm case carries the Python-generated premise
list marked `untrusted: true`; Rust evaluates and searches over it and its verdict must agree with Python's and
Lean's regenerated ones (regression evidence; the trust path is Lean).

## 12. Statement review checklist (Astra + Fable, before Lean starts)

1. `holdsCatala` / `Value` (4.3, 6.1): is the four-way case split the intended reading of exceptions and defaults?
2. `applies`, `yields`, `selects` (4.2): carve-outs as guard narrowing rather than nodes; same-sign double
   selection as overlap (the stated Catala deviation).
3. The conflict formula (5.1) over base structures after substitution, and `ConflictFree`.
4. `elab_p` in the three-clause form (4.4) and `Intended_p` of the layer (6.2): faithful, not the completed
   biconditional.
5. Prefix satisfaction in `AdmissibleOut` (own meaning plus all earlier meanings and closed pairs), typed
   `subst_sound`, local `ConflictFreeAt`, and the actual `conflictFree_expands_document` / `_all` iff over base
   structures; the W3 biconditional requirement and executable admission theorem of 11.4.
6. The profile premise as declared pairs `∀x̄. r(x̄) → m(x̄)` in Background (3.1), generalising `∀a. required(a) →
   permitted(a)`.
7. `InFragment` (7.1) and the bound in `conflict_smallModel` (7.2).
8. The English table of 2.1 and 2.4: one reading per wording; the input synonyms; `unless` as carve-out only.
9. The Cedar translation table (8) and the shape lemma `cedar_decision`.

## 13. Resolved plan deviations and implementation decisions

Both reviews explicitly accepted decisions 13.1 and 13.2 on 2026-09-26. They are the specification's resolved
semantics, with the descendant/default clarifications below; neither requires a change to a frozen P0 contract.

1. **Accepted: carve-outs narrow the guard; exceptions are nodes.** The plan lists `unless` and `except when` beside "takes
   precedence over" without saying whether `unless` carries a consequence. Reading it as a consequence-free
   carve-out matches English and keeps every tree node a Catala node with a value; the alternative (an
   exception node with the default as its value) blocks parents even when the exception's own guard fails
   (the doctor-on-Monday case) and was rejected for that reason. A carved-out node cannot itself select, but its
   subtree may still yield through a descendant (4.2, 10.1(s)). Every English carve-out paraphrase names the
   actual environment default and explains that other rules may decide (2.5).
2. **Accepted: three-clause elaboration.** The plan's `elab(p) := ∀x̄. p ↔ O_p` is satisfiable at a `P ∧ N` point, so
   "no conflict ⇔ unique expansion" would fail in one direction for intra-predicate conflicts. The three-clause
   form makes the iff exact and reduces to the plan's biconditional on conflict-free documents
   (`elab_completion`); the plan's formula stays as the reader's picture.
3. **Roles and act phrases** (3.1, 2.4) realise `required`/`permitted` as declared roles with declared duals,
   so that any act ("enforce a law") gets `must`/`must not`/`may`/`need not` wordings, Cedar's `permitted(request)`
   is a permission predicate, and plain regulated predicates remain possible. The profile premise generalises to
   declared pairs of any sorts. If both roles describe one canonical act, linkage is mandatory; unrelated acts
   with equal sorts cannot be linked (3.1).
4. **Defaults in the environment**, rendered as the legend's `By default, ...` sentence, not as a document unit:
   the completion is identity-bound like flags and definitions.
5. **Consequence arguments are exactly the situation variables** (no constants, no repeats); constants go in
   the guard. Keeps every rule on `p` over the same `x̄`, which the selection disjunctions need.
6. **One layer per regulated predicate** in DAG order (not one norms layer), because definitions interleave
   (3.5); the pair premise is an admissibility condition of the pair's later layer. Every layer's output
   admissibility includes its own meaning and full prefix satisfaction, including W3 definitions (6.1).
7. **Numbers resolve at parse time** to stable names; English references use numbers; rendering regenerates
   them. A persistent block manifest preserves names through editing/export, including duplicate-looking rules;
   bare text alone is not an identity-preserving serialization (11.2).
8. **`InvalidModel("norms")`** for a supplied regulated table, by analogy with W3's defined tables; a `P ∧ N`
   point is a false premise, not an invalid model.
9. **Rust receives the elaboration untrusted** (11.6), the only reading consistent with 3.7's "Rust never
   elaborates norms" and "a list supplied on the wire is never trusted": Rust's verdict is regression evidence.

## 14. Hand-off

W1 Lean (Opus 5.5) starts in `lean/VE/Norms/*` after this review, against the frozen `Layer` and `dependencyOrder`;
W1 Python (Sol) after W3 merges (definitions for `forbidden`, `violation`, `breach`), owning `ve/norms.py`,
`ve/surface/norms.py`, `ve/adapters/cedar.py`, `tests/test_norms*.py`, the `norms` conformance family and the two
pilots' norm units through W2's format; W8 builds `add_norm` from sections 2.5 and 2.6 (tool spec: name, act,
sign, guard, carve-outs, parents; five examples in 9.1 to 9.3). Effort as planned: spec review 2 days, Python and
adapter 5 days, Lean 5 to 7 days.

The hand-off includes the W3 prefix-admissibility requirement, the new `ve_norms_route` executable/decoder and
wire theorem, all deterministic regressions in section 10, and preservation of the English metadata protocol.
Implementation must satisfy these gates before claiming W1 acceptance; the generated suites alone are insufficient.

## 15. Contract change requests

None. The repair strengthens W1/W3 **instances** of the existing `Admissible_out` field and proves the missing
document-wide statements. The new executable and admission types extend reachability without changing
`VE.Route.Layer`, `Layer.expands`, composition, `dependencyOrder`, checker interfaces, old decoders, labels,
canonical identities or existing Route source files. Any implementation that cannot meet these requirements
must record a concrete contract change request here before proposing a frozen-contract edit.

## 16. Review response table (finding → change)

Sources: Astra [w1-spec-review-astra.final.md](../../../manage-agents/w1-spec-review-astra.final.md) and Fable
[w1-spec-review-fable.md](../../../manage-agents/reviews/w1-spec-review-fable.md), both **FIX FIRST**. Every A/B
finding is addressed below. “Regression” names a required implementation test, not a test run in this spec revision.

| Review finding | Specification change and required regression |
|---|---|
| Astra A1 — incomplete lower admissibility / missing document iff | 6.1 includes own meaning, full prefix and closed pairs in output admissibility; W3 biconditionals required. 6.2 separates local iff, pointwise base-structure document iff and universal document iff, with constructive/contrapositive proof obligations and prefix-derived `hc`. 10.1(m–p), 10.11 instantiate the frozen layers. |
| Astra A2 — binary argument reversal | 6.1 defines `tupleVal = reverse`; relation tuples stay in argument order everywhere. Completion, local/base conflict, substitution interfaces, witness and small-model statements use the correct valuation. 10.1(t) fixes disjoint state/person domains and asymmetric relation data. |
| Astra A3 — substitution/witness hypotheses | 6.2 supplies explicit prefix, well-formed formula and typed valuation; witness conclusion uses base `ConflictFree`, not local `ConflictFreeAt`; 7.2 returns a typed tuple. 10.1(u), 10.11 reject undefined/wrong-sort tuples. |
| Astra B1 — optional/mismatched act duals | 3.1 gives canonical act identity, unique roles, mandatory linkage when both roles exist, sort/act mismatch diagnostics. 10.1(v) covers unlinked must/must-not and unrelated equal-sort acts. |
| Astra B2 — contradictory English / descendant explanation | 2.1 binds `each person`; 2.6 distinguishes no-third-rule permission from the independent-forbid conflict; 4.2 says descendants can make a carved-out subtree yield. 10.1(s,w) and 10.6 are deterministic. |
| Astra B3 — Cedar runtime type errors | 8 retains runtime tags, Boolean operand checks and all-member entity checks before set membership; exact short-circuit and branch behavior. 10.2 checks errors as well as decisions, including the matching-Alice/mixed-set forbid. |
| Astra B4 — hidden stable-name round trips | 11.2 defines bound export manifests and handle-based editing, duplicate/copy/deletion rules, fresh bare-import naming and the precise round-trip law. 10.6–10.7 exercise arbitrary names and duplicate text. |
| Astra B5 — frozen decoder cannot reach norms | 11.4 adds a separate Lake executable, strict extended decoding, regeneration, original-document/inner-certificate binding and `norms_wire_acceptance` from raw JSON. 10.8 exercises the public entry point and tampering; 15 requests no frozen-contract change. |
| Fable A1 — own premises missing from output / local test wrong | 6.1–6.2 make prefix predicates independent of `Layer` construction, include each layer's own meaning, evaluate local tests in actual lower tables and derive `hc` by substitution. Definition layers must preserve their biconditionals. The actual whole-document iff replaces the quantified per-layer claim. 10.1(m–p). |
| Fable B1 — non-base premises in base certificates | 5.2 and 6.2 use `Background_base` alone after substitution; 11.4 regenerates and binds that base environment. 10.8 rejects derived symbols/unexpanded definitions in base packages. |
| Fable B2 — flagship non-binder | 2.1 uses `each person` in both rules; 10.6 tests valid binding and dangling `a person … that person`. |
| Fable B3 — wrong ambiguity paraphrase | 2.6 removes the third rule from the distinguishing situation; 10.1(w) checks forbidden/permitted, while existing (i) retains the independent-forbid conflict. |
| Fable B4 — object `every` invites wrong negation scope | 2.1 drops that synonym, keeps `each`/`any` and prescribes the rewrite; 10.6 tests acceptance/rejection under `must not`. |
| Fable B5 — exception outside parent guard / missing gates | 2.1, 2.3 and 2.5 state and illustrate independent child applicability. 10.1(r) checks Tuesday; (q) a diamond; (p) a paired-permission guard; (c,o) real Lean layer construction. |
| Fable B6 — base model passed to local predicate | 6.2 witness theorem concludes `¬ConflictFree E T M.asStructure` and failure of whole-document unique expansion; local tests require an interpreted prefix. |
| Both reviews — section 13.1 | Accepted guard-only carve-outs; 4.2 corrects descendant yielding and 2.5 requires the actual default in every paraphrase. 10.1(s), 10.6. |
| Both reviews — section 13.2 | Accepted three-clause elaboration; 4.4/6.2 retain faithfulness and reduction to the biconditional under no opposite selection. |
| Fable C1 — overlap is not redundancy | 4.2, 8 and 10 use `Overlap` without claiming logical redundancy. |
| Fable C2 — empty sorts in substructures | 7.2 states the frozen semantics' empty-sort allowance and enumeration requirement; if nonemptiness is later required, retain an existing element of a nonempty sort, never invent one in an empty sort. 10.11. |
| Fable C3 — `A doctor` not accepted grammar | 2.6 now explicitly rejects and rewrites to `Every doctor`; 10.6 verifies it. |
| Fable C4 — noncanonical pilot wording | 9.2 uses separate `Except when` sentences and the act-consistent default `a situation`; 10.4/10.6 round trips apply. |

## 17. Dated change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-26 | Draft 1 | Initial W1 statement-review specification, including zero-training English, direct semantics, three-clause elaboration, base conflict checks and proof-gated small-model claim. |
| 2026-09-26 | Draft 2 | Applied every A/B finding from both FIX FIRST reviews and the four Fable C clarifications; repaired prefix composition and the document-wide iff; typed tuple/substitution/witness statements; mandatory same-act duals; corrected English and accepted both section-13 deviations; runtime-typed Cedar translation; identity-preserving English metadata; reachable new wire admission and theorem; deterministic regression gates and this response table. Spec-only revision: frozen P0 code/contracts unchanged; proofs/tests remain implementation gates. |
