# Cross-sentence scope (`scope@0`): plan

> Status: planning draft 3, 2026-10-13, design only. No product code, tests or generated files change. Baseline
> `main` at `49de179e`. Draft 2 applied the converged design debate (`manage-agents/debates/design-scope/`,
> Astra + Fable, CONVERGED after round 3: REVISE draft 1, then BUILD) and the DRI's cross-plan synthesis edits 1–8
> of 2026-10-13 (`manage-agents/debates/plan-synthesis/SYNTHESIS.md`), which are part of the final joint position
> and supersede the debate where they differ (edit 3). Draft 3 applies the statement review of the item-1 spec
> (`manage-agents/debates/scope-spec/`, Astra + Fable, CONVERGED after round 3: FIX), and nothing else: its
> corrections, which the spec's 9.3 lists, and the plan sync it asked for (the Boolean `sign`, the status rule,
> F13's three candidates, one stand-in predicate). The research behind every choice here, with the measurements and
> their methods, is [docs/research/scope.md](../research/scope.md). Lean blocks are statement schemata; the exact
> statements, type-checked as a scratch stub, are the item-1 specification [docs/spec/scope.md](scope.md), and
> where a schema here differs, the spec's statement governs. Names marked *(pinned at spec)* depend on in-flight
> branches and are fixed there. Byte figures are ledger spans of the pinned runs
> (`manage-agents/pilots/{claude-constitution,udhr}/run-20261012T1800Z`). Every unlock is an **estimate** until a
> pilot rerun measures it.

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
- provenance, including precedence edges and the owner's provenance for symbols its decoder generates;
- order independence (a conservative, syntactic `Commutes`; anything else is refused);
- reaches regenerated from structure;
- the complete document preserved: exactly as written when there are no governors, and every member, unit and
  content it does not govern unchanged when there are;
- scope introduces no symbol;
- governor status.

A reach that the source leaves open becomes one reading set on its governor, never a guess. Readers see each
governed rule written out in full, with one plain sentence saying where each part came from.

The batches, in build order (5):

| Batch | Hours | What it builds | Bytes on the pinned pilots (estimate) |
|---|---|---|---|
| SC-M0 | 1–2 | pilot tally; no product code | — |
| SC-1a | 4–6 | Lean core: lists and lead-ins | 0 |
| SC-3a | 2–3 | layout anchors (containment moved from discourse), heading and label reaches, titles | 0 pinned |
| **SC-1b** | 3–5 | on the stack: **first number moves** | **+22 B OPEN** |
| SC-1c | 3–5 | explain route and relay | 0 |
| SC-2 | 4–6 | named lists and later qualifications | +68 B LABELLED; +263 B OPEN once attitudes' AT-3a guard decoder lands; fidelity of 874 B |
| SC-E2 | 2 | experiment: plain-English presentation (Sonnet proxy, preliminary); first run after SC-2, rerun after each batch that adds effects or wordings | — |
| SC-3b | 2–3 | condition headings and assertion targets, after its approved addendum | 0 pinned |
| SC-4 | 3–4 | far precedence and forward exceptions | 0 pinned |
| SC-E1 | 2–3 | experiment: deictic reaches | — |
| SC-5 | 4–6 | deictic reaches as reading sets, after its approved addendum | up to 4,196 B upper bound; 0–300 B expected in the next two runs |
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
- It returns the complete document representation, not a list of contents. It first admits the scope block, with
  or without governors, so malformed list names, anchors or forward declarations are refused before anything else
  (`govern_admits`). With no governor and an admitted block it returns the document exactly as written, so the
  chain's ordinary decoding of it is unchanged (`govern_identity`). With governors, every member outside the units,
  every unit's other members and every content it does not govern are unchanged (`govern_preserves`). If the
  item-1 spec finds document metadata outside `units`, `govern` returns it too and the theorem covers it.
- Preservation counts a precedence governor's own rule as affected, although that rule is outside its reach.
- Scope introduces no symbol. Every string `govern` writes is a string of the document or of a governor's payload,
  its frame part or condition (`govern_strings`). For governors bound to the scope block as written, which the
  front-matter decoder guarantees (`decodeScope_bound`), every string is one of the document or the block
  (`govern_no_new_symbols`). Owner-generated declarations and premises arise later, in the owner's decoder, and are
  kept with their provenance (1.6).
- A governor or a governed unit inside a `readings@1` set is refused (`ScopeReadings: <unit>`, theorem
  `readings_refused`). Unrelated reading sets are preserved. SC-5's spec gives a per-choice `govern` over lf-14d's
  joint choices before SC-5 is built.
- It never reads a recorded reach, reading choice or weight as an input to a candidate set.

### 1.2 Governors, reaches, effects

A **governor** is a unit, an effect and a reach.

