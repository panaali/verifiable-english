# Cross-sentence scope (`scope@0`): item-1 specification

> Status: item-1 specification, draft 1, 2026-10-13, design only: no product code, test or generated file changes.
> Written from [scope-PLAN.md](scope-PLAN.md) draft 2, which applies the converged Astra + Fable design debate
> (`manage-agents/debates/design-scope/`, CONVERGED after round 3) and the DRI's cross-plan synthesis edits 1–8 of
> 2026-10-13. It is the statement under the Astra + Opus statement review (Fable arbiter only on disagreement); a
> draft alone opens nothing. Baseline `main` at `49de179e`, read on branch `design/scope` at `3372d8e0`.
> **Checked, not proved.** Every definition and theorem statement in sections 4 and 5 was elaborated by Lean
> v4.24.0 as a scratch stub, `lean/SpecStubs_scope.lean`, against the merged modules it names (`VE.Readings.Wire`,
> `VE.Discourse.{Wire,Access}`, `VE.Finite`, `VE.Attribution.Status`), with `sorry` for every proof; the stub was
> deleted before commit and nothing here is proved. Names that in-flight branches own are typed against `opaque`
> placeholders in a `Pinned` namespace (8.1) and are pinned when each branch merges. **Every fixture value in
> section 7 marked "computed" was produced by `#eval` or `decide` in that stub, not by hand.** Fixtures over the
> pilot layout use the pilot's own bytes for the units involved, shortened only inside sentences (7.0).

## 0. Scope, one paragraph

`scope@0` lets one unit change other units: a list's lead-in completes each item of its list; a heading or a bold
bullet label conditions what lies under it; a later sentence narrows, replaces or carves out the condition of a
named set of rules; a far clause orders rules ("notwithstanding", "subject to"). It is a wrapper at step 1b of the
composition stack, after RESOLVE and before STRUCTURE. GOVERN reads the complete document after RESOLVE, rewrites
the content of each affected unit as plain JSON in the chain's own norm-object form (the lead-in's part joined to
the item's part, conditions substituted, carve-outs appended, precedence names added), and returns the whole
document; the chain's own decoders then read it as if the author had written each rule out in full. So every
effect is meaning the chain already owns (W1's guard, carve-outs and precedence; soft's fields; attitudes' guard
nodes), and scope's proof obligations are about composition only: one owner per field, provenance, order
independence, reaches regenerated from structure, preservation of the whole document, no new symbol, governor
status. A reach the source leaves open is a reading set, never a guess (SC-5, gated). The sections: definitions (1),
English (2), wire (3), Lean definitions (4), theorem statements by batch (5), diagnostics (6), acceptance fixtures
(7), pinned names, limits and files (8), the choices this draft made and the questions for the review (9), the
review checklist (10).

Out of scope, by the plan: anything inside a unit (in-sentence coordination, ellipsis and quantifier scope are the
phrase grammar's: english-lean's engine and act-phrases); what attitude words, weighing words or rights mean
(their owners'); the frontier reach until SC-E1 passes and lf-14d merges; the UDHR rights reach until composition
S2b; any coverage number before a pilot rerun measures it.

## 1. Definitions

### 1.1 Position, input and output

```text
source bytes + front matter
  1  RESOLVE    ve.discourse@1     owns references (unchanged)
  1b GOVERN     scope@0            owns governance: lead-ins, headings, labels, later qualifications, far precedence
  2  STRUCTURE  right-clauses@0    owns line shape (unchanged)
  3  SUPERPOSE  readings@1         owns readings (unchanged)
  4  CHAIN      rights@0 → soft-norms@0 → [norm-defaults@0] → norms@0     owns norm meaning (unchanged)
  5  CHECK      relational-fol@0   frozen route
```

GOVERN's input is an `SDoc` (4.2):

```text
layout     the units as the layout reads them from the source bytes (1.2); never from the wire
doc        the complete document after RESOLVE, as JSON: an object whose "units" array holds each unit's object
           ({"id", "kind", "content", ...}); every other member (reading sets, metadata) is carried, not read,
           except "reading_sets", whose units are refused as governors or governed units (1.5)
block      the "scope" block as written (3)
governors  the decoded governors (1.3)
listNames  the decoded list names: discourse's ContentName, the lead-in whose run it names, the registering unit
anchors    discourse's anchors, decoded by discourse's decoder from the block (SC-3a; 9.2)
re         the chain's decoding environment, VE.Readings.Wire.ReadingsEnvironment (pinned, 8.1)
```

GOVERN's output is the complete document, as JSON: `doc` with the content of each **affected** unit (1.5.4)
replaced by its composed rule, and nothing else changed. With no governor and no `part` content it is `doc` itself,
byte for byte as a value (`govern_identity`), so the chain's ordinary decoding is exactly today's. A document
without `scope@0` never reaches GOVERN (`scope_absent_unchanged`).

### 1.2 Layout: what the source bytes say

The layout is read from the source bytes and each unit's span, never from the wire. For a unit with span `[s, e)`
over the source's UTF-8 bytes `b`:

| Field | Definition |
|---|---|
| line start `ls` | the largest `k ≤ s` with `k = 0` or `b[k-1]` a newline |
| `midLine` | some byte of `[ls, s)` is not a space: the unit begins after other text on its line |
| first text byte `f` | the first byte of `[s, e)` that is not a space (or `e`) |
| marker | at `f`: `* `, `- ` or `+ `, or one or more ASCII digits followed by `. ` |
| `item` | `some d` when the unit is not `midLine`, a marker is at `f`, and the number of spaces `f − ls` is even, with `d = (f − ls) / 2`; else `none`. An odd indentation is not an item |
| `lead` | the last byte of `[s, e)` that is not a space, tab, CR or newline is `:` |
| `label` | an item whose text after the marker is `**`, a nonempty text without a newline, `**`, with `:` just before or just after the closing `**` (`**There’s no operator prompt:**`, `**Process**:`) |
| `para` | the number of blank lines (a newline, then only spaces, tabs or CRs, then a newline) before byte `s` |

Unit ids are distinct (the document loader checks it); the theorems that need it take `(L.map (·.id)).Nodup`.

**List run.** For a lead-in `x`: `x.lead` holds and the next unit is an item of some depth `d`. Its governed items
are the items of depth exactly `d` in the run that follows, where the run continues over every unit that is an item
of depth at least `d` or begins mid-line, and stops at the first other unit (a new paragraph, an item of smaller
depth). Otherwise `NotALeadIn: <unit>`. Deeper items (sub-bullets) and mid-line continuation sentences belong to
the run but are not governed items (fixtures F2, F2′).

**Item units (label reach).** For an item `x` of depth `d` with `x.label`: `x` itself, then every following unit
that is a deeper item or begins mid-line, up to the first other unit. Otherwise `NotALabel: <unit>`.

**Anchors (SC-3a).** Discourse's containment bodies move to `VE.Layout` over `(unit spans, anchors)`: `within`
(the unit's span lies inside the anchor's), `narrower` and `innermostAnchor`. Discourse's three definitions become
one-line calls (`discourse_within_unchanged`, `discourse_innermost_unchanged`). An anchor's units are the layout
units within it, in source order; the first is its **heading**; the anchor reach is the others.

### 1.3 Governors, reaches, effects

A **governor** is `(id, unit, effect, reach, units)`: `unit` is the unit whose words govern, `units` the reach as
recorded, which Lean regenerates and compares (`ManifestMismatch: scope.governors.<id>.units`).

| Reach | Governed units | Batch |
|---|---|---|
| `list <lead>` | the list run's governed items of the lead-in (1.2) | SC-1a |
| `list_name <name>` | the run of the lead-in the name registers; the name's recorded units must equal it | SC-2 |
| `anchor <id>` | the anchor's units after its heading; the governor's unit must be the heading | SC-3a |
| `label <item>` | the item units of 1.2; the governor's unit must be the item | SC-3a |
| `rules [names]` | the rule units whose base rule (1.5.1) has one of the names; an unknown name is `ScopeUnknownRule` | SC-4 |
| `frontier` | the candidates of 1.7 | SC-5 |

| Effect | What it writes (the meaning is the owner's) | Reach allowed | Batch |
|---|---|---|---|
| `frame <part>` | the lead-in's part, joined to each governed item's part with disjoint keys (one owner per field); the governor's unit is the lead-in | `list`, `list_name` | SC-1a |
| `reguard <c>` | the rule's `guard` becomes `c` with `own` replaced by the rule's guard (1.4) | any but `frontier` before SC-5 | SC-2 |
| `carve_out <c>` | one more element of the rule's `unless`, `c` with `own` replaced by the rule's guard | as `reguard` | SC-2 |
| `precedes` | each reached rule on the same predicate joins the governor's own rule's `over` | any | SC-4 |
| `yields` | the governor's own rule's name joins the `over` of each reached rule on the same predicate | any | SC-4 |
| `title` | nothing | `anchor`, `label` | SC-3a |

`frame`, `reguard` and `carve_out` change content; `reguard` and `carve_out` are the **unary** effects;
`precedes` and `yields` are the **graph** effects (1.5.5).

### 1.4 Conditions and `own`

A condition is a guard in the chain's guard wire form (the indexed formula arrays of `VE.Bridge.decodeFormula`,
and any other profile's guard nodes the chain's decoder reads, such as attitudes' AT-3a nodes
`{"attitude": {"holder", "mode", "degree"?, "slot"?, "content"}}`). In a condition, **the JSON string value
`"own"`, at any depth, stands for the governed rule's own guard** ("the relevant restricted category" of each rule).

- **Substitution.** `substOwn g c` replaces every JSON string value `"own"` in `c` by the rule's guard JSON `g`,
  in one pass; object keys are never touched. The result is decoded by the chain's own norm decoder as part of the
  composed rule, so attitude nodes are decoded by AT-3a's hook in the chain's decoders. Scope decodes no condition.
- **Why `"own"` can be reserved.** In the base guard grammar a bare JSON string is never a formula (formulas and
  terms are arrays); it occurs only as a head, a predicate, sort or constant name. So `"own"` at a formula position
  is unambiguous, and the only collision is a vocabulary symbol named `own`: a document whose environment declares
  a sort, predicate or constant `own` and has any condition is refused, `ScopeReserved: own`.
- **No capture.** `own` must not occur under a binder of the base grammar (`["forall", s, a]`, `["exists", s, a]`):
  `ScopeOwnBound: <governor>`. The rule's guard is typed in the rule's situation context, and so is every position
  of `own` (`own_congr`). Inside another profile's node the owner's decoder decides; a rule whose guard is not
  quantifier-free over the base vocabulary gets attitudes' own refusal there, not a scope diagnostic.
- **Depth.** A condition deeper than 64 levels is `ResourceLimit: scope condition depth exceeds 64` (the formula
  decoders' own depth bound; `substOwn`, `hasOwn` and `ownSafe` are total with fuel 64 and complete on admitted
  conditions).
- **Plain narrowing** is the condition `["and", "own", C]` with `C` free of `own`.

### 1.5 Composition

**1.5.1 Base object.** For a unit `u` whose content is a part (`{"part": p}` or `{"cites", "part"}`) or a norm
(`{"norm": o}` or `{"cites", "norm"}`): with no frame governor covering `u`, a norm's base object is `o` and a part
is `ScopeOrphanPart: u`; with exactly one, it is `mergeParts u lead (p or o)`; with two, `ScopeOrder: u: <g1>, <g2>`.
A unit a `frame`, `reguard` or `carve_out` governor covers whose content is written but is neither a part nor a
norm (an assertion before SC-3b, a rights content) is refused, `ScopeNotARule: u`, never skipped
(`nonrule_refused`): a governor never counts a unit it did not change. A unit without content (`null`, the W2
"pending") is never composed: it stays UNFORMALISED, and it makes the governor's status UNFORMALISED (1.6).

**1.5.2 Joining parts.** `mergeParts u lead item`: both must be objects; a key on both sides is
`ScopeConflict: u: <key>` (the first such key in sorted order), never an override; otherwise the union of the
members. The keys are the chain's own norm-object keys; scope keeps no list of them. The joined object is the
chain decoder's to read; a missing key is the decoder's own diagnostic, unchanged (F1″).

**1.5.3 Unary effects and their order.** For each governed unit the unary governors covering it apply to the base
object in the order of the plan's 1.4: by reach class (anchors 0, labels 1, lists and list names 2, rules 3,
frontier 4), then by the position of the governor's unit in the layout (so nested anchors apply outermost first),
stably. Before any composition, every unit with two unary governors whose effects do not `Commutes` is refused,
`ScopeOrder: <unit>: <g1>, <g2>` (`orderCheck`). `Commutes` is syntactic and conservative: true only for two plain
narrowings, a plain narrowing and an own-free carve-out (either order), or two own-free carve-outs. Accepted pairs
commute in meaning (`commute_applies`), so the fixed order decides only the JSON's shape, never a verdict.

**1.5.4 Affected units.** A rule unit is affected when it is a part, a frame covers it, a unary governor covers it,
it is the unit of a `precedes` governor, or a `yields` governor covers it. `govern` changes no other content
(`govern_preserves`); preservation counts a precedence governor's own rule as affected, although that rule is
outside its reach.

