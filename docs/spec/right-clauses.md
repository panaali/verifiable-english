# Composition stage S3: structured right lines (`right-clauses@0`)

> Status: item-1 specification, draft 3 (2026-10-31; drafts 2 and 3 apply the FIX edits of the statement review,
> which converged on draft 3's edits with "the build may start once these edits are in"; change log), written from [composition-PLAN.md](composition-PLAN.md) draft 2
> (sections 2.1, 2.3 `Rel_D, gated`, 2.7, 3, S3, 5 F11 to F14, 6, 7 questions 11 and 15, 9) and from the frozen
> contracts it cites: [composition.md](composition.md) (S0: the stack, the slot, `gate`, labels, `Content`, `dispatch`,
> the English frames E9 and G8, the report contract), [rights.md](rights.md) (W2 units `right` and `right_lines`, line
> instances, `correlate`, `Lim_D`, `narrowings_complete`), [composition-s1.md](composition-s1.md) (separation, E24) and
> [composition-s2.md](composition-s2.md) (the four routes; `gatedRel` empty until S3). Read at `main` `09fca5013`:
> `lean/VE/Rights/{Tree,Correlate,Scope,Projections,Wire}.lean`, `lean/VE/Compose/{Slot,Content,Dispatch}.lean`,
> `lean/VE/Readings/{Separate,Choice}.lean`, `ve/profile_table.json`. It is the statement under the item-1 statement
> review that gates S3's Lean (`manage-agents/debates/spec-right-clauses/`). Statements and fixtures are
> implementation obligations, not claims of proofs or tests. Nothing here changes a frozen contract, a canonical
> byte or identity of a document that does not enable `right-clauses@0`, an existing theorem statement, or the answer
> of any executable on such a document. Points the plan leaves open are OPEN lines (section 11), each with what the
> build does until the DRI decides; none is decided here.

## 0. Scope, one paragraph

A rights line today is one rule `∀ bearer ∀ holder` whose content beyond its guard lives in an 80-character act
phrase or in a sort's prose description, and no field says which bearer owes which holder (plan section 1, failure
3). `right-clauses@0` is the STRUCTURE step of the stack (rank 2, between RESOLVE and SUPERPOSE): a line may carry
**clauses** (base formulas with the source bytes they account for), at most one **relation** (a declared binary base
predicate between two slots of the line, optionally **total**), and a mandatory **elided** list (the bytes of the
unit nothing accounts for). The layer's elaboration `plain` conjoins the clauses and the relation atom to the line's
guard and changes nothing else, so every rights theorem applies to the result unchanged; a total relation adds one
closed premise to the base-premise slot (`Rel_D`), appended after `Lim_D`. Profiles off, or on with no clause and no
relation, the elaboration is the identity (`plain_identity`). S3 depends on S0 only: it imports `VE.Compose.Slot`
and `VE.Compose.Content`, and nothing of `VE.Readings`.

Out of scope, by the plan: the superposed rights route and the gated `Rel_D` it needs (S2b: S3 fixes the label and
the gating statement, 4.6); any change to act phrases, to the 80-character linter, to `rights@0`'s wire, identity
or theorems, or to `correlate`; a universal surrogate for totality (plan question 11); folding clauses into a
`rights@1` (plan question 15: this specification keeps the profile the plan proposes); any coverage number.

## 1. Definitions

### 1.1 A structured line

```text
line              a rights@0 source line (rights 1.2, 3.2): kind, norm (or a power's two units), fan_out, holder_slot,
                  cites; its rule name n is its norm's name (a power line's: its liberty unit's name); its context is the argument sorts of its predicate,
                  ss = [s_0, …, s_{k-1}], slot j bound to de Bruijn variable k-1-j (rights 4.2, `atom`, `tupleVal`)
clause            (role, formula, span): role ∈ {scope, trigger, object}, rendering order and audit accounting only;
                  formula a base formula typed in the line's context; span [a, b) UTF-8 byte offsets into the pinned
                  source, a < b, inside the unit's span
relation          (pred, slots (a, b), total, cites): pred a declared binary base predicate whose argument sorts are
                  (s_a, s_b); a ≠ b, both < k; total ∈ {none, j}; cites a list of source unit ids (attribution only)
relation atom     pred(x_a, x_b): the binary atom on the variables of slots a and b, in that argument order
elided            a list of spans of the unit that neither the act phrase, a clause nor the relation accounts for;
                  mandatory under the profile, [] when nothing is left out
structured line   a line with its clauses (possibly none), its relation (possibly none) and its elided list
```

Spans of one line (its clauses' and its elided ones) are pairwise disjoint. The act phrase and the relation carry no
span; `elided` is the author's account of what is left, and the checker verifies containment and disjointness, not
that the spans cover the unit (it cannot: the act phrase has no span).

**Which lines may be structured.** A claim, liberty or immunity line without `fan_out` (rights 1.2). A `power` line
or a fan-out line may carry `elided` and nothing else (`ClauseLineShape`, section 7; OPEN-3).

### 1.2 `plain`

```text
plain guard       G_n ⊕ c_1 ⊕ … ⊕ c_m ⊕ r   left-nested: ((G_n ∧ c_1) ∧ …) ∧ r, i.e. foldl (∧) G_n [c_1, …, c_m, r],
                  c_i the clause formulas in wire order, r the relation atom when there is a relation; G_n alone when
                  there is neither
plain D           the rights document D with every structured line's norm guard replaced by its plain guard; every
                  other field of every line, right, limitation, bar, the environment and the soft block unchanged
```

`plain` is the whole elaboration (plan 2.7: "No act phrase rule changes"). `correlate` then adds the holder guard
and the limitation pack to the plain guard exactly as to any guard (rights 4.2), so the line's own guard is
`own_N = (G_n ∧ clauses ∧ r) ∧ H_R[slot(N)]`. Because the predicates, kinds, names, holder slots and act keys of every
line are unchanged, `linesOf`, `limKeys`, `condKeys` and therefore `Lim_D` are unchanged (`plain_shape`,
`plain_limPremises`, 9.3).

### 1.3 Totality and `Rel_D`

For a structured line n of right R with relation (pred, (a, b), total = j) and `o` the other slot of {a, b}:

```text
ρ_n       ∀x:s_j. H_R(x) → ∃y:s_o. pred(t_a, t_b)      t_j := x, t_o := y
          "every element of slot j's sort satisfying the holder guard is related to at least one element of the other
          slot's sort" (plan 2.7)
label     rights:relation:<n>:total                      (composition.md 1.5)
Rel_D     [ρ_n for every structured line with a total relation, in document order of the lines]
slot      clauseSlot D := Lim_{plain D} ++ Rel_D, labels Lim's then Rel's     (composition.md 1.5: Rel_D appended last)
```

`total` must be the line's holder slot (rights 1.2: the object slot of the holder sort for a claim or immunity, slot
0 for a liberty), so `s_j` is the holder sort and `H_R` is typed for it; for a total relation the head checks `H_R` over `baseEnv D` (rights 1.1 requires a base formula; rights' checker does not enforce it) (OPEN-4 records that the plan does not say
whether totality on the other slot is wanted). Rule names are unique in a rights document, so the labels are pairwise
distinct (`clauseSlot_labelled`).

