# Cross-sentence scope (`scope@0`): plan

> Status: planning draft 1, 2026-10-12, design only. No product code, tests or generated files change. Baseline
> `main` at `49de179e`. The research behind every choice here, with the measurements and their methods, is
> [docs/research/scope.md](../research/scope.md). Lean blocks are statement schemata for the item-1 specification
> (`docs/spec/scope.md`, not yet written) and its Astra + Opus statement review. They are not proofs and have not
> been elaborated; names marked *(pinned at spec)* depend on in-flight branches and are fixed there. Byte figures
> are ledger spans of the pinned runs (`manage-agents/pilots/{claude-constitution,udhr}/run-20261012T1800Z`).
> Every unlock is an **estimate** until a pilot rerun measures it.

## 0. Summary

`scope@0` lets one unit change other units, for four cases:
- a list's lead-in completes each item of the list;
- a heading or a bullet's bold label conditions the sentences under it;
- a later sentence narrows or carves out a named set of rules;
- a far clause orders rules ("notwithstanding", "subject to").

It is a wrapper at step **1b** of the composition stack, after RESOLVE (`ve.discourse@1`) and before STRUCTURE
(`right-clauses@0`). Lean regenerates each governed unit's content from its own words and its governors and hands
the chain ordinary `VE.Compose.Content`. Every effect is meaning W1 or the soft route already owns:
- the guard;
- carve-outs (`VE.Norms.applies`);
- precedence (`over`, `VE.Norms.check`);
- the soft fields.

The new proof obligations cover only how effects are composed:
- each field has exactly one owner;
- provenance;
- order independence;
- reaches regenerated from structure;
- identity when there are no governors;
- governor status.

A reach that the source leaves open becomes one reading set on its governor, never a guess. Readers see each
governed rule written out in full, with one plain sentence saying where each part came from.

The batches:

| Batch | Hours | What it builds | Bytes on the pinned pilots (estimate) |
|---|---|---|---|
| SC-M0 | 1–2 | pilot tally; no product code | — |
| SC-1a | 4–6 | Lean core: lists and lead-ins | 0 |
| **SC-1b** | 3–5 | on the stack: **first number moves** | **+22 B OPEN** |
| SC-1c | 3–5 | explain route and relay | 0 |
| SC-2 | 4–6 | named lists and later qualifications | +68 B LABELLED; +263 B OPEN once attitudes' hook lands; fidelity of 874 B |
| SC-3 | 3–5 | headings and bullet labels | 0 pinned |
| SC-4 | 3–4 | far precedence and forward exceptions | 0 pinned |
| SC-E1 | 2–3 | experiment: deictic reaches | — |
| SC-5 | 4–6 | deictic reaches as reading sets | up to 4,196 B upper bound; 0–300 B expected in the next two runs |
| SC-E2 | 2 | experiment: plain-English presentation | — |
| SC-6 | 3–4 | UDHR rights reach | 0 new B; fidelity of 683 B |
| SC-7 | 4–6 | authoring wordings | — |

## 1. The design

### 1.1 Position in the stack

```text
source bytes + front matter
  1  RESOLVE    ve.discourse@1     owns references (unchanged)
  1b GOVERN     scope@0            owns governance: lead-ins, headings, labels, later qualifications, far precedence
  2  STRUCTURE  right-clauses@0    owns line shape (unchanged)
  3  SUPERPOSE  readings@1         owns readings (unchanged)
  4  CHAIN      rights@0 → soft-norms@0 → [norm-defaults@0] → norms@0     owns norm meaning (unchanged)
  5  CHECK      relational-fol@0   frozen route
```

GOVERN is a total function regenerated at every trusted site.
- It returns its input unchanged when the document declares no governor (`govern_identity`).
- It adds no declaration (`govern_no_new_symbols`).
- It never reads a recorded reach, reading choice or weight as an input to a candidate set.

### 1.2 Governors, reaches, effects

A **governor** is a unit, an effect and a reach.