**1.5.5 Precedence: the graph step (SC-4).** After the unary effects, the composed objects of the units a graph
governor reads (its own unit and its reach) are decoded by the chain's own decoder (`ruleTable`; a decoder failure
is the decoder's text). For a `precedes` governor with own rule `N` and a reached rule `M` on the same predicate
with another name, `M.name` joins `N`'s `over`; for `yields`, `N.name` joins `M`'s `over`. Reached rules on other
predicates add nothing; a graph governor that adds nothing is `ScopeNoEffect: <governor>`. `addOver` appends only
names not already present (soft refuses a repeated `over` name). W1's same-predicate and acyclicity checks run in
the chain, unchanged. Names are source rule names: act-phrases' elaboration maps "r over a split s" to "r over
every s-a<i>" after GOVERN (1.8).

**1.5.6 Patch and output.** The output is `doc` with its `units` member replaced by the same array in which each
affected unit's `content` member is replaced: a part content becomes `{"norm": o}` (with `cites` kept when
written), a norm content keeps its other members and gets `"norm": o`, where `o` is the composed object with its
edges. Every other unit value is the original value.

**1.5.7 Fault order.** `govern D`: with no governor, the document itself, or `ScopeOrphanPart` for the first part
unit; otherwise `admitBlock` (6.1, in order), `orderCheck`, composition of every affected unit in document order,
`ruleTable`, the `ScopeNoEffect` check in governor order, and (SC-4) the forward declarations; then the patch.

### 1.6 Statuses

| Unit | Status |
|---|---|
| A governed rule unit | the status the chain gives its composed content, unchanged |
| A governor unit **without content** whose effects change content (`frame`, `reguard`, `carve_out`), with meaning `specified` | `governorStatus st us`: the weakest of the statuses `st` of all units its content-changing governors cover, by `VE.Reports.Status.rank` (UNFORMALISED < OPEN < UNKNOWN < LABELLED < CHECKED); UNFORMALISED when the list is empty or a unit has no status. A governed unit that is not admitted is UNFORMALISED, so the governor is too (`governor_status_weakest`, `governor_status_none`) |
| A governor unit without content and with any other meaning | its own status, unchanged: scope never claims a unit the translator marked open or unformalised |
| A governor unit with content (a label item, a `precedes`/`yields` rule) | its own composed content's status: it is a governed or ordinary rule unit |
| A title governor, a list-name registration | the document mode's own status, unchanged: LABELLED when its meaning is `specified` and it has no content, as for discourse's naming clause; reported apart from semantic coverage |
| A forward declaration (SC-4) | `governorStatus` over the later rules it announces |

`st` is the document mode's status of each unit before the fold (no fixpoint). Governor and governed bytes are each
counted once, under their own spans.

### 1.7 Ambiguity: frontier reaches (SC-5; after SC-E1 and lf-14d)

**Frontier.** For a governor on unit `u`, its constituents, innermost first, without repeats or empty ones:
1. the unit before `u`;
2. that unit's paragraph, up to it (units with its `para`);
3. the last list before `u` in `u`'s innermost anchor: the last item unit's depth and the items of that depth in
   the run that ends with it (no lead-in needed);
4. for each anchor enclosing `u`, innermost first, its units before `u` (the heading excluded).

More than 8 constituents is `ResourceLimit: scope`: UNKNOWN for every dependent verdict, never a truncated list,
never a rejection, never a chosen reach (`frontier_limit_iff`). The frontier reads only layout and anchors
(`frontier_no_heuristic`).

**Three-valued fit.** At one unit, `fitAt` is `none` when the unit is not admitted (no base rule the chain's decoder
reads), else whether the effect applies and the composed rule is typed by the chain's own rule check (pinned at
SC-5's addendum, 8.1). A candidate **fails** only when every unit is admitted and the effect fails at one; it
**fits** when every unit fits; otherwise it is **unresolved** (`fitOf_fails_iff`). Live candidates are those that
do not fail.

**Validation.**
- no live candidate: `UnresolvedScope: <g>: no candidate fits`; the governor stays UNFORMALISED;
- one live candidate that fits: the reach is fixed (`frontier_accepted`). In authoring the structural rule defines
  the reading; in translation a single surviving candidate is a recorded claim, not a certified reading;
- one live candidate that is unresolved: it is the only remaining candidate, not the only one established to fit:
  `UnresolvedScope: <g>: a unit of its only candidate is not admitted`, with no definitive dependent verdict
  (`frontier_unresolved`);
- two or more: `AmbiguousScope: <g>: <candidates>` (`frontier_ambiguous`). In authoring the IDE asks one question;
  in translation the live candidates become one reading set on the governor, coupled to every affected unit
  through lf-14d's joint choices: one choice among at most 8 candidates, never a product over the affected units.
  An unsupported candidate stays live: unsupported content never resolves ambiguity.

