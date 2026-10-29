# Cross-sentence scope (`scope@0`): item-1 specification

> Status: item-1 specification, draft 4, 2026-10-13, design only: no product code, test or generated file changes.
> Draft 4 records the phase-1 results ([docs/research/scope-phase1.md](../research/scope-phase1.md), SC-M0) beside
> [scope-PLAN.md](scope-PLAN.md) draft 5; it changes no definition, statement or fixture value (9.6).
> Draft 3 applies the confirmation round's one finding (`manage-agents/scope-p3ver1.final.md`): the document mode
> calls the run path `governFast`, not `govern` (1.5.8, 5.2, 9.5); no statement changes, and nothing else does.
> Written from [scope-PLAN.md](scope-PLAN.md) draft 3 (draft 4 adds only that fix), which applies the converged
> Astra + Fable design debate (`manage-agents/debates/design-scope/`, CONVERGED after round 3) and the DRI's
> cross-plan synthesis edits 1–8 of 2026-10-13. Draft 2 applies the statement review of draft 1
> (`manage-agents/debates/scope-spec/`, Astra + Fable, CONVERGED after round 3: **FIX**): every correction of the
> joint position, and no other design change (9.3 lists them, each with where it lands). A confirmation round on
> this diff only, not a fresh review, decides PASS; a clean confirmation opens SC-1a and SC-3a, while SC-3b and SC-5
> stay gated on their approved addenda (9.4). Baseline `main` at `49de179e`, read on branch `design/scope` at
> `f80910c1`.
> **Checked, not proved.** Every definition and theorem statement in sections 4 and 5 was elaborated by Lean
> v4.24.0 as a scratch stub, `lean/SpecStubs_scope.lean` (untracked, never committed), against the merged modules
> it names (`VE.Readings.Wire`, `VE.Discourse.{Wire,Access,WellFormed}`, `VE.Finite`, `VE.Attribution.Status`),
> with `sorry` for every proof. Elaborating with `sorry` establishes only that the statements typecheck: nothing
> here is proved, and each repaired contract also has its executed counterfixture (9.3). Names that in-flight
> branches own are typed against `opaque` placeholders in a `Pinned` namespace (8.1) and are pinned when each branch
> merges. **Every fixture value in section 7 marked "computed" was produced by `#eval` or `decide` in that stub,
> not by hand.** Fixtures over the pilot layout use the pilot's own bytes for the units involved, shortened only
> inside sentences (7.0).

## Changes in this draft (draft 4)

- **No definition, theorem statement, diagnostic or fixture value changes,** so the scratch stub needs no
  re-elaboration: phase 1 measured the pilots and checked the spec's layout results (C11), and found nothing a statement
  depends on (9.6).
- **7.0:** the results C11 checks of the layout fixtures L1, F1, F1‴, F2, F2′, F2″ (its pilot half) and F10 agree
  on the full pinned layout of 1,132 units under SC-M0's independent transcription of 1.2 and 4.1, and L1's `para`
  values agree after rebasing (7.0 lists the checked fields); B1's input is that layout.
- **9.6:** u0123.s03 is six source limits, which act-phrases' AP-3 turns into five prohibitions and one explicit
  residual (its A14); the open question for SC-4's section accounts for the residual.
- **1.2:** a note on what `item` counts on the pilot (182 units: every marker, not only `* ` bullets).
- **New 9.6:** the phase-1 results that bear on the spec, and one open question for SC-4's section: the reading of
  u0123.s03 (candidate fixture F15 in plan SC-4).
- **10:** one checklist line for the phase-1 layout check.

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
(7), pinned names, limits and files (8), the choices the drafts made, the review's answers and corrections, and the
addenda that gate SC-3b and SC-5 (9), the review checklist (10).

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
anchors    discourse's anchors, decoded by discourse's decoder from the block and checked by discourse's anchor
           checks, moved to VE.Layout (SC-3a; 1.2)
re         the chain's decoding environment, VE.Readings.Wire.ReadingsEnvironment (pinned, 8.1)
```

GOVERN's output is the complete document, as JSON: `doc` with the content of each **affected** unit (1.5.4)
replaced by its composed rule, and nothing else changed. GOVERN first admits the block (`admitBlock`, 6.1), with or
without governors, so malformed metadata (list names, anchors, at SC-4 forward declarations) is refused before
anything else (`govern_admits`). With no governor, an admitted block and no `part` content, the output is `doc`
itself, byte for byte as a value (`govern_identity`), so the chain's ordinary decoding is exactly today's. A
document without `scope@0` never reaches GOVERN (`scope_absent_unchanged`).

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
| `para` | the number of blank lines (a newline, then only spaces, tabs or CRs, then a newline) before byte `s`; one pass over the bytes gives it for every unit (`paraCounts`) |

Unit ids are distinct (the document loader checks it); the theorems that need it take `(L.map (·.id)).Nodup`.

On the pinned constitution, `item` holds for 182 units: 141 `* ` bullets at depth 0, 37 `+ ` sub-bullets at depth
1 and 4 numbered items (SC-M0, C7; the research's 141 counted `* ` lines only). Every one of its 23 `lead` units
(1,600 B) is followed by an item, so the source has no `NotALeadIn` (9.6).

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
units within it, in source order; the first is its **heading**; the anchor reach is the others. Discourse's anchor
checks (its 4.1(2): one tree, nested and non-overlapping spans, unique labels per parent, exports) move the same
way, over `(anchors, the spans of the definition units, the environment's unary test)`, with the generic helpers
they call; discourse's `anchorsOk` becomes a one-line call (`discourse_anchorsOk_unchanged`) and its anchor fixtures
pass unchanged. So one body checks anchors for both discourse and scope (`admitBlock` step 7), and no view of a
discourse document has to be invented for scope.

### 1.3 Governors, reaches, effects

A **governor** is `(id, unit, effect, reach, units)`: `unit` is the unit whose words govern, `units` the reach as
recorded, which Lean regenerates and compares (`ManifestMismatch: scope.governors.<id>.units`).

| Reach | Governed units | Batch |
|---|---|---|
| `list <lead>` | the list run's governed items of the lead-in (1.2) | SC-1a |
| `list_name <name>` | the run of the lead-in the name registers; the name's recorded units must equal it | SC-2 |
| `anchor <id>` | the anchor's units after its heading; a unary or `title` governor's unit must be the heading, while a `precedes` or `yields` governor's unit is its own rule and may be any unit | SC-3a |
| `label <item>` | the item units of 1.2; a unary or `title` governor's unit must be the item, while a graph governor's unit may be any unit | SC-3a |
| `rules [names]` | the rule units whose base rule (1.5.1) has one of the names; an unknown name is `ScopeUnknownRule` | SC-4 |
| `frontier` | the candidates of 1.7 | SC-5 |

| Effect | What it writes (the meaning is the owner's) | Reach allowed | Batch |
|---|---|---|---|
| `frame <part>` | the lead-in's part, joined to each governed item's part with disjoint keys (one owner per field); the governor's unit is the lead-in | `list`, `list_name` | SC-1a |
| `reguard <c>` | the rule's `guard` becomes `c` with `own` replaced by the rule's guard (1.4) | any but `frontier` before SC-5 | SC-2 |
| `carve_out <c>` | one more element of the rule's `unless`, `c` with `own` replaced by the rule's guard | as `reguard` | SC-2 |
| `precedes` | each reached rule on the same predicate joins the governor's own rule's `over` | any but `frontier` | SC-4 |
| `yields` | the governor's own rule's name joins the `over` of each reached rule on the same predicate | any but `frontier` | SC-4 |
| `title` | nothing | `anchor`, `label` | SC-3a |

`frame`, `reguard` and `carve_out` change content; `reguard` and `carve_out` are the **unary** effects;
`precedes` and `yields` are the **graph** effects (1.5.5). A graph governor's own rule is the unit it sits on, so
"Notwithstanding the rules of section 3, <rule>." sits outside section 3 and reaches it by `anchor` (F11-a). A
`frontier` reach carries a unary effect only: a graph effect there is `ScopeReach` (`frontier_graph_refused`) until
SC-5's addendum adds graph fitting (9.4).

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

**1.5.7 Fault order.** `govern D`: first `admitBlock` (6.1, in order, with or without governors; from SC-4 its last
step checks the forward declarations, 1.9); then, with no governor, the document itself, or `ScopeOrphanPart` for
the first part unit; otherwise `orderCheck`, composition of every affected unit in document order, `ruleTable` and
the `ScopeNoEffect` check in governor order; then the patch.

**1.5.8 Run path.** `govern` is the statement. It recomputes a governor's reach wherever a unit asks for it
(`coversU`, `frameOn`, `governorsOf`), and a `rules` reach decodes every rule unit's base rule each time (`covered`,
`baseName`), so `orderCheck` and `affected`, which ask for every unit, are cubic on the pinned pilot (1,132 units).
The run path is `governFast`, SC-1a's own definition: the same steps with each governor's reach and each rule unit's
base name computed once, into a table keyed by governor id that the reach tests read. `governFast_eq` states that it
answers exactly as `govern`, so every theorem about `govern` holds of the run path. SC-1b's document mode calls
`governFast`, never `govern` (5.2). Its speed is measured by a benchmark row on the full pilot (7.2 B1), never
asserted in the suite.

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
reads) or when a resource limit stops the decoding of the composed rule (`ResourceLimit`: exhaustion is UNKNOWN,
never evidence against a candidate, `fitAt_limit`); else whether the effect applies and the composed rule is typed
by the chain's own rule check (pinned at SC-5's addendum, 8.1). A candidate **fails** only when every unit is
admitted and the effect fails at one; it **fits** when every unit fits; otherwise it is **unresolved**
(`fitOf_fails_iff`). Live candidates are those that do not fail. A frontier reach carries a unary effect only (1.3),
so fitting applies the effect at each unit and never needs the governor's own rule or the graph step.

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
a governor's **payload**, its frame part or its condition (`govern_strings`; the rule names `addOver` writes are
read verbatim by the chain's decoder, `decodeNorm_name`). For governors bound to the block as written
(`BlockBound`: every string value of a payload is one of the block), every string value of the output is one of
the document or the block (`govern_no_new_symbols`), and SC-1b's decoder guarantees that binding for every decoded
document (`decodeScope_bound`). The binding is needed: a governor list that is not tied to the block puts a string
into the output that is in neither (F-sym). For provenance, scope reads the owner's exported map and never
re-derives a split or a key: for act-phrases `VE.Acts.SplitMap.rules` (AP-3), for the packs their `origins` (PK-1).
The explain route lists a generated rule under its source unit and names its source rule (`explain_generated`).