### 1.4 Where the layer sits

```text
profile          right-clauses@0, wrapper of rank 2 (composition.md 1.1); sits on route rights only (composition.md 4.2,
                 step 3: `right-clauses@0 requires rights@0`, `right-clauses@0 with <b>`); the profile table rows of
                 ve/profile_table.json (slot clauses, requires rights@0, the four refusals) are already on main
head clauses     validates and strips right-clauses@0, elaborates every structured line with plain, computes Rel_D and
                 elided_bytes, then calls dispatch on the remaining list (composition.md 4.1 rule 1): the next head is
                 readings when readings@1 is enabled, else rights
```

The head hands its successor an ordinary `rights@0` document (rule 2): every structured line, in a fixed unit or in a
reading candidate's content, leaves the head as a plain `rights@0` line without the three fields. A reading
candidate's line is plained before `readings@1` sees it (STRUCTURE before SUPERPOSE, plan 2.1), so S1's admission,
interface, declaration and separation checks run on plained contents and need no change for clauses and relations
without totality. A candidate line's totality premise needs the readings layer to carry it (gated on the superposed
route, per choice on the enumerated one): until that join exists the head refuses such a document with
`RelationOnCandidate` (section 7; OPEN-1).

### 1.5 Reserved names

Under the profile the label prefix `rights:relation:` stays reserved for generated premises (composition.md 1.7); a
relation predicate obeys every author-name rule of rights 3.2 and soft-norms (no `rights__`, `soft__`, `ve__`
prefix).

## 2. The English (one reading each)

Composition.md 2.1 numbers its wordings E1 to E21 and composition-s1.md continues to E25; this specification's
wordings are RC1 to RC5 so that no number is shared. W7 registers each with S3 and each passes the all-derivations
gate before it is shown; the fidelity gate (W8) covers RC4 and RC5. No sentence here is a norm word an author can
write as content, except that RC1 and RC2 are how a structured line is written and read.

| # | Wording | The one reading | Formal content |
|---|---|---|---|
| RC1 | `<rights 2.1 line sentence up to and including its act and holder>[, where <relation instance>][, if C[ and <clause>]*][, unless U].` with `C` the line's own guard (omitted when `⊤`, in which case the list begins `if <clause>`) | The line exactly as rights 2.1 reads it, applying only where the relation holds between the two named parties and every listed condition holds. | the plain guard (1.2); `plain_guard` |
| RC2 | `<relation instance>` := `that <noun of slot a> <phrase of pred> that <noun of slot b>` | The two parties of the line in the relation the predicate declares, in its argument order. The plan's instance: "where that state is the country of that person". | the relation atom `pred(x_a, x_b)` |
| RC3 | `For every <holder>[ that H] there is at least one <noun of slot o> such that <relation instance>.` | The totality premise: every holder satisfying the holder guard stands in the relation to at least one party of the other slot's sort. VE does not say it is true; it is a proviso (E3). The plan's short form "Every person has at least one country" needs a relational noun no declaration provides, so it is not produced. | `ρ_n`, label `rights:relation:<n>:total`; RC3 is composition.md's `<totality sentence>` in E9 |
| RC4 | `This line leaves out: "<elided text>"[; "<elided text>"]*.` / `This line leaves out nothing.`; a span whose text contains "may not", a double quote (`"`) or a G6 substring (`ve__`, `rd-`, `soft__`, `rights__`) takes the form `bytes [<a>, <b>)` in place of its quotation | The quoted source bytes are part of the unit and are not formalised by this line. Nothing is claimed about them. | `elided`; `elided_bytes` (6) |
| RC5 | `These two readings differ here: <situation>. Under <assertion reading>, sentence <n> is true there, and so is every other asserted sentence checked: <citation>. Under <other reading>, this situation is ruled out, whatever is decided.` (the citation part is omitted when no fixed assertion was checked) | Used only for a mixed pair (one assertion candidate, one that is not) recorded with a `holds` probe whose witnessing side is the assertion candidate, with recorded value `true`, when the other reading has no admissible completion on the shown base. The assertion candidate's sentence and every fixed assertion the probe evaluated are true in the shown situation; under the other reading the situation is impossible. No truth value is stated for the other reading. | composition.md 2.1 "What E19 to E21 may state", case 1; `Observes … .holds` (S1) |

Slots: `<noun of slot a>` is the sort noun of the line's slot as rights 2.1 renders it (`<bearer>`, `<holder>`, or an
object's sort noun); `<phrase of pred>` is the binary predicate's registered English in the environment (the same
production a guard atom on it renders with), placed between its two arguments; when `s_a = s_b` the two nouns follow rights 2.1's guard renderer for a repeated
sort ("that person" … "the second person", rights fixture μ); in RC3, which introduces the holder first, the nouns
are `the first <sort>` for the holder slot and `the second <sort>` for slot o, whatever their slot order; `<clause>` is the clause formula
rendered by the guard renderer of rights 2.1 in the line's context ("that person", "that state"); `<elided text>` is
the elided span's source text (or, for such a span, that form); `<citation>`, `<n>`, `<situation>`, `<reading>` are
composition.md 2.1's. Order in RC1 is fixed: relation first, then the guard, then the clauses in wire order;
conjunction is commutative, and the rendering order is the reading order, not the AST order of 1.2.

**Mixed pairs in other configurations.** A mixed pair recorded with `holds` that is not RC5's case (the witnessing
side is the non-assertion candidate, or the recorded value is `false`, or the other reading has an admissible
completion) keeps composition-s1.md's E24 ("These two readings differ in a checked situation that VE cannot yet show
in words."). Such a probe's value is a conjunction over assertions that include other sentences, so no per-sentence
value is checked; RC5 states values only where the check established them (composition.md 2.2, G8).

Not wordings, and never produced: "has the right against" or any wording that names a bearer the relation does not
relate; a totality sentence as a fact ("every person has a country" without E3); "the sentence is false there" of a
non-assertion reading (composition.md 2.2); a relation instance with the arguments exchanged; a clause role word
("trigger", "scope", "object") in a rendered sentence; any generated name (`rights:relation:…`, `rd-`, `ve__`).

**Reader's checklist** (rights 2.3, extended): for every structured line, RC1; for a total relation, RC3 under every
result that used it (inside E3); RC4 for every line of a unit under the profile; for a candidate pair, the wording of
its probe (composition.md 2.3), RC5 in its case.