**Per choice.** `governAt D pick` is `govern` on `D` with each frontier governor's reach fixed to the candidate the
joint choice picks (a `fixed` reach, never on the wire). Every theorem of SC-1a holds per choice
(`governAt_preserves`), owner-generated declarations and premises are kept with their provenance per choice, and
with no frontier governor `governAt D pick = govern D` (`governAt_no_frontier`). The choices of reach the joint set
admits are exactly the live candidates (`scope_choices`, stated over lf-14d's set, pinned).

### 1.8 Generated symbols and provenance

GOVERN writes JSON before any owner's decoder runs, so every symbol an owner generates (act-phrases' `<rule>-a<i>`
and `p__i`, a pack's generated names and labels) is generated downstream from the composed content, by its owner,
and kept. Scope introduces no symbol: every string value of GOVERN's output is a string value of the document or of
the block (`govern_no_new_symbols`). For provenance, scope reads the owner's exported map and never re-derives a
split or a key: for act-phrases `VE.Acts.SplitMap.rules` (AP-3), for the packs their `origins` (PK-1). The explain
route lists a generated rule under its source unit and names its source rule (`explain_generated`).

### 1.9 Forward declarations (SC-4)

"Rule r has exceptions stated later in this section." is recorded as `(unit w, rule r, anchor a)` and checked: some
unit of `a` after `w` has a base rule whose `over` names `r` (`forward_exception_sound`, and its converse
`forward_exception_complete`); otherwise `ScopeForward: <w>: rule <r> has no later exception in <a>`. A forward
announcement whose exceptions the source never identifies is not recorded: the unit stays UNFORMALISED with the
residual `UnresolvedScope` (F12), never a guessed edge.

## 2. English

### 2.1 Translation: what a translator records

| Source wording | Recorded as |
|---|---|
| "Claude should never:" + bullets | `frame` over the `list` reach; each item's content a `part` |
| "The current hard constraints ... are as follows." | a list name over the next lead-in's run |
| "... are centrally meant to apply to cases where ..." | `reguard` over the list name, its attitude words written as attitudes' guard nodes and `own` |
| "Regardless of operator instructions, Claude should by default:" + bullets | `frame` whose part carries the soft fields, which weighing and soft own |
| "Notwithstanding <rules or section>", "Subject to <rules or section>" | `precedes` / `yields` over `rules` or `anchor` |
| a heading or bullet label that is a full clause ("There's no operator prompt:") | `reguard` (plain narrowing) over `anchor` or `label` |
| a noun heading ("Hard constraints") | `title` |
| "Rule n has exceptions stated later in this section." | a forward declaration (1.9) |

A wording whose reach the source leaves open is a reading set (1.7). A wording that states something *about* a
list without changing its rules (u0170.s01, "The list of hard constraints above is not a list of all the behaviors
we think Claude should never exhibit.") is not a governor. Two checks refuse to read it as one: the shared English
catalogue parses that wording to no governor (F5a, SC-7), and the pilot audit flags any governor recorded on
u0170.s01 (F5b). Lean sees the layout and the recorded content, not the wording: **in translation an effect is a
recorded claim**; Lean checks its reach and how it composes, not that the sentence says it, and source fidelity is
reviewed outside Lean, by the pilot audit.

### 2.2 Authoring wordings (SC-7, last)

Each wording has one reading; the IDE shows the paraphrase and writes the block from the English. The templates are
rows in english-lean's catalogue (the one grammar owner); scope adds no grammar of its own.

| Wording | Block | The one reading (IDE paraphrase) |
|---|---|---|
| `Every instance of Claude must not:` followed by a bulleted list | `frame` over `list` | "Each item below is its own rule: ‘Every instance of Claude must not <item>.’" Each item must complete the sentence |
| `The rules below are called the hard constraints.` | list name | "‘The hard constraints’ names the rules of the list that follows." |
| `The hard constraints apply only where <condition>.` | `reguard ["and", "own", C]` over `list_name` | "Each of the 7 rules called ‘the hard constraints’ applies only where <condition>." |
| `The hard constraints apply only where Claude knows that the act is of its kind, or thinks it quite likely that it is.` | `reguard` with attitude nodes and `own` | "‘Its kind’ is each rule's own act." (`own`; the attitude words are attitudes') |
| `The hard constraints do not apply when <condition>.` | `carve_out` over `list_name` | "None of the 7 rules applies when <condition>; then the other rules and the default decide." |
| `Rule 9 takes precedence over the rules of section 3.` | `precedes` over `anchor` | "Where rule 9 and a rule of section 3 regulate the same act, rule 9 decides." |
| `## When there is no operator prompt` (a heading that is a full `When`/`If` clause) | `reguard ["and", "own", C]` over `anchor` | "Every rule in this section applies only when there is no operator prompt." |
| any other heading | `title` | "A title: it changes no rule." |
| `This applies only where <condition>.` after a rule or list (SC-5) | `reguard` over `frontier` | one candidate established to fit: "This qualifies <the rule above / the list above>"; otherwise a question |

### 2.3 Provenance sentences (`VE/Scope/English.lean`, SC-1c)

The reviewed presentation shows each governed rule written out in full by the existing rule renderer (one owner),
then one sentence per contributing governor, under the heading *Where the parts come from:*. Lean owns the table;
Python prints it; SC-E2 may change the wording, never the semantics.

| Contributor | Sentence |
|---|---|
| `frame` | The start of this rule comes from the line above the list, "<text>". |
| `reguard` | Its condition comes from <where>, "<text>", which covers <cover>. |
| `carve_out` | Its exception comes from <where>, "<text>", which covers <cover>. |
| `precedes` (own rule) | It takes precedence over <names>; this comes from "<text>". |
| `yields` (reached rule) | <name> takes precedence over it; this comes from <where>, "<text>". |
| a generated rule | This rule is part <i> of rule <source>. — then the source rule's sentences |

- `<text>`: the governor unit's source text, its first 12 words, then "…" when longer.
- `<where>`: "the line above the list" (a list reach whose lead-in is the governor), "the heading of this section"
  (anchor), "the label of this item" (label), "a later sentence" or "an earlier sentence" (by layout position).
- `<cover>`: "all <n> items of this list" for a list or list-name reach of the item's own list, else "<n> rules".
- Unit ids, arrows and brackets appear only in the provenance view.

The plan's example reads, in these templates: *Where the parts come from:* The start of this rule comes from the
line above the list, "Claude should never:". Its condition comes from a later sentence, "Hard constraints are
centrally meant to apply to cases where Claude would either be knowingly …", which covers all 7 items of this list.

## 3. Wire

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

Item unit content: `{"part": {"name": "hc-cbrn-uplift", "predicate": "…", "guard": [...]}}`.

| Member | Form | Notes |
|---|---|---|
| `version` | `"scope@0"` | required |
| `list_names` | array of `{"name", "units", "scope", "lead", "unit"}` | optional; `lead` and `unit` are read by scope, the rest is passed to `VE.Discourse.Wire.decodeContentName` unchanged |
| `anchors` | array of discourse anchor objects | optional (SC-3a); decoded by `VE.Discourse.Wire.decodeAnchor` and checked by discourse's anchor checks (9.2) |
| `forward` | array of `{"unit", "rule", "anchor"}` | optional (SC-4) |
| `governors` | array of `{"id", "unit", "reach", "effect", "units"}` | `units` absent only for a frontier reach |
| `reach` | `{"list": id}`, `{"list_name": name}`, `{"anchor": id}`, `{"label": id}`, `{"rules": [names]}`, or `"frontier"` | |
| `effect` | `{"frame": object}`, `{"reguard": condition}`, `{"carve_out": condition}`, or `"precedes"`, `"yields"`, `"title"` | |

Wire rules:
- Every id is a token of the existing grammar. Optional members are absent, never `null`; an unknown member is
  `InvalidInput: scope@0 unknown member <path>`.
- Reaches and list-name units are recorded, then regenerated and compared: a mismatch is
  `ManifestMismatch: scope.<path>`.
- The block is inside the document identity, like discourse's.
- The `part` and `frame` keys are the chain's own norm-object keys. Scope keeps no list of its own. W1's `sign` is
  a Boolean; the frame's keys for F1 are pinned in 7.1.
- Without `scope@0` the block is refused as unknown front matter, and a `part` content decodes as pending
  (`VE.Readings.Wire.decodeContent` returns `.pending` for an unknown key): UNFORMALISED (F1-off).

## 4. Lean definitions

New files (plan 4): `lean/VE/Layout/{List,Anchors}.lean`, `lean/VE/Scope/{Wire,Govern,Effects,Frontier,English,Run,
Theorems,Examples}.lean`, `lean/SCOPE.md`. No `mutual`, no primed theorem names, no `native_decide`, no `partial`;
JSON recursion is by fuel 64 (1.4). The definitions below are the stub's, verbatim apart from shortened doc
comments and the `-- SC-5` remark in `coveredLayout`.

### 4.1 `VE.Layout`

```lean
namespace VE.Layout

structure Unit where
  id : String
  span : Nat × Nat
  item : Option Nat      -- some d: the unit begins a list item at depth d
  midLine : Bool         -- some non-space byte precedes the unit on its line
  lead : Bool            -- its last byte that is not a space, tab, CR or LF is ":"
  label : Bool           -- it begins a list item whose text after the marker opens with a bold label ending in ":"
  para : Nat             -- the number of blank lines before the unit's first byte
  deriving DecidableEq, Repr

def sp : UInt8 := 32
def nl : UInt8 := 10
def isBlank (c : UInt8) : Bool := c == 32 || c == 9 || c == 10 || c == 13

def lineStart (b : ByteArray) : Nat → Nat
  | 0 => 0
  | k + 1 => if b.get! k == nl then k + 1 else lineStart b k

def spacesOnly (b : ByteArray) (i j : Nat) : Bool :=
  (List.range (j - i)).all (fun k => b.get! (i + k) == sp)

def skipSpaces (b : ByteArray) (i e : Nat) : Nat :=
  (((List.range (e - i)).find? (fun k => b.get! (i + k) != sp)).map (i + ·)).getD e

def isDigit (c : UInt8) : Bool := 48 ≤ c && c ≤ 57

def markerLen (b : ByteArray) (f e : Nat) : Option Nat :=
  let c := b.get! f
  if f + 1 < e && (c == 42 || c == 45 || c == 43) && b.get! (f + 1) == sp then some 2
  else
    let n := ((List.range (e - f)).find? (fun k => !isDigit (b.get! (f + k)))).getD (e - f)
    if 0 < n && f + n + 1 < e && b.get! (f + n) == 46 && b.get! (f + n + 1) == sp then some (n + 2) else none

def lastNonBlank (b : ByteArray) (s e : Nat) : Option UInt8 :=
  ((List.range (e - s)).reverse.find? (fun k => !isBlank (b.get! (s + k)))).map (fun k => b.get! (s + k))

def boldLabel (b : ByteArray) (p e : Nat) : Bool :=
  p + 1 < e && b.get! p == 42 && b.get! (p + 1) == 42 &&
  match (List.range (e - (p + 2))).find? (fun k => b.get! (p + 2 + k) == nl ||
      (b.get! (p + 2 + k) == 42 && p + 3 + k < e && b.get! (p + 3 + k) == 42)) with
  | some k => b.get! (p + 2 + k) == 42 && 0 < k &&
      (b.get! (p + 1 + k) == 58 || (p + 4 + k < e && b.get! (p + 4 + k) == 58))
  | none => false

def blankLinesBefore (b : ByteArray) (s : Nat) : Nat :=
  ((List.range s).filter (fun k => b.get! k == nl &&
    let j := ((List.range (s - (k + 1))).find? (fun i => !(b.get! (k + 1 + i) == sp ||
      b.get! (k + 1 + i) == 9 || b.get! (k + 1 + i) == 13))).map (k + 1 + ·)
    match j with
    | some j => b.get! j == nl
    | none => false)).length

def ofSource (prose : String) (units : List (String × Nat × Nat)) : List Unit :=
  let b := prose.toUTF8
  units.map fun (id, s, e) =>
    let ls := lineStart b s
    let f := skipSpaces b s e
    let mid := !spacesOnly b ls s
    let m := if mid then none else markerLen b f e
    let item := match m with
      | some _ => if (f - ls) % 2 == 0 then some ((f - ls) / 2) else none
      | none => none
    let label := match item, m with
      | some _, some k => boldLabel b (f + k) e
      | _, _ => false
    { id, span := (s, e), item, midLine := mid, lead := lastNonBlank b s e == some 58, label,
      para := blankLinesBefore b s }

def indexOf (L : List Unit) (u : String) : Option Nat := L.findIdx? (·.id == u)

def continues (d : Nat) (x : Unit) : Bool := x.item.any (d ≤ ·) || x.midLine

def runFrom (d : Nat) : List Unit → List String
  | [] => []
  | x :: xs => if continues d x then (if x.item == some d then x.id :: runFrom d xs else runFrom d xs) else []

def listRun (L : List Unit) (lead : String) : Except String (List String) :=
  match indexOf L lead with
  | none => .error s!"ScopeUnknownUnit: {lead}"
  | some i =>
    match L[i]?, L[i + 1]? with
    | some x, some y =>
      if x.lead then
        match y.item with
        | some d => .ok (runFrom d (L.drop (i + 1)))
        | none => .error s!"NotALeadIn: {lead}"
      else .error s!"NotALeadIn: {lead}"
    | _, _ => .error s!"NotALeadIn: {lead}"

def itemFrom (d : Nat) : List Unit → List String
  | [] => []
  | x :: xs => if x.item.any (d < ·) || x.midLine then x.id :: itemFrom d xs else []

def itemRun (L : List Unit) (item : String) : Except String (List String) :=
  match indexOf L item with
  | none => .error s!"ScopeUnknownUnit: {item}"
  | some i =>
    match L[i]? with
    | some x =>
      match x.item with
      | some d => if x.label then .ok (x.id :: itemFrom d (L.drop (i + 1))) else .error s!"NotALabel: {item}"
      | none => .error s!"NotALabel: {item}"
    | none => .error s!"ScopeUnknownUnit: {item}"

/-- Independent statement of a governed item (SC-1a). -/
def GovernedItem (L : List Unit) (lead u : String) : Prop :=
  ∃ (i j d : Nat), (L[i]?).map (·.id) = some lead ∧ (L[i]?).map (·.lead) = some true ∧
    (L[i+1]?).bind (·.item) = some d ∧ i < j ∧ (L[j]?).map (·.id) = some u ∧ (L[j]?).bind (·.item) = some d ∧
    ∀ k, i < k → k < j → ∃ x, L[k]? = some x ∧ ((∃ e, x.item = some e ∧ d ≤ e) ∨ x.midLine = true)

/-- Independent statement of an item's units (SC-3a). -/
def ItemUnit (L : List Unit) (item u : String) : Prop :=
  ∃ (i d : Nat), (L[i]?).map (·.id) = some item ∧ (L[i]?).bind (·.item) = some d ∧
    (L[i]?).map (·.label) = some true ∧
    (u = item ∨ ∃ (j : Nat), i < j ∧ (L[j]?).map (·.id) = some u ∧
      ∀ k, i < k → k ≤ j → ∃ x, L[k]? = some x ∧ ((∃ e, x.item = some e ∧ d < e) ∨ x.midLine = true))

/-! Anchors (SC-3a): discourse's containment bodies, moved; discourse's three definitions call these. -/

def spansOf (L : List Unit) : List (String × Nat × Nat) := L.map fun x => (x.id, x.span.1, x.span.2)

def within (spans : List (String × Nat × Nat)) (anchors : List VE.Discourse.Anchor) (unit anchor : String) : Bool :=
  match (spans.find? (·.1 == unit)).map (fun k => (k.2.1, k.2.2)), anchors.find? (·.id == anchor) with
  | some (b, e), some a => a.span.1 ≤ b && e ≤ a.span.2
  | _, _ => false

def narrower (best : Option VE.Discourse.Anchor) (a : VE.Discourse.Anchor) : Option VE.Discourse.Anchor :=
  match best with
  | none => some a
  | some b => if a.span.2 - a.span.1 < b.span.2 - b.span.1 then some a else some b

def innermostAnchor (spans : List (String × Nat × Nat)) (anchors : List VE.Discourse.Anchor) (unit : String) :
    Option VE.Discourse.Anchor :=
  (anchors.filter fun a => within spans anchors unit a.id).foldl narrower none

def anchorUnits (L : List Unit) (anchors : List VE.Discourse.Anchor) (a : String) : List String :=
  (L.filter fun x => within (spansOf L) anchors x.id a).map (·.id)

def headingOf (L : List Unit) (anchors : List VE.Discourse.Anchor) (a : String) : Option String :=
  (anchorUnits L anchors a).head?

def anchorReach (L : List Unit) (anchors : List VE.Discourse.Anchor) (a : String) : Except String (List String) :=
  match anchorUnits L anchors a with
  | [] => .error s!"ScopeUnknownAnchor: {a}"
  | _ :: us => .ok us

end VE.Layout
```

### 4.2 `VE.Scope`

```lean
namespace VE.Scope
open Lean
open VE.SoftNorms (SoftNode)

def depthLimit : Nat := 64

inductive Effect
  | frame (part : Json)
  | reguard (c : Json)
  | carveOut (c : Json)
  | precedes
  | yields
  | title

inductive Reach
  | list (lead : String)
  | listName (name : String)
  | anchor (id : String)
  | label (item : String)
  | rules (names : List String)
  | frontier
  | fixed (units : List String)   -- never on the wire: a frontier reach fixed by one joint choice (SC-5)

structure Governor where
  id : String
  unit : String
  effect : Effect
  reach : Reach
  units : List String       -- the recorded reach, regenerated and compared; empty for a frontier reach

structure SDoc where
  layout : List VE.Layout.Unit
  doc : Json                -- the document as written after RESOLVE: `{"units": [...], ...}`
  block : Json              -- the `scope` block as written
  governors : List Governor
  listNames : List (VE.Discourse.ContentName × String × String)   -- name, its lead-in, its registering unit
  anchors : List VE.Discourse.Anchor
  re : VE.Readings.Wire.ReadingsEnvironment

/-! JSON access (read only; scope decodes no rule field itself) -/

def members (j : Json) : List (String × Json) := (VE.Bridge.fields j).toOption.getD []
def keysOf (j : Json) : List String := (members j).map (·.1)
def unitsOf (doc : Json) : List Json := match doc.getObjValD "units" with
  | .arr xs => xs.toList
  | _ => []
def idOf (u : Json) : String := (u.getObjValD "id").getStr?.toOption.getD ""
def unitIds (doc : Json) : List String := (unitsOf doc).map idOf
def contentOf (doc : Json) (u : String) : Json :=
  (((unitsOf doc).find? (idOf · == u)).map (·.getObjValD "content")).getD .null
def isPart (c : Json) : Bool := keysOf c == ["part"] || keysOf c == ["cites", "part"]
def isNorm (c : Json) : Bool := keysOf c == ["norm"] || keysOf c == ["cites", "norm"]
def objectOf (c : Json) : Json := if isPart c then c.getObjValD "part" else c.getObjValD "norm"
def normOf (c : Json) : Option Json := (c.getObjVal? "norm").toOption
def partUnits (D : SDoc) : List String := (unitIds D.doc).filter (fun u => isPart (contentOf D.doc u))
def ruleUnits (D : SDoc) : List String :=
  (unitIds D.doc).filter (fun u => isPart (contentOf D.doc u) || isNorm (contentOf D.doc u))
def setUnits (doc : Json) : List String := match doc.getObjValD "reading_sets" with
  | .arr xs => xs.toList.map (fun s => (s.getObjValD "unit").getStr?.toOption.getD "")
  | _ => []

/-! Conditions and `own` -/

def hasOwn : Nat → Json → Bool
  | 0, _ => false
  | n + 1, j => match j with
    | .str s => s == "own"
    | .arr xs => xs.toList.any (hasOwn n)
    | .obj _ => (members j).any (fun kv => hasOwn n kv.2)
    | _ => false

def depthOk : Nat → Json → Bool
  | 0, _ => false
  | n + 1, j => match j with
    | .arr xs => xs.toList.all (depthOk n)
    | .obj _ => (members j).all (fun kv => depthOk n kv.2)
    | _ => true

/-- `own` occurs under no binder of the base guard grammar. -/
def ownSafe : Nat → Json → Bool
  | 0, _ => true
  | n + 1, j => match j with
    | .arr xs => match xs.toList with
      | [.str "forall", _, a] => !hasOwn n a
      | [.str "exists", _, a] => !hasOwn n a
      | ys => ys.all (ownSafe n)
    | .obj _ => (members j).all (fun kv => ownSafe n kv.2)
    | _ => true

/-- Every JSON string value `"own"` in `c`, at any depth, replaced by `g`. -/
def substOwn (g : Json) : Nat → Json → Json
  | 0, j => j
  | n + 1, j => match j with
    | .str s => if s == "own" then g else j
    | .arr xs => .arr (xs.map (substOwn g n))
    | .obj kvs => .obj (kvs.map fun _ v => substOwn g n v)
    | _ => j

def narrowing (c : Json) : Option Json := match c with
  | .arr #[.str "and", .str "own", C] => if hasOwn depthLimit C then none else some C
  | _ => none

def Commutes : Effect → Effect → Bool
  | .reguard c₁, .reguard c₂ => (narrowing c₁).isSome && (narrowing c₂).isSome
  | .reguard c, .carveOut d => (narrowing c).isSome && !hasOwn depthLimit d
  | .carveOut d, .reguard c => (narrowing c).isSome && !hasOwn depthLimit d
  | .carveOut d₁, .carveOut d₂ => !hasOwn depthLimit d₁ && !hasOwn depthLimit d₂
  | _, _ => false

/-! Joining parts and applying effects (on the rule's JSON object) -/

def mergeParts (u : String) (lead item : Json) : Except String Json := do
  let bad := s!"InvalidInput: scope@0 parts of {u} must be objects"
  let ls ← (VE.Bridge.fields lead).mapError (fun _ => bad)
  let is ← (VE.Bridge.fields item).mapError (fun _ => bad)
  match ls.find? (fun kv => is.any (·.1 == kv.1)) with
  | some (k, _) => throw s!"ScopeConflict: {u}: {k}"
  | none => pure (Json.mkObj (ls ++ is))

def applyEffect (u : String) : Effect → Json → Except String Json
  | .reguard c, o => match o.getObjVal? "guard" with
    | .ok g => pure (o.setObjVal! "guard" (substOwn g depthLimit c))
    | .error _ => throw s!"ScopeNotARule: {u}"
  | .carveOut c, o => match o.getObjVal? "guard", o.getObjVal? "unless" with
    | .ok g, .ok (.arr xs) => pure (o.setObjVal! "unless" (.arr (xs.push (substOwn g depthLimit c))))
    | _, _ => throw s!"ScopeNotARule: {u}"
  | _, o => pure o

/-- An item's rule as the chain reads it (the explain route). -/
def itemRule (D : SDoc) (u : String) (lead item : Json) : Except String SoftNode :=
  do VE.Readings.Wire.decodeNorm D.re (← mergeParts u lead item)

/-! Reaches -/

def isFrame : Effect → Bool | .frame _ => true | _ => false
def unary : Effect → Bool | .reguard _ | .carveOut _ => true | _ => false
def graph : Effect → Bool | .precedes | .yields => true | _ => false

def coveredLayout (D : SDoc) : Reach → Except String (List String)
  | .list lead => VE.Layout.listRun D.layout lead
  | .listName n => match D.listNames.find? (·.1.name == n) with
    | some (cn, lead, _) => do
      let us ← VE.Layout.listRun D.layout lead
      if cn.units == us then pure us else throw s!"ManifestMismatch: scope.list_names.{n}.units"
    | none => throw s!"ScopeUnknownName: {n}"
  | .anchor a => VE.Layout.anchorReach D.layout D.anchors a
  | .label i => VE.Layout.itemRun D.layout i
  | .rules _ => .ok []
  | .frontier => throw "UnsupportedProfile: scope@0 frontier reach requires SC-5"   -- SC-5: validateFrontier
  | .fixed us => .ok us

def frameOn (D : SDoc) (u : String) : List Governor :=
  D.governors.filter (fun g => isFrame g.effect && ((coveredLayout D g.reach).toOption.getD []).contains u)

def baseObj (D : SDoc) (u : String) : Except String Json :=
  let c := contentOf D.doc u
  if !(isPart c || isNorm c) then .error s!"ScopeNotARule: {u}" else
  match frameOn D u with
  | [] => if isPart c then .error s!"ScopeOrphanPart: {u}" else .ok (objectOf c)
  | [g] => match g.effect with
    | .frame lead => mergeParts u lead (objectOf c)
    | _ => .ok (objectOf c)
  | g₁ :: g₂ :: _ => .error s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def baseName (D : SDoc) (u : String) : Option String :=
  ((baseObj D u).toOption.bind fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption).map (·.name)

def covered (D : SDoc) : Reach → Except String (List String)
  | .rules ns => do
    for n in ns do
      unless (ruleUnits D).any (fun u => baseName D u == some n) do throw s!"ScopeUnknownRule: {n}"
    pure ((ruleUnits D).filter (fun u => (baseName D u).any ns.contains))
  | r => coveredLayout D r

/-! Order (plan 1.4) -/

def classOf : Reach → Nat
  | .anchor _ => 0 | .label _ => 1 | .list _ => 2 | .listName _ => 2 | .rules _ => 3 | .frontier => 4
  | .fixed _ => 4

def position (D : SDoc) (u : String) : Nat := (VE.Layout.indexOf D.layout u).getD D.layout.length

def ordered (D : SDoc) : List Governor :=
  D.governors.mergeSort (fun g h => classOf g.reach < classOf h.reach ||
    (classOf g.reach == classOf h.reach && position D g.unit ≤ position D h.unit))

def coversU (D : SDoc) (g : Governor) (u : String) : Bool := ((covered D g.reach).toOption.getD []).contains u

def governorsOf (D : SDoc) (u : String) : List Governor := (ordered D).filter (fun g => unary g.effect && coversU D g u)

def composed (D : SDoc) (u : String) : Except String Json := do
  (governorsOf D u).foldlM (fun o g => applyEffect u g.effect o) (← baseObj D u)

def orderCheck (D : SDoc) : Except String Unit := do
  for u in unitIds D.doc do
    let gs := governorsOf D u
    for g₁ in gs do
      for g₂ in gs do
        if g₁.id != g₂.id && !Commutes g₁.effect g₂.effect then throw s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def affected (D : SDoc) : List String :=
  (ruleUnits D).filter fun u =>
    isPart (contentOf D.doc u) || !(frameOn D u).isEmpty || !(governorsOf D u).isEmpty ||
    D.governors.any (fun g => match g.effect with
      | .precedes => g.unit == u
      | .yields => coversU D g u
      | _ => false)

/-! Precedence: the graph step over the composed rules (SC-4) -/

def edgesOf (D : SDoc) (rule : String → Option SoftNode) (g : Governor) : List (String × String) :=
  let targets := (covered D g.reach).toOption.getD []
  match rule g.unit with
  | none => []
  | some N => match g.effect with
    | .precedes => targets.filterMap fun v => (rule v).bind fun M =>
        if M.pred == N.pred && M.name != N.name then some (g.unit, M.name) else none
    | .yields => targets.filterMap fun v => (rule v).bind fun M =>
        if M.pred == N.pred && M.name != N.name then some (v, N.name) else none
    | _ => []

def edgesInto (D : SDoc) (rule : String → Option SoftNode) (u : String) : List String :=
  (((ordered D).filter (graph ·.effect)).flatMap (edgesOf D rule)).filterMap fun (w, n) => if w == u then some n else none

def ruleTable (D : SDoc) : Except String (List (String × SoftNode)) := do
  let gs := (ordered D).filter (graph ·.effect)
  let needed := (ruleUnits D).filter (fun u => gs.any (fun g => g.unit == u || coversU D g u))
  needed.mapM (fun u => do pure (u, ← VE.Readings.Wire.decodeNorm D.re (← composed D u)))

def edgesFor (D : SDoc) (u : String) : Except String (List String) := do
  let t ← ruleTable D
  pure (edgesInto D (fun v => t.lookup v) u)

def addOver (names : List String) (o : Json) : Json :=
  match o.getObjVal? "over" with
  | .ok (.arr xs) =>
    let old := xs.toList.filterMap (·.getStr?.toOption)
    let fresh := names.foldl (fun acc n => if old.contains n || acc.contains n then acc else acc ++ [n]) []
    if fresh.isEmpty then o else o.setObjVal! "over" (.arr (xs ++ (fresh.map Json.str).toArray))
  | _ => o

/-! The block's admission and `govern` -/

def conditions : Effect → List Json
  | .reguard c => [c]
  | .carveOut c => [c]
  | _ => []

def vocabularyNames (D : SDoc) : List String :=
  let v := D.re.se.ne.rv.vocabulary
  v.sorts ++ v.predicates.map (·.1) ++ v.constants.map (·.1)

def firstDup : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else firstDup xs

def admitBlock (D : SDoc) : Except String Unit := do
  if D.governors.length > 256 then throw "ResourceLimit: scope governors"
  if let some i := firstDup (D.governors.map (·.id)) then throw s!"DuplicateDeclaration: governor {i}"
  if let some n := firstDup (D.listNames.map (·.1.name)) then throw s!"DuplicateDeclaration: list name {n}"
  for g in D.governors do
    unless (unitIds D.doc).contains g.unit do throw s!"ScopeUnknownUnit: {g.unit}"
  if D.governors.any (fun g => !(conditions g.effect).isEmpty) && (vocabularyNames D).contains "own" then
    throw "ScopeReserved: own"
  for (cn, lead, unit) in D.listNames do
    unless (unitIds D.doc).contains unit do throw s!"ScopeUnknownUnit: {unit}"
    let us ← VE.Layout.listRun D.layout lead
    unless cn.units == us do throw s!"ManifestMismatch: scope.list_names.{cn.name}.units"
  for g in D.governors do
    for c in conditions g.effect do
      unless depthOk depthLimit c do throw "ResourceLimit: scope condition depth exceeds 64"
      unless ownSafe depthLimit c do throw s!"ScopeOwnBound: {g.id}"
    match g.effect, g.reach with
    | .frame _, .list lead =>
      unless lead == g.unit do throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .frame _, .listName n =>
      unless (D.listNames.find? (·.1.name == n)).any (·.2.1 == g.unit) do
        throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .frame _, _ => throw s!"ScopeReach: {g.id}"
    | .title, .anchor _ => pure ()
    | .title, .label _ => pure ()
    | .title, _ => throw s!"ScopeReach: {g.id}"
    | _, _ => pure ()
    match g.reach with
    | .anchor a =>
      unless VE.Layout.headingOf D.layout D.anchors a == some g.unit do
        throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .label i => unless i == g.unit do throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | _ => pure ()
    let us ← covered D g.reach
    unless us == g.units do throw s!"ManifestMismatch: scope.governors.{g.id}.units"
    for u in g.unit :: us do
      if (setUnits D.doc).contains u then throw s!"ScopeReadings: {u}"
    if isFrame g.effect || unary g.effect then
      for u in us do
        let c := contentOf D.doc u
        unless c == .null || isPart c || isNorm c do throw s!"ScopeNotARule: {u}"

def newContent (c o : Json) : Json :=
  if isPart c then Json.mkObj ((members c).filter (·.1 != "part") ++ [("norm", o)]) else c.setObjVal! "norm" o

def patch (D : SDoc) (comp : List (String × Json)) : Json :=
  D.doc.setObjVal! "units" (.arr ((unitsOf D.doc).map fun u =>
    match comp.lookup (idOf u) with
    | some o => u.setObjVal! "content" (newContent (u.getObjValD "content") o)
    | none => u).toArray)

def govern (D : SDoc) : Except String Json :=
  if D.governors.isEmpty then
    match partUnits D with
    | [] => .ok D.doc
    | u :: _ => .error s!"ScopeOrphanPart: {u}"
  else do
    admitBlock D
    orderCheck D
    let comp ← (affected D).mapM (fun u => do pure (u, ← composed D u))
    let t ← ruleTable D
    for g in (ordered D).filter (graph ·.effect) do
      if (edgesOf D (fun v => t.lookup v) g).isEmpty then throw s!"ScopeNoEffect: {g.id}"
    pure (patch D (comp.map fun (u, o) => (u, addOver (edgesInto D (fun v => t.lookup v) u) o)))

/-- A JSON string value occurs in a JSON value (object keys are not values). -/
inductive HasStr (s : String) : Json → Prop
  | str : HasStr s (.str s)
  | arr {xs : Array Json} {x : Json} : x ∈ xs → HasStr s x → HasStr s (.arr xs)
  | obj {j x : Json} {k : String} : j.getObjVal? k = .ok x → HasStr s x → HasStr s j

end VE.Scope
```

SC-4 adds a `forwards : List (String × String × String)` field and, after the `ScopeNoEffect` loop of `govern`,
`for (w, r, a) in D.forwards do forwardCheck D w r a` (5.6). SC-5 replaces `coveredLayout`'s `frontier` case by
`validateFrontier` (5.7) and adds `governAt`.

## 5. Theorem statements, by batch

Universes: `universe v`; `VE.Structure.{v}`. The `Pinned` placeholders are listed in 8.1.

### 5.1 SC-1a (Lean core: lists and lead-ins)

```lean
namespace VE.Layout

theorem listRun_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (lead : String) (us : List String)
    (h : listRun L lead = .ok us) (u : String) : u ∈ us ↔ GovernedItem L lead u

theorem listRun_ok_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (lead : String) :
    (listRun L lead).isOk = true ↔
      ∃ i d, (L[i]?).map (·.id) = some lead ∧ (L[i]?).map (·.lead) = some true ∧ (L[i+1]?).bind (·.item) = some d

end VE.Layout

namespace VE.Scope

theorem substOwn_no_own (g c : Json) (hg : hasOwn depthLimit g = false) (hc : depthOk depthLimit c = true) :
    hasOwn depthLimit (substOwn g depthLimit c) = false

theorem substOwn_id (g c : Json) (hc : hasOwn depthLimit c = false) : substOwn g depthLimit c = c

theorem commutes_symm (e₁ e₂ : Effect) : Commutes e₁ e₂ = Commutes e₂ e₁

/-- One owner per field: every key of the joined object comes from exactly one side. -/
theorem mergeParts_keys (u : String) (lead item out : Json) (h : mergeParts u lead item = .ok out) (k : String)
    (v : Json) : out.getObjVal? k = .ok v ↔
      (lead.getObjVal? k = .ok v ∧ (item.getObjVal? k).toOption = none) ∨
      (item.getObjVal? k = .ok v ∧ (lead.getObjVal? k).toOption = none)

theorem mergeParts_conflict (u : String) (lead item : Json) (k : String)
    (hl : (lead.getObjVal? k).toOption.isSome) (hi : (item.getObjVal? k).toOption.isSome) :
    (mergeParts u lead item).isOk = false

/-- The item's rule is the chain's own decoding of the joined object: scope decodes no rule field itself. -/
theorem itemRule_decoder (D : SDoc) (u : String) (lead item : Json) (N : SoftNode)
    (h : itemRule D u lead item = .ok N) :
    ∃ m, mergeParts u lead item = .ok m ∧ VE.Readings.Wire.decodeNorm D.re m = .ok N

/-- Identity: without governors, `govern` returns the document exactly as written. -/
theorem govern_identity (D : SDoc) (h : D.governors = []) (hp : partUnits D = []) : govern D = .ok D.doc

/-- Without governors a `part` content is refused. -/
theorem govern_orphan (D : SDoc) (h : D.governors = []) (u : String) (hu : u ∈ partUnits D) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeOrphanPart" = true

/-- Preservation: every member outside `units`, the unit order, every unit member but `content`, and every
    content outside `affected D`, are the document's own. -/
theorem govern_preserves (D : SDoc) (out : Json) (ho : govern D = .ok out) :
    (∀ k, k ≠ "units" → out.getObjVal? k = D.doc.getObjVal? k) ∧
    (unitsOf out).map idOf = (unitsOf D.doc).map idOf ∧
    ∀ (i : Nat) (x y : Json), (unitsOf out)[i]? = some x → (unitsOf D.doc)[i]? = some y →
      (∀ k, k ≠ "content" → x.getObjVal? k = y.getObjVal? k) ∧ (idOf y ∉ affected D → x = y)

/-- Provenance: an affected unit's rule is its base object, then exactly its unary governors in order, then the
    precedence edges into it. -/
theorem govern_provenance (D : SDoc) (out : Json) (ho : govern D = .ok out) (u : String) (hu : u ∈ affected D) :
    ∃ o₀ o₁ es, baseObj D u = .ok o₀ ∧
      (governorsOf D u).foldlM (fun o g => applyEffect u g.effect o) o₀ = .ok o₁ ∧
      edgesFor D u = .ok es ∧
      normOf (contentOf out u) = some (addOver es o₁) ∧
      ∀ g ∈ governorsOf D u, ∃ us, covered D g.reach = .ok us ∧ u ∈ us

theorem governorsOf_iff (D : SDoc) (u : String) (g : Governor) :
    g ∈ governorsOf D u ↔ g ∈ D.governors ∧ unary g.effect = true ∧ ∃ us, covered D g.reach = .ok us ∧ u ∈ us

/-- Scope introduces no symbol: every string value of the answer is a string value of the document or the block. -/
theorem govern_no_new_symbols (D : SDoc) (out : Json) (ho : govern D = .ok out) (s : String) (hs : HasStr s out) :
    HasStr s D.doc ∨ HasStr s D.block

/-- A governor or a governed unit that a reading set owns is refused. -/
theorem readings_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (us : List String)
    (hc : covered D g.reach = .ok us) (u : String) (hu : u = g.unit ∨ u ∈ us) (hs : u ∈ setUnits D.doc) :
    (govern D).isOk = false

/-- A content-changing governor never covers a unit whose content it cannot change: such a unit is refused, never
    skipped (an unwritten unit, `null`, stays pending and makes the governor UNFORMALISED). -/
theorem nonrule_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (he : isFrame g.effect || unary g.effect)
    (us : List String) (hc : covered D g.reach = .ok us) (u : String) (hu : u ∈ us)
    (hn : contentOf D.doc u ≠ .null) (hr : isPart (contentOf D.doc u) = false) (hm : isNorm (contentOf D.doc u) = false) :
    (govern D).isOk = false

end VE.Scope
```

### 5.2 SC-1b (on the stack)

```lean
namespace VE.Scope
open VE.Reports (Status)

def governorStatus (st : String → Option Status) (us : List String) : Option Status :=
  if us.isEmpty then none else (us.mapM st).map VE.Reports.foldStatus

theorem governor_status_weakest (st : String → Option Status) (us : List String) (s : Status)
    (h : governorStatus st us = some s) :
    us ≠ [] ∧ (∀ u ∈ us, ∃ t, st u = some t ∧ s.rank ≤ t.rank) ∧ ∃ u ∈ us, st u = some s

theorem governor_status_none (st : String → Option Status) (us : List String)
    (h : us = [] ∨ ∃ u ∈ us, st u = none) : governorStatus st us = none

/-- The document mode's answer on a scope@0 document is its answer on govern's output, statuses folded. -/
theorem scope_admission (front ans : Json) (h : Pinned.checkDoc front = .ok ans)
    (hs : "scope@0" ∈ Pinned.profilesOf front) :
    ∃ D out a, Pinned.decodeScope front = .ok D ∧ govern D = .ok out ∧
      Pinned.checkCore (Pinned.withUnits front out) = .ok a ∧ ans = Pinned.foldGovernors D a

/-- Documents without scope@0 are answered exactly as before. -/
theorem scope_absent_unchanged (front : Json) (h : "scope@0" ∉ Pinned.profilesOf front) :
    Pinned.checkDoc front = Pinned.checkCore front

end VE.Scope
```

`scope@0` is one row of AR-10's profile-gate table (a wrapper at step 1b over the norms, norm-defaults, soft and
rights routes); the row carries the composition theorem `scope_admission` for every combination it newly admits,
and AR-10's generic lemma shows the table runs as written. `foldGovernors` applies 1.6's table with `governorStatus`.

### 5.3 SC-1c (explain route and relay)

The mode follows CLAUDE.md's relayed-route recipe and registers through AR-10's mode registry: runner
`VE.Scope.Run.runCaseReported`, equation `VE.Service.runMode_scope` (listed in `lean/VE/Audit.lean`), shape
`ResponseShape.Schemas.Scope`, encoder theorem `ResponseShape.Encoders.Scope.runCaseReported_fits` (listed in
`lean/ResponseShape/Audit.lean`), generated `ve/backends/lean_service_schema/scope.json`. Those two recipe
theorems have the recipe's fixed forms (`runMode_discourse`, `Discourse.runCaseReported_fits`) and cannot be
elaborated before the batch adds the mode's constructor and shape; the rows they encode are:

```lean
namespace VE.Scope

structure GovRow where
  id : String
  unit : String
  effect : String
  reach : List String

structure Row where
  unit : String
  governors : List GovRow
  generated : List String      -- the owner's generated rule names for this unit (AP's split map), else []
  provenance : List String     -- Lean's sentences (`VE/Scope/English.lean`, 2.3)

def effectWord : Effect → String
  | .frame _ => "frame" | .reguard _ => "reguard" | .carveOut _ => "carve-out" | .precedes => "precedes"
  | .yields => "yields" | .title => "title"

def contributors (D : SDoc) (u : String) : List Governor :=
  frameOn D u ++ governorsOf D u ++ (ordered D).filter (fun g => match g.effect with
    | .precedes => g.unit == u
    | .yields => coversU D g u
    | _ => false)

def explainRows (D : SDoc) : Except String (List Row) := do
  let _ ← govern D
  pure ((affected D).map fun u =>
    let gs := contributors D u
    { unit := u,
      governors := gs.map (fun g => ⟨g.id, g.unit, effectWord g.effect, (covered D g.reach).toOption.getD []⟩),
      generated := (Pinned.splitRules D).filterMap (fun (n, src, _) => if baseName D u == some src then some n else none),
      provenance := gs.map (Pinned.sentence D u) })

theorem explain_bound (D : SDoc) (rows : List Row) (h : explainRows D = .ok rows) (r : Row) (hr : r ∈ rows) :
    r.unit ∈ unitIds D.doc ∧ ∀ x ∈ r.governors, x.unit ∈ unitIds D.doc ∧ ∃ g ∈ D.governors, g.id = x.id

theorem explain_rows_iff (D : SDoc) (rows : List Row) (h : explainRows D = .ok rows) (u : String) :
    (∃ r ∈ rows, r.unit = u) ↔ u ∈ affected D

theorem explain_generated (D : SDoc) (rows : List Row) (h : explainRows D = .ok rows) (r : Row) (hr : r ∈ rows)
    (n : String) : n ∈ r.generated ↔ ∃ src i, (n, src, i) ∈ Pinned.splitRules D ∧ baseName D r.unit = some src

end VE.Scope
```

The relay `ve/scope.py` checks the schema and the binding only (every unit and governor id exists in the request; no
row empty or extra), with fuzz tests that drop, empty, retype, duplicate or reorder each member and push an index
out of range: every mutant is `CheckerUnavailable` or changes nothing shown.

### 5.4 SC-2 (named lists and later qualifications)

Stated over the chain decoder's output, for conditions without attitude words: the hypothesis that the substituted
condition decodes under `VE.Norms.Wire.decodeBudgeted` (the base guard grammar) is false for a condition with an
attitude node, so these theorems say nothing about attitude words, which are attitudes'.

```lean
namespace VE.Scope

theorem reguard_applies (D : SDoc) (u : String) (c o o' : Json) (N N' : SoftNode) (G' : VE.Formula)
    (h : applyEffect u (.reguard c) o = .ok o') (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N')
    (hG : VE.Norms.Wire.decodeBudgeted (substOwn (o.getObjValD "guard") depthLimit c) = .ok G')
    (S : VE.Structure.{v}) (ρ : VE.Valuation S) :
    N' = { N with guard := G' } ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ G'.denote S ρ ∧ ¬ (VE.Norms.anyF N.carveOuts).denote S ρ)

/-- Plain narrowing is the special case: one more guard conjunct. -/
theorem restrict_applies (D : SDoc) (u : String) (C o o' : Json) (C' : VE.Formula) (N N' : SoftNode)
    (hC : hasOwn depthLimit C = false) (hC' : VE.Norms.Wire.decodeBudgeted C = .ok C')
    (h : applyEffect u (.reguard (Json.arr #[.str "and", .str "own", C])) o = .ok o')
    (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N) (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N')
    (S : VE.Structure.{v}) (ρ : VE.Valuation S) :
    N' = { N with guard := .and N.guard C' } ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ (VE.Norms.applies N.toNode).denote S ρ ∧ C'.denote S ρ)

theorem carveOut_applies (D : SDoc) (u : String) (c o o' : Json) (N N' : SoftNode) (C : VE.Formula)
    (h : applyEffect u (.carveOut c) o = .ok o') (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N')
    (hC : VE.Norms.Wire.decodeBudgeted (substOwn (o.getObjValD "guard") depthLimit c) = .ok C)
    (S : VE.Structure.{v}) (ρ : VE.Valuation S) :
    N' = { N with carveOuts := N.carveOuts ++ [C] } ∧
      ((VE.Norms.applies N'.toNode).denote S ρ ↔ (VE.Norms.applies N.toNode).denote S ρ ∧ ¬ C.denote S ρ)

def Typed (E : VE.Environment) (Γ : List String) (N : SoftNode) : Prop :=
  N.guard.check E Γ = true ∧ ∀ C ∈ N.carveOuts, C.check E Γ = true

/-- Typing is kept when the instantiated condition type-checks in the rule's situation context. -/
theorem applyEffect_typed (D : SDoc) (u : String) (e : Effect) (o o' : Json) (N N' : SoftNode)
    (E : VE.Environment) (Γ : List String) (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (h : applyEffect u e o = .ok o') (hN' : VE.Readings.Wire.decodeNorm D.re o' = .ok N') (hT : Typed E Γ N)
    (hc : ∀ c ∈ conditions e, ∀ C,
      VE.Norms.Wire.decodeBudgeted (substOwn (o.getObjValD "guard") depthLimit c) = .ok C → C.check E Γ = true) :
    Typed E Γ N'

/-- `own` is read at the rule's own valuation: it never sits under a binder, so it captures no variable. -/
theorem own_congr (c g₁ g₂ : Json) (hs : ownSafe depthLimit c = true) (G₁ G₂ C₁ C₂ : VE.Formula)
    (h₁ : VE.Norms.Wire.decodeBudgeted g₁ = .ok G₁) (h₂ : VE.Norms.Wire.decodeBudgeted g₂ = .ok G₂)
    (hc₁ : VE.Norms.Wire.decodeBudgeted (substOwn g₁ depthLimit c) = .ok C₁)
    (hc₂ : VE.Norms.Wire.decodeBudgeted (substOwn g₂ depthLimit c) = .ok C₂)
    (S : VE.Structure.{v}) (ρ : VE.Valuation S) (hG : G₁.denote S ρ ↔ G₂.denote S ρ) :
    C₁.denote S ρ ↔ C₂.denote S ρ

/-- Narrowings and own-free carve-outs commute, so source order is never a hidden choice. -/
theorem commute_applies (D : SDoc) (u : String) (e₁ e₂ : Effect) (hc : Commutes e₁ e₂ = true)
    (o o₁ o₂ : Json) (N₁ N₂ : SoftNode)
    (h₁ : (applyEffect u e₁ o).bind (applyEffect u e₂) = .ok o₁)
    (h₂ : (applyEffect u e₂ o).bind (applyEffect u e₁) = .ok o₂)
    (hN₁ : VE.Readings.Wire.decodeNorm D.re o₁ = .ok N₁) (hN₂ : VE.Readings.Wire.decodeNorm D.re o₂ = .ok N₂)
    (S : VE.Structure.{v}) (ρ : VE.Valuation S) :
    { N₁ with guard := .top, carveOuts := [] } = { N₂ with guard := .top, carveOuts := [] } ∧
      ((VE.Norms.applies N₁.toNode).denote S ρ ↔ (VE.Norms.applies N₂.toNode).denote S ρ)

theorem order_refused (D : SDoc) (h₀ : admitBlock D = .ok ()) (u : String) (hu : u ∈ unitIds D.doc)
    (g₁ g₂ : Governor) (h₁ : g₁ ∈ governorsOf D u) (h₂ : g₂ ∈ governorsOf D u) (hne : g₁.id ≠ g₂.id)
    (hc : Commutes g₁.effect g₂.effect = false) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeOrder" = true

/-- A list name names exactly its lead-in's run. -/
theorem listName_run (D : SDoc) (h₀ : admitBlock D = .ok ()) (n : VE.Discourse.ContentName) (lead unit : String)
    (h : (n, lead, unit) ∈ D.listNames) (us : List String) (hc : covered D (.listName n.name) = .ok us) :
    VE.Layout.listRun D.layout lead = .ok us ∧ n.units = us

end VE.Scope
```

`reguard_applies` and `carveOut_applies` say the effect changes the guard, or appends one carve-out, and nothing
else: `name`, `pred`, `sign`, `over` and the soft fields are the decoder's reading of the same members. On W1's
shared node budget the composite may exceed the budget where the parts did not; the decode hypotheses `hN'` carry
that. With attitudes, AT-3a's decoder reads the same substituted JSON; what the attitude words mean, and the frame
premises they add, are attitudes' theorems over that decoder.

### 5.5 SC-3a and SC-3b (headings and labels)

```lean
namespace VE.Layout

theorem itemRun_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (item : String) (us : List String)
    (h : itemRun L item = .ok us) (u : String) : u ∈ us ↔ ItemUnit L item u

theorem anchorReach_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (anchors : List VE.Discourse.Anchor)
    (a : String) (us : List String) (h : anchorReach L anchors a = .ok us) (u : String) :
    u ∈ us ↔ u ∈ L.map (·.id) ∧ within (spansOf L) anchors u a = true ∧ some u ≠ headingOf L anchors a

theorem discourse_within_unchanged (D : VE.Discourse.DDoc) (u a : String) :
    VE.Discourse.within D u a =
      within ((VE.Discourse.unitKeys D).map (fun k => (k.1, k.2.1, k.2.2.1))) D.K.anchors u a

theorem discourse_innermost_unchanged (D : VE.Discourse.DDoc) (u : String) :
    VE.Discourse.innermostAnchor D u =
      innermostAnchor ((VE.Discourse.unitKeys D).map (fun k => (k.1, k.2.1, k.2.2.1))) D.K.anchors u

end VE.Layout

namespace VE.Scope

theorem anchor_reach_iff (D : SDoc) (hd : (D.layout.map (·.id)).Nodup) (a : String) (us : List String)
    (hc : covered D (.anchor a) = .ok us) (u : String) :
    u ∈ us ↔ u ∈ D.layout.map (·.id) ∧ VE.Layout.within (VE.Layout.spansOf D.layout) D.anchors u a = true ∧
      some u ≠ VE.Layout.headingOf D.layout D.anchors a

theorem label_reach_iff (D : SDoc) (hd : (D.layout.map (·.id)).Nodup) (i : String) (us : List String)
    (hc : covered D (.label i) = .ok us) (u : String) : u ∈ us ↔ VE.Layout.ItemUnit D.layout i u

theorem title_identity (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (h : g.effect = .title) (out : Json)
    (ho : govern D = .ok out) : govern { D with governors := D.governors.filter (·.id != g.id) } = .ok out

-- SC-3b
def restrictAssertion (C φ : VE.Formula) : VE.Formula := .implies C φ
def carveAssertion (C φ : VE.Formula) : VE.Formula := .implies (.not C) φ

theorem assertion_restrict_denote (C φ : VE.Formula) (S : VE.Structure.{v}) :
    (restrictAssertion C φ).denote S [] ↔ (C.denote S [] → φ.denote S [])

theorem assertion_carve_denote (C φ : VE.Formula) (S : VE.Structure.{v}) :
    (carveAssertion C φ).denote S [] ↔ (¬ C.denote S [] → φ.denote S [])

end VE.Scope
```

SC-3b extends `baseObj` to an assertion content (an array) under a plain narrowing or an own-free carve-out of an
`anchor` or `label` reach: the content becomes `["implies", C, φ]` or `["implies", ["not", C], φ]`, closed
conditions only. Any other effect on an assertion stays `ScopeNotARule: <unit>`.

### 5.6 SC-4 (far precedence and forward exceptions)

```lean
namespace VE.Scope

theorem precedes_edges (D : SDoc) (out : Json) (ho : govern D = .ok out) (g : Governor) (hg : g ∈ D.governors)
    (he : g.effect = .precedes) (t : List (String × SoftNode)) (ht : ruleTable D = .ok t) (v : String)
    (N M : SoftNode) (hN : t.lookup g.unit = some N) (hM : t.lookup v = some M)
    (hv : ∃ us, covered D g.reach = .ok us ∧ v ∈ us) (hp : M.pred = N.pred) (hn : M.name ≠ N.name) :
    ∃ o xs, normOf (contentOf out g.unit) = some o ∧ o.getObjVal? "over" = .ok (.arr xs) ∧ Json.str M.name ∈ xs

theorem yields_edges (D : SDoc) (out : Json) (ho : govern D = .ok out) (g : Governor) (hg : g ∈ D.governors)
    (he : g.effect = .yields) (t : List (String × SoftNode)) (ht : ruleTable D = .ok t) (v : String)
    (N M : SoftNode) (hN : t.lookup g.unit = some N) (hM : t.lookup v = some M)
    (hv : ∃ us, covered D g.reach = .ok us ∧ v ∈ us) (hp : M.pred = N.pred) (hn : M.name ≠ N.name) :
    ∃ o xs, normOf (contentOf out v) = some o ∧ o.getObjVal? "over" = .ok (.arr xs) ∧ Json.str N.name ∈ xs

theorem no_effect_refused (D : SDoc) (h₀ : admitBlock D = .ok ()) (h₁ : orderCheck D = .ok ())
    (hc : ∀ u ∈ affected D, (composed D u).isOk = true) (t : List (String × SoftNode)) (ht : ruleTable D = .ok t)
    (g : Governor) (hg : g ∈ D.governors) (hgr : graph g.effect = true) (he : edgesOf D (fun v => t.lookup v) g = []) :
    ∃ e, govern D = .error e ∧ e.startsWith "ScopeNoEffect" = true

def laterUnitsIn (D : SDoc) (a w : String) : List String :=
  ((VE.Layout.anchorUnits D.layout D.anchors a).dropWhile (· != w)).drop 1

def forwardCheck (D : SDoc) (w r a : String) : Except String Unit :=
  if (laterUnitsIn D a w).any (fun x => ((baseObj D x).toOption.bind
      (fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption)).any (fun N => N.over.contains r)) then .ok ()
  else .error s!"ScopeForward: {w}: rule {r} has no later exception in {a}"

theorem forward_exception_sound (D : SDoc) (w r a : String) (h : forwardCheck D w r a = .ok ()) :
    ∃ x o N, x ∈ laterUnitsIn D a w ∧ baseObj D x = .ok o ∧ VE.Readings.Wire.decodeNorm D.re o = .ok N ∧
      r ∈ N.over

theorem forward_exception_complete (D : SDoc) (w r a : String) (x : String) (o : Json) (N : SoftNode)
    (hx : x ∈ laterUnitsIn D a w) (ho : baseObj D x = .ok o) (hN : VE.Readings.Wire.decodeNorm D.re o = .ok N)
    (hr : r ∈ N.over) : forwardCheck D w r a = .ok ()

end VE.Scope
```

### 5.7 SC-5 (frontier reaches; after SC-E1, lf-14d and an approved per-choice contract)

```lean
namespace VE.Scope

def enclosing (D : SDoc) (u : String) : List VE.Discourse.Anchor :=
  (D.anchors.filter fun a => VE.Layout.within (VE.Layout.spansOf D.layout) D.anchors u a.id).mergeSort
    (fun a b => a.span.2 - a.span.1 ≤ b.span.2 - b.span.1)

def lastList (bs : List VE.Layout.Unit) : List String :=
  match bs.reverse.dropWhile (fun x => x.item.isNone) with
  | [] => []
  | x :: rest => match x.item with
    | some d => (x.id :: (rest.takeWhile (VE.Layout.continues d ·)).filterMap
        (fun y => if y.item == some d then some y.id else none)).reverse
    | none => []

def frontierRaw (D : SDoc) (u : String) : List (List String) :=
  let L := D.layout
  match VE.Layout.indexOf L u with
  | some (i + 1) =>
    match L[i]? with
    | some p =>
      let before := L.take (i + 1)
      let beforeIds := before.map (·.id)
      let para := ((before.reverse.takeWhile (·.para == p.para)).reverse).map (·.id)
      let scopeIds := match enclosing D u with
        | a :: _ => VE.Layout.anchorUnits L D.anchors a.id
        | [] => L.map (fun (x : VE.Layout.Unit) => x.id)
      let closes := lastList (before.filter (fun x => scopeIds.contains x.id))
      let sections := (enclosing D u).map (fun a =>
        ((VE.Layout.anchorReach L D.anchors a.id).toOption.getD []).filter beforeIds.contains)
      ([[p.id], para, closes] ++ sections).foldl
        (fun acc c => if c.isEmpty || acc.contains c then acc else acc ++ [c]) []
    | none => []
  | _ => []

def frontier (D : SDoc) (u : String) : Except String (List (List String)) :=
  let fs := frontierRaw D u
  if fs.length > 8 then .error "ResourceLimit: scope" else .ok fs

inductive Fit | fits | fails | unresolved
  deriving DecidableEq, Repr

def fitAt (D : SDoc) (e : Effect) (u : String) : Option Bool :=
  match (baseObj D u).toOption.bind (fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption) with
  | none => none
  | some _ => some (match (do
        let o ← baseObj D u
        let o' ← applyEffect u e o
        VE.Readings.Wire.decodeNorm D.re o') with
      | .ok N' => Pinned.ruleTyped D.re N'
      | .error _ => false)

def fitFrom (rs : List (Option Bool)) : Fit :=
  if rs.all Option.isSome && rs.any (· == some false) then .fails
  else if !rs.isEmpty && rs.all (· == some true) then .fits
  else .unresolved

def fitOf (D : SDoc) (e : Effect) (us : List String) : Fit := fitFrom (us.map (fitAt D e))

def scopeCandidates (D : SDoc) (g : Governor) : List (List String) :=
  ((frontier D g.unit).toOption.getD []).filter (fun us => fitOf D g.effect us != .fails)

def validateFrom (gid : String) (fs : List (List String)) (fit : List String → Fit) : Except String (List String) :=
  match fs.filter (fun us => fit us != .fails) with
  | [] => .error s!"UnresolvedScope: {gid}: no candidate fits"
  | [us] => if fit us == .fits then .ok us
            else .error s!"UnresolvedScope: {gid}: a unit of its only candidate is not admitted"
  | cs => .error s!"AmbiguousScope: {gid}: {cs}"

def validateFrontier (D : SDoc) (g : Governor) : Except String (List String) := do
  validateFrom g.id (← frontier D g.unit) (fitOf D g.effect)

def fixAt (pick : String → Option (List String)) (g : Governor) : Governor :=
  match g.reach, pick g.id with
  | .frontier, some us => { g with reach := .fixed us, units := us }
  | _, _ => g

def governAt (D : SDoc) (pick : String → Option (List String)) : Except String Json :=
  govern { D with governors := D.governors.map (fixAt pick) }

theorem frontier_no_heuristic (D D₂ : SDoc) (u : String) (hL : D.layout = D₂.layout) (ha : D.anchors = D₂.anchors) :
    frontier D u = frontier D₂ u

theorem frontier_limit_iff (D : SDoc) (u : String) :
    (frontier D u).isOk = false ↔ 8 < (frontierRaw D u).length

theorem fitOf_fails_iff (D : SDoc) (e : Effect) (us : List String) :
    fitOf D e us = .fails ↔ (∀ u ∈ us, (fitAt D e u).isSome) ∧ ∃ u ∈ us, fitAt D e u = some false

theorem scopeCandidates_iff (D : SDoc) (g : Governor) (fs : List (List String)) (hf : frontier D g.unit = .ok fs)
    (us : List String) : us ∈ scopeCandidates D g ↔ us ∈ fs ∧ fitOf D g.effect us ≠ .fails

theorem frontier_accepted (D : SDoc) (g : Governor) (us : List String) (h : validateFrontier D g = .ok us) :
    ∃ fs, frontier D g.unit = .ok fs ∧ us ∈ fs ∧ fitOf D g.effect us = .fits ∧
      ∀ vs ∈ fs, fitOf D g.effect vs ≠ .fails → vs = us

theorem frontier_unresolved (D : SDoc) (g : Governor) (fs : List (List String)) (hf : frontier D g.unit = .ok fs)
    (h : scopeCandidates D g = [] ∨ ∃ us, scopeCandidates D g = [us] ∧ fitOf D g.effect us = .unresolved) :
    ∃ e, validateFrontier D g = .error e ∧ e.startsWith "UnresolvedScope" = true

theorem frontier_ambiguous (D : SDoc) (g : Governor) (fs : List (List String)) (hf : frontier D g.unit = .ok fs)
    (h : 2 ≤ (scopeCandidates D g).length) :
    ∃ e, validateFrontier D g = .error e ∧ e.startsWith "AmbiguousScope" = true

theorem governAt_no_frontier (D : SDoc) (h : ∀ g ∈ D.governors, g.reach ≠ .frontier)
    (pick : String → Option (List String)) : governAt D pick = govern D

theorem governAt_preserves (D : SDoc) (pick : String → Option (List String)) (out : Json)
    (ho : governAt D pick = .ok out) :
    (∀ k, k ≠ "units" → out.getObjVal? k = D.doc.getObjVal? k) ∧
    (unitsOf out).map idOf = (unitsOf D.doc).map idOf

/-- The reading set's compatible choices of reach are exactly the live candidates (lf-14d's joint set). -/
theorem scope_choices (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (hf : g.reach = .frontier)
    (hn : 2 ≤ (scopeCandidates D g).length) (us : List String) :
    (∃ pick ∈ Pinned.jointPicks D, pick g.id = some us) ↔ us ∈ scopeCandidates D g

end VE.Scope
```

SC-5's addendum, approved before SC-5 is built, pins `Pinned.ruleTyped` (the chain's existing per-rule typing
check) and `Pinned.jointPicks` (lf-14d's joint choices read as a pick per frontier governor), and states
`govern_provenance` and `govern_no_new_symbols` per choice.

### 5.8 SC-6 and SC-7

```lean
namespace VE.Scope

theorem limitation_scope_of_reach (D : SDoc) (g : Governor) (L L' : VE.Rights.Limitation)
    (h : Pinned.withReach D g L = .ok L') (us : List String) (hc : covered D g.reach = .ok us) :
    L'.scope = some (Pinned.rightNames D us) ∧ { L' with scope := L.scope } = L

theorem scope_parseRender (w : String) (b : Json) (h : Pinned.parseGovernor w = some b) :
    Pinned.renderGovernor b = w

theorem scope_renderParse (w : String) (b : Json) (h : Pinned.parseGovernor w = some b) :
    Pinned.parseGovernor (Pinned.renderGovernor b) = some b

end VE.Scope
```

## 6. Diagnostics and fault order

### 6.1 Texts

| Text | When | Stage |
|---|---|---|
| `InvalidInput: scope@0 unknown member <path>`, `InvalidInput: scope@0 <member> must be <form>` | a malformed block (3) | wire decoder |
| `ResourceLimit: scope governors` | more than 256 governors | `admitBlock` 1 |
| `DuplicateDeclaration: governor <id>` / `DuplicateDeclaration: list name <n>` | a repeated id or name | `admitBlock` 2–3 |
| `ScopeUnknownUnit: <unit>` | a governor's or registering unit, or a lead-in or item, not in the document | `admitBlock` 4, 6; reaches |
| `ScopeReserved: own` | a condition, and the vocabulary declares `own` | `admitBlock` 5 |
| `NotALeadIn: <unit>` | a list reach or list name whose unit does not end with ":" or is not followed by an item | reaches |
| `ManifestMismatch: scope.list_names.<n>.units` | a list name's recorded units differ from the run | `admitBlock` 6; reaches |
| `ResourceLimit: scope condition depth exceeds 64` | a condition deeper than 64 | `admitBlock` 7 |
| `ScopeOwnBound: <g>` | `own` under a binder | `admitBlock` 7 |
| `ManifestMismatch: scope.governors.<g>.unit` | a frame not on its lead-in, an anchor governor not on its heading, a label governor not on its item | `admitBlock` 7 |
| `ScopeReach: <g>` | a frame over another reach than a list or list name; a title over another reach than an anchor or label | `admitBlock` 7 |
| `NotALabel: <unit>`, `ScopeUnknownAnchor: <a>`, `ScopeUnknownName: <n>`, `ScopeUnknownRule: <r>` | a reach that does not exist | reaches |
| `UnsupportedProfile: scope@0 frontier reach requires SC-5` | a frontier reach before SC-5 | reaches |
| `ManifestMismatch: scope.governors.<g>.units` | the recorded reach differs from the regenerated one | `admitBlock` 7 |
| `ScopeReadings: <unit>` | the governor's unit or a governed unit is the unit of a reading set | `admitBlock` 7 |
| `ScopeNotARule: <unit>` | a `frame`, `reguard` or `carve_out` covers a unit whose written content is neither a part nor a norm | `admitBlock` 7 |
| `ScopeOrder: <unit>: <g1>, <g2>` | two unary governors on a unit that do not commute; two frames on a unit | `orderCheck`; composition |
| `ScopeNotARule: <unit>` | an effect on a unit whose content is not a part or norm (or lacks `guard`/`unless`) | composition |
| `ScopeOrphanPart: <unit>` | a part content no frame covers | composition; `govern` without governors |
| `InvalidInput: scope@0 parts of <unit> must be objects` | a frame part or item part that is not an object | composition |
| `ScopeConflict: <unit>: <key>` | a key written by both the lead-in and the item | composition |
| the chain decoder's own text | a composed rule the chain's decoder refuses (F1″) | `ruleTable`, or the chain |
| `ScopeNoEffect: <g>` | a graph governor whose reach has no other rule on the same predicate | graph step |
| `ScopeForward: <w>: rule <r> has no later exception in <a>` | a forward declaration with no later exception | SC-4 stage |
| `ResourceLimit: scope` | more than 8 frontier constituents (UNKNOWN) | SC-5 |
| `UnresolvedScope: <g>: no candidate fits` / `UnresolvedScope: <g>: a unit of its only candidate is not admitted` | 1.7 | SC-5 |
| `AmbiguousScope: <g>: <candidates>` | two or more live candidates | SC-5 |

The texts join AR-13's typed codes if AR-13 has merged; the codes are the words before the first ":".

### 6.2 Order

`govern` reports the first fault in this order (1.5.7): the wire decoder; `admitBlock` steps 1 to 7 (step 7 per
governor in block order: depth, `ownSafe`, the unit checks, the reach, the recorded units, reading sets, units it
cannot change); `orderCheck`
in document order of units and order 1.4 of governors; composition of affected units in document order; `ruleTable`;
`ScopeNoEffect` in order 1.4; forward declarations in block order. A `ResourceLimit` is UNKNOWN for every dependent
verdict, never a rejection.

## 7. Acceptance fixtures

### 7.0 How the values were obtained

"Computed" values come from `#eval` and `decide` in the scratch stub (4, 5 verbatim). Layout fixtures use the pilot
source's own bytes for each unit, shortened only inside sentences; each piece keeps its line structure (where its
line starts, its indentation, its marker, its trailing newlines), so `item`, `midLine`, `lead`, `label` and `para`
are those of the source. The pilot rule names, predicates and guards in the `govern` fixtures are stand-ins with the
pilot's shape; SC-1b's pilot fixtures compare against the translation itself (7.2). Each "exactly when" claim has a
fixture in each direction; the column "Direction" says which.

### 7.1 SC-1a (`Examples.lean` by `decide`/`rfl`; `tests/test_scope_lean.py`)

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| L1 | the layout of u0164.s01–u0166.s01 (hard constraints) | computed: u0164.s02 `midLine`, `lead`; u0165.s01–s07 `item = some 0`, `para = 1`; u0166.s01 `para = 2`, not an item | — |
| F1 | `listRun` from u0164.s02 | computed: `.ok [u0165.s01, …, u0165.s07]` | `listRun_iff` →, `listRun_ok_iff` → |
| F1-m | `mergeParts` of the frame `{"sign": false, "unless": [], "over": []}` and the item `{"name": "hc-cbrn-uplift", "predicate": "cbrn_uplift_avoidance_required", "guard": ["unary", "mass_casualty_weapon_uplift", ["var", 1]]}` | computed: equal to the whole rule object (all six W1 keys) | `mergeParts_keys` |
| F1-g | `govern` with the frame governor `g1` over seven part units | computed: u0165.s01's content is `{"norm":{"guard":["unary","mass_casualty_weapon_uplift",["var",1]],"name":"hc-cbrn-uplift","over":[],"predicate":"restricted_act_permitted","sign":false,"unless":[]}}`; u0165.s07's likewise with `hc-csam` and `csam_generation`; u0164.s02 keeps no content | `govern_provenance` |
| F1′ | u0165.s03's part also writes `sign` | computed: `ScopeConflict: u0165.s03: sign` | `mergeParts_conflict` |
| F1″ | an item missing `predicate` | `govern` succeeds; the chain's decoder refuses the rule with its own text, computed on the norms chain: `fields do not match: expected [name, predicate, sign, guard, unless, over], got [guard, name, over, sign, unless]` (the soft chain's own text there) | — |
| F1‴ | u0166.s01 after the run | computed: not in the run (a new paragraph, not an item) | `listRun_iff` ← |
| F2 | u0181.s02 "Key questions include:" over u0182.s01–s05 | computed: `.ok [u0182.s01, u0182.s02, u0182.s04]`; u0182.s03 ("Or does it escape these mechanisms?") and u0182.s05 are mid-line continuations | `listRun_iff` ← |
| F2′ | u0072.s02 over u0073.s01–s10 | computed: `.ok [u0073.s01, u0073.s05, u0073.s08]`; the "+ Example:" sub-bullets s04, s06, s07, s09, s10 are depth 1 | `listRun_iff` ← |
| F2″ | a lead-in followed by prose; a unit not ending with ":" | computed: `NotALeadIn: x.s01`; `NotALeadIn: u0164.s01` | `listRun_ok_iff` ← |
| F-id | no governors, no part (a four-unit norm document) | computed: `govern` returns the document, equal as a value | `govern_identity` |
| F-orph | no governors, seven part units | computed: `ScopeOrphanPart: u0165.s01` | `govern_orphan` |
| F-mm | the frame governor recording six of the seven units | computed: `ManifestMismatch: scope.governors.g1.units` | — |
| F-2f | two frame governors over the same list | computed: `ScopeOrder: u0165.s01: g1, g1b` | — |
| F-rs | a reading set on u0165.s03 | computed: `ScopeReadings: u0165.s03` | `readings_refused` |
| F-nr | u0165.s04's content an assertion `["top"]` under the frame | computed: `ScopeNotARule: u0165.s04`, not skipped | `nonrule_refused` |
| F-pend | u0165.s04 written without content | computed: u0165.s04 stays `null` (pending); u0165.s05 is composed as in F1-g | `nonrule_refused` (the other side) |
| F-go | `governorsOf` with `g1` (frame) and `g2` (reguard over the list name) | computed: u0165.s01 → `[g2]`; u0166.s01 → `[]`; u0164.s02 → `[]` | `governorsOf_iff` both |
| F-own | `hasOwn`, `ownSafe`, `depthOk` on u0173.s01's condition; `substOwn` on an own-free condition | computed: `(true, false after substitution, true, true)`; `own` under `forall` → `ownSafe` false; `own` beside a `forall` → true; an own-free condition is unchanged (`true`) | `substOwn_no_own`, `substOwn_id` |