### 1.9 Forward declarations (SC-4)

"Rule r has exceptions stated later in this section." is recorded as `(unit w, rule r, anchor a)` and checked: some
unit of `a` after `w` has a base rule whose `over` names `r` (`forward_exception_sound`, and its converse
`forward_exception_complete`); otherwise `ScopeForward: <w>: rule <r> has no later exception in <a>`. The check is
the last step of `admitBlock` (6.1), so it runs with or without governors, before the identity shortcut. A forward
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
| `The hard constraints apply only where <condition>.`, where <condition> does not mention "its kind" | `reguard ["and", "own", C]` over `list_name`, `C` free of `own` | "Each of the 7 rules called ‘the hard constraints’ applies only where <condition>." A condition that mentions "its kind" takes the next row's wording |
| `In place of their own condition, the hard constraints apply only where Claude knows that the act is of its kind, or thinks it quite likely that it is.` | `reguard` over `list_name` with attitude nodes and `own` (F3's condition) | "Each of the 7 rules now applies where Claude knows that the act is of its kind, or thinks it quite likely that it is, instead of where its own act occurs; its existing carve-outs still apply. ‘Its kind’ is each rule's own act." ("In place of" marks the replacement; F4 separates it from the previous row's reading) |
| `The hard constraints do not apply when <condition>.` | `carve_out` over `list_name` | "None of the 7 rules applies when <condition>; other rules may decide; if none does, <the default sentence of each rule's predicate>." (W1 2.5: the default is named, never "the default decides") |
| `Notwithstanding the rules of section 3, <rule>.` (the rule is rule 9) | `precedes` over `anchor`, on rule 9's own unit | "Wherever rule 9, or a rule that takes precedence over it directly or through other rules, applies, no rule of section 3 decides on that act." (W1 2.3 and 4.2: rule 9's subtree yields) |
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
| `list_names` | array of `{"name", "units", "scope", "lead", "unit"}` | optional; at most 256; `lead` and `unit` are read by scope, the rest is passed to `VE.Discourse.Wire.decodeContentName` unchanged; in `scope@0` the name's `scope` must be `"doc"` (anything else is `InvalidInput`), since no scoped lookup exists yet |
| `anchors` | array of discourse anchor objects | optional (SC-3a); decoded by `VE.Discourse.Wire.decodeAnchor` and checked by discourse's anchor checks, moved to `VE.Layout` (1.2) |
| `forward` | array of `{"unit", "rule", "anchor"}` | optional (SC-4); checked by the last step of `admitBlock` (1.9) |
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
comments and the `-- SC-5` remark in `coveredLayout`. Inside `namespace VE.Layout` the name `Unit` is the layout's
structure, so the type of a check's success is written `_root_.Unit` there.

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

/-- One pass over the bytes: at each position `s ≤ b.size`, the number of blank lines (a newline, then only
    spaces, tabs or CRs, then a newline) whose last newline lies before `s`. -/
def paraCounts (b : ByteArray) : Array Nat :=
  let r := b.foldl (fun (acc : Array Nat × Nat × Bool) c =>
    let (arr, cnt, blank) := acc
    let arr := arr.push cnt
    if c == nl then (arr, if blank then cnt + 1 else cnt, true)
    else if c == sp || c == 9 || c == 13 then (arr, cnt, blank)
    else (arr, cnt, false)) (#[], 0, false)
  r.1.push r.2.1

def ofSource (prose : String) (units : List (String × Nat × Nat)) : List Unit :=
  let b := prose.toUTF8
  let pc := paraCounts b
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
      para := pc.getD s 0 }

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

/-! Discourse's anchor checks (SC-3a), moved; discourse's `anchorsOk` calls this. -/

open VE.Discourse (req runAll allOk dupOf spanIn spansDisjoint)

def reachesRoot (anchors : List VE.Discourse.Anchor) : Nat → VE.Discourse.Anchor → Bool
  | 0, _ => false
  | n + 1, a => match a.parent with
    | none => true
    | some p => match anchors.find? (·.id == p) with
      | some b => spanIn a.span b.span && reachesRoot anchors n b
      | none => false

def anchorsOk (anchors : List VE.Discourse.Anchor) (defSpans : List (Nat × Nat)) (unary : String → Bool) :
    Except String _root_.Unit := runAll [
  fun _ => req (anchors.length ≤ 1024) "ResourceLimit: anchors",
  fun _ => match dupOf (anchors.map VE.Discourse.Anchor.id) with
    | some a => .error ("DuplicateDeclaration: anchor " ++ a)
    | none => .ok (),
  fun _ => req ((anchors.filter (·.parent.isNone)).length == 1 || anchors.isEmpty)
    "InvalidInput: anchors must form one tree",
  fun _ => allOk anchors fun a => req (reachesRoot anchors (anchors.length + 1) a)
    ("DanglingAnchor: " ++ ((a.parent).getD a.id)),
  fun _ => allOk anchors fun a => allOk anchors fun b =>
    if a.id != b.id && a.parent == b.parent && a.parent.isSome then
      if a.label.toLower == b.label.toLower then .error ("DuplicateAnchor: " ++ a.label)
      else req (spansDisjoint a.span b.span) ("InvalidInput: anchors " ++ a.id ++ ", " ++ b.id ++ " overlap")
    else .ok (),
  fun _ => allOk anchors fun a => req (a.exports.all fun p => unary p && defSpans.any (spanIn · a.span))
    ("ManifestMismatch: anchors." ++ a.id ++ ".exports")]

