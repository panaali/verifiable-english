# Reports and attitudes (`reports@0`): structured reported content, attitude wrappers and open assessments over `ve-document@1`

> Status: item-1 specification, draft 1 (2026-09-28), written from [attribution-PLAN.md](attribution-PLAN.md)
> revision 2, the transcription of the converged Astra/Fable design debate
> (`manage-agents/debates/design-attribution/{astra,fable}.md`: BUILD after six text edits, CONVERGED after
> round 2). It is the statement under the Astra + Fable item-1 review that gates items 2 to 5 of the plan
> (PLAN-EXPAND2 rule 10) and any implementation. Sections 4 to 6 and 9 are the statements under review; section 10
> gives the fixtures with their definitions (10.1) separated from their expected results (10.2); section 13 lists
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
`(S, J)`, so a report entails neither its content nor any other report, belief is not closed under consequence,
and an intention entails neither success nor obligation. Two open assessments, `May` and `Probably`, are named
open judgments over content with W2's complete open-term record; admission checks their content and declared
criteria and establishes neither possibility nor likelihood. Elaboration generates, for every finite acyclic key
(act or judgment, holder sort, context with its tense, content), one fresh unary predicate in `E_reports`; the
route layer is `Layer.id` over `E_reports`, the report atoms are document premises in `Γ`, and two Lean
obligations carry the meaning: `reports_elaboration_faithful` (truth preservation with model correspondence in
both directions) and `reports_old_language_conservative` (old-language consequence is unchanged). Bridges, norm
adoption and definition import are explicit typed operations that name their exact target; a certificate of
faithful quotation never discharges truth. The English has one reading per wording and round-trips together with
its bound environment, contexts, criteria, versions and reading choices, never through mutable defaults.

In this specification: the report document (1), the English (2), the wire form and identity (3), the semantics
and elaboration (4), scoped checks, bridges and assessments (5), status and coverage (6), the report (7),
diagnostics (8), the Lean definitions and every theorem of plan item 2 as a statement (9), the item-1 acceptance
fixtures (10), limits, regeneration and trust (11), the review checklist (12) and the resolved choices (13).

Out of scope, by the plan: promising, pledging, denying, expecting, reaffirming and determination (distinct
reviewed acts, pending); modal inference of any kind and the candidate possible-worlds profile (plan page 2);
numerical probability; de re and cross-boundary bindings; adoption and import beyond their typed provenance
(5.4); composition with active `norms@0` or `definitions@0` outer layers (11.3); the coverage counting protocol
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
               | a quoted W3 definition package with a pinned local environment E_q (no outer effect)
               | a report node: holder, act, context, content, optional literal words
               | an assessment node: judgment, assessment record, content
content id     sha256 of the canonical content object (3.4): structural identity under the declared
               canonicalisation (P5 normalisation of formulas; canonical W1 and W3 blocks; nested objects inline;
               literal words when present; reading choices when the content was chosen from a set). Never equality
               of truth values, never logical equivalence.
occurrence     one report or assessment unit: the document's source id, the unit's byte span, the context it
               names. Repeated occurrences may share a content id and a key; each keeps its own span.
complement id  the content id of a report node's body together with its literal words when present (3.4): what
               the holder said, believed, wanted or intended, as content
