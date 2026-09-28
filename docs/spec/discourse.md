# Discourse and cross-reference (`ve.discourse@1` over `ve-document@2`): names, anaphora, descriptions, document references and correlated readings

> Status: item-1 specification, draft 1 (2026-09-28), written from [discourse-PLAN.md](discourse-PLAN.md) as revised
> by the converged Astra/Fable debate (`manage-agents/debates/design-discourse/{astra,fable}.md`, round 2, edits J1 to
> J8) and the lead's additional input recorded in that debate's `TOPIC.md` (document names, validity claims by
> fingerprint, the truth boundary). It is the statement under the Astra + Fable item-1 review that gates sequences 2
> to 5 of the plan (PLAN-EXPAND2 rule 10). Sections 4 to 6 and 9 are the statements under review; section 13 lists
> every point where this draft chose between readings of the plan. Theorem statements and fixtures are implementation
> obligations, not claims of completed proofs or tests. Inputs: [document.md](document.md) (W2),
> [norms.md](norms.md) (W1), [lean/VE/Definitions/STATEMENTS.md](../../lean/VE/Definitions/STATEMENTS.md) (W3),
> [natural-view.md](../natural-view.md), [VISION.md](../../VISION.md) including its self-reference boundary
> (2026-09-28, branch `docs/self-reference`), `lean/VE/Route/{Admission,Readings}.lean`,
> `lean/VE/Definitions/Bundle.lean`, `lean/VE/English/Statements.lean`, `ve/document.py`, `ve/readings.py`,
> `ve/english.py`, the pinned constitution run `20260927T1800Z` and the UDHR run `20260927T1800Z`. Nothing here
> changes a frozen contract, a `ve-document@1` identity, a P0/W1/W3 theorem statement or a checker function.

## 0. Scope, one paragraph

A reference is resolved **before** anything is checked, into an explicit typed target recorded in a versioned
manifest, and the checker sees only closed formulas of the existing logic. "It", "this service", "such", "the
former", "her manager", "they", "as defined in section 2", "Article 29", "by clause 2.1", "this document" and "the
above document" each become one of seven target kinds (entity, predicate, source unit, anchor, rule, claim,
document); the kinds never coerce into one another; names and section numbers are display labels, never identities.
Acceptance of a sentence requires exactly one derivation and one reference assignment, modulo declared aliases,
yielding a closed typed formula `A`; the checker regenerates that assignment from source plus manifest and rejects
anything stale, missing, colliding, ill-typed or inaccessible. A quantifier's witness never becomes a name: the
same-witness reading of "A service is deployed. It is reviewed" is one fused assertion bound to both source spans.
A definite description exposes existence and uniqueness as formulas over equality; a document name is an ordinary
declared constant; a validity claim about a document is a checker verdict computed independently of the claiming
sentence, and a document may not certify its own truth. Correlated reading choices are enumerated jointly under
declared compatibility constraints, never as independent products. What this buys, exactly: existing W2 statuses,
W1 rule identities, W3 declarations and citations, P0 identities and every existing theorem are reused unchanged;
the new obligations (section 9) are about resolution, elaboration, compatible choices and model correspondence, and
no coverage gain is claimed until a rerun measures one.

In this specification: the manifest and its target kinds (1), the English (2), the wire form and identity (3), the
semantics of accessibility, resolution, elaboration, descriptions, fusion, document names and joint choices (4),
what stays frozen (5), modes and the reviewed presentation (6), the report (7), diagnostics (8), the Lean
definitions and every theorem as a statement (9), the item-1 acceptance fixtures (10), limits (11), the review
checklist (12) and the resolved choices (13).

Out of scope, by the plan: any new logical operator or checker rule; bare `this`/`that` referring to a claim or an
action as a term (attribution and speech-act semantics own it); collective, generic and unknown-group plurals;
"respectively"; incorporation of a cited article's content as premises ("under Article 29"); legal authority and
override semantics; rights, soft-weighing, modality and causation co-blockers on the pinned units; the surface
registrations (sequence 2), the readings/IDE actions (sequence 4) and the integration gates (sequence 5) beyond the
wordings and fixtures fixed here.

## 1. What a discourse manifest is

### 1.1 Format and profile

`ve.discourse@1` is a profile enabled in the environment (`profiles` sorted, as `norms@0`). Its manifest is the
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
             label (display text: "2", "2.1", "Article 29"), span [a, b) in prose bytes, edition (optional)}
```

Anchors form one tree by `parent`; a child's span lies inside its parent's; sibling spans do not overlap; the root
spans the whole prose. Labels are display only: two anchors may not share a label under one parent
(`DuplicateAnchor: <label>`), and a label never identifies a target. `edition` names the edition of an external
document an anchor belongs to (an import, 1.6); an anchor of an import without a pinned edition is
`AmbiguousEdition: <document>`. Section scope is explicit (an anchor), never inferred from typography.

### 1.3 Registered names and aliases

```text
name     := {constant, display, scope (an anchor id), aliases (display strings)}
```

A registered name binds a declared constant of the environment (a `Const` symbol) to its display form ("the API",
"Alice") and to the anchor within which mentions may use it. The vocabulary overlay of the natural view already
declares display forms (`natural-view.md`, `constants` entries); the manifest adds the scope and the aliases. Two
names with one display string in overlapping scopes are `DuplicateDeclaration: name <display>`. Aliases are
declared per constant; "modulo declared aliases" in 4.3 means: two assignments that differ only in which alias of
one constant a mention used are the same assignment. Predicate synonyms remain W3 alias definitions (VISION,
"Synonyms and varied wording"); this profile declares no predicate alias of its own.

### 1.4 Mentions, forms and target kinds

```text
mention  := {id, unit (the source unit containing it), span [a, b) in prose bytes, form, target,
             restriction (definite descriptions only, 4.5), reading (definite: assertive | presuppositional;
             plural: distributive)}
form     ∈ {pronoun, demonstrative, definite, ordinal_pair, such, possessive, plural, section_ref,
            definition_ref, document_name, citation, navigation}
