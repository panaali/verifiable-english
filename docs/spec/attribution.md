# Reports and attitudes (`reports@0`): structured reported content, attitude wrappers and open assessments over `ve-document@1`

> Status: item-1 specification, draft 10 (2026-09-28), written from [attribution-PLAN.md](attribution-PLAN.md)
> revision 9. Draft 1 transcribed the converged Astra/Fable design debate
> (`manage-agents/debates/design-attribution/{astra,fable}.md`: BUILD after six text edits, CONVERGED after
> round 2); draft 2 applies the converged FIX of the Astra/Fable statement review of draft 1
> (`manage-agents/debates/attribution-spec/{astra,fable}.md`: FIX, CONVERGED after round 3; the change log lists
> the nine edits); draft 3 applies the three findings of the read-only verification of draft 2 against that FIX
> (`manage-agents/attribution-p3ver1.final.md`: independence fixtures over premise subsets that keep the queried
> vocabulary, well-formed signed atoms in `reports_no_leak`, and `scoped_background_local` as no automatic
> insertion); draft 4 applies the two findings of the second read-only verification
> (`manage-agents/attribution-p3ver2.final.md`: a dropped key leaves `topKeys (D ▷ U)` only when no kept unit
> asserts or denies it, and fixture γ's subset premises list one registration atom per omitted unit); draft 5
> applies the finding of the third read-only verification (`manage-agents/attribution-p3ver3.final.md`: a
> registration unit can itself assert a dropped `says` key, so the properties of the premise-subset device are
> stated for documents with no `says` key) and the audit of every biconditional, "never" and "no …" claim that
> finding prompted: each is now stated with the fragment on which it holds, and section 10.3 gives one fixture at
> each boundary, nested attribution among them; draft 6 applies the three findings of the fourth read-only
> verification (`manage-agents/attribution-p3ver4.final.md`: 5.3's "exactly when" is stated for formula contents
> over `E`, a nested content being a generated atom that another unit may assert, fixture B₇; the checklist's
> situation line of 2.3 handles a nested content that another unit asserts, B₁; B₂ now forces the renumbering it
> exhibits) and a second audit pass that names `Γ_reports(D)` as the premise list of every entailment claim, the
> author's premises aside (B₈); draft 7 applies the orchestrator's design directive after the fifth read-only
> verification (`manage-agents/attribution-p3ver5.final.md`: "asserting the inner key entails the nested content"
> fails when the key is asserted at another holder, B₉, and for a negated nested content, `D_ω`): the normative
> semantic content of this specification is only its definitions, its theorem statements with every hypothesis
> explicit and its fixtures with expected results (section 0, "Normative content"); every prose entailment claim
> is either the reading of a named theorem under that theorem's hypotheses or deleted; nested-content entailment is
> stated on the holder-applied atom with its polarity explicit, as five theorem statements of 9.2
> (`nested_positive_entailed`, `nested_positive_refuted`, `nested_negated_entailed`, `nested_negated_refuted`,
> `holder_atom_free`), with boundary fixtures B₉ to B₁₂ offered as each breaking one hypothesis, and the questions
> the directive left open are in 4.6 (NON-NORMATIVE); draft 8 applies the three findings of the sixth read-only
> verification (`manage-agents/attribution-p3ver6.final.md`) as instances of that directive: `content_depth_bounded`
> is stated at the admitted bound `≤ 16`, with `Content.depth` defined in 9.1 so that a unit's content depth is its
> W2 kind depth (B₁₃, the verification's depth-16 document, and B₁₃′ beyond the bound); the one-hypothesis
> boundaries of `nested_independent` are B₁₁′ (a negated inner node) and B₁₂ (depth 2), single-unit documents in
> which the nested key is asserted and denied by nothing, while B₁₁, `D_ω` and B₁₂′, which also put that key at
> top level, break two of its hypotheses and are recorded as instances of the nested-content theorems; the table
> at the end of 10.3 names, for every boundary fixture, the theorem and the one hypothesis it breaks; and the
> plan's summary (revision 7) carries no unconditional semantic sentence; draft 9 applies the two findings of the
> seventh read-only verification (`manage-agents/attribution-p3ver7.final.md`) as instances of the same directive,
> each a fixture assertion corrected to what the definitions and statements give: B₂ is no instance of
> `nested_independent`, whose shape hypothesis `hb` names an inner `believes` node while B₂'s inner node is a
> `says` report, so B₂ is recorded as breaking exactly `hb`, the freedom of its nested atom being
> `unreported_key_free`'s at `k_in`; and B₁₂'s content depth is 4 under `Content.depth` (three report nodes over
> the formula leaf, its W2 kind of depth 4 likewise), not 3, its nesting depth of 2 counting the report nodes
> below the top-level one; draft 10 applies the finding of the eighth read-only verification
> (`manage-agents/attribution-p3ver8.final.md`) as an instance of the same directive: the collision check of 4.1
> step 4 is document-local, comparing only the objects the document digests (the content object of every node
> and the complement object of every report node, now named there, in 1.1 and in 3.4, with
> `no_collision_complement` beside `no_collision`), so the digest and name conclusions of
> `literal_paraphrase_distinct`, `negation_scopes_distinct` and `probably_not_scopes_distinct` are stated under
> occurrence hypotheses (`OccursComplement`, `Occurs`, 9.1: both objects digested by the document) in place of
> key-membership hypotheses, which the digest of an absent object could witness with one key; the
> canonical-object conjuncts are unchanged, and B₁₄ to B₁₆ are the boundaries at which one object is absent. It
> returns for the one focused statement review that gates items 2 to 5 of the plan
> (PLAN-EXPAND2 rule 10) and any implementation. Sections 4 to 6 and 9 are the statements under review; section 10
> gives the fixtures with their definitions (10.1) separated from their expected results (10.2) and the boundary
> fixtures (10.3); section 13 lists
> every point where this draft chose between readings of the plan. Theorem statements and fixtures are
> implementation obligations, not claims of completed proofs or tests. Inputs: [document.md](document.md) (W2),
> [norms.md](norms.md) (W1, cited `norms.md n`), [soft-norms.md](soft-norms.md) (whose Lean conventions this spec
> reuses), [verification-contract.md](verification-contract.md) (P1 to P11), [VISION.md](../../VISION.md) (the
> converged rule and the zero-training principle), [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md),
> [INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md), the frozen P0 route (`lean/VE/Route/{Layer,Route,Checker,
> Admission,Background}.lean`, [docs/P0-Lean-NOTES.md](../P0-Lean-NOTES.md)), and the four pinned sources of
> section 2.5. Nothing here changes a frozen contract, a W2 identity, a P0 label, a `norms@0` hash, a W1 theorem
> statement or a checker function.

## 0. Scope, one paragraph

A report is **a holder, an act, a context and an inspectable content**: "the article says that the service is
safe" asserts that a saying occurred and keeps "the service is safe" as a closed, typed, identity-bound content
that is displayed, checked locally and never promoted to a premise without an explicit bridge. Four acts are
admitted, saying, believing, wanting and intending; each is an arbitrary relation of the independent semantics
`(S, J)`, so, in the semantics, a report entails neither its content nor any other report, belief is not closed
under consequence, and an intention entails neither success nor obligation (over a document's own premise set,
what holds is what the theorem statements of 9.2 and 9.3 say under their hypotheses; 4.5 is their non-normative
reading). Two open assessments, `May` and `Probably`, are named
open judgments over content with W2's complete open-term record; admission checks their content and declared
criteria and establishes neither possibility nor likelihood. Elaboration generates, for every finite acyclic key
(act or judgment, holder sort, context with its tense, content), one fresh unary predicate in `E_reports`; the
route layer is `Layer.id` over `E_reports`, the report atoms (and, for a unit that denies a report, their
negations: negation is the only connective admitted over report statements in this slice) are document premises
in `Γ`, and two Lean obligations carry the meaning: `reports_elaboration_faithful` (truth preservation with
typed model correspondence in both directions) and `reports_old_language_conservative` (the vocabulary extension
changes no old-language consequence; signed report premises add exactly the holder disequalities they force,
4.4). Every certificate is bound to the whole document through a checked envelope digest. Bridges, norm
adoption and definition import are explicit typed operations that name their exact target; a certificate of
faithful quotation never discharges truth. The English has one reading per wording and round-trips together with
its bound environment, contexts, criteria, versions and reading choices, never through mutable defaults.

In this specification: the report document (1), the English (2), the wire form and identity (3), the semantics
and elaboration (4), scoped checks, bridges and assessments (5), status and coverage (6), the report (7),
diagnostics (8), the Lean definitions and every theorem of plan item 2 as a statement (9), the item-1 acceptance
fixtures (10), limits, regeneration and trust (11), the review checklist (12) and the resolved choices (13).

**Normative content.** The normative semantic content of this specification is exactly three things: (a) the
definitions (sections 1, 3, 4.1 to 4.4 and 9.1), (b) the theorem statements of 9.2 and 9.3, each with every
hypothesis explicit, and (c) the fixtures of section 10 with their expected results. Every other sentence about
what a document's premises entail, refute or leave free is a NON-NORMATIVE reading: it names the theorem it reads
and that theorem's hypotheses, or it is an example under a fixture, and it claims nothing the theorem statement
does not. Where such a reading and a theorem statement differ, the statement governs and the reading is a defect
to be repaired by deletion, never by rewording. Sections 4.5 and 4.6 are marked NON-NORMATIVE for this reason;
the prose of 2.3 and 5.3 defines what the IDE displays and points to theorems for what exists. Entailment of a
nested content (a report or assessment node, or the negation of one, inside another node) is stated only on the
holder-applied signed atom the node elaborates to, at the node's own holder or evidence context and with the
node's polarity, never on the holder-free key: the five nested-content theorems of 9.2 and the fixtures B₇, B₉
to B₁₂′ and `D_ω`.

**Fragments.** Every "exactly when", "↔", "never", "only" and "no …" claim in this specification is a claim over
the fragment of report documents named beside it; where none is named, it is over every well-formed report
document (4.1) and is a definition or a design rule, not a theorem. Every entailment and independence claim of
2.3, 4.5 and 5.3 is over the report premises `Γ_reports(D)` alone: the author's premises `Γ_author` and the
literals may entail what the report premises do not (B₈). The fragments that recur: a positive document (no
negated unit), or an `Expandable` structure (4.4); a key that no top-level unit asserts or denies (9.2); a content
that is a formula over `E`, not a nested report or assessment node, whose elaboration is a signed generated atom
at the node's own holder or evidence context, covered by the nested-content theorems of 9.2 and by nothing else in
this list (B₁, B₇, B₉ to B₁₂′, `D_ω`); a content that the forced holder disequalities do not
entail (4.5); a consistent premise set; for a digest or key-distinctness claim, a document that digests both
objects, each occurring in it (`Occurs`, `OccursComplement`, 9.1; B₁₄ to B₁₆); and, for the premise-subset
device, a document with no `says` key (10.1).
Section 10.3 gives one fixture at the boundary of each restricted claim and, for each nested-content theorem, for
`nested_independent` and for each digest theorem, fixtures that break exactly one of its hypotheses, the
hypothesis named in the table that closes 10.3.

Out of scope, by the plan: promising, pledging, denying, expecting, reaffirming and determination (distinct
reviewed acts, pending); modal inference of any kind and the candidate possible-worlds profile (plan page 2);
numerical probability; de re and cross-boundary bindings; adoption and import beyond their typed provenance
(5.4); composition with active `norms@0`, `definitions@0` or `data@0` layers (11.3); Boolean combinations of
report statements other than negation (`and`, `or`, quantifiers over reports: no wording row, 2.1, 4.3); the
coverage counting protocol
(plan page 4, items 4 and 5); the surface registrations (item 4) and W8 hooks beyond the wordings fixed in
section 2; every pilot gain.

## 1. What a report document is

A report document is a `ve-document@1` document (document.md) whose environment enables `reports@0`, whose
front matter declares contexts, assessments, bridges and scoped checks, and whose units of the frozen W2 kinds
`attributed(agent, act, kind)` and `hedged(modality, kind)` may carry `report` or `assessment` content. Everything
W2 requires still holds (spans partition the source; kinds nest; open terms are declared); the reports checks come
on top (4.1).

### 1.1 Contents, occurrences and keys

```text
content        a closed, typed formula over the author's environment E
               | a quoted W1 norm block with a pinned local environment E_q (no active layer)
               | a quoted W3 definition package with a pinned local environment E_q (no outer effect), with an
                 optional statement: one closed formula over E_q made under those definitions
               | a report node: holder, act, context, content, optional literal words
               | an assessment node: judgment, assessment record, content
               | a negated node: the negation of one report node or one assessment node (never of a formula,
                 whose negation is inside the formula; never of a negated node)
statement      what a top-level unit carries: a report node, an assessment node or a negated node. The grammar
               of statements is  Stmt ::= formula φ | report h act c Stmt lit | assess j a Stmt | not (report | assess)
               with formula, norm and definition nodes as leaves; `not` is the only connective over report
               statements in this slice (4.3)
content id     sha256 of the canonical content object (3.4): structural identity under the declared
               canonicalisation (P5 normalisation of formulas; canonical W1 and W3 blocks; nested objects inline;
               literal words when present; reading choices when the content was chosen from a set). Never equality
               of truth values, never logical equivalence. The objects one document digests are the content
               object of every node and the complement object of every report node (4.1 step 4); two distinct
               ones with one digest are rejected (`HashCollision`), so for two objects one document digests,
               identity of digests is identity of canonical objects (`no_collision`, `no_collision_complement`,
               9.2). The check inspects no object the document does not digest (B₁₄).
occurrence     one report or assessment unit: the document's source id, the unit's byte span, the context it
               names. Repeated occurrences may share a content id and a key; each keeps its own span.
complement id  the content id of a report node's body together with its literal words when present (3.4): what
               the holder said, believed, wanted or intended, as content
key            report:      (act, holder sort, context id, complement id)
               assessment:  (judgment, assessment id, content id of the body)
               finite (bounded depth and count, 11.1) and acyclic (content ids are hashes of finite trees, and a
               node's content is a strict subtree, 4.1 step 4). A negated node has no key of its own: it
               constrains the key of its operand (negatively when top-level; not at all when nested, 4.2)
```

Literal quotation binds the exact words into the content id; a paraphrase claims no word identity. The two are
different canonical complement objects and, in a document that digests both, different complement ids and so
different keys (`literal_paraphrase_distinct` under its occurrence hypotheses, 9.2; B₁₄′, with B₁₄ at the
boundary); neither entails the other (13.6; the reading of `all_truth_combinations`
with `ks` the two keys under its hypotheses: neither key in `topKeys D`, `S₀` admissible, `Expandable D S₀`, 9.2).

### 1.2 Holders, acts and contexts

```text
holders         constants of a declared holder sort (environment block, 3.1): "anthropic", "the_article",
                "the_fed"; a report with no named holder (a passive "has been proclaimed") is not a report unit
act             ∈ {says, believes, wants, intends}      exactly these four under reports@0
context c       a declared record: id, tense ∈ {present, past, perfect}, optional reference-time tag (an opaque
                token; no temporal arithmetic, no inference between tenses), English description
                tense is part of the key: "believed" and "believes" are different predicates
```

Every other act named by a W2 kind (`promised`, `expects`, `denies`) or by a source (pledged, reaffirmed, is
determined to, plans, hopes, predicts, claims, argues) is admitted only as W2 metadata (a LABELLED kind with no
content) or as `unformalised(act_unreviewed)`; a `report` block naming it is `UnsupportedAct` (8). Nothing is
silently renamed: a pledge is not an intention, a denial is not a negated belief.

### 1.3 Complement forms

| Form | Admitted as | Embedded subject |
|---|---|---|
| finite "that"-clause: `says that S`, `believes that S` | closed content `S` | as written in `S` |
| finite "that"-clause over a denied report: `says that it is not the case that <Holder2> believes that S` | closed content: a negated node over the inner report (or assessment) | as written in `S` |
| object-controlled infinitival: `wants X to VP` | closed content "X VP" | `X` (a resolved name) |
| subject-controlled infinitival: `wants to VP`, `intends to VP` | closed content "holder VP" | the holder |
| noun-phrase object: `reaffirmed their faith in fundamental human rights`, `has pledged themselves to the promotion of …` | not a complement: `unformalised(noun_complement)` | none |
| clause with a variable bound outside the quote: "every model is such that Anthropic believes it is safe" | rejected in this slice: `OpenComplement` (de re) | none |
| adverbial fragment as the whole content: S14's "clearly and at sufficient speed" | not a complement: `unformalised(fragment_complement)` | none |

The embedded subject is resolved per template and per the declared names; "it", "they", "themselves" do not cross
the quote boundary (plan page 2). The complement's own tense is whatever its content's vocabulary says ("{0} was
helpful" and "{0} is helpful" are two declared predicates); the first slice relates the outer tense (in `c`) and
the complement's tense in no way.

### 1.4 Open assessments and their records

```text
judgment        ∈ {may, probably}
assessment a    a declared record (3.2): id; evidence context (a constant of the declared evidence sort);
                decided_by (a token; the explicit value `unresolved_decider` when the source names no assessor;
                never absent); necessary and sufficient criteria (closed formulas over E, possibly empty);
                factors; precedents; jurisdiction; version  — W2's complete open-term record
May(a, q)       "according to assessment a, q may be so": a fresh unary predicate on the evidence sort, keyed by
                (may, a, content id of q), applied to a's evidence context
Probably(a, q)  likewise for "probably"
```

`May(a, q)` and `Probably(a, q)` are open: no rule of the checker decides them, relates them to each other or to
`q`, or reads a threshold, a percentage or an accessibility relation (what a document's own report premises
entail is the theorem statements of 9.2 and 9.3; 5.3 points to them). `May(a, ¬q)`, `¬May(a, q)`,
`Probably(a, ¬q)` and `¬Probably(a, q)` are four different formulas (2.1). Admission checks the structured content
`q`, the record's shape and that its criteria are closed formulas over `E`; it does not establish evidential
possibility or likelihood. The modal profile sketched on plan page 2 is not this profile.

### 1.5 The extended vocabulary `E_reports` and generated names

`E_reports = E + {one unary predicate per key}`, regenerated at every site from `E` and the decoded document,
never taken from the wire. Every generated predicate is a base predicate (not regulated, not defined, no data
flag) with arbitrary interpretation. Names are identifiers of the existing grammar, at most 64 bytes, injective
over the keys of the document (`names_injective_on_keys`, 9.2: two distinct keys of `D` have two names, a name
being the key's position among the keys of its act; that two report nodes of `D` with distinct canonical
complement objects are two keys is the document-local collision check of 4.1 step 4, `no_collision_complement`)
and regenerable without a table:

```text
key order          report keys sorted by (act, holder sort, context id, content id); assessment keys sorted by
                   (judgment, assessment id, content id); k is the 1-based position of the key among the keys
                   with the same act (or the same judgment), in that order
reports__<act>__<k>        the report predicate of the k-th key of that act, on the key's holder sort
reports__<judgment>__<k>   the assessment predicate of the k-th key of that judgment, on the evidence sort
```

Under `reports@0` an author predicate beginning with `reports__` is rejected (`InvalidInput: author predicate <p>
begins with reports__`), so generated and author names never collide. The names are ordinal: a generated
predicate carries only its name and argument sort, so a change that leaves the key order and count intact (a
context's tense, a payload of the sole key) leaves `E_reports` and `Γ_reports` byte-identical. That is why a
certificate is bound to the document envelope and not only to `E_reports` (3.4). Adding a report renumbers. Every
report and residual line renders the source key beside the generated name (`reports__believes__2` as "believes,
organisation, context c2 (past), content ‹Claude was helpful›"); `J_{act,c,q}(h)` and `May(a, q)` in this
specification are that rendering.

### 1.6 What reports@0 adds to a document, in one table

| Object | Where | Effect on the checked premise set `Γ` |
|---|---|---|
| report unit | a unit with `report` content | one atom `J_{act,c,q}(h)`, labelled `report:<unit>` |
| assessment unit | a unit with `assessment` content | one atom `May(a,q)` or `Probably(a,q)`, labelled `assessment:<unit>`; one open term in the residual |
| negated unit | a unit with `negated` content | the negation of its operand's atom, `¬J_{act,c,q}(h)` or `¬May(a,q)`, labelled as the operand (`report:<unit>` or `assessment:<unit>`): that one signed entry in `Γ_reports(D)` and no other; for old-language consequences it adds exactly the holder disequalities of `neqs` (`reports_no_leak`, 4.4) |
| nested content | inside a report, assessment or negated node | nothing through the node that contains it: it is content, and a bridge is needed to use any part of it; what a top-level unit that carries the same node, its negation, or the same key at another holder entails about the node's own signed atom is the nested-content theorems of 9.2 (B₁, B₇, B₉ to B₁₂′, `D_ω`) |
| scoped check | front matter `scoped` | nothing: a report about the contents, computed in the content's environment with that environment's own background (5.1) |
| bridge | a graph leaf `bridge:accepts(<holder>,<unit>)` (root, legacy) or `bridge:accepts_at(<holder>,<unit>,<path>)` (nested, with a record) | exactly the elaborated formula at the path, as a labelled assumption |
| quoted norm block or definition package | content | nothing: a local check only; no layer, no `background:definitions` premise outside; a package's statement is a payload for scoped checks over `E_q` only |

## 2. The English (one reading each; rejected as today when `reports@0` is off)

### 2.1 Wordings

Names are declared holder constants rendered by the environment legend; contexts are chosen from the declared
records and shown in the inspector; the verb form carries the context's tense. `S` is any sentence the reports
surface admits as content (a formula sentence of the existing grammar, or a nested report or assessment wording).
The paraphrase column is the display text the IDE shows for one wording (2.3), a definition: it states what that
wording claims and leaves unclaimed in the semantics of 4.2, not what a whole document entails. Another unit may
carry what a wording leaves open (B₁, B₃, B₇, B₉ to B₁₂′), and what a premise set entails is the theorem
statements of 9.2 and 9.3 (4.5 reads them).

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `<Holder> says that S.` / `<Holder> said that S.` | <Holder> says (in context c) that S; whether S is true is not claimed; nothing about what <Holder> believes follows. | `J_{says,c,q}(h)`, `c` present / past |
| `<Holder> believes that S.` / `believed that S.` | <Holder> believes (in c) that S; whether S is true is not claimed; no other belief follows, not even a consequence of S. | `J_{believes,c,q}(h)` |
| `<Holder> wants <Name> to <VP>.` | <Holder> wants it to be the case that <Name> <VP>; no duty on anyone and no fact about <Name> follows. | `J_{wants,c,q}(h)`, `q` = "<Name> <VP>" |
| `<Holder> wants to <VP>.` | as above with <Holder> as the embedded subject. | `q` = "<Holder> <VP>" |
| `<Holder> intends to <VP>.` / `intended to <VP>.` | <Holder> intends (in c) to <VP>; neither that <Holder> <VP>, nor an obligation, nor a promise follows. | `J_{intends,c,q}(h)`, `q` = "<Holder> <VP>" |
| `<Holder> believes that it is not the case that S.` | the negation is inside the belief. | `J_{believes,c,¬q}(h)` |
| `It is not the case that <Holder> believes that S.` | the negation is outside: no claim that <Holder> believes the opposite. | `¬J_{believes,c,q}(h)` |
| `<Holder> says that <Holder2> believes that S.` | two attribution scopes: <Holder> says it; that <Holder2> believes S is not claimed; S is not claimed. | `J_{says,c,⟨believes,c′,q⟩}(h)`; `c′` from the inner verb |
| `<Holder> says that it is not the case that <Holder2> believes that S.` (likewise with an assessment wording in place of the inner report) | the negation is inside the outer report and outside the inner one: <Holder> says that <Holder2> does not believe S; neither that <Holder2> lacks the belief nor anything about S is claimed. | `J_{says,c,⟨¬⟨believes,c′,q⟩⟩}(h)`: the complement is a negated node |
| `<Holder> says, "W".` (literal) | <Holder> said exactly the words W, whose content is S (shown); the words are bound. | `J_{says,c,q_W}(h)`, `q_W` binds `W` |
| `According to the stated assessment, it may be that S.` | The assessment on record for this unit (criteria …, decided by …) holds that S may be so; the checker establishes neither that S is possible nor that it is likely. | `May(a, q)` |
| `According to the stated assessment, it is probably the case that S.` | likewise, "probably". | `Probably(a, q)` |
| `According to the stated assessment, <Subject> may <VP>.` / `… <Subject> is probably <Adj>.` | the rendered form of the two rows above when S is one positive atomic sentence; same reading. | same |
| `According to the stated assessment, it may be that it is not the case that S.` | the negation is inside the assessment. | `May(a, ¬q)` |
| `It is not the case that, according to the stated assessment, it may be that S.` | the negation is outside. | `¬May(a, q)` |
| `Context c: <description>; tense <tense>[; reference time <tag>].` (inspector legend) | Names the context the verb form refers to; the tag is a label, not a date. | context record |
| `For this argument, <reviewer> accepts as true what <Holder> says in <unit>: S.` (rendering of a bridge leaf) | S is assumed for this argument on <reviewer>'s responsibility, with occurrence, content identity, environment, choices and reason recorded; nothing else in <unit> is assumed. | `bridge:accepts(h, u)` (root, legacy label) |
| `For this argument, <reviewer> accepts as true what <Holder2> believes according to <Holder> in <unit>: S.` | the nested payload is assumed; that <Holder2> believes it is not. | `bridge:accepts_at(h2, u, 1)` (nested label with its record) |
| `S follows from the reported contents <paths>.` (report line, never writable) | Under the payloads' own environment `E_q` and its background (the literals; a quoted package's definition premises, 5.1, fixtures λ and B₅), S is a consequence of the selected contents and of no other unit of the document; nothing about the outer document or the holder's beliefs follows. | scoped check FOLLOWS |

The act is fixed by the verb: `says`, `believes`, `wants`, `intends` and their past forms. `may` and `probably`
are assessment words only inside the `According to the stated assessment` template; the parser binds "the stated
assessment" to the unit's assessment record, never to a holder, and no holder may display as "the stated
assessment" (`InvalidInput: holder verbalisation reserved`). `may not` and `probably not` are rejected with the two
rewrites (negation inside, negation outside). W1's `Every <noun> may <act>` is a rule block (norms.md 2.1) and is
not a reports wording; the all-derivations gate rejects any input that derives both.

`It is not the case that <R>`, with `<R>` a report or assessment wording, is the only Boolean wording over report
statements, and it may appear wherever `S` may (top level, or as a complement). `and`, `or` and `every` over
report wordings ("Anthropic believes that S and the article says that S", "every organisation believes that S")
have no wording row: they are rejected with the rewrite into separate units (for `and`) or as `OpenComplement` (a
binder over holders), and they enter this table the day a wording row with one reading is added. Negation of a
formula stays inside the formula (row 6), so no wording of this table has two encodings by construction; that no
admitted sentence has two derivations is what the all-derivations gate enforces at parse time, and the theorem
(`reports_parse_unique`, P1) is item 4's, not this draft's (9.5).

### 2.2 Synonyms and non-synonyms

Input synonyms rendered canonically: `states that` → `says that`; `stated that` → `said that`; `it is likely
that` → `it is probably the case that`, inside the assessment template only. Nothing else.

Not synonyms, each rejected with the reason shown: `thinks that` (belief or opinion; not admitted), `claims that`,
`argues that`, `denies that` (acts pending review), `plans to`, `hopes to`, `expects to`, `predicts that`
(promise/prediction/intention are never identified), `should` (desire and duty are never synonyms; a `should`
unit is W1's or soft-norms' business), `could`, `might`, `possibly` (not the assessment template; a hedged W2
kind at most), `According to <Holder>, S` (W2's rendering of a LABELLED attributed unit, not a reports sentence).
In translation, a force or act word the source uses loosely ("has determined to", "pledged themselves to") is a
READINGS set only when each reading is an admitted act; otherwise the unit stays UNFORMALISED with the reason
named.

### 2.3 The reader's checklist (norms.md 2.5, extended)

For every positive report unit the IDE shows, in English only: the paraphrase of 2.1; "claimed: that <Holder>
<act> …; not claimed: <S>; not claimed: any other belief or statement of <Holder>"; the **situation line**: one
situation in which every report of the document holds and S is false, that is, a source model of the report
premises `Γ_reports(D)` (4.2; the author's premises `Γ_author` and the literals are not part of it, and may entail
S when the report premises do not, B₈). The situation line is defined by what the IDE runs, not by a claim about
when a situation exists: it submits `Γ_reports(D) ⊢ elab(S)` to the finite-model search over `E_reports` within
the existing budget and, when a countermodel is found, decodes it to a source model and shows that
(`reports_route_countermodel` with `Γ = []`, `finite_witness_decodes`); when a certificate for
`Γ_reports(D) ⊢ elab(S)` replays, the line says that there is none, beside the certificate; otherwise the line
says UNKNOWN with the budget. Which of the three a document produces is the business of the theorem statements of
9.2 and of the fixtures, not of this paragraph: for a formula content over `E`, `reports_no_leak` with `Γ = []`
and `R = Γ_reports(D)` (B₄, B₆, B₈); for a nested report or assessment wording, whose elaboration is a signed
generated atom at the nested node's own holder, the nested-content theorems of 9.2 (`nested_positive_entailed`,
B₁, B₇, B₁₂′; `holder_atom_free`, B₉′; `unreported_key_free`, `D_ζ`, B₁₂; `nested_positive_refuted`, B₁₀; for a
negated nested wording, `nested_negated_entailed`, B₁₁, `nested_negated_refuted`, `D_ω`, and
`all_truth_combinations`, B₁₁′). For a belief in P
and a Q, the **belief line**: one situation in which <Holder> believes P and believes that P implies Q and does
not believe Q, run and displayed the same way for the conclusion `J_{believes,c,Q}(h)`; the theorems that supply
a situation are `no_closure_under_consequence` under its hypotheses (`beliefsIn D hd c P (P → Q)`,
`holderSort D hd = some s`, the belief-in-Q key `∉ topKeys D`, `S₀` admissible, `Expandable D S₀`; `D_β`),
`holder_atom_free` and `all_truth_combinations`; B₃ is the case in which a certificate replays. For a nested
report, which bridge
would assume which sentence; for an intention, one situation in which the act never happens and nothing is
required, run and displayed as the situation line; for a literal quotation, the exact words beside the
content. For every negated unit: the paraphrase of 2.1's outside-negation row and the denied status line of 7.2
(the content is not claimed and neither is its negation); no situation line. For every assessment unit: the
record's criteria, factors and decider (or "the source names no
assessor; recorded as unresolved"), and the sentence "admission checks the assessment's content and criteria; it
establishes neither possibility nor likelihood". For every scoped check: the payloads by occurrence, and the
sentence "this is a consequence among the reported contents, not a claim of the document". For every bridge: the
exact target, the reviewer, the reason units, and "assumed, not proved".

### 2.4 The round-trip contract

An exact round trip preserves the sentence **together with** its manifest: the environment (W2's environment-bound
`meaning_id` of every content formula, extended by 3.4 to the report object), the context records the verbs refer
to, the assessment records, the profile list and versions, and the reading choices under which the contents were
selected. Typed text and rendered text pass through one grammar; `print(parse(s)) = s` on canonical text and
`parse(print(A)) = A` (P4) hold for the report object with its manifest, not for the sentence string alone. Bare
sentence text is not a unit: rendering a sentence under a different environment, context table, assessment record
or choice map is `ManifestMismatch`, never a silent recovery through defaults. Technical identifiers stay in the
inspector; the manifest travels with the sentence. Explicit-form fallback is a visible repair, not a passed
English gate (natural-view.md).

### 2.5 Examples from the four pinned sources

Sources pinned for item 1: the Claude constitution (`manage-agents/pilots/claude-constitution/source/
claude-constitution.md`, SHA-256 `fa10ed48…50dd`, run `run-20260927T1800Z`), the Universal Declaration
(`manage-agents/pilots/udhr/source/udhr.md`, SHA-256 `d6495201…d3a`, same run), the Reuters article
(`usecases/news-article/source.md`, coverage rows cited `row n`) and the BlueDot grant README
(`ve-bluedot/usecases/bluedot-grant/README.md`, external commit `fbe0337`). Every translator's choice is an
attributed unit, never the source's content (VISION.md 3).

```text
constitution u0007.s01   "Anthropic wants Claude to be genuinely helpful to the people it works with or on behalf
                         of, as well as to society, while avoiding actions that are unsafe, unethical, or
                         deceptive."
                         wrapper: Anthropic wants Claude to <VP>   (object-controlled infinitival; Claude bound)
                         complement: open term genuine_helpfulness (three arguments, decided by unresolved_decider)
                         and a norm-shaped "while avoiding"; not a closed sentence about Claude.
                         Result: MIXED; "Anthropic wants " LABELLED (attributed metadata), the complement
                         UNFORMALISED (norms; open term). 0 B substantive.
constitution u0169.s01   "We believe that hard constraints also serve Claude's interests by providing a stable
                         foundation of identity and values that cannot be eroded through sophisticated
                         argumentation, …"
                         wrapper: <Holder> believes that S with "we" resolved to anthropic by a cited narrowing
                         (the document's author); complement: causal "serve … by providing" and open "cannot be
                         eroded". Result: MIXED; wrapper LABELLED, complement UNFORMALISED (causation). 0 B.
news S7 (row 15)         "Today's policy action will support a timelier return to the Committee's 2% goal," the
                         central bank said in its policy statement.
                         wrapper: The Fed said, "W" (literal; act says; context past; holder the_fed)
                         complement: future time, causal "support", a numeric goal tag: UNFORMALISED. The inert
                         token @statement_timelier is replaced by the literal content object; 0 B substantive.
news S14 (row 24)        "Warsh has pledged to lower inflation back to 2% 'clearly and at sufficient speed'"
                         act pledged: outside the slice (UnsupportedAct as report content; W2 kind absent);
                         content: an adverbial fragment (fragment_complement). Stays OPAQUE/UNFORMALISED until a
                         reviewed pledge act exists.
UDHR u005                "… has been proclaimed as the highest aspiration of the common people": passive with no
                         named holder; act outside the slice; nominal complement.               UNFORMALISED
UDHR u006, u007          "it is essential … that human rights should be protected by the rule of law" / "to
                         promote the development of friendly relations": open term essential (not an assessment
                         word), an embedded norm, a promotion complement.                          UNFORMALISED
UDHR u008a               "reaffirmed their faith in fundamental human rights, …": act outside the slice;
                         noun-phrase object (noun_complement).                                      UNFORMALISED
UDHR u008b               "have determined to promote social progress and better standards of life in larger
                         freedom": act outside the slice; promotion and a vague standard.           UNFORMALISED
UDHR u009                "have pledged themselves to achieve … the promotion of universal respect …": act
                         outside the slice; promotion.                                              UNFORMALISED
BlueDot                  milestones as intentions ("we intend to publish the results"): wrapper reachable when the
                         complement is a closed sentence; "may misstate" is an assessment only with a record;
                         "should help" is neither: READINGS {hope, prediction} pending acts. Gain unknown; the
                         README's totals lack an independent fidelity audit.
```

All six UDHR tagged units and both constitution targets are blocked by this slice: the expected substantive gain
from `reports@0` alone is 0 B on both, inside the tagged bounds (plan page 4). Metadata may be LABELLED; a passage
never loses its residual because its wrapper parsed. The fixtures of section 10 therefore use synthetic
complements that the existing grammar admits.

## 3. Declarations, wire form and identity

### 3.1 The environment `reports` block (identity-bound like `regulated`)

```json
"reports": {"holders": ["organisation", "person", "text"],
            "evidence": "evidence"},
"constants": {"anthropic": {"sort": "organisation", "description": "Anthropic", "verbalisation": "Anthropic"},
              "the_article": {"sort": "text", "verbalisation": "the article"},
              "e1": {"sort": "evidence", "verbalisation": "the stated evidence of 16 September"}}
```

`holders` is a non-empty list of distinct declared sorts (at most 8; `UnknownSymbol: holder sort <s>` otherwise);
`evidence` names one declared sort whose constants are evidence contexts (`UnknownSymbol: evidence sort`). A holder
constant's verbalisation may not be "the stated assessment" (2.1). The block is part of the canonical environment
bytes: `environment_id` changes when it changes and is unchanged for every existing environment (none has the
block). `reports@0` requires `relational-fol@0` and is rejected when the block is absent (`UnsupportedProfile:
reports@0 needs a reports block`).

### 3.2 Front-matter declarations

```json
"contexts": [{"id": "c1", "tense": "present", "reference_time": null, "description": "the constitution as published"},
             {"id": "c2", "tense": "past", "reference_time": "sept16", "description": "the policy statement of 16 September 2026"}],
"assessments": [{"id": "a1", "context": "e1", "decided_by": "unresolved_decider",
                 "necessary": [], "sufficient": [], "factors": ["review status", "incident history"],
                 "precedents": [], "jurisdiction": "news_desk", "version": 1}],
"bridges": [{"id": "b1", "unit": "u7", "path": "1", "accepted_by": "reviewer_ann", "reason": ["u9"]}],
"scoped": [{"id": "s1", "payloads": ["u3", {"unit": "u4", "path": "1"}],
            "conclusion": {"ast": ["unary", "safe", ["const", "service"]]}, "certificate": null}]
```

A path on the wire is a unit id alone (the unit's root complement) or an object `{"unit": <id>, "path": <p>}`
with `p` a dot-separated string of `1`s (`"1"`, `"1.1"`, …; one `1` per descent, 5.2). Unit ids are W2 tokens and
tokens admit dots (`lean/VE/Route/Admission.lean`, `token`), so a unit may itself be named `u7.1`; the explicit
`unit` and `path` fields are what keep a root target and a nested target apart. A bare string never names a nested
node.

`contexts`: distinct token ids (at most 256), `tense` one of the three values, `reference_time` a token or `null`
(no `time@0` dependency: the tag is opaque), `description` at most 200 bytes. `assessments`: distinct ids (at most
256), `context` a constant of the evidence sort, `decided_by` a token (the literal `unresolved_decider` when the
source names none; an absent field is `InvalidInput: assessment <a> needs decided_by`), criteria closed formulas
over `E` (P0 wire form), the other fields as W2's open-term schema (`ve/openterms.py`). `bridges`: a record per
nested target (`unit` and a non-empty `path`); a root target (`path` absent) may have one and needs none
(legacy). `scoped`: payload paths whose contents are formula nodes over one environment (the author's `E`, or the
pinned `E_q` of one quoted package whose statement they are), a closed conclusion over that environment, an
optional certificate (5.1). The four lists are new front-matter keys admitted only under `reports@0`
(`unknown document metadata` otherwise, as today).

### 3.3 Unit content (W2 units of the frozen kinds)

```json
{"id": "u7", "span": [1507, 1560], "kind": ["attributed", "the_article", "says", ["attributed", "anthropic", "believes", "asserted"]],
 "meaning": "specified", "support": "testimony",
 "content": {"report": {"holder": "the_article", "act": "says", "context": "c2", "literal": null,
             "content": {"report": {"holder": "anthropic", "act": "believes", "context": "c1", "literal": null,
                         "content": {"ast": ["unary", "helpful", ["const", "claude"]]}}}}}}

{"id": "u8", "span": [1560, 1610], "kind": ["hedged", "could", "asserted"],
 "meaning": {"open": ["reports__may__1"]}, "support": "testimony",
 "content": {"assessment": {"judgment": "may", "record": "a1", "content": {"ast": ["unary", "safe", ["const", "service"]]}}}}
```

```json
{"id": "u9", "span": [1610, 1660], "kind": ["attributed", "anthropic", "believes", "asserted"],
 "meaning": "specified", "support": "testimony",
 "content": {"negated": {"report": {"holder": "anthropic", "act": "believes", "context": "c1", "literal": null,
                                    "content": {"ast": ["unary", "human", ["const", "claude"]]}}}}}
```

Content forms: `{"ast": …}` or `{"fence": "<id>"}` with `surface` (a closed formula over `E`, admitted through
the existing all-derivations parser and bound by `meaning_id`); `{"norm": {"environment": {…}, "norms": […]}}` and
`{"definition": {"environment": {…}, "content": {"ast": …} | null}}` (a pinned local environment `E_q` inline with
its own `environment_id`, validated by the unchanged W1 and W3 validators, contributing no layer and no Background
premise outside; a definition package's optional `content` is one closed formula over `E_q`, the statement the
source makes under those definitions, reachable by path for scoped checks over `E_q` and for nothing else);
`{"report": …}`, `{"assessment": …}` and `{"negated": <report | assessment>}` recursively (`negated` wraps exactly
one report or assessment node: `InvalidInput: negated operand in <unit>` for a formula, a quoted block or a
negated node). A top-level unit's content is a report node, an assessment node or a negated node (`InvalidInput:
invalid content for <unit>` otherwise). The W2 `kind` must agree with the content tree: `attributed(<holder>,
<act>, k)` for a report node and `hedged(could, k)` / `hedged(likely, k)` for `may` / `probably`
(`KindMismatch` otherwise); a negated node is transparent to kinds (W2 kinds carry no polarity: the kind of
`{"negated": n}` is the kind of `n`, so u9 above keeps `attributed(anthropic, believes, asserted)`). Under
`reports@0` the kind decoder accepts the act `wants` (13.2), and the frozen decoder outside the profile is
unchanged. A unit of kind `attributed` or `hedged` with no `report`, `assessment` or `negated` content is what it
is today: LABELLED metadata, whatever act its kind names (4.1 step 2 checks acts only on units with report
content). The `meaning` of a report unit is `specified` when every formula node is closed over declared
vocabulary, `{"open": [...]}` when a content or an assessment introduces open terms; an assessment unit always
lists its generated open term. `support` is the author's, as today (`testimony` for the pilots).

### 3.4 Identity

```text
content_id(x)  := sha256("ve-content-<identity_version>\n" + canonical(object(x)))
  object(formula)     = {"environment_id", "ast"}                     (W2's meaning_id input, so a formula content's
                                                                       content_id equals its meaning_id domain-shifted;
                                                                       the id is that of the environment the formula is
                                                                       over: E, or E_q for a package's statement, which
                                                                       is canonicalised inside its definition node)
  object(norm)        = {"environment_id": E_q's, "norms": canonical W1 blocks}
  object(definition)  = {"environment_id": E_q's, "content": object(statement) | null}
  object(complement)  = {"content": object(inner), "literal"}                    its hash is the complement id
  object(report)      = {"holder", "act", "context": the context record, "complement": object(complement)}
  object(assessment)  = {"judgment", "record": the assessment record, "content": object(inner)}
  object(negated)     = {"negated": object(inner)}
  plus "choices": the reading-set choices (set@version:choice) under which any content node was selected, when any
meaning_id(u)  := sha256("ve-meaning-<identity_version>\n" + canonical({"environment_id", "ast": object(u.content)}))
                  for a report, assessment or negated unit, over the author's environment_id
document_id(D) := sha256("ve-reports-<identity_version>\n" + canonical({"environment_id": environment_id(E),
                  "document": the canonical array of unit objects (with their content objects and choices),
                  contexts, assessments, bridges and scoped checks in document order}))
```

Identity is the canonical object; the digest is its name. The objects a document digests are the content object
`object(x)` of every node `x` of every tree and the complement object of every report node; two distinct ones
with one digest are rejected (`HashCollision: <digest>`, 4.1 step 4), and the check compares those objects and
no other. So every identity theorem of 9.2 and 9.3 is stated on canonical objects and transfers to digests only
for objects a well-formed document digests, under an explicit occurrence hypothesis for each (`no_collision`,
`no_collision_complement`, `content_structural`, `negation_scopes_distinct`, `literal_paraphrase_distinct`,
`probably_not_scopes_distinct`); nothing is stated about the digest of an object the document does not digest
(B₁₄ to B₁₆), and no theorem asserts SHA-256 injectivity.

`E_reports`, its generated names, the open-term records of the assessments, `Γ_reports` and every bridge formula
are regenerated from these at every site. A certificate has two bindings, both recomputed from the raw source at
replay and never read from the wire. The inner binding is P0's: the regenerated `E_reports`
(`environment_id(E_reports)`), the ordered premise list `Background(E_reports) ++ Γ_reports ++ Γ` and the
conclusion by meaning id (P0 3.9). The outer binding is the reports envelope, `{"environment_id": environment_id(E),
"document_id": document_id(D)}`, checked exactly as `VE.Norms.Replay.outerBound` checks the norms envelope
(`environment_id`, `document_hash`, target); a certificate whose envelope differs from the recomputed one is not
`valid`, whatever its inner binding says. The inner binding alone is not enough: generated predicates are ordinal
(1.5), so changing the sole context's tense, or the sole payload, can leave `E_reports` and every elaborated
premise byte-identical while `document_id(D)` changes. With both bindings, changing a holder, an act, a context's
tense or tag, a content node, the literal words, a reading choice, an assessment record or the environment
changes `document_id(D)` as a canonical object and so, absent a digest collision that no theorem excludes (9.5),
invalidates every certificate of the document (fixture φ).

### 3.5 Strict text

There is no strict text for report units beyond W2's: the wire form is the JSON of 3.3 and the English of 2.1 is
the writable form; `{"fence": …}` content inside a report node is parsed by the existing strict or English parser
as today. Contexts, assessments, bridges and scoped checks are front matter only.

## 4. Semantics and elaboration

### 4.1 Well-formedness (`WellFormedReports`)

A report document `D = (E, contexts, assessments, units, bridges, scoped)` is well-formed when, in this order:

1. The reports gate passes (9.4): `reports@0` is in the profile list, the frozen `VE.Route.Gate.classify` on the
   list minus `reports@0` returns `.fol` (so `relational-fol@0` is present and no `closure@0`, `nary@0` or
   `order@0`), and none of `norms@0`, `definitions@0`, `data@0` is present (`UnsupportedProfile: reports@0 with
   <profile> layers`, 11.3); the `reports` block decodes (3.1); no author predicate begins with `reports__`; no
   holder verbalisation is "the stated assessment".
2. Every W2 check passes (spans, kinds, open terms, reading sets); for every unit that carries `report` content
   (directly or under `negated`), the act named by its `attributed` kind is in the profile's act list. A unit
   whose kind names another act and carries no report content is LABELLED metadata (3.3, fixture σ).
3. Contexts and assessments decode (3.2); every assessment's criteria are closed and typed over `E`; every
   `decided_by` is a token.
4. Every content tree decodes: depth at most 16 (`Content.depth`, 9.1: a leaf counts one, a report or assessment
   node one more than its body, a negated node nothing, so a unit's content depth is the depth of its W2 kind;
   `ResourceLimit: content depth` is the content decoder's own bound, and a unit whose kind exceeds 16 is
   already rejected at step 2 by W2's `ResourceLimit: kind depth exceeds 16`, B₁₃′), each formula node closed and
   typed over `E` (or over its pinned `E_q` for the statement of a definition node and for the rules of a norm
   node, which are validated by the unchanged W1 and W3 validators without composing any layer), each report
   node's holder a constant of a holder sort (`UnknownHolder`, `HolderSort`), its act in the list
   (`UnsupportedAct`), its context declared (`UnknownContext`), each assessment node's record declared
   (`UnknownAssessment`), each negated node's operand a report or assessment node (`InvalidInput: negated operand
   in <unit>`), each top-level content a report, assessment or negated node (`InvalidInput: invalid content for
   <unit>`); the W2 kind matches the tree (`KindMismatch`); the content graph is acyclic by construction and the
   digest table computed from the decoded trees, which holds the content id of every node of every tree and the
   complement id of every report node (3.4) and nothing else, has no forward reference (`DependencyCycle: <sorted
   content ids>` through the shared `dependencyOrder`, reachable only from a malformed wire) and no two distinct
   canonical objects with one digest (`HashCollision: <digest>`; the check compares the objects the table holds
   and inspects no other, `no_collision`, `no_collision_complement`, B₁₄).
5. Every scoped check's payload paths resolve to formula nodes over one environment (`envAt`, 5.2, equal for all
   payloads: `ScopedEnvironment`; a path that is not a formula node: `ScopedTarget`); its conclusion is closed
   over that environment; payload count at most 64.
6. Every bridge record's target path resolves (`BridgeTarget`), names a formula or report node over the author's
   `E` (`BridgeKindMismatch` for a norm or definition node and for any node under a pinned `E_q`, such as a
   definition package's statement), and every nested bridge label (`bridge:accepts_at`) in the graph has a record
   (`MissingBridgeRecord`).
7. `E_reports` is a valid environment (identifier lengths, predicate count within `MAX_PREDICATES`;
   `ResourceLimit` otherwise).

### 4.2 The independent semantics: a source model `(S, J, A)`

```text
S     an admissible structure over E (the author's environment; holders and evidence contexts are constants)
J     act → holder sort → context id → complement id → element → Prop     arbitrary, typed: J act s c q v → S.domain s v
A     judgment → assessment id → content id → element → Prop              arbitrary, typed: A j a q v → S.domain evidence v
```

`J` is indexed by the complete report key (act, holder sort, context id, complement id) and `A` by the complete
assessment key, and each is typed: it holds only of elements of the key's sort (the holder sort; the evidence
sort). Sort domains may overlap in a `VE.Structure` (`Semantics.lean`), so two keys that differ only in the sort
are two relations, never merged. Beyond typing, `J` and `A` have no closure conditions: no factivity, no
consistency, no closure under consequence, no link between tenses, between acts, between `may` and `probably`, or
between literal and paraphrased contents. The **intended meaning** of a document is satisfaction of every
top-level statement, defined by recursion on the statement grammar of 1.1:

```text
Sat_M (report h act c body lit) := ∀ v, S.constant h = some v → J act (sort h) c (complement_id body lit) v
Sat_M (assess j a body)         := ∀ v, S.constant (record a).context = some v → A j a (content_id body) v
Sat_M (not n)                   := ¬ Sat_M n
IntendedReports D M             := ∀ top-level unit u of D, Sat_M u.content
```

Only the document's top-level statements are asserted; a nested node, negated or not, is content: `J` is indexed
by the content id, so the recursion never descends into a complement, and nested nodes constrain nothing through
the node that contains them (what a top-level unit that carries the same node, its negation, or the same key at
another holder entails about the nested node's own signed atom is the nested-content theorems of 9.2: B₁, B₇,
B₉ to B₁₂′, `D_ω`). A negated top-level unit's clause is `¬ Sat_M n`: the denial of its operand's atom at its
operand's holder, and no other clause. The single theorem
behind non-factivity, non-closure, nested independence and harmless inconsistent quotation is
`source_over_any_structure` (9.2): every admissible `S` extends to a source model of `D`, unconditionally when
every top-level unit is positive, and, when some unit is negated, exactly when `S` satisfies the holder
disequalities `neqs (Γ_reports D)` that the signed premises force (4.4).

### 4.3 Elaboration

```text
elab(formula E φ)                 = φ
elab(report h act c body lit)     = J_{act, sort(h), c, complement_id(body, lit)}(h)   an atom over E_reports
elab(assessment j a body)         = A_{j, a, content_id(body)}(context(a))              an atom over E_reports
elab(not n)                       = ¬ elab(n)                                            a negated atom
elab(norm …) = elab(definition …) = none                                                 no formula; local checks only
Γ_reports(D) := [elab(u.content) : u a top-level unit of D, in document order]           signed generated atoms
```

`elab` is total on formula, report, assessment and negated nodes and every formula it produces is well-formed
over `E_reports` (`premises_wellFormed`). Because a top-level unit is one wording of 2.1, every entry of
`Γ_reports(D)` is a signed literal, a generated atom or its negation, never an arbitrary Boolean formula. The
negation is the existing FOL `not`; no truth predicate, dynamic quotation or proof rule is added. Other Boolean
combinations of report statements (`and`, `or`, quantification over holders) are deferred: they have no wording
(2.1), no wire form (3.3) and no `elab` case, and adding one is a change to this specification, not an
implementation choice.

Interpretation and restriction, the two directions of the typed model correspondence:

```text
interp (S, J, A)   the structure over E_reports that agrees with S on E and interprets
                     J_{act,s,c,q} by {v | J act s c q v}   and   A_{j,a,q} by {v | A j a q v}
                   (admissible over E_reports because J and A are typed)
restrictJ S′       the source model (forget (names D) S′, J, A) with
                     J act s c q v := ⟨act,s,c,q⟩ ∈ keys D ∧ S′.domain s v ∧ S′.relation (name of the key) [v]
                     A j a q v     := ⟨j,a,q⟩ ∈ akeys D ∧ S′.domain evidence v ∧ S′.relation (name of the key) [v]
                   (the domain guards discharge the typing fields for every S′; forget keeps domains and constants)
```

`reports_elaboration_faithful` (9.2): `Sat (interp M) Γ_reports(D) ↔ IntendedReports D M` for every source model
`M`, and `Sat S′ Γ_reports(D) ↔ IntendedReports D (restrictJ S′)` for every admissible `S′` over `E_reports`;
`restrictJ ∘ interp` is the identity on the keys of `D` and `interp ∘ restrictJ` is the identity on the relations
of an admissible `S′`; old formulas keep their truth value across `interp`; every valid finite model over
`E_reports` decodes to a source model. This is truth preservation with typed model correspondence in both
directions and finite witness decoding, and it is stated at every universe.

### 4.4 The route instance and conservativity

The reports gate (4.1 step 1, 9.4) admits exactly the FOL family under `reports@0`: no `norms@0`, `definitions@0`
or `data@0` layer is present (11.3). The route is then

```text
reportsRoute D := folLayer (envReports D) D.lits          P0's FOL route at E_reports, which is by definition
                                                          Layer.id (envReports D) (StringAdmissible (envReports D) D.lits) _
premises        [] ; Γ := Γ_reports(D) ++ Γ_author       (document premises: the signed report atoms, then the author's)
background      literals D.lits                           (the literal distinctness premises of the FOL family)
```

`Layer.id`'s `Intended` is `True`: it says that the empty layer means nothing, and it is not the meaning of a
report; the meaning is `IntendedReports` through `reports_elaboration_faithful`, which composes with
`route_acceptance` (`reports_route_acceptance`, 9.3) and with finite countermodel decoding
(`reports_route_countermodel`). Existing deterministic layers keep their own contracts.

`reports_old_language_conservative` (9.2) is a statement about the vocabulary: for `Γ` and `φ` over the old
language `E`, `Entails E_reports Γ φ ↔ Entails E Γ φ`. The proof is existence of expansion (every admissible
`E`-structure expands to an admissible `E_reports`-structure, the fresh relations empty) plus restriction;
uniqueness is neither claimed nor true, because the fresh relations are arbitrary.

Removing the report premises themselves is a different statement, because P0 has `Formula.eq` and no
distinct-name assumption: the signed atoms `R(a)` and `¬R(b)` together entail the old-language formula
`¬(a = b)`. For a list `R` of signed generated atoms define

```text
neqs R := [¬(h = h′) : P(h) ∈ R, ¬P(h′) ∈ R]          the holder disequalities R forces, in R's order
```

Then `reports_no_leak` (9.2): `Entails E_reports (Γ ++ R) φ ↔ Entails E (Γ ++ neqs R) φ`, for `Γ`, `φ` over `E`
and `R` a list of well-formed signed atoms of the generated predicates: each a generated predicate applied to a
declared constant of its argument sort, or the negation of one (`SignedAtom`, 9.1; every entry of `Γ_reports(D)`
is one, `premises_signed`). The typing is part of the statement, not a convenience: over an undeclared name `x`
the pair `P(x), ¬P(x)` has no model, while `¬(x = x)` is not a well-formed formula over `E` and nothing relates
the two sides; so the equivalence is stated for atoms over declared constants only, which are the only atoms
this specification generates, and then every disequality in `neqs R` is a well-formed old-language formula
(`neqs_wellFormed`). For positive `R` (every top-level unit a report or
assessment, no negation) `neqs R = []` and the report premises change no old-language verdict; the same holds
whenever the polarity of each generated predicate is uniform in `R`. For an admissible `S₀` over `E`,
`fol.Sat S₀ (neqs R)` is equivalent to the
existence of an expansion of `S₀` satisfying `R` (`expansion_exists_iff` for `R = Γ_reports(D)`, and by the same
construction for any list of well-formed signed atoms, which is what `reports_no_leak` uses: interpret each
generated predicate by its asserted holders, which lie in its sort's domain because the atoms are well-formed), and
it is the hypothesis of every theorem of 9.2 that builds a model of a document with negated units
(`expansion_exists`, `source_over_any_structure` and its instances); a positive document needs no hypothesis.
`R(a), ¬R(a)` yields `¬(a = a)`, so on both sides the P0 vacuity report says INCONSISTENT and every dependent
certificate is `vacuous`, visibly: the same line, at `E_reports` and at `E`. `reports_route_acceptance_base`
(9.3) carries `neqs (Γ_reports D)` into its old-language conclusion for the same reason.

### 4.5 The structure theorems, in words (NON-NORMATIVE: a reading of 9.2; the statements there govern)

Nothing in this section is a claim beyond the theorem statement each bullet names, read under that statement's
hypotheses and no wider (section 0, "Normative content"); a bullet that said more than its theorem would be a
defect, to be deleted. Each theorem is over the report premises `Γ_reports(D)` and holds on the fragment its
hypotheses name: a positive document, or a document with negated units under `Expandable D S₀`, that is,
`fol.Sat S₀ (neqs (Γ_reports D))` (4.4); a queried key that no top-level unit asserts or denies (`∉ topKeys D`),
or a queried holder-applied atom that no positive top-level premise carries at a co-denoting holder
(`holder_atom_free`); a content that is a formula over `E` and is false in `S₀`. The fixtures at the boundaries,
one hypothesis broken each: an inconsistent signed premise set (`D_μ″`, `D_π′`); the queried key asserted at the
same holder (`D_η`, B₁, B₃) or at another holder (B₉, B₉′); a content the disequalities force (B₄) or a valid
content (B₆); the author's premises (B₈); a nested content carried or denied by another unit (B₇, B₁₀, B₁₁,
`D_ω`, B₁₂′), or nested under a negation or two deep with no unit carrying its key (B₁₁′, B₁₂); a canonical
object the document does not digest, for the digest theorems (B₁₄, B₁₅, B₁₆). Each fixture
names the premise subset it is over (γ, ε, η, μ over `D ▷ U`, 10.1; the boundaries in 10.3, whose closing table
names the one hypothesis each breaks).

- **Not factive** (`attitude_not_factive`; hypotheses: `u ∈ D.units` with content `report hd act c (formula q)
  lit`, `S₀` admissible over `E`, `Expandable D S₀`, `q` false in `S₀`; conclusion: a source model with `S = S₀`
  in which every top-level statement of `D` holds and `q` is false). Read with `reports_no_leak` at `Γ = []` and
  `R = Γ_reports(D)`, for `q` over `E`: `Γ_reports(D)` entails `q` exactly when `neqs (Γ_reports D)` does; with
  `reports_no_leak_uniform` and `positive_uniform`, for a positive document exactly when `q` is valid over `E` on
  its own (B₆); for a document with negated units, B₄. The same statement for belief, desire and intention (the
  act is a parameter) and, as `assessment_not_factive`, for the formula content of an assessment (5.3). A nested
  content is outside every hypothesis of this bullet: it elaborates to a signed generated atom at the nested
  node's own holder or evidence context, not to a formula over `E`, and `reports_no_leak` does not cover it. What
  the report premises entail about that atom is the five nested-content theorems of 9.2, each read under its own
  hypotheses: `nested_positive_entailed` (a top-level unit carries the very node, holder and all: B₁, B₇, B₁₂′),
  `nested_positive_refuted` (a top-level unit carries the node's negation: B₁₀), `nested_negated_entailed` and
  `nested_negated_refuted` (the nested node is itself negated; a top-level unit denies, B₁₁, or asserts, `D_ω`,
  its operand), and `holder_atom_free` (no positive top-level premise carries the atom at a holder co-denoting
  with the node's, whatever `topKeys` contains: B₉, the same key at another holder), beside `unreported_key_free`
  (no top-level unit carries the key at all: `D_ζ`, B₂, B₁₂).
- **Not closed** (`no_closure_under_consequence`; hypotheses: `beliefsIn D hd c P (P → Q)`, `holderSort D hd =
  some s`, the key `⟨believes, s, c, cid Q⟩ ∉ topKeys D`, `S₀` admissible, `Expandable D S₀`; conclusion: a
  source model over `S₀` with the belief-in-`Q` relation empty; `D_β`). B₃ carries the belief in `Q` as a
  top-level unit at the same holder, so its atom is a premise and the theorem has no instance (`hQ` fails); for
  `Q` over `E` itself, the first bullet.
- **Nested independence** (`nested_independent`; hypotheses: `u`'s content is `report h₁ act c (report h₂
  believes c′ (formula q) none) lit`, `holderSort D h₂ = some s₂`, `⟨believes, s₂, c′, cid q⟩ ∉ topKeys D`, `S₀`
  admissible, `Expandable D S₀`, `q` false in `S₀`; conclusion: a source model over `S₀` with the inner belief
  relation empty and `q` false; `D_ζ`). One hypothesis broken each: `hin`, the inner key in `topKeys` at the
  same holder (B₁: `nested_positive_entailed` applies instead) or at another holder (B₉′: `holder_atom_free`
  applies instead); `hb`, an inner `says` node (B₂: `hb` names an inner `believes` node, and
  `unreported_key_free` applies at the inner key instead), a negated inner node whose key no top-level unit
  asserts or denies (B₁₁′: `all_truth_combinations` applies instead) or nesting depth 2 with no top-level unit of
  either nested key (B₁₂: `hb` names a formula body at depth 1, and `unreported_key_free` applies at both nested
  keys instead). B₁₁,
  `D_ω` and B₁₂′ break `hb` and `hin` together, their nested key being denied or asserted at top level, and are
  instances of the nested-content theorems, not one-hypothesis boundaries of this one (the table of 10.3).
- **Negation scopes** (`negation_scopes_distinct`, under its hypotheses that a belief node over `¬q` and one
  over `q`, in one context and with holders of one sort, both occur in the document, as `D_ε`'s u1 and u2's
  operand do: `J_{believes,c,¬q}(h)` and `¬J_{believes,c,q}(h)` are a positive atom of one key and the negation
  of an atom of another key, with different complement objects and names; B₁₅, `D_ε`'s u1 alone, is the boundary
  at which the second node is absent; `all_truth_combinations` with `ks` the two keys under its hypotheses,
  neither key in `topKeys`, `S₀` admissible, `Expandable D S₀`: any of the four truth combinations, uniformly on
  the holder sort's domain; `D_ε ▷ []`).
- **Denial is not the opposite belief** (`unreported_key_free` at the key of `J_{believes,c,¬q}(h)` when it is
  `∉ topKeys D`, under `Expandable D S₀`; `reports_no_leak` at `Γ = []` for a formula content `q` over `E`:
  `Γ_reports(D)` entails `q` exactly when `neqs (Γ_reports D)` does, and with another unit asserting
  `J_{believes,c,q}(h′)` beside the denial at `h`, `neqs` is `[¬(h′ = h)]`; `D_ω′`, B₄).
- **Tense** (`tense_keys_distinct`: `c` (past) and `c′` (present) give different names; `unreported_key_free` at
  the present key when it is `∉ topKeys D`, under `Expandable D S₀`: a source model over `S₀` with the present
  relation empty; `D_η ▷ [u1]`, which is positive; over `D_η` itself both are premises).
- **Contents are structural** (`content_structural`: two formula contents over `E` have one canonical object
  exactly when their P5 normal forms are equal, never when they are merely logically equivalent; for two formula
  nodes that both occur in a well-formed document, its `Occurs` hypotheses, the same for their content ids).
- **Intention is not fulfilment or obligation** (`attitude_not_factive` with `act = intends`: `J_{intends,c,q}(h)`
  with `q` false, under the first bullet's hypotheses). No `required` atom is generated: `elab` produces one
  predicate per key and nothing else (4.3); an author may declare a base predicate of that name, decided by
  nothing (fixture ο), and a regulated one needs `norms@0`, which this slice rejects beside `reports@0` (11.3).

### 4.6 Open questions (NON-NORMATIVE)

Readings the directive of draft 7 did not let this draft assert, because no theorem statement of 9.2 covers them
as written. Each is a question for the statement review, not a claim; an answer enters this specification as a
theorem statement with its fixtures or not at all.

1. **Canonically equal, syntactically distinct nested contents.** `nested_positive_entailed` is stated on node
   identity (`u′.content = n`). Two report nodes with one holder, act and context whose formula bodies are
   distinct ASTs with one P5 normal form have one complement id (3.4) and elaborate to one atom (4.3), so the
   nested one would be entailed by the top-level one; no theorem states it, and no fixture expects it.
2. **The situation line for a nested content at another holder.** Over B₉′ the line shows a situation from
   `holder_atom_free`; over B₁ it reports a certificate. Whether the line should also say, in English, that the
   key is asserted at another holder (so that a reader sees why B₉′ and B₁ differ) is a display question for
   item 4; nothing here depends on it.
3. **`topKeys` versus holder-applied atoms in the premise-subset device.** 10.1's properties (i) to (iii) are
   stated on keys, which is what `unreported_key_free` and `all_truth_combinations` need. Whether the device
   should also be stated on signed holder-applied atoms, so that an independence fixture can keep a key asserted
   at one holder and query it at another (B₉'s shape), is left open; no fixture of 10.2 needs it.

## 5. Scoped checks, bridges, assessments, adoption and import

### 5.1 Scoped consequence and inner consistency

A scoped check selects payloads by path (occurrence-qualified content nodes, so two occurrences of one content
are two payloads and sharing a holder merges nothing) and asks, in the payloads' own environment `E_q` and under
that environment's own frozen route, whether the conclusion follows. `E_q` is the author's `E` when the payloads
are ordinary formula contents, or the pinned environment of one quoted package when they are its statement
(3.3); the check runs the frozen route of `E_q`'s own profiles locally (the FOL route with its literal
premises; for a `definitions@0` package the definitions route, whose background `Background(E_q)` is
`VE.Definitions.Route.background`, the definition premises followed by the literals), as κ's local W1 check
already runs the frozen W1 route under its pinned environment:

```text
FOLLOWS               a certificate for  E_q, Background(E_q) ++ payloads ⊢ conclusion   (the unchanged tableau
                      checker at E_q's route)
DOES NOT FOLLOW       a checked finite model over E_q, valid for E_q's route, satisfying Background(E_q) and the
                      payloads and refuting the conclusion
PAYLOADS INCONSISTENT a certificate for  E_q, Background(E_q) ++ payloads ⊢ ⊥   (reported once per payload set;
                      dependent scoped results are vacuous)
UNKNOWN               budget named
```

Display: "S follows from the reported contents ‹paths›." Never "the speaker believes S", "the article says S" or
bare S. A scoped check is a report line: it is not in `Γ`, not in `E_reports`, not a premise of anything
(`scoped_not_premise`), and an inconsistent payload set makes nothing outside vacuous: the report premises make
the outer checked list inconsistent only through `neqs` (for `Γ` over `E`, `checkedList D Γ` is inconsistent
exactly when `literals ++ neqs (Γ_reports D) ++ Γ` is, `reports_no_leak` with `φ = ⊥`, 4.4; the author's own `Γ`
may be inconsistent by itself), never through a payload (`quoted_inconsistency_local`, fixture θ).
`Background(E_q)` is local to the check exactly as `E_q` is: a definition premise used inside a scoped check is
never inserted into the document's checked list. It is not in `Background(E_reports)` (the literals) and not
among the report premises, so it is in `checkedList D Γ` only when the author has written it into `Γ` as an
ordinary premise of their own, which locality does not forbid (`scoped_background_local`, fixture λ). Vacuity of
the *inner* set is shown with the check;
vacuity of the *outer* premise set is P0's line (7.1).

### 5.2 Bridges are explicit premises with an exact target

```text
path        (unit, ε)              the unit's root complement (legacy meaning: W2's QuotedUnit rule, unchanged)
            (unit, 1), (unit, 1.1)… the complement of the nested node reached by descending into the complement
                                   once per "1" (every report, assessment and definition node has exactly one
                                   complement: its body, or its statement; a negated node is transparent, the
                                   step passes through it into its operand's complement; a norm node has none)
envAt p     the environment the node at p is over: E, or the pinned E_q of the enclosing quoted package
holderAt p  the holder of the report node whose complement p names; none for an assessment node (its accepting
            agent is unrestricted, as W2's agentMatches leaves it for hedged kinds) and for other nodes
formulaAt p elab(content at p)     none for a norm or definition node
bridge leaf root:    a graph leaf labelled bridge:accepts(<holder>,<unit>), parsed by the frozen two-token
                     parseLabelRaw; formula = formulaAt (unit, ε); holder = holderAt when the root is a report
                     node, any agent when it is an assessment node (exactly QuotedUnit's agentMatches)
            nested:  a graph leaf labelled bridge:accepts_at(<holder>,<unit>,<path>), a new label constructor
                     with explicit unit and path fields parsed by a new branch (the frozen branch accepts exactly
                     two tokens and is untouched); formula = formulaAt p; the same holder rule; envAt p = E; and a
                     bridge record (3.2) with that unit and path naming reviewer and reason
```

Accepting the article's complement in "the article says that Anthropic believes that q" (root path) assumes the
belief atom `J_{believes,c′,q}(anthropic)`; accepting the payload (path `(u, 1)`) assumes `q`; neither assumes the
other, and accepting that a report occurred needs no bridge at all, because the report atom is already the
document's premise `report:<unit>`. A denied report is no different: the root complement of "it is not the case
that Anthropic believes that q" is `q`, and its bridge assumes `q`, not the denial. An independent proof of a
payload is cited with all its dependencies (`cite:`) instead. Testimony, prestige, a URL and a certificate of
faithful quotation never discharge a bridge: it stays in the assumption list of every report that uses it and
propagates through citations (`admit_report_sound` and `CitationsClosed`, unchanged). Root-path bridges keep the
legacy `bridge:accepts` meaning byte for byte (`bridge_root_is_legacy`): a unit named `u1.1` is a root target
under that label, never a nested one. The nested form is a separate label under the profile, never retrofitted
into a legacy record. A definition package's statement is reachable by path for scoped checks and is never a
bridge target, because it is over `E_q` (`BridgeKindMismatch`).

### 5.3 Assessments

Each assessment unit contributes one atom `May(a, q)` or `Probably(a, q)` to `Γ` (labelled `assessment:<unit>`;
negated for a denied assessment) and one open term to the residual: name `reports__<judgment>__<k>`, arguments
`[<evidence sort>]`, and the record's `decided_by`, criteria, factors, precedents, jurisdiction and version (W2's
complete schema). In Lean the W2 open-term inventory is a list of names (`Doc.openTerms : List String`,
`Route/Admission.lean`), so `openTerms D` is the list of generated assessment names and the record behind each
name is `recordOf D a`; the Python residual renders both. The atom is an
assumption like any premise: "the assessment on record holds that q may be so". No rule of the checker derives
`q` from `May(a, q)`, `Probably(a, q)` from `May(a, q)`, `May(a, q)` from `Probably(a, q)`, or anything from the
criteria; what the report premises `Γ_reports(D)` entail is the theorem statements of 9.2 and 9.3, read here
under their hypotheses and no wider (the author's premises aside, B₈): a generated assessment atom whose key is
`∉ topAKeys D` is free over an admissible `Expandable` `S₀` (`all_truth_combinations_assess`; `D_μ ▷ [u1]`); for
a content `q` that is a formula over `E`, `assessment_not_factive` under its hypotheses (`q` false in an
admissible `Expandable` `S₀`) gives a source model in which every top-level statement holds and `q` is false, and
`reports_no_leak` with `Γ = []` reads: `q` is entailed exactly when `neqs (Γ_reports D)` entails it (for a
positive document, exactly when `q` is valid on its own, B₆); for a nested content, a report node, an assessment
node or the negation of one, `q` elaborates to a signed generated atom at the nested node's own holder or
evidence context, which `reports_no_leak` does not cover and `assessment_not_factive`'s `hc` excludes, and what
is entailed about it is the nested-content theorems of 9.2: `nested_positive_entailed` (B₇: u1 carries the very
node u2 nests, holder included, so a certificate for the atom replays from u1's premise; `neqs = []` and the
content not valid), `holder_atom_free` (B₉: the same key at another holder, the atom free), `unreported_key_free`
(`B₇ ▷ [u2]`) and, for a negated nested content, `nested_negated_entailed` (B₁₁) and `nested_negated_refuted`
(`D_ω`); an asserted atom is a premise (`D_μ` asserts both `May` and `Probably` of `safe`; `D_μ″` is inconsistent
and entails everything). The
criteria bind only when the author writes them into `Γ` (they are not premises by themselves; 13.5). The status
of an assessment unit is OPEN (6).

### 5.4 Adoption and import are typed operations, not bridges

A quoted W1 block gets the local conflict and completion check of W1 (norms.md 5) under its pinned `E_q`, reported
as "among the quoted rules" with no active outer layer; a quoted W3 package is validated under its pinned `E_q`
and never redefines outer vocabulary (no `background:definitions` premise outside, no unfolding). A bridge whose
target is a norm or definition node is rejected (`BridgeKindMismatch`): a formula bridge cannot activate rules or
install definitions. Adoption and import are W8 actions that write ordinary norm or definition units into the
*destination* document with the provenance field `adopted_from: <path>` / `imported_from: <path>` (a token path
plus the source document id); the destination document is then admitted as any norm or definition document is
today, regenerating its own validated layers and environments. An unsupported destination combination retains the
existing integration gates (INTEGRATION-GAPS.md). The provenance field is part of the unit object and its hash; it
adds no semantics.

## 6. Status and coverage (plan page 3, no new status)

| Unit | Status | Bytes |
|---|---|---|
| report unit, complement admitted, no open terms | CHECKED: scope, types, identities and content admitted; the report atom is an identified assumption (support `testimony`), not proved true | whole span |
| report unit whose content carries open terms | OPEN | whole span |
| assessment unit | OPEN, with its generated open term | whole span |
| negated report or assessment unit | as its operand (CHECKED or OPEN): the denial is the identified assumption, the content is not claimed and neither is the opposite report | whole span |
| report wrapper whose complement is unformalised | MIXED: the wrapper bytes LABELLED (`attributed` metadata: holder, act, occurrence), the complement bytes UNFORMALISED with the reason | by part |
| unit with a reading set over contents or acts | READINGS per W2; unelaborated alternatives earn nothing | whole span |
| attributed or hedged kind with no content | LABELLED, as today | whole span |

A wrapper alone never upgrades a span: the complement's bytes take the complement's status, and a passage whose
source meaning is missing keeps its residual (plan page 4, accounting gate). Recursive complements add no bytes;
scoped checks add none. Residual lines beside W2's (open terms, assumptions, bridge leaves, unresolved reading
sets): `reports` (report premises by act and tense, asserted and denied counted separately), `assessments` (by
decider, `unresolved_decider` counted separately, asserted and denied separately), `bridges_nested` (with unit
and path), `scoped_checks` (with inner status and environment), `literal_quotations`,
`unreviewed_acts` (units whose act is outside the slice, by act). Counting is by the plan's accounting gate; this
specification predicts no number.

## 7. The report

### 7.1 The five questions

| Question | Method | Result |
|---|---|---|
| What does each report establish? | elaboration (4.3), paraphrase (2.1, 2.3) | per unit: the atom, the paraphrase, "claimed / not claimed", the key beside the generated name |
| Do the selected reported contents entail S, and are they consistent? | scoped check at `E_q` (5.1) | FOLLOWS / DOES NOT FOLLOW / PAYLOADS INCONSISTENT / UNKNOWN, with certificate, model or budget |
| Which bridges does an argument use, and what exactly do they assume? | admission (5.2), `admit_report_sound` | per leaf: holder, path, formula, reviewer, reason; in the assumption list and the residual |
| Is the document's premise set consistent, including the report literals? | P0 vacuity report over `Background(E_reports) ++ Γ` (PLAN-EXPAND2 3.8) | model id / INCONSISTENT (dependent certificates `vacuous`) / UNKNOWN |
| Which assessments are open and who decides? | the open-term records (5.3) | per assessment: judgment, content, decider, criteria, factors, version |

### 7.2 Status text

```text
REPORT <unit>: <holder> <act> (<context id>, <tense>) content <content_id> [literal]; claimed: the report;
               not claimed: the content, any other act of <holder>
REPORT <unit>: denied: <holder> <act> (<context id>, <tense>) content <content_id>; claimed: that the report did
               not occur; not claimed: the content, its negation, any other act of <holder>
SCOPED <id>: FOLLOWS from <paths> under <E_q> (certificate <id>) | DOES NOT FOLLOW (model <id>) |
             PAYLOADS INCONSISTENT (certificate <id>) | UNKNOWN (<budget>)
BRIDGE <label>: assumes <sentence> at <unit>[, path <path>] for <reviewer>, reason <units>; not discharged
ASSESSMENT <unit>: OPEN; <judgment> per assessment <a>, decided by <decider>; admission establishes neither
                   possibility nor likelihood
PREMISES: model <id> | INCONSISTENT(<certificate>) | UNKNOWN(<budget>)        (P0's line, unchanged)
```

## 8. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: reports@0 requires the FOL family` (with the frozen `classify` text for the list minus `reports@0`) / `reports@0 needs a reports block` / `reports@0 with <profile> layers` | the reports gate (4.1 step 1, 9.4); block absent; `norms@0`, `definitions@0` or `data@0` present (11.3) | error |
| `HashCollision: <digest>` / `InvalidInput: negated operand in <unit>` | two distinct canonical objects with one digest; `negated` around a formula, a quoted block or a negated node (3.3, 4.1 step 4) | error |
| `UnsupportedAct: <act> (reports@0 admits says, believes, wants, intends)` | a `report` block naming another act | error |
| `UnknownHolder: <name>` / `HolderSort: <name> is not of a holder sort` / `UnknownSymbol: holder sort <s>` / `UnknownSymbol: evidence sort` | holder or sort declarations (3.1, 4.1) | error |
| `UnknownContext: <c>` / `ContextTense: <c>` / `UnknownAssessment: <a>` / `DuplicateDeclaration: context <c>` / `assessment <a>` / `bridge <b>` / `scoped <s>` | front matter (3.2) | error |
| `InvalidInput: assessment <a> needs decided_by` / `author predicate <p> begins with reports__` / `holder verbalisation reserved` / `invalid content for <unit>` | field consistency | error |
| `KindMismatch: <unit>` | W2 kind and content tree disagree (3.3) | error |
| `OpenComplement: <unit>` | a content formula is not closed, or a name is unresolved, or a binder crosses a node | error |
| `ScopedEnvironment: <s>` / `ScopedTarget: <s>, <path>` | payloads over two environments; a payload path that is not a formula node | error |
| `BridgeTarget: <unit>[, <path>]` / `BridgeKindMismatch: <unit>[, <path>]` / `BridgeHolder: <unit>[, <path>]` / `MissingBridgeRecord: <unit>, <path>` / `InvalidInput: bridge path <p>` | bridge path unresolved; norm or definition target, or a node under a pinned `E_q`; label holder differs from `holderAt` on a report node; `bridge:accepts_at` label without a record; a path that is not `1(.1)*` | error |
| `AdmissionError: quoted content of unit <u> is used without a bridge leaf` and the other P0 admission texts | unchanged, extended to paths | error |
| `DependencyCycle: <sorted content ids>` | a malformed wire's content-id table (4.1 step 4) | error |
| `ManifestMismatch: <unit>` (English layer only) | rendering or parsing a sentence under a manifest other than its own (2.4) | error |
| `ResourceLimit: content depth` / `contexts` / `assessments` / `scoped payloads` / `literal bytes` / `MAX_PREDICATES` / `identifier <n> exceeds 64 bytes` | limits (11.1) | error |
| the existing all-derivations rejection with the two rewrites | `may not`, `probably not`, or any input with two derivations (2.1) | error |
| `unreviewed act <act> in <unit>` / `noun complement in <unit>` / `fragment complement in <unit>` | report lines for units that stay UNFORMALISED with those reasons | warning |

Order: environment declarations, then W2's checks, then contexts and assessments, then units in document order
(kind, holder, act, context, content recursively), then scoped checks, then bridges, then `E_reports`. English
diagnostics carry the span and the plain-language expectation as today. Existing P0, W1, W2 and W3 diagnostics are
unchanged.

## 9. Lean (item 2): definitions and the exact statements to prove

Files: `lean/VE/Reports/Content.lean` (contents, keys, ids, `envReports`), `Semantics.lean` (source models,
`IntendedReports`, `interp`, `restrictJ`), `Elaborate.lean` (`elab`, `premises`, the faithfulness and
conservativity theorems), `Route.lean` (the `Layer.id` instance and the restated acceptance and countermodel
theorems), `Scoped.lean`, `Bridge.lean`, `Assess.lean`, `Wire.lean`, `Admission.lean`, `Run.lean` (the
`ve_reports_route` executable, its own Lake target: `lean/Main.lean` is hash-frozen), and `lean/REPORTS.md` listing
every theorem in plain words. Frozen `Route/*`, `Norms/*`, `Definitions/*` and all P0 sources are untouched;
`VE.lean`, `VE/Audit.lean` and `lakefile.toml` gain imports, audit entries and the new target only; the audit
allowlist is unchanged; Lean text never uses the audit's forbidden tokens, even in comments. Names below have the
prefix `VE.Reports.`; P0 names are `VE.Route.*` as in `lean/VE/Route/`. The blocks are statement schemata: helper
names are defined here, not already implemented Lean. Every theorem is stated for `VE.Structure.{u}` at every
universe `u`.

### 9.1 Definitions

```lean
namespace VE.Reports
open VE.Route (Layer Unique Semantics fol Checker CertificateSound)
open VE.Route.Background (StringAdmissible LiteralsDistinct literals literalsValid folLayer EntailsString)
open VE.Definitions (forget hide)                -- forget ns S and hide E ns, the list forms of lean/VE/Definitions/Layer.lean
universe u

inductive Act | says | believes | wants | intends
inductive Judgment | may | probably
inductive Tense | present | past | perfect

structure Context where
  id : String
  tense : Tense
  referenceTime : Option String        -- opaque tag; no temporal inference
  description : String

/-- W2's complete open-term record, per assessment. `decidedBy` is never absent. -/
structure Assessment where
  id : String
  context : String                     -- a constant of the evidence sort
  decidedBy : String                   -- "unresolved_decider" when the source names none
  necessary sufficient : List VE.Formula
  factors precedents : List String
  jurisdiction : String
  version : Nat

/-- 1.1: contents and statements in one type. `negated` wraps one report or assessment node (4.1 step 4). -/
inductive Content where
  | formula (φ : VE.Formula)                                    -- closed, typed over E (over E_q as a package's statement)
  | norm (Eq : VE.Environment) (D : VE.Norms.Doc)               -- pinned local environment; no layer
  | definition (Eq : VE.Environment) (ds : List VE.Definitions.Def) (stmt : Option VE.Formula)   -- statement over Eq
  | report (holder : String) (act : Act) (ctx : String) (body : Content) (literal : Option String)
  | assessment (j : Judgment) (a : String) (body : Content)
  | negated (n : Content)

def Content.isReport : Content → Bool     | .report .. => true | _ => false
def Content.isAssessment : Content → Bool | .assessment .. => true | _ => false
/-- The top-level form (the statement grammar of 1.1): a report, an assessment, or the negation of one. -/
def Content.Statement : Content → Prop
  | .report .. => True
  | .assessment .. => True
  | .negated n => n.isReport = true ∨ n.isAssessment = true
  | _ => False
/-- Every node of a tree, including the root. -/
def Content.nodes : Content → List Content

structure ReportKey where act : Act; sort : String; ctx : String; content : String        -- complement id
structure AssessKey where j : Judgment; a : String; content : String

/-- One top-level unit: its id and its statement; document order is the order of `ReportDoc.units`. -/
structure Unit where id : String; content : Content

/-- 5.2: a unit and a depth. Depth 0 is the unit's root complement (the legacy target); depth n descends n times,
    once per `1` of the rendered path. -/
structure Path where unit : String; depth : Nat

structure Bridge where id : String; target : Path; acceptedBy : String; reason : List String   -- target.depth ≥ 1
structure ScopedCheck where id : String; payloads : List Path; conclusion : VE.Formula

structure ReportDoc where
  E : VE.Environment                    -- the author's environment, with the reports block decoded
  lits : List String
  holders : List String                 -- holder sorts
  evidence : String                     -- the evidence sort
  contexts : List Context
  assessments : List Assessment
  units : List Unit                     -- report, assessment and negated units, one sequence, document order
  bridges : List Bridge
  scoped : List ScopedCheck

def Occurs (D : ReportDoc) (x : Content) : Prop := ∃ u ∈ D.units, x ∈ u.content.nodes
/-- 3.4: a complement object occurs in D when some report node of some tree, under a negated node or not, has
    that body and literal. The collision check of 4.1 step 4 digests exactly the content objects of occurring
    nodes and the complement objects of occurring report nodes; an object outside both is never digested. -/
def OccursComplement (D : ReportDoc) (body : Content) (lit : Option String) : Prop :=
  ∃ hd act c, Occurs D (.report hd act c body lit)
def Positive (D : ReportDoc) : Prop := ∀ u ∈ D.units, ¬ ∃ n, u.content = .negated n

/-- 3.4: the identity is the canonical object; the digest names it. -/
def canonicalObject (D : ReportDoc) : Content → Json                       -- object(x) of 3.4
def complementObject (D : ReportDoc) (body : Content) (lit : Option String) : Json
def contentId (D : ReportDoc) : Content → String                           -- digest of canonicalObject
def complementId (D : ReportDoc) (body : Content) (lit : Option String) : String   -- digest of complementObject
def documentId (D : ReportDoc) : String                                    -- document_id(D) of 3.4
/-- 4.1 step 4, the depth the admission check bounds: a leaf (formula, norm, definition) counts one, a report or
    assessment node one more than its body, a negated node nothing, as it counts nothing in a W2 kind (3.3). A
    well-formed unit's content depth is therefore the depth of its W2 kind, whose frozen decoder
    (`VE.Route.Admission.decodeKind`, fuel 16) admits exactly the kinds of depth at most 16 (B₁₃, B₁₃′). -/
def Content.depth : Content → Nat
  | .report _ _ _ b _ => b.depth + 1
  | .assessment _ _ b => b.depth + 1
  | .negated n => n.depth
  | _ => 1
def holderSort (D : ReportDoc) (h : String) : Option String       -- D.E.constants h, when a holder sort
def keys (D : ReportDoc) : List ReportKey                          -- every report node of every tree, deduplicated, sorted (1.5)
def akeys (D : ReportDoc) : List AssessKey
def topKeys (D : ReportDoc) : List ReportKey                       -- keys of the top-level report units, asserted or denied
def topAKeys (D : ReportDoc) : List AssessKey                      -- likewise for assessment units
def keyOf (D : ReportDoc) (r : String) : Option (ReportKey ⊕ AssessKey)   -- the key whose generated name is r
def reportName (D : ReportDoc) (k : ReportKey) : String            -- reports__<act>__<i>, i among the keys of that act
def assessName (D : ReportDoc) (k : AssessKey) : String            -- reports__<judgment>__<i>, likewise
def names (D : ReportDoc) : List String
def envReports (D : ReportDoc) : VE.Environment                    -- E + one unary predicate per key
def recordOf (D : ReportDoc) (a : String) : Option Assessment
def tenseOf (D : ReportDoc) (c : String) : Option Tense
def WellFormedReports (D : ReportDoc) : Bool                       -- 4.1; HashCollision over the content ids of occurring nodes
                                                                   -- and the complement ids of occurring report nodes only

/-- 4.3: total on formula, report, assessment and negated nodes; none on norm and definition nodes. -/
def elab (D : ReportDoc) : Content → Option VE.Formula
  | .formula φ => some φ
  | .report h act c b lit =>
      (holderSort D h).map fun s => .unary (reportName D ⟨act, s, c, complementId D b lit⟩) (.const h)
  | .assessment j a b =>
      (recordOf D a).map fun r => .unary (assessName D ⟨j, a, contentId D b⟩) (.const r.context)
  | .negated n => (elab D n).map .not
  | _ => none
def unitPremise (D : ReportDoc) (u : Unit) : Option VE.Formula := elab D u.content
def premises (D : ReportDoc) : List VE.Formula := D.units.filterMap (unitPremise D)   -- Γ_reports(D), document order
def openTerms (D : ReportDoc) : List String := (akeys D).map (assessName D)          -- W2's inventory: names (5.3)

/-- 4.4: well-formed signed generated atoms (a generated predicate applied to a declared constant of its argument
    sort, or the negation of one), defined by shape and typing and not by membership in `premises D`, and the
    holder disequalities a signed list forces (in the list's order). The typing is what keeps `neqs` exact: it
    puts every asserted holder in the predicate's sort domain and makes every disequality well-formed over `D.E`;
    a signed pair over an undeclared name has no model and forces no well-formed disequality. -/
def SignedAtom (D : ReportDoc) (a : VE.Formula) : Prop :=
  ∃ r ∈ names D, ∃ h, (VE.Formula.unary r (.const h)).WellFormed (envReports D) [] ∧
    (a = .unary r (.const h) ∨ a = .not (.unary r (.const h)))
def neqs (R : List VE.Formula) : List VE.Formula                   -- [¬(h = h') | P(h) ∈ R, ¬P(h') ∈ R]
def UniformPolarity (R : List VE.Formula) : Prop :=
  ¬ ∃ P h h', .unary P (.const h) ∈ R ∧ .not (.unary P (.const h')) ∈ R
/-- The model-existence hypothesis of every theorem that builds a model of D: trivial for a positive D. -/
def Expandable (D : ReportDoc) (S₀ : VE.Structure.{u}) : Prop := fol.Sat S₀ (neqs (premises D))

/-- 5.2: paths. `complementOf` passes through a negated node into its operand; a norm node has no complement. -/
def complementOf : Content → Option Content
  | .report _ _ _ b _ => some b
  | .assessment _ _ b => some b
  | .definition _ _ (some st) => some (.formula st)
  | .negated n => complementOf n
  | _ => none
def contentAt (D : ReportDoc) : Path → Option Content            -- the unit's root complement, then complementOf depth times
def envAt (D : ReportDoc) : Path → Option VE.Environment         -- D.E, or the pinned Eq of the enclosing package
def holderAt (D : ReportDoc) : Path → Option String              -- the holder of the report node whose complement p names
def isAssessmentAt (D : ReportDoc) : Path → Bool                 -- p names an assessment node's complement
def bridgeFormula (D : ReportDoc) (p : Path) : Option VE.Formula := (contentAt D p).bind (elab D)
inductive BridgeLabel
  | root (agent unit : String)                     -- bridge:accepts(<agent>,<unit>): the frozen two-token branch
  | nested (agent unit : String) (depth : Nat)     -- bridge:accepts_at(<agent>,<unit>,<path>): the new branch, path = 1(.1)*
def BridgeLabel.agent : BridgeLabel → String
def BridgeLabel.path : BridgeLabel → Path          -- root a u ↦ ⟨u, 0⟩; nested a u n ↦ ⟨u, n⟩
def parseBridge : String → Option BridgeLabel      -- root case: exactly VE.Route.Admission.parseLabelRaw's bridge branch
/-- The holder rule: a report node's holder must match; an assessment node's accepting agent is unrestricted
    (W2's agentMatches for hedged kinds); no other node is a target. -/
def HolderOk (D : ReportDoc) (p : Path) (a : String) : Prop := isAssessmentAt D p = true ∨ holderAt D p = some a
def BridgeAdmitted (D : ReportDoc) (leaf : VE.Graph.Claim) : Prop :=
  ∃ l, parseBridge leaf.label = some l ∧ HolderOk D l.path l.agent ∧ bridgeFormula D l.path = some leaf.formula ∧
    envAt D l.path = some D.E ∧
    (match l with | .root .. => True | .nested _ u n => ∃ b ∈ D.bridges, b.target = ⟨u, n⟩)

/-- 5.1 -/
def payloadFormulas (D : ReportDoc) (s : ScopedCheck) : Option (VE.Environment × List VE.Formula)
  -- some (Eq, ps) when every payload path names a formula node and envAt agrees on Eq for all of them; else none
def background (Eq : VE.Environment) : List VE.Formula
  -- Background(Eq) of Eq's own frozen route: literals for the FOL family; VE.Definitions.Route.background
  -- (expand ds ++ literals) for a definitions@0 package; the W1 base background for a norms@0 block

/-- 4.2: the independent semantics, typed by the key's sort. -/
structure Source (D : ReportDoc) where
  S : VE.Structure.{u}
  J : Act → String → String → String → S.Carrier → Prop        -- act, holder sort, context id, complement id
  A : Judgment → String → String → S.Carrier → Prop            -- judgment, assessment id, content id
  J_typed : ∀ a s c q v, J a s c q v → S.domain s v
  A_typed : ∀ j a q v, A j a q v → S.domain D.evidence v

/-- 4.2: satisfaction of a statement, by recursion on the statement grammar. Nested nodes are contents: the
    recursion stops at a report or assessment node and never visits its body. -/
def Sat (D : ReportDoc) (M : Source.{u} D) : Content → Prop
  | .report h act c b lit =>
      ∀ s, holderSort D h = some s → ∀ v, M.S.constant h = some v → M.J act s c (complementId D b lit) v
  | .assessment j a b =>
      ∀ r, recordOf D a = some r → ∀ v, M.S.constant r.context = some v → M.A j a (contentId D b) v
  | .negated n => ¬ Sat D M n
  | _ => True
def IntendedReports (D : ReportDoc) (M : Source.{u} D) : Prop := ∀ u ∈ D.units, Sat D M u.content

def interp (D : ReportDoc) (M : Source.{u} D) : VE.Structure.{u} :=
  { M.S with relation := fun r vs =>
      match keyOf D r, vs with
      | some (.inl k), [v] => M.J k.act k.sort k.ctx k.content v
      | some (.inr k), [v] => M.A k.j k.a k.content v
      | some _, _ => False
      | none, _ => M.S.relation r vs }

/-- The domain guards discharge the typing fields for every S'; forget keeps carrier, domains and constants. -/
def restrictJ (D : ReportDoc) (S' : VE.Structure.{u}) : Source.{u} D where
  S := forget (names D) S'
  J := fun act s c q v =>
    ⟨act, s, c, q⟩ ∈ keys D ∧ S'.domain s v ∧ S'.relation (reportName D ⟨act, s, c, q⟩) [v]
  A := fun j a q v =>
    ⟨j, a, q⟩ ∈ akeys D ∧ S'.domain D.evidence v ∧ S'.relation (assessName D ⟨j, a, q⟩) [v]
  J_typed := fun _ _ _ _ _ hv => hv.2.1
  A_typed := fun _ _ _ _ hv => hv.2.1

/-- Two source models agree on D: one structure and, transported along that equality, one relation on every
    key of D. -/
def AgreeOn (D : ReportDoc) (M N : Source.{u} D) : Prop :=
  ∃ e : M.S = N.S,
    (∀ k ∈ keys D, ∀ v, M.J k.act k.sort k.ctx k.content v ↔
       N.J k.act k.sort k.ctx k.content (congrArg VE.Structure.Carrier e ▸ v)) ∧
    (∀ k ∈ akeys D, ∀ v, M.A k.j k.a k.content v ↔ N.A k.j k.a k.content (congrArg VE.Structure.Carrier e ▸ v))

/-- 4.4: P0's FOL route at E_reports (folLayer E lits is Layer.id E (StringAdmissible E lits) _). -/
def reportsRoute (D : ReportDoc) : Layer fol.{u} Unit := folLayer (envReports D) D.lits
def checkedList (D : ReportDoc) (Γ : List VE.Formula) : List VE.Formula := literals D.lits ++ premises D ++ Γ
```

### 9.2 Theorems: vocabulary, faithfulness, conservativity and structure

```lean
/-- 1.5: E ⊆ E_reports; generated names are fresh, bounded, injective on the document's keys; every premise is a
    well-formed signed atom. -/
theorem envReports_extends (D : ReportDoc) (h : WellFormedReports D = true) :
  ∀ a, a.WellFormed D.E [] → a.WellFormed (envReports D) []
theorem names_fresh (D) (h) :
  (∀ n ∈ names D, D.E.predicates n = none ∧ n.utf8ByteSize ≤ 64) ∧ (names D).Nodup
theorem names_injective_on_keys (D) (h) :
  (∀ k ∈ keys D, ∀ k' ∈ keys D, reportName D k = reportName D k' → k = k') ∧
  (∀ k ∈ akeys D, ∀ k' ∈ akeys D, assessName D k = assessName D k' → k = k')
theorem hide_envReports (D) (h) : hide (envReports D) (names D) = D.E
theorem premises_wellFormed (D) (h) : ∀ a ∈ premises D, a.WellFormed (envReports D) []
theorem premises_signed (D) (h) : ∀ a ∈ premises D, SignedAtom D a
theorem premises_all (D) (h) : (premises D).length = D.units.length              -- elab is total on statements
theorem keys_finite (D) (h) : (keys D).length + (akeys D).length ≤ contentCount D
/-- 4.1 step 4 and 11.1 admit depth 16, so the bound is `≤ 16`, attained by B₁₃ (fifteen negated nested reports
    over a formula: content depth 16, kind depth 16). From W2's kind bound and `KindMismatch` (3.3): a well-formed
    unit's content depth is its kind's depth. -/
theorem content_depth_bounded (D) (h) : ∀ u ∈ D.units, u.content.depth ≤ 16
/-- 3.4: among the objects a well-formed document digests, the content object of every occurring node and the
    complement object of every occurring report node, a digest names one canonical object (HashCollision
    rejected). Nothing is stated for an object the document does not digest (B₁₄ to B₁₆, 13.26). -/
theorem no_collision (D) (h) (x y : Content) (hx : Occurs D x) (hy : Occurs D y) :
  contentId D x = contentId D y → canonicalObject D x = canonicalObject D y
theorem no_collision_complement (D) (h) (b b' : Content) (l l' : Option String)
    (hb : OccursComplement D b l) (hb' : OccursComplement D b' l') :
  complementId D b l = complementId D b' l' → complementObject D b l = complementObject D b' l'

/-- reports_elaboration_faithful, the source-model direction: the elaborated premises hold in the interpretation
    of a source model exactly when the document's intended meaning holds of it. -/
theorem reports_elaboration_faithful (D : ReportDoc) (h : WellFormedReports D = true) (M : Source.{u} D)
    (hM : M.S.Admissible D.E) :
  (interp D M).Admissible (envReports D) ∧
  (fol.Sat (interp D M) (premises D) ↔ IntendedReports D M)

/-- The structure direction: on every admissible E_reports structure. -/
theorem reports_elaboration_faithful_out (D) (h) (S' : VE.Structure.{u}) (hS : S'.Admissible (envReports D)) :
  fol.Sat S' (premises D) ↔ IntendedReports D (restrictJ D S')

/-- Typed model correspondence in both directions. -/
theorem restrict_interp (D) (h) (M : Source.{u} D) (hM : M.S.Admissible D.E) : AgreeOn D (restrictJ D (interp D M)) M
theorem interp_restrict (D) (h) (S' : VE.Structure.{u}) (hS : S'.Admissible (envReports D)) :
  ∀ r vs, (interp D (restrictJ D S')).relation r vs ↔ S'.relation r vs
theorem old_formula_invariant (D) (h) (M : Source.{u} D) (a : VE.Formula) (ha : a.WellFormed D.E []) :
  a.denote (interp D M) [] ↔ a.denote M.S []
theorem restrictJ_admissible (D) (h) (S') (hS : S'.Admissible (envReports D)) : (restrictJ D S').S.Admissible D.E

/-- Finite witness decoding, at every universe: a valid finite model over E_reports is the interpretation of a
    source model. -/
theorem finite_witness_decodes {α : Type u} [DecidableEq α] (D) (h) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid (envReports D)) :
  ∃ M : Source.{u} D, M.S.Admissible D.E ∧ ∀ r vs, (interp D M).relation r vs ↔ Mo.asStructure.relation r vs

/-- 4.4: the hypothesis of every model-existence theorem is trivial for a positive document. -/
theorem positive_uniform (D) (h) (hp : Positive D) : UniformPolarity (premises D)
theorem uniform_neqs (R : List VE.Formula) (hu : UniformPolarity R) : neqs R = []
theorem neqs_wellFormed (D) (h) (R : List VE.Formula) (hR : ∀ a ∈ R, SignedAtom D a) :
  ∀ a ∈ neqs R, a.WellFormed D.E []                                                -- the forced disequalities are old-language
theorem positive_expandable (D) (h) (hp : Positive D) (S₀ : VE.Structure.{u}) : Expandable D S₀

/-- 4.2: every admissible old-language structure that satisfies the forced disequalities underlies a source model
    of D, and only such a structure does. -/
theorem source_over_any_structure (D) (h) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M
theorem source_over_any_structure_iff (D) (h) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) :
  (∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M) ↔ Expandable D S₀
/-- and with any key that no top-level unit asserts or denies interpreted as empty. -/
theorem unreported_key_free (D) (h) (S₀) (h₀) (he : Expandable D S₀) (k : ReportKey) (hk : k ∉ topKeys D) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ∀ v, ¬ M.J k.act k.sort k.ctx k.content v

/-- 4.4: existence of expansion (not uniqueness), exactly under the forced disequalities. -/
theorem expansion_exists (D) (h) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
  ∃ S', forget (names D) S' = S₀ ∧ S'.Admissible (envReports D) ∧ fol.Sat S' (premises D)
theorem expansion_exists_iff (D) (h) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) :
  (∃ S', forget (names D) S' = S₀ ∧ S'.Admissible (envReports D) ∧ fol.Sat S' (premises D)) ↔ Expandable D S₀

/-- reports_old_language_conservative: the vocabulary extension, unconditional. -/
theorem reports_old_language_conservative (D : ReportDoc) (h : WellFormedReports D = true)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E []) :
  VE.Entails.{u} (envReports D) Γ φ ↔ VE.Entails.{u} D.E Γ φ

/-- Removing signed report premises: they change old-language verdicts by exactly the disequalities they force. -/
theorem reports_no_leak (D) (h) (Γ) (φ) (hΓ) (hφ) (R : List VE.Formula) (hR : ∀ a ∈ R, SignedAtom D a) :
  VE.Entails.{u} (envReports D) (Γ ++ R) φ ↔ VE.Entails.{u} D.E (Γ ++ neqs R) φ
theorem reports_no_leak_uniform (D) (h) (Γ) (φ) (hΓ) (hφ) (R) (hR : ∀ a ∈ R, SignedAtom D a)
    (hu : UniformPolarity R) :
  VE.Entails.{u} (envReports D) (Γ ++ R) φ ↔ VE.Entails.{u} D.E Γ φ

/-- 4.5, each an instance of source_over_any_structure or unreported_key_free, stated for formula contents and
    with the underlying structure fixed. -/
theorem attitude_not_factive (D) (h) (u : Unit) (hu : u ∈ D.units) (hd c : String) (act : Act)
    (q : VE.Formula) (lit : Option String) (hb : u.content = .report hd act c (.formula q) lit)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (hn : ¬ q.denote S₀ []) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ¬ q.denote (interp D M) []
theorem no_closure_under_consequence (D) (h) (hd c s : String) (P Q : VE.Formula)
    (hb : beliefsIn D hd c P (.implies P Q)) (hs : holderSort D hd = some s)
    (hQ : ⟨.believes, s, c, complementId D (.formula Q) none⟩ ∉ topKeys D)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
    ∀ v, ¬ M.J .believes s c (complementId D (.formula Q) none) v
theorem nested_independent (D) (h) (u : Unit) (hu : u ∈ D.units) (h₁ h₂ c c' s₂ : String) (act : Act)
    (q : VE.Formula) (lit : Option String)
    (hb : u.content = .report h₁ act c (.report h₂ .believes c' (.formula q) none) lit)
    (hs₂ : holderSort D h₂ = some s₂)
    (hin : ⟨.believes, s₂, c', complementId D (.formula q) none⟩ ∉ topKeys D)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (hn : ¬ q.denote S₀ []) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
    (∀ v, ¬ M.J .believes s₂ c' (complementId D (.formula q) none) v) ∧ ¬ q.denote (interp D M) []

/-- 4.5, nested contents (draft 7). Stated on the holder-applied signed atom a nested node elaborates to, at the
    node's own holder or evidence context, with the node's polarity explicit; never on the holder-free key. `n` is
    a positive report or assessment node that occurs nested in a top-level unit `u`, and `φ = elab D n` is its atom
    (`J_{act,sort h,c,q}(h)` or `A_{j,a,q}(context a)`). The hypothesis that decides entailment is a top-level unit
    `u'` and its statement, never `topKeys`: the same key at another holder is B₉, and `hn` only locates the claim
    (the conclusion follows from `hb'` alone, as `unitPremise D u'` is in `premises D`). -/
theorem nested_positive_entailed (D) (h) (u u' : Unit) (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true) (hb' : u'.content = n)
    (φ : VE.Formula) (he : elab D n = some φ) :
  VE.Entails.{u} (envReports D) (premises D) φ
/-- The opposite polarity at top level refutes the nested positive node: its atom is false in every model of the
    report premises (B₁₀). -/
theorem nested_positive_refuted (D) (h) (u u' : Unit) (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true) (hb' : u'.content = .negated n)
    (φ : VE.Formula) (he : elab D n = some φ) :
  VE.Entails.{u} (envReports D) (premises D) (.not φ)
/-- A negated nested node `¬n` (D_ω's u1 content) elaborates to `¬φ`: entailed when a top-level unit denies `n`
    (B₁₁), refuted when a top-level unit asserts `n` (`D_ω`: `¬φ` is false in every model of the premises). -/
theorem nested_negated_entailed (D) (h) (u u' : Unit) (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : .negated n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true)
    (hb' : u'.content = .negated n) (φ : VE.Formula) (he : elab D n = some φ) :
  VE.Entails.{u} (envReports D) (premises D) (.not φ)
theorem nested_negated_refuted (D) (h) (u u' : Unit) (hu : u ∈ D.units) (hu' : u' ∈ D.units) (n : Content)
    (hn : .negated n ∈ u.content.nodes) (hr : n.isReport = true ∨ n.isAssessment = true)
    (hb' : u'.content = n) (φ : VE.Formula) (he : elab D n = some φ) :
  VE.Entails.{u} (envReports D) (premises D) φ
/-- The holder-applied atom of a report key `k` at a holder `hd` is free when no positive top-level premise carries
    that atom at a holder co-denoting with `hd` in `S₀`; the hypothesis is on the signed premises, not on `topKeys`
    (`unreported_key_free` is the case with no top-level premise of `k` at all). Proof: the source model of
    `source_over_any_structure`, with `J` at `k` made false at `hd`'s element; positive premises of `k` sit at
    other elements by `hfree`, negated ones are preserved by shrinking `J`. B₉ is the instance with the key in
    `topKeys` at another holder; B₇ and B₁ are the boundary, where `hfree` fails at the asserting unit's holder. -/
theorem holder_atom_free (D) (h) (k : ReportKey) (hk : k ∈ keys D) (hd : String) (hs : holderSort D hd = some k.sort)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀)
    (hfree : ∀ h', .unary (reportName D k) (.const h') ∈ premises D → S₀.constant h' ≠ S₀.constant hd) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
    ∀ v, S₀.constant hd = some v → ¬ M.J k.act k.sort k.ctx k.content v

/-- Identity theorems on canonical objects. A digest or name conclusion is under the occurrence in `D` of both
    objects it compares, which is what the document-local collision check digests (3.4, 13.26): an occurring node
    puts its key in `keys D` or `akeys D`, so each occurrence hypothesis is stronger than the key membership it
    replaces, which the digest of an absent object could witness with one key (B₁₄ to B₁₆). -/
theorem negation_scopes_distinct (D) (h) (hd₁ hd₂ c s : String) (q : VE.Formula)
    (hs₁ : holderSort D hd₁ = some s) (hs₂ : holderSort D hd₂ = some s)
    (ho : Occurs D (.report hd₁ .believes c (.formula (.not q)) none))
    (ho' : Occurs D (.report hd₂ .believes c (.formula q) none)) :
  complementObject D (.formula (.not q)) none ≠ complementObject D (.formula q) none ∧
  reportName D ⟨.believes, s, c, complementId D (.formula (.not q)) none⟩ ≠
    reportName D ⟨.believes, s, c, complementId D (.formula q) none⟩
theorem tense_keys_distinct (D) (h) (c c' : String) (hc : tenseOf D c ≠ tenseOf D c') (s q : String)
    (hk : ⟨.believes, s, c, q⟩ ∈ keys D) (hk' : ⟨.believes, s, c', q⟩ ∈ keys D) :
  reportName D ⟨.believes, s, c, q⟩ ≠ reportName D ⟨.believes, s, c', q⟩
/-- Formula nodes over the author's E, the only bare formula nodes of a tree; a package's statement is canonicalised
    inside its definition node with E_q's id (3.4). -/
theorem content_structural (D) (h) (φ ψ : VE.Formula) :
  (canonicalObject D (.formula φ) = canonicalObject D (.formula ψ) ↔ canonical φ = canonical ψ) ∧
  (Occurs D (.formula φ) → Occurs D (.formula ψ) →
    (contentId D (.formula φ) = contentId D (.formula ψ) ↔ canonical φ = canonical ψ))   -- never ↔ logical equivalence
theorem literal_paraphrase_distinct (D) (h) (b : Content) (l₁ l₂ : Option String) (hw : l₁ ≠ l₂) :
  complementObject D b l₁ ≠ complementObject D b l₂ ∧
  (OccursComplement D b l₁ → OccursComplement D b l₂ → complementId D b l₁ ≠ complementId D b l₂)

/-- Truth combinations over unasserted keys, typed: only elements of the key's sort are constrained. -/
theorem all_truth_combinations (D) (h) (ks : List ReportKey) (hk : ∀ k ∈ ks, k ∉ topKeys D) (f : ReportKey → Bool)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
    ∀ k ∈ ks, ∀ v, M.S.domain k.sort v → (M.J k.act k.sort k.ctx k.content v ↔ f k = true)
theorem all_truth_combinations_assess (D) (h) (ks : List AssessKey) (hk : ∀ k ∈ ks, k ∉ topAKeys D)
    (f : AssessKey → Bool) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
    ∀ k ∈ ks, ∀ v, M.S.domain D.evidence v → (M.A k.j k.a k.content v ↔ f k = true)
```

`topKeys D` are the keys of the top-level units, asserted or denied (a negated unit constrains its key and so
counts); `beliefsIn D hd c P R` says `D` has positive top-level belief units of holder `hd` in context `c` with
formula contents `P` and `R`; `tenseOf` reads the context table; `canonical` is the P5 normal form; `contentCount D`
is the number of nodes of all trees. `Expandable D S₀` is `fol.Sat S₀ (neqs (premises D))`, discharged by
`positive_expandable` for every document without negated units, so a positive document recovers the draft-1
statements verbatim. `topKeys` membership is a hypothesis of the freedom theorems only (`unreported_key_free`,
`no_closure_under_consequence`, `nested_independent`, `all_truth_combinations`): a key is holder-free, so no
theorem concludes that an atom is entailed from a key's membership in `topKeys`; the four nested-content
entailment and refutation theorems take a top-level unit's statement, holder and polarity included, and
`holder_atom_free` takes the signed premises themselves (B₉). The digest and name conclusions of
`negation_scopes_distinct`, `literal_paraphrase_distinct` and `probably_not_scopes_distinct` (9.3) are under the
occurrence of both compared objects in `D`, because the collision check digests occurring objects only (3.4,
13.26; B₁₄ to B₁₆). `all_truth_combinations` and `all_truth_combinations_assess` are the two statements behind
the "different attributions for equivalent payloads", "may and probably independent" and "negation inside versus
outside" fixtures; each fixture names the premise subset `D ▷ U` (10.1: the top-level units it keeps, every
dropped key retained in the vocabulary by a registration unit, no kept unit asserting or denying a queried key,
and `D` a document with no `says` key, so that no registration unit asserts a queried key either and the queried
keys are in `keys` or `akeys` and not in `topKeys` or `topAKeys`; B₁ is the boundary) over which it applies
them.

### 9.3 Theorems: the route, scoped checks, bridges, assessments and the wire

```lean
/-- 4.4: fol_route_acceptance at E_reports with Γ_reports ++ Γ as the document premises, then transported to
    source models by reports_elaboration_faithful_out and reports_elaboration_faithful. -/
theorem reports_route_acceptance (D : ReportDoc) (h : WellFormedReports D = true) (hn : D.lits.Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envReports D) (checkedList D Γ) φ c = true) :
  VE.Entails.{u} (envReports D) (checkedList D Γ) φ ∧
  EntailsString.{u} (envReports D) D.lits (premises D ++ Γ) φ ∧
  (∀ S' : VE.Structure.{u}, StringAdmissible (envReports D) D.lits S' →
     IntendedReports D (restrictJ D S') → fol.Sat S' Γ → φ.denote S' []) ∧
  (∀ M : Source.{u} D, StringAdmissible D.E D.lits M.S → IntendedReports D M →
     fol.Sat (interp D M) Γ → φ.denote (interp D M) [])

/-- The old-language reading: for Γ and φ over E the signed report atoms add exactly the disequalities they force
    (reports_no_leak with R = premises D), so the accepted certificate is one of old-language consequence from
    the literals, those disequalities and Γ. -/
theorem reports_route_acceptance_base (D) (h) (hn) (Γ) (φ) (c) (accepted)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E []) :
  VE.Entails.{u} D.E (literals D.lits ++ neqs (premises D) ++ Γ) φ ∧
  EntailsString.{u} D.E D.lits (neqs (premises D) ++ Γ) φ
/-- A positive document, or one whose old-language premises already entail the disequalities, recovers the
    plain old-language statement. -/
theorem reports_route_acceptance_base_positive (D) (h) (hn) (Γ) (φ) (c) (accepted) (hΓ) (hφ)
    (hp : Positive D ∨ ∀ a ∈ neqs (premises D), VE.Entails.{u} D.E (literals D.lits ++ Γ) a) :
  VE.Entails.{u} D.E (literals D.lits ++ Γ) φ ∧ EntailsString.{u} D.E D.lits Γ φ

theorem reports_route_countermodel {α : Type u} [DecidableEq α] (D) (h) (hn) (Γ : List VE.Formula) (φ : VE.Formula)
    (Mo : VE.FiniteModel α) (valid : Mo.Valid (envReports D)) (hl : literalsValid Mo D.lits = true)
    (checked : VE.countermodelCheck Mo (premises D ++ Γ) φ = true) :
  ¬ EntailsString.{u} (envReports D) D.lits (premises D ++ Γ) φ ∧
  ¬ VE.Entails.{u} (envReports D) (checkedList D Γ) φ ∧
  ∃ M : Source.{u} D, IntendedReports D M ∧ fol.Sat (interp D M) Γ ∧ ¬ φ.denote (interp D M) []

/-- 5.1: at the payloads' environment under its own route background, at every universe. -/
theorem scoped_consequence_sound (D) (h) (s : ScopedCheck) (hs : s ∈ D.scoped) (Eq) (ps)
    (hp : payloadFormulas D s = some (Eq, ps)) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate Eq (background Eq ++ ps) s.conclusion c = true) :
  VE.Entails.{u} Eq (background Eq ++ ps) s.conclusion
theorem scoped_witness_sound {α : Type u} [DecidableEq α] (D) (h) (s) (hs) (Eq) (ps) (hp) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid Eq) (hb : ∀ a ∈ background Eq, a.eval Mo [] = true)
    (hps : ∀ a ∈ ps, a.eval Mo [] = true) (hn : s.conclusion.eval Mo [] = false) :
  ¬ VE.Entails.{u} Eq (background Eq ++ ps) s.conclusion
theorem scoped_not_premise (D) (h) :
  premises D = premises { D with scoped := [] } ∧ envReports D = envReports { D with scoped := [] }
/-- A quoted package's definition premises are local to the check: none is inserted into the document's checked
    list. The literals and the report premises never contain one, so a definition premise is in `checkedList D Γ`
    only when the author wrote it into `Γ` explicitly, as an ordinary premise; locality forbids the automatic
    insertion, not the author's premise. -/
theorem scoped_background_local (D) (h) (Eq : VE.Environment) (ds : List VE.Definitions.Def) (st : Option VE.Formula)
    (hq : Occurs D (.definition Eq ds st)) (Γ : List VE.Formula) :
  ∀ a ∈ VE.Definitions.expand ds, a ∉ literals D.lits ++ premises D ∧ (a ∈ checkedList D Γ → a ∈ Γ)
theorem quoted_inconsistency_local (D) (h) (s) (hs) (Eq) (ps) (hp) (c)
    (acc : VE.Tableau.checkCertificate Eq (background Eq ++ ps) .bottom c = true) :
  (∀ S : VE.Structure.{u}, S.Admissible Eq → fol.Sat S (background Eq) → ¬ fol.Sat S ps) ∧
  ∀ S₀ : VE.Structure.{u}, S₀.Admissible D.E → Expandable D S₀ →
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M

/-- 5.2 -/
theorem bridge_root_is_legacy (D) (h) (leaf : VE.Graph.Claim) (hl : ∃ a u, parseBridge leaf.label = some (.root a u)) :
  BridgeAdmitted D leaf ↔ ∃ a u, parseBridge leaf.label = some (.root a u) ∧
    VE.Route.Admission.QuotedUnit (w2Doc D) a u leaf.formula
  -- w2Doc D: the W2 view of D with each unit's content the elab of its root complement and its kind as in 3.3
  -- (a negated unit's kind is its operand's); a unit named u1.1 is a root target here as it is in W2
theorem bridge_root_parse_frozen (s : String) :
  (∃ a u, parseBridge s = some (.root a u)) ↔ (∃ a u, VE.Route.Admission.parseLabelRaw s = some (.bridge a u))
theorem bridge_nested_label_new (s : String) (hl : ∃ a u n, parseBridge s = some (.nested a u n)) :
  VE.Route.Admission.parseLabelRaw s = none
theorem bridge_formula_exact (D) (h) (leaf) (hb : BridgeAdmitted D leaf) :
  ∃ l, parseBridge leaf.label = some l ∧ bridgeFormula D l.path = some leaf.formula ∧ envAt D l.path = some D.E
theorem bridge_kind_rejected (D) (h) (p : Path)
    (hc : (∃ Eq x, contentAt D p = some (.norm Eq x)) ∨ (∃ Eq x st, contentAt D p = some (.definition Eq x st)) ∨
          envAt D p ≠ some D.E) :
  ¬ ∃ leaf l, BridgeAdmitted D leaf ∧ parseBridge leaf.label = some l ∧ l.path = p
theorem bridge_nested_needs_record (D) (h) (leaf) (a u : String) (n : Nat)
    (hl : parseBridge leaf.label = some (.nested a u n)) (hb : BridgeAdmitted D leaf) :
  ∃ b ∈ D.bridges, b.target = ⟨u, n⟩
theorem bridge_assessment_any_agent (D) (h) (p : Path) (hp : isAssessmentAt D p = true) (a a' : String) :
  HolderOk D p a ↔ HolderOk D p a'
theorem bridge_payload_not_belief (D) (h) (u : Unit) (hu : u ∈ D.units) (h₁ h₂ c c' : String) (act : Act)
    (q : VE.Formula) (lit : Option String)
    (hb : u.content = .report h₁ act c (.report h₂ .believes c' (.formula q) none) lit) :
  bridgeFormula D ⟨u.id, 0⟩ = elab D (.report h₂ .believes c' (.formula q) none) ∧
  bridgeFormula D ⟨u.id, 1⟩ = some q ∧ elab D (.report h₂ .believes c' (.formula q) none) ≠ some q
theorem bridge_through_negation (D) (h) (u : Unit) (hu : u ∈ D.units) (n : Content) (hb : u.content = .negated n) :
  contentAt D ⟨u.id, 0⟩ = complementOf n

/-- 5.3 -/
theorem assessment_open_term (D) (h) (u : Unit) (hu : u ∈ D.units) (j : Judgment) (a : String) (b : Content)
    (hc : u.content = .assessment j a b ∨ u.content = .negated (.assessment j a b)) :
  assessName D ⟨j, a, contentId D b⟩ ∈ openTerms D ∧
  (envReports D).predicates (assessName D ⟨j, a, contentId D b⟩) = some [D.evidence] ∧
  ∃ r, recordOf D a = some r ∧ r.decidedBy ≠ ""
theorem assessment_not_factive (D) (h) (u : Unit) (hu : u ∈ D.units) (j : Judgment) (a : String) (q : VE.Formula)
    (hc : u.content = .assessment j a (.formula q))
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (he : Expandable D S₀) (hn : ¬ q.denote S₀ []) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ¬ q.denote (interp D M) []
theorem may_probably_independent (D) (h) (a q : String) :
  assessName D ⟨.may, a, q⟩ ≠ assessName D ⟨.probably, a, q⟩ ∧
  ∀ (f : Judgment → Bool) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E), Expandable D S₀ →
    (∀ j, ⟨j, a, q⟩ ∉ topAKeys D) →
    ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧
      ∀ j v, M.S.domain D.evidence v → (M.A j a q v ↔ f j = true)
/-- Both `probably` nodes occur, so both formula bodies are digested (9.2's identity convention, 13.26). -/
theorem probably_not_scopes_distinct (D) (h) (a : String) (q : VE.Formula)
    (ho : Occurs D (.assessment .probably a (.formula (.not q))))
    (ho' : Occurs D (.assessment .probably a (.formula q))) :
  canonicalObject D (.formula (.not q)) ≠ canonicalObject D (.formula q) ∧
  assessName D ⟨.probably, a, contentId D (.formula (.not q))⟩ ≠ assessName D ⟨.probably, a, contentId D (.formula q)⟩

/-- 9.4: the reports gate is a function around the frozen classifier, never a change to it. -/
def reportsGate (ps : List String) : Except String Unit
  -- requires "reports@0" ∈ ps, VE.Route.Gate.classify (ps.erase "reports@0") = .ok .fol, and none of
  -- "norms@0", "definitions@0", "data@0" in ps; diagnostics as in section 8
theorem reports_gate_sound (ps : List String) (h : reportsGate ps = .ok ()) :
  "reports@0" ∈ ps ∧ VE.Route.Gate.classify (ps.erase "reports@0") = .ok .fol ∧
  "norms@0" ∉ ps ∧ "definitions@0" ∉ ps ∧ "data@0" ∉ ps

/-- 9.4: the wire. The admitted record carries the decoded document, the decoded wire nodes, the graph, the
    report and the recomputed envelope. -/
structure ReportsAdmitted where
  D : ReportDoc
  wires : List VE.Route.Admission.WireNode
  graph : VE.Graph.Graph
  report : VE.Graph.Report
  envelope : String × String                 -- (environment_id(E), document_id(D)), recomputed from the raw input

/-- The leaf rule under the profile: report and assessment labels carry exactly the regenerated signed premise of
    their unit; bridge labels satisfy BridgeAdmitted (root ones coincide with the legacy rule,
    bridge_root_is_legacy); every other label is the unchanged LeafAdmitted on the W2 view. -/
def ReportsLeafAdmitted (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Prop :=
  (∃ u ∈ D.units, w.claim.label = "report:" ++ u.id ∧ unitPremise D u = some w.claim.formula ∧
     (u.content.isReport = true ∨ ∃ n, u.content = .negated n ∧ n.isReport = true)) ∨
  (∃ u ∈ D.units, w.claim.label = "assessment:" ++ u.id ∧ unitPremise D u = some w.claim.formula ∧
     (u.content.isAssessment = true ∨ ∃ n, u.content = .negated n ∧ n.isAssessment = true)) ∨
  (BridgeAdmitted D w.claim ∧ (w.unit = none ∨ ∃ l, parseBridge w.claim.label = some l ∧ w.unit = some l.path.unit)) ∨
  VE.Route.Admission.LeafAdmitted (w2Doc D) w
def ReportsNodeAdmitted (D : ReportDoc) (w : VE.Route.Admission.WireNode) : Prop :=
  match w.deduction with
  | some _ => w.claim.label = "asserted" ∧ ∀ u, w.unit = some u → VE.Route.Admission.AssertedUnit (w2Doc D) u w.claim.formula
  | none => ReportsLeafAdmitted D w

/-- A successful reports `admission` answer is exactly the encoding of an admission whose inner bindings equal
    the recomputed digests, whose envelope equals the recomputed (environment_id, document_id), and whose
    regenerated E_reports, premises, open terms and bridge formulas are the ones this specification defines; the
    graph is checked by the unchanged VE.Graph.checkTableau. -/
theorem Run.reports_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : Run.usesReportsPath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.ReportsAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
/-- Mirrors VE.Route.Admission.admit_report_sound conjunct for conjunct, with the envelope added. -/
theorem reports_admission_sound (profiles : List String) (environment : Json) (j : Json) (res : ReportsAdmitted)
    (h : admissionReports profiles environment j = .ok res) :
  WellFormedReports res.D = true ∧
  res.envelope = (VE.Route.Wire.environmentId profiles (canonical environment), documentId res.D) ∧
  res.graph.nodes = res.wires.map VE.Route.Admission.WireNode.toNode ∧
  VE.Graph.Acyclic res.graph ∧ (res.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
  res.report.root.name = res.graph.root ∧
  VE.Graph.SoundReport.{u} (envReports res.D) res.graph res.report ∧
  (∀ w ∈ res.wires, ReportsNodeAdmitted res.D w) ∧
  (∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
     w.claim = leaf ∧ w.deduction = none ∧ ReportsLeafAdmitted res.D w) ∧
  VE.Route.Admission.CitationsClosed (w2Doc res.D) res.report ∧ VE.Route.Admission.ChoicesCompatible res.report
/-- As VE.Route.Admission.admit_labels_decoded: every assumption of the report is a decoded leaf with exactly its
    decoded label, name and formula. -/
theorem reports_labels_decoded (profiles : List String) (environment : Json) (j : Json) (res : ReportsAdmitted)
    (h : admissionReports profiles environment j = .ok res) :
  ∀ leaf ∈ res.report.assumptions, ∃ w ∈ res.wires,
    w.claim.label = leaf.label ∧ w.claim.name = leaf.name ∧ w.claim.formula = leaf.formula
```

`ReportsAdmissionAnswer` is P0's admission answer with the reports decoder, the envelope `{"environment_id",
"document_id"}` equal to the recomputed pair, `report:*`, `assessment:*` and bridge leaves admitted by
`ReportsLeafAdmitted`, every other label by the unchanged `LeafAdmitted`, and the report consequence stated over
`literals ++ premises D ++ Γ`. `canonical environment` is `VE.Route.Wire.canonicalEnvironmentJson` of the raw
environment, as in `VE.Norms.Replay.outerBound`.

### 9.4 The executable `ve_reports_route`

`lean/.lake/build/bin/ve_reports_route <cases.json>`, root `ReportsMain.lean`, a new Lake target; `Run.main` is the
executable root and no frozen file changes. On raw input it runs the frozen envelope check and then the **reports
gate**: the frozen `VE.Route.Gate.registry` does not list `reports@0` and `classify` rejects every unknown
profile, so the gate requires `reports@0` in the sorted, unique profile list, runs the frozen `classify` on the
list minus `reports@0`, requires the answer `.fol` (which makes `relational-fol@0` present and excludes
`closure@0`, `nary@0` and `order@0` with the frozen diagnostics), and rejects `norms@0`, `definitions@0` and
`data@0` (`UnsupportedProfile: reports@0 with <profile> layers`, 11.3). The gate is a new function around the
frozen classifier, not a change to it (`reports_gate_sound`: a list the gate accepts is, minus `reports@0`, one
the frozen classifier classifies as `.fol`). It then decodes the environment with its `reports` block through the
P0 vocabulary decoder plus a strict reports decoder (unknown fields rejected; the original complete environment
hashed), decodes contexts, assessments, units with their content trees (recursively validating quoted norm and
definition content through the unchanged W1 and W3 decoders under their pinned environments), bridges and scoped
checks, runs `WellFormedReports`, regenerates `E_reports`, `Γ_reports`, the open-term names and records and every
bridge formula, recomputes the envelope `(environment_id(E), document_id(D))`, validates every binding against
the recomputed values, and delegates every checker call to the unchanged tableau, finite-model and graph
functions. Case kinds:

| Kind | Extra input | Output |
|---|---|---|
| `reports-elaborate` | none | `environment_reports` (canonical), `keys` (each with its generated name and source key), `premises` (labelled `report:<unit>` / `assessment:<unit>`, signed), `open_terms`, `bridge_formulas` (per declared record), `envelope`, `warnings` |
| `reports-scoped` | per check: `certificate` or `witness` | FOLLOWS / DOES NOT FOLLOW / PAYLOADS INCONSISTENT / UNKNOWN with detail, the check's environment id and its background |
| `reports-certificate` | `premises`, `conclusion`, `certificate` bound to `literals ++ Γ_reports ++ premises` and carrying the envelope | `valid` (false on any binding or envelope mismatch), `environment_reports_id`, `envelope`, `bindings` |
| `reports-countermodel` | `premises`, `conclusion`, finite model over `E_reports` | `refutes`, the decoded source-model rendering |
| `admission` | W2 document with report, assessment and negated units, bridges, scoped checks and graph | `admitted`, `report`, `report_id`, `envelope`, `kinds`, `residual` |

P0 cases without reports constructs delegate unchanged to `VE.Route.Run.runCase`; malformed reports inputs never
fall back after a failed reports decode.

### 9.5 What is not claimed

No theorem about the English surface: `reports_parse_unique` (P1) and `reports_print_parse` (P4) over the
templates of 2.1 are item-4 obligations in `lean/VE/English/Reports*.lean`, stated against the reports grammar and
its manifest; the existing Lean English model covers the v0 unary and binary core only (INTEGRATION-GAPS.md), and
tests alone do not discharge them. No claim that `IntendedReports` matches an author's or a source's intent: that
is this statement review, W8's fidelity gate and the blind whole-span review. No theorem about assessors,
criteria or the truth of any content. No modal theorem. No completeness of scoped checks beyond the tableau's.
No theorem about adoption or import beyond provenance. No theorem about `Layer.comp` with the norms,
definitions or data chains (11.3). No theorem about `and`, `or` or quantifiers over report statements: they
have no wording, no wire form and no `elab` case (4.3). No theorem asserts SHA-256 injectivity: identity
theorems are on canonical objects, and digests follow only for objects a well-formed document digests, under an
explicit occurrence hypothesis for each; nothing is stated about the digest of an object the document does not
digest, which the collision check never computes (3.4, B₁₄ to B₁₆).

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind,
from Lean (`tests/test_reports*.py`, the `reports` conformance family). Section 10.1 fixes the environment,
contexts, assessments and documents; 10.2 states what each must produce, so that a reviewer derives the
expectation from the definitions before reading it.

### 10.1 Definitions

Environment `E₀`: sorts `organisation`, `text`, `service`, `model`, `evidence`; `reports.holders = [organisation,
text]`, `reports.evidence = evidence`; constants `anthropic : organisation`, `the_article : text`, `the_team :
organisation`, `service : service`, `claude : model`, `e1 : evidence`; unary predicates `safe(service)`,
`helpful(model)` ("{0} is helpful"), `was_helpful(model)` ("{0} was helpful"), `human(model)`,
`reviewed(service)`; the binary predicate `publishes(organisation, service)` ("{0} publishes the results of
{1}"); profiles `[relational-fol@0, reports@0]`; no literals. Contexts: `c1` (present, "the constitution"), `c2`
(past, "the article of 16 September", tag `sept16`), `c3` (present, "the article"). Assessment `a1`: context
`e1`, `decided_by: unresolved_decider`, no criteria, factors ["review status"], jurisdiction `news_desk`, version
1. Every document below partitions a synthetic source whose bytes are the sentences shown; graph nodes are named
after their units; `Γ_author` is empty unless stated. Paths are written `(unit, path)`; a bare unit is its root.

**Premise subsets that keep the vocabulary.** `D ▷ U`, for a list `U` of top-level units of `D`, is the document
whose top-level units are those of `U` in `D`'s order, followed by one *registration unit* for every unit of `D`
not in `U`: `The article says that R.` (says, `the_article`, `c3`), where `R` is that unit's report or
assessment wording (its operand's for a negated unit: a negated node has no key of its own, 1.1); two omitted
units with one wording, such as `D_γ`'s u2 and u3, give two identical registration units. `Γ_reports(D ▷ U)` is
the signed premises of `U` followed by one positive registration atom `reports__says__i(the_article)` per
registration unit. The construction is defined for every document; the three properties below are stated for,
and hold on, the fragment of documents with **no `says` key** (no key of `keys D`, top-level or nested, has act
`says`), which `D_γ`, `D_ε`, `D_η` and `D_μ` occupy, and they fail outside it (B₁, B₂). On that fragment every
registration key `(says, text, c3, ·)` is new to the document, so: (i) a registration unit puts the dropped
unit's key, and every key nested in it, into `keys (D ▷ U)` or `akeys (D ▷ U)` without asserting or denying it,
as `D_β`'s u3 does for the belief-in-safe key; (ii) registration does not by itself remove a dropped key from
`topKeys (D ▷ U)` or `topAKeys (D ▷ U)`: a dropped key is outside them exactly when no unit of `U` asserts or
denies it, since a kept unit that shares the key keeps it asserted (over `D_γ ▷ [u2]`, u3's key is u2's and stays
in `topKeys`), and `D ▷ []` asserts and denies no key of `D`; (iii) per-act numbering (1.5) gives every queried
predicate the name it has in `D`, and `E_reports(D ▷ U)` is `E_reports(D)` plus the registration predicates.
Outside the fragment a registration unit can reproduce a dropped `says` key of `the_article` in `c3` and assert
it (B₁: over `B₁ ▷ []`, u2's key is a registration key and stays in `topKeys` although `U` is empty, so (i) and
(ii) fail), and a nested `says` key can be renumbered among the registration keys, so (iii) fails (B₂: the
nested key sorts after the registration key, and its name changes from `reports__says__1` to
`reports__says__2`). Every
independence expectation of 10.2 names the `D ▷ U` it is over, is over its premises and no other, is over a
document with no `says` key, and queries only keys that no unit of that `U` asserts or denies, so each queried
key is in `keys (D ▷ U)` or `akeys (D ▷ U)` and not in `topKeys (D ▷ U)` or `topAKeys (D ▷ U)`, which is the
hypothesis of `unreported_key_free`, `all_truth_combinations` and `all_truth_combinations_assess`. A document
with a `says` key states its independence claims over itself or over an explicitly listed sub-document; where
10.3 applies `▷` to such a document it is to exhibit the boundary, and every key it queries is checked against
`topKeys` directly.

```text
D_α   u1: The article says that the service is safe.                          says, the_article, c3, safe(service)
D_β   u1: Anthropic believes that the service is reviewed.                    believes, anthropic, c1, reviewed(service)
      u2: Anthropic believes that if the service is reviewed then the service is safe.
      u3: The article says that Anthropic believes that the service is safe.  says, the_article, c3,
          ⟨believes, anthropic, c1, safe(service)⟩   (registers the belief-in-safe key by nesting; asserts nothing of it)
      s1: scoped check, payloads [u1, u2], conclusion safe(service), certificate supplied (E_q = E₀, background [])
D_γ   u1: Anthropic believes that the service is safe and the service is safe.  content safe ∧ safe
      u2: Anthropic believes that the service is safe.                           content safe
      u3: Anthropic believes that the service is safe.   (second occurrence, same key as u2, distinct span)
D_δ   u1: The team intends to publish the results of the service.             intends, the_team, c1, publishes(the_team, service)
D_ε   u1: Anthropic believes that it is not the case that Claude is human.    believes, anthropic, c1, ¬human(claude)
      u2: It is not the case that Anthropic believes that Claude is human.    negated ⟨believes, anthropic, c1, human(claude)⟩
D_ζ   u1: The article says that Anthropic believes that Claude is helpful.    says, the_article, c3, ⟨believes, anthropic, c1, helpful(claude)⟩
      graph G₁: leaf L1 labelled bridge:accepts(the_article,u1), formula J_{believes,c1,helpful}(anthropic)
      graph G₂: leaf L2 labelled bridge:accepts_at(anthropic,u1,1), formula helpful(claude), record b1 = {unit u1, path 1}
      graph G₃: leaf L3 labelled bridge:accepts_at(anthropic,u1,1) with no record
      graph G₄: leaf L4 labelled bridge:accepts_at(the_article,u1,1), formula helpful(claude), record b1
      graph G₅: leaf L5 labelled bridge:accepts(anthropic,u1.1), formula helpful(claude)   (legacy label, no unit u1.1)
D_η   u1: Anthropic believed that Claude was helpful.                         believes, anthropic, c2, was_helpful(claude)
      u2: Anthropic believes that Claude is helpful.                          believes, anthropic, c1, helpful(claude)
D_θ   u1: The article says that the service is safe.
      u2: The article says that it is not the case that the service is safe.
      s1: scoped check, payloads [u1, u2], conclusion ⊥, certificate supplied
      u3: The article says that the service is safe and it is not the case that the service is safe.
D_ι   D_α with graph G: leaf L labelled asserted, unit u1, formula safe(service); root R = L
      G′: L labelled bridge:accepts(the_article,u1); G″: G′ with the label stripped on the wire
D_κ   u1: The article says that: [quoted W1 block, pinned E_q with regulated enter_permitted; rule 1 forbids,
          rule 2 permits, no precedence, both live]     kind attributed(the_article, says, norm)
      graph: leaf labelled bridge:accepts(the_article,u1) with formula ∀x. ¬enter_permitted(x)
      Γ_author: enter_permitted(a)   (a name outside E₀)
D_λ   u1: The article says that, under its definitions, the service is reviewed.
          [quoted W3 package under E_q = E₀'s sorts and constants with definitions@0 defining safe(x) as
          reviewed(x); statement reviewed(service) over E_q]        kind attributed(the_article, says, definition)
      s1: scoped check, payloads [(u1, 1)], conclusion safe(service), certificate C bound to
          E_q, Background(E_q) ++ [reviewed(service)] (Background(E_q) = the definition premise, no literals)
      Γ_author: reviewed(service); the same certificate C submitted outside for Γ_author ⊢ safe(service)
      graph: leaf labelled bridge:accepts_at(the_article,u1,1), formula reviewed(service), record {unit u1, path 1}
D_μ   u1: According to the stated assessment, the service may be safe.        may, a1, safe(service)
      u2: According to the stated assessment, the service is probably safe.   probably, a1, safe(service)
      u3: According to the stated assessment, it is probably the case that it is not the case that the service is safe.
      a1′: a1 with the decided_by field removed
      D_μ′: u4 alone: It is not the case that, according to the stated assessment, it is probably the case that
            the service is safe.                                                negated ⟨probably, a1, safe(service)⟩
      D_μ″: u2 and u4 together
D_ν   E₀ plus a holder constant assessment : organisation with verbalisation "the stated assessment"
      input: According to the stated assessment, the service may be safe.
      input: Anthropic says that, according to the stated assessment, the service may be safe.
D_ξ   u1 of D_η; manifest M₁ = (E₀ id, c2, no assessment, profiles, no choices); M₂ = M₁ with c2's tense present
D_ο   D_δ with norms@0 also enabled and no rule; D_ο′: D_δ with data@0 also enabled
D_π   D_α with Γ_author = [reviewed(service) → safe(service), reviewed(service)]; conclusion safe(service);
      D_π′: D_π plus u2: It is not the case that the article says that the service is safe.
            negated ⟨says, the_article, c3, safe(service)⟩ (the key of u1)
D_ρ   D_γ's u2 and u3; scoped check s1 with payloads [u2, u3], conclusion safe(service)
D_σ   u1: The Fed pledged to lower inflation.    (report block with act pledged)
      u2: kind attributed(the_fed, promised, asserted) with no content
D_τ   u1: Anthropic wants Claude to be helpful.                    wants, anthropic, c1, helpful(claude)
      u2: The team wants to publish the results of the service.   wants, the_team, c1, publishes(the_team, service)
      u3: The peoples reaffirmed their faith in fundamental human rights.   unformalised(noun_complement)
      u4: Warsh pledged, "clearly and at sufficient speed".                 unformalised(fragment_complement)
D_υ   u1: Anthropic believes that every model is helpful.                    content ∀x:model. helpful(x)
      u2: Every model is such that Anthropic believes that it is helpful.    (input only)
D_φ   D_ζ with a certificate for Γ_author = [J_{says,…}(the_article)] ⊢ J_{says,…}(the_article), carrying the
      envelope; then each of: c3's tense changed; the_article replaced by anthropic; helpful replaced by human;
      literal words added; a1-style record attached; a reading choice recorded; E₀'s legend for helpful changed;
      and D_α with its certificate for Γ ⊢ J_{says,c3,safe}(the_article), then safe replaced by reviewed
      (the sole key's payload: E_reports and Γ_reports byte-identical)
D_χ   1,000 generated report documents (depth ≤ 4, acts and judgments mixed, negation at random positions,
      nested to depth 3)
D_ψ   every existing W2 document fixture, (a) without reports@0; (b) with reports@0 added and no reports block;
      (c) with reports@0 added, a minimal reports block (holders = [the fixture's first declared sort], evidence
      = that sort) and no report content
D_ω   u1: The article says that it is not the case that Anthropic believes that Claude is helpful.
          says, the_article, c3, ⟨¬⟨believes, anthropic, c1, helpful(claude)⟩⟩
      u2: Anthropic believes that Claude is helpful.                          believes, anthropic, c1, helpful(claude)
      input: Anthropic believes that Claude is helpful and the article says that Claude is helpful.
      input: It is not the case that it is not the case that Anthropic believes that Claude is helpful.
      D_ω′: u1: It is not the case that the team believes that the service is safe.
                                                                              negated ⟨believes, the_team, c1, safe(service)⟩
            u2: Anthropic believes that the service is safe.                  believes, anthropic, c1, safe(service)
```

### 10.2 Expected results

- **(α) Not factive.** `E_reports = E₀ + reports__says__1(text)`; `Γ = [reports__says__1(the_article)]` labelled
  `report:u1`; status CHECKED; residual `reports: says 1`. The finite model with `safe` empty and
  `reports__says__1 = {the_article}` is valid, satisfies `Γ`, refutes `safe(service)`; `reports-countermodel`
  reports `refutes` and renders "the article says the service is safe; the service is not safe". A certificate
  for `Γ ⊢ safe(service)` does not exist and a forged one fails to replay.
- **(β) Not closed; scoped consequence.** Three top-level keys: `(believes, organisation, c1, reviewed)`,
  `(believes, organisation, c1, reviewed → safe)` and u3's `(says, text, c3, ⟨believes …⟩)`; the belief-in-safe
  key `(believes, organisation, c1, safe)` is in `keys D_β` (it occurs as u3's content, so `E_reports` has its
  predicate) and not in `topKeys D_β`. Over the premises of `D_β`, the model with the three top-level atoms true,
  the belief-in-safe atom false and `safe` empty is valid and satisfies `Γ` (`unreported_key_free`); no
  certificate for `Γ ⊢ safe(service)` or for `Γ ⊢ ` the belief-in-safe atom replays. The scoped check `s1` is
  FOLLOWS with its certificate at `E₀` with empty background; the report line reads "the service is safe follows
  from the reported contents u1, u2"; `Γ` and `E_reports` are unchanged by `s1` (`scoped_not_premise`).
- **(γ) Structural content.** u1 and u2 have different canonical content objects, hence different content ids
  and different keys (`content_structural`); u2 and u3 share one key and one atom; `Γ` has three entries with
  two distinct formulas, and over `D_γ` itself the model with both atoms true and `safe` empty is valid and
  satisfies `Γ`. Independence over `D_γ ▷ [u1]` (u2 and u3 omitted, so two identical registration units for
  their shared key; `Γ = [u1's atom, reports__says__1(the_article), reports__says__1(the_article)]`, three
  entries with two distinct formulas): the model with the u1 atom true and the u2/u3 atom false is valid and
  satisfies `Γ`, so no certificate for the u2/u3 atom replays there; over `D_γ ▷ [u2, u3]` (u1 omitted, one
  registration unit; `Γ = [u2's atom, u3's atom, reports__says__1(the_article)]`) the model with the u2/u3 atom
  true and the u1 atom false likewise, so none for the u1 atom replays (`all_truth_combinations`: in each subset
  the queried key is asserted or denied by no kept unit and, `D_γ` having no `says` key, by no registration unit
  (10.1), so it is not in `topKeys`; `D_γ ▷ [u2]` would not do for u3's key, which u2 keeps asserted). The residual of `D_γ` counts two report keys and three occurrences.
- **(δ) Intention.** `Γ = [reports__intends__1(the_team)]`; the model with `publishes` empty satisfies `Γ`; no
  `required` symbol exists (`UnknownSymbol` on a `Γ` naming one); paraphrase: "neither that the team publishes
  the results of the service, nor an obligation, nor a promise follows".
- **(ε) Negation scopes.** u2 is a negated unit: `Γ = [reports__believes__i(anthropic),
  ¬reports__believes__j(anthropic)]` with `{i, j} = {1, 2}` in the key order of the two content ids (the fixture
  reads the names from the key table). Two different keys and names (`negation_scopes_distinct`: both belief
  nodes occur, u1's and u2's operand, so its occurrence hypotheses hold; B₁₅ is u1 alone); `neqs Γ = []` (two
  predicates, no shared one), so over `D_ε` itself the model with u1's atom true and u2's key atom false is valid
  and satisfies `Γ` (the premise-set model exists). Independence over `D_ε ▷ []` (both keys registered: `The
  article says that Anthropic believes that it is not the case that Claude is human.` and `The article says that
  Anthropic believes that Claude is human.`; `E_reports` keeps both `believes` predicates with their names; `Γ`
  is the two positive `says` atoms): all four truth combinations of the two atoms at `anthropic` are realised
  (`all_truth_combinations` with `ks` the two keys). Over `D_ε ▷ [u1]` the model with u1's atom true and u2's
  key atom true is valid and satisfies `Γ`, so no certificate for u2's premise `¬reports__believes__j(anthropic)`
  replays; over `D_ε ▷ [u2]` the model with u2's key atom false and u1's atom false likewise, so none for u1's
  atom replays. The paraphrases differ as in 2.1; u2's status line is the "denied" form of 7.2.
- **(ζ) Nested and bridges.** One top-level key; `E_reports` also contains the inner key's predicate
  (`reports__believes__1(organisation)`) because it occurs as content, but no premise mentions it. Model with the
  outer atom true, the inner atom false and `helpful` empty: valid, satisfies `Γ`. `G₁` admitted: `L1` is a
  root-path bridge with the inner belief atom (legacy `QuotedUnit` on the W2 view, `bridge_root_is_legacy`);
  `G₂` admitted: `L2` assumes `helpful(claude)`, listed in the assumptions with its label and record; `G₃`
  rejected `MissingBridgeRecord: u1, 1`; `G₄` rejected `BridgeHolder: u1, 1` (the holder at `(u1, 1)` is
  anthropic); `G₅` rejected by the unchanged legacy rule (`QuotedUnit` finds no unit `u1.1`), never read as a
  nested target. Under `G₂` a certificate for `helpful(claude)` replays with `L2` as its only assumption; nothing
  certifies the inner belief atom from `L2`.
- **(η) Tense.** Two keys, two predicates (`tense_keys_distinct`), `E_reports` has `reports__believes__1` (c1,
  present) and `reports__believes__2` (c2, past) in key order; over `D_η` itself both atoms are premises, so the
  independence check is over `D_η ▷ [u1]` (u2's key registered: `The article says that Anthropic believes that
  Claude is helpful.`; `Γ = [reports__believes__2(anthropic), reports__says__1(the_article)]`): the model with
  the past atom true and the present atom `reports__believes__1(anthropic)` false is valid and satisfies `Γ`, so
  no certificate for the present atom replays there; over `D_η ▷ [u2]` (u1's key registered) the model with the
  present atom true and the past atom false likewise, so none for the past atom replays. The renderings differ in
  verb form and in context; the round trip of each preserves its context.
- **(θ) Inconsistent quotation is local.** `Γ` has two atoms with different keys; the premise-set model exists (P0
  line: model id); `s1` reports PAYLOADS INCONSISTENT with its certificate; u3's content is one contradiction as
  content: its key exists, its atom is a premise, the outer model still exists; no dependent outer certificate is
  `vacuous`.
- **(ι) Bridge required; tamper.** `G` rejected: `AdmissionError: quoted content of unit u1 is used without a
  bridge leaf` (unchanged text); `G′` admitted with `L` in the assumptions labelled `bridge:accepts(the_article,u1)`
  and in the residual as a bridge leaf; `G″` rejected, and its wire hash differs from `G′`'s.
- **(κ) Quoted norms.** The block validates under `E_q`; the local W1 check reports CONFLICT "among the quoted
  rules" with the witness; no `layer:norms:*` premise, no `background:profile` premise exists outside; the bridge
  leaf is rejected `BridgeKindMismatch: u1`; `Γ_author`'s `enter_permitted(a)` is `UnknownSymbol` under `E₀`.
- **(λ) Quoted definitions.** The package validates under `E_q`; `safe` in `E₀` keeps its own declaration; the
  definition premise `∀x. safe(x) ↔ reviewed(x)` is in `Background(E_q)` and nowhere in `checkedList D_λ
  Γ_author`: not among the literals or the report premises, and `Γ_author = [reviewed(service)]` does not contain
  it (`scoped_background_local`: it would be checked outside only if the author wrote it into `Γ_author`, as an
  ordinary premise over `E₀`); `s1` is FOLLOWS: `C` replays at `E_q` against `Background(E_q) ++
  [reviewed(service)]` (`scoped_consequence_sound`), the report line reads "the service is safe follows from the
  reported contents (u1, 1)"; the same `C` submitted outside for `Γ_author ⊢ safe(service)` fails to replay (its
  binding names `E_q` and the definition premise, neither of which exists at `E_reports`); the bridge leaf is
  rejected `BridgeKindMismatch: u1, 1` (the statement is over `E_q`).
- **(μ) Assessments.** `D_μ`: three assessment units, keys `(may, a1, safe)`, `(probably, a1, safe)`,
  `(probably, a1, ¬safe)`; every unit OPEN; three open terms `reports__may__1`, `reports__probably__1`,
  `reports__probably__2` (the two `probably` names in key order of their content ids) with `decided_by:
  unresolved_decider`, arguments `[evidence]`; residual `assessments: unresolved_decider 3`. Independence over
  `D_μ ▷ []` (the three keys registered: `The article says that, according to the stated assessment, the service
  may be safe.` and likewise for u2 and u3, the inner "the stated assessment" bound to `a1` as in ν; `E_reports`
  keeps the three assessment predicates with their names and the residual its three open terms; `Γ` is the three
  positive `says` atoms): all eight truth combinations of the three atoms at `e1` are realised
  (`all_truth_combinations_assess` with `ks` the three keys; `may_probably_independent` for the first two). Over
  `D_μ ▷ [u1]` the model with u1's atom true, u2's and u3's atoms false and `safe` empty is valid and satisfies
  `Γ`, so no certificate for u2's atom, u3's atom or `safe(service)` replays; over `D_μ ▷ [u2]` the model with
  u2's atom true, u1's and u3's atoms false and `safe` empty likewise, so none for u1's atom, u3's atom or
  `safe(service)` replays. `a1′` is `InvalidInput: assessment a1 needs decided_by`. `D_μ′`: `Γ =
  [¬reports__probably__1(e1)]`, OPEN, the "denied" status line, `neqs Γ = []`, the premise-set model exists. `D_μ″`: `Γ = [reports__probably__1(e1),
  ¬reports__probably__1(e1)]`, `neqs Γ = [¬(e1 = e1)]`; the P0 line reports INCONSISTENT with its certificate at
  `E_reports`, and `reports_route_acceptance_base` gives the same line at `E₀` from `neqs`; every dependent
  certificate is `vacuous`, and a certificate for `Γ ⊢ safe(service)` replays there too, `vacuous`: an
  inconsistent premise set is outside the fragment of every independence claim of 4.5 and 5.3. Over `D_μ` itself
  both `May` and `Probably` of `safe` are premises, which is why 5.3's independence is stated over `D_μ ▷ [u1]`
  and `D_μ ▷ [u2]`. u4's atom is the negation of u2's atom, while u3's atom is a different key with a different
  name (`probably_not_scopes_distinct`: the `probably` nodes over `safe(service)` and over `¬safe(service)` both
  occur, u2 and u3, so its occurrence hypotheses hold; B₁₆ is u3 alone).
- **(ν) Parser binding.** The environment is rejected: `InvalidInput: holder verbalisation reserved`. With a
  holder verbalised "the assessment desk" instead, the first input parses to `May(a1, safe)` only (one derivation);
  the second parses to `says(anthropic, c1, May(a1, safe))`, kind `attributed(anthropic, says, hedged(could,
  asserted))`; there is no derivation with a `says` holder named by the phrase.
- **(ξ) Round trip.** `print(parse(s, M₁)) = s` and `parse(print(A), M₁) = A`; parsing the same sentence under
  `M₂` is `ManifestMismatch: u1` (the verb form disagrees with the context's tense); rendering u1 without a manifest
  is refused; the inspector shows `c2`'s record beside the sentence.
- **(ο) Desire is not duty; the gate.** `D_ο` is rejected by the reports gate, `UnsupportedProfile: reports@0
  with norms@0 layers`, before any unit is read; `D_ο′` likewise with `data@0` (11.3). Under `D_δ` alone,
  `required` and `permitted` predicates, if declared, are base predicates decided by nothing; a `Γ` naming `must`
  is not a wording.
- **(π) Conservativity.** The certificate for `safe(service)` from `Γ_author` replays under `E_reports` and under
  `E₀` (`reports_old_language_conservative`); `D_π` is positive, so `neqs Γ_reports = []` and the report atom's
  presence changes no old-language verdict (`reports_no_leak_uniform`, `reports_route_acceptance_base_positive`).
  `D_π′`: `Γ_reports = [reports__says__1(the_article), ¬reports__says__1(the_article)]`, `neqs = [¬(the_article =
  the_article)]`; the P0 line reports INCONSISTENT with its certificate and the `safe(service)` certificate is
  `vacuous`, at `E_reports` and, through `neqs`, at `E₀`.
- **(ρ) Occurrences.** Payloads `[u2, u3]` are two payloads with one formula; the scoped check FOLLOWS trivially;
  the report line lists both occurrences; the key count is one.
- **(σ) Unreviewed acts.** u1 is `UnsupportedAct: pledged (reports@0 admits says, believes, wants, intends)`; u2
  carries no report content, so 4.1 step 2 does not check its act: it is LABELLED as today with the warning line
  "unreviewed act promised in u2"; neither adds a key.
- **(τ) Complements.** u1's content is `helpful(claude)` with Claude as subject; u2's is `publishes(the_team,
  service)` with the team as the intending holder and as the embedded subject (1.3); u3 is UNFORMALISED
  `noun_complement` and u4 `fragment_complement`, each with its warning line; none of u3, u4 adds a key.
- **(υ) Scope.** u1 admitted with the quantifier inside the content; u2 rejected `OpenComplement: u2` with the
  rewrite "Anthropic believes that every model is helpful" and the paraphrase that the two differ.
- **(φ) Identity.** Every listed change alters `document_id(D)` (and some also `environment_id(E_reports)` or a
  content id); the certificate's envelope no longer matches the recomputed one, so `valid` is false under every
  changed document, including the two whose `E_reports` and `Γ_reports` are byte-identical to the original (c3's
  tense; `safe` replaced by `reviewed` in `D_α`): there the inner binding still matches and only the envelope
  fails, which is the case draft 1 missed. The unchanged document replays.
- **(χ) Differential.** Python's `E_reports`, keys, signed premises, open terms, bridge formulas and envelope
  equal Lean's on every generated document (regression evidence, not proof); Rust evaluates the elaborated
  premises and agrees on every verdict with `untrusted: true`.
- **(ψ) Frozen fixtures.** (a) byte-identical outputs, identities and reports; (b) rejected,
  `UnsupportedProfile: reports@0 needs a reports block` (3.1); (c) identical outputs except the identities, where
  the profile list and the block change `environment_id` as any environment change does, and the envelope, which
  is new; the reports residual lines are empty and `Γ_reports = []`.
- **(ω) Nested negation; deferred connectives; forced disequalities.** `D_ω`: u1's key is `(says, text, c3,
  ⟨¬⟨believes, anthropic, c1, helpful⟩⟩)`; its complement object is `{"negated": …}`; `E_reports` has the inner
  key's predicate (it occurs as content) and u2 asserts it; `Γ = [reports__says__1(the_article),
  reports__believes__1(anthropic)]`, positive, consistent; u1's content, the negated node, elaborates to
  `¬reports__believes__1(anthropic)` and u2's premise is its operand's atom at the same holder, so the content is
  false in every model of `Γ` (`nested_negated_refuted` at u1's nested negated node with `u′ = u2`): a
  certificate for `Γ ⊢ reports__believes__1(anthropic)` replays from u2's premise, and the situation line of 2.3
  for u1 shows any model of `Γ` as one in which u1's report holds and its content is false (B₁₁ is the same u1
  with u2 denying instead of asserting, where the content is entailed; B₁₁′ is u1 alone, where it is free); u1's
  paraphrase is the 2.1 row; u1's kind is
  `attributed(the_article, says, attributed(anthropic, believes, asserted))`, the negation invisible to the kind;
  the bridge `bridge:accepts_at(anthropic,u1,1)` assumes `helpful(claude)` (the path passes through the negated
  node, `bridge_through_negation`). The first input is rejected with the rewrite into two units; the second is
  `InvalidInput: negated operand` (no double negation). `D_ω′`: `Γ = [¬reports__believes__1(the_team),
  reports__believes__1(anthropic)]`, `neqs Γ = [¬(anthropic = the_team)]` (the asserted holder first, as `neqs`
  is defined); a certificate for `¬(anthropic = the_team)` from `Γ` replays under `E_reports`, and
  `reports_no_leak` reads it as the old-language consequence
  of `neqs Γ`; the finite model over `E₀` in which `the_team` and `anthropic` co-denote is not `Expandable`, and
  `reports-countermodel` on it reports that no source model extends it; the model in which they differ, with the
  key true of anthropic only, is valid and satisfies `Γ`.

Beside these: W2's schema, partition, kind depth and tamper tests repeated on report documents; norms.md 10.6 to
10.8 shapes for the surface round trip of every wording in 2.1 (canonical text, synonyms, the two rejected modal
forms with their rewrites), identity of every existing fixture unchanged, and certificate binding against each
change of φ.

### 10.3 Boundary fixtures

One fixture at the boundary of each claim that sections 2 to 5, 9 and 10.1 restrict to a fragment; for each
nested-content theorem of 9.2 and for `nested_independent`, fixtures that break exactly one of its hypotheses,
the hypothesis named in the table that closes this section (the holder differs, B₉ and B₉′; the polarity
differs, B₁₀, B₁₁, B₁₁′ and `D_ω`; the inner act differs, B₂; the nesting is two deep, B₁₂ and B₁₂′); for
`content_depth_bounded` the
admitted bound and the first document beyond it (B₁₃, B₁₃′); and for the three digest theorems
(`literal_paraphrase_distinct`, `negation_scopes_distinct`, `probably_not_scopes_distinct`) a document that
digests only one of the two compared objects (B₁₄, B₁₅, B₁₆) beside one that digests both (B₁₄′, `D_ε`, `D_μ`);
all over `E₀` and the declarations of 10.1 (B₂ adds
one context, `c4`, to them; B₈ is `D_π` of 10.1; B₉ is B₇ and B₉′ is B₁ with u1's holder changed; B₁₁ is `D_ω`
with u2's polarity changed; B₁₁′ is `D_ω`'s u1 alone; B₁₂′ is B₁₂ with the innermost node carried at top level;
B₁₃ is the sixth verification's depth-16 document and B₁₃′ its extension by one node; B₁₄′ is B₁₄ with `D_α`'s u1
added; B₁₅ is `D_ε`'s u1 alone; B₁₆ is `D_μ`'s u3 alone), with expected results
derivable from the definitions as in 10.2. Every entailment expectation below is an instance of a named theorem
of 9.2 or 9.3 under its hypotheses, or a countermodel. `D ▷ U` is applied here to documents with a `says` key
only to exhibit the boundary of 10.1, and every key such an expectation queries is checked against `topKeys`
directly.

```text
B₁   u1: Anthropic believes that the service is safe.                        believes, anthropic, c1, safe(service)   key k₁
     u2: The article says that Anthropic believes that the service is safe.   says, the_article, c3, ⟨k₁⟩             key k₂
         (nested attribution: u2's content is u1's key, and the document has a top-level says key)
B₂   u1: Anthropic believes that the article says that the service is safe.   believes, anthropic, c1, ⟨says, the_article, c4, safe(service)⟩
         (a nested says key k_in under the belief key k_out: the inner node is a says report, not the believes
          node that nested_independent's hb names; no top-level says key; the inner context is c4,
          a fourth context declared for this fixture only: present, "the article, later edition", so that k_in
          sorts after every registration key (says, text, c3, ·) in the key order of 1.5, whatever the content ids)
B₃   u1, u2 of D_β; u3: Anthropic believes that the service is safe.          believes, anthropic, c1, safe(service)
         (the belief in Q asserted; no says key)
B₄   u1: It is not the case that the team believes that the service is safe.  negated ⟨believes, the_team, c1, safe(service)⟩
     u2: Anthropic believes that the service is safe.                         believes, anthropic, c1, safe(service)   (u1's key)
     u3: The article says that it is not the case that Anthropic is the same as the team.
                                                                              says, the_article, c3, ¬(anthropic = the_team)
         (a content that the forced disequalities entail)
B₅   u1: The article says that the service is reviewed.                       says, the_article, c3, reviewed(service)
     s1: scoped check, payloads [u1], conclusion safe(service)                (E_q = E₀, background [])
B₆   u1: The article says that either the service is safe or it is not the case that the service is safe, or both.
                                                                              says, the_article, c3, safe(service) ∨ ¬safe(service)
         (a content valid on its own)
B₇   u1: Anthropic believes that the service is safe.                        believes, anthropic, c1, safe(service)   key k₁
     u2: According to the stated assessment, it may be that Anthropic believes that the service is safe.
                                                                              may, a1, ⟨k₁⟩   kind hedged(could, attributed(anthropic, believes, asserted))
         (a nested assessment content whose key u1 asserts; no says key)
B₈   D_π of 10.1: D_α with Γ_author = [reviewed(service) → safe(service), reviewed(service)]
         (u1's content entailed by the author's premises and not by the report premises)
B₉   u1: The team believes that the service is safe.                         believes, the_team, c1, safe(service)   key k₁
     u2: According to the stated assessment, it may be that Anthropic believes that the service is safe.
                                                                              may, a1, ⟨anthropic, believes, c1, safe(service)⟩   (k₁ at anthropic)
         (B₇ with u1's holder changed: one key k₁, asserted at the_team, nested at anthropic; no says key. The
          fifth verification's counterexample)
B₉′  u1: The team believes that the service is safe.                         believes, the_team, c1, safe(service)   key k₁
     u2: The article says that Anthropic believes that the service is safe.   says, the_article, c3, ⟨anthropic, believes, c1, safe(service)⟩
         (B₁ with u1's holder changed: the report form of B₉, for the situation line of 2.3)
B₁₀  u1: The article says that Anthropic believes that the service is safe.   says, the_article, c3, ⟨anthropic, believes, c1, safe(service)⟩
     u2: It is not the case that Anthropic believes that the service is safe.  negated ⟨anthropic, believes, c1, safe(service)⟩
         (the nested positive node denied at top level, same holder)
B₁₁  u1: The article says that it is not the case that Anthropic believes that Claude is helpful.   (D_ω's u1)
                                                                              says, the_article, c3, ⟨¬⟨anthropic, believes, c1, helpful(claude)⟩⟩
     u2: It is not the case that Anthropic believes that Claude is helpful.   negated ⟨anthropic, believes, c1, helpful(claude)⟩
         (D_ω with u2 denying, instead of asserting, the operand of u1's negated content)
B₁₁′ u1 of B₁₁ alone: The article says that it is not the case that Anthropic believes that Claude is helpful.
         (D_ω's u1 with no second unit: the operand's key k₁′ = (believes, organisation, c1, helpful) is nested
          only, asserted and denied by no top-level unit)
B₁₂  u1: The article says that the team says that Anthropic believes that the service is safe.
                                                                              says, the_article, c3, ⟨the_team, says, c3, ⟨anthropic, believes, c1, safe(service)⟩⟩
         (nesting depth 2, no other unit: the middle key k_mid = (says, organisation, c3, ⟨anthropic, believes,
          c1, safe⟩) and the innermost key k₁ = (believes, organisation, c1, safe) are nested only)
B₁₂′ B₁₂ plus u2: Anthropic believes that the service is safe.               believes, anthropic, c1, safe(service)   key k₁
         (the innermost node carried at top level, holder included; k_mid still nested only)
B₁₃  u1: It is not the case that the article says that it is not the case that the article says that … that
         the service is safe.   (fifteen says reports of the_article in c3, each under a negated node, over safe(service))
                                                                              ¬⟨says, the_article, c3, ¬⟨says, the_article, c3, … ¬⟨says, the_article, c3, safe(service)⟩ …⟩⟩
         (the sixth verification's document: fifteen report nodes and fifteen negated nodes on one path, content
          depth 16, W2 kind depth 16, both at the admitted bound)
B₁₃′ B₁₃ with a sixteenth negated says report of the_article in c3 inserted between the innermost report and
     safe(service)   (content depth 17, kind depth 17)
B₁₄  u1: The article says, "the service is safe".                             says, the_article, c3, ⟨safe(service), literal W⟩
         (W the words "the service is safe"; a literal quotation whose paraphrase complement ⟨safe(service), none⟩
          occurs nowhere: the document digests one complement object of that body and computes no digest for the
          other)
B₁₄′ B₁₄ plus u2: The article says that the service is safe.                  says, the_article, c3, ⟨safe(service), none⟩   (D_α's u1)
         (both complements of the body safe(service) occur, so both are digested and compared)
B₁₅  u1 of D_ε alone: Anthropic believes that it is not the case that Claude is human.
                                                                              believes, anthropic, c1, ¬human(claude)
         (no belief node over human(claude), asserted or denied, occurs: the complement ⟨human(claude), none⟩ is
          never digested)
B₁₆  u3 of D_μ alone: According to the stated assessment, it is probably the case that it is not the case that
     the service is safe.                                                     probably, a1, ¬safe(service)
         (no formula node safe(service) occurs: safe(service) is a subformula of the one leaf, not a node)
```

- **(B₁) Registration and nested attribution.** Over `B₁`: keys `k₁`, `k₂`; `E_reports = E₀ +
  reports__believes__1(organisation) + reports__says__1(text)`; `Γ = [reports__believes__1(anthropic),
  reports__says__1(the_article)]`, positive; `topKeys = {k₁, k₂}`. The model with the outer atom true and the
  inner atom false does not satisfy `Γ`, and a certificate for `Γ ⊢ reports__believes__1(anthropic)` replays from
  u1's premise: `nested_independent` has no instance at u2 (its hypothesis `k₁ ∉ topKeys` fails), which is the
  boundary of 4.5's nested independence; `safe(service)` is still not entailed (the model with both atoms true and
  `safe` empty is valid and satisfies `Γ`). Over `B₁ ▷ []`: the registration units are `The article says that
  Anthropic believes that the service is safe.` (for u1; key `k₂`) and `The article says that the article says
  that Anthropic believes that the service is safe.` (for u2; key `k₃ = (says, text, c3, ⟨k₂⟩)`); the two `says`
  predicates are numbered by content-id order and read from the key table; `Γ` is their two atoms at
  `the_article`; `topKeys (B₁ ▷ []) = {k₂, k₃}` contains `k₂` although `U` is empty, so `B₁ ▷ []` asserts a key
  of `B₁`: 10.1 (i) and (ii) fail, which is why they are stated for documents with no `says` key. `k₁` is nested
  only, so over `B₁ ▷ []` the model with both `says` atoms true, the `believes` atom false and `safe` empty is
  valid and satisfies `Γ` (`all_truth_combinations` with `ks = [k₁]`). Over `B₁ ▷ [u1]` (u2 registered as `k₃`;
  `Γ = [reports__believes__1(anthropic), reports__says__j(the_article)]` with `j` the position of `k₃` among the
  two `says` keys `k₂`, `k₃`): `k₂` is nested in the registration unit and not in `topKeys`, so the model with the
  `k₁` and `k₃` atoms true and the `k₂` atom false is valid and satisfies `Γ`, and no certificate for u2's atom
  replays there. The situation line of 2.3 for u2 reports that there is none, beside the certificate that replays
  from u1's premise (`nested_positive_entailed` at u2's nested node with `u′ = u1`: u1 carries the very node,
  holder included; `holder_atom_free` at `k₁`, `hd = anthropic` has no instance, `hfree` failing at u1's own
  holder; B₉′ is the same u2 with u1 at another holder, where the line shows a situation); the line for u1 shows
  the situation in which u1's belief holds and `safe(service)` is false.
- **(B₂) A nested `says` key.** Over `B₂`: keys `k_in = (says, text, c4, safe)` and `k_out`; names
  `reports__says__1`, `reports__believes__1`; `Γ = [reports__believes__1(anthropic)]`; `topKeys = {k_out}`. The
  model with the `believes` atom true, the `says` atom false and `safe` empty is valid and satisfies `Γ`
  (`unreported_key_free` at `k_in`, `k_in ∉ topKeys`): the nested atom is free over `B₂` itself, without
  registration. `nested_independent` has no instance at u1 and fails exactly `hb`, whose inner node is a
  `believes` report while u1's inner node is the `says` node (`hs₂` holds, `the_article : text`; `hin` holds,
  `⟨believes, text, c4, safe⟩ ∉ topKeys = {k_out}`; `he` and `hn` over any admissible `S₀` with `safe` empty, the
  document being positive): the one-hypothesis boundary of that theorem's shape hypothesis for the inner act,
  the seventh verification's finding. Over
  `B₂ ▷ []`: the registration unit `The article says that Anthropic believes that the article says that the
  service is safe.` has key `k_r = (says, text, c3, ⟨k_out⟩)`; the `says` keys are now `k_r` and `k_in`, and in
  the key order of 1.5 `k_r` precedes `k_in` (`c3` before `c4`, whatever the content ids), so `k_r` is
  `reports__says__1` and `k_in` is `reports__says__2`: the name of `k_in` differs from its name over `B₂`, while
  `reports__believes__1` is unchanged, and 10.1 (iii) fails outside the no-`says` fragment. The fixture requires
  this renumbering (the key table of `reports-elaborate` over `B₂ ▷ []` lists `k_in` under `reports__says__2`
  and `k_r` under `reports__says__1`), that `keyOf` recovers `k_in` under each of its two names, and that `k_in`
  and `k_out` are both outside `topKeys (B₂ ▷ []) = {k_r}`, so that all four truth combinations of their atoms at
  `the_article` and `anthropic` are realised (`all_truth_combinations`).
- **(B₃) The belief in `Q` asserted.** Three keys, all in `topKeys`; `Γ` is three positive `believes` atoms; the
  belief-in-safe atom is a premise, so (β)'s model with it false does not satisfy `Γ`, and
  `no_closure_under_consequence` has no instance (its hypothesis fails): the "not closed" bullet of 4.5 is stated
  for documents that do not assert the belief in `Q`. `safe(service)` is not entailed: the model with the three
  atoms true and `safe` empty is valid and satisfies `Γ`. Over `B₃ ▷ [u1, u2]` (u3 registered by `The article
  says that Anthropic believes that the service is safe.`; `B₃` has no `says` key) the belief-in-safe key is
  outside `topKeys`, and (β)'s model is recovered.
- **(B₄) A content the disequalities entail.** `Γ = [¬reports__believes__1(the_team),
  reports__believes__1(anthropic), reports__says__1(the_article)]`; `neqs Γ = [¬(anthropic = the_team)]`, which is
  u3's content. A certificate for `Γ ⊢ ¬(anthropic = the_team)` replays (`reports_no_leak` reads it as the
  old-language consequence of `neqs Γ`, as in ω′), so `B₄` entails the content of its own report u3;
  `attitude_not_factive` has no instance at u3, because no `Expandable` `S₀` falsifies the content, and the "not
  factive" bullet of 4.5 names exactly this case. The report atom plays no part: the sub-document `[u1, u2]`
  entails the same formula (ω′), and the sub-document `[u3]` alone is positive, so there the model in which
  `anthropic` and `the_team` co-denote with the `says` atom true is valid and satisfies its `Γ`. The checklist
  line of 2.3 for u3 has no situation in which the report holds and its content is false, and says so.
- **(B₅) Scoped consequence without `E_q`'s background.** `s1` is DOES NOT FOLLOW: the finite model over `E₀`
  with `reviewed = {service}` and `safe` empty is valid, satisfies `Background(E₀) = []` and the payload, and
  refutes `safe(service)` (`scoped_witness_sound`). The same payload formula `reviewed(service)` at `(u1, 1)` of
  `D_λ`, over `E_q`, is FOLLOWS through the definition premise of `Background(E_q)`: "follows from the reported
  contents" is consequence under the payloads' environment and its background (2.1, 5.1), never from the
  payloads alone.
- **(B₆) A valid content.** `Γ = [reports__says__1(the_article)]`, positive, `neqs Γ = []`; the content
  `safe(service) ∨ ¬safe(service)` is valid over `E₀`, so a certificate for `Γ ⊢ safe(service) ∨ ¬safe(service)`
  replays, and so does one for `[] ⊢ safe(service) ∨ ¬safe(service)` (`reports_no_leak_uniform` with `Γ = []`):
  the report entails its content, and `attitude_not_factive` has no instance (no `S₀` falsifies the content).
  This is the case the "not factive" bullet of 4.5 names for positive documents: `Γ_reports(D) ⊨ q` exactly when
  `q` is valid on its own. The checklist line of 2.3 for u1 has no situation in which the content is false, and
  says so.
- **(B₇) A nested assessment content that another unit asserts.** Keys `k₁` and `(may, a1, ⟨k₁⟩)`;
  `E_reports = E₀ + reports__believes__1(organisation) + reports__may__1(evidence)`;
  `Γ = [reports__believes__1(anthropic), reports__may__1(e1)]`, positive, `neqs Γ = []`; u2 is OPEN with its open
  term `reports__may__1`. u2's content elaborates to u1's atom, so a certificate for
  `Γ ⊢ reports__believes__1(anthropic)` replays from u1's premise (`nested_positive_entailed` at u2's nested node
  with `u′ = u1`: u1 carries the very node, holder included): `B₇` entails the content of its own assessment
  although `neqs` is empty and the content is not valid, and `assessment_not_factive` has no instance at u2 (its
  hypothesis names a formula content, and u2's is a report node), which is why 5.3 states its "exactly when" for
  formula contents over `E`; `holder_atom_free` at `k₁`, `hd = anthropic` has no instance over any `S₀` (`hfree`
  fails at u1's own holder), and B₉ is this fixture with u1 at `the_team`, where the atom is free although the
  key is asserted. `safe(service)` is still not entailed: the model with both atoms true and `safe`
  empty is valid and satisfies `Γ`. Over `B₇ ▷ [u2]` (u1 registered by `The article says that Anthropic believes
  that the service is safe.`; `B₇` has no `says` key, so 10.1 applies): `Γ = [reports__may__1(e1),
  reports__says__1(the_article)]`, `k₁` is nested in both units and outside `topKeys`, and the model with the
  `may` and `says` atoms true, the `believes` atom false and `safe` empty is valid and satisfies `Γ`
  (`unreported_key_free` at `k₁`): the nested content is free on the fragment 5.3 names.
- **(B₈) The author's premises entail the content.** `Γ_reports(D_π) = Γ_reports(D_α) =
  [reports__says__1(the_article)]`, positive; the checked list is `Γ_reports ++ Γ_author`. The certificate for
  `safe(service)` from `Γ_author` replays (π), so the document's checked premise set entails u1's content, while
  `Γ_reports(D_π)` alone does not (α's countermodel; `attitude_not_factive` at u1: the source model with `safe`
  empty satisfies every report, falsifies the content and does not satisfy `Γ_author`). The checklist line of
  2.3 for u1 shows that situation as a model of the report premises and not of `Γ_author`; what the whole checked
  list entails is the P0 line and the certificate. Every entailment claim of 2.3, 4.5 and 5.3 is over
  `Γ_reports(D)`; this fixture is the boundary of that restriction.
- **(B₉) The same key at another holder.** Keys `k₁ = (believes, organisation, c1, safe)` and
  `(may, a1, ⟨anthropic, believes, c1, safe⟩)`; `E_reports = E₀ + reports__believes__1(organisation) +
  reports__may__1(evidence)`; `Γ = [reports__believes__1(the_team), reports__may__1(e1)]`, positive,
  `neqs Γ = []`; `topKeys = {k₁}`; u2 OPEN with its open term. u2's content elaborates to
  `reports__believes__1(anthropic)`, the atom of `k₁` at `anthropic`, which no premise carries. The finite model
  in which `anthropic` and `the_team` are distinct elements, `reports__believes__1 = {the_team}`,
  `reports__may__1 = {e1}` and `safe` empty is valid, satisfies `Γ` and falsifies u2's content, so no certificate
  for `Γ ⊢ reports__believes__1(anthropic)` replays (`holder_atom_free` at `k₁`, `hd = anthropic`, over any
  admissible `S₀` in which the two constants differ: the one positive premise of `k₁` is at `the_team`, so
  `hfree` holds). `nested_positive_entailed` has no instance at u2's nested node (no top-level unit carries
  `⟨anthropic, believes, c1, safe⟩`; u1 carries `⟨the_team, …⟩`, another node of the same key), and
  `unreported_key_free` has none at `k₁` (`k₁ ∈ topKeys`): the key is asserted and the atom is free, which is the
  boundary of every reading that put a key where the theorems put a holder-applied atom, the fifth verification's
  counterexample. Over the `S₀` in which `anthropic` and `the_team` co-denote, `hfree` fails and every source model
  over `S₀` has the relation true at their shared element (u1's premise), so u2's content is true there: the
  finite model with both constants at one element, that element in `reports__believes__1`, is valid and satisfies
  `Γ`. u2's content is therefore neither entailed nor refuted by `Γ`. `safe(service)` is not entailed (the first
  model). Over `B₉ ▷ [u2]` (u1 registered; `B₉` has no `says` key, so 10.1 applies) the expectation of
  `B₇ ▷ [u2]` is recovered.
- **(B₉′) The report form.** Keys `k₁` and `(says, text, c3, ⟨anthropic, believes, c1, safe⟩)`;
  `Γ = [reports__believes__1(the_team), reports__says__1(the_article)]`, positive; the same two models with
  `reports__says__1 = {the_article}` in place of the assessment atom, and the same theorem instances. The
  situation line of 2.3 for u2 shows the first model (the team believes, Anthropic does not, the article says),
  and no certificate for u2's content replays; over B₁, the same u2 beside the belief at `anthropic`, the line
  reports the certificate instead. `nested_independent` has no instance at u2 in either (`k₁ ∈ topKeys` in both).
- **(B₁₀) The nested positive node denied at top level.** Keys `k₁` and `k₂ = (says, text, c3, ⟨anthropic,
  believes, c1, safe⟩)`; `Γ = [reports__says__1(the_article), ¬reports__believes__1(anthropic)]`; `neqs Γ = []`
  (no positive `believes` premise); `topKeys = {k₁, k₂}`; u2's status line is the denied form of 7.2. u1's content
  elaborates to `reports__believes__1(anthropic)`, whose negation is u2's premise, so a certificate for
  `Γ ⊢ ¬reports__believes__1(anthropic)` replays from u2's premise and u1's content is false in every model of `Γ`
  (`nested_positive_refuted` at u1's nested node with `u′ = u2`). `nested_positive_entailed` has no instance (no
  unit carries the positive node); `holder_atom_free` at `k₁`, `hd = anthropic` has one over every admissible
  `S₀` (`Expandable` trivially, `hfree` vacuously), and its model is any model of `Γ`. The situation line of 2.3
  for u1 shows the finite model with `reports__says__1 = {the_article}`, `reports__believes__1` empty and `safe`
  empty. `safe(service)` is not entailed.
- **(B₁₁) The nested negated node denied at top level.** Keys `k₁′ = (believes, organisation, c1, helpful)` and
  `(says, text, c3, ⟨¬⟨anthropic, believes, c1, helpful⟩⟩)`; `Γ = [reports__says__1(the_article),
  ¬reports__believes__1(anthropic)]`, `neqs Γ = []`. u1's content, the negated node, elaborates to
  `¬reports__believes__1(anthropic)`, which is u2's premise: a certificate for
  `Γ ⊢ ¬reports__believes__1(anthropic)` replays (`nested_negated_entailed` at u1's nested negated node with
  `u′ = u2`), u1's content is true in every model of `Γ`, and the situation line of 2.3 for u1 reports that there
  is none, beside the certificate. Over `D_ω`, the same u1 beside the assertion of the operand, the same content
  is false in every model (`nested_negated_refuted`, ω). Over the sub-document `[u1]` alone, `k₁′ ∉ topKeys` and
  both truth values of the atom at `anthropic` are realised (`all_truth_combinations` with `ks = [k₁′]`), so there
  the content is neither entailed nor refuted; that sub-document is B₁₁′. For `nested_independent`, u1 breaks
  two hypotheses here, `hb` (its body is a negated node) and `hin` (u2 puts `k₁′` into `topKeys`), so B₁₁ is not
  a one-hypothesis boundary of that theorem; B₁₁′ is.
- **(B₁₁′) The nested negated node with no top-level unit of its key.** Keys `k₁′` and
  `k_s = (says, text, c3, ⟨¬⟨anthropic, believes, c1, helpful⟩⟩)`; `E_reports = E₀ +
  reports__believes__1(organisation) + reports__says__1(text)`; `Γ = [reports__says__1(the_article)]`, positive,
  `neqs Γ = []`; `topKeys = {k_s}`, so `k₁′ ∉ topKeys`. u1's content, the negated node, elaborates to
  `¬reports__believes__1(anthropic)`, an atom no premise carries in either polarity: the finite model with
  `reports__says__1 = {the_article}`, `reports__believes__1` empty and `helpful` empty is valid, satisfies `Γ` and
  makes the content true; the model with `reports__believes__1 = {anthropic}` instead is valid, satisfies `Γ` and
  makes it false (`all_truth_combinations` with `ks = [k₁′]`, both values); so no certificate for
  `Γ ⊢ ¬reports__believes__1(anthropic)` and none for `Γ ⊢ reports__believes__1(anthropic)` replays, and the
  situation line of 2.3 for u1 shows the second model. `nested_negated_entailed` and `nested_negated_refuted` have
  no instance at u1's negated node, each failing exactly `hb′` (no top-level unit's content is `¬n`, or `n`; u1's
  is the `says` node). `nested_independent` has no instance at u1 and fails exactly `hb` (its `hb` names a report
  body over a formula, and u1's body is a negated node), `hin` holding because `k₁′ ∉ topKeys`, `hs₂` because
  `anthropic : organisation`, and `he`, `hn` over any admissible `S₀` with `helpful` empty (the document is
  positive): this is the one-hypothesis boundary of that theorem's shape hypothesis for a negated inner node,
  which B₁₁ and `D_ω` are not. `helpful(claude)` is not entailed (the first model).
- **(B₁₂) Nesting depth 2, no other unit.** Keys `k₁`, `k_mid = (says, organisation, c3, ⟨anthropic, believes,
  c1, safe⟩)` and `k_top = (says, text, c3, ⟨the_team, says, c3, ⟨…⟩⟩)`; in the key order of 1.5 `k_mid`
  precedes `k_top` (`organisation` before `text`), so `E_reports = E₀ + reports__believes__1(organisation) +
  reports__says__1(organisation) + reports__says__2(text)`; `Γ = [reports__says__2(the_article)]`, positive,
  `neqs Γ = []`; `topKeys = {k_top}`; u1's content depth is 4 (`Content.depth`, 9.1: three report nodes, each one
  more than its body, over the formula leaf, which counts one) and its kind `attributed(the_article, says,
  attributed(the_team, says, attributed(anthropic, believes, asserted)))` has depth 4 likewise; the fixture's
  "nesting depth 2" counts the report nodes below the top-level one (the formula leaf is at path depth 2,
  `(u1, 1.1)`, 5.2). Neither nested atom is carried by a
  premise and neither nested key is in `topKeys`: the finite model with `reports__says__2 = {the_article}`,
  `reports__says__1` empty, `reports__believes__1` empty and `safe` empty is valid and satisfies `Γ`
  (`unreported_key_free` at `k_mid` and at `k₁`; `all_truth_combinations` with `ks = [k₁, k_mid]` realises all
  four truth combinations of the two atoms, uniformly on the `organisation` domain), so no certificate for u1's
  content `reports__says__1(the_team)`, for the innermost atom `reports__believes__1(anthropic)` or for
  `safe(service)` replays, and the situation line of 2.3 for u1 shows that model. `nested_independent` has no
  instance at u1 and fails exactly `hb` (its `hb` names a formula body one level down, and u1's body one level
  down is a report node), `hin` holding because `k₁ ∉ topKeys`: this is the one-hypothesis boundary of that
  theorem's shape hypothesis for depth 2, and why 4.5's nested-independence bullet stops at depth 1.
  `nested_positive_entailed` has no instance at either nested node, failing exactly `hb′` (no top-level unit
  carries it). The bridge paths `(u1, ε)`, `(u1, 1)` and `(u1, 1.1)` assume the middle atom, the innermost atom
  and `safe(service)` respectively (5.2).
- **(B₁₂′) Nesting depth 2, the innermost node carried at top level.** B₁₂ with u2: the same keys and
  `E_reports`; `Γ = [reports__says__2(the_article), reports__believes__1(anthropic)]`, positive, `neqs Γ = []`;
  `topKeys = {k_top, k₁}`. The innermost node is u2's content, holder included: a certificate for
  `Γ ⊢ reports__believes__1(anthropic)` replays from u2's premise (`nested_positive_entailed` at u1's innermost
  node with `u′ = u2`, every hypothesis holding at depth 2 because `nodes` lists every descendant: the theorem's
  depth-2 instance, not a boundary). The middle node's atom `reports__says__1(the_team)` is carried by no premise
  and `k_mid ∉ topKeys`: B₁₂'s model with `reports__believes__1 = {anthropic}` added is valid and satisfies `Γ`
  (`unreported_key_free` at `k_mid`), so no certificate for u1's content replays, and the situation line of 2.3
  for u1 shows that model. `nested_independent` has no instance at u1 and fails two hypotheses, `hb` as in B₁₂
  and `hin` because u2 puts `k₁` into `topKeys`, so this fixture is not a one-hypothesis boundary of that
  theorem; B₁₂ is. `safe(service)` is not entailed (`attitude_not_factive` at u2). The bridge paths are those of
  B₁₂; the second, `(u1, 1)`, assumes what is already the premise `report:u2`.
- **(B₁₃) The depth bound attained.** u1's kind is fifteen `attributed(the_article, says, ·)` wrappers around
  `asserted`, of depth 16, which the frozen W2 decoder admits (`decodeKind` at fuel 16 reaches `asserted` at fuel
  1); its content tree has fifteen report nodes and fifteen negated nodes on one path over `safe(service)`, and
  `Content.depth` of it is 16 (a leaf counts one, each report one more, each negated node nothing), so 4.1 step 4
  admits it and `content_depth_bounded` holds with equality, which the previous statement `< 16` did not. Fifteen
  `says` keys with distinct content ids (each body a strict subtree of the next), names `reports__says__1` to
  `reports__says__15` in content-id order, all on `text`; `E_reports = E₀` plus those fifteen predicates;
  `Γ = [¬reports__says__i(the_article)]` for the outermost key's position `i`; `neqs Γ = []` (no positive entry);
  u1's status line is the denied form of 7.2; the premise-set model exists (any model with that predicate empty at
  `the_article`), and no certificate for any of the fourteen nested atoms, in either polarity, replays
  (`all_truth_combinations` with `ks` the fourteen nested keys, none in `topKeys`). The bridge path of fourteen
  descents, which passes through every negated node on the way (5.2, `bridge_through_negation` at the top-level
  one), assumes `safe(service)`. The residual's `reports` line counts one denied `says` premise and no asserted
  one (6).
- **(B₁₃′) One node beyond the bound.** Rejected at 4.1 step 2 by the frozen W2 kind decoder, `ResourceLimit: kind
  depth exceeds 16` (`decodeKind` reaches `asserted` at fuel 0), before any content tree is read: no key, name or
  premise is generated and `content_depth_bounded` has no instance (`WellFormedReports = false`). The content
  decoder's own bound, `ResourceLimit: content depth`, is the same 16 and is not reached here, the kind being
  rejected first; a content tree of depth 17 under a kind of depth 16 would be `KindMismatch` at step 4.
- **(B₁₄) A literal quotation alone.** One key `k_W = (says, text, c3, ⟨safe(service), W⟩)`; `E_reports = E₀ +
  reports__says__1(text)`; `Γ = [reports__says__1(the_article)]`, positive; status CHECKED; the residual's
  `literal_quotations` line counts one; the checklist of 2.3 shows the exact words beside the content. The digest
  table of 4.1 step 4 holds the content ids of u1's two nodes (the report node and its formula leaf) and the one
  complement id `complementId B₁₄ (formula safe(service)) (some W)`; the paraphrase complement `⟨safe(service),
  none⟩` is digested by no step of admission, so no check compares its digest with anything and `HashCollision`
  cannot fire for it. `literal_paraphrase_distinct` at `b = safe(service)`, `l₁ = some W`, `l₂ = none`: `hw`
  holds and the canonical-object conjunct holds (the two complement objects differ in their `literal` field);
  the digest conjunct has no instance, exactly `OccursComplement B₁₄ b none` failing. Whether `complementId B₁₄ b
  none` equals `complementId B₁₄ b (some W)` is a proposition about a digest the document never computes, which
  no check of the document decides and no statement of this specification asserts either way; under draft 9's
  statement that equality would have witnessed the second key-membership premise by `k_W` itself and
  contradicted the conclusion, the eighth verification's finding (13.26). `safe(service)` is not entailed (α's
  model with the literal key in place of `D_α`'s).
- **(B₁₄′) Literal and paraphrase together.** Both complement objects of the body `safe(service)` occur, as the
  complements of u1 and u2, so both are digested and compared at 4.1 step 4: the keys `k_W` and `k_P = (says,
  text, c3, ⟨safe(service), none⟩)` differ in their complement ids (`literal_paraphrase_distinct`, both
  occurrence hypotheses holding; `no_collision_complement` on the two distinct objects says the same), names
  `reports__says__1` and `reports__says__2` in content-id order (the fixture reads them from the key table);
  `E_reports = E₀` plus both; `Γ` is the two atoms at `the_article`, positive; the residual counts two report
  keys and one literal quotation; the `reports-elaborate` key table lists both keys with their source keys and
  u1's literal words. The alternative the definitions leave, that the two digests coincide, is the rejection
  `HashCollision: <digest>` of the whole document at step 4 and never one merged key; it is not the expected
  result on the fixture's bytes, as no fixture with two keys of one act expects it. Over `B₁₄′` both keys are in
  `topKeys` (both atoms are premises), so no independence expectation is stated here; 1.1's "neither entails the
  other" is the reading of `all_truth_combinations` over a document in which neither key is at top level.
- **(B₁₅) The negation-inside belief alone.** One key `(believes, organisation, c1, ⟨¬human(claude), none⟩)`,
  name `reports__believes__1`; `Γ = [reports__believes__1(anthropic)]`, positive; the paraphrase of 2.1's
  inside-negation row. No node `human(claude)` and no report node over it occurs, so the document digests no
  complement `⟨human(claude), none⟩`, and `negation_scopes_distinct` at `q = human(claude)`, `c = c1`, `s =
  organisation` has no instance, exactly `ho'` failing (`hs₁`, `hs₂` at `anthropic` and `ho` hold); its
  canonical-object conjunct holds regardless. `D_ε` is the instance: u2's operand is the belief node over
  `human(claude)`, occurring under the negated node, so both complements are digested and the two names differ
  (ε). Under draft 9's statement the second key-membership premise could be witnessed by the one key present if
  the absent complement's digest equalled it, a digest the document never computes (13.26).
- **(B₁₆) The negated assessment content alone.** One key `(probably, a1, ⟨¬safe(service)⟩)`, name
  `reports__probably__1`, one open term; u3 OPEN; `Γ = [reports__probably__1(e1)]`. No formula node
  `safe(service)` occurs (it is a subformula of the one leaf `¬safe(service)`, and 4.1 step 4 digests nodes, not
  subformulas), so `probably_not_scopes_distinct` at `a = a1`, `q = safe(service)` has no instance, exactly `ho'`
  failing; its canonical-object conjunct holds regardless. `D_μ` is the instance: u2's body is the node
  `safe(service)`, so both formula nodes are digested and the two `probably` names differ (μ).

**Which hypothesis each boundary fixture breaks.** For every fixture this section offers as the boundary of a
theorem: the theorem, the fixture, the one hypothesis that fails (every other hypothesis of the statement holds,
over some admissible `S₀` where one is needed) and the expected result. A row that names two hypotheses records
that the fixture is an instance of another theorem, not a one-hypothesis boundary of this one.

| Theorem | Fixture | Hypothesis that fails | Expected |
|---|---|---|---|
| `nested_positive_entailed` | B₁, B₇, B₁₂′ | none: instances (B₁₂′ at depth 2) | the nested atom's certificate replays from the carrying unit |
| | B₉, B₉′ | `hb′`: the only top-level unit of the key carries it at another holder | the atom free (`holder_atom_free`) |
| | B₁₀ | `hb′`: the top-level unit carries `¬n` | the atom refuted (`nested_positive_refuted`) |
| | B₁₂ | `hb′`: no top-level unit carries either nested node | both atoms free (`unreported_key_free`) |
| `nested_positive_refuted` | B₁₀ | none: instance | the certificate for `¬φ` replays |
| | B₁, B₇ | `hb′`: the top-level unit carries `n`, not `¬n` | entailed (`nested_positive_entailed`) |
| | B₉ | `hb′`: no top-level unit carries `¬n` | free (`holder_atom_free`) |
| `nested_negated_entailed` | B₁₁ | none: instance | the certificate for `¬φ` replays |
| | `D_ω` | `hb′`: the top-level unit carries `n`, not `¬n` | refuted (`nested_negated_refuted`) |
| | B₁₁′ | `hb′`: no top-level unit carries `¬n` | free (`all_truth_combinations`) |
| `nested_negated_refuted` | `D_ω` | none: instance | the certificate for `φ` replays |
| | B₁₁ | `hb′`: the top-level unit carries `¬n`, not `n` | entailed (`nested_negated_entailed`) |
| | B₁₁′ | `hb′`: no top-level unit carries `n` | free (`all_truth_combinations`) |
| `holder_atom_free` | B₉ over an `S₀` with the two constants distinct; B₁₀; B₁₂ | none: instances | a source model over `S₀` with the atom false at `hd` |
| | B₁, B₇; B₉ over an `S₀` in which `anthropic` and `the_team` co-denote | `hfree`: a positive premise of the key at a holder co-denoting with `hd` | no instance; the atom true in every source model over that `S₀` |
| `nested_independent` | `D_ζ` | none: instance | inner relation empty, `q` false |
| | B₁ | `hin`: the inner key asserted at the same holder | entailed (`nested_positive_entailed`) |
| | B₉′ | `hin`: the inner key asserted at another holder | free (`holder_atom_free`) |
| | B₂ | `hb`: the inner node is a `says` report, not the `believes` node the shape names; no top-level unit of its key | free (`unreported_key_free` at `k_in`) |
| | B₁₁′ | `hb`: the inner node is negated; no top-level unit of its key | free (`all_truth_combinations`) |
| | B₁₂ | `hb`: the body one level down is a report node; no top-level unit of either nested key | free (`unreported_key_free`) |
| | B₁₁, `D_ω`, B₁₂′ | `hb` and `hin` together: the nested key denied or asserted at top level | not one-hypothesis boundaries of this theorem; instances of the nested-content theorems above |
| `no_closure_under_consequence` | `D_β` | none: instance | belief-in-`Q` relation empty |
| | B₃ | `hQ`: the belief in `Q` asserted | entailed (its atom is a premise) |
| `attitude_not_factive` | `D_α` | none: instance | `q` false in a source model of every report |
| | B₆ | `hn`: no `S₀` falsifies a valid content | entailed (`reports_no_leak_uniform`) |
| | B₄ | `he` and `hn` jointly unsatisfiable: every `Expandable` `S₀` makes the content true | entailed (`reports_no_leak`, through `neqs`) |
| | B₈ | none over `Γ_reports(D)`; `Γ_author` is outside the statement | free over the report premises, entailed by the checked list |
| `content_depth_bounded` | B₁₃ | none: instance at the bound, depth 16 | admitted; `depth = 16` |
| | B₁₃′ | `h`: `WellFormedReports` fails at W2's kind bound | `ResourceLimit: kind depth exceeds 16` |
| `literal_paraphrase_distinct` | B₁₄′ | none: instance, both complements occur | two keys, two names; the object and digest conjuncts |
| | B₁₄ | `OccursComplement D b none`: the paraphrase complement occurs nowhere | one key; the object conjunct holds; the digest conjunct has no instance; the absent complement is never digested |
| `negation_scopes_distinct` | `D_ε` | none: instance | two keys, two names (ε) |
| | B₁₅ | `ho'`: no belief node over `human(claude)` occurs | one key; the object conjunct holds; the name conjunct has no instance |
| `probably_not_scopes_distinct` | `D_μ` | none: instance | two `probably` keys, two names (μ) |
| | B₁₆ | `ho'`: no formula node `safe(service)` occurs | one `probably` key; the object conjunct holds; the name conjunct has no instance |

## 11. Limits, regeneration, Rust and trust

### 11.1 Limits

Contexts ≤ 256, assessments ≤ 256, bridges ≤ 1,000, scoped checks ≤ 256 with ≤ 64 payloads each, content depth ≤ 16
(`Content.depth`, 9.1: a well-formed unit's content depth is its W2 kind depth, whose frozen decoder admits exactly
16, so `content_depth_bounded` is stated at `≤ 16` and B₁₃ attains it), literal words ≤ 4,096 bytes, generated
names ≤ 64 bytes, predicates within `MAX_PREDICATES`
(256, so a document with more distinct keys than the free predicate budget is `ResourceLimit: MAX_PREDICATES`
rather than a verdict), formulas within `MAX_NODES`; witness search uses the existing bounds and `MAX_EVALUATIONS`.
Every overflow is `ResourceLimit` with the limit named, never a truth value.

### 11.2 Regeneration and model validity

`E_reports`, the key order, the generated names, `Γ_reports`, the open-term records and every bridge formula are
regenerated from the decoded units and declarations at every trusted site; a list supplied on the wire is never
trusted (norms.md 11.3). A finite model supplies tables for the author's predicates and for the generated
predicates alike (they are base predicates); a model omitting a generated predicate's table is invalid
(`InvalidModel`), and a model over `E₀` alone is a model of the old language, not of the document.

### 11.3 Composition with other statement layers

In this slice `reports@0` with any of `norms@0`, `definitions@0` or `data@0` is `UnsupportedProfile: reports@0
with <profile> layers`, rejected by the reports gate (4.1 step 1, 9.4) before any unit is read and listed in the
status table beside the plan's boundary with its criterion. For the norms and definitions chains the criterion is
that the composition `Layer.comp` of `reportsRoute` with the chain (`E_in` of the chain `= E_reports`, the report
atoms being base predicates below every regulated or defined symbol in the shared DAG) and the executable's
regeneration of that chain over `E_reports` are unproved and unbuilt. For `data@0` it is that every theorem of
9.3 is stated over `StringAdmissible`, and the data layer's admissibility, its flag premises and its route
statements over `E_reports` have no theorem here; draft 1's sentence that `data@0` "composes as today" had none
behind it and is withdrawn. Quoted W1 and W3 content is handled locally (5.1, 5.4) and needs no composition;
`documents@1` is the W2 wrapper this profile extends.

### 11.4 Rust and trust

Rust never elaborates reports: on the `elaborated-document` family a reports case carries the Python-generated
`E_reports` and `Γ_reports` marked `untrusted: true`, and its verdict must agree with Python's and Lean's
regenerated ones (regression evidence; the trust path is Lean; SEMANTICS-MIGRATION-PLAN 6: no new Python
semantics, Python presents and searches). Trust remaining after the theorems of section 9, in the
verification-contract table's terms: the reports decoder (contexts, assessments, content trees, bridges, scoped
checks, the pinned environments of quoted blocks), the display of paraphrases and manifests, and the English
round trip until item 4's theorems exist. The registered route's trust cost is exactly that list; no oracle,
theorem name or successful build substitutes for a replayed certificate.

## 12. Statement review checklist (Astra + Fable, before items 2 to 5)

1. The key (1.1): act, holder sort, context with tense, content id; finite and acyclic; literal versus paraphrase
   as distinct contents (13.6); the statement grammar with `not` as the only connective over reports (13.15);
   identity on canonical objects with `HashCollision` over the objects the document digests, the content object
   of every node and the complement object of every report node, and digest conclusions only under the
   occurrence of both compared objects (3.4, 13.26).
2. The four acts and the complement forms (1.2, 1.3); unreviewed acts as `UnsupportedAct` or LABELLED metadata,
   never renamed; the act check only on units with report content (4.1 step 2, fixture σ).
3. The assessment record and the explicit `unresolved_decider` (1.4, 5.3); the parser binding of "the stated
   assessment" (2.1, fixture ν); the admission sentence.
4. `E_reports` and the generated names (1.5), per-act numbering, injective on the document's keys; the reserved
   prefix.
5. The typed semantics `(S, J, A)` with `J` on the complete key, recursive `Sat` and `IntendedReports` (4.2): only
   top-level statements assert; nested nodes, negated or not, are contents; what a top-level unit entails about a
   nested node's atom is 9.2's nested-content theorems, on the holder-applied atom with its polarity (B₇, B₉ to
   B₁₂′, `D_ω`).
6. `elab` through negation, `interp`, `restrictJ` with its domain guards (13.17) and
   `reports_elaboration_faithful` in both directions with finite witness decoding (4.3, 9.2), at every universe.
7. The route instance: `Layer.id` over `E_reports`, signed report atoms in `Γ`, `Intended = True` as the empty
   layer's meaning only (4.4); the reports gate around the frozen classifier (9.4); `reports_route_acceptance`
   and `reports_route_countermodel` (9.3).
8. `reports_old_language_conservative` as the unconditional vocabulary statement; `reports_no_leak` with `neqs`
   over well-formed signed atoms (`SignedAtom` typed, `neqs_wellFormed`); `Expandable` on every model-existence
   theorem, trivial for a positive document; the same vacuity line at `E_reports` and at `E` (4.4, 13.18).
9. The structure theorems as instances of `source_over_any_structure`, on formula contents over `E` with
   `M.S = S₀`, each stated over `Γ_reports(D)` and with the fragment on which it holds and its boundary fixture
   (4.5, 9.2, 10.3, 13.22); the assessment counterpart `all_truth_combinations_assess` and 5.3's non-factivity
   for formula contents only (B₇); the five nested-content theorems (`nested_positive_entailed`,
   `nested_positive_refuted`, `nested_negated_entailed`, `nested_negated_refuted`, `holder_atom_free`) on the
   holder-applied atom and never on a key, the `holderSort` hypotheses of `no_closure_under_consequence` and
   `nested_independent` (13.23); 4.5 and 4.6 as NON-NORMATIVE readings that claim nothing beyond the statements;
   `content_depth_bounded` at the admitted bound `≤ 16` with `Content.depth` defined so that a well-formed
   unit's content depth is its W2 kind depth (9.1, 4.1 step 4, 11.1, B₁₃, 13.24).
10. Scoped checks as report lines, not premises, under `Background(E_q)` of the pinned route; inner
    inconsistency local (5.1); a quoted definition premise never inserted into the checked list and present there
    only as an explicit author premise (`scoped_background_local`); a package's statement as the only formula
    node over `E_q` (13.16).
11. Bridges: explicit unit and path fields, `bridge:accepts_at` beside the frozen root label, the holder rule
    that leaves assessment nodes to any agent, records for nested targets, the legacy root meaning byte for byte
    including dotted unit ids, the kind rejection extended to nodes over `E_q` (5.2, 9.3, 13.8).
12. Adoption and import as provenance-only typed operations (5.4).
13. Status and residual lines (6), the negated-unit row; the wrapper/complement byte split.
14. The English table (2.1): one reading per wording, the nested-negation row, the deferral of other
    connectives; the synonyms and non-synonyms (2.2); the checklist (2.3); the round-trip contract and
    `ManifestMismatch` (2.4); the source examples with zero substantive gain (2.5).
15. The diagnostics (8) and the fixtures (10), each against the definitions, each independence expectation over
    its named premise subset `D ▷ U` over a document with no `says` key, with the queried keys kept in the
    vocabulary by registration and asserted or denied by no kept unit (10.1, 13.21); the boundary fixtures of
    10.3, B₁ to B₁₆, one per restricted claim, the nested assessment (B₇), the author's premises (B₈), B₂'s
    forced renumbering, the one-hypothesis-broken fixtures of the nested-content theorems and of
    `nested_independent` as the closing table of 10.3 names them (B₉ and B₉′, the holder; B₁₀, B₁₁ and ω's
    refutation, the polarity; B₂, B₁₁′ and B₁₂, `nested_independent`'s shape hypothesis alone, the inner act, a
    negated inner node and depth 2, with B₁₁, `D_ω` and B₁₂′ recorded as breaking two), the depth bound
    attained and exceeded (B₁₃, B₁₃′) and the digest boundaries (B₁₄, B₁₅, B₁₆, one compared object absent;
    B₁₄′, `D_ε`, `D_μ` the instances) among them; the
    checklist's situation lines of 2.3, defined by what the IDE runs, against B₁, B₃, B₄, B₆, B₈, B₉′, B₁₀, B₁₁,
    B₁₁′, B₁₂, B₁₂′ and `D_ω`; the envelope in fixture φ (13.19).
16. The composition gate with `data@0` rejected (11.3) and the trust list (11.4).
17. The resolved choices of section 13, in particular 13.2 (the profile-gated act list), 13.5 (criteria are not
    premises), the draft-2 choices 13.15 to 13.19, the draft-5 choice 13.21 (the no-`says` fragment of the
    premise-subset device), the draft-6 choice 13.22 (entailment claims over `Γ_reports(D)` for formula
    contents over `E`), the draft-7 choice 13.23 (normative content is definitions, statements and fixtures;
    nested-content entailment on the holder-applied atom), the draft-8 choice 13.24 (a boundary fixture names
    the one hypothesis it breaks; a theorem is weakened to the admitted bound, never the bound tightened) and the
    draft-9 choice 13.25 (an instance claim unifies the fixture's content with the shape hypothesis literally,
    act included; a fixture's depth is `Content.depth` computed) and the draft-10 choice 13.26 (a digest or name
    conclusion is under the occurrence of both compared objects; the collision check is document-local); the
    "Fragments" convention of section 0.
18. The "Normative content" rule of section 0: every prose entailment, "iff", "exactly when" and "no …" claim
    outside the definitions, 9.2, 9.3 and section 10 names the theorem it reads and that theorem's hypotheses, or
    is absent; 4.5 and 4.6 marked NON-NORMATIVE; the three open questions of 4.6 left as questions, none promoted
    to a claim; the plan's pages and summary (revision 9) carrying no unconditional semantic sentence and marked
    NON-NORMATIVE on the same terms.

## 13. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **Unary predicates on the holder sort, keyed by holder sort.** The plan's "fresh unary predicate on its holder
   sort" needs the sort in the key so that two holders of different sorts with one content and context get two
   predicates. Assessments are unary on the evidence sort, keyed by (judgment, assessment id, content id), and
   applied to the record's evidence context, so `May(a, q)` keeps the plan's `May(c, q)` shape with the record
   carrying the criteria.
2. **The W2 kind list gains `wants` under the profile only.** The frozen decoder's acts are `says, promised,
   believes, intends, expects, denies`; a desire unit cannot be tagged today. The reports decoder accepts
   `attributed(agent, wants, k)` when `reports@0` is enabled; outside the profile the frozen decoder is unchanged,
   so no existing artefact changes. A change to the frozen decoder is not proposed.
3. **Contexts are document records, evidence contexts are constants.** Attitude contexts are key components (tense,
   tag, description) declared in the front matter; evidence contexts are constants of a declared sort because the
   assessment predicate needs an argument. Two notions, two places, both identity-bound.
4. **Tense values are three and the reference-time tag is opaque.** `present`, `past`, `perfect` cover every pilot
   target; no `time@0` dependency and no inference between tenses (the plan: "admit only supported temporal
   readings").
5. **Assessment criteria are records, not premises.** `necessary` and `sufficient` are W2 open-term fields
   (validated formulas) and enter the residual; they are not added to `Γ`, because the plan says admission checks
   the declared criteria and establishes nothing about likelihood. An author who wants a criterion to bind writes
   it as a unit.
6. **Literal and paraphrase are different contents.** The plan binds exact words into literal quotation; the
   simplest faithful reading is a different content id, hence a different key, with both shown.
7. **Report atoms are document premises with their own labels** (`report:<unit>`, `assessment:<unit>`), not
   `asserted` leaves, so the legacy rule that a quoted-kind unit needs a bridge is preserved verbatim and the new
   meaning is a new label.
8. **Nested bridge targets are a separate label with explicit unit and path fields; root paths are legacy.** W2
   tokens admit dots, so a unit may be named `u1.1` and the frozen two-token label `bridge:accepts(a,u1.1)` must
   keep meaning that root unit; the nested form is `bridge:accepts_at(a,u1,1)`, parsed by a new branch, with a
   record supplying reviewer and reason as the plan requires. Draft 1's reading, that `u1.1` could name no unit,
   was wrong and is withdrawn (statement review, both reviewers).
9. **Scoped checks are front matter, not units,** because they cover no source bytes; their payloads are paths so
   that occurrences, not holders, select them.
10. **Adoption and import are provenance fields on ordinary units in the destination document** (5.4); the plan's
    "regenerate validated W1 layers or W3 environments" is then the destination's ordinary admission.
11. **Composition with active norms or definitions layers is gated,** not specified (11.3), and quoted W1/W3 content
    is local; the pilots' whole-document runs under `norms@0` therefore report the gate, honestly, until the
    composition proof exists.
12. **The canonical rendering of assessments** is subject-raised for one positive atomic sentence and clausal
    otherwise; `may not` and `probably not` are rejected with the two rewrites rather than given a default scope.
13. **`According to <Holder>, S` is not a reports wording,** so the phrase "the stated assessment" is unambiguous by
    construction; the reserved-verbalisation check is a second guard.
14. **`MAX_PREDICATES` bounds the key count** rather than a separate limit, so the environment validator's existing
    error is the one reported.
15. **Negation is the only Boolean connective over report statements, and it is recursive.** The review found
    that draft 1 had wordings (2.1 rows for outer negation) with no wire form, no `elab` case and no clause in
    `IntendedReports`. The repair is the statement grammar of 1.1 (`not` over a report or assessment node,
    anywhere `S` may stand), because 2.1 admits a report wording wherever `S` occurs; a general Boolean AST would
    carry constructors with no wording row and would fail this very gate. `and`, `or` and quantifiers over report
    statements enter with a wording row or not at all (Astra's completion, accepted by Fable).
16. **A quoted definition package carries an optional statement over `E_q`.** Fixture λ needs a payload over the
    pinned environment, and draft 1 had no node that could be one. The statement is the only way a formula node
    over `E_q` arises; it is reachable by path for scoped checks and is never a bridge target (5.2).
17. **`restrictJ` carries domain guards rather than an admissibility argument.** The review offered both; the
    guards keep `restrictJ` total on every structure and make the typing fields definitional, and the
    correspondence theorems still take admissibility as a hypothesis where they need it (Fable's form, Astra
    proposed the argument form; the review may overturn).
18. **`neqs` rather than `UniformPolarity` as the hypothesis for removing report premises.** `neqs R` is exact
    for well-formed signed atoms (satisfying it is equivalent to the existence of an expansion satisfying `R`,
    `expansion_exists_iff`; the typing in `SignedAtom` is what keeps it exact, 4.4);
    `UniformPolarity` is the sufficient special case (`uniform_neqs`); a positive document satisfies both, so
    every draft-1 statement is recovered where it was true.
19. **The envelope is a second binding, not a change to P0's.** P0's certificate binding is frozen and stays the
    inner binding; the envelope `(environment_id(E), document_id(D))` is checked beside it as the norms envelope
    is (`VE.Norms.Replay.outerBound`), because ordinal generated names make the inner binding blind to some
    document changes (1.5, fixture φ).
20. **Every top-level unit sits in one sequence.** `ReportDoc.units` is one list in document order (report,
    assessment and negated units together), so `premises D` has a definition that does not interleave two
    lists, and a negated unit's label follows its operand's kind.
21. **The premise-subset device `D ▷ U` has its properties on documents with no `says` key.** The third
    verification found that a registration unit, itself a `says` report of `the_article` in `c3`, can reproduce
    and so assert a dropped `says` key (B₁). Rather than reserve a holder and a context for registration, or add a
    fourth hypothesis to every independence fixture, the construction stays as it is and its three properties
    (registration asserts nothing, a dropped key leaves `topKeys` exactly when no kept unit asserts or denies it,
    names are preserved) are stated for the fragment the four independence fixtures occupy; a document with a
    `says` key states its independence claims over itself or over an explicit sub-document (10.1, 10.3). Every
    biconditional and negative claim of the specification was audited at the same time and now carries its
    fragment (section 0, "Fragments"); none was broadened, and the two that were over-broad for positive
    documents as well (a report "never entails" its content, 4.5; the checklist's "one situation" line, 2.3) are
    restricted to contents that are not valid on their own (B₆).
22. **Entailment claims are over the report premises and for formula contents over `E`.** The fourth
    verification found that 5.3's "exactly when" admitted a nested assessment content, whose elaboration is a
    generated atom that another unit may assert (B₇), and that the checklist's situation line promised a source
    model for a nested content that another unit asserts (B₁). Both are now stated for formula contents over
    `E`, which is what `reports_no_leak` and the non-factivity theorems cover, with a nested content deferred to
    its own key (draft 6's reading of that deferral, "entailed when a top-level unit asserts that key", was the
    fifth verification's finding and is replaced by 13.23: the holder-applied atom, never the key); every
    entailment claim of 2.3, 4.5 and 5.3 names `Γ_reports(D)` as its premise list, since the author's premises
    may entail what the report premises do not (B₈ is `D_π`); and B₂ forces the renumbering it exhibits with a
    fourth context, `c4`, so that the nested `says` key sorts after the registration key whatever the content
    ids. Nothing was broadened.
23. **Normative content is definitions, theorem statements and fixtures; nested-content entailment is on the
    holder-applied atom with its polarity.** The fifth verification found that "asserting the inner key entails
    the nested content" (draft 6, 4.5 and 5.3) is false: a key omits the holder, so B₇ with u1's holder changed to
    `the_team` (B₉) asserts the key and leaves u2's content, the atom at `anthropic`, free; and `D_ω` nests the
    negation of the belief u2 asserts, so its content is refuted, not entailed. The orchestrator's directive made
    the repair a class rule rather than a sixth rewording: the normative semantic content is the definitions, the
    theorem statements with every hypothesis explicit and the fixtures (section 0); every prose "entails", "iff",
    "exactly when" and "no …" claim is either the reading of a named theorem under that theorem's hypotheses or
    deleted, never replaced by new prose; nested-content entailment is stated as four theorems on the
    holder-applied atom, positive and negated nested nodes separately (`nested_positive_entailed`,
    `nested_positive_refuted`, `nested_negated_entailed`, `nested_negated_refuted`), each taking a top-level
    unit's statement, holder and polarity included, and freedom of an atom whose key another holder asserts as
    `holder_atom_free`, whose hypothesis is on the signed premises and not on `topKeys`;
    `no_closure_under_consequence` and `nested_independent` gained the `holderSort` hypothesis that ties their
    key's sort to the holder named; 4.5 is NON-NORMATIVE and 4.6 holds, as open questions, the readings no
    statement covers. Boundary fixtures B₉ to B₁₁ each break one hypothesis of a nested-content theorem (holder,
    polarity), B₉ being the verification's counterexample; this draft's depth fixture broke two hypotheses of
    `nested_independent` and is B₁₂′ since 13.24. Nothing was broadened.
24. **A boundary fixture names the one hypothesis it breaks; a theorem is weakened to the admitted bound, never
    the bound tightened.** The sixth verification found three instances of the directive's class: (1)
    `content_depth_bounded` said `< 16` where 4.1 step 4 and 11.1 admit `≤ 16`, and a document of fifteen negated
    nested reports over a formula (content depth 16, W2 kind depth 16, negation transparent to both) is admitted
    and falsified it; (2) B₁₂ was offered as breaking one hypothesis of `nested_independent` while breaking two
    (`hb`, the shape, and `hin`, the key's freedom, since its u2 asserts the innermost key), as were B₁₁ and
    `D_ω`; (3) the plan's summary kept two unconditional semantic sentences. The repairs: `Content.depth` is
    defined (9.1: a leaf one, a report or assessment node one more than its body, a negated node nothing) so that
    a well-formed unit's content depth is its W2 kind depth, whose frozen decoder admits exactly 16, and the
    theorem is stated at `≤ 16` with B₁₃ attaining it and B₁₃′ rejected by W2's kind bound first; the
    one-hypothesis boundaries of `nested_independent` are the single-unit documents B₁₁′ (a negated inner node)
    and B₁₂ (depth 2), in which the nested key is asserted and denied by nothing, while B₁₁, `D_ω` and B₁₂′ (the
    former B₁₂) are recorded as instances of the nested-content theorems that break two hypotheses of
    `nested_independent`; 10.3 closes with a table naming, for every boundary fixture, the theorem and the one
    hypothesis it breaks, so that "exactly one" is checkable against the statements of 9.2 and not against prose;
    and the plan's summary is reduced to pointers at the statements, with every semantic sentence of the plan
    NON-NORMATIVE on the terms of section 0. The admission bound was not tightened to `< 16`, which would have
    rejected documents 4.1 admits today; the theorem was weakened to what admission guarantees. Nothing was
    broadened.
25. **An instance claim unifies the fixture's content with the shape hypothesis literally, act included; a
    fixture's depth is `Content.depth` computed.** The seventh verification found two fixture assertions
    incorrect, neither a theorem statement, a definition nor an expected verdict: (1) the table of 10.3 listed B₂
    as an instance of `nested_independent` with every hypothesis satisfied, while that theorem's `hb` fixes the
    inner node's act to `believes` and B₂'s inner node is a `says` report; B₂'s expected freedom was and is
    `unreported_key_free`'s at its nested key, so B₂ is recorded as breaking exactly `hb` (the inner act; `hs₂`,
    `hin`, `he` and `hn` hold), in its row, in 4.5's bullet, in 10.3's intro and in its own definition and
    expectation, and `D_ζ` is the theorem's one listed instance; (2) B₁₂ stated a content depth of 3 where
    `Content.depth` (9.1) gives 4, three report nodes over the formula leaf, as does its W2 kind; B₁₂ says 4 and
    distinguishes its nesting depth of 2, the report nodes below the top-level one, from its content depth. Both
    are the directive's class: a fixture assertion is checked against the statement or definition it cites, not
    against the prose around it. Nothing was broadened.
26. **A digest or name conclusion is under the occurrence of both compared objects; the collision check is
    document-local.** The eighth verification found that `literal_paraphrase_distinct`'s digest conjunct took
    as hypotheses that both complement ids appear in `keys D`, which does not put both canonical complement
    objects in the document: a document holding `(b, l₁)` and no `(b, l₂)`, the two digests coinciding,
    witnesses both premises with one key and falsifies the conclusion, and the admission check, which digests
    only what the document contains, cannot detect it; the key-membership hypotheses of
    `negation_scopes_distinct` and `probably_not_scopes_distinct` had the same gap. This is the directive's
    class: three digest conjuncts claimed what the definition of `WellFormedReports` does not give, an
    unsupported collision-freedom assumption about an absent object. The repair: the objects the collision check
    compares are named in the definition (1.1, 3.4, 4.1 step 4: the content object of every node and the
    complement object of every report node, nothing else), `OccursComplement` is defined beside `Occurs` (9.1)
    and `no_collision_complement` beside `no_collision` (9.2); the three theorems keep their canonical-object
    conjuncts unchanged and take, for their digest and name conjuncts, the occurrence in the document of both
    compared objects (`OccursComplement D b l₁` and `OccursComplement D b l₂`; a belief node over `¬q` and one
    over `q` in one context with holders of the sort named; a `probably` node over `¬q` and one over `q`),
    hypotheses strictly stronger than the key memberships they replace, since an occurring node puts its key in
    `keys D` or `akeys D`, so no claim is broadened. The alternative the finding offered, keeping only the
    canonical-object conjuncts, was not taken because ε and μ use the name conclusions and satisfy the occurrence
    hypotheses. B₁₄, B₁₅ and B₁₆ each break exactly the occurrence hypothesis of the absent object (a literal
    quotation alone, `D_ε`'s u1 alone, `D_μ`'s u3 alone); B₁₄′, `D_ε` and `D_μ` are the instances; and what the
    definitions leave for two occurring objects with one digest is the rejection of the document, never a merged
    key (B₁₄′). No SHA-256 collision was computed or assumed.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-28 | Draft 1 | Item-1 specification from attribution-PLAN.md revision 2: contents, occurrences and keys with tense in the context; the four acts and the complement forms; open assessments with W2's complete record and `unresolved_decider`; `E_reports` and generated names; the English table with the "According to the stated assessment" templates, the past-tense row, the parser binding and the round-trip contract; wire form and identity; the independent semantics `(S, J, A)`, `elab`, `interp`, `restrictJ`; the `Layer.id` route instance with report atoms in `Γ`; `reports_elaboration_faithful` and `reports_old_language_conservative` as the first Lean statements, with `reports_no_leak`, the structure theorems, scoped checks, bridges by path, assessments and the wire; status and residual lines; diagnostics; fixtures α to ψ with definitions separated from expectations; limits, the composition gate and the trust list; resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-28 | Draft 2 | The converged FIX of the Astra/Fable statement review (`manage-agents/debates/attribution-spec/`, CONVERGED after round 3), nine edits: (1) `J` and `A` typed and indexed by the complete key (sort included), `restrictJ` guarded by `keys D` and the domain, typed arguments in every correspondence statement (4.2, 4.3, 9.1, 9.2); (2) `reports_no_leak` restated with `neqs` (signed atoms force holder disequalities; P0 has no distinct-name assumption), `SignedAtom` defined by shape, `Expandable` as the hypothesis of every model-existence theorem, `reports_route_acceptance_base` carrying `neqs (premises D)`, positive documents recovering the draft-1 statements (4.4, 9.2, 9.3); (3) recursive negation: the statement grammar, the `negated` wire form, `elab` through `not`, recursive `Sat` in `IntendedReports`, a nested-negation wording row, one unit sequence, kinds and paths transparent to negation, other connectives deferred (1.1, 2.1, 3.3, 4.1 to 4.3, 13.15, 13.20); (4) the reports envelope `(environment_id(E), document_id(D))` as a checked second binding, identity theorems on canonical objects with `HashCollision` rejection, name distinctness on the document's keys, per-act numbering (1.5, 3.4, 9.2, 9.3, 13.19); (5) nested bridges as `bridge:accepts_at(<holder>,<unit>,<path>)` with explicit unit and path fields beside the frozen root label, assessment nodes bridgeable by any agent, "the record's decider" dropped, 13.8 corrected (3.2, 5.2, 9.1, 9.3); (6) the reports gate around the frozen `classify`, `data@0` rejected (4.1, 9.4, 11.3); (7) non-factivity theorems on formula contents with `M.S = S₀` (9.2, 9.3); (8) fixtures: β registers by nesting, λ with a package statement and `Background(E_q)`, `publishes(organisation, service)` in δ and τ, σ under the restricted act check, ψ(b) rejection and ψ(c) minimal block, μ split into μ, μ′, μ″, independence expectations over named premise subsets, φ through the envelope, ω added (10); (9) exactness: `admit_report_sound` mirrored conjunct for conjunct, `reports_labels_decoded` stated, `finite_witness_decodes` and `scoped_witness_sound` at every universe, `AgreeOn` and `openTerms` defined, every free variable bound, `h` no longer reused. Scoped checks run under the pinned route's background (5.1). Boundary, status table and plan obligations unchanged. Spec only. |
| 2026-09-28 | Draft 3 | The three findings of the read-only verification of draft 2 against the converged FIX (`manage-agents/attribution-p3ver1.final.md`, FAIL on commit `078de15`): (1) independence fixtures γ, ε, η and μ restated over explicit premise subsets `D ▷ U` that keep the queried keys in the vocabulary by registration under a `says` report (10.1, the device of fixture β): γ no longer requires an asserted atom false, η keeps the past premise and drops the present one, ε and μ no longer use the empty document, and each names the subset over which no certificate replays (9.2, 10.2, checklist 15); (2) `SignedAtom` requires a well-formed atom (a generated predicate applied to a declared constant of its sort), so `reports_no_leak` is stated over well-formed signed atoms and `neqs R` is well-formed over `E` (`neqs_wellFormed`; 4.4, 9.1, 9.2, 13.18, checklist 8); (3) `scoped_background_local` restated as no automatic insertion: a quoted definition premise is never among the literals or report premises and is in `checkedList D Γ` only when the author wrote it into `Γ` (5.1, 9.3, fixture λ, checklist 10). Spec only; the plan's pointer moves to draft 3. |
| 2026-09-28 | Draft 4 | The two findings of the second read-only verification (`manage-agents/attribution-p3ver2.final.md`, FAIL on commit `b4b5d22`), both in the registration specification of 10.1: (1) registration keeps a dropped key in the vocabulary but does not by itself remove it from `topKeys (D ▷ U)` or `topAKeys (D ▷ U)`; a dropped key is outside them exactly when no kept unit asserts or denies it (over `D_γ ▷ [u2]`, u3's key is u2's and stays asserted), and every independence expectation is stated to query only such keys (9.2, 10.1, 10.2 γ, checklist 15); (2) registration is one unit per omitted unit, so `D_γ ▷ [u1]` has two identical registration premises and its `Γ` lists three entries with two distinct formulas, and `D_γ ▷ [u2, u3]`'s `Γ` is listed (10.1, 10.2 γ). The countermodels, ε, η, μ, `SignedAtom`, `neqs` and `scoped_background_local` are unchanged. Spec only; the plan's pointer moves to draft 4. |
| 2026-09-28 | Draft 5 | The finding of the third read-only verification (`manage-agents/attribution-p3ver3.final.md`, FAIL on commit `0d8836e`) and the audit it prompted. (1) 10.1: a registration unit is itself a `says` report of `the_article` in `c3`, so it can reproduce and assert a dropped `says` key (the finding's `D ▷ []` over "Anthropic believes that the service is safe" and "The article says that Anthropic believes that the service is safe"); the construction stays, and its three properties (registration asserts nothing, a dropped key leaves `topKeys` exactly when no kept unit asserts or denies it, names preserved) are stated for documents with no `says` key, which γ, ε, η and μ are, with the boundary in fixtures B₁ (top-level `says` key reproduced) and B₂ (nested `says` key renumbered) (10.1, 9.2 prose, 10.2 γ, checklist 15, 13.21). (2) Audit of every "exactly when", "↔", "never", "only" and "no …" claim of this specification and of the plan, each restricted to the fragment on which it holds, never broadened: the "Fragments" convention (0); the semantic reading of the summary (0); "neither entails the other" for literal versus paraphrase over a subset that asserts neither (1.1); the checker's "never" for assessments as the absence of a rule, with entailment deferred to 4.4 (1.4, 5.3); a negated unit's "nothing else" beside the disequality it forces (1.6); the scoped report line's "exactly the selected contents" under `E_q`'s background (2.1, B₅); "no sentence has two encodings" as a design rule with the theorem item 4's (2.1); the checklist's "one situation" line for contents that are neither forced by `neqs` nor valid (2.3, B₄, B₆); `object(formula)`'s environment id and `content_structural` on formula nodes over `E` (3.4, 9.2); the envelope's "invalidates every certificate" absent a digest collision (3.4); `expansion_exists_iff` named for `R = Γ_reports(D)` (4.4, 13.18 unchanged); 4.5 restated with its fragment and boundaries: non-factivity as `Γ_reports(D) ⊨ q ↔ neqs ⊨ q` (so for a positive document exactly when `q` is valid on its own), closure under an unasserted `Q`, nested independence under an unasserted inner key, denial, tense over a positive subset, structural contents over `E`, no generated `required` atom (4.5); inner inconsistency and the outer vacuity line (5.1). (3) New section 10.3, boundary fixtures B₁ to B₆ (nested attribution asserted elsewhere and registration, nested `says` key, asserted belief in `Q`, a content the disequalities force, scoped consequence without `E_q`'s background, a valid content); μ's expectation names the inconsistent boundary; ω′'s `neqs` entry is written as the definition orders it, `¬(anthropic = the_team)`. Spec only; the plan's pointer moves to draft 5 and the plan's page 1 carries the same fragment. |
| 2026-09-28 | Draft 6 | The three findings of the fourth read-only verification (`manage-agents/attribution-p3ver4.final.md`, FAIL on commit `5afac55`) and the second audit pass they prompted. (1) 5.3: "`q` is entailed exactly when `neqs` entails it" is stated for a content `q` that is a formula over `E`; a nested content elaborates to a generated atom of the inner key, entailed when a top-level unit asserts it and free when none asserts or denies it; new fixture B₇ (`May(a1, ⟨believes …⟩)` beside the belief itself: positive, `neqs = []`, the content not valid and entailed). The same restriction is written into 4.5's "not factive" and "denial" bullets and its intro. (2) 2.3: the situation line is for positive report units, is a source model of `Γ_reports(D)`, exists for a formula content exactly when `neqs` does not entail it, and for a nested content when no top-level unit asserts or denies its key, naming the asserting unit otherwise (B₁); the belief line names its two theorems and B₃; negated units get the denied line and no situation. (3) B₂ declares a fourth context `c4` for its nested `says` key so that the registration key precedes it in the key order of 1.5 and the renumbering `reports__says__1` to `reports__says__2` is forced, not permitted (10.1 (iii), 10.3). (4) Audit: every entailment and independence claim of 2.3, 4.5 and 5.3 is over the report premises `Γ_reports(D)`, the author's premises and the literals aside, with `D_π` as the boundary (B₈, section 0 "Fragments"); "neither entails the other" (1.1), "negation scopes" and "tense" (4.5) name a consistent premise set; the nested-content rows of 1.6 and 4.2 and the paraphrase column of 2.1 say that another unit may assert what a node or a wording leaves open; 5.1's "inconsistent only through `neqs`" is stated as `reports_no_leak` with `φ = ⊥` for `Γ` over `E`; 4.4's expansion equivalence names an admissible `S₀`. No claim broadened. Spec only; the plan's pointer moves to draft 6 and its page 1 carries the two restrictions. |
| 2026-09-28 | Draft 7 | The orchestrator's design directive after the fifth read-only verification (`manage-agents/attribution-p3ver5.final.md`, FAIL on commit `fe35218`: asserting the inner key does not entail a nested content at another holder; a negated nested content is false when its operand is asserted). (1) Section 0, "Normative content": the normative semantic content is definitions, theorem statements with every hypothesis explicit and fixtures with expected results; prose readings claim nothing beyond the statement they name; 4.5 retitled and marked NON-NORMATIVE, each bullet reduced to its theorem, that theorem's hypotheses and its fixtures, the key-level nested-content claims deleted; new 4.6 (NON-NORMATIVE) with three open questions; 2.3's situation and belief lines defined by what the IDE runs (countermodel, certificate or UNKNOWN), with the theorems and fixtures deciding which; 1.1, 1.4, 1.6, 2.1, 4.2 and 5.3 pointed at the statements. (2) 9.2: five nested-content theorems on the holder-applied atom with polarity explicit, `nested_positive_entailed`, `nested_positive_refuted`, `nested_negated_entailed`, `nested_negated_refuted` (a top-level unit carrying the very node or its opposite) and `holder_atom_free` (no positive premise at a co-denoting holder); `holderSort` hypotheses added to `no_closure_under_consequence` and `nested_independent`; the prose after the block states that `topKeys` is a hypothesis of the freedom theorems only. (3) 10.3: B₉ (the verification's counterexample, B₇ with u1 at `the_team`), B₉′ (its report form), B₁₀ (the nested positive node denied), B₁₁ (the nested negated node denied; `D_ω` is the asserted case), B₁₂ (depth 2), each breaking one hypothesis; ω's expectation states the refutation; B₁ and B₇ name their theorem instances; checklist items 5, 9, 15, 17 and 18; 13.23. No claim broadened. Spec only; the plan's pointer moves to draft 7 and its page 1 restates its nested-content sentence on the holder-applied atom. |
| 2026-09-28 | Draft 8 | The three findings of the sixth read-only verification (`manage-agents/attribution-p3ver6.final.md`, FAIL on commit `0c1ad1b`), each applied as an instance of the draft-7 directive. (1) `content_depth_bounded` restated at the admitted bound, `∀ u ∈ D.units, u.content.depth ≤ 16`, with `Content.depth` defined in 9.1 (a leaf one, a report or assessment node one more than its body, a negated node nothing) so that a well-formed unit's content depth is its W2 kind depth, which the frozen `decodeKind` admits up to exactly 16; 4.1 step 4 and 11.1 name the definition and the W2 bound that fires first; new fixtures B₁₃ (the verification's document: fifteen negated nested `says` reports over `safe(service)`, depth 16, admitted, the theorem holding with equality) and B₁₃′ (one node more: `ResourceLimit: kind depth exceeds 16` at step 2). (2) One-hypothesis boundaries of `nested_independent`: B₁₂ is now the depth-2 document alone (breaks `hb` only; both nested atoms free by `unreported_key_free`) and the former B₁₂ is B₁₂′ (the depth-2 instance of `nested_positive_entailed`, breaking `hb` and `hin` of `nested_independent`); new B₁₁′, `D_ω`'s u1 alone (breaks `hb` only; the atom free by `all_truth_combinations`), with B₁₁ and `D_ω` recorded as breaking `hb` and `hin` together; 10.3 closes with a table naming, for every boundary fixture of the nested-content theorems, `nested_independent`, `no_closure_under_consequence`, `attitude_not_factive` and `content_depth_bounded`, the one hypothesis it breaks; 4.5's nested-independence bullet, the intro of 4.5, 2.3, section 0, 1.6, 2.1, 4.2, ω and checklist items 9, 15, 17, 18 updated to the new fixture names. (3) The plan's summary and pages carry no unconditional semantic sentence (revision 7). 13.24 added. No claim broadened. Spec only; the plan's pointer moves to draft 8. |
| 2026-09-28 | Draft 9 | The two findings of the seventh read-only verification (`manage-agents/attribution-p3ver7.final.md`, FAIL on commit `5587ec2`), each a fixture assertion corrected to what the definitions and statements give, as instances of the draft-7 directive. (1) B₂ is no instance of `nested_independent`: its `hb` names an inner `believes` node and B₂'s inner node is a `says` report; the closing table of 10.3 lists `D_ζ` alone as the instance and B₂ as breaking exactly `hb` (the inner act) with the expected freedom from `unreported_key_free` at `k_in`, and 4.5's nested-independence bullet, 10.3's intro, B₂'s definition and expectation and checklist 15 say the same. (2) B₁₂'s content depth is 4 under `Content.depth` (three report nodes over the formula leaf; its W2 kind has depth 4 likewise), not 3; its expectation says so and distinguishes the nesting depth of 2 from the content depth. 13.25 added; checklist 17 names it. No theorem statement, definition or expected verdict changed; no claim broadened. Spec only; the plan's pointer moves to draft 9 (revision 8). |
| 2026-09-28 | Draft 10 | The finding of the eighth read-only verification (`manage-agents/attribution-p3ver8.final.md`, FAIL on commit `becf7cb`), applied as an instance of the draft-7 directive: `literal_paraphrase_distinct`'s digest conjunct was stated under key-membership hypotheses that the digest of an absent complement could witness with one key, outrunning the document-local collision check, and `negation_scopes_distinct` and `probably_not_scopes_distinct` had the same gap. (1) Definitions: the objects the collision check of 4.1 step 4 compares are named (the content object of every node and the complement object of every report node, nothing else) in 1.1, 3.4 and 4.1; `OccursComplement` defined in 9.1. (2) Statements: `no_collision_complement` added beside `no_collision`; the digest and name conjuncts of the three theorems restated under the occurrence of both compared objects, hypotheses strictly stronger than the memberships they replace; the canonical-object conjuncts unchanged; the readings of 1.1, 1.5, 3.4, 4.5, 9.2's prose, 9.5, ε and μ name the hypotheses. (3) Fixtures: B₁₄ (a literal quotation alone), B₁₄′ (literal and paraphrase together), B₁₅ (`D_ε`'s u1 alone), B₁₆ (`D_μ`'s u3 alone), each boundary breaking exactly the occurrence hypothesis of the absent object, with the instances B₁₄′, `D_ε`, `D_μ` in the closing table of 10.3; checklist items 1, 15, 17, 18; 13.26. No claim broadened; no digest collision computed or assumed. Spec only; the plan's pointer moves to draft 10 (revision 9). |
