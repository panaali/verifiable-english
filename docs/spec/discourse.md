# Discourse and cross-reference (`ve.discourse@1` over `ve-document@2`): names, anaphora, descriptions, document references and correlated readings

> Status: item-1 specification, draft 2 (2026-09-28). Draft 1 was written from [discourse-PLAN.md](discourse-PLAN.md)
> as revised by the converged Astra/Fable debate (`manage-agents/debates/design-discourse/{astra,fable}.md`, round 2,
> edits J1 to J8) and the lead's additional input recorded in that debate's `TOPIC.md` (document names, validity
> claims by fingerprint, the truth boundary). Draft 2 applies the converged Astra + Fable statement review of draft 1
> (`manage-agents/debates/discourse-spec/{astra,fable}.md`, rounds 1 to 3, verdict FIX: typed competitors and the
> corrected uniqueness statement, explicit target representations, nested mentions, the owning reading set, the three
> adapters to the frozen interfaces (profile stripping, the two carriers of a presupposition, citation extension to a
> compatible joint choice), import integrity separated from admission outcome with rejection distinguished from
> UNKNOWN, exact theorem contracts, corrected boundary fixtures, and the natural-view difference). It is the statement
> under the Astra + Fable item-1 review that gates sequences 2 to 5 of the plan (PLAN-EXPAND2 rule 10); convergence on
> the repair list is not a PASS for these files, and both reviewers re-review the complete amended gate (definitions,
> adapter contracts, theorem statements and fixtures together, with their consistency with the plan) before sequence
> 2 starts. Sections 3.5, 4 to 6 and 9 are the statements under review; section 13 lists every point where this
> draft chose between readings of the plan. Theorem statements and fixtures are implementation obligations, not
> claims of completed proofs or tests. Inputs: [document.md](document.md) (W2), [norms.md](norms.md) (W1),
> [soft-norms.md](soft-norms.md) (the soft route), [lean/VE/Definitions/STATEMENTS.md](../../lean/VE/Definitions/STATEMENTS.md)
> (W3), [natural-view.md](../natural-view.md), [VISION.md](../../VISION.md) including its self-reference boundary
> (branch `docs/self-reference`, commit `da8d8e2396cb`, 2026-09-28), `lean/VE/Route/{Admission,Readings,Gate,Wire}.lean`,
> `lean/VE/Definitions/Bundle.lean`, `lean/VE/Norms/Replay.lean` (the profile-stripping pattern),
> `lean/VE/English/Statements.lean`, `ve/document.py`, `ve/readings.py`, `ve/english.py`, the pinned constitution
> run `20260927T1800Z` and the UDHR run `20260927T1800Z`. Nothing here changes a frozen contract, a `ve-document@1`
> identity, a P0/W1/W3 theorem statement or a checker function.

## 0. Scope, one paragraph

A reference is resolved **before** anything is checked, into an explicit typed target recorded in a versioned
manifest, and the checker sees only closed formulas of the existing logic. "It", "this service", "such", "the
former", "her manager", "they", "as defined in section 2", "Article 29", "by clause 2.1", "this document" and "the
above document" each become one of seven target kinds (entity, predicate, source unit, anchor, rule, claim,
document); the kinds never coerce into one another; names and section numbers are display labels, never identities.
Acceptance of a sentence requires exactly one derivation and one reference assignment, modulo declared aliases,
yielding a closed typed formula `A`; the type check is the only filter on competing derivations and assignments,
and the recorded targets are the comparison point, never a filter; the checker regenerates that assignment from
source plus manifest and rejects anything stale, missing, colliding, ill-typed or inaccessible. A quantifier's
witness never becomes a name: the
same-witness reading of "A service is deployed. It is reviewed" is one fused assertion bound to both source spans.
A definite description exposes existence and uniqueness as formulas over equality; a document name is an ordinary
declared constant; a validity claim about a document is a checker verdict computed independently of the claiming
sentence, and a document may not certify its own truth. Correlated reading choices are enumerated jointly under
declared compatibility constraints, never as independent products. What this buys, exactly: existing W2 statuses,
W1 rule identities, W3 declarations and citations, P0 identities and every existing theorem are reused unchanged;
the new obligations (section 9) are about resolution, elaboration, compatible choices and model correspondence, and
no coverage gain is claimed until a rerun measures one.

In this specification: the manifest and its target kinds (1), the English (2), the wire form, identity and the
profile adapter (3), the semantics of accessibility, resolution, elaboration, descriptions, fusion, document names
and joint choices (4), what stays frozen (5), modes and the reviewed presentation (6), the report (7), diagnostics
(8), the Lean definitions and every theorem as a statement (9), the item-1 acceptance fixtures (10), limits (11),
the review checklist (12) and the resolved choices (13).

Out of scope, by the plan: any new logical operator or checker rule; bare `this`/`that` referring to a claim or an
action as a term (attribution and speech-act semantics own it); collective, generic and unknown-group plurals;
"respectively"; incorporation of a cited article's content as premises ("under Article 29"); legal authority and
override semantics; rights, soft-weighing, modality and causation co-blockers on the pinned units; the surface
registrations (sequence 2), the readings/IDE actions (sequence 4) and the integration gates (sequence 5) beyond the
wordings and fixtures fixed here.

## 1. What a discourse manifest is

### 1.1 Format and profile

`ve.discourse@1` is a profile enabled in the environment (`profiles` sorted, as `norms@0`). Unlike `norms@0` it is
not in the frozen profile registry (`lean/VE/Route/Gate.lean`, `registry`), so the frozen gate would reject it
(`UnsupportedProfile: Unsupported profile ve.discourse@1`): the discourse wrapper validates the profile itself and
strips it from the list and from the environment JSON before every frozen call (the profile adapter, 3.5), exactly
as `lean/VE/Norms/Replay.lean` (`baseEnvironmentJson`) strips `norms@0` for the base environment. Its manifest is the
`discourse` block of the front matter of a `ve-document@2` document. A `ve-document@1` document has no such block
and is rejected today by `ve/document.py` with `unknown document metadata` when one is present; the `@2` loader
accepts `format: "ve-document@1"` inputs and delegates them unchanged to the `@1` path (theorem `format1_unchanged`,
9.6), so no existing identity, status or verdict moves. `ve-document@2` is `ve-document@1` plus the `discourse`
block plus the reading-group and constraint fields of 1.5; every other field keeps its `@1` meaning. The profile
requires the format (`UnsupportedProfile: ve.discourse@1 requires ve-document@2`) and the format requires the
profile whenever the block is present.

### 1.2 Anchors

```text
anchor   := {id, kind ∈ {document, section, clause, item, article}, parent (an anchor id, absent for the root),
             label (display text: "2", "2.1", "Article 29"), span [a, b) in prose bytes, edition (optional),
             exports (optional: the declared predicate names whose W3 declarations this anchor exports, 4.2)}
```

Anchors form one tree by `parent`; a child's span lies inside its parent's; sibling spans do not overlap; the root
spans the whole prose. Labels are display only: two anchors may not share a label under one parent
(`DuplicateAnchor: <label>`), and a label never identifies a target. `edition` names the edition of an external
document an anchor belongs to (an import, 1.6); an anchor of an import without a pinned edition is
`AmbiguousEdition: <document>`. `exports` is the explicit representation of "the declarations an anchor exports":
each name is a predicate declared in `E` at `definitions_version` whose W3 definition unit lies inside the anchor's
span (`ManifestMismatch: anchors.<id>.exports` otherwise); a `definition_ref` resolves only through this list.
Section scope is explicit (an anchor), never inferred from typography.

### 1.3 Registered names and aliases

```text
name     := {constant, display, scope (an anchor id), aliases (display strings)}
```