### 7.2 SC-1b

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F1-doc | the pilot's hard-constraint block rewritten with the lead-in part and seven item parts, the guards exactly as AT-0p left them, checked end to end | the seven units OPEN as today, their answers byte for byte apart from the provenance lines; u0164.s02 OPEN (computed: `governorStatus` of seven OPEN units is `OPEN`) | `governor_status_weakest` |
| F1-off | the same document without `scope@0` | computed: `decodeContent` of a part content is `.pending`, so the seven units are UNFORMALISED | `scope_absent_unchanged` |
| F1-bad | one item not admitted | computed: `governorStatus` is `UNFORMALISED`; u0164.s02 UNFORMALISED | `governor_status_weakest` |
| F1-none | a governed unit with no status, or no governed unit | computed: `governorStatus` is `none` | `governor_status_none` |
| F1-lead | the frame part for the pilot | exactly the members on which all seven rules (as AT-0p left them) agree, minus `name`, `predicate` and `guard`; computed from the translation at SC-1b start | — |

### 7.3 SC-1c

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F-ex | `explainRows` with `g1` and `g2` | computed: seven rows, u0165.s01–s07, each with governors `[g1, g2]`; no row for u0164.s02, u0166.s01, u0173.s01 | `explain_rows_iff` both |
| F-ex-gen | a governed rule that act-phrases splits | its row lists the generated rules through `SplitMap.rules`; a unit with no split lists none | `explain_generated` both (at SC-1c, once AP-3 is merged; else the empty direction only) |
| F-ex-bind | route fixtures and fuzz mutants | every unit and governor id in a row exists in the request | `explain_bound` |