target   := {kind, name, version (optional)}
```

| Target kind | `name` is | Accessible when (4.2) | What the mention elaborates to |
|---|---|---|---|
| `entity` | a declared constant, or `binder:<i>` for a local binder of the same sentence or rule | the constant is registered with a scope containing the mention's unit; a binder only inside its own sentence/rule | the constant term; the bound variable |
| `predicate` | a declared unary or binary predicate | declared in `E` at `definitions_version`; for `definition_ref`, exported by the anchor named | the predicate symbol (for `such`, the copied property; for `definition_ref`, the pinned declaration) |
| `unit` | an ordered list of source unit ids | every id exists; forward references allowed | nothing: a location; a registered content name |
| `anchor` | an anchor id | exists; forward references allowed | nothing: a location |
| `rule` | a W1 stable rule name | a norm unit of the document | the rule (W1 exception/precedence references, unchanged) |
| `claim` | a lemma meaning id in the document's bundle | strictly earlier in the bundle (`Bundle.checkLemma`) | a W3 citation (`cite:` leaf) |
| `document` | a document name (1.6) | declared | the document constant (a term); or the target of a validity claim (4.7) |

Kinds never coerce: a `unit` or `anchor` target is never a term, a `document` target is never a predicate, a `claim`
target never enters as an assumption without its transitive leaves. A mention whose form and target kind do not fit
(a `pronoun` targeting an `anchor`, a `section_ref` targeting an `entity`) is `TargetKindMismatch`. A `demonstrative`
or `pronoun` whose intended referent is a claim or an action as a term is `UnsupportedTarget: <mention>: claim` in
this profile (it is a READINGS/UNFORMALISED unit, never guessed).

### 1.5 Reading groups and compatibility constraints

```text
group      := {set, version, reading (a reading id of that set version), spans (ordered unit ids, source order)}
constraint := {kind ∈ {requires, excludes}, a: [set, version, reading], b: [set, version, reading]}
```

A group binds one reading of one reading set to an ordered list of source units: the reading's content is **one**
assertion; every listed unit keeps its historical span and receives the group's status; bytes are counted once; no
listed unit may carry content of its own or its own reading set (`IndependentFragment: <unit>`). The reading set's
`unit` is the group's first span. A `same-witness` group's content must share one witness across the spans
(4.6); a content whose spans are quantified independently is `WitnessSplit`. Constraints relate named readings of
two active sets: `requires` (if `a` is chosen then `b` is chosen), `excludes` (not both). The joint set of 4.8 is
the product of the active sets filtered by exactly the declared constraints; nothing is inferred from wording.

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
| `Alice and Bob are reviewed. The former is ready.` | "‘The former’ is the first of the pair ‘Alice and Bob’: Alice." Presentation `Alice is ready.` Pair order asserts no inequality. Two candidate pairs: a question. | `ordinal_pair` → `entity alice` |
| `Alice is reviewed. Her manager is ready.` | "‘Her’ means Alice. ‘Her manager’ is a description: someone who is a manager of Alice." Then the two description readings (4.5): "Alice has exactly one manager, and that manager is ready" / "Assuming Alice has exactly one manager: every manager of Alice is ready." | `possessive` → `entity alice`; `definite` with restriction `manager_of(x, alice)` |
| `Alice and Bob are reviewed. They are ready.` | "‘They’ means Alice and Bob, each." Presentation `Alice is ready and Bob is ready.` Collective or generic readings stay unresolved. | `plural` distributive → `entity alice`, `entity bob`; `ready(alice) ∧ ready(bob)` |
| `Every eligible service is reviewed, where eligible has the meaning defined in section 2.` | Rewrite: `Eligible has the meaning defined in section 2. Every eligible service is reviewed.` "The first sentence selects the definition of ‘eligible’ exported by section 2 (version pinned); the second is an ordinary sentence." | `definition_ref` → `predicate eligible@v`; `∀x (eligible(x) → reviewed(x))` |
| `Eligible has the meaning defined in section 2.` | Selects the pinned W3 declaration (signature and body); neither invents a definition nor changes its environment. | `definition_ref`; no premise of its own |
| `Article 29`; `clause 2.1`; `section 2` | A location in a qualified document/edition. A whole article is a location, not one inferred proposition. | `section_ref` → `anchor` |
| `See Article 29 of the Universal Declaration of Human Rights.` | A navigation instruction; nothing is asserted. | `navigation` → `anchor`; LABELLED |
| `By clause 2.1, the API is safe.` | "Clause 2.1's checked result is cited; this sentence is proved from it with every cited assumption listed." | `citation` → `claim`; W3 `cite:` leaf, unchanged |
| `The owner is ready.` | Two readings shown with situations: "There is exactly one owner, and that owner is ready" / "Assuming there is exactly one owner: every owner is ready." Never: existence from "the". | `definite` with restriction `owner(x)`; 4.5 |
| `A service is deployed. It is reviewed.` | "‘It’ here is the service just mentioned: the same-witness reading is `Some service is deployed and reviewed.`; alternatives are kept." | group `same-witness`; `∃x (deployed(x) ∧ reviewed(x))` bound to both spans |
| `Every service is deployed. It is reviewed.` | No automatic reading. Rewrite offered: `Every service is deployed and reviewed.`; translation keeps the alternatives. | `UnresolvedReference`; scoped rewrite |
| `This document is a valid VE document.` | "Checked: this document is admitted; the verdict is computed without using this sentence." | validity claim, `self`, positive; CHECKED |
| `This document is not a valid VE document.` | "False: this document is admitted." Admission is unchanged. | validity claim, `self`, negative; `ValidityRefuted` warning |
| `The above document is a valid VE document.` | "Checked: the document quoted above (fingerprint shown) is admitted when re-checked." | validity claim, `embedded` |
| `Policy 3 is a valid VE document.` | "Checked/refuted/unconfirmed: the pinned document ‘Policy 3’ (fingerprint shown) is re-checked from its stored bytes." | validity claim, `import` |
| `This policy supersedes policy 3.` | An ordinary claim over two document names and the declared predicate `supersedes`; its truth is not certified. | `supersedes(this_policy, policy3)` |
| `Everything in this document is true.` / `This sentence is false.` / `This document is correct.` | "Labelled: a document cannot certify its own truth or correctness; this sentence is recorded and never checked." | kind `meta`, LABELLED, label `self-truth` |
| `Under Article 29, ...` | A location; imports no premise, establishes no authority, chooses no override. The rest of the sentence is checked on its own. | `section_ref`; no premise |
| `Rule 4 (exception to rule 3).` | W1, unchanged: a stable rule name. | `rule` |
| `In this document, staff, employees and personnel mean the same thing.` | W3 alias definition, unchanged. | W3 |

### 2.2 Synonyms and non-synonyms

Input synonyms rendered canonically: `the latter` for the second member of the pair (as `the former` for the first);
`that <noun>` for `this <noun>` when both would bind the same registered name; `the said <noun>`,
`the aforementioned <noun>`, `the above <noun>` for `this <noun>` only when a registered name has that display form.
Nothing else. `it` inside a `that`/`who` relative clause keeps its local binder (natural view). `respectively` is
not a wording. A section number without a declared anchor is `DanglingAnchor`. "Valid" in a validity claim means
admitted, exactly (4.7); "true", "correct", "sound", "accurate" applied to this document or a unit of it are the
self-truth wordings of 2.1, never synonyms of "valid".

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
distinguishing situation leaves the candidate pending, not fictitiously checked.

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
           MIXED: the naming clause registers the display name "Claude's principal hierarchy" for a `unit` target
           (the preceding units) and is LABELLED; "it helps define what we mean by broad safety" resolves `it` to
           that name and stays UNFORMALISED (no "helps define" semantics; `broad_safety` remains the open term).
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
              {"id": "sec2", "kind": "section", "parent": "doc", "label": "2", "span": [120, 980]}],
  "names": [{"constant": "api", "display": "the API", "scope": "doc", "aliases": ["the service API"]}],
  "mentions": [{"id": "m1", "unit": "u2", "span": [45, 47], "form": "pronoun",
                "target": {"kind": "entity", "name": "api"}},
               {"id": "m2", "unit": "u7", "span": [301, 320], "form": "definition_ref",
                "target": {"kind": "predicate", "name": "eligible", "version": 2}},
               {"id": "m3", "unit": "u9", "span": [410, 421], "form": "definite",
                "target": {"kind": "entity", "name": "binder:0"}, "reading": "presuppositional",
                "restriction": ["binary", "manager_of", ["var", 0], ["const", "alice"]]}],
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
existing grammar (`[a-z][a-z0-9_-]*`, at most 64 bytes); `definitions_version` must equal the embedded
environment's `environment_id` (`StaleTarget: definitions@<version>` otherwise); `document_sort` names a declared
sort that only document names use (`InvalidInput: document sort <s> has other constants`); `restriction` is a P0
wire formula over the context `[sort of the description]` (index 0 is the described entity) mentioning declared
base or defined predicates and resolved constants only.

### 3.2 Units, groups and statuses

A unit of `ve-document@2` is a `@1` unit; the discourse block adds nothing to a unit. Status is W2's: `CHECKED`,
`OPEN`, `LABELLED`, `UNFORMALISED`, with `MIXED` parents. A unit listed in a group has no `content`, no
`meaning_id` and no reading set of its own; its status is the group's set status under W2's rule (an authored
assertion singleton with content is CHECKED, an open set is OPEN). A `meta` unit that is the target of a validity
claim binding (4.7) has no content; its status is CHECKED when the verdict is `checked`, LABELLED otherwise. A
`meta` unit labelled `self-truth` has no content and is LABELLED. Coverage tables (`bytes_by_status`,
`bytes_by_kind`) still each total the source byte count; a group's units are counted once, each under its own span.

### 3.3 Identity

```text
source_id      unchanged (sha256("ve-source-<identity_version>\n" + prose bytes))
meaning_id     unchanged for every formula, norm and definition (the elaborated formula is a P0 formula)
document_id    sha256("ve-document@2\n" + canonical({"metadata": front matter minus "weights", "source": prose,
               "fences": fences})), the `@1` payload under the new domain tag; the discourse block is inside
               "metadata", so every anchor, name, mention, target, version pin, group, constraint and document
               declaration is identity-bound; removable weights and JSON layout are not