| Reach | Fixed by | Batch |
|---|---|---|
| `list` | the lead-in's unit text ends with ":". The governed items are the run of list items of the first item's depth, regenerated from the source bytes (Dickerson's rule: each item must complete its lead-in) | SC-1a |
| `list name` | a registered name for a list run ("The current hard constraints ... are as follows."), using discourse's `ContentName` type and decoder; its units must equal the run | SC-2 |
| `anchor` | a heading unit is the first unit of a discourse anchor; it reaches that anchor's units. A condition or title governor sits on the heading; a `precedes` or `yields` governor sits on its own rule, anywhere ("Notwithstanding the rules of section 3, …") | SC-3a |
| `label` | a bold label ending in ":" at the start of a list item reaches that item's units (its continuing sentences and deeper items). A condition or title governor sits on the item; a graph governor anywhere | SC-3a |
| `rules` | stable W1 rule names | SC-4 |
| `frontier` | for "this" and "these": one constituent of the right frontier, removed only when the effect is established not to fit (three-valued `Fits`, 1.5); several remaining candidates make a reading set | SC-5 (after SC-E1) |

| Effect | Meaning (owned by) | Batch |
|---|---|---|
| `frame` | the lead-in's part of each item's norm object; the lead-in's and the item's keys must be disjoint (one owner per field); the merged object is decoded by the chain's own norm decoder | SC-1a |
| `reguard c` | the rule's guard becomes the condition `c`, written in the chain's guard wire form, where `own` in `c` stands for the rule's own guard ("the relevant category"): `own` is substituted with the governed rule's guard JSON and the result is decoded by the chain's own decoder; `c = own and C` is plain narrowing (W1 guard, `VE.Norms.applies`) | SC-2 |
| `carve-out c` | one more W1 carve-out (W1's `applies := G ∧ ¬⋁U`), written and decoded as `reguard`'s condition; the decoding route's own carve-out limit applies | SC-2 |
| `precedes` / `yields` | W1 precedence edges: "notwithstanding X" makes the governor's rules take precedence over X's; "subject to X" the reverse (W1's same-predicate and acyclicity checks, unchanged). A graph step after the unary effects, not an `applyEffect` case (1.4). Never over a `frontier` reach (`ScopeReach`) until SC-5's addendum adds graph fitting | SC-4 |
| `title` | none: a heading or label that only names | SC-3a |

A condition may contain another profile's guard words, such as attitudes' attitude guard nodes. They are written
in the chain's guard wire form and decoded by that profile's decoder after `own` is substituted. Scope defines no
such word.

### 1.3 Statuses

| Unit | Status |
|---|---|
| Governed units | the status the chain gives their composed content, unchanged |
| A governor unit **without content** whose effects change content (`frame`, `reguard`, `carve-out`), with meaning `specified` | the **weakest** status among the units its content-changing governors cover, by `VE.Reports.Status.rank`; UNFORMALISED if any of them is not admitted or has no status, or if it covers none (`governor_status_weakest`, `governor_status_none`) |
| A governor unit without content and with any other meaning | its own status, unchanged: scope never claims a unit the translator marked open or unformalised |
| A governor unit with content (a label item, a `precedes`/`yields` rule) | its own composed content's status: it is a governed or ordinary rule unit |
| Title governor, list-name registration | the document mode's own status, unchanged: LABELLED when its meaning is `specified` and it has no content, as discourse's naming clause is; reported apart from semantic coverage |
| A forward declaration (SC-4) | the weakest status of the later rules it announces |

Governed and governor bytes are each counted once, under their own spans. The statuses folded are the document
mode's, before the fold (no fixpoint).

### 1.4 Order

For each governed unit, the effects apply in a fixed order:
1. its lead-in's frame (which makes the rule);
2. anchors, outermost first;
3. bullet labels;
4. list and list-name governors;
5. rule governors;
6. frontier governors.

Within one class, governors apply in source order. `Commutes` is syntactic and conservative: it is true only for
pairs drawn from plain narrowings `own and C` (with `C` free of `own`) and carve-outs free of `own`, and these
commute (`commute_applies`), so the order changes nothing. Every other pair of governors on one unit is refused
with `ScopeOrder: <unit>: <g1>, <g2>`: unknown commutation is refused, so source order is never a hidden choice.

Precedence is its own step. The unary effects (`reguard`, `carve-out`) go through `applyEffect`. Then
`edgesOf D g` is computed over the composed rules and added to `over`: on the governor's own rule for `precedes`,
on the targets' rules for `yields`, each edge with its governor as provenance. The composed tree then goes to the
chain's checker unchanged.

### 1.5 Ambiguity

Only the `frontier` reach can have several candidates. `Fits` is three-valued: a candidate is removed only when
every one of its units is admitted and the effect fails to type there. A unit that is not admitted keeps its
candidate live, so a gap in coverage never manufactures a unique reach. A unit whose composed rule meets a decoder
limit (`ResourceLimit`) is unresolved too: exhaustion is UNKNOWN, never evidence against a candidate
(`fitAt_limit`). A frontier reach carries only the unary effects (`reguard`, `carve-out`), so fitting never needs
the governor's own rule or the graph step.
- **Several candidates remain:** `AmbiguousScope: <governor>: <candidates>`.
  - In authoring, the IDE asks one question.
  - In translation, the candidates become one reading set on the governor, coupled to every affected unit through
    lf-14d's joint choices. That is one choice among at most 8 candidates, never a product over the affected
    units.
- **One candidate remains and it is established to fit:** the reach is fixed. In authoring the structural rule
  defines the reading. In translation a single surviving candidate is a recorded claim, not a certified reading
  of the source.
- **One candidate remains only because one of its units is not admitted:** it is the only remaining candidate, not
  the only one established to fit. It stays unresolved (`UnresolvedScope`), with no definitive dependent verdict.
- **No candidate fits:** `UnresolvedScope: <governor>`; the unit stays UNFORMALISED.
- **More than 8 frontier constituents, or budget exhausted:** `ResourceLimit: scope`, which is UNKNOWN for every
  dependent verdict, never a truncated list, never a rejection and never a chosen reach.

### 1.6 What the reader sees

The reviewed presentation shows each governed rule written out in full, rendered by the existing rule renderer
(one owner). It then adds one provenance sentence per contributing governor, e.g.:

> *Where the parts come from:* "should never" comes from the line above the list, "Claude should never:". The
> condition comes from a later sentence, "Hard constraints are centrally meant to apply to cases where ...", which
> covers all seven items of this list.

Unit ids, arrows and brackets are hidden by default; they appear in the provenance view. Lean owns the
provenance wording table (`VE/Scope/English.lean`); Python prints it.

When an owner's decoder generates symbols from a governed unit, scope's preservation and provenance statements use
the owner's exported provenance; scope never re-derives a split or a key.
- For act-phrases, the chain splits a governed rule into `<rule>-a<i>` and predicates `p__i`; scope uses
  `VE.Acts.SplitMap`.
- For attitudes and the other packs, scope uses the pack's `origins`.

A provenance sentence for a generated rule names its source rule through the map. A `rules` reach naming a split
source rule follows AP's reference table: "r over a split s" becomes "r over every s-a<i>". Owner-generated
declarations and premises are kept **with** their provenance, per joint choice for SC-5.

## 2. English

### 2.1 Translation (what the pilots write)

A translator records governors in the front matter `scope` block (3) and writes each item's part of a rule as
`{"part": {...}}` content. Source wordings and how they are recorded:

| Source wording | Recorded as |
|---|---|
| "Claude should never:" + bullets | `frame` over the `list` reach |
| "The current hard constraints ... are as follows." | list name |
| "... are centrally meant to apply to cases where ..." | `reguard` over the list name, its attitude words written as attitudes' guard nodes |
| "Regardless of operator instructions, Claude should by default:" + bullets | `frame` whose part carries the soft fields, which weighing and soft own |
| "Notwithstanding ...", "Subject to ..." | `precedes` / `yields` |
| a heading or bullet label that is a full clause ("There's no operator prompt:") | `reguard` (narrowing) |
| a noun heading ("Hard constraints") | `title` |

A wording whose reach the source leaves open is a reading set (1.5). A wording that states something *about* a
list without changing its rules (u0170.s01, "The list of hard constraints above is not a list of all the behaviors
we think Claude should never exhibit.") is not a governor. Two checks refuse to read it as one:
- **F5a (SC-7):** the shared English catalogue parses that wording to no governor (the grammar check).
- **F5b (translation):** the pilot audit flags any governor recorded on u0170.s01.

Lean sees the layout and the recorded content, not the wording. In translation an effect is therefore a recorded
claim: Lean checks its reach and how it composes, not that the sentence says it. Source fidelity is reviewed outside
Lean, by the pilot audit.

### 2.2 Authoring (SC-7, last)

Each wording below has one reading. The IDE shows the paraphrase and writes the block from the English.

| Wording | The one reading (IDE paraphrase) |
|---|---|
| `Every instance of Claude must not:` followed by a bulleted list | "Each item below is its own rule: ‘Every instance of Claude must not <item>.’" Each item must complete the sentence |
| `The rules below are called the hard constraints.` | "‘The hard constraints’ names the rules of the list that follows." |
| `The hard constraints apply only where <condition>.`, where <condition> does not mention "its kind" (a plain narrowing) | "Each of the 7 rules called ‘the hard constraints’ applies only where <condition>." |
| `In place of their own condition, the hard constraints apply only where Claude knows that the act is of its kind, or thinks it quite likely that it is.` (a guard replacement; "In place of" marks it) | "Each of the 7 rules now applies where Claude knows that the act is of its kind, or thinks it quite likely that it is, instead of where its own act occurs; its existing carve-outs still apply. ‘Its kind’ is each rule's own act." (`own`; the attitude words are attitudes'.) |
| `The hard constraints do not apply when <condition>.` | "None of the 7 rules applies when <condition>; other rules may decide; if none does, <the default sentence of each rule's predicate>." (W1 2.5) |
| `Notwithstanding the rules of section 3, <rule>.` (the rule is rule 9; the governor is rule 9's own unit) | "Wherever rule 9, or a rule that takes precedence over it directly or through other rules, applies, no rule of section 3 decides on that act." (W1 2.3) |
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
    {"id": "g1", "unit": "u0164.s02", "reach": {"list": "u0164.s02"}, "units": ["u0165.s01", "…", "u0165.s07"],
     "effect": {"frame": {"sign": false, "unless": [], "over": []}}},
    {"id": "g2", "unit": "u0173.s01", "reach": {"list_name": "the hard constraints"},
     "units": ["u0165.s01", "…", "u0165.s07"],
     "effect": {"reguard": ["or", ["and", "own", {"attitude": {"holder": ["var", 0], "mode": "knows",
                                                               "content": "own"}}],
                                  {"attitude": {"holder": ["var", 0], "mode": "thinks", "degree": "quite likely",
                                                "content": "own"}}]}}
  ]
}
```

The example is illustrative:
- The frame's keys are whichever norm-object keys the seven rules share today; the spec pins them from the
  chain's decoder. W1's `sign` is a Boolean; on the norms chain the shared members are `sign`, `unless` and `over`.
- `units` records each governor's reach, regenerated and compared (absent only for a frontier reach).
- The condition uses attitudes' guard nodes (AT-3a): the knowledge conjunct is a `"knows"` node and the likelihood
  is a `"thinks"` node with `degree` `"quite likely"`, each with `content` `own`.
- `own` is substituted with the governed rule's guard JSON before decoding. A rule whose guard is not
  quantifier-free over the base vocabulary therefore gets attitudes' own refusal, not a scope diagnostic.

Item unit content: `{"part": {"name": "hc-cbrn-uplift", "predicate": "restricted_act_permitted", "guard": [...]}}`
(`restricted_act_permitted` is the one stand-in predicate of every F1 fixture).

Wire rules:
- Every id is a token of the existing grammar. Optional fields are absent, never `null`.
- Reaches and list-name units are recorded, then **regenerated and compared**: a mismatch is
  `ManifestMismatch: scope.<field>`.
- At most 256 governors and 256 list names. A list name's `scope` must be `"doc"` in `scope@0`, since no scoped
  lookup exists yet; anything else is `InvalidInput`.
- The block is inside the document identity, like discourse's.
- The `part` keys are the chain's own norm-object keys. Scope keeps no list of its own.

## 4. Lean: files and shared definitions

New directories:
- `lean/VE/Layout/`: `List.lean` (SC-1a), `Anchors.lean` (SC-3a).
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

/-- A condition is guard wire JSON in the chain's guard form; the JSON string `"own"` stands for the governed
    rule's own guard. No hooks: another profile's guard words (attitudes' guard nodes) are that profile's wire,
    decoded by the chain's decoder after `own` is substituted. -/
inductive Effect
  | frame (part : Lean.Json) | reguard (c : Lean.Json) | carveOut (c : Lean.Json) | precedes | yields | title

inductive Reach
  | list (lead : String) | listName (name : String) | anchor (id : String) | label (item : String)
  | rules (names : List String) | frontier

structure Governor where
  id : String
  unit : String
  effect : Effect
  reach : Reach

structure SDoc where
  layout : List VE.Layout.Unit
  doc : Lean.Json                                         -- the complete document after RESOLVE (units and metadata)
  governors : List Governor
  listNames : List (VE.Discourse.ContentName × String)    -- the name and the lead-in whose run it names (SC-2)
  anchors : List VE.Discourse.Anchor                      -- discourse's anchors, decoded by discourse's decoder (SC-3a)
  re : VE.Readings.ReadingsEnvironment                    -- the chain's decoding environment (pinned at spec)

/-- Lead-in and item joined; a key on both sides is refused, never overridden. -/
def mergeParts (unit : String) (lead item : Lean.Json) : Except String Lean.Json
/-- An item's rule: the chain's own norm decoder (today `VE.Readings.Wire.decodeNorm`) on the joined object. -/
def itemRule (D : SDoc) (u : String) (lead item : Lean.Json) : Except String VE.SoftNorms.SoftNode :=
  do VE.Readings.Wire.decodeNorm D.re (← mergeParts u lead item)
/-- `own` replaced by the rule's guard JSON; the chain's decoder reads the result. -/
def substOwn (guard c : Lean.Json) : Lean.Json
/-- Unary effects only, on the rule's JSON object; precedence is the graph step `edgesOf`. -/
def applyEffect : Effect → Lean.Json → Except String Lean.Json
def covered (D : SDoc) : Reach → Except String (List String)
def baseObj (D : SDoc) (u : String) : Except String Lean.Json   -- its own norm object, or its frame joined to its part
def governorsOf (D : SDoc) (u : String) : List Governor        -- unary governors covering u, order 1.4
def edgesOf (D : SDoc) (g : Governor) : List (String × String)  -- over the composed rules (SC-4)
def govern (D : SDoc) : Except String Lean.Json                 -- the complete document

end VE.Scope
```

## 5. Batches

The item-1 specification `docs/spec/scope.md` and its statement review come before any build:
- The statement review of spec draft 1 (Astra + Fable, `manage-agents/debates/scope-spec/`) returned **FIX** with
  one converged correction set; spec draft 2 applies it (its 9.3).
- A confirmation round on that diff only, not a fresh review, decides PASS. A clean confirmation opens SC-1a and
  SC-3a.
- SC-3b and SC-5 stay gated on approved addenda, whose obligations the spec records now (its 9.4).
- Theorem statements are type-checked as stubs in a scratch file that is never committed. Elaborating with
  `sorry` only shows that a statement typechecks; every repaired contract also has an executed fixture.

That is a stage, not a batch.

The first pilot number moves at **SC-1b**:
- SC-1a and SC-1b are the smallest feature that moves one, split because SC-1b must edit files that lf-16g is
  still changing.
- If lf-16g has merged when building starts, they run as one batch.

Build order (the debate's, unchanged by the cross-plan review):
1. SC-M0.
2. The item-1 spec and its statement review (FIX; draft 2 applies the corrections), then the confirmation round.
3. SC-1a.
4. SC-3a, alongside SC-1a or right after it.
5. SC-1b after lf-16g. It joins SC-1a as one batch if lf-16g has already merged.
6. SC-1c.
7. SC-2. Its 263 B claim waits for attitudes' AT-3a guard decoder.
8. SC-E2, first run, on the effects built so far.
9. SC-3b, after its addendum is approved.
10. SC-4, then an SC-E2 rerun.
11. SC-E1, revised (three-valued `Fits`, the added bar and the stated scope).
12. SC-5, after lf-14d and its approved addendum, which includes the per-choice `govern`.
13. SC-6, after composition S2b.
14. SC-7, carrying F5a. Final SC-E2 run.

Landing order across the plans (cross-plan synthesis):
- SC-M0 runs now.
- SC-1a and SC-3a are Lean-core work, in parallel with the other plans' cores.
- SC-1/SC-2 land after attitudes and before quantities. SC-2 waits for AT-3a's decoder.
- SC-3b to SC-7 land after events and before math-evidence.

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
  - `lean/VE/Layout/List.lean` (`Unit`, `ofSource` with the one-pass paragraph count `paraCounts`, `listRun`,
    `GovernedItem`);
  - `lean/VE/Scope/{Wire,Govern,Theorems,Examples}.lean`, frame effect only, with the block's admission run first
    and the run path `governFast` (each governor's reach and each rule unit's base name computed once, proved
    equal to `govern`);
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

/-- Identity: without governors, an admitted block leaves the complete document exactly as written, so the chain's
    ordinary decoding of it is unchanged. -/
theorem govern_identity (D : SDoc) (h₀ : admitBlock D = .ok ()) (h : D.governors = []) (hp : partUnits D = []) :
    govern D = .ok D.doc

/-- The block is admitted before anything else, with or without governors. -/
theorem govern_admits (D : SDoc) (out : Lean.Json) (ho : govern D = .ok out) : admitBlock D = .ok ()

/-- Preservation: every member outside `units`, the unit order, every unit member but its content, and every
    content `govern` does not affect, are the document's own. -/
theorem govern_preserves (D : SDoc) (out : Lean.Json) (ho : govern D = .ok out) :
    (∀ k, k ≠ "units" → out.getObjVal? k = D.doc.getObjVal? k) ∧
    (unitsOf out).map idOf = (unitsOf D.doc).map idOf ∧
    ∀ i x y, (unitsOf out)[i]? = some x → (unitsOf D.doc)[i]? = some y →
      (∀ k, k ≠ "content" → x.getObjVal? k = y.getObjVal? k) ∧ (idOf y ∉ affected D → x = y)

/-- Provenance: a governed rule is its unit's base rule with exactly the covering unary governors applied, in
    order, and `over` is the base `over` plus exactly the precedence edges into the unit. -/
theorem govern_provenance (D : SDoc) (out : Lean.Json) (ho : govern D = .ok out) (u : String) (hu : u ∈ affected D) :
    ∃ o₀ o₁ es, baseObj D u = .ok o₀ ∧
      (governorsOf D u).foldlM (fun o g => applyEffect u g.effect o) o₀ = .ok o₁ ∧
      edgesFor D u = .ok es ∧ normOf (contentOf out u) = some (addOver es o₁) ∧
      ∀ g ∈ governorsOf D u, ∃ us, covered D g.reach = .ok us ∧ u ∈ us

theorem governorsOf_iff (D : SDoc) (u : String) (g : Governor) :
    g ∈ governorsOf D u ↔ g ∈ D.governors ∧ unary g.effect = true ∧
      ∃ us, covered D g.reach = .ok us ∧ u ∈ us

/-- Every string value of the answer is one of the document or of a governor's payload (frame part or condition). -/
theorem govern_strings (D : SDoc) (out : Lean.Json) (ho : govern D = .ok out) (s : String) (hs : HasStr s out) :
    HasStr s D.doc ∨ ∃ g ∈ D.governors, HasStr s (payload g.effect)

/-- Scope introduces no symbol: for governors bound to the block (`BlockBound`, which SC-1b's decoder guarantees),
    every string value of the answer is one of the document or of the scope block. Owner-generated declarations
    and premises arise in the owner's decoder and are kept with their provenance. -/
theorem govern_no_new_symbols (D : SDoc) (hb : BlockBound D) (out : Lean.Json) (ho : govern D = .ok out)
    (s : String) (hs : HasStr s out) : HasStr s D.doc ∨ HasStr s D.block

/-- The run path answers exactly as `govern`. -/
theorem governFast_eq (D : SDoc) : governFast D = govern D
```

**Fixtures** (pinned bytes, `Examples.lean` and `tests/test_scope_lean.py`):

| Id | Fixture | Expected |
|---|---|---|
| F1 | u0164.s02 "Claude should never:" with u0165.s01–s07; the lead part holds the members the seven rules share, minus `name`, `predicate` and `guard` (on the norms chain `{"sign": false, "unless": [], "over": []}`, with W1's Boolean `sign`; any soft field on the soft chain); each item part `{name, predicate, guard}` comes from the pilot's rules, with the guards exactly as AT-0p left them | 7 rules equal to the pilot's, byte for byte |
| F1′ | an item that also writes `sign` | `ScopeConflict: u0165.s03: sign` |
| F1″ | an item missing `predicate` | the chain decoder's own diagnostic, unchanged |
| F1‴ | u0166.s01 after the run | not an item |
| F2 | u0182.s02 + u0182.s03 ("Or does it escape these mechanisms?", mid-line) | u0182.s03 continues u0182.s02, not a new item |
| F2′ | u0072.s02 + u0073.s01–s10 | the "+ Example:" sub-bullets (depth 1) are not items of the depth-0 run |
| F2″ | a lead-in followed by prose | `NotALeadIn: <unit>` |

| F-id | no governors, no `part` content; and no governors with a `part` content | the document as written; `ScopeOrphanPart: <unit>` |
| F-meta | malformed metadata with no governor: a list name's units, a list name's `scope`, 257 list names, two root anchors (once SC-3a's anchor checks are in) | refused with the admission's text each time, never the document |
| F-sym | a decoded governor whose payload is not in the block (`block = null`) | the answer holds a string in neither the document nor the block: the binding hypothesis of `govern_no_new_symbols` is needed |
| F-rs | a governed unit owned by a reading set | `ScopeReadings: <unit>`; an unrelated reading set is returned unchanged |

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
  - **AR-10**'s profile-gate table lands before SC-1b's row. `scope@0` is one row of AR-10's table, as a wrapper
    at step 1b over the norms, norm-defaults, soft and rights routes. The row carries scope's composition proof.
- **Shared files touched.**
  - `lean/VE/Compose/Dispatch.lean`: one row of AR-10's profile-gate table, in landing order, and its composition
    proof. No hand edits to `wrapperProfiles`, `Route.scope`, `sitsOn`, `wrapperHead` or the existing case proofs.
  - `lean/VE/Service/Document.lean` *(pinned at spec; lf-16's file)*: calls `VE.Scope.govern` before the chain,
    and folds `governorStatus` for governor units. Two call sites, after lf-16g. They join the document-mode queue
    in landing order: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10.
  - `ve/profiles.py`: no hand-written line. Python's profile data is generated from AR-10's table.
  - Generated, via `tools/regen_generated.py --write` (never by hand): the document mode's schema,
    `tools/gate-collection.json`, `lean/checkers.lock`, the profile data.
  - `tools/bench/test_perf.py` and its baselines: the B1 row.

```lean
/-- A governor counts under the weakest status of what it governs, never a stronger one. -/
def governorStatus (st : String → Option Status) (us : List String) : Option Status   -- VE.Reports.Status, by rank

theorem governor_status_weakest (st : String → Option Status) (us : List String) (s : Status)
    (h : governorStatus st us = some s) :
    us ≠ [] ∧ (∀ u ∈ us, ∃ t, st u = some t ∧ s.rank ≤ t.rank) ∧ ∃ u ∈ us, st u = some s

/-- The front-matter decoder binds the governors to the scope block as written, and reads the layout of exactly
    the document's units. -/
theorem decodeScope_bound (front : Lean.Json) (D : SDoc) (h : decodeScope front = .ok D) : BlockBound D
theorem decodeScope_layout (front : Lean.Json) (D : SDoc) (h : decodeScope front = .ok D) :
    D.layout.map (·.id) = unitIds D.doc

/-- For a decoded document, scope introduces no symbol: every string GOVERN writes is the document's or the
    block's. -/
theorem decoded_no_new_symbols (front : Lean.Json) (D : SDoc) (h : decodeScope front = .ok D) (out : Lean.Json)
    (ho : govern D = .ok out) (s : String) (hs : HasStr s out) : HasStr s D.doc ∨ HasStr s D.block

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
| F1-off | the same document without `scope@0` | the `part` contents decode as pending (`decodeContent` returns `.pending` for an unknown key), so the seven units are UNFORMALISED |
| F1-bad | one item not admitted | u0164.s02 UNFORMALISED |
| B1 | a `tools/bench` row: F1-doc's document, the full pinned constitution pilot (184,893 B, 1,132 units), through the layout and the run path `governFast` | a benchmark row with its baseline; never a timing assertion in the suite |

- **Pilot.**
  - SC-1b's and SC-2's edits to u0164.s01–s02, u0165.s01–s07 and u0173.s01 are steps 2 and 3 of the
    hard-constraint queue `AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5` (then QT-B4 and WG-8, whichever is ready
    first). Each step starts from the translation as the previous step left it.
  - Rerun the constitution with the translation's u0164/u0165 block rewritten (pilot data). The item parts keep
    the guards exactly as AT-0p left them.
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
- **Registration.** The `scope` mode registers through AR-10's mode registry and keeps the relayed-route recipe.
- **Answer rows.** Per governed unit: `unit`, `governors` (`id`, `unit`, `effect` word, `reach` units), and
  `provenance` (Lean's sentences from `VE/Scope/English.lean`). A rule an owner's decoder generates from the unit
  is listed through the owner's map (`VE.Acts.SplitMap` for act-phrases; a pack's `origins`), and its provenance
  sentence names its source rule (1.6).
- **Binding.** Every unit and governor id must exist in the request.
- **Shared files touched.**
  - `lean/VE/Service/Protocol.lean`: AR-10's registry line. Its edit joins the protocol queue in landing order.
  - `ve/backends/service_schema.py`: `MODES`, append, in the same queue.
  - `ve/__main__.py`: subcommand, append.
  - The two audit files: append, or regenerate.
  - Generated files via `regen_generated.py`.
- **Bytes.** 0. This batch is the reader's view, and it gates SC-E2.

### SC-2. Named lists and later qualifications (4–6 h)

- **Goal.** A later sentence narrows, replaces or carves out the condition of a named set of rules. A list name
  registers a run.
- **Depends on.** SC-1a. The pilot claim of u0173.s01 also needs SC-1b and attitudes' AT-3a, which decodes
  attitude guard nodes inside the chain's norm decoders (`design/attitudes`, AT plan: "u0173.s01 attached to the
  seven rules"). SC-2's code needs AT-3a for the F3 case with attitude words; u0173.s01's 263 B claim waits for it.
- **New files.** `lean/VE/Scope/Effects.lean`. The list-name check is added to `Govern.lean` (a scope file).
- **Shared files touched.**
  - The audit, append.
  - `lean/VE/Discourse/Wire.lean`: none. Scope calls `decodeContentName` as is.

The effect theorems are stated over the chain decoder's output, for conditions without attitude words (their
substituted condition decodes in the base guard grammar). What attitude words mean is attitudes' theorem, not
scope's.

```lean
theorem reguard_applies (D : SDoc) (u : String) (c o o' : Lean.Json) (N N' : VE.SoftNorms.SoftNode) (G' : VE.Formula)
    (h : applyEffect u (.reguard c) o = .ok o') (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N')
    (hG : VE.Norms.Wire.decodeBudgeted (substOwn (o.getObjValD "guard") c) = .ok G')
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    N' = { N with guard := G' } ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ G'.denote S ρ ∧ ¬ (VE.Norms.anyF N.carveOuts).denote S ρ)

/-- Plain narrowing is the special case: one more guard conjunct. -/
theorem restrict_applies (D : SDoc) (u : String) (C o o' : Lean.Json) (C' : VE.Formula) (N N' : VE.SoftNorms.SoftNode)
    (hC : hasOwn C = false) (hC' : VE.Norms.Wire.decodeBudgeted C = .ok C')
    (h : applyEffect u (.reguard (Lean.Json.arr #[.str "and", .str "own", C])) o = .ok o')
    (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N) (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N')
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    N' = { N with guard := .and N.guard C' } ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ (VE.Norms.applies N.toNode).denote S ρ ∧ C'.denote S ρ)

theorem carveOut_applies (D : SDoc) (u : String) (c o o' : Lean.Json) (N N' : VE.SoftNorms.SoftNode) (C : VE.Formula)
    (h : applyEffect u (.carveOut c) o = .ok o') (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N')
    (hC : VE.Norms.Wire.decodeBudgeted (substOwn (o.getObjValD "guard") c) = .ok C)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    N' = { N with carveOuts := N.carveOuts ++ [C] } ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ (VE.Norms.applies N.toNode).denote S ρ ∧ ¬ C.denote S ρ)

/-- Typing is kept when the instantiated condition type-checks in the rule's situation context. -/
theorem applyEffect_typed (D : SDoc) (u : String) (e : Effect) (o o' : Lean.Json) (N N' : VE.SoftNorms.SoftNode)
    (E : VE.Environment) (Γ : List String) (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (h : applyEffect u e o = .ok o') (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N') (hT : Typed E Γ N)
    (hc : ∀ c ∈ conditions e, ∀ C,
      VE.Norms.Wire.decodeBudgeted (substOwn (o.getObjValD "guard") c) = .ok C → C.check E Γ = true) :
    Typed E Γ N'

/-- Narrowings and own-free carve-outs commute, so source order is never a hidden choice. -/
theorem commute_applies (D : SDoc) (u : String) (e₁ e₂ : Effect) (hc : Commutes e₁ e₂ = true) (o o₁ o₂ : Lean.Json)
    (N₁ N₂ : VE.SoftNorms.SoftNode)
    (h₁ : (applyEffect u e₁ o).bind (applyEffect u e₂) = .ok o₁)
    (h₂ : (applyEffect u e₂ o).bind (applyEffect u e₁) = .ok o₂)
    (hN₁ : VE.Readings.Wire.decodeNorm D.re o₁ = .ok N₁) (hN₂ : VE.Readings.Wire.decodeNorm D.re o₂ = .ok N₂)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    { N₁ with guard := .top, carveOuts := [] } = { N₂ with guard := .top, carveOuts := [] } ∧
      ((VE.Norms.applies N₁.toNode).denote S ρ ↔ (VE.Norms.applies N₂.toNode).denote S ρ)

theorem order_refused (D : SDoc) (h₀ : admitBlock D = .ok ()) (u : String) (hu : u ∈ unitIds D.doc)
    (g₁ g₂ : Governor) (h₁ : g₁ ∈ governorsOf D u) (h₂ : g₂ ∈ governorsOf D u) (hne : g₁.id ≠ g₂.id)
    (hc : Commutes g₁.effect g₂.effect = false) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeOrder" = true

/-- A list name names exactly its lead-in's run. -/
theorem listName_run (D : SDoc) (n : VE.Discourse.ContentName) (lead : String) (h : (n, lead) ∈ D.listNames)
    (us : List String) (hc : covered D (.listName n.name) = .ok us) :
    VE.Layout.listRun D.layout lead = .ok us ∧ n.units = us
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F3 | u0164.s01 registers "the hard constraints" over the run of u0164.s02; u0173.s01 is `reguard ((own and knows(own)) or thinks-quite-likely(own))`, written with attitude guard nodes | Each rule's guard JSON is the condition with `own` replaced by that rule's guard. With `attitudes@0`, AT-3a's decoder reads it as `(G_N ∧ K(G_N)) ∨ L(G_N)`. Without `attitudes@0` the decoder refuses the attitude node, and u0173.s01 stays UNFORMALISED |
| F4 | **the audit's case**: a two-element model where L(G) holds and G does not | the rule applies under F3 and does not under the pilot's narrowed guard `G ∧ K`. This separates the faithful reading from the rejected one |
| F4-r3 | F4 against the "only where" row: the replacement's condition read as a narrowing, `G ∧ ((G ∧ K) ∨ L)` | does not hold where the replacement holds, so the two wordings are two readings and "In place of" decides |
| F4-c | the replacement on a rule with a carve-out `T` | the carve-out is kept; with `T` holding, the replaced rule does not apply |
| F6 | synthetic "The hard constraints do not apply when Claude is being tested by Anthropic." | one carve-out on each of the 7 rules |
| F6′ | a carve-out on a rule already at its route's carve-out limit | the decoding route's own limit diagnostic, unchanged |
| F7 | two `own`-mentioning reguards on one rule | `ScopeOrder` |
| F7′ | a narrowing plus a carve-out | accepted, and the same in either order |

F5 moves to SC-7 (F5a, the catalogue check) and to the pilot audit (F5b), 2.1: Lean sees no wording.

**Bytes (estimates):**
- u0164.s01, 68 B: LABELLED, reported apart from semantic coverage.
- u0173.s01, 263 B: OPEN, **only** with AT-3a's guard decoder; 0 otherwise.
- Fidelity: the 874 B of u0165.s01–s07, which the audit judged unfaithful, carry the reading the audit asks for.

**Pre-registered:**
- u0173.s01 is claimed only with the full schema, never with the narrowing `G ∧ K`.
- The F4 model must separate the two readings.

**Pilot (step 3 of the hard-constraint queue).** SC-2 starts from the translation as SC-1b left it. It removes from
the seven item guards whatever attitude conjuncts they then carry, and moves the condition into u0173.s01's
governor, written with attitude guard nodes and `own`. AT-6a/AT-6b then work on the translation as SC-2 left it.

**Deleted.** In the pilot translation:
- the per-rule attitude conjuncts (AT-0p's open terms, two per rule);
- the seven notes that restate u0173.s01.

Both become one governor. `restricted_action_knowing_or_quite_likely` is already gone after AT-0p.

### SC-3a. Layout anchors, heading and label reaches, titles (2–3 h)

- **Goal.** A heading reaches its anchor and a bold label reaches its item; a heading or label that only names is
  a title (no effect). This batch adds no condition effect: condition headings are SC-3b's.
- **Depends on.** SC-1a (`Effect`, `Governor` and `Reach` already exist there, and `title` is identity). The
  discourse anchor decoder, merged. It runs alongside SC-1a or right after it, which also lands the only edit to
  `Access.lean` while no branch touches discourse.
- **New files.** `lean/VE/Layout/Anchors.lean`. The bodies of discourse's `within`, `narrower` and
  `innermostAnchor` move here, over `(unit spans, anchors)`. Discourse's three definitions become one-line calls,
  so there is one owner for anchor containment. Discourse's anchor checks (`anchorsOk`: one tree, nested and
  non-overlapping spans, unique labels per parent, exports) move here the same way, over `(anchors, definition
  spans, unary test)`, with the generic helpers they call (`req`, `runAll`, `allOk`, `dupOf`, `spanIn`,
  `spansDisjoint`). Scope's admission calls them on the block's anchors, so one body checks anchors for both (the
  statement review's decision on the spec's question 9.2.1).
- **Shared files touched.**
  - `lean/VE/Discourse/Access.lean`: the three bodies become calls. Statements and theorems are unchanged;
    `acc_no_heuristic`, `name_scope` and `innermost_within` are re-proved by unfolding. No in-flight branch touches
    discourse (survey 2026-10-12); recheck at start.
  - `lean/VE/Discourse/WellFormed.lean`: `anchorsOk` becomes a call (`discourse_anchorsOk_unchanged`); the helpers
    move below `Access.lean` and discourse opens them from there; discourse's anchor fixtures pass unchanged.
  - `lean/VE/Route/frozen-sources.sha256`: `Access.lean` and `WellFormed.lean` are listed there; regenerated with
    its own tool, never by hand.
  - `tools/trust-classes.json`: the entries of `Access.lean` and `WellFormed.lean`, and the trust class of the new
    `VE/Layout/Anchors.lean`.

```lean
theorem anchor_reach_iff (D : SDoc) (a : VE.Discourse.Anchor) (h : a ∈ D.anchors) (us : List String)
    (hc : covered D (.anchor a.id) = .ok us) (u : String) :
    u ∈ us ↔ VE.Layout.within (unitSpans D) D.anchors u a.id = true ∧ u ≠ headingOf D a.id

theorem title_identity (D : SDoc) (g : Governor) (h : g.effect = .title) (D' : SDoc)
    (hD : D' = { D with governors := D.governors.erase g }) : govern D = govern D'

theorem discourse_within_unchanged (D : VE.Discourse.DDoc) (u a : String) :
    VE.Discourse.within D u a = VE.Layout.within (VE.Discourse.unitSpans D) D.K.anchors u a

theorem discourse_anchorsOk_unchanged (D : VE.Discourse.DDoc) :
    VE.Discourse.anchorsOk D = VE.Layout.anchorsOk D.K.anchors (definitionSpans D) (VE.Discourse.unaryPred D.E)
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F8 | UDHR u109 "## Article 29" with u110–u112, under the document's root anchor | a title: contents and statuses unchanged (regression) |
| F8-tree | the same anchors without a root | discourse's `InvalidInput: anchors must form one tree`, from scope's admission |
| F9′ | `## Instructable behaviors` | title |
| F10 | u0073.s01 "* **There’s no operator prompt:** ..." | the label reaches u0073.s01–s04 and not the "+ Example:" sub-bullets' own label. Structure only: their content is blocked by graded force |

- **Bytes.** 0 on the pinned runs (estimate). The u0073 block (2,475 B) waits on graded force.
- **Deleted.** Discourse's anchor bodies: the three containment definitions and the anchor checks (moved, not
  copied).

### SC-3b. Condition headings and assertion targets (2–3 h)

- **Goal.** A heading or label that is a full `When`/`If` clause governs its anchor or item as a condition.
- **Depends on.** SC-2 (`Effects.lean`: the condition effects) and SC-3a (the anchor and label reaches). An
  **approved addendum** to the spec (its 9.4), reviewed before the batch is built. Extending `baseObj` alone cannot
  admit an assertion: admission, `ruleUnits` and `affected` exclude assertions, and `newContent` writes norm
  wrappers. The addendum specifies the assertion cases of `baseObj`, `ruleUnits`, `affected`, the `ScopeNotARule`
  check and `newContent`, and the matching preservation and provenance statements.
- **Shared files touched.** None beyond the audit.

**Assertions.** Assertion targets are added here because headings in policies and papers govern plain claims too.
For a closed condition `C`:
- narrowing turns `φ` into `C → φ`;
- a carve-out turns `φ` into `¬C → φ`.

```lean
theorem assertion_restrict_denote (C φ : VE.Formula) (S : VE.Structure.{u}) :
    (restrictAssertion C φ).denote S [] ↔ (C.denote S [] → φ.denote S [])
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F9 | synthetic `## When there is no operator prompt` over two rules | each guard gains the condition |

- **Bytes.** 0 on the pinned runs (estimate).

### SC-4. Far precedence and forward exceptions (3–4 h)

- **Goal.** Handle three wordings:
  - "Notwithstanding <rules or section>" and "Subject to <rules or section>" become W1 precedence edges.
  - "Rule n has exceptions stated later in this section." becomes a checked forward declaration.
- **Depends on.** SC-2 (`Effect`), SC-3a (anchor reach).
- **Shared files touched.** None beyond the audit. The composed tree goes through `VE.Norms.check` unchanged.

Precedence is the graph step of 1.4: the edges are computed over the composed rules (the unary effects already
applied), added to `over` of the governor's own rule (`precedes`) or of the targets' rules (`yields`), and
`govern_provenance`'s `over` is the base `over` plus exactly the edges into the unit. A graph governor sits on its
own rule, so "Notwithstanding the rules of section 3, …" reaches section 3 by `anchor` from outside it (F11-a).
Forward declarations are checked as the last step of the block's admission, so a document without governors is
checked too, and every theorem whose hypothesis is a successful admission covers them unchanged.

```lean
theorem precedes_edges (D : SDoc) (out : Lean.Json) (ho : govern D = .ok out) (g : Governor) (hg : g ∈ D.governors)
    (he : g.effect = .precedes) (t : List (String × VE.SoftNorms.SoftNode)) (ht : ruleTable D = .ok t) (v : String)
    (N M : VE.SoftNorms.SoftNode) (hN : t.lookup g.unit = some N) (hM : t.lookup v = some M)
    (hv : ∃ us, covered D g.reach = .ok us ∧ v ∈ us) (hp : M.pred = N.pred) (hn : M.name ≠ N.name) :
    ∃ o xs, normOf (contentOf out g.unit) = some o ∧ o.getObjVal? "over" = .ok (.arr xs) ∧ Lean.Json.str M.name ∈ xs

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
| F11-a | the same wording with an `anchor` reach on section 3, the governor on rule 9's own unit outside it, end to end | edges added (`r9`'s `over` gains the same-predicate rule) |
| F11′ | the same over other predicates | `ScopeNoEffect` |
| F11″ | edges that close a cycle | W1's `DependencyCycle`, unchanged |
| F12 | u0047.s05–s06 "That said, we discuss some exceptions to this in the section on “broad safety” below." | the reach is an anchor, but no rules are named, so recorded as residual (`UnresolvedScope`), never guessed |
| F12-f0 | a forward declaration with no later exception, in a document with no governor | `ScopeForward`, never the document |

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
- **`Fits` is three-valued** (1.5): the scratch script removes a candidate only when every one of its units is
  admitted and the effect fails to type there.
- **Pre-registered bar.** Pass needs all four:
  1. On cases where the annotations agree, the intended reach is a frontier constituent in at least 90%.
  2. The annotations agree on at least 80% of cases.
  3. At most 4 structural candidates in at least 90% of cases.
  4. No case where the single surviving candidate differs from the agreed annotation.
- **Stated scope.** The structural rule defines authoring. In translation a single surviving candidate is a
  recorded claim, not a certified reading of the source.
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
- **Depends on.** SC-E1 passed; **lf-14d** merged (coupled reading sets in Lean); SC-2; and an **approved
  addendum** to the spec (its 9.4), reviewed before this batch is built. The addendum settles:
  - the per-choice `govern` over lf-14d's joint choices;
  - how a frontier reach is validated and fixed: `coveredLayout` cannot call `validateFrontier`, which needs the
    governor; the call would recurse through `fitAt → baseObj → frameOn → coveredLayout` with no `mutual` allowed;
    an unfixed frontier governor records `units = []`;
  - resource uncertainty per choice;
  - graph fitting, if frontier reaches are ever to carry `precedes` or `yields`, and the unary-only rule enforced
    before a frontier reach becomes an internal `fixed` reach;
  - the pins `ruleTyped` and `jointPicks`.
- **In force before the addendum.** A frontier reach carries a unary effect only (`ScopeReach` otherwise,
  `frontier_graph_refused`). A decoder limit met while fitting a candidate leaves the unit unresolved
  (`fitAt_limit`).
- **New files.** `lean/VE/Scope/Frontier.lean`.
- **Shared files touched.** None. lf-14d's coupling functions are called, not edited.

```lean
def frontier (D : SDoc) (u : String) : Except String (List (List String))   -- innermost first; ResourceLimit over 8
inductive Fit | fits | fails | unresolved
def fitOf (D : SDoc) (e : Effect) (us : List String) : Fit   -- fails only if every unit is admitted and e fails at one
def scopeCandidates (D : SDoc) (g : Governor) : List (List String)        -- the frontier minus the failing ones

/-- No heuristic: the frontier depends only on layout and anchors, never on contents, recorded reaches or choices. -/
theorem frontier_no_heuristic (D D₂ : SDoc) (u : String) (hL : D.layout = D₂.layout) (ha : D.anchors = D₂.anchors) :
    frontier D u = frontier D₂ u

theorem scopeCandidates_iff (D : SDoc) (g : Governor) (fs : List (List String)) (hf : frontier D g.unit = .ok fs)
    (us : List String) : us ∈ scopeCandidates D g ↔ us ∈ fs ∧ fitOf D g.effect us ≠ .fails

theorem frontier_accepted (D : SDoc) (g : Governor) (us : List String) (h : validateFrontier D g = .ok us) :
    ∃ fs, frontier D g.unit = .ok fs ∧ us ∈ fs ∧ fitOf D g.effect us = .fits ∧
      ∀ vs ∈ fs, fitOf D g.effect vs ≠ .fails → vs = us

/-- The only remaining candidate is not the only one established to fit: unresolved, never accepted. -/
theorem frontier_unresolved (D : SDoc) (g : Governor) (fs : List (List String)) (hf : frontier D g.unit = .ok fs)
    (h : scopeCandidates D g = [] ∨ ∃ us, scopeCandidates D g = [us] ∧ fitOf D g.effect us = .unresolved) :
    ∃ e, validateFrontier D g = .error e ∧ e.startsWith "UnresolvedScope" = true

theorem frontier_ambiguous (D : SDoc) (g : Governor) (fs : List (List String)) (hf : frontier D g.unit = .ok fs)
    (h : 2 ≤ (scopeCandidates D g).length) :
    ∃ e, validateFrontier D g = .error e ∧ e.startsWith "AmbiguousScope" = true

/-- The reading set's compatible choices are exactly the candidates, one each (lf-14d's joint set). -/
theorem scope_choices (D : SDoc) (g : Governor) (cs : List (List String)) (hc : scopeCandidates D g = cs)
    (hn : 2 ≤ cs.length) (c : VE.Discourse.Choice) :
    c ∈ jointChoices (coupledSets D g) ↔ ∃ i < cs.length, c = choiceAt D g i    -- jointChoices: lf-14d's owner (pinned at spec)
```

**Fixtures:**

| Id | Fixture | Expected |
|---|---|---|
| F13 | u0046.s02 | three candidates (the previous sentence; the ordered list; the section's earlier units) → `AmbiguousScope`; in translation one reading set with three candidates |
| F13′ | synthetic "Rule 4. ... This applies only where the user is an adult." with one fitting candidate | fixed reach |
| F13‴ | an unsupported alternative: two candidates, one established to fit, the other with a unit that is not admitted | both stay live: `AmbiguousScope`, never a unique reach |
| F13⁗ | an unresolved singleton: one candidate remains, and only because one of its units is not admitted | `UnresolvedScope`, no definitive dependent verdict |
| F13″ | a frontier with more than 8 constituents | `ResourceLimit: scope` (UNKNOWN), never a truncated list |
| F13-r | two candidates: one that fits, and one whose composed rule exceeds the decoder's depth limit | both stay live: `AmbiguousScope`, never the fitting candidate as the unique reach; the reach is not fixed, and under the exhausted choice every dependent verdict is UNKNOWN |

- **Bytes.** Upper bound 4,196 B (the 22 restrictive-connective units). Most are co-blocked; 0–300 B expected in
  the next two runs (estimate).

### SC-E2. Experiment: the plain-English presentation (2 h)

- **Question.** Can a reader with no training answer applicability questions from the reviewed presentation
  (1.6)?
- **Runs.** The first run follows SC-2 and tests only the effects built so far. SC-E2 reruns after every batch
  that adds effects or wordings (SC-3b, SC-4, SC-5, SC-7). "Every effect" is judged on the last run.
- **Method.** 20 governed rules: the 7 hard constraints after SC-2 plus 13 synthetic, covering every effect built
  by the run. 40 yes/no questions ("Does rule X forbid Y when Claude only suspects Z?"). Sonnet 5.5 as human proxy
  (the lead's decision of 2026-10-03).
  - Arm A: the source text alone.
  - Arm B: the reviewed presentation with provenance sentences.
- **Pre-registered bar.**
  - Arm B: at least 90% correct.
  - Arm B: names the sentence a condition came from in at least 90%.
  - Arm B is no worse than arm A on any question.
- **What it supports.** Results are labelled "Sonnet proxy, preliminary; assumed upper bound for careful readers,
  not validated against humans". They may justify presentation revisions and report proxy success. "Untrained
  people understand it" is claimed only after a human study. No batch waits for that study.
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
- **Depends on.** english-lean's grammar extension point (the catalogue that owns templates) and SC-1c. SC-7 is
  last in the serialised `lean/VE/EnglishGrammar/*` queue: `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7`.
- **Shared files touched.** The English catalogue's template list, append. Its templates and the F5a fixture are
  rows in english-lean's catalogue.
- **Theorem.**
  - `scope_parseRender`: every accepted governor wording renders back to itself.
  - Its block is the one the parser builds (stated over the catalogue's parse function, pinned at spec).
- **Fixture F5a.** The catalogue parses u0170.s01's wording ("The list of hard constraints above is not a list of
  all the behaviors we think Claude should never exhibit.") to no governor.
- **Exit.** The final SC-E2 run.
- **Bytes.** None on the translations. This batch serves zero-training authoring.

## 6. Dependencies and merge-conflict map

| In-flight or planned item | Branch / worktree | Needed by | How conflicts are avoided |
|---|---|---|---|
| Lean document mode, soft norms, Python switch | lf-16e, lf-16f, lf-16g (`ve-lf-16e`, …) | SC-1b | SC-1b starts after lf-16g merges; until then only new files (SC-1a, SC-3a, SC-2) |
| Lean document-mode call sites | the document-mode queue after lf-16g: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10 | SC-1b | SC-1b's two call sites land in that order |
| Coupled reading sets in Lean | lf-14d (`lean-first/b14d`, `ve-lf-14d`) | SC-5 | called, never edited; SC-5 after it merges and after SC-5's addendum (with its per-choice `govern`) is approved |
| Attitude guard nodes in the chain's norm decoders | attitudes' AT-3a (`design/attitudes`) | u0173.s01's claim (SC-2) | decoded by W1's and soft's norm decoders when `attitudes@0` is on; scope defines no attitude word; SC-2 waits for AT-3a's decoder |
| The seven hard constraints (u0164, u0165.s01–s07, u0173) | the hard-constraint queue `AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5`, then QT-B4 and WG-8 | SC-1b, SC-2 pilot steps | one step at a time; each starts from the translation as the previous step left it |
| Act identity and the split map | act-phrases' AP-3 (`VE.Acts.SplitMap`, `elaborateMap`) | SC-1c provenance rows, SC-4 `rules` reach | read, never re-derived |
| Premise packs and their `origins` | PK-1 (RD-9 composition owner) | SC-1c provenance rows | read, never re-derived |
| Generated audit manifests | AR-1 (`arch-20261010-1`) | every batch | append by hand before AR-1, regenerate after; never both |
| Profile-gate table and mode registry | AR-10 (existing item, scope widened to `Dispatch.lean:417–474`) | SC-1b, SC-1c | the table lands before SC-1b's row; `scope@0` is one row with its composition proof; SC-1c registers in its mode registry; `Protocol.lean` and `service_schema.py` edits join the protocol queue in landing order |
| English catalogue | the `lean/VE/EnglishGrammar/*` queue `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7` | SC-7 | SC-7 is last; its templates and F5a are catalogue rows |
| Typed diagnostic codes | AR-13 | SC-1c onwards | scope's codes join the typed list if merged |
| Per-mode test invalidation | ts-B2 | SC-1c | the new mode's manifest entry is generated |
| Composition S2b; S4 | not in flight | SC-6; none | SC-6 waits for S2b. Scope does not need S4: list names use discourse's `ContentName` type and decoder in scope's own block |
| Weighing, events, quantities, act-phrases | `design/*` | none | conditions may contain their formulas; their meaning stays theirs |
| rd-9, qa-q2, oom-rootcause | in flight | none | no shared file |

Every shared file a batch touches:
- `lean/VE.lean`, `lean/VE/Audit.lean` (SC-1a onwards);
- `tools/layer_policy.py` (SC-1a);
- `lean/VE/Compose/Dispatch.lean` (one row of AR-10's table), the Lean document mode file and the B1 row of
  `tools/bench` (SC-1b);
- `lean/VE/Service/Protocol.lean`, `lean/ResponseShape/Audit.lean`, `ve/backends/service_schema.py`,
  `ve/__main__.py` (SC-1c);
- `lean/VE/Discourse/Access.lean`, `lean/VE/Discourse/WellFormed.lean`, `lean/VE/Route/frozen-sources.sha256`
  (regenerated) and `tools/trust-classes.json` (SC-3a);
- the English catalogue (SC-7).

Generated files are regenerated with `tools/regen_generated.py --write` and never edited or merged by hand:
- the schemas;
- `tools/gate-collection.json`;
- `lean/checkers.lock`;
- Python's profile data, generated from AR-10's table;
- `lean/VE/Route/frozen-sources.sha256`;
- route cases through `tests/route_case_recorder.py`.

## 7. One owner per piece of logic

| Logic | Owner | Scope's use |
|---|---|---|
| Guards, carve-outs, applicability | W1 `VE.Norms.applies`, `anyF` | called by `applyEffect`; its theorems are stated over it |
| Precedence, cycles, same predicate | W1 `VE.Norms.check`, `dependencyOrder` | composed tree checked unchanged |
| Norm object decoding, soft fields | the chain's decoder (`VE.Readings.Wire.decodeNorm`, *pinned at spec*) | lead-in and item joined as JSON, then decoded by it |
| Anchors, content names | discourse (`Anchor`, `ContentName`, their decoders, `anchorsOk`) | read; containment and the anchor checks moved to `VE.Layout` in SC-3a so both call one body |
| Joint choices | lf-14d (Lean) | SC-5 builds its sets through it |
| Rights limitations, bar | rights@0 | SC-6 fills `scope` from a reach |
| Attitude words | attitudes (AT-3a's guard nodes, decoded by the chain's norm decoders) | written inside conditions in the chain's guard wire form; decoded after `own` is substituted |
| Weighing words | weighing | soft fields only |
| Generated rules and predicates, generated names and labels | act-phrases (`VE.Acts.SplitMap`), the packs (`origins`, PK-1) | provenance through the owner's map; never re-derived |
| Profile registration, mode registry | AR-10 | one table row, one registry line |
| Statuses and their order | the Lean document mode | `governorStatus` reads its order |
| Rule English | the existing rule renderer | scope renders only provenance sentences |
| List markers and runs, governance order, provenance wording | **scope** (`VE.Layout.List`, `VE.Scope.*`) | new; nothing else reads list layout across units |

What is deleted:
- **Product code: nothing.** No scope logic exists to delete. SC-3a moves discourse's anchor-containment and
  anchor-check bodies rather than copying them.
- **Pilot data:**
  - the force restated in seven items (SC-1b);
  - the per-rule attitude conjuncts and the notes copying u0173.s01 (SC-2; the shared open term
    `restricted_action_knowing_or_quite_likely` is already gone after AT-0p);
  - the UDHR stand-in term `rights_and_freedoms_set_forth` (SC-6).

## 8. Risks and questions for the review

1. **SC-1b's wait.** It waits for lf-16g. If that slips, the first measured number slips with it. SC-1a, SC-3a
   and SC-2 can proceed meanwhile. Nothing is claimed early.
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
7. **F3's condition does not commute.** F3's `reguard` uses `own` inside an "or", so it does not commute with any
   narrowing. A heading condition over the hard constraints would therefore get `ScopeOrder`. That is acceptable:
   the refusal is explicit, and the author restates the condition once.
8. **Translation fidelity.** In translation an effect, and a single surviving frontier candidate, is a recorded
   claim. Lean checks reach and composition; source fidelity is the pilot audit's (2.1, F5b).

## 9. Shared pieces

These are abstractions several of the seven topics could share. The cross-plan review may move them.

| Shared piece | Who would use it | Proposal |
|---|---|---|
| **Document layout tree**: unit order, paragraphs, list items and depth, headings, anchors, containment | scope (runs, frontier), discourse (`within`, `innermostAnchor`), senses (section-scoped defaults between "whole document" and "one occurrence"), math-evidence (theorem, proof and definition environments; "Let" / "Assume" over a proof), act-phrases (the line between in-sentence and cross-sentence lists) | `VE.Layout`, one owner, read from source bytes; discourse's containment and anchor checks move there in SC-3a |
| **One owner per field** when two units supply parts of one content | scope (lead-in and item), act-phrases (a subject shared by predicates split across units, UDHR u060/u061), rights ("this right includes" lines added to a right), weighing (a later sentence that supplies who may override) | join JSON parts with disjoint keys, then the owner's own decoder; never a mirror type |
| **Reach candidates as one reading set**, coupled to the units they affect | scope (deictic reaches), act-phrases (attachment of modifiers), discourse (pronoun candidates), rights (limitation scope) | one candidate list per choice point, coupled through lf-14d's joint choices, never a product over affected units |
| **Contributor status**: a unit whose meaning lives in other units counts under the weakest of their statuses | scope governors, discourse groups, rights "this right includes", attribution containers | one function in the Lean document mode with `governor_status_weakest`-style theorems |
| **Named sets of rules or units** ("the hard constraints", "the rights and freedoms set forth in this Declaration") | scope (list names), rights (limitation and bar scope), weighing (rank classes: "hard constraints outrank ..."), attitudes (u0173.s01's target) | discourse's `ContentName` type and decoder, with a regenerated membership check |
| **Provenance sentences** in plain English (which sentence contributes which part) | scope, discourse (reviewed presentation), weighing (decision records), attribution (who said it) | one wording table in Lean per owner, one display format in Python |
| **Section-scoped declarations** (definitions, sense defaults, units of measure, assumptions) | senses, quantities ("all amounts in this section are in euros"), math-evidence, discourse names (already anchor-scoped) | an `anchor` reach on a declaration, using the same layout tree |
| **Boundary with phrase grammar** | act-phrases, events | In-sentence coordination, ellipsis and quantifier scope ('every day before') are the phrase grammar's (english-lean's engine and act-phrases). Scope never reads inside a unit, and no other plan assigns sentence-internal scope to scope. |