key            report:      (act, holder sort, context id, complement id)
               assessment:  (judgment, assessment id, content id of the body)
               finite (bounded depth and count, 11.1) and acyclic (content ids are hashes of finite trees, and a
               node's content is a strict subtree, 4.1 step 4)
```

Literal quotation binds the exact words into the content id; a paraphrase claims no word identity. The two are
different contents and different keys; neither entails the other (13.6).

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

`May(a, q)` and `Probably(a, q)` are open: the checker never decides them, never relates them to each other or to
`q`, and never reads a threshold, a percentage or an accessibility relation. `May(a, ¬q)`, `¬May(a, q)`,
`Probably(a, ¬q)` and `¬Probably(a, q)` are four different formulas (2.1). Admission checks the structured content
`q`, the record's shape and that its criteria are closed formulas over `E`; it does not establish evidential
possibility or likelihood. The modal profile sketched on plan page 2 is not this profile.

### 1.5 The extended vocabulary `E_reports` and generated names

`E_reports = E + {one unary predicate per key}`, regenerated at every site from `E` and the decoded document,
never taken from the wire. Every generated predicate is a base predicate (not regulated, not defined, no data
flag) with arbitrary interpretation. Names are identifiers of the existing grammar, at most 64 bytes, injective
over the namespace and regenerable without a table:

```text
key order          report keys sorted by (act, holder sort, context id, content id); assessment keys sorted by
                   (judgment, assessment id, content id); k is the 1-based position
reports__<act>__<k>        the report predicate of the k-th report key, on the key's holder sort
reports__<judgment>__<k>   the assessment predicate of the k-th assessment key, on the evidence sort
```

Under `reports@0` an author predicate beginning with `reports__` is rejected (`InvalidInput: author predicate <p>
begins with reports__`), so generated and author names never collide. Adding a report renumbers; every certificate
is already invalidated by such a change (3.5). Every report and residual line renders the source key beside the
generated name (`reports__believes__3` as "believes, organisation, context c2 (past), content ‹Claude was
helpful›"); `J_{act,c,q}(h)` and `May(a, q)` in this specification are that rendering.

### 1.6 What reports@0 adds to a document, in one table

| Object | Where | Effect on the checked premise set `Γ` |
|---|---|---|
| report unit | a unit with `report` content | one atom `J_{act,c,q}(h)`, labelled `report:<unit>` |
| assessment unit | a unit with `assessment` content | one atom `May(a,q)` or `Probably(a,q)`, labelled `assessment:<unit>`; one open term in the residual |
| nested content | inside a report or assessment | nothing: it is content; a bridge is needed to use any part of it |
| scoped check | front matter `scoped` | nothing: a report about the contents, computed in the content's environment |
| bridge | a graph leaf `bridge:accepts(<holder>,<path>)`, with a record for nested paths | exactly the elaborated formula at the path, as a labelled assumption |
| quoted norm block or definition package | content | nothing: a local check only; no layer, no `background:definitions` premise |

## 2. The English (one reading each; rejected as today when `reports@0` is off)

### 2.1 Wordings

Names are declared holder constants rendered by the environment legend; contexts are chosen from the declared
records and shown in the inspector; the verb form carries the context's tense. `S` is any sentence the reports
surface admits as content (a formula sentence of the existing grammar, or a nested report or assessment wording).

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
| `<Holder> says, "W".` (literal) | <Holder> said exactly the words W, whose content is S (shown); the words are bound. | `J_{says,c,q_W}(h)`, `q_W` binds `W` |
| `According to the stated assessment, it may be that S.` | The assessment on record for this unit (criteria …, decided by …) holds that S may be so; the checker establishes neither that S is possible nor that it is likely. | `May(a, q)` |
| `According to the stated assessment, it is probably the case that S.` | likewise, "probably". | `Probably(a, q)` |
| `According to the stated assessment, <Subject> may <VP>.` / `… <Subject> is probably <Adj>.` | the rendered form of the two rows above when S is one positive atomic sentence; same reading. | same |
| `According to the stated assessment, it may be that it is not the case that S.` | the negation is inside the assessment. | `May(a, ¬q)` |
| `It is not the case that, according to the stated assessment, it may be that S.` | the negation is outside. | `¬May(a, q)` |
| `Context c: <description>; tense <tense>[; reference time <tag>].` (inspector legend) | Names the context the verb form refers to; the tag is a label, not a date. | context record |
| `For this argument, <reviewer> accepts as true what <Holder> says in <unit>: S.` (rendering of a bridge leaf) | S is assumed for this argument on <reviewer>'s responsibility, with occurrence, content identity, environment, choices and reason recorded; nothing else in <unit> is assumed. | `bridge:accepts(h, u)` |
| `For this argument, <reviewer> accepts as true what <Holder2> believes according to <Holder> in <unit>: S.` | the nested payload is assumed; that <Holder2> believes it is not. | `bridge:accepts(h2, u.1)` |
| `S follows from the reported contents <paths>.` (report line, never writable) | Under the payloads' own environment, S is a consequence of exactly the selected contents; nothing about the outer document or the holder's beliefs follows. | scoped check FOLLOWS |

The act is fixed by the verb: `says`, `believes`, `wants`, `intends` and their past forms. `may` and `probably`
are assessment words only inside the `According to the stated assessment` template; the parser binds "the stated
assessment" to the unit's assessment record, never to a holder, and no holder may display as "the stated
assessment" (`InvalidInput: holder verbalisation reserved`). `may not` and `probably not` are rejected with the two
rewrites (negation inside, negation outside). W1's `Every <noun> may <act>` is a rule block (norms.md 2.1) and is
not a reports wording; the all-derivations gate rejects any input that derives both.

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

For every report unit the IDE shows, in English only: the paraphrase of 2.1; "claimed: that <Holder> <act>
…; not claimed: <S>; not claimed: any other belief or statement of <Holder>"; one situation in which the report
holds and S is false; for a belief, one situation in which <Holder> believes P and believes that P implies Q and
does not believe Q; for a nested report, which bridge would assume which sentence; for an intention, one situation
in which the act never happens and nothing is required; for a literal quotation, the exact words beside the
content. For every assessment unit: the record's criteria, factors and decider (or "the source names no
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
"bridges": [{"id": "b1", "target": "u7.1", "accepted_by": "reviewer_ann", "reason": ["u9"]}],
"scoped": [{"id": "s1", "payloads": ["u3", "u4"], "conclusion": {"ast": ["unary", "safe", ["const", "service"]]},
            "certificate": null}]
```

`contexts`: distinct token ids (at most 256), `tense` one of the three values, `reference_time` a token or `null`
(no `time@0` dependency: the tag is opaque), `description` at most 200 bytes. `assessments`: distinct ids (at most
256), `context` a constant of the evidence sort, `decided_by` a token (the literal `unresolved_decider` when the
source names none; an absent field is `InvalidInput: assessment <a> needs decided_by`), criteria closed formulas
over `E` (P0 wire form), the other fields as W2's open-term schema (`ve/openterms.py`). `bridges`: a record per
nested target (`<unit>.<i>…`); a root target (`<unit>`) may have one and needs none (legacy). `scoped`: payload
paths whose contents are formula nodes over one environment, a closed conclusion over that environment, an
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

Content forms: `{"ast": …}` or `{"fence": "<id>"}` with `surface` (a closed formula over `E`, admitted through
the existing all-derivations parser and bound by `meaning_id`); `{"norm": {"environment": {…}, "norms": […]}}` and
`{"definition": {"environment": {…}}}` (a pinned local environment `E_q` inline with its own `environment_id`,
validated by the unchanged W1 and W3 validators, contributing no layer and no Background premise outside);
`{"report": …}` and `{"assessment": …}` recursively. The W2 `kind` must agree with the content tree:
`attributed(<holder>, <act>, k)` for a report node and `hedged(could, k)` / `hedged(likely, k)` for `may` /
`probably` (`KindMismatch` otherwise); under `reports@0` the kind decoder accepts the act `wants` (13.2), and the
frozen decoder outside the profile is unchanged. A unit of kind `attributed` or `hedged` with no `report` or
`assessment` content is what it is today: LABELLED metadata. The `meaning` of a report unit is `specified` when
every formula node is closed over declared vocabulary, `{"open": [...]}` when a content or an assessment
introduces open terms; an assessment unit always lists its generated open term. `support` is the author's, as
today (`testimony` for the pilots).

### 3.4 Identity

```text
content_id(x)  := sha256("ve-content-<identity_version>\n" + canonical(object(x)))
  object(formula)     = {"environment_id", "ast"}                     (W2's meaning_id input, so a formula content's
                                                                       content_id equals its meaning_id domain-shifted)
  object(norm)        = {"environment_id": E_q's, "norms": canonical W1 blocks}
  object(definition)  = {"environment_id": E_q's}
  object(complement)  = {"content": object(inner), "literal"}                    its hash is the complement id
  object(report)      = {"holder", "act", "context": the context record, "complement": object(complement)}
  object(assessment)  = {"judgment", "record": the assessment record, "content": object(inner)}
  plus "choices": the reading-set choices (set@version:choice) under which any content node was selected, when any
meaning_id(u)  := sha256("ve-meaning-<identity_version>\n" + canonical({"environment_id", "ast": object(u.content)}))
                  for a report or assessment unit, over the author's environment_id
document hash  := the canonical array of unit objects, contexts, assessments, bridges and scoped checks in document
                  order under environment_id
```

`E_reports`, its generated names, the open-term records of the assessments, `Γ_reports` and every bridge formula
are regenerated from these at every site. A certificate binds the full regenerated `E_reports`
(`environment_id(E_reports)`), the ordered premise list `Background(E_reports) ++ Γ_reports ++ Γ` and the
conclusion by meaning id (P0 3.9). Changing a holder, an act, a context's tense or tag, a content node, the literal
words, a reading choice, an assessment record or the environment invalidates every certificate of the document
(fixture φ).

### 3.5 Strict text

There is no strict text for report units beyond W2's: the wire form is the JSON of 3.3 and the English of 2.1 is
the writable form; `{"fence": …}` content inside a report node is parsed by the existing strict or English parser
as today. Contexts, assessments, bridges and scoped checks are front matter only.

## 4. Semantics and elaboration

### 4.1 Well-formedness (`WellFormedReports`)

A report document `D = (E, contexts, assessments, units, bridges, scoped)` is well-formed when, in this order:

1. `E` enables `reports@0` and `relational-fol@0`; the `reports` block decodes (3.1); no author predicate begins
   with `reports__`; no holder verbalisation is "the stated assessment".
2. Every W2 check passes (spans, kinds, open terms, reading sets); every `attributed` kind's act is in the
   profile's act list.
3. Contexts and assessments decode (3.2); every assessment's criteria are closed and typed over `E`; every
   `decided_by` is a token.
4. Every content tree decodes: depth at most 16 (`ResourceLimit: content depth`), each formula node closed and
   typed over `E` (or over its pinned `E_q` for norm and definition nodes, which are validated by the unchanged W1
   and W3 validators without composing any layer), each report node's holder a constant of a holder sort
   (`UnknownHolder`, `HolderSort`), its act in the list (`UnsupportedAct`), its context declared
   (`UnknownContext`), each assessment node's record declared (`UnknownAssessment`); the W2 kind matches the tree
   (`KindMismatch`); the content graph is acyclic by construction and the content-id table computed from the
   decoded trees has no forward reference (`DependencyCycle: <sorted content ids>` through the shared
   `dependencyOrder`, reachable only from a malformed wire).
5. Every scoped check's payload paths resolve to formula nodes over one environment (`ScopedEnvironment`,
   `ScopedTarget`); its conclusion is closed over that environment; payload count at most 64.
6. Every bridge record's target path resolves (`BridgeTarget`), is a formula or report node (`BridgeKindMismatch`
   for a norm or definition node), and every nested bridge label in the graph has a record (`MissingBridgeRecord`).
7. `E_reports` is a valid environment (identifier lengths, predicate count within `MAX_PREDICATES`;
   `ResourceLimit` otherwise).

### 4.2 The independent semantics: a source model `(S, J, A)`

```text
S     an admissible structure over E (the author's environment; holders and evidence contexts are constants)
J     act → context id → content id → holder element → Prop            arbitrary
A     judgment → assessment id → content id → evidence element → Prop   arbitrary
```

`J` and `A` are relations with no closure conditions: no factivity, no consistency, no closure under consequence,
no link between tenses, between acts, between `may` and `probably`, or between literal and paraphrased contents.
The **intended meaning** of a document is:

```text
IntendedReports D (S, J, A) :=
  ∀ report unit u of D, ∀ v, S.constant u.holder = some v → J u.act u.context (content_id u.content) v
∧ ∀ assessment unit u of D, ∀ v, S.constant (record u).context = some v → A u.judgment u.record (content_id u.content) v
```

Only the document's top-level units are asserted; nested nodes are contents and constrain nothing. Consequently
every admissible `S` extends to a source model of `D` (`source_over_any_structure`, 9.2), which is the single
theorem behind non-factivity, non-closure, nested independence and harmless inconsistent quotation.

### 4.3 Elaboration

```text
elab(formula E φ)                 = φ
elab(report h act c body lit)     = J_{act, sort(h), c, complement_id(body, lit)}(h)   an atom over E_reports
elab(assessment j a body)         = A_{j, a, content_id(body)}(context(a))              an atom over E_reports
elab(norm …) = elab(definition …) = none                                                 no formula; local checks only
Γ_reports(D) := [elab(u.content) : u a top-level report or assessment unit of D, in document order]
```

`elab` is total on formula, report and assessment nodes and every atom it produces is well-formed over
`E_reports` (`premises_wellFormed`). Boolean structure around a report ("it is not the case that …") is the
existing FOL; no truth predicate, dynamic quotation or proof rule is added.

Interpretation and restriction, the two directions of the model correspondence:

```text
interp (S, J, A)   the structure over E_reports that agrees with S on E and interprets
                     J_{act,s,c,q} by {v | J act c q v}   and   A_{j,a,q} by {v | A j a q v}
restrictJ S′       the source model (forget (names D) S′, J, A) with
                     J act c q v := S′.relation (name of the key) [v] when the key is in keys D, else False
```

`reports_elaboration_faithful` (9.2): `Sat (interp M) Γ_reports(D) ↔ IntendedReports D M` for every source model
`M`, and `Sat S′ Γ_reports(D) ↔ IntendedReports D (restrictJ S′)` for every admissible `S′` over `E_reports`;
`restrictJ ∘ interp` is the identity on the keys of `D` and `interp ∘ restrictJ` is the identity on the relations
of `S′`; old formulas keep their truth value across `interp`; every valid finite model over `E_reports` decodes
to a source model. This is truth preservation with model correspondence in both directions and finite witness
decoding, and it is stated at every universe.

### 4.4 The route instance and conservativity

When no deterministic layer applies (no active `norms@0` or `definitions@0` layer; 11.3), the route is

```text
reportsRoute D := folLayer (envReports D) D.lits          P0's FOL route at E_reports, which is by definition
                                                          Layer.id (envReports D) (StringAdmissible (envReports D) D.lits) _
premises        [] ; Γ := Γ_reports(D) ++ Γ_author       (document premises: the report atoms, then the author's)
background      literals D.lits                           (the literal distinctness premises of the FOL family)
```

`Layer.id`'s `Intended` is `True`: it says that the empty layer means nothing, and it is not the meaning of a
report; the meaning is `IntendedReports` through `reports_elaboration_faithful`, which composes with
`route_acceptance` (`reports_route_acceptance`, 9.3) and with finite countermodel decoding
(`reports_route_countermodel`). Existing deterministic layers keep their own contracts.

`reports_old_language_conservative` (9.3): for `Γ` and `φ` over the old language `E`, `Entails E_reports Γ φ ↔
Entails E Γ φ`. The proof is existence of expansion (`expansion_exists`: every admissible `E`-structure expands to
an admissible `E_reports`-structure satisfying `Γ_reports(D)`) plus `restrict_holds`; uniqueness is neither
claimed nor true, because the fresh relations are arbitrary. Its corollary `reports_no_leak`: a consistent set of
report literals (atoms of `Γ_reports(D)` and their negations, no atom on both sides) added to old-language
premises changes no old-language verdict; when the literal set is inconsistent the P0 vacuity report says
INCONSISTENT and every dependent certificate is `vacuous`, visibly.

### 4.5 What the structure theorems say, in words (each an instance of 4.2 in 9.2)

- **Not factive.** For any admissible `S₀` in which `q` is false, there is a source model with `S = S₀` in which
  every report of `D` holds; so `J_{says,…,q}(h)` never entails `q`, nor does belief, desire or intention.
- **Not closed.** With beliefs in `P` and in `P → Q` recorded, the belief in `Q` is a key not in `D`, and
  `unreported_key_free` gives a source model with that relation empty.
- **Nested independence.** `says(article, believes(anthropic, q))` constrains only the outer key; the inner belief
  atom and `q` are free.
- **Negation scopes.** `J_{believes,c,¬q}(h)` and `¬J_{believes,c,q}(h)` are different atoms (different content
  ids); any of the four truth combinations is realised by a source model.
- **Tense.** `c` (past) and `c′` (present) give different keys; a past report never entails a present one.
- **Contents are structural.** Two contents that are canonically distinct formulas, even logically equivalent
  ones, have different keys; canonically equal ones share a key.
- **Intention is not fulfilment or obligation.** `J_{intends,c,q}(h)` with `¬q` is consistent; no `required` atom
  exists unless `norms@0` supplies one, and then only from a rule.

## 5. Scoped checks, bridges, assessments, adoption and import

### 5.1 Scoped consequence and inner consistency

A scoped check selects payloads by path (occurrence-qualified content nodes, so two occurrences of one content
are two payloads and sharing a holder merges nothing) and asks, in the payloads' own environment `E_q`, whether
the conclusion follows:

```text
FOLLOWS               a certificate for  E_q, payloads ⊢ conclusion   (unchanged tableau checker at E_q)
DOES NOT FOLLOW       a checked finite model over E_q satisfying the payloads and refuting the conclusion
PAYLOADS INCONSISTENT a certificate for  E_q, payloads ⊢ ⊥   (reported once per payload set; dependent scoped
                      results are vacuous)
UNKNOWN               budget named
```

Display: "S follows from the reported contents ‹paths›." Never "the speaker believes S", "the article says S" or
bare S. A scoped check is a report line: it is not in `Γ`, not in `E_reports`, not a premise of anything
(`scoped_not_premise`), and an inconsistent payload set makes nothing outside vacuous (`quoted_inconsistency_local`).
Vacuity of the *inner* set is shown with the check; vacuity of the *outer* premise set is P0's line (7.1).

### 5.2 Bridges are explicit premises with an exact target

```text
path        <unit>                 the unit's root complement (legacy meaning: W2's QuotedUnit rule, unchanged)
            <unit>.1, <unit>.1.1…  the complement of the nested report or assessment node reached by descending
                                   into the complement once per ".1" (every node has exactly one complement)
holderAt p  the holder (or, for an assessment node, the record's decider) of the node whose complement p names
formulaAt p elab(content at p)     none for a norm or definition node
bridge leaf a graph leaf labelled bridge:accepts(<holder>,<path>) with formula = formulaAt p and holder = holderAt p;
            a nested path needs a bridge record (3.2) naming reviewer and reason
```

Accepting the article's complement in "the article says that Anthropic believes that q" (path `u`) assumes the
belief atom `J_{believes,c′,q}(anthropic)`; accepting the payload (path `u.1`) assumes `q`; neither assumes the
other, and accepting that a report occurred needs no bridge at all, because the report atom is already the
document's premise `report:<unit>`. An independent proof of a payload is cited with all its dependencies
(`cite:`) instead. Testimony, prestige, a URL and a certificate of faithful quotation never discharge a bridge:
it stays in the assumption list of every report that uses it and propagates through citations (`admit_report_sound`
and `CitationsClosed`, unchanged). Root-path bridges keep the legacy `bridge:accepts` meaning byte for byte
(`bridge_root_is_legacy`); the nested form is a new label meaning under the profile, never retrofitted.

### 5.3 Assessments

Each assessment unit contributes one atom `May(a, q)` or `Probably(a, q)` to `Γ` (labelled `assessment:<unit>`)
and one open term to the residual: name `reports__<judgment>__<k>`, arguments `[<evidence sort>]`, and the record's
`decided_by`, criteria, factors, precedents, jurisdiction and version (W2's complete schema). The atom is an
assumption like any premise: "the assessment on record holds that q may be so". The checker never derives `q`,
`Probably(a, q)` from `May(a, q)`, `May(a, q)` from `Probably(a, q)`, or anything from the criteria beyond what
their formulas say when the author writes them into `Γ` (they are not premises by themselves; 13.5). The status
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
| report wrapper whose complement is unformalised | MIXED: the wrapper bytes LABELLED (`attributed` metadata: holder, act, occurrence), the complement bytes UNFORMALISED with the reason | by part |
| unit with a reading set over contents or acts | READINGS per W2; unelaborated alternatives earn nothing | whole span |
| attributed or hedged kind with no content | LABELLED, as today | whole span |

A wrapper alone never upgrades a span: the complement's bytes take the complement's status, and a passage whose
source meaning is missing keeps its residual (plan page 4, accounting gate). Recursive complements add no bytes;
scoped checks add none. Residual lines beside W2's (open terms, assumptions, bridge leaves, unresolved reading
sets): `reports` (report premises by act and tense), `assessments` (by decider, `unresolved_decider` counted
separately), `bridges_nested` (with targets), `scoped_checks` (with inner status), `literal_quotations`,
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
SCOPED <id>: FOLLOWS from <paths> (certificate <id>) | DOES NOT FOLLOW (model <id>) |
             PAYLOADS INCONSISTENT (certificate <id>) | UNKNOWN (<budget>)
BRIDGE <label>: assumes <sentence> at <path> for <reviewer>, reason <units>; not discharged
ASSESSMENT <unit>: OPEN; <judgment> per assessment <a>, decided by <decider>; admission establishes neither
                   possibility nor likelihood