### 7.4 SC-2

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F3 | u0164.s01 registers "the hard constraints" over u0164.s02's run; u0173.s01 is `reguard` with the condition of 3 | computed guard JSON of u0165.s01: `["or",["and",["unary","mass_casualty_weapon_uplift",["var",1]],{"attitude":{"content":["unary","mass_casualty_weapon_uplift",["var",1]],"holder":["var",0],"mode":"knows"}}],{"attitude":{"content":["unary","mass_casualty_weapon_uplift",["var",1]],"degree":"quite likely","holder":["var",0],"mode":"thinks"}}]`. With `attitudes@0`, AT-3a's decoder reads it as `(G ∧ K(G)) ∨ L(G)`; without, the decoder refuses the node and u0173.s01 stays UNFORMALISED | `reguard_applies` (base part) |
| F4 | **the audit's case**: a two-element model (an instance `c`, a situation `s`) where Claude thinks it quite likely that `s` is of the category and `s` is not | computed by `decide` (attitude atoms standing in for AT-3a's generated predicates): F3's guard holds (`true`), the narrowed guard `G ∧ K` does not (`false`) | — |
| F6 | "The hard constraints do not apply when Claude is being tested by Anthropic." | computed: each rule's `unless` is `[["unary","tested_by_anthropic",["var",1]]]` | `carveOut_applies` |
| F6′ | a carve-out on a rule already at its route's carve-out limit | the decoding route's own limit diagnostic, unchanged (on the soft route today `InvalidInput: invalid sign or too many carve-outs`) | — |
| F7 | F3's `reguard` and a narrowing on one rule (the §8 note of the plan) | computed: `ScopeOrder: u0165.s01: gN, g2` | `order_refused` |
| F7-c | an own-mentioning carve-out and an own-free carve-out | computed: `ScopeOrder: u0165.s01: gOC, g6` | `order_refused` |
| F7′ | a narrowing plus a carve-out, in either block order | computed: the same JSON both ways: guard `["and", G, ["unary","no_operator_prompt",["var",1]]]`, `unless` `[["unary","tested_by_anthropic",["var",1]]]` | `commute_applies` |
| F7-t | the `Commutes` table | computed: (F3, F3) false; (F3, narrowing) false; (narrowing, carve-out) true; (carve-out, narrowing) true; (carve-out, carve-out) true; (narrowing, narrowing) true; (own carve-out, carve-out) false; (frame, narrowing) false | `commutes_symm` |
| F-ln | `covered` of the list name | computed: the seven units; a recorded list that differs is `ManifestMismatch: scope.list_names.<n>.units` | `listName_run` |

