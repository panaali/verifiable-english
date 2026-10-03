# Composition stage S2: superposed verdicts across readings (`readings@1`, part B), milestone S2a

> Status: item-1 specification, draft 5 (2026-10-03: the DRI rulings on the S2a Lean report applied, see the
> change log), written from [composition-PLAN.md](composition-PLAN.md)
> draft 2 (its sections 2.1, 2.3, 2.5 and 2.6, its S2 section, its fixtures and its open questions 1, 2, 5, 6, 9, 13
> and 16) through the pointer plan [composition-S2-PLAN.md](composition-S2-PLAN.md) draft 5, which records the
> converged Astra + Fable design debate (`manage-agents/debates/design-compose-s2/{astra,fable}.md`, CONVERGED after
> round 3; the Astra seat was held by Sol xhigh as the recorded cross-family stand-in) and the edits of it that bind
> S2. Draft 2 applied the converged Astra + Fable statement review of draft 1
> (`manage-agents/debates/compose-s2-spec/{astra,fable}.md`, CONVERGED after round 2 on FIX: five corrections, listed
> in the change log; the Astra seat's round 1 is recorded as held by Sol xhigh) and nothing else. Draft 3 applied the
> three wording corrections of the confirmation round on draft 2 (`manage-agents/compose-s2-p3ver1.final.md`: FAIL on
> three statement-level claims, 1.1's route order, 7's decoder claim and M17(a), with every definition confirmed as
> the requested repair) and nothing else. Draft 4 applies the one correction of the confirmation round on draft 3
> (`manage-agents/compose-s2-p3ver2.final.md`: 7's decoder correction and M17(a) confirmed; FAIL on one statement,
> the route choice of 1.1 and 4.1 step 2, which evaluated `superposable D` on the rights chain) and nothing else: no
> definition, theorem statement or fixture value changed. It is the
> statement under the Astra + Fable item-1 review that gates S2's Lean (PLAN-EXPAND2 rule 10): a draft alone opens
> nothing, and the build opens on the PASS of the confirmation round on draft 4, scoped to the edited passages.
> Its item is **S2a**: superposition on the soft and norms chains, the enumerated fallback on
> every chain; section 12 says what S2b inherits and does not specify it. **Frozen inputs**: composition.md draft 3
> (the stack contract, `dispatch`, the slot, `gate`, the labelled slot, `Content`, the wordings E1 to E21, the label
> families of its 1.5 and the texts of its section 8) and `lean/VE/Compose/{Slot,Dispatch,Content}.lean` as merged;
> composition-s1.md draft 2 with its review, recheck and loop fixes (documents, candidates, `one`, `free`, `build`,
> source keys, situations, `separates`, the wordings E22 to E25) and `lean/VE/Readings/{Doc,Separate,Lines,Wire,Run}.lean`
> as merged. This file instantiates them and changes no statement of them (8.1: `Wire.lean` and `Run.lean` gain
> S2a's case kinds additively). Sections 1, 4 and 8 are the statements under review;
> section 14 lists every point where this draft chose between readings of the plan, and the three places where the
> plan's S2 sketch had to be repaired to be true or well typed (14.3, 14.4, 14.6). Theorem statements and fixtures are
> implementation obligations, not claims of completed proofs or tests. Every expected value of section 9 was derived
> by reading the sources; none has been executed. Inputs: the plan; composition.md; composition-s1.md and
> [composition-s1-measured.md](composition-s1-measured.md); [document.md](document.md) (W2); [norms.md](norms.md)
> (W1); [soft-norms.md](soft-norms.md); [rights.md](rights.md); [discourse.md](discourse.md) 1.5; and, read at
> `119e2f8a`, `ve/readings.py`, `ve/readings_route.py`, `ve/readings_s1.py`, `ve/document.py`, `ve/limits.py`,
> `lean/VE/{Syntax,Semantics,Finite}.lean`, `lean/VE/Norms/{Basic,Tree}.lean`,
> `lean/VE/SoftNorms/{Tree,Soften,Semantics,Coherence}.lean`, `lean/VE/Rights/{Tree,Correlate,Route}.lean`,
> `lean/VE/Route/Readings.lean`, `lean/VE/Compose/Slot.lean`, `lean/VE/Readings/*.lean`. Nothing here changes a
> frozen contract, a canonical byte, an identity or an existing theorem statement, or the answer of any executable on
> a document that does not turn `readings@1` on.

## 0. Scope, one paragraph

After S1 a content-bearing reading set is admitted in its document, but every verdict that depends on it is UNKNOWN
("superposition pending"): the readings are checked for separation and nothing else. S2a gives such a document its
verdicts across readings. On the soft and norms chains it builds **one superposed document** `sup D`: every
candidate of every open set is in it, guarded by a choice atom over one fresh sort, one constant and ⌈log₂ k⌉ bit
predicates per set; a candidate's rule, its sufficient exception conditions and its assertion are gated, its
generated predicates are qualified and silenced under every choice that does not take it, and the couplings and
narrowings become closed premises. All of this enters the lower route through the base-premise slot of S0 as
`Choice_D`, so every route theorem is the slot lemma at `P := Lim_D ++ Choice_D` and no route theorem is restated.
"Under every reading" is then one certificate, "under this reading" one certificate with that reading's atoms assumed,
a countermodel names the reading its atoms encode, and `superpose_faithful` with `base_down` and `base_up` say that
this is exactly the per-choice semantics of rights 6.3. Where superposition is unavailable (a cycle across candidates,
a size limit, or the precedence leak of 1.8), and on the rights chain until S2b, the route enumerates the compatible
complete choices up to 64 and checks each choice's own document with the lower route, UNKNOWN beyond. What it buys
on the pilots is measured, not predicted (11).

In this specification: definitions (1), the English (2), wire and identity (3), the semantics (4), what a superposed
verdict certifies (5), the report (6), diagnostics (7), the Lean definitions and every theorem as a statement (8),
the acceptance fixtures (9), limits, regeneration, Python and Rust (10), the measured unlock (11), what S2b inherits
(12), the review checklist (13), the resolved choices (14).

Out of scope, by the plan and by the frozen inputs: separation and admission of a set (S1, unchanged); the rights
case of `superpose_faithful`, the `lim`, `cond` and `aimed` quiescence, the copies of a fixed `right_lines` unit, the
bar axis and E20 (S2b, section 12); `Rel_D` (S3: `gatedRel` is empty here); constraints between readings (they are
recorded in the discourse manifest, which reaches the chain in S4: the `constraint:<n>` family is defined and no
S2a document has one); a claim graph beside a content-bearing set (14.10: today's handling stays); the `fill`
instance of `norm-defaults@0` (4.10: S1's abstention stays); any coverage number.

## 1. Definitions

### 1.1 Where S2a applies: the four routes of a `readings@1` document

Composition-s1.md's head `readings` admits the document (its 4.1) and hands every other case to the route `dispatch`
names for the profile list without `readings@1` (composition.md 4.2). S2a adds what the head does for the verdicts
of a document with at least one content-bearing set, chosen by the first row that applies:

```text
W2            no open set is content-bearing                       W2's route verbatim, as today (S1 4.9); nothing below
                                                                   is built for it
pending       some open set has a pending candidate (S1 1.2)       every verdict across readings is UNKNOWN with today's
                                                                   reason `non-assertion reading elaboration pending`
abstention    norm-defaults@0 in the list                          S1's UnsupportedProfile text, unchanged (4.10)
superposed    the chain is soft or norms and superposable D        sup D on the lower route with the slot Lim_D ++ Choice_D
enumerated    otherwise: the rights chain (until S2b), or not      every compatible complete choice up to 64, each choice's
              superposable (finding ReadingsNotSuperposable, 1.8)  own document checked by the lower route; UNKNOWN beyond
```

On the norms chain the superposed document is checked as the soft document with the empty `soft` block, every rule
strict, as S1 checks a candidate's document there (S1 13.6): the slot theorems are stated for the soft route.

The row is chosen after the couplings and narrowings are decoded with today's texts (4.1 step 1). The first three
rows are decided from the decoded document alone, and W2 returns there: a W2 document keeps today's coupled choices,
its on-request narrowing and its budget, and never sees `choiceCore D`, `ReadingsUnsatisfiable` or `DeadReading`
(4.7, fixture M18); no narrowing becomes a premise, no finding is computed and nothing of 1.2 to 1.9 is built for
it. A document on none of the first three rows whose chain is rights takes the enumerated row unconditionally (until
S2b): choosing it computes nothing of 1.2 to 1.9, `superposable D` is not evaluated, and `ReadingsNotSuperposable`
never reaches a rights document (fixture M12); `sup D` of a rights document is S2b's (12). On the soft and norms
chains, choosing between the last two rows computes exactly what `superposable D` reads (1.8: `supReady D`,
`uniformPrecedence D`, `sup D` of 1.4 and the chain's well-formedness on it) and nothing else of 1.2 to 1.9:
`ReadingsNotSuperposable` is that choice's own outcome when `superposable D` is false, and `choiceCore D`,
`DeadReading` and `Choice_D` are computed only after the route is chosen (4.1 steps 3 and 4).

### 1.2 Choices

```text
open sets            D.sets: the active versions of the open sets, in source order (S1 1.2); their ids are distinct
choice c             a list of (set id, candidate index), one entry per open set in source order
complete             c names every open set once, in order, with an index below the set's candidate count
compatible           complete, and every coupling and every narrowing in force holds of it:
  coupling K         for consecutive sets s, t of K.sets, the chosen candidates carry the same label on K.axis
  narrowing N        in force when (N.set, N.version) is an open set at its active version; then the chosen candidate
                     of that set is one of N.keeps. A narrowing on another version is not in force and adds nothing
choiceDoc D c        the ordinary chain document of every fixed unit and the chosen candidate of every open set, each
                     unit at its source position, under the units' own names (S1's build with every unit kept); with
                     the assertions in force: the fixed assertions and the chosen assertion candidates
```

A set with one candidate has one choice for that set. On the superposed and enumerated routes (1.1), a document whose
couplings and narrowings in force admit no compatible choice is refused before any verdict across readings
(`ReadingsUnsatisfiable`, 7): a verdict over no reading is never reported. On W2's route nothing of this section is
computed: the couplings go through today's `coupled_choices` and a recorded narrowing is applied only on request, as
today (4.1 step 2, 4.7).

### 1.3 The choice vocabulary and the atoms

For the `n`-th open set (`n` from 1, source order) with `k` candidates, `b := ⌈log₂ k⌉` bit predicates (the least `b`
with `k ≤ 2^b`; none for one candidate):

```text
sort           ve__reading                      one, added when the document has an open set
constant       ve__here : ve__reading           one
predicates     ve__bit__<n>__<j>(ve__reading)   j = 0 … b−1, j = 0 the least significant bit
literal        ve__bit__<n>__<j>(ve__here) or its negation
pattern n k i  the conjunction, j ascending, of the literal for each bit j spelling binary digit j of i
χ_{s,i}        the pattern of set s (its n and k) for candidate index i: "candidate i of s is chosen"
```

The conjunction of a list is `⊤` for no literal, the literal alone for one, and `a ∧ (…)` right-nested otherwise;
every regenerated formula below uses this one form, since Python's and Lean's elaborations are compared byte for
byte. Every structure spells exactly one pattern per set, whatever it does with `ve__here`: each literal is true or
its negation is. "Exactly one candidate" therefore needs no distinctness premise and no constant per candidate; what
is needed is to exclude the patterns that spell no candidate (1.6, `readings:<set>@<v>:one`).

### 1.4 The superposed document

For a document `D` on the soft or norms chain with open sets in source order and candidate `a_{s,i}` at position `k`
in the canonical order (sets in source order, candidates by index, `k` from 1):

```text
frame         the frame with E extended by the choice vocabulary
fixed unit    unchanged, except that an `over` entry of a fixed rule, and a `cites` key `over:<n>`, naming an
              interface rule name n of an open set (S1 1.3: declared by every candidate) is replaced by the
              qualified copies of n, one per candidate of that set in index order
candidate     q(n) := rd-<k>-<n> for every name the candidate declares (the reserved prefix of S1 1.8)
  assertion φ   the assertion χ_{s,i} → φ, in the assertions in force at the candidate's position
  norm N        the rule q(N): guard G_N ∧ χ_{s,i} (as `.and`, the guard first), every sufficient exception condition
                C replaced by C ∧ χ_{s,i}, the author carve-outs, necessary conditions, mode, rank, parties and over
                unchanged (a candidate's `over` names fixed names only, by closure); its cites as written
  right, right_lines, limitation, bar      S2b (12); not reached on these chains
```

`sup D` is this document assembled in source order as S1's `build` assembles a candidate's document (`place` on each
content). Names beginning `ve__` and `rd-` are rejected in author input by S1, so nothing in `sup D` collides with
an author name, and `rd-<k>-<n>` is injective (`k` is a numeral, `n` begins with a letter). The chain then runs on
`sup D` unchanged: its decision predicates are named by its own naming functions (`soft__excepted__rd_2_no_deception`
for candidate 2's rule `no-deception`), its coherence premises range over every colliding pair of `sup D`, and a pair
of two candidates of one set has contradictory atoms in its two guards, so it is DISJOINT by a certificate that
assumes no premise and is never a weighing point.

Why this is the per-choice semantics (plan 2.3, for these chains). Fix a compatible choice `c` and a structure in
which exactly `c`'s atoms hold. A rule of an unchosen candidate has a false guard: it is not live, so it never
applies, never selects, is never eligible and never dominates, blocks nothing and is blocked by nothing that
matters; its gated sufficient conditions hold trivially and quiescence (1.6) empties its decision tables, so its
necessary conditions hold too; a coherence premise with an unchosen member is satisfied. A chosen candidate's rule
has guard `G ∧ χ` with `χ` true, so it behaves as `G`. What remains is `choiceDoc D c` with renamed generated
predicates, provided no unchosen rule passes a yield up to a parent the chosen rule lacks: that is the one condition
superposition needs beyond S1's admission (1.8), and `superpose_faithful` (8.4) states the equality exactly.

### 1.5 Generated predicates and their owners

The chain generates base predicates on `sup D` (S1 1.5's keys, S2a's share): `excepted r` and `off r π` for a rule
`r`, `outweighs a L H` for an act and an ordered rank pair under the holistic flag. The **origin** of a rule name of
`sup D` is the candidate `(s, i)` whose content declares it (through `q`), or none for a fixed rule. It is defined on
the names of `sup D` and not on author names: an interface name is declared by every candidate of its set and has no
one origin, so the name map of 1.7 goes through the declaring set and the chosen candidate instead (`qName`, 8.3).

```text
owners(g)      the sets of candidates whose joint choice puts g into the choice's document; each a list of (set, index)
  excepted q(r), off q(r) π     [[origin r]]: one owner, the candidate                             (S2a: always one)
  excepted r, off r (fixed r)   [[]]: the fixed units alone generate it
  outweighs a L H               for every comparable colliding default pair (M, N) of sup D with that act and ranks,
                                the origins of M and N (none, one, or two candidates), the pair dropped when the two
                                are different candidates of one set (never chosen together), the list deduplicated
                                in colliding-pair order
fixed-generated g              [] ∈ owners(g): some fixed pair or fixed rule generates it alone
```

### 1.6 `Choice_D` and the combined slot

`Choice_D` is a labelled slot (composition.md 1.5): one closed formula per label, each over the base vocabulary of
`sup D`'s soft route (`E′_base`: the author's base predicates, the bits, the decision predicates). It is regenerated
from the decoded document after the chain's naming functions have run on `sup D` and never read from the wire (plan
2.1 rule 2's stated exception: these premises name the chain's generated vocabulary). Families in the order of
composition.md 1.5; within a family, sets in source order, candidates by index, couplings and narrowings in document
order, keys in S1 1.5's table order then by name. A label whose formula list is empty is omitted.

```text
readings:<set>@<v>:one          the conjunction of ¬(pattern) for every bit pattern i with k ≤ i < 2^b (none when k
                                is a power of two)
readings:<set>@<v>:<i>:quiet    the conjunction, over every generated predicate g of sup D with owners(g) = [[(s, i)]],
                                of ∀x̄. g(x̄) → χ_{s,i}                                      (x̄ typed by g's sorts)
readings:quiet:<key>            for every other g that is not fixed-generated: ∀x̄. g(x̄) → ⋁_{o ∈ owners(g)} ⋀_{a ∈ o} χ_a;
                                <key> is the source key in colon form: outweighs:<act key>:<L>:<H>
coupling:<id>                   the conjunction of ¬(χ_{s,i} ∧ χ_{t,j}) for s, t consecutive in the coupling's set
                                list and candidates i, j whose labels on the axis differ (i ascending, then j)
constraint:<n>                  discourse 1.5: requires χ_a → χ_b; excludes ¬(χ_a ∧ χ_b). No S2a document has one (0)
narrowing:<id>                  the conjunction of ¬χ_{s,i} for every candidate i of the set that the narrowing in
                                force does not keep, i ascending
```

The disjunction of a list is `⊥` for none, the one formula alone, or `a ∨ (…)` right-nested; a disjunct's conjunction
is as 1.3. Quiescence is emitted for every generated predicate that is not fixed-generated, whether or not some
compatible choice lacks it (14.5): where every compatible choice has `g`, the premise is implied by the other
premises and changes no model, and the elaboration then never asks which choices are compatible. Under E8 these
premises say one thing: a way of reading a sentence that is not taken adds nothing.

```text
Choice_D       the formulas of the labelled list above, in order
choiceCore D   the one, coupling, constraint and narrowing formulas alone: closed formulas over the bits, which
               decide which choices are compatible (encodes_unique, dead_sound); quiescence never restricts a choice
gatedRel D     [] until right-clauses@0 (S3), when a candidate line's totality premise enters as χ_{s,i} → ρ
slotP D        Lim_D ++ Choice_D ++ gatedRel D, each formula with its label; on these chains Lim_D is empty
               (correlate_noRights), so slotP D is Choice_D
```

### 1.7 The name map, the pulled structure, and the situations of a reading

```text
nameMap D c p    the name in sup D of a base predicate p of choiceDoc D c: for a generated predicate with source key
                 κ in c's document, the name of the key q(κ) in sup D, where q qualifies the rule name of an excepted
                 or off key by the candidate c takes in the set that declares that name, when that candidate declares
                 it (qName, 8.3: the set and the choice decide, not the name, since an interface name is declared by
                 every candidate of its set); every other name is itself
pull D c S       S read as a structure of c's document: a predicate p of that document's complete vocabulary has the
                 tuples of nameMap D c p in S, every other predicate (the bits, the unchosen candidates' decision
                 predicates) is empty; sorts and constants are S's
Encodes D c S    for every open set and candidate, χ_{s,i} is true in S exactly when (s, i) ∈ c
situation of c   a base structure B admissible for choiceDoc D c (BaseAdmissibleR), read in its expansion
                 expand (choiceDoc D c).1 B (S1 1.6: every regulated and defined predicate at its meaning over B)
```

`pull` restricts to the choice's vocabulary because an admissible structure has no true tuple on an undeclared
predicate (`Structure.Admissible`); a map that only renamed would carry the bits across and no structure of `sup D`
would ever be admissible for a choice's document (14.4). The shared vocabulary of 1.7 of S1 is what `nameMap` reads:
a fixed unit's decision predicate has one name in `sup D` and in every choice's document.

### 1.8 Superposable

```text
supReady D             every open set has a candidate, every candidate has content, set ids distinct (1.1 row 2); and
                       the couplings and narrowings have the shape today's decoders require (7): coupling ids
                       distinct; every coupling names at least two sets, none twice, each an open set at its active
                       version, every candidate of which carries a label on the coupling's axis; narrowing ids
                       distinct; every narrowing in force keeps at least one candidate and only candidates of its set;
                       the frame declares neither the constant ve__here nor a bit predicate of the choice
                       vocabulary (choiceFresh, 1.3); and every item stands for a unit of its own (unitsDistinct)
uniformPrecedence D    for every fixed rule X and interface rule name n in X.over: every candidate of that set gives
                       its rule n the same `over` list, as a set
superposable D         supReady D, uniformPrecedence D, and sup D passes the chain's well-formedness with every
                       assertion in force typed (S1's sideWF on sup D)
```

The coupling and narrowing conjuncts of `supReady` are the Lean counterpart of the shape part of today's checks
under the texts `invalid coupling`, `invalid coupling set`, `CouplingLabelMissing` (its per-set form: a coupled
candidate without the axis label), `invalid narrowing` and `narrowing must keep named readings` (7), which the
decoder runs before the route is chosen (4.1 step 1); a narrowing on a non-active version is not in force and adds
no conjunct (1.2, 14.17). They are not the whole of those checks: `validate_couplings` also refuses a coupling whose
sets share no label value on the axis (its second `CouplingLabelMissing`), a coupling that admits no choice
(`CouplingUnsatisfiable`) and its field and count checks, none of which has a conjunct (7). They are what
`encodes_unique` needs: `couplingHolds` is false on a missing label
where `couplingPremises` adds no premise, and both read a coupling's set by id, so a reference to a non-active
version would be read as the active set that Python refuses; with the conjuncts every slot-admissible base of `sup D`
encodes a compatible choice (8.4, fixture M17). `superposable`, `SupReplay.sp` and the `hr` of `choices_spec`,
`dead_sound`, `unsat_sound` and `superpose_assertions` carry them.

The last conjunct, `choiceFresh`, is the Lean counterpart of S1's reserved names (S1 1.8) on the frame's constants
and base predicates: `VE.Environment` lists constants and predicates as functions, so `WellFormedDoc` cannot see a
frame that declares `ve__here` or a predicate `ve__bit__<n>__<j>`, while the wire decoders refuse every such name
with S1's text `InvalidInput: name <n> begins with ve__` (Python and Lean alike, before the route is chosen). On a
`Doc` built as a Lean value the conjunct is what `base_down`, `base_up`, `superpose_conflict_free` and
`superpose_assertions` need: `choiceEnv` overrides a frame declaration of the choice vocabulary in `sup D`, while
`choiceDoc D c` keeps it, so a slot-admissible base of `sup D` could interpret `ve__here` outside the frame's sort
(fixture M19, `KH`), and an assertion candidate could mention the very bit that gates it (M19, `KB`). It is decidable:
the constant `ve__here` and the names of `bitDecls D` are looked up in the frame's environment. A decoded document
always satisfies it; Python's `sup_ready` carries the same conjunct and refuses a document failing it with the
decoder's text (DRI ruling 1 of 2026-10-03).

`unitsDistinct` (no two items carry one unit id) is the Lean counterpart of today's `duplicate or invalid unit id`:
S1's attachment is computed per unit id and `one D s i` reads a set by its id, so with a repeated unit id or set id
an assertion would be checked only beside another unit's or set's rules, and `asserted_shared` would be false
(fixture M20; finding 4 of the S2a Lean build, 2026-10-03, pending the DRI's confirmation).

Uniform precedence is the condition A1's copy mapping needs. A fixed rule `X` whose `over` names `n` is, after the
mapping, a child of every copy of `n`. An unchosen copy has a false guard and never applies, but W1's `yields` is
`applies ∨ ⋁ children yields`, so the unchosen copy still yields wherever `X` does, and every parent of that copy
stops selecting there. If the chosen copy has the same parents, nothing changes: the chosen copy yields there too
and the parent's children in `sup D` yield exactly when they do in the choice's document. If the copies have
different `over` lists, a parent of the unchosen copy alone is silenced in `sup D` and not in the choice's document
(fixture M8: a strict collision in the choice's own document, and no conflict in `sup D`). The condition is checked
once over the open sets; when it fails the document is not superposed and the enumerated route decides, under the
finding `ReadingsNotSuperposable: <set>` (7). The other two causes of that finding are the plan's: the dependency
order of norms 4.1(4) fails on `sup D` while every candidate's document stratifies (two candidates read each other's
predicates in their guards), and a size limit of the chain reached by `sup D` and by no candidate's document (plan
open question 5: a qualified name, the predicate count, the unfolded carve-outs). The limit on a qualified name is
the chain's own: every generated decision predicate within `MAX_IDENTIFIER_BYTES` (64 bytes), which the soft
decoder enforces on every soft document (`ResourceLimit: decision predicate <name>`, soft-norms 6.4) and which S1's
`chainWF` on the soft chain carries as `namesFit` (DRI ruling 2 of 2026-10-03; fixture M16), so `sideWF D (sup D)`
is false exactly when Python's chain check refuses `sup D` for it.

### 1.9 Verdicts, evidence and findings

All statuses are W2's; no new status. Evidence on the superposed route is one of:

```text
certificate under A    a tableau certificate from background′(sup D) ++ slotP D ++ atoms(A) ++ layers ++ assertions ++ Γ
                       for φ, A a list of named candidates (empty for "under every reading")
model under A          a checked finite base model of sup D satisfying the regenerated base background, the whole slot,
                       the atoms of A, the assertions and Γ; it encodes exactly one compatible choice (encodes_unique)
conflict certificates  one per W1 conflict target of sup D over Background_base′ ++ slotP D ++ atoms(A)
conflict witness       a checked model of that background where a target holds; it encodes the reading of the conflict
dead reading           a certificate of ¬χ_{s,i} from choiceCore D                                (finding DeadReading)
unsatisfiable          a certificate of ⊥ from choiceCore D                                      (error ReadingsUnsatisfiable)
```

Findings: `DeadReading: <set>:<i>` for a candidate that no narrowing in force drops and that no compatible choice
takes (its atom is refuted from `choiceCore D`); a candidate a narrowing drops is reported under the narrowing (E7)
and not as dead (14.7). `ReadingsNotSuperposable: <sets>` as 1.8. Both are report lines, never errors, and both are
computed only on the superposed and enumerated routes (4.1): a W2 document gets neither.

## 2. The English (one reading each)

S2a registers E4, E6, E7, E8, E10, E12, E13 and E17 of composition.md 2.1 with the slots that table leaves to the
registering stage, E11 only under the fallback of 4.4, and four sentences of its own (E26 to E29). The frames of
E4 to E17 are composition.md's and are not restated. No sentence here can be written by an author as document
content. Each goes through W7's all-derivations gate before it is shown; none is an IDE question, so none goes
through W8. E5 and E3 are S1's and composition.md's, used here with their frames. E6 is registered and passes its
gate; no S2a document can show it (0).

### 2.1 Slots

| Slot | Definition | Used in |
|---|---|---|
| `<k>` in E4 | the number of candidates of the open set, as a numeral | E4 |
| `<k>` in E10, E27 | the number of open sets of the document, as a numeral; at least 2 (E26 is the one-set form) | E10, E27 |
| `<reading>` | composition.md 2.1's: `reading <i>` with the 1-based position, or the deontic verb in italics when the set's candidates differ only in it | E7, E12, E17 |
| `<citation>` | composition.md 2.1's, over the narrowing's or coupling's cited units, by display number | E7 |
| `<result sentence>` | one of the closed forms below | E10, E11, E12, E26 |
| `<situation>` | composition-s1.md 2.1's slot, on the pulled situation `pull D c B` of the reading named (1.7): no choice vocabulary; the decisions of the chosen readings' own rules as suppositions, of fixed rules as S1 words them | result sentences R3 to R5 |
| `<conclusion>` | the canonical VE sentence of the conclusion `φ` (the existing English surface), in italics | R2, R3 |

Result sentences, each a fixed lead that no other registered production begins with:

```text
R1  no two rules on the same act contradict each other.                           conflict certificates under A
R2  the conclusion follows: <conclusion>                                           a certificate under A
R3  the conclusion does not follow. It fails here: <situation>.                   a countermodel (E12 only)
R4  two rules contradict each other here: <situation>.                            a conflict witness (E12 only); the
                                                                                  lower route's classification line
                                                                                  follows, with names as 6 says
R5  the sentences of this document can all be true together, as here: <situation>. a premise model (E12 only)
R6  the sentences of this document cannot all be true together.                   a certificate of ⊥ under A
```

### 2.2 Wordings S2a adds

| # | Wording | The one reading | Formal content | Gate |
|---|---|---|---|---|
| E26 | `Under every reading of the open sentence, <result sentence>` | As E10, for a document with exactly one open set. | `superpose_all` or `superpose_conflict_free` with `A = []`, `D.sets.length = 1` | W7 |
| E27 | `Under no reading of the <k> open sentences does the conclusion follow.` | For every compatible choice there is a checked situation of that choice's document in which the premises hold and the conclusion is false. | a countermodel under every compatible choice, at most 64 (NONE); each shown by E12 with R3 | W7 |
| E28 | `VE did not check every way of reading the open sentences: there are more than 64.` | More than 64 compatible choices exist; the verdict that needed one check per reading is UNKNOWN. | the enumeration budget (4.6, 7) | W7 |
| E29 | `The readings of <citation> were checked one way at a time, not together.` | The named sentences' sets were not superposed; every compatible way of reading them was checked as its own document. | finding `ReadingsNotSuperposable` (1.8) | W7 |

### 2.3 Which wording a result gets

1. A certificate with `A = []` on the superposed route: E10 (E26 for one open set) with R1, R2 or R6; then E3 with one
   line per used slot label: E4 for a `:one` label, E8 once for any quiescence label, E5 for a coupling, E7 for a
   narrowing (one E7 per candidate it drops), E6 for a constraint; then E13 for every open set no used leaf mentions.
   Composition.md 2.1's label rule applies: `readings:<set>@<v>:all` for a set some used leaf mentions with no atom
   of it assumed, `readings:<set>@<v>:<i>` when an atom of it was assumed, nothing for a set no used leaf mentions;
   a leaf mentions a set when its formula contains a bit predicate of that set.
2. A certificate with `A ≠ []`: E12 naming exactly the candidates of `A`, in source order, with R1, R2 or R6; then
   E3 and E13 as in 1.
3. A model (premise model, countermodel, conflict witness): E12 naming **every** open set's candidate of the complete
   choice the model encodes, with R5, R3 or R4. A model is one reading; naming fewer sentences would claim the result
   for readings the model does not show.
4. NONE: E27, then one E12 with R3 per compatible choice. SOME: the E12 of the proof and the E12 of the countermodel.
5. UNKNOWN beyond 64: E28, with the E12 of the countermodel found (plan 2.5: "not ALL: countermodel under <choice>").
6. A dead reading: E17. A set that is not superposed: E29 under the document's readings.
7. The enumerated route uses the same sentences: E10 (E26) when every compatible choice gives the result, E12 per
   choice otherwise. Nothing in the English says which route produced a verdict; the report's `route` field does (6).

### 2.4 Non-wordings, beyond composition.md 2.2

- E10 or E26 for a model-based result, or E12 naming fewer sentences than the complete choice a model encodes.
- "under every reading" when any compatible choice was not checked (the enumeration budget) or when the conflict
  status under the named readings is not CONFLICT-FREE (4.5).
- E17 for a candidate a narrowing drops: that candidate is shown under its narrowing by E7.
- Any qualified rule name (`rd-`), bit predicate, `ve__here` or generated decision predicate; a rule of a candidate
  is named as the author named it, with its reading (6).
- `may not`, in a frame or a slot: `<situation>` and `<conclusion>` are rendered by the existing English surface, which
  never produces it (composition.md 13.20; S1 2.4), so G9 holds of every sentence here.
- E11 unless the lifting lemma failed in statement review (4.4); E10 for an entailment when E11 is in force.

### 2.5 Examples

On fixture M4 (9.2): E26 with R2, "Under every reading of the open sentence, the conclusion follows: *For every
agent, for every user, that agent must help that user.*" followed by E13, "This does not depend on how sentence 1 is
read." On M4's second conclusion (SOME): "Read sentence 1 as *must*: the conclusion follows: *For every agent, for
every user, that agent must avoid deceiving that user.*" and "Read sentence 1 as *should*: the conclusion does not
follow. It fails here: a is an agent; u is a user; suppose the decider decides the exception applies to a and u." (As
built, `<conclusion>` is the existing English surface's sentence of the formula, read back by its all-derivations
parser; draft 5's *Every agent must help each user.* was the rule surface, which does not render a formula; and the
element names of `<situation>` are the checked model's.) On M3: "Read sentence 1 as *must*: two rules contradict
each other here: a is an agent; u is a user." On M5: E26 with R2, then E3 and E7, "Sentence 1 is not read as *should*, because of
sentence 2." On M6 with its narrowing: E17, "No compatible way of reading the open sentences reads sentence 2 as
*should*." On M9: E29, "The readings of sentences 1 and 2 were checked one way at a time, not together."

## 3. Wire form and identity

S2a adds no wire field to a document: couplings, narrowings and reading sets are W2's and rights 3.3's as S1 left
them. Case kinds on `ve_readings_route`, beside S1's `readings-validate` and `readings-separate`:

- `readings-elaborate`: the environment and the document. The answer, regenerated and compared byte for byte with
  Python's (`ve/readings_sup.py`): the route of 1.1; the choice vocabulary (sort, constant, bit declarations per set);
  every unit of `sup D` in the chain's canonical wire form with its position; the labelled slot (label, formula) in
  order; per set and candidate, the position `k` and the name map's entries (each declared name and generated
  predicate of the candidate's own document with its name in `sup D`); the compatible choices when at most 64, else
  `over`; the finding of 1.8 with its cause; the sizes (sorts, predicates, nodes of the elaborated tree, against the
  limits).
- `readings-conflict`: the conflict certificates (one per target, `slotConflictFreeCheck` at `slotP D ++ atoms(A)`) or a
  witness model with its target; the answer names the choice a witness encodes.
- `readings-certificate`: `A`, `Γ`, `φ`, the certificate; the answer is accepted/rejected, the used slot labels, the
  sets the used leaves mention, and the `readings:` labels of composition.md 2.1.
- `readings-model`: `A`, `Γ`, optional `φ`, a finite model; the answer is valid/invalid with the first failing premise
  label, the choice it encodes, and the pulled model.
- `readings-dead`: a set, an index and a certificate of `¬χ` from `choiceCore D`; or no index and a certificate of `⊥`.
- `readings-choice`: a complete choice and an inner case of the lower route's kinds; Lean checks `compatible D c`,
  builds `choiceDoc D c` and runs the lower route's logic for the inner kind on it; the answer is the inner answer
  with the chain's document hash of `choiceDoc D c`.
- Every other kind: `readings@1` is stripped and the case is run by the lower route's logic unchanged (S1 8.4).

Identity. S2a adds no identity. `sup D`, `Choice_D`, the name map and every compatible choice are regenerated from the
decoded document at every trusted site and bound to the chain's document hash; none is on the wire as authority.
Certificates and models on the wire are evidence checked against the regenerated premises. The wrapper report
identity binds the verdicts as W2 binds reading verdicts today; no meaning identity changes. With `readings@1` off,
or on with no content-bearing set, nothing of this section is reachable and every identity, status and verdict is
byte-identical (4.7).

## 4. Semantics

### 4.1 The head and the order of steps

After S1's admission (its 4.1, unchanged, through the separation check and couplings), the head `readings`:

1. Decodes the couplings and narrowings with today's texts (lifting S1's limitation of 4.1: Lean now reads both, with
   W2's and rights 3.3's checks and texts, 7; a narrowing not in force is recorded, 6). `supReady D` is the Lean
   counterpart of the shape part of those checks on the decoded document (1.8, 7). A document with couplings that
   today's `validate_couplings` refuses keeps today's `CouplingUnsatisfiable: <ids>`. Nothing of 1.2 to 1.9 is
   computed here.
2. Chooses the route of 1.1. The first three rows are decided from the decoded document alone. W2 ends here with its
   route verbatim: today's `coupled_choices` over the couplings, a recorded narrowing applied only on request
   (`--narrowing`, `ve/document.py`), today's budget; no `choiceCore D`, no `ReadingsUnsatisfiable`, no
   `DeadReading` (4.7, fixture M18). Pending ends here; the abstention is S1's. For a document on none of the first
   three rows: on the rights chain, the enumerated route unconditionally (until S2b), with nothing of 1.2 to 1.9
   computed, `superposable D` not evaluated and no finding (fixture M12); on the soft and norms chains,
   `superposable D` decides between the last two rows (1.8): `supReady D`, `uniformPrecedence D`, `sup D` (1.4)
   and the chain's well-formedness on it are computed here and nothing else of 1.2 to 1.9; when it is false, the
   finding `ReadingsNotSuperposable` with its cause (1.8, 7) and the enumerated route.
3. On the superposed and enumerated routes: computes `choiceCore D` (1.6). If no choice is compatible, the document
   is refused with `ReadingsUnsatisfiable: <ids>` (7) before any verdict. As built (review A1 of 2026-10-03), Lean
   decides it with its own exhaustive search (`choices D = []`, sound by `no_compatible_of_choices`) in
   `readings-elaborate` and in the replay of every superposed case kind (`SupReplay.sat`), and Python's search must
   agree; `readings-dead` still checks a certificate of `⊥` from `choiceCore D`. Dead readings are certified here
   (`DeadReading`, 1.9). Before any verdict the route also checks every compatible choice's document (DRI ruling 5):
   on the superposed route the soft check of each, up to 1024 compatible choices (`choicesSoftChecked`; past them
   the superposed case kinds refuse with `ResourceLimit: more than 1024 readings to check`), on the enumerated route
   the chain's check of each of the at most 64 it enumerates; a choice whose document fails is the chain's
   diagnostic under the choice (7).
4. Superposed (`superposable D = true` at step 2): builds `Choice_D` (1.6) on `sup D` and hands `sup D` with
   `slotP D` to the route `dispatch` names for the list without `readings@1` (`soft`, or `norms` checked as 1.1
   says), which runs its checks relative to the slot (composition.md 4.3): conflict-freedom certified or witnessed,
   the premise models, certificates and countermodels for queries, with the atoms of a named reading appended to
   the slot (1.9). Every regenerated formula is bound to the document hash.
5. Enumerated (the rights chain, or `superposable D = false` at step 2): enumerates the compatible complete choices
   in canonical order, stopping past 64; for each, checks
   `choiceDoc D c` with the lower route (`readings-choice`), refusing the document when a choice's document fails
   the chain's well-formedness (7); combines the verdicts (4.6).
6. Reports (6). Findings (`ReadingsNotSuperposable` at step 2, on the soft and norms chains only; `DeadReading` at
   step 3) never change a verdict; neither reaches a W2, pending or abstaining document.

### 4.2 The elaboration, regenerated

`sup D`, `Choice_D`, the name map and the compatible choices are functions of the decoded document (8.3). Lean's
`readings-elaborate` answer is compared with Python's byte for byte on every load; a difference is
`CheckerUnavailable`, never a verdict (S1 10). Rust evaluates the Python-generated formulas of `sup D` (slot
premises, assertions, conflict targets, conclusions) on every model shown, marked `untrusted: true`, and its values
must agree with Lean's (10).

### 4.3 Model correspondence (composition.md 1.5, both directions)

For a compatible choice `c`:

- **Down** (`base_down`): a base structure `B` of `sup D` that satisfies the slot and in which exactly `c`'s atoms hold
  is, pulled (1.7), a base structure of `choiceDoc D c`; the assertions in force agree in the two expansions; every
  regulated predicate has the same value in the two situations and every sentence over the shared vocabulary the
  same truth (`superpose_situation`). `encodes_unique` says every slot-admissible base of `sup D` encodes exactly one
  compatible choice, so a model of `sup D` **is** a reading together with a situation of that reading's document.
- **Up** (`base_up`): a base structure of `choiceDoc D c` with at least one element extends to a slot-admissible base
  of `sup D` encoding `c`: the bits set by `c`, `ve__here` any element, `ve__reading` containing it, the chosen
  candidates' decision tables under their qualified names, every unchosen candidate's table empty; pulled back it is
  the structure it came from.
- **Pointwise** (`superpose_faithful`): in any structure in which exactly `c`'s atoms hold, every regulated predicate
  has the value `ValueSoft` gives it in `choiceDoc D c` on the pulled structure. On these chains the quiescence
  hypothesis is not needed for this equality (an unchosen rule is not live, whatever its tables say); it is stated
  because S2b's bar case needs it (plan F21), so that S2b removes only the chain hypothesis.

### 4.4 The empty situation

Composition.md 4.5 as built here. `superpose_conflict_free` needs no non-emptiness hypothesis on either side: a
regulated predicate has arity 1 or 2, so `ConflictFree` is vacuous on an empty carrier, and every slot-admissible
structure of `sup D` interprets `ve__here`. `superpose_all` covers the empty situation of a reading's document through
the lifting lemma (`adjoinOne`, composition.md 9.5, built in S2a, 8.2): the new element lies in no sort and no tuple,
so base admissibility and every closed formula's truth are preserved (`adjoin_baseAdmissibleP`, `adjoin_denote`), and
the truth of a sentence over the complete vocabulary in the expansion is preserved too, because that truth is the
truth of its outcome substitution on the base (`circ_canon`, existing). `base_up` keeps `hne` either way. If the
lifting lemma fails in statement review, `hne` returns to `superpose_all` and every entailment report says E11,
never E10 or E26 (G5).

### 4.5 Verdicts on the superposed route

| Question | Evidence on `sup D` (1.9) | Report |
|---|---|---|
| Can the rules contradict each other? | conflict certificates under `A = []`, or a witness | CONFLICT-FREE under every reading: the lower route's status line on `sup D` with `<m> reading premises` (composition.md 7), `conditional_on` the used slot labels; CONFLICT: the lower route's line, the witness's choice and pulled situation (E12, R4); UNKNOWN with the budget |
| Under a named reading? | the same under `A` | the same, under the choice listed |
| Are the premises consistent? | a model under `A = []`; then one model per candidate under `A = [(s, i)]` | `model` with its choice (E12, R5); per candidate `model`, `dead` (finding), `INCONSISTENT` (a certificate of `⊥` under its atom, only when CONFLICT-FREE under that atom) or `UNKNOWN` |
| Does φ follow under every reading? (ALL) | a certificate under `A = []`, only when the conflict status under `A = []` is CONFLICT-FREE | E10 or E26 with R2, E3, the `readings:` labels, E13 |
| Under a named reading? | a certificate under `A`, only when CONFLICT-FREE under `A` | E12 with R2 |
| SOME | a certificate under one complete choice and a countermodel encoding another | both E12 lines |
| NONE | a countermodel per compatible choice, enumerated up to 64 | E27 and the E12 lines; beyond 64: `UNKNOWN (not ALL: countermodel under <choice>)`, E28 |
| Any entailment, when the conflict status under `A` is not CONFLICT-FREE | — | `UNKNOWN (conflict status: <status>)` (14.8) |

Soft's classification of colliding default pairs runs on `sup D` with `choiceCore D` added to its classification
background (soft-norms 6.2 excludes coherence conjuncts and nothing else): a pair of two candidates of one set is
DISJOINT without any premise; a pair excluded by a coupling is DISJOINT by the coupling's premise and is listed with
that label; the other pairs are classified as today. Classification marks conjuncts as discharged and is a premise of
no theorem here.

### 4.6 The enumerated route

The compatible complete choices in canonical order, at most 64 (`choices_spec`): for each `c`, `choiceDoc D c` is
checked by the lower route as an ordinary document. Combination: CONFLICT-FREE under every reading when every choice
is CONFLICT-FREE (E10/E26 with R1; `conditional_on` the union of the choices' lists); CONFLICT when some choice is,
reported per choice (E12, R4); premises `model` when some choice has a model, per candidate the status of the
choices that take it; ALL when every choice proves `φ` (E10/E26, R2), NONE when every choice refutes it (E27), SOME
with one of each, UNKNOWN otherwise with the first UNKNOWN choice named. Beyond 64: UNKNOWN with W2's budget shape
(`budget: {max_choices: 64}`, `units`), E28. A compatible choice whose document fails the chain's well-formedness is
an error (7): the choices together are not a document, and the route does not report around it.

### 4.7 Conservativity

- `readings@1` off: nothing here is reachable; identities, statuses and verdicts byte-identical (plan F20).
- `readings@1` on, no content-bearing set: W2's ALL, NONE and SOME route verbatim (`ve/readings.py`), with today's
  `models`, today's `coupled_choices` over the couplings and a recorded narrowing only on request (`--narrowing`);
  `sup D` is never built and `choiceCore D` is never computed, so no `ReadingsUnsatisfiable` and no `DeadReading`
  (M18: a coupling admitting two choices with two recorded narrowings that together keep none is W2's two-choice
  verdict, as today). `superpose_assertions` (8.4) relates the two routes: for a document whose sets are
  all assertions, without couplings or narrowings, a structure extends to one satisfying `sup D`'s assertions and
  `Choice_D` exactly when it satisfies the fixed assertions and one candidate of every set (`readings_all_iff`).
- No open set: `sup D` is the document of every fixed unit and `Choice_D` is empty (`sup_no_sets`).
- A pending candidate: today's UNKNOWN with today's reason (1.1).
- No frozen file, canonical byte, identity or theorem statement changes; nothing of S1's admission, separation or
  report changes except the status text that S1 set to `superposition pending` (4.8).

### 4.8 Statuses

S2a defines no status and no status rule. Rights 7.2's READINGS rule stays S1's. A query or report that S1 left
UNKNOWN with `superposition pending` now carries the verdict of 4.5 or 4.6, or the UNKNOWN of 1.1 (pending), 4.6
(budget), 4.5 (conflict status) or the lower route's budget. On the rights chain every such verdict is the
enumerated route's; the rights report of a document over budget stays `UNKNOWN: per-choice rights elaboration
pending` (S1 4.8) until S2b.

### 4.9 The layer contract (composition.md 4.1), for this stage

| Rule | What S2a supplies |
|---|---|
| 1. One position | the head `readings` hands `sup D` to `dispatch`'s next route; "unchanged when off" is 4.7 |
| 2. Source in, same kind out | `sup D` is an ordinary soft (or norms) document: `sup_wellFormed`. Rule 2's stated exception: `Choice_D` names the chain's generated predicates on `sup D`, computed by the chain's own naming after it has run (1.6) |
| 3. Regenerated | `readings-elaborate`, byte for byte (4.2) |
| 4. Premises through slots | `Choice_D` labelled (`slot_wellLabelled`), closed over `E′_base` (`slot_wellFormed`), appended after `Lim_D`, never inserted before it; no premise of `Choice_D` is itself gated; the model correspondence of 4.3 |
| 5. Identity when unused | `sup_no_sets`; a formula-only document keeps W2's route (`superpose_assertions`) |
| 6. Abstention is named | `ReadingsNotSuperposable` with its cause and the enumerated route; `ReadingsUnsatisfiable`; S1's texts; W2's budget |

### 4.10 `norm-defaults@0`

Composition.md 6 asks each stage to state the `fill` instance for the routes it sits on. S2a's is: not built; S1's
abstention `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` stays. DRI ruling 4 (2026-10-03,
the constitution pilot of run 20261003T0600Z) requires that the abstention, or W2's route, is what such a document
reaches: the frame of a `norm-defaults@0` environment is read with each `unspecified` completion as the placeholder
`deny` (norm-defaults 2.3's E‴; Lean `placeholderFrame`, Python's S1 environment), so a content-bearing set reaches
the abstention instead of a decoder text, and a document whose sets have no content (the pilot's main translation
with `readings@1` added) is W2's, answering as without the profile; the filled document's base environment sets
`readings@1` aside with `norms@0`. The pilot's case is the fixture `tests/data/readings_s2/constitution-nd-readings.ve.md`. The instance is the
plan's (2.9, open question 13): `fill` runs on `sup D`'s tree last; `unsaid__p` is per predicate and shared by every
candidate, so it has no owner and no quiescence premise; `Fill_T` joins the slot after `Choice_D`. The constitution's
main translation uses the profile (composition-s1-measured.md), so the pilot of section 11 runs on the document S1's
rerun built, as S1's did.

## 5. What a superposed verdict certifies

1. CONFLICT-FREE under every reading: for every compatible choice `c` and every base structure admissible for
   `choiceDoc D c`, every regulated predicate has exactly one outcome (`superpose_conflict_free`), conditional on the
   coherence premises of `sup D` and the slot premises listed. Nothing is claimed for a choice that is not compatible.
2. A certificate under `A` proves, for every compatible choice that takes the candidates of `A` and every situation of
   that choice's document in which the premises and the assertions in force hold, that the conclusion holds there
   (`superpose_all`), when the conflict status under `A` is CONFLICT-FREE. It proves no more: nothing about a
   choice that does not take `A`'s candidates, nothing about a situation that violates a slot premise.
3. A checked model is a compatible choice and a situation of that choice's document (`superpose_countermodel`,
   `superpose_conflict_witness`): the premises hold there and the conclusion fails, or two rules contradict. It
   says nothing about any other choice.
4. A dead reading (`dead_sound`): no compatible choice takes the candidate. It says nothing about whether the
   candidate is right.
5. No verdict says that a set is exhaustive, that a coupling or narrowing is the right interpretation, or that
   the author meant any reading (plan section 8).
6. On the enumerated route each claim is the lower route's for the choice's own document; the combination claims
   exactly the conjunction over the compatible choices checked, and nothing beyond 64.

## 6. The report

The `readings` block of S1's report (its 6) gains: `route` (`w2`, `pending`, `superposed`, `enumerated`), the
`choice_count` (exact when at most 64, else `over 64`), `reading_premises` (every `Choice_D` label in force, and per
result the labels used), `dead_readings`, `not_superposable` (the finding with its cause: `precedence under <name>`,
or the chain's diagnostic on `sup D`), `narrowings_stale` (narrowings not in force, 1.2), the sizes of `sup D`, and
per verdict its evidence form, the choice or choices named and the `readings:` labels of composition.md 2.1.
`checked_by` now says that Lean covers the couplings and narrowings as premises and the verdicts across readings;
W2's structural validation of sets stays Python's (S1 4.1). Residual lines: `reading_premises`, `dead_readings`
(composition.md 7), `slot_premises_used` by family.

As built (review of 2026-10-03): `ve document check` reports `premises` from 4.5 or 4.6 (with `route`, the choice a
model encodes, and per candidate `model`, `dead`, `narrowed` for a candidate a narrowing in force drops,
`INCONSISTENT` or `UNKNOWN`), or the pending row's UNKNOWN; the `readings` block adds `choices_checked`, `conflict`
(the status under every reading with its evidence form, and its `conditional_on`), `status` (its line),
`dead_readings` (each certified by `readings-dead`; `null` when the compatible choices were too many to enumerate,
never an unchecked empty list) and `english` (2.3's sentences, each through the gate of 2). `ve document readings
--conclusion` answers ALL, SOME or NONE across readings (`--under <set>:<i>` names readings), with its English.

`conditional_on`: `soft:coherence:*` of `sup D`, then the slot labels used, verbatim, in slot order (composition.md 3).
A coherence label of `sup D` names rule names as `sup D` has them; the report's `names` table maps each qualified name
to its set, version, index and author name, so a reader of the JSON can resolve it. Status text: the lower route's
line verbatim on `sup D`, with `and <m> reading premises` when `m > 0` (composition.md 7). The English of every result
is 2.3's; a rule of a candidate is named as the author named it followed by ` under <set>@<v>:<i>` in the lower
route's own lines (the witness kind of a CONFLICT line, a weighing point), as S1 suffixes a chain diagnostic.

## 7. Diagnostics

In the order of 4.1. Texts in the first table are composition.md 8's or today's, verbatim.

| Text | When | Kind |
|---|---|---|
| `ReadingsNotSuperposable: <sets>` | 1.8; `<sets>` in source order, comma-separated: the set of the first non-uniform interface name; the sets with a candidate rule on a predicate of the cycle; every open set for a size limit. The cause is a report field | finding |
| `DeadReading: <set>:<i>` | 1.9; on the superposed and enumerated routes only (4.1 step 3) | finding |
| `CouplingUnsatisfiable: <ids>` | today's check of `validate_couplings`, unchanged, on every route | error |
| `UNKNOWN (not ALL: countermodel under <choice>)` | NONE beyond 64 choices (plan 2.5) | status |
| `invalid coupling`, `invalid coupling set`, `CouplingLabelMissing: <id>, <set>`, `ResourceLimit: couplings`, `invalid narrowing`, `narrowing must keep named readings`, `narrowing cites unknown reading set version` | W2's and rights 3.3's texts; Python first, Lean's decoder with the same texts (a difference is `CheckerUnavailable`), before the route is chosen (4.1 step 1). The coupling and narrowing conjuncts of `supReady` (1.8, 8.3) are the Lean counterpart of the shape part of these checks on the decoded document, and of that part only: at least two sets, none twice, each an open set at its active version, every candidate of which is labelled on the axis; every narrowing in force keeping at least one candidate, all of its set; distinct ids. A `Doc` that fails a conjunct is one these texts refuse (M17 a to c). The converse is not claimed: `validate_couplings` also refuses a coupling whose sets share no label value on the axis (its second `CouplingLabelMissing: <id>, <first set>`), a coupling admitting no choice (`CouplingUnsatisfiable`, above) and its field and count checks, and `supReady` carries none of these. Two active sets whose candidates are labelled A and B exclusively on the axis have `supReady D = true` and are refused by Python with `CouplingLabelMissing`; the theorems of 8.4 are stated for the Lean value and hold of it (no choice is compatible and no base is slot-admissible), and the route never reaches it | error |

New in S2a:

| Text | When | Kind |
|---|---|---|
| `ReadingsUnsatisfiable: <ids>` | 4.1 step 3, on the superposed and enumerated routes only: the couplings and narrowings in force admit no compatible choice, certified by `⊥` from `choiceCore D`; `<ids>` the ids of those couplings and narrowings, sorted. Never on W2's route, where a recorded narrowing is applied only on request (M18) | error |
| `UNKNOWN (conflict status: <status>)` | 4.5: an entailment asked under readings whose conflict status is not CONFLICT-FREE | status |
| `InvalidInput: name <n> begins with ve__` | S1's text, unchanged, for a frame constant `ve__here` or a frame predicate `ve__bit__<n>__<j>`: the decoders refuse it before the route is chosen (4.1 step 1); `choiceFresh`, a conjunct of `supReady` (1.8), is its Lean counterpart on a `Doc` value (DRI ruling 1; fixture M19) | error |
| `ResourceLimit: decision predicate <name>` | the soft decoder's text, unchanged, for a generated decision predicate beyond `MAX_IDENTIFIER_BYTES`: on `sup D` it is the cause of `ReadingsNotSuperposable` (1.8, M16), on a candidate's or a choice's document the chain's error; Lean's `chainWF` carries it as `namesFit` (DRI ruling 2) | finding on `sup D`, error otherwise |
| `<chain diagnostic> under <set>@<v>:<i>[, <set>@<v>:<i>]*` | 4.6: a compatible choice whose document the chain refuses, the choice written in source order; as built (DRI ruling 5) on the superposed route too, for the soft check of every compatible choice's document (4.1 step 3) | error |
| `ReadingsUnsatisfiable: no compatible reading takes <set>@<v>:<i>[, <set>@<v>:<i>]*` | as built (review A1's class): a case or query under named readings (`assumed`) that no compatible choice takes, whose every verdict would be vacuous (`takenBy`, `CertificateReplay.taken`, `readings_wire_assumed_taken`) | error |
| `ResourceLimit: more than 1024 readings to check` | DRI ruling 5: the superposed case kinds past 1024 compatible choices, whose documents the route has not checked; `readings-elaborate` reports `choices_checked: "over 1024"` and every superposed verdict is UNKNOWN with this reason | error of the verdict kinds |
| `CheckerUnavailable` | 4.2: Python's `readings-elaborate` differs from Lean's | error, never a verdict |

Unchanged: S1's texts; every W1, soft, rights and P0 text; `dispatch`'s texts; W2's budget shape for UNKNOWN.

## 8. Lean (S2a): definitions and the exact statements to prove

### 8.1 Files

`lean/VE/Compose/Adjoin.lean` (8.2: the lifting lemma, namespace `VE.Compose`, a new file; `Slot.lean`, `Dispatch.lean`
and `Content.lean` untouched), `lean/VE/Readings/Choice.lean` (8.3), `Superpose.lean` (8.4), `Route.lean` and
additions to `Wire.lean` and `Run.lean` (8.5), `Examples.lean` (the `#guard` fixtures of 9.2), `lean/READINGS.md`
extended. The target `ve_readings_route` gains the case kinds of section 3. `VE.lean` and `VE/Audit.lean` gain
imports and audit entries; the audit allowlist is unchanged. Frozen `Norms/*`, `SoftNorms/*`, `Rights/*`, `Route/*`,
`Discourse/*` and `Compose/{Slot,Dispatch,Content}.lean` are untouched. Of S1's five files, `Separate.lean` and
`Lines.lean` are untouched; `Wire.lean` and `Run.lean` receive S2a's additions (the structures, decoders and
theorems of 8.5 and the case kinds of section 3), and one change of an S1 definition is made by DRI ruling 2 of
2026-10-03: `chainWF` on the soft chain (`Doc.lean`) gains the conjunct `namesFit` (every generated decision
predicate within `MAX_IDENTIFIER_BYTES`), and `Wire.chainText` reports its failure with the soft decoder's text
`ResourceLimit: decision predicate <name>` before `validateSoft`, as `decodeSoftSource` orders them. That is the
limit Python's chain check already enforces on every soft document, so the change refuses in Lean exactly the
documents Python refuses for it (S1's `readings-validate` included); no S1 theorem statement changes, every S1
statement is used as merged, and S1's case kinds answer byte-identically on every document Python admits (F20). The blocks are statement schemata: binders shown once are
repeated where a later statement abbreviates them;
`(D) (h) (hch) (hs)` abbreviates `(D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
(hs : superposable D = true)`.

As built (2026-10-03), the statements of 8.3 to 8.5 are where these blocks put them, with their proofs spread over
helper files of `lean/VE/Readings/` that `lean/READINGS.md` lists (`SupSlot`, `Labels`, `SupEnv`, `Asserted`,
`Assertions`, `ChoiceValid`, `ChoiceTyped`, `Situation`, `SupConflict`, `BaseDown`, `SupWitness`, `BaseUp`,
`UpPremises`, `UpSlot`, `SupFree`, `SupAll`, `ChoiceWF`, `Strings`); 8.5 is `Route.lean` (the route of 1.1 and the
regenerated elaboration), `SupWire.lean` (its structures and decoders, namespace `VE.Readings.Wire`),
`SupWireSound.lean` (its two theorems, which need `superpose_all` and so cannot sit in `Wire.lean` below it) and
`SupRun.lean` (the case kinds), which `Run.lean` dispatches to.

### 8.2 `Compose/Adjoin.lean` (composition.md 9.5, verbatim)

```lean
import VE.Compose.Slot

namespace VE.Compose
universe u

/-- B with one new element that lies in no sort and in no tuple. -/
def adjoinOne (B : VE.Structure.{u}) : VE.Structure.{u} where
  Carrier := Option B.Carrier
  domain s v := ∃ x, v = some x ∧ B.domain s x
  constant c := (B.constant c).map some
  relation p vs := ∃ xs, vs = xs.map some ∧ B.relation p xs

theorem adjoin_term (B : VE.Structure.{u}) (ρ : VE.Valuation B) (t : VE.Term) :
  t.denote (adjoinOne B) (ρ.map some) = (t.denote B ρ).map some
theorem adjoin_denote (B : VE.Structure.{u}) (φ : VE.Formula) (ρ : VE.Valuation B) :
  φ.denote (adjoinOne B) (ρ.map some) ↔ φ.denote B ρ
theorem adjoin_admissible (E : VE.Environment) (B : VE.Structure.{u}) : (adjoinOne B).Admissible E ↔ B.Admissible E
theorem adjoin_nonempty (B : VE.Structure.{u}) : Nonempty (adjoinOne B).Carrier
theorem adjoin_baseAdmissibleP (X : VE.SoftNorms.SoftDoc) (P : List VE.Formula) (B : VE.Structure.{u}) :
  BaseAdmissibleP X P (adjoinOne B) ↔ BaseAdmissibleP X P B
end VE.Compose
```

### 8.3 `Readings/Choice.lean`

```lean
import VE.Readings.Lines
import VE.Compose.Adjoin

namespace VE.Readings
open VE.Norms (Sat envAt size bindAll atom)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate limPremises limPremisesLabelled)
open VE.Compose (Content Labelled)
universe u

/-! ## Choices (1.2) -/

abbrev Choice := List (String × Nat)
def Choice.index (c : Choice) (s : String) : Option Nat := (c.find? (·.1 == s)).map (·.2)
def labelOf (a : Candidate) (axis : String) : Option String := (a.labels.find? (·.1 == axis)).map (·.2)
/-- The open set a narrowing is in force on: its set at the active version. -/
def inForce (D : Doc) (N : Narrowing) : Option ReadingSet :=
  D.sets.find? (fun R => R.id == N.set && R.version == N.version)
/-- The shape part of what today's `validate_couplings` requires (7; not its shared-value or satisfiability checks):
    at least two sets, none twice, each an open set at its active version, every candidate of which is labelled on
    the axis. -/
def couplingShape (D : Doc) (K : Coupling) : Bool :=
  decide (2 ≤ K.sets.length) && decide (K.sets.map (·.1)).Nodup &&
    K.sets.all (fun x => D.sets.any (fun R => R.id == x.1 && R.version == x.2 &&
      R.candidates.all (fun a => (labelOf a K.axis).isSome)))
/-- The shape of a narrowing in force as today's `validate_narrowings` requires it (7): it keeps at least one
    candidate and only candidates of its set. A narrowing not in force adds nothing (1.2). -/
def narrowingShape (D : Doc) (N : Narrowing) : Bool :=
  match inForce D N with
  | some R => !N.keeps.isEmpty && N.keeps.all (fun x => R.candidates.any (·.id == x))
  | none => true
/-- ⌈log₂ k⌉: the least b with k ≤ 2^b. -/
def bitsOf (k : Nat) : Nat := ((List.range (k + 1)).find? (fun b => k ≤ 2 ^ b)).getD k
def bitName (n j : Nat) : String := "ve__bit__" ++ toString n ++ "__" ++ toString j
def setSize (D : Doc) (m : Nat) : Nat := (D.sets[m]?.map (·.candidates.length)).getD 0
def bitDecls (D : Doc) : List (String × List String) :=
  (List.range D.sets.length).flatMap (fun m =>
    (List.range (bitsOf (setSize D m))).map (fun j => (bitName (m + 1) j, ["ve__reading"])))
/-- The frame declares neither the constant `ve__here` nor a bit predicate of the choice vocabulary (1.8, DRI
    ruling 1); the wire decoders refuse every `ve__` name, so a decoded document always satisfies it. -/
def choiceFresh (D : Doc) : Bool :=
  D.frame.soft.E.constants "ve__here" == none && (bitDecls D).all (fun d => D.frame.soft.E.predicates d.1 == none)
def itemUnit : Item → String
  | .fixed u _ _ => u
  | .bar u _ => u
  | .set R => R.unit
/-- Every item stands for its own unit, as today's decoders require (1.8). -/
def unitsDistinct (D : Doc) : Bool := decide (D.items.map itemUnit).Nodup
/-- 1.1 row 2 and 1.8: distinct set ids, every open set with a candidate, every candidate with content; the couplings
    and narrowings in today's shape, with distinct ids; the frame free of the choice vocabulary. The Lean
    counterpart of the shape part of the decoder checks of 7, and of that part only. -/
def supReady (D : Doc) : Bool :=
  decide (D.sets.map (·.id)).Nodup &&
    D.sets.all (fun R => !R.candidates.isEmpty && R.candidates.all (·.content.isSome)) &&
    decide (D.couplings.map (·.id)).Nodup && D.couplings.all (couplingShape D) &&
    decide (D.narrowings.map (·.id)).Nodup && D.narrowings.all (narrowingShape D) && choiceFresh D &&
    unitsDistinct D
def complete (D : Doc) (c : Choice) : Bool :=
  c.map (·.1) == D.sets.map (·.id) && c.all (fun x => (candidate D x.1 x.2).isSome)
/-- Consecutive sets of the coupling take candidates with one label on the axis. -/
def couplingHolds (D : Doc) (c : Choice) (K : Coupling) : Bool :=
  (K.sets.zip K.sets.tail).all (fun (x, y) =>
    match c.index x.1, c.index y.1 with
    | some i, some j => match (candidate D x.1 i).bind (labelOf · K.axis), (candidate D y.1 j).bind (labelOf · K.axis) with
      | some l, some l' => l == l'
      | _, _ => false
    | _, _ => false)
def narrowingHolds (D : Doc) (c : Choice) (N : Narrowing) : Bool :=
  match inForce D N with
  | some R => match c.index R.id with
    | some i => (R.candidates[i]?.map (fun a => N.keeps.contains a.id)).getD false
    | none => false
  | none => true
def compatible (D : Doc) (c : Choice) : Bool :=
  complete D c && D.couplings.all (couplingHolds D c) && D.narrowings.all (narrowingHolds D c)
def Compatible (D : Doc) (c : Choice) : Prop := compatible D c = true
/-- Every fixed unit and the chosen candidate of every open set, under their own names (S1's build). -/
def choiceDoc (D : Doc) (c : Choice) : RightsDoc × List VE.Formula :=
  build D (fun _ => true) (fun R => (c.index R.id).bind (R.candidates[·]?))
def maxChoices : Nat := 64
/-- The compatible choices in canonical order (sets in source order, candidates by index), cut after maxChoices + 1. -/
def choices (D : Doc) : List Choice
theorem choices_spec (D : Doc) (hr : supReady D = true) (hle : (choices D).length ≤ maxChoices) (c : Choice) :
  c ∈ choices D ↔ Compatible D c
/-- 4.1 step 3 as built (review A1 of 2026-10-03): Lean decides that no choice is compatible by its own search. -/
theorem exists_compatible_of_choices (D : Doc) (h : (choices D).isEmpty = false) : ∃ c, Compatible D c
theorem no_compatible_of_choices (D : Doc) (hr : supReady D = true) (h : (choices D).isEmpty = true) :
  ¬ ∃ c, Compatible D c
/-- DRI ruling 5 (2026-10-03): the route's soft check of every compatible choice's document, up to maxChoiceChecks. -/
def maxChoiceChecks : Nat := 1024
def checkedChoices (D : Doc) : List Choice      -- the compatible choices, cut after maxChoiceChecks + 1
def choicesSoftChecked (D : Doc) : Bool :=
  decide ((checkedChoices D).length ≤ maxChoiceChecks) &&
    (checkedChoices D).all (fun c => VE.SoftNorms.WellFormedSoft (choiceDoc D c).1.soft)

/-! ## The choice vocabulary and the atoms (1.3) -/

def here : VE.Term := .const "ve__here"
def conj : List VE.Formula → VE.Formula
  | [] => .top
  | [a] => a
  | a :: as => .and a (conj as)
def disj : List VE.Formula → VE.Formula
  | [] => .bottom
  | [a] => a
  | a :: as => .or a (disj as)
def lit (n j : Nat) (b : Bool) : VE.Formula :=
  if b then .unary (bitName n j) here else .not (.unary (bitName n j) here)
/-- The pattern of the n-th set (1-based) with k candidates spelling i. -/
def pattern (n k i : Nat) : VE.Formula := conj ((List.range (bitsOf k)).map (fun j => lit n j (i.testBit j)))
/-- χ_{s,i}; ⊥ when s is no open set or i is no candidate of it. (`atom` is W1's predicate atom; this is the choice's.) -/
def choiceAtom (D : Doc) (s : String) (i : Nat) : VE.Formula :=
  match D.sets.findIdx? (·.id == s) with
  | some m => if i < setSize D m then pattern (m + 1) (setSize D m) i else .bottom
  | none => .bottom
def atoms (D : Doc) (A : Choice) : List VE.Formula := A.map (fun x => choiceAtom D x.1 x.2)
def choiceEnv (D : Doc) (E : VE.Environment) : VE.Environment :=
  if D.sets.isEmpty then E else
  { sorts := E.sorts ++ ["ve__reading"],
    constants := fun x => if x == "ve__here" then some "ve__reading" else E.constants x,
    predicates := fun p => match (bitDecls D).find? (·.1 == p) with
      | some d => some d.2
      | none => E.predicates p }

/-! ## The superposed document (1.4) -/

def qualify (k : Nat) (n : String) : String := "rd-" ++ toString k ++ "-" ++ n
/-- The 1-based position of candidate i of the m-th set in the canonical order. -/
def position (D : Doc) (m i : Nat) : Nat := ((D.sets.take m).map (·.candidates.length)).sum + i + 1
/-- Candidate i of the m-th set declares the author rule name n. -/
def declaresRule (D : Doc) (m i : Nat) (n : String) : Bool :=
  (((D.sets[m]?).bind (·.candidates[i]?)).bind (·.content)).any (fun c => c.declared.contains ("rule", n))
/-- The origin of a rule name of sup D (1.5): the candidate (set 0-based, index) whose qualified copy it is; none for
    a fixed rule's name. Defined on the names of sup D and not on author names: an interface name is declared by
    every candidate of its set and has no one origin (the name map goes through qName instead). -/
def origin (D : Doc) (n : String) : Option (Nat × Nat) :=
  (List.range D.sets.length).findSome? (fun m =>
    ((List.range (setSize D m)).find? (fun i =>
      (((D.sets[m]?).bind (·.candidates[i]?)).bind (·.content)).any
        (fun c => c.declared.any (fun d => qualify (position D m i) d.2 == n)))).map (fun i => (m, i)))
/-- The qualified copies of an interface rule name, in candidate order; [n] for a fixed name. -/
def copies (D : Doc) (n : String) : List String :=
  match D.sets.findIdx? (fun R => (interfaceOf R).contains ("rule", n)) with
  | some m => (List.range (setSize D m)).map (fun i => qualify (position D m i) n)
  | none => [n]
def copyOver (D : Doc) (N : SoftNode) : SoftNode := { N with over := N.over.flatMap (copies D) }
def copyCites (D : Doc) (cs : List (String × List String)) : List (String × List String) :=
  cs.flatMap (fun kv => if kv.1.startsWith "over:" then (copies D (kv.1.drop 5)).map (fun n => ("over:" ++ n, kv.2))
                        else [kv])
/-- A fixed content in sup D: its over and cites entries on interface names name every copy (S2a: norms). -/
def copyContent (D : Doc) : Content → Content
  | .norm N => .norm (copyOver D N)
  | c => c
/-- Candidate i of the m-th set: gated and qualified (S2a: assertions and norms; the other contents are S2b's). -/
def gateContent (D : Doc) (m i : Nat) : Content → Content
  | .assertion φ => .assertion (.implies (pattern (m + 1) (setSize D m) i) φ)
  | .norm N =>
    let χ := pattern (m + 1) (setSize D m) i
    .norm { N with name := qualify (position D m i) N.name, guard := .and N.guard χ,
                   exception := N.exception.map (fun e => { e with sufficient := e.sufficient.map (fun C => .and C χ) }) }
  | c => c
def supFrame (D : Doc) : RightsDoc := { D.frame with soft := { D.frame.soft with E := choiceEnv D D.frame.soft.E } }
def sup (D : Doc) : RightsDoc × List VE.Formula :=
  (D.items.foldl (fun acc it => match it with
    | .fixed _ c cs => ((place acc.1.1 (copyContent D c) (copyCites D cs), acc.1.2 ++ asserted c), acc.2)
    | .bar _ b => (({ acc.1.1 with bars := acc.1.1.bars ++ [b] }, acc.1.2), acc.2)
    | .set R =>
      ((List.range R.candidates.length).foldl (fun acc' i =>
        match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
        | some (c, cs) => let g := gateContent D acc.2 i c
                          (place acc'.1 g cs, acc'.2 ++ asserted g)
        | none => acc') acc.1, acc.2 + 1)) ((supFrame D, []), 0)).1

/-! ## Owners and Choice_D (1.5, 1.6) -/

/-- The owners of a generated key of sup D (1.5); [] among them means the fixed units alone generate it. -/
def owners (D : Doc) (k : GenKey) : List (List (Nat × Nat))
def fixedGenerated (D : Doc) (k : GenKey) : Bool := (owners D k).contains []
def atomAt (D : Doc) (o : Nat × Nat) : VE.Formula := choiceAtom D ((D.sets[o.1]?.map (·.id)).getD "") o.2
def quietFormula (D : Doc) (g : GenKey × String × List String) : VE.Formula :=
  bindAll g.2.2 (.implies (atom g.2.1 g.2.2) (disj ((owners D g.1).map (fun o => conj (o.map (atomAt D))))))
def label (R : ReadingSet) : String := R.id ++ "@" ++ toString R.version
def onePremises (D : Doc) : Labelled :=
  (List.range D.sets.length).filterMap (fun m => (D.sets[m]?).bind (fun R =>
    let k := R.candidates.length
    let unused := (List.range (2 ^ bitsOf k)).filter (k ≤ ·)
    if unused.isEmpty then none
    else some ("readings:" ++ label R ++ ":one", conj (unused.map (fun i => .not (pattern (m + 1) k i))))))
/-- The keys of sup D with exactly one owner, under that candidate's label; then every other key that is not
    fixed-generated, under its own label (keys in genKeys order). -/
def quietOwn (D : Doc) : Labelled :=
  (List.range D.sets.length).flatMap (fun m => (D.sets[m]?).toList.flatMap (fun R =>
    (List.range R.candidates.length).filterMap (fun i =>
      let mine := (genKeys (sup D).1).filter (fun g => owners D g.1 == [[(m, i)]])
      if mine.isEmpty then none
      else some ("readings:" ++ label R ++ ":" ++ toString i ++ ":quiet", conj (mine.map (quietFormula D))))))
/-- The source key in colon form (1.6); only the outweighs form is reachable in S2a. -/
def keyLabel : GenKey → String
  | .excepted r b => "excepted:" ++ r ++ (b.map (":" ++ ·)).getD ""
  | .off r b π => "off:" ++ r ++ (b.map (":" ++ ·)).getD "" ++ ":" ++ π
  | .outweighs a L H => "outweighs:" ++ a ++ ":" ++ L ++ ":" ++ H
  | .lim L a => "lim:" ++ L ++ ":" ++ a
  | .cond L a c => "cond:" ++ L ++ ":" ++ a ++ ":" ++ c
  | .aimed m => "aimed:" ++ m
def quietShared (D : Doc) : Labelled :=
  ((genKeys (sup D).1).filter (fun g => !fixedGenerated D g.1 &&
      ((owners D g.1).length != 1 || (owners D g.1).any (·.length != 1)))).map
    (fun g => ("readings:quiet:" ++ keyLabel g.1, quietFormula D g))
def couplingPremises (D : Doc) : Labelled :=
  D.couplings.filterMap (fun K =>
    let body := (K.sets.zip K.sets.tail).flatMap (fun (x, y) =>
      match D.sets.find? (·.id == x.1), D.sets.find? (·.id == y.1) with
      | some R, some R' => (List.range R.candidates.length).flatMap (fun i => (List.range R'.candidates.length).filterMap (fun j =>
          if (R.candidates[i]?.bind (labelOf · K.axis)) != (R'.candidates[j]?.bind (labelOf · K.axis))
          then some (.not (.and (choiceAtom D R.id i) (choiceAtom D R'.id j))) else none))
      | _, _ => [])
    if body.isEmpty then none else some ("coupling:" ++ K.id, conj body))
def narrowingPremises (D : Doc) : Labelled :=
  D.narrowings.filterMap (fun N => (inForce D N).bind (fun R =>
    let dropped := (List.range R.candidates.length).filter (fun i =>
      !((R.candidates[i]?.map (fun a => N.keeps.contains a.id)).getD true))
    if dropped.isEmpty then none
    else some ("narrowing:" ++ N.id, conj (dropped.map (fun i => .not (choiceAtom D R.id i))))))
def choiceLabelled (D : Doc) : Labelled :=
  onePremises D ++ quietOwn D ++ quietShared D ++ couplingPremises D ++ narrowingPremises D
def choicePremises (D : Doc) : List VE.Formula := (choiceLabelled D).formulas
def choiceCore (D : Doc) : List VE.Formula := (onePremises D ++ couplingPremises D ++ narrowingPremises D).formulas
def gatedRel (D : Doc) : Labelled := []                                      -- S3
def slotLabelled (D : Doc) : Labelled := limPremisesLabelled (sup D).1 ++ choiceLabelled D ++ gatedRel D
def slotP (D : Doc) : List VE.Formula := (slotLabelled D).formulas
def slotUnder (D : Doc) (A : Choice) : List VE.Formula := slotP D ++ atoms D A

/-! ## Superposable (1.8) -/

/-- The rule named n that a content declares (S2a: a norm content's rule when it has that name). -/
def ruleNamed (c : Content) (n : String) : Option SoftNode
def uniformPrecedence (D : Doc) : Bool
theorem uniformPrecedence_spec (D : Doc) : uniformPrecedence D = true ↔
  ∀ u c cs, Item.fixed u c cs ∈ D.items → ∀ N, c = .norm N → ∀ n ∈ N.over, ∀ R ∈ D.sets, ("rule", n) ∈ interfaceOf R →
    ∀ a ∈ R.candidates, ∀ b ∈ R.candidates, ∀ Na Nb, a.content.bind (ruleNamed · n) = some Na →
      b.content.bind (ruleNamed · n) = some Nb → ∀ m, m ∈ Na.over ↔ m ∈ Nb.over
def superposable (D : Doc) : Bool := supReady D && uniformPrecedence D && sideWF D (sup D)

/-! ## The name map and the pulled structure (1.7) -/

/-- The name a declared rule name n of c's document takes in sup D: found through the set that declares n (an
    interface name is declared by every candidate of its set, so the set and not the name decides; by
    distinctAcrossSets at most one set declares n) and qualified by the candidate c takes in that set when that
    candidate declares n; itself for a fixed name. -/
def qName (D : Doc) (c : Choice) (n : String) : String :=
  match D.sets.findIdx? (fun R => (declaredBy R).contains ("rule", n)) with
  | some m => match c.index ((D.sets[m]?.map (·.id)).getD "") with
    | some i => if declaresRule D m i n then qualify (position D m i) n else n
    | none => n
  | none => n
def qualifyKey (D : Doc) (c : Choice) : GenKey → GenKey
  | .excepted r b => .excepted (qName D c r) b
  | .off r b π => .off (qName D c r) b π
  | k => k                                                                   -- outweighs; lim, cond, aimed: S2b
def nameMap (D : Doc) (c : Choice) (p : String) : String :=
  match (genKeys (choiceDoc D c).1).find? (·.2.1 == p) with
  | some g => (((genKeys (sup D).1).find? (·.1 == qualifyKey D c g.1)).map (·.2.1)).getD p
  | none => p
/-- The complete vocabulary of c's document. -/
def choiceEnvFull (D : Doc) (c : Choice) : VE.Environment :=
  envAt (soften (correlate (choiceDoc D c).1)) (size (soften (correlate (choiceDoc D c).1)))
def pull (D : Doc) (c : Choice) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun p vs => (choiceEnvFull D c).predicates p ≠ none ∧ S.relation (nameMap D c p) vs }
def Encodes (D : Doc) (c : Choice) (S : VE.Structure.{u}) : Prop :=
  ∀ R ∈ D.sets, ∀ i, i < R.candidates.length → ((choiceAtom D R.id i).denote S [] ↔ (R.id, i) ∈ c)
/-- S' is S with only the choice vocabulary of D reinterpreted: its sort, its constant and its bit predicates. -/
def ChoiceExtension (D : Doc) (S S' : VE.Structure.{u}) : Prop :=
  ∃ (R : String → List S.Carrier → Prop) (dom : String → S.Carrier → Prop) (k : String → Option S.Carrier),
    S' = { S with relation := R, domain := dom, constant := k } ∧
    (∀ p, p ∉ (bitDecls D).map (·.1) → ∀ vs, R p vs ↔ S.relation p vs) ∧
    (∀ σ, σ ≠ "ve__reading" → dom σ = S.domain σ) ∧ (∀ x, x ≠ "ve__here" → k x = S.constant x)
/-- The complete vocabulary every reading shares: the author's, the regulated and defined predicates, and the
    decision predicates of the fixed units that depend on no open set. -/
def sharedEnv (D : Doc) : VE.Environment :=
  envAt (soften (correlate (free D).1)) (size (soften (correlate (free D).1)))
end VE.Readings
```

Notes for the review. `sup` folds over the items with the index of the current set beside the document, so that
candidate `i` of the `m`-th set is gated by `pattern (m + 1) (setSize D m) i` and named by `position D m i`; a
candidate's `cites` are placed as written, and `asserted g` of a gated assertion is `χ → φ`. `copies` and `copyCites`
are the whole of A1's mapping on these chains; `copyContent` leaves every content that is not a norm as it is,
because S2a never reaches a rights content (chain ≠ rights). `owners` is executable from `collidingPairs
(correlate (sup D).1)` and `origin`, applied to the rule names of the keys of `genKeys (sup D).1`, which are names of
`sup D` (qualified for a candidate's rule, the author's for a fixed one); its specification is 1.5. `origin` is not
applied to author names: `qName` finds the declaring set and the candidate the choice takes there, so that under
every choice the name map of an interface name lands on the chosen copy (M1: `nameMap D [(rs1, 1)]` sends
`soft__excepted__no_deception` to `ex₂`, and `nameMap D [(rs1, 0)]` is the identity because candidate 0's rule is
strict and has no key). `supReady`'s coupling and narrowing conjuncts mirror the shape checks of `validate_couplings`
and `validate_narrowings` on the decoded document and no other check of theirs (7): without them `couplingHolds` and
`couplingPremises` disagree on a missing label, and both would read a stale reference as the active set. `quietShared` takes every key that is not fixed-generated and
whose owners are not one single candidate, that is: several owners, or an owner that is a pair of candidates.
`keyLabel` writes S1's six key forms in colon form; only the outweighs form is reachable in S2a. `superposable` runs the chain's well-formedness
on `sup D` (S1's `sideWF`), which is what makes `sup_wellFormed` definitional: a theorem deriving it from the
candidates' documents would need the chain's size limits to be monotone, which they are not (the superposed tree
is larger than any choice's). `pull` uses the complete vocabulary of the choice's document and not its base
vocabulary so that it applies to expansions as well as to bases (`superpose_situation`); on a base the two agree,
since a base has no true tuple on a regulated predicate. `sharedEnv` is what every assertion in force is well-formed
over: a fixed assertion is checked in `free D` and an assertion candidate in `one D s i`, whose document is `free D`'s
whenever the set holds an assertion (S1 1.3, 1.4; `asserted_shared`, 8.4).

### 8.4 `Readings/Superpose.lean`

```lean
import VE.Readings.Choice

namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size elaborate targets)
open VE.SoftNorms (SoftDoc soften ValueSoft circ)
open VE.Rights (RightsDoc correlate limPremises BaseAdmissibleR RightsConflictFree)
open VE.Compose (BaseAdmissibleP ConflictFreeP SlotWellFormed backgroundP backgroundValidP slotConflictFreeCheck adjoinOne)
universe u

/-! ## Identity, well-formedness, the slot -/

theorem sup_no_sets (D : Doc) (h : D.sets = []) :
  sup D = build D (fun _ => true) (fun _ => none) ∧ choicePremises D = [] ∧ slotP D = limPremises (sup D).1
/-- Definitional: superposable D runs the chain's check on sup D. Stated so that the instance is a checked fact. -/
theorem sup_wellFormed (D : Doc) (hs : superposable D = true) :
  chainWF D.chain (sup D).1 = true ∧ WellFormedSoft (correlate (sup D).1) = true
/-- Needs the cross-set check of S1 4.3, a conjunct of WellFormedDoc: without it two chosen candidates could declare
    one name. By DRI ruling 5 (2026-10-03) the soft check of the choice's document is the route's runtime check
    `choicesSoftChecked`, discharged by the replays (`SupReplay.checked`); the unconditional statement is a
    follow-up item and is not claimed. -/
theorem choice_wellFormed (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights) (hs : superposable D = true)
    (hw : choicesSoftChecked D = true) (c : Choice) (hc : Compatible D c) : sideWF D (choiceDoc D c) = true
theorem asserted_shared (D : Doc) (h : WellFormedDoc D = true) (hr : supReady D = true) (c : Choice)
    (hc : Compatible D c) :
  ∀ a ∈ (choiceDoc D c).2, a.WellFormed (sharedEnv D) []
theorem slot_wellFormed (D) (h) (hch) (hs) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome) :
  SlotWellFormed (correlate (sup D).1) (slotUnder D A)
theorem slot_wellLabelled (D) (h) (hch) (hs) : (slotLabelled D).wellLabelled = true

/-! ## Every admissible base of sup D is one compatible choice -/

theorem encodes_unique (D) (h) (hch) (hs) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) :
  ∃ c, Compatible D c ∧ Encodes D c B ∧ ∀ c', complete D c' = true → Encodes D c' B → c' = c
theorem encodes_atoms (D) (c : Choice) (hc : complete D c = true) (S : VE.Structure.{u}) (he : Encodes D c S)
    (A : Choice) : Sat S (atoms D A) ↔ ∀ x ∈ A, x ∈ c

/-! ## Faithfulness (1.4, 4.3) -/

/-- 2.3 of the plan: where exactly c's atoms hold, the superposed document decides every act as c's document does on
    the pulled structure. On these chains hq is not needed (an unchosen rule is not live); it is stated because S2b's
    bar case needs it (F21), so that S2b removes only hch. -/
theorem superpose_faithful (D) (h) (hch) (hs) (c : Choice) (hc : Compatible D c) (S : VE.Structure.{u})
    (he : Encodes D c S) (hq : Sat S (choicePremises D)) (r : Regulated)
    (hr : r ∈ (correlate (choiceDoc D c).1).T.regulated) (vs : List S.Carrier) :
  ValueSoft (correlate (sup D).1) r S vs = ValueSoft (correlate (choiceDoc D c).1) r (pull D c S) vs

/-- Bases correspond, downward. -/
theorem base_down (D) (h) (hch) (hs) (c) (hc : Compatible D c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) (he : Encodes D c B) :
  BaseAdmissibleR (choiceDoc D c).1 (pull D c B)
/-- The two situations agree: every regulated predicate's value, every sentence over the shared vocabulary, and
    the assertions in force. -/
theorem superpose_situation (D) (h) (hch) (hs) (c) (hc : Compatible D c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) (he : Encodes D c B) :
  (∀ r ∈ (correlate (choiceDoc D c).1).T.regulated, ∀ vs : List B.Carrier,
     ValueSoft (correlate (sup D).1) r (expand (sup D).1 B) vs =
       ValueSoft (correlate (choiceDoc D c).1) r (expand (choiceDoc D c).1 (pull D c B)) vs) ∧
  (∀ φ : VE.Formula, φ.WellFormed (sharedEnv D) [] →
     (φ.denote (expand (sup D).1 B) [] ↔ φ.denote (expand (choiceDoc D c).1 (pull D c B)) [])) ∧
  (Sat (expand (sup D).1 B) (sup D).2 ↔ Sat (expand (choiceDoc D c).1 (pull D c B)) (choiceDoc D c).2)
/-- Bases correspond, upward; the extension pulls back to the structure it came from. -/
theorem base_up (D) (h) (hch) (hs) (c) (hc : Compatible D c) (B₀ : VE.Structure.{u}) (hne : Nonempty B₀.Carrier)
    (hB : BaseAdmissibleR (choiceDoc D c).1 B₀) :
  ∃ (R : String → List B₀.Carrier → Prop) (dom : String → B₀.Carrier → Prop) (k : String → Option B₀.Carrier),
    ChoiceExtension D { B₀ with relation := R } { B₀ with relation := R, domain := dom, constant := k } ∧
    BaseAdmissibleP (correlate (sup D).1) (slotP D) { B₀ with relation := R, domain := dom, constant := k } ∧
    Encodes D c { B₀ with relation := R, domain := dom, constant := k } ∧
    ∀ p (vs : List B₀.Carrier), (pull D c { B₀ with relation := R, domain := dom, constant := k }).relation p vs ↔
      B₀.relation p vs                                                     -- finding 6: the extension over B₀'s carrier

/-! ## Conflict-freedom under every reading, in one check (4.4: no non-emptiness hypothesis on either side) -/

theorem superpose_conflict_iff (D) (h) (hch) (hs) (c) (hc : Compatible D c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (sup D).1) (slotP D) B) (he : Encodes D c B) :
  VE.Norms.ConflictFree (soften (correlate (sup D).1)) B ↔
    VE.Norms.ConflictFree (soften (correlate (choiceDoc D c).1)) (pull D c B)
theorem superpose_conflict_free (D) (h) (hch) (hs) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome) :
  ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A) ↔
    ∀ c, Compatible D c → (∀ x ∈ A, x ∈ c) → RightsConflictFree.{u} (choiceDoc D c).1
theorem superpose_conflict_witness {α : Type u} [DecidableEq α] (D) (h) (hch) (hs) (A : Choice)
    (t : String × List String × VE.Formula) (ht : t ∈ targets (soften (correlate (sup D).1)))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0))
    (hb : backgroundValidP (correlate (sup D).1) (slotUnder D A) M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
  ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
    BaseAdmissibleR (choiceDoc D c).1 (pull D c M.asStructure) ∧
    ¬ VE.Norms.ConflictFree (soften (correlate (choiceDoc D c).1)) (pull D c M.asStructure)

/-! ## ALL and the countermodel (4.5) -/

/-- checkCertificate on background′ ++ slot ++ atoms ++ layers ++ assertions ++ Γ for correlate (sup D).1. -/
def supCertificateCheck (D : Doc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  let X := correlate (sup D).1
  VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
    (backgroundP X (slotUnder D A) ++ elaborate (soften X).T ++ ((sup D).2 ++ Γ)) φ cert
/-- The finite validity of the base background with the slot and the atoms, and of the assertions and Γ read on the
    base through the outcome substitution. -/
def supModelCheck {α : Type u} [DecidableEq α] (D : Doc) (A : Choice) (Γ : List VE.Formula)
    (M : VE.FiniteModel α) : Bool :=
  let X := correlate (sup D).1
  backgroundValidP X (slotUnder D A) M && ((sup D).2 ++ Γ).all (fun a => (circ X a).eval M [])

/-- ALL under A: a certificate on sup D proves φ in every situation of every compatible reading that takes A's
    candidates, read in that reading's own document. No non-emptiness hypothesis: a base with no element is lifted
    by adjoinOne (adjoin_baseAdmissibleP, adjoin_denote with circ_canon), then base_up applies. Fallback if the
    lifting lemma fails in statement review: (hne : Nonempty B.Carrier) returns and every entailment says E11. -/
theorem superpose_all (D) (h) (hch) (hs) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheck D A Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleR (choiceDoc D c).1 B)
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
  φ.denote (expand (choiceDoc D c).1 B) []
/-- The plan's form, a corollary: over the author's base vocabulary the expansion changes nothing (canon_base). -/
theorem superpose_all_base (D) (h) (hch) (hs) (A) (hA) (hcf) (Γ) (φ)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (authorEnv D) []) (hφ : φ.WellFormed (authorEnv D) [])
    (cert) (accepted : supCertificateCheck D A Γ φ cert = true) (c) (hc) (hAc) (B : VE.Structure.{u})
    (hB : BaseAdmissibleR (choiceDoc D c).1 B) (ha : ∀ a ∈ (choiceDoc D c).2, a.WellFormed (authorEnv D) [])
    (hp : Sat B ((choiceDoc D c).2 ++ Γ)) :
  φ.denote B []

/-- A checked model on sup D is a situation of the reading its atoms encode; with φ it is a countermodel there.
    The premise model of 4.5 is the case Γ := [], φ := ⊥. -/
theorem superpose_countermodel {α : Type u} [DecidableEq α] (D) (h) (hch) (hs) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)) (hm : supModelCheck D A Γ M = true)
    (hn : (circ (correlate (sup D).1) φ).eval M [] = false) :
  ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
    BaseAdmissibleR (choiceDoc D c).1 (pull D c M.asStructure) ∧
    Sat (expand (choiceDoc D c).1 (pull D c M.asStructure)) ((choiceDoc D c).2 ++ Γ) ∧
    ¬ φ.denote (expand (choiceDoc D c).1 (pull D c M.asStructure)) []

/-! ## Dead readings and unsatisfiable readings (1.9) -/

def deadCheck (D : Doc) (s : String) (i : Nat) (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften (correlate (sup D).1)) 0) (choiceCore D) (.not (choiceAtom D s i)) cert
def unsatCheck (D : Doc) (cert : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften (correlate (sup D).1)) 0) (choiceCore D) .bottom cert
theorem dead_sound (D : Doc) (hr : supReady D = true) (s : String) (i : Nat) (cert : VE.Tableau.Certificate)
    (hd : deadCheck D s i cert = true) : ∀ c, Compatible D c → (s, i) ∉ c
theorem unsat_sound (D : Doc) (hr : supReady D = true) (cert : VE.Tableau.Certificate)
    (hu : unsatCheck D cert = true) : ¬ ∃ c, Compatible D c

/-! ## Formula-only documents: superposition is W2's shortcut (4.7) -/

theorem superpose_assertions (D : Doc) (h : WellFormedDoc D = true) (hr : supReady D = true)
    (hk : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ))
    (hn : D.couplings = [] ∧ D.narrowings = []) (S : VE.Structure.{u}) (hne : Nonempty S.Carrier) :
  (∃ S', ChoiceExtension D S S' ∧ Sat S' ((sup D).2 ++ choicePremises D)) ↔
  (Sat S (free D).2 ∧ ∀ R ∈ D.sets, ∃ a ∈ R.candidates, ∃ φ, a.content = some (.assertion φ) ∧ φ.denote S [])
end VE.Readings
```

Notes for the review. The chain hypothesis `hch` is what S2b removes: every statement is otherwise the one the
rights case must satisfy, with `limPremises (sup D).1` already in `slotP` and `BaseAdmissibleR` on the choice side.
`superpose_faithful` is the plan's pointwise statement; `superpose_situation` is its base-level corollary, by
induction over the dependency order of `sup D` (whose layers restrict to the choice's: a choice's dependency graph is
a subgraph of `sup D`'s up to the names), and is what `superpose_conflict_iff`, `superpose_all` and
`superpose_countermodel` use. `encodes_unique` asks `complete D c'` of the other choice: `Encodes` constrains only
the entries of open sets, so without it `c ++ junk` would encode too; and its `hs` carries `supReady`'s coupling and
narrowing conjuncts (1.8), without which a slot-admissible base could encode a complete choice that is not
`Compatible` (a coupled candidate without the axis label: `couplingHolds` false, no coupling premise; M17), and
`base_down`, `superpose_conflict_free` and `superpose_countermodel` would fall with it. The plan's `pull (ν) S` is replaced by `pull D c`
(14.4). `superpose_all` is stated per situation of a reading's document in its expansion, so that a conclusion about
a regulated predicate is covered (E10's one reading: every situation of that choice's document); its proof lifts an
empty base with `adjoinOne`, maps it up with `base_up`, applies `slot_route_intended` to the expansion of the
superposed base (an intended structure, by `hcf` and unique expansion), and transfers by `superpose_situation`;
`circ_canon` carries the truth of a sentence over the shared vocabulary between an expansion and its base, and
`adjoin_denote` carries it across the lift. `superpose_all_base` is the plan's statement. `superpose_conflict_free`
with `A` is the plan's at `A = []`; `A` is what lets a named reading be certified while another reading has a
conflict (4.5). `dead_sound` and `unsat_sound` need no chain: `choiceCore D` is propositional over the bits, and a
compatible choice gives a one-element admissible structure of the level-0 vocabulary that satisfies it with the
atom true. `superpose_assertions` drops the plan's admissibility hypothesis on `S`: the equivalence holds for any
structure, because the author's formulas mention no choice symbol (S1's reserved names, and on a `Doc` value
`choiceFresh` in `supReady`) and the choice vocabulary is the only difference between `S` and `S'`. `base_down`,
`base_up`, `superpose_conflict_free` and `superpose_assertions` hold in this form because `supReady` carries
`choiceFresh` (DRI ruling 1): without it each is false of a frame that declares the choice vocabulary (M19). `choice_wellFormed`'s size part is the one proof risk the review should
weigh: every check of the chain's well-formedness on a choice's document is a check on a sub-tree of `sup D`'s with
shorter names and smaller unfolded carve-outs, but the limits are counted on the whole document and the argument
must be made for each (13.5). As built (DRI ruling 5), the route runs that check on every compatible choice's
document at runtime (`choicesSoftChecked`, up to 1024 choices) and `choice_wellFormed` takes its success as `hw`.

### 8.5 `Route.lean`, `Wire.lean`, `Run.lean`

```lean
namespace VE.Readings.Wire
/-- The decoded document of a superposed case: S1's admission with couplings and narrowings decoded (4.1 step 1). -/
structure SupReplay where
  D : Doc
  wf : WellFormedDoc D = true
  soft : D.chain ≠ .rights
  sp : superposable D = true
  sat : (choices D).isEmpty = false               -- 4.1 step 3: never a verdict over no reading (review A1)
  checked : choicesSoftChecked D = true           -- DRI ruling 5: every compatible choice's document checked
def replaySup (j : Lean.Json) : Except String SupReplay
theorem readings_wire_satisfiable (j : Lean.Json) (r : SupReplay) (h : replaySup j = .ok r) : ∃ c, Compatible r.D c
theorem readings_wire_choice_wellFormed (j : Lean.Json) (r : SupReplay) (h : replaySup j = .ok r) :
    ∀ c, Compatible r.D c → sideWF r.D (choiceDoc r.D c) = true
structure CertificateReplay extends SupReplay where
  assumed : Choice
  hA : ∀ x ∈ assumed, (candidate D x.1 x.2).isSome
  Γ : List VE.Formula
  φ : VE.Formula
  hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) []
  hφ : φ.WellFormed (sharedEnv D) []
  conflictCerts : List (Option VE.Tableau.Certificate)
  cert : VE.Tableau.Certificate
def replayCertificate (j : Lean.Json) : Except String CertificateReplay
theorem readings_wire_all_sound (j : Lean.Json) (r : CertificateReplay) (h : replayCertificate j = .ok r)
    (hc : slotConflictFreeCheck (correlate (sup r.D).1) (slotUnder r.D r.assumed) r.conflictCerts = true)
    (ha : supCertificateCheck r.D r.assumed r.Γ r.φ r.cert = true) :
  ∀ c, Compatible r.D c → (∀ x ∈ r.assumed, x ∈ c) → ∀ B : VE.Structure.{u},
    BaseAdmissibleR (choiceDoc r.D c).1 B → Sat (expand (choiceDoc r.D c).1 B) ((choiceDoc r.D c).2 ++ r.Γ) →
    r.φ.denote (expand (choiceDoc r.D c).1 B) []
structure ModelReplay extends SupReplay where
  assumed : Choice
  Γ : List VE.Formula
  φ : VE.Formula
  hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) []
  hφ : φ.WellFormed (sharedEnv D) []
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)
def replayModel (j : Lean.Json) : Except String ModelReplay
theorem readings_wire_model_sound (j : Lean.Json) (r : ModelReplay) (h : replayModel j = .ok r)
    (hm : supModelCheck r.D r.assumed r.Γ r.M = true) (hn : (circ (correlate (sup r.D).1) r.φ).eval r.M [] = false) :
  ∃ c, Compatible r.D c ∧ (∀ x ∈ r.assumed, x ∈ c) ∧ Encodes r.D c r.M.asStructure ∧
    BaseAdmissibleR (choiceDoc r.D c).1 (pull r.D c r.M.asStructure) ∧
    Sat (expand (choiceDoc r.D c).1 (pull r.D c r.M.asStructure)) ((choiceDoc r.D c).2 ++ r.Γ) ∧
    ¬ r.φ.denote (expand (choiceDoc r.D c).1 (pull r.D c r.M.asStructure)) []
end VE.Readings.Wire
```

The decoders refuse a case whose document is not superposable with the finding of 1.8 and the enumerated route's
answer instead (`readings-choice`), never `separated: false`-style silence; a model whose base is not valid over the
level-0 vocabulary is `InvalidInput` with the model decoder's text, as today (`decodeModel_valid`). `Run.lean`
regenerates the `readings-elaborate` answer of section 3 and runs the case kinds; `readings-choice` runs
`VE.SoftNorms.Run` (or the norms logic of 1.1) on `choiceDoc D c` after `compatible D c = true`.

### 8.6 What is not claimed

No theorem about a rights document's superposition, a bar, a limitation or `right_lines` copies: S2b. No claim that
`sup D` is well-formed whenever every candidate's document is: `superposable` checks it. No entailment claim for a
document, or a named reading, whose conflict status is not CONFLICT-FREE (4.5). No claim about the English of
section 2. No completeness: a set that the search cannot classify within budget is UNKNOWN; `DeadReading` is emitted
only with a certificate. No claim that the enumeration beyond 64 choices could be avoided. No claim about
`norm-defaults@0` documents (4.10) or about a claim graph beside a content-bearing set (14.10). Python's search for
certificates and models is not verified; Lean checks what it finds.

## 9. Acceptance fixtures for item 1

Review protocol as composition.md 10: each reviewer derives the expectation from sections 1, 4 and 8 before reading
the expected column; a builder who finds one wrong reports it against this section instead of changing the fixture.

### 9.1 The plan's fixtures (S2a's share, composition.md 10.5)

| # | Unit | Input | Expected in S2a | Left to |
|---|---|---|---|---|
| F2 | C `u0165.s03` with narrowing `narrow-u0165-s03` (keeps strict, cites `u0166.s01`, `u0166.s04`) | the set of F1's shape plus the narrowing | `Choice_D` holds `narrowing:narrow-u0165-s03` = `¬χ_default`; every result whose certificate uses it lists it in `conditional_on` and shows E7 citing the two units' display numbers; the dropped candidate is not a `DeadReading`; removing the narrowing changes no identity of the set and no separation | — |
| F3 | C main document as S1's rerun built it (composition-s1-measured.md: the all-default document with `readings@1`, the strict/default force sets as open sets, 7 pairs on the run of 2026-10-02; the plan's ledger of 2026-09-30 counted 14 sets, 7 narrowed) | `readings-conflict`, `readings-model`, `readings-elaborate` | `superposable D = true` (every force set is a pair of twins with one `over` list); a conflict status under every reading from one certificate or one witness per target, never `pending`; a premise model for one choice and one per candidate that no narrowing of the run drops; with the atoms of the all-strict and of the all-default choice assumed, the premise and conflict results equal the lower route's on `choiceDoc D c` for those two choices (the shadow of 9.3), and equal the companion files `readings/all-strict.ve.md` and `readings/all-default.ve.md` where those are the same documents (the measured note records two units whose all-strict rule is over another environment's predicate: the rerun reports any difference); the sizes of `sup D` against the limits | the main translation itself: the `fill` instance (4.10) |
| F18 | synthetic: M9 | `readings-elaborate` | `ReadingsNotSuperposable: rs1, rs2` with cause `DependencyCycle: avoid_required, help_required, warn_required`; the enumerated route gives the verdict over 4 choices (CONFLICT-FREE under every reading; ALL for `∀agent ∀user. asks → warn_required`) | — |
| F20 | U translation, rights fixtures, discourse fixtures; and every document with `readings@1` on and no content-bearing set, M18's coupled formula-only document with two recorded narrowings included | `readings@1` off / on; M18 with no `--narrowing`, with `--narrowing n1` and with `--narrowing n2` | identities, statuses and verdicts byte-identical; `sup D` never built, `choiceCore D` never computed; M18: W2's `coupled-choices` verdict over two choices, and under either `--narrowing` today's one-choice answer, no `ReadingsUnsatisfiable` | — |
| F4, F6 to F10, F21 | UDHR units | — | the UDHR is a rights document on the enumerated route and over the 64-choice budget: its verdicts across readings stay UNKNOWN with W2's budget shape, and its rights report `per-choice rights elaboration pending` | S2b |

### 9.2 Lean and Python fixtures on one small document

`lean/VE/Readings/Examples.lean` as `#guard` lines and `example`s, and the same cases through the case kinds of
section 3 in `tests/test_readings_s2.py`. Environment K is composition-s1.md 9.2's (sorts `agent`, `user`; base
predicate `asks(agent, user)`; obligations `avoid_required`, `help_required`, deny by default, no dual; rules `S`,
`Df`; set `rs1` on `u1`, version 1, {0: `S`, 1: `Df`}; models `m0` (one agent `a`, one user `u`, `asks` empty) and
`m1` (`asks` = {(a, u)})). `b` abbreviates `.unary "ve__bit__1__0" (.const "ve__here")`; `χ₀ = .not b`, `χ₁ = b`;
`ex₂` abbreviates `soft__excepted__rd_2_no_deception`. Display numbers follow unit order: `u1` is sentence 1.

| # | Input | Expected |
|---|---|---|
| M1 | K1's document | `supReady`, `uniformPrecedence`, `superposable` true; `(sup D).1.soft.E`: sorts `[agent, user, ve__reading]`, constant `ve__here : ve__reading`, predicate `ve__bit__1__0 : [ve__reading]`; rules `rd-1-no-deception` (strict, guard `.and .top χ₀`) and `rd-2-no-deception` (default, guard `.and .top χ₁`, exception unchanged: no sufficient condition); `genKeys (sup D).1` = one key `excepted rd-2-no-deception` named `ex₂` with sorts `[agent, user]`; `choiceLabelled D` = `[("readings:rs1@1:1:quiet", bindAll [agent, user] (.implies (atom ex₂ [agent, user]) b))]`; no `:one` label; `slotP D` = that formula; `choices D` = `[[(rs1, 0)], [(rs1, 1)]]`; `position` 1 and 2; `origin D "rd-2-no-deception" = some (0, 1)`, `origin D "rd-1-no-deception" = some (0, 0)`, `origin D "no-deception" = none`; `qName D [(rs1, 1)] "no-deception" = "rd-2-no-deception"` (the set `rs1` declares it, the choice takes candidate 1 there, candidate 1 declares it), `qName D [(rs1, 0)] "no-deception" = "rd-1-no-deception"`; `nameMap D [(rs1, 1)] "soft__excepted__no_deception" = ex₂`, identity on every other name; `nameMap D [(rs1, 0)]` the identity (candidate 0's rule is strict: no key) |
| M2 | M1; base `B₁` = `m0` with `ve__reading` = {e}, `ve__here` = e, bit {e}, `ex₂` {(a, u)}; `B₀` = the same with the bit empty and `ex₂` empty; `B₂` = bit empty, `ex₂` {(a, u)} | `B₁`: slot holds, `Encodes D [(rs1, 1)]`, outcome `avoid_required (a, u)` = `some false` in both `expand (sup D).1 B₁` and `expand (choiceDoc D [(rs1, 1)]).1 (pull D [(rs1, 1)] B₁)`; `(pull D [(rs1, 1)] B₁).relation "ve__bit__1__0" [e]` false and `"soft__excepted__no_deception" [a, u]` true. `B₀`: `Encodes D [(rs1, 0)]`, outcome `some true` on both sides. `B₂`: the quiescence premise fails (`ex₂` holds at (a, u) with the bit false), so `BaseAdmissibleP (correlate (sup D).1) (slotP D) B₂` is false: not a model, no choice; its finite form is refused by `backgroundValidP` with the label `readings:rs1@1:1:quiet` |
| M3 | M1 plus a fixed strict rule `never-avoid` on `−avoid_required`, guard `⊤` (K6's) | conflict target of `avoid_required`: witness `B₀` of M2 (choice 0: `rd-1-no-deception` and `never-avoid` both select at (a, u)); `superpose_conflict_witness` names `[(rs1, 0)]`; status CONFLICT, E12 with R4 naming *must*; under `A = [(rs1, 1)]` a certificate (`rd-2` is blocked by `never-avoid`), so CONFLICT-FREE under *should*, and `∀agent ∀user. ¬avoid_required` is certified under `A`: E12 with R2. Under `A = []` every entailment is `UNKNOWN (conflict status: CONFLICT)` |
| M4 | M1 plus a fixed strict rule `help-x` on `+help_required`, guard `⊤`; conclusions `φ = ∀agent ∀user. help_required`, `φ′ = ∀agent ∀user. avoid_required` | CONFLICT-FREE under every reading (two certificates); `φ`: ALL, the certificate's used leaves mention no bit of `rs1`: no `readings:` label, E26 with R2, E13 for sentence 1. `φ′`: SOME: a certificate under `[(rs1, 0)]` and the countermodel `B₁` of M2 under `[(rs1, 1)]`; E12 with R2 naming *must*, E12 with R3 naming *should* with the situation of 2.5 |
| M5 | M4 plus a fixed assertion unit `u2` (⊤) and narrowing `n1` (set `rs1`, version 1, keeps `S`'s id, cites `u2`) | `choiceLabelled D` = `[rs1@1:1:quiet, ("narrowing:n1", .not b)]`; `choices D` = `[[(rs1, 0)]]`; `φ′` is ALL with `conditional_on` `[narrowing:n1]`: E26, E3, E7 "Sentence 1 is not read as *should*, because of sentence 2."; no `DeadReading`; candidate 1 listed under `n1` |
| M6 | M1 plus set `rs2` on `u2` {0: strict `be-kind` on `+help_required`, 1: default `be-kind`}, labels `force` strict/default on both sets, coupling `c1` on `force` over `[rs1@1, rs2@1]`; `b₂` the bit of `rs2` | `coupling:c1` = `.and (.not (.and χ₀ b₂)) (.not (.and b (.not b₂)))`; `choices D` = `[[(rs1,0),(rs2,0)], [(rs1,1),(rs2,1)]]`; quiet labels `rs1@1:1:quiet` (`ex₂`) and `rs2@1:1:quiet` (`soft__excepted__rd_4_be_kind`); premise models: one per candidate, four in all. With M5's `n1` added: `choices D` = `[[(rs1,0),(rs2,0)]]`, `DeadReading: rs2:1` with a certificate of `.not b₂` from `choiceCore D`, E17 "No compatible way of reading the open sentences reads sentence 2 as *should*."; candidate 1 of `rs1` under `n1`, not dead |
| M7 | `rs1` = {0: `S`, 1: `Df`, 2: assertion `∀agent ∀user. asks`}; `b₀`, `b₁` its two bits | `bitsOf 3 = 2`; `χ₀ = .and (.not b₀) (.not b₁)`, `χ₁ = .and b₀ (.not b₁)`, `χ₂ = .and (.not b₀) b₁`; `readings:rs1@1:one` = `.not (.and b₀ b₁)`; `(sup D).2 = [.implies χ₂ (∀agent ∀user. asks)]`; `choiceLabelled D` = `[one, rs1@1:1:quiet]`; `choices D` has 3 entries; a model with `b₀` and `b₁` both true is rejected by the `:one` premise |
| M8 | fixed strict `base-x` on `+avoid_required`, guard `⊤` (`u0`); `rs1` on `u1` = {0: strict `waive-x` on `−avoid_required`, guard `asks`, over `[]`; 1: the same with over `[base-x]`}; fixed strict `stop-x` on `−avoid_required`, guard `⊤`, over `[waive-x]` (`u3`) | admitted by S1 (`waive-x` is an interface name; `stop-x` attached to `rs1`; the pair separated on `m1` with witness 1, value `false`). `uniformPrecedence D = false`, `superposable D = false`, `ReadingsNotSuperposable: rs1` with cause `precedence under waive-x`; enumerated: choice 0 CONFLICT (strict collision on `avoid_required` at `m0`: `base-x` and `stop-x` both select), choice 1 CONFLICT-FREE (`base-x` never selects: its child `waive-x` yields wherever `stop-x` does). **Mutation check**: with `uniformPrecedence` removed from `superposable`, the superposed document has no conflict (only `rd-2-waive-x`, whose `over` is `[base-x]`, is a child of `base-x`, not both copies; `stop-x` is a child of both copies; under choice 0 the unchosen `rd-2-waive-x` yields wherever `stop-x` does, so `base-x` never selects), so the shadow test of 9.3 disagrees with the enumerated route on this document; the check must fail then and pass with the condition in place |
| M9 | environment K plus obligation `warn_required(agent, user)`, act `{0} warn {1}`; fixed strict `f-warn` on `+warn_required`, guard `asks`; `rs1` on `u1` = {0: strict `r-a` on `+avoid_required`, guard `help_required(x, y)`; 1: strict `r-b` on `+help_required`, guard `warn_required(x, y)`}; `rs2` on `u2` = {0: strict `r-c` on `+warn_required`, guard `avoid_required(x, y)`; 1: strict `r-d` on `+warn_required`, guard `⊤`} | admitted by S1 (`rs1` separated on `m1` by `help_required (a, u)`: true under 1, false under 0; `rs2` on `m0` by `warn_required (a, u)`); every `one D s i` stratifies; `sup D` has the cycle `avoid_required → help_required → warn_required → avoid_required`: `superposable D = false`, `ReadingsNotSuperposable: rs1, rs2`, cause `DependencyCycle: avoid_required, help_required, warn_required`; `choices D` has 4 entries, each `choiceDoc` stratifies and is CONFLICT-FREE; `∀agent ∀user. asks → warn_required` is ALL on the enumerated route (E10 with R2, `<k>` = 2); E29 names sentences 1 and 2 |
| M10 | K with the `soft` block ranks `lo`, `hi`, `hi` outranks `lo`, outranking `holistic` decided by `unstated`; `rs1` = {0: `S`, 1: `Df` ranked `lo`}; fixed default `never-avoid-d` on `−avoid_required`, guard `⊤`, ranked `hi`, exception as `Df`'s (K21(c)'s rules) | `genKeys (sup D).1` has `excepted rd-2-no-deception`, `excepted never-avoid-d` and `outweighs avoid_required lo hi` (the pair `(rd-2-no-deception, never-avoid-d)`); `owners` of the outweighs key = `[[(0, 1)]]`, of `excepted never-avoid-d` = `[[]]`; `quietOwn D` = `[("readings:rs1@1:1:quiet", .and (∀∀. ex₂ → b) (∀∀. soft__outweighs__lo__hi__avoid_required → b))]`, `quietShared D = []`; under choice 0 the outweighs predicate is absent from `choiceDoc`, `pull` gives it no tuple and the slot forces its table empty |
| M10b | M10 without `never-avoid-d`, plus `rs2` on `u2` = {0: strict `be-firm` on `−avoid_required`, guard `⊤`; 1: default `be-firm`, ranked `hi`} | the outweighs key's owners = `[[(0, 1), (1, 1)]]`: `quietShared D` = `[("readings:quiet:outweighs:avoid_required:lo:hi", ∀∀. soft__outweighs__lo__hi__avoid_required → .and b b₂)]`; the parent plan's flagged precision (a disjunct that is a conjunction of two atoms) |
| M11 | K16: two formula sets with today's `models`, no content-bearing set | route `w2`: W2's code and verdicts, `sup D` not built; `superpose_assertions` as an `example` on a two-element structure |
| M12 | K19's document (rights chain, `rs9` {claim strict, claim default}) | route `enumerated` (`hch` fails), 2 choices, each `choiceDoc` checked by the rights route: premises `model` under each, CONFLICT-FREE under every reading; the rights report per choice; no finding |
| M13 | K15 ({`S`, `content: null`}) | route `pending`: every verdict across readings UNKNOWN, reason `non-assertion reading elaboration pending`; S1's report unchanged |
| M14 | K9: fixed strict `except-x` on `−avoid_required`, guard `asks`, over `[no-deception]`, with `rs1` = {`S`, `Df`} | `copies D "no-deception" = [rd-1-no-deception, rd-2-no-deception]`, `except-x`'s over in `sup D` names both; `uniformPrecedence D = true` (both twins have over `[]`); on `m1` under either choice the outcome at (a, u) is `some false` in `sup D` and in the choice's document (`except-x` selects, the twin yields through it); `superposable D = true` |
| M15 | the empty structure `E∅` (Carrier `Empty`) over K, and M1's document | `example`: `BaseAdmissibleR (choiceDoc D [(rs1, 0)]).1 E∅`; no `S'` with `ChoiceExtension D E∅ S'` is admissible for `(sup D).1.soft.E` (nothing denotes `ve__here`); `adjoinOne E∅` has one element, is `BaseAdmissibleR` for the choice's document (`adjoin_baseAdmissibleP` at `rights_is_slot`), and `base_up` applies to it; `ConflictFree` of any soft document holds of `E∅` (no typed tuple) |
| M16 | M1 with `Df` and `S` renamed to a 45-byte rule name | own names stay within `MAX_IDENTIFIER_BYTES` (16 + 45 bytes for the decision predicate) and `sup D`'s `soft__excepted__rd_2_…` does not (66 bytes): `sideWF D (sup D) = false` with the chain's own text for that limit, `ReadingsNotSuperposable: rs1` with that cause, the enumerated route over 2 choices. Lean's `chainWF` carries the limit as `namesFit` (DRI ruling 2), and `Wire.chainText` gives `ResourceLimit: decision predicate soft__excepted__rd_2_<name>` |
| M17 | the shape of couplings and narrowings (1.8, 7), on M6's document: (a) `rs1` and `rs2` without `force` labels, coupling `c1` on `force`; (b) M6 with a second coupling also named `c1`; (c) M6 with `c1` naming `rs2@2` while `rs2` is active at version 1; (d) M6 with `rs2` re-recorded at version 2 (the same two candidates; `c1` names `rs2@2`) plus a narrowing `n0` on `rs2@1` keeping the strict candidate's id | (a) Python and Lean's decoder: `CouplingLabelMissing: c1, rs1`; on the `Doc` as a Lean value `supReady D = false` (`couplingShape` fails), so no theorem of 8.4 that assumes `supReady` or `superposable` (`hr`, `hs`, `SupReplay.sp`) applies to it (`encodes_atoms`, which assumes neither, does), and what the conjunct excludes is visible: `couplingHolds D c c1 = false` for every one of the four complete choices while `couplingPremises D = []`, so a slot-admissible base of `sup D` would encode a complete choice that is not `Compatible` (`encodes_unique` would be false without the conjunct). (b) `invalid coupling`; `supReady D = false` (ids not `Nodup`). (c) `invalid coupling set`; `supReady D = false` (`rs2@2` is no open set at its active version), where `couplingHolds` and `couplingPremises` alone would have read `rs2` at version 1. (d) admitted by Python (`rs2@1` is a recorded version) and by Lean; `n0` is not in force (`inForce D n0 = none`: `D.sets` holds `rs2` at version 2), `narrowingShape D n0 = true`, `supReady D = true`, no `narrowing:n0` label, `choices D` as M6's, `n0` listed under `narrowings_stale` (6); stale narrowings stay inactive |
| M18 | two formula sets, no content-bearing set: `rs1` on `u1` = {0: assertion `∀agent ∀user. asks`, label `force` A; 1: assertion `∀agent ∀user. ¬asks`, label `force` B}, `rs2` on `u2` the same two assertions with labels A, B; coupling `c1` on `force` over `[rs1@1, rs2@1]`; narrowing `n1` (set `rs1`, version 1, keeps the A candidate), narrowing `n2` (set `rs2`, version 1, keeps the B candidate) | route `w2` (1.1 row 1, chosen at 4.1 step 2): W2's `coupled-choices` route over the two compatible choices A/A and B/B, with today's `models`, verdicts byte-identical to today's; `sup D` not built, `choiceCore D` not computed; no `ReadingsUnsatisfiable`, no `DeadReading`; `CouplingUnsatisfiable` not raised (today's `validate_couplings` finds A/A). Under `--narrowing n1` today's one-choice answer (A/A) with `narrowing: narrowing:n1`, under `--narrowing n2` likewise (B/B), unchanged (F20). As a Lean value: `supReady D = true`, `choices D = []` and `unsatCheck` would accept a certificate of `⊥` from `choiceCore D` (= `[coupling:c1, narrowing:n1, narrowing:n2]`): the refusal draft 1 raised and the route order now never reaches |
| M19 | the frame declares the choice vocabulary (DRI ruling 1): `KH`, M1's frame with the constant `ve__here : agent` and `rs1` = {0: assertion `⊤`, 1: assertion `⊥`}; `KB`, M1's frame with `ve__here : agent` and the predicate `ve__bit__1__0(agent)`, and `rs1` = {0: assertion `ve__bit__1__0(ve__here)`, 1: its negation} | both refused by the wire decoders with `InvalidInput: name ve__here begins with ve__` (Python and Lean); as Lean values `WellFormedDoc` holds (it cannot see the names), `choiceFresh` and so `supReady` and `superposable` are false, and no theorem of 8.4 applies. What the conjunct excludes is formal: on `KH` a slot-admissible base of `sup D` encoding `[(rs1, 0)]` whose `ve__here` is no agent pulls to a structure that is not admissible for the choice's document (`base_down` would fail), and on `KB` the gated assertions `¬b → b` and `b → ¬b` have no model while every structure satisfies one candidate (`superpose_assertions` would fail) |
| M20 | two open sets under one id `s`: `u1` = {0: assertion `∀agent ∀user. soft__excepted__no_deception`, 1: assertion `⊤`}, `u2` = {0: `Df`, 1: `S`} (finding 4) | `WellFormedDoc` holds (S1 checks candidate 0 of `u1` beside `Df`, whose decision predicate types the assertion); `supReady D = false` (set ids not distinct); for the choice `[(s, 0), (s, 0)]`, compatible, `(choiceDoc D c).2` is that assertion and it is not typed over `sharedEnv D`: the statement of `asserted_shared` without `hr` is false here. The same holds of a fixed assertion unit that shares its id with a norm unit attached to a set (`unitsDistinct`) |

### 9.3 Differential, shadow and pilots

- **Differential.** 1,000 seeded generated soft and norms documents with open sets (twins, mixed kinds, three to five
  candidates, couplings, narrowings, fixed rules over interface names with equal and with unequal `over` lists,
  colliding default pairs under both outranking flags, faulty sources): Python's `readings-elaborate` against Lean's,
  byte for byte; faulty sources rejected by both with one text.
- **Shadow of the theorems.** On every generated document with at most 64 compatible choices and `superposable D =
  true`, the superposed verdicts (conflict status, premise status and per-candidate statuses, ALL/SOME/NONE for
  three generated conclusions over the shared vocabulary) equal the enumerated route's over the same choices; every
  model found on the superposed route is pulled and checked by the lower route on the choice's document it encodes,
  and the outcomes agree on every regulated predicate. The mutation check of M8 is part of this test.
- **Dead readings.** On every generated document the candidates `dead_sound` certifies are exactly those no
  enumerated compatible choice takes (when at most 64).
- **Pilots.** The constitution's rerun document of S1 (F3) on the superposed route; the UDHR's translation on the
  enumerated route (over budget: the report says so); section 11's figures.
- **F20.** With `readings@1` off no file under `conformance/` changes and `python3 VE/Route/frozen.py` passes; with it
  on and no content-bearing set, every verdict is byte-identical to today's, M18 included (W2's `coupled-choices`
  over two choices; `--narrowing n1` and `--narrowing n2` as today).

### 9.4 The English

| # | Instance | Expected |
|---|---|---|
| G5 | E10 and E11 | never both in one report; E11 only under the fallback of 4.4 (none in this draft) |
| G6 | every sentence of section 2 rendered on M1 to M18 | no `ve__`, `rd-`, `soft__` or `rights__` substring; candidate rules named as written |
| G9 | every sentence of section 2 | no rendered sentence contains "may not" |
| N1 | E26 and E13 on M4's `φ` | the texts of 2.5; one derivation each |
| N2 | E12 on M4's `φ′` | two lines, naming *must* and *should*; the countermodel's situation includes "suppose the decider decides the exception applies to a and u" and no fact stated for the decision |
| N3 | E12 on M3's witness | names *must*; R4; the lower route's classification line follows with `no-deception` named as written and ` under rs1@1:0` |
| N4 | E26, E3, E7 on M5 | E7 cites sentence 2; the E3 list is the one narrowing line |
| N5 | E17 on M6 with `n1` | the text of 2.5; nothing for candidate 1 of `rs1` beyond E7 |
| N6 | E27 and E28 | E27 on a generated NONE document with 3 choices, then three E12 lines; E28 on a generated document with 65 choices, with the E12 of the countermodel found |
| N7 | E29 on M9 | the text of 2.5 |
| N8 | E8 | registered and gated on a hand-written certificate that uses `readings:rs1@1:1:quiet` of M1; no fixture of 9.2 produces one, and the rerun reports whether any pilot certificate does |

## 10. Limits, regeneration, Python, Rust

Limits: 64 candidates per set (W2) and 64 compatible choices on the enumerated route (W2's budget shape); couplings
at most 8 (rights 11); the chain's limits on `sup D` (`MAX_SORTS` 32 with one sort added, `MAX_PREDICATES` 256 with
the bits and the qualified decision predicates added, `MAX_IDENTIFIER_BYTES` 64 on qualified names,
`MAX_NODES` 10,000 on the unfolded tree); a limit reached by `sup D` is the finding of 1.8 and the enumerated route,
never a truth value; a limit reached by a choice's document is the lower route's `ResourceLimit`. Cost: one
elaboration of `sup D` per load, with one conflict certificate per target and one model per candidate; on the
enumerated route one lower-route check per compatible choice. Both are measured on the pilots (11), not assumed; the
plan's open question 5 (a per-component split) is the next design if `MAX_NODES` is reached.

Regeneration: `sup D`, `Choice_D`, the name map, the compatible choices and every formula evaluated are recomputed
from the decoded document at every trusted site and bound to the chain's document hash (4.2). Python: `ve/readings_sup.py`
regenerates `readings-elaborate`; `ve/readings_route.py` compares it with Lean's byte for byte on every load
(`CheckerUnavailable` on a difference); `ve/readings_verdicts.py` searches for certificates and models on `sup D` with
the existing prover and model search over the regenerated premise lists (a model first on a compatible choice's own
document, lifted to `sup D` as `base_up` builds it, then on `sup D`; the slot labels a certificate uses are the
ones it still needs when each is replaced by `⊤` in turn), enumerates compatible choices with today's `coupled_choices`
extended by the narrowings in force, and renders section 2 (`Wording`); `ve/document.py` replaces its
`superposition pending` branch by the verdicts of 4.5 and 4.6 and the UNKNOWN of 1.1. Rust: no elaboration; it
evaluates the Python-generated slot premises, assertions, conflict targets and conclusions of `sup D` on every model
shown, marked `untrusted: true`, and its values must agree with Lean's (regression evidence; plan open question 12).
Lean is the authority for every verdict.

## 11. The measured unlock

The plan names, for S2a (its section 6, row S2a):

| Text | What the plan expects | Baseline (composition-s1-measured.md, 2026-10-02) |
|---|---|---|
| Constitution (1,127 units, 184,893 bytes) | the main document's premises and conflict status leave UNKNOWN; the two companion documents (`readings/all-strict.ve.md`, `readings/all-default.ve.md`) become redundant | the rerun document (the all-default document with `readings@1` and 7 strict/default force sets as open sets): premises `UNKNOWN, superposition pending`; the main translation itself uses `norm-defaults@0` and is S1's abstention (4.10) |
| UDHR (130 units, 10,916 bytes) | none: a rights document on the enumerated route, over the 64-choice budget | 23 content-bearing sets; premises `UNKNOWN, superposition pending`; rights report `per-choice rights elaboration pending`; load 141.7 s |

The stage's rerun (`tools/readings_s2_pilot.py`) reports, per text: the route; for the constitution's rerun
document, `superposable` with its cause if false, the sizes of `sup D` against the limits, the conflict status under
every reading with its certificates or witness, the premise status and the per-candidate statuses, the number of
reading premises in force and used, dead readings, the time of the superposed checks against the two companion
documents' checks, and whether every result the two companions give is given by the superposed route under the
corresponding atoms; for the UDHR, the compatible choice count against the budget and the time of the enumeration
attempt. For the constitution the plan expects no status change of any unit (S2a adds no status) and the premise
line to leave UNKNOWN. No coverage number is predicted, and the measured row replaces the plan's.

## 12. What S2b inherits from this specification

Not statements under this review; listed so that the plan's S2 section maps onto this file. S2b removes `hch` from
every theorem of 8.4 and adds: `gateContent` for `right`, `rightLines` and `limitation` contents (the plan's 2.3:
every line's norm gated as a norm is, a `right_lines` unit attached to q(R), a limitation's scope naming every copy of
a set-declared right); the copy of a fixed `right_lines` unit on a set-declared right once per candidate, each copy
guarded by that candidate's atom; `qualifyKey` for `lim`, `cond` and `aimed` keys over rights' positional names, with
`nameMap` as defined; `owners` for the `lim` and `cond` predicates of a candidate limitation or of a fixed limitation
on an act only candidate lines have, and for `aimed m` when the permission `m` is right-derived only through
candidate liberties (the fixed bar's node kept, F21); the bar set as the one enumerated axis (plan 2.6); E20 with
its slots; fixtures F4, F6 to F10 and F21; the rights report's per-reading findings (`UnlicensedLimitation … under
<set>:<i>`). Its statement review attacks `superpose_faithful` with F21 first, as the plan orders.

## 13. Statement review checklist (Astra + Fable, before S2a's Lean)

1. The frozen inputs: nothing of composition.md or composition-s1.md is changed; no existing file of
   `lean/VE/Compose/*` or S1's five files is changed beyond the additions 8.1 permits (`Adjoin.lean` new; `Wire.lean`
   and `Run.lean` additive, no S1 definition, statement or case kind changed); `build`, `one`, `free`, `genKeys`,
   `sideWF`, `expand`, `gate`, `Labelled`, `BaseAdmissibleP`, `slotConflictFreeCheck`, `backgroundValidP` are used as
   merged; S1's single-attachment refusal stays (14.2).
2. **`superpose_faithful` first** (plan section 9): the leak of 1.8 and M8 against W1's `yields`; whether uniform
   precedence is sufficient on these chains (the induction of 8.4's note) and whether any other construct of a
   fixed unit can reach an unchosen copy (`cites` carries no semantics; carve-outs and conditions are the rule's
   own); whether `hq` is indeed unused here and needed only for S2b.
3. `sup` (1.4, 8.3): the fold, positions, `copies`, gating of guards and sufficient conditions, the assertions;
   `sup_no_sets`; reserved names; byte-for-byte regeneration (the one form of `conj` and `disj`).
4. `Choice_D` (1.6, 8.3): each family against composition.md 1.5's labels; one formula per label; owners (1.5) and
   M10, M10b; the always-emitted quiescence (14.5); `choiceCore` as the decider of compatibility; `slot_wellFormed`,
   `slot_wellLabelled`.
5. `superposable` (1.8): the three causes, the finding's `<sets>`; that `sup_wellFormed` is definitional and why;
   `choice_wellFormed` and its size part (8.4's note).
6. Choices (1.2, 8.3): `complete`, `compatible`, narrowings in force, `choiceDoc` as S1's `build`; `choices_spec`;
   `ReadingsUnsatisfiable` against today's `CouplingUnsatisfiable`; `supReady`'s coupling and narrowing conjuncts
   against today's texts of 7 and against `couplingHolds`/`couplingPremises` (M17); the route order of 4.1 (W2 before
   `choiceCore D`, M18).
7. The name map and `pull` (1.7, 8.3; 14.4): why restriction is necessary; `qName` through the declaring set and the
   chosen candidate on an interface name (M1's name map, the twin case) and `origin` on the names of `sup D` only;
   `sharedEnv` and `asserted_shared`.
8. `encodes_unique` with `complete D c'` (14.6); `base_down`, `superpose_situation`, `base_up`, `ChoiceExtension`.
9. The empty situation (4.4, 8.2): `adjoinOne` case by case; the lift inside `superpose_all`'s proof through
   `circ_canon`; `superpose_conflict_free` without `hne`; M15.
10. `superpose_all` in expansion form against E10's one reading and against the plan's base form (14.3); `hcf` under
    `A` and the UNKNOWN of 4.5 (14.8); `superpose_countermodel` and `superpose_conflict_witness`; the premise model
    as the case `φ := ⊥`.
11. `dead_sound`, `unsat_sound`, `superpose_assertions` (its dropped hypothesis, 14.9).
12. The enumerated route (4.6): combination rules; a choice whose document the chain refuses; the budget texts.
13. The English (2): the slots; the result sentences; E12's naming rule for models (14.11); E26 to E29; G5, G6, G9.
14. The report (6), the diagnostics (7) and the fixtures (9), each derived by hand; the mutation check of M8.
15. The resolved choices of section 14, in particular 14.2 (single attachment), 14.10 (a claim graph) and 14.12
    (the `fill` instance).

## 14. Resolved choices in this draft

Each is a point where the plan left a reading open, or where its sketch had to be repaired; the review may overturn
any of them.

1. **S2a covers the soft and norms chains and builds the enumerated route for every chain.** The plan's S2a says
   "soft documents"; a norms-chain document is the soft document with the empty block (S1 13.6), and the enumerated
   fallback is chain-generic (`choiceDoc` is S1's `build`), so a rights document with at most 64 compatible choices
   gets its verdicts in S2a (M12) and the UDHR, over budget, does not (11).
2. **S1's single-attachment refusal stays.** Composition-s1.md 4.2 says S2 lifts it. Lifting it means admitting a
   fixed unit that is in no `one D s i`, which every S1 theorem takes as `WellFormedDoc D` (with `singlyAttached`),
   so `separates_sound` would have to be restated under a weaker predicate: a change to a frozen S1 statement.
   Neither pilot has such a unit (composition-s1-measured.md). This draft keeps the refusal and leaves the lift to a
   later amendment of S1, if the review wants it at all.
3. **Uniform precedence is a superposability condition, not a design change.** A1's copy mapping stands as
   converged; the condition states when it is faithful (1.8, M8). The alternative, copying a fixed rule per
   candidate as the plan does for `right_lines`, would be a design change and is not taken.
4. **`pull` restricts to the choice's vocabulary.** The plan's `pull (ν) S` keeps every tuple of `S`, so with any bit
   true the pulled structure is never admissible for the choice's document; the plan's `base_down` is false as
   sketched. `pull D c` is defined on the complete vocabulary so that it applies to expansions too.
5. **Quiescence is emitted for every generated predicate that is not fixed-generated.** The plan says "that the
   document of some compatible choice lacks"; deciding that needs the compatible choices, and the two slots have the
   same models (1.6). Single-owner keys join the candidate's label (`readings:<set>@<v>:<i>:quiet`), as the plan has
   it; a key with several owners or a pair of owners has its own label, written in colon form.
6. **`encodes_unique` asks the other choice to be complete**, because `Encodes` only constrains the entries of the
   open sets.
7. **A candidate a narrowing drops is not a `DeadReading`.** It is reported under its narrowing by E7; `DeadReading`
   names a candidate excluded only by the interaction of couplings and narrowings (M6), which no single sentence
   otherwise explains. Composition.md's E17 reading ("the couplings, constraints and narrowings exclude the
   candidate") is kept; the dropped candidate is the narrowing's own sentence.
8. **An entailment is certified only under readings whose conflict status is CONFLICT-FREE** (`hcf` of
   `superpose_all`, at the slot with the named atoms), as the plan's statement has it; otherwise `UNKNOWN (conflict
   status: <status>)`. The pointwise strengthening (conflict-freedom at the situation only) is not claimed. Naming
   readings in `A` lets a document with a conflict under one reading still be certified under another (M3).
9. **`superpose_assertions` drops the plan's `hS : S.Admissible (authorEnv D)`.** The equivalence holds for any
   structure, and a formula-only document on the norms chain may have assertions over regulated predicates, which
   a base structure cannot carry.
10. **A claim graph beside a content-bearing set keeps today's handling.** The plan lists `admission` among S2's case
    kinds and `Admission.lean` among its files. A graph leaf would have to assume a reading, and an author cannot
    write a choice atom (reserved names), so the leaf's wire form is a decision the plan does not make. Today
    (`ve/document.py`) the graph is the lower route's case on the fixed units free of every open set, and a leaf that
    cites a content-bearing set is `non-assertion reading admission needs an elaborator`; that stays, named here as
    an abstention, and the review decides whether S2a must include the superposed admission.
11. **E12 names every open sentence for a model-based result** and exactly the assumed candidates for a
    certificate-based one, so that E12's one reading ("under exactly the named candidates and whatever the other
    open sentences are read as") is true in both cases.
12. **The `fill` instance is stated and not built** (4.10), as S1 did; the constitution pilot therefore runs on S1's
    rerun document, which is said in 11 rather than hidden in a figure.
13. **`superposable` runs the chain's check on `sup D`** rather than deriving it, because the chain's size limits are
    not monotone from the candidates' documents to the superposed one (8.3's note); `sup_wellFormed` is then a
    checked fact, and the finding of 1.8 carries the chain's own text as its cause.
14. **`choiceCore D`** is defined so that compatibility, dead readings and unsatisfiability are decided over the bits
    alone (plan 2.6: "checked on atoms alone as today"); quiescence can never exclude a choice.
15. **New sentences E26 to E29** exist because E10's frame has a plural count, NONE and the budget have no sentence in
    composition.md, and the finding of 1.8 needs one. Each has a lead no other production begins with.
16. **`readings-choice` and `readings-dead`** are the two case kinds beyond the plan's four: the enumerated route
    must regenerate each choice's document in Lean (rule 3), so Python never sends a choice's document as authority;
    and a dead or unsatisfiable reading is a certified fact, not a search result.
17. **A narrowing on a non-active version is not in force** and is listed as stale; today it is applied only on
    request (`--narrowing`), and on the superposed and enumerated routes every narrowing in force is a premise, as
    the plan's F2 and F3 require. W2's route keeps today's on-request application (4.1 step 2, M18): the route is
    chosen before any narrowing becomes a premise, so a formula-only document's verdicts stay byte-identical (F20).

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-02 | Draft 1 | First statement specification of stage S2's item 1 (S2a), from plan draft 2 through the pointer plan's draft 2: the four routes of a `readings@1` document; choices, compatibility and `choiceDoc`; the choice vocabulary and atoms; `sup D` with gating, qualification and A1's copy mapping; owners and the labelled `Choice_D`; the name map and the pulled structure; the superposability condition with its three causes; the evidence forms and two findings; the slots of E4, E7, E8, E10, E12, E13, E17 and the sentences E26 to E29; the case kinds; the semantics with both directions of model correspondence, the empty situation, the verdict table and the enumerated route; the report and diagnostics; the Lean statements `sup_no_sets`, `sup_wellFormed`, `choice_wellFormed`, `asserted_shared`, `slot_wellFormed`, `slot_wellLabelled`, `encodes_unique`, `encodes_atoms`, `superpose_faithful`, `base_down`, `superpose_situation`, `base_up`, `superpose_conflict_iff`, `superpose_conflict_free`, `superpose_conflict_witness`, `superpose_all`, `superpose_all_base`, `superpose_countermodel`, `dead_sound`, `unsat_sound`, `superpose_assertions`, `choices_spec`, the lifting lemma of composition.md 9.5 and two wire theorems; fixtures F2, F3, F18 and F20 in S2a's share, M1 to M16, the differential, the shadow test with M8's mutation check, the pilots, the English; the measured unlock; what S2b inherits; seventeen resolved choices, three of them repairs of the plan's sketch (14.3, 14.4, 14.6). No code, Lean or frozen contract changes. |
| 2026-10-02 | Draft 2 | The converged Astra + Fable statement review of draft 1 applied (`manage-agents/debates/compose-s2-spec/{astra,fable}.md`, CONVERGED after round 2 on FIX) and nothing else, five corrections: (1) the route of 1.1 is chosen after the decoders run with today's texts and before `choiceCore D`, the `⊥` check and `DeadReading`, which now run only on the superposed and enumerated routes; W2 keeps its verdicts, `CouplingUnsatisfiable`, its on-request narrowing and its budget verbatim (1.1, 1.2, 1.9, 4.1, 4.7, 7, 14.17; F20 extended; fixture M18, the coupled formula-only document with two recorded narrowings that draft 1 would have refused). (2) `supReady` gains the shape of the couplings and narrowings that today's `validate_couplings` and `validate_narrowings` require (`couplingShape`, `narrowingShape`: active references, a label on every coupled candidate, distinct coupling ids and narrowing ids, non-empty keeps of the set's own candidates for a narrowing in force; a stale narrowing stays inactive), named in 7 as the Lean counterpart of their texts and carried by `superposable`, `SupReplay.sp` and the `hr` of `choices_spec`, `dead_sound` and `unsat_sound`; this is what `encodes_unique` and the theorems on it need (1.8, 8.3, 8.4's note; fixture M17 a to d). (3) `origin` is defined on the names of `sup D` and used by `owners` there; `qName` goes through the set that declares the name and the candidate the choice takes in it, so the name map of an interface name lands on the chosen copy (1.5, 1.7, 8.3; M1's expected map retained and spelled out). (4) M8's mutation check names the one copy that is a child of `base-x` and the leak through `stop-x` under choice 0. (5) 8.1 and 13.1 say which S1 files receive additive integration (`Wire.lean`, `Run.lean`) with no S1 definition, statement or case kind changed. No statement of S0 or S1 changed; no design change. The converged process: one confirmation round on the edited passages opens the build. |
| 2026-10-02 | Draft 3 | The confirmation round on draft 2 applied (`manage-agents/compose-s2-p3ver1.final.md`: FAIL on three statement-level wording claims, every definition confirmed as the requested repair, no unrelated change found) and nothing else, three corrections: (1) 1.1 and 4.1 say what choosing the route computes: the first three rows are decided from the decoded document alone, and W2 returns before any narrowing becomes a premise, before `choiceCore D` and before any finding; choosing between the superposed and enumerated rows computes `superposable D`, and so `sup D`, and nothing else of 1.2 to 1.9 (1.1; 4.1 steps 1, 2, 4, 5 and 6). (2) The decoder claim of 7 is limited to the shape invariants `supReady` enforces: a `Doc` that fails a conjunct is one today's texts refuse, and not conversely, since `validate_couplings` also refuses an empty label intersection (its second `CouplingLabelMissing`), an unsatisfiable coupling and its field and count checks (7; 1.8; 8.3's docstrings and note). (3) M17(a) says that no theorem of 8.4 assuming `supReady` or `superposable` applies to the document, not that no theorem of 8.4 does (`encodes_atoms` assumes neither). No definition, theorem statement or fixture value changed; no design change. The build opens on the PASS of the confirmation round on draft 3, scoped to these passages. |
| 2026-10-02 | Draft 4 | The confirmation round on draft 3 applied (`manage-agents/compose-s2-p3ver2.final.md`: 7's decoder correction and M17(a) confirmed; FAIL on one statement-level claim introduced by draft 3's route-order repair; definitions, theorem statements and fixture values found unchanged, no unrelated change found) and nothing else, one correction: 1.1 and 4.1 step 2 said that every document on none of the first three rows computes `superposable D` to choose between the superposed and enumerated rows, which reached the rights chain, whose fallback 1.1's table makes unconditional and whose `sup D` is S2b's (12); they now say that a rights document takes the enumerated row unconditionally (until S2b) with nothing of 1.2 to 1.9 computed, `superposable D` not evaluated and no `ReadingsNotSuperposable` (fixture M12), and that computing `superposable D`, and so `sup D`, is the soft and norms chains' alone (1.1; 4.1 steps 2 and 6). No definition, theorem statement or fixture value changed; no design change. The build opens on the PASS of the confirmation round on draft 4, scoped to these passages. |
| 2026-10-03 | Draft 5 | The DRI rulings on the S2a Lean report (`manage-agents/compose-s2-dri-note.md`) applied and nothing else. (1) The frame can declare the choice vocabulary: `supReady` gains the decidable conjunct `choiceFresh` (the frame declares neither `ve__here` nor a bit predicate of `bitDecls D`; `bitsOf`, `bitName`, `setSize` and `bitDecls` move ahead of it in 8.3), Python's `sup_ready` the same conjunct with the decoders' text `InvalidInput: name <n> begins with ve__` (1.8, 7); `base_down`, `base_up`, `superpose_conflict_free` and `superpose_assertions` are to be proved in this form, their statements unchanged since their `hs` or `hr` carries the conjunct (8.4's note); the two Lean counterexamples of the report become the rejection fixture M19. (2) M16: Lean is the authority, so S1's `chainWF` on the soft chain gains `namesFit` (every generated decision predicate within `MAX_IDENTIFIER_BYTES`), with the soft decoder's text in `Wire.chainText`; M16 holds as specified, and 8.1 records this one change of an S1 definition (1.8, 7, 8.1, M16). (3) Every remaining 8.4 theorem and 8.5 are required for S2a; the wire shape of 8.5 is recorded in `lean/READINGS.md`. No other definition, theorem statement or fixture value changed. |
| 2026-10-03 | Draft 5, finding 4 | The S2a Lean build found `asserted_shared` false as stated: its only hypotheses are `WellFormedDoc` and compatibility, and S1's documents read sets and units by id, so with two open sets under one id (or two units under one id) an assertion is checked only beside another set's or unit's rules (fixture M20, a formal counterexample in `Examples.lean`). Applied, pending the DRI's confirmation: `supReady` gains `unitsDistinct` (the Lean counterpart of today's `duplicate or invalid unit id`), and `asserted_shared` gains `(hr : supReady D = true)`, which carries the distinct set and unit ids; every theorem that uses it has `hs` and so `hr`. |
| 2026-10-03 | Draft 5, finding 5 | The S2a Lean build found `superpose_assertions` false with `ChoiceExtension` as written: it let `S'` reinterpret every predicate whose name begins `ve__bit__`, while `choiceFresh` (a decidable conjunct) keeps only the bits of `bitDecls D` out of the frame, so a frame predicate `ve__bit__9__9` used by a fixed assertion could be set true in `S'` and false in `S`. Applied, pending the DRI's confirmation: `ChoiceExtension` reinterprets exactly the choice vocabulary of `D` (the sort, `ve__here`, the names of `bitDecls D`), which is what its docstring says; `base_up`'s statement is unchanged and its witness reinterprets only those names. |
| 2026-10-03 | Draft 5, finding 6 | The S2a Lean build found `base_up` ill-typed as written: `B` was quantified over every structure, so the conjunct `(pull D c B).relation p vs ↔ B₀.relation p vs` compared relations over two unrelated carriers (`ChoiceExtension` fixes `B`'s carrier only in a proof, not in the statement's typing). Applied, pending the DRI's confirmation: the extension is `{ B₀ with relation := R, domain := dom, constant := k }`, quantified by `R`, `dom` and `k`, which is what `ChoiceExtension` already required of it; nothing else in the statement changes. |
| 2026-10-03 | Draft 5, review fixes | The Astra and Fable reviews of the S2a integration (`manage-agents/compose-s2-review-astra.final.md`, `reviews/compose-s2-review-fable.md`) applied to the as-built text, no statement of 8.4 weakened. A1: a document whose couplings and narrowings in force admit no compatible choice was accepted by the superposed case kinds over an inconsistent slot; Lean now decides it by its own search (`exists_compatible_of_choices`, `no_compatible_of_choices`), `SupReplay` carries `sat`, and the route refuses with `ReadingsUnsatisfiable` before any verdict (4.1 step 3, 8.3, 8.5, `readings_wire_satisfiable`). B1 (both) and DRI ruling 5: `choice_wellFormed` gains `(hw : choicesSoftChecked D = true)`, the route's runtime soft check of every compatible choice's document (up to 1024), carried by `SupReplay.checked` (`readings_wire_choice_wellFormed`), with the chain's text under the choice or `ResourceLimit: more than 1024 readings to check` (4.1, 7, 8.3, 8.4, 8.5). B2 (Astra) / B3 (Fable) and DRI ruling 4: the abstention of 4.10, or W2's route, is reached beside `norm-defaults@0` (the frame's placeholder `deny`), with the pilot's fixture. B3 (Astra) and B2 (Fable): the verdicts across readings, the report and `dead_readings` from checked evidence (6). B4 (Astra): the English of 2 registered and gated with all derivations; 2.5's `<conclusion>` is the existing English surface's sentence. |