| Reach | Fixed by | Batch |
|---|---|---|
| `list` | the lead-in's unit text ends with ":". The governed items are the run of list items of the first item's depth, regenerated from the source bytes (Dickerson's rule: each item must complete its lead-in) | SC-1a |
| `list name` | a registered name for a list run ("The current hard constraints ... are as follows."), using discourse's `ContentName` type and decoder; its units must equal the run | SC-2 |
| `anchor` | a heading unit is the first unit of a discourse anchor; it reaches that anchor's units | SC-3 |
| `label` | a bold label ending in ":" at the start of a list item reaches that item's units (its continuing sentences and deeper items) | SC-3 |
| `rules` | stable W1 rule names | SC-4 |
| `frontier` | for "this" and "these": one constituent of the right frontier, kept only if the effect fits; several fitting candidates make a reading set | SC-5 (after SC-E1) |

| Effect | Meaning (owned by) | Batch |
|---|---|---|
| `frame` | the lead-in's part of each item's norm object; the lead-in's and the item's keys must be disjoint (one owner per field); the merged object is decoded by the chain's own norm decoder | SC-1a |
| `reguard c` | the rule's guard becomes the condition `c`, where `own` in `c` stands for the rule's own guard ("the relevant category"); `c = own and C` is plain narrowing (W1 guard, `VE.Norms.applies`) | SC-2 |
| `carve-out c` | one more W1 carve-out (W1's `applies := G ∧ ¬⋁U`; W1's limit of 8) | SC-2 |
| `precedes` / `yields` | W1 precedence edges: "notwithstanding X" makes the governor's rules take precedence over X's; "subject to X" the reverse (W1's same-predicate and acyclicity checks, unchanged) | SC-4 |
| `title` | none: a heading or label that only names | SC-3 |

A condition may use a **hook**, a word another profile owns, such as attitudes' "thinks it quite likely that". The
hook's meaning, typing and conservativity are that profile's. Scope defines no hook. A hook that no enabled
profile supplies is `UnsupportedProfile: scope@0 condition <word> needs <profile>`.

### 1.3 Statuses

| Unit | Status |
|---|---|
| Governed units | the status the chain gives their composed content, unchanged |
| Governor that changes content (`frame`, `reguard`, `carve-out`, `precedes`, `yields`) | the **weakest** status among the units it governs; UNFORMALISED if any of them is not admitted (`governor_status_weakest`) |
| Title governor, list-name registration | LABELLED, as discourse's naming clause is; reported apart from semantic coverage |

Governed and governor bytes are each counted once, under their own spans.

### 1.4 Order

For each governed unit, the effects apply in a fixed order:
1. its lead-in's frame (which makes the rule);
2. anchors, outermost first;
3. bullet labels;
4. list and list-name governors;
5. rule governors;
6. frontier governors.

Within one class, governors apply in source order. Plain narrowing (`own and C`) and carve-outs without `own`
commute (`commute_applies`), so the order changes nothing. Two governors on one unit whose effects do not commute
are refused with `ScopeOrder: <unit>: <g1>, <g2>`, so source order is never a hidden choice.

### 1.5 Ambiguity

Only the `frontier` reach can have several candidates.
- **Several candidates fit:** `AmbiguousScope: <governor>: <candidates>`.
  - In authoring, the IDE asks one question.
  - In translation, the candidates become one reading set on the governor, coupled to every affected unit through
    lf-14d's joint choices. That is one choice among at most 8 candidates, never a product over the affected
    units.
- **No candidate fits:** `UnresolvedScope: <governor>`; the unit stays UNFORMALISED.
- **Budget exhausted:** `ResourceLimit: scope`, which is UNKNOWN for every dependent verdict, never a rejection and
  never a chosen reach.

### 1.6 What the reader sees

The reviewed presentation shows each governed rule written out in full, rendered by the existing rule renderer
(one owner). It then adds one provenance sentence per contributing governor, e.g.:

> *Where the parts come from:* "should never" comes from the line above the list, "Claude should never:". The
> condition comes from a later sentence, "Hard constraints are centrally meant to apply to cases where ...", which
> covers all seven items of this list.

Unit ids, arrows and brackets are hidden by default; they appear in the provenance view. Lean owns the
provenance wording table (`VE/Scope/English.lean`); Python prints it.

## 2. English

### 2.1 Translation (what the pilots write)

A translator records governors in the front matter `scope` block (3) and writes each item's part of a rule as
`{"part": {...}}` content. Source wordings and how they are recorded:

| Source wording | Recorded as |
|---|---|
| "Claude should never:" + bullets | `frame` over the `list` reach |
| "The current hard constraints ... are as follows." | list name |
| "... are centrally meant to apply to cases where ..." | `reguard` over the list name |
| "Regardless of operator instructions, Claude should by default:" + bullets | `frame` whose part carries the soft fields, which weighing and soft own |
| "Notwithstanding ...", "Subject to ..." | `precedes` / `yields` |
| a heading or bullet label that is a full clause ("There's no operator prompt:") | `reguard` (narrowing) |
| a noun heading ("Hard constraints") | `title` |

A wording whose reach the source leaves open is a reading set (1.5). A wording that states something *about* a
list without changing its rules (u0170.s01, "The list of hard constraints above is not a list of all the behaviors
we think Claude should never exhibit.") is not a governor: scope refuses to read it as one (fixture F5).

### 2.2 Authoring (SC-7, last)

Each wording below has one reading. The IDE shows the paraphrase and writes the block from the English.

| Wording | The one reading (IDE paraphrase) |
|---|---|
| `Every instance of Claude must not:` followed by a bulleted list | "Each item below is its own rule: ‘Every instance of Claude must not <item>.’" Each item must complete the sentence |
| `The rules below are called the hard constraints.` | "‘The hard constraints’ names the rules of the list that follows." |
| `The hard constraints apply only where <condition>.` | "Each of the 7 rules called ‘the hard constraints’ applies only where <condition>." |
| `The hard constraints apply only where Claude knows that the act is of its kind, or thinks it quite likely that it is.` | "‘Its kind’ is each rule's own act." (`own`; the attitude words are attitudes'.) |
| `The hard constraints do not apply when <condition>.` | "None of the 7 rules applies when <condition>; then the other rules and the default decide." |
| `Rule 9 takes precedence over the rules of section 3.` | "Where rule 9 and a rule of section 3 regulate the same act, rule 9 decides." |
| `## When there is no operator prompt` (a heading that is a full `When`/`If` clause) | "Every rule in this section applies only when there is no operator prompt." |
| any other heading | "A title: it changes no rule." |
| `This applies only where <condition>.` after a rule or list (SC-5) | one fitting candidate: "This qualifies <the rule above / the list above>"; otherwise a question |

The templates live in the English catalogue that owns the grammar (english-lean). Scope registers them there and
adds no grammar of its own.

## 3. Wire form

```json
"profiles": ["norm-defaults@0", "norms@0", "relational-fol@0", "scope@0", "soft-norms@0"],
"scope": {
  "version": "scope@0",
  "list_names": [{"name": "the hard constraints", "units": ["u0165.s01", "u0165.s02", "u0165.s03", "u0165.s04",
                  "u0165.s05", "u0165.s06", "u0165.s07"], "scope": "doc", "lead": "u0164.s02", "unit": "u0164.s01"}],
  "governors": [
    {"id": "g1", "unit": "u0164.s02", "reach": {"list": "u0164.s02"},
     "effect": {"frame": {"sign": "negative", "mode": "strict"}}},
    {"id": "g2", "unit": "u0173.s01", "reach": {"list_name": "the hard constraints"},
     "effect": {"reguard": ["or", ["and", "own", ["unary", "knowingly_and_intentionally", ["var", 0]]],
                                  ["hook", "attitudes@0", "thinks_quite_likely", "own"]]}}
  ]
}
```

The example is illustrative:
- The frame's keys are whichever norm-object keys the seven rules share today; the spec pins them from the
  chain's decoder.
- The knowledge atom stands for attitudes' typed condition once that design lands.

Item unit content: `{"part": {"name": "hc-cbrn-uplift", "predicate": "weapons_uplift_permitted", "guard": [...]}}`.

Wire rules:
- Every id is a token of the existing grammar. Optional fields are absent, never `null`.
- Reaches and list-name units are recorded, then **regenerated and compared**: a mismatch is
  `ManifestMismatch: scope.<field>`.
- The block is inside the document identity, like discourse's.
- The `part` keys are the chain's own norm-object keys. Scope keeps no list of its own.

## 4. Lean: files and shared definitions

New directories:
- `lean/VE/Layout/`: `List.lean` (SC-1a), `Anchors.lean` (SC-3).
- `lean/VE/Scope/`: `Wire`, `Govern`, `Effects`, `Frontier`, `English`, `Run`, `Theorems`, `Examples`.
- `lean/SCOPE.md`: each theorem in plain words.

Response shape and encoder (SC-1c): `lean/ResponseShape/{Schemas,Encoders}/Scope.lean`.

Rules for the Lean code:
- No `mutual`, no primed theorem names, no `native_decide`.
- Examples prove by `decide` or `rfl`.
- The audit allowlist is unchanged.

```lean
namespace VE.Layout

/-- A unit as the layout reads it from its own source bytes; never from the wire. -/
structure Unit where
  id : String
  span : Nat × Nat
  item : Option Nat      -- some d: the unit begins a list item ("* ", "- ", "+ ", "<digits>. ") at depth d
  midLine : Bool         -- the unit begins after other text on its line (it continues the unit before it)
  lead : Bool            -- its text, without trailing layout, ends with ":"
  deriving DecidableEq, Repr

def ofSource (prose : String) (units : List (String × Nat × Nat)) : List Unit
def listRun (L : List Unit) (lead : String) : Except String (List String)   -- the governed items

/-- Independent statement of a governed item (SC-1a). -/
def GovernedItem (L : List Unit) (lead u : String) : Prop :=
  ∃ i j d, (L[i]?).map (·.id) = some lead ∧ (L[i]?).map (·.lead) = some true ∧
    (L[i+1]?).bind (·.item) = some d ∧ i < j ∧ (L[j]?).map (·.id) = some u ∧ (L[j]?).bind (·.item) = some d ∧
    ∀ k, i < k → k < j → ∃ x, L[k]? = some x ∧ ((∃ e, x.item = some e ∧ d ≤ e) ∨ x.midLine = true)

end VE.Layout

namespace VE.Scope

/-- A condition: `own` is the governed rule's own guard; `hook` is a word another profile owns. -/
inductive Cond
  | atom (φ : VE.Formula)
  | own
  | and (a b : Cond) | or (a b : Cond) | not (a : Cond)
  | hook (profile word : String) (arg : Cond)
  deriving DecidableEq, Repr

/-- The meaning of hook words, assembled from the enabled profiles; scope supplies none. -/
abbrev Hooks := String → String → VE.Formula → Option VE.Formula

def Cond.inst (H : Hooks) (G : VE.Formula) : Cond → Option VE.Formula
  | .atom φ => some φ
  | .own => some G
  | .and a b => do pure (.and (← a.inst H G) (← b.inst H G))
  | .or a b => do pure (.or (← a.inst H G) (← b.inst H G))
  | .not a => do pure (.not (← a.inst H G))
  | .hook p w a => do H p w (← a.inst H G)

inductive Effect
  | frame (part : Lean.Json) | reguard (c : Cond) | carveOut (c : Cond) | precedes | yields | title

inductive Reach
  | list (lead : String) | listName (name : String) | anchor (id : String) | label (item : String)
  | rules (names : List String) | frontier (k : Nat)

structure Governor where
  id : String
  unit : String
  effect : Effect
  reach : Reach

structure SDoc where
  layout : List VE.Layout.Unit
  units : List (String × Lean.Json)                       -- each unit's content object after RESOLVE
  governors : List Governor
  listNames : List (VE.Discourse.ContentName × String)    -- the name and the lead-in whose run it names (SC-2)
  anchors : List VE.Discourse.Anchor                      -- discourse's anchors, decoded by discourse's decoder (SC-3)
  hooks : Hooks
  re : VE.Readings.ReadingsEnvironment                    -- the chain's decoding environment (pinned at spec)

/-- Lead-in and item joined; a key on both sides is refused, never overridden. -/
def mergeParts (unit : String) (lead item : Lean.Json) : Except String Lean.Json
/-- An item's rule: the chain's own norm decoder (today `VE.Readings.Wire.decodeNorm`) on the joined object. -/
def itemRule (D : SDoc) (u : String) (lead item : Lean.Json) : Except String VE.SoftNorms.SoftNode :=
  do VE.Readings.Wire.decodeNorm D.re (← mergeParts u lead item)
def applyEffect (H : Hooks) : Effect → VE.SoftNorms.SoftNode → Except String VE.SoftNorms.SoftNode
  | .reguard c, N => match c.inst H N.guard with
    | some G => .ok { N with guard := G } | none => .error "UnsupportedProfile: scope@0 condition"
  | .carveOut c, N => match c.inst H N.guard with
    | some C => .ok { N with carveOuts := N.carveOuts ++ [C] } | none => .error "UnsupportedProfile: scope@0 condition"
  | _, N => .ok N
def covered (D : SDoc) : Reach → Except String (List String)
def baseRule (D : SDoc) (u : String) : Except String VE.SoftNorms.SoftNode   -- its own norm, or its item rule
def governorsOf (D : SDoc) (u : String) : List Governor                     -- rule-changing governors covering u, order 1.4
def govern (D : SDoc) : Except String (List (String × VE.Compose.Content))

end VE.Scope
```

## 5. Batches

The item-1 specification `docs/spec/scope.md` and its statement review come before any build:
- Astra + Opus review, with Fable arbiter only on disagreement.
- Theorem statements are type-checked as stubs in a scratch file, deleted before commit.

That is a stage, not a batch.

The first pilot number moves at **SC-1b**:
- SC-1a and SC-1b are the smallest feature that moves one, split because SC-1b must edit files that lf-16g is
  still changing.
- If lf-16g has merged when building starts, they run as one batch.

### SC-M0. Pilot tally (measurement; no product code; 1–2 h)

- **Goal.** Make the need measurable. The ledgers record no `other:*` co-blocker, so scope phenomena are filed
  under other tags (research 2.2).
- **Work.** In the pilot prompts (`manage-agents/prompts/pilot-*.txt`, outside the repository), the next runs:
  - tag `other:scope` as primary or co-blocker on every governor unit and governed unit;
  - record `governed_by: [unit ids]` on governed units;
  - write `scope-tally.json`: units and bytes by reach kind and effect, plus the 22 colon lead-ins and the 22
    restrictive connectives of research 2.2.
- **Moves.** A tally, not a coverage number.
- **Shared files.** None in the repository.

### SC-1a. Lists and lead-ins: Lean core (4–6 h)

- **Goal.** A lead-in completes each item of its list; Lean regenerates the run and the rules.
- **Depends on.** Nothing in flight: new files only.
- **New files.**
  - `lean/VE/Layout/List.lean` (`Unit`, `ofSource`, `listRun`, `GovernedItem`);
  - `lean/VE/Scope/{Wire,Govern,Theorems,Examples}.lean`, frame effect only;
  - `lean/SCOPE.md`.
- **Shared files touched**, append only:
  - `lean/VE.lean`: imports.
  - `lean/VE/Audit.lean`: one `#print axioms` per theorem. If AR-1's generator has merged, regenerate instead of
    editing.
  - `tools/layer_policy.py`: `VE.Layout.*` and `VE.Scope.*` in the profiles layer.

```lean
theorem listRun_iff (L : List VE.Layout.Unit) (lead : String) (us : List String)
    (h : VE.Layout.listRun L lead = .ok us) (u : String) : u ∈ us ↔ VE.Layout.GovernedItem L lead u

theorem listRun_ok_iff (L : List VE.Layout.Unit) (lead : String) :
    (VE.Layout.listRun L lead).isOk = true ↔
      ∃ i d, (L[i]?).map (·.id) = some lead ∧ (L[i]?).map (·.lead) = some true ∧ (L[i+1]?).bind (·.item) = some d

/-- One owner per field: every key of the joined object comes from exactly one side. -/
theorem mergeParts_keys (u : String) (lead item out : Lean.Json) (h : mergeParts u lead item = .ok out) (k : String)
    (v : Lean.Json) : out.getObjVal? k = .ok v ↔
      (lead.getObjVal? k = .ok v ∧ (item.getObjVal? k).toOption = none) ∨
      (item.getObjVal? k = .ok v ∧ (lead.getObjVal? k).toOption = none)

theorem mergeParts_conflict (u : String) (lead item : Lean.Json) (k : String)
    (hl : (lead.getObjVal? k).toOption.isSome) (hi : (item.getObjVal? k).toOption.isSome) :
    (mergeParts u lead item).isOk = false

/-- The item's rule is the chain's own decoding of the joined object: scope decodes no rule field itself. -/
theorem itemRule_decoder (D : SDoc) (u : String) (lead item : Lean.Json) (N : VE.SoftNorms.SoftNode)
    (h : itemRule D u lead item = .ok N) :
    ∃ m, mergeParts u lead item = .ok m ∧ VE.Readings.Wire.decodeNorm D.re m = .ok N

/-- Identity: without governors every unit's content is the chain's own decoding of what was written. -/
theorem govern_identity (D : SDoc) (h : D.governors = []) (out : List (String × VE.Compose.Content))
    (ho : govern D = .ok out) (u : String) (c : VE.Compose.Content) (hu : (u, c) ∈ out) :
    ∃ j cites, (u, j) ∈ D.units ∧ VE.Readings.Wire.decodeContent D.re j = .ok (.content c cites)

/-- Provenance: a governed rule is its unit's base rule with exactly the covering governors applied, in order. -/
theorem govern_provenance (D : SDoc) (out : List (String × VE.Compose.Content)) (ho : govern D = .ok out)
    (u : String) (N : VE.SoftNorms.SoftNode) (hu : (u, .norm N) ∈ out) :
    ∃ N₀, baseRule D u = .ok N₀ ∧
      (governorsOf D u).foldlM (fun M g => applyEffect D.hooks g.effect M) N₀ = .ok N ∧
      ∀ g ∈ governorsOf D u, ∃ us, covered D g.reach = .ok us ∧ u ∈ us

theorem governorsOf_iff (D : SDoc) (u : String) (g : Governor) :
    g ∈ governorsOf D u ↔ g ∈ D.governors ∧ changesRule g.effect = true ∧
      ∃ us, covered D g.reach = .ok us ∧ u ∈ us
```

**Fixtures** (pinned bytes, `Examples.lean` and `tests/test_scope_lean.py`):

| Id | Fixture | Expected |
|---|---|---|
| F1 | u0164.s02 "Claude should never:" with u0165.s01–s07; the lead part holds the keys the seven rules share (sign, mode and any soft field); each item part `{name, predicate, guard}` comes from the pilot's rules, without the knowledge conjunct | 7 rules equal to the pilot's except for that conjunct |
| F1′ | an item that also writes `sign` | `ScopeConflict: u0165.s03: sign` |
| F1″ | an item missing `predicate` | the chain decoder's own diagnostic, unchanged |
| F1‴ | u0166.s01 after the run | not an item |
| F2 | u0182.s02 + u0182.s03 ("Or does it escape these mechanisms?", mid-line) | u0182.s03 continues u0182.s02, not a new item |
| F2′ | u0072.s02 + u0073.s01–s10 | the "+ Example:" sub-bullets (depth 1) are not items of the depth-0 run |
| F2″ | a lead-in followed by prose | `NotALeadIn: <unit>` |

- **Bytes.** 0 (no route yet).
- **Deleted / not duplicated.** No rule field list in scope: decoding is `VE.Readings.Wire.decodeNorm`.
- **Exit.** `lake build`; the audit; `Examples` by `decide`; seeded Lean bugs (one per theorem family) shown to fail
  a test.

### SC-1b. On the stack: the first number moves (3–5 h)

- **Goal.** `ve document check` admits `scope@0` documents. The lead-in's bytes take the weakest status of its
  rules.
- **Depends on.**
  - **lf-16g** merged: the Lean document mode, with status inference for soft-norm documents, and the switch that
    deletes the Python document code.
  - Composition S0, merged (`VE.Compose.Dispatch`).
  - SC-1a.
  - If **AR-10** (one Lean route registry) has merged, registration is its one line instead of a `Route`
    constructor.
- **Shared files touched.**
  - `lean/VE/Compose/Dispatch.lean`: `wrapperProfiles` gains `"scope@0"` after `"ve.discourse@1"`; `Route.scope`;
    `sitsOn "scope@0"` for norms, normDefaults, soft and rights; `wrapperHead`; the existing case proofs updated.
    No in-flight branch touches this file today (survey, 2026-10-12); recheck at start.
  - `lean/VE/Service/Document.lean` *(pinned at spec; lf-16's file)*: calls `VE.Scope.govern` before the chain,
    and folds `governorStatus` for governor units. Two call sites, after lf-16g.
  - `ve/profiles.py`: one line, only if Python still lists profiles. After lf-18 this is Lean's.
  - Generated, via `tools/regen_generated.py --write` (never by hand): the document mode's schema,
    `tools/gate-collection.json`, `lean/checkers.lock`.

```lean
/-- A governor counts under the weakest status of what it governs, never a stronger one. -/
def governorStatus (st : String → Option Status) (us : List String) : Option Status   -- Status, ≤: the document mode's (pinned at spec)

theorem governor_status_weakest (st : String → Option Status) (us : List String) (s : Status)
    (h : governorStatus st us = some s) :
    us ≠ [] ∧ (∀ u ∈ us, ∃ t, st u = some t ∧ s ≤ t) ∧ ∃ u ∈ us, st u = some s

theorem governor_status_none (st : String → Option Status) (us : List String)
    (h : us = [] ∨ ∃ u ∈ us, st u = none) : governorStatus st us = none

/-- The document mode's answer on a scope@0 document is the chain's answer on govern's output. -/
theorem scope_admission (j : Lean.Json) (res : DocumentAnswer) (h : admitDocument j = .ok res)
    (hs : "scope@0" ∈ profilesOf j) :
    ∃ D out, decodeScope j = .ok D ∧ govern D = .ok out ∧ res.inner = admitChain (withContents j out)
    -- admitDocument, DocumentAnswer, admitChain, withContents: lf-16g's names (pinned at spec)

/-- Documents without scope@0 are answered exactly as before. -/
theorem scope_absent_unchanged (j : Lean.Json) (h : "scope@0" ∉ profilesOf j) :
    admitDocument j = admitDocumentBefore j
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F1-doc | the pilot's hard-constraint block rewritten with the lead-in part and seven item parts, checked end to end | the seven units OPEN as today; u0164.s02 OPEN |
| F1-off | the same document without `scope@0` | `UnsupportedProfile` for the `part` contents |
| F1-bad | one item not admitted | u0164.s02 UNFORMALISED |

- **Pilot.**
  - Rerun the constitution with the translation's u0164/u0165 block rewritten (pilot data).
  - Measure: u0164.s02, 22 B, from UNFORMALISED to OPEN (**estimate**).
  - Pre-registered: the seven rules keep their statuses and their `ve document check` answers byte for byte, apart
    from the provenance lines.
- **Deleted.** In the pilot translation, the restated force in each item ("Every instance of Claude must not")
  becomes one lead-in part. That is pilot data, not product code.
- **Exit.** Selected tests; the full gate once on the final head; pilot rerun numbers saved as batch evidence (D4).

### SC-1c. Explain route and relay (3–5 h)

- **Goal.** `ve scope explain <doc>` prints, for every governed unit, its full rule and the provenance sentences.
- **Depends on.** SC-1b. **AR-13** typed codes, if merged.
- **Work.** This follows the CLAUDE.md recipe for a relayed Lean route:
  - mode `scope`, runner `VE.Scope.Run.runCaseReported`;
  - `VE.Service.runMode_scope` listed in `lean/VE/Audit.lean`;
  - the shape `ResponseShape.Schemas.Scope`, with the encoder theorem
    `ResponseShape.Encoders.Scope.runCaseReported_fits` listed in `lean/ResponseShape/Audit.lean`;
  - the generated `ve/backends/lean_service_schema/scope.json` and its `MODES` entry;
  - the relay `ve/scope.py`, through `rows` in `ve/backends/relay.py`, checking schema and binding only;
  - a CLI subcommand in `ve/__main__.py`;
  - fixtures recorded in `tests/data/route-cases.jsonl`;
  - fuzz tests in `tests/test_scope_answer.py`: each member dropped, emptied, retyped, duplicated or reordered, an
    index pushed out of range, so every mutant is `CheckerUnavailable` or changes nothing shown.
- **Answer rows.** Per governed unit: `unit`, `governors` (`id`, `unit`, `effect` word, `reach` units), and
  `provenance` (Lean's sentences from `VE/Scope/English.lean`).
- **Binding.** Every unit and governor id must exist in the request.
- **Shared files touched.**
  - `lean/VE/Service/Protocol.lean`: one dispatch case and equation, or AR-10's registry line.
  - `ve/backends/service_schema.py`: `MODES`, append.
  - `ve/__main__.py`: subcommand, append.
  - The two audit files: append, or regenerate.
  - Generated files via `regen_generated.py`.
- **Bytes.** 0. This batch is the reader's view, and it gates SC-E2.

### SC-2. Named lists and later qualifications (4–6 h)

- **Goal.** A later sentence narrows, replaces or carves out the condition of a named set of rules. A list name
  registers a run.
- **Depends on.** SC-1a. The pilot claim of u0173.s01 also needs SC-1b and the **attitudes** batch that supplies
  the "thinks it quite likely that" hook (`design/attitudes`, AT plan: "u0173.s01 attached to the seven rules").
- **New files.** `lean/VE/Scope/Effects.lean`. The list-name check is added to `Govern.lean` (a scope file).
- **Shared files touched.**
  - The audit, append.
  - `lean/VE/Discourse/Wire.lean`: none. Scope calls `decodeContentName` as is.

```lean
theorem reguard_applies (H : Hooks) (c : Cond) (N N' : VE.SoftNorms.SoftNode)
    (h : applyEffect H (.reguard c) N = .ok N') (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∃ G, c.inst H N.guard = some G ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ G.denote S ρ ∧ ¬ (VE.Norms.anyF N.carveOuts).denote S ρ)

/-- Plain narrowing is the special case: one more guard conjunct. -/
theorem restrict_applies (H : Hooks) (C : VE.Formula) (N N' : VE.SoftNorms.SoftNode)
    (h : applyEffect H (.reguard (.and .own (.atom C))) N = .ok N') (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.Norms.applies N'.toNode).denote S ρ ↔ (VE.Norms.applies N.toNode).denote S ρ ∧ C.denote S ρ

theorem carveOut_applies (H : Hooks) (c : Cond) (C : VE.Formula) (N N' : VE.SoftNorms.SoftNode)
    (hc : c.inst H N.guard = some C) (h : applyEffect H (.carveOut c) N = .ok N')
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.Norms.applies N'.toNode).denote S ρ ↔ (VE.Norms.applies N.toNode).denote S ρ ∧ ¬ C.denote S ρ

/-- Typing is kept when the instantiated condition type-checks in the rule's situation context. -/
theorem applyEffect_typed (E : VE.Environment) (Γ : List String) (H : Hooks) (e : Effect)
    (N N' : VE.SoftNorms.SoftNode) (hN : N.guard.check E Γ = true ∧ ∀ C ∈ N.carveOuts, C.check E Γ = true)
    (h : applyEffect H e N = .ok N') (hc : ∀ C, condOf H e N = some C → C.check E Γ = true) :
    N'.guard.check E Γ = true ∧ ∀ C ∈ N'.carveOuts, C.check E Γ = true

/-- Narrowings and own-free carve-outs commute, so source order is never a hidden choice. -/
theorem commute_applies (H : Hooks) (e₁ e₂ : Effect) (hc : Commutes e₁ e₂ = true) (N N₁ N₂ : VE.SoftNorms.SoftNode)
    (h₁ : (applyEffect H e₁ N).bind (applyEffect H e₂) = .ok N₁)
    (h₂ : (applyEffect H e₂ N).bind (applyEffect H e₁) = .ok N₂) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.Norms.applies N₁.toNode).denote S ρ ↔ (VE.Norms.applies N₂.toNode).denote S ρ

theorem order_refused (D : SDoc) (u : String) (g₁ g₂ : Governor) (h₁ : g₁ ∈ governorsOf D u)
    (h₂ : g₂ ∈ governorsOf D u) (hne : g₁ ≠ g₂) (hc : Commutes g₁.effect g₂.effect = false) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeOrder" = true

/-- A condition with no hook means the same whatever hooks are enabled. -/
theorem inst_hookFree (H : Hooks) (c : Cond) (G : VE.Formula) (h : c.hookFree = true) :
    c.inst H G = c.inst (fun _ _ _ => none) G

/-- A list name names exactly its lead-in's run. -/
theorem listName_run (D : SDoc) (n : VE.Discourse.ContentName) (lead : String) (h : (n, lead) ∈ D.listNames)
    (us : List String) (hc : covered D (.listName n.name) = .ok us) :
    VE.Layout.listRun D.layout lead = .ok us ∧ n.units = us
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F3 | u0164.s01 registers "the hard constraints" over the run of u0164.s02; u0173.s01 is `reguard ((own and knowing) or thinks-quite-likely(own))` | With the hooks of `Examples` (a test-only `Hooks` value, not attitudes'): each rule's guard is `(G_N ∧ K) ∨ L(G_N)`. Without hooks: `UnsupportedProfile: scope@0 condition thinks_quite_likely needs attitudes@0`, and u0173.s01 stays UNFORMALISED |
| F4 | **the audit's case**: a two-element model where L(G) holds and G does not | the rule applies under F3 and does not under the pilot's current guard `G ∧ K`. This separates the faithful reading from the rejected one |
| F5 | u0170.s01 | not a governor: a block declaring it with any effect is `ScopeNoEffect: <governor>` |
| F6 | synthetic "The hard constraints do not apply when Claude is being tested by Anthropic." | one carve-out on each of the 7 rules |
| F6′ | a carve-out on a rule that already has 8 | W1's own limit diagnostic, unchanged |
| F7 | two `own`-mentioning reguards on one rule | `ScopeOrder` |
| F7′ | a narrowing plus a carve-out | accepted, and the same in either order |

**Bytes (estimates):**
- u0164.s01, 68 B: LABELLED, reported apart from semantic coverage.
- u0173.s01, 263 B: OPEN, **only** with the attitudes hook; 0 otherwise.
- Fidelity: the 874 B of u0165.s01–s07, which the audit judged unfaithful, carry the reading the audit asks for.

**Pre-registered:**
- u0173.s01 is claimed only with the full schema, never with the narrowing `G ∧ K`.
- The F4 model must separate the two readings.

**Deleted.** In the pilot translation:
- the shared open term `restricted_action_knowing_or_quite_likely` in seven guards;
- the seven notes that restate u0173.s01.

Both become one governor.

### SC-3. Headings and bullet labels (3–5 h)

- **Goal.** A heading governs its anchor and a bold label governs its item: as a condition (a full `When`/`If`
  clause) or as a title (no effect).
- **Depends on.** SC-1a. The discourse anchor decoder, merged.
- **New files.** `lean/VE/Layout/Anchors.lean`. The bodies of discourse's `within`, `narrower` and
  `innermostAnchor` move here, over `(unit spans, anchors)`. Discourse's three definitions become one-line calls,
  so there is one owner for anchor containment.
- **Shared files touched.** `lean/VE/Discourse/Access.lean`: the three bodies become calls. Statements and
  theorems are unchanged; `acc_no_heuristic`, `name_scope` and `innermost_within` are re-proved by unfolding. No
  in-flight branch touches discourse (survey 2026-10-12); recheck at start.

**Assertions.** Assertion targets are added here because headings in policies and papers govern plain claims too.
For a closed condition `C`:
- narrowing turns `φ` into `C → φ`;
- a carve-out turns `φ` into `¬C → φ`.

```lean
theorem anchor_reach_iff (D : SDoc) (a : VE.Discourse.Anchor) (h : a ∈ D.anchors) (us : List String)
    (hc : covered D (.anchor a.id) = .ok us) (u : String) :
    u ∈ us ↔ VE.Layout.within (unitSpans D) D.anchors u a.id = true ∧ u ≠ headingOf D a.id

theorem title_identity (D : SDoc) (g : Governor) (h : g.effect = .title) (D' : SDoc)
    (hD : D' = { D with governors := D.governors.erase g }) : govern D = govern D'

theorem discourse_within_unchanged (D : VE.Discourse.DDoc) (u a : String) :
    VE.Discourse.within D u a = VE.Layout.within (VE.Discourse.unitSpans D) D.K.anchors u a

theorem assertion_restrict_denote (C φ : VE.Formula) (S : VE.Structure.{u}) :
    (restrictAssertion C φ).denote S [] ↔ (C.denote S [] → φ.denote S [])
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F8 | UDHR u109 "## Article 29" with u110–u112 | a title: contents and statuses unchanged (regression) |
| F9 | synthetic `## When there is no operator prompt` over two rules | each guard gains the condition |
| F9′ | `## Instructable behaviors` | title |
| F10 | u0073.s01 "* **There’s no operator prompt:** ..." | the label reaches u0073.s01–s04 and not the "+ Example:" sub-bullets' own label. Structure only: their content is blocked by graded force |

- **Bytes.** 0 on the pinned runs (estimate). The u0073 block (2,475 B) waits on graded force.
- **Deleted.** Discourse's three anchor bodies (moved, not copied).

### SC-4. Far precedence and forward exceptions (3–4 h)

- **Goal.** Handle three wordings:
  - "Notwithstanding <rules or section>" and "Subject to <rules or section>" become W1 precedence edges.
  - "Rule n has exceptions stated later in this section." becomes a checked forward declaration.
- **Depends on.** SC-2 (`Effect`), SC-3 (anchor reach).
- **Shared files touched.** None beyond the audit. The composed tree goes through `VE.Norms.check` unchanged.

```lean
theorem precedes_edges (D : SDoc) (out : List (String × VE.Compose.Content)) (ho : govern D = .ok out)
    (g : Governor) (hg : g ∈ D.governors) (he : g.effect = .precedes) (u v : String)
    (N M : VE.SoftNorms.SoftNode) (hu : (u, .norm N) ∈ out) (hv : (v, .norm M) ∈ out) (hN : u = g.unit)
    (hM : ∃ us, covered D g.reach = .ok us ∧ v ∈ us) (hp : M.pred = N.pred) : M.name ∈ N.over

theorem no_effect_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors)
    (he : g.effect = .precedes ∨ g.effect = .yields) (h : edgesOf D g = []) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeNoEffect" = true

theorem forward_exception_sound (D : SDoc) (r a : String) (h : forwardCheck D r a = .ok ()) :
    ∃ v N, v ∈ laterUnitsIn D a r ∧ baseRule D v = .ok N ∧ r ∈ N.over
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F11 | synthetic "Notwithstanding section 3, every operator may ..." over same-predicate rules | edges added |
| F11′ | the same over other predicates | `ScopeNoEffect` |
| F11″ | edges that close a cycle | W1's `DependencyCycle`, unchanged |
| F12 | u0047.s05–s06 "That said, we discuss some exceptions to this in the section on “broad safety” below." | the reach is an anchor, but no rules are named, so recorded as residual (`UnresolvedScope`), never guessed |

- **Bytes.** 0 on the pinned runs (estimate; the units are co-blocked).

### SC-E1. Experiment: are deictic reaches structural? (2–3 h; no product code)

- **Question.** For "This ..." / "That said, ..." qualifiers, is the intended reach one of the right-frontier
  constituents (previous sentence, its paragraph, the list it closes, the enclosing sections), and is the
  candidate set small?
- **Corpus.** 29 cases, frozen before any annotation:
  - the 22 restrictive-connective units of research 2.2;
  - u0046.s02, u0170.s01 and u0179.s03;
  - the 4 "In particular" units;
  - UDHR u052 and u112.
- **Method.** A scratch script outside the product applies the frontier rule to the ledger structure (SC-M0).
  Two independent annotations of the intended reach:
  - the pilot ledger's note, where it names one;
  - a Sonnet 5.5 human-proxy reading, blind to the frontier output.
- **Pre-registered bar.** Pass needs all three:
  1. On cases where the annotations agree, the intended reach is a frontier constituent in at least 90%.
  2. The annotations agree on at least 80% of cases.
  3. At most 4 structural candidates in at least 90% of cases.
- **Fail.**
  - If (1) fails, deictic reaches must be named in authoring ("This rule ...", "The list above ..."), and
    translation records the candidates of the enclosing section, capped at 8, as the reading set. SC-5 is
    re-specified before it is built.
  - If (2) fails, the reach is genuinely open in the source, and the reading set is the expected outcome.

### SC-5. Deictic reaches as reading sets (4–6 h)

- **Goal.** "This applies only where ...", "This is not a strict hierarchy, however." For each governor, compute the
  frontier candidates the effect fits:
  - one candidate: the reach is fixed;
  - several: one reading set, coupled to the affected units.
- **Depends on.** SC-E1 passed; **lf-14d** merged (coupled reading sets in Lean); SC-2.
- **New files.** `lean/VE/Scope/Frontier.lean`.
- **Shared files touched.** None. lf-14d's coupling functions are called, not edited.

```lean
def frontier (D : SDoc) (u : String) : List (List String)          -- innermost first; at most 8
def Fits (D : SDoc) (e : Effect) (us : List String) : Prop          -- every unit of us has a rule e applies to, typed
def scopeCandidates (D : SDoc) (g : Governor) : List (List String)

/-- No heuristic: the frontier depends only on layout and anchors, never on contents, recorded reaches or choices. -/
theorem frontier_no_heuristic (D D₂ : SDoc) (u : String) (hL : D.layout = D₂.layout) (ha : D.anchors = D₂.anchors) :
    frontier D u = frontier D₂ u

theorem scopeCandidates_iff (D : SDoc) (g : Governor) (us : List String) :
    us ∈ scopeCandidates D g ↔ us ∈ frontier D g.unit ∧ Fits D g.effect us

theorem frontier_accepted (D : SDoc) (g : Governor) (us : List String) (h : validateFrontier D g = .ok us) :
    us ∈ frontier D g.unit ∧ Fits D g.effect us ∧ ∀ vs ∈ frontier D g.unit, Fits D g.effect vs → vs = us

theorem frontier_ambiguous (D : SDoc) (g : Governor) (h : 2 ≤ (scopeCandidates D g).length) :
    ∃ e, validateFrontier D g = .error e ∧ e.startsWith "AmbiguousScope" = true

/-- The reading set's compatible choices are exactly the candidates, one each (lf-14d's joint set). -/
theorem scope_choices (D : SDoc) (g : Governor) (cs : List (List String)) (hc : scopeCandidates D g = cs)
    (hn : 2 ≤ cs.length) (c : VE.Discourse.Choice) :
    c ∈ jointChoices (coupledSets D g) ↔ ∃ i < cs.length, c = choiceAt D g i    -- jointChoices: lf-14d's owner (pinned at spec)
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F13 | u0046.s02 | two candidates (the previous sentence; the ordered list) → `AmbiguousScope`; in translation one reading set with two candidates |
| F13′ | synthetic "Rule 4. ... This applies only where the user is an adult." with one fitting candidate | fixed reach |
| F13″ | a frontier over the budget | `ResourceLimit: scope` (UNKNOWN) |

- **Bytes.** Upper bound 4,196 B (the 22 restrictive-connective units). Most are co-blocked; 0–300 B expected in
  the next two runs (estimate).

### SC-E2. Experiment: the plain-English presentation (2 h)

- **Question.** Can a reader with no training answer applicability questions from the reviewed presentation
  (1.6)?
- **Method.** 20 governed rules: the 7 hard constraints after SC-2 plus 13 synthetic, covering every effect. 40
  yes/no questions ("Does rule X forbid Y when Claude only suspects Z?"). Sonnet 5.5 as human proxy.
  - Arm A: the source text alone.
  - Arm B: the reviewed presentation with provenance sentences.
- **Pre-registered bar.**
  - Arm B: at least 90% correct.
  - Arm B: names the sentence a condition came from in at least 90%.
  - Arm B is no worse than arm A on any question.
- **Fail.** Revise the provenance wording table (`VE/Scope/English.lean`) and rerun. Semantics does not change.

### SC-6. UDHR: rights reach (3–4 h)

- **Goal.** "The rights and freedoms set forth in this Declaration" reaches the document's right units. A
  limitation's or bar's scope is generated from that reach. The UDHR's stand-in open term
  `rights_and_freedoms_set_forth` is removed.
- **Depends on.** **Composition S2b** (rights documents superposed; not in flight). SC-2. SC-5 for u112's "These
  rights and freedoms", whose candidates are all rights or the rights of 29(2).
- **Shared files touched.** None. rights@0 is called as is; its `Limitation.scope` is filled from the reach, not
  written twice.

```lean
theorem limitation_scope_of_reach (D : SDoc) (g : Governor) (L L' : VE.Rights.Limitation)
    (h : withReach D g L = .ok L') (us : List String) (hc : covered D g.reach = .ok us) :
    L'.scope = some (rightNames D us) ∧ { L' with scope := L.scope } = L
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F14 | u111 (29(2)) | its limitation reaches every right line; the residual `limitation_not_attached_to_rights_lines` closes |
| F14′ | u114 (Article 30) | its bar reaches every right line |
| F14″ | u112 | a two-candidate reading set |

- **Bytes.** 0 new (u111 stays READINGS, u112 OPEN, u114 READINGS). Fidelity of 683 B.

### SC-7. Authoring wordings (4–6 h)

- **Goal.** Writers type the wordings of 2.2 and the IDE writes the block. The reviewed presentation round-trips.
- **Depends on.** english-lean's grammar extension point (the catalogue that owns templates) and SC-1c.
- **Shared files touched.** The English catalogue's template list, append.
- **Theorem.**
  - `scope_parseRender`: every accepted governor wording renders back to itself.
  - Its block is the one the parser builds (stated over the catalogue's parse function, pinned at spec).
- **Bytes.** None on the translations. This batch serves zero-training authoring.

## 6. Dependencies and merge-conflict map

| In-flight or planned item | Branch / worktree | Needed by | How conflicts are avoided |
|---|---|---|---|
| Lean document mode, soft norms, Python switch | lf-16e, lf-16f, lf-16g (`ve-lf-16e`, …) | SC-1b | SC-1b starts after lf-16g merges; until then only new files (SC-1a, SC-2, SC-3) |
| Coupled reading sets in Lean | lf-14d (`lean-first/b14d`, `ve-lf-14d`) | SC-5 | called, never edited; SC-5 after it merges |
| Typed attitude conditions | `design/attitudes` → AT build batches | u0173.s01's claim (SC-2) | the hook interface; scope defines no attitude word |
| Generated audit manifests | AR-1 (`arch-20261010-1`) | every batch | append by hand before AR-1, regenerate after; never both |
| One route registry | AR-10 (after lf-18) | SC-1b, SC-1c | if merged, one registry line instead of `Route.scope` and a Protocol case |
| Typed diagnostic codes | AR-13 | SC-1c onwards | scope's codes join the typed list if merged |
| Per-mode test invalidation | ts-B2 | SC-1c | the new mode's manifest entry is generated |
| Composition S2b; S4 | not in flight | SC-6; none | SC-6 waits for S2b. Scope does not need S4: list names use discourse's `ContentName` type and decoder in scope's own block |
| Weighing, events, quantities, act-phrases | `design/*` | none | conditions may contain their formulas; their meaning stays theirs |
| rd-9, qa-q2, oom-rootcause | in flight | none | no shared file |

Every shared file a batch touches:
- `lean/VE.lean`, `lean/VE/Audit.lean` (SC-1a onwards);
- `tools/layer_policy.py` (SC-1a);
- `lean/VE/Compose/Dispatch.lean`, the Lean document mode file and `ve/profiles.py` (SC-1b);
- `lean/VE/Service/Protocol.lean`, `lean/ResponseShape/Audit.lean`, `ve/backends/service_schema.py`,
  `ve/__main__.py` (SC-1c);
- `lean/VE/Discourse/Access.lean` (SC-3);
- the English catalogue (SC-7).

Generated files are regenerated with `tools/regen_generated.py --write` and never edited or merged by hand:
- the schemas;
- `tools/gate-collection.json`;
- `lean/checkers.lock`;
- route cases through `tests/route_case_recorder.py`.

## 7. One owner per piece of logic

| Logic | Owner | Scope's use |
|---|---|---|
| Guards, carve-outs, applicability | W1 `VE.Norms.applies`, `anyF` | called by `applyEffect`; its theorems are stated over it |
| Precedence, cycles, same predicate | W1 `VE.Norms.check`, `dependencyOrder` | composed tree checked unchanged |
| Norm object decoding, soft fields | the chain's decoder (`VE.Readings.Wire.decodeNorm`, *pinned at spec*) | lead-in and item joined as JSON, then decoded by it |
| Anchors, content names | discourse (`Anchor`, `ContentName`, their decoders, `anchorsOk`) | read; containment moved to `VE.Layout` in SC-3 so both call one body |
| Joint choices | lf-14d (Lean) | SC-5 builds its sets through it |
| Rights limitations, bar | rights@0 | SC-6 fills `scope` from a reach |
| Attitude words, weighing words | attitudes, weighing | hooks and soft fields only |
| Statuses and their order | the Lean document mode | `governorStatus` reads its order |
| Rule English | the existing rule renderer | scope renders only provenance sentences |
| List markers and runs, governance order, provenance wording | **scope** (`VE.Layout.List`, `VE.Scope.*`) | new; nothing else reads list layout across units |

What is deleted:
- **Product code: nothing.** No scope logic exists to delete. SC-3 moves discourse's anchor-containment bodies
  rather than copying them.
- **Pilot data:**
  - the force restated in seven items (SC-1b);
  - the shared open term and notes copying u0173.s01 (SC-2);
  - the UDHR stand-in term `rights_and_freedoms_set_forth` (SC-6).

## 8. Risks and questions for the review

1. **SC-1b's wait.** It waits for lf-16g. If that slips, the first measured number slips with it. SC-1a, SC-2 and
   SC-3 can proceed meanwhile. Nothing is claimed early.
2. **`own` is a new kind of reference.** It refers to the governed rule's own guard. The review should check that
   it cannot capture a variable: the rule's situation context is the same for the rule and the condition, and
   `applyEffect_typed` requires the instantiated condition to type-check there.
3. **Where list names live.** Should they move into discourse's `content_names` when composition S4 lands? This is
   a question for the cross-plan review; the type and decoder are already shared.
4. **The governor status rule.** "weakest of governed" is conservative. Is LABELLED right for list-name
   registrations? This follows discourse's naming clause.
5. **The frontier is gated.** If SC-E1 fails, deictic reaches must be named in authoring. That is a stricter
   English, not a weaker check.
6. **The coverage bar.** No packed identifiers: lists of noun-phrase items (u0139, u0071) stay UNFORMALISED. A
   governor's bytes are claimed only under the weakest status of rules that exist.

## 9. Shared pieces

These are abstractions several of the seven topics could share. The cross-plan review may move them.

| Shared piece | Who would use it | Proposal |
|---|---|---|
| **Document layout tree**: unit order, paragraphs, list items and depth, headings, anchors, containment | scope (runs, frontier), discourse (`within`, `innermostAnchor`), senses (section-scoped defaults between "whole document" and "one occurrence"), math-evidence (theorem, proof and definition environments; "Let" / "Assume" over a proof), act-phrases (the line between in-sentence and cross-sentence lists) | `VE.Layout`, one owner, read from source bytes; discourse's containment moves there in SC-3 |
| **Condition hooks**: a word owned by one profile used inside another's condition | attitudes ("thinks it quite likely that", "knows that"), quantities (graded comparisons), events ("before the date of this document"), weighing (override conditions) | `Hooks := profile → word → formula → formula`, assembled by the document mode from enabled profiles; each owner proves typing and conservativity of its words once |
| **One owner per field** when two units supply parts of one content | scope (lead-in and item), act-phrases (a subject shared by predicates split across units, UDHR u060/u061), rights ("this right includes" lines added to a right), weighing (a later sentence that supplies who may override) | join JSON parts with disjoint keys, then the owner's own decoder; never a mirror type |
| **Reach candidates as one reading set**, coupled to the units they affect | scope (deictic reaches), act-phrases (attachment of modifiers), discourse (pronoun candidates), rights (limitation scope) | one candidate list per choice point, coupled through lf-14d's joint choices, never a product over affected units |
| **Contributor status**: a unit whose meaning lives in other units counts under the weakest of their statuses | scope governors, discourse groups, rights "this right includes", attribution containers | one function in the Lean document mode with `governor_status_weakest`-style theorems |
| **Named sets of rules or units** ("the hard constraints", "the rights and freedoms set forth in this Declaration") | scope (list names), rights (limitation and bar scope), weighing (rank classes: "hard constraints outrank ..."), attitudes (u0173.s01's target) | discourse's `ContentName` type and decoder, with a regenerated membership check |
| **Provenance sentences** in plain English (which sentence contributes which part) | scope, discourse (reviewed presentation), weighing (decision records), attribution (who said it) | one wording table in Lean per owner, one display format in Python |
| **Section-scoped declarations** (definitions, sense defaults, units of measure, assumptions) | senses, quantities ("all amounts in this section are in euros"), math-evidence, discourse names (already anchor-scoped) | an `anchor` reach on a declaration, using the same layout tree |
| **Boundary with phrase grammar** | act-phrases, events | in-sentence coordination, ellipsis and quantifier scope ("every day before") are the grammar's; scope starts at a unit boundary |