**Examples.** UDHR `u077` Art. 21(2) (plan F14): "Claim of right 21. Every state must give each person equal access
to public service in that state, where that state is the country of that person." (illustrative act phrase; the
translation's declared phrase is used). UDHR `u054` Art. 15(1) under its claim reading (plan F13): RC3 "For every
person there is at least one state such that that state is responsible for that person." UDHR `u039` Art. 10 (plan
F12): RC4 "This line leaves out nothing."

## 3. Wire form and identity

Under `right-clauses@0`, a line object (rights 3.2, in a `right` unit's `lines` or a `right_lines` unit, fixed or
inside a reading candidate's content) has three more keys:

```json
{"kind": "claim", "holder_slot": null,
 "norm": {"name": "remedy", "predicate": "remedy_required", "sign": true, "guard": ["top"], "unless": [], "over": []},
 "clauses": [{"role": "trigger", "span": [3541, 3635],
              "formula": ["exists", "act", ["and", ["binary", "violates_right_of", ["var", 0], ["var", 1]],
                                                   ["unary", "right_granted_by_law", ["var", 0]]]]}],
 "relation": {"predicate": "has_tribunals_competent_for", "slots": [0, 1], "total": 1, "cites": ["u035"]},
 "elided": [], "cites": {}}
```

- `elided`: mandatory on every line under the profile (`InvalidInput: elided missing on rule <n>`), a list of
  `[a, b]` spans.
- `clauses`: optional, absent or a non-empty list; each `{"role", "span", "formula"}`, all three required.
- `relation`: optional, absent or `{"predicate", "slots", "total", "cites"}`; `total` is `null` or a slot index;
  `cites` a list of source unit ids, each validated as rights' `cites` entries are (`UnknownSymbol: unit <u>`).
- Profile off: the three keys are rejected exactly as today (`fields do not match`, `VE.Bridge.displayFields`), so no
  existing document, identity or verdict moves (plan fixture F20).

**Identity.** Rights 3.5 unchanged: a unit's `meaning_id` is W1's digest over `{environment_id, ast}` with `ast` the
unit object as on the wire, so the three keys are part of it, and the profile list is part of `environment_id`. A
document that does not enable the profile has the bytes and identities it has today. The rights document hash and
every certificate bind the plained document and `Rel_D`, regenerated at every trusted site (rule 3); neither is on
the wire as authority. Under the profile the inner rights route computes its identities on `plain D` under the list
without `right-clauses@0`, and the outer report binds the full list, as the discourse wrapper does (composition.md 3).

## 4. Semantics

### 4.1 The head, in order

1. `dispatch` on the profile list (composition.md 4.2); its refusals are final.
2. Decode the document with the three keys allowed on every line object, fixed and in candidates.
3. For each structured line in document order (fixed units, then reading sets in source order, candidates by
   index): the line shape (1.1), clause typing, spans, the relation (1.1, 1.3), then the relation's `cites` (`checkCandidates` for candidates). The first
   failure is the answer (section 7).
4. If any reading candidate's line has a relation with `total` set: `RelationOnCandidate: <set>:<i>: <n>` (OPEN-1) (`checkCandidates` for candidates).
5. `plain` every structured line; compute `Rel_D` and `elided_bytes`.
6. Hand the plained document, without the three keys, to the head `dispatch` names for the list without
   `right-clauses@0`; `Rel_D` joins the slot (4.2). The rights checks (`WellFormedRights` on `plain D`, rights 4.1)
   run there with their own texts; a `ResourceLimit` from a longer guard is reported as such (`plain_wellFormed`).

### 4.2 The slot and the route

On the rights route (no reading set, or the enumerated route of composition-s2.md 1.1, where each choice's document
is set-free and S3 refuses candidate totality by step 4) the route is the S0 slot lemma at
`X := correlate (plain D)`, `P := clauseSlot D = Lim_{plain D} ++ Rel_D`: acceptance, countermodel, conflict-freedom
and exactness are `VE.Compose.slot_route_acceptance`, `slot_route_countermodel`, `slot_conflict_free`,
`slot_route_entails_iff` at that instance, with `clauseSlot_wellFormed` as their `hP`. No route theorem is restated.
With `Rel_D = []` the instance is the rights route on `plain D` (`clauseSlot_no_total`, `rights_is_slot`).

### 4.3 What the clauses and the relation do

A line applies only where its plain guard holds. Where a clause or the relation atom fails at a tuple, the line's own
guard fails, so the line does not select there and no duty or liberty follows from it at that tuple
(`clause_fails_not_selected`): "a person with no violated right is owed nothing by this line" (F11), "a state that
is not the person's country owes nothing under this line" (F14). Where they hold, the line is the rights line it was.

### 4.4 "Some bearer owes it"

Under a total relation on a duty line whose relation runs from the bearer slot 0 to the holder slot,
`relation_some_bearer` gives every holder that satisfies the holder guard a related bearer, and that bearer owes the
act wherever the line's own guard (its clauses included) holds and no narrowing mechanism of rights 4.5 is active.
It is `narrowings_complete` read contrapositively plus `ρ_n`, stated for any arity (the plan states it for a binary
claim; a binary claim is the instance `vs = [bv, hv]`).

### 4.5 Fragment

`ρ_n` is existential under a universal, so a document with a non-empty `Rel_D` leaves norms 7's fragment. The
report's single line is `fragment: no (<first reason>)` (norms 7.1; soft-norms 6.1); the slot premises are examined
after every existing reason, so the line names the first `ρ_n` in slot order, `fragment: no
(rights:relation:<n>:total)`, exactly when nothing earlier puts the document outside. Certificates and checked
witnesses still decide; completeness of the conflict check is not claimed (plan 2.7).

### 4.6 Readings (stated for S2b, not built in S3)

On the superposed rights route (S2b) a candidate line's totality premise enters the combined slot gated by its
candidate's atom: `gatedRel D` (composition-s2.md 8.3, `[]` today) becomes the concatenation, candidates in
canonical order, of `(l ++ " under " ++ <set> ++ "@" ++ <v> ++ ":" ++ <i>, χ_{s,i} → ρ)` for each `(l, ρ)` in
`relPremisesLabelled` of that candidate's structured lines. Its two facts are S0's `sat_gate_on` and `sat_gate_off`;
its fixture shape is composition.md L7, its sentence E9 with RC3. Whether S2b or the item that lifts OPEN-1 builds it
is OPEN-1.

### 4.7 Conservativity

Profile off: rejected as today. Profile on, no clause and no relation on any line: `plain D = D` (`plain_identity`),
`Rel_D = []`, so every rights verdict, status and certificate is the rights route's on the same document (rights'
seventeen fixture shapes, with `elided: []` added to each line). The only verdicts that move are on lines that opt
in, and they move only by the guard conjuncts and premises stated here.

## 5. What a result certifies