A registered name binds a declared constant of the environment (a `Const` symbol) to its display form ("the API",
"Alice") and to the anchor within which mentions may use it. The constant's sort is its declaration in `E`
(`E.constants c`); the manifest never restates it. The vocabulary overlay of the natural view already declares
display forms (`natural-view.md`, `constants` entries); the manifest adds the scope and the aliases. Two names with
one display string in overlapping scopes are `DuplicateDeclaration: name <display>`. Aliases are declared per
constant; "modulo declared aliases" in 4.3 means: two assignments that differ only in which alias of one constant a
mention used are the same assignment. Predicate synonyms remain W3 alias definitions (VISION, "Synonyms and varied
wording"); this profile declares no predicate alias of its own.

```text
content_name := {name (display text: "Claude's principal hierarchy"), units (ordered source unit ids), scope (anchor id)}
```

A content name is a registered display name for content (a list of units), the explicit representation of "a
registered content name" (2.5): it is not a constant, never a term and never a premise; a `unit` target may cite it
(`content_name`), and a later "it"/"this <name>" whose intended referent is that content resolves to the `unit`
target of those units, not to an entity. Two content names with one display string in overlapping scopes are
`DuplicateDeclaration: content_name <display>`.

### 1.4 Mentions, forms and target kinds

```text
mention  := {id, unit (the source unit containing it), span [a, b) in prose bytes, form, target,
             restriction (definite descriptions only, 4.5), reading (definite: assertive | presuppositional;
             plural: distributive),
             presupposition_unit (presuppositional definites only: the id of the asserted unit carrying U(D), 4.5)}
form     ∈ {pronoun, demonstrative, definite, ordinal_pair, such, possessive, plural, section_ref,
            definition_ref, document_name, citation, navigation}
target   := {kind, name (optional), version (optional),
             members (kind entity, form plural: the ordered list of constants, n ≥ 2, distinct),
             pair (kind entity, form ordinal_pair: the identified ordered pair [c₁, c₂]; name is the selected member),
             units (kind unit: the ordered list of source unit ids), content_name (kind unit, optional: a registered
             content name, 1.3, whose units equal `units`)}
```

| Target kind | The target is | Accessible when (4.2) | What the mention elaborates to |
|---|---|---|---|
| `entity` | `name`: a declared constant, or `binder:<i>` for a local binder of the same sentence or rule; for `plural`, `members`; for `ordinal_pair`, `pair` with `name` the selected member | the constant is registered with a scope containing the mention's unit; a binder only inside its own sentence/rule; every member of a list or pair individually | the constant term (of its declared sort); the bound variable; the members (a distributive conjunction, 4.4); the selected member |
| `predicate` | `name`: a declared unary or binary predicate | declared in `E` at `definitions_version`; for `definition_ref`, in the `exports` of the anchor named; for `such`, the explicitly bound property (4.2) | the predicate symbol (for `such`, the copied property applied at its argument sort; for `definition_ref`, the pinned declaration) |
| `unit` | `units`: an ordered list of source unit ids, optionally under a `content_name` | every id exists and the content name (if any) lists exactly these units; forward references allowed | nothing: a location; content named for display |
| `anchor` | `name`: an anchor id | exists; forward references allowed | nothing: a location |
| `rule` | `name`: a W1 stable rule name | a norm unit of the document | the rule (W1 exception/precedence references, unchanged) |
| `claim` | `name`: a lemma meaning id in the document's bundle | strictly earlier in the bundle (`Bundle.checkLemma`) | a W3 citation (`cite:` leaf) |
| `document` | `name`: a document name (1.6) | declared | the document constant (a term); or the target of a validity claim (4.7) |

Kinds never coerce: a `unit` or `anchor` target is never a term, a `document` target is never a predicate, a `claim`
target never enters as an assumption without its transitive leaves. A mention whose form and target kind do not fit
(a `pronoun` targeting an `anchor`, a `section_ref` targeting an `entity`) is `TargetKindMismatch`. A `demonstrative`
or `pronoun` whose intended referent is a claim or an action as a term is `UnsupportedTarget: <mention>: claim` in
this profile (it is a READINGS/UNFORMALISED unit, never guessed).

**Typed candidates.** Every entity candidate carries a sort: a constant its declared sort; `binder:<i>` the sort of
binder `i` in the sentence's context; a plural list the sorts of its members (each listed); a pair member its own
sort; a `such` property the argument sort of its predicate. Sorts do not restrict accessibility (4.2); they enter
through the type check of the elaborated formula, which is the only filter on competing resolutions (4.3). A
recorded target whose elaboration is ill-typed (a `person` where `safe : service` is predicated) is
`IllTypedTarget: <mention>: <target>`, a manifest error distinct from `TargetKindMismatch` (form/kind only).

**Nested mentions.** Within one unit, two mention spans are either disjoint or properly nested (η: `Her` lies inside
`Her manager`); a partial overlap is `InvalidInput: mentions <a>, <b> overlap`. An inner mention is resolved first
and its target is what the outer mention's `restriction` may name (a `possessive` inside a `definite`); the outer
mention is the slot (4.3), the inner one a binding of the restriction.

**Formula-producing versus location bindings.** `pronoun`, `demonstrative`, `definite`, `ordinal_pair`, `such`,
`possessive`, `plural`, `definition_ref` (as a rewrite, 2.1), `document_name` and `citation` are formula-producing:
their mention is a slot of the unit's derivation (4.3). `section_ref`, `navigation`, `unit` and `anchor` targets are
location bindings: they are entries of the unit's binding table, produce no formula, and never occupy a slot; a
unit consisting only of a location binding is LABELLED (4.9), and a location target in a slot position is
`TargetKindMismatch`.

### 1.5 Reading groups and compatibility constraints

```text
group      := {set, version, reading (a reading id of that set version), spans (ordered unit ids, source order)}
constraint := {kind ∈ {requires, excludes}, a: [set, version, reading], b: [set, version, reading]}
```

A group binds one reading of one reading set to an ordered list of source units: the reading's content is **one**
assertion; every listed unit keeps its historical span and receives the group's status; bytes are counted once. The
reading set the group names is the group's **owning set**, and W2 places it on the group's first span (the set's
`unit`); that unit carrying the owning set is not a fragment. No listed unit may carry content of its own, and no
listed unit may carry a reading set other than the owning set (`IndependentFragment: <unit>`). The group's formula
is validated per group and reading (`groupFormula` regenerates the owning set's reading and compares it with the
set's recorded content), never per fragment: a listed unit is not elaborated on its own and has no `bound` formula.
A `same-witness` group's content must share one witness across the spans (4.6); a content whose spans are quantified
independently is `WitnessSplit`. Constraints relate named readings of two active sets: `requires` (if `a` is chosen
then `b` is chosen), `excludes` (not both). On the wire a reading is named by its id in the set version; in Lean and
in W2's labels it is its `original_index`, the position in the set version's `readings` list (the `<i>` of
`readings:<set>@<version>:<i>`, `ve/readings.py`); the decoder maps id to index by position and rejects an id the
set version does not declare (`InvalidInput: reading <id> not in <set>@<version>`). The joint set of 4.8 is the
product of the active sets filtered by exactly the declared constraints; nothing is inferred from wording.

### 1.6 Document names and imports

```text
document := {name (a declared constant of the manifest's document sort), display (["this document", "this policy"]),
             refers: "self" | {"embedded": unit} | {"import": key} | {"part": anchor},
             version (integer), author (optional), supersedes (document names), scope (anchor, optional),
             source_id, document_id (pins: required for import, optional for embedded, forbidden for self and part)}
import   := key ↦ {source_id, document_id, bytes (a sibling file name pinned by source_id)}
```

A document name is an ordinary declared constant of a sort the manifest names as its document sort (`document_sort`,
a declared sort of `E` that no other declared constant uses). "This document" is the name whose `refers` is `self`;
"the above document" is a name whose `refers` is an `embedded` unit, a unit of kind `meta` whose bytes are a
complete `ve-document@1` or `@2` text; an external document is an `import` whose bytes are stored beside the
document and re-fingerprinted at every site; a `part` names an anchor of this document (a section) for
`supersedes` metadata and ordinary predicates only. `version`, `author`, `supersedes` and `scope` are provenance
shown by the IDE; they generate no premise (a sentence "This policy supersedes policy 3" is an ordinary binary atom
over these constants and a declared predicate, checked like any assertion; 2.1). What a document name licenses
beyond being a term is exactly one thing: a validity claim (4.7).

### 1.7 What the manifest is not

Not a proof, not an authority and not a truth predicate. A resolved link confers no truth (the target's content is
checked where it is, under its own premises); a navigation instruction is a label; a document constant asserts
nothing about its document; "under Article 29" imports no premise; incorporation and authority require explicit
admitted content and remain open otherwise. Weights never select a referent. Nothing in the manifest is trusted:
the resolver's proposals are validated at every site (3.4).

## 2. The English (one reading each; rejected as today when `ve.discourse@1` is off)

### 2.1 Wordings

These are proposed admission rules for sequence 2, not claims that today's parser accepts every row. Declared
vocabulary still controls predicate meanings. Every accepted rendering is writable and round-trips with its
bindings (theorem `discourse_parseRender`, 9.5). The paraphrase column is what the IDE shows.

| Wording (input) | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `The API is reviewed. It is safe.` | "‘It’ here means the API (registered in this document)." The reviewed presentation is `The API is safe.`; the source `It` is provenance. | `pronoun` → `entity api`; `safe(api)` |
| `Alice is reviewed. Bob is reviewed. She is ready.` | Question: "Does ‘she’ mean Alice or Bob?" with "Alice is ready" / "Bob is ready" and a distinguishing situation. Never chosen by name or gender. | `AmbiguousReference`; authoring: signed choice; translation: READINGS |
| `This service is safe.` | "‘This service’ means the API." Presentation `The API is safe.` | `demonstrative` → `entity api` |
| `Every reviewed service is deployed. Every such service is safe.` | "‘Such service’ copies exactly the property ‘reviewed’." Presentation `Every reviewed service is safe.` | `such` → `predicate reviewed`; `∀x (reviewed(x) → safe(x))` |
| `Alice and Bob are reviewed. The former is ready.` | "‘The former’ is the first of the pair ‘Alice and Bob’: Alice." Presentation `Alice is ready.` Pair order asserts no inequality. Two candidate pairs: a question. | `ordinal_pair` → `entity alice` with `pair [alice, bob]` |
| `Alice is reviewed. Her manager is ready.` | "‘Her’ means Alice. ‘Her manager’ is a description: someone who is a manager of Alice." Then the two description readings (4.5): "Alice has exactly one manager, and that manager is ready" / "Assuming Alice has exactly one manager: every manager of Alice is ready." Under the second, the IDE offers the uniqueness sentence `Alice has exactly one manager.` as an explicit unit of the document (its `presupposition_unit`) unless it is proved from the document's premises. | `possessive` → `entity alice` (nested inside the definite); `definite` with restriction `manager_of(x, alice)` |
| `Alice and Bob are reviewed. They are ready.` | "‘They’ means Alice and Bob, each." Presentation `Alice is ready and Bob is ready.` Collective or generic readings stay unresolved. | `plural` distributive → `entity` with `members [alice, bob]`; `ready(alice) ∧ ready(bob)` |
| `Every eligible service is reviewed, where eligible has the meaning defined in section 2.` | Rewrite: `Eligible has the meaning defined in section 2. Every eligible service is reviewed.` "The first sentence selects the definition of ‘eligible’ exported by section 2 (version pinned); the second is an ordinary sentence." | `definition_ref` → `predicate eligible@v`; `∀x (eligible(x) → reviewed(x))` |
| `Eligible has the meaning defined in section 2.` | Selects the pinned W3 declaration (signature and body); neither invents a definition nor changes its environment. | `definition_ref`; no premise of its own |
| `Article 29`; `clause 2.1`; `section 2` | A location in a qualified document/edition. A whole article is a location, not one inferred proposition. | `section_ref` → `anchor` |
| `See Article 29 of the Universal Declaration of Human Rights.` | A navigation instruction; nothing is asserted. | `navigation` → `anchor`; LABELLED |
| `By clause 2.1, the API is safe.` | "Clause 2.1's checked result is cited; this sentence is proved from it with every cited assumption listed, and the cited reading choices fit one compatible joint choice of this document (4.8)." | `citation` → `claim`; W3 `cite:` leaf, unchanged; plus the discourse extension check |
| `The owner is ready.` | Two readings shown with situations: "There is exactly one owner, and that owner is ready" / "Assuming there is exactly one owner: every owner is ready." (with `There is exactly one owner.` offered as an explicit unit, as above). Never: existence from "the". | `definite` with restriction `owner(x)`; 4.5 |
| `A service is deployed. It is reviewed.` | "‘It’ here is the service just mentioned: the same-witness reading is `Some service is deployed and reviewed.`; alternatives are kept." | group `same-witness`; `∃x (deployed(x) ∧ reviewed(x))` bound to both spans |
| `Every service is deployed. It is reviewed.` | No automatic reading. Rewrite offered: `Every service is deployed and reviewed.`; translation keeps the alternatives. | `UnresolvedReference`; scoped rewrite |
| `This document is a valid VE document.` | "Checked: this document is admitted; the verdict is computed without using this sentence." | validity claim, `self`, positive; CHECKED |
| `This document is not a valid VE document.` | "False: this document is admitted." Admission is unchanged. | validity claim, `self`, negative; `ValidityRefuted` warning |
| `The above document is a valid VE document.` | "Checked: the document quoted above (fingerprint shown) is admitted when re-checked." | validity claim, `embedded` |
| `Policy 3 is a valid VE document.` | "Checked/refuted/unconfirmed: the pinned document ‘Policy 3’ (fingerprint shown) is re-checked from its stored bytes." | validity claim, `import` |
| `This policy supersedes policy 3.` | An ordinary claim over two document names and the declared predicate `supersedes`; its truth is not certified. | `supersedes(this_policy, policy3)` |
| `Everything in this document is true.` / `This sentence is false.` / `This document is correct.` / `The above document is true.` / `Policy 3 is correct.` | "Labelled: VE certifies admission, never the truth or correctness of a document; this sentence is recorded and never checked." The document may be named by any document name (1.6), not only "this document". | kind `meta`, LABELLED, label `self-truth` |
| `Under Article 29, ...` | A location; imports no premise, establishes no authority, chooses no override. The rest of the sentence is checked on its own. | `section_ref`; no premise |
| `Rule 4 (exception to rule 3).` | W1, unchanged: a stable rule name. | `rule` |
| `In this document, staff, employees and personnel mean the same thing.` | W3 alias definition, unchanged. | W3 |

### 2.2 Synonyms and non-synonyms

Input synonyms rendered canonically: `the latter` for the second member of the pair (as `the former` for the first);
`that <noun>` for `this <noun>` when both would bind the same registered name; `the said <noun>`,
`the aforementioned <noun>`, `the above <noun>` for `this <noun>` only when a registered name has that display form.
Nothing else. `it` inside a `that`/`who` relative clause keeps its local binder (natural view). `respectively` is
not a wording. A section number without a declared anchor is `DanglingAnchor`. "Valid" in a validity claim means
admitted, exactly (4.7); "true", "correct", "sound", "accurate" applied to any document name (this document, the
above document, a named import), to a unit of this document or to the sentence itself are the self-truth wordings
of 2.1, never synonyms of "valid".

### 2.3 The reader's checklist (what the IDE shows on accept)

For every resolved mention, in English only: what it means ("‘it’ here means the API"), where the name was
registered (the anchor), the reviewed presentation with the expansion, and, for a description, which of the two
readings was chosen with the uniqueness sentence shown as a separate premise when presuppositional. For a same-witness
group: "these two sentences make one claim: some service is deployed and reviewed; each sentence keeps its place in
the source". For a validity claim: "checked by re-running the check on the named document; nothing here depends on
this sentence being true". For a self-truth sentence: "labelled; VE does not certify a document's own truth". For a
citation: the cited result and every retained assumption, bridge and reading choice it carries.

### 2.4 Questions the IDE asks, and what translation records

Authoring asks one short English question per unresolved mention, shows each candidate as a rewritten sentence with
a concrete distinguishing situation (a checked finite model rendered in document terms), and records the author's
signed choice as an `authored` reading set. Approval uses the reviewed presentation (the expansion); a hidden
binding never rescues ambiguous displayed prose. Translation records the candidates as an `open` reading set, with a
group when a candidate fuses sentences; a translator's narrowing is attributed and labelled on every dependent
result and never replaces the source set; weights never select a referent. Missing semantics or a missing
distinguishing situation leaves the candidate pending, not fictitiously checked; a pending candidate is a
`references` line, never a reading of the set (a reading set holds admitted formulas only). For a presuppositional
description, authoring offers the uniqueness sentence as an explicit unit the author signs (the mention's
`presupposition_unit`); translation cannot add a unit, so a presupposition that is not proved stays pending there.

### 2.5 Examples from the pinned sources

Expected reference outcomes only; no status upgrade is claimed for any of these units (plan page 4).

```text
Constitution run 20260927T1800Z (units.json; spans are the ledger's)
u0136.s01  "Such potential harms always have to be weighed against the potential benefits of taking an action."
           `such` → predicate copied from the harms enumerated in the preceding units (a `unit` target list until a
           property is registered); "have to be weighed" is a soft-weighing co-blocker. Reference resolved and
           recorded; the unit stays UNFORMALISED.
u0182.s03  "Or does it escape these mechanisms?"
           kind question; `it` → the entity registered for the model in that section, `these mechanisms` → a `unit`
           list; LABELLED as a question with its references in the inventory.
u0214.s02  "We call this broad pattern of treatment and trust Claude's principal hierarchy, and it helps define what
           we mean by broad safety."
           MIXED: the naming clause registers the content name "Claude's principal hierarchy" (1.3) over a `unit`
           target (the preceding units) and is LABELLED; "it helps define what we mean by broad safety" resolves
           `it` to that content name's `unit` target and stays UNFORMALISED (no "helps define" semantics;
           `broad_safety` remains the open term).
           Calling the whole passage OPEN stays forbidden (the rejected u0214 audit).
u0256.s03  "Indeed, it can explore these questions as fascinating aspects of its novel existence."
           `it`/`its` → the registered model entity; `these questions` → a `unit` list (content, not an entity);
           "can explore" is a modality co-blocker; UNFORMALISED with references recorded.
UDHR run 20260927T1800Z
u109       "## Article 29": anchor `article` with label "Article 29"; LABELLED heading.
u110–u112  items 1–3 of Article 29: anchors `item` "29.1", "29.2", "29.3" under u109's anchor.
u112       "These rights and freedoms may in no case be exercised contrary to the purposes and principles of the
           United Nations.": `these rights and freedoms` → a `unit` list (the rights declared in Articles 1–28, as the
           translator records it, with the alternative "the rights of Article 29.2" kept as a reading); rights
           semantics remain the co-blocker; UNFORMALISED with the reference recorded.
```

## 3. Wire form and identity

### 3.1 The `discourse` block

```json
"format": "ve-document@2",
"discourse": {
  "version": "ve.discourse@1",
  "definitions_version": "<environment_id the definitions are pinned at>",
  "document_sort": "document",
  "anchors": [{"id": "doc", "kind": "document", "label": "Policy", "span": [0, 2210]},
              {"id": "sec2", "kind": "section", "parent": "doc", "label": "2", "span": [120, 980],
               "exports": ["eligible"]}],
  "names": [{"constant": "api", "display": "the API", "scope": "doc", "aliases": ["the service API"]}],
  "content_names": [{"name": "Claude's principal hierarchy", "units": ["u40", "u41"], "scope": "doc"}],
  "mentions": [{"id": "m1", "unit": "u2", "span": [45, 47], "form": "pronoun",
                "target": {"kind": "entity", "name": "api"}},
               {"id": "m2", "unit": "u7", "span": [301, 320], "form": "definition_ref",
                "target": {"kind": "predicate", "name": "eligible", "version": 2}},
               {"id": "m3", "unit": "u9", "span": [410, 421], "form": "definite",
                "target": {"kind": "entity", "name": "binder:0"}, "reading": "presuppositional",
                "restriction": ["binary", "manager_of", ["var", 0], ["const", "alice"]],
                "presupposition_unit": "u10"},
               {"id": "m4", "unit": "u9", "span": [410, 413], "form": "possessive",
                "target": {"kind": "entity", "name": "alice"}},
               {"id": "m5", "unit": "u12", "span": [520, 524], "form": "plural",
                "target": {"kind": "entity", "members": ["alice", "bob"]}, "reading": "distributive"},
               {"id": "m6", "unit": "u13", "span": [560, 570], "form": "ordinal_pair",
                "target": {"kind": "entity", "name": "alice", "pair": ["alice", "bob"]}},
               {"id": "m7", "unit": "u42", "span": [900, 902], "form": "pronoun",
                "target": {"kind": "unit", "units": ["u40", "u41"], "content_name": "Claude's principal hierarchy"}}],
  "documents": [{"name": "this_policy", "display": ["this document", "this policy"], "refers": "self",
                 "version": 3, "author": "ops", "supersedes": ["policy2"]},
                {"name": "policy2", "display": ["policy 2"], "refers": {"import": "policy2"}, "version": 2,
                 "source_id": "<sha256>", "document_id": "<sha256>"}],
  "imports": {"policy2": {"source_id": "<sha256>", "document_id": "<sha256>", "bytes": "policy2.ve.md"}},
  "groups": [{"set": "rs1", "version": 1, "reading": "same-witness", "spans": ["u3", "u4"]}],
  "constraints": [{"kind": "requires", "a": ["rs5", 1, "pattern-a"], "b": ["rs6", 1, "it-a"]}]
}
```

Optional fields are absent, never `null` (the frozen Lean JSON parser rejects `null`). Every id is a token of the
existing grammar (`[a-z][a-z0-9_-]*`, at most 64 bytes); `definitions_version` must equal the `environment_id`
computed under the stripped profile list (3.5; `StaleTarget: definitions@<version>` otherwise); `document_sort`
names a declared sort that only document names use (`InvalidInput: document sort <s> has other constants`);
`restriction` is a P0 wire formula over the context `[sort of the description]` (index 0 is the described entity)
mentioning declared base or defined predicates and resolved constants only. A `group.reading` and the `a`/`b`
entries of a constraint name a reading by its id in the set version and decode to its `original_index` (1.5). A
`reading` value outside `assertive`, `presuppositional`, `distributive` (a recorded `collective`) is a decode-time
`InvalidInput: reading <value>`.

### 3.2 Units, groups and statuses

A unit of `ve-document@2` is a `@1` unit; the discourse block adds nothing to a unit. Status is W2's: `CHECKED`,
`OPEN`, `LABELLED`, `UNFORMALISED`, with `MIXED` parents. A unit listed in a group has no `content`, no
`meaning_id` and no reading set other than the group's owning set (which W2 places on the first span, 1.5); its
status is the owning set's status under W2's rule (an authored assertion singleton with content is CHECKED, an open
set is OPEN). A `presupposition_unit` (4.5) is an ordinary asserted unit with content `U(D)` and W2's status for
it (CHECKED as an assumption, listed in the residual). A `meta` unit that is the target of a validity
claim binding (4.7) has no content; its status is CHECKED when the verdict is `checked`, LABELLED otherwise. A
`meta` unit labelled `self-truth` has no content and is LABELLED. Coverage tables (`bytes_by_status`,
`bytes_by_kind`) still each total the source byte count; a group's units are counted once, each under its own span.

### 3.3 Identity

```text
source_id      unchanged (sha256("ve-source-<identity_version>\n" + prose bytes))
environment_id P0's, computed by the frozen Wire.environmentId on (baseProfiles, baseEnvironment) (3.5): the profile
               list without ve.discourse@1 and the environment JSON with its "profiles" field regenerated to that list
meaning_id     unchanged for every formula, norm and definition (the elaborated formula is a P0 formula), computed
               under baseProfiles and the environment_id above; the same formula in a @1 document without the
               profile has the same meaning_id
definitions_version  the environment_id above (3.1)
document_id    sha256("ve-document@2\n" + canonical({"metadata": front matter minus "weights", "source": prose,
               "fences": fences})), the `@1` payload under the new domain tag; the discourse block is inside
               "metadata", so every anchor, name, content name, mention, target, version pin, group, constraint
               and document declaration is identity-bound; removable weights and JSON layout are not
report_id      P0's for the inner (W2) report, under baseProfiles; the discourse wrapper report identity
               (sha256("ve-discourse-report@1\n" + canonical({"profiles": the original sorted list including
               ve.discourse@1, "environment_id": ..., "document_id": ..., "report_id": the inner one,
               "references": ..., "validity": ...}))) binds the original profile declaration, the manifest
               (through document_id) and the @2 document identity
```

A `@1` document keeps its `@1` `document_id` (the `@2` loader does not re-tag it). Renumbering a section changes
labels (display) and therefore `document_id`, but no target identity (`anchor` ids and rule names are stable); the
source and its presentation need renewed approval, as `natural-view.md` requires for any changed presentation.
Editing a target's content changes the target's `meaning_id` or the definition version, so every certificate bound
to a dependent unit fails replay (`stale_target_rejected`, 9.6). Every certificate of the document is bound, through
the P0 premise/conclusion identities, to the elaborated formulas, and through the wrapper report to the `@2`
`document_id`; the envelope is recomputed from the raw input at replay, never read from the wire.

### 3.4 Regeneration and trust

The resolver (Python `ve/discourse.py`, sequence 2) proposes mentions, targets and groups; nothing it writes is
trusted. At every trusted site the validator recomputes, from source bytes plus manifest: the anchor tree, the
registered scopes and content names, each mention's accessible targets (4.2), the uniqueness of the recorded
assignment among the type-checking competitors (4.3), the elaborated formula of every bound unit (a non-grouped
unit with a formula-producing mention, 4.4), each group's reading per group (1.5, `groupFormula`; fragments are
never elaborated separately), the location bindings as tables (1.4), the constraint checks (4.8), the document
table (4.7) and every identity. A manifest whose recorded target is not the unique accepted one, or whose recorded
formula differs from the regenerated elaboration, is `ManifestMismatch: <field>`. Python/Rust/Lean agreement is
regression evidence; the trust path is Lean (`ve_discourse_route`, 9.7). Decoding, hashing and display remain named
trust boundaries.

### 3.5 The profile adapter (the frozen gate never sees `ve.discourse@1`)

The frozen envelope decoder and classifier (`VE.Route.Gate.decodeEnvelope`, `classify`) reject any profile outside
their registry, and `Gate.decodeEnvelope` reads the `profiles` field of the environment JSON while
`VE.Route.Wire.environmentId` hashes the environment JSON it is given. The wrapper therefore regenerates both:

```text
baseProfiles    := profiles.filter (· != "ve.discourse@1")
baseEnvironment := environment.setObjVal! "profiles" (toJson baseProfiles)
```

In order: (1) the wrapper validates the original envelope: `profiles` sorted and unique, containing
`relational-fol@0` and `ve.discourse@1`, the environment object's `profiles` field equal to that list, the format
`ve-document@2` (`UnsupportedProfile: ve.discourse@1 requires ve-document@2`), the `discourse` block decoding
strictly; (2) every frozen function (`Gate.decodeEnvelope`, `Gate.classify`, `Wire.decodeVocabulary`,
`Wire.environmentId`, `Wire.meaningId`, `Wire.bindingOk`, `Admission.admitDocument`, `Bundle.checkLemma`) is called
on `(baseProfiles, baseEnvironment)`, as `Norms/Replay.lean` (`baseEnvironmentJson`, `decodePackage`) calls them on
the environment with `norms@0` removed; (3) the inner `environment_id`, every `meaning_id`, `definitions_version`
and every certificate binding are computed from that same pair (3.3); (4) the outer wrapper report binds the
original profile declaration (the full sorted list), the manifest and the `@2` `document_id`. The frozen gate's
diagnostics for the base list are unchanged (`profile_adapter_base`, 9.6). No frozen file changes.

## 4. Semantics

### 4.1 Well-formedness (`WellFormedDiscourse`)

A `ve-document@2` document `D` over environment `E` is well-formed when, in this order:

1. The wrapper validates the original envelope and the format is `ve-document@2` (3.5); the base list passes the
   frozen gate on `baseEnvironment`; the block decodes (3.1); the `@1` part loads under `(baseProfiles,
   baseEnvironment)` (W2's checks unchanged, including the byte partition).
2. Anchors form one tree with nested, non-overlapping spans and unique labels per parent (1.2); every `exports`
   entry is a predicate declared at `definitions_version` whose definition unit lies in the anchor.
3. Names bind declared constants to unique display strings per scope (1.3); content names bind display strings to
   existing units per scope; every document name is a declared constant of `document_sort` and no other constant
   has that sort (1.6); imports pin `source_id` and `document_id`; an `embedded` unit exists and has kind `meta`.
4. Every mention lies inside its unit's span; mention spans within one unit are disjoint or properly nested
   (`InvalidInput: mentions <a>, <b> overlap`); every target exists (`UnresolvedReference` when the manifest
   records none, `DanglingAnchor`, `UnknownDocument`, `UnknownRule`, W3's `Citation is absent, cyclic, or not
   earlier in the bundle`); a `plural` target lists at least two distinct members, an `ordinal_pair` target's
   `name` is a member of its `pair`, a `unit` target's `content_name` (if any) lists exactly its `units`.
5. Every mention's form fits its target kind (`TargetKindMismatch`); descriptions carry a typed restriction;
   plurals are distributive over an explicit finite list; every entity candidate has a sort (1.4); a
   presuppositional definite's `presupposition_unit`, when present, names an asserted unit of `D` whose content is
   `U(D)` for that mention's restriction (`ManifestMismatch: mentions.<m>.presupposition_unit` otherwise).
6. Every recorded target is accessible (4.2); its elaboration type-checks (`IllTypedTarget`); it is unique modulo
   aliases among the type-checking competitors (4.3); every bound unit (a non-grouped unit with a
   formula-producing mention) elaborates to a closed typed formula (4.4), and its recorded mentions are exactly
   the accepted derivation's slots (`UnrecordedSlot`, `MentionNotSlot`).
7. Groups and constraints are well-formed (1.5): listed units carry no content and no reading set other than the
   owning set (`IndependentFragment`), the group's reading regenerates per group (`groupFormula`), the
   `same-witness` content shares its witness (`WitnessSplit`), constraints name active readings by
   `original_index`.
8. The joint set of the active open sets is validated to completion and nonempty (`InvalidCompatibility`) or its
   validation hits the budget (UNKNOWN for every reading-dependent verdict, including the citation and report
   extension checks of 4.8; not a rejection). Zero open sets give the one empty choice (4.8).
9. Definition and proof dependencies are acyclic: `dependencyOrder` over definition anchors and cited lemmas
   (`DependencyCycle: <sorted names>`, W1's shared text). Navigation edges are not in this graph.
10. Every embedded or imported document **decodes** (format, block, envelope) and its **identities** are intact
    (an import's stored bytes, when present, re-fingerprint to the pinned `source_id`; an embedded unit's pinned
    `document_id`, when present, equals the recomputed one; `StaleTarget: <document>` otherwise), the chain has
    no repeated `source_id` (`ImportCycle: <source ids>`) and nesting depth is at most 4 (`ResourceLimit:
    document nesting`). Whether the embedded or imported document is itself **admitted** is not a
    well-formedness condition: it is the second-phase outcome of 4.7, so a rejected import is reportable
    (`refuted`) rather than rejecting the importing document.
11. Limits (11).

Warnings (reported, never rejecting): `ValidityRefuted`, undeclared names used only as display in exposition,
navigation targets outside any admitted import (a label with no target content).

### 4.2 Accessibility `Acc(D, m, t)`

An independent relation between a mention and a candidate target, with no nearest-mention, gender, salience,
paragraph-reset or frequency heuristic:

```text
entity, constant c        c is registered (1.3) with scope σ and m.unit lies in σ's span, and m's form is one of
                          pronoun, demonstrative, possessive (never definite: "the API" is a registered name, not a
                          description; never such: `such` targets a predicate)
                          AND, for a pronoun or bare demonstrative, no competing quantified mention: no existential or
                          universal binder of c's sort occurs in an earlier sentence of the innermost anchor
                          containing m, nor earlier in m's own sentence (natural-view rule, scoped by anchor and
                          sort; these binders are an explicit input of Acc, listed below)
entity, list [c₁ … cₙ]     form plural; n ≥ 2, the cᵢ distinct, each cᵢ accessible as a constant above (form plural)
entity, pair (c₁, c₂), k  form ordinal_pair; the coordination "c₁ and c₂" (two registered display forms joined by
                          `and`) occurs in an earlier sentence of the innermost anchor containing m or earlier in
                          m's own sentence, both cᵢ accessible as constants; the candidate is member k (the former:
                          1, the latter: 2); two such coordinations are two candidates
entity, binder:i          only inside the sentence or rule that introduces binder i, in a position the binder scopes
                          over; never across a sentence boundary (WitnessEscape); never out of quantification,
                          negation, disjunction, a conditional, quotation or an attitude
predicate p               p declared in E at definitions_version; for definition_ref, p is in the named anchor's
                          `exports` (1.2); for such, p is a declared unary predicate applied, as a restrictive
                          modifier of the same noun, in an earlier sentence of the innermost anchor containing m or
                          earlier in m's own sentence (the explicitly bound property; its argument sort is the
                          candidate's sort); two such properties are two candidates
unit / anchor             the ids exist; forward references allowed after indexing; a content name lists the units
rule r                    r is a stable name of a norm unit of D (W1's same-predicate and DAG restrictions unchanged)
claim l                   l is a lemma strictly earlier in D's bundle (Bundle.checkLemma)
document d                d is declared in D.documents
```

A quoted name can be identified across a quotation (a pronoun in "Bob says that the API is not reviewed. It is
safe" may target `api`) without admitting the quoted fact: identification uses the registration, and the quoted
content still needs its bridge leaf. `Acc`'s inputs are exactly: the registrations, content names, anchors and
declarations; the mention's unit, span and form; the binders of the mention's own sentence; and the binders and
coordinations of the earlier sentences of the innermost anchor containing the mention (the competing-quantifier,
pair and `such` inputs). It does not depend on any other mention, on any recorded target, on the reading choices,
or on wording outside the innermost anchor (theorem `acc_no_heuristic`, 9.2, whose hypotheses are these inputs).
Recorded targets and reading choices never prune candidates; sorts never restrict `Acc` (they act in 4.3).

A manifest supersedes the natural-view rule by sort-typing it. `natural-view.md` admits a bare "It" only when
exactly one constant has been mentioned earlier in the document, untyped and document-wide; here the candidates
are the constants accessible by scope and the sort of the predication filters the competitors (4.3). The two
agree whenever every constant mentioned earlier has one sort (the candidate set and the competing-quantifier set
then coincide); with two sorts and one typed candidate they differ by design (fixture α′, section 10).

### 4.3 Resolution and acceptance

```text
Derives(D, s, d)            d is a derivation of sentence s in the discourse grammar: the existing English grammar with
                            a slot production for each formula-producing form of 1.4 (the slot yields the mention's
                            surface text)
slots(d)                    the slots of d in source order; a slot is (unit, span, form): a surface position and a
                            form, never a target
K.target(m)                 the target the manifest records at slot m: the mention of K.mentions with m's unit, span
                            and form (none when K records no mention there)
assignment σ                slots(d) → targets
elaborate(D, d, σ, ρ)       the closed formula obtained by substituting each slot by its target's elaboration (1.4,
                            4.5, 4.6) under the recorded reading choices ρ, a fixed input, never a filter;
                            capture-avoiding; fails when a slot's target has no elaboration (a location target)
Accepted(D, s, ρ, A)        := ∃ d σ. Derives(D, s, d)
                                 ∧ (∀ m ∈ slots(d). Acc(D, m, σ m) ∧ σ m = K.target(m))
                                 ∧ elaborate(D, d, σ, ρ) = A ∧ A closed and well-typed over E
                                 ∧ ∀ d' σ' A'. Derives(D, s, d') → (∀ m ∈ slots(d'). Acc(D, m, σ' m))
                                     → elaborate(D, d', σ', ρ) = A' → A' closed and well-typed over E
                                     → tree(d') = tree(d) ∧ slots(d') = slots(d)
                                       ∧ ∀ m ∈ slots(d). AliasEq(D, σ' m, σ m)
```

One recorded, typed derivation and assignment is fixed first; every competitor (any derivation of `s`, any
accessible assignment of its slots) whose elaboration is closed and well-typed must equal it: the same tree, the
same slots, and the same targets modulo declared aliases. The type check is the only filter on competitors:
recorded targets never prune (they are the comparison point, `σ m = K.target(m)`), reading choices never prune (`ρ`
is a fixed input to elaboration), and a competitor that selects itself is not a witness, because the comparison is
against the one recorded pair, not against a pair of the competitor's choosing. Consequences: a recorded target
whose elaboration is ill-typed is `IllTypedTarget: <mention>: <target>`; two type-checking assignments with
different targets are `AmbiguousReference: <mention>: <targets>`; two type-checking derivations with different
trees or slots are the all-derivations diagnostic of P0 3.2 (scope or antecedent alternatives are derivations).
After uniqueness, the unit's recorded mention set must equal `slots(d)`: a slot with no recorded mention is
`UnrecordedSlot: <unit>: <span>`, a recorded formula-producing mention that is not a slot is
`MentionNotSlot: <mention>`. Selecting one parser result is insufficient. Resource exhaustion is `ResourceLimit:
resolution` (UNKNOWN), never uniqueness. Logical judgment uses `A`, never a mutable conversation history; the
standalone export repeats the targets (6).

### 4.4 Elaboration and the intended meaning

`Intended(E, K, s, ρ, S)` is defined on the derivation and the validated assignment, against a structure `S`,
without reference to `elaborate`: the sentence's meaning with each slot interpreted directly in `S`:

```text
entity constant c          the element S.constant c
entity pair member         the element S.constant c_k of the selected member
entity binder:i            the valuation's value for binder i
predicate p (such)         the relation S.relation p
definite, assertive        ∃ a in S.domain σ (σ the restriction's sort): D holds at a in S, every b in S.domain σ
                           with D at b equals a, and the sentence's predication holds at a
definite, presuppositional the predication holds at every a in S.domain σ with D at a in S (the uniqueness premise
                           is carried separately, 4.5)
plural, distributive       the conjunction over the listed members
same-witness group         ∃ a in S.domain σ: each span's predication holds at a (4.6)
document name d            the element S.constant d
```

`elaborate` produces the corresponding formula: the constant term, the bound variable, the predicate symbol,
`∃x (D(x) ∧ ∀y (D(y) → y = x) ∧ P(x))`, `∀x (D(x) → P(x))`, `P(c₁) ∧ … ∧ P(cₙ)`, `∃x (φ(x) ∧ ψ(x))`, the constant
term. `elaborate_faithful` (9.3): on every admissible structure, `A` holds iff `Intended`. Nothing is added to `E`:
no witness constant, no choice function, no fresh predicate (`elaborate_no_new_symbols`).

### 4.5 Definite descriptions

For an explicit restriction `D` (a declared unary predicate, or a declared binary predicate with its other
argument a resolved entity, e.g. `manager_of(x, alice)`), with `U(D) := ∃x (D(x) ∧ ∀y (D(y) → y = x))`:

```text
assertive reading          A := ∃x:σ (D(x) ∧ ∀y:σ (D(y) → y = x) ∧ P(x))      one claim; false when there is no or
                                                                              more than one D
presuppositional reading   premise  U(D)   carried in one of the two frozen forms below
                           claim    ∀x:σ (D(x) → P(x))                        checked only under that displayed premise
```

Every binder is typed by `σ`, the restriction's sort (P0's `.ex σ` / `.all σ`). No `discourse:*` label exists at
W2: the frozen `Route/Admission.lean` `parseLabel` reads only W2's labels and `LeafAdmitted` is `False` for any
other, so the uniqueness premise enters the claim graph in one of two frozen forms (the presupposition adapter):

- **proved**: `U(D)` is a unit-less `asserted` deduction node carrying its certificate from the document's
  premises (`NodeAdmitted` admits a deduction whose `unit = none` under the label `asserted`); the report lists it
  under `presuppositions: proved` with its certificate;
- **assumed**: `U(D)` is an explicit asserted unit of the document, the IDE's offered sentence ("Alice has exactly
  one manager."), named by the mention's `presupposition_unit`; it is an ordinary `asserted` leaf with its unit and
  appears in the residual as an assumption; translation cannot add a unit, so there the mention stays pending;
- **neither**: the mention is `PresuppositionUnresolved: <mention>` and the unit stays pending (READINGS in
  translation, a question in authoring).

`discourse:presupposition:<mention>` is a report line (7.1) naming the carrier, never a leaf label.
`description_definedness` (9.3): the assertive reading holds iff `U(D)` and the presuppositional claim both hold;
`presupposition_retained` (9.3) is stated over the two carriers. Never inferred: existence from "the" (fixture ξ
has a model with no owner where the presuppositional claim is vacuously true and the assertive one false, and a
model with two ready owners where the presuppositional claim is true while `U(D)` and the assertive reading are
false), uniqueness from one known instance, or truth from a finite lookup. Contextual restrictions ("the owner",
in a section about the API, meaning `owns(x, api)`) are explicit in the manifest's `restriction` or the mention is
unresolved. Competing presupposition/accommodation readings are two readings of one set, distinguished by a
situation.

### 4.6 Same-witness fusion

"A service is deployed. It is reviewed" licenses no fresh constant and no two unrelated existentials. The
same-witness reading is the group reading with content `∃x:service (deployed(x) ∧ reviewed(x))` (`sharedWitness`
holds: one outermost existential whose body is a conjunction in which every conjunct mentions the bound variable),
presented as `Some service is deployed and reviewed.` and bound to both spans; the other admitted readings (the
pronoun targets a registered constant, when one is accessible) remain alternatives in the owning set, which W2
places on the first span; a candidate without admitted content (the sentences are unrelated and the second is
pending) is a pending `references` line outside the set's readings, never a member of an admitted reading
inventory. A universal followed by "it" likewise needs an explicit scoped rewrite (`Every service is deployed and
reviewed.`). Fusion changes the reviewed presentation, never the historical source boundaries: both spans keep
their bytes, each receives the owning set's status, the set's reading is regenerated per group, and no fragment is
elaborated or admitted on its own (theorem `group_single_assertion`, 9.3; fixture μ shows the split reading
`∃x:service deployed(x) ∧ ∃x:service reviewed(x)` is weaker on a two-element model).

### 4.7 Document names, validity claims and the truth boundary

A document name is a constant (1.6); the environment's sort `document_sort` and its constants are the author's
declarations, so the profile adds no symbol (`document_sort_conservative`, 9.6: old-vocabulary consequences are
unchanged by declaring the sort and its constants).

A **validity claim** is a `meta` unit bound in the manifest to a document name and a polarity
(`{"validity": {"document": "policy2", "holds": true}}` in the unit's discourse binding; the wording is 2.1). It
has no content and enters no premise list; it is evaluated in a **second phase**, after admission, from the
admission verdicts alone:

```text
Outcome(d) ∈ {admitted, rejected (diagnostic), unknown (reason)}
           admitted   admitDiscourse succeeds on the document d refers to, checked to completion
           rejected   admitDiscourse fails with a completed admission diagnostic (not a ResourceLimit)
           unknown    the check does not complete: bytes absent, ResourceLimit (any), the nesting budget
self       Outcome = this document's own admission; computed on stripValidity(D), the document with every validity
           binding removed, so the verdict never depends on any validity unit (validity_independent, 9.6); always
           `admitted` inside an admitted document
embedded   the unit's bytes are loaded as a document (depth + 1) and checked (the pinned document_id was verified
           at 4.1(10))
import     the stored bytes (their source_id verified at 4.1(10)) are checked (depth + 1); bytes absent: unknown
part       no validity claim (UnsupportedTarget: part): a section is not a document
verdict    checked      when Outcome(d) = admitted and holds, or Outcome(d) = rejected and ¬holds
           refuted      when Outcome(d) = admitted and ¬holds, or Outcome(d) = rejected and holds
                                                   warning ValidityRefuted: <unit>; admission unchanged
           unconfirmed (reason)                    when Outcome(d) = unknown; report line; the unit is LABELLED
```

Rejection and UNKNOWN are distinguished explicitly: `.isOk = false` alone never establishes invalidity. A negative
claim ("Policy 2 is not a valid VE document") is `checked` only against a completed rejection; a check that hits a
resource limit, absent bytes or the nesting budget leaves both polarities `unconfirmed` (never assumed valid, never
refuted). Import integrity (a pinned fingerprint that does not match the bytes) is the manifest error `StaleTarget`
of 4.1(10), not an outcome; the imported document's own admission diagnostics are outcomes and are reported.

Because admission never reads a validity unit, "This document is not a valid VE document" in an admitted document
is simply false (refuted), not paradoxical: rejecting the document for it would make it true. The boundary is
**truth**: no construct lets a sentence certify the truth or correctness of its own document, of a unit of it, or
of itself; such sentences (2.1) are `meta` units labelled `self-truth`, LABELLED, with no content, never a premise
and never CHECKED (`self_truth_never_content`, 9.6). Claims about other documents' content go through citations
(W3) or imports with admitted content, never through a validity claim. The stratification is by document: an
embedded or imported document is checked as its own level with its own `self`; the chain is acyclic by
`source_id` and bounded in depth (`import_acyclic`).

### 4.8 Correlated readings and the joint set

A choice assigning "this pattern" controls every later reference to that same mention; the manifest records the
dependency as constraints (1.5). Let the active open sets be `R₁ … Rₙ` (latest version per unit, W2) and
`Compatible(K, c)` hold for a choice vector `c` (one reading per set) that satisfies every declared constraint.

```text
JointSet(K)      := { c : Compatible(K, c) }                     enumerated, at most 64 (ResourceLimit: joint choices → UNKNOWN)
                    zero open sets: the one empty choice [] (JointSet = {[]}); empty after a completed enumeration:
                    InvalidCompatibility: <sets> (a manifest validation error, 4.1(8)), distinct from inconsistent
                    premises inside an existing choice, which keep W2's inconsistency and vacuity report
Conj(c)          := the conjunction of the chosen readings' contents (same environment, same background, all
                    assertion readings); Conj([]) = top