report_id      P0's, unchanged; a discourse document's wrapper report identity binds the `@2` document_id
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
registered scopes, each mention's accessible targets (4.2), the uniqueness of the recorded assignment (4.3), the
elaborated formula of every bound unit (4.4), the group and constraint checks (1.5, 4.8), the document table (4.7)
and every identity. A manifest whose recorded target is not the unique accessible one, or whose recorded formula
differs from the regenerated elaboration, is `ManifestMismatch: <field>`. Python/Rust/Lean agreement is regression
evidence; the trust path is Lean (`ve_discourse_route`, 9.7). Decoding, hashing and display remain named trust
boundaries.

## 4. Semantics

### 4.1 Well-formedness (`WellFormedDiscourse`)

A `ve-document@2` document `D` over environment `E` is well-formed when, in this order:

1. `E` enables `ve.discourse@1`; the format is `ve-document@2`; the block decodes (3.1); the `@1` part loads
   (W2's checks unchanged, including the byte partition).
2. Anchors form one tree with nested, non-overlapping spans and unique labels per parent (1.2).
3. Names bind declared constants to unique display strings per scope (1.3); every document name is a declared
   constant of `document_sort` and no other constant has that sort (1.6); imports pin `source_id` and
   `document_id`; an `embedded` unit exists and has kind `meta`.
4. Every mention lies inside its unit's span; mention spans within one unit do not overlap; every target exists
   (`UnresolvedReference` when the manifest records none, `DanglingAnchor`, `UnknownDocument`, `UnknownRule`,
   W3's `Citation is absent, cyclic, or not earlier in the bundle`).
5. Every mention's form fits its target kind (`TargetKindMismatch`); descriptions carry a typed restriction;
   plurals are distributive over an explicit finite list.
6. Every recorded target is accessible (4.2) and unique modulo aliases (4.3); every bound unit elaborates to a
   closed typed formula (4.4).
7. Groups and constraints are well-formed (1.5): listed units carry no content or set (`IndependentFragment`),
   the `same-witness` content shares its witness (`WitnessSplit`), constraints name active readings.
8. The joint set of the active open sets is validated and nonempty (`InvalidCompatibility`) or its validation
   hits the budget (UNKNOWN for every reading-dependent verdict; not a rejection).
9. Definition and proof dependencies are acyclic: `dependencyOrder` over definition anchors and cited lemmas
   (`DependencyCycle: <sorted names>`, W1's shared text). Navigation edges are not in this graph.
10. Every embedded or imported document decodes and is itself well-formed, to nesting depth 4, with no repeated
    `source_id` along the chain (`ImportCycle: <source ids>`, `ResourceLimit: document nesting`).
11. Limits (11).

Warnings (reported, never rejecting): `ValidityRefuted`, undeclared names used only as display in exposition,
navigation targets outside any admitted import (a label with no target content).

### 4.2 Accessibility `Acc(D, m, t)`

An independent relation between a mention and a candidate target, with no nearest-mention, gender, salience,
paragraph-reset or frequency heuristic:

```text
entity, constant c        c is registered (1.3) with scope σ and m.unit lies in σ's span, and m's form is one of
                          pronoun, demonstrative, ordinal_pair, plural, possessive, or `such` with a property
                          (never definite: "the API" is a registered name, not a description)
                          AND, for a pronoun or bare demonstrative, no competing quantified mention: no existential or
                          universal binder of c's sort occurs in an earlier sentence of the innermost anchor
                          containing m, nor earlier in m's own sentence (natural-view rule, scoped by anchor and sort)
entity, binder:i          only inside the sentence or rule that introduces binder i, in a position the binder scopes
                          over; never across a sentence boundary (WitnessEscape); never out of quantification,
                          negation, disjunction, a conditional, quotation or an attitude
predicate p               p declared in E at definitions_version; for definition_ref, p is exported by the named
                          anchor's pinned declaration (the anchor lists the declarations it exports)
unit / anchor             the ids exist; forward references allowed after indexing
rule r                    r is a stable name of a norm unit of D (W1's same-predicate and DAG restrictions unchanged)
claim l                   l is a lemma strictly earlier in D's bundle (Bundle.checkLemma)
document d                d is declared in D.documents
```

A quoted name can be identified across a quotation (a pronoun in "Bob says that the API is not reviewed. It is
safe" may target `api`) without admitting the quoted fact: identification uses the registration, and the quoted
content still needs its bridge leaf. `Acc` depends only on the registrations, anchors, declarations, the mention's
unit and form, and the binders of the mention's own sentence; it does not depend on any other mention or on wording
elsewhere (theorem `acc_no_heuristic`, 9.2).

### 4.3 Resolution and acceptance

```text
Derives(E, L, s, d)         d is a derivation of sentence s in the discourse grammar: the existing English grammar with
                            a slot production for each form of 1.4 (the slot yields the mention's surface text)
slots(d)                    the mentions of d, in source order, with their forms
assignment σ                slots(d) → targets
elaborate(E, K, d, σ, ρ)    the closed formula obtained by substituting each slot by its target's elaboration (1.4,
                            4.5, 4.6) under the recorded reading choices ρ; capture-avoiding; fails when a slot's
                            target has no elaboration (unit, anchor, navigation)
Resolve(E, K, s, ρ, A)      := ∃ d σ. Derives(E, L_K, s, d) ∧ (∀ m ∈ slots(d). Acc(D, m, σ m) ∧ σ m = K.target(m))
                               ∧ elaborate(E, K, d, σ, ρ) = A ∧ A closed and well-typed over E
Accepted(E, K, s, ρ, A)     := Resolve(E, K, s, ρ, A) ∧ every (d', σ') with Derives and Acc for all slots is
                               alias-equal to the recorded (d, σ)
```

Acceptance requires exactly one derivation and one assignment modulo declared aliases; selecting one parser result
is insufficient (the all-derivations gate of P0 3.2 includes antecedent and scope alternatives as derivations).
Resource exhaustion is `ResourceLimit: resolution` (UNKNOWN), never uniqueness. Logical judgment uses `A`, never a
mutable conversation history; the standalone export repeats the targets (6).

### 4.4 Elaboration and the intended meaning

`Intended(E, K, s, ρ, S)` is defined on the derivation and the validated assignment, against a structure `S`,
without reference to `elaborate`: the sentence's meaning with each slot interpreted directly in `S`:

```text
entity constant c          the element S.constant c
entity binder:i            the valuation's value for binder i
predicate p (such)         the relation S.relation p
definite, assertive        ∃ a typed for the restriction's sort: D holds at a in S, every b with D at b equals a, and
                           the sentence's predication holds at a
definite, presuppositional the predication holds at every a with D at a in S (the uniqueness premise is a separate
                           leaf, 4.5)
plural, distributive       the conjunction over the listed constants
same-witness group         ∃ a: each span's predication holds at a (4.6)
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
assertive reading          A := ∃x (D(x) ∧ ∀y (D(y) → y = x) ∧ P(x))          one claim; false when there is no or
                                                                              more than one D
presuppositional reading   premise  U(D)   as the labelled leaf discourse:presupposition:<mention>
                           claim    ∀x (D(x) → P(x))                          checked only under that displayed premise
```

Under the presuppositional reading the presupposition is proved from the document's premises (a certificate,
listed as `certificate` support) or retained as an admitted assumption (listed in the residual as an assumption);
if neither, the mention is `PresuppositionUnresolved` and the unit stays pending (READINGS in translation, a question
in authoring). `description_definedness` (9.3): the assertive reading holds iff `U(D)` and the presuppositional
claim both hold. Never inferred: existence from "the" (fixture ξ has a model with no owner where the presuppositional
claim is vacuously true and the assertive one false), uniqueness from one known instance, or truth from a finite
lookup. Contextual restrictions ("the owner", in a section about the API, meaning `owns(x, api)`) are explicit in
the manifest's `restriction` or the mention is unresolved. Competing presupposition/accommodation readings are two
readings of one set, distinguished by a situation.

### 4.6 Same-witness fusion

"A service is deployed. It is reviewed" licenses no fresh constant and no two unrelated existentials. The
same-witness reading is the group reading with content `∃x (deployed(x) ∧ reviewed(x))` (`sharedWitness` holds: one
outermost existential whose body is a conjunction in which every conjunct mentions the bound variable), presented
as `Some service is deployed and reviewed.` and bound to both spans; the other readings (the pronoun targets a
registered constant; the sentences are unrelated) remain alternatives in the set. A universal followed by "it"
likewise needs an explicit scoped rewrite (`Every service is deployed and reviewed.`). Fusion changes the reviewed
presentation, never the historical source boundaries: both spans keep their bytes, each receives the group's status,
and no fragment is admitted on its own (theorem `group_single_assertion`, 9.3; fixture μ shows the split reading
`∃x deployed(x) ∧ ∃x reviewed(x)` is weaker on a two-element model).

### 4.7 Document names, validity claims and the truth boundary

A document name is a constant (1.6); the environment's sort `document_sort` and its constants are the author's
declarations, so the profile adds no symbol (`document_sort_conservative`, 9.6: old-vocabulary consequences are
unchanged by declaring the sort and its constants).

A **validity claim** is a `meta` unit bound in the manifest to a document name and a polarity
(`{"validity": {"document": "policy2", "holds": true}}` in the unit's discourse binding; the wording is 2.1). It
has no content and enters no premise list; it is evaluated in a **second phase**, after admission, from the
admission verdicts alone:

```text
Valid(d)   := the document d refers to is admitted (admitDiscourse succeeds on it)
self       Valid = this document's own admission; computed on stripValidity(D), the document with every validity
           binding removed, so the verdict never depends on any validity unit (validity_independent, 9.6)
embedded   the unit's bytes are loaded as a document (depth + 1) and checked; the pinned document_id, if any, must
           equal the recomputed one (StaleTarget otherwise)
import     the stored bytes are re-fingerprinted (source_id must equal the pin) and checked (depth + 1); bytes absent
           or the check UNKNOWN: verdict `unconfirmed` (never assumed valid, never refuted)
part       no validity claim (UnsupportedTarget: part): a section is not a document
verdict    checked   when Valid(d) = holds
           refuted   when Valid(d) ≠ holds        warning ValidityRefuted: <unit>; admission unchanged
           unconfirmed (reason)                  report line; the unit is LABELLED
```

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
                    empty: InvalidCompatibility: <sets> (a manifest validation error, 4.1(8)), distinct from
                    inconsistent premises inside an existing choice, which keep W2's inconsistency and vacuity report
Conj(c)          := the conjunction of the chosen readings' contents (same environment, same background, all
                    assertion readings)
Joint(K)         := ⋁_{c ∈ JointSet(K)} Conj(c)                 defined only when JointSet(K) ≠ ∅
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

### 4.9 The three operations

"See Article 29 of the Universal Declaration of Human Rights" is a navigation instruction: a `navigation` mention
to an anchor, LABELLED, no premise. "Eligible has the meaning defined in section 2" selects the pinned W3
declaration exported by that anchor at `definitions_version` (signature and body); it neither invents a definition
nor changes its environment; a later change of the definition is `StaleTarget`. "By clause 2.1, the API is safe"
requests a W3 checked deduction: matching environment identity, every cited non-background transitive leaf listed
among the citing claim's own hypotheses, compatible reading choices and inherited transitive leaves; all retained
assumptions, bridges and reading choices remain visible (`Bundle.checkLemma`, unchanged). A link alone performs
neither of the latter two operations. Missing imported content stays unresolved; no live lookup can change committed
meaning. Renumbering preserves target identity but refreshes source/display approval; duplicate numbers, ambiguous
editions and dangling anchors fail; navigation cycles are harmless, inference cycles fail.

## 5. What stays frozen

`ve.discourse@1` adds no operator, no checker rule, no symbol and no premise other than the explicit
`discourse:presupposition:<mention>` leaves and the elaborated formulas themselves, which are P0 formulas with P0
`meaning_id`s. Old routes, canonical bytes, meanings and certificates are unchanged; `ve.prose@1` behaviour is
retained; `ve-document@1` documents load, check and identify exactly as before through the `@2` loader
(`format1_unchanged`). The obligations of VISION's converged rule (a committed failed elaboration case,
conservativity, executable model validity, certificate/countermodel soundness, composition) are met by reuse:
the elaborated formulas go through the unchanged P0/W1/W3 routes, whose theorems apply verbatim; what is new and
must be proved is that the elaboration is faithful to `Intended` (4.4), that the joint disjunction corresponds to
the compatibility relation (4.8), and that bindings are exact (3.3). Existential witness naming is not presented as
W3's unique conservative expansion; there is no witness naming.

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
`references` (per mention: form, target kind, target, `resolved` | `pending` | `ambiguous` | `navigation`),
`groups` (each fused reading with its spans and status), `presuppositions` (proved, assumed, unresolved),
`validity_claims` (checked, refuted, unconfirmed with reason), `self_truth_labels`, `definition_references` (with
pinned versions), `citations` (with retained leaves), `joint_choices` (count, constraints, or `invalid` /
`UNKNOWN(budget)`). Reference-resolution counts are reported separately from C/L/O/R/U bytes and units and never
enter them: a resolved pronoun in an UNFORMALISED unit changes no status.

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
| `AmbiguousReference: <mention>: <targets>` | more than one accessible target modulo aliases | error (as above) |
| `InaccessibleTarget: <mention>: <target>` | recorded target exists but `Acc` fails (scope, competing quantifier, quotation) | error |
| `WitnessEscape: <mention>` | recorded target is a binder of another sentence or outside its scope | error |
| `TargetKindMismatch: <mention>: <form>, <kind>` | form and target kind do not fit (1.4) | error |
| `UnsupportedTarget: <mention>: <kind>` | `this`/`that` as a claim or action term; collective/generic plural; validity of a `part` | error (READINGS/UNFORMALISED unit) |
| `StaleTarget: <mention>: <target>@<version>` / `StaleTarget: definitions@<version>` | target content, definition version, pinned fingerprint or `definitions_version` differs from the regenerated one | error |
| `DanglingAnchor: <anchor>` / `DuplicateAnchor: <label>` / `AmbiguousEdition: <document>` | anchor table (1.2) | error |
| `DependencyCycle: <sorted names>` | definition/proof dependency cycle (4.1(9)); W1's shared text | error |
| `InvalidCompatibility: <sets>` | empty compatible-joint set (4.8) | error |
| `IndependentFragment: <unit>` | a grouped unit carries content or its own reading set | error |
| `WitnessSplit: <set>@<version>:<reading>` | a `same-witness` content does not share its witness | error |
| `PresuppositionUnresolved: <mention>` | presuppositional reading with the uniqueness premise neither proved nor admitted | pending (not a rejection) |
| `ManifestMismatch: <field>` | regenerated binding, formula or table differs from the manifest | error |
| `UnknownDocument: <name>` / `DuplicateDeclaration: anchor <id>` / `mention <id>` / `document <name>` / `name <display>` | tables (1.2, 1.3, 1.4, 1.6) | error |
| `ImportCycle: <source ids>` / `ResourceLimit: document nesting` | 4.1(10) | error |
| `ResourceLimit: mentions` / `anchors` / `joint choices` / `resolution` | limits (11); the last two are UNKNOWN for dependent verdicts | error / UNKNOWN |
| `InvalidInput: document sort <s> has other constants` / `restriction of <mention> mentions <q>` / `null in discourse block` | field consistency (3.1) | error |
| `UnsupportedProfile: ve.discourse@1 requires ve-document@2` | profile gate | error |
| `ValidityRefuted: <unit>` | a validity claim's polarity disagrees with the verdict (4.7) | warning |
| `SelfTruth: <unit>` | a self-truth sentence recognised and labelled (4.7) | label |

Order: format and profile, the `@1` checks, anchors, names and documents, mentions in source order (existence,
kind fit, accessibility, uniqueness, elaboration), groups and constraints, the joint set, the dependency DAG,
embedded/imported documents, limits; validity claims are evaluated after admission (4.7). English diagnostics carry
the span and the plain-language expectation as today. Existing P0, W1, W2 and W3 diagnostics are unchanged.

## 9. Lean (sequence 3): definitions and the exact statements to prove

Files: `lean/VE/Discourse/Manifest.lean` (1.2 to 1.6 as data, `WellFormedDiscourse`), `Access.lean` (`Acc`,
`accessible`), `Resolve.lean` (`Derives`, `Resolve`, `Accepted`, `validate`), `Elaborate.lean` (`elaborateD`,
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
open VE.Route.Admission (ReadingSet Doc DocUnit Lemma Label parseLabel disjunction)

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
  name : String                       -- constant | "binder:<i>" | predicate | unit list key | anchor | rule | meaning id | document
  version : Option Nat
  deriving DecidableEq, Repr

structure Anchor where
  id : String; kind : String; parent : Option String; label : String
  span : Nat × Nat; edition : Option String
  deriving DecidableEq, Repr

structure Name where
  constant : String; display : String; scope : String; aliases : List String
  deriving DecidableEq, Repr

structure Mention where
  id : String; unit : String; span : Nat × Nat; form : Form; target : Target
  restriction : Option VE.Formula     -- context [sort]; index 0 is the described entity
  reading : Option Reading
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
def competingQuantifier (D : DDoc) (m : Mention) (sort : String) : Bool   -- a binder of `sort` earlier in the innermost anchor or earlier in m's sentence
def binderScopes (D : DDoc) (m : Mention) (i : Nat) : Bool                -- binder i of m's own sentence scopes over m's slot
def Acc (D : DDoc) (m : Mention) (t : Target) : Prop
def accessible (D : DDoc) (m : Mention) : List Target
def AliasEq (D : DDoc) (t t' : Target) : Prop                              -- equal, or the same constant through declared aliases

/-- 4.3: derivations with slots; the independent resolution relation. -/
structure DTree where tree : VE.English.Tree; slots : List Mention
def Derives (D : DDoc) (s : List VE.English.Tok) (d : DTree) : Prop
def Assignment := Mention → Target
def elaborateD (D : DDoc) (d : DTree) (σ : Assignment) : Option VE.Formula   -- capture-avoiding slot substitution
def Resolve (D : DDoc) (s : List VE.English.Tok) (A : VE.Formula) : Prop :=
  ∃ d σ, Derives D s d ∧ (∀ m ∈ d.slots, Acc D m (σ m) ∧ σ m = m.target) ∧
    elaborateD D d σ = some A ∧ A.check D.E [] = true
def Accepted (D : DDoc) (s : List VE.English.Tok) (A : VE.Formula) : Prop :=
  Resolve D s A ∧ ∀ d' σ', Derives D s d' → (∀ m ∈ d'.slots, Acc D m (σ' m)) →
    ∃ d σ, Derives D s d ∧ (∀ m ∈ d.slots, σ m = m.target) ∧ d'.tree = d.tree ∧
      ∀ m ∈ d.slots, AliasEq D (σ' m) (σ m)
/-- The executable validator (untrusted proposals in, one formula out); fuel = mentions + anchors + 1. -/
def validate (D : DDoc) (unit : String) : Except String VE.Formula
def Supported (D : DDoc) (s : List VE.English.Tok) : Prop        -- the supported fragment: forms of 1.4 over the core grammar

/-- 4.4: the intended meaning, by recursion on the derivation against S. -/
def SlotDenote (D : DDoc) (S : VE.Structure) (m : Mention) (t : Target) : (S.Carrier → Prop) → Prop
def Intended (D : DDoc) (s : List VE.English.Tok) (S : VE.Structure) : Prop   -- ∃ accepted (d, σ), the derivation's meaning with SlotDenote

/-- 4.5 -/
def uniqueD (Dr : VE.Formula) : VE.Formula                     -- ∃x (Dr x ∧ ∀y (Dr y → y = x))
def assertive (Dr P : VE.Formula) : VE.Formula                 -- ∃x (Dr x ∧ ∀y (Dr y → y = x) ∧ P x)
def presupposed (Dr P : VE.Formula) : VE.Formula               -- ∀x (Dr x → P x)
def presuppositionLeaf (m : Mention) (Dr : VE.Formula) : String × VE.Formula :=
  ("discourse:presupposition:" ++ m.id, uniqueD Dr)

/-- 4.6 -/
def fused (φ ψ : VE.Formula) : VE.Formula                      -- ∃x (φ ∧ ψ), one binder
def sharedWitness (φ : VE.Formula) : Bool
def groupFormula (D : DDoc) (g : Group) : Option VE.Formula
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
def compatibleChoices (K : Manifest) (sets : List ReadingSet) (limit : Nat) : Except String (List Choice)
  -- .error "InvalidCompatibility: <sets>" when empty; .error "ResourceLimit: joint choices" beyond limit
def readingsOf (sets : List ReadingSet) (c : Choice) : List VE.Formula
def conj : List VE.Formula → Option VE.Formula                   -- right-nested ∧; [] ↦ none
def joint (sets : List ReadingSet) (cs : List Choice) : Option VE.Formula   -- disjunction of the conj's; [] ↦ none
def occurring (sets : List ReadingSet) (cs : List Choice) : List VE.Formula  -- every reading in some c ∈ cs

/-- 4.7 -/
def stripValidity (D : DDoc) : DDoc := { D with K := { D.K with validity := [] } }
def refersSelf (D : DDoc) (name : String) : Prop := ∃ d ∈ D.K.documents, d.name = name ∧ d.refers = .self
def refersImport (D : DDoc) (name key : String) : Prop := ∃ d ∈ D.K.documents, d.name = name ∧ d.refers = .imported key
def withDocuments (E : VE.Environment) (sort : String) (names : List String) : VE.Environment
def importNodes (D : DDoc) : List VE.Route.DepNode              -- source id → source ids it embeds or imports

structure Admitted where
  doc : DDoc
  base : VE.Route.Admission.Admitted                             -- the unchanged W2 result on the elaborated document
  documentId : String
  bound : String → Option VE.Formula                             -- the elaborated formula of each bound unit
  validity : String → Option Verdict
  selfTruth : List String
  premiseUnits : List String

def admitDiscourse (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (j : Json)
    (fuel : Nat) : Except String Admitted
def documentId2 (front : Json) (prose : ByteArray) (fences : List (String × String)) : String
def project1 (j : Json) : Json                                    -- the ve-document@1 document with elaborated content in place of bound units
```

`VE.Route.DepNode` and `VE.Route.dependencyOrder` are the shared DAG machinery (W1 4.1); `Wire.RouteVocabulary`,
`Wire.decodeClosed`, `Wire.meaningId`, `VE.Route.Admission.Admitted` are the frozen P0/W2 names. The tuple and
valuation conventions are P0's: closed formulas use `[]`; a description's restriction is evaluated at `[a]`.

### 9.2 Theorems: accessibility and resolution (plan obligation 1)

```lean
/-- The list and the relation agree. -/
theorem accessible_iff (D : DDoc) (m : Mention) (t : Target) : t ∈ accessible D m ↔ Acc D m t

/-- No heuristic: accessibility depends only on registrations, anchors, declarations, the mention's unit, form and
    own-sentence binders. Two documents agreeing on those agree on Acc, whatever else they contain. -/
theorem acc_no_heuristic (D D₂ : DDoc) (m : Mention) (t : Target)
    (hK : D.K.names = D₂.K.names ∧ D.K.anchors = D₂.K.anchors ∧ D.K.documents = D₂.K.documents ∧
          D.K.definitionsVersion = D₂.K.definitionsVersion ∧ D.E = D₂.E)
    (hu : D.text m.unit = D₂.text m.unit) (hq : ∀ s, competingQuantifier D m s = competingQuantifier D₂ m s)
    (hb : D.base.units.map DocUnit.id = D₂.base.units.map DocUnit.id) :
  Acc D m t ↔ Acc D₂ m t

/-- Witness scope: a binder target is accessible only inside its own sentence and under its scope. -/
theorem no_witness_escape (D : DDoc) (m : Mention) (i : Nat)
    (h : ¬ binderScopes D m i) : ¬ Acc D m ⟨.entity, "binder:" ++ toString i, none⟩

/-- Names are scope-based, not distance-based: a registered constant is accessible at every unit of its scope
    without a competing quantifier, and at no unit outside it. -/
theorem name_scope (D : DDoc) (m : Mention) (c : String) (n : Name) (hn : registered D c = some n)
    (hf : m.form = .pronoun ∨ m.form = .demonstrative) :
  Acc D m ⟨.entity, c, none⟩ ↔ within D m.unit n.scope = true ∧ competingQuantifier D m (sortOf D.E c) = false

/-- Kinds never coerce. -/
theorem kind_fit (D : DDoc) (m : Mention) (t : Target) (h : Acc D m t) : formFits m.form t.kind = true

/-- The validator is sound: whatever it returns is the unique accepted resolution of that unit's text. -/
theorem validate_sound (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List VE.English.Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) : Accepted D s A

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
    (S : VE.Structure) (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S (contextOf d) ρ) :
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

/-- 4.5: definedness of the assertive reading. -/
theorem description_definedness (E : VE.Environment) (Dr P : VE.Formula) (σ : String)
    (hD : Dr.WellFormed E [σ]) (hP : P.WellFormed E [σ]) (S : VE.Structure) (hS : S.Admissible E) :
  (assertive Dr P).denote S [] ↔ (uniqueD Dr).denote S [] ∧ (presupposed Dr P).denote S []

/-- The assertive reading is the unique-element statement, element-wise. -/
theorem assertive_denote (E) (Dr P) (σ) (hD) (hP) (S) (hS : S.Admissible E) :
  (assertive Dr P).denote S [] ↔
    ∃ a, VE.TypedAt S σ a ∧ Dr.denote S [a] ∧ (∀ b, VE.TypedAt S σ b → Dr.denote S [b] → b = a) ∧ P.denote S [a]

/-- The presuppositional reading's certificate carries the uniqueness leaf: a checked certificate for the claim
    over premises that include the leaf proves the claim only where the leaf holds (the P0 acceptance theorem,
    instantiated; reused, not restated). -/
theorem presupposition_retained (E) (Γ : List VE.Formula) (m : Mention) (Dr P : VE.Formula) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E (Γ ++ [(presuppositionLeaf m Dr).2]) (presupposed Dr P) c = true)
    (S : VE.Structure) (hS : S.Admissible E) (hΓ : VE.Norms.Sat S Γ) (hU : (uniqueD Dr).denote S []) :
  (presupposed Dr P).denote S []

/-- 4.6: a group contributes exactly one formula to the premise list, and each of its spans has the group's status. -/
theorem group_single_assertion (D : DDoc) (h : WellFormedDiscourse D = true) (g : Group) (hg : g ∈ D.K.groups)
    (res : Admitted) (ha : admitDiscourse profiles environment rv (encode D) fuel = .ok res) :
  (∃ φ, groupFormula D g = some φ ∧ (res.premiseUnits.filter (· ∈ g.spans)).length = 1 ∧
     ∀ u ∈ g.spans, res.bound u = some φ) ∧
  ∀ u ∈ g.spans, (unitOf D.base u).bind DocUnit.content = none

/-- The fused reading implies the split reading; the converse is refuted on a concrete model (Examples.lean). -/
theorem fused_implies_split (E) (φ ψ : VE.Formula) (σ : String) (hφ : φ.WellFormed E [σ]) (hψ : ψ.WellFormed E [σ]) :
  VE.Entails E [fused φ ψ] (.and (.exists σ φ) (.exists σ ψ))
theorem split_not_fused_model :
  (Examples.splitFormula).eval Examples.twoServices [] = true ∧
  (Examples.fusedFormula).eval Examples.twoServices [] = false

/-- Shared witness is decided syntactically and is what the group check requires. -/
theorem sharedWitness_spec (φ : VE.Formula) :
  sharedWitness φ = true ↔ ∃ σ body, φ = .exists σ body ∧ IsConjunctionMentioningZero body
```

### 9.4 Theorems: joint choices and citation composition (plan obligation 4)

```lean
/-- The enumeration is exactly the compatibility relation, and never empty on success. -/
theorem compatible_sound (K : Manifest) (sets : List ReadingSet) (n : Nat) (cs : List Choice)
    (h : compatibleChoices K sets n = .ok cs) : (∀ c, c ∈ cs ↔ Compatible K sets c) ∧ cs ≠ [] ∧ cs.length ≤ n
theorem compatible_empty_error (K) (sets) (n) (hε : ∀ c, ¬ Compatible K sets c) :
  compatibleChoices K sets n = .error ("InvalidCompatibility: " ++ setsText sets)

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

/-- Independence: without constraints the per-unit shortcut and the joint enumeration give the same verdicts. -/
theorem independent_shortcut (E) (K) (hK : K.constraints = []) (sets) (cs) (hcs) (Γ) (φ) (J) (hJ : joint sets cs = some J) :
  VE.Entails E (Γ ++ [J]) φ ↔ VE.Entails E (Γ ++ (sets.filterMap (fun rs => disjunction rs.readings))) φ

/-- Citation composition is W3's, reused: a citing lemma's transitive leaves include every cited leaf, its reading
    choices are compatible, and the manifest's recorded choices equal the choices derived from the leaves. -/
theorem citation_choices_retained (E) (bg) (sets) (bind) (known : List VE.Definitions.Bundle.Known)
    (L : VE.Definitions.Bundle.Lemma) (k : VE.Definitions.Bundle.Known)
    (h : VE.Definitions.Bundle.checkLemma E bg sets bind known L = .ok k) :
  VE.Definitions.Bundle.ReadingCompatible k.leaves ∧
  (∀ m ∈ L.cites, ∀ k' ∈ known, k'.meaningId = m → ∀ l ∈ k'.leaves, l ∈ k.leaves) ∧
  VE.Definitions.Bundle.choicesEqual L.choices k.choices = true
theorem manifest_choices_are_labels (D : DDoc) (res : Admitted) (h : admitDiscourse profiles environment rv (encode D) fuel = .ok res)
    (L : VE.Definitions.Bundle.Lemma) (hL : L ∈ lemmasOf D) :
  VE.Definitions.Bundle.leafChoices L.leaves = .ok (choicesAsLabels D.K.choices L)
```

### 9.5 Theorems: English correspondence and binding (plan obligation 5)

```lean
/-- The discourse surface: texts are unit token lists with slot forms; meanings are (formula, assignment) pairs;
    render is the reviewed presentation (the expansion); parse is validate. -/
def discourseSurface (D : DDoc) (L : VE.English.Lexicon) : VE.English.Surface

theorem discourse_parseRender (D : DDoc) (h : WellFormedDiscourse D = true) (L) :
  VE.English.ParseRender (discourseSurface D L)
theorem discourse_uniqueDerivation (D) (h) (L) : VE.English.UniqueDerivation (discourseSurface D L)
theorem discourse_parseSound (D) (h) (L) : VE.English.ParseSound (discourseSurface D L)
theorem discourse_oneReading (D) (h) (L) : VE.English.OneReading (discourseSurface D L)
  -- := VE.English.oneReading_of (discourse_parseSound D h L) (discourse_uniqueDerivation D h L)

/-- The reviewed presentation is ordinary English with the same formula: the expansion parses, through the unchanged
    core parser, to exactly the elaborated formula. -/
theorem presentation_expands (D : DDoc) (h) (L) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
  VE.English.parse D.E L (presentation D L u) = some [A]
```

### 9.6 Theorems: documents, validity, conservativity and the wire

```lean
/-- The `@1` path is delegated unchanged. -/
theorem format1_unchanged (profiles) (environment) (rv) (j : Json) (fuel)
    (h1 : (j.getObjValD "format").getStr? = .ok "ve-document@1") :
  admitDiscourse profiles environment rv j fuel = (VE.Route.Admission.admitDocument profiles environment rv j).map lift1

/-- The `@2` admission is W2's admission of the projected document, plus the discourse checks. -/
theorem admission_projects (profiles) (environment) (rv) (j) (fuel) (res : Admitted)
    (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  VE.Route.Admission.admitDocument profiles environment rv (project1 j) = .ok res.base ∧
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
theorem validity_import (profiles) (environment) (rv) (j) (fuel) (res) (h : admitDiscourse profiles environment rv j (fuel + 1) = .ok res)
    (v : Validity) (hv : v ∈ res.doc.K.validity) (key : String) (hi : refersImport res.doc v.document key)
    (imp : Import) (hk : imp ∈ res.doc.K.imports ∧ imp.key = key) :
  (imp.bytes = none → res.validity v.unit = some (.unconfirmed "import bytes absent")) ∧
  (∀ b, imp.bytes = some b → sourceIdOf b ≠ imp.sourceId → res.validity v.unit = none ∧ False) ∧   -- StaleTarget: admission fails
  (∀ b, imp.bytes = some b → sourceIdOf b = imp.sourceId →
     (res.validity v.unit = some .checked ↔ (v.holds ↔ (admitDiscourse profiles (envOf b) (rvOf b) (jsonOf b) fuel).isOk)))
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

/-- Declaring the document sort and its constants changes no old-vocabulary consequence. -/
theorem document_sort_conservative (E : VE.Environment) (sort : String) (hs : sort ∉ E.sorts) (names : List String)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ g ∈ Γ, g.WellFormed E []) (hφ : φ.WellFormed E []) :
  VE.Entails (withDocuments E sort names) Γ φ ↔ VE.Entails E Γ φ

/-- Binding: every result is bound to the recomputed identities and the regenerated bindings; a changed target
    fails replay. -/
theorem discourse_wire_binding (j : Json) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res) :
  res.doc.sourceId = Wire.sourceId (prose j) ∧
  Wire.decodeManifest (j.getObjValD "discourse") = .ok res.doc.K ∧
  (∀ u A, res.bound u = some A → ∃ mid, Wire.meaningId profiles (envIdOf environment) (Wire.encodeFormula A) = .ok mid ∧
     boundMeaningId res u = some mid) ∧
  res.doc.K.definitionsVersion = envIdOf environment
theorem stale_target_rejected (j j' : Json) (res : Admitted) (h : admitDiscourse profiles environment rv j fuel = .ok res)
    (u : String) (m : Mention) (hm : m ∈ res.doc.K.mentions ∧ m.unit = u)
    (hchange : targetObject j m ≠ targetObject j' m) (c : VE.Tableau.Certificate) (hc : c ∈ certificatesOf j u) :
  ∀ res', admitDiscourse profiles environment rv j' fuel = .ok res' → c ∉ acceptedCertificates res' u

/-- The public entry point, as Norms.Run.norms_wire_acceptance: a successful `admission` answer is exactly the
    encoding of a checked discourse admission whose bindings equal the recomputed digests and regenerated tables. -/
theorem Run.discourse_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hd : Run.usesDiscoursePath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.DiscourseAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
```

### 9.7 The executable `ve_discourse_route`

`lean/.lake/build/bin/ve_discourse_route <cases.json>`, root `DiscourseMain.lean`, a new Lake target; `Run.main` is
the executable root and no frozen file changes. On raw input it runs the frozen envelope and profile gate, requires
`ve.discourse@1` and format `ve-document@2` (or delegates a `@1` document unchanged), decodes the environment through
the frozen decoder plus a strict discourse decoder (unknown fields rejected; `null` rejected; the original complete
environment hashed), decodes the manifest, runs `WellFormedDiscourse`, regenerates every binding, elaborates every
bound unit, projects the `@1` document and delegates its admission, graph and premise checks to the unchanged W2
functions, evaluates validity claims in the second phase, and binds the `@2` `document_id`. Case kinds:

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
W8's fidelity gate. No theorem that a validity claim about an import is true when its bytes are absent (it is
`unconfirmed`). No theorem about SHA-256 injectivity: identity statements are on canonical objects and transfer to
digests under the occurrence hypotheses of P0 3.9. No coverage theorem. Rust never resolves references (11).

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind, from
Lean (`tests/test_discourse*.py`, the `discourse` conformance family). Unless a fixture says otherwise: sorts
`service`, `person`, `document`; constants `api : service` (display "the API"), `alice`, `bob : person`; unary
predicates `reviewed`, `deployed`, `safe`, `ready`, `eligible`, `owner`; binary `manager_of(person, person)`,
`supersedes(document, document)`; one root anchor `doc` and section anchors `sec1`, `sec2`; every registered name
has scope `doc`; profiles `relational-fol@0`, `ve.discourse@1`; format `ve-document@2`.

- **(α) Named antecedent.** Units u1 "The API is reviewed." u2 "It is safe." Mention m1 (`It`) → `entity api`.
  Expected: `reviewed(api)`, `safe(api)`, both CHECKED; presentation of u2 "The API is safe."; provenance keeps
  "It"; `references: 1 resolved`; bytes of u1 and u2 counted once each. The same manifest with m1 → `entity alice`:
  `TargetKindMismatch` (sort) and `ManifestMismatch: mentions.m1.target`.
- **(β) Competing quantifier.** u1 "A service is deployed." u2 "The API is reviewed." u3 "It is safe." Expected:
  `UnresolvedReference: m1` in authoring with the question "Does ‘it’ mean the API, or the service just mentioned?"
  offering "The API is safe." and the group reading "Some service is deployed and safe." (with u1); translation: an
  open set of those two readings with distinguishing models. With u1 moved into `sec1` and u2, u3 into `sec2`
  (different innermost anchors): m1 → `api` resolves (scope-based, no distance).
- **(γ) Gender never selects.** "Alice is reviewed. Bob is reviewed. She is ready." Expected:
  `AmbiguousReference: m1: alice, bob`; the question offers both; a manifest recording `alice` without a signed
  choice or narrowing is `ManifestMismatch`.
- **(δ) Demonstrative.** "This service is safe." with m1 → `api`: presentation "The API is safe.", CHECKED. "This
  claim is disputed." with m1 recorded as `claim`: `UnsupportedTarget: m1: claim`; the unit is UNFORMALISED with the
  reference recorded.
- **(ε) `such`.** "Every reviewed service is deployed. Every such service is safe." with m1 → `predicate reviewed`:
  presentation "Every reviewed service is safe."; `∀x (reviewed(x) → safe(x))`; CHECKED. A `such` with no bound
  property: `UnresolvedReference`.
- **(ζ) Ordinal pair.** "Alice and Bob are reviewed. The former is ready." → `alice`; "Alice is ready."; no
  inequality premise (a model with `alice = bob` is not excluded by the document; the vacuity report is unchanged).
  Two candidate pairs in scope: `AmbiguousReference`. "The latter" → `bob`.
- **(η) Possessive description.** "Alice is reviewed. Her manager is ready." m1 (`Her`) → `alice`; m2 (`Her
  manager`) `definite`, restriction `manager_of(x, alice)`. Assertive: `∃x (manager_of(x, alice) ∧ ∀y (manager_of(y,
  alice) → y = x) ∧ ready(x))`. Presuppositional with `Γ ⊢ U(D)` certified: claim `∀x (manager_of(x, alice) →
  ready(x))` CHECKED with leaf `discourse:presupposition:m2` listed; without a certificate and without an admitted
  assumption: `PresuppositionUnresolved: m2`, unit pending. Countermodels: a model with two managers of Alice
  refutes both `U(D)` and the assertive reading; with none, the presuppositional claim is vacuously true and the
  vacuity report says so.
- **(θ) Plural.** "Alice and Bob are reviewed. They are ready." distributive → `ready(alice) ∧ ready(bob)`,
  presentation "Alice is ready and Bob is ready."; "They" with no listed constants in scope:
  `UnresolvedReference`; a recorded `collective` reading: `UnsupportedTarget`.
- **(ι) Definition reference (J1).** `sec2` exports W3 `eligible`@2. "Every eligible service is reviewed, where
  eligible has the meaning defined in section 2." → rewrite "Eligible has the meaning defined in section 2. Every
  eligible service is reviewed."; m1 → `predicate eligible` version 2; `∀x (eligible(x) → reviewed(x))` CHECKED
  under W3's definition Background. Changing the definition body (version 3) with the manifest still pinning 2:
  `StaleTarget: m1: eligible@2`; every certificate of dependent units fails replay. Section 2 exporting no
  `eligible`: `UnresolvedReference`.
- **(κ) Anchors.** Anchors "Article 29" with items "29.1" to "29.3"; a `section_ref` to "29.3" resolves; two
  anchors labelled "2" under `doc`: `DuplicateAnchor: 2`; a reference to "section 4" with no anchor:
  `DanglingAnchor: section 4`; renumbering "2" to "3": anchor id unchanged, `document_id` changed, presentation
  approval required, no `StaleTarget`; a `definition_ref` to a definition whose anchor cites a lemma that cites the
  definition: `DependencyCycle: <names>`; two navigation mentions pointing at each other's sections: accepted.
- **(λ) Three operations.** "See Article 29 of the Universal Declaration of Human Rights." LABELLED navigation, no
  premise. "By clause 2.1, the API is safe." with lemma `2.1` earlier in the bundle: CHECKED via `cite:` with every
  transitive leaf of `2.1` listed among the citing unit's leaves; the same with one cited leaf stripped: W3's
  "Citation transitive leaf labels were changed or stripped"; the same with `2.1` under a different reading
  choice of a shared set: "Citation has incompatible reading choices". A bare link (`navigation`) to clause 2.1
  proves nothing.
- **(μ) Same-witness fusion and the J5 negatives.** u3 "A service is deployed." u4 "It is reviewed."; set `rs1` on
  u3, open, readings: `same-witness` (content `∃x (deployed(x) ∧ reviewed(x))`, group spans [u3, u4]),
  `named` (m1 → a registered service constant, if any), `unrelated` (u4 pending). Expected: group status OPEN on
  both u3 and u4; presentation of the group reading "Some service is deployed and reviewed."; bytes counted once.
  Negative 1: u4 also carries content `∃x reviewed(x)`: `IndependentFragment: u4`. Negative 2: the `same-witness`
  content recorded as `∃x deployed(x) ∧ ∃x reviewed(x)`: `WitnessSplit: rs1@1:same-witness`. Lean: on the
  two-element model `twoServices` (`s1` deployed not reviewed, `s2` reviewed not deployed) the split formula
  evaluates true and the fused one false (`split_not_fused_model`).
- **(ν) Universal plus `it`.** "Every service is deployed. It is reviewed." → `UnresolvedReference: m1` with the
  rewrite "Every service is deployed and reviewed."; the authored rewrite elaborates to `∀x (deployed(x) ∧
  reviewed(x))`; translation: an open set (the rewrite; a registered-constant reading if any).
- **(ξ) Description without a possessor.** "The owner is ready." restriction `owner(x)`. Assertive
  `∃x (owner(x) ∧ ∀y (owner(y) → y = x) ∧ ready(x))`; presuppositional as (η). Models: no owner (assertive false,
  presuppositional vacuously true, `U(D)` false), two owners (both false, `U(D)` false), one owner ready (both true).
  "The owner" with a registered name `owner` of a constant: a name, not a description (the manifest decides; both
  recorded is `DuplicateDeclaration: name the owner`).
- **(ο) Correlated readings (J4).** Sets `rs5` ("this pattern": `pattern-a`, `pattern-b`) and `rs6` ("it":
  `it-a`, `it-b`), constraints `requires (rs5, pattern-a) → (rs6, it-a)` and `requires (rs5, pattern-b) → (rs6,
  it-b)`. Joint set {(a, a), (b, b)}; ALL of φ needs a proof from `Joint`; NONE: one model satisfying the four
  readings and refuting φ; SOME: a certificate under (a, a) and a countermodel under (b, b). Constraints
  `excludes` on all four combinations: `InvalidCompatibility: rs5, rs6`. Seven sets of two readings each (128
  choices) with no constraints: `ResourceLimit: joint choices`, verdict UNKNOWN, statuses unchanged. No constraints,
  two sets: the joint verdicts equal W2's `ve document readings --conclusion` verdicts on the same document. A `Γ`
  contradicting one compatible choice's readings: that choice's certificate is `vacuous`; the joint set is
  unchanged.
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
  `source_id` equal to the pin: re-checked, `checked` (or `refuted` when the stored document is rejected); bytes
  absent: `unconfirmed (import bytes absent)`, unit LABELLED, no error; bytes with another `source_id`:
  `StaleTarget: policy2`; a chain A imports B imports A (same source ids): `ImportCycle: <ids>`; five levels of
  embedding: `ResourceLimit: document nesting`.
- **(υ) Self-truth.** "Everything in this document is true." / "This sentence is false." / "This document is
  correct." / "The above document is true." Each: kind `meta`, LABELLED, label `self-truth`, no content, absent from
  every premise list, `SelfTruth: <unit>` in the report; admission unchanged; a manifest binding one of them as a
  validity claim: `InvalidInput` (the wording is not a validity wording, 2.2).
- **(φ) Identity and tampering.** Mention target altered (m1 → `bob`) with unchanged text where `alice` is the
  unique accessible target: `ManifestMismatch: mentions.m1.target`; the elaborated formula on the wire differing
  from the regenerated one: `ManifestMismatch: bound.u2`; `definitions_version` not equal to `environment_id`:
  `StaleTarget: definitions@<v>`; a certificate of (α) replayed after u1 is edited to "The API is deployed.": the
  premise identities differ and replay fails; the `document_id` of every fixture changes under any manifest edit
  and is unchanged under a `weights` edit or JSON reformatting; a `ve-document@1` fixture loaded by the `@2` loader
  has byte-identical `document_id`, statuses and report.
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
statuses, verdicts, reports; `document_id` in the `@2` domain); the natural-view `It` cases (`natural-view.md`:
zero, one and multiple named referents; an earlier quantifier) reproduced through the manifest with identical
accept/reject outcomes; differential `validate` Python versus Lean on 1,000 generated manifests; the 200-graph DAG
differential extended to definition/citation dependency graphs; the mixed English harness (W7) extended with the
2.1 wordings, each passing the per-input all-derivations gate.

## 11. Limits, regeneration, Rust

Anchors ≤ 1,024, mentions ≤ 4,096, names ≤ 1,024, documents ≤ 64, imports ≤ 64, groups ≤ 256 with ≤ 16 spans each,
constraints ≤ 1,024, joint choices ≤ 64, document nesting ≤ 4, validator fuel = mentions + anchors + 1, restriction
formulas within `MAX_NODES`; every overflow is `ResourceLimit` with the limit named, never a verdict. Every binding,
elaborated formula, joint set, document table and identity is regenerated from the decoded document at every trusted
site (3.4); the manifest is validated, never trusted. Rust never resolves references: on the `elaborated-document`
family a discourse case carries the Python-generated elaborated formulas marked `untrusted: true`, and its verdict
must agree with Python's and Lean's regenerated ones (regression evidence; the trust path is Lean).

## 12. Statement review checklist (Astra + Fable, before sequences 2 to 5)

1. The seven target kinds and their non-coercion (1.4); the registered-name model of "the API" versus the
   description model of "the owner" (1.3, 4.5).
2. `Acc` (4.2): scope by anchor, no distance, the competing-quantifier condition (same sort, same innermost anchor
   or same sentence), binder locality, quotation identification without admission.
3. `Resolve`/`Accepted` (4.3): uniqueness modulo declared aliases; the all-derivations gate covering antecedent and
   scope alternatives; UNKNOWN never uniqueness.
4. `Intended` and `elaborate` (4.4) and the faithfulness statement (9.3); no witness constants or choice functions.
5. Descriptions (4.5): the two readings, the presupposition leaf, `PresuppositionUnresolved` as pending.
6. Fusion (4.6): one assertion per group, status through the group, `sharedWitness`, the J5 negatives.
7. Document names, validity claims and the truth boundary (4.7): the second phase, `stripValidity`, refutation as
   a warning, `unconfirmed` for absent bytes, self-truth as LABELLED `meta`; stratification by source id.
8. The joint set (4.8): `requires`/`excludes` only, nonempty requirement, `joint_all_iff`, the shortcut regained
   without constraints, NONE with one shared model, SOME.
9. The three operations (4.9) and the J2 citation wording.
10. What stays frozen (5) and `format1_unchanged`; the `@2` identity domain (3.3).
11. The English table (2.1): one reading per wording; the synonyms (2.2); the reviewed presentation (6).
12. The diagnostics (8) and the fixtures (10), each against the definitions.
13. The resolved choices of section 13.

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
16. **The self-reference wording** follows VISION's boundary note (branch `docs/self-reference`, 2026-09-28)
    exactly: validity claims supported and checked; truth claims labelled.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-28 | Draft 1 | Item-1 specification from the plan as revised by the converged debate (J1 to J8) and the lead's document-name/validity/truth input: the manifest with seven target kinds; the English table; wire form and the `@2` identity domain; accessibility, resolution, elaboration and `Intended`; descriptions with the presupposition leaf; same-witness groups with the J5 negatives; document names, validity claims in a second phase, the self-truth label and stratification; the joint set with declared constraints and the nonempty requirement; the three operations with the J2 citation wording; report, diagnostics; every theorem of the plan's five obligation groups plus documents as a statement; fixtures α to ω; resolved choices. Spec only: no code, Lean or frozen contract changed. |