A certified result holds in every situation whose decision tables satisfy the coherence premises and whose base
satisfies `Lim_D` and every `ρ_n` (composition.md 5). Each used `ρ_n` is listed in `conditional_on` by its label and
in the English by RC3 inside E3. A countermodel satisfies the whole slot, so a situation in which some holder has no
related party is never offered as a countermodel when that line's relation is total. A relation table is never
claimed correct (plan 8): the relation is an author's predicate, and an open term with a decider when declared so.

## 6. The report

Rights 7.3's status line with composition.md 7's relation family: `… and <n> relation premises`, omitted when no
`ρ_n` was used. Residual lines: `relation_premises` (the labels used), `elided_bytes` per unit under the profile (the
sum of `b - a` over its lines' elided spans; 0 printed) and their document total, and `fragment: no (…)` as 4.5. The
reader's checklist of section 2.

## 7. Diagnostics

Raised by the head, in the order of 4.1; each text is shared by Python and Lean.

| Text | When | Kind |
|---|---|---|
| `InvalidInput: elided missing on rule <n>` | a line under the profile without `elided` | error |
| `InvalidInput: invalid elided of rule <n>` | `elided` not a list of two-natural spans | error |
| `InvalidInput: invalid clauses of rule <n>` | `clauses` is `[]` or not a list | error |
| `InvalidInput: invalid clause <i> of rule <n>` | a clause object without its three keys, a role outside the three, a span not two naturals | error |
| `InvalidInput: invalid relation of rule <n>` | a key missing or extra, `slots` not two naturals, `total` neither null nor a natural, or `cites` not a list of strings | error |
| `ClauseLineShape: <n>` | `clauses` or `relation` on a power line or a fan-out line (OPEN-3) | error |
| `InvalidInput: ill-typed clause <i> of rule <n>` | a clause formula not a base formula of the line's context | error |
| `ClauseSpan: <n>: [<a>, <b>)` | a clause or elided span empty, outside the unit's span, or overlapping another span of the line | error |
| `RelationShape: <n>` | slots equal or out of range; `pred` not a declared binary base predicate of sorts `(s_a, s_b)`; `total` set and not the line's holder slot, or not one of the two slots; `total` set and `H_R` not typed over `baseEnv D` | error |
| `UnknownSymbol: unit <u>` | a relation `cites` entry that names no source unit | error |
| `RelationOnCandidate: <set>:<i>: <n>` | a reading candidate's line with a total relation, until OPEN-1 is lifted | error (abstention: nothing in the document is checked) |
| `fragment: no (rights:relation:<n>:total)` | 4.5 | report line |

Spans are checked clauses first, then elided, in wire order; the first that is empty, outside the unit, or overlaps an
earlier span is reported (K6). `<n>` of a power line is its liberty unit's name (K11). Decoding (4.1 step 2) takes
line objects in document order. Within one, it first runs `decodeLine` on the object without the three keys (this
yields `<n>`), whose text is then the answer; then it checks `elided`, then `clauses` and each clause in order, then
`relation`; the first failure is the answer. `<n>` is the decoded line's `lineName`. A line whose `lineName` is
`none` gets none of the head's checks; rights' `IncidentShape` rejects it in step 6.

Unchanged and not the head's: `dispatch`'s texts (`UnsupportedProfile: right-clauses@0 requires rights@0`, `… with
<b>`), every rights, soft and W1 text on `plain D`, every readings text.

## 8. Lean (S3): definitions and the exact statements to prove

### 8.1 Files

`lean/VE/RightClauses/{Tree,Plain,Relation,Wire}.lean` (plan S3), `Examples.lean` (the `#guard` fixtures of section
9), `lean/RIGHT-CLAUSES.md` listing each theorem in plain words. Case kind `clauses-elaborate`: input the document,
output the plained document's canonical bytes, `clauseSlotLabelled` and `elided_bytes`, compared byte for byte
between Python and Lean (rule 3). `VE.lean` and `VE/Audit.lean` gain imports and audit entries only; the audit
allowlist is unchanged; frozen `Rights/*`, `SoftNorms/*`, `Norms/*`, `Route/*` and P0 sources are untouched.
`right-clauses@0` joins the registered list of `VE.Compose.profileTable` (and the regenerated
`ve/profile_table.json`); its rows there are unchanged, and composition.md's D29, D33, D41 and D52 keep their
expected values. No import of `VE.Readings`.

### 8.2 `Tree.lean`

```lean
import VE.Compose.Slot
import VE.Compose.Content

namespace VE.RightClauses
open VE.Rights (RightsDoc SourceLine)

inductive Role | scope | trigger | object
  deriving DecidableEq, Repr
structure Clause where
  role : Role
  formula : VE.Formula
  span : Nat × Nat
  deriving DecidableEq, Repr
structure Relation where
  pred : String
  slots : Nat × Nat
  total : Option Nat
  cites : List String
  deriving DecidableEq, Repr
/-- A structured line. `unitSpan` is the span of the unit the line is written in (1.1: clause and elided spans
    lie inside it); the plan's sketch has no such field, and the span check needs it. -/
structure CLine where
  line : SourceLine
  clauses : List Clause
  relation : Option Relation
  elided : List (Nat × Nat)
  unitSpan : Nat × Nat
  deriving DecidableEq, Repr
/-- The rights document and its structured lines, each as (right, rule name, line). -/
structure ClauseDoc where
  doc : RightsDoc
  lines : List (String × String × CLine)
  /-- Reading candidates: (set, candidate index, content, its structured lines); `[]` when there is no reading set. -/
  cands : List (String × Nat × VE.Compose.Content × List (String × String × CLine))

/-- The rule name of a line; a power's is its liberty unit's name. -/
def lineName (S : SourceLine) : Option String := (S.norm <|> S.liberty).map (·.name)
/-- The argument sorts of a line's predicate (its context, slot order). -/
def lineSorts (E : VE.SoftNorms.SoftDoc) (S : SourceLine) : List String :=
  (S.norm.map (fun N => VE.SoftNorms.sortsOf E N.pred)).getD []
/-- The base vocabulary clauses and relations are typed in. -/
def baseEnv (D : ClauseDoc) : VE.Environment := VE.Norms.envAt D.doc.soft.base 0
end VE.RightClauses
```

### 8.3 `Plain.lean`

```lean
namespace VE.RightClauses
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines holderSlot sortsOf lineAct limPremisesLabelled
  limPremises WellFormedRights validateRights correlate)

/-- The relation atom over a context of `k` slots: slot j is variable k-1-j. -/
def relAtom (k : Nat) (rel : Relation) : VE.Formula :=
  .binary rel.pred (.var (k - 1 - rel.slots.1)) (.var (k - 1 - rel.slots.2))
/-- The plain guard (1.2): left-nested conjunction of the guard, the clauses in order, then the relation atom. -/
def plainGuard (k : Nat) (G : VE.Formula) (L : CLine) : VE.Formula :=
  (L.clauses.map (·.formula) ++ (L.relation.map (relAtom k)).toList).foldl .and G
/-- One source line through its entry, if any: only the norm's guard changes. -/
def plainSource (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String) (S : SourceLine) :
    SourceLine :=
  match cl.find? (fun x => x.1 == R && some x.2.1 == lineName S) with
  | some x => { S with norm := S.norm.map (fun N => { N with guard := plainGuard (lineSorts E S).length N.guard x.2.2 }) }
  | none => S
def plain (D : ClauseDoc) : RightsDoc :=
  { D.doc with
    rs := D.doc.rs.map (fun R => { R with lines := R.lines.map (plainSource D.doc.soft D.lines R.name) })
    sourceOrder := D.doc.sourceOrder.map (·.map (fun RS => (RS.1, plainSource D.doc.soft D.lines RS.1 RS.2))) }
/-- A reading candidate's content through its own structured lines (1.4); other contents unchanged. -/
def plainContent (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) : VE.Compose.Content → VE.Compose.Content
  | .right R => .right { R with lines := R.lines.map (plainSource E cl R.name) }
  | .rightLines r ls => .rightLines r (ls.map (plainSource E cl r))
  | c => c

/-- The guard of the source line whose rule is `n` (⊤ when there is none). -/
def guardOf (D : RightsDoc) (n : String) : VE.Formula :=
  ((sourceLines D).findSome? (fun RS => RS.2.norm.filter (·.name == n))).elim .top (·.guard)
/-- The holder guard `H_R` (⊤ for an unknown right). -/
def holderGuardOf (D : ClauseDoc) (R : String) : VE.Formula :=
  ((VE.Rights.rightOf D.doc R).map (·.guard)).getD .top

/-- 1.1, 1.3, 7: shape, typing, spans, relation and cites of every entry; the entries name distinct rules, each the
    rule of exactly one source line of `D.doc`, of the right the entry names, and `L.line` is that source line;
    and, for a total relation, `(holderGuardOf D R).check (baseEnv D) [holder]`. -/
def checkClauses (D : ClauseDoc) : Except String Unit
def WellFormedClauses (D : ClauseDoc) : Bool := match checkClauses D with | .ok () => true | .error _ => false
/-- 4.1 steps 3 and 4 over `D.cands`, in order. First the checks of 1.1, 1.3 and 7 on each candidate's entries
    against its content's lines, each span against its own `unitSpan`, types over `baseEnv D`. The right (holder
    sort, `H_R`) is the candidate's own when its content is `.right`, else `D.doc`'s; unit ids are `D.doc`'s. Then
    `RelationOnCandidate` for the first total relation. -/
def checkCandidates (D : ClauseDoc) : Except String Unit

/-- Identity when unused (composition.md 4.1 rule 5). No well-formedness hypothesis: `plainSource` keeps the
    source line's own norm. -/
theorem plain_identity (D : ClauseDoc) (h : ∀ x ∈ D.lines, x.2.2.clauses = [] ∧ x.2.2.relation = none) :
  plain D = D.doc
theorem plainContent_identity (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine))
    (h : ∀ x ∈ cl, x.2.2.clauses = [] ∧ x.2.2.relation = none) (c : VE.Compose.Content) : plainContent E cl c = c
/-- Declared names, kinds and needs are unchanged, so S1's interface and cross-set checks see the same names. -/
theorem plainContent_declared (E) (cl) (c : VE.Compose.Content) :
  (plainContent E cl c).declared = c.declared ∧ (plainContent E cl c).kind = c.kind ∧
  (plainContent E cl c).needs = c.needs

/-- Everything but guards is unchanged. -/
theorem plain_shape (D : ClauseDoc) :
  (plain D).soft = D.doc.soft ∧ (plain D).rights = D.doc.rights ∧ (plain D).limits = D.doc.limits ∧
  (plain D).bars = D.doc.bars ∧ (plain D).sourceUnits = D.doc.sourceUnits ∧
  (linesOf (plain D)).map (fun RN => (RN.1, RN.2.kind, RN.2.ikind, RN.2.node.name, RN.2.node.pred, RN.2.bearer)) =
    (linesOf D.doc).map (fun RN => (RN.1, RN.2.kind, RN.2.ikind, RN.2.node.name, RN.2.node.pred, RN.2.bearer)) ∧
  ∀ RN ∈ linesOf (plain D), ∃ RN' ∈ linesOf D.doc, RN'.1 = RN.1 ∧ RN'.2.node.name = RN.2.node.name ∧
    holderSlot (plain D) RN.2 = holderSlot D.doc RN'.2 ∧ sortsOf (plain D) RN.2 = sortsOf D.doc RN'.2 ∧
    lineAct (plain D) RN.2 = lineAct D.doc RN'.2
theorem plain_limPremises (D : ClauseDoc) : limPremisesLabelled (plain D) = limPremisesLabelled D.doc

/-- The plain guard, read (1.2). -/
theorem plain_guard (D : ClauseDoc) (h : WellFormedClauses D = true) (R n : String) (L : CLine)
    (hL : (R, n, L) ∈ D.lines) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
  (guardOf (plain D) n).denote S ρ ↔
    (guardOf D.doc n).denote S ρ ∧ (∀ c ∈ L.clauses, c.formula.denote S ρ) ∧
    (∀ rel, L.relation = some rel → (relAtom (lineSorts D.doc.soft L.line).length rel).denote S ρ)

/-- Rule 2 (source in, same kind out): the only new way the successor's check can fail is a resource limit, since
    the plain guard adds base conjuncts typed in the line's context and changes no name, predicate, edge or
    precedence. -/
theorem plain_wellFormed (D : ClauseDoc) (h : WellFormedClauses D = true) (h0 : WellFormedRights D.doc = true) :
  WellFormedRights (plain D) = true ∨
    ∃ e, validateRights (plain D) = .error e ∧ "ResourceLimit: ".isPrefixOf e = true
end VE.RightClauses
```

### 8.4 `Relation.lean`

```lean
namespace VE.RightClauses
open VE.Norms (Sat tupleVal)
open VE.Rights (RightsDoc Line linesOf holderSlot sortsOf dutyKind ownGuard narrowings NarrowsAt owes SelectsRN
  WellFormedRights correlate limPremises limPremisesLabelled)
open VE.SoftNorms (soften)
universe u

/-- ρ_n (1.3), for total slot `j`; `o` is the other slot. Inside: variable 0 is y (slot o), variable 1 is x (slot j). -/
def totalF (D : ClauseDoc) (R : String) (L : CLine) (rel : Relation) (j : Nat) : VE.Formula :=
  let ss := lineSorts D.doc.soft L.line
  let o := if rel.slots.1 = j then rel.slots.2 else rel.slots.1
  let t := fun k => if k = j then VE.Term.var 1 else VE.Term.var 0
  .all (ss.getD j "") (.implies (holderGuardOf D R) (.ex (ss.getD o "") (.binary rel.pred (t rel.slots.1) (t rel.slots.2))))
def relPremisesLabelled (D : ClauseDoc) : VE.Compose.Labelled :=
  D.lines.filterMap (fun x => x.2.2.relation.bind (fun rel => rel.total.map (fun j =>
    ("rights:relation:" ++ x.2.1 ++ ":total", totalF D x.1 x.2.2 rel j))))
def relPremises (D : ClauseDoc) : List VE.Formula := VE.Compose.Labelled.formulas (relPremisesLabelled D)
def clauseSlotLabelled (D : ClauseDoc) : VE.Compose.Labelled := limPremisesLabelled (plain D) ++ relPremisesLabelled D
def clauseSlot (D : ClauseDoc) : List VE.Formula := VE.Compose.Labelled.formulas (clauseSlotLabelled D)

theorem clauseSlot_eq (D : ClauseDoc) : clauseSlot D = limPremises (plain D) ++ relPremises D
theorem clauseSlot_labelled (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true) :
  VE.Compose.Labelled.wellLabelled (clauseSlotLabelled D) = true
/-- The hP of every slot theorem at this instance (4.2). -/
theorem clauseSlot_wellFormed (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true) :
  VE.Compose.SlotWellFormed (correlate (plain D)) (clauseSlot D)
/-- No total relation: the slot is Lim_D and the route is the rights route on plain D (rights_is_slot). -/
theorem clauseSlot_no_total (D : ClauseDoc) (h : ∀ x ∈ D.lines, ∀ rel, x.2.2.relation = some rel → rel.total = none) :
  clauseSlot D = limPremises (plain D)

/-- 4.3: where a clause or the relation fails at a tuple, the line does not select there. -/
theorem clause_fails_not_selected (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (N : Line) (hN : (R, N) ∈ linesOf (plain D))
    (hn : N.node.name = n) (S : VE.Structure.{u}) (vs : List S.Carrier) (typed : VE.TupleTyped S (sortsOf (plain D) N) vs)
    (hf : (∃ c ∈ L.clauses, ¬ c.formula.denote S (tupleVal vs)) ∨
          (∃ rel, L.relation = some rel ∧ ¬ (relAtom (sortsOf (plain D) N).length rel).denote S (tupleVal vs))) :
  ¬ SelectsRN (plain D) S (tupleVal vs) N

/-- 4.4: "some bearer owes it". Under ρ_n every holder satisfying the holder guard has a related bearer, and that
    bearer owes the act wherever the line's own guard holds and no narrowing mechanism is active. -/
theorem relation_some_bearer (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (N : Line) (hN : (R, N) ∈ linesOf (plain D))
    (hn : N.node.name = n) (hk : dutyKind N = true) (rel : Relation) (hr : L.relation = some rel)
    (ht : rel.total = some (holderSlot (plain D) N)) (hs : rel.slots = (0, holderSlot (plain D) N))
    (S : VE.Structure.{u}) (hS : Sat S (relPremises D))
    (sh : String) (hsh : (sortsOf (plain D) N)[holderSlot (plain D) N]? = some sh)
    (hv : S.Carrier) (hd : S.domain sh hv) (hH : (holderGuardOf D R).denote S [hv]) :
  ∃ bv, (∃ sb, (sortsOf (plain D) N).head? = some sb ∧ S.domain sb bv) ∧ S.relation rel.pred [bv, hv] ∧
    ∀ vs, VE.TupleTyped S (sortsOf (plain D) N) vs → vs.head? = some bv →
      vs[holderSlot (plain D) N]? = some hv →
      (ownGuard (plain D) N).denote S (tupleVal vs) →
      (¬ ∃ m ∈ narrowings (plain D) N, NarrowsAt (plain D) S (tupleVal vs) N m) →
      owes (plain D) S N vs
end VE.RightClauses
```

Notes for the review. Departures from the plan's sketch (plan S3), each needed to make the statement well typed or
true: `relAtom` takes the arity, since a slot's variable depends on it; `plain_identity` needs no well-formedness
because `plainSource` keeps the source line's own norm; `plain_wellFormed` concludes "well-formed or a resource
limit", because a longer guard can exceed the 10,000-node budget W1 enforces (`Norms/Tree.lean`), which the
sketch's unconditional conclusion would deny; `relation_some_bearer` adds `hw` (the sketch has no rights hypothesis)
(it is what `narrowings_complete` needs), the holder's sort and domain (`hsh`, `hd`; the totality premise
quantifies over a sort, and a carrier element outside it gets nothing), the holder guard's valuation as the list
`[hv]` (`VE.Valuation S` is `List S.Carrier`), concludes the bearer's sort membership, and drops the sketch's
binary restriction (a binary claim is the instance). `hs` fixes the relation as bearer-to-holder in that argument
order; RC2 renders that order.