end VE.Layout
```

The bodies are discourse's `reachesRoot` and `anchorsOk` (`lean/VE/Discourse/WellFormed.lean`), with `anchorOf D`
read as `anchors.find?` and `definitionIn D a` as `defSpans.any`. The generic helpers they open (`req`, `runAll`,
`allOk`, `dupOf`, `spanIn`, `spansDisjoint`, with their lemmas) sit in `WellFormed.lean` above `Access.lean` in the
import graph today; SC-3a moves them with the bodies, below `Access.lean`, and discourse opens them from there. The
stub opens them from `VE.Discourse.WellFormed`.

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
  | .frontier => throw "UnsupportedProfile: scope@0 frontier reach requires SC-5"   -- SC-5: its addendum (9.4)
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

def kindOf (doc : Json) (u : String) : String :=
  (((unitsOf doc).find? (idOf · == u)).map (fun x => (x.getObjValD "kind").getStr?.toOption.getD "")).getD ""

/-- The spans of the definition units, for discourse's export check. -/
def defSpans (D : SDoc) : List (Nat × Nat) :=
  (D.layout.filter (fun x => kindOf D.doc x.id == "definition")).map (·.span)

def admitBlock (D : SDoc) : Except String Unit := do
  if D.governors.length > 256 then throw "ResourceLimit: scope governors"
  if D.listNames.length > 256 then throw "ResourceLimit: scope list names"
  if let some i := firstDup (D.governors.map (·.id)) then throw s!"DuplicateDeclaration: governor {i}"
  if let some n := firstDup (D.listNames.map (·.1.name)) then throw s!"DuplicateDeclaration: list name {n}"
  for g in D.governors do
    unless (unitIds D.doc).contains g.unit do throw s!"ScopeUnknownUnit: {g.unit}"
  if D.governors.any (fun g => !(conditions g.effect).isEmpty) && (vocabularyNames D).contains "own" then
    throw "ScopeReserved: own"
  for (cn, lead, unit) in D.listNames do
    unless cn.scope == "doc" do throw s!"InvalidInput: scope@0 list_names.{cn.name}.scope must be doc"
    unless (unitIds D.doc).contains unit do throw s!"ScopeUnknownUnit: {unit}"
    let us ← VE.Layout.listRun D.layout lead
    unless cn.units == us do throw s!"ManifestMismatch: scope.list_names.{cn.name}.units"
  VE.Layout.anchorsOk D.anchors (defSpans D) (VE.Discourse.unaryPred D.re.se.ne.rv.environment)
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
    | .precedes, .frontier => throw s!"ScopeReach: {g.id}"
    | .yields, .frontier => throw s!"ScopeReach: {g.id}"
    | _, _ => pure ()
    match g.reach with
    | .anchor a =>
      unless graph g.effect || VE.Layout.headingOf D.layout D.anchors a == some g.unit do
        throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .label i => unless graph g.effect || i == g.unit do throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
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

/-- The block is admitted first, with or without governors. -/
def govern (D : SDoc) : Except String Json := do
  admitBlock D
  if D.governors.isEmpty then
    match partUnits D with
    | [] => pure D.doc
    | u :: _ => throw s!"ScopeOrphanPart: {u}"
  else
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

/-- What a governor's effect can write into the output: its frame part or its condition; nothing for the others. -/
def payload : Effect → Json
  | .frame p => p
  | .reguard c => c
  | .carveOut c => c
  | _ => .null

/-- The decoded governors are bound to the block as written: every string value of a payload is one of the block. -/
def BlockBound (D : SDoc) : Prop :=
  ∀ g ∈ D.governors, ∀ s, HasStr s (payload g.effect) → HasStr s D.block

end VE.Scope
```

SC-4 adds a `forwards : List (String × String × String)` field and, as the **last step of `admitBlock`** (step 9),
`for (w, r, a) in D.forwards do forwardCheck D w r a` (5.6). The forward declarations are then checked before the
no-governor branch of `govern`, and every hypothesis `admitBlock D = .ok ()` (`govern_identity`, `govern_orphan`,
`order_refused`, `listName_run`, `no_effect_refused`) covers them with no change to its statement. SC-5's frontier
validation and its per-choice `governAt` (5.7) cannot be wired into `coveredLayout` as written; how it is wired is
an obligation of SC-5's addendum (9.4).

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

/-- Identity: without governors, an admitted block leaves the document exactly as written. -/
theorem govern_identity (D : SDoc) (h₀ : admitBlock D = .ok ()) (h : D.governors = []) (hp : partUnits D = []) :
    govern D = .ok D.doc

/-- Without governors, once the block is admitted, a `part` content is refused. -/
theorem govern_orphan (D : SDoc) (h₀ : admitBlock D = .ok ()) (h : D.governors = []) (u : String)
    (hu : u ∈ partUnits D) : ∃ e, govern D = .error e ∧ e.startsWith "ScopeOrphanPart" = true

/-- The block is admitted before anything else, with or without governors. -/
theorem govern_admits (D : SDoc) (out : Json) (ho : govern D = .ok out) : admitBlock D = .ok ()

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

/-- The chain's decoder reads a rule's name from the object as written (the names `addOver` writes). -/
theorem decodeNorm_name (re : VE.Readings.Wire.ReadingsEnvironment) (o : Json) (N : SoftNode)
    (h : VE.Readings.Wire.decodeNorm re o = .ok N) : HasStr N.name o

/-- Every string value of the answer is a string value of the document or of a governor's payload. -/
theorem govern_strings (D : SDoc) (out : Json) (ho : govern D = .ok out) (s : String) (hs : HasStr s out) :
    HasStr s D.doc ∨ ∃ g ∈ D.governors, HasStr s (payload g.effect)

/-- Scope introduces no symbol: for governors bound to the block, every string value of the answer is a string
    value of the document or the block. -/
theorem govern_no_new_symbols (D : SDoc) (hb : BlockBound D) (out : Json) (ho : govern D = .ok out) (s : String)
    (hs : HasStr s out) : HasStr s D.doc ∨ HasStr s D.block