Pre-registered: u0173.s01 is claimed only with the full condition, never with the narrowing `G ∧ K`; F4 must
separate the two readings.

### 7.5 SC-3a and SC-3b

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F8 | UDHR u109 "## Article 29" over u110–u112 as a title | computed: the anchor reach is `[u110, u111, u112]`, the heading `u109`; `govern` returns the document unchanged (equal as a value) | `title_identity`, `anchorReach_iff` → |
| F8-out | u109 (the heading) and u113 (Article 30's heading) | not in Article 29's reach | `anchorReach_iff` ← |
| F9′ | `## Instructable behaviors` | a title, as F8 | `title_identity` |
| F10 | u0073.s01 "* **There’s no operator prompt:** ..." | computed: the label reaches `[u0073.s01, u0073.s02, u0073.s03, u0073.s04]` (the item, its two continuing sentences, its "+ Example:" sub-bullet), not u0073.s05; u0073.s04 is not a label (`NotALabel: u0073.s04`, no bold label); u0182.s02's label reaches `[u0182.s02, u0182.s03]` | `itemRun_iff`, `label_reach_iff` both |
| F9 (SC-3b) | `## When there is no operator prompt` over two rules, a narrowing over the anchor | computed: both guards become `["and", ["top"], ["unary","no_operator_prompt",["var",1]]]`; the rule under the next heading is unchanged; the same governor on a non-heading unit is `ManifestMismatch: scope.governors.g9b.unit` | `anchor_reach_iff` both |
| F9-a (SC-3b) | a narrowing over an anchor holding an assertion `φ` | the content becomes `["implies", C, φ]` | `assertion_restrict_denote` |

### 7.6 SC-4

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F11 | "Notwithstanding section 3, every operator may share." over rules `r3a` (same predicate) and `r3b` (another) | computed: `r9`'s `over` is `["r3a"]`; `r3b` adds nothing | `precedes_edges` |
| F11-y | the same as `yields` | computed: `r3a`'s `over` is `["r9"]` | `yields_edges` |
| F11′ | the same over `r3b` only | computed: `ScopeNoEffect: g11` | `no_effect_refused` |
| F11-u | an unknown rule name | computed: `ScopeUnknownRule: r7` | — |
| F11″ | edges that close a cycle | W1's `DependencyCycle`, unchanged | — |
| F12 | u0047.s05–s06 "That said, we discuss some exceptions to this in the section on “broad safety” below." | not recorded as a forward declaration (no rule is named): u0047.s06 stays UNFORMALISED with residual `UnresolvedScope`, never a guessed edge | — |
| F12-f | a forward declaration on h.s02 for rule `r1` in section `sec` | computed: with a later rule whose `over` is `["r1"]`, `.ok ()`; without, `ScopeForward: h.s02: rule r1 has no later exception in sec` | `forward_exception_sound`, `_complete` |

### 7.7 SC-5

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F13 | u0046.s02 "This is not a strict hierarchy, however." in its section | computed frontier: `[[u0046.s01], [u0045.s01, u0045.s02, u0045.s03], [u0044.s02, …, u0046.s01]]`: the previous sentence, the ordered list, the section's earlier units (three, not the plan's two: 9.1); every unit unadmitted, so all three live: `AmbiguousScope`; in translation one reading set with three candidates | `frontier_ambiguous` |
| F13′ | "Rule 4. ... This applies only where the user is an adult." with candidates `[r4]` (fits) and `[r1, r4]` (fails) | computed: the reach is fixed, `.ok [r4]` | `frontier_accepted`, `scopeCandidates_iff` both |
| F13‴ | an unsupported alternative: `[r4]` fits, `[r1, r4]` unresolved | computed: `AmbiguousScope: g13: [[r4], [r1, r4]]`, never a unique reach | `scopeCandidates_iff` |
| F13⁗ | an unresolved singleton: `[r4]` unresolved, `[r1, r4]` fails | computed: `UnresolvedScope: g13: a unit of its only candidate is not admitted` | `frontier_unresolved` |
| F13-n | every candidate fails | computed: `UnresolvedScope: g13: no candidate fits` | `frontier_unresolved` |
| F13″ | a sentence inside seven nested sections | computed: 9 constituents, `ResourceLimit: scope`; F13's 3 are within the limit | `frontier_limit_iff` both |
| F-fit | `fitFrom` on `[none, none]`, `[T, T]`, `[T, F]`, `[none, F]`, `[T, none]`, `[]` | computed: unresolved, fits, fails, unresolved, unresolved, unresolved | `fitOf_fails_iff` both |
| F-ch | lf-14d's joint choices for F13 | exactly the three candidates | `scope_choices` (at SC-5) |