Joint(K)         := ⋁_{c ∈ JointSet(K)} Conj(c)                 defined only when JointSet(K) ≠ ∅; top with no open sets
ALL   φ          := Background ++ Γ_fixed ++ [Joint(K)] ⊢ φ       one certificate; equivalent to a proof under every
                    compatible choice (joint_all_iff, 9.4)
NONE  φ          := one checked finite model of Background ++ Γ_fixed satisfying every reading that occurs in some
                    compatible choice and refuting φ (one shared model may suffice); else a checked countermodel per
                    compatible choice
SOME  φ          := a certificate for one named compatible choice and a checked countermodel for another; the vacuity
                    report describes the proved choice's premises
```

The shortcut applies only to same-environment, same-background assertion readings; with no constraints
`JointSet` is the full product and `Joint(K)` is W2's conjunction of per-unit disjunctions (`unconstrained_product`
regains `VE.Route.readings_all_iff`). For any other kind (norm, definition, differing backgrounds) each compatible
choice is elaborated separately (at most 64), else UNKNOWN, as W2 states. A choice is global per unit, so one
sentence is never read two ways inside one argument; a cited result carries its choices as `readings:` labels and
`Bundle.checkLemma` rejects incompatible citations unchanged (`citation_choices_retained`, 9.4). Vacuity and global
choice/version labels are retained through citations.

**Citation and report extension (the composition gate).** W3's `Bundle.checkLemma` (`leafChoices`, `mergeChoices`,
`ReadingCompatible`) merges choices within each reading set only, and W2's `ChoicesCompatible` (`compatible`)
rejects only two labels of one set with different versions or concrete choices; neither sees `requires` or
`excludes`. Two citations choosing `rs5:pattern-a` and `rs6:it-b` pass both checks even when the manifest excludes
that pair, and two lemmas that each extend to a compatible choice may combine into a pair that does not. After the
unchanged W3 and W2 checks, `admitDiscourse` therefore requires, with the validated `JointSet(K)`:

```text
ExtendsTo(ch, c)         for every entry (set, "v:i") of a W3 choice list ch, c's entry for set is (set, v, i);
                         for every entry (set, "v:all"), c's entry for set has version v (all preserves its version
                         and imposes no branch selection)