### 8.5 `Wire.lean`

The decoder of 3: `decodeCLine` beside `VE.Rights.Wire.decodeLine`, which it calls on the object without the three
keys (so a line's own fields are decoded by the frozen decoder, unchanged); `decodeClauseDoc` builds `ClauseDoc` with
each entry's `unitSpan` from its unit; `elaborate` is `clauses-elaborate` (8.1). Statements:

```lean
/-- With the three keys absent from every line, the head decodes what the rights route decodes under the list
    without right-clauses@0 (`stripProfile`), and every entry is unstructured. -/
theorem decode_unstructured (environment document : Lean.Json) (D : ClauseDoc)
    (h : decodeClauseDoc environment document = .ok D) (hk : NoClauseKeys document)
    (src : VE.Rights.Wire.RightsSource)
    (hs : VE.Rights.Wire.decodeRightsSource (stripProfile environment) (stripElided document) = .ok src) :
  src.D = D.doc ∧ ∀ x ∈ D.lines, x.2.2.clauses = [] ∧ x.2.2.relation = none
/-- The elaborated output carries none of the three keys and decodes under rights@0 to plain D. -/
theorem elaborate_plain (environment document : Lean.Json) (D : ClauseDoc)
    (h : decodeClauseDoc environment document = .ok D) (hw : WellFormedClauses D = true)
    (hset : NoReadingSets document)
    (hp : WellFormedRights (plain D) = true) :
  ∃ src, VE.Rights.Wire.decodeRightsSource (stripProfile environment) (elaborateJson D document) = .ok src ∧
    src.D = plain D
```

`decodeRightsSource` is the existing decoder of the rights route (`lean/VE/Rights/Wire.lean`); it returns only
well-formed documents (its `wf` field), hence `hp`. `NoClauseKeys` says no line object has `clauses` or `relation`;
`stripElided` removes the mandatory `elided` key; `stripProfile` removes `right-clauses@0` from the environment's
profile list; `elaborateJson` writes every line through `plainSource`'s guard, writes each candidate's content
through `plainContent`, and drops the three keys. `decodeClauseDoc` fills `cands` (`[]` without reading sets);
`NoReadingSets` says the document has no reading set, which the rights decoder does not accept.

### 8.6 What is not claimed

No theorem that a relation table, a clause or an elided list is correct or complete; no claim that `elided` covers
the unit; no completeness of the conflict check once `Rel_D` is non-empty; nothing about reading candidates' totality
(OPEN-1) or the superposed rights route (S2b); no change to `correlate`, act phrases or any rights statement.

## 9. Acceptance fixtures for item 1

Deterministic, hand-derived; none executed. A builder who finds an expectation wrong reports it against this
section. Lean fixtures are `#guard` lines of `lean/VE/RightClauses/Examples.lean`; Python fixtures
`tests/test_right_clauses.py`; the case kind compares the two.

### 9.1 Small documents

On `lean/VE/Rights/Examples.lean`'s environment (one state `Texas`, persons `Ann`, `Bob`) extended by the base
predicates `country_of(state, person)` and `charged(person)`; right `r21`, holder `person`, guard `⊤`, one claim line
`equal-access` on `public_service_access_required(state, person)`, obligation `+`, guard `⊤`; unit span `[0, 100)`.

| # | Input | Expected |
|---|---|---|
| K1 | no clause, no relation, `elided: []` | `plain D = D.doc` (`plain_identity`); `clauseSlot D = limPremises D.doc = []`; output bytes equal the rights document's |
| K2 | relation `country_of`, slots `[0, 1]`, total null | plain guard `.and .top (.binary "country_of" (.var 1) (.var 0))`; `Rel_D = []`; on the model `country_of = {(Texas, Ann)}`: the line selects at (Texas, Ann), not at (Texas, Bob) (`clause_fails_not_selected`) |
| K3 | K2 with total 1 | `relPremisesLabelled = [("rights:relation:equal-access:total", ∀x:person. ⊤ → ∃y:state. country_of(y, x))]`; on K2's model `backgroundValidP … (clauseSlot D)` is false (Bob has no country); with `(Texas, Bob)` added it is true, and `relation_some_bearer` gives Texas for Bob; report `fragment: no (rights:relation:equal-access:total)` |
| K4 | clause `trigger`, formula `charged(var 0)`, span `[10, 20)`, elided `[[30, 40]]` | plain guard `.and .top (.unary "charged" (.var 0))`; `elided_bytes = 10`; RC4 quotes bytes 30 to 40 |
| K5 | K4 with clause span `[90, 110)` | `ClauseSpan: equal-access: [90, 110)` |
| K6 | K4 with elided `[[15, 25]]` | `ClauseSpan: equal-access: [15, 25)` (overlaps the clause) |
| K7 | clause formula `charged(var 1)` (var 1 is the state) | `InvalidInput: ill-typed clause 0 of rule equal-access` |
| K8 | relation slots `[1, 1]`; then `[0, 1]` with total 0 | `RelationShape: equal-access` both times (total not the holder slot) |
| K9 | line without `elided` | `InvalidInput: elided missing on rule equal-access` |
| K10 | profile off, K2's line | today's `fields do not match` text; nothing else changes |
| K11 | relation on a power line (rights fixture ε) | `ClauseLineShape: <its liberty rule name>` |
| K12 | K3's line as candidate 1 of a reading set beside an unstructured candidate 0, `readings@1` on | `RelationOnCandidate: <set>:1: equal-access` (OPEN-1); with total null instead, the head plains the candidate and readings receives `plainContent` of it |
| K13 | K3, `Lim_D` of `gamma` (limitation 29) added to the document | `clauseSlotLabelled = limPremisesLabelled (plain D) ++ relPremisesLabelled D`, the limitation labels first; `plain_limPremises` holds by `#guard` on the formula lists |
| K14 | K3 with the right's guard an atom on an added regulated `person` predicate | `RelationShape: equal-access` |
| K15 | K9 with `clauses: []` | `InvalidInput: elided missing on rule equal-access` |

### 9.2 The plan's fixtures (composition.md 10.5: F11 to F14 are this specification's)

| # | Unit | Input | Expected |
|---|---|---|---|
| F11 | UDHR `u035` [3469, 3637) Art. 8 | claim with the trigger clause of 3 for "for acts violating the fundamental rights granted him by the constitution or by law", span [3541, 3635); relation `has_tribunals_competent_for`, slots [0, 1], total 1, cites `u035` | `elided: []`; the clause and the relation atom are in the guard (`plain_guard`); in a situation where the person has no violated right, the line does not select at any tuple of that person (`clause_fails_not_selected`); the totality premise is in the slot and listed by label when used |
| F12 | UDHR `u039` [3734, 3935) Art. 10 | scope clause "in the determination of his rights and obligations and of any criminal charge against him"; "in full equality" as a clause over the open term `full_equality` | both clauses in the guard with their spans; `elided: []`; the unit OPEN through the open term (its decider decides `full_equality`) |
| F13 | UDHR `u054` [5239, 5284) Art. 15(1) | S3's share: the claim reading alone, as a set-free document: claim with relation `responsible_for`, slots [0, 1], total 1 | `relation_some_bearer` gives a responsible state per person; a two-state situation (one person, `responsible_for` only with the first state) is a model, and in it the second state owes nothing under this line while the unscoped claim "every state must grant" would have it owe (the separation F13 names, run by S1's `separates` once the set is admitted). The mixed-kind set itself, the gated premise `χ_claim → ρ`, and G8 wait for OPEN-1 |
| F14 | UDHR `u077` [6861, 6938) Art. 21(2) "in his country" | set {claim with relation `country_of` (slots [0, 1], total null), the same claim without it} | admitted through S1 on plained candidates; separated by a situation with a state that is not the person's country (an `outcome` probe at that pair: under the relation reading no line selects, under the other the duty does), worded by composition.md E19 |
| G8 | composition.md 10.4 | F13's mixed pair recorded with `holds` | RC5's case: the assertion reading's sentence and the fixed assertions checked are true; the claim reading "is ruled out, whatever is decided"; never E14, E21 or "suppose". Checked when OPEN-1 is lifted (the claim reading's lack of a completion comes from its totality premise, which S1's `Achieves` sees only through the join) |