### 7.8 SC-6 and SC-7

| Id | Fixture | Expected |
|---|---|---|
| F14 | u111 (29(2)) | its limitation reaches every right line; the residual `limitation_not_attached_to_rights_lines` closes |
| F14′ | u114 (Article 30) | its bar reaches every right line |
| F14″ | u112 | a two-candidate reading set |
| F5a | the catalogue on u0170.s01's wording | no governor |
| F5b | the pilot audit | flags any governor recorded on u0170.s01 (translation review, not Lean) |

## 8. Pinned names, limits and files

### 8.1 Names in-flight branches own (typed against placeholders; pinned when each merges)

| Placeholder | Owner | Pinned to |
|---|---|---|
| `Pinned.checkCore`, `Pinned.checkDoc`, `Pinned.profilesOf`, `Pinned.withUnits` | lf-16g's Lean document mode (`lean/VE/Service/Document.lean`; today `VE.Service.Document.check`) | its entry at SC-1b start; `checkCore` is the entry without scope's branch |
| `Pinned.decodeScope`, `Pinned.foldGovernors` | SC-1b's own definitions | written by SC-1b |
| `VE.Readings.Wire.ReadingsEnvironment`, `VE.Readings.Wire.decodeNorm` | the chain's decoder (merged) | as merged; for a document without `readings@1`, SC-1b builds the same record from the chain's environment decoding |
| `Pinned.ruleTyped` | the chain's per-rule typing check | SC-5's addendum |
| `Pinned.jointPicks` | lf-14d (`VE.Discourse` joint choices in Lean) | SC-5's addendum |
| `Pinned.splitRules`, `Pinned.sentence` | AP-3's `VE.Acts.SplitMap.rules`; SC-1c's `VE/Scope/English.lean` | SC-1c |
| `Pinned.parseGovernor`, `Pinned.renderGovernor` | english-lean's catalogue | SC-7 |
| `Pinned.rightNames`, `Pinned.withReach` | rights@0 (`VE.Rights.Limitation.scope`) | SC-6, after S2b |
| attitude guard nodes | AT-3a, inside W1's `decodeNorm` and soft's `decodeSoftNorm` | SC-2's claim |
| AR-10's profile-gate row and mode registry | AR-10 | SC-1b, SC-1c |