citationExtendsJoint     for every lemma L: leafChoices(L's transitive leaves) = ch and ∃ c ∈ JointSet(K), ExtendsTo(ch, c);
                         else InvalidCompatibility: citation <lemma>
reportExtendsJoint       for every reported graph result: leafChoices(the merged transitive assumptions of the report)
                         = ch and ∃ c ∈ JointSet(K), ExtendsTo(ch, c); else InvalidCompatibility: report <root>
```

Both diagnostics require a completed enumeration; when `JointSet(K)` is UNKNOWN (budget) the two checks are UNKNOWN
for every reading-dependent verdict and never a rejection (`citation_extends_joint`, `report_extends_joint`, 9.4).

### 4.9 The three operations

"See Article 29 of the Universal Declaration of Human Rights" is a navigation instruction: a `navigation` mention
to an anchor, a location binding (1.4), LABELLED, no premise, no slot. "Eligible has the meaning defined in section
2" selects the pinned W3 declaration in that anchor's `exports` at `definitions_version` (signature and body); it
neither invents a definition nor changes its environment; a later change of the definition is `StaleTarget`. "By
clause 2.1, the API is safe" requests a W3 checked deduction: matching environment identity, every cited
non-background transitive leaf listed among the citing claim's own hypotheses, compatible reading choices and
inherited transitive leaves; all retained assumptions, bridges and reading choices remain visible
(`Bundle.checkLemma`, unchanged), and the cited choices extend to a compatible joint choice (4.8). A link alone performs
neither of the latter two operations. Missing imported content stays unresolved; no live lookup can change committed
meaning. Renumbering preserves target identity but refreshes source/display approval; duplicate numbers, ambiguous
editions and dangling anchors fail; navigation cycles are harmless, inference cycles fail.

## 5. What stays frozen

`ve.discourse@1` adds no operator, no checker rule, no symbol, no leaf label and no premise other than the
elaborated formulas themselves and the uniqueness premises of 4.5, which enter through W2's own `asserted` forms;
every such formula is a P0 formula with a P0 `meaning_id` computed under the stripped profile list (3.5). Old
routes, canonical bytes, meanings and certificates are unchanged; the frozen gate never sees `ve.discourse@1`;
`ve.prose@1` behaviour is retained; `ve-document@1` documents load, check and identify exactly as before through
the `@2` loader (`format1_unchanged`). The obligations of VISION's converged rule (a committed failed elaboration
case, conservativity, executable model validity, certificate/countermodel soundness, composition) are met by reuse:
the elaborated formulas go through the unchanged P0/W1/W3 routes, whose theorems apply verbatim; what is new and
must be proved is that the elaboration is faithful to `Intended` (4.4), that the joint disjunction corresponds to
the compatibility relation and that citations and reports extend to it (4.8), that the three adapters preserve
identities and provenance (3.5, 4.5, 4.8), and that bindings are exact (3.3). Existential witness naming is not
presented as W3's unique conservative expansion; there is no witness naming.

**Composition with the norm routes.** An elaborated norm unit enters W1 (`norms@0`) as ordinary norm content with
its rule identity unchanged. Where the soft route (`soft-norms@0`, [soft-norms.md](soft-norms.md) 6) applies to
such a unit, its coherence premises (`Coh_T`, the `conditional_on: soft:coherence:<a>,<b>` list) and its conditional
guarantees are retained unchanged on the elaborated content: no discourse binding discharges, hides or reorders a
coherence premise, and every soft result stays conditional exactly as the soft route states it. Any other
composition (a mention inside an environment `soft` block, a rank, party or decider field, or a reference whose
elaboration would alter `T′` or a regulated predicate's declaration) is explicitly unsupported
(`UnsupportedTarget: <mention>: soft`); it is never silently accepted.

## 6. Modes and the reviewed presentation

Authoring: the IDE asks (2.4), records the signed choice, and the unit's presentation is the expansion. Approval:
the expansion is what is approved; a hidden binding never rescues ambiguous displayed prose. Export: the standalone
export is the expansion with the manifest beside it (as W1's English identity protocol exports text with its
manifest); bare text without the manifest is labelled as such. The expansion is the reviewed presentation in
authoring, approval and export; the source pronoun is kept as provenance only (the `provenance` view shows the source
bytes with the resolved targets as annotations). Translation: the reading set keeps every admitted candidate; the
inventory is "readings considered so far", extensible by anyone and never a claim of exhaustive interpretation.

## 7. The report

### 7.1 Reference lines

Beside W2's open terms, assumptions, bridge leaves and unresolved reading sets, the residual reports:
`references` (per mention: form, target kind, target, `resolved` | `pending` | `ambiguous` | `navigation`; a
pending candidate of a reading set appears here, never in the set), `groups` (each fused reading with its owning
set, spans and status), `presuppositions` (`discourse:presupposition:<mention>: proved (<deduction node>)` |
`assumed (<presupposition_unit>)` | `unresolved`; a report line naming the carrier of 4.5, never a leaf label),
`validity_claims` (checked, refuted, unconfirmed with reason), `self_truth_labels`, `definition_references` (with
pinned versions), `citations` (with retained leaves and the extension verdict of 4.8), `joint_choices` (count,
constraints, or `invalid` / `UNKNOWN(budget)`). Reference-resolution counts are reported separately from C/L/O/R/U
bytes and units and never enter them: a resolved pronoun in an UNFORMALISED unit changes no status.

### 7.2 Status text

```text
RESOLVED: <k> references, <j> pending (<mention ids>), <i> ambiguous; groups: <n>; joint choices: <m> | invalid | UNKNOWN (<budget>)
VALIDITY: <unit>: checked | refuted | unconfirmed (<reason>)
LABELLED self-truth: <unit>
```

### 7.3 Accounting

Exact UTF-8 partitions including punctuation; a group's spans are counted once each under their own span; shared
references never count bytes twice. W2 internally calls open reading sets OPEN, so pilot READINGS are derived from
admitted content, not that enum alone. Splitting or relabelling is reported separately from new semantics;
old-boundary comparisons and certificate/audit provenance are retained. No new measured gain until a rerun.

## 8. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `UnresolvedReference: <mention>` | no accessible target, or the manifest records none | error (authoring: question; translation: READINGS) |
| `AmbiguousReference: <mention>: <targets>` | more than one type-checking accessible target modulo aliases (4.3) | error (as above) |
| `InaccessibleTarget: <mention>: <target>` | recorded target exists but `Acc` fails (scope, competing quantifier, quotation) | error |
| `IllTypedTarget: <mention>: <target>` | the recorded target's elaboration is not closed and well-typed over `E` (a sort mismatch; 1.4, 4.3) | error |
| `UnrecordedSlot: <unit>: <span>` / `MentionNotSlot: <mention>` | the accepted derivation's slots differ from the unit's recorded formula-producing mentions (4.3) | error |
| `WitnessEscape: <mention>` | recorded target is a binder of another sentence or outside its scope | error |
| `TargetKindMismatch: <mention>: <form>, <kind>` | form and target kind do not fit (1.4); a location target in a slot position | error |
| `UnsupportedTarget: <mention>: <kind>` | `this`/`that` as a claim or action term; validity of a `part`; a mention inside soft-route fields (`soft`, 5) | error (READINGS/UNFORMALISED unit) |
| `StaleTarget: <mention>: <target>@<version>` / `StaleTarget: definitions@<version>` / `StaleTarget: <document>` | target content, definition version or `definitions_version` differs from the regenerated one; an import's or embedded unit's pinned fingerprint differs from its bytes (4.1(10)) | error |
| `DanglingAnchor: <anchor>` / `DuplicateAnchor: <label>` / `AmbiguousEdition: <document>` | anchor table (1.2) | error |
| `DependencyCycle: <sorted names>` | definition/proof dependency cycle (4.1(9)); W1's shared text | error |
| `InvalidCompatibility: <sets>` / `InvalidCompatibility: citation <lemma>` / `InvalidCompatibility: report <root>` | empty compatible-joint set after a completed enumeration; a lemma's or a reported result's merged choices extend to no compatible choice (4.8) | error |
| `IndependentFragment: <unit>` | a grouped unit carries content, or a reading set other than the group's owning set (1.5) | error |
| `WitnessSplit: <set>@<version>:<reading>` | a `same-witness` content does not share its witness | error |
| `PresuppositionUnresolved: <mention>` | presuppositional reading with the uniqueness premise neither proved (a certified unit-less deduction) nor assumed (an explicit `presupposition_unit`) (4.5) | pending (not a rejection) |
| `ManifestMismatch: <field>` | regenerated binding, formula, export list, presupposition unit or table differs from the manifest | error |
| `UnknownDocument: <name>` / `DuplicateDeclaration: anchor <id>` / `mention <id>` / `document <name>` / `name <display>` / `content_name <display>` | tables (1.2, 1.3, 1.4, 1.6) | error |
| `ImportCycle: <source ids>` / `ResourceLimit: document nesting` | 4.1(10); nesting inside a validity check is `unconfirmed` (4.7), not an error | error / UNKNOWN |
| `ResourceLimit: mentions` / `anchors` / `joint choices` / `resolution` | limits (11); the last two are UNKNOWN for dependent verdicts (including the extension checks of 4.8) | error / UNKNOWN |
| `InvalidInput: document sort <s> has other constants` / `restriction of <mention> mentions <q>` / `null in discourse block` / `mentions <a>, <b> overlap` / `reading <value>` / `reading <id> not in <set>@<version>` | field consistency (1.4, 1.5, 3.1); a recorded `collective` reading is the decode-time `reading collective` | error |
| `UnsupportedProfile: ve.discourse@1 requires ve-document@2` | profile gate (3.5); the frozen gate's own `UnsupportedProfile` texts for the base list are unchanged | error |
| `ValidityRefuted: <unit>` | a validity claim's polarity disagrees with a completed outcome (4.7) | warning |
| `SelfTruth: <unit>` | a self-truth sentence recognised and labelled (4.7) | label |

Order: wrapper and profile adapter (3.5), the `@1` checks under the base pair, anchors, names, content names and
documents, mentions in source order (existence, kind fit, accessibility, typing, uniqueness, slot correspondence,
elaboration), groups and constraints, the joint set, the dependency DAG, embedded/imported documents (decode,
identity, cycle, depth), limits, then W3 and W2 on the projected document, then the citation and report extension
checks; validity claims are evaluated after admission (4.7). English diagnostics carry the span and the
plain-language expectation as today. Existing P0, W1, W2 and W3 diagnostics are unchanged.

## 9. Lean (sequence 3): definitions and the exact statements to prove

Files: `lean/VE/Discourse/Manifest.lean` (1.2 to 1.6 as data, `WellFormedDiscourse`), `Access.lean` (`Acc`,
`accessible`), `Resolve.lean` (`Slot`, `Derives`, `Accepted`, `validate`), `Elaborate.lean` (`elaborateD`,
`Intended`, faithfulness), `Descriptions.lean`, `Fusion.lean`, `Joint.lean`, `Documents.lean` (document names,
validity, stratification, self-truth, conservativity), `Wire.lean`, `Admission.lean` (`admitDiscourse` over
`ve-document@2`, delegating the unit/graph part to the unchanged `VE.Route.Admission.admitDocument`), `Run.lean`
(the `ve_discourse_route` executable, its own `[[lean_exe]]`), `Examples.lean` (fixture models, proofs by `decide`
or `rfl`, never `native_decide`), and `lean/DISCOURSE.md` listing each theorem in plain words. Frozen `Route/*`,
`Definitions/*`, `Norms/*`, `English/*` and all P0 sources are untouched; `VE.lean`, `VE/Audit.lean` (one
`#print axioms` line per theorem) and `lakefile.toml` gain imports, audit entries and the new target only; the audit
allowlist is unchanged; no file uses `mutual` or a primed theorem name. Names below have prefix `VE.Discourse.`;
W2 names are `VE.Route.Admission.*`, W3 names `VE.Definitions.Bundle.*`, English names `VE.English.*`. The blocks
are statement schemata: helper names are defined here, not already implemented Lean.

### 9.1 Definitions

```lean
namespace VE.Discourse
open VE.Route (Unique)
open VE.Route.Admission (ReadingSet Doc DocUnit Lemma Label parseLabel disjunction WireNode NodeAdmitted AssertedUnit)

/-- 3.5: the profile adapter. The frozen gate never sees `ve.discourse@1`. -/
def baseProfiles (profiles : List String) : List String := profiles.filter (· != "ve.discourse@1")
def baseEnvironment (environment : Json) : Json :=
  environment.setObjVal! "profiles" (toJson (baseProfiles ((VE.Route.Gate.profilesOf environment).toOption.getD [])))
def wrapperOk (profiles : List String) (environment : Json) (j : Json) : Except String Unit
  -- sorted, unique, contains relational-fol@0 and ve.discourse@1, environment "profiles" = profiles, format ve-document@2

inductive TargetKind | entity | predicate | unit | anchor | rule | claim | document
  deriving DecidableEq, Repr
inductive Form
  | pronoun | demonstrative | definite | ordinalPair | such | possessive | plural
  | sectionRef | definitionRef | documentName | citation | navigation
  deriving DecidableEq, Repr
inductive Reading | assertive | presuppositional | distributive deriving DecidableEq, Repr
inductive ConstraintKind | requires | excludes deriving DecidableEq, Repr
inductive DocRefers | self | embedded (unit : String) | imported (key : String) | part (anchor : String)
  deriving DecidableEq, Repr
inductive Verdict | checked | refuted | unconfirmed (reason : String) deriving DecidableEq, Repr

structure Target where
  kind : TargetKind
  name : Option String                -- constant | "binder:<i>" | predicate | anchor | rule | meaning id | document;
                                      -- for ordinalPair the selected member; absent for plural and unit
  version : Option Nat
  members : List String               -- kind entity, form plural: the ordered member constants (n ≥ 2, distinct)
  pair : Option (String × String)     -- kind entity, form ordinalPair: the identified ordered pair
  units : List String                 -- kind unit: the ordered source unit ids
  contentName : Option String         -- kind unit: a registered content name whose units equal `units`
  deriving DecidableEq, Repr

structure Anchor where
  id : String; kind : String; parent : Option String; label : String
  span : Nat × Nat; edition : Option String
  exports : List String               -- the declared predicates whose W3 declarations this anchor exports
  deriving DecidableEq, Repr

structure Name where
  constant : String; display : String; scope : String; aliases : List String
  deriving DecidableEq, Repr

structure ContentName where
  name : String; units : List String; scope : String
  deriving DecidableEq, Repr

structure Mention where
  id : String; unit : String; span : Nat × Nat; form : Form; target : Target
  restriction : Option VE.Formula     -- context [sort]; index 0 is the described entity
  reading : Option Reading
  presuppositionUnit : Option String  -- 4.5, the assumed carrier: an asserted unit whose content is U(D)
  deriving DecidableEq, Repr

/-- A slot of a derivation: a surface position and a form, never a target (4.3). -/
structure Slot where
  unit : String; span : Nat × Nat; form : Form
  deriving DecidableEq, Repr

structure DocName where
  name : String; display : List String; refers : DocRefers
  version : Nat; author : Option String; supersedes : List String; scope : Option String
  sourceId : Option String; documentId : Option String
  deriving DecidableEq, Repr

structure Import where key : String; sourceId : String; documentId : String; bytes : Option ByteArray

structure Group where
  set : String; version : Nat; reading : Nat; spans : List String   -- reading index in the set version
  deriving DecidableEq, Repr

structure Constraint where
  kind : ConstraintKind
  a : String × Nat × Nat              -- (set, version, reading index)
  b : String × Nat × Nat
  deriving DecidableEq, Repr

structure Validity where unit : String; document : String; holds : Bool deriving DecidableEq, Repr

structure Manifest where
  definitionsVersion : String
  documentSort : String
  anchors : List Anchor
  names : List Name
  contentNames : List ContentName
  mentions : List Mention
  documents : List DocName
  imports : List Import
  groups : List Group
  constraints : List Constraint
  validity : List Validity
  selfTruth : List String             -- units labelled self-truth
  choices : List (String × Nat × Nat) -- ρ: the recorded reading choices (authored, or narrowed)

/-- A `ve-document@2` document: W2's decoded document, the manifest, the source and the unit texts. -/
structure DDoc where
  E : VE.Environment
  base : Doc                          -- VE.Route.Admission.Doc, unchanged
  K : Manifest
  sourceId : String
  text : String → Option (List VE.English.Tok)   -- the English text of a unit, tokenised

/-- 4.1 in order; every check returns the diagnostic text of section 8. -/
def wellFormed (D : DDoc) : Except String Unit
def WellFormedDiscourse (D : DDoc) : Bool := (wellFormed D).toBool

/-- 4.2: the accessibility relation, as a proposition and as a list. -/
def innermostAnchor (D : DDoc) (unit : String) : Option Anchor
def registered (D : DDoc) (c : String) : Option Name
def within (D : DDoc) (unit anchor : String) : Bool
def sortOf (E : VE.Environment) (c : String) : Option String := E.constants c
def earlierBinders (D : DDoc) (m : Slot) : List String        -- sorts of the binders of earlier sentences of the innermost anchor and earlier in m's sentence: an input of Acc
def earlierPairs (D : DDoc) (m : Slot) : List (String × String) -- the coordinations "c₁ and c₂" of those sentences: an input of Acc
def earlierProperties (D : DDoc) (m : Slot) : List (String × String) -- (predicate, noun sort) applied restrictively in those sentences: an input of Acc
def competingQuantifier (D : DDoc) (m : Slot) (sort : String) : Bool := sort ∈ earlierBinders D m
def binderScopes (D : DDoc) (m : Slot) (i : Nat) : Bool                   -- binder i of m's own sentence scopes over m's slot
def candidateSort (D : DDoc) (m : Slot) (t : Target) : Option (List String) -- 1.4: the sort(s) of an entity candidate; a predicate's argument sort for such
def formFits (f : Form) (k : TargetKind) : Bool
def Acc (D : DDoc) (m : Slot) (t : Target) : Prop                          -- 4.2; sorts play no part
def accessible (D : DDoc) (m : Slot) : List Target
def AliasEq (D : DDoc) (t t' : Target) : Prop                              -- equal, or the same constant(s) through declared aliases

/-- 4.3: derivations with slots; the independent resolution relation. -/
structure DTree where tree : VE.English.Tree; slots : List Slot
def Derives (D : DDoc) (s : List VE.English.Tok) (d : DTree) : Prop
def Assignment := Slot → Target
def recordedTarget (D : DDoc) (m : Slot) : Option Target :=              -- K.target(m): the mention of K.mentions at (unit, span, form)
  (D.K.mentions.find? (fun x => x.unit == m.unit && x.span == m.span && x.form == m.form)).map Mention.target
def recordedSlots (D : DDoc) (u : String) : List Slot                     -- the formula-producing mentions of u as slots, source order
def elaborateD (D : DDoc) (d : DTree) (σ : Assignment) : Option VE.Formula   -- capture-avoiding slot substitution under D.K.choices (ρ), a fixed input
/-- One recorded, typed (d, σ) first; every type-checking competitor equals it. The type check is the only filter. -/
def Accepted (D : DDoc) (s : List VE.English.Tok) (A : VE.Formula) : Prop :=
  ∃ d σ, Derives D s d ∧ (∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m)) ∧
    elaborateD D d σ = some A ∧ A.check D.E [] = true ∧
    ∀ d' σ' A', Derives D s d' → (∀ m ∈ d'.slots, Acc D m (σ' m)) →
      elaborateD D d' σ' = some A' → A'.check D.E [] = true →
      d'.tree = d.tree ∧ d'.slots = d.slots ∧ ∀ m ∈ d.slots, AliasEq D (σ' m) (σ m)
/-- The executable validator (untrusted proposals in, one formula out); fuel = mentions + anchors + 1.
    Also checks recordedSlots D unit = d.slots (UnrecordedSlot / MentionNotSlot). -/
def validate (D : DDoc) (unit : String) : Except String VE.Formula
def Supported (D : DDoc) (s : List VE.English.Tok) : Prop        -- the supported fragment: forms of 1.4 over the core grammar

/-- 4.4: the intended meaning, by recursion on the derivation against S. -/
def SlotDenote (D : DDoc) (S : VE.Structure) (m : Slot) (t : Target) : (S.Carrier → Prop) → Prop
def Intended (D : DDoc) (s : List VE.English.Tok) (S : VE.Structure) : Prop   -- ∃ accepted (d, σ), the derivation's meaning with SlotDenote

/-- 4.5: every constructor is parameterised by the binder sort σ (P0's `.ex σ` / `.all σ`). -/
def uniqueD (σ : String) (Dr : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.all σ (.implies Dr (.eq (.var 0) (.var 1)))))       -- ∃x:σ (Dr x ∧ ∀y:σ (Dr y → y = x)); de Bruijn: var 0 the innermost binder
def assertive (σ : String) (Dr P : VE.Formula) : VE.Formula                   -- ∃x:σ (Dr x ∧ ∀y:σ (Dr y → y = x) ∧ P x)
def presupposed (σ : String) (Dr P : VE.Formula) : VE.Formula := .all σ (.implies Dr P)   -- ∀x:σ (Dr x → P x)
def restrictionSort (D : DDoc) (m : Mention) : Option String              -- the sort the restriction's context [σ] names
/-- The two frozen carriers of U(D) (no `discourse:*` label reaches W2). -/
inductive PresuppositionCarrier
  | proved (node : String)             -- a unit-less `asserted` deduction node named `node`, carrying its certificate
  | assumed (unit : String)            -- the explicit asserted unit named by presuppositionUnit
  deriving DecidableEq, Repr
def presuppositionLine (m : Mention) (c : Option PresuppositionCarrier) : String   -- 7.1: "discourse:presupposition:<m>: proved (<node>) | assumed (<unit>) | unresolved"

/-- 4.6 -/
def fused (σ : String) (φ ψ : VE.Formula) : VE.Formula := .ex σ (.and φ ψ)   -- one binder of sort σ
def sharedWitness (φ : VE.Formula) : Bool
def groupFormula (D : DDoc) (g : Group) : Option VE.Formula                -- the owning set's reading, regenerated per group
def owningUnit (D : DDoc) (g : Group) : Option String := g.spans.head?     -- W2 places the owning set here
def groupedUnits (D : DDoc) : List String

/-- 4.8 -/
abbrev Choice := List (String × Nat × Nat)
def activeSets (D : DDoc) : List ReadingSet                      -- W2's latest version per unit, open sets only
def chosen (c : Choice) (x : String × Nat × Nat) : Prop := x ∈ c
def Satisfies (c : Choice) : Constraint → Prop
  | ⟨.requires, a, b⟩ => chosen c a → chosen c b
  | ⟨.excludes, a, b⟩ => ¬ (chosen c a ∧ chosen c b)
def Compatible (K : Manifest) (sets : List ReadingSet) (c : Choice) : Prop :=
  c.length = sets.length ∧
  (∀ i (h : i < sets.length), ∃ r, c[i]? = some (sets[i].id, sets[i].version, r) ∧ r < sets[i].readings.length) ∧
  ∀ k ∈ K.constraints, Satisfies c k
def productSize (sets : List ReadingSet) : Nat := sets.foldl (fun n rs => n * rs.readings.length) 1
def compatibleChoices (K : Manifest) (sets : List ReadingSet) (limit : Nat) : Except String (List Choice)
  -- .error "ResourceLimit: joint choices" when productSize sets > limit (validation not completed);
  -- .error "InvalidCompatibility: <sets>" when the completed enumeration is empty; sets = [] ↦ .ok [[]]
def readingsOf (sets : List ReadingSet) (c : Choice) : List VE.Formula
def conj : List VE.Formula → VE.Formula                          -- right-nested ∧; [] ↦ .top
  | [] => .top
  | [a] => a
  | a :: as => .and a (conj as)
def joint (sets : List ReadingSet) (cs : List Choice) : Option VE.Formula   -- disjunction of the conj's; cs = [] ↦ none; [[]] ↦ some .top
def occurring (sets : List ReadingSet) (cs : List Choice) : List VE.Formula  -- every reading in some c ∈ cs

/-- 4.8, the composition gate: a W3 choice list (set ↦ "v:i" | "v:all") extends to a compatible choice. -/
def ExtendsTo (ch : List (String × String)) (c : Choice) : Prop :=
  ∀ e ∈ ch, ∃ v i, (e.1, v, i) ∈ c ∧ (e.2 = toString v ++ ":" ++ toString i ∨ e.2 = toString v ++ ":all")
def extendsTo (ch : List (String × String)) (c : Choice) : Bool
def citationExtendsJoint (cs : List Choice) (L : VE.Definitions.Bundle.Lemma) : Except String Unit
  -- leafChoices L.leaves = .ok ch and cs.any (extendsTo ch), else "InvalidCompatibility: citation <L.name>"
def reportExtendsJoint (cs : List Choice) (r : VE.Graph.Report) : Except String Unit
  -- leafChoices (r.assumptions.map (fun l => (l.label, l.formula))) = .ok ch and cs.any (extendsTo ch),
  -- else "InvalidCompatibility: report <r.root.name>"

/-- 4.7 -/
def stripValidity (D : DDoc) : DDoc := { D with K := { D.K with validity := [] } }
def refersSelf (D : DDoc) (name : String) : Prop := ∃ d ∈ D.K.documents, d.name = name ∧ d.refers = .self
def refersImport (D : DDoc) (name key : String) : Prop := ∃ d ∈ D.K.documents, d.name = name ∧ d.refers = .imported key
def withDocuments (E : VE.Environment) (sort : String) (names : List String) : VE.Environment
def importNodes (D : DDoc) : List VE.Route.DepNode              -- source id → source ids it embeds or imports
/-- 4.7: the three outcomes of checking another document; rejection is a completed diagnostic. -/
inductive ImportOutcome | admitted | rejected (diagnostic : String) | unknown (reason : String)
  deriving DecidableEq, Repr
def outcomeOf : Except String Admitted → ImportOutcome
  | .ok _ => .admitted
  | .error e => if e.startsWith "ResourceLimit" then .unknown e else .rejected e
def checkImport (profiles : List String) (b : ByteArray) (fuel : Nat) : ImportOutcome   -- fuel = 0 ↦ .unknown "ResourceLimit: document nesting"
def verdictOf (holds : Bool) : ImportOutcome → Verdict
  | .admitted => if holds then .checked else .refuted
  | .rejected _ => if holds then .refuted else .checked
  | .unknown r => .unconfirmed r

structure Admitted where
  doc : DDoc
  base : VE.Route.Admission.Admitted                             -- the unchanged W2 result on the elaborated document, under (baseProfiles, baseEnvironment)
  documentId : String
  reportId : String                                              -- the wrapper report identity (3.3), over the original profile list
  bound : String → Option VE.Formula                             -- the elaborated formula of each bound unit
  joint : Except String (List Choice)                            -- the validated joint set, or its ResourceLimit (UNKNOWN)
  presuppositions : String → Option PresuppositionCarrier        -- per presuppositional mention id; none = unresolved
  pending : List (String × String)                               -- (unit, diagnostic) for pending units (PresuppositionUnresolved, pending candidates)
  validity : String → Option Verdict
  selfTruth : List String
  premiseUnits : List String

def admitDiscourse (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) : Except String Admitted
  -- wrapperOk profiles environment j; then every frozen call on (baseProfiles profiles, baseEnvironment environment)
def documentId2 (front : Json) (prose : ByteArray) (fences : List (String × String)) : String
def project1 (j : Json) : Json                                    -- the ve-document@1 document with elaborated content in place of bound units
```

`VE.Route.DepNode` and `VE.Route.dependencyOrder` are the shared DAG machinery (W1 4.1); `Wire.RouteVocabulary`,
`Wire.decodeClosed`, `Wire.meaningId`, `Wire.environmentId`, `VE.Route.Gate.{decodeEnvelope, classify,
profilesOf}`, `VE.Route.Admission.Admitted` are the frozen P0/W2 names; `Formula.ex`, `Formula.all`,
`Formula.top`, `Formula.eq` and `Structure.domain` are P0's constructors and typing (`VE.TypedAt` does not exist:
typed membership is `S.domain σ a`). The tuple and valuation conventions are P0's: closed formulas use `[]`; a
description's restriction is evaluated at `[a]`. `LexiconCovers L E` (9.5) is the lexicon admission/coverage
hypothesis: every sort of `E` is in `L.sorts`, every declared constant in `L.constants` with the registered
display form (1.3) among its spellings, and every declared predicate has a template of its arity (the executable
`VE.English.Run.covers`, as a proposition over `E`).

### 9.2 Theorems: accessibility and resolution (plan obligation 1)

```lean
/-- The list and the relation agree. -/
theorem accessible_iff (D : DDoc) (m : Slot) (t : Target) : t ∈ accessible D m ↔ Acc D m t

/-- No heuristic: accessibility depends only on registrations, content names, anchors, declarations, the slot's
    unit, span and form, own-sentence binders, and the binders, coordinations and restrictive properties of the
    earlier sentences of the innermost anchor (4.2). Two documents agreeing on those inputs agree on Acc, whatever
    else they contain: the hypotheses are the inputs, not the conclusion. -/
theorem acc_no_heuristic (D D₂ : DDoc) (m : Slot) (t : Target)
    (hK : D.K.names = D₂.K.names ∧ D.K.contentNames = D₂.K.contentNames ∧ D.K.anchors = D₂.K.anchors ∧
          D.K.documents = D₂.K.documents ∧ D.K.definitionsVersion = D₂.K.definitionsVersion ∧ D.E = D₂.E)
    (ha : innermostAnchor D m.unit = innermostAnchor D₂ m.unit)
    (ht : ∀ a u, innermostAnchor D m.unit = some a → within D u a.id = true → D.text u = D₂.text u)
    (hb : D.base.units.map DocUnit.id = D₂.base.units.map DocUnit.id) :
  Acc D m t ↔ Acc D₂ m t

/-- Neither the recorded targets nor the reading choices are inputs of Acc (no pruning). -/
theorem acc_ignores_manifest_choices (D : DDoc) (m : Slot) (t : Target) (ms : List Mention) (ρ : List (String × Nat × Nat)) :
  Acc D m t ↔ Acc { D with K := { D.K with mentions := ms, choices := ρ } } m t

/-- Witness scope: a binder target is accessible only inside its own sentence and under its scope. -/
theorem no_witness_escape (D : DDoc) (m : Slot) (i : Nat)
    (h : ¬ binderScopes D m i) : ¬ Acc D m ⟨.entity, some ("binder:" ++ toString i), none, [], none, [], none⟩

/-- Names are scope-based, not distance-based: a registered constant is accessible at every unit of its scope
    without a competing quantifier of its sort, and at no unit outside it. -/
theorem name_scope (D : DDoc) (m : Slot) (c s : String) (n : Name) (hn : registered D c = some n)
    (hs : sortOf D.E c = some s) (hf : m.form = .pronoun ∨ m.form = .demonstrative) :
  Acc D m ⟨.entity, some c, none, [], none, [], none⟩ ↔
    within D m.unit n.scope = true ∧ competingQuantifier D m s = false

/-- Kinds never coerce. -/
theorem kind_fit (D : DDoc) (m : Slot) (t : Target) (h : Acc D m t) : formFits m.form t.kind = true

/-- The validator is sound: whatever it returns is the unique accepted resolution of that unit's text. -/
theorem validate_sound (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List VE.English.Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) : Accepted D s A

/-- Slot correspondence: the recorded formula-producing mentions of the unit are the accepted derivation's slots. -/
theorem validate_slots_recorded (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List VE.English.Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) :
  ∃ d σ, Derives D s d ∧ (∀ m ∈ d.slots, recordedTarget D m = some (σ m)) ∧ elaborateD D d σ = some A ∧
    recordedSlots D u = d.slots

/-- The type check is the only filter: an ill-typed recorded target is the named error, and a competitor is
    excluded only by failing the check. -/
theorem ill_typed_target (D : DDoc) (u : String) (s) (hs : D.text u = some s) (d : DTree) (σ : Assignment)
    (hd : Derives D s d) (hr : ∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m))
    (m : Slot) (hm : m ∈ d.slots) (A : VE.Formula) (he : elaborateD D d σ = some A) (hc : A.check D.E [] = false) :
  ∃ e, validate D u = .error e ∧ e.startsWith ("IllTypedTarget: " ++ mentionIdAt D m)
theorem accepted_no_pruning (D : DDoc) (s : List VE.English.Tok) (A : VE.Formula) (h : Accepted D s A)
    (d' : DTree) (σ' : Assignment) (A' : VE.Formula) (hd : Derives D s d') (ha : ∀ m ∈ d'.slots, Acc D m (σ' m))
    (he : elaborateD D d' σ' = some A') (hc : A'.check D.E [] = true) : A' = A

/-- Complete on the supported fragment within fuel. -/
theorem validate_complete (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (s) (hs : D.text u = some s)
    (hsup : Supported D s) (A : VE.Formula) (hA : Accepted D s A) : validate D u = .ok A

/-- Exactly one accepted formula. -/
theorem accepted_unique (D : DDoc) (s : List VE.English.Tok) (A A' : VE.Formula)
    (h : Accepted D s A) (h' : Accepted D s A') : A = A'

/-- Closed and typed. -/
theorem validate_closed (D : DDoc) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
  A.check D.E [] = true

/-- Total: the validator never loops; resource exhaustion is the named error, never a formula. -/
theorem validate_total (D : DDoc) (u : String) :
  (∃ A, validate D u = .ok A) ∨ (∃ e, validate D u = .error e)
theorem validate_budget (D : DDoc) (u : String) (hover : D.K.mentions.length > mentionLimit) :
  validate D u = .error "ResourceLimit: resolution"

/-- Capture-avoiding substitution: the slot substitution denotes the slot's value under any valuation in which the
    substituted terms' free variables are bound as in the sentence. -/
theorem elaborateD_capture (D : DDoc) (d : DTree) (σ : Assignment) (A : VE.Formula) (h : elaborateD D d σ = some A)
    (S : VE.Structure) (hS : S.Admissible D.E) (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S (contextOf d) ρ) :
  A.denote S ρ ↔ SlotMeaning D S ρ d σ
```

### 9.3 Theorems: elaboration, descriptions and fusion (plan obligation 2)

```lean
/-- 4.4: the elaborated formula holds exactly when the intended meaning does, on every admissible structure. -/
theorem elaborate_faithful (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (s) (hs : D.text u = some s)
    (A : VE.Formula) (hv : validate D u = .ok A) (S : VE.Structure) (hS : S.Admissible D.E) :
  A.denote S [] ↔ Intended D s S

/-- No new symbols: the elaboration is well-formed over E itself. -/
theorem elaborate_no_new_symbols (D : DDoc) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
  A.WellFormed D.E [] ∧ ∀ q ∈ VE.symbolsOf A, q ∈ VE.symbolsOf D.E

/-- 4.5: definedness of the assertive reading, at the binder sort σ. -/
theorem description_definedness (E : VE.Environment) (σ : String) (hσ : σ ∈ E.sorts) (Dr P : VE.Formula)
    (hD : Dr.WellFormed E [σ]) (hP : P.WellFormed E [σ]) (S : VE.Structure) (hS : S.Admissible E) :
  (assertive σ Dr P).denote S [] ↔ (uniqueD σ Dr).denote S [] ∧ (presupposed σ Dr P).denote S []

/-- The assertive reading is the unique-element statement, element-wise, over the sort's domain. -/
theorem assertive_denote (E : VE.Environment) (σ : String) (hσ : σ ∈ E.sorts) (Dr P : VE.Formula)
    (hD : Dr.WellFormed E [σ]) (hP : P.WellFormed E [σ]) (S : VE.Structure) (hS : S.Admissible E) :
  (assertive σ Dr P).denote S [] ↔
    ∃ a, S.domain σ a ∧ Dr.denote S [a] ∧ (∀ b, S.domain σ b → Dr.denote S [b] → b = a) ∧ P.denote S [a]

/-- The presuppositional claim is proved only where U(D) holds: a checked certificate for the claim over premises
    that include U(D) (the P0 acceptance theorem, instantiated; reused, not restated). -/
theorem presupposition_retained (E : VE.Environment) (Γ : List VE.Formula) (σ : String) (Dr P : VE.Formula)
    (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E (Γ ++ [uniqueD σ Dr]) (presupposed σ Dr P) c = true)
    (S : VE.Structure) (hS : S.Admissible E) (hΓ : VE.Norms.Sat S Γ) (hU : (uniqueD σ Dr).denote S []) :
  (presupposed σ Dr P).denote S []

/-- The two carriers (4.5): in an admitted document every presuppositional mention's U(D) is either a certified
    unit-less `asserted` deduction node or an explicit asserted unit named by presuppositionUnit, and otherwise the
    unit is pending with the named diagnostic. No `discourse:*` label exists in the report. -/
theorem presupposition_carried (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (m : Mention) (hm : m ∈ res.doc.K.mentions)
    (hr : m.reading = some .presuppositional) (Dr : VE.Formula) (hD : m.restriction = some Dr)
    (σ : String) (hσ : restrictionSort res.doc m = some σ) :
  (∃ n w, res.presuppositions m.id = some (.proved n) ∧ w ∈ res.base.wires ∧ w.claim.name = n ∧
     w.unit = none ∧ w.deduction.isSome ∧ w.claim.label = "asserted" ∧ w.claim.formula = uniqueD σ Dr) ∨
  (∃ u, res.presuppositions m.id = some (.assumed u) ∧ m.presuppositionUnit = some u ∧
     AssertedUnit res.base.doc u (uniqueD σ Dr) ∧ u ∈ res.premiseUnits) ∨
  (res.presuppositions m.id = none ∧ (m.unit, "PresuppositionUnresolved: " ++ m.id) ∈ res.pending ∧
     res.bound m.unit = none)
theorem no_discourse_label (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  ∀ leaf ∈ res.base.report.assumptions, (parseLabel leaf.label).isSome

/-- 4.6: a group's reading is one formula regenerated per group; exactly one leaf carries the owning set when it is
    used; every span has the owning set's status, no content, no bound formula and is no premise unit. -/
theorem group_single_assertion (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (g : Group) (hg : g ∈ res.doc.K.groups) :
  (∃ rs ∈ res.base.doc.readingSets, rs.id = g.set ∧ rs.version = g.version ∧
     ∃ φ, groupFormula res.doc g = some φ ∧ rs.readings[g.reading]? = some φ) ∧
  owningUnit res.doc g = g.spans.head? ∧
  (res.base.report.assumptions.filter (fun l => setOfLabel l.label = some (g.set, g.version))).length ≤ 1 ∧
  (∀ l ∈ res.base.report.assumptions, l.label = "asserted" → ∀ u ∈ g.spans, unitOfLeaf res l ≠ some u) ∧
  ∀ u ∈ g.spans, (unitOf res.base.doc u).bind DocUnit.content = none ∧ res.bound u = none ∧
    u ∉ res.premiseUnits ∧ statusOf res u = statusOf res (g.spans.head!)

/-- The fused reading implies the split reading; the converse is refuted on a concrete model (Examples.lean). -/
theorem fused_implies_split (E : VE.Environment) (σ : String) (hσ : σ ∈ E.sorts) (φ ψ : VE.Formula)
    (hφ : φ.WellFormed E [σ]) (hψ : ψ.WellFormed E [σ]) :
  VE.Entails E [fused σ φ ψ] (.and (.ex σ φ) (.ex σ ψ))
theorem split_not_fused_model :
  (Examples.splitFormula).eval Examples.twoServices [] = true ∧
  (Examples.fusedFormula).eval Examples.twoServices [] = false

/-- Shared witness is decided syntactically and is what the group check requires. -/
theorem sharedWitness_spec (φ : VE.Formula) :
  sharedWitness φ = true ↔ ∃ σ body, φ = .ex σ body ∧ IsConjunctionMentioningZero body
```

### 9.4 Theorems: joint choices and citation composition (plan obligation 4)

```lean
/-- The enumeration is exactly the compatibility relation, and never empty on success. -/
theorem compatible_sound (K : Manifest) (sets : List ReadingSet) (n : Nat) (cs : List Choice)
    (h : compatibleChoices K sets n = .ok cs) : (∀ c, c ∈ cs ↔ Compatible K sets c) ∧ cs ≠ [] ∧ cs.length ≤ n
/-- Emptiness is reported only by a completed enumeration (the product within the limit); beyond it the result is
    the resource error, never InvalidCompatibility. -/
theorem compatible_empty_error (K : Manifest) (sets : List ReadingSet) (n : Nat) (hfin : productSize sets ≤ n)
    (hε : ∀ c, ¬ Compatible K sets c) :
  compatibleChoices K sets n = .error ("InvalidCompatibility: " ++ setsText sets)
theorem compatible_budget (K : Manifest) (sets : List ReadingSet) (n : Nat) (hover : productSize sets > n) :
  compatibleChoices K sets n = .error "ResourceLimit: joint choices"
/-- Zero open sets: the one empty choice, whose conjunction is top. -/
theorem compatible_no_sets (K : Manifest) (n : Nat) : compatibleChoices K [] n = .ok [[]] ∧ Compatible K [] []
theorem conj_nil : conj [] = .top
theorem joint_no_sets : joint [] [[]] = some .top

/-- 4.8: the joint disjunction holds iff some compatible choice holds. -/
theorem joint_denote (sets : List ReadingSet) (cs : List Choice) (J : VE.Formula) (hJ : joint sets cs = some J)
    (S : VE.Structure) : J.denote S [] ↔ ∃ c ∈ cs, ∀ r ∈ readingsOf sets c, r.denote S []

/-- ALL over the joint set is one entailment from the disjunction. -/
theorem joint_all_iff (E : VE.Environment) (K) (sets) (cs) (Γ : List VE.Formula) (φ J : VE.Formula)
    (hcs : compatibleChoices K sets 64 = .ok cs) (hJ : joint sets cs = some J) :
  VE.Entails E (Γ ++ [J]) φ ↔ ∀ c ∈ cs, VE.Entails E (Γ ++ readingsOf sets c) φ

/-- With no constraints the joint set is the product and W2's shortcut is regained (VE.Route.readings_all_iff). -/
theorem unconstrained_product (K) (hK : K.constraints = []) (sets) (cs) (hcs : compatibleChoices K sets 64 = .ok cs)
    (S : VE.Structure) :
  (∃ c ∈ cs, ∀ r ∈ readingsOf sets c, r.denote S []) ↔ ∀ rs ∈ sets, ∃ r ∈ rs.readings, r.denote S []

/-- NONE: one shared model refutes every compatible choice. -/
theorem joint_none_sound {α} [DecidableEq α] (E) (sets) (cs) (Γ : List VE.Formula) (φ : VE.Formula)
    (M : VE.FiniteModel α) (valid : M.Valid E) (hΓ : ∀ g ∈ Γ, g.eval M [] = true)
    (hr : ∀ r ∈ occurring sets cs, r.eval M [] = true) (hφ : φ.eval M [] = false) :
  ∀ c ∈ cs, ¬ VE.Entails E (Γ ++ readingsOf sets c) φ

/-- SOME: a certificate for one compatible choice and a countermodel for another. -/
theorem joint_some_sound {α} [DecidableEq α] (E) (sets) (cs) (Γ) (φ) (c₁ c₂ : Choice) (h₁ : c₁ ∈ cs) (h₂ : c₂ ∈ cs)
    (cert : VE.Tableau.Certificate) (acc : VE.Tableau.checkCertificate E (Γ ++ readingsOf sets c₁) φ cert = true)
    (M : VE.FiniteModel α) (valid : M.Valid E) (hΓ : ∀ g ∈ Γ, g.eval M [] = true)
    (hr : ∀ r ∈ readingsOf sets c₂, r.eval M [] = true) (hφ : φ.eval M [] = false) :
  VE.Entails E (Γ ++ readingsOf sets c₁) φ ∧ ¬ VE.Entails E (Γ ++ readingsOf sets c₂) φ

/-- Independence: without constraints, on a completed enumeration of nonempty sets, the per-unit shortcut and the
    joint enumeration give the same verdicts. -/
theorem independent_shortcut (E : VE.Environment) (K : Manifest) (hK : K.constraints = []) (sets : List ReadingSet)
    (hne : ∀ rs ∈ sets, rs.readings ≠ []) (cs : List Choice) (hcs : compatibleChoices K sets 64 = .ok cs)
    (Γ : List VE.Formula) (φ J : VE.Formula) (hJ : joint sets cs = some J) :
  VE.Entails E (Γ ++ [J]) φ ↔ VE.Entails E (Γ ++ (sets.filterMap (fun rs => disjunction rs.readings))) φ

/-- Citation composition is W3's, reused with its per-set meaning: a citing lemma's transitive leaves include every
    cited leaf, its reading choices agree within each set, and the manifest's recorded choices equal the choices
    derived from the leaves. -/
theorem citation_choices_retained (E : VE.Environment) (bg : List VE.Definitions.Bundle.Leaf) (sets : List ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
    (known : List VE.Definitions.Bundle.Known) (L : VE.Definitions.Bundle.Lemma) (k : VE.Definitions.Bundle.Known)
    (h : VE.Definitions.Bundle.checkLemma E bg sets bind known L = .ok k) :
  VE.Definitions.Bundle.ReadingCompatible k.leaves ∧
  (∀ m ∈ L.cites, ∀ k' ∈ known, k'.meaningId = m → ∀ l ∈ k'.leaves, l ∈ k.leaves) ∧
  VE.Definitions.Bundle.choicesEqual L.choices k.choices = true
theorem manifest_choices_are_labels (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (L : VE.Definitions.Bundle.Lemma) (hL : L ∈ lemmasOf res.doc) :
  VE.Definitions.Bundle.leafChoices L.leaves = .ok (choicesAsLabels res.doc.K.choices L)   -- via original_index (1.5)

/-- 4.8, the composition gate. Each lemma's transitive choices, and the merged transitive assumptions of every
    reported graph result, extend to a validated compatible choice; failure after a completed enumeration is the
    named InvalidCompatibility; an unfinished enumeration leaves every reading-dependent verdict UNKNOWN. -/
theorem citation_extends_joint (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (cs : List Choice) (hcs : res.joint = .ok cs)
    (L : VE.Definitions.Bundle.Lemma) (hL : L ∈ lemmasOf res.doc) (ch : List (String × String))
    (hch : VE.Definitions.Bundle.leafChoices L.leaves = .ok ch) :
  ∃ c ∈ cs, ExtendsTo ch c
theorem report_extends_joint (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (cs : List Choice) (hcs : res.joint = .ok cs)
    (ch : List (String × String))
    (hch : VE.Definitions.Bundle.leafChoices (res.base.report.assumptions.map (fun l => (l.label, l.formula))) = .ok ch) :
  ∃ c ∈ cs, ExtendsTo ch c
theorem extension_rejected (profiles) (environment) (rv) (j) (fuel) (K : Manifest) (sets : List ReadingSet) (cs : List Choice)
    (hK : manifestOf j = .ok K) (hsets : activeSetsOf j = .ok sets) (hcs : compatibleChoices K sets 64 = .ok cs)
    (L : VE.Definitions.Bundle.Lemma) (hL : L ∈ lemmasOfJson j) (ch : List (String × String))
    (hch : VE.Definitions.Bundle.leafChoices L.leaves = .ok ch) (hno : ∀ c ∈ cs, ¬ ExtendsTo ch c)
    (hw3 : w3Passes j L) :
  admitDiscourse profiles environment rv j fuel = .error ("InvalidCompatibility: citation " ++ L.name)
theorem extension_unknown (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (hb : res.joint = .error "ResourceLimit: joint choices") :
  (∀ e, e ∈ res.pending → ¬ (e.2.startsWith "InvalidCompatibility")) ∧
  ∀ v ∈ readingVerdicts res, v.2 = "UNKNOWN (joint choices)"
```

### 9.5 Theorems: English correspondence and binding (plan obligation 5)

```lean
/-- The discourse surface. Meaning := VE.Formula (the elaborated formula, closed and typed): an assignment is
    provenance validated separately (validate_slots_recorded), not part of the meaning, because the expansion has
    no slots and a (formula, assignment) meaning could not round-trip through ParseRender. Text := unit token lists;
    Derivation := DTree with Derives; yield := the source text; render := the reviewed presentation (the expansion,
    ordinary core English); parse := the core parser lifted to one formula; admitted := the formulas validate returns. -/
def LexiconCovers (L : VE.English.Lexicon) (E : VE.Environment) : Prop
def presentation (D : DDoc) (L : VE.English.Lexicon) (u : String) : List VE.English.Tok
def discourseSurface (D : DDoc) (L : VE.English.Lexicon) : VE.English.Surface where
  Text := List VE.English.Tok
  Meaning := VE.Formula
  Derivation := DTree
  admitted := fun A => ∃ u, validate D u = .ok A
  render := fun A => presentation D L (unitOfFormula D A)
  parse := fun s => match VE.English.parse D.E L s with | some [A] => some A | _ => none
  derives := Derives D (textOf D)
  yield := fun d => yieldOf D L d
  reading := fun d => elaborateD D d (recordedAssignment D d)

theorem discourse_parseRender (D : DDoc) (h : WellFormedDiscourse D = true) (L : VE.English.Lexicon)
    (hL : LexiconCovers L D.E) : VE.English.ParseRender (discourseSurface D L)
  -- from presentation_expands and the core surface's round trip
theorem discourse_uniqueDerivation (D : DDoc) (h : WellFormedDiscourse D = true) (L : VE.English.Lexicon)
    (hL : LexiconCovers L D.E) : VE.English.UniqueDerivation (discourseSurface D L)
  -- Accepted's uniqueness clause: one tree, one slot list
theorem discourse_parseSound (D : DDoc) (h : WellFormedDiscourse D = true) (L : VE.English.Lexicon)
    (hL : LexiconCovers L D.E) : VE.English.ParseSound (discourseSurface D L)
theorem discourse_oneReading (D : DDoc) (h : WellFormedDiscourse D = true) (L : VE.English.Lexicon)
    (hL : LexiconCovers L D.E) : VE.English.OneReading (discourseSurface D L)
  -- := VE.English.oneReading_of (discourse_parseSound D h L hL) (discourse_uniqueDerivation D h L hL)

/-- The reviewed presentation is ordinary English with the same formula: the expansion parses, through the unchanged
    core parser, to exactly the elaborated formula. -/
theorem presentation_expands (D : DDoc) (h : WellFormedDiscourse D = true) (L : VE.English.Lexicon)
    (hL : LexiconCovers L D.E) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
  VE.English.parse D.E L (presentation D L u) = some [A]
```

### 9.6 Theorems: documents, validity, conservativity and the wire

```lean
/-- The `@1` path is delegated unchanged when the profile is off; with the profile on, a `@1` document is the
    profile-gate error (1.1), never a silent delegation. -/
theorem format1_unchanged (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json) (fuel : Nat)
    (h1 : (j.getObjValD "format").getStr? = .ok "ve-document@1") (hp : "ve.discourse@1" ∉ profiles) :
  admitDiscourse profiles environment rv j fuel = (VE.Route.Admission.admitDocument profiles environment rv j).map lift1
theorem format1_profile_requires_format2 (profiles) (environment) (rv) (j : Json) (fuel)
    (h1 : (j.getObjValD "format").getStr? = .ok "ve-document@1") (hp : "ve.discourse@1" ∈ profiles) :
  admitDiscourse profiles environment rv j fuel = .error "UnsupportedProfile: ve.discourse@1 requires ve-document@2"

/-- 3.5: the frozen gate runs on the base pair, and its verdict on the base list is unchanged. -/
theorem profile_adapter_base (profiles : List String) (environment : Json) (hw : wrapperOk profiles environment j = .ok ()) :
  VE.Route.Gate.profilesOf (baseEnvironment environment) = .ok (baseProfiles profiles) ∧
  "ve.discourse@1" ∉ baseProfiles profiles ∧
  (VE.Route.Gate.decodeEnvelope (baseEnvironment environment)).map VE.Route.Gate.Envelope.family =
    VE.Route.Gate.classify (baseProfiles profiles)

/-- The `@2` admission is W2's admission of the projected document under the base pair, plus the discourse checks;
    stated for `@2` inputs only. -/
theorem admission_projects (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h2 : (j.getObjValD "format").getStr? = .ok "ve-document@2")
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  VE.Route.Admission.admitDocument (baseProfiles profiles) (baseEnvironment environment) rv (project1 j) = .ok res.base ∧
  WellFormedDiscourse res.doc = true ∧
  (∀ u A, res.bound u = some A → validate res.doc u = .ok A) ∧
  res.documentId = documentId2 (frontMatter j) (prose j) (fences j)

/-- The W2 soundness statement transfers verbatim to the elaborated document (reused: admit_report_sound). -/
theorem discourse_report_sound (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  VE.Graph.SoundReport.{u} rv.environment res.base.graph res.base.report ∧
  (∀ w ∈ res.base.wires, VE.Route.Admission.NodeAdmitted res.base.doc w) ∧
  VE.Route.Admission.CitationsClosed res.base.doc res.base.report ∧ VE.Route.Admission.ChoicesCompatible res.base.report

/-- 4.7: admission never reads a validity unit. -/
theorem validity_independent (profiles) (environment) (rv) (j) (fuel) :
  (admitDiscourse profiles environment rv j fuel).map Admitted.base =
    (admitDiscourse profiles environment rv (stripValidityJson j) fuel).map Admitted.base
theorem validity_self (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (hs : refersSelf res.doc v.document) :
  res.validity v.unit = some (if v.holds then .checked else .refuted)
/-- An import's verdict follows its outcome: rejection is a completed diagnostic, and absent bytes, a resource
    limit or the nesting budget are `unconfirmed` for either polarity (never `checked` for a negative claim). The
    integrity of the stored bytes is a well-formedness condition (stale_import_rejected), not a case here. -/
theorem validity_import (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (key : String) (hi : refersImport res.doc v.document key)
    (imp : Import) (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) :
  (imp.bytes = none → res.validity v.unit = some (.unconfirmed "import bytes absent")) ∧
  (∀ b, imp.bytes = some b → res.validity v.unit = some (verdictOf v.holds (checkImport profiles b fuel))) ∧
  (∀ b, imp.bytes = some b → checkImport profiles b fuel = outcomeOf (admitDiscourse profiles (envOf b) (rvOf b) (jsonOf b) fuel))
theorem validity_unknown_never_checked (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (key) (hi : refersImport res.doc v.document key) (imp : Import)
    (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) (b) (hb : imp.bytes = some b) (r : String)
    (hu : checkImport profiles b fuel = .unknown r) :
  res.validity v.unit = some (.unconfirmed r)
theorem stale_import_rejected (profiles) (environment) (rv) (j) (fuel) (imp : Import) (hk : imp ∈ importsOf j)
    (b : ByteArray) (hb : imp.bytes = some b) (hne : sourceIdOf b ≠ imp.sourceId) :
  ∃ e, admitDiscourse profiles environment rv j fuel = .error e ∧ e.startsWith "StaleTarget: "
theorem validity_never_premise (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) : v.unit ∉ res.premiseUnits ∧ res.bound v.unit = none

/-- The truth boundary: a self-truth unit has no content, is never a premise and is never CHECKED. -/
theorem self_truth_never_content (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (u : String) (hu : u ∈ res.selfTruth) :
  (unitOf res.doc.base u).bind DocUnit.content = none ∧ u ∉ res.premiseUnits ∧ res.bound u = none ∧
  statusOf res u = "LABELLED"

/-- Stratification: the embed/import chain is acyclic by source id and bounded. -/
theorem import_acyclic (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  VE.Route.DagAcyclic (importNodes res.doc) ∧ depthOf res.doc ≤ 4

/-- Declaring a fresh document sort and fresh constant names changes no old-vocabulary consequence. -/
theorem document_sort_conservative (E : VE.Environment) (sort : String) (hs : sort ∉ E.sorts) (names : List String)
    (hfresh : ∀ n ∈ names, E.constants n = none) (hnodup : names.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ g ∈ Γ, g.WellFormed E []) (hφ : φ.WellFormed E []) :
  VE.Entails (withDocuments E sort names) Γ φ ↔ VE.Entails E Γ φ

/-- Binding: every result is bound to the identities recomputed under the base pair (3.5) and to the regenerated
    bindings; the wrapper report binds the original profile declaration and the @2 document identity. -/
theorem discourse_wire_binding (profiles) (environment) (rv) (j : Json) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  res.doc.sourceId = Wire.sourceId (prose j) ∧
  Wire.decodeManifest (j.getObjValD "discourse") = .ok res.doc.K ∧
  (∃ envId, Wire.environmentId (baseProfiles profiles) (canonicalOf (baseEnvironment environment)) = .ok envId ∧
     res.doc.K.definitionsVersion = envId ∧
     (∀ u A, res.bound u = some A →
        ∃ mid, Wire.meaningId (baseProfiles profiles) envId (Wire.encodeFormula A) = .ok mid ∧ boundMeaningId res u = some mid) ∧
     (∀ w ∈ res.base.wires, ∀ edge, w.deduction = some edge → edge.certificate.environment_id = envId) ∧
     res.reportId = wrapperReportId profiles envId res.documentId (innerReportId res) (referencesJson res) (validityJson res))
/-- Stale rejection over the bound evidence envelope: a certificate accepted for u under j carries the meaning id
    of u's elaboration; when a mention's target changes so that the regenerated meaning id differs (the occurrence
    hypothesis of P0 3.9), that certificate, with its envelope unchanged, is not accepted under j'. Nothing is said
    about a raw proof rebound to the new envelope. -/
theorem stale_target_rejected (profiles) (environment) (rv) (j j' : Json) (fuel) (res res' : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) (h' : admitDiscourse profiles environment rv j' fuel = .ok res')
    (u : String) (m : Mention) (hm : m ∈ res.doc.K.mentions ∧ m.unit = u)
    (hchange : targetObject j m ≠ targetObject j' m) (mid mid' : String)
    (hmid : boundMeaningId res u = some mid) (hmid' : boundMeaningId res' u = some mid') (hne : mid ≠ mid')
    (c : VE.Tableau.Certificate) (hc : c ∈ acceptedCertificates res u) (henv : c.conclusion_meaning_id = mid) :
  c ∉ acceptedCertificates res' u

/-- The public entry point, as Norms.Run.norms_wire_acceptance: a successful `admission` answer is exactly the
    encoding of a checked discourse admission whose bindings equal the recomputed digests and regenerated tables. -/
theorem Run.discourse_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hd : Run.usesDiscoursePath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.DiscourseAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
```

### 9.7 The executable `ve_discourse_route`

`lean/.lake/build/bin/ve_discourse_route <cases.json>`, root `DiscourseMain.lean`, a new Lake target; `Run.main` is
the executable root and no frozen file changes. On raw input it (1) validates the wrapper (3.5: the original
`profiles` sorted and unique with `ve.discourse@1`, the environment's `profiles` field equal to it, format
`ve-document@2`; a `@1` document without the profile is delegated unchanged, with the profile it is the
`UnsupportedProfile` error); (2) computes `baseProfiles` and `baseEnvironment` and runs the frozen envelope and
profile gate (`Gate.decodeEnvelope`, `classify`) and the frozen environment decoder on that pair, plus a strict
discourse decoder (unknown fields rejected; `null` rejected); (3) computes `environment_id`, every `meaning_id` and
`definitions_version` from that same pair; (4) decodes the manifest, runs `WellFormedDiscourse`, regenerates every
binding, elaborates every bound unit and every group's reading, inserts the presupposition carriers (4.5: certified
unit-less `asserted` deduction nodes, or the named `presupposition_unit`s already in the document), projects the
`@1` document and delegates its admission, graph and premise checks to the unchanged W2 functions and its lemmas to
the unchanged W3 `checkLemma` under the base pair; (5) runs the composition gate (`citationExtendsJoint` per lemma,
`reportExtendsJoint` per reported result; UNKNOWN when the joint set is); (6) evaluates validity claims in the
second phase with the three outcomes of 4.7; (7) binds the `@2` `document_id` and emits the wrapper report whose
identity covers the original profile declaration. Case kinds:

| Kind | Extra input | Output |
|---|---|---|
| `discourse-resolve` | none | per mention: accessible targets, the recorded target, `resolved` / diagnostics; per bound unit the elaborated formula and its `meaning_id`; groups; the joint set or its diagnostic |
| `discourse-joint` | `conclusion`, `certificate` or `witness` per choice | ALL / NONE / SOME / UNKNOWN with the named choices |
| `discourse-validity` | none | per validity unit: `checked` / `refuted` / `unconfirmed (reason)`; the import chain |
| `admission` | `ve-document@2` with graph and lemmas | `admitted`, `report`, `report_id`, `document_id`, `kinds`, `references`, `validity` |

P0, W1, W2 and W3 cases without the block delegate unchanged; malformed discourse inputs never fall back after a
failed discourse decode.

### 9.8 What is not claimed

No completeness of resolution outside the supported fragment (`Supported`). No theorem about the resolver's
proposals (untrusted). No claim that `Intended` matches an author's intent: that is this statement review and
W8's fidelity gate. No theorem that a validity claim about an import is true when its bytes are absent or its
check does not complete (it is `unconfirmed`), and no theorem that a failed inner check is a rejection unless it
completed with a non-resource diagnostic. No theorem about SHA-256 injectivity: identity statements are on
canonical objects and transfer to digests under the occurrence hypotheses of P0 3.9 (`stale_target_rejected` takes
the distinct meaning ids as a hypothesis). No theorem that the manifest and the natural-view rule agree beyond the
one-sort cases of section 10 (α′ is the intended difference). No coverage theorem. Rust never resolves references
(11).

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind, from
Lean (`tests/test_discourse*.py`, the `discourse` conformance family). Unless a fixture says otherwise: sorts
`service`, `person`, `document`; constants `api : service` (display "the API"), `alice`, `bob : person`; unary
predicates `reviewed`, `deployed`, `safe`, `eligible : service`, `ready`, `owner : person`; binary
`manager_of(person, person)`, `supersedes(document, document)`; one root anchor `doc` and section anchors `sec1`,
`sec2`; every registered name (`api`, `alice`, `bob`) has scope `doc`; profiles `relational-fol@0`, `ve.discourse@1`;
format `ve-document@2`. A P0 predicate has one signature, so a fixture that predicates a symbol of the other sort
declares its own signature (γ, ζ, θ declare `reviewed : person`); a fixture never applies one predicate to both
sorts. With all three names at scope `doc`, a bare "It"/"She" has three accessible candidates in every fixture; the
type check of 4.3 is what leaves one.

- **(α) Named antecedent.** Units u1 "The API is reviewed." u2 "It is safe." Mention m1 (`It`) → `entity api`.
  Accessible candidates: `api`, `alice`, `bob` (all at scope `doc`); only `api` type-checks under `safe : service`.
  Expected: `reviewed(api)`, `safe(api)`, both CHECKED; presentation of u2 "The API is safe."; provenance keeps
  "It"; `references: 1 resolved`; bytes of u1 and u2 counted once each. The same manifest with m1 → `entity alice`:
  `IllTypedTarget: m1: alice` (`safe(alice)` is ill-typed; not `TargetKindMismatch`, which is form/kind only) and
  `ManifestMismatch: mentions.m1.target`.
- **(α′) Natural view versus manifest, two sorts.** u1 "The API is reviewed." u2 "Alice is ready." u3 "It is safe."
  m1 (`It`) → `api`. The natural-view rule (`natural-view.md`, untyped and document-wide: exactly one constant
  mentioned earlier) REJECTS u3 (two constants mentioned). The manifest: three accessible candidates, one
  type-checking (`api`): `safe(api)` CHECKED. The difference is intended (4.2, 13.17): the manifest sort-types
  the rule. With `alice` not mentioned earlier (u2 removed) both accept; with a second service constant `beta`
  registered and mentioned earlier both reject (natural view: two constants; manifest: `AmbiguousReference: m1:
  api, beta`).
- **(β) Competing quantifier.** u1 "A service is deployed." u2 "The API is reviewed." u3 "It is safe." Expected:
  `UnresolvedReference: m1` in authoring with the question "Does ‘it’ mean the API, or the service just mentioned?"
  offering "The API is safe." and the group reading "Some service is deployed and safe." (with u1); translation: an
  open set of those two readings with distinguishing models. With u1 moved into `sec1` and u2, u3 into `sec2`
  (different innermost anchors): m1 → `api` resolves (scope-based, no distance).
- **(γ) Gender never selects.** Signature `reviewed : person`, `ready : person`. "Alice is reviewed. Bob is
  reviewed. She is ready." Expected: `alice` and `bob` both accessible and both type-checking under `ready :
  person` (`api` is accessible but ill-typed): `AmbiguousReference: m1: alice, bob`; the question offers both; a
  manifest recording `alice` without a signed choice or narrowing is `ManifestMismatch`.
- **(δ) Demonstrative.** "This service is safe." with m1 → `api`: presentation "The API is safe.", CHECKED. "This
  claim is disputed." with m1 recorded as `claim`: `UnsupportedTarget: m1: claim`; the unit is UNFORMALISED with the
  reference recorded.
- **(ε) `such`.** "Every reviewed service is deployed. Every such service is safe." with m1 → `predicate reviewed`:
  presentation "Every reviewed service is safe."; `∀x (reviewed(x) → safe(x))`; CHECKED. A `such` with no bound
  property: `UnresolvedReference`.
- **(ζ) Ordinal pair.** Signature `reviewed : person`, `ready : person`. "Alice and Bob are reviewed. The former is
  ready." m1 target `{kind: entity, name: alice, pair: [alice, bob]}` → `alice`; "Alice is ready."; no inequality
  premise (a model with `alice = bob` is not excluded by the document; the vacuity report is unchanged). Two
  coordinations in the innermost anchor ("Alice and Bob", "Bob and Carol"): two candidates, `AmbiguousReference`.
  "The latter" → `bob`. A `pair` whose `name` is not a member: `InvalidInput`.
- **(η) Possessive description, nested mentions.** "Alice is reviewed. Her manager is ready." m1 (`Her`, bytes
  [a, a+3)) → `alice`; m2 (`Her manager`, bytes [a, a+11)) `definite`, restriction `manager_of(x, alice)`; m1 is
  properly nested inside m2 (accepted; a partial overlap would be `InvalidInput: mentions m1, m2 overlap`); m2 is
  the slot, m1 the binding of its restriction. Assertive: `∃x:person (manager_of(x, alice) ∧ ∀y:person
  (manager_of(y, alice) → y = x) ∧ ready(x))`. Presuppositional, proved: `Γ ⊢ U(D)` certified as a unit-less
  `asserted` deduction node; claim `∀x:person (manager_of(x, alice) → ready(x))` CHECKED with the report line
  `discourse:presupposition:m2: proved (<node>)`. Presuppositional, assumed: an authored unit u3 "Alice has exactly
  one manager." with content `U(D)`, `presupposition_unit: u3`; the claim is CHECKED under that assumption, u3 is
  listed in the residual, report line `assumed (u3)`. Neither: `PresuppositionUnresolved: m2`, unit pending (in
  translation always, since translation cannot add u3). No `discourse:*` label appears in any leaf. Countermodels:
  a model with two managers of Alice, both ready: `U(D)` false, assertive false, presuppositional claim true; two
  managers, one not ready: all three false; no manager: `U(D)` false, assertive false, presuppositional vacuously
  true and the vacuity report says so.
- **(θ) Plural.** Signature `reviewed : person`, `ready : person`. "Alice and Bob are reviewed. They are ready."
  m1 target `{kind: entity, members: [alice, bob]}`, reading `distributive` → `ready(alice) ∧ ready(bob)`,
  presentation "Alice is ready and Bob is ready."; "They" with no listed constants in scope:
  `UnresolvedReference`; a recorded `"reading": "collective"`: the decode-time `InvalidInput: reading collective`
  (`Reading` has no such constructor); `members` with one entry or a repeated entry: `InvalidInput`.
- **(ι) Definition reference (J1).** `sec2` has `exports: ["eligible"]`, W3 `eligible`@2 defined inside it. "Every
  eligible service is reviewed, where eligible has the meaning defined in section 2." → rewrite "Eligible has the
  meaning defined in section 2. Every eligible service is reviewed."; m1 → `predicate eligible` version 2;
  `∀x:service (eligible(x) → reviewed(x))` CHECKED under W3's definition Background. Changing the definition body
  (version 3) with the manifest still pinning 2: `StaleTarget: m1: eligible@2`; every certificate of dependent
  units fails replay. `sec2` without `eligible` in `exports`: `UnresolvedReference`; `exports` naming a predicate
  whose definition unit lies outside `sec2`: `ManifestMismatch: anchors.sec2.exports`.
- **(κ) Anchors.** Anchors "Article 29" with items "29.1" to "29.3"; a `section_ref` to "29.3" resolves; two
  anchors labelled "2" under `doc`: `DuplicateAnchor: 2`; a reference to "section 4" with no anchor:
  `DanglingAnchor: section 4`; renumbering "2" to "3": anchor id unchanged, `document_id` changed, presentation
  approval required, no `StaleTarget`; a `definition_ref` to a definition whose anchor cites a lemma that cites the
  definition: `DependencyCycle: <names>`; two navigation mentions pointing at each other's sections: accepted.
- **(λ) Three operations.** "See Article 29 of the Universal Declaration of Human Rights." LABELLED navigation, no
  premise. "By clause 2.1, the API is safe." with lemma `2.1` earlier in the bundle: CHECKED via `cite:` with every
  transitive leaf of `2.1` listed among the citing unit's leaves; the same with one cited leaf stripped: W3's
  "Citation transitive leaf labels were changed or stripped"; the same with `2.1` under a different reading
  choice of a shared set: "Citation has incompatible reading choices". Cross-set (4.8): with the constraints of
  (ο), lemma `2.1` proved under `readings:rs5@1:0` (pattern-a) cited by a unit whose own leaves carry
  `readings:rs6@1:1` (it-b): W3 and W2 both pass (different sets); discourse: `InvalidCompatibility: citation
  <lemma>`. Report level: lemma `2.1` under `rs5@1:0` and lemma `2.2` under `rs6@1:1`, each extending to a
  compatible choice on its own, both cited by the root: `InvalidCompatibility: report <root>`. The same two cases
  with the joint set UNKNOWN (the 128-choice document of (ο)): no rejection, verdict UNKNOWN. A bare link
  (`navigation`) to clause 2.1 proves nothing.
- **(μ) Same-witness fusion and the J5 negatives.** u3 "A service is deployed." u4 "It is reviewed."; set `rs1`
  on u3 (the owning set, on the group's first span), open, readings: `same-witness` (content `∃x:service
  (deployed(x) ∧ reviewed(x))`, group spans [u3, u4]) and, only when a service constant is registered and
  accessible, `named` (m1 → that constant); the candidate "the sentences are unrelated, u4 pending" is a pending
  `references` line for m1, not a reading of `rs1` (a reading set holds admitted formulas only). Expected: group
  status OPEN on both u3 and u4; presentation of the group reading "Some service is deployed and reviewed."; bytes
  counted once; u3 carrying `rs1` is not `IndependentFragment`. Negative 1: u4 also carries content `∃x:service
  reviewed(x)`: `IndependentFragment: u4`. Negative 1′: u4 carries its own reading set `rs2`: `IndependentFragment:
  u4`. Negative 2: the `same-witness` content recorded as `∃x:service deployed(x) ∧ ∃x:service reviewed(x)`:
  `WitnessSplit: rs1@1:same-witness`. On the wire `"reading": "same-witness"` decodes to `original_index` 0 of
  `rs1@1`; a `"reading": "fused"` absent from the set: `InvalidInput: reading fused not in rs1@1`. Lean: on the
  two-element model `twoServices` (`s1` deployed not reviewed, `s2` reviewed not deployed) the split formula
  evaluates true and the fused one false (`split_not_fused_model`).
- **(ν) Universal plus `it`.** "Every service is deployed. It is reviewed." → `UnresolvedReference: m1` with the
  rewrite "Every service is deployed and reviewed."; the authored rewrite elaborates to `∀x:service (deployed(x) ∧
  reviewed(x))`; translation: an open set (the rewrite; a registered-constant reading if any).
- **(ξ) Description without a possessor.** "The owner is ready." restriction `owner(x)`, sort `person`. Assertive
  `∃x:person (owner(x) ∧ ∀y:person (owner(y) → y = x) ∧ ready(x))`; presuppositional as (η). Models: no owner
  (`U(D)` false, assertive false, presuppositional vacuously true); two owners, both ready (`U(D)` false, assertive
  false, presuppositional **true**); two owners, one not ready (`U(D)` false, assertive false, presuppositional
  false); one owner, ready (all three true); one owner, not ready (`U(D)` true, assertive false, presuppositional
  false). "The owner" with a registered name `owner` of a constant: a name, not a description (the manifest
  decides; both recorded is `DuplicateDeclaration: name the owner`).
- **(ο) Correlated readings (J4).** Sets `rs5` ("this pattern": `pattern-a`, `pattern-b`) and `rs6` ("it":
  `it-a`, `it-b`), constraints `requires (rs5, pattern-a) → (rs6, it-a)` and `requires (rs5, pattern-b) → (rs6,
  it-b)`. Joint set {(a, a), (b, b)}; ALL of φ needs a proof from `Joint`; NONE: one model satisfying the four
  readings and refuting φ; SOME: a certificate under (a, a) and a countermodel under (b, b). Constraints
  `excludes` on all four combinations: `InvalidCompatibility: rs5, rs6` (the enumeration of four choices
  completed). Seven sets of two readings each (128 choices) with no constraints: `ResourceLimit: joint choices`,
  verdict UNKNOWN, statuses unchanged, never `InvalidCompatibility` even with contradictory constraints. No
  constraints, two sets: the joint verdicts equal W2's `ve document readings --conclusion` verdicts on the same
  document. Zero open sets: the joint set is the one empty choice, `Joint = top`, and ALL/NONE/SOME are W2's
  verdicts on `Background ++ Γ_fixed`. A `Γ` contradicting one compatible choice's readings: that choice's
  certificate is `vacuous`; the joint set is unchanged.
- **(π) Document names.** Documents `this_policy` (self, version 3), `policy2` (import, pinned). "This policy
  supersedes policy 2." → `supersedes(this_policy, policy2)`, an ordinary CHECKED assertion (support `assumption`);
  the manifest's `supersedes: ["policy2"]` is provenance and generates no premise; deleting the sentence leaves no
  `supersedes` premise. A second constant of sort `document` not in `documents`: `InvalidInput: document sort
  document has other constants`.
- **(ρ) Validity, self.** "This document is a valid VE document." bound to `this_policy` positive: verdict
  `checked`, unit CHECKED, not a premise; the document with that unit removed has the same admission verdict and
  the same statuses elsewhere (`validity_independent`). "This document is not a valid VE document." (negative):
  `ValidityRefuted: <unit>`, unit LABELLED, admission unchanged. Both sentences in one document: one `checked`, one
  refuted, admission unchanged.
- **(σ) Validity, embedded.** A `meta` unit u9 whose bytes are a complete `ve-document@2` text; document `above`
  refers `embedded: u9`; "The above document is a valid VE document." → the embedded document is loaded at depth 1
  and admitted: `checked`. One byte of u9 changed with the pinned `document_id` kept: `StaleTarget: above`. The
  embedded document itself containing "This document is a valid VE document.": its own `self`, `checked` at its
  level; the outer document's verdicts are unchanged.
- **(τ) Validity, import.** "Policy 2 is a valid VE document." with `imports.policy2.bytes` present and its
  `source_id` equal to the pin: re-checked to completion, `checked`; the stored document rejected with a completed
  admission diagnostic (a dangling premise): `refuted`, the outer document still admitted (the import's outcome
  is second-phase, 4.1(10)); the negative claim "Policy 2 is not a valid VE document." on that rejected import:
  `checked`. The stored document's check hitting `ResourceLimit: graph node count` or the nesting budget:
  `unconfirmed (ResourceLimit: …)` for either polarity (the negative claim is not `checked`: `.isOk = false` is
  not a rejection). Bytes absent: `unconfirmed (import bytes absent)`, unit LABELLED, no error. Bytes with another
  `source_id`: `StaleTarget: policy2`, a manifest error of the importing document (integrity, not outcome). A
  chain A imports B imports A (same source ids): `ImportCycle: <ids>`; five levels of embedding: `ResourceLimit:
  document nesting` at 4.1(10), and inside a validity check `unconfirmed (ResourceLimit: document nesting)`.
- **(υ) Self-truth.** "Everything in this document is true." / "This sentence is false." / "This document is
  correct." / "The above document is true." / "Policy 2 is correct." Each: kind `meta`, LABELLED, label
  `self-truth`, no content, absent from every premise list, `SelfTruth: <unit>` in the report; admission unchanged;
  a manifest binding one of them as a validity claim: `InvalidInput` (the wording is not a validity wording, 2.2:
  any document name, not only "this document").
- **(φ) Identity and tampering.** Mention target altered (m1 → `bob`) with unchanged text where `alice` is the
  unique accepted target: `ManifestMismatch: mentions.m1.target`; the elaborated formula on the wire differing
  from the regenerated one: `ManifestMismatch: bound.u2`; `definitions_version` not equal to the `environment_id`
  computed under the base pair: `StaleTarget: definitions@<v>`; a certificate of (α) replayed after u1 is edited
  to "The API is deployed.": the premise identities differ and replay fails; a certificate of (α) replayed after
  m1 is retargeted so that the regenerated `safe(...)` has another `meaning_id`: rejected with its envelope
  unchanged (`stale_target_rejected`); the `document_id` of every fixture changes under any manifest edit and is
  unchanged under a `weights` edit or JSON reformatting; a `ve-document@1` fixture loaded by the `@2` loader
  without `ve.discourse@1` has byte-identical `document_id`, statuses and report, and with `ve.discourse@1` in
  `profiles` is `UnsupportedProfile: ve.discourse@1 requires ve-document@2`. Profile adapter: `safe(api)` in (α)
  has the same `meaning_id` as `safe(api)` in the same environment without `ve.discourse@1` (both computed under
  `baseProfiles`, `baseEnvironment`); the inner `environment_id` equals the `@1` document's; adding the profile
  changes the wrapper `report_id` and no `meaning_id`; the frozen gate on the base pair answers exactly as on the
  `@1` environment (`profile_adapter_base`).
- **(χ) Quotation.** "Bob says that the API is not reviewed. It is safe." m1 (`It`) → `api` resolves across the
  quotation; `safe(api)` CHECKED; the attributed unit still needs its bridge leaf to enter any deduction (W2
  unchanged). A pronoun inside the quoted clause targeting a constant registered outside: identification only.
- **(ψ) W1 rule references.** "Rule 4 (exception to rule 3)." resolves to the stable name; renumbering keeps the
  edge; cross-predicate precedence: W1's `PrecedenceAcrossPredicates`, unchanged; a `rule` target naming a deleted
  block: `UnknownRule`.
- **(ω) Corpus.** The four constitution units and UDHR u109–u112 of 2.5 with the expected reference outcomes and
  the expected unchanged statuses; the run's C/L/O/R/U totals are byte-identical before and after adding the
  manifest (no coverage claimed); the `references` lines carry the resolutions.

Beside these: every W2 fixture repeated as a `ve-document@2` document with an empty `discourse` block (identical
statuses, verdicts, inner reports and `meaning_id`s; `document_id` in the `@2` domain); the four natural-view `It`
cases (`natural-view.md`: zero, one and multiple named referents; an earlier quantifier) reproduced through the
manifest with identical accept/reject outcomes **when every constant mentioned earlier has one sort**, which is
exactly when the natural-view candidate set and competing-quantifier set coincide with the manifest's typed
candidates and sort-scoped competing binders; α′ records the intended divergence for two sorts; differential
`validate` Python versus Lean on 1,000 generated manifests; the 200-graph DAG differential extended to
definition/citation dependency graphs; the mixed English harness (W7) extended with the 2.1 wordings, each passing
the per-input all-derivations gate.

## 11. Limits, regeneration, Rust

Anchors ≤ 1,024, mentions ≤ 4,096, names ≤ 1,024, documents ≤ 64, imports ≤ 64, groups ≤ 256 with ≤ 16 spans each,
constraints ≤ 1,024, joint choices ≤ 64, document nesting ≤ 4, validator fuel = mentions + anchors + 1, restriction
formulas within `MAX_NODES`; every overflow is `ResourceLimit` with the limit named, never a verdict (and inside a
validity check, `unconfirmed`). Every binding, elaborated formula, group reading, joint set, document table and
identity is regenerated from the decoded document at every trusted site (3.4); the manifest is validated, never
trusted. Compositions: `norms@0` unchanged; `soft-norms@0` only with its coherence premises and conditional
guarantees retained, otherwise explicitly unsupported (5). Rust never resolves references: on the
`elaborated-document` family a discourse case carries the Python-generated elaborated formulas marked `untrusted:
true`, and its verdict must agree with Python's and Lean's regenerated ones (regression evidence; the trust path is
Lean).

## 12. Statement review checklist (Astra + Fable, before sequences 2 to 5)

The re-review after draft 2 covers the complete amended gate, not a bounded subset: the amended definitions, the
three adapter contracts, every theorem statement and the affected fixtures together, including their consistency
with the plan.

1. The seven target kinds, their explicit representations (`members`, `pair`, `units`, `content_name`, `exports`)
   and their non-coercion (1.2 to 1.4); the registered-name model of "the API" versus the description model of
   "the owner" (1.3, 4.5); nested mentions; location versus formula-producing bindings.
2. `Acc` (4.2): scope by anchor, no distance, the competing-quantifier condition (same sort, same innermost anchor
   or same sentence) with its inputs listed, pairs and `such`, binder locality, quotation identification without
   admission; sorts outside `Acc`; the natural-view difference.
3. `Accepted` (4.3): one recorded typed derivation fixed first, every type-checking competitor equal to it modulo
   aliases; the type check as the only filter (no pruning by recorded targets or reading choices); slot
   correspondence (`UnrecordedSlot`, `MentionNotSlot`); the all-derivations gate covering antecedent and scope
   alternatives; UNKNOWN never uniqueness.
4. `Intended` and `elaborate` (4.4) and the faithfulness statement (9.3); no witness constants or choice functions;
   binder sorts on every constructor.
5. Descriptions (4.5): the two readings, the two frozen carriers of `U(D)` (certified unit-less deduction node;
   explicit `presupposition_unit`), no `discourse:*` label, `PresuppositionUnresolved` as pending.
6. Fusion (4.6): one assertion per group regenerated per group, the owning set exempt from `IndependentFragment`,
   status through the owning set, `sharedWitness`, the J5 negatives, pending candidates outside the set.
7. Document names, validity claims and the truth boundary (4.7): the second phase, `stripValidity`, the three
   outcomes with rejection distinct from UNKNOWN, import integrity at 4.1(10) versus outcome, refutation as a
   warning, `unconfirmed` for absent bytes and incomplete checks, self-truth as LABELLED `meta` for any document
   name; stratification by source id.
8. The joint set (4.8): `requires`/`excludes` only, the empty conjunction as `top`, the nonempty requirement after
   a completed enumeration, `joint_all_iff`, the shortcut regained without constraints, NONE with one shared model,
   SOME; the composition gate (`ExtendsTo`, per lemma and per reported result, UNKNOWN when the joint set is).
9. The three operations (4.9) and the J2 citation wording with the extension clause.
10. What stays frozen (5), the profile adapter (3.5: `baseProfiles`, `baseEnvironment`, identities under the base
    pair, the wrapper binding the original declaration), `format1_unchanged` with the profile-on case, the soft
    composition clause; the `@2` identity domain (3.3).
11. The English table (2.1): one reading per wording; the synonyms (2.2); the reviewed presentation (6) with
    `Meaning := Formula` (9.5) and the lexicon coverage hypothesis.
12. The diagnostics (8) and the fixtures (10, including α′, the corrected ξ and μ, the λ cross-set cases and the
    τ outcomes), each against the definitions.
13. The resolved choices of section 13.
14. The plan (discourse-PLAN.md) states the same contracts as this draft (page 1 acceptance and fusion, page 3
    correlated readings and Lean obligations, page 4 sequence gates).

## 13. Resolved choices in this draft

Each is a point where the plan or the debate left a reading open; the review may overturn any of them.

1. **Always expand (J6).** Fable's round-2 pick is applied: the expansion is the reviewed presentation in authoring,
   approval and export, with the pronoun as provenance. Astra's round-2 permission (an in-document reading view
   may keep a pronoun when the displayed document passes the accessibility and all-derivations checks with one
   reading) is not exercised; Astra had accepted the always-expand alternative in round 1's E3. Astra's sentence "a
   hidden binding never rescues ambiguous displayed prose" is kept verbatim.
2. **Row 8 (J1).** Fable's two-sentence rewrite is the rule, with Astra's requirement met inside it: the first
   sentence attaches the pinned declaration to `eligible`; the assertion is the same universal on both sides;
   "clarify quantification separately" is deleted.
3. **Competing quantified mention** is defined by sort and innermost anchor (or the same sentence), not by
   distance, so the natural-view rule is kept without a paragraph-reset heuristic.
4. **Validity claims** are `meta` units with a manifest binding, evaluated after admission on `stripValidity(D)`;
   refutation is a warning; absent import bytes give `unconfirmed`; a validity claim is never a premise. This
   realises the lead's "validity = admission, computed independently of the sentence's truth".
5. **Self-truth** sentences are `meta`, LABELLED, label `self-truth`, no content; not UNFORMALISED, because they
   are recognised and permanently outside certification rather than "not yet formalised".
6. **Document names** are ordinary declared constants of a declared `document_sort` reserved for them; the profile
   adds no symbol; metadata is provenance only.
7. **Compatibility constraints** are `requires` and `excludes` between named readings; the joint set is the
   product filtered by exactly these (nothing inferred), which is what "joint enumeration uses only these" means.
8. **Restrictions** of descriptions are a declared unary predicate or a binary predicate with a resolved entity;
   arbitrary formulas are deferred.
9. **Groups** are a property of readings (a reading set's reading bound to spans), so a `@1` document's unit
   content model is unchanged and W2's status rule applies to the group through its set.
10. **`@1` delegation.** The `@2` loader decides by the `format` field and never re-tags a `@1` `document_id`.
11. **Embedded documents** are `meta` units holding a complete document; imports are stored beside the document
    and re-fingerprinted; the chain is acyclic by `source_id` with depth 4.
12. **Reference counts** are report lines and never statuses; no new status is introduced.
13. **Plural `they`** is distributive over an explicit finite list only; everything else is unsupported.
14. **`this` as a claim or action term** is `UnsupportedTarget` here; attribution and speech-act semantics own it.
15. **Aliases** are declared per constant in `names`; predicate synonymy stays W3.
16. **The self-reference wording** follows VISION's boundary note (branch `docs/self-reference`, commit
    `da8d8e2396cb`, "VISION: refine self-reference boundary with the lead (validity claims ok and checked; truth
    claims not)", 2026-09-28) exactly: validity claims supported and checked; truth claims labelled.
17. **The type check is the only competitor filter (review F1/F2/A1).** `Accepted` fixes one recorded, typed
    derivation and assignment and compares every type-checking competitor against it; recorded targets and
    reading choices never prune. A manifest therefore supersedes the natural-view rule by sort-typing it, and the
    two agree exactly when every earlier-mentioned constant has one sort (α′ records the intended difference)
    rather than being forced to coincide, which would undo the typed filter.
18. **The profile adapter (review A3, Astra round 3).** `ve.discourse@1` is validated by the wrapper and stripped
    from both the list and the environment JSON before every frozen call; identities are computed under the base
    pair; the wrapper report binds the original declaration. This mirrors `Norms/Replay.lean`.
19. **The presupposition carriers (review A3, Fable round 2).** No `discourse:*` label exists at W2; `U(D)` is
    either a certified unit-less `asserted` deduction node or an explicit `presupposition_unit`; otherwise the
    mention is pending. The report line keeps the `discourse:presupposition:<mention>` name.
20. **The composition gate (review A3, Astra round 3).** W3 and W2 merge choices within a set only, so
    `admitDiscourse` requires each lemma's transitive choices and each reported result's merged assumptions to
    extend to a validated compatible choice; failure after completion is `InvalidCompatibility`, otherwise UNKNOWN.
21. **Empty conjunction is `top` (review A6).** Zero open sets yield the one empty choice; `InvalidCompatibility`
    and the extension diagnostics require a completed enumeration.
22. **Import integrity versus outcome (review A4/F4).** Fingerprint integrity is well-formedness (`StaleTarget`);
    the imported document's admission is a second-phase outcome with rejection (a completed non-resource
    diagnostic) distinct from UNKNOWN, so τ's rejected import is reportable and a negative claim is never
    `checked` by exhaustion.
23. **`Meaning := Formula` (review F7).** Assignments are provenance validated separately (slot correspondence),
    so `ParseRender` is stated over the expansion through the unchanged core parser.
24. **Soft composition (review, Astra round 2).** Supported only with the soft route's coherence premises and
    conditional guarantees retained; anything else is explicitly unsupported.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-28 | Draft 1 | Item-1 specification from the plan as revised by the converged debate (J1 to J8) and the lead's document-name/validity/truth input: the manifest with seven target kinds; the English table; wire form and the `@2` identity domain; accessibility, resolution, elaboration and `Intended`; descriptions with the presupposition leaf; same-witness groups with the J5 negatives; document names, validity claims in a second phase, the self-truth label and stratification; the joint set with declared constraints and the nonempty requirement; the three operations with the J2 citation wording; report, diagnostics; every theorem of the plan's five obligation groups plus documents as a statement; fixtures α to ω; resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-28 | Draft 2 | The converged Astra + Fable statement review of draft 1 applied (`manage-agents/debates/discourse-spec`, rounds 1 to 3, FIX). F1: typed competitors, `IllTypedTarget`, per-fixture signatures. F2/A1: `Accepted` with one recorded typed (d, σ) outside the universal, slots as (unit, span, form), targets looked up in `K.mentions`, slot correspondence (`UnrecordedSlot`/`MentionNotSlot`), no pruning, typed candidates for pairs, lists and `such`. F3: `Acc`'s inputs listed; `acc_no_heuristic` over equal anchor trees and innermost-anchor texts. F4/A4: `validity_import` over the three outcomes, `stale_import_rejected` separate, rejection distinct from UNKNOWN, 4.1(10) reduced to decode, identity, cycle and depth. F5/A2: `group_single_assertion` over the owning set's leaf; owning set exempt from `IndependentFragment`; formulas validated per group; nested mentions; location versus formula bindings; `members`, `pair`, `units`, `content_names`, `exports`. F6: `target.units` and `content_names`. F7: `Meaning := Formula`, `presentation_expands`, `LexiconCovers`. F8: `such` dropped from the constant forms; `original_index` mapping; `S.domain σ a`; θ decode-time `InvalidInput`; υ over any document name; VISION commit pinned; the natural-view difference stated with fixture α′. A3: the profile adapter (`baseProfiles`, `baseEnvironment`, identities under the base pair, wrapper binding the original declaration; `profile_adapter_base`, `format1_profile_requires_format2`); the presupposition carriers (`presupposition_carried`, `no_discourse_label`); the composition gate (`ExtendsTo`, `citation_extends_joint`, `report_extends_joint`, `extension_rejected`, `extension_unknown`). A5: binder sorts on `uniqueD`/`assertive`/`presupposed`/`fused`, `.ex`, typed hypotheses throughout, `independent_shortcut` with its enumeration premise, `admission_projects` for `@2` inputs under the base pair, constant freshness in `document_sort_conservative`, `stale_target_rejected` over the bound envelope. A6: `conj [] = .top`, `compatible_empty_error` under completed enumeration, ξ corrected (two ready owners), μ's pending candidate outside the inventory. Soft composition clause (5, 11). Checklist 12 now the complete amended gate; resolved choices 17 to 24. Spec only. |