/-- A frontier reach carries a unary effect only (until SC-5's addendum): a graph governor on it is refused. -/
theorem frontier_graph_refused (D : SDoc) (g : Governor) (hg : g ∈ D.governors) (hf : g.reach = .frontier)
    (he : graph g.effect = true) : (govern D).isOk = false

/-- The run path (1.5.8) answers exactly as `govern`, so every theorem about `govern` holds of it. -/
theorem governFast_eq (D : SDoc) : Pinned.governFast D = govern D

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

`govern_no_new_symbols` follows from `govern_strings` and `BlockBound`; draft 1 stated it without the binding, and
then it was false (F-sym). `decodeNorm_name` is the fact the proof needs about the chain's decoder: no merged module
states it, so SC-1a states and proves it in its theorem file, as a lemma about the merged decoder; it edits no
decoder file. W1's `VE.Norms.Wire.decodeNorm` reads `name` as the JSON string written, and soft's
`Phases.ruleFields` reads it through that same decoder.

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

/-- SC-1b's decoder binds the governors to the block as written. -/
theorem decodeScope_bound (front : Json) (D : SDoc) (h : Pinned.decodeScope front = .ok D) : BlockBound D

/-- SC-1b's decoder reads the layout of exactly the document's units, in order. -/
theorem decodeScope_layout (front : Json) (D : SDoc) (h : Pinned.decodeScope front = .ok D) :
    D.layout.map (·.id) = unitIds D.doc

/-- For a decoded document, every string value GOVERN writes is one of the document or of its scope block. -/
theorem decoded_no_new_symbols (front : Json) (D : SDoc) (h : Pinned.decodeScope front = .ok D) (out : Json)
    (ho : govern D = .ok out) (s : String) (hs : HasStr s out) : HasStr s D.doc ∨ HasStr s D.block

end VE.Scope
```

`decoded_no_new_symbols` is draft 1's claim, restated for the inputs it was meant for: it follows from
`decodeScope_bound` and `govern_no_new_symbols`, and with `scope_admission` it covers every `scope@0` document the
document mode answers. `decodeScope_layout` is
the layout's binding: every reach names the document's own units, while no layout string reaches the output, since
`patch` maps over `D.doc`'s units.

`scope@0` is one row of AR-10's profile-gate table (a wrapper at step 1b over the norms, norm-defaults, soft and
rights routes); the row carries the composition theorem `scope_admission` for every combination it newly admits,
and AR-10's generic lemma shows the table runs as written. `foldGovernors` applies 1.6's table with `governorStatus`.
The document mode calls the run path `governFast` (1.5.8), the function B1 measures; `scope_admission` is stated
over `govern`, and its proof rewrites the call with `governFast_eq`.

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

/-- Discourse's anchor checks are the moved body, on discourse's own anchors, definition spans and environment. -/
theorem discourse_anchorsOk_unchanged (D : VE.Discourse.DDoc) :
    VE.Discourse.anchorsOk D = anchorsOk D.K.anchors
      ((D.base.units.filter (fun x => decide (x.kind = .definition))).map (fun x => (x.start, x.stop)))
      (VE.Discourse.unaryPred D.E)

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

SC-3b's intent is unchanged: an assertion content (an array) under a plain narrowing or an own-free carve-out of an
`anchor` or `label` reach becomes `["implies", C, φ]` or `["implies", ["not", C], φ]`, closed conditions only, and
any other effect on an assertion stays `ScopeNotARule: <unit>`. The two denotation lemmas above are its meaning.
Its composition is not one paragraph's work: `baseObj`, `ruleUnits`, `affected`, the `ScopeNotARule` check of
`admitBlock` and `newContent` all exclude assertions or write norm wrappers today. SC-3b is therefore built only
after an approved addendum that specifies those functions' assertion cases and the matching preservation and
provenance statements (9.4).

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

### 5.7 SC-5 (frontier reaches; after SC-E1, lf-14d and its approved addendum, 9.4)

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

/-- One unit's rule with one effect applied, decoded by the chain's own decoder. -/
def composedRule (D : SDoc) (e : Effect) (u : String) : Except String SoftNode := do
  let o ← baseObj D u
  let o' ← applyEffect u e o
  VE.Readings.Wire.decodeNorm D.re o'

/-- `none` when the unit is not admitted or a resource limit stops the composed rule's decoding. -/
def fitAt (D : SDoc) (e : Effect) (u : String) : Option Bool :=
  match (baseObj D u).toOption.bind (fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption) with
  | none => none
  | some _ => match composedRule D e u with
    | .ok N' => some (Pinned.ruleTyped D.re N')
    | .error err => if err.startsWith "ResourceLimit" then none else some false

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

/-- Exhaustion is never evidence against a candidate: a resource limit leaves the unit unresolved. -/
theorem fitAt_limit (D : SDoc) (e : Effect) (u : String) (err : String) (h : composedRule D e u = .error err)
    (hr : err.startsWith "ResourceLimit" = true) : fitAt D e u = none

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

These are the statements of the frontier's parts. SC-5 is built only after an approved addendum (9.4) that, among
its obligations, wires the frontier into `govern` (as written, `coveredLayout` cannot call `validateFrontier`),
pins `Pinned.ruleTyped` (the chain's existing per-rule typing check) and `Pinned.jointPicks` (lf-14d's joint
choices read as a pick per frontier governor), and states `govern_provenance` and `govern_no_new_symbols` per
choice. Two repairs hold now, before the addendum: a resource limit in fitting is `none` (`fitAt_limit`, F13-r), and
a frontier reach carries a unary effect only (`frontier_graph_refused`).

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
| `ResourceLimit: scope governors` / `ResourceLimit: scope list names` | more than 256 governors / list names | `admitBlock` 1 |
| `DuplicateDeclaration: governor <id>` / `DuplicateDeclaration: list name <n>` | a repeated id or name | `admitBlock` 2–3 |
| `ScopeUnknownUnit: <unit>` | a governor's or registering unit, or a lead-in or item, not in the document | `admitBlock` 4, 6; reaches |
| `ScopeReserved: own` | a condition, and the vocabulary declares `own` | `admitBlock` 5 |
| `InvalidInput: scope@0 list_names.<n>.scope must be doc` | a list name with another `scope` than `"doc"` | `admitBlock` 6 |
| `NotALeadIn: <unit>` | a list reach or list name whose unit does not end with ":" or is not followed by an item | `admitBlock` 6; reaches |
| `ManifestMismatch: scope.list_names.<n>.units` | a list name's recorded units differ from the run | `admitBlock` 6; reaches |
| discourse's anchor texts, unchanged (`ResourceLimit: anchors`, `DuplicateDeclaration: anchor <a>`, `InvalidInput: anchors must form one tree`, `DanglingAnchor: <a>`, `DuplicateAnchor: <label>`, `InvalidInput: anchors <a>, <b> overlap`, `ManifestMismatch: anchors.<a>.exports`) | anchors that fail discourse's checks (1.2) | `admitBlock` 7 |
| `ResourceLimit: scope condition depth exceeds 64` | a condition deeper than 64 | `admitBlock` 8 |
| `ScopeOwnBound: <g>` | `own` under a binder | `admitBlock` 8 |
| `ManifestMismatch: scope.governors.<g>.unit` | a frame not on its lead-in; a unary or title governor over an anchor not on its heading, or over a label not on its item | `admitBlock` 8 |
| `ScopeReach: <g>` | a frame over another reach than a list or list name; a title over another reach than an anchor or label; a `precedes` or `yields` over a frontier reach | `admitBlock` 8 |
| `NotALabel: <unit>`, `ScopeUnknownAnchor: <a>`, `ScopeUnknownName: <n>`, `ScopeUnknownRule: <r>` | a reach that does not exist | reaches |
| `UnsupportedProfile: scope@0 frontier reach requires SC-5` | a unary governor over a frontier reach before SC-5 | reaches |
| `ManifestMismatch: scope.governors.<g>.units` | the recorded reach differs from the regenerated one | `admitBlock` 8 |
| `ScopeReadings: <unit>` | the governor's unit or a governed unit is the unit of a reading set | `admitBlock` 8 |
| `ScopeNotARule: <unit>` | a `frame`, `reguard` or `carve_out` covers a unit whose written content is neither a part nor a norm | `admitBlock` 8 |
| `ScopeForward: <w>: rule <r> has no later exception in <a>` | a forward declaration with no later exception (SC-4) | `admitBlock` 9 |
| `ScopeOrder: <unit>: <g1>, <g2>` | two unary governors on a unit that do not commute; two frames on a unit | `orderCheck`; composition |
| `ScopeNotARule: <unit>` | an effect on a unit whose content is not a part or norm (or lacks `guard`/`unless`) | composition |
| `ScopeOrphanPart: <unit>` | a part content no frame covers | composition; `govern` without governors |
| `InvalidInput: scope@0 parts of <unit> must be objects` | a frame part or item part that is not an object | composition |
| `ScopeConflict: <unit>: <key>` | a key written by both the lead-in and the item | composition |
| the chain decoder's own text | a composed rule the chain's decoder refuses (F1″) | `ruleTable`, or the chain |
| `ScopeNoEffect: <g>` | a graph governor whose reach has no other rule on the same predicate | graph step |
| `ResourceLimit: scope` | more than 8 frontier constituents (UNKNOWN) | SC-5 |
| a decoder's `ResourceLimit…` text on a candidate's composed rule | the candidate's unit is unresolved (`fitAt` is `none`), never failing (UNKNOWN) | SC-5 fitting |
| `UnresolvedScope: <g>: no candidate fits` / `UnresolvedScope: <g>: a unit of its only candidate is not admitted` | 1.7 | SC-5 |
| `AmbiguousScope: <g>: <candidates>` | two or more live candidates | SC-5 |

The texts join AR-13's typed codes if AR-13 has merged; the codes are the words before the first ":".

### 6.2 Order

`govern` reports the first fault in this order (1.5.7): the wire decoder; `admitBlock` steps 1 to 9, with or without
governors (step 6 per list name in block order: its scope, its registering unit, its run; step 7 discourse's anchor
checks in their own order; step 8 per governor in block order: depth, `ownSafe`, the effect's reach and unit, the
anchor or label unit, the recorded units, reading sets, units it cannot change; step 9, from SC-4, the forward
declarations in block order); with no governor, `ScopeOrphanPart` for the first part unit; otherwise `orderCheck` in
document order of units and order 1.4 of governors, composition of affected units in document order, `ruleTable`,
and `ScopeNoEffect` in order 1.4. A `ResourceLimit` is UNKNOWN for every dependent verdict, never a rejection, and in
fitting never evidence against a candidate (1.7).

## 7. Acceptance fixtures

### 7.0 How the values were obtained

"Computed" values come from `#eval` and `decide` in the scratch stub (4, 5 verbatim). Layout fixtures use the pilot
source's own bytes for each unit, shortened only inside sentences; each piece keeps its line structure (where its
line starts, its indentation, its marker, its trailing newlines), so `item`, `midLine`, `lead`, `label` and `para`
are those of the source. The pilot rule names, predicates and guards in the `govern` fixtures are stand-ins with the
pilot's shape; SC-1b's pilot fixtures compare against the translation itself (7.2). Each "exactly when" claim has a
fixture in each direction; the column "Direction" says which. Anchor fixtures carry the document's root anchor
`doc`, because `admitBlock` now runs discourse's anchor checks and they require one tree (draft 1's F8 anchors,
two children of a missing root, are refused: F8-tree). Each contract the statement review repaired has an executed
fixture: F-sym, F-meta and F-fg (7.1), F4-r3 and F4-c (7.4), F11-a (7.6), F13-r (7.7). Four of them are cases that
draft 1 gets wrong: F-sym (its statement is false there, computed), F13-r (its `fitAt` fixes the reach, computed
beside draft 2's), and, read directly off draft 1's definitions, F-meta (its `govern` returned the document without
admitting the block) and F11-a (its `admitBlock` required every anchor governor to sit on the heading).

**Checked on the full pilot layout (draft 4).** The layout fixtures above were computed on excerpts of the
pilot's bytes. Phase 1 (SC-M0, check C11) recomputed some of their results on the full pinned constitution,
184,893 B and 1,132 units, with an independent Python transcription of `ofSource`, `listRun` and `itemRun` (1.2,
4.1) in `research/scope/sc_m0_tally.py`, and they agree. C11 checks exactly these: F1's run from u0164.s02; F1‴
(u0166.s01 is not an item and not in that run); L1's u0164.s02 `midLine` and `lead` and u0165.s01–s07
`item = some 0`; F2's run from u0181.s02; F2′'s run from u0072.s02; F2″'s pilot half (`NotALeadIn: u0164.s01`);
F10's `itemRun` from u0073.s01. It does not check the other fields or fixtures of 7.1 and 7.5. L1's `para` values
agree after rebasing, outside C11: on the full layout u0164.s01–s02 have `para = 163`, u0165.s01–s07 `para = 164`
and u0166.s01 `para = 165`, which are L1's 1 and 2 counted from the excerpt's first paragraph. That is a second
implementation agreeing on the checked results, not a proof, and not the Lean stub; it shows the excerpts did not
hide a unit that changes those runs. B1 (7.2) runs on the same layout.

### 7.1 SC-1a (`Examples.lean` by `decide`/`rfl`; `tests/test_scope_lean.py`)

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| L1 | the layout of u0164.s01–u0166.s01 (hard constraints) | computed: u0164.s02 `midLine`, `lead`; u0165.s01–s07 `item = some 0`, `para = 1`; u0166.s01 `para = 2`, not an item | — |
| L1-p | `paraCounts` against draft 1's per-unit count, at every byte of the three pilot layouts (L1, F2, F2′) and of a synthetic layout with tab, CR and space-only blank lines | computed: equal at every position (`true` four times) | — |
| F1 | `listRun` from u0164.s02 | computed: `.ok [u0165.s01, …, u0165.s07]` | `listRun_iff` →, `listRun_ok_iff` → |
| F1-m | `mergeParts` of the frame `{"sign": false, "unless": [], "over": []}` and the item `{"name": "hc-cbrn-uplift", "predicate": "restricted_act_permitted", "guard": ["unary", "mass_casualty_weapon_uplift", ["var", 1]]}` (the one stand-in predicate of every F1 fixture) | computed: equal to the whole rule object (all six W1 keys) | `mergeParts_keys` |
| F1-g | `govern` with the frame governor `g1` over seven part units | computed: u0165.s01's content is `{"norm":{"guard":["unary","mass_casualty_weapon_uplift",["var",1]],"name":"hc-cbrn-uplift","over":[],"predicate":"restricted_act_permitted","sign":false,"unless":[]}}`; u0165.s07's likewise with `hc-csam` and `csam_generation`; u0164.s02 keeps no content | `govern_provenance` |
| F1′ | u0165.s03's part also writes `sign` | computed: `ScopeConflict: u0165.s03: sign` | `mergeParts_conflict` |
| F1″ | an item missing `predicate` | `govern` succeeds; the chain's decoder refuses the rule with its own text, computed on the norms chain: `fields do not match: expected [name, predicate, sign, guard, unless, over], got [guard, name, over, sign, unless]` (the soft chain's own text there) | — |
| F1‴ | u0166.s01 after the run | computed: not in the run (a new paragraph, not an item) | `listRun_iff` ← |
| F2 | u0181.s02 "Key questions include:" over u0182.s01–s05 | computed: `.ok [u0182.s01, u0182.s02, u0182.s04]`; u0182.s03 ("Or does it escape these mechanisms?") and u0182.s05 are mid-line continuations | `listRun_iff` ← |
| F2′ | u0072.s02 over u0073.s01–s10 | computed: `.ok [u0073.s01, u0073.s05, u0073.s08]`; the "+ Example:" sub-bullets s04, s06, s07, s09, s10 are depth 1 | `listRun_iff` ← |
| F2″ | a lead-in followed by prose; a unit not ending with ":" | computed: `NotALeadIn: x.s01`; `NotALeadIn: u0164.s01` | `listRun_ok_iff` ← |
| F-id | no governors, no part (a four-unit norm document); and no governors, no content, with a well-formed list name | computed: `govern` returns the document, equal as a value, both times | `govern_identity` |
| F-orph | no governors, seven part units | computed: `ScopeOrphanPart: u0165.s01` | `govern_orphan` |
| F-meta | malformed metadata with no governor, on the hard-constraint layout with no content (draft 1 returned the document each time): a list name recording six of the seven units; a list name with `scope` `"section"`; 257 list names; two root anchors (with SC-3a's checks) | computed: `ManifestMismatch: scope.list_names.the hard constraints.units`; `InvalidInput: scope@0 list_names.the hard constraints.scope must be doc`; `ResourceLimit: scope list names`; `InvalidInput: anchors must form one tree` | `govern_admits` |
| F-sym | **counterfixture**: `block = null`, the frame `g1` and a carve-out governor whose condition is `["unary", "invented", ["var", 1]]` | computed: `govern` succeeds; u0165.s01's `unless` is `[["unary","invented",["var",1]]]`; the output contains "invented", the document and the block do not. Draft 1's unrestricted `govern_no_new_symbols` is false here; `govern_strings` holds (the string is the governor's payload) and `BlockBound` fails, so `govern_no_new_symbols` does not apply | `govern_strings`, `govern_no_new_symbols` (its hypothesis) |
| F-fg | a `precedes` governor over a `frontier` reach | computed: `ScopeReach: gF` | `frontier_graph_refused` |
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
| F1-dec | F1-doc's front matter through `decodeScope` | the decoded governors' payloads are sub-values of the `scope` block, and the layout's ids are the document's unit ids in order; every string of `govern`'s answer is one of the document or the block | `decodeScope_bound`, `decodeScope_layout`, `decoded_no_new_symbols` |
| B1 | a `tools/bench` row: F1-doc's document, the full pinned constitution pilot (184,893 B, 1,132 units), through `ofSource` and `governFast` | a benchmark row with its baseline; never a timing assertion in the suite | `governFast_eq` (the bench runs the run path) |

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
| F4-r3 | F4 against row 3 of 2.2: the replacement wording's condition read instead as a narrowing (`["and", "own", C]`, the "only where" row), giving `G ∧ ((G ∧ K) ∨ L)` | computed by `decide` in F4's model: the replacement guard `(G ∧ K) ∨ L` holds (`true`), the narrowing reading does not (`false`), so "In place of" decides a verdict | — |
| F4-c | carve-outs survive the replacement: u0173.s01's `reguard` on a rule whose `unless` is `[T]` (`T` = tested by Anthropic), and F4's model with and without `T` | computed: the composed `unless` is still `[["unary","tested_by_anthropic",["var",1]]]`; by `decide`, `(G ∧ K ∨ L) ∧ ¬T` holds without `T` (`true`) and not with it (`false`) | `reguard_applies` (`¬ anyF N.carveOuts`) |
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
| F8 | UDHR u109 "## Article 29" over u110–u112 as a title, Articles 29 and 30 under the root anchor `doc` | computed: the anchor reach is `[u110, u111, u112]`, the heading `u109`; `govern` returns the document unchanged (equal as a value) | `title_identity`, `anchorReach_iff` → |
| F8-tree | F8 with draft 1's anchors: Articles 29 and 30 as children of a missing root | computed: `InvalidInput: anchors must form one tree` (discourse's text, from `admitBlock` step 7) | `discourse_anchorsOk_unchanged` (discourse's anchor fixtures also pass unchanged) |
| F8-out | u109 (the heading) and u113 (Article 30's heading) | not in Article 29's reach | `anchorReach_iff` ← |
| F9′ | `## Instructable behaviors` | a title, as F8 | `title_identity` |
| F10 | u0073.s01 "* **There’s no operator prompt:** ..." | computed: the label reaches `[u0073.s01, u0073.s02, u0073.s03, u0073.s04]` (the item, its two continuing sentences, its "+ Example:" sub-bullet), not u0073.s05; u0073.s04 is not a label (`NotALabel: u0073.s04`, no bold label); u0182.s02's label reaches `[u0182.s02, u0182.s03]` | `itemRun_iff`, `label_reach_iff` both |
| F9 (SC-3b) | `## When there is no operator prompt` over two rules, a narrowing over the anchor | computed: both guards become `["and", ["top"], ["unary","no_operator_prompt",["var",1]]]`; the rule under the next heading is unchanged; the same governor on a non-heading unit is `ManifestMismatch: scope.governors.g9b.unit` | `anchor_reach_iff` both |
| F9-a (SC-3b) | a narrowing over an anchor holding an assertion `φ` | the content becomes `["implies", C, φ]` | `assertion_restrict_denote` |

### 7.6 SC-4

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F11 | "Notwithstanding section 3, every operator may share." over rules `r3a` (same predicate) and `r3b` (another) | computed: `r9`'s `over` is `["r3a"]`; `r3b` adds nothing | `precedes_edges` |
| F11-a | F11's wording recorded with reach `{"anchor": "sec3"}`, the governor on r9's own unit, outside section 3 (end to end through `govern`) | computed: `r9`'s `over` is `["r3a"]`; as `yields`, `r3a`'s `over` is `["r9"]`; a narrowing over the same anchor on the same unit is still `ManifestMismatch: scope.governors.g11n.unit` | `precedes_edges`, `yields_edges` |
| F11-y | the same as `yields` | computed: `r3a`'s `over` is `["r9"]` | `yields_edges` |
| F11′ | the same over `r3b` only | computed: `ScopeNoEffect: g11` | `no_effect_refused` |
| F11-u | an unknown rule name | computed: `ScopeUnknownRule: r7` | — |
| F11″ | edges that close a cycle | W1's `DependencyCycle`, unchanged | — |
| F12 | u0047.s05–s06 "That said, we discuss some exceptions to this in the section on “broad safety” below." | not recorded as a forward declaration (no rule is named): u0047.s06 stays UNFORMALISED with residual `UnresolvedScope`, never a guessed edge | — |
| F12-f | a forward declaration on h.s02 for rule `r1` in section `sec` | computed: with a later rule whose `over` is `["r1"]`, `.ok ()`; without, `ScopeForward: h.s02: rule r1 has no later exception in sec` | `forward_exception_sound`, `_complete` |
| F12-f0 | F12-f's failing declaration in a document with no governor | `ScopeForward: h.s02: rule r1 has no later exception in sec` from `govern` (`admitBlock` step 9), never the document | `govern_admits` (at SC-4) |

### 7.7 SC-5

| Id | Fixture | Expected | Direction |
|---|---|---|---|
| F13 | u0046.s02 "This is not a strict hierarchy, however." in its section | computed frontier, the same with and without the root anchor `doc`: `[[u0046.s01], [u0045.s01, u0045.s02, u0045.s03], [u0044.s02, …, u0046.s01]]`: the previous sentence, the ordered list, the section's earlier units (three, not two: 9.1); every unit unadmitted, so all three live: `AmbiguousScope`; in translation one reading set with three candidates | `frontier_ambiguous` |
| F13-r | **counterfixture**: "Rule 1. … Rule 4. … This applies only where the user is an adult." with r1's base guard 64 levels deep (it decodes) and r4's `["top"]`; candidates `[r4]` (fits) and `[r1, r4]` | computed: r1's composed rule is `ResourceLimit: formula depth exceeds 64`, so `fitAt` at r1 is `none` (draft 1: `some false`); frontier `[[r.s02], [r.s01, r.s02]]`; with r4 fitting, `AmbiguousScope: g13: [[r.s02], [r.s01, r.s02]]`, never `.ok [r.s02]` (draft 1's answer, computed beside it): the reach is not fixed by exhaustion, and under the choice `[r1, r4]` the chain's decoder answers `ResourceLimit` for r1, UNKNOWN for every dependent verdict | `fitAt_limit`, `fitOf_fails_iff` |
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
| `Pinned.governFast` | SC-1a's own definition: the run path (1.5.8) | written by SC-1a; its contract is `governFast_eq` |
| `VE.Readings.Wire.ReadingsEnvironment`, `VE.Readings.Wire.decodeNorm` | the chain's decoder (merged) | as merged; for a document without `readings@1`, SC-1b builds the same record from the chain's environment decoding |
| `Pinned.ruleTyped` | the chain's per-rule typing check | SC-5's addendum |
| `Pinned.jointPicks` | lf-14d (`VE.Discourse` joint choices in Lean) | SC-5's addendum |
| `Pinned.splitRules`, `Pinned.sentence` | AP-3's `VE.Acts.SplitMap.rules`; SC-1c's `VE/Scope/English.lean` | SC-1c |
| `Pinned.parseGovernor`, `Pinned.renderGovernor` | english-lean's catalogue | SC-7 |
| `Pinned.rightNames`, `Pinned.withReach` | rights@0 (`VE.Rights.Limitation.scope`) | SC-6, after S2b |
| attitude guard nodes | AT-3a, inside W1's `decodeNorm` and soft's `decodeSoftNorm` | SC-2's claim |
| AR-10's profile-gate row and mode registry | AR-10 | SC-1b, SC-1c |

### 8.2 Limits

Governors ≤ 256; list names ≤ 256 (the governor limit's, enforced by `admitBlock` step 1); anchors ≤ 1,024
(discourse's); condition depth ≤ 64; frontier constituents ≤ 8; reading-set candidates ≤ 8 (one choice per frontier
governor). Every limit is `ResourceLimit`, UNKNOWN; a decoder's limit met while fitting a candidate leaves it live.

### 8.3 Files, generated files and the audit

As the plan's batches list them; SC-3a's shared files now include `lean/VE/Discourse/WellFormed.lean` (the anchor
checks and their helpers move out of it, 1.2), whose line in `lean/VE/Route/frozen-sources.sha256` is regenerated
with `Access.lean`'s. SC-1b adds the benchmark row B1 to `tools/bench`. Generated files (schemas,
`tools/gate-collection.json`, `lean/checkers.lock`, Python's profile data, `lean/VE/Route/frozen-sources.sha256`,
route cases) are regenerated with `tools/regen_generated.py --write`, never by hand. Each theorem gets one
`#print axioms` line in `lean/VE/Audit.lean` (or AR-1's generator); the audit allowlist is unchanged.

## 9. Choices, the review's answers and corrections, and the addenda

### 9.1 Where the drafts chose between readings of the plan or of the review

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
   plan already does for list names; they are checked by discourse's own checks, moved (1.2; 9.2 question 1).
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

Draft 2's choices, where the review allowed more than one repair:

14. **The run path is `governFast` with `governFast_eq`** (1.5.8), of the two repairs the review allowed (a reach
    table that `coversU`, `frameOn` and `governorsOf` read, or a proved-equal fast form). The statement functions
    and every theorem about them stay as written; only the run path changes.
15. **The source binding is stated both ways.** The reviewers' last rounds crossed, each conceding the other's form:
    the payload form (`govern_strings`, no hypothesis) and the binding form (`govern_no_new_symbols` with
    `BlockBound`) are both stated, the second a corollary of the first, and SC-1b proves the binding for decoded
    documents (`decodeScope_bound`, with `decodeScope_layout`).
16. **Forward declarations are the last step of `admitBlock`** (step 9), which puts them before the identity
    shortcut and inside every existing `admitBlock D = .ok ()` hypothesis, so no theorem's statement changes at SC-4.
17. **The anchor checks' generic helpers move with the bodies** (`req`, `runAll`, `allOk`, `dupOf`, `spanIn`,
    `spansDisjoint`, 1.2), the only way the bodies can sit below `Access.lean` in the import graph.
18. **`decodeNorm_name` is stated in scope's theorem file**, about the merged decoder, which no merged module states;
    no decoder file is edited (5.1).
19. **A list name's `scope` must be `"doc"`** (checked, no longer ignored): of Astra's two options, scoped lookup or
    the wire restricted to the document scope, the review agreed on the second until scoped lookup exists.
20. **The addendum obligations of SC-3b and SC-5**, which the review asked to record here, are listed in 9.4, beside
    the gate they set.

### 9.2 Questions for the statement review, answered

1. *Anchors in scope's block: discourse's `anchorsOk` on a manifest view, or the check bodies moved into
   `VE.Layout`?* **Moved** (both reviewers, round 3). `anchorsOk` takes a `DDoc` with `E`, `base`, `K`, `sourceId`,
   `text`, `sets`, `status`, `prose`, `files` and `nouns`, and its export check reads unit kinds from
   `D.base.units`, so a view would have to invent those values. SC-3a moves the bodies beside `within` (1.2, 4.1),
   with `discourse_anchorsOk_unchanged`; `lean/VE/Discourse/WellFormed.lean` joins SC-3a's shared files (8.3).
2. *Any-depth `"own"` with the reserved name.* No finding: Fable's round 1 accepted `own`, `ownSafe` and `Commutes`,
   and Astra raised none. Draft 1's choice stands.
3. *The status rule of 1.6.* No finding: Fable's round 1 accepted the statuses, and Astra raised none. It stands.
4. *A statement over AT-3a's decoder in scope.* Not raised. 5.4 stands: attitudes' decoder theorems own what the
   attitude words mean.

### 9.3 Corrections from the statement review (draft 2)

The review (`manage-agents/debates/scope-spec/`, round 3, both reviewers CONVERGED on FIX) agreed on this set of
corrections; draft 2 applies each, and nothing else changes.

| # | Finding (who raised it) | Correction | Where | Fixture |
|---|---|---|---|---|
| 1 | `govern_no_new_symbols` is false for an unrestricted `SDoc`: a decoded governor list is not tied to `block` (Astra) | `payload`, `BlockBound`; `govern_strings`; `govern_no_new_symbols` takes `hb : BlockBound D`; `decodeNorm_name`; SC-1b proves `decodeScope_bound` and `decodeScope_layout`, and from them `decoded_no_new_symbols` | 1.8, 4.2, 5.1, 5.2 | F-sym, F1-dec |
| 2 | Without governors `govern` returned before `admitBlock`: malformed metadata was accepted, and SC-4's forward checks were bypassed (Astra) | `govern` admits the block first; `govern_identity` and `govern_orphan` take `admitBlock D = .ok ()`; `govern_admits`; forward checks are `admitBlock`'s last step | 1.1, 1.5.7, 1.9, 4.2, 5.1, 6 | F-meta, F12-f0 |
| 3 | The 256-list-name limit was advertised, not enforced (Astra) | `admitBlock` step 1, `ResourceLimit: scope list names` | 4.2, 6.1, 8.2 | F-meta |
| 4 | `ContentName.scope` was ignored (Astra) | must be `"doc"`, else `InvalidInput` (step 6) | 3, 4.2, 6.1 | F-meta |
| 5 | Anchor validation had no owner (9.2 question 1; both) | discourse's checks move to `VE.Layout`, `discourse_anchorsOk_unchanged`, `admitBlock` step 7; fixtures carry the root anchor | 1.2, 4.1, 4.2, 5.5, 7.5, 8.3 | F8-tree |
| 6 | `admitBlock` required every anchor or label governor on the heading or item, so "Notwithstanding section 3" could not reach by anchor (both) | the check applies to unary and `title` effects only; the authoring row is the in-rule form | 1.3, 2.2, 4.2, 6.1 | F11-a |
| 7 | Rows 3 and 4 of 2.2 gave one sentence two blocks, since row 4's sentence is an instance of row 3's template (both); the first proposed fix, "apply exactly where", would be false, since carve-outs survive a replacement (Astra) | row 3 for conditions that do not mention "its kind"; row 4 is "In place of their own condition, …", paraphrased as a guard replacement whose carve-outs still apply | 2.2 | F4-r3, F4-c |
| 8 | The precedence and carve-out paraphrases did not follow W1 2.3 and 2.5 (Astra) | "Wherever rule 9, or a rule that takes precedence over it directly or through other rules, applies, no rule of section 3 decides on that act."; the carve-out paraphrase names the predicate's default sentence | 2.2 | — |
| 9 | `fitAt` read every composed-decoder error, `ResourceLimit` included, as `some false`, so exhaustion could eliminate a candidate (Astra) | `composedRule`; a `ResourceLimit` is `none`; `fitAt_limit` | 1.7, 5.7, 6 | F13-r |
| 10 | Graph effects cannot be fitted: `applyEffect` treats them as identity and fitting lacks the governor's own rule (Astra) | a `frontier` reach carries a unary effect only (`ScopeReach`); `frontier_graph_refused`; lifting it is an SC-5 addendum obligation | 1.3, 1.7, 4.2, 5.1, 9.4 | F-fg |
| 11 | `blankLinesBefore` and `covered` are quadratic and cubic on the 1,132-unit pilot (Fable) | `paraCounts`, one fold; the run path `governFast` with `governFast_eq`; a pilot benchmark row | 1.2, 1.5.8, 4.1, 5.1, 7.2, 8.1 | L1-p, B1 |
| 12 | SC-5's step "replace `coveredLayout`'s frontier case by `validateFrontier`" does not typecheck (Fable) | recorded as SC-5 addendum obligations | 4.2, 5.7, 9.4 | — |
| 13 | SC-3b cannot extend `baseObj` alone: admission, `ruleUnits`, `affected` and `newContent` exclude assertions or wrap them as norms (Astra) | SC-3b is gated on an approved addendum | 5.5, 9.4 | — |
| 14 | F1-m and F1-g used different stand-in predicates (Fable) | `restricted_act_permitted` throughout, F1-m recomputed | 7.1 | F1-m |
| 15 | The plan disagreed with the spec on the Boolean `sign`, the status rule and F13's candidates (Astra) | plan draft 3 synced, with one stand-in predicate | the plan | — |

### 9.4 Addenda required before SC-3b and SC-5

Each addendum is a spec section with its own statements and fixtures. It goes through the statement review and is
approved before its batch is built. SC-1a, SC-3a and the other batches do not wait for either.

**SC-3b (assertion targets).** It specifies:
1. the assertion cases of `baseObj` (an assertion under a plain narrowing or an own-free carve-out of an `anchor` or
   `label` reach becomes `["implies", C, φ]` or `["implies", ["not", C], φ]`, closed conditions only);
2. the assertion cases of `ruleUnits` (or a separate list of governable units), of `affected`, and of the
   `ScopeNotARule` check of `admitBlock`;
3. `newContent` writing an assertion back as an assertion, never in a norm wrapper;
4. the matching preservation and provenance statements for assertion units (`govern_preserves`,
   `govern_provenance`, `govern_strings`), with F9-a both ways.

**SC-5 (frontier reaches).** It settles:
1. *The governor parameter.* `coveredLayout : Reach → …` cannot call `validateFrontier D g`, which needs the
   governor.
2. *The dependency cycle.* That call would recurse through `fitAt → baseObj → frameOn → coveredLayout`, and no
   `mutual` is allowed. The addendum fixes the order, for example validating before `govern` and handing it only
   `fixed` reaches.
3. *The empty manifest.* An unfixed frontier governor records `units = []`, so it fails `admitBlock`'s
   `us == g.units`. The addendum fixes what is recorded and compared.
4. *Resource uncertainty per choice.* `fitAt_limit` holds now. Per choice, a composed rule that meets a decoder
   limit leaves every dependent verdict UNKNOWN, and F13-r stays: exhaustion never makes a competing candidate the
   unique reach.
5. *Graph fitting.* Frontier reaches stay unary-only (`frontier_graph_refused`), and the addendum enforces that
   before any frontier reach becomes an internal `fixed` reach: after `fixAt`, `admitBlock` sees a `fixed` reach,
   which it does not refuse. Lifting the restriction needs fitting that receives the governor's own rule and
   evaluates graph effects, with its own theorems and fixtures.
6. *The pins.* `Pinned.ruleTyped` and `Pinned.jointPicks` are pinned. `govern_provenance` and
   `govern_no_new_symbols` are stated per choice, through `governAt`, and `scope_choices` over lf-14d's joint set.

### 9.5 Correction from the confirmation round (draft 3)

The confirmation round on draft 2's diff (`manage-agents/scope-p3ver1.final.md`) found every 9.3 correction applied
and no unrelated change, and one inconsistency; draft 3 corrects it, and nothing else changes.

| # | Finding | Correction | Where | Fixture |
|---|---|---|---|---|
| 16 | 1.5.8 makes `governFast` the run path, but the plan's SC-1b had the document mode call `VE.Scope.govern`, so the service would run the cubic path while B1 measured `governFast` | the document mode calls `governFast`; `scope_admission` keeps its statement over `govern`, and its proof rewrites the call with `governFast_eq` | 1.5.8, 5.2, plan SC-1b | B1 |

### 9.6 Phase-1 results (draft 4)

Phase 1 (SC-M0, [docs/research/scope-phase1.md](../research/scope-phase1.md); evidence in
`docs/research/evidence/scope/`) recounted the pinned ledgers from the source bytes with the layout of 1.2. Plan
draft 5, 5.0, records every check with its verdict and what it gates. What bears on this spec:

- **Confirmed, no change.**
  - The layout definitions: the fixtures of 7.1 and 7.5 over the pilot hold on the full layout (7.0).
  - The status rule of 1.6 on the pilot: exactly one lead-in, u0164.s02 (22 B), has a wholly admitted run, so F1-doc
    is the only lead-in whose `governorStatus` is OPEN on the pinned run (C12).
  - F12 and the absence of far precedence: no unit says "notwithstanding", and "subject to" occurs in 4 units, none
    a precedence wording; no heading in either source is a When/If clause, so F9 stays synthetic.
  - The 22 restrictive-connective units, the frozen part of SC-E1's corpus (plan SC-E1), are listed by id in
    `scope-tally.json`.
- **Facts the spec now states.** `item` counts every list marker (1.2: 182 units on the constitution). No colon
  lead-in of the pilot is `NotALeadIn` (1.2).
- **Open question for SC-4's section, not decided here.** u0123.s03 ("Operators cannot instruct Claude to ...", 351
  B, OPEN, six limited acts in the source) limits three OPEN permissions, u0062.s01, u0123.s01.p1 and
  u0123.s02.p1 (613 B). The pinned translation copies its six limits into each permission as open terms (18 copies)
  and records `scoped_by_source: u0123.s03`. Act-phrases' AP-3 does not give six rules: its A14 gives **five
  prohibitions plus one explicit residual**, because "provide false information that could deceive the user" holds
  the clause word *false*, which `acts@0` refuses even in a fixed phrase. So five limits have a rule that
  `VE.Acts.SplitMap` (1.8) can name and an act phrase a condition can hold; the sixth has neither. Two readings fit
  the governors of 1.3 for the five, and they differ only where W1's same-predicate rule applies:
  1. a governor on u0123.s03 with a `carve-out` whose condition is the five limited acts and whose reach is `rules`,
     naming the three permissions; or
  2. precedence: the permissions yield to the five prohibitions, written as `precedes` on u0123.s03 over a `rules`
     reach naming the permissions (W1 precedence, `precedes_edges`), so the prohibitions' `over` names them.

  In both, the five prohibitions are named through `VE.Acts.SplitMap`, and the residual limit is not in the governor's
  effect: it stays where the pinned translation has it, one open term in each permission (3 of the 18 copies), and
  the residual stays recorded as AP-3's, never folded into the condition or guessed as a rule. F15's expected values
  therefore name five acts or five rules and the residual's three surviving copies. Either reading needs only
  definitions and statements already here (`carveOut_applies` with a `rules` reach; `precedes_edges`), so no
  statement waits on it. SC-4's section chooses, and the candidate becomes fixture F15 with computed values. If
  AP-3's residual is later admitted, F15 gains the sixth act then, and not before. The plan's cross-plan issue 1
  (u0123.s03 is also AP-3's A14) is the DRI's; until it is answered F15 is a candidate only.

## 10. Review checklist

- [ ] One reading: every wording of 2.1 and 2.2 maps to one block; ambiguity becomes a reading set or a refusal.
- [ ] Lean owns meaning: no effect is decided in Python; every effect's meaning is the chain's decoder's (5.4).
- [ ] One owner per piece of logic: no rule-field list in scope; containment moved, not copied; split maps and pack
      origins read, not re-derived; the wording table in Lean.
- [ ] Preservation is expressible and strong (`govern_identity` after admission, `govern_admits`,
      `govern_preserves`, `govern_strings`, `govern_no_new_symbols` under `BlockBound`).
- [ ] Every hypothesis a statement needs is stated and discharged where the input arises (`BlockBound` by
      `decodeScope_bound`; `admitBlock D = .ok ()` by `govern_admits`).
- [ ] Precedence is a graph step with provenance (`govern_provenance`'s edges, `precedes_edges`, `yields_edges`),
      and a graph governor may sit outside its anchor (F11-a).
- [ ] `Commutes` is syntactic and conservative; everything else is `ScopeOrder`.
- [ ] Three-valued `Fits`; unresolved singletons stay unresolved; overflow is UNKNOWN, never truncated; exhaustion
      in fitting is UNKNOWN, never evidence against a candidate (`fitAt_limit`, F13-r).
- [ ] Every "exactly when" claim has a fixture each way (7, column "Direction").
- [ ] Every paraphrase follows W1's meaning (2.2: precedence per W1 2.3 and 4.2, carve-outs naming the default per
      W1 2.5) and no sentence has two blocks (rows 3 and 4, F4-r3).
- [ ] The run path is fast and proved equal (`governFast_eq`, `paraCounts`, B1).
- [ ] Honest limits: translation effects are recorded claims; SC-E2 is proxy evidence; the 263 B claim waits for
      AT-3a; SC-3b and SC-5 wait for their addenda (9.4).
- [ ] Every statement elaborates (stub, Lean v4.24.0, re-elaborated for draft 2), and each repaired contract has an
      executed fixture (9.3); nothing is proved yet.
- [ ] The layout results C11 checks hold on the full pilot layout, not only on excerpts (7.0); draft 4 changes no
      statement, so the stub was not re-elaborated for it.