### 9.3 Regression and pilots

- Rights' seventeen fixture shapes with the profile on and `elided: []` on every line: elaboration, verdicts and
  statuses equal the profile-off ones (`plain_identity`); with the profile off, byte-identical (F20).
- `clauses-elaborate` differential: Python and Lean outputs equal on K1 to K15, F11, F12, F14 (K12 also by `#guard`
  on `checkCandidates` and `plainContent`, F14 by `#guard` on `plainContent`).
- UDHR rerun: every unit under the profile reports `elided_bytes`; the audit's seven units (`u035`, `u039`, `u041`,
  `u046`, `u054`, `u077`, `u033b`) are re-audited; `u076` and `u108` are re-attempted with clauses (plan section 6).
- English: RC1 to RC5 each with one instance (RC3 also with `s_a = s_b` and slot o before the holder slot) through W7; G6 and G9 of composition.md for every rendered sentence
  (both unconditional, composition.md 13.20).

## 10. Limits, regeneration, Python, Rust

Clauses add AST nodes to guards, counted in W1's 10,000-node budget on `plain D` (`ResourceLimit: AST exceeds 10,000
nodes`); no new limit. `plain`, `Rel_D` and `elided_bytes` are regenerated from the decoded units at every trusted
site. Python: `ve/right_clauses.py` decodes, checks, plains and renders; its `clauses-elaborate` output is compared
with Lean's; Lean is the authority. Rust evaluates the regenerated formulas marked `untrusted: true`, as for every
stack layer (plan question 12).

## 11. OPEN lines (for the DRI; not decided here)

- **OPEN-1. Totality on a reading candidate's line.** The plan puts a candidate's `ρ` into the combined slot gated
  (2.3, 2.7, F13), and composition-s2.md leaves `gatedRel` empty "until S3"; but rights documents with
  content-bearing sets stay on the enumerated route until S2b, and neither the readings `Doc` nor S0's `Content`
  carries a relation premise, so neither S1's `Achieves` nor S2's per-choice slot can see one without a change to
  `VE.Readings`, which S3 does not import. Undecided: whether S3 makes that join (a readings `Doc` field or a
  `Content` extension, S1's admissibility with the candidate's `ρ`, the enumerated route's per-choice slot), or S2b
  does, or a separate item. Until then: `RelationOnCandidate` (7), F13's set and G8 wait, clauses and non-total
  relations on candidates work.
- **OPEN-2. Separation with clause-bearing candidates.** S1 separates plained candidates (1.4); a separating
  situation that exists only because a clause is false there is reported by S1's wordings like any other. Whether
  the IDE should name the clause ("under reading 1 the line does not apply here because …") is not in the plan.
  Until then: S1's wordings unchanged.
- **OPEN-3. Power and fan-out lines.** The plan's example and fixtures are claims; it does not say whether a clause
  on a power applies to both units, or how a clause is typed on a fan-out line whose slot-0 sort differs per bearer
  sort. Until then: `ClauseLineShape`; `elided` is still allowed (and required) there.
- **OPEN-4. Totality on a non-holder slot.** Plan 2.7 defines totality "satisfying the holder guard", which only
  types on the holder slot. Until then: `total` must be the holder slot (`RelationShape`).
- **OPEN-6. Interface value under profile-composition.** If profile-composition's PC-3 (AR-10 `interface` slot)
  merges first, `right-clauses@0`'s row needs an `interface` value; the plan predates it. Until then: S3 adds the
  name to the registry only, rows unchanged; whichever merges second sets the value (precedent: plan question 13).

## 12. Statement review checklist

1. Definitions (1): the structured line, `plain`, `ρ_n`, the slot order `Lim_D ++ Rel_D` against composition.md 1.5;
   the context and de Bruijn convention against rights 4.2 (`atom`, `holderConj`, `tupleVal`).
2. `plain` (8.3) leaves names, predicates, kinds and act keys unchanged (`plain_shape`, `plain_limPremises`);
   `plain_identity` without a hypothesis; `plain_wellFormed`'s disjunction: does any non-limit check of
   `validateRights` read a guard in a way a base conjunct could break?
3. `totalF` (8.4) against plan 2.7's sentence, variable by variable; `relPremisesLabelled`'s labels; why total must
   be the holder slot (OPEN-4).
4. `relation_some_bearer` against `narrowings_complete` (`Rights/Scope.lean`) and `owes` (`Rights/Projections.lean`);
   each departure from the plan's sketch (8.4 notes).
5. `clause_fails_not_selected`: that `SelectsRN` implies the own guard holds at the tuple.
6. The head (4.1) and its order; rule 2's output kind; candidates plained before readings; `RelationOnCandidate` as
   a named abstention (rule 6) while OPEN-1 stands.
7. Wire and identity (3) against rights 3.2 and 3.5 and composition.md 3; profile-off rejection unchanged.
8. The English (2): one reading for RC1 to RC5; RC5 against composition.md 2.1 case 1 and G8; E24 for the other
   mixed configurations; the non-wordings.
9. Diagnostics (7) and fixtures (9), each derived by hand from 1, 4 and 8 before reading the expected column.
10. The OPEN lines (11): each is a real gap in the plan, and its interim behaviour is conservative.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-31 | Draft 1 | First statement specification of S3 from plan draft 2 and S0 (composition.md draft 3): the structured line, `plain`, `Rel_D` and its slot, the head, wire and identity, five wordings, diagnostics, `VE.RightClauses` with eleven theorem statements, fixtures K1 to K13 and the plan's F11 to F14 and G8, six OPEN lines. No code, Lean or frozen contract changes. |
| 2026-10-31 | Draft 2 | The statement review's FIX edits (`manage-agents/debates/spec-right-clauses/`, rounds 1 and 2, union of both seats' lists): E1 `H_R` checked over `baseEnv D` for a total relation (1.3, 7 `RelationShape`, `checkClauses`, K14); a power line's rule name is its liberty unit's (`lineName`, 1.1); candidates: `ClauseDoc.cands`, `checkCandidates`, `elaborateJson` through `plainContent`, `elaborate_plain` under `NoReadingSets`, 4.1 steps 3 and 4, 9.3; E3 RC4's byte-range form for "may not" and G6 substrings, OPEN-5 deleted (decided by composition.md 13.20); E4 three `InvalidInput` rows and the span order; E5 the u039 RC1 example dropped; E6 the 8.4 note; RC2's nouns for two slots of one sort (rights fixture μ; the Astra seat's round 2, in place of an OPEN-7). |
| 2026-10-31 | Draft 3 | The recheck's converged FIX edits (`manage-agents/debates/spec-right-clauses/`, recheck rounds 1 and 2, both seats CONVERGED): A `checkCandidates (D : ClauseDoc)` with the right from the content or `D.doc` and unit ids from `D.doc`; B RC4's byte form also for a double quote, written `bytes [<a>, <b>)`; C the decode order within a line object (`decodeLine` first, then `elided`, `clauses`, `relation`), `<n>` as the decoded `lineName`, section 7's rows reordered to 4.1's order, K15; RC3 names two same-sort slots `the first <sort>` (holder) and `the second <sort>` (slot o), with its 9.3 instance. |