PREMISES: model <id> | INCONSISTENT(<certificate>) | UNKNOWN(<budget>)        (P0's line, unchanged)
```

## 8. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: reports@0 requires relational-fol@0` / `reports@0 needs a reports block` / `reports@0 with <profile> layers` | profile gate; block absent; an active `norms@0` or `definitions@0` outer layer (11.3) | error |
| `UnsupportedAct: <act> (reports@0 admits says, believes, wants, intends)` | a `report` block naming another act | error |
| `UnknownHolder: <name>` / `HolderSort: <name> is not of a holder sort` / `UnknownSymbol: holder sort <s>` / `UnknownSymbol: evidence sort` | holder or sort declarations (3.1, 4.1) | error |
| `UnknownContext: <c>` / `ContextTense: <c>` / `UnknownAssessment: <a>` / `DuplicateDeclaration: context <c>` / `assessment <a>` / `bridge <b>` / `scoped <s>` | front matter (3.2) | error |
| `InvalidInput: assessment <a> needs decided_by` / `author predicate <p> begins with reports__` / `holder verbalisation reserved` / `invalid content for <unit>` | field consistency | error |
| `KindMismatch: <unit>` | W2 kind and content tree disagree (3.3) | error |
| `OpenComplement: <unit>` | a content formula is not closed, or a name is unresolved, or a binder crosses a node | error |
| `ScopedEnvironment: <s>` / `ScopedTarget: <s>, <path>` | payloads over two environments; a payload path that is not a formula node | error |
| `BridgeTarget: <path>` / `BridgeKindMismatch: <path>` / `BridgeHolder: <path>` / `MissingBridgeRecord: <path>` | bridge path unresolved; norm or definition target; label holder differs from `holderAt`; nested label without a record | error |
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

inductive Content where
  | formula (φ : VE.Formula)                                    -- closed, typed over E
  | norm (Eq : VE.Environment) (D : VE.Norms.Doc)               -- pinned local environment; no layer
  | definition (Eq : VE.Environment) (ds : List VE.Definitions.Def)
  | report (holder : String) (act : Act) (ctx : String) (body : Content) (literal : Option String)
  | assessment (j : Judgment) (a : String) (body : Content)

structure ReportKey where act : Act; sort : String; ctx : String; content : String        -- content id
structure AssessKey where j : Judgment; a : String; content : String

structure ReportUnit where id : String; holder : String; act : Act; ctx : String; body : Content; literal : Option String
structure AssessUnit where id : String; j : Judgment; a : String; body : Content

inductive Path | root (unit : String) | inner (unit : String) (depth : Nat)   -- depth ≥ 1: descend that many times

structure Bridge where id : String; target : Path; acceptedBy : String; reason : List String
structure ScopedCheck where id : String; payloads : List Path; conclusion : VE.Formula

structure ReportDoc where
  E : VE.Environment                    -- the author's environment, with the reports block decoded
  lits : List String
  holders : List String                 -- holder sorts
  evidence : String                     -- the evidence sort
  contexts : List Context
  assessments : List Assessment
  reports : List ReportUnit
  assesses : List AssessUnit
  bridges : List Bridge
  scoped : List ScopedCheck

def contentId (D : ReportDoc) : Content → String                 -- 3.4, over the decoded objects
def complementId (D : ReportDoc) (body : Content) (lit : Option String) : String   -- 1.1, 3.4
def Content.depth : Content → Nat
def holderSort (D : ReportDoc) (h : String) : Option String       -- D.E.constants h, when a holder sort
def keys (D : ReportDoc) : List ReportKey                          -- every report node of every tree, deduplicated, sorted (1.5)
def akeys (D : ReportDoc) : List AssessKey
def topKeys (D : ReportDoc) : List ReportKey                       -- the keys of the top-level report units
def topAKeys (D : ReportDoc) : List AssessKey
def keyOf (D : ReportDoc) (r : String) : Option (ReportKey ⊕ AssessKey)   -- the key whose generated name is r
def reportName (D : ReportDoc) (k : ReportKey) : String            -- reports__<act>__<i>
def assessName (D : ReportDoc) (k : AssessKey) : String            -- reports__<judgment>__<i>
def names (D : ReportDoc) : List String
def envReports (D : ReportDoc) : VE.Environment                    -- E + one unary predicate per key
def recordOf (D : ReportDoc) (a : String) : Option Assessment
def WellFormedReports (D : ReportDoc) : Bool                       -- 4.1

/-- 4.3: total on formula, report and assessment nodes; none on norm and definition nodes. -/
def elab (D : ReportDoc) : Content → Option VE.Formula
  | .formula φ => some φ
  | .report h act c b lit =>
      (holderSort D h).map fun s => .unary (reportName D ⟨act, s, c, complementId D b lit⟩) (.const h)
  | .assessment j a b =>
      (recordOf D a).map fun r => .unary (assessName D ⟨j, a, contentId D b⟩) (.const r.context)
  | _ => none
def reportPremise (D : ReportDoc) (u : ReportUnit) : VE.Formula     -- elab of the unit as a report node
def assessPremise (D : ReportDoc) (u : AssessUnit) : VE.Formula
def premises (D : ReportDoc) : List VE.Formula                     -- Γ_reports(D), document order
def openTerms (D : ReportDoc) : List OpenTerm                       -- one per assessment key (5.3)

/-- 5.2 -/
def contentAt (D : ReportDoc) : Path → Option Content
def holderAt (D : ReportDoc) : Path → Option String
def bridgeFormula (D : ReportDoc) (p : Path) : Option VE.Formula := (contentAt D p).bind (elab D)
def parseBridge : String → Option (String × Path)                  -- bridge:accepts(<holder>,<path>); root = unit id
def BridgeAdmitted (D : ReportDoc) (leaf : VE.Graph.Claim) : Prop :=
  ∃ h p, parseBridge leaf.label = some (h, p) ∧ holderAt D p = some h ∧ bridgeFormula D p = some leaf.formula ∧
    (match p with | .root _ => True | .inner .. => ∃ b ∈ D.bridges, b.target = p)

/-- 5.1 -/
def payloadFormulas (D : ReportDoc) (s : ScopedCheck) : Option (VE.Environment × List VE.Formula)
  -- some (Eq, ps) when every payload path names a formula node over one environment Eq; else none

/-- 4.2: the independent semantics. -/
structure Source (D : ReportDoc) where
  S : VE.Structure.{u}
  J : Act → String → String → S.Carrier → Prop
  A : Judgment → String → String → S.Carrier → Prop

def IntendedReports (D : ReportDoc) (M : Source.{u} D) : Prop :=
  (∀ u ∈ D.reports, ∀ v, M.S.constant u.holder = some v →
     M.J u.act u.ctx (complementId D u.body u.literal) v) ∧
  (∀ u ∈ D.assesses, ∀ r, recordOf D u.a = some r → ∀ v, M.S.constant r.context = some v →
     M.A u.j u.a (contentId D u.body) v)

def interp (D : ReportDoc) (M : Source.{u} D) : VE.Structure.{u} :=
  { M.S with relation := fun r vs =>
      match keyOf D r, vs with
      | some (.inl k), [v] => M.J k.act k.ctx k.content v
      | some (.inr k), [v] => M.A k.j k.a k.content v
      | some _, _ => False
      | none, _ => M.S.relation r vs }

def restrictJ (D : ReportDoc) (S' : VE.Structure.{u}) : Source.{u} D :=
  { S := forget (names D) S',
    J := fun act c q v => ∃ k ∈ keys D, k.act = act ∧ k.ctx = c ∧ k.content = q ∧ S'.relation (reportName D k) [v],
    A := fun j a q v => ∃ k ∈ akeys D, k.j = j ∧ k.a = a ∧ k.content = q ∧ S'.relation (assessName D k) [v] }

/-- Two source models agree on D when they agree on S and on every key of D. -/
def AgreeOn (D : ReportDoc) (M N : Source.{u} D) : Prop

/-- 4.4: P0's FOL route at E_reports (folLayer E lits is Layer.id E (StringAdmissible E lits) _). -/
def reportsRoute (D : ReportDoc) : Layer fol.{u} Unit := folLayer (envReports D) D.lits
def checkedList (D : ReportDoc) (Γ : List VE.Formula) : List VE.Formula := literals D.lits ++ premises D ++ Γ

/-- 4.4: report literals. -/
def ReportLiteral (D : ReportDoc) (a : VE.Formula) : Prop := a ∈ premises D ∨ ∃ b ∈ premises D, a = .not b
def ConsistentLiterals (R : List VE.Formula) : Prop := ¬ ∃ a, a ∈ R ∧ .not a ∈ R
```

### 9.2 Theorems: vocabulary, faithfulness, conservativity and structure

```lean
/-- 1.5: E ⊆ E_reports; generated names are fresh, bounded, injective; every premise is well-formed. -/
theorem envReports_extends (D : ReportDoc) (h : WellFormedReports D = true) :
  ∀ a, a.WellFormed D.E [] → a.WellFormed (envReports D) []
theorem names_fresh (D) (h) :
  (∀ n ∈ names D, D.E.predicates n = none ∧ n.utf8ByteSize ≤ 64) ∧ (names D).Nodup
theorem hide_envReports (D) (h) : hide (envReports D) (names D) = D.E
theorem premises_wellFormed (D) (h) : ∀ a ∈ premises D, a.WellFormed (envReports D) []
theorem keys_finite (D) (h) : (keys D).length + (akeys D).length ≤ contentCount D
theorem content_depth_bounded (D) (h) : ∀ u ∈ D.reports, u.body.depth < 16

/-- reports_elaboration_faithful, the source-model direction: the elaborated premises hold in the interpretation
    of a source model exactly when the document's intended meaning holds of it. -/
theorem reports_elaboration_faithful (D : ReportDoc) (h : WellFormedReports D = true) (M : Source.{u} D)
    (hM : M.S.Admissible D.E) :
  (interp D M).Admissible (envReports D) ∧
  (fol.Sat (interp D M) (premises D) ↔ IntendedReports D M)

/-- The structure direction: on every admissible E_reports structure. -/
theorem reports_elaboration_faithful_out (D) (h) (S' : VE.Structure.{u}) (hS : S'.Admissible (envReports D)) :
  fol.Sat S' (premises D) ↔ IntendedReports D (restrictJ D S')

/-- Model correspondence in both directions. -/
theorem restrict_interp (D) (h) (M : Source.{u} D) (hM : M.S.Admissible D.E) : AgreeOn D (restrictJ D (interp D M)) M
theorem interp_restrict (D) (h) (S' : VE.Structure.{u}) (hS : S'.Admissible (envReports D)) :
  ∀ r vs, (interp D (restrictJ D S')).relation r vs ↔ S'.relation r vs
theorem old_formula_invariant (D) (h) (M : Source.{u} D) (a : VE.Formula) (ha : a.WellFormed D.E []) :
  a.denote (interp D M) [] ↔ a.denote M.S []
theorem restrictJ_admissible (D) (h) (S') (hS : S'.Admissible (envReports D)) : (restrictJ D S').S.Admissible D.E

/-- Finite witness decoding: a valid finite model over E_reports is the interpretation of a source model. -/
theorem finite_witness_decodes {α} [DecidableEq α] (D) (h) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid (envReports D)) :
  ∃ M : Source.{0} D, M.S.Admissible D.E ∧ ∀ r vs, (interp D M).relation r vs ↔ Mo.asStructure.relation r vs

/-- 4.2: every admissible old-language structure underlies a source model of D. -/
theorem source_over_any_structure (D) (h) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M
/-- and with any key outside the document's top-level units interpreted as empty. -/
theorem unreported_key_free (D) (h) (S₀) (h₀) (k : ReportKey) (hk : k ∉ topKeys D) :
  ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M ∧ ∀ v, ¬ M.J k.act k.ctx k.content v

/-- 4.4: existence of expansion (not uniqueness). -/
theorem expansion_exists (D) (h) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) :
  ∃ S', forget (names D) S' = S₀ ∧ S'.Admissible (envReports D) ∧ fol.Sat S' (premises D)

/-- reports_old_language_conservative. -/
theorem reports_old_language_conservative (D : ReportDoc) (h : WellFormedReports D = true)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E []) :
  VE.Entails.{u} (envReports D) Γ φ ↔ VE.Entails.{u} D.E Γ φ

/-- Its corollary: consistent report literals change no old-language verdict. -/
theorem reports_no_leak (D) (h) (Γ) (φ) (hΓ) (hφ) (R : List VE.Formula)
    (hR : ∀ a ∈ R, ReportLiteral D a) (hc : ConsistentLiterals R) :
  VE.Entails.{u} (envReports D) (Γ ++ R) φ ↔ VE.Entails.{u} D.E Γ φ

/-- 4.5, each an instance of source_over_any_structure or unreported_key_free. -/
theorem attitude_not_factive (D) (h) (u : ReportUnit) (hu : u ∈ D.reports) (q : VE.Formula)
    (hq : elab D u.body = some q) (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible D.E) (hn : ¬ q.denote S₀ []) :
  ∃ M : Source.{u} D, IntendedReports D M ∧ ¬ q.denote (interp D M) []
theorem no_closure_under_consequence (D) (h) (hb : beliefsIn D h c P (.implies P Q))
    (hQ : ⟨.believes, s, c, complementId D (.formula Q) none⟩ ∉ topKeys D) (S₀) (h₀) :
  ∃ M : Source.{u} D, IntendedReports D M ∧ ∀ v, ¬ M.J .believes c (complementId D (.formula Q) none) v
theorem nested_independent (D) (h) (u ∈ D.reports) (hu : u.body = .report h₂ .believes c' (.formula q) none)
    (hin : ⟨.believes, s₂, c', complementId D (.formula q) none⟩ ∉ topKeys D) (S₀) (h₀) (hn : ¬ q.denote S₀ []) :
  ∃ M : Source.{u} D, IntendedReports D M ∧ (∀ v, ¬ M.J .believes c' (complementId D (.formula q) none) v) ∧
    ¬ q.denote (interp D M) []
theorem negation_scopes_distinct (D) (h) (c s) (q : VE.Formula) :
  reportName D ⟨.believes, s, c, complementId D (.formula (.not q)) none⟩ ≠
    reportName D ⟨.believes, s, c, complementId D (.formula q) none⟩
theorem tense_keys_distinct (D) (h) (c c' : String) (hc : tenseOf D c ≠ tenseOf D c') (s q) :
  reportName D ⟨.believes, s, c, q⟩ ≠ reportName D ⟨.believes, s, c', q⟩
theorem content_structural (D) (h) (φ ψ : VE.Formula) :
  contentId D (.formula φ) = contentId D (.formula ψ) ↔ canonical φ = canonical ψ     -- never ↔ logical equivalence
theorem literal_paraphrase_distinct (D) (h) (u₁ u₂ : ReportUnit) (hw : u₁.literal ≠ u₂.literal)
    (hs : u₁.body = u₂.body) : complementId D u₁.body u₁.literal ≠ complementId D u₂.body u₂.literal
theorem all_truth_combinations (D) (h) (ks : List ReportKey) (hk : ∀ k ∈ ks, k ∉ topKeys D) (f : ReportKey → Bool)
    (S₀) (h₀) : ∃ M : Source.{u} D, IntendedReports D M ∧ ∀ k ∈ ks, ∀ v, M.J k.act k.ctx k.content v ↔ f k = true
```

`topKeys D` are the keys of the top-level units; `beliefsIn D h c P R` says `D` has top-level belief units of
holder `h` in context `c` with formula contents `P` and `R`; `tenseOf` reads the context table; `canonical` is the
P5 normal form. `all_truth_combinations` is the single statement behind the "different attributions for
equivalent payloads", "may and probably independent" and "negation inside versus outside" fixtures.

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

/-- The old-language reading: for Γ and φ over E the report atoms add nothing (reports_no_leak with the
    consistent positive literal set premises D), so the accepted certificate is one of old-language consequence. -/
theorem reports_route_acceptance_base (D) (h) (hn) (Γ) (φ) (c) (accepted)
    (hΓ : ∀ a ∈ Γ, a.WellFormed D.E []) (hφ : φ.WellFormed D.E []) :
  VE.Entails.{u} D.E (literals D.lits ++ Γ) φ ∧ EntailsString.{u} D.E D.lits Γ φ

theorem reports_route_countermodel {α : Type u} [DecidableEq α] (D) (h) (hn) (Γ : List VE.Formula) (φ : VE.Formula)
    (Mo : VE.FiniteModel α) (valid : Mo.Valid (envReports D)) (hl : literalsValid Mo D.lits = true)
    (checked : VE.countermodelCheck Mo (premises D ++ Γ) φ = true) :
  ¬ EntailsString.{u} (envReports D) D.lits (premises D ++ Γ) φ ∧
  ¬ VE.Entails.{u} (envReports D) (checkedList D Γ) φ ∧
  ∃ M : Source.{u} D, IntendedReports D M ∧ fol.Sat (interp D M) Γ ∧ ¬ φ.denote (interp D M) []

/-- 5.1 -/
theorem scoped_consequence_sound (D) (h) (s : ScopedCheck) (hs : s ∈ D.scoped) (Eq) (ps)
    (hp : payloadFormulas D s = some (Eq, ps)) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate Eq ps s.conclusion c = true) :
  VE.Entails.{u} Eq ps s.conclusion
theorem scoped_witness_sound {α} [DecidableEq α] (D) (h) (s) (hs) (Eq) (ps) (hp) (Mo : VE.FiniteModel α)
    (valid : Mo.Valid Eq) (hps : ∀ a ∈ ps, a.eval Mo [] = true) (hn : s.conclusion.eval Mo [] = false) :
  ¬ VE.Entails.{0} Eq ps s.conclusion
theorem scoped_not_premise (D) (h) :
  premises D = premises { D with scoped := [] } ∧ envReports D = envReports { D with scoped := [] }
theorem quoted_inconsistency_local (D) (h) (s) (hs) (Eq) (ps) (hp) (c)
    (acc : VE.Tableau.checkCertificate Eq ps .bottom c = true) :
  (∀ S : VE.Structure.{u}, S.Admissible Eq → ¬ fol.Sat S ps) ∧
  ∀ S₀ : VE.Structure.{u}, S₀.Admissible D.E → ∃ M : Source.{u} D, M.S = S₀ ∧ IntendedReports D M

/-- 5.2 -/
theorem bridge_root_is_legacy (D) (h) (leaf : VE.Graph.Claim) (hl : ∃ a u, parseBridge leaf.label = some (a, .root u)) :
  BridgeAdmitted D leaf ↔ ∃ a u, parseBridge leaf.label = some (a, .root u) ∧
    VE.Route.Admission.QuotedUnit (w2Doc D) a u leaf.formula
  -- w2Doc D: the W2 view of D with each report unit's content the elab of its root complement
theorem bridge_formula_exact (D) (h) (leaf) (hb : BridgeAdmitted D leaf) :
  ∃ p, bridgeFormula D p = some leaf.formula
theorem bridge_kind_rejected (D) (h) (p : Path) (hc : ∃ Eq x, contentAt D p = some (.norm Eq x) ∨ ∃ Eq x, contentAt D p = some (.definition Eq x)) :
  ¬ ∃ leaf, BridgeAdmitted D leaf ∧ ∃ a, parseBridge leaf.label = some (a, p)
theorem bridge_nested_needs_record (D) (h) (leaf) (u n) (hl : ∃ a, parseBridge leaf.label = some (a, .inner u n))
    (hb : BridgeAdmitted D leaf) : ∃ b ∈ D.bridges, b.target = .inner u n
theorem bridge_payload_not_belief (D) (h) (u ∈ D.reports) (hu : u.body = .report h₂ .believes c' (.formula q) none) :
  bridgeFormula D (.root u.id) = elab D u.body ∧ bridgeFormula D (.inner u.id 1) = some q ∧ elab D u.body ≠ some q

/-- 5.3 -/
theorem assessment_open_term (D) (h) (u : AssessUnit) (hu : u ∈ D.assesses) :
  ∃ t ∈ openTerms D, t.name = assessName D ⟨u.j, u.a, contentId D u.body⟩ ∧ t.arguments = [D.evidence] ∧
    ∃ r, recordOf D u.a = some r ∧ t.decidedBy = r.decidedBy ∧ t.decidedBy ≠ ""
theorem assessment_not_factive (D) (h) (u ∈ D.assesses) (q) (hq : elab D u.body = some q) (S₀) (h₀) (hn : ¬ q.denote S₀ []) :
  ∃ M : Source.{u} D, IntendedReports D M ∧ ¬ q.denote (interp D M) []
theorem may_probably_independent (D) (h) (a q) :
  assessName D ⟨.may, a, q⟩ ≠ assessName D ⟨.probably, a, q⟩ ∧
  ∀ (f : Judgment → Bool) (S₀) (h₀ : S₀.Admissible D.E), (∀ j, ⟨j, a, q⟩ ∉ topAKeys D) →
    ∃ M : Source.{u} D, IntendedReports D M ∧ ∀ j v, M.A j a q v ↔ f j = true
theorem probably_not_scopes_distinct (D) (h) (a) (q : VE.Formula) :
  assessName D ⟨.probably, a, contentId D (.formula (.not q))⟩ ≠ assessName D ⟨.probably, a, contentId D (.formula q)⟩

/-- 9.4: the wire. A successful reports `admission` answer is exactly the encoding of an admission whose bindings
    equal the recomputed digests and whose regenerated E_reports, premises, open terms and bridge formulas are
    the ones this specification defines; the graph is checked by the unchanged VE.Graph.checkTableau. -/
theorem Run.reports_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : Run.usesReportsPath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.ReportsAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
theorem reports_admission_sound (profiles : List String) (environment : Json) (j : Json) (res : ReportsAdmitted)
    (h : admissionReports profiles environment j = .ok res) :
  WellFormedReports res.D = true ∧
  VE.Graph.Acyclic res.graph ∧ (res.graph.nodes.map (fun n => n.claim.name)).Nodup ∧
  VE.Graph.SoundReport.{u} (envReports res.D) res.graph res.report ∧
  (∀ leaf ∈ res.report.assumptions,
     (∃ u ∈ res.D.reports, leaf.label = "report:" ++ u.id ∧ leaf.formula = reportPremise res.D u) ∨
     (∃ u ∈ res.D.assesses, leaf.label = "assessment:" ++ u.id ∧ leaf.formula = assessPremise res.D u) ∨
     BridgeAdmitted res.D leaf ∨
     (∃ w, w.claim = leaf ∧ VE.Route.Admission.LeafAdmitted (w2Doc res.D) w)) ∧
  VE.Route.Admission.CitationsClosed (w2Doc res.D) res.report ∧ VE.Route.Admission.ChoicesCompatible res.report
theorem reports_labels_decoded : as VE.Route.Admission.admit_labels_decoded, for admissionReports
```

`ReportsAdmissionAnswer` is P0's admission answer with the reports decoder, `report:*`, `assessment:*` and
nested-bridge leaves admitted only when equal to the regenerated formulas, every other label by the unchanged
`LeafAdmitted`, and the report consequence stated over `literals ++ premises D ++ Γ`.

### 9.4 The executable `ve_reports_route`

`lean/.lake/build/bin/ve_reports_route <cases.json>`, root `ReportsMain.lean`, a new Lake target; `Run.main` is the
executable root and no frozen file changes. On raw input it runs the frozen envelope and profile gate, requires
`reports@0` and `relational-fol@0`, decodes the environment with its `reports` block through the P0 vocabulary
decoder plus a strict reports decoder (unknown fields rejected; the original complete environment hashed), decodes
contexts, assessments, units with their content trees (recursively validating quoted norm and definition content
through the unchanged W1 and W3 decoders under their pinned environments), bridges and scoped checks, runs
`WellFormedReports`, regenerates `E_reports`, `Γ_reports`, the open-term records and every bridge formula,
validates bindings, and delegates every checker call to the unchanged tableau, finite-model and graph functions.
Case kinds:

| Kind | Extra input | Output |
|---|---|---|
| `reports-elaborate` | none | `environment_reports` (canonical), `keys` (each with its generated name and source key), `premises` (labelled `report:<unit>` / `assessment:<unit>`), `open_terms`, `bridge_formulas` (per declared record), `warnings` |
| `reports-scoped` | per check: `certificate` or `witness` | FOLLOWS / DOES NOT FOLLOW / PAYLOADS INCONSISTENT / UNKNOWN with detail |
| `reports-certificate` | `premises`, `conclusion`, `certificate` bound to `literals ++ Γ_reports ++ premises` | `valid`, `environment_reports_id`, `bindings` |
| `reports-countermodel` | `premises`, `conclusion`, finite model over `E_reports` | `refutes`, the decoded source-model rendering |
| `admission` | W2 document with report and assessment units, bridges, scoped checks and graph | `admitted`, `report`, `report_id`, `kinds`, `residual` |

P0 cases without reports constructs delegate unchanged to `VE.Route.Run.runCase`; malformed reports inputs never
fall back after a failed reports decode.

### 9.5 What is not claimed

No theorem about the English surface: `reports_parse_unique` (P1) and `reports_print_parse` (P4) over the
templates of 2.1 are item-4 obligations in `lean/VE/English/Reports*.lean`, stated against the reports grammar and
its manifest; the existing Lean English model covers the v0 unary and binary core only (INTEGRATION-GAPS.md), and
tests alone do not discharge them. No claim that `IntendedReports` matches an author's or a source's intent: that
is this statement review, W8's fidelity gate and the blind whole-span review. No theorem about assessors,
criteria or the truth of any content. No modal theorem. No completeness of scoped checks beyond the tableau's.
No theorem about adoption or import beyond provenance. No theorem about `Layer.comp` with the norms or
definitions chains (11.3).

## 10. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from Python and, where the Lean route has a case kind,
from Lean (`tests/test_reports*.py`, the `reports` conformance family). Section 10.1 fixes the environment,
contexts, assessments and documents; 10.2 states what each must produce, so that a reviewer derives the
expectation from the definitions before reading it.

### 10.1 Definitions

Environment `E₀`: sorts `organisation`, `text`, `service`, `model`, `evidence`; `reports.holders = [organisation,
text]`, `reports.evidence = evidence`; constants `anthropic : organisation`, `the_article : text`, `the_team :
organisation`, `service : service`, `claude : model`, `e1 : evidence`; unary predicates `safe(service)`,
`helpful(model)` ("{0} is helpful"), `was_helpful(model)` ("{0} was helpful"), `human(model)`, `published(service)`
("the results of {0} are published"), `reviewed(service)`; profiles `[relational-fol@0, reports@0]`; no literals.
Contexts: `c1` (present, "the constitution"), `c2` (past, "the article of 16 September", tag `sept16`), `c3`
(present, "the article"). Assessment `a1`: context `e1`, `decided_by: unresolved_decider`, no criteria, factors
["review status"], jurisdiction `news_desk`, version 1. Every document below partitions a synthetic source whose
bytes are the sentences shown; graph nodes are named after their units; `Γ_author` is empty unless stated.

```text
D_α   u1: The article says that the service is safe.                          says, the_article, c3, safe(service)
D_β   u1: Anthropic believes that the service is reviewed.                    believes, anthropic, c1, reviewed(service)
      u2: Anthropic believes that if the service is reviewed then the service is safe.
      s1: scoped check, payloads [u1, u2], conclusion safe(service), certificate supplied
D_γ   u1: Anthropic believes that the service is safe and the service is safe.  content safe ∧ safe
      u2: Anthropic believes that the service is safe.                           content safe
      u3: Anthropic believes that the service is safe.   (second occurrence, same key as u2, distinct span)
D_δ   u1: The team intends to publish the results.                            intends, the_team, c1, published(service)
D_ε   u1: Anthropic believes that it is not the case that Claude is human.
      u2: It is not the case that Anthropic believes that Claude is human.
D_ζ   u1: The article says that Anthropic believes that Claude is helpful.    says, the_article, c3, ⟨believes, anthropic, c1, helpful(claude)⟩
      graph G₁: leaf L1 labelled bridge:accepts(the_article,u1), formula J_{believes,c1,helpful}(anthropic)
      graph G₂: leaf L2 labelled bridge:accepts(anthropic,u1.1), formula helpful(claude), bridge record b1
      graph G₃: leaf L3 labelled bridge:accepts(anthropic,u1.1) with no record
      graph G₄: leaf L4 labelled bridge:accepts(the_article,u1.1), formula helpful(claude), record b1
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
D_λ   u1: The article says that: [quoted W3 package under E_q defining safe(x) as reviewed(x)]
      Γ_author: reviewed(service); conclusion safe(service) with a certificate that unfolds the definition
D_μ   u1: According to the stated assessment, the service may be safe.        may, a1, safe(service)
      u2: According to the stated assessment, the service is probably safe.   probably, a1, safe(service)
      u3: According to the stated assessment, it is probably the case that it is not the case that the service is safe.
      u4: It is not the case that, according to the stated assessment, it is probably the case that the service is safe.
      a1′: a1 with the decided_by field removed
D_ν   E₀ plus a holder constant assessment : organisation with verbalisation "the stated assessment"
      input: According to the stated assessment, the service may be safe.
      input: Anthropic says that, according to the stated assessment, the service may be safe.
D_ξ   u1 of D_η; manifest M₁ = (E₀ id, c2, no assessment, profiles, no choices); M₂ = M₁ with c2's tense present
D_ο   D_δ with norms@0 also enabled and no rule
D_π   D_α with Γ_author = [reviewed(service) → safe(service), reviewed(service)]; conclusion safe(service);
      D_π′: D_π with Γ_author += [¬ J_{says,c3,safe}(the_article)]  (written as "It is not the case that the
      article says that the service is safe.")
D_ρ   D_γ's u2 and u3; scoped check s1 with payloads [u2, u3], conclusion safe(service)
D_σ   u1: The Fed pledged to lower inflation.    (report block with act pledged)
      u2: kind attributed(the_fed, promised, asserted) with no content
D_τ   u1: Anthropic wants Claude to be helpful.                    wants, anthropic, c1, helpful(claude)
      u2: The team wants to publish the results.                   wants, the_team, c1, published(service)
      u3: The peoples reaffirmed their faith in fundamental human rights.   unformalised(noun_complement)
      u4: Warsh pledged, "clearly and at sufficient speed".                 unformalised(fragment_complement)
D_υ   u1: Anthropic believes that every model is helpful.                    content ∀x:model. helpful(x)
      u2: Every model is such that Anthropic believes that it is helpful.    (input only)
D_φ   D_ζ with a certificate for Γ_author = [J_{says,…}(the_article)] ⊢ J_{says,…}(the_article); then each of:
      c3's tense changed; the_article replaced by anthropic; helpful replaced by human; literal words added;
      a1-style record attached; a reading choice recorded; E₀'s legend for helpful changed
D_χ   1,000 generated report documents (depth ≤ 4, acts and judgments mixed, nested to depth 3)
D_ψ   every existing W2 document fixture, (a) without reports@0, (b) with reports@0 and no report content
```

### 10.2 Expected results

- **(α) Not factive.** `E_reports = E₀ + reports__says__1(text)`; `Γ = [reports__says__1(the_article)]` labelled
  `report:u1`; status CHECKED; residual `reports: says 1`. The finite model with `safe` empty and
  `reports__says__1 = {the_article}` is valid, satisfies `Γ`, refutes `safe(service)`; `reports-countermodel`
  reports `refutes` and renders "the article says the service is safe; the service is not safe". A certificate
  for `Γ ⊢ safe(service)` does not exist and a forged one fails to replay.
- **(β) Not closed; scoped consequence.** Two top-level keys (`believes, organisation, c1, reviewed` and
  `believes, organisation, c1, reviewed → safe`); a belief in `safe` has no key in `D_β`. The model with both
  atoms true and `safe` empty is valid and satisfies `Γ`. Adding "Anthropic believes that the service is safe" as
  u3 makes a third key; the model that sets its atom false while the first two are true is valid
  (`unreported_key_free` before the addition, `all_truth_combinations` after it). The scoped check `s1` is
  FOLLOWS with its certificate at `E₀`; the report line reads "the service is safe follows from the reported
  contents u1, u2"; `Γ` and `E_reports` are unchanged by `s1` (`scoped_not_premise`); no certificate for
  `Γ ⊢ safe(service)` or for `Γ ⊢ reports__believes__3(anthropic)` replays.
- **(γ) Structural content.** u1 and u2 have different content ids and different keys (`content_structural`);
  u2 and u3 share one key and one atom; `Γ` has three entries with two distinct formulas; a model with the u1 atom
  true and the u2/u3 atom false is valid. The residual counts two report keys and three occurrences.
- **(δ) Intention.** `Γ = [reports__intends__1(the_team)]`; the model with `published` empty satisfies `Γ`; no
  `required` symbol exists (`UnknownSymbol` on a `Γ` naming one); paraphrase: "neither that the results are
  published, nor an obligation, nor a promise follows".
- **(ε) Negation scopes.** Two different keys (`negation_scopes_distinct`); models for all four truth
  combinations; neither certificate `u1 ⊢ u2` nor `u2 ⊢ u1` replays; the paraphrases differ as in 2.1.
- **(ζ) Nested and bridges.** One top-level key; `E_reports` also contains the inner key's predicate
  (`reports__believes__1(organisation)`) because it occurs as content, but no premise mentions it. Model with the
  outer atom true, the inner atom false and `helpful` empty: valid, satisfies `Γ`. `G₁` admitted: `L1` is a
  root-path bridge with the inner belief atom (legacy `QuotedUnit` on the W2 view); `G₂` admitted: `L2` assumes
  `helpful(claude)`, listed in the assumptions with its label and record; `G₃` rejected `MissingBridgeRecord:
  u1.1`; `G₄` rejected `BridgeHolder: u1.1` (the holder at `u1.1` is anthropic). Under `G₂` a certificate for
  `helpful(claude)` replays with `L2` as its only assumption; nothing certifies the inner belief atom from `L2`.
- **(η) Tense.** Two keys, two predicates (`tense_keys_distinct`), `E_reports` has `reports__believes__1` (c1,
  present) and `reports__believes__2` (c2, past) in key order; a model with the past atom true and the present atom
  false; the renderings differ in verb form and in context; the round trip of each preserves its context.
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
- **(λ) Quoted definitions.** The package validates under `E_q`; `safe` in `E₀` keeps its own declaration; no
  `background:definitions` premise for it exists in `Background(E_reports)`; the certificate fails to replay
  outside; inside a scoped check over `E_q` with payload `reviewed(service)` the conclusion FOLLOWS.
- **(μ) Assessments.** Four assessment units; keys `(may, a1, safe)`, `(probably, a1, safe)`, `(probably, a1,
  ¬safe)`; u4's atom is the negation of u2's (`probably_not_scopes_distinct`); every unit OPEN; three open terms
  `reports__may__1`, `reports__probably__1`, `reports__probably__2` with `decided_by: unresolved_decider`,
  arguments `[evidence]`; residual `assessments: unresolved_decider 3`; no certificate among `safe(service)`, u1,
  u2 replays in any direction (`all_truth_combinations` instances); `a1′` is `InvalidInput: assessment a1 needs
  decided_by`.
- **(ν) Parser binding.** The environment is rejected: `InvalidInput: holder verbalisation reserved`. With a
  holder verbalised "the assessment desk" instead, the first input parses to `May(a1, safe)` only (one derivation);
  the second parses to `says(anthropic, c1, May(a1, safe))`, kind `attributed(anthropic, says, hedged(could,
  asserted))`; there is no derivation with a `says` holder named by the phrase.
- **(ξ) Round trip.** `print(parse(s, M₁)) = s` and `parse(print(A), M₁) = A`; parsing the same sentence under
  `M₂` is `ManifestMismatch: u1` (the verb form disagrees with the context's tense); rendering u1 without a manifest
  is refused; the inspector shows `c2`'s record beside the sentence.
- **(ο) Desire is not duty.** With `norms@0` on, `Γ` still has one atom; the norms route sees no rule; `required`
  and `permitted` predicates, if declared, are decided by completions alone; a `Γ` naming `must` is not a wording.
- **(π) Conservativity.** The certificate for `safe(service)` from `Γ_author` replays under `E_reports` and under
  `E₀` (`reports_old_language_conservative`); the report atom's presence changes no old-language verdict
  (`reports_no_leak`); `D_π′` makes `Γ` inconsistent: the P0 line reports INCONSISTENT with its certificate and
  the `safe(service)` certificate is `vacuous`.
- **(ρ) Occurrences.** Payloads `[u2, u3]` are two payloads with one formula; the scoped check FOLLOWS trivially;
  the report line lists both occurrences; the key count is one.
- **(σ) Unreviewed acts.** u1 is `UnsupportedAct: pledged (reports@0 admits says, believes, wants, intends)`; u2
  is LABELLED as today with the warning line "unreviewed act promised in u2"; neither adds a key.
- **(τ) Complements.** u1's content is `helpful(claude)` with Claude as subject; u2's is `published(service)` with
  the team as the intending holder; u3 is UNFORMALISED `noun_complement` and u4 `fragment_complement`, each with
  its warning line; none of u3, u4 adds a key.
- **(υ) Scope.** u1 admitted with the quantifier inside the content; u2 rejected `OpenComplement: u2` with the
  rewrite "Anthropic believes that every model is helpful" and the paraphrase that the two differ.
- **(φ) Identity.** Every listed change alters `environment_id(E_reports)` or the document hash or a content id,
  and the certificate fails to replay under the changed document; the unchanged document replays.
- **(χ) Differential.** Python's `E_reports`, keys, premises, open terms and bridge formulas equal Lean's on every
  generated document (regression evidence, not proof); Rust evaluates the elaborated premises and agrees on every
  verdict with `untrusted: true`.
- **(ψ) Frozen fixtures.** (a) byte-identical outputs, identities and reports; (b) identical outputs except the
  profile list in identities, which changes `environment_id` as any profile addition does; the reports residual
  lines are empty.

Beside these: W2's schema, partition, kind depth and tamper tests repeated on report documents; norms.md 10.6 to
10.8 shapes for the surface round trip of every wording in 2.1 (canonical text, synonyms, the two rejected modal
forms with their rewrites), identity of every existing fixture unchanged, and certificate binding against each
change of φ.

## 11. Limits, regeneration, Rust and trust

### 11.1 Limits

Contexts ≤ 256, assessments ≤ 256, bridges ≤ 1,000, scoped checks ≤ 256 with ≤ 64 payloads each, content depth ≤ 16
(the W2 kind depth), literal words ≤ 4,096 bytes, generated names ≤ 64 bytes, predicates within `MAX_PREDICATES`
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

In this slice an active `norms@0` or `definitions@0` outer layer with `reports@0` is `UnsupportedProfile:
reports@0 with <profile> layers`, listed in the status table beside the plan's boundary with its criterion: the
composition `Layer.comp` of `reportsRoute` with the norms chain (`E_in` of the chain `= E_reports`, the report atoms
being base predicates below every regulated or defined symbol in the shared DAG) and the executable's regeneration
of that chain over `E_reports` are unproved and unbuilt. Quoted W1 and W3 content is handled locally (5.4) and needs
no composition. `data@0` composes as today (the data layer's admissibility in place of `StringAdmissible`, its
flags in Background); `documents@1` is the W2 wrapper this profile extends.

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
   as distinct contents (13.6).
2. The four acts and the complement forms (1.2, 1.3); unreviewed acts as `UnsupportedAct` or LABELLED metadata,
   never renamed.
3. The assessment record and the explicit `unresolved_decider` (1.4, 5.3); the parser binding of "the stated
   assessment" (2.1, fixture ν); the admission sentence.
4. `E_reports` and the generated names (1.5); the reserved prefix.
5. The independent semantics `(S, J, A)` and `IntendedReports` (4.2): only top-level units assert; nested nodes
   are contents.
6. `elab`, `interp`, `restrictJ` and `reports_elaboration_faithful` in both directions with finite witness
   decoding (4.3, 9.2), at every universe.
7. The route instance: `Layer.id` over `E_reports`, report atoms in `Γ`, `Intended = True` as the empty layer's
   meaning only (4.4); `reports_route_acceptance` and `reports_route_countermodel` (9.3).
8. `reports_old_language_conservative` by existence of expansion, `reports_no_leak` and the inconsistent-literal
   case through the vacuity line (4.4).
9. The structure theorems as instances of `source_over_any_structure` (4.5, 9.2).
10. Scoped checks as report lines, not premises; inner inconsistency local (5.1).
11. Bridges: paths, `holderAt`, records for nested targets, the legacy root meaning byte for byte, the kind
    rejection (5.2, 9.3).
12. Adoption and import as provenance-only typed operations (5.4).
13. Status and residual lines (6); the wrapper/complement byte split.
14. The English table (2.1): one reading per wording; the synonyms and non-synonyms (2.2); the checklist (2.3);
    the round-trip contract and `ManifestMismatch` (2.4); the source examples with zero substantive gain (2.5).
15. The diagnostics (8) and the fixtures (10), each against the definitions.
16. The composition gate (11.3) and the trust list (11.4).
17. The resolved choices of section 13, in particular 13.2 (the profile-gated act list) and 13.5 (criteria are
    not premises).

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
8. **Nested bridge targets are paths with a record; root paths are legacy.** Tokens admit dots, so `u1.1` is a
   label token the legacy admission cannot match (no such unit) and the reports admission resolves; the record
   supplies reviewer and reason as the plan requires.
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

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-28 | Draft 1 | Item-1 specification from attribution-PLAN.md revision 2: contents, occurrences and keys with tense in the context; the four acts and the complement forms; open assessments with W2's complete record and `unresolved_decider`; `E_reports` and generated names; the English table with the "According to the stated assessment" templates, the past-tense row, the parser binding and the round-trip contract; wire form and identity; the independent semantics `(S, J, A)`, `elab`, `interp`, `restrictJ`; the `Layer.id` route instance with report atoms in `Γ`; `reports_elaboration_faithful` and `reports_old_language_conservative` as the first Lean statements, with `reports_no_leak`, the structure theorems, scoped checks, bridges by path, assessments and the wire; status and residual lines; diagnostics; fixtures α to ψ with definitions separated from expectations; limits, the composition gate and the trust list; resolved choices. Spec only: no code, Lean or frozen contract changed. |