### 8.2 Limits

Governors ≤ 256; list names ≤ 256 (the governor limit's); anchors ≤ 1,024 (discourse's); condition depth ≤ 64;
frontier constituents ≤ 8; reading-set candidates ≤ 8 (one choice per frontier governor). Every limit is
`ResourceLimit`, UNKNOWN.

### 8.3 Files, generated files and the audit

As the plan's batches list them. Generated files (schemas, `tools/gate-collection.json`, `lean/checkers.lock`,
Python's profile data, `lean/VE/Route/frozen-sources.sha256`, route cases) are regenerated with
`tools/regen_generated.py --write`, never by hand. Each theorem gets one `#print axioms` line in
`lean/VE/Audit.lean` (or AR-1's generator); the audit allowlist is unchanged.

## 9. Choices this draft made, and questions for the review

### 9.1 Where the draft chose between readings of the plan

1. **The document representation is JSON, and effects act on the rule's JSON object.** The debate required a
   return type that can express preservation and conditions decoded by the owner's decoder after `own` is
   substituted. Composing on JSON and decoding once, downstream, satisfies both and keeps every attitude
   elaboration in the owner's decoder. Untouched unit values are returned as the original values, so
   preservation is literal equality (Lean's JSON objects compare by tree shape, so nothing untouched is rebuilt).
2. **`own` is the JSON string value `"own"` at any depth, with the name `own` reserved** (1.4). A formula-position
   rule would need the grammar of every profile's guard nodes; the reservation needs none and is decidable.
3. **`own` under a base-grammar binder is refused** (`ScopeOwnBound`), not lifted: capture-avoiding substitution on
   JSON would be scope's own de Bruijn code. `own_congr` is the theorem that answers the plan's risk 2.
4. **Governors record their reach units** (`units`), regenerated and compared, as the plan's wire rule says for
   reaches; readers of the front matter see what each governor governs.
5. **Anchors ride in scope's block** until composition S4 lets a discourse manifest sit beside norm content, as the
   plan already does for list names (9.2 asks how they are checked).
6. **Status order is `VE.Reports.Status.rank`** (attribution's spec 6, the one merged order); the document mode
   names statuses with the same words.
7. **Governor status applies only to content-less governor units with meaning `specified`** (1.6): scope never
   claims a unit the translator marked open or unformalised. The plan's "LABELLED" for titles and list names is
   the document mode's own status for such a unit, unchanged.
8. **`frame` must sit on its lead-in; a title reaches only an anchor or label** (`ScopeReach`), so each effect has
   one place it can be written.
9. **Depth is half the indentation, odd indentation is not an item** (1.2), so the layout reading is one function of
   the bytes.
10. **The frontier's list constituent needs no lead-in** (the last list in the innermost anchor), so F13 has three
    candidates where the plan estimated two; the frontier rule is what SC-E1 tests, and its fixtures change if
    SC-E1 changes the rule.
11. **F12 is a translation-ledger fixture**: an announcement that names no rule is not recorded, rather than
    recorded and refused.
12. **The provenance wording table (2.3)** is a first draft for SC-E2 to test; the plan gave one example.
13. **A content-changing governor never covers a unit it cannot change** (`ScopeNotARule`, `nonrule_refused`):
    without this check such a unit would be skipped while its status still counted toward the governor's, so the
    governor could be claimed over a unit it did not change. An unwritten (pending) unit stays allowed and makes
    the governor UNFORMALISED.

### 9.2 Questions for the statement review

1. Anchors in scope's block: should their tree, duplicate and overlap checks be discourse's `anchorsOk` called on
   a manifest view (it takes a `DDoc`), or should SC-3a move those check bodies into `VE.Layout` beside
   containment, as it moves `within`? The second adds `lean/VE/Discourse/WellFormed.lean` to SC-3a's shared files.
2. Is the any-depth `"own"` with the reserved name acceptable to attitudes (AT-3a's node has no member whose value
   could be the string `own` except `content`), and to the other packs whose guard nodes may follow?
3. Is the status rule of 1.6 (content-less governors with meaning `specified` only) the intended reading of the
   plan's "weakest of governed", or should a governor with another meaning take the weaker of its own status and
   the governed ones?
4. `restrict_applies` and `reguard_applies` are stated for the base guard grammar only. Is a statement over
   AT-3a's decoder needed in scope at all, or is attitudes' own decoder theorem the right and only owner?

## 10. Review checklist

- [ ] One reading: every wording of 2.1 and 2.2 maps to one block; ambiguity becomes a reading set or a refusal.
- [ ] Lean owns meaning: no effect is decided in Python; every effect's meaning is the chain's decoder's (5.4).
- [ ] One owner per piece of logic: no rule-field list in scope; containment moved, not copied; split maps and pack
      origins read, not re-derived; the wording table in Lean.
- [ ] Preservation is expressible and strong (`govern_identity`, `govern_preserves`, `govern_no_new_symbols`).
- [ ] Precedence is a graph step with provenance (`govern_provenance`'s edges, `precedes_edges`, `yields_edges`).
- [ ] `Commutes` is syntactic and conservative; everything else is `ScopeOrder`.
- [ ] Three-valued `Fits`; unresolved singletons stay unresolved; overflow is UNKNOWN, never truncated.
- [ ] Every "exactly when" claim has a fixture each way (7, column "Direction").
- [ ] Honest limits: translation effects are recorded claims; SC-E2 is proxy evidence; the 263 B claim waits for
      AT-3a.
- [ ] Every statement elaborates (stub, Lean v4.24.0); nothing is proved yet.
